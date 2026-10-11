---
kb_id: "bg-google-cpp-style-v1"
title: "Google C++ 风格落地决策"
domain: "cpp-teaching"
subdomain: "style"
tags: [google-style, naming, identifiers, headers, style-guide, clang-tidy]
level_range: [0, 5]
dependencies: [bg-comment-style-v1]
created: "2026-09-28"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 6200
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

命名翻转：函数与查询型访问器统一 PascalCase（`is_valid` → `IsValid`），变量 snake_case（`defaultLimit` → `default_limit`），枚举子补 `k` 前缀（`Player::X` → `Player::kCross`）。Google Function Names 一节允许访问器用 `snake_case`，本仓有意统一为 PascalCase，属策略性收紧而非指南原文要求；`IsValid` 这类普通函数的 PascalCase 则是指南原文规则。

映射函数的名字必须让读者看出源端或目标端角色（`PlayerToCellState`、`BoardToString`）；单独的 `Of` / `To` 短后缀看不出两端是什么，禁止使用。依据是 Google「descriptive；eschew abbreviation」：`MarkOf(Player)` 要读签名才知道返回棋子还是返回别的。正反对照见标识 `bg-naming-cases-v1` 的知识文件。

## 函数语义角色表

命名形态只解决「长得像什么」，语义角色解决「做什么」。函数名的前缀或首词按语义角色固定，读者从名字即可判断返回值性质与调用约束：

| 语义角色 | 前缀 / 首词 | 返回 | 示例 |
| --- | --- | --- | --- |
| 读取查询 | `Get` + 名词短语 | 被读取的对象 | `GetCellState`、`GetCurrentPlayer`、`GetHistory`、`Game::GetResult` |
| 谓词判定 | `Is` / `Has` / `Are` + 名词短语 | `bool` | `IsValidPosition`、`IsFull`、`HasPlayerLine` |
| 尝试受理 | `Try` + 动词 | 结果类型表达成败 | `Game::TryPlace` → `PlaceResult` |
| 确定性动作 | 领域动词原形 | 视操作 | `PlacePiece`、`PlayToEnd`、`PrintGame`、`ChooseMove` |
| 映射 / 转换 | 源端 + `To` + 目标端 | 目标类型 | `PlayerToCellState`、`BoardToString`、`GameResultToString`、`ToFlatIndex` |
| 读入 | `Read` + 宾语 | 读入结果或是否成功 | `ReadRowAndCol`、`ReadOwnedLine`、`ReadMatchKind`、`ReadStrength` |
| 写出 | `Write` + 宾语 | `void` | `WriteSnapshot` |
| 计算 | 结果名词短语（不强制 `Compute` 前缀） | 计算值 | `TerminalScore`、`ResultAfterMove` |

动作与查询分界：会改动状态的函数用领域动词（`PlacePiece`、`TryPlace`），只读函数用 `Get` / `Is` / `Has`，同一函数只能落在一行。谓词宾语可由接收者类名承担：成员谓词 `Board::IsFull` 不必叠成 `IsBoardFull`（Google/本仓风格下冗余，对比 `IsValidPosition` 不叫 `IsBoardPositionValid`）；自由函数场景才把对象写进名字（如 `IsBoardFull(board)`）。`ResultAfterMove` 是终局判定助手，返回计算出的 `GameResult`，语义属「计算」；`CompletesLine` 返回 `bool` 却是谓词白名单例外，登记见「有意偏离白名单」第 10 条。

表内是第一档，已经在用或一出现就按此落地。第一档的分界补充：`Set` 只表示简单赋值，现在没有 `Set` 函数，不把 `PlacePiece`、`TryPlace` 改成 `Set`；`Can` 留给「做得成做不成」，与 `Is` 分开（现在没有这种函数，不把 `IsValidPosition` 改成 `CanPlace`）；中缀 `From` 是反方向的工厂名，现在不用，也不把已有的 `To` 翻成 `From`。

第二档只登记角色、等出现对应函数再用，不预先造函数：`Find` 表示查找，找不到要有明确的空结果，不与 `Has` 混用；`Make` 表示造出新对象，本仓用构造函数，不另造 `CreateGame`；`Add` / `Remove` / `Clear` / `Reset` 表示容器式修改，现在没有这种接口。中缀 `Of` / `And` 不采用——`Of` 看不出两端，`And` 会把两个动作写成一个名字。后缀 `Count` 只用于个数，尺寸常量继续 `kCellCount`，不改成函数；`Kind` 是 LLVM 给判别枚举的后缀，本仓枚举已经叫 `GameResult`、`CellState`，不加；`Impl`、`Internal`、`Ex` 和双下划线前缀都不进公开名字。不把 LLVM 的 `Kind`、OpenCV 的 `cvt` 缩写、Linux 内核的 `__` 内部前缀带进本仓。

