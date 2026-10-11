#!/usr/bin/env python3
"""按中文行文规则检查仓库内的中文载体。

只服务 agent 侧门禁（run.py check --profile fast）：规则只收高精度项，命中即失败，
误报代价高于漏报时宁可不收。判定总纲见标识 bg-chinese-quality-v1 的知识文件，
注释形态见 bg-comment-style-v1，术语与锚点见 bg-terminology-v1 与
bg-chinese-style-cases-v1 的知识文件。

注释规则（作用于源码与配置注释）：

1. 注释以「表示」开头。类型与常量注释直接写名词短语，不写「表示 X」。
2. 相邻两行注释完全重复。同一事实只写一次；纯分隔线（`//===`、`#---`）与闭括号不算。

正文规则（作用于 `content/` 与仓库根 `README.md`、`index.qmd`）：

3. 跨仓链接标签仍是旧章名。标签必须等于目标章的当前 title。
4. 顿号后接「以及」。大小并列分层，改用逗号。
5. 「九格」。统一写「九个棋盘格子」。
6. 「的的」。连续两个「的」。
7. 「进行…的实现」。名词化堆叠，改用动词句。
8. 「公开段 / 私有段 / 公共成员 / 成员变量」。C++ 术语按
   `bg-cpp-chinese-terms-v1` 定案词写，见「访问说明符」。
   自造比喻「公开段 / 私有段」读者对不上源码；写 `public:` /
   `private:` 下（或之后）的成员，成员称「公开成员 / 私有成员」，
   数据成员不作「成员变量」。

句式规则（作用于 `content/` 正文、`.agents/**/*.md` 与源码/配置注释）：

9. 「下一节 / 上一节」。读者正文禁写小节导航预告或回指（章末「下一章」
   保留），衔接靠新节首句承接；规则见 `bg-paragraph-craft-v1`。
10. 「代码把它写成」。元叙述开场把源码当施事，改用对象先行的
    「对象 → 名称 → 约束 → 出处」；规则见 `bg-chinese-quality-v1`。
11. 「第二道…防线」类实现注。禁隐喻式防御旁白；规则见
    `bg-comment-style-v1`。
12. agent 免责腔：「服务于讲解」「片段不保证」「不等于文件内顺序」。
    摘录同源保证交给 verify；免责声明只在 `.agents` 权威与闸脚本里，
    读者正文整句删除；规则见 `bg-chapter-structure-v1`。
13. 「由…完成」。被动交接把施事藏在「由」后，读者正文改主动句；
    仅限 `content/**/*.qmd` 与根 `index.qmd` 的围栏外正文，`.agents`
    案例必须能引用反例，不扫；规则见 `bg-paragraph-craft-v1`。
14. 「分别交给 / 各说一层」。拉链句把两组对象配进一句，删任一配对
    仍成立；读者正文改按「推迟 → 拆句 → 一项一行」处理；仅限读者
    正文，`.agents` 案例必须能引用反例，不扫；规则见
    `bg-paragraph-craft-v1`「拉链句」。宽泛的「分别」不硬拦。

术语引用豁免：命中串紧贴中文引号「」或反引号时（如「下一节／上一节」、
`九格` 之外的引用形态）视为规则描述引用，不判违规——`.agents` 讨论规则时
保留术语，读者正文里裸写才命中。围栏代码块（```/~~~）内的示例文本按设计
保留被禁写法，不参与句式规则。

覆盖证据：运行时输出每个载体组的文件计数，证明本轮扫过全部中文载体；排除的
生成物与第三方许可证在 SKIP_DIRS、SKIP_NAMES 里列明，不静默跳过。

用法：python check_zh_lint.py [--verbose]
退出码：0 = 无命中，1 = 有命中。
"""

from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[4]

# 排除目录：生成物、缓存与临时产物不入上下文（读取边界见 AGENTS.md）。
SKIP_DIRS = {
    ".git", "_book", "build", ".quarto", ".cache", ".tmp", "temp",
    "__pycache__", "node_modules", "_freeze", ".zcode", ".venv",
}
# 第三方许可证与字体二进制不参与中文体检。
SKIP_NAMES = {"LICENSE", "LICENSE.txt", "OFL.txt"}

# 载体分组：用于输出覆盖计数。
CARRIER_GROUPS = (
    ("qmd", {".qmd"}),
    ("md", {".md"}),
    ("html/svg", {".html", ".svg"}),
    ("css/scss", {".css", ".scss"}),
    ("C++", {".h", ".hpp", ".hh", ".cpp", ".cc", ".cxx"}),
    ("sh", {".sh", ".bash"}),
    ("cmake", {".cmake"}),
    ("python", {".py"}),
    ("json", {".json", ".jsonc"}),
    ("toml", {".toml"}),
    ("yaml", {".yml", ".yaml"}),
    ("js/ts", {".js", ".mjs", ".ts"}),
    ("txt", {".txt"}),
)
CMAKE_NAMES = {"CMakeLists.txt"}
# 注释规则的作用域：有注释语法的载体。
COMMENT_EXTENSIONS = (
    {".h", ".hpp", ".hh", ".cpp", ".cc", ".cxx", ".sh", ".bash", ".cmake", ".py",
     ".json", ".jsonc", ".toml", ".yml", ".yaml", ".css", ".scss", ".js", ".mjs",
     ".ts", ".html", ".svg"}
)
# 正文规则的路径：只有面向读者的载体受管。
PROSE_ROOT_DIRS = {"content"}
PROSE_ROOT_FILES = {"README.md", "index.qmd"}
# agent 文档作用域：只收本轮新增的句式禁令，不收正文六条（压缩语域豁免）。
AGENT_DOC_ROOT = ".agents"

