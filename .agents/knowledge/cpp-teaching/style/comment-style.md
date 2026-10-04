---
kb_id: "bg-comment-style-v1"
title: "统一注释风格规范"
domain: "cpp-teaching"
subdomain: "style"
tags: [comment, llvm, google-style, chinese]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-10-04"
chunk_strategy: "semantic_heading"
estimated_tokens: 3000
---

# 统一注释风格规范

本文件是全仓库生成和评审注释的唯一基准，覆盖 C++、Bash、CMake、YAML（`.clang-format`、`.clang-tidy`、`.clangd`）、JSONC（`.vscode/*.json`）和未来的 Python。Agent 生成任何代码或配置注释时必须遵循本规范。2026-09 依据 LLVM、Google C++、Google Shell、Linux 内核、PEP 8/257 等公开标准联网核实后沉淀，来源见文末。

## 分段基准与内容原则

- **分段形式**以 LLVM 为基准：文件头和段落用定宽 `===` 横幅分隔。
- **注释内容**以 Google 为基准：解释意图与取舍，不逐行复述代码；"不要事事注释"，只注释不显而易见的部分。
- **注释不承载规范说理**：命名惯例、官方建议（如「CMake 官方不建议 file(GLOB)」）、未来演化指引（如「将来改成 PUBLIC」）、外部规范引用（clig.dev、Google Shell）一律不写进代码注释；面向读者的说理进 Quarto 对应章节的 callout，面向作者的论证进 `.agents/knowledge/`。注释只回答「这段代码做什么、有什么关键约束」。
- Linux 内核的 `/*\n * ...\n */` 盒式注释仅适用于 C，本项目不采用；OpenAI 无公开注释风格指南，不作为依据。

## 语言注释符