## 四家形态对照

Google / LLVM / OpenCV 三家的命名形态对照（Microsoft 仅作对照），本仓取 Google 为主标准。此表是内部审查口径，不进入读者正文：

| 形态 | Google | LLVM | OpenCV | Microsoft（仅对照） | 本仓 |
| --- | --- | --- | --- | --- | --- |
| 类型 | PascalCase | PascalCase | PascalCase | PascalCase | PascalCase |
| 函数 | PascalCase | camelBack（首词小写，如 `isValid`） | camelCase（如 `cvtColor`） | PascalCase | PascalCase |
| 变量 / 参数 | snake_case | camelCase | camelCase | camelCase | snake_case |
| 类数据成员 | snake_case 加尾下划线 | camelCase（无后缀） | camelCase | `m_` 前缀或 camelCase | snake_case 加尾下划线 |
| 常量 / 枚举子 | `k` 加 PascalCase（偏好） | 命名常量 PascalCase | 全大写宏（`CV_8UC1`）为主 | PascalCase | `k` 加 PascalCase |
| 访问器 | 允许与数据成员同名（snake_case） | 无统一强制 | 小写 `get` / `set` 前缀 | `Get` / `Set` 前缀 | `Get` 前缀加 PascalCase |

本仓在「函数 PascalCase」「常量 `k` 前缀」上与 Google 一致，在「访问器统一 `Get` 前缀」上比 Google 更紧。LLVM / OpenCV 的函数与变量形态与本仓不同，跨仓对照时不得把 camelCase 函数带入本仓代码。

## 访问器取舍

查询型访问器统一取 `Get` 前缀加 PascalCase（`GetCellState`、`GetResult`、`GetCurrentPlayer`、`GetHistory`），不复用数据成员名。Google「Accessors and Mutators」允许访问器用与数据成员同形的 snake_case（`cells()` 读 `cells_`），本仓有意收紧为 `Get` 前缀：

- 头文件注释概述以「获取」开头（`/// 获取当前对局结果。`），与 `Get` 前缀的动词对齐；
- 查询与「计算 / 判定」在类内并存（`GetResult` 读缓存，`ResultAfterMove` 重算），`Get` 前缀把「读已存状态」与「算新结果」区分开；
- 谓词已用 `Is` / `Has` 前缀，`Get` 前缀使三类只读接口一眼可分。

取舍不扩散：底层写入 `PlacePiece` 保持领域动词，不用 `Set` 前缀；`ResultAfterMove`、`TerminalScore` 等计算角色不用 `Get` 前缀。

## 领域形参角色表

同一领域角色跨函数取同一个名字：调用点与实现点不必回看签名就能对上（OpenCV「一致实参次序」、LLVM「descriptive names」、Google Variable Names「按角色命名」）。本仓固定表：

| 类型 / 角色 | 固定名 | 禁止 |
| --- | --- | --- |
| `CellState` 形参（写入或比对的值） | `state` | `cell`、`piece`、`mark` |
| `CellState` 局部值（含 lambda 形参） | `state`；相对玩家时用 `mine` / `theirs` | 用 `cell` 表示状态 |
| `CellState&` 指向存储槽 | `stored` | `cell` |
| `CellPosition` 形参或局部 | `position` | `cell` |
| `Player` 形参 | `player`；已有语义处沿用 `current` / `opponent` | — |
| `Board` / `Game` 形参 | `board` / `game` | — |
| 类数据成员 | snake_case 加尾下划线 | — |

