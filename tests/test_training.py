import unittest
from scripts.train_lora import encode_example


class FakeTokenizer:
    eos_token_id = 999

    def apply_chat_template(self, messages, **kwargs):
        assert kwargs['enable_thinking'] is False
        assert messages[-1]['role'] == 'user'
        assert all(m['role'] != 'assistant' for m in messages)
        return 'PROMPT:' + messages[-1]['content']

    def encode(self, text, **kwargs):
        return list(text.encode('utf-8'))


class TrainingTests(unittest.TestCase):
    def test_only_answer_and_eos_are_supervised(self):
        tokenizer = FakeTokenizer()
        row = {'id': 'x', 'input': 'cok', 'target': 'çok'}
        result = encode_example(tokenizer, row, 100)
        prefix = len('PROMPT:cok'.encode())
        self.assertEqual(result['labels'][:prefix], [-100] * prefix)
        self.assertEqual(result['labels'][prefix:], list('çok'.encode()) + [999])
        self.assertEqual(result['input_ids'][prefix:], result['labels'][prefix:])
        self.assertEqual(len(result['attention_mask']), len(result['labels']))

    def test_target_is_never_silently_truncated(self):
        with self.assertRaisesRegex(ValueError, 'refusing to truncate'):
            encode_example(FakeTokenizer(), {'id': 'x', 'input': 'cok', 'target': 'çok'}, 3)
