# Google C++ 风格检查清单

写或改 C++ 代码时按本清单自查；采纳范围、命名表与偏离白名单的依据见知识库 `bg-google-cpp-style-v1`。自动执行部分由 `.clang-format` 与 `.clang-tidy` 承担（clangd 在编辑器内实时报告命名违规），本清单管自动检查覆盖不到的条目。

## 标识符命名

- 类型、函数用 PascalCase（`Game`、`IsValidPosition`）；变量、参数用 snake_case（`position`）。
- 类数据成员带尾下划线（`cells_`）；常量与枚举子用 `k` 前缀（`kRows`、`Player::kCross`）。
- 命名空间 snake_case（`tictactoe`）；宏尽量不用，必须时 `UPPER_CASE` 带项目前缀。
- 同一 API 不得混用两套函数命名：查询型成员一律 `Get` 前缀加 PascalCase（`GetCurrentPlayer`、`GetHistory`）。
- 映射函数名必须含源端或目标端角色（`PlayerToCellState`、`BoardToString`、`GameResultToString`）；禁止单独 `Of` / `To` 且看不出两端的短名。
- 函数语义角色速查：查询 `Get`；谓词 `Is` / `Has`；尝试受理 `Try`（`Game::TryPlace`）；确定性动作用领域动词（`PlacePiece`）；映射 `源端 + To + 目标端`；读入 `Read`；写出 `Write`；计算用结果名词短语（`TerminalScore`、`ResultAfterMove`）。完整角色表见知识 `bg-google-cpp-style-v1`「函数语义角色表」。
- 访问器统一 `Get` 前缀加 PascalCase，不复用数据成员名（Google 允许 snake_case 同名访问器，本仓收紧，见「访问器取舍」）；底层写入保持领域动词，不用 `Set` 前缀。
- 谓词白名单例外：`CompletesLine` 返回 `bool` 但不取 `Is` / `Has` 前缀，已登记（白名单第 10 条），新谓词不得仿造。

## 头文件

- 头文件自包含：单独编译不缺声明；include 按组排序（相关头 → C 系统头 → C++ 标准库 → 其他库 → 项目头），组间空行，由 `clang-format` 维护。
- 项目头 include 写引号加相对 PUBLIC 根的裸文件名（`"board.h"`、`"game.h"`）；禁止 `"tictactoe/….h"` 前缀与尖括号项目头；库组件 PUBLIC include 根指向 `include/`，头文件直接放在该根下（白名单第 9 条与 `bg-google-cpp-style-v1`「Header Files」）。
- include guard 用 `#pragma once`（有意偏离 Google，白名单第 1 条）。
- 头文件内不写 `using namespace`；函数定义仅限模板与简单函数。
- 库对外头文件里的跨文件常量写成命名空间内 `inline constexpr` 加 `k` 前缀（`tictactoe::kRows`）；头文件内不写非 inline 的普通全局变量定义。

## 类与函数

- 单参构造 `explicit`；零参构造不加 `explicit`；`struct` 只做数据聚合，带不变量的类型用 `class`。
- 用户声明的拷贝/移动、析构等特殊成员：头文件只声明，定义放 `.cpp`；零参默认构造例外，`Board() = default;` 直接写在头文件类内，`.cpp` 不重复定义；有函数体的成员定义也在 `.cpp`；平凡析构不声明（见 `bg-google-cpp-style-v1`「特殊成员」）。
- 成员默认值写在类内声明处（NSDMI），不在构造函数重复：聚合型 `std::array` 写 `cells_{}`；带默认构造的类子对象与容器不写 `{}`（`board_`、`history_`，写 `{}` 触发 `readability-redundant-member-init`）；枚举/标量非零默认写 `current_player_ = Player::kCross`、`result_ = GameResult::kInProgress`。禁止同一成员既写 NSDMI 又在构造初始化列表重复（见 `bg-google-cpp-style-v1`「成员初始化（NSDMI）」）。
- 查询型 const 成员（`GetCellState`、`Game::GetResult`）与结果型 API（`Game::TryPlace` → `PlaceResult`）标 `[[nodiscard]]`；不在所有非 void 函数上无差别铺开。
- 终端打印与读入放在 `apps/` 私有模块（`include/cli.h` + `src/cli.cpp`）。`PrintGame` 按行列号打印，`PlayToEnd` 跑完一局。`src/main.cpp` 只把标准流交给 `PlayToEnd`。不把 `iostream` 推进井字棋动态库；`apps/include` 仅 PRIVATE。函数仍在 `namespace tictactoe`，不另加 `cli` 命名空间。
- 类内声明顺序：类型与别名 →（仅 `struct` 可把数据成员放最前）→ 静态常量 → 工厂 → 构造/赋值/析构 → 其余函数 → 数据成员。
- 命名空间作用域头文件自上而下：includes → `namespace` → `inline constexpr` 常量 → `enum class` → `struct`（被依赖者在前）→ 自由函数 → `class` 公开接口类型；`.cpp` 定义顺序与头一致。完整标准见知识库 `bg-declaration-order-v1`。
- 输出优先用返回值；重载优于易混淆默认实参；不写尾返回类型。

