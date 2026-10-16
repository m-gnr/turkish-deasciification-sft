# İlk LoRA: sabit chunking deneyi

900 doğrulama cümlesi, yalnız zero-shot; yeniden eğitim ve test kümesi erişimi yok. Sabit A=120/B=80 karakter, seed=42, batch=8, greedy, max_new_tokens=256, thinking kapalı. Mevcut şablon, durdurma ve puanlayıcı aynen kullanıldı. Ayarlar sonuçlardan sonra değiştirilmedi.

## Özet ve yorum

Önceden sabitlenen iki ayar da **işe yaramadı**. Ham uyum ve tam eşleşme düştü; bu sonuç bu ayarlar ve ham birleştirme sistemi içindir, her tür parçalamanın olanaksız olduğu anlamına gelmez.

| Ham sistem | Uyum | Tam eşleşme | İhlal |
|---|---:|---:|---:|
| sft_zero_shot | 65.56% | 43.78% | 310 |
| sft_zero_shot_chunk120 | 58.33% | 39.56% | 375 |
| sft_zero_shot_chunk80 | 49.11% | 34.00% | 458 |

**120:** uyum farkı -7.22 yüzde puan (%95 GA -8.89…-5.56); tam eşleşme farkı -4.22 yüzde puan (%95 GA -5.56…-2.89). 230 sınırın 205 tanesinde sol parçanın son boşluğu değişmiş. Önceden uyumlu olup yeni ihlal üreten 65 cümlenin 65 tanesinde sınır belirtisi var. Tam doğrudan yanlışa dönen 38 örneğin 30 tanesi yalnız whitespace farkı; 8 tanesinde başka içerik değişimi de var.

**80:** uyum farkı -16.44 yüzde puan (%95 GA -18.89…-13.89); tam eşleşme farkı -9.78 yüzde puan (%95 GA -11.78…-7.78). 555 sınırın 473 tanesinde sol parçanın son boşluğu değişmiş. Önceden uyumlu olup yeni ihlal üreten 152 cümlenin 148 tanesinde sınır belirtisi var. Tam doğrudan yanlışa dönen 90 örneğin 71 tanesi yalnız whitespace farkı; 19 tanesinde başka içerik değişimi de var.

Boşluklar bölme sırasında kaybolmadı: 1.800 bayt-eşitlik kontrolü geçti. Kayıp modelin parça çıktısında görülüyor; ham birleştirme bu çıktıları aynen yan yana koyuyor. Boşluk farkını çıkarma yalnız tanısal sınıflandırmadır; yeni bir son işlem sistemi olarak puanlanmadı. Bağlam kaybı hipotezi, sınır boşluğu kaybı ve diğer üretim etkilerinden bu deneyle tek başına ayrıştırılamaz.

Repair karşılaştırması da parçalamaya açık bir üstünlük göstermedi: tek parça 500/900 (%55,56) tam doğru; 120+repair 495/900 (%55,00), 80+repair 491/900 (%54,56). Gereksiz dönüşüm U: 203→219/215; yanlış değişen sözcük W: 301→306/320. Repair sistemlerinin tümü uyumlu olduğundan bu U/W karşılaştırması uzunluk kaynaklı eksik sayımdan etkilenmiyor. Bu küçük repair farklarına ayrıca anlamlılık iddiası eklenmedi.

Kalibrasyon ve devam dahil 1.298 yeni parçanın üretimi 12.68 dk, model yükleme dahil çalıştırma süresi 13.04 dk. Önceki çıktıların yeniden kullanıldığı bu ek maliyet, yeni 900 girdinin sıfırdan işlenme maliyeti değildir; aşağıdaki soğuk çalışma tahmini bunu ayrıca gösterir.

**Önerilen sonraki adım:** bu iki ham parçalama ayarını mevcut hâliyle ilerletmemek; tek-parça repair/fallback arasındaki düzeltme–yanlış müdahale ödünleşimini seçim kuralıyla değerlendirmek. Hipoteze devam edilecekse sınır boşluklarını modelden bağımsız koruyan ayrı bir sistem önceden tanımlanabilir; bu raporda uygulanmadı veya puanlanmadı. Yeni ayar için ayrı kullanıcı onayı gerekir. Nihai sistem seçimi yapılmadı.

## Sabit karar kuralı

Uyum farkının %95 bootstrap alt sınırı >0; tam eşleşme farkının alt sınırı >−2 yüzde puan; 31+ aday ve 121+ karakter dilimlerinde uyum nokta farkları >0. 10.000 kaynak/pair kümeli tekrar, seed=42. Bu sonuç nihai sistem seçimi değildir. İki ayarın sınanması ve tek doğrulama kümesi seçim yanlılığı riski taşır; test açılmadı.

- **120: İŞE YARAMADI (sabit kural karşılanmadı)**; kontroller: {'compliance_ci_low_positive': False, 'exact_noninferiority_2pp': False, 'candidate31_compliance_increased': False, 'length121_compliance_increased': False}.
- **80: İŞE YARAMADI (sabit kural karşılanmadı)**; kontroller: {'compliance_ci_low_positive': False, 'exact_noninferiority_2pp': False, 'candidate31_compliance_increased': False, 'length121_compliance_increased': False}.

## Sistem metrikleri

