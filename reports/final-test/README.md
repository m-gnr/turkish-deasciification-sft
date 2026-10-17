# Nihai test: dondurulmuş sistem

900 test örneği; 7.340 eğitim ve 900 doğrulama örneğiyle birebir/NFC/normalize girdi-hedef çakışması ve kaynak/pair kimliği çakışması 0. Normalize kontrol Türkçe küçük harf, diakritik katlama ve `\W+` çıkarımıdır; semantik yakın kopya taraması değildir.

Sistem: Qwen/Qwen3-1.7B + first-lora-v1 (`runs/first-sft-v1/training/adapter`), zero-shot, greedy (`do_sample=False`), batch=8, max_new_tokens=256, MPS/float16, seed=0; parçalama yok. Tek-parça ham çıktıya mevcut `repair` uygulanır. Commit: `596d47dc70632c5b59f271b2d38712377fd66321`. Dondurma öncesi çalışma ağacı temizdi; sonradan yalnız bu rapor dizini oluşturuldu.

Kullanıcı onayıyla temel model ve SFT için birer test geçişi yapıldı. Identity üretim gerektirmez; fallback ve repair aynı ham SFT çıktısını kullanır. Fallback, kural ihlalinde girdiyi döndürür; repair hedefe bakmadan izinli dönüşümleri hizalamadan aktarır. Eğitim, ayar değişikliği veya test sonucuna göre seçim yapılmadı.

Hücreler değer [%95 GA] biçiminde; ilk dört metrik yüzde, U gereksiz dönüşüm karakter sayısı, W yanlış değiştirilmiş sözcük sayısıdır. Mevcut puanlayıcı ve kaynak/pair bağlantılı küme percentile bootstrap: 10.000 tekrar, seed=42. U/W aralıkları yeniden örneklenen küme toplamlarının aralıklarıdır. Doğrulama çıktıları yeniden üretilmedi.

| Sistem | Metrik | Doğrulama | Test |
|---|---|---:|---:|
| Identity | Uyum (%) | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| Identity | Tam eşleşme (%) | 15.00 [12.67, 17.33] | 15.00 [12.67, 17.44] |
| Identity | Aday doğruluğu (%) | 69.59 [68.42, 70.81] | 70.31 [69.12, 71.52] |
| Identity | Gerekli düzeltme (%) | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Identity | U | 0 [0.0, 0.0] | 0 [0.0, 0.0] |
| Identity | W | 0 [0.0, 0.0] | 0 [0.0, 0.0] |
| Eğitim öncesi zero-shot | Uyum (%) | 73.67 [70.78, 76.56] | 72.22 [69.33, 75.11] |
| Eğitim öncesi zero-shot | Tam eşleşme (%) | 16.89 [14.44, 19.33] | 17.67 [15.22, 20.11] |
| Eğitim öncesi zero-shot | Aday doğruluğu (%) | 50.56 [47.43, 53.73] | 50.13 [46.88, 53.42] |
| Eğitim öncesi zero-shot | Gerekli düzeltme (%) | 10.73 [9.13, 12.51] | 10.70 [9.01, 12.51] |
| Eğitim öncesi zero-shot | U | 3 [0.0, 7.0] | 7 [1.0, 14.0] |
| Eğitim öncesi zero-shot | W | 121 [94.0, 152.0] | 152 [102.0, 218.0] |
| Ham SFT | Uyum (%) | 65.56 [62.44, 68.56] | 65.44 [62.33, 68.44] |
| Ham SFT | Tam eşleşme (%) | 43.78 [40.56, 47.00] | 48.89 [45.67, 52.11] |
| Ham SFT | Aday doğruluğu (%) | 48.49 [44.53, 52.46] | 49.69 [45.73, 53.77] |
| Ham SFT | Gerekli düzeltme (%) | 38.10 [34.16, 42.30] | 39.63 [35.63, 43.84] |
| Ham SFT | U | 124 [93.0, 158.0] | 73 [53.0, 94.0] |
| Ham SFT | W | 241 [199.0, 287.0] | 230 [174.0, 293.0] |
| SFT+fallback | Uyum (%) | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| SFT+fallback | Tam eşleşme (%) | 44.56 [41.33, 47.78] | 49.22 [46.00, 52.44] |
| SFT+fallback | Aday doğruluğu (%) | 80.67 [79.17, 82.21] | 81.84 [80.39, 83.32] |
| SFT+fallback | Gerekli düzeltme (%) | 38.10 [34.16, 42.30] | 39.63 [35.63, 43.84] |
| SFT+fallback | U | 88 [63.0, 115.0] | 42 [28.0, 57.0] |
| SFT+fallback | W | 110 [88.0, 132.0] | 70 [54.0, 88.0] |
| SFT+repair | Uyum (%) | 100.00 [100.00, 100.00] | 100.00 [100.00, 100.00] |
| SFT+repair | Tam eşleşme (%) | 55.56 [52.33, 58.78] | 60.44 [57.33, 63.67] |
| SFT+repair | Aday doğruluğu (%) | 94.93 [94.47, 95.37] | 95.66 [95.23, 96.07] |
| SFT+repair | Gerekli düzeltme (%) | 87.20 [86.04, 88.29] | 88.52 [87.40, 89.61] |
| SFT+repair | U | 203 [166.0, 243.0] | 161 [130.0, 193.0] |
| SFT+repair | W | 301 [264.0, 338.0] | 264 [229.0, 301.0] |

