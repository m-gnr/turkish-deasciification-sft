# SFT öncesi hata ve metrik incelemesi

40 farklı doğrulama girdisinde iki koşulun toplam 80 çıktısı incelendi. Seçim: Python random.Random(42), doğrulama sırasındaki dört havuzdan sırasıyla 25/5/5/5 örnek. Havuzlar: yalnız five-shot ihlali (250), iki koşulda ihlal (197), yalnız zero-shot ihlali (40), iki koşul da uyumlu ancak five-shot tam eşleşmiyor (245). Bu amaçlı tabakalı örneklem hata yaygınlığı tahmini değildir. Test kümesi açılmadı.

## Bulgular

Five-shot 250 yeni ihlal üretirken 40 ihlali gideriyor: net +210 ihlal. İncelenen yeni ihlallerde kelime/ek yeniden yazımı ve silme baskın; ayrıca başlık harflerini küçültme, mevcut ğ harfini g yapma ve apostrof öncesi boşluğu kaldırma var. Örnekler açıklama eklemekten çok metni dönüştürme sorununa işaret ediyor. Bu gözlem nedensel mekanizma kanıtı değildir. Beş gösterim kurallara uygun; gösterim seçiminin etkisi ayrıca deney gerektirir.

Girdiyi aynen bırakma 432→154; tam eşleşme 152→187; katı uyum 663→453. Model daha çok müdahale ediyor, hem doğru düzeltme hem izinsiz değişiklik artıyor. İki koşulda da token sınırına ulaşan çıktı yok.

## Metrik denetimi

Kaydedilmiş 1.800 model çıktısı ve 900 identity çıktısı yeniden puanlandı. Örnek puanları, özetler, kategori sonuçları ve kaydedilmiş dosya SHA-256 özetleri birebir eşleşti. Metrik formülleri değiştirilmedi.

- `candidate_accuracy`: NFC sonrasında girdide cgiosuCGIOSU olan konumlar; karakter sayıları üzerinden mikro ortalama. Kural ihlali varsa o cümlenin bütün aday konumları başarısız. Payda iki koşulda da 17.289. Gerekli düzeltme ve aday koruma pay/payda toplamlarına eşit.
- `missing_correction`: yalnız uzunluk eşitse, gerekli değişikliğin yapılmayıp özgün harfin bırakıldığı konum sayısı. Uzunluğu farklı çıktıda 0, “hiç eksik yok” anlamına gelmez; konumsal sayım yapılmamıştır.
- `unalignable`: yalnız NFC sonrası uzunluk farkını gösterir. Aynı uzunluktaki silme/ekleme veya yeniden yazım güvenilir dilsel hizalama sağlamaz; alanın anlamı bu sınırla okunmalıdır.
- Uzunluğu eşit çıktılar 697→547; uzunluğu farklı çıktılardaki gerekli konumlar 1.636→2.820. Bu nedenle ham eksik düzeltme sayısını tek başına iki koşul arasında başarı göstergesi olarak kullanmayın.
- `candidate_accuracy_compliant_only` seçilmiş farklı alt kümeleri karşılaştırır; ana başarı metriği değildir.
- Hata sınıfları örtüşür; rule_violation/unalignable cümle, missing/unnecessary karakter, wrongly_changed_word kelime birimindedir. Toplanarak toplam hata oranı elde edilmez.

## Sabit baseline

`reports/baselines/boun-v1-pre-sft.json` model sürümünü, veri/çıktı/kod özetlerini, doğrulanmış sonuçları ve eğitim sonrası karşılaştırma protokolünü tutar. Orijinal koşu dosyaları korunur. SFT ve istem seçimi doğrulamada yapılır; seçim sabitlenmeden nihai test ölçülmez.

## İncelenen örnekler

### 1. validation:boun:news_388:kismi

Grup: `five_only_violation`

