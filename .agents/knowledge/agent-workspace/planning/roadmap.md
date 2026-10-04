---
kb_id: "bg-roadmap-v1"
title: "项目路线依据"
domain: "agent-workspace"
subdomain: "planning"
tags: [roadmap, stages, milestones]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-10-02"
chunk_strategy: "semantic_heading"
estimated_tokens: 900
---

# 项目路线依据

本文件供 Agent 判断阶段边界使用。井字棋读者页是 `content/tictactoe/` 的各章，不另设路线章。

## 当前文档范围

`content/` 当前只维护井字棋。其他棋类暂不创建对应 content 页面。新游戏仍要每步可验证，先有可编译示例再注册章节。井字棋当前的章节链覆盖 01 规则与终端、02 对手和 03 逐行协议；Python 回放与本地 Web 适配作为协议层之后的辅助程序维护。

## 井字棋阶段顺序

井字棋有三份可运行目录。`01-cli-game` 是双人终端。`02-cpu-opponent` 是人机，先选双人或人机，选人机后再选随机、启发式或 minimax 难度。`03-line-protocol` 在每次打印后追加版本化 JSON，包含九格、序号、轮到谁、状态和胜者；`games/tictactoe/python/replay.py` 只解析这行，不重判胜负。`games/tictactoe/python/web.py` 是只监听回环地址的本地 HTTP/Fetch 适配，复用 03 的终端协议，不属于 C++ 规则核心。

## 已实现阶段与辅助适配

02 与 03 已完成独立构建、CTest 和脚本验收。Python 回放已覆盖版本、字段和序号校验；本地 Web 适配已实现模式/难度选择、坐标校验、请求体上限、回环监听和子进程错误边界。HTTP 只作为本地辅助适配，不新增 `04-http-play` 阶段、不引入远程部署或 WebSocket。

人机对战的短需求：复制 `01-cli-game` 为 `games/tictactoe/02-cpu-opponent`。输入仍是一行两个整数。电脑的一步由 `tictactoe` 库里的 `ChooseMove` 产生 `Move`，再调用同一个 `Game::Place`。规则库不读终端、不选着。随机合法空格、能赢则赢否则阻挡、minimax（终局效用胜 `+1`、和 `0`、负 `-1`）三种强度放在同一目录。alpha-beta 只有在与不剪枝选出同一着时才留在这一阶段。验收是 CTest 覆盖必胜、必挡和双 minimax 开局成和，以及 `build-and-run.sh` 能完成一局人机。

逐行协议与回放的短需求：复制 `02-cpu-opponent` 为 `games/tictactoe/03-line-protocol`。标准输出在原有局面文本之外多一行版本化 JSON（版本、序号、九格、轮到谁、状态和胜者）。人的输入仍是两个整数。`games/tictactoe/python/replay.py` 解析这些行，用 `unittest` 检查协议，不重测胜负。读者章 `07-line-protocol.qmd` 用解析结果调用 `render_grid`。不引入 Flask、WebSocket 或 matplotlib。

`04-http-play` 不创建：本地 Web 适配已经存在于 `games/tictactoe/python/web.py`，但它不改变阶段路由，也不等同于可部署的 HTTP 产品。若未来需要正式服务，再另行定义认证、并发和部署边界。

## 阶段门槛

这一阶段必须能配置、编译、测试和运行。门槛写在本文件，不单设读者章。

## 测试框架时机

- `01-cli-game` 用 FetchContent 引入 GoogleTest `v1.17.0`，测试注册进 CTest。
- 管道棋谱是另一条 CTest：喂入固定着法，要求输出含有 `X 获胜`。脚本自己再用管道喂同一局。

## 架构边界

规则核心不依赖终端、GUI、Python、Web 或 Quarto。适配层只能通过明确动作和结果与核心交互；测试直接调用规则核心。先让井字棋具体实现成立，再根据至少两个游戏的真实共性考虑共享库。

## Agent 行为门槛

未获用户明确实现要求前只维护设计和文档，边界以根 `AGENTS.md`「工作规则」为准。Quarto 渲染成功不等于 C++ 构建或测试成功；文档只能把实际运行过的结果记录为已通过。
