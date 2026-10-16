"""Run full local training followed by validation; preserve logs and stage status."""
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys

from scripts.compare_prompts import save


def main():
    root = Path('runs/first-sft-v1')
    root.mkdir(parents=True, exist_ok=False)
    stages = [
        ('training', [sys.executable, '-m', 'scripts.train_lora', '--output', str(root / 'training')]),
        ('validation', [sys.executable, '-m', 'scripts.evaluate_adapter', '--run', str(root / 'training'),
                        '--output', 'reports/sft-validation/first-lora-v1']),
    ]
    state = {'status': 'running', 'pid': os.getpid(), 'started_at': datetime.now(timezone.utc).isoformat()}
    for stage, command in stages:
        state['stage'] = stage
        save(root / 'pipeline.json', state)
        with (root / f'{stage}.log').open('x') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        state[f'{stage}_exit_code'] = result.returncode
        if result.returncode:
            state.update(status='failed', finished_at=datetime.now(timezone.utc).isoformat())
            save(root / 'pipeline.json', state)
            raise SystemExit(result.returncode)
    state.update(status='complete', finished_at=datetime.now(timezone.utc).isoformat())
    save(root / 'pipeline.json', state)


if __name__ == '__main__':
    main()
