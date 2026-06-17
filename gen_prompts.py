#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 AI 众议院各子模型、各阶段的【独立可投喂】提示词文件。
每个文件 = 一个可直接丢给对应网页 AI 的完整提示词(无外层代码围栏)。
输出:
  docs/zhongyiyuan/prompts/<key>/step1.md ... step4.md   (11 主力 × 4 阶段)
  docs/zhongyiyuan/prompts/review/<reviewer>.md           (5 评议员)
  docs/zhongyiyuan/prompts/README.md                      (用法)
改分工/清单后重跑即可刷新。
"""
import json, os, shutil
ROOT = os.path.dirname(os.path.abspath(__file__))
occ = json.load(open(os.path.join(ROOT, 'data', 'occupations.cn.json'), encoding='utf-8'))
G = occ['groups']
LIST = '\n'.join(f"{g['code']}  {g['title']}  【{g['da_title']}】"
                 + ('  [含S数字职业]' if g['digital'] else '') + ('  [含L绿色职业]' if g['green'] else '')
                 for g in G)
N = len(G)
import collections as _c
_da = _c.OrderedDict()
for g in G:
    _da.setdefault((g['parent'], g['da_title']), []).append(g)
LIST_BY_DA = '\n'.join(
    f"## 大类{dac} {dat}\n" + '\n'.join(
        f"  {x['code']} {x['title']}" + ('  [含数字职业]' if x['digital'] else '') for x in gs)
    for (dac, dat), gs in _da.items())
ANCHOR = "AI 时代各岗位冲击图谱(中国版)数据采集"

ROSTER = [
 ("wenxin","文心一言(m码牛模式)","部委与政策原文。主攻人社部、国家统计局、发改委、工信部、教育部的公报/国家标准/政策文件,给出文件名与可核查链接。","结合中国政策、行业准入与监管,判断其对落地速度与护城河的影响。"),
 ("qwen","通义千问 Qwen3.7max(任务助理)","行业与产业。主攻行业协会报告、白皮书、上市公司年报、招聘平台官方报告,反映岗位真实产业样态与规模。","结合行业真实 AI 部署进度(是真用还是观望),校准落地速度。"),
 ("zhipu","智谱清言 GLM5.1(研究模式)","学术统计。主攻 CNKI、劳动经济与就业研究文献中的职业就业与薪资测算,给出文献出处。","从学术对自动化可行性的研究判断任务自动化的边界。"),
 ("yuanbao","腾讯元宝(Hy3 preview)","行业协会与地方。主攻各行业协会、地方统计局、专业社群中的一手数据,补充国家级之外的官方与准官方来源。","结合行业内部与一线实操,判断真实可替代部分。"),
 ("gpt","GPT(深度研究)","国际官方对照。主攻 ILO、OECD、世界银行等对华就业/职业统计与英文一手报告,做跨语言交叉印证。","参考国际 AI 能力前沿与海外同类岗位的演变趋势。"),
 ("gemini","Gemini 3.1 Pro(深度研究)","深度综述与查漏。系统检索多来源、交叉核对、补齐其他模型遗漏的官方资料,标注来源可靠性。","做六维之间的一致性校验,避免单点高估或低估。"),
 ("deepseek","DeepSeek(专家模式)","口径核对。专查不同来源的统计年份、单位、口径差异(如城镇单位 vs 全社会就业),给出可比性说明。","从第一性原理审视任务可自动化的真实边界与前提条件。"),
 ("doubao","豆包(深入研究)","二次核对。主攻权威媒体、民生报道中引用的官方数据,回溯其原始官方出处并核验。","结合一线从业者与社区的真实感受,校准 AI 增强的体感幅度。"),
 ("grok","Grok 4.3 fast","数据质疑。专门标出哪些流传数字不可靠、来源存疑、相互矛盾,给出质疑理由,宁缺毋滥。","警惕炒作高估,标出被夸大但实际尚未落地的环节,压低虚高分。"),
 ("kimi","Kimi 2.6(thinking)","长文档精读。主攻统计年鉴、人口普查年鉴、行业蓝皮书等长 PDF 的精确抽取,给出页/表出处。","结合长篇研究报告的细节,补强对增强与落地的判断。"),
 ("claude","Claude(Opus · Extended Thinking)","结构化汇编与最终交叉核对。把各来源对齐到统一口径,标注冲突与置信度。","对六维做结构化权衡,确保同一大类内部相对关系自洽。"),
]

def footer(research=True):
    base = (f"""【输出铁律(务必遵守)】
