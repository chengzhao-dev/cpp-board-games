"""知识库检索评测集。

每个查询只保留一个高价值时，预期片段写成当前知识文件的真实标题。
这组样本覆盖全部保留文件，同时避免同一结论被大量改述重复计分。
"""

TOOLING = [
    # cpp-teaching/toolchain：CMake、构建与库
    ("为什么每次都要无条件重新配置", "构建目录与缓存", "procedure"),
    ("根目录为什么不放 CMake 文件", "构建入口与根目录边界", "concept"),
    ("target_compile_features 声明 C++20", "C++ 标准声明方式", "concept"),
    ("可执行文件和库输出到哪个目录", "产物输出目录", "concept"),
    ("动态库程序运行时怎么找到库文件", "动态库运行时查找", "concept"),
    ("GoogleTest 在什么时机引入", "GoogleTest 引入约定", "concept"),
    ("clangd 为什么需要编译数据库", "clangd 与 CMake 配套", "concept"),
    # cpp-teaching/style：注释与终端输出
    ("源码文件头部的横幅注释写什么", "文件头", "concept"),
    ("CMakeLists.txt 的注释怎么分段", "CMakeLists.txt 注释分段", "concept"),
    ("脚本输出里的 ==> 阶段标题", "步骤展示（Bash 构建脚本）", "concept"),
    ("C++ 程序的终端输出遵循什么风格", "C++ 程序输出", "concept"),
    ("函数名用 PascalCase 还是小驼峰", "命名表", "concept"),
    ("枚举子用什么命名", "命名表", "concept"),
    ("哪些 Google 规则允许偏离", "有意偏离白名单", "concept"),
    ("头文件里能不能写 using namespace", "各章采纳要点", "concept"),
    # agent-workspace/navigation：阶段布局
    ("编号阶段目录里配置文件放在哪", "阶段项目定义", "concept"),
    ("章节编号和阶段编号对不上以什么为准", "章节映射规则", "concept"),
    ("尚未实现的阶段能不能先建空目录", "实现方式边界", "concept"),
    ("每个阶段的 build-and-run.sh 承担什么", "阶段脚本与文档展示约定", "concept"),
    # agent-workspace/planning：流程、决策与路线
    ("开发的八个步骤各由谁做", "八步开发流程", "procedure"),
    ("STAR 摘要写进哪些章", "STAR 四段模板", "concept"),
    ("报错记录应该沉淀到哪里", "八步开发流程", "concept"),
    ("AI 生成代码前人要做哪些事", "八步开发流程", "procedure"),
    ("跨游戏共享库什么时候提取", "架构决策", "concept"),
    ("WebSocket 或 GUI 这类未来能力怎么决策", "未来能力口径", "concept"),
    ("游戏核心为什么不能依赖终端和 Web", "架构边界", "concept"),
    ("井字棋的编号目录从最小到完整怎么排", "井字棋阶段顺序", "concept"),
    # agent-workspace/retrieval：检索治理
    ("改知识库正文后要按什么顺序验收", "评测闭环", "procedure"),
    ("单次知识检索最多注入多少 Token", "统一检索协议", "concept"),
    ("memory 和 incidents 各自什么时候读", "职责边界", "concept"),
    # quarto-writing/writing：骨架与标题
    ("无标题引言、任务序列、常见错误的页面顺序是什么", "六段块序列", "concept"),
    ("游戏首章和末章各承担什么", "六段块序列", "concept"),
    ("规划页和实现页的骨架差异是什么", "六段块序列", "concept"),
    ("title 和二级标题各限制多少字", "字数硬限", "concept"),
    ("标题不加冒号、破折号和括号补充", "形式规则", "concept"),
    ("无标题引言承担哪三件事", "六段块序列", "concept"),
    ("页面篇幅超了先删什么", "凑字数禁令", "procedure"),
    ("什么时候用有序列表什么时候用无序列表", "列表选择", "concept"),
    ("自测答案要怎么折叠", "多问一答拆分", "concept"),
    ("一段最多容纳几个主题", "段落规则", "concept"),
    ("相邻段落各讲各的怎么修", "段间：过渡句只在话题切换处", "procedure"),
    ("过渡句写在什么位置", "段间：过渡句只在话题切换处", "concept"),
    ("口语讲义腔为什么不合格", "两轴禁例与允许写法", "concept"),
    ("规划页引言的状态说明怎么写", "对照案例", "procedure"),
    ("篇幅预算怎么计算 token", "计数口径", "concept"),
    ("单个二级标题最多几个盒子", "盒子与正文的比例", "concept"),
    # quarto-writing/writing：元素与案例
    ("代码块标题里的 filename 写什么", "代码块 filename 标注", "concept"),
    ("代码片段的省略怎么表示", "代码块 filename 标注", "concept"),
    ("多命令代码块后面怎么讲解", "内容块前后的闭环", "concept"),
    ("术语解释用正文还是 Callout", "Callout 克制且尾置", "concept"),
    ("Callout 为什么放在任务末尾", "Callout 尾置的原因", "concept"),
    ("目录树应该展示哪些文件", "目录树与多命令块", "concept"),
    ("故障定位第一步先确认什么", "执行位置判据", "procedure"),
    ("CMake 命令的职责句怎么写", "命令介绍模式", "concept"),
    ("术语「阶段」为什么不能写进正文", "禁用与替换", "concept"),
    ("接口桩为什么不能写进正文", "禁用与替换", "concept"),
    ("C++ 单行注释的写法有什么要求", "单行注释", "concept"),
    ("破损句子改写的判定信号是什么", "判定信号", "concept"),
    # quarto-writing/rendering：include 与链接
    ("include 短代码要不要包在围栏里", "include 短代码必须包在围栏代码块内", "concept"),
    ("仓库内路径链接用相对路径还是 GitHub 绝对链接", "链接使用约定", "concept"),
    ("Mermaid 图表必须用什么围栏", "只使用 {mermaid} 围栏", "concept"),
    ("mermaid 块首的 init 指令起什么作用", "块首固定 init 指令", "concept"),
]

ROWS = TOOLING
