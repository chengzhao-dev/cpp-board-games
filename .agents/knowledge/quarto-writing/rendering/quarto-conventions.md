---
kb_id: "bg-quarto-conventions-v1"
title: "Quarto 渲染与链接约定"
domain: "quarto-writing"
subdomain: "rendering"
tags: [quarto, include, github-links, rendering]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-09-27"
chunk_strategy: "semantic_heading"
estimated_tokens: 700
---

# Quarto 渲染与链接约定

本文件记录本仓库 `content/**/*.qmd` 的渲染层约定，供 Agent 编写和评审章节时使用；写作层骨架与元素规则见 `writing/` 子域。

## include 短代码必须包在围栏代码块内

展示源码默认**内联摘录片段**（片段规则见标识 `bg-qmd-element-cases-v1` 的知识文件，生效）；include 是可选手段，仅用于确实需要完整展示且很短的文件。仍在使用 include 时，必须包在围栏代码块内。

`{{< include <文件> >}}` 裸用（不包代码块）时，Quarto 把文件内容当作 Markdown 正文渲染——换行丢失、`#===` 横幅被解析为 Markdown 标记，最终在 HTML 中变成一串 `<p>` 段落，代码结构完全破坏。

正确写法是包在带语言标注的围栏代码块内（[官方文档](https://quarto.org/docs/authoring/includes.html)给出了同样模式）：

````markdown
```cmake
{{< include ../../games/<game>/<stage>/CMakeLists.txt >}}
```
````

- include 路径相对于 qmd 文件所在目录解析（`content/tictactoe/` 下用 `../../games/...` 指向仓库根的 `games/`）。
- 语言标注决定语法高亮：CMake 用 `cmake`，C++ 用 `cpp`，Shell 用 `bash`。
- 新增或修改 include 后必须 `quarto render` 并检查 `_book` 中对应 HTML：嵌入内容应出现在 `<pre class="sourceCode ...">` 代码块中，而不是 `<p>` 段落里。
- include 展示的是 `games/` 下真实源文件，渲染问题只修 qmd 的包裹方式，不改被引用的源文件。

## 链接使用约定

qmd 指向仓库内路径的链接仍**一律使用 GitHub 绝对链接**，不使用相对路径链接；锚文本与外链按下列规则执行。

- 章节互引：用章节 title 作链接文字，`.qmd` 相对路径（规则见标识 `bg-terminology-v1` 的知识文件）；
- 仓库内目录：`https://github.com/chengzhao-dev/cpp-board-games/tree/main/<路径>`，锚文本用简短中文描述（如「最小工程目录」）；
- 仓库内文件：`https://github.com/chengzhao-dev/cpp-board-games/blob/main/<路径>`，锚文本用中文描述或专名文件名（如「构建规则 CMakeLists.txt」「main.cpp」）；
- 锚文本不写路径结构：`games/tictactoe/01-cli-game/` 这类层级不进锚文本；完整路径只出现在 GitHub URL、目录树和确需精确指路的行文里，不进代码块 filename（filename 一律短名，见标识 `bg-qmd-element-cases-v1` 的知识文件）；
- 行文叙述少用行内代码路径指代目录：正文指向仓库内目录或文件时，首次出现处用中文锚文本的 GitHub 链接，此后用中文短指称；行内代码路径只保留在目录树与目录映射表格，正文里的实现目录用 GitHub 链接（模板见标识 `bg-chapter-page-pattern-v1` 的知识文件）；
- 外部官方文档非必要不链接：命令与概念默认用行内代码加正文一句话讲清；引用第三方内容注明出处与章末参考资料清单是外链的合法位置；
- 全路径在行文首次出现后改用中文短指称（工程目录、一键脚本、构建规则），不重复全路径；
- base 与 cpp-notes 同账号；仓库推送远端之前链接暂时 404 属预期，推送后即生效；统一格式的代价是离线阅读仍指向 GitHub，仓库改名需全量替换（首次提交前固定 base 即可）；
- 跨仓读者链接只用两个稳定 base：`https://github.com/chengzhao-dev/cpp-board-games` 与 `https://github.com/chengzhao-dev/cpp-notes`；目录用 `tree/main/<路径>`、文件用 `blob/main/<路径>`，不写姊妹仓的本机路径；教学内容互补与同步边界见两仓 `.agents/skills/governing-agents/references/structure.md` 对照表；
- 跨仓锚文本禁止「写法依据见 / 依据见 / 机制见 / 选型见 / 承诺见 / 用法见 / 陷阱见」式；默认不挂链，可选尾置用「若要系统阅读…」；细则见 `writing-quarto` 技能 `references/zh/chapter-writing.md`「叙事范围」；
- 新增链接后渲染检查 HTML：锚文本与 URL 对应、无相对路径仓库链接混入（章节互引除外）；
- 正文与代码块 filename 标注不引用 `.agents/` 内部路径：读者所需的解释就地写清，仓库内路径一律链 GitHub；内部知识路径的读者/作者分离依据见标识 `bg-comment-style-v1` 的知识文件。

## 章节结构约定的归属

章节骨架（无标题引言、任务序列、常见错误、自测问题、本章回顾）、标题字数硬限与教学元素写法统一由 `writing/` 子域维护，按标识查阅：

- 见标识 `bg-chapter-page-pattern-v1` 的知识文件：六段骨架、引言职责边界、H2/H3 门槛、术语策略；
- 见标识 `bg-file-title-naming-v1` 的知识文件：title 与二三级标题的字数硬限（动词短语、无冒号）；
- 见标识 `bg-qmd-element-cases-v1` 的知识文件：代码块 filename 标注、盒子密度、Callout、目录树、多命令块；
- 见标识 `bg-chinese-style-cases-v1` 的知识文件：句段、措辞替换与术语节奏；
- 见标识 `bg-section-focus-density-v1` 的知识文件：小节主线收束与信息分层。

本文件只维护 include 包裹与链接使用两条渲染层约定。