## 转换与所有权

- 禁止 C 风格转换，用 `static_cast` 等具名转换；指针判空用 `nullptr`。
- 堆所有权用 `unique_ptr`，禁止裸 `new`/`delete`；规则核心不用 `dynamic_cast` 做规则分支。

## 整型与枚举

- 棋盘尺寸、`kCellCount`、坐标和坐标遍历用 `int`。负坐标和上界越界都由 `Board::IsValidPosition` 判为非法（白名单第 7 条）。
- `kCellCount = kRows * kCols` 与行优先乘加留在 `int` 域。private `Board::ToFlatIndex` 对行、列操作数各自 `static_cast<std::size_t>` 后再乘加（`kCols` 保持 `int`），`std::array` 容量同样显式转换；整式一次性转换 `static_cast<std::size_t>(row * kCols + col)` 禁止（乘加在窄类型域内可能溢出）。不关闭 `bugprone-implicit-widening-of-multiplication-result`。
- 混合优先级算术（`*` / `/` / `%` 与 `+` / `-` 或位运算混用）给高优先级子表达式显式加括号（如 `ToFlatIndex` 先括住乘积再相加）；`readability-math-missing-parentheses` 报警即改代码，不关检查。依据见知识库 `bg-google-cpp-style-v1`「混合优先级算术括号」。
- 封闭状态码枚举默认写底层类型：`enum class Name : std::uint8_t`，且 `std::uint8_t` 仅用于这类封闭状态码（白名单第 8 条）；枚举子用作用域 `::` 访问（`CellState::kEmpty`），不用点号（`CellState.kEmpty` 编译错误）。
- 枚举行尾注释同一 `enum` 内要么全量、要么全不注，禁止半套（`CellState`、`Player` 全量判例）；行尾**语义结果优先**（先写「平局」「游戏进行中」等结果词，判定条件可选跟冒号后）；多条行尾时 `///<` 列对齐；写法见知识库 `bg-comment-style-v1`「枚举与常量行尾注释」。
- 混合优先级算术与命名等 `readability-*` 诊断：**先改代码消警告**，禁止新增 `NOLINT` 掩盖；占位成员函数若被 `readability-convert-member-functions-to-static` 命中，应在实现里真实读取实例状态（如 `cells_`），仍返回占位结果，而不是 NOLINT。

## 比较与区间

- 比较操作数次序（反 Yoda）：一侧是字面量、`nullptr` 或枚举常量时，非常量表达式在左（`x == 0`、`state == CellState::kEmpty`）；禁止 `0 == x`、`nullptr == p`，也禁止为「常量在左」写 `0 < x`。依据见知识库 `bg-google-cpp-style-v1`「比较操作数次序（反 Yoda）」。
- 半开区间写成两次"变量在左"比较（`position.row >= 0 && position.row < kRows`），不用 `0 <= x` 夹心方向；教学文本可用文字讲数学区间，代码仍写此形态。依据见知识库同文件「区间谓词写法」。

## 格式

- 行宽由 `ColumnLimit: 100` 统一控制（`assets/config/.clang-format` 模板与各阶段副本一致）；取三家对照里已有人用的 100（OpenCV），不取 Microsoft 的 120。断行位置交给 clang-format，不增设键值强行按维断行；超长行的断开与对齐规则见 `bg-google-cpp-style-v1`「行宽 ColumnLimit」「超长续行」。

## 异常与注释

- 规则核心与可测试 API 用结果类型表达业务结果（`PlaceResult`、`GameResult`），不用异常；契约违反（如 `GetCellState` 越界）可抛 `std::out_of_range`；CLI 与工具边界允许异常。文案见 `bg-exception-message-format-v1`。
- 注释内容写意图与取舍、不复述代码；分段横幅与注释语言按知识库 `bg-comment-style-v1`。`.clang-format` / `.clang-tidy` / `.clangd` 另见同文件「键值配置」下对应文件的三个小节：短横幅 + 邻接，禁止政策头与 kb 指针。
- 未完成实现用 `// TODO: <阶段或 issue> - <要做什么>`（旧式 `TODO(参考): …` 已降级为历史可识别、新码不写），禁止只写「见后续章」普通注释；收口用 `rg TODO`。