- 只输出 JSON 数组本身。不要研究报告、前言、结语、解释、表格或 Markdown 标题。
- 严格使用上面给定的英文字段名,不要改成中文键名。
- 必须覆盖本清单全部 {N} 个中类,逐项不漏、顺序一致。
- 若一条消息放不下:先输出前 40 项,等我回复"继续"后再输出其余 {N-40} 项。不得省略、不得用省略号占位、不得编造。
- JSON 内的换行与引号必须转义,不要出现裸控制字符,不要尾随逗号。
- 中性、专业、直接,不使用破折号。""")
    if research:
        base += "\n- 官方优先、有据可查;查不到就写 null 或在 note 标注,绝不编造数字或链接。"
    return base

def head(name, step, total, title):
    return f"【AI众议院 · {name} · 步骤{step}/{total}:{title}】\n"

def step1(name, angle):
    return head(name,1,4,"职业分类校验与扩源(考据,官方锚定)") + f"""
【锚点主题】{ANCHOR}:职业分类校验与扩源
【意图】考据/检索(官方锚定,纯客观);独立盲测,以官方来源为准交叉核对。
【你的专属切入角度】{angle}
【基准】《中华人民共和国职业分类大典(2022年版)》(人社部、市场监管总局、国家统计局):8大类/79中类/449小类/1636细类,官方标注数字职业(S)97个、绿色职业(L)133个。

【中类清单(共{N},全部处理)】
{LIST}

【任务】对每个中类:1) 校验编码与名称是否与官方一致(以大典为准);2) 指出其下哪些细类属数字职业(S)/绿色职业(L);3) 用你的专属领域尽量多地补充官方级来源(名称+可核查链接);4) 给规范英文名;5) 查不到如实标注。

【字段(英文键)】code, title_official, title_match(bool), english, digital_xilei(数组), green_xilei(数组), sources(数组,每项{{name,url,type}}), confidence(high/medium/low), evidence(事实/推断/不确定), note
【示例一项】
{{"code":"2-02","title_official":"工程技术人员","title_match":true,"english":"Engineering Technicians","digital_xilei":["2-02-30-01 人工智能工程技术人员"],"green_xilei":[],"sources":[{{"name":"职业分类大典(2022年版)","url":"https://www.mohrss.gov.cn/...","type":"official"}}],"confidence":"high","evidence":"事实","note":""}}

{footer(True)}
"""

def step2(name, angle):
    return head(name,2,4,"就业人数(考据,官方锚定)") + f"""
【锚点主题】{ANCHOR}:就业人数
【意图】考据/检索(官方锚定);独立盲测。
【你的专属切入角度】{angle}
【任务】为每个中类给出全国就业人数(单位:人,整数)。优先官方:第七次全国人口普查 / 中国人口普查年鉴-2020(分职业)、中国统计年鉴、人社部公报、行业统计。注明数据年份与统计口径。
重要:employment 必须尽量给数值。若能查到精确官方值,evidence 标 official;若取不到精确值,请基于官方口径(如该大类总量、行业就业结构、相近年份数据)给出**合理估计**,evidence 标 estimate,并在 note 写明估计依据;只有完全无任何依据时才写 null。不要为了"严谨"而大面积留空,也不要把估计值谎标为 official。

【中类清单(共{N},全部处理)】
{LIST}

【字段(英文键)】code, employment(整数或null), year, caliber(口径), source, source_url, evidence(official/estimate/unknown), confidence
【示例一项】
{{"code":"4-04","employment":8000000,"year":2020,"caliber":"全社会就业(七普分职业)","source":"中国人口普查年鉴-2020","source_url":"https://www.stats.gov.cn/...","evidence":"official","confidence":"high"}}

{footer(True)}
"""

def step3(name, angle):
    return head(name,3,4,"薪资 + 学历(考据,官方锚定)") + f"""
【锚点主题】{ANCHOR}:薪资与学历
【意图】考据/检索(官方锚定);独立盲测。
【你的专属切入角度】{angle}
【任务】为每个中类给出:1) 年薪中位数(元/年,整数);2) 典型入职学历(博士/硕士/本科/大专/高中/初中)。
薪资优先用国家统计局"分行业城镇单位就业人员平均工资"映射(注明对应行业门类与年份)或其他官方薪酬调查;若取不到精确值,基于官方口径给**合理估计**并把 confidence 标 low、在来源里写明"估计"。学历优先职业分类大典或国家职业标准。pay_median 尽量给数值,只有完全无依据才 null;不要大面积留空。

【中类清单(共{N},全部处理)】
{LIST}

【字段(英文键)】code, pay_median(整数或null), pay_year, pay_source, pay_source_url, education, edu_source, confidence
【示例一项】
{{"code":"2-06","pay_median":200000,"pay_year":2023,"pay_source":"国家统计局2023分行业平均工资·金融业(映射)","pay_source_url":"https://www.stats.gov.cn/...","education":"本科","edu_source":"职业分类大典(2022年版)","confidence":"medium"}}