```text
Girdi: Bu yaş diliminin en az calışanlari ise Slovakya, Belçika ve Fransa'da.
Hedef: Bu yaş diliminin en az çalışanları ise Slovakya, Belçika ve Fransa'da.
Zero:  Bu yaş diliminin en az calışanlari ise Slovakya, Belçika ve Fransa'da.
Five:  Bu yaş diliminin en az çalışanları Slovakya, Belçika ve Fransa'da.
```

‘ise’ kelimesi silinmiş; gerekli harf düzeltmeleri yapılsa da çıktı geçersiz.

### 2. validation:boun:ess_1462:tam

Grup: `five_only_violation`

```text
Girdi: O yuzden hava karardiktan sonra hicbirini kacirmadan, butun yildizlari ayni anda gorebiliyorsunuz.
Hedef: O yüzden hava karardıktan sonra hiçbirini kaçırmadan, bütün yıldızları aynı anda görebiliyorsunuz.
Zero:  O yuzden hava karardiktan sonra hicbirini kacirmadan, butun yildizlari ayni anda gorebiliyorsunuz.
Five:  O yüzden hava karardığında hiçbirini kâcmadan, bütün yıldızları aynı anda görebiliyorsunuz.
```

‘karardıktan sonra’ → ‘karardığında’; ‘kaçırmadan’ bozulmuş, izin verilmeyen â eklenmiş.

### 3. validation:boun:pop_277:kismi

Grup: `five_only_violation`

```text
Girdi: Seçtigi kisiyi esi olmaya layık gorduyse, tüm askını ona verecek, tum gücüyle yanında yer alacaktir.
Hedef: Seçtiği kişiyi eşi olmaya layık gördüyse, tüm aşkını ona verecek, tüm gücüyle yanında yer alacaktır.
Zero:  Seçtigi kisiyi esi olmaya layık gorduyse, tüm askını ona verecek, tüm gücüyle yanında yer alacaktir.
Five:  Seçtiği kisiyi esim olmaya layık görse, tüm askını ona verecek, tüm gücüyle yanında yer alacaktır.
```

‘esi’ → ‘esim’, ‘gorduyse’ → ‘görse’: ek ve kelime yapısı değişmiş.

### 4. validation:boun:news_403:tam

Grup: `five_only_violation`

```text
Girdi: Hele bizim gibi topluma ornek olmasi gereken futbolcularin egitimli olmalari cok onem arz ediyor.
Hedef: Hele bizim gibi topluma örnek olması gereken futbolcuların eğitimli olmaları çok önem arz ediyor.
Zero:  Hele bizim gibi topluma örnek olmasi gereken futbolcuların eğitimli olmalari çok önem arz ediyor.
Five:  Hele bizim gibi topluma örnek olmasi gereken futbolcuların eğitilmiş olmalari çok önem arz ediyor.
```

‘egitimli’ → ‘eğitilmiş’: harf geri yüklemenin ötesinde ek değişikliği.

### 5. validation:boun:ess_1101:tam

Grup: `five_only_violation`

```text
Girdi: Minik Faruk, o anda kucucuk akliyla sunun farkina vardi.
Hedef: Minik Faruk, o anda küçücük aklıyla şunun farkına vardı.
Zero:  Minik Faruk, o anda kucucuk akliyla sunun farkina vardi.
Five:  Minik Faruk, o anda küçük akıla vardi.
```

‘şunun farkına’ silinmiş, ‘küçücük’ kısaltılmış, ‘aklıyla’ bozulmuş.

### 6. validation:boun:pop_814:tam

Grup: `five_only_violation`

```text
Girdi: O yuzden para kazanmaya baslayinca pazar yerinden alis veris etmeye son vermek gibi zimni bir hedef vardir pek cogumuzun kafasinda.
Hedef: O yüzden para kazanmaya başlayınca pazar yerinden alış veriş etmeye son vermek gibi zımni bir hedef vardır pek çoğumuzun kafasında.
Zero:  O yuzden para kazanmaya baslayinca pazar yerinden alis veris etmeye son vermek gibi zimni bir hedef vardir pek cogumuzun kafasinda.
Five:  O yüzden para kazanmaya başlayınca pazar yerinden alış verme işlemi son vermek gibi zimni bir hedef vardir pek çoğunuzun kafasında.
```

