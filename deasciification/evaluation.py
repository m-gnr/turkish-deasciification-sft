"""Evaluate raw deasciification outputs without altering whitespace or casing."""
from collections import Counter, defaultdict
import json
import re
import unicodedata

PAIRS = dict(zip('cgiosuCGIOSU', 'çğıöşüÇĞİÖŞÜ'))


def nfc(text):
    return unicodedata.normalize('NFC', text)


def allowed(source, output):
    return len(source) == len(output) and all(
        b in (a, PAIRS.get(a, a)) for a, b in zip(source, output)
    )


def fraction(correct, total):
    return {'correct': correct, 'total': total,
            'rate': correct / total if total else None}


def score(row, raw_output):
    source, target, output = map(nfc, (row['input'], row['target'], raw_output))
    if not allowed(source, target):
        raise ValueError(f"{row['id']}: target violates transformation rules")
    spans = list(re.finditer(r'\S+', source))
    focus = row.get('focus_word_index')
    if focus is not None and (type(focus) is not int or not 0 <= focus < len(spans)):
        raise ValueError(f"{row['id']}: invalid focus_word_index")
    compliant = allowed(source, output)
    aligned = len(source) == len(output)
    metrics = {'strict_compliance': fraction(int(compliant), 1),
               'sentence_exact': fraction(int(output == target), 1)}
    masks = {
        'candidate_accuracy': [i for i, c in enumerate(source) if c in PAIRS],
        'required_correction': [i for i, (a, b) in enumerate(zip(source, target)) if a != b],
        'character_preservation': [i for i, (a, b) in enumerate(zip(source, target)) if a == b],
        'candidate_preservation': [i for i, (a, b) in enumerate(zip(source, target)) if a == b and a in PAIRS],
    }
    for name, indices in masks.items():
        hits = sum(output[i] == target[i] for i in indices) if compliant else 0
        metrics[name] = fraction(hits, len(indices))
    candidates = masks['candidate_accuracy']
    metrics['candidate_accuracy_compliant_only'] = fraction(
        sum(output[i] == target[i] for i in candidates) if compliant else 0,
        len(candidates) if compliant else 0)
    unchanged = [(m.start(), m.end()) for m in spans
                 if source[m.start():m.end()] == target[m.start():m.end()]]
    metrics['word_preservation'] = fraction(
        sum(output[a:b] == target[a:b] for a, b in unchanged) if compliant else 0,
        len(unchanged))
    if focus is not None:
        a, b = spans[focus].span()
        metrics['ambiguous_word_accuracy'] = fraction(
            int(compliant and output[a:b] == target[a:b]), 1)
        preserve = source[a:b] == target[a:b]
        metrics['ambiguous_word_preservation'] = fraction(
            int(preserve and compliant and output[a:b] == source[a:b]), int(preserve))
    errors = {'rule_violation': int(not compliant), 'unalignable': int(not aligned),
              'missing_correction': 0, 'unnecessary_correction': 0,
              'wrongly_changed_word': 0}
    positions = []
    if aligned:
        for i, (a, t, o) in enumerate(zip(source, target, output)):
            kind = None
            if o not in (a, PAIRS.get(a, a)):
                kind = 'rule_violation'
            elif a != t and o == a:
                kind = 'missing_correction'
            elif a == t and o != a:
                kind = 'unnecessary_correction'
            if kind:
                positions.append({'index': i, 'input': a, 'target': t, 'output': o, 'type': kind})
                if kind != 'rule_violation':
                    errors[kind] += 1
        errors['wrongly_changed_word'] = sum(
            output[m.start():m.end()] != source[m.start():m.end()]
            and output[m.start():m.end()] != target[m.start():m.end()] for m in spans)
    return {**row, 'output': raw_output, 'metrics': metrics,
            'errors': errors, 'error_positions': positions}


def aggregate(results):
    counts = defaultdict(lambda: [0, 0])
    errors = Counter()
    for result in results:
        errors.update(result['errors'])
        for name, value in result['metrics'].items():
            counts[name][0] += value['correct']
            counts[name][1] += value['total']
    pairs = defaultdict(list)
    for result in results:
        if result.get('pair_id'):
            pairs[result['pair_id']].append(result)
    if any(len(group) != 2 for group in pairs.values()):
        raise ValueError('Each pair_id must identify exactly two examples')
    counts['minimal_pair_success'] = [
        sum(all(r['metrics']['sentence_exact']['correct'] for r in group) for group in pairs.values()),
        len(pairs)]
    return {'examples': len(results),
            'metrics': {name: fraction(*value) for name, value in counts.items()},
            'errors': dict(errors)}


def read_jsonl(path):
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    ids = [row['id'] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f'{path}: duplicate IDs')
    return rows


def resampling_groups(rows):
    """Connected components: preserve BOTH source families and minimal pairs.

    This only defines sampling units; it does not compute bootstrap intervals.
    """
    parent = {r['id']: r['id'] for r in rows}

    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    seen = {}
    for row in rows:
        for field in ('source_id', 'pair_id'):
            if row.get(field):
                key = (field, row[field])
                if key in seen:
                    parent[root(row['id'])] = root(seen[key])
                else:
                    seen[key] = row['id']
    groups = defaultdict(list)
    for row in rows:
        groups[root(row['id'])].append(row['id'])
    return sorted((sorted(group) for group in groups.values()), key=lambda g: g[0])

