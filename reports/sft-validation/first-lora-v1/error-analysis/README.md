# İlk LoRA SFT: doğrulama hata analizi

900 doğrulama örneği; yalnız mevcut çıktılar. Eğitim denetimi için 7.340 eğitim örneği okundu. Ayrı test kümesi açılmadı; model yüklenmedi, üretim/eğitim yapılmadı. Tüm örnekleme seed=42. Betik: `scripts/analyze_sft_errors.py`; çalıştırma: `.venv/bin/python -m scripts.analyze_sft_errors`.

## Puanların doğrulanması

4 model koşulu + identity: 4.500 örneğin skorları, özetleri ve kategori özetleri mevcut puanlayıcıyla birebir eşleşti. Zero-shot uyum 663/900 → 590/900; tam eşleşme 152/900 → 394/900. Orijinal dosyaların SHA-256 değerleri çalışma başı/sonu aynı (`rescoring.json`).

## Sistem ve koşullu metrikler

Yüzdeler mevcut mikro ortalama tanımlarıdır. “Uyumlu” sütunları her sistemin farklı seçilmiş alt kümesine aittir; doğrudan nedensel karşılaştırma değildir. U=unnecessary_correction karakter sayısı; W=wrongly_changed_word sözcük sayısı. Mevcut puanlayıcı bu iki hatayı yalnız eşit uzunluklu çıktılarda sayar: uzunluğu farklı çıktılar için 0, hatasızlık anlamına gelmez.

| Sistem | Uyum | Tam eşleşme | Aday doğruluğu | Gerekli düzeltme (tümü) | Aday (uyumlu) | Gerekli (uyumlu) | Tam (uyumlu) | U | W | Eşit uzunluk n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pre_zero_shot | 73.67% | 16.89% | 50.56% | 10.73% | 75.46% | 16.57% | 22.93% | 3 | 121 | 697 |
| pre_five_shot | 50.33% | 20.78% | 33.48% | 17.60% | 87.18% | 52.29% | 41.28% | 17 | 311 | 547 |
| sft_zero_shot | 65.56% | 43.78% | 48.49% | 38.10% | 96.01% | 88.51% | 66.78% | 124 | 241 | 663 |
| sft_five_shot | 65.89% | 43.33% | 50.48% | 41.05% | 96.18% | 89.40% | 65.77% | 132 | 249 | 666 |
| identity | 100.00% | 15.00% | 69.59% | 0.00% | 69.59% | 0.00% | 15.00% | 0 | 0 | 900 |
| sft_zero_shot_fallback | 100.00% | 44.56% | 80.67% | 38.10% | 80.67% | 38.10% | 44.56% | 88 | 110 | 900 |
| sft_zero_shot_repair | 100.00% | 55.56% | 94.93% | 87.20% | 94.93% | 87.20% | 55.56% | 203 | 301 | 900 |
| sft_five_shot_fallback | 100.00% | 44.67% | 81.55% | 41.05% | 81.55% | 41.05% | 44.67% | 91 | 112 | 900 |
| sft_five_shot_repair | 100.00% | 54.33% | 94.82% | 87.26% | 94.82% | 87.26% | 54.33% | 225 | 322 | 900 |

### Temel bulgular ve pratik anlamı

- Zero-shot tam eşleşme +242 cümle; 254 örnek düzelirken 12 örnek bozuldu. Uyum net −73 cümle: 186 yeni ihlal, 113 giderilen ihlal.
- Zero-shot 310 ihlalden 237’si farklı uzunlukta; 73’ü eşit uzunlukta. Token sınırı zero-shot’ta 0/900, five-shot’ta 1/900: ana zero-shot sorunu sınır kesilmesiyle açıklanamıyor.
- Eğitim hedeflerinin 7.340/7.340’ı katı kurala uyuyor; normalize train/validation çakışması 0; iki kümede de koruma payı %15. Bu kontroller dilsel hedef kalitesini kanıtlamaz.
- SFT+fallback zero-shot: 401/900 tam doğru (%44,56), gerekli düzeltme %38,10. SFT+hizalama: 500/900 (%55,56), gerekli düzeltme %87,20; ikisi de %100 uyumlu ayrı sistemler.
- Hizalama mevcut tam doğru çıktılardan 0’ını bozup 106 yeni tam doğru kazandırıyor. Fallback’e göre gereksiz dönüşüm 88→203 ve yanlış değiştirilmiş sözcük 110→301: daha çok düzeltmenin bedeli daha çok yanlış müdahale. Bu iki sistemin tüm çıktıları eşit uzunlukta olduğundan bu hata sayıları karşılaştırılabilir.

