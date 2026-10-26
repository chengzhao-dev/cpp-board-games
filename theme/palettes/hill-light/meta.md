# Palette: hill-light（山光）

运行时可选色板。读者在导航栏选「山光」后，`html[data-palette="hill-light"]` 与 `html[data-mode="dawn|noon|dusk|night"]` 同时生效：`tokens.css` 覆盖语义颜色，`syntax.css` 覆盖语法色。色值取自用户自己的仓库 `D:\Github\hill-light\hill-light-theme\css\tokens.css`（单一色值来源），四种时辰沿用原站命名：晓雾 `dawn`、午荫 `noon`、暮烟 `dusk`、夜月 `night`；夜月是唯一暗色时辰，其余三种都在浅纸上。

本插件与山光原站的取舍写在「与 hill-light 的偏离」一节：栏宽、字体、callout 类型色、语法色都没有照搬原站，理由逐条记录。

## 接线

| 项 | 路径 / 值 |
| --- | --- |
| tokens | `palettes/hill-light/tokens.css` |
| syntax 覆盖 | `palettes/hill-light/syntax.css` |
| brand mark | `palettes/hill-light/brand-mark.svg` |
| favicon light | `palettes/hill-light/favicon-light.svg`（晓雾/午荫/暮烟共用） |
| favicon dark | `palettes/hill-light/favicon-dark.svg`（夜月） |

当前 `_quarto.yml` **不**引用本目录的 SCSS 与 highlight 主题，只挂 `tokens.css` + `syntax.css`，原因和 Solarized 不同：Quarto 只能编译一对 light/dark 高亮与一对 Bootstrap 主题，而山光有四种时辰，任何一种都会被编译期固定成两态。所以山光只做运行时层：语法色由 `syntax.css` 按 `html[data-palette="hill-light"][data-mode]` 覆盖 `code span.*`，没有 `.theme` 与 SCSS 素材。

## 四时切换

| 项 | 值 |
| --- | --- |
| 属性 | `html[data-palette="hill-light"][data-mode="dawn\|noon\|dusk\|night"]` |
| 存储键 | `localStorage["book-hill-mode"]` |
| 默认时辰 | 按本地时间：06–11 晓雾、11–17 午荫、17–20 暮烟，其余夜月 |
| 明暗 | `data-mode="night"` 同时声明 `color-scheme: dark`，`includes/palette.html` 的 `isDark()` 也以夜月为准 |
| Quarto 明暗钮 | 山光下隐藏（`css/nav.css`）：山光的明暗由时辰决定，两套开关并存会互相看不出谁生效 |
| 控件 | 导航栏色板分段控件右侧的四段胶囊；≤575.98px 退成四个圆点 |

切走山光时 `data-mode` 被移除，避免其他色板误吃四时令牌。四种模式的 `body` 令牌用 `html[data-palette="hill-light"][data-mode="…"] body` 选择器，比共享的 `body` / `body.quarto-dark` 令牌（Flexoki 默认）特异性高，因此无论 Quarto 处在明暗哪一态，山光都稳定生效。

## 页面分层

| 表面 | 晓雾 dawn | 午荫 noon | 暮烟 dusk | 夜月 night |
| --- | --- | --- | --- | --- |
| page / navbar | `#F2EFE7` | `#FAF6EC` | `#F1E2D0` | `#1B2223` |
| surface-raised | `#F8F5EE` | `#FFFCF4` | `#F8EBDA` | `#232B2C` |
| 代码底 / 代码边 | `#E9E5DA` / `#D6D2C6` | `#F0EBDD` / `#D8D3C3` | `#E8D6C1` / `#D8C4AE` | `#283132` / `#3A4644` |
| 正文 / 次要文字 | `#2B3538` / `#58686B` | `#263230` / `#4F615B` | `#3A2C26` / `#67534A` | `#D7DDD9` / `#A2AEA9` |
| 动作色 / hover | `#2D6A66` / `#1F4F4C` | `#1D6A55` / `#14503F` | `#35645D` / `#264E49` | `#8CB9AE` / `#A9CFC5` |
| 表格行线 | `#DCD8CD` | `#E0DACC` | `#DECCB8` | `#313C3A` |
| 选中底色 | `#CFE0DA` | `#CCE5D8` | `#E4CFB6` | `#35514B` |

链接沿用本插件的「常态墨色 + 动作色下划线」，hover 才转动作色（山光原站是常态动作色）；其余令牌直接映射原站语义。

## 对比度记录

`temp/hill-light-build/gen.py` 生成令牌时逐对校验，四种模式全部 ≥ 目标值：

| 组合 | 晓雾 | 午荫 | 暮烟 | 夜月 |
| --- | --- | --- | --- | --- |
| 正文 / 纸 | 10.95 | 12.31 | 10.54 | 11.72 |
| 次要文字 / 纸 | 5.07 | 6.09 | 5.67 | 7.05 |
| 图注 / 纸（≥3.0） | 4.63 | 5.24 | 4.75 | 5.07 |
| 动作色 / 纸 | 5.43 | 6.00 | 5.28 | 7.44 |
| 代码字 / 代码底 | 10.00 | 11.15 | 9.45 | 9.67 |
| 代码标题字 / 标题条 | 4.85 | 5.78 | 5.37 | 5.33 |
| callout 四型 / 纸（最低） | 5.15 | 6.16 | 4.87 | 6.70 |
| 边框 / 纸（≥1.3） | 1.32 | 1.39 | 1.33 | 1.65 |

callout 五型条色由山光的低饱和色相派生：note 用次要文字灰、tip 青绿、warning 赭黄、important 靛蓝、caution 砖红；四时各一套，全部 ≥4.5:1。

## 与 hill-light 的偏离

| 项 | 山光原站 | 本插件 | 理由 |
| --- | --- | --- | --- |
| 栏宽 | `--measure: 680px` | `--content-width: 840px` | 本插件面向 C++ 书籍：代码块、方向表、终端输出在 680px 下折行严重 |
| 字体 | 思源宋体 / 思源黑体 / JetBrains Mono（系统栈） | 自托管 LXGW Bright Medium / Code | 多数 Windows 用户没有思源宋体，会落到 SimSun；1.25MB 字体的取舍见 `knowledge/reading-surface.md` |
| callout | 五型同色，只靠图标形状区分 | 五型各一条 2px 色条 | 技术书里「这是注意还是危险」必须一眼可辨；只靠色相区分又违反 WCAG 1.4.1，所以色条 + 图标 + 标题词三重编码 |
| 语法高亮 | 单色（正文色 + 淡注释） | 四色克制版（关键字/字符串/数字/注释） | 代码是本书主体，单色会让长代码块难扫读；色相仍取山光的低饱和色 |
| 组件语言 | 3px 强调条、卡片式抬升面 | 2px 强调条、无卡片、发丝线 | 本插件全站统一的设计语言，三套色板共享，不随色板变化 |
| 链接 | 常态动作色 | 常态墨色 + 动作色下划线 | 同上，三套色板一致 |
| 行号色 | 直接取次要文字色（`#5F6E6F` / `#725F55` / `#87938E`） | 各压/抬一档（`#556565` / `#68554B` / `#8F9B96`） | 原值在各自代码底上 4.19–4.25:1，行号虽属辅助信息，但它是代码块里最常被读到的小字，够不到 4.5 线就压一档 |

## 来源

- 用户仓库 `D:\Github\hill-light\hill-light-theme`：`css/tokens.css`（四时令牌）、`DESIGN.md`（设计决策）
- 生成脚本：`temp/hill-light-build/gen.py`（令牌映射 + 语法色派生 + 对比度校验）
