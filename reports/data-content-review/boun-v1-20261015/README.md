# BOUN v1 — eğitim verisi içerik kontrolü

Tarih: 15 Ekim 2026. İnceleyen: Codex; bu çalışma bağımsız insan onayı değildir.

## Sonuç

75 eğitim örneğinin tamamı girdi ve hedef birlikte okunarak incelendi. Dönüşüm kaynaklı hata veya kesin yanlış Türkçe harf hedefi saptanmadı. Tüm 7.340 eğitim kaydında otomatik dönüşüm ve biçim kontrolleri geçti. Küçük eğitim denemesine geçişi engelleyen bir dönüşüm sorunu bulunmadı; iki kaynak ifadesi yeniden inceleme için işaretlendi. Bu, bütün hedeflerin dilsel açıdan hatasız olduğunun kanıtı değildir.

Veri dosyaları değiştirilmedi. Kaynağın yazım, noktalama ve anlatım özelliklerini düzeltmek bu görevin kapsamı dışındadır. İşaretli kayıtlar otomatik olarak elenmedi.

## Örnekleme

Yalnızca `data/prepared/boun-v1/splits/train.jsonl` kullanıldı. 25 tam, 25 kısmi ve 25 koruma örneği seçildi. Koruma içinde 12 Türkçe karakter gerektirmeyen ve 13 Türkçe karakterli örnek var. Bu dağılım türleri incelemek içindir; eğitimdeki %60/%25/%15 oranını temsil etmez ve hata oranı tahmini olarak kullanılmamalıdır.

Tekrarlanabilir seçim: her havuz `SHA256("content-review-20261015:" + id)` değerine göre artan sırada sıralanıp belirtilen ilk N kayıt alındı. Rapor sırası tam, kısmi, Türkçe karakter gerektirmeyen koruma, Türkçe karakterli koruma şeklindedir. Seçimden sonra yeniden örnekleme yapılmadı.

Eğitim dosyası SHA-256: `48cd9494bd76b6a6fbaabdeac88ace006094662115e53cc9f48e8debc7da3b56`.

## Otomatik kontroller

Her kontrol 7.340/7.340 kayıtta geçti: izinli konumsal dönüşüm, hedeften türetilebilirlik, tam/kısmi/koruma tür koşulları, eşit karakter uzunluğu, boşlukların konum ve değerleri, Unicode noktalama karakterlerinin konum ve değerleri, mevcut Türkçe karakterlerin korunması ve NFC normalizasyonu. Ayrıntılar [checks.json](checks.json) içinde.

`python3 -m scripts.audit_data data/prepared/boun-v1` ayrıca başarıyla tamamlandı: 9.140 benzersiz kaynak, 0 yakın tekrar çifti ve 0 korunan pilot örtüşmesi. Bu komut tüm bölümlerin yapısal ayrılığını ve dosya özetlerini denetler; doğrulama/test örnekleri dilsel inceleme veya ayar seçimi için okunmadı. Sıfır örtüşme yalnızca uygulanan benzerlik kuralları kapsamındadır.

## Dikkat gerektiren bulgular

- `news_1413`: “büyük çaba almıyor” alışılmadık bir kullanım. Dönüşüm hatası yok; kaynak anlatımı açısından yeniden incelenmeli.
- `bio_1110`: “Büyük Kardan Hazinenin Batısı” bağlamsız olarak anlamı açık olmayan bir ifade. Özel ad/çeviri bağlamı olabilir; kesin yanlış hedef diye etiketlenmedi.
- `bio_1427`: “Hastanenin bahçesindeyiz .” hedefinde noktadan önce boşluk var. Aynı boşluk girdide de var; görev açısından doğru biçim koruma örneği.

Bu üç hedefin özgün CoNLL-U `# text` alanları yerel kaynak dosyalarında doğrulandı; görülen özellikler hazırlama sırasında oluşmamış.

