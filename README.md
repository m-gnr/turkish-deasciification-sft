# turkish-deasciification-sft

Türkçe karakter geri yükleme için yönergeyle ince ayarın (SFT) bağlamsal doğruluğa, doğru metni korumaya ve yönerge uyumuna etkisini inceleyen Doğal Dil İşlemeye Giriş dersi projesi.

## Araştırma sorusu

SFT, küçük bir dil modelinin Türkçe karakterleri bağlama uygun biçimde geri getirmesini ve metnin geri kalanını korumasını ne kadar iyileştiriyor?

```text
her sabah ise gidiyor → her sabah işe gidiyor
yorgun ise dinlensin → yorgun ise dinlensin
yarin gelicem → yarın gelicem
```

Görev yalnızca izin verilen ASCII → Türkçe harf dönüşümleridir. Mevcut Türkçe karakterler, büyük/küçük harf düzeni, boşluk, noktalama, yazım hataları ve kısaltmalar korunur; açıklama eklenmez. Çift yönlü düzeltme ve genel yazım düzeltme kapsam dışındadır.

## Deney tasarımı

Ana SFT modelinin eğitim karışımı örnek sayısı üzerinden %60 tam ASCII, %25 kısmi ASCII ve %15 değişiklik gerektirmeyen metindir. Bu oranlar başlangıç tasarım tercihidir. Koruma örnekleri hem doğru Türkçe karakter içeren hem de Türkçe karakter gerektirmeyen metinleri kapsar.

Kısmi bozma, uygun Türkçe harf konumlarında bağımsız %50 olasılıkla uygulanır; en az bir konum bozulmalı ve en az biri korunmalıdır. Tekrarlar/yakın tekrarlar ele alınır, pilot ve elle hazırlanmış testler eğitimden dışlanır, kaynak cümleler **önce ayrılır, sonra bozulur**.

Karşılaştırmalar:

- Girdiyi hiç değiştirmeyen baseline.
- Temel model: sıfır örnekli ve 3–5 örnekli istem.
- Tam veri karışımıyla ana SFT modeli.
- Eğitim verisinden oluşturulan frekans ve bigram baseline'ları.
- Bütçe yeterse koruma örnekleri çıkarılmış SFT ablasyonu; toplam eğitim token bütçesi eşitlenerek.

## Değerlendirme

Ana metrikler **katı yönerge uyumu** ve **cümle tam eşleşmesi**dir. Gerekli düzeltme başarısı, doğru harf/kelime koruma oranı, belirsiz kelime doğruluğu ve minimal çift başarısı ayrıca raporlanır. Uyumsuz çıktılar ana metriklerde başarısız sayılır.

Hata analizi kural ihlali, eksik düzeltme, gereksiz düzeltme ve kelime düzeyinde yanlış düzeltmeyi kapsar. Son başlık diğerleriyle örtüşebilir; dört başlık ayrık sınıflar olarak toplanmaz.

Model farkları için eşleştirilmiş bootstrap güven aralıkları hesaplanır; minimal çiftler ve aynı kaynağın varyantları birlikte örneklenir. Bu aralıklar eğitim tohumları arasındaki değişkenliği kapsamaz.

## Plan ve mevcut durum

- [Ayrıntılı ölçüm planı ve pilot veri kararları](<docs/plans/Deasciification Projesi Ölçüm Planı ve Pilot Veri.md>) deney kurallarının ana kaynağıdır.
- [Pilot veri](data/pilot.jsonl) 34 kayıt içerir; üç `zaten_dogru` örneği ve dört minimal çift için `pair_id` / `focus_word_index` etiketleri eklendi.
- Pilot ölçüm kodu ve hata analizi hazır; 13 otomatik kontrol geçti. Qwen3-1.7B modelinin sıfır örnekli tüm pilot değerlendirmesi tamamlandı. BOUN v1 veri hazırlama hattı ve ilk eğitim/doğrulama/test dosyaları hazır; SFT eğitimi henüz yapılmadı.

Bu README deney tasarımını özetler; eğitim tamamlandığı veya başarı elde edildiği iddiası içermez. Yalnızca ana model eğitilirse koruma örneklerinin katkısı ayrı olarak kanıtlanmış sayılmaz.

## Dosya yapısı ve komutlar

