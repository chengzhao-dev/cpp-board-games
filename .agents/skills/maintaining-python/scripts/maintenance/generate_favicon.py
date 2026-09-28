#!/usr/bin/env python3
"""生成站点图标 favicon.svg（纯标准库，无第三方依赖）。

图标形状参数集中在本文件顶部，`svg_text()` 据此序列化 SVG。同一套参数也能
光栅化（`render()`），供 `--preview` 出小尺寸放大图，人工核对 16/32px 是否糊。

设计参考 GitHub / Cursor 等主流站点 favicon 的共性：强对比单色剪影、边缘留白、
16px 仍可辨的实心字形（少用细描边）、圆角容器、明暗自适应。

用法：
    python .agents/skills/maintaining-python/scripts/maintenance/generate_favicon.py              # 写 .agents/skills/designing-theme/assets/theme/assets/favicon.svg
    python .agents/skills/maintaining-python/scripts/maintenance/generate_favicon.py --preview d  # 另存 16/32/256 预览 PNG 到目录 d

说明：_quarto.yml 的 book.favicon 只接受单个文件，现代浏览器（含 Safari 15+）
支持 SVG favicon，故不附带 ICO——避免发布无人引用的产物。
"""

import argparse
import math
import struct
import zlib
from pathlib import Path

# GitHub Primer 级对比：亮色标签页用深底白字，暗色反过来，「++」用站点绿点强调色
LIGHT_BG = (0x0D, 0x11, 0x17)
LIGHT_FG = (0xFF, 0xFF, 0xFF)
LIGHT_ACCENT = (0x3F, 0xB9, 0x50)  # 对齐 --dot-accent 暗色
DARK_BG = (0xF0, 0xF6, 0xFC)
DARK_FG = (0x0D, 0x11, 0x17)
DARK_ACCENT = (0x1F, 0x88, 0x3D)  # 对齐 --dot-accent 亮色
VB = 64.0
CORNER_R = 15.0  # 保留清晰轮廓，同时接近 Quarto 的简洁品牌标
PAD = 4.0  # 字形相对画布的安全边距

# 「C」：实心圆环缺口，圆心偏左，给右侧两个「+」留足间隙
C_CX, C_CY = 20.0, 32.0
C_ROUT, C_RIN = 13.0, 5.75
C_OPEN = 48.0  # 开口半角（度）

# 两个「+」：实心十字，中心距须足够，避免 16px 下糊成一条
PLUS_CY = 32.0
PLUS_ARM = 4.5
PLUS_T = 4.25
PLUS_CX = (38.5, 52.5)


def _in_bg(x, y):
    """背景圆角矩形命中判定。"""
    r = CORNER_R
    if r <= x <= VB - r or r <= y <= VB - r:
        return 0 <= x <= VB and 0 <= y <= VB
    cx = r if x < r else VB - r
    cy = r if y < r else VB - r
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def _coverage_dist(d, half):
    """距中心线 half 内为实，边缘 0.5 单位抗锯齿。"""
    if d <= half - 0.5:
        return 1.0
    if d >= half + 0.5:
        return 0.0
    return half + 0.5 - d


def _coverage_c(x, y):
    """实心 C：圆环带扣掉右侧开口扇区，开口边界做软过渡。"""
    dx, dy = x - C_CX, y - C_CY
    dist = math.hypot(dx, dy)
    ang = (math.degrees(math.atan2(dy, dx)) + 180.0) % 360.0 - 180.0
    r_mid = 0.5 * (C_ROUT + C_RIN)
    half = 0.5 * (C_ROUT - C_RIN)
    ring = _coverage_dist(abs(dist - r_mid), half)
    soft = 2.0
    aa = abs(ang)
    if aa <= C_OPEN - soft:
        return 0.0
    if aa >= C_OPEN + soft:
        return ring
    return ring * ((aa - (C_OPEN - soft)) / (2.0 * soft))


def _dist_to_seg(x, y, ax, ay, bx, by):
    """到线段距离。"""
    px, py = x - ax, y - ay
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, (px * vx + py * vy) / L2))
    return math.hypot(px - t * vx, py - t * vy)


