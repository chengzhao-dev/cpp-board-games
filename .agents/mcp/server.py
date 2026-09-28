#!/usr/bin/env python3
"""cpp-board-games 的受限 MCP stdio server。

只使用 Python 标准库。stdout 仅输出 JSON-RPC，诊断信息写入 stderr。
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config.toml"


def config_python() -> str | None:
    try:
        import tomllib
    except ImportError:  # pragma: no cover - Python < 3.11
        return None
    try:
        data = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
        return str(data.get("python") or "").strip() or None
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None


PYTHON = config_python()
MAX_READ_BYTES = 512 * 1024
MAX_OUTPUT_CHARS = 12_000
MAX_CONTEXT_LINES = 3
MIN_PYTHON = (3, 12)
SUPPORTED_PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
DENIED_PARTS = {".git", ".quarto", "_book", "node_modules", ".cache", ".tmp", "temp"}
DENIED_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
DENIED_NAMES = {".env", ".env.local", "id_rsa", "id_ed25519"}
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|access[_-]?token|token|secret|password|passwd|private[_-]?key|authorization)"
    r"(\s*[:=]\s*)([^\s,;]+)"
)
BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
RAW_KEY_RE = re.compile(r"(?<![A-Za-z0-9])(sk-[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9_]{16,})")
TARGET_RE = re.compile(r"^[A-Za-z0-9_-]+/[A-Za-z0-9_-]+$")


class MCPError(Exception):
    """可安全返回给 MCP 客户端的参数或权限错误。"""


def jsonrpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def redact(text: str) -> str:
    """隐藏常见键值凭据，避免 diff、搜索和命令输出回显秘密。"""
    text = BEARER_RE.sub("Bearer [REDACTED]", text)
    text = SECRET_RE.sub(r"\1\2[REDACTED]", text)
    return RAW_KEY_RE.sub("[REDACTED]", text)


def compact(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    text = redact(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[output truncated]"


def redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_value(item) for key, item in value.items()}
    return value


def is_sensitive_name(name: str) -> bool:
    return name in DENIED_NAMES or (name.startswith(".env") and name != ".env.example")


def relative_path(value: str) -> Path:
    """解析并验证仓库相对路径。"""
    if not isinstance(value, str) or not value.strip():
        raise MCPError("path must be a non-empty repository-relative string")
    candidate = Path(value)
    if candidate.is_absolute():
        raise MCPError("absolute paths are not allowed")
    resolved = (ROOT / candidate).resolve()
    try:
        rel = resolved.relative_to(ROOT)
    except ValueError as exc:
        raise MCPError("path escapes the repository root") from exc
    parts = set(rel.parts)
    if parts & DENIED_PARTS or any(part == "build" for part in rel.parts):
        raise MCPError("generated files and private metadata are not accessible")
    if rel.name == "runtime.json" and rel.parent.name == "python":
        raise MCPError("local runtime configuration is not accessible")
    if is_sensitive_name(rel.name):
        raise MCPError("secret files are not accessible")
    if rel.name.startswith(".") and rel.name not in {".gitignore", ".editorconfig"}:
        if rel.name in {".env", ".env.local"}:
            raise MCPError("secret files are not accessible")
    if rel.suffix.lower() in DENIED_SUFFIXES:
        raise MCPError("private key material is not accessible")
    return rel


def safe_path(value: str) -> Path:
    rel = relative_path(value)
    path = ROOT / rel
    if path.exists() and path.is_symlink():
        resolved = path.resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError as exc:
            raise MCPError("symlinks outside the repository are not accessible") from exc
    return path


def read_text(value: str, max_bytes: int = MAX_READ_BYTES) -> str:
    path = safe_path(value)
    if not path.is_file():
        raise MCPError(f"file not found: {value}")
    if path.stat().st_size > max_bytes:
        raise MCPError(f"file exceeds max_bytes ({max_bytes})")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise MCPError("only UTF-8 text files are supported") from exc


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_command(args: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {"exitCode": 127, "output": f"python interpreter not found: {PYTHON}"}
    except PermissionError:
        return {"exitCode": 126, "output": f"python interpreter is not executable: {PYTHON}"}
    except subprocess.TimeoutExpired as exc:
        return {"exitCode": 124, "output": compact((exc.stdout or "") + "\n[timeout]")}
    return {"exitCode": proc.returncode, "output": compact(proc.stdout)}


def run_agent(*args: str, timeout: int = 120) -> dict[str, Any]:
    if not PYTHON:
        return {"exitCode": 127, "output": "config.toml python is missing"}
    return run_command([PYTHON, str(ROOT / ".agents/skills/governing-agents/scripts/run.py"), *args], timeout)


def validate_python() -> None:
    """MCP 使用固定解释器。不可用时在启动阶段直接失败。"""
    if not PYTHON:
        print("config.toml python is missing", file=sys.stderr)
        raise SystemExit(127)
    interpreter = Path(PYTHON)
    if not interpreter.is_file():
        print(f"python interpreter not found: {PYTHON}", file=sys.stderr)
        raise SystemExit(127)
    try:
        result = subprocess.run(
            [PYTHON, "-c", "import sys; print(sys.version)"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        print(f"python interpreter failed: {exc}", file=sys.stderr)
        raise SystemExit(126) from exc
    if result.returncode != 0:
        print(f"python interpreter failed with exit code {result.returncode}: {result.stdout.strip()}", file=sys.stderr)
        raise SystemExit(result.returncode)
    try:
        version = subprocess.run(
            [PYTHON, "-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        major, minor = (int(part) for part in version.stdout.strip().split(".", 1))
    except (OSError, ValueError):
        print("python interpreter version could not be determined", file=sys.stderr)
        raise SystemExit(126)
    if (major, minor) < MIN_PYTHON:
        print(
            f"python interpreter must be >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}; "
            f"got {major}.{minor}",
            file=sys.stderr,
        )
        raise SystemExit(126)


def tool_result(value: Any, is_error: bool = False) -> dict[str, Any]:
    safe_value = redact_value(value)
    text = safe_value if isinstance(safe_value, str) else json.dumps(safe_value, ensure_ascii=False, indent=2)
    return {
        "content": [{"type": "text", "text": text}],
        "isError": is_error,
        "structuredContent": safe_value if isinstance(safe_value, dict) else {"value": safe_value},
    }


TOOLS = [
    {
        "name": "project_review",
        "description": "Execution mode only; never call in Plan Mode. Run the repository preflight checks before a defect-first review.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_status",
        "description": "Return concise git status for the repository.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_diff",
        "description": "Return a bounded git diff, optionally limited to one repository path.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_scope",
        "description": "Resolve the repository's minimal task scope using .agents/skills/governing-agents/scripts/run.py.",
        "inputSchema": {"type": "object", "required": ["target"], "properties": {"target": {"type": "string"}}},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_read",
        "description": "Read one UTF-8 repository file within the safety boundary.",
        "inputSchema": {"type": "object", "required": ["path"], "properties": {"path": {"type": "string"}, "maxBytes": {"type": "integer", "minimum": 1, "maximum": MAX_READ_BYTES}, "startLine": {"type": "integer", "minimum": 1}, "endLine": {"type": "integer", "minimum": 1}}},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_search",
        "description": "Search UTF-8 project files while skipping generated output and caches.",
        "inputSchema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "path": {"type": "string"}, "maxResults": {"type": "integer", "minimum": 1, "maximum": 200}, "contextLines": {"type": "integer", "minimum": 0, "maximum": MAX_CONTEXT_LINES}}},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "knowledge_search",
        "description": "Read-only hybrid knowledge retrieval with source, status, rank, and token budget metadata.",
        "inputSchema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "domain": {"type": "string"}, "topK": {"type": "integer", "minimum": 1, "maximum": 20}, "tokenBudget": {"type": "integer", "minimum": 1, "maximum": 6000}, "explain": {"type": "boolean"}}},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_edit",
        "description": "Execution mode only; never call in Plan Mode. Replace one exact text occurrence after checking the expected SHA-256.",
        "inputSchema": {"type": "object", "required": ["path", "oldText", "newText", "expectedSha256"], "properties": {"path": {"type": "string"}, "oldText": {"type": "string"}, "newText": {"type": "string"}, "expectedSha256": {"type": "string", "pattern": "^[0-9a-fA-F]{64}$"}}},
        "annotations": {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": False},
    },
    {
        "name": "project_check",
        "description": "Execution mode only; never call in Plan Mode. Run the repository's standard check command.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile": {
                    "type": "string",
                    "enum": ["fast", "book", "knowledge", "python", "full"],
                    "default": "full",
                },
                "verbose": {"type": "boolean"},
            },
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_verify",
        "description": "Execution mode only; never call in Plan Mode. Verify qmd content incrementally (verify_content --changed/--paths).",
        "inputSchema": {"type": "object", "properties": {"changedOnly": {"type": "boolean"}, "verbose": {"type": "boolean"}}},
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_render",
        "description": "Execution mode only; never call in Plan Mode. Render the Quarto Book and run its checks.",
        "inputSchema": {"type": "object", "properties": {"verbose": {"type": "boolean"}}},
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "project_build",
        "description": "Execution mode only; never call in Plan Mode. Build one game stage through its build-and-run.sh wrapper.",
        "inputSchema": {"type": "object", "required": ["target"], "properties": {"target": {"type": "string", "pattern": "^[A-Za-z0-9_-]+/[A-Za-z0-9_-]+$"}, "verbose": {"type": "boolean"}}},
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
]


def handle_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "project_status":
        return tool_result(run_command(["git", "status", "--short", "--untracked-files=all"]))
    if name == "project_diff":
        path = args.get("path")
        command = ["git", "diff", "--no-ext-diff", "--"]
        if path:
            command.append(relative_path(path).as_posix())
        result = run_command(command)
        result["output"] = redact(result["output"])
        return tool_result(result)
    if name == "project_scope":
        return tool_result(run_agent("scope", args.get("target", "")))
    if name == "project_read":
        value = read_text(args.get("path", ""), int(args.get("maxBytes", MAX_READ_BYTES)))
        lines = value.splitlines()
        start = int(args.get("startLine", 1))
        end = int(args.get("endLine", len(lines)))
        if start > end:
            raise MCPError("startLine must be <= endLine")
        selected = "\n".join(lines[start - 1:end])
        return tool_result({"path": args["path"], "sha256": sha256_text(value),
                            "startLine": start, "endLine": min(end, len(lines)),
                            "totalLines": len(lines), "text": redact(selected)})
    if name == "project_search":
        query = args.get("query")
        if not isinstance(query, str) or not query:
            raise MCPError("query must be a non-empty string")
        root = safe_path(args.get("path", ".")) if args.get("path") else ROOT
        if root.is_file():
            candidates = [root]
        else:
            candidates = sorted(p for p in root.rglob("*") if p.is_file())
        results = []
        limit = min(int(args.get("maxResults", 50)), 200)
        context = min(int(args.get("contextLines", 0)), MAX_CONTEXT_LINES)
        for path in candidates:
            rel = path.relative_to(ROOT)
            if set(rel.parts) & DENIED_PARTS or "build" in rel.parts:
                continue
            if is_sensitive_name(rel.name) or rel.suffix.lower() in DENIED_SUFFIXES:
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".woff", ".woff2", ".ico", ".o", ".obj"}:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(lines, 1):
                if query.casefold() in line.casefold():
                    before = lines[max(0, number - 1 - context):number - 1]
                    after = lines[number:min(len(lines), number + context)]
                    results.append({"path": rel.as_posix(), "line": number,
                                    "text": redact(line[:500]), "before": [redact(x[:500]) for x in before],
                                    "after": [redact(x[:500]) for x in after]})
                    if len(results) >= limit:
                        return tool_result({"query": query, "results": results, "truncated": True})
        return tool_result({"query": query, "results": results, "truncated": False})
    if name == "knowledge_search":
        query = args.get("query")
        if not isinstance(query, str) or not query.strip():
            raise MCPError("query must be a non-empty string")
        top_k = min(int(args.get("topK", 5)), 20)
        budget = min(int(args.get("tokenBudget", 4000)), 6000)
        command = [PYTHON, str(ROOT / ".agents/skills/maintaining-python/scripts/unified_retrieval.py"),
                   query, "--top-k", str(top_k), "--budget", str(budget)]
        if args.get("domain"):
            command.extend(["--domain", str(args["domain"])])
        if args.get("explain"):
            command.append("--explain")
        result = run_command(command)
        if result["exitCode"] != 0:
            raise MCPError(result["output"])
        try:
            return tool_result(json.loads(result["output"]))
        except json.JSONDecodeError as exc:
            raise MCPError("knowledge retrieval returned invalid JSON") from exc
    if name == "project_edit":
        path = safe_path(args.get("path", ""))
        current = read_text(args["path"])
        expected = args.get("expectedSha256", "").lower()
        if sha256_text(current) != expected:
            raise MCPError("expectedSha256 does not match the current file")
        old = args.get("oldText")
        new = args.get("newText")
        if not isinstance(old, str) or not isinstance(new, str) or not old:
            raise MCPError("oldText must be a non-empty string")
        if current.count(old) != 1:
            raise MCPError("oldText must occur exactly once")
        updated = current.replace(old, new, 1)
        path.write_text(updated, encoding="utf-8", newline="\n")
        return tool_result({"path": args["path"], "sha256": sha256_text(updated), "changed": True})
    if name == "project_review":
        check_res = run_agent("check", "--profile", "full")
        verify_res = run_agent("verify", "--changed")
        output = f"Review Summary:\n- Check Suite: exit {check_res['exitCode']}\n{check_res['output']}\n- C++ Verify: exit {verify_res['exitCode']}\n{verify_res['output']}"
        return tool_result(output)
    if name in {"project_check", "project_verify", "project_render", "project_build"}:
        verbose = bool(args.get("verbose", False))
        if name == "project_check":
            profile = args.get("profile", "full")
            if profile not in {"fast", "book", "knowledge", "python", "full"}:
                raise MCPError("profile must be one of: fast, book, knowledge, python, full")
            command = ["check", "--profile", profile]
        elif name == "project_verify":
            command = ["verify"] + (["--changed"] if args.get("changedOnly", True) else [])
        elif name == "project_render":
            command = ["render"]
        else:
            target = args.get("target", "")
            if not TARGET_RE.fullmatch(target):
                raise MCPError("target must look like game/stage")
            command = ["build", target]
        if verbose:
            command.append("--verbose")
        timeout = 900 if name in {"project_render", "project_build", "project_verify"} else 300
        return tool_result(run_agent(*command, timeout=timeout))
    raise MCPError(f"unknown tool: {name}")


def resource_text(uri: str) -> str:
    if uri == "project://structure":
        paths = []
        for path in sorted(ROOT.iterdir()):
            if path.name in DENIED_PARTS:
                continue
            paths.append(path.name + ("/" if path.is_dir() else ""))
        return "\n".join(paths) + "\n"
    if uri == "project://skills":
        return read_text(".agents/skills/governing-agents/references/catalog.md")
    if uri == "project://agent":
        return read_text(".agents/mcp/README.md")
    raise MCPError(f"unknown resource: {uri}")


def dispatch(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}
    if request_id is None and method.startswith("notifications/"):
        return None
    if method == "initialize":
        requested = params.get("protocolVersion")
        version = requested if requested in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
        return {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}, "resources": {"subscribe": False, "listChanged": False}}, "serverInfo": {"name": "cpp-board-games", "version": "0.1.0"}}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "resources/list":
        resources = [{"uri": uri, "name": name, "mimeType": "text/plain"} for uri, name in (("project://structure", "Project structure"), ("project://skills", "Agent skill catalog"), ("project://agent", "Agent configuration") )]
        return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": resources}}
    if method == "resources/read":
        uri = params.get("uri", "")
        try:
            text = resource_text(uri)
        except MCPError as exc:
            return jsonrpc_error(request_id, -32602, str(exc))
        return {"jsonrpc": "2.0", "id": request_id, "result": {"contents": [{"uri": uri, "mimeType": "text/plain", "text": text}]}}
    if method == "tools/call":
        try:
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": handle_tool(params.get("name", ""), params.get("arguments") or {})}
        except MCPError as exc:
            return {"jsonrpc": "2.0", "id": request_id, "result": tool_result(str(exc), True)}
        except Exception as exc:  # pragma: no cover - 防止单次工具错误杀死 stdio server
            print(f"tool error: {exc}", file=sys.stderr)
            return {"jsonrpc": "2.0", "id": request_id, "result": tool_result("internal server error", True)}
    return jsonrpc_error(request_id, -32601, f"method not found: {method}")


def main() -> int:
    # MCP stdio is always UTF-8.  Without this on Windows, a redirected
    # stdout stream may use the active code page and corrupt Chinese content.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    validate_python()
    for raw in sys.stdin:
        if not raw.strip():
            continue
        try:
            message = json.loads(raw)
            response = dispatch(message)
        except json.JSONDecodeError:
            response = jsonrpc_error(None, -32700, "invalid JSON")
        except Exception as exc:  # pragma: no cover
            print(f"protocol error: {exc}", file=sys.stderr)
            response = jsonrpc_error(None, -32603, "internal error")
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