‘alis veris etmeye’ yeniden yazılmış; ‘çoğumuzun’ → ‘çoğunuzun’ kişi değişikliği.

### 7. validation:boun:ess_1896:tam

Grup: `five_only_violation`

```text
Girdi: Kendimi batil inanclarla alay eden biri olarak nitelendirmeme karsin, ornegin 13.
Hedef: Kendimi batıl inançlarla alay eden biri olarak nitelendirmeme karşın, örneğin 13.
Zero:  Kendimi batil inanclarla alay eden biri olarak nitelendirmeme karsin, ornegin 13.
Five:  Kendimi batılı inanclarla alay eden biri olarak nitelendirmeme karsin, örneğin 13.
```

‘batil’ → ‘batılı’: fazladan harf eklenmiş.

### 8. validation:boun:news_1230:tam

Grup: `five_only_violation`

```text
Girdi: Buna gore maclar ikiser dakikadan uc devre uzerinden yapilacak ve iki seti kazanan guresci musabakadan galip ayrilacak.
Hedef: Buna göre maçlar ikişer dakikadan üç devre üzerinden yapılacak ve iki seti kazanan güreşçi müsabakadan galip ayrılacak.
Zero:  Buna gore maclar ikiser dakikadan uc devre uzerinden yapilacak ve iki seti kazanan guresci musabakadan galip ayrilacak.
Five:  Buna göre maclar ikişer dakikadan üçüncü devre uzerinden yapilacak ve iki seti kazanan Güresci Musabakadan galip ayrilacak.
```

‘uc’ → ‘üçüncü’; özel ad olmayan kelimelerde büyük harf eklenmiş.

### 9. validation:boun:ins_1750:tam

Grup: `five_only_violation`

```text
Girdi: Tepmis oylugun ezmis.
Hedef: Tepmiş oyluğun ezmiş.
Zero:  Tepmis oylugun ezmis.
Five:  Tepme öylüğünün ezilmiş.
```

Kısa cümlede bile kelime ve ekler yeniden yazılmış.

### 10. validation:boun:ins_646:tam

Grup: `five_only_violation`

```text
Girdi: Ebubekir Mehmet Razi, cicek ile kizamik'in ayri ayri hastaliklar oldugunu ve bu hastaliklardan korunma tedbirlerini Dunya'ya tanitan Turk Hekimidir.
Hedef: Ebubekir Mehmet Razi, çiçek ile kızamık'ın ayrı ayrı hastalıklar olduğunu ve bu hastalıklardan korunma tedbirlerini Dünya'ya tanıtan Türk Hekimidir.
Zero:  Ebubekir Mehmet Razi, cicek ile kizamik'in ayri ayri hastaliklar oldugunu ve bu hastaliklardan korunma tedbirlerini Dunya'ya tanitan Turk Hekimidir.
Five:  Ebubekir Mehmet Razi, cicek ile kizamik'in ayri ayri hastalıklar oldugunu ve bu hastalıklardan korunma tedbirlerini Dunya'ya tanitan Türk Hekimdir.
```

‘Hekimidir’ → ‘Hekimdir’: harf silinmiş; çok sayıda düzeltme eksik.

### 11. validation:boun:pop_1021:kismi

Grup: `five_only_violation`

```text
Girdi: Tarihin Doktor Tarafından Ileri Alınması
Hedef: Tarihin Doktor Tarafından İleri Alınması
Zero:  Tarihin Doktor Tarafından Ileri Alınması
Five:  Tarihin doktor tarafından ileri alınması
```

Başlıktaki büyük harfler küçültülmüş; uzunluk eşit olsa da kural ihlali.

### 12. validation:boun:bio_1537:tam

Grup: `five_only_violation`

