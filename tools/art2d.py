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


# ================================================================== 33. 물수제비
def s33_stone():
    def f(d, im, s):
        W, H = im.size
        d.ellipse((s, s, W - s, H - s), fill=(150, 158, 176, 255), outline=(40, 44, 60, 255), width=int(1.2 * s))
        d.ellipse((W * 0.2, H * 0.18, W * 0.6, H * 0.45), fill=(220, 226, 240, 160))
    return art('s33_stone', 14, 9, f)


def s33_splash():
    def f(d, im, s):
        W, H = im.size
        d.ellipse((W * 0.08, H * 0.62, W * 0.92, H * 0.98), outline=(230, 245, 255, 230), width=int(1.4 * s))
        for k in range(7):
            a = math.radians(200 + k * 23)
            x, y = W / 2 + math.cos(a) * W * 0.36, H * 0.78 + math.sin(a) * H * 0.62
            r = (1.6 - abs(k - 3) * 0.2) * s
            d.ellipse((x - r, y - r, x + r, y + r), fill=(235, 248, 255, 240))
        d.polygon([(W * 0.42, H * 0.8), (W * 0.5, H * 0.2), (W * 0.58, H * 0.8)], fill=(200, 235, 255, 200))
    return art('s33_splash', 32, 22, f)


def s33_gauge(R=62):
    """각도계: 그림 가운데가 회전 중심 (오른쪽 위 4분의 1만 그림)."""
    def f(d, im, s):
        W = im.width
        c = W / 2
        r = R * s
        d.pieslice((c - r, c - r, c + r, c + r), -62, 0, fill=(10, 16, 40, 200), outline=(120, 150, 250, 255), width=int(1.4 * s))
        d.pieslice((c - r, c - r, c + r, c + r), -26, -14, fill=(40, 200, 120, 230))
        for a in range(0, 61, 5):
            rad = math.radians(-a)
            r0 = r * (0.86 if a % 15 else 0.78)
            d.line([(c + r0 * math.cos(rad), c + r0 * math.sin(rad)), (c + r * 0.97 * math.cos(rad), c + r * 0.97 * math.sin(rad))],
                   fill=(220, 230, 255, 255), width=int((1.4 if a % 15 == 0 else 0.8) * s))
        for a in (0, 30, 60):
            rad = math.radians(-a)
            d.text((c + r * 0.62 * math.cos(rad) + 2 * s, c + r * 0.62 * math.sin(rad) - 2 * s), '%d°' % a, font=font('jalnan', int(7 * s)),
                   fill=(200, 210, 240, 255), anchor='mm')
        d.text((c + r * 0.5, c - r * 0.12), '20°', font=font('jalnan', int(6 * s)), fill=(120, 255, 170, 255), anchor='mm')
    return art('s33_gauge', 2 * R + 4, 2 * R + 4, f)


def s33_needle(L=58):
    def f(d, im, s):
        W, H = im.size
        c = W / 2
        d.line([(c, H / 2), (W - 2 * s, H / 2)], fill=(255, 90, 110, 255), width=int(2.4 * s))
        d.ellipse((c - 3 * s, H / 2 - 3 * s, c + 3 * s, H / 2 + 3 * s), fill=(255, 255, 255, 255), outline=(60, 10, 20, 255), width=int(s))
    return art('s33_needle', 2 * L, 8, f)


def s33_power(H=96):
    def f(d, im, s):
        W, Hh = im.size
        d.rounded_rectangle((0, 0, W - 1, Hh - 1), 4 * s, fill=(6, 10, 30, 230), outline=(120, 150, 250, 255), width=int(1.2 * s))
        top, bot = 3 * s, Hh - 3 * s
        for y in range(int(top), int(bot)):
            t = 1 - (y - top) / (bot - top)
            col = (int(60 + 180 * t), int(110 + 40 * (1 - t)), int(255 - 160 * t))
            d.line([(3 * s, y), (W - 3 * s, y)], fill=col + (255,))
        # 좋은 힘 구간 (78~94)
        y0 = bot - (bot - top) * 0.94
        y1 = bot - (bot - top) * 0.78
        d.rectangle((1 * s, y0, W - 1 * s, y1), outline=(120, 255, 170, 255), width=int(1.6 * s))
    return art('s33_power', 18, H, f)


