# 井字棋阶段路由表

`scope.py` 解析 `tictactoe/<目标>` 的唯一数据源。前五个说明页共用一个代码目录；章节职责以 `chapter-page-pattern.md` 和各页正文为准。
状态只允许 `todo` / `done`。

- **必读** 根 `AGENTS.md`、`.agents/skills/cpp-development/SKILL.md`（改代码时）、`.agents/skills/writing-quarto/SKILL.md`（改章节时）、`.agents/skills/testing/references/verification-matrix.md`

| 目标 | 章节正文 | 代码目录 | 专项必读 | 状态 |
| --- | --- | --- | --- | --- |
| `01-rules` | `content/tictactoe/01-rules.qmd` | `games/tictactoe/01-cli-game` | `.agents/knowledge/agent-workspace/planning/engineering-storyline.md` | done |
| `02-project-layout` | `content/tictactoe/02-project-layout.qmd` | `games/tictactoe/01-cli-game` | `.agents/context/conventions/cmake.md` | done |
| `03-board` | `content/tictactoe/03-board.qmd` | `games/tictactoe/01-cli-game` | `.agents/context/conventions/cpp-style.md` | done |
| `04-game` | `content/tictactoe/04-game.qmd` | `games/tictactoe/01-cli-game` | `.agents/context/architecture.md` | done |
| `05-terminal-play` | `content/tictactoe/05-terminal-play.qmd` | `games/tictactoe/01-cli-game` | `.agents/context/conventions/terminal-output.md` | done |
| `06-opponent` | `content/tictactoe/06-opponent.qmd` | `games/tictactoe/02-cpu-opponent` | `.agents/context/project.md` | done |
| `07-line-protocol` | `content/tictactoe/07-line-protocol.qmd` | `games/tictactoe/03-line-protocol` | `.agents/context/project.md` | done |
