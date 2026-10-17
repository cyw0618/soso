# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 21~30번 그림 (mg_art3.art 로 2배 해상도 저장, 크기 인자는 무대 px)."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3

art = A3.art


def _c(col, a=255):
    return tuple(col[:3]) + (a,)


def _glow_disc(d, cx, cy, r, col, steps=8, amax=90):
    for k in range(steps, 0, -1):
        rr = r * k / steps
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=_c(col, int(amax * (1 - k / steps) + 8)))


# ================================================================== 21 테이블 하키
def hockey_table(w=440, h=200, goal_h=68):
    def f(d, im, s):
        W, H = im.width, im.height
        rim = 10 * s
        d.rounded_rectangle((0, 0, W - 1, H - 1), 22 * s, fill=(34, 52, 120, 255), outline=(150, 176, 255, 255), width=int(1.5 * s))
        d.rounded_rectangle((4 * s, 4 * s, W - 4 * s, H - 4 * s), 19 * s, outline=(80, 108, 210, 255), width=int(1 * s))
        x0, y0, x1, y1 = rim, rim, W - rim, H - rim
        d.rounded_rectangle((x0, y0, x1, y1), 14 * s, fill=(14, 22, 58, 255), outline=(190, 210, 255, 255), width=int(1.2 * s))
        # 공기 구멍
        for yy in range(int(y0 + 10 * s), int(y1 - 6 * s), int(14 * s)):
            for xx in range(int(x0 + 10 * s), int(x1 - 6 * s), int(14 * s)):
                d.ellipse((xx - 0.7 * s, yy - 0.7 * s, xx + 0.7 * s, yy + 0.7 * s), fill=(44, 60, 120, 255))
        cx, cy = W / 2, H / 2
        d.line((cx, y0, cx, y1), fill=(120, 150, 255, 200), width=int(1.6 * s))
        r = 30 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(120, 150, 255, 200), width=int(1.6 * s))
        d.ellipse((cx - 4 * s, cy - 4 * s, cx + 4 * s, cy + 4 * s), fill=(120, 150, 255, 220))
        gh = goal_h * s / 2
        for side, col in ((0, (80, 150, 255)), (1, (255, 80, 100))):
            gx = x0 if side == 0 else x1
            r2 = 42 * s
            box = (gx - r2, cy - r2, gx + r2, cy + r2)
            d.arc(box, -90 if side == 0 else 90, 90 if side == 0 else 270, fill=_c(col, 220), width=int(1.6 * s))
            # 골문 (틈)
            gx0 = 0 if side == 0 else x1 - 1 * s
            gx1 = x0 + 1 * s if side == 0 else W
            d.rectangle((gx0, cy - gh, gx1, cy + gh), fill=(4, 6, 16, 255))
            for k in range(6):
                a = 200 - k * 30
                xx = (x0 + k * s) if side == 0 else (x1 - k * s)
                d.line((xx, cy - gh, xx, cy + gh), fill=_c(col, a), width=int(1 * s))
            d.ellipse((gx - 3 * s, cy - gh - 3 * s, gx + 3 * s, cy - gh + 3 * s), fill=(230, 236, 255, 255))
            d.ellipse((gx - 3 * s, cy + gh - 3 * s, gx + 3 * s, cy + gh + 3 * s), fill=(230, 236, 255, 255))
    return art('k21_table', w, h, f)


def hockey_puck(r=10):
    def f(d, im, s):
        W = im.width
        d.ellipse((0.5 * s, 1.5 * s, W - 0.5 * s, W - 0.2 * s), fill=(0, 0, 0, 120))
        d.ellipse((s, s, W - s, W - 2 * s), fill=(250, 210, 70, 255), outline=(120, 80, 0, 255), width=int(1 * s))
        d.ellipse((W * 0.26, W * 0.24, W * 0.74, W * 0.66), outline=(255, 244, 190, 255), width=int(1 * s))
        d.ellipse((W * 0.3, W * 0.18, W * 0.5, W * 0.32), fill=(255, 255, 255, 140))
    return art('k21_puck', r * 2, r * 2, f)


def hockey_mallet(kind, r=15):
    col = {'me': ((90, 150, 255), (20, 50, 170)), 'ai': ((255, 100, 120), (150, 20, 40))}[kind]

    def f(d, im, s):
        W = im.width
        d.ellipse((s, 2 * s, W - s, W), fill=(0, 0, 0, 110))
        d.ellipse((s, s, W - s, W - 2 * s), fill=_c(col[1]), outline=(255, 255, 255, 255), width=int(1.2 * s))
        d.ellipse((W * 0.16, W * 0.14, W * 0.84, W * 0.8), fill=_c(col[0]))
        d.ellipse((W * 0.32, W * 0.3, W * 0.68, W * 0.64), fill=_c(col[1]), outline=(255, 255, 255, 180), width=int(0.8 * s))
        d.ellipse((W * 0.36, W * 0.32, W * 0.5, W * 0.42), fill=(255, 255, 255, 170))
    return art('k21_mallet_%s' % kind, r * 2, r * 2, f)


def score_pill(w=150, h=22):
    def f(d, im, s):
        d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height / 2, fill=(6, 10, 30, 225),
                            outline=(110, 140, 255, 255), width=int(1 * s))
    return art('k2x_pill_%d_%d' % (w, h), w, h, f)
