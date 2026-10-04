---
kb_id: "bg-cmake-conventions-v1"
title: "CMake 约定依据"
domain: "cpp-teaching"
subdomain: "toolchain"
tags: [cmake, build, clangd, ninja]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-10-01"
chunk_strategy: "semantic_heading"
estimated_tokens: 4200
---

# CMake 约定依据

本文件记录 2026-09 联网核实（CMake 官方文档、clangd 官方文档、《Professional CMake: A Practical Guide》）后确定的 CMake 实践决策，供 Agent 编写和评审各阶段 `CMakeLists.txt` 时使用。

## 构建入口与根目录边界

撤销此前引入的根 `CMakeLists.txt` 编排（原设想为 `add_subdirectory` 逐阶段追加）。现行约定：每个阶段目录自带完整 `CMakeLists.txt`，通过该目录的 `build-and-run.sh` 独立完成配置、编译、测试和运行；根目录不放任何 CMake 文件，一次性脚本与中间产物只进 `temp/`。规则出处是 AGENTS.md「CMake 约定」与「工作规则」。

## C++ 标准声明方式

- 使用 `target_compile_features(<target> PRIVATE cxx_std_20)`，不使用 `set(CMAKE_CXX_STANDARD 20)`。
- 原因：`target_compile_features` 是 target 级"用法要求"（usage requirement），将来阶段演化为库时改成 `PUBLIC` 即可让标准要求随 target 传播给链接方；`CMAKE_CXX_STANDARD` 是全局变量，影响其后创建的所有目标、不随依赖传播。这与仓库 AGENTS.md 的 target-based 约定一致。
- `set(CMAKE_CXX_STANDARD ...)` 只对"自用顶层应用"是可接受的简化写法；本项目仍统一用 target 命令。

## 源文件收集方式

- `add_executable` / `add_library` 中显式逐行列出源文件，不使用 `file(GLOB)`。
- 官方依据：CMake `file()` 文档明确"不建议用 GLOB 收集源文件"——新增或删除源文件时若 `CMakeLists.txt` 未变，构建系统不会自动重新配置，导致新文件被静默漏编或已删文件引发构建错误。
- `file(GLOB ... CONFIGURE_DEPENDS)` 可让构建系统每次重查文件列表，但官方仍有保留意见（部分生成器/平台开销大、可移植性有限），不作为默认方案。
- 排版：源文件多于一个时每行一个、按字母序排列，保持 diff 清晰。

## 命名大小写惯例

CMake 对命令和关键字大小写不敏感，无官方强制风格；本项目遵循社区事实标准：

- 命令一律小写（`project()`、`add_executable()`；全大写命令是 CMake 2.x 遗风）。
- 关键字大写：`PRIVATE`、`PUBLIC`、`INTERFACE`、`ON`/`OFF`。
- 自定义局部变量小写 snake_case；缓存/全局变量大写（与 `CMAKE_*`、`PROJECT_*` 呼应）。
- `project()` 项目名与 target 命名保持同风格（本项目用小写 snake_case）。

## clangd 与 CMake 配套

- 依赖机制：CMake 配置时开启 `CMAKE_EXPORT_COMPILE_COMMANDS=ON`，在 build 目录生成 `compile_commands.json`（Ninja/Makefile 生成器支持）。组件化阶段顶层 `CMakeLists.txt` 显式写这一行，不只在脚本里传 `-D`，保证绕过脚本直接配置时 clangd 仍有真实编译参数。
- 自动发现：clangd 按"源文件所在目录 → 各级父目录 → 各目录下的 `build/` 子目录"顺序查找该文件；阶段目录名保持 `build/` 作为构建目录名即可零配置命中，不需要 `--compile-commands-dir` 或 `.clangd` 配置。若未来构建目录改名，用项目根 `.clangd` 文件指定：`CompileFlags: CompilationDatabase: <目录名>`。
- 未构建时兜底：阶段 `.clangd` 的 `CompileFlags.Add` 提供 `-std=c++20` 等基础参数与 `-Itictactoe/include`（相对 `.clangd` 所在目录解析，指向库组件 PUBLIC include 根），让首次构建前编辑器也能解析 `"game_state.h"` 等裸项目头；`Suppress: pp_file_not_found` 只为压掉首次未构建时的 include 报错噪音，正式阶段必须以 `build/compile_commands.json` 为准，构建后诊断应来自真实编译参数。
- 更新时机：修改 `CMakeLists.txt`（如新增源文件、改编译选项）后必须重新运行 CMake 配置，`compile_commands.json` 才会更新；clangd 监听该文件变化并自动重载索引。索引停滞时手动兜底：VS Code 命令面板 "clangd: Restart language server"。
- 常见坑：未被任何 target 收进的源文件（如刚创建还没加入 `add_executable` 的文件）在 `compile_commands.json` 中没有编译条目，clangd 对其只做启发式分析；先加入 target 并重新配置，补全才会准确。