{footer(True)}
"""

def step4(name, lens):
    return head(name,4,4,"AI 综合冲击打分(自然语言版)") + f"""
【锚点主题】{ANCHOR}:岗位 AI 综合冲击打分
【意图】主观研判;独立盲测,你的判断会与其他模型集成(取均值/中位数并展示分歧度)。

【你要做的事】
用正常的中文,先给 8 个大类各打一个"AI 综合冲击"总分(0-100)加一句话总结,再逐个给 {N} 个中类打分(0-100)加简短理由。综合冲击 = 该职业在当前及可见近未来被 AI 整体重塑的程度(高分=被重塑、生产力剧变,不等于失业)。

【最重要:务必拉开差距,别都挤在中间】
请充分使用 0-100 全程,敢打极端:
- 几乎全在电脑上、信息处理为主、可远程(编程、数据分析、文案、客服、录入、财会、设计、翻译)→ 80-100;
- 重体力 / 不可预测现场 / 强人际信任 / 线下操作为主(种地、建筑、采矿、护理、餐饮、美发、家政、安保)→ 5-25;
- 真正一半一半的才给 40-70。
同一个大类内部,不同中类也要分出明显高低。宁可极端、敢下判断,不要保守居中、不要和稀泥。

【你的专属视角(只补强判断)】{lens}

【打分对象(8 大类 / {N} 中类)】
{LIST_BY_DA}

【输出怎么写】
按大类组织,正常说话即可,但要便于汇总:
- 每个大类一个小标题并给总分,例如:
  ## 大类2 专业技术人员 — 总冲击 65
  (一句话:这个大类为什么整体偏高或偏低)
- 该大类下每个中类一行,理由一两句,结尾用粗体明确给分,例如:
  - 2-02 工程技术人员:设计、编码、仿真大量被 AI 接管,现场调试与担责仍需人。**综合冲击 75**
  - 2-03 农业技术人员:田间实操与本地经验为主,AI 多在辅助决策。**综合冲击 35**

【硬要求】
- 覆盖全部 8 大类、{N} 个中类,一个不漏,编码写对。
- 每个中类结尾必须有"**综合冲击 XX**"(XX 为 0-100 整数);每个大类标题必须有"总冲击 XX"。
- 每个中类一两句话即可,不要写成长篇报告。
- 中性、专业、直接,不使用破折号。
"""

PROMPTS = os.path.join(ROOT, 'docs', 'zhongyiyuan', 'prompts')
# 重建目录结构(按步骤分)
if os.path.isdir(PROMPTS): shutil.rmtree(PROMPTS)
for sub in ('step1', 'step2', 'step3', 'step4', 'review'):
    os.makedirs(os.path.join(PROMPTS, sub), exist_ok=True)
for key, name, angle, lens in ROSTER:
    open(os.path.join(PROMPTS, 'step1', key + '.md'), 'w', encoding='utf-8').write(step1(name, angle))
    open(os.path.join(PROMPTS, 'step2', key + '.md'), 'w', encoding='utf-8').write(step2(name, angle))
    open(os.path.join(PROMPTS, 'step3', key + '.md'), 'w', encoding='utf-8').write(step3(name, angle))
    open(os.path.join(PROMPTS, 'step4', key + '.md'), 'w', encoding='utf-8').write(step4(name, lens))

REVIEW = [
 ("nemotron-3-super-120b-a12b","盲点扫描","11个主力是否集体遗漏了某些重要官方来源或职业?列出被忽略的视角与应补的官方资料。"),
 ("qwq-32b","反方代言","针对多数派的打分,给出尽可能扎实的反面论据;若少数派更有理,为其补强。"),
 ("llama-3.2-90b-vision-instruct","信息源补位","补充主流模型未见的非主流/小众官方与准官方资料(地方、行业、英文小语种)。"),
 ("gpt-oss-120b","数值合理性核查","核查就业/薪资/打分中的异常值与口径冲突,标出最可疑的若干项及理由。"),
 ("Mistral-Large","一致性与可比性审查","审查跨中类打分是否自洽(同类内部相对关系、量纲一致性),指出矛盾点。"),
]
rd = os.path.join(PROMPTS, 'review'); os.makedirs(rd, exist_ok=True)
for key, role, task in REVIEW:
    body = f"""【AI众议院评议团 · {key} · {role}】

【锚点主题】{ANCHOR}:对已采集数据的事后审查
【意图】事后审查(不重新采集);独立盲测。11个主力已完成步骤1-4并由 aggregate.py 聚合。

【已聚合摘要(粘贴 data/aggregated.cn.json 关键字段或 data/qa_report.md 内容)】
{{{{在此粘贴}}}}

