# Örnekler

Seed 42; amaçlı tabakalı seçim, yaygınlık tahmini değildir.

## 1. validation:boun:ins_1051:kismi — sft_zero_shot:case

```text
Girdi: tubitak: Alan adini gösterir.
Hedef: tubitak: Alan adını gösterir.

Sonra: TÜBİTAK: Alan adını gösterir.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [0, 7], "output_span": [0, 7], "input": "tubitak", "output": "TÜBİTAK"}, {"op": "replace", "input_span": [16, 17], "output_span": [16, 17], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [18, 19], "output_span": [18, 19], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [0, 7], "output_span": [0, 7], "input": "tubitak", "output": "TÜBİTAK"}]
```

## 2. validation:boun:pop_1257:tam — sft_zero_shot:case

```text
Girdi: 63. Butun agaclar ve tabiat kutsaldir, ayirim yapmadan.
Hedef: 63. Bütün ağaçlar ve tabiat kutsaldır, ayırım yapmadan.

Sonra: 63. bütün ağaçlar ve tabiat kutsaldır, ayırım yapmadan.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [4, 6], "output_span": [4, 6], "input": "Bu", "output": "bü"}, {"op": "replace", "input_span": [7, 8], "output_span": [7, 8], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [11, 12], "output_span": [11, 12], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [13, 14], "output_span": [13, 14], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [35, 36], "output_span": [35, 36], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [41, 42], "output_span": [41, 42], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [43, 44], "output_span": [43, 44], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [4, 5], "output_span": [4, 5], "input": "B", "output": "b"}]
```

## 3. validation:boun:pop_853:kismi — sft_zero_shot:case

```text
Girdi: Temiz ve titiz bir calismanin urünü olarak da bir bütunlük tasidıgina inandigimız bu yapiti ortaya cıkardık." Gelelim turkulerimizin sentezine:
Hedef: Temiz ve titiz bir çalışmanın ürünü olarak da bir bütünlük taşıdığına inandığımız bu yapıtı ortaya çıkardık." Gelelim türkülerimizin sentezine:

Sonra: Temiz ve titiz bir çalışmanın ürünü olarak da bir bütünlük taşıdığına inandığımız bu yapıtı ortaya çıkardık." Gelelim Türkülerimizin sentezine:
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [19, 20], "output_span": [19, 20], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [22, 24], "output_span": [22, 24], "input": "is", "output": "ış"}, {"op": "replace", "input_span": [27, 28], "output_span": [27, 28], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [30, 31], "output_span": [30, 31], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [53, 54], "output_span": [53, 54], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [61, 63], "output_span": [61, 63], "input": "si", "output": "şı"}, {"op": "replace", "input_span": [65, 67], "output_span": [65, 67], "input": "gi", "output": "ğı"}, {"op": "replace", "input_span": [75, 78], "output_span": [75, 78], "input": "igi", "output": "ığı"}, {"op": "replace", "input_span": [88, 89], "output_span": [88, 89], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [90, 91], "output_span": [90, 91], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [99, 100], "output_span": [99, 100], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [118, 120], "output_span": [118, 120], "input": "tu", "output": "Tü"}, {"op": "replace", "input_span": [122, 123], "output_span": [122, 123], "input": "u", "output": "ü"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [118, 119], "output_span": [118, 119], "input": "t", "output": "T"}]
```

## 4. validation:boun:news_719:kismi — sft_zero_shot:punctuation

```text
Girdi: Socrates, farkli bir kultürü öğrenmek, yabancı bir universitede egitim görmek, yeni arkadaslar edinmek, başka bir dil ögrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmis bir program.
Hedef: Socrates, farklı bir kültürü öğrenmek, yabancı bir üniversitede eğitim görmek, yeni arkadaşlar edinmek, başka bir dil öğrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmış bir program.

Sonra: Socrates, farklı bir kültürü öğrenmek, yabancı bir üniversite de eğitim görmek, yeni arkadaşlar edinmek, başka bir dil öğrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmış bir program.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [22, 23], "output_span": [22, 23], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [51, 52], "output_span": [51, 52], "input": "u", "output": "ü"}, {"op": "insert", "input_span": [61, 61], "output_span": [61, 62], "input": "", "output": " "}, {"op": "replace", "input_span": [65, 66], "output_span": [66, 67], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [90, 91], "output_span": [91, 92], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [119, 120], "output_span": [120, 121], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [183, 185], "output_span": [184, 186], "input": "is", "output": "ış"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [61, 61], "output_span": [61, 62], "input": "", "output": " "}]
```

## 5. validation:boun:bio_974:tam — sft_zero_shot:punctuation

```text
Girdi: Eger bir iliskide iki taraf da kendi ayaklari uzerinde durabildikleri halde bu beraberligi surduruyorlarsa, iste ancak o zaman o iliski icin saglikli denebilir.
Hedef: Eğer bir ilişkide iki taraf da kendi ayakları üzerinde durabildikleri halde bu beraberliği sürdürüyorlarsa, işte ancak o zaman o ilişki için sağlıklı denebilir.

Sonra: Eğer bir ilişki de iki taraf da kendi ayakları üzerinde durabildikleri halde bu beraberliği sürdürüyorlarsa, iste ancak o zaman o ilişki için sağlıklı denebilir.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [1, 2], "output_span": [1, 2], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [12, 13], "output_span": [12, 13], "input": "s", "output": "ş"}, {"op": "insert", "input_span": [15, 15], "output_span": [15, 16], "input": "", "output": " "}, {"op": "replace", "input_span": [44, 45], "output_span": [45, 46], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [46, 47], "output_span": [47, 48], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [88, 89], "output_span": [89, 90], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [92, 93], "output_span": [93, 94], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [95, 96], "output_span": [96, 97], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [97, 98], "output_span": [98, 99], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [132, 133], "output_span": [133, 134], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [137, 138], "output_span": [138, 139], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [143, 144], "output_span": [144, 145], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [145, 146], "output_span": [146, 147], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [148, 149], "output_span": [149, 150], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [15, 15], "output_span": [15, 16], "input": "", "output": " "}, {"op": "replace", "input_span": [109, 110], "output_span": [110, 111], "input": "ş", "output": "s"}]
```

## 6. validation:boun:news_1791:tam — sft_zero_shot:punctuation

