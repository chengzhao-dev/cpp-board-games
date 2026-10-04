---
kb_id: "bg-naming-cases-v1"
title: "标识符命名正反对照"
domain: "cpp-teaching"
subdomain: "cases"
tags: [naming, google-style, pascal-case]
level_range: [0, 5]
dependencies: [bg-google-cpp-style-v1]
created: "2026-09-29"
updated: "2026-09-30"
chunk_strategy: "semantic_heading"
estimated_tokens: 400
---

# 标识符命名正反对照

命名规则与偏离白名单见标识 `bg-google-cpp-style-v1` 的知识文件；本文件保存正反对照，检索单元是「正确 + 不佳 + 改写」。

## 歧义映射命名对照

映射函数的名字必须让读者看出源端或目标端角色；单独的 `Of` / `To` 短后缀看不出两端是什么，禁止使用（依据 Google「descriptive；eschew abbreviation」）：

```text
不佳（MarkOf 看不出是「玩家 → 棋子」还是「棋盘 → 棋子」）：
CellState MarkOf(Player player);

改写（名字同时含源端与目标端角色）：
CellState CellStateFor(Player player);
```

```text
不佳（To 悬空，目标类型只能去签名里找）：
std::string To(const Board& board);

改写（目标端进名字）：
std::string BoardToString(const Board& board);
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
CellState CellStateFor(Player player);

// 动作：动词开头，结果类型表达失败而非异常。
PlaceResult Place(const Move& move);
```

正例的判定条件：谓词 `Is/Are/Has` 开头；读取用 `Get` 前缀（`GetCellState`，与返回类型对齐）；放置棋子的动作直接用领域动词（`PlacePiece`，用户定案弃用 Try 前缀）；下标换算用 `To` 前缀（`ToFlatIndex`）；映射函数含源端或目标端角色；动作函数动词开头；类型 PascalCase、变量 snake_case、常量与枚举子 `k` 前缀。