【你的专属任务】{task}

【字段(英文键)】code(相关中类编码或 GLOBAL), issue, suggestion, severity(high/medium/low), evidence
【示例一项】
{{"code":"2-02","issue":"就业人数与七普口径不符","suggestion":"改用人口普查年鉴-2020表X","severity":"medium","evidence":"..."}}

{footer(True)}
"""
    open(os.path.join(rd, key + '.md'), 'w', encoding='utf-8').write(body)

readme = f"""# 众议院提示词(独立可投喂)

每个文件 = 一个**可直接丢给对应网页 AI** 的完整提示词。结构**按步骤分**:`prompts/step1/<模型>.md` … `prompts/step4/<模型>.md` + `prompts/review/<评议员>.md`。

## 用法
1. 做某一步时,打开该步目录(如 `step2/`),把里面每个 `<模型>.md` 投喂给对应模型;收到回复后存为 `data/collected/step{{n}}_*/<模型键>.json`(step1→step1_taxonomy、step2→step2_employment、step3→step3_pay_edu、step4→step4_scoring)。
2. 全部模型回填后运行:`python tools/ingest.py <step> <你的原始返回目录>`(容错救回 + 校验),再 `python aggregate.py`。
3. 站点 `site/index.html` 自动更新。

## 注意(根据首轮经验)
- **不要把模型回答页另存为网页**(会变成 HTML/UTF-16,无法解析);请复制**纯文本/JSON**。
- 若模型输出被**截断**(算力受限):回复"继续"让它接着写,或分两条(前40 / 后{N-40})。
- 深度研究模式容易输出**长报告而非 JSON**:提示词已要求"只输出 JSON";若它仍给报告,追加一句"现在只输出 JSON 数组"。
- 字段名必须用**英文键**(首轮有模型用了中文键);`tools/ingest.py` 已能容错映射,但仍以英文键为准。

## 模型键
{' · '.join('`'+k+'`' for k,_,_,_ in ROSTER)}
评议员(免费API):{' · '.join('`'+k+'`' for k,_,_ in REVIEW)}
"""
open(os.path.join(PROMPTS, 'README.md'), 'w', encoding='utf-8').write(readme)

print(f"已生成 {len(ROSTER)} 模型 × 4 阶段 = {len(ROSTER)*4} 个独立提示词 + {len(REVIEW)} 评议员 + README")
print("目录:", PROMPTS)

# ============ 细类工程(打包 · 分层 · 加长版)============
# 已采集首批(11模型,旧提示词):原始返回存于 data/collected/xilei_raw/,本轮不再重复生成
PRI = ['4-04', '3-01', '2-06', '2-02', '2-08', '2-07', '4-01', '6-29', '5-01', '4-03']
PRI_SET = set(PRI)
GMAP = {g['code']: g for g in G}
import math as _m
# 中类级聚合(用于判定重点/长尾:高冲击 dims.overall>=55 或 就业Top15)
try:
    AGG = json.load(open(os.path.join(ROOT, 'data', 'aggregated.cn.json'), encoding='utf-8'))
    AGG_G = {g['code']: g for g in (AGG.get('groups') or AGG)}
except Exception:
    AGG_G = {}
KEY_EMP_THR = 4919730
def is_key_zl(code):
    g = AGG_G.get(code)
    if not g: return False
    ov = (g.get('dims') or {}).get('overall')
    emp = g.get('employment') or 0
    return (ov is not None and ov >= 55) or emp >= KEY_EMP_THR

# 新成员(全新专属领地;先中档试用,出分后再定权重)
MIMO = ("mimo", "小米MiMo(mimo-v2.5pro)",
        "移动互联网与智能终端生态。主攻智能手机/IoT/车机/可穿戴等端侧 AI 应用、App 与小程序生态,以及由此催生或改写的新职业样态。",
        "结合端侧 AI 与消费级智能硬件的真实普及速度,校准落地速度与数字化程度。")
MINIMAX = ("minimax", "MiniMax-M3(思考)",
           "多智能体与长流程任务。主攻 Agent/工作流自动化在真实长链条业务(客服、运营、内容生产、流程审批)中的端到端落地证据,评估其接管整段流程而非单点任务的能力。",
           "以多智能体能否接管完整工作流为尺度,判断任务自动化的真实上限与护城河。")
ROSTER_XI = ROSTER + [MIMO, MINIMAX]                       # 重点中类:全 13 模型
_CLEAN = {'gpt', 'deepseek', 'grok', 'kimi', 'wenxin', 'zhipu', 'qwen', 'claude', 'mimo', 'minimax'}
LEAN_XI = [m for m in ROSTER_XI if m[0] in _CLEAN]         # 长尾中类:精简 10(去 gemini/doubao/yuanbao)

TARGET, CAP = 70, 80    # 每条目标~70细类;合并多个小中类上限~80;单中类>70自动均分分批
def even_chunks(xs, target):
    k = max(1, _m.ceil(len(xs) / target)); sz = _m.ceil(len(xs) / k)
    return [xs[i:i+sz] for i in range(0, len(xs), sz)]
def pack_da(mids):
    """把同一(大类,层级)内的中类打包成若干 bundle;bundle=[(g,细类切片,批序,批数),...]"""
    bundles, cur, tot = [], [], 0
    for g in mids:
        xs = g['细类']; n = len(xs)
        if n > TARGET:
            if cur: bundles.append(cur); cur, tot = [], 0
            chs = even_chunks(xs, TARGET)
            for bi, ch in enumerate(chs, 1): bundles.append([(g, ch, bi, len(chs))])
            continue
        if cur and tot + n > CAP: bundles.append(cur); cur, tot = [], 0
        cur.append((g, xs, 1, 1)); tot += n
    if cur: bundles.append(cur)
    return bundles

def xilei_prompt(name, lens, bundle, dac, dat, tag):
    nxi = sum(len(xs) for _, xs, _, _ in bundle)
    head = f"【AI众议院 · {name} · 细类深评打分 · 大类{dac} {dat} · {tag}】\n"
    blocks = []
    for g, xs, bi, bn in bundle:
        sub = '\n'.join(f"    {x['code']} {x['title']}" + ('  [数字S]' if x['digital'] else '') + ('  [绿色L]' if x['green'] else '') for x in xs)
        blocks.append(f"◇ 中类 {g['code']} {g['title']}" + (f"(本中类第{bi}/{bn}批)" if bn > 1 else "") + f",共{len(xs)}个细类:\n{sub}")
    mm = "\n【你支持团队/多智能体】可选启用 Agent 团队模式分工检索与交叉核对(不强制),但最终仍按统一尾行格式输出。" if name.startswith('MiniMax') else ""
    return head + f"""
