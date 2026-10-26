#!/usr/bin/env python3
"""检查已安装的 dsh-quarto-book 与 dsh-cpp-workflow 是否完整、可用。

只读：不安装、不写文件、不改 PATH。默认检查 DSH_HOME 下 desktop profile 的
node_modules；可以用 --profile 指定 profile 名，或用 --root 指定 profile 目录。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 12)
PACKAGES = {
    "dsh-quarto-book": {
        "required": [
            "package.json",
            "lib/index.js",
            "cordis.patch.yml",
            "skills/writing-quarto/SKILL.md",
            "skills/writing-quarto/scripts/verifying-content.py",
            "skills/designing-theme/SKILL.md",
            "skills/designing-theme/assets/theme/css/landing.css",
        ],
        "python": ["skills/writing-quarto/scripts/verifying-content.py"],
    },
    "dsh-cpp-workflow": {
        "required": [
            "package.json",
            "lib/index.js",
            "cordis.patch.yml",
            "skills/developing-cpp/SKILL.md",
            "skills/building-cpp/SKILL.md",
            "skills/building-cpp/scripts/checking-environment.mjs",
            "templates/cpp-workflow-project/SKILL.md",
        ],
        "python": [],
    },
}


def profile_root(explicit: Path | None, profile: str) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    home = Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh"))
    return (home / "profiles" / profile).expanduser().resolve()


def package_root(profile: Path, name: str) -> Path:
    return profile / "node_modules" / "@chengzhao-dev" / name


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("顶层不是对象")
    return value


def check_syntax(path: Path, python: str | None) -> str | None:
    if not path.is_file():
        return "文件不存在"
    try:
        if path.suffix in {".py"}:
            with path.open(encoding="utf-8") as handle:
                compile(handle.read(), str(path), "exec")
        elif path.suffix in {".js", ".mjs"}:
            node = shutil.which("node")
            if node is None:
                return "找不到 node，跳过语法检查"
            result = subprocess.run(
                [node, "--check", str(path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode != 0:
                return (result.stderr or result.stdout).strip().splitlines()[-1]
    except Exception as error:  # noqa: BLE001
        return str(error)
    return None


def _version_tuple(value: str | None) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in str(value or "").split("."))
    except ValueError:
        return (0,)


def check_package(profile: Path, name: str) -> dict:
    spec = PACKAGES[name]
    root = package_root(profile, name)
    result = {"name": name, "root": str(root), "version": None, "ok": True, "problems": []}
    manifest = root / "package.json"
    if not root.is_dir():
        result["ok"] = False
        result["problems"].append("未安装")
        return result
    try:
        data = load_json(manifest)
    except Exception as error:  # noqa: BLE001
        result["ok"] = False
        result["problems"].append(f"package.json 无效：{error}")
        return result
    result["version"] = data.get("version")
    required = list(spec["required"])
    if name == "dsh-cpp-workflow" and _version_tuple(result["version"]) >= (0, 3, 0):
        required += ["skills/building-cpp/references/encoding.md", "skills/building-cpp/scripts/checking-encoding.mjs"]
    if data.get("name") != f"@chengzhao-dev/{name}":
        result["problems"].append(f"包名不是 @chengzhao-dev/{name}")
    for relative in required:
        candidate = root / relative
        if not candidate.is_file():
            result["problems"].append(f"缺少 {relative}")
    for relative in spec["python"]:
        error = check_syntax(root / relative, None)
        if error:
            result["problems"].append(f"{relative} 语法：{error}")
    for relative in ("lib/index.js",):
        error = check_syntax(root / relative, None)
        if error:
            result["problems"].append(f"{relative} 语法：{error}")
    patch = root / "cordis.patch.yml"
    if patch.is_file():
        text = patch.read_text(encoding="utf-8", errors="replace")
        if f"@chengzhao-dev/{name}" not in text:
            result["problems"].append("cordis.patch.yml 未指向本包")
    if result["problems"]:
        result["ok"] = False
    return result


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.version_info < MIN_PYTHON:
        print(f"需要 Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} 或更高", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="profile 目录，默认 DSH_HOME/profiles/desktop")
    parser.add_argument("--profile", default="desktop", help="DSH profile 名")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--quiet", action="store_true", help="只输出问题")
    args = parser.parse_args(argv)

    profile = profile_root(args.root, args.profile)
    if not profile.is_dir():
        print(f"profile 目录不存在：{profile}", file=sys.stderr)
        return 2

    reports = [check_package(profile, name) for name in PACKAGES]
    if args.json:
        print(json.dumps({"profile": str(profile), "packages": reports}, ensure_ascii=False, indent=2))
    else:
        if not args.quiet:
            print(f"DSH profile：{profile}")
        for report in reports:
            state = "OK" if report["ok"] else "FAIL"
            version = report["version"] or "未知版本"
            print(f"{state}  @chengzhao-dev/{report['name']}  {version}")
            for problem in report["problems"]:
                print(f"      - {problem}")
    return 0 if all(report["ok"] for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