def s33_marker():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(0, 0), (W, H / 2), (0, H)], fill=(255, 255, 255, 255), outline=(20, 20, 40, 255))
    return art('s33_marker', 10, 10, f)


def s33_bank():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(0, H * 0.25), (W * 0.7, H * 0.3), (W, H * 0.62), (W, H), (0, H)], fill=(52, 84, 60, 255))
        d.polygon([(0, H * 0.25), (W * 0.7, H * 0.3), (W, H * 0.62), (W * 0.9, H * 0.66), (W * 0.62, H * 0.4), (0, H * 0.38)],
                  fill=(92, 140, 90, 255))
        rng = random.Random(33)
        for k in range(26):
            x = rng.uniform(0.02, 0.85) * W
            y = H * (0.27 + 0.03 * x / W)
            d.line([(x, y), (x + rng.uniform(-2, 2) * s, y - rng.uniform(3, 7) * s)], fill=(140, 200, 120, 255), width=int(0.8 * s))
        for k in range(5):
            x, y = rng.uniform(0.1, 0.8) * W, rng.uniform(0.55, 0.9) * H
            d.ellipse((x - 4 * s, y - 2.5 * s, x + 4 * s, y + 2.5 * s), fill=(120, 126, 140, 255))
    return art('s33_bank', 110, 60, f)


def s33_water(w=400, h=8):
    def f(d, im, s):
        W, H = im.size
        for k in range(0, int(W), int(14 * s)):
            d.arc((k, 0, k + 14 * s, H), 200, 340, fill=(200, 230, 255, 150), width=int(1 * s))
    return art('s33_water', w, h, f)


# ================================================================== 35. BRT 정차
def s35_bus():
    def f(d, im, s):
        W, H = im.size
        body = (2 * s, 3 * s, W - 3 * s, H - 9 * s)
        d.rounded_rectangle(body, 7 * s, fill=(28, 170, 160, 255), outline=(6, 40, 40, 255), width=int(1.4 * s))
        d.rounded_rectangle((W - 20 * s, 5 * s, W - 4 * s, H - 20 * s), 4 * s, fill=(160, 220, 255, 255), outline=(10, 40, 60, 255),
                            width=int(s))
        for k in range(6):
            x = 10 * s + k * 22 * s
            d.rounded_rectangle((x, 7 * s, x + 18 * s, 20 * s), 2 * s, fill=(130, 190, 230, 255), outline=(10, 40, 60, 255), width=int(s))
            d.ellipse((x + 5 * s, 11 * s, x + 11 * s, 19 * s), fill=(40, 40, 60, 255))
        # 앞문 (오른쪽 앞) / 가운데 문
        for x0 in (W - 38 * s, W * 0.42):
            d.rectangle((x0, 7 * s, x0 + 14 * s, H - 10 * s), fill=(120, 180, 220, 255), outline=(255, 255, 255, 255), width=int(1.2 * s))
            d.line([(x0 + 7 * s, 7 * s), (x0 + 7 * s, H - 10 * s)], fill=(30, 60, 80, 255), width=int(s))
        d.rectangle((2 * s, H - 17 * s, W - 3 * s, H - 13 * s), fill=(250, 250, 255, 255))
        d.text((W * 0.24, H - 26 * s), 'BRT', font=font('jalnan', int(8 * s)), fill=(255, 255, 255, 255), anchor='mm')
        for x in (24 * s, W - 52 * s):
            d.ellipse((x - 8 * s, H - 17 * s, x + 8 * s, H - 1 * s), fill=(20, 22, 30, 255), outline=(90, 96, 120, 255), width=int(1.4 * s))
            d.ellipse((x - 3 * s, H - 12 * s, x + 3 * s, H - 6 * s), fill=(170, 176, 196, 255))
        d.rectangle((W - 6 * s, H - 24 * s, W - 2 * s, H - 19 * s), fill=(255, 240, 180, 255))
    return art('s35_bus', 172, 54, f)


