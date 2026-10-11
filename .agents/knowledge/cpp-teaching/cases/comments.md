---
kb_id: "bg-comment-cases-v1"
title: "注释写法正反对照"
domain: "cpp-teaching"
subdomain: "cases"
tags: [comment, llvm, enum, trailing-comment]
level_range: [0, 5]
dependencies: [bg-comment-style-v1]
created: "2026-09-29"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 6500
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

类型意图写在 enum 上一行（声明注释 `///`）；成员名不能让初学者直接对应领域语义时写行尾注释，多条行尾时 `///<` 列对齐（`ColumnLimit: 100` 内，依赖 Google `BasedOnStyle` 的 `AlignTrailingComments`）：

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
/// 对局的结果：进行中、X 获胜、O 获胜或平局。
enum class GameResult : std::uint8_t {
  kInProgress,
  kDraw,   ///< 棋盘下满且无人三连。
  kCrossWin,  ///< 先手 X 达成三连。
  kNoughtWin,  ///< 对手 O 达成三连。
};

不佳（齐全但仍只写条件：kDraw 行尾看不出「平局」）：
/// 对局的结果：进行中、X 获胜、O 获胜或平局。
enum class GameResult : std::uint8_t {
  kInProgress,  ///< 对局尚未结束，可继续落子。
  kDraw,        ///< 棋盘下满且无人三连。
  kCrossWin,       ///< 先手 X 达成三连。
  kNoughtWin,       ///< 对手 O 达成三连。
};

改写（类型注释收口为一句整体含义，不列举成员取值；语义结果在前，判定条件跟在全角冒号后，`///<` 列对齐；`kInProgress` 用「游戏进行中」与 CLI 结果短语统一，用户定案）：
/// 对局的结果。
enum class GameResult : std::uint8_t {
  kInProgress = 0,  ///< 游戏进行中：对局尚未结束，可继续落子。
  kCrossWin = 1,    ///< X 获胜：达成三连。
  kNoughtWin = 2,   ///< O 获胜：达成三连。
  kDraw = 3,        ///< 平局：棋盘已满且双方均未三连。
};
```

成员名看不出领域语义时，全量行尾注释比「全自明」判断更稳妥（`Player` 判例，用户定案）；行尾写「使用 X 棋子」式直述，不用「执 X」棋类行话——读者对不上「执」对应什么动作（用户定案禁用）：

```text
不佳（误判全自明一条不注，初学者对不上 kCross/kNought 谁先手、用哪个棋子）：
/// 对局玩家。
enum class Player : std::uint8_t {
  kCross = 0,
  kNought = 1,
};

改写（全量行尾：先手后手与棋子归属是类型注释装不下的领域语义）：
/// 对局玩家。
enum class Player : std::uint8_t {
  kCross = 0,   ///< 先手：使用 X 棋子。
  kNought = 1,  ///< 后手：使用 O 棋子。
};
```

## 领域函数注释对照

领域换算与读取注释写结果与约束（规则见标识 `bg-comment-style-v1` 的知识文件）：

```text
不佳（映射 + 错用「棋子」）：
// 把玩家映射为它落下的棋子。
constexpr CellState PlayerToCellState(Player player);

改写（由 A 得到 B，术语用棋盘格子状态）：
/// 由对局玩家得到应写入的棋盘格子状态。
///
/// Player::kCross 对应 CellState::kCross。
constexpr CellState PlayerToCellState(Player player);
```

「接受」黑话对照（规则见标识 `bg-comment-style-v1` 的知识文件「领域函数与成员注释」）：以「接受」暗指写入成功，读者看不出对应什么动作；结果词直接写「写入」：

```text
不佳（「接受」黑话：落子被谁接受、接受后发生什么都要读者猜）：
///< 落子已接受。