U/W mevcut puanlayıcının gereksiz dönüşüm/yanlış değişen sözcük sayılarıdır; uzunluğu farklı çıktılarda sayılmadığı için ham sistemler arasında eksik sayım vardır. Koşullu metrikler farklı uyumlu alt kümeleri karşılaştırır. Repair/fallback ayrı sistemlerdir; ham model başarısı olarak sunulmaz.

| Sistem | Uyum | Tam | Aday | Gerekli | Uyumlu: tam | Uyumlu: aday | Uyumlu: gerekli | U | W | Unalignable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sft_zero_shot | 65.56% | 43.78% | 48.49% | 38.10% | 66.78% | 96.01% | 88.51% | 124 | 241 | 237 |
| sft_zero_shot_chunk120 | 58.33% | 39.56% | 36.14% | 29.28% | 67.81% | 95.67% | 87.84% | 97 | 337 | 306 |
| sft_zero_shot_chunk80 | 49.11% | 34.00% | 25.48% | 20.47% | 69.23% | 95.29% | 86.43% | 68 | 275 | 400 |
| sft_zero_shot_repair | 100.00% | 55.56% | 94.93% | 87.20% | 55.56% | 94.93% | 87.20% | 203 | 301 | 0 |
| sft_zero_shot_fallback | 100.00% | 44.56% | 80.67% | 38.10% | 44.56% | 80.67% | 38.10% | 88 | 110 | 0 |
| sft_zero_shot_chunk120_repair | 100.00% | 55.00% | 94.90% | 87.39% | 55.00% | 94.90% | 87.39% | 219 | 306 | 0 |
| sft_zero_shot_chunk120_fallback | 100.00% | 42.44% | 78.09% | 29.28% | 42.44% | 78.09% | 29.28% | 70 | 85 | 0 |
| sft_zero_shot_chunk80_repair | 100.00% | 54.56% | 94.83% | 87.08% | 54.56% | 94.83% | 87.08% | 215 | 320 | 0 |
| sft_zero_shot_chunk80_fallback | 100.00% | 38.56% | 75.53% | 20.47% | 38.56% | 75.53% | 20.47% | 49 | 63 | 0 |

## Parçalar ve sınırlar

Ham parçalar ayraç eklenmeden birleştirildi; çıktı boşlukları düzeltilmedi. Sınır içindeki cümlelerde eski çıktı kullanıldı; aday içermeyen yeni parçalar kopyalandı. Bölme/birleştirme ham bayt eşitliği ve sözcük/uzunluk kontrolleri tüm 900×2 girdide geçti. Tek aşırı uzun sözcük istisnaları plan içinde işaretlidir. Sınır belirtileri nedensel kanıt değildir.

| Ayar | Bölünen cümle | Eski çıktı | Toplam parça | Yeni üretim | Kopya | Uzun sözcük istisnası |
|---|---:|---:|---:|---:|---:|---:|
| 120 | 177 | 723 | 1130 | 403 | 4 | 0 |
| 80 | 350 | 550 | 1455 | 895 | 10 | 0 |

| Ayar / parça grubu | n | İhlal | İhlal oranı |
|---|---:|---:|---:|
| 120/mode:reuse | 723 | 204 | 28.22% |
| 120/mode:generate | 403 | 269 | 66.75% |
| 120/new_length:81-120 | 206 | 162 | 78.64% |
| 120/new_length:41-80 | 132 | 80 | 60.61% |
| 120/new_length:1-40 | 69 | 27 | 39.13% |
| 120/mode:copy | 4 | 0 | 0.00% |
| 80/mode:reuse | 550 | 126 | 22.91% |
| 80/mode:generate | 895 | 576 | 64.36% |
| 80/new_length:41-80 | 639 | 447 | 69.95% |
| 80/new_length:1-40 | 266 | 129 | 48.50% |
| 80/mode:copy | 10 | 0 | 0.00% |

120 sınır tanısı: {'boundaries': 230, 'trailing_whitespace_changed': 205, 'leading_whitespace_changed': 0, 'terminal_punctuation_changed': 0, 'sentences_with_boundary_symptom': 163, 'previously_compliant_new_violation_with_boundary_symptom': 65}.

80 sınır tanısı: {'boundaries': 555, 'trailing_whitespace_changed': 473, 'leading_whitespace_changed': 0, 'terminal_punctuation_changed': 2, 'sentences_with_boundary_symptom': 313, 'previously_compliant_new_violation_with_boundary_symptom': 148}.

## İhlal kategorileri

Mevcut hata analizi sınıflandırıcısı ve öncelik sırası aynen kullanıldı. Kategoriler birbirini dışlar; sınır belirtileri ayrıca örtüşebilir.

| Kategori | Tek parça | 120 | 80 |
|---|---:|---:|---:|
| Boş çıktı | 0 | 0 | 0 |
| Ek biçim/açıklama belirtisi | 0 | 0 | 0 |
| EOS olmadan token sınırı | 0 | 0 | 0 |
| Girdinin eksik öneki (erken bitiş belirtisi) | 0 | 0 | 0 |
| Tam sözcük silme | 0 | 0 | 0 |
| Tam sözcük tekrarı | 0 | 0 | 0 |
| Tam sözcük ekleme | 0 | 0 | 0 |
| Yalnız harf büyüklüğü ihlali | 4 | 3 | 3 |
| Yalnız boşluk/noktalama ihlali | 4 | 68 | 148 |
| Diğer kısa çıktı / sözcük içi yeniden yazım | 122 | 142 | 178 |
| Diğer uzun çıktı / sözcük içi yeniden yazım | 111 | 96 | 74 |
| Eşit uzunlukta izin verilmeyen harf değişimi | 68 | 66 | 55 |
| Diğer eşit uzunluklu karma ihlal | 1 | 0 | 0 |

