#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 step1 各模型结果回填进 data/occupations.cn.json:
- english:跨模型多数票的规范英文译名(用于多语言)
- official_sources:各模型给出的官方来源去重合集(满足"更多官方来源")
官方编码/名称/S/L 标注以大典为准(不被模型覆盖);仅打印模型标记的名称存疑项供人工看。
"""
import json, os, glob, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
occ = json.load(open(os.path.join(ROOT, 'data', 'occupations.cn.json'), encoding='utf-8'))
groups = {g['code']: g for g in occ['groups']}

eng = collections.defaultdict(collections.Counter)
src = collections.defaultdict(dict)   # code -> {key: {name,url}}
mismatch = []
nmodels = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'collected', 'step1_taxonomy', '*.json'))):
    nmodels += 1
    for o in json.load(open(f, encoding='utf-8')):
        c = o.get('code')
        if c not in groups: continue
        e = (o.get('english') or '').strip()
        if e and len(e) < 80: eng[c][e] += 1
        if o.get('title_match') in (False, 'false', '不一致', 0):
            mismatch.append((c, o.get('title_official')))
        ss = o.get('sources') or []
        if isinstance(ss, dict): ss = [ss]
        for s in ss if isinstance(ss, list) else []:
            if isinstance(s, str): name, url = s, ''
            elif isinstance(s, dict): name, url = (s.get('name') or s.get('title') or '').strip(), (s.get('url') or '').strip()
            else: continue
            if not name and not url: continue
            k = (url or name).lower()
            src[c].setdefault(k, {'name': name, 'url': url})

ne = ns = 0
for c, g in groups.items():
    if eng[c]:
        g['english'] = eng[c].most_common(1)[0][0]; ne += 1
    if src[c]:
        g['official_sources'] = list(src[c].values())[:6]; ns += 1

json.dump(occ, open(os.path.join(ROOT, 'data', 'occupations.cn.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'回填:english {ne}/79 个中类 · official_sources {ns}/79 个中类(来自 {nmodels} 个模型的 step1)')
if mismatch:
    print(f'模型标记的名称存疑(供人工核,共{len(mismatch)}):', mismatch[:10])
