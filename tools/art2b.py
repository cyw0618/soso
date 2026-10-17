# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 11~20번 그림 (mg_art3.art 사용: 무대 px 로 크기, 2배 해상도 저장)."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3

art = A3.art


def _blur_layer(im, draw_fn, radius):
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(radius)))


def _txt(d, xy, s, size, fill, fname='jalnan', anchor='mm', stroke=0, sfill=(0, 0, 0)):
    d.text(xy, s, font=font(fname, int(size)), fill=fill, anchor=anchor, stroke_width=int(stroke), stroke_fill=sfill)


# ================================================================== 11. 음악분수
F11_W, F11_H, F11_B, F11_STEP = 44, 176, 18, 28      # 기둥 그림 크기, 0단 높이, 한 단 높이


def s11_column(level):
    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        top = H - (F11_B + level * F11_STEP) * s
        rng = random.Random(11 + level)
        # 물보라 빛
        _blur_layer(im, lambda g: g.rounded_rectangle((cx - 9 * s, top, cx + 9 * s, H), 9 * s,
                                                      fill=(120, 200, 255, 120)), 5 * s)
        if level > 0:
            # 기둥 (가장자리 하늘색, 가운데 흰색)
            for k in range(7, 0, -1):
                w = (2.2 + k) * s * (0.85 + 0.15 * min(level, 3) / 3)
                a = int(40 + 26 * (7 - k))
                col = (min(255, 150 + 15 * (7 - k)), min(255, 210 + 7 * (7 - k)), 255, a)
                d.rounded_rectangle((cx - w, top + 6 * s, cx + w, H - 2 * s), w, fill=col)
            # 물방울 왕관
            for k in range(26):
                ang = rng.uniform(-80, 80)
                r = rng.uniform(4, 14) * s
                x = cx + math.sin(math.radians(ang)) * r * 1.3
                y = top + 8 * s - math.cos(math.radians(ang)) * r * 0.8 + rng.uniform(-2, 6) * s
                rr = rng.uniform(0.8, 2.0) * s
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(235, 248, 255, rng.randint(150, 255)))
            # 옆으로 떨어지는 물방울
            for k in range(14):
                side = -1 if k % 2 else 1
                fy = rng.uniform(0.15, 0.9)
                y = top + 10 * s + fy * (H - top - 14 * s)
                x = cx + side * (6 + 10 * fy + rng.uniform(-2, 3)) * s
                rr = rng.uniform(0.7, 1.5) * s
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(210, 236, 255, rng.randint(110, 220)))
            d.ellipse((cx - 5 * s, top + 2 * s, cx + 5 * s, top + 10 * s), fill=(255, 255, 255, 230))
        # 바닥 물거품
        for k in range(10):
            x = cx + rng.uniform(-12, 12) * s
            y = H - rng.uniform(2, 7) * s
            rr = rng.uniform(1.5, 3.5) * s
            d.ellipse((x - rr, y - rr * 0.6, x + rr, y + rr * 0.6), fill=(225, 244, 255, 200))
    return art('s11_col%d' % level, F11_W, F11_H, f)


def s11_ghost(level):
    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        top = H - (F11_B + level * F11_STEP) * s
        box = (cx - 13 * s, top, cx + 13 * s, H - 1 * s)
        d.rounded_rectangle(box, 10 * s, fill=(255, 214, 110, 46))
        # 점선 테두리
        x0, y0, x1, y1 = box
        n = int((y1 - y0) / (5 * s))
        for k in range(0, n, 2):
            ya, yb = y0 + 10 * s + k * 5 * s, y0 + 10 * s + (k + 1) * 5 * s
            if yb > y1:
                break
            d.line([(x0, ya), (x0, yb)], fill=(255, 220, 120, 235), width=int(1.6 * s))
            d.line([(x1, ya), (x1, yb)], fill=(255, 220, 120, 235), width=int(1.6 * s))
        d.arc((x0, y0, x1, y0 + 20 * s), 180, 360, fill=(255, 220, 120, 235), width=int(1.6 * s))
        # 목표 높이 표시 막대
        d.rounded_rectangle((cx - 19 * s, top - 2 * s, cx + 19 * s, top + 2 * s), 2 * s, fill=(255, 226, 130, 255))
    return art('s11_ghost%d' % level, F11_W, F11_H, f)


