# 发布闸门与上库内容

发布前验收的固定顺序与各步验证方式。为什么这样划界、风格维持哪些条目，见 kb_id `bg-publish-surface-v1` 的知识文件（检索入口：`run.ps1 kb-search "上库内容" --domain repo-github`）。

## 上库内容

`main` 上进 GitHub 的是未被 `.gitignore` 排除的源码；`gh-pages` 上只有 Actions 推上去的 `_book/`。以下内容不进任一分支：`build/`、`main` 上的 `_book/`、`.quarto/`、`temp/`、`.zcode/`、根目录 `.vscode/`。

## 闸门顺序

每批次只跑一次闸，输出重定向 `temp/`，对话只读失败摘要；闸次纪律见 testing 技能 `../../testing/references/verification-matrix.md`「闸次与退出」：

1. 确认生成物被忽略：`git check-ignore -v _book .quarto games/tictactoe/01-cli-game/build temp`，四条都应命中。
2. 文档与 `.agents`：在仓库根执行 `& .agents/skills/governing-agents/scripts/run.ps1 check --profile fast`。
3. 三个阶段各自构建：在 WSL 进入阶段目录执行 `./build-and-run.sh`（或根上 `run.ps1 build tictactoe/<阶段>`）。脚本内部顺序与 `01-cli-game/build-and-run.sh` 一致，02、03 同构：
   - 配置：`cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`
   - 编译：`cmake --build build`
   - 格式：`clang-format --dry-run --Werror`（跳过 `build/`）
   - 静态检查：`clang-tidy -p build --warnings-as-errors=*`，头过滤限定本阶段，排除 `build/_deps`
   - 测试：`ctest --test-dir build --output-on-failure`
   - 运行：管道喂入一局，输出必须含 `对局结果：X 获胜`
4. 改了 `games/tictactoe/python/` 才跑回放与本地 Web 的 `unittest`：解释器只用根 `config.toml` 的 `python`，不写本机绝对路径。
5. 改了 qmd、主题或 `_quarto.yml` 才 `run.ps1 render`，然后 `check --profile full`。
6. 改了知识才 `kb-index`、`kb-check`、`kb-eval`。
7. 用户要求推送时，CI 会重跑 `render-check.yml`（PR）或 `pages.yml`（`main`，workflow 步骤见 `ci.md`）。本地闸通过不等于已经发布。

## 前提

WSL Ubuntu、Clang、CMake 4.2、Ninja、CTest、clang-format、clang-tidy，环境口径见 kb_id `bg-development-environment-v1` 的知识文件。根目录没有 CMake，不存在仓库根的统一构建；三个阶段各自完整，缺哪个工具先补环境再过闸。