Yarım ifadeler, başlıklar, malzeme listeleri, kapanmamış tırnaklar ve aynı kayıtta birden fazla cümle bulunuyor. Bunlar tek başına eleme nedeni değildir. Uzun örnekler için eğitimden önce tokenizer ile token uzunluğu kontrolü yapılmalı. â gibi görev eşlemesinde olmayan harfler “tam ASCII” girdilerinde kalabilir; bu, mevcut tanıma göre beklenen davranıştır.

İki şüpheli ifadenin kaynak bağlamıyla veya insan incelemesiyle kontrol edilmesi önerilir. Bir eleme kararı alınırsa dondurulmuş boun-v1 elle değiştirilmemeli; gerekçe kaydedilerek yeni sürüm üretilmelidir. Bu inceleme genel kültür/bilim/tarih iddialarının veya özel adların dış kaynakla doğrulanmasını kapsamaz.

## Kayıt bazında inceleme

İnceleme etiketleri: 52 uygun, 21 biçim/bağlam notlu, 2 yeniden inceleme. Biçim/bağlam notu hata etiketi değildir.

### 01. train:boun:pop_1129:tam

Tür: `tam` — `uygun`

```text
Girdi: - Agrilari kesiyor.
Hedef: - Ağrıları kesiyor.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 02. train:boun:ins_1156:tam

Tür: `tam` — `bicim_veya_baglam`

```text
Girdi: Cok buyuk su insan akli
Hedef: Çok büyük şu insan aklı
```

Devrik, doğal ifade; son noktalama kaynakta yok, eklenmemeli.

### 03. train:boun:news_725:tam

Tür: `tam` — `bicim_veya_baglam`

```text
Girdi: "Ha Almanyali ha Kibrisli Turkler"
Hedef: "Ha Almanyalı ha Kıbrıslı Türkler"
```

Başlık/alıntı niteliğinde; tam cümle olmaması dönüşüm hatası değil.

### 04. train:boun:ins_121:tam

Tür: `tam` — `bicim_veya_baglam`

```text
Girdi: Cok para yer ama
Hedef: Çok para yer ama
```

Konuşma dilinde yarım ifade; devamı olmadan bağlam sınırlı.

### 05. train:boun:news_178:tam

Tür: `tam` — `uygun`

```text
Girdi: Psikolojik, psikiyatrik, organik, ilac kullanimi gibi nedenlerle ortaya cikar.
Hedef: Psikolojik, psikiyatrik, organik, ilaç kullanımı gibi nedenlerle ortaya çıkar.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 06. train:boun:ins_1882:tam

Tür: `tam` — `uygun`

```text
Girdi: Mustafa, bunlarin oyunlarina hicbir gun karismaz, elleri cebinde, basi yukarida, buyuk bir adam gibi onlari seyrederdi.
Hedef: Mustafa, bunların oyunlarına hiçbir gün karışmaz, elleri cebinde, başı yukarıda, büyük bir adam gibi onları seyrederdi.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 07. train:boun:news_901:tam

Tür: `tam` — `uygun`

```text
Girdi: Iran medyasinda cikan bir habere gore, Tahran yonetimi son donemde artan dis tehditler karsisinda Sahap 3 fuzelerini Israil'deki onemli ve stratejik hedeflere yonlendirdi.
Hedef: İran medyasında çıkan bir habere göre, Tahran yönetimi son dönemde artan dış tehditler karşısında Şahap 3 füzelerini İsrail'deki önemli ve stratejik hedeflere yönlendirdi.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 08. train:boun:news_1413:tam

Tür: `tam` — `yeniden_incele`

```text
Girdi: "Putin Rusyasi"nin dikensiz gul bahcesine donusmesi; hal boyleyken buyuk caba almiyor...
Hedef: "Putin Rusyası"nın dikensiz gül bahçesine dönüşmesi; hal böyleyken büyük çaba almıyor...
```

