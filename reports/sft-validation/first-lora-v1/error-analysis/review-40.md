# Örnekler

Seed 42; amaçlı tabakalı seçim, yaygınlık tahmini değildir.

## 1. validation:boun:pop_120:kismi — regression

```text
Girdi: - Geçmis yaşamımı anımsamaktan dolayı mutluyum.
Hedef: - Geçmiş yaşamımı anımsamaktan dolayı mutluyum.
Önce:  - Geçmiş yaşamımı anımsamaktan dolayı mutluyum.
Sonra: - geçmiş yaşamımı anımsamaktan dolayı mutluyum.
```

Geçmiş → geçmiş: gerekli ş düzeltmesi yapılırken baştaki G küçültülmüş; önceki tam doğru çıktı bozulmuş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [2, 3], "output_span": [2, 3], "input": "G", "output": "g"}, {"op": "replace", "input_span": [7, 8], "output_span": [7, 8], "input": "s", "output": "ş"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [2, 3], "output_span": [2, 3], "input": "G", "output": "g"}]
```

## 2. validation:boun:bio_1245:kismi — regression

```text
Girdi: Bu degisime sürekli ayak uydurmaniz, yeniliğe acik olmaniz, elbetteki o söyledikleriniz sizi bugune getirmiş olabilir.
Hedef: Bu değişime sürekli ayak uydurmanız, yeniliğe açık olmanız, elbetteki o söyledikleriniz sizi bugüne getirmiş olabilir.
Önce:  Bu değişime sürekli ayak uydurmanız, yeniliğe açık olmanız, elbetteki o söyledikleriniz sizi bugüne getirmiş olabilir.
Sonra: Bu değişime sürekli ayak uydurmazsınız, yeniliğe açık olmanız, elbetteki o söyledikleriniz sizi bugünün getirmiş olabilir.
```

uydurmanız → uydurmazsınız ve bugüne → bugünün: iki sözcükte biçim/ek yeniden yazımı; izin verilen karakter dönüşümlerini aşıyor.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [5, 6], "output_span": [5, 6], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [7, 8], "output_span": [7, 8], "input": "s", "output": "ş"}, {"op": "insert", "input_span": [32, 32], "output_span": [32, 35], "input": "", "output": "zsı"}, {"op": "replace", "input_span": [33, 34], "output_span": [36, 37], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [47, 49], "output_span": [50, 52], "input": "ci", "output": "çı"}, {"op": "replace", "input_span": [56, 57], "output_span": [59, 60], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [96, 97], "output_span": [99, 100], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [98, 99], "output_span": [101, 103], "input": "e", "output": "ün"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [32, 32], "output_span": [32, 35], "input": "", "output": "zsı"}, {"op": "replace", "input_span": [98, 99], "output_span": [101, 103], "input": "e", "output": "ün"}]
```

## 3. validation:boun:news_161:kismi — regression

```text
Girdi: Oyunun kuralları açiktır" dedi.
Hedef: Oyunun kuralları açıktır" dedi.
Önce:  Oyunun kuralları açıktır" dedi.
Sonra: Oyunun kuralları açıkçaştır" dedi.
```

açıktır → açıkçaştır: sözcük içine fazladan karakterler eklenmiş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [19, 20], "output_span": [19, 20], "input": "i", "output": "ı"}, {"op": "insert", "input_span": [21, 21], "output_span": [21, 24], "input": "", "output": "çaş"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [21, 21], "output_span": [21, 24], "input": "", "output": "çaş"}]
```

## 4. validation:boun:ess_1932:koruma — regression

```text
Girdi: Aileye gelen ilk torun olmamdan dolayı adımı İlknur koymuşlar ki ben bundan çok memnunum.
Hedef: Aileye gelen ilk torun olmamdan dolayı adımı İlknur koymuşlar ki ben bundan çok memnunum.
Önce:  Aileye gelen ilk torun olmamdan dolayı adımı İlknur koymuşlar ki ben bundan çok memnunum.
Sonra: Aileye gelen ilk torun olmamdan dolayı adım İlknur koymuşlar ki ben bundan çok memnunum.
```

Koruma örneğinde adımı → adım: son ı silinmiş; girdi zaten hedefti.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "delete", "input_span": [43, 44], "output_span": [43, 43], "input": "ı", "output": ""}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [43, 44], "output_span": [43, 43], "input": "ı", "output": ""}]
```

## 5. validation:boun:pop_383:koruma — regression

```text
Girdi: El Ensar takımının 11 yıllık egemenliğine son veren, yeni Lübnan şampiyonu 25 yıl süren "bekleyişin" ürününü El Ekhi takımını 1 - 0 yenerek aldı.
Hedef: El Ensar takımının 11 yıllık egemenliğine son veren, yeni Lübnan şampiyonu 25 yıl süren "bekleyişin" ürününü El Ekhi takımını 1 - 0 yenerek aldı.
Önce:  El Ensar takımının 11 yıllık egemenliğine son veren, yeni Lübnan şampiyonu 25 yıl süren "bekleyişin" ürününü El Ekhi takımını 1 - 0 yenerek aldı.
Sonra: El Enşar takımının 11 yıllık egemenliğine son veren, yeni Lübnan şampiyonu 25 yıl süren "bekleyişin" ürününü El Ekhi takımını 1 - 0 yenerek aldı.
```

Koruma örneğinde özel isim Ensar → Enşar: izinli s→ş dönüşümü bağlam/hedef açısından gereksiz. Kurala uyum doğru cevap garantisi değil.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [5, 6], "output_span": [5, 6], "input": "s", "output": "ş"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [5, 6], "output_span": [5, 6], "input": "s", "output": "ş"}]
```

## 6. validation:boun:news_136:kismi — improvement

```text
Girdi: Bahçesinde karton kutular yigiliydı.
Hedef: Bahçesinde karton kutular yığılıydı.
Önce:  Bahçesinde karton kutular yığıldı.
Sonra: Bahçesinde karton kutular yığılıydı.
```

Eğitim öncesi yığılıydı → yığıldı kısalması vardı; SFT sözcüğü hedefle tam eşleşecek biçimde koruyup düzeltiyor.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [27, 30], "output_span": [27, 30], "input": "igi", "output": "ığı"}, {"op": "replace", "input_span": [31, 32], "output_span": [31, 32], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[]
```

## 7. validation:boun:pop_1853:tam — improvement

