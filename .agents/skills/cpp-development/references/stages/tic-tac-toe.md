# 井字棋阶段路由表

`scope.py` 解析 `tic-tac-toe/<目标>` 的唯一数据源：阶段行给出章节、代码目录、专项必读与状态。
章号与阶段号允许错位（横向说明页占章号不对应代码阶段），对应关系以本表为准，不靠数字推断。
验收语义与 `.agents/skills/testing/references/verification-matrix.md` 一致，本表只补读取边界；
状态只允许 `todo` / `done`，新阶段开工时先在这里补行。

- **必读** 根 `AGENTS.md`、`.agents/skills/cpp-development/SKILL.md`（改代码时）、`.agents/skills/writing-quarto/SKILL.md`（改章节时）、`.agents/skills/testing/references/verification-matrix.md`

| 目标 | 章节正文 | 代码目录 | 专项必读 | 状态 |
| --- | --- | --- | --- | --- |
| `01-scope-and-principles` | `content/tic-tac-toe/01-scope-and-principles.qmd` | —（横向说明页，无代码阶段） | `.agents/knowledge/agent-workspace/planning/engineering-storyline.md` | done |
| `01-toolchain-probe` | `content/tic-tac-toe/02-toolchain-probe.qmd` | `games/tic-tac-toe/01-toolchain-probe` | `.agents/knowledge/cpp-teaching/toolchain/cmake-conventions.md`、`.agents/knowledge/cpp-teaching/style/comment-style.md`、`.agents/knowledge/cpp-teaching/style/terminal-output-style.md` | done |
| `02-board-and-state` | `content/tic-tac-toe/03-board-and-state.qmd` | `games/tic-tac-toe/02-board-and-state` | `.agents/knowledge/cpp-teaching/toolchain/cmake-conventions.md`、`.agents/knowledge/agent-workspace/navigation/staged-game-layout.md` | done |
| `03-move-validation` | `content/tic-tac-toe/04-move-validation.qmd` | `games/tic-tac-toe/03-move-validation` | `.agents/knowledge/agent-workspace/planning/project-decisions.md` | todo |
| `04-turns-and-terminal-rules` | `content/tic-tac-toe/05-turns-and-terminal-rules.qmd` | `games/tic-tac-toe/04-turns-and-terminal-rules` | `.agents/knowledge/agent-workspace/planning/project-decisions.md` | todo |
| `05-cli-and-acceptance` | `content/tic-tac-toe/06-cli-and-acceptance.qmd` | `games/tic-tac-toe/05-cli-and-acceptance` | `.agents/knowledge/agent-workspace/planning/roadmap.md` | todo |
| `07-incremental-roadmap` | `content/tic-tac-toe/07-incremental-roadmap.qmd` | —（门槛表说明页，无代码阶段） | `.agents/knowledge/agent-workspace/planning/roadmap.md` | done |
| `08-ai-and-two-player-extension` | `content/tic-tac-toe/08-ai-and-two-player-extension.qmd` | —（规划页，实现前不建代码目录） | `.agents/knowledge/agent-workspace/planning/roadmap.md` | todo |
| `09-python-and-web-transition` | `content/tic-tac-toe/09-python-and-web-transition.qmd` | —（规划页，实现前不建代码目录） | `.agents/knowledge/agent-workspace/planning/roadmap.md`、`.agents/skills/python-tooling/SKILL.md` | todo |
| `10-completion-and-next-steps` | `content/tic-tac-toe/10-completion-and-next-steps.qmd` | —（收官页，无代码阶段） | `.agents/knowledge/agent-workspace/planning/engineering-storyline.md` | todo |
