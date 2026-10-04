# .agents/knowledge/ 知识库

本目录是领域依据的唯一出处：回答「为什么这样配置、为什么这样设计、为什么会失败」。目录名是名词 kebab 领域名，与对应技能的功能域对应。
「skill 与 knowledge 怎么分工」的权威定义在 `.agents/skills/governing-agents/references/catalog.md`「skill 与 knowledge 的分工」，本文件只引用不复制。

## 目录结构（领域路由）

```text
.agents/knowledge/
├── agent-workspace/ # Agent 工作区、规划、导航与检索治理（技能：governing-agents）
│   ├── navigation/  # 仓库与阶段目录结构
│   ├── planning/    # 项目决策、路线与开发流程
│   └── retrieval/   # 检索协议与四区职责边界
├── cpp-teaching/    # C++ 工程与风格依据（技能：cpp-development）
│   ├── style/       # 注释、终端输出与 Google C++ 风格决策
│   ├── toolchain/   # 工具链、CMake 与环境
│   └── cases/       # 正反对照（正确/不佳/改写）；appendix/ 不进索引
└── quarto-writing/  # Quarto 写作与渲染依据（技能：writing-quarto）
    ├── rendering/   # include、链接与 Mermaid 等渲染层约定
    ├── writing/     # 章节骨架、标题、元素与中文风格的取舍与差异
    └── cases/       # 正反对照（正确/不佳/改写）；appendix/ 不进索引
```

`cases/` 放正反对照，一条对照的检索单元是「正确 + 不佳 + 改写」；规范条文留在 `writing/`、`style/` 等条文叶子。`cases/appendix/` 是低频人审附录：索引、检索、评测与校验全部跳过，仅人审或用户点名时读。

`visual-theme/`（技能：designing-theme）与 `repo-github/`（技能：shipping-github）在出现第一个文件时再创建，不建空目录。文件名与目录名一律纯 ASCII kebab-case。

写作类任务先读 `writing-quarto` 技能的 `references/`（通用 how），再按 `kb_id` 取本目录的差异与依据；两层的分工见 `catalog.md`「skill 与 knowledge 的分工」。

## 按任务定点取用

先在对应技能的任务路由中定位，再按下表直取 `kb_id`，不通读知识库：

| 任务 | kb_id |
| --- | --- |
| 写或评审各阶段 CMakeLists.txt | `bg-cmake-conventions-v1` |
| 写代码注释、终端输出与日志 | `bg-comment-style-v1`、`bg-terminal-output-style-v1` |
| 写或改 `.clang-format` / `.clang-tidy` / `.clangd` 注释 | `bg-comment-style-v1`（「工具配置 YAML」）、对照 `bg-comment-cases-v1` |
| 判定 clang-tidy 门禁范围、`at()` 与下标检查 | `bg-static-analysis-boundaries-v1` |
| 写或评审异常边界与 `what()` 文案 | `bg-exception-message-format-v1`、`bg-google-cpp-style-v1` |
| 写或评审 C++ 标识符命名与风格 | `bg-google-cpp-style-v1` |
| 判断阶段目录命名与配置归属 | `bg-staged-game-layout-v1` |
| 判断阶段顺序、门槛与测试框架时机 | `bg-roadmap-v1` |
| 判断架构、共享库与外部依据 | `bg-project-decisions-v1` |
| 写或评审代码旁白的工程叙事范围（语言课禁令） | `bg-project-decisions-v1`、`bg-chinese-style-cases-v1` |
| 写游戏开篇/收官章与 STAR 摘要 | `bg-engineering-storyline-v1` |
| 确认 WSL、VS Code 与工具链环境 | `bg-development-environment-v1` |
| 检索协议与四区职责边界 | `bg-retrieval-governance-v1` |
| 判断技能分层、AGENTS.md 体量与参考目录为什么不拍平 | `bg-skills-engineering-v1` |
| 写或改章节骨架、标题与自测 | `bg-chapter-page-pattern-v1`、`bg-file-title-naming-v1` |
| 查句段与措辞的正反对照 | `bg-chinese-style-cases-v1`（核心）、低频章级对照在 `cases/appendix/` |
| 查 Quarto 元素写法正反对照 | `bg-qmd-elements-cases-v1`（元素细则见 `bg-qmd-element-cases-v1`） |
| 查注释写法正反对照 | `bg-comment-cases-v1`（条文见 `bg-comment-style-v1`） |
| 查标识符命名正反对照 | `bg-naming-cases-v1`（规则见 `bg-google-cpp-style-v1`） |
| 查类内与命名空间作用域声明顺序 | `bg-declaration-order-v1` |
| 写代码块、列表、表格与 Callout | `bg-qmd-element-cases-v1` |
| 核对篇幅预算 | `bg-content-budget-v1` |
| 改写句段、措辞与列表 | `bg-chinese-style-cases-v1`、`bg-paragraph-list-style-v1` |
| 统一语气与语域（口语腔、公文腔、规划元叙述、压缩隐喻） | `bg-chinese-voice-register-v1` |
| 判断代码与图的放置节奏（一图一事、同主题相邻、拆节） | `bg-qmd-element-cases-v1`，依据见 `bg-section-focus-density-v1` |
| 衔接段落与小节过渡 | `bg-paragraph-cohesion-v1` |
| 查术语与禁用词 | `bg-terminology-v1` |
| 处理 include 与链接 | `bg-quarto-conventions-v1` |
| 写或改 Mermaid 图表 | `bg-mermaid-conventions-v1` |
| 画坐标轴类网格图（棋盘行列、二维下标） | `bg-coords-diagram-v1` |
| 权衡小节密度与盒子比例 | `bg-section-focus-density-v1` |
| 写代码块与图（mermaid/python 坐标图）之间的桥接正文 | `bg-qmd-element-cases-v1`、`bg-coords-diagram-v1`，对照见 `bg-qmd-elements-cases-v1` |
| 改写目录式堆砌（引言交付物清单、树后复述） | `bg-chinese-style-cases-v1`「目录式堆砌」 |
| 判断块后正文与代码注释的分工、单段是否混对象 | `bg-qmd-element-cases-v1`，对照见 `bg-chinese-style-cases-v1`「块后复述注释」「单段混并列对象」 |
| 判断同节递进代码块是否合并、多围栏导语形态 | `bg-qmd-element-cases-v1`，对照见 `bg-chinese-style-cases-v1`「递进片段合并」「多代码块一句导语」 |

