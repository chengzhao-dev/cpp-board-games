#!/usr/bin/env python3
"""Agent 编码、MCP 范围读取、作用域解析和安全输出的最小回归测试。"""

from pathlib import Path
import importlib.util
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
sys.dont_write_bytecode = True


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


encoding = load(ROOT / ".agents/skills/governing-agents/scripts/check_encoding.py", "check_encoding")
mcp = load(ROOT / ".agents/mcp/server.py", "mcp_server")
runner = load(ROOT / ".agents/skills/governing-agents/scripts/run.py", "run_agent")
scope = load(ROOT / ".agents/skills/governing-agents/scripts/scope.py", "scope")
size = load(ROOT / ".agents/skills/governing-agents/scripts/check_skill_size.py", "check_skill_size")


def main() -> int:
    assert encoding.control_issues("auto\x07") == [(1, 5, "U+0007")]
    assert encoding.control_issues("中文\n\ttext") == []
    assert encoding.severity(Path(".agents/skills/governing-agents/scripts/x.py")) == "hard"
    assert encoding.severity(Path("content/tictactoe/02-project-layout.qmd")) == "soft"

    # 体量脚本：L1 front matter 字段可解析
    fields = size.front_fields(ROOT / ".agents/skills/writing-quarto/SKILL.md")
    assert fields.get("name") == "writing-quarto"

    assert mcp.redact("API_KEY=secret-value") == "API_KEY=[REDACTED]"
    assert "abc.def-123" not in mcp.redact("Authorization: Bearer abc.def-123")
    assert mcp.redact("sk-1234567890abcdef") == "[REDACTED]"
    result = mcp.tool_result({"text": "token: secret-value"})
    assert "secret-value" not in result["content"][0]["text"]
    try:
        mcp.relative_path(".env")
    except mcp.MCPError:
        pass
    else:
        raise AssertionError(".env must be denied")

    read = mcp.handle_tool("project_read", {"path": "AGENTS.md", "startLine": 1, "endLine": 2})
    assert read["structuredContent"]["startLine"] == 1
    assert read["structuredContent"]["totalLines"] >= 2
    search = mcp.handle_tool("project_search", {
        "query": "build-and-run", "path": "AGENTS.md",
        "maxResults": 1, "contextLines": 1,
    })
    item = search["structuredContent"]["results"][0]
    assert item["line"] > 0 and isinstance(item["before"], list)
    knowledge_tool = next(tool for tool in mcp.TOOLS if tool["name"] == "knowledge_search")
    assert knowledge_tool["annotations"]["readOnlyHint"] is True
    assert knowledge_tool["inputSchema"]["properties"]["topK"]["maximum"] == 20
    review = next(tool for tool in mcp.TOOLS if tool["name"] == "project_review")
    assert review["inputSchema"]["properties"] == {}
    assert runner.status_group(".agents/skills/governing-agents/references/catalog.md") == "maintenance"
    assert runner.status_group("content/tictactoe/03-board.qmd") == "content"
    assert runner.display_command("kb-index") == "知识库索引"
    assert runner.display_check("kb-eval") == "知识库评测"
    fast = [name for name, *_rest in runner.checks_for_profile("fast")]
    full = [name for name, *_rest in runner.checks_for_profile("full")]
    assert len(fast) < len(full)
    assert {"kb", "kb-eval"} <= set(full)
    assert "content" in fast and "dom" not in fast

    # 作用域：阶段解析、路径反查与仓库域
    unit = scope.find_stage("tictactoe/03-board", ROOT)
    assert unit and unit["row"]["status"] == "done"
    assert unit["row"]["qmd"] == "content/tictactoe/03-board.qmd"
    by_qmd = scope.find_stage_by_qmd(ROOT / "content/tictactoe/02-project-layout.qmd", ROOT)
    assert by_qmd and by_qmd["stage"] == "02-project-layout"
    by_code = scope.find_stage_by_code_path(
        ROOT / "games/tictactoe/01-cli-game", ROOT
    )
    assert by_code and by_code["stage"] == "01-rules"
    assert scope.resolve_repo_domain(
        ".agents/skills/shipping-github/SKILL.md", ROOT
    )["label"] == "skill shipping-github"
    skill_reads = scope.resolve_repo_domain(
        ".agents/skills/cpp-development/SKILL.md", ROOT
    )["reads"]
    assert skill_reads == [".agents/skills/cpp-development/SKILL.md"]
    maintenance_reads = scope.resolve_repo_domain(
        ".agents/skills/governing-agents/references/refactor-guidelines.md", ROOT
    )["reads"]
    assert ".agents/skills/governing-agents/references/catalog.md" in maintenance_reads
    assert scope.resolve_repo_domain(
        ".agents/knowledge/KNOWLEDGE.md", ROOT
    )["label"] == "knowledge"
    table_rows = scope.parse_table(
        ROOT / ".agents/skills/cpp-development/references/stages/tictactoe.md"
    )
    assert "01-rules" in table_rows and "05-terminal-play" in table_rows

    # 项目级硬约束留在 AGENTS.md
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "Plan Mode" in agents_text
    assert "提交与推送默认不做" in agents_text
    assert "chengzhao-dev" in agents_text
    assert (ROOT / ".agents/skills/shipping-github/references/git-workflow.md").is_file()
    assert (ROOT / ".agents/skills/cpp-development/references/stages/tictactoe.md").is_file()
    assert (ROOT / ".agents/knowledge/agent-workspace/navigation/staged-game-layout.md").is_file()

    allowed_root = {
        ".agents", ".github", "content", "games", "shared", "_freeze",
        ".gitattributes", ".gitignore", "AGENTS.md", "config.toml",
        "index.qmd", "LICENSE", "README.md", "_quarto.yml",
    }
    unexpected_root = []
    for path in ROOT.iterdir():
        if path.name in allowed_root or path.name == ".git":
            continue
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", "--", path.name],
            cwd=ROOT,
            check=False,
        ).returncode == 0
        if not ignored:
            unexpected_root.append(path.name)
    assert unexpected_root == [], unexpected_root

    tools = {tool["name"]: tool for tool in mcp.TOOLS}
    execution_only = {
        "project_review",
        "project_edit",
        "project_check",
        "project_verify",
        "project_render",
        "project_build",
    }
    for name in execution_only:
        assert "Plan Mode" in tools[name]["description"]
        annotations = tools[name]["annotations"]
        assert annotations["readOnlyHint"] is False
        assert annotations["openWorldHint"] is False
    for name in {"project_status", "project_diff", "project_scope", "project_read", "project_search"}:
        assert tools[name]["annotations"]["readOnlyHint"] is True
    profile_schema = tools["project_check"]["inputSchema"]["properties"]["profile"]
    assert profile_schema["default"] == "full"
    assert "fast" in profile_schema["enum"]
    print("通过  Agent 控制检查")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
