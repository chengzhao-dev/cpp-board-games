# build-and-run.sh 步骤清单

阶段一键脚本的固定结构与验收步骤。机制取舍（RPATH 主路径、临时库加固、每次重新配置）见知识库：

- 脚本次序与横幅：标识 `bg-comment-style-v1`（`.agents/knowledge/cpp-teaching/style/comment-style.md`）
- 库路径封装与运行目录：标识 `bg-cmake-conventions-v1`（`.agents/knowledge/cpp-teaching/toolchain/cmake-conventions.md`）
- 步骤输出格式：标识 `bg-terminal-output-style-v1`（`.agents/knowledge/cpp-teaching/style/terminal-output-style.md`）

## 结构清单

1. shebang 第一行，其后文件头横幅（用途 + WSL 用法；SHARED 阶段注明临时库加固）。
2. 「严格模式与工作目录」段横幅：`set -euo pipefail`、`cd "$(dirname "$0")"`、`readonly STAGE_ROOT` / `STAGE_LIB`（仅 SHARED）/ `STAGE_BIN` / `APP_NAME`。
3. 「输出辅助」段横幅：`header()`、`err()` 与 `trap ERR`。
4. 「阶段库加固」段横幅（仅 SHARED）：`run_with_stage_libs()` 用 `env LD_LIBRARY_PATH="${STAGE_LIB}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"` 包住单条命令。
5. `main()`：1 配置（每次无条件重新配置）→ 2 编译 → 3 格式与静态检查（`clang-format --dry-run --Werror` 与基于 `build/compile_commands.json` 的 `clang-tidy`）→ 4 测试（SHARED 阶段经 `run_with_stage_libs` 调 `ctest`）→ 5 运行（子 shell `cd "${STAGE_BIN}"` 后执行 `./"${APP_NAME}"`）。
6. 文件末行 `main "$@"`。

## 验收清单

- `bash -n` 通过。
- WSL 中 `run.ps1 build <game>/<stage>` 全绿（配置、编译、格式与静态检查、CTest、运行）。
- 脚本结束后调用方 shell 的 `LD_LIBRARY_PATH` 未被改写；步骤 4 在子 shell 内工作目录为 `build/bin`，父脚本保持阶段根。
- 从阶段根不带 `env` 前缀直接运行 `./build/bin/app` 应当成功（验证 RPATH 主路径）。

主程序 target 命名依据见标识 `bg-cmake-conventions-v1` 的知识文件「组件化阶段布局」：可执行 target 固定 `app`，脚本常量固定 `APP_NAME`。
