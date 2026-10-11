# C++ 棋盘游戏实践

[![render check](https://github.com/chengzhao-dev/cpp-board-games/actions/workflows/render-check.yml/badge.svg)](https://github.com/chengzhao-dev/cpp-board-games/actions/workflows/render-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)

从终端井字棋开始的 C++ 工程实践。`games/tictactoe/` 下有三个可运行目录，从双人终端对局演进到电脑对手与逐行 JSON 协议。

在线阅读：<https://chengzhao-dev.github.io/cpp-board-games/>

## 从哪里读起

1. [确定对局规则](content/tictactoe/01-rules.qmd)
2. [对应工程目录](content/tictactoe/02-project-layout.qmd)
3. [实现棋盘存储](content/tictactoe/03-board.qmd)

完整列表见[井字棋落地页](content/tictactoe/index.qmd)。

## 当前状态

- 井字棋有三个可运行目录：`01-cli-game` 双人终端、`02-cpu-opponent` 电脑对手、`03-line-protocol` 逐行 JSON 协议
- 文档：Quarto Book 由 GitHub Actions 渲染并发布

## 仓库地图

仓库分四块：`content/` 是在线书的正文；`games/tictactoe/` 下的 `01-cli-game`、`02-cpu-opponent`、`03-line-protocol` 是三份各自完整的程序（双人终端、电脑对手、逐行 JSON 协议），每份都能单独配置、编译、测试和运行；`games/tictactoe/python/` 是协议之后的回放脚本与本地网页，只启动 03 已编好的程序；`.agents/` 是维护规则、领域知识库与检查脚本。章号与目录编号不必对齐，前五章都讲 `01-cli-game`。

需要修改仓库时，先阅读 [AGENTS.md](AGENTS.md)；贡献约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 在本机运行

前提：WSL Ubuntu，装好 CMake 4.2、Clang 和 Ninja。用 VS Code 的 Remote - WSL 打开某一个游戏目录（不是仓库根），三个目录各自执行一条构建命令。编辑器保存文件时读取仓库根的 `.editorconfig`，行尾和缩进保持仓库约定：

```bash
cd games/tictactoe/01-cli-game && ./build-and-run.sh
cd games/tictactoe/02-cpu-opponent && ./build-and-run.sh
cd games/tictactoe/03-line-protocol && ./build-and-run.sh
```

脚本完成配置、编译、格式与静态检查、测试和一局管道棋谱。回放与本地网页用仓库根 `config.toml` 指定的 Python 运行：

```bash
python games/tictactoe/python/replay.py
python games/tictactoe/python/web.py
```

`replay.py` 自带协议自检；`web.py` 启动后访问它打印出的地址，网页依赖 03 已生成的 `build/bin/app`。

## 学习路线

语言机制见姊妹仓库 [cpp-notes](https://github.com/chengzhao-dev/cpp-notes)。这些机制在棋盘上的用法见[实现棋盘存储](content/tictactoe/03-board.qmd)和[完成一次落子](content/tictactoe/04-game.qmd)。

## 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE)。
