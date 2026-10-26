# 章节对照

本文件只收通用技能不知道的事实：每一章的文件名、类章或能力章、关键对象、YAML `title` 与二级标题。类章与能力章的定义、一章一个关键、标题分层与收尾节名由插件 `writing-quarto` 的 `steps/02-structure.md` 负责，这里不抄。

章节顺序以根 `_quarto.yml` 的 `book.chapters` 与 `book.appendices` 为准；下表只用于核对章节骨架。`content/tictactoe/index.qmd` 是 part 落地页（`part:` 指向它），不在 `chapters` 里重复列出。

| 路径 | 类章 / 能力章 | 关键（类或交付物） | `title` | 二级标题（按顺序） | 视角 |
| --- | --- | --- | --- | --- | --- |
| `content/tictactoe/index.qmd` | 散文页 | 本书的组织方式 | 井字棋 | — | 总览 |
| `content/tictactoe/01-rules.qmd` | 能力章 | 一局对局要遵守的约定 | 对局规则 | 落子规则、胜负判定、对局演示、自测问题、本章回顾 | 总览 |
| `content/tictactoe/02-mapping-layout.qmd` | 能力章 | 工程结构的组织 | 工程结构 | 目录分工、文件位置、常见错误、自测问题、本章回顾 | 总览 |
| `content/tictactoe/viewing-program.qmd` | 散文页 | 程序的整体形状 | 程序结构 | 结构总览、分块明细、常见错误、自测问题、本章回顾 | 总览 |
| `content/tictactoe/03-board.qmd` | 类章 | `Board` | 棋盘 | 类型与坐标、成员与接口、棋子写入、终局判定、常见错误、自测问题、本章回顾 | 对象 |
| `content/tictactoe/04-game.qmd` | 类章 | `Game` | 对局 | 类型与玩家、成员与接口、落子入口、常见错误、自测问题、本章回顾 | 对象 |
| `content/tictactoe/05-ai.qmd` | 类章 | `Ai` | 电脑落子 | 落子强度、选择接口、派生选择、创建选择对象、常见错误、自测问题、本章回顾 | 对象 |
| `content/tictactoe/06-writing-terminal.qmd` | 能力章 | `RunMatch` 驱动的终端对局 | 终端程序 | 输入与输出、对局循环、常见错误、自测问题、本章回顾 | 对象 |
| `content/tictactoe/07-main.qmd` | 能力章 | `main` 的最小动态库调用 | 程序入口 | 调用动态库、退出码、常见错误、自测问题、本章回顾 | 对象 |
| `content/tictactoe/08-tests.qmd` | 能力章 | 14 条棋盘用例 | 测试 | 测试用例结构、测试运行、常见错误、自测问题、本章回顾 | 对象 |
| `content/tictactoe/09-running-build.qmd` | 能力章 | 配置、编译、测试与运行的三步流程 | 构建与运行 | 构建脚本、构建规则、验收结果、常见错误、自测问题、本章回顾 | 对象 |
| `content/tictactoe/10-defining-snapshot.qmd` | 能力章 | 终端层 `WriteSnapshot` 的快照设计 | 局面快照 | 快照字段、棋盘还原、常见错误、自测问题、本章回顾 | 对象 |

## 三级标题的单点条目

以下三级标题只属于对应章的关键，升成章标题会切走该章的关键：

- `03-board`：`## 成员与接口` 下的 `### 检查下标区间`（`IsInRange`）；`## 棋子写入` 下的 `### 落子校验` 与 `### 清空棋盘`（`Clear`）；`## 终局判定` 下的 `### 线坐标表`（`kLines`）、`### 成线判断`（`HasLine`）与 `### 三连判定`（`IsLineComplete` 复用 `kLines`）。
- `05-ai`：`## 选择接口` 下的 `### 调用约定` 与 `### 候选落子列表`。

## 写作约束

- `title` 与 `_quarto.yml` 及正文 YAML 中的写法逐字一致；类章的 `title` 用读者名（棋盘、对局、电脑落子），不写英文类名，除非关键对象本身只有一个英文名。
- 项目名「井字棋」在 `content/tictactoe/03-board.qmd` 首次提到棋盘时写全「井字棋棋盘」，同章后文用「棋盘」；其他章需要点明项目时同样首次写全，后文不再逐段重复「井字棋」。
- 本表是章题约定：`title`、`关键`、`二级标题` 三列与正文同轮同步；改 title 或任务节时同轮改本表，表与正文不一致按章题脱节处理。`checking-book.py` 会逐章核对本表的 `title` 与 `##` 顺序。
- 二级标题是这一章关键的部分，顺序与「关键」一列对应；成员函数可以做三级标题，不能做章标题。
- 固定收尾 `常见错误`、`自测问题`、`本章回顾` 不改名，不升成关键；`content/tictactoe/index.qmd` 没有这三节，其余章按现有骨架保留。
- 类型章的文件名镜像关键类：`03-board` 对 `Board`、`04-game` 对 `Game`、`05-ai` 对 `Ai`、`06-writing-terminal` 交出 `RunMatch`、`07-main` 交出 `main`。
- `viewing-program.qmd` 排在 02 与 03 之间，不是第十一章，编号继续留在 `02` 与 `03` 上。
- 改文件名时同轮同步 `_quarto.yml`、本表、`title`、已有链接与 `.agents/skills/quarto-book-project/checks.json` 的 `chapter_titles`，不留旧名孤儿。
