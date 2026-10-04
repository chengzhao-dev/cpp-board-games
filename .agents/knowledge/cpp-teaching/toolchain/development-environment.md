---
kb_id: "bg-development-environment-v1"
title: "开发环境依据"
domain: "cpp-teaching"
subdomain: "toolchain"
tags: [wsl, vscode, clangd, environment]
level_range: [0, 5]
dependencies: [bg-cmake-conventions-v1]
created: "2026-09-26"
updated: "2026-09-30"
chunk_strategy: "semantic_heading"
estimated_tokens: 1200
---

# 开发环境依据

本项目主线使用 WSL Ubuntu，Windows 侧主要用于编辑、浏览器展示和后续兼容性验证。井字棋是无图形界面的终端程序。

## 计划工具链

- C++20
- Clang/clang++
- CMake
- Ninja
- CTest
- clang-format、clang-tidy、clangd
- Python 3
- Black
- Quarto

开始实现前，应在实际 WSL 环境确认版本和可执行路径。当前文档阶段不安装依赖、不伪造构建结果。实现阶段的构建、测试和文档命令必须与实际目标一致。

## 编辑器

井字棋目录使用本地 `.clang-format` 和 `.vscode/` 管理可复用开发约定；`.agents/skills/cpp-development/assets/config/.clang-format` 只作为通用脚手架，不是井字棋运行时依赖。`.vscode/` 只放在阶段等子目录内，仓库根目录不放（根目录 `.vscode/` 已删除，`.gitignore` 中以 `/.vscode/` 守卫）。井字棋从 `games/tictactoe/` 目录独立执行时，不依赖仓库根目录或 `.config/`；未来其他游戏和游戏内脚本也遵循相同边界。不得写入用户机器绝对路径、密钥或不存在的实现目标。Python 代码使用 Black 默认风格。

`.vscode/extensions.json` 只提供扩展推荐，不控制扩展安装位置。通过 VS Code Remote - WSL 打开仓库时，clangd、CMake Tools、Python 等需要访问编译器和源码的扩展安装在 WSL 远程端，VS Code UI 运行在 Windows 侧。终端、编译器、CMake、CTest 和格式化命令都在 WSL 内执行。

C/C++ 格式化由 clangd 扩展（`llvm-vs-code-extensions.vscode-clangd`）承担，作为 `[cpp]`/`[c]` 的 `editor.defaultFormatter`；clangd 直接读取阶段内 `.clang-format`。不使用 `xaver.clang-format`：该扩展长期未维护，在 WSL 远程端安装与格式化不可用（2026-09 决策）。不配置 `clang-format.executable`。

Python 编辑器配置（`ms-python.black-formatter`、`python.analysis.typeCheckingMode`）不提前保留在没有 Python 代码的阶段：black-formatter 必须在 WSL 远程端安装才可用，未用即产生"格式化器不可用"噪音（2026-09 决策）。Python 编辑器配置跟随首个真实包含 Python 代码的阶段，在其 `.vscode/` 中配置。

clangd 依赖 `CMAKE_EXPORT_COMPILE_COMMANDS=ON` 生成的 `build/compile_commands.json`，阶段目录作为工作区打开时零配置命中；查找顺序、重载时机与手动兜底见标识 `bg-cmake-conventions-v1` 的知识文件。clangd 的 clang-tidy 诊断读取阶段目录 `.clang-tidy`；`.vscode/settings.json` 不传 `--clang-tidy=false`，编辑器与阶段 `build-and-run.sh` 的格式与静态检查步骤看到同一套诊断。若 `build` 已零警告而编辑器仍黄，先确认阶段 `build/compile_commands.json` 存在，再执行 clangd Restart。

## 文档预览（Windows 与 CI）

- 整书渲染与含 `{python}` 的章节预览：优先 `run.ps1 render` / `run.ps1 preview`（注入 `QUARTO_PYTHON` = `config.toml` 的 `python`）。
- CI（Ubuntu）把 `config.toml` 的 python 改成 runner 的 `python3` 后装依赖再裸 `quarto render`；本地 Windows 不依赖 PATH 上的 `python3`。
- Cursor Quarto Preview：用 `Python: Select Interpreter` 选与 `config.toml` 相同的解释器；用户级 `QUARTO_PYTHON` 仅作镜像桥接。细节见标识 `bg-coords-diagram-v1`。

VS Code 专用 JSON 配置支持 JSONC 注释；程序读取的普通 JSON 保持严格 JSON。

终端主用 VS Code 集成终端和 Windows Terminal；脚本默认输出纯文本阶段标题和错误提示，底层工具是否着色由工具自身决定。展示形式规范见标识 `bg-terminal-output-style-v1` 的知识文件。

## 文档验证

Quarto 源文件位于 `content/`、`index.qmd` 和 `_quarto.yml`。`_book/` 与 `.quarto/` 是生成物或缓存，不作为源文件手工修改。
