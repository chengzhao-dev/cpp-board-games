---
kb_id: "bg-publish-surface-v1"
title: "公开面与风格维持依据"
domain: "repo-github"
tags: [publishing, ci-boundary, style, layout, skills, quarto]
level_range: [0, 5]
dependencies: [bg-staged-game-layout-v1]
created: "2026-10-11"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 1700
---

# 公开面与风格维持依据

本文件回答公开面为什么这样划界：哪些内容上 GitHub、风格维持哪些偏离、目录布局与技能形态为什么保持现状。怎么做（闸门顺序与命令）见 `shipping-github` 技能的 `references/publish-gate.md`。

## 上库内容为什么这样划界

- `main` 上进 GitHub 的是未被 `.gitignore` 排除的源码；`gh-pages` 上只有 Actions 推上去的 `_book/`（`force_orphan` 孤立分支覆盖，产物不累积历史）。
- 不进任一分支的条目各有归属：`build/` 是各阶段本机构建产物；`main` 上的 `_book/` 与 `.quarto/` 是渲染生成物和本地缓存，线上只认 Actions 发布的那份；`temp/` 收一次性产物；`.zcode/` 是本地计划与临时区；根 `.vscode/` 按仓库约定只在阶段子目录内保留编辑器配置。
- CI 只覆盖文档与 `.agents`（渲染与文档校验），游戏代码不进 CI：三个阶段各跑一次本地 `build-and-run.sh`。教学仓不为单一游戏维护 CI 侧交叉构建或工具链缓存；推送后的 Actions 是复核，发布闸以本地脚本为准。

## 仓库根上的入口文件

- `.gitignore`、`.gitattributes`、`.editorconfig`、`config.toml` 与 `CONTRIBUTING.md` 留在仓库根，不进 `.github/` 也不进阶段目录：EditorConfig 从打开的文件向上查找，`root = true` 必须写在任何节之前，放进某个阶段目录盖不住 `content/` 和其他阶段；Git 的忽略与属性规则按所在目录向上生效，根上一份就是全部；GitHub 在仓库根、`docs/`、`.github/` 三处识别贡献指南，本仓没有 `docs/`，README 已链到根上的 `CONTRIBUTING.md`。
- `config.toml` 只写本机工具路径与版本：解释器等纯工具路径可以入库，密钥类信息与可识别个人的用户主目录路径不进仓库。
- 不新增行为准则、安全政策或议题模板：单人维护的教学仓，Issue 讨论已经够用。

## 风格维持项与不动条文

现行标准仍是 Google C++ Style 的十条有意偏离，条文出处是标识 `bg-google-cpp-style-v1` 的知识文件与 `cpp-development` 技能的 `references/google-cpp-style.md`；本文件只登记复核结论，不改白名单条文本身：

- 行宽 100：Google 与 LLVM 默认 80，OpenCV 用 100；Windows 上教学代码取已有先例的 100，不回 80 也不放到 120。
- 命名形态维持：函数 PascalCase、变量 snake_case、成员 `_` 后缀、常量 `k` 前缀。函数 PascalCase 与 Google 的 CamelCase 要求一致，不构成偏离。
- `#pragma once`、扩展名 `.cpp` / `.h`、项目头裸文件名引号 include 维持。
- 业务结果用 `PlaceResult` / `GameResult` 表达，契约违反可以抛 `std::out_of_range`。
- 坐标与尺寸用 `int`，封闭状态枚举底层用 `std::uint8_t`。
- 成员默认值写在声明处（NSDMI），零参构造头内 `= default`。
- 声明注释用 Doxygen，实现注释比 Google 的 Function Comments 更密：教学需要，不削到指南基线。
- 源码 `.cpp` 不用匿名命名空间；测试文件里的匿名命名空间仍是唯一例外。
- `CompletesLine` 仍是谓词白名单的唯一例外，不扩散。

## 目录为什么保持三份快照

对照过 LLVM 的 `lib` 与 `tools`、OpenCV 的 `modules` 与 `apps`：那两家是一份会演进的产品树，目录按组件划分；本仓要让每一章对应的程序还能单独打开、单独构建，三份编号目录是教学快照，不是重复劳动。由此：

