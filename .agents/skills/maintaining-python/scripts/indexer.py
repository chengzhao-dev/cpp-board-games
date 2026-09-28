#!/usr/bin/env python3
"""知识库索引构建器：从 chunk_registry.json 增量构建 FTS5、向量与知识图谱。

为什么用 SQLite 而不是 FAISS / Tantivy：知识库要能在 CI 与 WSL 之间用同一个文件跑。
SQLite 自带 FTS5 与 bm25()；向量走 sqlite-vec 扩展（同一库文件、vec0 虚表），
把「再装一个向量库」换成「已存在的 SQLite 进程内扩展」。

检索由三层互补（retriever.py 按 RRF 融合）：
  FTS5：CJK 二元组与 ASCII 标识符，bm25() 负责精确召回。
  向量：sqlite-vec + MiniLM 多语模型，补充同义与改写类查询。
  图谱：concept / edge / community 三张表，补充符号与概念关联。

增量策略：以 content_hash 为准，未变的 Chunk 不重建 FTS 行。
删除的文件与消失的 Chunk 标 deprecated 而不是物理删除，支持回溯。

用法：
    python .agents/skills/maintaining-python/scripts/indexer.py              # 增量构建（先跑 chunker）
    python .agents/skills/maintaining-python/scripts/indexer.py --rebuild    # 推倒重建
    python .agents/skills/maintaining-python/scripts/indexer.py --verbose    # 打印每层的行数与耗时
退出码：0 = 成功，1 = 注册表缺失或有文件不符合规范。
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kb  # noqa: E402
from chunker import build as build_registry  # noqa: E402

IDENT_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{1,63}")
# 冲突检测专用的严格标识符：只认反引号片段内的完整符号名，不吃路径与散文词。
IDENT_STRICT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{2,63}$")
SPAN_RE = re.compile(r"`([^`\n]{1,80})`")
SCOPE_RE = re.compile(r"::|\(\)|\[\]")
CONFLICT_MIN_SHARED = 1
# 重合度降权上限：最多把旧版降到一半，避免词面相似就把知识压到看不见。
CONFLICT_MAX_PENALTY = 0.5
# FTS 布局标记：chunks_fts.rowid 与 chunks.rowid 对齐，删改走 rowid 而不是按值全表扫。
FTS_LAYOUT = "rowid-v1"
ASCII_RUN = re.compile(r"[A-Za-z0-9_]+")
CJK_RUN = re.compile(r"[一-鿿]{1,}")
# 停用词只放没有检索信号的英文虚词。C++ 关键字（this / int / const / std …）在
# C++ 知识库里就是被查的对象本身，把它们当噪声词会在查询侧直接清空 tokens，
# 「this」这类查询因此三路全零。曾在此列表里的语言关键字已全部移出。
STOP = {"the", "and", "for", "with", "that", "from", "use"}
SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS chunks (
        chunk_id   TEXT PRIMARY KEY,
        parent_id  TEXT,
        doc_id     TEXT NOT NULL,
        kind       TEXT NOT NULL,
        heading_path TEXT,
        content    TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        token_count INTEGER NOT NULL,
        domain     TEXT, subdomain TEXT, updated TEXT,
        tags       TEXT, levels TEXT, status TEXT NOT NULL DEFAULT 'live'
    );
    CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS concept (
        name TEXT PRIMARY KEY, kind TEXT, chunk_ids TEXT, doc_ids TEXT, weight REAL
    );
    CREATE TABLE IF NOT EXISTS edge (
        a TEXT, b TEXT, kind TEXT, weight REAL, PRIMARY KEY (a, b, kind)
    );
    CREATE TABLE IF NOT EXISTS community (
        id INTEGER, label TEXT, member TEXT, size INTEGER
    );
    CREATE TABLE IF NOT EXISTS query_cache (
        q TEXT PRIMARY KEY, payload TEXT, written_at REAL
    );
    CREATE TABLE IF NOT EXISTS summary (
        key TEXT PRIMARY KEY, doc_id TEXT, kind TEXT, ref_id TEXT,
        text TEXT, token_count INTEGER
    );
    CREATE TABLE IF NOT EXISTS conflict (
        older_doc TEXT, newer_doc TEXT, overlap REAL,
        shared TEXT, PRIMARY KEY (older_doc, newer_doc)
    );
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
        tokens,
        chunk_id UNINDEXED,
        doc_id UNINDEXED,
        tokenize = 'unicode61 remove_diacritics 2'
    );
    """,
)