def _coverage_plus(x, y, cx):
    """实心圆角十字：横臂 ∪ 竖臂。"""
    h = _dist_to_seg(x, y, cx - PLUS_ARM, PLUS_CY, cx + PLUS_ARM, PLUS_CY)
    v = _dist_to_seg(x, y, cx, PLUS_CY - PLUS_ARM, cx, PLUS_CY + PLUS_ARM)
    return max(_coverage_dist(h, PLUS_T / 2.0), _coverage_dist(v, PLUS_T / 2.0))


def sample(x, y):
    """viewBox 坐标 -> (r, g, b, a)：亮色方案下的 C++ 图标合成。"""
    if not _in_bg(x, y):
        return 0, 0, 0, 0
    if x < PAD or y < PAD or x > VB - PAD or y > VB - PAD:
        return (*LIGHT_BG, 255)
    c_a = min(1.0, max(0.0, _coverage_c(x, y)))
    p_a = 0.0
    for cx in PLUS_CX:
        p_a = max(p_a, min(1.0, max(0.0, _coverage_plus(x, y, cx))))
    # 先铺底，再叠 C（白），再叠 ++（绿）。重叠处绿优先于白
    r, g, b = LIGHT_BG
    if c_a > 0:
        r = round(r * (1 - c_a) + LIGHT_FG[0] * c_a)
        g = round(g * (1 - c_a) + LIGHT_FG[1] * c_a)
        b = round(b * (1 - c_a) + LIGHT_FG[2] * c_a)
    if p_a > 0:
        r = round(r * (1 - p_a) + LIGHT_ACCENT[0] * p_a)
        g = round(g * (1 - p_a) + LIGHT_ACCENT[1] * p_a)
        b = round(b * (1 - p_a) + LIGHT_ACCENT[2] * p_a)
    return r, g, b, 255


def render(size, ss=4):
    """光栅化 size×size（每边 ss 倍超采样），返回 RGBA 字节串。"""
    scale = VB / size
    px = bytearray(size * size * 4)
    for py_ in range(size):
        for pxx in range(size):
            acc = [0.0, 0.0, 0.0, 0.0]
            for sy in range(ss):
                for sx in range(ss):
                    vx = (pxx + (sx + 0.5) / ss) * scale
                    vy = (py_ + (sy + 0.5) / ss) * scale
                    r, g, b, a = sample(vx, vy)
                    acc[0] += r * a
                    acc[1] += g * a
                    acc[2] += b * a
                    acc[3] += a
            i = (py_ * size + pxx) * 4
            if acc[3] == 0:
                continue
            a = acc[3]
            px[i : i + 4] = bytes(
                (
                    round(acc[0] / a),
                    round(acc[1] / a),
                    round(acc[2] / a),
                    round(a / (ss * ss)),
                )
            )
    return bytes(px)


