#!/usr/bin/env python3
"""校验渲染产物中的 callout 是否真的渲染成提示框（防自定义类静默退化）。

Quarto 只认内置 5 类 callout（note/tip/warning/important/caution）。未知的
.callout-<name> 类会被静默丢弃，callout 退化成带 <h2> 的 <section>，既没有
提示框样式，又混进右侧目录。本脚本扫描 _book/**/*.html 抓这一回归。

用法：python check_callouts.py [--book-dir _book]
退出码：0 = 全部正常，1 = 发现退化的 callout。
"""

import argparse
import re
import sys
from pathlib import Path

# Quarto 内置 callout 类型（唯一的合法集合，none 用于无类型 callout）
BUILTIN_TYPES = {"none", "note", "tip", "warning", "important", "caution"}

# <section ... class="level2 callout-xxx"> => callout 退化成了普通小节
DEGRADED_RE = re.compile(r'<section[^>]*class="[^"]*\bcallout-[a-z0-9-]+\b[^"]*"')

# callout 外层容器的开头标签：必带 callout-style-*（内层的 callout-body / callout-header
# 等结构 div 没有该类，据此把它们排除，避免误判为「非内置类型」）
CALLOUT_DIV_RE = re.compile(r'<div[^>]*class="[^"]*\bcallout-style-[a-z]+[^"]*"[^>]*>')
CLASS_RE = re.compile(r'class="([^"]*)"')

# 外层容器上的结构性类（不是 callout 类型）
STRUCTURAL_CLASSES = {"callout", "callout-titled", "callout-empty-content", "no-icon"}


def check_file(path):
    """返回 (退化小节数, 非内置类型集合, 缺标题容器数)。"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    degraded = len(DEGRADED_RE.findall(text))

    unknown = set()
    missing_title = 0
    matches = list(CALLOUT_DIV_RE.finditer(text))
    for idx, m in enumerate(matches):
        classes = CLASS_RE.search(m.group(0)).group(1).split()
        for c in classes:
            if c in STRUCTURAL_CLASSES or c.startswith("callout-style-"):
                continue
            if c.startswith("callout-") and c[len("callout-") :] not in BUILTIN_TYPES:
                unknown.add(c[len("callout-") :])
        # 标题容器应紧随本 div 出现。用下一个 callout div 的起点作为窗口边界
        if "callout-titled" in classes:
            stop = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            window = text[m.start() : min(stop, m.start() + 3000)]
            if "callout-title-container" not in window:
                missing_title += 1
    return degraded, unknown, missing_title


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-dir", default="_book", help="渲染产物目录（默认 _book）")
    args = parser.parse_args()

    book_dir = Path(args.book_dir)
    if not book_dir.is_dir():
        print(f"未找到渲染产物目录：{book_dir}；请先执行 quarto render。")
        return 1

    html_files = sorted(book_dir.rglob("*.html"))
    bad_pages = 0
    for path in html_files:
        degraded, unknown, missing_title = check_file(path)
        if not (degraded or unknown or missing_title):
            continue
        bad_pages += 1
        rel = path.relative_to(book_dir)
        print(f"  FAIL {rel}")
        if degraded:
            print(f"       {degraded} 处 callout 退化为 <section>（未渲染成提示框）")
        if unknown:
            print(f"       非内置 callout 类型：{sorted(unknown)}")
        if missing_title:
            print(f"       {missing_title} 个带标题 callout 缺少 callout-title-container")

    print()
    if bad_pages:
        print(f"{bad_pages} 个页面存在 callout 问题。")
        print('修复：改用内置 5 类，并用 `title="中文标题"` 提供标题（见 quarto/rendering-and-output.md #12）。')
        return 1
    print(f"OK：{len(html_files)} 个页面的 callout 均正常渲染。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
