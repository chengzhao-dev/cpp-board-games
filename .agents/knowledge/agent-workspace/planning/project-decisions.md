---
kb_id: "bg-project-decisions-v1"
title: "项目决策依据"
domain: "agent-workspace"
subdomain: "planning"
tags: [decisions, architecture, boundaries]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 800
---

# 项目决策依据

本文件是项目决策的取舍记录：定案是什么、对照过哪些方案、为什么否决替代项。现行事实与现状以标识 `bg-project-overview-v1`、`bg-architecture-overview-v1` 的规范文件为准，编码条文权威在 `.agents/context/conventions/`，本文件不复述现行条文。

## 文档面定案记录

- 文档面采用完整重置方案：清理旧 `content/` 文件，保留 `content/` 目录本身，只创建 `content/tictactoe/`；`_quarto.yml` 仍只注册井字棋章节，不引用已清理的开发、架构或 Python 章节。现行文档范围见标识 `bg-project-overview-v1` 的规范文件。

## 架构决策

- C++ 是核心实现语言，当前基线为 C++20、CMake、Ninja、Clang 和 CTest。
- 井字棋已有三个阶段：`games/tictactoe/01-cli-game` 为双人终端，`02-cpu-opponent` 为同一规则核心上的双人/人机与多难度，`03-line-protocol` 为应用层逐行 JSON。Python 回放和本地 Web 只在协议层之后适配，不进入规则动态库。
- 井字棋核心规则与终端、Python、JSON、HTTP 和 WebSocket 解耦；规则核心不得依赖终端、GUI、Web、Python 或 Quarto。
- 同一套规则先由 C++ 测试直接验证，再由终端或其他适配层复用。
- 先用具体值类型和小型规则接口建立不变量，再考虑抽象；至少两个游戏真实复用且语义稳定后才提取共享库。
- 新代码的类型形式：取值封闭的集合用 `enum class`（Core Guidelines Enum.3），数据组合用 `struct` 聚合，不提前引入继承体系；类型定义在 `<game>` 命名空间并放在库组件 `include/` 下（裸文件名，不建 `include/<namespace>/`）。强类型包装不在井字棋首批使用。语言机制的系统讲解由 cpp-notes 基础分册承担，跨仓读者链接用 GitHub 绝对 URL（base 见标识 `bg-quarto-conventions-v1` 的知识文件）。
- 标识符命名与编码规则以 Google C++ Style Guide 为主标准，函数 PascalCase、变量 snake_case、常量与枚举子 `k` 前缀；此前「函数与变量小驼峰」决策废止，两仓（cpp-board-games 与 cpp-notes）对等执行。命名表、偏离白名单与各章采纳要点见标识 `bg-google-cpp-style-v1` 的知识文件。
- 井字棋库对外头文件里的常量形态固定为具名命名空间内的 `inline constexpr` 加 `k` 前缀（如 `tictactoe::kRows`），棋盘边界检查为 `Board` 的 public static 函数，内部行优先下标转换保持 private，头文件只留声明，`IsValidPosition`、`ToFlatIndex` 与 `IsFull` 的定义写在对应 `.cpp` 且不标 `constexpr`（运行期函数；依据见标识 `bg-google-cpp-style-v1` 的知识文件「特殊成员」，已联网复核 Google/LLVM/Chromium/Linux 内核四家后维持）；并按 Function Names 用 PascalCase；`const` 变量、`constexpr`、常量关键词与成员函数尾部 `const` 的语言讲解放 cpp-notes 的 `const-variables`、`constexpr`、`constant-keywords`、`const-member-functions` 四章（依据见其知识文件 `cpp-constant-keywords-v1`）；`[[nodiscard]]` 单独成章 `nodiscard.qmd`，查询型 const 成员与结果型 API 一律标注（采纳范围见标识 `bg-google-cpp-style-v1` 的知识文件）。
- **Board 与 Game 职责拆分**（主流两派调研后取「状态/规则」拆分派）：`Board` 只做状态与格子级操作（`IsValidPosition`、`GetCellState`、`PlacePiece`、`IsFull`、private `ToFlatIndex`），`Game` 承担回合、落子编排与胜负平判定（private static 的 `ResultAfterMove`、`HasPlayerLine`，及 `GetResult`、`TryPlace`）；胜负判定不进 `Board`——`GameResult` 在 game.h，Board 收结果查询会反向依赖，且与 04 章「Game 决定获胜」的教学线冲突；python-chess 式「规则全合并进 Board」属库便利设计，不采用。判平局由 `Board::IsFull()` 承担，Game 不再逐格扫空格。
- **棋子不单独建类型（用户定案，主流调研后维持）**：棋子身份由 `Player` 表达、棋盘格子状态由 `CellState` 表达，二者互不替代，映射只在 `PlayerToCellState` 一处；不引入第三套 `Piece` 枚举或 `std::optional` 重构——主流实现（GeeksforGeeks 的 char 网格、Code Review SE 的 Board+enum、Arduboy 的合并式格子枚举、AlgoMaster LLD 的 Player/Cell 双枚举）均无第三套棋子类型，继承式棋子属国际象棋式过度设计，与本仓「不预先建立复杂棋子继承体系」一致；`PlacePiece(position, CellState)` 可传 kEmpty 的缺口由运行时拒绝（board.cpp 守卫）、专测 `PlacePieceRejectsEmptyState` 与 03 章「kEmpty 只表示未落子，不能写入」教学共同覆盖；「强类型包装不在井字棋首批使用」继续有效。
- **API 改名定案（三轮收敛）**：最终形态为 `GetCellState`、`PlacePiece`、`PlayerToCellState`、`Game::TryPlace`、`GetCurrentPlayer`、`GetHistory`、`Game::HasPlayerLine`（private static）、`ToFlatIndex`——查询统一 `Get` 前缀、谓词取 `Is`，类内私有助手取 `Has` 前缀，映射源端进名（映射函数不用 For 后缀），受理可被拒的动作取 `Try`（推翻「富结果保持原名」例外）；中途的 `CellAt`、`Place`、`ToIndex`、`CellStateFor`、`LineFilled` 等旧名已全部替换，异常文案同步为 `"GetCellState: position is outside the board"`。
- **终局判定归 `Game`（用户定案）**：原自由函数 `IsLineFilled` 更名为 `Game::HasPlayerLine` 并与 `ResultAfterMove` 一起收进 `Game` 的 `private static`（`TryPlace` 内改静态成员调用）；两助手只服务 `Game` 自身不变量、无外部调用方，收进类后「谁负责判定」一眼可见（[Abseil TotW #186](https://abseil.io/tips/186) 偏好自由函数，本仓教学线有意取类内私有）。纯映射的 `PlayerToCellState` 与 AI 探测用的 `opponent` 侧 `CompletesLine` 仍作自由函数。对外叙事与 04 章只讲「判定对局是否结束 / 游戏结果」。规则见标识 `bg-google-cpp-style-v1` 的知识文件「Scoping」。
- **noexcept 取舍**：`IsValidPosition`、`IsFull`、`ToFlatIndex` 标注（无潜在抛出路径），`GetCellState`（契约抛 `std::out_of_range`）与 `PlacePiece`（经 `cells_.at()` 保留潜在抛出路径）不标；`noexcept` 属函数类型，声明与定义都必须写；规则见标识 `bg-google-cpp-style-v1` 的知识文件。
- **游戏目录更名**：`content/` 与 `games/` 下 `tic-tac-toe`→`tictactoe`，对齐 C++ 命名空间与库组件目录；stages 路由表同步改名 `tictactoe.md`，全仓路径引用已清洗。
- 终端展示与规则核心分层：`PrintGame` 与 `PlayToEnd` 住在适配层 `apps/include/cli.h`、`apps/src/cli.cpp`，仍在 `namespace tictactoe`，不另加 `cli` 命名空间。规则库 `tictactoe/` 不依赖 `iostream` 或终端。`apps/src/main.cpp` 只把标准流交给 `PlayToEnd`。`apps/include` 仅 PRIVATE 给 `app` 目标。
- **apps/ 分层经主流复核维持（用户定案）**：`cli.h`/`cli.cpp` 不并入 `tictactoe/`——LLVM（`llvm/include|lib|tools`，tools 全部 LLVM 专属）与 OpenCV（`modules/` 库代码 + 顶层 `apps/` 专属 CLI）都把可执行物与库分目录，判据是依赖方向而非领域相关性；并入会让「井字棋动态库不依赖终端」失去 CMake 层的机械可检查性。适配层职责的读者面叙述由 02 章分层句补足。
- **cli.h 组件接口头化（用户定案）**：cli.cpp 匿名命名空间的组件内助手（`kProgramName`、`Report`、`CellSymbol`、`BoardToString` 等）全部改为 cli.h 声明、cli.cpp 定义，cli.cpp 零匿名命名空间；与 OpenCV 模块私有头（`precomp.hpp`/`private.hpp`）同构，与 Google「头文件不放内部链接声明」不冲突（移入头的是外部链接组件 API）。同日扩展到规则库：game.cpp/opponent.cpp 匿名命名空间一并废除，全仓源码 `.cpp` 零匿名命名空间、测试文件整包匿名登记为唯一例外（其中 `At`/`kLines` 后整体删除）。规则落地见标识 `bg-google-cpp-style-v1` 的知识文件「Scoping」。
- **字符串默认类型（用户定案）**：持有、拼接与修改用 `std::string`，只读参数、局部查表与编译期常量用 `std::string_view`（常量写 `inline constexpr std::string_view`），`const char*` 仅留零终止 C API 或 `nullptr` 语义边界，不作默认；`kProgramName` ×3 与 03 章 `WriteSnapshot` 的 `status`/`winner` 查表局部变量已按此改造。规则落地见标识 `bg-google-cpp-style-v1` 的知识文件「字符串类型默认」。
- `01-cli-game` 保持双人终端。`02-cpu-opponent` 的对手只产生 `Move` 并调用同一个 `Game::TryPlace`。AI 不得成为核心规则的前置依赖。
- Python 过渡顺序为稳定 CLI、`subprocess`、版本化逐行 JSON、HTTP/Fetch；当前 Web 仅监听回环地址，限制请求体与坐标输入，实时需求明确后才评估 WebSocket。

## 编码与注释约定

编码定案的理由、覆盖过程与被否决的替代写法集中在此；条文的现行权威在 `.agents/context/conventions/` 的对应规范文件（`bg-google-cpp-style-v1`、`bg-comment-style-v1` 等），便于按需检索。

- **声明注释与契约注释统一用 Doxygen（用户定案）**：库头文件里的常量、枚举、结构体、类与函数声明注释一律 `///`（枚举值与字段行尾用 `///<` 列对齐），参数、返回值与异常用 `@param`/`@returns`/`@throws` 逐项说明，概述以动词开头且与函数名前缀对应；无额外约束的简单函数只留单行 `///` 概述；文件横幅、实现注释与 `.cpp` 内注释维持普通 `//`。调研依据（公开声明注释形态判例、`\param` 与 `@param` 取一、第三人称陈述主流）见标识 `bg-comment-style-v1` 的知识文件。
- **零参默认构造头内 `= default`（用户定案）**：`Board() = default;`、`Game() = default;` 直接写在头文件类内，`.cpp` 不再重复定义（已从 Board 泛化到 Game）；其余特殊成员与有函数体的定义仍在 `.cpp`。覆盖原「`Type::Type() = default;` 一律写 `.cpp`」的条款，规则见标识 `bg-google-cpp-style-v1` 的知识文件「特殊成员」与标识 `bg-declaration-order-v1` 的知识文件 C 节。
- **CellState 枚举值全量行尾注释**（用户定案，覆盖原「kCross/kNought 自明不注释」判例）：成员名需翻译为 X/O 棋子且与 `Player` 同名异义；`Player` 同步定为全量行尾注释（先手后手与棋子归属是类型注释装不下的语义，「执 X/O」禁用）；规则修订见标识 `bg-comment-style-v1` 的知识文件「枚举与常量行尾注释」。
- **ToFlatIndex 操作数转换（用户定案，推翻原「乘加留在 int、先存局部再转换一次」判例）**：`return (static_cast<std::size_t>(position.row) * kCols) + static_cast<std::size_t>(position.col);`，`kCols` 保持 `int` 由通常算术转换提升；整式一次性转换仍禁（`bugprone-misplaced-widening-cast`），`const int` 中间变量形态废弃。判例修订见标识 `bg-comment-cases-v1` 的知识文件「整型转换注释」与标识 `bg-google-cpp-style-v1` 的知识文件「整型与枚举底层类型」。
- **IsFull 用 `all_of`（用户定案）**：`std::ranges::all_of(cells_, …state != kEmpty)`，算法方向与函数名 IsFull 同向，弃用反向表达的 `none_of(cell == kEmpty)`；真值等价，行为不变。lambda 形参按「领域形参角色表」取名 `state`（`CellState` 形参一律 `state`，不用 `cell`）。
- **`CellPosition` 与 `Move` 默认成员初始化（用户定案）**：`int row = 0;`、`int col = 0;` 让默认构造坐标为 (0, 0)；`Move::player = Player::kCross` 为 clang-tidy `cppcoreguidelines-pro-type-member-init` 要求补齐（头内 `= default` 构造链要求所有字段可默认安全初始化）；聚合初始化与指名初始化不受影响；三阶段同步。
- **成员初始化定案（用户定案，经机械验收修正）**：成员默认值写在类内声明处（NSDMI），不在构造函数重复。三档：聚合型 `std::array` 写 `cells_{}`（省略 `{}` 会落到不确定值）；带默认构造的类子对象与容器不写花括号（`Board board_;`、`std::vector<Move> history_;`，写 `{}` 被 `readability-redundant-member-init` 判冗余）；枚举/标量非零默认写 `current_player_ = Player::kCross`、`result_ = GameResult::kInProgress`。**关键澄清**：`cells_{}` 与 `Game` 的 `board_` 分属两层、互不排斥，不必因看见 `cells_{}` 而回避 `board_`。依据与完整表述见标识 `bg-google-cpp-style-v1` 的知识文件「成员初始化（NSDMI）」。
- **NSDMI 与头内 `= default` 联网复核维持（用户定案）**：联网复核 Google Classes / Chromium / Abseil TotW #61 主路径与 LLVM/OpenCV 对照后，维持「NSDMI + 头内 `= default`」，否决「改回构造初始化列表」与「给 `board_`/`history_` 加 `{}`」（后者触发 `readability-redundant-member-init`）。复核摘要见标识 `bg-google-cpp-style-v1` 的知识文件「成员初始化（NSDMI）」。
- **ColumnLimit 定案 = 100（用户定案，覆盖原「ColumnLimit 定案 = 80」）**：对照 Google/LLVM 的 80、OpenCV 的 100 与 Microsoft 的 120 后取 100——Windows 上 80 列偏窄，放宽只取三家里有先例的 100，不取 90 或 120；同时显式锁定 `AlignAfterOpenBracket: Align`、`BreakBeforeTernaryOperators: true`、`AlignOperands: Align`，文件头横幅与列宽同档（C++ 横幅 `//===` + 90 个 `-` + `===//`、`#` 家族 `#===` + 92 个 `-` + `===#`，都正好 100 列；覆盖原「横幅固定 80 列」）；正文栏与 `--content-width` 同步加宽（后经 `bg-reading-surface-v1` 修正为 `body-width` 872px、内容列 840px），使 16px Bright Code 的代码块能不换行放下 100 列。理由与超长续行正例见标识 `bg-google-cpp-style-v1` 的知识文件「行宽 ColumnLimit」「超长续行」。
- **`.cpp` 实现注释密度（用户定案改写，推翻原「定义上方一行操作注释」）**：函数定义上一行不写操作摘要，契约留在头文件 `///`；实现注释只补契约没写的要点——关键分支行尾注（拒绝原因）、lambda 上一行写它判断什么；注释自己把对象写出，不用「该状态」「该玩家」和词条冒号；平凡访问器不加、不复制 @ 标签；守卫与主逻辑空行分组。规则见标识 `bg-comment-style-v1` 的知识文件「实现注释」。
- **注释动词与函数名前缀硬对齐（用户定案，覆盖旧「`Get` 取短结果名词句」条款）**：函数概述一律以动词开头，动词与函数名前缀对应——`Get` 用「获取」（`/// 获取当前对局结果。`、`/// 获取本局落子历史。`、`/// 获取指定坐标处的棋盘格子状态。`），`Is`/`Has` 用「检查」，`Try` 用「尝试」，`Place` 用「放置」，`To` 用「将…转换为…」（`ToFlatIndex` 结果词是一维索引），无前缀领域动词与函数名动词一致（`ResultAfterMove` 保持「判定…」）；禁纯名词短语概述、禁概述用「返回…」、禁垫话长动宾；类型与常量的概述仍用名词短语，不要求动词。细节进 `@param`/`@returns`；存储成员注释本体先行，不以排布开头；`GameResult` 行尾注释语义结果优先。规则与对照见标识 `bg-comment-style-v1` 与 `bg-comment-cases-v1` 的知识文件。
- **注释位置矩阵与实现注释密度（用户定案改写）**：位置由「注释回答哪一类问题」决定——声明契约 → 上一行 `///`；单条语句结果或拒绝原因 → 行尾 `//`（与代码 2 空格）；枚举值与公开/聚合字段 → 行尾 `///<` 列对齐；私有数据成员默认行尾 `//`，长类型声明已折行或超 100 列则整条回退上一行；成功路径只翻译语句的注释不写。`.cpp` 函数定义上一行不写操作摘要，关键步骤加行尾或上方注。类内垂直空白：`public:`/`private:` 后不空行，成员函数声明之间空 1 行，函数与数据成员之间空 1 行，数据成员组内不空行；Quarto 围栏同规、禁止坍缩。`.cpp` 定义顺序随头文件声明序。规则见标识 `bg-comment-style-v1` 的知识文件「注释位置：上方 vs 行尾」「实现注释」「空行总则」，案例见标识 `bg-comment-cases-v1`。
- **终局助手命名复核维持（用户定案）**：`HasPlayerLine`（谓词 `Has` + 名词，`Line` 与 `CompletesLine` 共用领域词）与 `ResultAfterMove`（计算：结果名词短语，与 `GetResult` 读缓存对仗）经别名评估后**维持现名**，不引入 `HasWinner`/`CheckWin`/`Evaluate*`/`Update*`；`PlayerLine` 不单独建类型，中文叙述用「获胜线」/「三连」。禁用废名 `IsLineFilled`。评估表见本文件同轮记录与标识 `bg-naming-cases-v1`。
- **Move/Board 分层接缝维持（用户定案）**：`Board` 只收 `CellPosition` + `CellState`（`PlacePiece(pos, state)` 保持双参）；`Move` 只装 `position` + `player`，不再存 `CellState`；映射唯一开口在 `Game::TryPlace`——用命名局部 `const CellState state = PlayerToCellState(move.player);` 再 `board_.PlacePiece(move.position, state)`。禁 `Board::PlacePiece(const Move&)`、禁 `Move` 增 `CellState` 字段、禁把 `Player` 枚举当棋盘存储类型、禁为消映射把胜负判定搬回 `Board`。理由与四派对照见标识 `bg-project-decisions-v1` 同轮记录。
- **`HasPlayerLine` 局部 lambda + `all_of`（用户定案）**：保留函数内局部 lambda（仅本函数使用，不拆 `private static` 成员或自由函数），作 `std::ranges::all_of` 的三格谓词（与 `IsFull` 同族）；算法仍为逐行、逐列循环 + 两条显式对角线，否决八线表/bitboard/增量计数器/魔法方阵。`CompletesLine` 与 `HasPlayerLine` 算法同构且必用 `all_of` 三格。规则见标识 `bg-google-cpp-style-v1` 的知识文件「局部 lambda 与标准算法」。
- **获胜判定算法化与注释文案收口（用户定案）**：`At`/`kLines` 整体删除，`IsLineFilled` 改签名 `bool IsLineFilled(const Board&, CellState)` 并以逐行、逐列加两条对角线的循环算法实现（联网复核两派并列，取可读性更好的循环；否决方向表法、末着三线、增量计数器），`ResultAfterMove` 直判；坐标构造统一指定初始化器 `.row/.col`（聚合表须显式双花括号），测试与 opponent 同步。后一轮把 `IsLineFilled` 更名为 `Game::HasPlayerLine` 并收进 `private static`（见「终局判定归 `Game`」）。枚举类型注释一句整体含义、「游戏进行中」统一、「执 X/O」禁用等文案收口见标识 `bg-comment-style-v1` 的知识文件。
- **「规则库」旧称清出代码与脚本注释（用户定案平实化）**：CMakeLists 注释、`apps/include/cli.h` 与测试 banner 的「规则库」改称「井字棋动态库」（`add_library` 为 SHARED）；「对手着法」「minimax」「终局效用」「即胜着」等旧称平实化为「落子选择」「极小极大」「终局得分」等。
- **布尔表达式语义分组（用户定案）**：比较子句按维度分组加括号，如 `IsValidPosition` 的 `(position.row >= 0 && position.row < kRows) && (position.col >= 0 && position.col < kCols)`；恰好两个简单比较的守卫不括号，`&&` 与 `||` 混用必须括号（`-Wlogical-op-parentheses`），禁止给整式外包一层。依据与阈值见标识 `bg-google-cpp-style-v1` 的知识文件「布尔表达式语义分组」。
- **命名形态表与语义角色表定案（用户定案）**：维持「类型 / 函数 PascalCase、变量 snake_case、常量与枚举子 `k` 前缀、成员 snake_case_」形态表，并补充「函数语义角色表」（Get / Is / Has / Try / 动词 / To / Read / Write / Compute，见标识 `bg-google-cpp-style-v1` 的知识文件「函数语义角色表」）；访问器统一 `Get` 前缀的取舍及四家形态对照也一并登记在该文件。`CompletesLine` 作为谓词白名单例外登记（返回 `bool` 但不取 `Is` / `Has` 前缀），不扩散。API 全量审计后仅重命名 `StatusToString` → `GameResultToString`（三阶段 apps 侧 cli.h / cli.cpp 共 6 个文件 + 07 章引用同步），其余标识符（`IsFull`、`TryPlace`、`GetResult`、`CompletesLine` 等）经审计维持现名。正反对照见标识 `bg-naming-cases-v1` 的知识文件「语义角色对照」与「谓词白名单例外」。
- **类内 `[[nodiscard]]` 同行与访问说明符空白（用户定案）**：`[[` 属性与声明同一行、缩进跟普通成员；`public:` / `private:` 后不空行，`private:` 前空 1 行。由 `.clang-format` 的 `AccessModifierOffset: -1`、`EmptyLineAfterAccessModifier: Never`、`BreakAfterAttributes: Never` 锁定，编辑器里的 clangd 必须认得这些键，过旧的版本会静默忽略。规则见标识 `bg-comment-style-v1` 的知识文件「类内属性与访问说明符空白」。

## 叙事与文档决策

- **03 章补全棋盘存储与下标换算（用户定案）**：board.h 的 `private:` 下（`cells_` 与 `ToFlatIndex`）入正文——`std::array` 选型理由（长度 `kCellCount` 写进类型、格子数不增减）、`row * kCols + col` 换算公式与示例 `(1, 2) → 5`、九个下标与行列坐标的对应图（共享助手新增 `render_index_strip`，qmd 单元只调用）；任务级 H2 重排为「认识棋盘格子」（2 个 H3）与「读写棋盘格子」（3 个 H3），单一类型、单枚举或单函数的小节不再独占任务级 H2。读者正文不用「数轴」课堂对照，图称数组下标对应图；「行优先」不进读者正文，用下标区间（第 0 行占下标 0–2）表述。
- **章节 title 全量复审（用户要求与二、三级标题同标）**：7 个章节 title、part 与 book title 按 `bg-chapter-structure-v1` 逐一复审后全部合规保留；需要修改的标题都在 H2/H3 层——「查看编号目录」→「查看井字棋工程目录」、「对手只返回一次落子」→「选择一次落子」、「直接完成一局」→「在终端完成一局」、03 章 H2/H3 重排、「占格后仍写成新状态」→「同一棋盘格子写入第二次」，反例已登记进标识 `bg-chapter-structure-v1` 的知识文件反例表；01 章 title 后续二次定稿，最终对象名见「标题短名重构定案」。
- **读者面工程叙事硬禁令**：上面的类型形式与命名决策只供 Agent 写代码使用，禁止把决策原样复述成读者正文的语言课。`content/**` 旁白只写契约的工程问题、消费方与验证方式。跨仓外链**默认零条**；仅小节末尾置可选深潜（「若要系统阅读…」），禁止「写法依据见 / 机制见 / 选型见 …」+ cpp-notes 的突兀依据句。点名反例句式（一律不进正文）：「取值封闭的集合用 `enum class`…」「数据组合用 `struct` 聚合…」「`inline` 让各翻译单元共享同一份定义…」「`CellPosition` 是纯数据聚合」「按 Google 风格用大驼峰」「命名遵守 Google C++ 风格指南：…」「用有符号整型承载…」「坐标字段为什么选定宽有符号整型…」「头文件里的常量统一写成 `inline constexpr`，写法依据见 cpp-notes…」。除 01 设计章外，工程 qmd 不为坐标选型链到「类型安全与数值边界」。工程改写对照见标识 `bg-chinese-style-cases-v1` 的知识文件，硬边界细则见 `writing-quarto` 技能 `references/zh/chapter-writing.md`「叙事范围」。
- **课堂类比禁令与 Plan 落盘约束**：正文与 agents 知识不写「数学课 / 平面直角坐标系」等跨学科课堂对照；坐标系只用程序事实（原点在左上角、`row` 向下增长、`col` 向右增长）与可观察行为表述，图注已交代原点与轴向的正文不复述。作者可在 Plan 里借类比构思，落盘到 qmd / agents 前必须改写成工程对象与可观察行为；自动执行见 `verify_content.py` 禁用模式（规则见 `writing-quarto` 技能 `references/zh/chapter-writing.md`「叙事范围」）。
- **验证闸有界（定案）**：每批次只跑一次闸（首验 + 至多一次复验），输出重定向 `temp/`，对话只读失败摘要；FAIL 必须清零、WARN 记台账不追清零；同一失败指纹连续 2 轮停手转人工。依据与细则见 testing 技能 `verification-matrix.md`「闸次与退出」，教训见 memory 的 `verify-loop` 主题。

- **段落连贯与体量定案（用户定案）**：逗号、句号后的下一分句必须复用上一分句的对象或写出关系词（given-new），禁止过简断裂；普通自然段最多 1–3 个主要概念，文件位置、入口个数等默认次要；普通段 token 带 70–220（链接只计锚文本），豁免章引言、节导语、块前单句导语、回顾、自测固定导语与 Callout。低于下限补衔接与必要次要概念，禁止凑字数句；节导语与块前单句导语豁免下限，过简改写靠衔接禁令。全仓读者 qmd 按概念盘点拆分重组，04 章「查看对局接口」导语定稿为「类 `Game` 编排 + 内部存储/对外入口次要展开」。规则见标识 `bg-paragraph-craft-v1` 的知识文件「过简断裂禁令」「概念负荷」与标识 `bg-chapter-structure-v1` 的知识文件「计数口径」「分层上限」，正反例见标识 `bg-chinese-style-cases-v1` 的知识文件「过简断裂段」，机械闸见 `verify_content.py`（`PARA_TOKENS_MIN=70`、链接折叠为锚文本后计数）。
- **书的单位称「章」与否定式预告禁令**：读者正文与 agents 知识指称书的单位一律用「章」（这一章、第 N 章、每章），停用「课」「课程」讲法（「语言课旁白」「课堂类比」等风格禁令标签除外）；正文不写「程序不提供 / 不实现 X」式否定式预告，即使当下为真也不写——后文补上该能力时句子失效，规则见标识 `bg-terminology-v1` 与 `bg-paragraph-craft-v1` 的知识文件。自测问题必须能由本章正文回答，本章回顾须承接本章正文各节交出的结果（规则见标识 `bg-chapter-structure-v1` 的知识文件）；起因是读者反馈：01 章「程序不提供电脑对手」一句与后文人机章冲突，回顾空泛，自测题目缺少正文依据。
- 游戏章节叙事按「八步流程 + STAR」故事线分配章内职责，依据见标识 `bg-engineering-storyline-v1` 的知识文件。
- **「职责 / 负责 / 承担」话术硬禁与 02/03 章叙事收口（用户定案）**：三词入 `verify_content.py` FORBIDDEN_TERMS 硬闸（qmd 范围），全仓 12 处清零；同节同一文件 blob 链接 ≥2 记 WARN，链接分三层——章引言是全章链接位、摘录短 filename 自明文件、正文复提用裸文件名（03 章链接 10→5，02、03 同节重复清零）；有 `###` 子节的 `##` 引言须承接上文并按顺序点名子节对象，禁无对象抽象并列（03 章「描述棋盘格子」引言重写）；代码块周边自然段写调用方与可观察后果，不复述成员清单（03 章「检查坐标后读写」块后段重写，02 章目录列表收进同一字数带、build/ 生成物句与树引出句拆分）；自测答案先答所问、一到两句（02 章两答案重写）。写作参照 learncpp 结构模式：概念先行 → 代码 → 逐细节工程讨论 → 测验。
- **四目录列表、自测行内代码与「；」并列分句定案（用户定案）**：并列目录（含构建生成的 `build/`）一次列全并入同一列表，列表后不用段落补列成员（02 章「井字棋工程有四个目录」）；自测问答的文件、路径与标识符指称统一行内代码，不挂链接，所属目录已确立时路径省去重复顶层前缀（如先写 `tictactoe/`，后文写 `include/board.h`）；停用「分进」；图前段只讲本页可见对象且单一主题，描述前章画面复述关键事实、不指称其版式（03 章「画面上方是列号」句删除，两段并一段）；H2 概览句可用「；」连接两个并列主谓分句（分句均以行内代码主语开头，03 章「`CellPosition` 定位一个棋盘格子；`CellState` 保存格子的状态」）。自动执行见 `verify_content.py`：「分进」硬闸、自测节链接 WARN、分号检查按同一口径豁免并列分句。
- **代码块版式定案（用户定案）**：删除 `--code-max-width` 宽度二次限宽（原 45rem），代码块与正文同宽、贴满 800px 正文列；代码块字号 0.9375rem → 1rem（16px，与正文同级）。正文列保持 800px、三栏壳约 1404（≤VitePress 1440 上限），宽屏只增加外侧留白，不以显示器宽度拉大正文（VitePress/Vue 文档站做法对照见 `theme-system.md`）。同步落点：`tokens.css`、`content.css`、`_quarto.yml` 注释、`check_layout.py` 断言、`theme-system.md`、`section-focus-and-density.md`（后已并入 `writing-howto.md`）。（后两条被同轮 ColumnLimit=100 与字体定案更新：`body-width` 现为 872px，内容列 840px。）
- **主题任务工序定案**：主题任务以 `designing-theme` 技能 `references/theme-spine.md` 为次序唯一入口（定表面 → 定字体 → 定尺度 → 定颜色 → 定组件 → 过闸），`theme-system.md` 只承担各步的 how；字体、栏宽与颜色定案的理由统一写进标识 `bg-reading-surface-v1` 的知识文件。
- **正文字体与阅读表面定案（用户定案）**：正文改为单字面 `LXGW Bright Medium`（Klee One 中笔画 + Ysabeau Office 西文，登记 weight 400，全站层级靠字号），移除 Fixel 与文楷 Screen；代码保持 `LXGW Bright Code`；`body-width` 872px（内容列 840px）承载 100 列代码不折行，窄屏只在代码块内横向滚动、打印恢复折行；`**` 保留 `font-synthesis: weight` 合成加粗，强调色不用链接蓝（亮 #000000、暗 #FFFFFF），callout 条色收敛到页面功能色。理由与排除项见标识 `bg-reading-surface-v1` 的知识文件。
- **代码语法色定案（用户定案）**：页面色与语法色统一到同一对 Primer 主题——亮色 Light Default、暗色 Dark Dimmed；语法色不再用 Quarto 内置的 2020 年 `github-light`/`github-dark`，改由 `palettes/github/highlight-light.theme` / `highlight-dark.theme` 提供（取色 Primer 当前 prettylights，`BackgroundColor` 与 `--code-bg` 相同，CSS 仍不覆盖 `span`）。暗色两处抬色：注释 `#768390`→`#9AA1AB`（本书代码底上过 4.5:1），关键字改用 Dark Default 红 `#FF7B72`；不把整页换回 Dark Default 近黑。配对结论与三处偏离见标识 `bg-reading-surface-v1` 的知识文件「明暗代码色跟哪一对 GitHub 主题」。
- **指称对象名定案（用户定案）**：自测题干禁用「这个、那个、这些、那些、哪个、哪些、哪一句、哪一层、哪一行、哪一块」（「什么」允许），题干先写出被问的对象与候选；节首句不得以「这些／这个／这一步」作话题而同句列不出对象名，所指要等后面 `###` 或代码围栏的算悬空。段内回指（同句或上一句已列出对象名的「这个数量」）合法；「这一章／下一章／这一节」不算。判定以整篇 qmd 为范围按标题切开，自动检查在 `verify_content.py`（题干 + 节首两处，答案折叠不扫）；条文见标识 `bg-paragraph-craft-v1` 的知识文件「代词不能代替未写出的对象」，题干条文同见 `bg-chapter-structure-v1`「自测问题」，对照见标识 `bg-chinese-style-cases-v1` 的知识文件「定结构与定句子：代词不能代替未写出的对象」。
- **先切模块再判句子定案（用户定案）**：写作判定先切分单位（章、节、自然段、句子、列表项、表格单元格、块；围栏、YAML、链接 URL 跳过），再按单位套对应工序规则，切分清单写在 `writing-quarto` 技能 `references/zh/writing-howto.md`「润色流程」开头；「一次对话」不是切分单位，是挂定段落与定句子的判定，全文见标识 `bg-paragraph-craft-v1` 的知识文件「一次对话」，读者正文默认不把结构体成员叫「字段」（03、07 章现用法保留）。`verify_content.py` 全量切分并只收三类高精度失败（类型接线句、「接着看／第 N 个枚举」改口、全称被下一句否定），段中心与对话件数留给工序与案例；九章按书序逐章走完九步、每章只跑 `verify --paths`，九章走完才跑一次 fast 与一次渲染。
- **章引言形态与免责腔定案（用户定案）**：无标题引言首选单个自然段（承接 + 本章做什么 + 可选源文件位置嵌段末句，2–4 句），必要时「一段 + 列表」；禁止两个散文自然段并立、≥3 段、单句孤儿段、结尾导航段；「示例位置句开口子」废止，摘录免责句（「服务于讲解」「片段不保证与源文件逐字一致」「不等于文件内顺序」）永不进入读者正文，同源保证交给 `verify`。自动执行：`check_zh_lint.py` 免责腔硬拦（仅读者正文）、`verify_content.py` 对章引言 ≥2 散文段判失败；规则正文见标识 `bg-chapter-structure-v1`，正反例见标识 `bg-chinese-style-cases-v1`。
- **标题短名重构定案（用户定案）**：标题只留对象名，三层字数硬限——title 2–6 字（对象名优先，本页交付就是一个动作才用动宾）、二级 2–6 字、三级 2–6 字（「常见错误」症状可到 8 字），同级同句式，指示（这一步、这次）、过程动词（记下、收进、用到）、方式、数量与把字句下放导语不进标题。01–07 章二级、三级与 title 都按章收成对象名（对局规则、工程目录、棋盘存储、一次落子、终端对局、电脑对手、局面快照），着陆页豁免，文件名不改，标题一变 Quarto 派生锚随之变化、旧深链失效是接受的代价。`verify_content.py` 对 title、二级、三级按新上限判失败并拦标题填充词，原 H2 10 字 WARN 分支删除。规则见标识 `bg-chapter-structure-v1` 的知识文件「字数硬限」「形式规则」。
## 外部依据

- C++ Core Guidelines：具体类型、纯函数倾向、RAII、窄接口和避免过早抽象。
- CMake `enable_testing`/`add_test`：顶层启用并注册可由 CTest 执行的测试。
- Python `subprocess`：退出码、stdout/stderr、超时和一次性/持续进程边界。
- MDN Fetch 与 WHATWG WebSocket：HTTP 状态检查、JSON 解析、连接生命周期和应用层消息协议。
- Berkeley CS188 Multi-Agent Search：Minimax 的 MAX/MIN、终局 utility、搜索深度和 alpha-beta。

## Agent 行为边界

Agent 读写边界的唯一出处是根 `AGENTS.md`「工作规则」（只读默认、写入触发、删除前读取、不动生成物），本文件不再复述。
