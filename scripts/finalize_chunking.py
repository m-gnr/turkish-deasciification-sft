"""Add offline diagnostic interpretation to the frozen chunking report; no new systems."""
from collections import Counter
import json
import re

from scripts.compare_prompts import digest, save
from scripts.run_chunking import OUT, assert_hashes


def regression_kind(target, output):
    if target == output:
        return 'exact'
    if re.sub(r'\s+', '', target) == re.sub(r'\s+', '', output):
        return 'whitespace_only'
    return 'content_changed'


def select_examples(rows, maximum=10):
    """Show content changes as well as separator failures; deterministic, unique."""
    changed = [r for r in rows if r['diagnostic_kind'] == 'content_changed']
    spaces = [r for r in rows if r['diagnostic_kind'] == 'whitespace_only']
    selected = changed[:maximum//2] + spaces[:maximum//2]
    seen = {r['id'] for r in selected}
    selected += [r for r in rows if r['id'] not in seen][:maximum-len(selected)]
    return selected


def main():
    manifest = json.loads((OUT/'manifest.json').read_text())
    if manifest['status'] != 'complete':
        raise ValueError('Complete both frozen settings before interpretation')
    assert_hashes(manifest['protected_sha256'])
    metrics = json.loads((OUT/'metrics.json').read_text())
    paired = json.loads((OUT/'paired.json').read_text())
    decisions = json.loads((OUT/'decision.json').read_text())
    boundaries = json.loads((OUT/'boundary-summary.json').read_text())
    regressions = json.loads((OUT/'regressions.json').read_text())
    costs = json.loads((OUT/'costs.json').read_text())
    review, summaries = {}, {}
    for limit, rows in regressions.items():
        review[limit] = [dict(r, diagnostic_kind=regression_kind(r['target'],r['chunk_output'])) for r in rows]
        summaries[limit] = dict(Counter(r['diagnostic_kind'] for r in review[limit]))
    save(OUT/'regression-review.json', {'counts':summaries,'rows':review,
        'definition':'Remove whitespace only to classify differences, never to create/rescore a system.',
        'causal_limit':'Content changes may be consistent with context loss, but do not prove that mechanism.'})
    summary = ['## Özet ve yorum', '',
        'Önceden sabitlenen iki ayar da **işe yaramadı**. Ham uyum ve tam eşleşme düştü; '
        'bu sonuç bu ayarlar ve ham birleştirme sistemi içindir, her tür parçalamanın olanaksız olduğu anlamına gelmez.', '',
        '| Ham sistem | Uyum | Tam eşleşme | İhlal |', '|---|---:|---:|---:|']
    for name in ('sft_zero_shot','sft_zero_shot_chunk120','sft_zero_shot_chunk80'):
        v=metrics[name]['all']
        summary.append(f"| {name} | {v['metrics']['strict_compliance']['rate']:.2%} | {v['metrics']['sentence_exact']['rate']:.2%} | {v['errors']['rule_violation']} |")
    for limit in ('120','80'):
        v=paired[limit]['metrics']; b=boundaries[limit]; s=summaries[limit]
        summary += ['', f"**{limit}:** uyum farkı {v['strict_compliance']['difference']*100:+.2f} yüzde puan "
            f"(%95 GA {v['strict_compliance']['ci95'][0]*100:.2f}…{v['strict_compliance']['ci95'][1]*100:.2f}); "
            f"tam eşleşme farkı {v['sentence_exact']['difference']*100:+.2f} yüzde puan "
            f"(%95 GA {v['sentence_exact']['ci95'][0]*100:.2f}…{v['sentence_exact']['ci95'][1]*100:.2f}). "
            f"{b['boundaries']} sınırın {b['trailing_whitespace_changed']} tanesinde sol parçanın son boşluğu değişmiş. "
            f"Önceden uyumlu olup yeni ihlal üreten {v['strict_compliance']['before_only']} cümlenin "
            f"{b['previously_compliant_new_violation_with_boundary_symptom']} tanesinde sınır belirtisi var. "
            f"Tam doğrudan yanlışa dönen {len(review[limit])} örneğin {s.get('whitespace_only',0)} tanesi yalnız whitespace farkı; "
            f"{s.get('content_changed',0)} tanesinde başka içerik değişimi de var."]
    summary += ['', 'Boşluklar bölme sırasında kaybolmadı: 1.800 bayt-eşitlik kontrolü geçti. '
        'Kayıp modelin parça çıktısında görülüyor; ham birleştirme bu çıktıları aynen yan yana koyuyor. '
        'Boşluk farkını çıkarma yalnız tanısal sınıflandırmadır; yeni bir son işlem sistemi olarak puanlanmadı. '
        'Bağlam kaybı hipotezi, sınır boşluğu kaybı ve diğer üretim etkilerinden bu deneyle tek başına ayrıştırılamaz.', '',
        'Repair karşılaştırması da parçalamaya açık bir üstünlük göstermedi: tek parça 500/900 (%55,56) tam doğru; '
        '120+repair 495/900 (%55,00), 80+repair 491/900 (%54,56). '
        'Gereksiz dönüşüm U: 203→219/215; yanlış değişen sözcük W: 301→306/320. '
        'Repair sistemlerinin tümü uyumlu olduğundan bu U/W karşılaştırması uzunluk kaynaklı eksik sayımdan etkilenmiyor. '
        'Bu küçük repair farklarına ayrıca anlamlılık iddiası eklenmedi.', '',
        f"Kalibrasyon ve devam dahil 1.298 yeni parçanın üretimi {costs['total_generation_seconds']/60:.2f} dk, "
        f"model yükleme dahil çalıştırma süresi {costs['total_run_wall_seconds']/60:.2f} dk. "
        'Önceki çıktıların yeniden kullanıldığı bu ek maliyet, yeni 900 girdinin sıfırdan işlenme maliyeti değildir; '
        'aşağıdaki soğuk çalışma tahmini bunu ayrıca gösterir.', '',
        '**Önerilen sonraki adım:** bu iki ham parçalama ayarını mevcut hâliyle ilerletmemek; '
        'tek-parça repair/fallback arasındaki düzeltme–yanlış müdahale ödünleşimini seçim kuralıyla değerlendirmek. '
        'Hipoteze devam edilecekse sınır boşluklarını modelden bağımsız koruyan ayrı bir sistem önceden tanımlanabilir; '
        'bu raporda uygulanmadı veya puanlanmadı. Yeni ayar için ayrı kullanıcı onayı gerekir. Nihai sistem seçimi yapılmadı.', '']
    if any(d['worked_under_frozen_rule'] for d in decisions.values()):
        raise ValueError('Interpretation is specific to the observed failed experiment')
    section=['## Tek parçada doğru, parçalıda yanlış örnekler', '',
        'Her ayardan en fazla 10 örnek: veri sırasındaki ilk 5 içerik değişimi ve ilk 5 yalnız whitespace farkı; '
        'havuz yetersizse kalan örnekler veri sırasından tamamlanır. Rastgele seçim yok. '
        'Tüm 38/90 regresyon `regression-review.json` içinde. İçerik değişimi bağlam kaybını kanıtlamaz.', '']
    for limit, rows in review.items():
        section += [f'### {limit}: {len(rows)} regresyon', '']
        for r in select_examples(rows):
            section += [f"#### {r['id']}", '', f"Tanı: `{r['diagnostic_kind']}`; bölme konumları: {r['boundaries']}", '',
                '```text','Girdi: '+r['input'],'Hedef: '+r['target'],'Tek parça: '+r['single_output'],'Parçalı: '+r['chunk_output'],'```', '',
                'Hedef → çıktı farkı:', '```json',json.dumps(r['diff'],ensure_ascii=False),'```','']
    path=OUT/'README.md'
    text=path.read_text()
    if '## Özet ve yorum' in text:
        start=text.index('## Özet ve yorum')
        end=text.index('## Sabit karar kuralı')
        text=text[:start]+text[end:]
    text=text.replace('## Sabit karar kuralı','\n'.join(summary)+'\n## Sabit karar kuralı',1)
    start=text.index('## Tek parçada doğru, parçalıda yanlış örnekler')
    end=text.index('## Sınırlar ve devam',start)
    text=text[:start]+'\n'.join(section)+'\n'+text[end:]
    text += '\nYorum/örnek incelemesi yeniden üretimi: `.venv/bin/python -m scripts.run_chunking report` ardından `.venv/bin/python -m scripts.finalize_chunking`.\n'
    path.write_text(text)
    assert_hashes(manifest['protected_sha256'])
    manifest['interpretation_script_sha256']=digest(__import__('pathlib').Path(__file__))
    manifest['output_sha256']={p.name:digest(p) for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json'}
    save(OUT/'manifest.json',manifest)


if __name__=='__main__':
    main()
