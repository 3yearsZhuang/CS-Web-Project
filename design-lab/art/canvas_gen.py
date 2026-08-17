#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIXEL CONGREGATION — canvas triptych generator
哲学：每一个成员是一个像素；近看是数据，远看是图像。
三张画布：THE RING(莫比乌斯环) / THE DAWN(网格日出) / THE RECURSION(递归像素)
所有元素严格对齐 cell 网格；颜色按哲学限量配给；文字只做坐标与印章。
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

random.seed(20260817)

# ───────────────────────── 画布与网格 ─────────────────────────
W, H = 1800, 2400          # 3:4 海报
CELL = 30                  # 每个像素块 = 30px
COLS, ROWS = W // CELL, H // CELL   # 60 × 80

# 有限色板（哲学：两三色 + 近黑）
INK       = (10, 14, 26)     # 夜之墨蓝 #0a0e1a
INK_LIGHT = (18, 24, 42)
AMBER     = (212, 165, 116)  # #d4a574 琥珀 — 点亮
AMBER_DIM = (64, 52, 40)
PINK      = (240, 176, 192)  # #f0b0c0 粉 — 黎明
PALE_BLUE = (160, 208, 240)  # #a0d0f0 浅蓝
MID_BLUE  = (64, 112, 224)   # #4070e0 中蓝
CREAM     = (247, 234, 216)  # 奶油光
WARM_WHITE= (245, 245, 244)
GRID_LINE = (255, 255, 255, 14)    # 细网格（极淡）
GRID_MAJOR= (255, 255, 255, 26)    # 主网格

# ───────────────────────── 字体 ─────────────────────────
FD = "/Users/3yearszhuang/.workbuddy/skills/canvas-design/canvas-fonts/"
def F(path, size):
    try: return ImageFont.truetype(FD + path, size)
    except Exception: return ImageFont.load_default()

SILK   = lambda s: F("Silkscreen-Regular.ttf", s)
PIX    = lambda s: F("PixelifySans-Medium.ttf", s)
JBM    = lambda s: F("JetBrainsMono-Regular.ttf", s)
JBM_B  = lambda s: F("JetBrainsMono-Bold.ttf", s)

# 中文印章字体：宋体/黑体兜底
def zh_font(size):
    for p in ("/System/Library/Fonts/Songti.ttc",
              "/System/Library/Fonts/STHeiti Medium.ttc",
              "/System/Library/Fonts/Supplemental/Songti.ttc"):
        try: return ImageFont.truetype(p, size)
        except Exception: continue
    return ImageFont.load_default()

# ───────────────────────── 公共工具 ─────────────────────────
def new_canvas():
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img, "RGBA")
    return img, d

