#!/usr/bin/env python3
"""在同一 cpp-notes knowledge 语料上比较 registry 定位与 FTS 检索。

默认只输出 JSON，不写报告；如需保存报告显式传 --output，文件必须位于 temp/ 下。
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import kb_common as kb  # noqa: E402
from unified_retrieval import adapt  # noqa: E402

CASES = [
    ("链接阶段为什么需要目标文件", "writing-cpp", "目标文件"),
    ("为什么统一使用列表初始化", "writing-cpp", "列表初始化"),
    ("Quarto HTML 选项在哪些作用域生效", "writing-quarto", "作用域"),
    ("项目级 MCP 的安全边界", "governing-agents", "MCP"),
    ("知识库增长后怎样避免按文档扫描全部 Chunk", "writing-cpp", "知识分块"),
]


def estimate(text: str) -> int:
    return kb.estimate_tokens(text)


def registry_rows() -> list[dict]:
    registry = kb.read_json(kb.REGISTRY_PATH, {"documents": {}})
    rows = []
    for doc in registry.get("documents", {}).values():
        path = ROOT / doc.get("path", "")
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        rows.append({"path": doc.get("path", ""), "title": doc.get("title", ""), "text": text})
    return rows


def registry_search(query: str, domain: str, top_k: int) -> list[dict]:
    # 条目级路由基线：以标题和 frontmatter 元数据构造紧凑视图，
    # 不读取正文，不把条目命中伪装成段落级语义召回。
    terms = [part.casefold() for part in query.split() if len(part) > 1]
    scored = []
    for row in registry_rows():
        front = row["text"].split("---", 2)[1] if row["text"].startswith("---") else ""
        haystack = (row["title"] + " " + front).casefold()
        if domain and f"domain: {domain}" not in haystack:
            continue
        score = sum(haystack.count(term) for term in terms)
        if score:
            scored.append((score, row))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["path"]))
    return [row for _, row in scored[:top_k]]


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * p) - 1))
    return ordered[index]


def run(top_k: int) -> dict:
    rows = []
    for query, domain, expected in CASES:
        started = time.perf_counter()
        registry = registry_search(query, domain, top_k)
        registry_ms = (time.perf_counter() - started) * 1000
        started = time.perf_counter()
        hybrid = adapt(query, domain=domain, top_k=top_k, explain=False)
        hybrid_ms = (time.perf_counter() - started) * 1000
        registry_hit = any(expected.casefold() in row["title"].casefold() for row in registry)
        hybrid_hit = any(expected.casefold() in (row.get("heading_path", "") + row.get("path", "")).casefold()
                         for row in hybrid["results"])
        rows.append({"query": query, "domain": domain, "expected": expected,
                     "registry_hit": registry_hit, "hybrid_hit": hybrid_hit,
                     "registry_ms": round(registry_ms, 3), "hybrid_ms": round(hybrid_ms, 3),
                     "registry_tokens": sum(estimate(row["title"]) for row in registry),
                     "hybrid_tokens": hybrid.get("budget", {}).get("used", 0)})
    return {
        "corpus": {"repository": "cpp-notes", "root": ".agents/knowledge", "cases": len(CASES)},
        "control_variables": {"top_k": top_k, "token_estimator": "kb_common.estimate_tokens", "cache": "retriever default"},
        "metrics": {
            "registry_recall_at_k": sum(row["registry_hit"] for row in rows) / len(rows),
            "hybrid_recall_at_k": sum(row["hybrid_hit"] for row in rows) / len(rows),
            "registry_p50_ms": statistics.median(row["registry_ms"] for row in rows),
            "registry_p95_ms": percentile([row["registry_ms"] for row in rows], .95),
            "hybrid_p50_ms": statistics.median(row["hybrid_ms"] for row in rows),
            "hybrid_p95_ms": percentile([row["hybrid_ms"] for row in rows], .95),
            "registry_mean_tokens": statistics.mean(row["registry_tokens"] for row in rows),
            "hybrid_mean_tokens": statistics.mean(row["hybrid_tokens"] for row in rows),
        },
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="同语料检索公平 benchmark")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", default="", help="可选，只允许写入 temp/ 下")
    args = parser.parse_args()
    report = json.dumps(run(max(1, args.top_k)), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = (ROOT / args.output).resolve()
        if ROOT / "temp" not in target.parents:
            raise SystemExit("output must be under temp/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
