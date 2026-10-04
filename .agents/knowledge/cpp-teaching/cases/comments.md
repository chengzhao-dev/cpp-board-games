---
kb_id: "bg-comment-cases-v1"
title: "注释写法正反对照"
domain: "cpp-teaching"
subdomain: "cases"
tags: [comment, llvm, enum, trailing-comment]
level_range: [0, 5]
dependencies: [bg-comment-style-v1]
created: "2026-09-29"
updated: "2026-10-04"
chunk_strategy: "semantic_heading"
estimated_tokens: 1100
---

# 注释写法正反对照

注释规范条文（横幅、层级、语言、上限）见标识 `bg-comment-style-v1` 的知识文件；本文件保存正反对照，检索单元是「正确 + 不佳 + 改写」。

## 论证性旁白对照

注释里不写「为什么不用某方案」的选型论证，理由外移到知识文件：

```text
不佳（论证性旁白，读者不知道注释在约束什么）：
# 每次都重新配置：跳过会让改动的参数静默失效。
# 换编译器报错时 rm -rf build 重跑即可。

不佳（关键命令过短，生成器、编译器和编译数据库都没出现）：
# 每次重新配置，使脚本里的参数进入当前构建计划。
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

改写（两行内点名这些开关改变了什么，不写排查长文）：
# 用 Ninja 和 clang++ 配置 Debug，并写出 build/compile_commands.json。
# 每次都重新配置，避免这些开关留在上一次的 CMake 缓存里。
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

## 枚举行尾注释对照

类型意图写在 enum 上一行（声明注释 `///`）；成员名不能让初学者直接对应领域语义时写行尾注释，多条行尾时 `///<` 列对齐（`ColumnLimit: 80` 内，依赖 Google `BasedOnStyle` 的 `AlignTrailingComments`）：

```text
不佳（成员注释另起一行逐条复述类型意图，同一信息重复多遍）：
/// 棋盘格子的状态。
/// kEmpty 表示空棋盘格子
/// kCross 与 kNought 表示棋盘格子状态
enum class CellState : std::uint8_t {
  kEmpty,
  kCross,
  kNought,
};

不佳（类型上一行丢掉棋盘锚点，写成「格子内容」）：
/// 格子内容
enum class CellState : std::uint8_t {
  kEmpty = 0,   ///< 空格。
  kCross = 1,   ///< X 棋子。
  kNought = 2,  ///< O 棋子。
};

改写（上一行保留棋盘锚点，成员行尾注释用简洁词、`///<` 列对齐）：
/// 棋盘格子的状态。
enum class CellState : std::uint8_t {
  kEmpty = 0,   ///< 空格。
  kCross = 1,   ///< X 棋子。
  kNought = 2,  ///< O 棋子。
};
```

同一枚举要注就全注、要不注就全不注，禁止半套；行尾须**语义结果优先**（规则见标识 `bg-comment-style-v1` 的知识文件「枚举与常量行尾注释」）：

```text
不佳（半套：终局成员有行尾注释，进行中成员没有，读者怀疑漏写）：
/// 终局结果；规则补全前固定返回 kInProgress。
enum class GameResult : std::uint8_t {
  kInProgress,
  kDraw,   ///< 棋盘下满且无人三连。
  kCrossWin,  ///< 先手 X 达成三连。
  kNoughtWin,  ///< 对手 O 达成三连。
};

不佳（齐全但仍只写条件：kDraw 行尾看不出「平局」）：
/// 终局结果；规则补全前固定返回 kInProgress。
enum class GameResult : std::uint8_t {
  kInProgress,  ///< 对局尚未结束，可继续落子。
  kDraw,        ///< 棋盘下满且无人三连。
  kCrossWin,       ///< 先手 X 达成三连。
  kNoughtWin,       ///< 对手 O 达成三连。
};

