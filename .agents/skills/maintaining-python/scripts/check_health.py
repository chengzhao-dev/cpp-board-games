#!/usr/bin/env python3
"""知识库健康度体检：格式合规、索引一致性、重复与断链、检索延迟。

只做「能断言的事」，每条都能对应到修法，不做主观评价：

| 指标 | 阈值 | 超标含义 |
| 格式违规 | 0 | Frontmatter 缺字段 / 无 ## 段落，文件根本没进索引 |
| 未索引文档 | 0 | knowledge 下有文件但注册表里没有，通常是上表违规连带 |
| 孤立 Chunk | 0 | Child 找不到 Parent，Stage 5 回溯会静默降级 |
| 重复 Chunk | 0 | 同一 hash 出现多次，检索结果互相挤占预算 |
| 图谱断链 | 0 | 概念节点的 chunk_id 指向不存在的 Chunk |
| Parent 超限 | 0 | 任一可检索 Parent 超过默认 4000 Token 预算 |
| 检索 P95 | <= 200ms | 评测集上端到端延迟，超标即验收不通过 |
| 陈旧条目 | 0 | 源码 hash 变了但索引还是旧的，说明增量没跑 |

用法：
    python .agents/skills/maintaining-python/scripts/check_health.py            # 体检（有告警时退出码 1）
    python .agents/skills/maintaining-python/scripts/check_health.py --gate     # 给 run.py check 用：只在 FAIL 时非 0
    python .agents/skills/maintaining-python/scripts/check_health.py --verbose   # 打印每条超阈值项的具体位置
退出码：0 = 全部达标（或 --gate 下无 FAIL），1 = 有 WARN/FAIL。
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kb  # noqa: E402

LIMITS = {
    "format": 0, "unindexed": 0, "orphan": 0, "duplicate": 0,
    "graph_broken": 0, "oversized_parent": 0, "stale": 0, "p95_ms": 200.0,
    "dangling": 0,
}
ROOT_PATH = kb.ROOT


def check_format() -> tuple[list[str], list[str]]:
    """直接对磁盘上的文件做规范校验，不依赖索引是否新鲜。"""
    problems = []
    paths = set()
    for path in kb.list_knowledge_files():
        paths.add(kb.rel(path))
        try:
            meta, body = kb.frontmatter(path.read_text(encoding="utf-8"))
        except (ValueError, OSError, UnicodeDecodeError) as exc:
            problems.append(kb.rel(path) + ": " + str(exc))
            continue
        missing = [name for name in kb.REQUIRED_FIELDS if not meta.get(name)]
        if missing:
            problems.append(kb.rel(path) + ": 缺字段 " + ", ".join(missing))
            continue
        if not [row for row in kb.headings(body) if row[1] == 2]:
            problems.append(kb.rel(path) + ": 没有 ## 段落，无法建立两层结构")
        h1 = [row for row in kb.headings(body) if row[1] == 1]
        if len(h1) != 1:
            problems.append(kb.rel(path) + ": H1 标题数量应为 1，实测 " + str(len(h1)))
    return problems, sorted(paths)


def check_index(paths: list[str], registry_out: list) -> tuple[dict, list[str]]:
    """比对注册表与 SQLite，找出未索引、陈旧、孤立和重复。"""
    details: list[str] = []
    registry = kb.read_json(kb.REGISTRY_PATH, {"documents": {}, "chunks": {}})
    registry_out.append(registry)
    docs = registry.get("documents", {})
    chunks = registry.get("chunks", {})
    counts = {
        "unindexed": 0, "stale": 0, "orphan": 0, "duplicate": 0,
        "graph_broken": 0, "oversized_parent": 0,
    }

    indexed_paths = {row["path"] for row in docs.values()}
    for path in paths:
        if path not in indexed_paths:
            counts["unindexed"] += 1
            details.append("未索引: " + path)

    if not kb.DB_PATH.is_file():
        counts["stale"] = len(paths)
        details.append("索引文件缺失: " + kb.rel(kb.DB_PATH))
        return counts, details

    con = sqlite3.connect(kb.DB_PATH)
    db_rows = {
        row[0]: row for row in con.execute(
            "SELECT chunk_id, content_hash, token_count, kind, parent_id, status FROM chunks"
        )
    }
    for chunk_id, chunk in chunks.items():
        row = db_rows.get(chunk_id)
        if row is None:
            counts["stale"] += 1
            details.append("索引缺 Chunk: " + chunk_id)
        elif row[1] != chunk["content_hash"]:
            counts["stale"] += 1
            details.append("内容已变更但索引未更新: " + chunk_id)
    for row in con.execute("SELECT count(*) FROM chunks WHERE status='live'").fetchone():
        live = row

    # 源码与注册表比对：文件改了但没重跑 chunker
    for doc_id, doc in docs.items():
        path = ROOT_PATH / doc["path"]
        if path.is_file() and kb.content_hash(path.read_text(encoding="utf-8")) != doc["source_hash"]:
            counts["stale"] += 1
            details.append("源文件已改但注册表是旧的: " + doc["path"])

    for chunk_id, chunk in chunks.items():
        if chunk["kind"] == "child" and chunk.get("parent_id") not in chunks:
            counts["orphan"] += 1
            details.append("孤立 Child（Parent 不存在）: " + chunk_id)
    hashes = Counter(c["content_hash"] for c in chunks.values() if c["kind"] == "child")
    for digest, times in hashes.items():
        if times > 1:
            counts["duplicate"] += times - 1
            details.append("重复内容 " + str(times) + " 次: " + digest[:19])

    known = set(chunks)
    for name, chunk_ids in con.execute("SELECT name, chunk_ids FROM concept"):
        broken = [c for c in chunk_ids.split(",") if c and c not in known]
        if broken:
            counts["graph_broken"] += 1
            details.append("概念 " + name + " 挂空 " + str(len(broken)) + " 处")
    oversized = list(con.execute(
        "SELECT chunk_id, heading_path, token_count FROM chunks "
        "WHERE kind='parent' AND status='live' AND token_count>? "
        "ORDER BY token_count DESC",
        (kb.AVAILABLE_FOR_RETRIEVAL,),
    ))
    counts["oversized_parent"] = len(oversized)
    for chunk_id, heading_path, token_count in oversized:
        details.append(
            "Parent 超过默认预算: " + chunk_id + " " + str(token_count)
            + " Token > " + str(kb.AVAILABLE_FOR_RETRIEVAL)
            + "（" + heading_path + "）"
        )
    con.close()
    counts["live"] = live
    return counts, details


def check_version(registry: dict, con) -> tuple[list[str], int]:
    """检查 supersedes 是否指向存在的文档，并数出冲突候选。

    悬空的 supersedes 是真实的腐化信号：目标文档改名或删掉之后，旧版永远拿不到
    降权，检索会把两版并列返回。这项断言廉价且可修（改 frontmatter 或删字段）。

    冲突候选不是错误：设计上只做“两份文档覆盖同批概念且 updated 更新晚于对方”的
    事实陈述，要不要处理由人判断。它一旦算进失败项，知识库就没法长出第二份文档
    ——每加一份都必然制造若干候选，体检会永久变红。所以这里单独返回计数。
    """
    problems = []
    for doc in registry.get("documents", {}).values():
        target = str(doc.get("supersedes") or "")
        if target and target not in registry.get("documents", {}):
            problems.append("悬空 supersedes: " + doc["doc_id"] + " -> " + target)
    conflicts = con.execute("SELECT count(*) FROM conflict").fetchone()[0]
    return problems, conflicts



def measure_latency(samples: int) -> tuple[float, float]:
    """端到端测 P50/P95（含预算裁剪与图谱查询），不是只测 SQL。"""
    from retriever import retrieve
    # 探针必须是当前知识库里真实存在依据的查询：拿已迁走的 C++ 语言条目测延迟，
    # 量到的只是空结果集，既掩盖真实冷路径成本，也不覆盖任何现存领域。
    queries = [
        # 工具链
        "最小构建链为什么要固定编译器版本", "版本要求为什么只写在构建配置里",
        "编译与诊断开关为什么默认全开",
        # Quarto 渲染与输出
        "Quarto 渲染配置为什么会静默失效", "Quarto HTML 输出选项在哪些作用域生效",
        "提示框与包含文件为什么渲染不出来",
        # 页面块序列
        "教学正文的块序列为什么固定为六段", "一个二级标题对应一个可验证任务",
        "常见错误、自测与回顾如何分工", "元素选择的判定依据是什么",
        # 页面几何与信息密度
        "正文三栏为什么被压缩", "段落和盒子的比例为什么要设阈值",
        "命令和输出为什么要分块", "代码块为什么不能做成框中框",
        # 入口页与写作案例
        "入口页的卡片可以放命令吗", "README 和站点首页怎么分工",
        "Windows 与 WSL2 环境的命令怎么展示",
        # Pages 部署与仓库卫生
        "GitHub Pages 部署源怎么选", "站点路径与首次启用要注意什么",
        "为什么忽略规则要集中", "行尾与编码为什么要归一化",
        # 宿主契约
        "上下文压缩由谁触发",
    ][:samples]
    # 24h 查询缓存会让重复查询只走 dict 查找，测出来的 P95 是假的。
    # 每次测量前清空缓存，量的是真正的端到端冷路径。
    if kb.DB_PATH.is_file():
        probe = sqlite3.connect(kb.DB_PATH)
        probe.execute("DELETE FROM query_cache")
        probe.commit()
        probe.close()
    times = []
    for query in queries:
        started = time.time()
        retrieve(query)
        times.append((time.time() - started) * 1000)
    if not times:
        return 0.0, 0.0
    times.sort()
    p50 = times[len(times) // 2]
    p95 = times[max(0, int(round(len(times) * 0.95)) - 1)]
    return p50, p95


def run(gate: bool, verbose: bool, samples: int) -> int:
    started = time.time()
    problems, paths = check_format()
    holder: list = []
    counts, details = check_index(paths, holder)
    counts["format"] = len(problems)
    p50, p95 = (measure_latency(samples) if paths else (0.0, 0.0))
    counts["p95_ms"] = p95

    order = ["format", "unindexed", "stale", "orphan", "duplicate", "graph_broken",
             "oversized_parent", "dangling"]
    version_problems, conflicts = ([], 0)
    if holder and kb.DB_PATH.is_file():
        probe = sqlite3.connect(kb.DB_PATH)
        version_problems, conflicts = check_version(holder[0], probe)
        probe.close()
    counts["dangling"] = len(version_problems)
    problems = problems + version_problems
    degraded = p95 > LIMITS["p95_ms"]
    failed = [k for k in order if counts[k] > LIMITS[k]]
    if degraded and not gate:
        failed.append("p95_ms")            # gate 模式只把结构性问题当失败，延迟降级为告警

    live = counts.get("live", 0)
    status = "PASS" if not failed else "FAIL"
    print(status + "  kb-health  文件=" + str(len(paths))
          + "  Chunk(live)=" + str(live)
          + "  格式违规=" + str(counts["format"])
          + "  未索引=" + str(counts["unindexed"])
          + "  陈旧=" + str(counts["stale"])
          + "  孤立=" + str(counts["orphan"])
          + "  重复=" + str(counts["duplicate"])
          + "  图谱断链=" + str(counts["graph_broken"])
          + "  Parent超限=" + str(counts["oversized_parent"])
          + "  悬空supersedes=" + str(counts["dangling"])
          + "  冲突候选=" + str(conflicts)
          + "  P50=" + format(p50, ".1f") + "ms P95=" + format(p95, ".1f") + "ms")
    if failed:
        print("      超阈值项: " + ", ".join(failed))
    if conflicts:
        print("      提示：冲突候选 " + str(conflicts)
              + " 处待人工确认（方向按 updated，含共享概念名）；确认后在新版写 supersedes，不视为失败")
    if verbose:
        for row in problems:
            print("      [格式/目录] " + row)
        for row in details[:20]:
            print("      [索引] " + row)
        print("      体检耗时 " + format(time.time() - started, ".2f") + "s")
    return 1 if failed else 0


def main() -> int:
    kb.configure_stdout()
    parser = argparse.ArgumentParser(description="知识库健康度体检")
    parser.add_argument("--gate", action="store_true", help="只把结构性问题视为失败（供 run.py check 调用）")
    parser.add_argument("--verbose", action="store_true", help="打印超阈值项的具体位置")
    parser.add_argument("--samples", type=int, default=20, help="延迟测量用的查询条数")
    args = parser.parse_args()
    return run(args.gate, args.verbose, args.samples)


if __name__ == "__main__":
    sys.exit(main())
