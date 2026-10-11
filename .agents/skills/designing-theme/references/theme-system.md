# 主题系统（设计令牌与文件结构）

## 令牌与色板（定颜色）

令牌语义与流程见本文件。**颜色**只写在 `palettes/<name>/tokens.css`；**结构尺度**（字号、半径、字体栈、`--content-width`）写在 `css/tokens.css`。本文件不维护数值副本。

生产默认色板是 `palettes/github`（亮色 Primer Light / 暗色 Primer Dark Dimmed，不做第二套色板）。换色板只改 `_quarto.yml` 的 pack SCSS、`palettes/<name>/tokens.css` 与 `highlight-style`，共享组件 CSS 不动。

### 令牌索引

| 语义 | CSS 变量 | 使用边界 |
|---|---|---|
| 页面底色 / 浮起面 | `--page-bg` / `--surface-raised` | 页面与抬升表面 |
| 正文最大宽度 | `--content-width` | 正文容器上限，不是段落二次限宽 |
| 正文 / 次要文字 | `--body-color` / `--text-secondary` | 正文层级 |
| 正文强调 / 链接 | `--emphasis-color` / `--link-color` / `--text-link` | 强调不用链接蓝，链接保持 Primer 蓝 |
| 代码外观 | `--code-*` / `--code-title-*` | 语言块、纯文本块与代码标题 |
| 表格 / 卡片边框 | `--table-border` / `--card-border` | 分隔与边框 |
| 眉标与状态点 | `--dot-accent` | 首页与状态强调 |
| 顶栏 | `--navbar-*` | 导航、搜索与主题切换 |

### callout 色（左条 + 浅底）

每个内置 callout 有一对 `--callout-<type>-border` / `-bg`，写在活跃 palette。SCSS `$callout-*` 须与 border 同步，供编译期图标 data URI。条色用页面已有功能色（亮：链接蓝 `#0969DA`、成功绿 `#1F883D`、低饱和琥珀 `#8A5C00`、Primer 紫 `#8250DF`、红 `#CF222E`；暗：Primer Dark Dimmed 同族），浅底用同色 8%–12% 透明；callout 内链接回到正文链接色，不跟条色。

### 强调、链接与明暗一致性

- 正文 `strong` 用「颜色 + 加粗」双重强调（`content.css`）：`font-weight: 700` 加 `font-synthesis: weight`——全站只有 Bright Medium 一个字面且 body 禁合成，合成只放开给 strong；强调色比正文更实一档（亮更深、暗更亮），不用链接蓝。
- 列表里独占一段的 `strong`（如「出错的原因」）保持块级小标题，颜色用正文色，不走强调色。
- 链接里的加粗跟链接色走；代码文件名用自己的 `--code-title-fg`，不被 strong 强调色盖住。
- 行内代码与 `kbd` 保持「弱底 + 正文色」，不继承强调色。
- `prefers-contrast: more` 段与常规模式用同一套强调色，不回退旧值。
- 组件 CSS 不写色值，明暗各写一套；切换后核对加粗、链接、链接里的加粗、列表小标题和代码文件名没有串色。

## 字体栈与字形来源（定字体）

全站一份正文字面：`LXGW Bright Medium`（Klee One 中笔画 + Ysabeau Office 西文，登记 `font-weight: 400`，标题请求 600 时在 `font-synthesis: none` 下仍落到这一份）；代码用 `LXGW Bright Code`（Klee + Monaspace Argon）。中文保持霞鹜楷体路线，不换黑体；文楷 Screen 与 Fixel 已移除。西文来源依据：文楷仓库点名 Ysabeau；Bright 用齐线数字的 Ysabeau Office；文楷 Screen 的 Medium 笔画标 Regular、度量对齐 Roboto，不适合中西文都自托管的站点。