```text
Girdi: Domatesin icini alin, dilimler halinde kesin ve sebzelerin arasina karistirin.
Hedef: Domatesin içini alın, dilimler halinde kesin ve sebzelerin arasına karıştırın.
Önce:  Domatesin içini alin, dilimler halinde kesin ve sebzelerin arasına karıştırin.
Sonra: Domatesin içini alın, dilimler halinde kesin ve sebzelerin arasına karıştırın.
```

alın, karıştırın dahil eksik ı düzeltmeleri tamamlanmış; tüm cümle hedefle aynı.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [11, 12], "output_span": [11, 12], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [18, 19], "output_span": [18, 19], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [63, 64], "output_span": [63, 64], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [70, 72], "output_span": [70, 72], "input": "is", "output": "ış"}, {"op": "replace", "input_span": [73, 74], "output_span": [73, 74], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [75, 76], "output_span": [75, 76], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[]
```

## 8. validation:boun:news_1625:tam — improvement

```text
Girdi: Nitekim Marco daha en basta, sahnedeki performansin etkileyiciligi, dans eden kadinlarin yalnizligi ve caresizligi karsisinda gozyaslarini tutamaz.
Hedef: Nitekim Marco daha en başta, sahnedeki performansın etkileyiciliği, dans eden kadınların yalnızlığı ve çaresizliği karşısında gözyaşlarını tutamaz.
Önce:  Nitekim Marco daha en basta, sahnedeki performansın etkileyiciliği, dans eden kadinların yalnizliği ve çaresizliği karşısında gözyaşları tutamaz.
Sonra: Nitekim Marco daha en başta, sahnedeki performansın etkileyiciliği, dans eden kadınların yalnızlığı ve çaresizliği karşısında gözyaşlarını tutamaz.
```

Önce gözyaşlarını → gözyaşları kısalması ve eksik düzeltmeler vardı; SFT hedefi tam üretmiş. Bu kaynak önceki incelemede de sorunluydu.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [24, 25], "output_span": [24, 25], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [49, 50], "output_span": [49, 50], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [64, 65], "output_span": [64, 65], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [81, 82], "output_span": [81, 82], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [86, 87], "output_span": [86, 87], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [93, 94], "output_span": [93, 94], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [96, 99], "output_span": [96, 99], "input": "igi", "output": "ığı"}, {"op": "replace", "input_span": [103, 104], "output_span": [103, 104], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [112, 113], "output_span": [112, 113], "input": "g", "output": "ğ"}, {"op": "insert", "input_span": [118, 118], "output_span": [118, 120], "input": "", "output": "şı"}, {"op": "replace", "input_span": [119, 122], "output_span": [121, 122], "input": "isi", "output": "ı"}, {"op": "replace", "input_span": [127, 128], "output_span": [127, 128], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [131, 132], "output_span": [131, 132], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [135, 136], "output_span": [135, 136], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [137, 138], "output_span": [137, 138], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[]
```

## 9. validation:boun:pop_1597:kismi — improvement

```text
Girdi: - Bu yıl Eurovision 'a kaç sarkı ile katılacaksıniz?
Hedef: - Bu yıl Eurovision 'a kaç şarkı ile katılacaksınız?
Önce:  - Bu yıl Eurovision 'a kaç sarkı ile katılacaksıniz?
Sonra: - Bu yıl Eurovision 'a kaç şarkı ile katılacaksınız?
```

şarkı ve katılacaksınız düzeltilmiş; Eurovision öncesi/sonrası özgün boşluk ve apostrof düzeni korunmuş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [27, 28], "output_span": [27, 28], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [49, 50], "output_span": [49, 50], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[]
```

## 10. validation:boun:news_1963:kismi — improvement

```text
Girdi: Yeni uygulama ile yakın gelecekte cok daha verimli isler yapacağiz"
Hedef: Yeni uygulama ile yakın gelecekte çok daha verimli işler yapacağız"
Önce:  Yeni uygulama ile yakın gelecekte çok daha verimli işler yapacağız
Sonra: Yeni uygulama ile yakın gelecekte çok daha verimli işler yapacağız"
```

Önce silinen sondaki tırnak SFT çıktısında korunmuş; cümle hedefle aynı.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [34, 35], "output_span": [34, 35], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [52, 53], "output_span": [52, 53], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [64, 65], "output_span": [64, 65], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[]
```

## 11. validation:boun:bio_1283:tam — violation

```text
Girdi: Bir turlu ayrilamazdim onlardan ve gece onlarla yattim.
Hedef: Bir türlü ayrılamazdım onlardan ve gece onlarla yattım.
Önce:  Bir turlu ayrilamazdim onlardan ve gece onlarla yattim.
Sonra: Bir türlü ayrılıamazdım onlardan ve gece onlarla yattım.
```

ayrılamazdım → ayrılıamazdım: sözcük içine ı eklenmiş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [5, 6], "output_span": [5, 6], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [8, 9], "output_span": [8, 9], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [13, 14], "output_span": [13, 14], "input": "i", "output": "ı"}, {"op": "insert", "input_span": [15, 15], "output_span": [15, 16], "input": "", "output": "ı"}, {"op": "replace", "input_span": [20, 21], "output_span": [21, 22], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [52, 53], "output_span": [53, 54], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [15, 15], "output_span": [15, 16], "input": "", "output": "ı"}]
```

## 12. validation:boun:news_1654:tam — violation

```text
Girdi: Fazla beklemeden olmek isteyen McVeigh, ayrica idamini tum Amerikalilarin izleyebilecegini belirtmisti.
Hedef: Fazla beklemeden ölmek isteyen McVeigh, ayrıca idamını tüm Amerikalıların izleyebileceğini belirtmişti.
Önce:  Fazla beklemeden olmek isteyen McVeigh, ayrıca idamini tüm Amerikalılar için izleyebileceğini belirtmisti.
Sonra: Fazla beklemeden olmak isteyen McVeigh, ayrıca idamını tüm Amerikalıların izleyebileceğini belirtmişti.
```

ölmek yerine olmak: e→a izin dışı değişimi; cümlenin anlamı da değişiyor.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "e", "output": "a"}, {"op": "replace", "input_span": [43, 44], "output_span": [43, 44], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [51, 52], "output_span": [51, 52], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [53, 54], "output_span": [53, 54], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [56, 57], "output_span": [56, 57], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [67, 68], "output_span": [67, 68], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [71, 72], "output_span": [71, 72], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [86, 87], "output_span": [86, 87], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [99, 100], "output_span": [99, 100], "input": "s", "output": "ş"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [17, 18], "output_span": [17, 18], "input": "ö", "output": "o"}, {"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "e", "output": "a"}]
```

## 13. validation:boun:ess_155:koruma — violation

