"""Reproducible offline analysis of saved validation predictions; never generates or reads test."""
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import csv
import json
import math
from pathlib import Path
import random
import re

from deasciification.evaluation import PAIRS, allowed, aggregate, nfc, read_jsonl, resampling_groups
from deasciification.prompting import build_messages
from scripts.compare_prompts import digest, save, summarize
from scripts.train_lora import encode_example

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/sft-validation/first-lora-v1/error-analysis'
SEED = 42
FOLD = str.maketrans({v: k for k, v in PAIRS.items()})
CATEGORY = {
    'empty': 'Boş çıktı', 'format': 'Ek biçim/açıklama belirtisi',
    'limit': 'EOS olmadan token sınırı', 'prefix': 'Girdinin eksik öneki (erken bitiş belirtisi)',
    'word_delete': 'Tam sözcük silme', 'word_repeat': 'Tam sözcük tekrarı',
    'word_add': 'Tam sözcük ekleme', 'case': 'Yalnız harf büyüklüğü ihlali',
    'punctuation': 'Yalnız boşluk/noktalama ihlali',
    'shorter': 'Diğer kısa çıktı / sözcük içi yeniden yazım',
    'longer': 'Diğer uzun çıktı / sözcük içi yeniden yazım',
    'letter': 'Eşit uzunlukta izin verilmeyen harf değişimi',
    'unalignable': 'Diğer eşit uzunluklu karma ihlal',
}


def tr_lower(text):
    return nfc(text).translate(str.maketrans({'I': 'ı', 'İ': 'i'})).lower()


def fold(text):
    return nfc(text).translate(FOLD)


def normalized(text):
    # Duplicate search only: Turkish lowercase then diacritic folding.
    # Intentionally merges I/İ/ı/i; strict scoring never uses this normalization.
    return re.sub(r'\W+', '', fold(tr_lower(text)))


def char_diff(source, output):
    return [{'op': tag, 'input_span': [a, b], 'output_span': [c, d],
             'input': source[a:b], 'output': output[c:d]}
            for tag, a, b, c, d in SequenceMatcher(None, source, output, autojunk=False).get_opcodes()
            if tag != 'equal']


def classify(source, output, at_limit=False):
    s, o = nfc(source), nfc(output)
    if allowed(s, o):
        return 'compliant'
    fs, fo = fold(s), fold(o)
    if not o:
        return 'empty'
    if ((o.startswith('```') and not s.startswith('```'))
        or (o.startswith('{') and not s.startswith('{'))
        or (len(o) >= 2 and o[0] == o[-1] == '"' and fs in fo[1:-1])
        or re.match(r'^(?:Açıklama|Sonuç|Düzeltilmiş metin)\s*:', o)):
        return 'format'
    if at_limit:
        return 'limit'
    if len(fo) < len(fs) and fs.startswith(fo):
        return 'prefix'
    a, b = fs.split(), fo.split()
    ops = [x for x in SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if x[0] != 'equal']
    if ops and all(x[0] == 'delete' for x in ops):
        return 'word_delete'
    if ops and all(x[0] == 'insert' for x in ops):
        added = [w for _, _, _, c, d in ops for w in b[c:d]]
        return 'word_repeat' if all(w in a for w in added) else 'word_add'
    bad = [(x, y) for x, y in zip(s, o) if y not in (x, PAIRS.get(x, x))]
    # Explicit Turkish casing; I -> İ remains an allowed deasciification, not case change.
    if len(s) == len(o) and bad and all(x.isupper() != y.isupper() and tr_lower(y) in {tr_lower(x), tr_lower(PAIRS.get(x, x))} for x, y in bad):
        return 'case'
    if allowed(''.join(c for c in s if c.isalnum()), ''.join(c for c in o if c.isalnum())) and ''.join(c for c in s if not c.isalnum()) != ''.join(c for c in o if not c.isalnum()):
        return 'punctuation'
    if len(o) != len(s):
        return 'shorter' if len(o) < len(s) else 'longer'
    if any(x.isalpha() and y.isalpha() for x, y in bad):
        return 'letter'
    return 'unalignable'


def violation_signals(source, output):
    """Overlapping edit symptoms; descriptive alignment, not linguistic causality."""
    s, o = nfc(source), nfc(output)
    a, b = fold(s).split(), fold(o).split()
    ops = SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    deleted = sum(j-i for tag, i, j, k, l in ops if tag == 'delete')
    inserted = sum(l-k for tag, i, j, k, l in ops if tag == 'insert')
    # Repeated output bigrams >=3 times, exceeding the source frequency.
    bi = lambda seq: Counter(zip(seq, seq[1:]))
    sa, sb = bi(a), bi(b)
    repeat = any(n >= 3 and n > sa[k] for k, n in sb.items())
    case, noncandidate, candidate_forbidden = False, False, False
    for tag, i, j, k, l in SequenceMatcher(None, fold(s), fold(o), autojunk=False).get_opcodes():
        if j-i == l-k:
            for x, y in zip(s[i:j], o[k:l]):
                if y in (x, PAIRS.get(x, x)):
                    continue
                case |= x.isupper() != y.isupper() and tr_lower(y) in {tr_lower(x), tr_lower(PAIRS.get(x, x))}
                noncandidate |= x.isalpha() and x not in PAIRS
                candidate_forbidden |= x in PAIRS
    return {'whole_word_delete_block': deleted > 0, 'whole_word_insert_block': inserted > 0,
            'repeated_bigram_proxy': repeat, 'case_change_in_aligned_blocks': case,
            'noncandidate_letter_change_in_aligned_blocks': noncandidate,
            'candidate_forbidden_change_in_aligned_blocks': candidate_forbidden,
            'whitespace_sequence_changed': re.findall(r'\s+', s) != re.findall(r'\s+', o),
            'punctuation_sequence_changed': ''.join(c for c in s if not c.isalnum() and not c.isspace()) != ''.join(c for c in o if not c.isalnum() and not c.isspace())}


def repair(source, output):
    """Conservative character alignment: only equal folded blocks; never use gold."""
    s, o = nfc(source), nfc(output)
    result = list(s)
    for tag, a, b, c, d in SequenceMatcher(None, fold(s), fold(o), autojunk=False).get_opcodes():
        if tag == 'equal':
            for i, j in zip(range(a, b), range(c, d)):
                if s[i] in PAIRS and o[j] in (s[i], PAIRS[s[i]]):
                    result[i] = o[j]
    result = ''.join(result)
    assert allowed(s, result)
    return result


def mcnemar(b, c):
    n = b + c
    # Exact two-sided binomial, stable for n <= 900, no scipy dependency.
    return min(1., 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2**n) if n else 1.


