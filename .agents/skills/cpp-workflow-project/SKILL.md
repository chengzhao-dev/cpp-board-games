---
name: cpp-workflow-project
description: 井字棋 C++ 工程事实：源码根、target、构建入口与阶段表；通用源码四步、CMake 三步与构建三步由插件 developing-cpp、configuring-cmake、building-cpp 提供
metadata:
  short-description: 井字棋工程事实
---

# 井字棋 C++ 工程

本书的 C++ 工作事实：通用技能由插件 `dsh-cpp-workflow` 提供（`developing-cpp` 定行为/边界/声明/实现，`configuring-cmake` 定 target/模块/CMake 检查，`building-cpp` 定构建/工具配置/通过检查），本文件只写本项目自己的选择。类分工与设计依据见 `decisions/architecture.md`。

## 适用场景

- 修改 `games/tictactoe/` 的源码、CMake、测试或 `running-build.sh`。
- 新建下一款棋盘游戏工程，或调整 `stages/<game>.md`。
- 不适用：通用棋规与棋盘设计走插件 `developing-cpp` 的 project-design 参考，文档走插件 `writing-quarto` 与本仓 `quarto-book-project`。

## 工程事实

| 项 | 值 |
| --- | --- |
| 工程名 | 井字棋（`tictactoe`），无图形界面的终端程序 |
| 源码根 | `games/tictactoe/`（仓库根不放 CMake 文件） |
| 库 target | `tictactoe`（SHARED，`tictactoe/` 下；公开头文件放 `tictactoe/include/`） |
| 程序 target | `app`（`apps/` 下，连 `tictactoe`）；测试 target `tictactoe_test`（`tests/` 下，连 `tictactoe` 与 GoogleTest） |
| 构建目录 | `games/tictactoe/build/`（`lib/`、`bin/` 为阶段产物） |
| 入口命令 | `python .agents/scripts/building-wsl.py tictactoe`（内部进 WSL2 Ubuntu 跑 `running-build.sh`；Linux CI 直接跑 `bash running-build.sh`） |
| 阶段表 | `stages/stage-table.md`，`scope.py` 解析的唯一数据源 |
| 编码与行尾 | 根 `.gitattributes`、`.editorconfig`；`.sh` 用 LF，`.bat`/`.cmd` 用 CRLF，C++ 源文件 UTF-8 无 BOM、LF |

## P0 硬约束

1. WSL2 Ubuntu 内用 C++23、Clang、CMake、Ninja；CTest 在工程内注册并运行；代理不在 PowerShell 里输入 `wsl.exe` 或 `bash`。
2. 命名按 Google C++ 风格加本仓偏离白名单；谓词用 `Is/Has/Can/Completes` 等肯定式，`Check/Validate` 不做纯 bool getter，细则见插件 `developing-cpp` 的 `references/naming.md`。`.clang-format`、`.clang-tidy`、`.clangd` 随工程存放，不引用仓库根配置。
3. C++23 与警告等级由 `cmake/CompileSettings.cmake` 的 `CompileSettings_SetCxxStandard`、`CompileSettings_SetWarnings` 统一声明与施加；`environment.json` 的 `standard` 与 `.clang-format` 的 `Standard: Latest` 同步保持一致。
4. 库与主程序分开 target，主程序链接库；终端读入编进 `app`，不另建库。
5. 每款游戏自带工程，可独立配置、编译和运行；当前 tictactoe 构建动态库、`app` 与棋盘测试，终端层保留源码，共享库按至少两款游戏的实际重复提取。
6. CTest 只在各游戏工程内注册并运行，仓库根不构建、不注册测试。
7. 章节、代码目录与阶段表三处对齐；改代码先看对应 `content/tictactoe/<章节>.qmd` 的当前阶段。
8. 环境三轴记录在 `environment.json`；换主机、换编译器或换构建宿主时先改它，再重跑检查。
9. 头文件用路径式 Google 守卫 `#ifndef <PROJECT>_<PATH>_<FILE>_H_`，以 `games/tictactoe/` 为源码树顶；不用 `#pragma once`，也不与守卫并存。槽位见插件 `developing-cpp` 的 `references/file-template.md`。

## 编辑器补全

- 补全由 clangd 提供，配置分两处：`games/tictactoe/.clangd` 给编译数据库与补充参数，仓库根 `.vscode/settings.json` 给 `--query-driver` 与 `clangd.path`。
- Windows 上的 Cursor 必须打开 WSL 远程窗口，clangd 才用得到 `/usr/bin/clangd` 与 `/usr/bin/clang++`；扩展装在 WSL 侧，C/C++ 扩展的 IntelliSense 关闭。
- 补全或诊断不对时，先在 WSL 里跑 `clangd --check=games/tictactoe/apps/src/main.cpp --query-driver=/usr/bin/clang++`，看 `Compile command from CDB` 是否带 `-std=c++23`；`tweak: ExtractFunction ==> FAIL` 是检查工具的自测项，不是源码诊断。

## 工作流程

1. 用 `python .agents/scripts/scope.py <game>/<stage>` 取目标（如 `tictactoe/03-board`），读本文件与插件 `developing-cpp` 对应步骤。
2. 按技能推进：源码四步（定行为 → 定边界 → 定声明 → 定实现）→ CMake 三步（定 target → 定模块 → 通过检查）→ 构建三步（定构建 → 定工具配置 → 通过检查）。
3. CMake 引用插件 `configuring-cmake`，构建与工具配置引用插件 `building-cpp`；本项目只覆盖确有差异的部分并写明理由。
4. 改完跑 `python .agents/scripts/building-wsl.py tictactoe`，再跑 `python .agents/scripts/checking-book.py` 核对受影响的章节。

## 完成判据

- [ ] 对应章节代码可独立构建、运行 `app` 成功，构建无新警告，CTest 13 条全部通过。
- [ ] 源码按 `.clang-format` 排版，`clang-tidy` 无新警告；构建脚本不再代跑这两项，编辑时手动检查。
- [ ] `stages/<game>.md` 的状态与正文实际进度一致。
- [ ] `python .agents/scripts/checking-book.py` 通过；跨域改动同样跑这一条。
