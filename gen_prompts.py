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
【任务】为每个中类给出全国就业人数(单位:人)。优先官方:第七次全国人口普查 / 中国人口普查年鉴-2020(分职业)、中国统计年鉴、人社部公报、行业统计。注明数据年份与统计口径;证据类型分 official / estimate / unknown;查不到 employment 写 null 并在 note 说明,不要编造精确数字。

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
【任务】为每个中类给出:1) 年薪中位数(元/年),优先用国家统计局"分行业城镇单位就业人员平均工资"映射(注明对应行业门类与年份)或其他官方薪酬调查;2) 典型入职学历(博士/硕士/本科/大专/高中/初中),优先职业分类大典或国家职业标准。给来源与置信度;查不到写 null。

【中类清单(共{N},全部处理)】
{LIST}

【字段(英文键)】code, pay_median(整数或null), pay_year, pay_source, pay_source_url, education, edu_source, confidence
【示例一项】
{{"code":"2-06","pay_median":200000,"pay_year":2023,"pay_source":"国家统计局2023分行业平均工资·金融业(映射)","pay_source_url":"https://www.stats.gov.cn/...","education":"本科","edu_source":"职业分类大典(2022年版)","confidence":"medium"}}

{footer(True)}
"""

def step4(name, lens):
    return head(name,4,4,"AI 冲击 6 维打分(评审,集成)") + f"""
【锚点主题】{ANCHOR}:岗位 AI 冲击 6 维打分
【意图】主观研判;独立盲测,你的打分将与其他模型集成(取均值/中位数并展示分歧度)。评分细则对所有模型一致以保证可比。

【六维(各 0-100 整数)】
overall 综合冲击:被当前及可见近未来 AI 整体重塑的程度。
automation 任务自动化:AI 可独立完成其核心任务的比例(越高越可能被替代)。
augmentation AI增强:借助 AI 从业者生产力可被提升的幅度(高=被重塑而非必然消失)。
digital 数字化程度:工作可在纯数字/电脑环境完成的比例。
moat 护城河:对线下实操、人际信任、资质监管的依赖(越高越抗冲击)。
adoption 落地速度:该行业当前实际部署 AI 的速度。
【综合冲击锚点带】0-20极低(纯体力/强人际);21-40较低(体力或人际为主,AI仅边角);41-60中等(体力+脑力混合);61-80较高(脑力为主,用AI者生产力大增);81-100极高(几乎全在电脑完成,核心任务正被AI攻克)。核心原则:若工作几乎可完全在电脑上完成(写作/编程/分析/沟通),综合冲击天然≥60。高分=会被重塑、生产力剧变,不等于失业。
【你的专属视角(只补强判断,不改变所评对象与口径)】{lens}

【中类清单(共{N},全部处理)】
{LIST}

【字段(英文键)】code, overall, automation, augmentation, digital, moat, adoption(均0-100整数), confidence(high/medium/low), rationale(≤30字)
【示例一项】
{{"code":"2-02","overall":72,"automation":62,"augmentation":90,"digital":88,"moat":36,"adoption":72,"confidence":"medium","rationale":"设计与编码被AI大幅增强,现场调试与担责仍需人。"}}

{footer(False)}
"""

PROMPTS = os.path.join(ROOT, 'docs', 'zhongyiyuan', 'prompts')
# 清理旧的扁平文件,重建目录结构
if os.path.isdir(PROMPTS): shutil.rmtree(PROMPTS)
for key, name, angle, lens in ROSTER:
    d = os.path.join(PROMPTS, key); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'step1.md'), 'w', encoding='utf-8').write(step1(name, angle))
    open(os.path.join(d, 'step2.md'), 'w', encoding='utf-8').write(step2(name, angle))
    open(os.path.join(d, 'step3.md'), 'w', encoding='utf-8').write(step3(name, angle))
    open(os.path.join(d, 'step4.md'), 'w', encoding='utf-8').write(step4(name, lens))

REVIEW = [
 ("nemotron-3-super-120b-a12b","盲点扫描","11个主力是否集体遗漏了某些重要官方来源或职业?列出被忽略的视角与应补的官方资料。"),
 ("minimax-m2.7","反方代言","针对多数派的打分,给出尽可能扎实的反面论据;若少数派更有理,为其补强。"),
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

每个文件 = 一个**可直接丢给对应网页 AI** 的完整提示词。结构:`prompts/<模型>/step1~4.md` + `prompts/review/<评议员>.md`。

## 用法
1. 打开某模型目录(如 `wenxin/`),把 `step1.md` 整个内容投喂给该模型;收到回复后,把 **JSON** 存为 `data/collected/step1_taxonomy/<模型键>.json`。依次做 step2/3/4(分别存到 `step2_employment` / `step3_pay_edu` / `step4_scoring`)。
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
