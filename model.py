from huggingface_hub import snapshot_download

model_klasoru = snapshot_download(
    repo_id="Qwen/Qwen3-1.7B"
)

print(model_klasoru)