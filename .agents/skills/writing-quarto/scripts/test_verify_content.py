# test_verify_content.py - verify_content.py 任务级标题、token 区间、禁用词门禁
# 与句子模块切分的回归自测
#
# 用临时 qmd 样例核对：任务级 `##` 超过 4 个失败、二三级 token 区间
# （单一任务节 200–1200、多任务节每节 400–1200、任务级 ### 120–480、
# 症状 ### 60–240）、孤立三级标题、固定收尾节不计入任务数、着陆页与
# 代码围栏内的伪标题不触发限制、C++ 访问说明符禁用词被扫描命中、
# 句子模块三类失败（类型接线、改口、全称被下一句否定）与豁免
# （单次「使用」、自测导语、「两个字段」「第一个格子」）。
# 由 run.py 的 fast profile 调用；规则正文见标识 bg-chapter-structure-v1、
# bg-cpp-chinese-terms-v1 与 bg-paragraph-craft-v1 的知识文件。

import importlib.util
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "verify_content.py"

# 夹具用填充段：单段约 160 token、3 句，落在 70–220 的正文段落区间内，
# 不含禁用词，也不含行内代码（避免牵动其他启发式检查）。
FILLER = (
    "棋盘格子按行列编号，程序在每一轮先读取当前状态，再根据输入决定下一步的动作。"
    "测试核对同一规则在不同入口上的表现，输出保持一致，验收因此可以重复进行。"
    "约定写进构建规则之后，检查工具逐条核对源码，报告与预期不符的位置。"
)
# 节开头的引导句加列表：闭合节导语，使其不吞掉后续填充段。
LEAD = "要点如下：\n\n- 项一\n- 项二\n\n"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_content", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def filler(n: int) -> str:
    return "\n\n".join([FILLER] * n)