def s11_basin(w=340, h=34):
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((2 * s, 8 * s, W - 2 * s, H - 2 * s), 8 * s, fill=(70, 78, 110, 255), outline=(150, 160, 200, 255),
                            width=int(1.5 * s))
        d.rounded_rectangle((6 * s, 4 * s, W - 6 * s, 14 * s), 5 * s, fill=(60, 140, 220, 255), outline=(170, 220, 255, 255),
                            width=int(1 * s))
        for k in range(14):
            x = (14 + k * 23) * s
            d.arc((x, 6 * s, x + 14 * s, 12 * s), 200, 340, fill=(220, 240, 255, 160), width=int(0.8 * s))
        for k in range(5):
            x = W / 2 + (k - 2) * 66 * s
            d.ellipse((x - 8 * s, 6 * s, x + 8 * s, 12 * s), fill=(40, 60, 100, 255), outline=(200, 220, 255, 255), width=int(s))
            d.rounded_rectangle((x - 8 * s, 18 * s, x + 8 * s, 30 * s), 3 * s, fill=(40, 46, 74, 255))
            _txt(d, (x, 24.5 * s), str(k + 1), 9 * s, (200, 214, 255, 255))
    return art('s11_basin', w, h, f)


def s11_sel():
    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        _blur_layer(im, lambda g: g.ellipse((cx - 20 * s, 2 * s, cx + 20 * s, 14 * s), outline=(120, 170, 255, 255),
                                            width=int(3 * s)), 2 * s)
        d.ellipse((cx - 18 * s, 3 * s, cx + 18 * s, 13 * s), outline=(170, 205, 255, 255), width=int(1.6 * s))
        d.polygon([(cx, H - 13 * s), (cx - 9 * s, H - 2 * s), (cx + 9 * s, H - 2 * s)], fill=(110, 150, 255, 255),
                  outline=(230, 240, 255, 255))
    return art('s11_sel', 50, 46, f)


def check_badge(name, r=8, col=(40, 190, 110)):
    def f(d, im, s):
        W = im.width
        d.ellipse((s, s, W - s, W - s), fill=col + (255,), outline=(255, 255, 255, 255), width=int(1.2 * s))
        d.line([(W * 0.28, W * 0.52), (W * 0.44, W * 0.68), (W * 0.74, W * 0.34)], fill=(255, 255, 255, 255),
               width=int(2 * s), joint='curve')
    return art(name, r * 2, r * 2, f)


# ================================================================== 12. 개구리 연잎 점프
def s12_pad(kind):
    """옆에서 본 연잎: normal / small / final(연꽃)."""
    w = {'normal': 66, 'small': 42, 'final': 84}[kind]
    h = 40 if kind == 'final' else 16

    def f(d, im, s):
        W, H = im.size
        y0 = H - 14 * s
        d.ellipse((2 * s, y0, W - 2 * s, H - 2 * s), fill=(28, 92, 50, 255), outline=(14, 50, 28, 255), width=int(1.2 * s))
        d.ellipse((4 * s, y0 - 1 * s, W - 4 * s, H - 5 * s), fill=(62, 160, 80, 255))
        d.ellipse((10 * s, y0 + 1 * s, W * 0.55, H - 8 * s), fill=(110, 200, 110, 140))
        # 잎맥
        cx, cy = W / 2, (y0 + H - 5 * s) / 2
        for a in range(-60, 61, 30):
            d.line([(cx, cy), (cx + math.sin(math.radians(a)) * (W / 2 - 6 * s), cy - 2 * s)], fill=(40, 120, 60, 200),
                   width=int(0.7 * s))
        # 갈라진 틈
        d.polygon([(cx, cy), (cx + 6 * s, y0 - 1 * s), (cx + 12 * s, y0)], fill=(0, 0, 0, 0))
        if kind == 'final':
            fx = W * 0.62
            fy = y0 - 4 * s
            for a, col in ((-50, (255, 170, 200)), (50, (255, 170, 200)), (-22, (255, 140, 185)), (22, (255, 140, 185)),
                           (0, (255, 120, 170))):
                pts = []
                for t in range(0, 181, 15):
                    r = 13 * s * math.sin(math.radians(t))
                    ang = math.radians(a) + (t - 90) / 90 * 0.32
                    pts.append((fx + math.sin(ang) * r * 1.0, fy - math.cos(ang) * r * 1.6 * (t / 180 + 0.3)))
                d.polygon(pts, fill=col + (255,), outline=(200, 70, 120, 255))
            d.ellipse((fx - 4 * s, fy - 6 * s, fx + 4 * s, fy - 1 * s), fill=(255, 220, 90, 255))
            # 깃발
            px = W * 0.22
            d.line([(px, y0 + 2 * s), (px, 3 * s)], fill=(230, 230, 240, 255), width=int(1.4 * s))
            d.polygon([(px, 3 * s), (px + 18 * s, 8 * s), (px, 13 * s)], fill=(70, 110, 255, 255), outline=(255, 255, 255, 255))
    return art('s12_pad_%s' % kind, w, h, f)


