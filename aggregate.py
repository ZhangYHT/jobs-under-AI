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
import json, glob, os, re, statistics, collections

DIMS = ['overall', 'automation', 'augmentation', 'digital', 'moat', 'adoption']
def LEVEL(o): return '极高' if o >= 81 else '高' if o >= 61 else '中' if o >= 41 else '低' if o >= 21 else '极低'
PAY_TIER = {'高': 1.3, '中': 1.0, '低': 0.75}
ROOT = os.path.dirname(os.path.abspath(__file__))
def p(*a): return os.path.join(ROOT, *a)

def clean_rat(t):
    """清掉中类理由里串进来的评分尾巴/下一条编码名称(parse_step4 的 70 字截断遗留),用作简介回退。"""
    t = re.split(r'综合冲击', t)[0]                     # 砍掉串入的评分尾巴(连带其后的下一条编码名称)
    t = re.sub(r'^[^:：\n]{0,14}[:：]\s*', '', t)       # 去开头"名称:"标签
    return t.strip(' 　。.，,、;；')

# 细类代表性评价(eval)的污染识别:剔除"思考过程/方法论/批次脚手架/报告标题/跨批汇总/装饰横幅/HTML"
# 等非本细类正文的候选,使各细类从 13 个模型里挑到真正描述本职业的那条(详见 README 数据说明)。
EVAL_START = ('占比', '学历', '薪资', '等级', '综合', '说明', '注', '本中类', '同一中类')
_EVAL_BAD = re.compile(
    r'好的[，,。]|收到[，,。]|^行[，,]|来[，,]\s*先[交上给]|先出前|这个批次|继续(输出|交|给)|我来|我将|我们开始|让我[来帮]|我先|我明确|我需要|首先[，,]|现在开始|下面(按|开始)|'
    r'根据搜索|基于搜索|本报告|以下是|打分标准|评分标准|评分口径|统计口径|(占比|学历|薪资)[^。]{0,12}口径|作为(研究|资深|一名|对)|从第一性原理|基于(公开|国内官方)|官方智库|头部招聘|'
    r'研究报告|评估报告|综合评估报告|深度研究|宏观背景|中类研判|研判脉络|涵盖编码|编码范围|细类深评|系列[｜|]|评估说明|方法论|摘要[ 　]|'
    r'中类\s*[「『]|中类\s*\d|大类\s*[\d一二三四五六]|小类\s*\d|第\s*[\d一二三四五六]\s*[/／]?\s*[\d六]?\s*批|共[6六]批|逐一(进行|处理|评估)|上述(职业|细类|岗位)|本批[次的]|得分均(超过|高于|低于|在)|\d\s*个细类|集群[（(]约|'
    r'[═━─＝]{3,}|={4,}|</?[a-zA-Z]|section-|WEF|OECD|ILO|O\*NET')
def bad_eval(e):
    return (not e) or e.startswith(EVAL_START) or bool(_EVAL_BAD.search(e[:60]))
def clean_eval_head(e):
    e = re.sub(r'^[\s#>*•·\-]+', '', e)                 # 去开头 markdown/项目符
    e = re.sub(r'^【[^】]{0,30}】\s*', '', e)            # 去开头【编码 名称】
    return re.sub(r'^\d-\d\d(-\d\d-\d\d)?[ 　]*', '', e)  # 去开头裸编码

# 温和可信度加权(data/model_weights.json)。未列模型默认 1.0;Arena 匿名票 0.80。
try:
    _W = dict(json.load(open(p('data', 'model_weights.json'), encoding='utf-8')).get('weights', {}))
except Exception as e:
    print(f'  [warn] 未能加载 model_weights.json,改用等权: {e}'); _W = {}