Önceki five-shot incelemesine aynı otomatik belirtilerle bakıldığında tam sözcük silme bloğu 11→2, harf büyüklüğü belirtisi 17→7, boşluk dizisi değişimi 100→36, noktalama değişimi 97→6. SFT bu belirtileri azaltıyor; kalan sözcük içi yeniden yazımlar kısa/uzun ve yasak harf kategorilerinde belirgin. Hizalama belirtileri tam dilsel envanter değildir; karma silme+ekleme bloklarını ayrı sözcük silme olarak saymayabilir.

## İhlal sınıflandırması

Birbirini dışlayan ana kategoriler aşağıdaki sıra ile atanır: boş → ek biçim → EOS’suz sınır → eksik önek → yalnız tam sözcük silme → yalnız tekrar/ekleme → yalnız Türkçe harf büyüklüğü → yalnız boşluk/noktalama → diğer kısa/uzun → eşit uzunlukta yasak harf → diğer karma. İlk eşleşme kazanır. Sözcük eşleme diakritikleri kaldırır, büyüklüğü korur; tam sözcük kategorileri sadece saf silme/ekleme hizalamasıdır. Karma olaylar kısa/uzun altında kalabilir. Eksik önek erken EOS nedenini kanıtlamaz. Açıklama/biçim sınıfı sabit önek ve sarmalayıcı sezgisidir. Uzunluk farkı ayrıca raporlanır, kategori toplamına eklenmez. Mevcut `unalignable` metriği yalnız uzunluk farkıdır; yeni sınıflandırmanın “diğer karma” etiketiyle aynı değildir.

| Kategori | Zero n | İhlallerde | 900 içinde | Five n | İhlallerde | 900 içinde |
|---|---:|---:|---:|---:|---:|---:|
| Boş çıktı | 0 | 0.00% | 0.00% | 0 | 0.00% | 0.00% |
| Ek biçim/açıklama belirtisi | 0 | 0.00% | 0.00% | 0 | 0.00% | 0.00% |
| EOS olmadan token sınırı | 0 | 0.00% | 0.00% | 1 | 0.33% | 0.11% |
| Girdinin eksik öneki (erken bitiş belirtisi) | 0 | 0.00% | 0.00% | 0 | 0.00% | 0.00% |
| Tam sözcük silme | 0 | 0.00% | 0.00% | 0 | 0.00% | 0.00% |
| Tam sözcük tekrarı | 0 | 0.00% | 0.00% | 0 | 0.00% | 0.00% |
| Tam sözcük ekleme | 0 | 0.00% | 0.00% | 0 | 0.00% | 0.00% |
| Yalnız harf büyüklüğü ihlali | 4 | 1.29% | 0.44% | 4 | 1.30% | 0.44% |
| Yalnız boşluk/noktalama ihlali | 4 | 1.29% | 0.44% | 4 | 1.30% | 0.44% |
| Diğer kısa çıktı / sözcük içi yeniden yazım | 122 | 39.35% | 13.56% | 117 | 38.11% | 13.00% |
| Diğer uzun çıktı / sözcük içi yeniden yazım | 111 | 35.81% | 12.33% | 112 | 36.48% | 12.44% |
| Eşit uzunlukta izin verilmeyen harf değişimi | 68 | 21.94% | 7.56% | 68 | 22.15% | 7.56% |
| Diğer eşit uzunluklu karma ihlal | 1 | 0.32% | 0.11% | 1 | 0.33% | 0.11% |

pre_zero_shot: toplam 237 ihlal; uzunluk dağılımı {'longer': 66, 'equal': 34, 'shorter': 137}.

pre_five_shot: toplam 447 ihlal; uzunluk dağılımı {'equal': 94, 'longer': 159, 'shorter': 194}.

sft_zero_shot: toplam 310 ihlal; uzunluk dağılımı {'shorter': 123, 'equal': 73, 'longer': 114}.

sft_five_shot: toplam 307 ihlal; uzunluk dağılımı {'equal': 73, 'shorter': 119, 'longer': 115}.

