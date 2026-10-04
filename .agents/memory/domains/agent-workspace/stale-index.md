# 知识库索引陈旧导致 full 误报失败

## 现象与根因

编辑 `.agents/knowledge/**` 或 `.agents/skills/**` 后直接运行 `check --profile full`，知识库项失败（`kb-check` 报 stale>0），而文件本身没有格式问题。根因是索引快照落后于文件修改时间：本轮凡是动过知识文件，`full` 都会先撞上一次陈旧失败。

## 对策

编辑知识文件或技能文件后、跑 `full` 之前，先执行 `run.ps1 kb-index` 重建索引，再跑 `full`。`kb-index` 幂等且开销小，把它当作知识域改动的固定收尾步骤，不要等到 `full` 失败才补。