```text
Girdi: Her ne kadar burçlara inanmasam da burcumun bazı özelliklerini birebir yansıtmaktayım.
Hedef: Her ne kadar burçlara inanmasam da burcumun bazı özelliklerini birebir yansıtmaktayım.
Önce:  Her ne kadar burçlara inanmasam da burcumun bazı özelliklerini birebir yansıtmaktayım.
Sonra: Her ne kadar burçlara inanmasam da burçmun bazı özelliklerini birebir yansıtmaktayım.
```

Koruma örneğinde burcumun → burçmun: gereksiz c→ç ve u silme bir arada.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [38, 40], "output_span": [38, 39], "input": "cu", "output": "ç"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [38, 40], "output_span": [38, 39], "input": "cu", "output": "ç"}]
```

## 14. validation:boun:news_719:kismi — violation

```text
Girdi: Socrates, farkli bir kultürü öğrenmek, yabancı bir universitede egitim görmek, yeni arkadaslar edinmek, başka bir dil ögrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmis bir program.
Hedef: Socrates, farklı bir kültürü öğrenmek, yabancı bir üniversitede eğitim görmek, yeni arkadaşlar edinmek, başka bir dil öğrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmış bir program.
Önce:  Socrates, farklı bir kültürü öğrenmek, yabancı bir üniversitede eğitim görmek, yeni arkadaşlar edinmek, başka bir dil öğrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmış bir program.
Sonra: Socrates, farklı bir kültürü öğrenmek, yabancı bir üniversite de eğitim görmek, yeni arkadaşlar edinmek, başka bir dil öğrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmış bir program.
```

üniversitede → üniversite de: sözcük içine boşluk eklenmiş. Başka düzeltmeler doğru olsa da katı uyum bozuluyor.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [22, 23], "output_span": [22, 23], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [51, 52], "output_span": [51, 52], "input": "u", "output": "ü"}, {"op": "insert", "input_span": [61, 61], "output_span": [61, 62], "input": "", "output": " "}, {"op": "replace", "input_span": [65, 66], "output_span": [66, 67], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [90, 91], "output_span": [91, 92], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [119, 120], "output_span": [120, 121], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [183, 185], "output_span": [184, 186], "input": "is", "output": "ış"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [61, 61], "output_span": [61, 62], "input": "", "output": " "}]
```

## 15. validation:boun:pop_1918:tam — violation

```text
Girdi: Amac, hatirlayacaginiz gibi, kullerin ucusup size bulasmasini engellemekti.
Hedef: Amaç, hatırlayacağınız gibi, küllerin uçuşup size bulaşmasını engellemekti.
Önce:  Amac, hatirlayacaginiz gibi, kullerin ucusup size bulasmasini engellemekti.
Sonra: Amaç, hatırlayacağınız gibi, kulların uçuşup size bulamasını engellemekti.
```

küllerin → kulların ve bulaşmasını → bulamasını: harf/ek değişimi ile ş silme birleşmiş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [3, 4], "output_span": [3, 4], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [9, 10], "output_span": [9, 10], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [17, 19], "output_span": [17, 19], "input": "gi", "output": "ğı"}, {"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [33, 34], "output_span": [33, 34], "input": "e", "output": "a"}, {"op": "replace", "input_span": [35, 36], "output_span": [35, 36], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [39, 40], "output_span": [39, 40], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [41, 42], "output_span": [41, 42], "input": "s", "output": "ş"}, {"op": "delete", "input_span": [54, 55], "output_span": [54, 54], "input": "s", "output": ""}, {"op": "replace", "input_span": [58, 59], "output_span": [57, 58], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [60, 61], "output_span": [59, 60], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [30, 31], "output_span": [30, 31], "input": "ü", "output": "u"}, {"op": "replace", "input_span": [33, 34], "output_span": [33, 34], "input": "e", "output": "a"}, {"op": "replace", "input_span": [35, 36], "output_span": [35, 36], "input": "i", "output": "ı"}, {"op": "delete", "input_span": [54, 55], "output_span": [54, 54], "input": "ş", "output": ""}]
```

## 16. validation:boun:pop_1220:kismi — violation

```text
Girdi: Onunla beraberlik istiyorsaniz yeterince dayanıkli olup olmadıginızi bilmeniz lazim.
Hedef: Onunla beraberlik istiyorsanız yeterince dayanıklı olup olmadığınızı bilmeniz lazım.
Önce:  Onunla beraberlik istiyorsanız yeterince dayanıklı olup olmadığınızı bilmeniz lazim.
Sonra: Onunla beraberlik istiyorsanız yeterince dayanıklı olup olmadığını bilmeniz lazımdır.
```

olmadığınızı → olmadığını ve lazım → lazımdır: ek silme/ekleme; modelin görevi aşan yeniden yazımı.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [28, 29], "output_span": [28, 29], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [49, 50], "output_span": [49, 50], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [62, 64], "output_span": [62, 64], "input": "gi", "output": "ğı"}, {"op": "delete", "input_span": [66, 68], "output_span": [66, 66], "input": "zi", "output": ""}, {"op": "replace", "input_span": [81, 82], "output_span": [79, 80], "input": "i", "output": "ı"}, {"op": "insert", "input_span": [83, 83], "output_span": [81, 84], "input": "", "output": "dır"}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [66, 68], "output_span": [66, 66], "input": "zı", "output": ""}, {"op": "insert", "input_span": [83, 83], "output_span": [81, 84], "input": "", "output": "dır"}]
```

## 17. validation:boun:news_1756:kismi — violation

```text
Girdi: Fransa Cumhurbaskani Nicolas Sarkozy, gencin ölumunden duydugu derin üzüntuyu dile getirdi.
Hedef: Fransa Cumhurbaşkanı Nicolas Sarkozy, gencin ölümünden duyduğu derin üzüntüyü dile getirdi.
Önce:  Fransa Cumhurbaskani Nicolas Sarkozy, gencin ölümünden duydugu derin üzüntuyu dile getirdi.
Sonra: Fransa Cumhurbaşkanı Nicolas Sarkozy, gençinin ölümünden duydğu derin üzüntüyü dile getirdi.
```

gencin → gençinin ve duyduğu → duydğu: ekleme ve silme aynı cümlede.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [19, 20], "output_span": [19, 20], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [41, 42], "output_span": [41, 44], "input": "c", "output": "çin"}, {"op": "replace", "input_span": [47, 48], "output_span": [49, 50], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [49, 50], "output_span": [51, 52], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [59, 61], "output_span": [61, 62], "input": "ug", "output": "ğ"}, {"op": "replace", "input_span": [74, 75], "output_span": [75, 76], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [76, 77], "output_span": [77, 78], "input": "u", "output": "ü"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [41, 42], "output_span": [41, 44], "input": "c", "output": "çin"}, {"op": "delete", "input_span": [59, 60], "output_span": [61, 61], "input": "u", "output": ""}]
```

## 18. validation:boun:bio_1557:tam — violation

```text
Girdi: Dedemin huyu belliydi, kafayi bulunca illa ki dedigi olacak.
Hedef: Dedemin huyu belliydi, kafayı bulunca illa ki dediği olacak.
Önce:  Dedemin huyu belliydi, kafayi bulunca illa ki dedigi olacak.
Sonra: Dedemin huyu belleiydi, kafayı bulunca illa ki dediği olacak.
```

belliydi → belleiydi: aday olmayan e eklenmiş; gerekli düzeltmelerin doğruluğu ihlali telafi etmiyor.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "insert", "input_span": [17, 17], "output_span": [17, 18], "input": "", "output": "e"}, {"op": "replace", "input_span": [28, 29], "output_span": [29, 30], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [50, 51], "output_span": [51, 52], "input": "g", "output": "ğ"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [17, 17], "output_span": [17, 18], "input": "", "output": "e"}]
```

