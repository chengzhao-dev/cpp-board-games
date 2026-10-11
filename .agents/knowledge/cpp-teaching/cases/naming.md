---
kb_id: "bg-naming-cases-v1"
title: "标识符命名正反对照"
domain: "cpp-teaching"
subdomain: "cases"
tags: [naming, google-style, pascal-case]
level_range: [0, 5]
dependencies: [bg-google-cpp-style-v1]
created: "2026-09-29"
updated: "2026-10-08"
chunk_strategy: "semantic_heading"
estimated_tokens: 1750
---

# 标识符命名正反对照

命名规则与偏离白名单见标识 `bg-google-cpp-style-v1` 的知识文件；本文件保存正反对照，检索单元是「正确 + 不佳 + 改写」。

## 歧义映射命名对照

映射函数的名字必须让读者看出源端或目标端角色；单独的 `Of` / `To` 短后缀看不出两端是什么，禁止使用（依据 Google「descriptive；eschew abbreviation」）：

```text
不佳（MarkOf 看不出是「玩家 → 棋子」还是「棋盘 → 棋子」）：
CellState MarkOf(Player player);

改写（名字同时含源端与目标端角色）：
CellState PlayerToCellState(Player player);
```

```text
不佳（To 悬空，目标类型只能去签名里找）：
std::string To(const Board& board);

改写（目标端进名字）：
std::string BoardToString(const Board& board);
```

## 语义角色对照

函数名的语义角色决定前缀形态，角色表见标识 `bg-google-cpp-style-v1` 的知识文件「函数语义角色表」：

```text
不佳（谓词用名词直写或 Check 前缀，返回 bool 这一点要读者猜）：
bool Full() const;
bool CheckFull() const;

改写（谓词统一 Is 前缀）：
bool IsFull() const noexcept;
```

```text
不佳（整局受理与底层格子写入同名 Place，分不清哪一层可被拒绝）：
PlaceResult Place(const Move& move);

改写（整局受理取 Try 前缀，底层写入保留领域动词 PlacePiece）：
PlaceResult TryPlace(const Move& move);
```

```text
不佳（StatusToString 只写「状态 → 字符串」，与枚举名 GameResult 术语不一致，
读者要回看签名才知道源端是什么）：
std::string StatusToString(GameResult result);

改写（源端类型进名字，与枚举名对齐）：
std::string GameResultToString(GameResult result);
```

```text
不佳（查询访问器与数据成员同名 Result()，分不清是读缓存还是重算判定）：
GameResult Result() const;

改写（读缓存用 Get 前缀，重算判定保留 ResultAfterMove）：
GameResult GetResult() const;
```

## 枚举子访问对照

`enum class` 枚举子用作用域 `::` 访问，不用点号；点号把类型名当对象用，clangd 报 `'CellState' does not refer to a value`，指向枚举声明行但不指问题本身：

```text
不佳（CellState.kEmpty 把枚举类型当值，编译错误）：
cells_.fill(CellState.kEmpty);

改写（枚举子用作用域解析符访问）：
cells_.fill(CellState::kEmpty);
```

## 正确形态正例

```cpp
// 谓词：PascalCase，返回 bool，一眼可读。
static bool IsValidPosition(CellPosition position) noexcept;

// 读取：Get 前缀标明只读访问。
[[nodiscard]] CellState GetCellState(CellPosition position) const;

// 映射：源端与目标端都在名字里。
CellState PlayerToCellState(Player player);

// 动作：Try 前缀尝试受理，结果类型表达失败而非异常。
PlaceResult TryPlace(const Move& move);
```

正例的判定条件：谓词 `Is/Are/Has` 开头；读取一律 `Get` 前缀（`GetCellState`，与返回类型对齐；`GetCurrentPlayer`、`GetHistory` 为用户定案）；放置棋子的底层写入直接用领域动词（`PlacePiece`），整局受理取 `Try` 前缀（`Game::TryPlace`，用户定案）；下标换算用 `To` 前缀（`ToFlatIndex`）；映射函数含源端与目标端角色（`PlayerToCellState`）；动作函数动词开头；类型 PascalCase、变量 snake_case、常量与枚举子 `k` 前缀。

## 领域形参角色对照