| 文件类型 | 注释符 |
| --- | --- |
| C++（.cpp/.hpp） | `//`，不使用 `/* */` 盒式注释 |
| Bash（.sh） | `#` |
| CMake（CMakeLists.txt） | `#` |
| YAML（`.clang-format`、`.clang-tidy`、`.clangd`） | `#` |
| JSONC（.vscode/*.json） | `//` |
| 严格 JSON（compile_commands.json 等） | 禁止任何注释 |
| Python（未来阶段） | docstring（`"""`）+ `#` |

## 注释层级与职责

注释按读者需要的信息分三层加一类函数契约，不用同一段文字同时承担文件说明、代码分组和规范论证：

| 层 | 写什么 | 不写什么 |
| --- | --- | --- |
| 文件头横幅 | 文件是什么 + 读者可直接理解的用途（1–3 行） | 版权、作者、日期；「探针」「阶段」「领域值类型」「存储抽象」等读者黑话；规范说理 |
| 职责段横幅 `#===...===#` | 只标大职责块名（如「1. 配置」「可执行目标」「测试」） | 意图、参数含义、失败处理、论证 |
| 普通邻接注释 | 紧随其后的代码的关键约束或失败后动作，≤2 行；多标志命令必须写明这些标志改变了什么 | 复述命令字面；「为什么不用某写法」的长论证；颜色/TTY 展示细节；只说「重新配置」却不点名生成器、编译器或编译数据库 |
| 函数注释（Bash 等） | 1–2 行关键约束：结果写到哪一路、失败后做什么 | `Arguments:` / `Outputs:` / `Returns:` 清单；把函数体里已经看得见的 `printf` 再写一遍 |

短文件（约 ≤20 行）只写文件头，不加段横幅。段横幅只划分工程声明、目标、测试或脚本步骤等大职责块。

多标志命令的注释要短，但必须能核对。`cmake` 配置行上方写明生成器、编译器、构建类型和 `compile_commands.json`，并写明每次都重新配置，避免这些开关留在旧缓存里。换编译器时删除 `build/` 的完整排查步骤写入 Quarto 或本知识文件，不在脚本旁展开。

禁止错配：几行就能读完的辅助函数配上 `Arguments:` / `Outputs:`，而真正决定构建结果的命令只留「使脚本里的参数进入当前构建计划」这种空话。函数体已经写出 `printf` 的去向时，不再单列参数和输出清单。正反对照见 `cpp-teaching/cases/comments.md`（标识 `bg-comment-cases-v1`）。

## 邻接单行注释：一注一句

并列语句需要注释时，一句注释只标紧随的一条语句，注释与代码之间不空行；不是每行必注，没有独立意图的语句不加：

- 正确：每条语句正上方一行意图注释（如产物目录的三条 `set` 各配一行）。
- 错误：一行注释覆盖后面多条兄弟 `set`/命令——读者对不上哪句由哪条注释负责。
- 注释与命令错位同样不行：注释写「链接规则库」却放在 `add_executable` 上方，链接命令反而无注释，是「一注多句」的变体。
- 不改范围：文件头与 `#===` 段横幅、枚举行尾注释、单命令 ≤2 行折行注释不受本条约束；语义上不可拆的单个操作（如 `FetchContent_Declare` + `FetchContent_MakeAvailable` 成对完成一次拉取）可共用一行注释。

源码与 Quarto 摘录同源同规：摘录片段逐字取自源文件，源文件改成「一注一句」后摘录自然继承。正反对照见标识 `bg-comment-cases-v1` 的知识文件「一注多句对照」。

## 枚举与常量行尾注释

- 类型意图写在 enum 定义上一行（如 `/// 棋盘格子的状态。`，声明注释的 Doxygen 标记见「多行注释」）；成员行尾注释只在成员名不能让初学者直接对应领域语义时才写，避免把同一信息重复多遍。
- 需要行尾注释的成员用 Doxygen 行尾形式加简洁词（如 `kEmpty = 0,   ///< 空格。`；行尾成员文档在标记后加 `<`，见 [Doxygen 手册](https://doxygen.nl/manual/docblocks.html)，LLVM [GlobalValue.h](https://github.com/llvm/llvm-project/blob/main/llvm/include/llvm/IR/GlobalValue.h) 与 [OpenCV utility.hpp](https://github.com/opencv/opencv/blob/4.x/modules/core/include/opencv2/core/utility.hpp) 的枚举均逐行行尾标注）；类型上一行已含「棋盘格子」锚点时，成员行尾不写「空棋盘格子」。多条行尾注释时 `///<` 列对齐，且整行不超 `ColumnLimit: 80`（对齐由 Google `BasedOnStyle` 的 `AlignTrailingComments` 承担）。
- **语义结果优先**：不自明成员的行尾须先写出读者不识英文名也能懂的结果词（如 `平局`、`进行中`、`先手 X 获胜`），判定条件可选跟在全角冒号后（如 `///< 平局：棋盘下满且无人三连。`）。禁止只写条件、不写结果（读者从 `kDraw` 的「棋盘下满且无人三连」对不上「平局」）。
- 同一 `enum` 内要么全部成员都有行尾注释、要么全部没有，禁止半套：部分成员有、部分没有会让读者怀疑漏写。`CellState` 定案**全量**行尾注释（用户定案：`kCross`/`kNought` 需翻译为 X/O 棋子，且与 `Player` 的同名成员异义）；全自明的枚举（如 `Player` 的成员由类型注释「对局玩家」承担语义）则一条都不写。
- 井字棋领域注释保留现实锚点：单格写「棋盘格子」，`CellPosition` 写「棋盘格子坐标」，`CellState` 类型注释写「棋盘格子的状态」，`Player` 写「对局玩家」。`CellPosition` 注释只写坐标含义，不写「用有符号整型承载」等选型旁白；选型旁白禁令的完整表述见下文「类型选型与组织自述不进注释」。
- 正反对照见标识 `bg-comment-cases-v1` 的知识文件「枚举行尾注释对照」。

## 类型选型与组织自述不进注释

注释只写读者理解对局语义所需要的信息（Google 的「Optimize for the reader, not the writer」原则：读代码的时间多于写代码的时间）。两类内容默认不进注释：

- **类型选型旁白**：宽度、拓宽、承载与转换细节（如「同为 int32，乘积不再拓宽」「只在结果上转成 size_t」）不写——类型在代码里已经可见，初学者读的是对局语义。整型乘加的做法本身仍按标识 `bg-google-cpp-style-v1` 的知识文件「整型与枚举底层类型」与标识 `bg-comment-cases-v1` 的知识文件「整型转换注释」执行：理由记录在知识文件，注释不复述。仅当该处代码的主题就是类型或性能承载（NEON/SIMD、宽化窄化、位布局）时，类型说明才是正文语义，可以写。
- **写给作者的组织自述**：「全仓只在这里定义一次」类说明回答「维护者应在哪里定义」，不回答「读者应如何理解这行代码」，不进注释；单一出处等工程约束放知识文件或 Quarto 正文。

两类禁令都不影响契约注释：前置条件、异常与失败后动作（如「调用方应先用 IsValid 排除越界；非法坐标抛 std::out_of_range」）是读者正确使用 API 的必要信息，照常保留。正反对照见标识 `bg-comment-cases-v1` 的知识文件「类型选型旁白对照」。

## 领域函数与成员注释

领域 API 注释写**结果与约束**，不写抽象动作词。概述与能力行不用压缩式黑话（「向空格落子」「查询满盘」），用与函数名对应的平实说法（「放置棋子」「检查棋盘是否已满」——用户定案）。函数概述一律以动词开头，且动词与函数名前缀对应：`Get` 用「获取」（不用「返回」）、`Is` 用「检查」、`Place` 用「放置」、`To` 用「将…转换为…」（用户定案；联网复核：C++/Doxygen 系主流用第三人称陈述动词开头，Python 系用祈使句，本仓取动词陈述句式；反面例：`棋盘是否已无空格。` 是名词短语，改写为动词陈述句）。句式表：

| 场景 | 句式 | 禁止 |
| --- | --- | --- |
| 常量与类型声明（`kRows`、`CellState`、`CellPosition`、`Board`） | **`///` 单行概述**；类与需补充说明的类型（如 `CellPosition`）用「概述 + 空 `///` + 细节」 | 用 `//` 写头文件声明注释；行尾标注漏 `<` |
| 构造函数 | **「构造函数：」开头**（如 `/// 构造函数：创建一个所有格子均为空的棋盘。`，用户定案） | 只写动作不标角色（读者扫注释时对不上这是构造） |
| 类型/领域换算（`CellStateFor`、`Board::ToFlatIndex`） | **由 A 得到 B**（`CellStateFor`）；`To` 前缀用**将 A 转换为 B**（`ToFlatIndex`）；需要时括号给一对例子 | 映射、翻译、棋子（指 `CellState`）、以排布术语当结果（「行优先下标」）、空话「作个…」 |
| 读取（`GetCellState`、`Game::GetResult`） | **概述行：获取什么**（`Get` 前缀一律「获取」，不用「返回」）；失败边界写 `@throw`（如 `/// @throw std::out_of_range 坐标不在棋盘范围内。`），返回值用 `@return` | 只写「查询」不写获取结果；`Get` 概述用「返回」；裸英文参数名当主语；「必须合法」不点名 `IsValid` |
| 展示层转换（`CellSymbol` 等） | **转成…（展示用途）** 可保留「转成」 | 与领域换算混用「映射」 |

正反对照见标识 `bg-comment-cases-v1` 的知识文件「领域函数注释对照」。文件头与类上一行同样结果向：写「可读各格状态」等能力，不写含糊的「查询棋盘格子」。指 `CellState` 时用术语「棋盘格子状态」，不用「棋子」。

存储成员注释**本体先行**：先写成员装的是什么（如 `// 棋盘格子的存储数组，按行依次存放。`），再补排布；不用「按行优先保存棋盘格子」这类以排布开头的句子——读者先要知道成员是什么，才轮到它怎么排。

## 实现注释

`.cpp` 实现注释服务于「隔期回看能快速接上」，密度按用户定案高于 [Google Function Comments](https://google.github.io/styleguide/cppguide.html#Function_Comments) 的基线（"definition comments describe function operation"）：

- 每个非平凡函数定义上方一行 `//` 操作注释，写实现要点（如 ToFlatIndex 的「先跳过前面的整行，再加上列偏移，得到一维索引。」）；不逐字镜像声明处的契约句；平凡访问器（直接返回成员的委托）不加。
- 函数体内关键分支与步骤用行尾或上方 `//` 注释：失败分支写拒绝原因（如 PlacePiece 的 `return false;  // 目标格子已被占用，拒绝覆盖。`），关键写入点与防御性写法各一句（如「`.at()` 保留作第二道越界防线」）。
- 守卫/前置校验与主逻辑之间空一行分组（见标识 `bg-google-cpp-style-v1` 的知识文件「实现文件分组与垂直空白」）。
- 不复制 `@param` / `@return` / `@throw` 标签到 `.cpp`；声明契约改动时同步核对定义处注释。正反对照见标识 `bg-comment-cases-v1` 的知识文件「实现注释对照」。

## 文件头

每个源码文件的注释开头必须有一段用途块，让读者不读代码就知道文件是什么。不写版权、作者、日期（教学仓库）。结构：

1. 定宽横幅行；
2. 标题行：`文件名 - 一句话用途`；
3. 空注释行 + 1–3 行补充说明（短文件可省略）；
4. 收尾定宽横幅行；
5. 空 1 行后开始内容。

横幅模板（一律 80 列、纯 ASCII）：

- C++ / JSONC：`//===----------------------------------------------------------------------===//`（`//===` + 70 个 `-` + `===//`）
- sh / CMake / YAML：`#===------------------------------------------------------------------------===#`（`#===` + 72 个 `-` + `===#`）

规则：

- 横幅**单独成行、定宽 80 列、纯 ASCII**，标题不嵌在横幅行内——避免中日韩字符宽度不同导致的对齐破坏。
- Bash 的 shebang 永远是第一行，横幅从第二行开始。
- 短文件（约 ≤20 行）只写文件头，不加段横幅。
- Bash 长脚本在文件头横幅之后、可执行内容之前设「严格模式与工作目录」独立段横幅，收纳 `set` 与 `cd`/路径常量；`set`、`cd` 不散落在文件头与函数区之间。

## Bash 脚本次序

较长 Bash 脚本按 Google Shell Style Guide 组织次序：`set`（严格模式）→ `readonly` 常量 → 全部函数聚在一起 → `main` 定义 → 文件末行 `main "$@"`。函数之间不夹可执行代码；有多个函数时必须有 `main`。步骤「1. 配置」等运行期输出由 `main` 内的 `header` 调用承担，不再各自占段横幅。

## 段落分隔

文件较长（约 >20 行）且含多个职责块时，用段横幅分隔：

```text
<空 1 行>
<横幅行>
<标题行>
<横幅行>
<空 1 行>
<段落内容>
```

- 段标题一行写完，不嵌横幅；两段之间恰好一组横幅。
- 段落内的子分组不需要横幅，用普通单行注释即可。

## 单行注释

- C++ 用 `//`、Bash 用 `#`，注释符后空一格：`// 说明`、`# 说明`。
- 写意图和关键约束，不复述代码（"做什么"由代码自答）；规范说理按「注释不承载规范说理」外移，不进注释。
- 完整句子；遵守 80 列（与 `.clang-format` 的 `ColumnLimit: 80` 一致）；超长时折为多行连续注释，后续行与首行注释内容对齐或紧随注释符。

## 多行注释

- 一律写成**连续的单行注释行**，不用 `/* */` 或盒式框线。
- 库对外头文件里的**声明注释**一律用 `///` Doxygen：常量、枚举、结构体、类与函数契约同一层（用户定案：先函数契约迁移，同日扩到类型与常量声明；LLVM [StringRef.h](https://github.com/llvm/llvm-project/blob/main/llvm/include/llvm/ADT/StringRef.h)、[GlobalValue.h](https://github.com/llvm/llvm-project/blob/main/llvm/include/llvm/IR/GlobalValue.h) 与 [OpenCV utility.hpp](https://github.com/opencv/opencv/blob/4.x/modules/core/include/opencv2/core/utility.hpp) 的公开声明均用 Doxygen 注释）；枚举值与字段的行尾标注用 `///<`（见「枚举与常量行尾注释」），类等需要补充说明的声明写「概述行 + 空 `///` + 细节」；文件级说明用横幅头；`///` 不用于实现注释（调研结论：[LLVM 编码标准](https://llvm.org/docs/CodingStandards.html)以 `///` 作 Doxygen 标记、`\param` 与 `@param` 等价、取一种保持一致即可，RIOT 等项目同样约定 `///` 为 Doxygen、`//` 为普通注释；Google C++ Style Guide 全文不出现 Doxygen，本条不是对齐 Google 的结果）。展开规则：
  - 参数、返回值或异常带函数名与类型签名**之外**的约束（前置条件、失败行为、异常、取值限制）时，概述后空一行 `///`，再逐项 `@param`、`@return`、`@throw`（如 `Board::GetCellState`、`Board::PlacePiece`、`Game::Place`）。
  - 无额外约束的简单函数只留单行 `///` 概述（如 `Board::IsFull`、`Game::CurrentPlayer`），禁止用 @ 标签复述函数名与类型签名。
  - 失败行为等约束写在概述与 @ 标签之间的正文段（如 `PlacePiece` 的「坐标无效、要写入的是空格或目标格子已有棋子时放置失败，棋盘保持不变。」），不塞进单条 `@return`。
