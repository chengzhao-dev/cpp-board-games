#!/usr/bin/env python3
"""检索管道：查询改写 -> 元数据预过滤 -> BM25 + 图谱 -> RRF 融合 -> 精排 -> Parent 扩展。

对应知识库四大原则：
  不读全量：Child 命中后回溯替换成 Parent，并按令牌预算裁剪，永不返回整篇文档。
  不乱读：先按 domain/tags/level 预过滤缩小候选集，再双路召回与精排。
  不阻塞增长：只查索引，索引由 indexer.py 增量维护。
  不信任单一检索：BM25 抓精确词面、图谱补充概念关联、RRF(k=60) 融合、最后精排。

回退实现必须说清楚，别当成真实模型：
  Stage 1 查询改写 = 规则改写（去口语前缀、抽符号、拆并列项），不调用 LLM。
  Stage 2/4 精排 = 词面重合度打分，可插拔点是 rerank_score()。
  Stage 3 的 BM25 是 SQLite FTS5 的真实 bm25()，不是近似实现。

版本与冲突（§3.6）：supersedes 指向的旧版命中乘 0.35 惩罚，冲突表里较旧的一方
  按块重合度降权（最多降一半）。
渐进式披露（§3.4）：--toc 只给 L1/L2 摘要地图（几百令牌），再用 --parent <ref_id>
  取 L3 正文。命中段落末尾含「接下来/下一节」时自动追加 1 个同级 Child（最多 1 次）。
缓存（§3.5）：非 explain 排名结果按全参数键缓存 24h，命中时不重跑四路召回。

用法：
    python .agents/skills/maintaining-python/scripts/retriever.py "shared_ptr 循环引用怎么打破"
    python .agents/skills/maintaining-python/scripts/retriever.py --explain "std::span 和裸指针加长度比有什么好处"
    python .agents/skills/maintaining-python/scripts/retriever.py --domain cpp_core --level 5 --budget 2500 "所有权转移"
    python .agents/skills/maintaining-python/scripts/retriever.py --rounds 2 --json "动态库为什么需要 RPATH"
退出码：0 = 有注入结果，2 = 无结果（便于上层脚本判断）。
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kb  # noqa: E402
from indexer import CONFLICT_MAX_PENALTY, tokens  # noqa: E402  分词口径必须与索引一致

RRF_K = 60
# 精排候选池：RRF 只负责排序，没有否决权。单路强命中（名次在前 5）即使融合分被
# 噪声向量挤到 20 名之外，也必须进精排，否则 `侵入式` 这种稀有精确词会被静默丢弃。
RESCUE_RANK = 5
CANDIDATE_POOL = 20
# 融合分只作为精排之后的补充信号，不让检索名次盖过正文词面命中。
RRF_SCORE_WEIGHT = 8.0
QUOTE = chr(34)
SYMBOL_PATTERN = r"[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z0-9_~]+)+"
DOTTED_PATTERN = r"[A-Za-z_][A-Za-z0-9_]{3,}"
# 意图判定只认真正的语言符号（带 :: 的作用域名）。否则 vector / list 这类普通英文
# 词会被误判成符号查询并抢占分类，图谱那一路的权重就架空了。
SYMBOL_RE = re.compile(SYMBOL_PATTERN)
# 召回侧用宽松符号（含普通长标识符），那里只影响候选补充，不改变意图。
LOOSE_SYMBOL_RE = re.compile(SYMBOL_PATTERN + chr(124) + DOTTED_PATTERN)
BARE_WORD_RE = re.compile(DOTTED_PATTERN)
CONTRAST_RE = re.compile('|'.join(["区别", "不同", "对比", "比较", "哪个更", "优劣", "差异", "vs"]))
CODE_RE = re.compile('|'.join(["代码", "示例", "写法", "怎么实现", "implement"]))
NAV_RE = re.compile('|'.join(["目录", "大纲", "章节"]))
NOISE_RE = re.compile("^(请问|帮我|麻烦|能不能|可以|解释一下|讲讲|说下)+")
# 精排专用的口语疑问二元组：只从查询侧覆盖率分母里剔除，索引侧 tokens()
# 保持不变。中文二元组切不出词界，「什么」会连带产生「学什/么后/和什」这类碎片，
# 而它本身在散文标题里高频出现（「工具链为什么是…」），留在分母里会把真正的
# 领域词稀释掉，让无关段落靠一个虚词拿到非零覆盖率。
RERANK_QUERY_NOISE = frozenset({"什么"})
SPLIT_RE = re.compile('[，、；;]')
SUPERSEDED_FACTOR = 0.35
CACHE_TTL = 24 * 3600
NEXT_RE = re.compile('|'.join(["接下来", "下一节", "下一章", "下一段", "随后", "继续看", "see next"]))


class TokenBudgetController:
    """按硬上限裁剪注入内容：优先给 Parent，Parent 放不下就降级给 Child。"""

    MAX_CONTEXT_TOKENS = kb.MAX_CONTEXT_TOKENS
    RESERVED_FOR_RESPONSE = kb.RESERVED_FOR_RESPONSE
    AVAILABLE_FOR_RETRIEVAL = kb.AVAILABLE_FOR_RETRIEVAL

    def __init__(self, budget: int | None = None):
        self.budget = self.AVAILABLE_FOR_RETRIEVAL if budget is None else budget

    def select(self, candidates: list[dict]) -> tuple[list[dict], int]:
        selected: list[dict] = []
        seen: set[str] = set()
        used = 0
        for item in candidates:
            child = item["child"]
            parent = item.get("parent")
            if child["chunk_id"] in seen or (parent and parent["chunk_id"] in seen):
                continue
            if parent and used + parent["token_count"] <= self.budget:
                selected.append(parent)
                used += parent["token_count"]
                seen.add(parent["chunk_id"])
            elif used + child["token_count"] <= self.budget:
                selected.append(child)          # 超预算降级：Parent -> Child
                used += child["token_count"]
                seen.add(child["chunk_id"])
            else:
                continue                       # 紧预算时继续找放得下的小块，不整体放弃
        return selected, used


def classify(query: str) -> dict:
    """意图分类（轻量规则，不用 LLM）：决定 BM25 与图谱两路的相对权重。"""
    symbols = SYMBOL_RE.findall(query)
    if NAV_RE.search(query):
        kind = "navigation"
    elif symbols:
        kind = "symbol"
    elif CONTRAST_RE.search(query):
        kind = "contrast"
    elif CODE_RE.search(query):
        kind = "code"
    else:
        kind = "concept"
    weights = {
        "symbol": (3.0, 0.2),
        "concept": (1.0, 0.6),
        "contrast": (1.2, 2.0),
        "code": (2.2, 0.4),
        "navigation": (1.5, 0.2),
    }
    return {"kind": kind, "symbols": symbols, "weights": weights[kind]}


def rewrite(query: str) -> list[str]:
    """Stage 1：规则改写。去口语前缀，长句按并列符号拆子查询，符号单独成一个子查询。"""
    base = NOISE_RE.sub("", query).strip() or query.strip()
    subs: list[str] = []
    if len(base) > 24:
        for piece in SPLIT_RE.split(base):
            piece = piece.strip()
            if len(piece) >= 6:
                subs.append(piece)
    for symbol in LOOSE_SYMBOL_RE.findall(base)[:3]:
        if symbol not in subs:
            subs.append(symbol)
    out: list[str] = []
    for item in [base] + subs:
        if item and item not in out:
            out.append(item)
    return out[:3]


def fts_match(query: str) -> str:
    """构造 FTS5 MATCH 串：token 以 OR 组合，排序交给 bm25() 而不是布尔过滤。

    用 AND 会让中文二元组几乎必然漏一个而整体为 0 命中，所以这里刻意用 OR。
    """
    terms = [t for t in dict.fromkeys(tokens(query)) if t]
    if not terms:
        return ""
    return " OR ".join(QUOTE + t + QUOTE for t in terms[:24])


def child_ids_by_doc(registry: dict) -> dict:
    """doc_id -> 该文档全部 live Child id，用于文档级字段（level_range）预过滤。"""
    mapping: dict[str, list[str]] = {}
    for chunk_id, chunk in registry["chunks"].items():
        if chunk.get("kind") == "child":
            mapping.setdefault(chunk["doc_id"], []).append(chunk_id)
    return mapping




def cache_key(query, domain, subdomain, level, tags, budget, rounds):
    """缓存键含全部影响结果的参数：少带一个就会命中「看着对但其实是别的过滤条件」的旧结果。"""
    shape = chr(124).join([
        "q=" + query, "d=" + domain, "s=" + subdomain, "l=" + str(level),
        "t=" + ",".join(sorted(tags or [])),
        "$" + str(budget), "r=" + str(rounds),
    ])
    return kb.content_hash(shape)


def cache_get(con: sqlite3.Connection, key: str):
    """24h TTL 的查询缓存。过期行顺手删掉，避免冷查询无限堆积。"""
    row = con.execute("SELECT payload, written_at FROM query_cache WHERE q=?", (key,)).fetchone()
    if not row:
        return None
    if time.time() - float(row[1]) > CACHE_TTL:
        con.execute("DELETE FROM query_cache WHERE q=?", (key,))
        con.commit()
        return None
    try:
        return json.loads(row[0])
    except json.JSONDecodeError:
        con.execute("DELETE FROM query_cache WHERE q=?", (key,))
        con.commit()
        return None


def cache_put(con: sqlite3.Connection, key: str, payload: dict) -> None:
    """只缓存非 explain 的排名结果：正文注入体积大且已经排好，缓存它没有收益。"""
    slim = {k: v for k, v in payload.items() if k not in ("injected", "elapsed_ms")}
    slim["injected"] = [
        {k: v for k, v in row.items() if k != "content"} for row in payload.get("injected", [])
    ]
    slim["cached"] = True
    con.execute(
        "INSERT INTO query_cache VALUES (?,?,?) ON CONFLICT(q) DO UPDATE SET"
        " payload=excluded.payload, written_at=excluded.written_at",
        (key, json.dumps(slim, ensure_ascii=False), time.time()),
    )
    con.commit()


def stale_factors(con: sqlite3.Connection, registry: dict) -> dict:
    """返回 doc_id -> 惩罚系数（<1 才降权）。

    两个来源：frontmatter 的 supersedes（明确的版本替代，旧版一律降到
    SUPERSEDED_FACTOR），以及 conflict 表（两份文档覆盖同一批概念且新版更新更晚，
    旧版按概念名集合的重合度降权，最多降一半）。
    """
    factors: dict[str, float] = {}
    docs = registry["documents"]
    for doc_id, doc in docs.items():
        target = str(doc.get("supersedes") or "")
        if target and target != doc_id:
            factors[target] = SUPERSEDED_FACTOR
    try:
        rows = list(con.execute("SELECT older_doc, newer_doc, overlap FROM conflict"))
    except sqlite3.OperationalError:
        rows = []
    for older, newer, overlap in rows:
        if older not in docs or newer not in docs:
            continue
        penalty = 1.0 - min(CONFLICT_MAX_PENALTY, float(overlap))
        factors[older] = min(factors.get(older, 1.0), penalty)
    return factors


def sibling_after(registry: dict, chunk: dict):
    """滑动窗口要追加的下一块：Child 命中给同 Parent 的下一块，Parent 命中给下一节首块。

    刻意只返回 Child：Parent 动辄 700 令牌，追加一个 Parent 等于把预算翻倍，
    「最多 1 次」的扩展就变成「多读一大段」，与不读全量的原则相冲突。
    """
    chunks = registry["chunks"]
    position = chunk.get("order")
    if position is None:
        return None
    if chunk["kind"] == "parent":
        parents = sorted((c for c in chunks.values() if c["kind"] == "parent"),
                         key=lambda c: c.get("order", 0))
        index = next((i for i, c in enumerate(parents) if c["chunk_id"] == chunk["chunk_id"]), None)
        if index is None or index + 1 >= len(parents):
            return None
        kids = sorted((c for c in chunks.values()
                       if c["kind"] == "child" and c.get("parent_id") == parents[index + 1]["chunk_id"]),
                      key=lambda c: c.get("order", 0))
        return kids[0] if kids else None
    kids = sorted((c for c in chunks.values()
                   if c["kind"] == "child" and c.get("parent_id") == chunk.get("parent_id")),
                  key=lambda c: c.get("order", 0))
    for kid in kids:
        if kid.get("order", 0) > position:
            return kid
    return None


def summaries(con: sqlite3.Connection, doc_ids: list[str], kind: str) -> list[dict]:
    """取 L1（文档一句话）或 L2（Parent 概要）摘要，按令牌口径统计。"""
    if not doc_ids:
        return []
    marks = ", ".join(["?"] * len(doc_ids))
    sql = "SELECT key, ref_id, text, token_count FROM summary WHERE kind=? AND doc_id IN (" + marks + ")"
    rows = []
    for key, ref_id, text_value, token_count in con.execute(sql, [kind] + list(doc_ids)):
        rows.append({"key": key, "ref_id": ref_id, "text": text_value,
                     "token_count": token_count})
    return rows


def rank_parents(query: str, rows: list[dict], candidates: list[dict]) -> list[dict]:
    """给 --toc 摘要地图的 Parent 排序：概要词面得分 + 子块召回名次加成。

    地图只回 ref_id 和概要，本身必须按查询相关性排列。按索引插入序返回会让
    「用几百令牌决定读哪个 Parent」变成让 agent 从头翻目录。
    """
    bonus: dict[str, float] = {}
    for rank, row in enumerate(candidates, start=1):
        parent = row.get("parent")
        if parent:
            bonus.setdefault(parent["chunk_id"], 1.0 / (RRF_K + rank))
    for row in rows:
        row["score"] = round(rerank_score(query, row["text"])
                              + RRF_SCORE_WEIGHT * bonus.get(row["ref_id"], 0.0), 4)
    rows.sort(key=lambda row: (-row["score"], row["ref_id"]))
    return rows

def prefilter(con: sqlite3.Connection, registry: dict, domain: str, subdomain: str,
              level, tags: list[str]):
    """Stage 2：元数据预过滤，把候选缩到「可能被读到」的最小集合。
    返回 None 表示不设限。返回空集合由调用方按过滤过窄处理。
    """
    sql = ["SELECT chunk_id FROM chunks WHERE kind=" + chr(39) + "child" + chr(39)
           + " AND status=" + chr(39) + "live" + chr(39)]
    args: list[object] = []
    if domain:
        sql.append("AND domain=?")
        args.append(domain)
    if subdomain:
        sql.append("AND subdomain LIKE ?")
        args.append("%" + subdomain + "%")
    if tags:
        sql.append("AND (" + " OR ".join(["tags LIKE ?"] * len(tags)) + ")")
        args.extend("%," + t + ",%" for t in tags)
    allow = {r for (r,) in con.execute(" ".join(sql), args)}
    if level is None:
        return allow
    mapping = child_ids_by_doc(registry)
    keep: set[str] = set()
    for doc in registry["documents"].values():
        spans = doc.get("levels") or []
        if not spans or min(spans) <= level <= max(spans):
            keep.update(mapping.get(doc["doc_id"], []))
    return allow & keep


def bm25_search(con: sqlite3.Connection, query: str, allow, limit: int) -> list[str]:
    match = fts_match(query)
    if not match:
        return []
    rows = [r for (r,) in con.execute(
        "SELECT chunk_id FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) LIMIT ?",
        (match, limit * 3))]
    if allow is None:
        return rows[:limit]
    return [r for r in rows if r in allow][:limit]


def graph_search(con: sqlite3.Connection, query: str, allow, limit: int) -> list[str]:
    """图谱侧召回：查询命中的概念节点，取其挂载的 Chunk（对比类查询主要靠这条）。"""
    names = {n.lower() for n in LOOSE_SYMBOL_RE.findall(query)} | {n.lower() for n in BARE_WORD_RE.findall(query)}
    hits: list[str] = []
    if not names:
        return hits
    picked = list(names)[:8]
    clause = " OR ".join(["name LIKE ?"] * len(picked))
    for chunk_ids in con.execute("SELECT chunk_ids FROM concept WHERE (" + clause + ")",
                                 ["%" + n + "%" for n in picked]):
        for chunk_id in chunk_ids[0].split(","):
            if chunk_id and chunk_id not in hits and (allow is None or chunk_id in allow):
                hits.append(chunk_id)
    return hits[:limit]


def merge_lists(lists: list[list[str]]) -> list[str]:
    """多个子查询的名次再融合一次（同样用 RRF），保证子查询之间平权。"""
    scores: dict[str, float] = {}
    for listing in lists:
        for rank, chunk_id in enumerate(listing, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
    return [c for c, _s in sorted(scores.items(), key=lambda kv: -kv[1])]


def rrf_fusion(lists: list[list[str]], weights: tuple) -> dict:
    """Reciprocal Rank Fusion：score = Σ weight / (k + rank)。"""
    scores: dict[str, float] = {}
    for index, listing in enumerate(lists):
        weight = weights[index] if index < len(weights) else 1.0
        for rank, chunk_id in enumerate(listing, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + weight / (RRF_K + rank)
    return scores


def rerank_score(query: str, content: str) -> float:
    """精排（词面重合度回退实现）：查询词覆盖率 + 符号命中奖励。

    这不是 Cross-Encoder。换成 bge-reranker 之类模型时只替换本函数，
    排序接口与预算裁剪都不用动。
    """
    q_tokens = [t for t in dict.fromkeys(tokens(query))
                if len(t) > 1 and t not in RERANK_QUERY_NOISE]
    if not q_tokens:
        return 0.0
    c_tokens = set(tokens(content))
    coverage = sum(1 for t in q_tokens if t in c_tokens) / len(q_tokens)
    symbols = sum(1 for s in LOOSE_SYMBOL_RE.findall(query) if s.lower() in content.lower())
    return coverage + 0.25 * min(symbols, 4)


def index_of(listing: list[str], chunk_id: str):
    return listing.index(chunk_id) + 1 if chunk_id in listing else None




def retrieve(query: str, domain: str = "", subdomain: str = "", level=None,
             tags: list[str] | None = None, budget: int | None = None, rounds: int = 1,
             explain: bool = False, toc: bool = False):
    """五阶段检索 + 版本降权 + 滑动窗口 + 24h 查询缓存。toc=True 时只回摘要地图。"""
    started = time.time()
    if not kb.DB_PATH.is_file():
        raise SystemExit("FAIL  retriever  索引不存在，先运行 python .agents/skills/maintaining-python/scripts/indexer.py")
    registry = kb.read_json(kb.REGISTRY_PATH, {"documents": {}, "chunks": {}})
    if not registry.get("chunks"):
        raise SystemExit("FAIL  retriever  注册表为空，先运行 python .agents/skills/maintaining-python/scripts/indexer.py")
    con = sqlite3.connect(kb.DB_PATH)
    tags = tags or []

    key = cache_key(query, domain, subdomain, level, tags, budget, rounds)
    if not explain and not toc:
        hit = cache_get(con, key)
        if hit:
            hit["cache"] = "hit"
            hit["elapsed_ms"] = round((time.time() - started) * 1000, 1)
            con.close()
            return hit

    intent = classify(query)
    subqueries = rewrite(query)
    allow = prefilter(con, registry, domain, subdomain, level, tags)
    if allow is not None and not allow:
        allow = None  # 过滤后为空时放宽而不是直接失败，体检会报告过窄的过滤

    bm25 = merge_lists([bm25_search(con, q, allow, 20) for q in subqueries])
    graph = graph_search(con, query, allow, 20)
    scores = rrf_fusion([bm25, graph], intent["weights"])
    penalties = stale_factors(con, registry)

    pool = sorted(scores.items(), key=lambda kv: -kv[1])[:CANDIDATE_POOL]
    picked = {chunk_id for chunk_id, _f in pool}
    for listing in (bm25,):
        for rank, chunk_id in enumerate(listing[:RESCUE_RANK], start=1):
            if chunk_id in scores and chunk_id not in picked:
                picked.add(chunk_id)
                pool.append((chunk_id, scores[chunk_id]))
    candidates = []
    for chunk_id, fused in pool:
        child = registry["chunks"][chunk_id]
        parent = registry["chunks"].get(child.get("parent_id"))
        penalty = penalties.get(child["doc_id"], 1.0)
        candidates.append({
            "child": child,
            "parent": parent,
            "rrf": fused,
            "rerank": rerank_score(query, child["content"]),
            "penalty": penalty,
            "bm25_rank": index_of(bm25, chunk_id),
            "graph_hit": chunk_id in graph,
        })
    # 精排主导、RRF 次之，再乘版本惩罚。同分时优先更短的 Parent 以省预算
    for row in candidates:
        row["score"] = (row["rerank"] + RRF_SCORE_WEIGHT * row["rrf"]) * row["penalty"]
    candidates.sort(key=lambda c: (-c["score"],
                                   c["parent"]["token_count"] if c["parent"] else c["child"]["token_count"]))

    doc_ids = sorted({row["child"]["doc_id"] for row in candidates})
    controller = TokenBudgetController(budget)
    if toc or intent["kind"] == "navigation":
        # 渐进式披露的第一层：只给摘要地图，让 agent 用几百令牌决定读哪个 Parent
        l1 = summaries(con, doc_ids, "l1")
        l2 = rank_parents(query, summaries(con, doc_ids, "l2"), candidates)[:8]
        payload = {
            "query": query, "mode": "toc",
            "intent": {"kind": intent["kind"], "weights": intent["weights"]},
            "documents": l1,
            "parents": l2,
            "budget": {"max_context": controller.MAX_CONTEXT_TOKENS,
                       "reserved": controller.RESERVED_FOR_RESPONSE,
                       "limit": controller.budget,
                       "used": sum(r["token_count"] for r in l1) + sum(r["token_count"] for r in l2),
                       "headroom": 0},
            "injected": [], "ranked": [],
            "elapsed_ms": round((time.time() - started) * 1000, 1),
            "cache": "skip",
        }
        con.close()
        return payload

    # 渐进式披露：首轮只给 1 个 Parent，之后每轮追加 2 个（最多 3 轮）
    take = min(1 + 2 * (rounds - 1), len(candidates))
    injected, used = controller.select(candidates[:take])

    # 滑动窗口：命中段落末尾出现「接下来/下一节」时追加 1 个同级 Child（最多 1 次）
    window = []
    for row in injected:
        if not NEXT_RE.search(row["content"][-120:]):
            continue
        nxt = sibling_after(registry, row)
        if nxt is None or any(other["chunk_id"] == nxt["chunk_id"] for other in injected):
            continue
        if used + nxt["token_count"] <= controller.budget:
            injected.append(nxt)
            used += nxt["token_count"]
            window.append(nxt["chunk_id"])
        break

    payload = {
        "query": query,
        "mode": "chunks",
        "subqueries": subqueries,
        "intent": {"kind": intent["kind"], "weights": intent["weights"]},
        "prefilter": {"domain": domain, "subdomain": subdomain, "level": level,
                      "tags": tags,
                      "candidates": len(allow) if allow is not None else "all"},
        "penalties": penalties,
        "window": window,
        "budget": {"max_context": controller.MAX_CONTEXT_TOKENS,
                   "reserved": controller.RESERVED_FOR_RESPONSE,
                   "limit": controller.budget, "used": used,
                   "headroom": controller.budget - used},
        "injected": [
            {"chunk_id": row["chunk_id"], "kind": row["kind"],
             "heading_path": row["heading_path"], "token_count": row["token_count"],
             "content": row["content"] if explain else None}
            for row in injected
        ],
        "ranked": [
            {"chunk_id": row["child"]["chunk_id"],
             "heading_path": row["child"]["heading_path"],
             "rrf": round(row["rrf"], 5), "rerank": round(row["rerank"], 3),
             "penalty": row["penalty"], "score": round(row["score"], 4),
             "bm25_rank": row["bm25_rank"], "graph_hit": row["graph_hit"],
             "parent_tokens": row["parent"]["token_count"] if row["parent"] else None}
            for row in candidates[:8]
        ],
        "elapsed_ms": round((time.time() - started) * 1000, 1),
        "cache": "miss",
    }
    if not explain:
        cache_put(con, key, payload)
    con.close()
    return payload


def fetch_parent(parent_id: str, budget: int | None) -> dict:
    """按 Parent id 精确取 L3 正文：配合 toc 地图完成第二、三轮披露。"""
    if not kb.DB_PATH.is_file():
        raise SystemExit("FAIL  retriever  索引不存在，先运行 python .agents/skills/maintaining-python/scripts/indexer.py")
    registry = kb.read_json(kb.REGISTRY_PATH, {"documents": {}, "chunks": {}})
    chunk = registry["chunks"].get(parent_id)
    if not chunk:
        raise SystemExit("FAIL  retriever  没有这个 Parent: " + parent_id
                         + "；先用 --toc 看可用的 ref_id")
    if chunk["kind"] != "parent":
        raise SystemExit("FAIL  retriever  " + parent_id + " 不是 Parent（--toc 的 ref_id 才是）")
    controller = TokenBudgetController(budget)
    if chunk["token_count"] > controller.budget:
        raise SystemExit("FAIL  retriever  Parent " + str(chunk["token_count"])
                         + " 令牌超过预算 " + str(controller.budget))
    return {
        "chunk_id": chunk["chunk_id"], "heading_path": chunk["heading_path"],
        "token_count": chunk["token_count"], "doc_id": chunk["doc_id"],
        "content": chunk["content"],
    }


def main() -> int:
    kb.configure_stdout()
    parser = argparse.ArgumentParser(description="知识库检索管道")
    parser.add_argument("query", nargs="?", help="自然语言查询（用 --parent 取正文时可省略）")
    parser.add_argument("--domain", default="", help="按领域预过滤，如 cpp_core")
    parser.add_argument("--subdomain", default="", help="按子领域预过滤，如 memory")
    parser.add_argument("--level", type=int, default=None, help="按 level_range 预过滤")
    parser.add_argument("--tag", action="append", default=[], help="按标签过滤，可重复")
    parser.add_argument("--budget", type=int, default=None, help="注入令牌上限，默认 4000")
    parser.add_argument("--rounds", type=int, default=1, help="渐进式披露轮数（1-3）")
    parser.add_argument("--toc", action="store_true",
                        help="只输出 L1/L2 摘要地图（渐进式披露第一层，几百令牌）")
    parser.add_argument("--parent", default="", help="按 Parent id 直接取 L3 正文")
    parser.add_argument("--explain", action="store_true", help="输出命中 Chunk 正文")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    args = parser.parse_args()

    if args.parent:
        row = fetch_parent(args.parent, args.budget)
        if args.json:
            print(json.dumps(row, ensure_ascii=False, indent=1))
        else:
            print("----- " + row["heading_path"] + "  [parent, "
                  + str(row["token_count"]) + " 令牌] -----")
            print(row["content"])
        return 0
    if not args.query:
        parser.error("需要查询词，或者改用 --parent <id> / --toc")

    result = retrieve(args.query, args.domain, args.subdomain, args.level, args.tag,
                      args.budget, min(max(args.rounds, 1), 3), args.explain, args.toc)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        if result.get("mode") == "toc":
            return 0 if result["documents"] or result["parents"] else 2
        return 0 if result["injected"] else 2

    if result.get("mode") == "toc":
        print("查询 " + result["query"] + "  模式=摘要地图  摘要令牌="
              + str(result["budget"]["used"])
              + "  耗时=" + str(result["elapsed_ms"]) + "ms")
        for row in result["documents"]:
            print("  L1 " + str(row["token_count"]).rjust(4) + "  " + row["text"])
        for row in result["parents"]:
            print("  L2 " + str(row["token_count"]).rjust(4) + "  [" + row["ref_id"] + "] "
                  + row["text"][:120])
        print("      取正文：python .agents/skills/maintaining-python/scripts/retriever.py --parent <ref_id>")
        return 0

    print("查询 " + result["query"] + "  意图=" + result["intent"]["kind"]
          + "  子查询=" + str(len(result["subqueries"]))
          + "  候选=" + str(result["prefilter"]["candidates"])
          + "  注入令牌=" + str(result["budget"]["used"]) + "/" + str(result["budget"]["limit"])
          + "  缓存=" + str(result.get("cache"))
          + ("  降权文档=" + ",".join(result["penalties"]) if result.get("penalties") else "")
          + ("  窗口追加=" + str(len(result["window"])) if result.get("window") else "")
          + "  耗时=" + str(result["elapsed_ms"]) + "ms")
    if not result["injected"]:
        print("FAIL  retriever  无命中；检查 --domain/--level 是否过滤过窄，或先跑 indexer")
        return 2
    if args.explain:
        for row in result["injected"]:
            print(chr(10) + "----- " + row["heading_path"] + "  [" + row["kind"] + ", "
                  + str(row["token_count"]) + " 令牌] -----")
            print(row["content"])
        return 0
    for position, row in enumerate(result["ranked"], start=1):
        print("  " + str(position) + ". " + row["heading_path"]
              + "  rrf=" + str(row["rrf"]) + " rerank=" + str(row["rerank"])
              + " penalty=" + str(row["penalty"])
              + " bm25#" + str(row["bm25_rank"])
              + (" graph" if row["graph_hit"] else "")
              + "  Parent=" + str(row["parent_tokens"]) + "令牌")
    return 0


if __name__ == "__main__":
    sys.exit(main())
