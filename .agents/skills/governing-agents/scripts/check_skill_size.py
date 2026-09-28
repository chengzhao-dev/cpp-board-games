#!/usr/bin/env python3
"""检查稳定上下文体量：L0/L1/L2 分层加载契约的体积护栏。

为什么需要它：省 token 的地基是「稳定前缀要短」。AGENTS.md 与 SKILL.md 每轮都被
重读，reference 过长则一次任务就读掉大量无关内容。

按字符而非字节：上限多为字符数，字符数对中文是更好的 token 代理（一个汉字约一个
token）；字节只用在厂商明确按字节定义的 L0（project_doc_max_bytes = 65536）。

阈值分两档（预算按本仓需求可调，不与 cpp-notes 对齐数字）：
  厂商硬约束（默认即失败）：
    L0  AGENTS.md                        <= 65536 字节
        name <= 64 字符、description <= 1024 字符
        全部 skill 的 name + description <= 8000 字符（Codex 列表预算）
  本仓建议（默认 WARN，--strict 升级为失败；调整时同步 refactor-guidelines.md）：
    L1  .agents/skills/*/SKILL.md          <= 45 行 且 <= 3000 字符
    L2  .agents/skills/*/references/**/*.md <= 160 行 且 <= 6000 字符
    catalog.md                             <= 3000 字符
  教学正文体量不在本脚本：content/**/*.qmd 由 verify_content.py 的 token 预算负责。

用法：python check_skill_size.py [--strict] [--verbose]
退出码：0 = 无硬失败（建议越界只 WARN），1 = 有硬失败或 --strict 下有建议越界。
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
L0_BYTE_LIMIT = 65536
L1 = (".agents/skills/*/SKILL.md", 45, 3000, "L1 任务路由")
L2 = (".agents/skills/*/references/**/*.md", 160, 6000, "L2 原子知识")
CATALOG = ".agents/skills/governing-agents/references/catalog.md"
CATALOG_CHAR_LIMIT = 3000
NAME_CHAR_LIMIT = 64
DESCRIPTION_CHAR_LIMIT = 1024
LISTING_CHAR_LIMIT = 8000

FIELD_RE = re.compile(r"(?m)^(name|description):\s*(.*?)\s*$")


def stat(path):
    """返回 (行数, 字符数, 字节数)。"""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    return len(raw.splitlines()), len(raw), len(raw.encode("utf-8"))


def front_fields(path):
    """取出 SKILL.md front matter 里的 name 与 description。"""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if not raw.startswith("---"):
        return {}
    end = raw.find("\n---", 3)
    if end < 0:
        return {}
    return dict(FIELD_RE.findall(raw[:end]))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="skills 体积护栏")
    ap.add_argument("--strict", action="store_true", help="建议阈值越界也判失败")
    ap.add_argument("--verbose", action="store_true", help="逐项列出文件与字符数")
    args = ap.parse_args()

    hard = []
    warned = []
    rows = []

    n0, c0, b0 = stat(ROOT / "AGENTS.md")
    if b0 > L0_BYTE_LIMIT:
        hard.append(("L0 稳定前缀", "AGENTS.md", f"{b0} 字节 > {L0_BYTE_LIMIT}"))
    rows.append(("AGENTS.md", n0, c0))

    listing = 0
    for pattern, line_limit, char_limit, tier in (L1, L2):
        for path in sorted(ROOT.glob(pattern)):
            n, c, _b = stat(path)
            rel = path.relative_to(ROOT).as_posix()
            rows.append((rel, n, c))
            if n > line_limit:
                warned.append((tier, rel, f"{n} 行 > {line_limit}（本仓建议）"))
            elif c > char_limit:
                warned.append((tier, rel, f"{c} 字符 > {char_limit}（本仓建议）"))
            if tier.startswith("L1"):
                fields = front_fields(path)
                name = fields.get("name", "")
                desc = fields.get("description", "")
                listing += len(name) + len(desc)
                if not name or not desc:
                    hard.append((tier, rel, "front matter 缺少 name 或 description"))
                if len(name) > NAME_CHAR_LIMIT:
                    hard.append((tier, rel, f"name {len(name)} 字符 > {NAME_CHAR_LIMIT}"))
                if len(desc) > DESCRIPTION_CHAR_LIMIT:
                    hard.append(
                        (tier, rel, f"description {len(desc)} 字符 > {DESCRIPTION_CHAR_LIMIT}")
                    )

    if listing > LISTING_CHAR_LIMIT:
        hard.append(
            ("L1 列表预算", "全部 SKILL.md",
             f"name+description {listing} 字符 > {LISTING_CHAR_LIMIT}")
        )

    catalog_path = ROOT / CATALOG
    if catalog_path.is_file():
        cn, cc, _cb = stat(catalog_path)
        rows.append((CATALOG, cn, cc))
        if cc > CATALOG_CHAR_LIMIT:
            warned.append(("L1 目录路由", CATALOG, f"{cc} 字符 > {CATALOG_CHAR_LIMIT}（本仓建议）"))

    if args.verbose:
        for rel, n, c in rows:
            print(f"  {n:>4} 行 {c:>6} 字符  {rel}")

    if args.strict:
        hard.extend(warned)
        warned = []
    if hard:
        print(f"FAIL  context-size 硬失败 {len(hard)} 项")
        for tier, name, why in hard:
            print(f"      {tier}  {name}  {why}")
        for tier, name, why in warned:
            print(f"      WARN {tier}  {name}  {why}")
        return 1
    if warned:
        print(f"WARN  context-size 建议越界 {len(warned)} 项（--strict 升级为失败）")
        for tier, name, why in warned:
            print(f"      {tier}  {name}  {why}")
        return 0
    skills = len(list(ROOT.glob(L1[0])))
    refs = len(list(ROOT.glob(L2[0])))
    print(
        f"PASS  context-size  AGENTS.md={n0} 行/{b0} 字节；"
        f"{skills} 个 L1、{refs} 个 L2 在建议内；列表 {listing}/{LISTING_CHAR_LIMIT} 字符"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