```text
deasciification/          Ortak Python kodu
  config.py              Model adı, sabit sürüm ve yönerge
  inference.py           Model yükleme ve cevap üretme
  evaluation.py          Metrikler ve hata analizi
  validation.py          Veri doğrulama kuralları
scripts/                 Komut satırı girişleri
  download_model.py      Model indirme
  predict.py             Tek cümle denemesi
  run_pilot.py           Pilot üzerinde toplu tahmin
  evaluate.py            Tahminleri puanlama
  validate_data.py       Veriyi kontrol etme
data/                    Pilot veri
docs/plans/              Deney tasarımı
reports/single-example/  Tek cümle denemesi
reports/pilot-base/      SFT öncesi modelin tahmin, ayar ve puanları
reports/pilot-identity/  Hiç-değiştirme raporları (34 ve eski 33 örnek)
tests/                   Otomatik kontroller
```

Komutları **proje kökünden**, `python -m scripts.<komut>` biçiminde çalıştırın.
Model işlemleri için bağımlılıkların kurulu olduğu sanal ortamı kullanın:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m scripts.download_model
.venv/bin/python -m scripts.predict "yarin ise gidecegim."
```

Tek cümle komutu `reports/single-example/ilk-deneme.json` dosyasını günceller.
Pilot komutu mevcut sonuçların üzerine yazmaz; yeniden çalıştırırken yeni bir
çıktı adı seçin. İndirme ve çalıştırma aynı sabit model sürümünü kullanır.

Klasör düzenlemesinde eski raporların içerikleri korunmuştur. İçlerindeki kod
SHA-256 özetleri özgün çalıştırmaya aittir. Yeni pilot çalıştırmaları komut
betiğinin yanı sıra ortak model kodunun ve ayar dosyasının özetlerini de kaydeder.

## Pilot ölçümünü çalıştırma

Ölçüm aracı yalnızca Python standart kütüphanesini kullanır:

```bash
python3 -m scripts.validate_data data/pilot.jsonl
python3 -m unittest discover -s tests -v
python3 -m scripts.evaluate --identity --report reports/pilot-identity/pilot-identity.json
python3 -m scripts.evaluate --predictions predictions.jsonl --report reports/pilot-model/pilot-model.json
```

Model tahminleri JSONL biçiminde `{"id":"p001","output":"ham model cevabı"}` kayıtlarıdır. Veriyle birebir aynı ID kümesi gerekir. Çıktılardaki boşluklar ve açıklamalar temizlenmeden kaydedilmelidir. `category`, `pair_id` ve sıfırdan başlayan `focus_word_index` değerlendirme etiketleridir; modele verilmez.

[Hiç-değiştirme pilot raporu](reports/pilot-identity/pilot-identity.json): cümle tam eşleşmesi 4/34 (%11,76), belirsiz harf doğruluğu 165/260 (%63,46), gerekli düzeltme 0/95, katı uyum 34/34 ve doğru kelimeleri koruma 68/68. Minimal çift başarısı 0/4. Bunlar pilot ölçüm sonuçlarıdır; base veya SFT model sonucu değildir.

Rapor ham çıktıları, veri SHA-256 özetini, örnek/kategori düzeyinde metrikleri ve hata konumlarını içerir. Oranlar 0–1 aralığındadır; sıfır payda `null` (N/A) olarak verilir. Hata sayıları örtüşebilir. Bootstrap ve iki model arasında karşılaştırma bu ilk ölçüm aracında henüz uygulanmadı.

Her pilot kaydı `source_id` taşır. `p002/p028` ve `p017/p018/p031` ortak kaynak gruplarıdır; ikinci grup ortak metin parçası nedeniyle korumacı biçimde birleştirilmiştir. `p034`, `Ğ/Ö/Ş` büyük harf düzeltmelerini kapsar. Türetilen dağılım 26 tam, 4 kısmi ve 4 korumadır; pilot eğitim karışımı oranlarını temsil etmez.

Raporun `resampling_groups` alanı hem kaynak hem minimal çift bağlantılarının birleşiminden oluşur. Bootstrap henüz hesaplanmaz; alan gelecekte kullanılacak örnekleme birimlerini tanımlar. Kısmi bozma ölçümleri ayrıca 12 uygun konumun 4.094 farklı kısmi maskesiyle otomatik sınandı; bunlar eğitim veya pilot verisi değildir.

Önceki 33 kayıtlık sürümün gerçek dosya üzerinde doğrulanan sonucu 165/256 (%64,45) idi; [eski rapor](reports/pilot-identity/pilot-identity-33.json) veri özeti ve kayıtlarıyla saklanır. Yeni sonuçtaki fark eklenen test örneğinden kaynaklanır, model değişiminden değil.

Sağlanan doğrulayıcının kuralları `deasciification/validation.py` içinde, komut arayüzü `scripts/validate_data.py` içindedir. Yakın kaynak uyarıları `source_id` atanmış olsa da gösterilir. Betik hata bulduğunda başarısız çıkış kodu üretmez; otomatik geçme/kalma kontrolü için yukarıdaki unittest komutu kullanılmalıdır.

## Eğitim öncesi model: ilk pilot sonucu

Qwen3-1.7B, mevcut yönergeyle ve düşünme modu kapalı olarak 34 girdide çalıştırıldı.
Burada “base”, projeye özel SFT öncesindeki Qwen3-1.7B checkpoint'idir; ham ön eğitim modeli iddiası değildir.

| Ölçüm | Hiç değiştirme | SFT öncesi model |
| --- | --- | --- |
| Cümle tam eşleşmesi | 4/34 (%11,76) | 6/34 (%17,65) |
| Katı yönerge uyumu | 34/34 (%100) | 31/34 (%91,18) |
| Gerekli düzeltme başarısı | 0/95 (%0) | 8/95 (%8,42) |
| Doğru kelimeleri koruma | 68/68 (%100) | 56/68 (%82,35) |
| Aday harf doğruluğu | 165/260 (%63,46) | 149/260 (%57,31) |
| Minimal çift başarısı | 0/4 | 0/4 |

Uyumsuz cevapların ilgili tüm birimleri ana metriklerde başarısız sayılır. Bu yüzden
8/95, ham çıktıda görülen bütün doğru harf değişimlerinin sayısı değildir; katı ölçümün sonucudur.
Aynı şekilde 56/68, doğrudan bozulmuş kelime sayısından türetilen bir oran değildir.
Model dört değişiklik gerektirmeyen girdiyi korudu; düzeltme gerektiren 30 cümlenin
ikisini tam doğru yaptı. Henüz SFT sonucu veya istatistiksel üstünlük iddiası yoktur.

Örnekler:

- `Google uzerinden arama yaptim.` → `Google üzerinden arama yaptım.`: tam doğru.
- `bugun hava cok guzel.` → `bugun hava çok güzel.`: `bugun` eksik kaldı.
- `her sabah ise gidiyor` → aynı metin: bağlamın gerektirdiği `işe` düzeltmesi yapılmadı.
- `p029` ve `p030`: boşluk/sekme düzeni değişti; `p015`: kelime yapısı bozuldu.

[Ham cevaplar](reports/pilot-base/pilot-base-predictions.jsonl),
[çalıştırma ayarları](reports/pilot-base/pilot-base-predictions.metadata.json) ve
[ayrıntılı puanlama](reports/pilot-base/pilot-base.json) saklanır. Hiçbir örnek 128 yeni token sınırına ulaşmadı.
Bu küçük geliştirme pilotu, bağımsız nihai test değildir.

Yeniden çalıştırma (mevcut sonuçları korumak için yeni çıktı adı kullanın):

```bash
.venv/bin/python -m scripts.run_pilot --output reports/pilot-base/pilot-base-rerun.jsonl
.venv/bin/python -m scripts.evaluate --predictions reports/pilot-base/pilot-base-rerun.jsonl --report reports/pilot-base/pilot-base-rerun.json
```

`scripts/run_pilot.py` yalnızca yönerge ve girdiyi modele iletir; hedefler ve değerlendirme
etiketleri isteme eklenmez. Model revision'ı, yönerge, paket sürümleri, veri özeti,
ham cevaplar ve üretilen token kimlikleri kaydedilir. Mevcut çıktıların üzerine yazılmaz.

## Eğitim verisi: BOUN v1

[Veri hazırlama kuralları ve komutları](docs/data/README.md) ile ilk veri sürümü hazır.
Kaynak UD Turkish BOUN r2.16; kaynak sürümü ve dosya özetleri
[configs/data-source.json](configs/data-source.json) içinde sabitlendi.
Kaynak/türetilmiş veri CC BY-SA 4.0 lisanslıdır; yazılımın Apache lisansından ayrıdır.

### Veriyi nereden, kaç tane ve nasıl aldık?

Veri, [Universal Dependencies / UD Turkish BOUN GitHub deposundan](https://github.com/UniversalDependencies/UD_Turkish-BOUN/tree/cfa62ac55a426d596700eceac436944e5cf0a967)
alındı. BOUN, Boğaziçi Üniversitesi TABILAB tarafından Türkçe Ulusal Derlemi
(TNC) metinlerinden hazırlanmış bir derlemdir. Bu projede TNC sitesi taranmadı;
BOUN deposundaki hazır CoNLL-U dosyaları indirildi.

| İndirilen özgün dosya | Kaynak cümle sayısı |
| --- | ---: |
| `tr_boun-ud-train.conllu` | 7.803 |
| `tr_boun-ud-dev.conllu` | 979 |
| `tr_boun-ud-test.conllu` | 979 |
| **Toplam** | **9.761** |

Sayılar indirilen dosyalardaki `# sent_id` kayıtlarından doğrulandı.
Üç veri dosyasının tamamı ve kaynak `README.md` / `LICENSE.txt` dosyaları,
`r2.16` sürümünün `cfa62ac55a426d596700eceac436944e5cf0a967` commit'ine
sabitlenmiş ham GitHub adreslerinden HTTPS ile alındı; rastgele bir internet
örneklemesi yapılmadı. İlk indirmede yerel DNS sorunu nedeniyle `curl` ile
adres çözümlemesi belirtildi; TLS doğrulaması açık kaldı. İndirilen veri dosyaları
GitHub'daki sabit Git blob kimlikleriyle de karşılaştırıldı.