def s35_mark():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((W / 2 - 1.5 * s, 14 * s, W / 2 + 1.5 * s, H), fill=(255, 255, 255, 255))
        d.polygon([(W / 2 - 7 * s, 2 * s), (W / 2 + 7 * s, 2 * s), (W / 2, 13 * s)], fill=(255, 80, 100, 255), outline=(60, 0, 10, 255))
        d.text((W / 2, H - 6 * s), '정차', font=font('jalnan', int(6 * s)), fill=(255, 255, 255, 255), anchor='mm',
               stroke_width=int(s), stroke_fill=(20, 20, 40))
    return art('s35_mark', 28, 66, f)


def s35_shelter():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, H - 10 * s, W, H), fill=(150, 156, 176, 255), outline=(40, 44, 60, 255), width=int(s))
        d.rectangle((0, H - 10 * s, W, H - 8 * s), fill=(255, 230, 120, 255))
        d.polygon([(6 * s, 12 * s), (W - 6 * s, 12 * s), (W - 2 * s, 4 * s), (2 * s, 4 * s)], fill=(40, 70, 170, 255), outline=(10, 16, 50, 255))
        for x in (14 * s, W - 14 * s):
            d.rectangle((x - 1.5 * s, 12 * s, x + 1.5 * s, H - 10 * s), fill=(80, 90, 120, 255))
        d.rectangle((18 * s, 16 * s, W - 18 * s, H - 14 * s), fill=(160, 200, 240, 110), outline=(200, 220, 255, 200), width=int(s))
        d.rounded_rectangle((W / 2 - 22 * s, 16 * s, W / 2 + 22 * s, 26 * s), 2 * s, fill=(10, 20, 60, 255))
        d.text((W / 2, 21 * s), 'BRT 정류장', font=font('nsr', int(6 * s)), fill=(255, 255, 255, 255), anchor='mm')
        d.rectangle((W / 2 - 12 * s, H - 22 * s, W / 2 + 12 * s, H - 16 * s), fill=(110, 80, 60, 255))
    return art('s35_shelter', 130, 70, f)


def s35_post():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((W / 2 - 1.5 * s, 8 * s, W / 2 + 1.5 * s, H), fill=(90, 100, 130, 255))
        d.line([(W / 2, 8 * s), (W / 2 + 9 * s, 5 * s)], fill=(90, 100, 130, 255), width=int(2 * s))
        d.ellipse((W / 2 + 6 * s, 3 * s, W / 2 + 14 * s, 8 * s), fill=(255, 236, 170, 255))
    return art('s35_post', 30, 80, f)


def s35_road():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, 8 * s), fill=(110, 116, 136, 255))
        d.rectangle((0, 8 * s, W, H), fill=(44, 48, 62, 255))
        d.rectangle((0, 7 * s, W, 9 * s), fill=(200, 205, 220, 255))
        d.rectangle((0, H - 3 * s, W, H), fill=(26, 28, 38, 255))
    return art('s35_road', 480, 56, f)


def s35_dash():
    return A3.box('s35_dash', 30, 4, (230, 230, 240), rim=None, r=1)


def s35_rider(lean):
    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        d.ellipse((cx - 5 * s, 2 * s, cx + 5 * s, 12 * s), fill=(250, 214, 180, 255), outline=(40, 30, 30, 255), width=int(s))
        d.rounded_rectangle((cx - 6 * s, 12 * s, cx + 6 * s, 30 * s), 3 * s, fill=(200, 80, 110, 255) if lean == 0 else (220, 60, 70, 255),
                            outline=(40, 10, 20, 255), width=int(s))
        d.line([(cx - 3 * s, 30 * s), (cx - 3 * s, H - s)], fill=(40, 50, 90, 255), width=int(3 * s))
        d.line([(cx + 3 * s, 30 * s), (cx + 3 * s, H - s)], fill=(40, 50, 90, 255), width=int(3 * s))
        d.line([(cx + 5 * s, 14 * s), (cx + 6 * s, 1 * s)], fill=(250, 214, 180, 255), width=int(2.4 * s))
    return art('s35_rider_%d' % lean, 20, 44, f)


