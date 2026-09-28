#!/usr/bin/env python3
"""检查仓库文本的 UTF-8、BOM、行尾、控制字符和常见乱码。

只服务 agent 侧门禁（run.py check --profile fast）：中文文件使用 UTF-8 无 BOM、
LF；.gitattributes 已强制 LF 入库，工作区出现 CRLF 即报出。content/ 与 games/
下的命中默认只报告不失败，.agents/ 与根部入口文件命中即失败。

用法：python check_encoding.py [--strict-all] [--verbose]
退出码：0 = 无硬失败，1 = 有硬失败。
"""

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[4]
SKIP_DIRS = {".git", "_book", ".quarto", "build", "node_modules", ".cache", ".tmp", "temp", "__pycache__"}
TEXT_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cmake", ".css", ".h", ".hpp", ".html", ".json", ".lua",
    ".md", ".py", ".qmd", ".scss", ".sh", ".toml", ".txt", ".yml", ".yaml",
}
TEXT_NAMES = {".editorconfig", ".gitignore", ".gitattributes", "AGENTS.md", "README.md", "_quarto.yml"}
MOJIBAKE_MARKERS = ("锟", "鏂", "鐜", "绔", "鎴", "璇", "浠", "鍏", "瀹", "閸")
ALLOWED_CONTROLS = {"\n", "\r", "\t"}
HARD_NAMES = {"AGENTS.md", "README.md", "_quarto.yml", "config.toml"}


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def is_text_candidate(path: Path) -> bool:
    return path.name in TEXT_NAMES or path.suffix.lower() in TEXT_EXTENSIONS


def control_issues(text: str) -> list[tuple[int, int, str]]:
    """返回 (行号, 列号, code point)，排除正常空白控制字符。"""
    issues = []
    line = column = 1
    for char in text:
        code = ord(char)
        if (code < 0x20 or 0x7F <= code <= 0x9F) and char not in ALLOWED_CONTROLS:
            issues.append((line, column, f"U+{code:04X}"))
        if char == "\n":
            line, column = line + 1, 1
        else:
            column += 1
    return issues


def issue_details(text: str) -> list[str]:
    details = [f"控制字符 {code}（第 {line} 行第 {column} 列）"
               for line, column, code in control_issues(text)]
    if "\ufffd" in text:
        details.append("含 U+FFFD 替换字符")
    if any(0xE000 <= ord(ch) <= 0xF8FF for ch in text):
        details.append("含私用区字符")
    if sum(text.count(marker) for marker in MOJIBAKE_MARKERS) >= 4:
        details.append("含常见 UTF-8/GBK 乱码标记")
    return details


def severity(rel: Path) -> str:
    """agents 与根部入口是硬约束；content/ 与 games/ 默认只报告。"""
    value = rel.as_posix()
    if value in HARD_NAMES or value.startswith(".agents/"):
        return "hard"
    return "soft"


def main() -> int:
    parser = argparse.ArgumentParser(description="检查仓库文本编码和乱码")
    parser.add_argument("--strict-all", action="store_true", help="content/games 命中也返回失败")
    parser.add_argument("--verbose", action="store_true", help="展开每个文件的全部诊断")
    parser.add_argument("--max-findings", type=int, default=30, help="默认最多输出的命中数")
    args = parser.parse_args()
    hard, soft = [], []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or is_skipped(path) or not is_text_candidate(path):
            continue
        rel = path.relative_to(ROOT)
        if rel.as_posix() == ".agents/skills/governing-agents/scripts/check_encoding.py":
            continue
        findings = []
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            findings.append(f"非 UTF-8（字节 {exc.start}）")
            text = ""
        else:
            if raw.startswith(b"\xef\xbb\xbf"):
                findings.append("含 UTF-8 BOM")
            if b"\r\n" in raw or b"\r" in raw:
                findings.append("含 CRLF/CR 行尾，应统一为 LF")
            findings.extend(issue_details(text))
        if findings:
            target = soft if severity(rel) == "soft" and not args.strict_all else hard
            target.append(f"{rel}: " + "；".join(findings))

    total = len(hard) + len(soft)
    if total:
        if hard:
            print(f"FAIL encoding 硬失败={len(hard)} 软报告={len(soft)}")
        else:
            print(f"REPORT encoding 硬失败=0 软报告={len(soft)}")
        shown = hard + soft if args.verbose else (hard + soft)[:max(1, args.max_findings)]
        for finding in shown:
            print(f"  {finding}")
        if len(shown) < total:
            print(f"  ... 其余 {total - len(shown)} 项省略，使用 --verbose 查看")
        return 1 if hard else 0
    print("PASS encoding UTF-8 无 BOM、LF、无明显乱码")
    return 0


if __name__ == "__main__":
    sys.exit(main())