def s12_frog(pose):
    def f(d, im, s):
        W, H = im.size
        G1, G2, DK = (88, 190, 70, 255), (150, 225, 110, 255), (30, 80, 30, 255)
        if pose == 'sit':
            d.ellipse((4 * s, 14 * s, 18 * s, 27 * s), fill=G1, outline=DK, width=int(s))        # 뒷다리
            d.ellipse((6 * s, 6 * s, 28 * s, 25 * s), fill=G1, outline=DK, width=int(s))         # 몸
            d.ellipse((12 * s, 13 * s, 26 * s, 24 * s), fill=G2)                                # 배
            d.ellipse((20 * s, 20 * s, 30 * s, 27 * s), fill=G1, outline=DK, width=int(s))       # 앞발
            ex, ey = 22 * s, 6 * s
        else:
            d.polygon([(2 * s, 22 * s), (12 * s, 14 * s), (16 * s, 18 * s), (6 * s, 27 * s)], fill=G1, outline=DK)
            d.ellipse((8 * s, 6 * s, 32 * s, 22 * s), fill=G1, outline=DK, width=int(s))
            d.ellipse((14 * s, 12 * s, 30 * s, 21 * s), fill=G2)
            d.polygon([(28 * s, 16 * s), (36 * s, 20 * s), (34 * s, 23 * s), (27 * s, 20 * s)], fill=G1, outline=DK)
            ex, ey = 26 * s, 5 * s
        d.ellipse((ex - 5 * s, ey - 4 * s, ex + 5 * s, ey + 5 * s), fill=G1, outline=DK, width=int(s))
        d.ellipse((ex - 3 * s, ey - 2.5 * s, ex + 3.5 * s, ey + 3.5 * s), fill=(255, 255, 255, 255))
        d.ellipse((ex - 0.5 * s, ey - 1 * s, ex + 2.5 * s, ey + 2.5 * s), fill=(10, 10, 20, 255))
        d.arc((ex - 4 * s, ey + 4 * s, ex + 7 * s, ey + 11 * s), 10, 90, fill=DK, width=int(s))
        d.ellipse((ex - 9 * s, ey + 6 * s, ex - 5 * s, ey + 9 * s), fill=(255, 140, 150, 160))
    return art('s12_frog_%s' % pose, 38, 30, f)


def s12_splash():
    def f(d, im, s):
        W, H = im.size
        rng = random.Random(12)
        d.ellipse((4 * s, H - 10 * s, W - 4 * s, H - 2 * s), outline=(220, 240, 255, 220), width=int(1.5 * s))
        for k in range(9):
            a = -70 + k * 17.5
            x = W / 2 + math.sin(math.radians(a)) * 6 * s
            h = (14 + rng.uniform(0, 12)) * s
            d.line([(x, H - 6 * s), (x + math.sin(math.radians(a)) * 10 * s, H - 6 * s - h)], fill=(200, 230, 255, 230),
                   width=int(2.4 * s))
            d.ellipse((x + math.sin(math.radians(a)) * 11 * s - 2 * s, H - 8 * s - h - 2 * s,
                       x + math.sin(math.radians(a)) * 11 * s + 2 * s, H - 8 * s - h + 2 * s), fill=(235, 248, 255, 255))
    return art('s12_splash', 46, 36, f)


