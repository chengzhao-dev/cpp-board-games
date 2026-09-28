#!/usr/bin/env python3
"""按文档类型检查仓库 Markdown 与 QMD 的基础结构。

链接标签两侧空格（DOC-N10）与标签内反引号（DOC-E12）默认记为 NOTICE，
`--strict` 下升级为失败。空文件、空目录与关键工具标记始终作为错误。
"""

import argparse
import os
from pathlib import Path
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[4]
SKIP = {".git", "_book", ".quarto", "build", "node_modules"}
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
LINK_TEXT = re.compile(r"(?<!!)\[(?P<label>[^\]\n]+)\]\((?P<url>[^)\n]*)\)")
ANSWER_OPEN = re.compile(
    r"^(?P<indent>[ \t]*):::\s*\{(?P<attrs>[^}]*)\}\s*$"
)
ANSWER_CLASS = re.compile(r"(?:^|\s)\.answer(?:\s|$)")
ANSWER_CLOSE = re.compile(r"^[ \t]*:::\s*$")
RAW_ANSWER_DETAILS = re.compile(
    r"^(?P<indent>[ \t]*)<details\b(?P<attrs>[^>]*)>"
)
ORDERED_LIST = re.compile(r"^[ \t]*\d+[.)][ \t]+\S")
CJK = re.compile(r"[\u4e00-\u9fff]")
WIDE = re.compile(r"[\u3000-\u303f\uff00-\uffef]")
ASCII_EDGE = re.compile(r"[A-Za-z0-9_.+\-/]")
IMAGE = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
CALLOUT = re.compile(r"^\s*:::\s*\{\.callout-([\w-]+)(?:\s+[^}]*)?\}")
CALLOUT_OPEN = re.compile(r"^\s*:::\s*\{\.callout-[\w-]+(?:\s+[^}]*)?\}\s*$")
CALLOUT_CLOSE = re.compile(r"^\s*:::\s*$")
CALLOUTS = {"note", "tip", "warning", "important", "caution"}
CODE_EXTENSIONS = {".cpp", ".cc", ".cxx", ".h", ".hpp", ".cmake", ".sh", ".bash"}
CODE_NAMES = {"CMakeLists.txt"}
CODE_LANGUAGES = {"cpp", "c", "bash", "sh", "shell", "powershell", "ps1", "cmake", "text", "markdown", "yaml", "json", "toml", "mermaid"}
SHELL_LANGUAGES = {"bash", "sh", "shell"}
POWERSHELL_LANGUAGES = {"powershell", "ps1"}
TARGET_CREATION = re.compile(r"^\s*(add_executable|add_library)\s*\(")
INLINE_TOOLS = ()
TOOL_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_+.-])(%s)(?![A-Za-z0-9_+.-])"
    % "|".join(map(re.escape, INLINE_TOOLS))
)


def parse_fence_info(info):
    """解析普通语言围栏与 Quarto/Pandoc 属性围栏。"""
    info = info.strip()
    if not info:
        return "", {}, None
    if not info.startswith("{"):
        return info.split()[0], {}, None
    if not info.endswith("}"):
        return "", {}, f"属性围栏缺少右花括号：{info}"
    try:
        tokens = shlex.split(info[1:-1])
    except ValueError as exc:
        return "", {}, f"属性围栏无法解析：{exc}"
    language = ""
    attributes = {}
    for token in tokens:
        if token.startswith(".") and not language:
            language = token[1:]
            continue
        if "=" in token:
            key, value = token.split("=", 1)
            attributes[key] = value.strip("\"'")
            continue
        if not language:
            language = token
    return language, attributes, None


def documents():
    paths = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "index.qmd"]
    for folder in ("content", ".agents/skills", ".agents/knowledge"):
        base = ROOT / folder
        if base.is_dir():
            paths.extend(base.rglob("*.qmd" if folder == "content" else "*.md"))
    return sorted(p for p in set(paths) if p.is_file() and not any(x in p.parts for x in SKIP))


def doc_kind(path):
    if path.name == "README.md":
        return "readme"
    if path.name == "AGENTS.md":
        return "agents"
    if path.suffix == ".qmd":
        return "qmd"
    return "md"