def png_bytes(size, data):
    """RGBA 字节串 -> PNG。"""

    def chunk(typ, payload):
        return (
            struct.pack(">I", len(payload))
            + typ
            + payload
            + struct.pack(">I", zlib.crc32(typ + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    stride = size * 4
    raw = b"".join(b"\x00" + data[y * stride : (y + 1) * stride] for y in range(size))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def upscale(size, data, factor):
    """最近邻放大，便于肉眼检查小尺寸清晰度。"""
    w = size * factor
    big = bytearray(w * w * 4)
    for y in range(size):
        for x in range(size):
            src = (y * size + x) * 4
            for dy in range(factor):
                row = ((y * factor + dy) * w + x * factor) * 4
                for dx in range(factor):
                    big[row + dx * 4 : row + dx * 4 + 4] = data[src : src + 4]
    return w, bytes(big)


def _c_path():
    """实心 C：外弧与内弧组成的 evenodd 路径。"""
    open_rad = math.radians(C_OPEN)
    # 外弧端点（开口上下）
    ox0 = C_CX + C_ROUT * math.cos(open_rad)
    oy0 = C_CY + C_ROUT * math.sin(open_rad)
    ox1 = C_CX + C_ROUT * math.cos(-open_rad)
    oy1 = C_CY + C_ROUT * math.sin(-open_rad)
    ix0 = C_CX + C_RIN * math.cos(open_rad)
    iy0 = C_CY + C_RIN * math.sin(open_rad)
    ix1 = C_CX + C_RIN * math.cos(-open_rad)
    iy1 = C_CY + C_RIN * math.sin(-open_rad)
    # 大弧扫过开口以外的部分（sweep=1 逆时针从下端到上端，绕过左侧）
    return (
        f"M{ox0:.2f} {oy0:.2f}"
        f" A{C_ROUT:g} {C_ROUT:g} 0 1 1 {ox1:.2f} {oy1:.2f}"
        f" L{ix1:.2f} {iy1:.2f}"
        f" A{C_RIN:g} {C_RIN:g} 0 1 0 {ix0:.2f} {iy0:.2f}"
        f" Z"
    )


def _plus_rects(cx):
    """实心圆角十字：横竖两条圆角矩形（避免 stroke 圆帽在间隙处粘连）。"""
    t = PLUS_T
    half_t = t / 2.0
    rx = half_t
    h = (
        f'<rect x="{cx - PLUS_ARM:g}" y="{PLUS_CY - half_t:g}" '
        f'width="{2 * PLUS_ARM:g}" height="{t:g}" rx="{rx:g}" fill="var(--accent)"/>'
    )
    v = (
        f'<rect x="{cx - half_t:g}" y="{PLUS_CY - PLUS_ARM:g}" '
        f'width="{t:g}" height="{2 * PLUS_ARM:g}" rx="{rx:g}" fill="var(--accent)"/>'
    )
    return h, v


def svg_text():
    """按形状参数序列化 SVG（与 render() 同一套几何意图）。"""
    bg = f"#{LIGHT_BG[0]:02X}{LIGHT_BG[1]:02X}{LIGHT_BG[2]:02X}"
    fg = f"#{LIGHT_FG[0]:02X}{LIGHT_FG[1]:02X}{LIGHT_FG[2]:02X}"
    ac = f"#{LIGHT_ACCENT[0]:02X}{LIGHT_ACCENT[1]:02X}{LIGHT_ACCENT[2]:02X}"
    dbg = f"#{DARK_BG[0]:02X}{DARK_BG[1]:02X}{DARK_BG[2]:02X}"
    dfg = f"#{DARK_FG[0]:02X}{DARK_FG[1]:02X}{DARK_FG[2]:02X}"
    dac = f"#{DARK_ACCENT[0]:02X}{DARK_ACCENT[1]:02X}{DARK_ACCENT[2]:02X}"
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"'
        ' role="img" aria-label="C++">',
        f'  <style>:root {{ --bg: {bg}; --fg: {fg}; --accent: {ac}; }}'
        f' @media (prefers-color-scheme: dark) {{'
        f' :root {{ --bg: {dbg}; --fg: {dfg}; --accent: {dac}; }} }}</style>',
        f'  <rect width="64" height="64" rx="{CORNER_R:g}" fill="var(--bg)"/>',
        f'  <path fill="var(--fg)" fill-rule="evenodd" d="{_c_path()}"/>',
    ]
    for cx in PLUS_CX:
        h, v = _plus_rects(cx)
        lines.append(f"  {h}")
        lines.append(f"  {v}")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preview",
        metavar="DIR",
        help="额外输出 16/32/256 预览 PNG（16、32 做 10x 最近邻放大）到 DIR",
    )
    args = parser.parse_args()

    out = Path(".agents/skills/designing-theme/assets/theme/assets")
    out.mkdir(parents=True, exist_ok=True)
    target = out / "favicon.svg"
    target.write_text(svg_text(), encoding="utf-8", newline="\n")
    print(f"已生成 {target} ({target.stat().st_size} bytes)")

    if args.preview:
        prev = Path(args.preview)
        prev.mkdir(parents=True, exist_ok=True)
        for size in (16, 32):
            w, big = upscale(size, render(size), 10)
            (prev / f"favicon-{size}px@10x.png").write_bytes(png_bytes(w, big))
        (prev / "favicon-256.png").write_bytes(png_bytes(256, render(256)))
        print(f"预览已输出到 {prev}")


if __name__ == "__main__":
    main()