改写（语义结果在前，判定条件跟在全角冒号后，`///<` 列对齐）：
/// 终局结果；规则补全前固定返回 kInProgress。
enum class GameResult : std::uint8_t {
  kInProgress,  ///< 进行中：对局尚未结束，可继续落子。
  kDraw,        ///< 平局：棋盘下满且无人三连。
  kCrossWin,       ///< 先手 X 获胜：达成三连。
  kNoughtWin,       ///< 对手 O 获胜：达成三连。
};
```

## 领域函数注释对照

领域换算与读取注释写结果与约束（规则见标识 `bg-comment-style-v1` 的知识文件「领域函数与成员注释」）：

```text
不佳（映射 + 错用「棋子」）：
// 把玩家映射为它落下的棋子。
constexpr CellState CellStateFor(Player player);

改写（由 A 得到 B，术语用棋盘格子状态）：
// 由对局玩家得到应写入的棋盘格子状态（Player::kCross 对应 CellState::kCross）。
constexpr CellState CellStateFor(Player player);

不佳（只写「查询」+ 裸参数名 +「必须合法」）：
// 查询棋盘格子状态；position 必须合法。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

改写（Get 用「获取」+ 非法坐标的失败行为）：
// 获取指定坐标处的格子状态。
// 非法坐标抛出 std::out_of_range。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

不佳（Get 前缀概述写「返回」，动词与函数名脱节）：
// 返回当前对局结果。
[[nodiscard]] GameResult GetResult() const;

改写（Get 一律「获取」）：
// 获取当前对局结果。
[[nodiscard]] GameResult GetResult() const;

不佳（To 前缀用排布术语当结果，读者对不上换算出了什么）：
// 将已验证的坐标转换为行优先下标。
/// @return 行优先展开的一维下标。
[[nodiscard]] static std::size_t ToFlatIndex(CellPosition position) noexcept;

改写（To 写「将 A 转换为 B」，结果词用一维索引）：
// 将二维坐标转换为一维索引。
/// @return 转换得到的一维索引。
[[nodiscard]] static std::size_t ToFlatIndex(CellPosition position) noexcept;

不佳（存储成员注释以排布开头，读完仍不知道装的是什么）：
// 按行优先保存棋盘格子。
std::array<CellState, static_cast<std::size_t>(kCellCount)> cells_{};

改写（本体先行：先写是什么的数组，再补排布）：
// 棋盘格子的存储数组，按行依次存放。
std::array<CellState, static_cast<std::size_t>(kCellCount)> cells_{};
```

## 未完成实现用 TODO

后续才补全的占位实现必须用可检索的 TODO，不要只写「见后续章」普通注释（规则见标识 `bg-comment-style-v1` 的知识文件「TODO」）：

```text
不佳（普通注释，rg TODO 扫不到）：
// 终局规则见后续章；此处读取 cells_ 保持实例方法，固定返回进行中。
GameResult Game::GetResult() const {
  static_cast<void>(cells_);
  return GameResult::kInProgress;
}

改写（Google Hyphen 式 TODO，参考用阶段目录名）：
// TODO: 01-cli-game - Detect win/draw from cells_;
// currently always returns kInProgress.
GameResult Game::GetResult() const {
  static_cast<void>(cells_);
  return GameResult::kInProgress;
}
```

## 一注多句对照

并列语句需要注释时，一句注释只标紧随的一条语句（规则见标识 `bg-comment-style-v1` 的知识文件「邻接单行注释」）：

```text
不佳（一行注释覆盖三条兄弟 set，读者对不上哪句归哪条）：
# 可执行文件归入 build/bin，动态库与静态库归入 build/lib。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")

改写（每条语句正上方一行意图注释）：
# 可执行文件归入 build/bin。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
# 动态库归入 build/lib。
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
# 静态库归入 build/lib。
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
```

```text
不佳（注释与命令错位：注释写链接，位置却在 add_executable 上方）：
# 测试可执行文件链接规则库与 GoogleTest 的 main 适配。
add_executable(tictactoe_game_state_test
  game_state_test.cpp
)
target_link_libraries(tictactoe_game_state_test ...)