def s12_marker():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(2 * s, 2 * s), (W - 2 * s, 2 * s), (W / 2, H - 2 * s)], fill=(255, 214, 90, 255), outline=(60, 40, 0, 255))
    return art('s12_marker', 14, 12, f)


def s12_wave(w=240):
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 7 * s, W, H), fill=(40, 70, 150, 120))
        for k in range(0, int(w / 16) + 1):
            x = k * 16 * s
            d.arc((x, 3 * s, x + 16 * s, 11 * s), 200, 340, fill=(190, 220, 255, 200), width=int(1.3 * s))
    return art('s12_wave', w, 16, f)


# ================================================================== 13. 청사 엘리베이터
E13_FLOORS = [-104, -62, -20, 22, 64]      # 층 바닥 y (무대)


def s13_building(w=300, h=206, cx=-15, cy=-8):
    """건물 단면 (무대 좌표 cx, cy 에 놓임)."""
    def f(d, im, s):
        W, H = im.size
        X = lambda x: (x - (cx - w / 2)) * s
        Y = lambda y: ((cy + h / 2) - y) * s
        d.rounded_rectangle((X(-160), Y(98), X(136), Y(-108)), 8 * s, fill=(18, 24, 52, 225), outline=(90, 110, 180, 255),
                            width=int(1.5 * s))
        # 지붕 (청사 물결 지붕 느낌)
        pts = [(X(-160 + k * 4), Y(98 + 4 * math.sin(k / 74 * math.pi * 2))) for k in range(75)]
        d.line(pts, fill=(140, 170, 255, 255), width=int(2 * s))
        for i, fy in enumerate(E13_FLOORS):
            d.rectangle((X(-156), Y(fy), X(132), Y(fy - 4)), fill=(70, 84, 130, 255))
            d.line([(X(-156), Y(fy)), (X(132), Y(fy))], fill=(150, 170, 230, 255), width=int(1 * s))
            # 창문 (뒤 벽)
            for k in range(5):
                x0 = -146 + k * 22
                d.rounded_rectangle((X(x0), Y(fy + 34), X(x0 + 14), Y(fy + 14)), 2 * s, fill=(40, 60, 110, 255))
            for k in range(3):
                x0 = 58 + k * 24
                d.rounded_rectangle((X(x0), Y(fy + 34), X(x0 + 14), Y(fy + 14)), 2 * s, fill=(40, 60, 110, 255))
            _txt(d, (X(-146 + 2), Y(fy + 8)), '%dF' % (i + 1), 7 * s, (170, 190, 240, 255), anchor='lm')
        # 승강로
        d.rectangle((X(-12), Y(98), X(32), Y(-108)), fill=(8, 10, 24, 255))
        d.line([(X(-12), Y(98)), (X(-12), Y(-108))], fill=(110, 130, 200, 255), width=int(1.4 * s))
        d.line([(X(32), Y(98)), (X(32), Y(-108))], fill=(110, 130, 200, 255), width=int(1.4 * s))
        for x in (-2, 22):
            d.line([(X(x), Y(98)), (X(x), Y(-108))], fill=(50, 60, 100, 255), width=int(0.8 * s))
    return art('s13_building', w, h, f)


def s13_car(state):
    def f(d, im, s):
        W, H = im.size
        d.rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), fill=(150, 160, 190, 255), outline=(230, 236, 255, 255),
                    width=int(1.4 * s))
        d.rectangle((3 * s, 3 * s, W - 3 * s, H - 3 * s), fill=(250, 236, 190, 255))
        if state == 'closed':
            for x0, x1 in ((3, W / s / 2 - 0.5), (W / s / 2 + 0.5, W / s - 3)):
                d.rectangle((x0 * s, 3 * s, x1 * s, H - 3 * s), fill=(120, 140, 190, 150), outline=(70, 80, 120, 255))
        else:
            d.rectangle((3 * s, 3 * s, 6 * s, H - 3 * s), fill=(120, 140, 190, 255))
            d.rectangle((W - 6 * s, 3 * s, W - 3 * s, H - 3 * s), fill=(120, 140, 190, 255))
        d.ellipse((W / 2 - 2 * s, 4 * s, W / 2 + 2 * s, 8 * s), fill=(255, 250, 220, 255))
    return art('s13_car_%s' % state, 42, 38, f)


