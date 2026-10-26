# Agent 工作区

`.agents/` 保存本项目的 Agent 资源。根 `AGENTS.md` 只写项目级硬约束；本文件负责定位，不重复规则。通用 C++、Quarto 与 GitHub 流程由插件技能提供，本仓只留项目事实与检查配置。

## 按任务进入

| 任务 | 入口 |
| --- | --- |
| C++、CMake、WSL 游戏阶段开发 | 插件 `developing-cpp`、`building-cpp`；工程事实 `skills/cpp-workflow-project/SKILL.md` |
| 棋盘游戏抽象和规则设计 | 插件 `developing-cpp` 的 project-design 参考 |
| 编写 Quarto 文档和章节 | 插件 `writing-quarto`；本书事实 `skills/quarto-book-project/SKILL.md` |
| 调整主题、布局和页面资源 | 插件 `designing-theme`；主题副本在根 `theme/` |
| 提交、推送与发布 | 插件 `shipping-github` |
| 查看读取边界 | `scripts/scope.py` |
| 校验全部章节正文 | `scripts/checking-book.py` |
| 构建某个游戏工程 | `scripts/building-wsl.py <game>` |
| 检查已安装插件是否可用 | `scripts/checking-plugins.py` |

## 目录职责

```text
.agents/
├── scripts/                        #/ 仓库脚本
├── skills/cpp-workflow-project/    #/ 工程事实与阶段表
├── skills/quarto-book-project/     #/ 章节规则
└── README.md                        # 本目录导航
```

## 运行入口

四个脚本都从自身路径解析仓库根，不依赖当前工作目录。`scope.py` 输出读取边界；`checking-book.py` 调用已安装插件的正文检查器；`building-wsl.py` 在 WSL（Windows）或本机 bash（CI）里运行 `games/<game>/running-build.sh`；`checking-plugins.py` 检查两个已安装插件的入口、技能文件与语法。解释器以 `config/config.toml` 为准，这里不复制子命令。

游戏代码按游戏工程目录组织在 `games/<game>/` 下；配置归属与格式模板的判断依据在插件 `building-cpp` 的 `references/cmake.md`，阶段表见本仓 `skills/cpp-workflow-project/stages/stage-table.md`。
