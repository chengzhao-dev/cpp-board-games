#!/usr/bin/env python3
"""导出不含游戏内容的 Agent 骨架，供以后的仓库初始化。

用法：python export_agent_skeleton.py <空目录>
退出码：0 = 写好；1 = 目标不合法或含禁止路径。
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
FILES = [
    ".agents/README.md",
    ".agents/skills/governing-agents/SKILL.md",
    ".agents/skills/governing-agents/references/structure.md",
    ".agents/skills/governing-agents/references/naming.md",
    ".agents/skills/governing-agents/references/bootstrap.md",
    ".agents/skills/governing-agents/scripts/run.py",
    ".agents/skills/governing-agents/scripts/run.ps1",
    ".agents/skills/maintaining-python/SKILL.md",
    ".agents/skills/maintaining-python/scripts/kb_common.py",
    ".agents/skills/maintaining-python/scripts/chunker.py",
    ".agents/skills/maintaining-python/scripts/indexer.py",
    ".agents/skills/maintaining-python/scripts/retriever.py",
    ".agents/skills/governing-agents/scripts/check_encoding.py",
    ".agents/skills/governing-agents/scripts/check_skill_size.py",
    ".agents/skills/governing-agents/scripts/check_commit_identity.py",
]
FORBIDDEN = ("content/", "games/", "game-design", "incidents/")


AGENTS = """# 项目 Agent 工作标准

本文件是这个仓库唯一的项目级 Agent 入口。解释器只读根目录 `config.toml` 的 `python`（最低 3.12），缺失即停。

## 待填写

- 这个仓库是什么。
- 目录表。
- 不能从文件看出来的命令。
- 安全上的不变量。

命令经 `.agents/skills/governing-agents/scripts/run.ps1` 进入 `run.py`。子命令以 `run.py` 文件头为准。不要在子目录再放 `AGENTS.md`。不要把 Python 来源改回 PATH 或 `runtime.json`。提交不使用 `Co-authored-by`。
"""


def main() -> int:
    if len(sys.argv) != 2:
        print("用法：export_agent_skeleton.py <空目录>")
        return 1
    dest = Path(sys.argv[1]).resolve()
    if dest.exists() and any(dest.iterdir()):
        print(f"目标不是空目录：{dest}")
        return 1
    for rel in FILES:
        if any(part in rel for part in ("content/", "games/", "game-design")):
            print(f"拒绝复制：{rel}")
            return 1
        src = ROOT / rel
        if not src.is_file():
            print(f"缺少骨架文件：{rel}")
            return 1
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    agents = dest / "AGENTS.md"
    agents.write_text(AGENTS, encoding="utf-8", newline="\n")
    (dest / "config.toml").write_text(
        'python = ""\nquarto_python_packages = []\n',
        encoding="utf-8",
        newline="\n",
    )
    knowledge = dest / ".agents/knowledge"
    knowledge.mkdir(parents=True, exist_ok=True)
    (knowledge / "KNOWLEDGE.md").write_text(
        "# 知识库\n\n领域文件放在 `<domain>/<subdomain>/`。先有文件再写路由。\n",
        encoding="utf-8",
        newline="\n",
    )
    memory = dest / ".agents/memory"
    memory.mkdir(parents=True, exist_ok=True)
    (memory / "MEMORY.md").write_text("# 记忆索引\n\n只做领域路由。\n", encoding="utf-8", newline="\n")
    incidents = dest / ".agents/incidents"
    incidents.mkdir(parents=True, exist_ok=True)
    (incidents / "INDEX.md").write_text("# 失败复盘索引\n\n仅排查失败时读。\n", encoding="utf-8", newline="\n")
    text = agents.read_text(encoding="utf-8")
    if "tictactoe" in text or "井字棋" in text:
        print("骨架 AGENTS.md 含游戏内容，停止")
        return 1
    if len(text.splitlines()) >= 150:
        print("骨架 AGENTS.md 不少于 150 行，停止")
        return 1
    print(f"已导出 {len(FILES)} 个文件到 {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
