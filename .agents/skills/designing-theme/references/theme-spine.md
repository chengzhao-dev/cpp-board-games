# 主题工序：唯一入口

所有改主题资产（`assets/theme/` 下的 css、scss、字体、palette）或 `_quarto.yml` 视觉配置的任务先读本文件按工序走，禁止跳过本文件直接通读 references 或知识库。本文件只登记步骤和该步打开的文件与 `##`，不复制色值、字号和字体理由；冲突裁决：knowledge 条文 > 本文件的步骤登记。

本轮不改写根 `AGENTS.md`；同一步只打开登记的那一个文件和那一个 `##`；本轮已经读过的文件不重复读。

## 主题工序

从定表面到过闸依次走完；后一步发现前一步没做完，退回那一步，不在当前步补。每一步只打开登记的那一个文件和那一个 `##`。

| 步骤 | 动作与产出 | 登记的文件与一节 |
| --- | --- | --- |
| 1 定表面 | 这次动的是正文、代码、Callout 还是导航；只判定，还不动 CSS | 本文件的步骤表 |
| 2 定字体 | 中文保持霞鹜楷体路线；西文和代码按已有定案，产出字体栈改动 | `references/theme-system.md`「字体栈与字形来源（定字体）」+ `css/fonts.css` |
| 3 定尺度 | 字号台阶、行长与栏宽；视口不够时不改字号，只让代码块横向滚动 | `references/theme-system.md`「字号、行长与页面尺度（定尺度）」+ `css/tokens.css` |
| 4 定颜色 | 正文、强调、链接、次要文字、代码标题在 `body` 与 `body.quarto-dark` 各写一套；代码语法色改 `palettes/<pack>/highlight-light.theme` / `highlight-dark.theme` 两份主题文件，CSS 不覆盖 `span` 色；切换后核对加粗、链接、链接里的加粗、列表小标题和代码文件名没有串色 | `references/theme-system.md`「令牌与色板（定颜色）」+ `palettes/github/tokens.css` + `palettes/github/highlight-*.theme` |
| 5 定组件 | 只打开要改的那一个 `css/*.css`；导航字重、答案折叠、行内代码、复制按钮、打印换行属于这一步，不在定颜色里顺手改 | `references/theme-system.md`「组件约定（定组件）」对应条目 |
| 6 过闸 | `check_layout.py`，然后整本 `render`；只检查，不在这一步发明新的字号或颜色 | `scripts/check_layout.py`；闸的登记见 `.agents/skills/testing/references/verification-matrix.md` |

## 增量链（改规则）

1. 查权威矩阵（KNOWLEDGE.md「按任务定点取用」表）→ 只改 `theme-system.md` 对应 `##`。
2. 新规则必须先标明属于哪一步：能放进已有 `##` 就放进去；只有尺度真的变了才允许新开一步。禁止再写一条不标明步骤的禁令。
3. 字体、栏宽、颜色定案的理由写进知识 `bg-reading-surface-v1`，不在 reference 里重复论证。
4. 同步更新本文件 / SKILL / theme-system / 知识 / 闸。
5. `kb-index` → `kb-check` → `kb-eval`。
