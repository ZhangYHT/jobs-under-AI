#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并各批别名 harvest 结果 -> data/aliases.cn.json。
读取 data/collected/aliases_raw/*.json(每个 {code:[别名,...]},gen_* 富量优先、old_* 旧保守批补充)。
清洗:并集去重(大小写不敏感)、剔与官方名/编码相同、去破折号、限长限量。
产物 data/aliases.cn.json 由 aggregate.py 读入,写到每个中类/细类的 alias 字段,供搜索 rankHits 命中。"""
import json, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def p(*a): return os.path.join(ROOT, *a)

occ = json.load(open(p('data', 'occupations.cn.json'), encoding='utf-8'))
TITLE = {}
for g in occ['groups']:
    TITLE[g['code']] = g.get('title', '')
    for x in g.get('细类', []):
        TITLE[x['code']] = x.get('title', '')

MAXLEN, MAXN = 16, 15
def clean(code, lst):
    t = TITLE.get(code, ''); tl = t.lower()
    seen, out = set(), []
    for a in lst:
        a = (a or '').strip().strip('、,，/ ').strip()
        if not a or a == t or a == code: continue
        if any(c in a for c in '–—'): continue   # en/em dash
        if len(a) > MAXLEN: continue
        k = a.lower()
        if k == tl or k in seen: continue
        seen.add(k); out.append(a)
        if len(out) >= MAXN: break
    return out

merged = {}
for f in sorted(glob.glob(p('data', 'collected', 'aliases_raw', '*.json'))):  # gen_* 先于 old_*
    for code, lst in json.load(open(f, encoding='utf-8')).items():
        merged.setdefault(code, []).extend(lst)

out = {}
for code in sorted(merged):
    al = clean(code, merged[code])
    if al: out[code] = al

json.dump(out, open(p('data', 'aliases.cn.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
tot = sum(len(v) for v in out.values())
print(f'aliases.cn.json: {len(out)} codes / {tot} aliases (官方职业共 {len(TITLE)})')
