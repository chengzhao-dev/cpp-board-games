#!/usr/bin/env python3
"""coords_grid.py - 坐标轴网格图的共享 SVG 绘图助手。

Quarto 章节里的 ``{python}`` 可执行单元调用本助手生成坐标轴网格图
（棋盘行列、二维数组下标等），绘图逻辑只存在于本文件；正文单元应
只含调用，不内联第二套 SVG 逻辑（口径见标识 bg-coords-diagram-v1
的知识文件）。只用标准库拼 SVG；描边与文字用 currentColor，跟随
页面明暗主题，不写死颜色。
"""

#===------------------------------------------------------------------------===#
# 常量
#===------------------------------------------------------------------------===#

FONT_FAMILY = "Fixel Text, LXGW WenKai Screen, system-ui, sans-serif"


#===------------------------------------------------------------------------===#
# 绘图
#===------------------------------------------------------------------------===#

def render_grid(rows=3, cols=3, labels="coords", origin="top-left",
                cell=64, label_gap=30, font_size=14, marks=None,
                highlight=None, axis=True):
    """渲染一张程序坐标系网格图，返回 SVG 字符串。

    rows/cols：网格行数与列数；labels："coords" 时格子内标注 (r,c)，
    "empty" 时只画格线；origin 目前只支持 "top-left"（row 0 在上、
    col 0 在左）。axis 为 True 时画两条带箭头的轴：横轴 `col` 从
    原点向右增长，纵轴 `row` 向下增长，轴与网格之间的数字是各列/
    各行的下标；左上格外角画一个原点记号，箭头方向与原点位置直观
    呈现「row 向下增长、原点在左上角」这两处程序事实。轴名与代码
    字段 `Position::row` / `Position::col` 及 `kRows` / `kCols` 对应。
    marks：{(r,c): 文本}，在对应格子居中放大绘制棋子等标记，
    覆盖该格的坐标标注；highlight：(r,c)，为该格加一圈加粗描边，
    表达落子目标框。
    """
    if origin != "top-left":
        raise ValueError(f"不支持的 origin: {origin!r}")
    if rows < 1 or cols < 1:
        raise ValueError("rows 与 cols 至少为 1")
    if labels not in ("coords", "empty"):
        raise ValueError(f"不支持的 labels: {labels!r}")
    marks = dict(marks or {})
    for r, c in marks:
        if not (0 <= r < rows and 0 <= c < cols):
            raise ValueError(f"marks 越界: {(r, c)!r}")
    if highlight is not None:
        hr, hc = highlight
        if not (0 <= hr < rows and 0 <= hc < cols):
            raise ValueError(f"highlight 越界: {highlight!r}")

    # 轴几何：axis 开启时画带箭头的两条轴，轴名压在轴线上方/左方。
    axis_top = 18 if axis else 0
    axis_left = 18 if axis else 0
    arrow_pad = 18  # 箭头伸出网格外的留白
    grid_left = axis_left + label_gap
    grid_top = axis_top + label_gap
    grid_right = grid_left + cols * cell
    grid_bottom = grid_top + rows * cell
    width = grid_right + arrow_pad
    height = grid_bottom + arrow_pad
    parts = [
        f'<svg class="coords-grid" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="{FONT_FAMILY}" font-size="{font_size}">',
        '<style>.coords-grid{color:#1F2328}'
        '@media (prefers-color-scheme: dark){.coords-grid{color:#CDD9E5}}</style>',
        '<g stroke="currentColor" fill="none" stroke-width="1.25">',
    ]

    if axis:
        # 横轴：从原点侧向右延伸，箭头指右，表达 col 向右增长。
        parts.append(
            f'<line x1="{axis_left}" y1="{axis_top}" '
            f'x2="{grid_right + 10}" y2="{axis_top}"/>'
        )
        parts.append(
            f'<polygon points="{grid_right + 10},{axis_top - 4} '
            f'{grid_right + 18},{axis_top} '
            f'{grid_right + 10},{axis_top + 4}" '
            f'fill="currentColor" stroke="none"/>'
        )
        parts.append(
            f'<text x="{grid_left + cols * cell / 2}" y="{axis_top - 6}" '
            f'text-anchor="middle" '
            f'fill="currentColor" stroke="none">col</text>'
        )
        # 纵轴：从原点侧向下延伸，箭头指下，表达 row 向下增长。
        parts.append(
            f'<line x1="{axis_left}" y1="{axis_top}" '
            f'x2="{axis_left}" y2="{grid_bottom + 10}"/>'
        )
        parts.append(
            f'<polygon points="{axis_left - 4},{grid_bottom + 10} '
            f'{axis_left},{grid_bottom + 18} '
            f'{axis_left + 4},{grid_bottom + 10}" '
            f'fill="currentColor" stroke="none"/>'
        )
        center_y = axis_top + label_gap + rows * cell / 2
        parts.append(
            f'<text x="10" y="{center_y}" '
            f'transform="rotate(-90 10 {center_y})" text-anchor="middle" '
            f'fill="currentColor" stroke="none">row</text>'
        )

    for c in range(cols):
        x = grid_left + c * cell
        parts.append(
            f'<text x="{x + cell / 2}" y="{grid_top - 10}" '
            f'text-anchor="middle" fill="currentColor" stroke="none">{c}</text>'
        )
    for r in range(rows):
        y = grid_top + r * cell
        parts.append(
            f'<text x="{grid_left - 10}" y="{y + cell / 2}" '
            f'text-anchor="end" dominant-baseline="middle" '
            f'fill="currentColor" stroke="none">{r}</text>'
        )

    for r in range(rows):
        for c in range(cols):
            x = grid_left + c * cell
            y = grid_top + r * cell
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}"/>'
            )
            if labels == "coords" and (r, c) not in marks:
                parts.append(
                    f'<text x="{x + cell / 2}" y="{y + cell / 2}" '
                    f'text-anchor="middle" dominant-baseline="middle" '
                    f'fill="currentColor" stroke="none">({r},{c})</text>'
                )

    parts.append("</g>")

    # 标记、高亮与原点记号画在格线组外：棋子是内容不是格线，加粗描边
    # 与实心原点需要独立线宽和填充。
    if axis:
        parts.append(
            f'<circle cx="{grid_left}" cy="{grid_top}" r="3" '
            f'fill="currentColor"/>'
        )
    for (r, c), text in marks.items():
        x = grid_left + c * cell + cell / 2
        y = grid_top + r * cell + cell / 2
        parts.append(
            f'<text x="{x}" y="{y}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="{font_size * 2}" '
            f'fill="currentColor">{text}</text>'
        )
    if highlight is not None:
        hr, hc = highlight
        x = axis_left + label_gap + hc * cell
        y = axis_top + label_gap + hr * cell
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'fill="none" stroke="currentColor" stroke-width="3"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def render_index_strip(count, cols=3, highlight=None, cell=56, font_size=14):
    """渲染一维下标与行列坐标的对应条带图，返回 SVG 字符串。

    count：数组长度；cols：每 cols 个下标分成一组，对应 kCols。
    每组上方标 row = N 并画一条组线，格内标一维下标，格下标换算
    前的 (row, col)；highlight 指定加粗的下标，用于标出公式示例
    （如 (1, 2) 换算出的 5）。越界参数直接抛 ValueError。
    """
    if count < 1:
        raise ValueError("count 至少为 1")
    if cols < 1:
        raise ValueError("cols 至少为 1")
    if highlight is not None and not 0 <= highlight < count:
        raise ValueError(f"highlight 越界: {highlight!r}")

    # 几何：每组上方留 row = N 标注行，格下留 (row, col) 标注行；
    # 组内格间距小、组间距大，隔开各行占用的下标段。
    gap_in = 8
    gap_group = 30
    label_h = 24
    below_h = 24
    pad = 6
    groups = (count + cols - 1) // cols
    width = (pad * 2 + count * cell
             + (count - groups) * gap_in + (groups - 1) * gap_group)
    height = pad * 2 + label_h + cell + below_h
    parts = [
        f'<svg class="coords-grid" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="{FONT_FAMILY}" font-size="{font_size}">',
        '<style>.coords-grid{color:#1F2328}'
        '@media (prefers-color-scheme: dark){.coords-grid{color:#CDD9E5}}</style>',
        '<g stroke="currentColor" fill="none" stroke-width="1.25">',
    ]

    def group_left(row):
        """返回第 row 组第一个格子的左边缘 x 坐标。"""
        x = pad
        for r in range(row):
            n_prev = min(cols, count - r * cols)
            x += n_prev * cell + (n_prev - 1) * gap_in + gap_group
        return x

    for row in range(groups):
        n_in_group = min(cols, count - row * cols)
        left = group_left(row)
        right = left + (n_in_group - 1) * (cell + gap_in) + cell
        center = (left + right) / 2
        parts.append(
            f'<text x="{center}" y="{pad + 13}" text-anchor="middle" '
            f'fill="currentColor" stroke="none">row = {row}</text>'
        )
        parts.append(
            f'<line x1="{left}" y1="{pad + label_h - 5}" '
            f'x2="{right}" y2="{pad + label_h - 5}"/>'
        )

    for index in range(count):
        row, col = divmod(index, cols)
        x = group_left(row) + col * (cell + gap_in)
        y = pad + label_h
        parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}"/>')
        parts.append(
            f'<text x="{x + cell / 2}" y="{y + cell / 2}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'font-size="{font_size + 2}" '
            f'fill="currentColor" stroke="none">{index}</text>'
        )
        parts.append(
            f'<text x="{x + cell / 2}" y="{y + cell + 16}" '
            f'text-anchor="middle" font-size="{font_size - 2}" '
            f'fill="currentColor" stroke="none">({row},{col})</text>'
        )

    parts.append("</g>")

    if highlight is not None:
        row, col = divmod(highlight, cols)
        x = group_left(row) + col * (cell + gap_in)
        y = pad + label_h
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'fill="none" stroke="currentColor" stroke-width="3"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts)
