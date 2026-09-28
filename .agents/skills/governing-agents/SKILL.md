---
name: governing-agents
description: 维护项目 Agent 规则、读取边界、工作区结构和验收流程；重构 .agents 或调整治理规则时使用
metadata:
  short-description: 维护 Agent 规则与工作区结构
---

# Skill: governing-agents

统一承载 Agent 治理规则、`.agents/` 结构与验收边界。只回答「怎么组织与维护」，领域结论交给 `.agents/knowledge/`。

## 适用场景

- 新建、合并、重构、改名或删除 skill、reference 与技能内资源。
- 调整 `.agents/` 四区结构、命名或规则出处。
- **不适用**：写章节正文（转 `writing-quarto`）、C++ 实现与构建（转 `cpp-development`）、改样式（转 `designing-theme`）、游戏规则设计（转 `game-design`）。

## 任务路由

| 任务 | 读取 |
| --- | --- |
| 四区职责、目标结构、叶子目录规则、两仓对照 | `references/structure.md` |
| 命名、kb_id 方案、frontmatter 元数据规则 | `references/naming.md` |
| 统一脚本入口用法与校验 profile | `scripts/run.py`（文件头说明） |
| 注释写法的完整依据 | `.agents/knowledge/cpp-teaching/style/comment-style.md` |

## P0 硬约束

1. 根目录 `AGENTS.md` 是项目级唯一硬约束入口；每条规则只有一个权威出处，其他文档通过链接引用。
2. 规划、解释、搜索和评审默认只读；用户明确要求实现、修复或重构时才进入写入流程。
3. 重构可以修改已有文件，但不自动授权新增代码文件；新增、删除和大范围迁移必须先列出路径、原因、影响和验证方式。
4. 删除或覆盖前先读取目标，确认没有超出用户描述的内容；计划阶段只读，执行阶段按改动域验证。
5. 面向用户的项目设计、路线、环境、验收和开发记录统一写入 `content/**/*.qmd`，不再新建根级 `docs/*.md`；`.agents/knowledge/` 只服务 Agent 内部判断。
6. 默认不提交、不推送、不修改远端；不修改 `_book/`、`.quarto/`、`build/` 等生成物和缓存作为源文件。
7. 目录结构随真实需求增长，不预先创建大量空模块。
8. VS Code 专用配置（`extensions.json`、`settings.json`）使用 JSONC 注释；程序读取的普通 JSON（fixture、协议、交换数据）保持严格 JSON，禁止注释；修改 `extensions.json` 推荐项时核对与 `settings.json` 指定的 formatter 一致。
9. 游戏的 `.vscode/`、脚本、构建和测试入口以 `games/<game>/` 为边界，直接使用游戏本地配置，不依赖仓库根脚手架；仓库根不保留 `.clang-format`，格式模板在 `skills/cpp-development/assets/config/`，注释与终端输出规范见 `.agents/knowledge/cpp-teaching/style/`。
10. 正式代码与配置只进既定位置（`games/<game>/`、`shared/`、`content/` 与根部既定入口文件）；一次性脚本、草稿和中间产物一律生成到 `temp/`，不提交；不在根目录或其他位置随意生成工程文件，根目录不放 CMake 文件。

## 完成判据

- [ ] 改动域内每条规则都能指向唯一出处。
- [ ] 结构与命名符合 `references/structure.md` 与 `naming.md`。
- [ ] 按改动范围完成对应验证（CTest、`quarto render` 或文档检查）。
