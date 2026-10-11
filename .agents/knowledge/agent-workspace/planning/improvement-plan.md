---
kb_id: "bg-improvement-plan-v1"
title: "全面审计改善计划"
domain: "agent-workspace"
subdomain: "planning"
tags: [audit, improvement, tests, ci, terminology, theme]
level_range: [0, 5]
dependencies: ["bg-roadmap-v1"]
created: "2026-10-06"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 2800
---

# 全面审计改善计划

本计划汇总一轮全面审计的结论：三个只读侦察分别审代码（`games/tictactoe` 三个编号目录）、读者文档（`content/tictactoe` 八个 qmd 与落地页）与工程设施（CI、脚本、主题、MCP），叠加本地校验基线与联网调研。每项给出证据位置与方案；无争议的客观错误已在本轮顺手收口，其余按五批推进，标注【需拍板】的三项先取得用户确认。

## 目的与基线

- 审计时点的基线：`check --profile full` 17 项全通过；`kb-eval` 通过；三个编号目录的构建与 CTest 全绿（改动未提交）。
- 审计方法：只读侦察不改文件，结论必须带 file:line 证据；联网结论只作「建议依据」，是否采纳由对应批次执行时决定。
- 本计划是路线图不是定案；正文提到的日期一律见 frontmatter 的 created/updated。

## 发现总览

| 域 | P0 | P1 | P2 |
| --- | --- | --- | --- |
| 代码（三个编号目录） | 2 | 6 | 9 |
| 读者文档 | 1 | 1 | 13 |
| 工程设施 | 1 | 7 | 10 |

【已收口】五项：07 章示例 JSON 的 `sequence`、README 当前状态、05 章「共享库」误称、`content/tictactoe/06-opponent_files/` 生成物（连同 `.gitignore` 的 `*_files/` 规则）、02/03 测试 CMake 的「静态库」过时注释。

## 第一批：正确性修复

1. `ReadRowAndCol` 超出 int 范围的分支不丢行（01 `apps/src/cli.cpp:89`、02 `:90`、03 `:131`）：头文件契约（`apps/include/cli.h:50`）要求「不是两个整数或超出可用范围时，清掉错误并丢掉本行」，超范围分支只报错返回 `kRetry`，行内剩余 token 会串到下一次读取。方案：与解析失败分支同样 `in.clear()` 后按行 `ignore`，处理 EOF 边界。验收：cli 测试喂 `5000000000 1 2`，断言下一行仍从行首读。
2. `RandomMove` 空盘下溢（02/03 `tictactoe/src/opponent.cpp:56`）：`size() - 1` 回绕成 `SIZE_MAX` 后越界；同型无设防还有 `:86`、`:135` 的 `front()`。方案：`ChooseMove` 入口断言棋盘有空位（契约在 `opponent.h:40`），不改返回类型以免教学复杂化。验收：CTest 全绿。
3. `build-and-run.sh` 的 ERR trap 是死代码（三个编号目录 `:13`）：`set -euo pipefail` 缺 `-E`，函数内的失败不触发 trap 的定位提示。方案：改 `set -Eeuo pipefail`。验收：制造一次编译失败，确认失败提示来自 trap 分支。

## 第二批：测试与工具链加固

测试缺口（按文件）：

- `game_test.cpp`：O 获胜对局（`game.cpp` 的 `kNoughtWin` 分支无测试）、`Board::IsFull` 直接用例、`Game::TryPlace` 的占用格与越界坐标两条拒绝分支、`GetHistory` 只测 size 未测顺序与内容。
- `opponent_test.cpp`：启发式的「能挡」（现只测能赢）、无威胁时的中心到角到边优先序（`opponent.cpp:77`）、`EmptyCells` 行序契约、`TerminalScore` 三态、`RandomMove` 非空盘合法性。
- cli 层零单测：菜单无效输入重试、菜单处 EOF 退出码、坐标重试循环、`ReportRejected` 文案；接口已按流参数设计，补一个 `cli_test.cpp` 即可注入字符串流。
- 03 协议（`tests/CMakeLists.txt:78`）：现仅一条终局前缀正则；补每步恰一行 JSON、`sequence` 递进、`draw` 终局用例；或把 `WriteSnapshot` 改为返回字符串再单测。

工具链：