改写（结果词直述写入成功）：
///< 落子已写入。
```

不佳（只写「查询」+ 裸参数名 +「必须合法」）：
// 查询棋盘格子状态；position 必须合法。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

改写（Get 概述以「获取」开头，参数与失败行为进标签；@returns 只会复述概述，省略）：
/// 获取指定坐标处的棋盘格子状态。
///
/// @param position 行列坐标。
/// @throws std::out_of_range 坐标不在棋盘范围内。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

不佳（Get 概述纯名词短语，读不出是获取、设置还是别的动作）：
/// 当前对局结果。
[[nodiscard]] GameResult GetResult() const;

不佳（Get 概述用「返回」，与函数名前缀不对应）：
// 返回当前对局结果。
[[nodiscard]] GameResult GetResult() const;

改写（Get 概述以「获取」开头）：
/// 获取当前对局结果。
[[nodiscard]] GameResult GetResult() const;

不佳（查询不取 Get 前缀，调用点看不出这是读取当前玩家）：
// 返回当前应当落子的玩家。
[[nodiscard]] Player CurrentPlayer() const;

改写（查询一律 Get 前缀，概述以「获取」开头）：
/// 获取当前落子玩家。
[[nodiscard]] Player GetCurrentPlayer() const;

不佳（Get 概述写成把排布说明也挤进去的纯名词句）：
/// 本局落子历史，按发生顺序排列。
[[nodiscard]] const std::vector<Move>& GetHistory() const;

改写（概述以「获取」开头，细节槽写具体的先后顺序，不挤进概述）：
/// 获取本局落子历史。
///
/// 先手的第一步在最前，最近一步在最后。
[[nodiscard]] const std::vector<Move>& GetHistory() const;

不佳（「接受」黑话：读者看不出「接受」对应什么动作）：
// 尝试接受一次落子。
// 玩家、坐标或格子不符合规则时拒绝，局面保持不变。
[[nodiscard]] PlaceResult Place(const Move& move);

改写（Try 前缀概述「尝试…」，拒绝条件写成可观察行为）：
/// 尝试执行一次落子。
///
/// 落子合法时，把落子玩家的棋子写入棋盘并轮到另一名玩家。
/// 对局已结束、落子的玩家不是当前玩家、坐标无效或目标棋盘格子已被占用时拒绝，棋盘和轮次保持不变。
[[nodiscard]] PlaceResult TryPlace(const Move& move);

不佳（To 前缀用排布术语当结果，读者对不上换算出了什么）：
// 将已验证的坐标转换为行优先下标。
/// @returns 行优先展开的一维下标。
[[nodiscard]] static std::size_t ToFlatIndex(CellPosition position) noexcept;

改写（To 写「将 A 转换为 B」，结果词用一维索引；@returns 只会复述概述，省略）：
/// 将二维坐标转换为一维索引。
[[nodiscard]] static std::size_t ToFlatIndex(CellPosition position) noexcept;

不佳（存储成员注释以排布开头，读完仍不知道装的是什么）：
// 按行优先保存棋盘格子。
std::array<CellState, static_cast<std::size_t>(kCellCount)> cells_{};

改写（本体先行：先写是什么的数组，再补排布）：
// 棋盘格子的存储数组，按行依次存放。
std::array<CellState, static_cast<std::size_t>(kCellCount)> cells_{};

## 声明注释块骨架对照

库头文件的声明注释统一走「概述 → 槽 1 → 可选细节 → 槽 2 → 标签」骨架，空 `///` 只出现在两个固定槽位（规则见标识 `bg-comment-style-v1` 的知识文件「声明注释块骨架」）：