“Büyük çaba almıyor” ifadesi alışılmadık; kaynakta da aynı. Üslup veya kaynak anlatım sorunu olabilir; kesin etiket hatası değil, otomatik düzeltilmemeli.

### 09. train:boun:pop_999:tam

Tür: `tam` — `uygun`

```text
Girdi: Hint nehirlerinin efsanevi ozellikleri vardi.
Hedef: Hint nehirlerinin efsanevi özellikleri vardı.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 10. train:boun:news_1825:tam

Tür: `tam` — `uygun`

```text
Girdi: Agar, gecmiste yaptiklari bazi arastirmalarda, silahli sag ve sol orgutlerle iliskileri bulunan kesimlerin, genellikle Bati Avrupa ulkelerinin gizli servisleri oldugunu tespit ettiklerini belirterek, bunlarin, Turkiye'yi istikrarsizlastirmayi amacladigini da sozlerine ekledi.
Hedef: Ağar, geçmişte yaptıkları bazı araştırmalarda, silahlı sağ ve sol örgütlerle ilişkileri bulunan kesimlerin, genellikle Batı Avrupa ülkelerinin gizli servisleri olduğunu tespit ettiklerini belirterek, bunların, Türkiye'yi istikrarsızlaştırmayı amaçladığını da sözlerine ekledi.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 11. train:boun:ins_2000:tam

Tür: `tam` — `bicim_veya_baglam`

```text
Girdi: Karsisinda Alibey adaciklari...
Hedef: Karşısında Alibey adacıkları...
```

Eksiltili betimleme; üç nokta korunuyor.

### 12. train:boun:bio_1646:tam

Tür: `tam` — `uygun`

```text
Girdi: Tezini verdikten sonra Ataturk sordu, Aydin yanitladi.
Hedef: Tezini verdikten sonra Atatürk sordu, Aydın yanıtladı.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 13. train:boun:news_1540:tam

Tür: `tam` — `uygun`

```text
Girdi: Bir parti iktidara gelince taraftar ve oy verenlerinin, biraz da yillarca dislanmanin verdigi hislerle bazi beklentiler icine girmeleri, is imkanlari aramalari olagandir.
Hedef: Bir parti iktidara gelince taraftar ve oy verenlerinin, biraz da yıllarca dışlanmanın verdiği hislerle bazı beklentiler içine girmeleri, iş imkanları aramaları olağandır.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 14. train:boun:ins_1261:tam

Tür: `tam` — `uygun`

```text
Girdi: Madeni halatlar caplari, bitkisel, sentetik halatlar ise cevreleri ile olculurler.
Hedef: Madeni halatlar çapları, bitkisel, sentetik halatlar ise çevreleri ile ölçülürler.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 15. train:boun:ess_1673:tam

Tür: `tam` — `uygun`

```text
Girdi: Soz, bizler yok oldugumuzda bile tamamen ucup gitmez, otekilere aktarilir.
Hedef: Söz, bizler yok olduğumuzda bile tamamen uçup gitmez, ötekilere aktarılır.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 16. train:boun:ins_1406:tam

Tür: `tam` — `uygun`

```text
Girdi: Koskoca arabayi nasil cekerler, dort ayak uzerinde duracak hâlleri yok.
Hedef: Koskoca arabayı nasıl çekerler, dört ayak üzerinde duracak hâlleri yok.
```

Doğal hedef. â görev eşlemesi dışında; tam bozma girdisinde hâlleri biçiminin kalması doğru.

### 17. train:boun:pop_1326:tam

Tür: `tam` — `uygun`

```text
Girdi: O insan yasamamaktadir; ancak yasadigini zannetmektedir.
Hedef: O insan yaşamamaktadır; ancak yaşadığını zannetmektedir.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 18. train:boun:pop_1040:tam

Tür: `tam` — `uygun`

```text
Girdi: Elmalari yikayin ve butun olarak kabuklarini soyun.
Hedef: Elmaları yıkayın ve bütün olarak kabuklarını soyun.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 19. train:boun:ins_111:tam

