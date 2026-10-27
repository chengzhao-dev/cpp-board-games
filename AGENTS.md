# Agent 工作标准

本文件只写本仓硬约束。通用 C++、Quarto 与 Git 流程由插件技能提供，工程事实读 `.agents/skills/cpp-workflow-project/SKILL.md`，章节与检查规则读 `.agents/skills/quarto-book-project/SKILL.md`。

## 每轮硬约束

1. 先跑 `python .agents/scripts/scope.py <改动单元>`，只读它列出的文件与命中技能的 `SKILL.md`。多词文件名和目录名用 `designing-theme` 这种动词现在分词加对象；`config.toml` 这种一个词的文件和工具规定的原名保持不动。
2. 按改动域进入技能步骤：改 qmd 或中文读者正文进插件 `writing-quarto` 与本仓 `quarto-book-project`；改 C++、CMake 或阶段脚本进插件 `developing-cpp`、`configuring-cmake`、`building-cpp` 与本仓 `cpp-workflow-project`；改 `.agents` 规则只改权威文件本身，不另建一份复述。
3. 收到要归档的成段材料时，先出写入位置计划，用户确认后再改文件。
4. 改动完成前：改过 qmd 就跑 `python .agents/scripts/checking-book.py`；改过 `games/` 就跑 `python .agents/scripts/building-wsl.py <game>`。构建脚本当前只做配置、编译、CTest 与最小入口运行，Debug 一轮；根目录不构建。
5. 规划、解释、搜索和评审默认只读；用最少、可验证的改动解决问题，不做无关重构。同一判断只留一个权威文件。`.agents` 下每份 Markdown 整文件不超过 4000 token。
6. 游戏核心不得依赖终端、GUI、Web、Python 或 Quarto；跨游戏共享库只在至少两个游戏真实复用且语义稳定后提取。一章只有一个关键，对照见 `.agents/skills/quarto-book-project/writing/chapter-map.md`。布尔谓词用肯定式 `Is/Has/Can/Completes`，`Check/Validate` 只用于会报告错误或产生诊断的操作。
7. 提交与推送默认不做；只有用户明确要求时才按插件 `shipping-github` 执行，提交信息用 `type(scope): 中文说明`。贡献者只有 `chengzhao-dev`：commit 的 author 与 committer 必须是用户身份，禁止把 AI 或第三方写进 `Co-authored-by:` 等 trailer；push 前检查近期提交作者集合，出现非 `chengzhao-dev` 即停止并报告。
8. Python 解释器只读 `config/config.toml` 的 `python`（最低 3.12）；字段缺失或不可执行时立即停止，不回退 PATH。代理用 dsh-ops 的 `ops_bash` 执行仓库命令，不在 PowerShell 会话里手写 `bash -lc`、`python -c`；`quarto` 只在渲染或核对 HTML 时直接调用。重定向合并标准错误只写 2>&1；除 temp/ 外不在仓库里新建输出文件。
9. 面向用户的进度、结论和总结使用中文；命令、路径、代码和 API 名保留原文。成功只回一行中文结论，失败先给结论再附最少诊断。不回显密钥、凭据、`.env` 或无关个人信息。
10. 永不读取或索引 `_book/**`、`games/**/build/**`、`.quarto/**`、`.cache/**`、`.tmp/**`、`temp/**`。中文文件的主编码是 UTF-8 无 BOM、LF；机器规则以根 `.gitattributes` 与 `.editorconfig` 为准，`.bat`/`.cmd` 用 CRLF。
11. Plan Mode 严格只读：不写文件、不编译、不渲染；只有用户发来新的明确批准消息后才进入执行。
12. 有 goal 时，一轮只做当前文件和它的那条检查；检查通过就在同一轮结束 goal，不再继续走没失败的步骤。没有 goal 的长任务每轮只推进一个可验证子目标。收尾只能是「已完成：本轮路径或退出码」或「阻塞：缺的那一个路径」。同一阻塞连续 2 轮没有新证据即停手。子计划里同一段的只读核对为 2 到 10 块；DeepSeek 同一条消息至多发出 5 块，余下的等这一批交回后再发出。

## 常用命令

统一由 `config/config.toml` 的 `python` 指定解释器执行（最低 3.12）：

| 命令 | 用途 |
| --- | --- |
| `python .agents/scripts/scope.py <game>/<stage>` | 输出最小读取作用域 |
| `python .agents/scripts/checking-book.py` | 校验全部章节正文 |
| `python .agents/scripts/building-wsl.py <game>` | 在 WSL（Windows）或本机 bash（CI）中运行 `games/<game>/running-build.sh` |
| `python .agents/scripts/checking-plugins.py` | 检查已安装的 dsh-quarto-book 与 dsh-cpp-workflow 是否完整可用 |
| `python .agents/scripts/checking-ci.py` | 本地复现 CI：章节检查与各游戏构建；加 `--render` 连整书渲染 |
| `bash games/<game>/running-build.sh`（Linux CI 直接调用） | Debug 配置、编译、CTest 与最小入口运行 |
| `quarto render` | 在仓库根渲染 Book |

## 项目结构

| 路径 | 职责 |
| --- | --- |
| `content/`、`index.qmd`、`_quarto.yml` | Quarto Book 读者文档 |
| `games/<game>/` | 单个游戏的一份工程，可独立配置、编译和运行；井字棋 `games/tictactoe/` 当前构建动态库、`app` 与棋盘测试，终端层保留源码 |
| `.agents/scripts/` | `scope.py` 读取边界、`checking-book.py` 正文检查、`building-wsl.py` 构建入口、`checking-plugins.py` 插件体检、`checking-ci.py` 本地 CI |
| `.agents/skills/cpp-workflow-project/` | 井字棋工程事实、阶段表与架构决定 |
| `.agents/skills/quarto-book-project/` | 章节对照、术语表与内容检查配置 |
| `theme/`、`filters/` | Quarto 消费的主题副本与过滤器；权威在插件 `designing-theme` 与 `writing-quarto` |
| `temp/`、`games/**/build/`、`_book/`、`.quarto/` | 生成物与缓存，不入库 |

游戏章节与代码目录的对应关系登记在 `.agents/skills/cpp-workflow-project/stages/stage-table.md`。
