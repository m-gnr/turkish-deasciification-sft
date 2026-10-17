# Nihai test: dondurulmuş sistem

Bu raporda 'SFT', SFT ile ince ayar yapılmış Qwen3-1.7B (first-lora-v1) ve çıktısına uygulanan kural tabanlı repair adımının birlikte oluşturduğu sistemi ifade eder. Ham model çıktısı (repair'siz) ve fallback varyantı ayrıca ölçülmüş olup ek dosyalarda bulunur.

Karşılaştırılan diğer sistem **Eğitim öncesi**: Qwen/Qwen3-1.7B, zero-shot; projeye özel ince ayar öncesindeki modeldir.

900 test örneği; 7.340 eğitim ve 900 doğrulama örneğiyle birebir/NFC/normalize girdi-hedef çakışması ve kaynak/pair kimliği çakışması 0. Normalize kontrol Türkçe küçük harf, diakritik katlama ve `\W+` çıkarımıdır; semantik yakın kopya taraması değildir.

Sistem: Qwen/Qwen3-1.7B + first-lora-v1 (`runs/first-sft-v1/training/adapter`), zero-shot, greedy (`do_sample=False`), batch=8, max_new_tokens=256, MPS/float16, seed=0; parçalama yok. Tek-parça ham çıktıya mevcut `repair` uygulanır. Commit: `596d47dc70632c5b59f271b2d38712377fd66321`. Dondurma öncesi çalışma ağacı temizdi; sonradan yalnız bu rapor dizini oluşturuldu.

Kullanıcı onayıyla Eğitim öncesi ve SFT için birer test geçişi yapıldı. Eğitim, ayar değişikliği veya test sonucuna göre seçim yapılmadı. Doğrulama çıktıları yeniden üretilmedi.

## Ana karşılaştırma

Hücreler değer [%95 GA] biçimindedir; ilk dört metrik yüzde, U karakter sayısı, W sözcük sayısıdır. Ondalık ayırıcı virgüldür; köşeli parantez içindeki iki sınır virgül ve boşlukla ayrılır.

| Sistem | Metrik | Doğrulama | Test |
|---|---|---:|---:|
| Eğitim öncesi | Uyum (%) | 73,67 [70,78, 76,56] | 72,22 [69,33, 75,11] |
| Eğitim öncesi | Tam eşleşme (%) | 16,89 [14,44, 19,33] | 17,67 [15,22, 20,11] |
| Eğitim öncesi | Aday doğruluğu (%) | 50,56 [47,43, 53,73] | 50,13 [46,88, 53,42] |
| Eğitim öncesi | Gerekli düzeltme (%) | 10,73 [9,13, 12,51] | 10,70 [9,01, 12,51] |
| Eğitim öncesi | U | 3 [0,0, 7,0] | 7 [1,0, 14,0] |
| Eğitim öncesi | W | 121 [94,0, 152,0] | 152 [102,0, 218,0] |
| SFT | Uyum (%) | 100,00 [100,00, 100,00] | 100,00 [100,00, 100,00] |
| SFT | Tam eşleşme (%) | 55,56 [52,33, 58,78] | 60,44 [57,33, 63,67] |
| SFT | Aday doğruluğu (%) | 94,93 [94,47, 95,37] | 95,66 [95,23, 96,07] |
| SFT | Gerekli düzeltme (%) | 87,20 [86,04, 88,29] | 88,52 [87,40, 89,61] |
| SFT | U | 203 [166,0, 243,0] | 161 [130,0, 193,0] |
| SFT | W | 301 [264,0, 338,0] | 264 [229,0, 301,0] |

U ve W yalnız NFC sonrası girdiyle eşit uzunluklu çıktılarda sayılır; farklı uzunlukta 0 yazılması hatasızlık değildir. Eğitim öncesi modelin düşük W değeri kısmen bu sayım sınırından kaynaklanır; doğrudan daha az hata yaptığı anlamına gelmez.

Identity, girdiyi değiştirmeden döndüren aday doğruluğu tabanıdır: testte %70,31.

### Testte eşleştirilmiş fark

Aşağıdaki aralıklar doğrudan [test-bootstrap.json](test-bootstrap.json) dosyasının `repair_minus_comparator_paired_ci95.pre_zero_shot` alanındandır; yp yüzde puandır. İlk dört metrikte pozitif fark SFT lehine başarı artışını, U/W'de pozitif fark daha fazla sayılan hatayı gösterir.

| Metrik | SFT − Eğitim öncesi, eşleştirilmiş %95 GA |
|---|---:|
| Uyum (yp) | [24,89, 30,67] |
| Tam eşleşme (yp) | [39,56, 46,11] |
| Aday doğruluğu (yp) | [42,27, 48,75] |
| Gerekli düzeltme (yp) | [75,80, 79,71] |
| U (karakter) | [123,0, 187,0] |
| W (sözcük) | [41,0, 174,0] |

Aynı test örnekleri ve aynı yeniden örneklenen kümeler iki sistemde birlikte kullanılır; her tekrarda SFT − Eğitim öncesi farkı alınır. Bu aralıklar iki ayrı marjinal güven aralığının uçlarını çıkararak hesaplanmaz.

## Metrikler ve ölçüm yöntemi

Tanımlar [puanlayıcıdaki `score`, `allowed` ve `aggregate`](../../deasciification/evaluation.py) işlevlerinden çıkarılmış; [puanlayıcı testleri](../../tests/test_evaluate.py) ve [repair testleri](../../tests/test_sft_error_analysis.py) okunarak denetlenmiştir. Bu düzenlemede testler çalıştırılmamıştır.

Girdi, hedef ve çıktı yalnız Unicode NFC ile normalleştirilir; boşluk kırpma, harf büyüklüğü eşitleme veya noktalama temizliği yapılmaz. Karakter birimi NFC sonrası Python dizgesinin konumudur. İzinli dönüşümler `c→ç, g→ğ, i→ı, o→ö, s→ş, u→ü, C→Ç, G→Ğ, I→İ, O→Ö, S→Ş, U→Ü` biçimindedir; her karakterin aynen kalmasına da izin verilir. **Kural ihlali**, çıktı uzunluğunun girdiden farklı olması veya herhangi bir konumda bu seçenekler dışında karakter bulunmasıdır; mevcut Türkçe harfleri geri çevirmek, harf büyüklüğünü değiştirmek, boşluk/noktalama değiştirmek ve açıklama eklemek bu koşullara göre ihlaldir. Hedef kurala uymuyorsa puanlayıcı hata vererek durur.

Bir cümlede herhangi bir kural ihlali varsa aday doğruluğu, gerekli düzeltme, karakter/aday koruma ve sözcük koruma gibi birincil karakter/sözcük başarı payları **0** olur; ilgili paydalar korunur. Tam eşleşme doğrudan hedef eşitliğiyle hesaplanır. Ek dosyalardaki yalnız uyumlu aday doğruluğu ise uyumsuz cümlenin paydasını da dışlar; ana tablodaki aday doğruluğu bu koşullu metrik değildir. Toplam oranlar cümle oranlarının ortalamasıyla değil, payların toplamı / paydaların toplamı ile hesaplanır (mikro ortalama); sıfır payda `null` (N/A) olur.

Girdi `UZUMLU FIRIN SUTLAC`, hedef `ÜZÜMLÜ FIRIN SÜTLAÇ`, kayıtlı SFT çıktısı `ÜZÜMLÜ FİRİN SÜTLAC` olan `test:boun:pop_574:tam` örneği kullanılmıştır. Bu tek örnek `score` ile yeniden puanlanmış ve kayıtlı değerlerle aynı sonuç alınmıştır; test kümesi yeniden puanlanmamıştır.

| Metrik | Ne ölçer; pay / payda ve birim | Gerçek örnek | Yorum sınırı |
|---|---|---|---|
| Uyum | İzin verilen dönüşüm kuralını sağlayan cümle sayısı / tüm cümle sayısı. | 1/1 = %100; bütün değişimler izinlidir. | Hedefe uygunluğu ölçmez; yanlış fakat izinli bir dönüşüm de uyumludur. |
| Tam eşleşme | NFC sonrası çıktısı hedefle bütünüyle aynı olan cümle sayısı / tüm cümle sayısı. | 0/1 = %0. | Tek bir harf farkı bile cümleyi başarısız yapar; boşluk ve noktalama korunmalıdır. |
| Aday doğruluğu | Uyumlu cümlelerde hedefle eşleşen aday konum sayısı / tüm cümlelerde girdisi `cgiosuCGIOSU` kümesinde olan karakter konumu sayısı. | 5/8 = %62,50. | Değişmeden kalması gereken adayları da içerir; yalnız düzeltme başarısı değildir. |
| Gerekli düzeltme | Uyumlu cümlelerde hedefe doğru çevrilen gerekli konum sayısı / tüm cümlelerde girdi ile hedefin farklı olduğu karakter konumu sayısı. | 4/5 = %80; sondaki `C→Ç` eksiktir. | Gereksiz dönüşümleri doğrudan cezalandırmaz; aday doğruluğu ve U ile birlikte okunur. |
| U | Eşit uzunluklu çıktılarda girdi=hedef iken izinli bir dönüşümle değiştirilen karakterlerin toplam sayısı; oran değildir, paydası yoktur. | 2 karakter: `FIRIN` içindeki iki `I→İ`. | İzin dışı değişim U'ya eklenmez; ayrı kural ihlalidir. U tüm karakter hatalarının sayısı değildir. |
| W | Eşit uzunluklu çıktılarda hem girdiden hem hedeften farklı çıktı parçası bulunan girdi sözcüklerinin toplam sayısı; oran değildir, paydası yoktur. | 2 sözcük: `FİRİN` ve `SÜTLAC`. | Girdideki `\S+` aralıkları kullanılır; noktalama sözcüğe dahil olabilir. Hiç değişmeyen yanlış sözcük W'ye girmez; kısmen düzeltilmiş sözcük girebilir. |

U/W sayımı cümlenin uyumlu olmasını gerektirmez, eşit uzunluk yeterlidir. Eşit uzunluklu bir çıktının başka yerindeki kural ihlali U/W toplamlarını sıfırlamaz. U ve W örtüşebilir; ayrı hata türleriymiş gibi toplanmamalıdır.

### Repair ve fallback

[Repair kodu](../../scripts/analyze_sft_errors.py), NFC sonrası girdi ve çıktının Türkçe harfleri ASCII karşılıklarına katlanmış biçimlerini `SequenceMatcher(autojunk=False)` ile hizalar. Sonucu girdinin kopyasından başlatır ve yalnız katlanmış biçimde eşleşen bloklardaki aday konumlara, ham çıktıdaki izinli karakteri aktarır; diğer konumlar girdideki gibi kalır. Hedefe bakmaz, yeni model üretimi yapmaz ve dilsel doğruluğu garanti etmez.

Gerçek kayıt `test:boun:pop_228:kismi`: girdi `1 defne yapragı` için ham çıktı `1 defne yaprakığı` → repair çıktısı `1 defne yaprağı`; hedef de `1 defne yaprağı`dır. Bu dönüşüm yalnız bu örnekte `repair` çağrısıyla doğrulanmıştır. Fallback, ham çıktı kurala uyuyorsa onu, aksi halde girdinin tamamını döndürür; [uygulaması](score_and_report.py) ek dosyalardaki varyantın nasıl oluşturulduğunu gösterir.

### %95 güven aralığı

[Bootstrap uygulaması](score_and_report.py), aynı `source_id` veya `pair_id` ile doğrudan ya da geçişli bağlanan kayıtları [bağlantılı kümeler](../../deasciification/evaluation.py) halinde tutar. Kaynak varyantlarını veya minimal çift üyelerini bağımsız cümleler gibi örneklemek aralarındaki bağımlılığı bozacağı için yeniden örnekleme birimi kümedir; test kaydında 900 küme vardır. Her tekrarda mevcut küme sayısı kadar küme yerine koyarak çekilir; seçilen kümelerin payları/paydaları toplanarak oranlar, U/W için toplam sayılar hesaplanır. Kaynak/pair bağlantılı küme percentile bootstrap, 10.000 tekrar ve seed=42 kullanır; dağılımın 0,025 ve 0,975 nicelikleri %95 GA sınırlarıdır. U/W aralıkları oranların değil yeniden örneklenen küme toplamlarının aralıklarıdır.

Eşleştirilmiş karşılaştırma aynı örneklerde iki sistemin farkını ölçer ve ortak küme seçimlerini korur. Doğrulama ile test farklı örnek kümeleridir; aralarındaki fark eşleştirilmemiş betimsel farktır ve yukarıdaki eşleştirilmiş GA ona uygulanamaz.

## Doğrulama–test farkı

| Sistem | Uyum (yp) | Tam eşleşme (yp) | Aday (yp) | Gerekli (yp) |
|---|---:|---:|---:|---:|
| Eğitim öncesi | -1,44 | +0,78 | -0,43 | -0,03 |
| SFT | +0,00 | +4,89 | +0,73 | +1,32 |

SFT testte 544/900 tam doğru çıktı verdi (%60,44; %95 GA: %57,33–63,67). Doğrulamaya göre tam eşleşme +4,89 yüzde puan (yaklaşık +5 puan), gerekli düzeltme +1,32 yüzde puandır. Eşleştirilmemiş bu fark, test kümesinin daha kolay olması veya örnekleme/etiket gürültüsü olasılığıyla ilişkili olabilir; bu açıklamalar ayrıca sınanmadığından kanıtlanmış değildir. Fark sistem seçimini değiştirmek için kullanılmadı.

## Sınırlılıklar ve iddia sınırı

- Ham model çıktısı tek başına kural ihlalleri içerir (uyum %65,4) ve raporlanan başarı repair adımı dahil sistemin başarısıdır; ham çıktı ve fallback ayrıntıları [metrics.csv](metrics.csv) / [comparison.json](comparison.json) dosyalarındadır.
- Eğitim öncesi modele repair uygulanmadı; eğitimin ve repair'in katkısı bu raporda ayrıştırılmadı.
- Dış baseline (frekans, bigram veya kural tabanlı deasciifier) yoktur.
- Uyum, dilsel doğruluk garantisi değildir; aday doğruluğu korunması gereken konumları da içerir. U/W'nin uzunluk koşulu nedeniyle bu sayılar tek başına hata üstünlüğü göstermez.
- Bootstrap aralıkları bu örneklemdeki belirsizliği gösterir; eğitim tohumu, model seçimi veya alan değişimini kapsamaz. Doğrulama sistem seçiminde kullanılmıştır. Test artık bağımsız yeni seçimler için kullanılmamalıdır.
- **Ne iddia edebiliriz:** Önceden sabitlenen SFT sisteminin bu ayrılmış BOUN testindeki başarısı ve aynı örneklerde Eğitim öncesi sisteme göre farkları ölçülmüştür. SFT için elde edilen uyum ve doğruluk ayrı ölçütlerdir.
- **Ne iddia edemeyiz:** Her Türkçe metinde aynı başarı, tüm hataların düzelmesi, bütün veri sızıntısı türlerinin yokluğu, başka modellerden üstünlük veya tekrar eğitimlerde aynı sonuç garantisi; gözlenen farkın yalnız eğitime ait olduğu.

## Kayıtlar

[freeze-manifest.json](freeze-manifest.json) değişmeden korunan üretim öncesi anlık kayıttır; içindeki bekleyen onay durumu tarihseldir. Gerçek koşu durumu [generation-status.json](generation-status.json), başlangıç kilidi [generation-started.json](generation-started.json), son bütünlük denetimi [verification.json](verification.json) içindedir. Ham çıktılar [pre_zero_shot.jsonl](pre_zero_shot.jsonl) ve [sft_zero_shot.jsonl](sft_zero_shot.jsonl); tüm ölçülen varyantların çıktıları ve skorları `test-*-scores.json`; sayısal tablolar [metrics.csv](metrics.csv) ve [comparison.json](comparison.json) içindedir.

Ölçülen üretim süresi: temel model 15,01 dakika, SFT 15,83 dakika; toplam 30,84 dakika (model yükleme/puanlama hariç). Altyapı tekrarı: 0.

Bu belge düzenlemesinde sayısal artefaktlar ve dondurma kayıtları değiştirilmemiştir. `verification.json` içindeki belge özeti özgün rapora aittir; düzenlenen bu metnin özeti olarak yorumlanmamalıdır.