## CMakeLists.txt 注释分段

- 阶段级 `CMakeLists.txt` 按职责分段（工程声明 / 可执行目标 / 测试），段与文件头使用 `#===...===#` 定宽横幅。
- 注释解释意图与取舍（如"为什么不用 GLOB"），不逐行复述命令参数；完整规范见 标识 `bg-comment-style-v1` 的知识文件。

## 产物输出目录

联网核实（CMake 输出目录属性文档、GNUInstallDirs 文档、llvm-project `llvm/CMakeLists.txt` 原文）后确定：各阶段产物按 LLVM 构建树惯例归入 `build/bin`、`build/lib`，不在 `build/` 根平铺。

- **默认行为**：不设置任何输出属性时，产物落在当前二进制目录（`CMAKE_CURRENT_BINARY_DIR`）；单目录阶段即 `build/` 根——阶段 01 初版正是如此，现已改为归类。
- **三组输出属性分工**：

 | 属性 | 收纳产物 |
 |---|---|
 | `RUNTIME_OUTPUT_DIRECTORY` | 可执行文件；Windows DLL 本体 |
 | `LIBRARY_OUTPUT_DIRECTORY` | Linux `.so`、macOS `.dylib`（含符号链接链） |
 | `ARCHIVE_OUTPUT_DIRECTORY` | 静态库 `.a`/`.lib`；Windows DLL 的导入库 `.lib` |

