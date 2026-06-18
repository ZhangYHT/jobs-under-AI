#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析自然语言版 step4(每行:编码 名称:理由。综合冲击 XX),抽出每个中类的 overall+理由,
以及每个大类的总冲击+一句话总结。写入 data/collected/step4_overall/<model>.json 和 step4_da/<model>.json。
用法: python tools/parse_step4_nl.py <raw_dir>"""
import re, json, os, sys, glob, bisect
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES = {g['code'] for g in json.load(open(os.path.join(ROOT,'data','occupations.cn.json'),encoding='utf-8'))['groups']}
FN = {'chatgpt':'gpt','gpt':'gpt','deepseek':'deepseek','glm':'zhipu','智谱':'zhipu','智谱清言':'zhipu',
 'gemini':'gemini','grok':'grok','kimi':'kimi','千问':'qwen','通义':'qwen','通义千问':'qwen','qwen':'qwen',
 '文心':'wenxin','文心一言':'wenxin','wenxin':'wenxin','腾讯元宝':'yuanbao','元宝':'yuanbao','yuanbao':'yuanbao',
 '豆包':'doubao','doubao':'doubao','claude':'claude'}
DAW = {'1':'1','一':'1','2':'2','二':'2','3':'3','三':'3','4':'4','四':'4','5':'5','五':'5','6':'6','六':'6','7':'7','七':'7','8':'8','八':'8'}

def decode(b):
    if b[:2] in (b'\xff\xfe',b'\xfe\xff') or b.count(b'\x00')>len(b)//5:
        for e in ('utf-16','utf-16-le'):
            try:return b.decode(e)
            except:pass
    return b.decode('utf-8','replace')

def parse(t):
    if re.search(r'<!DOCTYPE|<html|<div|<script',t,re.I):
        t=re.sub(r'<(script|style)[\s\S]*?</\1>',' ',t,flags=re.I); t=re.sub(r'<[^>]+>',' ',t)
    codes=[(m.start(),m.group(1)) for m in re.finditer(r'(?<![\d-])(\d-\d\d)(?!-\d)',t)]
    cpos=[p for p,_ in codes]
    mid={}
    for m in re.finditer(r'综合冲击\D{0,4}(\d{1,3})',t):
        sp=m.start(); sc=int(m.group(1))
        if sc>100: continue
        i=bisect.bisect_left(cpos,sp)-1
        if i<0: continue
        p,c=codes[i]
        if c not in CODES or sp-p>500: continue
        seg=t[p:sp]
        seg=re.sub(r'^\s*\d-\d\d\s*','',seg)
        parts=re.split(r'[:：]',seg,1)
        reason=(parts[1] if len(parts)>1 else parts[0]).strip()
        reason=re.sub(r'[\*\s。、,，;；]+$','',reason)
        reason=re.sub(r'\s+',' ',reason)[:70]
        mid[c]=(sc,reason)   # 后写覆盖
    da={}
    for m in re.finditer(r'大类\s*([0-9一二三四五六七八])[^0-9\n]{0,50}?总冲击\D{0,4}(\d{1,3})',t):
        c=DAW.get(m.group(1)); v=int(m.group(2))
        if c and v<=100:
            tail=t[m.end():m.end()+90]
            s=re.split(r'\d-\d\d|##|\n',tail)[0].strip(' :：。()（）')
            da[c]=(v, re.sub(r'\s+',' ',s)[:60])
    return mid,da

def main():
    raw=sys.argv[1]
    od=os.path.join(ROOT,'data','collected','step4_overall'); os.makedirs(od,exist_ok=True)
    dd=os.path.join(ROOT,'data','collected','step4_da'); os.makedirs(dd,exist_ok=True)
    print('== 解析自然语言 step4 ==')
    for f in sorted(glob.glob(os.path.join(raw,'*'))):
        base=os.path.splitext(os.path.basename(f))[0]; key=FN.get(base.lower())
        if not key: print('  ?跳过',base); continue
        mid,da=parse(decode(open(f,'rb').read()))
        json.dump([{'code':c,'overall':v,'rationale':r} for c,(v,r) in mid.items()],
                  open(os.path.join(od,key+'.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
        json.dump([{'da':c,'total':v,'summary':s} for c,(v,s) in da.items()],
                  open(os.path.join(dd,key+'.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
        vs=[v for v,_ in mid.values()]
        tag='OK' if len(mid)>=79 else ('部分' if mid else '失败')
        print(f'  {tag:4} {base:12}->{key:9} 中类{len(mid):2}/79 大类{len(da)}/8  分数范围 {min(vs) if vs else "-"}-{max(vs) if vs else "-"}')

if __name__=='__main__': main()
