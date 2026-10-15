# Deasciification Projesi: Ölçüm Planı ve Pilot Veri

Doğal Dil İşlemeye Giriş dersi için Türkçe karakter geri yükleme projesi. Bu belge deney tasarımını tanımlar; planlanan çalışmalar tamamlanmış sonuçlar olarak sunulmaz.

## Araştırma sorusu

Yönergeyle ince ayar (SFT), küçük bir dil modelinin Türkçe karakterleri bağlama uygun biçimde geri getirmesini ve metnin geri kalanını korumasını ne kadar iyileştiriyor?

Üç ayrı boyut ölçülür:

- **Düzeltme doğruluğu:** Değişmesi gereken harfler doğru düzeltildi mi?
- **Doğruyu koruma:** Başlangıçta doğru olan harfler ve kelimeler korundu mu?
- **Yönerge uyumu:** Yalnızca izin verilen değişiklikler mi yapıldı?

## Görevin kapsamı ve dönüşüm kuralları

Görev tek yönlü Türkçe karakter geri yüklemedir. LSTM mimarisini yeniden kurmak, çift yönlü diakritik düzeltme ve genel yazım düzeltme kapsam dışındadır. Girdideki Türkçe karakterler, büyük/küçük harf düzeni, boşluklar, noktalama, sayılar ve diğer içerik korunur. Açıklama eklenmez. Yazım hataları ve kısaltmalar hedefte düzeltilmez: `yarin gelicem` → `yarın gelicem`.

Uyum kontrolü konum bazlıdır:

| Girdi | İzin verilen çıktı |
| --- | --- |
| c / C | c, ç / C, Ç |
| g / G | g, ğ / G, Ğ |
| i | i, ı |
| I | I, İ |
| o / O | o, ö / O, Ö |
| s / S | s, ş / S, Ş |
| u / U | u, ü / U, Ü |
| Diğer her karakter | Aynen aynı |

Ham çıktı saklanır. Karşılaştırma öncesinde yalnızca NFC Unicode normalizasyonu uygulanır; boşluk temizleme, küçük harfe çevirme veya açıklama ayıklama yapılmaz. NFC sonrasında çıktı ve girdi uzunlukları aynı olmalıdır. Baştaki/sondaki boşlukları temizleyen yumuşak uyum ölçümü ancak ikincil olarak verilebilir.

Python `.lower()` / `.upper()` yerine `I/İ` ve `ı/i` için açık eşleme kullanılır. `ş → s` kural ihlalidir. `Google` içindeki `o → ö` izinli olsa da hedefe göre yanlıştır; uyum doğruluk anlamına gelmez.

## Eğitim verisi

Ana modelin başlangıç karışımı örnek sayısı üzerinden şöyledir. Oranlar deneysel olarak kanıtlanmış optimum değerler değil, tasarım tercihleridir.

| Tür | Pay | Amaç |
| --- | --- | --- |
| Tam ASCII dönüşümü | %60 | Temel geri yükleme görevini öğrenmek |
| Kısmi ASCII dönüşümü | %25 | Türkçe ve ASCII harflerin karıştığı girdileri işlemek |
| Değişiklik gerektirmeyen örnekler | %15 | Gereksiz müdahaleyi azaltmak |

İlk iki türde en az bir gerçek değişiklik bulunmalıdır. Koruma örnekleri iki alt türü de içermelidir: zaten doğru Türkçe karakter içeren metin ve Türkçe karakter gerektirmeyen doğru metin. Alt türlerin gerçekleşen sayıları raporlanır; yalnızca bir tür kullanılmaz.

| Tür | Girdi | Hedef |
| --- | --- | --- |
| Tam ASCII | ogrenci kartini unutmusum | öğrenci kartını unutmuşum |
| Kısmi ASCII | ögrenci kartını unutmusum | öğrenci kartını unutmuşum |
| Doğru Türkçe | öğrenci kartını unutmuşum | öğrenci kartını unutmuşum |
| Türkçe karakter gerektirmeyen | yorgun ise dinlensin | yorgun ise dinlensin |

### Bozma algoritması

Yalnızca `ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u` ve büyük harf karşılıkları `Ç→C, Ğ→G, İ→I, Ö→O, Ş→S, Ü→U` uygulanır. Genel transliterasyon veya harf küçültme kullanılmaz; diğer karakterler aynen kalır.

