# Agent 记忆索引

这里是跨会话教训的唯一入口：回答「过去哪里容易出错」。每个任务开始时读本文件选择领域，再读该领域 `index.md`；需要完整失败复盘时转 `.agents/incidents/INDEX.md`。

## 领域

| 领域 | 管什么 |
| --- | --- |
| agent-workspace | 检索管线与评测闭环（`domains/agent-workspace/`） |

## 写入规则

- `MEMORY.md` 只做领域路由，不放正文。
- 每个领域一个 `domains/<domain>/index.md`（关键词 → 主题表）加若干原子主题文件；主题文件聚焦单一教训，领域随第一个教训创建，不预建空目录。
- 内容格式：`## 现象与根因` + `## 对策`；需要完整过程时链到 incidents 案例，不复制。
