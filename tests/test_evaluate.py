import unittest
from deasciification.evaluation import aggregate, score


def example(source, target, output, **extra):
    return score(dict(id='test', category='test', input=source, target=target, **extra), output)


class EvaluationTests(unittest.TestCase):
    def test_missing_and_unnecessary_are_distinct(self):
        self.assertEqual(example('cok', 'çok', 'cok')['errors']['missing_correction'], 1)
        r = example('ise', 'ise', 'işe')
        self.assertEqual(r['errors']['unnecessary_correction'], 1)
        self.assertEqual(r['metrics']['strict_compliance']['rate'], 1)

    def test_wrong_word_overlaps_character_error(self):
        r = example('ise', 'işe', 'ışe')
        self.assertEqual(r['errors']['wrongly_changed_word'], 1)
        self.assertEqual(r['errors']['unnecessary_correction'], 1)
        self.assertEqual(r['errors']['missing_correction'], 0)

    def test_illegal_change_penalizes_all_primary_units(self):
        r = example('işe cok', 'işe çok', 'ise çok')
        self.assertEqual(r['errors']['rule_violation'], 1)
        self.assertEqual(r['metrics']['candidate_accuracy']['correct'], 0)
        self.assertEqual(r['metrics']['required_correction']['correct'], 0)
        self.assertEqual(r['metrics']['candidate_accuracy_compliant_only']['total'], 0)

    def test_length_change_is_not_aligned(self):
        for output in ['çok açıklama', 'ço', ' çok']:
            r = example('cok', 'çok', output)
            self.assertEqual(r['errors']['unalignable'], 1)
            self.assertEqual(r['error_positions'], [])

    def test_unaligned_missing_count_is_unobserved_not_success(self):
        r = example('cok', 'çok', 'çok!')
        self.assertEqual(r['errors']['missing_correction'], 0)
        self.assertEqual(r['errors']['unalignable'], 1)
        self.assertEqual(r['metrics']['required_correction'],
                         {'correct': 0, 'total': 1, 'rate': 0})

    def test_equal_length_does_not_imply_compliance(self):
        r = example('cok iyi', 'çok iyi', 'cok iyi'.upper())
        self.assertEqual(r['errors']['unalignable'], 0)
        self.assertEqual(r['errors']['rule_violation'], 1)
        self.assertEqual(r['metrics']['candidate_accuracy']['correct'], 0)

    def test_candidate_accuracy_is_micro_averaged_and_partitioned(self):
        rows = [example('cok', 'çok', 'çok'), example('iiii', 'ıııı', 'iiii'),
                example('s', 'ş', 'ş!')]
        result = aggregate(rows)['metrics']
        self.assertEqual(result['candidate_accuracy'],
                         {'correct': 2, 'total': 7, 'rate': 2 / 7})
        for key in ('correct', 'total'):
            self.assertEqual(result['candidate_accuracy'][key],
                             result['required_correction'][key]
                             + result['candidate_preservation'][key])
        self.assertEqual(result['candidate_accuracy_compliant_only']['total'], 6)

    def test_nfc_only_and_raw_output(self):
        raw = 'c\u0327ok'
        r = example('cok', 'çok', raw)
        self.assertEqual(r['metrics']['sentence_exact']['rate'], 1)
        self.assertEqual(r['output'], raw)
        self.assertEqual(example('cok ', 'çok ', 'çok')['metrics']['sentence_exact']['rate'], 0)

    def test_turkish_uppercase(self):
        self.assertEqual(example('IZMIR', 'İZMİR', 'İZMİR')['metrics']['sentence_exact']['rate'], 1)
        self.assertEqual(example('Isik', 'Işık', 'Işık')['metrics']['strict_compliance']['rate'], 1)

    def test_zero_denominator(self):
        self.assertIsNone(example('ev', 'ev', 'ev')['metrics']['required_correction']['rate'])

    def test_invalid_target_rejected(self):
        with self.assertRaises(ValueError):
            example('ş', 's', 's')

    def test_pair_requires_both_correct_and_two_members(self):
        a = example('ise', 'işe', 'işe', pair_id='p', focus_word_index=0)
        b = example('ise', 'ise', 'işe', pair_id='p', focus_word_index=0)
        self.assertEqual(aggregate([a, b])['metrics']['minimal_pair_success']['rate'], 0)
        with self.assertRaises(ValueError):
            aggregate([a])

    def test_pilot_targets_and_perfect_predictions(self):
        from pathlib import Path
        from deasciification.evaluation import read_jsonl
        rows = read_jsonl(Path('data/pilot.jsonl'))
        result = aggregate([score(r, r['target']) for r in rows])
        self.assertEqual(result['examples'], 34)
        for metric in result['metrics'].values():
            if metric['total']:
                self.assertEqual(metric['rate'], 1)
        self.assertEqual(result['metrics']['minimal_pair_success']['total'], 4)

    def test_source_and_pair_groups_are_transitive(self):
        from deasciification.evaluation import resampling_groups
        rows = [dict(id='a', source_id='s', pair_id='p'),
                dict(id='b', source_id='s'), dict(id='c', pair_id='p'),
                dict(id='d', source_id='other')]
        self.assertEqual(resampling_groups(rows), [['a', 'b', 'c'], ['d']])

    def test_raw_pilot_unicode_coverage_and_groups(self):
        from pathlib import Path
        import unicodedata
        from deasciification.evaluation import read_jsonl, resampling_groups
        from deasciification.validation import CORRUPT, derivable, focus
        rows = read_jsonl(Path('data/pilot.jsonl'))
        covered = set()
        pairs = {}
        for row in rows:
            for field in ('input', 'target'):
                self.assertTrue(unicodedata.is_normalized('NFC', row[field]))
                self.assertNotIn('\u0307', row[field])
            self.assertTrue(derivable(row['input'], row['target'])[0])
            self.assertTrue(row['source_id'])
            covered.update(t for i, t in zip(row['input'], row['target']) if i != t)
            if row.get('pair_id'):
                pairs.setdefault(row['pair_id'], []).append(focus(row))
        self.assertTrue(set(CORRUPT) <= covered)
        for pair in pairs.values():
            self.assertEqual(len(pair), 2)
            self.assertEqual(pair[0][0], pair[1][0])
            self.assertNotEqual(pair[0][1], pair[1][1])
        groups = resampling_groups(rows)
        self.assertIn(['p002', 'p028'], groups)
        self.assertIn(['p017', 'p018', 'p031'], groups)

    def test_all_nontrivial_partial_masks(self):
        # Test fixtures only, never training data. Exercise every mixed mask.
        from itertools import product
        from deasciification.validation import CORRUPT
        target = 'çğışöü ÇĞİŞÖÜ'
        positions = [i for i, c in enumerate(target) if c in CORRUPT]
        for mask in product((False, True), repeat=len(positions)):
            if not any(mask) or all(mask):
                continue
            chars = list(target)
            for pos, change in zip(positions, mask):
                if change:
                    chars[pos] = CORRUPT[chars[pos]]
            source = ''.join(chars)
            exact = example(source, target, target)
            identity = example(source, target, source)
            self.assertEqual(exact['metrics']['sentence_exact']['rate'], 1)
            self.assertEqual(identity['errors']['missing_correction'], sum(mask))
            self.assertEqual(identity['errors']['unnecessary_correction'], 0)


if __name__ == '__main__':
    unittest.main()