- **Tam bozma:** Uygun konumların tamamı dönüştürülür.
- **Kısmi bozma:** Uygun her karakter konumu bağımsız olarak %50 olasılıkla dönüştürülür. Cümlede en az bir uygun konum bozulmalı ve en az biri korunmalıdır. Koşul sağlanmazsa maske yeniden örneklenir; ikiden az uygun konumu olan cümle bu kategoriye alınmaz. Kabul edilen maskeler bu koşula bağlı olduğundan nihai dağılım koşulludur; kelime başına sabit oran uygulanmaz.
- **Koruma:** Girdi hedefle aynıdır.

Üretim kodunda eşleme, olasılık, yeniden örnekleme kuralı ve rastgelelik tohumu açıkça kaydedilir. Kaynak cümle kimliği, varyant türü ve üretim ayarları izlenebilir olmalıdır. Test varyantları bir kez üretilip sabitlenir.

## Veri sızıntısı kontrolü

1. Derlemde birebir tekrarlar temizlenir. Yakın tekrarlar için yöntem ve eşik, test sonuçlarına bakılmadan belirlenip kaydedilir; tespit edilen gruplardan temsilci seçilir veya grubun tamamı tek bölümde tutulur.
2. Pilot ve elle hazırlanmış test cümleleri ile bunların birebir/yakın kopyaları eğitim ve eğitimde kullanılan doğrulama verisinden hariç tutulur.
3. Kaynak cümleler eğitim, doğrulama ve test olarak ayrılır; **bozma bundan sonra yapılır**. Aynı kaynağın tüm varyantları aynı bölümde kalır.
4. Frekans sözlüğü ve bigram istatistikleri yalnızca eğitim bölümünden çıkarılır. İstem örnekleri testten alınmaz.
5. Test, eğitim veya hiperparametre seçimi için kullanılmaz. Pilot geliştirme amaçlıdır; bağımsız nihai test gibi raporlanmaz.

Temel modelin ön eğitiminde derlem metinlerini görmüş olma ihtimali tamamen dışlanamaz. Yeni/elle hazırlanmış testler bu riski azaltabilir, ortadan kaldırdığını kanıtlamaz.

## Karşılaştırılacak koşullar

| Koşul | Açıklama |
| --- | --- |
| Hiç değiştirme baseline'ı | Girdiyi aynen döndürür; koruma ile düzeltme arasındaki farkı görünür kılar |
| Temel model, sıfır örnekli | Yalnızca yönerge |
| Temel model, birkaç örnekli | Yönerge + sabit 3–5 örnek |
| Ana SFT modeli | %60 / %25 / %15 karışımıyla eğitim, sıfır örnekli değerlendirme |
| Koruma örnekleri çıkarılmış SFT ablasyonu | Zaman/bütçe yeterse; koruma bileşeninin katkısını sınar |
| Frekans baseline'ı | Eğitim sözlüğündeki en olası karşılık |
| Bigram baseline'ı | Önceki kelimeyi kullanan basit bağlam modeli |

### Ablasyon ve eğitim bütçesi

Ana model tam karışımdır; ablasyon bu karışımdan koruma örneklerinin çıkarılmasıdır. İki koşulda aynı düzeltme örneği havuzu kullanılır. Ana modele bu havuzun üzerine koruma örnekleri eklenerek hedef karışım oluşturulur; ablasyonda tam/kısmi düzeltme oranı 60:25 olarak korunur.

Aynı temel model, tokenizer, yönerge, değerlendirme/üretim ayarları ve mümkün olduğunca aynı eğitim ayarları kullanılır. Toplam eğitim token bütçesi eşitlenir; padding hariç hangi tokenların bütçeye sayıldığı, kaybın hangi tokenlarda hesaplandığı ve gerçekleşen token sayıları kaydedilir. Eşit epoch sayısı, eşit token bütçesi sayılmaz.

Koruma eklemek ve token bütçesini eşitlemek, düzeltme örneklerine maruz kalma sayısını değiştirebilir. Bu sayılar da raporlanır; deney sabit bütçede veri karışımının etkisini ölçer, yalnızca koruma içeriğinin bütünüyle yalıtılmış etkisini kanıtlamaz.

Zaman yetmezse yalnızca ana SFT modeli eğitilir; koruma örneklerinin nedensel katkısı kanıtlanmış gibi sunulmaz.

## Test kümeleri

