"""Çalıştırma betiklerinin kullandığı sabit model sürümünü indir."""
from huggingface_hub import snapshot_download
from deasciification.config import MODEL, REVISION


def main():
    print(snapshot_download(repo_id=MODEL, revision=REVISION))


if __name__ == "__main__":
    main()