```text
Girdi: Turkiye  Gazze  icin  ayakta
Hedef: Türkiye  Gazze  için  ayakta

Sonra: Türkiye Gazze için ayakta
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [1, 2], "output_span": [1, 2], "input": "u", "output": "ü"}, {"op": "delete", "input_span": [7, 8], "output_span": [7, 7], "input": " ", "output": ""}, {"op": "delete", "input_span": [15, 16], "output_span": [14, 14], "input": " ", "output": ""}, {"op": "replace", "input_span": [17, 18], "output_span": [15, 16], "input": "c", "output": "ç"}, {"op": "delete", "input_span": [20, 21], "output_span": [18, 18], "input": " ", "output": ""}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [8, 9], "output_span": [8, 8], "input": " ", "output": ""}, {"op": "delete", "input_span": [15, 16], "output_span": [14, 14], "input": " ", "output": ""}, {"op": "delete", "input_span": [20, 21], "output_span": [18, 18], "input": " ", "output": ""}]
```

## 7. validation:boun:news_1159:tam — sft_zero_shot:shorter

```text
Girdi: Kurdelayi esi Aysel Oymen ile birlikte kesen CHP lideri, kalici konutlarin onumuzdeki kisa kadar yetistirilmesini diledi.
Hedef: Kurdelayı eşi Aysel Öymen ile birlikte kesen CHP lideri, kalıcı konutların önümüzdeki kışa kadar yetiştirilmesini diledi.

Sonra: Kurdelayı esi Aysel Oymen ile birlikte kesen CHP lideri, kalıcı konutların onumuzdaki kısa kadar yetiştiğini diledi.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [8, 9], "output_span": [8, 9], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [60, 61], "output_span": [60, 61], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [62, 63], "output_span": [62, 63], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [72, 73], "output_span": [72, 73], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [82, 83], "output_span": [82, 83], "input": "e", "output": "a"}, {"op": "replace", "input_span": [87, 88], "output_span": [87, 88], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [101, 102], "output_span": [101, 102], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [104, 110], "output_span": [104, 105], "input": "rilmes", "output": "ğ"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [11, 12], "output_span": [11, 12], "input": "ş", "output": "s"}, {"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "Ö", "output": "O"}, {"op": "replace", "input_span": [75, 76], "output_span": [75, 76], "input": "ö", "output": "o"}, {"op": "replace", "input_span": [77, 78], "output_span": [77, 78], "input": "ü", "output": "u"}, {"op": "replace", "input_span": [79, 80], "output_span": [79, 80], "input": "ü", "output": "u"}, {"op": "replace", "input_span": [82, 83], "output_span": [82, 83], "input": "e", "output": "a"}, {"op": "replace", "input_span": [88, 89], "output_span": [88, 89], "input": "ş", "output": "s"}, {"op": "replace", "input_span": [104, 110], "output_span": [104, 105], "input": "rilmes", "output": "ğ"}]
```

## 8. validation:boun:ess_726:tam — sft_zero_shot:shorter

```text
Girdi: Ortada bir toplum varsa, insanlarin karsilikli saygi cercevesi icinde birbirlerine elestiri de olmalidir.
Hedef: Ortada bir toplum varsa, insanların karşılıklı saygı çerçevesi içinde birbirlerine eleştiri de olmalıdır.

Sonra: Ortada bir toplum varsa, insanların karşılıklı saygı çerçevesinde birbirlerine eleştiri de olmalıdır.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [33, 34], "output_span": [33, 34], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [39, 41], "output_span": [39, 41], "input": "si", "output": "şı"}, {"op": "replace", "input_span": [42, 43], "output_span": [42, 43], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [45, 46], "output_span": [45, 46], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [51, 52], "output_span": [51, 52], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [53, 54], "output_span": [53, 54], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [56, 57], "output_span": [56, 57], "input": "c", "output": "ç"}, {"op": "delete", "input_span": [61, 65], "output_span": [61, 61], "input": "i ic", "output": ""}, {"op": "replace", "input_span": [86, 87], "output_span": [82, 83], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [100, 101], "output_span": [96, 97], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [102, 103], "output_span": [98, 99], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [62, 66], "output_span": [62, 62], "input": " içi", "output": ""}]
```

## 9. validation:boun:news_1458:tam — sft_zero_shot:shorter

```text
Girdi: Kanalin icinde bulundugu Dogan Televizyon Merkezi'nin dokuz studyosuyla BBC'nin sahip oldugu bir altyapiya sahip oldugunu anlatan Yalcindag, Kanal D'nin onceligini "yayincilik sorumlugu ve etik degerlere baglilik" diye ozetledi.
Hedef: Kanalın içinde bulunduğu Doğan Televizyon Merkezi'nin dokuz stüdyosuyla BBC'nin sahip olduğu bir altyapıya sahip olduğunu anlatan Yalçındağ, Kanal D'nin önceliğini "yayıncılık sorumluğu ve etik değerlere bağlılık" diye özetledi.

Sonra: Kanalın içinde bulunduğu Doğan Televizyon Merkezi'nin dokuz studyosuyla BBC'nin sahip olduğu bir altyapıya sahip olduğunu anlatan Yalçındag, Kanal D'nin önünü "yayıncılık sorumluluğu ve etik değerlere bağlılık" diye özetledi.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [5, 6], "output_span": [5, 6], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [9, 10], "output_span": [9, 10], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [22, 23], "output_span": [22, 23], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [27, 28], "output_span": [27, 28], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [90, 91], "output_span": [90, 91], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [103, 104], "output_span": [103, 104], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [117, 118], "output_span": [117, 118], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [133, 135], "output_span": [133, 135], "input": "ci", "output": "çı"}, {"op": "replace", "input_span": [153, 154], "output_span": [153, 154], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [155, 161], "output_span": [155, 156], "input": "celigi", "output": "ü"}, {"op": "replace", "input_span": [162, 163], "output_span": [157, 158], "input": "i", "output": "ü"}, {"op": "replace", "input_span": [168, 169], "output_span": [163, 164], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [171, 172], "output_span": [166, 167], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [173, 174], "output_span": [168, 169], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [183, 184], "output_span": [178, 181], "input": "g", "output": "luğ"}, {"op": "replace", "input_span": [196, 197], "output_span": [193, 194], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [206, 207], "output_span": [203, 204], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [208, 209], "output_span": [205, 206], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [210, 211], "output_span": [207, 208], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [219, 220], "output_span": [216, 217], "input": "o", "output": "ö"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [62, 63], "output_span": [62, 63], "input": "ü", "output": "u"}, {"op": "replace", "input_span": [138, 139], "output_span": [138, 139], "input": "ğ", "output": "g"}, {"op": "replace", "input_span": [155, 161], "output_span": [155, 156], "input": "celiği", "output": "ü"}, {"op": "replace", "input_span": [162, 163], "output_span": [157, 158], "input": "i", "output": "ü"}, {"op": "insert", "input_span": [181, 181], "output_span": [176, 178], "input": "", "output": "lu"}]
```