1. **Sentetik test:** Ayrılmış kaynaklardan tam ve kısmi bozma; sonuçlar tür bazında da verilir.
2. **Bağlam ve minimal çift testi:** Aynı belirsiz kelimenin farklı cevap gerektirdiği cümle çiftleri.
3. **Elle hazırlanmış günlük dil testi:** Yazım hatası, kısaltma, yabancı kelime ve biçim öğeleri; görev dışı hatalar hedefte korunur. Gerçek kullanıcı verisi diye sunulmaz.
4. **Zaten doğru testi:** Her iki koruma alt türü; belirsiz doğru kelimeler ayrıca etiketlenir.
5. **Gerçekten belirsiz küçük küme:** Birden fazla kabul edilen tam hedefle ayrı değerlendirme. Ana tek-hedefli teste karıştırılmaz; belirsizlikten hareketle otomatik bir başarı tavanı iddia edilmez.

Test dağılımının eğitimdeki %60 / %25 / %15 oranlarına uyması gerekmez. Her alt kümenin örnek sayısı ve genel sonuç hesaplanırken kullanılan ağırlıklar açıklanır.

## Ölçüm planı

Ana metrikler katı uyum ve cümle tam eşleşmesidir. Koruma, düzeltme ve bağlam ölçümleri bunlarla birlikte raporlanır; tek bir harf doğruluğu yeterli değildir.

| Metrik | Hesaplama |
| --- | --- |
| Katı uyum oranı | Kurallara uyan çıktı sayısı / tüm örnekler |
| Cümle tam eşleşmesi | Hedefle tam eşleşen çıktı sayısı / tüm örnekler; uyumsuz çıktı başarısız |
| Belirsiz harf doğruluğu, tüm örnekler | Girdideki `c,g,i,o,s,u` ve büyük karşılıklarında doğru tahmin / bu konumların toplamı; uyumsuz örneğin tüm ilgili konumları başarısız |
| Belirsiz harf doğruluğu, yalnız uyumlular | İkincil ölçüm; uygun örnek ve konum sayılarıyla birlikte |
| Gerekli düzeltme başarısı | Girdi ile hedefin farklı olduğu konumlarda doğru çıktı / değişmesi gereken konumlar; uyumsuz örneklerde ilgili konumlar başarısız |
| Doğru harfleri koruma | Girdi ile hedefin aynı olduğu konumlarda korunmuş karakter / bu konumların toplamı |
| Doğru kelimeleri koruma | Girdi ile hedefte aynı olan kelimelerden aynen korunanlar / bu kelimelerin toplamı |
| Belirsiz kelime doğruluğu | Önceden etiketlenmiş belirsiz hedef kelimelerde tam doğru tahmin oranı |
| Minimal çift başarısı | Her iki cümlesi de tam doğru olan çift sayısı / tüm çiftler |

Koruma oranları belirsiz kelimelerde ayrıca verilir. Tüm değişmemesi gereken karakterlerin yanında, kolay karakterlerin oranı şişirmemesi için izinli dönüşüm adayı olup hedefte değişmeyen harfler de ayrı raporlanır. Kelime sınırları, girdi üzerinde sabitlenen boşluk temelli aralıklarla belirlenir; noktalama korunur.

Ana koruma ve kelime ölçümlerinde uyumsuz örneğin ilgili birimleri başarısız sayılır. Yalnız uyumlulardaki oranlar ikincil olarak, kapsanan örnek/birim sayısıyla verilebilir. Böylece uyumsuz çıktılar sessizce paydadan çıkarılmaz. Paydası sıfır olan ölçüm `N/A` ve `n=0` olarak verilir.

## Hata analizi

Dört başlık raporlanır; bunlar aynı düzeyde, birbirini dışlayan dört sınıf değildir:

| Hata başlığı | Düzey ve tanım | Örnek |
| --- | --- | --- |
| Kural ihlali | Çıktı düzeyinde izinli olmayan değişiklik; hizalama mümkünse konumları da kaydedilir | `ş→s`, kelime atma, açıklama ekleme |
| Eksik düzeltme | Karakter düzeyinde değişmesi gereken harfin aynı kalması | Hedef `çok`, çıktı `cok` |
| Gereksiz düzeltme | Karakter düzeyinde hedefte aynı kalması gereken harfin izinli fakat yanlış değiştirilmesi | `yorgun ise` → `yorgun işe` |
| Yanlış düzeltme | Kelime değişmiş fakat hedefe ulaşmamış; diğer başlıklarla örtüşebilen kelime düzeyi ölçüm | Girdi `ise`, hedef `işe`, çıktı `ışe` |

Son örnekte `s→ş` doğrudur, `i→ı` gereksiz düzeltmedir. Her aday karakterin yalnızca iki izinli çıktısı olduğundan, değişmesi gereken bir karakterin izinli biçimde değişip üçüncü bir yanlış seçeneğe gitmesi mümkün değildir.

