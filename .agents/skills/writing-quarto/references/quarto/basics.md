# Quarto 基础（Book 项目）

本文件是 Quarto Book 项目结构、YAML front matter、章节标题约定的**规范唯一出处**。其他文件提到这些约定时一律引用本文件，不重复陈述。`format: html` 的选项语义与失效边界归 `rendering-and-output.md`，本文件不复制。

> 速查：`.qmd` = YAML front matter + Markdown 正文 · `title:` 与 `# H1` 二选一 · `index.qmd` 必须存在 · Book 输出 `_book/` · `part:` 分组章节

## .qmd 文档结构

一个 `.qmd` 文件由两部分组成：

```yaml
---
title: "文档标题"
description: "一句话说明"
format: html
---

正文内容。
```

- **YAML front matter**：文档元数据与配置，位于文件顶部 `---` 之间。
- **Markdown 正文**：标准 Markdown + Quarto 扩展（divs、spans、callout、交叉引用等）。

## 常用 front matter 字段

| 字段 | 作用 |
|---|---|
| `title` | 标题；侧边栏、TOC 与章节号均取自它 |
| `description` | 页面描述。本仓规划页用它承载一句定位；着陆页（`index.qmd`）的 description 会渲染为可见引导段 |
| `format` | 输出格式（本仓统一 `html`），可写对象形式配置子选项 |
| `lang` | 语言，本仓在 `_quarto.yml` 统一设 `zh` |
| `toc` | 目录（本仓统一在 `format: html` 下设置，见 `rendering-and-output.md`） |

## 常用命令

```bash
quarto render 文档.qmd            # 渲染单个文档
quarto preview 文档.qmd           # 本地预览（实时刷新）
quarto render                     # 渲染当前项目全部内容
```

`quarto render` 必须在仓库根目录执行，在其他目录执行会静默不渲染。

## Quarto Book 项目（本仓所用格式）

本仓使用 **Quarto Book**（`project: type: book`）。核心配置已对齐仓库 `_quarto.yml`：

```yaml
project:
  type: book

book:
  title: "C++ 棋盘游戏实践"
  sidebar:
    collapse-level: 1
  chapters:
    - index.qmd
    - part: content/tic-tac-toe/index.qmd
      chapters:
        - content/tic-tac-toe/01-scope-and-principles.qmd
```

- **`index.qmd` 必须存在**，作为 Book 首页/入口。
- **`part:` 指向游戏落地页**（如 `content/tic-tac-toe/index.qmd`），产生分组标题；新增游戏时先建游戏落地页，再加 part。
- 章节可放子目录，在 `chapters` 写相对路径；`_quarto.yml` 的章节顺序与游戏落地页的阅读顺序保持一致。
- 渲染：`quarto render`，Book 默认输出到 `_book/`。

### 根首页与游戏落地页的链接边界

根首页和游戏落地页分别完成一次选择，不能越过对方直接承担章节导航。

- 根 `index.qmd` 只展示 `content/<game>/` 这一层：当前游戏用高光 landing-card（带 CTA，按由易到难排序），后续棋类用 `.coming-soon` 占位卡（无链接，样式自带「规划中」角标）。
- 游戏 `content/<game>/index.qmd` 只展示本游戏已发布的正文页面：短引言 + `feature-grid` / `landing-card`，每卡是章节 title 链接 + 一句职责，按 `_quarto.yml` 阅读顺序排满全部章节。
- 新增游戏时先写游戏落地页，再在根首页增加分组；根首页不直接链接游戏内正文页面。

## 章节标题约定（规范，唯一出处）

章节标题**二选一**：用 YAML `title:` **或**顶层 `# H1`，二者皆有时同文本必然重复渲染，并造成章节结构错乱。推荐用 `title:`，小节从 `##` 开始：

```markdown
---
title: "章节标题"
---

开篇说明写正文普通段落（1-3 句），普通章节的 `description` 只进 `<meta>`。

## 第一个小节
正文。
```

- 页面内不得再出现顶层 `# H1`。
- **标题层级**：`##` 表示阅读阶段、范围或一个可验收任务，`###` 表示该阶段中可独立完成或观察的子任务。正文最多到 `###`，禁止 `####` 及更深标题。
- `###` 只用于源码阅读、验证、可选分支、排错症状等拥有独立动作或观察结果的内容。只有一两句话的解释并入相邻段落，不为目录对称强行拆分。
- 根首页、游戏落地页的卡片标题可以保留 `###`，那是导航组件的视觉层级，不改变正文最多三级的约束。
- 归并或改名标题前先检索 `@sec-` 与 `#anchor`，避免破坏交叉引用。标题字数与形式的建议值见知识库 `bg-file-title-naming-v1`。

## 输出结构

单个文档渲染后产生 `.html` 与 `_files/` 伴随目录；Book 项目统一输出到 `_book/`。如希望单文件自包含 HTML，用 `embed-resources: true`（见 `rendering-and-output.md`）。

## 延伸

- 正文结构、代码块/终端约定与文档元素：`authoring.md`
- 外观配置与渲染排错：`rendering-and-output.md`
- 发布 GitHub Pages：`.agents/skills/shipping-github/references/github-pages.md`
- 页面宽度与视觉依据：知识库 `bg-section-focus-density-v1`