## 文件规范（强制）

frontmatter 字段（与 cpp-notes 同一标准）：

| 字段 | 必填 | 作用 |
|---|---|---|
| `kb_id` | 是 | 全局唯一，格式 `bg-<area>-<topic>-v<N>`（如 `bg-cmake-conventions-v1`）；改名等于新建知识，历史 id 保持不改名 |
| `title` | 是 | 文档级标题，与正文唯一 H1 一致 |
| `domain` | 是 | 检索预过滤维度，取同名领域目录值 |
| `subdomain` | 建议 | 同一领域内的主题筛选，取子域目录名 |
| `tags` | 建议 | 概念标签列表，用于冲突检测与图谱连线 |
| `level_range` | 建议 | 面向读者的难度区间 |
| `dependencies` | 建议 | 前置知识的 `kb_id` 列表 |
| `supersedes` | 版本替换时必填 | 被替代的 `kb_id` |
| `created` / `updated` | 是 / 是 | 日期字符串；`updated` 变化表示内容有修订 |
| `chunk_strategy` | 是 | 目前只有 `semantic_heading` |
| `estimated_tokens` | 建议 | 人工估计值，实际预算以索引测得为准 |

正文结构：

1. 全文只有一个 `# H1`，与 `title` 一致。
2. `##` 是 Parent Chunk 边界，`###` 是 Child Chunk 边界。
3. 每个 `###` 下必须有正文：只有标题没有内容的壳块会被分块器丢弃。
4. 不复述 skill 侧的流程约定。需要指向别处时写「见标识 `<kb_id>` 的知识文件」；指向技能侧写「见 `<skill>` 的 …」。
5. 表格不超过 30 行，禁止段落中间的 HTML 锚点跳转。

## 检索不变量

1. 不产出无正文的标题壳 Child。不产出与 Parent 逐字节相同的 Child。
2. 每个 Child 都带 `[标题路径] ` 前缀，保证独立可判读。
3. 检索器交给 LLM 的是 Parent 回溯后的结果，评测口径必须与之一致。
4. 中文分词取二元组，ASCII 标识符整体保留并拆下划线，语言关键字永不作为停用词。
5. 冲突候选按全库文档级概念集合（`tags` ∪ 反引号内的严格标识符）的 Jaccard 判定，并跳过已被 `supersedes` 关联的一对。

## Token 预算与增长

知识文件不设整文件大小上限，避免把内聚主题机械拆散。实际约束放在检索单元：默认单次检索最多使用 4000 Token，上下文硬上限为 6000 Token，任一 live Parent Chunk 不得超过 4000 Token。

新增或扩容前先更新已有知识。同一主题需要更多细节时，按 `##` 的独立概念边界扩容；一个父块超过 4000 Token 时，先压缩重复表述，再按可独立检索的概念拆分。每次新增 `kb_id` 都要在 `eval_set.py` 补查询，让召回率与注入预算接受自动评测。

## 索引与验证

```powershell
& .agents/skills/governing-agents/scripts/run.ps1 kb-index            # 增量（按 content_hash 跳过未变文件）
& .agents/skills/governing-agents/scripts/run.ps1 kb-index --rebuild  # 改分词或结构后全量重建
& .agents/skills/governing-agents/scripts/run.ps1 kb-check            # 格式违规、重复、孤立、断链、P95 延迟
& .agents/skills/governing-agents/scripts/run.ps1 kb-eval             # Top-5 召回率与注入 Token 预算
& .agents/skills/governing-agents/scripts/run.ps1 kb-search "<查询>" --domain quarto-writing --explain
```

产物写在 `temp/knowledge-index/`（已 gitignore，缺失时 `run.py` 的 kb-* 子命令自动重建）。管道代码在 `.agents/skills/maintaining-python/scripts/`：
`kb_common.py` 公共工具、`chunker.py` 语义分块、`indexer.py` FTS5、向量与图谱索引、
`retriever.py` 混合检索与 Parent 回溯、`evaluator.py` 与 `eval_set.py` 评测、`check_health.py` 体检、
`test_conflict_detection.py` 锁住「重合度 → 检索降权」链路（已接入 `check --profile knowledge`）。
检索协议与四区职责边界见标识 `bg-retrieval-governance-v1` 的知识文件。

## 新增知识的最小闭环

1. 建文件或更新唯一权威，按上表写 frontmatter；领域与子域目录随文件生长，不预建空目录 → `kb-index` → `kb-check`（重复与 Parent 超限必须为 0）。
2. 在上方目录树的对应领域补充说明（新领域才改树），并同步引用方（交叉引用一律用 kb_id）。
3. 在 `.agents/skills/maintaining-python/scripts/eval_set.py` 补该文件的查询条目，让召回率可验证而不是自我声明。
4. 精简对应的 skill reference，只留怎么做和一行 `kb-search` 入口；详细取舍依据留在 knowledge。
5. 更新 `.agents/skills/governing-agents/references/catalog.md` 短路由，最后按改动域运行 `run.py check --profile ...`。
