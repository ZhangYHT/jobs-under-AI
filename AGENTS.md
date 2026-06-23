# AGENTS.md · 给 Codex 及任何非 Claude agent 的仓库须知

> 本仓库由作者(ZhangYHT)+ Claude + Codex 协作。项目背景见 `README.md`,数据规范见 `docs/data-spec.md`(不在此重复)。

## 一句话定位
中文交互式树状图(Canvas treemap),用官方职业分类为地基、用「AI 众议院」(多模型集成)评估 AI 对中国 1639 个职业的冲击。大类(8)→ 中类(79)→ 细类(1639)。

## 头号规矩:维护 WORKLOG.md
- **每次提交前**,把本次改动按 `WORKLOG.md` 顶部「维护约定」追加为一条,归属标签用 **`[Codex]`**(或你对应的 agent 名);记清日期、commit、改了哪些文件、做了什么/为什么。
- WORKLOG.md 是多方协作的追溯依据,append-only(只在文件末尾新增)。
- **不要冒领或改写 `[Claude]` / `[作者]` 的历史条目**;归属务必如实。
- 条目格式以 `WORKLOG.md` 顶部「维护约定」为唯一事实源(三份须知文件不各自定义格式,避免漂移)。

## 关键纪律
- **分支**:不要直接推 main;在你自己的开发分支上工作,合并走 PR。Claude 的分支是 `claude/vigilant-babbage-atJ5w`,**不要在上面改动**(那是 Claude 的),除非作者明确要求。
- **产物禁破折号**:`site/*.js`、`*.html`、`data/*.json` 等产物不得出现长破折号(em-dash, U+2014)或短破折号(en-dash, U+2013),用 ASCII `-` 或中文标点。
- **改 UI 后重生 standalone**:UI 全在单文件 `site/index.html`(HTML/CSS/JS 全内联、零外部依赖)。改完务必 `python aggregate.py` 重生 `site/index.standalone.html` 与 `site/data.cn.js`。
- **模型 ID 不进产物**:模型标识只在对话里说,不写进仓库任何文件。
