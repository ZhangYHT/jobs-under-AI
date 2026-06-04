# 数据规范

## 单元与粒度
- 测量/打分单元 = **中类(79)**。概览展示 大类(8)→ 中类;点击中类钻取到其官方**细类**(继承中类打分;细类级打分为后续)。
- 分类、S(数字职业)/L(绿色职业)标注直接来自《职业分类大典(2022年版)》。

## 文件
```
data/
  occupations.cn.json              官方分类骨架(本仓库已生成)
  collected/
    step1_taxonomy/<model>.json    分类校验与扩源
    step2_employment/<model>.json  就业人数
    step3_pay_edu/<model>.json     薪资 + 学历
    step4_scoring/<model>.json     6 维打分
  aggregated.cn.json               aggregate.py 产出,站点读取
  qa_report.md                     人工复核工作单
site/data.cn.js                    aggregate.py 同步产出(站点 <script> 加载)
```
模型键:`claude/gemini/gpt/qwen/zhipu/doubao/deepseek/wenxin/grok/yuanbao/kimi`。

## Schema(采集端,每文件为 JSON 数组)
- step1:`{code,title_official,title_match,english,digital_xilei[],green_xilei[],sources[],confidence,evidence,note}`
- step2:`{code,employment,year,caliber,source,source_url,evidence("official"/"estimate"/"unknown"),confidence}`
- step3:`{code,pay_median,pay_year,pay_source,pay_source_url,education,edu_source,confidence}`
- step4:`{code,overall,automation,augmentation,digital,moat,adoption,confidence,rationale}`(各维 0–100 整数)

## occupations.cn.json(骨架)
`{meta, categories:[{code,title}](8 大类), groups:[{code,title,parent,da_title,digital,green,n_xi,n_digital,n_green,细类:[{code,title,digital,green}]}](79 中类)}`

## aggregated.cn.json(成品,站点读取)
每个中类:骨架字段 + `employment / employment_basis / employment_sources[]`、`pay / pay_sources[] / education`、`dims{6维均值} / dims_median / dims_std`、`by_model{model:{6维}}`、`rationales{model:理由}`、`n_models`、`std(综合冲击分歧度)`、`flags[]`。顶层含 `meta`(模型阵容、免责声明)、`categories`、`groups`。

## 归并与聚合规则(aggregate.py)
- 步骤 2/3 官方锚定:取证据为 official 或置信度 high 的来源中位数;否则用全部值中位数并标 `*_provisional`;保留全部来源(满足"广搜官方")。
- 步骤 4 集成:每维 均值/中位数/标准差(分歧度)+ 各模型分。
- flags:`employment_missing`(无任何来源)、`employment_provisional`(无官方来源)、`employment_disagreement`(变异系数 > 0.5)、`pay_provisional`、`score_missing`、`score_disagreement`(综合冲击标准差 ≥ 12)。flags 汇总进 `qa_report.md` 作为人工复核工作单。

## 免责声明
分类与 S/L 标注源自官方大典;就业/薪资经众议院官方锚定(含 provisional 项见 flags,待官方核);AI 冲击为多模型集成估算,仅供参考,不代表官方结论。
