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
    def f(d, im, s):
        d.rectangle((0, 0, im.width, im.height), fill=(230, 230, 240, 255))
    return art('s35_dash', 30, 4, f)


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


# ================================================================== 34. 자전거 기어
def s34_tile(slope, TW=80, TH=300):
    def f(d, im, s):
        W, H = im.size
        ym = 40 * s
        yl, yr = ym + slope * 10 * s, ym - slope * 10 * s
        d.polygon([(0, yl), (W, yr), (W, H), (0, H)], fill=(58, 46, 70, 255))
        d.polygon([(0, yl), (W, yr), (W, yr + 9 * s), (0, yl + 9 * s)], fill=(90, 150, 90, 255))
        d.line([(0, yl), (W, yr)], fill=(170, 230, 150, 255), width=int(2 * s))
        d.line([(0, yl + 4 * s), (W, yr + 4 * s)], fill=(120, 124, 140, 255), width=int(3 * s))
        for k in range(3):
            x = (10 + k * 26) * s
            y = yl + (yr - yl) * x / W + (40 + k * 30) * s
            d.ellipse((x - 4 * s, y - 2 * s, x + 4 * s, y + 2 * s), fill=(80, 66, 92, 255))
    return art('s34_tile_%d' % (slope + 2), TW + 1, TH, f)


def s34_gauge():
    def f(d, im, s):
        W, H = im.size
        c, r = W / 2, W / 2 - 2 * s
        d.pieslice((c - r, H - r - 2 * s, c + r, H + r - 2 * s), 180, 360, fill=(10, 14, 36, 230), outline=(120, 150, 250, 255), width=int(1.4 * s))
        for a0, a1, col in ((180, 236, (230, 70, 90)), (236, 304, (50, 200, 120)), (304, 360, (240, 160, 60))):
            d.arc((c - r * 0.86, H - r * 0.86 - 2 * s, c + r * 0.86, H + r * 0.86 - 2 * s), a0, a1, fill=col + (255,), width=int(5 * s))
        d.text((c - r * 0.58, H - 9 * s), '무거움', font=font('nsr', int(6 * s)), fill=(255, 150, 160, 255), anchor='mm')
        d.text((c + r * 0.58, H - 9 * s), '헛돎', font=font('nsr', int(6 * s)), fill=(255, 200, 140, 255), anchor='mm')
    return art('s34_gauge', 86, 46, f)


def s34_needle(L=36):
    def f(d, im, s):
        W, H = im.size
        d.line([(W / 2, H / 2), (W / 2, 2 * s)], fill=(255, 255, 255, 255), width=int(2.4 * s))
        d.ellipse((W / 2 - 3 * s, H / 2 - 3 * s, W / 2 + 3 * s, H / 2 + 3 * s), fill=(255, 90, 110, 255))
    return art('s34_needle', 8, 2 * L, f)


def s34_gears(g):
    def f(d, im, s):
        W, H = im.size
        for k in range(5):
            r = (5 + (4 - k) * 1.6) * s
            cx, cy = (12 + k * 21) * s, H / 2
            on = k + 1 == g
            col = (255, 210, 80, 255) if on else (90, 100, 140, 255)
            for t in range(10):
                a = math.radians(t * 36)
                d.line([(cx, cy), (cx + math.cos(a) * (r + 2 * s), cy + math.sin(a) * (r + 2 * s))], fill=col, width=int(2 * s))
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=(10, 12, 30, 255), width=int(s))
            d.ellipse((cx - 2 * s, cy - 2 * s, cx + 2 * s, cy + 2 * s), fill=(10, 12, 30, 255))
    return art('s34_gears_%d' % g, 110, 26, f)


