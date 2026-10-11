---
kb_id: "bg-project-overview-v1"
title: "项目现状与范围"
domain: "agent-workspace"
subdomain: "overview"
tags: [project, scope, stages, milestones]
level_range: [0, 5]
dependencies: []
created: "2026-10-11"
updated: "2026-10-11"
chunk_strategy: "semantic_heading"
estimated_tokens: 900
---

# 项目现状与范围

本文件回答「这个仓库现在是什么、现在做到哪、现在允许做什么」。读者面的完整解释统一维护在 `content/**/*.qmd`；决策与调研的取舍记录在标识 `bg-project-decisions-v1` 的知识文件。当前进度与状态以本文件为权威，改动现状时先改这里。

## 项目定位

- 本仓库用可运行的棋盘游戏程序演示 C++ 工程实践，配套 Quarto Book 作为读者文档。核心实现语言是 C++20，构建链为 CMake、Ninja、Clang 与 CTest；环境与命令入口见标识 `bg-development-environment-v1` 的规范文件。
- 面向读者的设计、路线、验收和调研总结写入 Quarto；`.agents/` 只保留 Agent 判断所需的事实与取舍。
- 根 `index.qmd` 是整个仓库的项目入口，只说明项目目标、当前游戏入口和未来游戏范围；`content/<game>/index.qmd` 负责单个游戏已发布章节的阅读顺序。根首页不复制具体游戏章节卡片，也不把井字棋的一种玩法写成整个项目。

## 当前文档范围

`content/` 当前只维护井字棋。其他棋类暂不创建对应 content 页面。新游戏仍要每步可验证，先有可编译示例再注册章节。井字棋当前的章节链覆盖 01 规则与终端、02 对手和 03 逐行协议；Python 回放与本地 Web 适配作为协议层之后的辅助程序维护。

## 井字棋阶段顺序

井字棋的编号目录从最小到完整共三份，均可运行。`01-cli-game` 是双人终端。`02-cpu-opponent` 是人机，先选双人或人机，选人机后再选随机、启发式或 minimax 难度。`03-line-protocol` 在每次打印后追加版本化 JSON，包含九格、序号、轮到谁、状态和胜者；`games/tictactoe/python/replay.py` 只解析这行，不重判胜负。`games/tictactoe/python/web.py` 是只监听回环地址的本地 HTTP/Fetch 适配，复用 03 的终端协议，不属于 C++ 规则核心。目录命名与配置归属见标识 `bg-staged-game-layout-v1` 的规范文件。

## 已实现阶段与辅助适配

02 与 03 已完成独立构建、CTest 和脚本验收。Python 回放已覆盖版本、字段和序号校验；本地 Web 适配已实现模式/难度选择、坐标校验、请求体上限、回环监听和子进程错误边界。HTTP 只作为本地辅助适配，不新增 `04-http-play` 阶段、不引入远程部署或 WebSocket。

02-cpu-opponent（人机对战）：输入仍是一行两个整数，电脑的一步由 `tictactoe` 库里的 `ChooseMove` 产生 `Move`，再调用同一个 `Game::TryPlace`。随机合法空格、能赢则赢否则阻挡、minimax（终局效用胜 `+1`、和 `0`、负 `-1`）三种强度放在同一目录。alpha-beta 只有在与不剪枝选出同一着时才留在这一阶段。验收是 CTest 覆盖必胜、必挡和双 minimax 开局成和，以及 `build-and-run.sh` 能完成一局人机。

03-line-protocol（逐行协议）：标准输出在原有局面文本之外多一行版本化 JSON（版本、序号、九个棋盘格子、轮到谁、状态和胜者）。`games/tictactoe/python/replay.py` 解析这些行，用 `unittest` 检查协议，不重测胜负。读者章 `07-line-protocol.qmd` 用解析结果调用 `render_grid`。不引入 Flask、WebSocket 或 matplotlib。

`04-http-play` 不创建：本地 Web 适配已经存在于 `games/tictactoe/python/web.py`，但它不改变阶段路由，也不等同于可部署的 HTTP 产品。若未来需要正式服务，再另行定义认证、并发和部署边界。

## 阶段门槛

每个阶段必须能配置、编译、测试和运行。一轮全面审计的逐项结论、执行批次与未决项见标识 `bg-improvement-plan-v1` 的知识文件，阶段顺序本身以本文件为准。

## 测试与管道棋谱

- `01-cli-game` 用 FetchContent 引入 GoogleTest 并注册进 CTest（版本与接入细节见标识 `bg-cmake-conventions-v1` 的规范文件「测试框架时机」）。
- 管道棋谱是另一条 CTest：喂入固定着法，要求输出含完整结果行 `对局结果：X 获胜`。脚本自己再用管道喂同一局。

## 未来能力口径

人机、逐行 JSON、Python 回放和本地 Web 适配已有代码与对应测试；HTTP 适配仍不属于正式部署阶段，WebSocket、GUI 和共享游戏引擎仍不验收。共享库仍要至少两个游戏真实复用后才提取。GoogleTest 已在阶段中经 FetchContent 引入。阶段目录只在出现新的真实行为时新建。

## 其他棋类

四子棋、五子棋、黑白棋等未来游戏遵循同一渐进式开发和验证原则。井字棋的架构定案是方案 A（教学较优演进）：数组 `Board` + 全深度 minimax + αβ，不上 bitboard/置换表；其他棋类与 B 族引擎技术的推荐路径以标识 `bg-future-board-games-v1` 的知识文件为准。读者 `content` 仍只维护井字棋，其他棋类的实现路径已登记但未开工——不提前创建其他棋类的 `games/`、`content/` 目录或阶段路由表。

## 公开面与布局定案

- 上库内容 = `main` 未被 `.gitignore` 排除的源码 + `gh-pages` 上 Actions 推的 `_book/`；发布闸门顺序见 `shipping-github` 技能 `references/publish-gate.md`，划界、风格维持项与三阶段快照取舍见标识 `bg-publish-surface-v1` 的知识文件。
- 脚手架模板 `cmake_minimum_required` 与三阶段同为 4.2；CI 步骤清单以 `.github/actions/ci-prepare` 复合动作为准；`_quarto.yml` 钉 `repo-actions: [source]`。
- 技能形态维持 OpenAI 现状（单 `AGENTS.md`、技能目录名不改），互斥排除条件写进各技能 description。
