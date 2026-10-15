"""Verify a frozen dataset's hashes, corruption rules and protected-source separation."""
import argparse
import json
from pathlib import Path

from deasciification.data import (audit, comparison_key, digest, protected_match, read_jsonl)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.directory / 'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        if digest(args.directory / name) != expected:
            raise ValueError(f'Output checksum mismatch: {name}')
    protected = []
    for name, expected in manifest['protected_files'].items():
        if digest(name) != expected:
            raise ValueError(f'Protected data changed: {name}; build a new dataset version')
        protected.extend(read_jsonl(name))
    keys = {comparison_key(r[f]) for r in protected for f in ('input', 'target')}
    splits = {s: read_jsonl(args.directory / f'{s}.jsonl') for s in ('train', 'validation', 'test')}
    result = audit(splits)
    sources = read_jsonl(args.directory / 'sources.jsonl')
    by_id = {r['source_id']: r for r in sources}
    if len(by_id) != len(sources):
        raise ValueError('Source split assignments are not unique')
    for split, rows in splits.items():
        for row in rows:
            source = by_id[row['source_id']]
            if source['split'] != split or source['target'] != row['target'] or row['split'] != split:
                raise ValueError('Source assignment/target mismatch')
    for row in sources:
        if any(protected_match(comparison_key(row['target']), key) for key in keys):
            raise ValueError(f"Protected overlap: {row['source_id']}")
    result['protected_overlaps'] = 0
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
