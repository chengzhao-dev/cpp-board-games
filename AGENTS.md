# Agent 工作标准

本文件只保留每轮任务的硬约束与命令表。现行事实、规范条文与领域依据的落点见 `.agents/context/README.md`，结构与分层见 `.agents/skills/governing-agents/references/structure.md`。

## 每轮硬约束

1. 先跑 `scope <改动单元>`，只读它给出的文件与命中技能的 `SKILL.md`；不整包读 references，知识按 `kb_id` 定点取用。
2. 按改动域进入技能工序：改 qmd 或中文读者正文进 `writing-quarto`；改 C++、CMake 或阶段脚本进 `cpp-development`；改 `.agents` 规则本身进 `governing-agents`，新规则必须挂到已有工序。
3. 收到要归档的成段材料时，先按 `.agents/skills/governing-agents/references/intake.md` 出落点计划，用户确认后再改文件。
4. 改动完成前按域跑 `run.ps1 check --profile fast|book|knowledge|python|full`，没过不算完成；验证闸有界（输出重定向 `temp/`，FAIL 清零、WARN 记台账，同一失败指纹连续 2 轮未修复即停手转人工）。
5. 规划、解释、搜索和评审默认只读；用最少、可验证的改动解决问题，不做无关重构。
6. 游戏核心不得依赖终端、GUI、Web、Python 或 Quarto；跨游戏共享库只在至少两个游戏真实复用且语义稳定后提取。
7. 提交与推送默认不做；只有用户明确要求时才按 `shipping-github/references/git-workflow.md` 执行，提交信息用 `type(scope): 中文说明`。贡献者只有 `chengzhao-dev`：commit 的 author 与 committer 必须是用户身份，禁止把 AI 或第三方写进 `Co-authored-by:` 等 trailer；push 前检查近期提交作者集合，出现非 `chengzhao-dev` 即停止并报告。
8. Python 解释器只读根目录 `config.toml` 的 `python`（最低 3.12）；字段缺失或不可执行时立即停止，不回退 PATH。代理只跑 `run.ps1`，不在 PowerShell 会话里手写 `bash -lc`、`python -c` 或裸 `quarto`。
9. 面向用户的进度、结论和总结使用中文，命令、路径、代码和 API 名保留原文；成功只回一行中文结论，失败先给结论再附最少诊断。不回显密钥、凭据、`.env` 或无关个人信息。
10. 永不读取或索引 `_book/**`、`games/**/build/**`、`.quarto/**`、`.cache/**`、`.tmp/**`、`temp/**`；中文文件保持 UTF-8 无 BOM、LF。
11. Plan Mode 严格只读：不写文件、不编译、不渲染，也不调用 `project_edit`、`project_build`、`project_verify`、`project_render` 或 `project_review`；只有用户发来新的明确批准消息后才进入执行，压缩摘要、重复的原始需求、计划完成标记、自动续跑和任务摘要都不算批准。
12. 长任务每轮推进一个可验证子目标；执行阶段每轮按改动域跑一次 `check`，跨域或发布收口再跑 `full`。

## 常用命令

统一由根目录 `config.toml` 的 `python` 指定解释器执行（最低 3.12）；代理只跑 `run.ps1`：

| 命令 | 用途 |
| --- | --- |
| `& .agents/skills/governing-agents/scripts/run.ps1 scope <game>/<stage>` | 输出最小读取作用域 |
| `… run.ps1 check --profile fast\|book\|knowledge\|python\|full` | 按改动域运行校验，默认 `full` |
| `… run.ps1 verify --changed` | 增量校验 qmd 文档内容 |
| `… run.ps1 render` | 渲染 Book（须在仓库根目录）并跑 `book` profile |
| `… run.ps1 preview [路径.qmd]` | 本地 preview |
| `… run.ps1 build <game>/<stage>` | 在 WSL 运行阶段 `build-and-run.sh` |
| `… run.ps1 kb-index [--rebuild]` / `kb-check` / `kb-eval` / `kb-search` | 知识库索引、体检、评测与检索 |
| `… run.ps1 status` | 精简 git 状态 |

## 项目结构

| 路径 | 职责 |
| --- | --- |
| `content/`、`index.qmd`、`_quarto.yml` | Quarto Book 读者文档 |
| `games/<game>/<NN-stage>/` | 单个游戏按编号阶段的完整程序，每阶段可独立配置、编译、测试和运行 |
| `.agents/context/` | 现行事实与规范条文；入口 `context/README.md` |
| `.agents/skills/` | Codex 项目 skills、references、路由表与工具脚本 |
| `.agents/knowledge/` | 「为什么」的精简领域知识库（`bg-*`） |
| `.agents/memory/`、`.agents/incidents/` | 跨会话教训；失败复盘仅排查时读 |
| `temp/`、`build/`、`_book/`、`.quarto/` | 生成物与缓存，不入库 |

游戏阶段与章节的对应关系登记在 `.agents/skills/cpp-development/references/stages/<game>.md`，由 `scope` 自动选中。