def s34_profile(heights, w=300, h=30):
    key = abs(hash(tuple(heights))) % 100000

    def f(d, im, s):
        W, H = im.size
        lo, hi = min(heights), max(heights)
        pts = [(W * i / (len(heights) - 1), (H - 3 * s) - (H - 6 * s) * (v - lo) / max(1, hi - lo)) for i, v in enumerate(heights)]
        d.rounded_rectangle((0, 0, W - 1, H - 1), 4 * s, fill=(8, 12, 30, 200), outline=(90, 110, 190, 255), width=int(s))
        d.polygon(pts + [(W, H), (0, H)], fill=(60, 90, 70, 255))
        d.line(pts, fill=(170, 230, 150, 255), width=int(1.4 * s))
        d.line([(W - 2 * s, 0), (W - 2 * s, H)], fill=(255, 255, 255, 255), width=int(2 * s))
    return art('s34_profile_%d' % key, w, h, f)


# ================================================================== 36. 민원 창구
S36_COL = [(70, 120, 255), (160, 100, 240), (50, 180, 120), (240, 100, 140)]


def _s36_icon(d, k, cx, cy, r, s):
    w = (255, 255, 255, 255)
    if k == 0:      # 집 (전입신고)
        d.polygon([(cx - r, cy), (cx, cy - r), (cx + r, cy)], fill=w)
        d.rectangle((cx - r * 0.7, cy, cx + r * 0.7, cy + r * 0.8), fill=w)
        d.rectangle((cx - r * 0.2, cy + r * 0.25, cx + r * 0.2, cy + r * 0.8), fill=S36_COL[0] + (255,))
    elif k == 1:    # 여권
        d.rounded_rectangle((cx - r * 0.7, cy - r, cx + r * 0.7, cy + r), 1.5 * s, fill=w)
        d.ellipse((cx - r * 0.35, cy - r * 0.45, cx + r * 0.35, cy + r * 0.25), outline=S36_COL[1] + (255,), width=int(1.2 * s))
        d.line([(cx - r * 0.4, cy + r * 0.6), (cx + r * 0.4, cy + r * 0.6)], fill=S36_COL[1] + (255,), width=int(s))
    elif k == 2:    # 세금 (동전)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=w)
        d.text((cx, cy + 0.5 * s), '₩', font=font('nanum', int(r * 1.5)), fill=S36_COL[2] + (255,), anchor='mm')
    else:           # 복지 (하트)
        d.ellipse((cx - r, cy - r * 0.8, cx, cy + r * 0.2), fill=w)
        d.ellipse((cx, cy - r * 0.8, cx + r, cy + r * 0.2), fill=w)
        d.polygon([(cx - r * 0.95, cy - r * 0.15), (cx + r * 0.95, cy - r * 0.15), (cx, cy + r)], fill=w)


S36_NAMES = ['전입신고', '여권', '세금', '복지']