改写（各归各位）：
# 源文件显式列出，新增文件在这里追加。
add_executable(tictactoe_game_state_test
  game_state_test.cpp
)

# 链接规则库与 GoogleTest 的 main 适配。
target_link_libraries(tictactoe_game_state_test ...)
```

## 函数注释与关键命令错配

小函数不配 `Arguments:` / `Outputs:`。多标志命令不能只留一句空话。两种毛病经常成对出现，写脚本时一起改掉。

```text
不佳（辅助函数复述函数体，配置命令却没有写出开关）：
# 将错误提示写到 stderr，避免混入正常输出。
# Arguments: 错误描述
# Outputs:   一行 "错误: 描述" 到 stderr
err() {
  printf '错误: %s\n' "$*" >&2
}

# 每次重新配置，使脚本里的参数进入当前构建计划。
cmake -S . -B build -G Ninja \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

改写（函数只留去向；配置行点名 Ninja、clang++、Debug 和编译数据库）：
# 把错误写到 stderr，避免混进管道对局的正常输出。
err() {
  printf '错误: %s\n' "$*" >&2
}

# 用 Ninja 和 clang++ 配置 Debug，并写出 build/compile_commands.json。
# 每次都重新配置，避免这些开关留在上一次的 CMake 缓存里。
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

## 整型转换注释

整式一次性转换禁用：`static_cast<std::size_t>(position.row * kCols + position.col)` 的乘加发生在 `int` 域内，转换前就可能溢出，`bugprone-misplaced-widening-cast` 报警（该检查随 `bugprone-*` 启用，报警时改代码、不加 NOLINT）。先建 `const int` 中间变量再对变量转换一次的写法同样废弃（用户定案）：转换点离开数据来源一层，逐操作数转换更直接。

```text
不佳（先存中间变量再转换，用户定案废弃）：
std::size_t Board::ToFlatIndex(CellPosition position) noexcept {
  const int index = (position.row * kCols) + position.col;
  return static_cast<std::size_t>(index);
}

改写（行、列操作数各自转换；`kCols` 保持 int，由通常算术转换提升）：
std::size_t Board::ToFlatIndex(CellPosition position) noexcept {
  return (static_cast<std::size_t>(position.row) * kCols) +
         static_cast<std::size_t>(position.col);
}
```

本节取代原「领域乘加留在 `int`、不要把行、列和列数分别 `static_cast`」的判例；做法理由留在本节与标识 `bg-google-cpp-style-v1` 的知识文件「整型与枚举底层类型」，代码注释不复述转换过程（见标识 `bg-comment-style-v1` 的知识文件「类型选型与组织自述不进注释」）。

## 实现注释对照

`.cpp` 实现注释按用户定案保持高于 Google 基线的密度：非平凡函数定义上方一行操作注释，关键分支与步骤行尾注明原因；平凡访问器不加，不复制 `@param`/`@return` 标签（规则见标识 `bg-comment-style-v1` 的知识文件「实现注释」）：

```text
不佳（实现零注释，隔期回看必须重读头文件契约才能接上）：
bool Board::PlacePiece(CellPosition position, CellState state) {
  if (!IsValidPosition(position) || state == CellState::kEmpty) {
    return false;
  }
  CellState& cell = cells_.at(ToFlatIndex(position));
  if (cell != CellState::kEmpty) {
    return false;
  }
  cell = state;
  return true;
}

不佳（逐行尾复述代码，注释只把语句翻译一遍）：
  cell_state = piece;  // 放置棋子
  return true;         // 放置成功

改写（定义上方一句操作要点，失败分支行尾写拒绝原因）：
// 先校验后写入：任何失败都在改动棋盘前返回，拒绝时棋盘保持不变。
bool Board::PlacePiece(CellPosition position, CellState state) {
  if (!IsValidPosition(position) || state == CellState::kEmpty) {
    return false;  // 坐标无效或不是向空格落子，拒绝。
  }
  CellState& cell = cells_.at(ToFlatIndex(position));
  if (cell != CellState::kEmpty) {
    return false;  // 目标格子已被占用，拒绝覆盖。
  }
  cell = state;  // 校验全部通过，写入棋子。
  return true;
}
```