Örtüşen belirtiler (saf kategori dışında karma olayları da yakalar; toplanmaz):

| Belirti | Önce zero | Önce five | SFT zero | SFT five |
|---|---:|---:|---:|---:|
| candidate_forbidden_change_in_aligned_blocks | 21 | 61 | 52 | 48 |
| case_change_in_aligned_blocks | 5 | 17 | 6 | 7 |
| noncandidate_letter_change_in_aligned_blocks | 40 | 121 | 79 | 87 |
| punctuation_sequence_changed | 84 | 97 | 4 | 6 |
| repeated_bigram_proxy | 1 | 1 | 1 | 1 |
| whitespace_sequence_changed | 50 | 100 | 28 | 36 |
| whole_word_delete_block | 12 | 11 | 2 | 2 |
| whole_word_insert_block | 3 | 7 | 0 | 0 |

Belirtiler: diakritik katlanmış sözcük hizalamasında saf delete/insert blokları; çıktıda en az 3 kez geçen ve girdide daha az görülen bigram vekili (tek başına döngü kanıtı değil); eşit boyutlu karakter bloklarında harf büyüklüğü/aday olmayan harf değişimi; boşluk ve noktalama dizilerinin değişimi. Hizalama belirsizliği nedeniyle bunlar alt düzey otomatik belirtilerdir.

Her gözlenen SFT kategorisinden en çok 3 örnek [kategori örnekleri](category-examples.md) içinde; kategori 0/1/2 örnekliyse olmayan örnek üretilmedi. Tüm atamalar ve diff’ler `violations.json` içinde.

## Eşleştirilmiş geçişler

Tablo hücreleri cümle sayısıdır. Fark = SFT − önce; GA yüzde puan. 10.000 tekrar, seed 42, kaynak/pair bağlantılı kümeler korunur. McNemar iki taraflı exact binom testidir; cümle bağımsızlığı varsayar. Aynı kaynağın varyantları bağımlıysa bootstrap aralığı daha uygun kanıttır.

| Koşul / metrik | İkisi evet | Önce evet | Sonra evet | İkisi hayır | Fark (yp) | %95 GA (yp) | McNemar p |
|---|---:|---:|---:|---:|---:|---:|---:|
| zero_shot/strict_compliance | 477 | 186 | 113 | 124 | -8.11 | [-11.89, -4.33] | 2.874e-05 |
| zero_shot/sentence_exact | 140 | 12 | 254 | 494 | 26.89 | [23.89, 30.00] | 3.604e-60 |
| five_shot/strict_compliance | 367 | 86 | 226 | 221 | 15.56 | [11.89, 19.22] | 1.17e-15 |
| five_shot/sentence_exact | 160 | 27 | 230 | 483 | 22.56 | [19.44, 25.78] | 2.55e-41 |

## Üretim, EOS ve istem denetimi

Tokenizer EOS=151645; generation EOS=[151643, 151645] ({'151643': '<|endoftext|>', '151645': '<|im_end|>'}). Eğitim EOS’u durdurma listesinde: True. Kaydedilmiş ve temel tokenizer şablonları aynı: True; 900 zero-shot isteminin 900 tanesi birebir aynı. Five-shot istemlerinin 900/900 tanesi beş gösterim nedeniyle eğitimden farklıdır.

Kod: `train_lora.encode_example` ve `inference.generate_batch` aynı `build_messages`, `add_generation_prompt=True`, `enable_thinking=False` kullanır. Eğitim hedef+EOS öğretir; değerlendirme greedy, batch=8, sol padding, max_new_tokens=256; bitmiş diziler ilk stop token’dan kesilir. Padding token farkı prompt içeriğini değiştirmez; eğitim padding label’ları -100’dür. Tarihsel kod hash kontrolleri: 12/12 eşleşme. Generation config’in tarihsel hash’i kaydedilmedi; EOS denetimi sabit model revision’ının yerel config’i ve saklanan tokenlar üzerinden yapılmıştır.