def s36_counter(k):
    col = S36_COL[k]

    def f(d, im, s):
        W, H = im.size
        # 직원
        d.ellipse((W / 2 - 8 * s, 18 * s, W / 2 + 8 * s, 34 * s), fill=(250, 214, 182, 255), outline=(60, 40, 30, 255), width=int(s))
        d.pieslice((W / 2 - 9 * s, 16 * s, W / 2 + 9 * s, 30 * s), 180, 360, fill=(40, 30, 30, 255))
        d.rounded_rectangle((W / 2 - 12 * s, 33 * s, W / 2 + 12 * s, 48 * s), 4 * s, fill=(60, 70, 110, 255))
        # 책상
        d.rounded_rectangle((2 * s, 40 * s, W - 2 * s, H - s), 3 * s, fill=(36, 42, 70, 255), outline=col + (255,), width=int(1.5 * s))
        d.rectangle((2 * s, 40 * s, W - 2 * s, 44 * s), fill=(200, 205, 225, 255))
        # 간판
        d.rounded_rectangle((6 * s, 1 * s, W - 6 * s, 15 * s), 3 * s, fill=col + (255,), outline=(255, 255, 255, 200), width=int(s))
        _s36_icon(d, k, 15 * s, 8 * s, 4.5 * s, s)
        d.text((W / 2 + 6 * s, 8 * s), S36_NAMES[k], font=font('jalnan', int(8 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return art('s36_counter_%d' % k, 100, 64, f)


def s36_person(k, mood, look=0):
    col = S36_COL[k]
    shirts = [(110, 130, 170), (170, 120, 90), (90, 150, 140)]

    def f(d, im, s):
        W, H = im.size
        cx = W * 0.42
        d.rounded_rectangle((s, 2 * s, W - s, H - s), 6 * s, fill=(20, 28, 64, 150), outline=col + (200,), width=int(s))
        skin = (250, 214, 182, 255) if mood < 2 else (255, 150, 140, 255)
        d.rounded_rectangle((cx - 10 * s, 30 * s, cx + 10 * s, H - s), 6 * s, fill=shirts[look] + (255,), outline=(20, 24, 40, 255), width=int(s))
        d.ellipse((cx - 9 * s, 12 * s, cx + 9 * s, 30 * s), fill=skin, outline=(60, 40, 30, 255), width=int(s))
        d.pieslice((cx - 9.5 * s, 11 * s, cx + 9.5 * s, 25 * s), 180, 360, fill=(50, 36, 30, 255))
        ey = 21 * s
        for ex in (cx - 3.5 * s, cx + 3.5 * s):
            d.ellipse((ex - 1.2 * s, ey - 1.2 * s, ex + 1.2 * s, ey + 1.2 * s), fill=(20, 20, 30, 255))
        if mood == 0:
            d.arc((cx - 4 * s, 22 * s, cx + 4 * s, 28 * s), 20, 160, fill=(120, 40, 40, 255), width=int(1.2 * s))
        elif mood == 1:
            d.line([(cx - 3.5 * s, 26 * s), (cx + 3.5 * s, 26 * s)], fill=(120, 40, 40, 255), width=int(1.2 * s))
        else:
            d.arc((cx - 4 * s, 25 * s, cx + 4 * s, 31 * s), 200, 340, fill=(120, 20, 20, 255), width=int(1.4 * s))
            d.line([(cx - 6 * s, 17 * s), (cx - 1.5 * s, 19 * s)], fill=(60, 10, 10, 255), width=int(1.2 * s))
            d.line([(cx + 6 * s, 17 * s), (cx + 1.5 * s, 19 * s)], fill=(60, 10, 10, 255), width=int(1.2 * s))
        # 말풍선
        bx, by, r = W - 10 * s, 9 * s, 8.5 * s
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=col + (255,), outline=(255, 255, 255, 255), width=int(1.2 * s))
        d.polygon([(bx - 6 * s, by + 4 * s), (bx - 2 * s, by + 7 * s), (bx - 10 * s, by + 11 * s)], fill=col + (255,))
        _s36_icon(d, k, bx, by, 4.6 * s, s)
    return art('s36_p%d_%d_%d' % (k, mood, look), 40, 56, f)


def s36_ring():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, s, W - s, H - s), 8 * s, outline=(255, 220, 90, 255), width=int(2.4 * s))
    return art('s36_ring', 50, 66, f)


# ================================================================== 32. 옛 분교 교무실 방탈출
WOOD, WOOD_D, WOOD_L = (140, 92, 56), (64, 38, 20), (186, 132, 86)


def s32_room():
    def f(d, im, s):
        W, H = im.size
        fy = H - 70 * s           # 바닥 시작
        d.rectangle((0, 0, W, fy), fill=(58, 70, 96, 255))
        d.rectangle((0, fy - 34 * s, W, fy), fill=(92, 66, 48, 255))
        d.line([(0, fy - 34 * s), (W, fy - 34 * s)], fill=(140, 104, 74, 255), width=int(2 * s))
        for x in range(0, int(W), int(40 * s)):
            d.line([(x, fy - 32 * s), (x, fy)], fill=(70, 50, 36, 255), width=int(s))
        d.rectangle((0, fy, W, H), fill=(110, 78, 52, 255))
        for k in range(1, 6):
            y = fy + k * 12 * s
            d.line([(0, y), (W, y)], fill=(86, 60, 40, 255), width=int(s))
        # 창문 (밤)
        wx, wy = 300 * s, 22 * s
        d.rectangle((wx, wy, wx + 70 * s, wy + 52 * s), fill=(14, 20, 46, 255), outline=WOOD_L + (255,), width=int(3 * s))
        d.line([(wx + 35 * s, wy), (wx + 35 * s, wy + 52 * s)], fill=WOOD_L + (255,), width=int(2 * s))
        d.line([(wx, wy + 26 * s), (wx + 70 * s, wy + 26 * s)], fill=WOOD_L + (255,), width=int(2 * s))
        d.ellipse((wx + 46 * s, wy + 6 * s, wx + 58 * s, wy + 18 * s), fill=(240, 240, 210, 255))
        # 천장 띠와 '교무실' 팻말
        d.rectangle((0, 0, W, 6 * s), fill=(40, 46, 66, 255))
    return art('s32_room', 480, 206, f)


