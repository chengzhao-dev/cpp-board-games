#!/usr/bin/env python3
#===------------------------------------------------------------------------===#
# verify_content.py - content 侧写作规范自动检查
#
# 检查 qmd 禁用词、代码片段与源文件的一致性、篇幅预算（含正文段落长度，
# 链接 URL 不计入）以及渲染后的 HTML。在仓库根目录执行；优先用根目录
# config.toml 的 python 完整路径启动，例如：
#   D:/ProgramData/miniforge3/python.exe .agents/skills/writing-quarto/scripts/verify_content.py
# 任意 ≥3.11 的 Python 也可作启动器：脚本读 config.toml 后 exec 到受控
# 解释器；配置缺失或路径不存在立即失败，不回退 PATH。只用标准库；
# 任何一项失败时退出码为 1。
#
# 范围参数（降 token：按改动集检查，避免无差别整仓读入）：
#   --book       扫描 _book/**/*.html 渲染产物；默认不扫，渲染检查交由
#                run.py check --profile book 或本参数显式触发
#   --paths ...  只检查指定 qmd 文件或目录（相对仓库根）
#   --changed    只检查 git 工作区改动的 qmd（相对 HEAD）
#===------------------------------------------------------------------------===#

import argparse
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

#===------------------------------------------------------------------------===#
# 检查配置
#===------------------------------------------------------------------------===#

# content 侧停用的统称与写法；新增禁用词时在这里追加。
FORBIDDEN_TERMS = [
    "第一版", "探针", "阶段", "切片", "自足", "{{< include",
    "链路", "四步", "片段：", "「", "」",
    "这条路线", "这条流程", "这套流程", "下面分别精读", "如下分别说明",
    "刻意保持", "只可能", "不可能来自",
    "只包含",
    "读懂", "务必", "严禁", "千万不要", "千万别",
    # 语气与语域（规则见标识 bg-chinese-voice-register-v1 的知识文件）：
    # 口语讲义腔与规划元叙述套话。
    "动手前", "弄清", "咱们", "搞定", "别慌",
    "本章规划", "落点是", "类型名只是设计方向",
    # 书面腔动词、倒装强调与元标签开场（规则见标识 bg-terminology-v1、
    # bg-paragraph-cohesion-v1 的知识文件）。
    "标明", "跑通", "重读", "这正是", "容易混淆",
    # 测试语境混用与压缩表述（规则见标识 bg-terminology-v1 的知识文件）。
    "接口桩", "静态到动态",
]

