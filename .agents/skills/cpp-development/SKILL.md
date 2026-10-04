---
name: cpp-development
description: 使用 C++20、CMake、Clang 和 WSL 开发棋盘游戏；编写游戏源码、构建规则或阶段脚本时使用
metadata:
  short-description: C++ 与 CMake 游戏开发
---

# Skill: cpp-development

承载 `games/<game>/` 下源码、构建规则与阶段脚本的实现流程。领域取舍依据交给 `.agents/knowledge/`。

## 适用场景

- 创建或修改游戏源码、`CMakeLists.txt`、测试与 `build-and-run.sh`。
- 建立新的编号阶段目录。
- **不适用**：棋盘与规则设计（转 `game-design`）、验证编排（转 `testing`）、Quarto 文档（转 `writing-quarto`）。

## 任务路由

| 任务 | 读取 |
| --- | --- |
| CMake 写法、构建目录与缓存、clangd 配套 | `.agents/knowledge/cpp-teaching/toolchain/cmake-conventions.md` |
| clang-tidy 项目边界、header filter 与系统头诊断 | `.agents/knowledge/cpp-teaching/toolchain/static-analysis-boundaries.md` |
| 项目类型形式约定（enum class、struct 聚合、namespace） | `.agents/knowledge/agent-workspace/planning/project-decisions.md` |
| 标识符命名、Google 风格自查与偏离白名单 | `references/google-cpp-style.md`；依据见知识 `bg-google-cpp-style-v1` |
| 类内与命名空间作用域声明顺序 | 知识 `bg-declaration-order-v1` |
| 注释与终端输出规范 | `.agents/knowledge/cpp-teaching/style/` |
| 阶段目录布局 | `.agents/knowledge/agent-workspace/navigation/staged-game-layout.md` |
| 游戏开篇/收官章的流程与 STAR 职责 | `.agents/knowledge/agent-workspace/planning/engineering-storyline.md` |
| 格式配置 | 复制 `assets/config/.clang-format`、`.clang-tidy`、`.clangd` 到阶段目录；注释外形见知识 `bg-comment-style-v1`「工具配置 YAML」。复制后按阶段增删 `.clangd` 的 `-I…`，去掉模板元叙述。 |

## P0 硬约束

1. 在 WSL Ubuntu 中使用 C++20、Clang、CMake、Ninja 和 CTest。
2. 标识符命名与头文件规则以 Google C++ 风格主标准加偏离白名单为准（见 `references/google-cpp-style.md`）：函数与类型 PascalCase、变量与参数 snake_case、常量与枚举子 `k` 前缀；`.clang-tidy` 随 `.clang-format` 复制进阶段目录。
3. 引入库组件的阶段采用组件式布局：`<component>/include/`、`<component>/src/`、`tests/` 各归其位，库对外头文件直接放在 `<component>/include/`（裸文件名，不建 `include/<namespace>/`；依据见标识 `bg-staged-game-layout-v1` 的知识文件）。
4. 使用 target-based CMake，不使用全局 `include_directories()` 管理依赖。
5. 游戏库、CLI 和测试必须是不同 target，CLI 和测试都链接游戏库。
6. 先完成具体游戏，再根据至少两个游戏的真实重复提取共享库。
7. 每个阶段目录自带完整 `CMakeLists.txt`，可独立配置、编译、测试和运行；根目录不放任何 CMake 文件，不使用根级编排。
8. 修改后重跑该阶段 `build-and-run.sh`，脚本内部完成重新配置、编译、格式与静态检查、CTest 和运行。
9. 大规模代码重构先取全量语料：`scope` 命中范围 → 本 SKILL → 其路由指向的全部参考与知识文件、模板读完再动手，禁止只按任务清单的增量条目改写。

## 完成判据

- [ ] 对应游戏 CTest 全部通过，构建无新告警。
- [ ] Bash 脚本通过 `bash -n`；C++ 源码经脚本内 `clang-format --dry-run --Werror` 与 `clang-tidy` 零警告，clangd 编辑器诊断与阶段 `.clang-tidy` 一致（检查方式见知识 `bg-google-cpp-style-v1`）。clang-tidy 日常门禁只接收项目源文件，`--header-filter` 只覆盖项目头文件，不使用 `--system-headers`；依赖审计另行运行。
- [ ] Bash 脚本按「`set` → `readonly` 常量 → 函数 → `main` → `main "$@"`」次序组织；文件头之后设「严格模式与工作目录」独立段横幅；SHARED 阶段测试与运行用 `run_with_stage_libs`，运行步骤子 shell `cd` 进 `STAGE_BIN`。
- [ ] 源码、CMake、脚本和 `.clang-format` / `.clang-tidy` / `.clangd` 的文件头与邻接注释符合统一注释规范（含工具配置 YAML 合同）；阶段副本无模板元叙述与知识库 id 指针。
- [ ] 新阶段目录自带 `.clang-format`、`.clang-tidy`、`.clangd` 与 `.vscode/`，配置归属阶段本身。
