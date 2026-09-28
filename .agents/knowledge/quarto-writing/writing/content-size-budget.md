---
kb_id: "bg-content-budget-v1"
title: "content 篇幅的 token 预算"
domain: "quarto-writing"
subdomain: "writing"
tags: [size-budget, token, density, length]
level_range: [0, 5]
dependencies: [bg-chapter-page-pattern-v1, bg-section-focus-density-v1, bg-qmd-element-cases-v1]
created: "2026-09-27"
updated: "2026-09-28"
chunk_strategy: "semantic_heading"
estimated_tokens: 800
---

# content 篇幅的 token 预算

起因是 02 章连环出现凑字数句、复述导航段和长注释片段：逐条句式规则拦得住具体坏句，拦不住「每一句都合规但整页过量」。本预算给每种层级一个硬上限，由 `writing-quarto` 技能的 `verify_content.py` 第 3 查「篇幅预算」自动执行，超限即为失败。

## 计数口径

估算 token = 中日韩字符数 × 1.5 + 其他字符数 ÷ 4。公式对主流分词器（GLM、Claude、GPT）取保守上界，只用于预算比较，不声称等于真实 token 数。

- 正文、列表、表格、代码块、图表（Mermaid 与文本图）全部计入；YAML frontmatter 不计。
- Markdown 链接只计入锚文本，URL 不计入：GitHub 绝对链接的 URL 是机器寻址字符串，读者扫读时整体跳过，计入会挤占正文预算并与「仓库内一律 GitHub 绝对链接」的约定冲突；`verify_content.py` 在计数前剥离链接 URL，锚文本照常计入。
- 字符数按 Unicode 字符计：汉字、全角标点各算 1 个字符，归入中日韩一侧。

## 分层上限

| 层级 | 上限 |
| --- | --- |
| 整章（frontmatter 外全部内容） | 5000 token |
| 无标题引言（首个 `##` 之前） | 400 token |
| 单个 `##`（含其下全部 `###`） | 1800 token |
| 单个 `###`（含其代码块） | 600 token |
| 每个 `##` 下 `###` 数量 | 4 个 |
| 单个代码块（围栏内内容行） | 20 行 |
| 单个正文段落（代码块、表格、列表与标题之外的连续文本段） | 220 token |
| 代码片段内注释 | 每处 ≤2 行，单行 ≤40 字；命令型片段每条命令保留一行意图注释 |

数字依据：没有规定章节字数的权威国标（GB/T 7713《科技报告编写规则》只管结构格式）；技术写作社区实践是单节对应 3-5 分钟阅读（约 1500-3000 字）、单个功能模块 800-1200 字，超限优先拆分。按 CJK×1.5 换算，整章 5000 token 约合 3300 汉字的正文当量，是「一节一件事、一章四节左右」的自然边界。

## 执行方式

- `verify_content.py` 第 3 查按上表逐文件、逐节、逐代码块、逐正文段落核对，超限即整体失败；限额调整只改该脚本的常量与本表，两处必须同步。
- 根目录 `index.qmd` 与 `content/<game>/index.qmd`（YAML 含 `body-classes: index-page`）是着陆页：短引言与卡片网格不是章节引言，只核对整章总量与代码块限额，不做引言与分节限额。
- 结构性规则（引言构成、`###` 数量）同时受标识 `bg-chapter-page-pattern-v1` 的知识文件约束；本表提供量化兜底。
- 接近上限不是目标：预算是硬顶，内容仍按凑字数禁令与密度规则精简（见标识 `bg-paragraph-list-style-v1` 的知识文件）。