## 19. validation:boun:ins_471:tam — violation

```text
Girdi: Kazanlarda kaynayan pekmezin kokusu kiskirticidir, uyku tutturmaz adama.
Hedef: Kazanlarda kaynayan pekmezin kokusu kışkırtıcıdır, uyku tutturmaz adama.
Önce:  Kazanlarda kaynayan pekmezin kokusu kiskirticidir, uyku tutturmaz adama.
Sonra: Kazanlarda kaynayan pekmezin kokusu kışkırtıcıdır, uyku tutturur adama.
```

tutturmaz → tutturur: olumsuzluk yapısı değişmiş; salt diakritik sorunu değil.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [37, 39], "output_span": [37, 39], "input": "is", "output": "ış"}, {"op": "replace", "input_span": [40, 41], "output_span": [40, 41], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [43, 44], "output_span": [43, 44], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [45, 46], "output_span": [45, 46], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [47, 48], "output_span": [47, 48], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [62, 65], "output_span": [62, 64], "input": "maz", "output": "ur"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [62, 65], "output_span": [62, 64], "input": "maz", "output": "ur"}]
```

## 20. validation:boun:pop_86:tam — violation

```text
Girdi: Tek tek soforlerle ugrasmaktansa, gelenege uyup isi tepeden cozmek daha kolaydi.
Hedef: Tek tek şoförlerle uğraşmaktansa, geleneğe uyup işi tepeden çözmek daha kolaydı.
Önce:  Tek tek soforlerle ugrasmaktansa, gelenege uyup isi tepeden cozmek daha kolaydi.
Sonra: Tek tek soforlerle ugrasmaktansa, geleneğe uyup işi tepeden çıkmak daha kolaydı.
```

çözmek → çıkmak: sözcük değiştirilmiş; şoförlerle/uğraşmaktansa düzeltmeleri de eksik.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [40, 41], "output_span": [40, 41], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [49, 50], "output_span": [49, 50], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [60, 63], "output_span": [60, 63], "input": "coz", "output": "çık"}, {"op": "replace", "input_span": [64, 65], "output_span": [64, 65], "input": "e", "output": "a"}, {"op": "replace", "input_span": [78, 79], "output_span": [78, 79], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [8, 9], "output_span": [8, 9], "input": "ş", "output": "s"}, {"op": "replace", "input_span": [11, 12], "output_span": [11, 12], "input": "ö", "output": "o"}, {"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "ğ", "output": "g"}, {"op": "replace", "input_span": [23, 24], "output_span": [23, 24], "input": "ş", "output": "s"}, {"op": "replace", "input_span": [61, 63], "output_span": [61, 63], "input": "öz", "output": "ık"}, {"op": "replace", "input_span": [64, 65], "output_span": [64, 65], "input": "e", "output": "a"}]
```

## 21. validation:boun:ess_56:kismi — violation

```text
Girdi: KORKMUYORUM SENDEN Onlar laik insanlar olarak, papazların hakimiyetine karsı çıkmıs, sert eleştirilerle kiliseyi hırpalamiş, baskıcı imana karşı çıkmışlardir.
Hedef: KORKMUYORUM SENDEN Onlar laik insanlar olarak, papazların hakimiyetine karşı çıkmış, sert eleştirilerle kiliseyi hırpalamış, baskıcı imana karşı çıkmışlardır.
Önce:  KORKMUYORUM SİNDEN Onlar laik insanlar olarak, papazların hakimiyetine karşı çıkmış, sert eleştirilerle kiliseyi hırpalamiş, baskıcı imana karşı çıkmışlardır.
Sonra: KORKMUYORUM SEDEN Onlar laik insanlar olarak, papazların hakimiyetine karşı çıkmış, sert eleştirilerle kiliseyi hırpalamış, baskıçı imana karşı çıkmışlardı.
```

