---
kb_id: "bg-terminal-output-style-v1"
title: "统一终端输出与日志规范"
domain: "cpp-teaching"
subdomain: "style"
tags: [terminal, stdout, stderr, logging, color]
level_range: [0, 5]
dependencies: []
created: "2026-09-26"
updated: "2026-09-29"
chunk_strategy: "semantic_heading"
estimated_tokens: 1400
---

# 统一终端输出与日志规范

本文件是全仓库生成和评审终端输出、进度展示与日志的唯一基准，覆盖 Bash 构建/辅助脚本、C++ 程序和未来的 Python 工具。Agent 生成任何会向终端打印内容的代码时必须遵循本规范。2026-09 依据 Google Shell、clig.dev、GNU Coding Standards、LLVM、Python Logging HOWTO、Homebrew 惯例联网核实后沉淀，来源见文末。注释本身的写法见 标识 `bg-comment-style-v1` 的知识文件。

## 流分流总则

- **stdout** 只放"产物"：程序的主输出、构建工具的原生输出。它可能被管道接给下一个命令或重定向成文件，必须干净可用。
- **stderr** 放"对话"：错误、告警和必要的进度提示。这样 `脚本 | tee log.txt` 时消息仍显示在终端上而不污染日志文件。
- Bash 中错误一律通过 `err()` 辅助函数输出（`echo ... >&2`），不允许散落的裸 `echo ... >&2`。
- C++ 中正常输出用 `std::cout`，错误/诊断用 `std::cerr`；Python 中用户可见结果用 `print()`，诊断走 `logging`（默认 stderr）。

## 步骤展示（Bash 构建脚本）

多步骤脚本（配置→编译→测试→运行）必须让用户在终端上一眼看出当前在哪一步。脚本输出段落统一称「步骤」：

1. 每个步骤开头打印一行 `==> N. 标题`，实现为 `header()` 辅助函数（Homebrew 安装器同款惯例）。
2. 相邻步骤之间用一个空行分隔：`header()` 在打印标题前先输出一个空行，多步骤连跑时各步骤在终端输出中一眼可分，也便于向上翻找"最靠近上方的失败步骤"。
3. 成功路径输出保持简短——底层工具（cmake/ninja/ctest）的原生输出已经足够详细，脚本不重复转述。
4. `set -e` 负责失败即停；配合 `trap 'err "构建流程失败"' ERR` 在 stderr 打印一条提示并保留非零退出码。
5. 不默认打印只有开发者才懂的调试信息；确需详细模式时用环境变量或参数显式开启。
6. `header()`、`err()` 与 `trap ERR` 归入脚本的「输出辅助」段横幅，不与「严格模式与工作目录」段的 `set`、常量混段（段落划分见标识 `bg-comment-style-v1` 的知识文件）。

### 纯文本输出

构建脚本默认使用纯文本标题和错误提示，不自行输出 ANSI 颜色。这样同一份输出在终端、重定向、管道和 CI 日志中保持一致，底层工具自己的颜色由工具自行决定。

## C++ 程序输出

- 结果输出用 `std::cout`，换行用 `'\n'` 而不是 `std::endl`（避免不必要的流刷新）。
- 错误与诊断写 `std::cerr`，格式 `程序名: 描述`（GNU 格式）：以大写字母开头、不以句号结尾、消息在 stderr 上自解释，不依赖上下文。
- 现阶段教学代码用 `<iostream>` 即可；LLVM 禁止库代码使用 `<iostream>` 并提供 `WithColor` 等彩色诊断处理器，属于大型 C++ 库实践，仅作后续参考记录，本仓库暂不采用。

## Python 输出与日志（未来阶段）

- 面向终端用户的简单结果用 `print()`。
- 过程诊断、可观测信息一律用 `logging` 模块，不用散落的 `print()`：
 - 级别语义：`DEBUG` 调试细节 / `INFO` 常规事件 / `WARNING` 可恢复问题 / `ERROR` 失败 / `CRITICAL` 致命。
 - 每模块 `logging.getLogger(__name__)` 取 logger；程序入口处 `logging.basicConfig()` 配置一次。
- 面向人的简短状态（如 CLI 进度）可以打印，面向机器的日志不要加颜色和表情。

## 杂项

- 非终端环境（管道、CI）不输出动画、进度条和颜色。
- 错误消息写给"需要修复它的人"：说明发生了什么、如何修复；同类重复错误合并展示。

## 来源

- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)——错误一律 STDERR、`err()` 函数范例、函数需声明输出流。
- [Command Line Interface Guidelines](https://clig.dev/)——stdout/stderr 分流、进度展示、成功输出简短。
- [GNU Coding Standards: Format of Error Messages](https://www.gnu.org/prep/standards/standards.html#Errors)——`program: file:line: message` 格式、大写开头、无句尾句号。
- [LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html)——诊断消息风格、库代码禁 `<iostream>`、WithColor 处理器（仅作参考）。
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)——级别语义、logger/basicConfig 用法。
- [Homebrew Manpage](https://docs.brew.sh/Manpage)——`==> ` 步骤标题惯例。
- OpenAI 无公开终端输出或日志风格指南，不作为依据。
