"""Run the pinned, pre-SFT model on the pilot without exposing targets."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import torch
import transformers

from deasciification.config import MODEL, REVISION, YONERGE
from deasciification.inference import generate, load_model
from deasciification import config, inference
from deasciification.evaluation import read_jsonl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('data/pilot.jsonl'))
    parser.add_argument('--output', type=Path, default=Path('reports/pilot-base/pilot-base-predictions.jsonl'))
    args = parser.parse_args()
    rows = read_jsonl(args.data)
    if not rows:
        raise ValueError('Empty dataset')
    metadata_path = args.output.with_suffix('.metadata.json')
    if args.output.exists() or metadata_path.exists():
        raise FileExistsError('Choose a new output path; existing runs are preserved')
    tokenizer, model, device, dtype = load_model()
    torch.manual_seed(0)
    metadata = {
        'model': MODEL, 'revision': REVISION, 'condition': 'pre_sft_zero_shot',
        'instruction': YONERGE, 'device': device, 'dtype': str(dtype),
        'torch': torch.__version__, 'transformers': transformers.__version__,
        'enable_thinking': False, 'do_sample': False, 'max_new_tokens': 128,
        'seed': 0, 'data_sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
        'inference_sha256': hashlib.sha256(Path(inference.__file__).read_bytes()).hexdigest(),
        'config_sha256': hashlib.sha256(Path(config.__file__).read_bytes()).hexdigest(),
        'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'started_at': datetime.now(timezone.utc).isoformat(),
        'expected_examples': len(rows), 'completed_examples': 0, 'status': 'running',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    with args.output.open('x', encoding='utf-8') as stream:
        for index, row in enumerate(rows, 1):
            started = time.monotonic()
            output, tokens = generate(tokenizer, model, device, row['input'])
            prediction = {
                'id': row['id'], 'output': output, 'generated_token_ids': tokens,
                'generated_tokens': len(tokens), 'reached_token_limit': len(tokens) >= 128,
                'seconds': time.monotonic() - started,
            }
            stream.write(json.dumps(prediction, ensure_ascii=False) + '\n')
            stream.flush()
            metadata['completed_examples'] = index
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
            print(f"[{index}/{len(rows)}] {row['id']}: {output!r}", flush=True)
    metadata.update(status='complete', finished_at=datetime.now(timezone.utc).isoformat(),
                    predictions_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest())
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
