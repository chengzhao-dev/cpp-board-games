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
| 脚本、回放和本地 Web 的边界 | 本文件，以及知识 `bg-roadmap-v1`「已实现阶段与辅助适配」。`games/<game>/python/` 已存在时在原目录内维护，不重复创建功能平行目录 |

## P0 硬约束

1. 推荐顺序：标准库和 `unittest` → `subprocess` 调用游戏 CLI → 版本化逐行 JSON → 回放/分析 → 本地 HTTP/Fetch 适配 → 实时需求明确后再评估 WebSocket 或 `pybind11`。
2. 每个游戏的专属 Python 内容放在 `games/<game>/python/`；回放、协议校验和本地 Web 适配共享该目录，不按功能再建平行顶层目录。
3. Python 测试验证脚本、协议和 HTTP 输入边界，不替代 C++ 规则测试；本地 Web 默认只绑定回环地址，不写远程部署或认证假设。

## 完成判据

- [x] Python 测试通过且不重复覆盖 C++ 规则测试。
- [x] 脚本职责、输入输出在游戏目录内有记录。
