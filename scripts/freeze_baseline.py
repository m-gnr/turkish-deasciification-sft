"""Verify saved validation predictions and freeze their hashes without inference."""
import argparse
import json
from pathlib import Path

from deasciification.evaluation import read_jsonl
from scripts.compare_prompts import digest, save, summarize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=Path('reports/validation-prompts/boun-v1-20261015-batch8'))
    parser.add_argument('--data', type=Path, default=Path('data/prepared/boun-v1'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    metadata = json.loads((args.run / 'metadata.json').read_text())
    if metadata['status'] != 'complete':
        raise ValueError('Baseline run is incomplete')
    for name, expected in metadata['output_sha256'].items():
        if digest(args.run / name) != expected:
            raise ValueError(f'Changed baseline file: {name}')
    for split in ('train', 'validation'):
        if digest(args.data / 'splits' / f'{split}.jsonl') != metadata[f'{split}_sha256']:
            raise ValueError(f'Changed {split} data')
    rows = read_jsonl(args.data / 'splits/validation.jsonl')
    if len(rows) != 900 or any(r['split'] != 'validation' for r in rows):
        raise ValueError('Expected the fixed 900 validation examples')
    comparison = json.loads((args.run / 'comparison.json').read_text())
    reports, diagnostics = {}, {}
    for condition in ('zero_shot', 'five_shot', 'identity'):
        predictions = read_jsonl(args.run / f'{condition}.jsonl') if condition != 'identity' else [dict(id=r['id'], output=r['input']) for r in rows]
        current = summarize(rows, {r['id']: r['output'] for r in predictions})
        saved = json.loads((args.run / f'{condition}-scores.json').read_text())
        if current != saved or current['summary'] != comparison['summary'][condition] or current['by_category'] != comparison['by_category'][condition]:
            raise ValueError(f'Evaluator disagrees with saved {condition} scores')
        reports[condition] = current['summary']
        examples = current['examples']
        diagnostics[condition] = {
            'equal_length_examples': sum(not r['errors']['unalignable'] for r in examples),
            'unequal_length_examples': sum(r['errors']['unalignable'] for r in examples),
            'required_positions_in_equal_length_outputs': sum(r['metrics']['required_correction']['total'] for r in examples if not r['errors']['unalignable']),
            'required_positions_in_unequal_length_outputs': sum(r['metrics']['required_correction']['total'] for r in examples if r['errors']['unalignable']),
            'candidate_positions_penalized_by_noncompliance': sum(r['metrics']['candidate_accuracy']['total'] for r in examples if r['errors']['rule_violation']),
            'identity_outputs': sum(r['output'] == r['input'] for r in examples),
            'token_limit_outputs': sum(r.get('reached_token_limit', False) for r in predictions),
        }
    files = [*sorted(args.run.glob('*.json')), *sorted(args.run.glob('*.jsonl')),
             args.data / 'splits/train.jsonl', args.data / 'splits/validation.jsonl',
             Path('deasciification/evaluation.py'), Path('deasciification/config.py'),
             Path('deasciification/inference.py'), Path('deasciification/prompting.py')]
    frozen = {'baseline_id': 'qwen3-1.7b-boun-v1-pre-sft-batch8',
              'run': str(args.run), 'model': metadata['model'], 'revision': metadata['revision'],
              'verification': 'All saved example scores, summaries, categories and recorded output hashes match.',
              'evaluation_policy': 'NFC only; any rule violation zeros all primary character/word units. Error counts are overlapping diagnostics; unequal-length outputs have no positional error counts.',
              'post_sft_protocol': {'split': 'validation', 'examples': 900, 'conditions': ['zero_shot', 'five_shot'],
                                    'demonstrations': str(args.run / 'demonstrations.json'),
                                    'batch_size': 8, 'max_new_tokens': 256, 'do_sample': False, 'enable_thinking': False,
                                    'selection': 'strict_compliance first, sentence_exact as tie breaker',
                                    'test': 'Evaluate the separate 900 test examples only after checkpoint and prompt selection is frozen.'},
              'sha256': {str(p): digest(p) for p in files}, 'summary': reports, 'diagnostics': diagnostics}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    save(args.output, frozen)
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
