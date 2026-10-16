"""Render the completed validation prompt comparison as a reviewable report."""
import argparse
import json
from pathlib import Path
from deasciification.evaluation import read_jsonl

LABELS = {
    'sentence_exact': 'Cümle tam eşleşmesi',
    'strict_compliance': 'Katı yönerge uyumu',
    'required_correction': 'Gerekli düzeltme başarısı',
    'word_preservation': 'Doğru kelimeleri koruma',
    'candidate_accuracy': 'Aday harf doğruluğu',
}


def percentage(value):
    return f"%{100 * value:.2f}".replace('.', ',')


def cell(metric):
    return f"{metric['correct']}/{metric['total']} ({percentage(metric['rate'])})" if metric['rate'] is not None else 'N/A'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    root = args.directory
    metadata = json.loads((root / 'metadata.json').read_text())
    if metadata['status'] != 'complete':
        raise ValueError('Run is not complete')
    comparison = json.loads((root / 'comparison.json').read_text())
    demos = json.loads((root / 'demonstrations.json').read_text())
    lines = ['# Eğitim öncesi doğrulama: sıfır ve beş örnekli istem', '',
             'BOUN v1 doğrulama kümesinin 900 kaydının tamamı kullanıldı. Test kümesi değerlendirilmedi. '
             'Bu sonuçlar SFT öncesindeki Qwen3-1.7B checkpoint’ine aittir.', '',
             '| Ölçüm | Hiç değiştirme | Sıfır örnek | Sabit beş örnek |',
             '| --- | ---: | ---: | ---: |']
    for metric, label in LABELS.items():
        lines.append('| ' + label + ' | ' + ' | '.join(cell(comparison['summary'][c]['metrics'][metric]) for c in ['identity', 'zero_shot', 'five_shot']) + ' |')
    lines.extend(['', '## Eşleştirilmiş farklar', '',
                  'Fark = beş örnek − sıfır örnek, yüzde puan. %95 güven aralıkları '
                  '2.000 eşleştirilmiş bootstrap tekrarından hesaplandı (tohum 20261015). '
                  'Aynı kaynak ve minimal çift bağlantıları birlikte örneklendi. '
                  'Aralıklar farklı eğitim tohumları veya farklı örnekli istem seçimleri arasındaki değişkenliği kapsamaz.', '',
                  '| Ölçüm | Fark (yüzde puan) | %95 güven aralığı |', '| --- | ---: | ---: |'])
    for metric, label in LABELS.items():
        interval = comparison['paired_bootstrap']['metrics'][metric]
        low, high = interval['ci95']
        lines.append(f"| {label} | {100 * interval['difference']:+.2f} | [{100 * low:+.2f}, {100 * high:+.2f}] |")
    lines.extend(['', '## Kategori sonuçları', '', '| Kategori | N | Sıfır örnek: tam eşleşme | Beş örnek: tam eşleşme | Sıfır örnek: uyum | Beş örnek: uyum |', '| --- | ---: | ---: | ---: | ---: | ---: |'])
    for category in ['tam', 'kismi', 'koruma']:
        zero = comparison['by_category']['zero_shot'][category]
        few = comparison['by_category']['five_shot'][category]
        lines.append(f"| {category} | {zero['examples']} | " + ' | '.join(cell(r['metrics'][m]) for m in ['sentence_exact', 'strict_compliance'] for r in [zero, few]) + ' |')
    zero_examples = {r['id']: r for r in json.loads((root / 'zero_shot-scores.json').read_text())['examples']}
    few_examples = json.loads((root / 'five_shot-scores.json').read_text())['examples']
    lines.extend(['', '## Aynı girdide değişen sonuçlar', '',
                  'Her grupta doğrulama dosyası sırasındaki ilk iki örnek gösterilir; tüm çıktılar puan dosyalarındadır.', ''])
    for label, before, after in [('Tam eşleşmeye geçen', 0, 1), ('Tam eşleşmeyi kaybeden', 1, 0)]:
        shown = 0
        lines.extend([f'### {label}', ''])
        for few in few_examples:
            zero = zero_examples[few['id']]
            if zero['metrics']['sentence_exact']['correct'] == before and few['metrics']['sentence_exact']['correct'] == after:
                lines.extend([f"`{few['id']}`", '', '```text', f"Girdi: {few['input']}",
                              f"Hedef: {few['target']}", f"Sıfır: {zero['output']}",
                              f"Beş:   {few['output']}", '```', ''])
                shown += 1
                if shown == 2:
                    break
    lines.extend(['', '## Sabit örnekler ve yöntem', '',
                  'Örnekler yalnızca eğitim bölümünden, 40–150 karakter uzunluğundaki girdiler arasından '
                  '`SHA256("few-shot-v1:" + id)` sırasıyla seçildi: 3 tam ASCII, 1 kısmi ASCII, 1 koruma. '
                  'Seçim doğrulama sonuçlarına göre değiştirilmedi. Her girdiye aynı sırada aynı beş '
                  'user/assistant mesaj çifti eklendi; sıfır örnekli koşulda bu çiftler yoktur. '
                  'Sistem yönergesi iki koşulda aynıdır.', ''])
    for row in demos['examples']:
        lines.extend([f"- `{row['id']}`", f"  - Girdi: {row['input']}", f"  - Hedef: {row['target']}"])
    lines.extend(['', f"Model: `{metadata['model']}`; revision: `{metadata['revision']}`. "
                  f"Cihaz: `{metadata['device']}`, veri türü: `{metadata['dtype']}`. "
                  'Düşünme kapalı, örnekleme kapalı, tohum 0, maksimum 256 yeni token; sol dolgulama ile sekizli gruplar. '
                  'Önce sıfır örnekli, sonra beş örnekli koşul çalıştırıldı. Ham çıktılar temizlenmedi; '
                  'ortak değerlendirici yalnızca NFC normalizasyonu yapar. Kural dışı çıktılar katı metriklerde başarısızdır.', ''])
    for condition in ['zero_shot', 'five_shot']:
        rows = read_jsonl(root / f'{condition}.jsonl')
        lines.append(f"- {condition}: {len(rows)} yanıt; token sınırına ulaşan {sum(r['reached_token_limit'] for r in rows)}; toplam üretim süresi {sum(r['seconds'] for r in rows):.1f} saniye.")
    lines.extend(['', 'Bu karşılaştırma tek bir sabit beş örnekli istemin katkısını ölçer; en iyi istem araması değildir. '
                  'Doğrulama kümesi geliştirme için kullanılabilir, nihai test sonucu sayılmaz. '
                  'Bu kümede belirsiz kelime/minimal çift etiketleri bulunmadığından bu metrikler raporlanmaz.', '',
                  'Veri kaynağı: UD Turkish BOUN r2.16; örnek metinler CC BY-SA 4.0 lisanslıdır. '
                  'Kaynak ve lisans kaydı: `data/prepared/boun-v1/source/`.', '',
                  'Ham yanıtlar `zero_shot.jsonl` ve `five_shot.jsonl`; örnek bazındaki puanlar '
                  '`*-scores.json`; özet ve güven aralıkları `comparison.json`; sürümler ve dosya '
                  'SHA-256 özetleri `metadata.json` içinde saklanır.', '',
                  'Yeniden çalıştırma (yeni çıktı klasörü gerekir):', '', '```bash',
                  '.venv/bin/python -m scripts.compare_prompts --output reports/validation-prompts/boun-v1-rerun',
                  '.venv/bin/python -m scripts.report_prompt_comparison reports/validation-prompts/boun-v1-rerun', '```', ''])
    (root / 'README.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
