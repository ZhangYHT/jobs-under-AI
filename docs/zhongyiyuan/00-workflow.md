# AI 众议院数据采集工作流(中国版)

众议院全程驱动四个步骤,分两种模式:

| 步骤 | 内容 | 模式 | 产出 |
|---|---|---|---|
| 1 | 职业分类校验与扩源 | 考据(官方锚定) | `data/collected/step1_taxonomy/<key>.json` |
| 2 | 就业人数 | 考据(官方锚定) | `data/collected/step2_employment/<key>.json` |
| 3 | 薪资 + 学历 | 考据(官方锚定) | `data/collected/step3_pay_edu/<key>.json` |
| 4 | AI 冲击 6 维打分 | 评审(集成) | `data/collected/step4_scoring/<key>.json` |

步骤 1-3 是客观事实:各模型按**不同官方来源领域**查证并引用,Claude 在 `aggregate.py` 中以官方来源锚定、用分歧做质检。步骤 4 是主观研判:各模型独立盲测打分,聚合为均值/中位数/标准差。

## 提示词:独立可投喂(每个文件一个阶段)
见 [`prompts/`](prompts/),**按步骤分文件夹**:`prompts/step1/<模型>.md` … `prompts/step4/<模型>.md`,每个文件可**直接丢给对应网页 AI**。由 `gen_prompts.py` 从官方 79 中类生成。做第 N 步时打开 `stepN/` 目录,把每个模型文件投喂给对应模型即可。

| 模型键 | 模型(版本/模式) | 步骤1-3 官方来源专属领域 |
|---|---|---|
| wenxin | 文心一言(m码牛模式) | 部委与政策原文(人社部/统计局/发改委/工信部/教育部) |
| qwen | 通义千问 Qwen3.7max(任务助理) | 行业与产业(协会/白皮书/年报/招聘平台官方报告) |
| zhipu | 智谱清言 GLM5.1(研究模式) | 学术统计(CNKI/劳动经济与就业研究) |
| yuanbao | 腾讯元宝(Hy3 preview) | 行业协会/地方统计局/专业社群一手数据 |
| gpt | GPT(深度研究) | 国际官方对照(ILO/OECD/世行 + 英文一手) |
| gemini | Gemini 3.1 Pro(深度研究) | 深度综述与查漏、跨来源交叉核对 |
| deepseek | DeepSeek(专家模式) | 口径核对(年份/单位/统计口径对齐) |
| doubao | 豆包(深入研究) | 媒体引用官方数据的回溯核验 |
| grok | Grok 4.3 fast | 数据质疑(可靠性、来源存疑标记) |
| kimi | Kimi 2.6(thinking) | 长文档/年鉴 PDF 精读抽取 |
| claude | Claude(Opus · Extended Thinking) | 结构化汇编与最终交叉核对 |

步骤 4 评分细则**全员一致**(保证可比),仅附每模型"专属视角"补强。

**评议团(5,免费 API · 事后审查)**:[`prompts/review/`](prompts/review/)。在主力跑完并 `aggregate.py` 后运行。
`nemotron-3-super-120b-a12b` · `minimax-m2.7` · `llama-3.2-90b-vision-instruct` · `gpt-oss-120b` · `Mistral-Large`

## 操作流程
1. 把 `prompts/<模型>/stepN.md` 投喂给对应模型,收到回复后把 **JSON** 存为 `data/collected/step{n}_*/<key>.json`。
2. 也可把各模型原始返回先丢进一个目录,用 `python tools/ingest.py step1_taxonomy <目录>` 容错救回(自动去围栏/修控制字符/逐对象救/中文键映射/按官方编码校验)。
3. `python aggregate.py` → 生成 `data/aggregated.cn.json` 与 `data/qa_report.md`,并刷新 `site/data.cn.js`。
4. step1 结果可用 `python tools/reconcile_taxonomy.py` 把英文名与官方来源回填进 `occupations.cn.json`。

## 首轮经验(已写入提示词硬约束)
- 不要把模型回答页另存为**网页**(会变 HTML/UTF-16 无法解析);复制纯文本/JSON。
- 输出被**截断**(算力受限):回复"继续"接着写,或分两条(前40 / 后39)。
- 深度研究模式易输出**长报告而非 JSON**:提示词已要求只输出 JSON;若仍给报告,追加"现在只输出 JSON 数组"。
- 字段名用**英文键**;`ingest.py` 可容错映射中文键。

## 铁律
锚点防漂移 · 独立盲测 · 证据类型与置信度标注 · 中性专业、禁破折号 · 只输出严格 JSON · 步骤1-3 官方有据、查不到如实标注不编造。