Uzunluğu değişen veya açıklama içeren çıktılarda zorla karakter hizalaması yapılmaz. Bunlar kural ihlali ve ana metriklerde başarısızlık olarak kaydedilir; karakter/kelime hata dökümünde hizalanamayan örnek sayısı ayrıca gösterilir. Hata sayıları toplanarak tek bir ayrık toplam elde edilmeye çalışılmaz.

Hatalar harf çifti, belirsiz kelime, özel isim/yabancı kelime, büyük harf ve test türü bazında incelenir. Her oranla birlikte pay ve payda verilir.

## Belirsizlik ve güven aralıkları

Modeller arasındaki metrik farkları için eşleştirilmiş bootstrap kullanılır: aynı örnek/grup örneklemesi iki modele de uygulanır. Başlangıç ayarı sabit tohumla 2.000 tekrar ve %95 yüzdelik güven aralığıdır; her tekrarda metrikler pay ve paydalarından yeniden hesaplanır.

Minimal çiftler birlikte örneklenir. Aynı kaynak cümlenin birden fazla test varyantı varsa bunlar da aynı grupta tutulur. Farklı test türleri ayrı raporlanır; birleşik ölçümde tür ağırlıkları sabit tutulur.

Bu aralıklar sabit eğitilmiş modeller için test örneklemesi belirsizliğini gösterir; eğitim rastgeleliğini ölçmez. Zaman varsa 2–3 eğitim tohumu kullanılır ve tohumlar arası değişkenlik ayrıca raporlanır. Küçük farklar veya sıfırı içeren fark aralıkları kesin üstünlük olarak yorumlanmaz.

## Pilot veri ve ilk teslim noktası

Mevcut `data/pilot.jsonl` 34 kayıt içeriyor. İlk 30 kaydın girdi ve hedefleri korundu; `zaten_dogru` kategorisinde üç kayıt eklendi. Dört minimal çifte `pair_id` ve sıfırdan başlayan `focus_word_index` alanları eklendi. Bunlar değerlendirme metadatasıdır; eğitim hedefi metnin kendisidir.

Eklenen kayıtlar:

| Alt tür | Girdi ve hedef (aynı) |
| --- | --- |
| Doğru Türkçe | öğrenci kartını unutmuşum |
| Doğru Türkçe ve biçim | Bugün öğle yemeği çok güzeldi. |
| Türkçe karakter gerektirmeyen | herkes evde beklesin |

Mevcut bağlam testindeki `yorgun ise dinlensin` gibi doğru belirsiz örnekler ayrıca koruma analizine katılır. Kategoriler ile analiz etiketleri farklı amaçlara hizmet edebilir.

Pilotun amacı ölçüm kodunun ve görev kurallarının boşluklarını bulmaktır; nihai genelleme başarısını ölçmek değildir. Genişletilmiş 34 kayıt üzerinde `scripts/evaluate.py` ile hiç-değiştirme baseline'ı yeniden ölçüldü: aday harf doğruluğu 165/260 (%63,46), cümle tam eşleşmesi 4/34 (%11,76), gerekli düzeltme başarısı 0/95, katı uyum 34/34, doğru kelime koruma 68/68, minimal çift başarısı 0/4. Sonuçlar `reports/pilot-identity/pilot-identity.json` içinde veri SHA-256 özetiyle kayıtlıdır; önceki 30 kayıtlık pilotla aynı veri sürümü değildir. Mümkünse 10 kayıt bağımsız bir kişi tarafından kontrol edilir.

Ölçüm kodu; doğru çıktı, eksik/gereksiz düzeltme, mevcut Türkçe harfin bozulması, uzunluk değişimi, açıklama ekleme, `I/İ`, Unicode ve sıfır payda durumlarıyla doğrulanır.

## Literatür bağlantısı ve sınırlılıklar