- 文件与预算：`assets/fonts/` 每字体一个 `*-common.woff2`（共 2 个），单页合计 ≤ 1.6 MB、≤ 5 个文件。
- 子集：沿用常用字表并覆盖全书正文与终端输出；生成方式 `pyftsubset --flavor=woff2 --no-hinting`。改结果文案或新增字符后，用 fontTools 读 woff2 cmap 复核（起因：子集共用字符表漏「胜」，结果行末字落到宋体）；`check_layout.py` 的覆盖断言在未声明 unicode-range 时直接读 cmap。
- 同步点：改字体须同步 SCSS、tokens、fonts、OFL、资产与 `check_layout.py`；Mermaid 的 `%%{init}%%` 与 `coords_grid.py` 的 `FONT_FAMILY` 用同栈短版（`LXGW Bright Medium, system-ui, sans-serif`），保证测量与渲染一致。
- 栈尾 CJK 系统字体兜底（PingFang SC、Microsoft YaHei、Noto Sans CJK SC、Source Han Sans SC）保留，缺字时落系统黑体而不是浏览器默认宋体。
- 不采用 Inter、思源黑体、JetBrains Mono、Cascadia、Iosevka、Inconsolata；Roboto/Segoe UI 不放进 `assets/fonts/`（OFL 政策）。

## 字号、行长与页面尺度（定尺度）

| 元素 | 值 |
|---|---|
| 正文 | 16px / lh 1.75 / 内容列 840px |
| H1（title） | 32px / w600 |
| H2 | 24px / w600 / mt 2.75rem mb 0.9rem |
| H3 | 20px（1.25rem）/ w600 / mt 2rem |
| H4 | 18px / w600 |
| 代码块 | 16px（1rem）/ lh 1.75 |
| 行内代码 | 0.875em |
| Callout 正文 / 标题 | 16px / 15px |

- 层级只靠字号与颜色：全站一个字面，导航、标题、卡片上的 `font-weight: 600` 不再书写（写了也不变粗），靠色条、浅底、字号区分。
- 正文与代码行高 1.75（CJK 阅读舒适带）；章节分隔靠 H2 的 `margin-top`，无通栏底线。
- `grid.body-width` 是正文列上限（现 300+872+272+2×16=1476 封顶）；Quarto 会从 body-width 中减去两侧各 1rem 的栅格内边距，正文内容列 = body-width − 32px（现 840px）。取 872px 是让 16px Bright Code 下 100 列代码块（834px 内容宽）不换行的最小配置。取值只在 `_quarto.yml`，`--content-width` 只限正文容器；禁止 `75ch` 二次限宽。
- 代码块不折行：`white-space: pre` + 块内横向滚动（`_quarto.yml` 的 `code-overflow: scroll`）；窄视口整页不出横向滚动条，打印时恢复折行（`code.css` 的打印规则）。
- ≤991.98px 左栏浮层必须不透明实底（见 `cpp-quarto-sidebar-overlay-v1`）。

## 组件约定（定组件）

- **代码块**：弱底 + 细边。有 `filename` 时用标题条，复制钮右上角；复制钮边框和图标用 `--text-secondary`（暗色下按钮底与代码底同色，边框太暗图标会沉进去）。
- **Callout**：左 3px 色条 + 浅底 + `border-radius: var(--radius-sm)`；正文 16px、标题 15px；内链接用正文链接色。
- **侧栏 active**：浅底高亮 + `--accent` 左轨；右目录 active 同策略（正文色 + 色条，`!important` 压住 Quarto 写死的 `#0969da`，暗色不得漏亮蓝）；侧栏与目录焦点环用中性灰，正文焦点环用链接色。
- **列表与折叠**：marker 用 `--text-secondary`，折叠三角用正文色；答案盒子边框用 `--card-border`。
- **首页卡片**：平边框、轻 hover 变边框色 + `--card-shadow` 软阴影，一行最多两列；根首页 Hero 无框左对齐。
- **顶栏品牌标**：`brand-mark.svg` 作 `mask`、以 `--navbar-fg` 上色；标签页用 `favicon.svg`。图标高 1.5rem，`margin-bottom` 对齐汉字基线（换字体后只调这一处偏移）；窄屏先压搜索再省标题。
- **color-scheme**：浅色声明 `light`，深色由 `body.quarto-dark` 覆盖，避免系统偏好渗入控件与内嵌 SVG。
- **纯文本代码块**：与语言块共用 `--code-*`；`text` 不启用语言 token。
- **`.code-caption`**：次要说明色，紧贴对象；写作见 writing-quarto `authoring.md`。
- **可折叠答案**：`details.answer-disclosure` 默认收起，边框圆角与卡片一致。
- **图**：Mermaid 与坐标图用令牌着色、字体随 `--ui-font`；围栏 `%%{init}%%` 用同栈短版；暗色不为白底图加滤镜。
- **打印**：`pre` 恢复折行；屏幕横向滚动规则不动。
- **高对比偏好**：`prefers-contrast: more` 段与常规模式保持同一套强调与边框色。