def paired(rows, before, after):
    import numpy as np
    index = {r['id']: i for i, r in enumerate(rows)}
    groups = [[index[i] for i in g] for g in resampling_groups(rows)]
    rng = np.random.default_rng(SEED)
    selections = rng.integers(0, len(groups), size=(10000, len(groups)))
    sizes = np.array([len(g) for g in groups])
    result = {}
    for name in ('strict_compliance', 'sentence_exact'):
        a = [r['metrics'][name]['correct'] for r in before]
        b = [r['metrics'][name]['correct'] for r in after]
        table = Counter(f'{x}{y}' for x, y in zip(a, b))
        values = np.array([sum(b[i] - a[i] for i in g) for g in groups])
        diffs = values[selections].sum(axis=1) / sizes[selections].sum(axis=1)
        result[name] = {'both_yes': table['11'], 'before_only': table['10'],
                        'after_only': table['01'], 'both_no': table['00'],
                        'difference': (sum(b) - sum(a)) / len(a),
                        'ci95': np.quantile(diffs, [.025, .975]).tolist(),
                        'mcnemar_exact_two_sided_p': mcnemar(table['10'], table['01'])}
    return {'seed': SEED, 'replicates': 10000, 'groups': len(groups),
            'method': 'paired source/pair cluster percentile bootstrap; McNemar assumes independent sentences',
            'metrics': result}


def stats(values):
    import numpy as np
    return dict(zip(['min', 'p25', 'median', 'p75', 'p95', 'p99', 'max'],
                    map(float, np.quantile(values, [0, .25, .5, .75, .95, .99, 1]))))


def compact(results):
    full = aggregate(results)
    compliant = [r for r in results if r['metrics']['strict_compliance']['correct']]
    conditional = aggregate(compliant)
    return {'all': full, 'compliant_only': conditional,
            'equal_length_count': sum(len(nfc(r['input'])) == len(nfc(r['output'])) for r in results)}


def example(row, before=None):
    return {k: row[k] for k in ('id', 'input', 'target', 'output')} | {
        'before': before, 'input_output_diff': char_diff(row['input'], row['output']),
        'target_output_diff': char_diff(row['target'], row['output']),
        'before_diff': char_diff(row['input'], before) if before is not None else [],
        'errors': row['errors'], 'error_positions': row['error_positions']}


def write_examples(path, examples):
    save(path.with_suffix('.json'), examples)
    lines = ['# Örnekler', '', 'Seed 42; amaçlı tabakalı seçim, yaygınlık tahmini değildir.', '']
    for i, r in enumerate(examples, 1):
        lines += [f"## {i}. {r['id']} — {r.get('group', '')}", '', '```text',
                  f"Girdi: {r['input']}", f"Hedef: {r['target']}",
                  f"Önce:  {r['before']}" if r.get('before') is not None else '',
                  f"Sonra: {r['output']}", '```', '', r.get('review_note', ''), '', 'Karakter diff (0 tabanlı, bitiş hariç):', '```json',
                  json.dumps(r['input_output_diff'], ensure_ascii=False), '```',
                  'Hedef → çıktı diff:', '```json', json.dumps(r['target_output_diff'], ensure_ascii=False), '```', '']
    path.with_suffix('.md').write_text('\n'.join(lines))


