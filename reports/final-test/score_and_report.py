"""Score saved predictions only; never loads a model or changes the frozen system."""
from datetime import datetime, timezone
import csv
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from deasciification.evaluation import allowed, nfc, read_jsonl, resampling_groups
from scripts.analyze_sft_errors import repair
from scripts.compare_prompts import digest, save, summarize
OUT = ROOT / 'reports/final-test'
METRICS = ['strict_compliance', 'sentence_exact', 'candidate_accuracy', 'required_correction']
ERRORS = ['unnecessary_correction', 'wrongly_changed_word']
LABELS = {'identity': 'Identity', 'pre_zero_shot': 'Eğitim öncesi zero-shot', 'sft_zero_shot': 'Ham SFT', 'sft_zero_shot_fallback': 'SFT+fallback', 'sft_zero_shot_repair': 'SFT+repair'}


def bootstrap(rows, reports):
    groups = resampling_groups(rows)
    indexed = {name: {r['id']: r for r in report['examples']} for name, report in reports.items()}
    arrays = {}
    for name, data in indexed.items():
        arrays[name] = np.array([[*[sum(data[i]['metrics'][m]['correct'] for i in g) for m in METRICS], *[sum(data[i]['metrics'][m]['total'] for i in g) for m in METRICS], *[sum(data[i]['errors'][m] for i in g) for m in ERRORS]] for g in groups], dtype=np.int64)
    samples = {name: [] for name in reports}
    rng = np.random.default_rng(42)
    for _ in range(40):
        selections = rng.integers(0, len(groups), size=(250, len(groups)))
        for name, values in arrays.items():
            sums = values[selections].sum(axis=1)
            samples[name].append(np.column_stack((sums[:, :4] / sums[:, 4:8], sums[:, 8:])))
    samples = {name: np.concatenate(parts) for name, parts in samples.items()}
    intervals = {name: {metric: np.quantile(values[:, i], [.025, .975]).tolist() for i, metric in enumerate(METRICS + ERRORS)} for name, values in samples.items()}
    paired = {name: {metric: np.quantile((samples['sft_zero_shot_repair'] - values)[:, i], [.025, .975]).tolist() for i, metric in enumerate(METRICS + ERRORS)} for name, values in samples.items() if name != 'sft_zero_shot_repair'}
    return {'method': 'source/pair cluster percentile bootstrap', 'seed': 42, 'replicates': 10000, 'groups': len(groups), 'marginal_ci95': intervals, 'repair_minus_comparator_paired_ci95': paired}


def systems(rows, pre_path, sft_path):
    pre, sft = read_jsonl(pre_path), read_jsonl(sft_path)
    expected = [r['id'] for r in rows]
    assert [r['id'] for r in pre] == expected
    assert [r['id'] for r in sft] == expected
    raw = {r['id']: r['output'] for r in sft}
    predictions = {'identity': {r['id']: r['input'] for r in rows}, 'pre_zero_shot': {r['id']: r['output'] for r in pre}, 'sft_zero_shot': raw,
                   'sft_zero_shot_fallback': {r['id']: raw[r['id']] if allowed(nfc(r['input']), nfc(raw[r['id']])) else r['input'] for r in rows},
                   'sft_zero_shot_repair': {r['id']: repair(r['input'], raw[r['id']]) for r in rows}}
    return {name: summarize(rows, outputs) for name, outputs in predictions.items()}