# ================================================================== 37. 떡메치기
def s37_board():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((0, 4 * s, W, H - 2 * s), 6 * s, fill=(150, 96, 56, 255), outline=(50, 26, 10, 255), width=int(1.5 * s))
        d.rounded_rectangle((4 * s, 4 * s, W - 4 * s, 12 * s), 4 * s, fill=(196, 140, 90, 255))
        for k in range(5):
            y = (16 + k * 4) * s
            d.line([(10 * s, y), (W - 10 * s, y)], fill=(120, 72, 40, 255), width=int(0.8 * s))
        for x in (14 * s, W - 14 * s):
            d.rectangle((x - 5 * s, H - 6 * s, x + 5 * s, H), fill=(90, 56, 30, 255))
    return art('s37_board', 200, 34, f)


def s37_cake(kind):
    def f(d, im, s):
        W, H = im.size
        if kind == 'round':
            box = (4 * s, H * 0.18, W - 4 * s, H - 2 * s)
        elif kind == 'flat':
            box = (0, H * 0.48, W, H - 2 * s)
        else:
            box = (8 * s, H * 0.05, W - 8 * s, H - 2 * s)
        d.ellipse(box, fill=(246, 246, 240, 255), outline=(150, 150, 160, 255), width=int(1.2 * s))
        x0, y0, x1, y1 = box
        d.ellipse((x0 + (x1 - x0) * 0.2, y0 + (y1 - y0) * 0.12, x0 + (x1 - x0) * 0.55, y0 + (y1 - y0) * 0.4), fill=(255, 255, 255, 255))
        d.ellipse((x0 + (x1 - x0) * 0.62, y0 + (y1 - y0) * 0.5, x0 + (x1 - x0) * 0.72, y0 + (y1 - y0) * 0.62), fill=(215, 215, 210, 255))
    return art('s37_cake_%s' % kind, 96, 40, f)


def s37_mallet(pose):
    """떡메: up(들어 올림) / down(내리침). 그림 가운데가 판 위치에 맞도록 크게 그림."""
    def f(d, im, s):
        W, H = im.size
        wood, dark = (176, 120, 70, 255), (60, 34, 14, 255)
        if pose == 'up':
            # 손잡이: 왼쪽 아래 → 오른쪽 위로 들린 머리
            d.line([(W * 0.12, H * 0.92), (W * 0.48, H * 0.3)], fill=(120, 80, 44, 255), width=int(5 * s))
            cx, cy = W * 0.52, H * 0.22
            d.polygon([(cx - 22 * s, cy - 2 * s), (cx + 8 * s, cy - 20 * s), (cx + 22 * s, cy + 4 * s), (cx - 8 * s, cy + 22 * s)], fill=wood,
                      outline=dark)
            d.line([(cx - 8 * s, cy + 22 * s), (cx + 22 * s, cy + 4 * s)], fill=(140, 92, 50, 255), width=int(3 * s))
        else:
            d.line([(W * 0.08, H * 0.82), (W * 0.66, H * 0.62)], fill=(120, 80, 44, 255), width=int(5 * s))
            cx, cy = W * 0.74, H * 0.66
            d.rounded_rectangle((cx - 13 * s, cy - 24 * s, cx + 13 * s, cy + 24 * s), 4 * s, fill=wood, outline=dark, width=int(1.4 * s))
            d.line([(cx - 13 * s, cy + 18 * s), (cx + 13 * s, cy + 18 * s)], fill=(140, 92, 50, 255), width=int(3 * s))
    return art('s37_mallet_%s' % pose, 150, 110, f)


