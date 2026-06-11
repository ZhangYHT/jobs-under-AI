#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析细类深评打分(自然语言评价 + 结构化尾行)。
尾行格式:〔编码 名称〕综合NN 自动化NN 增强NN 数字NN 护城河NN 落地NN ┃ 占比N% ┃ 学历X ┃ 薪资X ┃ 等级X
每个细类的评价 = 紧挨其尾行之前的那段自然语言。
输出 data/collected/xilei/<model>.json。用法: python tools/parse_xilei.py <raw_dir>"""
import re, json, os, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCC = json.load(open(os.path.join(ROOT, 'data', 'occupations.cn.json'), encoding='utf-8'))
XICODES = {x['code'] for g in OCC['groups'] for x in g.get('细类', [])}
FN = {'chatgpt':'gpt','gpt':'gpt','deepseek':'deepseek','glm':'zhipu','智谱':'zhipu','智谱清言':'zhipu',
 'gemini':'gemini','grok':'grok','kimi':'kimi','千问':'qwen','通义':'qwen','通义千问':'qwen','qwen':'qwen',
 '文心':'wenxin','文心一言':'wenxin','wenxin':'wenxin','腾讯元宝':'yuanbao','元宝':'yuanbao','yuanbao':'yuanbao',
 '豆包':'doubao','doubao':'doubao','claude':'claude'}

def decode(b):
    if b[:2] in (b'\xff\xfe', b'\xfe\xff') or b.count(b'\x00') > len(b)//5:
        for e in ('utf-16','utf-16-le'):
            try: return b.decode(e)
            except: pass
    return b.decode('utf-8','replace')

# 各种连字符/减号变体统一成 ASCII '-'(元宝爱用不换行连字符 U+2011,导致编码匹配失败)
DASHES = '‐‑‒–—―−－﹣'
DASH_TR = {ord(c): '-' for c in DASHES}

def num(label, s):
    m = re.search(label + r'\D{0,3}(\d{1,3})', s)
    return int(m.group(1)) if m and int(m.group(1)) <= 100 else None

def parse(t):
    t = t.translate(DASH_TR)
    if re.search(r'<!DOCTYPE|<html|<div', t, re.I):
        t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t, flags=re.I); t = re.sub(r'<[^>]+>', ' ', t)
    marks = [m.start() for m in re.finditer(r'〔', t)]
    out, prev = {}, 0
    for p in marks:
        nl = t.find('\n', p); end = nl if nl >= 0 else len(t)
        tail = t[p:end]
        mc = re.search(r'(\d-\d\d-\d\d-\d\d)', tail)
        if not mc or mc.group(1) not in XICODES:
            prev = end; continue
        code = mc.group(1)
        rec = {'code': code}
        for lab, key in [('综合','overall'),('自动化','automation'),('增强','augmentation'),
                         ('数字','digital'),('护城河','moat'),('落地','adoption'),('占比','share')]:
            v = num(lab, tail)
            if v is not None: rec[key] = v
        me = re.search(r'学历\s*(博士|硕士|本科|大专|高中|初中)', tail)
        if me: rec['education'] = me.group(1)
        ms = re.search(r'薪资\s*([高中低])', tail)
        if ms: rec['pay_tier'] = ms.group(1)
        ml = re.search(r'等级\s*(极高|极低|高|中|低)', tail)
        if ml: rec['level'] = ml.group(1)
        ev = t[prev:p]
        ev = re.sub(r'^\s*[\-*#>\d.、]*\s*', '', ev)              # 去前缀符号
        ev = re.split(r'〔', ev)[-1]
        ev = re.sub(r'^[^:：]{0,18}[:：]', '', ev, 1)             # 去"名称:"
        ev = re.sub(r'\s+', ' ', ev).strip(' 　。;；')[:140]
        if ev: rec['eval'] = ev
        if 'overall' in rec: out[code] = rec
        prev = end
    return out

def main():
    raw = sys.argv[1]
    od = os.path.join(ROOT, 'data', 'collected', 'xilei'); os.makedirs(od, exist_ok=True)
    print('== 解析细类深评 ==')
    agg = {}
    for f in sorted(glob.glob(os.path.join(raw, '**', '*'), recursive=True)):
        if os.path.isdir(f): continue
        base = os.path.splitext(os.path.basename(f))[0]
        base = re.sub(r'_b\d+$', '', base)            # 去分批后缀
        key = FN.get(base.lower())
        if not key: continue
        recs = parse(decode(open(f, 'rb').read()))
        agg.setdefault(key, {}).update(recs)          # 同模型多批合并
    for key, d in agg.items():
        rows = list(d.values())
        json.dump(rows, open(os.path.join(od, key + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        ov = [r['overall'] for r in rows if 'overall' in r]
        print(f'  {key:9} 细类 {len(rows):3}  分数 {min(ov) if ov else "-"}-{max(ov) if ov else "-"}')
    print('写入', od)

if __name__ == '__main__':
    main()
