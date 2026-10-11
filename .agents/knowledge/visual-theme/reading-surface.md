---
kb_id: "bg-reading-surface-v1"
title: "阅读表面：字体、栏宽与强调"
domain: "visual-theme"
tags: [fonts, typography, layout, theme, readability, contrast]
level_range: [0, 5]
dependencies: []
created: "2026-10-10"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 1500
---

# 阅读表面：字体、栏宽与强调

本文件回答这本书的阅读表面为什么这样定：正文字体、正文栏宽、窄屏行为与加粗/链接颜色。怎么做（改哪一步、动哪个文件）见 `designing-theme` 技能的 `references/theme-spine.md`，数值与实现见 `references/theme-system.md`。本文件只放理由，与 cpp-notes 同源的部分若两仓后续分叉，以本仓为准。

## 正文为什么是 LXGW 的单一字面

中文保持霞鹜文楷路线（楷体），不换黑体：这本书是长时间连续阅读的技术书，楷体的笔画变化比几何无衬线更耐读；作者「文楷不适合超长正文」的评价针对的是屏幕上偏细的 Regular，不构成换字体的理由——用 Bright 的 Medium 解决偏细。

### 为什么合并成一份 Bright Medium

旧方案是「Fixel Text（拉丁）+ 文楷 Screen（中文）」双字体拼接：Fixel 是几何无衬线、没有 400 字重，与楷体的笔形对不上；两套西文与中文各算各的基线，混排节奏不一致。LXGW Bright 本身就是「Ysabeau Office（西文，齐线数字）+ 文楷中等笔画（中文）」的合并字体，一个文件解决拼接问题；全站只挂这一个字面，层级靠字号，标题请求 600 时在全站 `font-synthesis: none` 下仍落到这一份，不合成假粗体。

### 为什么不用文楷 Screen 与系统西文

文楷 Screen 是给「系统里已有 Segoe/Roboto」的场景准备的：它的度量对齐 Roboto、Medium 笔画标成 Regular。本站中西文都自托管，继续「文楷 Screen + 另一套西文」会回到双基线拼接。Bright Code 的西文是收窄的 Monaspace Argon（与汉字宽约 1:2），所以代码字体保持 Bright Code 不变。

### 代码西文与正文西文为什么不是同一个设计

代码块的西文是 Monaspace Argon，正文西文是 Ysabeau，两者不是一套——这是配对理由，不是待修缺陷：文楷等宽配别的西文时楷体与西文不协调，Argon 是上游作者认为与楷体风格最接近的等宽字，西文经收窄再缩至 90%，与汉字 advance 成 1∶2，代码列按 1∶2 对齐。字重表有意错位：Bright Code 的 Regular 对应文楷 Medium；主题子集已用 fontTools 读 name 表核对为 LXGW Bright Code Regular（OS/2 weight 400），代码里的汉字笔画与正文同一档，不是「代码更细」。因此不因「代码西文与正文西文不同源」换字体，也不为对齐西文改用黑体路线的等宽字。

### 排除的候选

Inter、思源黑体、JetBrains Mono、Cascadia、Iosevka、Inconsolata 均不采用：前两者是黑体路线（与「中文保持楷体」冲突），后四者是代码字体（代码已有 Bright Code）。Roboto 与 Segoe UI 是 Apache/微软许可，不满足本仓「只收 OFL 到 `assets/fonts/`」的政策。旧式数字（Ysabeau Infant 一系）不适合和汉字混排，不用于这本书。

## 栏宽为什么是 872px（内容列 840px）

Bright Code 在 16px 下每个 ASCII 字符前进 8px，代码区内边距左右各 16px、边框左右各 1px，100 列代码需要 100×8+32+2=834px 的内容宽。Quarto 会从 `body-width` 中再减去两侧各 1rem 的栅格内边距（内容列 = body-width − 32px），因此 `body-width` 取 872px，内容列 840px、代码文本区 806px，留约 6px 余量。栏宽随代码列宽走而不是随显示器走：宽视口只增大外侧留白，正文行长保持在可读范围（WCAG 建议不超过约 80 个拉丁字母或 40 个汉字）。标题下的 description 副标题与正文段落同一内容列，不再用 `ch` 二次限宽（Bright 的西文是比例字体，`ch` 只量出半个汉字宽，会先于正文折行）。

## 窄屏为什么只让代码块横向滚动

