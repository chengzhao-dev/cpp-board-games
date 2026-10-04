# 用本仓库初始化另一个仓库的 Agent 骨架

新仓库只拿走治理脚本和知识库管道，不拿走游戏、章节和已有知识正文。

在本仓库用 `config.toml` 的解释器执行：

```text
python .agents/skills/maintaining-python/scripts/scaffold/export_agent_skeleton.py <空目录>
```

目标必须是空目录。脚本写出一份短 `AGENTS.md`，并复制 `governing-agents` 与知识库管道脚本。它不复制 `content/`、`games/`、`game-design`、阶段路由和 incidents 案例。

新仓库自己填：项目一句话、目录表、不能从文件看出来的命令、安全不变量、`config.toml` 的 `python`、领域技能和 `kb_id` 前缀。第一个真实任务出现之前不预建空技能目录。不要在子目录再放 `AGENTS.md`。不要把 Python 来源改回 PATH 或 `runtime.json`。

初始化结束后跑 `kb-index` 和 `check --profile fast`。