def write_sample(directory: Path, name: str, frontmatter: str, headings,
                 filler_count: int = 3) -> Path:
    """每个标题下写引导列表加 filler_count 个填充段，满足任务级下限。"""
    parts = [frontmatter] if frontmatter else []
    for heading in headings:
        parts.append(f"{heading}\n\n{LEAD}{filler(filler_count)}")
    path = directory / name
    path.write_text("\n\n".join(parts) + "\n", encoding="utf-8", newline="\n")
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

        # 单一任务节下限 200：只有一节时按 200 判。
        single_low = temp_path / "single-low.qmd"
        single_low.write_text("## 任务\n\n" + LEAD, encoding="utf-8", newline="\n")
        errors = module.check_file_budget(single_low)
        if len(errors) != 1 or "低于下限 200" not in errors[0]:
            failures.append(f"单一任务节低于 200 应报下限错误：{errors}")

        # 多任务节下限 400：两节中一节不足 400 时报下限错误。
        multi_low = temp_path / "multi-low.qmd"
        multi_low.write_text(
            "## 任务一\n\n" + LEAD + filler(1)
            + "\n\n## 任务二\n\n" + LEAD + filler(3) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(multi_low)
        if len(errors) != 1 or "低于下限 400" not in errors[0]:
            failures.append(f"多任务节中不足 400 应报下限错误：{errors}")

        # 任务级 ### 区间 120–480：不足 120 报下限，超过 480 报上限。
        h3_low = temp_path / "h3-low.qmd"
        h3_low.write_text(
            "## 任务\n\n" + LEAD + "### 小节一\n\n正文。\n\n### 小节二\n\n"
            + LEAD + filler(2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(h3_low)
        if len(errors) != 1 or "「小节一」" not in errors[0] or "低于下限 120" not in errors[0]:
            failures.append(f"任务级 ### 低于 120 应报下限错误：{errors}")

        h3_high = temp_path / "h3-high.qmd"
        h3_high.write_text(
            "## 任务\n\n" + LEAD + "### 小节一\n\n" + LEAD + filler(4)
            + "\n\n### 小节二\n\n" + LEAD + filler(1) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(h3_high)
        if len(errors) != 1 or "超过 480" not in errors[0]:
            failures.append(f"任务级 ### 超过 480 应报上限错误：{errors}")

        # 症状 ### 区间 60–240：不足 60 报下限，不套任务级 120 的下限。
        symptom = temp_path / "symptom-low.qmd"
        symptom.write_text(
            "## 常见错误\n\n### 症状\n\n正文。\n\n## 本章回顾\n\n回顾。\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(symptom)
        if len(errors) != 1 or "「症状」" not in errors[0] or "低于下限 60" not in errors[0]:
            failures.append(f"症状 ### 低于 60 应报下限错误：{errors}")

        # 孤立三级标题：任务级 ## 下只有一个 ### 时报错。
        lonely = temp_path / "lonely-h3.qmd"
        lonely.write_text(
            "## 任务\n\n" + LEAD + "### 小节\n\n" + LEAD + filler(2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(lonely)
        if len(errors) != 1 or "孤立三级标题" not in errors[0]:
            failures.append(f"只有一个三级标题应报孤立错误：{errors}")

        fence = temp_path / "fence.qmd"
        fence.write_text(
            "## 任务一\n\n" + LEAD + "```bash\n## 这不是标题\n```\n\n"
            "围栏之后的收束段落写得更长一些，确保它不会触发段落下限检查；"
            "本条用例只核对围栏内的伪标题不会被当作结构标题计入预算与标题数。\n\n"
            + filler(2) + "\n\n## 任务二\n\n" + LEAD + filler(3) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(fence)
        if errors:
            failures.append(f"围栏内伪标题不应计入：{errors}")

        # 段落下限 70 token：豁免口径（规则见标识 bg-chapter-structure-v1
        # 的知识文件「分层上限」）与失败口径。
        short = temp_path / "short-para.qmd"
        short.write_text(
            "## 任务\n\n```bash\n./build.sh\n```\n\n" + filler(2) + "\n\n"
            "构建先于运行。构建产出目标文件。运行读取这些目标文件。\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(short)
        if len(errors) != 1 or "低于下限" not in errors[0]:
            failures.append(f"多句短段落应报低于下限：{errors}")

        lead_block = temp_path / "lead-block.qmd"
        lead_block.write_text(
            "## 任务\n\n构建命令如下：\n\n```bash\n./build.sh\n```\n\n" + filler(2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(lead_block)
        if errors:
            failures.append(f"紧邻代码块的单句导语应豁免下限：{errors}")

        callout_short = temp_path / "callout-short.qmd"
        callout_short.write_text(
            "## 任务\n\n::: {.callout-note}\n这是盒子里的短提示。\n:::\n\n" + filler(2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(callout_short)
        if errors:
            failures.append(f"Callout 盒子内短段应豁免下限：{errors}")

        # 链接折叠口径：任何链接只计锚文本，不计目标。
        if module.strip_link_urls("[board.h](03-board.qmd)") != "board.h":
            failures.append("相对链接应折叠为锚文本")
        if module.strip_link_urls("[锚](https://github.com/a/b)") != "锚":
            failures.append("绝对链接应折叠为锚文本")
        if module.strip_link_urls("[锚][ref]") != "锚":
            failures.append("引用式链接应折叠为锚文本")
        if module.strip_link_urls("见 <https://example.com/a>") != "见 ":
            failures.append("自动链接应计 0")
        if module.strip_link_urls("见 https://example.com/a") != "见 ":
            failures.append("裸 URL 应计 0")

        landing = write_sample(
            temp_path,
            "index.qmd",
            "---\ntitle: 着陆页\nbody-classes: index-page\n---\n",
            [f"## 卡片{i}" for i in range(1, 7)],
        )
        errors = module.check_file_budget(landing)
        if errors:
            failures.append(f"着陆页不应触发任务级标题限制：{errors}")

        banned = temp_path / "banned.qmd"
        banned.write_text(
            "## 任务\n\n公开段只留下入口，存储收在私有段。\n",
            encoding="utf-8",
            newline="\n",
        )
        findings = module.scan_qmd_forbidden([banned])
        terms = {term for _, _, term in findings}
        if not {"公开段", "私有段"} <= terms:
            failures.append(f"禁用词「公开段/私有段」应被 scan_qmd_forbidden 命中：{findings}")

        twin = temp_path / "twin-intro.qmd"
        twin.write_text(
            "承接上一章的结果。\n\n本章交出可以检查坐标的棋盘读写。\n\n## 任务一\n\n"
            + LEAD + filler(2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(twin)
        if len(errors) != 1 or "章引言" not in errors[0]:
            failures.append(f"两个散文段引言应报章引言形态错误：{errors}")

        single = temp_path / "single-intro.qmd"
        single.write_text(
            "承接上一章的结果，本章交出棋盘读写。\n\n- 范围一\n- 范围二\n\n## 任务一\n\n"
            + LEAD + filler(2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        errors = module.check_file_budget(single)
        if errors:
            failures.append(f"一段 + 列表引言不应报错：{errors}")

        # 5g 段内同义堆叠（WARN 启发式）
        stack = temp_path / "synonym-stack.qmd"
        stack.write_text(
            "## 任务\n\n"
            "数组长度写成 `kCellCount`，长度在编译期确定下来。"
            "也就是说，这个数量是井字棋规则的一部分。\n",
            encoding="utf-8",
            newline="\n",
        )
        hits = module.find_intra_paragraph_synonym_stack_warnings(stack)
        if len(hits) != 1 or "复述连接词" not in hits[0][2]:
            failures.append(f"复述连接词应命中段内同义堆叠：{hits}")

        echo_pair = temp_path / "synonym-echo.qmd"
        echo_pair.write_text(
            "## 任务\n\n"
            "棋盘一共九个格子，这个数量是井字棋规则的一部分。"
            "这个数量是井字棋规则的一部分，从开局到终局不变。\n",
            encoding="utf-8",
            newline="\n",
        )
        hits = module.find_intra_paragraph_synonym_stack_warnings(echo_pair)
        if not hits or "重叠" not in hits[0][2]:
            failures.append(f"高重叠句对应命中段内同义堆叠：{hits}")

        clean_pair = temp_path / "synonym-clean.qmd"
        clean_pair.write_text(
            "## 任务\n\n"
            "数组长度用编译期常量 `kCellCount`，与固定长度的容器一致。"
            "访问棋盘格子时，还要把行列坐标换算成数组下标。\n",
            encoding="utf-8",
            newline="\n",
        )
        hits = module.find_intra_paragraph_synonym_stack_warnings(clean_pair)
        if hits:
            failures.append(f"递进两句不应命中同义堆叠：{hits}")

        # 5h 散文伪标签冒号（WARN 启发式）
        label = temp_path / "pseudo-label.qmd"
        label.write_text(
            "## 任务\n\n"
            "数组长度写成 `kCellCount`：棋盘格子有多少个，编译期就确定下来。\n",
            encoding="utf-8",
            newline="\n",
        )
        hits = module.find_pseudo_label_colon_warnings(label)
        if len(hits) != 1 or "kCellCount" not in hits[0][2]:
            failures.append(f"词条腔冒号应命中伪标签检查：{hits}")

        intro = temp_path / "colon-intro.qmd"
        intro.write_text(
            "## 任务\n\n约定如下：\n\n- 项一\n- 项二\n",
            encoding="utf-8",
            newline="\n",
        )
        hits = module.find_pseudo_label_colon_warnings(intro)
        if hits:
            failures.append(f"引出列表的冒号不应命中：{hits}")

        literal = temp_path / "colon-literal.qmd"
        literal.write_text(
            "## 任务\n\n终端打印对局结果：X 获胜。\n",
            encoding="utf-8",
            newline="\n",
        )
        hits = module.find_pseudo_label_colon_warnings(literal)
        if hits:
            failures.append(f"协议字面量豁免失效：{hits}")

        # 句子模块切分（规则见 bg-paragraph-craft-v1「一次对话」）：
        # 类型接线句失败。
        wiring = temp_path / "module-wiring.qmd"
        wiring.write_text(
            "## 任务\n\n"
            "`Move` 的位置直接使用上一章的 `CellPosition`，玩家字段使用本节的 `Player`，"
            "一个结构体装下一次落子的全部信息。先手和后手交替落子，一次落子由当时轮到的玩家提交。\n",
            encoding="utf-8",
            newline="\n",
        )
        errors, counts = module.scan_sentence_modules(wiring)
        if len(errors) != 1 or "类型接线" not in errors[0]:
            failures.append(f"两个分句各自「使用+行内代码」应报类型接线：{errors}")
        if counts["段"] != 1 or counts["节"] != 0 or counts["章"] != 0:
            failures.append(f"模块计数应含 1 段且无 ### 节：{counts}")

        # 改口：「接着看」与「第 N 个枚举」失败，跨围栏的散文句各报一次。
        glance = temp_path / "module-glance.qmd"
        glance.write_text(
            "## 任务\n\n"
            "至于落子有没有写进棋盘、整局进行到了哪一步，是两个不同的问题，"
            "`Game` 用两个枚举分开回答。接着看落子可能写入棋盘、也可能被拒绝的处理结果，"
            "用第一个枚举 `PlaceResult` 表示：\n\n"
            "```{.cpp}\nenum class PlaceResult {};\n```\n\n"
            "第二个枚举回答对局整体的走向，用 `GameResult` 表示：\n",
            encoding="utf-8",
            newline="\n",
        )
        errors, _ = module.scan_sentence_modules(glance)
        glance_hits = [e for e in errors if "改口" in e]
        if len(glance_hits) != 2 or not all("枚举" in e or "接着看" in e for e in glance_hits):
            failures.append(f"「接着看」与「第一个/第二个枚举」应各报一次改口：{errors}")

        # 改口扩展：「第 N 个」接成员、入口、步骤、结果同样失败。
        glance2 = temp_path / "module-glance2.qmd"
        glance2.write_text(
            "## 任务\n\n"
            "落子结果与对局走向用两个枚举分开回答。第二个数据成员保存对局结果。"
            "第三个入口负责写入。第三个步骤判定终局。第四个结果记平局。\n",
            encoding="utf-8",
            newline="\n",
        )
        errors, _ = module.scan_sentence_modules(glance2)
        glance2_hits = [e for e in errors if "改口" in e]
        if len(glance2_hits) != 4:
            failures.append(f"「第 N 个」接成员/入口/步骤/结果应各报改口：{errors}")

        # 序数豁免：真实位置的格子、行列与「第 N 次写入」不进改口词表。
        ordinal_ok = temp_path / "module-ordinal-ok.qmd"
        ordinal_ok.write_text(
            "## 任务\n\n"
            "第一个格子从下标 0 开始，第一行的三个下标是 0、1、2，"
            "第二次写入同一个棋盘格子会被拒绝。\n",
            encoding="utf-8",
            newline="\n",
        )
        errors, _ = module.scan_sentence_modules(ordinal_ok)
        if errors:
            failures.append(f"真实位置序数不应报改口：{errors}")

        # 全称被下一句否定。
        universal = temp_path / "module-universal.qmd"
        universal.write_text(
            "## 任务\n\n"
            "一个结构体装下一次落子的全部信息。落子结果和整局结果是不同的两件事。\n",
            encoding="utf-8",
            newline="\n",
        )
        errors, _ = module.scan_sentence_modules(universal)
        if len(errors) != 1 or "全称" not in errors[0]:
            failures.append(f"全称被下一句否定应报错：{errors}")

        # 豁免：单次「使用」、自测导语、03 章「两个字段」与「第一个格子」、
        # 列表项与表格不进句子判定。
        exempt = temp_path / "module-exempt.qmd"
        exempt.write_text(
            "## 任务\n\n"
            "先手使用 `X` 棋子，后手落 `O`。\n"
            "坐标按先行后列写入 `CellPosition` 的两个字段，第一个格子从下标 0 开始。\n\n"
            "| 成员 | 含义 |\n| --- | --- |\n| `position` | 落子的行列坐标 |\n\n"
            "- 快照字段由解析方按名字读取\n\n"
            "## 自测问题\n\n"
            "先不要展开答案，试着自己把回答完整说出来，再展开对照。"
            "说不出来的部分，回到对应小节对照正文。\n"
            "1. 空棋盘开局，轮到 X。没轮到的一方来落子时，棋盘会改变吗？\n",
            encoding="utf-8",
            newline="\n",
        )
        errors, counts = module.scan_sentence_modules(exempt)
        if errors:
            failures.append(f"豁免样例不应报句子模块失败：{errors}")
        if counts["列表项"] != 2 or counts["表元"] != 4 or counts["节"] != 0:
            failures.append(f"列表项、表元与节计数不符：{counts}")

        # 标题命名（规则见 bg-chapter-structure-v1「字数硬限」「形式规则」）：
        # 合规的 2 字名词不报错。
        clean = temp_path / "heading-clean.qmd"
        clean.write_text(
            "---\ntitle: \"完成一次落子\"\n---\n\n"
            "## 终局判定\n\n### 三连\n\n正文。\n",
            encoding="utf-8", newline="\n",
        )
        errors = module.find_heading_errors(clean)
        if errors:
            failures.append(f"合规的 2 字名词标题不应报错：{errors}")

        # 超长任务级三级（超过 6 汉字）失败。
        long_h3 = temp_path / "heading-long-h3.qmd"
        long_h3.write_text(
            "## 任务\n\n### 下标换算与数组位置详解\n\n正文。\n",
            encoding="utf-8", newline="\n",
        )
        errors = module.find_heading_errors(long_h3)
        if len(errors) != 1 or "三级标题" not in errors[0]:
            failures.append(f"超长任务级三级应报字数失败：{errors}")

        # 标题里的「收进」（过程动词）失败。
        filler_head = temp_path / "heading-filler.qmd"
        filler_head.write_text("## 任务\n\n### 收进这一局\n\n正文。\n",
                               encoding="utf-8", newline="\n")
        errors = module.find_heading_errors(filler_head)
        if len(errors) != 1 or "填充词" not in errors[0]:
            failures.append(f"标题过程动词应报填充词失败：{errors}")

        # 页面 title 2-6 汉字：2 字下限通过、1 字失败、超过 6 字失败
        # （对象名标准；旧 4-8 标准下合法的动宾形式现在只卡字数，
        # 形式不单独判，见上面「完成一次落子」合规例）。
        title_min = temp_path / "heading-title-min.qmd"
        title_min.write_text(
            "---\ntitle: \"对局\"\n---\n\n## 任务\n\n正文。\n",
            encoding="utf-8", newline="\n",
        )
        errors = module.find_heading_errors(title_min)
        if errors:
            failures.append(f"2 字 title 不应报错：{errors}")
        title_under = temp_path / "heading-title-under.qmd"
        title_under.write_text(
            "---\ntitle: \"棋\"\n---\n\n## 任务\n\n正文。\n",
            encoding="utf-8", newline="\n",
        )
        errors = module.find_heading_errors(title_under)
        if len(errors) != 1 or "title" not in errors[0]:
            failures.append(f"1 字 title 应报字数失败：{errors}")
        title_over = temp_path / "heading-title-over.qmd"
        title_over.write_text(
            "---\ntitle: \"输出局面快照协议\"\n---\n\n## 任务\n\n正文。\n",
            encoding="utf-8", newline="\n",
        )
        errors = module.find_heading_errors(title_over)
        if len(errors) != 1 or "title" not in errors[0]:
            failures.append(f"7 字以上 title 应报字数失败：{errors}")

        # 症状标题 8 字边界：8 字通过、9 字以上失败。
        symptom_edge = temp_path / "heading-symptom.qmd"
        symptom_edge.write_text(
            "## 常见错误\n\n### 非法输入反复提示\n\n正文。\n",
            encoding="utf-8", newline="\n",
        )
        errors = module.find_heading_errors(symptom_edge)
        if errors:
            failures.append(f"8 字症状标题不应报错：{errors}")
        symptom_over = temp_path / "heading-symptom-over.qmd"
        symptom_over.write_text(
            "## 常见错误\n\n### 非法输入后反复提示同一句\n\n正文。\n",
            encoding="utf-8", newline="\n",
        )
        errors = module.find_heading_errors(symptom_over)
        if len(errors) != 1 or "三级标题" not in errors[0]:
            failures.append(f"超过 8 字的症状标题应报字数失败：{errors}")

        # 编写腔：教作者写注释的句子判失败（规则见 bg-qmd-element-cases-v1）。
        authoring = temp_path / "authoring-voice.qmd"
        authoring.write_text(
            "## 任务\n\n至于按什么顺序排列，属于第二句信息，由正文交代。\n",
            encoding="utf-8", newline="\n",
        )
        errors = module.find_authoring_voice_errors(authoring)
        if len(errors) != 1 or "编写腔" not in errors[0]:
            failures.append(f"编写腔句应报失败：{errors}")

    if failures:
        for line in failures:
            print(f"失败  {line}")
        raise SystemExit(1)
    print("内容规则自测：全部通过")


if __name__ == "__main__":
    main()