- `.clang-tidy` 补 `google-readability-casting`（风格手册已禁 C 风格转换）、`clang-analyzer-core*` 子项、`misc-include-cleaner`；CMake 编译选项补 `-Wold-style-cast`、`-Wshadow`。
- `RandomMove` 每次调用重建 `std::mt19937` 且单值播种（`opponent.cpp:55`）：改为 `static thread_local` 单次播种（依据见「联网调研依据」第 6 条）。
- `FetchContent_Declare(googletest URL …)` 补 `URL_HASH SHA256=…`（三个编号目录 `tests/CMakeLists.txt:15`）。
- `PlayToEnd` 两个重载重复约 30 行人走棋逻辑（02 `apps/src/cli.cpp:214` 与 `:255`）：抽 `readHumanMove` 助手。
- 测试助手 `Play()` 在 `game_test.cpp:26` 与 `opponent_test.cpp:27` 重复：加 `cli_test.cpp` 时顺手提为测试头。

## 第三批：CI 与供应链加固

- 两条 workflow 的 action 从 tag 钉扎改为 commit SHA 加版本注释（`.github/workflows/pages.yml:21,24,25,44`、`render-check.yml:15,18,19`），升级交给 Dependabot。
- Quarto 版本钉扎：`config.toml` 增设 `quarto_version` 并传入 `quarto-dev/quarto-actions/setup` 的 `version` 输入——仓库自己的 DOM 契约检查已声明 Quarto 升级会改代码块 DOM，属已知风险面。
- `render-check.yml` 补 `concurrency`（按 ref 取消旧跑）；两条 workflow 每个 job 补 `timeout-minutes: 30`。
- `config.toml` 的 Python 依赖只写下限（`:10-14`）：补版本上限或导出锁定清单；pip 缓存键从整份 config.toml 改为依赖清单 hash。
- MCP `project_review` 超时从 120s 提到 300s（`.agents/mcp/server.py:168,413`），与 `project_check` 对齐（前者跑的是 `check --profile full`）。

## 第四批：内容与术语清扫

【需拍板】「棋盘格子」锚点清扫是本批主体，但 03 章 title 曾在标题定稿轮次被保留，改标题需用户确认：

- title 与四处引用（`content/tictactoe/03-board.qmd:2`、根 `index.qmd:19`、`02-project-layout.qmd:53`、`04-game.qmd:6`）；
- 正文「格子」「九格」共 15 处（03 `:6,86,100,101`；04 `:28,85`；05 `:35`；06 `:35,53`；07 `:6,10,36,51,56`）；
- 清扫同批把「单独的『格子』」「九格」补进 `verify_content.py` 词表形成硬闸。

其余按词表与规范收口：

- 03 章两处摘录与 `board.h` 非逐字（`:24` 合并空注释行、`:130` 删「棋盘为 3 行 3 列。」）：恢复逐字或在导语声明节选约定。
- 称谓各收敛一个：`build-and-run.sh`（入口脚本/一键验证脚本/构建与验收入口）、管道棋谱（管道对局/管道验收/双人管道棋谱）、07 章「给人看的棋盘」与「中文棋盘」、根落地页「逐行协议」孤词。
- 首次出现补同位语：CMake/Ninja/CTest（05 `:15,19`）、可执行文件名 `app`（05 `:42`）、`board_test.cpp` 点名并挂链接（05 `:15`）、`Board` 首现同位语（03 `:32`）、`CellPosition` 首定义用「棋盘格子坐标」（03 `:14`）。
- 图题编号统一：仅 07 章用「图 1：」前缀；Quarto Book 的交叉引用可按章自动编号，或全书统一无编号。
- 规范侧两处收口：「示例位置句」开口子已在章引言形态定案中废止，引言现为「单段 ± 列表」契约（见标识 `bg-chapter-structure-v1`）；02 章无「常见错误」节的豁免条件已写进六段骨架。

同批追加（四目录与自测格式收口，已完成）：02 章目录列表并入 `build/` 成四项并删列表后补段，自测答案去链接改行内代码路径（所属目录已确立时省顶层前缀）；「分进」入 `verify_content.py` 硬闸，新增自测节链接 WARN 与分号「并列主谓分句」豁免；03 章 H2 概览句改「；」并列分句、图前段两段并一段（删前章画面版式指称与第二主题）、数组段去电报体；04 章「定义见」式文件指称改「声明在……里」（该方向后按术语表「声明/定义」条目收口：完整实体称定义，「声明在」仅保留给只写函数名与参数表的成员函数行）；01、index 复查零改动，05–07 自测节核对无链接。

