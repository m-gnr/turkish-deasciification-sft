"""Frozen 120/80-character validation-only chunking experiment.

prepare/report never load model weights. calibrate/run require an explicitly recorded
human authorization; authorization must be obtained in chat before invoking either.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import json
import os
from pathlib import Path
import re
import time

from deasciification.evaluation import PAIRS, allowed, aggregate, nfc, read_jsonl
from scripts.analyze_sft_errors import CATEGORY, char_diff, classify, compact, paired, pct, repair
from scripts.compare_prompts import digest, save, summarize

ROOT = Path(__file__).resolve().parents[1]
POST = ROOT / 'reports/sft-validation/first-lora-v1'
OUT = POST / 'chunking'
VALIDATION = ROOT / 'data/prepared/boun-v1/splits/validation.jsonl'
LIMITS = (120, 80)
BATCH_SIZE = 8
CALIBRATION_SIZE = 50
RULE = {'compliance_ci_low_gt': 0, 'exact_ci_low_gt': -0.02,
        'candidate31_compliance_delta_gt': 0, 'length121_compliance_delta_gt': 0}


def priority(prefix):
    tail = prefix.rstrip().rstrip('\"\'’”)]}')
    if tail.endswith(('.', '!', '?', '…')):
        return 2
    if tail.endswith((',', ';', ':', '-', '–', '—')):
        return 1
    return 0


def split_text(text, limit):
    """Raw Unicode character limits; no strip/normalize or word splitting.

    Prefer the rightmost boundary in the highest punctuation class that fits.
    Whitespace stays on the left where possible. An overlong indivisible word
    and its following whitespace form an explicitly tagged exception.
    """
    if limit <= 0:
        raise ValueError('limit must be positive')
    chunks, start = [], 0
    while len(text) - start > limit:
        stop = start + limit
        # After whitespace, prefer complete runs; partial runs are only a fallback.
        boundaries = [i for i in range(start + 1, stop + 1)
                      if text[i-1].isspace() and (i == len(text) or not text[i].isspace())]
        if not boundaries:
            boundaries = [i for i in range(start + 1, stop + 1) if text[i-1].isspace()]
        if boundaries:
            end = max(boundaries, key=lambda i: (priority(text[start:i]), i))
        elif text[stop].isspace():
            # A word exactly fills the budget; preserve following whitespace separately.
            end = stop
        else:
            match = re.match(r'\S+\s*', text[start:])
            if not match:
                raise ValueError('No safe boundary')
            end = start + match.end()
        if end <= start:
            raise ValueError('Splitter did not advance')
        chunks.append(text[start:end])
        start = end
    if start < len(text) or not chunks:
        chunks.append(text[start:])
    validate_split(text, chunks, limit)
    return chunks


def validate_split(text, chunks, limit):
    if ''.join(chunks).encode('utf-8') != text.encode('utf-8'):
        raise ValueError('Byte-level reconstruction failed')
    cursor, exceptions = 0, []
    for i, chunk in enumerate(chunks):
        cursor += len(chunk)
        if cursor < len(text) and not (text[cursor-1].isspace() or text[cursor].isspace()):
            raise ValueError('Word split')
        if len(chunk) > limit:
            words = re.findall(r'\S+', chunk)
            if len(words) != 1 or len(words[0]) <= limit:
                raise ValueError('Unjustified oversize chunk')
            exceptions.append(i)
    return exceptions


def build_plan(rows):
    pieces, summaries = [], {}
    for limit in LIMITS:
        summary = Counter()
        for row in rows:
            chunks = split_text(row['input'], limit)
            unchanged = len(row['input']) <= limit
            summary['split_sentences'] += len(chunks) > 1
            summary['long_but_indivisible'] += len(chunks) == 1 and not unchanged
            summary['reused_sentences'] += unchanged
            start = 0
            for i, chunk in enumerate(chunks):
                mode = 'reuse' if unchanged else 'generate' if any(c in PAIRS for c in chunk) else 'copy'
                piece = {'id': f'chunk{limit}:{row["id"]}:{i}', 'sentence_id': row['id'],
                         'limit': limit, 'index': i, 'start': start, 'end': start + len(chunk),
                         'input': chunk, 'mode': mode, 'oversize_word_exception': len(chunk) > limit}
                pieces.append(piece)
                start += len(chunk)
                summary[mode + '_pieces'] += 1
                summary['total_pieces'] += 1
                summary['oversize_exceptions'] += len(chunk) > limit
            if start != len(row['input']):
                raise ValueError('Bad offsets')
        summaries[str(limit)] = dict(summary)
    # Fixed interleaving: 25 per setting in the first 50; no result-dependent ordering.
    tasks = {limit: [p['id'] for p in pieces if p['limit'] == limit and p['mode'] == 'generate'] for limit in LIMITS}
    schedule = [tasks[limit][i] for i in range(max(map(len, tasks.values()), default=0))
                for limit in LIMITS if i < len(tasks[limit])]
    return {'seed': 42, 'limits': list(LIMITS), 'batch_size': BATCH_SIZE,
            'max_new_tokens': 256, 'do_sample': False, 'enable_thinking': False,
            'prompt': 'unchanged build_messages, zero-shot only', 'decision_rule': RULE,
            'split_rule': 'rightmost fitting whitespace boundary, priority sentence punctuation > clause punctuation > any; no normalization',
            'calibration_size': CALIBRATION_SIZE, 'schedule': schedule,
            'summaries': summaries, 'pieces': pieces}


def load_inputs():
    rows = read_jsonl(VALIDATION)
    if len(rows) != 900 or any(r.get('split') != 'validation' for r in rows):
        raise ValueError('Only fixed validation split is supported')
    # Needed only for diagnostic target slicing. Inputs stay raw throughout generation.
    if any(nfc(r['input']) != r['input'] or nfc(r['target']) != r['target'] or
           len(r['input']) != len(r['target']) for r in rows):
        raise ValueError('Raw target offsets require the current NFC, equal-length dataset')
    old = read_jsonl(POST / 'zero_shot.jsonl')
    scored = summarize(rows, {r['id']: r['output'] for r in old})
    if scored != json.loads((POST / 'zero_shot-scores.json').read_text()):
        raise ValueError('Saved SFT zero-shot rescoring mismatch')
    return rows, old, scored


def protected_paths():
    baseline = ROOT / 'reports/baselines/boun-v1-pre-sft.json'
    base = ROOT / json.loads(baseline.read_text())['run']
    files = [baseline, VALIDATION, *base.glob('*.json*'), *POST.glob('*.json*'), POST / 'README.md']
    files += [p for p in (POST / 'error-analysis').rglob('*') if p.is_file()]
    files += [ROOT / 'runs/first-sft-v1/training/run.json']
    files += list((ROOT / 'runs/first-sft-v1/training/adapter').glob('*'))
    files += [ROOT / p for p in ('scripts/analyze_sft_errors.py', 'deasciification/evaluation.py',
                                 'deasciification/inference.py', 'deasciification/prompting.py', 'deasciification/config.py')]
    return sorted(set(p for p in files if p.is_file()))


def assert_hashes(hashes):
    for name, expected in hashes.items():
        if digest(ROOT / name) != expected:
            raise ValueError(f'Protected file changed: {name}')


def prepared():
    plan = json.loads((OUT / 'plan.json').read_text())
    manifest = json.loads((OUT / 'manifest.json').read_text())
    assert_hashes(manifest['protected_sha256'])
    if digest(OUT / 'plan.json') != manifest['plan_sha256']:
        raise ValueError('Frozen plan changed')
    if digest(Path(__file__)) != manifest['runner_sha256']:
        raise ValueError('Runner changed after plan freeze; inspect before any generation')
    return plan, manifest


def prepare():
    rows, old, scored = load_inputs()
    plan = build_plan(rows)
    if (OUT / 'plan.json').exists():
        previous, _ = prepared()
        if plan != previous:
            raise ValueError('Plan already frozen and differs; do not tune silently')
        print('Existing frozen plan verified.')
        return
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in protected_paths()}
    OUT.mkdir(parents=True, exist_ok=True)
    save(OUT / 'plan.json', plan)
    save(OUT / 'manifest.json', {'status': 'prepared_waiting_calibration_approval',
        'created_at': datetime.now(timezone.utc).isoformat(), 'protected_sha256': hashes,
        'plan_sha256': digest(OUT / 'plan.json'), 'runner_sha256': digest(Path(__file__)),
        'test_set_read': False, 'training_performed': False})
    save(OUT / 'baseline-rescored.json', scored)
    with (OUT / 'pieces.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(plan['pieces'][0]))
        w.writeheader()
        w.writerows(plan['pieces'])
    baseline_seconds = sum(r['seconds'] for r in old)
    estimated = len(plan['schedule']) * baseline_seconds / 900
    save(OUT / 'preflight.json', {'all_1800_split_roundtrips_byte_exact': True,
         'word_boundary_checks_passed': True, 'length_checks_passed': True,
         'baseline_generation_seconds': baseline_seconds,
         'generated_pieces_required': len(plan['schedule']),
         'naive_seconds_using_old_per_example_rate': estimated,
         'calibration_preliminary_estimate_minutes': [1, 3],
         'estimate_caveat': 'Different chunk lengths/batches; first 50 must be timed before full run.'})
    lines = ['# Chunking deneyi — üretim öncesi sabit plan', '',
        'Durum: ilk 50 parça için kullanıcı onayı bekleniyor. Henüz yeni model çıktısı üretilmedi; sonuç/başarı iddiası yok.', '',
        'Yalnız 900 doğrulama cümlesi, yalnız zero-shot. Yeniden eğitim yok, test kümesi açılmadı. '
        'Ayarlar sonuç görülmeden sabit: A=120, B=80 karakter. Greedy, 256 yeni token, thinking kapalı, '
        'aynı build_messages/şablon/durdurma ve 8’li batch. Seed=42.', '',
        'Bölme: sınır içinde en sağdaki en yüksek öncelikli whitespace sınırı; .!?… > ,;:-–— > herhangi boşluk. '
        'Noktalama sonrası kapanış tırnağı/parantezi öncelik tayininde yok sayılır, metinden silinmez. '
        'Boşluklar mümkün olduğunda sol parçada tutulur; uzun whitespace dizileri gerekirse bölünür. '
        'Sözcük ortasından kesilmez. Sınırı aşan tek sözcük ve sonrasındaki boşluk istisnası kayda alınır. '
        'Girdiler strip/normalize edilmez; birleştirmede ayraç eklenmez.', '',
        'Sınır içindeki cümleler mevcut çıktıdan alınır; bu öncelik hiç aday içermeyen kısa cümlelerde de geçerlidir. '
        'Yalnız yeni parçalarda aday bulunmuyorsa girdi kopyalanır. A/B arasında ayrıca çıktı önbelleği paylaşılmaz.', '',
        '| Ayar | Bölünen cümle | Mevcut çıktısı kullanılan cümle | Toplam parça | Üretilecek | Aday yok/kopya | Uzun sözcük istisnası |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for limit in LIMITS:
        v = plan['summaries'][str(limit)]
        lines.append(f"| {limit} | {v['split_sentences']} | {v['reused_sentences']} | {v['total_pieces']} | {v.get('generate_pieces',0)} | {v.get('copy_pieces',0)} | {v['oversize_exceptions']} |")
    lines += ['', '900×2 bölme/birleştirme ham UTF-8 bayt düzeyinde doğrulandı; sözcük sınırı ve uzunluk kontrolleri geçti.', '',
        f"Önceki 900 çıktı üretimi {baseline_seconds/60:.2f} dk. Aynı amortize süreyle yeni parçalar için kaba hesap {estimated/60:.2f} dk; "
        'bu henüz ölçülmüş chunking süresi değildir. İlk 50 üretim parçası (sabit A/B sırasından 25’er adet), '
        'model yükleme dahil yaklaşık 1–3 dakika. Bu çalıştırmadan önce kullanıcı onayı gerekir. '
        'Kalibrasyon çıktıları saklanır, devamda tekrar üretilmez. Ölçülen süreyle kalan iş tahmin edilir ve devam için ayrı onay beklenir.', '',
        'Sabit karar: uyum farkı %95 bootstrap alt sınırı >0; tam eşleşme farkı alt sınırı >−2 yüzde puan; '
        '31+ aday ve 121+ karakter dilimlerindeki uyum farkları ayrıca gösterilir ve her ikisinin nokta tahmini >0 olmalıdır. '
        'Alt dilimler için ilave anlamlılık eşiği konulmaz. 10.000 tekrar, seed=42, mevcut kaynak/pair kümeleri; exact McNemar. '
        'Bu deneyin başarı kararı nihai sistem seçimi değildir.', '',
        'Komutlar: `.venv/bin/python -m scripts.run_chunking prepare`; onaydan sonra `calibrate --approval-note ...`, '
        'ayrı devam onayından sonra `run --approval-note ...`; sonuçlar için `report`. '
        'Üretim komutları kendiliğinden çağrılmaz. `plan.json`, `pieces.csv`, `manifest.json`, `preflight.json` sabit hazırlık kanıtlarıdır.', '']
    (OUT / 'README.md').write_text('\n'.join(lines))
    assert_hashes(hashes)
    print(json.dumps(plan['summaries'], ensure_ascii=False, indent=2))
    print(f'Generation tasks: {len(plan["schedule"])}; naive minutes: {estimated/60:.2f}')


def completed_records():
    p = OUT / 'generated.jsonl'
    records = read_jsonl(p) if p.exists() else []
    return {r['id']: r for r in records}


def run_generation(stage, approval_note):
    if not approval_note or not approval_note.strip():
        raise ValueError('Explicit human approval must be obtained and recorded before generation')
    plan, manifest = prepared()
    done = completed_records()
    if not set(done) <= set(plan['schedule']):
        raise ValueError('Unexpected generated IDs')
    desired = plan['schedule'][:CALIBRATION_SIZE] if stage == 'calibrate' else plan['schedule']
    if stage == 'run' and not set(plan['schedule'][:CALIBRATION_SIZE]) <= set(done):
        raise ValueError('Finish the approved calibration and obtain a new runtime approval first')
    lookup = {p['id']: p for p in plan['pieces']}
    todo = [lookup[i] for i in desired if i not in done]
    if not todo:
        print('Requested stage already complete; no generation.')
        return
    lock = OUT / 'generation.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    started = time.monotonic()
    events_path = OUT / 'runs.json'
    events = json.loads(events_path.read_text()) if events_path.exists() else []
    event = {'stage': stage, 'approval_note': approval_note, 'status': 'loading',
             'started_at': datetime.now(timezone.utc).isoformat(), 'requested_pieces': len(todo),
             'completed_pieces': 0, 'generation_seconds': 0.0}
    events.append(event)
    save(events_path, events)
    try:
        from peft import PeftModel
        import torch
        from deasciification.inference import load_model, generate_batch
        torch.manual_seed(42)
        tokenizer, model, device, dtype = load_model()
        model = PeftModel.from_pretrained(model, ROOT / 'runs/first-sft-v1/training/adapter', is_trainable=False)
        model.config.use_cache = True
        model.eval()
        eos = model.generation_config.eos_token_id
        eos_ids = {eos} if isinstance(eos, int) else set(eos or [])
        event.update(status='generating', load_seconds=time.monotonic()-started,
                     device=device, dtype=str(dtype), eos_token_ids=sorted(eos_ids))
        save(events_path, events)
        with (OUT / 'generated.jsonl').open('a') as stream:
            for offset in range(0, len(todo), BATCH_SIZE):
                batch = todo[offset:offset+BATCH_SIZE]
                t = time.monotonic()
                predictions = generate_batch(tokenizer, model, device, [p['input'] for p in batch], (), 256)
                elapsed = time.monotonic()-t
                for piece, (output, tokens) in zip(batch, predictions, strict=True):
                    record = {'id': piece['id'], 'sentence_id': piece['sentence_id'], 'limit': piece['limit'],
                              'output': output, 'generated_token_ids': tokens, 'generated_tokens': len(tokens),
                              'reached_token_limit': len(tokens) >= 256,
                              'ends_with_eos': bool(tokens and tokens[-1] in eos_ids),
                              'batch_seconds': elapsed, 'seconds': elapsed/len(batch),
                              'run_index': len(events)-1, 'batch_offset': offset, 'batch_size': len(batch)}
                    stream.write(json.dumps(record, ensure_ascii=False)+'\n')
                    done[piece['id']] = record
                stream.flush()
                os.fsync(stream.fileno())
                event['completed_pieces'] += len(batch)
                event['generation_seconds'] += elapsed
                save(events_path, events)
                print(f'{stage}: {event["completed_pieces"]}/{len(todo)} chunks; {elapsed:.2f}s batch', flush=True)
        event.update(status='complete', wall_seconds=time.monotonic()-started)
    except BaseException as error:
        event.update(status='failed', error=str(error), wall_seconds=time.monotonic()-started)
        raise
    finally:
        save(events_path, events)
        lock.unlink()
        assert_hashes(manifest['protected_sha256'])
    first = [done[i] for i in plan['schedule'][:CALIBRATION_SIZE] if i in done]
    mean_seconds = sum(r['seconds'] for r in first) / len(first)
    remaining = len(plan['schedule'])-len(done)
    timing = {'calibration_pieces': len(first), 'calibration_generation_seconds': sum(r['seconds'] for r in first),
              'seconds_per_piece_amortized': mean_seconds, 'remaining_pieces': remaining,
              'remaining_generation_seconds_estimate': mean_seconds*remaining,
              'range_minutes_0_7_to_1_5_multiplier': [mean_seconds*remaining*.7/60, mean_seconds*remaining*1.5/60],
              'note': 'First 50 are fixed, not a random speed sample. Lengths, batch shape and thermal throttling can change rate.'}
    save(OUT / 'timing-estimate.json', timing)
    manifest['status'] = 'generation_complete' if not remaining else 'calibration_complete_waiting_run_approval'
    save(OUT / 'manifest.json', manifest)
    print(json.dumps(timing, ensure_ascii=False, indent=2))


def assemble(plan, done, old):
    old = {r['id']: r for r in old}
    outputs, detail = {n: {} for n in LIMITS}, []
    for piece in plan['pieces']:
        mode = piece['mode']
        if mode == 'reuse':
            value = old[piece['sentence_id']]['output']
            record = old[piece['sentence_id']]
        elif mode == 'copy':
            value, record = piece['input'], {}
        else:
            record = done[piece['id']]
            value = record['output']
        dest = outputs[piece['limit']]
        dest[piece['sentence_id']] = dest.get(piece['sentence_id'], '') + value
        detail.append({**piece, 'output': value,
                       'compliant': allowed(nfc(piece['input']), nfc(value)),
                       'at_limit_without_eos': record.get('reached_token_limit', False) and not record.get('ends_with_eos', True)})
    return outputs, detail


def boundary_diagnostics(detail, rows, before, systems):
    """Boundary symptoms vs the immutable input, plus whole-sentence regressions.

    Do not repair trailing whitespace: preserving raw output exposes this failure.
    Target snippets and proximity are observational, not proof of lost context.
    """
    lookup = {r['id']: r for r in rows}
    groups = defaultdict(list)
    for p in detail:
        groups[(p['limit'], p['sentence_id'])].append(p)
    boundaries, regressions = [], {n: [] for n in LIMITS}
    pre = {r['id']: r for r in before}
    for (limit, sid), pieces in groups.items():
        row = lookup[sid]
        result = systems[f'sft_zero_shot_chunk{limit}']
        r = next(x for x in result if x['id'] == sid)
        before_exact = bool(pre[sid]['metrics']['sentence_exact']['correct'])
        after_exact = bool(r['metrics']['sentence_exact']['correct'])
        for left, right in zip(pieces, pieces[1:]):
            trailing_in = re.search(r'\s*$', left['input']).group()
            trailing_out = re.search(r'\s*$', left['output']).group()
            leading_in = re.match(r'\s*', right['input']).group()
            leading_out = re.match(r'\s*', right['output']).group()
            def terminal_punct(s):
                return re.search(r'[^\w\s]*$', s.rstrip()).group()
            boundaries.append({'limit': limit, 'sentence_id': sid, 'offset': left['end'],
                'left_input_tail': left['input'][-25:], 'left_output_tail': left['output'][-25:],
                'right_input_head': right['input'][:25], 'right_output_head': right['output'][:25],
                'trailing_whitespace_changed': trailing_in != trailing_out,
                'leading_whitespace_changed': leading_in != leading_out,
                'terminal_punctuation_changed': terminal_punct(left['input']) != terminal_punct(left['output']),
                'old_compliant': bool(pre[sid]['metrics']['strict_compliance']['correct']),
                'new_compliant': bool(r['metrics']['strict_compliance']['correct'])})
        if len(pieces) > 1 and before_exact and not after_exact:
            piece_errors = []
            for piece in pieces:
                target = row['target'][piece['start']:piece['end']]
                if target != piece['output']:
                    piece_errors.append({'index': piece['index'], 'input': piece['input'], 'target': target,
                                         'output': piece['output'], 'target_diff': char_diff(target, piece['output'])})
            regressions[limit].append({'id': sid, 'input': row['input'], 'target': row['target'],
                'single_output': pre[sid]['output'], 'chunk_output': r['output'],
                'boundaries': [p['end'] for p in pieces[:-1]], 'pieces': piece_errors,
                'diff': char_diff(row['target'], r['output']),
                'interpretation': 'Chunking-associated regression; context loss is a hypothesis, not a proven cause.'})
    return boundaries, regressions


def decide(intervals, slice_deltas):
    m = intervals['metrics']
    checks = {'compliance_ci_low_positive': m['strict_compliance']['ci95'][0] > RULE['compliance_ci_low_gt'],
              'exact_noninferiority_2pp': m['sentence_exact']['ci95'][0] > RULE['exact_ci_low_gt'],
              'candidate31_compliance_increased': slice_deltas['candidates31+'] > 0,
              'length121_compliance_increased': slice_deltas['length121+'] > 0}
    return {'checks': checks, 'worked_under_frozen_rule': all(checks.values())}


def report():
    plan, manifest = prepared()
    done = completed_records()
    if set(done) != set(plan['schedule']):
        raise ValueError('All planned generation must finish before reporting results')
    rows, old, base = load_inputs()
    outputs, detail = assemble(plan, done, old)
    systems = {'sft_zero_shot': base['examples']}
    for limit in LIMITS:
        name = f'sft_zero_shot_chunk{limit}'
        systems[name] = summarize(rows, outputs[limit])['examples']
        save(OUT / f'{name}-outputs.json', outputs[limit])
    for name in list(systems):
        result = systems[name]
        for mode in ('repair', 'fallback'):
            transformed = {r['id']: repair(r['input'], r['output']) if mode == 'repair' else
                           r['output'] if r['metrics']['strict_compliance']['correct'] else r['input'] for r in result}
            systems[name+'_'+mode] = summarize(rows, transformed)['examples']
            save(OUT / f'{name}_{mode}-outputs.json', transformed)
    metrics = {name: compact(result) for name, result in systems.items()}
    save(OUT / 'metrics.json', metrics)
    save(OUT / 'piece-outputs.json', detail)
    boundaries, regressions = boundary_diagnostics(detail, rows, systems['sft_zero_shot'], systems)
    save(OUT / 'boundaries.json', boundaries)
    save(OUT / 'regressions.json', {str(k): v for k, v in regressions.items()})
    selectors = {'candidates31+': lambda r: sum(c in PAIRS for c in r['input']) >= 31,
                 'candidates21-30': lambda r: 21 <= sum(c in PAIRS for c in r['input']) <= 30,
                 'length121+': lambda r: len(r['input']) >= 121,
                 'length81-120': lambda r: 81 <= len(r['input']) <= 120,
                 'needs_correction': lambda r: r['input'] != r['target'],
                 'preservation': lambda r: r['input'] == r['target']}
    slices = {name: {key: aggregate([r for r in result if predicate(r)]) for key, predicate in selectors.items()}
              for name, result in systems.items()}
    save(OUT / 'slices.json', slices)
    transitions, decisions, categories, pieces_summary, boundary_summary = {}, {}, {}, {}, {}
    piece_lookup = defaultdict(list)
    for p in detail:
        piece_lookup[(p['limit'], p['sentence_id'])].append(p)
    for name in ('sft_zero_shot', 'sft_zero_shot_chunk120', 'sft_zero_shot_chunk80'):
        limit = None if name == 'sft_zero_shot' else int(name.split('chunk')[-1])
        counts = Counter(classify(r['input'], r['output'],
                         any(p['at_limit_without_eos'] for p in piece_lookup[(limit, r['id'])]) if limit else False)
                         for r in systems[name])
        categories[name] = dict(counts)
    save(OUT / 'categories.json', categories)
    for limit in LIMITS:
        name = f'sft_zero_shot_chunk{limit}'
        transitions[str(limit)] = paired(rows, systems['sft_zero_shot'], systems[name])
        deltas = {k: slices[name][k]['metrics']['strict_compliance']['rate'] -
                     slices['sft_zero_shot'][k]['metrics']['strict_compliance']['rate'] for k in ('candidates31+', 'length121+')}
        decisions[str(limit)] = decide(transitions[str(limit)], deltas) | {'slice_compliance_deltas': deltas}
        selected = [p for p in detail if p['limit'] == limit]
        buckets = defaultdict(list)
        for p in selected:
            buckets['mode:'+p['mode']].append(p)
            if p['mode'] != 'reuse':
                length = len(p['input'])
                buckets['new_length:'+('1-40' if length <= 40 else '41-80' if length <= 80 else '81-120' if length <= 120 else '121+')].append(p)
        pieces_summary[str(limit)] = {k: {'n': len(v), 'violations': sum(not p['compliant'] for p in v),
                                           'violation_rate': sum(not p['compliant'] for p in v)/len(v)} for k,v in buckets.items()}
        bs = [b for b in boundaries if b['limit'] == limit]
        boundary_summary[str(limit)] = {'boundaries': len(bs),
            **{key: sum(b[key] for b in bs) for key in ('trailing_whitespace_changed','leading_whitespace_changed','terminal_punctuation_changed')},
            'sentences_with_boundary_symptom': len({b['sentence_id'] for b in bs if any(b[k] for k in ('trailing_whitespace_changed','leading_whitespace_changed','terminal_punctuation_changed'))}),
            'previously_compliant_new_violation_with_boundary_symptom': len({b['sentence_id'] for b in bs if b['old_compliant'] and not b['new_compliant'] and any(b[k] for k in ('trailing_whitespace_changed','leading_whitespace_changed','terminal_punctuation_changed'))})}
    save(OUT / 'paired.json', transitions)
    save(OUT / 'decision.json', decisions)
    save(OUT / 'piece-summary.json', pieces_summary)
    save(OUT / 'boundary-summary.json', boundary_summary)
    events = json.loads((OUT / 'runs.json').read_text())
    old_seconds = sum(r['seconds'] for r in old)
    costs = {'baseline_generation_seconds': old_seconds, 'total_run_wall_seconds': sum(e.get('wall_seconds',0) for e in events),
             'total_load_seconds': sum(e.get('load_seconds',0) for e in events),
             'total_generation_seconds': sum(r['seconds'] for r in done.values()),
             'note': 'Mixed A/B batches: per-setting generation time is amortized, not isolated wall time.', 'settings': {}}
    for limit in LIMITS:
        records = [r for r in done.values() if r['limit'] == limit]
        duration = sum(r['seconds'] for r in records)
        reuse_ids = {p['sentence_id'] for p in detail if p['limit'] == limit and p['mode'] == 'reuse'}
        old_reused_seconds = sum(r['seconds'] for r in old if r['id'] in reuse_ids)
        costs['settings'][str(limit)] = {'generated_pieces':len(records), 'generation_seconds':duration,
            'seconds_per_generated_piece':duration/len(records) if records else None,
            'incremental_vs_baseline_ratio': duration/old_seconds,
            'estimated_cold_all900_seconds': duration+old_reused_seconds,
            'estimated_cold_vs_baseline_ratio': (duration+old_reused_seconds)/old_seconds,
            'reused_historical_seconds':old_reused_seconds}
    save(OUT / 'costs.json', costs)
    with (OUT / 'metrics.csv').open('w') as f:
        w = csv.writer(f); w.writerow(['system','metric','correct','total','rate'])
        for name,v in metrics.items():
            for metric,m in v['all']['metrics'].items():
                w.writerow([name,metric,m['correct'],m['total'],m['rate']])
    render_report(plan, metrics, categories, slices, transitions, decisions, pieces_summary,
                  boundary_summary, regressions, costs)
    assert_hashes(manifest['protected_sha256'])
    manifest.update(status='complete', finished_at=datetime.now(timezone.utc).isoformat(), protected_hashes_unchanged=True,
                    output_sha256={p.name:digest(p) for p in OUT.iterdir() if p.is_file() and p.name != 'manifest.json'})
    save(OUT / 'manifest.json',manifest)


def render_report(plan, metrics, categories, slices, transitions, decisions, pieces_summary, boundaries, regressions, costs):
    lines=['# İlk LoRA: sabit chunking deneyi', '',
           '900 doğrulama cümlesi, yalnız zero-shot; yeniden eğitim ve test kümesi erişimi yok. '
           'Sabit A=120/B=80 karakter, seed=42, batch=8, greedy, max_new_tokens=256, thinking kapalı. '
           'Mevcut şablon, durdurma ve puanlayıcı aynen kullanıldı. Ayarlar sonuçlardan sonra değiştirilmedi.', '',
           '## Sabit karar kuralı', '',
           'Uyum farkının %95 bootstrap alt sınırı >0; tam eşleşme farkının alt sınırı >−2 yüzde puan; '
           '31+ aday ve 121+ karakter dilimlerinde uyum nokta farkları >0. 10.000 kaynak/pair kümeli tekrar, seed=42. '
           'Bu sonuç nihai sistem seçimi değildir. İki ayarın sınanması ve tek doğrulama kümesi seçim yanlılığı riski taşır; test açılmadı.', '']
    for limit in LIMITS:
        d=decisions[str(limit)]
        lines.append(f"- **{limit}: {'İŞE YARADI (sabit kurala göre)' if d['worked_under_frozen_rule'] else 'İŞE YARAMADI (sabit kural karşılanmadı)'}**; kontroller: {d['checks']}.")
    lines += ['', '## Sistem metrikleri', '',
        'U/W mevcut puanlayıcının gereksiz dönüşüm/yanlış değişen sözcük sayılarıdır; uzunluğu farklı çıktılarda sayılmadığı için ham sistemler arasında eksik sayım vardır. '
        'Koşullu metrikler farklı uyumlu alt kümeleri karşılaştırır. Repair/fallback ayrı sistemlerdir; ham model başarısı olarak sunulmaz.', '',
        '| Sistem | Uyum | Tam | Aday | Gerekli | Uyumlu: tam | Uyumlu: aday | Uyumlu: gerekli | U | W | Unalignable |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,v in metrics.items():
        m,c=v['all']['metrics'],v['compliant_only']['metrics']
        vals=[m[k]['rate'] for k in ('strict_compliance','sentence_exact','candidate_accuracy','required_correction')]
        vals += [c[k]['rate'] for k in ('sentence_exact','candidate_accuracy','required_correction')]
        e=v['all']['errors']
        lines.append('| '+name+' | '+' | '.join(map(pct,vals))+f" | {e['unnecessary_correction']} | {e['wrongly_changed_word']} | {e['unalignable']} |")
    lines += ['', '## Parçalar ve sınırlar', '',
        'Ham parçalar ayraç eklenmeden birleştirildi; çıktı boşlukları düzeltilmedi. '
        'Sınır içindeki cümlelerde eski çıktı kullanıldı; aday içermeyen yeni parçalar kopyalandı. '
        'Bölme/birleştirme ham bayt eşitliği ve sözcük/uzunluk kontrolleri tüm 900×2 girdide geçti. '
        'Tek aşırı uzun sözcük istisnaları plan içinde işaretlidir. Sınır belirtileri nedensel kanıt değildir.', '',
        '| Ayar | Bölünen cümle | Eski çıktı | Toplam parça | Yeni üretim | Kopya | Uzun sözcük istisnası |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for limit in LIMITS:
        v=plan['summaries'][str(limit)]
        lines.append(f"| {limit} | {v['split_sentences']} | {v['reused_sentences']} | {v['total_pieces']} | {v.get('generate_pieces',0)} | {v.get('copy_pieces',0)} | {v['oversize_exceptions']} |")
    lines += ['', '| Ayar / parça grubu | n | İhlal | İhlal oranı |', '|---|---:|---:|---:|']
    for limit, groups in pieces_summary.items():
        for name,v in groups.items():
            lines.append(f"| {limit}/{name} | {v['n']} | {v['violations']} | {pct(v['violation_rate'])} |")
    for limit,v in boundaries.items():
        lines.append(f"\n{limit} sınır tanısı: {v}.")
    lines += ['', '## İhlal kategorileri', '',
        'Mevcut hata analizi sınıflandırıcısı ve öncelik sırası aynen kullanıldı. Kategoriler birbirini dışlar; sınır belirtileri ayrıca örtüşebilir.', '',
        '| Kategori | Tek parça | 120 | 80 |', '|---|---:|---:|---:|']
    for key,label in CATEGORY.items():
        lines.append('| '+label+' | '+' | '.join(str(categories[n].get(key,0)) for n in ('sft_zero_shot','sft_zero_shot_chunk120','sft_zero_shot_chunk80'))+' |')
    lines += ['', '## Eşleştirilmiş geçişler', '',
        'Fark=parçalı−tek parça; GA yüzde puan. Exact McNemar cümle bağımsızlığı varsayar; kaynak bağımlılığını bootstrap korur.', '',
        '| Ayar / metrik | İkisi evet | Yalnız önce | Yalnız sonra | İkisi hayır | Fark yp | %95 GA yp | McNemar p |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for limit,v in transitions.items():
        for name,m in v['metrics'].items():
            lines.append(f"| {limit}/{name} | {m['both_yes']} | {m['before_only']} | {m['after_only']} | {m['both_no']} | {m['difference']*100:.2f} | [{m['ci95'][0]*100:.2f}, {m['ci95'][1]*100:.2f}] | {m['mcnemar_exact_two_sided_p']:.4g} |")
    lines += ['', '## Dilimler', '', '| Sistem / dilim | n | Uyum | Tam | Aday | Gerekli |', '|---|---:|---:|---:|---:|---:|']
    for name,groups in slices.items():
        for key,v in groups.items():
            lines.append(f"| {name}/{key} | {v['examples']} | "+' | '.join(pct(v['metrics'][k]['rate']) for k in ('strict_compliance','sentence_exact','candidate_accuracy','required_correction'))+' |')
    lines += ['', '## Maliyet', '',
        f"Önceki tek-parça üretim {costs['baseline_generation_seconds']/60:.2f} dk; yeni toplam üretim {costs['total_generation_seconds']/60:.2f} dk; "
        f"model yükleme {costs['total_load_seconds']/60:.2f} dk; çalıştırma duvar süresi {costs['total_run_wall_seconds']/60:.2f} dk. "
        'A/B karışık batch süreleri parçalara eşit paylaştırılmıştır; ayar başına ayrı duvar süresi değildir. '
        'Ek maliyet yalnız yeni üretimi; soğuk 900 tahmini yeniden kullanılan kısa cümlelerin tarihsel üretim süresini de içerir.', '',
        '| Ayar | Yeni parça | Üretim dk | sn/parça | Ek / eski süre | Soğuk 900 tahmini dk | Soğuk / eski |', '|---|---:|---:|---:|---:|---:|---:|']
    for limit,v in costs['settings'].items():
        lines.append(f"| {limit} | {v['generated_pieces']} | {v['generation_seconds']/60:.2f} | {v['seconds_per_generated_piece']:.2f} | {v['incremental_vs_baseline_ratio']:.2f}× | {v['estimated_cold_all900_seconds']/60:.2f} | {v['estimated_cold_vs_baseline_ratio']:.2f}× |")
    lines += ['', '## Tek parçada doğru, parçalıda yanlış örnekler', '',
        'Her ayardan sabit veri sırasındaki en çok 10 örnek gösterilir; tüm regresyonlar `regressions.json` içinde. '
        'Bağlam kaybı olası açıklamadır; bu karşılaştırma onu boşluk kaybı, batch değişikliği ve diğer üretim etkilerinden nedensel olarak ayırmaz.']
    for limit,items in regressions.items():
        lines += ['', f'### {limit}: toplam {len(items)} regresyon', '']
        for r in items[:10]:
            lines += [f"#### {r['id']}", '', f"Bölme konumları: {r['boundaries']}", '', '```text',
                      'Girdi: '+r['input'], 'Hedef: '+r['target'], 'Tek parça: '+r['single_output'],
                      'Parçalı: '+r['chunk_output'], '```', '', 'Hedef → çıktı farkı:',
                      '```json',json.dumps(r['diff'],ensure_ascii=False),'```','']
    lines += ['', '## Sınırlar ve devam', '',
        'Sözcük bağlamı kaybı ve sınır boşlukları ayrı belirtilerle raporlandı; nedensel ayrıştırma için yeni kontrollü ayar gerekir ve bu plana eklenmedi. '
        'Başarısızlık varsa sabit kuralın sonucu yukarıda açıkça yazılıdır. Repair daha çok doğru düzeltme üretirken U/W maliyeti taşıyabilir. '
        'Nihai sistem seçilmedi. Yeni ayar, üretim veya test açılması için kullanıcı kararı beklenir.', '',
        'Orijinal dosyaların başlangıç/son SHA-256 kontrolü `manifest.json` içindedir. '
        '`plan.json` tüm parçaları ve sabit sırayı; `generated.jsonl` tüm yeni token dizilerini; `piece-outputs.json` kopya/eski/yeni tüm parçaları saklar. '
        'BOUN kaynak metinleri CC BY-SA 4.0.', '']
    (OUT / 'README.md').write_text('\n'.join(lines))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['prepare','calibrate','run','report'])
    parser.add_argument('--approval-note', default=None)
    args=parser.parse_args()
    if args.stage=='prepare': prepare()
    elif args.stage=='report': report()
    else: run_generation(args.stage,args.approval_note)


if __name__=='__main__':
    main()
