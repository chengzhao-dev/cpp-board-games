# 审查清单（代码与文档）

## C++ 代码审查准则

### 审查重点

重点审查 C++20 现代特性运用、资源管理、未定义行为与阶段工程约定：

- **标识符命名（Google 主标准）**：类型与函数 PascalCase、变量与参数 snake_case、常量与枚举子 `k` 前缀、成员尾下划线；访问器统一 PascalCase，同一 API 不混两套函数命名。偏离仅限 `bg-google-cpp-style-v1` 白名单（`#pragma once`、`.cpp`/`.h`、C++20、异常边界、LLVM 横幅、不强制 cpplint）。
- **头文件**：自包含；头文件内不写 `using namespace`；include 分组与排序由 `clang-format` 维护；头文件内函数定义仅限模板与简单函数；项目头用裸文件名引号 include（`"game.h"`），禁止 `include/<namespace>/` 与 `"tictactoe/….h"`。
- **命名空间头文件顺序**：includes → `namespace` → `inline constexpr` 常量 → `enum class` → `struct`（被依赖者在前）→ 自由函数；类内按 public → protected → private，段内类型 → 静态常量 → 工厂 → 构造/赋值/析构 → 函数 → 数据；`.cpp` 定义顺序与头一致。标准见 `bg-declaration-order-v1`。
- **类与转换**：单参构造 `explicit`，零参不加；`=default` 与有体定义出类写在 `.cpp`；平凡析构不声明；`struct` 数据聚合、`class` 不变量加行为；禁止 C 风格转换；声明顺序类型 → 常量 → 工厂 → 构造/析构 → 方法 → 数据。
- **可读性括号与枚举行尾**：混合优先级算术给高优先级子表达式显式括号（`readability-math-missing-parentheses` 保留不关闭）；同一 `enum` 内不自明成员的行尾注释必须齐全，禁止半套，且语义结果优先（先写「平局」等结果词）；`readability-*` 先改代码消诊断，禁止用 NOLINT 掩盖（规则见 `bg-google-cpp-style-v1` 与 `bg-comment-style-v1`）。
- **领域注释结果向**：换算写「由 A 得到 B」，读取写「返回…」并写明失败边界；禁映射/翻译/棋子（指 `CellState`）、禁「查询…必须合法」空话（规则见 `bg-comment-style-v1`「领域函数与成员注释」）。
- **资源与生命周期**：严格遵守 RAII 原则。严禁裸 `new`/`delete`。检查指针与引用离开作用域时是否悬挂，移动后对象是否仍被访问；堆所有权用 `unique_ptr`。
- **现代特性与传参**：优先使用 `auto`、结构化绑定和基于范围的 for 循环，大对象参数使用 `const T&` 或值传递并移动，避免无意的隐式深拷贝。值类型与强类型按 `game-design` 的建模依据核对。
- **异常边界**：规则核心与可测试 API 用结果类型表达业务结果，不用异常；契约违反可抛 `std::out_of_range`（英文 `what()` 句式见 `bg-exception-message-format-v1`）；CLI 与工具边界允许异常。不引入日志框架。
- **apps 布局**：组件式阶段 `apps/` 为私有 `include/` + `src/`（全部 `.cpp` 含 `main` 在 `src/`）；`apps/include` 仅 PRIVATE，展示不进规则库。
- **游戏核心边界**：游戏核心不得依赖终端、GUI、Web、Python 或 Quarto；终端适配层与规则核心的职责划分是否被破坏。
- **构建与测试**：组件式布局（`<component>/include|src/`、`apps/`、`tests/`）与 CMake 约定是否一致；target 是否用 `target_*` 命令表达依赖；测试是否注册进 CTest；`.clang-format` 与 `.clang-tidy` 是否沿用阶段配置。
- **注释与输出**：注释为简洁中文、专有名词保留英文，LLVM 横幅分段；注释写意图与取舍、不复述代码；未完成实现必须有可检索的 `TODO:`（见 `bg-comment-style-v1`）；终端输出遵循 `bg-terminal-output-style-v1` 的口径。
- **工具配置 YAML**：`.clang-format` / `.clang-tidy` / `.clangd` 禁止文件顶部长篇政策块、知识库 id 指针与「两仓/复制本文件」模板元叙述；短横幅 + 邻接/单行分组，见 `bg-comment-style-v1`「工具配置 YAML」。

### 缺陷判定原则

- 只有存在具体调用场景、能够证明发生未定义行为或内存泄漏时，才评定为 P0/P1。
- 能通过编译器警告、CTest 或 `run.py build <game>/<stage>` 拦截的问题，应直接指出违规点并引用对应规则。

## Quarto 文档与排版审查准则

### 审查重点

审查 .qmd 章节正文、中文表达与 Quarto 特有语法规范：

- **DOM 与布局契约**：检查代码块是否符合仓库风格。Mermaid 图表是否严格使用 ```` ```{mermaid} ```` 围栏，而不是普通的 ```` ```mermaid ```` 代码块。普通终端演示是否使用 `text` 代码块。
- **中文写作与体例**：章节是否按六段骨架（引言 → 任务序列 → 常见错误 → 自测 → 回顾）推进，是否在标题后第一句直接兑现承诺，正文反引号是否仅包裹真实技术对象；语气与禁用词以 `verify_content.py` 词表为准；禁止「接口清单压缩段」（把私有成员、公开成员名单、`const`、`[[nodiscard]]` 等压进同一段旁白），定稿形态见 `bg-chinese-style-cases-v1`。
- **片段一致性**：qmd 中的代码摘录是否与 `games/**` 源文件逐字一致（`verify_content.py` 的片段校验覆盖，审查时关注上下文衔接）。
- **删改连续性**：局部删除或移动内容后，是否按 `writing-quarto` 的 `authoring` reference 回读切口，动作、因果、指代和验收没有因过渡句消失而断裂。
- **正文与 Callout 密度**：相邻正文与尾置 Callout 的信息密度、列表结构和视觉重量是否协调；术语卡就近放置且不替代主流程。规则以 `writing-quarto` 的 `section-focus-and-density` reference 为准。
- **结构与链接**：跨章交叉引用使用中文标题锚点或 GitHub 链接，仓库路径锚文本用中文短描述；图片与本地文件引用是否存在，小节标题层级是否跳跃。
- **Callout 规范**：是否仅使用内置的 `note`、`tip`、`warning`、`important`、`caution` 五类，严禁自定义类。
- **可折叠答案**：自测题答案是否使用 `.answer` 组件、紧跟对应列表项、默认收起，且没有把新概念或标题藏进折叠区。列表型答案是否先用导语交代对象、起止范围或顺序。

### 缺陷判定原则

- 导致渲染失败或死链的问题归为 P1。
- 破坏中文排版节奏、正文与代码块事实不一致归为 P2。
