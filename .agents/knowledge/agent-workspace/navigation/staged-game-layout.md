---
kb_id: "bg-staged-game-layout-v1"
title: "编号阶段目录依据"
domain: "agent-workspace"
subdomain: "navigation"
tags: [stages, directory-layout, configuration]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-09-28"
chunk_strategy: "semantic_heading"
estimated_tokens: 1150
---

# 编号阶段目录依据

本文件供 Agent 判断游戏阶段目录、配置归属和章节映射使用；面向读者的解释位于 `content/tic-tac-toe/02-toolchain-probe.qmd` 和 `content/tic-tac-toe/07-incremental-roadmap.qmd`。

## 目录命名规则

- `games/<game>/` 下使用两位数字编号阶段目录：`01-toolchain-probe/`、`02-board-and-state/`……
- 编号表示学习和实现顺序，不表示 C++ 命名空间、CMake target 或版本号。
- 阶段目录名使用小写 kebab-case；游戏目录名不变（如 `tic-tac-toe`）。

## 阶段项目定义

- 每个阶段目录都是一个完整项目：可独立作为 VS Code 工作区打开，可独立配置、构建、运行或测试。
- 每个阶段拥有自己的 `.clang-format` 和 `.vscode/`；`games/<game>/` 根目录不保留这些运行时配置。
- `.agents/skills/cpp-development/assets/config/.clang-format` 只是新阶段初始化模板，不是任何阶段的运行时依赖。
- 根目录不放 CMake 文件；每个阶段目录自带完整 `CMakeLists.txt`，阶段内的 target、源文件和测试由阶段自己的 CMake 管理，依据见标识 `bg-cmake-conventions-v1` 的知识文件。
- 引入库 target 的阶段改用组件式布局：库组件目录（`tic_tac_toe/`，含 `include/`、`src/` 与自己的 `CMakeLists.txt`）、`apps/`（CLI）与 `tests/` 各带 `CMakeLists.txt`，顶层只做工程声明、产物目录、`enable_testing()` 与 `add_subdirectory`；源码树不建 `lib/`，`lib` 只是 `build/` 下的产物目录（依据见标识 `bg-cmake-conventions-v1` 的知识文件）。
- 终端双人井字棋的编号目录为 `01-toolchain-probe` 到 `05-cli-and-acceptance`；`06-ai` 到 `10-websocket` 只在真实开始实现时创建，不提前建立空目录。

## 章节映射规则

- `content/<game>/index.qmd` 是游戏入口页，不编号；YAML 设 `body-classes: index-page` 与 `number-sections: false`。
- 根 `index.qmd` 形态：hero 加 1–2 句总起，正文用 `##` 分组（当前游戏 + 后续棋类）；当前游戏组至多 4 张高光 landing-card（带 CTA，按由易到难排序），后续棋类用 `.landing-card.coming-soon` 占位卡（无链接、无 CTA，样式自带「规划中」角标）。根首页不写总体原则列表与完成状态免责段，原则与状态口径只进 `.agents` 知识。
- 入口页形态：短引言（1–2 句）+ `feature-grid` / `landing-card`（每卡：章节 title 链接 + 一句职责）；按 `_quarto.yml` 阅读顺序排满该游戏全部章节；不放目录对照长表、不放长状态段。后续其他棋类同此。
- 章节编号与代码阶段编号不一定是同一个数字：横向说明页（如 `01-scope-and-principles.qmd`，title「先看清工程」）占用编号但不对应代码阶段；井字棋从 `02-toolchain-probe.qmd` 起与代码阶段一一对应。
- 横向说明页必须明确标注为说明页，不冒充实现阶段的代码快照。
- `_quarto.yml` 的章节顺序与阶段入口页的阅读顺序保持一致。

## 配置注释约定

- `.clang-format` 使用 YAML 注释按职责分段（基础风格、行宽、缩进等），注释解释意图，不逐行重复键名。
- `.vscode/settings.json` 和 `extensions.json` 保持 JSONC 格式，使用注释分段；不得改写成严格 JSON。
- `CMakeLists.txt` 与 `build-and-run.sh` 按职责分段，文件头与段使用 LLVM 式定宽 `===` 横幅，注释解释意图与取舍，面向新人可读；完整规范见 标识 `bg-comment-style-v1` 的知识文件。
- Python 相关编辑器配置不提前保留为整条路线的编辑器预设，跟随首个真实包含 Python 代码的阶段配置（black-formatter 需 WSL 远程端安装，未用即噪音）。

## 阶段脚本与文档展示约定

- 每个阶段可在阶段根放置一个 `build-and-run.sh`：依次完成配置（每次无条件重新配置，不判断 `build/` 是否已存在，依据见标识 `bg-cmake-conventions-v1` 的知识文件）、编译、CTest 和运行，并保持可执行权限；阶段内不额外拆分 build/run 多个脚本，除非复杂度确实需要。
- 含 SHARED 库的阶段，脚本的测试与运行步骤用 `env LD_LIBRARY_PATH=...` 包住单条命令作临时加固，主路径是可执行文件的 `BUILD_RPATH`，写法与禁改项见标识 `bg-cmake-conventions-v1` 的知识文件。
- Quarto 章节展示阶段真实代码时默认内联摘录关键片段：片段逐字摘自源文件并标注省略范围（规则见标识 `bg-qmd-element-cases-v1` 的知识文件）；确需完整展示的短文件可用 `{{< include >}}` 短代码，路径相对 qmd 文件解析（如 `content/tic-tac-toe/` 中的章节引用 `../../games/<game>/<阶段>/...`）。include 的文件必须是真实存在的源文件，片段与代码副本都不得与源文件不一致。

## 实现方式边界

- 阶段之间采用复制快照或持续演进实现，由实际变更成本决定；无论哪种方式，每个阶段都必须保持可配置、可构建、可测试和可追溯。
- 尚未实现的阶段不得创建 C++、CMake、测试或 Python 文件，也不得在文档中记录为已完成。
