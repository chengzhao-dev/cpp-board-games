# 主题系统（设计令牌与文件结构）

## 设计令牌

令牌语义与流程见本文件。**颜色**只写在 `palettes/<name>/tokens.css`；**结构尺度**（字号、半径、字体栈、`--content-width`）写在 `css/tokens.css`。本文件不维护数值副本。

生产默认色板是 `palettes/github`（亮色 Primer Light / 暗色 Primer Dark Dimmed，不做第二套色板）。换色板只改 `_quarto.yml` 的 pack SCSS、`palettes/<name>/tokens.css` 与 `highlight-style`，共享组件 CSS 不动。

### 令牌索引

| 语义 | CSS 变量 | 使用边界 |
|---|---|---|
| 页面底色 / 浮起面 | `--page-bg` / `--surface-raised` | 页面与抬升表面 |
| 正文最大宽度 | `--content-width` | 正文容器上限，不是段落二次限宽 |
| 正文 / 次要文字 | `--body-color` / `--text-secondary` | 正文层级 |
| 链接 / 强调 | `--link-color` / `--accent` / `--text-link` | 链接和交互强调 |
| 代码外观 | `--code-*` / `--code-title-*` | 语言块、纯文本块与代码标题 |
| 表格 / 卡片边框 | `--table-border` / `--card-border` | 分隔与边框 |
| 按钮 / 眉标 | `--btn-primary-*` / `--dot-accent` | 首页与状态强调 |
| 顶栏 | `--navbar-*` | 导航、搜索与主题切换 |

### callout 色（左条 + 浅底）

每个内置 callout 有一对 `--callout-<type>-border` / `-bg`，写在活跃 palette。SCSS `$callout-color-*` 须与 border 同步，供编译期图标 data URI。

### 组件约定

- **代码块**：弱底 + 细边。有 `filename` 时用标题条，复制钮右上角。
- **Callout**：左 3px 色条 + 浅底 + `border-radius: var(--radius-sm)`；正文 16px、标题 15px。
- **侧栏 active**：浅底高亮 + `--accent` 左轨。
- **首页卡片**：平边框、轻 hover 变边框色 + `--card-shadow` 软阴影，一行最多两列；根首页 Hero 无框左对齐。
- **顶栏品牌标**：`brand-mark.svg` 作 `mask`、以 `--navbar-fg` 上色；标签页用 `favicon.svg`。不直接用 favicon 做顶栏图标（SVG 内 `prefers-color-scheme` 会跟系统而非站点主题）。图标高 1.5rem，`margin-bottom: 0.375rem` 对齐汉字基线；窄屏先压搜索再省标题。
- **color-scheme**：浅色声明 `light`，深色由 `body.quarto-dark` 覆盖，避免系统偏好渗入控件与内嵌 SVG。
- **纯文本代码块**：与语言块共用 `--code-*`；`text` 不启用语言 token。
- **`.code-caption`**：次要说明色，紧贴对象；写作见 writing-quarto `authoring.md`。
- **可折叠答案**：`details.answer-disclosure` 默认收起，边框圆角与卡片一致。

### 页面列宽与正文宽度

- `grid.body-width` 是正文列上限；sidebar + body + margin + gutter 合计不得超过目标视口。取值只在 `_quarto.yml`。
- `--content-width` 只限正文容器；禁止再用 `75ch` 二次限宽。≤991.98px 左栏浮层必须不透明实底（见 `cpp-quarto-sidebar-overlay-v1`）。

### 字体栈（三处同步）

自托管 OFL（`assets/fonts/` + `css/fonts.css`）：Sans 为 Fixel → WenKai Screen；Mono 为 Bright Code → WenKai Screen。高亮主题与活跃 palette `meta.md` 同步（github 包为 github-light/dark）。改字体须同步 SCSS、tokens、fonts、OFL、资产与 `check_layout.py`；单页最多 5 个字体文件、预算 1.6 MB。

### 正文字号

| 元素 | 值 |
|---|---|
| 正文 | 16px / lh 1.75 |
| H1（title） | 32px / w600 |
| H2 | 24px / w600 / mt 2.75rem mb 0.9rem |
| H3 | 20px / w600 / mt 2rem |
| 代码块 | 15px / lh 1.75 |
| 行内代码 | 0.875em |
| Callout 正文 / 标题 | 16px / 15px w600 |

正文与代码行高 1.75（CJK 阅读舒适带，2026-09 自 1.65 上调）。章节分隔用 Quarto 默认 h2 下边框，qmd 不写 `---`。

### 设计来源

Quarto Book 三栏；生产唯一色板 `palettes/github`：亮色对齐 Primer Light Default，暗色对齐 Primer Dark Dimmed（软暗色）。实现为 Bootstrap cosmo/darkly + 主题 CSS。

## 主题结构与组件规则

官方字段见 Quarto HTML format reference。下列路径与装配顺序是本项目契约。

### 文件职责

| 文件 | 放什么 | 不放什么 |
|---|---|---|
| `palettes/<name>/theme-*.scss` | `$primary`、`$callout-color-*` 等 | 组件规则 |
| `palettes/<name>/tokens.css` | 明暗语义颜色 | 结构尺度、选择器 |
| `palettes/<name>/meta.md` | 来源、highlight 映射 | 运行时 CSS |
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
- 正文链接用 `--link-color` + 细下划线。
- 表格无外框/斑马纹，表头底线 + 行 hairline。
- 导航「Search / Source Code」英文默认值由 `includes/footer.html` 按 zh 同义补齐，只替换英文原文。

### 新增 callout

1. 活跃 palette `tokens.css` 加 border/bg（亮暗各一对）。
2. 同 pack `theme-*.scss` 加 `$callout-color-*`。
3. `callouts.css` 加 `.callout.callout-<name>`。
4. 新语义写入本节令牌索引。

### 校验与高亮契约

- `check_layout.py` 校验令牌与布局；发布用 `1280/768/390` 明暗与触屏、窄屏浮层。
- 高亮由 `_quarto.yml` 提供且与 palette `meta.md` 一致；CSS 不覆盖语法 token 色。
- `text` 与语言块共用字体尺度；标题块用 `.code-with-filename`。
- `check_dom_contracts.py`：C0 palette↔highlight；复制按钮兄弟 DOM；触屏/打印；favicon；Mermaid SVG。
