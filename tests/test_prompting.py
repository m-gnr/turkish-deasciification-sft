import unittest
from deasciification.prompting import build_messages, select_examples
from scripts.compare_prompts import summarize, paired_intervals


class PromptTests(unittest.TestCase):
    def test_frozen_training_selection(self):
        train = [{'id': str(i), 'source_id': str(i), 'split': 'train',
                  'category': cat, 'input': 'a' * 50, 'target': 'b' * 50}
                 for i, cat in enumerate(['tam'] * 5 + ['kismi'] * 2 + ['koruma'] * 2)]
        a = select_examples(train, [{'source_id': 'validation'}])
        self.assertEqual(a, select_examples(train[::-1], [{'source_id': 'validation'}]))
        self.assertEqual(len(a), 5)
        with self.assertRaises(ValueError):
            select_examples(train, [{'source_id': '0'}])

    def test_only_demo_targets_in_prompt(self):
        messages = build_messages('validation input', [{'input': 'demo', 'target': 'answer', 'category': 'hidden'}])
        self.assertEqual([m['role'] for m in messages], ['system', 'user', 'assistant', 'user'])
        self.assertEqual(messages[-1]['content'], 'validation input')
        self.assertNotIn('hidden', str(messages))
        self.assertEqual(len(build_messages('input')), 2)

    def test_identical_predictions_have_zero_difference(self):
        rows = [{'id': 'a', 'source_id': 'a', 'category': 'tam', 'input': 'c', 'target': 'ç'}]
        report = summarize(rows, {'a': 'ç'})
        result = paired_intervals(rows, report, report)
        for metric in result['metrics'].values():
            self.assertEqual(metric['difference'], 0)
            self.assertEqual(metric['ci95'], [0, 0])

    def test_bootstrap_uses_each_conditions_denominator(self):
        rows = [{'id': 'a', 'source_id': 'shared', 'category': 'tam', 'input': 'c', 'target': 'ç'},
                {'id': 'b', 'source_id': 'shared', 'category': 'tam', 'input': 's', 'target': 'ş'}]
        zero = summarize(rows, {'a': 'ç', 'b': 'invalid'})
        few = summarize(rows, {'a': 'ç', 'b': 's'})
        metric = paired_intervals(rows, zero, few)['metrics']['candidate_accuracy_compliant_only']
        self.assertEqual(metric['difference'], -.5)
        self.assertEqual(metric['ci95'], [-.5, -.5])