- 多配置生成器（Visual Studio、Xcode、Ninja Multi-Config）会在指定目录下自动追加 `Debug/`、`Release/` 等 per-config 子目录；本仓库单配置 Ninja 不追加。属性值支持 generator expressions，可用 `RUNTIME_OUTPUT_DIRECTORY_<CONFIG>` 按构建类型覆盖。
- **本仓库决策**：每个阶段 `CMakeLists.txt` 在创建 target 前用目录变量声明 `set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")`；引入库 target 时补 `set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ...)` 与 `set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ...)`，同样指向 `${CMAKE_BINARY_DIR}/lib`。同名目录变量在 target 创建时初始化对应 target 属性，三组属性也有 `<CONFIG>` 变体。
- **为何目录变量而非 target 属性**：产物位置是构建布局配置，不是 target 的用法要求；目录变量一处声明即覆盖本目录现在与未来的所有 target（LLVM 正是此做法），不必每加一个 target 重复 `set_target_properties`。这不违背仓库"统一用 target 命令"约定——该约定约束的是 `CMAKE_CXX_STANDARD` 这类用法属性，见上文「C++ 标准声明方式」。
- **安装侧**：沿用 GNUInstallDirs 默认（可执行 `bin`、库 `lib`、头文件 `include`），与构建树分类互相印证；将来引入 `install()` 规则时直接依赖其默认值，不另行定制。
- **附带事实**：CTest 的 `add_test(COMMAND <target>)` 按 target 名解析可执行位置，产物搬家不影响测试注册与运行；`compile_commands.json` 与 clangd 也不受影响。
- 来源：[RUNTIME_OUTPUT_DIRECTORY](https://cmake.org/cmake/help/latest/prop_tgt/RUNTIME_OUTPUT_DIRECTORY.html)、[GNUInstallDirs](https://cmake.org/cmake/help/latest/module/GNUInstallDirs.html)、[llvm-project llvm/CMakeLists.txt](https://github.com/llvm/llvm-project/blob/main/llvm/CMakeLists.txt)（`set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${LLVM_TOOLS_BINARY_DIR})` 等三行，bin/lib 分类的直接先例）。

## 构建目录与缓存

联网核实（CMake Ninja 生成器文档、CMake Discourse、microsoft/vscode-cmake-tools issue #3978）后确定，`build-and-run.sh` 一键脚本采用**每次无条件重新配置**，不做"`build/CMakeCache.txt` 已存在就跳过"的判断。

- 配置是幂等的：重复运行只耗时一两秒，编译仍由 Ninja 增量进行，已编译的目标不会重编。
- 跳过式写法的风险边界（均属"后续迭代才会踩到"的坑）：
 - **配置参数漂移**：`-D` 参数只写入首次配置生成的 `CMakeCache.txt`；以后修改脚本中的配置行，已存在的 `build/` 不会吸收新参数，静默失配。
 - **半成品 build 目录**：首次配置中途被打断时，`CMakeCache.txt` 可能已生成而 `build.ninja` 尚未生成；以 `CMakeCache.txt` 存在与否作为"已配置"判据会把半成品误判为可用，直到编译阶段才报出难以理解的错误。
 - **缓存陈旧**：换编译器会触发 CMake 致命错误（"You have changed variables that require your cache to be deleted..."），切分支后旧缓存值也会持久残留；社区共识是此类情况直接删除构建目录重新配置。
- 安全面：迭代 `CMakeLists.txt` 本身（加源文件、target、测试）不需要担心配置跳过与否——Ninja 生成器在 `build.ninja` 中内置重新生成规则，检测到 `CMakeLists.txt` 变化后 `cmake --build` 会自动重跑配置再继续编译。
- 手动兜底：换编译器、生成器或出现无法解释的构建异常时，`rm -rf build` 后重跑脚本。
- 演进方向：`CMakePresets.json` 是 CMake 官方承载配置参数的机制（`cacheVariables` + `cmake --preset`，IDE/CI 通用）。`01-cli-game` 引入 GoogleTest 后配置参数并未增多（FetchContent 参数固定在 `tests/CMakeLists.txt` 内，脚本 `-D` 参数与阶段 01 相同），Presets 继续延后到配置参数再多时评估。
- 来源：[CMake Ninja 生成器文档](https://cmake.org/cmake/help/latest/generator/Ninja.html)、[microsoft/vscode-cmake-tools #3978](https://github.com/microsoft/vscode-cmake-tools/issues/3978)（官方建议"删除构建目录重新配置以丢弃陈旧配置"）。

## 组件化阶段布局

阶段从单文件演进为组件式布局，首个使用目录是 `01-cli-game/`：

- 顶层 `CMakeLists.txt` 只做工程声明、产物目录、`enable_testing()` 和 `add_subdirectory`；各组件 target 由组件目录自己的 `CMakeLists.txt` 定义。库组件 `tictactoe/` 拥有扁平 `include/`（头文件直接放在该目录下，如 `include/game_state.h`）、`src/` 与库 target `tictactoe`；`apps/` 拥有主程序；`tests/` 拥有测试。禁止再建 `include/tictactoe/` 这类命名空间子目录。
- `apps/` 采用私有 `include/` + `src/`：全部 `.cpp`（含 `main.cpp`）在 `apps/src/`，助手头在 `apps/include/`；`add_executable` 显式列出源文件；`target_include_directories(app PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/include")`。`apps/include` 不是 PUBLIC 规则库头，仅供本可执行目标使用。
- `target_include_directories` 的 PUBLIC 根指向库组件的 `include/`：使用方按裸文件名引号 include（`#include "game_state.h"`），与标识 `bg-google-cpp-style-v1` 的知识文件「Header Files」及有意偏离白名单第 9 条一致。
- **路径一律加双引号**：凡展开后是文件系统路径的变量（如 `"${CMAKE_CURRENT_SOURCE_DIR}/include"`、`"${CMAKE_BINARY_DIR}/bin"`、`BUILD_RPATH "$ORIGIN/../lib"`）都写成双引号包裹；避免路径含空格时被 CMake 拆成多个参数。相对目录名字面量（如模板里的 `include`）无变量时可省略引号。- 组件化阶段顶层 `CMakeLists.txt` 显式 `set(CMAKE_EXPORT_COMPILE_COMMANDS ON)`，不只依赖 `build-and-run.sh` 的 `-D` 参数；阶段目录本身可独立作为工作区打开。
- 目标命名固定为下表，与本仓模板 `shared-library`（`greeting` 库 + `app` 可执行文件）一致：

 | 角色 | 命名 | 本仓示例 |
 |---|---|---|
 | 库 target | 与组件目录同名，不加 `lib` 前缀 | `add_library(tictactoe SHARED …)` → `libtictactoe.so` |
 | 阶段主程序 target | 固定用 `app` | `build/bin/app` |
 | 冒烟测试名 | 跟随主程序 | `app_smoke` |
 | 行为测试可执行文件 | 按被测行为命名 | `tictactoe_game_state_test` |
 | 脚本主程序常量 | `APP_NAME` | `readonly APP_NAME="app"` |

 依据：CMake 逻辑 target 全局唯一，库与可执行文件不能同名（CMP0002），库名用组件名、主程序用 `app` 作别名即可区分；库名手写 `lib` 前缀会得到 `liblib….so`，平台前缀由 CMake 自动加。不引入 `OUTPUT_NAME` 把逻辑名与文件名拆开。旧写法 `tictactoe_core` / `tictactoe_cli` 偏离模板，已废弃。
- 源码树不建 `lib/` 目录；`lib` 只是 `build/` 下的产物目录（见上文「产物输出目录」）。
- `enable_testing()` 必须在顶层、`add_subdirectory(tests)` 之前调用；缺失时 `ctest` 报 "No tests were found"。googletest 子目录内的 `enable_testing()` 不会替顶层生效，`01-cli-game` 初版漏写后由一键脚本暴露，已固化为顶层必写项。

## 动态库运行时查找

规则核心编译为 `SHARED` 库后，运行时查找按三层组织，机制教学在 cpp-notes [构建动态库并运行程序](https://github.com/chengzhao-dev/cpp-notes/blob/main/content/getting-started/shared-library.qmd)：

- **主路径**：CLI 与测试可执行文件都设置 `BUILD_RPATH "$ORIGIN/../lib"`。两者产物都落 `build/bin/`，`$ORIGIN` 是可执行文件所在目录，查找位置写进 ELF 随文件移动，不依赖调用目录。
- **脚本加固**：`build-and-run.sh` 定义 `STAGE_LIB` 常量与 `run_with_stage_libs()`，用 `env LD_LIBRARY_PATH="${STAGE_LIB}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"` 包住测试与运行单条命令，命令结束即失效；展开保留调用者已有值。
- **禁止**：把 `LD_LIBRARY_PATH` 写进 `~/.bashrc`、修改系统 PATH 或用 `ldconfig` 注册工程产物；教学工程只依赖 RPATH 加一次性临时变量。
- 运行步骤用子 shell `cd "${STAGE_BIN}"` 后执行 `./${APP_NAME}`，父脚本工作目录保持阶段根；ctest/cmake 仍在阶段根执行。
- 抽查方法：从阶段根不带 `env` 前缀直接运行 `./build/bin/app` 应当成功（验证 RPATH 主路径）；脚本路径则进 `build/bin` 执行；`ldd build/bin/app` 的解析结果应落在 `build/bin/../lib/`。

## 静态检查的依赖边界

日常 clang-tidy 只传入阶段自己的源文件，项目头文件通过明确的 `--header-filter` 纳入；不使用 `--system-headers`，也不把 `compile_commands.json` 中的 GoogleTest 或其他 FetchContent 编译单元当成项目门禁。第三方 include 保持 system include 语义，项目 include 使用普通 `PUBLIC`/`PRIVATE` 路径。汇总的 `warnings generated` 必须回到具体路径和检查名分类，不能直接称为系统库错误。动态数组访问先验证坐标，再用 `std::array::at` 或有证据的局部例外；完整依据见标识 `bg-static-analysis-boundaries-v1` 的知识文件。


- 首个使用目录 `01-cli-game`：`tests/CMakeLists.txt` 用 `FetchContent_Declare` + `FetchContent_MakeAvailable` 引入，固定版本 `v1.17.0`。
- 下载地址用 `https://codeload.github.com/google/googletest/tar.gz/refs/tags/v1.17.0` tarball 而非 `GIT_REPOSITORY`：本环境 WSL 对 `github.com` 的 git 协议常超时，codeload 的 HTTPS 下载稳定。
- 链接 `GTest::gtest_main`（自带 `main()`），测试可执行文件用 `add_test(NAME ... COMMAND ...)` 注册；不启用 `gtest_discover_tests`（其配置期探测对动态库查找多一层依赖，无收益）。
- GoogleTest 自身编为静态库，落 `build/lib/`（ARCHIVE 输出目录），不参与运行时查找问题。
