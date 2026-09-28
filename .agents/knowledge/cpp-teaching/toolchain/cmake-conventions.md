---
kb_id: "bg-cmake-conventions-v1"
title: "CMake 约定依据"
domain: "cpp-teaching"
subdomain: "toolchain"
tags: [cmake, build, clangd, ninja]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-09-28"
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

- 依赖机制：CMake 配置时开启 `CMAKE_EXPORT_COMPILE_COMMANDS=ON`，在 build 目录生成 `compile_commands.json`（Ninja/Makefile 生成器支持）。
- 自动发现：clangd 按"源文件所在目录 → 各级父目录 → 各目录下的 `build/` 子目录"顺序查找该文件；阶段目录名保持 `build/` 作为构建目录名即可零配置命中，不需要 `--compile-commands-dir` 或 `.clangd` 配置。若未来构建目录改名，用项目根 `.clangd` 文件指定：`CompileFlags: CompilationDatabase: <目录名>`。
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
- 演进方向：`CMakePresets.json` 是 CMake 官方承载配置参数的机制（`cacheVariables` + `cmake --preset`，IDE/CI 通用）。`02-board-and-state` 引入 GoogleTest 后配置参数并未增多（FetchContent 参数固定在 `tests/CMakeLists.txt` 内，脚本 `-D` 参数与阶段 01 相同），Presets 继续延后到配置参数再多时评估。
- 来源：[CMake Ninja 生成器文档](https://cmake.org/cmake/help/latest/generator/Ninja.html)、[microsoft/vscode-cmake-tools #3978](https://github.com/microsoft/vscode-cmake-tools/issues/3978)（官方建议"删除构建目录重新配置以丢弃陈旧配置"）。

## 组件化阶段布局

阶段从单文件演进为组件式布局，首个使用目录是 `02-board-and-state/`：

- 顶层 `CMakeLists.txt` 只做工程声明、产物目录、`enable_testing()` 和 `add_subdirectory`；各组件 target 由组件目录自己的 `CMakeLists.txt` 定义。库组件 `tic_tac_toe/` 拥有 `include/tic_tac_toe/`、`src/` 与库 target `tic_tac_toe_core`；`apps/` 拥有 CLI；`tests/` 拥有测试。
- 源码树不建 `lib/` 目录；`lib` 只是 `build/` 下的产物目录（见上文「产物输出目录」）。
- `enable_testing()` 必须在顶层、`add_subdirectory(tests)` 之前调用；缺失时 `ctest` 报 "No tests were found"。googletest 子目录内的 `enable_testing()` 不会替顶层生效，`02-board-and-state` 初版漏写后由一键脚本暴露，已固化为顶层必写项。

## 动态库运行时查找

规则核心编译为 `SHARED` 库后，运行时查找按三层组织，机制教学在 cpp-notes [构建动态库并运行程序](https://github.com/chengzhao-dev/cpp-notes/blob/main/content/getting-started/shared-library.qmd)：

- **主路径**：CLI 与测试可执行文件都设置 `BUILD_RPATH "$ORIGIN/../lib"`。两者产物都落 `build/bin/`，`$ORIGIN` 是可执行文件所在目录，查找位置写进 ELF 随文件移动，不依赖调用目录。
- **脚本加固**：`build-and-run.sh` 的测试与运行步骤用 `env LD_LIBRARY_PATH="$PWD/build/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"` 包住单条命令，命令结束即失效；展开保留调用者已有值。
- **禁止**：把 `LD_LIBRARY_PATH` 写进 `~/.bashrc`、修改系统 PATH 或用 `ldconfig` 注册工程产物；教学工程只依赖 RPATH 加一次性临时变量。
- 抽查方法：不带 `env` 前缀直接运行 `./build/bin/tic_tac_toe_cli` 应当成功；`ldd build/bin/tic_tac_toe_cli` 的解析结果应落在 `build/bin/../lib/`。

## GoogleTest 引入约定

- 首个使用目录 `02-board-and-state`：`tests/CMakeLists.txt` 用 `FetchContent_Declare` + `FetchContent_MakeAvailable` 引入，固定版本 `v1.17.0`。
- 下载地址用 `https://codeload.github.com/google/googletest/tar.gz/refs/tags/v1.17.0` tarball 而非 `GIT_REPOSITORY`：本环境 WSL 对 `github.com` 的 git 协议常超时，codeload 的 HTTPS 下载稳定。
- 链接 `GTest::gtest_main`（自带 `main()`），测试可执行文件用 `add_test(NAME ... COMMAND ...)` 注册；不启用 `gtest_discover_tests`（其配置期探测对动态库查找多一层依赖，无收益）。
- GoogleTest 自身编为静态库，落 `build/lib/`（ARCHIVE 输出目录），不参与运行时查找问题。
