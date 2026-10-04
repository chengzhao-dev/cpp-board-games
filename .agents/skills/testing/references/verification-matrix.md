# 改动范围与验证矩阵

供 Agent 在改动后快速圈定验证范围。面向读者的终端验收在 `content/tictactoe/05-terminal-play.qmd`。

| 改动 | 对应验证 |
| --- | --- |
| 构建规则或工具链 | 被改阶段目录内的 `build-and-run.sh` |
| 棋盘和棋盘格子状态 | 初始状态、占格、越界 |
| 规则 | 错人落子、胜负、平局 |
| 终端 | 管道棋谱的输出和返回码 |
| 人机落子 | `games/tictactoe/02-cpu-opponent/build-and-run.sh` |
| 逐行 JSON | `games/tictactoe/03-line-protocol/build-and-run.sh`，以及 `games/tictactoe/python/replay.py` 的协议校验 |
| Python 回放 | `D:/ProgramData/miniforge3/python.exe -m unittest games/tictactoe/python/replay.py` |
| 本地 Web 适配 | `D:/ProgramData/miniforge3/python.exe -m unittest games/tictactoe/python/web.py`；必要时用浏览器黑盒测试页面与 API |
| Quarto、主题或代码块标题 | `verify_content.py`、根目录 `quarto render` |
| C++、CMake、Bash 或格式注释 | 该目录 `build-and-run.sh` |

本地 Web 只监听回环地址，当前不作为可部署 HTTP 阶段验收；WebSocket 仍没有代码。

验证入口：各阶段目录内 `build-and-run.sh` 一键完成该阶段的配置、编译、格式与静态检查、CTest 和运行；根目录不放 CMake 文件，不做根级统一构建。文档改动运行 `verify_content.py` 与仓库根 `quarto render`。
