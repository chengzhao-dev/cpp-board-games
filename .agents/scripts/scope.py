#!/usr/bin/env python3
"""本脚本解析任务作用域。输出本次任务「该读什么 / 不该读什么」的最小清单。

为什么需要它：上下文的量不由自觉控制。上下文的量由构造封顶。本脚本按仓库的阶段
路由表反查当前任务的最小文件集。构建产物、渲染产物、其他阶段一律列入禁止清单。
调用方只需读「单元」与「读取」所列文件。其余文件一律不碰。这样可省掉「整包多读」
与「反复枚举目录」。

零新增元数据：路由表就是 .agents/skills/cpp-workflow-project/stages/<game>.md；单游戏仓库也接受 stages/stage-table.md。
「公共必读」行给出该游戏每个阶段共用的 reference。「专项必读」列给出该阶段独有的
部分。「状态」列给出开工状态。路由表改名或新增阶段因此都不需要改本脚本。
本脚本只补读取边界。

用法：
  python scope.py <game>/<stage>        # 一个阶段单元（路由表登记即可解析，代码可尚未存在）
  python scope.py <仓库内任意路径>       # 由路径反查其所属阶段
  python scope.py theme|dev|repo        # 非阶段类域任务
  python scope.py --list                # 列出路由表登记的全部阶段单元与状态
退出码：0 = 解析成功，1 = 目标无法解析（提示按约定命名，不做猜测）。
"""

import argparse
import re
import sys
from pathlib import Path

# 构建产物目录：任何情况下都不进上下文。这些目录内含 CMakeCXXCompilerId.cpp 等
# 生成物。其中含 int main。误读会污染写作与评审判断。
BUILD_DIRS = ("build", ".cache", ".tmp", "temp", "__pycache__")
ALWAYS_DENY = [
    "_book/**（渲染产物：校验走 checking-dom.py 等脚本，不直接读）",
    "games/**/build/**（CMake 产物：永不入上下文）",
    ".quarto/**（Quarto 缓存）",
    "**/.cache/**（工具缓存）",
    "**/.tmp/**（临时文件）",
    "temp/**（统一临时产物目录）",
    # 宿主六项原则文件：只服务个性化设置。这些文件永不作为任务阅读项
    "宿主个性化说明（六项原则，来自用户全局配置）：不列入单元与读取",
]
# 单个单元的代码文件上限：超出则只报计数。上限可避免清单本身膨胀。
MAX_UNIT_FILES = 12
STAGES_DIR = ".agents/skills/cpp-workflow-project/stages"
STATUS_LABELS = {"todo": "待办", "done": "完成"}
# 该正则反查单元时剥离文件后缀（章节名与阶段同名，含连字符与 .cpp/.qmd/.txt）。
STEM_RE = re.compile(r"\.(qmd|cpp|cc|cxx|h|hpp|txt|sh|json|py)$")

TICK_RE = re.compile(r"`([^`]+)`")
REPO_PATH_PREFIX = (".agents/", "content/", "games/", "shared/")


def repo_root():
    return Path(__file__).resolve().parents[2]


def rel(path, root):
    return path.relative_to(root).as_posix()


def status_label(value):
    """把路由表状态转成用户可读的中文。"""
    return STATUS_LABELS.get(value, value)


def is_code_dir(entry):
    """判断目录内是否存在构建产物子目录。判断结果供提示使用。"""
    return any((entry / b).is_dir() for b in BUILD_DIRS)


def unit_files(directory, root):
    """列出一个代码目录里的源文件。构建产物被剔除。"""
    out = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        if any(part in BUILD_DIRS for part in path.relative_to(directory).parts[:-1]):
            continue
        out.append(rel(path, root))
    return out


def repo_paths(text):
    """从一行文本里取出反引号包裹的仓库路径。取出结果去重保序。"""
    seen, uniq = set(), []
    for cand in TICK_RE.findall(text):
        cand = cand.strip().strip("()")
        if cand.startswith(REPO_PATH_PREFIX) and cand not in seen:
            seen.add(cand)
            uniq.append(cand)
    return uniq


def stages_path(root, game):
    """查 game 对应的路由表文件；单游戏仓库也接受共用的 stage-table.md。"""
    path = root / STAGES_DIR / f"{game}.md"
    if path.is_file():
        return path
    shared = root / STAGES_DIR / "stage-table.md"
    return shared if shared.is_file() else None


def parse_table(path):
    """解析阶段路由表。返回值是 {stage: {qmd, code, code_paths, spec, status, note}}。"""
    rows = {}
    if not path or not path.is_file():
        return rows
    common = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("- **必读**"):
            common = repo_paths(line)
            break
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        stage = cells[0].strip("`")
        rows[stage] = {
            "qmd": first_path(cells[1]),
            "code": first_path(cells[2]),
            "code_paths": repo_paths(cells[2]),
            "spec": [p for p in repo_paths(cells[3]) if p not in common],
            "status": cells[4],
            "note": cells[4],
            "common": common,
        }
    return rows


