# HTML 输出与渲染排错

## HTML 输出配置

> 速查：外观选项集中在根目录配置的格式块下 · 目录收至三级标题放右侧 · 本仓不用行号、代码块不折叠。自测答案使用 `.answer` 并渲染为原生 details

选项语义、作用域层级与生效边界的唯一出处是本文件与知识库 `bg-section-focus-density-v1`（宽度与节奏）；本文件只留本仓的取值和写作口径：

```powershell
& .agents/skills/governing-agents/scripts/run.ps1 kb-search "正文列宽度" --domain quarto-writing
```

### 本仓的现行取值

全部写在根目录 `_quarto.yml` 的 `format: html:` 下，章节 front matter 不重复设置：

| 选项 | 取值 | 备注 |
|---|---|---|
| `theme` | `light: [cosmo, palettes/github/theme-light.scss]` + `dark: [darkly, …]` | 内置主题与项目样式叠加，顺序决定覆盖关系 |
| `highlight-style` | `light: github-light` + `dark: github-dark` | 明暗分别指定，与 `palettes/github/meta.md` 同步，语义颜色交给引擎 |
| `filters` | `.agents/skills/writing-quarto/scripts/answer-disclosure.lua`（顶层 `filters:`） | 将正文 `.answer` 转为默认收起的原生 `details` |
| `toc` / `toc-depth` / `toc-location` | `true` / `3` / `right` | 右侧目录最多到 H3，窄屏会折叠，不作唯一定位手段 |
| `number-sections` | `false` | 因此标题不手填序号，见 `basics.md` |
| `code-copy` / `code-overflow` | `true` / `wrap` | 长行换行，不让读者横向拖动 |
| `grid` | sidebar 272 / body 720 / margin 256 / gutter 1rem | 正文列约 45 个汉字，对齐 1280 视口 |
| `lang` | `zh` | 影响部分 HTML 行为与提示框默认词 |

本仓**不开启**代码行号（`code-line-numbers`）与代码折叠（`code-fold`）。站点 QMD 代码块使用 `{.语言 filename="标题"}`；Quarto 会把标题渲染为 `.code-with-filename`，外观与复制按钮位置由主题统一控制。filename 缺失由 `check_docs.py` 拦截，内容语义与篇幅由 `verify_content.py` 负责。

### 改动约定

1. 改 `format: html:` 任何取值都属于主题级改动，会触发整本渲染，先确认代价再走 `run.py render`。
2. 新增或删减 `.agents/skills/designing-theme/assets/theme/css/**` 组件样式表时，同步修改配置里的样式表清单，否则新样式不参与渲染。
3. 页面视觉问题（提示符配色、文件名条、术语色）改 `.agents/skills/designing-theme/assets/theme/**` 与设计令牌，不在文档里内联样式，也不改高亮配置。主题系统详见 `.agents/skills/designing-theme/references/theme-system.md`。
4. 流程图使用 `{mermaid}` 属性围栏，配色由主题样式控制。配置里不指定图表主题名；围栏与 init 指令细则见知识库 `bg-mermaid-conventions-v1`。
5. 拿不准选项名、默认值或嵌套层级时查官方参考页，不凭记忆写 YAML（入口见本文件 #8）。

### 验证

渲染后确认：目录深度与位置符合预期、明暗两套高亮都可读。渲染产物结构由 `run.py check --profile book`（layout/callouts/dom 三项）自动核对；页面宽度与视觉依据见知识库 `bg-section-focus-density-v1`。主题或目录看起来没生效时先硬刷新排除缓存，再核对选项嵌套层级。

## 渲染与发布排查索引
按症状查此表：每条只给可执行处置。行为成因与取舍的唯一出处是知识库，用
`& .agents/skills/governing-agents/scripts/run.ps1 kb-search "<症状关键词>"` 取用
（可加 `--domain quarto-writing`）。本文件不重复解释根因，只保留编号、症状与处置。

> 速查：内嵌资源用 `embed-resources` 且必须嵌在 `format: html:` 下 · 路径用相对、纯 ASCII · 拿不准 YAML 先查官方 `llms.txt` · callout 只用内置 5 类 · `{{< include >}}` 必须包在带语言名的围栏里

### 1. `self-contained` 已弃用

- **症状**：渲染出现 deprecated 警告。
- **处置**：改名为 `embed-resources: true`，并确认它嵌套在 `format: html:` 下而非顶层。

### 2. 渲染后仍有 `_files/` 依赖目录

- **症状**：目标是单文件 HTML，产物仍带伴随目录。
- **处置**：核对 `embed-resources` 的拼写、缩进与嵌套层级。由 JS 运行时加载的资源无法内嵌，属已知限制，不要再改配置。

### 3. 路径与资源 404

- **症状**：本地正常，发布后图片或资源打不开。
- **处置**：改用相对路径，不要写死 `https://...` 指向内部资源，核对文件名大小写，站点托管区分大小写。

### 4. 主题/TOC 不生效

- **症状**：改了 `theme:` 或 `toc:` 页面没变化。
- **处置**：先硬刷新（Ctrl+Shift+R）排除缓存，再确认两者位于 `format: html:` 下。TOC 只收录 `##` 及以下的真实 Markdown 标题，`**加粗**` 与裸 `<h2>` 不会进入。

