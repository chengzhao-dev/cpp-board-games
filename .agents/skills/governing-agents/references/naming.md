# Agent 工作区命名规范

本规范适用于 `.agents/` 下 `skills/`、`knowledge/`、`memory/`、`incidents/` 及技能内部目录。结构规则见同技能下的 `structure.md`；两者冲突时，命名以本文件为准，结构以 `structure.md` 为准。

## 1. 核心原则

- 默认 **kebab-case**：全小写 + 连字符，如 `writing-quarto`。
- 固定入口文件用大写：`AGENTS.md`、`SKILL.md`、`KNOWLEDGE.md`、`MEMORY.md`、`INDEX.md`、`README.md`。
- 名称有语义：能看出「是什么」或「做什么」，禁用 `utils`、`misc`、`temp`、`new`、`final`。
- 技能目录名 ≤ 20 字符，动作 + 对象（如 `shipping-github`），且必须与 `SKILL.md` 的 `name` 字段一致。
- 字符集仅 `a-z`、`0-9`、`-`、`_`、`.`；禁止连续连字符；文档路径一律纯 ASCII，中文只出现在文件内容里。
- 技能内 Python 脚本用 `snake_case`（`check_health.py`）；Shell 用 kebab-case（`build-and-run.sh`）；Lua filter 用 kebab-case（`answer-disclosure.lua`）。

## 2. 各类命名

| 类型 | 规则 | 示例 |
| --- | --- | --- |
| 技能目录 | 动作+对象 kebab-case，≤20 | `governing-agents`、`writing-quarto` |
| 知识领域 | 领域名词 kebab-case | `agent-workspace`、`cpp-teaching` |
| 记忆 / 事故领域 | 领域名词 kebab-case | `quarto-render`、`git-github` |
| 普通 Markdown | kebab-case + `.md` | `cmake-conventions.md` |
| 领域索引 | `<domain>/index.md` | `agent-workspace/index.md` |
| 技能内参考 | `<topic>.md`，可按性质分子夹 | `.agents/skills/writing-quarto/references/…` |

## 3. kb_id 方案

- 本仓库知识文件 `kb_id` 统一为 `bg-<area>-<topic>-v<N>`（如 `bg-cmake-conventions-v1`）；cpp-notes 仓库用 `cpp-<area>-<topic>-v<N>`，前缀区分两仓，其余规则一致。
- `kb_id` 全局唯一，改名等于新建知识；历史 id 保持不改名。

## 4. 元数据规则

- `SKILL.md` frontmatter 固定三个字段：`name`（= 目录名）、`description`（长句，承载触发场景关键词）、`metadata.short-description`。
- 每个技能一份 `agents/openai.yaml`：`interface.display_name`、`interface.short_description`、`interface.default_prompt`（用 `$<skill>` 语法）、`policy.allow_implicit_invocation`。
- 知识文件 frontmatter 的 `domain` 字段取同名领域目录值（如 `cpp-teaching/` 下文件 `domain: cpp-teaching`）；`subdomain` 取其上层子域目录名。完整字段表见 `.agents/knowledge/KNOWLEDGE.md`。

## 5. 正文禁日期戳

`.agents/skills/**` 与 `.agents/knowledge/**` 的 Markdown **正文**不得出现 `YYYY-MM-DD` 时间戳（含标题后缀、列表标签、表格原因列、`…修订` / `…起` / `…决策：` 前缀）。变更溯源只用 frontmatter 的 `created` / `updated`；拆分或重组技能与知识文件时以稳定 `kb_id` 引用，不靠日期后缀区分版本。`verify_content.py` 扫描上述目录正文，命中即失败。

## 6. 一致性要求

- 同一层级、同一类资源保持同一种命名风格；改名时同步所有引用，不留旧名孤儿路径。
- 知识文件之间引用统一写「见标识 `<kb_id>` 的知识文件」；指向技能侧规则写「见 `<skill>` 的 …」，不使用 `[[wiki]]` 链接。
