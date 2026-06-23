# CLAUDE.md · 给 Claude 的仓库须知

> 本仓库由作者(ZhangYHT)+ Claude + Codex 协作。项目背景见 `README.md`,数据规范见 `docs/data-spec.md`(不在此重复)。

## 一句话定位
中文交互式树状图(Canvas treemap),用官方职业分类为地基、用「AI 众议院」(多模型集成)评估 AI 对中国 1639 个职业的冲击。大类(8)→ 中类(79)→ 细类(1639)。

## 头号规矩:维护 WORKLOG.md
- **每次提交前**,把本次改动按 `WORKLOG.md` 顶部「维护约定」追加为一条 **`[Claude]`** 条目(日期、commit、改了哪些文件、做了什么/为什么)。
- WORKLOG.md 是协作的追溯依据。作者已说明:**没被记录、归属不清的改动,默认算到 Claude 头上**,所以宁可多记。
- 条目格式以 `WORKLOG.md` 顶部为唯一事实源;**只在文件末尾追加,不改写他人(`[Codex]` / `[作者]`)的历史条目**。

## 关键纪律
- **开发分支**:在 `claude/vigilant-babbage-atJ5w` 上开发,不直接推 main。
- **产物禁破折号**:`site/*.js`、`*.html`、`data/*.json` 等产物不得出现长破折号(em-dash, U+2014)或短破折号(en-dash, U+2013),用 ASCII `-` 或中文标点。
- **改 UI 后重生 standalone**:UI 全在单文件 `site/index.html`(HTML/CSS/JS 全内联、零外部依赖)。改完务必 `python aggregate.py` 重生 `site/index.standalone.html` 与 `site/data.cn.js`。
- **模型 ID 不进产物**:模型标识只在对话里说,不写进仓库任何文件。