## Eşleştirilmiş geçişler

Fark=parçalı−tek parça; GA yüzde puan. Exact McNemar cümle bağımsızlığı varsayar; kaynak bağımlılığını bootstrap korur.

| Ayar / metrik | İkisi evet | Yalnız önce | Yalnız sonra | İkisi hayır | Fark yp | %95 GA yp | McNemar p |
|---|---:|---:|---:|---:|---:|---:|---:|
| 120/strict_compliance | 525 | 65 | 0 | 310 | -7.22 | [-8.89, -5.56] | 5.421e-20 |
| 120/sentence_exact | 356 | 38 | 0 | 506 | -4.22 | [-5.56, -2.89] | 7.276e-12 |
| 80/strict_compliance | 438 | 152 | 4 | 306 | -16.44 | [-18.89, -13.89] | 5.336e-40 |
| 80/sentence_exact | 304 | 90 | 2 | 504 | -9.78 | [-11.78, -7.78] | 1.728e-24 |

## Dilimler

| Sistem / dilim | n | Uyum | Tam | Aday | Gerekli |
|---|---:|---:|---:|---:|---:|
| sft_zero_shot/candidates31+ | 152 | 32.89% | 14.47% | 27.82% | 21.56% |
| sft_zero_shot/candidates21-30 | 168 | 53.57% | 30.95% | 50.83% | 41.18% |
| sft_zero_shot/length121+ | 177 | 40.11% | 23.16% | 31.75% | 21.81% |
| sft_zero_shot/length81-120 | 173 | 54.91% | 31.79% | 51.47% | 43.31% |
| sft_zero_shot/needs_correction | 765 | 60.39% | 35.03% | 43.99% | 38.10% |
| sft_zero_shot/preservation | 135 | 94.81% | 93.33% | 93.34% | — |
| sft_zero_shot_chunk120/candidates31+ | 152 | 7.89% | 2.63% | 5.68% | 4.73% |
| sft_zero_shot_chunk120/candidates21-30 | 168 | 40.48% | 21.43% | 37.83% | 34.14% |
| sft_zero_shot_chunk120/length121+ | 177 | 3.39% | 1.69% | 2.28% | 1.07% |
| sft_zero_shot_chunk120/length81-120 | 173 | 54.91% | 31.79% | 51.47% | 43.31% |
| sft_zero_shot_chunk120/needs_correction | 765 | 54.38% | 32.42% | 33.55% | 29.28% |
| sft_zero_shot_chunk120/preservation | 135 | 80.74% | 80.00% | 61.93% | — |
| sft_zero_shot_chunk80/candidates31+ | 152 | 1.97% | 0.66% | 1.38% | 0.76% |
| sft_zero_shot_chunk80/candidates21-30 | 168 | 14.88% | 7.74% | 13.64% | 11.57% |
| sft_zero_shot_chunk80/length121+ | 177 | 3.95% | 1.69% | 2.75% | 1.61% |
| sft_zero_shot_chunk80/length81-120 | 173 | 6.36% | 2.89% | 5.79% | 4.79% |
| sft_zero_shot_chunk80/needs_correction | 765 | 45.49% | 27.84% | 23.64% | 20.47% |
| sft_zero_shot_chunk80/preservation | 135 | 69.63% | 68.89% | 43.91% | — |
| sft_zero_shot_repair/candidates31+ | 152 | 100.00% | 27.63% | 94.70% | 86.83% |
| sft_zero_shot_repair/candidates21-30 | 168 | 100.00% | 47.62% | 95.75% | 89.56% |
| sft_zero_shot_repair/length121+ | 177 | 100.00% | 36.16% | 95.06% | 86.72% |
| sft_zero_shot_repair/length81-120 | 173 | 100.00% | 47.98% | 95.69% | 90.02% |
| sft_zero_shot_repair/needs_correction | 765 | 100.00% | 48.37% | 94.49% | 87.20% |
| sft_zero_shot_repair/preservation | 135 | 100.00% | 96.30% | 99.37% | — |
| sft_zero_shot_fallback/candidates31+ | 152 | 100.00% | 14.47% | 73.78% | 21.56% |
| sft_zero_shot_fallback/candidates21-30 | 168 | 100.00% | 32.14% | 82.34% | 41.18% |
| sft_zero_shot_fallback/length121+ | 177 | 100.00% | 24.29% | 75.59% | 21.81% |
| sft_zero_shot_fallback/length81-120 | 173 | 100.00% | 33.53% | 82.37% | 43.31% |
| sft_zero_shot_fallback/needs_correction | 765 | 100.00% | 35.03% | 78.74% | 38.10% |
| sft_zero_shot_fallback/preservation | 135 | 100.00% | 98.52% | 99.87% | — |
| sft_zero_shot_chunk120_repair/candidates31+ | 152 | 100.00% | 25.00% | 94.67% | 87.46% |
| sft_zero_shot_chunk120_repair/candidates21-30 | 168 | 100.00% | 47.02% | 95.65% | 89.24% |
| sft_zero_shot_chunk120_repair/length121+ | 177 | 100.00% | 33.33% | 94.98% | 87.17% |
| sft_zero_shot_chunk120_repair/length81-120 | 173 | 100.00% | 47.98% | 95.69% | 90.02% |
| sft_zero_shot_chunk120_repair/needs_correction | 765 | 100.00% | 47.71% | 94.45% | 87.39% |
| sft_zero_shot_chunk120_repair/preservation | 135 | 100.00% | 96.30% | 99.37% | — |
| sft_zero_shot_chunk120_fallback/candidates31+ | 152 | 100.00% | 5.92% | 68.46% | 4.73% |
| sft_zero_shot_chunk120_fallback/candidates21-30 | 168 | 100.00% | 27.98% | 80.32% | 34.14% |
| sft_zero_shot_chunk120_fallback/length121+ | 177 | 100.00% | 13.56% | 69.44% | 1.07% |
| sft_zero_shot_chunk120_fallback/length81-120 | 173 | 100.00% | 33.53% | 82.37% | 43.31% |
| sft_zero_shot_chunk120_fallback/needs_correction | 765 | 100.00% | 32.42% | 75.90% | 29.28% |
| sft_zero_shot_chunk120_fallback/preservation | 135 | 100.00% | 99.26% | 99.94% | — |
| sft_zero_shot_chunk80_repair/candidates31+ | 152 | 100.00% | 23.68% | 94.54% | 87.10% |
| sft_zero_shot_chunk80_repair/candidates21-30 | 168 | 100.00% | 48.21% | 95.70% | 89.00% |
| sft_zero_shot_chunk80_repair/length121+ | 177 | 100.00% | 32.20% | 94.98% | 87.22% |
| sft_zero_shot_chunk80_repair/length81-120 | 173 | 100.00% | 46.82% | 95.40% | 88.65% |
| sft_zero_shot_chunk80_repair/needs_correction | 765 | 100.00% | 47.19% | 94.37% | 87.08% |
| sft_zero_shot_chunk80_repair/preservation | 135 | 100.00% | 96.30% | 99.37% | — |
| sft_zero_shot_chunk80_fallback/candidates31+ | 152 | 100.00% | 4.61% | 67.29% | 0.76% |
| sft_zero_shot_chunk80_fallback/candidates21-30 | 168 | 100.00% | 16.07% | 73.84% | 11.57% |
| sft_zero_shot_chunk80_fallback/length121+ | 177 | 100.00% | 15.25% | 69.60% | 1.61% |
| sft_zero_shot_chunk80_fallback/length81-120 | 173 | 100.00% | 11.56% | 71.32% | 4.79% |
| sft_zero_shot_chunk80_fallback/needs_correction | 765 | 100.00% | 27.84% | 73.09% | 20.47% |
| sft_zero_shot_chunk80_fallback/preservation | 135 | 100.00% | 99.26% | 99.94% | — |

