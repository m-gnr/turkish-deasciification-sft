"""Tek cümle ve toplu çalıştırma için ortak model işlemleri."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import MODEL, REVISION
from .prompting import build_messages


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


def generate(tokenizer, model, device, text, examples=(), max_new_tokens=128):
    messages = build_messages(text, examples)
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )
    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(device)
    with torch.inference_mode():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    tokens = outputs[0, inputs["input_ids"].shape[1]:].tolist()
    return tokenizer.decode(tokens, skip_special_tokens=True), tokens


def generate_batch(tokenizer, model, device, texts, examples=(), max_new_tokens=256):
    """Left-pad independent prompts; retain every generated non-padding token."""
    tokenizer.padding_side = 'left'
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    prompts = [tokenizer.apply_chat_template(
        build_messages(text, examples), tokenize=False,
        add_generation_prompt=True, enable_thinking=False) for text in texts]
    inputs = tokenizer(prompts, padding=True, return_tensors='pt', add_special_tokens=False).to(device)
    with torch.inference_mode():
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                                 pad_token_id=tokenizer.pad_token_id)
    result = []
    eos = model.generation_config.eos_token_id
    eos_ids = {eos} if isinstance(eos, int) else set(eos or [])
    for output in outputs[:, inputs['input_ids'].shape[1]:].tolist():
        # generate() pads finished sequences up to the longest output in the batch.
        stop = next((i + 1 for i, token in enumerate(output) if token in eos_ids), len(output))
        tokens = output[:stop]
        result.append((tokenizer.decode(tokens, skip_special_tokens=True), tokens))
    return result
