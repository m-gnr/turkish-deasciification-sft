# Deasciification Projesi: Ölçüm Planı ve Pilot Veri

Doğal Dil İşlemeye Giriş dersi projesi için düzeltilmiş ölçüm planı: ASCII ile yazılmış Türkçe metni doğru Türkçe karakterlerle geri yazma görevi, yönergeyle ince ayar (SFT) ile.

## Araştırma sorusu

Yönergeyle ince ayar, küçük bir dil modelinin ASCII ile yazılmış Türkçe metni doğru Türkçe karakterlerle geri yazma başarısını ve "sadece harfleri düzelt, başka bir şey değiştirme" yönergesine uyumunu artırıyor mu?

İki ayrı şey ölçülür: doğruluk (doğru harfi seçti mi?) ve yönerge uyumu (yalnızca istenen işi yaptı mı?).

## Önceki taslağa yapılan düzeltmeler

1. **Koşullu doğruluk çarpıtabilir.** Yalnızca uyumlu çıktılarda doğruluk hesaplamak yanıltıcıdır. Kurala az örnekte uyup hepsini doğru yapan model, çoğunda uyup birkaç hata yapan modelden iyi görünebilir. Bu yüzden tüm örnekler üzerinden hesaplanan metrikler ana metrik olur; koşullu doğruluk yanında n sayısıyla ikincil olarak verilir.
2. **Gerçekçi test görevin sınırını değiştirmemeli.** Girdide yazım hatası ve kısaltma bulunabilir, ancak hedef çıktıda düzeltilmez (`yarin gelicem` → `yarın gelicem`). Kendi yazdığımız cümleler "elle hazırlanmış günlük dil testi" olarak adlandırılır; gerçek kullanıcı verisi gibi sunulmaz.
3. **Bütünlük kontrolü kesin tanımlanmalı.** Yalnızca sadeleştirip karşılaştırmak, mevcut bir `ş` harfinin `s` yapılmasını yakalamaz. Konum bazlı kontrol kullanılır. Ham çıktı her zaman saklanır; baştaki ve sondaki boşluk temizleme yalnızca ikincil "yumuşak uyum" ölçüsünde kullanılır.
4. **Frekans baseline'ı tek başına bağlam kullanımını kanıtlamaz.** Bağlam etkisi, aynı belirsiz kelimenin farklı cevap gerektirdiği minimal çiftlerle sınanır. Frekans sözlüğü yalnızca eğitim bölümünden oluşturulur.
5. **Tahmini başarı yüzdeleri bulgu değildir.** Önceki taslaktaki oranlar hipotezdir. "Daha itaatkâr" gibi yorumlar ancak sonuçlar destekliyorsa yazılır.
6. **Belirsiz örneklerde tek doğru cevap varsayımı sorunlu.** Gerçekten iki okumaya açık örnekler ana testte kullanılmaz; ayrı küçük bir kümeye alınır ve birden fazla kabul edilen cevap tanımlanır. "Tavan %100'dür" ifadesi yanlıştı: bu kümede tavan zaten %100'ün altındadır.

Ek iki not:

- **Veri sızıntısı:** Temel model Vikipedi ve haber metinleriyle ön eğitim görmüş olabilir; test cümlelerini ezbere bilebilir. Test için yeni veya elle yazılmış cümleler kullanmak riski azaltır.
- **Bağlam baseline'ı:** Frekans sözlüğünün yanında önceki kelimeye bakan basit bir bigram baseline'ı da konur.

## Düzeltilmiş ölçüm planı

| Metrik | Nasıl hesaplanır |
| --- | --- |
| Uyum oranı (katı) | Ham çıktı üzerinde, tüm örnekler paydada |
| Cümle tam eşleşmesi | Tüm testte; uyumsuz çıktı yanlış sayılır |
| Belirsiz harf doğruluğu (tüm örnekler) | Uyumsuz çıktılar yanlış sayılır |
| Belirsiz harf doğruluğu (yalnız uyumlular) | Yanında n sayısı yazılır |
| Belirsiz kelime ve minimal çift doğruluğu | Ayrı raporlanır |

Ana metrikler ilk ikisidir. Belirsiz harfler `c, g, i, o, s, u` ve büyük karşılıklarıdır.

## Karşılaştırılacak koşullar

| Koşul | Açıklama |
| --- | --- |
| Temel model, sıfır örnekli | Yalnızca yönerge |
| Temel model, birkaç örnekli | Yönerge + 3-5 örnek |
| İnce ayarlı model | SFT sonrası, sıfır örnekli |
| Frekans baseline'ı | Eğitim bölümünden çıkarılan sözlük, en olası karşılık |
| Bigram baseline'ı | Önceki kelimeye bakan basit bağlam modeli |

