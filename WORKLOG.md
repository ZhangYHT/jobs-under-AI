# WORKLOG · jobs-under-AI 协作改动日志

> 本仓库由 **作者(ZhangYHT)** 主理,**Claude** 与 **Codex** 两个 AI 协作开发。
> 这份日志按时间线逐条记录每次改动并标注归属,用于多方协作时的追溯与对账。

## 维护约定(Claude / Codex / 作者 都按此办)

- **事实源**:git 提交历史是最终事实源,本文件是它的人类可读索引。**凡未出现在某作者名下 commit 里的改动,即不属于该作者。**
- **append-only**:新条目追加到「时间线」段**末尾**(即文末「当前状态快照 / 给协作方的提醒」两段常驻元信息**之前**);旧条目不改写、不删除、不重排(最旧在上、最新在下)。这样两个 AI 即便同时写,冲突也只落在时间线尾部、极易合并。
- **谁写谁标**:每条用 `[Claude]` / `[Codex]` / `[作者]` 标注归属;**不得冒领或改写他人条目**。
- **何时写**:每次 `git commit`(或 push)前,把本次改动补成一条。
- **条目格式**:

  ```
  ### YYYY-MM-DD · [归属标签] · PR #N
  - `<commit 短哈希>` <提交标题原文照抄>
    - 文件:<改了哪些文件/目录>
    - 说明:<一句话:做了什么 / 为什么>(标题已说清可省)
  ```

