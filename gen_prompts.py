#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 AI 众议院各子模型的专属指令(同题异构,可直接粘贴)。
读 data/occupations.cn.json,为 11 个主力模型各生成 docs/zhongyiyuan/prompts/<key>.md
(含步骤1-4 四个代码块 + 官方79中类清单附录),并生成 review_team.md(5 位评议员)。
"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
occ = json.load(open(os.path.join(ROOT, 'data', 'occupations.cn.json'), encoding='utf-8'))
G = occ['groups']
# 紧凑 79 中类清单
LIST = '\n'.join(f"{g['code']}  {g['title']}  【{g['da_title']}】"
                 + ('  [含S数字职业]' if g['digital'] else '') + ('  [含L绿色职业]' if g['green'] else '')
                 for g in G)
ANCHOR = "AI 时代各岗位冲击图谱(中国版)数据采集"

# 11 主力:key, 显示名, 步骤1-3官方来源专属领域, 步骤4打分专属视角(不改评分对象,只补强其知识)
ROSTER = [
 ("wenxin","文心一言(m码牛模式)",
  "部委与政策原文。主攻人社部、国家统计局、发改委、工信部、教育部的公报/国家标准/政策文件,给出文件名与可核查链接。",
  "结合中国政策、行业准入与监管,判断其对落地速度与护城河的影响。"),
 ("qwen","通义千问 Qwen3.7max(任务助理)",
  "行业与产业。主攻行业协会报告、白皮书、上市公司年报、招聘平台官方报告,反映岗位的真实产业样态与规模。",
  "结合行业真实 AI 部署进度(是真用还是观望),校准落地速度。"),
 ("zhipu","智谱清言 GLM5.1(研究模式)",
  "学术统计。主攻 CNKI、劳动经济与就业研究文献中的职业就业与薪资测算,给出文献出处。",
  "从学术对自动化可行性的研究判断任务自动化的边界。"),
 ("yuanbao","腾讯元宝(Hy3 preview)",
  "行业协会与地方。主攻各行业协会、地方统计局、专业社群中的一手数据,补充国家级之外的官方与准官方来源。",
  "结合行业内部与一线实操,判断真实可替代部分。"),
 ("gpt","GPT(深度研究)",
  "国际官方对照。主攻 ILO、OECD、世界银行等对华就业/职业统计与英文一手报告,做跨语言交叉印证。",
  "参考国际 AI 能力前沿与海外同类岗位的演变趋势。"),
 ("gemini","Gemini 3.1 Pro(深度研究)",
  "深度综述与查漏。系统检索多来源、交叉核对、补齐其他模型遗漏的官方资料,标注来源可靠性。",
  "做六维之间的一致性校验,避免单点高估或低估。"),
 ("deepseek","DeepSeek(专家模式)",
  "口径核对。专查不同来源的统计年份、单位、口径差异(如城镇单位 vs 全社会就业),给出可比性说明。",
  "从第一性原理审视任务可自动化的真实边界与前提条件。"),
 ("doubao","豆包(深入研究)",
  "二次核对。主攻权威媒体、民生报道中引用的官方数据,回溯其原始官方出处并核验。",
  "结合一线从业者与社区的真实感受,校准 AI 增强的体感幅度。"),
 ("grok","Grok 4.3 fast",
  "数据质疑。专门标出哪些流传数字不可靠、来源存疑、相互矛盾,给出质疑理由,宁缺毋滥。",
  "警惕炒作高估,标出被夸大但实际尚未落地的环节,压低虚高分。"),
 ("kimi","Kimi 2.6(thinking)",
  "长文档精读。主攻统计年鉴、人口普查年鉴、行业蓝皮书等长 PDF 的精确抽取,给出页/表出处。",
  "结合长篇研究报告的细节,补强对增强与落地的判断。"),
 ("claude","Claude(Opus · Extended Thinking)",
  "结构化汇编与最终交叉核对。把各来源对齐到统一口径,标注冲突与置信度。",
  "对六维做结构化权衡,确保同一大类内部相对关系自洽。"),
]

USE = ("> 用法:把下面每个代码块依次粘进【{name}】。建议在**同一个对话**里按 步骤1→2→3→4 顺序进行"
       "(这样步骤2-4 可直接沿用步骤1 中的 79 个中类清单);若分开新对话,清单见文末附录。\n"
       "> 收到各模型返回的 JSON 后,按文件名 `data/collected/step{{n}}_*/{key}.json` 保存,再运行 `python aggregate.py`。\n")