关键区分：`cell` 只表示位置或存储槽，不表示状态。`CellState& stored` 是槽位引用、`CellState state` 是状态值，两者不共用一个名字；`CellState& cell = cells_.at(...)` 让 `cell` 同时指槽与状态，禁用。正反对照见标识 `bg-naming-cases-v1` 的知识文件「领域形参角色对照」。

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
3. **C++20**：本仓锁定 C++20，与指南的版本策略一致。四家基线对照：Google 风格指南以 C++20 为目标、不使用 C++23 特性；LLVM 构建要求 C++17（`LLVM_REQUIRED_CXX_STANDARD 17`）；Linux 内核锁在 `-std=gnu11`，GCC 15 默认改 gnu23 后仍显式锁旧标准避开 C23 的 `bool`；OpenCV 5.0 要求并推荐 C++17。编译器有 `-std=c++23` 等开关不等于该升标准；四家基线都不高于 20 时保留 20。
4. **异常**：规则核心与可测试 API 禁止用异常表达**业务结果**，用结果类型（`PlaceResult`、`GameResult`）承担；**契约违反**（如 `GetCellState` 越界前置条件失败）可抛 `std::out_of_range`；CLI 与工具边界允许异常。相对指南「基本不用异常」，核心对业务更严、对契约与边界略松。`what()` 文案与「本阶段不用日志框架」见标识 `bg-exception-message-format-v1` 的知识文件。
5. **注释外形**：内容跟 Google（写意图与取舍，不复述代码），分段横幅跟 LLVM（见标识 `bg-comment-style-v1` 的知识文件）。
6. **不强制 cpplint**：用 `clang-format` 与 `clang-tidy`（含 `google-*` 可启用项）代替。
7. **固定棋盘坐标**：尺寸、坐标和坐标遍历用 `int`，由 `Board::IsValidPosition` 同时检查负数和上界；仅 private `ToFlatIndex` 与容器容量使用 `std::size_t`。分层表见「整型与枚举底层类型」。
8. **枚举底层类型**：封闭状态码类默认写 `enum class Name : std::uint8_t`；Google 与 LLVM 均不强制，本仓定为默认约定。详见「整型与枚举底层类型」。
9. **项目头裸文件名**：单游戏单库组件教学阶段，库对外头文件放在库组件 `include/` 下（如 `include/game_state.h`），项目头一律写引号裸文件名（`#include "game_state.h"`），不建 `include/<namespace>/` 子目录，也不写 `"tictactoe/….h"`。Google Names and Order of Includes 倾向带路径前缀；本仓与脚手架、`cpp-notes` 的 `greeting` 布局对齐，组件目录名已隔离，多库真实共享前禁止再引入 `include/<ns>/`。详见「Header Files」与标识 `bg-cmake-conventions-v1` 的知识文件「组件化阶段布局」。
10. **`CompletesLine` 谓词形态**：`bool CompletesLine(const Game&, CellPosition, CellState)` 返回 `bool` 但不取 `Is` / `Has` 前缀，保留领域动词形态。它描述「假设落子凑成三连」这一 AI 探测动作，`IsCompletingLine` 现在进行时别扭、`CanCompleteLine` 与搜索的确定性语义不符。白名单只此一例，新谓词仍必须取 `Is` / `Has` 前缀，不扩散。案例见标识 `bg-naming-cases-v1` 的知识文件「谓词白名单例外」。

## 各章采纳要点