# vec0 表在 connect() 里动态建（需要先加载 sqlite-vec 扩展），列维度来自 kb.EMBED_DIM。
VEC_SCHEMA = (
    "CREATE VIRTUAL TABLE IF NOT EXISTS " + kb.VEC_TABLE + " USING vec0("
    " chunk_id TEXT PRIMARY KEY, embedding float[" + str(kb.EMBED_DIM) + "]"
    ");"
)


def tokens(text: str) -> list[str]:
    """统一的分词口径：ASCII 标识符保留整体与拆解形式，中文产出二元组。

    索引与查询必须调用同一个函数，否则符号检索会静默失效（`shared_ptr` 被两边
    切成不同的 token，分数就永远是 0）。中文用二元组而不是单字，是因为单字在
    中文里歧义太高（指/针 各自能匹配大片无关段落），二元组基本等于词。
    """
    out: list[str] = []
    for run in ASCII_RUN.findall(text):
        parts = [part for part in run.lower().split("_") if part]
        if len(parts) > 1:
            out.extend(part for part in parts if part not in STOP)
            out.append("".join(parts))
        elif parts and parts[0] not in STOP:
            out.append(parts[0])
    for run in CJK_RUN.findall(text):
        if len(run) == 1:
            out.append(run)
        else:
            out.extend(run[i:i + 2] for i in range(len(run) - 1))
    for chunk in re.split(r"[:/./-]+", text):
        for run in ASCII_RUN.findall(chunk):
            lowered = run.lower()
            if lowered not in STOP and lowered not in out:
                out.append(lowered)
    return out


def align_fts_rowids(con: sqlite3.Connection) -> int:
    """把 chunks_fts 的 rowid 对齐到主表，返回重建的行数。

    FTS5 里 chunk_id 是 UNINDEXED 列，按它删除会退化成全表扫描，增量索引因此
    近似 O(N^2)。对齐后删改都按 rowid 定位，代价与索引规模无关。历史行的 rowid
    与主表无对应关系，所以只在布局迁移时整体重建一次。
    """
    con.execute("DELETE FROM chunks_fts")
    rows = con.execute("SELECT rowid, chunk_id, doc_id, content FROM chunks "
                       "WHERE status='live' ORDER BY rowid").fetchall()
    con.executemany(
        "INSERT INTO chunks_fts(rowid, tokens, chunk_id, doc_id) VALUES (?,?,?,?)",
        [(rowid, " ".join(tokens(content)), chunk_id, doc_id)
         for rowid, chunk_id, doc_id, content in rows],
    )
    return len(rows)


def graph_nodes(content: str, doc: dict) -> list[tuple[str, str]]:
    """从 Chunk 里抽图谱节点：C++ 标识符 + 文档标签。"""
    nodes = []
    for name in IDENT_RE.findall(content):
        if len(name) > 2 and name.lower() not in STOP:
            nodes.append((name, "symbol"))
    for tag in doc.get("tags", []):
        if tag:
            nodes.append((tag, "tag"))
    return nodes