- Bash 函数不使用 `Arguments:` / `Outputs:` / `Returns:` 清单。不直观时用 1–2 行中文写出关键约束；参数含义从名字和函数体看不出来时，写进同一段话，不另起清单。

## TODO

未完成或临时够用的实现必须用 TODO 标注，禁止只写「见后续章」一类普通注释——后者无法用检索保证不遗漏。

格式（与 [Google TODO Comments](https://google.github.io/styleguide/cppguide.html#TODO_Comments) 及现行 `google-readability-todo` 一致）：

1. **推荐（Hyphen）**：`// TODO: <参考> - <要做什么>`
2. **仍接受（Parentheses）**：`// TODO(<参考>): <要做什么>`

`<参考>` 优先 issue / bug（如 `b/12345`、GitHub issue URL）；本仓教学阶段尚无 issue 时，用**将落地的阶段目录名或章节 slug**（如 `01-cli-game`），不要只写人名。描述写清「现在缺什么、完成后应变成什么」。sh / YAML / CMake 用 `# TODO: ...`。

```cpp
// TODO: 01-cli-game - Detect win/draw from cells_;
// currently always returns kInProgress.
GameResult Game::GetResult() const {
  static_cast<void>(cells_);
  return GameResult::kInProgress;
}
```

TODO 表示临时方案；补全实现后删除该 TODO。可用 `rg TODO` / IDE TODO 视图做收口检查。

## Python（未来阶段）

- 模块、类、公共函数必须用 PEP 257 docstring：单行 docstring 用 `"""一句话"""`；多行时首行为摘要、空 1 行、再写详情，收尾 `"""` 独占一行。
- 块注释每行 `#` 前缀并与代码同级缩进；行内 `#` 注释与代码至少隔两个空格。
- 公共接口文档用 docstring，不用 `#` 注释。

## 空行总则

- 文件头横幅块之后空 1 行。
- 段横幅块之前空 1 行、之后空 1 行。
- 普通注释与被注释的代码之间不空行；逻辑上独立的代码块之间空 1 行。

## 注释语言与内容风格

- **语言跟随读者**：OpenHarmony 面向国际社区选择英文注释，说明注释语言取决于目标读者；本仓库的目标读者是中文初学者，注释正文一律使用**简洁、明了、新人易懂的中文**。
- **专业名词保留英文**：工具名（CMake、Ninja、Clang、clangd、CTest、g++、VS Code、GitHub Actions）、命令与关键字（`target_compile_features`、`PRIVATE`）和无通行中文译名的技术术语（target、stdout/stderr、TTY 等）直接写英文原文；有通行中文说法的普通词用中文，不刻意夹杂英文。
- **中文语法与标点**：
 - 完整句子要有主谓结构，一句话说一件事，避免多重复句堆叠和翻译腔。
 - 中文句子用全角标点（，。：""）；普通邻接注释默认使用简洁完整句，并以句号结尾；仅枚举行尾的单词式说明可省略句号。
 - 中文与英文单词、数字之间加一个半角空格（如"使用 CMake 配置"），便于阅读和检索。
- **内容取舍**（Google、Linux 内核、OpenHarmony 共识）：讲 WHAT 和 WHY，不讲 HOW；不重复代码能自表达的信息；从读者的角度按需注释，不写空有格式的注释；改代码时同步维护注释；不用的代码段直接删除，不注释掉。

## 工具配置 YAML

三文件（`.clang-format`、`.clang-tidy`、`.clangd`）与源码/CMake/sh 共用文件头横幅模板，但**不用段横幅**；分组只用单行 `#`，或对非自明键做邻接注释。正反对照见标识 `bg-comment-cases-v1` 的知识文件「配置 YAML 正反对照」。

### 禁止形态

- 文件顶部长篇政策块（Google 主标准、偏离白名单、`at()` 全局策略、知识库 id 指针）折成多行 `#`。
- 注释内出现 `bg-*` / `cpp-*` / `.agents/`，或「见知识库…」。
- 阶段副本残留模板元叙述（「两仓统一基准源」「把本文件复制…」「与 cpp-notes 保持一致」）。
- 一段注释同时覆盖多条 `Checks` 关闭项或多组 `CheckOptions`（违反「一注一句」）。

### 文件头

LLVM 定宽横幅 + 标题行「文件名 - 一句话用途」+ 收尾横幅；标题下**不再**跟补充政策段。三文件一律要横幅（不因篇幅短而省略）。

### 邻接与分组

- 只标非自明项；紧贴被约束的键或 list item；`#` 后一空格；完整中文短句；专有名词保留英文；≤2 行。
- `.clang-format`：保留单行分组注释（基础风格、行宽、缩进等），禁止分组下再堆政策折行。
- `.clang-tidy`：`Checks` 用 YAML 列表，不用 `>` 折叠字符串。折叠字符串里的 `#` 会进入检查名。每个显式关闭项的说明紧贴该项上方，写清检查名和一句原因，可再折一行把原因说完。`CheckOptions` 里自明的 `CamelCase` / `lower_case` / `k` 前缀不写注释；仅对偏离直觉的项（如 `LocalConstantCase`）邻接注释。
- `.clangd`：`CompilationDatabase`、兜底 `Add`、`ClangTidy.Add`、`Suppress` 与阶段特有 `-I…` 各自邻接一句；阶段路径只写在该阶段副本，不写回通用模板。
- 不全局关闭 `cppcoreguidelines-pro-bounds-constant-array-index`；边界与 `at()` / 局部 `NOLINT` 见标识 `bg-static-analysis-boundaries-v1` 的知识文件。

### 与 CMake / sh 的异同

CMake 与长 Bash 用段横幅划分职责块；上述三配置文件无段横幅，只用文件头 + 单行分组/邻接。说理进 `.agents/knowledge/`，读者工程句进 Quarto，注释只答「这项约束什么」。

## 长注释与文档分层

Linux 内核明确警告"过度注释有危险"（"there is also a danger of over-commenting"），其长篇 API 与设计说明走独立的 kernel-doc 与 Documentation/ 文档体系，不堆在代码里。本仓库的对应分层结构：`.agents/knowledge/` 放完整论证与外部依据（Agent 按主题直接读取），Quarto content 放面向读者的讲解。

- **上限**：紧跟代码的说明注释不超过 **2 行**；文件头横幅和函数结构化头注释等已有格式规定的块不受此限。
- **超限处理**：精炼为 1–2 行结论；完整论证移入对应知识文件，注释不加指向知识库的指针。
- **文档分层**：代码旁注释只留结论和关键动作（如出错时 `rm -rf build`）；论证、方案对比和外部链接放 `.agents/knowledge/`；面向读者的讲解放 Quarto 对应章节。三处不得全文重复，注释只放结论。
- **内部路径禁令**：`games/**` 与 `content/**` 下的任何文件（代码、脚本、配置注释、qmd 正文）不得出现 `.agents/` 路径引用。games 源码会被 Quarto include 展示给读者，content 是读者文档，内部知识路径混入会混淆读者与作者视角；Agent 所需论证一律回本知识库按主题检索，不通过代码注释跳转。
- **精简手法**：一句话说一件事；"为什么不用某方案"的整段对比论证移入知识文件，注释不展开。

## 来源

- [LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html)——横幅分段、`\file` 文件级注释、`///` 文档注释与 `//` 普通注释之分。
- [Doxygen 手册](https://doxygen.nl/manual/docblocks.html)——`///`/`//!` 特殊注释与 `///<` 行尾成员文档语法。
- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)——文件头描述内容、`//` 优先、TODO 格式、注释写意图、注释语法不要求 Doxygen。
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)——文件头、函数结构化注释、"不要事事注释"。
- [Linux kernel coding style](https://docs.kernel.org/process/coding-style.html)——第 8 章"注释讲 WHAT 和 WHY、不放函数体内"，多行盒式注释仅作对比不采用。
- [OpenHarmony C++ 语言编程规范](https://gitee.com/openharmony/docs/blob/master/zh-cn/contribute/OpenHarmony-cpp-coding-style-guide.md)——注释"简洁、明了、无二义性"、从读者角度按需注释、注释与代码同步维护；其"注释语言跟随读者"的取舍是本仓库选中文注释的参照。
- [PEP 8](https://peps.python.org/pep-0008/)、[PEP 257](https://peps.python.org/pep-0257/)——Python 注释与 docstring。

程序运行时向终端打印内容（阶段标题、进度、错误、日志）的展示形式不属于注释范畴，另见 标识 `bg-terminal-output-style-v1` 的知识文件。
