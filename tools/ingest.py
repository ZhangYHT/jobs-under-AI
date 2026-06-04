#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""健壮摄取众议院各模型的返回(容错救回),归一化写入 data/collected/<step>/<key>.json。
用法: python tools/ingest.py <step> <raw_dir>
  step: step1_taxonomy | step2_employment | step3_pay_edu | step4_scoring
按文件名识别模型;救回 JSON(去代码围栏/修尾逗号/修控制字符/逐对象救/UTF-16/HTML);
归一化字段(含中文键名同义词);按官方 79 中类编码校验。打印逐模型质检报告。
"""
import json, re, os, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCC = json.load(open(os.path.join(ROOT, 'data', 'occupations.cn.json'), encoding='utf-8'))
CODES = {g['code'] for g in OCC['groups']}

FNAME2KEY = {  # 文件名(小写,去扩展)-> 模型键
 'chatgpt':'gpt','gpt':'gpt','openai':'gpt','deepseek':'deepseek','glm':'zhipu','智谱':'zhipu','智谱清言':'zhipu',
 'gemini':'gemini','grok':'grok','kimi':'kimi','千问':'qwen','通义':'qwen','通义千问':'qwen','qwen':'qwen',
 '文心':'wenxin','文心一言':'wenxin','wenxin':'wenxin','腾讯元宝':'yuanbao','元宝':'yuanbao','yuanbao':'yuanbao',
 '豆包':'doubao','doubao':'doubao','claude':'claude',
}
SYN = {  # 规范键 -> 可能出现的同义键
 'code':['code','中类编码','编码','中类代码','代码'],
 'title_official':['title_official','中类官方名称','官方名称','名称','title','中类名称'],
 'title_match':['title_match','校验结果','是否一致','match','一致'],
 'english':['english','规范英文译名','英文名','英文名称','english_name','en'],
 'digital_xilei':['digital_xilei','含数字职业细类','数字职业','数字职业细类','digital'],
 'green_xilei':['green_xilei','含绿色职业细类','绿色职业','绿色职业细类','green'],
 'sources':['sources','官方来源链接','来源','来源链接','source','官方来源'],
 'confidence':['confidence','置信度'],'evidence':['evidence','证据类型','证据'],
 'note':['note','备注','含双重标记细类','说明'],
 # 后续步骤字段
 'employment':['employment','就业人数','人数'],'pay_median':['pay_median','年薪中位数','薪资中位数','中位年薪'],
 'education':['education','学历','典型学历'],
 'overall':['overall','综合冲击'],'automation':['automation','任务自动化'],'augmentation':['augmentation','ai增强','增强'],
 'digital':['digital','数字化程度','数字化'],'moat':['moat','护城河'],'adoption':['adoption','落地速度'],
 'rationale':['rationale','理由','简短理由'],
}
KEY2CANON = {syn.lower(): canon for canon, l in SYN.items() for syn in l}

def decode(b):
    if b[:2] in (b'\xff\xfe', b'\xfe\xff') or b.count(b'\x00') > len(b)//5:
        for enc in ('utf-16','utf-16-le','utf-16-be'):
            try: return b.decode(enc)
            except Exception: pass
    return b.decode('utf-8', errors='replace')

def fix_frag(s):
    s = re.sub(r',\s*([\]}])', r'\1', s)        # 尾逗号
    s = re.sub(r'[\x00-\x1f]', ' ', s)          # 所有控制字符(含字符串内裸换行/制表)-> 空格
    return s

def salvage_objects(s):
    objs, depth, start, instr, esc = [], 0, None, False, False
    for i, ch in enumerate(s):
        if instr:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': instr = False
            continue
        if ch == '"': instr = True
        elif ch == '{':
            if depth == 0: start = i
            depth += 1
        elif ch == '}':
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    frag = s[start:i+1]
                    for cand in (frag, fix_frag(frag)):
                        try: objs.append(json.loads(cand)); break
                        except Exception: continue
                    start = None
    return objs

def parse(text):
    t = re.sub(r'```[a-zA-Z]*', '', text).replace('```', '')
    if re.search(r'<!DOCTYPE|<html', t, re.I):           # HTML 存档:去标签
        t = re.sub(r'<[^>]+>', ' ', t)
    i, j = t.find('['), t.rfind(']')
    if 0 <= i < j:
        for cand in (t[i:j+1], fix_frag(t[i:j+1])):
            try: return json.loads(cand)
            except Exception: pass
    return salvage_objects(t)                            # 逐对象救(容截断)

def norm_obj(o):
    out = {}
    for k, v in o.items():
        ck = KEY2CANON.get(str(k).strip().lower())
        if ck: out[ck] = v
    if 'code' in out:
        out['code'] = str(out['code']).strip()
    return out

def main():
    step, raw = sys.argv[1], sys.argv[2]
    outdir = os.path.join(ROOT, 'data', 'collected', step); os.makedirs(outdir, exist_ok=True)
    print(f'== 摄取 {step} 从 {raw} ==')
    for f in sorted(glob.glob(os.path.join(raw, '*'))):
        base = os.path.splitext(os.path.basename(f))[0]
        key = FNAME2KEY.get(base.lower())
        if not key:
            print(f'  ? 跳过(未识别模型名): {base}'); continue
        data = parse(decode(open(f, 'rb').read()))
        objs = [norm_obj(o) for o in data if isinstance(o, dict)]
        objs = [o for o in objs if o.get('code') in CODES]
        # 去重保留首次
        seen, uniq = set(), []
        for o in objs:
            if o['code'] in seen: continue
            seen.add(o['code']); uniq.append(o)
        json.dump(uniq, open(os.path.join(outdir, key+'.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        miss = len(CODES) - len(seen)
        tag = 'OK' if len(seen) >= 79 else ('截断/不全' if len(seen) > 0 else '失败')
        print(f'  {tag:8} {base:12}->{key:9} 有效中类 {len(seen):2}/79  缺{miss:2}')
    print('完成。写入', outdir)

if __name__ == '__main__':
    main()