| Sistem | Hedef med/p95/max | Çıktı med/p95/max (yeniden tokenize) | Üretilen max (stop dahil) | Sınıra ulaşan | Sınırda EOS yok | EOS yok |
|---|---:|---:|---:|---:|---:|---:|
| pre_zero_shot | 23.00/68.00/117.00 | 23.50/69.00/130.00 | 131.0 | 0 | 0 | 0 |
| pre_five_shot | 23.00/68.00/117.00 | 23.00/68.00/129.00 | 130.0 | 0 | 0 | 0 |
| sft_zero_shot | 23.00/68.00/117.00 | 23.00/67.05/115.00 | 119.0 | 0 | 0 | 0 |
| sft_five_shot | 23.00/68.00/117.00 | 23.00/68.00/256.00 | 256.0 | 1 | 1 | 1 |

Kayıtlı token dizileri yeniden decode edilerek 3.600 çıktı ile birebir eşleşti. Hedef/çıktı içerik uzunluğu EOS hariç; orijinal üretilen uzunluk stop dahil. Tam quantile’lar `generation-audit.json` içinde. Sınır/EOS ve biçim belirtileri gözlemseldir: yeni kontrollü üretim olmadan “ayar kaynaklı” nedensel pay atanamaz. Boş/biçim/sınır/eksik-önek dışındaki ihlaller gözlenen metin değişiklikleridir; bunların da model/ayar nedensel ayrımı kesin değildir.

Gözlemsel ayrım: zero-shot 0/310 ihlalde boş/biçim/sınır/eksik-önek belirtisi, 310/310 ihlalde diğer metin değişikliği; five-shot 1/307 sınır belirtisi ve 306/307 diğer değişiklik. Five-shot `validation:boun:pop_1949:tam` çıktısı “kıyı şanlı” tekrarına giriyor; hedef 256 token gerektirmiyor. Sınırı yükseltmek tek başına çözüm olarak gerekçelendirilemez. Bu örneğin 8’li batch’i yaklaşık 31 saniye sürmüş; tek örnek kontrollü üretim için model yükleme dahil 1–3 dakika ihtiyatlı planlama tahminidir, ölçülmüş tek-örnek süre değildir. Üretim yapılmadı; ön onay gerekir.

## Uyumlu çıktılarda karakterler

Doğru = hedefle eşleşen tüm aday konumları (koruma dahil). Kaçırılan = gerekli dönüşüm yapılmamış; yanlış = gereksiz dönüşüm. Katı uyumlu çıktıda mevcut Türkçe harfi ters yönde değiştirmek mümkün değildir. Büyük harfler ayrı tutulur; I→İ izinli, I→ı ve İ→i büyüklük değişimidir. Aşağıda SFT koşulları; eğitim öncesi sayılar da `characters.json` içindedir.

| Çift | Zero doğru | Kaçırılan | Yanlış | Five doğru | Kaçırılan | Yanlış |
|---|---:|---:|---:|---:|---:|---:|
| c/ç | 446 | 21 | 11 | 469 | 20 | 11 |
| g/ğ | 539 | 16 | 1 | 566 | 16 | 0 |
| i/ı | 3593 | 77 | 17 | 3768 | 76 | 17 |
| o/ö | 981 | 12 | 7 | 1012 | 13 | 7 |
| s/ş | 1227 | 74 | 18 | 1262 | 72 | 22 |
| u/ü | 1354 | 40 | 22 | 1404 | 39 | 23 |
| C/Ç | 29 | 4 | 3 | 28 | 7 | 2 |
| G/Ğ | 32 | 0 | 0 | 31 | 1 | 0 |
| I/İ | 49 | 6 | 3 | 52 | 5 | 3 |
| O/Ö | 46 | 2 | 2 | 48 | 1 | 2 |
| S/Ş | 70 | 7 | 2 | 71 | 5 | 2 |
| U/Ü | 17 | 1 | 2 | 17 | 1 | 2 |

## Sözcük ve konum incelemesi

Yalnız uyumlu çıktıda hedefle farklı whitespace sözcükleri. Uzunluk alfanümerik karakter sayısı. Konum ilk/son whitespace sözcüğüne göre; tek sözcük baş sayılır. Özel isim vekili=başta olmayan büyük harfli sözcük; kısaltma vekili=tam büyük harf; yabancı vekili=q/w/x. Bunlar dilsel etiket değildir. Belirsizlik vekili=eğitim hedeflerinde aynı ASCII biçimin en az iki Türkçe karşılığı; bağlamda ikisinin de geçerli olduğu iddia edilmez. Ön ek ortak karakter uzunluğu, son 3 karakter ve yüzey son-ek listesi raporlanır; morfolojik çözümleme yoktur. Gerçek özel isim/yabancı köken/ek ve bağlamsal çoklu doğru sayısı mevcut etiketlerden doğrulanamaz.

