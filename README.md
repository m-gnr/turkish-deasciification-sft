# Türkçe karakter geri yükleme — SFT

Bu Doğal Dil İşlemeye Giriş dersi projesi, tek yönlü Türkçe karakter geri yükleme görevinde Eğitim öncesi Qwen/Qwen3-1.7B (zero-shot) ile SFT sistemini karşılaştırır. Görev yalnız `c/g/i/o/s/u → ç/ğ/ı/ö/ş/ü` ve `C/G/I/O/S/U → Ç/Ğ/İ/Ö/Ş/Ü` dönüşümlerine izin verir; mevcut Türkçe karakterler, diğer harfler, boşluklar ve noktalama korunur. Genel yazım düzeltme yapılmaz.

Bu projede 'SFT', SFT ile ince ayar yapılmış Qwen3-1.7B (first-lora-v1) ve çıktısına uygulanan kural tabanlı repair adımının birlikte oluşturduğu sistemi ifade eder. Ham model çıktısı (repair'siz) ve fallback varyantı ayrıca ölçülmüş olup ek dosyalarda bulunur.

BOUN v1 bölüm büyüklükleri: 7.340 eğitim, 900 doğrulama, 900 test örneği. Nihai sistem testten önce dondurulmuştur; sonuçlara göre seçim yapılmamıştır. Sistem zero-shot, greedy (`do_sample=False`), batch=8, max_new_tokens=256, MPS/float16 ve seed=0 ile çalışmıştır; parçalama yoktur. Eğitim seed=42, bootstrap seed=42; dondurulan commit `596d47dc70632c5b59f271b2d38712377fd66321`.

## Ana sonuçlar: test

Değerler [%95 GA] biçimindedir; ilk dört metrik yüzde, U/W toplam sayıdır.

| Metrik | Eğitim öncesi | SFT |
|---|---:|---:|
| Uyum (%) | 72,22 [69,33, 75,11] | 100,00 [100,00, 100,00] |
| Tam eşleşme (%) | 17,67 [15,22, 20,11] | 60,44 [57,33, 63,67] |
| Aday doğruluğu (%) | 50,13 [46,88, 53,42] | 95,66 [95,23, 96,07] |
| Gerekli düzeltme (%) | 10,70 [9,01, 12,51] | 88,52 [87,40, 89,61] |
| U | 7 [1,0, 14,0] | 161 [130,0, 193,0] |
| W | 152 [102,0, 218,0] | 264 [229,0, 301,0] |

U ve W yalnız NFC sonrası girdiyle eşit uzunluklu çıktılarda sayılır; farklı uzunlukta 0 yazılması hatasızlık değildir. Eğitim öncesi modelin düşük W'si kısmen bu sayım sınırından kaynaklanır.

Identity, girdiyi değiştirmeden döndüren aday doğruluğu tabanıdır: testte %70,31.

## Metrikler ve ölçüm yöntemi

Girdi `UZUMLU FIRIN SUTLAC`, hedef `ÜZÜMLÜ FIRIN SÜTLAÇ`, kayıtlı SFT çıktısı `ÜZÜMLÜ FİRİN SÜTLAC` olan `test:boun:pop_574:tam` örneği kullanılmıştır. Bu tek örnek `score` ile yeniden puanlanmış ve kayıtlı değerlerle aynı sonuç alınmıştır; test kümesi yeniden puanlanmamıştır.

| Metrik | Ne ölçer; pay / payda ve birim | Gerçek örnek | Yorum sınırı |
|---|---|---|---|
| Uyum | İzin verilen dönüşüm kuralını sağlayan cümle sayısı / tüm cümle sayısı. | 1/1 = %100; bütün değişimler izinlidir. | Hedefe uygunluğu ölçmez; yanlış fakat izinli bir dönüşüm de uyumludur. |
| Tam eşleşme | NFC sonrası çıktısı hedefle bütünüyle aynı olan cümle sayısı / tüm cümle sayısı. | 0/1 = %0. | Tek bir harf farkı bile cümleyi başarısız yapar; boşluk ve noktalama korunmalıdır. |
| Aday doğruluğu | Uyumlu cümlelerde hedefle eşleşen aday konum sayısı / tüm cümlelerde girdisi `cgiosuCGIOSU` kümesinde olan karakter konumu sayısı. | 5/8 = %62,50. | Değişmeden kalması gereken adayları da içerir; yalnız düzeltme başarısı değildir. |
| Gerekli düzeltme | Uyumlu cümlelerde hedefe doğru çevrilen gerekli konum sayısı / tüm cümlelerde girdi ile hedefin farklı olduğu karakter konumu sayısı. | 4/5 = %80; sondaki `C→Ç` eksiktir. | Gereksiz dönüşümleri doğrudan cezalandırmaz; aday doğruluğu ve U ile birlikte okunur. |
| U | Eşit uzunluklu çıktılarda girdi=hedef iken izinli bir dönüşümle değiştirilen karakterlerin toplam sayısı; oran değildir, paydası yoktur. | 2 karakter: `FIRIN` içindeki iki `I→İ`. | İzin dışı değişim U'ya eklenmez; ayrı kural ihlalidir. U tüm karakter hatalarının sayısı değildir. |
| W | Eşit uzunluklu çıktılarda hem girdiden hem hedeften farklı çıktı parçası bulunan girdi sözcüklerinin toplam sayısı; oran değildir, paydası yoktur. | 2 sözcük: `FİRİN` ve `SÜTLAC`. | Girdideki `\S+` aralıkları kullanılır; noktalama sözcüğe dahil olabilir. Hiç değişmeyen yanlış sözcük W'ye girmez; kısmen düzeltilmiş sözcük girebilir. |

Puanlama yalnız NFC normalleştirmesi yapar. Kural ihlali, çıktı uzunluğunun girdiden farklı olması veya bir konumda karakterin aynı kalma/izinli dönüşüm seçenekleri dışında değişmesidir. Bir ihlal, birincil karakter/sözcük başarı paylarını sıfırlar; paydalar kalır. Toplam oranlar payların toplamı / paydaların toplamıdır; sıfır payda N/A'dır. U/W oran değildir ve örtüşebilir; uyumsuz ama eşit uzunluklu çıktılarda da sayılır.

Repair, Türkçe harfleri ASCII'ye katlanmış girdi/çıktıyı hizalar; eşleşen bloklardaki izinli aday dönüşümlerini girdinin kopyasına aktarır, diğer konumları korur ve hedefe bakmaz. Gerçek örnek: `1 defne yapragı` girdisi için `1 defne yaprakığı` → `1 defne yaprağı`. Fallback, kurala uyan ham çıktıyı korur; ihlalde girdinin tamamını döndürür.

%95 GA, kaynak/pair bağlantılı küme percentile bootstrap ile 10.000 tekrar, seed=42 kullanılarak hesaplanır: kümeler yerine koyarak örneklenir, toplam pay/payda oranlarının (U/W için toplamların) 0,025 ve 0,975 nicelikleri alınır. Aynı kaynak ve minimal çift üyelerinin bağımlılığını korumak için cümle yerine küme örneklenir. Eşleştirilmiş fark aynı test örneklerinde, ortak küme seçimleriyle hesaplanır; doğrulama–test farkı farklı örnek kümelerine ait olduğundan eşleştirilmemiştir. [Nihai rapor](reports/final-test/README.md) kod bağlantılarını, doğrulama sütununu ve SFT − Eğitim öncesi eşleştirilmiş aralıklarını içerir.

## Sınırlılıklar

- Ham model çıktısı tek başına kural ihlalleri içerir (uyum %65,4) ve raporlanan başarı repair adımı dahil sistemin başarısıdır; ham çıktı ve fallback ayrıntıları [metrics.csv](reports/final-test/metrics.csv) / [comparison.json](reports/final-test/comparison.json) dosyalarındadır.
- Eğitim öncesi modele repair uygulanmadı; eğitimin ve repair'in katkısı ayrıştırılmadı. Dış baseline (frekans/bigram/kural tabanlı deasciifier) yoktur.
- Sonuçlar bu ayrılmış BOUN testine aittir; uyum dilsel doğruluk garantisi değildir. GA eğitim tohumu veya alan değişimini kapsamaz. Doğrulama seçimde kullanılmıştır; test yeni seçimler için kullanılmamalıdır.

## Tekrar üretim adımları

Aşağıdaki adımlar yöntem kaydıdır; bu belge düzenlemesinde eğitim, üretim ve toplu puanlama yeniden çalıştırılmadı.

1. [Dondurma kaydından](reports/final-test/freeze-manifest.json) commit, model revision, paket sürümleri, veri/adapter özetleri ve üretim ayarlarını alın. Kaynak veri UD Turkish BOUN r2.16'dır; veri lisansı CC BY-SA 4.0, yazılım lisansı Apache'dir.
2. Veri hazırlama için [veri rehberini](docs/data/README.md), eğitim için [LoRA rehberini](docs/first-sft.md) izleyin. Ayrı bir çalışma kopyasında ve yeni çıktı dizinlerinde kullanılabilecek komutlar:

   ```bash
   .venv/bin/python -m pip install -r requirements-training.txt
   .venv/bin/python -m scripts.download_model
   .venv/bin/python -m scripts.download_data
   .venv/bin/python -m scripts.prepare_data --output data/prepared/boun-rerun
   .venv/bin/python -m scripts.train_lora --output runs/another-lora
   .venv/bin/python -m scripts.evaluate_adapter --run runs/another-lora --output reports/sft-validation/another-lora
   ```

   Eğitim komutu varsayılan olarak sabit `data/prepared/boun-v1/splits/train.jsonl` dosyasını kullanır; yeni hazırlanan dizin otomatik seçilmez. Yeni eğitim, kaydedilmiş adapter'ın aynısını garanti etmez.
3. Nihai testin özgün üretim protokolü [generate_once.py](reports/final-test/generate_once.py), kayıtlı çıktıları puanlama ve bootstrap yöntemi [score_and_report.py](reports/final-test/score_and_report.py) içindedir. Üretim sürücüsü sabit dizin, commit denetimi ve tek geçiş kilidi kullanır; mevcut nihai test klasöründe tekrar çalıştırılacak genel bir komut değildir. Kayıtlı sonuçları incelemek için aşağıdaki artefaktları kullanın; bağımsız tekrar için mevcut kayıtları koruyan ayrı çalışma kopyası gerekir.

## Rapor ve artefaktlar

- [Nihai rapor](reports/final-test/README.md), [sayısal tablo](reports/final-test/metrics.csv), [karşılaştırma](reports/final-test/comparison.json), [test bootstrap aralıkları](reports/final-test/test-bootstrap.json).
- [Eğitim öncesi test puanları](reports/final-test/test-pre_zero_shot-scores.json), [SFT test puanları](reports/final-test/test-sft_zero_shot_repair-scores.json).
- [Dondurma kaydı](reports/final-test/freeze-manifest.json), [üretim durumu](reports/final-test/generation-status.json), [özgün bütünlük denetimi](reports/final-test/verification.json). Denetimdeki rapor özeti belge düzenlemesinden önceki sürüme aittir.
- [Veri manifesti](data/prepared/boun-v1/manifest.json), [veri klasör rehberi](data/prepared/README.md), [ölçüm planı](<docs/plans/Deasciification Projesi Ölçüm Planı ve Pilot Veri.md>).