## 类型选型旁白对照

代码注释不复述类型选型与实现细节，也不写组织自述（规则见标识 `bg-comment-style-v1` 的知识文件「类型选型与组织自述不进注释」）：

```text
不佳（组织自述回答「维护者应在哪里定义」，类型旁白复述代码可见的宽度）：
// 棋盘尺寸：行数与列数，全仓只在这里定义一次。
inline constexpr int kRows = 3;

// 棋盘格子总数：与行数、列数同为 int，乘积不再拓宽。
inline constexpr int kCellCount = kRows * kCols;

改写（只写读者需要的领域语义；整型做法的理由留在知识文件）：
// 棋盘尺寸：行数与列数。
inline constexpr int kRows = 3;

// 棋盘格子总数。
inline constexpr int kCellCount = kRows * kCols;
```

契约注释不受此限：前置条件、异常与失败后动作照常保留（如「非法坐标抛出 std::out_of_range」）。

## 正确形态正例

```cpp
//===----------------------------------------------------------------------===//
// board.h - 定义井字棋棋盘及其格子状态。
//===----------------------------------------------------------------------===//

/// 棋盘的行数。
inline constexpr int kRows = 3;

/// 棋盘格子的状态。
enum class CellState : std::uint8_t {
  kEmpty = 0,   ///< 空格。
  kCross = 1,   ///< X 棋子。
  kNought = 2,  ///< O 棋子。
};

/// 表示棋盘格子的行列坐标；行和列从 0 开始。
struct CellPosition {
  int row = 0;  ///< 行坐标。
  int col = 0;  ///< 列坐标。
};
```

正例的判定条件：文件头横幅定宽 80 列、标题行在横幅之间；声明注释用 `///`，类型意图独占一行并保留棋盘锚点；行尾注释成员齐全（`CellState` 定案全量），用 `///<` 列对齐、用简洁词；`CellPosition` 字段带 `= 0` 默认值；`CellPosition` 不写有符号选型旁白；不写类型选型旁白与组织自述；注释是完整中文短句，专有名词保留英文。

## 配置 YAML 正反对照

`.clang-format` / `.clang-tidy` / `.clangd` 的条文见标识 `bg-comment-style-v1` 的知识文件「工具配置 YAML」。

不佳（文件顶部长篇政策块，折行引用知识库 id，一段话覆盖多项关闭策略）：

```yaml
---
# C++ 静态检查：modernize + cppcoreguidelines + bugprone 等，命名规则
# 与 google-* 启用项以 Google C++ Style Guide 为主标准（偏离白名单见
# 知识库 bg-google-cpp-style-v1）。
# 仅对边界已验证的访问使用 std::array::at；不对该检查做全局豁免。
Checks: >
  bugprone-*,
  -portability-avoid-pragma-once
```

改写（短横幅 + YAML 列表；关闭说明紧贴该项，不写进折叠字符串）：

```yaml
#===------------------------------------------------------------------------===#
# .clang-tidy - C++ 静态检查与命名规则
#===------------------------------------------------------------------------===#
---
Checks:
  - bugprone-*
  # 关闭 portability-avoid-pragma-once：头文件使用 #pragma once。
  - "-portability-avoid-pragma-once"
CheckOptions:
  # 局部常量不是全程固定的 k 常量，避免误套 ConstantCase。
  - key: readability-identifier-naming.LocalConstantCase
    value: lower_case
```

不佳（模板元叙述写进阶段副本）：

```yaml
#===------------------------------------------------------------------------===#
# .clang-format - C++ 工程格式模板
#
# 本文件是两仓统一格式基准源：新阶段 / 新工程把本文件复制为各自根目录。
#===------------------------------------------------------------------------===#
```

改写（一行用途，无复制/两仓旁白）：

```yaml
#===------------------------------------------------------------------------===#
# .clang-format - C++ 格式化规则
#===------------------------------------------------------------------------===#
```