- 不把 `01-cli-game`、`02-cpu-opponent`、`03-line-protocol` 收成一个 CMake 工程，也不把棋盘源码抽到阶段外的公共目录；至少两个游戏真实复用且语义稳定之前不建 `shared/`。
- 根目录不加 `CMakeLists.txt`：三个阶段不能也不需要在仓库根一次配完。
- 主题继续放在 `.agents/skills/designing-theme/assets/theme/`，`_quarto.yml` 已指向这里；挪到根上 `theme/` 只改路径，不改变读者看到的页面。
- 三份 `.clang-format`、`.clang-tidy`、`.clangd` 各放一份，不用符号链接指回模板：阶段必须在不依赖 `.agents` 时仍能格式化与做静态检查；与模板的一致性由抽查保证。
- `games/tictactoe/python/` 不改名为 `04-`，也不并入 `03-line-protocol` 的 CMake：它不是新的 C++ 行为，只是去启动 03 已经编好的 `app`。
- 章号 01–07 与阶段号 01–03 不必对齐：前五章都指向 `01-cli-game`，依据见标识 `bg-staged-game-layout-v1` 的知识文件。

### 仓库四块与辅助程序的关系

访客看不出的几层关系登记在此，仓库级地图放 README，读者章 `02-project-layout.qmd` 继续只画 `01-cli-game` 里的四个目录，不提前展开后两个阶段：`content/` 是书，`games/tictactoe/<编号阶段>/` 是三份各自完整的程序，`games/tictactoe/python/` 是协议之后的回放和本地网页，`.agents/` 是维护规则与主题。回放和网页依赖 03 已生成的 `build/bin/app`；`web.py` 的阶段路径写成相对本文件的 `../03-line-protocol`，让「辅助程序在编号目录旁边、只调用 03」在代码里对得上。`python/` 不是编号阶段，编辑器配置跟有这份代码的目录走：其 `.vscode/` 只推荐 Python 与 Black，不把 C++ 扩展再抄一份。

## 技能形态为什么维持 OpenAI 现状

对照 OpenAI 的 AGENTS.md 指南、Customization 与 Agent Skills 规范复核后，形态不变，理由如下：

- 根上只有一份 `AGENTS.md`。官方允许子目录再放一份、后读覆盖先读，那是给单体仓库不同子树用的；这里再拆一份会出现两个硬约束出处。文件保持在已配置的 65536 字节上限内，不为凑默认 32 KiB 去砍命令表。
- 十个技能的目录名保持 `cpp-development` 这类动名词 kebab：改名会打断路由、`openai.yaml` 与检索；官方只要求短、可区分、不超过 64 字符。
- `knowledge/`、`memory/`、`incidents/` 三区继续分开放：官方的技能解剖图里没有这三区，它们对应「为什么」和「上次错在哪」，不把内容并进 `SKILL.md`，也不在技能下加 README。
- `agents/openai.yaml` 保持默认可被任务隐式选中；只有用户明确要求「只能点名调用」时才关掉隐式调用。
- 发布闸门写成 `publish-gate.md` 并调用已有 `run.py`，不为这份清单新写检查脚本。
- 已有 spine 或路由表的技能不在 `SKILL.md` 补「## 工作流程」段：官方只要求易错、顺序不能变的步骤写死，工序抄进入口违反「参考按需打开、入口不重复」；`refactor-guidelines.md` 同步记为「有固定工序链接时空的工作流程段不算缺项」。
- `description` 在打开 `SKILL.md` 之前就参与技能选择，选择阶段只看 `name` 与 `description`；互斥边界（改 CSS 不转 `writing-quarto`、改棋规不转 `cpp-development` 等）必须写进 description，只写在正文里来不及。描述保持远低于 1024 字符，不把路由表抄进描述。

## Quarto 书形为什么不再加

对照 Quarto 书籍结构与 HTML 主题文档复核，以下维持不动：单根 `_quarto.yml`、`index.qmd` 首页、井字棋章节在 `content/tictactoe/` 用 `part` 收组、输出目录 `_book/`；明暗两套走 `theme.light` / `theme.dark` 加 `respect-user-color-scheme`；章内中文提示框与页脚维持。不再加的能力：

- 不加 PDF 或 EPUB：官方模板里有，但会绕开现在只为 HTML 调过的字体、栏宽和代码横滑。
- 不加参考文献章：书里没有书目。
- 章节不自动编号：标题已是短语，再加「第 N 章」与现有章名叠两套。
- 不写 `book.author`：页脚已有版权行，维护者身份只留在提交者与 `CONTRIBUTING.md`。
- `book` 下钉 `repo-actions: [source]`：读者能从页面打开 GitHub 源文件，不提供编辑与议题按钮；不钉死的话 Quarto 升级可能默认多出「编辑此页」。