## 10. validation:boun:ins_1352:tam — sft_zero_shot:longer

```text
Girdi: Bu ozellikleri nedeniyle matematik ogretmeni Yuzbasi Mustafa Efendi, ona "olgun" anlamina gelen Kemal adini verdi.
Hedef: Bu özellikleri nedeniyle matematik öğretmeni Yüzbaşı Mustafa Efendi, ona "olgun" anlamına gelen Kemal adını verdi.

Sonra: Bu özelliklerini nedeniyle matematik öğretmeni Yüzbaşı Mustafa Efendi, ona "olgun" anlamına gelen Kemal adını verdi.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [3, 4], "output_span": [3, 4], "input": "o", "output": "ö"}, {"op": "insert", "input_span": [13, 13], "output_span": [13, 15], "input": "", "output": "in"}, {"op": "replace", "input_span": [35, 37], "output_span": [37, 39], "input": "og", "output": "öğ"}, {"op": "replace", "input_span": [46, 47], "output_span": [48, 49], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [50, 52], "output_span": [52, 54], "input": "si", "output": "şı"}, {"op": "replace", "input_span": [86, 87], "output_span": [88, 89], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [104, 105], "output_span": [106, 107], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [106, 107], "output_span": [108, 109], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [13, 13], "output_span": [13, 15], "input": "", "output": "in"}]
```

## 11. validation:boun:news_1837:tam — sft_zero_shot:longer

```text
Girdi: GAZETECI OLDU: Bagdat'a ilerleyis sirasinda Irak askerlerinin atesinden kacarken bir kanala dusen Humvee tipi aractaki The Washington Post gazetesinin kose yazarlarindan Michael Kelly ile bir Amerikan askeri oldu.
Hedef: GAZETECİ ÖLDÜ: Bağdat'a ilerleyiş sırasında Irak askerlerinin ateşinden kaçarken bir kanala düşen Humvee tipi araçtaki The Washington Post gazetesinin köşe yazarlarından Michael Kelly ile bir Amerikan askeri öldü.

Sonra: GAZETECİ OLDU: Bagdat'a ilerleyiş sırasında Irak askerlerinin ateşinden kaçarken bir kanala düşen Humvee tipi aracındaki The Washington Post gazetesinin köşe yazarlarından Michael Kelly ile bir Amerikan askeri oldu.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [7, 8], "output_span": [7, 8], "input": "I", "output": "İ"}, {"op": "replace", "input_span": [32, 33], "output_span": [32, 33], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [35, 36], "output_span": [35, 36], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [39, 40], "output_span": [39, 40], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [65, 66], "output_span": [65, 66], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [74, 75], "output_span": [74, 75], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [93, 95], "output_span": [93, 95], "input": "us", "output": "üş"}, {"op": "replace", "input_span": [114, 115], "output_span": [114, 117], "input": "t", "output": "ınd"}, {"op": "replace", "input_span": [152, 154], "output_span": [154, 156], "input": "os", "output": "öş"}, {"op": "replace", "input_span": [164, 165], "output_span": [166, 167], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [9, 10], "output_span": [9, 10], "input": "Ö", "output": "O"}, {"op": "replace", "input_span": [12, 13], "output_span": [12, 13], "input": "Ü", "output": "U"}, {"op": "replace", "input_span": [17, 18], "output_span": [17, 18], "input": "ğ", "output": "g"}, {"op": "replace", "input_span": [113, 115], "output_span": [113, 117], "input": "çt", "output": "cınd"}, {"op": "replace", "input_span": [208, 209], "output_span": [210, 211], "input": "ö", "output": "o"}, {"op": "replace", "input_span": [211, 212], "output_span": [213, 214], "input": "ü", "output": "u"}]
```

## 12. validation:boun:ess_284:tam — sft_zero_shot:longer

```text
Girdi: Genis vitrinli, aydinlik tecimsel yapilarin yerini, agirbasli, ciddi gorunumlu yuksek bloklar almakta.
Hedef: Geniş vitrinli, aydınlık tecimsel yapıların yerini, ağırbaşlı, ciddi görünümlü yüksek bloklar almakta.

Sonra: Geniş vitrinli, aydınlatılmış teçimsel yapıların yerini, ağırbaşlı, ciddi görünümü yüksek bloklar almakta.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [4, 5], "output_span": [4, 5], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [19, 20], "output_span": [19, 20], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [22, 24], "output_span": [22, 29], "input": "ik", "output": "atılmış"}, {"op": "replace", "input_span": [27, 28], "output_span": [32, 33], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [37, 38], "output_span": [42, 43], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [41, 42], "output_span": [46, 47], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [53, 55], "output_span": [58, 60], "input": "gi", "output": "ğı"}, {"op": "replace", "input_span": [58, 59], "output_span": [63, 64], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [60, 61], "output_span": [65, 66], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [70, 71], "output_span": [75, 76], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [72, 73], "output_span": [77, 78], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [74, 75], "output_span": [79, 80], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [76, 78], "output_span": [81, 82], "input": "lu", "output": "ü"}, {"op": "replace", "input_span": [80, 81], "output_span": [84, 85], "input": "u", "output": "ü"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [22, 22], "output_span": [22, 24], "input": "", "output": "at"}, {"op": "replace", "input_span": [23, 24], "output_span": [25, 29], "input": "k", "output": "lmış"}, {"op": "replace", "input_span": [27, 28], "output_span": [32, 33], "input": "c", "output": "ç"}, {"op": "delete", "input_span": [76, 77], "output_span": [81, 81], "input": "l", "output": ""}]
```

