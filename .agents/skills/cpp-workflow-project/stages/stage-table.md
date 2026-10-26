# 井字棋章节与代码目录路由表

`scope.py` 解析 `tictactoe/<目标>` 的唯一数据源。十个章节共用一个代码目录；章节结构以插件 `writing-quarto` 的 `steps/02-structure.md` 和各页正文为准。
状态只允许 `todo` / `done`。

- **必读** 根 `AGENTS.md`、插件 `dsh-cpp-workflow` 的 `developing-cpp`、`configuring-cmake` 与 `building-cpp`、本仓 `.agents/skills/cpp-workflow-project/SKILL.md`（改代码时）、插件 `writing-quarto` 与本仓 `.agents/skills/quarto-book-project/SKILL.md`（改章节时）、`.agents/skills/quarto-book-project/glossary/forbidden-terms.md`

| 目标 | 章节正文 | 代码目录 | 专项必读 | 状态 |
| --- | --- | --- | --- | --- |
| `01-rules` | `content/tictactoe/01-rules.qmd` | `games/tictactoe` | `插件 writing-quarto 的 steps/02-structure.md` | done |
| `02-mapping-layout` | `content/tictactoe/02-mapping-layout.qmd` | `games/tictactoe` | `插件 configuring-cmake 的 references/cmake.md` | done |
| `03-board` | `content/tictactoe/03-board.qmd` | `games/tictactoe` | `插件 developing-cpp 的 references/google-cpp-style.md` | done |
| `04-game` | `content/tictactoe/04-game.qmd` | `games/tictactoe` | `decisions/architecture.md` | done |
| `05-ai` | `content/tictactoe/05-ai.qmd` | `games/tictactoe` | `decisions/architecture.md` | done |
| `06-writing-terminal` | `content/tictactoe/06-writing-terminal.qmd` | `games/tictactoe` | `SKILL.md` | done |
| `07-main` | `content/tictactoe/07-main.qmd` | `games/tictactoe` | `SKILL.md` | done |
| `08-tests` | `content/tictactoe/08-tests.qmd` | `games/tictactoe` | `SKILL.md` | done |
| `09-running-build` | `content/tictactoe/09-running-build.qmd` | `games/tictactoe` | `SKILL.md` | done |
| `10-defining-snapshot` | `content/tictactoe/10-defining-snapshot.qmd` | `games/tictactoe` | `SKILL.md` | done |

当前构建只接入 01–05 与 07 的代码；06、08、10 三章保留终端层、测试与快照设计，接回构建后再恢复对应运行状态。
