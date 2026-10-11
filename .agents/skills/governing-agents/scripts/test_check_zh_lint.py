# test_check_zh_lint.py - check_zh_lint.py 的回归自测
#
# 用内存样例核对十三条规则的命中与豁免：注释以「表示」开头与相邻重复注释行命中，
# 纯分隔线与空注释行不报；正文六条规则命中；句式禁令（下一节/上一节、代码把它写成、
# 第二道…防线）在正文与 agent 文档命中，紧贴引号或反引号的术语引用豁免；
# 「由…完成」只拦读者 qmd 围栏外正文。
# 由 run.py 的 fast profile 调用；规则正文见标识 bg-chinese-quality-v1、
# bg-comment-style-v1、bg-paragraph-craft-v1 与 bg-terminology-v1 的知识文件。

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_zh_lint.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_zh_lint", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    module = load_module()
    failures = []

    def expect(case, got, want):
        if got != want:
            failures.append(f"{case}：期望 {want}，实际 {got}")

    comment_case = "/// 表示一局对局。\n// 棋盘为 3 行 3 列。\n// 棋盘为 3 行 3 列。\n"
    got = [key for _, key, _ in module.scan_text(Path("x.h"), comment_case, True, False)]
    expect("注释规则命中「表示」与相邻重复", got, ["bai-shi", "duplicate-comment"])

    separator_case = "//===------===//\n//===------===//\n///\n///\n// --\n// --\n"
    got = [key for _, key, _ in module.scan_text(Path("x.h"), separator_case, True, False)]
    expect("纯分隔线与空注释行豁免", got, [])

    prose_case = (
        "见[定义棋盘与格子状态](x.qmd)。\n"
        "覆盖四类场景：拒绝落子、按行获胜、以及获胜后再落子被拒绝。\n"
        "九格按行依次排列。\n"
        "这是一份的的重复写法。\n"
        "进行棋盘状态的实现。\n"
        "棋盘状态存放在私有段的一个数组里。\n"
    )
    got = [key for _, key, _ in module.scan_text(Path("x.qmd"), prose_case, False, True)]
    expect(
        "正文规则命中六条",
        got,
        ["stale-link-label", "odd-and", "nine-grid", "de-de", "make-impl",
         "access-specifier"],
    )

    phrase_case = (
        "下一节会讲棋盘存储。\n"
        "棋盘多大是规则，代码把它写成常量 kRows。\n"
        ".at() 保留作第二道越界防线。\n"
        "规则描述里的「下一节／上一节」只是术语引用。\n"
        "`下一节` 与「代码把它写成」包在引号里同样豁免。\n"
    )
    got = [
        key for _, key, _ in module.scan_text(Path("x.qmd"), phrase_case, False, True)
    ]
    expect("正文句式禁令命中三条", got, ["next-section", "code-wrote-it", "defense-line"])

    agent_case = "下一节讲存储。\n不写「下一节」预告。\n"
    got = [
        key
        for _, key, _ in module.scan_text(Path("x.md"), agent_case, False, False, True)
    ]
    expect("agent 文档命中一条、引号豁免一条", got, ["next-section"])

    disclaimer_case = (
        "本章摘录源码服务于讲解，片段不保证与源文件逐字一致。\n"
        "免责声明「服务于讲解」只在 .agents 里出现。\n"
    )
    got = [
        key
        for _, key, _ in module.scan_text(Path("x.qmd"), disclaimer_case, False, True)
    ]
    expect("agent 免责腔每行报一次、引号豁免一条", got, ["agent-disclaimer"])

    passive_case = (
        "配置由 CMake 完成。\n"
        "换算由 `ToFlatIndex` 完成。\n"
        "豁免写法「由 CMake 完成」包在引号里。\n"
    )
    got = [
        key for _, key, _ in module.scan_text(Path("x.qmd"), passive_case, False, True)
    ]
    expect("由…完成在 qmd 命中两条、引号豁免一条", got, ["passive-done", "passive-done"])
    got = [
        key for _, key, _ in module.scan_text(Path("README.md"), passive_case, False, True)
    ]
    expect("由…完成不扫 README（非 qmd）", got, [])

    zipper_case = (
        "先把两类信息分开，分别交给 `CellPosition` 和 `CellState`。\n"
        "落子结果和对局结果各说一层。\n"
        "豁免写法「分别交给」包在引号里。\n"
        "可执行文件和动态库文件分别在 build/ 的哪一层？\n"
    )
    got = [
        key for _, key, _ in module.scan_text(Path("x.qmd"), zipper_case, False, True)
    ]
    expect("拉链句高频词命中两条、引号豁免一条、宽泛的「分别」不拦", got, ["zipper-pairing", "zipper-pairing"])
    got = [
        key
        for _, key, _ in module.scan_text(Path("x.md"), zipper_case, False, False, True)
    ]
    expect("拉链句高频词不扫 agent 文档（案例引用反例）", got, [])

    scopes = [
        (".agents/knowledge/quarto-writing/x.md", (False, False, True)),
        ("content/tictactoe/03-board.qmd", (False, True, False)),
        ("README.md", (False, True, False)),
        ("index.qmd", (False, True, False)),
        ("games/tictactoe/01-cli-game/tictactoe/include/board.h", (True, False, False)),
        (
            ".agents/skills/governing-agents/scripts/check_docs.py",
            (True, False, False),
        ),
    ]
    for relative, want in scopes:
        expect(f"作用域 {relative}", module.rules_for(module.ROOT / relative), want)

    if failures:
        for line in failures:
            print(f"失败  {line}")
        raise SystemExit(1)
    print("OK: 中文体检自测全部通过")


if __name__ == "__main__":
    main()
