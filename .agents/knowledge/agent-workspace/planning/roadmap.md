---
kb_id: "bg-roadmap-v1"
title: "项目路线依据"
domain: "agent-workspace"
subdomain: "planning"
tags: [roadmap, stages, milestones]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 500
---

# 项目路线依据

本文件是路线与阶段边界的取舍记录：未开工棋类的登记路径和不开工的理由。井字棋现行阶段状态、能力口径与阶段门槛见标识 `bg-project-overview-v1` 的规范文件；读者页是 `content/tictactoe/` 的各章，不另设路线章。

## 后续棋类（未开工）

后续棋类的推荐分层、首阶段形态与何时引入引擎级技术（bitboard/置换表等）登记在标识 `bg-future-board-games-v1` 的知识文件。当前只登记路径，不创建目录、不建阶段路由、不注册章节：

| 棋类 | 目录键 | 首阶段 | 强力人机 |
| --- | --- | --- | --- |
| 四子棋 | `connect4` | 数组盘 + 浅/中层 αβ | bitboard + αβ + 着法序 + TT |
| 五子棋 | `gomoku` | 数组 15×15 + 浅层 αβ/启发式 | NegaMax/αβ + 迭代加深 + Zobrist/TT + 威胁评估 |
| 黑白棋 | `reversi` | 数组 + 合法翻转列表 | 中后期再评估 bitboard/TT |

## Agent 行为门槛

未获用户明确实现要求前只维护设计和文档，边界以根 `AGENTS.md`「工作规则」为准。Quarto 渲染成功不等于 C++ 构建或测试成功；文档只能把实际运行过的结果记录为已通过。