SENDEN → SEDEN ve çıkmışlardır → çıkmışlardı silmeleri; baskıcı → baskıçı gereksiz düzeltmesi de var.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "delete", "input_span": [14, 15], "output_span": [14, 14], "input": "N", "output": ""}, {"op": "replace", "input_span": [74, 75], "output_span": [73, 74], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [82, 83], "output_span": [81, 82], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [121, 122], "output_span": [120, 121], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [130, 131], "output_span": [129, 130], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [155, 157], "output_span": [154, 155], "input": "ir", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [14, 15], "output_span": [14, 14], "input": "N", "output": ""}, {"op": "replace", "input_span": [130, 131], "output_span": [129, 130], "input": "c", "output": "ç"}, {"op": "delete", "input_span": [156, 157], "output_span": [155, 155], "input": "r", "output": ""}]
```

## 22. validation:boun:ess_176:tam — violation

```text
Girdi: ) olumu, yenidogan yogun bakim unitesindeki yaygin enfeksiyon, siddet olaylari, hastanenin bulundugu bolgenin sosyal ve ekonomik sartlari, degisiklikleri hastanede yasanacak kriz bicimidir.
Hedef: ) ölümü, yenidoğan yoğun bakım ünitesindeki yaygın enfeksiyon, şiddet olayları, hastanenin bulunduğu bölgenin sosyal ve ekonomik şartları, değişiklikleri hastanede yaşanacak kriz biçimidir.
Önce:  ) olumu, yenidogan yogun bakim unitesindeki yaygin enfeksiyon, siddet olaylari, hastanenin bulundugu bolgenin sosyal ve ekonomik sartlari, degisiklikleri hastanede yasanacak kriz bicimidir.
Sonra: ) olumu, yenidoğan yoğun bakım ünitesindeki yaygın enfeksiyon, şiddet olayları, hastanenin bulunduğu bölgenin sosyal ve ekonomik şartları, değişiklikleri hastanede yaşacak kriz biçimidir.
```

yaşanacak → yaşacak: na silinmiş; ölümü düzeltmesi eksik kalmış.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [21, 22], "output_span": [21, 22], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [28, 29], "output_span": [28, 29], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [31, 32], "output_span": [31, 32], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [48, 49], "output_span": [48, 49], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [63, 64], "output_span": [63, 64], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [77, 78], "output_span": [77, 78], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [98, 99], "output_span": [98, 99], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [102, 103], "output_span": [102, 103], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [129, 130], "output_span": [129, 130], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [136, 137], "output_span": [136, 137], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [141, 142], "output_span": [141, 142], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [143, 144], "output_span": [143, 144], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [166, 169], "output_span": [166, 167], "input": "san", "output": "ş"}, {"op": "replace", "input_span": [181, 182], "output_span": [179, 180], "input": "c", "output": "ç"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [2, 3], "output_span": [2, 3], "input": "ö", "output": "o"}, {"op": "replace", "input_span": [4, 5], "output_span": [4, 5], "input": "ü", "output": "u"}, {"op": "replace", "input_span": [6, 7], "output_span": [6, 7], "input": "ü", "output": "u"}, {"op": "delete", "input_span": [168, 170], "output_span": [168, 168], "input": "na", "output": ""}]
```

## 23. validation:boun:news_798:tam — violation

```text
Girdi: Kardeslik her seye kadir
Hedef: Kardeşlik her şeye kadir
Önce:  Kardeslik her seye kadir
Sonra:  kardeşlik her seye kadir
```

Başa boşluk eklenmiş ve K küçültülmüş; şeye düzeltmesi eksik. Karma ihlal yalnız uzunluk kategorisinde görünür.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [0, 1], "output_span": [0, 2], "input": "K", "output": " k"}, {"op": "replace", "input_span": [5, 6], "output_span": [6, 7], "input": "s", "output": "ş"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [0, 1], "output_span": [0, 2], "input": "K", "output": " k"}, {"op": "replace", "input_span": [14, 15], "output_span": [15, 16], "input": "ş", "output": "s"}]
```

## 24. validation:boun:news_1145:tam — violation

```text
Girdi: Gozlemciler Kremlin'in gecmiste zengin isadami Boris Berezovski'nin muhalif rolunu Hodorkovskiy'in oynamasindan cekinildigi gorusunde.
Hedef: Gözlemciler Kremlin'in geçmişte zengin işadamı Boris Berezovski'nin muhalif rolünü Hodorkovskiy'in oynamasından çekinildiği görüşünde.
Önce:  Gözlemciler Kremlin'in gecmiste zengin isadami Boris Berezovski'nin muhalif rolunu Hodorkovskiy'in oynamasından çekinildiği görüşünde.
Sonra: Gözlemciler Kremlin'in geçmişt zengin isadami Boris Berezovski'nin muhalif rolunu Hodorkovski'nin oynamasından çekinildiği görüşünde.
```

geçmişte → geçmişt ve Hodorkovskiy → Hodorkovski: iki sözcükte harf silme; özel isme müdahale.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [1, 2], "output_span": [1, 2], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [25, 26], "output_span": [25, 26], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [28, 29], "output_span": [28, 29], "input": "s", "output": "ş"}, {"op": "delete", "input_span": [30, 31], "output_span": [30, 30], "input": "e", "output": ""}, {"op": "delete", "input_span": [94, 95], "output_span": [93, 93], "input": "y", "output": ""}, {"op": "insert", "input_span": [96, 96], "output_span": [94, 95], "input": "", "output": "n"}, {"op": "replace", "input_span": [106, 107], "output_span": [105, 106], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [112, 113], "output_span": [111, 112], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [121, 122], "output_span": [120, 121], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [125, 126], "output_span": [124, 125], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [127, 130], "output_span": [126, 129], "input": "usu", "output": "üşü"}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [30, 31], "output_span": [30, 30], "input": "e", "output": ""}, {"op": "replace", "input_span": [40, 41], "output_span": [39, 40], "input": "ş", "output": "s"}, {"op": "replace", "input_span": [45, 46], "output_span": [44, 45], "input": "ı", "output": "i"}, {"op": "replace", "input_span": [79, 80], "output_span": [78, 79], "input": "ü", "output": "u"}, {"op": "replace", "input_span": [81, 82], "output_span": [80, 81], "input": "ü", "output": "u"}, {"op": "delete", "input_span": [94, 95], "output_span": [93, 93], "input": "y", "output": ""}, {"op": "insert", "input_span": [96, 96], "output_span": [94, 95], "input": "", "output": "n"}]
```

## 25. validation:boun:ess_1042:tam — violation

```text
Girdi: Bizler, esitlige ve demokrasiye anlamlar yukledik, ozunu yasatamadik.
Hedef: Bizler, eşitliğe ve demokrasiye anlamlar yükledik, özünü yaşatamadık.
Önce:  Bizler, esitlige ve demokrasiye anlamlar yukledik, ozunu yasatamadik.
Sonra: Bizler, eşitliğe ve demokrasiye anlamlar yüklüydük, öznünü yaşatamadık.
```

