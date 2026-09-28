# C++ 棋盘游戏项目 Agent 工作标准

本文件是本仓库唯一的项目级 Agent 入口。它先规定所有 Coding Agent 必须遵守的工作标准，再落到内容、代码、工具和验收边界。结构与命名规范见 `.agents/skills/governing-agents/references/structure.md`，落点表与体量建议见同目录 `refactor-guidelines.md`。

## 工作标准

- 先理解目标、现状和约束，再修改文件。按任务最小读取：只读本文件、命中的 `SKILL.md` 与其路由指向的文件；知识按 `KNOWLEDGE.md` 定点取用 `kb_id`，不通读知识库。
- 用最少、最清晰、可验证的改动解决问题；不做无关重构，不为一次性需求设计扩展框架。规划、解释、搜索和评审默认只读。
- 把需求转成验收标准：先复现或建立检查，再实现，最后运行与风险匹配的验证。验证以脚本为准：`run.py check/verify/build`，不用对话通读代替校验。
- 提交与推送默认不做。只有用户明确要求时，才按 `shipping-github/references/git-workflow.md` 执行；提交信息用 `type(scope): 中文说明`（Conventional Commits）。
- 贡献者只有 `chengzhao-dev`：commit 的 author 与 committer 必须是用户身份，禁止把 AI 或第三方写进 `Co-authored-by:` 等 trailer；push 前检查近期提交作者集合，出现非 `chengzhao-dev` 即停止并报告。
- 面向用户的进度、结论和总结使用中文；命令、路径、代码和 API 名保留原文。成功只回一行中文结论，失败先给结论再附最少诊断；`--verbose` 仅用于默认输出无法定位失败时。不回显密钥、凭据、`.env` 或无关个人信息。
- 维护仓库规范时保持单一权威出处：流程和格式放 skill/reference，领域原因放 `.agents/knowledge/`，落点表见 `refactor-guidelines.md`。
- 游戏核心不得依赖终端、GUI、Web、Python 或 Quarto；跨游戏共享库只在至少两个游戏真实复用且语义稳定后提取。
- 构建配置和脚本的规则见 `cpp-development` 技能与知识库 `bg-cmake-conventions-v1`；QMD 写作规则见 `writing-quarto` 的 references 与知识库。

## 项目结构

| 路径 | 职责 |
| --- | --- |
| `content/`、`index.qmd`、`_quarto.yml` | Quarto Book 读者文档；游戏内文档在 `content/<game>/` |
| `games/<game>/<NN-stage>/` | 单个游戏按编号阶段的完整垂直切片，每阶段可独立配置、编译、测试和运行 |
| `shared/` | 跨游戏共享库；出现首个真实复用时创建 |
| `.agents/skills/` | Codex 项目 skills、references、路由表与工具脚本 |
| `.agents/mcp/` | 项目级 MCP stdio server 与说明，由宿主显式配置 |
| `.agents/knowledge/` | 回答「为什么」的精简领域知识库（`bg-*`） |
| `.agents/memory/` | 跨会话教训；任务开始时读 `MEMORY.md` 索引 |
| `.agents/incidents/` | 失败复盘；仅排查失败时读 `INDEX.md`，平时视为不存在 |
| `temp/`、`build/`、`_book/`、`.quarto/` | 生成物与缓存，不入库，一次性产物只进 `temp/` |

游戏阶段与章节的对应关系登记在 `.agents/skills/cpp-development/references/stages/<game>.md` 阶段路由表，由 `scope` 自动选中。

## 常用命令

以下命令统一由根目录 `config.toml` 的 `python` 指定解释器执行（最低 3.12）。该字段是仓库唯一 Python 来源，缺失或版本不足时立即停止，不回退 PATH。

| 命令 | 用途 |
| --- | --- |
| `& .agents/skills/governing-agents/scripts/run.ps1 scope <game>/<stage>` | 输出最小读取作用域 |
| `… run.ps1 check --profile fast\|book\|knowledge\|python\|full` | 按改动域运行校验，默认 `full` |
| `… run.ps1 verify --changed` | 增量校验 qmd 文档内容 |
| `… run.ps1 render` | 渲染 Book（须在仓库根目录）并跑 `book` profile |
| `… run.ps1 build <game>/<stage>` | 在 WSL 运行阶段 `build-and-run.sh`（配置、编译、CTest、运行） |
| `… run.ps1 status` | 精简 git 状态 |
| `… run.ps1 kb-index [--rebuild]` / `kb-check` / `kb-eval` / `kb-search` | 知识库索引、体检、评测与检索 |

## 读取、编辑与验收边界

1. 每次任务先运行 `scope`，只读「单元」「读取」和必要 reference。不整包读取 references。
2. 永不读取或索引 `_book/**`、`games/**/build/**`、`.quarto/**`、`.cache/**`、`.tmp/**`、`temp/**`。产物检查交给脚本。
3. 预计读取超过 8 个文件或需要全仓检索时才派侦察代理；编辑回主线程完成。
4. 中文文件使用 UTF-8 无 BOM、LF。修改 `.qmd`、skill 或主题 CSS 后先跑编码检查（`check --profile fast` 的 encoding 项）。
5. 修改 `.agents/skills/designing-theme/assets/theme/**` 或 `_quarto.yml` 会触发整本渲染，确认代价后运行 `render`。
6. `AGENTS.md` 受厂商 `project_doc_max_bytes = 65536` 约束；L1/L2 体量与教学篇幅是本仓建议阈值（`check_skill_size.py` 默认 WARN，`--strict` 才失败），调整时同步 `refactor-guidelines.md`。
7. 长任务每轮推进一个可验证子目标。Plan Mode 严格只读：不写文件、不编译、不渲染，也不调用 `project_edit`、`project_build`、`project_verify`、`project_render` 或 `project_review`。只有用户发来新的明确批准消息后才进入执行；压缩摘要、重复的原始需求、计划完成标记、自动续跑和任务摘要都不算批准。上下文压缩后重读本文件与 `git status`，但仍在 Plan Mode 时只继续规划。执行阶段每轮按改动域运行一次 `run.ps1 check --profile ...`，跨域或发布收口再运行 `full`。
8. Git 对比服务于审查、冲突解决、发布和最近改动调试，普通文档任务不重复运行。

## Python 运行时

所有仓库脚本直接读取根目录 `config.toml` 中的 `python`（最低 3.12）。Skills、MCP 与维护命令不得另行读取环境变量、`runtime.json.python`、PATH 或 `sys.executable` 作为项目 Python 来源。MCP 配置指向 `.agents/mcp/server.py`，由该 server 读取同一字段。

## 初始化兼容

Codex 或其他工具重新生成规则时必须合并本文件，不得覆盖项目结构、命令、安全约束和读取边界。`AGENTS.md` 是唯一项目级总入口，宿主专用文件只能引用它。