[Diacritics correction in Turkish with context-aware sequence to sequence modeling (2022)](https://doi.org/10.55730/1300-0632.3948), bağlamın katkısını ve doğru kelimeleri bozmamayı ayrı incelemek için dayanak oluşturur. Bu projeye aktarılan fikirler değerlendirme tasarımı ve koruma örnekleridir; makalenin LSTM mimarisi ve çift yönlü görevi aktarılmaz. Veri, görev ve metrik farklılıkları nedeniyle makaledeki F1 değerleriyle doğrudan üstünlük karşılaştırması yapılmaz.

Sentetik bozma gerçek yazım alışkanlıklarını tam temsil etmez. Tek model ve tek eğitim çalıştırması genelleme iddialarını sınırlar. Veri oranları ve beklenen iyileşmeler hipotez/tasarım kararıdır; rapora yalnızca doğrulanmış deney sonuçları bulgu olarak yazılır.

## Uygulama sırası

1. **Tamamlandı:** Pilota üç `zaten_dogru` örneği ve minimal çift etiketleri eklendi; hedefler dönüşüm kurallarına göre doğrulandı.
2. **Tamamlandı:** `scripts/evaluate.py` ile metrikler ve hiç-değiştirme baseline'ı hesaplandı.
3. **Tamamlandı:** Hata analizi, Unicode, biçim koruma, sıfır payda ve minimal çift hesaplamaları dahil 13 otomatik kontrol geçti (`tests/test_evaluate.py`).
4. **Tamamlandı (BOUN v1):** Tekrar/pilot örtüşme kontrolü, kaynak cümle bazlı ayrım ve sabit tohumla veri üretimi. Ayrıntılar `docs/data/README.md`; 7.340 eğitim, 900 doğrulama, 900 test örneği. Yeni elle hazırlanmış testler eklendiğinde dışlama listesiyle yeniden üretim gerekir.
5. Baseline'ları ve ana SFT modelini aynı sabit test düzeninde değerlendir.
6. Bütçe varsa korumasız ablasyonu ve birden fazla eğitim tohumunu çalıştır.
7. Eşleştirilmiş bootstrap fark aralıklarını, hata türlerini ve sınırlılıkları raporla.

## Pilot doğrulama güncellemesi

Sağlanan `validate_pilot.py` betiği önce gerçek 33 kayıtlık dosyada çalıştırıldı: NFC ve U+0307 hatası yoktu; 165/256 sonucu doğrulandı. Bu sürümün raporu `reports/pilot-identity/pilot-identity-33.json` içinde saklandı. Ardından şu değişiklikler yapıldı:

- Tüm kayıtlara `source_id` eklendi. `p002/p028` aynı kimliği, `p017/p018/p031` başka bir ortak kimliği paylaşır. `p017` daha kısa bir ifade olduğundan ikinci grup kesin kaynak eşitliği iddiası değil, ortak parça nedeniyle korumacı gruplamadır.
- `p034`: `OGRETMEN SEHIRDE` → `ÖĞRETMEN ŞEHİRDE` eklendi. On iki Türkçe harfin tamamı artık gerekli düzeltme kapsamında bulunur.
- Güncel dağılım 26 tam, 4 kısmi, 4 korumadır. Gerçek dosya NFC, U+0307, dönüşüm ve minimal çift kontrollerinden hatasız geçti.
- Örnekleme grupları hem `source_id` hem `pair_id` bağlantılarının geçişli birleşimidir; raporda saklanır. Bootstrap güven aralığı henüz uygulanmadı.
- Ölçüm kodu, 12 uygun konumun tüm 4.094 kısmi maskesinde doğru çıktı ve hiç-değiştirme çıktısıyla sınandı. Bu yapay test dizileri pilot veya eğitim örnekleri değildir.
- Yeni rapor hem veri hem ölçüm kodunun SHA-256 özetini içerir. Önceki ve yeni pilot oranları farklı veri sürümlerine aittir.

## SFT öncesi pilot çalıştırması

Qwen3-1.7B revision `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` ile 34 girdinin
sıfır örnekli değerlendirmesi tamamlandı. Mevcut `deasciification/config.py` yönergesi, greedy üretim,
`enable_thinking=False`, 128 yeni token sınırı ve yerel MPS/float16 kullanıldı.
Ham çıktılara temizlik uygulanmadı; hedefler modele gösterilmedi.

Cümle tam eşleşmesi 6/34, katı uyum 31/34, gerekli düzeltme 8/95,
doğru kelime koruma 56/68 ve minimal çift başarısı 0/4 bulundu.
Uyumsuz cevapların ilgili birimleri ana metriklerde başarısız sayılır.
Üç kural ihlali p015, p029 ve p030 kayıtlarındadır; hiçbir çıktı token sınırına ulaşmadı.
Ham cevaplar ve üretim metadatası `reports/pilot-base/pilot-base-predictions.*`, puanlama
`reports/pilot-base/pilot-base.json` içinde saklanır. 13 mevcut otomatik kontrol geçti.
Bu sonuç geliştirme pilotuna aittir; SFT henüz yapılmadı ve bağımsız nihai test sonucu değildir.