yükledik → yüklüydük ve özünü → öznünü: yeniden yazım ve fazladan n.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [9, 10], "output_span": [9, 10], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [14, 15], "output_span": [14, 15], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [42, 43], "output_span": [42, 43], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [45, 46], "output_span": [45, 47], "input": "e", "output": "üy"}, {"op": "replace", "input_span": [47, 48], "output_span": [48, 49], "input": "i", "output": "ü"}, {"op": "replace", "input_span": [51, 52], "output_span": [52, 53], "input": "o", "output": "ö"}, {"op": "delete", "input_span": [53, 54], "output_span": [54, 54], "input": "u", "output": ""}, {"op": "replace", "input_span": [55, 56], "output_span": [55, 58], "input": "u", "output": "ünü"}, {"op": "replace", "input_span": [59, 60], "output_span": [61, 62], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [66, 67], "output_span": [68, 69], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [45, 46], "output_span": [45, 47], "input": "e", "output": "üy"}, {"op": "replace", "input_span": [47, 48], "output_span": [48, 49], "input": "i", "output": "ü"}, {"op": "insert", "input_span": [53, 53], "output_span": [54, 55], "input": "", "output": "n"}]
```

## 26. validation:boun:ess_267:tam — violation

```text
Girdi: HAYATIN ARMAGANI Belki tatli bir burukluk var duygularimizda, ama asla yakinmak icin anmadim bu hatirayi.
Hedef: HAYATIN ARMAĞANI Belki tatlı bir burukluk var duygularımızda, ama asla yakınmak için anmadım bu hatırayı.
Önce:  HAYATIN ARMAGANI Belki tatli bir burukluk var duygularimizda, ama asla yakinmak icin anmadim bu hatirayi.
Sonra: HAYATIN ARMAGANI Belki tatlı bir burukluk var duygularımızda, ama asla yakındanmak için anmadım bu hatıra.
```

yakınmak → yakındanmak ve hatırayı → hatıra: ekleme/silme; ARMAĞANI düzeltmesi de eksik.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [27, 28], "output_span": [27, 28], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [54, 55], "output_span": [54, 55], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [56, 57], "output_span": [56, 57], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [74, 75], "output_span": [74, 78], "input": "i", "output": "ında"}, {"op": "replace", "input_span": [81, 82], "output_span": [84, 85], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [90, 91], "output_span": [93, 94], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [99, 100], "output_span": [102, 103], "input": "i", "output": "ı"}, {"op": "delete", "input_span": [102, 104], "output_span": [105, 105], "input": "yi", "output": ""}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [12, 13], "output_span": [12, 13], "input": "Ğ", "output": "G"}, {"op": "insert", "input_span": [76, 76], "output_span": [76, 79], "input": "", "output": "dan"}, {"op": "delete", "input_span": [102, 104], "output_span": [105, 105], "input": "yı", "output": ""}]
```

## 27. validation:boun:bio_1537:tam — violation

```text
Girdi: Aday, locada bir kez dolastirildiktan sonra ant kursusunun onune getirilir.
Hedef: Aday, locada bir kez dolaştırıldıktan sonra ant kürsüsünün önüne getirilir.
Önce:  Aday, locada bir kez dolastirildiktan sonra ant kursusunun onune getirilir.
Sonra: Aday, locada bir kez dolastırdıktan sonra ant kursuunun önüne getirilir.
```

dolaştırıldıktan → dolastırdıktan ve kürsüsünün → kursuunun: eksik düzeltmeler yanında harf silmeleri.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [27, 28], "output_span": [27, 28], "input": "i", "output": "ı"}, {"op": "delete", "input_span": [29, 31], "output_span": [29, 29], "input": "il", "output": ""}, {"op": "replace", "input_span": [32, 33], "output_span": [30, 31], "input": "i", "output": "ı"}, {"op": "delete", "input_span": [53, 54], "output_span": [51, 51], "input": "s", "output": ""}, {"op": "replace", "input_span": [59, 60], "output_span": [56, 57], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [61, 62], "output_span": [58, 59], "input": "u", "output": "ü"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [25, 26], "output_span": [25, 26], "input": "ş", "output": "s"}, {"op": "delete", "input_span": [29, 31], "output_span": [29, 29], "input": "ıl", "output": ""}, {"op": "replace", "input_span": [49, 50], "output_span": [47, 48], "input": "ü", "output": "u"}, {"op": "replace", "input_span": [52, 55], "output_span": [50, 52], "input": "üsü", "output": "uu"}, {"op": "replace", "input_span": [56, 57], "output_span": [53, 54], "input": "ü", "output": "u"}]
```

## 28. validation:boun:pop_819:kismi — violation

```text
Girdi: Bu durum karsisında Maliye bakanliğindan istifa etti.
Hedef: Bu durum karşısında Maliye bakanlığından istifa etti.
Önce:  Bu durum karsisında Maliye bakanlığında istifa etti.
Sonra: Bu durum karşısında Maliye Bakanı tarafından istifa etti.
```

bakanlığından → Bakanı tarafından: büyük harf değişimi ve tek sözcüğün iki sözcüklü ifadeye dönüştürülmesi.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [12, 14], "output_span": [12, 14], "input": "si", "output": "şı"}, {"op": "replace", "input_span": [27, 28], "output_span": [27, 28], "input": "b", "output": "B"}, {"op": "replace", "input_span": [32, 36], "output_span": [32, 40], "input": "liği", "output": "ı tarafı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [27, 28], "output_span": [27, 28], "input": "b", "output": "B"}, {"op": "delete", "input_span": [32, 33], "output_span": [32, 32], "input": "l", "output": ""}, {"op": "replace", "input_span": [34, 35], "output_span": [33, 39], "input": "ğ", "output": " taraf"}]
```

## 29. validation:boun:ess_1009:kismi — violation

```text
Girdi: KOPEK BALIKLARININ BILINMEYEN ÖZELLIKLERI Bit pazarına gider, oğluna 100 TL'ye çalintı bisiklet alir.
Hedef: KÖPEK BALIKLARININ BİLİNMEYEN ÖZELLİKLERİ Bit pazarına gider, oğluna 100 TL'ye çalıntı bisiklet alır.
Önce:  KOPEK BALIKLARININ BILINMEYEN ÖZELLIKLERI Bit pazarına gider, oğluna 100 TL'ye çalintı bisiklet alir.
Sonra: KOPEK BALIKLARININ BİLİNMEYEN ÖZELİKLERİ Bit pazarına gider, oğluna 100 TL'ye çalıntı bisiklet alır.
```