Tür: `tam` — `uygun`

```text
Girdi: Yillardan bir yil, bu koye bir kiran girer, suru koymaz, kirar gecirir.
Hedef: Yıllardan bir yıl, bu köye bir kıran girer, sürü koymaz, kırar geçirir.
```

“Kıran” ve “sürü koymaz” edebî/eski kullanım olarak değerlendirildi; alışılmadık sözcükler otomatik düzeltilmemeli.

### 20. train:boun:ins_956:tam

Tür: `tam` — `uygun`

```text
Girdi: - Cabuk olun, demis.
Hedef: - Çabuk olun, demiş.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 21. train:boun:ess_451:tam

Tür: `tam` — `uygun`

```text
Girdi: Ve fakat bu yeni gercek, Kadikoy vapurunun karsidan karsiya gecis suresini hicbir sekilde degistirmedi.
Hedef: Ve fakat bu yeni gerçek, Kadıköy vapurunun karşıdan karşıya geçiş süresini hiçbir şekilde değiştirmedi.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 22. train:boun:bio_326:tam

Tür: `tam` — `bicim_veya_baglam`

```text
Girdi: "Ah Meral, ben senin gelin arabani kullanacaktim.
Hedef: "Ah Meral, ben senin gelin arabanı kullanacaktım.
```

Açılan çift tırnak kapanmıyor; kaynak parçalanmasına bağlı olabilir, hedefe tırnak eklenmemeli.

### 23. train:boun:bio_1427:tam

Tür: `tam` — `bicim_veya_baglam`

```text
Girdi: Hastanenin bahcesindeyiz .
Hedef: Hastanenin bahçesindeyiz .
```

Noktadan önceki boşluk kaynakta da var; girdi ve hedefte aynı konumda korunuyor.

### 24. train:boun:pop_662:tam

Tür: `tam` — `uygun`

```text
Girdi: Ne hindiler kesildi, ne hediyeler alindi.
Hedef: Ne hindiler kesildi, ne hediyeler alındı.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 25. train:boun:ess_1950:tam

Tür: `tam` — `uygun`

```text
Girdi: Zaman zaman kavgaya donusen tartisma, pasaportum uzerineydi.
Hedef: Zaman zaman kavgaya dönüşen tartışma, pasaportum üzerineydi.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 26. train:boun:bio_1338:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Kizilirmak kenarinda yetişmiş bu pembe kir çicegine, başkentin butün uçuk renkleri, baygin kokuları bir incelik veriyordu.
Hedef: Kızılırmak kenarında yetişmiş bu pembe kır çiçeğine, başkentin bütün uçuk renkleri, baygın kokuları bir incelik veriyordu.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 27. train:boun:pop_905:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Doğrusunu yalniz Allah bilir.
Hedef: Doğrusunu yalnız Allah bilir.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 28. train:boun:ins_721:kismi

Tür: `kismi` — `bicim_veya_baglam`

```text
Girdi: MESE İLE SAZ
Hedef: MEŞE İLE SAZ
```

Büyük harfli başlık; Ş geri yüklenirken mevcut İ korunuyor.

### 29. train:boun:bio_81:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Benim de canim cıkmadan bu huyum cıkmayacaktı demek.
Hedef: Benim de canım çıkmadan bu huyum çıkmayacaktı demek.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 30. train:boun:news_981:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Hayat ile baş edememis bir müzisyenin son cigligi bu albüm.
Hedef: Hayat ile baş edememiş bir müzisyenin son çığlığı bu albüm.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 31. train:boun:ess_301:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Doğan Nadi bunun uzerine Atina'ya gidip, oradan yazilar yazmaya karar verdi.
Hedef: Doğan Nadi bunun üzerine Atina'ya gidip, oradan yazılar yazmaya karar verdi.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 32. train:boun:news_596:kismi