## 设计来源

Quarto Book 三栏；生产唯一色板 `palettes/github`：亮色对齐 Primer Light Default，暗色对齐 Primer Dark Dimmed（软暗色）。实现为 Bootstrap cosmo/darkly + 主题 CSS。字体依据见标识 `bg-reading-surface-v1` 的知识文件。

## 主题结构与装配

官方字段见 Quarto HTML format reference。下列路径与装配顺序是本项目契约。

### 文件职责

| 文件 | 放什么 | 不放什么 |
|---|---|---|
| `palettes/<name>/theme-*.scss` | `$primary`、`$callout-color-*`、字体栈等 | 组件规则 |
| `palettes/<name>/tokens.css` | 明暗语义颜色 | 结构尺度、选择器 |
| `palettes/<name>/meta.md` | 来源、highlight 映射 | 运行时 CSS |
| `css/fonts.css` | `@font-face` 声明 | 字体栈选择 |
| `css/tokens.css` | 字号、半径、字体栈、`--content-width`、`color-scheme` 基线 | 色值、选择器 |
| `css/*.css`（除 tokens） | 组件规则；顺序 = `_quarto.yml` 的 `css:` | Bootstrap 变量 |

### 切换色板

1. `_quarto.yml` 的 `theme.light/dark` 指到目标 pack SCSS。
2. `css:` 列表替换为目标 `palettes/<name>/tokens.css`（共享 `css/tokens.css` 保留）。
3. `highlight-style` 与该 pack `meta.md` 一致。
4. 跑 `check_layout` / `check_dom_contracts`（C0 断言 yml↔meta；色值按活跃 pack 表）。

### 页面结构约定

- 垂直节奏由正文容器与 section 的 `* + *` 控制，不对 `pre`/`p` 另设 `margin-bottom`。
- 顶栏与页面同底 + 底发丝线，用 `--navbar-*`。
- 正文链接用 `--link-color` + 细下划线；不加 `:visited` 紫色。
- 表格无外框/斑马纹，表头底线 + 行 hairline。
- 导航「Search / Source Code」英文默认值由 `includes/footer.html` 按 zh 同义补齐，只替换英文原文。

### 新增 callout

1. 活跃 palette `tokens.css` 加 border/bg（亮暗各一对）。
2. 同 pack `theme-*.scss` 加 `$callout-color-*`。
3. `callouts.css` 加 `.callout.callout-<name>`。
4. 新语义写入本节令牌索引。

### 校验与高亮契约

- `check_layout.py` 校验令牌与布局；发布用 `1280/768/390` 明暗与触屏、窄屏浮层。
- 高亮由 `_quarto.yml` 提供且与 palette `meta.md` 一致（github 包为色板目录里的 `palettes/github/highlight-light.theme` / `highlight-dark.theme`，取色自 Primer 当前 prettylights）；CSS 不覆盖语法 token 色。注释色必须在本书代码底（亮 `#F6F8FA`、暗 `#2D333B`）上达到 4.5:1，暗色靠抬一档灰（`#9AA1AB`）满足，不回退整页近黑。
- `text` 与语言块共用字体尺度；标题块用 `.code-with-filename`。
- `check_dom_contracts.py`：C0 palette↔highlight；复制按钮兄弟 DOM；触屏/打印；favicon；Mermaid SVG。