IRON = "【铁律】\n官方优先、有据可查;无法核实写 null 或标注,绝不编造。中性专业,不使用破折号。只输出规定的严格 JSON,不要额外文字。"

def block(title, body):
    return f"### {title}\n\n```\n{body}\n```\n"

def step1(name, angle):
    return block("步骤 1 · 职业分类校验与扩源(考据,官方锚定)", f"""【锚点主题】
{ANCHOR}:职业分类校验与扩源

【模型】{name}　【意图】考据/检索(官方锚定,纯客观)
【本轮定位】独立盲测,你看不到其他模型输出;最终以官方来源为准交叉核对。

【你的专属切入角度】
{angle}

【基准】《中华人民共和国职业分类大典(2022年版)》(人社部、市场监管总局、国家统计局):8大类/79中类/449小类/1636细类,官方标注数字职业(S)97个、绿色职业(L)133个。

【中类清单(共79,全部处理)】
{LIST}

【任务】对每个中类:1) 校验编码与名称是否与官方一致;2) 指出其下哪些细类属数字职业(S)/绿色职业(L);3) 用你的专属领域尽量多地补充官方级来源(名称+可核查链接);4) 给规范英文名;5) 查不到如实标注。

【输出:严格 JSON 数组,每个中类一项】
[{{"code":"2-02","title_official":"工程技术人员","title_match":true,"english":"Engineering Technicians","digital_xilei":["2-02-30-01 人工智能工程技术人员"],"green_xilei":[],"sources":[{{"name":"职业分类大典(2022年版)","url":"https://www.mohrss.gov.cn/...","type":"official"}}],"confidence":"high","evidence":"事实","note":""}}]

{IRON}""")

def step2(name, angle):
    return block("步骤 2 · 就业人数(考据,官方锚定)", f"""【锚点主题】
{ANCHOR}:就业人数

【模型】{name}　【意图】考据/检索(官方锚定)
【本轮定位】独立盲测。沿用上文同一份 79 个中类(如新对话见文末附录)。

【你的专属切入角度】
{angle}

【任务】为每个中类给出全国就业人数(单位:人)。优先官方:第七次全国人口普查/中国人口普查年鉴-2020(分职业)、中国统计年鉴、人社部公报、行业统计。注明年份与统计口径;证据类型分 official/estimate/unknown;查不到 employment 写 null 并说明,不要编造精确数字。

【输出:严格 JSON 数组】
[{{"code":"4-04","employment":8000000,"year":2020,"caliber":"全社会就业(七普分职业)","source":"中国人口普查年鉴-2020","source_url":"https://www.stats.gov.cn/...","evidence":"official","confidence":"high"}}]

{IRON}""")

def step3(name, angle):
    return block("步骤 3 · 薪资 + 学历(考据,官方锚定)", f"""【锚点主题】
{ANCHOR}:薪资与学历

【模型】{name}　【意图】考据/检索(官方锚定)
【本轮定位】独立盲测。沿用上文同一份 79 个中类。

【你的专属切入角度】
{angle}

【任务】为每个中类给出:1) 年薪中位数(元/年),优先用国家统计局"分行业城镇单位就业人员平均工资"映射(注明对应行业门类与年份)或其他官方薪酬调查;2) 典型入职学历(博士/硕士/本科/大专/高中/初中),优先职业分类大典或国家职业标准。给来源与置信度;查不到写 null。

【输出:严格 JSON 数组】
[{{"code":"2-06","pay_median":200000,"pay_year":2023,"pay_source":"国家统计局2023分行业平均工资·金融业(映射)","pay_source_url":"https://www.stats.gov.cn/...","education":"本科","edu_source":"职业分类大典(2022年版)","confidence":"medium"}}]

{IRON}""")

