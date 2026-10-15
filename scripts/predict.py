"""İndirilen Qwen modelini tek cümle üzerinde dene; eğitim yapmaz."""

import argparse
import json
from pathlib import Path

import torch
from deasciification.config import MODEL, REVISION, YONERGE
from deasciification.inference import generate, load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metin", nargs="?", default="yarin ise gidecegim.")
    args = parser.parse_args()
    tokenizer, model, device, _ = load_model()
    print(f"Kullanılan cihaz: {device}", flush=True)
    print("Yanıt üretiliyor…", flush=True)
    result, tokens = generate(tokenizer, model, device, args.metin)
    print("Girdi:", repr(args.metin))
    print("Çıktı:", repr(result))
    report = {
        "model": MODEL, "revision": REVISION, "device": device,
        "torch": torch.__version__, "instruction": YONERGE,
        "enable_thinking": False, "do_sample": False, "max_new_tokens": 128,
        "input": args.metin, "output": result,
        "generated_token_ids": tokens,
    }
    path = Path(__file__).resolve().parents[1] / "reports" / "single-example" / "ilk-deneme.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Sonuç kaydedildi: {path}")


if __name__ == "__main__":
    main()