def s32_organ(state):
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((4 * s, 6 * s, W - 4 * s, H - 4 * s), 4 * s, fill=WOOD + (255,), outline=WOOD_D + (255,), width=int(1.4 * s))
        d.rectangle((10 * s, 2 * s, W - 10 * s, 10 * s), fill=WOOD_L + (255,), outline=WOOD_D + (255,), width=int(s))
        d.rectangle((14 * s, 28 * s, W - 14 * s, 38 * s), fill=(250, 248, 240, 255), outline=(40, 30, 20, 255), width=int(s))
        for k in range(1, 14):
            x = 14 * s + k * (W - 28 * s) / 14
            d.line([(x, 28 * s), (x, 38 * s)], fill=(60, 50, 40, 255), width=int(0.6 * s))
            if k % 7 not in (0, 3):
                d.rectangle((x - 1.2 * s, 28 * s, x + 1.2 * s, 34 * s), fill=(20, 20, 24, 255))
        d.rectangle((W * 0.3, 12 * s, W * 0.7, 24 * s), fill=(240, 236, 220, 255))
        for k in range(4):
            d.line([(W * 0.32, (14 + k * 2.6) * s), (W * 0.68, (14 + k * 2.6) * s)], fill=(60, 60, 70, 255), width=int(0.5 * s))
        # 아래 칸
        bx = (W * 0.3, H - 26 * s, W * 0.7, H - 8 * s)
        if state == 'open':
            d.rectangle(bx, fill=(30, 18, 10, 255), outline=WOOD_D + (255,), width=int(s))
        else:
            d.rectangle(bx, fill=WOOD_L + (255,), outline=WOOD_D + (255,), width=int(s))
            d.ellipse((W / 2 - 2 * s, H - 19 * s, W / 2 + 2 * s, H - 15 * s), fill=(220, 200, 120, 255))
        for x in (10 * s, W - 14 * s):
            d.rectangle((x, H - 8 * s, x + 4 * s, H), fill=WOOD_D + (255,))
    return art('s32_organ_%s' % state, 96, 76, f)


def s32_frame(state):
    def f(d, im, s):
        W, H = im.size
        if state == 'moved':
            d.rectangle((12 * s, 8 * s, W - 12 * s, H - 8 * s), fill=(250, 250, 236, 255), outline=(120, 120, 110, 255), width=int(s))
            for k in range(3):
                d.line([(16 * s, (14 + k * 5) * s), (W - 16 * s, (14 + k * 5) * s)], fill=(90, 90, 120, 255), width=int(0.8 * s))
        box = (2 * s, 2 * s, W * 0.62, H * 0.62) if state == 'moved' else (4 * s, 3 * s, W - 4 * s, H - 3 * s)
        d.rectangle(box, fill=(196, 160, 70, 255), outline=(90, 64, 20, 255), width=int(1.4 * s))
        x0, y0, x1, y1 = box
        d.rectangle((x0 + 4 * s, y0 + 4 * s, x1 - 4 * s, y1 - 4 * s), fill=(250, 246, 230, 255))
        d.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.36), '상장', font=font('jalnan', int((7 if state == 'hang' else 5) * s)), fill=(150, 30, 40, 255),
               anchor='mm')
        for k in range(2):
            yy = y0 + (y1 - y0) * (0.58 + k * 0.14)
            d.line([(x0 + 8 * s, yy), (x1 - 8 * s, yy)], fill=(120, 120, 130, 255), width=int(0.6 * s))
    return art('s32_frame_%s' % state, 54, 42, f)


