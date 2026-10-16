"""Train an answer-only LoRA adapter on the fixed BOUN training split."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import time

from deasciification.config import MODEL, REVISION
from deasciification.evaluation import allowed, read_jsonl
from deasciification.prompting import build_messages
from scripts.compare_prompts import digest, save


def encode_example(tokenizer, row, max_length):
    prompt = tokenizer.apply_chat_template(build_messages(row['input']), tokenize=False,
                                          add_generation_prompt=True, enable_thinking=False)
    prefix = tokenizer.encode(prompt, add_special_tokens=False)
    answer = tokenizer.encode(row['target'], add_special_tokens=False) + [tokenizer.eos_token_id]
    if len(prefix) + len(answer) > max_length:
        raise ValueError(f"{row['id']}: exceeds max_length; refusing to truncate target")
    return {'input_ids': prefix + answer, 'attention_mask': [1] * (len(prefix) + len(answer)),
            'labels': [-100] * len(prefix) + answer}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--train', type=Path, default=Path('data/prepared/boun-v1/splits/train.jsonl'))
    parser.add_argument('--baseline', type=Path, default=Path('reports/baselines/boun-v1-pre-sft.json'))
    parser.add_argument('--max-steps', type=int, default=-1, help='Positive values are smoke runs, not full SFT')
    parser.add_argument('--epochs', type=int, default=1)
    parser.add_argument('--accumulation', type=int, default=16)
    parser.add_argument('--max-length', type=int, default=1024)
    args = parser.parse_args()
    if args.epochs < 1 or args.accumulation < 1 or args.max_steps == 0:
        raise ValueError('Invalid training duration or accumulation')
    baseline = json.loads(args.baseline.read_text())
    if digest(args.train) != baseline['sha256'].get(str(args.train)):
        raise ValueError('Training data must match frozen baseline')
    rows = read_jsonl(args.train)
    if len(rows) != 7340 or any(r['split'] != 'train' or not allowed(r['input'], r['target']) for r in rows):
        raise ValueError('Expected 7340 valid training examples')
    import torch
    import peft
    import transformers
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, set_seed
    set_seed(42)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    encoded = [encode_example(tokenizer, r, args.max_length) for r in rows]
    device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
    dtype = torch.float16 if device != 'cpu' else torch.float32
    args.output.mkdir(parents=True, exist_ok=False)
    metadata = {'status': 'running', 'run_type': 'smoke' if args.max_steps > 0 else 'full_train',
                'model': MODEL, 'revision': REVISION, 'device': device, 'dtype': str(dtype),
                'seed': 42, 'train_sha256': digest(args.train), 'baseline_sha256': digest(args.baseline),
                'code_sha256': {str(p): digest(p) for p in [Path(__file__), Path('deasciification/prompting.py'), Path('deasciification/config.py')]},
                'torch': torch.__version__, 'transformers': transformers.__version__, 'peft': peft.__version__,
                'examples': len(rows), 'categories': dict(Counter(r['category'] for r in rows)),
                'maximum_tokens': max(len(r['input_ids']) for r in encoded),
                'answer_tokens': sum(sum(v != -100 for v in r['labels']) for r in encoded),
                'epochs': args.epochs, 'accumulation': args.accumulation, 'max_steps': args.max_steps,
                'learning_rate': 2e-4, 'loss': 'assistant target and EOS only; prompt/padding masked'}
    save(args.output / 'run.json', metadata)
    started = time.monotonic()
    try:
        model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION, local_files_only=True, dtype=dtype)
        model.config.use_cache = False
        model = get_peft_model(model, LoraConfig(task_type='CAUSAL_LM', r=8, lora_alpha=16,
                                               lora_dropout=0.05, target_modules=['q_proj', 'v_proj']))
        model.enable_input_require_grads()
        metadata['trainable_parameters'], metadata['all_parameters'] = model.get_nb_trainable_parameters()
        def collate(batch):
            length = max(len(x['input_ids']) for x in batch)
            return {key: torch.tensor([x[key] + [pad] * (length - len(x[key])) for x in batch])
                    for key, pad in [('input_ids', tokenizer.pad_token_id), ('attention_mask', 0), ('labels', -100)]}
        trainer = Trainer(model=model, train_dataset=encoded, data_collator=collate,
                          args=TrainingArguments(output_dir=str(args.output / 'checkpoints'),
                              per_device_train_batch_size=1, gradient_accumulation_steps=args.accumulation,
                              num_train_epochs=args.epochs, max_steps=args.max_steps,
                              learning_rate=2e-4, warmup_steps=max(1, math.ceil(0.03 * (args.max_steps if args.max_steps > 0 else math.ceil(len(rows) / args.accumulation) * args.epochs))), lr_scheduler_type='cosine',
                              optim='adamw_torch', gradient_checkpointing=True,
                              gradient_checkpointing_kwargs={'use_reentrant': False},
                              logging_steps=1 if args.max_steps > 0 else 10,
                              save_strategy='steps', save_steps=100, save_total_limit=2,
                              report_to='none', seed=42, data_seed=42, dataloader_pin_memory=False))
        result = trainer.train()
        if not all(torch.isfinite(p).all().item() for p in model.parameters() if p.requires_grad):
            raise ValueError('Nonfinite adapter parameters')
        model.save_pretrained(args.output / 'adapter')
        tokenizer.save_pretrained(args.output / 'adapter')
        metadata.update(status='complete', metrics=result.metrics, elapsed_seconds=time.monotonic() - started)
    except BaseException as error:
        metadata.update(status='failed', error=str(error), elapsed_seconds=time.monotonic() - started)
        raise
    finally:
        save(args.output / 'run.json', metadata)


if __name__ == '__main__':
    main()
