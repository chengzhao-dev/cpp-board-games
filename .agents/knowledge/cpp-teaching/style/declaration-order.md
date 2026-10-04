---
kb_id: "bg-declaration-order-v1"
title: "声明顺序标准"
domain: "cpp-teaching"
subdomain: "style"
tags: [declaration-order, google-style, headers, code-review]
level_range: [0, 5]
dependencies: [bg-google-cpp-style-v1]
created: "2026-09-30"
updated: "2026-10-04"
chunk_strategy: "semantic_heading"
estimated_tokens: 900
---

# 声明顺序标准

类内顺序沿用 [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) 现行 Declaration Order 一节；命名空间作用域头文件的顺序 Google 未细写，本仓对齐 LLVM「相似声明分组」习惯并结合现有工程现状固定为下述 B 表。目的：任何人打开头文件能按「常量 → 类型 → 函数」的依赖顺序读下去，评审有逐条可核对的清单。

## A. 类内声明顺序

可见性段按 `public` → `protected` → `private` 排列；每段内部依次：

1. 类型与别名（`using`、嵌套 `enum class`）；
2. 仅 `struct` 可把非 static 数据成员放最前（聚合初始化需要）；`class` 不适用；
3. 静态常量（`static constexpr`，`k` 前缀）；
4. 工厂函数；
5. 静态无状态谓词（用户定案排在构造之前，如 `Board::IsValidPosition`；这类声明是类对外的边界检查入口，先于构造读更像能力清单）；
6. 构造、赋值、析构；
7. 其余成员函数；
8. 其余数据成员。

## B. 命名空间作用域头文件顺序

头文件自上而下按依赖方向排列，被依赖者在前：

1. 文件头横幅 + `#pragma once` + includes（分组见 `bg-google-cpp-style-v1` 各章采纳要点）；
2. `namespace` 打开；
3. `inline constexpr` 常量（`k…`，如 `kRows` / `kCols`）；
4. `enum class`（按依赖与主题分组；同一主题的状态码相邻，如 `Player`、`CellState` 相邻）；
5. `struct` 聚合类型（被依赖者在前：`CellPosition` 先于 `Move`）；
6. 自由函数（映射：`CellStateFor`；无状态谓词可作类内 public static 成员，如 `Board::IsValidPosition`）；
7. `namespace` 关闭。

## C. `.cpp` 定义顺序

对应头文件的 include 放第一位；函数定义顺序与头文件中声明顺序一致，读者在两个文件间往返时不需重新定位。拷贝/移动/析构等特殊成员在头文件只留声明，其 `= default` 与有函数体的定义都写在本文件；例外（用户定案）：零参默认构造在头文件类内写 `Board() = default;`，本文件不再重复定义。落点依据见标识 `bg-google-cpp-style-v1` 的知识文件「特殊成员」。

## D. 与教学摘录的关系

qmd 可以按教学顺序摘录源码，但正文不得暗示摘录顺序等于文件内顺序；需要点破时写一句「摘录顺序服务于讲解，文件内完整顺序见声明顺序标准」。判定：摘录跳过了中间成员、或顺序与源文件不同时，必须有这句或等效说明。

## 检查方式

代码评审按 `reviewing-code` 技能 `references/review-checklists.md` 的「命名空间头文件顺序」条目逐条核对；`.clang-format` 不约束声明顺序，本标准无法自动执行，属人审项。