def first_path(cell):
    """取单元格里的第一个仓库路径。「—（不新建）」之类返回空串。"""
    paths = repo_paths(cell)
    return paths[0] if paths else ""


def find_stage(target, root):
    """把 <game>/<stage> 解析成阶段单元（以路由表登记为准）。"""
    if "/" not in target:
        return None
    game, stage = target.split("/", 1)
    table_file = stages_path(root, game)
    row = parse_table(table_file).get(stage)
    if row is None:
        return None
    qmd = root / row["qmd"] if row["qmd"] else None
    return {"kind": "stage", "game": game, "stage": stage,
            "qmd": qmd if qmd and qmd.is_file() else None,
            "table": table_file, "row": row}


def find_stage_by_qmd(path, root):
    """由章节 qmd 路径反查阶段。章号与阶段号错位时按路由表登记匹配。"""
    for table in sorted((root / STAGES_DIR).glob("*.md")):
        for stage, row in parse_table(table).items():
            if not row["qmd"]:
                continue
            if (root / row["qmd"]).resolve() == path:
                qmd = root / row["qmd"]
                return {
                    "kind": "stage",
                    "game": table.stem,
                    "stage": stage,
                    "qmd": qmd if qmd.is_file() else None,
                    "table": table,
                    "row": row,
                }
    return None


def find_stage_by_code_path(path, root):
    """由游戏代码目录反查阶段。同一阶段可登记多个代码目录。"""
    for table in sorted((root / STAGES_DIR).glob("*.md")):
        game = table.stem
        for stage, row in parse_table(table).items():
            for code_path in row.get("code_paths", []):
                code_root = (root / code_path).resolve()
                try:
                    path.relative_to(code_root)
                except ValueError:
                    continue
                qmd = root / row["qmd"] if row["qmd"] else None
                return {
                    "kind": "stage",
                    "game": game,
                    "stage": stage,
                    "qmd": qmd if qmd and qmd.is_file() else None,
                    "table": table,
                    "row": row,
                }
    return None


def resolve_path(target, root):
    """由任意仓库内路径反查所属阶段单元。

    `content/<game>/<chapter>.qmd` 与默认代码路径按阶段名反查。路由表可登记多个
    代码目录。多目录时按路径前缀匹配对应阶段。两种反查都以路由表登记为前提。
    """
    path = (root / target).resolve()
    try:
        parts = rel(path, root).split("/")
    except ValueError:
        return None
    if len(parts) < 3 or parts[0] not in ("content", "games"):
        return None
    game = parts[1]
    stage = parts[2] if len(parts) > 3 else STEM_RE.sub("", parts[2])
    if not stage or stage == "index" or stage == ".gitkeep":
        return None
    return find_stage(f"{game}/{stage}", root) or find_stage_by_qmd(path, root) or find_stage_by_code_path(path, root)


DOMAIN_READ = {
    "theme": ["designing-theme 技能: SKILL.md",
              "theme/css/landing.css"],
    "dev": ["config/config.toml", ".editorconfig"],
    "repo": ["AGENTS.md", ".agents/README.md"],
}


def resolve_repo_domain(target, root):
    """把 .agents 下的 skill 或任意仓库路径解析成最小读取域。"""
    path = (root / target).resolve()
    try:
        rel_path = rel(path, root)
    except ValueError:
        return None
    parts = rel_path.split("/")
    if parts[:2] == [".agents", "skills"]:
        reads = [".agents/README.md"]
        label = "skills"
        if len(parts) >= 3 and parts[2]:
            label = f"skill {parts[2]}"
            reads.append(f".agents/skills/{parts[2]}/SKILL.md")
        if len(parts) > 3:
            reads.append(rel_path + ("/" if path.is_dir() else ""))
        return {"kind": "repo", "label": label, "reads": reads}
    if path.exists():
        # 阶段路由表没接住的 content/ 与 games/ 路径：读取边界同阶段单元。这类路径
        # 还要带中文注释必读。emit 据此补两份文件。theme/dev/repo 常规域不带该要求。
        path_domain = rel_path.split("/")[0] in ("content", "games")
        return {"kind": "repo", "label": "path", "reads": [rel_path], "path_domain": path_domain}
    return None