【锚点主题】AI 时代各岗位冲击图谱(中国版):中类下细类(具体职业)的深度评估与打分
【意图】主观研判 + 证据检索;独立盲测,你的判断会与其他模型集成(取均值/中位数并展示分歧度)。
【你的专属视角(只补强判断,不必面面俱到)】{lens}{mm}
【背景与口径】官方数据只到中类:细类没有官方人数/薪资。所以人数请估"该细类在其所属中类内部的就业占比%"(同一中类的细类占比之和≈100,不同中类各自归一);薪资给"相对本中类的高/中/低档";AI 冲击与文字评价是本轮重点。
【尽量多查证据】在你的视角范围内结合真实行业落地、招聘需求、技术成熟度等可核查信息判断(可在评价里极简带一句依据),但不要堆砌长篇,把篇幅留给覆盖全部细类。

【本批覆盖 {len(bundle)} 个中类 / 共 {nxi} 个细类,逐项不漏】
{chr(10).join(blocks)}

【对每个细类:先 1-2 句自然语言评价,再给一行结构化尾行】
评价(务必精炼,1-2 句、约40-80字):点出 ①AI 最受冲击/已落地处 或 ②人仍不可替代处 即可,不必三点都写满。禁止写章节、摘要、总述、表格或长篇报告。
尾行(务必逐字照此格式,便于自动汇总):
〔编码 名称〕综合NN 自动化NN 增强NN 数字NN 护城河NN 落地NN ┃ 占比N% ┃ 学历X ┃ 薪资X ┃ 等级X
说明:六维均 0-100 整数,务必拉开差距(敢打极端、别挤中间);占比=该细类在其所属中类内部的就业百分比;学历∈{{博士,硕士,本科,大专,高中,初中}};薪资∈{{高,中,低}}(相对本中类);等级∈{{极高,高,中,低,极低}}(对应综合冲击 81+/61-80/41-60/21-40/0-20)。

【示例】
人工智能工程技术人员:模型与算法本身即产出,设计、编码、调参高度可被 AI 接管;系统集成与工程担责仍需人。
〔2-02-30-01 人工智能工程技术人员〕综合88 自动化70 增强96 数字98 护城河28 落地85 ┃ 占比6% ┃ 学历硕士 ┃ 薪资高 ┃ 等级极高

