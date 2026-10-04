---
name: maintaining-python
description: 当任务需要运行、维护或迁移本仓库 Python 工具、知识库管道、维护脚本或其配置时触发。
metadata:
  short-description: 运行与维护仓库 Python 工具链
---

# Skill: maintaining-python

管本仓库 Python 脚本、知识库管道与运行时选择。检查项编排交给 `governing-agents`，知识正文交给 `.agents/knowledge/`。

## 适用场景

- 运行或修改 `scripts/` 下的知识库管道、脚手架与维护脚本，调整 Python 版本与格式化配置。
- **不适用**：检查顺序与子命令编排（转 `governing-agents`）、领域结论（转 `.agents/knowledge/`）、对局分析等游戏 Python 工具（转 `python-tooling`）。

## 任务路由

| 要做的事 | 读取 |
| --- | --- |
| 知识库管道（分块 / 索引 / 检索 / 评测 / 体检） | `scripts/`，规范见 `.agents/knowledge/KNOWLEDGE.md` 与 `retrieval/retrieval-governance.md` |
| Python 版本与格式化配置 | `assets/config/pyproject.toml` |
| 新建 C++ 工程骨架（目录名派生 PascalCase CMake 工程名） | `scripts/scaffold/init_project.py --layout single|multi|static-library|shared-library` |

## P0 硬约束

1. 仓库检查一律走 `.agents/skills/governing-agents/scripts/run.py`，不绕过它直接串脚本。
2. 运行时只读取根目录 `config.toml` 的 `python`（最低 3.12），不得使用环境变量、`runtime.json.python`、PATH 或 `sys.executable` 回退。字段缺失、路径不可执行或版本不足时立即中止，不伪造结果。唯一例外：向 Quarto 子进程注入 `QUARTO_PYTHON` 时，值必须来自同一 `config.toml` 字段（`run.py` 的 `render` / `preview`）。
3. 知识库正文只在根 `.agents/knowledge/`。所有项目临时产物（包括脚本测试、测量和基准的中间文件）统一写在 `temp/<用途>/`，索引产物写在 `temp/knowledge-index/`（均不入库）。统一检索协议见 `.agents/knowledge/agent-workspace/retrieval/retrieval-governance.md`。
4. 作用域、检索和索引统一跳过构建产物、Quarto 缓存、依赖目录、Python 缓存与密钥文件。规则来源是根目录 `.gitignore`，不依赖 `.agents/` 下的忽略文件。
5. 脚本改动后同步更新 `AGENTS.md` 命令表与 `run.py` 子命令说明。

## 工作流程

1. 先确认脚本归属目录（`scripts/`、`scripts/render/`、`scripts/scaffold/`、`scripts/maintenance/`）。
2. 用受控 Python 运行最小复现命令，失败才加 `--verbose`。
3. 改知识库管道后依次跑 `kb-index --rebuild`、`kb-check`、`kb-eval`。

## 完成判据

- [ ] `run.ps1 check --profile knowledge` 或 `python` 全通过。
- [ ] 相关 `test_*.py` 通过。未新增顶层脚本目录或空目录。
