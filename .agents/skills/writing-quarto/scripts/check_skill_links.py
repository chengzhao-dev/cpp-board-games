#!/usr/bin/env python3
"""检查所有 skills 的内部链接是否可解析。

覆盖范围：.agents/skills/governing-agents/references/catalog.md、各 SKILL.md、references/**/*.md 和 templates/*.qmd。
校验的链接形态：
  - <skill>/references/...、<skill>/templates/...（skills 根相对路径，catalog.md 用这种跨 skill 指路）
  - references/...、templates/...（skill 根相对路径）
  - scripts/...（skill 根相对路径，未命中时回退按仓库根 scripts/ 解析，两处任一存在即通过）
  - ./、../ 相对路径（含跨 skill 的 ../..）
  - .agents/... 全仓库路径
校验两类引用：
  - 带扩展名的 .md / .qmd / .py：目标必须存在。
  - 指向 references/ 的无扩展名引用：判为「漏写扩展名」直接 FAIL——该目录下的知识文件一律带
    .md，历史上曾有残留文件因无扩展名躲过全部检查。
模板路径（紧跟 <占位符> 的目录，如 references/tasks/<part>.md）只校验目录存在。
其余无扩展名路径（示例命令路径如 ./build/main）跳过。

用法：python check_skill_links.py
退出码：0 = 全部链接可达，1 = 存在断链。
"""

import os
import re
import sys

# catalog.md 用 `<skill>/references/...` 形式跨 skill 指路，必须先于无 skill 前缀的形态匹配，
# 否则会退化成「当前 skill 目录下的 references/...」而全部误判为断链。
LINK_RE = re.compile(
    r"\.agents/[A-Za-z0-9_./-]+"
    r"|[A-Za-z0-9_-]+/(?:references|templates|scripts)/[A-Za-z0-9_./-]+"
    r"|(?:references|templates|scripts)/[A-Za-z0-9_./-]+"
    r"|\.{1,2}/[A-Za-z0-9_./-]+"
)
VALID_EXT_RE = re.compile(r"\.(md|qmd|py)$")


def collect_files(skills_root):
    """待扫文件：catalog.md（skill 与 reference 的总路由表，已迁入 governing-agents/references/）+ 各 skill 的 SKILL.md/references/templates。"""
    files = []
    for catalog in (
        os.path.join(skills_root, "governing-agents", "references", "catalog.md"),
        os.path.join(skills_root, "catalog.md"),  # 兼容旧位置
    ):
        if os.path.isfile(catalog):
            files.append(catalog)
    for name in sorted(os.listdir(skills_root)):
        skill_dir = os.path.join(skills_root, name)
        if not os.path.isdir(skill_dir):
            continue
        candidates = [os.path.join(skill_dir, "SKILL.md")]
        refs = os.path.join(skill_dir, "references")
        if os.path.isdir(refs):
            for dirpath, _, filenames in os.walk(refs):
                candidates.extend(
                    os.path.join(dirpath, fn) for fn in filenames if fn.endswith(".md")
                )
        templates = os.path.join(skill_dir, "templates")
        if os.path.isdir(templates):
            candidates.extend(
                os.path.join(templates, fn) for fn in sorted(os.listdir(templates))
                if fn.endswith(".qmd")
            )
        files.extend(c for c in candidates if os.path.isfile(c))
    return files


def resolve_link(repo_root, skill_root, file_dir, link):
    """把三种形态的链接解析为仓库内绝对路径。"""
    if link.startswith(".agents/"):
        base, rel = repo_root, link
    elif link.startswith("./") or link.startswith("../"):
        base, rel = file_dir, link
    else:
        base, rel = skill_root, link
    return os.path.normpath(os.path.join(base, rel.replace("/", os.sep)))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    repo_root = os.getcwd()
    skills_root = os.path.join(repo_root, ".agents", "skills")
    if not os.path.isdir(skills_root):
        print(f"skills 目录不存在：{skills_root}")
        return 1

    bad = []
    for f in collect_files(skills_root):
        rel = os.path.relpath(f, skills_root).replace(os.sep, "/")
        # catalog.md 现位于 governing-agents/references/，其链接按仓库内 .agents/skills/ 下的相对路径解析
        skill_root = (
            skills_root if rel.endswith("catalog.md")
            else os.path.join(skills_root, rel.split("/")[0])
        )
        file_dir = os.path.dirname(f)
        with open(f, encoding="utf-8") as fh:
            text = fh.read()
        for m in LINK_RE.finditer(text):
            link = m.group(0)
            target = resolve_link(repo_root, skill_root, file_dir, link)
            if not VALID_EXT_RE.search(link):
                if text[m.end():m.end() + 1] == "<":
                    # 模板路径：截断处应为已存在的目录
                    if not os.path.isdir(target):
                        bad.append((rel, link, "模板路径的目录不存在"))
                    continue
                if "references/" in link and not os.path.isdir(target):
                    bad.append((rel, link, "无扩展名的 reference 引用（应带 .md）"))
                continue
            if not os.path.exists(target):
                if link.startswith((".agents/skills/governing-agents/scripts/",
                                     ".agents/skills/maintaining-python/scripts/")):
                    target = os.path.normpath(os.path.join(repo_root, link))
                elif link.startswith("scripts/"):
                    # 兼容 .agents/skills/maintaining-python/scripts 与 .agents/skills/governing-agents/scripts
                    cand1 = os.path.normpath(os.path.join(repo_root, ".agents", "skills", link))
                    cand2 = os.path.normpath(os.path.join(repo_root, ".agents", "tools",
                                                          os.path.basename(link)))
                    if os.path.exists(cand1):
                        target = cand1
                    elif os.path.exists(cand2):
                        target = cand2
            if not os.path.exists(target):
                bad.append((rel, link, os.path.relpath(target, repo_root)))

    if not bad:
        print("OK: all internal references/templates/scripts, relative links, and catalog entries resolve.")
        return 0

    print(f"Found {len(bad)} broken link(s):")
    for rel, link, reason in bad:
        print(f"  {rel} -> {link} ({reason})")
    return 1

if __name__ == "__main__":
    sys.exit(main())
