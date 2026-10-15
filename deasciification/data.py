"""Deterministic source splitting and Turkish corruption (standard library only)."""
import hashlib
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from .validation import CORRUPT, derivable


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_jsonl(path, rows):
    Path(path).write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n'
                                  for r in rows), encoding='utf-8')


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def comparison_key(text):
    # Comparison only: never apply this to targets. Explicit Turkish I mapping.
    text = unicodedata.normalize('NFC', text)
    text = ''.join(CORRUPT.get(c, c) for c in text).lower()
    return ' '.join(re.findall(r'\w+', text))


def shingles(text):
    return {text[i:i + 3] for i in range(len(text) - 2)} or {text}


def near_pairs(keys):
    """Exact >= 0.8 character-trigram Jaccard join using prefix filtering.

    A common global order and prefixes of n-ceil(.8*n)+1 guarantee candidate
    recall. Integer arithmetic avoids boundary-dependent floating point errors.
    """
    sets = [shingles(k) for k in keys]
    frequencies = Counter(s for group in sets for s in group)
    postings = defaultdict(list)
    for i, group in enumerate(sets):
        prefix = sorted(group, key=lambda s: (frequencies[s], s))[:len(group) - (4 * len(group) + 4) // 5 + 1]
        candidates = {j for s in prefix for j in postings[s]}
        for j in sorted(candidates):
            other = sets[j]
            if 5 * min(len(group), len(other)) < 4 * max(len(group), len(other)):
                continue
            common = len(group & other)
            if 5 * common >= 4 * (len(group) + len(other) - common):
                yield j, i
        for s in prefix:
            postings[s].append(i)


def protected_match(a, b):
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    sa, sb = shingles(a), shingles(b)
    if 5 * len(sa & sb) >= 4 * len(sa | sb):
        return True
    if 5 * min(len(a), len(b)) < 2 * (len(a) + len(b)):
        return False
    # Symmetric because SequenceMatcher may depend on argument order.
    return max(SequenceMatcher(None, a, b, autojunk=False).ratio(),
               SequenceMatcher(None, b, a, autojunk=False).ratio()) >= .8


def load_conllu(raw_dir):
    rows = []
    seen = set()
    for path in sorted(Path(raw_dir).glob('*.conllu')):
        for block in path.read_text(encoding='utf-8').strip().split('\n\n'):
            meta = dict(line[2:].split(' = ', 1) for line in block.splitlines()
                        if line.startswith('# ') and ' = ' in line)
            if 'sent_id' not in meta or 'text' not in meta:
                raise ValueError(f'Missing sent_id/text: {path}')
            sid = 'boun:' + meta['sent_id']
            if sid in seen:
                raise ValueError(f'Duplicate source ID: {sid}')
            seen.add(sid)
            rows.append(dict(source_id=sid, target=unicodedata.normalize('NFC', meta['text']),
                             original_file=path.name, original_sent_id=meta['sent_id']))
    if not rows:
        raise ValueError('No source sentences')
    return sorted(rows, key=lambda r: r['source_id'])


def clean_sources(rows, protected):
    """Collapse connected near-duplicate components; exclude whole protected components."""
    rejected, valid = [], []
    for row in rows:
        text = row['target']
        if not (10 <= len(text) <= 500 and len(text.split()) >= 3
                and '\u0307' not in text and any(c.isalpha() for c in text)
                and not any(unicodedata.category(c).startswith('C') for c in text)):
            rejected.append(dict(source_id=row['source_id'], reason='quality_filter'))
        else:
            valid.append(row)
    keys = [comparison_key(r['target']) for r in valid]
    parents = list(range(len(valid)))

    def root(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    for a, b in near_pairs(keys):
        parents[root(b)] = root(a)
    groups = defaultdict(list)
    for i in range(len(valid)):
        groups[root(i)].append(i)
    protected_keys = sorted({comparison_key(r[f]) for r in protected for f in ('input', 'target')})
    kept = []
    for members in groups.values():
        hits = [valid[i]['source_id'] for i in members
                if any(protected_match(keys[i], p) for p in protected_keys)]
        representative = members[0]
        for i in members:
            if hits or i != representative:
                rejected.append(dict(source_id=valid[i]['source_id'],
                                     reason='protected_overlap' if hits else 'duplicate',
                                     representative=valid[representative]['source_id'], protected_members=hits))
        if not hits:
            kept.append(valid[representative])
    return kept, rejected


def eligible(text):
    return sum(c in CORRUPT for c in text)


def split_sources(rows, seed):
    """80/10/10, stratified by 0, 1, >=2 corruptible positions."""
    result = {s: [] for s in ('train', 'validation', 'test')}
    for bucket in range(3):
        pool = [r for r in rows if min(eligible(r['target']), 2) == bucket]
        # Stable hash ordering is independent of input order and Python RNG versions.
        pool.sort(key=lambda r: hashlib.sha256(f"{seed}:split:{r['source_id']}".encode()).hexdigest())
        counts = [len(pool) * p // 10 for p in (8, 1, 1)]
        for i in sorted(range(3), key=lambda i: (-(len(pool) * (8, 1, 1)[i] % 10), i))[:len(pool) - sum(counts)]:
            counts[i] += 1
        offset = 0
        for split, n in zip(result, counts):
            result[split].extend(pool[offset:offset + n])
            offset += n
    return result


def corrupt(text, variant, rng):
    positions = [i for i, c in enumerate(text) if c in CORRUPT]
    if variant == 'koruma':
        return text
    if variant == 'tam':
        if not positions:
            raise ValueError('Full corruption needs a Turkish character')
        return ''.join(CORRUPT.get(c, c) for c in text)
    if variant != 'kismi' or len(positions) < 2:
        raise ValueError('Partial corruption needs at least two positions')
    while True:
        mask = [rng.random() < .5 for _ in positions]
        if any(mask) and not all(mask):
            chars = list(text)
            for pos, change in zip(positions, mask):
                if change:
                    chars[pos] = CORRUPT[chars[pos]]
            return ''.join(chars)


def generate(rows, split, seed):
    pools = {b: [r for r in rows if min(eligible(r['target']), 2) == b] for b in range(3)}
    for pool in pools.values():
        pool.sort(key=lambda r: hashlib.sha256(f"{seed}:assign:{r['source_id']}".encode()).hexdigest())
    # One variant per source; exact proportions, no oversampling rare preservation text.
    for blocks in range(len(rows) // 20, 0, -1):
        full, partial, preserve = blocks * 12, blocks * 5, blocks * 3
        ascii_keep = min(len(pools[0]), max(1, preserve // 2))
        if ascii_keep and len(pools[2]) >= partial and len(pools[1]) + len(pools[2]) >= full + partial + preserve - ascii_keep:
            break
    else:
        raise ValueError(f'{split}: insufficient distinct sources for exact 60/25/15 with both preservation types')
    assignments = [(r, 'kismi') for r in pools[2][:partial]]
    remaining = pools[1] + pools[2][partial:]
    assignments += [(r, 'tam') for r in remaining[:full]]
    assignments += [(r, 'koruma') for r in remaining[full:full + preserve - ascii_keep] + pools[0][:ascii_keep]]
    output = []
    for row, variant in assignments:
        rng = random.Random(f"{seed}:{row['source_id']}:{variant}")
        record = dict(row, id=f"{split}:{row['source_id']}:{variant}", split=split,
                      category=variant, variant=variant, input=corrupt(row['target'], variant, rng))
        if variant == 'koruma':
            record['subcategory'] = 'turkce_karakterli' if eligible(row['target']) else 'turkce_karakter_gerektirmeyen'
        output.append(record)
    return sorted(output, key=lambda r: hashlib.sha256(f"{seed}:order:{r['id']}".encode()).hexdigest())


def audit(splits):
    seen = set()
    for name, rows in splits.items():
        counts = Counter(r['variant'] for r in rows)
        if counts != {'tam': len(rows) * 60 // 100, 'kismi': len(rows) * 25 // 100, 'koruma': len(rows) * 15 // 100}:
            raise ValueError(f'{name}: invalid mixture')
        if len({r['subcategory'] for r in rows if r['variant'] == 'koruma'}) != 2:
            raise ValueError('Missing preservation subtype')
        for row in rows:
            if row['source_id'] in seen:
                raise ValueError('Repeated source across outputs')
            seen.add(row['source_id'])
            ok, n, k = derivable(row['input'], row['target'])
            valid = {'tam': k == n and k > 0, 'kismi': 0 < k < n, 'koruma': k == 0}
            if not ok or not valid[row['variant']]:
                raise ValueError(f"Invalid corruption: {row['id']}")
    all_rows = [r for rows in splits.values() for r in rows]
    if next(near_pairs([comparison_key(r['target']) for r in all_rows]), None) is not None:
        raise ValueError('Near duplicates remain')
    return {'passed': True, 'unique_sources': len(seen), 'near_duplicate_pairs': 0}