```text
Girdi: Aday, locada bir kez dolastirildiktan sonra ant kursusunun onune getirilir.
Hedef: Aday, locada bir kez dolaştırıldıktan sonra ant kürsüsünün önüne getirilir.
Zero:  Aday, locada bir kez dolastirildiktan sonra ant kursusunun onune getirilir.
Five:  Aday, locada bir kez dolastırildiktan sonra ant kursusunun önuna getirilir.
```

‘onune’ → ‘önuna’: izin verilmeyen e→a değişimi; eksik düzeltmeler de var.

### 13. validation:boun:pop_1984:tam

Grup: `five_only_violation`

```text
Girdi: Gazeteyi ikiye katladi, aldigi yere koydu, kendi koltuguna gecti, ayak ayakustune atti, kollarini gogsunde caprazladi.
Hedef: Gazeteyi ikiye katladı, aldığı yere koydu, kendi koltuğuna geçti, ayak ayaküstüne attı, kollarını göğsünde çaprazladı.
Zero:  Gazeteyi ikiye katladi, aldigi yere koydu, kendi koltuguna gecti, ayak ayakustune atti, kollarini gogsunde caprazladi.
Five:  Gazeteyi ikiye katladı, aldığını yere koydu, kendi koltuguna gecti, ayak ayakustune attı, kollarını göğsünde çaprazladi.
```

‘aldigi’ → ‘aldığını’: ek harfler üretilmiş.

### 14. validation:boun:pop_1178:tam

Grup: `five_only_violation`

```text
Girdi: Sadece kimi zaman kimi seyleri bos vermeyi ya da biraz ipin ucunu birakmayi deneyin.
Hedef: Sadece kimi zaman kimi şeyleri boş vermeyi ya da biraz ipin ucunu bırakmayı deneyin.
Zero:  Sadece kimi zaman kimi seyleri bos vermeyi ya da biraz ipin ucunu birakmayi deneyin.
Five:  Sadece kimi zaman, kimi seyleri boş vermeyi, biraz ipin ucunu bırakmayı deneyin.
```

Virgüller eklenmiş, ‘ya da’ silinmiş.

### 15. validation:boun:news_1343:tam

Grup: `five_only_violation`

```text
Girdi: Uzmanlar, bilgisayar kullanicilarina Nyxem'in 3 Subat'ta yani bugun aktif hale gececegini duyurdu.
Hedef: Uzmanlar, bilgisayar kullanıcılarına Nyxem'in 3 Şubat'ta yani bugün aktif hale geçeceğini duyurdu.
Zero:  Uzmanlar, bilgisayar kullanıcılarına Nyxem'in 3 Subat'ta yani bugun aktif hale gececegini duyurdu.
Five:  Uzmanlar, bilgisayar kullanıcıları için Nyxem'in 3 Subat'ta yani bugün aktif hale geleceğini duyurdu.
```

‘kullanicilarina’ → ‘kullanıcıları için’; ‘gececegini’ → ‘geleceğini’: yeniden yazım.

### 16. validation:boun:pop_1667:kismi

Grup: `five_only_violation`

```text
Girdi: Ama onlarin cağdası, fakat Ahmed Midhat Efendi ile Muallim Naci'nin izinde, Edebiyat-ı Cedide yazarlarina karsi cıkmış, devrin çok verimli bir yazarı vardi ki Saltanat ve Cumhuriyet yillarında, Kadiköy'de oturacak ve bu semtin guzelliklerine bağli kalacakti.
Hedef: Ama onların çağdaşı, fakat Ahmed Midhat Efendi ile Muallim Naci'nin izinde, Edebiyat-ı Cedide yazarlarına karşı çıkmış, devrin çok verimli bir yazarı vardı ki Saltanat ve Cumhuriyet yıllarında, Kadıköy'de oturacak ve bu semtin güzelliklerine bağlı kalacaktı.
Zero:  Ama onların cağdası, fakat Ahmed Midhat Efendi ile Muallim Naci'nin izinde, Edebiyat-ı Cedide yazarlarina karşı çıkmış, devrin çok verimli bir yazarı vardi ki Saltanat ve Cumhuriyet yillarında, Kadiköy'de oturacak ve bu semtin güzelliklerine bağlı kalacakti.
Five:  Ama onların çagdası, fakat Ahmed Midhat Efendi ile Muallim Naci'nin izinde, Edebiyat-ı Cedide yazarlarina karşı çıkmış, devrin çok verimli bir yazarı vardi ki Saltanat ve Cumhuriyet yillarında, Kadiköy'de oturacak ve bu semtin güzelliklerine bağli kalacakti.
```