def local_path(path, value):
    value = value.split("#", 1)[0].split("?", 1)[0].strip("<>")
    if not value or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        return None
    candidate = (path.parent / value).resolve()
    if candidate.exists():
        return candidate
    if Path(value).name == "AGENTS.md":
        return (ROOT / "AGENTS.md").resolve()
    return candidate


def inline_code_spans(line):
    """行内代码的字符区间，用于跳过代码块式文本里的伪链接。"""
    spans, index, length = [], 0, len(line)
    while index < length:
        if line[index] != "`":
            index += 1
            continue
        marker_end = index
        while marker_end < length and line[marker_end] == "`":
            marker_end += 1
        fence = "`" * (marker_end - index)
        close = line.find(fence, marker_end)
        while close != -1 and close + len(fence) < length and line[close + len(fence)] == "`":
            close = line.find(fence, close + len(fence))
        if close == -1:
            index = marker_end
            continue
        spans.append((index, close + len(fence)))
        index = close + len(fence)
    return spans


def in_spans(spans, position):
    return any(start <= position < end for start, end in spans)


def label_edge(label):
    """按标签内第一个/最后一个可见字符分类：ascii / code / cjk / other。"""
    stripped = label.strip()
    plain = stripped.strip("`")
    if not plain:
        return "code", "code"

    def kind(char, marked):
        if ASCII_EDGE.fullmatch(char):
            return "ascii"
        if marked:
            return "code"
        if CJK.fullmatch(char):
            return "cjk"
        return "other"

    return (kind(plain[0], stripped.startswith("`")),
            kind(plain[-1], stripped.endswith("`")))


def check_link_spacing(rel, lines, blocks):
    """链接标签两侧的空格与标签内反引号，判定只看标签首尾可见字符。"""
    errors, notices = [], []
    fenced = set()
    for start, end, _info in blocks:
        fenced.update(range(start, end + 1))
    front_end = 0
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                front_end = index + 1
                break
    for number, line in enumerate(lines, 1):
        if number <= front_end or number in fenced or line.lstrip().startswith("#"):
            continue
        spans = inline_code_spans(line)
        for match in LINK_TEXT.finditer(line):
            if in_spans(spans, match.start()) or in_spans(spans, match.start() - 1):
                continue
            label, url = match.group("label"), match.group("url")
            if not label.strip() or url.startswith("<"):
                continue
            first, last = label_edge(label)
            previous = line[match.start() - 1:match.start()]
            before = line[match.start() - 2:match.start() - 1]
            after = line[match.end():match.end() + 1]
            following = line[match.end() + 1:match.end() + 2]
            short = label.strip()[:20]
            if "`" in label:
                errors.append(f"{rel}:{number}: DOC-E12 链接标签内不要使用反引号：{short}")
            if previous == " ":
                if first == "cjk" and (not before or CJK.fullmatch(before) or WIDE.fullmatch(before)):
                    notices.append(f"{rel}:{number}: DOC-N10 中文链接标签前多余空格：{before}[ {short}")
                elif before and WIDE.fullmatch(before):
                    notices.append(f"{rel}:{number}: DOC-N10 全角标点后多余空格：{before}[ {short}")
            elif previous and CJK.fullmatch(previous) and first in {"ascii", "code"}:
                notices.append(f"{rel}:{number}: DOC-N10 英文链接标签前缺空格：{previous}[{short}")
            if after == " " and following and CJK.fullmatch(following) and last == "cjk":
                notices.append(f"{rel}:{number}: DOC-N10 中文链接标签后多余空格：{short}] {following}")
            elif after and CJK.fullmatch(after) and last in {"ascii", "code"}:
                notices.append(f"{rel}:{number}: DOC-N10 英文链接标签后缺空格：{short}]{after}")
    return errors, notices


def check_callout_placement(rel, lines):
    """检查正文 Callout 是否是任务末尾的独立块。"""
    errors = []
    in_fence = False
    opening_line = None
    for index, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if opening_line is None:
            if not CALLOUT_OPEN.match(line):
                continue
            if index and lines[index - 1].strip():
                errors.append(f"{rel}:{index + 1}: DOC-E13 Callout 前必须留空行")
            opening_line = index + 1
            continue
        if not CALLOUT_CLOSE.match(line):
            continue
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        if index + 1 < len(lines) and lines[index + 1].strip():
            errors.append(f"{rel}:{index + 1}: DOC-E13 Callout 后必须留空行")
        if next_index < len(lines) and not HEADING.match(lines[next_index]):
            errors.append(f"{rel}:{opening_line}: DOC-E13 Callout 必须是当前任务的最后一个信息块")
        opening_line = None
    if opening_line is not None:
        errors.append(f"{rel}:{opening_line}: DOC-E13 Callout 未闭合")
    return errors