_W.setdefault('arena', 0.80)
def W(m): return _W.get(m, 1.0)
def wmean(pairs):
    sw = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / sw if sw else 0.0

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
    scn = load_models('step4_overall')   # 自然语言版综合冲击(更拉开)
    xl  = load_models('xilei')            # 细类深评打分
    all_models = sorted((set(emp) | set(pe) | set(sc) | set(scn)) - {'census7', 'official'})
    # 人工挑选的高质量大类/中类简介(逐字摘自各模型概述,覆盖自动抽取版,避免把思考过程当摘要)
    curated = json.load(open(p('data', 'curated_summaries.json'), encoding='utf-8'))
    cur_da = {k: (v.get('summary') if isinstance(v, dict) else v) for k, v in curated.get('da', {}).items()}
    cur_zhong = {k: (v.get('summary') if isinstance(v, dict) else v) for k, v in curated.get('zhong', {}).items()}
    # 大类一句话总结(自然语言版)
    da_sum = {}
    for f in sorted(glob.glob(p('data', 'collected', 'step4_da', '*.json'))):
        for r in json.load(open(f, encoding='utf-8')):
            d = da_sum.setdefault(str(r.get('da')), {'totals': [], 'summary': ''})
            if isinstance(r.get('total'), (int, float)): d['totals'].append(r['total'])
            if r.get('summary') and len(r['summary']) > len(d['summary']): d['summary'] = r['summary']

    out_groups, qa = [], []
    for code, g in groups.items():
        rec = {k: g.get(k) for k in ('code', 'title', 'parent', 'da_title', 'english',
                                     'digital', 'green', 'n_xi', 'n_digital', 'n_green', 'official_sources')}
        rec['细类'] = g.get('细类', [])
        flags = []

        # ---- 步骤2 就业(七普官方优先,其次众议院) ----
        e_rows = [(m, emp[m][code]) for m in emp if code in emp[m]
                  and emp[m][code].get('employment') is not None]
        vals = [r['employment'] for m, r in e_rows if m != 'census7']
        cen = emp.get('census7', {}).get(code)
        official = [r for m, r in e_rows if m != 'census7' and is_official(r)]
        if cen and cen.get('employment') is not None:          # 七普权威数据,直接采用
            rec['employment'] = int(cen['employment']); rec['employment_basis'] = 'census7'
        elif official:
            rec['employment'] = int(statistics.median([r['employment'] for r in official])); rec['employment_basis'] = 'official'
        elif vals:
            rec['employment'] = int(statistics.median(vals)); rec['employment_basis'] = 'provisional'
            flags.append('employment_provisional')
        else:
            rec['employment'] = None; rec['employment_basis'] = 'missing'; flags.append('employment_missing')
        rec['employment_sources'] = [{'model': m, 'value': r.get('employment'),
                                       'source': r.get('source', ''), 'confidence': r.get('confidence', '')}
                                      for m, r in e_rows]
        # 非七普锚定时,标记模型间大幅分歧(供人工核)
        if rec['employment_basis'] != 'census7' and len(vals) > 1 and statistics.mean(vals) \
                and statistics.pstdev(vals) / statistics.mean(vals) > 0.5:
            flags.append('employment_disagreement')

        # ---- 步骤3 薪资(官方分岗位工资优先)/ 学历(模型估计) ----
        pay_rows = [(m, pe[m][code]) for m in pe if code in pe[m] and pe[m][code].get('pay_median') is not None]
        pays = [r['pay_median'] for m, r in pay_rows if m != 'official']
        offpay = pe.get('official', {}).get(code)
        pays_off = [r['pay_median'] for m, r in pay_rows if m != 'official' and is_official(r)]
        if offpay and offpay.get('pay_median') is not None:        # 统计局分岗位工资,直接采用
            rec['pay'] = int(offpay['pay_median']); rec['pay_basis'] = 'official'
        elif pays_off:
            rec['pay'] = int(statistics.median(pays_off)); rec['pay_basis'] = 'official'
        elif pays:
            rec['pay'] = int(statistics.median(pays)); rec['pay_basis'] = 'provisional'; flags.append('pay_provisional')
        else:
            rec['pay'] = None; rec['pay_basis'] = 'missing'
        edus = [pe[m][code]['education'] for m in pe if m != 'official'
                and code in pe[m] and pe[m][code].get('education')]
        rec['education'] = collections.Counter(edus).most_common(1)[0][0] if edus else None
        rec['pay_sources'] = [{'model': m, 'value': r.get('pay_median'), 'source': r.get('pay_source', '')}
                              for m, r in pay_rows]

        # ---- 步骤4 打分:综合冲击优先取自然语言版(更拉开),子维取 JSON 版 ----
        by_model, mean, median, std = {}, {}, {}, {}
        for m in sorted(set(scn) | set(sc)):                 # 综合冲击(sorted 保证 by_model 键序稳定,避免每次跑出无意义大 diff)
            ov = scn[m][code].get('overall') if code in scn.get(m, {}) else None
            if ov is None and code in sc.get(m, {}): ov = sc[m][code].get('overall')
            if ov is not None: by_model.setdefault(m, {})['overall'] = ov
        for d in DIMS[1:]:                                   # 子维只来自 JSON 版
            for m in sc:
                if code in sc[m] and d in sc[m][code]: by_model.setdefault(m, {})[d] = sc[m][code][d]
        for d in DIMS:
            pairs = [(by_model[m][d], W(m)) for m in by_model if d in by_model[m]]
            vs = [v for v, _ in pairs]
            if vs:
                mean[d] = round(wmean(pairs))                      # 加权均值
                median[d] = round(statistics.median(vs))
                std[d] = round(statistics.pstdev(vs), 1) if len(vs) > 1 else 0.0
        rec['dims'] = mean
        rec['dims_median'] = median
        rec['dims_std'] = std
        rec['by_model'] = by_model
        rec['rationales'] = {m: (scn[m][code]['rationale'] if code in scn.get(m, {}) and scn[m][code].get('rationale')
                                 else sc.get(m, {}).get(code, {}).get('rationale', '')) for m in by_model}
        rec['rationales'] = {m: r for m, r in rec['rationales'].items() if r}
        # 中类简介:优先人工挑选(curated zhong),否则回退最长的一条"干净"模型理由
        _cln = [c for c in (clean_rat(r) for r in rec['rationales'].values()) if len(c) >= 12]
        rec['summary'] = cur_zhong.get(code) or (max(_cln, key=len) if _cln else '')
        rec['n_models'] = len([m for m in by_model if 'overall' in by_model[m]])
        rec['std'] = std.get('overall', 0)
        if rec['n_models'] == 0:
            flags.append('score_missing')
        elif std.get('overall', 0) >= 12:
            flags.append('score_disagreement')

        # ---- 细类深评(若已采集):人数=中类官方×归一占比;薪资=中类×档位;等级由分分档 ----
        scored = []
        for x in rec['细类']:
            mrows = [(m, xl[m][x['code']]) for m in xl if x['code'] in xl[m]]
            if not mrows: continue
            rows = [r for _, r in mrows]
            xd = {}
            for dd in DIMS:
                pairs = [(r[dd], W(m)) for m, r in mrows if isinstance(r.get(dd), (int, float))]
                if pairs: xd[dd] = round(wmean(pairs))            # 加权均值
            ov = xd.get('overall')
            x['overall'] = ov; x['dims'] = xd
            ovs = [r['overall'] for r in rows if isinstance(r.get('overall'), (int, float))]
            x['std'] = round(statistics.pstdev(ovs), 1) if len(ovs) > 1 else 0.0
            x['by_model'] = {m: xl[m][x['code']]['overall'] for m in xl if x['code'] in xl[m] and isinstance(xl[m][x['code']].get('overall'), (int, float))}
            # 细类不逐模型存理由文本(体积大头,1.4M字符);分歧由 by_model 分数体现,代表性评价见 eval
            shs = [r['share'] for r in rows if isinstance(r.get('share'), (int, float)) and r['share'] > 0]
            x['_share'] = statistics.median(shs) if shs else 1.0   # 中位数,抗离群 share
            edus = [r['education'] for r in rows if r.get('education')]
            x['education'] = collections.Counter(edus).most_common(1)[0][0] if edus else None
            tiers = [r['pay_tier'] for r in rows if r.get('pay_tier')]
            x['pay_tier'] = collections.Counter(tiers).most_common(1)[0][0] if tiers else None
            evs = [r['eval'] for r in rows if not bad_eval(r.get('eval'))]   # 剔除思考/方法论/批次脚手架等污染候选
            ev = max(evs, key=len) if evs else next((r['eval'] for r in rows if r.get('eval')), '')
            ev = clean_eval_head(ev)                              # 去开头 markdown/编码/横幅装饰
            ev = re.sub(r'\s*[（(]\[.*$', '', ev)                 # 砍掉 ([来源…]) 引用括注(常被截断)
            ev = re.sub(r'\[[^\]\n]{0,40}\]', '', ev)             # 去 [1]/[OECD] 等剩余方括号标记
            ev = re.sub(r'[（(]\s*[)）]', '', ev)                  # 去清空后的空括号
            x['eval'] = re.sub(r'\s{2,}', ' ', ev).strip(' ，,、;；')
            x['n_models'] = len(x['by_model'])
            if ov is not None:
                x['level'] = LEVEL(ov); scored.append(x)
        if scored:
            tot = sum(x['_share'] for x in scored) or 1
            for x in scored:
                if rec.get('employment'): x['employment'] = int(rec['employment'] * x['_share'] / tot)
                if rec.get('pay'): x['pay'] = int(rec['pay'] * PAY_TIER.get(x['pay_tier'], 1.0))
                x.pop('_share', None)
        rec['xilei_scored'] = len(scored)

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
            'version': 'v1.0',
            'taxonomy': occ['meta'],
            'models': all_models, 'n_models': len(all_models),
            'xilei_models': sorted(xl), 'weights': _W,
            'unit': '中类(79)', 'dims': DIMS,
            'disclaimer': '分类与S/L标注=职业分类大典2022;就业=第七次全国人口普查(年鉴表4-7);薪资=国家统计局2023分岗位+分行业平均工资;学历=AI估计;AI冲击=多模型集成估算(细类层13个模型+Arena匿名双盲补充票,按温和可信度加权)。仅供参考,不代表官方结论。',
        },
        'categories': occ['categories'],
        'da_summary': {k: {'overall': round(statistics.mean(v['totals'])) if v['totals'] else None,
                           'summary': cur_da.get(k) or v['summary']} for k, v in da_sum.items()},
        'groups': out_groups,
    }
    json.dump(agg, open(p('data', 'aggregated.cn.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 同时输出站点可直接 <script> 加载的数据(双击 HTML 也能渲染,免本地服务器)
    os.makedirs(p('site'), exist_ok=True)
    data_js = 'window.DATA=' + json.dumps(agg, ensure_ascii=False) + ';'
    open(p('site', 'data.cn.js'), 'w', encoding='utf-8').write(data_js)
    # 自包含单文件:把数据内联进 HTML,免相对路径(供 WordPress 等自托管直接上传;GitHub Pages 仍用双文件 index.html)
    idx = open(p('site', 'index.html'), encoding='utf-8').read()
    marker = '<script src="data.cn.js"></script>'
    if marker in idx:
        inline = '<script>' + data_js.replace('</', '<\\/') + '</script>'  # 转义 </ 防数据里万一出现 </script> 提前闭合
        open(p('site', 'index.standalone.html'), 'w', encoding='utf-8').write(idx.replace(marker, inline, 1))
        print('✅ index.standalone.html:数据已内联,免路径自托管版')
    else:
        print('⚠ 未在 index.html 找到 data.cn.js 引用,跳过自包含单文件(检查加载方式是否变了)')

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
