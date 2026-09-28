# cpp-board-games MCP Server

实现依据：[MCP Specification](https://modelcontextprotocol.io/specification/latest)；本服务采用 stdio transport，并只暴露项目白名单能力。

这是一个项目级 MCP（Model Context Protocol）stdio server。它把仓库已有的作用域、校验和构建入口包装成结构化工具，避免 Agent 直接执行任意 shell 命令。

## 启动

skills 和知识库中的命令由统一入口执行。MCP 宿主配置使用根目录 `config.toml` 的 `python`，不通过 PATH 或其他运行时配置查找。

在仓库根目录执行：

```powershell
<config.toml 中 python 的绝对路径> .agents/mcp/server.py
```

服务通过 stdin 接收 JSON-RPC 2.0 消息，通过 stdout 返回 JSON-RPC 2.0 消息。MCP 客户端通常会自动完成下面的初始化流程。服务本身不会自动注册到宿主：

1. 发送 `initialize`。
2. 发送 `notifications/initialized`。
3. 调用 `tools/list` 或 `resources/list`。
4. 通过 `tools/call` 调用工具，或通过 `resources/read` 读取资源。

## 工具

`project_review` 是标准检查组合入口，会运行仓库检查和改动文档校验。它不替代宿主侧的人工缺陷审查。工具名称、参数和副作用以 `tools/list` 返回的 schema 为准。

所有可能写入、构建或渲染的工具描述都带有“仅执行阶段调用”约束，并通过 `annotations` 标记只读与破坏性属性。Plan Mode 只能调用只读工具，不能把这些工具的返回结果当成执行批准。

| 工具 | 用途 | 是否写入 |
|---|---|---|
| `project_status` | 获取精简 Git 状态 | 否 |
| `project_diff` | 查看指定文件或工作区 diff | 否 |
| `project_scope` | 调用现有作用域解析器（game/stage） | 否 |
| `project_read` | 读取仓库内文本文件 | 否 |
| `project_search` | 在允许的源码、文档和配置中检索 | 否 |
| `knowledge_search` | 调用知识库混合检索并返回来源、排名和 Token 预算 | 否 |
| `project_edit` | 对单个文件执行精确文本替换 | 是 |
| `project_check` | 运行 `run.py check --profile <fast|book|knowledge|python|full>` | 可能生成检查缓存 |
| `project_verify` | 增量校验 qmd 文档内容（verify_content） | 可能生成检查缓存 |
| `project_render` | 渲染 Quarto Book 并校验 | 是，生成 `_book/` |
| `project_build` | 在 WSL 构建指定游戏阶段（build-and-run.sh） | 是，生成 `build/` |
| `project_review` | 运行仓库预检与改动文档校验，供后续缺陷审查使用 | 可能生成检查缓存 |

`project_read` 支持可选的 `startLine`/`endLine`，默认仍受最大字节数限制。`project_search` 支持 `maxResults` 和 `contextLines`，结果带有 `truncated` 标记。先用 `project_scope`，再按范围读取，避免整包进入上下文。

`project_edit` 必须提供 `expectedSha256`，并且 `oldText` 只能精确匹配一次。文件在 Agent 读取后被其他进程修改时，编辑会拒绝执行。MCP 不提供任意 shell、文件删除、`git commit` 或 `git push` 工具。

## 资源

- `project://structure`：当前允许访问的项目结构。
- `project://skills`：`.agents/skills/governing-agents/references/catalog.md`。
- `project://agent`：`.agents/mcp/README.md` 和能力边界。

## 安全边界

- 所有路径必须位于仓库根目录内，拒绝路径穿越和越界符号链接。
- 工具描述和注解不能替代宿主的用户授权。`project_edit`、`project_check`、`project_verify`、`project_render`、`project_build` 和 `project_review` 只应在用户明确批准后调用，Plan Mode 不得调用。
- 永不读取或写入 `.git/`、`_book/`、`.quarto/`、`games/**/build/`、依赖缓存和密钥文件。
- `project_search` 自动跳过构建产物、缓存和二进制文件，并跳过 `.env`、私钥等敏感文件；输出对常见凭据键值脱敏。
- 校验、构建和渲染只能调用仓库现有的白名单命令。
- 输出默认截断，避免把完整构建日志或渲染产物带入上下文。

## 宿主配置

任何支持 stdio MCP 的宿主都可以使用以下配置：

```json
{
  "mcpServers": {
    "cpp-board-games": {
      "command": "<config.toml 中 python 的绝对路径>",
      "args": [".agents/mcp/server.py"]
    }
  }
}
```

如果该解释器不存在或启动失败，MCP 直接向 stderr 输出错误并退出。不回退到 PATH，也不尝试其他解释器。