def connect(con: sqlite3.Connection) -> None:
    # 旧版 conflict 表按 (concept, older_doc) 逐行记，且 overlap 因 chunk_id 命名空间
    # 恒为 0（见 detect_conflicts 的说明），口径与新版不兼容：先删表，再按新 schema 重建。
    stale = {row[1] for row in con.execute("PRAGMA table_info(conflict)")}
    if stale and "shared" not in stale:
        con.execute("DROP TABLE conflict")
    con.executescript(SCHEMA[0])
    con.executescript(SCHEMA[1])
    con.execute("PRAGMA journal_mode=WAL")
    # FTS rowid 布局：缺标记（旧库或新库）时对齐一次，之后增量都按 rowid 删改。
    mark = con.execute("SELECT value FROM meta WHERE key='fts_layout'").fetchone()
    if not mark or mark[0] != FTS_LAYOUT:
        align_fts_rowids(con)
        con.execute("INSERT INTO meta VALUES ('fts_layout', ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (FTS_LAYOUT,))


def upsert(con: sqlite3.Connection, chunk: dict, doc: dict, previous: dict) -> str:
    """写入一个 Chunk，返回动作：insert / update / unchanged。"""
    existing = previous.get(chunk["chunk_id"])
    if (existing and existing["content_hash"] == chunk["content_hash"]
            and existing.get("status", "live") == "live"):
        return "unchanged"
    action = "update" if existing else "insert"
    payload = (
        chunk["chunk_id"], chunk.get("parent_id"), chunk["doc_id"], chunk["kind"],
        chunk["heading_path"], chunk["content"], chunk["content_hash"],
        chunk["token_count"], doc["domain"], doc["subdomain"], doc["updated"],
        ",".join(doc["tags"]), ",".join(map(str, doc["levels"])), "live",
    )
    columns = ("chunk_id, parent_id, doc_id, kind, heading_path, content, content_hash,"
               " token_count, domain, subdomain, updated, tags, levels, status")
    marks = ", ".join(["?"] * 14)
    con.execute(
        "INSERT INTO chunks (" + columns + ") VALUES (" + marks + ") "
        "ON CONFLICT(chunk_id) DO UPDATE SET content=excluded.content,"
        "content_hash=excluded.content_hash,token_count=excluded.token_count,"
        "heading_path=excluded.heading_path,updated=excluded.updated,"
        "status=excluded.status",
        payload,
    )
    rowid = con.execute("SELECT rowid FROM chunks WHERE chunk_id=?",
                        (chunk["chunk_id"],)).fetchone()[0]
    con.execute("DELETE FROM chunks_fts WHERE rowid=?", (rowid,))
    con.execute(
        "INSERT INTO chunks_fts(rowid, tokens, chunk_id, doc_id) VALUES (?,?,?,?)",
        (rowid, " ".join(tokens(chunk["content"])),
         chunk["chunk_id"], chunk["doc_id"]),
    )
    return action


def build_graph(con: sqlite3.Connection) -> tuple[int, int]:
    """重建图谱：节点权重 = 出现的 Chunk 数，边 = 同块共现次数，社区 = 连通分量。"""
    con.execute("DELETE FROM concept")
    con.execute("DELETE FROM edge")
    con.execute("DELETE FROM community")
    occurrences: dict[str, list[str]] = defaultdict(list)
    docs: dict[str, set] = defaultdict(set)
    kinds: dict[str, str] = {}
    pairs: dict[tuple[str, str, str], float] = defaultdict(float)
    for chunk_id, doc_id, content, tags in con.execute(
        "SELECT chunk_id, doc_id, content, tags FROM chunks WHERE kind='child' AND status='live'"
    ):
        nodes = sorted({name for name, _kind in graph_nodes(content, {"tags": (tags or "").split(",")})})
        nodes = nodes[:40]
        for name in nodes:
            occurrences[name].append(chunk_id)
            docs[name].add(doc_id)
            kinds.setdefault(name, "symbol")
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                pairs[(nodes[i], nodes[j], "co")] += 1.0
    for name, chunk_ids in occurrences.items():
        con.execute(
            "INSERT INTO concept VALUES (?,?,?,?,?)",
            (name, kinds[name], ",".join(chunk_ids), ",".join(sorted(docs[name])), len(chunk_ids)),
        )
    for (a, b, kind), weight in pairs.items():
        con.execute("INSERT OR REPLACE INTO edge VALUES (?,?,?,?)", (a, b, kind, weight))
    communities = connected_components(list(occurrences), [(a, b) for (a, b, _k) in pairs])
    for cid, members in enumerate(communities):
        top = sorted(members, key=lambda m: -len(occurrences[m]))[:6]
        for member in members:
            con.execute("INSERT INTO community VALUES (?,?,?,?)",
                        (cid, ", ".join(top), member, len(members)))
    return len(occurrences), len(pairs)


def connected_components(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    """并查集求连通分量，作为图谱社区（无第三方图库时的最小可用实现）。"""
    parent = {node: node for node in nodes}

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    groups: dict[str, list[str]] = defaultdict(list)
    for node in nodes:
        groups[find(node)].append(node)
    return sorted(groups.values(), key=len, reverse=True)


def summarize(value: str, limit: int) -> str:
    """把 Chunk 压成一行概要：去掉 Markdown 装饰，按令牌上限截断。

    L1/L2 摘要存在的意义是「先看目录再看正文」：agent 花 50 令牌就能判断该不该
    读某个 Parent，而不是每次都把正文灌进上下文。截断按 estimate_tokens 倒序试探，
    这样摘要的令牌数和检索预算用的是同一口径，不会出现「摘要号称 50 实际 120」。
    """
    backtick = chr(96)
    sharp = chr(35)
    parts = []
    for raw in value.split(kb.NL):
        line = raw.strip()
        if not line or line.startswith(backtick):
            continue
        while line.startswith(sharp):
            line = line.lstrip(sharp).lstrip()
        line = line.replace(chr(42) * 2, "").replace(backtick, "")
        if line:
            parts.append(line)
    flat = "; ".join(parts)
    for index in range(len(flat), 0, -1):
        piece = flat[:index].rstrip()
        if piece and kb.estimate_tokens(piece) <= limit:
            return piece
    return ""


def build_summaries(con: sqlite3.Connection, registry: dict) -> tuple[int, int]:
    """写入 L1（文档一句话）与 L2（每个 Parent 概要）。L3 就是 Chunk 本身。

    摘要随索引一起重建，因此永远不比正文陈旧。单独记一份摘要时间戳只会多出
    第二个真相源，增量判断仍然只看 content_hash。
    """
    con.execute("DELETE FROM summary")
    counters = defaultdict(int)
    children_by_doc = defaultdict(list)
    for chunk in registry["chunks"].values():
        if chunk["kind"] == "child":
            children_by_doc[chunk["doc_id"]].append(chunk)
    for doc_id, doc in registry["documents"].items():
        kids = children_by_doc.get(doc_id, [])
        topics = []
        for kid in sorted(kids, key=lambda c: c.get("order", 0)):
            topic = kid["heading_path"].split(" > ")[-1]
            if topic not in topics:
                topics.append(topic)
        one_line = doc["title"] + ": " + "、".join(topics[:6])
        if len(topics) > 6:
            one_line += " 等 " + str(len(topics)) + " 节"
        con.execute(
            "INSERT OR REPLACE INTO summary VALUES (?,?,?,?,?,?)",
            ("l1:" + doc_id, doc_id, "l1", doc_id, one_line, kb.estimate_tokens(one_line)),
        )
        counters["l1"] += 1
    for chunk_id, chunk in registry["chunks"].items():
        if chunk["kind"] != "parent":
            continue
        brief = summarize(chunk["content"], 200)
        con.execute(
            "INSERT OR REPLACE INTO summary VALUES (?,?,?,?,?,?)",
            ("l2:" + chunk_id, chunk["doc_id"], "l2", chunk_id, brief,
             kb.estimate_tokens(brief)),
        )
        counters["l2"] += 1
    return counters["l1"], counters["l2"]


def doc_concepts(registry: dict) -> dict:
    """文档级概念集合：frontmatter tags ∪ 代码片段里的严格标识符。

    刻意不用 graph_nodes()：后者把正文里所有 ASCII 串都当标识符，于是
    `.agents/skills/writing-quarto/references/…` 贡献 `references`、`GitHub Pages`
    贡献 `github`，四份 tooling 文档靠这类路径碎片「共享概念」，重合度全是噪声。
    这里只认反引号片段内的完整标识符（3–64 字符、允许下划线），加上人工维护的 tags。
    """
    out: dict[str, set] = {doc_id: set() for doc_id in registry["documents"]}
    for doc_id, doc in registry["documents"].items():
        for tag in doc.get("tags", []):
            if tag:
                out[doc_id].add(str(tag))
    for chunk in registry["chunks"].values():
        bucket = out.setdefault(chunk["doc_id"], set())
        for span in SPAN_RE.findall(chunk["content"]):
            for piece in SCOPE_RE.split(span):
                piece = piece.strip()
                if IDENT_STRICT_RE.match(piece):
                    bucket.add(piece)
    return out


def detect_conflicts(con: sqlite3.Connection, registry: dict) -> int:
    """两份文档覆盖同一批概念、且新版更新更晚 → 记一条待确认冲突。

    三个限定条件都是实测逼出来的，缺一个就会误报或误降权：
    1. 重合度取文档级概念名集合的 Jaccard。旧实现按 chunk_id 取交集，而 chunk_id
       以 doc_id 为前缀，跨文档交集恒空 → overlap 恒 0 → 检索侧降权从未生效。
    2. 跳过已被 supersedes 关联的一对：版本演进已有明确结论，再报冲突是重复告警。

    刻意不猜「描述是否矛盾」：纯词面分不清互补还是冲突，猜错会把正确知识静默降权。
    所以只报告共享概念名与较旧的一方，人工确认后再改 supersedes。
    """
    con.execute("DELETE FROM conflict")
    concepts = doc_concepts(registry)
    docs = registry["documents"]
    dates = {d: str(docs[d].get("updated", "")) for d in docs}
    supersedes = {d: str(docs[d].get("supersedes") or "") for d in docs}
    rows = 0
    ids = sorted(docs)
    for index, first in enumerate(ids):
        for second in ids[index + 1:]:
            # 配对只按 doc_id 枚举一次，新旧方向必须按 updated 判定：ID 顺序和
            # 日期顺序没有必然关系（doc-new 可能比 doc-old 更新）。日期相同则
            # 无从判断谁替代谁，直接跳过。
            if dates[first] < dates[second]:
                older, newer = first, second
            elif dates[second] < dates[first]:
                older, newer = second, first
            else:
                continue
            if not concepts.get(older) or not concepts.get(newer):
                continue
            if supersedes[newer] == older or supersedes[older] == newer:
                continue
            shared = concepts[older] & concepts[newer]
            if len(shared) < CONFLICT_MIN_SHARED:
                continue
            overlap = len(shared) / max(1, len(concepts[older] | concepts[newer]))
            con.execute(
                "INSERT INTO conflict VALUES (?,?,?,?)",
                (older, newer, round(overlap, 3), ",".join(sorted(shared))),
            )
            rows += 1
    return rows
def prune(con: sqlite3.Connection, alive: set) -> int:
    """把注册表里已经消失的 Chunk 标 deprecated（不物理删除，支持回溯）。"""
    rows = list(con.execute("SELECT chunk_id, rowid FROM chunks"))
    gone = [r for r in rows if r[0] not in alive]
    for chunk_id, rowid in gone:
        con.execute("UPDATE chunks SET status='deprecated' WHERE chunk_id=?", (chunk_id,))
        con.execute("DELETE FROM chunks_fts WHERE rowid=?", (rowid,))
    return len(gone)


def main() -> int:
    kb.configure_stdout()
    parser = argparse.ArgumentParser(description="知识库双层索引构建器")
    parser.add_argument("--rebuild", action="store_true", help="清空索引后全量重建")
    parser.add_argument("--verbose", action="store_true", help="打印每层行数与耗时")
    args = parser.parse_args()

    started = time.time()
    kb.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if args.rebuild and kb.DB_PATH.is_file():
        kb.DB_PATH.unlink()
        kb.REGISTRY_PATH.unlink(missing_ok=True)

    registry = build_registry(all_files=args.rebuild)
    if registry["failures"]:
        print("FAIL  indexer  分块阶段有文件不符合规范")
        for row in registry["failures"]:
            print("      " + row)
        return 1
    kb.write_json(kb.REGISTRY_PATH, registry)

    chunks = registry["chunks"]
    documents = registry["documents"]
    previous = {}
    con = sqlite3.connect(kb.DB_PATH)
    connect(con)
    if not args.rebuild:
        previous = {
            row[0]: {"content_hash": row[1], "status": row[2]}
            for row in con.execute("SELECT chunk_id, content_hash, status FROM chunks")
        }

    counts = defaultdict(int)
    for chunk_id, chunk in sorted(chunks.items()):
        doc = documents[chunk["doc_id"]]
        counts[upsert(con, chunk, doc, previous)] += 1
    deprecated = prune(con, set(chunks))
    concepts, edges = build_graph(con)
    l1, l2 = build_summaries(con, registry)
    conflicts = detect_conflicts(con, registry)
    con.execute("INSERT INTO meta VALUES ('built_at', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (time.strftime("%Y-%m-%dT%H:%M:%S"),))
    con.commit()

    live = con.execute("SELECT count(*) FROM chunks WHERE status='live'").fetchone()[0]
    if concepts == 0 or live == 0:
        print("FAIL  indexer  索引为空，检查 .agents/knowledge/ 是否有合规文件")
        con.close()
        return 1
    print("PASS  indexer  Chunk=" + str(live) + "  新增=" + str(counts["insert"])
          + "  更新=" + str(counts["update"]) + "  跳过=" + str(counts["unchanged"])
          + "  降权=" + str(deprecated) + "  概念=" + str(concepts) + "  边=" + str(edges)
          + "  摘要L1=" + str(l1) + " L2=" + str(l2) + " 冲突候选=" + str(conflicts))
    if args.verbose:
        print("      耗时 " + format(time.time() - started, ".2f") + "s"
              "  文档=" + str(len(documents))
              + "  FTS行=" + str(con.execute('SELECT count(*) FROM chunks_fts').fetchone()[0])
              + "  社区=" + str(con.execute("SELECT count(DISTINCT id) FROM community").fetchone()[0]))
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
