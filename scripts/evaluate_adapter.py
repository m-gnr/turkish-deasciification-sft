"""Compare a completed LoRA run with the frozen baseline on validation only."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from deasciification.evaluation import read_jsonl
from scripts.compare_prompts import digest, paired_intervals, save, summarize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, default=Path('reports/baselines/boun-v1-pre-sft.json'))
    args = parser.parse_args()
    training = json.loads((args.run / 'run.json').read_text())
    if training['status'] != 'complete' or training['run_type'] != 'full_train':
        raise ValueError('A completed full training run is required')
    baseline = json.loads(args.baseline.read_text())
    for name, expected in baseline['sha256'].items():
        if digest(Path(name)) != expected:
            raise ValueError(f'Frozen baseline changed: {name}')
    protocol = baseline['post_sft_protocol']
    data = Path('data/prepared/boun-v1/splits/validation.jsonl')
    rows = read_jsonl(data)
    if len(rows) != 900 or any(r['split'] != 'validation' for r in rows):
        raise ValueError('Expected fixed validation split')
    demos = json.loads(Path(protocol['demonstrations']).read_text())['examples']
    args.output.mkdir(parents=True, exist_ok=False)
    from peft import PeftModel
    import torch
    from deasciification.inference import load_model, generate_batch
    tokenizer, model, device, dtype = load_model()
    model = PeftModel.from_pretrained(model, args.run / 'adapter', is_trainable=False)
    model.config.use_cache = True
    model.eval()
    torch.manual_seed(0)
    metadata = {'status': 'running', 'training_run': str(args.run), 'baseline_sha256': digest(args.baseline),
                'validation_sha256': digest(data), 'device': device, 'dtype': str(dtype),
                'protocol': protocol, 'seed': 0,
                'adapter_sha256': {p.name: digest(p) for p in (args.run / 'adapter').glob('adapter*')},
                'code_sha256': digest(Path(__file__)), 'started_at': datetime.now(timezone.utc).isoformat(), 'completed': {}}
    save(args.output / 'metadata.json', metadata)
    comparisons = {}
    for condition, examples in [('zero_shot', []), ('five_shot', demos)]:
        outputs = {}
        with (args.output / f'{condition}.jsonl').open('x') as stream:
            for offset in range(0, len(rows), protocol['batch_size']):
                batch = rows[offset:offset + protocol['batch_size']]
                started = time.monotonic()
                predictions = generate_batch(tokenizer, model, device, [r['input'] for r in batch],
                                             examples, protocol['max_new_tokens'])
                elapsed = time.monotonic() - started
                for row, (output, tokens) in zip(batch, predictions, strict=True):
                    record = {'id': row['id'], 'output': output, 'generated_token_ids': tokens,
                              'generated_tokens': len(tokens), 'reached_token_limit': len(tokens) >= protocol['max_new_tokens'],
                              'seconds': elapsed / len(batch), 'batch_offset': offset}
                    stream.write(json.dumps(record, ensure_ascii=False) + '\n')
                    outputs[row['id']] = output
                stream.flush()
                metadata['completed'][condition] = offset + len(batch)
                save(args.output / 'metadata.json', metadata)
                print(f'{condition}: {offset + len(batch)}/900', flush=True)
        report = summarize(rows, outputs)
        save(args.output / f'{condition}-scores.json', report)
        before = json.loads((Path(baseline['run']) / f'{condition}-scores.json').read_text())
        interval = paired_intervals(rows, before, report)
        interval['direction'] = 'post_sft minus pre_sft, same prompt condition'
        comparisons[condition] = {'before': before['summary'], 'after': report['summary'], 'paired_bootstrap': interval}
        save(args.output / 'comparison.json', comparisons)
    lines = ['# İlk LoRA: doğrulama sonuçları', '',
             '900 doğrulama örneği; test kümesi değerlendirilmedi.', '',
             '| İstem | Metrik | Eğitim öncesi | Eğitim sonrası |',
             '| --- | --- | ---: | ---: |']
    for condition, result in comparisons.items():
        for metric in ('strict_compliance', 'sentence_exact', 'candidate_accuracy', 'required_correction'):
            before = result['before']['metrics'][metric]['rate']
            after = result['after']['metrics'][metric]['rate']
            lines.append(f'| {condition} | {metric} | {before:.2%} | {after:.2%} |')
    lines.extend(['', 'Farkların %95 eşleştirilmiş bootstrap aralıkları comparison.json içindedir.',
                  'Bu ilk eğitim koşusudur; nihai testten önce model/istem seçimi sabitlenmelidir.', ''])
    (args.output / 'README.md').write_text('\n'.join(lines))
    metadata.update(status='complete', finished_at=datetime.now(timezone.utc).isoformat(),
                    output_sha256={p.name: digest(p) for p in args.output.glob('*.json*') if p.name != 'metadata.json'})
    save(args.output / 'metadata.json', metadata)


if __name__ == '__main__':
    main()