# 注释开头标记与注释正文（`//` 覆盖 `///`，`#` 覆盖 `##`）。
COMMENT_START = re.compile(r"^\s*(?://|#|\*|/\*|<!--)")
COMMENT_BODY = re.compile(r"^\s*(?://+|#+|/\*+|<!--|\*)\s*(?P<body>.*?)\s*$")
SEPARATOR_BODY = re.compile(r"^[=\-*#_/\\<>|\s]*$")

RULE_SOURCES = {
    "bai-shi": "bg-comment-style-v1",
    "duplicate-comment": "bg-comment-style-v1",
    "stale-link-label": "bg-terminology-v1",
    "odd-and": "bg-chinese-quality-v1",
    "nine-grid": "bg-terminology-v1",
    "de-de": "bg-chinese-quality-v1",
    "make-impl": "bg-chinese-quality-v1",
    "access-specifier": "bg-cpp-chinese-terms-v1",
    "next-section": "bg-paragraph-craft-v1",
    "code-wrote-it": "bg-chinese-quality-v1",
    "defense-line": "bg-comment-style-v1",
    "agent-disclaimer": "bg-chapter-structure-v1",
    "passive-done": "bg-paragraph-craft-v1",
    "zipper-pairing": "bg-paragraph-craft-v1",
}
BAI_SHI = re.compile(r"^\s*(?://+|#+|\*|/\*+|<!--)\s*表示")
STALE_LABELS = (
    "定义棋盘与格子状态",
    "检查落子并判定终局",
    "写下井字棋规则",
    "配置并运行井字棋",
)
ODD_AND = re.compile(r"、\s*以及")
NINE_GRID = re.compile(r"九格")
DE_DE = re.compile(r"的的")
MAKE_IMPL = re.compile(r"进行[^，。；：、\n]{0,8}的实现")
ACCESS_SPEC = re.compile(r"公开段|私有段|公共成员|成员变量")
# 句式禁令（作用于正文、agent 文档与注释）。
NEXT_SECTION = re.compile(r"下一节|上一节")
CODE_WROTE_IT = re.compile(r"代码把它写成")
DEFENSE_LINE = re.compile(r"第二道[^，。；\n]{0,6}防线")
AGENT_DISCLAIMER = re.compile(r"服务于讲解|片段不保证|不等于文件内顺序")
# 「由…完成」被动交接：仅限读者 qmd 围栏外正文，.agents 案例可引用反例。
PASSIVE_DONE = re.compile(r"由[^，。；：、\n]{1,20}完成")
# 拉链句高频词：仅限读者正文，.agents 案例可引用反例；宽泛的「分别」不拦。
ZIPPER_PAIRING = re.compile(r"分别交给|各说一层")
# 术语引用豁免符号：命中串任一侧紧贴这些符号即视为引用，不算违规。
QUOTE_MARKS = "「」`"
# 门禁自测文件按设计载入被禁样例，句式规则对它整体豁免。
FIXTURE_FILES = {"test_check_zh_lint.py"}


def is_skipped(path):
    """判断路径是否落在排除目录或第三方许可证名单里。"""
    if path.name in SKIP_NAMES:
        return True
    return any(part in SKIP_DIRS for part in path.parts)


def group_of(path):
    """返回路径所属的载体组名；不属于任何组时返回 None。"""
    if path.name in CMAKE_NAMES:
        return "cmake"
    suffix = path.suffix.lower()
    for name, suffixes in CARRIER_GROUPS:
        if suffix in suffixes:
            return name
    return None


def collect_carriers():
    """按固定顺序收集全部中文载体，返回 [(路径, 组名)]。"""
    carriers = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or is_skipped(path):
            continue
        name = group_of(path)
        if name:
            carriers.append((path, name))
    return carriers


def rules_for(path):
    """返回路径适用的规则开关 (注释规则, 正文规则, agent 文档规则)。"""
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return False, False, False
    suffix_ok = (
        path.suffix.lower() in COMMENT_EXTENSIONS or path.name in CMAKE_NAMES
    )
    in_prose = rel.parts[0] in PROSE_ROOT_DIRS or rel.as_posix() in PROSE_ROOT_FILES
    in_agents = rel.parts[0] == AGENT_DOC_ROOT and path.suffix.lower() == ".md"
    return suffix_ok, in_prose, in_agents