‘cağdası’ → ‘çagdası’: mevcut ğ bozulmuş; uzunluk eşit olması uyum anlamına gelmez.

### 17. validation:boun:pop_1478:tam

Grup: `five_only_violation`

```text
Girdi: Hele de karsinizda bir arkadasiniz ya da sevdiginiz bir insan, hepsinden beteri sevgiliniz varsa bu durum iyice karin agritici bir hale gelir.
Hedef: Hele de karşınızda bir arkadaşınız ya da sevdiğiniz bir insan, hepsinden beteri sevgiliniz varsa bu durum iyice karın ağrıtıcı bir hale gelir.
Zero:  Hele de karsinizda bir arkadasiniz ya da sevdiginiz bir insan, hepsinden beteri sevgiliniz varsa bu durum iyice karin agritici bir hale gelir.
Five:  Hele de karanıza bir arkadaşıınız ya da sevdiginiz bir insan, hepsinden beteri sevgiliniz varsa bu durum iyice karın agırıcı bir hale gelir.
```

Birden çok kelimede harf ekleme/silme ve sıralama bozukluğu.

### 18. validation:boun:ess_1373:tam

Grup: `five_only_violation`

```text
Girdi: Baglar, agac kumeleri gecerler ara ara.
Hedef: Bağlar, ağaç kümeleri geçerler ara ara.
Zero:  Baglar, ağaç kumeleri gecerler ara ara.
Five:  Baglar, ağaç kumeleri gece rârâr.
```

‘gecerler ara ara’ bozulmuş; izin verilmeyen â üretilmiş.

### 19. validation:boun:ess_1758:kismi

Grup: `five_only_violation`

```text
Girdi: Psikiyatri hekimliğin en eski, buna karsın gelişmesi yeni dallarından biridir.
Hedef: Psikiyatri hekimliğin en eski, buna karşın gelişmesi yeni dallarından biridir.
Zero:  Psikiyatri hekimliğin en eski, buna karsın gelişmesi yeni dallarından biridir.
Five:  Psikiyatri hekimliğin en eski, bu nedenle gelişmesi yeni dallarından biridir.
```

‘buna karsın’ → ‘bu nedenle’: anlamı da değiştiren yeniden yazım.

### 20. validation:boun:pop_1597:kismi

Grup: `five_only_violation`

```text
Girdi: - Bu yıl Eurovision 'a kaç sarkı ile katılacaksıniz?
Hedef: - Bu yıl Eurovision 'a kaç şarkı ile katılacaksınız?
Zero:  - Bu yıl Eurovision 'a kaç sarkı ile katılacaksıniz?
Five:  - Bu yıl Eurovision'a kaç sarkı ile katılacaksınız?
```

Eurovision ile apostrof arasındaki özgün boşluk silinmiş.

### 21. validation:boun:bio_1335:tam

Grup: `five_only_violation`

```text
Girdi: Evimize gidip gelmeye basladi.
Hedef: Evimize gidip gelmeye başladı.
Zero:  Evimize gidip gelmeye başladi.
Five:  Evimize gidebilme basladi.
```

‘gidip gelmeye’ → ‘gidebilme’: kelime yapısı ve anlam değişmiş.

### 22. validation:boun:ins_1134:tam

Grup: `five_only_violation`