def s37_hand(kind):
    def f(d, im, s):
        W, H = im.size
        skin = (250, 214, 182, 255) if kind != 'ouch' else (255, 150, 150, 255)
        # 소매 (오른쪽에서 들어옴)
        d.polygon([(W * 0.55, H * 0.15), (W, H * 0.05), (W, H * 0.95), (W * 0.55, H * 0.85)], fill=(232, 92, 132, 255), outline=(80, 20, 40, 255))
        d.rectangle((W * 0.5, H * 0.18, W * 0.58, H * 0.82), fill=(255, 255, 255, 255), outline=(80, 20, 40, 255))
        # 손바닥
        d.rounded_rectangle((W * 0.12, H * 0.28, W * 0.52, H * 0.72), 8 * s, fill=skin, outline=(110, 60, 40, 255), width=int(1.2 * s))
        for k in range(4):
            y = H * (0.3 + k * 0.12)
            d.rounded_rectangle((W * 0.02, y, W * 0.2, y + H * 0.09), 3 * s, fill=skin, outline=(110, 60, 40, 255), width=int(s))
        d.rounded_rectangle((W * 0.3, H * 0.08, W * 0.42, H * 0.34), 3 * s, fill=skin, outline=(110, 60, 40, 255), width=int(s))
        if kind == 'ouch':
            for k in range(5):
                a = math.radians(200 + k * 30)
                cx, cy = W * 0.3, H * 0.5
                d.line([(cx + math.cos(a) * 14 * s, cy + math.sin(a) * 14 * s), (cx + math.cos(a) * 22 * s, cy + math.sin(a) * 22 * s)],
                       fill=(255, 60, 60, 255), width=int(1.6 * s))
    return art('s37_hand_%s' % kind, 96, 46, f)


