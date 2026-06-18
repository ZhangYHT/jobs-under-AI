#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Arena.ai 双盲对战产出的匿名样本池化成一个低权重投票者。
每个细类在其大类的那对提示词里得到 2 份匿名答案(原件 + 副本)。
按编码汇总所有 arena 样本,逐维取均值,等级由池化后的综合分重新分档,
学历/薪资档取众数,评价取最长一条。产出 data/collected/xilei/arena.json,
聚合时作为权重 0.80 的匿名补充票并入(见 data/model_weights.json)。
用法: python tools/pool_arena.py [raw_dir]   默认 data/collected/xilei_raw/arena
"""
import os, sys, glob, json, statistics, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from parse_xilei import parse, decode

DIMS = ['overall', 'automation', 'augmentation', 'digital', 'moat', 'adoption']
def LEVEL(o): return '极高' if o >= 81 else '高' if o >= 61 else '中' if o >= 41 else '低' if o >= 21 else '极低'

def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'data', 'collected', 'xilei_raw', 'arena')
    samples = collections.defaultdict(list)            # code -> [rec, rec, ...]
    nfiles = 0
    for f in sorted(glob.glob(os.path.join(raw, '**', '*'), recursive=True)):
        if os.path.isdir(f) or os.path.basename(f).lower().startswith('readme'): continue
        nfiles += 1
        for code, rec in parse(decode(open(f, 'rb').read())).items():
            samples[code].append(rec)

    out = []
    for code, recs in samples.items():
        pooled = {'code': code}
        for d in DIMS:
            vs = [r[d] for r in recs if isinstance(r.get(d), (int, float))]
            if vs: pooled[d] = round(statistics.mean(vs))
        if 'overall' not in pooled: continue
        shs = [r['share'] for r in recs if isinstance(r.get('share'), (int, float))]
        if shs: pooled['share'] = round(statistics.mean(shs), 1)
        edus = [r['education'] for r in recs if r.get('education')]
        if edus: pooled['education'] = collections.Counter(edus).most_common(1)[0][0]
        tiers = [r['pay_tier'] for r in recs if r.get('pay_tier')]
        if tiers: pooled['pay_tier'] = collections.Counter(tiers).most_common(1)[0][0]
        evs = [r['eval'] for r in recs if r.get('eval')]
        if evs: pooled['eval'] = max(evs, key=len)
        pooled['level'] = LEVEL(pooled['overall'])
        pooled['n_arena'] = len(recs)
        out.append(pooled)

    od = os.path.join(ROOT, 'data', 'collected', 'xilei')
    os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, 'arena.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ov = [r['overall'] for r in out]
    pair = collections.Counter(r['n_arena'] for r in out)
    print(f'arena: {nfiles} 文件 → 池化 {len(out)} 细类  综合 {min(ov)}-{max(ov)}  每码样本数分布 {dict(pair)}')
    print('写入', os.path.join(od, 'arena.json'))

if __name__ == '__main__':
    main()