## Maliyet

Önceki tek-parça üretim 14.59 dk; yeni toplam üretim 12.68 dk; model yükleme 0.36 dk; çalıştırma duvar süresi 13.04 dk. A/B karışık batch süreleri parçalara eşit paylaştırılmıştır; ayar başına ayrı duvar süresi değildir. Ek maliyet yalnız yeni üretimi; soğuk 900 tahmini yeniden kullanılan kısa cümlelerin tarihsel üretim süresini de içerir.

| Ayar | Yeni parça | Üretim dk | sn/parça | Ek / eski süre | Soğuk 900 tahmini dk | Soğuk / eski |
|---|---:|---:|---:|---:|---:|---:|
| 120 | 403 | 4.20 | 0.62 | 0.29× | 15.67 | 1.07× |
| 80 | 895 | 8.48 | 0.57 | 0.58× | 17.24 | 1.18× |

## Tek parçada doğru, parçalıda yanlış örnekler

Her ayardan en fazla 10 örnek: veri sırasındaki ilk 5 içerik değişimi ve ilk 5 yalnız whitespace farkı; havuz yetersizse kalan örnekler veri sırasından tamamlanır. Rastgele seçim yok. Tüm 38/90 regresyon `regression-review.json` içinde. İçerik değişimi bağlam kaybını kanıtlamaz.

### 120: 38 regresyon

#### validation:boun:pop_272:kismi

Tanı: `content_changed`; bölme konumları: [80]

```text
Girdi: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda gormezden gelmeyi, hesap disi birakmayı en çok arzu edeceginiz sey bu karmasıkliktır.
Hedef: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda görmezden gelmeyi, hesap dışı bırakmayı en çok arzu edeceğiniz şey bu karmaşıklıktır.
Tek parça: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda görmezden gelmeyi, hesap dışı bırakmayı en çok arzu edeceğiniz şey bu karmaşıklıktır.
Parçalı: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda görmezden gelmeyi,hesap dışına bırakmayı en çok arzu edeceğiniz şey bu karışıklıktaştır.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [79, 80], "output_span": [79, 79], "input": " ", "output": ""}, {"op": "insert", "input_span": [90, 90], "output_span": [89, 91], "input": "", "output": "na"}, {"op": "replace", "input_span": [134, 136], "output_span": [135, 136], "input": "ma", "output": "ı"}, {"op": "insert", "input_span": [143, 143], "output_span": [143, 146], "input": "", "output": "aşt"}]
```