### 5. 中文乱码/编码

- **症状**：中文变成乱码特征串，或文件带 BOM、行尾变 CRLF。
- **处置**：改 `.qmd` 或规范文档后先跑 `run.py check --profile fast`。失败时从 Git 可读版本恢复再重做修改，**不要**对已乱码文本反向转码。全仓库统一 UTF-8 无 BOM、LF（`.gitattributes` 约定）。
- **注意**：PowerShell 5.1 的 `Out-File`/`Set-Content -Encoding utf8` 会附带 BOM，需显式无 BOM 或改用 Python 写入。

### 6. 渲染失败排查顺序

1. 看完整报错，先判断失败阶段：YAML 解析、Lua 过滤器，还是代码执行。
2. YAML 阶段：核对缩进/冒号与选项嵌套层级。
3. 代码执行阶段：检查依赖是否安装、缓存是否过期。
4. 找不到单文件：确认在仓库根目录执行，`quarto render` 默认作用于整个项目。

### 7. 发布到 GitHub 但页面没更新 / 打不开 / 乱码

- **处置顺序**：先看 Actions 是否成功（失败查日志）→ 分支部署核对分支与目录 → `gh-pages` 方式确认推送成功且远端存在该分支 → 用 `GET /repos/:repo/pages` 核对 Pages 源配置（404 = 源从未配置，线上就是 404）→ 最后才考虑缓存或 CDN 延迟。
- **发布前拦截**：`pages.yml` 必须先跑 `run.py check --profile fast`（编码）与渲染后 `--profile full`（含 `check_book_output.py` 的产物 smoke：首页、charset、乱码特征、sitemap）。渲染成功不代表线上可读。
- **错误必须阻断**：workflow 里以**读回判定**收口——`POST`/`PUT /repos/:repo/pages` 尽力而为（`PUT` 成功返回 204），最后 `GET` 读回 source，不是 `gh-pages` `/` 即 `exit 1`，不允许降级成 warning。`GITHUB_TOKEN` 首次创建 Pages 可能 403，需一次性用 PAT 或在 Settings → Pages 手动启用；未认证的 `GET /pages` 恒为 404，不能当作「未启用」的判据。
- **发布架构**：Actions 渲染校验后推 `_book/` 到 `gh-pages`，Pages legacy 源 = `gh-pages /`，`gh-pages` 只由 Actions 更新。legacy 模式下 `GITHUB_TOKEN` 改不动 Pages 配置（403），读回判定只检测不自愈，漂移需 PAT 或手动改回。

### 8. 文档关键词速查（避免幻觉 YAML）

- **规则**：拿不准选项名、默认值或嵌套层级时不要凭记忆写 YAML，先查官方参考：
  - Quarto LLM 优化文档索引：`quarto.org/llms.txt`
  - 单页把 `.html` 换成 `.llms.md`（如 `https://quarto.org/docs/reference/formats/html.llms.md`）
  - 普通文档页：`https://quarto.org/docs/reference/formats/html.html`

### 9. 路径/名称含特殊字符导致渲染失败

- **症状**：`quarto render` 报 `recoverEncode: invalid argument` 类错误。
- **处置**：项目、目录、文件名一律纯 ASCII，连字符一律用普通 `-`（U+002D）。用 `.agents/skills/writing-quarto/scripts/check_ascii_names.py` 校验整个仓库。

### 10. YAML `title:` 与同文本 `# H1` 重复 → 页面出现两个标题

- **症状**：标题重复出现两遍，Book 章节结构错位。
- **处置**：章节标题**二选一**，用 YAML `title:` 后不再写同文本 `# H1`。规范唯一出处见 `basics.md`「章节标题约定」。

### 11. `---` 紧接段落 → 前一段被解析为 setext 二级标题

- **症状**：某段文字莫名变成大号 H2，TOC 出现意料外标题。
- **处置**：本仓约定小节前**不写** `---` 分隔线。YAML front matter 的 `---` 不受影响。

### 12. 自定义 `.callout-*` 类被静默丢弃 → 提示框退化成普通小节

- **症状**：源文件写了未登记的 callout 类，渲染后没有提示框，且块内标题混进右侧目录。
- **处置**：只用内置 `note`/`tip`/`warning`/`important`/`caution` 五类，标题写成 `::: {.callout-note title="中文标题"}`。语义映射见 `authoring.md`「Callout 提示框」。
- **自检**：渲染后跑 `run.py check --profile book`，`callouts` 项会扫描 `_book/**/*.html`。

### 13. `{{< include >}}` 引用代码文件未加属性围栏 → 乱码式排版、目录被污染

- **症状**：渲染出的脚本失去高亮与等宽底色，`#` 注释行变成大号标题，含 `*`、`_` 的行变成斜体或粗体，右侧目录多出假标题。
- **处置**：`{{< include >}}` 整体放进 `{.cpp filename="game_state.cpp"}` 形式的属性围栏，按扩展名选语言并把 `filename` 写成真实文件名短名，**没有一个例外**。规则见 `authoring.md`「代码与媒体」；include 的使用边界见知识库 `bg-quarto-conventions-v1`。