Tür: `kismi` — `uygun`

```text
Girdi: "Bu Sevgililer Gunü'nde de ayıcık almak istemiyorum" diyenlerin yardimına ise giyim magazalari koşuyor.
Hedef: "Bu Sevgililer Günü'nde de ayıcık almak istemiyorum" diyenlerin yardımına ise giyim mağazaları koşuyor.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 33. train:boun:ess_482:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Sefil, zavalli bir acgozlülük; aşağilık bir egoizm ve hırs adina, kökleri 3650 yıl önceye dayanan bu "yanliş uygarlik" inatla ve ısrarla korunmaya çalisilıyor.
Hedef: Sefil, zavallı bir açgözlülük; aşağılık bir egoizm ve hırs adına, kökleri 3650 yıl önceye dayanan bu "yanlış uygarlık" inatla ve ısrarla korunmaya çalışılıyor.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 34. train:boun:ins_458:kismi

Tür: `kismi` — `bicim_veya_baglam`

```text
Girdi: "Kosma yavrum, terleyeceksin! Terliyken su içme!" Ah şu büyükleriniz! Bir türlü vazgeçmezler sizleri uyarmaktan...
Hedef: "Koşma yavrum, terleyeceksin! Terliyken su içme!" Ah şu büyükleriniz! Bir türlü vazgeçmezler sizleri uyarmaktan...
```

Bir kayıtta birden fazla cümle var; alıntı ve ünlem düzeni korunuyor.

### 35. train:boun:ess_1340:kismi

Tür: `kismi` — `uygun`

```text
Girdi: - Bakalım, biz de bir yazlıga girdik.
Hedef: - Bakalım, biz de bir yazlığa girdik.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 36. train:boun:pop_877:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Bunun sebebi acık.
Hedef: Bunun sebebi açık.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 37. train:boun:ess_1944:kismi

Tür: `kismi` — `bicim_veya_baglam`

```text
Girdi: Koyu yeşilligiyle, ağırbasli Heybeli.
Hedef: Koyu yeşilliğiyle, ağırbaşlı Heybeli.
```

Eksiltili edebî betimleme; bağımsız bağlam sınırlı.

### 38. train:boun:ess_139:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Eğer böyle olursa, bilimin kapisina kilit vurulur.
Hedef: Eğer böyle olursa, bilimin kapısına kilit vurulur.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 39. train:boun:news_534:kismi

Tür: `kismi` — `bicim_veya_baglam`

```text
Girdi: * Ombudsman Denetimine Ilişkin Araştirma Raporu,
Hedef: * Ombudsman Denetimine İlişkin Araştırma Raporu,
```

Liste/başlık parçası; baştaki yıldız ve sondaki virgül korunuyor.

### 40. train:boun:bio_260:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Yeğen kursunlari boşalttı, at bu kez öldu.
Hedef: Yeğen kurşunları boşalttı, at bu kez öldü.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 41. train:boun:bio_1616:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Birahanede kavga oldu ve alti kişi yaralandı...
Hedef: Birahanede kavga oldu ve altı kişi yaralandı...
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 42. train:boun:pop_1511:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Serdar Ortaç'ın "Okyanus" albumu geçtigimiz yıl piyasaya çikmişti.
Hedef: Serdar Ortaç'ın "Okyanus" albümü geçtiğimiz yıl piyasaya çıkmıştı.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 43. train:boun:bio_29:kismi

Tür: `kismi` — `bicim_veya_baglam`

```text
Girdi: Bir taraftan da para biriktireceğiz, yeterince para biriktirinceye, yani işin finans yonünden aksamaması teminat altına alınincaya kadar da kampusun insaatina girmeyecegiz."
Hedef: Bir taraftan da para biriktireceğiz, yeterince para biriktirinceye, yani işin finans yönünden aksamaması teminat altına alınıncaya kadar da kampusun inşaatına girmeyeceğiz."
```

