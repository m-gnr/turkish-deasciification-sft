"""Build a frozen, auditable 60/25/15 dataset from checksum-locked sources."""
import argparse
import json
import platform
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from deasciification.data import (audit, clean_sources, digest, generate, load_conllu,
                                 read_jsonl, split_sources, write_jsonl)
from deasciification.validation import CORRUPT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw/boun'))
    parser.add_argument('--source-config', type=Path, default=Path('configs/data-source.json'))
    parser.add_argument('--exclude', type=Path, action='append', default=[], help='Additional held-out JSONL; pilot always excluded')
    parser.add_argument('--output', type=Path, default=Path('data/prepared/boun-v1'))
    parser.add_argument('--seed', type=int, default=20261015)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists; choose a new version directory')
    config = json.loads(args.source_config.read_text())
    for name, entry in config['files'].items():
        if digest(args.raw_dir / name) != entry['sha256']:
            raise ValueError(f'Source checksum mismatch: {name}')
    expected = {n for n in config['files'] if n.endswith('.conllu')}
    if {p.name for p in args.raw_dir.glob('*.conllu')} != expected:
        raise ValueError('Unexpected source file set')
    excludes = [Path('data/pilot.jsonl')] + args.exclude
    protected = [r for p in excludes for r in read_jsonl(p)]
    original = load_conllu(args.raw_dir)
    print(f'Loaded {len(original)} sources; deduplicating and checking protected text...', flush=True)
    clean, rejected = clean_sources(original, protected)
    source_splits = split_sources(clean, args.seed)
    splits = {s: generate(rows, s, args.seed) for s, rows in source_splits.items()}
    checks = audit(splits)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.prepare-', dir=args.output.parent))
    try:
        for folder in ('splits', 'metadata', 'source'):
            (temp / folder).mkdir()
        for split, rows in splits.items():
            write_jsonl(temp / 'splits' / f'{split}.jsonl', rows)
        write_jsonl(temp / 'metadata' / 'sources.jsonl', [dict(r, split=s) for s, rows in source_splits.items() for r in rows])
        write_jsonl(temp / 'metadata' / 'excluded.jsonl', rejected)
        shutil.copyfile(args.raw_dir / 'LICENSE.txt', temp / 'source' / 'LICENSE.txt')
        shutil.copyfile(args.raw_dir / 'README.md', temp / 'source' / 'README.md')
        manifest = dict(schema_version=2, source=config, seed=args.seed, python=platform.python_version(),
                        source_config_sha256=digest(args.source_config),
                        protected_files={str(p): digest(p) for p in excludes},
                        code_sha256={p: digest(p) for p in ('deasciification/data.py', 'deasciification/validation.py', 'scripts/prepare_data.py')},
                        rules=dict(split='80/10/10 stratified by 0,1,>=2 corruptible positions; largest remainder',
                                   normalization='NFC only for targets; comparison key ASCII folds, lowercases, removes punctuation, collapses spaces',
                                   quality='10..500 characters, >=3 whitespace words, alphabetic content, no Unicode C categories or U+0307',
                                   near_duplicate='character trigram set Jaccard >=0.8; connected components, lexicographically first source_id',
                                   protected='substring, trigram Jaccard >=0.8 or symmetric SequenceMatcher >=0.8, autojunk=False; exclude entire component from all splits',
                                   corruption_mapping=CORRUPT, partial_probability=.5, partial_sampling='reject empty/full masks',
                                   mixture='60/25/15 exact; maximum feasible multiple of 20 per split; one variant per source',
                                   preservation='up to half preservation quota from zero-corruptible sources; at least one of each subtype'),
                        original_sources=len(original), clean_sources=len(clean), exclusions=dict(Counter(r['reason'] for r in rejected)),
                        splits={s: dict(sources=len(source_splits[s]), examples=len(rows),
                                        unused_sources=len(source_splits[s])-len(rows),
                                        variants=dict(Counter(r['variant'] for r in rows)),
                                        preservation_subtypes=dict(Counter(r['subcategory'] for r in rows if r['variant']=='koruma')))
                                for s, rows in splits.items()}, audit=checks,
                        files={p.relative_to(temp).as_posix(): digest(p) for p in sorted(temp.rglob('*')) if p.is_file()})
        (temp / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temp.rename(args.output)
    except BaseException:
        shutil.rmtree(temp)
        raise
    print(json.dumps(manifest['splits'], ensure_ascii=False, indent=2))
    print(f'Passed audit; saved {args.output}')


if __name__ == '__main__':
    main()
