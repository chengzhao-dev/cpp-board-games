# 向 Agent 提问

只做第 2 节线框里的事。线框是空的，就停下来向我要需求，不要自己编任务，也不要自己选子计划。

## 1. 提问要求

先写计划，先不要改仓库文件。你把计划写成子计划，我确认后再执行。每个子计划写明要改的文件、改成的原句，以及通过哪一条命令才算完成。事情多就按依赖排成先后几段，前一段的出口命令没通过，就不进入下一段。句子要落到具体文件和原句上，不要写「优化一下」或「处理相关问题」。

材料先收成写入位置，一条只进一个已有文件。删掉就会每轮做错的，在根目录 AGENTS.md 加一句；步骤和完成判据放进已有技能的 reference。相关的 .agents 条文按职责拆开、收短、归位，不另建一套目录。执行中若出现构建冲突，先写出原因和改法，再继续。

要对照多份文件里的原句，并且这些文件能分成 2 到 10 份互不重叠的范围时，在该子计划开头写下同样数量的调用块。ZCode 同一轮一次发出这一段，交齐后再改。DeepSeek 同一条消息至多发出 5 块，余下的块等这一批交回后再发出，整段交齐后再改。DeepSeek 见到 `In-flight request cap reached` 时下一批改为更少块，不原样重发，这次不计块失败。少于 2 份时不写调用块，你自己读原句。超过 10 份时，本段最多放 10 块，其余范围写成下一段。不要把同一文件拆成两块来凑数。每一块都是这五行：调用：只读核对，交齐再改；任务：要找的原句和判定，这句话必须自带判定；范围：只列这一块的文件；交回：路径、行号、原句，不改文件，不交改写稿；没有交回就停：阻塞：缺只读核对交回的路径。交回零条算已经交回。这一行「没有交回」只指出启动即被拒绝，或完成通知写明失败、中止、token 上限。仍在执行不使用这一行。有多种做法时先列出利弊，等我选定再写进计划。不要新建 ~/.zcode/agents/ 里的角色。

线框里如果写的是执行已经确认的某一段，就只做那一段。先数这一段的调用块。有 2 到 10 块时，ZCode 同一轮一起发出；DeepSeek 同一条消息至多 5 块，余下的块等这一批交回后再发出。整段都交回路径、行号和原句之后再改文件。少于 2 块时不要拉起，你自己线性读完再改文件，没有调用块也一样。超过 10 块时停住，写下「阻塞：本段调用块超过 10」，不要改文件。DeepSeek 同一条消息已有 5 块时，其余块留到下一条消息，不停在这一句。没有交回就停，不要改文件；交回零条算已经交回，计划里已经写死的句子照改。「没有交回」只指出启动即被拒绝，或完成通知写明失败、中止、token 上限；仍在执行时本轮不写「已完成」或「阻塞」，也不再发工具调用。这一段的出口命令没通过，就停，不要做下一个子计划。

## 2. 本次需求

======================================== 本次需求 ========================================

(1) 重构的方向：

(2)

像下面的内容，我感觉下面的 IsDraw 方法里面的 GetWinner() == CellType::kEmpty 调用其实就是 IsWin，那这样直接把 IsWin 函数拿过来就好了，不需要像现在这样子。

bool Board::IsWin() const {
  return GetWinner() != CellType::kEmpty;
}

bool Board::IsDraw() const {
  return IsFull() && GetWinner() == CellType::kEmpty;
}

像下面的命名，是否使用 stored_cell 比较好
CellType& stored = cells_.at(position.row).at(position.col);






然后是现在校验下，dsh-quarto-book 插件 token 量，准确率等一个 deepseek harness 基础插件的功能是否合格，还是拿 cpp-boarg-games 作为例子。





在现在规则基础上，帮我设计一个合理的方案来解决上述问题，方向由我来决定，需要修改所有涉及到的文件和内容。



======================================== 本次需求结束 ========================================

## 3. 重构范围

第 2 节线框里的「(1) 重构的方向」从下面这些词里选一个填上。没填时按「本次需求」这一档做，只改线框里点名的内容。

- 本次需求：只改线框里点名的内容。
- 全仓：重构项目里的全部内容。
- 文档：重构全部 qmd 和 README.md。
- 代码：重构 games/ 下面的全部代码。
- 布局：重构整个仓库的目录、文件名和布局；同时重构 .agents 里的各个子模块，以及子模块下面的内容，包括 Markdown 规范、Markdown 里 Agent 规则的排版，以及同类排版。

可以只选一档，也可以在线框里另外写明比这些档更窄的文件。「(1)」留空时，不扩大到全仓、文档、代码或布局。

重构按这个次序做：先改 .agents 里的规则，再改相关脚本，然后按 .agents/skills/governing-agents/references/structure.md「分层加载与全量润色调用序」里已经写明的主流程，去改 qmd、games 等后面的文件。

