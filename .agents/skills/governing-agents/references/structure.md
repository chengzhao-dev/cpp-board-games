# Agent 工作区结构规范

本规范适用于 `.agents/` 及其下的 `skills/`、`knowledge/`、`memory/`、`incidents/`，以及技能内部资源目录。配套命名规范见同技能下的 `naming.md`；两者冲突时，命名以 `naming.md` 为准，结构以本文件为准。本文件与 cpp-notes 仓库的同名规范同构，两仓统一决策与保留差异见第 6 节对照表。

## 1. 四区职责

| 区 | 回答的问题 | 何时读 |
| --- | --- | --- |
| `skills/` | 怎么做（流程、清单、硬约束） | 命中任务时读对应 `SKILL.md` |
| `knowledge/` | 是什么 / 为什么（稳定事实、取舍） | 需要依据时，经 `kb-search` 或 `kb_id` |
| `memory/` | 过去哪里容易出错 | 每个任务开始时读 `MEMORY.md` 索引 |
| `incidents/` | 这次失败有没有先例 | **仅排查失败时**读 `INDEX.md`，平时视为不存在 |

一个知识点只允许一个出处：同一规则不要在多个区完整复制；引用用路径或 `kb_id` 指回唯一出处。

## 2. 目标结构

```text
.agents/
├── README.md                     # 一级入口，允许
├── skills/
│   ├── governing-agents/         # 三级：具体技能
│   │   ├── SKILL.md
│   │   ├── references/           # naming.md、structure.md、catalog.md、refactor-guidelines.md
│   │   └── scripts/
│   └── <skill>/
│       ├── SKILL.md
│       ├── references/
│       └── scripts/
├── knowledge/
│   ├── KNOWLEDGE.md              # 领域路由
│   └── <domain>/<subdomain>/<topic>.md
├── memory/
│   ├── MEMORY.md
│   └── domains/<domain>/{index.md,<topic>.md}
├── incidents/
│   ├── INDEX.md
│   └── <domain>/<topic>.md
└── mcp/
    ├── README.md
    └── server.py
```

## 2.1 按性质封装

一个文件夹只封装一种「性质」（领域、职责、技能、生命周期、格式）。同目录出现两种以上性质时，继续拆子文件夹。

## 2.2 叶子目录规则（强制）

- **非叶子目录**（还有子文件夹的目录）只放：固定入口文件（`SKILL.md`、`KNOWLEDGE.md`、`MEMORY.md`、`INDEX.md`、`README.md`、`index.md`）、子文件夹、必要的轻量索引。
- **叶子目录**（其下没有子文件夹）直接放该性质的最终文件。
- 具体内容文件尽量放在从仓库根算起的三级或更深目录。

判定方法：目录里同时有 `x.md` 和子文件夹 `y/`，且 `x.md` 不是入口索引 → 把 `x.md` 移入性质相符的叶子（新建或已有的 `y/` 内）。

## 3. 技能内部

- `SKILL.md` 是唯一入口；详细规则放 `references/`，脚本放 `scripts/`，资源放 `assets/`。
- `references/` 内按性质建子目录（如 `stages/`、`zh/`、`quarto/`）；子目录本身成为叶子时才直接放文件。
- 脚本数量增多时按职责分子目录；统一入口 `run.ps1`/`run.py` 保留在 `scripts/` 顶层。

## 4. memory 与 incidents

- `memory/`：三层索引，`MEMORY.md` 只做领域路由；每个领域一个 `index.md`（关键词 → 主题表）+ 若干原子主题文件。
- `incidents/`：单一 `INDEX.md`（症状关键词 → 案例指针）；案例文件放 `<domain>/`。不进任何常规路由、catalog 或检索索引。
- 复盘案例正文顺序：frontmatter → `# 标题` → 日期与关键词 → `## 症状` → `## 根因` → `## 修复方案` →（可选）`## 验证方法`。

## 5. 本仓特例

- 知识库索引产物只写根目录 `temp/knowledge-index/`，不入 `.agents/`。
- `.agents/skills/designing-theme/assets/theme/**` 是 Quarto 消费的主题资源，其内部组织以渲染链路为准，不受 2.2 约束。
- `.agents/skills/cpp-development/assets/` 下的 C++ 配置模板与工程脚手架模板是 `init_project.py` 与新阶段的初始化素材，不是任何阶段的运行时依赖。
- `mcp/server.py` 是宿主登记的固定入口路径，保持不动。

## 6. 与 cpp-notes 的对照表

两仓 `.agents/` 同构（四区 + 同名知识领域目录），职责与落点对齐；具体数字（体量阈值、篇幅预算）按仓可调，不对齐。除下表所列差异外，同名文件语义一致，双向同步只在用户显式要求时执行。

| 项 | 本仓（cpp-board-games） | cpp-notes | 说明 |
| --- | --- | --- | --- |
| 领域知识 | `agent-workspace`、`cpp-teaching`、`quarto-writing`；`repo-github`、`visual-theme` 有文件再建 | 同左三个 + `repo-github`、`visual-theme` 已建 | 领域目录名与 `domain` 字段取值规则一致 |
| `kb_id` 前缀 | 一律 `bg-*` | 一律 `cpp-*` | 跨仓只链 GitHub，索引与 eval 各认各的前缀 |
| C++ 技能 | `cpp-development`（游戏工程用法）+ `game-design`（规则建模）+ `python-tooling` | `writing-cpp`（语言机制系统讲解） | 教学内容互补：本仓讲工程用法，notes 讲语言机制 |
| 任务路由 | 阶段路由表 `.agents/skills/cpp-development/references/stages/<game>.md`，`scope.py` 解析 game/stage | 任务矩阵（notes 侧 `writing-cpp` 技能按 part 分册的任务表），`scope.py` 解析 part/chapter，另有任务矩阵检查脚本 | 本仓不移植任务矩阵与其检查脚本 |
| C++ 验证 | 各阶段 `build-and-run.sh`，`run.py build <game>/<stage>` 进 WSL；C++ 不进 CI | `verify_examples.py`，`run.py verify`，CI 不编译 | 验证入口不同，`scope` 输出的读取边界语义一致 |
| `run.py` 子命令 | check/verify/render/scope/build/status/kb-* | check/verify/render/scope/build/status/kb-* | 同名同义；`verify` 在本仓包装 verify_content，在 notes 包装 verify_examples |
| Python 来源 | 根 `config.toml` 的 `python`，最低 3.12，失败即停 | 同左 | CI 用 `sed` 把该字段指向 runner 的 python3 |
| 体量阈值 | L0/listing 厂商硬约束；L1/L2/catalog 为本仓建议（WARN，`--strict` 失败） | L0–L3 数字硬顶 | 落点表与「预算按仓可调」原则见各自 `refactor-guidelines.md` |
| C++ 命名 | Google C++ Style Guide 为主标准：函数与类型 PascalCase、变量 snake_case、常量与枚举子 `k` 前缀；偏离白名单（`#pragma once`、`.cpp`/`.h`、C++20、异常边界、LLVM 横幅、不强制 cpplint），权威见 `bg-google-cpp-style-v1` | 同构：同一主标准与白名单，权威见 `cpp-naming-format-v1` | 两仓同步废止小驼峰选型；`.clang-tidy` 命名配置一致 |
| 主题资产 | 同一套 GitHub palette 与组件 CSS | 同左 | `check_layout.py` 环境变量前缀 `BOARD_GAMES_*` vs `CPP_MEMO_*` |
