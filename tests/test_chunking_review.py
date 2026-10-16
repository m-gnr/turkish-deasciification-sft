import unittest
from scripts.finalize_chunking import regression_kind, select_examples


class ChunkingReviewTests(unittest.TestCase):
    def test_whitespace_diagnostic_does_not_hide_spelling_or_case(self):
        self.assertEqual(regression_kind('çok iyi','çokiyi'),'whitespace_only')
        self.assertEqual(regression_kind('çok\t iyi','çok iyi'),'whitespace_only')
        self.assertEqual(regression_kind('çok iyi','çok iyı'),'content_changed')
        self.assertEqual(regression_kind('İyi','iyi'),'content_changed')
        self.assertEqual(regression_kind('çok iyi','çok iyi'),'exact')

    def test_review_is_unique_bounded_and_represents_both_types(self):
        rows=[{'id':str(i),'diagnostic_kind':'content_changed' if i%2 else 'whitespace_only'} for i in range(30)]
        chosen=select_examples(rows)
        self.assertEqual(len(chosen),10)
        self.assertEqual(len({r['id'] for r in chosen}),10)
        self.assertEqual(sum(r['diagnostic_kind']=='content_changed' for r in chosen),5)
        self.assertEqual(chosen,select_examples(rows))
        self.assertEqual(len(select_examples(rows[:3])),3)


if __name__=='__main__':
    unittest.main()