def has_html_class(attrs, name):
    """Return whether an HTML attribute string contains one class token."""
    match = re.search(
        r"""\bclass\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""",
        attrs,
        re.IGNORECASE,
    )
    if not match:
        return False
    value = next(group for group in match.groups() if group is not None)
    return name in value.split()


def find_answer_close(lines, start):
    """Find the matching fenced-div close, ignoring fenced code and nested divs."""
    depth = 1
    in_fence = False
    fence_char = ""
    fence_size = 0
    for candidate in range(start + 1, len(lines)):
        fence = FENCE.match(lines[candidate])
        if fence:
            marker, _info = fence.groups()
            if not in_fence:
                in_fence, fence_char, fence_size = True, marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                in_fence = False
            continue
        if in_fence:
            continue
        if ANSWER_CLOSE.match(lines[candidate]):
            depth -= 1
            if depth == 0:
                return candidate
        elif re.match(r"^[ \t]*:::\s*\S", lines[candidate]):
            depth += 1
    return None


def check_answer_disclosures(rel, lines):
    """检查可折叠答案使用站点组件、位于列表内并正常闭合。"""
    errors = []
    index = 0
    in_fence = False
    fence_char = ""
    fence_size = 0
    while index < len(lines):
        fence = FENCE.match(lines[index])
        if fence:
            marker, _info = fence.groups()
            if not in_fence:
                in_fence, fence_char, fence_size = True, marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                in_fence = False
            index += 1
            continue
        if in_fence:
            index += 1
            continue

        raw_match = RAW_ANSWER_DETAILS.match(lines[index])
        if raw_match and has_html_class(raw_match.group("attrs"), "answer-disclosure"):
            errors.append(
                f"{rel}:{index + 1}: DOC-E18 可折叠答案必须使用 ::: {{.answer}} 组件"
            )
            index += 1
            continue

        match = ANSWER_OPEN.match(lines[index])
        if not match or not ANSWER_CLASS.search(match.group("attrs")):
            index += 1
            continue

        line_number = index + 1
        if len(match.group("indent").expandtabs(4)) < 3:
            errors.append(f"{rel}:{line_number}: DOC-E18 可折叠答案必须缩进在对应列表项下")
        closing = find_answer_close(lines, index)
        if closing is None:
            errors.append(f"{rel}:{line_number}: DOC-E18 可折叠答案缺少结束标记 :::")
            break
        content = [
            (candidate, line)
            for candidate, line in enumerate(lines[index + 1:closing], index + 1)
            if line.strip()
        ]
        for content_index, content_line in content:
            if len(content_line[: len(content_line) - len(content_line.lstrip())]
                   .expandtabs(4)) < 3:
                errors.append(
                    f"{rel}:{content_index + 1}: DOC-E18 "
                    "可折叠答案正文必须与 ::: 保持相同缩进"
                )
        if not content:
            errors.append(f"{rel}:{line_number}: DOC-E18 可折叠答案不能为空")
        elif ORDERED_LIST.match(content[0][1]):
            errors.append(
                f"{rel}:{line_number}: DOC-E19 列表型答案必须以导语开头，"
                "先说明对象、起止范围或顺序"
            )
        index = closing + 1
    return errors


def heading_level_errors(rel, headings):
    """检查标题是否超过三级。headings 每项为 (行号, 层级, 标题)。"""
    return [
        f"{rel}:{number}: DOC-E21 文档标题最多到三级标题，禁止 H4 及更深标题"
        for number, level, _title in headings
        if level >= 4
    ]


def frontmatter_title_errors(rel, lines):
    """检查 YAML front matter 的 title 是否使用反引号。"""
    if not lines or lines[0].strip() != "---":
        return []
    errors = []
    for number, line in enumerate(lines[1:], 2):
        if line.strip() == "---":
            break
        if re.match(r"^title\s*:", line) and "`" in line:
            errors.append(f"{rel}:{number}: DOC-E2 标题不应使用反引号")
    return errors


