---
kb_id: "bg-google-cpp-style-v1"
title: "Google C++ 风格落地决策"
domain: "cpp-teaching"
subdomain: "style"
tags: [google-style, naming, identifiers, headers, style-guide, clang-tidy]
level_range: [0, 5]
dependencies: [bg-comment-style-v1]
created: "2026-09-28"
updated: "2026-10-04"
chunk_strategy: "semantic_heading"
estimated_tokens: 2100
---

# Google C++ 风格落地决策

两仓（cpp-board-games 与 cpp-notes）的 C++ 标识符命名与编码规则以 [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) 为主标准，废止此前「函数与变量小驼峰」决策。本文件记录主标准的采纳范围、有意偏离的白名单与各章的检查方式；审查清单见 `cpp-development` 技能 `references/google-cpp-style.md`，可自动执行的部分由 `.clang-format`（`BasedOnStyle: Google`）与 `.clang-tidy`（`readability-identifier-naming` 等）承担。

## 命名表

| 类别 | 规则 | 示例 |
| --- | --- | --- |
| 类型（class/struct/enum/别名模板） | PascalCase | `Game`、`PlaceResult` |
| 概念与模板参数（类型形参） | PascalCase | `Board` |
| 函数（普通、成员、访问器） | PascalCase | `IsValidPosition`、`GetCellState`、`PlacePiece`、`GetResult` |
| 变量与参数（含 lambda 捕获外的局部量） | snake_case | `position`、`table_name` |
| 类数据成员（含私有/受保护） | snake_case 加尾下划线 | `cells_` |
| 常量与 constexpr（含枚举子） | `k` 加 PascalCase | `kRows`、`Player::kCross`、`CellState::kEmpty` |
| 命名空间 | 语义明确的小写单词 | `tictactoe` |
| 宏 | `UPPER_CASE` 且带项目前缀 | 尽量不使用宏 |
| 文件名 | snake_case（扩展名偏离，见下） | `game_state.h` |

命名翻转的影响面：函数从 camelBack 翻转为 PascalCase（`is_valid` → `IsValid`、`makeGreeting` → `MakeGreeting`），变量从 camelBack 翻转为 snake_case（`defaultLimit` → `default_limit`），枚举子补 `k` 前缀（`Player::X` → `Player::kCross`）。查询型访问器同样用 PascalCase，避免同一章内混用两套函数命名。Google Function Names 一节允许访问器用 `snake_case`，本仓有意统一为 PascalCase，属策略性收紧而非指南原文要求；`IsValid` 这类普通函数的 PascalCase 则是指南原文规则。

映射函数的名字必须让读者看出源端或目标端角色（`CellStateFor`、`BoardToString`）；单独的 `Of` / `To` 短后缀看不出两端是什么，禁止使用。依据是 Google「descriptive；eschew abbreviation」：`MarkOf(Player)` 要读签名才知道返回棋子还是返回别的。正反对照见标识 `bg-naming-cases-v1` 的知识文件。

## 整型与枚举底层类型

按角色分层的采纳表（代码按此落地）：

| 角色 | 类型 | 理由 |
| --- | --- | --- |
| `kRows` / `kCols` / `kCellCount` | `int` | 固定小棋盘的领域边界与坐标使用同一有符号类型 |
| `CellPosition::row` / `col` | `int` | Board 必须直接拒绝负坐标和上界越界 |
| 遍历棋盘的循环变量 | `int` | 遍历的是领域坐标，不是容器下标 |
| `Board::ToFlatIndex` 与 `std::array` 容量 | `std::size_t` | 已验证坐标转存储下标；行、列操作数先各自转换，`kCols` 保持 `int` |
| 封闭状态枚举底层 | `std::uint8_t` | 取值集合与布局，不是算术尺寸 |

