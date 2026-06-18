#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查漏补缺:对比每个批次"应采(提示词里列出的细类 + 该批模型集)"与"实采(模型返回里成功解析的细类)",
找出 缺文件/被截断(只给一部分)/缺编码。输出每模型待补编码清单 data/collected/xilei_gaps/<model>.json。
用法: python tools/xilei_gaps.py <返回根目录(镜像 大类N/层-NN/<model>.txt)>"""
import re, json, os, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from parse_xilei import parse, decode, XICODES, FN
PROMPTS = os.path.join(ROOT, 'docs', 'zhongyiyuan', 'prompts', 'xilei')
OCC = json.load(open(os.path.join(ROOT, 'data', 'occupations.cn.json'), encoding='utf-8'))
TITLE = {x['code']: x['title'] for g in OCC['groups'] for x in g.get('细类', [])}
ZT = {g['code']: g['title'] for g in OCC['groups']}

def bundle_codes(d):
    """从该批任一提示词 .md 抽取应采细类编码(有序)。"""
    md = sorted(glob.glob(os.path.join(d, '*.md')))
    if not md: return [], []
    t = open(md[0], encoding='utf-8').read()
    codes = re.findall(r'(\d-\d\d-\d\d-\d\d)', t)
    seen = [c for i, c in enumerate(codes) if c in XICODES and c not in codes[:i]]
    models = [os.path.splitext(os.path.basename(m))[0] for m in md]
    return seen, models

def main():
    rawroot = sys.argv[1]
    od = os.path.join(ROOT, 'data', 'collected', 'xilei_gaps'); os.makedirs(od, exist_ok=True)
    gaps = {}            # model -> [ {code,title,zt,bundle} ]
    rows = []            # report rows
    tot_exp = tot_missfile = tot_trunc = 0
    for d in sorted(glob.glob(os.path.join(PROMPTS, '大类*', '*-*'))):
        rel = os.path.relpath(d, PROMPTS)
        exp_codes, models = bundle_codes(d)
        if not exp_codes: continue
        for mdl in models:
            tot_exp += 1
            ret = os.path.join(rawroot, rel, mdl + '.txt')
            if not os.path.exists(ret):
                # try alt names via FN inverse not needed; mark whole bundle missing
                tot_missfile += 1
                rows.append((rel, mdl, 'NO_FILE', 0, len(exp_codes)))
                for c in exp_codes: gaps.setdefault(mdl, []).append({'code': c, 'title': TITLE.get(c, ''), 'zt': ZT.get('-'.join(c.split('-')[:2]), ''), 'bundle': rel})
                continue
            got = parse(decode(open(ret, 'rb').read()))
            miss = [c for c in exp_codes if c not in got]
            frac = 1 - len(miss) / len(exp_codes)
            tag = 'OK' if not miss else ('TRUNC' if frac >= 0.5 else 'BAD')
            if miss:
                tot_trunc += 1
                rows.append((rel, mdl, tag, len(exp_codes) - len(miss), len(exp_codes)))
                for c in miss: gaps.setdefault(mdl, []).append({'code': c, 'title': TITLE.get(c, ''), 'zt': ZT.get('-'.join(c.split('-')[:2]), ''), 'bundle': rel})
    # write per-model gap lists
    for mdl, items in gaps.items():
        json.dump(items, open(os.path.join(od, mdl + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # report
    print(f'应采(批次×模型)= {tot_exp}  缺整文件 = {tot_missfile}  有缺漏 = {tot_trunc}')
    print('\n各模型待补细类数(缺文件+被截断+漏项):')
    for mdl in sorted(gaps, key=lambda m: -len(gaps[m])):
        print(f'  {mdl:9} 待补 {len(gaps[mdl]):4}')
    print('\n缺整文件 / 严重截断(<50%) 明细:')
    for rel, mdl, tag, got, exp in rows:
        if tag in ('NO_FILE', 'BAD'):
            print(f'  {tag:7} {rel:22} {mdl:9} {got}/{exp}')
    print('\n写入待补清单 ->', od)

if __name__ == '__main__':
    main()