def draw_grid(d, major_every=6):
    """全幅细网格 + 主网格（极淡，作为宪法而非牢笼）"""
    for x in range(0, W + 1, CELL):
        is_major = (x // CELL) % major_every == 0
        d.line([(x, 0), (x, H)], fill=GRID_MAJOR if is_major else GRID_LINE, width=1 if not is_major else 2)
    for y in range(0, H + 1, CELL):
        is_major = (y // CELL) % major_every == 0
        d.line([(0, y), (W, y)], fill=GRID_MAJOR if is_major else GRID_LINE, width=1 if not is_major else 2)

def cell(x_c, y_c, color):
    """点亮一个像素块（x_c/y_c 为格坐标）"""
    return [(x_c * CELL, y_c * CELL), (x_c * CELL + CELL, y_c * CELL + CELL)], color

def paint(d, cells, outline=False):
    for rect, color in cells:
        d.rectangle(rect, fill=color, outline=(color if outline else None))

def stamp_corner_ticks(d, pad=14, len_=34, color=AMBER):
    """印刷定位角标 — 让它像被精心裁切过的印刷品"""
    for (x0, y0, dx, dy) in [(pad, pad, 1, 1), (W - pad, pad, -1, 1),
                             (pad, H - pad, 1, -1), (W - pad, H - pad, -1, -1)]:
        d.line([(x0, y0), (x0 + dx * len_, y0)], fill=color, width=3)
        d.line([(x0, y0), (x0, y0 + dy * len_)], fill=color, width=3)

def header_block(d, no, en, zh):
    """左上角标题：像素英文 + 中文小注"""
    d.text((34, 34), f"CANVAS {no} / {en}", font=PIX(26), fill=AMBER)
    d.text((36, 72), zh, font=zh_font(22), fill=(175, 183, 200))

def page_no(d, no):
    d.text((W - 120, 40), f"{no} / 3", font=JBM(20), fill=(110, 118, 132))

def seal(d, x, y, size=40, text="计协", color=(176, 60, 44)):
    """朱红印章 — 中文锚定时间与地点"""
    try:
        d.rounded_rectangle([x, y, x + size, y + size], radius=7, fill=color)
        f = ImageFont.truetype("/System/Library/Fonts/Songti.ttc", int(size * 0.52))
        d.text((x + size / 2, y + size / 2), text, font=f, fill=(253, 248, 239), anchor="mm")
    except Exception:
        d.rectangle([x, y, x + size, y + size], fill=color)

def ruler_left(d, step_cells=6, color=(110, 118, 132)):
    """左侧坐标标尺 — 仪器面板语言"""
    for row in range(0, ROWS, step_cells):
        y = row * CELL
        d.line([(10, y), (26, y)], fill=color, width=2)
        d.text((34, y - 9), f"{row:02d}", font=JBM(14), fill=(110, 118, 132))

def member_pixels(d, n, box, colors, seed):
    """离群像素 — 举手的成员（个体，按设计打破秩序）"""
    r = random.Random(seed)
    for _ in range(n):
        cx = r.randint(box[0], box[2]); cy = r.randint(box[1], box[3])
        d.rectangle([cx * CELL, cy * CELL, cx * CELL + CELL, cy * CELL + CELL],
                    fill=r.choice(colors))

def statement(d, text, cy=None, font=None, color=WARM_WHITE):
    """底部单一宣言句"""
    font = font or SILK(30)
    if cy is None: cy = H - 150
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) / 2, cy), text, font=font, fill=color)

# ───────────────────────── CANVAS 01 · 莫比乌斯环 ─────────────────────────
def canvas_ring():
    img, d = new_canvas()
    draw_grid(d)
    stamp_corner_ticks(d)
    header_block(d, "01", "THE RING", "环 · 每一位成员都是像素")
    page_no(d, 1)
    ruler_left(d)

    # 莫比乌斯带：参数曲面投影（绕 x 轴旋转展示扭转）
    R = 14.5 * CELL          # 主半径 14.5 格
    HW = 3.2 * CELL          # 半宽 3.2 格
    rot = 0.42               # 投影旋转角
    cx0, cy0 = 30 * CELL, 40 * CELL

    def project(t, u):
        x = (R + u * math.cos(t / 2)) * math.cos(t)
        y = (R + u * math.cos(t / 2)) * math.sin(t)
        z = u * math.sin(t / 2)
        yp = y * math.cos(rot) - z * math.sin(rot)
        zp = y * math.sin(rot) + z * math.cos(rot)
        return x, yp, zp

    # 表面（暗琥珀 — 沉睡的大多数）＋ 边缘（亮琥珀 — 曲线本身）
    surface = {}
    edge = {}
    meridian = {}              # u 方向经线 — 让带子有体积
    T_N, U_N = 420, 28
    for i in range(T_N):
        t = 2 * math.pi * i / T_N
        for j in range(U_N):
            u = -HW + 2 * HW * j / (U_N - 1)
            x, y, z = project(t, u)
            gx, gy = int((cx0 + x) / CELL), int((cy0 + y) / CELL)
            if 0 <= gx < COLS and 0 <= gy < ROWS:
                surface[(gx, gy)] = True
                if j in (0, U_N - 1):
                    edge[(gx, gy)] = True
                if i % 35 == 0:
                    meridian[(gx, gy)] = True

    # 画表面（先）
    for (gx, gy) in surface:
        if (gx, gy) in edge or (gx, gy) in meridian: continue
        d.rectangle([gx * CELL, gy * CELL, gx * CELL + CELL, gy * CELL + CELL],
                    fill=(212, 165, 116, 62))
    # 经线（中等亮度 — 让带子有结构）
    for (gx, gy) in meridian:
        if (gx, gy) in edge: continue
        d.rectangle([gx * CELL, gy * CELL, gx * CELL + CELL, gy * CELL + CELL],
                    fill=(212, 165, 116, 96))
    # 边缘（最亮 — 环的轮廓）
    for (gx, gy) in edge:
        d.rectangle([gx * CELL, gy * CELL, gx * CELL + CELL, gy * CELL + CELL], fill=AMBER)

    # 举手的成员：更克制，留白更讲究
    member_pixels(d, 18, (8, 12, 52, 68), [PINK, PALE_BLUE, CREAM, AMBER], 11)

    statement(d, "298 PIXELS · ONE IMAGE", cy=H - 96, font=SILK(38))
    # 底部坐标 + 印章
    d.text((40, H - 60), "N 26°04′  E 119°17′  ·  FUZHOU", font=JBM(20), fill=(130, 138, 152))
    seal(d, W - 130, H - 110, size=64)
    return img