【一次性完整输出(最重要)】本批共 {nxi} 个细类,请在这一条回复里一次性给全 {nxi} 行尾行,一行都不能少。禁止中途停下等我说"继续";禁止"由于篇幅""接下来我将""其余略""……"等拖延或省略占位;禁止编造。你的单次输出容量足以容纳全部 {nxi} 条,只要把每条评价压到 1-2 句即可一次写完。写完请自查尾行数量是否等于 {nxi},不足就补齐后再发。
【证据须针对中国大陆】判断与举证一律基于中国大陆的官方/行业资料,或国外机构针对中国大陆的专门分析;不得把对美国、欧洲等地岗位的研究直接套用到中国大陆。
【硬要求】① 覆盖本批全部 {nxi} 个细类、编码逐字写对 ② 充分拉开分数(敢打极端) ③ 每个中类内部占比之和≈100 ④ 评价精炼 1-2 句 ⑤ 不要 JSON、不使用破折号。"""

xd = os.path.join(PROMPTS, 'xilei')
if os.path.isdir(xd): shutil.rmtree(xd)
rem_by_da = _c.OrderedDict()
for g in G:
    if g['code'] in PRI_SET or len(g.get('细类', [])) == 0: continue
    rem_by_da.setdefault((g['parent'], g['da_title']), []).append(g)
plan, nfiles, nbundles, npastes = [], 0, 0, 0
for (dac, dat), gs in rem_by_da.items():
    key_mids = [g for g in gs if is_key_zl(g['code'])]
    tail_mids = [g for g in gs if not is_key_zl(g['code'])]
    for tier, mids, roster in (('重点', key_mids, ROSTER_XI), ('长尾', tail_mids, LEAN_XI)):
        if not mids: continue
        for idx, bundle in enumerate(pack_da(mids), 1):
            nbundles += 1; npastes += len(roster)
            folder = os.path.join(xd, f"大类{dac}", f"{tier}-{idx:02d}"); os.makedirs(folder, exist_ok=True)
            tag = f"{tier}批{idx}"
            for key, nm, angle, lens in roster:
                open(os.path.join(folder, key + '.md'), 'w', encoding='utf-8').write(xilei_prompt(nm, lens, bundle, dac, dat, tag)); nfiles += 1
            plan.append((dac, dat, tier, idx, len(roster), [(g['code'], g['title'], len(xs), bi, bn) for g, xs, bi, bn in bundle]))

# 进度追踪表
prog = ["# 细类采集进度追踪(剩余 69 中类)", "",
        f"> 重点中类(高冲击或就业Top15)用 **全 13 模型**;长尾中类用 **精简 10 强**(去 gemini深研/豆包/元宝)。",
        f"> 共 **{nbundles}** 个批次、**{nfiles}** 个提示词文件、约 **{npastes}** 次粘贴。每个批次目录里有几个 `.md` 就投喂几个模型,回复原文按模型存好,跑 `tools/parse_xilei.py` 解析。", "",
        "## 已采集(首批10重点中类 · 11模型 · 原始存于 data/collected/xilei_raw/)",
        "`" + "` `".join(PRI) + "`  ←  这10个还缺 mimo/minimax,可在收尾时补;其余无需重采。", "",
        "## 待采集批次"]
_cur_da = None
for dac, dat, tier, idx, nmodel, items in plan:
    if dac != _cur_da:
        prog.append(f"\n### 大类{dac} {dat}"); _cur_da = dac
    cov = '; '.join(f"{c} {t}" + (f"(第{bi}/{bn}批)" if bn > 1 else "") + f"·{n}细类" for c, t, n, bi, bn in items)
    prog.append(f"- [ ] **{tier}-{idx:02d}**(`大类{dac}/{tier}-{idx:02d}/`,{nmodel}模型):{cov}")
open(os.path.join(xd, 'PROGRESS.md'), 'w', encoding='utf-8').write('\n'.join(prog) + '\n')

xreadme = f"""# 细类深评打分提示词(剩余 69 中类 · 打包分层版)

每个文件 = 一个**可直接投喂**的提示词,一条覆盖**多个小中类或一个大中类的一批**(约 70 个细类)以减少粘贴次数。
结构:`xilei/大类<码>/<重点|长尾>-<批号>/<模型>.md`。**目录里有几个模型文件就投喂几个**(重点=13,长尾=10)。

## 分层(决定每批投喂几个模型)
- **重点中类**(高冲击 dims.overall≥55 或 就业 Top15):全 **13** 模型(含 gemini/豆包/元宝/mimo/minimax)。
- **长尾中类**:精简 **10** 强({' · '.join(k for k,_,_,_ in LEAN_XI)});去掉爱写长报告/乱编码的 gemini深研、豆包、元宝。

## 新成员
- `mimo` 小米MiMo(mimo-v2.5pro)·端侧/终端生态视角
- `minimax` MiniMax-M3(思考)·多智能体长流程视角(可选 Agent 团队模式)
- 两者先中档试用,出分后再定可信度权重。

