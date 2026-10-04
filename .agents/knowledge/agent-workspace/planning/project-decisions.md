---
kb_id: "bg-project-decisions-v1"
title: "项目决策依据"
domain: "agent-workspace"
subdomain: "planning"
tags: [decisions, architecture, boundaries]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-10-04"
chunk_strategy: "semantic_heading"
estimated_tokens: 800
---

# 项目决策依据

本文件供 Agent 理解项目边界和已确认取舍使用。面向读者的完整解释统一维护在 `content/**/*.qmd`，本文件不作为 Quarto 入口。

## 文档重置决策

- 本轮采用完整重置方案：清理旧 `content/` 文件，保留 `content/` 目录本身，并只创建 `content/tictactoe/`。
- 根 `index.qmd` 服务井字棋主线，允许「后续棋类」用 `.landing-card.coming-soon` 占位，但不提前创建其他棋类页面或实现；`_quarto.yml` 仍只注册井字棋章节，不引用已清理的开发、架构或 Python 章节。
- 面向读者的完整设计、路线、验收和联网调研总结写入 Quarto；`.agents/knowledge/` 只保留 Agent 判断所需的简短决策和边界。
- 根 `index.qmd` 是整个仓库的项目入口，只说明项目目标、当前游戏入口和未来游戏范围；`content/<game>/index.qmd` 负责单个游戏已发布章节的阅读顺序。根首页不得复制具体游戏章节卡片，也不得把井字棋的一种玩法写成整个项目；规则、源码、构建、测试和协议内容留在对应游戏落地页与正文中。

## 架构决策