Tekrar indirme için `python3 -m scripts.download_data` kullanılır. Bu betik
Python standart kütüphanesiyle dosyaları `data/raw/boun/` klasörüne indirir ve
`configs/data-source.json` içindeki SHA-256 özetleriyle doğrular; mevcut önbellek
varsa yalnızca doğrular. Hazırlama betiği her kaydın `# text` alanını hedef cümle,
`# sent_id` alanını kaynak kimliği olarak okur. Ayrıştırma etiketleri modele
verilmez, sözcükler yeniden birleştirilmez.

Özgün train/dev/test dosyaları birleştirildi; tekrar ve pilot örtüşmesi
ayıklamasından sonra bu proje için kaynak cümle bazında yeniden bölündü.
Dolayısıyla aşağıdaki bölüm sayıları özgün BOUN bölüm sayılarından farklıdır.

### Hazırlanan görev verisi

| Bölüm | Tam ASCII | Kısmi ASCII | Koruma | Toplam |
| --- | ---: | ---: | ---: | ---: |
| Eğitim | 4.404 | 1.835 | 1.101 | 7.340 |
| Doğrulama | 540 | 225 | 135 | 900 |
| Test | 540 | 225 | 135 | 900 |

9.761 kaynak cümlenin 534'ü kalite filtresi, 28'i tekrar, 15'i pilot örtüşmesi
nedeniyle dışlandı. Kalan 9.184 kaynak cümle önce %80/%10/%10 bölündü; sonra
her bölümde tam %60/%25/%15 karışım üretildi. Kota için 44 kaynak kullanılmadı.
Her bölümde iki koruma alt türü de var. Kaynak ve pilot ayrılığı tanımlanan
benzerlik kuralları altında denetlenir; belge/semantik bağımsızlık iddiası yoktur.

