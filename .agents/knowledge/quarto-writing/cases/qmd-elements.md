---
kb_id: "bg-qmd-elements-cases-v1"
title: "Quarto 元素写法正反对照"
domain: "quarto-writing"
subdomain: "cases"
tags: [code-blocks, filename, captions, qmd-elements]
level_range: [0, 5]
dependencies: [bg-qmd-element-cases-v1]
created: "2026-09-29"
updated: "2026-09-30"
chunk_strategy: "semantic_heading"
estimated_tokens: 850
---

# Quarto 元素写法正反对照

元素细则（filename 标注、闭环、盒子密度、Callout）见标识 `bg-qmd-element-cases-v1` 的知识文件；本文件保存元素写法的正反对照，检索单元是「正确 + 不佳 + 改写」。

## 代码块导语元计数对照

```text
不佳（元计数开场，读者要回数一遍才知道是哪三段）：
可执行目标由三段命令定义：输出目录、源文件清单和语言标准：

改写（职责顺序点名对象）：
下面这段规则定义可执行目标 app：先规定产物目录，再列出源文件，最后声明 C++20。
```

判定信号：导语里出现「N 段 / 三条命令定义」，用计数代替职责。

## 代码与图桥接对照

````text
不佳（代码块紧贴坐标图，中间零正文，读者不知道图核对什么）：
```{.cpp filename="board.h"}
constexpr bool IsValidPosition(CellPosition position) { … }
```

```{python}
#| fig-cap: "图 1：…"
```

改写（块前引语只讲一个对象，桥接句核对已讲清的关系，图后补图外结论）：
落子前的坐标检查都经过同一个入口，`IsValidPosition` 只依赖入参判定边界：

```{.cpp filename="board.h"}
constexpr bool IsValidPosition(CellPosition position) { … }
```

桥接句：下面的图标出每个棋盘格子的 (row, col)，与 `IsValidPosition` 接受的范围一致。

```{python}
#| fig-cap: "图 1：…"
```

图后：图外坐标一律拒绝。
````

判定信号：两个围栏之间只有空行；图后直接进入与图无关的下一块；块前引语同时推进多个对象（如 `CellPosition` 与 `IsValidPosition` 各讲一句）。

## 图后一句一中心对照

````text
不佳（图后句堆两个分句，既复述图注的空盘，又讲状态类型）：
对局开始时棋盘还没有任何棋子，下面的图展示这个初始局面。

```{python}
#| fig-cap: "图 2：初始棋盘，九个棋盘格子都为空。"
```

CLI 打印的三行 . . . 对应图中空棋盘格子，每个棋盘格子都是 CellState::kEmpty。

改写（图注已写明九格皆空，图后只留一句图外结论）：
对局开始时棋盘还没有任何棋子，下面的图展示这个初始局面。

```{python}
#| fig-cap: "图 2：初始棋盘，九个棋盘格子都为空。"
```

终端程序打印的三行 . . . 对应图中每个棋盘格子的 CellState::kEmpty。
````

判定信号：图后句删掉任一分句中心仍成立；图注或桥接句已写明的信息在图后再讲一遍。图后正文只给图注讲不完的新结论，图后对照与句段侧的冒号分号堆叠见标识 `bg-chinese-style-cases-v1` 的知识文件「冒号后堆叠分号解释」。

## 块后解释先于图对照

同一小节既有代码块项目解释又有图时，解释紧跟代码块，桥接句与图在后；图后不再回头讲代码项。

````text
不佳（代码 → 图 → 再解释代码项，解释插队）：
```{.cpp filename="board.h"}
struct Move { … };
```

桥接句：下面的图展示落子目标框。

```{python}
#| fig-cap: "图 1：…"
```

- Move：目标棋盘格子坐标与对局玩家组成的动作。（图后回头讲代码项）

改写（代码 → 块后解释 → 桥接 → 图 → 图后）：
```{.cpp filename="board.h"}
struct Move { … };
```

- Move：目标棋盘格子坐标与对局玩家组成的动作。

下面的图展示一局进行到中途的局面。

```{python}
#| fig-cap: "图 1：…"
```

图中加粗描边的格子是下一步落子目标。
````

判定信号：代码项的解释出现在图之后；或图后正文复述代码注释。固定序列见 `writing-quarto` 技能 `references/quarto/authoring.md`「代码与图的桥接」。

## 递进片段拆围栏对照

递进依赖链的判定与豁免见标识 `bg-qmd-element-cases-v1` 的知识文件「内容块前后的闭环」；句段对照见标识 `bg-chinese-style-cases-v1` 的知识文件「递进片段合并」。

````text
不佳（同一组递进定义拆成三个同源围栏，各配半句导语，首句点名了后块符号）：
棋盘固定为 3 行 3 列；…调规模只改这一处：
```{.cpp filename="board.h"}
inline constexpr int kRows = 3;
inline constexpr int kCols = 3;
```

CellPosition 携带从 0 起算的行列坐标，越界由 IsValidPosition 判为非法：
```{.cpp filename="board.h"}
struct CellPosition { … }
```

提交动作前的坐标检查都经过同一个入口：
```{.cpp filename="board.h"}
constexpr bool IsValidPosition(CellPosition position) { … }
```

改写（合并为一个围栏，块前一句交代整链，块后列表分项）：
board.h 定义棋盘尺寸、格子坐标与越界检查这三个对象，终端程序打印棋盘和测试遍历棋盘格子都读它们：

```{.cpp filename="board.h"}
（kRows/kCols → CellPosition → IsValidPosition 按源码相对顺序摘录为一个围栏）
```

- kRows / kCols：调整棋盘规模只改这一处；
- CellPosition：各层传递格子坐标共用这一类型；
- IsValidPosition：提交动作前的坐标检查都经过这个入口。
````

判定信号：同一小节内同源围栏 ≥2、后块使用前块已展示的符号、中间没有 `{python}` / `{mermaid}` 或独立验证盒子打断。

## 正确形态正例

```markdown
::: {.callout-note title="术语：冒烟测试（smoke test）"}
业界对“程序能启动且基本行为正确”这类最基础检查的叫法。本章的通过条件是
退出码 0 与输出断言同时满足。
:::
```

```text
正确（片段 + 短 filename + 闭环正文）：
块前：下面这段规则定义可执行目标 app，产物落在 build/bin。
块内：```{.cpp filename="CMakeLists.txt"} …
块后：add_test() 把它注册成冒烟测试，看到 PASS 即为通过。
```

正例的判定条件：filename 是短显示名；块前导语讲工程语境，块后解释讲看到什么算成功；注释只在片段内、每处不超过 2 行。
