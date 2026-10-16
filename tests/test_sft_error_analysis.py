import unittest

from deasciification.evaluation import allowed, score
from scripts.analyze_sft_errors import classify, tr_lower, repair, mcnemar, paired, normalized, violation_signals


class ErrorAnalysisTests(unittest.TestCase):
    def test_turkish_case_and_allowed_uppercase_i(self):
        self.assertEqual(tr_lower('Iİıi'), 'ıiıi')
        self.assertEqual(classify('ISIK', 'İSİK'), 'compliant')
        self.assertEqual(classify('I', 'ı'), 'case')
        self.assertEqual(classify('İ', 'i'), 'case')
        self.assertEqual(classify('I', 'i'), 'case')
        self.assertEqual(classify('i', 'I'), 'case')
        self.assertEqual(classify('İ', 'I'), 'letter')

    def test_mutually_exclusive_categories_and_priority(self):
        cases = [('', 'empty'), ('"çok iyi"', 'format'), ('çok', 'prefix'),
                 ('çok iyi iyi', 'word_repeat'), ('çok iyi bugün', 'word_add'),
                 ('çok  iyi', 'punctuation'), ('Çok iyi', 'case'),
                 ('çok iyilik', 'longer'), ('çok iy', 'prefix')]
        for output, expected in cases:
            with self.subTest(output=output):
                self.assertEqual(classify('cok iyi', output), expected)
        self.assertEqual(classify('cok da iyi', 'çok iyi'), 'word_delete')
        self.assertEqual(classify('cok iyi', 'çok iyi'), 'compliant')
        self.assertEqual(classify('cok iyi', 'çok', at_limit=True), 'limit')
        self.assertEqual(classify('cok iyi', '', at_limit=True), 'empty')

    def test_repair_preserves_non_candidates_and_source_shape(self):
        for source, output in [('cok iyi', 'Açıklama: çok iyi!'),
                               ('I İ ı i', 'ı i I ı'),
                               ('cok da iyi', 'çok iyi'),
                               ('bir bir', 'bır'),
                               ('', 'ek metin'), ('abc', '')]:
            repaired = repair(source, output)
            self.assertTrue(allowed(source, repaired))
            self.assertEqual(len(source), len(repaired))
        self.assertEqual(repair('cok iyi', 'çok iyi!'), 'çok iyi')
        self.assertEqual(repair('cok da iyi', 'çok iyi'), 'çok da iyi')
        self.assertEqual(repair('ç ğ İ', 'c g I'), 'ç ğ İ')

    def test_repair_keeps_every_compliant_output(self):
        for source, output in [('cok iyi', 'çok ıyı'), ('ISIK', 'İSİK'), ('i', 'ı')]:
            self.assertTrue(allowed(source, output))
            self.assertEqual(repair(source, output), output)

    def test_normalization_turkish_and_nfc(self):
        self.assertEqual(normalized('Çok, İYİ!'), normalized('Cok IYI'))
        self.assertEqual(tr_lower('I\u0307'), 'i')
        self.assertNotEqual(tr_lower('I'), tr_lower('i'))

    def test_diacritic_reversal_is_not_whitespace_or_punctuation(self):
        self.assertEqual(classify('ç iyi', 'c  iyi'), 'longer')
        self.assertEqual(classify('İ', 'I'), 'letter')
        self.assertEqual(classify('ç iyi', 'ç  iyi'), 'punctuation')

    def test_overlap_signals_keep_mixed_deletion(self):
        signals = violation_signals('cok da iyi guzel', 'çok iyi güzellik')
        self.assertTrue(signals['whole_word_delete_block'])
        self.assertTrue(signals['whitespace_sequence_changed'])
        self.assertFalse(signals['repeated_bigram_proxy'])

    def test_duplicate_normalization_merges_case_and_diacritics_only_for_audit(self):
        self.assertEqual(len({normalized(c) for c in 'Iİıi'}), 1)
        self.assertEqual(normalized('ÇÖĞÜŞ'), normalized('cogus'))
        self.assertFalse(allowed('İ', 'i'))

    def test_mcnemar_exact(self):
        self.assertEqual(mcnemar(0, 0), 1)
        self.assertEqual(mcnemar(5, 5), 1)
        self.assertAlmostEqual(mcnemar(0, 5), .0625)
        self.assertEqual(mcnemar(2, 8), mcnemar(8, 2))

    def test_paired_direction_counts_clusters_and_reproducibility(self):
        rows = [{'id': str(i), 'source_id': str(i//2), 'input': 'c', 'target': 'ç'} for i in range(4)]
        before = [score(r, out) for r, out in zip(rows, ['ç', 'ç', 'x', 'c'])]
        after = [score(r, out) for r, out in zip(rows, ['ç', 'x', 'ç', 'c'])]
        result = paired(rows, before, after)
        self.assertEqual(result, paired(rows, before, after))
        self.assertEqual(result['groups'], 2)
        self.assertEqual(result['metrics']['sentence_exact']['difference'], 0)
        self.assertEqual(result['metrics']['sentence_exact']['before_only'], 1)
        self.assertEqual(result['metrics']['sentence_exact']['after_only'], 1)
        self.assertEqual(result['metrics']['sentence_exact']['both_yes'], 1)
        self.assertEqual(result['metrics']['sentence_exact']['both_no'], 1)


if __name__ == '__main__':
    unittest.main()