```text
Girdi: Teknenin bu gibi agir kosullari zarar gormeden atlatmasini saglamanin basta gelen sarti, guclu demir takimlari ile bunlarin volta edilecegi ici dolu, yekpare metalden yapilma cok saglam, kocboynuzlari ve babalara sahip olmak.
Hedef: Teknenin bu gibi ağır koşulları zarar görmeden atlatmasını sağlamanın başta gelen şartı, güçlü demir takımları ile bunların volta edileceği içi dolu, yekpare metalden yapılma çok sağlam, koçboynuzları ve babalara sahip olmak.
Zero:  Teknenin bu gibi agir kosullari zarar gormeden atlatmasini saglamanin basta gelen sarti, guclu demir takimlari ile bunlarin volta edilecegi ici dolu, yekpare metalden yapilma cok saglam, kocboynuzlari ve babalara sahip olmak.
Five:  Teknenin bu gibi ağır koşullarından atlatmasının başta gelen şartı, güçlü demir takımlarının bu yüzden volat edileceğinden kaynaklanıyor, yekpare metali yapılı olması çok sağlam, kocboynuzlari ve babalara sahip olmak.
```

Uzun cümlede birden çok parça yeniden yazılmış ve silinmiş.

### 23. validation:boun:ins_115:tam

Grup: `five_only_violation`

```text
Girdi: Biz guzel Ayvalik'in mutlu kapisini soyle bir aralayalim dedik.
Hedef: Biz güzel Ayvalık'ın mutlu kapısını şöyle bir aralayalım dedik.
Zero:  Biz güzel Ayvalik'in mutlu kapısını soyle bir aralayalim dedik.
Five:  Biz güzel Ayvalik'tin mutlu kapısını söyle bir aralayalim dedik.
```

‘Ayvalik’in’ → ‘Ayvalik’tin’: fazladan t eklenmiş.

### 24. validation:boun:bio_1838:tam

Grup: `five_only_violation`

```text
Girdi: Disi arslan bu mini miniyi kendi yavrulari yaninda gorunce onu da dogurdugunu sandi.
Hedef: Dişi arslan bu mini miniyi kendi yavruları yanında görünce onu da doğurduğunu sandı.
Zero:  Disi arslan bu mini miniyi kendi yavrulari yaninda gorunce onu da dogurdugunu sandi.
Five:  Disi arslan bu mini miniyi kendi yavruları yanında görence onu da doğurdugunu sandı.
```

‘gorunce’ → ‘görence’: u→e izinsiz değişimi.

### 25. validation:boun:pop_1886:tam

Grup: `five_only_violation`

```text
Girdi: Freddie Mercury, olumunden birkac yil sonra grubu Queen ile yeniden biraraya geldi.
Hedef: Freddie Mercury, ölümünden birkaç yıl sonra grubu Queen ile yeniden biraraya geldi.
Zero:  Freddie Mercury, olumunden birkac yil sonra grubu Queen ile yeniden biraraya geldi.
Five:  Freddie Mercury, ölmüşten birkaç yıl sonra grubu Queen ile yeniden biraraya geldi.
```

‘olumunden’ → ‘ölmüşten’: sözcük yapısı değiştirilmiş.

### 26. validation:boun:news_1625:tam

Grup: `both_violate`

```text
Girdi: Nitekim Marco daha en basta, sahnedeki performansin etkileyiciligi, dans eden kadinlarin yalnizligi ve caresizligi karsisinda gozyaslarini tutamaz.
Hedef: Nitekim Marco daha en başta, sahnedeki performansın etkileyiciliği, dans eden kadınların yalnızlığı ve çaresizliği karşısında gözyaşlarını tutamaz.
Zero:  Nitekim Marco daha en basta, sahnedeki performansın etkileyiciliği, dans eden kadinların yalnizliği ve çaresizliği karşısında gözyaşları tutamaz.
Five:  Nitekim Marco daha en başta, sahnedeki performansın etkileyiciliği, dans eden kadinların yalnızlığı ve çaresizliği karşısında göz yasları tutamaz.
```

Her iki koşulda gözyaşlarını sözcüğü bozulmuş; five-shot ayrıca sözcüğü bölmüş.

### 27. validation:boun:ess_1625:kismi

Grup: `both_violate`