ÖZELLİKLERİ → ÖZELİKLERİ: bir L silinmiş; KÖPEK düzeltmesi eksik.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "I", "output": "İ"}, {"op": "replace", "input_span": [22, 23], "output_span": [22, 23], "input": "I", "output": "İ"}, {"op": "replace", "input_span": [34, 36], "output_span": [34, 35], "input": "LI", "output": "İ"}, {"op": "replace", "input_span": [40, 41], "output_span": [39, 40], "input": "I", "output": "İ"}, {"op": "replace", "input_span": [82, 83], "output_span": [81, 82], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [98, 99], "output_span": [97, 98], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [1, 2], "output_span": [1, 2], "input": "Ö", "output": "O"}, {"op": "delete", "input_span": [33, 34], "output_span": [33, 33], "input": "L", "output": ""}]
```

## 30. validation:boun:news_1688:tam — violation

```text
Girdi: ABD ordusu "buyuk ihtimalle masum olan insanlarin kaybindan dolayi derin uzuntu duydugunu"  acikladi.
Hedef: ABD ordusu "büyük ihtimalle masum olan insanların kaybından dolayı derin üzüntü duyduğunu"  açıkladı.
Önce:  ABD ordusu "buyuk ihtimalle masum olan insanlarin kaybindan dolayi derin uzuntu duydugunu" acikladi.
Sonra: ABD ordusu "büyük ihtimalle masum olan insanların kaybindan dolayı derin uzanç duydüğünü" açıkladı.
```

üzüntü → uzanç ve duyduğunu → duydüğünü: yeniden yazım; iki boşluk da teke indirilmiş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [13, 14], "output_span": [13, 14], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [47, 48], "output_span": [47, 48], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [65, 66], "output_span": [65, 66], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [75, 76], "output_span": [75, 76], "input": "u", "output": "a"}, {"op": "replace", "input_span": [77, 79], "output_span": [77, 78], "input": "tu", "output": "ç"}, {"op": "replace", "input_span": [84, 87], "output_span": [83, 86], "input": "ugu", "output": "üğü"}, {"op": "replace", "input_span": [88, 89], "output_span": [87, 88], "input": "u", "output": "ü"}, {"op": "delete", "input_span": [91, 92], "output_span": [90, 90], "input": " ", "output": ""}, {"op": "replace", "input_span": [93, 95], "output_span": [91, 93], "input": "ci", "output": "çı"}, {"op": "replace", "input_span": [99, 100], "output_span": [97, 98], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [54, 55], "output_span": [54, 55], "input": "ı", "output": "i"}, {"op": "replace", "input_span": [73, 74], "output_span": [73, 74], "input": "ü", "output": "u"}, {"op": "replace", "input_span": [75, 76], "output_span": [75, 76], "input": "ü", "output": "a"}, {"op": "replace", "input_span": [77, 79], "output_span": [77, 78], "input": "tü", "output": "ç"}, {"op": "replace", "input_span": [84, 85], "output_span": [83, 84], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [86, 87], "output_span": [85, 86], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [88, 89], "output_span": [87, 88], "input": "u", "output": "ü"}, {"op": "delete", "input_span": [90, 91], "output_span": [89, 89], "input": " ", "output": ""}]
```

## 31. validation:boun:news_412:tam — compliant_wrong

```text
Girdi: 70 yili askin Sovyet tarihinde ilk kez "gizlenmeyen, ortaya cikan, demecler veren, esiyle birlikte resmi gezilere katilan" bir lider esiydi.
Hedef: 70 yılı aşkın Sovyet tarihinde ilk kez "gizlenmeyen, ortaya çıkan, demeçler veren, eşiyle birlikte resmi gezilere katılan" bir lider eşiydi.
Önce:  70 yılı askin Sovyet tarihinde ilk kez "gizlenmeyen, ortaya cikan, demecler veren, esiyle birlikte resmi gezilere katilan" bir lider esiydi.
Sonra: 70 yılı aşkın Sovyet tarihinde ilk kez "gizlenmeyen, ortaya çıkan, demeçler veren, eşiyle birlikte resmi gezilere katılan" bir lider esiydi.
```

esiydi → eşiydi düzeltmesi eksik; diğer gerekli düzeltmeler yapılmış.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [4, 5], "output_span": [4, 5], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [6, 7], "output_span": [6, 7], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [9, 10], "output_span": [9, 10], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [11, 12], "output_span": [11, 12], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [60, 62], "output_span": [60, 62], "input": "ci", "output": "çı"}, {"op": "replace", "input_span": [71, 72], "output_span": [71, 72], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [84, 85], "output_span": [84, 85], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [117, 118], "output_span": [117, 118], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [134, 135], "output_span": [134, 135], "input": "ş", "output": "s"}]
```

## 32. validation:boun:pop_1988:tam — compliant_wrong

```text
Girdi: Bu en taninmis spor merkezlerine uyelikten, esofmanlari cekip kirda, parkta, ormanda kosmaya kadar her sekilde olabilir.
Hedef: Bu en tanınmış spor merkezlerine üyelikten, eşofmanları çekip kırda, parkta, ormanda koşmaya kadar her şekilde olabilir.
Önce:  Bu en tanınmış spor merkezlerine uyulmakta, esofmanlari çeker ve kirda, parkta, ormanda kosmaya kadar her şekilde olabilir.
Sonra: Bu en tanınmış spor merkezlerine üyelikten, esofmanları çekip kirda, parkta, ormanda koşmaya kadar her şekilde olabilir.
```

eşofmanları ve kırda sözcüklerinde ş/ı düzeltmeleri eksik; biçim korunuyor.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [9, 10], "output_span": [9, 10], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [12, 14], "output_span": [12, 14], "input": "is", "output": "ış"}, {"op": "replace", "input_span": [33, 34], "output_span": [33, 34], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [54, 55], "output_span": [54, 55], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [56, 57], "output_span": [56, 57], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [87, 88], "output_span": [87, 88], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [103, 104], "output_span": [103, 104], "input": "s", "output": "ş"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [45, 46], "output_span": [45, 46], "input": "ş", "output": "s"}, {"op": "replace", "input_span": [63, 64], "output_span": [63, 64], "input": "ı", "output": "i"}]
```

## 33. validation:boun:bio_678:kismi — compliant_wrong

```text
Girdi: Kapıyi kapadı, "Bashekim bey, ameliyathanede bir hirsız var, parcalarin yarisini caliyor.
Hedef: Kapıyı kapadı, "Başhekim bey, ameliyathanede bir hırsız var, parçaların yarısını çalıyor.
Önce:  Kapıyi kapadı, "Bashekim bey, ameliyathanede bir hirsız var, parcalarin yarisini caliyor."
Sonra: Kapıyı kapadı, "Başhekim bey, ameliyathanede bir hirsız var, parçaların yarısını çalıyor.
```

hirsız → hırsız düzeltmesi eksik; özgün kapanmayan tırnak yapısı korunmuş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [5, 6], "output_span": [5, 6], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [18, 19], "output_span": [18, 19], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [64, 65], "output_span": [64, 65], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [69, 70], "output_span": [69, 70], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [75, 76], "output_span": [75, 76], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [77, 78], "output_span": [77, 78], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [79, 80], "output_span": [79, 80], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [81, 82], "output_span": [81, 82], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [84, 85], "output_span": [84, 85], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [50, 51], "output_span": [50, 51], "input": "ı", "output": "i"}]
```

## 34. validation:boun:pop_971:tam — compliant_wrong

```text
Girdi: Alayci bir kinle nefret edebilir ve siddetli bir tutkuyla sevebilir.
Hedef: Alaycı bir kinle nefret edebilir ve şiddetli bir tutkuyla sevebilir.
Önce:  Alayci bir kinle nefret edebilir ve siddetli bir tutkuyla sevebilir.
Sonra: Alaycı bir kinle nefret edebilir ve siddetli bir tutkuyla sevebilir.
```

siddetli → şiddetli düzeltmesi eksik; Alaycı doğru düzeltilmiş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [5, 6], "output_span": [5, 6], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [36, 37], "output_span": [36, 37], "input": "ş", "output": "s"}]
```

