# test_verify_content.py - verify_content.py 任务级标题门禁的回归自测
#
# 用临时 qmd 样例核对三条规则：任务级 `##` 超过 4 个失败、固定收尾节
# 不计入任务数、着陆页与代码围栏内的伪标题不触发限制。由 run.py 的
# fast profile 调用；规则正文见标识 bg-content-budget-v1 的知识文件。

import importlib.util
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "verify_content.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_content", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_sample(directory: Path, name: str, frontmatter: str, headings) -> Path:
    parts = [frontmatter] if frontmatter else []
    for heading in headings:
        parts.append(f"{heading}\n\n正文。\n")
    path = directory / name
    path.write_text("\n".join(parts), encoding="utf-8", newline="\n")
    return path


def main() -> None:
    module = load_module()
    fixed = ["## 常见错误", "## 自测问题", "## 本章回顾"]
    content_root = module.REPO_ROOT / "content"
    failures = []

    with tempfile.TemporaryDirectory(dir=content_root) as temp:
        temp_path = Path(temp)

        four = write_sample(temp_path, "four.qmd", "", [f"## 任务{i}" for i in range(1, 5)] + fixed)
        errors = module.check_file_budget(four)
        if errors:
            failures.append(f"四个任务级标题不应报错：{errors}")

        five = write_sample(temp_path, "five.qmd", "", [f"## 任务{i}" for i in range(1, 6)] + fixed)
        errors = module.check_file_budget(five)
        if len(errors) != 1 or "任务级二级标题" not in errors[0]:
            failures.append(f"五个任务级标题应只报任务数超限：{errors}")

        fence = write_sample(
            temp_path,
            "fence.qmd",
            "",
            ["## 任务一", "```bash", "## 这不是标题", "```", "## 任务二"],
        )
        errors = module.check_file_budget(fence)
        if errors:
            failures.append(f"围栏内伪标题不应计入：{errors}")

        landing = write_sample(
            temp_path,
            "index.qmd",
            "---\ntitle: 着陆页\nbody-classes: index-page\n---\n",
            [f"## 卡片{i}" for i in range(1, 7)],
        )
        errors = module.check_file_budget(landing)
        if errors:
            failures.append(f"着陆页不应触发任务级标题限制：{errors}")

    if failures:
        for line in failures:
            print(f"失败  {line}")
        raise SystemExit(1)
    print("内容规则自测：4 项全部通过")


if __name__ == "__main__":
    main()
