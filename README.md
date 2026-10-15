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
- Pilot ölçüm kodu ve hata analizi hazır; 13 otomatik kontrol geçti. Qwen3-1.7B modelinin sıfır örnekli tüm pilot değerlendirmesi tamamlandı. Büyük veri üretimi ve SFT eğitimi henüz tamamlanmadı.

Bu README deney tasarımını özetler; eğitim tamamlandığı veya başarı elde edildiği iddiası içermez. Yalnızca ana model eğitilirse koruma örneklerinin katkısı ayrı olarak kanıtlanmış sayılmaz.

## Pilot ölçümünü çalıştırma

Ölçüm aracı yalnızca Python standart kütüphanesini kullanır:

```bash
python3 validate_pilot.py data/pilot.jsonl
python3 -m unittest discover -s tests -v
python3 evaluate.py --identity --report reports/pilot-identity.json
python3 evaluate.py --predictions predictions.jsonl --report reports/pilot-model.json
```

Model tahminleri JSONL biçiminde `{"id":"p001","output":"ham model cevabı"}` kayıtlarıdır. Veriyle birebir aynı ID kümesi gerekir. Çıktılardaki boşluklar ve açıklamalar temizlenmeden kaydedilmelidir. `category`, `pair_id` ve sıfırdan başlayan `focus_word_index` değerlendirme etiketleridir; modele verilmez.

[Hiç-değiştirme pilot raporu](reports/pilot-identity.json): cümle tam eşleşmesi 4/34 (%11,76), belirsiz harf doğruluğu 165/260 (%63,46), gerekli düzeltme 0/95, katı uyum 34/34 ve doğru kelimeleri koruma 68/68. Minimal çift başarısı 0/4. Bunlar pilot ölçüm sonuçlarıdır; base veya SFT model sonucu değildir.

Rapor ham çıktıları, veri SHA-256 özetini, örnek/kategori düzeyinde metrikleri ve hata konumlarını içerir. Oranlar 0–1 aralığındadır; sıfır payda `null` (N/A) olarak verilir. Hata sayıları örtüşebilir. Bootstrap ve iki model arasında karşılaştırma bu ilk ölçüm aracında henüz uygulanmadı.

Her pilot kaydı `source_id` taşır. `p002/p028` ve `p017/p018/p031` ortak kaynak gruplarıdır; ikinci grup ortak metin parçası nedeniyle korumacı biçimde birleştirilmiştir. `p034`, `Ğ/Ö/Ş` büyük harf düzeltmelerini kapsar. Türetilen dağılım 26 tam, 4 kısmi ve 4 korumadır; pilot eğitim karışımı oranlarını temsil etmez.

Raporun `resampling_groups` alanı hem kaynak hem minimal çift bağlantılarının birleşiminden oluşur. Bootstrap henüz hesaplanmaz; alan gelecekte kullanılacak örnekleme birimlerini tanımlar. Kısmi bozma ölçümleri ayrıca 12 uygun konumun 4.094 farklı kısmi maskesiyle otomatik sınandı; bunlar eğitim veya pilot verisi değildir.

Önceki 33 kayıtlık sürümün gerçek dosya üzerinde doğrulanan sonucu 165/256 (%64,45) idi; [eski rapor](reports/pilot-identity-33.json) veri özeti ve kayıtlarıyla saklanır. Yeni sonuçtaki fark eklenen test örneğinden kaynaklanır, model değişiminden değil.

`validate_pilot.py`, sağlanan betiğin değiştirilmemiş kopyasıdır. Yakın kaynak uyarıları `source_id` atanmış olsa da gösterilir. Betik hata bulduğunda başarısız çıkış kodu üretmez; otomatik geçme/kalma kontrolü için yukarıdaki unittest komutu kullanılmalıdır.

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

[Ham cevaplar](reports/pilot-base-predictions.jsonl),
[çalıştırma ayarları](reports/pilot-base-predictions.metadata.json) ve
[ayrıntılı puanlama](reports/pilot-base.json) saklanır. Hiçbir örnek 128 yeni token sınırına ulaşmadı.
Bu küçük geliştirme pilotu, bağımsız nihai test değildir.

Yeniden çalıştırma (mevcut sonuçları korumak için yeni çıktı adı kullanın):

```bash
.venv/bin/python run_pilot.py --output reports/pilot-base-rerun.jsonl
.venv/bin/python evaluate.py --predictions reports/pilot-base-rerun.jsonl --report reports/pilot-base-rerun.json
```

`run_pilot.py` yalnızca yönerge ve girdiyi modele iletir; hedefler ve değerlendirme
etiketleri isteme eklenmez. Model revision'ı, yönerge, paket sürümleri, veri özeti,
ham cevaplar ve üretilen token kimlikleri kaydedilir. Mevcut çıktıların üzerine yazılmaz.
