# 贡献指南

本仓库由 [chengzhao-dev](https://github.com/chengzhao-dev) 单人维护，提交只来自维护者。阅读中发现的问题与建议请开 Issue 讨论。

## 在本地运行

克隆仓库后，按 [README](README.md) 的「在本机运行」在 WSL 中构建三个可运行目录；回放脚本与本地网页的运行方式也在那里。

## 改动边界

- GitHub Actions 只检查在线书与 `.agents/`（Quarto 渲染与文档校验）；游戏代码不进 CI，改动后在对应目录执行 `running-build.sh`。
- 修改仓库前先读 [AGENTS.md](AGENTS.md)：它是内容、代码、工具与验收边界的唯一入口。
