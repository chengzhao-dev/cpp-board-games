# Palette: github

生产默认（唯一）色板。亮色对齐 GitHub Primer Light Default；暗色对齐 GitHub Primer **Dark Dimmed**（软暗色：近灰底 `#22272E`，缓解 Dark Default `#0D1117` 的偏黑与光晕）。代码高亮使用 Quarto 内置 `github-light` / `github-dark`。

## 接线

| 项 | 路径 / 值 |
| --- | --- |
| tokens | `palettes/github/tokens.css` |
| SCSS light | `palettes/github/theme-light.scss` |
| SCSS dark | `palettes/github/theme-dark.scss` |
| highlight light | `github-light` |
| highlight dark | `github-dark` |

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
- GitHub Light / Dark Dimmed 文档表面色
