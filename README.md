# C++ 棋盘游戏实践

[![render check](https://github.com/chengzhao-dev/cpp-board-games/actions/workflows/render-check.yml/badge.svg)](https://github.com/chengzhao-dev/cpp-board-games/actions/workflows/render-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)

从终端井字棋开始的渐进式 C++ 工程实践：每个棋类按编号阶段推进，一个阶段一个可运行的项目，同步学习 CMake、GoogleTest 与后续的 Python 衔接。

在线阅读：<https://chengzhao-dev.github.io/cpp-board-games/>

## 从哪里读起

井字棋全书按阅读顺序组织，前几章是：

1. [先看清工程](content/tic-tac-toe/01-scope-and-principles.qmd)——需求形态、实现层次与开发环境选型
2. [配置并运行最小工程](content/tic-tac-toe/02-toolchain-probe.qmd)——工具链验证与 CMake 最小项目
3. [棋盘与状态](content/tic-tac-toe/03-board-and-state.qmd)——第一个游戏状态库与自动化测试

完整章节列表见[井字棋落地页](content/tic-tac-toe/index.qmd)。

## 当前状态

- 井字棋：`01-toolchain-probe` 与 `02-board-and-state` 两个阶段已完成，各自可独立配置、编译、通过 CTest 并运行；后续阶段按书中渐进路线推进
- 文档：Quarto Book 承载全部设计、路线与开发记录，由 GitHub Actions 渲染并发布
- Python 衔接：计划从标准库、`subprocess` 与 JSON 开始，出现在真实需要的阶段

## 仓库内容

| 路径 | 内容 |
| --- | --- |
| `content/` | Quarto Book 正文（设计、路线与开发记录） |
| `games/` | 按编号阶段组织的游戏代码，每个阶段自带构建与测试 |
| `.agents/` | 维护规则、领域知识库与检查脚本 |

需要修改仓库时，先阅读 [AGENTS.md](AGENTS.md)。

## 学习路线

本项目配合姊妹仓库 [cpp-notes](https://github.com/chengzhao-dev/cpp-notes) 使用：`cpp-notes` 负责 C++ 语言机制的系统讲解，本仓库负责这些机制在完整项目中的工程用法。例如值类型与命名空间的语言机制见 [cpp-notes 语言基础分册](https://github.com/chengzhao-dev/cpp-notes/tree/main/content/language-basics)，它们在游戏状态模型中的用法见[棋盘与状态](content/tic-tac-toe/03-board-and-state.qmd)。

## 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE)。