```text
不佳（旧三段式：两道空 `///` 把类细节拆成能力与约束两段，违反「禁止第三道空行」）：
/// 一局井字棋对局。
///
/// 提供读取棋盘格子状态与对局结果、执行落子和查看落子历史的功能。
///
/// 对局由 X 先手，两名玩家轮流落子。
class Game {

改写（类细节最多一段：能力与结构约束合并进同一段，只留槽 1）：
/// 一局井字棋对局。
///
/// 提供读取棋盘格子状态与对局结果、执行落子和查看落子历史的功能；
/// 对局由 X 先手，两名玩家轮流落子。
class Game {

不佳（有细节又有 @ 块时漏掉槽 2，细节与首个 @ 标签挤在一起）：
/// 尝试执行一次落子。
///
/// 落子合法时，把落子玩家的棋子写入棋盘并轮到另一名玩家。
/// 对局已结束、落子的玩家不是当前玩家、坐标无效或目标棋盘格子已被占用时拒绝，棋盘和轮次保持不变。
/// @param move 待执行的落子。
[[nodiscard]] PlaceResult TryPlace(const Move& move);

改写（细节与首个 @ 之间补一行空 `///`，即槽 2）：
/// 尝试执行一次落子。
///
/// 落子合法时，把落子玩家的棋子写入棋盘并轮到另一名玩家。
/// 对局已结束、落子的玩家不是当前玩家、坐标无效或目标棋盘格子已被占用时拒绝，棋盘和轮次保持不变。
///
/// @param move 待执行的落子。
/// @returns 落子执行成功返回 kPlaced，被拒绝返回 kRejected。
[[nodiscard]] PlaceResult TryPlace(const Move& move);
```

无细节、只有标签时，概述后直接跟槽 1 再进 `@` 块，不再多空一行（见「领域函数注释对照」的 `GetCellState` 改写）。

## @ 标签句式对照

`@` 标签只服务 API 契约，顺序锁死为 `@param` → `@returns` → `@throws`，彼此不空行（规则见标识 `bg-comment-style-v1` 的知识文件「标签规则」）：

```text
不佳（用 @p 标记参数名，第三套标记与正文风格割裂）：
/// 获取指定坐标处的棋盘格子状态。
///
/// @param[in] position @p position 须先经 @p IsValidPosition 校验。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

改写（正文直接写参数名，普通入参不写方向）：
/// 获取指定坐标处的棋盘格子状态。
///
/// @param position 行列坐标，调用前须先经 IsValidPosition 校验。
/// @throws std::out_of_range 坐标不在棋盘范围内。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

不佳（@returns 复述概述，读者没有获得新信息）：
/// 获取指定坐标处的棋盘格子状态。
///
/// @param position 行列坐标。
/// @returns 该坐标处的棋盘格子状态。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

改写（@returns 只会复述概述，整行省略；@param 与 @throws 保留）：
/// 获取指定坐标处的棋盘格子状态。
///
/// @param position 行列坐标。
/// @throws std::out_of_range 坐标不在棋盘范围内。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

不佳（出参漏写 [out]，调用方看不出 row/col 由函数写出）：
/// @param in 玩家输入流。
/// @param err 诊断输出流。
/// @param row 读到的行坐标。
/// @param col 读到的列坐标。
ReadResult ReadRowAndCol(std::istream& in, std::ostream& err, int& row,
                         int& col);

改写（出参标注 [out]，普通入参不加 [in]）：
/// @param in 玩家输入流。
/// @param err 诊断输出流。
/// @param[out] row 读到的行坐标。
/// @param[out] col 读到的列坐标。
ReadResult ReadRowAndCol(std::istream& in, std::ostream& err, int& row,
                         int& col);
```

## private 声明对照

头文件里出现的 private 成员与辅助函数，有签名外约束用 `///`（可带标签），平凡数据成员用 `//` 邻接注释（规则见标识 `bg-comment-style-v1` 的知识文件「private 声明」）：

```text
不佳（private 辅助函数用普通 //，丢失 Doxygen 声明契约）：
// 将二维坐标转换为一维索引。
[[nodiscard]] static std::size_t ToFlatIndex(CellPosition position) noexcept;

改写（private 辅助函数仍用 /// 声明注释）：
/// 将二维坐标转换为一维索引。
[[nodiscard]] static std::size_t ToFlatIndex(CellPosition position) noexcept;

不佳（数据成员用 ///，与实现注释混用标记）：
/// 棋盘格子的存储数组，按行依次存放。
std::array<CellState, static_cast<std::size_t>(kCellCount)> cells_{};

改写（平凡数据成员用 // 邻接注释）：
// 棋盘格子的存储数组，按行依次存放。
std::array<CellState, static_cast<std::size_t>(kCellCount)> cells_{};
```

访问说明符与属性行的空白也按 `game.h` 的形态写，规则见标识 `bg-comment-style-v1` 的知识文件「类内属性与访问说明符空白」：

```text
不佳（`private:` 后空一行，属性行缩到访问说明符那一列）：
private:

 [[nodiscard]] static bool HasPlayerLine(const Board& board, CellState state);

改写（`private:` 后不空行，属性行与声明同一行、缩进两格）：
 private:
  /// 检查棋盘上是否已形成三连获胜线。
  [[nodiscard]] static bool HasPlayerLine(const Board& board, CellState state);
```

## 类型声明注释对照

类与结构体的声明注释按实体方案写（规则见标识 `bg-comment-style-v1` 的知识文件「多行注释」与「枚举与常量行尾注释」）：

```text
不佳（class 概述只写职责动词串，能力与约束缺失）：
/// 管理轮次、落子记录和对局结果。
class Game {

不佳（类型概述以「表示」开头，读者绕一层才到对象，禁用）：
/// 表示一局井字棋对局。
class Game {

改写（类细节最多一段，仅槽 1；能力与结构约束合并进同一段）：
/// 一局井字棋对局。
///
/// 提供读取棋盘格子状态与对局结果、执行落子和查看落子历史的功能；
/// 对局由 X 先手，两名玩家轮流落子。
class Game {

不佳（struct 字段无行尾注释，与 CellPosition 全量判例不一致）：
struct Move {
  CellPosition position;
  Player player = Player::kCross;
};

改写（字段行尾全量，///< 列对齐）：
struct Move {
  CellPosition position;          ///< 落子的行列坐标。
  Player player = Player::kCross;  ///< 执行落子的玩家。
};

不佳（枚举成员行尾用普通 //，Doxygen 不识别）：
enum class ReadResult : std::uint8_t {
  kOk = 0,     // 读到两个整数。
  kRetry = 1,  // 本行不是两个整数，已丢掉，需要重试。
  kEof = 2,    // 输入结束。
};

改写（行尾用 ///<）：
enum class ReadResult : std::uint8_t {
  kOk = 0,     ///< 读到两个整数。
  kRetry = 1,  ///< 本行不是两个整数，已丢掉，需要重试。
  kEof = 2,    ///< 输入结束。
};
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

改写（Google Hyphen 式 TODO，参考用阶段目录名，中文句号收尾）：
// TODO: 01-cli-game - 从 cells_ 判断胜负或平局。
// 当前总是返回 kInProgress。
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
# 测试可执行文件链接井字棋动态库与 GoogleTest 的 main 适配。
add_executable(tictactoe_game_state_test
  game_state_test.cpp
)
target_link_libraries(tictactoe_game_state_test ...)

改写（各归各位）：
# 源文件显式列出，新增文件在这里追加。
add_executable(tictactoe_game_state_test
  game_state_test.cpp
)

# 链接井字棋动态库与 GoogleTest 的 main 适配。
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

`.cpp` 实现注释只补头文件契约没写的实现要点：函数定义上一行不写操作摘要，关键分支与拒绝原因行尾注明；平凡访问器不加，不复制 `@param`/`@returns` 标签（规则见标识 `bg-comment-style-v1` 的知识文件「实现注释」）：

```text
不佳（定义上方写操作摘要，把头文件契约复述一遍）：
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

不佳（逐行尾复述代码，注释只把语句翻译一遍）：
  cell_state = piece;  // 放置棋子
  return true;         // 放置成功

改写（摘要删除；拒绝原因与关键写入行尾保留）：
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

## 无对象代词与词条冒号对照

`HasPlayerLine` 的旧文本把三类问题凑在一起：定义上方摘要只说「该状态」，循环注释用词条冒号，lambda 名 `line_filled` 与「棋盘下满」撞车（规则见标识 `bg-comment-style-v1` 的知识文件「实现注释」）：

```text
不佳（「该状态」读不出对象，「行：」是词条冒号，lambda 名 filled 与「棋盘下满」撞车）：
// 逐行、逐列加两条对角线地检查该状态是否连成一条线。
bool Game::HasPlayerLine(const Board& board, CellState state) {
  const auto has_state = [&](CellPosition position) {
    return board.GetCellState(position) == state;
  };
  const auto line_filled = [&](CellPosition a, CellPosition b, CellPosition c) {
    const std::array<CellPosition, 3> line{a, b, c};
    return std::ranges::all_of(line, has_state);
  };
  // 行：同一 row 的三列均已是该状态。
  for (int row = 0; row < kRows; ++row) {
    if (line_filled({.row = row, .col = 0}, {.row = row, .col = 1}, {.row = row, .col = 2})) {
      return true;
    }
  }
  ……

改写（摘要删除；谓词 lambda 用 is_ / has_ 前缀给「一格是不是 state」「三个坐标连成线」起名；循环注释删掉，行、列由循环变量和函数名说出）：
bool Game::HasPlayerLine(const Board& board, CellState state) {
  const auto has_state = [&](CellPosition position) {
    return board.GetCellState(position) == state;
  };
  const auto has_line = [&](CellPosition a, CellPosition b, CellPosition c) {
    const std::array<CellPosition, 3> line{a, b, c};
    return std::ranges::all_of(line, has_state);
  };
  for (int row = 0; row < kRows; ++row) {
    if (has_line({.row = row, .col = 0}, {.row = row, .col = 1}, {.row = row, .col = 2})) {
      return true;
    }
  }
  ……
```

## 注释位置对照

位置由注释回答哪一类问题决定（规则与矩阵见标识 `bg-comment-style-v1` 的知识文件「注释位置：上方 vs 行尾」）：

```text
不佳（同一意图一会儿上方、一会儿行尾，读者摸不到规律）：
// 校验坐标与目标格子。
if (!IsValidPosition(position)) {
  return false;
}
CellState& cell = cells_.at(ToFlatIndex(position));
if (cell != CellState::kEmpty) {
  return false;
}
cell = state;  // 写入棋子

改写（块级注释放它解释的步骤上方；单条拒绝原因行尾）：
if (!IsValidPosition(position) || state == CellState::kEmpty) {
  return false;  // 坐标无效或不是向空格落子，拒绝。
}
CellState& cell = cells_.at(ToFlatIndex(position));
if (cell != CellState::kEmpty) {
  return false;  // 目标格子已被占用，拒绝覆盖。
}
cell = state;  // 校验全部通过，写入棋子。
```

另一类禁止改法是把单句拒绝原因抬到 `if` 上方——条件已自明，注释离开它解释的语句：

```text
不佳（单句拒绝原因离开行尾，叠成一块）：
// 坐标无效或要写入的是空格，拒绝。
if (!IsValidPosition(position) || state == CellState::kEmpty) {
  return false;
}

改写（拒绝原因留在行尾）：
if (!IsValidPosition(position) || state == CellState::kEmpty) {
  return false;  // 坐标无效或要写入的是空格，拒绝。
}
```

私有成员默认行尾；长类型声明已折行时整条回退上方（规则见标识 `bg-comment-style-v1` 的知识文件「行尾超宽 / 声明过长：溢出回退」）：

```cpp
// 棋盘格子的存储数组，按行依次存放。   ← std::array 声明已折行，走上方
std::array<CellState, static_cast<std::size_t>(kCellCount)> cells_{};

Board board_;                                  // 对局的棋盘。
Player current_player_ = Player::kCross;       // 当前轮到的对局玩家，X 先手。
GameResult result_ = GameResult::kInProgress;  // 当前对局结果。
std::vector<Move> history_;                    // 本局落子历史。
```

同组短成员的行尾注释先写成员装的是什么（如「本局落子历史。」），缩短时只删排布、先后、写入动作这后半句，禁止为对齐删掉「它是什么」——`history_` 曾被缩成「按发生顺序存放。」，删掉本体后读者看不到这是本局的落子历史：

```text
不佳（为对齐缩短行尾注释时删掉了本体，只剩存放动作）：
std::vector<Move> history_;                    // 按发生顺序存放。

改写（先写成员装的是什么，与「对局的棋盘。」同一句式，宽度相当仍在同一列对齐）：
std::vector<Move> history_;                    // 本局落子历史。
```

短字段行尾与长数组上方回退在同一个 class 内并存，是溢出规则的合法结果，不是随意不一致（`history_` 判例；规则见标识 `bg-comment-style-v1` 的知识文件「行尾超宽 / 声明过长：溢出回退」与「领域函数与成员注释」）。

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
//===------------------------------------------------------------------------------------------===//
// board.h - 定义井字棋棋盘及其格子状态。
//===------------------------------------------------------------------------------------------===//

/// 棋盘的行数。
inline constexpr int kRows = 3;

/// 棋盘格子的状态。
enum class CellState : std::uint8_t {
  kEmpty = 0,   ///< 空格。
  kCross = 1,   ///< X 棋子。
  kNought = 2,  ///< O 棋子。
};

/// 棋盘格子的行列坐标，行和列从 0 开始。
struct CellPosition {
  int row = 0;  ///< 行坐标。
  int col = 0;  ///< 列坐标。
};

/// 井字棋的棋盘。
///
/// 固定 3 行 3 列；提供读取棋盘格子状态、放置棋子和检查棋盘是否已满的功能。
class Board {
 public:
  /// 获取指定坐标处的棋盘格子状态。
  ///
  /// @param position 行列坐标。
  /// @throws std::out_of_range 坐标不在棋盘范围内。
  [[nodiscard]] CellState GetCellState(CellPosition position) const;
};
```

正例的判定条件：文件头横幅定宽 100 列（与 `ColumnLimit: 100` 同一档）、标题行在横幅之间；声明注释用 `///`，类型意图独占一行并保留棋盘锚点；行尾注释成员齐全（`CellState` 定案全量），用 `///<` 列对齐、用简洁词；`CellPosition` 字段带 `= 0` 默认值；类注释走「概述 + 槽 1 + 一段细节」，能力与结构约束不拆两道空行；函数声明带 `@` 块时按骨架留槽位，`@returns` 复述概述则省略；`CellPosition` 不写有符号选型旁白；不写类型选型旁白与组织自述；注释是完整中文短句，专有名词保留英文。

## 键值配置正反对照

键值配置文件（`.clang-format` / `.clang-tidy` / `.clangd` / `config.toml` / `.gitignore` 等）的条文见标识 `bg-comment-style-v1` 的知识文件「键值配置」，三种 YAML 注释粒度分见其下三个小节。

不佳（`.clangd` 的每个警告标志各写一遍「未生成编译数据库时」，同一句重复多遍）：

```yaml
  Add:
    # 未生成编译数据库时按 C++20 解析，与目标的 cxx_std_20 一致。
    - -std=c++20
    # 未生成编译数据库时仍用 libc++，与 CMake 的 -stdlib=libc++ 相同。
    - -stdlib=libc++
    # 未生成编译数据库时打开 -Wall，与目标编译选项一致。
    - -Wall
    # 未生成编译数据库时打开 -Wextra，与目标编译选项一致。
    - -Wextra
    # 未生成编译数据库时警告即错误，与目标编译选项一致。
    - -Werror
```

改写（注释贴在 `Add` 键上，覆盖整组标志；标志列表不再重复）：

```yaml
  # 未生成编译数据库时的解析兜底，与目标的 C++20、libc++ 和警告选项一致。
  Add:
    - -std=c++20
    - -stdlib=libc++
    - -Wall
    - -Wextra
    - -Werror
```

不佳（关闭项注释把检查名再写一遍，名字已经在下一行）：

```yaml
  # 关闭 readability-magic-numbers：尺寸常量集中定义，不逐个字面量报警。
  - "-readability-magic-numbers"
```

改写（上一行只留原因，检查名不再复述）：

```yaml
  # 尺寸常量集中定义，不逐个字面量报警。
  - "-readability-magic-numbers"
```

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
#===--------------------------------------------------------------------------------------------===#
# .clang-tidy - C++ 静态检查与命名规则
#===--------------------------------------------------------------------------------------------===#
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
#===--------------------------------------------------------------------------------------------===#
# .clang-format - C++ 工程格式模板
#
# 本文件是两仓统一格式基准源：新阶段 / 新工程把本文件复制为各自根目录。
#===--------------------------------------------------------------------------------------------===#
```

改写（一行用途，无复制/两仓旁白）：

```yaml
#===--------------------------------------------------------------------------------------------===#
# .clang-format - C++ 格式化规则
#===--------------------------------------------------------------------------------------------===#
```

不佳（段标题把 `header` 运行期要打印的步骤链再列一遍，导航复述）：

```bash
#===--------------------------------------------------------------------------------------------===#
# main：1 配置 → 2 编译 → 3 格式与静态检查 → 4 测试 → 5 运行
#===--------------------------------------------------------------------------------------------===#
```

改写（段标题是对象名；步骤留在 `header` 的字符串里，五步由运行期输出承担）：

```bash
#===--------------------------------------------------------------------------------------------===#
# main - 验证步骤
#===--------------------------------------------------------------------------------------------===#
```