#### validation:boun:bio_1575:tam

Tanı: `content_changed`; bölme konumları: [51]

```text
Girdi: Buna karsilik yoneticilerden Kolombiyali Pasquali, Misirli Hamdi Kandil ve Fransiz Herve Bourges yeni gorusleri savunanlar arasinda yer aliyorlardi.
Hedef: Buna karşılık yöneticilerden Kolombiyalı Pasquali, Mısırlı Hamdi Kandil ve Fransız Herve Bourges yeni görüşleri savunanlar arasında yer alıyorlardı.
Tek parça: Buna karşılık yöneticilerden Kolombiyalı Pasquali, Mısırlı Hamdi Kandil ve Fransız Herve Bourges yeni görüşleri savunanlar arasında yer alıyorlardı.
Parçalı: Buna karşılık yöneticilerden Kolombiyali Pasquali,Misirli Hamdi Kandil ve Fransız Herve Bourges yeni görüşleri savunanlar arasında yer alıyorlardı.
```

Hedef → çıktı farkı:
```json
[{"op": "replace", "input_span": [39, 40], "output_span": [39, 40], "input": "ı", "output": "i"}, {"op": "delete", "input_span": [50, 51], "output_span": [50, 50], "input": " ", "output": ""}, {"op": "replace", "input_span": [52, 53], "output_span": [51, 52], "input": "ı", "output": "i"}, {"op": "replace", "input_span": [54, 55], "output_span": [53, 54], "input": "ı", "output": "i"}, {"op": "replace", "input_span": [57, 58], "output_span": [56, 57], "input": "ı", "output": "i"}]
```

#### validation:boun:news_1865:tam

Tanı: `content_changed`; bölme konumları: [83]

```text
Girdi: Babacan, Kanada ile iliskilerin oldukca gelismekte oldugunu vurgulamakla birlikte, Ermeni iddialari konusunda Kanada'nin takindigi tutumun iliskilere golge dusurdugunu ifade etti.
Hedef: Babacan, Kanada ile ilişkilerin oldukça gelişmekte olduğunu vurgulamakla birlikte, Ermeni iddiaları konusunda Kanada'nın takındığı tutumun ilişkilere gölge düşürdüğünü ifade etti.
Tek parça: Babacan, Kanada ile ilişkilerin oldukça gelişmekte olduğunu vurgulamakla birlikte, Ermeni iddiaları konusunda Kanada'nın takındığı tutumun ilişkilere gölge düşürdüğünü ifade etti.
Parçalı: Babacan, Kanada ile ilişkilerin oldukça gelişmekte olduğunu vurgulamakla birlikte,Ermeni iddiaları konusunda Kanada'nın takındığı tutumun ilişkilere gölge düşürdüğini ifade etti.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [82, 83], "output_span": [82, 82], "input": " ", "output": ""}, {"op": "replace", "input_span": [164, 165], "output_span": [163, 164], "input": "ü", "output": "i"}, {"op": "replace", "input_span": [166, 167], "output_span": [165, 166], "input": "ü", "output": "i"}]
```

#### validation:boun:pop_157:koruma

Tanı: `content_changed`; bölme konumları: [114]

```text
Girdi: Bu kişileri anlamlı güzel birkaç sözle yüceltmek ya da basit bile olsa bir teşekkür etmek bu kişiler için oldukça anlamlı olacaktır.
Hedef: Bu kişileri anlamlı güzel birkaç sözle yüceltmek ya da basit bile olsa bir teşekkür etmek bu kişiler için oldukça anlamlı olacaktır.
Tek parça: Bu kişileri anlamlı güzel birkaç sözle yüceltmek ya da basit bile olsa bir teşekkür etmek bu kişiler için oldukça anlamlı olacaktır.
Parçalı: Bu kişileri anlamlı güzel birkaç sözle yüceltmek ya da basit bile olsa bir teşekkür etmek bu kişiler için oldukça önemlianlamlı olacaktır.
```

Hedef → çıktı farkı:
```json
[{"op": "insert", "input_span": [114, 114], "output_span": [114, 120], "input": "", "output": "önemli"}]
```

#### validation:boun:news_449:tam

Tanı: `content_changed`; bölme konumları: [91]

```text
Girdi: Gittigi her secim bolgesinde ve televizyon konusmalarinda cekilme konusunu isleyen Ciller, farki uce cikararak Yilmaz'dan noter destekli imza istiyor.
Hedef: Gittiği her seçim bölgesinde ve televizyon konuşmalarında çekilme konusunu işleyen Çiller, farkı üçe çıkararak Yılmaz'dan noter destekli imza istiyor.
Tek parça: Gittiği her seçim bölgesinde ve televizyon konuşmalarında çekilme konusunu işleyen Çiller, farkı üçe çıkararak Yılmaz'dan noter destekli imza istiyor.
Parçalı: Gittiği her seçim bölgesinde ve televizyon konuşmalarında çekilme konusunu işleyen Çiller,farkı üççıkarak Yılmaz'dan noter destekli imza istiyor.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [90, 91], "output_span": [90, 90], "input": " ", "output": ""}, {"op": "delete", "input_span": [99, 101], "output_span": [98, 98], "input": "e ", "output": ""}, {"op": "delete", "input_span": [104, 106], "output_span": [101, 101], "input": "ar", "output": ""}]
```

#### validation:boun:ins_1785:koruma

