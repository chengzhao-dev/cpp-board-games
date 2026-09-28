---
name: designing-theme
description: 维护 Quarto Book 主题资产（css、scss、字体、palette）；调整页面样式、颜色或字体时使用
metadata:
  short-description: 维护共享 Quarto 主题
---

# Skill: designing-theme

维护 `.agents/skills/designing-theme/assets/theme/` 下的主题资产，与 cpp-notes 仓库共享同一套文件。

## 适用场景

- 调整颜色、字体、间距、导航、Callout 或落地页样式。
- 新增 palette 或页面组件样式。
- **不适用**：`.qmd` 正文写法（转 `writing-quarto`）、代码内容（转 `cpp-development`）。

## 任务路由

| 任务 | 读取 |
| --- | --- |
| 色板接线与暗色分层 | `assets/theme/palettes/github/meta.md` |
| 结构尺度令牌 | `assets/theme/css/tokens.css` 头注释 |

## P0 硬约束

1. 主题资产被根 `_quarto.yml` 以相对路径直接消费，移动或改名必须同步 `_quarto.yml`。
2. `css/` 组件规则不写色值，语义颜色只来自 `palettes/github/tokens.css`；`css/tokens.css` 只放结构尺度令牌，明暗共用。
3. 资产与 cpp-notes 共享，改动需评估两仓同步。
4. 修改主题或 `_quarto.yml` 后在仓库根目录整本 `quarto render`，验证明暗两套主题；布局调整优先修改 grid 与共享节奏，不用页面局部样式堆叠间距。

## 完成判据

- [ ] `quarto render` 通过，明暗主题下页面无错位或对比度问题。
- [ ] 代码块 filename 标题在长路径输入下不撑破容器，窄屏仍可读。
- [ ] 两仓主题资产保持一致，或差异已记录。