```text
Girdi: Diğer kıtalara nazaran Madagaskarda cumhuriyet yonetim şekli olarak benimsenmistir.
Hedef: Diğer kıtalara nazaran Madagaskarda cumhuriyet yönetim şekli olarak benimsenmiştir.
Zero:  Diğer kıtalara nazaran Madagaskarda cumhuriyet yürürlüğe girmiştir.
Five:  Diğer kıtalara nazaran Madagaskarda cumhuriyet yürütmek şekli olarak benimsenmistir.
```

Her iki koşul yönetim sözcüğünü başka bir ifadeye dönüştürmüş.

### 28. validation:boun:ess_1436:tam

Grup: `both_violate`

```text
Girdi: Aradigin sorunun bendeki cevabi, boyutlardir.
Hedef: Aradığın sorunun bendeki cevabı, boyutlardır.
Zero:  Aradığın sorunun benim cevabım, boyutlardır.
Five:  Aradığın sorunun benim cevabım, boyutlardır.
```

Her iki koşul ‘bendeki cevabi’ ifadesini ‘benim cevabım’ olarak yeniden yazmış.

### 29. validation:boun:bio_1043:koruma

Grup: `both_violate`

```text
Girdi: Cemal Hoca hepimizi Teknik Üniversite'ye gidecekmişiz gibi çalıştırırdı.
Hedef: Cemal Hoca hepimizi Teknik Üniversite'ye gidecekmişiz gibi çalıştırırdı.
Zero:  Cemal Hoca hepimizi Teknik Üniversitesi'ne gidecekmişiz gibi çalıştırırdı.
Five:  Cemal Hoca hepimizi Teknik Üniversitesiye gidecekmişiz gibi çalıştırırdı.
```

Koruma örneğinde her iki koşul Üniversite’ye ifadesini değiştirmiş.

### 30. validation:boun:pop_1097:koruma

Grup: `both_violate`

```text
Girdi: CEVAP 2: Her ikisi de doğal gereksinim olmakla birlikte, insanlar cinsel yaşam olmadan yaşayabilir ancak uykusuzluğa dayanamazlar.
Hedef: CEVAP 2: Her ikisi de doğal gereksinim olmakla birlikte, insanlar cinsel yaşam olmadan yaşayabilir ancak uykusuzluğa dayanamazlar.
Zero:  Her ikisi de doğal gereksinim olmakla birlikte, insanlar cinsel yaşam olmadan yaşayabilir ancak uykusuzluğa dayanamazlar.
Five:  Her ikisi de doğal gereksinim olmakla birlikte, insanlar cinsel yaşam olmadan yaşayabilir ancak uykusuzluğa dayanamazlar.
```

Koruma örneğinde her iki koşul ‘CEVAP 2:’ önekini silmiş.

### 31. validation:boun:pop_153:tam

Grup: `zero_only_violation`

```text
Girdi: 1 adet buyuk domates
Hedef: 1 adet büyük domates
Zero:  1 adet Büyük Domates
Five:  1 adet büyük domates
```

Zero-shot büyük harf ihlali yapıyor; five-shot tam doğru.

### 32. validation:boun:bio_714:tam

Grup: `zero_only_violation`

```text
Girdi: Bunlar genel sorulardi.
Hedef: Bunlar genel sorulardı.
Zero:  Bunlar genel sorulardır.
Five:  Bunlar genel sorulardı.
```

Zero-shot zaman/ek değiştiriyor; five-shot tam doğru.

### 33. validation:boun:pop_1146:tam

Grup: `zero_only_violation`

```text
Girdi: 3 adet yesil biber (ince dogranmis)
Hedef: 3 adet yeşil biber (ince doğranmış)
Zero:  3 adet yeşil biber (ince doğranaş)
Five:  3 adet yeşil biber (ince doğranmış)
```

Zero-shot doğranmış sözcüğünü bozuyor; five-shot tam doğru.

### 34. validation:boun:bio_1437:tam

Grup: `zero_only_violation`