## 终端结果文本与展示收口

人类终局文本原先使用含义偏弱的 `状态` 标签，而 01、05、07 章分别重复完整画面、终局关键字和协议映射；阶段测试也只匹配 `X 获胜` 子串，无法保护结果标签。已将 CLI 结果行统一为 `对局结果：X 获胜`，保留 `GameResult` 语义、棋盘排版和 JSON 协议字段不变。

改动落点包括 `01-cli-game/apps/src/cli.cpp`、阶段 CTest 与 `build-and-run.sh`，以及 `content/tictactoe/01-rules.qmd`、`04-game.qmd`、`05-terminal-play.qmd`、`06-opponent.qmd`、`07-line-protocol.qmd`。文档只保留 01 章的权威终局画面，其他章节分别说明领域判定、终端适配器、人机输入和机器协议；列表项统一到短而并列的句式。验收需覆盖完整结果行、QMD 代码块前后承接、人类文本与机器协议分界，并运行阶段构建、内容校验、知识库校验和全书渲染。

## 第五批：主题、脚本与 CMake 修缮

- 主题：删死令牌（`--btn-primary-*`、`--navbar-shadow`）；`code.css:127,134` 重复声明去一；搜索图标暗色 `%23768390` 与 `--navbar-muted` 暗值对齐；字体栈把 `sans-serif` 移到 emoji 字体之后（否则 emoji 字体不可达）；`color-scheme` 收敛到一处声明。
- 脚本：`run.py` 与 `check_layout.py` 的子进程补 timeout；`check_docs.py` 与 `check_encoding.py` 抽公共跳过清单；`check_encoding.py` 的自豁免改为文件头标记；两条 workflow 前 8 步抽 composite action。
- CMake：`cmake_minimum_required(VERSION 4.2)`【已定】留 4.2，版本约束注释保持简洁一句（「保证本目录使用的命令可用」）；`apps/CMakeLists.txt` 源文件按字母序；`opponent.h` 查询型自由函数补 `[[nodiscard]]`；`ReadStrength` 补 `@param in/out/err`；`build-and-run.sh` 的 `find | xargs` 改 `-print0|-0`。
- 知识库：`development-environment.md` 的 CI 描述同步为「`run.py render` + book profile」现状；`cmake-conventions.md` 的测试名示例同步为 `tictactoe_test`、`tictactoe_scripted_match`。

## 字体子集与标题风格收口

现象与处理（本轮已完成）：两个自托管 `common` 子集共用同一份字符表，缺「弈、胜、赢、颠、黑」，结果行末字「胜」在 HTML 代码块中落到系统宋体。已从本机 LXGWWenKai v1.522（upem 1000）提取 5 个字形，分别缩放到两个子集的 upem（2048/2000）后注入，其余字形一字不动；`--mono-font` 与两个 palette SCSS 的栈尾追加 CJK 系统字体兜底。01、02 章 title 收口为列表引导词风格（「确定对局规则」「对应工程目录」），H2 同步更名或拍平；02-cpu-opponent 与 03-line-protocol 的结果行迁移为「对局结果：」，CTest 与 `build-and-run.sh` 断言升级为完整结果行。

同批追加：03、04 章 title 收口为「实现棋盘存储」「实现对局规则」，05 章引言链接与落地页卡片同步；获胜判定删除 `At`/`kLines`，`IsLineFilled` 改为逐行、逐列加两条对角线的算法，坐标构造统一指定初始化器（三阶段同步，build 全绿）；「进行中」统一为「游戏进行中」（注释与 CLI/网页输出）；「执 X/O」行话与「遵循同一套」无铺垫套语禁令入库（terminology、comment-style、chinese-style、verify 词表）。

- 规则沉淀：`theme-system.md`「字体栈（三处同步）」补 CJK 兜底与子集覆盖校验；`chapter-writing.md` 自测条目补「答案首句回答问题所问的对象」；`verify_content.py` 增加结构元词「并列」模式；`chinese-style.md` 补「输出引言的结构元词」「问答对象错位」两案例。
- 后续批：05–07 章 title 与二三级标题按同风格收口（03、04 已完成）；04–07 章同节重复文件链接清理（「职责 / 负责 / 承担」三词硬禁与摘录链接密度 WARN 落地后新增，02、03 已清零）；子集覆盖检查目前靠人工 fontTools 复核，可考虑纳入主题校验脚本。

