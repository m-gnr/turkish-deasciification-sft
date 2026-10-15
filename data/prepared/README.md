# Hazırlanmış veri kümeleri

Her klasör bir veri sürümüdür. Mevcut sürüm: [`boun-v1`](boun-v1/manifest.json).

```text
prepared/
├── README.md
└── boun-v1/
    ├── manifest.json
    ├── splits/
    │   ├── train.jsonl
    │   ├── validation.jsonl
    │   └── test.jsonl
    ├── metadata/
    │   ├── sources.jsonl
    │   └── excluded.jsonl
    └── source/
        ├── README.md
        └── LICENSE.txt
```

| Konum | Kullanım |
| --- | --- |
| `splits/` | Eğitim, doğrulama ve test örnekleri. Modele yalnız `input` ve `target` metinlerini verin. |
| `metadata/sources.jsonl` | Kota dışında kalanlar dahil temiz kaynakların bölüm atamaları. Baseline sözlükleri için yalnız eğitim bölümünü kullanın. |
| `metadata/excluded.jsonl` | Elenen kaynaklar ve elenme nedenleri. |
| `source/` | Kaynağın özgün açıklaması, atıfları ve CC BY-SA 4.0 lisansı. |
| `manifest.json` | Kaynak sürümü, üretim kuralları, sayımlar ve göreli dosya yollarıyla SHA-256 özetleri. |

Denetim komutuna sürüm klasörünü verin:

```bash
python3 -m scripts.audit_data data/prepared/boun-v1
```

Üretilen dosyaları elle düzenlemeyin. Yeni üretim için farklı bir sürüm klasörü
kullanın. Hazırlama adımları ve veri sınırlılıkları için
[veri hazırlama rehberine](../../docs/data/README.md) bakın.