def s37_warn():
    def f(d, im, s):
        W, H = im.size
        d.ellipse((s, s, W - s, H - s), fill=(255, 70, 90, 255), outline=(255, 255, 255, 255), width=int(1.4 * s))
        d.text((W / 2, H / 2 + 0.5 * s), '!', font=font('jalnan', int(14 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return art('s37_warn', 22, 22, f)


# ================================================================== 38. 간판 글자
def s38_tile(kind):
    cols = {'n': ((246, 240, 226), (200, 186, 160)), 'u': ((70, 80, 110), (40, 46, 70)), 'x': ((255, 120, 130), (200, 40, 60)),
            'g': ((140, 240, 170), (40, 160, 90))}
    top, bot = cols[kind]

    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, 3 * s, W - s, H - s), 6 * s, fill=tuple(int(c * 0.6) for c in bot) + (255,))
        d.rounded_rectangle((s, s, W - s, H - 4 * s), 6 * s, fill=top + (255,), outline=tuple(int(c * 0.5) for c in bot) + (255,),
                            width=int(1.2 * s))
        d.rounded_rectangle((4 * s, 3 * s, W - 4 * s, H * 0.4), 4 * s, fill=(255, 255, 255, 60))
    return art('s38_tile_%s' % kind, 46, 50, f)


def s38_sign(kind):
    def f(d, im, s):
        W, H = im.size
        glow = kind == 'on'
        if glow:
            for k in range(6, 0, -1):
                d.rounded_rectangle((k * s, k * s, W - k * s, H - k * s), 10 * s, outline=(120, 180, 255, 40), width=int(2 * s))
        d.rounded_rectangle((6 * s, 6 * s, W - 6 * s, H - 6 * s), 8 * s, fill=(16, 22, 50, 255) if not glow else (30, 50, 120, 255),
                            outline=(140, 170, 255, 255) if glow else (80, 96, 150, 255), width=int(2 * s))
        for x in (14 * s, W - 14 * s):
            for y in (13 * s, H - 13 * s):
                d.ellipse((x - 2 * s, y - 2 * s, x + 2 * s, y + 2 * s), fill=(180, 190, 220, 255))
    return art('s38_sign_%s' % kind, 300, 66, f)


# ================================================================== 39. 숫자 합 10
def s39_digit(n, CL=30):
    pal = [(96, 130, 255), (80, 170, 255), (60, 190, 200), (70, 190, 130), (150, 200, 80), (230, 180, 60), (240, 130, 70),
           (240, 90, 110), (190, 100, 230)]

    def f(d, im, s):
        W, H = im.size
        if n == 0:
            d.rounded_rectangle((s, s, W - s, H - s), 5 * s, fill=(10, 14, 32, 255))
            return
        col = pal[n - 1]
        d.rounded_rectangle((s, s, W - s, H - s), 6 * s, fill=(18, 24, 52, 255), outline=col + (255,), width=int(1.6 * s))
        d.rounded_rectangle((3 * s, 3 * s, W - 3 * s, H * 0.45), 4 * s, fill=col + (40,))
        d.text((W / 2, H / 2 + s), str(n), font=font('jalnan', int(17 * s)), fill=(255, 255, 255, 255), anchor='mm',
               stroke_width=int(1.2 * s), stroke_fill=tuple(int(c * 0.4) for c in col))
    return art('s39_d%d' % n, CL, CL, f)


def s39_pop():
    def f(d, im, s):
        W = im.width
        for k in range(8):
            a = math.radians(k * 45)
            x, y = W / 2 + math.cos(a) * W * 0.34, W / 2 + math.sin(a) * W * 0.34
            d.ellipse((x - 2.2 * s, y - 2.2 * s, x + 2.2 * s, y + 2.2 * s), fill=(255, 255, 255, 230))
        d.ellipse((W * 0.3, W * 0.3, W * 0.7, W * 0.7), outline=(160, 200, 255, 255), width=int(1.6 * s))
    return art('s39_pop', 34, 34, f)


# ================================================================== 40. 선로 전환
TRAIN_COLS = [(230, 70, 90), (70, 120, 255), (60, 190, 110), (190, 110, 240)]


def s40_train(k):
    col = TRAIN_COLS[k]

    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, 2 * s, W - s, H - 2 * s), 4 * s, fill=col + (255,), outline=(10, 12, 30, 255), width=int(1.2 * s))
        d.polygon([(W - 9 * s, 2 * s), (W - s, H / 2), (W - 9 * s, H - 2 * s)], fill=tuple(min(255, c + 50) for c in col) + (255,))
        for x in range(5, int(W / s) - 12, 7):
            d.rectangle((x * s, 4.5 * s, (x + 4) * s, H - 4.5 * s), fill=(230, 240, 255, 230))
        d.line([(W * 0.55, 2 * s), (W * 0.55, H - 2 * s)], fill=(10, 12, 30, 200), width=int(s))
    return art('s40_train_%d' % k, 34, 14, f)


def s40_station(k, label):
    col = TRAIN_COLS[k]

    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, s, W - s, H - s), 6 * s, fill=(16, 20, 44, 240), outline=col + (255,), width=int(2 * s))
        d.rectangle((3 * s, 3 * s, W - 3 * s, 11 * s), fill=col + (255,))
        d.text((W / 2, 7.5 * s), '역', font=font('jalnan', int(6 * s)), fill=(255, 255, 255, 255), anchor='mm')
        d.text((W / 2, H * 0.64), label, font=font('jalnan', int(9 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return art('s40_station_%d' % k, 50, 36, f)


def s40_switch(state):
    """선로 전환기: up/down 방향 화살표 (원 안)."""
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((s, s, W - s, W - s), fill=(20, 26, 60, 235), outline=(255, 255, 255, 255), width=int(1.6 * s))
        sgn = -1 if state == 'up' else 1
        pts = [(c - 7 * s, c + sgn * 6 * s), (c + 5 * s, c - sgn * 6 * s)]
        d.line(pts, fill=(255, 220, 90, 255), width=int(3 * s))
        hx, hy = pts[1]
        d.polygon([(hx + 3 * s, hy - sgn * 3 * s), (hx - 6 * s, hy - sgn * 1 * s), (hx + 1 * s, hy + sgn * 7 * s)], fill=(255, 220, 90, 255))
    return art('s40_switch_%s' % state, 24, 24, f)
