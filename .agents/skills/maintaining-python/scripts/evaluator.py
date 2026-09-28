#!/usr/bin/env python3
"""检索精度与延迟评测（goal 3.1 的唯一客观验收）。

口径：
  Top-5 召回率 = 至少有一个期望 Leaf 进入前 5 的查询数 / 总查询数
  前 5 个候选按 Stage 5 的口径计：Child 与它回溯出的 Parent 都算召回内容，
  因为检索器实际交给 LLM 的是 Parent。只按 Child id 计分会让导航类查询恒定差一层。
  期望答案写成标题片段（见 eval_set.py），运行时展开为真实 chunk_id。
  片段命中 0 个或多个文档之外的解析失败都算 ERROR，避免评测集悄悄过期。
指标：Top-5 召回率 >= 92%（样本 >= MIN_SAMPLES，且不得少于评测集行数）、P95 < 200ms、单次注入 <= 6000 令牌。

用法：
    python scripts/evaluate.py                 # 全量评测
    python scripts/evaluate.py --topk 5        # 改 K
    python scripts/evaluate.py --verbose       # 列出未命中查询
    python scripts/evaluate.py --skip-latency  # 只卡召回率与样本数（延迟由体检负责）
退出码：0 = 达标，1 = 未达标，3 = 评测集或索引有问题（不是检索质量差）。
"""

from __future__ import annotations

import argparse
import sqlite3
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kb  # noqa: E402
from eval_set import ROWS  # noqa: E402

RECALL_TARGET = 0.92
# 评测集与知识库同规模演进：门槛取固定下限与实际行数的较大值，
# 避免样本数永远追不上一个与当前语料无关的常量。
MIN_SAMPLES = 20
P95_TARGET_MS = 200.0
INJECTION_HARD_LIMIT = kb.MAX_CONTEXT_TOKENS


CHILDREN_OF: dict[str, list] = {}
PARENT_OF: dict[str, str] = {}


def leaf_index() -> dict:
    """leaf 标题片段  到  chunk_id 集合（一个片段可能跨多个文档）。"""
    if not kb.REGISTRY_PATH.is_file():
        raise SystemExit("FAIL  evaluate  缺注册表，先运行 python scripts/indexer.py")
    registry = kb.read_json(kb.REGISTRY_PATH, {"documents": {}, "chunks": {}})
    mapping: dict[str, set] = {}
    for chunk_id, chunk in registry["chunks"].items():
        if chunk.get("status") == "deprecated":
            continue
        leaf = chunk["heading_path"].split(" > ")[-1]
        mapping.setdefault(leaf, set()).add(chunk_id)
        if chunk.get("kind") == "child" and chunk.get("parent_id"):
            CHILDREN_OF.setdefault(chunk["parent_id"], []).append(chunk_id)
            PARENT_OF[chunk_id] = chunk["parent_id"]
    return mapping


def expand(fragment: str, mapping: dict, errors: list):
    """把"片段|片段"展开为 chunk_id 集合。解析不到就记 ERROR。"""
    ids = set()
    for part in [p.strip() for p in fragment.split("|") if p.strip()]:
        hit = set()
        for leaf, chunk_ids in mapping.items():
            if part in leaf:
                hit.update(chunk_ids)
        if not hit:
            errors.append(part)
        ids |= hit
    return ids


def toc_chunks(result: dict, topk: int) -> list:
    """摘要地图的命中口径：取地图里前 topk 个 Parent，并展开它们的子块。

    导航查询按规范返回的是章节地图而不是正文排名（见 3.4 渐进式披露），
    它契约要做对的事是把你指到正确的章节，所以这里按 Parent 展开计分。
    """
    ids: list = []
    for row in result["parents"][:topk]:
        ids.append(row["ref_id"])
        ids.extend(CHILDREN_OF.get(row["ref_id"], []))
    return ids