```text
Girdi: (Bunlardan birkacina ilerde rastlayacagim.
Hedef: (Bunlardan birkaçına ilerde rastlayacağım.
Zero:  Bunlardan birkacina ilerde rastlayacagim.
Five:  (Bunlardan birkaçına ilerde rastlayacagim.
```

Five-shot açılış parantezini koruyor; ancak eksik düzeltme devam ediyor.

### 35. validation:boun:news_1501:tam

Grup: `zero_only_violation`

```text
Girdi: Daha once Ferrari'yle test surusleri yapan, hatta F1'e gecmesi bile gundeme gelen Rossi, bu defa Dunya Ralli Sampiyonasi'nin Yeni Zelanda ayaginda ortaya cikti.
Hedef: Daha önce Ferrari'yle test sürüşleri yapan, hatta F1'e geçmesi bile gündeme gelen Rossi, bu defa Dünya Ralli Şampiyonası'nın Yeni Zelanda ayağında ortaya çıktı.
Zero:  Daha önce Ferrari'yle test surusleri yapan, hatta F1'e gecmesi bile gundeme gelen Rossi, bu defa Dünya Rally Sampiyonası'nın Yeni Zelanda ayagında ortaya çıktı.
Five:  Daha önce Ferrari'yle test surusleri yapan, hatta F1'e gecmesi bile gundeme gelen Rossi, bu defa Dunya Ralli Sampiyonası'nın Yeni Zelanda ayagında ortaya çıktı.
```

Zero-shot Ralli sözcüğünü Rally yapıyor; five-shot bu ihlali kaldırıyor ama düzeltmeler eksik.

### 36. validation:boun:pop_1893:tam

Grup: `compliant_errors`

```text
Girdi: 1 adet havuc (ince rendelenmis)
Hedef: 1 adet havuç (ince rendelenmiş)
Zero:  1 adet havuc (ince rendelenmis)
Five:  1 adet havuc (ince rendelenmiş)
```

Five-shot rendelenmiş düzeltmesini yapmış, havuç düzeltmesi eksik; ikisi de kurala uyuyor.

### 37. validation:boun:pop_1937:tam

Grup: `compliant_errors`

```text
Girdi: 1 kutu misir
Hedef: 1 kutu mısır
Zero:  1 kutu misir
Five:  1 kutu misir
```

Her iki koşul girdiyi aynen kopyalamış; mısır için iki düzeltme eksik.

### 38. validation:boun:ess_1741:tam

Grup: `compliant_errors`

```text
Girdi: Bi kerze yonetmeninin hakkini teslim edelim.
Hedef: Bi kerze yönetmeninin hakkını teslim edelim.
Zero:  Bi kerze yonetmeninin hakkını teslim edelim.
Five:  Bi kerze yonetmeninin hakkını teslim edelim.
```

Her iki koşul hakkını düzeltmiş, yönetmeninin eksik; özgün yazım hatası korunmuş.

### 39. validation:boun:ins_220:tam

Grup: `compliant_errors`

```text
Girdi: AGAC DIYOR KI
Hedef: AĞAÇ DİYOR Kİ
Zero:  AGAC DİYOR KI
Five:  AGAC DIYOR KI
```

Büyük harfli örnekte five-shot tüm düzeltmeleri kaçırmış; zero-shot yalnızca bir İ düzeltmiş.

### 40. validation:boun:pop_1796:tam

Grup: `compliant_errors`

```text
Girdi: "Musait yerde"nin bu ilk haliydi, bunun bir de ikinci hali vardir.
Hedef: "Müsait yerde"nin bu ilk haliydi, bunun bir de ikinci hali vardır.
Zero:  "Musait yerde"nin bu ilk haliydi, bunun bir de ikinci hali vardir.
Five:  "Musait yerde"nin bu ilk haliydi, bunun bir de ikinci hali vardir.
```

Her iki koşul girdiyi aynen bırakmış; Müsait ve vardır düzeltmeleri eksik.

Örneklerin kaynağı UD Turkish BOUN r2.16; CC BY-SA 4.0. Kaynak/lisans: data/prepared/boun-v1/source/.