- **固定棋盘坐标**：棋盘尺寸、`CellPosition` 和棋盘遍历使用 `int`。`Board::IsValidPosition` 同时检查负坐标和上界，调用方不必先在输入层替 Board 补边界。
- **受控存储下标**：`Board::ToFlatIndex` 是 private static 函数；行、列操作数各自 `static_cast<std::size_t>` 后再做乘加（`kCols` 保持 `int`，由通常算术转换提升；用户定案，先建 `const int` 中间变量再对变量转换一次的写法同时废弃），并交给 `std::array`。整式一次性转换（`static_cast<std::size_t>(row * kCols + col)`）仍禁——乘加发生在窄类型域内，`bugprone-misplaced-widening-cast` 报警。
- **枚举底层类型**：成员少的状态码类（`Player`、`CellState`、`GameResult`、`PlaceResult`）默认写 `enum class Name : std::uint8_t`。Google 与 LLVM 都不强制底层类型，LLVM 仅在紧凑布局时按需使用；本仓定为默认约定，依据是教学可预测与对象布局稳定，属有意偏离。`std::uint8_t` 只用于这类封闭状态码，不回溢到坐标或尺寸。
- 依据与落地明细见「有意偏离白名单」第 7、8 条；注释写法见标识 `bg-comment-style-v1` 的知识文件「枚举与常量行尾注释」。

## 有意偏离白名单

只允许以下偏离，其余章节默认按 Google 落地；新增偏离必须先改本表：

1. **`#pragma once`**：不用 path-based `#ifndef` include guard，教学与 Clang 生态下更简单。
2. **扩展名 `.cpp` / `.h`**：不用 Google 的 `.cc`。
3. **C++20**：本仓锁定 C++20，与指南的版本策略一致。
4. **异常**：规则核心与可测试 API 禁止用异常表达**业务结果**，用结果类型（`PlaceResult`、`GameResult`）承担；**契约违反**（如 `GetCellState` 越界前置条件失败）可抛 `std::out_of_range`；CLI 与工具边界允许异常。相对指南「基本不用异常」，核心对业务更严、对契约与边界略松。`what()` 文案与「本阶段不用日志框架」见标识 `bg-exception-message-format-v1` 的知识文件。
5. **注释外形**：内容跟 Google（写意图与取舍，不复述代码），分段横幅跟 LLVM（见标识 `bg-comment-style-v1` 的知识文件）。
6. **不强制 cpplint**：用 `clang-format` 与 `clang-tidy`（含 `google-*` 可启用项）代替。
7. **固定棋盘坐标**：尺寸、坐标和坐标遍历用 `int`，由 `Board::IsValidPosition` 同时检查负数和上界；仅 private `ToFlatIndex` 与容器容量使用 `std::size_t`。分层表见「整型与枚举底层类型」。
8. **枚举底层类型**：封闭状态码类默认写 `enum class Name : std::uint8_t`；Google 与 LLVM 均不强制，本仓定为默认约定。详见「整型与枚举底层类型」。
9. **项目头裸文件名**：单游戏单库组件教学阶段，库对外头文件放在库组件 `include/` 下（如 `include/game_state.h`），项目头一律写引号裸文件名（`#include "game_state.h"`），不建 `include/<namespace>/` 子目录，也不写 `"tictactoe/….h"`。Google Names and Order of Includes 倾向带路径前缀；本仓与脚手架、`cpp-notes` 的 `greeting` 布局对齐，组件目录名已隔离，多库真实共享前禁止再引入 `include/<ns>/`。详见「Header Files」与标识 `bg-cmake-conventions-v1` 的知识文件「组件化阶段布局」。

## 各章采纳要点

