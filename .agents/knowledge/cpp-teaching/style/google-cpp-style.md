---
kb_id: "bg-google-cpp-style-v1"
title: "Google C++ 风格落地决策"
domain: "cpp-teaching"
subdomain: "style"
tags: [google-style, naming, identifiers, headers, style-guide, clang-tidy]
level_range: [0, 5]
dependencies: [bg-comment-style-v1]
created: "2026-09-28"
updated: "2026-09-28"
chunk_strategy: "semantic_heading"
estimated_tokens: 1600
---

# Google C++ 风格落地决策

两仓（cpp-board-games 与 cpp-notes）的 C++ 标识符命名与编码规则以 [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) 为主标准，废止此前「函数与变量小驼峰」决策。本文件记录主标准的采纳范围、有意偏离的白名单与各章的检查方式；审查清单见 `cpp-development` 技能 `references/google-cpp-style.md`，可自动执行的部分由 `.clang-format`（`BasedOnStyle: Google`）与 `.clang-tidy`（`readability-identifier-naming` 等）承担。

## 命名表

| 类别 | 规则 | 示例 |
| --- | --- | --- |
| 类型（class/struct/enum/别名模板） | PascalCase | `GameState`、`ApplyResult` |
| 概念与模板参数（类型形参） | PascalCase | `Board` |
| 函数（普通、成员、访问器） | PascalCase | `IsValid`、`MarkAt`、`Apply`、`Status` |
| 变量与参数（含 lambda 捕获外的局部量） | snake_case | `position`、`table_name` |
| 类数据成员（含私有/受保护） | snake_case 加尾下划线 | `cells_` |
| 常量与 constexpr（含枚举子） | `k` 加 PascalCase | `kRows`、`Player::kX`、`Mark::kEmpty` |
| 命名空间 | snake_case | `tic_tac_toe` |
| 宏 | `UPPER_CASE` 且带项目前缀 | 尽量不使用宏 |
| 文件名 | snake_case（扩展名偏离，见下） | `game_state.h` |

命名翻转的影响面：函数从 camelBack 翻转为 PascalCase（`is_valid` → `IsValid`、`makeGreeting` → `MakeGreeting`），变量从 camelBack 翻转为 snake_case（`defaultLimit` → `default_limit`），枚举子补 `k` 前缀（`Player::X` → `Player::kX`）。查询型访问器同样用 PascalCase，避免同一章内混用两套函数命名。

## 有意偏离白名单

只允许以下偏离，其余章节默认按 Google 落地；新增偏离必须先改本表：

1. **`#pragma once`**：不用 path-based `#ifndef` include guard，教学与 Clang 生态下更简单。
2. **扩展名 `.cpp` / `.h`**：不用 Google 的 `.cc`。
3. **C++20**：本仓锁定 C++20，与指南的版本策略一致。
4. **异常**：规则核心与可测试 API 禁止用异常表达业务结果，用结果类型（`ApplyResult`、`GameStatus`）承担；CLI 与工具边界允许异常。相对指南「基本不用异常」，核心更严、边界略松。
5. **注释外形**：内容跟 Google（写意图与取舍，不复述代码），分段横幅跟 LLVM（见标识 `bg-comment-style-v1` 的知识文件）。
6. **不强制 cpplint**：用 `clang-format` 与 `clang-tidy`（含 `google-*` 可启用项）代替。

## 各章采纳要点

- **Header Files**：自包含头文件；include 顺序与分组（相关头 → C 系统头 → C++ 标准库 → 其他库 → 项目头，组间空行）由 Google `clang-format` 承担；头文件内函数定义仅限模板与简单函数；慎用前置声明。
- **Scoping**：头文件禁止 `using namespace`（检查 `google-build-using-namespace`、`google-global-names-in-headers`）；内部链接优先匿名命名空间；非 const 全局变量严控。
- **Classes**：单参构造 `explicit`（检查 `google-explicit-constructor`）；`struct` = 数据聚合、`class` = 不变量加行为（与标识 `bg-project-decisions-v1` 的类型形式决策一致）；声明顺序：类型 → 常量 → 工厂 → 构造/析构 → 方法 → 数据成员。
- **Functions**：短函数；重载优于易混淆默认实参；输出优先用返回值；不强制尾返回类型。
- **所有权与转换**：堆所有权用 `unique_ptr`，禁止裸 `new`/`delete`；禁止 C 风格转换，用 `static_cast` 等具名转换；指针判空用 `nullptr`；规则核心不依赖 `dynamic_cast` 做分支。
- **const 与整型**：只读接口标 `const`，编译期常量用 `constexpr` 加 `k` 命名；棋盘坐标用 `int` 可接受，跨 ABI 边界再考虑定宽整型。
- **Inclusive Language**：标识符与注释避免排斥性用语；中文教学语域另见标识 `bg-chinese-voice-register-v1` 的知识文件。

## 检查方式

- 可自动执行：`.clang-format`（排版与 include 分组）、`.clang-tidy` 命名选项与 `google-*` 启用项、`clang-tidy` 由 clangd 在编辑器内实时报告。
- 不能自动检查的条目（命名表语义、偏离白名单、声明顺序、所有权）：Agent 按 `cpp-development` 技能 P0 与审查清单把关，代码评审逐条核对。
