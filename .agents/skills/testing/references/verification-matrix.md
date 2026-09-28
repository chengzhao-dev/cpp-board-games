# 改动范围与验证矩阵

供 Agent 在改动后快速圈定验证范围，避免为确认验收边界而通读读者文档。面向读者的同表位于 `content/tic-tac-toe/06-cli-and-acceptance.qmd`，两处需同步维护。

| 改动 | 必须验证 |
| --- | --- |
| 阶段 CMake 或工具链 | 该阶段 `build-and-run.sh`（配置、编译、CTest、运行） |
| 棋盘和值类型 | 初始状态、边界、位置转换 |
| 规则 | 合法/非法动作、回合、胜负、平局 |
| CLI | 少量端到端输入、输出和返回码 |
| AI | 必胜、防守、合法动作、确定性 |
| Python subprocess | 启动、输入输出、退出码、超时 |
| JSON | 合法消息、非法消息、错误结构 |
| HTTP | 状态码、`response.ok`、JSON 内容 |
| WebSocket | 建连、消息、错误、正常关闭 |
| Quarto、主题或代码块标题 | `verify_content.py`、根目录 `quarto render`，检查链接、结构、filename 和响应式 CSS |
| C++、CMake、Bash 或 `.clang-format`/`.clang-tidy` 注释 | `bash -n`、阶段 `build-and-run.sh`、`clang-format --dry-run --Werror`，命名经阶段 `.clang-tidy`（clangd 实时报告），并检查注释与真实代码同步 |

验证入口：各阶段目录内 `build-and-run.sh` 一键完成该阶段的配置、编译、CTest 和运行；根目录不放 CMake 文件，不做根级统一构建。文档改动运行 `verify_content.py` 与仓库根 `quarto render`。
