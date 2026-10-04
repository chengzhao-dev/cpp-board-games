---
kb_id: "bg-mermaid-conventions-v1"
title: "Mermaid 图表渲染约定"
domain: "quarto-writing"
subdomain: "rendering"
tags: [mermaid, diagrams, rendering, quarto]
level_range: [0, 5]
dependencies: ["bg-quarto-conventions-v1"]
created: "2026-09-28"
updated: "2026-09-30"
chunk_strategy: "semantic_heading"
estimated_tokens: 600
---

# Mermaid 图表渲染约定

本文件记录 `content/**/*.qmd` 中 Mermaid 图表的渲染层约定；是否使用图表的门槛见 `writing-quarto` 技能的 P0 硬约束，主题侧取色与排版守卫见 `designing-theme` 技能的 `assets/theme/css/mermaid.css`。

Mermaid 只承担流程图、分层图与调用链；坐标轴类网格图（棋盘行列、二维下标）走 `coords_grid.py` 加 `{python}` 可执行单元，分工与写法见标识 `bg-coords-diagram-v1` 的知识文件，禁止用 Mermaid 硬画网格。

## 只使用 {mermaid} 围栏

Quarto 只执行 ` ```{mermaid} ` 属性围栏；plain 的 ` ```mermaid ` 围栏被当作普通代码块，渲染结果是语法高亮的源码而不是图。`verify_content.py` 在禁用词扫描中拦截 plain 围栏。

渲染核对方法：`quarto render` 后检查 `_book` 中对应 HTML 应出现 mermaid 图表容器（`mermaid-js` 或 `quarto-diagram` 类名），不应出现 `sourceCode mermaid` 高亮代码块。

## 块首固定 init 指令

每个 `{mermaid}` 块的第一行写：

```text
%%{init: {"fontFamily": "Fixel Text, LXGW WenKai Screen, system-ui, sans-serif"}}%%
```

mermaid 用 init 指令中的字体测量标签宽度，页面 CSS 按 `--ui-font` 渲染文字；两者使用同一字体栈，标签测量与最终渲染一致，避免文字溢出或留白。`mermaid.css` 的排版守卫依赖这一约定。

## 节点与边标签写法

- 节点标签一律放在双引号内，例如 `A["标签文字"]`，不依赖裸文本解析；
- 节点标签只画抽象层名，不把职责明细塞进节点括号；逐项职责用图后列表交代；
- 标签中不使用全角冒号与直角引号「」承载分隔语义；并列用顿号，补充说明用全角括号；
- 边标签写在 `-- 文字 -->` 中，保持简短中文；
- 图表方向以窄屏可读为底线：分层结构用 `TB`；单向推进链节点数 ≥ 5 时默认 `TB` 单列，一屏过高时拆成两张图（如「01–05」「06–10」各一张），禁止长 `LR` 挤爆视口；节点数 ≤ 4 的短链可用 `LR`；
- 单图节点建议 ≤ 6，一图一事不变，超出优先拆图而不是压缩标签；
- 图后不设 `>` 引用块图注：图注内容并入图后列表的引言句或正文句，图表之后直接跟职责列表，不让图独立承载全部信息。
