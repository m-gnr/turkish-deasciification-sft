from collections import Counter
import random
import unittest
from unittest.mock import patch

from scripts.run_chunking import (split_text, validate_split, build_plan, assemble,
                                 decide, run_generation, boundary_diagnostics)
from scripts.compare_prompts import summarize


class ChunkingTests(unittest.TestCase):
    def test_byte_exact_with_turkish_decomposed_text_and_whitespace(self):
        text = 'I İ ı i\tI\u0307!  Çok güzel;\n bir metin.\r\nSon…  '
        for limit in (5, 8, 12, 80, 120):
            chunks = split_text(text, limit)
            self.assertEqual(''.join(chunks).encode(), text.encode())
            validate_split(text, chunks, limit)

    def test_priority_sentence_over_comma_and_any(self):
        text = 'Bir. iki, üç dört beş altı'
        self.assertEqual(split_text(text, 17)[0], 'Bir. ')
        self.assertEqual(split_text('Bir, iki üç dört beş', 12)[0], 'Bir, ')
        self.assertEqual(split_text('bir iki üç dört', 10)[0], 'bir iki ')

    def test_rightmost_equal_priority_and_closing_quote(self):
        self.assertEqual(split_text('a. b! c d e f g', 10)[0], 'a. b! ')
        self.assertEqual(split_text('"a." b c d e', 8)[0], '"a." ')

    def test_never_split_short_sentence_even_with_internal_punctuation(self):
        text = 'Bir. İki; üç.'
        self.assertEqual(split_text(text, len(text)), [text])
        self.assertEqual(split_text('', 80), [''])

    def test_long_word_exception_and_exact_limit_word(self):
        self.assertEqual(split_text('abcdefghij xyz', 5), ['abcdefghij ', 'xyz'])
        self.assertEqual(validate_split('abcdefghij xyz', ['abcdefghij ', 'xyz'], 5), [0])
        chunks = split_text('abcde  xyz', 5)
        self.assertTrue(all(len(c) <= 5 for c in chunks))
        self.assertEqual(''.join(chunks), 'abcde  xyz')

    def test_whitespace_run_does_not_create_false_exception(self):
        text = 'ab' + ' '*40 + 'cd'
        chunks = split_text(text, 7)
        self.assertTrue(all(len(c) <= 7 for c in chunks))
        self.assertEqual(''.join(chunks), text)

    def test_validator_rejects_corruption_and_word_split(self):
        with self.assertRaisesRegex(ValueError, 'Byte-level'):
            validate_split('a  b', ['a ', 'b'], 3)
        with self.assertRaisesRegex(ValueError, 'Word split'):
            validate_split('abcd', ['ab', 'cd'], 3)
        with self.assertRaisesRegex(ValueError, 'Unjustified'):
            validate_split('a b c', ['a b c'], 3)
        with self.assertRaises(ValueError):
            split_text('a', 0)

    def test_randomized_unicode_roundtrip_and_word_boundaries(self):
        rng = random.Random(42)
        words = ['cok', 'İ', 'I\u0307', 'ı', 'a'*130, 'son.', 'ile;', '—', 'üç!', 'x?']
        for _ in range(500):
            text = ''.join(rng.choice(words)+rng.choice([' ', '  ', '\t', '\n', '\r\n']) for _ in range(rng.randint(1,20)))
            for limit in (80, 120):
                chunks = split_text(text, limit)
                self.assertEqual(''.join(chunks).encode(), text.encode())
                validate_split(text, chunks, limit)

    def test_reuse_precedes_no_candidate_shortcut(self):
        rows = [{'id': 'short', 'input': 'XYZ 12'}, {'id':'long','input': 'XYZ '*70}]
        plan = build_plan(rows)
        for limit in (80, 120):
            short = [p for p in plan['pieces'] if p['sentence_id']=='short' and p['limit']==limit]
            self.assertEqual(short[0]['mode'], 'reuse')
            long = [p for p in plan['pieces'] if p['sentence_id']=='long' and p['limit']==limit]
            self.assertTrue(all(p['mode']=='copy' for p in long))
        self.assertEqual(plan['schedule'], [])

    def test_frozen_schedule_interleaves_without_duplicates(self):
        rows = [{'id':str(i), 'input':'cok iyi '*30} for i in range(20)]
        plan = build_plan(rows)
        self.assertEqual(plan, build_plan(rows))
        self.assertEqual(len(plan['schedule']),len(set(plan['schedule'])))
        self.assertEqual(Counter(x.split(':')[0] for x in plan['schedule'][:50]), {'chunk120':25,'chunk80':25})

    def test_assembly_preserves_raw_model_boundary_errors(self):
        rows = [{'id':'x','input':'cok '*40}, {'id':'y','input':'cok'}]
        plan = build_plan(rows)
        generated = {p['id']:{'output':p['input'].rstrip()} for p in plan['pieces'] if p['mode']=='generate'}
        outputs, details = assemble(plan, generated, [{'id':'x','output':'OLD'}, {'id':'y','output':'REUSED'}])
        self.assertEqual(outputs[80]['y'], 'REUSED')
        self.assertNotEqual(outputs[80]['x'], rows[0]['input'])
        expected = ''.join(p['input'].rstrip() for p in plan['pieces'] if p['limit']==80 and p['sentence_id']=='x')
        self.assertEqual(outputs[80]['x'], expected)
        self.assertTrue(any(not p['compliant'] for p in details if p['mode']=='generate'))

    def test_approval_guard_before_any_file_or_model_access(self):
        with patch('scripts.run_chunking.prepared') as prepare:
            with self.assertRaisesRegex(ValueError, 'approval'):
                run_generation('calibrate', None)
            prepare.assert_not_called()

    def test_strict_decision_thresholds(self):
        intervals={'metrics':{'strict_compliance':{'ci95':[.001,.1]},'sentence_exact':{'ci95':[-.019,.1]}}}
        deltas={'candidates31+':.01,'length121+':.01}
        self.assertTrue(decide(intervals,deltas)['worked_under_frozen_rule'])
        intervals['metrics']['strict_compliance']['ci95'][0]=0
        self.assertFalse(decide(intervals,deltas)['worked_under_frozen_rule'])
        intervals['metrics']['strict_compliance']['ci95'][0]=.01
        intervals['metrics']['sentence_exact']['ci95'][0]=-.02
        self.assertFalse(decide(intervals,deltas)['worked_under_frozen_rule'])
        intervals['metrics']['sentence_exact']['ci95'][0]=0
        deltas['length121+']=0
        self.assertFalse(decide(intervals,deltas)['worked_under_frozen_rule'])

    def test_boundary_diagnostic_detects_lost_separator(self):
        row={'id':'x','input':'cok iyi','target':'çok iyi','category':'tam'}
        before=summarize([row],{'x':'çok iyi'})['examples']
        systems={'sft_zero_shot_chunk80':summarize([row],{'x':'çokiyi'})['examples']}
        detail=[{'limit':80,'sentence_id':'x','index':0,'start':0,'end':4,'input':'cok ','output':'çok'},
                {'limit':80,'sentence_id':'x','index':1,'start':4,'end':7,'input':'iyi','output':'iyi'}]
        boundaries,regressions=boundary_diagnostics(detail,[row],before,systems)
        self.assertTrue(boundaries[0]['trailing_whitespace_changed'])
        self.assertEqual(len(regressions[80]),1)
        self.assertEqual(regressions[80][0]['boundaries'],[4])


if __name__=='__main__':
    unittest.main()