# 词表表达不了的句式用正则：编号指称、统计性凑句与旧片段标注
# （规则见标识 bg-terminology-v1、bg-paragraph-list-style-v1 与
# bg-qmd-element-cases-v1 的知识文件）。
FORBIDDEN_PATTERNS = [
    (r"第 \d+ 章", "第 N 章式编号指称"),
    (r"(?:文件|代码).{0,6}只有.{0,6}\d+\s*行", "统计性凑句"),
    (r'filename="片段：', "filename 片段前缀"),
    (r"（第 \d+(-\d+)? 行）", "filename 行号标注"),
    # filename 值中的全角括号仅限执行位置标注（WSL Ubuntu（仓库根目录）等）；
    # 样式说明（如「运行效果（终端中步骤标题为青色加粗）」）写进正文。
    (r'filename="(?!WSL Ubuntu)[^"]*（', "filename 全角括号仅限执行位置标注"),
    # 标题栏只用短名；深层 games/、shared/ 路径由正文 GitHub 链接提供
    # （规则见标识 bg-qmd-element-cases-v1 的知识文件）。
    (r'filename="(?:games|shared)/', "filename 深层路径（改用短名）"),
    # 元计数导语（规则见标识 bg-chinese-style-cases-v1）。
    (r"\d+段命令", "N 段命令式元计数导语"),
    # 渐进披露元叙述（规则见标识 bg-qmd-element-cases-v1、
    # bg-terminology-v1 的知识文件）：写作策略不念给读者听。
    (r"语法细节留到", "渐进披露元叙述（直接陈述对象和结果）"),
    (r"真正用到时再", "渐进披露元叙述（直接陈述对象和结果）"),
    (r"本章只需认清", "渐进披露元叙述（直接陈述对象和结果）"),
    # 操作节离题辩白（规则见标识 bg-paragraph-cohesion-v1、
    # 对照见 bg-chinese-style-cases-v1）：「为何不跳过/幂等」长论不进操作正文。
    (r"配置漂移", "操作节离题辩白（删除或归属排查节）"),
    # 强语气「绝对…」（不拦技术词「绝对链接」）。
    (r"绝对(?:不要|不能|禁止|必须|不行)", "强语气绝对（改可核对条件句）"),
    # Mermaid 图表必须用 {mermaid} 属性围栏（规则见标识
    # bg-mermaid-conventions-v1 的知识文件）：plain 围栏被当作代码块。
    (r"^```mermaid\b", "plain mermaid 围栏（改用 {mermaid}）"),
    # 编号旁注（规则见标识 bg-chapter-page-pattern-v1 的知识文件）：
    # 目录与章节的编号差只在渐进式路线章说明。
    (r"目录编号比章节", "编号旁注（编号差只在渐进式路线章说明）"),
]
FORBIDDEN_RES = [(re.compile(pattern), label) for pattern, label in FORBIDDEN_PATTERNS]

# 规划页标记与行内代码路径：含标记的页面是实现目录未创建的设计页，
# 实现目录一律用中文锚文本 GitHub 链接（规则见标识
# bg-chapter-page-pattern-v1 的知识文件）。
PLANNING_MARKER = "实现并通过验收前按设计页阅读"
PLANNING_INLINE_PATH_RE = re.compile(r"`(?:games|shared)/[^`]+`")

# 渲染 HTML 只查黑话与 include 残留；直角引号交给 qmd 层检查，
# 避免主题资源里的全角符号造成误报。
HTML_FORBIDDEN_TERMS = FORBIDDEN_TERMS[: FORBIDDEN_TERMS.index("「")]

# 片段代码块：filename 为短显示名；真实路径由同节 GitHub blob 链接解析。
# 目录树、运行效果和执行位置块跳过。
FRAGMENT_RE = re.compile(r'^```\{\.(\w+) filename="([^"]+)"\}\s*$')
FRAGMENT_SOURCE_PREFIXES = ("games/", "shared/")
GITHUB_BLOB_RE = re.compile(
    r"https://github\.com/[^/]+/[^/]+/blob/[^/]+/"
    r"((?:games|shared)/[^)\s]+)"
)
HEADING_RE = re.compile(r"^(#{2,3})\s+")

# 省略标记行（strip 后精确匹配）：片段比对时跳过；在源码语言围栏内出现
# 即报错（省略处直接省略；输出摘录块的 ... 不受限，.text 不在 CODE_LANGS 内）。
OMISSION_LINES = ("...", "# ...", "// ...")

# Markdown 链接在预算计数前剥离 URL：URL 是机器寻址串，读者扫读时整体
# 跳过，计入会挤占正文预算（口径见标识 bg-content-budget-v1 的知识文件）。
# 锚文本保留照常计数。
LINK_URL_RES = [
    re.compile(r"\]\([^)\s]*https?://[^)\s]*\)"),
    re.compile(r"<https?://[^>\s]+>"),
]


def strip_link_urls(text: str) -> str:
    for pattern in LINK_URL_RES:
        text = pattern.sub("]()", text)
    return text

REPO_ROOT = Path(__file__).resolve().parents[4]
CONTENT_GLOBS = ["content/**/*.qmd", "index.qmd"]
AGENTS_MD_GLOBS = [".agents/skills/**/*.md", ".agents/knowledge/**/*.md"]
AGENTS_BODY_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
MIN_PYTHON = (3, 11)

