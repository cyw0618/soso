# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 31~40번 그림 (mg_art3.art 위에 그린다. 이름은 s31_ ... 접두어)."""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter
from art_common import font, ensure_out
import mg_art3 as A3

art = A3.art


def _rr(d, box, r, **kw):
    d.rounded_rectangle(box, r, **kw)


def _c(col, a=255):
    return tuple(col[:3]) + (a,)


# ================================================================== 31. 드론 방제
def s31_cell(kind, CL=36):
    """논 칸: paddy / done / house / tree."""
    def f(d, im, s):
        W, H = im.size
        m = 1.2 * s
        if kind in ('paddy', 'done'):
            top, bot = ((70, 150, 84), (40, 104, 56)) if kind == 'paddy' else ((86, 186, 196), (40, 120, 150))
            for y in range(int(m), int(H - m)):
                t = y / H
                d.line([(m, y), (W - m, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
            # 모 줄
            for k in range(4):
                y = H * (0.2 + k * 0.2)
                for j in range(5):
                    x = W * (0.14 + j * 0.18)
                    col = (150, 220, 120, 255) if kind == 'paddy' else (200, 245, 255, 255)
                    d.line([(x, y + 2.5 * s), (x - 1.2 * s, y - 2.5 * s)], fill=col, width=int(0.9 * s))
                    d.line([(x, y + 2.5 * s), (x + 1.2 * s, y - 2.5 * s)], fill=col, width=int(0.9 * s))
            if kind == 'done':
                for k in range(7):
                    rx, ry = W * (0.15 + 0.7 * ((k * 37) % 10) / 10), H * (0.12 + 0.76 * ((k * 53) % 10) / 10)
                    d.ellipse((rx - 1.4 * s, ry - 1.4 * s, rx + 1.4 * s, ry + 1.4 * s), fill=(235, 252, 255, 230))
            d.rounded_rectangle((m, m, W - m, H - m), 4 * s, outline=(16, 40, 24, 255) if kind == 'paddy' else (220, 250, 255, 255),
                                width=int(1.2 * s))
        else:
            d.rounded_rectangle((m, m, W - m, H - m), 4 * s, fill=(54, 62, 80, 255), outline=(20, 24, 36, 255), width=int(1.2 * s))
            if kind == 'house':
                d.rectangle((W * 0.26, H * 0.48, W * 0.74, H * 0.84), fill=(226, 222, 210, 255), outline=(40, 30, 30, 255), width=int(s))
                d.polygon([(W * 0.16, H * 0.5), (W * 0.5, H * 0.18), (W * 0.84, H * 0.5)], fill=(200, 64, 70, 255), outline=(60, 10, 14, 255))
                d.rectangle((W * 0.44, H * 0.62, W * 0.56, H * 0.84), fill=(110, 70, 50, 255))
                d.rectangle((W * 0.3, H * 0.55, W * 0.4, H * 0.64), fill=(130, 190, 255, 255))
            else:
                d.rectangle((W * 0.46, H * 0.58, W * 0.54, H * 0.86), fill=(110, 76, 50, 255))
                for (cx, cy, r) in ((0.5, 0.36, 0.24), (0.34, 0.5, 0.17), (0.66, 0.5, 0.17)):
                    d.ellipse((W * (cx - r), H * (cy - r), W * (cx + r), H * (cy + r)), fill=(40, 120, 64, 255), outline=(14, 50, 24, 255),
                              width=int(s))
                d.ellipse((W * 0.38, H * 0.2, W * 0.5, H * 0.3), fill=(110, 190, 120, 160))
    return art('s31_cell_%s' % kind, CL, CL, f)


def s31_drone(frame):
    def f(d, im, s):
        W = im.width
        c = W / 2
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x, y = c + dx * W * 0.28, c + dy * W * 0.28
            d.line([(c, c), (x, y)], fill=(40, 46, 70, 255), width=int(2.2 * s))
            r = W * 0.17
            d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 220, 255, 70), outline=(230, 240, 255, 200), width=int(0.8 * s))
            a = (30 if frame == 1 else 75) + (0 if dx * dy > 0 else 90)
            for k in (0, 180):
                rad = math.radians(a + k)
                d.line([(x, y), (x + r * math.cos(rad), y + r * math.sin(rad))], fill=(255, 255, 255, 255), width=int(1.4 * s))
            d.ellipse((x - 1.5 * s, y - 1.5 * s, x + 1.5 * s, y + 1.5 * s), fill=(30, 30, 40, 255))
        d.rounded_rectangle((c - W * 0.17, c - W * 0.17, c + W * 0.17, c + W * 0.17), 3 * s, fill=(70, 110, 250, 255),
                            outline=(10, 16, 50, 255), width=int(1.2 * s))
        d.ellipse((c - W * 0.07, c - W * 0.07, c + W * 0.07, c + W * 0.07), fill=(170, 230, 255, 255))
    return art('s31_drone_%d' % frame, 34, 34, f)


def s31_start_ring():
    def f(d, im, s):
        W = im.width
        d.ellipse((2 * s, 2 * s, W - 2 * s, W - 2 * s), outline=(255, 255, 255, 230), width=int(2 * s))
    return art('s31_ring', 30, 30, f)