# ───────────────────────── CANVAS 02 · 网格日出 ─────────────────────────
def canvas_dawn():
    img, d = new_canvas()
    draw_grid(d)
    stamp_corner_ticks(d)
    header_block(d, "02", "THE DAWN", "黎明 · 每一次日出都是一次构建")
    page_no(d, 2)
    ruler_left(d)

    # 天空：离散色带（低分辨率色块，远看渐变、近看普查）
    bands = [
        (0, 9,   INK),
        (10, 17, (18, 26, 48)),
        (18, 25, (28, 44, 78)),
        (26, 31, MID_BLUE),
        (32, 37, (110, 148, 220)),
        (38, 43, PALE_BLUE),
        (44, 47, (232, 190, 196)),
        (48, 51, PINK),
        (52, 54, AMBER),
    ]
    for r0, r1, c in bands:
        for row in range(r0, r1 + 1):
            for col in range(COLS):
                d.rectangle([col * CELL, row * CELL, col * CELL + CELL, row * CELL + CELL], fill=c)

    # 太阳：格点对齐的圆，中心 (41, 45)，半径 5 格
    sun_c, sun_r, sun_row = 41, 5, 45
    sun_pixels = []
    for row in range(sun_row - sun_r, sun_row + sun_r + 1):
        for col in range(sun_c - sun_r, sun_c + sun_r + 1):
            if (col - sun_c) ** 2 + (row - sun_row) ** 2 <= sun_r ** 2:
                d.rectangle([col * CELL, row * CELL, col * CELL + CELL, row * CELL + CELL], fill=CREAM)
                sun_pixels.append((col, row))
    # 极克制光晕 — 太阳外圈 1 格孤立奶油像素
    for col, row in sun_pixels:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nc, nr = col + dx, row + dy
            if (nc, nr) not in sun_pixels and 30 <= nc <= 52 and 30 <= nr <= 54:
                d.rectangle([nc * CELL, nr * CELL, nc * CELL + CELL, nr * CELL + CELL], fill=AMBER)

    # 地平线（琥珀一线）
    for col in range(COLS):
        d.rectangle([col * CELL, 55 * CELL, col * CELL + CELL, 55 * CELL + CELL], fill=AMBER)

    # 大地：夜色 + 城市灯火（离散个体）
    for row in range(56, ROWS):
        for col in range(COLS):
            d.rectangle([col * CELL, row * CELL, col * CELL + CELL, row * CELL + CELL], fill=INK)
    r = random.Random(7)
    for _ in range(54):
        row = r.randint(57, 72); col = r.randint(1, COLS - 2)   # 留 8 行干净底带放文字
        d.rectangle([col * CELL, row * CELL, col * CELL + CELL, row * CELL + CELL],
                    fill=r.choice([PINK, PALE_BLUE, AMBER, CREAM]))

    # 水中倒影：太阳正下方几粒琥珀
    for i in range(1, 6):
        d.rectangle([(sun_c - 2 + i) * CELL, (58 + i) * CELL,
                     (sun_c - 2 + i) * CELL + CELL, (58 + i) * CELL + CELL], fill=AMBER)

    statement(d, "EVERY DAWN IS A BUILD", cy=H - 90)
    d.text((40, H - 60), "06:12:00  ·  BUILD #2026", font=JBM(18), fill=(110, 118, 132))
    seal(d, W - 120, H - 100, size=58)
    return img