## 中文全量润色（1B+2A）批次状态

独立于上方 v6 批次的中文润色计划（范围定案：允许章内重组 1B、规范只进 `.agents` 2A）。批次与验收：

| 批 | 内容 | 状态 | 验收证据 |
| --- | --- | --- | --- |
| 术语全表入库 | `bg-cpp-chinese-terms-v1` 新建；`terminology` 只加读者禁用行；`comment-style`/`comments`/`chinese-style`/两 SKILL/KNOWLEDGE 路由同步；`bg-chinese-quality-v1` 与 polish-pass（已并入 writing-howto.md）布局检查 | 完成 | kb-index/kb-check 绿；`verify --changed` 不拦合法「公开成员」 |
| 正文清扫 | 8 个 qmd 按章审读重组润色；「公开段/私有段」清零；摘录与源码一致；title 微调处同步 index/链接/`_quarto.yml`/stages | 完成 | `verify --changed` + `check --profile fast` 按章绿 |
| 注释清扫 | 三阶段注释润色；「接受」清零；三目录同名文件 diff 一致 | 完成 | 三阶段 diff 一致 + `build` 绿 |
| 命名对照入库与全量校验 | 形态表 + 语义角色表写入 `bg-google-cpp-style-v1`/`bg-naming-cases-v1`/`bg-project-decisions-v1`；全量校验；仅 `StatusToString` → `GameResultToString` | 完成 | `Set*`=0；角色前缀列表通过；重命名全引用同步；三阶段 `build` 绿 |
| 机械闸 | 「公开段」「私有段」写入 `verify_content.py` 与 `check_zh_lint.py`，补自测 | 完成 | selftest + fast 绿 |
| 收口 | `render` + kb-index/kb-check + 本计划域校验 + `full` | 完成 | 见上表；kb-eval 存量单独记账 |

**kb-eval 召回修复（独立批次，已完成）**：基线 Top-5 召回 88.0%（154/175），未命中 21 条全部是旧查询，公开面批次新增的 6 条查询全部命中。`evaluator.py --verbose` 补期望块标题路径与最佳名次后冻结诊断，四类为：锚点目录块占 Top-5 为 0 条，短节占位 3 条，池内近失（去重后第 6–8 位）8 条，不在候选池 13 条，导航误判 0 条——欠账主因不是目录块，而是改写查询的词面缺口与覆盖率打平后短节靠「更短 Parent 优先」获胜。做法分三批：① 分块器不把「正文只有自锚点链接列表」的整节收成块（形态规则 `is_self_anchor_list`，自测 `test_chunker.py`）；② 精排 `rerank_score` 在覆盖率之外加封顶词频（`TF_CAP = 3`），让反复讨论查询词的正文节胜过只提一次的交叉引用；③ 逐条只留一个权威——期望片段改指现行权威节 1 条（公式隔代码块改指「内容块前后的闭环」），四处自然补词（实现方式边界补空目录禁令、路线开篇补编号目录顺序、开工检查单补导语句、Google 采纳要点补「头文件里的公共常量」），不改标题、不批量改旧期望。结果 88.0% → 89.1% → 92.0% → 94.9%（166/175），每批一次闸（`kb-index --rebuild`、`kb-check`、`kb-eval`）全绿，注入峰值 3529 ≤ 6000。剩余 9 条记台账（答案已在权威节内，同分排序损失，补词即堆关键词，不再追）：`.clang-tidy` 文件头、Doxygen 格式、枚举子命名、六段块序列（首章末章、页面骨架两条）、禁用与替换（阶段、接口桩、true/false 三条）、单行注释。不做项：不下调 0.92、不冲高分母、不在同一次改动里调 `RRF_K` 或意图权重、不把检索评测写进读者章节。

## 联网调研依据