def main():
    manifest = json.loads((OUT / 'freeze-manifest.json').read_text())
    status = json.loads((OUT / 'generation-status.json').read_text())
    assert status['status'] == 'complete', status
    assert digest(OUT / 'freeze-manifest.json') == json.loads((OUT / 'generation-started.json').read_text())['manifest_sha256']
    for name, expected in manifest['file_sha256'].items():
        assert digest(ROOT / name) == expected, name
    for info in manifest['datasets'].values():
        assert digest(ROOT / info['path']) == info['sha256']
    for name, expected in status['output_sha256'].items():
        assert digest(OUT / name) == expected
    reports, intervals = {}, {}
    for split in ('validation', 'test'):
        rows = read_jsonl(ROOT / manifest['datasets'][split]['path'])
        pre = OUT / 'pre_zero_shot.jsonl' if split == 'test' else ROOT / 'reports/validation-prompts/boun-v1-20261015-batch8/zero_shot.jsonl'
        sft = OUT / 'sft_zero_shot.jsonl' if split == 'test' else ROOT / 'reports/sft-validation/first-lora-v1/zero_shot.jsonl'
        reports[split] = systems(rows, pre, sft)
        if split == 'validation':
            for name, old in [('pre_zero_shot', pre.with_name('zero_shot-scores.json')), ('sft_zero_shot', sft.with_name('zero_shot-scores.json'))]:
                assert reports[split][name] == json.loads(old.read_text()), name
            for mode in ('fallback', 'repair'):
                old = ROOT / f'reports/sft-validation/first-lora-v1/error-analysis/zero_shot-{mode}-outputs.json'
                assert {r['id']: r['output'] for r in reports[split]['sft_zero_shot_' + mode]['examples']} == json.loads(old.read_text())
        intervals[split] = bootstrap(rows, reports[split])
        save(OUT / f'{split}-bootstrap.json', intervals[split])
        for name, report in reports[split].items():
            save(OUT / f'{split}-{name}-scores.json', report)
        print(f'{split}: scoring and bootstrap complete', flush=True)
    summaries = {split: {name: report['summary'] for name, report in systems_.items()} for split, systems_ in reports.items()}
    save(OUT / 'comparison.json', {'summaries': summaries, 'bootstrap': intervals, 'test_minus_validation': {name: {m: summaries['test'][name]['metrics'][m]['rate'] - summaries['validation'][name]['metrics'][m]['rate'] for m in METRICS} for name in LABELS}})
    with (OUT / 'metrics.csv').open('w') as stream:
        writer = csv.writer(stream)
        writer.writerow(['split', 'system', 'metric', 'value', 'ci95_low', 'ci95_high', 'numerator', 'denominator'])
        for split in reports:
            for name in LABELS:
                for metric in METRICS + ERRORS:
                    summary = summaries[split][name]
                    value = summary['metrics'][metric]['rate'] if metric in METRICS else summary['errors'][metric]
                    frac = summary['metrics'].get(metric, {})
                    writer.writerow([split, name, metric, value, *intervals[split]['marginal_ci95'][name][metric], frac.get('correct', ''), frac.get('total', '')])
    def cell(split, name, metric):
        s = summaries[split][name]
        lo, hi = intervals[split]['marginal_ci95'][name][metric]
        if metric in METRICS:
            return f"{100*s['metrics'][metric]['rate']:.2f} [{100*lo:.2f}, {100*hi:.2f}]"
        return f"{s['errors'][metric]} [{lo:.1f}, {hi:.1f}]"
    lines = ['# Nihai test: dondurulmuş sistem', '',
        '900 test örneği; 7.340 eğitim ve 900 doğrulama örneğiyle birebir/NFC/normalize girdi-hedef çakışması ve kaynak/pair kimliği çakışması 0. Normalize kontrol Türkçe küçük harf, diakritik katlama ve `\\W+` çıkarımıdır; semantik yakın kopya taraması değildir.', '',
        f"Sistem: Qwen/Qwen3-1.7B + first-lora-v1 (`runs/first-sft-v1/training/adapter`), zero-shot, greedy (`do_sample=False`), batch=8, max_new_tokens=256, MPS/float16, seed=0; parçalama yok. Tek-parça ham çıktıya mevcut `repair` uygulanır. Commit: `{manifest['git_commit']}`. Dondurma öncesi çalışma ağacı temizdi; sonradan yalnız bu rapor dizini oluşturuldu.", '',
        'Kullanıcı onayıyla temel model ve SFT için birer test geçişi yapıldı. Identity üretim gerektirmez; fallback ve repair aynı ham SFT çıktısını kullanır. Fallback, kural ihlalinde girdiyi döndürür; repair hedefe bakmadan izinli dönüşümleri hizalamadan aktarır. Eğitim, ayar değişikliği veya test sonucuna göre seçim yapılmadı.', '',
        'Hücreler değer [%95 GA] biçiminde; ilk dört metrik yüzde, U gereksiz dönüşüm karakter sayısı, W yanlış değiştirilmiş sözcük sayısıdır. Mevcut puanlayıcı ve kaynak/pair bağlantılı küme percentile bootstrap: 10.000 tekrar, seed=42. U/W aralıkları yeniden örneklenen küme toplamlarının aralıklarıdır. Doğrulama çıktıları yeniden üretilmedi.', '',
        '| Sistem | Metrik | Doğrulama | Test |', '|---|---|---:|---:|']
    metric_labels = dict(zip(METRICS + ERRORS, ['Uyum (%)', 'Tam eşleşme (%)', 'Aday doğruluğu (%)', 'Gerekli düzeltme (%)', 'U', 'W']))
    for name in LABELS:
        for metric in METRICS + ERRORS:
            lines.append(f'| {LABELS[name]} | {metric_labels[metric]} | {cell("validation", name, metric)} | {cell("test", name, metric)} |')
    lines += ['', '## Doğrulama–test farkı', '', '| Sistem | Uyum (yp) | Tam eşleşme (yp) | Aday (yp) | Gerekli (yp) |', '|---|---:|---:|---:|---:|']
    for name in LABELS:
        values = [100*(summaries['test'][name]['metrics'][m]['rate'] - summaries['validation'][name]['metrics'][m]['rate']) for m in METRICS]
        lines.append('| ' + LABELS[name] + ' | ' + ' | '.join(f'{v:+.2f}' for v in values) + ' |')
    lines += ['', 'Farklar test−doğrulama betimsel farklarıdır; iki küme eşleştirilmiş değildir. Test içindeki repair−karşılaştırıcı eşleştirilmiş GA’lar `test-bootstrap.json` içindedir.', '', '## Sınırlılıklar ve iddia sınırı', '',
        '- Uyum, dilsel doğruluk garantisi değildir. Mevcut puanlayıcı kural ihlalinde birincil karakter/sözcük başarı paylarını sıfırlar. Aday doğruluğu, korunması gereken konumları da içerir.',
        '- U ve W yalnız eşit uzunluklu çıktılarda sayılır; farklı uzunlukta 0 yazılması hatasızlık değildir. Ham sistemlerle son işlemli sistemlerin U/W toplamları bu yüzden doğrudan hata üstünlüğü göstermez.',
        '- Bootstrap aralıkları bu örneklemdeki belirsizliği gösterir; eğitim tohumu, model seçimi veya alan değişimini kapsamaz. Doğrulama sistem seçiminde kullanılmıştır. Test artık bağımsız yeni seçimler için kullanılmamalıdır.',
        '- Ne iddia edebiliriz: Önceden sabitlenen sistemin bu ayrılmış BOUN testindeki başarısı ve aynı örneklerdeki karşılaştırıcı farkları ölçülmüştür. Repair için elde edilen uyum ve doğruluk ayrı ölçütlerdir.',
        '- Ne iddia edemeyiz: Her Türkçe metinde aynı başarı, tüm hataların düzelmesi, bütün veri sızıntısı türlerinin yokluğu, başka modellerden üstünlük veya tekrar eğitimlerde aynı sonuç garantisi.', '',
        '## Kayıtlar', '',
        '`freeze-manifest.json` değişmeden korunan üretim öncesi anlık kayıttır; içindeki bekleyen onay durumu tarihseldir. Gerçek koşu durumu `generation-status.json`, başlangıç kilidi `generation-started.json`, son bütünlük denetimi `verification.json` içindedir. Ham çıktılar `pre_zero_shot.jsonl` ve `sft_zero_shot.jsonl`; beş sistemin tüm çıktıları ve skorları `test-*-scores.json`; sayısal tablolar `metrics.csv` ve `comparison.json` içindedir.', '']
    (OUT / 'README.md').write_text('\n'.join(lines))
    changes = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=all'], cwd=ROOT, text=True)
    assert all(line.startswith('?? reports/final-test/') for line in changes.splitlines()), changes
    save(OUT / 'verification.json', {'completed_at': datetime.now(timezone.utc).isoformat(), 'frozen_files_unchanged': True, 'manifest_unchanged_since_generation_start': True, 'validation_rescoring_matches_saved_results': True, 'test_examples_per_system': {name: report['summary']['examples'] for name, report in reports['test'].items()}, 'generation_passes': {'pre_zero_shot': 1, 'sft_zero_shot': 1}, 'infrastructure_retries': 0, 'generation_seconds': {name: sum(r['seconds'] for r in read_jsonl(OUT / f'{name}.jsonl')) for name in ('pre_zero_shot', 'sft_zero_shot')}, 'output_sha256': {p.name: digest(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'verification.json'}})
    print(json.dumps(summaries['test'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
