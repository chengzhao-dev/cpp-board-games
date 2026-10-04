#!/usr/bin/env python3
"""agent 命令统一入口：把易踩坑的 Windows 调用包成稳定的单轮输出。

为什么需要它：省 token 的最大杠杆不是「少读文件」，而是「少几轮」。Windows 上
手写命令常因引号与编码失败，渲染与校验的原始输出动辄上千行。本脚本用 Python
直接 subprocess 调用（不经 PowerShell 解析），成功只回一行中文结论，失败才展开
末尾若干行。

子命令：
  check   按 fast|book|knowledge|python|full profile 运行校验（默认 full；缺少 _book 时显示跳过）
  verify  增量校验文档内容（verify_content.py 的 --changed/--paths 包装）
  render  渲染 Book 并自动跑 book profile 校验（合并为 1 轮）
  preview 本地 preview（注入 config.toml 的 QUARTO_PYTHON，可传 .qmd 路径）
  install-quarto-deps  用 config.toml 安装 Quarto 可执行单元依赖
  scope   解析任务作用域，输出范围、单元、读取和禁止清单
  build   在 WSL 中运行某编号阶段的 build-and-run.sh
  status  精简 git 状态：默认折叠内容与工程域改动，只看维护域
  kb-index  增量或全量重建知识库索引（.agents/knowledge/ -> temp/knowledge-index/）
  kb-search  知识库单次检索（透传 retriever 参数，如 --toc/--parent/--explain）
  kb-check  知识库健康度与检索延迟测量
  kb-eval   标注集召回率与 Token 预算验收（延迟由 kb-check 负责）
通用参数：
  --verbose  展开全部原始输出（仅失败排查时使用）
退出码：透传被包装命令的退出码，0 = 成功。

与 cpp-notes 的差异：本仓 C++ 验证只走各阶段 build-and-run.sh（build 子命令），
没有 verify_examples 编译管线；run.py 本体可由任意 >= 3.12 的解释器启动，子进程
统一用 config.toml 的 python（CI 通过改写 config.toml 切换）。
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MIN_PYTHON = (3, 12)
CONFIG = ROOT / "config.toml"


class ToolNotFound(RuntimeError):
    """外部工具未找到。"""


def python_version(candidate):
    """返回解释器版本元组。无法执行时返回空值。"""
    try:
        result = subprocess.run(
            [candidate, "-c", "import sys; print(sys.version_info[:2])"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False,
        )
        value = result.stdout.strip().strip("()")
        major, minor = (int(part.strip()) for part in value.split(","))
        return major, minor
    except (OSError, ValueError):
        return None


def load_config():
    """读取根目录工具配置；配置错误由调用方显示为明确失败。"""
    import tomllib

    return tomllib.loads(CONFIG.read_text(encoding="utf-8"))


def select_python():
    """只使用根目录 config.toml 的 python 字段且满足最低版本的解释器。"""
    try:
        config = load_config()
    except (ImportError, OSError, UnicodeDecodeError, ValueError):
        return None
    candidate = str(config.get("python") or "").strip()
    if not candidate or not Path(candidate).is_file():
        return None
    version = python_version(candidate)
    if version and version >= MIN_PYTHON:
        return candidate
    return None


def quarto_python_packages():
    """返回 config.toml 声明的 Quarto 可执行单元运行时依赖。"""
    try:
        packages = load_config().get("quarto_python_packages", [])
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"无法读取 config.toml：{exc}") from exc
    if not isinstance(packages, list) or any(
        not isinstance(package, str) or not package.strip() for package in packages
    ):
        raise ValueError("config.toml 的 quarto_python_packages 必须是非空字符串数组")
    return [package.strip() for package in packages]


PY = select_python()


def resolve_tool(name):
    """从环境变量与 PATH 解析外部工具；.cmd 包装器优先换成同目录 .exe。"""
    env_name = "BOARD_GAMES_" + name.upper()
    candidates = [os.environ.get(env_name), shutil.which(name)]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            # Windows 的 PATH 常先返回 .cmd 包装器。Quarto 的 .cmd 会把
            # Deno/Sass 相对路径解析到当前工作目录，优先同目录 .exe 可避免该问题。
            if Path(candidate).suffix.lower() == ".cmd":
                executable = Path(candidate).with_suffix(".exe")
                if executable.is_file():
                    return str(executable)
            return str(candidate)
    raise ToolNotFound(f"找不到工具 {name}；请安装后加入 PATH 或设置 {env_name}")


# 校验项：(名称, 脚本相对路径, 需要 _book 产物, 固定参数)
CHECKS = [
    ("encoding", ".agents/skills/governing-agents/scripts/check_encoding.py", False, ()),
    ("identity", ".agents/skills/governing-agents/scripts/check_commit_identity.py", False, ()),
    ("agent-controls", ".agents/skills/governing-agents/scripts/test_agent_controls.py", False, ()),
    ("size", ".agents/skills/governing-agents/scripts/check_skill_size.py", False, ()),
    ("ascii", ".agents/skills/writing-quarto/scripts/check_ascii_names.py", False, ()),
    ("links", ".agents/skills/writing-quarto/scripts/check_skill_links.py", False, ()),
    ("content", ".agents/skills/writing-quarto/scripts/verify_content.py", False, ()),
    ("content-selftest", ".agents/skills/writing-quarto/scripts/test_verify_content.py", False, ()),
    ("docs", ".agents/skills/governing-agents/scripts/check_docs.py", False, ()),
    ("layout", ".agents/skills/designing-theme/scripts/check_layout.py", True, ()),
    ("callouts", ".agents/skills/writing-quarto/scripts/check_callouts.py", True, ()),
    ("dom", ".agents/skills/governing-agents/scripts/check_dom_contracts.py", True, ()),
    ("book-output", ".agents/skills/writing-quarto/scripts/check_book_output.py", True, ()),
    ("scaffold", ".agents/skills/maintaining-python/scripts/test_scaffold_projects.py", False, ()),
    ("kb", ".agents/skills/maintaining-python/scripts/check_health.py", False, ("--gate",)),
    ("kb-eval", ".agents/skills/maintaining-python/scripts/evaluator.py", False, ("--skip-latency",)),
    ("conflict", ".agents/skills/maintaining-python/scripts/test_conflict_detection.py", False, ()),
]

PROFILE_CHECKS = {
    "fast": {"encoding", "agent-controls", "size", "ascii", "links", "content", "content-selftest", "docs", "identity"},
    "book": {"layout", "callouts", "dom", "book-output"},
    "knowledge": {"kb", "kb-eval", "conflict"},
    "python": {"scaffold"},
}

# 成功判据行：命中即认为该步通过，用于从大输出里挑出唯一有价值的一行
PASS_HINTS = ("PASS", "OK:", "OK  ", "全部通过", "qmd 与片段检查通过", "无阻塞", "DOM contracts")
CHECK_LABELS = {
    "encoding": "编码",
    "identity": "提交身份",
    "agent-controls": "Agent 控制",
    "size": "上下文体量",
    "ascii": "文件名",
    "links": "链接",
    "content": "文档内容",
    "content-selftest": "内容自测",
    "docs": "文档结构",
    "layout": "布局",
    "callouts": "提示框",
    "dom": "页面结构",
    "book-output": "发布产物",
    "scaffold": "脚手架",
    "kb": "知识库",
    "kb-eval": "知识库评测",
    "conflict": "冲突检测",
}
COMMAND_LABELS = {
    "kb-index": "知识库索引",
    "kb-check": "知识库检查",
    "kb-eval": "知识库评测",
}


def display_check(item):
    """把内部检查名转换成中文状态文本。"""
    name, separator, detail = item.partition(":")
    label = CHECK_LABELS.get(name, name)
    return f"{label}（{detail}）" if separator else label


def display_command(label):
    """把内部子命令名转换成中文状态文本。"""
    return COMMAND_LABELS.get(label, label)


def checks_for_profile(profile):
    """返回指定 profile 的校验项；full 保持全部检查。"""
    if profile == "full":
        return CHECKS
    names = PROFILE_CHECKS[profile]
    return [item for item in CHECKS if item[0] in names]


def to_wsl_path(win_path):
    """把 Windows 绝对路径转成 WSL 可见路径：D:\\a\\b -> /mnt/d/a/b。"""
    s = str(win_path).replace("\\", "/")
    return "/mnt/" + s[0].lower() + s[2:]


def run(argv, cwd=ROOT):
    """执行命令并捕获输出（bytes 手工解码，绕开 PowerShell 与 GBK 问题）。"""
    command = list(argv)
    if command and not Path(command[0]).is_file():
        command[0] = resolve_tool(command[0])
    child_env = dict(os.environ)
    if PY:
        child_env["PYTHONIOENCODING"] = "utf-8"
        # Quarto 的 jupyter 引擎经 QUARTO_PYTHON 定位解释器；本仓仍只认 config.toml 的 python。
        child_env["QUARTO_PYTHON"] = PY
    proc = subprocess.run(command, cwd=str(cwd), env=child_env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    text = proc.stdout.decode("utf-8", errors="replace")
    return proc.returncode, text


def tail(text, n):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return lines[-n:]


def interpret(rc, text, verbose, label):
    """分级输出：成功一行、失败展开末尾若干行。"""
    if rc == 0:
        if verbose:
            print(text.rstrip())
        else:
            print(f"通过  {display_command(label)}")
        return 0
    print(f"失败  {display_command(label)}（退出码 {rc}）")
    for ln in tail(text, 60 if verbose else 15):
        print(f"      {ln}")
    return rc


def cmd_check(args):
    """运行指定 profile 的校验。默认只回一行总结。"""
    checks = checks_for_profile(args.profile)
    details, failed, skipped = [], [], []
    kb_ready = True
    if any(name in {"kb", "kb-eval"} for name, *_rest in checks):
        rc = ensure_kb_index()
        if rc != 0:
            failed.append("kb:index")
            kb_ready = False
    with_book = (ROOT / "_book").is_dir()
    for name, script, need_book, extra in checks:
        path = ROOT / script
        if not path.is_file():
            failed.append(f"{name}:脚本缺失")
            continue
        if name in {"kb", "kb-eval"} and not kb_ready:
            continue
        if need_book and not with_book:
            skipped.append(f"{CHECK_LABELS.get(name, name)}：未渲染")
            continue
        argv = [PY, str(path), *extra]
        if need_book:
            argv += ["--book-dir", "_book"]
        if name == "content" and with_book:
            # 渲染产物存在时才扫描 HTML；_book 缺失时脚本自身会跳过该节。
            argv.append("--book")
        rc, text = run(argv)
        if rc != 0:
            failed.append(name)
            if args.verbose:
                print(f"--- {name} ---")
                print(text.rstrip())
            continue
        report_line = next(
            (ln for ln in text.splitlines() if ln.startswith("REPORT ")), ""
        )
        if report_line:
            details.append(f"{name}={report_line.strip()}")
        skip_line = next(
            (ln.strip() for ln in text.splitlines() if ln.strip().startswith("SKIP ")),
            "",
        )
        if skip_line:
            skipped.append(f"{CHECK_LABELS.get(name, name)}：{skip_line.removeprefix('SKIP ').strip()}")
        last = next(
            (ln.strip() for ln in reversed(text.splitlines())
             if any(h in ln for h in PASS_HINTS)),
            "",
        )
        details.append(f"{name}={skip_line or last or 'ok'}")

    if not failed:
        suffix = ""
        if skipped:
            suffix += f"；跳过 {len(skipped)} 项"
        print(f"通过  检查（{args.profile}）：{len(checks)} 项全通过{suffix}")
        if args.verbose:
            for d in details:
                print(f"      {d}")
        return 0
    print(f"失败  检查（{args.profile}）：{', '.join(display_check(item) for item in failed)}")
    if not args.verbose:
        print("      提示：加 --verbose 查看失败项详情")
    return 1


def cmd_verify(args):
    """增量校验文档内容：verify_content.py 的 --changed/--paths 包装。"""
    argv = [PY, str(ROOT / ".agents/skills/writing-quarto/scripts/verify_content.py")]
    if args.book:
        argv.append("--book")
    if args.paths:
        argv += ["--paths", *args.paths]
    elif args.changed:
        argv.append("--changed")
    rc, text = run(argv)
    if args.verbose:
        print(text.rstrip())
        return rc
    if rc != 0:
        print(f"失败  文档内容校验（退出码 {rc}）")
        for ln in tail(text, 25):
            print(f"      {ln}")
        return rc
    last = next(
        (ln.strip() for ln in reversed(text.splitlines())
         if any(h in ln for h in PASS_HINTS)),
        "",
    )
    print(f"通过  文档内容校验{f'；{last}' if last else ''}")
    return 0


def cmd_render(args):
    """渲染 Book 后运行 book profile；渲染必须在仓库根目录执行。"""
    rc, text = run(["quarto", "render"])
    if rc != 0:
        print(f"失败  渲染（退出码 {rc}）")
        for ln in tail(text, 30):
            print(f"      {ln}")
        return rc
    defer = ROOT / ".agents/skills/maintaining-python/scripts/render/defer_mermaid.py"
    defer_rc, defer_text = run([PY, str(defer), "_book"])
    if defer_rc != 0:
        print(f"失败  Mermaid defer（退出码 {defer_rc}）")
        for ln in tail(defer_text, 15):
            print(f"      {ln}")
        return defer_rc
    err = [ln for ln in text.splitlines() if "WARNING" in ln or "ERROR" in ln]
    print(f"通过  渲染：警告或错误 {len(err)} 条")
    if args.skip_check:
        return 0
    args.profile = "book"
    return cmd_check(args)


def cmd_preview(args):
    """本地 preview：注入 QUARTO_PYTHON 后调用 quarto preview（须在仓库根目录）。"""
    cmd = ["quarto", "preview"]
    if args.target:
        cmd.append(args.target)
    if args.port is not None:
        cmd.extend(["--port", str(args.port)])
    # preview 为长驻进程；直接交给子进程，不捕获输出。
    child_env = os.environ.copy()
    if PY:
        child_env["PYTHONIOENCODING"] = "utf-8"
        child_env["QUARTO_PYTHON"] = PY
    try:
        return subprocess.call(cmd, cwd=ROOT, env=child_env)
    except FileNotFoundError:
        print("失败  未找到 quarto，请先安装 Quarto CLI")
        return 1


def cmd_install_quarto_deps(args):
    """用 config.toml 的受控解释器安装 Quarto 可执行单元依赖。"""
    try:
        packages = quarto_python_packages()
    except ValueError as exc:
        print(f"失败  Quarto Python 依赖：{exc}")
        return 1
    if not packages:
        print("通过  Quarto Python 依赖：未声明依赖，跳过安装")
        return 0
    rc, text = run([PY, "-m", "pip", "install", *packages])
    if rc != 0:
        print(f"失败  Quarto Python 依赖（退出码 {rc}）")
        for ln in tail(text, 15):
            print(f"      {ln}")
        return rc
    print(f"通过  Quarto Python 依赖：已安装 {len(packages)} 项")
    return 0


def cmd_scope(args):
    argv = [PY, str(ROOT / ".agents/skills/governing-agents/scripts/scope.py")]
    if args.list:
        argv.append("--list")
    if args.verbose:
        argv.append("--verbose")
    if args.target:
        argv.append(args.target)
    rc, text = run(argv)
    print(text.rstrip())
    return rc


def cmd_build(args):
    """按需启动 WSL 运行编号阶段的一键构建脚本。"""
    target = args.target.strip("/\\")
    script = ROOT / "games" / target / "build-and-run.sh"
    if not script.is_file():
        print(f"失败  构建：找不到 {script.relative_to(ROOT)}")
        return 1
    env_path = to_wsl_path(script.parent)
    rc, text = run(["wsl.exe", "bash", "-lc", f"cd '{env_path}' && bash build-and-run.sh"])
    if rc != 0:
        print(f"失败  构建 {target}（退出码 {rc}）")
        for ln in tail(text, 20):
            print(f"      {ln}")
        return rc
    print(f"通过  构建 {target}")
    if args.verbose:
        for ln in tail(text, 8):
            print(f"      {ln}")
    return 0


def cmd_status(args):
    """git 状态：按维护域与内容域归类，不推断改动归属。"""
    rc, text = run(["git", "status", "--porcelain"])
    maintenance, content = [], []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        body = ln[3:].split(" -> ")[-1].strip().strip('"')
        (maintenance if status_group(body) == "maintenance" else content).append(ln)
    print(f"维护域文件 {len(maintenance)} 项 / 内容与工程域 {len(content)} 项")
    if args.verbose or args.all:
        for ln in maintenance:
            print(f"  {ln}")
    if args.all:
        for ln in content:
            print(f"  (内容/工程) {ln}")
    return rc


def status_group(path):
    """按文件域归类 git 状态，不推断改动作者。"""
    maintenance_prefixes = (".agents/", "AGENTS.md", "config.toml", ".gitattributes", ".gitignore")
    return "maintenance" if path.startswith(maintenance_prefixes) else "content"


KB_INDEX_DB = "temp/knowledge-index/kb_index.sqlite"


def kb_script(name):
    """拼出 .agents/skills/maintaining-python/scripts/ 下的知识库脚本绝对路径。"""
    return str(ROOT / ".agents" / "skills" / "maintaining-python" / "scripts" / name)


def ensure_kb_index():
    """索引产物不入库（见 .gitignore），缺失时先全量重建，避免子命令空跑。"""
    if (ROOT / KB_INDEX_DB).is_file():
        return 0
    print("提示  知识库索引缺失，正在全量重建")
    rc, text = run([PY, kb_script("indexer.py"), "--rebuild"])
    if rc != 0:
        print(f"失败  知识库索引（退出码 {rc}）")
        for ln in tail(text, 12):
            print(f"      {ln}")
        return rc
    return rc


def cmd_kb_index(args):
    """重建或增量更新索引。"""
    argv = [PY, kb_script("indexer.py")]
    if args.rebuild:
        argv.append("--rebuild")
    rc, text = run(argv)
    return interpret(rc, text, args.verbose, "kb-index")


def cmd_kb_search(args):
    """检索知识库：retriever 已按预算输出，故直接透传结果。"""
    rc = ensure_kb_index()
    if rc != 0:
        return rc
    rc, text = run([PY, kb_script("retriever.py"), *args.rest])
    print(text.rstrip())
    return rc


def cmd_kb_check(args):
    """知识库健康度检查（结构 + 延迟）。"""
    rc = ensure_kb_index()
    if rc != 0:
        return rc
    argv = [PY, kb_script("check_health.py")]
    if args.gate:
        argv.append("--gate")
    if args.verbose:
        argv.append("--verbose")
    rc, text = run(argv)
    return interpret(rc, text, args.verbose, "kb-check")


def cmd_kb_eval(args):
    """标注集验收：Top-K 召回率与注入令牌，延迟由 kb-check 负责。"""
    rc = ensure_kb_index()
    if rc != 0:
        return rc
    argv = [PY, kb_script("evaluator.py"), "--topk", str(args.topk), "--skip-latency"]
    if args.verbose:
        argv.append("--verbose")
    rc, text = run(argv)
    return interpret(rc, text, args.verbose, "kb-eval")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if PY is None:
        print("失败  config.toml 未提供可执行的 Python >= 3.12；请修复根目录 config.toml 的 python 字段")
        return 1
    if sys.version_info < MIN_PYTHON:
        required = ".".join(map(str, MIN_PYTHON))
        print(f"失败  Python 需要 >= {required}，当前为 {sys.version.split()[0]}；请切换解释器")
        return 1

    # 公共参数：用 parents 挂到每个子命令上，这样 --verbose 放前放后都能识别
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--verbose", action="store_true", help="展开完整原始输出")

    parser = argparse.ArgumentParser(description="agent 命令统一入口（默认 terse 输出）")
    subs = parser.add_subparsers(dest="cmd", required=True)

    p = subs.add_parser("check", parents=[common], help="一次跑完 profile 内全部校验")
    p.add_argument("--profile", choices=("fast", "book", "knowledge", "python", "full"),
                   default="full",
                   help="校验范围：fast=编码+体量+内容，book=渲染产物，knowledge=知识库，python=脚手架；默认 full")
    p.add_argument("--strict", action="store_true",
                   help="把体量建议阈值升级为失败（作用于 size）")
    p = subs.add_parser("verify", parents=[common], help="增量校验文档内容")
    p.add_argument("--changed", action="store_true", help="只校验相对 HEAD 修改的 qmd")
    p.add_argument("--paths", nargs="+", help="只校验指定 qmd 路径")
    p.add_argument("--book", action="store_true", help="同时扫描 _book 渲染产物")
    p = subs.add_parser("render", parents=[common], help="渲染并自动校验")
    p.add_argument("--skip-check", action="store_true", help="渲染后不跑校验")
    p = subs.add_parser("preview", parents=[common], help="本地 preview（注入 QUARTO_PYTHON）")
    p.add_argument("target", nargs="?", help="可选：单个 .qmd 路径")
    p.add_argument("--port", type=int, help="可选：preview 端口")
    subs.add_parser("install-quarto-deps", parents=[common],
                    help="用 config.toml 安装 Quarto 可执行单元依赖")
    p = subs.add_parser("scope", parents=[common], help="输出任务作用域清单")
    p.add_argument("target", nargs="?")
    p.add_argument("--list", action="store_true")
    p = subs.add_parser("build", parents=[common], help="WSL 内跑阶段一键构建")
    p.add_argument("target", help="games/ 下的相对路径，如 tictactoe/01-cli-game")
    p = subs.add_parser("status", parents=[common], help="精简 git 状态")
    p.add_argument("--all", action="store_true", help="同时列出内容与工程域改动")
    p = subs.add_parser("kb-index", parents=[common], help="重建或增量更新知识库索引")
    p.add_argument("--rebuild", action="store_true", help="清空索引后全量重建")
    p = subs.add_parser("kb-search", parents=[common], help="知识库检索（参数透传 retriever）")
    p.add_argument("rest", nargs=argparse.REMAINDER, help="查询串与 retriever 参数（顺序任意）")
    p = subs.add_parser("kb-check", parents=[common], help="知识库健康度与延迟")
    p.add_argument("--gate", action="store_true", help="只把结构性问题视为失败")
    p = subs.add_parser("kb-eval", parents=[common], help="标注集召回率与预算验收")
    p.add_argument("--topk", type=int, default=5, help="召回评价的 K，默认 5")

    args, extra = parser.parse_known_args()
    if args.cmd == "kb-search":
        # retriever 的参数表由 retriever.py 自己定义，本解析器只做统一入口，
        # 故按原始 argv 顺序整体接管 kb-search 之后的参数，避免 --toc 这类
        # flag 被本层吞掉后报 unrecognized arguments。--verbose 归本层使用。
        tail_args = sys.argv[sys.argv.index("kb-search") + 1:]
        args.rest = [t for t in tail_args if t != "--verbose"]
    elif extra:
        parser.error("未识别的参数: " + " ".join(extra))
    handlers = {"check": cmd_check, "verify": cmd_verify, "render": cmd_render,
                "preview": cmd_preview,
                "install-quarto-deps": cmd_install_quarto_deps, "scope": cmd_scope,
                "build": cmd_build, "status": cmd_status,
                "kb-index": cmd_kb_index, "kb-search": cmd_kb_search,
                "kb-check": cmd_kb_check, "kb-eval": cmd_kb_eval}
    try:
        return handlers[args.cmd](args)
    except ToolNotFound as exc:
        print(f"失败  {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
