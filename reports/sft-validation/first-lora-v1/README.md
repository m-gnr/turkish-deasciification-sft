# İlk LoRA: doğrulama sonuçları

900 doğrulama örneği; test kümesi değerlendirilmedi.

| İstem | Metrik | Eğitim öncesi | Eğitim sonrası |
| --- | --- | ---: | ---: |
| zero_shot | strict_compliance | 73.67% | 65.56% |
| zero_shot | sentence_exact | 16.89% | 43.78% |
| zero_shot | candidate_accuracy | 50.56% | 48.49% |
| zero_shot | required_correction | 10.73% | 38.10% |
| five_shot | strict_compliance | 50.33% | 65.89% |
| five_shot | sentence_exact | 20.78% | 43.33% |
| five_shot | candidate_accuracy | 33.48% | 50.48% |
| five_shot | required_correction | 17.60% | 41.05% |

Farkların %95 eşleştirilmiş bootstrap aralıkları comparison.json içindedir.
Bu ilk eğitim koşusudur; nihai testten önce model/istem seçimi sabitlenmelidir.
