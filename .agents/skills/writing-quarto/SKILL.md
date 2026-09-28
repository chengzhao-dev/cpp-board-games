---
name: writing-quarto
description: 使用 Quarto Book HTML 展示设计、演示和学习过程；编写或修改 .qmd 章节时使用
metadata:
  short-description: 编写中文 Quarto 章节
---

# Skill: writing-quarto

承载 `.qmd` 章节的写法流程与 Book 结构约定。通用 how 在 `references/`（先读），本仓差异与依据在知识库（按 `kb_id` 定点取用），两层都不复制进本文件。

## 适用场景

- 新建或修改 `content/**/*.qmd` 章节、`index.qmd` 或 `_quarto.yml`；渲染验证与产物契约走下表脚本。
- **不适用**：改主题样式（转 `designing-theme`）、游戏语义与 C++ 内容（转 `cpp-development` / `game-design`）。

## 任务路由

| 任务 | 读取 |
| --- | --- |
| 中文写作最高优先规则（句长、术语、降噪、删改） | `references/zh/writing-principles.md` |
| 章节骨架、页面类型与收尾 | `references/zh/chapter-writing.md`；差异判定见知识 `bg-chapter-page-pattern-v1`、`bg-engineering-storyline-v1` |
| 小节主线、密度与 Callout 下沉 | `references/zh/section-focus-and-density.md`；依据见知识 `bg-section-focus-density-v1` |
| Quarto 结构、front matter、标题约定与渲染取值 | `references/quarto/basics.md`、`references/quarto/rendering-and-output.md`；字数建议见知识 `bg-file-title-naming-v1`，Mermaid 围栏见 `bg-mermaid-conventions-v1` |
| 元素写法（片段 filename、Callout、链接） | `references/quarto/authoring.md`；细则见知识 `bg-qmd-element-cases-v1`、`bg-quarto-conventions-v1` |
| 命令、输出与常见错误三步流 | `references/quarto/terminal-validation.md` |
| 段落拆分、凑字数禁令、衔接、语气、篇幅与术语 | 知识 `bg-paragraph-list-style-v1`、`bg-paragraph-cohesion-v1`、`bg-chinese-voice-register-v1`、`bg-content-budget-v1`、`bg-terminology-v1`；改写对照见 `bg-chinese-style-cases-v1` |
| 内容规范核对与增量校验 | `.agents/skills/governing-agents/scripts/run.py check/verify`（verify = verify_content 的 --changed/--paths 包装）；自测答案折叠由 `scripts/answer-disclosure.lua` 提供（`_quarto.yml` 顶层 `filters:` 注册） |

## P0 硬约束

1. 根目录 `_quarto.yml` 是 Book 章节顺序的唯一来源。
2. `README.md` 只做项目入口，完整设计和演示放 Quarto。
3. 页面标题由 YAML `title:` 提供，正文从 `##` 开始，最多到 `###`。
4. 含代码块、列表或表格的小节按「引言 → 块 → 结尾（可选）→ Callout（可选）」组织，一段只推进一个对象。
5. 展示 `games/<game>/` 源码默认内联摘录关键片段：逐字摘录，省略处直接省略不写标记行，每处注释不超过 2 行；include 仅限完整展示的短文件且必须包在带语言标注的围栏代码块内。
6. 复杂关系才使用 Mermaid；图表一律使用 `{mermaid}` 属性围栏，plain ```` ```mermaid ```` 围栏不会渲染。
7. 修改 QMD 或 Quarto 配置后在仓库根目录运行 `quarto render`（在其他目录执行会静默不渲染）。
8. 同段不堆砌流程名词；对照表用关系句承接；相邻段落不得各成独立说明书。禁用词以 `scripts/verify_content.py` 词表为准。
9. 大规模正文重构先取全量语料：`scope` 命中范围 → 本 SKILL → 其路由指向的全部参考与知识文件、校验脚本读完再动笔，禁止只按任务清单的增量条目改写。

## 完成判据

- [ ] `run.py check --profile fast`（或 `run.py verify --changed`）与 `quarto render` 通过；改动渲染产物语义时补 `--profile book`。
- [ ] 章节骨架与 `references/zh/chapter-writing.md` 一致，游戏章差异与知识文件相符。
- [ ] qmd 验证只跑 `verify_content.py` 与 `quarto render`，不截图 PNG、不做视觉评审。
