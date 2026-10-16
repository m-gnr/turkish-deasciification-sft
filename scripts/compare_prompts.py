"""Evaluate frozen zero/five-shot prompts on validation before SFT."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from deasciification.config import MODEL, REVISION, YONERGE
from deasciification.evaluation import aggregate, read_jsonl, resampling_groups, score
from deasciification.prompting import select_examples


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def summarize(rows, outputs):
    if set(outputs) != {r['id'] for r in rows}:
        raise ValueError('Prediction IDs must match validation exactly')
    results = [score(r, outputs[r['id']]) for r in rows]
    categories = defaultdict(list)
    for result in results:
        categories[result['category']].append(result)
    return {'summary': aggregate(results),
            'by_category': {k: aggregate(v) for k, v in categories.items()},
            'examples': results}


def paired_intervals(rows, zero, few):
    import random
    rng = random.Random(20261015)
    groups = resampling_groups(rows)
    za = {r['id']: r for r in zero['examples']}
    fa = {r['id']: r for r in few['examples']}
    intervals = {}
    for metric in zero['summary']['metrics']:
        if metric == 'minimal_pair_success':
            continue
        values = [(sum(fa[i]['metrics'][metric]['correct'] for i in group),
                   sum(fa[i]['metrics'][metric]['total'] for i in group),
                   sum(za[i]['metrics'][metric]['correct'] for i in group),
                   sum(za[i]['metrics'][metric]['total'] for i in group)) for group in groups]
        if not sum(v[1] for v in values) or not sum(v[3] for v in values):
            continue
        samples = []
        for _ in range(2000):
            selected = rng.choices(values, k=len(values))
            few_total, zero_total = sum(v[1] for v in selected), sum(v[3] for v in selected)
            if few_total and zero_total:
                samples.append(sum(v[0] for v in selected) / few_total - sum(v[2] for v in selected) / zero_total)
        samples.sort()
        intervals[metric] = {'difference': sum(v[0] for v in values) / sum(v[1] for v in values) - sum(v[2] for v in values) / sum(v[3] for v in values),
                             'ci95': [samples[int(.025 * len(samples))], samples[int(.975 * len(samples))]]}
    return {'direction': 'five_shot minus zero_shot', 'seed': 20261015,
            'replicates': 2000, 'method': 'paired source/pair cluster percentile bootstrap',
            'groups': len(groups), 'metrics': intervals}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train', type=Path, default=Path('data/prepared/boun-v1/splits/train.jsonl'))
    parser.add_argument('--validation', type=Path, default=Path('data/prepared/boun-v1/splits/validation.jsonl'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    train, rows = read_jsonl(args.train), read_jsonl(args.validation)
    if not rows or any(r.get('split') != 'validation' for r in rows):
        raise ValueError('Expected nonempty validation split')
    examples = select_examples(train, rows)
    args.output.mkdir(parents=True, exist_ok=False)
    save(args.output / 'demonstrations.json', {'selection': 'SHA256(few-shot-v1:ID), input length 40..150; 3 tam, 1 kismi, 1 koruma; no validation outcome selection', 'examples': examples})
    import torch
    import transformers
    from deasciification.inference import load_model, generate_batch
    tokenizer, model, device, dtype = load_model()
    torch.manual_seed(0)
    metadata = {'model': MODEL, 'revision': REVISION, 'instruction': YONERGE,
                'device': device, 'dtype': str(dtype), 'torch': torch.__version__,
                'transformers': transformers.__version__, 'seed': 0,
                'enable_thinking': False, 'do_sample': False, 'max_new_tokens': 256, 'batch_size': 8, 'padding_side': 'left',
                'train_sha256': digest(args.train), 'validation_sha256': digest(args.validation),
                'demonstrations_sha256': digest(args.output / 'demonstrations.json'),
                'code_sha256': {str(p): digest(p) for p in [Path(__file__), *Path('deasciification').glob('*.py')]},
                'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'running',
                'expected_per_condition': len(rows), 'completed': {}}
    save(args.output / 'metadata.json', metadata)
    reports = {}
    for condition, demos in [('zero_shot', []), ('five_shot', examples)]:
        outputs = {}
        with (args.output / f'{condition}.jsonl').open('x') as stream:
            for offset in range(0, len(rows), 8):
                batch = rows[offset:offset + 8]
                start = time.monotonic()
                predictions = generate_batch(tokenizer, model, device, [r['input'] for r in batch], demos, 256)
                seconds = time.monotonic() - start
                for row, (output, tokens) in zip(batch, predictions):
                    prediction = {'id': row['id'], 'output': output, 'generated_token_ids': tokens,
                                  'generated_tokens': len(tokens), 'reached_token_limit': len(tokens) >= 256,
                                  'seconds': seconds / len(batch), 'batch_seconds': seconds,
                                  'batch_offset': offset}
                    stream.write(json.dumps(prediction, ensure_ascii=False) + '\n')
                    outputs[row['id']] = output
                stream.flush()
                metadata['completed'][condition] = offset + len(batch)
                save(args.output / 'metadata.json', metadata)
                print(f'{condition}: {offset + len(batch)}/{len(rows)} ({seconds:.1f}s)', flush=True)
        reports[condition] = summarize(rows, outputs)
        save(args.output / f'{condition}-scores.json', reports[condition])
    reports['identity'] = summarize(rows, {r['id']: r['input'] for r in rows})
    save(args.output / 'identity-scores.json', reports['identity'])
    comparison = {'summary': {k: r['summary'] for k, r in reports.items()},
                  'by_category': {k: r['by_category'] for k, r in reports.items()},
                  'paired_bootstrap': paired_intervals(rows, reports['zero_shot'], reports['five_shot'])}
    save(args.output / 'comparison.json', comparison)
    metadata.update(status='complete', finished_at=datetime.now(timezone.utc).isoformat(),
                    output_sha256={p.name: digest(p) for p in args.output.glob('*') if p.name != 'metadata.json'})
    save(args.output / 'metadata.json', metadata)
    print(json.dumps(comparison['summary'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