1. GitHub Actions 钉扎：tag 可变、SHA 不可变，GitHub 已支持组织级强制 SHA 钉扎；OWASP 与 StepSecurity 指南为权威出处。（https://cheatsheetseries.owasp.org/cheatsheets/GitHub_Actions_Security_Cheat_Sheet.html 、https://www.stepsecurity.io/blog/pinning-github-actions-for-enhanced-security-a-complete-guide）
2. Quarto CI 安装：`quarto-dev/quarto-actions/setup` 提供 `version` 输入钉扎具体版本。（https://github.com/quarto-dev/quarto-actions）
3. FetchContent 完整性：`URL_HASH SHA256=…` 校验下载物；`CMP0135` 消除抽取时间戳警告。（https://cmake.org/cmake/help/latest/policy/CMP0135.html）
4. clang-tidy 检查集：bugprone、performance、readability、modernize 全家族是主流基线，配少量豁免。（https://clang.llvm.org/extra/clang-tidy/checks/list.html）
5. 流输入校验：`clear()` 加按行 `ignore` 是清标志丢行的标准式（learncpp「std::cin and handling invalid input」一节）。（https://www.learncpp.com/cpp-tutorial/introduction-to-these-tutorials/）
6. 随机数播种：引擎每线程构造一次（`static thread_local`），单值播种只覆盖 32 位状态空间，`random_device` 只用于初始化。（https://stackoverflow.com/questions/45069219/how-to-succinctly-portably-and-thoroughly-seed-the-mt19937-prng）
7. 图题编号：Quarto Book 交叉引用按章自动编号 figure（`#fig-` 标签加 `@fig-` 引用）。（https://quarto.org/docs/books/book-crossrefs.html）
8. 教学递进：learncpp 的螺旋式（先广后深）与 PPP 的推迟复杂度是两条被广泛验证的排序依据；本仓「先能跑再补强」的七章与此一致。（https://isocpp.org/get-started）
9. 对比度：WCAG 2.2 AA 正文 4.5:1，大字 3:1；`color-scheme` 的两套配色都要独立达标。（https://www.w3.org/TR/WCAG22/#contrast-minimum 、https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme）
10. GoogleTest 实践：测试名直述行为，fixture 承担公共装置。（https://google.github.io/googletest/primer.html）
11. 获胜判定：固定 3×3 下「8 条线坐标表」与「行列循环 + 两条对角线」两派并列，坐标表利于 m,n,k 推广与性能，循环算法可读性更好；本仓取算法。（https://leetcode.ca 、https://codereview.stackexchange.com）

## 批次验收与边界

- 代码批：先 `clang-format` 再 `run.ps1 build <阶段>`（脚本内置格式与 clang-tidy 闸门）；改动落在三个目录共有文件时先改 01 再按 MD5 同步 02/03。
- 内容批：`check --profile fast`（编码）+ `verify --changed` + `render`（计算页更新 `_freeze` 快照）。
- 工程批：CI 改动合入后看 GitHub Actions 首跑；本地先目视核对 YAML 与脚本行为。
- 知识批：kb-index → kb-check → kb-eval → `check --profile knowledge`。
- 全程不 commit 不 push；不读 `_book/`、`games/**/build/`、`.quarto/`、`temp/`。
- 【需拍板】三项：03 章 title 措辞（已定「实现棋盘存储」）、`verify_content.py` 新词表硬闸（已加入「遵循同一套」「执 X」「执 O」）、`cmake_minimum_required` 放宽与否（已定：保留 4.2，论证见 `bg-cmake-conventions-v1`）。其余批次按本计划顺序执行。

## v6 收口与轨道 F 执行状态

在五轨道之上补一条**轨道 F**：统一 API 形参与成员初始化写法、终局判定归属、测试 include 分组、注释短句、CLI 测试链库与 04 章 `class Game` 叙事。本轮按批推进，逐项状态如下。

