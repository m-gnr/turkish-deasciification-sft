"""Batch decoding must not include padding after an early stop."""
import unittest
from types import SimpleNamespace
try:
    import torch
    from deasciification.inference import generate_batch
except ImportError:
    torch = None


class Inputs(dict):
    def to(self, device):
        return self


class Tokenizer:
    pad_token_id = 0
    eos_token_id = 9
    def apply_chat_template(self, messages, **kwargs):
        return str(messages)
    def __call__(self, prompts, **kwargs):
        self.prompts = prompts
        return Inputs(input_ids=torch.tensor([[0, 1], [2, 3]]),
                      attention_mask=torch.tensor([[0, 1], [1, 1]]))
    def decode(self, tokens, **kwargs):
        return str(tokens)


class Model:
    generation_config = SimpleNamespace(eos_token_id=[9, 10])
    def generate(self, **kwargs):
        return torch.tensor([[0, 1, 7, 9, 0], [2, 3, 8, 8, 10]])


@unittest.skipIf(torch is None, 'Optional model dependencies are not installed')
class BatchTests(unittest.TestCase):
    def test_stop_and_padding_are_distinguished(self):
        tokenizer = Tokenizer()
        result = generate_batch(tokenizer, Model(), 'cpu', ['first', 'second'])
        self.assertEqual(result, [('[7, 9]', [7, 9]), ('[8, 8, 10]', [8, 8, 10])])
        self.assertEqual(tokenizer.padding_side, 'left')
        self.assertIn('first', tokenizer.prompts[0])
        self.assertNotIn('second', tokenizer.prompts[0])