Başta açılmayan kapanış tırnağı var; kaynak alıntısının parçası olabilir, korunmalı.

### 44. train:boun:bio_1892:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Parmak ucu duyarliligına tam güvendigim bir zamanda, muziğin bütün ayrıntılarıyla gozümun onune serildiği, onu icimde hissettigim bir zamanda, tam konsantre olabildiğim bir zamanda çalmalıyim Bach'ı...
Hedef: Parmak ucu duyarlılığına tam güvendiğim bir zamanda, müziğin bütün ayrıntılarıyla gözümün önüne serildiği, onu içimde hissettiğim bir zamanda, tam konsantre olabildiğim bir zamanda çalmalıyım Bach'ı...
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 45. train:boun:bio_1723:kismi

Tür: `kismi` — `bicim_veya_baglam`

```text
Girdi: Iki ucunda, pratik bir şekilde toparlanıp kaçabilmek icin kalin sicimler gecirilmis brandalar ...
Hedef: İki ucunda, pratik bir şekilde toparlanıp kaçabilmek için kalın sicimler geçirilmiş brandalar ...
```

Eksiltili betimleme ve üç noktadan önce boşluk var; aynen korunuyor.

### 46. train:boun:pop_1839:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Kadıkoy'deki rovans maçinda, binlerce Rum seyirci tribünleri doldurmuştu.
Hedef: Kadıköy'deki rövanş maçında, binlerce Rum seyirci tribünleri doldurmuştu.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 47. train:boun:news_391:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Mehmet Basaran, Refik Durbaş, Haydar Ergulen, Sait Maden ve Faruk Suyun'den olusan seçici kurul, yil icinde her ay finale kalıp Dunya Kitap'ta yapitları yayımlanan 18 sairin gönderdikleri çalişmaları değerlendirdi.
Hedef: Mehmet Başaran, Refik Durbaş, Haydar Ergülen, Sait Maden ve Faruk Şüyün'den oluşan seçici kurul, yıl içinde her ay finale kalıp Dünya Kitap'ta yapıtları yayımlanan 18 şairin gönderdikleri çalışmaları değerlendirdi.
```

Çok sayıda özel ad içeriyor; kaynakla uyumlu dönüşüm var. Özel adların gerçek dünyadaki yazımları dış kaynakla doğrulanmadı.

### 48. train:boun:ess_811:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Tatli, hossohbet, konuşkan bir kisiydi.
Hedef: Tatlı, hoşsohbet, konuşkan bir kişiydi.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 49. train:boun:ins_643:kismi

Tür: `kismi` — `uygun`

```text
Girdi: Kasabaya yaklaşirken ugursuz, silâhli uc adam yolunu kesmis.
Hedef: Kasabaya yaklaşırken uğursuz, silâhlı üç adam yolunu kesmiş.
```

Doğal hedef; silâhlı sözcüğündeki â görev kapsamı dışında ve aynen korunuyor.

### 50. train:boun:ins_1965:kismi

Tür: `kismi` — `bicim_veya_baglam`

```text
Girdi: Cami, ceşme, kutüphane, hastane, kervansaray, külliye...
Hedef: Cami, çeşme, kütüphane, hastane, kervansaray, külliye...
```

İsim listesi; yüklemsiz olması görev için hata değil.

### 51. train:boun:bio_1483:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `uygun`

```text
Girdi: Evimde olmak istiyorum.
Hedef: Evimde olmak istiyorum.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 52. train:boun:pop_25:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `bicim_veya_baglam`

```text
Girdi: Diyeceksiniz ki "peki...
Hedef: Diyeceksiniz ki "peki...
```

Yarım alıntı ve kapanmayan tırnak; koruma örneğinde metin tamamlanmamalı.

### 53. train:boun:ins_1506:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `bicim_veya_baglam`