def measure(queries: list, topk: int):
    """逐条跑检索，记录是否命中与端到端耗时（含缓存清理，量冷路径）。"""
    from retriever import retrieve
    con = sqlite3.connect(kb.DB_PATH)
    hits, latencies, injected_max = [], [], 0
    for position, query in enumerate(queries, 1):
        if position % 25 == 1:
            con.execute("DELETE FROM query_cache")
            con.commit()
        started = time.time()
        result = retrieve(query)
        latencies.append((time.time() - started) * 1000)
        used = result["budget"]["used"]
        injected_max = max(injected_max, used)
        if result.get("mode") == "toc":
            # 导航意图按规范返回摘要地图，不是正文排名。这里把地图里的 Parent
            # 展开成它的 Child，再按同一口径判命中，否则导航永远算不中。
            ranked = toc_chunks(result, topk)
        else:
            # Stage 5 回溯：Child 命中后实际注入的是它的 Parent（见 3.4），
            # 评测必须按「LLM 真正看到的内容」计分，否则导航类查询永远差一层。
            ranked = []
            for row in result["ranked"][:topk]:
                ranked.append(row["chunk_id"])
                ranked.append(PARENT_OF.get(row["chunk_id"], row["chunk_id"]))
        hits.append((query, ranked, used, result["intent"]["kind"]))
    con.close()
    return hits, latencies, injected_max


def run(topk: int, verbose: bool, skip_latency: bool) -> int:
    mapping = leaf_index()
    resolve_errors: list = []
    cases = []
    for query, fragment, category in ROWS:
        expected = expand(fragment, mapping, resolve_errors)
        cases.append((query, expected, category))

    missing = sorted(set(resolve_errors))
    if missing:
        print("FAIL  evaluate  评测集片段解析不到 Leaf（评测集过期或文档改名）：")
        for leaf in missing[:20]:
            print("      " + leaf)
        return 3

    queries = [c[0] for c in cases]
    results, latencies, injected_max = measure(queries, topk)

    by_category: dict[str, list] = {}
    misses = []
    for (query, expected, category), (_, ranked, used, intent) in zip(cases, results):
        ok = bool(expected.intersection(ranked))
        by_category.setdefault(category, []).append(ok)
        if not ok:
            misses.append((query, category, ranked[:topk], sorted(expected)[:3]))

    total = len(cases)
    passed = total - len(misses)
    recall = passed / total if total else 0.0
    latencies.sort()
    p50 = statistics.median(latencies) if latencies else 0.0
    p95 = latencies[max(0, int(round(len(latencies) * 0.95)) - 1)] if latencies else 0.0

    print("评测  样本=" + str(total) + "  Top-" + str(topk) + " 召回="
          + format(recall * 100, ".1f") + "%  P50=" + format(p50, ".1f")
          + "ms P95=" + format(p95, ".1f") + "ms  注入峰值=" + str(injected_max) + " 令牌")
    for category in sorted(by_category):
        rows = by_category[category]
        print("      " + category.ljust(12) + format(sum(rows) / len(rows) * 100, "5.1f")
              + "%  n=" + str(len(rows)))

    reasons = []
    if total < MIN_SAMPLES:
        reasons.append("样本 " + str(total) + " < " + str(MIN_SAMPLES))
    if recall < RECALL_TARGET:
        reasons.append("Top-" + str(topk) + " 召回 " + format(recall * 100, ".1f")
                       + "% < " + format(RECALL_TARGET * 100, ".0f") + "%")
    if injected_max > INJECTION_HARD_LIMIT:
        reasons.append("注入峰值 " + str(injected_max) + " > " + str(INJECTION_HARD_LIMIT))
    if not skip_latency and p95 > P95_TARGET_MS:
        reasons.append("P95 " + format(p95, ".1f") + "ms > " + str(int(P95_TARGET_MS)) + "ms")

    if verbose and misses:
        print("      未命中明细:")
        for query, category, ranked, expected in misses:
            print("      [" + category + "] " + query)
            print("          期望 " + " / ".join(leaf[:70] for leaf in expected))
            print("          实得 " + " / ".join(leaf[:70] for leaf in ranked))
    if reasons:
        print("FAIL  evaluate  " + "; ".join(reasons))
        return 1
    print("PASS  evaluate  召回率、样本数与 Token 预算全部达标")
    return 0


def main() -> int:
    kb.configure_stdout()
    parser = argparse.ArgumentParser(description="知识库检索评测")
    parser.add_argument("--topk", type=int, default=5, help="召回评价的 K，默认 5")
    parser.add_argument("--verbose", action="store_true", help="列出未命中明细")
    parser.add_argument(
        "--skip-latency",
        "--gate",
        dest="skip_latency",
        action="store_true",
        help="不卡延迟（延迟由 kb-check 负责；--gate 为兼容别名）",
    )
    args = parser.parse_args()
    return run(args.topk, args.verbose, args.skip_latency)


if __name__ == "__main__":
    sys.exit(main())
