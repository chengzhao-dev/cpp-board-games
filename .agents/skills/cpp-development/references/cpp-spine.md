# 代码工序：唯一入口

所有改 C++、CMake、阶段脚本和三份 Clang 配置（`.clang-format`、`.clang-tidy`、`.clangd`）的任务先读本文件按工序走，禁止跳过本文件直接通读 references 或知识库。本文件只登记步骤和该步打开的文件与 `##`，不复制知识条文；冲突裁决：knowledge 条文 > 本文件的步骤登记。

本轮不改写根 `AGENTS.md`；同一步只打开登记的那一个文件和那一个 `##`；本轮已经读过的文件不重复读。

## 代码工序

从定行为到过闸依次走完；后一步发现前一步没做完，退回那一步，不在当前步补结构。

| 步骤 | 动作与产出 | 登记的依据 |
| --- | --- | --- |
| 1 定行为 | 本阶段新增的可观察行为 | `references/stages/<game>.md` 对应行 |
| 2 定边界 | 游戏库不依赖终端；配置属于阶段目录 | 知识 `bg-staged-game-layout-v1`、`bg-project-decisions-v1` |
| 3 定声明 | 命名、声明顺序、头文件契约 | `references/google-cpp-style.md` 对应节；知识 `bg-declaration-order-v1`；`bg-comment-style-v1` 的声明节（「声明注释块骨架」「标签规则」「枚举与常量行尾注释」） |
| 4 定实现 | `.cpp` 操作注释与分组空白 | `bg-comment-style-v1`「实现注释」「注释位置：上方 vs 行尾」 |
| 5 定构建 | target、`compile_commands.json` | 知识 `bg-cmake-conventions-v1` 对应节 |
| 6 定工具配置 | 三文件各走自己的注释粒度 | `bg-comment-style-v1`「键值配置」下对应文件的三个小节 |
| 7 过闸 | 该阶段 `build-and-run.sh` | 闸的登记在 `.agents/skills/testing/references/verification-matrix.md` |

注释是代码工序的支线，不另建中心：第 3、4、6 步按任务打开 `bg-comment-style-v1` 的对应节，正反对照见 `bg-comment-cases-v1`。
