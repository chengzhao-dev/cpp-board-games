#!/usr/bin/env python3
"""校验渲染产物（_book）里的「结构契约」，防止已修过的 HTML/CSS 联动 bug 复发。

为什么需要它：Quarto 升级会改动代码块的 DOM（例如复制按钮从 div.sourceCode 的
后代变成兄弟），这类问题在任何单一源文件中都看不出来——只有把「产物结构」和
「CSS 选择器」放在一起校验才能发现。本脚本把历史上真实踩过的坑固化成断言。

省 token 的机制：脚本自己去读产物里那些几十 KB 的 HTML/CSS，对外只输出
每条契约一行的结论（PASS/MISS）。正常情况下人肉读 _book 的必要性被消除。
只有某条契约报 FAIL 时，才需要开诊断模式去看具体文件。

契约清单：
  C1 复制按钮可见性：产物中 button.code-copy-button 必须与 div.sourceCode
     同处 .code-copy-outer-scaffold 之下且互为兄弟，且 CSS 里必须存在
     .code-copy-outer-scaffold:hover .code-copy-button 规则。
     （若选择器仍写成 div.sourceCode:hover 的后代形式，hover 永不生效。）
  C2 触屏兜底：CSS 必须包含 @media (hover: none) 下的 .code-copy-button 可见规则，
     否则移动端永远无法复制代码。
  C3 打印不隐藏代码：@media print 内不得对 .code-copy-outer-scaffold 设 display:none。
     （该层现在包裹代码本身，隐藏它 = 打印/PDF 时代码整块消失。）
  C4 站点图标：每个 HTML 的 <head> 必须含 rel="icon" 且指向 favicon.svg，
     且该图标文件确实被发布到产物目录。
  C5 Mermaid 图表（按产物条件）：产物没有 mermaid-js 占位符，说明正文本就不用图表，
     契约 N/A。一旦出现占位符，就必须同时包含 Quarto Mermaid 运行时，且不得退化为
     普通 sourceCode 代码块。浏览器加载脚本后由占位符转换为 SVG。
  C6 代码主题稳定性：源 CSS 必须使用统一代码字体，不得保留按 Bash/PowerShell
      命令 token 强制改色的旧选择器。普通文本代码块不得带语言 token。
  C7 代码块视觉契约：普通文本代码块与语言代码块必须共用代码背景、边框、
      字体和布局令牌，避免两套代码块样式分叉。
  C8 代码来源标题：QMD 代码块必须由 .code-with-filename 包裹，且主题必须提供
      标题背景、文字和间距令牌。标题条不能退化为普通代码块。
  C9 可折叠答案：产物中的 details.answer-disclosure 存在时，必须默认收起，
      摘要必须等于“查看答案”，且答案区不得混入标题层级；没有答案块时为 N/A。

用法：python check_dom_contracts.py [--book-dir _book] [--verbose]
退出码：0 = 全部契约通过，1 = 有契约失败，2 = 产物目录不存在（需先 quarto render）。
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SCAFFOLD = "code-copy-outer-scaffold"
COPY_BTN = "code-copy-button"
SRCODE = "sourceCode"

# 无闭合标签的元素：不入栈，否则解析栈会被打乱
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class Node:
    """极简 DOM 节点：只保留契约所需的 tag / class / attrs / 父子关系。"""

    __slots__ = ("tag", "classes", "attrs", "children", "parent")

    def __init__(self, tag, classes, attrs, parent):
        self.tag = tag
        self.classes = set(classes)
        self.attrs = attrs
        self.children = []
        self.parent = parent


class TreeBuilder(HTMLParser):
    """把 HTML 解析成只含 class 信息的轻量树，避免引入第三方解析库。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", set(), {}, None)
        self.stack = [self.root]
        self.link_rels = []  # [(rel, href)] 供 favicon 契约使用

    def handle_starttag(self, tag, attrs):
        attrd = dict(attrs)
        classes = (attrd.get("class") or "").split()
        node = Node(tag, classes, attrd, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag == "link":
            self.link_rels.append(((attrd.get("rel") or "").lower(), attrd.get("href") or ""))
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_endtag(self, tag):
        # 容忍源文档里缺失的闭合标签（Quarto 输出常有）：向上回溯到匹配的开标签
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return


def walk(node):
    for child in node.children:
        yield child
        yield from walk(child)


def is_descendant(node, ancestor):
    parent = node.parent
    while parent is not None:
        if parent is ancestor:
            return True
        parent = parent.parent
    return False


def normalize(css):
    """压掉注释与多余空白，让选择器匹配不受换行/缩进影响。"""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\s+", " ", css)


def collect_css(book_dir):
    texts = []
    for path in sorted(book_dir.rglob("*.css")):
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if SCAFFOLD in raw or COPY_BTN in raw or "@media" in raw:
            texts.append((path, normalize(raw)))
    return texts


def media_blocks(css, keyword):
    """提取 @media <keyword> 整块内容（含嵌套），按花括号配平扫描。"""
    blocks = []
    for m in re.finditer(r"@media[^{]*\b" + keyword + r"\b[^{]*\{", css):
        depth = 1
        i = m.end()
        while i < len(css) and depth:
            if css[i] == "{":
                depth += 1
            elif css[i] == "}":
                depth -= 1
            i += 1
        if depth == 0:
            blocks.append(css[m.end():i - 1])
    return blocks


def rules_of(block_css):
    """把一段 CSS 拆成 (selector, body) 列表（跳过嵌套的 @规则首部）。"""
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", block_css):
        out.append((m.group(1).strip(), m.group(2)))
    return out


def hidden_selectors(block_css, needle):
    """返回该 CSS 块中对 needle 设了 display:none 的选择器列表。"""
    hits = []
    for selector, body in rules_of(block_css):
        if needle in selector and re.search(r"display\s*:\s*none", body):
            hits.append(selector)
    return hits


def parse_highlight_styles(quarto_text):
    """从 _quarto.yml 解析 highlight-style.light / .dark。"""
    block = re.search(
        r"highlight-style:\s*\n((?:[ \t]+.+\n)+)",
        quarto_text,
    )
    if not block:
        return None, None
    body = block.group(1)
    light = re.search(r"light:\s*(\S+)", body)
    dark = re.search(r"dark:\s*(\S+)", body)
    return (
        light.group(1) if light else None,
        dark.group(1) if dark else None,
    )


def parse_active_palette(quarto_text):
    """从 css 列表解析 palettes/<name>/tokens.css。"""
    match = re.search(r"palettes/([A-Za-z0-9_-]+)/tokens\.css", quarto_text)
    return match.group(1) if match else None


def parse_palette_meta_highlights(meta_text):
    """从 palette meta.md 表格读取期望的 highlight 主题名。"""
    light = re.search(r"highlight light\s*\|\s*`([^`]+)`", meta_text)
    dark = re.search(r"highlight dark\s*\|\s*`([^`]+)`", meta_text)
    return (
        light.group(1) if light else None,
        dark.group(1) if dark else None,
    )


def check_contracts(book_dir, htmls, css_pairs):
    """跑完全部契约，返回 [(id, 名称, ok, 摘要, [细节行])]。"""
    results = []
    root = Path(__file__).resolve().parents[4]

    # ---------- C0 活跃 palette 与高亮主题一致 ----------
    quarto = root / "_quarto.yml"
    try:
        quarto_text = quarto.read_text(encoding="utf-8")
    except OSError:
        quarto_text = ""
    light_hl, dark_hl = parse_highlight_styles(quarto_text)
    palette = parse_active_palette(quarto_text)
    meta_path = (
        root
        / ".agents/skills/designing-theme/assets/theme/palettes"
        / (palette or "_missing_")
        / "meta.md"
    )
    try:
        meta_text = meta_path.read_text(encoding="utf-8") if meta_path.is_file() else ""
    except OSError:
        meta_text = ""
    expect_light, expect_dark = parse_palette_meta_highlights(meta_text)
    no_custom = "custom.theme" not in quarto_text.lower()
    c0 = bool(
        palette
        and light_hl
        and dark_hl
        and expect_light
        and expect_dark
        and light_hl == expect_light
        and dark_hl == expect_dark
        and no_custom
    )
    results.append((
        "C0", "活跃 palette 与 highlight-style 一致", c0,
        "palette=%s，light=%s（期望 %s），dark=%s（期望 %s），无 custom.theme=%s" % (
            palette, light_hl, expect_light, dark_hl, expect_dark, no_custom),
        [
            "_quarto.yml 的 palettes/<name>/tokens.css 须与同 pack meta.md 的 highlight 映射一致",
            "禁止 custom.theme；换色板时同步改 theme SCSS、palette tokens 与 highlight-style",
        ],
    ))

    # ---------- C1 复制按钮可见性 ----------
    sibling_ok = False
    scaffold_pages = 0
    for path, tree, _rels in htmls:
        scaffolds = [n for n in walk(tree) if SCAFFOLD in n.classes]
        if not scaffolds:
            continue
        scaffold_pages += 1
        for sc in scaffolds:
            code = [c for c in sc.children if c.tag == "div" and SRCODE in c.classes]
            btns = [c for c in sc.children if c.tag == "button" and COPY_BTN in c.classes]
            if code and btns and not any(is_descendant(b, code[0]) for b in btns):
                sibling_ok = True
    hover_rule = any(
        ".%s:hover .%s" % (SCAFFOLD, COPY_BTN) in css for _, css in css_pairs
    )
    stale_rule = any(
        "div.%s:hover .%s" % (SRCODE, COPY_BTN) in css for _, css in css_pairs
    )
    c1 = sibling_ok and hover_rule and not stale_rule
    results.append((
        "C1", "复制按钮 hover 可见（兄弟 DOM + scaffold 选择器）", c1,
        "pages=%d sibling=%s hover-rule=%s%s"
        % (scaffold_pages, sibling_ok, hover_rule, " stale-rule!" if stale_rule else ""),
        [
            "产物中 button.%s 必须与 div.%s 同为 .%s 的直接子元素" % (COPY_BTN, SRCODE, SCAFFOLD),
            "CSS 必须含 .%s:hover .%s（不能停留在 div.%s:hover 的后代写法）"
            % (SCAFFOLD, COPY_BTN, SRCODE),
        ],
    ))

    # ---------- C2 触屏兜底 ----------
    touch_ok = False
    for _, css in css_pairs:
        for block in media_blocks(css, "hover: none"):
            if COPY_BTN in block and re.search(r"opacity\s*:\s*1", block):
                touch_ok = True
    results.append((
        "C2", "触屏无 hover 时复制按钮仍可见", touch_ok,
        "@media (hover: none) 规则=%s" % touch_ok,
        ["CSS 需含 @media (hover: none) { .%s { opacity: 1 } }" % COPY_BTN],
    ))

    # ---------- C3 打印不隐藏代码 ----------
    offenders = []
    for path, css in css_pairs:
        for block in media_blocks(css, "print"):
            for sel in hidden_selectors(block, SCAFFOLD):
                offenders.append("%s: %s" % (path.name, sel))
    c3 = not offenders
    results.append((
        "C3", "打印/PDF 时代码块不被隐藏", c3,
        "违规规则数=%d" % len(offenders),
        ["@media print 内不得对 .%s 设 display:none（它现在包裹代码本身），只可隐藏 .%s"
         % (SCAFFOLD, COPY_BTN)] + offenders,
    ))

    # ---------- C4 favicon ----------
    icon_pages = 0
    missing = []
    for path, _tree, link_rels in htmls:
        rels = [(r, h) for r, h in link_rels if "icon" in r]
        if any("favicon.svg" in h for r, h in rels):
            icon_pages += 1
        else:
            missing.append(str(path.relative_to(book_dir)))
    icon_file = any(p.name == "favicon.svg" for p in book_dir.rglob("favicon.svg"))
    c4 = icon_pages == len(htmls) and icon_file and bool(htmls)
    summary = "%d/%d 页含 icon 链接，图标已发布=%s" % (icon_pages, len(htmls), icon_file)
    if missing:
        summary += "；缺链接: " + ", ".join(missing[:3])
        if len(missing) > 3:
            summary += " …"
    results.append((
        "C4", "站点图标已注入并发布", c4, summary,
        ["每页 <head> 需 <link rel=\"icon\" … favicon.svg>；源文件见 .agents/skills/designing-theme/assets/theme/assets/favicon.svg，"
         "由 .agents/skills/maintaining-python/scripts/maintenance/generate_favicon.py 生成"],
    ))

    # ---------- C5 Mermaid ----------
    mermaid_blocks = 0
    mermaid_runtime_pages = 0
    raw_mermaid = []
    for path, _tree, _rels in htmls:
        try:
            html = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        mermaid_blocks += len(re.findall(r"<pre\b[^>]*class=\"[^\"]*\bmermaid-js\b", html))
        if "quarto-diagram/mermaid.min.js" in html and "quarto-diagram/mermaid-init.js" in html:
            mermaid_runtime_pages += 1
        if re.search(
            r"<pre\b[^>]*class=\"[^\"]*\bsourceCode\b[^\"]*\"[^>]*>"
            r"(?:(?!</pre>).)*?(?:(?:flowchart|graph)\s+(?:TD|TB|LR|RL|BT)"
            r"|sequenceDiagram|stateDiagram|classDiagram)",
            html, re.S,
        ):
            raw_mermaid.append(str(path.relative_to(book_dir)))
    # 无占位符 = 正文不用图表，契约 N/A。有占位符才要求 Quarto Mermaid 运行时。
    c5 = not raw_mermaid and (mermaid_blocks == 0 or mermaid_runtime_pages > 0)
    if mermaid_blocks == 0 and not raw_mermaid:
        summary = "正文无 Mermaid 图（契约 N/A）"
    elif mermaid_blocks == 0:
        summary = "未发现 mermaid-js 占位符，疑似围栏写错退化为普通源码块=%d" % len(raw_mermaid)
    else:
        summary = "Mermaid 占位符=%d，运行时页面=%d，普通源码块=%d" % (
            mermaid_blocks, mermaid_runtime_pages, len(raw_mermaid))
    if raw_mermaid:
        summary += "（" + ", ".join(raw_mermaid[:3]) + (" …" if len(raw_mermaid) > 3 else "") + "）"
    results.append((
        "C5", "Mermaid 使用 Quarto 图表运行时", c5, summary,
        ["Mermaid 围栏必须使用 ```{mermaid}",
         "正文含 Mermaid 图时，产物必须同时有 mermaid-js 占位符和 Quarto Mermaid 运行时",
         "不得退化为带 sourceCode 类的普通图表代码块"],
    ))

    # ---------- C6 GitHub 代码主题与稳定 token ----------
    css_text = "\n".join(css for _, css in css_pairs)
    source_css = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in sorted(book_dir.rglob("*.css"))
    )
    has_font = "var(--mono-font)" in source_css and "pre.sourceCode" in source_css
    has_left_align = bool(re.search(r"text-align\s*:\s*left", source_css))
    stale_selectors = re.findall(
        r"(?:pre|div)\.sourceCode:is\(\.bash,\s*\.powershell\)[^{]*\{[^}]*color",
        source_css,
        flags=re.S,
    )
    legacy_output_pages = []
    for path, tree, _rels in htmls:
        for node in walk(tree):
            if node.tag != "pre" or SRCODE in node.classes:
                continue
            if any(cls in node.classes for cls in ("bash", "powershell", "hljs")):
                legacy_output_pages.append(str(path.relative_to(book_dir)))
    c6 = has_font and has_left_align and not stale_selectors and not legacy_output_pages
    summary = "统一字体=%s，左对齐=%s，旧命令着色选择器=%d，普通文本代码块语言类=%d" % (
        has_font, has_left_align, len(stale_selectors), len(legacy_output_pages))
    results.append((
        "C6", "代码主题与 token 样式稳定", c6, summary,
        [
            "亮色/暗色应由 _quarto.yml 的 highlight-style（与活跃 palette meta 一致）提供",
            "代码 CSS 应统一使用 --mono-font，不按 Bash/PowerShell 命令 token 强制改色",
            "普通文本代码块应保持左对齐并保留终端输出的空格",
            "普通文本代码块不应带 sourceCode、bash、powershell 或 hljs 类",
        ],
    ))

    # ---------- C7 普通文本代码块与语言代码块的视觉契约 ----------
    theme_root = root / ".agents/skills/designing-theme/assets/theme"
    source_css_paths = list(theme_root.glob("css/*.css"))
    if palette:
        pack_tokens = theme_root / "palettes" / palette / "tokens.css"
        if pack_tokens.is_file():
            source_css_paths.append(pack_tokens)
    source_css_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in sorted(source_css_paths)
    )
    shared_selectors = (
        "pre.sourceCode,\npre:not(.sourceCode)" in source_css_text
        or "pre.sourceCode, pre:not(.sourceCode)" in source_css_text
    )
    shared_tokens = all(token in source_css_text for token in (
        "--code-bg", "--code-border", "--code-fg", "--mono-font",
        "--code-font-size", "--code-line-height", "--code-padding",
    ))
    c7 = shared_selectors and shared_tokens
    results.append((
        "C7", "普通文本代码块与语言代码块共享视觉令牌", c7,
        "共享选择器=%s，代码令牌=%s" % (shared_selectors, shared_tokens),
        [
            ".agents/skills/designing-theme/assets/theme/css/code.css 应让 pre.sourceCode、pre:not(.sourceCode) 与 div.sourceCode 共用布局",
            "背景、边框、字体、字号、行高和内边距应引用共享 tokens 与活跃 palette 的代码令牌",
        ],
    ))

    # ---------- C8 代码来源标题 ----------
    titled_blocks = 0
    untitled = []
    for path, tree, _rels in htmls:
        wrappers = [n for n in walk(tree) if "code-with-filename" in n.classes]
        titled_blocks += len(wrappers)
        for node in walk(tree):
            if node.tag != "pre":
                continue
            if any(is_descendant(node, wrapper) for wrapper in wrappers):
                continue
            if node.classes & {"mermaid", "mermaid-js"}:
                continue
            untitled.append(str(path.relative_to(book_dir)))
    title_tokens = all(token in source_css_text for token in (
        "--code-title-bg", "--code-title-fg", "--code-title-font-size", "--code-title-padding",
    ))
    c8 = titled_blocks > 0 and not untitled and title_tokens
    summary = "代码标题块=%d，未包裹 pre=%d，标题令牌=%s" % (
        titled_blocks, len(untitled), title_tokens)
    if untitled:
        summary += "（" + ", ".join(sorted(set(untitled))[:3]) + " …）"
    results.append((
        "C8", "代码块来源标题已渲染并受主题控制", c8, summary,
        [
            "站点 QMD 代码块必须使用 {.语言 filename=\"标题\"} 属性围栏",
            "产物中的 pre 必须位于 .code-with-filename 下",
            "tokens.css 必须提供 --code-title-bg/fg/font-size/padding",
        ],
    ))

    # ---------- C9 可折叠答案 ----------
    answer_total = 0
    answer_open = []
    answer_summary = []
    answer_heading = []
    for path, _root, _link_rels in htmls:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        pattern = re.compile(
            r"<details\b(?P<attrs>[^>]*)>(?P<body>.*?)</details>",
            flags=re.S | re.I,
        )
        for match in pattern.finditer(text):
            attrs = match.group("attrs")
            if "answer-disclosure" not in attrs:
                continue
            answer_total += 1
            rel = str(path.relative_to(book_dir))
            if re.search(r"\bopen\b", attrs):
                answer_open.append(rel)
            summary_match = re.search(
                r"<summary\b[^>]*>(?P<summary>.*?)</summary>",
                match.group("body"),
                flags=re.S | re.I,
            )
            visible = re.sub(r"<[^>]+>", "", summary_match.group("summary")).strip() if summary_match else ""
            if visible != "查看答案":
                answer_summary.append(rel)
            if re.search(r"<h[1-6]\b", match.group("body"), flags=re.I):
                answer_heading.append(rel)
    c9 = (
        not answer_open
        and not answer_summary
        and not answer_heading
    )
    summary = "答案块=%d，默认展开=%d，摘要异常=%d，内部标题=%d" % (
        answer_total,
        len(answer_open),
        len(answer_summary),
        len(answer_heading),
    )
    results.append((
        "C9", "可折叠答案默认收起且摘要与层级正确（无答案时 N/A）", c9, summary,
        [
            "站点 QMD 使用 {.answer} 组件，产物为 details.answer-disclosure 和固定摘要",
            "answer-disclosure 不得带 open 属性",
            "折叠答案内部不得出现 h1–h6",
        ],
    ))

    return results


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="校验渲染产物中的结构契约")
    parser.add_argument("--book-dir", default="_book", help="渲染产物目录（默认 _book）")
    parser.add_argument("--verbose", action="store_true", help="失败时展开修复指引")
    args = parser.parse_args()

    book_dir = Path(args.book_dir)
    if not book_dir.is_dir():
        print("MISS 产物目录不存在：%s（请先运行 quarto render）" % book_dir)
        return 2

    htmls = []
    for path in sorted(book_dir.rglob("*.html")):
        builder = TreeBuilder()
        try:
            builder.feed(path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        htmls.append((path, builder.root, builder.link_rels))

    if not htmls:
        print("MISS 未找到任何 HTML：%s" % book_dir)
        return 1

    css_pairs = collect_css(book_dir)
    results = check_contracts(book_dir, htmls, css_pairs)

    # 默认每条契约只占一行，失败项排前面，方便快速定位
    failed = 0
    for cid, name, ok, summary, hints in sorted(results, key=lambda r: r[2]):
        if not ok:
            failed += 1
        print("%s %s %s  (%s)" % ("OK  " if ok else "FAIL", cid, name, summary))
        if not ok and args.verbose:
            for line in hints:
                print("       · %s" % line)

    print()
    if failed == 0:
        print("DOM contracts: %d/%d PASS" % (len(results), len(results)))
        return 0
    print("DOM contracts: %d 项失败，需开诊断模式定位（见 --verbose）" % failed)
    return 1


if __name__ == "__main__":
    sys.exit(main())