```bash
python3 -m scripts.download_data
python3 -m scripts.prepare_data --output data/prepared/boun-v1
python3 -m scripts.audit_data data/prepared/boun-v1
```

Mevcut çıktı klasörüne yeniden yazılmaz; tekrar üretim için yeni ad kullanın.
[Üretim raporu](data/prepared/boun-v1/manifest.json), kaynak atamaları ve dışlama
kayıtları verinin yanında tutulur. Eğitim dosyaları `splits/`, denetim kayıtları
`metadata/`, lisans ve kaynak açıklaması `source/` altındadır;
[klasör rehberi](data/prepared/README.md) dosyaların rollerini açıklar. Veri hazırlama için yedi yeni testle toplam
20 otomatik kontrol vardır. Sıradaki aşama eğitim örneklerinin içerik kontrolü,
birkaç örnekli istem karşılaştırması ve küçük SFT denemesidir.

## Doğrulamada sıfır ve beş örnekli istem karşılaştırması

`python -m scripts.compare_prompts --output <yeni-klasör>` doğrulama kümesinin
tamamında aynı sabit model/yönerge/üretim ayarlarıyla iki koşulu ölçer. Beş örnek
yalnızca eğitimden deterministik olarak seçilir (3 tam, 1 kısmi, 1 koruma) ve
bütün doğrulama girdilerinde aynı sırayla kullanılır. Test kümesi açılmaz.
Ham çıktılar, örnek kimlikleri, veri/kod özetleri, kategori puanları ve
kaynak/minimal çift grupları üzerinden 2.000 tekrarlı eşleştirilmiş bootstrap
fark aralıkları kaydedilir. Bu aralıklar istem örneği seçiminin değişkenliğini
kapsamaz. `scripts.report_prompt_comparison` tamamlanan koşunun okunabilir
raporunu üretir. Mevcut çıktı klasörüne yazılmaz.

```bash
.venv/bin/python -m scripts.compare_prompts --output reports/validation-prompts/boun-v1-rerun
.venv/bin/python -m scripts.report_prompt_comparison reports/validation-prompts/boun-v1-rerun
```
