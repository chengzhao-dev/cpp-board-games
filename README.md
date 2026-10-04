# C++ 棋盘游戏实践

[![render check](https://github.com/chengzhao-dev/cpp-board-games/actions/workflows/render-check.yml/badge.svg)](https://github.com/chengzhao-dev/cpp-board-games/actions/workflows/render-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)

从终端井字棋开始的 C++ 工程实践：当前只有一个可运行目录，两名玩家在终端下完一局，没有电脑对手。

在线阅读：<https://chengzhao-dev.github.io/cpp-board-games/>

## 从哪里读起

1. [写下井字棋规则](content/tictactoe/01-rules.qmd)
2. [配置并运行井字棋](content/tictactoe/02-project-layout.qmd)
3. [定义棋盘与格子状态](content/tictactoe/03-board.qmd)

完整列表见[井字棋落地页](content/tictactoe/index.qmd)。

## 当前状态

- 井字棋只有 `games/tictactoe/01-cli-game`，双人，无 AI
- 文档：Quarto Book 由 GitHub Actions 渲染并发布

## 仓库内容

| 路径 | 内容 |
| --- | --- |
| `content/` | Quarto Book 正文 |
| `games/` | 井字棋工程，自带构建与测试 |
| `.agents/` | 维护规则、领域知识库与检查脚本 |

需要修改仓库时，先阅读 [AGENTS.md](AGENTS.md)。

## 学习路线

语言机制见姊妹仓库 [cpp-notes](https://github.com/chengzhao-dev/cpp-notes)。它们在棋盘上的用法见[定义棋盘与格子状态](content/tictactoe/03-board.qmd)和[检查落子并判定终局](content/tictactoe/04-game.qmd)。

## 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE)。