def check(path):
    rel = path.relative_to(ROOT).as_posix()
    errors, notices = [], []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{rel}: DOC-E1 非 UTF-8"], []
    kind = doc_kind(path)
    in_fence = False
    fence_char = ""
    fence_size = 0
    fence_start = 0
    fence_info = ""
    headings = []
    blocks = []
    callout_section = None
    callout_counts = {}
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        match = FENCE.match(line)
        if match:
            marker, info = match.groups()
            if not in_fence:
                in_fence, fence_char, fence_size = True, marker[0], len(marker)
                fence_start, fence_info = number, info.strip()
            elif marker[0] == fence_char and len(marker) >= fence_size:
                blocks.append((fence_start, number, fence_info))
                in_fence = False
            continue
        if not in_fence:
            heading = HEADING.match(line)
            if heading:
                headings.append((number, len(heading.group(1)), heading.group(2)))
                if len(heading.group(1)) <= 3:
                    callout_section = number
                if kind in {"qmd", "readme", "agents"} and "`" in heading.group(2):
                    errors.append(f"{rel}:{number}: DOC-E2 标题不应使用反引号")
                elif "`" in heading.group(2):
                    notices.append(f"{rel}:{number}: DOC-N4 标题含反引号，请确认是否便于检索")
                if (
                    kind == "qmd"
                    and rel.startswith("content/")
                    and not rel.endswith("/index.qmd")
                    and len(heading.group(1)) == 1
                ):
                    errors.append(f"{rel}:{number}: DOC-E15 普通章节标题只由 YAML title 提供，正文禁止 H1")
            callout = CALLOUT.match(line)
            if callout and callout.group(1) not in CALLOUTS:
                errors.append(f"{rel}:{number}: DOC-E3 callout 类型不受支持")
            elif CALLOUT_OPEN.match(line):
                callout_counts[callout_section] = callout_counts.get(callout_section, 0) + 1
                if callout_counts[callout_section] > 1:
                    errors.append(f"{rel}:{number}: DOC-E16 同一任务最多保留一个 Callout")
    if in_fence:
        errors.append(f"{rel}:{fence_start}: DOC-E4 代码围栏未闭合")
    errors.extend(frontmatter_title_errors(rel, lines))
    errors.extend(heading_level_errors(rel, headings))
    if kind == "qmd" and rel.startswith("content/"):
        errors.extend(check_answer_disclosures(rel, lines))
        errors.extend(check_callout_placement(rel, lines))
    previous = 0
    for number, level, _title in headings:
        if previous and level > previous + 1:
            errors.append(f"{rel}:{number}: DOC-E5 标题层级跳跃")
        previous = level
    for (_previous_start, previous_end, _previous_info), (start, _end, _info) in zip(
        blocks, blocks[1:]
    ):
        if start == previous_end + 1:
            errors.append(f"{rel}:{start}: DOC-E11 相邻代码块之间应保留一个空行")
    for start, end, info in blocks:
        language, attributes, parse_error = parse_fence_info(info)
        if parse_error:
            errors.append(f"{rel}:{start}: DOC-E14 {parse_error}")
        body = "\n".join(lines[start:end - 1])
        if kind == "qmd":
            if language and language != "mermaid" and not attributes.get("filename"):
                errors.append(
                    f"{rel}:{start}: DOC-E14 站点 QMD 代码块必须用 filename 属性标明来源或运行环境"
                )
            if language == "mermaid" and not info.startswith("{mermaid}"):
                errors.append(f"{rel}:{start}: DOC-E6 Mermaid 必须使用 {{mermaid}} 围栏")
            if language and language not in CODE_LANGUAGES:
                notices.append(f"{rel}:{start}: DOC-N5 未登记的代码块语言 {language}，请确认高亮器支持")
            block_lines = body.splitlines()
            if language == "text" and any(
                re.match(r"^\s*(?:\$ |PS>)", line) for line in block_lines
            ):
                errors.append(f"{rel}:{start}: DOC-E7 text 代码块不能包含命令提示符")
            if language in SHELL_LANGUAGES | POWERSHELL_LANGUAGES:
                if any(re.match(r"^\s*(?:\$\s+|PS>)", line) for line in block_lines):
                    errors.append(
                        f"{rel}:{start}: DOC-E7 命令围栏不应使用 $ 或 PS> 提示符，命令直接左对齐"
                    )
            if re.search(r"\*\*|(?<!\*)\*(?!\*)", body):
                notices.append(f"{rel}:{start}: DOC-N1 代码块含强调符号，请人工确认")
            if language in SHELL_LANGUAGES | POWERSHELL_LANGUAGES:
                commands = [
                    re.sub(r"^\s*(?:\$\s+|PS>\s+)", "", line).strip()
                    for line in block_lines
                    if line.strip() and not line.lstrip().startswith("#")
                ]
                if len(commands) <= 2 and all(command in {"wsl", "wsl ~"} for command in commands):
                    notices.append(f"{rel}:{start}: DOC-N9 短命令可直接融入正文，无需单独代码块")
        elif kind in {"md", "agents"} and language == "mermaid":
            notices.append(f"{rel}:{start}: DOC-N2 说明文档默认不使用 Mermaid")
    if kind in {"md", "agents"}:
        for number, line in enumerate(lines, 1):
            if re.match(r"^\s*(?:!\[|<img\b)", line):
                notices.append(f"{rel}:{number}: DOC-N3 说明文档图片需确认信息价值")
    for match in IMAGE.finditer(text):
        if not match.group(1).strip():
            errors.append(f"{rel}: DOC-E8 图片缺少替代文字")
        target = local_path(path, match.group(2))
        if target and not target.is_file() and kind != "readme":
            errors.append(f"{rel}: DOC-E9 图片不存在：{match.group(2)}")
    for match in LINK.finditer(text):
        target = local_path(path, match.group(1))
        if target and not target.exists():
            errors.append(f"{rel}: DOC-E10 本地链接不存在：{match.group(1)}")
    colon_count = sum(line.count("：") for line in lines if line.strip() and not line.lstrip().startswith(("#", "-", "```")))
    if colon_count >= 8:
        notices.append(f"{rel}: DOC-N6 正文冒号较密，请确认是否可改为完整句子")
    spacing_errors, spacing_notices = check_link_spacing(rel, lines, blocks)
    errors.extend(spacing_errors)
    notices.extend(spacing_notices)
    return errors, notices


