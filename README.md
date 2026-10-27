# C++ 棋盘游戏实践

[![render check](https://github.com/chengzhao-dev/cpp-board-games/actions/workflows/render-check.yml/badge.svg)](https://github.com/chengzhao-dev/cpp-board-games/actions/workflows/render-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)

从终端井字棋开始的 C++ 工程实践。`games/tictactoe/` 是一份井字棋工程，当前构建包含动态库、最小主程序与棋盘测试；终端层与快照保留源码，等待接回构建。这个工程从双人终端对局演进到电脑对手与逐行 JSON 协议。

在线阅读：<https://chengzhao-dev.github.io/cpp-board-games/>

## 从哪里读起

1. [确定对局规则](content/tictactoe/01-rules.qmd)
2. [对应工程目录](content/tictactoe/02-mapping-layout.qmd)
3. [实现棋盘存储](content/tictactoe/03-board.qmd)

读完这三章，可以按顺序读工程。对局持有一块棋盘，在棋盘上判定胜负。电脑担任另一名玩家；完整设计里，终端程序打印棋盘并读入坐标，入口把标准流交给对局循环，测试核对库的行为。当前构建先用 14 条棋盘用例验收动态库，再由入口创建一局、落一子并检查返回值。最后的局面快照把每一轮写成一行 JSON，供其他程序读取。全部章节见 [井字棋首页](content/tictactoe/index.qmd)。

## 仓库构成

仓库由四部分组成：

- **在线书**：`content/` 与根 `index.qmd` 保存章节正文。GitHub Actions 渲染并发布。
- **井字棋工程**：`games/tictactoe/` 包含动态库、主程序与棋盘测试，另有保留的终端层与回放脚本；当前能独立构建并运行最小入口。
- **维护规则**：`.agents/` 保存项目技能、三个维护脚本与内容检查配置。
- **主题与过滤器**：`theme/` 与 `filters/` 提供渲染主题、配色和可折叠答案。内容检查由 `.agents/skills/quarto-book-project/checks.json` 与插件 `writing-quarto` 的脚本执行。

修改仓库之前先读 [AGENTS.md](AGENTS.md)。贡献约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 运行工程

前提：WSL Ubuntu，装好 CMake 3.20 或更高、Clang、Ninja 与 libc++ 开发包。用 VS Code Remote - WSL 打开仓库根，编辑器读取根目录的 `.editorconfig`，行尾和缩进保持仓库约定。构建从仓库根执行：

```bash
python .agents/scripts/building-wsl.py tictactoe
```

脚本在 WSL 里进入工程目录，运行 `running-build.sh`；CI 在 Linux 上直接执行 `bash games/tictactoe/running-build.sh`。构建脚本完成 Debug 的配置与编译，跑 CTest 的 14 条棋盘用例，再运行最小入口。首次配置会下载 GoogleTest v1.15.2。回放与本地网页用 `config/config.toml` 指定的 Python 运行：

```bash
python games/tictactoe/python/replay.py
python games/tictactoe/python/web.py
```

`replay.py` 自带协议自检；`web.py` 启动后访问它打印出的地址。两个脚本都在 `games/tictactoe/python/` 目录。网页按终端层的快照协议读取对局；当前入口不写快照，终端层接回后才会生成可回放的数据。

## 延伸阅读

数组与枚举在棋盘上的用法见 [实现棋盘存储](content/tictactoe/03-board.qmd) 和 [完成一次落子](content/tictactoe/04-game.qmd)。若要系统阅读这些机制，见姊妹仓库 [cpp-notes](https://github.com/chengzhao-dev/cpp-notes)。

## 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE)。