## 13. validation:boun:ess_541:tam — sft_zero_shot:letter

```text
Girdi: Gumus yillari asan saygili bir beraberligin "parlak" isiklari, gunlerin prizmasinda once ikiye bolunup tuz parca olacaksa, ortadan ikiye ayrik Karaoglan, demokratik sol terazisinin hangi kefesinden sesleniyor?
Hedef: Gümüş yılları aşan saygılı bir beraberliğin "parlak" ışıkları, günlerin prizmasında önce ikiye bölünüp tuz parça olacaksa, ortadan ikiye ayrık Karaoğlan, demokratik sol terazisinin hangi kefesinden sesleniyor?

Sonra: Gümüş yılları asan saygılı bir beraberliğin "parlak" ışıkları, günlerin prizmasında önce ikiye bölünüp tuz parça olacaksa, ortadan ikiye ayırt Karaoğlan, demokratik sol terazisinin hangi kefesinden sesleniyor?
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [1, 2], "output_span": [1, 2], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [3, 5], "output_span": [3, 5], "input": "us", "output": "üş"}, {"op": "replace", "input_span": [7, 8], "output_span": [7, 8], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [12, 13], "output_span": [12, 13], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [23, 24], "output_span": [23, 24], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [25, 26], "output_span": [25, 26], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [40, 41], "output_span": [40, 41], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [53, 56], "output_span": [53, 56], "input": "isi", "output": "ışı"}, {"op": "replace", "input_span": [60, 61], "output_span": [60, 61], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [64, 65], "output_span": [64, 65], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [79, 80], "output_span": [79, 80], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [84, 85], "output_span": [84, 85], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [96, 97], "output_span": [96, 97], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [98, 99], "output_span": [98, 99], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [100, 101], "output_span": [100, 101], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [110, 111], "output_span": [110, 111], "input": "c", "output": "ç"}, {"op": "insert", "input_span": [139, 139], "output_span": [139, 140], "input": "", "output": "ı"}, {"op": "replace", "input_span": [140, 142], "output_span": [141, 142], "input": "ik", "output": "t"}, {"op": "replace", "input_span": [148, 149], "output_span": [148, 149], "input": "g", "output": "ğ"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "ş", "output": "s"}, {"op": "insert", "input_span": [139, 139], "output_span": [139, 140], "input": "", "output": "ı"}, {"op": "replace", "input_span": [140, 142], "output_span": [141, 142], "input": "ık", "output": "t"}]
```

## 14. validation:boun:ins_574:tam — sft_zero_shot:letter

```text
Girdi: Onun su sozu akil ve mantiga verdigi degeri en guzel sekilde ifade eder: "Bizim akil, mantik ve zeka ile hareket etmek en buyuk ozelligimizdir.
Hedef: Onun şu sözü akıl ve mantığa verdiği değeri en güzel şekilde ifade eder: "Bizim akıl, mantık ve zeka ile hareket etmek en büyük özelliğimizdir.

Sonra: Onun şu sözü akıl ve mantıka verdiği değeri en güzel şekilde ifade eder: "Bizim akıl, mantık ve zeka ile hareket etmek en büyük özelligimizdir.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [5, 6], "output_span": [5, 6], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [9, 10], "output_span": [9, 10], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [11, 12], "output_span": [11, 12], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [25, 27], "output_span": [25, 27], "input": "ig", "output": "ık"}, {"op": "replace", "input_span": [34, 35], "output_span": [34, 35], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [39, 40], "output_span": [39, 40], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [48, 49], "output_span": [48, 49], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [53, 54], "output_span": [53, 54], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [82, 83], "output_span": [82, 83], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [90, 91], "output_span": [90, 91], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [123, 124], "output_span": [123, 124], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [125, 126], "output_span": [125, 126], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [128, 129], "output_span": [128, 129], "input": "o", "output": "ö"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [26, 27], "output_span": [26, 27], "input": "ğ", "output": "k"}, {"op": "replace", "input_span": [134, 135], "output_span": [134, 135], "input": "ğ", "output": "g"}]
```

## 15. validation:boun:ins_1197:koruma — sft_zero_shot:letter

```text
Girdi: Gezegencik cik cik cik,
Hedef: Gezegencik cik cik cik,

Sonra: Gezegencik çıç çıç çıç,
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [11, 14], "output_span": [11, 14], "input": "cik", "output": "çıç"}, {"op": "replace", "input_span": [15, 18], "output_span": [15, 18], "input": "cik", "output": "çıç"}, {"op": "replace", "input_span": [19, 22], "output_span": [19, 22], "input": "cik", "output": "çıç"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [11, 14], "output_span": [11, 14], "input": "cik", "output": "çıç"}, {"op": "replace", "input_span": [15, 18], "output_span": [15, 18], "input": "cik", "output": "çıç"}, {"op": "replace", "input_span": [19, 22], "output_span": [19, 22], "input": "cik", "output": "çıç"}]
```

## 16. validation:boun:pop_1250:tam — sft_zero_shot:unalignable

```text
Girdi: Bu paralari biriktirmek icin atalarimiz taa Afrika'da, Ortadogu'da, Hindistan'da ve dunyanin dort bir yaninda az mi mucadele edip kan doktu, Az mi kole ticareti yapti? Simdi bunlari tek tek saymanin ne yeri, ne de zamani...
Hedef: Bu paraları biriktirmek için atalarımız taa Afrika'da, Ortadoğu'da, Hindistan'da ve dünyanın dört bir yanında az mı mücadele edip kan döktü, Az mı köle ticareti yaptı? Şimdi bunları tek tek saymanın ne yeri, ne de zamanı...

Sonra: Bu paraları biriktirmek için atalarımız ta' Afrika'da, Ortadöğü'da, Hindistan'da ve dünyanın dört bir yanında az mı mücadele edip kan döktü, Az mı kole ticareti yaptı? Şimdi bunları tek tek saymanın ne yeri, ne de zamanı...
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [10, 11], "output_span": [10, 11], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [25, 26], "output_span": [25, 26], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [35, 36], "output_span": [35, 36], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [37, 38], "output_span": [37, 38], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [42, 43], "output_span": [42, 43], "input": "a", "output": "'"}, {"op": "replace", "input_span": [60, 63], "output_span": [60, 63], "input": "ogu", "output": "öğü"}, {"op": "replace", "input_span": [85, 86], "output_span": [85, 86], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [90, 91], "output_span": [90, 91], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [94, 95], "output_span": [94, 95], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [105, 106], "output_span": [105, 106], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [114, 115], "output_span": [114, 115], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [117, 118], "output_span": [117, 118], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [135, 136], "output_span": [135, 136], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [138, 139], "output_span": [138, 139], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [145, 146], "output_span": [145, 146], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [165, 166], "output_span": [165, 166], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [168, 169], "output_span": [168, 169], "input": "S", "output": "Ş"}, {"op": "replace", "input_span": [180, 181], "output_span": [180, 181], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [196, 197], "output_span": [196, 197], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [219, 220], "output_span": [219, 220], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [42, 43], "output_span": [42, 43], "input": "a", "output": "'"}, {"op": "replace", "input_span": [60, 61], "output_span": [60, 61], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [62, 63], "output_span": [62, 63], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [148, 149], "output_span": [148, 149], "input": "ö", "output": "o"}]
```