## 4. 重构要求

重构分两段做：先写计划，再按计划改仓库。两段都要对照第 3 节选定范围内已经写好的内容，检查会不会和这些内容冲突。

1. 写计划时，逐条对照已有规则、章节和代码。某一条和已有原句冲突，就在该子计划里写明冲突的文件、原句和取舍，不把互相打架的改法写进同一段。
2. 按已经确认的计划改文件时，再对照一次已有内容。执行中出现下面这些问题，以及其他改项目时常见的问题，就在当前这一段里实际改掉，写明原因和改法，再跑这一段的出口命令。问题没有改掉，就不进入下一段。
   - 冲突：同一件事有两种互不相容的写法或规则。
   - 冗余：同一件事写了多处，留一处就够。
   - 缺失：点名的文件、原句或步骤不在仓库里，或改完后引用处对不上。

## 5. 参考资料

下面三类只给方向，不是必须读完的清单，也不限制只能看这些链接。写计划时先看第 2 节线框里的需求，再按那个需求自己检索，包括联网搜索清单以外的页面。清单里的链接能对上需求时再打开，对不上就不必读。查到的内容只取和需求有关的结论，不把网页正文抄进子计划。

### Agent 资料

主 Agent 自己回答。子智能体只交回划定的结果。一段 2 到 10 个。ZCode 同一轮一次发出。DeepSeek 同一条消息至多 5 个。

- [OpenAI Agents 编排](https://developers.openai.com/api/docs/guides/agents/orchestration)：本仓只用「把 Agent 当工具」，不用交接。
- [agents.md](https://agents.md/)：仓库说明放这里，不放谁在哪一步被拉起。
- [ZCode 子智能体](https://zcode.z.ai/cn/docs/subagents)：前台同时启动的多个子智能体并行，主任务等它们全部完成。产品文档没有写个数。
- [ZCode 工具调度](https://daiw.org/manual/zcode/tool-executor)：默认同组最多 10 个并发调用，`Agent` 在其中。第 11 个会进入下一组，本仓因此把 ZCode 同一轮上限定为 10。DeepSeek 同一条消息至多 5，步骤在 `subagents.md`。
- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)：官方仓库，文档站是 [deepseek-harness.github.io/deepseek-harness](https://deepseek-harness.github.io/deepseek-harness/)。本仓不引入 dsh，不把宿主配置写进仓库。
- [插件配置目录](https://deepseek-harness.github.io/deepseek-harness/reference/config-catalog)：`dsh-agent-loop` 的 `maxParallelToolCalls` 管同一步里并行安全的工具调用；`dsh-subagent` 的 `maxActiveSubagents` 默认 8，只限制可续接子代理，`maxDepth` 默认 1。本仓不把这两个默认值当成同一条消息的委托上限，上限仍以 `subagents.md` 为准。
- [子代理](https://deepseek-harness.github.io/deepseek-harness/reference/subsystems/subagent)：一次执行和可续接会话是两种形状。`send_message` 只在相邻的本机会话之间。
- [工具 Schema 目录](https://deepseek-harness.github.io/deepseek-harness/reference/tool-catalog)：`subagent` 启动后立刻返回 id，结束时才通知，中间步骤不回到父会话。
- [Shell 执行器](https://deepseek-harness.github.io/deepseek-harness/reference/subsystems/shell)：面向模型的命令走 Bash 或 PowerShell 提供方。本仓代理只打 PowerShell，不另加 bash 工具，依据在 `development.md`。
- [讨论区](https://github.com/deepseek-ai/deepseek-harness/discussions)：问题解决先查这里。[#3819](https://github.com/deepseek-ai/deepseek-harness/discussions/3819) 记录推理要调别的工具、动作却连续发出成功的 `bash` 和 `echo`。不把讨论正文抄进仓库。

### C++ 编程资料

标识符、头文件和检查以 Google C++ 风格为主。具体类型和资源管理对照 C++ Core Guidelines。

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)：本仓标识符和头文件的主标准。
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)：具体类型、RAII、窄接口。
- [cppreference](https://en.cppreference.com/w/cpp)：查语言机制的定义。
- [LLVM Coding Standards](https://llvm.org/docs/CodingStandards.html)：注释分层和文件头。

### C++ 写作资料

章的外形对照 Learn C++，章内顺序对照 C++ Primer，单个函数小节的内部顺序对照 cppreference。

- [Learn C++](https://www.learncpp.com/)：标题只承诺一件做完能做的事。
- C++ Primer（第 5 版）：章内由易到难，零件讲完再讲调用它们的程序。这里不附全文链接。
- [cppreference 文档体例](https://en.cppreference.com/w/Help:Manual_of_style)：第一句概括行为；小节内部先声明，再一句行为，再实现。
- [ISO C++：Get Started](https://isocpp.org/get-started)：外部入门书单。本仓教学顺序用「先能跑再补强」与此对照。