def has_purpose_comment(path, lines):
    """检查首个有效行是否用原生注释说明文件用途。"""
    suffix = path.suffix.lower()
    start = 1 if suffix in {".sh", ".bash"} and lines and lines[0].startswith("#!") else 0
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            continue
        if suffix in {".cpp", ".cc", ".cxx", ".h", ".hpp"}:
            return stripped.startswith("//")
        if suffix in {".sh", ".bash", ".cmake"} or path.name == "CMakeLists.txt":
            return stripped.startswith("#")
        return True
    return False


def cmake_target_comment_errors(path, lines):
    """检查 CMake 目标创建命令是否紧邻一条职责注释。"""
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    for index, line in enumerate(lines):
        if not TARGET_CREATION.match(line):
            continue
        previous = index - 1
        if previous < 0 or not lines[previous].lstrip().startswith("#"):
            errors.append(
                f"{rel}:{index + 1}: DOC-E22 创建目标前必须用独立注释说明目标职责"
            )
    return errors


def check_source(path):
    """检查会被 include 的源文件，重点发现缺少用途注释和过长解释。"""
    rel = path.relative_to(ROOT).as_posix()
    errors, notices = [], []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return [f"{rel}: DOC-E1 非 UTF-8"], []
    if not has_purpose_comment(path, lines):
        errors.append(f"{rel}: DOC-E20 首个有效行需用原生注释说明文件用途")
    if path.name == "CMakeLists.txt":
        errors.extend(cmake_target_comment_errors(path, lines))
    for number, line in enumerate(lines, 1):
        if re.search(r"\S\s+#\s+[^#]", line) and path.suffix.lower() in {".sh", ".bash"}:
            notices.append(f"{rel}:{number}: DOC-N7 行尾 Shell 注释请移到被说明代码的上一行")
        if re.search(r"\S\s+//\s+", line) and path.suffix.lower() in {".cpp", ".cc", ".cxx", ".h", ".hpp"}:
            notices.append(f"{rel}:{number}: DOC-N7 行尾 C++ 注释请移到被说明代码的上一行")
        if len(line) > 110 and line.lstrip().startswith(("#", "//")):
            notices.append(f"{rel}:{number}: DOC-N8 注释过长，请移到正文或拆成短句")
        if re.match(r"^\s*(?:wsl(?:\s+~)?|wsl\s+--(?:shutdown|terminate)\b)", line) and number > 1:
            previous = lines[number - 2].strip()
            if previous and not previous.startswith("#"):
                notices.append(f"{rel}:{number}: DOC-N9 关键命令前可补一条简短注释，说明本节学习重点")
    return errors, notices