## 用法
1. 看 `PROGRESS.md` 挑一个未完成批次,打开其目录,把每个 `<模型>.md` 投喂给对应模型。
2. 回复(自然语言评价 + 尾行)按模型存为原始文本,文件名用模型键(如 `gpt.txt`/`minimax.txt`),放进一个目录。
3. `python tools/parse_xilei.py <该目录>` 解析 → `data/collected/xilei/<模型>.json`(多目录可多次跑,自动按编码合并)。
4. 全部 1636 细类采完后再统一 `aggregate.py`(温和加权)并上线,本轮不急于聚合。

共 {nbundles} 批 / {nfiles} 文件 / 约 {npastes} 次粘贴。
"""
open(os.path.join(xd, 'README.md'), 'w', encoding='utf-8').write(xreadme)
print(f"已生成细类提示词 {nfiles} 个:{nbundles} 批(重点13模型/长尾10模型),约 {npastes} 次粘贴 -> {xd}")
print("进度表:", os.path.join(xd, 'PROGRESS.md'))

# ============ 查漏补缺(gap-fill)+ Arena 双盲补充 ============
import glob as _glob
NAME_OF = {k: nm for k, nm, a, l in ROSTER_XI}
LENS_OF = {k: l for k, nm, a, l in ROSTER_XI}
TITLE_XI = {x['code']: x for g in G for x in g.get('细类', [])}
ANTILAZY = ('【一次性完整输出(最重要)】本批共 {n} 个细类,请在这一条回复里一次性给全 {n} 行尾行,一行都不能少。'
            '禁止中途停下等我说"继续";禁止"由于篇幅""接下来我将""其余略""……"等拖延或省略占位;禁止编造。'
            '你的单次输出容量足以容纳全部 {n} 条,把每条评价压到 1 句即可一次写完。写完请自查尾行数量是否等于 {n},不足就补齐再发。')
CHINA = ('【证据须针对中国大陆】判断与举证一律基于中国大陆的官方/行业资料,或国外机构针对中国大陆的专门分析;'
         '不得把对美国、欧洲等地岗位的研究直接套用到中国大陆。')
TAILSPEC = ('〔编码 名称〕综合NN 自动化NN 增强NN 数字NN 护城河NN 落地NN ┃ 占比N% ┃ 学历X ┃ 薪资X ┃ 等级X\n'
            '(六维0-100整数、务必拉开差距;占比=该细类在其所属中类内部的就业百分比;学历∈博士/硕士/本科/大专/高中/初中;'
            '薪资∈高/中/低;等级∈极高/高/中/低/极低=综合81+/61-80/41-60/21-40/0-20)')

def _blocks(groups):
    out = []
    for zl, codes in groups:
        zt = GMAP[zl]['title']
        sub = '\n'.join(f"    {c} {TITLE_XI[c]['title']}" + (' [数字S]' if TITLE_XI[c]['digital'] else '') + (' [绿色L]' if TITLE_XI[c]['green'] else '') for c in codes if c in TITLE_XI)
        out.append(f"◇ 中类 {zl} {zt}({len(codes)}个):\n{sub}")
    return '\n'.join(out)

def gapfill_prompt(name, lens, groups):
    n = sum(len(cs) for _, cs in groups)
    mm = "\n【你支持团队/多智能体】可选启用 Agent 团队模式,但仍按统一尾行一次性输出。" if name.startswith('MiniMax') else ""
    return f"""【AI众议院 · {name} · 细类深评打分 · 查漏补缺批(共{n}个)】

【为什么再次发给你】上一轮你这部分只给了一部分就停下了。下面是你尚未评分的细类,这一次请一口气全部补齐。
【你的专属视角(只补强判断,不必面面俱到)】{lens}{mm}
【口径】人数给"该细类在其所属中类内部的就业占比%"(同一中类内可与你已给的合计≈100);薪资给相对本中类的高/中/低档。
{CHINA}

【待补细类(共 {n} 个,逐项不漏)】
{_blocks(groups)}

【对每个细类:1 句评价 + 一行尾行】
{TAILSPEC}

{ANTILAZY.format(n=n)}
不要 JSON、不使用破折号。"""

def arena_prompt(groups):
    n = sum(len(cs) for _, cs in groups)
    return f"""你是一位研究"AI 对中国大陆各职业冲击"的资深专家。请对下列中国《职业分类大典(2022)》细类职业逐个打分。

【背景】官方数据只到中类,细类的人数/薪资无官方源:人数请估"该细类在其所属中类内部的就业占比%"(同一中类内合计≈100);薪资给相对本中类的高/中/低档。六维含义:综合冲击/任务自动化/AI增强/数字化程度/技能护城河/行业落地速度,均 0-100。
{CHINA}

【细类清单(共 {n} 个,逐项不漏)】
{_blocks(groups)}