Tanı: `whitespace_only`; bölme konumları: [79]

```text
Girdi: Şoför, "Şu gördüğünüz ardıçların her birinin altında ne maceralarım var benim, evlendikten sonra taşşakları çekilmiş tosuna döndük, tey tey tey" diye iç çekmiş.
Hedef: Şoför, "Şu gördüğünüz ardıçların her birinin altında ne maceralarım var benim, evlendikten sonra taşşakları çekilmiş tosuna döndük, tey tey tey" diye iç çekmiş.
Tek parça: Şoför, "Şu gördüğünüz ardıçların her birinin altında ne maceralarım var benim, evlendikten sonra taşşakları çekilmiş tosuna döndük, tey tey tey" diye iç çekmiş.
Parçalı: Şoför, "Şu gördüğünüz ardıçların her birinin altında ne maceralarım var benim,evlendikten sonra taşşakları çekilmiş tosuna döndük, tey tey tey" diye iç çekmiş.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [78, 79], "output_span": [78, 78], "input": " ", "output": ""}]
```

#### validation:boun:ins_371:kismi

Tanı: `whitespace_only`; bölme konumları: [99]

```text
Girdi: Ayrica mevcut "backbone" üzerinden çesitli elektronik ticaret sitelerine Web sunuculuğu, güvenlik, yedekleme ve odeme altyapısi hizmeti verilmektedir.
Hedef: Ayrıca mevcut "backbone" üzerinden çeşitli elektronik ticaret sitelerine Web sunuculuğu, güvenlik, yedekleme ve ödeme altyapısı hizmeti verilmektedir.
Tek parça: Ayrıca mevcut "backbone" üzerinden çeşitli elektronik ticaret sitelerine Web sunuculuğu, güvenlik, yedekleme ve ödeme altyapısı hizmeti verilmektedir.
Parçalı: Ayrıca mevcut "backbone" üzerinden çeşitli elektronik ticaret sitelerine Web sunuculuğu, güvenlik,yedekleme ve ödeme altyapısı hizmeti verilmektedir.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [98, 99], "output_span": [98, 98], "input": " ", "output": ""}]
```

#### validation:boun:pop_842:kismi

Tanı: `whitespace_only`; bölme konumları: [20]

```text
Girdi: Ardindan Escoffier, Fransiz mutfagının yuceliğini dogrudan soslarina baglıyor ve ''Soslar bir mutfagın merkezini olustururlar.
Hedef: Ardından Escoffier, Fransız mutfağının yüceliğini doğrudan soslarına bağlıyor ve ''Soslar bir mutfağın merkezini oluştururlar.
Tek parça: Ardından Escoffier, Fransız mutfağının yüceliğini doğrudan soslarına bağlıyor ve ''Soslar bir mutfağın merkezini oluştururlar.
Parçalı: Ardından Escoffier,Fransız mutfağının yüceliğini doğrudan soslarına bağlıyor ve ''Soslar bir mutfağın merkezini oluştururlar.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [19, 20], "output_span": [19, 19], "input": " ", "output": ""}]
```

#### validation:boun:ess_457:kismi

Tanı: `whitespace_only`; bölme konumları: [45]

```text
Girdi: Her iki nokta arasindaki potansiyel aslinda, dogru eğitim verilen sağlıklı ortamda bircok insanin ulaşma ihtimali olan bir potansiyeldir.
Hedef: Her iki nokta arasındaki potansiyel aslında, doğru eğitim verilen sağlıklı ortamda birçok insanın ulaşma ihtimali olan bir potansiyeldir.
Tek parça: Her iki nokta arasındaki potansiyel aslında, doğru eğitim verilen sağlıklı ortamda birçok insanın ulaşma ihtimali olan bir potansiyeldir.
Parçalı: Her iki nokta arasındaki potansiyel aslında,doğru eğitim verilen sağlıklı ortamda birçok insanın ulaşma ihtimali olan bir potansiyeldir.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [44, 45], "output_span": [44, 44], "input": " ", "output": ""}]
```

#### validation:boun:pop_1813:koruma

Tanı: `whitespace_only`; bölme konumları: [97]

```text
Girdi: Şapka konusundaki görüşlerinizi düşündüm, fena bir düşünce değil, bir dahaki sefere, bakarsınız, şapkayı da bırakıp giderim anasını satayım.
Hedef: Şapka konusundaki görüşlerinizi düşündüm, fena bir düşünce değil, bir dahaki sefere, bakarsınız, şapkayı da bırakıp giderim anasını satayım.
Tek parça: Şapka konusundaki görüşlerinizi düşündüm, fena bir düşünce değil, bir dahaki sefere, bakarsınız, şapkayı da bırakıp giderim anasını satayım.
Parçalı: Şapka konusundaki görüşlerinizi düşündüm, fena bir düşünce değil, bir dahaki sefere, bakarsınız,şapkayı da bırakıp giderim anasını satayım.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [96, 97], "output_span": [96, 96], "input": " ", "output": ""}]
```

### 80: 90 regresyon

#### validation:boun:news_1652:kismi

Tanı: `content_changed`; bölme konumları: [63]