def s32_paper(name, w, h, title):
    def f(d, im, s):
        W, H = im.size
        d.rectangle((s, s, W - s, H - s), fill=(244, 240, 226, 255), outline=(110, 100, 80, 255), width=int(s))
        d.text((W / 2, 7 * s), title, font=font('nsr', int(6 * s)), fill=(40, 40, 60, 255), anchor='mm')
        for r in range(2):
            for c in range(3):
                x, y = (8 + c * (w - 14) / 3) * s, (15 + r * (h - 20) / 2) * s
                d.rectangle((x, y, x + ((w - 14) / 3 - 4) * s, y + ((h - 20) / 2 - 4) * s), outline=(90, 90, 110, 255), width=int(0.8 * s))
        d.ellipse((W / 2 - 2 * s, -1 * s, W / 2 + 2 * s, 3 * s), fill=(220, 60, 60, 255))
    return art('s32_%s' % name, w, h, f)


def s32_board():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, H), fill=WOOD + (255,))
        d.rectangle((3 * s, 3 * s, W - 3 * s, H - 3 * s), fill=(34, 70, 52, 255))
        d.text((W / 2, 11 * s), '알림', font=font('nsr', int(8 * s)), fill=(240, 240, 230, 255), anchor='mm')
        for k, ln in enumerate(('서랍 번호 =', '결석한 아이들 자리', '(출석 번호 순)')):
            d.text((W / 2, (23 + k * 9) * s), ln, font=font('nsr', int(6.4 * s)), fill=(230, 236, 220, 255), anchor='mm')
    return art('s32_board', 96, 56, f)


def s32_desk():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, 8 * s), fill=WOOD_L + (255,), outline=WOOD_D + (255,), width=int(s))
        d.rectangle((4 * s, 8 * s, W - 4 * s, H), fill=WOOD + (255,), outline=WOOD_D + (255,), width=int(s))
        d.rectangle((10 * s, 14 * s, 40 * s, H - 4 * s), fill=(120, 78, 46, 255), outline=WOOD_D + (255,), width=int(s))
    return art('s32_desk', 132, 50, f)


def s32_drawer(state):
    def f(d, im, s):
        W, H = im.size
        if state == 'open':
            d.rectangle((0, 0, W, H), fill=(40, 24, 12, 255), outline=WOOD_D + (255,), width=int(s))
            d.rectangle((2 * s, H - 6 * s, W - 2 * s, H), fill=WOOD_L + (255,))
        else:
            d.rectangle((0, 0, W, H), fill=WOOD_L + (255,), outline=WOOD_D + (255,), width=int(s))
            d.rounded_rectangle((W / 2 - 7 * s, H / 2 - 3 * s, W / 2 + 7 * s, H / 2 + 3 * s), 2 * s, fill=(150, 156, 176, 255),
                                outline=(40, 40, 60, 255), width=int(s))
    return art('s32_drawer_%s' % state, 50, 18, f)


