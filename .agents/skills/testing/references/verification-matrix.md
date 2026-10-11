# 改动范围与验证矩阵

供 Agent 在改动后快速圈定验证范围。面向读者的终端验收在 `content/tictactoe/05-terminal-play.qmd`。

| 改动 | 对应验证 |
| --- | --- |
| 构建规则或工具链 | 被改阶段目录内的 `build-and-run.sh` |
| 棋盘和棋盘格子状态 | 初始状态、占格、越界 |
| 规则 | 错人落子、胜负、平局 |
| 终端 | 管道棋谱的输出和返回码 |
| 人机落子 | `games/tictactoe/02-cpu-opponent/build-and-run.sh` |
| 逐行 JSON | `games/tictactoe/03-line-protocol/build-and-run.sh`，以及 `games/tictactoe/python/replay.py` 的协议校验 |
| Python 回放 | `config.toml` 的 `python -m unittest games/tictactoe/python/replay.py` |
| 本地 Web 适配 | `config.toml` 的 `python -m unittest games/tictactoe/python/web.py`；必要时用浏览器黑盒测试页面与 API |
| Quarto、主题或代码块标题 | `verify_content.py`（content 项先切章、节、自然段、句、列表项、表元，再扫全部读者 qmd 的散文句，收类型接线句、「接着看／第 N 个枚举」改口、全称被下一句否定三类失败）、根目录 `quarto render` |
| C++、CMake、Bash 或格式注释 | 该目录 `build-and-run.sh` |

本地 Web 只监听回环地址，当前不作为可部署 HTTP 阶段验收；WebSocket 仍没有代码。

验证入口：各阶段目录内 `build-and-run.sh` 一键完成该阶段的配置、编译、格式与静态检查、CTest 和运行；根目录不放 CMake 文件，不做根级统一构建。文档改动运行 `verify_content.py` 与仓库根 `quarto render`。

## 闸次与退出

防止「验证验证」死循环：闸是验收，不是写作向导。命令模板（输出全部重定向，对话只读失败摘要）：

```powershell
& .agents/skills/governing-agents/scripts/run.ps1 verify --changed > temp/verify-<批次>.txt 2>&1
```

1. **先定形态再跑闸**：契约类改写（引言、同义堆叠、注释位置等）先对照目标形态把该批写完，再第一次跑闸；禁止把闸报错当逐条修改依据边写边闸。
2. **每批次只跑一次闸**：改完一组文件跑一次 `verify --changed`（或该批明确范围）；禁止未改文件又跑第二遍「确认一下」；`check --profile fast/full` 同纪律，每轮子目标至多一次。
3. **FAIL 与 WARN 分流**：FAIL 必须清零才算批次通过；WARN（启发式、风格类）只记台账人工判，不追清零——清 WARN 再生 WARN 是死循环主因。新增闸默认：机器能稳定判的才 FAIL，启发式保持 WARN。
4. **同指纹两轮停手**：同一 FAIL 指纹（规则名 + 文件 + 稳定行锚）连续 2 轮修复后仍红，立即停手记台账转人工，禁止「再试一次」。
5. **闸次硬顶**：单批次闸调用至多 2 次（首验 + 一次复验）；整项任务文档域闸调用软顶 6 次，超则停手汇报。
6. **回合收尾**：每轮以「已完成 | 阻塞 + 证据路径（temp/ 下的输出文件或退出码）」结束；禁止以「我再验证一下」收尾且不附证据。

长任务按批次推进的节奏仍按上表对应验证执行；本节只约束闸的调用次数与退出条件。