```text
Girdi: ■  Futbolla ilgili neler biliyorsunuz?
Hedef: ■  Futbolla ilgili neler biliyorsunuz?
```

Liste simgesi ve ardından iki boşluk var; birebir korunuyor.

### 54. train:boun:bio_92:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `uygun`

```text
Girdi: Bundan haberim bile yoktu.
Hedef: Bundan haberim bile yoktu.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 55. train:boun:bio_1749:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `uygun`

```text
Girdi: Peki ne oldu derseniz? Bulgaristan'a girdim.
Hedef: Peki ne oldu derseniz? Bulgaristan'a girdim.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 56. train:boun:pop_1989:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `bicim_veya_baglam`

```text
Girdi: nar pekmezi veya limon
Hedef: nar pekmezi veya limon
```

Tarif/malzeme listesi parçası; küçük harfle başlama ve noktasız bitiş korunmalı.

### 57. train:boun:news_1725:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `uygun`

```text
Girdi: Paris ve Londra, eski hegemon merkezlerini kaybediyorlar.
Hedef: Paris ve Londra, eski hegemon merkezlerini kaybediyorlar.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 58. train:boun:pop_10:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `bicim_veya_baglam`

```text
Girdi: 5 adet orta boy patates
Hedef: 5 adet orta boy patates
```

Malzeme listesi parçası; sayı ve biçim aynen korunuyor.

### 59. train:boun:bio_1755:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `uygun`

```text
Girdi: Evde de klima yok ki...
Hedef: Evde de klima yok ki...
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 60. train:boun:news_840:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `bicim_veya_baglam`

```text
Girdi: Fukaraya can suyu
Hedef: Fukaraya can suyu
```

Başlık niteliğinde isim öbeği; dönüşüm gerektirmiyor.

### 61. train:boun:news_528:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `uygun`