125%/150% 缩放后 CSS 像素变少，栏宽由 Quarto 按断点缩小；此时若代码跟着折行，同一行代码在宽窄屏上的断点不同，读者对照截图与本地输出时会错位。固定 `white-space: pre` + 块内 `overflow-x: auto`，代码行在任何视口下保持完整；正文段落照常折行。打印时横向滚动不存在，打印样式把 `pre` 恢复为折行，屏幕规则不动。内容列 840px 只比 834px 多 6px：若 Windows 滚动条或亚像素取整吃掉余量导致第 100 列被裁，再把 `body-width` 升到约 880px，不预先加宽。

## 加粗为什么仍合成且不用链接色

书里的 `**` 大量用作列表小标题（「出错的原因」「正确的做法」）和行内强调；Bright 只有一个字面，若同时去掉合成加粗和强调色，这些字与正文无差别。因此：`strong` 保留 `font-synthesis: weight` 的合成（全站唯一放开点），配一个比正文更实的强调色（亮更深、暗更亮），且强调色不取链接蓝——加粗必须和链接在明暗两套下都能区分。列表里独占一段的 `**` 小标题保持正文色块级形态，避免一列蓝标题；代码文件名、行内代码、kbd 各用自己令牌，不被强调色或链接色串染。

## 颜色与对比度的取值依据

色板不换：亮色 Primer Light、暗色 Primer Dark（Dimmed 软暗）。callout 条色收敛到页面已有功能色（链接蓝、成功绿、低饱和琥珀与红、Primer 紫），浅底用同色 8%–12% 透明。文本对比度按 WCAG 2.2 的 1.4.3（4.5:1）校验：正文、强调、链接、13px 表头、14px 图注与代码标题在各自底色上低于 4.5:1 时升到更实的一档，不改成纯黑或纯白，也不借用链接蓝。

## 已记录的偏低对比项

暗色代码高亮的注释色已抬到 `#9AA1AB`（本书代码底 `#2D333B` 上约 4.89:1，达到 4.5:1，仍暗于次要文字 `#B1BAC4` 的 6.49:1，注释看起来比正文淡）；旧值 `#768390`（官方 Dimmed 注释色，约 3.29:1）不再使用。亮色正文行号用 `#57606A`、警告琥珀用 `#8A5C00`，是按同一 4.5:1 口径从原值升档的结果。

## 明暗代码色跟哪一对 GitHub 主题

页面色和语法色来自同一对 Primer 主题：亮色 Primer Light Default、暗色 Primer Dark Dimmed。代码语法色不使用 Quarto 内置的 `github-light` / `github-dark`——那是 2020 年的 skylighting 主题，亮色按白底 `#FFFFFF` 设计、暗色按早已弃用的旧深色底 `#24292E` 设计，叠在本仓的代码底（亮 `#F6F8FA`、暗 `#2D333B`）上是两代主题错层；语法色改由色板目录的 `highlight-light.theme` / `highlight-dark.theme` 提供，取色自 Primer 当前 prettylights（primer/github-vscode-theme 的 light 与 dark-dimmed），`BackgroundColor` 与 `--code-bg` 相同，CSS 仍不覆盖 `span` 色。

三处允许偏离官方 prettylights，其余照抄：暗色普通文本用 `#CDD9E5`（与 `--code-fg` 和纯文本块一致，不用官方 `#ADBAC7`）；暗色注释一族从官方 `#768390`（约 3.29:1）抬到 `#9AA1AB`（约 4.89:1）——中文注释是这本书的阅读对象，必须过 4.5:1；暗色关键字一族改用 Dark Default 的关键字红 `#FF7B72`（约 5.05:1，官方 Dimmed 红 `#F47067` 在本书代码底上约 4.47:1 贴线）。亮色整表取 Primer Light：注释 `#57606A`（约 6.0:1，与行号同档）、关键字 `#CF222E`（约 5.03:1）、普通文本 `#1F2328`（与 `--code-fg` 一致），旧表的 `#6A737D` 注释与 `#D73A49` 关键字都不再用。

不把暗色整页换回 Dark Default（`#0D1117`）的原因：近黑底上注释对比更好（约 6.15:1），但近黑正是本书从 Dark Default 迁到 Dimmed 的原因——中文长文的正文面积大于代码，长文光晕比代码对比更伤阅读；所以保留 Dimmed 页面，注释对比用抬一档灰补齐，关键字用 Dark Default 的红补齐，不整页翻案。