def main():
    import os
    os.chdir(ROOT)
    from transformers import AutoTokenizer, GenerationConfig
    from deasciification.config import MODEL, REVISION
    baseline = json.loads(Path('reports/baselines/boun-v1-pre-sft.json').read_text())
    base, post = Path(baseline['run']), Path('reports/sft-validation/first-lora-v1')
    val_path = Path('data/prepared/boun-v1/splits/validation.jsonl')
    train_path = Path('data/prepared/boun-v1/splits/train.jsonl')
    rows, train = read_jsonl(val_path), read_jsonl(train_path)
    assert len(rows) == 900 and all(r['split'] == 'validation' for r in rows)
    assert len(train) == 7340 and all(r['split'] == 'train' for r in train)
    # Explicit allowlist: do not inspect test files even to hash them.
    protected = [val_path, train_path, Path('reports/baselines/boun-v1-pre-sft.json')]
    protected += [p for folder in (base, post) for p in folder.glob('*.json*')]
    before_hashes = {str(p): digest(p) for p in protected}
    for name, expected in baseline['sha256'].items():
        if name in before_hashes:
            assert before_hashes[name] == expected, f'Frozen hash mismatch: {name}'
    for folder in (base, post):
        meta = json.loads((folder / 'metadata.json').read_text())
        for filename, expected in meta['output_sha256'].items():
            assert digest(folder / filename) == expected, f'Saved output changed: {folder / filename}'
    systems, raw, reports = {}, {}, {}
    for phase, folder in [('pre', base), ('sft', post)]:
        for condition in ('zero_shot', 'five_shot'):
            name = f'{phase}_{condition}'
            raw[name] = read_jsonl(folder / f'{condition}.jsonl')
            report = summarize(rows, {r['id']: r['output'] for r in raw[name]})
            saved = json.loads((folder / f'{condition}-scores.json').read_text())
            assert report == saved, f'Rescore mismatch: {name}; STOP'
            reports[name] = report
            systems[name] = report['examples']
    for name, count_c, count_e in [('pre_zero_shot', 663, 152), ('sft_zero_shot', 590, 394)]:
        assert reports[name]['summary']['metrics']['strict_compliance']['correct'] == count_c
        assert reports[name]['summary']['metrics']['sentence_exact']['correct'] == count_e
    identity = summarize(rows, {r['id']: r['input'] for r in rows})
    assert identity == json.loads((base / 'identity-scores.json').read_text())
    systems['identity'] = identity['examples']
    OUT.mkdir(parents=True, exist_ok=True)
    save(OUT / 'rescoring.json', {'status': 'exact_match', 'systems': list(systems), 'hashes': before_hashes})
    print('Rescoring: all 4500 saved example scores and summaries match.', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    trained_tokenizer = AutoTokenizer.from_pretrained('runs/first-sft-v1/training/adapter', local_files_only=True)
    gc = GenerationConfig.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    eos = {gc.eos_token_id} if isinstance(gc.eos_token_id, int) else set(gc.eos_token_id)
    demos = json.loads((base / 'demonstrations.json').read_text())['examples']
    token_audit = {}
    violations, category_examples, label_rows = {}, [], []
    for name, predictions in raw.items():
        lookup = {r['id']: r for r in predictions}
        target_lengths = [len(tokenizer.encode(r['target'], add_special_tokens=False)) for r in rows]
        generated_lengths = [r['generated_tokens'] for r in predictions]
        content_lengths = [len(tokenizer.encode(r['output'], add_special_tokens=False)) for r in predictions]
        reached = [r for r in predictions if r['generated_tokens'] >= 256]
        no_eos = [r for r in predictions if not r['generated_token_ids'] or r['generated_token_ids'][-1] not in eos]
        assert all(r['generated_tokens'] == len(r['generated_token_ids']) for r in predictions)
        assert all(tokenizer.decode(r['generated_token_ids'], skip_special_tokens=True) == r['output'] for r in predictions)
        token_audit[name] = {'target_content': stats(target_lengths), 'output_content_retokenized': stats(content_lengths),
            'generated_including_stop': stats(generated_lengths), 'at_limit': len(reached),
            'at_limit_without_eos': sum(r in no_eos for r in reached), 'without_eos': len(no_eos),
            'last_token_counts': dict(Counter(str(r['generated_token_ids'][-1]) if r['generated_token_ids'] else 'empty' for r in predictions)),
            'seconds_sum': sum(r['seconds'] for r in predictions)}
        buckets = defaultdict(list)
        for row in systems[name]:
            p = lookup[row['id']]
            cat = classify(row['input'], row['output'], p in reached and p in no_eos)
            if cat != 'compliant':
                buckets[cat].append(row)
                label_rows.append({'system': name, 'id': row['id'], 'category': cat,
                                   'input_length': len(nfc(row['input'])), 'output_length': len(nfc(row['output'])),
                                   'diff': char_diff(row['input'], row['output']), 'signals': violation_signals(row['input'], row['output'])})
        total = sum(map(len, buckets.values()))
        violations[name] = {'total': total, 'categories': {k: {'n': len(buckets[k]),
            'share_violations': len(buckets[k])/total, 'share_900': len(buckets[k])/900} for k in CATEGORY},
            'signals': dict(Counter(k for r in label_rows if r['system'] == name for k, v in r['signals'].items() if v)),
            'lengths': dict(Counter('shorter' if len(nfc(r['output'])) < len(nfc(r['input'])) else 'longer'
                                   if len(nfc(r['output'])) > len(nfc(r['input'])) else 'equal' for v in buckets.values() for r in v))}
        rng = random.Random(SEED)
        if name.startswith('sft'):
            for k in CATEGORY:
                for r in rng.sample(buckets[k], min(3, len(buckets[k]))):
                    category_examples.append(example(r) | {'group': name + ':' + k})
    save(OUT / 'violations.json', {'definitions': CATEGORY, 'systems': violations, 'rows': label_rows})
    write_examples(OUT / 'category-examples', category_examples)
    # No gold values are passed to either postprocessor.
    for condition in ('zero_shot', 'five_shot'):
        original = systems['sft_' + condition]
        for mode in ('fallback', 'repair'):
            outputs = {r['id']: (r['output'] if allowed(nfc(r['input']), nfc(r['output'])) else r['input'])
                       if mode == 'fallback' else repair(r['input'], r['output']) for r in original}
            systems[f'sft_{condition}_{mode}'] = summarize(rows, outputs)['examples']
            save(OUT / f'{condition}-{mode}-outputs.json', outputs)
    metrics = {k: compact(v) for k, v in systems.items()}
    save(OUT / 'metrics.json', metrics)
    postprocess_changes = {}
    for c in ('zero_shot', 'five_shot'):
        original = systems['sft_' + c]
        for mode in ('fallback', 'repair'):
            result = systems['sft_' + c + '_' + mode]
            postprocess_changes[c + '_' + mode] = {
                'changed_outputs': sum(a['output'] != b['output'] for a, b in zip(original, result)),
                'exact_gained': sum(not a['metrics']['sentence_exact']['correct'] and b['metrics']['sentence_exact']['correct'] for a, b in zip(original, result)),
                'exact_lost': sum(a['metrics']['sentence_exact']['correct'] and not b['metrics']['sentence_exact']['correct'] for a, b in zip(original, result)),
                'compliant_outputs_changed': sum(a['metrics']['strict_compliance']['correct'] and a['output'] != b['output'] for a, b in zip(original, result))}
    save(OUT / 'postprocess-changes.json', postprocess_changes)

    transitions = {c: paired(rows, systems['pre_' + c], systems['sft_' + c]) for c in ('zero_shot', 'five_shot')}
    save(OUT / 'paired.json', transitions)
    # Character and word diagnostics on compliant outputs only, with explicit lexical proxies.
    lexicon = defaultdict(set)
    for r in train:
        for w in re.findall(r'\w+', r['target']):
            lexicon[fold(tr_lower(w))].add(tr_lower(w))
    characters, words = {}, []
    for name, result in systems.items():
        if name not in raw:
            continue
        counts = {a + '/' + b: Counter({'correct': 0, 'missed': 0, 'wrong': 0, 'correct_required': 0, 'correct_preserved': 0}) for a, b in PAIRS.items()}
        for r in result:
            if not r['metrics']['strict_compliance']['correct']:
                continue
            for a, t, o in zip(nfc(r['input']), nfc(r['target']), nfc(r['output'])):
                if a in PAIRS:
                    c = counts[a + '/' + PAIRS[a]]
                    kind = 'correct' if o == t else 'missed' if o == a else 'wrong'
                    c[kind] += 1
                    if kind == 'correct':
                        c['correct_required' if a != t else 'correct_preserved'] += 1
            spans = list(re.finditer(r'\S+', r['input']))
            for i, span in enumerate(spans):
                a, b = span.span()
                inp, target, output = r['input'][a:b], r['target'][a:b], r['output'][a:b]
                if target == output:
                    continue
                clean = re.sub(r'[^\w]', '', target)
                prefix = next((j for j, (t, o) in enumerate(zip(target, output)) if t != o), 0)
                suffix_hint = next((s for s in ('lar', 'ler', 'dan', 'den', 'dır', 'dir', 'mış', 'miş', 'yor', 'lık', 'lik') if tr_lower(clean).endswith(s)), None)
                words.append({'system': name, 'id': r['id'], 'input': inp, 'target': target, 'output': output,
                    'length': len(clean), 'position': 'start' if i == 0 else 'end' if i == len(spans)-1 else 'middle',
                    'proper_name_proxy': bool(clean and clean[0].isupper() and i > 0),
                    'acronym_proxy': len(clean) > 1 and clean.isupper(),
                    'foreign_letter_proxy': bool(re.search('[qwxQWX]', clean)),
                    'train_attested_ambiguity': len(lexicon.get(fold(tr_lower(clean)), set())) > 1,
                    'train_target_forms': sorted(lexicon.get(fold(tr_lower(clean)), set())),
                    'shared_prefix_length': prefix, 'suffix_surface_hint': suffix_hint,
                    'error_in_last_3_chars': any(target[j] != output[j] for j in range(max(0, len(target)-3), len(target)))})
        characters[name] = counts
    save(OUT / 'characters.json', characters)
    save(OUT / 'word-errors.json', words)
    word_summary = {}
    for name in raw:
        selected = [w for w in words if w['system'] == name]
        word_summary[name] = {'n': len(selected), 'length': dict(Counter('1-5' if w['length'] <= 5 else '6-10' if w['length'] <= 10 else '11+' for w in selected)),
            'position': dict(Counter(w['position'] for w in selected)),
            **{k: sum(bool(w[k]) for w in selected) for k in ('proper_name_proxy', 'acronym_proxy', 'foreign_letter_proxy', 'train_attested_ambiguity', 'error_in_last_3_chars')},
            'suffix_surface_hint': dict(Counter(w['suffix_surface_hint'] or 'none' for w in selected)),
            'shared_prefix_length': dict(Counter('0' if w['shared_prefix_length'] == 0 else '1-3' if w['shared_prefix_length'] <= 3 else '4+' for w in selected))}
    save(OUT / 'word-summary.json', word_summary)
    # Independent overlapping slices, each dimension partitions all 900 sentences.
    slices = []
    for name in raw:
        groups = defaultdict(list)
        for r in systems[name]:
            length, candidates = len(nfc(r['input'])), sum(c in PAIRS for c in nfc(r['input']))
            values = {'length': '1-40' if length <= 40 else '41-80' if length <= 80 else '81-120' if length <= 120 else '121+',
                      'candidates': '0-10' if candidates <= 10 else '11-20' if candidates <= 20 else '21-30' if candidates <= 30 else '31+',
                      'needs_correction': str(r['input'] != r['target']), 'category': r['category'],
                      'source_prefix': r['original_sent_id'].split('_')[0]}
            for dimension, value in values.items():
                groups[(dimension, value)].append(r)
        for (dimension, value), group in groups.items():
            ag = aggregate(group)
            slices.append({'system': name, 'dimension': dimension, 'value': value, 'n': len(group),
                           **{k: ag['metrics'][k]['rate'] for k in ('strict_compliance', 'sentence_exact')}})
    save(OUT / 'slices.json', slices)
    # Train audit: only the authorized train/validation files, no source corpus/test reads.
    lengths = [len(encode_example(tokenizer, r, 1024)['input_ids']) for r in train]
    overlap = {}
    for field in ('input', 'target'):
        for norm_name, norm in [('exact', nfc), ('normalized', normalized)]:
            mapping = defaultdict(list)
            for r in train:
                mapping[norm(r[field])].append(r['id'])
            hits = [{'validation_id': r['id'], 'train_ids': mapping[norm(r[field])]} for r in rows if norm(r[field]) in mapping]
            overlap[field + '_' + norm_name] = hits
    audit = {'invalid_targets': [r['id'] for r in train if not allowed(nfc(r['input']), nfc(r['target']))],
             'source_overlap': sorted({r['source_id'] for r in train} & {r['source_id'] for r in rows}),
             'overlap': overlap, 'sequence_tokens_including_prompt_and_eos': stats(lengths),
             'above_1024': sum(n > 1024 for n in lengths),
             'split_mix': {name: {'n': len(rs), 'categories': dict(Counter(r['category'] for r in rs)),
                                    'needs_correction': sum(r['input'] != r['target'] for r in rs),
                                    'preservation': sum(r['input'] == r['target'] for r in rs)} for name, rs in [('train', train), ('validation', rows)]}}
    save(OUT / 'training-audit.json', audit)
    prompt = lambda tok, r, ds=(): tok.apply_chat_template(build_messages(r['input'], ds), tokenize=False, add_generation_prompt=True, enable_thinking=False)
    run = json.loads(Path('runs/first-sft-v1/training/run.json').read_text())
    base_meta = json.loads((base / 'metadata.json').read_text())
    post_meta = json.loads((post / 'metadata.json').read_text())
    code_checks = {p: digest(Path(p)) == h for p, h in run['code_sha256'].items()}
    code_checks.update({'baseline:' + p: digest(Path(p)) == h for p, h in base_meta['code_sha256'].items()})
    code_checks['evaluate_adapter'] = digest(Path('scripts/evaluate_adapter.py')) == post_meta['code_sha256']
    protocol = {'tokenizer_eos': tokenizer.eos_token_id, 'generation_eos': sorted(eos),
                'eos_names': {str(i): tokenizer.convert_ids_to_tokens(i) for i in eos},
                'saved_tokenizer_eos': trained_tokenizer.eos_token_id,
                'template_equal': tokenizer.chat_template == trained_tokenizer.chat_template,
                'zero_shot_prompt_equal_count': sum(prompt(tokenizer, r) == prompt(trained_tokenizer, r) for r in rows),
                'five_shot_differs_from_training_count': sum(prompt(tokenizer, r, demos) != prompt(trained_tokenizer, r) for r in rows),
                'training_eos_is_generation_stop': tokenizer.eos_token_id in eos,
                'code_hash_checks': code_checks, 'token_audit': token_audit}
    save(OUT / 'generation-audit.json', protocol)
    # Unique sample: reserve transition groups before broader pools.
    pre, sft = systems['pre_zero_shot'], systems['sft_zero_shot']
    pools = {'regression': [i for i in range(900) if pre[i]['metrics']['sentence_exact']['correct'] and not sft[i]['metrics']['sentence_exact']['correct']],
             'improvement': [i for i in range(900) if not pre[i]['metrics']['sentence_exact']['correct'] and sft[i]['metrics']['sentence_exact']['correct']],
             'violation': [i for i in range(900) if not sft[i]['metrics']['strict_compliance']['correct']],
             'compliant_wrong': [i for i in range(900) if sft[i]['metrics']['strict_compliance']['correct'] and not sft[i]['metrics']['sentence_exact']['correct']]}
    chosen, used, rng = [], set(), random.Random(SEED)
    for group, n in [('regression', 5), ('improvement', 5), ('violation', 20), ('compliant_wrong', 10)]:
        selected = rng.sample([i for i in pools[group] if i not in used], n)
        used.update(selected)
        for i in selected:
            chosen.append(example(sft[i], pre[i]['output']) | {'group': group,
                'diagnostic': classify(sft[i]['input'], sft[i]['output'])})
    assert len(used) == 40
    notes_path = OUT / 'review-notes.json'
    if notes_path.exists():
        notes = json.loads(notes_path.read_text())
        for r in chosen:
            r['review_note'] = notes.get(r['id'], 'Bu örnek için ayrı yorum kaydedilmedi.')
    write_examples(OUT / 'review-40', chosen)
    save(OUT / 'sampling.json', {'seed': SEED, 'pool_sizes': {k: len(v) for k, v in pools.items()},
        'reservation_order': ['regression:5', 'improvement:5', 'violation:20', 'compliant_wrong:10']})
    for p, h in before_hashes.items():
        assert digest(Path(p)) == h, f'Protected file changed: {p}'
    save(OUT / 'analysis.json', {'seed': SEED, 'protected_files_unchanged': True,
        'metrics': metrics, 'violations': violations, 'paired': transitions, 'tokens': protocol,
        'train': audit, 'word_summary': word_summary})
    write_report(metrics, violations, transitions, protocol, audit, characters, word_summary, slices)
    with (OUT / 'metrics.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['system', 'metric', 'correct', 'total', 'rate'])
        for name, result in metrics.items():
            for k, v in result['all']['metrics'].items():
                writer.writerow([name, k, v['correct'], v['total'], v['rate']])
    print('Offline analysis complete: ' + str(OUT), flush=True)


def pct(value):
    return '—' if value is None else f'{100*value:.2f}%'


def write_report(metrics, violations, transitions, protocol, audit, characters, word_summary, slices):
    lines = ['# İlk LoRA SFT: doğrulama hata analizi', '',
        '900 doğrulama örneği; yalnız mevcut çıktılar. Eğitim denetimi için 7.340 eğitim örneği okundu. '
        'Ayrı test kümesi açılmadı; model yüklenmedi, üretim/eğitim yapılmadı. Tüm örnekleme seed=42. '
        'Betik: `scripts/analyze_sft_errors.py`; çalıştırma: `.venv/bin/python -m scripts.analyze_sft_errors`.', '',
        '## Puanların doğrulanması', '',
        '4 model koşulu + identity: 4.500 örneğin skorları, özetleri ve kategori özetleri mevcut puanlayıcıyla birebir eşleşti. '
        'Zero-shot uyum 663/900 → 590/900; tam eşleşme 152/900 → 394/900. '
        'Orijinal dosyaların SHA-256 değerleri çalışma başı/sonu aynı (`rescoring.json`).', '',
        '## Sistem ve koşullu metrikler', '',
        'Yüzdeler mevcut mikro ortalama tanımlarıdır. “Uyumlu” sütunları her sistemin farklı seçilmiş alt kümesine aittir; '
        'doğrudan nedensel karşılaştırma değildir. U=unnecessary_correction karakter sayısı; W=wrongly_changed_word sözcük sayısı. '
        'Mevcut puanlayıcı bu iki hatayı yalnız eşit uzunluklu çıktılarda sayar: uzunluğu farklı çıktılar için 0, hatasızlık anlamına gelmez.', '',
        '| Sistem | Uyum | Tam eşleşme | Aday doğruluğu | Gerekli düzeltme (tümü) | Aday (uyumlu) | Gerekli (uyumlu) | Tam (uyumlu) | U | W | Eşit uzunluk n |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name, value in metrics.items():
        m, c = value['all']['metrics'], value['compliant_only']['metrics']
        rates = [m[k]['rate'] for k in ('strict_compliance', 'sentence_exact', 'candidate_accuracy', 'required_correction')]
        rates += [c[k]['rate'] for k in ('candidate_accuracy_compliant_only', 'required_correction', 'sentence_exact')]
        lines.append('| ' + name + ' | ' + ' | '.join(map(pct, rates)) + f" | {value['all']['errors'].get('unnecessary_correction', 0)} | {value['all']['errors'].get('wrongly_changed_word', 0)} | {value['equal_length_count']} |")
    lines += ['', '### Temel bulgular ve pratik anlamı', '',
        '- Zero-shot tam eşleşme +242 cümle; 254 örnek düzelirken 12 örnek bozuldu. Uyum net −73 cümle: 186 yeni ihlal, 113 giderilen ihlal.',
        '- Zero-shot 310 ihlalden 237’si farklı uzunlukta; 73’ü eşit uzunlukta. Token sınırı zero-shot’ta 0/900, five-shot’ta 1/900: ana zero-shot sorunu sınır kesilmesiyle açıklanamıyor.',
        '- Eğitim hedeflerinin 7.340/7.340’ı katı kurala uyuyor; normalize train/validation çakışması 0; iki kümede de koruma payı %15. Bu kontroller dilsel hedef kalitesini kanıtlamaz.',
        '- SFT+fallback zero-shot: 401/900 tam doğru (%44,56), gerekli düzeltme %38,10. SFT+hizalama: 500/900 (%55,56), gerekli düzeltme %87,20; ikisi de %100 uyumlu ayrı sistemler.',
        '- Hizalama mevcut tam doğru çıktılardan 0’ını bozup 106 yeni tam doğru kazandırıyor. Fallback’e göre gereksiz dönüşüm 88→203 ve yanlış değiştirilmiş sözcük 110→301: daha çok düzeltmenin bedeli daha çok yanlış müdahale. Bu iki sistemin tüm çıktıları eşit uzunlukta olduğundan bu hata sayıları karşılaştırılabilir.', '',
        'Önceki five-shot incelemesine aynı otomatik belirtilerle bakıldığında tam sözcük silme bloğu 11→2, '
        'harf büyüklüğü belirtisi 17→7, boşluk dizisi değişimi 100→36, noktalama değişimi 97→6. '
        'SFT bu belirtileri azaltıyor; kalan sözcük içi yeniden yazımlar kısa/uzun ve yasak harf kategorilerinde belirgin. '
        'Hizalama belirtileri tam dilsel envanter değildir; karma silme+ekleme bloklarını ayrı sözcük silme olarak saymayabilir.']
    lines += ['', '## İhlal sınıflandırması', '',
        'Birbirini dışlayan ana kategoriler aşağıdaki sıra ile atanır: boş → ek biçim → EOS’suz sınır → eksik önek → '
        'yalnız tam sözcük silme → yalnız tekrar/ekleme → yalnız Türkçe harf büyüklüğü → yalnız boşluk/noktalama → '
        'diğer kısa/uzun → eşit uzunlukta yasak harf → diğer karma. İlk eşleşme kazanır. '
        'Sözcük eşleme diakritikleri kaldırır, büyüklüğü korur; tam sözcük kategorileri sadece saf silme/ekleme hizalamasıdır. '
        'Karma olaylar kısa/uzun altında kalabilir. Eksik önek erken EOS nedenini kanıtlamaz. '
        'Açıklama/biçim sınıfı sabit önek ve sarmalayıcı sezgisidir. Uzunluk farkı ayrıca raporlanır, kategori toplamına eklenmez. '
        'Mevcut `unalignable` metriği yalnız uzunluk farkıdır; yeni sınıflandırmanın “diğer karma” etiketiyle aynı değildir.', '',
        '| Kategori | Zero n | İhlallerde | 900 içinde | Five n | İhlallerde | 900 içinde |', '|---|---:|---:|---:|---:|---:|---:|']
    for k, label in CATEGORY.items():
        z, f = [violations['sft_' + c]['categories'][k] for c in ('zero_shot', 'five_shot')]
        lines.append(f"| {label} | {z['n']} | {pct(z['share_violations'])} | {pct(z['share_900'])} | {f['n']} | {pct(f['share_violations'])} | {pct(f['share_900'])} |")
    for name in violations:
        lines.append(f"\n{name}: toplam {violations[name]['total']} ihlal; uzunluk dağılımı {violations[name]['lengths']}.")
    lines += ['', 'Örtüşen belirtiler (saf kategori dışında karma olayları da yakalar; toplanmaz):', '',
              '| Belirti | Önce zero | Önce five | SFT zero | SFT five |', '|---|---:|---:|---:|---:|']
    keys = sorted({k for v in violations.values() for k in v['signals']})
    for k in keys:
        lines.append('| ' + k + ' | ' + ' | '.join(str(violations[n]['signals'].get(k, 0)) for n in
                     ('pre_zero_shot', 'pre_five_shot', 'sft_zero_shot', 'sft_five_shot')) + ' |')
    lines += ['', 'Belirtiler: diakritik katlanmış sözcük hizalamasında saf delete/insert blokları; '
              'çıktıda en az 3 kez geçen ve girdide daha az görülen bigram vekili (tek başına döngü kanıtı değil); '
              'eşit boyutlu karakter bloklarında harf büyüklüğü/aday olmayan harf değişimi; '
              'boşluk ve noktalama dizilerinin değişimi. Hizalama belirsizliği nedeniyle bunlar alt düzey otomatik belirtilerdir.']
    lines += ['', 'Her gözlenen SFT kategorisinden en çok 3 örnek [kategori örnekleri](category-examples.md) içinde; '
              'kategori 0/1/2 örnekliyse olmayan örnek üretilmedi. Tüm atamalar ve diff’ler `violations.json` içinde.', '',
              '## Eşleştirilmiş geçişler', '',
              'Tablo hücreleri cümle sayısıdır. Fark = SFT − önce; GA yüzde puan. 10.000 tekrar, seed 42, '
              'kaynak/pair bağlantılı kümeler korunur. McNemar iki taraflı exact binom testidir; cümle bağımsızlığı varsayar. '
              'Aynı kaynağın varyantları bağımlıysa bootstrap aralığı daha uygun kanıttır.', '',
              '| Koşul / metrik | İkisi evet | Önce evet | Sonra evet | İkisi hayır | Fark (yp) | %95 GA (yp) | McNemar p |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
    for condition, result in transitions.items():
        for metric, v in result['metrics'].items():
            lines.append(f"| {condition}/{metric} | {v['both_yes']} | {v['before_only']} | {v['after_only']} | {v['both_no']} | {v['difference']*100:.2f} | [{v['ci95'][0]*100:.2f}, {v['ci95'][1]*100:.2f}] | {v['mcnemar_exact_two_sided_p']:.4g} |")
    lines += ['', '## Üretim, EOS ve istem denetimi', '',
        f"Tokenizer EOS={protocol['tokenizer_eos']}; generation EOS={protocol['generation_eos']} ({protocol['eos_names']}). "
        f"Eğitim EOS’u durdurma listesinde: {protocol['training_eos_is_generation_stop']}. "
        f"Kaydedilmiş ve temel tokenizer şablonları aynı: {protocol['template_equal']}; "
        f"900 zero-shot isteminin {protocol['zero_shot_prompt_equal_count']} tanesi birebir aynı. "
        f"Five-shot istemlerinin {protocol['five_shot_differs_from_training_count']}/900 tanesi beş gösterim nedeniyle eğitimden farklıdır.", '',
        'Kod: `train_lora.encode_example` ve `inference.generate_batch` aynı `build_messages`, '
        '`add_generation_prompt=True`, `enable_thinking=False` kullanır. Eğitim hedef+EOS öğretir; '
        'değerlendirme greedy, batch=8, sol padding, max_new_tokens=256; bitmiş diziler ilk stop token’dan kesilir. '
        'Padding token farkı prompt içeriğini değiştirmez; eğitim padding label’ları -100’dür. '
        f"Tarihsel kod hash kontrolleri: {sum(protocol['code_hash_checks'].values())}/{len(protocol['code_hash_checks'])} eşleşme. "
        'Generation config’in tarihsel hash’i kaydedilmedi; EOS denetimi sabit model revision’ının yerel config’i ve saklanan tokenlar üzerinden yapılmıştır.', '',
        '| Sistem | Hedef med/p95/max | Çıktı med/p95/max (yeniden tokenize) | Üretilen max (stop dahil) | Sınıra ulaşan | Sınırda EOS yok | EOS yok |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for name, t in protocol['token_audit'].items():
        trip = lambda k: '/'.join(f'{t[k][p]:.2f}' for p in ('median', 'p95', 'max'))
        lines.append(f"| {name} | {trip('target_content')} | {trip('output_content_retokenized')} | {t['generated_including_stop']['max']} | {t['at_limit']} | {t['at_limit_without_eos']} | {t['without_eos']} |")
    lines += ['', 'Kayıtlı token dizileri yeniden decode edilerek 3.600 çıktı ile birebir eşleşti. '
        'Hedef/çıktı içerik uzunluğu EOS hariç; orijinal üretilen uzunluk stop dahil. Tam quantile’lar `generation-audit.json` içinde. '
        'Sınır/EOS ve biçim belirtileri gözlemseldir: yeni kontrollü üretim olmadan “ayar kaynaklı” nedensel pay atanamaz. '
        'Boş/biçim/sınır/eksik-önek dışındaki ihlaller gözlenen metin değişiklikleridir; bunların da model/ayar nedensel ayrımı kesin değildir.', '',
        'Gözlemsel ayrım: zero-shot 0/310 ihlalde boş/biçim/sınır/eksik-önek belirtisi, '
        '310/310 ihlalde diğer metin değişikliği; five-shot 1/307 sınır belirtisi ve 306/307 diğer değişiklik. '
        'Five-shot `validation:boun:pop_1949:tam` çıktısı “kıyı şanlı” tekrarına giriyor; hedef 256 token gerektirmiyor. '
        'Sınırı yükseltmek tek başına çözüm olarak gerekçelendirilemez. '
        'Bu örneğin 8’li batch’i yaklaşık 31 saniye sürmüş; tek örnek kontrollü üretim için model yükleme dahil '
        '1–3 dakika ihtiyatlı planlama tahminidir, ölçülmüş tek-örnek süre değildir. Üretim yapılmadı; ön onay gerekir.', '',
        '## Uyumlu çıktılarda karakterler', '',
        'Doğru = hedefle eşleşen tüm aday konumları (koruma dahil). Kaçırılan = gerekli dönüşüm yapılmamış; '
        'yanlış = gereksiz dönüşüm. Katı uyumlu çıktıda mevcut Türkçe harfi ters yönde değiştirmek mümkün değildir. '
        'Büyük harfler ayrı tutulur; I→İ izinli, I→ı ve İ→i büyüklük değişimidir. '
        'Aşağıda SFT koşulları; eğitim öncesi sayılar da `characters.json` içindedir.', '',
        '| Çift | Zero doğru | Kaçırılan | Yanlış | Five doğru | Kaçırılan | Yanlış |', '|---|---:|---:|---:|---:|---:|---:|']
    for pair in characters['sft_zero_shot']:
        vals = [characters['sft_' + c][pair][k] for c in ('zero_shot', 'five_shot') for k in ('correct', 'missed', 'wrong')]
        lines.append('| ' + pair + ' | ' + ' | '.join(map(str, vals)) + ' |')
    lines += ['', '## Sözcük ve konum incelemesi', '',
        'Yalnız uyumlu çıktıda hedefle farklı whitespace sözcükleri. Uzunluk alfanümerik karakter sayısı. '
        'Konum ilk/son whitespace sözcüğüne göre; tek sözcük baş sayılır. Özel isim vekili=başta olmayan büyük harfli sözcük; '
        'kısaltma vekili=tam büyük harf; yabancı vekili=q/w/x. Bunlar dilsel etiket değildir. '
        'Belirsizlik vekili=eğitim hedeflerinde aynı ASCII biçimin en az iki Türkçe karşılığı; bağlamda ikisinin de geçerli olduğu iddia edilmez. '
        'Ön ek ortak karakter uzunluğu, son 3 karakter ve yüzey son-ek listesi raporlanır; morfolojik çözümleme yoktur. '
        'Gerçek özel isim/yabancı köken/ek ve bağlamsal çoklu doğru sayısı mevcut etiketlerden doğrulanamaz.', '',
        '| Sistem | Hatalı sözcük | Uzunluk 1–5 / 6–10 / 11+ | Baş / orta / son | Özel isim vekili | Kısaltma | qwx | Çoklu biçim | Son 3 karakterde hata |',
        '|---|---:|---|---|---:|---:|---:|---:|---:|']
    for name, v in word_summary.items():
        lines.append(f"| {name} | {v['n']} | {v['length']} | {v['position']} | {v['proper_name_proxy']} | {v['acronym_proxy']} | {v['foreign_letter_proxy']} | {v['train_attested_ambiguity']} | {v['error_in_last_3_chars']} |")
    for name in ('sft_zero_shot', 'sft_five_shot'):
        v = word_summary[name]
        lines.append(f"\n{name}: hedef/çıktı ortak önek uzunluğu {v['shared_prefix_length']}; yüzey son-ek eşleşmeleri {v['suffix_surface_hint']}.")
    lines += ['', 'Sözcük bazında tüm girdi/hedef/çıktılar, ortak önek uzunlukları, yüzey ekleri ve eğitimde görülen alternatifler `word-errors.json` içinde.', '',
              '## Dilimler', '', 'En kötü = SFT zero-shot uyum oranı, eşitlikte tam eşleşme; n≥30. '
              'Dilimler farklı eksenlerde örtüşebilir. Kaynak öneki alan etiketi değil, original_sent_id önekidir.', '']
    worst = sorted([s for s in slices if s['system'] == 'sft_zero_shot' and s['n'] >= 30], key=lambda x: (x['strict_compliance'], x['sentence_exact']))[:3]
    for s in worst:
        lines.append(f"- {s['dimension']}={s['value']}: n={s['n']}, uyum {pct(s['strict_compliance'])}, tam eşleşme {pct(s['sentence_exact'])}.")
    lines += ['', '| Sistem | Dilim | n | Uyum | Tam eşleşme |', '|---|---|---:|---:|---:|']
    for s in slices:
        lines.append(f"| {s['system']} | {s['dimension']}={s['value']} | {s['n']} | {pct(s['strict_compliance'])} | {pct(s['sentence_exact'])} |")
    lines += ['', '## Eğitim verisi denetimi', '',
        f"Uyumsuz hedef: {len(audit['invalid_targets'])}/7340. Kaynak kimliği çakışması: {len(audit['source_overlap'])}. "
        f"Eğitim dizisi token quantile’ları (istem+cevap+EOS): {audit['sequence_tokens_including_prompt_and_eos']}. "
        f"1024 üstü: {audit['above_1024']}; kod sınır aşımında hata verir, sessiz kesme yapmaz.", '']
    for name, hits in audit['overlap'].items():
        lines.append(f'- {name}: {len(hits)} doğrulama örneği eğitimde eşleşiyor.')
    lines += ['', 'Normalize eşleme: NFC, Türkçe küçük harf, diakritik katlama, noktalama/boşluk çıkarma; '
              'edit-distance semantik yakınlık araması değildir. Bu tanım dışında yakın kopya yokluğu iddia edilmez.']
    for name, mix in audit['split_mix'].items():
        lines.append(f"\n{name}: n={mix['n']}; gerekli={mix['needs_correction']} ({pct(mix['needs_correction']/mix['n'])}); "
                     f"koruma={mix['preservation']} ({pct(mix['preservation']/mix['n'])}); kategoriler={mix['categories']}.")
    lines += ['', '## 40 örnek ve son işlem simülasyonları', '',
        '[40 örnek incelemesi](review-40.md): 20 ihlal, 10 uyumlu yanlış, 5 doğru→yanlış, 5 yanlış→doğru. '
        '40 benzersiz örnek için geçiş grupları önce ayrılmıştır; seed=42 ve havuz sayıları `sampling.json` içinde. '
        'Diff’ler girdi→çıktı ve hedef→çıktı için karakter düzeyindedir; tüm metinler JSON’da korunur.', '',
        '**Fallback:** ihlalde girdiyi döndürür. **Repair:** diakritikleri katlanmış girdi/çıktıyı SequenceMatcher ile hizalar; '
        'yalnız eşit bloklarda izinli aday değişimlerini alır, diğer tüm karakterleri girdiden kopyalar. '
        'Hedefe erişmez; metrikleri üst tabloda ayrı sistemlerdir. Tekrarlanan parçalarda hizalama yanlış konuma '
        'düzeltme taşıyabilir. Kurala uyum, hedef doğruluğu garantisi değildir. Yeni sistem seçimi henüz yapılmadı.', '',
        '## Seçim kuralı seçenekleri ve maliyet', '',
        'Ham modeller arasında uyum önceliği identity (%100 uyum, %15 tam eşleşme, %0 gerekli düzeltme) seçer. '
        'Fallback ve repair eklendiğinde %100 uyumda eşitlik olur; mevcut tam eşleşme ikinci kuralı artık identity’yi '
        'zorunlu kazanan yapmaz. Aday doğruluğu da korunan 12.032/17.289 konumdan dolayı identity lehine yüksek olabilir.', '',
        'Seçenekler (karar verilmedi; eşikler doğrulama üzerinde sonuca göre ayarlanırsa seçim yanlılığı oluşur):', '',
        '- Ürün gereksiniminden belirlenen uyum eşiği (ör. %99) + gerekli düzeltme başarısı; gereksiz düzeltmeye ayrıca üst sınır. '
        'Eşiği karşılayan aday yoksa model seçmemek veya ayrı korumalı sistem değerlendirmek gerekir.',
        '- %100 uyum sağlayan son işlemli sistemler arasında tam eşleşme, eşitlikte gerekli düzeltme; '
        'bu karar modelden ziyade bütün sistemi seçer, ham model puanları ayrıca kalır.',
        '- Pareto seçenekleri: uyum, gerekli düzeltme ve gereksiz müdahaleyi birlikte sunup kullanım maliyetine göre seçim. '
        'Maliyet ağırlıkları ve eşikler test açılmadan sabitlenir; bu rapor kazananı belirlemez.', '',
        '| Yol | Beklenen kazanç / kanıt | Risk | Süre varsayımı |', '|---|---|---|---|',
        '| Fallback / hizalama | Üst tablodaki gözlenen doğrulama kazancı; eğitim yok | Hizalama yanlış düzeltme taşıyabilir; fallback gerekli düzeltmeyi kaçırır | Mevcut 900 çıktıda CPU ile saniye–dakika; raporda ölçülen ayrı sistem |',
        '| Üretim/durdurma/biçim | Sınır/EOS/biçim tablosundaki şüpheli örnekler kadar inceleme adayı; başarı artışı ölçülmedi | EOS ile normal sonlanma erken anlamsal bitişi dışlamaz; ayar etkisi kontrollü deney ister | Mevcut seconds toplamı / 900 × yeniden üretilecek n; aşağıda tahmin |',
        '| Veri düzeltmesi | Uyumsuz hedef ve kopya sayıları yukarıda; kural uyumu dilsel hedef kalitesini kanıtlamaz | Koruma ağırlığı artarsa identity davranışı güçlenebilir | Planlama varsayımı: 40 örnek × 1–2 dk = 40–80 dk uzman denetimi; yeniden eğitim ayrıca gerekir |',
        '| İkinci eğitim | Kazanç henüz bilinmiyor; yalnız tek değişkenli deney gerekçelendirilebilir | Daha fazla epoch ezberleme/müdahale riskini artırabilir | 459 × 19 sn = 2 sa 25 dk / epoch; 918 adım ≈ 4 sa 51 dk + doğrulama |', '',
        'İkinci eğitim seçilirse başlangıç önerisi rank=8, q_proj/v_proj, 1 epoch sabit tutup '
        'yalnız öğrenme oranı 2e-4→1e-4 veya koruma ağırlığı 1→2 alternatiflerinden birini denemektir. '
        'Bunlar ölçülmüş iyileştirmeler değildir. Koruma örneklerini iki kez sunmak varsayımıyla '
        '8.441 örnek / accumulation 16 → 528 adım ≈ 2 sa 47 dk; ağırlıklı loss kullanılırsa adım 459 kalır. '
        'Rank 16 / daha fazla hedef modül için 19 sn/adım varsayımı doğrulanmaz ve 16 GB bellek ölçümü gerekir. '
        'Loss’un düşmesi tek başına bunları seçmeye yeterli değildir.', '']
    for c in ('zero_shot', 'five_shot'):
        cats = violations['sft_' + c]['categories']
        suspicious = sum(cats[k]['n'] for k in ('empty', 'format', 'limit', 'prefix'))
        sec = protocol['token_audit']['sft_' + c]['seconds_sum'] / 900
        lines.append(f"{c}: boş/biçim/sınır/önek şüphesi {suspicious}/900; aynı hız varsayımıyla yeniden üretim "
                     f"batch-amortize hesap ≈{suspicious*sec:.1f} sn + model yükleme; tüm 900 ≈{900*sec/60:.1f} dk. "
                     'Bu amortize hesap tek bir uzun çıktı için iyimserdir; yukarıdaki 1–3 dakika planlama payı kullanılmalıdır. Bu sayı ayar düzeltmesiyle kurtarılacak örnek sayısı değildir.')
    lines += ['', '**Önerilen sonraki adım:** ölçülmüş fallback ve hizalama sonuçlarını, ham modelden ayrı sistemler olarak '
        'karşılaştırıp seçim kuralını kullanıcıyla sabitlemek; yeniden eğitim kararı öncesi sınırlı niteliksel denetim. '
        'Yeni üretim için önceden süre tahmini ve onay gerekir; bu çalışmada üretim başlatılmadı. Test seti için seçim sabitlenmesi beklenir.', '',
        '## Dosyalar ve sınırlar', '',
        '`analysis.json` toplu ham sayılar; `metrics.csv` pay/payda; `paired.json`, `characters.json`, '
        '`word-errors.json`, `slices.json`, `training-audit.json`, `generation-audit.json` ayrıntılar. '
        'Test ve bütünlük kontrolü: `verification.json`. '
        'Morfoloji, gerçek özel isim/yabancı köken ve bağlamsal belirsizlik otomatik vekillerle kesinleştirilemez. '
        'Kategoriler gözlenen edit türleridir, nedensel etiket değildir. '
        'BOUN kaynak metinleri CC BY-SA 4.0; kaynak/lisans `data/prepared/boun-v1/source/`.', '']
    (OUT / 'README.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
