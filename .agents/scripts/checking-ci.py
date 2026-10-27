#!/usr/bin/env python3
"""在本地复现 CI 的检查序列。

CI 依次执行：章节检查、改动游戏的构建、整书渲染。推送前先跑同一组命令，
把失败留在本机。默认做章节检查与全部游戏的构建；加 --render 再跑整书渲染。

用 config/config.toml 指定的解释器启动本脚本，子步骤沿用同一个解释器。
退出码：0 = 全部通过，1 = 有一步失败或工具缺失。
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parent


def games():
    """列出带运行入口的游戏，按目录名排序。"""
    return sorted(path.parent.name for path in ROOT.glob("games/*/running-build.sh"))


def run(label, command):
    """跑一步并打印标题；失败返回 False，不吞输出。"""
    print(f"\n==> {label}", flush=True)
    result = subprocess.run(command, cwd=ROOT, check=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="复现 CI 的检查序列")
    parser.add_argument("--render", action="store_true", help="额外执行整书渲染")
    args = parser.parse_args()

    steps = [("章节检查", [sys.executable, str(SCRIPTS / "checking-book.py")])]
    for game in games():
        steps.append((f"构建 {game}", [sys.executable, str(SCRIPTS / "building-wsl.py"), game]))
    if args.render:
        quarto = shutil.which("quarto")
        if quarto is None:
            print("找不到 quarto：先安装 Quarto，或去掉 --render", file=sys.stderr)
            return 1
        steps.append(("整书渲染", [quarto, "render"]))

    for label, command in steps:
        if not run(label, command):
            print(f"\n失败：{label}", file=sys.stderr)
            return 1

    print("\nOK：本地 CI 检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
