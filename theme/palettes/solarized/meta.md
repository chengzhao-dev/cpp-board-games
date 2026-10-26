# Palette: solarized

运行时可选色板。默认页面是 Flexoki；读者在导航栏选择 Solarized 后，`html[data-palette="solarized"]` 生效，本目录的 `tokens.css` 覆盖语义颜色、`syntax.css` 覆盖语法色。亮色用 Solarized 官方 base3 页面（`#FDF6E3`），暗色用 base03 页面（`#002B36`）；正文与注释按 4.5:1 抬一档：亮色正文 `#526C74`、注释 `#556C73`；暗色正文 `#839496`、注释 `#93A1A1`。链接遵循官方 `rebase`：亮色 base01 `#586E75`、暗色 base1 `#93A1A1`，hover 才转官方蓝（亮 `#268BD2` / 暗 `#51A0D5`）；语法里的标识符蓝仍用抬过的 `#1B6EA3` / `#51A0D5`。本目录另带一对 skylighting 主题，供「整本按 Solarized 编译」时替换 `highlight-style` 使用。

## 接线

| 项 | 路径 / 值 |
| --- | --- |
| tokens | `palettes/solarized/tokens.css` |
| syntax 覆盖 | `palettes/solarized/syntax.css` |
| SCSS light | `palettes/solarized/theme-light.scss` |
| SCSS dark | `palettes/solarized/theme-dark.scss` |
| highlight light | `assets/theme/palettes/solarized/highlight-light.theme` |
| highlight dark | `assets/theme/palettes/solarized/highlight-dark.theme` |
| brand mark | `palettes/solarized/brand-mark.svg` |
| favicon light | `palettes/solarized/favicon-light.svg` |
| favicon dark | `palettes/solarized/favicon-dark.svg` |

当前 `_quarto.yml` **不**引用本目录的 SCSS 与 highlight 主题，只挂 `tokens.css` + `syntax.css`：Quarto 只能编译一对高亮样式，编译期保留 Flexoki 那对，Solarized 的语法色由 `syntax.css` 按 `html[data-palette="solarized"]` 覆盖 `code span.*`。当前目录只服务运行时层。若以后要整本编译 Solarized，需要另写不带 `html[data-palette]` 前缀的 tokens 版本，再换 `theme` 与 `highlight-style` 并删掉 `syntax.css` 这层覆盖。

## 书标与标签图标

两套色板共用同一枚「打开的书」：`brand-mark.svg` 是纯黑剪影、中缝镂空，16px 仍可辨认，顶栏用 mask 取 `--navbar-fg`，一份覆盖该色板明暗；`favicon-light.svg` / `favicon-dark.svg` 是圆角方底加同一枚书，底色/书/中缝分别用该色板的纸色、墨色、动作色。Solarized 亮色 `#FDF6E3`/`#526C74`/`#268BD2`，暗色 `#002B36`/`#839496`/`#51A0D5`。

用书项目在 `_quarto.yml` 设 `book.favicon: theme/palettes/flexoki/favicon-light.svg`，并把另外三份 favicon 放进 `resources`。`includes/palette.html` 在 head 内按 `book-palette` 与明暗改 `link[rel=icon]` 的 href，只替换 URL 里的色板名与 `favicon-light|dark`，保留 Quarto 写好的 `./` / `../` 前缀；发布 URL 仍带 `palettes/<name>/`。

## 页面分层

| 表面 | 亮色 | 暗色 |
| --- | --- | --- |
| page / navbar | `#FDF6E3` | `#002B36` |
| surface-raised / code | `#EEE8D5` | `#073642` |
| 代码标题条（派生） | `#E7E0CB` | `#0A3F4C` |
| 代码标题字（派生） | `#4C6166` | `#A9B7B7` |
| 边框 | `#93A1A1` | `#586E75` |
| 正文 / 次要文字 | `#526C74` / `#586E75` | `#839496` / `#93A1A1` |
| 链接常态 / hover | `#586E75` / `#268BD2` | `#93A1A1` / `#51A0D5` |

代码标题条不是官方 base 色，是在 base2 / base02 上各压一档得到的派生表面，用来把标题条与代码底分开；其余页面色取官方值。

## 对比度记录

Solarized 官方正文与注释在各自底色上低于 4.5:1；这里只抬正文与注释，链接回到官方 rebase，页面底色、强调色与 callout 条保持官方值：

| 组合 | 比值 |
| --- | --- |
| 亮色正文 `#526C74` / `#FDF6E3` | 5.18:1 |
| 亮色正文 `#526C74` / `#EEE8D5` | 4.56:1 |
| 亮色链接 `#586E75` / `#FDF6E3` | 4.99:1 |
| 亮色链接 `#586E75` / `#EEE8D5` | 4.39:1（代码内，正文链接不在代码底） |
| 亮色注释 `#556C73` / `#EEE8D5` | 4.54:1 |
| 暗色正文 `#839496` / `#002B36` | 4.75:1 |
| 暗色链接 `#93A1A1` / `#002B36` | 5.61:1 |
| 暗色链接 `#93A1A1` / `#073642` | 4.86:1 |
| 暗色注释 `#93A1A1` / `#073642` | 4.86:1 |
| 亮色代码标题字 `#4C6166` / `#E7E0CB` | 4.96:1 |
| 暗色代码标题字 `#A9B7B7` / `#0A3F4C` | 5.55:1 |

注释以官方 base01（亮）/ base1（暗）为起点：亮色 base1 `#93A1A1` 在 base2 上只有 2.18:1，不可用；暗色 base01 `#586E75` 在 base02 上只有 2.42:1，也不可用。亮色注释取更深的 `#556C73`（代码底 4.54:1），暗色注释保持官方 base1 `#93A1A1`（代码底 4.86:1）。强调色仍是 base01 `#586E75`（亮，4.99:1）；callout 左条用官方语义色（note base01/base1、warning orange `#CB4B16`、tip green `#859900`）。取舍见 `knowledge/reading-surface.md`。

## 来源

- [Solarized](https://ethanschoonover.com/solarized/)（Ethan Schoonover，MIT）
- Solarized 官方 palette：base03 `#002B36`、base02 `#073642`、base01 `#586E75`、base00 `#657B83`、base0 `#839496`、base1 `#93A1A1`、base2 `#EEE8D5`、base3 `#FDF6E3`；accent：yellow `#B58900`、orange `#CB4B16`、red `#DC322F`、magenta `#D33682`、violet `#6C71C4`、blue `#268BD2`、cyan `#2AA198`、green `#859900`

本目录 10 个文件随主题资产走；项目副本只同步到 `_quarto.yml` 实际引用的那份。
