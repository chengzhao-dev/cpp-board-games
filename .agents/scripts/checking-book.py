#!/usr/bin/env python3
"""核对全书读者正文。

正文字面规则来自已安装的 dsh-quarto-book 插件；本脚本只负责三件事：
找到 config/config.toml 指定的解释器，找到插件的 verifying-content.py，
再核对项目技能章节表与各章实际 title、二级标题一致。
子进程输出直接继承，成功或失败都原样留给调用方。

检查器位置优先级：
  1. 环境变量 BOARD_GAMES_CONTENT_CHECKER 指向的脚本；
  2. DSH_HOME 或 ~/.dsh 下 profiles/<DSH_PROFILE|desktop> 的已安装插件。

退出码：0 = 检查通过，1 = 检查有问题或工具缺失。
"""

import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "config.toml"
CHAPTER_MAP = ROOT / ".agents/skills/quarto-book-project/writing/chapter-map.md"
MIN_PYTHON = (3, 12)
CHECKER_REL = Path(
    "node_modules/@chengzhao-dev/dsh-quarto-book/skills/"
    "writing-quarto/scripts/verifying-content.py"
)


def select_python():
    """只使用根目录 config/config.toml 的 python 字段。"""
    try:
        config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    candidate = str(config.get("python") or "").strip()
    if not candidate or not Path(candidate).is_file():
        return None
    try:
        result = subprocess.run(
            [candidate, "-c", "import sys; print(*sys.version_info[:2])"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            check=False, timeout=30,
        )
        major, minor = (int(part) for part in result.stdout.split())
    except (OSError, ValueError):
        return None
    if (major, minor) >= MIN_PYTHON:
        return candidate
    return None


def content_checker():
    """定位插件里的正文检查脚本。先看显式环境变量，再按 DSH 安装布局查找。"""
    explicit = os.environ.get("BOARD_GAMES_CONTENT_CHECKER")
    candidates = [Path(explicit)] if explicit else []
    profiles = [os.environ.get("DSH_PROFILE") or "desktop"]
    homes = [os.environ.get("DSH_HOME"), str(Path.home() / ".dsh")]
    for home in filter(None, homes):
        for profile in profiles:
            candidates.append(Path(home) / "profiles" / profile / CHECKER_REL)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def yaml_title(lines):
    """取 front matter 里的 title 值。"""
    in_front_matter = False
    for index, line in enumerate(lines):
        if index == 0 and line.strip() == "---":
            in_front_matter = True
            continue
        if in_front_matter and line.strip() == "---":
            break
        if in_front_matter and line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def headings(lines):
    """取正文里的二级标题，跳过围栏内部。"""
    found = []
    in_fence = False
    for line in lines:
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## "):
            found.append(line[3:].strip())
    return found


def check_chapter_map():
    """章节表的 title 与二级标题必须与正文逐项一致。"""
    if not CHAPTER_MAP.is_file():
        return [f"找不到章节表：{CHAPTER_MAP.relative_to(ROOT)}"], 0
    errors = []
    checked = 0
    for line in CHAPTER_MAP.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `content/"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        checked += 1
        path = cells[0].strip("`")
        expected_title = cells[3]
        expected_h2 = [] if cells[4] == "—" else [
            item.strip() for item in cells[4].split("、") if item.strip()
        ]
        source = ROOT / path
        if not source.is_file():
            errors.append(f"{path}：章节表列出的文件不存在")
            continue
        lines = source.read_text(encoding="utf-8").splitlines()
        actual_title = yaml_title(lines)
        actual_h2 = headings(lines)
        if actual_title != expected_title:
            errors.append(
                f"{path}：章节表 title「{expected_title}」与正文「{actual_title}」不一致"
            )
        if actual_h2 != expected_h2:
            errors.append(
                f"{path}：章节表二级标题「{'、'.join(expected_h2)}」"
                f"与正文「{'、'.join(actual_h2)}」不一致"
            )
    return errors, checked


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    python = select_python()
    if python is None:
        print("失败  找不到 config/config.toml 指定的 Python（最低 3.12）")
        return 1
    checker = content_checker()
    if checker is None:
        print("失败  找不到插件 dsh-quarto-book 的正文检查脚本；请安装插件或设置 BOARD_GAMES_CONTENT_CHECKER")
        return 1
    child_env = dict(os.environ)
    child_env["PYTHONIOENCODING"] = "utf-8"
    child_env["PYTHONUTF8"] = "1"
    child_env["QUARTO_PYTHON"] = python
    try:
        code = subprocess.run(
            [python, str(checker), "--root", str(ROOT)],
            env=child_env, check=False,
        ).returncode
    except OSError as exc:
        print(f"失败  无法启动正文检查：{exc}")
        return 1
    if code != 0:
        return code
    errors, checked = check_chapter_map()
    if errors:
        print("失败  章节表与正文不一致：")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"章节表：核对 {checked} 行，title 与二级标题均与正文一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
