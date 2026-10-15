"""Tek cümle ve toplu çalıştırma için ortak model işlemleri."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import MODEL, REVISION, YONERGE


def load_model():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.float16 if device == "mps" else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL, revision=REVISION, local_files_only=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=REVISION, local_files_only=True, dtype=dtype,
    ).to(device)
    model.eval()
    return tokenizer, model, device, dtype


def generate(tokenizer, model, device, text):
    messages = [
        {"role": "system", "content": YONERGE},
        {"role": "user", "content": text},
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )
    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(device)
    with torch.inference_mode():
        outputs = model.generate(
            **inputs, max_new_tokens=128, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    tokens = outputs[0, inputs["input_ids"].shape[1]:].tolist()
    return tokenizer.decode(tokens, skip_special_tokens=True), tokens
