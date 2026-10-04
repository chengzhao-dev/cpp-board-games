# Agent 工作区

`.agents/` 是本项目 Agent 资源的唯一工作区。根目录 `AGENTS.md` 只保留项目级硬约束；本文件负责定位，不重复规则。本目录结构与 cpp-notes 仓库同构（四区 + 同名知识领域目录），统一决策与保留差异见 `skills/governing-agents/references/structure.md` 第 6 节对照表。

## 按任务进入

| 任务 | 入口 |
| --- | --- |
| 维护 Agent 规则、检查脚本与 `.agents/` 结构 | `skills/governing-agents/SKILL.md` |
| C++、CMake、WSL 游戏阶段开发 | `skills/cpp-development/SKILL.md` |
| 棋盘游戏抽象和规则设计 | `skills/game-design/SKILL.md` |
| 测试和验证 | `skills/testing/SKILL.md` |
| Python 脚本、知识库管道与 C++ 衔接工具 | `skills/maintaining-python/SKILL.md`、`skills/python-tooling/SKILL.md` |
| 编写 Quarto 文档和章节 | `skills/writing-quarto/SKILL.md` |
| 调整主题、布局和页面资源 | `skills/designing-theme/SKILL.md` |
| GitHub、提交和发布边界 | `skills/shipping-github/SKILL.md` |
| 只读代码审查 | `skills/reviewing-code/SKILL.md` |
| 领域依据（为什么这样设计） | `knowledge/KNOWLEDGE.md` |
| 跨会话教训（过去哪里易错） | `memory/MEMORY.md` |
| 失败复盘（仅排查时） | `incidents/INDEX.md` |

一次任务只读命中技能的 `SKILL.md` 与其路由指向的文件；完整短路由见 `skills/governing-agents/references/catalog.md`。知识按 `knowledge/KNOWLEDGE.md` 的定点取用表直取 `kb_id`，不通读整个知识库。

## 目录职责

```text
.agents/
├── knowledge/       # 稳定领域事实与「为什么」：<domain>/<subdomain>/<topic>.md；入口 KNOWLEDGE.md
├── memory/          # 跨会话教训；入口 MEMORY.md
├── incidents/       # 失败复盘，仅排查时读；入口 INDEX.md
├── mcp/             # 项目级 MCP server 与说明
├── skills/          # 可复用流程；每个 skill 含 SKILL.md、agents/openai.yaml，按需 references/、scripts/、assets/
└── README.md        # 本导航
```

规则只保留一份权威来源：流程放 `skills/`，设计原因放 `knowledge/`，历史经验放 `memory/`，失败案例放 `incidents/`。知识库索引产物写入根目录 `temp/knowledge-index/`，不入库。不要把临时计划、构建产物或缓存放进本目录。

## 运行入口

统一入口是 `skills/governing-agents/scripts/run.ps1`（Python 侧 `run.py`）。子命令以 `run.py` 文件头为准，这里不复制命令表。解释器只读根目录 `config.toml` 的 `python`。

脚本不得从当前工作目录推断仓库根；移动或新增脚本后，必须检查 `Path(__file__)` 的根目录解析，并更新所有统一入口、测试和文档引用。

游戏代码按编号阶段目录组织在 `games/<game>/` 下：每个阶段（如 `01-cli-game/`）是拥有自身 `.clang-format`、`.vscode/`、构建和测试的完整项目，配置归属阶段目录本身；格式模板在 `skills/cpp-development/assets/config/.clang-format`；判断依据见 `knowledge/agent-workspace/navigation/staged-game-layout.md`。
