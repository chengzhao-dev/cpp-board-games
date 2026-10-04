---
kb_id: "bg-static-analysis-boundaries-v1"
title: "C++ 静态检查的项目边界"
domain: "cpp-teaching"
subdomain: "toolchain"
tags: [clang-tidy, clang-format, clangd, header-filter, system-headers, compile-commands, cmake, dependencies]
level_range: [0, 5]
dependencies: ["bg-cmake-conventions-v1", "bg-comment-style-v1"]
created: "2026-10-01"
updated: "2026-10-01"
chunk_strategy: "semantic_heading"
estimated_tokens: 1200
---

# C++ 静态检查的项目边界

## 日常门禁范围

项目质量门禁应把传入 clang-tidy 的项目源文件和项目自己的头文件作为范围。`compile_commands.json` 记录所有 CMake 编译单元的真实参数，但不表示数据库中的第三方源码都必须接受本项目的诊断规则。GoogleTest、系统库和生成目录属于依赖或构建环境，应由其自身维护或在单独审计中检查。

日常命令不传 `--system-headers`。该选项会扩大到系统头文件，不能用来实现“只检查自己库”。`--header-filter` 只决定头文件诊断显示范围，不能替代明确的源文件清单。

## 诊断数量与动态下标

“warnings generated”是模板实例化和预处理路径的计数，不等于独立缺陷数量。先看诊断行的路径和检查名，按项目源文件、项目头文件、第三方头文件、系统头文件和汇总行分类；没有 `--system-headers` 时，不应直接把数字称为系统库警告。

`cppcoreguidelines-pro-bounds-constant-array-index` 不理解跨函数的 `IsValid` 前置条件。它指出动态 `operator[]` 缺少工具可见的边界证明，不等同于编译错误或必然越界。公共查询接口应先验证坐标，再使用 `std::array::at` 或项目明确的边界辅助函数；测试负数、行越界和列越界。只有局部边界已经证明时，才允许紧贴表达式的 `NOLINT`，**不能**在 `.clang-tidy` 里全局 `-` 关闭该检查。

## 配置注释职责

Google 主标准、偏离白名单与 `at()` 选型论证写在本文件与标识 `bg-google-cpp-style-v1` 的知识文件，不写进 `.clang-tidy` / `.clangd` / `.clang-format` 文件头。三配置的短横幅与邻接注释外形见标识 `bg-comment-style-v1` 的知识文件「工具配置 YAML」。
