"""Download checksum-locked BOUN sources, or verify the existing cache."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen
import hashlib

from deasciification.data import digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=Path('configs/data-source.json'))
    p.add_argument('--output', type=Path, default=Path('data/raw/boun'))
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    for name, entry in config['files'].items():
        path = args.output / name
        if not path.exists():
            with urlopen(entry['url'], timeout=60) as response:
                content = response.read()
            if hashlib.sha256(content).hexdigest() != entry['sha256']:
                raise ValueError(f'Download checksum mismatch: {name}')
            path.write_bytes(content)
        if digest(path) != entry['sha256']:
            raise ValueError(f'Cache checksum mismatch: {path}')
        print(f'OK {name}')


if __name__ == '__main__':
    main()
