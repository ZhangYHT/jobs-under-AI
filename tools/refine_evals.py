#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把细类评价从 xilei_raw 重新抽取得更长更干净(原 parse_xilei 截到140),
仅更新 data/collected/xilei/<model>.json 里的 'eval' 字段,其余字段(六维/占比/学历/
薪资/等级,含 subagent 已救回的)保持不变。用法: python tools/refine_evals.py"""
import re, os, sys, glob, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from parse_xilei import decode, XICODES, DASH_TR, FN

CAP = 220
# 像"思考过程/方法论/报告脚手架"的开头,整条丢弃
BAD_PREFIX = ('我来', '我将', '我先', '首先', '接下来', '好的', '收到', '根据搜索', '本报告', '评估说明',
              '方法论', '口径', '以下是', '让我', '现在', '第一步', '步骤')
def clean(ev):
    ev = re.split(r'〔', ev)[-1]
    ev = re.sub(r'^\s*[\-*#>•·\d.、\s]+', '', ev)                         # 去前缀符号/编号
    ev = re.sub(r'^\**\s*(中类\s*)?\d-\d\d(-\d\d-\d\d)?\s*[^\n:：]{0,16}\**\s*[:：]?\s*', '', ev)  # 去"中类X-XX 名称:"/"X-XX-XX-XX 名称"
    ev = re.sub(r'^[^:：\n]{0,16}[:：]\s*', '', ev, 1)                    # 去"名称:"
    ev = re.sub(r'\s*[（(]\[[^\n]*$', '', ev)                            # 去 ([来源…] 引用括注(常截断)
    ev = re.sub(r'\[[^\]\n]{0,40}\]', '', ev)                            # 去 [1]/[来源]
    ev = re.sub(r'[（(]\s*[)）]', '', ev)
    ev = re.sub(r'\s+', ' ', ev).strip(' 　*。;；,，、')
    return ev[:CAP].rstrip(' 　*,，、')

def extract(t):
    t = t.translate(DASH_TR)
    if re.search(r'<!DOCTYPE|<html|<div', t, re.I):
        t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t, flags=re.I); t = re.sub(r'<[^>]+>', ' ', t)
    marks = [m.start() for m in re.finditer(r'〔', t)]
    out, prev = {}, 0
    for p in marks:
        nl = t.find('\n', p); end = nl if nl >= 0 else len(t)
        tail = t[p:end]
        mc = re.search(r'(\d-\d\d-\d\d-\d\d)', tail)
        if not mc or mc.group(1) not in XICODES: prev = end; continue
        ev = clean(t[prev:p])
        if len(ev) >= 10 and not ev.startswith(BAD_PREFIX): out[mc.group(1)] = ev
        prev = end
    return out

def main():
    raw = os.path.join(ROOT, 'data', 'collected', 'xilei_raw')
    agg = {}
    for f in sorted(glob.glob(os.path.join(raw, '**', '*'), recursive=True)):
        if os.path.isdir(f): continue
        base = re.sub(r'_b\d+$', '', os.path.splitext(os.path.basename(f))[0]).lower()
        key = FN.get(base) or (base if re.match(r'arena\d*$', base) else None)
        if not key: continue
        for c, ev in extract(decode(open(f, 'rb').read())).items():
            d = agg.setdefault(key, {})
            if len(ev) > len(d.get(c, '')): d[c] = ev      # 同模型多文件取更长
    od = os.path.join(ROOT, 'data', 'collected', 'xilei')
    tot = 0
    for f in sorted(glob.glob(os.path.join(od, '*.json'))):
        key = os.path.splitext(os.path.basename(f))[0]
        rows = json.load(open(f, encoding='utf-8')); ev = agg.get(key, {}); n = 0
        for r in rows:
            ne = ev.get(r.get('code'))
            if ne and len(ne) > len(r.get('eval', '') or ''):
                r['eval'] = ne; n += 1
        json.dump(rows, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        tot += n; print(f'  {key:9} 更新 eval {n:4} 条')
    print('细类评价加长完成,共更新', tot, '条')

if __name__ == '__main__':
    main()
