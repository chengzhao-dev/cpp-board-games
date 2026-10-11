# .agents/context/ 现行事实与规范

本目录回答「现在是什么、现在就该照做的规范」，是每轮任务的主流程区。按任务打开其中一个文件，不整目录注入。「为什么这样定、否决过什么」在 `../knowledge/`（经 `kb_id` 取用）；「这一步怎么做」在 `../skills/` 的对应技能。文件名与目录名一律纯 ASCII kebab-case。

frontmatter 与检索规范与知识库同一标准（`kb_id` 一律 `bg-*` 前缀、`##`/`###` 两层分块、Parent 4000 Token 上限），权威定义见 `../knowledge/KNOWLEDGE.md`「文件规范」与「检索不变量」。

## 按任务打开哪个文件

| 任务 | 文件 |
| --- | --- |
| 项目现状、当前阶段、能力口径、上库与发布面 | `project.md` |
| 分层解耦、规则核心形态、组件布局、对手与协议 | `architecture.md` |
| WSL、VS Code、工具链与三层命令怎么交给代理 | `development.md` |
| C++ 命名、头文件、类内顺序之外的 Google 规则与偏离白名单 | `conventions/cpp-style.md` |
| 注释（横幅、声明契约、实现注释、键值配置） | `conventions/comments.md` |
| 类内与命名空间声明顺序 | `conventions/declaration-order.md` |
| 异常边界与 `what()` 文案 | `conventions/exceptions.md` |
| 终端与脚本输出风格 | `conventions/terminal-output.md` |
| clang-tidy 门禁范围与诊断边界 | `conventions/static-analysis.md` |
| CMake 写法、构建目录、测试框架时机 | `conventions/cmake.md` |
| 阶段目录命名、配置归属、章节映射 | `conventions/stages.md` |
| 章节骨架、段落、句法、中文质量、语域、密度、qmd 元素 | `conventions/writing/`（按文件名取） |
| include 与链接、Mermaid、坐标图 | `conventions/rendering/`（按文件名取） |
| 读者侧术语与禁用词、C++ 中文术语对照 | `glossary/project-terms.md`、`glossary/cpp-terms.md` |

## 收录新规范

成段材料的落点计划流程见 `../skills/governing-agents/references/intake.md`；新 `kb_id` 的最小闭环（含 `eval_set.py` 补查询）见 `../knowledge/KNOWLEDGE.md`「新增知识的最小闭环」。
