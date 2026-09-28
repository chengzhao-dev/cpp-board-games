# 重构与体量准则

重构以行为守恒和可验证契约为最终裁决：公共 CLI、MCP 工具名、`description`、参数 Schema 与返回结构保持兼容。

## 权威出处规则（落点表）

同一规则只允许一个权威正文；新增或迁移前先按下表判定落点，两处都有时删掉非权威的一份：

| 落点 | 放什么 | 禁止 |
| --- | --- | --- |
| `AGENTS.md` | 项目级硬约束、结构、命令表 | 长 why、评审清单、写作细则 |
| `skills/*/SKILL.md` | 路由 + P0 + 判据（L1 预算内） | 复制 knowledge 正文 |
| `skills/*/references/` | 可执行 how（步骤、清单、本仓约定） | 与 knowledge 双写完整规则 |
| `knowledge/` | 稳定 why / 取舍；本仓差异 `bg-*` | 流程步骤、命令表 |
| `content/**/*.qmd` | 面向读者的设计与过程 | Agent 内部路径与脚本细节 |
| `memory/` / `incidents/` | 教训 / 失败复盘 | 当作常规路由 |
| 脚本 | 强制执行 | 当文档通读 |

跨仓：通用 why 可链 cpp-notes 的 GitHub `cpp-*`；本仓索引与 eval 只认 `bg-*`。

## 分层加载契约（预算按本仓可调，不与 cpp-notes 对齐数字）

| 层 | 内容 | 建议阈值 | 判定 |
| --- | --- | --- | --- |
| L0 `AGENTS.md` | 项目结构、命令、硬约束 | ≤65536 字节（厂商硬约束） | `check_skill_size.py` |
| L1 `*/SKILL.md` | 职责、适用场景、路由、P0、流程、判据 | 建议 ≤45 行且 ≤3000 字符 | 同上；默认 WARN，`--strict` 才失败 |
| L2 `*/references/**/*.md` | 单一主题的 P1/P2 细则与按需知识 | 建议 ≤160 行且 ≤6000 字符 | 同上；内聚的单一主题不为过线机械拆分 |
| 教学 QMD | 单一读者任务、直接可读的叙述与指令 | token 预算见 `bg-content-budget-v1` | `verify_content.py`；超限时先判断内容是否必要，再拆分或上调本仓阈值 |

`name` ≤64 字符、`description` ≤1024 字符、全部 skill 的 `name + description` ≤8000 字符是厂商级硬约束。调整建议阈值时同步修改 `check_skill_size.py` 常量与本表，两处保持一致。

知识库不以整文件大小设硬上限，而以检索单元为边界：默认每次最多注入 4000 Token，硬上限 6000 Token，任一 live Parent 不得超过 4000 Token。这样保留内聚主题，同时约束真正进入上下文的内容。

## SKILL.md 统一骨架

必选段落按固定顺序出现，让 agent 用标题即可定位，不必通读：

1. H1 后一句职责与边界（负责什么、交给谁）。
2. `## 适用场景`：正向触发条件 + 明确的**不适用**去向。
3. `## 任务路由`：表格「要做的事 → 读哪个文件」，禁止整包加载。
4. `## P0 硬约束`：违反即返工，编号列表，不解释成因。
5. `## 工作流程`：动词开头的有序步骤，每步可验证。
6. `## 完成判据`：可执行命令或客观状态，不用「检查一下」收尾。
7. 可选 `## 输出格式`：仅在该 skill 有产物契约时保留。

P1 强制细则、P2 建议和反模式一律下沉 L2 或 `.agents/knowledge/`。

## 阶段路由表契约（scope 的数据源）

`.agents/skills/cpp-development/references/stages/<game>.md` 一行一个单元（代码阶段或说明页章节），是章节映射、读取边界与状态的唯一权威记录，格式由 `.agents/skills/governing-agents/scripts/scope.py` 解析：

1. 行以 `| \`目标\`` 开头且 5 格：目标 | 章节正文 | 代码目录 | 专项必读 | 状态。
2. `—` 表示空；无代码阶段写 `—（横向说明页，无代码阶段）` 或 `—（规划页，实现前不建代码目录）`，不留裸空白。
3. 目标键用阶段目录名或说明页章节名；章号与阶段号错位时以本表为准，不靠数字推断。
4. 文件级读取边界只写一次（`- **必读**` 公共行），行间只写差异。
5. 状态只允许 `todo` / `done`；新阶段开工时先补行再建目录。验收语义与 `.agents/skills/testing/references/verification-matrix.md` 一致，本表不设第二套。

## 重构执行纪律

- 修改前先检索入口、引用和测试，理解文件职责后再迁移或删除。
- 需要改名、提取或拆分时，先比较新旧职责，保留有效信息，完成后从整体复核术语、链接、顺序和重复内容。
- 相同职责只保留一个权威实现。公共逻辑放入对应 skill 的 `scripts/` 或 `references/`。
- 删除文件后移除空目录（`check --profile fast` 会把空文件与空目录判为错误）。
- Skill 目录与文件名使用 kebab-case 与 ASCII。`agents/openai.yaml` 是宿主 UI 元数据，不参与任务路由。
- 完成后按改动域运行 `check --profile fast|book|knowledge|python`。涉及知识库再跑 `kb-index`、`kb-check` 和 `kb-eval`；改动的游戏阶段在 WSL 跑 `build <game>/<stage>`。

## 增量准入

1. 先更新已有的 skill reference、knowledge 文件或阶段路由表；没有独立读者任务或独立结论时不得新增第二份权威。
2. 超出建议阈值时，依次压缩措辞、合并相近主题、删除一次性案例，再按读者任务拆页或按概念边界拆知识；确需放宽阈值时改脚本常量并同步本表。
3. 新增 QMD 时同步更新 `_quarto.yml` 与阶段路由表；新增 knowledge 时同步更新 `.agents/knowledge/KNOWLEDGE.md` 与 `eval_set.py`。
4. 收口按改动域运行 `run.py check --profile ...`；跨域或发布运行 `full`，知识内容变更先重建索引，再检查 Parent 预算、召回率和注入峰值。
