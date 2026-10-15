"""İndirilen Qwen modelini tek cümle üzerinde dene; eğitim yapmaz."""

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen3-1.7B"
REVISION = "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"
YONERGE = (
    "Metindeki eksik Türkçe karakterleri bağlama göre geri yükle. "
    "Yalnızca şu dönüşümlere izin ver: c→ç, C→Ç, g→ğ, G→Ğ, "
    "i→ı, I→İ, o→ö, O→Ö, s→ş, S→Ş, u→ü, U→Ü. "
    "Gerekmeyen harfleri değiştirme. Diğer karakterleri, mevcut Türkçe "
    "harfleri, boşlukları ve noktalama işaretlerini aynen koru. "
    "Yazım hatalarını düzeltme. Yalnızca sonuç metnini yaz; "
    "açıklama veya tırnak ekleme."
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metin", nargs="?", default="yarin ise gidecegim.")
    args = parser.parse_args()
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Kullanılan cihaz: {device}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL, revision=REVISION, local_files_only=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL,
        revision=REVISION,
        local_files_only=True,
        dtype=torch.float16 if device == "mps" else torch.float32,
    ).to(device)
    model.eval()
    messages = [
        {"role": "system", "content": YONERGE},
        {"role": "user", "content": args.metin},
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )
    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(device)
    print("Yanıt üretiliyor…", flush=True)
    with torch.inference_mode():
        outputs = model.generate(
            **inputs, max_new_tokens=128, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    tokens = outputs[0, inputs["input_ids"].shape[1]:]
    result = tokenizer.decode(tokens, skip_special_tokens=True)
    print("Girdi:", repr(args.metin))
    print("Çıktı:", repr(result))
    report = {
        "model": MODEL, "revision": REVISION, "device": device,
        "torch": torch.__version__, "instruction": YONERGE,
        "enable_thinking": False, "do_sample": False, "max_new_tokens": 128,
        "input": args.metin, "output": result,
        "generated_token_ids": tokens.tolist(),
    }
    path = Path(__file__).resolve().parent / "reports" / "ilk-deneme.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Sonuç kaydedildi: {path}")


if __name__ == "__main__":
    main()
