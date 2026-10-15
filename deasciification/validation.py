#!/usr/bin/env python3
"""Pilot/egitim verisi dogrulayici.
Kullanim:
  python -m scripts.validate_data data/pilot.jsonl
  python -m scripts.validate_data data/pilot.jsonl --check "aday egitim cumlesi"
"""
import json, re, unicodedata
from collections import Counter
from difflib import SequenceMatcher

ALLOWED = {'c': 'cç', 'C': 'CÇ', 'g': 'gğ', 'G': 'GĞ', 'i': 'iı', 'I': 'Iİ',
           'o': 'oö', 'O': 'OÖ', 's': 'sş', 'S': 'SŞ', 'u': 'uü', 'U': 'UÜ'}
CORRUPT = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
           'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'}
TURKISH = 'çğıöşüÇĞİÖŞÜ'


def fold(s):
    """Yalnizca yakin-tekrar karsilastirmasi icin: ASCII'ye indirge, kucult."""
    return ''.join(CORRUPT.get(c, c) for c in s).lower()


def key(s):
    return re.sub(r'[^\w ]', '', fold(s)).strip()


def compliant(inp, out):
    return len(inp) == len(out) and all(
        o == i or o in ALLOWED.get(i, '') for i, o in zip(inp, out))


def derivable(inp, tgt):
    """Girdi, hedeften yalniz CORRUPT eslemesiyle uretilebilir mi? -> (ok, n_uygun, n_bozulan)"""
    if len(inp) != len(tgt):
        return False, 0, 0
    n = k = 0
    for i, t in zip(inp, tgt):
        if t in CORRUPT:
            n += 1
            if i == CORRUPT[t]:
                k += 1
            elif i != t:
                return False, n, k
        elif i != t:
            return False, n, k
    return True, n, k


def spans(s):
    return [m.group() for m in re.finditer(r'\S+', s)]


def focus(r):
    wi, wt, j = spans(r['input']), spans(r['target']), r.get('focus_word_index')
    if j is None or len(wi) != len(wt) or not 0 <= j < len(wi):
        return None
    return wi[j], wt[j]


def validate_data(path, cand=None):
    recs = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    errs, cov, variants, cats = [], Counter(), Counter(), Counter()
    amb_n = amb_ok = 0
    for r in recs:
        rid, inp, tgt = r['id'], r['input'], r['target']
        cats[r['category']] += 1
        for name, s in (('input', inp), ('target', tgt)):
            if not unicodedata.is_normalized('NFC', s):
                errs.append(f'{rid}: {name} NFC degil')
            if '\u0307' in s:
                errs.append(f'{rid}: {name} birlesik nokta (U+0307) iceriyor')
        if not compliant(inp, tgt):
            errs.append(f'{rid}: hedef girdiyle konum bazli uyumsuz')
        ok, n, k = derivable(inp, tgt)
        if not ok:
            errs.append(f'{rid}: girdi hedeften bozma eslemesiyle uretilemiyor')
        variants['koruma' if k == 0 else 'tam' if k == n else 'kismi'] += 1
        for i, t in zip(inp, tgt):
            if i in ALLOWED:
                amb_n += 1
                amb_ok += (i == t)
                if i != t:
                    cov[t] += 1
        if 'focus_word_index' in r and focus(r) is None:
            errs.append(f'{rid}: focus_word_index gecersiz')
    pairs = {}
    for r in recs:
        if 'pair_id' in r:
            pairs.setdefault(r['pair_id'], []).append(r)
    for pid, rs in pairs.items():
        if len(rs) != 2 or any(focus(x) is None for x in rs):
            errs.append(f'{pid}: cift eksik/gecersiz ({len(rs)} kayit)')
            continue
        (ia, ta), (ib, tb) = focus(rs[0]), focus(rs[1])
        if ia != ib:
            errs.append(f'{pid}: odak kelimelerin girdisi ayni degil ({ia} / {ib})')
        if ta == tb:
            errs.append(f'{pid}: odak hedefleri ayni, minimal cift degil')
    near = []
    for a in range(len(recs)):
        for b in range(a + 1, len(recs)):
            ka, kb = key(recs[a]['target']), key(recs[b]['target'])
            if ka and kb and (ka in kb or kb in ka or SequenceMatcher(None, ka, kb).ratio() >= 0.8):
                near.append((recs[a]['id'], recs[b]['id']))

    print(f'{len(recs)} kayit | kategori: {dict(cats)}')
    print(f'bozma turu (veriden turetilen): {dict(variants)}')
    print(f'hic-degistirme, belirsiz harf dogrulugu: {amb_ok}/{amb_n} = {amb_ok / amb_n:.1%}')
    print('gerekli duzeltme sayilari:', {c: cov[c] for c in TURKISH})
    print('eksik harf kapsami:', [c for c in TURKISH if cov[c] == 0] or 'yok')
    print('ayni kaynak adayi (source_id gerekli):', near or 'yok')
    print('HATALAR:' if errs else 'hata yok', *errs, sep='\n  ')
    if cand:
        kc = key(cand)
        hits = sorted(((SequenceMatcher(None, kc, key(r['target'])).ratio(), r['id'], r['target'])
                       for r in recs), reverse=True)[:3]
        cont = [r['id'] for r in recs if kc in key(r['target']) or key(r['target']) in kc]
        print(f'\n--check {cand!r}')
        print('  icerme/yakin tekrar:', cont or 'yok')
        for s, i, t in hits:
            print(f'  {s:.2f} {i} {t}')
