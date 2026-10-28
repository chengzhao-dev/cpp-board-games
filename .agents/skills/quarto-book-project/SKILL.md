---
name: quarto-book-project
description: 记录《C++ 棋盘游戏实践》的项目级约定：书名、读者、井字棋章节对照、术语出处、检查命令、主题与过滤器路径；通用写法仍由插件的 writing-quarto 与 designing-theme 负责
---

# 项目级 Quarto Book 约定

本文件只写本书自己的事实。通用写法、章节骨架、标题分层和主题规则由插件 `writing-quarto` 与 `designing-theme` 负责，这里不复制。

## 书名与读者

- 书名：**C++ 棋盘游戏实践**（`_quarto.yml` 的 `book.title`）。
- 一句话定位：用一局可下完的终端井字棋，把 C++ 工程、构建和测试串成一条读者能自己走完的路线。
- 目标读者：会一点 C++ 语法、想从零走完一个工程的学生与自学读者；不预设 CMake、CTest、终端工具链经验。
- 本书不覆盖：C++ 语言机制的课程式讲解（那属于另一个仓库的正文）；棋盘游戏的历史与文化。

## 章节对照

- 章节顺序的唯一来源：根 `_quarto.yml` 的 `book.chapters`；每章的类章或能力章、关键对象、`title` 与二级标题在 `writing/chapter-map.md`。
- 本书关闭小节编号，互引一律用 `.qmd` 相对路径链接，不写 `@sec-`；书名里的「第 N 章」编号指称也不使用。格式选项只写在根 `_quarto.yml`，章节 YAML 只放 `title` 与页面 class。
- 目录布局：`content/tictactoe/<NN>-<chapter>.qmd`；读者侧入口 `content/tictactoe/index.qmd`（散文页，不是第十一章），根首页是 `index.qmd`。
- 改文件名时同轮同步 `_quarto.yml`、`writing/chapter-map.md`、正文 YAML 的 `title`、已有链接，以及 `checks.json` 的 `chapter_titles`。

## 术语

- 统一术语与替换规则：`glossary/project-terms.md`；禁用与替换词：`glossary/forbidden-terms.md`。
- 本书的定稿写法只在这两份文件里维护，本文件不重复词表。

## 检查命令

统一由 `config/config.toml` 的 `python` 取解释器（最低 3.12）；解释器缺失就停止，不回退 PATH。

- 内容检查：`python .agents/scripts/checking-book.py`，调用插件 `writing-quarto` 的 `verifying-content.py`，并读取本目录 `checks.json` 的项目规则。
- 改动域检查：改过 qmd 跑上面的检查；改过 `games/` 另跑 `python .agents/scripts/building-wsl.py <game>`。
- 渲染：在仓库根执行 `quarto render`。渲染后核对 HTML 用 `quarto_render_check`（`qmd_path` 传当前章节，`dry_run: true` 最多 2 次，`false` 最多 1 次）。
- 编码与行尾：qmd、YAML、CSS 跟根 `.editorconfig` 与 `.gitattributes`；UTF-8 无 BOM、LF，`.bat`/`.cmd` 用 CRLF。

`checks.json` 的三个字段：`forbidden_terms` 是正文禁用词（对每行做子串匹配，代码围栏也算）；`chapter_titles` 是「文件路径 → 标题必须包含的子串」；`fragment_prefixes` 登记本仓的路径前缀。

## 主题与过滤器路径

- Quarto 读取的书内主题副本：`theme/`（`css/`、`includes/`、`palettes/`、`assets/`）；`_quarto.yml` 只引用这份相对路径；过滤器在 `filters/answering-disclosure.lua`。
- 权威来源在插件的 `skills/designing-theme/assets/theme/`；改共享样式时同轮改插件源与书内副本，渲染只消费书内副本。
- 代码块里的 C++ 注释按插件 `developing-cpp` 的注释规则书写，本书不再留插件副本。

## 与通用技能的分工

- 通用写法、结构、标题层级、Mermaid 与主题规则：插件 `writing-quarto` / `designing-theme`；本书事实（书名、章节对照、术语、命令、路径）：本文件与 `writing/chapter-map.md`。
- 写章节前按 `writing-quarto` 读本文件，再读它指向的 `writing/chapter-map.md`。