| 批 | 内容 | 状态 | 验收证据 |
| --- | --- | --- | --- |
| 批 0 | 核对 `check_zh_lint.py` 规则集与覆盖率输出；命名/NSDMI/include/注释/终局定案入库；顺带修 5 个文件的 CRLF | 完成 | `check --profile fast` 11 项全通过 |
| 批 1 | 轨道 A + F1–F4/F7：三阶段 `board.h/.cpp`、`game.h/.cpp`、`opponent.h/.cpp`、`cli.h`、`apps/tests` 的 CMake、`build-and-run.sh`、全部测试 include | 完成 | `build tictactoe/{01,02,03}` 三阶段全绿（配置→编译→clang-format→clang-tidy→CTest→运行） |
| 批 2 | 轨道 B：action 钉 SHA、`concurrency`、`timeout-minutes: 30`、`config.toml` 增 `quarto_version`、pip 缓存键派生、MCP `project_review` 300s；前段步骤抽 `.github/actions/ci-prepare` | 完成（不声称 CI 绿） | 三份 YAML 解析通过；派生命令本地复跑得到依赖清单与 `1.10.18` |
| 批 3 | 轨道 C + F5/F6：05–07 title 定稿、04 章 `class Game` 叙事与 `## 游戏结果`、03 章节选约定、图题编号统一、称谓与同位语 | 完成 | `verify --changed`（片段一致性）通过；`render` + book profile 通过；`_freeze` 快照已更新 |
| 批 4 | 轨道 D：删死令牌 `--btn-primary-*`/`--navbar-shadow`、`code.css` 去重复声明、深色搜索图标对齐 `--navbar-muted`、字体栈 emoji 可达、`color-scheme` 收敛；脚本子进程补 timeout、跳过清单抽 `repo_scan.py`、编码自豁免改文件头标记；CMake 4.2 论证 | 完成 | `check --profile full` 19 项全通过 |
| 批 5 | 轨道 E：cpp-notes 侧陈旧跨仓标签（`检查落子并判定终局`→`实现对局规则`、`定义棋盘与格子状态`→`实现棋盘存储`，6 个文件） | **部分完成** | cpp-notes 工作区已修；`polish-pass`（已并入 writing-howto.md）载体表、`chinese-style` 认可态与闸脚本镜像留在 cpp-notes 自身一轮 |
| 批 6 | `check --profile full`、kb-index/kb-check/kb-eval、本状态表与 KNOWLEDGE.md 入站引用 | 完成 | full 19 项全通过；kb-health PASS；kb-eval 通过 |

### 本轮修订的定案（覆盖上文旧条款）

1. **`Board board_{};` 改回 `Board board_;`**（用户定案的目标形态经机械验收修正）：`readability-redundant-member-init` 判定有默认构造的类子对象与容器写 `{}` 冗余，`std::array` 的 `cells_{}` 则必需。诊断与结论见 `bg-google-cpp-style-v1`「成员初始化（NSDMI）」。
2. **测试 include 分组靠配置固定**：`.clang-format` 增 `IncludeBlocks: Regroup` + `IncludeCategories`（`^<gtest/` 归「其他库」），否则 Google 默认类别把 `<gtest/gtest.h>` 排到 C++ 标准库之前。
3. **CLI 实现编成 `tictactoe_cli` 静态库**：`app` 与测试链接它，测试源列表不再列 `../apps/src/cli.cpp`；命名表与旧「`tictactoe_cli` 已废弃」条款同步改写。
4. **`IsLineFilled` 更名 `Game::HasPlayerLine` 并收进 `private static`**，与 `ResultAfterMove` 同处；`PlayerToCellState` 与 `opponent` 的 `CompletesLine` 仍作自由函数。
5. **`Get*` 注释概述以「获取」开头**（用户定案，本轮再覆盖上一轮的「短结果名词句」条款，不保留双轨）：`/// 获取当前对局结果。`，细节进 `@param`/`@returns`。现行规则见标识 `bg-comment-style-v1` 的知识文件「领域函数与成员注释」，对照见标识 `bg-comment-cases-v1`。
6. **05–07 title 定稿**：`运行终端对局`、`加入电脑对手`、`输出局面快照`；04 章 `## 得出胜负与平局` 更名 `## 游戏结果`。
7. **`cmake_minimum_required` 保留 4.2**（不再列为待拍板）。
8. **knowledge 体量**：`bg-project-decisions-v1` 的「架构决策」超 Parent 预算，按内容拆出 `## 编码与注释约定`。

### 明确未做

- 不提交、不推送；未跑 GitHub Actions 首跑，CI 结论只到「本地 YAML 解析 + 派生命令复跑」。
- cpp-notes 的 `polish-pass`（已并入 writing-howto.md）载体表、`chinese-style` 认可态与 `check_zh_lint.py` 镜像未做：该仓有并行未提交改动，且其闸脚本与 `writing-cpp` 结构不同，需按它自己的 AGENTS.md 单独一轮。
- 字体字形表深核、`apps/CMakeLists.txt` 源文件字母序（拆库后每个 target 只剩一个源文件，无排序对象）。
