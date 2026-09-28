#!/usr/bin/env python3
"""cpp-notes 检索适配器：把现有知识库结果转换为统一协议。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kb  # noqa: E402
from retriever import retrieve  # noqa: E402


def adapt(query: str, *, repository: str = "cpp-notes", kind: str = "knowledge",
          domain: str = "", scope: str = "", status: str = "active",
          top_k: int = 5, token_budget: int | None = None,
          explain: bool = False) -> dict:
    result = retrieve(query, domain=domain, budget=token_budget, explain=explain)
    rows = result.get("ranked", [])[:max(1, top_k)]
    registry = kb.read_json(kb.REGISTRY_PATH, {"chunks": {}, "documents": {}})
    chunks = registry.get("chunks", {})
    documents = registry.get("documents", {})
    items = []
    for rank, row in enumerate(rows, 1):
        chunk = chunks.get(row["chunk_id"], {})
        doc = documents.get(chunk.get("doc_id", ""), {})
        items.append({
            "repository": repository,
            "id": chunk.get("chunk_id", row["chunk_id"]),
            "kind": kind,
            "path": doc.get("path", ""),
            "title": doc.get("title", ""),
            "heading_path": row.get("heading_path", chunk.get("heading_path", "")),
            "score": row.get("score", 0),
            "match_type": (["bm25"] if row.get("bm25_rank") else []) + (["graph"] if row.get("graph_hit") else []),
            "content": (chunk.get("content") if explain else None),
            "source": {"path": doc.get("path", ""), "heading": row.get("heading_path", "")},
            "updated": doc.get("updated", ""),
            "status": chunk.get("status", status),
            "rank": rank,
        })
    return {"request": {"repository": repository, "query": query, "kind": kind,
                         "domain": domain, "scope": scope, "status": status,
                         "top_k": top_k, "token_budget": token_budget, "explain": explain},
            "results": items, "elapsed_ms": result.get("elapsed_ms", 0),
            "budget": result.get("budget", {}), "mode": result.get("mode", "chunks")}


def main() -> int:
    parser = argparse.ArgumentParser(description="统一检索响应适配器")
    parser.add_argument("query")
    parser.add_argument("--domain", default="")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--explain", action="store_true")
    args = parser.parse_args()
    print(json.dumps(adapt(args.query, domain=args.domain, top_k=args.top_k,
                           token_budget=args.budget, explain=args.explain),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