def s32_book():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(2 * s, H - 2 * s), (W - 6 * s, H - 2 * s), (W - 2 * s, 2 * s), (6 * s, 2 * s)], fill=(40, 70, 150, 255), outline=(10, 20, 50, 255))
        d.text((W / 2, H / 2), '출석부', font=font('nsr', int(5 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return art('s32_book', 32, 14, f)


def s32_stove():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((W / 2 - 4 * s, 0, W / 2 + 4 * s, H - 60 * s), fill=(70, 74, 86, 255), outline=(20, 20, 30, 255), width=int(s))
        d.ellipse((6 * s, H - 66 * s, W - 6 * s, H - 54 * s), fill=(80, 84, 96, 255), outline=(20, 20, 30, 255), width=int(s))
        d.rounded_rectangle((6 * s, H - 60 * s, W - 6 * s, H - 10 * s), 6 * s, fill=(54, 58, 70, 255), outline=(20, 20, 30, 255), width=int(1.4 * s))
        d.rounded_rectangle((14 * s, H - 46 * s, W - 14 * s, H - 26 * s), 3 * s, fill=(255, 130, 50, 255), outline=(20, 20, 30, 255), width=int(s))
        d.ellipse((18 * s, H - 40 * s, W - 18 * s, H - 30 * s), fill=(255, 220, 120, 255))
        for x in (10 * s, W - 14 * s):
            d.rectangle((x, H - 10 * s, x + 4 * s, H), fill=(30, 30, 40, 255))
    return art('s32_stove', 50, 130, f)


def s32_safe(state):
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, s, W - s, H - s), 4 * s, fill=(70, 80, 104, 255), outline=(16, 20, 34, 255), width=int(1.4 * s))
        if state == 'open':
            d.rectangle((5 * s, 5 * s, W - 5 * s, H - 5 * s), fill=(16, 18, 26, 255))
            d.rectangle((W - 7 * s, 5 * s, W - 1 * s, H - 5 * s), fill=(110, 120, 150, 255))
        else:
            d.rectangle((5 * s, 5 * s, W - 5 * s, H - 5 * s), outline=(130, 140, 170, 255), width=int(s))
            d.ellipse((W / 2 - 9 * s, H / 2 - 11 * s, W / 2 + 9 * s, H / 2 + 7 * s), fill=(200, 205, 220, 255), outline=(30, 30, 40, 255),
                      width=int(s))
            d.ellipse((W / 2 - 3 * s, H / 2 - 5 * s, W / 2 + 3 * s, H / 2 + 1 * s), fill=(60, 60, 80, 255))
            d.rectangle((W / 2 - 1 * s, H / 2 + 11 * s, W / 2 + 1 * s, H / 2 + 16 * s), fill=(20, 20, 30, 255))
    return art('s32_safe_%s' % state, 46, 50, f)


def s32_door(state):
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, H), fill=WOOD_D + (255,))
        if state == 'open':
            d.rectangle((4 * s, 4 * s, W - 4 * s, H), fill=(230, 236, 255, 255))
            d.polygon([(4 * s, 4 * s), (16 * s, 10 * s), (16 * s, H - 6 * s), (4 * s, H)], fill=WOOD + (255,))
        else:
            d.rectangle((4 * s, 4 * s, W - 4 * s, H), fill=WOOD + (255,), outline=(50, 30, 16, 255), width=int(s))
            d.rectangle((10 * s, 12 * s, W - 10 * s, 50 * s), fill=(150, 190, 220, 160), outline=(50, 30, 16, 255), width=int(s))
            d.line([(W / 2, 12 * s), (W / 2, 50 * s)], fill=(50, 30, 16, 255), width=int(s))
            d.ellipse((W - 14 * s, H / 2, W - 8 * s, H / 2 + 6 * s), fill=(230, 200, 100, 255))
            d.rectangle((W - 13 * s, H / 2 + 9 * s, W - 9 * s, H / 2 + 15 * s), fill=(30, 30, 30, 255))
            d.rounded_rectangle((W / 2 - 16 * s, 56 * s, W / 2 + 16 * s, 66 * s), 2 * s, fill=(240, 236, 220, 255))
            d.text((W / 2, 61 * s), '교무실', font=font('nsr', int(6 * s)), fill=(40, 30, 30, 255), anchor='mm')
    return art('s32_door_%s' % state, 56, 124, f)


