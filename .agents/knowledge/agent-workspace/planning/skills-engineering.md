---
kb_id: "bg-skills-engineering-v1"
title: "技能工程与渐进披露"
domain: "agent-workspace"
subdomain: "planning"
tags: [skills, agents-md, progressive-disclosure, scripts]
level_range: [0, 5]
dependencies: ["bg-retrieval-governance-v1"]
created: "2026-10-02"
updated: "2026-10-02"
chunk_strategy: "semantic_heading"
estimated_tokens: 700
---

# 技能工程与渐进披露

本文件记录本仓相对 Agent Skills 规范的取舍。流程仍以 `governing-agents` 的 `SKILL.md` 与 `refactor-guidelines.md` 为准，本文件不复制步骤。

## 三层加载

启动时只注入每个技能的 `name` 与 `description`。`description` 只回答做什么、何时用，不写步骤；步骤写进正文会让模型跳过 `SKILL.md`。命中后再读正文。`references/`、`scripts/`、`assets/` 按路由再读。脚本执行后只把短输出放进上下文，不把脚本源码整篇读入。

根 `AGENTS.md` 只放每会话都会用到、删掉就会做错的约束。专项流程留在技能里。

## 与规范的有意差异

规范建议 `SKILL.md` 少于约 500 行。本仓 L1 更紧，约 45 行、3000 字符，默认只警告。根 `AGENTS.md` 保持远低于 150 行。

规范希望从 `SKILL.md` 到参考文件只隔一层目录。本仓按性质放在 `references/zh/`、`references/quarto/`、`references/stages/`。路由表直接指向叶子文件，对模型仍是一跳。不把这些目录拍平。

不使用规范里的可选字段 `allowed-tools`，也不使用非规范的 `disable-model-invocation`。

不在子目录再放 `AGENTS.md`。宿主会沿目录拼接指令，同一条规则会被注入多次。

## 两仓技能不互相覆盖

本仓的 `cpp-development`、`game-design`、`python-tooling` 讲工程用法。cpp-notes 的 `writing-cpp` 讲语言机制。同名的治理与写作技能可以字面不同，差异以 `structure.md` 对照表为准。改一边之前先看那张表，不整文件覆盖。
