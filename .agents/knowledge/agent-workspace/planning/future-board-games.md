---
kb_id: "bg-future-board-games-v1"
title: "后续棋类实现路径登记"
domain: "agent-workspace"
subdomain: "planning"
tags: [roadmap, future-games, engine, ai]
level_range: [0, 5]
dependencies: [bg-roadmap-v1, bg-project-decisions-v1]
created: "2026-10-09"
updated: "2026-10-09"
chunk_strategy: "semantic_heading"
estimated_tokens: 1200
---

# 后续棋类实现路径登记

本文件登记**尚未开工**的后续棋类的实现路径：每类游戏的推荐分层、首阶段形态、强力人机何时引入引擎级技术（下称 B 族），以及与井字棋方案 A 的边界。规划新游戏、判断是否上 B 族引擎时读本文件；阶段顺序与读者范围仍以标识 `bg-roadmap-v1` 的知识文件为准。

## 总原则

- 新游戏仍按 `Board`（状态）/`Game`（编排）/`apps`（适配）拆分；规则核心不依赖终端、GUI、Web、Python 或 Quarto。
- 共享库只在**至少两个游戏真实复用**且语义稳定后提取，不预建 `shared/`。
- 读者页「先可编译再注册章节」：新建 `games/<game>/` 前先改本文件状态 → 补 `references/stages/<game>.md` 路由表 → 再写代码 → 最后才注册 `_quarto.yml` / `content/`（与标识 `bg-roadmap-v1` 的知识文件一致）。

## 棋类对照表

| 棋类 | 建议目录键 | 首阶段（教学） | 强力人机阶段（B 族） | 备注 |
| --- | --- | --- | --- | --- |
| 井字棋 | `tictactoe`（已有） | 数组 Board + 全深度 αβ（方案 A） | **不升级 B** | 本仓现状 |
| 四子棋 | `connect4`（未建） | 数组或简易列高表示 + 浅/中层 αβ | bitboard + αβ + 着法序 + TT | 引擎标配见 Tromp Fhourstones 等 |
| 五子棋 | `gomoku`（未建） | 数组 15×15 + Game 分层 + 浅层 αβ/启发式 | NegaMax/αβ + 迭代加深 + Zobrist/TT + 威胁评估；可选 bitboard、VCF；进阶 MCTS/RL | 大盘主流方案 |
| 黑白棋 | `reversi`（未建） | 数组 + 合法翻转列表 | 中后期再评估 bitboard/TT | 仅占位，细节开工时补 |

## A 族与 B 族技术清单

**A 族（井字棋教学线允许）**：数组盘、全深度 minimax + αβ、`CompletesLine` 威胁探测、`Search` 内必胜/必挡优先枚举（根节点顺序守恒，见标识 `bg-project-decisions-v1`）。αβ 本身与「Search 内简单威胁着法序」属 A，不算 B。

**B 族（大盘引擎，禁止用在井字棋教学线）**：bitboard / 旋转 bitboard、NegaMax 包装、迭代加深、Zobrist、置换表、杀手着法/历史启发表、棋型/威胁评估引擎、VCF、MCTS/AlphaZero。

## 为什么井字棋不上 B

井字棋 3×3 状态空间约 10⁴ 量级，数组盘 + 全深度 αβ 已是完美博弈最优；bitboard/TT 只属课外玩具，加进来会稀释教学重点（规则分层与接缝），不带来可观察的行为提升。四子棋（约 10²¹）、五子棋（约 3²²⁵ 量级）、国际象棋才需要 B 族。

## 开工检查单

开新棋类游戏前按下面的顺序改文件：

1. 改本文件状态：把对应棋类从「未建」标为在建。
2. 补 `.agents/skills/cpp-development/references/stages/<game>.md` 阶段路由表（`scope` 依赖它解析 game/stage）。
3. 写首个可编译阶段（`games/<game>/01-*/`），过 `build`。
4. 最后才注册 `_quarto.yml` 与 `content/<game>/`，并补 `bg-engineering-storyline-v1` 的开篇叙事。

**禁止**：无源码时预建 `games/gomoku/`、`content/gomoku/` 或空 `stages/gomoku.md`；在井字棋 `.qmd` 正文预告其他棋类的 bitboard；把 B 族步骤写进 `cpp-development` references 当 how（未开工无执行步骤，why 留本文件）。