def s32_item(kind):
    def f(d, im, s):
        W, H = im.size
        if kind == 'note':
            d.polygon([(5 * s, 6 * s), (W - 4 * s, 4 * s), (W - 6 * s, H - 5 * s), (4 * s, H - 4 * s)], fill=(250, 246, 220, 255), outline=(90, 80, 60, 255))
            for k in range(3):
                d.line([(8 * s, (10 + k * 4) * s), (W - 9 * s, (9 + k * 4) * s)], fill=(60, 60, 120, 255), width=int(0.8 * s))
        elif kind == 'sheet':
            d.rectangle((4 * s, 4 * s, W - 4 * s, H - 4 * s), fill=(250, 250, 244, 255), outline=(90, 90, 100, 255), width=int(s))
            for k in range(5):
                d.line([(6 * s, (8 + k * 2.6) * s), (W - 6 * s, (8 + k * 2.6) * s)], fill=(40, 40, 60, 255), width=int(0.5 * s))
            for x, y in ((10, 17), (15, 13), (20, 15)):
                d.ellipse(((x - 2) * s, (y - 1.5) * s, (x + 2) * s, (y + 1.5) * s), fill=(20, 20, 30, 255))
        elif kind == 'tongs':
            d.line([(5 * s, H - 5 * s), (W - 6 * s, 5 * s)], fill=(160, 166, 186, 255), width=int(2.2 * s))
            d.line([(9 * s, H - 4 * s), (W - 4 * s, 9 * s)], fill=(130, 136, 156, 255), width=int(2.2 * s))
            d.ellipse((3 * s, H - 9 * s, 10 * s, H - 2 * s), outline=(200, 205, 220, 255), width=int(1.4 * s))
        else:
            big = kind == 'key_d'
            col = (230, 196, 80, 255) if big else (190, 200, 220, 255)
            r = (6 if big else 4.5) * s
            d.ellipse((4 * s, H / 2 - r, 4 * s + 2 * r, H / 2 + r), outline=col, width=int(2.4 * s))
            d.line([(4 * s + 2 * r, H / 2), (W - 3 * s, H / 2)], fill=col, width=int(2.4 * s))
            for x in (W - 6 * s, W - 10 * s):
                d.line([(x, H / 2), (x, H / 2 + 5 * s)], fill=col, width=int(2 * s))
    return art('s32_item_%s' % kind, 26, 26, f)


def s32_slot(sel):
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, s, W - s, H - s), 5 * s, fill=(10, 14, 34, 220),
                            outline=(255, 220, 90, 255) if sel else (90, 110, 180, 255), width=int((2 if sel else 1) * s))
    return art('s32_slot_%d' % sel, 32, 30, f)