| Sistem | Hatalı sözcük | Uzunluk 1–5 / 6–10 / 11+ | Baş / orta / son | Özel isim vekili | Kısaltma | qwx | Çoklu biçim | Son 3 karakterde hata |
|---|---:|---|---|---:|---:|---:|---:|---:|
| pre_zero_shot | 1894 | {'6-10': 1124, '1-5': 497, '11+': 273} | {'middle': 1516, 'end': 227, 'start': 151} | 187 | 23 | 0 | 89 | 1049 |
| pre_five_shot | 625 | {'6-10': 367, '11+': 87, '1-5': 171} | {'start': 57, 'middle': 483, 'end': 85} | 72 | 9 | 0 | 31 | 303 |
| sft_zero_shot | 277 | {'11+': 36, '6-10': 147, '1-5': 94} | {'middle': 190, 'end': 37, 'start': 50} | 55 | 7 | 0 | 15 | 126 |
| sft_five_shot | 273 | {'11+': 36, '6-10': 150, '1-5': 87} | {'middle': 187, 'end': 44, 'start': 42} | 42 | 6 | 0 | 12 | 117 |

sft_zero_shot: hedef/çıktı ortak önek uzunluğu {'0': 64, '1-3': 137, '4+': 76}; yüzey son-ek eşleşmeleri {'none': 263, 'dır': 1, 'dan': 3, 'lar': 1, 'lık': 2, 'den': 2, 'miş': 2, 'yor': 1, 'ler': 2}.

sft_five_shot: hedef/çıktı ortak önek uzunluğu {'0': 66, '1-3': 128, '4+': 79}; yüzey son-ek eşleşmeleri {'none': 259, 'dır': 1, 'dir': 1, 'dan': 2, 'lar': 1, 'lık': 3, 'den': 1, 'miş': 2, 'yor': 1, 'ler': 2}.

Sözcük bazında tüm girdi/hedef/çıktılar, ortak önek uzunlukları, yüzey ekleri ve eğitimde görülen alternatifler `word-errors.json` içinde.

## Dilimler

En kötü = SFT zero-shot uyum oranı, eşitlikte tam eşleşme; n≥30. Dilimler farklı eksenlerde örtüşebilir. Kaynak öneki alan etiketi değil, original_sent_id önekidir.

- candidates=31+: n=152, uyum 32.89%, tam eşleşme 14.47%.
- length=121+: n=177, uyum 40.11%, tam eşleşme 23.16%.
- candidates=21-30: n=168, uyum 53.57%, tam eşleşme 30.95%.

