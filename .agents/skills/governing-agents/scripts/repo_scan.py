#!/usr/bin/env python3
"""仓库扫描共用的目录跳过清单。

`check_docs.py` 与 `check_encoding.py` 都遍历仓库文本，跳过同一批生成物与缓存
目录；清单一处维护，避免两处漂移。各脚本仍可按自己的范围传 extra 追加目录。
"""

# 生成物、缓存与临时产物不入上下文（读取边界见 AGENTS.md）。
SKIP_DIRS = {
    ".git", "_book", ".quarto", "build", "node_modules",
    ".cache", ".tmp", "temp", "__pycache__",
}


def is_skipped(path, extra=()):
    """路径的任一段落在跳过清单或 extra 里时返回 True。"""
    names = SKIP_DIRS | set(extra)
    return any(part in names for part in path.parts)
