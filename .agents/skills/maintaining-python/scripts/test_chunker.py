#!/usr/bin/env python3
"""分块形态回归：纯自锚点链接列表不得单独成块（锚点目录占位的闸）。

为什么需要这份断言：`## 目录` 的正文就是后面各节的标题列表，改写查询里的词
在目录里出现一次即可拿满精排覆盖率，又比真正作答的那一节短，检索时会占住
候选位。规则按形态判断（整块只含 `- [x](#y)` 列表），不写死标题「目录」。
本测试用临时 Markdown 直接跑 split_doc，不依赖 index_data/，也不写任何产物。

用法：python .agents/skills/maintaining-python/scripts/test_chunker.py
退出码：0 = 断言全过，非 0 = 形态规则又断了（AssertionError 直接给现场）。
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chunker  # noqa: E402

FRONT = (
    "---\n"
    'kb_id: "bg-chunker-selftest-v1"\n'
    'title: "分块自测"\n'
    'domain: "tooling"\n'
    'updated: "2026-10-11"\n'
    "---\n\n"
    "# 分块自测\n\n"
)


def split_body(body: str):
    handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    path = Path(handle.name)
    try:
        handle.write(FRONT + body)
        handle.close()
        return chunker.split_doc(path)
    finally:
        path.unlink(missing_ok=True)


# 纯自锚点链接列表的整节：不产出 Parent/Child，正文章节照常入库
_docs, chunks = split_body(
    "这是概述段，让引言区有正文。\n\n"
    "## 目录\n\n"
    "- [六段块序列](#六段块序列)\n"
    "- [标题分层](#标题分层)\n"
    "- [反例与改写](#反例与改写)\n\n"
    "## 六段块序列\n\n"
    "正文段，讲六段块序列怎么排。\n"
)
parents = [c["heading_path"] for c in chunks if c["kind"] == "parent"]
assert not any("目录" in path for path in parents + [c["heading_path"] for c in chunks if c["kind"] == "child"]), parents
assert any("六段块序列" in path for path in parents), parents

# 列表混入散文行（或锚点列表外还有正文）：照常入库，不误删
_docs, chunks = split_body(
    "## 目录\n\n"
    "各节按阅读顺序排列：\n\n"
    "- [六段块序列](#六段块序列)\n\n"
    "## 六段块序列\n\n"
    "正文段。\n"
)
assert any(c["kind"] == "parent" and "目录" in c["heading_path"] for c in chunks), \
    [c["heading_path"] for c in chunks]

# 外部链接与相对路径链接不是自锚点：参考节照常入库
_docs, chunks = split_body(
    "## 参考\n\n"
    "- [上游仓库](https://github.com/lxgw/LxgwBright)\n"
    "- [同目录笔记](notes.md)\n\n"
    "## 主体\n\n"
    "正文段。\n"
)
assert any(c["kind"] == "parent" and "参考" in c["heading_path"] for c in chunks), \
    [c["heading_path"] for c in chunks]

print("PASS  分块形态回归  纯自锚点目录不成块，混排正文与外部链接不误删")
