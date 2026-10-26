# Palette: flexoki

编译默认色板。亮色用 Flexoki 的纸色页面（`#FFFCF0`）与墨色正文（`#100F0F`），暗色反转为墨色页面（`#100F0F`）与纸色正文（`#CECDC3`）；链接遵循 Flexoki 官方 UI 映射：常态与正文同墨色（亮 `#100F0F` / 暗 `#CECDC3`）并保留下划线，hover 才转 `cy`（亮 `#24837B` / 暗 `#3AA99F`）；`bl` 蓝只留给变量/属性与语法。代码语法色用本目录两份 skylighting 主题 `highlight-light.theme` / `highlight-dark.theme`，按 Flexoki 官方 VS Code 主题的语法映射取色（[kepano/flexoki](https://github.com/kepano/flexoki)），不再用 Quarto 内置高亮。Solarized 作为运行时可选色板放在同级 `solarized/`，只覆盖令牌与语法色，不改编译配置。

一处抬色：亮色注释从官方 `#6F6E69` 抬到 base-700 `#575653`（代码底 `#F2F0E5` 上 4.47:1 → 6.42:1），行号同步用 `#575653`；暗色注释保持官方 `#878580`（`#1C1B1A` 上 4.67:1）。亮色强调色与正文同为 `#100F0F`，靠字重区分，不引入纯黑。官方文档注释档（亮 `#B7B5AC` / 暗 `#575653`）对比不足，未采用。取舍见 `knowledge/reading-surface.md` 的「颜色与对比度的取值依据」。

## 接线

| 项 | 路径 / 值 |
| --- | --- |
| tokens | `palettes/flexoki/tokens.css` |
| SCSS light | `palettes/flexoki/theme-light.scss` |
| SCSS dark | `palettes/flexoki/theme-dark.scss` |
| highlight light | `theme/palettes/flexoki/highlight-light.theme` |
| highlight dark | `theme/palettes/flexoki/highlight-dark.theme` |
| brand mark | `palettes/flexoki/brand-mark.svg` |
| favicon light | `palettes/flexoki/favicon-light.svg` |
| favicon dark | `palettes/flexoki/favicon-dark.svg` |

`_quarto.yml` 的 `theme` 与 `highlight-style` 指向本目录；`css` 里本目录 tokens 必须排在 `palettes/solarized/tokens.css` 之前。

## 书标与标签图标

两套色板共用同一枚「打开的书」：`brand-mark.svg` 是纯黑剪影、中缝镂空，16px 仍可辨认，顶栏用 mask 取 `--navbar-fg`，一份覆盖该色板明暗；`favicon-light.svg` / `favicon-dark.svg` 是圆角方底加同一枚书，底色/书/中缝分别用该色板的纸色、墨色、动作色。Flexoki 亮色 `#FFFCF0`/`#100F0F`/`#24837B`，暗色 `#100F0F`/`#FFFCF0`/`#3AA99F`。

用书项目在 `_quarto.yml` 设 `book.favicon: theme/palettes/flexoki/favicon-light.svg`，并把另外三份 favicon 放进 `resources`。`includes/palette.html` 在 head 内按 `book-palette` 与明暗改 `link[rel=icon]` 的 href，只替换 URL 里的色板名与 `favicon-light|dark`，保留 Quarto 写好的 `./` / `../` 前缀；发布 URL 仍带 `palettes/<name>/`。

## 页面分层

| 表面 | 亮色 | 暗色 |
| --- | --- | --- |
| page / navbar | `#FFFCF0` | `#100F0F` |
| surface-raised / code / card | `#F2F0E5` | `#1C1B1A` |
| 代码标题条 | `#E6E4D9` | `#282726` |
| 边框 | `#DAD8CE` | `#343331` |
| 正文 / 次要文字 | `#100F0F` / `#6F6E69` | `#CECDC3` / `#9F9D96` |
| 链接常态 / hover | `#100F0F` / `#24837B` | `#CECDC3` / `#3AA99F` |

Callout 是编辑注：2px 左条、`-bg: transparent`、无圆角；note 用中性 base-600 / base-400，warning 用官方 orange（亮 `#BC5215` / 暗 `#DA702C`），不把黄当警告。

暗色次要文字保留 Flexoki base-400 `#9F9D96`：它在墨色底上 7.05:1，介于 base-300 `#B7B5AC` 与 base-500 `#878580` 之间，比正文 `#CECDC3` 低一档，不抢正文但仍高于 4.5:1。

## 切换

Flexoki 是编译默认：`_quarto.yml` 的 `theme`、`highlight-style` 都指向本目录。读者切到 Solarized 只改 `html[data-palette="solarized"]`，由 `palettes/solarized/tokens.css` 与 `syntax.css` 覆盖；选择器与首屏恢复在 `includes/palette.html`。

## 来源

- [Flexoki](https://stephango.com/flexoki)（Steph Ango，MIT）
- [kepano/flexoki](https://github.com/kepano/flexoki)（色值与 VS Code 语法映射）
- Flexoki 官方 VS Code 主题 `Flexoki Light` / `Flexoki Dark`

本目录 9 个文件随主题资产走；项目副本只同步到 `_quarto.yml` 实际引用的那份。