def s32_seats():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, H), fill=(244, 240, 226, 255), outline=(110, 100, 80, 255), width=int(1.4 * s))
        d.rounded_rectangle((W / 2 - 30 * s, 4 * s, W / 2 + 30 * s, 16 * s), 2 * s, fill=WOOD + (255,))
        d.text((W / 2, 10 * s), '교탁', font=font('nsr', int(7 * s)), fill=(255, 255, 255, 255), anchor='mm')
        for r in range(2):
            for c in range(3):
                x, y = (14 + c * 66) * s, (24 + r * 42) * s
                d.rounded_rectangle((x, y, x + 56 * s, y + 34 * s), 3 * s, fill=(226, 196, 150, 255), outline=WOOD_D + (255,), width=int(s))
                d.ellipse((x + 2 * s, y + 2 * s, x + 14 * s, y + 14 * s), fill=(40, 60, 140, 255))
                d.text((x + 8 * s, y + 8 * s), str(r * 3 + c + 1), font=font('jalnan', int(8 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return art('s32_seats', 212, 112, f)


def s32_staff():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((0, 0, W, H), 4 * s, fill=(250, 248, 240, 255), outline=(110, 100, 80, 255), width=int(s))
        for k in range(5):
            y = (16 + k * 8) * s
            d.line([(8 * s, y), (W - 8 * s, y)], fill=(30, 30, 40, 255), width=int(0.8 * s))
        d.text((14 * s, 56 * s), '도', font=font('nsr', int(6 * s)), fill=(150, 150, 170, 255), anchor='mm')
        d.text((16 * s, 9 * s), '풍금 악보', font=font('nsr', int(6 * s)), fill=(90, 90, 120, 255), anchor='lm')
        d.line([(W - 8 * s, 16 * s), (W - 8 * s, 48 * s)], fill=(30, 30, 40, 255), width=int(1.4 * s))
    return art('s32_staff', 236, 70, f)


def s32_notehead(ledger):
    def f(d, im, s):
        W, H = im.size
        if ledger:
            d.line([(0, H / 2), (W, H / 2)], fill=(30, 30, 40, 255), width=int(0.8 * s))
        d.ellipse((5 * s, H / 2 - 3 * s, W - 5 * s, H / 2 + 3 * s), fill=(20, 20, 30, 255))
        d.line([(W - 5.6 * s, H / 2), (W - 5.6 * s, H / 2 - 20 * s)], fill=(20, 20, 30, 255), width=int(1 * s))
    return art('s32_note_%d' % ledger, 20, 46, f)


def s32_key(pressed):
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, 0, W - s, H - s), 3 * s, fill=(255, 255, 250, 255) if not pressed else (190, 210, 255, 255),
                            outline=(40, 40, 50, 255), width=int(1.2 * s))
    return art('s32_key_%d' % pressed, 28, 72, f)


def s32_dial():
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((s, s, W - s, W - s), fill=(160, 166, 186, 255), outline=(30, 34, 50, 255), width=int(2 * s))
        d.ellipse((W * 0.18, W * 0.18, W * 0.82, W * 0.82), fill=(40, 44, 60, 255))
        for k in range(10):
            a = math.radians(-90 + k * 36)
            d.text((c + math.cos(a) * W * 0.4, c + math.sin(a) * W * 0.4), str(k), font=font('jalnan', int(10 * s)), fill=(20, 24, 40, 255),
                   anchor='mm')
            a2 = math.radians(-90 + k * 36 + 18)
            d.line([(c + math.cos(a2) * W * 0.34, c + math.sin(a2) * W * 0.34), (c + math.cos(a2) * W * 0.47, c + math.sin(a2) * W * 0.47)],
                   fill=(60, 64, 80, 255), width=int(s))
        d.ellipse((c - 8 * s, c - 8 * s, c + 8 * s, c + 8 * s), fill=(120, 126, 150, 255))
    return art('s32_dial', 110, 110, f)


def s32_wheel(n):
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, s, W - s, H - s), 4 * s, fill=(30, 34, 50, 255), outline=(170, 176, 200, 255), width=int(1.4 * s))
        for y, a in ((6 * s, 90), (H - 6 * s, 90)):
            d.text((W / 2, y), str((n + (1 if y < H / 2 else -1)) % 10), font=font('jalnan', int(7 * s)), fill=(120, 126, 150, a), anchor='mm')
        d.rectangle((3 * s, H / 2 - 10 * s, W - 3 * s, H / 2 + 10 * s), fill=(236, 238, 246, 255))
        d.text((W / 2, H / 2 + s), str(n), font=font('jalnan', int(15 * s)), fill=(20, 24, 40, 255), anchor='mm')
    return art('s32_wheel_%d' % n, 30, 46, f)


def s32_notes_snd():
    """풍금 소리 8음 (도~도) mp3. [(이름, 경로, 길이)]"""
    import numpy as np
    out = []
    SR = 22050
    for k, midi in enumerate((60, 62, 64, 65, 67, 69, 71, 72)):
        p = os.path.join(ensure_out(), 's32_organ_%d.mp3' % (k + 1))
        dur = 0.5
        if not os.path.exists(p):
            import lameenc
            t = np.arange(int(SR * dur)) / SR
            f0 = 440 * 2 ** ((midi - 69) / 12)
            x = sum(a * np.sin(2 * np.pi * f0 * h * t) for h, a in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15), (5, 0.08)))
            env = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.12)
            x = x * env
            x = x / np.max(np.abs(x)) * 0.7
            enc = lameenc.Encoder()
            enc.set_bit_rate(64)
            enc.set_in_sample_rate(SR)
            enc.set_channels(1)
            enc.set_quality(2)
            data = enc.encode((x * 32767).astype(np.int16).tobytes()) + enc.flush()
            open(p, 'wb').write(data)
        out.append(('s32_음%d' % (k + 1), p, dur))
    return out