| Sistem | Dilim | n | Uyum | Tam eşleşme |
|---|---|---:|---:|---:|
| pre_zero_shot | length=41-80 | 317 | 77.29% | 15.77% |
| pre_zero_shot | candidates=11-20 | 293 | 77.13% | 13.65% |
| pre_zero_shot | needs_correction=True | 765 | 71.37% | 4.71% |
| pre_zero_shot | category=kismi | 225 | 67.56% | 6.67% |
| pre_zero_shot | source_prefix=ins | 187 | 78.61% | 18.72% |
| pre_zero_shot | length=121+ | 177 | 58.19% | 10.17% |
| pre_zero_shot | candidates=31+ | 152 | 57.24% | 3.95% |
| pre_zero_shot | category=tam | 540 | 72.96% | 3.89% |
| pre_zero_shot | source_prefix=bio | 170 | 72.94% | 17.65% |
| pre_zero_shot | candidates=0-10 | 287 | 82.23% | 32.40% |
| pre_zero_shot | length=1-40 | 233 | 81.12% | 27.90% |
| pre_zero_shot | source_prefix=pop | 184 | 78.26% | 16.30% |
| pre_zero_shot | source_prefix=news | 174 | 70.69% | 14.94% |
| pre_zero_shot | length=81-120 | 173 | 72.83% | 10.98% |
| pre_zero_shot | candidates=21-30 | 168 | 67.86% | 7.74% |
| pre_zero_shot | needs_correction=False | 135 | 86.67% | 85.93% |
| pre_zero_shot | category=koruma | 135 | 86.67% | 85.93% |
| pre_zero_shot | source_prefix=ess | 185 | 67.57% | 16.76% |
| pre_five_shot | length=41-80 | 317 | 54.57% | 21.77% |
| pre_five_shot | candidates=11-20 | 293 | 52.22% | 19.80% |
| pre_five_shot | needs_correction=True | 765 | 47.32% | 12.55% |
| pre_five_shot | category=kismi | 225 | 44.89% | 15.56% |
| pre_five_shot | source_prefix=ins | 187 | 57.22% | 25.67% |
| pre_five_shot | length=121+ | 177 | 28.81% | 7.91% |
| pre_five_shot | candidates=31+ | 152 | 23.68% | 2.63% |
| pre_five_shot | category=tam | 540 | 48.33% | 11.30% |
| pre_five_shot | source_prefix=bio | 170 | 54.71% | 22.94% |
| pre_five_shot | candidates=0-10 | 287 | 70.03% | 38.68% |
| pre_five_shot | length=1-40 | 233 | 68.67% | 34.33% |
| pre_five_shot | source_prefix=pop | 184 | 54.35% | 18.48% |
| pre_five_shot | source_prefix=news | 174 | 43.10% | 14.37% |
| pre_five_shot | length=81-120 | 173 | 39.88% | 13.87% |
| pre_five_shot | candidates=21-30 | 168 | 37.50% | 8.33% |
| pre_five_shot | needs_correction=False | 135 | 67.41% | 67.41% |
| pre_five_shot | category=koruma | 135 | 67.41% | 67.41% |
| pre_five_shot | source_prefix=ess | 185 | 42.16% | 22.16% |
| sft_zero_shot | length=41-80 | 317 | 70.35% | 50.16% |
| sft_zero_shot | candidates=11-20 | 293 | 67.92% | 46.76% |
| sft_zero_shot | needs_correction=True | 765 | 60.39% | 35.03% |
| sft_zero_shot | category=kismi | 225 | 61.33% | 39.11% |
| sft_zero_shot | source_prefix=ins | 187 | 71.66% | 49.20% |
| sft_zero_shot | length=121+ | 177 | 40.11% | 23.16% |
| sft_zero_shot | candidates=31+ | 152 | 32.89% | 14.47% |
| sft_zero_shot | category=tam | 540 | 60.00% | 33.33% |
| sft_zero_shot | source_prefix=bio | 170 | 67.65% | 47.65% |
| sft_zero_shot | candidates=0-10 | 287 | 87.46% | 63.76% |
| sft_zero_shot | length=1-40 | 233 | 86.27% | 59.66% |
| sft_zero_shot | source_prefix=pop | 184 | 69.02% | 41.30% |
| sft_zero_shot | source_prefix=news | 174 | 62.07% | 40.80% |
| sft_zero_shot | length=81-120 | 173 | 54.91% | 31.79% |
| sft_zero_shot | candidates=21-30 | 168 | 53.57% | 30.95% |
| sft_zero_shot | needs_correction=False | 135 | 94.81% | 93.33% |
| sft_zero_shot | category=koruma | 135 | 94.81% | 93.33% |
| sft_zero_shot | source_prefix=ess | 185 | 57.30% | 40.00% |
| sft_five_shot | length=41-80 | 317 | 69.72% | 48.90% |
| sft_five_shot | candidates=11-20 | 293 | 68.26% | 47.10% |
| sft_five_shot | needs_correction=True | 765 | 61.44% | 35.29% |
| sft_five_shot | category=kismi | 225 | 59.56% | 37.78% |
| sft_five_shot | source_prefix=ins | 187 | 71.66% | 47.59% |
| sft_five_shot | length=121+ | 177 | 41.24% | 24.29% |
| sft_five_shot | candidates=31+ | 152 | 37.50% | 17.11% |
| sft_five_shot | category=tam | 540 | 62.22% | 34.26% |
| sft_five_shot | source_prefix=bio | 170 | 65.88% | 48.24% |
| sft_five_shot | candidates=0-10 | 287 | 84.67% | 60.63% |
| sft_five_shot | length=1-40 | 233 | 84.55% | 57.51% |
| sft_five_shot | source_prefix=pop | 184 | 69.57% | 39.13% |
| sft_five_shot | source_prefix=news | 174 | 61.49% | 39.66% |
| sft_five_shot | length=81-120 | 173 | 58.96% | 33.53% |
| sft_five_shot | candidates=21-30 | 168 | 55.36% | 30.95% |
| sft_five_shot | needs_correction=False | 135 | 91.11% | 88.89% |
| sft_five_shot | category=koruma | 135 | 91.11% | 88.89% |
| sft_five_shot | source_prefix=ess | 185 | 60.54% | 42.16% |