## 17. validation:boun:pop_1949:tam — sft_five_shot:limit

```text
Girdi: Kimisi de acikgozluluk edip, manikur pedikur'den isteklerde bulunmayi daha uygun gormustu:
Hedef: Kimisi de açıkgözlülük edip, manikür pedikür'den isteklerde bulunmayı daha uygun görmüştü:

Sonra: Kimisi de açık gözlüklü kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı k
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [11, 13], "output_span": [11, 13], "input": "ci", "output": "çı"}, {"op": "insert", "input_span": [14, 14], "output_span": [14, 15], "input": "", "output": " "}, {"op": "replace", "input_span": [15, 16], "output_span": [16, 17], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [18, 19], "output_span": [19, 21], "input": "u", "output": "ük"}, {"op": "replace", "input_span": [20, 21], "output_span": [22, 24], "input": "u", "output": "ü "}, {"op": "insert", "input_span": [22, 22], "output_span": [25, 28], "input": "", "output": "ıyı"}, {"op": "replace", "input_span": [23, 30], "output_span": [29, 30], "input": "edip, m", "output": "ş"}, {"op": "replace", "input_span": [32, 33], "output_span": [32, 35], "input": "i", "output": "lı "}, {"op": "replace", "input_span": [34, 36], "output_span": [36, 39], "input": "ur", "output": "ıyı"}, {"op": "replace", "input_span": [37, 41], "output_span": [40, 46], "input": "pedi", "output": "şanlı "}, {"op": "replace", "input_span": [42, 47], "output_span": [47, 53], "input": "ur'de", "output": "ıyı şa"}, {"op": "insert", "input_span": [48, 48], "output_span": [54, 56], "input": "", "output": "lı"}, {"op": "delete", "input_span": [49, 53], "output_span": [57, 57], "input": "iste", "output": ""}, {"op": "insert", "input_span": [54, 54], "output_span": [58, 65], "input": "", "output": "ıyı şan"}, {"op": "replace", "input_span": [55, 59], "output_span": [66, 67], "input": "erde", "output": "ı"}, {"op": "replace", "input_span": [60, 62], "output_span": [68, 76], "input": "bu", "output": "kıyı şan"}, {"op": "replace", "input_span": [63, 64], "output_span": [77, 86], "input": "u", "output": "ı kıyı şa"}, {"op": "replace", "input_span": [65, 66], "output_span": [87, 96], "input": "m", "output": "lı kıyı ş"}, {"op": "insert", "input_span": [67, 67], "output_span": [97, 103], "input": "", "output": "nlı kı"}, {"op": "replace", "input_span": [68, 69], "output_span": [104, 105], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [70, 71], "output_span": [106, 107], "input": "d", "output": "ş"}, {"op": "replace", "input_span": [72, 73], "output_span": [108, 118], "input": "h", "output": "nlı kıyı ş"}, {"op": "insert", "input_span": [74, 74], "output_span": [119, 122], "input": "", "output": "nlı"}, {"op": "replace", "input_span": [75, 76], "output_span": [123, 125], "input": "u", "output": "kı"}, {"op": "replace", "input_span": [77, 79], "output_span": [126, 130], "input": "gu", "output": "ı şa"}, {"op": "insert", "input_span": [80, 80], "output_span": [131, 133], "input": "", "output": "lı"}, {"op": "replace", "input_span": [81, 90], "output_span": [134, 476], "input": "gormustu:", "output": "kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı k"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [14, 14], "output_span": [14, 15], "input": "", "output": " "}, {"op": "insert", "input_span": [19, 19], "output_span": [20, 21], "input": "", "output": "k"}, {"op": "insert", "input_span": [21, 21], "output_span": [23, 24], "input": "", "output": " "}, {"op": "replace", "input_span": [22, 67], "output_span": [25, 26], "input": " edip, manikür pedikür'den isteklerde bulunma", "output": "ı"}, {"op": "replace", "input_span": [70, 71], "output_span": [29, 30], "input": "d", "output": "ş"}, {"op": "replace", "input_span": [72, 73], "output_span": [31, 41], "input": "h", "output": "nlı kıyı ş"}, {"op": "insert", "input_span": [74, 74], "output_span": [42, 45], "input": "", "output": "nlı"}, {"op": "replace", "input_span": [75, 76], "output_span": [46, 48], "input": "u", "output": "kı"}, {"op": "replace", "input_span": [77, 79], "output_span": [49, 53], "input": "gu", "output": "ı şa"}, {"op": "insert", "input_span": [80, 80], "output_span": [54, 56], "input": "", "output": "lı"}, {"op": "replace", "input_span": [81, 86], "output_span": [57, 62], "input": "görmü", "output": "kıyı "}, {"op": "replace", "input_span": [87, 90], "output_span": [63, 476], "input": "tü:", "output": "anlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı kıyı şanlı k"}]
```

## 18. validation:boun:ins_1051:kismi — sft_five_shot:case

```text
Girdi: tubitak: Alan adini gösterir.
Hedef: tubitak: Alan adını gösterir.

Sonra: TÜbıtak: Alan adını gösterir.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [0, 2], "output_span": [0, 2], "input": "tu", "output": "TÜ"}, {"op": "replace", "input_span": [3, 4], "output_span": [3, 4], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [16, 17], "output_span": [16, 17], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [18, 19], "output_span": [18, 19], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [0, 2], "output_span": [0, 2], "input": "tu", "output": "TÜ"}, {"op": "replace", "input_span": [3, 4], "output_span": [3, 4], "input": "i", "output": "ı"}]
```

