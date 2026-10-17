"""Frozen test generation. Invoke only after explicit user approval, from repo root."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.compare_prompts import digest, save
from deasciification.evaluation import read_jsonl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approved', action='store_true', required=True)
    parser.parse_args()
    out = ROOT / 'reports/final-test'
    manifest = json.loads((out / 'freeze-manifest.json').read_text())
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == manifest['git_commit']
    changes = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=all'], cwd=ROOT, text=True)
    assert all(line.startswith('?? reports/final-test/') for line in changes.splitlines()), changes
    for name, expected in manifest['file_sha256'].items():
        assert digest(ROOT / name) == expected, name
    for dataset in manifest['datasets'].values():
        assert digest(ROOT / dataset['path']) == dataset['sha256'], dataset['path']
    assert digest(out / 'overlap-audit.json') == manifest['overlap_audit_sha256']
    assert json.loads((out / 'overlap-audit.json').read_text())['passed']
    rows = read_jsonl(ROOT / manifest['datasets']['test']['path'])
    assert len(rows) == manifest['datasets']['test']['examples']
    assert all(r['split'] == 'test' for r in rows)
    assert len({r['id'] for r in rows}) == len(rows)
    # Exclusive lock persists after failures: any infrastructure retry needs an explicit audit.
    with (out / 'generation-started.json').open('x') as stream:
        json.dump({'started_at': datetime.now(timezone.utc).isoformat(), 'manifest_sha256': digest(out / 'freeze-manifest.json')}, stream)
    state = {'status': 'running', 'completed': {}}
    save(out / 'generation-status.json', state)
    try:
        import torch
        from peft import PeftModel
        from deasciification.inference import load_model, generate_batch
        tokenizer, model, device, dtype = load_model()
        assert device == 'mps' and dtype == torch.float16, (device, dtype)
        for condition in ('pre_zero_shot', 'sft_zero_shot'):
            if condition == 'sft_zero_shot':
                model = PeftModel.from_pretrained(model, ROOT / manifest['adapter']['path'], is_trainable=False)
                model.config.use_cache = True
                model.eval()
            torch.manual_seed(0)
            state[condition + '_generation_config'] = model.generation_config.to_dict()
            with (out / (condition + '.jsonl')).open('x') as stream:
                for offset in range(0, len(rows), 8):
                    batch = rows[offset:offset + 8]
                    started = time.monotonic()
                    predictions = generate_batch(tokenizer, model, device, [r['input'] for r in batch], [], 256)
                    elapsed = time.monotonic() - started
                    for row, (output, tokens) in zip(batch, predictions, strict=True):
                        stream.write(json.dumps({'id': row['id'], 'output': output, 'generated_token_ids': tokens, 'generated_tokens': len(tokens), 'reached_token_limit': len(tokens) >= 256, 'seconds': elapsed / len(batch), 'batch_seconds': elapsed, 'batch_offset': offset}, ensure_ascii=False) + '\n')
                    stream.flush()
                    state['completed'][condition] = offset + len(batch)
                    save(out / 'generation-status.json', state)
                    print(f'{condition}: {offset + len(batch)}/{len(rows)} ({elapsed:.1f}s)', flush=True)
        state.update(status='complete', finished_at=datetime.now(timezone.utc).isoformat(), output_sha256={p.name: digest(p) for p in out.glob('*zero_shot.jsonl')})
        save(out / 'generation-status.json', state)
    except BaseException as exc:
        state.update(status='failed', error=repr(exc))
        save(out / 'generation-status.json', state)
        raise


if __name__ == '__main__':
    main()
