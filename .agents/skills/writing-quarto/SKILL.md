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
| 工程叙事 vs 语言课禁令 | `references/zh/chapter-writing.md`「叙事范围」；依据见知识 `bg-project-decisions-v1`，改写对照见 `bg-chinese-style-cases-v1` |
| 小节主线、密度与 Callout 下沉 | `references/zh/section-focus-and-density.md`；依据见知识 `bg-section-focus-density-v1` |
| Quarto 结构、front matter、标题约定与渲染取值 | `references/quarto/basics.md`、`references/quarto/rendering-and-output.md`；字数建议见知识 `bg-file-title-naming-v1`，Mermaid 围栏见 `bg-mermaid-conventions-v1`，坐标/棋盘图见 `bg-coords-diagram-v1` |
| 元素写法（片段 filename、Callout、链接） | `references/quarto/authoring.md`；细则见知识 `bg-qmd-element-cases-v1`、`bg-quarto-conventions-v1` |
| 命令、输出与常见错误三步流 | `references/quarto/terminal-validation.md` |
| 段落拆分、凑字数禁令、衔接、语气、篇幅与术语 | 知识 `bg-paragraph-list-style-v1`、`bg-paragraph-cohesion-v1`、`bg-chinese-voice-register-v1`、`bg-content-budget-v1`、`bg-terminology-v1`；改写对照见 `bg-chinese-style-cases-v1` |
| 全仓 QMD 重构范围与收口 | `references/quarto/repository-wide-refactor.md` |
| 内容规范核对与增量校验 | `.agents/skills/governing-agents/scripts/run.py check/verify`（verify = verify_content 的 --changed/--paths 包装）；自测答案折叠由 `scripts/answer-disclosure.lua` 提供（`_quarto.yml` 顶层 `filters:` 注册） |

## P0 硬约束

1. 根目录 `_quarto.yml` 是 Book 章节顺序的唯一来源。
2. `README.md` 只做项目入口，完整设计和演示放 Quarto。
3. 页面标题由 YAML `title:` 提供，正文从 `##` 开始，最多到 `###`。
4. 含代码块、列表或表格的小节按「引言 → 块 → 结尾（可选）→ Callout（可选）」组织。一段只推进一个对象，对象切换必须新起段并用一句关系衔接；代码围栏内 `//` / `#` 注释已写明的意图，块后正文不得同义复述，只写注释没覆盖的新工程信息（谁调用、如何验证、与邻块或图的关系）。同一小节内递进依赖的同源片段（常量 → 类型 → 使用它们的函数）必须合并为一个围栏并润色导语与块后正文，禁止拆成连续多围栏。细则见知识 `bg-qmd-element-cases-v1`，改写对照见 `bg-chinese-style-cases-v1`。
5. 展示 `games/<game>/` 源码默认内联摘录关键片段：逐字摘录，省略处直接省略不写标记行，每处注释不超过 2 行；include 仅限完整展示的短文件且必须包在带语言标注的围栏代码块内。
6. 复杂关系才使用 Mermaid；默认图是 `{mermaid}` flowchart（流程、分层、调用链），一律使用 `{mermaid}` 属性围栏，plain ```` ```mermaid ```` 围栏不会渲染。坐标轴类网格图仅当用户明确指定时走 `coords_grid.py` 加 `{python}` 可执行单元（围栏、解释器与 CI 见知识 `bg-coords-diagram-v1`）；禁止用 Mermaid 硬画网格。
7. 修改 QMD 或 Quarto 配置后在仓库根目录运行 `quarto render`（在其他目录执行会静默不渲染）。
8. 同段不堆砌流程名词；对照表用关系句承接；相邻段落不得各成独立说明书；章引言与节引言不用顿号串交付物（目录式堆砌禁令见 `references/zh/writing-principles.md`，对照见知识 `bg-chinese-style-cases-v1`）。标题与正文禁用读者尚未建立的概念术语做标题或论据，术语未建立就删除或下沉到后续章节；一句话压缩多个论断而读者无法逐条核对的，拆成可核对表述或删除（规则见知识 `bg-paragraph-cohesion-v1`「小节标题与正文对齐」，对照见 `bg-chinese-style-cases-v1`「小节标题抽象与首句无中心」）。代码块与 `{mermaid}`/`{python}` 图之间必须有桥接正文（固定序列见 `references/quarto/authoring.md`「代码与图的桥接」，对照见知识 `bg-qmd-element-cases-v1`、`bg-coords-diagram-v1`）；图遵守一图一事、同主题相邻、不承载正文未写的新信息，主题错位拆 `###`（同上节规则）。读者正文写可观察对象与完整主谓句，禁用压缩隐喻与电报省略（禁用词以 `scripts/verify_content.py` 词表为准）。
9. `content/**` 正文禁止语言课：不讲解 C++ 语言机制或风格指南条目，旁白只谈工程（公共定义、调用方、验证）；跨仓外链默认零条，禁止「写法依据见」等突兀句，可选尾置「若要系统阅读…」（细则见 `references/zh/chapter-writing.md`「叙事范围」）。同一硬边界下禁止课堂类比：坐标系等工程对象只写程序事实与可观察行为，不写「数学课」「平面直角坐标系」类跨学科对照。头文件指称点名具体对象（文件名、`include/` 路径、调用方）或写全「库对外头文件」，禁用「公共头」类省略缩略（词表见知识 `bg-terminology-v1`）。节导语与 `>` 引用块的 token 与句数限额见知识 `bg-content-budget-v1`，由 `verify_content.py` 自动执行。
10. 大规模正文重构先取全量语料：`scope` 命中范围 → 本 SKILL → 其路由指向的全部参考与知识文件、校验脚本读完再动笔，禁止只按任务清单的增量条目改写。
11. 全仓 QMD 重构按 `references/quarto/repository-wide-refactor.md` 枚举源文件、排除生成物，并在收口时执行全量内容验证和渲染。

## 完成判据

- [ ] `run.py check --profile fast`（或 `run.py verify --changed`）与 `quarto render` 通过；改动渲染产物语义时补 `--profile book`。
- [ ] 章节骨架与 `references/zh/chapter-writing.md` 一致，游戏章差异与知识文件相符。
- [ ] qmd 验证只跑 `verify_content.py` 与 `quarto render`，不截图 PNG、不做视觉评审。
