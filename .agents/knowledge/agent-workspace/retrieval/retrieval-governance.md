---
kb_id: "bg-retrieval-governance-v1"
title: "检索与分区职责边界"
domain: "agent-workspace"
subdomain: "retrieval"
tags: [retrieval, context, knowledge, mcp, scope]
level_range: [0, 5]
dependencies: []
created: "2026-09-28"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 1100
---

# 检索与分区职责边界

本文件供 Agent 判断 skills、context、knowledge、memory、incidents 与 MCP 各自承载什么、检索协议怎么走。目录结构以 `<skill>` 的 `structure.md` 为准，本文件只回答「去哪里找、怎么检索」。

## 职责边界

| 区 | 承载 | 进入上下文的方式 |
| --- | --- | --- |
| `skills/*/SKILL.md` | 任务路由、P0、判据 | 命中任务时整篇读取 |
| `skills/*/references/` | 可执行 how（步骤、清单、本仓约定） | 按 SKILL 路由读取 |
| `.agents/context/` | 现在是什么、现在怎么做（现行事实与规范条文），`kb_id` 唯一标识 | 按任务打开 `context/README.md` 路由的那个文件 |
| `.agents/knowledge/` | 为什么 / 取舍 / 正反例，`kb_id` 唯一标识；正反对照在领域下 `cases/`，其 `appendix/` 仅人审 | 按 `KNOWLEDGE.md` 定点取用，或 `kb-search` |
| `.agents/memory/` | 跨会话教训 | 任务开始时读 `MEMORY.md` 索引 |
| `.agents/incidents/` | 失败复盘 | 仅排查失败时读 `INDEX.md`，不进检索索引 |
| `.agents/mcp/` | 结构化工具入口 | 宿主显式配置，不假设自动发现 |

同一知识点只允许一个出处；context 与 knowledge 同库索引（chunk 带 `zone=context|knowledge`），同一 `kb_id` 只落一个文件。检索命中两处重复表述时，先信 zone=context 的条文，knowledge 只作取舍依据。

## 统一检索协议

- 单次知识检索默认注入不超过 4000 Token，硬上限 6000 Token；任一 live Parent 不超过 4000 Token。
- 优先定点取用：`context/README.md` 与 `KNOWLEDGE.md` 的任务表给出 `kb_id`，直接读文件比检索省 token。
- 需要模糊检索时走统一入口：

```powershell
& .agents/skills/governing-agents/scripts/run.ps1 kb-search "<查询>" --zone context --domain agent-workspace --explain
```

- `--domain` 取文件 frontmatter 的 `domain` 字段值（本仓为 `agent-workspace`、`cpp-teaching`、`quarto-writing`）。
- `--zone` 取 `context`、`knowledge` 或默认 `all`；默认排序 context 加权 1.2、knowledge 1.0，让「现在怎么做」先于正反例。
- MCP 侧对应 `knowledge_search` 工具，参数（含 `zone`）与预算上限一致。

## 评测闭环

改知识库正文、frontmatter、分词或融合参数后，不能只靠 `kb-search` 抽查：按 `kb-index --rebuild` → `kb-check` → `kb-eval` 顺序收口。标注集在 `.agents/skills/maintaining-python/scripts/eval_set.py`，新增 `kb_id` 必须补查询条目，让召回率可验证而不是自我声明。评测口径与交付给 LLM 的内容一致（Parent 回溯后的结果）。

评测闭环的固定裁决：阈值保持 92%，不靠下调阈值换通过；一个答案在期望片段与知识正文之间只留一个权威，标题改名或内容搬家后同步 `eval_set.py`，不为召回堆关键词；纯本文件锚点目录（正文只有指向本文锚点的链接列表的整节）不单独成块，分块器按形态丢弃。召回过线后为某一节补检索查询时，确认它命中且总分仍不低于 92%。

索引产物在 `temp/knowledge-index/`（不入库，缺失时 `run.py` 的 kb-* 子命令会自动重建）。
