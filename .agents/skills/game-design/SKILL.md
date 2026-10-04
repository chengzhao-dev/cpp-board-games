---
name: game-design
description: 设计棋盘、棋子、动作、回合和游戏规则；建模游戏状态或判断规则歧义时使用
metadata:
  short-description: 棋盘游戏规则建模
---

# Skill: game-design

承载棋盘游戏的值类型建模与规则设计流程。具体实现转 `cpp-development`。

## 适用场景

- 设计棋盘、棋子、动作、回合、胜负与平局的状态表达。
- 判断规则歧义、抽象时机与共享库提取条件。
- **不适用**：写实现代码（转 `cpp-development`）、测试编排（转 `testing`）。

## 任务路由

| 任务 | 读取 |
| --- | --- |
| 对局规则 | `content/tictactoe/01-rules.qmd` |
| 棋盘与格子状态 | `content/tictactoe/03-board.qmd` |
| 落子与终局 | `content/tictactoe/04-game.qmd` |
| 项目值类型约定与语言机制讲解 | `.agents/knowledge/agent-workspace/planning/project-decisions.md`；语言机制见 [cpp-notes 语言基础](https://github.com/chengzhao-dev/cpp-notes/tree/main/content/language-basics) |
| 抽象与共享库决策依据 | `.agents/knowledge/agent-workspace/planning/project-decisions.md` |
| 游戏开篇/收官章的流程与 STAR 职责 | `.agents/knowledge/agent-workspace/planning/engineering-storyline.md` |
| 对手与后续阶段是否已实现 | `.agents/knowledge/agent-workspace/planning/roadmap.md`「已设计、未实现」 |

## P0 硬约束

1. 坐标、玩家、格子状态、动作和终局用值类型表达。`CellState` 等 `enum class` 的每个枚举子写连续初值。当前井字棋是双人终端，不含 AI。
2. 规则对象只负责规则，不直接读写终端或网页。
3. 井字棋优先组合，不预先建立复杂的棋子继承体系。
4. 只有至少两个游戏真实共享且语义稳定时，才提取公共库。
5. 记录每次抽象的动机、替代方案和测试依据。
6. 任何规则歧义都必须先询问用户并列出方案。

## 完成判据

- [ ] 每个新增抽象都有动机、替代方案和测试依据记录。
- [ ] 规则核心不依赖终端、GUI、Web、Python 或 Quarto。
