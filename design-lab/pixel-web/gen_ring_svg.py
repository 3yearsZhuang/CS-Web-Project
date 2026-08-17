#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成像素莫比乌斯环 SVG — 与 canvas-01 同源数学，供网页 Hero 使用。
输出：pixel-ring.svg（viewBox 0 0 600 600，cell=10 → 60 格）
"""
import math

CELL = 10
VIEW = 600
COLS = VIEW // CELL

R = 19 * CELL      # 主半径 19 格
HW = 4.2 * CELL    # 半宽 4.2 格
rot = 0.42
cx0, cy0 = VIEW / 2, VIEW / 2

surface = set()
edge = set()
meridian = set()

T_N, U_N = 420, 28
for i in range(T_N):
    t = 2 * math.pi * i / T_N
    for j in range(U_N):
        u = -HW + 2 * HW * j / (U_N - 1)
        x = (R + u * math.cos(t / 2)) * math.cos(t)
        y = (R + u * math.cos(t / 2)) * math.sin(t)
        z = u * math.sin(t / 2)
        yp = y * math.cos(rot) - z * math.sin(rot)
        zp = y * math.sin(rot) + z * math.cos(rot)
        gx = int((cx0 + x) / CELL)
        gy = int((cy0 + yp) / CELL)
        if 0 <= gx < COLS and 0 <= gy < COLS:
            surface.add((gx, gy))
            if j in (0, U_N - 1):
                edge.add((gx, gy))
            if i % 35 == 0:
                meridian.add((gx, gy))

rects = {
    "surface": [], "meridian": [], "edge": [],
}
for (gx, gy) in surface:
    if (gx, gy) in edge or (gx, gy) in meridian:
        continue
    rects["surface"].append((gx, gy))
for (gx, gy) in meridian:
    if (gx, gy) in edge:
        continue
    rects["meridian"].append((gx, gy))
for (gx, gy) in edge:
    rects["edge"].append((gx, gy))

def block(gx, gy, fill, opacity=None):
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return f'<rect x="{gx*CELL}" y="{gy*CELL}" width="{CELL}" height="{CELL}" fill="{fill}"{o}/>'

parts = []
# 表面（沉睡的大多数）
for gx, gy in rects["surface"]:
    parts.append(block(gx, gy, "#d4a574", 0.24))
# 经线（带子结构）
for gx, gy in rects["meridian"]:
    parts.append(block(gx, gy, "#d4a574", 0.38))
# 边缘（环的轮廓 — 全亮琥珀）
for gx, gy in rects["edge"]:
    parts.append(block(gx, gy, "#d4a574", 1.0))

# 举手的成员像素（粉色/浅蓝/奶油）
members = [
    (8, 20, "#f0b0c0"), (47, 14, "#a0d0f0"), (12, 44, "#f7ead8"),
    (50, 46, "#f0b0c0"), (6, 30, "#a0d0f0"), (53, 28, "#f7ead8"),
    (30, 6, "#f0b0c0"), (30, 53, "#a0d0f0"), (20, 10, "#f7ead8"),
]
for gx, gy, c in members:
    parts.append(block(gx, gy, c))

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}" '
    f'width="100%" height="100%">\n'
    + "\n".join(parts)
    + "\n</svg>\n"
)

out = "/Users/3yearszhuang/Documents/FztbuCS-Project/design-lab/pixel-web/pixel-ring.svg"
import os
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    f.write(svg)
print("saved", out, "| rects:", len(parts))