- C++ 是核心实现语言，当前基线为 C++20、CMake、Ninja、Clang 和 CTest。
- 井字棋已有三个阶段：`games/tictactoe/01-cli-game` 为双人终端，`02-cpu-opponent` 为同一规则核心上的双人/人机与多难度，`03-line-protocol` 为应用层逐行 JSON。Python 回放和本地 Web 只在协议层之后适配，不进入规则动态库。
- 井字棋核心规则与终端、Python、JSON、HTTP 和 WebSocket 解耦；规则核心不得依赖终端、GUI、Web、Python 或 Quarto。
- 同一套规则先由 C++ 测试直接验证，再由终端或其他适配层复用。
- 先用具体值类型和小型规则接口建立不变量，再考虑抽象；至少两个游戏真实复用且语义稳定后才提取共享库。
- 新代码的类型形式：取值封闭的集合用 `enum class`（Core Guidelines Enum.3），数据组合用 `struct` 聚合，不提前引入继承体系；类型定义在 `<game>` 命名空间并放在库组件 `include/` 下（裸文件名，不建 `include/<namespace>/`）。强类型包装不在井字棋首批使用。语言机制的系统讲解由 cpp-notes 基础分册承担，跨仓读者链接用 GitHub 绝对 URL（base 见标识 `bg-quarto-conventions-v1` 的知识文件）。
- 标识符命名与编码规则以 Google C++ Style Guide 为主标准，函数 PascalCase、变量 snake_case、常量与枚举子 `k` 前缀；此前「函数与变量小驼峰」决策废止，两仓（cpp-board-games 与 cpp-notes）对等执行。命名表、偏离白名单与各章采纳要点见标识 `bg-google-cpp-style-v1` 的知识文件。
- 井字棋库对外头文件里的常量形态固定为具名命名空间内的 `inline constexpr` 加 `k` 前缀（如 `tictactoe::kRows`），棋盘边界检查为 `Board` 的 public static 函数，内部行优先下标转换保持 private，头文件只留声明，`IsValidPosition`、`ToFlatIndex` 与 `IsFull` 的定义写在对应 `.cpp` 且不标 `constexpr`（运行期函数；依据见标识 `bg-google-cpp-style-v1` 的知识文件「特殊成员」，已联网复核 Google/LLVM/Chromium/Linux 内核四家后维持）；并按 Function Names 用 PascalCase；`const` 变量、`constexpr`、常量关键词与成员函数尾部 `const` 的语言讲解放 cpp-notes 的 `const-variables`、`constexpr`、`constant-keywords`、`const-member-functions` 四章（依据见其知识文件 `cpp-constant-keywords-v1`）；`[[nodiscard]]` 单独成章 `nodiscard.qmd`，查询型 const 成员与结果型 API 一律标注（采纳范围见标识 `bg-google-cpp-style-v1` 的知识文件）。
- **Board 与 Game 职责拆分**（主流两派调研后取「状态/规则」拆分派）：`Board` 只做状态与格子级操作（`IsValidPosition`、`GetCellState`、`PlacePiece`、`IsFull`、private `ToFlatIndex`），`Game` 承担回合、落子编排与胜负平判定（`LineFilled`、`ResultAfterMove`、`GetResult`、`Place`）；胜负判定不进 `Board`——`GameResult` 在 game.h，Board 收结果查询会反向依赖，且与 04 章「Game 决定获胜」的教学线冲突；python-chess 式「规则全合并进 Board」属库便利设计，不采用。判平局由 `Board::IsFull()` 承担，Game 不再逐格扫空格。
- **API 改名定案**（两轮收敛）：第一轮 `CellAt`→`GetCell`（Board 与 Game 两层）、`Place`→`TryPlace`（仅 Board；`Game::Place` 因返回 `PlaceResult` 富结果保持原名）、`ToIndex`→`ToFlatIndex`、`Game::Result`→`Game::GetResult`；第二轮（用户定案）`GetCell`→`GetCellState`（与返回类型 `CellState` 对齐）、`TryPlace`→`PlacePiece`（放置棋子的领域动词，弃用 Try 前缀）；异常文案同步为 `"GetCellState: position is outside the board"`。
- **noexcept 取舍**：`IsValidPosition`、`IsFull`、`ToFlatIndex` 标注（无潜在抛出路径），`GetCellState`（契约抛 `std::out_of_range`）与 `PlacePiece`（实现经 `cells_.at()` 保留潜在抛出路径）不标；`noexcept` 属函数类型，声明与定义都必须写；规则见标识 `bg-google-cpp-style-v1` 的知识文件。
- **声明注释与契约注释统一用 Doxygen（用户定案）**：库头文件里的常量、枚举、结构体、类与函数声明注释一律 `///`（枚举值与字段行尾用 `///<` 列对齐；先迁函数契约，同日扩到类型与常量声明）；函数参数、返回值与异常用 `@param`/`@return`/`@throw` 逐项说明，概述以动词开头且与函数名前缀对应（`Get` 获取、`Is` 检查、`Place` 放置、`To` 将…转换为…）；无额外约束的简单函数只留单行 `///` 概述，禁止用 @ 标签复述函数名与类型签名；文件横幅、实现注释与 `.cpp` 内注释维持普通 `//`。调研依据（LLVM StringRef.h/GlobalValue.h 与 OpenCV utility.hpp 的公开声明注释形态、`\param` 与 `@param` 等价取一保持一致、C++ 注释第三人称陈述主流）见标识 `bg-comment-style-v1` 的知识文件。
- **零参默认构造头内 `= default`（用户定案）**：`Board() = default;`、`Game() = default;` 直接写在头文件类内，`.cpp` 不再重复定义（已从 Board 泛化到 Game）；其余特殊成员与有函数体的定义仍在 `.cpp`。覆盖原「`Type::Type() = default;` 一律写 `.cpp`」的条款，规则见标识 `bg-google-cpp-style-v1` 的知识文件「特殊成员」与标识 `bg-declaration-order-v1` 的知识文件 C 节。
- **CellState 枚举值全量行尾注释**（用户定案，覆盖原「kCross/kNought 自明不注释」判例）：成员名需翻译为 X/O 棋子且与 `Player` 同名异义；规则修订见标识 `bg-comment-style-v1` 的知识文件「枚举与常量行尾注释」。
- **ToFlatIndex 操作数转换（用户定案，推翻原「乘加留在 int、先存局部再转换一次」判例）**：`return (static_cast<std::size_t>(position.row) * kCols) + static_cast<std::size_t>(position.col);`，`kCols` 保持 `int` 由通常算术转换提升；整式一次性转换仍禁（`bugprone-misplaced-widening-cast`），`const int` 中间变量形态废弃。判例修订见标识 `bg-comment-cases-v1` 的知识文件「整型转换注释」与标识 `bg-google-cpp-style-v1` 的知识文件「整型与枚举底层类型」。
- **IsFull 用 `all_of`（用户定案）**：`std::ranges::all_of(cells_, …cell != kEmpty)`，算法方向与函数名 IsFull 同向，弃用反向表达的 `none_of(cell == kEmpty)`；真值等价，行为不变。
- **`CellPosition` 与 `Move` 默认成员初始化（用户定案）**：`int row = 0;`、`int col = 0;` 让默认构造坐标为 (0, 0)；`Move::player = Player::kCross` 为 clang-tidy `cppcoreguidelines-pro-type-member-init` 要求补齐（头内 `= default` 构造链要求所有字段可默认安全初始化）；聚合初始化与指名初始化不受影响；三阶段同步。
- **`.cpp` 实现注释密度（用户定案）**：每个非平凡函数定义上方一行 `//` 操作注释 + 函数体内关键分支/步骤行尾注释（失败分支写拒绝原因），密度高于 Google Function Comments 基线；平凡访问器不加、不复制 @ 标签；函数体守卫与主逻辑之间空行分组（依据 Google Vertical Whitespace）。规则见标识 `bg-comment-style-v1` 的知识文件「实现注释」与标识 `bg-google-cpp-style-v1` 的知识文件「实现文件分组与垂直空白」。
- **注释动词与函数名前缀对齐（用户定案）**：`Get` 概述用「获取」不用「返回」（`GetCellState`、`Game::GetResult`），`Is` 用「检查」（`IsValidPosition`、`IsFull`），`Place` 用「放置」，`To` 用「将…转换为…」（`ToFlatIndex` 结果词是一维索引，不用「行优先下标」）；存储成员注释本体先行（`// 棋盘格子的存储数组，按行依次存放。`），不以排布开头；`GameResult` 行尾注释语义结果优先（`X 获胜：达成三连`、`平局：棋盘已满且双方均未三连`）。规则与对照见标识 `bg-comment-style-v1` 与 `bg-comment-cases-v1` 的知识文件。
- **「规则库」旧称清出代码与脚本注释（用户定案平实化）**：顶层与组件 CMakeLists 注释、`apps/include/cli.h` 与测试 banner 的「规则库」改称「井字棋动态库」（`add_library` 为 SHARED，定名与读者正文一致）；「对手着法」「minimax」「终局效用」「即胜着」「更好的着」等旧称同步平实化为「落子选择」「极小极大」「终局得分」等。
- **布尔表达式语义分组（用户定案）**：比较子句按维度分组加括号，如 `IsValidPosition` 的 `(position.row >= 0 && position.row < kRows) && (position.col >= 0 && position.col < kCols)`；恰好两个简单比较的守卫不括号，`&&` 与 `||` 混用必须括号（`-Wlogical-op-parentheses`），禁止给整式外包一层。依据与阈值见标识 `bg-google-cpp-style-v1` 的知识文件「布尔表达式语义分组」。
- **03 章补全棋盘存储与下标换算（用户定案）**：board.h 私有段（`cells_` 与 `ToFlatIndex`）入正文——`std::array` 选型理由（长度 `kCellCount` 写进类型、格子数不增减）、`row * kCols + col` 换算公式与示例 `(1, 2) → 5`、九个下标与行列坐标的对应图（共享助手新增 `render_index_strip`，qmd 单元只调用）；任务级 H2 重排为「认识棋盘格子」（2 个 H3）与「读写棋盘格子」（3 个 H3），单一类型、单枚举或单函数的小节不再独占任务级 H2。读者正文不用「数轴」课堂对照，图称数组下标对应图；「行优先」不进读者正文，用下标区间（第 0 行占下标 0–2）表述。
- **章节 title 全量复审（用户要求与二、三级标题同标）**：7 个章节 title、part 与 book title 按 `bg-file-title-naming-v1` 逐一复审后全部合规保留；需要修改的标题都在 H2/H3 层——「查看编号目录」→「查看井字棋工程目录」、「对手只返回一次落子」→「选择一次落子」、「直接完成一局」→「在终端完成一局」、03 章 H2/H3 重排、「占格后仍写成新状态」→「同一格子写入第二次」，反例已登记进标识 `bg-file-title-naming-v1` 的知识文件反例表。
- **游戏目录更名**：`content/` 与 `games/` 下 `tic-tac-toe`→`tictactoe`，对齐 C++ 命名空间与库组件目录；stages 路由表同步改名 `tictactoe.md`，全仓路径引用已清洗。
- 终端展示与规则核心分层：`PrintGame` 与 `PlayToEnd` 住在适配层 `apps/include/cli.h`、`apps/src/cli.cpp`，仍在 `namespace tictactoe`，不另加 `cli` 命名空间。规则库 `tictactoe/` 不依赖 `iostream` 或终端。`apps/src/main.cpp` 只把标准流交给 `PlayToEnd`。`apps/include` 仅 PRIVATE 给 `app` 目标。
- **读者面工程叙事硬禁令**：上面的类型形式与命名决策只供 Agent 写代码使用，禁止把决策原样复述成读者正文的语言课。`content/**` 旁白只写契约的工程问题、消费方与验证方式。跨仓外链**默认零条**；仅小节末尾置可选深潜（「若要系统阅读…」），禁止「写法依据见 / 机制见 / 选型见 …」+ cpp-notes 的突兀依据句。点名反例句式（一律不进正文）：「取值封闭的集合用 `enum class`…」「数据组合用 `struct` 聚合…」「`inline` 让各翻译单元共享同一份定义…」「`CellPosition` 是纯数据聚合」「按 Google 风格用大驼峰」「命名遵守 Google C++ 风格指南：…」「用有符号整型承载…」「坐标字段为什么选定宽有符号整型…」「头文件里的常量统一写成 `inline constexpr`，写法依据见 cpp-notes…」。除 01 设计章外，工程 qmd 不为坐标选型链到「类型安全与数值边界」。工程改写对照见标识 `bg-chinese-style-cases-v1` 的知识文件，硬边界细则见 `writing-quarto` 技能 `references/zh/chapter-writing.md`「叙事范围」。
- `01-cli-game` 保持双人终端。`02-cpu-opponent` 的对手只产生 `Move` 并调用同一个 `Place`。AI 不得成为核心规则的前置依赖。
- **课堂类比禁令与 Plan 落盘约束**：正文与 agents 知识不写「数学课 / 平面直角坐标系」等跨学科课堂对照；坐标系只用程序事实（原点在左上角、`row` 向下增长、`col` 向右增长）与可观察行为表述，图注已交代原点与轴向的正文不复述。作者可在 Plan 里借类比构思，落盘到 qmd / agents 前必须改写成工程对象与可观察行为；自动执行见 `verify_content.py` 禁用模式（规则见 `writing-quarto` 技能 `references/zh/chapter-writing.md`「叙事范围」）。
- **书的单位称「章」与否定式预告禁令**：读者正文与 agents 知识指称书的单位一律用「章」（这一章、第 N 章、每章），停用「课」「课程」讲法（「语言课旁白」「课堂类比」等风格禁令标签除外）；正文不写「程序不提供 / 不实现 X」式否定式预告，即使当下为真也不写——后文补上该能力时句子失效，规则见标识 `bg-terminology-v1` 与 `bg-paragraph-list-style-v1` 的知识文件。自测问题必须能由本章正文回答，本章回顾须承接本章正文各节交出的结果（规则见标识 `bg-chapter-page-pattern-v1` 的知识文件）；起因是 01 章「程序不提供电脑对手」一句与后文人机章冲突，且回顾空泛、自测题目缺少正文依据的读者反馈。
- Python 过渡顺序为稳定 CLI、`subprocess`、版本化逐行 JSON、HTTP/Fetch；当前 Web 仅监听回环地址，限制请求体与坐标输入，实时需求明确后才评估 WebSocket。
- 游戏章节叙事按「八步流程 + STAR」故事线分配章内职责，依据见标识 `bg-engineering-storyline-v1` 的知识文件。

