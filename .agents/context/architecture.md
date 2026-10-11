---
kb_id: "bg-architecture-overview-v1"
title: "现行架构"
domain: "agent-workspace"
subdomain: "overview"
tags: [architecture, layering, board, game]
level_range: [0, 5]
dependencies: []
created: "2026-10-11"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 800
---

# 现行架构

本文件回答「代码现在分几层、边界画在哪」。逐条编码规则见 `conventions/` 下的规范文件；决策过程与被否决的替代方案记录在标识 `bg-project-decisions-v1` 的知识文件。

## 架构边界

规则核心不依赖终端、GUI、Python、Web 或 Quarto。适配层只能通过明确动作和结果与核心交互；测试直接调用规则核心。先让井字棋具体实现成立，再根据至少两个游戏的真实共性考虑共享库。架构取舍的调研与否决记录见标识 `bg-project-decisions-v1` 的知识文件。

## 组件式布局

引入库 target 的阶段采用组件式布局：库组件目录（`tictactoe/`，含 `include/`、`src/` 与自己的 `CMakeLists.txt`）、`apps/`（主程序）与 `tests/` 各带 `CMakeLists.txt`，顶层只做工程声明、产物目录、`enable_testing()` 与 `add_subdirectory`。适配层 `apps/` 可含私有 `include/` 与 `src/`，展示助手住在 `apps/include/cli.h` 与 `apps/src/cli.cpp`，仍在 `namespace tictactoe`，不另加 `cli` 命名空间。target 命名、产物目录与库路径封装见标识 `bg-cmake-conventions-v1` 的规范文件；目录归属见标识 `bg-staged-game-layout-v1` 的规范文件。

## 规则核心形态

- `Board` 只做状态与格子级操作（`IsValidPosition`、`GetCellState`、`PlacePiece`、`IsFull`、private `ToFlatIndex`），`Game` 承担回合、落子编排与胜负平判定（private static 的 `ResultAfterMove`、`HasPlayerLine`，及 `GetResult`、`TryPlace`）；胜负判定不进 `Board`。
- 棋子身份由 `Player` 表达、格子状态由 `CellState` 表达，映射只在 `PlayerToCellState` 一处；`Move` 只装 `position` 与 `player`。`Board` 只收 `CellPosition` 加 `CellState`，映射唯一开口在 `Game::TryPlace`。
- 对外 API 为 `GetCellState`、`PlacePiece`、`PlayerToCellState`、`Game::TryPlace`、`GetCurrentPlayer`、`GetHistory`、`Game::HasPlayerLine`、`ToFlatIndex`；异常文案与命名规则见标识 `bg-exception-message-format-v1`、`bg-google-cpp-style-v1` 的规范文件。
- 头文件常量为具名命名空间内的 `inline constexpr` 加 `k` 前缀（如 `tictactoe::kRows`）；`noexcept` 只标注无潜在抛出路径的函数。规则见标识 `bg-google-cpp-style-v1` 的规范文件。

## 对手与逐行协议

`02-cpu-opponent` 的对手只产生 `Move` 并调用同一个 `Game::TryPlace`，AI 不进入规则核心的前置依赖；随机、启发式与 minimax 三种强度同住一个阶段。`03-line-protocol` 在应用层追加逐行版本化 JSON 快照，规则库保持不感知协议。分层细节见标识 `bg-cmake-conventions-v1` 的规范文件，项目现状见标识 `bg-project-overview-v1` 的规范文件。

## 演进约束

阶段之间采用复制快照或持续演进实现，由实际变更成本决定；无论哪种方式，每个阶段都必须保持可配置、可构建、可测试和可追溯。共享库在至少两个游戏真实复用且语义稳定后才提取到 `shared/`；语言机制的系统讲解由 cpp-notes 承担，跨仓读者链接用 GitHub 绝对 URL（base 见标识 `bg-quarto-conventions-v1` 的规范文件）。
