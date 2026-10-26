#!/usr/bin/env python3
"""在 WSL（Windows）或本机 bash（CI）里构建一个游戏工程。

参数是 games/ 下的工程目录名，例如 tictactoe。脚本只做一件事：把
games/<game>/running-build.sh 交给 bash 执行；不折叠输出、不跑 quarto、
不看 git 状态。构建脚本自己负责配置、编译和测试。

用法：
  python .agents/scripts/building-wsl.py tictactoe

退出码：0 = 构建脚本通过，非 0 = 构建脚本的退出码。
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main(argv):
    if len(argv) != 1:
        print("用法：building-wsl.py <games/ 下的工程名>")
        return 1
    game = argv[0].strip().strip("/\\")
    if not game or Path(game).name != game:
        print(f"失败  工程名只能是 games/ 下的一层目录：{argv[0]}")
        return 1
    script = ROOT / "games" / game / "running-build.sh"
    if not script.is_file():
        print(f"失败  找不到 games/{game}/running-build.sh")
        return 1
    if os.name != "nt":
        return subprocess.run(
            ["bash", "running-build.sh"], cwd=str(script.parent), check=False
        ).returncode
    windows_path = str(script.parent).replace("\\", "/")
    wsl_path = "/mnt/" + windows_path[0].lower() + windows_path[2:]
    return subprocess.run(
        ["wsl.exe", "bash", "-lc", f"cd '{wsl_path}' && bash running-build.sh"],
        check=False,
    ).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
