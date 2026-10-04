#!/usr/bin/env python3
"""校验关键设计令牌、字体资产与可用的浏览器布局指标。

静态阶段用单次字面匹配（子串查找）+ 计数，不对压缩后大 CSS 做宽模式扫描。
Node、Playwright 与 Edge 可用时，调用 measure_pages.mjs 验证真实几何。不可用时
输出明确 SKIP，不把静态断言冒充布局验收。
规范出处：.agents/skills/designing-theme/references/theme-system.md。

用法：python check_layout.py [--book-dir _book] [--browser]
退出码：0 = 关键令牌全部存在，1 = 有缺失。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

THEME_DIR = Path(__file__).resolve().parents[1]
FONT_DIR = THEME_DIR / "assets" / "theme" / "assets" / "fonts"
FONTS_CSS = THEME_DIR / "assets" / "theme" / "css" / "fonts.css"
SHARED_TOKENS_CSS = THEME_DIR / "assets" / "theme" / "css" / "tokens.css"
PALETTE_ROOT = THEME_DIR / "assets" / "theme" / "palettes"
MEASURE_SCRIPT = Path(__file__).resolve().parent / "measure_pages.mjs"
ROOT = THEME_DIR.parents[2]
QUARTO_YML = ROOT / "_quarto.yml"
FONT_FAMILIES = ("LXGW WenKai Screen", "LXGW Bright Code")
EXPECTED_FONT_FACES = {
    "Fixel Text": 3,
    "LXGW WenKai Screen": 1,
    "LXGW Bright Code": 1,
}
# 三个 Fixel 字重加两个常用汉字包，保留少量缓存与字重余量。
FONT_PAGE_BYTES_LIMIT = 1_600_000
FONT_PAGE_FACES_LIMIT = 5


def color_alpha(value):
    """返回 CSS 颜色的 alpha 通道；无法解析为 rgb/rgba 时按不透明处理。"""
    match = re.match(r"rgba?\(([^)]*)\)", (value or "").strip())
    if not match:
        return 1.0
    parts = [part.strip() for part in match.group(1).split(",")]
    return float(parts[3]) if len(parts) == 4 else 1.0


def active_palette_name(quarto_text=""):
    """从 _quarto.yml 的 css 列表解析活跃 palette 名。"""
    text = quarto_text
    if not text and QUARTO_YML.is_file():
        text = QUARTO_YML.read_text(encoding="utf-8")
    match = re.search(r"palettes/([A-Za-z0-9_-]+)/tokens\.css", text)
    return match.group(1) if match else None


# 共享结构令牌与组件规则（与色板无关）
SHARED_CHECKS = [
    ("body line-height 1.75", "line-height: 1.75"),
    ("content width", "--content-width: 720px"),
    ("code font 15px", "--code-font-size: 0.9375rem"),
    ("code line-height 1.75", "--code-line-height: 1.75"),
    ("code title padding token", "--code-title-padding"),
    ("ui font stack", '--ui-font: "Fixel Text", "LXGW WenKai Screen"'),
    ("cjk font fallback", '"LXGW WenKai Screen"'),
    ("code font stack", '--mono-font: "LXGW Bright Code", "LXGW WenKai Screen"'),
    ("bright code family", '"LXGW Bright Code"'),
    ("code followup gap", "--code-followup-gap: 1rem"),
    ("list code followup spacing", "margin-top: var(--code-followup-gap)"),
    ("list code with filename selector", "li > :is(.code-copy-outer-scaffold, .code-with-filename"),
    ("readable body font", "font-size: 1rem"),
    ("body block rhythm", "margin-top: 1.55rem"),
    ("paragraphs follow the body column", "max-width: 100%"),
    ("answer disclosure container", "details.answer-disclosure"),
    ("answer disclosure summary", "details.answer-disclosure > summary"),
    ("feature-grid max two columns", "calc((100% - 1.25rem) / 2)"),
]

# 语义令牌名必须存在（色值由活跃 palette 提供）
TOKEN_NAME_CHECKS = [
    ("code title background", "--code-title-bg"),
    ("code title foreground", "--code-title-fg"),
    ("accent dot token", "--dot-accent"),
    ("callout tip (best-practice semantics)", "--callout-tip-border"),
    ("callout warning (key-insight semantics)", "--callout-warning-border"),
    ("callout important (deep-dive semantics)", "--callout-important-border"),
]

# palettes/github 色值期望；换 pack 时改对应表，勿把实验包色值写进 github 表
PALETTE_VALUE_CHECKS = {
    "github": [
        ("light body token #1F2328", "--body-color: #1F2328"),
        ("light GitHub link #0969DA", "#0969DA"),
        ("light navbar page-bg token", "--navbar-bg: #FFFFFF"),
        ("dark navbar page-bg token", "--navbar-bg: #22272E"),
        ("light code background", "--code-bg: #F6F8FA"),
        ("dark code background", "--code-bg: #2D333B"),
        ("dark page #22272E", "#22272E"),
        ("dark body #CDD9E5", "#CDD9E5"),
        ("dark secondary #B1BAC4", "#B1BAC4"),
        ("dark link #539BF5", "#539BF5"),
        ("callout note border light", "--callout-note-border: #2563EB"),
    ],
}

# 兼容旧名：测试与外部引用仍可能导入 CHECKS
CHECKS = SHARED_CHECKS + TOKEN_NAME_CHECKS + PALETTE_VALUE_CHECKS["github"]

CALLOUT_CHECKS = [
    ("callout body font 16px", "font-size: 1rem;"),
    ("callout title font 15px", "font-size: 0.9375rem;"),
    ("callout padding 16px", "padding: 1rem;"),
    ("callout header gap 8px", "margin: 0 0 0.5rem;"),
]

FORBIDDEN_FONT_REFERENCES = [
    ("Inter reference", "Inter"),
    ("Noto Sans SC reference", "Noto Sans SC"),
    ("Noto Sans Mono CJK SC reference", "Noto Sans Mono CJK SC"),
    ("JetBrains Mono reference", "JetBrains Mono"),
    ("local font fallback", "local("),
]


class VisibleTextParser(HTMLParser):
    """Extract visible text from rendered pages without script/style content."""

    def __init__(self, code_only=False):
        super().__init__(convert_charrefs=True)
        self.hidden_depth = 0
        self.pre_depth = 0
        self.code_depth = 0
        self.code_only = code_only
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden_depth += 1
        if tag == "pre":
            self.pre_depth += 1
        if tag == "code":
            self.code_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.hidden_depth:
            self.hidden_depth -= 1
        if tag == "pre" and self.pre_depth:
            self.pre_depth -= 1
        if tag == "code" and self.code_depth:
            self.code_depth -= 1

    def handle_data(self, data):
        in_code = bool(self.pre_depth or self.code_depth)
        if not self.hidden_depth and (not self.code_only or in_code):
            self.chunks.append(data)


def parse_unicode_ranges(css_text, family):
    """Return the unicode ranges declared for one self-hosted font family."""
    ranges = []
    for block in re.findall(r"@font-face\s*\{([^}]*)\}", css_text, re.S):
        if not re.search(
            rf'font-family\s*:\s*["\']{re.escape(family)}["\']', block
        ):
            continue
        match = re.search(r"unicode-range:([^;}]+)", block)
        if not match:
            continue
        for token in match.group(1).split(","):
            token = token.strip()
            if not token.startswith("U+"):
                continue
            value = token[2:]
            if "-" in value:
                start, end = value.split("-", 1)
                ranges.append((int(start, 16), int(end, 16)))
            else:
                point = int(value, 16)
                ranges.append((point, point))
    return ranges


def font_face_entries(css_text):
    """Parse family and URL pairs from @font-face blocks."""
    entries = []
    for block in re.findall(r"@font-face\s*\{([^}]*)\}", css_text, re.S):
        family = re.search(r"font-family\s*:\s*[\"']([^\"']+)[\"']", block)
        url = re.search(r"url\(\s*[\"']?([^\"')]+)", block)
        if family and url:
            entries.append((family.group(1), url.group(1)))
    return entries


def check_font_assets(css_text):
    """Return missing, duplicate, orphan, and invalid-font diagnostics."""
    entries = font_face_entries(css_text)
    problems = []
    referenced = {}
    for family, url in entries:
        target = (FONTS_CSS.parent / url).resolve()
        referenced.setdefault(target, []).append(family)
        if not target.is_file():
            problems.append(f"missing font asset: {family} -> {target.name}")
            continue
        if target.read_bytes()[:4] != b"wOF2":
            problems.append(f"invalid WOFF2 signature: {target.name}")

    for family, expected in EXPECTED_FONT_FACES.items():
        actual = sum(1 for item, _url in entries if item == family)
        if actual != expected:
            problems.append(f"{family} font faces={actual}, expected={expected}")

    for target, families in referenced.items():
        if len(families) > 1:
            problems.append(f"font URL reused {len(families)} times: {target.name}")

    referenced_paths = set(referenced)
    actual_paths = set(FONT_DIR.glob("*.woff2"))
    for path in sorted(actual_paths - referenced_paths):
        problems.append(f"orphan font asset: {path.name}")
    if not actual_paths:
        problems.append("no WOFF2 font assets found")
    return problems


def check_font_partition(css_text):
    """Return overlap problems in explicitly partitioned CJK font faces."""
    problems = []
    for family in FONT_FAMILIES:
        declared = parse_unicode_ranges(css_text, family)
        if not declared:
            continue
        covered = set()
        overlaps = set()
        for start, end in declared:
            points = set(range(start, end + 1))
            overlaps.update(covered & points)
            covered.update(points)
        if overlaps:
            sample = ", ".join(f"U+{point:X}" for point in sorted(overlaps)[:8])
            problems.append(
                f"{family} unicode-range overlaps: {len(overlaps)} ({sample})"
            )
    return problems


def resolve_node():
    candidates = [os.environ.get("BOARD_GAMES_NODE"), shutil.which("node")]
    cache = Path.home() / ".cache" / "codex-runtimes"
    if cache.is_dir():
        candidates.extend(
            str(path)
            for path in sorted(cache.glob("*/dependencies/node/bin/node*"))
        )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def resolve_playwright_root():
    candidates = [os.environ.get("BOARD_GAMES_NODE_PATH"), os.environ.get("NODE_PATH")]
    cache = Path.home() / ".cache" / "codex-runtimes"
    if cache.is_dir():
        candidates.extend(
            str(path)
            for path in sorted(cache.glob("*/dependencies/node/node_modules"))
        )
    for candidate in candidates:
        if candidate and (Path(candidate) / "playwright" / "index.js").is_file():
            return str(candidate)
    return None


def full_layout_required():
    """主题或 Book 配置变化时跑全量页面矩阵，普通内容改动只跑代表页。"""
    result = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            "HEAD",
            "--",
            ".agents/skills/designing-theme/assets/theme",
            "_quarto.yml",
        ],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 1


def browser_layout(book_dir, verbose):
    """Measure rendered pages and return (problems, skipped_reason, info)."""
    node = resolve_node()
    playwright_root = resolve_playwright_root()
    if not node or not playwright_root or not MEASURE_SCRIPT.is_file():
        return [], (
            "Node/Playwright/Edge 运行时不可用"
            f" (node={node or '无'}, NODE_PATH={playwright_root or '无'})"
        ), {}

    shots_dir = ROOT / "temp" / "theme-regression"
    out_file = shots_dir / "measure.json"
    shots_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, NODE_PATH=playwright_root, PYTHONIOENCODING="utf-8")
    command = [
        node,
        str(MEASURE_SCRIPT),
        "--book-dir",
        str(book_dir),
        "--out",
        str(out_file),
        "--shots-dir",
        str(shots_dir),
    ]
    if full_layout_required():
        command.append("--all-pages")
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = proc.stdout.decode("utf-8", errors="replace")
    if proc.returncode == 2:
        return [], output.strip(), {}
    if proc.returncode != 0 or not out_file.is_file():
        return [f"browser measurement failed (exit={proc.returncode})"], output.strip(), {}

    metrics = json.loads(out_file.read_text(encoding="utf-8"))
    info = {
        "mode": metrics.get("mode", "full"),
        "pages": len(metrics.get("selectedPages", metrics.get("pages", []))),
    }
    problems = []
    font_assets_by_name = {}
    for _family, url in font_face_entries(FONTS_CSS.read_text(encoding="utf-8")):
        target = (FONTS_CSS.parent / url).resolve()
        font_assets_by_name[target.name] = target.stat().st_size if target.is_file() else 0
    width_floor = {1280: 640, 768: 500, 390: 320}
    for width_text, pages in metrics["viewports"].items():
        width = int(width_text)
        for key, data in pages.items():
            scheme, page_id = key.split(":", 1)
            label = f"{scheme}:{page_id}@{width}"
            if data.get("error"):
                problems.append(f"{label}: {data['error']}")
                continue
            requested_fonts = data.get("requestedFonts", [])
            unknown_fonts = sorted(set(requested_fonts) - set(font_assets_by_name))
            if unknown_fonts:
                problems.append(f"{label}: unknown font requests {unknown_fonts}")
            loaded_fonts = [
                (filename, font_assets_by_name[filename])
                for filename in requested_fonts
                if filename in font_assets_by_name
            ]
            loaded_font_bytes = sum(size for _name, size in loaded_fonts)
            if len(loaded_fonts) > FONT_PAGE_FACES_LIMIT:
                problems.append(
                    f"{label}: 字体请求 {len(loaded_fonts)} > {FONT_PAGE_FACES_LIMIT}"
                )
            if loaded_font_bytes > FONT_PAGE_BYTES_LIMIT:
                problems.append(
                    f"{label}: 字体字节 {loaded_font_bytes} > {FONT_PAGE_BYTES_LIMIT}"
                )
            data["loadedFontCount"] = len(loaded_fonts)
            data["loadedFontBytes"] = loaded_font_bytes
            if data["paragraphWidth"] < width_floor[width]:
                problems.append(
                    f"{label}: 正文段宽 {data['paragraphWidth']}px < {width_floor[width]}px"
                )
            if width <= 768:
                hidden_copy = [
                    opacity
                    for opacity in data.get("copyButtonOpacities", [])
                    if opacity < 0.99
                ]
                if hidden_copy:
                    problems.append(
                        f"{label}: 触屏复制按钮不可见 opacity={hidden_copy}"
                    )
            overlay = data.get("sidebarOverlay")
            if overlay and overlay.get("overlayState"):
                alpha = color_alpha(overlay.get("background"))
                if alpha < 0.99:
                    problems.append(
                        f"{label}: 窄屏左栏浮层底色 alpha={alpha}，正文会透上来，需不透明"
                    )
            # 侧栏折叠层级：桌面视口下只有当前页所在的分组默认展开，
            # 其余分组折叠。依据见本仓 designing-theme 技能的主题说明。
            sections = data.get("sidebarSections")
            if width >= 1280 and sections:
                expanded = [item for item in sections if item["expanded"]]
                in_part = page_id.startswith("content/")
                expected = 1 if in_part else 0
                if len(expanded) != expected:
                    problems.append(
                        f"{label}: 侧栏展开分组 {len(expanded)} 个，期望 {expected} 个"
                        f"（{[(item['text'], item['expanded']) for item in sections]}）"
                    )
                elif expanded and not expanded[0]["containsActive"]:
                    problems.append(
                        f"{label}: 侧栏展开的不是当前页所在分组 "
                        f"（展开={expanded[0]['text']}）"
                    )
            paragraph_font_size = data.get("paragraphFontSize", 0)
            for index, callout in enumerate(data.get("callouts", []), 1):
                if abs(callout["bodyFontSize"] - paragraph_font_size) > 0.01:
                    problems.append(
                        f"{label}: Callout#{index} 正文 {callout['bodyFontSize']}px "
                        f"!= 正文 {paragraph_font_size}px"
                    )
                if abs(callout["titleFontSize"] - 15) > 0.01:
                    problems.append(
                        f"{label}: Callout#{index} 标题 {callout['titleFontSize']}px != 15px"
                    )
                if (
                    abs(callout["paddingTop"] - 16) > 0.01
                    or abs(callout["paddingBottom"] - 16) > 0.01
                ):
                    problems.append(
                        f"{label}: Callout#{index} 内边距 "
                        f"{callout['paddingTop']}/{callout['paddingBottom']}px != 16/16px"
                    )
                if callout["width"] + 1 < data["paragraphWidth"]:
                    problems.append(
                        f"{label}: Callout#{index} 宽 {callout['width']}px "
                        f"< 正文列 {data['paragraphWidth']}px"
                    )
            if any(not item["scrolls"] for item in data["overflow"]):
                first = next(item for item in data["overflow"] if not item["scrolls"])
                problems.append(
                    f"{label}: 横向溢出 {first['tag']}.{first['classes']} "
                    f"{first['scrollWidth']}>{first['clientWidth']}"
                )
            wrapped = [item for item in data["tocItems"] if item["height"] > 46]
            if wrapped:
                problems.append(
                    f"{label}: 目录折行 {len(wrapped)} 项，最高 {max(item['height'] for item in wrapped)}px"
                )
            for block in data["languageBlocks"]:
                if block["outerBorder"] != 1 or block["innerBorder"] != 0:
                    problems.append(
                        f"{label}: 代码边框 outer={block['outerBorder']} inner={block['innerBorder']}"
                    )
                    break
            wraps = {
                item["whiteSpace"]
                for item in data["languageBlocks"] + data["barePres"]
                if item["whiteSpace"]
            }
            if wraps - {"pre-wrap"}:
                problems.append(f"{label}: 代码 white-space={sorted(wraps)}")
    if verbose:
        for width, pages in metrics["viewports"].items():
            for key, data in pages.items():
                print(
                    f"      {key}@{width} 正文宽={data['paragraphWidth']} "
                    f"带/盒={data['textBandCount']}/{data['boxCount']} "
                    f"正文号={data.get('paragraphFontSize', 0):g} "
                    f"Callout={len(data.get('callouts', []))} "
                    f"字体={data.get('loadedFontCount', 0)}/"
                    f"{data.get('loadedFontBytes', 0)}B "
                    f"复制钮={data.get('copyButtonOpacities', [])} "
                    f"溢出={len(data['overflow'])} "
                    f"侧栏展开="
                    f"{[item['text'] for item in data.get('sidebarSections') or [] if item['expanded']]}"
                )
    return problems, None, info


def needs_cjk_coverage(codepoint):
    """Only assert self-hosted coverage for CJK text and CJK punctuation."""
    return (
        0x2E80 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x3000 <= codepoint <= 0x303F
        or 0xFF00 <= codepoint <= 0xFFEF
    )


def check_font_coverage(book_dir):
    """Check Chinese coverage for UI text and code text separately."""
    css_path = THEME_DIR / "assets" / "theme" / "css" / "fonts.css"
    css_text = css_path.read_text(encoding="utf-8")
    ranges = {
        family: parse_unicode_ranges(css_text, family)
        for family in FONT_FAMILIES
    }
    missing = {family: set() for family in FONT_FAMILIES}
    if not any(ranges.values()):
        return ranges, missing
    range_sets = {
        family: {
            point
            for start, end in family_ranges
            for point in range(start, end + 1)
        }
        for family, family_ranges in ranges.items()
    }
    for html_path in sorted(book_dir.rglob("*.html")):
        html_text = html_path.read_text(encoding="utf-8", errors="ignore")
        page_parser = VisibleTextParser()
        page_parser.feed(html_text)
        code_parser = VisibleTextParser(code_only=True)
        code_parser.feed(html_text)
        for family, chunks in (
            ("LXGW WenKai Screen", page_parser.chunks),
            ("LXGW Bright Code", code_parser.chunks),
        ):
            for chunk in chunks:
                for char in chunk:
                    codepoint = ord(char)
                    if (
                        needs_cjk_coverage(codepoint)
                        and codepoint not in range_sets[family]
                    ):
                        missing[family].add(char)
    return ranges, missing


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-dir", default="_book", help="渲染产物目录（默认 _book）")
    parser.add_argument("--browser", action="store_true",
                        help="执行三档视口、明暗模式的完整浏览器矩阵")
    parser.add_argument("--verbose", action="store_true", help="展开浏览器测量指标")
    args = parser.parse_args()

    book_dir = Path(args.book_dir)
    if not book_dir.is_dir():
        print(f"BookDir not found: {book_dir}. Run 'quarto render' first.")
        return 1

    css_texts = [
        p.read_text(encoding="utf-8", errors="ignore")
        for p in sorted(book_dir.rglob("*.css"))
    ]
    # 源主题也纳入检索：共享令牌与活跃 palette 在渲染前即可核对
    theme_css_sources = [
        SHARED_TOKENS_CSS,
    ]
    quarto_text = QUARTO_YML.read_text(encoding="utf-8") if QUARTO_YML.is_file() else ""
    palette = active_palette_name(quarto_text)
    palette_tokens = None
    if palette:
        palette_tokens = PALETTE_ROOT / palette / "tokens.css"
        theme_css_sources.append(palette_tokens)
    source_css_texts = [
        p.read_text(encoding="utf-8", errors="ignore")
        for p in theme_css_sources
        if p.is_file()
    ]
    search_texts = css_texts + source_css_texts

    fail = 0
    if not palette or not palette_tokens or not palette_tokens.is_file():
        print("  MISS active palette tokens  (palettes/<name>/tokens.css in _quarto.yml)")
        fail += 1
    else:
        print(f"  OK   active palette `{palette}`  ({palette_tokens.as_posix()})")

    checks = list(SHARED_CHECKS) + list(TOKEN_NAME_CHECKS)
    checks.extend(PALETTE_VALUE_CHECKS.get(palette or "", []))
    for name, pattern in checks:
        found = any(pattern in text for text in search_texts)
        mark = "OK  " if found else "MISS"
        print(f"  {mark} {name}  ({pattern})")
        if not found:
            fail += 1

    callouts_css = (
        THEME_DIR / "assets" / "theme" / "css" / "callouts.css"
    ).read_text(encoding="utf-8")
    for name, pattern in CALLOUT_CHECKS:
        found = pattern in callouts_css
        mark = "OK  " if found else "MISS"
        print(f"  {mark} {name}  ({pattern})")
        if not found:
            fail += 1

    theme_texts = [
        p.read_text(encoding="utf-8", errors="ignore")
        for p in sorted((THEME_DIR / "assets" / "theme").rglob("*"))
        if p.suffix in {".css", ".scss"}
    ]
    theme_text = "\n".join(theme_texts)
    for name, pattern in FORBIDDEN_FONT_REFERENCES:
        found = pattern in theme_text
        mark = "MISS" if found else "OK  "
        print(f"  {mark} {name}  (forbidden)")
        if found:
            fail += 1

    legacy_font_files = sorted(
        p.name
        for pattern in ("inter-*", "noto-sans-sc-*", "jetbrains-mono-*")
        for p in FONT_DIR.glob(pattern)
    )
    print(f"  {'MISS' if legacy_font_files else 'OK  '} legacy font files removed")
    if legacy_font_files:
        print("       " + ", ".join(legacy_font_files))
        fail += 1

    font_asset_problems = check_font_assets(FONTS_CSS.read_text(encoding="utf-8"))
    print(
        f"  {'OK  ' if not font_asset_problems else 'MISS'} font asset set"
        f"  (Fixel=3, WenKai=1, Bright=1)"
    )
    for problem in font_asset_problems:
        print(f"       {problem}")
    if font_asset_problems:
        fail += 1

    font_partition_problems = check_font_partition(
        FONTS_CSS.read_text(encoding="utf-8")
    )
    print(
        f"  {'OK  ' if not font_partition_problems else 'MISS'} font partitions"
        "  (non-overlap when ranges are declared)"
    )
    for problem in font_partition_problems:
        print(f"       {problem}")
    if font_partition_problems:
        fail += 1

    ranges, missing = check_font_coverage(book_dir)
    coverage_ok = not any(missing.values())
    print(
        f"  {'OK  ' if coverage_ok else 'MISS'} CJK font coverage"
        f"  (declared-ranges={sum(map(len, ranges.values()))}, "
        f"missing={sum(map(len, missing.values()))})"
    )
    for family, chars in missing.items():
        if chars:
            print(f"       {family}: " + "".join(sorted(chars)[:20]))
    if not coverage_ok:
        fail += 1

    if args.browser:
        browser_problems, browser_note, browser_info = browser_layout(book_dir, args.verbose)
    else:
        browser_problems, browser_note, browser_info = [], "未请求浏览器矩阵（加 --browser 执行）", {}
    if browser_note and not browser_problems:
        print(f"  SKIP browser-layout  {browser_note}")
    else:
        print(
            f"  {'OK  ' if not browser_problems else 'MISS'} browser-layout"
            f"  (viewports=1280,768,390; schemes=light,dark; "
            f"mode={browser_info.get('mode', 'n/a')}; "
            f"pages={browser_info.get('pages', 0)})"
        )
        for problem in browser_problems:
            print(f"       {problem}")
        if browser_problems:
            fail += 1

    print()
    if fail == 0:
        if browser_note:
            print(f"PASS theme-static；SKIP browser-layout {browser_note}")
        else:
            print(
                "PASS theme-static；browser-layout "
                f"{browser_info.get('mode', 'full')} "
                f"{browser_info.get('pages', 0)} pages × 1280/768/390 × light/dark"
            )
        return 0
    print(f"{fail} theme check(s) failed; inspect the diagnostics above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
