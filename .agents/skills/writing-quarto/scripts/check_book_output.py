#!/usr/bin/env python3
"""渲染产物的发布前 smoke 检查：首页存在、编码干净、charset 正确、站点 URL 生效。

为什么需要它：渲染成功不等于线上可读。历史事故里 quarto render 全绿，但线上
404 或乱码，问题出在 site-url 缺失、Pages 源未配置或产物编码被破坏。本检查在
渲染后、发布前运行，把这类失败拦在 CI，不替代 run.py check 的其余产物检查。

用法：python check_book_output.py [--book-dir _book]
退出码：0 = 通过；1 = 存在阻塞问题。
"""

import argparse
import sys
from pathlib import Path

# 与 check_encoding.py 共用同一组乱码特征，命中任意一个即判为编码破坏。
# 用 \u 转义存放，避免本文件被 check_encoding.py 误判为含乱码
MOJIBAKE_MARKERS = (
    "\u951f", "\u93c2", "\u941c", "\u7ed4", "\u93b4",
    "\u7487", "\u6d60", "\u934f", "\u7039", "\u95b8",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="检查渲染产物可发布性")
    parser.add_argument("--book-dir", default="_book", help="渲染产物目录")
    args = parser.parse_args()
    book = Path(args.book_dir)
    problems = []

    index = book / "index.html"
    if not index.is_file():
        print(f"缺少产物首页 {book.as_posix()}/index.html：确认在仓库根目录渲染")
        return 1

    html_files = sorted(book.rglob("*.html"))
    if not html_files:
        print(f"{book.as_posix()} 下没有任何 HTML 文件")
        return 1

    for path in html_files:
        rel = path.relative_to(book).as_posix()
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            problems.append(f"{rel}: 带 BOM")
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            problems.append(f"{rel}: 非 UTF-8（{exc}）")
            continue
        if "\ufffd" in text:
            problems.append(f"{rel}: 含 U+FFFD 替换符")
            continue
        for marker in MOJIBAKE_MARKERS:
            if marker in text:
                problems.append(f"{rel}: 命中乱码特征「{marker}」")
                break

    index_text = index.read_text(encoding="utf-8", errors="replace")
    if "charset=utf-8" not in index_text.replace('"', "").replace("'", ""):
        problems.append("index.html 缺少 charset=utf-8 声明")
    if "file:///" in index_text:
        problems.append("index.html 引用 file:/// 本地绝对路径，发布后必然失效")

    # Book 项目渲染产物是 sitemap.xml（site-url 缺失时不生成），条目必须是绝对 URL
    sitemap = book / "sitemap.xml"
    if not sitemap.is_file():
        problems.append("缺少 sitemap.xml：通常是 _quarto.yml 的 book.site-url 未配置")
    else:
        sitemap_text = sitemap.read_text(encoding="utf-8", errors="replace")
        for loc in sitemap_text.split("<loc>")[1:]:
            url = loc.split("</loc>")[0].strip()
            if url and not url.startswith("https://"):
                problems.append(f"sitemap.xml 存在非绝对 URL：{url}")
                break

    root = Path(__file__).resolve().parents[4]
    for qmd in sorted((root / "content").rglob("*.qmd")):
        source = qmd.read_text(encoding="utf-8")
        if not source.startswith("---"):
            continue
        front = source.split("---", 2)[1]
        if "engine: jupyter" not in front:
            continue
        html = book / qmd.relative_to(root).with_suffix(".html")
        rel = html.relative_to(book).as_posix()
        if not html.is_file():
            problems.append(f"{rel}: 声明了 engine: jupyter，但没有对应 HTML")
            continue
        page = html.read_text(encoding="utf-8", errors="replace")
        figures = html.with_name(html.stem + "_files")
        figure_text = ""
        if figures.is_dir():
            figure_text = "\n".join(
                path.read_text(encoding="utf-8", errors="replace")
                for path in figures.rglob("*.svg")
            )
        if "coords-grid" not in page and "coords-grid" not in figure_text:
            problems.append(f"{rel}: 坐标图页面缺少 coords-grid")

    if problems:
        print(f"发布产物检查失败（{len(problems)} 项）：")
        for item in problems[:30]:
            print(f"  {item}")
        return 1
    print(f"发布产物检查全部通过：{len(html_files)} 个 HTML，编码干净，sitemap 就绪")
    return 0


if __name__ == "__main__":
    sys.exit(main())
