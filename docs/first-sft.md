# İlk SFT koşusu — 16 Ekim 2026

Önce [40 örnek incelemesi](../reports/error-review/boun-v1-20261016/README.md) tamamlandı;
[baseline](../reports/baselines/boun-v1-pre-sft.json) yeniden puanlanıp SHA-256 özetleriyle sabitlendi.
Metrik tanımları değiştirilmedi. Eğitim sonrası sonuçlar hazır olmadan başarı iddiası yoktur.

## Eğitim

- Qwen/Qwen3-1.7B, mevcut sabit revision ve yönerge.
- Apple Silicon MPS, float16 temel ağırlıklar, PEFT LoRA; QLoRA kullanılmıyor.
- q_proj/v_proj, rank 8, alpha 16, dropout 0.05: 1.605.632 eğitilebilir parametre.
- 7.340 örneğin tamamı, 1 epoch; mikro batch 1, gradient accumulation 16.
- AdamW, öğrenme oranı 0.0002, cosine schedule, yaklaşık %3 warmup, seed 42.
- Yalnız hedef cevap ve EOS loss'a katılır; yönerge, kullanıcı girdisi, boş düşünme öneki ve padding maskelenir.
- Gradient checkpointing açık. Maksimum 1.024 token; gerçek en uzun örnek 506 token.
  Uzun örnekler sessizce kesilmez, sınır aşılırsa çalıştırma durur.
- Eğitim karışımı 4.404 tam / 1.835 kısmi / 1.101 koruma. Test verisi eğitim kodunda açılmaz.
- Her 100 optimizer adımında checkpoint, son iki checkpoint saklanır; son adapter ayrıca kaydedilir.

PEFT yaklaşımı [resmi LoRA belgesine](https://huggingface.co/docs/peft/main/package_reference/lora)
dayanır. Parametreler ilk deney tercihidir; optimize edilmiş ayarlar olduğu iddia edilmez.

## Çalıştırma

```bash
.venv/bin/python -m pip install -r requirements-training.txt
.venv/bin/python -m scripts.run_first_sft
```

Koşu adı sabittir; mevcut klasörün üzerine yazmaz. Bu komut önce tam eğitimi, başarılı
olursa aynı 900 doğrulama örneğinin zero-shot ve sabit five-shot değerlendirmesini çalıştırır.
İlk koşu yerelde `caffeinate -i` altında başlatıldı; süreç açıkken boşta uyku engellenir.
Bilgisayarın kapanması/yeniden başlaması veya kapağın kapatılması sonrası otomatik devam garantisi yoktur.

Durum: `runs/first-sft-v1/pipeline.json`.
Eğitim günlüğü: `runs/first-sft-v1/training.log`.
Adapter: `runs/first-sft-v1/training/adapter/`.
Doğrulama günlüğü: `runs/first-sft-v1/validation.log`.
Sonuçlar: `reports/sft-validation/first-lora-v1/`.
`status: complete` görülmeden ilgili aşama bitmiş sayılmaz.

Bağımsız çalıştırma:

```bash
.venv/bin/python -m scripts.train_lora --output runs/another-lora
.venv/bin/python -m scripts.evaluate_adapter --run runs/another-lora --output reports/sft-validation/another-lora
```

## Doğrulama ve test sınırı

Çıktılar temizlenmez. Baseline ile aynı 8'li batch, greedy üretim, 256 yeni token sınırı,
düşünme kapalı biçim ve aynı beş eğitim gösterimi kullanılır. Her istem koşulunda eğitim
öncesi/sonrası farklar kaynak gruplarını koruyan 2.000 tekrarlı bootstrap ile raporlanır.

İlk seçim kuralı katı uyumu öncelemek, eşitlikte tam eşleşmeye bakmaktır; diğer metrikler
birlikte raporlanır. Baseline da aday olarak korunmalıdır; SFT'nin daha iyi olması varsayılmaz.
Bu ilk koşudan sonra checkpoint/istem seçimi sabitlenmeden 900 test örneği açılmaz.
Otomatik boru hattı doğrulamada durur; nihai test ölçümü içermez.

## Kontroller

30 unittest geçti. Gerçek tokenizer ile hedef ve EOS dışında loss etiketi bulunmadığı
kontrol edildi. İki optimizer adımlık yerel deneme `runs/lora-smoke-v2` içinde başarıyla
adapter kaydetti; parametreler sonlu. Bu deneme tam SFT sonucu değildir.
