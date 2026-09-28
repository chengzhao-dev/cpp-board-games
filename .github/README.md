# GitHub 展示与 CI

CI 只覆盖文档：Quarto 渲染与文档脚本校验。C++/游戏代码不进 CI，只在本地、且仅当有相关改动时经对应阶段的 `build-and-run.sh` 验证。

## Workflows

| workflow | 触发 | 内容 |
| --- | --- | --- |
| `render-check.yml` | PR / 手动 | 文档脚本校验（编码、体量、qmd 规则）+ `quarto render` + 渲染产物抽查 |
| `pages.yml` | push main / 手动 | 渲染并发布 `_book/` 到 gh-pages |

## 贡献者

提交作者与 committer 只用 `chengzhao-dev`；提交信息不添加 `Co-authored-by: Cursor` 等额外作者 trailer。push 前检查近期提交作者集合，出现其他作者即停止并报告；如需改写历史清理 Contributors，须用户明确授权。