## Doğrulama–test farkı

| Sistem | Uyum (yp) | Tam eşleşme (yp) | Aday (yp) | Gerekli (yp) |
|---|---:|---:|---:|---:|
| Identity | +0.00 | +0.00 | +0.72 | +0.00 |
| Eğitim öncesi zero-shot | -1.44 | +0.78 | -0.43 | -0.03 |
| Ham SFT | -0.11 | +5.11 | +1.21 | +1.53 |
| SFT+fallback | +0.00 | +4.67 | +1.17 | +1.53 |
| SFT+repair | +0.00 | +4.89 | +0.73 | +1.32 |

Farklar test−doğrulama betimsel farklarıdır; iki küme eşleştirilmiş değildir. Test içindeki repair−karşılaştırıcı eşleştirilmiş GA’lar `test-bootstrap.json` içindedir.

SFT+repair testte 544/900 tam doğru çıktı verdi (%60,44; %95 GA: %57,33–63,67). Doğrulamaya göre tam eşleşme +4,89 yüzde puan; gerekli düzeltme +1,32 yüzde puandır. Testte fallback’e göre tam eşleşme +11,22 yüzde puan ve gerekli düzeltme +48,89 yüzde puan artarken U 42→161, W 70→264 oldu: daha fazla düzeltme, daha fazla yanlış müdahaleyle birlikte geldi. Bu gözlem sistem seçimini değiştirmek için kullanılmadı.

## Sınırlılıklar ve iddia sınırı

- Uyum, dilsel doğruluk garantisi değildir. Mevcut puanlayıcı kural ihlalinde birincil karakter/sözcük başarı paylarını sıfırlar. Aday doğruluğu, korunması gereken konumları da içerir.
- U ve W yalnız eşit uzunluklu çıktılarda sayılır; farklı uzunlukta 0 yazılması hatasızlık değildir. Ham sistemlerle son işlemli sistemlerin U/W toplamları bu yüzden doğrudan hata üstünlüğü göstermez.
- Bootstrap aralıkları bu örneklemdeki belirsizliği gösterir; eğitim tohumu, model seçimi veya alan değişimini kapsamaz. Doğrulama sistem seçiminde kullanılmıştır. Test artık bağımsız yeni seçimler için kullanılmamalıdır.
- Ne iddia edebiliriz: Önceden sabitlenen sistemin bu ayrılmış BOUN testindeki başarısı ve aynı örneklerdeki karşılaştırıcı farkları ölçülmüştür. Repair için elde edilen uyum ve doğruluk ayrı ölçütlerdir.
- Ne iddia edemeyiz: Her Türkçe metinde aynı başarı, tüm hataların düzelmesi, bütün veri sızıntısı türlerinin yokluğu, başka modellerden üstünlük veya tekrar eğitimlerde aynı sonuç garantisi.

## Kayıtlar

`freeze-manifest.json` değişmeden korunan üretim öncesi anlık kayıttır; içindeki bekleyen onay durumu tarihseldir. Gerçek koşu durumu `generation-status.json`, başlangıç kilidi `generation-started.json`, son bütünlük denetimi `verification.json` içindedir. Ham çıktılar `pre_zero_shot.jsonl` ve `sft_zero_shot.jsonl`; beş sistemin tüm çıktıları ve skorları `test-*-scores.json`; sayısal tablolar `metrics.csv` ve `comparison.json` içindedir.
Ölçülen üretim süresi: temel model 15.01 dakika, SFT 15.83 dakika; toplam 30.84 dakika (model yükleme/puanlama hariç). Altyapı tekrarı: 0.
