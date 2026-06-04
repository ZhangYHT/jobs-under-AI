#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聚合脚本 —— AI 众议院数据流水线
读取:
  data/occupations.cn.json                官方分类骨架(大类/中类/细类 + 数字S/绿色L)
  data/collected/step2_employment/*.json   各模型:就业人数 + 来源 + 置信度
  data/collected/step3_pay_edu/*.json       各模型:薪资中位数 + 学历 + 来源
  data/collected/step4_scoring/*.json       各模型:6 维 0-100 打分 + 理由
产出:
  data/aggregated.cn.json                  站点读取的成品
  data/qa_report.md                        人工复核工作单(存疑/缺官方源/低置信/分歧)
规则:
  步骤1-3 官方锚定 —— 取有官方来源的值;否则用中位数并标 provisional;保留所有来源。
  步骤4   集成     —— 每维 均值/中位数/标准差(分歧度) + 各模型分。
"""
import json, glob, os, statistics, collections

DIMS = ['overall', 'automation', 'augmentation', 'digital', 'moat', 'adoption']
ROOT = os.path.dirname(os.path.abspath(__file__))
def p(*a): return os.path.join(ROOT, *a)

def load_models(step):
    out = {}
    for f in sorted(glob.glob(p('data', 'collected', step, '*.json'))):
        model = os.path.splitext(os.path.basename(f))[0]
        try:
            rows = json.load(open(f, encoding='utf-8'))
            out[model] = {r['code']: r for r in rows if 'code' in r}
        except Exception as e:
            print(f'  [warn] 跳过 {f}: {e}')
    return out

def is_official(rec):
    """该来源是否官方级:置信度 high,或证据标注 official/事实。"""
    return rec.get('confidence') == 'high' or rec.get('evidence') in ('official', '事实')

def main():
    occ = json.load(open(p('data', 'occupations.cn.json'), encoding='utf-8'))
    groups = {g['code']: g for g in occ['groups']}
    emp = load_models('step2_employment')
    pe  = load_models('step3_pay_edu')
    sc  = load_models('step4_scoring')
    all_models = sorted(set(emp) | set(pe) | set(sc))

    out_groups, qa = [], []
    for code, g in groups.items():
        rec = {k: g.get(k) for k in ('code', 'title', 'parent', 'da_title',
                                     'digital', 'green', 'n_xi', 'n_digital', 'n_green')}
        rec['细类'] = g.get('细类', [])
        flags = []

        # ---- 步骤2 就业(官方锚定) ----
        e_rows = [(m, emp[m][code]) for m in emp if code in emp[m]
                  and emp[m][code].get('employment') is not None]
        vals = [r['employment'] for _, r in e_rows]
        official = [r for _, r in e_rows if is_official(r)]
        if official:
            rec['employment'] = int(statistics.median([r['employment'] for r in official]))
            rec['employment_basis'] = 'official'
        elif vals:
            rec['employment'] = int(statistics.median(vals)); rec['employment_basis'] = 'provisional'
            flags.append('employment_provisional')
        else:
            rec['employment'] = None; rec['employment_basis'] = 'missing'; flags.append('employment_missing')
        rec['employment_sources'] = [{'model': m, 'value': r.get('employment'),
                                       'source': r.get('source', ''), 'confidence': r.get('confidence', '')}
                                      for m, r in e_rows]
        if len(vals) > 1 and statistics.mean(vals) and statistics.pstdev(vals) / statistics.mean(vals) > 0.5:
            flags.append('employment_disagreement')

        # ---- 步骤3 薪资/学历(官方锚定) ----
        pay_rows = [(m, pe[m][code]) for m in pe if code in pe[m] and pe[m][code].get('pay_median') is not None]
        pays = [r['pay_median'] for _, r in pay_rows]
        pays_off = [r['pay_median'] for _, r in pay_rows if is_official(r)]
        rec['pay'] = int(statistics.median(pays_off or pays)) if (pays_off or pays) else None
        if pays and not pays_off and 'employment_provisional' not in flags:
            flags.append('pay_provisional')
        edus = [pe[m][code]['education'] for m in pe if code in pe[m] and pe[m][code].get('education')]
        rec['education'] = collections.Counter(edus).most_common(1)[0][0] if edus else None
        rec['pay_sources'] = [{'model': m, 'value': r.get('pay_median'), 'source': r.get('pay_source', '')}
                              for m, r in pay_rows]

        # ---- 步骤4 打分(集成) ----
        by_model, mean, median, std = {}, {}, {}, {}
        for d in DIMS:
            col = [(m, sc[m][code][d]) for m in sc if code in sc[m] and d in sc[m][code]]
            for m, v in col:
                by_model.setdefault(m, {})[d] = v
            vs = [v for _, v in col]
            if vs:
                mean[d] = round(statistics.mean(vs))
                median[d] = round(statistics.median(vs))
                std[d] = round(statistics.pstdev(vs), 1) if len(vs) > 1 else 0.0
        rec['dims'] = mean
        rec['dims_median'] = median
        rec['dims_std'] = std
        rec['by_model'] = by_model
        rec['rationales'] = {m: sc[m][code].get('rationale', '') for m in sc
                             if code in sc[m] and sc[m][code].get('rationale')}
        rec['n_models'] = len(by_model)
        rec['std'] = std.get('overall', 0)
        if rec['n_models'] == 0:
            flags.append('score_missing')
        elif std.get('overall', 0) >= 12:
            flags.append('score_disagreement')

        rec['flags'] = flags
        out_groups.append(rec)
        for fl in flags:
            qa.append((code, g['title'], fl))

    scored = [g for g in out_groups if g['n_models'] > 0 and g.get('employment')]
    tot = sum(g['employment'] for g in scored) or 1
    wavg = sum(g['dims'].get('overall', 0) * g['employment'] for g in scored) / tot

    agg = {
        'meta': {
            'title': 'AI 时代各岗位冲击图谱 · 中国版',
            'taxonomy': occ['meta'],
            'models': all_models, 'n_models': len(all_models),
            'unit': '中类(79)', 'dims': DIMS,
            'disclaimer': '分类与S/L标注源自官方大典;就业/薪资经众议院官方锚定(本数据含 provisional 项见 flags);AI 冲击分为多模型集成估算,仅供参考。',
        },
        'categories': occ['categories'],
        'groups': out_groups,
    }
    json.dump(agg, open(p('data', 'aggregated.cn.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 同时输出站点可直接 <script> 加载的数据(双击 HTML 也能渲染,免本地服务器)
    os.makedirs(p('site'), exist_ok=True)
    open(p('site', 'data.cn.js'), 'w', encoding='utf-8').write(
        'window.DATA=' + json.dumps(agg, ensure_ascii=False) + ';')

    # QA 报告
    by_flag = collections.defaultdict(list)
    for code, title, fl in qa:
        by_flag[fl].append(f'- `{code}` {title}')
    lines = ['# QA 复核工作单\n', f'模型数:{len(all_models)} ({", ".join(all_models) or "无"})  ·  中类:{len(out_groups)}\n']
    if not qa:
        lines.append('\n✅ 无 flag。\n')
    for fl in sorted(by_flag):
        lines.append(f'\n## {fl}({len(by_flag[fl])})\n')
        lines.extend(by_flag[fl])
    open(p('data', 'qa_report.md'), 'w', encoding='utf-8').write('\n'.join(lines))

    print(f'✅ aggregated.cn.json:{len(out_groups)} 中类 · 模型 {len(all_models)} ({",".join(all_models)})')
    print(f'   覆盖就业(样例)≈ {tot/1e8:.2f} 亿 · 就业加权综合冲击 {wavg:.1f}')
    print(f'   flag 统计:' + (', '.join(f'{k}={len(v)}' for k, v in sorted(by_flag.items())) or '无'))
    print(f'   QA 报告:data/qa_report.md')

if __name__ == '__main__':
    main()