# ───────────────────────── CANVAS 03 · 递归像素 ─────────────────────────
def canvas_recursion():
    img, d = new_canvas()
    draw_grid(d)
    stamp_corner_ticks(d)
    header_block(d, "03", "THE RECURSION", "递归 · 像素中的像素")
    page_no(d, 3)
    ruler_left(d)

    cx, cy = 30, 40   # 中心格
    levels = [44, 30, 19, 11, 6, 2]   # 逐级递归框（格）

    # 视场：取消全图贯穿十字，改为中心四个角的微型角标
    # 留出最外框 1 格安全区供 member 像素游走
    for ax, ay in [(cx - 44, cy - 44), (cx + 45, cy - 44), (cx - 44, cy + 45), (cx + 45, cy + 45)]:
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            d.line([(ax * CELL + dx * 18, ay * CELL), (ax * CELL, ay * CELL),
                    (ax * CELL, ay * CELL + dy * 18)], fill=(110, 118, 132), width=2)

    # 递归框 + 缩放标尺
    for i, half in enumerate(levels):
        x0, y0 = (cx - half) * CELL, (cy - half) * CELL
        x1, y1 = (cx + half + 1) * CELL, (cy + half + 1) * CELL
        width = 2 if i < 3 else 3
        color = (110, 118, 132) if i < 2 else AMBER
        d.rectangle([x0, y0, x1, y1], outline=color, width=width)
        # 角标
        t = 16 if i < 2 else 22
        for (ax, ay, sxp, syp) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line([(ax, ay), (ax + sxp * t, ay)], fill=color, width=width + 1)
            d.line([(ax, ay), (ax, ay + syp * t)], fill=color, width=width + 1)
        # 缩放标号（左侧）
        d.text((x0 - 72, y0 + half * CELL - 10), f"×{4 ** (len(levels) - 1 - i)}",
               font=JBM(18), fill=(130, 138, 152))

    # 最内层：唯一的琥珀像素 — 举手的那个成员
    d.rectangle([cx * CELL, cy * CELL, cx * CELL + CELL, cy * CELL + CELL], fill=AMBER)
    # 更亮的光晕（一圈渐隐成员）
    for r_, c_ in [((2,), (150, 170, 200)), ((4,), (120, 140, 170)), ((8,), (90, 110, 140))]:
        pass
    glow = [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]
    for gx, gy in glow:
        d.rectangle([gx * CELL, gy * CELL, gx * CELL + CELL, gy * CELL + CELL], fill=AMBER_DIM)

    # 稀疏成员像素（避开最外框外的 1 格安全区）
    r = random.Random(3)
    safe = 46
    for _ in range(16):
        col = r.randint(8, 52); row = r.randint(18, 62)
        if abs(col - cx) < 5 and abs(row - cy) < 5: continue
        if abs(col - cx) > safe or abs(row - cy) > safe: continue
        d.rectangle([col * CELL, row * CELL, col * CELL + CELL, row * CELL + CELL],
                    fill=r.choice([PINK, PALE_BLUE, CREAM]))

    statement(d, "A PIXEL WITHIN A PIXEL", cy=H - 96, font=SILK(38))
    d.text((40, H - 60), "ZOOM ×256  ·  1 / 298", font=JBM(20), fill=(130, 138, 152))
    seal(d, W - 130, H - 110, size=64)
    return img

# ───────────────────────── 输出 ─────────────────────────
if __name__ == "__main__":
    import os
    out = "/Users/3yearszhuang/Documents/FztbuCS-Project/design-lab/art"
    os.makedirs(out, exist_ok=True)
    canvases = [canvas_ring(), canvas_dawn(), canvas_recursion()]
    for i, c in enumerate(canvases, 1):
        p = os.path.join(out, f"canvas-0{i}.png")
        c.save(p)
        print("saved", p, c.size)
    # 三联张合册 PDF
    pdf = os.path.join(out, "pixel-congregation-triptych.pdf")
    canvases[0].save(pdf, save_all=True, append_images=canvases[1:], resolution=150.0)
    print("saved", pdf)
