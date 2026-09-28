---
kb_id: "bg-roadmap-v1"
title: "项目路线依据"
domain: "agent-workspace"
subdomain: "planning"
tags: [roadmap, stages, milestones]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-09-28"
chunk_strategy: "semantic_heading"
estimated_tokens: 900
---

# 项目路线依据

本文件供 Agent 判断阶段边界使用；面向读者的完整路线记录在 `content/tic-tac-toe/`。

## 当前文档范围

本轮重置后，`content/` 只维护井字棋设计与执行路线。其他棋类暂不创建对应 content 页面，但未来四子棋、五子棋、黑白棋等必须沿用“最小可实现、每步可验证、先具体后抽象”的渐进式流程。

## 井字棋阶段顺序

终端双人井字棋按编号目录从最小到完整迭代，每个目录都是 `games/tic-tac-toe/<NN-名称>/` 下的完整项目（详见 标识 `bg-staged-game-layout-v1` 的知识文件）：

1. `01-toolchain-probe`：WSL Ubuntu 下的 C++20、CMake、Ninja、Clang、CTest 最小工程；目录已建立 `.clang-format` 和 `.vscode/` 配置归属。
2. `02-board-and-state`：固定棋盘、位置、玩家、棋子和状态值类型。
3. `03-move-validation`：合法落子，以及非法输入不改变状态。
4. `04-turns-and-terminal-rules`：回合切换、行列对角线胜负、平局和终局保护。
5. `05-cli-and-acceptance`：终端双人闭环、CLI smoke test 和分层验收。

后续阶段只在真实开始实现时创建目录：

6. `06-ai`：双人规则稳定后加入 Minimax AI。
7. `07-python-subprocess`：用 Python `subprocess` 驱动稳定 CLI。
8. `08-json-protocol`：在纯文本不足时定义逐行 JSON 协议。
9. `09-http-fetch`：用 Python HTTP 服务和浏览器 Fetch 构建 Web 原型。
10. `10-websocket`：只有实时推送确有需要时再评估。

## 阶段门槛

每个小步都应保持可配置、可构建、可运行或可测试，并记录目标、预期行为、验证方式、失败定位范围和完成状态。Hello World 或最小工程只验证开发环境，不成为最终游戏架构。

## 测试框架时机

- `01-toolchain-probe` 和 `05-cli-and-acceptance` 的冒烟验证使用纯 CTest（`add_test` + `PASS_REGULAR_EXPRESSION`）；第三方测试框架在出现真实规则逻辑的阶段按需评估引入。
- `02-board-and-state` 出现第一批真实规则逻辑时，通过 CMake FetchContent 引入 GoogleTest，测试统一注册进 CTest 运行；后续阶段沿用（2026-09 决策）。

## 架构边界

规则核心不依赖终端、GUI、Python、Web 或 Quarto。适配层只能通过明确动作和结果与核心交互；测试直接调用规则核心。先让井字棋具体实现成立，再根据至少两个游戏的真实共性考虑共享库。

## Agent 行为门槛

未获用户明确实现要求前只维护设计和文档，边界以根 `AGENTS.md`「工作规则」为准。Quarto 渲染成功不等于 C++ 构建或测试成功；文档只能把实际运行过的结果记录为已通过。
