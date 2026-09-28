#!/usr/bin/env python3
"""冲突检测回归：锁住 §3.6「图谱实体重合度 → 检索降权」这条曾经静默失效的链路。

为什么需要这份断言：旧实现按 chunk_id 取交集，而 chunk_id 以 doc_id 为前缀，
跨文档交集恒空 → overlap 恒 0 → 检索侧降权从未生效，且没有任何报错。
这里用内存 SQLite 和合成注册表跑，不依赖 index_data/，也不写任何产物。

用法：python .agents/skills/maintaining-python/scripts/test_conflict_detection.py
退出码：0 = 断言全过，非 0 = 链路又断了（AssertionError 直接给现场）。
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import indexer  # noqa: E402
import retriever  # noqa: E402


def make_doc(doc_id, updated, tags, supersedes=""):
    return {
        "doc_id": doc_id, "updated": updated, "tags": tags,
        "supersedes": supersedes, "domain": "tooling", "subdomain": "x", "levels": [0],
    }


def chunk(cid, doc_id, content):
    return {"chunk_id": cid, "doc_id": doc_id, "content": content, "kind": "child"}


OLD = make_doc("doc-old", "2026-01-01", ["ownership", "smart_pointer"])
NEW = make_doc("doc-new", "2026-09-01", ["ownership", "smart_pointer", "borrowing"])
REG = {
    "documents": {"doc-old": OLD, "doc-new": NEW},
    "chunks": {
        "doc-old__P__a": chunk("doc-old__P__a", "doc-old",
                                "见 `unique_ptr` 与 .agents/skills/x/references/y.md 说明"),
        "doc-new__P__b": chunk("doc-new__P__b", "doc-new",
                               "见 `unique_ptr` 与 GitHub Pages 部署"),
    },
}
con = sqlite3.connect(":memory:")
indexer.connect(con)
n = indexer.detect_conflicts(con, REG)
rows = list(con.execute("SELECT older_doc, newer_doc, overlap, shared FROM conflict"))
assert n == 1, "expected exactly one conflict candidate"
older, newer, overlap, shared = rows[0]
assert (older, newer) == ("doc-old", "doc-new")
assert overlap > 0, "overlap must not be the old always-zero value"
assert "ownership" in shared and "smart_pointer" in shared
assert "references" not in shared and "github" not in shared, "path/prose noise must not count"

# 检索侧：conflict 必须真的产生 <1 的降权，且只作用于较旧的一方
factors = retriever.stale_factors(con, REG)
assert factors.get("doc-old", 1.0) < 1.0, "conflict penalty never applied"
assert factors.get("doc-new") is None
expect = 1.0 - min(indexer.CONFLICT_MAX_PENALTY, overlap)
assert abs(factors["doc-old"] - expect) < 1e-9, (factors["doc-old"], expect)

# 排除项 1：已被 supersedes 关联的版本演进不重复报冲突
SV = {"documents": {"doc-old": dict(OLD),
                    "doc-new": dict(NEW, supersedes="doc-old")},
      "chunks": REG["chunks"]}
con2 = sqlite3.connect(":memory:")
indexer.connect(con2)
assert indexer.detect_conflicts(con2, SV) == 0, "supersedes pair must not be a conflict"
sup_factors = retriever.stale_factors(con2, SV)
assert sup_factors.get("doc-old") == retriever.SUPERSEDED_FACTOR

# 排除项 2：没有共享概念就不报
NB = {"documents": {"doc-old": dict(OLD, tags=["ownership"]),
                    "doc-new": dict(NEW, tags=["cache"])},
      "chunks": {}}
con3 = sqlite3.connect(":memory:")
indexer.connect(con3)
assert indexer.detect_conflicts(con3, NB) == 0
print("PASS  冲突检测回归  重合度与降权生效，supersedes/日期平手均不误报")