# 篇幅预算限额（计数口径与限额表见标识 bg-content-budget-v1 的知识文件，
# 两处必须同步）。
CJK_RE = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f]")
FILE_TOKENS = 5000
INTRO_TOKENS = 400
H2_TOKENS = 1800
H3_TOKENS = 600
H3_COUNT = 4
BLOCK_LINES = 20
# 单个正文段落 token 上限（与 bg-content-budget-v1 限额表同步）。
PARA_TOKENS = 220
COMMENT_RUN = 2
CODE_LANGS = {"cpp", "cmake", "bash", "sh", "python", "jsonc"}
FRONTMATTER_RE = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n?", re.DOTALL)

#===------------------------------------------------------------------------===#
# 受控解释器（与 cpp-notes 同款约定：只认 config.toml，不回退 PATH）
#===------------------------------------------------------------------------===#

def to_form(path: Path, form: str) -> str:
    """在 Windows 与 WSL 路径形态间转换：D:/a/b <-> /mnt/d/a/b。"""
    text = str(path).replace("\\", "/")
    drive = re.match(r"^([A-Za-z]):/(.*)$", text)
    mount = re.match(r"^/mnt/([A-Za-z])/(.*)$", text)
    if form == "posix" and drive:
        return f"/mnt/{drive.group(1).lower()}/{drive.group(2)}"
    if form == "win" and mount:
        return f"{mount.group(1).upper()}:/{mount.group(2)}"
    return text


