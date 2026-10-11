# Palette: github

生产默认（唯一）色板。亮色对齐 GitHub Primer Light Default；暗色对齐 GitHub Primer **Dark Dimmed**（软暗色：近灰底 `#22272E`，缓解 Dark Default `#0D1117` 的偏黑与光晕）。代码语法色用色板目录里的两份 skylighting 主题 `highlight-light.theme` / `highlight-dark.theme`，取色自 Primer 当前 prettylights（[primer/github-vscode-theme](https://github.com/primer/github-vscode-theme) 的 light 与 dark-dimmed），不再用 Quarto 内置的 2020 年 `github-light` / `github-dark`。两处抬色：暗色注释从官方 `#768390` 抬到 `#9AA1AB`（本书代码底上需 4.5:1），暗色关键字改用 Dark Default 的关键字红 `#FF7B72`；取舍见标识 `bg-reading-surface-v1` 的知识文件。

## 接线

| 项 | 路径 / 值 |
| --- | --- |
| tokens | `palettes/github/tokens.css` |
| SCSS light | `palettes/github/theme-light.scss` |
| SCSS dark | `palettes/github/theme-dark.scss` |
| highlight light | `.agents/skills/designing-theme/assets/theme/palettes/github/highlight-light.theme` |
| highlight dark | `.agents/skills/designing-theme/assets/theme/palettes/github/highlight-dark.theme` |

## 暗色分层（Dark Dimmed）

| 表面 | 色值 |
| --- | --- |
| page / navbar（最深） | `#22272E` |
| surface-raised / code / card | `#2D333B` |
| 代码标题条 | `#373E47` |
| 边框 | `#444C56` |
| 正文 / 次要文字 | `#CDD9E5` / `#B1BAC4` |
| 链接 | `#539BF5` |

2026-09 软化：暗色自 Dark Default 迁至 Dimmed；圆角抬升（sm 8px / md·lg 12px / 代码块 8px）；首页卡片亮色加轻阴影；正文与代码行高 1.75；表头去大写；品牌与卡片标题 700→600。

## 切换

生产固定本 pack，不做第二套色板。若未来换 pack：在 `_quarto.yml` 中把 theme SCSS、palette tokens 与 `highlight-style` 改成目标 pack；共享 `css/*.css`、字体与 includes 不动。

## 来源

- [Primer Color usage](https://primer.style/product/getting-started/foundations/color-usage/)
- [primer/github-vscode-theme](https://github.com/primer/github-vscode-theme)（prettylights 取色来源，light 与 dark-dimmed）
- GitHub Light / Dark Dimmed 文档表面色

主题资产与 cpp-notes 同源：本仓改动的语法色主题（`highlight-light.theme`、`highlight-dark.theme`）与 `meta.md` 接线表需同步到 cpp-notes 的对应文件。
