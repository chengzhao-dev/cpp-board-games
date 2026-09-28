#!/usr/bin/env python3
"""生成 C++ 项目骨架。

布局（--layout，默认 auto）：
  bare    仅 main.cpp，适合快速验证一段 C++ 代码。
  simple  main.cpp + CMakeLists.txt，不生成一键脚本。
  single  main.cpp + CMakeLists.txt + build-and-run.sh。
  multi   include/ + src/ + CMakeLists.txt + build-and-run.sh。
  static-library  greeting/ + 根 main.cpp + 静态库 CMake 工程。
  shared-library  greeting/ + 根 main.cpp + 动态库 CMake 工程。
  complete  single 的兼容别名。
  auto    目标在仓库 games/ 下 -> single，否则 -> simple。

标准用法（使用仓库配置的 Python 3.12）：
  python .agents/skills/maintaining-python/scripts/scaffold/init_project.py `
    --name cmake-project `
    --dir games/tic-tac-toe `
    --layout single
上例会自动创建 games/tic-tac-toe/cmake-project。
随后在 WSL2 Ubuntu 中进入项目目录并运行：
  bash build-and-run.sh

仓库根目录已配置好 Python 时，也可以使用：
  python .agents/skills/maintaining-python/scripts/scaffold/init_project.py `
    --name multi-file-project --dir games/tic-tac-toe --layout multi

库工程示例：
  python .agents/skills/maintaining-python/scripts/scaffold/init_project.py `
    --name static-library --dir games/tic-tac-toe --layout static-library

用法：python .agents/skills/maintaining-python/scripts/scaffold/init_project.py `
  --name <name> [--dir games/<game>] [--layout single|multi|static-library|shared-library]
退出码：0 成功，1 参数/路径错误。
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
CMAKE_PROJECT_NAME_PLACEHOLDER = "{{CMAKE_PROJECT_NAME}}"
LAYOUTS = (
    "auto",
    "bare",
    "simple",
    "single",
    "complete",
    "multi",
    "static-library",
    "shared-library",
)
LIBRARY_LAYOUTS = {"static-library", "shared-library"}

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[4]
CPP_CONFIG_DIR = (
    REPO_ROOT / ".agents" / "skills" / "cpp-development" / "assets" / "config"
)
PROJECT_TEMPLATE_DIR = (
    REPO_ROOT / ".agents" / "skills" / "cpp-development" / "assets" / "templates" / "projects"
)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"  create {path}")


def to_cmake_project_name(name):
    """把目录名转换为 CMake 常用的 PascalCase 工程名。"""
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[-_]+", name))


def render(template_path, target_path, cmake_project_name):
    text = template_path.read_text(encoding="utf-8")
    text = text.replace(CMAKE_PROJECT_NAME_PLACEHOLDER, cmake_project_name)
    write(target_path, text)


def render_tree(template_dir, target_dir, cmake_project_name):
    for template_path in sorted(template_dir.rglob("*")):
        if template_path.is_file():
            render(
                template_path,
                target_dir / template_path.relative_to(template_dir),
                cmake_project_name,
            )


def setup_development_configs(target_dir, no_clang):
    if no_clang:
        return
    for name in (".clang-format", ".clang-tidy", ".clangd"):
        bundled = CPP_CONFIG_DIR / name
        if not bundled.is_file():
            raise FileNotFoundError(f"缺少 C++ 配置模板：{bundled}")
        shutil.copyfile(bundled, target_dir / name)
        print(f"  copy   {name}")

    vscode_template = CPP_CONFIG_DIR / ".vscode"
    vscode_target = target_dir / ".vscode"
    vscode_target.mkdir(parents=True, exist_ok=True)
    for name in ("settings.json", "extensions.json"):
        bundled = vscode_template / name
        if not bundled.is_file():
            raise FileNotFoundError(f"缺少 VS Code 配置模板：{bundled}")
        shutil.copyfile(bundled, vscode_target / name)
        print(f"  copy   .vscode/{name}")


def readme_text(name, layout):
    lines = [f"# {name}", ""]
    if layout == "bare":
        lines += [
            "单文件验证：",
            "",
            "```bash",
            "# 直接编译运行",
            "clang++ -std=c++20 main.cpp -o app && ./app",
            "```",
        ]
    elif layout in LIBRARY_LAYOUTS:
        library_file = (
            "libgreeting.a" if layout == "static-library" else "libgreeting.so"
        )
        lines += [
            "这是一个使用 CMake 管理的 C++20 库工程。",
            "",
            "构建与运行：",
            "",
            "```bash",
            "# 配置 clang++ 与 Ninja Debug 构建",
            "cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_COMPILER=clang++",
            "",
            "# 构建库和 app",
            "cmake --build build",
            "",
            "# 运行 app",
            "./build/bin/app",
            "```",
            "",
            f"库文件生成在 `build/lib/{library_file}`，`app` 生成在 `build/bin/app`。",
            "",
            "配置阶段会生成 `build/compile_commands.json`，供 clangd 提供与实际构建一致的补全、跳转和诊断。",
        ]
    else:
        lines += [
            "这是一个使用 CMake 管理的 C++20 项目。",
            "",
            "构建与运行：",
            "",
            "```bash",
            "# 配置 clang++ 与 Ninja Debug 构建",
            "cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_COMPILER=clang++",
            "",
            "# 构建项目",
            "cmake --build build",
            "",
            "# 运行构建结果",
            "./build/bin/app",
            "```",
            "",
            "配置阶段会生成 `build/compile_commands.json`，供 clangd 提供与实际构建一致的补全、跳转和诊断。",
        ]
    return "\n".join(lines) + "\n"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="项目名（纯 ASCII；它会成为最终目录名）")
    parser.add_argument("--dir", default="games", help="目标父目录；脚本会创建 --dir/--name")
    parser.add_argument(
        "--layout",
        choices=LAYOUTS,
        default="auto",
        help="项目布局：single、multi、static-library 或 shared-library；另保留 bare/simple/complete 兼容用法",
    )
    parser.add_argument("--readme", action="store_true")
    parser.add_argument(
        "--no-clang", action="store_true", help="不生成 clangd/clang-format/VSCode 配置"
    )
    args = parser.parse_args()

    if not NAME_RE.match(args.name):
        print(f"错误：--name 必须为纯 ASCII，收到：{args.name}")
        return 1

    target = Path(args.dir) / args.name
    # 目标不存在时由 write() 创建。空目录可以安全复用，非空目录拒绝覆盖。
    if target.exists() and any(target.iterdir()):
        print(f"错误：目标目录已存在且非空：{target}")
        return 1

    layout = args.layout
    if layout == "auto":
        try:
            target.resolve().relative_to(REPO_ROOT / "games")
            layout = "single"
        except ValueError:
            layout = "simple"
    elif layout == "complete":
        layout = "single"
    print(f"布局：{layout}（目标：{target}）")

    name = args.name
    cmake_project_name = to_cmake_project_name(name)
    if layout == "bare":
        write(
            target / "main.cpp",
            (PROJECT_TEMPLATE_DIR / "single" / "main.cpp").read_text(encoding="utf-8"),
        )
    elif layout == "simple":
        render(
            PROJECT_TEMPLATE_DIR / "single" / "main.cpp",
            target / "main.cpp",
            cmake_project_name,
        )
        render(
            PROJECT_TEMPLATE_DIR / "single" / "CMakeLists.txt",
            target / "CMakeLists.txt",
            cmake_project_name,
        )
    elif layout == "single":
        render(
            PROJECT_TEMPLATE_DIR / "single" / "main.cpp",
            target / "main.cpp",
            cmake_project_name,
        )
        render(
            PROJECT_TEMPLATE_DIR / "single" / "CMakeLists.txt",
            target / "CMakeLists.txt",
            cmake_project_name,
        )
        render(
            PROJECT_TEMPLATE_DIR / "common" / "build-and-run.sh",
            target / "build-and-run.sh",
            cmake_project_name,
        )
    elif layout == "multi":
        render_tree(PROJECT_TEMPLATE_DIR / "multi", target, cmake_project_name)
        render(
            PROJECT_TEMPLATE_DIR / "common" / "build-and-run.sh",
            target / "build-and-run.sh",
            cmake_project_name,
        )
    else:
        render_tree(PROJECT_TEMPLATE_DIR / "library", target, cmake_project_name)
        render_tree(PROJECT_TEMPLATE_DIR / layout, target, cmake_project_name)
        render(
            PROJECT_TEMPLATE_DIR / "common" / "build-and-run.sh",
            target / "build-and-run.sh",
            cmake_project_name,
        )

    try:
        setup_development_configs(target, args.no_clang)
    except FileNotFoundError as exc:
        print(f"错误：{exc}")
        return 1
    if args.readme:
        write(target / "README.md", readme_text(name, layout))

    if layout == "bare":
        print("\n下一步：编辑源码并用 clang++ 直接编译验证。")
    elif layout in {"single", "multi"} | LIBRARY_LAYOUTS:
        print("\n下一步：编辑源码并运行 bash build-and-run.sh。")
    else:
        print("\n下一步：编辑源码并运行 cmake -S . -B build -G Ninja "
              "-DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_COMPILER=clang++。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