## Test kümeleri

1. **Sentetik test:** Derlemden ayrılmış, programla ASCII'ye çevrilmiş cümleler.
2. **Belirsizlik ve minimal çift testi:** Her cümlede bağlama bağlı belirsiz kelime geçer.
3. **Elle hazırlanmış günlük dil testi:** Günlük dil, kısaltma ve yazım hatası içerir; hedefte bunlar korunur.
4. **Gerçekten belirsiz küçük küme:** Birden fazla kabul edilen cevapla ayrı raporlanır.

Eğitim ve test cümleleri kesinlikle ayrı olmalıdır; test kümesine eğitim sırasında dokunulmaz.

## Dönüşüm kuralları

Uyum kontrolü, sadeleştirip karşılaştırmak yerine konum bazlıdır. Her konumda çıktı harfi, girdi harfinin izin verilen karşılıklarından biri olmalıdır:

| Girdi | Çıktıda olabilir |
| --- | --- |
| c / C | c, ç / C, Ç |
| g / G | g, ğ / G, Ğ |
| i | i, ı |
| I | I, İ |
| o / O | o, ö / O, Ö |
| s / S | s, ş / S, Ş |
| u / U | u, ü / U, Ü |
| Diğer her karakter (girdideki Türkçe harfler, rakam, noktalama, boşluk dahil) | Aynen aynı |

Ek kurallar:

- Çıktı uzunluğu girdiyle aynı olmalıdır (NFC normalizasyonundan sonra).
- Büyük/küçük harf dönüşümünde Python'un `.lower()` ve `.upper()` fonksiyonları `I/İ` ve `ı/i` yüzünden hata verir; açık bir eşleme tablosu kullanılır.
- Bu kural `ş→s` gibi bozulmaları yakalar. `Google` içindeki `o` → `ö` ise uyum kontrolünden geçer ama doğruluk kontrolünde yanlış sayılır. Uyum ve doğruluk ayrı çalışır.
- Hedef çıktıda yazım hatası ve kısaltmalar düzeltilmez (`gelicem` aynen kalır).

## Belirsizlik

Gerçekten iki okumaya açık örnekler ana testte kullanılmaz. Bunlar ayrı bir küçük kümeye alınır ve birden fazla kabul edilen cevap tanımlanır.

## 20-30 örneklik pilot

Amaç model ölçmek değil, kuralların ve ölçümün boşluklarını bulmaktır. Önerilen dağılım:

| Kategori | Örnek sayısı |
| --- | --- |
| Bağlama bağlı belirsiz kelime ve minimal çiftler | \~8 |
| Özel isim ve yabancı kelime (`Google`, `Ankara`, `mail`) | \~6 |
| Kısmen Türkçe karakterli girdi | \~4 |
| Yazım hatası ve kısaltma (korunacak) | \~4 |
| Büyük harf, `I/İ` | \~4 |
| Sayı, URL, emoji, noktalama | \~2 |

Örnekler:

| Girdi | Beklenen |
| --- | --- |
| her sabah ise gidiyor | her sabah işe gidiyor |
| yorgun ise dinlensin | yorgun ise dinlensin |
| Isik yandi | Işık yandı |
| yarin gelicem, mail attim | yarın gelicem, mail attım |
| ögrenci kartini unutmusum | öğrenci kartını unutmuşum |

Mümkünse 10 örnek başka birine bağımsız çevirtilir; anlaşmazlık çıkan yerler kural boşluğunu gösterir.

## Hata analizi (raporun "ne gördük" kısmı)

- En çok yanlış yapılan kelimeler hangileri?
- Hangi harfte hata yoğun? (`i/ı`, `o/ö` ...)
- Büyük harfli cümle başlarında `I/İ` sorunu
- Özel isimler ve yabancı kelimelerde gereksiz aksan ekleme
- Sentetik test ile elle hazırlanmış günlük dil testi arasındaki fark

## Sınırlılıklar

- Sentetik veri gerçek yazım alışkanlıklarını tam yansıtmaz.
- Tek model ve tek eğitim çalıştırması rastgeleliğe duyarlıdır; zaman varsa 2-3 farklı seed ile tekrarlanır.
- Tahmini sonuçlar hipotezdir; rapora yalnızca ölçülen bulgular yazılır.

## Sonraki adımlar

1. Kesin dönüşüm kurallarını sabitle.
2. 20-30 örneklik pilot veri setini hazırla.
3. Konum bazlı uyum kontrolü ve metrik betiğini yaz.
4. Pilot sonuçlarına göre kuralları güncelle, ardından büyük veri üretimine geç.