def emit(unit, root, out, verbose=False):
    """按固定格式打印范围、单元、读取和禁止清单。"""
    lines = out

    if unit["kind"] == "stage":
        game, stage, row = unit["game"], unit["stage"], unit["row"]
        lines.append(f"范围  阶段 {game}/{stage}")
        lines.append(f"任务  状态={status_label(row['status'])}")
        if unit["qmd"]:
            lines.append(f"单元  {rel(unit['qmd'], root)}")
        elif row["qmd"]:
            lines.append(f"单元  {row['qmd']}（待新建）")
        code_paths = row.get("code_paths")
        code_files = []
        created_dir = False
        for code_path in code_paths:
            candidate = (root / code_path).resolve()
            if candidate.is_file():
                code_files.append(rel(candidate, root))
            elif candidate.is_dir():
                created_dir = True
                code_files.extend(unit_files(candidate, root))
                if is_code_dir(candidate):
                    lines.append(f"暂停  {code_path.rstrip('/')}/build/ 存在构建产物：已排除，勿读")
        if code_paths and not created_dir and not code_files:
            lines.append(f"单元  {code_paths[0]}（待创建：实现并通过验收前按设计页阅读）")
        for item in code_files if verbose else code_files[:MAX_UNIT_FILES]:
            lines.append(f"单元  {item}")
        if not verbose and len(code_files) > MAX_UNIT_FILES:
            lines.append(f"单元  …共 {len(code_files)} 个源文件（已截断，--verbose 看全量）")
        lines.append(f"单元  {rel(unit['table'], root)}（阶段路由表：读取边界、状态与验收）")
        for ref in row["common"]:
            mark = "" if (root / ref).is_file() or (root / ref).is_dir() else "  ← 文件不存在，请核对"
            lines.append(f"读取  {ref}{mark}")
        for ref in row["spec"]:
            mark = "" if (root / ref).is_file() or (root / ref).is_dir() else "  ← 文件不存在，请核对"
            lines.append(f"读取  {ref}{mark}（本阶段专项）")
        lines.append("读取  writing-quarto 技能: SKILL.md")
        lines.append("读取  .agents/skills/quarto-book-project/glossary/forbidden-terms.md")
        lines.append("动笔前  先读上面两份。禁止先写：负责、承担、职责。")
        lines.append("禁止  其它 content/** 与 games/** 单元（跨章只按标题链接引用，不读正文）")
    else:
        label = unit.get("label", unit["kind"])
        kind = {"theme": "主题", "dev": "开发", "repo": "仓库"}.get(unit["kind"], unit["kind"])
        lines.append(f"范围  {kind} {label}".rstrip())
        refs = unit.get("reads") or DOMAIN_READ[unit["kind"]]
        for ref in refs:
            lines.append(f"读取  {ref}")
        if unit.get("path_domain"):
            lines.append("读取  writing-quarto 技能: SKILL.md")
            lines.append("读取  .agents/skills/quarto-book-project/glossary/forbidden-terms.md")
            lines.append("动笔前  先读上面两份。禁止先写：负责、承担、职责。")
        if unit["kind"] == "theme":
            lines.append("规则  只读取与当前任务直接相关的那一个主题资源或 CSS，禁止通读整个 css/。")
        lines.append("禁止  content/** 与 games/**（本域任务不改正文与游戏代码）")

    for deny in ALWAYS_DENY:
        lines.append(f"禁止  {deny}")
    lines.append("规则  只读单元与读取项；确需越界先一句声明理由（诊断逃生舱）")
    return lines


def all_units(root):
    """列出路由表登记的全部阶段单元：[(game/stage, status)]。"""
    units = []
    for table in sorted((root / STAGES_DIR).glob("*.md")):
        for stage, row in sorted(parse_table(table).items()):
            units.append((f"{table.stem}/{stage}", row["status"]))
    return units


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="解析任务作用域（单元、读取、禁止清单）")
    parser.add_argument("target", nargs="?", help="阶段 <game>/<stage>、.agents 下的技能，或 theme/dev/repo")
    parser.add_argument("--list", action="store_true", help="列出路由表登记的全部阶段单元")
    parser.add_argument("--verbose", action="store_true", help="展开被截断的单元文件")
    args = parser.parse_args()

    root = repo_root()

    if args.list:
        units = all_units(root)
        for unit, status in units:
            print(f"{unit}\t{status_label(status)}")
        todo = sum(1 for _u, s in units if s == "todo")
        print(f"（共 {len(units)} 个阶段单元：待办 {todo}，其余已完成）")
        return 0

    if not args.target:
        print("错误：缺少目标。用法见 python scope.py --help")
        return 1

    target = args.target.strip().strip("/\\").replace("\\", "/")

    if target in DOMAIN_READ:
        unit = {"kind": target}
    else:
        unit = find_stage(target, root) or resolve_path(target, root) or resolve_repo_domain(target, root)

    if not unit:
        print(f"无法解析目标：{target}")
        print("支持形式：<game>/<stage>、.agents 下的技能，或 theme/dev/repo。")
        print("阶段须先在 .agents/skills/cpp-workflow-project/stages/<game>.md 路由表登记；")
        print("未登记时请按约定补行，本脚本不做猜测。可用 --list 查看现有单元。")
        return 1

    out = []
    emit(unit, root, out, args.verbose)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
