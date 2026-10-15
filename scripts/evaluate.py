"""Ham tahminleri veya hiç-değiştirme yöntemini puanla."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from deasciification import evaluation
from deasciification.evaluation import aggregate, read_jsonl, resampling_groups, score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('data/pilot.jsonl'))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--identity', action='store_true')
    mode.add_argument('--predictions', type=Path, help='JSONL records with id and raw output')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    rows = read_jsonl(args.data)
    if not rows:
        raise ValueError('Dataset must not be empty')
    outputs = {r['id']: r['input'] for r in rows}
    if args.predictions:
        outputs = {r['id']: r['output'] for r in read_jsonl(args.predictions)}
        if set(outputs) != {r['id'] for r in rows}:
            raise ValueError('Prediction IDs must match dataset IDs exactly')
    results = [score(row, outputs[row['id']]) for row in rows]
    groups = defaultdict(list)
    for result in results:
        groups[result['category']].append(result)
    report = {'mode': 'identity' if args.identity else 'predictions',
              'data': str(args.data),
              'data_sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
              'evaluator_sha256': hashlib.sha256(Path(evaluation.__file__).read_bytes()).hexdigest(),
              'resampling_groups': resampling_groups(rows),
              'normalization': 'NFC only; raw outputs retained',
              'summary': aggregate(results),
              'by_category': {key: aggregate(group) for key, group in groups.items()},
              'examples': results}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
