---
name: shipping-github
description: 维护 GitHub 展示、CI、提交和发布边界；准备发布或远端操作时使用
metadata:
  short-description: GitHub 展示与发布边界
---

# Skill: shipping-github

承载 README 展示、CI 边界、提交身份与远端操作边界。

## 适用场景

- 更新 README、准备发布或评估 CI 范围。
- 执行 commit、push、PR 等远端操作前的边界确认。
- **不适用**：文档内容写法（转 `writing-quarto`）、构建与测试执行（转 `cpp-development`）。

## 任务路由

| 任务 | 读取 |
| --- | --- |
| workflows 清单与 CI 范围 | `.github/README.md` |
| GitHub 链接约定 | `.agents/knowledge/quarto-writing/rendering/quarto-conventions.md` |

## P0 硬约束

1. README 负责入口，Quarto Book 负责完整展示；完整 STAR 与游戏细节不进根 README。
2. CI 只覆盖文档（Quarto 渲染与文档脚本）；不建编译游戏代码的 workflow，C++ 与 CTest 只在本地按改动阶段验证。
3. 提交 author/committer 只用用户身份（当前 `chengzhao-dev`）；提交信息不添加 `Co-authored-by`、`cursoragent` 等额外作者 trailer。
4. 用户明确 push 时，先检查近期提交作者集合（`git log --format='%an %cn' -n 30 | sort -u`）；出现非 `chengzhao-dev` 的作者即停止并报告。远端 Contributors 出现额外账号时默认只防新增，改写历史清理需用户明确授权。
5. 远端操作、commit、push 和 PR 只有用户明确要求时执行。
6. 用户可见行为变化应同步更新 README、Quarto 或游戏文档。

## 完成判据

- [ ] 发布前文档校验（`run.ps1 check --profile full` 或等价脚本）通过。
- [ ] 近期提交作者集合只含 `chengzhao-dev`。
- [ ] 未执行任何未经用户要求的远端操作。
