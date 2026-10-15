import random
import unittest
from itertools import combinations

from deasciification.data import (audit, clean_sources, comparison_key, corrupt,
                                 generate, near_pairs, protected_match, shingles, split_sources)
from deasciification.validation import CORRUPT, derivable


class DataTests(unittest.TestCase):
    def test_prefix_join_matches_exhaustive_oracle(self):
        rng = random.Random(31)
        keys = [''.join(rng.choices('abcde ', k=rng.randint(3, 50))) for _ in range(100)]
        keys += [k[:-1] + 'a' for k in keys] + keys[:5]
        expected = set()
        for i, j in combinations(range(len(keys)), 2):
            a, b = shingles(keys[i]), shingles(keys[j])
            if len(a & b) / len(a | b) >= .8:
                expected.add((i, j))
        self.assertEqual(set(near_pairs(keys)), expected)

    def test_unicode_and_format_are_preserved(self):
        target = '  ÇĞİÖŞÜ çğıöşü\tI i!\n  '
        full = corrupt(target, 'tam', random.Random(0))
        self.assertEqual(full, '  CGIOSU cgiosu\tI i!\n  ')
        for seed in range(100):
            inp = corrupt(target, 'kismi', random.Random(seed))
            ok, n, k = derivable(inp, target)
            self.assertTrue(ok and 0 < k < n)
        self.assertEqual(corrupt(target, 'koruma', random.Random(0)), target)
        with self.assertRaises(ValueError):
            corrupt('bir kişi' .replace('ş', 's'), 'kismi', random.Random(0))

    def test_partial_mask_rejection(self):
        class Fake:
            def __init__(self):
                self.values = iter([.9, .9, .1, .1, .1, .9])
            def random(self):
                return next(self.values)
        self.assertEqual(corrupt('şü', 'kismi', Fake()), 'sü')

    def test_protected_ascii_case_and_containment(self):
        self.assertEqual(comparison_key('İŞ IŞIK'), 'is isik')
        self.assertTrue(protected_match(comparison_key('Bugün işe geldim.'), comparison_key('bugun ise geldim')))
        protected = [dict(input='ogrenci kartini unutmusum', target='öğrenci kartını unutmuşum')]
        rows = [dict(source_id='a', target='Ben öğrenci kartını unutmuşum dedim.'),
                dict(source_id='b', target='Mutfaktaki yemeklerin hepsi soğumuş.'),
                dict(source_id='c', target='Mutfaktaki yemeklerin hepsi soğumuş!')]
        kept, rejected = clean_sources(rows, protected)
        self.assertEqual([r['source_id'] for r in kept], ['b'])
        self.assertEqual({r['reason'] for r in rejected}, {'duplicate', 'protected_overlap'})

    def test_transitive_duplicate_component(self):
        # Pairwise edges form A-B-C while A and C are below the threshold.
        base = 'abcdefghijklmnopqrstuvwxyz0123456789'
        middle = base[:8] + 'X' + base[9:]
        keys = [base, middle, middle[:24] + 'Z' + middle[25:]]
        self.assertEqual(set(near_pairs(keys)), {(0, 1), (1, 2)})
        rows = [dict(source_id=str(i), target='bir ' + k + ' son') for i, k in enumerate(keys)]
        kept, rejected = clean_sources(rows, [])
        self.assertEqual(len(kept), 1)
        self.assertEqual(len(rejected), 2)

    def test_split_before_generation_and_exact_mix(self):
        rng = random.Random(3)
        rows = []
        for i in range(600):
            body = ''.join(rng.choices('abcdefgijklmnoprstuvyz', k=30))
            rows.append(dict(source_id=str(i), target=body + (' güzel dünya' if i % 10 else ' herkes evde')))
        splits = split_sources(rows, 42)
        self.assertEqual(splits, split_sources(list(reversed(rows)), 42))
        generated = {s: generate(r, s, 42) for s, r in splits.items()}
        self.assertTrue(audit(generated)['passed'])
        for s, records in generated.items():
            self.assertEqual(records, generate(splits[s], s, 42))
            self.assertEqual(len(records) % 20, 0)
            self.assertEqual(sum(r['variant'] == 'tam' for r in records), len(records)*.6)
            self.assertTrue({r['source_id'] for r in records} <= {r['source_id'] for r in splits[s]})
        self.assertEqual(sum(map(len, splits.values())), len(rows))

    def test_insufficient_preservation_fails(self):
        with self.assertRaises(ValueError):
            generate([dict(source_id=str(i), target='güzel dünya') for i in range(100)], 'train', 1)


if __name__ == '__main__':
    unittest.main()