## 19. validation:boun:pop_120:kismi — sft_five_shot:case

```text
Girdi: - Geçmis yaşamımı anımsamaktan dolayı mutluyum.
Hedef: - Geçmiş yaşamımı anımsamaktan dolayı mutluyum.

Sonra: - geçmiş yaşamımı anımsamaktan dolayı mutluyum.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [2, 3], "output_span": [2, 3], "input": "G", "output": "g"}, {"op": "replace", "input_span": [7, 8], "output_span": [7, 8], "input": "s", "output": "ş"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [2, 3], "output_span": [2, 3], "input": "G", "output": "g"}]
```

## 20. validation:boun:pop_1021:kismi — sft_five_shot:case

```text
Girdi: Tarihin Doktor Tarafından Ileri Alınması
Hedef: Tarihin Doktor Tarafından İleri Alınması

Sonra: Tarihin Doktor tarafından ileri alınması
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "T", "output": "t"}, {"op": "replace", "input_span": [26, 27], "output_span": [26, 27], "input": "I", "output": "i"}, {"op": "replace", "input_span": [32, 33], "output_span": [32, 33], "input": "A", "output": "a"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "T", "output": "t"}, {"op": "replace", "input_span": [26, 27], "output_span": [26, 27], "input": "İ", "output": "i"}, {"op": "replace", "input_span": [32, 33], "output_span": [32, 33], "input": "A", "output": "a"}]
```

## 21. validation:boun:news_719:kismi — sft_five_shot:punctuation

```text
Girdi: Socrates, farkli bir kultürü öğrenmek, yabancı bir universitede egitim görmek, yeni arkadaslar edinmek, başka bir dil ögrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmis bir program.
Hedef: Socrates, farklı bir kültürü öğrenmek, yabancı bir üniversitede eğitim görmek, yeni arkadaşlar edinmek, başka bir dil öğrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmış bir program.

Sonra: Socrates, farklı bir kültürü öğrenmek, yabancı bir üniversite de eğitim görmek, yeni arkadaşlar edinmek, başka bir dil öğrenmek ya da hepsini bir arada yapmak isteyenler için tasarlanmış bir program.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [15, 16], "output_span": [15, 16], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [22, 23], "output_span": [22, 23], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [51, 52], "output_span": [51, 52], "input": "u", "output": "ü"}, {"op": "insert", "input_span": [61, 61], "output_span": [61, 62], "input": "", "output": " "}, {"op": "replace", "input_span": [65, 66], "output_span": [66, 67], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [90, 91], "output_span": [91, 92], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [119, 120], "output_span": [120, 121], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [183, 185], "output_span": [184, 186], "input": "is", "output": "ış"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [61, 61], "output_span": [61, 62], "input": "", "output": " "}]
```

## 22. validation:boun:ins_1381:tam — sft_five_shot:punctuation

```text
Girdi: - Ay'i ve yildizlari goruyorum dayicigim.
Hedef: - Ay'ı ve yıldızları görüyorum dayıcığım.

Sonra: - Ayı ve yıldızları görüyorum dayıçığım.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [4, 6], "output_span": [4, 5], "input": "'i", "output": "ı"}, {"op": "replace", "input_span": [11, 12], "output_span": [10, 11], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [14, 15], "output_span": [13, 14], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [19, 20], "output_span": [18, 19], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [22, 23], "output_span": [21, 22], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [24, 25], "output_span": [23, 24], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [34, 39], "output_span": [33, 38], "input": "icigi", "output": "ıçığı"}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [4, 5], "output_span": [4, 4], "input": "'", "output": ""}, {"op": "replace", "input_span": [35, 36], "output_span": [34, 35], "input": "c", "output": "ç"}]
```

## 23. validation:boun:news_1791:tam — sft_five_shot:punctuation

```text
Girdi: Turkiye  Gazze  icin  ayakta
Hedef: Türkiye  Gazze  için  ayakta

Sonra: Türkiye Gazze için ayakta
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [1, 2], "output_span": [1, 2], "input": "u", "output": "ü"}, {"op": "delete", "input_span": [7, 8], "output_span": [7, 7], "input": " ", "output": ""}, {"op": "delete", "input_span": [15, 16], "output_span": [14, 14], "input": " ", "output": ""}, {"op": "replace", "input_span": [17, 18], "output_span": [15, 16], "input": "c", "output": "ç"}, {"op": "delete", "input_span": [20, 21], "output_span": [18, 18], "input": " ", "output": ""}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [8, 9], "output_span": [8, 8], "input": " ", "output": ""}, {"op": "delete", "input_span": [15, 16], "output_span": [14, 14], "input": " ", "output": ""}, {"op": "delete", "input_span": [20, 21], "output_span": [18, 18], "input": " ", "output": ""}]
```

## 24. validation:boun:ins_1489:kismi — sft_five_shot:shorter

```text
Girdi: Biz dünyanın uçsuz bucaksiz diyarlarinda ne kadar dolaşirsak dolasalim, sonuçta hep sokagimızin insaniyiz.
Hedef: Biz dünyanın uçsuz bucaksız diyarlarında ne kadar dolaşırsak dolaşalım, sonuçta hep sokağımızın insanıyız.

Sonra: Biz dünyanın uçsuz bucaksız diyarlarında ne kadar dolaşırsk dolaşalım, sonuçta hep sokağımızın insanıyız.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [25, 26], "output_span": [25, 26], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [36, 37], "output_span": [36, 37], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [55, 56], "output_span": [55, 56], "input": "i", "output": "ı"}, {"op": "delete", "input_span": [58, 59], "output_span": [58, 58], "input": "a", "output": ""}, {"op": "replace", "input_span": [65, 66], "output_span": [64, 65], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [68, 69], "output_span": [67, 68], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [88, 90], "output_span": [87, 89], "input": "gi", "output": "ğı"}, {"op": "replace", "input_span": [93, 94], "output_span": [92, 93], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [101, 102], "output_span": [100, 101], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [103, 104], "output_span": [102, 103], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [58, 59], "output_span": [58, 58], "input": "a", "output": ""}]
```

