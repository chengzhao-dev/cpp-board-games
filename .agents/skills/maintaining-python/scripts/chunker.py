#!/usr/bin/env python3
"""语义分块器：把 .agents/knowledge/ 下的 Markdown 切成 Parent / Child 两层 Chunk。

边界规则（对齐知识库规范）：## 是 Parent 边界，### 是 Child 边界，#### 及更深的
标题并入所属 Child 不再单独成块，否则父子映射会出现三层歧义。首个 ## 之前的概述
单独成一个 Parent，否则文档开头会被静默丢掉。

每个 Child 在正文前注入标题路径前缀（形如 [文档标题 > 阶段 > Level 5：智能指针]），
让脱离上下文的小块仍能独立成句——这是「小块精准召回、大块返回给 LLM」成立的前提。
Parent 不注入前缀，因为它本身就带标题。只有标题没有正文的段落不产出 Child：这种空壳
块会占住 BM25 与向量的候选位，把真正能回答问题的 Child 挤出 Top-5。

内容未变的文件直接复用上一次的分块结果，所以本步骤的开销随「改了多少」增长，
而不是随「库有多大」增长。

用法：
    python .agents/skills/maintaining-python/scripts/chunker.py               # 增量：只重切变更文件
    python .agents/skills/maintaining-python/scripts/chunker.py --all         # 忽略哈希，强制全量重切
    python .agents/skills/maintaining-python/scripts/chunker.py --verbose      # 逐篇打印 Parent/Child 数量
    python .agents/skills/maintaining-python/scripts/chunker.py --show         # 打印每篇的 Child 标题路径与令牌数
退出码：0 = 成功，1 = 有文件不符合规范（缺字段、无 ## 段落）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kb  # noqa: E402

STRATEGY = "semantic_heading"


def slug(heading: str) -> str:
    """标题转稳定 id 片段：ASCII 可读前缀 + 短哈希，避免中文 id 与同名冲突。"""
    ascii_part = "".join(ch if ch.isalnum() and ord(ch) < 128 else "-" for ch in heading)
    ascii_part = "-".join(part for part in ascii_part.split("-") if part)[:28] or "sec"
    return ascii_part + "-" + kb.content_hash(heading)[-8:]


def has_body(block: str) -> bool:
    """块里除了标题和空行是否还有内容。用于丢掉「只有标题没有正文」的空壳 Chunk。"""
    for line in block.split(kb.NL):
        if line.strip() and not line.lstrip().startswith("#"):
            return True
    return False


def child_record(doc_id: str, parent_id: str, chain: str, block: str, heading: str) -> dict:
    """构造一个 Child：标题路径前缀注入到正文开头，段首无子标题时沿用 Parent 的标题。"""
    path = chain + " > " + heading if heading else chain
    chunk_id = parent_id + "__C__" + (slug(heading) if heading else "self")
    return {
        "chunk_id": chunk_id,
        "parent_id": parent_id,
        "doc_id": doc_id,
        "kind": "child",
        "heading_path": path,
        "content": "[" + path + "] " + block.strip(),
    }


def split_doc(path: Path) -> tuple[dict, list[dict]]:
    """切分单篇文档，返回 (文档记录, Chunk 列表)。不符合规范时抛 ValueError。"""
    text = path.read_text(encoding="utf-8")
    meta, body = kb.frontmatter(text)
    missing = [name for name in kb.REQUIRED_FIELDS if not meta.get(name)]
    if missing:
        raise ValueError("Frontmatter 缺字段：" + ", ".join(missing))
    h2 = [row for row in kb.headings(body) if row[1] == 2]
    if not h2:
        raise ValueError("没有 ## 段落，无法建立 Parent/Child 两层结构")

    doc_id = str(meta["kb_id"])
    title = str(meta["title"])
    lines = body.split(kb.NL)
    total = len(lines)
    chunks: list[dict] = []

    # 段落起点：首个 ## 之前的概述，加上每个 ## 到下一个 ## 之前的区间。
    ranges: list[tuple[str, int, int]] = []
    if h2[0][0] > 2:
        ranges.append(("引言", 1, h2[0][0] - 1))
    for index, (number, _level, heading) in enumerate(h2):
        stop = h2[index + 1][0] - 1 if index + 1 < len(h2) else total
        ranges.append((heading, number, stop))

    for heading, start, stop in ranges:
        block = kb.NL.join(lines[start - 1:stop]).strip()
        parent_id = doc_id + "__P__" + slug(heading)
        chain = title + " > " + heading
        subs = [row for row in kb.headings(body) if row[1] == 3 and start < row[0] <= stop]
        local: list[dict] = []
        if not subs:
            if has_body(block):
                local.append(child_record(doc_id, parent_id, chain, block, ""))
        else:
            leading = kb.NL.join(lines[start - 1:subs[0][0] - 1])
            if has_body(leading):
                local.append(child_record(doc_id, parent_id, chain, leading, ""))
            for index, (number, _lvl, sub) in enumerate(subs):
                sub_stop = subs[index + 1][0] - 1 if index + 1 < len(subs) else stop
                piece = kb.NL.join(lines[number - 1:sub_stop])
                if has_body(piece):
                    local.append(child_record(doc_id, parent_id, chain, piece, sub))
        parent = {
            "chunk_id": parent_id,
            "doc_id": doc_id,
            "kind": "parent",
            "heading_path": chain,
            "content": block,
            "child_ids": [row["chunk_id"] for row in local],
        }
        chunks.extend(local)
        chunks.append(parent)

    for chunk in chunks:
        chunk["content_hash"] = kb.content_hash(chunk["content"])
        chunk["token_count"] = kb.estimate_tokens(chunk["content"])
    # order 记录块在文档里的先后，检索的滑动窗口靠它取「下一节」
    for position, chunk in enumerate(chunks):
        chunk["order"] = position

    document = {
        "doc_id": doc_id,
        "path": kb.rel(path),
        "title": title,
        "domain": str(meta["domain"]),
        "subdomain": str(meta.get("subdomain") or ""),
        "tags": kb.as_list(meta.get("tags")),
        "levels": kb.as_int_list(meta.get("level_range")),
        "dependencies": kb.as_list(meta.get("dependencies")),
        "supersedes": str(meta.get("supersedes") or ""),
        "updated": str(meta["updated"]),
        "chunk_strategy": str(meta.get("chunk_strategy") or STRATEGY),
        "source_tokens": kb.estimate_tokens(body),
        "source_hash": kb.content_hash(text),
    }
    return document, chunks


def build(all_files: bool = False, verbose: bool = False) -> dict:
    """切分全部知识文件并返回注册表。内容未变的文件复用旧条目。"""
    previous = kb.read_json(kb.REGISTRY_PATH, {"documents": {}, "chunks": {}})
    old_docs = previous.get("documents", {})
    old_chunks = previous.get("chunks", {})
    by_path = {row["path"]: row for row in old_docs.values()}
    old_chunks_by_doc = {}
    for chunk_id, chunk in old_chunks.items():
        old_chunks_by_doc.setdefault(chunk.get("doc_id"), []).append((chunk_id, chunk))

    documents: dict[str, dict] = {}
    chunks: dict[str, dict] = {}
    failures: list[str] = []
    reused = 0

    for path in kb.list_knowledge_files():
        digest = kb.content_hash(path.read_text(encoding="utf-8"))
        stale = by_path.get(kb.rel(path))
        if stale and not all_files and stale["source_hash"] == digest:
            documents[stale["doc_id"]] = stale
            for chunk_id, chunk in old_chunks_by_doc.get(stale["doc_id"], []):
                chunks[chunk_id] = chunk
            reused += 1
            continue
        try:
            doc, produced = split_doc(path)
        except (ValueError, OSError, UnicodeDecodeError) as exc:
            failures.append(kb.rel(path) + ": " + str(exc))
            continue
        documents[doc["doc_id"]] = doc
        for chunk in produced:
            chunks[chunk["chunk_id"]] = chunk
        if verbose:
            kids = [c for c in produced if c["kind"] == "child"]
            biggest = max((c["token_count"] for c in kids), default=0)
            print("  " + doc["doc_id"] + "  Parent=" + str(len({c["parent_id"] for c in kids}))
                  + "  Child=" + str(len(kids)) + "  最大Child=" + str(biggest))

    registry = {
        "strategy": STRATEGY,
        "documents": documents,
        "chunks": chunks,
        "failures": failures,
        "stats": {
            "documents": len(documents),
            "parents": sum(1 for c in chunks.values() if c["kind"] == "parent"),
            "children": sum(1 for c in chunks.values() if c["kind"] == "child"),
            "reused_documents": reused,
        },
    }
    return registry


def main() -> int:
    kb.configure_stdout()
    parser = argparse.ArgumentParser(description="知识库语义分块器")
    parser.add_argument("--all", action="store_true", help="忽略 content_hash，强制全量重切")
    parser.add_argument("--verbose", action="store_true", help="逐篇打印分块数量")
    parser.add_argument("--show", action="store_true", help="打印 Child 标题路径与令牌数")
    args = parser.parse_args()

    registry = build(all_files=args.all, verbose=args.verbose)

    if args.show:
        for doc_id in sorted(registry["documents"]):
            print(registry["documents"][doc_id]["path"] + "  (" + doc_id + ")")
            kids = [c for c in registry["chunks"].values()
                    if c["doc_id"] == doc_id and c["kind"] == "child"]
            for chunk in sorted(kids, key=lambda c: c["heading_path"]):
                print("   " + str(chunk["token_count"]).rjust(5) + "  " + chunk["heading_path"])
        return 0

    kb.write_json(kb.REGISTRY_PATH, registry)
    if registry["failures"]:
        print("FAIL  chunker  " + str(len(registry["failures"])) + " 个文件不符合规范")
        for row in registry["failures"]:
            print("      " + row)
        return 1
    stats = registry["stats"]
    print("PASS  chunker  文档=" + str(stats["documents"]) + "  Parent=" + str(stats["parents"])
          + "  Child=" + str(stats["children"]) + "  增量复用=" + str(stats["reused_documents"])
          + "  -> " + kb.rel(kb.REGISTRY_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