```text
Girdi: ABD Baskanı George Bush, Hindistan Basbakani Manmohan Singh'i, Teksas'taki ciftlik evine davet etti.
Hedef: ABD Başkanı George Bush, Hindistan Başbakanı Manmohan Singh'i, Teksas'taki çiftlik evine davet etti.
Tek parça: ABD Başkanı George Bush, Hindistan Başbakanı Manmohan Singh'i, Teksas'taki çiftlik evine davet etti.
Parçalı: ABD Başkanı George Bush, Hindistan Başbakanı Manmohan Singh'i, Texas'taki çiftlik evine davet etti.
```

Hedef → çıktı farkı:
```json
[{"op": "replace", "input_span": [65, 67], "output_span": [65, 66], "input": "ks", "output": "x"}]
```

#### validation:boun:bio_969:tam

Tanı: `content_changed`; bölme konumları: [43]

```text
Girdi: Yasamanin getirdigi sikintilari hafife al, ama onlari resme aktarmaktan da alikoyma kendini.
Hedef: Yaşamanın getirdiği sıkıntıları hafife al, ama onları resme aktarmaktan da alıkoyma kendini.
Tek parça: Yaşamanın getirdiği sıkıntıları hafife al, ama onları resme aktarmaktan da alıkoyma kendini.
Parçalı: Yaşamanın getirdiği sıkıntıları hafife al,ama onları resme aktarmaktan da alikoyma kendini.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [42, 43], "output_span": [42, 42], "input": " ", "output": ""}, {"op": "replace", "input_span": [77, 78], "output_span": [76, 77], "input": "ı", "output": "i"}]
```

#### validation:boun:bio_601:koruma

Tanı: `content_changed`; bölme konumları: [46]

```text
Girdi: Sana karşı dostluğunda çok sadık olduğu için, bu mevzudaki ihmali cidden hayret verici idi.
Hedef: Sana karşı dostluğunda çok sadık olduğu için, bu mevzudaki ihmali cidden hayret verici idi.
Tek parça: Sana karşı dostluğunda çok sadık olduğu için, bu mevzudaki ihmali cidden hayret verici idi.
Parçalı: Sana karşı dostluğunda çok sadık olduğu için,bu mevzudaki ihmali ciddi hayret verici idi.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [45, 46], "output_span": [45, 45], "input": " ", "output": ""}, {"op": "replace", "input_span": [70, 72], "output_span": [69, 70], "input": "en", "output": "i"}]
```

#### validation:boun:news_926:tam

Tanı: `content_changed`; bölme konumları: [77]

```text
Girdi: Guvenlik kamera setinizi kurduktan sonra cevrimici olarak ucretsiz bir hesap acabilirsiniz.
Hedef: Güvenlik kamera setinizi kurduktan sonra çevrimiçi olarak ücretsiz bir hesap açabilirsiniz.
Tek parça: Güvenlik kamera setinizi kurduktan sonra çevrimiçi olarak ücretsiz bir hesap açabilirsiniz.
Parçalı: Güvenlik kamera setinizi kurduktan sonra çevrimiçi olarak ücretsiz bir hesapacabilirsiniz.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [76, 77], "output_span": [76, 76], "input": " ", "output": ""}, {"op": "replace", "input_span": [78, 79], "output_span": [77, 78], "input": "ç", "output": "c"}]
```

#### validation:boun:pop_272:kismi

Tanı: `content_changed`; bölme konumları: [80]

```text
Girdi: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda gormezden gelmeyi, hesap disi birakmayı en çok arzu edeceginiz sey bu karmasıkliktır.
Hedef: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda görmezden gelmeyi, hesap dışı bırakmayı en çok arzu edeceğiniz şey bu karmaşıklıktır.
Tek parça: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda görmezden gelmeyi, hesap dışı bırakmayı en çok arzu edeceğiniz şey bu karmaşıklıktır.
Parçalı: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda görmezden gelmeyi,hesap dışına bırakmayı en çok arzu edeceğiniz şey bu karışıklıktaştır.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [79, 80], "output_span": [79, 79], "input": " ", "output": ""}, {"op": "insert", "input_span": [90, 90], "output_span": [89, 91], "input": "", "output": "na"}, {"op": "replace", "input_span": [134, 136], "output_span": [135, 136], "input": "ma", "output": "ı"}, {"op": "insert", "input_span": [143, 143], "output_span": [143, 146], "input": "", "output": "aşt"}]
```

#### validation:boun:ins_1785:koruma

Tanı: `whitespace_only`; bölme konumları: [79, 132]

```text
Girdi: Şoför, "Şu gördüğünüz ardıçların her birinin altında ne maceralarım var benim, evlendikten sonra taşşakları çekilmiş tosuna döndük, tey tey tey" diye iç çekmiş.
Hedef: Şoför, "Şu gördüğünüz ardıçların her birinin altında ne maceralarım var benim, evlendikten sonra taşşakları çekilmiş tosuna döndük, tey tey tey" diye iç çekmiş.
Tek parça: Şoför, "Şu gördüğünüz ardıçların her birinin altında ne maceralarım var benim, evlendikten sonra taşşakları çekilmiş tosuna döndük, tey tey tey" diye iç çekmiş.
Parçalı: Şoför, "Şu gördüğünüz ardıçların her birinin altında ne maceralarım var benim,evlendikten sonra taşşakları çekilmiş tosuna döndük,tey tey tey" diye iç çekmiş.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [78, 79], "output_span": [78, 78], "input": " ", "output": ""}, {"op": "delete", "input_span": [131, 132], "output_span": [130, 130], "input": " ", "output": ""}]
```