## Eğitim verisi denetimi

Uyumsuz hedef: 0/7340. Kaynak kimliği çakışması: 0. Eğitim dizisi token quantile’ları (istem+cevap+EOS): {'min': 173.0, 'p25': 194.0, 'median': 211.0, 'p75': 239.0, 'p95': 303.0, 'p99': 364.6099999999997, 'max': 506.0}. 1024 üstü: 0; kod sınır aşımında hata verir, sessiz kesme yapmaz.

- input_exact: 0 doğrulama örneği eğitimde eşleşiyor.
- input_normalized: 0 doğrulama örneği eğitimde eşleşiyor.
- target_exact: 0 doğrulama örneği eğitimde eşleşiyor.
- target_normalized: 0 doğrulama örneği eğitimde eşleşiyor.

Normalize eşleme: NFC, Türkçe küçük harf, diakritik katlama, noktalama/boşluk çıkarma; edit-distance semantik yakınlık araması değildir. Bu tanım dışında yakın kopya yokluğu iddia edilmez.

train: n=7340; gerekli=6239 (85.00%); koruma=1101 (15.00%); kategoriler={'tam': 4404, 'kismi': 1835, 'koruma': 1101}.

validation: n=900; gerekli=765 (85.00%); koruma=135 (15.00%); kategoriler={'kismi': 225, 'tam': 540, 'koruma': 135}.

## 40 örnek ve son işlem simülasyonları

[40 örnek incelemesi](review-40.md): 20 ihlal, 10 uyumlu yanlış, 5 doğru→yanlış, 5 yanlış→doğru. 40 benzersiz örnek için geçiş grupları önce ayrılmıştır; seed=42 ve havuz sayıları `sampling.json` içinde. Diff’ler girdi→çıktı ve hedef→çıktı için karakter düzeyindedir; tüm metinler JSON’da korunur.

**Fallback:** ihlalde girdiyi döndürür. **Repair:** diakritikleri katlanmış girdi/çıktıyı SequenceMatcher ile hizalar; yalnız eşit bloklarda izinli aday değişimlerini alır, diğer tüm karakterleri girdiden kopyalar. Hedefe erişmez; metrikleri üst tabloda ayrı sistemlerdir. Tekrarlanan parçalarda hizalama yanlış konuma düzeltme taşıyabilir. Kurala uyum, hedef doğruluğu garantisi değildir. Yeni sistem seçimi henüz yapılmadı.

## Seçim kuralı seçenekleri ve maliyet

Ham modeller arasında uyum önceliği identity (%100 uyum, %15 tam eşleşme, %0 gerekli düzeltme) seçer. Fallback ve repair eklendiğinde %100 uyumda eşitlik olur; mevcut tam eşleşme ikinci kuralı artık identity’yi zorunlu kazanan yapmaz. Aday doğruluğu da korunan 12.032/17.289 konumdan dolayı identity lehine yüksek olabilir.

Seçenekler (karar verilmedi; eşikler doğrulama üzerinde sonuca göre ayarlanırsa seçim yanlılığı oluşur):

- Ürün gereksiniminden belirlenen uyum eşiği (ör. %99) + gerekli düzeltme başarısı; gereksiz düzeltmeye ayrıca üst sınır. Eşiği karşılayan aday yoksa model seçmemek veya ayrı korumalı sistem değerlendirmek gerekir.
- %100 uyum sağlayan son işlemli sistemler arasında tam eşleşme, eşitlikte gerekli düzeltme; bu karar modelden ziyade bütün sistemi seçer, ham model puanları ayrıca kalır.
- Pareto seçenekleri: uyum, gerekli düzeltme ve gereksiz müdahaleyi birlikte sunup kullanım maliyetine göre seçim. Maliyet ağırlıkları ve eşikler test açılmadan sabitlenir; bu rapor kazananı belirlemez.