同一领域角色跨函数取同一个名字，固定表见标识 `bg-google-cpp-style-v1` 的知识文件「领域形参角色表」；检索单元是「正确 + 不佳 + 改写」。

```text
不佳（cell 同时指状态值与存储槽，读者分不清哪一层）：
CellState& cell = cells_.at(ToFlatIndex(position));
if (cell != CellState::kEmpty) { return false; }
cell = state;

改写（槽位引用叫 stored，写入的状态值叫 state）：
CellState& stored = cells_.at(ToFlatIndex(position));
if (stored != CellState::kEmpty) { return false; }
stored = state;
```

```text
不佳（lambda 形参叫 cell，但比对的是状态）：
std::ranges::all_of(cells_, [](CellState cell) { return cell != CellState::kEmpty; });

改写（CellState 形参一律 state）：
std::ranges::all_of(cells_, [](CellState state) { return state != CellState::kEmpty; });
```

```text
不佳（CompletesLine 的 CellPosition 形参叫 cell）：
bool CompletesLine(const Game& game, CellPosition cell, CellState state);

改写（位置形参叫 position，与 CellPosition 角色对齐）：
bool CompletesLine(const Game& game, CellPosition position, CellState state);
```

## 局部 lambda 谓词对照

lambda 是变量，按 snake_case 命名；返回 `bool` 的 lambda 是谓词，名字必须带 `is_` / `has_` / `are_` 前缀，与函数前缀同一套角色（`Can` 出现时用 `can_`）。角色表的两档分工见标识 `bg-google-cpp-style-v1` 的知识文件「函数语义角色表」。

```text
不佳（返回 bool 的 lambda 叫 line_matches_state，读不出谓词角色，也看不出问的是哪件事）：
const auto line_matches_state = [&](CellPosition a, CellPosition b, CellPosition c) {
  ...
};

改写（谓词 lambda 带 is_ / has_ 前缀；两个 lambda 分别给「一格是不是 state」和「三个坐标连成线」起名）：
const auto has_state = [&](CellPosition position) {
  return board.GetCellState(position) == state;
};
const auto has_line = [&](CellPosition a, CellPosition b, CellPosition c) {
  ...
};
```

## 谓词白名单例外

`CompletesLine` 返回 `bool` 但不取 `Is` / `Has` 前缀，保留领域动词形态。它描述「假设落子凑成三连」这一 AI 探测动作，`IsCompletingLine` 现在进行时别扭、`CanCompleteLine` 与搜索的确定性语义不符；白名单已登记（标识 `bg-google-cpp-style-v1` 的知识文件「有意偏离白名单」第 10 条），只此一例，新谓词仍必须取 `Is` / `Has` 前缀，不扩散。


## 棋盘占满谓词分层

`Board::IsFull` 保留现名，不改成 `IsBoardFull` / `IsDraw` / `IsOccupied`。它是 `Board` 成员，接收者已提供名词，成员上再叠 `IsBoardFull` 属于冗余（对比 `IsValidPosition` 不叫 `IsBoardPositionValid`）；自由函数场景才强制把对象写进名字（如 `IsBoardFull(board)`）。改名 `IsDraw` 会把棋盘占用谓词与终局结果混层：教程里 `isDraw()` 常被写成「占满」或「占满且无胜者」两种语义，本仓分层是先判胜（`HasPlayerLine`）、再判占满（`Board::IsFull`）、仅在「未胜 + 已满」时由 `Game` 组合出 `GameResult::kDraw`，`Board` 不直接报平局。歧义靠注释消除：声明注释写全「每个棋盘格子都有棋子；不含胜负或平局判定」。

```text
不佳（占位谓词与终局结果混层；成员名叠床架屋）：
bool Board::IsDraw() const;      // 占满还是「占满且无胜者」？语义含混。
bool Board::IsBoardFull() const; // 接收者已是 Board，宾语冗余。

改写（成员保持 IsFull，宾语由类名承担；平局留在 Game 层组合）：
[[nodiscard]] bool IsFull() const noexcept;  // 检查棋盘是否已满（每个棋盘格子都有棋子；不含胜负或平局判定）。
// Game 侧：未分胜负且 board.IsFull() → GameResult::kDraw。
```

判定信号：占满谓词名里出现 `Draw` / `Result` 等终局词；成员谓词名重复接收者名词；自由函数缺宾语。
