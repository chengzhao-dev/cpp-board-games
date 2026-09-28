# Skills 目录索引

本文件只做短路由，控制在 3000 字符以内。普通任务先读命中的 `SKILL.md`，再按其中的局部路由读取必要 reference，不加载完整索引。

## skill 与 knowledge 的分工

同一个知识点只允许有一个出处：怎么做（流程、格式约定、硬约束）留 `references/`，为什么（领域结论与取舍依据）进
`.agents/knowledge/`。`references/` 优先写稳定 `kb_id`，确需检索时再给一行带 `--domain` 的 `run.ps1 kb-search`
入口，不复制知识正文。

新增或迁移 `.agents/knowledge/` 文件后运行 `kb-index`、`kb-check` 和 `kb-eval`。索引产物统一放在 `temp/`，缺失时脚本会自动重建。

## L1 入口（每次只读命中的那一个）

| Skill | 管什么 | 不适用时转交 |
|---|---|---|
| `governing-agents/SKILL.md` | Agent 运行入口、Skills 分层、MCP、仓库重构与统一验收 | 写正文转 `writing-quarto`，改样式转 `designing-theme` |
| `reviewing-code/SKILL.md` | Defect-First 只读审查游戏代码与文档 | 需要动手改文件时转对应内容 skill |
| `cpp-development/SKILL.md` | 游戏阶段代码、CMake 工程与阶段路由表 | 页面结构转 `writing-quarto`，样式转 `designing-theme` |
| `shipping-github/SKILL.md` | git 工作流、提交身份、Pages 发布与 CI 操作清单 | 正文与 skill 内容改动转对应 skill |
| `maintaining-python/SKILL.md` | 本仓库 Python 工具、知识库管道、脚手架与运行时选择 | 检查项编排转 `governing-agents`，知识正文转 `.agents/knowledge/` |
| `writing-quarto/SKILL.md` | `.qmd` 正文写法、Book 结构、中文技术文档格式 | 渲染参数取值转 `designing-theme`，游戏语义转 `game-design` |
| `designing-theme/SKILL.md` | HTML 主题、设计令牌与布局契约 | 正文写法与 `.qmd` 结构转 `writing-quarto` |
| `game-design/SKILL.md` | 棋盘、棋子、动作与规则的建模依据 | 工程结构转 `cpp-development`，页面写法转 `writing-quarto` |
| `testing/SKILL.md` | C++、Python 与文档的分层验证与验收矩阵 | 实现细节转 `cpp-development` |
| `python-tooling/SKILL.md` | Python 脚本与 C++ 棋盘游戏衔接 | 工具链维护转 `maintaining-python` |

## 详细路由

- 游戏阶段与章节文件的对应关系以 `cpp-development/references/stages/<game>.md` 阶段路由表为准，由 `scope` 自动选中。

- `.agents/knowledge/<领域>/`：领域目录为名词 kebab（`agent-workspace`、`cpp-teaching`、`quarto-writing`），`domain` 字段取同名领域目录值，`subdomain` 取同名子域目录值。`visual-theme/`（designing-theme）与 `repo-github/`（shipping-github）在出现第一个文件时再创建。
- `.agents/knowledge/KNOWLEDGE.md`：知识库规范和新增流程。新增或迁移知识后运行 `kb-index`、`kb-check` 和 `kb-eval`。
- `.agents/knowledge/agent-workspace/retrieval/retrieval-governance.md`：skills、knowledge、memory、incidents 与 MCP 的职责边界，以及统一检索协议。
- `writing-quarto/references/zh/writing-principles.md`：所有中文文档任务的最高优先规则。
- `writing-quarto/references/zh/chapter-writing.md`：章节骨架、页面类型与新手成功路径。

普通任务只读取命中的 `SKILL.md`、目标文件和其中明确要求的 reference。需要了解知识文件规范时读取 `.agents/knowledge/KNOWLEDGE.md`，不维护第二份手工目录。