## 25. validation:boun:bio_192:tam — sft_five_shot:shorter

```text
Girdi: Sen hic padisah karisinin kocasini bosayip sadrazamla evlendigini duydun mu?
Hedef: Sen hiç padişah karısının kocasını boşayıp sadrazamla evlendiğini duydun mu?

Sonra: Sen hiç paçışah karısının çocuğını boşayıp sadrazamla evlendğini duydun mu?
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [6, 7], "output_span": [6, 7], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [10, 13], "output_span": [10, 13], "input": "dis", "output": "çış"}, {"op": "replace", "input_span": [19, 20], "output_span": [19, 20], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [21, 22], "output_span": [21, 22], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [23, 24], "output_span": [23, 24], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [26, 27], "output_span": [26, 27], "input": "k", "output": "ç"}, {"op": "replace", "input_span": [29, 32], "output_span": [29, 32], "input": "asi", "output": "uğı"}, {"op": "replace", "input_span": [33, 34], "output_span": [33, 34], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [37, 38], "output_span": [37, 38], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [40, 41], "output_span": [40, 41], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [60, 62], "output_span": [60, 61], "input": "ig", "output": "ğ"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [10, 12], "output_span": [10, 12], "input": "di", "output": "çı"}, {"op": "replace", "input_span": [26, 27], "output_span": [26, 27], "input": "k", "output": "ç"}, {"op": "replace", "input_span": [29, 31], "output_span": [29, 31], "input": "as", "output": "uğ"}, {"op": "delete", "input_span": [60, 61], "output_span": [60, 60], "input": "i", "output": ""}]
```

## 26. validation:boun:ess_80:kismi — sft_five_shot:shorter

```text
Girdi: Dinin mahiyetini doğru anlayabilmek icin şu soru karsisındaki fikri tavrimizın berraklasması gerekiyor: din, dunyayı olağanustü guclerle açıklamaya mı calişiyor, yoksa bir hakikati teblig mi ediyor?"Eylem " e katılanlar buyük bir olasilikla çeşitli goruşlerden insanlar...
Hedef: Dinin mahiyetini doğru anlayabilmek için şu soru karşısındaki fikri tavrımızın berraklaşması gerekiyor: din, dünyayı olağanüstü güçlerle açıklamaya mı çalışıyor, yoksa bir hakikati tebliğ mi ediyor?"Eylem " e katılanlar büyük bir olasılıkla çeşitli görüşlerden insanlar...

Sonra: Dinin mahiyetini doğru anlayabilmek için şu soru karşısında fikri taşımızın berraklaşması gerekiyor: din, dünyayı olağanüstü güçlerle açıklamaya mı çalışıyor, yoksa bir hakikatı teblig mi ediyor?"Eylem " e katılanlar büyük bir olasılıkla çeşitli görüşlerden insanlar...
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [37, 38], "output_span": [37, 38], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [52, 54], "output_span": [52, 54], "input": "si", "output": "şı"}, {"op": "delete", "input_span": [59, 61], "output_span": [59, 59], "input": "ki", "output": ""}, {"op": "replace", "input_span": [70, 73], "output_span": [68, 70], "input": "vri", "output": "şı"}, {"op": "replace", "input_span": [74, 75], "output_span": [71, 72], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [87, 88], "output_span": [84, 85], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [110, 111], "output_span": [107, 108], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [123, 124], "output_span": [120, 121], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [129, 131], "output_span": [126, 128], "input": "uc", "output": "üç"}, {"op": "replace", "input_span": [151, 152], "output_span": [148, 149], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [154, 155], "output_span": [151, 152], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [156, 157], "output_span": [153, 154], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [179, 180], "output_span": [176, 177], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [221, 222], "output_span": [218, 219], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [234, 235], "output_span": [231, 232], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [236, 237], "output_span": [233, 234], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [250, 251], "output_span": [247, 248], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [252, 253], "output_span": [249, 250], "input": "u", "output": "ü"}]
```
Hedef → çıktı diff:
```json
[{"op": "delete", "input_span": [59, 61], "output_span": [59, 59], "input": "ki", "output": ""}, {"op": "replace", "input_span": [70, 72], "output_span": [68, 69], "input": "vr", "output": "ş"}, {"op": "replace", "input_span": [179, 180], "output_span": [176, 177], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [186, 187], "output_span": [183, 184], "input": "ğ", "output": "g"}]
```

## 27. validation:boun:pop_717:koruma — sft_five_shot:longer

```text
Girdi: Öte yandan userler kendilerini fikirleriyle, (yanlış yada eksik fikirler olsa da) ispat etme çabası içinde olurlar.
Hedef: Öte yandan userler kendilerini fikirleriyle, (yanlış yada eksik fikirler olsa da) ispat etme çabası içinde olurlar.

Sonra: Öte yandan kullanıcılar kendilerini fikirleriyle, (yanlış ya da eksik fikirler olsa da) ispat etme çabası içinde olurlar.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "insert", "input_span": [11, 11], "output_span": [11, 12], "input": "", "output": "k"}, {"op": "delete", "input_span": [12, 15], "output_span": [13, 13], "input": "ser", "output": ""}, {"op": "replace", "input_span": [16, 17], "output_span": [14, 22], "input": "e", "output": "lanıcıla"}, {"op": "insert", "input_span": [55, 55], "output_span": [60, 61], "input": "", "output": " "}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [11, 11], "output_span": [11, 12], "input": "", "output": "k"}, {"op": "delete", "input_span": [12, 15], "output_span": [13, 13], "input": "ser", "output": ""}, {"op": "replace", "input_span": [16, 17], "output_span": [14, 22], "input": "e", "output": "lanıcıla"}, {"op": "insert", "input_span": [55, 55], "output_span": [60, 61], "input": "", "output": " "}]
```

## 28. validation:boun:ins_754:tam — sft_five_shot:longer