## 未来能力口径

人机、逐行 JSON、Python 回放和本地 Web 适配已有代码与对应测试；HTTP 适配仍不属于正式部署阶段，WebSocket、GUI 和共享游戏引擎仍不验收。共享库仍要至少两个游戏真实复用后才提取。GoogleTest 已在阶段中经 FetchContent 引入。阶段目录只在出现新的真实行为时新建。

## 其他棋类

四子棋、五子棋、黑白棋等未来游戏也遵循同一渐进式开发和验证原则，但本轮只负责井字棋 content，不提前创建其他棋类页面或实现。

## 外部依据

- C++ Core Guidelines：具体类型、纯函数倾向、RAII、窄接口和避免过早抽象。
- CMake `enable_testing`/`add_test`：顶层启用并注册可由 CTest 执行的测试。
- Python `subprocess`：退出码、stdout/stderr、超时和一次性/持续进程边界。
- MDN Fetch 与 WHATWG WebSocket：HTTP 状态检查、JSON 解析、连接生命周期和应用层消息协议。
- Berkeley CS188 Multi-Agent Search：Minimax 的 MAX/MIN、终局 utility、搜索深度和 alpha-beta。

## Agent 行为边界

Agent 读写边界的唯一出处是根 `AGENTS.md`「工作规则」（只读默认、写入触发、删除前读取、不动生成物），本文件不再复述。