| Yol | Beklenen kazanç / kanıt | Risk | Süre varsayımı |
|---|---|---|---|
| Fallback / hizalama | Üst tablodaki gözlenen doğrulama kazancı; eğitim yok | Hizalama yanlış düzeltme taşıyabilir; fallback gerekli düzeltmeyi kaçırır | Mevcut 900 çıktıda CPU ile saniye–dakika; raporda ölçülen ayrı sistem |
| Üretim/durdurma/biçim | Sınır/EOS/biçim tablosundaki şüpheli örnekler kadar inceleme adayı; başarı artışı ölçülmedi | EOS ile normal sonlanma erken anlamsal bitişi dışlamaz; ayar etkisi kontrollü deney ister | Mevcut seconds toplamı / 900 × yeniden üretilecek n; aşağıda tahmin |
| Veri düzeltmesi | Uyumsuz hedef ve kopya sayıları yukarıda; kural uyumu dilsel hedef kalitesini kanıtlamaz | Koruma ağırlığı artarsa identity davranışı güçlenebilir | Planlama varsayımı: 40 örnek × 1–2 dk = 40–80 dk uzman denetimi; yeniden eğitim ayrıca gerekir |
| İkinci eğitim | Kazanç henüz bilinmiyor; yalnız tek değişkenli deney gerekçelendirilebilir | Daha fazla epoch ezberleme/müdahale riskini artırabilir | 459 × 19 sn = 2 sa 25 dk / epoch; 918 adım ≈ 4 sa 51 dk + doğrulama |

İkinci eğitim seçilirse başlangıç önerisi rank=8, q_proj/v_proj, 1 epoch sabit tutup yalnız öğrenme oranı 2e-4→1e-4 veya koruma ağırlığı 1→2 alternatiflerinden birini denemektir. Bunlar ölçülmüş iyileştirmeler değildir. Koruma örneklerini iki kez sunmak varsayımıyla 8.441 örnek / accumulation 16 → 528 adım ≈ 2 sa 47 dk; ağırlıklı loss kullanılırsa adım 459 kalır. Rank 16 / daha fazla hedef modül için 19 sn/adım varsayımı doğrulanmaz ve 16 GB bellek ölçümü gerekir. Loss’un düşmesi tek başına bunları seçmeye yeterli değildir.

zero_shot: boş/biçim/sınır/önek şüphesi 0/900; aynı hız varsayımıyla yeniden üretim batch-amortize hesap ≈0.0 sn + model yükleme; tüm 900 ≈14.6 dk. Bu amortize hesap tek bir uzun çıktı için iyimserdir; yukarıdaki 1–3 dakika planlama payı kullanılmalıdır. Bu sayı ayar düzeltmesiyle kurtarılacak örnek sayısı değildir.
five_shot: boş/biçim/sınır/önek şüphesi 1/900; aynı hız varsayımıyla yeniden üretim batch-amortize hesap ≈1.6 sn + model yükleme; tüm 900 ≈23.9 dk. Bu amortize hesap tek bir uzun çıktı için iyimserdir; yukarıdaki 1–3 dakika planlama payı kullanılmalıdır. Bu sayı ayar düzeltmesiyle kurtarılacak örnek sayısı değildir.

**Önerilen sonraki adım:** ölçülmüş fallback ve hizalama sonuçlarını, ham modelden ayrı sistemler olarak karşılaştırıp seçim kuralını kullanıcıyla sabitlemek; yeniden eğitim kararı öncesi sınırlı niteliksel denetim. Yeni üretim için önceden süre tahmini ve onay gerekir; bu çalışmada üretim başlatılmadı. Test seti için seçim sabitlenmesi beklenir.

## Dosyalar ve sınırlar

`analysis.json` toplu ham sayılar; `metrics.csv` pay/payda; `paired.json`, `characters.json`, `word-errors.json`, `slices.json`, `training-audit.json`, `generation-audit.json` ayrıntılar. Test ve bütünlük kontrolü: `verification.json`. Morfoloji, gerçek özel isim/yabancı köken ve bağlamsal belirsizlik otomatik vekillerle kesinleştirilemez. Kategoriler gözlenen edit türleridir, nedensel etiket değildir. BOUN kaynak metinleri CC BY-SA 4.0; kaynak/lisans `data/prepared/boun-v1/source/`.
