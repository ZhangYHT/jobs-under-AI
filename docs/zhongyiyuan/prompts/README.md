# 众议院提示词(独立可投喂)

每个文件 = 一个**可直接丢给对应网页 AI** 的完整提示词。结构**按步骤分**:`prompts/step1/<模型>.md` … `prompts/step4/<模型>.md` + `prompts/review/<评议员>.md`。

## 用法
1. 做某一步时,打开该步目录(如 `step2/`),把里面每个 `<模型>.md` 投喂给对应模型;收到回复后存为 `data/collected/step{n}_*/<模型键>.json`(step1→step1_taxonomy、step2→step2_employment、step3→step3_pay_edu、step4→step4_scoring)。
2. 全部模型回填后运行:`python tools/ingest.py <step> <你的原始返回目录>`(容错救回 + 校验),再 `python aggregate.py`。
3. 站点 `site/index.html` 自动更新。

## 注意(根据首轮经验)
- **不要把模型回答页另存为网页**(会变成 HTML/UTF-16,无法解析);请复制**纯文本/JSON**。
- 若模型输出被**截断**(算力受限):回复"继续"让它接着写,或分两条(前40 / 后39)。
- 深度研究模式容易输出**长报告而非 JSON**:提示词已要求"只输出 JSON";若它仍给报告,追加一句"现在只输出 JSON 数组"。
- 字段名必须用**英文键**(首轮有模型用了中文键);`tools/ingest.py` 已能容错映射,但仍以英文键为准。

## 模型键
`wenxin` · `qwen` · `zhipu` · `yuanbao` · `gpt` · `gemini` · `deepseek` · `doubao` · `grok` · `kimi` · `claude`
评议员(免费API):`nemotron-3-super-120b-a12b` · `qwq-32b` · `llama-3.2-90b-vision-instruct` · `gpt-oss-120b` · `Mistral-Large`
