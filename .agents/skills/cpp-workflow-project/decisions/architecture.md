# 规则核心的类分工

本文件记录井字棋规则核心的职责划分与它依赖的设计依据。代码位置与阶段进度见 `stages/stage-table.md`。

## 分工

| 类 | 掌握的数据 | 交出的操作 |
| --- | --- | --- |
| `Board` | 九格状态、`CellPosition` 到下标、三连形状 | `IsInRange`、`IsCellEmpty`、`GetCellType`、`PlaceCell`、`Clear`、`IsFull`、`IsLineComplete`、`GetWinner`、`IsWin`、`IsDraw`、`IsGameOver`；`HasLine` 留在私有段 |
| `Game` | 当前玩家、落子历史、`GameResult` | `GetCurrentPlayer`、`GetHistory`、`TryPlace`、`IsLineComplete`（转发） |
| `Ai` | 选子所需的快照与强度 | `Choose`，只交 `Move` |

`Board` 回答棋盘事实，`Game` 回答对局事实。`IsDraw` 写成 `IsFull() && !IsWin()`；`IsGameOver` 写成 `IsWin() || IsDraw()`。假设落子后的成线判断 `IsLineComplete(position, cell_type)` 落在 `Board`，它不改棋盘，供 `Game` 与 `Ai` 共用；`Game::IsLineComplete` 只有一行转发，不额外开 `GetBoard()`。格子级终局与线扫描归 `Board`，`GameResult` 与当前玩家仍归 `Game`。

## 依据

- GRASP Information Expert：谁掌握数据，谁交出基于这些数据的判断。三连形状由格子组织，因此成线判断归 `Board`。
- C++ Core Guidelines C.4：只有需要直接访问类表示的函数才做成员。扫线要读九格，因此成为 `Board` 的成员函数，不再由 `Game` 或 `Ai` 另写一份。
- C.4 的接口一致例外：虚函数、运算符、同组重载或为了链式调用一致的接口，即使不碰内部表示也可以留在类内；判断时先看它是否属于同一组公开操作，再看它是否需要表示。`IsLineComplete` 需要读九格，不属于该例外。
- 规则核心不依赖终端、GUI、Web、Python 或 Quarto；适配层只通过 `Game` 的公开操作推进对局。

## 演进约束

共享库要等至少两款游戏真实复用且语义稳定后再提取，不提前抽象。`Board` 的查询方法一律 `const` 且不改棋盘；改格子的入口是 `PlaceCell` 与 `Clear`。`Clear` 整盘复位，不按坐标擦除，`PlaceCell` 仍拒绝覆盖已有棋子。
