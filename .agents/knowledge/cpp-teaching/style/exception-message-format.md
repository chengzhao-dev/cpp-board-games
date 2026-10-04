---
kb_id: "bg-exception-message-format-v1"
title: "异常与错误文案规范"
domain: "cpp-teaching"
subdomain: "style"
tags: [exceptions, error-messages, out-of-range, logging]
level_range: [0, 5]
dependencies: [bg-google-cpp-style-v1, bg-terminal-output-style-v1]
created: "2026-10-01"
updated: "2026-10-04"
chunk_strategy: "semantic_heading"
estimated_tokens: 700
---

# 异常与错误文案规范

本文件规定井字棋等教学阶段何时用异常、何时用结果类型，以及 `what()` 文案格式。日志框架选型不在本阶段范围。

## 何时抛异常

- **契约违反 / 硬边界**：查询 API 的边界失败（如 `GetCellState` 收到非法坐标）可抛 `std::out_of_range`。`Board` 在读写前先用 `IsValidPosition` 检查；异常是调用方可观察的失败信号。
- **业务结果**：合法对局中的拒绝（越界落子、占格、轮次不符）用结果类型（`PlaceResult::kRejected`、`GameResult`），**禁止**用异常表达。
- **CLI / 工具边界**：进程入口可捕获异常并写 `std::cerr`；不把异常当正常控制流。

相对 Google「基本不用异常」：本仓核心对业务结果更严，对契约违反与 CLI 边界略松。依据见标识 `bg-google-cpp-style-v1` 的知识文件偏离白名单第 4 条。

## 本阶段不用日志框架

- 不引入 Abseil Logging、glog 或同类框架；教学 CLI 的可观测性成本远大于收益。
- 正常输出用 `std::cout`，诊断用 `std::cerr`（见标识 `bg-terminal-output-style-v1` 的知识文件）。
- 异常消息本身就是契约失败的诊断载体；不要为同一事件再叠一层日志宏。

## what() 文案格式

1. **语言**：英文（与 STL / 常见工具链诊断一致）。中文只用于面向玩家的 CLI 文案。
2. **句式**：`<ApiName>: <subject> <reason>`，单行、无换行；句末可不加句号。
3. **subject**：优先领域对象名（`position`）；需要排障时再带值，如 `position (row=3, col=0)`。
4. **reason**：固定短语，同一 API 全仓同一措辞。常用：`is outside the board`、`is out of range`。
5. **禁止**：中英混杂、堆栈式长文、把业务拒绝写成 exception 文案、依赖日志库拼消息。

### 定稿示例

```cpp
throw std::out_of_range("GetCellState: position is outside the board");
```

本阶段默认用无坐标短句。测试用 `EXPECT_THROW(..., std::out_of_range)`；若断言 `what()`，锁上述短句。头文件注释须写明：非法坐标抛 `std::out_of_range`。