```text
Girdi: Yalman ne dedi?
Hedef: Yalman ne dedi?
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 62. train:boun:ins_1818:koruma

Tür: `koruma` / `turkce_karakter_gerektirmeyen` — `bicim_veya_baglam`

```text
Girdi: Yine bizimle beraber her yerde,
Hedef: Yine bizimle beraber her yerde,
```

Virgülle biten eksiltili ifade; devamı olmadan bağlam sınırlı.

### 63. train:boun:ins_185:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Bugün hepimiz çok çalışmış ve kurt gibi acıkmıştık.
Hedef: Bugün hepimiz çok çalışmış ve kurt gibi acıkmıştık.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 64. train:boun:ins_1689:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Kötümser gözler, güneşte bile kara kara lekeler bulacaklardır.
Hedef: Kötümser gözler, güneşte bile kara kara lekeler bulacaklardır.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 65. train:boun:pop_96:koruma

Tür: `koruma` / `turkce_karakterli` — `bicim_veya_baglam`

```text
Girdi: Peki, tuz ne yapıyor da balık gibi çok kısa zamanda bozulmaya ve özellikle de koku üretmeye son derece yatkın bir ürün uzun zaman saklanabiliyor? Gerçekten de balık vücudunda bulunan enzimler, buzdolabı ortamındaki düşük ısılarda bile aktif olarak faaliyet göstermeye devam edip bozulma sürecini hızlandırıyorlar.
Hedef: Peki, tuz ne yapıyor da balık gibi çok kısa zamanda bozulmaya ve özellikle de koku üretmeye son derece yatkın bir ürün uzun zaman saklanabiliyor? Gerçekten de balık vücudunda bulunan enzimler, buzdolabı ortamındaki düşük ısılarda bile aktif olarak faaliyet göstermeye devam edip bozulma sürecini hızlandırıyorlar.
```

Bir kayıtta iki uzun cümle bulunuyor; eğitim öncesinde tokenizer ile uzunluk denetlenmeli. İçerikteki bilimsel iddialar doğrulanmadı.

### 66. train:boun:bio_824:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Her gün Beldibi'ne, annemlerin yanına gidip geliyordum.
Hedef: Her gün Beldibi'ne, annemlerin yanına gidip geliyordum.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 67. train:boun:ins_1410:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Bütün bir günü çalışmadan büyük bir sessizlik içerisinde geçirdik.
Hedef: Bütün bir günü çalışmadan büyük bir sessizlik içerisinde geçirdik.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 68. train:boun:ess_612:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: O koşullarda, hangi dişi anne olmaya kalkışır, hangi er soyu devam etsin diler?
Hedef: O koşullarda, hangi dişi anne olmaya kalkışır, hangi er soyu devam etsin diler?
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 69. train:boun:pop_441:koruma

Tür: `koruma` / `turkce_karakterli` — `bicim_veya_baglam`

```text
Girdi: * Açık saçık konuşmanın her zaman iyi karşılanacağını zannetme.
Hedef: * Açık saçık konuşmanın her zaman iyi karşılanacağını zannetme.
```

Baştaki liste yıldızı korunuyor; hedef doğal.

### 70. train:boun:news_1869:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Hakan Ünsal'ın gönderilmesinin ardından Ergün'ün uzun süren sakatlığı, Altan'ın beklenen performansı gösterememesi, geçen sezon bu mevkide yıldızı parlayan Ayhan'ın sakatlanması, Hasan Şaş'ın sağ tarafa çekilmesi Belçikalı teknik adamın huzurunu kaçırdı.
Hedef: Hakan Ünsal'ın gönderilmesinin ardından Ergün'ün uzun süren sakatlığı, Altan'ın beklenen performansı gösterememesi, geçen sezon bu mevkide yıldızı parlayan Ayhan'ın sakatlanması, Hasan Şaş'ın sağ tarafa çekilmesi Belçikalı teknik adamın huzurunu kaçırdı.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 71. train:boun:ess_1114:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Ama atalarına ait mukaddesatların bugün nasıl alaya alınarak çiğnendiğini görmezlikten gelmek mümkün mü?
Hedef: Ama atalarına ait mukaddesatların bugün nasıl alaya alınarak çiğnendiğini görmezlikten gelmek mümkün mü?
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 72. train:boun:pop_1159:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Hayatın adil olduğunu düşünmek, sadece iyimser kişilerin iyimser bir yaklaşımı ya da saf kişilerin saflıklarını ortaya çıkartan bir tür yaklaşım biçimi olsa gerek.
Hedef: Hayatın adil olduğunu düşünmek, sadece iyimser kişilerin iyimser bir yaklaşımı ya da saf kişilerin saflıklarını ortaya çıkartan bir tür yaklaşım biçimi olsa gerek.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 73. train:boun:ess_1700:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Bunun yanında etrafındaki bütün bu insanlarla barışık olmayı da başarmalıdır.
Hedef: Bunun yanında etrafındaki bütün bu insanlarla barışık olmayı da başarmalıdır.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 74. train:boun:ins_1860:koruma

Tür: `koruma` / `turkce_karakterli` — `uygun`

```text
Girdi: Annesi, hiçbir şey yapmıyormuş.
Hedef: Annesi, hiçbir şey yapmıyormuş.
```

Hedef dilsel olarak doğal; gözlenen dönüşüm ve biçim görevle uyumlu.

### 75. train:boun:bio_1110:koruma

Tür: `koruma` / `turkce_karakterli` — `yeniden_incele`

```text
Girdi: Bu ismin bir başka açıklaması Büyük Kardan Hazinenin Batısı.
Hedef: Bu ismin bir başka açıklaması Büyük Kardan Hazinenin Batısı.
```

“Büyük Kardan Hazinenin Batısı” ifadesinin anlamı/özel ad niteliği bağlamsız belirsiz. Kaynakta da aynı; kesin hata sayılamaz, kaynak bağlamıyla yeniden incelenmeli.

