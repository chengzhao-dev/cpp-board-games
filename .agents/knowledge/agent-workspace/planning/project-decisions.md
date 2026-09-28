---
kb_id: "bg-project-decisions-v1"
title: "项目决策依据"
domain: "agent-workspace"
subdomain: "planning"
tags: [decisions, architecture, boundaries]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-09-28"
chunk_strategy: "semantic_heading"
estimated_tokens: 800
---

# 项目决策依据

本文件供 Agent 理解项目边界和已确认取舍使用。面向读者的完整解释统一维护在 `content/**/*.qmd`，本文件不作为 Quarto 入口。

## 文档重置决策

- 本轮采用完整重置方案：清理旧 `content/` 文件，保留 `content/` 目录本身，并只创建 `content/tic-tac-toe/`。
- 根 `index.qmd` 服务井字棋主线，允许「后续棋类」用 `.landing-card.coming-soon` 占位，但不提前创建其他棋类页面或实现；`_quarto.yml` 仍只注册井字棋章节，不引用已清理的开发、架构或 Python 章节。
- 面向读者的完整设计、路线、验收和联网调研总结写入 Quarto；`.agents/knowledge/` 只保留 Agent 判断所需的简短决策和边界。

## 架构决策

- C++ 是核心实现语言，当前基线为 C++20、CMake、Ninja、Clang 和 CTest。
- 首个编号目录是 `01-toolchain-probe` 最小工程：最小 CLI、稳定输出、返回码 0 和 CTest smoke test。
- 井字棋核心规则与终端、Python、JSON、HTTP 和 WebSocket 解耦；规则核心不得依赖终端、GUI、Web、Python 或 Quarto。
- 同一套规则先由 C++ 测试直接验证，再由终端或其他适配层复用。
- 先用具体值类型和小型规则接口建立不变量，再考虑抽象；至少两个游戏真实复用且语义稳定后才提取共享库。
- 新代码的类型形式：取值封闭的集合用 `enum class`（Core Guidelines Enum.3），数据组合用 `struct` 聚合，不提前引入继承体系；类型定义在 `<game>` 命名空间并放在 `include/<namespace>/` 下。强类型包装不在井字棋首批使用。语言机制的系统讲解由 cpp-notes 基础分册承担，跨仓读者链接用 GitHub 绝对 URL（base 见标识 `bg-quarto-conventions-v1` 的知识文件）。
- 标识符命名与编码规则以 Google C++ Style Guide 为主标准，函数 PascalCase、变量 snake_case、常量与枚举子 `k` 前缀；此前「函数与变量小驼峰」决策废止，两仓（cpp-board-games 与 cpp-notes）对等执行。命名表、偏离白名单与各章采纳要点见标识 `bg-google-cpp-style-v1` 的知识文件。
- 先完成双人终端闭环，再加入 Minimax；AI 不得成为核心规则的前置依赖。
- Python 过渡顺序为稳定 CLI、`subprocess`、逐行 JSON、HTTP/Fetch，实时需求明确后才评估 WebSocket。
- 游戏章节叙事按「八步流程 + STAR」故事线分配章内职责，依据见标识 `bg-engineering-storyline-v1` 的知识文件。

## 未来能力口径

对 AI、Python、JSON、HTTP、WebSocket、GUI、WebAssembly、第三方测试框架、共享游戏引擎等未来能力，不在面向读者的章节中预设「做/不做」结论或名词清单；这些口径只留在本文件供 Agent 判断。读者侧 `01-scope-and-principles.qmd`（title「先看清工程」）只写工具、项目内容与分层实现，不复述未来能力清单。已有条件式门槛继续有效：共享库需至少两个游戏真实复用、WebSocket 需实时推送确有必要、GoogleTest 待出现真实规则逻辑时经 FetchContent 引入、阶段目录只在真实开始实现时创建。

## 其他棋类

四子棋、五子棋、黑白棋等未来游戏也遵循同一渐进式开发和验证原则，但本轮只负责井字棋 content，不提前创建其他棋类页面或实现。

## 外部依据

- C++ Core Guidelines：具体类型、纯函数倾向、RAII、窄接口和避免过早抽象。
- CMake `enable_testing`/`add_test`：顶层启用并注册可由 CTest 执行的测试。
- Python `subprocess`：退出码、stdout/stderr、超时和一次性/持续进程边界。
- MDN Fetch 与 WHATWG WebSocket：HTTP 状态检查、JSON 解析、连接生命周期和应用层消息协议。
- Berkeley CS188 Multi-Agent Search：Minimax 的 MAX/MIN、终局 utility、搜索深度和 alpha-beta。

## Agent 行为边界

Agent 读写边界的唯一出处是根 `AGENTS.md`「工作规则」（只读默认、写入触发、删除前读取、不动生成物），本文件不再复述。
