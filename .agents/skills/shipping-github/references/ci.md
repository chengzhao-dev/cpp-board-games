# CI 与 Actions（操作清单）

## GitHub Actions

本仓库工作流：`.github/workflows/pages.yml`（发布）、`.github/workflows/render-check.yml`（PR 渲染检查）。CI 只覆盖文档渲染与 agents/qmd 校验；C++ 与游戏代码不进 CI，只在本地对改动阶段运行 `build-and-run.sh`。

两个工作流都先执行 `sed -i 's|^python = .*|python = "/usr/bin/python3"|' config.toml`：config.toml 的 python 字段是仓库唯一解释器来源，CI 机器没有该路径，改写这一个字段即完成解释器切换，不引入第二份配置。

### pages.yml

- 触发：`push` 到 `main`，或 `workflow_dispatch`
- 步骤：checkout → setup Quarto → setup Python 3.12 → 改写 config.toml → `quarto render` → `peaceiris/actions-gh-pages` 推 `_book/` 到 `gh-pages`（`force_orphan`）→ 幂等校正 Pages source
- 权限：`contents: write`（推分支）、`pages: write`（调 Pages API）
- 并发：`concurrency: pages`，不取消进行中的发布，避免 gh-pages 半更新
- Pages 设置：Deploy from a branch → `gh-pages` / `(root)`（见 `github-pages.md`）

### render-check.yml

- 触发：PR 到 `main` 与 `workflow_dispatch`
- 步骤：`run.py check --profile fast`（编码、体量、文件名、链接、文档内容）→ `quarto render` → `run.py check --profile full`（全量，含渲染产物契约与知识库评测）
- 范围边界：C++ 游戏代码的配置、编译、CTest 与运行全部留在本地阶段脚本，不作为 CI 门禁。

## CI 持续集成与检查规范
官方依据：[GitHub Actions workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)、[GITHUB_TOKEN 权限](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)与 [Pages deployment](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

### 调试与排错

- CI 失败时先在本地用 `run.py check --profile full` 复现，游戏代码问题另跑对应阶段 `build-and-run.sh`；禁止盲目推 commit 试错。
- 每个 workflow 显式声明最小 `permissions`。新增步骤只申请实际需要的权限，并为部署步骤单独说明写权限来源。