def empty_path_errors():
    """返回受管目录中的空文件和空目录。

    只遍历内容、代码、skills 和 knowledge 四个受管根，避免把 temp、构建缓存
    或宿主工具目录混进文档校验。每个根都原地跳过产物目录，成本随受管文件数增长。
    Quarto 渲染单页时会在源码旁生成 `<name>_files/` 产物目录（含空的 mediabag），
    与 `_book/` 同属渲染产物，不入库也不参与校验。
    """
    skip = {".git", "_book", ".quarto", ".cache", ".tmp", "build", "temp"}
    rows = []
    roots = (
        ROOT / "content",
        ROOT / "games",
        ROOT / "shared",
        ROOT / ".agents" / "skills",
        ROOT / ".agents" / "knowledge",
    )
    for managed in roots:
        if not managed.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(managed):
            dirnames[:] = [
                name for name in dirnames if name not in skip and not name.endswith("_files")
            ]
            current = Path(dirpath)
            if current != managed and not dirnames and not filenames:
                rows.append(f"{current.relative_to(ROOT).as_posix()}: DOC-E23 空目录")
            for name in filenames:
                path = current / name
                if path.stat().st_size == 0:
                    rows.append(f"{path.relative_to(ROOT).as_posix()}: DOC-E23 空文件")
    return rows


def inline_code_errors():
    """检查教学正文中的关键工具是否使用行内代码。"""
    rows = []
    if not INLINE_TOOLS:
        return rows
    for path in sorted((ROOT / "content").rglob("*.qmd")):
        rel = path.relative_to(ROOT).as_posix()
        in_fence = False
        in_frontmatter = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if number == 1 and line.strip() == "---":
                in_frontmatter = True
                continue
            if in_frontmatter:
                if line.strip() == "---":
                    in_frontmatter = False
                continue
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence or line.lstrip().startswith("#"):
                continue
            clean = re.sub(r"`[^`]*`", "", line)
            clean = re.sub(r"\[[^\]]*\]\([^)]*\)", "", clean)
            for token in TOOL_TOKEN.findall(clean):
                rows.append(f"{rel}:{number}: DOC-E24 {token} 应使用反引号")
    return rows


def main():
    parser = argparse.ArgumentParser(description="文档结构检查")
    parser.add_argument("--strict", action="store_true",
                        help="把链接间距等软规则升级为失败")
    parser.add_argument("--verbose", action="store_true", help="展开全部 NOTICE")
    args = parser.parse_args()
    errors, notices = [], []
    paths = documents()
    for path in paths:
        found_errors, found_notices = check(path)
        errors.extend(found_errors)
        notices.extend(found_notices)
    source_paths = sorted(
        p for base in (
            ROOT / "games",
            ROOT / "shared",
        )
        if base.is_dir() for p in base.rglob("*")
        if p.is_file() and (p.suffix.lower() in CODE_EXTENSIONS or p.name in CODE_NAMES)
        and not any(part in SKIP for part in p.parts)
    )
    for path in source_paths:
        found_errors, found_notices = check_source(path)
        errors.extend(found_errors)
        notices.extend(found_notices)
    errors.extend(empty_path_errors())
    errors.extend(inline_code_errors())
    if args.strict:
        soft = [n for n in notices if "DOC-N10" in n]
        notices = [n for n in notices if "DOC-N10" not in n]
        errors.extend(n + "（--strict 视为失败）" for n in soft)
    for notice in notices:
        print("NOTICE " + notice)
    if errors:
        print("FAIL docs")
        for error in errors:
            print("  " + error)
        return 1
    print(f"PASS docs 结构、空路径与关键工具标记（{len(paths)} 个文档）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