> 本文件的**初始历史(2026-06-04 ~ 2026-06-23)由 Claude 于 2026-06-23 依据 git 历史回填**。
> 截至回填:**Claude 提交 76 条**;作者提交若干(1 次初始化 + 06-19 几次手改 + 多次 PR 合并)。Codex 于 06-23 起开始提交(首条 `f6c916f`,见时间线 PR #8/#9)。

---

## 里程碑速览

| PR | 合并日 | 主题 | Claude 提交数 |
|---|---|---|---|
| **#1** | 06-19 | 项目地基:Phase 0 原型 → Phase 1 官方分类+众议院数据管线 → 1~4 步采集与官方锚定 → 站点 v3/v4 → Phase 2 细类管线 → Claude 全量自采 1639 细类 → 细类层上线 → 数据瘦身 → 部署工作流 → 收款码 | 36 |
| **#2** | 06-19 | 收款码方码 + 抽屉文案 + 触屏适配 | 2 |
| **#3** | 06-22 | 数据精修(Phase A/B)+ 配色 + SEO/性能/缓存 + 面积三态 + 底部信息条 + 搜索增强 + 站点自解释 | 25 |
| **#4** | 06-22 | 数据去脏 + 文案说人话 + 首屏教程化 + 搜索滚动 + 对比跨类 + 性能 + **自由画布视图初版** + 群友反馈 | 8 |
| **#5** | 06-23 | 自由画布重做(语义缩放嵌套画布)+ 加载提速 + 教程修复 | 3 |
| **#6** | 06-23 | 自由画布二次整改 + 体检·eval 截断修复 | 2 |
| **#7** | 06-23 | 新增 WORKLOG.md + CLAUDE.md + AGENTS.md(协作机制落地) | 2 |
| **#8** | 06-23 | Codex 首次提交(Worker 预计算)同步入 claude 分支 | Codex 1 |
| **#9** | 06-23 | 同一 Codex 提交(`f6c916f`)同步入 main | Codex 1(同 #8) |
| **#10** | 06-23 | Codex:自由画布「复位视图」整改(并入 claude 分支) | Codex 1 |

> 注:个别提交标题里的 `#6`(如「#6 2D 自由画布视图」)是作者内部的功能编号,**不是** PR 号;该提交实际并入 PR #4。
> 注:#8 与 #9 是同一个 Codex 提交分别同步进 claude 分支与 main,由作者手动操作,目的是避免两条分支互相不知道对方进度。

---

## 时间线

### 2026-06-04 · 项目启动 + Phase 0/1(PR #1)
- `4259398` [作者] Initial commit
  - 文件:README.md ·  建仓。
- `447ad15` [Claude] Add Phase 0 clickable prototype for AI job-impact treemap (CN)
  - 文件:.gitignore · prototype.html ·  说明:首版可点击原型(演示数据,留作参考)。
- `b95594a` [Claude] Upgrade prototype: modern palette, animations, radar, search, themes
  - 文件:prototype.html ·  说明:原型升级(现代配色/动画/雷达/搜索/深浅主题)。
- `03d427f` [Claude] Phase 1: official taxonomy + AI-congress data pipeline + data-driven site
  - 文件:site · aggregate.py · data · docs · README.md(16f)·  说明:正式架构落地,官方分类骨架 + 「AI 众议院」数据管线 + 数据驱动站点。
- `2f1205b` [Claude] Add per-model AI-congress prompts (heterogeneous, paste-ready)
  - 文件:docs/zhongyiyuan/prompts/** · gen_prompts.py(14f)·  说明:各模型异构提示词(可直接粘贴投喂)。
- `5530575` [Claude] Ingest step-1 results; rework prompts into per-stage droppable files
  - 文件:aggregate.py · site · data · tools/ingest.py · tools/reconcile_taxonomy.py · prompts(85f)·  说明:并入第 1 步(分类校验)结果;提示词重构为分步可投喂文件。
- `6013a1c` [Claude] Harden ingest salvage (strip in-string control chars)
  - 文件:tools/ingest.py ·  说明:加固解析容错(剔除字符串内控制字符)。

### 2026-06-05 · 官方锚定数据 + 站点 v3(PR #1)
- `6010968` [Claude] Ingest step-2 employment; reorganize prompts by step
  - 文件:site · data · tools · prompts(61f)·  说明:并入第 2 步就业人数;提示词按步重组。
- `673f2a2` [Claude] Anchor employment to the 7th census (read from the yearbook table image)
  - 文件:site · aggregate.py · data(5f)·  说明:就业人数锚定七普(从人口普查年鉴表格图读取)。
- `4d0f505` [Claude] Anchor pay to official per-post wages (NBS 2023)
  - 文件:site · aggregate.py · data(5f)·  说明:薪资锚定国家统计局分岗工资。
- `d26955e` [Claude] Refine pay with official industry wages (NBS 2023, by industry)
  - 文件:site · aggregate.py · data(5f)·  说明:薪资细化为分行业工资。
- `3819452` [Claude] Ingest step-4 scores: real 10-model ensemble with disagreement
  - 文件:site · data · tools(14f)·  说明:并入第 4 步打分,真 10 模型集成 + 分歧度。
- `4af447c` [Claude] Blend private-sector wages; add pay/education as treemap color layers
  - 文件:site · data(4f)·  说明:混入私营部门工资;薪资/学历作为树状图色层。
- `b132557` [Claude] Redesign site (full-screen treemap, collapsible overlays); natural-language step-4 prompt
  - 文件:site · prompts · gen_prompts.py(13f)·  说明:站点重设计(全屏树状图 + 可折叠浮层);step4 改自然语言提示词。
- `1d7499d` [Claude] Ingest natural-language step-4 scores (much wider spread) + da summaries
  - 文件:site · aggregate.py · data · tools(25f)·  说明:并入自然语言版 step4 打分(分布更广)+ 大类摘要。
- `6eb0ed0` [Claude] Site v3: address UI feedback (fade, detail-in-topbar, hover-zoom, wrap, etc.)
  - 文件:site/index.html ·  说明:站点 v3,回应 UI 反馈。

### 2026-06-08 · 站点 v4(PR #1)
- `1423616` [Claude] Site v4: drawer handle, left back-tab, proximity-grow, detail charts, da-in-topbar
  - 文件:site/index.html ·  说明:抽屉把手 / 左侧返回页签 / 邻近放大 / 详情图表 / 大类信息进顶栏。
- `cea604b` [Claude] Tweak: gentler hover zoom; handle follows panel; top flush to edge
  - 文件:site/index.html ·  说明:悬停放大更柔 / 把手跟随面板 / 顶部贴边。

### 2026-06-09 ~ 06-11 · Phase 2 细类管线 + 提示词(PR #1)
- `6bc9581` [Claude] Phase 2 kit: detailed-occupation (细类) scoring pipeline + first seed (06-09)
  - 文件:site · aggregate.py · data · tools · prompts(184f)·  说明:细类(具体职业)打分管线 + 首个种子。
- `d930a92` [Claude] 保存重点中类细类原始返回与解析结果(10中类/160文件),修复元宝非断行连字符解析 (06-11)
  - 文件:data/collected/** · tools(171f)。
- `862c096` [Claude] 细类提示词:打包分层加长版(剩余69中类) (06-11)
  - 文件:docs/zhongyiyuan/prompts/xilei/**(大量 .md)。

### 2026-06-17 · Claude 全量自采 1639 细类(PR #1)
- `f082426` [Claude] 查漏补缺 + 反偷懒提示词工程 + 新可信度排序 + Arena 双盲
  - 文件:prompts · tools · aggregate.py · data ·  说明:补采机制 + 提示词工程 + 可信度排序 + Arena 双盲匿名票。
- `5af0872` [Claude] Claude 自采细类 第1批:科研/新闻出版/金融 51细类(中国语境)
  - 文件:data/collected/**(4f)。
- `39e93ea` [Claude] Claude 自采 第2批:大类1/3/5/7/8 共113细类(负责人/办事/农林牧渔/军队)
  - 文件:data/collected/**(5f)。
- `d023bc1` [Claude] Claude 自采 第3批:大类4 全部317细类(批发零售/交通物流/餐饮/房产/商务/技术辅助/环境/居民服务/电燃水/修理/文教/健康休闲)
  - 文件:data/collected/**(6f)。
- `385e329` [Claude] Claude 自采 第4批:大类2 的 2-03/2-04/2-05/2-06/2-07/2-09 共229细类(农技/飞船/卫生/经金/法律/文艺)
  - 文件:data/collected/**(4f)。
- `260a5cc` [Claude] Claude 自采 第5批:2-02 工程技术人员 全部217细类(地勘测绘冶化机械航空电子IT电力交通建筑林水海洋纺织气象环境质量工业管理设计与AI新兴技术)
  - 文件:data/collected/**(4f)。
- `a745ff3` [Claude] Claude 自采 第6批(部分):大类6 的 6-01至6-11 共239细类(农副食品烟草纺织服装木纸印刷文教工美石化化学制品)
  - 文件:data/collected/**(3f)。
- `5910936` [Claude] Claude 自采完成:大类6 全部671细类,Claude 全量覆盖 1639/1639 细类
  - 文件:data/collected/**(4f)·  说明:Claude 单模型种子全量覆盖 1639 细类完成。

### 2026-06-18 · 细类层上线 + 数据瘦身 + 部署 + 收款码(PR #1)
- `114e1a4` [Claude] 查漏补缺重构:按发送轮次分组 + 自包含详细提示词 + 更大批量
  - 文件:prompts · tools。
- `f29d4ff` [Claude] 查漏补缺并入 + subagent 救回静默丢失维度 + 前端去破折号
  - 文件:data/collected · site · aggregate.py · data。
- `410f681` [Claude] 细类层上线:接入加权聚合 + Arena 匿名票 + 前端补全(待采集/等级/评价)
  - 文件:site · aggregate.py · data · data/collected。
- `c60bd7c` [Claude] 新增 GitHub Pages 部署工作流(发布 site/ 目录)
  - 文件:.github/**。
- `58a5494` [Claude] 数据瘦身:细类不逐模型存理由文本,data.cn.js 5.2MB->1.7MB(gzip 0.41MB)
  - 文件:site · aggregate.py · data(3f)。
- `947ef15` [Claude] 前端打磨上线版:支持作者抽屉 + 细类点开详情 + 等级色阶图例 + 品牌/移动端
  - 文件:site/index.html。
- `cb5f8eb` [Claude] 抽屉收款码改为保持比例显示(整张收款码长图或方码均清晰)
  - 文件:site/index.html。
- `743da68` [Claude] 嵌入微信/支付宝收款码(裁切为二维码白卡 + base64 内嵌)
  - 文件:site/index.html。

### 2026-06-19 · PR #1 合并 · 作者手改 · PR #2
- `fe5880a` [作者] Merge pull request #1 ·  合并以上 36 条 Claude 提交入 main。
- `879ec26` [作者] Add GitHub Actions workflow for deployment ·  作者直接提交。
- `1fa9600` [作者] Update index.html ·  作者手改。
- `eba3b16` [作者] Update index.html ·  作者手改。
- `f3f138b` [作者] 恢复内容 ·  作者把上面手改回滚/恢复。
- `fd6b6d7` [Claude] 更新内嵌收款码为作者裁好的方码(微信/支付宝各360px)
  - 文件:site/index.html。 ·  (PR #2)
- `75a58ed` [Claude] 抽屉重做作者文案 + 手机/平板触屏适配
  - 文件:site/index.html。 ·  (PR #2)
- `4bc7943` [作者] Merge pull request #2 ·  合并上面 2 条入 main。

### 2026-06-19 · 数据精修 Phase A/B + 配色(PR #3)
- `76b3f5b` [Claude] 删除顶部'巴别塔工程'徽标 + 新增手机端提示横幅
  - 文件:site/index.html。
- `bd8815c` [Claude] Phase A 准备:大类逐字摘要 curated + 细类评价加长脚本(待修sentence抽取)
  - 文件:data · tools(2f)。
- `d3204b2` [Claude] Phase B(配色):色阶改低饱和顺序色(去彩虹廉价感,顺带色盲更友好)+ 强调色降霓虹、阴影更柔(深浅主题)
  - 文件:site/index.html。
- `919230b` [Claude] Phase B 收尾:维度/薪资/学历旁加「?」释义气泡 + 8大类通俗标签样式 + 主脚本 try/catch 兜底(报错友好化)+ 维度高亮改用 dataset.key
  - 文件:site/index.html。
- `67f1f1c` [Claude] Phase A 简介:大类改用 curated 逐字摘要覆盖自动抽取版 + 中类简介取最长干净理由(clean_rat 砍掉串入的评分尾巴/下一条编码名称)+ 前端中类详情显示简介
  - 文件:site · aggregate.py · data(4f)。
- `415cc67` [Claude] Phase A 细类评价:强化污染过滤(bad_eval),从13模型里剔除思考过程/方法论/批次脚手架/报告标题/跨批汇总/装饰横幅/HTML 等非正文候选;1639条残留污染 28+ -> 0,且0空0兜底
  - 文件:site · aggregate.py · data(5f)。
- `84efa80` [Claude] 部署:aggregate.py 增产自包含单文件 index.standalone.html(数据内联、免相对路径,供 WordPress 等自托管直接上传;GitHub Pages 仍用双文件)+ by_model 键序 sorted 消除每次重跑的无意义大 diff
  - 文件:site · aggregate.py · data(4f)·  说明:从此 `aggregate.py` 同时产出 `site/index.standalone.html`(改 UI 后须重生)。

### 2026-06-20 · 站点自解释 + 中类简介 + 搜索增强 + 底部信息条(PR #3)
- `783f2bf` [Claude] 站点自解释(C3+E4):首屏说明卡(面积/颜色/下钻/AI分≠失业,localStorage首访门控)+ 顶部'说明'按钮开关于·数据与方法面板(从meta渲染官方来源/加权集成/模型分歧/caveat/版本)+ 移动端首访只弹说明卡;meta加version v1.0
  - 文件:site · aggregate.py · data(5f)。
- `00a9dfa` [Claude] Phase A 中类简介 harvest(43/74):从 step4 富推理逐字摘高质量中类简介写入 curated.zhong(大类1/2/3/4/5/7/8),替换70字回退;大类6 待会话上限重置后补
  - 文件:site · data(4f)。
- `d9d8e16` [Claude] Phase A 中类简介 harvest 完成(74/74):补齐大类6的31个中类(逐中类grep定位、无串味,gpt批次截断处改用其他模型),全部从step4富推理逐字摘;全79中类 0破折号0方法论0空
  - 文件:site · data(4f)。
- `d051105` [Claude] C4 搜索增强:搜索结果下拉(中类+细类,前缀/子串/中类英文匹配,按就业排序,方向键+回车选,点选跨层跳转 drillInto+openLeaf)+ 维度阈值筛选滑块
  - 文件:site/index.html(+standalone)。
- `5664070` [Claude] C2 底部信息条:新增通栏 #botbar(左面包屑/中AI免责声明/右支持作者),画布 #stage 底部让位 var(--both) 不再被遮;合并删除浮动 #supBtn 与顶部 #crumbTop;窄屏隐藏免责声明
  - 文件:site/index.html(+standalone)。

### 2026-06-21 · SEO/性能/缓存 + 面积三态 + 快捷键 + 拼音搜索 + CSV(PR #3)
- `2016346` [Claude] E1 SEO/分享卡:head 注入 description/keywords/robots/canonical/OG/Twitter/JSON-LD(WebApplication)+ 内联 SVG favicon + apple-touch-icon
  - 文件:site · tools(5f)。
- `5c64bb9` [Claude] E2 性能/idle 停帧:帧循环按需运行,静止即停(省 CPU 与电,低端/手机更友好)
  - 文件:site/index.html(+standalone)。
- `0227ce0` [Claude] E3 缓存版本号:data.cn.js 带 ?v=v1.0,版本不变 F5 走缓存、变则失效重拉
  - 文件:site · aggregate.py(3f)。
- `97a6191` [Claude] C1 方块面积双模式(三态):人数 / 影响体量 / 纯分
  - 文件:site/index.html(+standalone)。
- `840f37b` [Claude] C5 更新日志(changelog):左下角 v1.0 pill 打开版本说明抽屉
  - 文件:site/index.html(+standalone)。
- `74626ac` [Claude] C6 快捷键 + 手势 + 键盘可达(ARIA)
  - 文件:site/index.html(+standalone)。
- `bb54043` [Claude] C4 拼音搜索 + 别名管道:aggregate 生成 py/pyi,SI/rankHits 支持拼音/别名匹配
  - 文件:site · aggregate.py · data · requirements.txt(6f)。
- `6da9d6c` [Claude] D3 导出 CSV + 工具菜单 + 下载助手
  - 文件:site/index.html(+standalone)。

### 2026-06-22 · 对比/散点/分享图/引导 + 别名 + 自由画布初版(PR #3 收尾 → PR #4)
PR #3 部分(以下 5 条):
- `094a9ba` [Claude] D1 加入对比:多选同层职业并排比六维 + 人数/薪资
  - 文件:site/index.html(+standalone)。
- `6ea042e` [Claude] C4 别名:全量 1718 职业招聘叫法别名(7892 条),搜索命中率拉满
  - 文件:site · data · data/collected · tools(20f)。
- `4dd0fc6` [Claude] D2 综合散点图:就业 x 综合冲击散点浮层,点击联动主图
  - 文件:site/index.html(+standalone)。
- `fe32c3b` [Claude] D3 分享图:一键生成 1200x630 概况分享图(PNG 下载)
  - 文件:site/index.html(+standalone)。
- `60eb6cf` [Claude] C3 分步引导:工具菜单触发的高亮聚光导览(独立 tour_v1)
  - 文件:site/index.html(+standalone)。
- `0b6ba49` [作者] Merge pull request #3 ·  合并以上 24 条 Claude 提交入 main。

PR #4 部分(以下 8 条):
- `47b76a1` [Claude] 数据收尾:细类描述地毯式去脏(残留草稿/脚手架/破折号)+ 悬停看全文
  - 文件:site · aggregate.py · data(5f)。
- `0cc0506` [Claude] 说人话:全站文案去术语化 + 维度更名(护城河->AI难替代,落地速度->普及速度)
  - 文件:site/index.html(+standalone)。
- `f7688ee` [Claude] 首屏教程化:主按钮=新手教程(高亮),跳过(变暗),教程后自动展示数据与方法
  - 文件:site/index.html(+standalone)。
- `ef1283d` [Claude] 搜索候选可滚动 + 补高频技术岗别名(前端/后端/UI/大模型/产品经理)
  - 文件:site · data · data/collected · tools(7f)。
- `522c079` [Claude] 对比跨类自由选:去掉同层级限制,任意大类/中类/细类混选
  - 文件:site/index.html(+standalone)。
- `f134ba3` [Claude] 性能:删掉动画层上的 backdrop-filter(消除每帧重算卡顿)
  - 文件:site/index.html(+standalone)。
- `27f56dc` [Claude] #6 2D 自由画布视图:固定/自由切换,自由模式拖拽平移 + 滚轮/双指缩放
  - 文件:site/index.html(+standalone)·  说明:自由画布**初版**(标题里的 #6 是功能编号,非 PR 号)。
- `8e13904` [Claude] 群友新反馈:方块文字内移一点 + 细类详情改为居中弹出(抽屉留给中类)
  - 文件:site/index.html(+standalone)。

### 2026-06-22 ~ 06-23 · PR #4 合并 → 自由画布重做 + 加载提速(PR #5)
- `e707b9a` [作者] Merge pull request #4 ·  合并以上 8 条入 main(06-22)。
- `772e371` [Claude] 教程修复:进教程强制展开抽屉(禁过渡定位准)+ 第4步自动收起抽屉 (06-23)
  - 文件:site/index.html(+standalone)。 ·  (PR #5)
- `d98408a` [Claude] 加载提速:data.cn.js 减肥 16.5%(1.96MB->1.63MB)+ 搜索索引延后 + 加载指示 (06-23)
  - 文件:site · aggregate.py(4f)。 ·  (PR #5)
- `75b1960` [Claude] 自由画布重做:语义缩放嵌套画布(大类间隔加大 + 缩放浮现细类 + 点击展开) (06-23)
  - 文件:site/index.html(+standalone)·  说明:自由画布从平移缩放改为**语义缩放嵌套画布**。 ·  (PR #5)
- `4ff4561` [作者] Merge pull request #5 ·  合并以上 3 条入 main(06-23)。

### 2026-06-23 · 自由画布二次整改 + 全面体检(PR #6)
- `c1ea2c9` [Claude] 自由画布二次整改:点击展开细类 + × 关闭 + 抽屉跟随 + 悬停放大 + 按钮对齐
  - 文件:site/index.html · site/index.standalone.html(2f)
  - 说明:群友 4 点反馈,中类改为点击才展开(去掉自动铺开,性能封顶)、展开中类右上角加 × 关闭、抽屉概况跟随最近展开的中类、画布模式找回悬停微放大、并修掉「固定/自由」按钮的 CSS(ID->class)使其与「面积/维度」分段控件一致。
- `6c096a9` [Claude] 全面体检·数据:细类代表性评价(eval)不再选到被截断的半句
  - 文件:aggregate.py · data/aggregated.cn.json · site/data.cn.js · site/index.standalone.html(4f)
  - 说明:全面体检发现细类「代表性评价」会选到被 140 字截断的半句,改进选句逻辑后重跑聚合。
- `a23ddfa` [作者] Merge pull request #6 ·  合并以上 2 条入 main(06-23)。

### 2026-06-23 · 协作机制落地:WORKLOG + 维护须知(PR #7)
- `8c0f5c6` [Claude] 新增协作改动日志 WORKLOG.md + Claude/Codex 维护须知
  - 文件:WORKLOG.md · CLAUDE.md · AGENTS.md(3f,纯新增文档,未动任何代码/数据)
  - 说明:为与 Codex 共同开发建立单一事实源的改动日志与维护规矩(本条由 Claude 应作者要求创建)。注:本日志自身的「创建/维护」提交属引导性提交,不再逐条自列其后续 commit 哈希(如 `560a7fe` 补记、后续状态刷新),以免哈希自指无限套娃;功能性改动从下一次起按约定逐条记录。
- `da93622` [作者] Merge pull request #7 ·  WORKLOG 引导提交并入 main(06-23)。

### 2026-06-23 · [Codex] 首次提交:Worker 预计算(PR #8 → claude 分支 / PR #9 → main)
- `f6c916f` [Codex] Worker 预计算自由画布布局与搜索索引
  - 文件:site/index.html · site/index.standalone.html · WORKLOG.md(3f)
  - 说明:新增浏览器 Worker 预计算搜索索引与自由画布布局缓存,主线程保留同步兜底与 Canvas 绘制,减少自由画布切换/重算时的主线程压力。这是 Codex 的首次提交。
- `eeb9591` [作者] Merge pull request #8 ·  把该提交同步进 claude 分支(06-23)。
- `97c9195` [作者] Merge pull request #9 ·  同一提交(`f6c916f`)同步进 main(06-23);#8 与 #9 是同一改动分别入两条线,刻意让 claude 分支与 main 都拿到 Codex 进度、互不失联。
- `e1c39eb` [Claude] Merge origin/main into claude/vigilant-babbage-atJ5w(开工前同步)
  - 文件:.github/workflows/deploy.yml(找回此前本分支缺失的部署工作流)
  - 说明:遵守「开工前先同步最新 main」纪律,把 `origin/main`(含 PR #8/#9)合进本分支,确保在最新版本上改动。

### 2026-06-23 · [Codex] 自由画布复位整改(PR #10 → claude 分支)
- `a9fc370` [Codex] 自由画布复位关闭展开并固定全局概况
  - 文件:site/index.html · site/index.standalone.html · WORKLOG.md(3f)
  - 说明:自由画布「复位视图」同步清空已展开中类与悬停状态;顶部抽屉概况不再跟随展开的中类,始终保持全局综合视图。
- `68fd7a1` [作者] Merge pull request #10 ·  并入 claude 分支(06-23);该改动随后再经 PR 流向 main。

---

## 当前状态快照(2026-06-23 刷新)

- **main**:`b2e01b7`(PR #11 合并点);PR #1~#9、#11 已并入。
- **活动分支**:`claude/vigilant-babbage-atJ5w`,已合入最新 `origin/main` 与 Codex 的 PR #10(自由画布复位整改),并叠加本轮 WORKLOG 维护提交,工作树干净。
- **待回流 main**:PR #10 的 `a9fc370` 目前在 claude 分支上,尚未单独流入 main(下次 claude 分支并入 main 时一并带过去)。
- **已知遗留**(launch 后再办):
  - `by_model` 数组化(减小 data.cn.js)。
  - eval(细类代表性评价)懒加载。
  - `site/index.html` 的 CSS/JS 拆分(目前单文件全内联)。
  - 5 条细类 eval 因该细类全部候选均被截断,需重采方能根治。

---

## 给协作方的提醒(同见 CLAUDE.md / AGENTS.md)

- **开工前先同步最新 main**:每次开始改动前,先 `git fetch origin main` 并把当前分支与 `origin/main` 合一次(`--ff-only` 优先,有冲突再正常 merge,不要 rebase),确保是在最新版本上改;**推送/开 PR 前再同步一次**(对方可能已合进新东西)。
- **产物禁破折号**:`site/*.js`、`*.html`、`data/*.json` 等产物不得出现长破折号(em-dash, U+2014)或短破折号(en-dash, U+2013),用 ASCII `-` 或中文标点。
- **改 UI 后重生 standalone**:UI 全在 `site/index.html`;改完务必 `python aggregate.py` 重生 `site/index.standalone.html` 与 `site/data.cn.js`。
- **开发分支**:Claude 在 `claude/vigilant-babbage-atJ5w` 上开发;每次提交前回到本文件追加条目。
- **新条目位置**:时间线条目追加到「时间线」段的**末尾**(即本「当前状态快照 / 给协作方的提醒」两段**之前**),保持时间线连续;这两段是常驻元信息,始终留在文件最末。