- **Header Files**：自包含头文件；include 顺序与分组（相关头 → C 系统头 → C++ 标准库 → 其他库 → 项目头，组间空行）由 Google `clang-format` 承担；头文件内函数定义仅限模板与简单函数；慎用前置声明。项目头一律写成**引号 + 相对 PUBLIC include 根的裸文件名**（`#include "board.h"`、`#include "game.h"`）；禁止 `"tictactoe/….h"` 前缀路径，也禁止尖括号项目头；依据见有意偏离白名单第 9 条。配套约束：库组件的 `target_include_directories` PUBLIC 根指向 `include/`，头文件直接落在该根下，见标识 `bg-cmake-conventions-v1` 的知识文件「组件化阶段布局」。
- **特殊成员**：拷贝/移动或析构等需要用户声明的特殊成员，头文件只写声明、定义放在对应 `.cpp`，减轻头文件隐式内联与编译依赖（与 [Chromium C++ Dos and Don'ts](https://chromium.googlesource.com/chromium/src/+/HEAD/styleguide/c++/c++-dos-and-donts.md) 的出类定义习惯一致）；零参默认构造例外（用户定案）：`Board() = default;`、`Game() = default;` 直接写在头文件类内，`.cpp` 不再重复定义（已从 Board 泛化到 Game）。有函数体的成员函数定义一律在 `.cpp`。成员函数不因潜在的编译期求值而标 `constexpr`：现行 Google 指南把 constexpr 用于「define true constants or to ensure constant initialization」，且 constexpr 函数一般需定义在声明它的头文件里（LLVM 也只把 constexpr 用于全局/静态常量避免启动开销，Chromium 用 `inline constexpr` 表达真常量，Linux 内核是 C 项目、C23 的 constexpr 未被采用）；联网复核四家后维持本仓取舍——`Board::IsValidPosition`、`Board::IsFull`、`Board::ToFlatIndex` 这类运行期辅助只作头文件声明、定义在 `.cpp`，`constexpr` 留给 `kRows`/`kCols`/`kCellCount` 真常量。平凡析构不声明（交给隐式生成）。`explicit` 只约束单参构造（检查 `google-explicit-constructor`）；零参构造不加 `explicit`。声明与定义顺序见标识 `bg-declaration-order-v1` 的知识文件。
- **`[[nodiscard]]`**：查询型 const 成员（`GetCellState`、`GetResult`）与忽略结果即可能导致逻辑错误的结果型 API（`Game::Place` → `PlaceResult`）一律标注；不在几乎所有非 void 函数上无差别铺开。clang-tidy `modernize-use-nodiscard` 已随 `modernize-*` 启用；语言讲解见 cpp-notes 的 `nodiscard.qmd` 章。
- **`noexcept`**：依据 Google 原文「Specify noexcept when it is useful and correct」，接口简单性优先。无潜在抛出路径的查询与换算函数标注（`Board::IsValidPosition`、`Board::IsFull`、`Board::ToFlatIndex`）；契约含抛出（`GetCellState` 抛 `std::out_of_range`）或实现保留 `at()` 潜在抛出路径的函数不标（`PlacePiece`）。`noexcept` 是函数类型的一部分：头文件声明与 `.cpp` 定义**都必须**写，只写一侧编译报「missing exception specification」。`bugprone-exception-escape` 随 `bugprone-*` 启用，兜底校验 noexcept 承诺（如 noexcept 函数内不得调用可能抛出的 `at()`）。
- **终端展示与瘦 `main`**：打印和读入住游戏适配层 `apps/`，不进规则库——规则核心不得依赖 `iostream` 或终端（见标识 `bg-project-decisions-v1` 的知识文件「架构决策」）。`apps/include/cli.h` 与 `apps/src/cli.cpp` 放 `PrintGame` 和 `PlayToEnd`；`apps/src/main.cpp` 只把标准流交给 `PlayToEnd`。函数在 `namespace tictactoe`，不另加 `cli` 命名空间。`apps/include` 仅作该可执行目标的 **PRIVATE** include 根。映射命名依据 `BoardToString` 正例见标识 `bg-naming-cases-v1` 的知识文件。
- **Scoping**：头文件禁止 `using namespace`（检查 `google-build-using-namespace`、`google-global-names-in-headers`）；内部链接优先匿名命名空间；非 const 全局变量严控。
- **Classes**：单参构造 `explicit`（检查 `google-explicit-constructor`）；`struct` = 数据聚合、`class` = 不变量加行为（与标识 `bg-project-decisions-v1` 的类型形式决策一致）；类内声明顺序：类型 → 静态常量 → 工厂 → 构造/赋值/析构 → 其余函数 → 数据成员，命名空间作用域头文件按「常量 → `enum class` → `struct` → 自由函数」排列，完整标准见标识 `bg-declaration-order-v1` 的知识文件；`=default` 与有体定义落点见上文「特殊成员」。
- **Functions**：短函数；重载优于易混淆默认实参；输出优先用返回值；不强制尾返回类型；传参选型见「Functions 传参表」。
- **实现文件分组与垂直空白**：函数定义之间空一行；函数体内守卫/前置校验与主逻辑之间空一行，函数不以空行开头或结尾（依据 [Google Vertical Whitespace](https://google.github.io/styleguide/cppguide.html#Vertical_Whitespace)「Use vertical whitespace sparingly」，函数内空行只用于分隔逻辑块）；定义顺序随头文件（见标识 `bg-declaration-order-v1` 的知识文件 C 节）；实现注释的密度与写法见标识 `bg-comment-style-v1` 的知识文件「实现注释」。
- **所有权与转换**：堆所有权用 `unique_ptr`，禁止裸 `new`/`delete`；禁止 C 风格转换，用 `static_cast` 等具名转换；指针判空用 `nullptr`；规则核心不依赖 `dynamic_cast` 做分支。
- **const、命名空间与整型**：只读接口标 `const`，编译期常量用 `constexpr` 加 `k` 命名。井字棋公开类型、自由函数和跨头文件共享的领域常量统一位于 `namespace tictactoe`；三个相互依赖的棋盘尺寸常量须按依赖顺序连续写为命名空间作用域的 `inline constexpr` 声明（`kRows`、`kCols`、`kCellCount`），不分散到 class、重复头或无关 `.cpp`。组件目录与 CMake 动态库 target 同为 `tictactoe`，但它们与 C++ 命名空间属于不同层次，不从阶段编号推导。`Board::IsValidPosition` 是可供调用方使用的静态边界检查；只服务 Board 存储的 `ToFlatIndex` 保持 private。领域数值按「整型与枚举底层类型」分层使用 `int` 与 `std::size_t`。
- **Inclusive Language**：标识符与注释避免排斥性用语；中文教学语域另见标识 `bg-chinese-voice-register-v1` 的知识文件。

## Functions 传参表

传参选型按现行指南 [Inputs and Outputs](https://google.github.io/styleguide/cppguide.html#Inputs_and_Outputs) 一节执行，不沿用旧文与 cpplint 时代「输出一律指针」的经典表；notes 侧同表登记在标识 `cpp-naming-format-v1` 的知识文件。

| 场景 | 推荐方式 | 说明 |
| --- | --- | --- |
| 只读小对象（`int`、`double`、小 `struct` 如 `CellPosition`） | 按值 | 拷贝廉价，调用处清晰 |
| 只读大对象（`string`、`vector`、大结构） | `const T&` | 避免昂贵拷贝 |
| 需要修改且必须存在（非可选输出 / 输入输出） | 非 `const` 引用 `T&` | 引用不可为空，现行指南口径 |
| 需要修改且可能为空（可选输出 / 输入输出） | 非 `const` 指针 `T*` | 调用处可见 `&` 或 `nullptr` |
| 输入输出且必须存在 | `T&` | 同非可选输出 |
| 输入输出且可能为空 | `T*` | 可选 inout |
| 「本该是引用」的可选只读输入 | `const T*` | 可空输入 |
| 可选按值输入 | `std::optional<T>` | 现行指南对可选值输入的首选 |
| 转移所有权 | `std::unique_ptr<T>` 按值 | 现代所有权语义 |
| 共享所有权 | `std::shared_ptr<T>` 按值或 `const&` | 视是否增减引用计数 |

优先返回值，少用输出参数；堆所有权用 `unique_ptr` / `shared_ptr`，禁止裸 `new` / `delete`。输入参数排在输出参数之前。

## 区间谓词写法

边界判断默认写成 `x >= low && x < high`（如 `IsValidPosition` 里的 `position.row >= 0`），不写成 `0 <= x && x < high` 的夹心方向；两者长度相当，后者只损失「条件与边界同名」的可读性，不带来任何 formatter 收益。断行位置交给 `clang-format` 按 `ColumnLimit` 决定，不追求「一行一维」，也不增设 `.clang-format` 键值去强制按维断行（`AlignOperands` 等键只调运算符对齐，管不了语义配对）。分组括号按「布尔表达式语义分组」执行，本条只定比较方向。

## 混合优先级算术括号

`*` / `/` / `%` 与 `+` / `-`（或位运算）混用在同一表达式时，必须给高优先级子表达式显式加括号，如 `ToFlatIndex` 先括住乘积再相加；同优先级连续运算不强制。依据是可读性：读者不该靠心算优先级解析下标换算，也不该靠 formatter 的断行位置推断结合顺序。clang-tidy `readability-math-missing-parentheses`（随 `readability-*` 启用）负责报警；本仓保留该检查、改代码消警告，不关闭检查也不加 NOLINT。本条与「区间谓词写法」的「比较方向」并列、互不覆盖：前者管算术优先级，后者管比较写法；逻辑组合的分组括号见下节。

## 布尔表达式语义分组

布尔表达式的比较子句按语义分组加括号：同一维度的下界与上界两个比较括成一组，组间用逻辑运算符连接，如 `IsValidPosition` 的 `(position.row >= 0 && position.row < kRows) && (position.col >= 0 && position.col < kCols)`（用户定案，为本仓约定）。阈值与边界：

- 两个语义组各括一组（行一组、列一组）；组内、组间运算符不变。
- 恰好两个简单比较的守卫不括号（`PlacePiece` 的 `!IsValidPosition(position) || state == CellState::kEmpty`、`Game::Place` 的轮次检查）——两个条件一眼可数，加括号是噪声。
- `&&` 与 `||` 混用时必须加括号，`-Wlogical-op-parentheses`（随 `-Wall`）报警兜底。
- 禁止给整个表达式再套一层括号；折行位置交给 `clang-format`（`AlignOperands: Align` 对齐续行运算符）。

依据：[Google Boolean Expressions](https://google.github.io/styleguide/cppguide.html#Boolean_Expressions) 允许在行宽内为可读性使用恰当括号并要求同一文件一致；MISRA C:2004 Rule 12.5（Advisory，后并入 [MISRA C:2012](https://misra.org.uk/) Rule 12.1）要求 `&&` 与 `||` 的操作数加括号；[LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html) 对纯逻辑组合无此要求（仅编译器强制混合算术括号）；[OpenCV 编码风格](https://github.com/opencv/opencv/wiki/coding_style_guide) 以 Google 指南为基础。LLVM 与 MISRA 均不强制「语义分组」本身，本仓仍将其定为约定——分组让布尔式的维度结构与 `clang-format` 的断行对齐互相对应，隔期回看不必心算优先级。本条与「区间谓词写法」（定比较方向）、「混合优先级算术括号」（定算术优先级括号）并列、互不覆盖。

## 检查方式

- 可自动执行：`.clang-format`（排版与 include 分组）、`.clang-tidy` 命名选项与 `google-*` 启用项。阶段 `build-and-run.sh` 在编译后固定运行 `clang-format --dry-run --Werror` 与基于 `build/compile_commands.json` 的 `clang-tidy`，任一警告即失败；clangd 在编辑器内实时报告同一套诊断。目标是在本仓启用检查集内保持零 clang-tidy 警告。
- 不能自动检查的条目（命名表语义、偏离白名单、声明顺序、所有权）：Agent 按 `cpp-development` 技能 P0 与审查清单把关，代码评审逐条核对。
