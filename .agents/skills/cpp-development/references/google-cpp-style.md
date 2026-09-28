# Google C++ 风格检查清单

写或改 C++ 代码时按本清单自查；采纳范围、命名表与偏离白名单的依据见知识库 `bg-google-cpp-style-v1`。自动执行部分由 `.clang-format` 与 `.clang-tidy` 承担（clangd 在编辑器内实时报告命名违规），本清单管自动检查覆盖不到的条目。

## 标识符命名

- 类型、函数用 PascalCase（`GameState`、`IsValid`）；变量、参数用 snake_case（`position`）。
- 类数据成员带尾下划线（`cells_`）；常量与枚举子用 `k` 前缀（`kRows`、`Player::kX`）。
- 命名空间 snake_case（`tic_tac_toe`）；宏尽量不用，必须时 `UPPER_CASE` 带项目前缀。
- 同一 API 不得混用两套函数命名：查询型访问器也用 PascalCase（`MarkAt`、`Status`）。

## 头文件

- 头文件自包含：单独编译不缺声明；include 按组排序（相关头 → C 系统头 → C++ 标准库 → 其他库 → 项目头），组间空行，由 `clang-format` 维护。
- include guard 用 `#pragma once`（有意偏离 Google，白名单第 1 条）。
- 头文件内不写 `using namespace`；函数定义仅限模板与简单函数。

## 类与函数

- 单参构造 `explicit`；`struct` 只做数据聚合，带不变量的类型用 `class`。
- 声明顺序：类型 → 常量 → 工厂 → 构造/析构 → 方法 → 数据成员。
- 输出优先用返回值；重载优于易混淆默认实参；不写尾返回类型。

## 转换与所有权

- 禁止 C 风格转换，用 `static_cast` 等具名转换；指针判空用 `nullptr`。
- 堆所有权用 `unique_ptr`，禁止裸 `new`/`delete`；规则核心不用 `dynamic_cast` 做规则分支。

## 异常与注释

- 规则核心与可测试 API 用结果类型表达业务结果（`ApplyResult`、`GameStatus`），不用异常；CLI 与工具边界允许异常。
- 注释内容写意图与取舍、不复述代码；分段横幅与注释语言按知识库 `bg-comment-style-v1`。