```text
Girdi: Yeke ile dumen tutmak baslangicta biraz karmasiktir.
Hedef: Yeke ile dümen tutmak başlangıçta biraz karmaşıktır.

Sonra: Yeke ile dümengi tutmak başlangıçta biraz karmasıkştır.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [10, 11], "output_span": [10, 11], "input": "u", "output": "ü"}, {"op": "insert", "input_span": [14, 14], "output_span": [14, 16], "input": "", "output": "gi"}, {"op": "replace", "input_span": [24, 25], "output_span": [26, 27], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [29, 31], "output_span": [31, 33], "input": "ic", "output": "ıç"}, {"op": "replace", "input_span": [46, 47], "output_span": [48, 49], "input": "i", "output": "ı"}, {"op": "insert", "input_span": [48, 48], "output_span": [50, 51], "input": "", "output": "ş"}, {"op": "replace", "input_span": [49, 50], "output_span": [52, 53], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [14, 14], "output_span": [14, 16], "input": "", "output": "gi"}, {"op": "replace", "input_span": [45, 46], "output_span": [47, 48], "input": "ş", "output": "s"}, {"op": "insert", "input_span": [48, 48], "output_span": [50, 51], "input": "", "output": "ş"}]
```

## 29. validation:boun:pop_272:kismi — sft_five_shot:longer

```text
Girdi: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda gormezden gelmeyi, hesap disi birakmayı en çok arzu edeceginiz sey bu karmasıkliktır.
Hedef: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda görmezden gelmeyi, hesap dışı bırakmayı en çok arzu edeceğiniz şey bu karmaşıklıktır.

Sonra: Futbol gibi karmaşık bir oyuna taraftar gözüyle baktığınızda görmezden gelmeyi, hesap dışındaki bırakmayı en çok arzu edeceğiniz şey bu karmaşıklıktır.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [62, 63], "output_span": [62, 63], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [87, 89], "output_span": [87, 94], "input": "is", "output": "ışındak"}, {"op": "replace", "input_span": [92, 93], "output_span": [97, 98], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [118, 119], "output_span": [123, 124], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [124, 125], "output_span": [129, 130], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [136, 137], "output_span": [141, 142], "input": "s", "output": "ş"}, {"op": "replace", "input_span": [140, 141], "output_span": [145, 146], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "insert", "input_span": [90, 90], "output_span": [90, 95], "input": "", "output": "ndaki"}]
```

## 30. validation:boun:news_1964:tam — sft_five_shot:letter

```text
Girdi: Ayni donemde dunyadaki internet kullanici sayisi ise 183 milyondan 683 milyon kisiye cikti.
Hedef: Aynı dönemde dünyadaki internet kullanıcı sayısı ise 183 milyondan 683 milyon kişiye çıktı.

Sonra: Aynı dönemde dünyadaki internet kullanıcı sayısı ise 183 milyondan 683 milyon kişeye çıktı.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [3, 4], "output_span": [3, 4], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [6, 7], "output_span": [6, 7], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [14, 15], "output_span": [14, 15], "input": "u", "output": "ü"}, {"op": "replace", "input_span": [38, 39], "output_span": [38, 39], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [40, 41], "output_span": [40, 41], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [45, 46], "output_span": [45, 46], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [47, 48], "output_span": [47, 48], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [80, 82], "output_span": [80, 82], "input": "si", "output": "şe"}, {"op": "replace", "input_span": [85, 87], "output_span": [85, 87], "input": "ci", "output": "çı"}, {"op": "replace", "input_span": [89, 90], "output_span": [89, 90], "input": "i", "output": "ı"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [81, 82], "output_span": [81, 82], "input": "i", "output": "e"}]
```

## 31. validation:boun:ess_1629:tam — sft_five_shot:letter

```text
Girdi: Ekonomi ve psikolojiye de, yarar dogrusu.
Hedef: Ekonomi ve psikolojiye de, yarar doğrusu.

Sonra: Ekonomi ve psikolojiye de, yarar doğruyu.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [35, 36], "output_span": [35, 36], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [38, 39], "output_span": [38, 39], "input": "s", "output": "y"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [38, 39], "output_span": [38, 39], "input": "s", "output": "y"}]
```

## 32. validation:boun:ins_1197:koruma — sft_five_shot:letter

```text
Girdi: Gezegencik cik cik cik,
Hedef: Gezegencik cik cik cik,

Sonra: Gezegencik çıç çıç çıç,
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [11, 14], "output_span": [11, 14], "input": "cik", "output": "çıç"}, {"op": "replace", "input_span": [15, 18], "output_span": [15, 18], "input": "cik", "output": "çıç"}, {"op": "replace", "input_span": [19, 22], "output_span": [19, 22], "input": "cik", "output": "çıç"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [11, 14], "output_span": [11, 14], "input": "cik", "output": "çıç"}, {"op": "replace", "input_span": [15, 18], "output_span": [15, 18], "input": "cik", "output": "çıç"}, {"op": "replace", "input_span": [19, 22], "output_span": [19, 22], "input": "cik", "output": "çıç"}]
```

## 33. validation:boun:bio_1336:tam — sft_five_shot:unalignable

```text
Girdi: Ferruh Beyin ogrendigine gore ilacin fiyati 90 milyon liraymis.
Hedef: Ferruh Beyin öğrendiğine göre ilacın fiyatı 90 milyon liraymış.

Sonra: Ferruh Beyin öğrendiğine göre ilaçın fiyatı 90 milyon lira mış.
```



Karakter diff (0 tabanlı, bitiş hariç):
```json
[{"op": "replace", "input_span": [13, 15], "output_span": [13, 15], "input": "og", "output": "öğ"}, {"op": "replace", "input_span": [20, 21], "output_span": [20, 21], "input": "g", "output": "ğ"}, {"op": "replace", "input_span": [26, 27], "output_span": [26, 27], "input": "o", "output": "ö"}, {"op": "replace", "input_span": [33, 35], "output_span": [33, 35], "input": "ci", "output": "çı"}, {"op": "replace", "input_span": [42, 43], "output_span": [42, 43], "input": "i", "output": "ı"}, {"op": "replace", "input_span": [58, 59], "output_span": [58, 59], "input": "y", "output": " "}, {"op": "replace", "input_span": [60, 62], "output_span": [60, 62], "input": "is", "output": "ış"}]
```
Hedef → çıktı diff:
```json
[{"op": "replace", "input_span": [33, 34], "output_span": [33, 34], "input": "c", "output": "ç"}, {"op": "replace", "input_span": [58, 59], "output_span": [58, 59], "input": "y", "output": " "}]
```
