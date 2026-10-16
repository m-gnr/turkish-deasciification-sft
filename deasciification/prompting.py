"""Construct prompts without validation targets; freeze training demonstrations."""
import hashlib
from .config import YONERGE


def select_examples(train, validation):
    if any(r.get('split') != 'train' for r in train):
        raise ValueError('Demonstrations must come from the training split')
    if {r['source_id'] for r in train} & {r['source_id'] for r in validation}:
        raise ValueError('Training and validation sources overlap')
    selected = []
    for category, count in [('tam', 3), ('kismi', 1), ('koruma', 1)]:
        pool = [r for r in train if r['category'] == category and 40 <= len(r['input']) <= 150]
        pool.sort(key=lambda r: hashlib.sha256(('few-shot-v1:' + r['id']).encode()).hexdigest())
        if len(pool) < count:
            raise ValueError(f'Insufficient examples: {category}')
        selected.extend(pool[:count])
    return selected


def build_messages(text, examples=()):
    messages = [{'role': 'system', 'content': YONERGE}]
    for row in examples:
        messages.extend([{'role': 'user', 'content': row['input']},
                         {'role': 'assistant', 'content': row['target']}])
    messages.append({'role': 'user', 'content': text})
    return messages