## 35. validation:boun:bio_1081:tam — compliant_wrong

```text
Girdi: "Olen ben degilim, dayi degil, siir, siir!" diye inledim.
Hedef: "Ölen ben değilim, dayı değil, şiir, şiir!" diye inledim.
Önce:  "Olen ben degilim, dayi degil, siir, siir!" diye inledim.
Sonra: "Olen ben değilim, dayı değil, şiir, şiir!" diye inledim.
```

Olen → Ölen düzeltmesi eksik; büyük harfli adayda kaçırma.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [12, 13], "output_span": [12, 13], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [22, 23], "output_span": [22, 23], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [26, 27], "output_span": [26, 27], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [31, 32], "output_span": [31, 32], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [37, 38], "output_span": [37, 38], "input": "s", "output": "ş"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [1, 2], "output_span": [1, 2], "input": "Ö", "output": "O"}]
```

## 36. validation:boun:news_1163:kismi — compliant_wrong

```text
Girdi: Fransa ve bir iki ülke Acil Müdahale Gücu'nun ileride bagımsiz olmasını istiyor.
Hedef: Fransa ve bir iki ülke Acil Müdahale Gücü'nün ileride bağımsız olmasını istiyor.
Önce:  Fransa ve bir iki ülke Acil Müdahale Gücu'nun ileride bagımsız olmasını istiyor.
Sonra: Fransa ve bir iki ülke Acil Müdahale Gücü'nun ileride bağımsız olmasını istiyor.
```

Gücü'nun → Gücü'nün: ek içindeki u→ü kaçırılmış; sözcük gövdesi düzelmiş.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [40, 41], "output_span": [40, 41], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [56, 57], "output_span": [56, 57], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [60, 61], "output_span": [60, 61], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [43, 44], "output_span": [43, 44], "input": "ü", "output": "u"}]
```

## 37. validation:boun:news_1031:tam — compliant_wrong

```text
Girdi: Cephe icinde Islamci ve milliyetci gruplar birlikte temsil ediliyor.
Hedef: Cephe içinde İslamcı ve milliyetçi gruplar birlikte temsil ediliyor.
Önce:  Cephe içinde İslamcı ve milliyetci gruplar birlikte temsil ediliyor.
Sonra: Çephe içinde İslamcı ve milliyetçi gruplar birlikte temsil ediliyor.
```

Cephe → Çephe gereksiz C→Ç; diğer gerekli düzeltmeler tamamlanmış.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [0, 1], "output_span": [0, 1], "input": "C", "output": "Ç"}, {"op": "replace", "input_span": [7, 8], "output_span": [7, 8], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [13, 14], "output_span": [13, 14], "input": "I", "output": "İ"}, {"op": "replace", "input_span": [19, 20], "output_span": [19, 20], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [32, 33], "output_span": [32, 33], "input": "c", "output": "ç"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [0, 1], "output_span": [0, 1], "input": "C", "output": "Ç"}]
```

## 38. validation:boun:ess_602:tam — compliant_wrong

```text
Girdi: Bir kendisi var her seyi bilen Aslinda, ilk duzyazimin 1945'te yayinlanan bir oyku oldugunu soylemistim.
Hedef: Bir kendisi var her şeyi bilen Aslında, ilk düzyazımın 1945'te yayınlanan bir öykü olduğunu söylemiştim.
Önce:  Bir kendisi var her seyi bilen Aslinda, ilk duzyazimin 1945'te yayinlanan bir öykü oldugunu soylemistim.
Sonra: Bir kendisi var her şeyi bilen Aslında, ilk düzyazımin 1945'te yayınlanan bir öykü olduğunu söylemiştim.
```

düzyazımin → düzyazımın: ek içindeki i→ı kaçırılmış.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [34, 35], "output_span": [34, 35], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [45, 46], "output_span": [45, 46], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [50, 51], "output_span": [50, 51], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [66, 67], "output_span": [66, 67], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [78, 79], "output_span": [78, 79], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [81, 82], "output_span": [81, 82], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [87, 88], "output_span": [87, 88], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [93, 94], "output_span": [93, 94], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [99, 100], "output_span": [99, 100], "input": "s", "output": "ş"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [52, 53], "output_span": [52, 53], "input": "ı", "output": "i"}]
```

## 39. validation:boun:ins_47:tam — compliant_wrong

```text
Girdi: Elmabas bir ordek uzaktan uzaga suzulup gidiyor...
Hedef: Elmabaş bir ördek uzaktan uzağa süzülüp gidiyor...
Önce:  Elmabas bir ordek uzaktan uzaga suzulup gidiyor...
Sonra: Elmabas bir ordek uzaktan uzaga süzülüp gidiyor...
```

Elmabaş, ördek, uzağa düzeltmeleri eksik; süzülüp doğru düzeltilmiş. Elmabaş kuş adı bağlamındadır; büyük harf tek başına özel isim kanıtı değildir.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [33, 34], "output_span": [33, 34], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [35, 36], "output_span": [35, 36], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [37, 38], "output_span": [37, 38], "input": "u", "output": "ü"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [6, 7], "output_span": [6, 7], "input": "ş", "output": "s"}, {"op": "replace", "input_span": [12, 13], "output_span": [12, 13], "input": "ö", "output": "o"}, {"op": "replace", "input_span": [29, 30], "output_span": [29, 30], "input": "ğ", "output": "g"}]
```

## 40. validation:boun:ess_1845:tam — compliant_wrong

```text
Girdi: Yavasca salondan ayrildim.
Hedef: Yavaşça salondan ayrıldım.
Önce:  Yavasca salondan ayrildim.
Sonra: Yavasca salondan ayrıldım.
```

Yavasca → Yavaşça: iki gerekli düzeltme kaçırılmış; ayrıldım doğru.

Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [23, 24], "output_span": [23, 24], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [4, 6], "output_span": [4, 6], "input": "şç", "output": "sc"}]
```