def duplicate_body(line):
    """返回注释正文；非注释行或纯分隔线返回 None。"""
    match = COMMENT_BODY.match(line)
    if not match:
        return None
    body = match.group("body").strip()
    if not body or SEPARATOR_BODY.match(body):
        return None
    return body


def is_quoted(line, match):
    """术语引用豁免：命中串任一侧紧贴中文引号或反引号时不判违规。"""
    start, end = match.start(), match.end()
    left = line[start - 1] if start > 0 else ""
    right = line[end] if end < len(line) else ""
    return bool(left) and left in QUOTE_MARKS or bool(right) and right in QUOTE_MARKS


def scan_text(path, text, comment_rules, prose_rules, agent_rules=False):
    """扫描单个文本，返回 [(行号, 规则键, 原文)]。"""
    findings = []
    lines = text.splitlines()
    fixture = path.name in FIXTURE_FILES
    in_fence = False
    for number, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            # 围栏内的示例文本按设计保留被禁写法，句式规则不扫代码块内容。
            continue
        if comment_rules:
            if BAI_SHI.match(line):
                findings.append((number, "bai-shi", line.strip()))
            previous = duplicate_body(lines[number - 2]) if number > 1 else None
            if previous is not None and previous == duplicate_body(line):
                findings.append((number, "duplicate-comment", line.strip()))
            if not fixture:
                defense = DEFENSE_LINE.search(line)
                if defense and not is_quoted(line, defense):
                    findings.append((number, "defense-line", line.strip()))
        if prose_rules:
            for label in STALE_LABELS:
                if label in line:
                    findings.append(
                        (number, "stale-link-label", f"{label}｜{line.strip()}")
                    )
            if ODD_AND.search(line):
                findings.append((number, "odd-and", line.strip()))
            if NINE_GRID.search(line):
                findings.append((number, "nine-grid", line.strip()))
            if DE_DE.search(line):
                findings.append((number, "de-de", line.strip()))
            if MAKE_IMPL.search(line):
                findings.append((number, "make-impl", line.strip()))
            if ACCESS_SPEC.search(line):
                findings.append((number, "access-specifier", line.strip()))
        if (prose_rules or agent_rules) and not fixture:
            for key, pattern in (
                ("next-section", NEXT_SECTION),
                ("code-wrote-it", CODE_WROTE_IT),
                ("defense-line", DEFENSE_LINE),
            ):
                for match in pattern.finditer(line):
                    if not is_quoted(line, match):
                        findings.append((number, key, line.strip()))
        # agent 免责腔仅限读者正文：.agents 文档讨论规则本身时需要引用这些短语。
        if prose_rules and not fixture:
            match = AGENT_DISCLAIMER.search(line)
            if match and not is_quoted(line, match):
                findings.append((number, "agent-disclaimer", line.strip()))
            # 「由…完成」只拦读者 qmd 围栏外正文；README 与 .agents 不扫，
            # 案例要能引用反例。
            if path.suffix.lower() == ".qmd":
                match = PASSIVE_DONE.search(line)
                if match and not is_quoted(line, match):
                    findings.append((number, "passive-done", line.strip()))
            # 拉链句高频词只拦读者正文；.agents 案例要能引用反例。
            match = ZIPPER_PAIRING.search(line)
            if match and not is_quoted(line, match):
                findings.append((number, "zipper-pairing", line.strip()))
    return findings


def main():
    parser = argparse.ArgumentParser(description="中文载体行文体检")
    parser.add_argument("--verbose", action="store_true", help="逐个载体打印进度")
    args = parser.parse_args()

    carriers = collect_carriers()
    counts = {}
    comment_files = 0
    prose_files = 0
    agent_files = 0
    findings = []
    for path, name in carriers:
        counts[name] = counts.get(name, 0) + 1
        comment_rules, prose_rules, agent_rules = rules_for(path)
        if not (comment_rules or prose_rules or agent_rules):
            continue
        comment_files += comment_rules
        prose_files += prose_rules
        agent_files += agent_rules
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, key, snippet in scan_text(
            path, text, comment_rules, prose_rules, agent_rules
        ):
            findings.append((path, number, key, snippet))
        if args.verbose:
            print(f"扫描 {path.relative_to(ROOT).as_posix()}")

    census = "、".join(
        f"{name} {counts[name]}" for name, _ in CARRIER_GROUPS if counts.get(name)
    )
    print(f"覆盖 中文载体 {len(carriers)} 个：{census}")
    print(
        f"作用域 注释规则 {comment_files} 个文件，正文规则 {prose_files} 个文件，"
        f"agent 文档规则 {agent_files} 个文件"
    )

    if findings:
        for path, number, key, snippet in findings:
            rel = path.relative_to(ROOT).as_posix()
            source = RULE_SOURCES[key]
            print(f"{rel}:{number}: {key}（依据 {source}）{snippet}")
        print(f"中文载体体检：命中 {len(findings)} 处")
        return 1

    print("OK: 中文载体体检通过，未发现规则命中。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
