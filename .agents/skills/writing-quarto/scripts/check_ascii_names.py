#!/usr/bin/env python3
"""校验仓库内所有路径名（目录/文件名）是否为纯 ASCII。

目的：防止 U+2011（non-breaking hyphen）、全角、U+2212（减号）等特殊字符
触发 Quarto 渲染 `recoverEncode: invalid argument` 错误。
规范出处：.agents/skills/writing-cpp/references/cpp/cpp.md（命名规范）。

用法：python check_ascii_names.py
退出码：0 = 全部纯 ASCII，1 = 发现非法字符。
"""

import os
import sys
from pathlib import Path

# 需要排除的目录（生成产物 / 依赖 / VCS）
# 生成产物 / 依赖 / VCS / CMake 构建目录（build/ 非源码，不属校验对象）
EXCLUDE_DIRS = {"node_modules", "_book", ".quarto", ".git", "_site", "build"}


def first_non_ascii(name):
    """返回名称中第一个码点 > 127 的字符。无则返回 None。"""
    for ch in name:
        if ord(ch) > 127:
            return ch
    return None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    repo_root = str(Path(__file__).resolve().parents[4])
    print(f"扫描：{repo_root}")
    print(f"排除目录：{', '.join(sorted(EXCLUDE_DIRS))}")
    print()

    bad = []
    count = 0
    for dirpath, dirnames, filenames in os.walk(repo_root):
        # 原地剪枝：不进入排除目录
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in dirnames + filenames:
            count += 1
            ch = first_non_ascii(name)
            if ch is not None:
                bad.append(("U+{:04X}".format(ord(ch)), os.path.join(dirpath, name)))

    print(f"共检查 {count} 个路径项。")
    print()

    if not bad:
        print("OK：所有路径均为纯 ASCII，无特殊连字符风险。")
        return 0

    print(f"发现 {len(bad)} 个含非 ASCII 字符的路径：")
    for code, path in bad:
        print(f"  [{code}] {path}")
    print()
    print('建议：将非 ASCII 字符（尤其 U+2011 连字符）改为普通 "-"（U+002D）。')
    return 1


if __name__ == "__main__":
    sys.exit(main())