def s13_person(dest, angry=False, var=0):
    suits = [(40, 60, 120), (60, 64, 80), (90, 50, 80), (40, 90, 90), (90, 80, 50)]

    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        bc = (220, 60, 70) if angry else (60, 100, 230)
        d.rounded_rectangle((cx - 7 * s, 0.5 * s, cx + 7 * s, 12 * s), 4 * s, fill=bc + (255,), outline=(255, 255, 255, 255),
                            width=int(0.9 * s))
        d.polygon([(cx - 2 * s, 12 * s), (cx + 2 * s, 12 * s), (cx, 14.5 * s)], fill=(255, 255, 255, 255))
        _txt(d, (cx, 6.4 * s), str(dest), 8.5 * s, (255, 255, 255, 255))
        sc = suits[(dest + var) % 5]
        skin = (255, 150, 140) if angry else (250, 214, 180)
        d.rounded_rectangle((cx - 6.5 * s, 26 * s, cx + 6.5 * s, 39 * s), 3 * s, fill=sc + (255,))
        d.polygon([(cx - 2 * s, 26 * s), (cx + 2 * s, 26 * s), (cx, 31 * s)], fill=(255, 255, 255, 255))
        d.line([(cx, 27 * s), (cx, 32 * s)], fill=(200, 40, 50, 255), width=int(1.2 * s))
        d.ellipse((cx - 5.5 * s, 15 * s, cx + 5.5 * s, 26.5 * s), fill=skin + (255,), outline=(90, 60, 50, 255), width=int(0.6 * s))
        d.chord((cx - 5.8 * s, 14.5 * s, cx + 5.8 * s, 23 * s), 180, 360, fill=(40, 30, 30, 255))
        if angry:
            d.line([(cx - 4 * s, 19 * s), (cx - 1 * s, 20.5 * s)], fill=(60, 0, 0, 255), width=int(0.9 * s))
            d.line([(cx + 4 * s, 19 * s), (cx + 1 * s, 20.5 * s)], fill=(60, 0, 0, 255), width=int(0.9 * s))
            d.arc((cx - 2.5 * s, 23 * s, cx + 2.5 * s, 26 * s), 200, 340, fill=(60, 0, 0, 255), width=int(0.8 * s))
        else:
            d.arc((cx - 2.5 * s, 21 * s, cx + 2.5 * s, 24.5 * s), 20, 160, fill=(90, 40, 30, 255), width=int(0.8 * s))
        d.ellipse((cx - 3 * s, 20 * s, cx - 1.6 * s, 21.4 * s), fill=(20, 20, 20, 255))
        d.ellipse((cx + 1.6 * s, 20 * s, cx + 3 * s, 21.4 * s), fill=(20, 20, 20, 255))
    return art('s13_p%d%s' % (dest, 'a' if angry else ''), 18, 40, f)


def s13_button(n, state):
    """state: off / ride(안에서 누름) / go(가는 중)."""
    def f(d, im, s):
        W = im.width
        rim = {'off': (120, 130, 170), 'ride': (255, 200, 90), 'go': (120, 170, 255)}[state]
        fill = {'off': (30, 36, 64), 'ride': (110, 70, 10), 'go': (30, 60, 160)}[state]
        if state != 'off':
            _blur_layer(im, lambda g: g.ellipse((2 * s, 2 * s, W - 2 * s, W - 2 * s), fill=rim + (200,)), 3 * s)
        d.ellipse((4 * s, 4 * s, W - 4 * s, W - 4 * s), fill=fill + (255,), outline=rim + (255,), width=int(1.8 * s))
        _txt(d, (W / 2, W / 2 + 0.5 * s), str(n), 12 * s, (255, 255, 255, 255) if state != 'off' else (200, 210, 240, 255))
    return art('s13_btn%d_%s' % (n, state), 30, 30, f)


def s13_lamp(on):
    def f(d, im, s):
        W, H = im.size
        col = (255, 200, 80, 255) if on else (60, 66, 96, 255)
        d.polygon([(W / 2, 1 * s), (W - 1 * s, H - 1 * s), (1 * s, H - 1 * s)], fill=col, outline=(20, 20, 30, 255))
    return art('s13_lamp%d' % on, 10, 8, f)