def reexec_under_configured_python() -> None:
    """统一用 config.toml 的 python 运行本脚本；配置缺失或不可用立即失败。

    已由受控解释器运行时原样继续，否则 exec 到受控解释器重新启动。
    """
    try:
        import tomllib
    except ImportError:
        print("失败  启动脚本需要 Python >= 3.11（tomllib）；请更新 config.toml 的解释器")
        raise SystemExit(1)
    try:
        config = tomllib.loads((REPO_ROOT / "config.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        print("失败  无法读取根目录 config.toml；请修复 python 字段")
        raise SystemExit(1)
    configured = str(config.get("python") or "").strip()
    if not configured:
        print("失败  config.toml 未配置 python 字段")
        raise SystemExit(1)

    if re.match(r"^[A-Za-z]:/", configured):
        target_form = "win"
    elif configured.startswith("/mnt/"):
        target_form = "posix"
    else:
        target_form = "win" if os.name == "nt" else "posix"

    if target_form == "posix" and os.name == "nt":
        print("失败  config.toml 的 python 是 WSL 路径；请在 WSL 中运行本脚本")
        raise SystemExit(1)

    # 在 WSL 中启动 Windows 解释器时，exec 用 /mnt 形态，脚本参数用 Windows 形态
    os_path = to_form(Path(configured), "posix" if os.name == "posix" else "win")
    if not Path(os_path).is_file():
        print(f"失败  config.toml 的解释器不存在: {configured}")
        raise SystemExit(1)
    if os.path.normcase(os_path) == os.path.normcase(sys.executable):
        return
    script_arg = to_form(Path(__file__).resolve(), target_form)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    os.execve(os_path, [os_path, script_arg, *sys.argv[1:]], env)

#===------------------------------------------------------------------------===#
# 输出辅助
#===------------------------------------------------------------------------===#

use_color = (
    sys.stdout.isatty()
    and not os.environ.get("NO_COLOR")
    and os.environ.get("TERM") != "dumb"
)
CYAN = "\033[1;36m" if use_color else ""
RED = "\033[1;31m" if use_color else ""
RESET = "\033[0m" if use_color else ""


def header(number: int, title: str) -> None:
    print(f"\n{CYAN}==> {number}. {title}{RESET}")


#===------------------------------------------------------------------------===#
# 检查 1：禁用词扫描
#===------------------------------------------------------------------------===#

def scan_qmd_forbidden(qmd_files):
    """扫描给定 qmd 文件，返回 [(文件, 行号, 词)]。"""
    findings = []
    for path in qmd_files:
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for term in FORBIDDEN_TERMS:
                if term in line:
                    findings.append((path, lineno, term))
            for pattern, label in FORBIDDEN_RES:
                if pattern.search(line):
                    findings.append((path, lineno, label))
    return findings


def scan_planning_inline_paths(qmd_files):
    """规划页禁用行内代码路径，返回 [(文件, 行号, 摘录)]。"""
    findings = []
    for path in qmd_files:
        text = path.read_text(encoding="utf-8")
        if PLANNING_MARKER not in text:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if PLANNING_INLINE_PATH_RE.search(line):
                findings.append((path, lineno, line.strip()[:80]))
    return findings


def body_without_frontmatter(text: str) -> str:
    """去掉开头 YAML frontmatter，只返回正文（供 agents 日期戳扫描）。"""
    match = FRONTMATTER_RE.match(text)
    return text[match.end() :] if match else text


def changed_qmd_paths():
    """返回 git 工作区相对 HEAD 改动的 qmd 路径；git 不可用时立即失败。"""
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z"], cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if proc.returncode != 0:
        print(f"失败  git status 不可用：{proc.stdout.decode('utf-8', errors='replace').strip()}")
        raise SystemExit(1)
    paths, items = [], proc.stdout.decode("utf-8", errors="replace").split("\0")
    index = 0
    while index < len(items):
        item = items[index]
        if not item or len(item) < 4:
            index += 1
            continue
        status, path = item[:2], item[3:].strip('"').replace("\\", "/")
        if "R" in status or "C" in status:
            index += 1  # 跳过 rename 的原始路径字段
        index += 1
        if not path.endswith(".qmd"):
            continue
        candidate = REPO_ROOT / path
        if candidate.is_file():
            paths.append(candidate)
    return sorted(set(paths))


def resolve_qmd_paths(args):
    """返回待检查的 qmd 路径：--paths/--changed 缩小范围，默认全量。

    缩小范围只作用于 qmd 相关检查（禁用词、规划页路径、片段、篇幅）；
    agents 正文日期戳始终全量，成本可忽略。
    """
    if args.paths:
        files = []
        for raw in args.paths:
            path = Path(raw)
            if not path.is_absolute():
                path = REPO_ROOT / path
            path = path.resolve()
            if REPO_ROOT.resolve() not in path.parents and path != REPO_ROOT.resolve():
                print(f"失败  --paths 路径超出仓库范围: {raw}")
                raise SystemExit(1)
            if path.is_dir():
                files.extend(sorted(path.rglob("*.qmd")))
            elif path.is_file():
                files.append(path)
            else:
                print(f"失败  --paths 路径不存在: {raw}")
                raise SystemExit(1)
        return sorted(set(files))
    if args.changed:
        return changed_qmd_paths()
    return sorted(
        path for pattern in CONTENT_GLOBS for path in REPO_ROOT.glob(pattern)
    )


def scan_agents_body_dates():
    """扫描 .agents/skills 与 .agents/knowledge 正文中的 YYYY-MM-DD。

    frontmatter 的 created/updated 允许保留；正文命中即记为发现项。
    返回 [(文件, 行号, 摘录)]。
    """
    findings = []
    md_files = sorted(
        path for pattern in AGENTS_MD_GLOBS for path in REPO_ROOT.glob(pattern)
    )
    for path in md_files:
        text = path.read_text(encoding="utf-8")
        body = body_without_frontmatter(text)
        # 计算 frontmatter 占用的行数，使报错行号对齐原文件。
        offset = text[: len(text) - len(body)].count("\n")
        for lineno, line in enumerate(body.splitlines(), start=1):
            if AGENTS_BODY_DATE_RE.search(line):
                findings.append((path, offset + lineno, line.strip()[:80]))
    return md_files, findings


#===------------------------------------------------------------------------===#
# 检查 2：片段与源文件逐字一致
#===------------------------------------------------------------------------===#

def needs_fragment_check(lang: str, filename: str) -> bool:
    """源码语言且短文件名才核对；目录树、场景名、执行位置跳过。"""
    if lang not in CODE_LANGS:
        return False
    if filename.endswith("/") or "（" in filename or " " in filename:
        return False
    return True


def resolve_fragment_source(lines: list[str], block_index: int, filename: str):
    """把短 filename 解析成 games/ 或 shared/ 下的仓库相对路径。

    在同一 ## 节（含其中的 ###）内、代码块之前查找 GitHub blob 链接；
    取路径 basename 与 filename 相同的最近一条。找不到返回 None。
    """
    if filename.startswith(FRAGMENT_SOURCE_PREFIXES) and not filename.endswith("/"):
        return filename

    section_start = 0
    for i in range(block_index - 1, -1, -1):
        heading = HEADING_RE.match(lines[i])
        if heading and heading.group(1) == "##":
            section_start = i
            break

    matches = []
    for i in range(section_start, block_index):
        for blob in GITHUB_BLOB_RE.finditer(lines[i]):
            repo_path = blob.group(1)
            if repo_path.rstrip("/").endswith("/" + filename) or repo_path == filename:
                matches.append(repo_path)
    return matches[-1] if matches else None


def extract_fragments(path):
    """取出需核对的片段，返回 [(源路径或 None, filename, 内容行, 错误)]。

    源路径为 None 且带错误时表示短名无法解析，调用方记为失败。
    """
    fragments = []
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        match = FRAGMENT_RE.match(lines[index])
        if not match:
            index += 1
            continue
        lang, filename = match.group(1), match.group(2)
        block_index = index
        body = []
        index += 1
        while index < len(lines) and lines[index] != "```":
            body.append(lines[index])
            index += 1
        index += 1
        if not needs_fragment_check(lang, filename):
            continue
        source = resolve_fragment_source(lines, block_index, filename)
        if source is None:
            fragments.append(
                (
                    None,
                    filename,
                    body,
                    [
                        f"  短 filename={filename!r} 在同节找不到"
                        f" basename 匹配的 GitHub blob 链接"
                    ],
                )
            )
        else:
            fragments.append((source, filename, body, []))
    return fragments


def check_fragment(source_path, body):
    """核对单个片段；返回错误描述列表。

    片段行必须逐字出现在源文件中且顺序一致（子序列匹配，允许省略
    注释与空行）；历史内容中的省略标记行仍跳过比对，但新写法直接
    省略，标记行由检查 3 在源码围栏内拦截。
    """
    errors = []
    if not source_path.exists():
        return [f"源文件不存在: {source_path}"]
    source_lines = source_path.read_text(encoding="utf-8").splitlines()

    cursor = 0
    for line in body:
        if line.strip() in OMISSION_LINES:
            continue
        found = next(
            (i for i in range(cursor, len(source_lines)) if source_lines[i] == line),
            None,
        )
        if found is None:
            errors.append(f"  片段行不在源文件中或顺序不符: {line!r}")
        else:
            cursor = found + 1
    return errors


def check_all_fragments(qmd_files):
    """核对给定 qmd 的片段，返回 [(qmd 文件, 显示名或源路径, 错误列表)]。"""
    results = []
    for path in qmd_files:
        for source, filename, body, resolve_errors in extract_fragments(path):
            if resolve_errors:
                results.append((path, filename, resolve_errors))
                continue
            errors = check_fragment(REPO_ROOT / source, body)
            if errors:
                results.append((path, f"{filename} -> {source}", errors))
    return results


#===------------------------------------------------------------------------===#
# 检查 3：篇幅预算
#===------------------------------------------------------------------------===#

def estimate_tokens(text: str) -> int:
    """按 bg-content-budget-v1 口径估算 token 数：CJK×1.5 + 其他÷4。"""
    cjk = len(CJK_RE.findall(text))
    return int(cjk * 1.5 + (len(text) - cjk) / 4)


def check_file_budget(path):
    """按篇幅预算核对单个 qmd，返回错误明细列表。

    逐行归类到 (二级标题, 三级标题) 桶：二级为 None 表示无标题引言，
    三级为 None 表示 ## 直接内容；围栏代码块计入所在桶并单独核对
    行数与注释连续行数。
    """
    rel = str(path.relative_to(REPO_ROOT))
    errors = []
    raw = path.read_text(encoding="utf-8").splitlines()
    offset = 0
    if raw and raw[0].strip() == "---":
        for i in range(1, len(raw)):
            if raw[i].strip() == "---":
                offset = i + 1
                break
    lines = raw[offset:]

    tokens = {}  # (二级标题, 三级标题) -> 估算 token
    h3_count = {}  # 二级标题 -> ### 数量
    fence_lang = None
    fence_lineno = 0
    fence_lines = 0
    fence_run = 0
    fence_max_run = 0
    h2 = None
    h3 = None
    para_start = None
    para_text = []

    def flush_para():
        """正文段落超限时报错；无未结算段落时不动作。"""
        nonlocal para_start, para_text
        if para_start is not None and para_text:
            size = estimate_tokens(strip_link_urls("".join(para_text)))
            if size > PARA_TOKENS:
                errors.append(
                    f"{rel}:{para_start}: 正文段落约 {size} token，"
                    f"超过 {PARA_TOKENS}（见标识 bg-content-budget-v1 的知识文件）"
                )
        para_start = None
        para_text = []

    def add_token(text):
        key = (h2, h3)
        tokens[key] = tokens.get(key, 0) + estimate_tokens(strip_link_urls(text))

    for i, line in enumerate(lines):
        lineno = offset + i + 1
        if fence_lang is not None:
            if line.startswith("```"):
                flush_para()
                label = f"{rel}:{fence_lineno}"
                if fence_lines > BLOCK_LINES:
                    errors.append(
                        f"{label}: 代码块 {fence_lines} 行，超过 {BLOCK_LINES} 行"
                    )
                if fence_lang in CODE_LANGS and fence_max_run > COMMENT_RUN:
                    errors.append(
                        f"{label}: 代码块注释连续 {fence_max_run} 行，"
                        f"超过 {COMMENT_RUN} 行"
                    )
                fence_lang = None
                continue
            fence_lines += 1
            stripped = line.strip()
            if fence_lang in CODE_LANGS and stripped in OMISSION_LINES:
                errors.append(
                    f"{rel}:{lineno}: 源码片段省略标记行 {stripped!r}，"
                    f"省略处直接省略（见标识 bg-qmd-element-cases-v1 的知识文件）"
                )
            if stripped in OMISSION_LINES:
                fence_run = 0
            elif stripped.startswith("#") or stripped.startswith("//"):
                fence_run += 1
                fence_max_run = max(fence_max_run, fence_run)
            else:
                fence_run = 0
            add_token(line)
            continue
        if line.startswith("```"):
            flush_para()
            after = line[3:].strip()
            match = re.match(r"\{?\.?(\w+)", after)
            fence_lang = (match.group(1) if match else "").lower()
            fence_lineno = lineno
            fence_lines = 0
            fence_run = 0
            fence_max_run = 0
            add_token(line)
            continue
        if line.startswith("### ") and h2 is not None:
            flush_para()
            h3 = line[4:].strip()
            h3_count[h2] = h3_count.get(h2, 0) + 1
            add_token(line)
            continue
        if line.startswith("## "):
            flush_para()
            h2 = line[3:].strip()
            h3 = None
            add_token(line)
            continue
        # 正文段落长度检查（2026-09-28 增补）：标题、列表、表格、div 标记
        # 与引用行是段落边界；其余连续文本行累计为段落，口径见标识
        # bg-content-budget-v1 的知识文件。
        stripped = line.strip()
        is_prose = (
            bool(stripped)
            and not stripped.startswith(("|", ">", ":::"))
            and not line.startswith("#")
            and not re.match(r"^\s*[-*+]\s", line)
            and not re.match(r"^\s*\d+[.、)]\s", line)
        )
        if is_prose:
            if para_start is None:
                para_start = lineno
            para_text.append(line)
        else:
            flush_para()
        add_token(line)

    flush_para()

    # 根目录 index.qmd 与游戏入口页（body-classes: index-page）是着陆页：
    # 短引言 + 卡片网格不是章节引言，只核对整章总量与代码块限额，
    # 不做引言与分节限额（见标识 bg-content-budget-v1 的知识文件）。
    frontmatter = "\n".join(raw[:offset])
    is_landing = (
        path.name == "index.qmd"
        and (
            path.parent == REPO_ROOT
            or "index-page" in frontmatter
        )
    )
    chapter = "content" in path.parts and not is_landing

    intro = tokens.get((None, None), 0) if chapter else 0
    if intro > INTRO_TOKENS:
        errors.append(f"{rel}: 引言约 {intro} token，超过 {INTRO_TOKENS}")
    h2_totals = {}
    for (h2_key, h3_key), value in tokens.items():
        if h2_key is None or not chapter:
            continue
        h2_totals[h2_key] = h2_totals.get(h2_key, 0) + value
        if h3_key is not None and value > H3_TOKENS:
            errors.append(f"{rel}: 「{h3_key}」约 {value} token，超过 {H3_TOKENS}")
    for h2_key, value in h2_totals.items():
        if value > H2_TOKENS:
            errors.append(f"{rel}: 「{h2_key}」共约 {value} token，超过 {H2_TOKENS}")
    for h2_key, count in h3_count.items():
        if count > H3_COUNT:
            errors.append(
                f"{rel}: 「{h2_key}」下 {count} 个三级标题，超过 {H3_COUNT} 个"
            )
    total = sum(tokens.values())
    if total > FILE_TOKENS:
        errors.append(f"{rel}: 全章约 {total} token，超过 {FILE_TOKENS}")
    return errors


def check_size_budget(qmd_files):
    """核对给定 qmd 的篇幅预算，返回错误明细列表。"""
    errors = []
    for path in qmd_files:
        errors.extend(check_file_budget(path))
    return errors


#===------------------------------------------------------------------------===#
# 检查 4：渲染 HTML 抽查
#===------------------------------------------------------------------------===#

def check_rendered_html():
    """检查 _book 渲染产物；返回 (状态, 明细)。

    状态为 ok / skip / fail；skip 表示尚未渲染，不算失败。
    """
    book = REPO_ROOT / "_book"
    if not book.exists():
        return "skip", ["_book/ 不存在，先在仓库根目录运行 quarto render"]
    findings = []
    for html in sorted(book.rglob("*.html")):
        text = html.read_text(encoding="utf-8", errors="replace")
        for term in HTML_FORBIDDEN_TERMS:
            if term in text:
                findings.append(f"  {html.relative_to(book)}: 含禁用词“{term}”")
        for pattern, label in FORBIDDEN_RES:
            if pattern.search(text):
                findings.append(f"  {html.relative_to(book)}: 含{label}")
    chapter2 = book / "content" / "tic-tac-toe" / "02-toolchain-probe.html"
    if chapter2.exists():
        text = chapter2.read_text(encoding="utf-8", errors="replace")
        if "callout-note" not in text:
            findings.append("  02 章渲染结果缺少 callout-note（术语卡）")
        if "术语：冒烟测试" not in text:
            findings.append("  02 章渲染结果缺少术语卡标题")
    return ("fail" if findings else "ok"), findings


#===------------------------------------------------------------------------===#
# 主流程
#===------------------------------------------------------------------------===#

def parse_args():
    parser = argparse.ArgumentParser(
        description="content 侧写作规范自动检查（默认全量 qmd + 跳过渲染产物）"
    )
    parser.add_argument("--book", action="store_true",
                        help="扫描 _book/ 渲染产物；默认跳过，渲染后按需触发")
    parser.add_argument("--paths", nargs="+", metavar="PATH",
                        help="只检查指定 qmd 文件或目录（相对仓库根）")
    parser.add_argument("--changed", action="store_true",
                        help="只检查 git 工作区改动的 qmd")
    return parser.parse_args()


def main() -> int:
    reexec_under_configured_python()
    args = parse_args()
    if args.paths and args.changed:
        print("失败  --paths 与 --changed 不能同时使用")
        return 1
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if sys.version_info < MIN_PYTHON:
        required = ".".join(map(str, MIN_PYTHON))
        print(f"失败  Python 需要 >= {required}，当前为 {sys.version.split()[0]}")
        return 1
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

    qmd_files = resolve_qmd_paths(args)
    scope = "全量" if not (args.paths or args.changed) else "按指定范围"

    header(1, "禁用词扫描")
    term_findings = scan_qmd_forbidden(qmd_files)
    planning_findings = scan_planning_inline_paths(qmd_files)
    print(f"扫描 {len(qmd_files)} 个 qmd 文件（{scope}）")
    for path, lineno, term in term_findings:
        print(f"{RED}  {path.relative_to(REPO_ROOT)}:{lineno}: 禁用词“{term}”{RESET}")
    for path, lineno, excerpt in planning_findings:
        print(
            f"{RED}  {path.relative_to(REPO_ROOT)}:{lineno}: "
            f"规划页行内代码路径（实现目录改用中文锚文本 GitHub 链接）“{excerpt}”{RESET}"
        )

    header(2, "agents 正文日期戳")
    agents_files, date_findings = scan_agents_body_dates()
    print(f"扫描 {len(agents_files)} 个 agents Markdown（跳过 frontmatter）")
    for path, lineno, excerpt in date_findings:
        print(
            f"{RED}  {path.relative_to(REPO_ROOT)}:{lineno}: "
            f"正文含日期戳“{excerpt}”{RESET}"
        )

    header(3, "片段一致性")
    fragment_results = check_all_fragments(qmd_files)
    checked = sum(len(extract_fragments(path)) for path in qmd_files)
    print(f"核对 {checked} 个片段（短 filename 经同节 GitHub 链接解析）")
    for path, label, errors in fragment_results:
        print(f"{RED}  {path.relative_to(REPO_ROOT)} -> {label}{RESET}")
        for error in errors:
            print(f"{RED}{error}{RESET}")

    header(4, "篇幅预算")
    size_errors = check_size_budget(qmd_files)
    print(f"核对 {len(qmd_files)} 个 qmd 文件")
    for error in size_errors:
        print(f"{RED}  {error}{RESET}")

    header(5, "渲染 HTML 抽查")
    if args.book:
        status, details = check_rendered_html()
        print("跳过：尚未渲染" if status == "skip" else "检查 _book/ 下的 HTML")
        for detail in details:
            print(f"{RED}{detail}{RESET}")
    else:
        status = "off"
        print("默认不扫描渲染产物；需要时加 --book（或 run.py check --profile book）")

    header(6, "检查结果")
    failed = bool(
        term_findings
        or planning_findings
        or date_findings
        or fragment_results
        or size_errors
        or status == "fail"
    )
    if failed:
        print(
            f"{RED}未通过：存在禁用词、规划页行内路径、agents 日期戳、片段不一致、"
            f"篇幅超限或渲染问题（详见上方）{RESET}"
        )
        logging.error("verify_content: 检查未通过，按上方定位修复后重跑")
        return 1
    if status == "off":
        print("qmd 与片段检查通过；渲染产物未扫描")
        return 0
    if status == "skip":
        print("qmd 与片段检查通过；渲染检查跳过，渲染后重跑本脚本")
        return 0
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
