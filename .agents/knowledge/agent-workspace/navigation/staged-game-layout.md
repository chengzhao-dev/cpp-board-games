---
kb_id: "bg-staged-game-layout-v1"
title: "编号阶段目录依据"
domain: "agent-workspace"
subdomain: "navigation"
tags: [stages, directory-layout, configuration]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-10-02"
chunk_strategy: "semantic_heading"
estimated_tokens: 1150
---

# 编号阶段目录依据

本文件供 Agent 判断游戏阶段目录、配置归属和章节映射使用。井字棋读者说明在 `content/tictactoe/02-project-layout.qmd`。

## 目录命名规则

- `games/<game>/` 下使用两位数字编号阶段目录。井字棋当前有 `01-cli-game/`、`02-cpu-opponent/`、`03-line-protocol/`，分别提供双人终端、人机对手和逐行协议三种真实行为。只有出现新的真实行为时才继续新建。
- 编号表示学习和实现顺序，不表示 C++ 命名空间、CMake target 或版本号。
- 阶段目录名使用小写 kebab-case；游戏目录名与 C++ 命名空间一致（如 `tictactoe`），由原 `tic-tac-toe` 更名对齐，此后保持稳定。
- 读者正文不把该目录叫做探针或最小工程。它是一局可下完的双人终端井字棋。

## 阶段项目定义

- 每个阶段目录都是一个完整项目：可独立作为 VS Code 工作区打开，可独立配置、构建、运行或测试。
- 每个阶段拥有自己的 `.clang-format` 和 `.vscode/`；`games/<game>/` 根目录不保留这些运行时配置。
- `.agents/skills/cpp-development/assets/config/.clang-format` 只是新阶段初始化模板，不是任何阶段的运行时依赖。
- 根目录不放 CMake 文件；每个阶段目录自带完整 `CMakeLists.txt`，阶段内的 target、源文件和测试由阶段自己的 CMake 管理，依据见标识 `bg-cmake-conventions-v1` 的知识文件。
- 引入库 target 的阶段改用组件式布局：库组件目录（`tictactoe/`，含 `include/`、`src/` 与自己的 `CMakeLists.txt`）、`apps/`（主程序）与 `tests/` 各带 `CMakeLists.txt`，顶层只做工程声明、产物目录、`enable_testing()` 与 `add_subdirectory`；源码树不建 `lib/`，`lib` 只是 `build/` 下的产物目录（依据与 target 命名表见标识 `bg-cmake-conventions-v1` 的知识文件「组件化阶段布局」）。
- 组件式 `apps/` 可含私有 `include/` 与 `src/`：全部 `.cpp`（含 `main.cpp`）放在 `apps/src/`，展示等助手头文件放在 `apps/include/`；`target_include_directories(app PRIVATE …/include)`，不得把 `apps/include` 设为 PUBLIC 或当作第二套规则库。`apps/` 根目录通常只留 `CMakeLists.txt`。
- 组件式阶段的 PUBLIC include 根指向库组件的 `include/`；库对外头文件直接放在该根下（如 `include/board.h`、`include/game.h`），项目头一律写裸文件名引号 include（`#include "board.h"`）；禁止 `include/<namespace>/` 子目录与 `"tictactoe/….h"` 前缀路径；依据见标识 `bg-google-cpp-style-v1` 的知识文件「Header Files」。
- 井字棋前五章共用 `games/tictactoe/01-cli-game/`。不为每一章复制一份阶段快照。没有源文件的章不注册进 `_quarto.yml`。

## 章节映射规则

- `content/<game>/index.qmd` 是游戏入口页，不编号；YAML 设 `body-classes: index-page` 与 `number-sections: false`。
- 根 `index.qmd` 形态：hero 加 1–2 句总起，正文用 `##` 分组（当前游戏 + 后续棋类）；当前游戏组至多 4 张高光 landing-card（带 CTA，按由易到难排序），后续棋类用 `.landing-card.coming-soon` 占位卡（无链接、无 CTA，样式自带「规划中」角标）。根首页不写总体原则列表与完成状态免责段，原则与状态口径只进 `.agents` 知识。
- 入口页形态：短引言（1–2 句）+ `feature-grid` / `landing-card`（每卡：章节 title 链接 + 一句职责）；按 `_quarto.yml` 阅读顺序排满该游戏全部章节；不放目录对照长表、不放长状态段。后续其他棋类同此。
- 井字棋章节编号和阶段目录编号不必相同：前五章都指向 `01-cli-game`。路由表见 `.agents/skills/cpp-development/references/stages/tictactoe.md`。
- `_quarto.yml` 的章节顺序与阶段入口页的阅读顺序保持一致。

## 配置注释约定

- `.clang-format`、`.clang-tidy`、`.clangd` 遵循标识 `bg-comment-style-v1` 的知识文件「工具配置 YAML」：短 LLVM 文件头、单行分组或邻接注释；禁止文件顶部长篇政策块、知识库 id 指针与模板元叙述。脚手架从 `assets/config/` 复制后，阶段可按需补阶段特有 `-I…` 邻接注释，不得把「两仓/复制本文件」类旁白留在阶段副本。
- `.vscode/settings.json` 和 `extensions.json` 保持 JSONC 格式，使用注释分段；不得改写成严格 JSON。
- `CMakeLists.txt` 与 `build-and-run.sh` 按职责分段，文件头与段使用 LLVM 式定宽 `===` 横幅，注释解释意图与取舍，面向新人可读；完整规范见 标识 `bg-comment-style-v1` 的知识文件。
- Python 相关编辑器配置不提前保留为整条路线的编辑器预设，跟随首个真实包含 Python 代码的阶段配置（black-formatter 需 WSL 远程端安装，未用即噪音）。

## 阶段脚本与文档展示约定

- 每个阶段可在阶段根放置一个 `build-and-run.sh`：依次完成配置（每次无条件重新配置，不判断 `build/` 是否已存在，依据见标识 `bg-cmake-conventions-v1` 的知识文件）、编译、CTest 和运行，并保持可执行权限；阶段内不额外拆分 build/run 多个脚本，除非复杂度确实需要。
- 含 SHARED 库的阶段，脚本用 `STAGE_LIB` 常量与 `run_with_stage_libs()` 封装库路径：`env LD_LIBRARY_PATH=...` 只包住单条命令作临时加固，主路径是可执行文件的 `BUILD_RPATH`；运行步骤用子 shell `cd` 进 `build/bin` 执行可执行文件。写法与禁改项见标识 `bg-cmake-conventions-v1` 的知识文件。
- Quarto 章节展示阶段真实代码时默认内联摘录关键片段：片段逐字摘自源文件并标注省略范围（规则见标识 `bg-qmd-element-cases-v1` 的知识文件）；确需完整展示的短文件可用 `{{< include >}}` 短代码，路径相对 qmd 文件解析（如 `content/tictactoe/` 中的章节引用 `../../games/<game>/<阶段>/...`）。include 的文件必须是真实存在的源文件，片段与代码副本都不得与源文件不一致。

## 实现方式边界

- 阶段之间采用复制快照或持续演进实现，由实际变更成本决定；无论哪种方式，每个阶段都必须保持可配置、可构建、可测试和可追溯。
- 井字棋前三个阶段已经实现并分别可独立构建：`01-cli-game` 保留双人终端，`02-cpu-opponent` 在同一规则模型上增加对手，`03-line-protocol` 在应用层追加机器可读快照。终端打印和读入留在 `apps/`，规则与对手源码编进阶段内 `tictactoe` 动态库；Python 回放和本地 Web 适配属于协议层之后的辅助程序。