- **Header Files**：自包含头文件；include 顺序与分组（相关头 → C 系统头 → C++ 标准库 → 其他库 → 项目头，组间空行）由 Google `clang-format` 承担；头文件内函数定义仅限模板与简单函数；慎用前置声明。测试源文件（`*_test.cpp`、`test_support.h`）与生产代码同一顺序：`<gtest/gtest.h>` 属「其他库」，排在 C++ 标准库之后、项目头之前，不得插在标准库前面。落地靠 `.clang-format` 的 `IncludeBlocks: Regroup` + `IncludeCategories` 显式分类（`^<gtest/` → 其他库、`^<[^/>]*\.h>` → C 系统头、`^<.*>` → C++ 标准库、其余 → 项目头）；Google 默认类别把 `^<.*\.h>` 一律归为高优先级，会让 gtest 落到标准库之前，故必须覆盖类别才能固定本顺序。项目头一律写成**引号 + 相对 PUBLIC include 根的裸文件名**（`#include "board.h"`、`#include "game.h"`）；禁止 `"tictactoe/….h"` 前缀路径，也禁止尖括号项目头；依据见有意偏离白名单第 9 条。配套约束：库组件的 `target_include_directories` PUBLIC 根指向 `include/`，头文件直接落在该根下，见标识 `bg-cmake-conventions-v1` 的知识文件「组件化阶段布局」。
- **特殊成员**：拷贝/移动或析构等需要用户声明的特殊成员，头文件只写声明、定义放在对应 `.cpp`，减轻头文件隐式内联与编译依赖（与 [Chromium C++ Dos and Don'ts](https://chromium.googlesource.com/chromium/src/+/HEAD/styleguide/c++/c++-dos-and-donts.md) 的出类定义习惯一致）；零参默认构造例外（用户定案）：`Board() = default;`、`Game() = default;` 直接写在头文件类内，`.cpp` 不再重复定义（已从 Board 泛化到 Game）。有函数体的成员函数定义一律在 `.cpp`。成员函数不因潜在的编译期求值而标 `constexpr`：现行 Google 指南把 constexpr 用于「define true constants or to ensure constant initialization」，且 constexpr 函数一般需定义在声明它的头文件里（LLVM 也只把 constexpr 用于全局/静态常量避免启动开销，Chromium 用 `inline constexpr` 表达真常量，Linux 内核是 C 项目、C23 的 constexpr 未被采用）；联网复核四家后维持本仓取舍——`Board::IsValidPosition`、`Board::IsFull`、`Board::ToFlatIndex` 这类运行期辅助只作头文件声明、定义在 `.cpp`，`constexpr` 留给 `kRows`/`kCols`/`kCellCount` 这类头文件里的公共常量。平凡析构不声明（交给隐式生成）。`explicit` 只约束单参构造（检查 `google-explicit-constructor`）；零参构造不加 `explicit`。声明与定义顺序见标识 `bg-declaration-order-v1` 的知识文件。
- **成员初始化（NSDMI）**：成员默认值写在类内声明处，不在构造函数重复；零参构造仍以头内 `= default` 为唯一入口。按类型分三类写法（用户定案，经 `readability-redundant-member-init` 机械验收修正）：① `std::array` 与聚合型成员写 `member_{}`（`cells_{}`）——`std::array` 无值语义默认构造，省略 `{}` 会让元素落到不确定值，`{}` 才是逐元素值初始化；② 带默认构造的类子对象与容器**不写** `{}`（`Board board_;`、`std::vector<Move> history_;`）——`Board board_{};`、`history_{};` 与省略写法调用同一默认构造，clang-tidy `readability-redundant-member-init`（随 `readability-*` 启用，warnings-as-errors）报冗余；③ 枚举或标量非零默认写 `member_ = Enum::kValue`（`current_player_ = Player::kCross`、`result_ = GameResult::kInProgress`）。**误解澄清**：`cells_{}` 是 `Board` 内部对 `std::array` 的 NSDMI，与 `Game` 对子对象 `board_` 的声明分属不同层级、互不排斥——看见 `cells_{}` 不必回避 `board_`，也不能把两者写成同一种花括号形态；`Board` 含私有成员且有 user-declared 默认构造，属非聚合，空 `{}` 不是聚合初始化而是 value-initialization。禁止同一成员既写 NSDMI 又在构造函数初始化；`struct` 聚合字段继续类内 `=` / `{}`（`Move::player`、`CellPosition` 坐标）。依据：Google Classes「成员在声明或构造初始化列表二选一」、[Abseil TotW #61](https://abseil.io/tips/61)、Chromium「Initialize members in the declaration where possible」、[P1008R1](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1008r1.pdf)（user-declared 构造函数使类型非聚合）、[cppreference list-initialization](https://en.cppreference.com/w/cpp/language/list_initialization)（空花括号列表 + 有默认构造 → value-initialization）。联网复核 Google/Chromium/Abseil（主路径）与 LLVM/OpenCV（仅对照）后维持本写法：Google/Chromium 均优先类内初始化且能 `= default` 就 `= default`，Abseil TotW #61 禁止 NSDMI 与构造初始化列表重复；LLVM 偏传统 init-list 但不反对 NSDMI，OpenCV 风格文档不强制 NSDMI。定案同见标识 `bg-project-decisions-v1` 的知识文件「成员初始化定案」。
- **`[[nodiscard]]`**：查询型 const 成员（`GetCellState`、`GetResult`）与忽略结果即可能导致逻辑错误的结果型 API（`Game::TryPlace` → `PlaceResult`）一律标注；不在几乎所有非 void 函数上无差别铺开。clang-tidy `modernize-use-nodiscard` 已随 `modernize-*` 启用；语言讲解见 cpp-notes 的 `nodiscard.qmd` 章。
- **`noexcept`**：依据 Google 原文「Specify noexcept when it is useful and correct」，接口简单性优先。无潜在抛出路径的查询与换算函数标注（`Board::IsValidPosition`、`Board::IsFull`、`Board::ToFlatIndex`）；契约含抛出（`GetCellState` 抛 `std::out_of_range`）或实现保留 `at()` 潜在抛出路径的函数不标（`PlacePiece`）。`noexcept` 是函数类型的一部分：头文件声明与 `.cpp` 定义**都必须**写，只写一侧编译报「missing exception specification」。`bugprone-exception-escape` 随 `bugprone-*` 启用，兜底校验 noexcept 承诺（如 noexcept 函数内不得调用可能抛出的 `at()`）。
- **终端展示与瘦 `main`**：打印和读入住游戏适配层 `apps/`，不进井字棋动态库——规则核心不得依赖 `iostream` 或终端（见标识 `bg-project-decisions-v1` 的知识文件「架构决策」）。`apps/include/cli.h` 是应用层组件接口头：`PrintGame`、`PlayToEnd` 与组件内助手（`CellSymbol`、`BoardToString`、`ReadRowAndCol`、`ReadResult` 等）的声明集中在此，定义在 `apps/src/cli.cpp`；`apps/src/main.cpp` 只把标准流交给 `PlayToEnd`。函数在 `namespace tictactoe`，不另加 `cli` 命名空间。`apps/include` 仅作该可执行目标的 **PRIVATE** include 根。映射命名依据 `BoardToString` 正例见标识 `bg-naming-cases-v1` 的知识文件。
- **Scoping**：头文件禁止 `using namespace`（检查 `google-build-using-namespace`、`google-global-names-in-headers`）；非 const 全局变量严控。`.cpp` 定义写在 `namespace <项目> { }` 块内（Google/LLVM/OpenCV 一致做法），不逐个 `tictactoe::` 限定，调用点用限定名（如 `main` 的 `tictactoe::PlayToEnd(...)`）。**全仓源码 `.cpp` 禁用匿名命名空间**（用户定案，废止原匿名命名空间判例）：文件内助手一律声明在组件头文件、定义在对应 `.cpp`（`opponent.h` 的 `EmptyCells`/`Search` 等），打开头文件即见全部编排路径；测试文件的整包匿名命名空间（`game_test.cpp`、`opponent_test.cpp`）保留，登记为唯一例外。头文件禁用匿名命名空间（ODR 风险）。**类内私有助手与自由函数的边界**：只服务某个类型自身不变量的助手收进该类的 `private static`，不进命名空间作用域——终局判定两个助手 `ResultAfterMove`、`HasPlayerLine`（旧名 `IsLineFilled`）收进 `Game` 的 `private static`，`TryPlace` 内以静态成员调用（用户定案，与「`Game` 承担回合编排与胜负判定」的既有职责一致）；纯映射无状态的 `PlayerToCellState` 与 AI 探测用的 `opponent` 侧 `CompletesLine` 仍作命名空间自由函数。[Abseil TotW #186](https://abseil.io/tips/186) 偏好自由函数，本仓教学线取类内私有以保持「谁负责判定」一眼可见。定案与调研见标识 `bg-project-decisions-v1` 的知识文件「cli.h 组件接口头化」与「终局判定归 `Game`」。
- **Classes**：单参构造 `explicit`（检查 `google-explicit-constructor`）；`struct` = 数据聚合、`class` = 不变量加行为（与标识 `bg-project-decisions-v1` 的类型形式决策一致）；类内声明顺序：类型 → 静态常量 → 工厂 → 构造/赋值/析构 → 其余函数 → 数据成员，命名空间作用域头文件按「常量 → `enum class` → `struct` → 自由函数」排列，完整标准见标识 `bg-declaration-order-v1` 的知识文件；`=default` 与有体定义落点见上文「特殊成员」。
- **类内属性与访问说明符空白**：`.clang-format` 以 `AccessModifierOffset: -1`、`EmptyLineAfterAccessModifier: Never`（clang-format 13 起提供）、`BreakAfterAttributes: Never`（clang-format 16 起提供；不设时默认会在属性后断行，见 [llvm-project#75399](https://github.com/llvm/llvm-project/issues/75399)）锁定「访问说明符后不空行、`[[` 属性与声明同一行并按成员缩进」；编辑器里的 clangd 必须认得这些键，旧版会静默忽略未知键（依据 [ClangFormat Style Options](https://clang.llvm.org/docs/ClangFormatStyleOptions.html)）。条文见标识 `bg-comment-style-v1` 的知识文件「类内属性与访问说明符空白」。
- **Functions**：短函数；重载优于易混淆默认实参；输出优先用返回值；不强制尾返回类型；传参选型见「Functions 传参表」。
- **局部 lambda 与标准算法**：仅本函数使用的短闭包写成局部 lambda，并作 `std::ranges::all_of` 等标准算法的谓词（如 `Game::HasPlayerLine` 里的 `has_state`、`has_line`，与 `Board::IsFull` 的 `all_of` 同族），不拆成 `private static` 成员或自由函数，也不手写循环却不进标准算法（LLVM 常规使用 lambda、Google 现行指南允许 lambda，重点在格式与可读性）；需单测或多处复用才提为具名函数。lambda 是变量，按 snake_case 命名；返回 `bool` 的 lambda 是谓词，名字必须带 `is_` / `has_` / `are_` 前缀（若出现 `Can` 用 `can_`），与函数前缀同一套角色。已经是名词的局部量（`move`、`state`、`stored`）不动。正例见标识 `bg-naming-cases-v1` 的知识文件。
- **实现文件分组与垂直空白**：函数定义之间空一行；函数体内守卫/前置校验与主逻辑之间空一行；函数体内一段做一件事，同一段里性质相同的语句贴紧，换了一种检查或换了一步职责，段与段之间恰好空一行。性质相同指控制形状一样而且问的是同一件事：按行扫描与按列扫描都是「按下标取三个格子」，贴紧；写死的对角线坐标不是下标循环，前面空一行。函数不以空行开头或结尾，不连空两行（依据 [Google Vertical Whitespace](https://google.github.io/styleguide/cppguide.html#Vertical_Whitespace)「Use vertical whitespace sparingly」，函数内空行只用于分隔逻辑块；[LLVM 源码宽度](https://llvm.org/docs/CodingStandards.html#source-code-width) 同样要求不要堆空行；[OpenCV 编码风格](https://github.com/opencv/opencv/wiki/Coding_Style_Guide) 在函数之间和长函数的逻辑段之间留一行；[Linux 内核 coding-style](https://www.kernel.org/doc/html/latest/process/coding-style.html) 把函数写成一件事，空行只分开不同的逻辑块）。`clang-format` 的 `MaxEmptyLinesToKeep: 1` 只保住单行空行，没有键能按语义插空行，这是写法约定不是格式器选项。定义顺序随头文件（见标识 `bg-declaration-order-v1` 的知识文件 C 节）；实现注释的密度与写法见标识 `bg-comment-style-v1` 的知识文件「实现注释」。
- **所有权与转换**：堆所有权用 `unique_ptr`，禁止裸 `new`/`delete`；禁止 C 风格转换，用 `static_cast` 等具名转换；指针判空用 `nullptr`；规则核心不依赖 `dynamic_cast` 做分支。
- **字符串类型默认**：需要持有、拼接或修改的字符串用 `std::string`；只读参数、局部查表与编译期常量用 `std::string_view`（常量写 `inline constexpr std::string_view`，如 `kProgramName`；`std::string` 不可 `constexpr`，不用于编译期常量）；`const char*` 仅在零终止 C API 或需要 `nullptr` 语义的边界使用，不作默认。依据：Google/Abseil string_view 指引（只读参数按值传 `string_view`）、LLVM `StringRef`（只读参数默认，`.str()` 换取所有权）、OpenCV `cv::String` 即 `typedef std::string`、C++ Core Guidelines SL.str（`std::string` 持有、`std::string_view` 引用）。`string_view` 不承诺零终止，消费点限于流输出与查表赋值；接零终止 C 接口前先落 `std::string`。定案见标识 `bg-project-decisions-v1` 的知识文件「字符串默认类型」。
- **const、命名空间与整型**：只读接口标 `const`，编译期常量用 `constexpr` 加 `k` 命名。井字棋公开类型、自由函数和跨头文件共享的领域常量统一位于 `namespace tictactoe`；三个相互依赖的棋盘尺寸常量须按依赖顺序连续写为命名空间作用域的 `inline constexpr` 声明（`kRows`、`kCols`、`kCellCount`），不分散到 class、重复头或无关 `.cpp`。组件目录与 CMake 动态库 target 同为 `tictactoe`，但它们与 C++ 命名空间属于不同层次，不从阶段编号推导。`Board::IsValidPosition` 是可供调用方使用的静态边界检查；只服务 Board 存储的 `ToFlatIndex` 保持 private。领域数值按「整型与枚举底层类型」分层使用 `int` 与 `std::size_t`。
- **Inclusive Language**：标识符与注释避免排斥性用语；中文教学语域另见标识 `bg-chinese-voice-register-v1` 的知识文件。

## 配对头与 IWYU

`.cpp` 用到某个头提供的符号时，必须自己直接 include 该头；配对头已包含也不豁免，禁止吃传递包含：

| 情况 | `.cpp` 要不要再 include |
| --- | --- |
| 用到了该头的符号（如 `.cpp` 里的 `std::cout`），即使配对 `.h` 已含 `<iostream>` | 要（直接包含） |
| 完全没用到该符号（只是 `.h` 接口需要） | 不要 |
| 经配对头间接用到第三个头的符号 | 要，直接包含提供该符号的头 |

配套规则：`.cpp` 第一条 include 是自己的配对头（`board.cpp` → `"board.h"`）；头文件只包含自身声明需要的头，实现专用依赖（如仅 `.cpp` 用的 `<algorithm>`、`<stdexcept>`）放 `.cpp`。库核心仍禁止依赖终端：`<iostream>` 不得出现在动态库头文件，出现在 `apps/` 的 `cli.cpp` 时按上表直接包含。本仓以现行 Google Style「related headers 同样适用」条文为准（比 IWYU 工具「配对头可顶」的表述更严），不引入旧指南的例外句。抽检判例：三阶段 `board.cpp` 用 `std::ranges::all_of`/`std::size_t`/`std::out_of_range`，直接包含 `<algorithm>`/`<cstddef>`/`<stdexcept>`；`game.cpp`、`cli.cpp` 同法核对通过。

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

恰好几个同型坐标这类固定小元组：调用处要写明每个坐标时用几个参数（`has_line` 收三个 `CellPosition`，函数体内收进 `std::array<CellPosition, 3>` 交给 `std::ranges::all_of`）；已经握着一段现成序列时才用 `std::span<const T>`。不为三个参数换 span——花括号列表直接构造 `span` 是 C++26 的 P2447，C++20 下调用处要么先写具名数组、要么写双层花括号，都比现在难读。

## 比较操作数次序（反 Yoda）

对 `==`、`!=`、`<`、`<=`、`>`、`>=`（一侧为字面量、`nullptr`、枚举常量或具名 `constexpr` 时），非常量表达式一律写在左侧；为「常量在左」翻转操作数（Yoda 写法）禁止：

| 运算符 | 要求 | 正例 | 反例（禁止） |
| --- | --- | --- | --- |
| `==` / `!=` | 被测对象在左 | `x == 0`、`p != nullptr`、`state == CellState::kEmpty` | `0 == x`、`nullptr == p`、`CellState::kEmpty == state` |
| 单侧关系比较 | 非常量在左；必要时连同运算符一起翻转 | `x > 0`、`x < kRows`、`count >= 1` | `0 < x`、`kRows > x`（仅为「常量在左」而写时） |
| 半开区间 `[low, high)` | 两次比较均变量在左（形态 A，见「区间谓词写法」） | `x >= low && x < high` | `low <= x && x < high`（夹心方向，禁止） |

两侧皆非常量（`a == b`）或两侧皆字面量（`assert(3 != 4)`）无左右强制；`==`/`!=` 语义对称但仍固定「被测对象在左」。依据：Google C++ Style Guide 无「常量必须在左」专条、不推广 Yoda；Chromium 明文 Prefer `(foo == 0)` to `(0 == foo)`；LLVM clang-tidy 对比较操作数次序的默认偏好是常量在右（`PreferredConstantSide: Right`），且 `-Wparentheses` 已能抓住误写 `=`，Yoda 的历史动机失效。收口检查：`rg "0 ==|nullptr ==" games/`，期望零命中。

## 区间谓词写法

边界判断默认写成 `x >= low && x < high`（如 `IsValidPosition` 里的 `position.row >= 0`），不写成 `0 <= x && x < high` 的夹心方向；两者长度相当，后者只损失「条件与边界同名」的可读性，不带来任何 formatter 收益。断行位置交给 `clang-format` 按 `ColumnLimit` 决定，不追求「一行一维」，也不增设 `.clang-format` 键值去强制按维断行（`AlignOperands` 等键只调运算符对齐，管不了语义配对）。分组括号按「布尔表达式语义分组」执行，本条只定比较方向；夹心方向（`0 <= x && x < high`）与「比较操作数次序（反 Yoda）」同因禁止，教学文本可以用文字讲 `[0, kRows)` 数学区间，代码仍写形态 A。

## 混合优先级算术括号

`*` / `/` / `%` 与 `+` / `-`（或位运算）混用在同一表达式时，必须给高优先级子表达式显式加括号，如 `ToFlatIndex` 先括住乘积再相加；同优先级连续运算不强制。依据是可读性：读者不该靠心算优先级解析下标换算，也不该靠 formatter 的断行位置推断结合顺序。clang-tidy `readability-math-missing-parentheses`（随 `readability-*` 启用）负责报警；本仓保留该检查、改代码消警告，不关闭检查也不加 NOLINT。本条与「区间谓词写法」的「比较方向」并列、互不覆盖：前者管算术优先级，后者管比较写法；逻辑组合的分组括号见下节。

## 布尔表达式语义分组

布尔表达式的比较子句按语义分组加括号：同一维度的下界与上界两个比较括成一组，组间用逻辑运算符连接，如 `IsValidPosition` 的 `(position.row >= 0 && position.row < kRows) && (position.col >= 0 && position.col < kCols)`（用户定案，为本仓约定）。阈值与边界：

- 两个语义组各括一组（行一组、列一组）；组内、组间运算符不变。
- 恰好两个简单比较的守卫不括号（`PlacePiece` 的 `!IsValidPosition(position) || state == CellState::kEmpty`、`Game::TryPlace` 的轮次检查）——两个条件一眼可数，加括号是噪声。
- `&&` 与 `||` 混用时必须加括号，`-Wlogical-op-parentheses`（随 `-Wall`）报警兜底。
- 禁止给整个表达式再套一层括号；折行位置交给 `clang-format`（`AlignOperands: Align` 对齐续行运算符）。

依据：[Google Boolean Expressions](https://google.github.io/styleguide/cppguide.html#Boolean_Expressions) 允许在行宽内为可读性使用恰当括号并要求同一文件一致；MISRA C:2004 Rule 12.5（Advisory，后并入 [MISRA C:2012](https://misra.org.uk/) Rule 12.1）要求 `&&` 与 `||` 的操作数加括号；[LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html) 对纯逻辑组合无此要求（仅编译器强制混合算术括号）；[OpenCV 编码风格](https://github.com/opencv/opencv/wiki/coding_style_guide) 以 Google 指南为基础。LLVM 与 MISRA 均不强制「语义分组」本身，本仓仍将其定为约定——分组让布尔式的维度结构与 `clang-format` 的断行对齐互相对应，隔期回看不必心算优先级。本条与「区间谓词写法」（定比较方向）、「混合优先级算术括号」（定算术优先级括号）并列、互不覆盖。

## 行宽 ColumnLimit

| 来源 | 默认行宽 |
| --- | --- |
| Google `BasedOnStyle: Google` | 80 |
| LLVM Coding Standards + LLVM style | 80 |
| OpenCV `.clang-format` | 100 |
| Microsoft style（仅对照） | 120 |

本仓 `ColumnLimit: 100`（`assets/config/.clang-format` 模板与三阶段副本一致，已校验同源），取三家对照里已有人用的 100（OpenCV），不取没有出处的 90，也不取 Microsoft 的 120。此前的「80 且不跟 OpenCV 改 100」定案由本条覆盖：Windows 上 80 列偏窄，放宽只取有先例的 100。文件头横幅与 `ColumnLimit` 同一档：C++ 横幅 `//===` + 90 个 `-` + `===//`、`#` 家族横幅 `#===` + 92 个 `-` + `===#`，都正好 100 个字符（旧的「横幅固定 80 列、不随列宽拉长」定案由本条覆盖；模板与规则见标识 `bg-comment-style-v1` 的知识文件「文件头」）。断行位置交给 clang-format 按此值决定；超长行的断开与对齐见「超长续行」，相关括号约定见「区间谓词写法」「混合优先级算术括号」「布尔表达式语义分组」。

## 超长续行

超过 100 列的行按三类断开，`.clang-format` 显式锁定 `AlignAfterOpenBracket: Align`、`BreakBeforeTernaryOperators: true`、`AlignOperands: Align`；不写 `BinPackParameters`、`BreakBeforeBinaryOperators`、`ContinuationIndentWidth`，它们已是 `BasedOnStyle: Google` 的 C++ 默认，多写一键不改变 clang-format 21 的结果。用 21.1.8 对 `game.cpp` / `game.h` 预览（`ColumnLimit: 100`，其余继承阶段配置）得到以下正例：

- **形参（两档）**：整段签名不超过 100 列就一行；第一个形参仍能留在函数名那一行时，后续形参与它对齐——对齐的是 `(` 后面的第一个字符，不是 `(` 本身；连第一个形参都放不下时，在 `(` 后换行，再按 `ContinuationIndentWidth: 4` 续行，右括号留在最后一个形参那一行。正例：`ResultAfterMove(const Board& board, Player player)` 整行 85 列，收成一行。
- **三元运算符**：放得进 100 列就一行；放不下则在 `?` 和 `:` 之前断开，这两个运算符上下对齐。正例：`return player == Player::kCross ? GameResult::kCrossWin : GameResult::kNoughtWin;` 整行 85 列，收成一行。
- **二元运算符（如 `||`）**：沿用 Google/LLVM 默认 `BreakBeforeBinaryOperators: None`（运算符留在上一行末尾）加 `AlignOperands: Align`（下一操作数与上一操作数对齐）。正例：两条对角线的 `return has_line(...) || has_line(...)` 单行放不下，断成两行——`||` 留在第一行末尾，第二行的 `has_line` 与第一行的 `has_line` 对齐；实参列表本身能放进 100，不再在花括号中间断开。

## 检查方式

- 可自动执行：`.clang-format`（排版与 include 分组）、`.clang-tidy` 命名选项与 `google-*` 启用项。阶段 `build-and-run.sh` 在编译后固定运行 `clang-format --dry-run --Werror` 与基于 `build/compile_commands.json` 的 `clang-tidy`，任一警告即失败；clangd 在编辑器内实时报告同一套诊断。目标是在本仓启用检查集内保持零 clang-tidy 警告。
- 不能自动检查的条目（命名表语义、偏离白名单、声明顺序、所有权）：Agent 按 `cpp-development` 技能 P0 与审查清单把关，代码评审逐条核对。
