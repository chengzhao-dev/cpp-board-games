---
name: python-tooling
description: 学习 Python 脚本并连接 C++ 棋盘游戏；编写对局驱动、分析脚本或 JSON 协议时使用
metadata:
  short-description: Python 辅助工具与 C++ 衔接
---

# Skill: python-tooling

Python 是本项目的正式辅助学习路线，不承担 C++ 核心规则。

## 适用场景

- 编写调用游戏 CLI、处理 JSON 或分析对局的 Python 脚本。
- 为游戏生成测试局面与分析报告。
- **不适用**：C++ 规则实现（转 `cpp-development`）、知识检索管线维护（本仓库暂无）。

## 任务路由

| 任务 | 读取 |
| --- | --- |
| Python 衔接路线与切片规划 | `content/tic-tac-toe/09-python-and-web-transition.qmd` |

## P0 硬约束

1. 推荐顺序：标准库和 `unittest` → `subprocess` 调用游戏 CLI → JSON 文件或标准输入输出传递游戏状态 → 生成测试局面、分析对局并输出报告 → 再评估本地 HTTP、Web 和 `pybind11`。
2. 每个游戏的专属 Python 内容放在 `games/<game>/python/`。
3. Python 测试验证脚本和接口，不替代 C++ 规则测试。

## 完成判据

- [ ] Python 测试通过且不重复覆盖 C++ 规则测试。
- [ ] 脚本职责、输入输出在游戏目录内有记录。