#### validation:boun:ins_371:kismi

Tanı: `whitespace_only`; bölme konumları: [77]

```text
Girdi: Ayrica mevcut "backbone" üzerinden çesitli elektronik ticaret sitelerine Web sunuculuğu, güvenlik, yedekleme ve odeme altyapısi hizmeti verilmektedir.
Hedef: Ayrıca mevcut "backbone" üzerinden çeşitli elektronik ticaret sitelerine Web sunuculuğu, güvenlik, yedekleme ve ödeme altyapısı hizmeti verilmektedir.
Tek parça: Ayrıca mevcut "backbone" üzerinden çeşitli elektronik ticaret sitelerine Web sunuculuğu, güvenlik, yedekleme ve ödeme altyapısı hizmeti verilmektedir.
Parçalı: Ayrıca mevcut "backbone" üzerinden çeşitli elektronik ticaret sitelerine Websunuculuğu, güvenlik, yedekleme ve ödeme altyapısı hizmeti verilmektedir.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [76, 77], "output_span": [76, 76], "input": " ", "output": ""}]
```

#### validation:boun:pop_842:kismi

Tanı: `whitespace_only`; bölme konumları: [20, 94]

```text
Girdi: Ardindan Escoffier, Fransiz mutfagının yuceliğini dogrudan soslarina baglıyor ve ''Soslar bir mutfagın merkezini olustururlar.
Hedef: Ardından Escoffier, Fransız mutfağının yüceliğini doğrudan soslarına bağlıyor ve ''Soslar bir mutfağın merkezini oluştururlar.
Tek parça: Ardından Escoffier, Fransız mutfağının yüceliğini doğrudan soslarına bağlıyor ve ''Soslar bir mutfağın merkezini oluştururlar.
Parçalı: Ardından Escoffier,Fransız mutfağının yüceliğini doğrudan soslarına bağlıyor ve ''Soslar bir mutfağın merkezini oluştururlar.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [19, 20], "output_span": [19, 19], "input": " ", "output": ""}]
```

#### validation:boun:ins_40:tam

Tanı: `whitespace_only`; bölme konumları: [57]

```text
Girdi: O, hic degismeyen toplum olaylarinin tabii akisi icinde, her cagda yasayip durdu.
Hedef: O, hiç değişmeyen toplum olaylarının tabii akışı içinde, her çağda yaşayıp durdu.
Tek parça: O, hiç değişmeyen toplum olaylarının tabii akışı içinde, her çağda yaşayıp durdu.
Parçalı: O, hiç değişmeyen toplum olaylarının tabii akışı içinde,her çağda yaşayıp durdu.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [56, 57], "output_span": [56, 56], "input": " ", "output": ""}]
```

#### validation:boun:pop_1435:koruma

Tanı: `whitespace_only`; bölme konumları: [75]

```text
Girdi: Ülkenin tüm gelirlerinin yurttaşlar arasında ihtiyaçlarına göre hakkaniyet ölçülerinde dağıtılmasıdır.
Hedef: Ülkenin tüm gelirlerinin yurttaşlar arasında ihtiyaçlarına göre hakkaniyet ölçülerinde dağıtılmasıdır.
Tek parça: Ülkenin tüm gelirlerinin yurttaşlar arasında ihtiyaçlarına göre hakkaniyet ölçülerinde dağıtılmasıdır.
Parçalı: Ülkenin tüm gelirlerinin yurttaşlar arasında ihtiyaçlarına göre hakkaniyetölçülerinde dağıtılmasıdır.
```

Hedef → çıktı farkı:
```json
[{"op": "delete", "input_span": [74, 75], "output_span": [74, 74], "input": " ", "output": ""}]
```

## Sınırlar ve devam

Sözcük bağlamı kaybı ve sınır boşlukları ayrı belirtilerle raporlandı; nedensel ayrıştırma için yeni kontrollü ayar gerekir ve bu plana eklenmedi. Başarısızlık varsa sabit kuralın sonucu yukarıda açıkça yazılıdır. Repair daha çok doğru düzeltme üretirken U/W maliyeti taşıyabilir. Nihai sistem seçilmedi. Yeni ayar, üretim veya test açılması için kullanıcı kararı beklenir.

Orijinal dosyaların başlangıç/son SHA-256 kontrolü `manifest.json` içindedir. `plan.json` tüm parçaları ve sabit sırayı; `generated.jsonl` tüm yeni token dizilerini; `piece-outputs.json` kopya/eski/yeni tüm parçaları saklar. BOUN kaynak metinleri CC BY-SA 4.0.

Yorum/örnek incelemesi yeniden üretimi: `.venv/bin/python -m scripts.run_chunking report` ardından `.venv/bin/python -m scripts.finalize_chunking`.

## Son doğrulama

56 test geçti (`.venv/bin/python -m unittest discover -s tests`). 1.298 üretim kaydı benzersiz ve tam; hepsi EOS ile bitmiş, 256 token sınırına ulaşan 0. Kısa cümlelerin eski çıktıları ve aday içermeyen parçaların birebir kopyaları doğrulandı. 900×2 bayt-eşitliği testi geçti. Tek-parça ham/repair/fallback metrikleri önceki hata analiziyle birebir aynı. Orijinal 54 dosyanın SHA-256 değeri değişmedi. Ayrıntılar `verification.json` içinde.