【对每个细类:1 句评价 + 一行尾行】
{TAILSPEC}

{ANTILAZY.format(n=n)}
请自包含作答(不要反问、不要要求更多上下文),不要 JSON、不使用破折号。"""

def _pack_codes(codes, size=70):
    return [codes[i:i+size] for i in range(0, len(codes), size)]

def _regroup(chunk):
    bz = _c.OrderedDict()
    for c in chunk: bz.setdefault('-'.join(c.split('-')[:2]), []).append(c)
    return list(bz.items())

# --- 查漏补缺:读 data/collected/xilei_gaps/<model>.json ---
gapdir = os.path.join(ROOT, 'data', 'collected', 'xilei_gaps')
gxd = os.path.join(PROMPTS, 'xilei_gaps')
if os.path.isdir(gxd): shutil.rmtree(gxd)
gap_files, gap_rows = 0, []
if os.path.isdir(gapdir):
    for fp in sorted(_glob.glob(os.path.join(gapdir, '*.json'))):
        key = os.path.splitext(os.path.basename(fp))[0]
        if key == 'claude' or key not in NAME_OF: continue       # claude 由我自采,不投喂
        codes = [it['code'] for it in json.load(open(fp, encoding='utf-8')) if it['code'] in TITLE_XI]
        seen = list(dict.fromkeys(codes))
        if not seen: continue
        d = os.path.join(gxd, key); os.makedirs(d, exist_ok=True)
        chunks = _pack_codes(seen, 70)
        for bi, ch in enumerate(chunks, 1):
            open(os.path.join(d, f'g{bi:02d}.md'), 'w', encoding='utf-8').write(gapfill_prompt(NAME_OF[key], LENS_OF[key], _regroup(ch)))
            gap_files += 1
        gap_rows.append((key, len(seen), len(chunks)))
    greadme = ["# 查漏补缺提示词(把各模型上一轮偷懒/截断漏掉的细类补齐)", "",
               "上一轮许多非深度研究模式的模型只输出一部分就停下等「继续」。这里按模型汇总它们漏掉的细类,",
               "用强化版「一次性完整输出」提示词重新投喂。强调:禁止「继续」、一口气写全。", "",
               "结构:`xilei_gaps/<模型>/g01.md ...`。每个模型把自己目录下的每条投喂给它本人,回复存为 `<模型>.txt` 再跑 `tools/parse_xilei.py`(按编码自动并入,不会覆盖已有)。", "",
               "## 各模型待补量"]
    for key, n, nb in sorted(gap_rows, key=lambda r: -r[1]):
        greadme.append(f"- **{key}**:待补 {n} 个,分 {nb} 批")
    greadme.append("\n> `claude` 的那份(约1200+)由本系统作者模型(我)自行产出,不在此目录。")
    open(os.path.join(gxd, 'README.md'), 'w', encoding='utf-8').write('\n'.join(greadme) + '\n')
    print(f"已生成查漏补缺提示词 {gap_files} 个,覆盖 {len(gap_rows)} 个模型 -> {gxd}")

# --- Arena 双盲:对剩余69中类生成中性匿名提示词(一批可投喂 lmarena,收两个匿名模型的票) ---
axd = os.path.join(PROMPTS, 'xilei_arena')
if os.path.isdir(axd): shutil.rmtree(axd)
arena_files = 0
for (dac, dat), gs in rem_by_da.items():
    mids = [g for g in gs]
    for idx, bundle in enumerate(pack_da(mids), 1):
        groups = [(g['code'], [x['code'] for x in xs]) for g, xs, bi, bn in bundle]
        d = os.path.join(axd, f"大类{dac}"); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, f"a{idx:02d}.md"), 'w', encoding='utf-8').write(arena_prompt(groups))
        arena_files += 1
areadme = ("# Arena 双盲补充数据(lmarena 随机对战)\n\n"
           "把 `xilei_arena/大类N/aNN.md` 丢进 lmarena 的匿名对战,一次能收到**两个匿名模型**的打分,作为补充低权重票(每票约0.80)。\n"
           "提示词已做成自包含中性版(不依赖模型身份),并强化「一次性完整输出」。\n\n"
           "## 回收\n两个回复分别存为 `arena1.txt`/`arena2.txt`(或 `arena3`...,序号区分不同对战),放进一个目录跑 `tools/parse_xilei.py`;\n"
           "解析器已把 `arena+数字` 当作独立模型键保留,聚合时按 arena 低权重取平均并入。别忘了十三大主流模型仍是主力。\n")
open(os.path.join(axd, 'README.md'), 'w', encoding='utf-8').write(areadme)
print(f"已生成 Arena 匿名提示词 {arena_files} 个 -> {axd}")
