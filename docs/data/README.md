# Türkçe veri hazırlama — BOUN v1

İlk kaynak, [UD Turkish BOUN](https://universaldependencies.org/treebanks/tr_boun/)
`r2.16`, commit `cfa62ac55a426d596700eceac436944e5cf0a967` sürümüdür.
TABILAB / Boğaziçi Üniversitesi tarafından Türkçe Ulusal Derlemi metinlerinden
hazırlanmıştır. Kaynak ve türetilmiş veri CC BY-SA 4.0 kapsamındadır; projenin
Apache lisansı bu verinin lisansını değiştirmez. Yazarlar, atıflar ve kaynak
lisansı çıktı klasöründeki `source/README.md` ve `source/LICENSE.txt` dosyalarında korunur.
Bu projedeki değişiklikler: cümle seçimi, NFC normalizasyonu, tekrar eleme,
yeniden bölümleme ve sentetik Türkçe karakter bozmasıdır.

## Üretim

Proje kökünden, Python standart kütüphanesiyle:

```bash
python3 -m scripts.download_data
python3 -m scripts.prepare_data --output data/prepared/boun-v1
python3 -m scripts.audit_data data/prepared/boun-v1
python3 -m unittest discover -s tests -v
```

İndirme adresleri ve SHA-256 özetleri `configs/data-source.json` içinde sabittir.
Önbellek dosyaları varsa tekrar indirilmeden doğrulanır. Yanlış özet, eksik veya
fazladan kaynak dosyası işlemi durdurur. Hazırlama komutu mevcut çıktı klasörünün
üzerine yazmaz; yeniden üretim için farklı bir klasör adı verin.

Yeni elle hazırlanmış testler varsa **üretimden önce** ekleyin:

```bash
python3 -m scripts.prepare_data --exclude data/manual-test.jsonl --output data/prepared/boun-v2
```

Ek dosyalar `input` ve `target` alanlarını içeren JSONL olmalıdır.
`data/pilot.jsonl` her durumda dışlama listesine alınır. Sonradan test eklenirse
eski veri sürümü otomatik olarak güvenli sayılmaz; yeniden üretim gerekir.

## Sabit kurallar

1. CoNLL-U dosyalarının `# text` alanı hedef metindir. Sözcüklerden yeniden metin
   birleştirilmez. `sent_id` ve özgün dosya adı saklanır; hedefte yalnız NFC uygulanır.
   10–500 karakter, en az üç boşlukla ayrılmış sözcük ve en az bir harf aranır.
   Unicode kontrol/format karakterleri ve U+0307 içeren cümleler dışlanır.
2. Karşılaştırma anahtarı Türkçe harfleri açık eşlemeyle ASCII'ye indirger,
   küçük harfe çevirir, noktalama ayırır ve boşlukları birleştirir. Bu işlem hedef
   metni değiştirmez. Karakter üçlülerinin **küme Jaccard benzerliği ≥0,80** olan
   kaynaklar birleştirilir. Birebir tekrarlar da buna dahildir. Geçişli bağlı
   bileşenin kaynak kimliğine göre ilk kaydı temsilci olur. Prefix indeksi aday
   aramasını hızlandırır; yaklaşık/olasılıksal eşleşme kullanılmaz.
3. Pilot/ek testin girdi ve hedefleriyle içerme, aynı Jaccard eşiği veya iki yönlü
   `SequenceMatcher` benzerliği ≥0,80 bulunan kaynağın **tüm tekrar grubu** dışlanır.
   `autojunk=False` kullanılır. Bu eleme üç bölümün tamamına uygulanır.
4. Temiz kaynaklar, bozulabilir harf sayısı 0 / 1 / ≥2 katmanlarında sabit tohumla
   %80 eğitim, %10 doğrulama, %10 test olarak ayrılır. Tam sayı sayımları en büyük
   kalan yöntemiyle dağıtılır. Özgün UD train/dev/test bölümleri birleştirilip bu
   görev için yeniden ayrılır; sonuçlar özgün UD test karşılaştırması değildir.
5. **Bölümleme bittikten sonra** her kaynaktan en fazla bir örnek üretilir.
   Her bölümde %60 tam, %25 kısmi ve %15 koruma oranını tam sağlayan en büyük
   mümkün 20 katı örnek sayısı seçilir. Kısmi bozma en az iki uygun harf gerektirir;
   her konum bağımsız %50 olasılıkla bozulur, boş/tam maskeler yeniden örneklenir.
   Mevcut Türkçe harfler, diğer harfler, noktalama ve biçim kuralları korunur.
6. Koruma kotasının en fazla yarısı Türkçe karakter dönüşümü gerektirmeyen
   kaynaklardan gelir; kaynak sayısı yetmezse kalan kota Türkçe karakterli
   kaynaklarla doldurulur. İki alt türden de en az bir örnek zorunludur.
   Yeterli kaynak yoksa işlem hata verir; oranlar sessizce değiştirilmez.

Tohum `20261015`; seçim ve sıralama kaynak kimliğiyle SHA-256 üzerinden yapılır.
Kısmi maskelerde kaynak başına ayrı Python RNG kullanılır; Python sürümü kaydedilir.
Aynı kaynak dosyaları, kod, Python sürümü ve tohumla çıktı dosyaları yeniden üretilebilir.

## Çıktılar ve denetim

- `splits/train.jsonl`, `splits/validation.jsonl`, `splits/test.jsonl`: `id`, `source_id`, `input`,
  `target`, `variant`, `category`, `split` ve kaynak bilgileri.
- `metadata/sources.jsonl`: temiz kaynakların **tam** bölüm atamaları; kota nedeniyle
  kullanılmayan cümleler de dahildir. Sonraki baseline sözlükleri yalnız eğitim
  bölümünden oluşturulmalıdır.
- `metadata/excluded.jsonl`: dışlanan kaynak kimliği, neden ve varsa tekrar temsilcisi.
- `manifest.json`: kaynak sürümü/özetleri, pilot ve ek test özetleri, kod özetleri,
  üretim kuralları, gerçek oranlar, alt tür sayıları ve çıktı dosyası özetleri.

Klasör ağacı ve kullanım rehberi: [data/prepared/README.md](../../data/prepared/README.md).
Yeni çıktılar manifest şeması 2 ile üretilir; denetim komutu eski düz şemayı da
okur. Mevcut BOUN v1 yalnızca yeniden düzenlenmiştir: veri içerikleri ve üretim
anındaki kod özetleri korunmuş, manifestte dosya yolları güncellenmiştir.

`audit_data` dosya özetlerini, kaynak ayrılığını, girdi-hedef dönüşümlerini,
karışımı, yakın tekrarları ve korunan testlerle örtüşmeyi denetler; hata durumunda
başarısız çıkış kodu verir. Üretilen dosyalar görev verisidir; eğitim sırasında
kaynak kimlikleri ve değerlendirme etiketleri modele verilmemelidir.

## Sınırlılıklar

BOUN ağırlıkla yazılı dil içerir; sohbet veya kullanıcı yazım alışkanlıklarını
tek başına temsil etmez. Kaynak metinler insan eliyle bu görev için tek tek
onaylanmış hedefler değildir. Semantik benzerliğin tüm biçimleri bu karakter
benzerliği filtresiyle saptanamaz. Bölümleme **cümle bazlıdır**, belge bazında
bağımsızlık iddiası yoktur. Kaynağın model ön eğitiminde bulunma ihtimali vardır.
Bu sentetik test, planlanan bağımsız günlük dil ve minimal çift testlerinin
yerine geçmez. SFT veya model başarısı sonucu bu veri üretiminden çıkarılmaz.

## İlk üretimin sayımları

9.761 kaynak → 9.184 temiz kaynak. Dışlamalar: 534 kalite, 28 tekrar,
15 pilot örtüşmesi. Bölüm atamaları: 7.347 eğitim, 919 doğrulama, 918 test kaynağı.
Kotalardan sonra 7.340 / 900 / 900 görev örneği üretildi; 44 kaynak kullanılmadı.
Eğitimde koruma alt türleri 859 Türkçe karakterli ve 242 dönüşüm gerektirmeyen;
doğrulama ve testin her birinde 105 ve 30'dur.

Bu sürümde her bölüm %60 tam, %25 kısmi, %15 koruma dağılımındadır. Testin bu
karışıma sahip olması bir tasarım tercihidir; gerçek kullanıcı dağılımı değildir.