def step4(name, lens):
    return block("步骤 4 · AI 冲击 6 维打分(评审,集成)", f"""【锚点主题】
{ANCHOR}:岗位 AI 冲击 6 维打分

【模型】{name}　【意图】主观研判(独立盲测,将与其他模型集成)
【本轮定位】沿用上文同一份 79 个中类,逐个打分。评分细则对所有模型一致以保证可比。

【六维(各 0-100 整数)】
overall 综合冲击:被当前及可见近未来 AI 整体重塑的程度。
automation 任务自动化:AI 可独立完成其核心任务的比例(越高越可能被替代)。
augmentation AI增强:借助 AI 从业者生产力可被提升的幅度(高=被重塑而非必然消失)。
digital 数字化程度:工作可在纯数字/电脑环境完成的比例。
moat 护城河:对线下实操、人际信任、资质监管的依赖(越高越抗冲击)。
adoption 落地速度:该行业当前实际部署 AI 的速度。

【综合冲击锚点带】0-20极低(纯体力/强人际,AI几乎不触及);21-40较低(体力或人际为主,AI仅边角);41-60中等(体力+脑力混合,AI显著辅助);61-80较高(脑力为主,用AI者生产力大增);81-100极高(几乎全在电脑完成,核心任务正被AI攻克)。核心原则:若工作几乎可完全在电脑上完成(写作/编程/分析/沟通),综合冲击天然≥60。高分=会被重塑、生产力剧变,不等于失业。

【你的专属视角(只补强判断,不改变所评对象与口径)】
{lens}

【输出:严格 JSON 数组,每个中类一项,理由≤30字】
[{{"code":"2-02","overall":72,"automation":62,"augmentation":90,"digital":88,"moat":36,"adoption":72,"confidence":"medium","rationale":"设计与编码被AI大幅增强,现场调试与担责仍需人。"}}]

{IRON}""")

os.makedirs(os.path.join(ROOT, 'docs', 'zhongyiyuan', 'prompts'), exist_ok=True)
for key, name, angle, lens in ROSTER:
    md = (f"# 众议院专属指令 · {name}\n\n保存到:`data/collected/step1~4/{key}.json`\n\n{USE.format(name=name, key=key)}\n"
          + step1(name, angle) + "\n" + step2(name, angle) + "\n" + step3(name, angle) + "\n" + step4(name, lens)
          + f"\n---\n\n## 附录:官方 79 中类清单(如分开新对话时粘贴)\n\n```\n{LIST}\n```\n")
    open(os.path.join(ROOT, 'docs', 'zhongyiyuan', 'prompts', f'{key}.md'), 'w', encoding='utf-8').write(md)

# 5 位评议员(免费 API):事后审查已采集数据,各有侧重
REVIEW = [
 ("nemotron-3-super-120b-a12b","盲点扫描","11个主力是否集体遗漏了某些重要官方来源或职业?列出被忽略的视角与应补的官方资料。"),
 ("minimax-m2.7","反方代言","针对多数派的打分,给出尽可能扎实的反面论据;若少数派更有理,为其补强。"),
 ("llama-3.2-90b-vision-instruct","信息源补位","补充主流模型未见的非主流/小众官方与准官方资料(地方、行业、英文小语种)。"),
 ("gpt-oss-120b","数值合理性核查","核查就业/薪资/打分中的异常值与口径冲突,标出最可疑的若干项及理由。"),
 ("Mistral Large","一致性与可比性审查","审查跨中类打分是否自洽(同类内部相对关系、量纲一致性),指出矛盾点。"),
]
rev = ("# 众议院评议团指令(5 位免费 API · 事后审查)\n\n"
       "在 11 个主力跑完步骤1-4 且 `python aggregate.py` 生成 `data/aggregated.cn.json` 与 `data/qa_report.md` 之后运行。"
       "把聚合摘要(或 qa_report 内容)粘到下面 `{{聚合摘要}}` 处。各评议员独立盲测、互不可见。\n\n")
for key, role, task in REVIEW:
    rev += block(f"评议员 · {key}({role})", f"""【锚点主题】
{ANCHOR}:对已采集数据的事后审查

【模型】{key}　【角色】{role}(评议团,事后审查,不重新采集)
【本轮定位】独立盲测。11个主力已完成步骤1-4并聚合。你的任务是审查,不是复述。

【已聚合摘要】
{{{{聚合摘要:粘贴 data/aggregated.cn.json 关键字段或 data/qa_report.md}}}}

【你的专属任务】
{task}

【输出:严格 JSON 数组】
[{{"code":"<相关中类编码或 GLOBAL>","issue":"问题简述","suggestion":"建议(补哪份官方资料/如何修正)","severity":"high|medium|low","evidence":"依据"}}]

{IRON}""") + "\n"
open(os.path.join(ROOT, 'docs', 'zhongyiyuan', 'prompts', 'review_team.md'), 'w', encoding='utf-8').write(rev)

print("已生成:", len(ROSTER), "个主力模型文件 + 1 个评议团文件")
print("目录: docs/zhongyiyuan/prompts/")
for key, name, *_ in ROSTER: print("  ", key + '.md', '·', name)
print("   review_team.md · 5 位评议员")
