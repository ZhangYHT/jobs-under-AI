# AI 众议院数据采集工作流(中国版)

本目录是「AI 众议院」为本项目产出真实数据的全部指令。众议院全程驱动四个步骤,分两种模式:

| 步骤 | 内容 | 众议院模式 | 产出文件 |
|---|---|---|---|
| 1 | 职业分类校验与扩源 | 考据/检索团(官方锚定) | `data/collected/step1_taxonomy/<model>.json` |
| 2 | 就业人数 | 考据/检索团(官方锚定) | `data/collected/step2_employment/<model>.json` |
| 3 | 薪资 + 学历 | 考据/检索团(官方锚定) | `data/collected/step3_pay_edu/<model>.json` |
| 4 | AI 冲击 6 维打分 | 评审团(集成) | `data/collected/step4_scoring/<model>.json` |

- 步骤 1 至 3 是**客观事实**:每个模型负责**查证并引用官方来源**,不得凭空编造;Claude 在 `aggregate.py` 中以官方来源为准锚定,模型间分歧用于质检并写入 QA 报告。
- 步骤 4 是**主观研判**:11 个模型独立盲测打分,聚合为均值/中位数/标准差(分歧度)。

## 模型阵容与专属指令
**主力研究/评分团(11)**,每个模型有**专属指令**(已生成,直接粘贴):见 [`prompts/`](prompts/)。
由 `gen_prompts.py` 从官方 79 中类生成,改分工后重跑即可刷新。

| 文件 | 模型(版本/模式) | 步骤1-3 官方来源专属领域 |
|---|---|---|
| `prompts/wenxin.md` | 文心一言(m码牛模式) | 部委与政策原文(人社部/统计局/发改委/工信部/教育部) |
| `prompts/qwen.md` | 通义千问 Qwen3.7max(任务助理) | 行业与产业(协会/白皮书/年报/招聘平台官方报告) |
| `prompts/zhipu.md` | 智谱清言 GLM5.1(研究模式) | 学术统计(CNKI/劳动经济与就业研究) |
| `prompts/yuanbao.md` | 腾讯元宝(Hy3 preview) | 行业协会/地方统计局/专业社群一手数据 |
| `prompts/gpt.md` | GPT(深度研究) | 国际官方对照(ILO/OECD/世行 + 英文一手) |
| `prompts/gemini.md` | Gemini 3.1 Pro(深度研究) | 深度综述与查漏、跨来源交叉核对 |
| `prompts/deepseek.md` | DeepSeek(专家模式) | 口径核对(年份/单位/统计口径对齐) |
| `prompts/doubao.md` | 豆包(深入研究) | 媒体引用官方数据的回溯核验 |
| `prompts/grok.md` | Grok 4.3 fast | 数据质疑(可靠性、来源存疑标记) |
| `prompts/kimi.md` | Kimi 2.6(thinking) | 长文档/年鉴 PDF 精读抽取 |
| `prompts/claude.md` | Claude(Opus · Extended Thinking) | 结构化汇编与最终交叉核对 |

每个文件含 步骤1-4 四个代码块(步骤4 评分细则全员一致以保证可比,仅附"专属视角"补强)。产出按文件名 `data/collected/step{n}_*/<key>.json` 保存。

**评议团(5,免费 API · 事后审查)**:见 [`prompts/review_team.md`](prompts/review_team.md)。在主力跑完并 `python aggregate.py` 后运行,审查数据(盲点/反方/补源/数值核查/一致性)。
`nemotron-3-super-120b-a12b` · `minimax-m2.7` · `llama-3.2-90b-vision-instruct` · `gpt-oss-120b` · `Mistral Large`

## 操作流程(手动)
1. 打开 `data/occupations.cn.json`,这是官方分类骨架(8 大类 / 79 中类 / 细类,带 S 数字职业、L 绿色职业标注)。
2. 按下面每步的指令文件,把指令 + 本批中类清单粘贴给每个模型。步骤 4 建议每批约 20 个中类、分 4 批。
3. 收集每个模型返回的 JSON,按文件名存入 `data/collected/step*/<model>.json`。
4. 运行 `python aggregate.py`,生成 `data/aggregated.cn.json` 与 `data/qa_report.md`。
5. 站点 `site/index.html` 自动读取(`aggregate.py` 同时刷新 `site/data.cn.js`)。

## 铁律(所有指令通用)
- 锚点主题在每份指令顶部原文重现,防漂移。
- 独立盲测,模型之间互不可见。
- 每个判断标注证据类型与置信度。
- 中性、专业、直接的中文,不写寒暄与表演式文案,不使用破折号。
- 只输出规定的严格 JSON,不要额外文字(可被代码块包裹)。
- 步骤 1 至 3 必须给出可核查的官方来源;查不到就如实标注,不要编造。
