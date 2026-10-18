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


# ================================================================== 14. 오케스트라 지휘
def s14_player(kind, frame):
    """연주자 (kind: violin cello flute trumpet drum), frame 0/1."""
    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        d.rounded_rectangle((cx - 9 * s, 22 * s, cx + 9 * s, 48 * s), 5 * s, fill=(20, 20, 30, 255), outline=(70, 80, 120, 255))
        d.polygon([(cx - 3 * s, 22 * s), (cx + 3 * s, 22 * s), (cx, 28 * s)], fill=(240, 240, 250, 255))
        d.ellipse((cx - 7 * s, 8 * s, cx + 7 * s, 23 * s), fill=(250, 214, 180, 255), outline=(90, 60, 50, 255), width=int(0.7 * s))
        d.chord((cx - 7.3 * s, 7.5 * s, cx + 7.3 * s, 18 * s), 180, 360, fill=(50, 36, 30, 255))
        d.ellipse((cx - 3.5 * s, 15 * s, cx - 1.8 * s, 16.8 * s), fill=(20, 20, 20, 255))
        d.ellipse((cx + 1.8 * s, 15 * s, cx + 3.5 * s, 16.8 * s), fill=(20, 20, 20, 255))
        wood, brass = (170, 90, 40, 255), (240, 200, 80, 255)
        a = 1 if frame else -1
        if kind == 'violin':
            d.ellipse((cx + 2 * s, 20 * s, cx + 14 * s, 30 * s), fill=wood, outline=(90, 40, 10, 255))
            d.line([(cx - 8 * s, 26 * s + a * 3 * s), (cx + 18 * s, 18 * s - a * 3 * s)], fill=(230, 220, 200, 255), width=int(1 * s))
        elif kind == 'cello':
            d.ellipse((cx - 8 * s, 28 * s, cx + 8 * s, 50 * s), fill=wood, outline=(90, 40, 10, 255))
            d.line([(cx, 16 * s), (cx, 30 * s)], fill=(60, 30, 10, 255), width=int(2 * s))
            d.line([(cx - 14 * s, 36 * s + a * 3 * s), (cx + 12 * s, 40 * s - a * 3 * s)], fill=(230, 220, 200, 255), width=int(1.2 * s))
        elif kind == 'flute':
            d.line([(cx - 2 * s, 20 * s), (cx + 18 * s, 22 * s + a * 2 * s)], fill=(220, 225, 235, 255), width=int(1.8 * s))
        elif kind == 'trumpet':
            d.line([(cx + 2 * s, 20 * s), (cx + 14 * s, 18 * s + a * 2 * s)], fill=brass, width=int(2.2 * s))
            d.polygon([(cx + 14 * s, 14 * s + a * 2 * s), (cx + 19 * s, 12 * s + a * 2 * s), (cx + 19 * s, 25 * s + a * 2 * s),
                       (cx + 14 * s, 22 * s + a * 2 * s)], fill=brass)
        else:
            d.ellipse((cx - 13 * s, 34 * s, cx + 13 * s, 44 * s), fill=(200, 60, 60, 255), outline=(255, 230, 200, 255))
            d.rectangle((cx - 13 * s, 39 * s, cx + 13 * s, 48 * s), fill=(200, 60, 60, 255))
            d.ellipse((cx - 13 * s, 34 * s, cx + 13 * s, 42 * s), fill=(240, 236, 220, 255), outline=(150, 140, 120, 255))
            d.line([(cx - 10 * s, 26 * s), (cx - 4 * s, 36 * s - a * 4 * s)], fill=(230, 220, 200, 255), width=int(1.4 * s))
            d.line([(cx + 10 * s, 26 * s), (cx + 4 * s, 36 * s + a * 4 * s)], fill=(230, 220, 200, 255), width=int(1.4 * s))
    return art('s14_%s%d' % (kind, frame), 40, 50, f)


def s14_card(tempo, dyn, w=150, h=44):
    cols = {'빠르게': (200, 70, 90), '보통': (70, 110, 220), '느리게': (60, 160, 120)}

    def f(d, im, s):
        W, H = im.size
        c = cols[tempo]
        d.rounded_rectangle((s, s, W - s, H - s), 8 * s, fill=(250, 246, 232, 255), outline=c + (255,), width=int(2.4 * s))
        for k in range(5):
            y = (10 + k * 6) * s
            d.line([(6 * s, y), (W - 6 * s, y)], fill=(200, 196, 180, 255), width=int(0.6 * s))
        _txt(d, (W * 0.38, H / 2), tempo, 17 * s, c + (255,), stroke=1.2 * s, sfill=(255, 255, 255, 255))
        _txt(d, (W * 0.83, H / 2 + 1 * s), dyn, 24 * s, (40, 30, 60, 255), fname='black')
    return art('s14_card_%s_%s' % (tempo, dyn), w, h, f)


def s14_baton():
    def f(d, im, s):
        W, H = im.size
        d.line([(3 * s, H - 3 * s), (W - 3 * s, 3 * s)], fill=(255, 255, 255, 255), width=int(2 * s))
        d.ellipse((1 * s, H - 8 * s, 8 * s, H - 1 * s), fill=(120, 70, 30, 255))
    return art('s14_baton', 26, 26, f)


def s14_band(label, up):
    def f(d, im, s):
        W, H = im.size
        _txt(d, (W / 2, H / 2), label, 9 * s, (255, 220, 140, 255) if up else (160, 200, 255, 255), stroke=1.4 * s,
             sfill=(0, 0, 20, 255))
    return art('s14_bandb%d' % up, 84, 20, f)


# ================================================================== 15. 금강 카누
def s15_canoe(pose):
    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        d.ellipse((cx - 8 * s, 2 * s, cx + 8 * s, H - 2 * s), fill=(210, 80, 50, 255), outline=(90, 30, 20, 255), width=int(1.2 * s))
        d.ellipse((cx - 5 * s, 8 * s, cx + 5 * s, H - 8 * s), fill=(120, 60, 40, 255))
        d.ellipse((cx - 6 * s, H / 2 - 6 * s, cx + 6 * s, H / 2 + 6 * s), fill=(250, 214, 180, 255), outline=(60, 40, 30, 255))
        d.ellipse((cx - 4 * s, H / 2 - 4 * s, cx + 4 * s, H / 2 + 2 * s), fill=(40, 30, 30, 255))
        if pose == 'c':
            d.line([(cx - 16 * s, H / 2 + 2 * s), (cx + 16 * s, H / 2 + 2 * s)], fill=(240, 220, 150, 255), width=int(1.6 * s))
        else:
            sgn = -1 if pose == 'l' else 1
            d.line([(cx, H / 2), (cx + sgn * 13 * s, H / 2 + 12 * s)], fill=(240, 220, 150, 255), width=int(1.6 * s))
            d.ellipse((cx + sgn * 13 * s - 3 * s, H / 2 + 10 * s, cx + sgn * 13 * s + 3 * s, H / 2 + 18 * s), fill=(240, 220, 150, 255))
            for k in range(5):
                a = k * 72
                x = cx + sgn * 14 * s + math.cos(math.radians(a)) * 5 * s
                y = H / 2 + 16 * s + math.sin(math.radians(a)) * 4 * s
                d.ellipse((x - 1.5 * s, y - 1.5 * s, x + 1.5 * s, y + 1.5 * s), fill=(230, 245, 255, 230))
    return art('s15_canoe_%s' % pose, 40, 54, f)


def s15_buoy(state):
    col = {'red': (230, 60, 60), 'green': (60, 200, 110), 'gray': (110, 110, 130)}[state]

    def f(d, im, s):
        W = im.width
        d.ellipse((1 * s, 1 * s, W - 1 * s, W - 1 * s), fill=(220, 240, 255, 90))
        d.ellipse((3 * s, 3 * s, W - 3 * s, W - 3 * s), fill=col + (255,), outline=(255, 255, 255, 255), width=int(1.2 * s))
        d.ellipse((W * 0.35, W * 0.35, W * 0.65, W * 0.65), fill=(255, 255, 255, 230))
    return art('s15_buoy_%s' % state, 16, 16, f)


def s15_bank():
    def f(d, im, s):
        W, H = im.size
        rng = random.Random(15)
        d.rectangle((0, 0, W * 0.62, H), fill=(54, 96, 60, 255))
        for y0 in range(0, int(H / s), 80):
            for k in range(7):
                yy = (y0 + rng.uniform(0, 80)) * s
                x = rng.uniform(4, 22) * s
                d.ellipse((x, yy, x + rng.uniform(6, 12) * s, yy + rng.uniform(4, 8) * s), fill=(80, 140, 70, 255))
            for k in range(3):
                yy = (y0 + k * 26 + 6) * s
                d.ellipse((W * 0.5, yy, W * 0.8, yy + 10 * s), fill=(120, 120, 130, 255), outline=(70, 70, 80, 255))
        d.line([(W * 0.62, 0), (W * 0.62, H)], fill=(200, 230, 255, 160), width=int(1.5 * s))
    return art('s15_bank', 40, 360, f)


def s15_finish(w=340):
    def f(d, im, s):
        W, H = im.size
        n = 34
        for k in range(n):
            for r in range(2):
                col = (255, 255, 255, 230) if (k + r) % 2 else (20, 20, 30, 230)
                d.rectangle((k * W / n, r * H / 2, (k + 1) * W / n, (r + 1) * H / 2), fill=col)
    return art('s15_finish', w, 10, f)


def s15_arrow():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(2 * s, H * 0.35), (W * 0.65, H * 0.35), (W * 0.65, 2 * s), (W - 2 * s, H / 2), (W * 0.65, H - 2 * s),
                   (W * 0.65, H * 0.65), (2 * s, H * 0.65)], fill=(200, 230, 255, 110))
    return art('s15_arrow', 40, 20, f)


def s15_ripple():
    def f(d, im, s):
        W, H = im.size
        d.arc((2 * s, 2 * s, W - 2 * s, H * 2), 200, 340, fill=(190, 225, 255, 150), width=int(1.2 * s))
    return art('s15_ripple', 22, 8, f)


# ================================================================== 16. 망원경 찾기
def s16_scope(R=70):
    def f(d, im, s):
        W, H = im.size
        cx, cy = W / 2, H / 2
        d.rectangle((0, 0, W, H), fill=(4, 6, 16, 250))
        d.ellipse((cx - R * s, cy - R * s, cx + R * s, cy + R * s), fill=(0, 0, 0, 0))
        d.ellipse((cx - (R + 6) * s, cy - (R + 6) * s, cx + (R + 6) * s, cy + (R + 6) * s), outline=(40, 46, 70, 255), width=int(7 * s))
        d.ellipse((cx - (R + 1) * s, cy - (R + 1) * s, cx + (R + 1) * s, cy + (R + 1) * s), outline=(140, 160, 220, 255), width=int(1.5 * s))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d.line([(cx + dx * 10 * s, cy + dy * 10 * s), (cx + dx * 30 * s, cy + dy * 30 * s)], fill=(255, 80, 80, 200), width=int(1 * s))
        d.ellipse((cx - 2 * s, cy - 2 * s, cx + 2 * s, cy + 2 * s), outline=(255, 80, 80, 220), width=int(0.8 * s))
    return art('s16_scope', 960, 540, f)


def s16_thing(kind):
    """kind: rb/bb/gb(풍선) flag/bflag bike walk bird kite ykite"""
    sz = {'flag': (22, 26), 'bflag': (22, 26), 'bike': (30, 30), 'walk': (16, 30), 'bird': (26, 16), 'kite': (24, 36),
          'ykite': (24, 36)}.get(kind, (18, 32))

    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        if kind in ('rb', 'bb', 'gb'):
            c = {'rb': (235, 50, 60), 'bb': (60, 110, 240), 'gb': (60, 190, 100)}[kind]
            d.line([(cx, 18 * s), (cx + 2 * s, H - 1 * s)], fill=(230, 230, 230, 255), width=int(0.8 * s))
            d.ellipse((cx - 8 * s, 1 * s, cx + 8 * s, 19 * s), fill=c + (255,), outline=(255, 255, 255, 200), width=int(0.8 * s))
            d.ellipse((cx - 5 * s, 4 * s, cx - 1 * s, 9 * s), fill=(255, 255, 255, 150))
        elif kind in ('flag', 'bflag'):
            d.line([(3 * s, 2 * s), (3 * s, H - 1 * s)], fill=(220, 220, 230, 255), width=int(1.3 * s))
            d.rectangle((4 * s, 2 * s, W - 1 * s, 15 * s), fill=(255, 255, 255, 255) if kind == 'flag' else (60, 90, 220, 255),
                        outline=(80, 80, 90, 255))
            if kind == 'flag':
                c = (4 * s + W) / 2
                d.pieslice((c - 4 * s, 4.5 * s, c + 4 * s, 12.5 * s), 180, 360, fill=(220, 40, 50, 255))
                d.pieslice((c - 4 * s, 4.5 * s, c + 4 * s, 12.5 * s), 0, 180, fill=(30, 60, 160, 255))
                for xx in (6.5, W / s - 3.5):
                    for yy in (4.5, 11):
                        d.line([(xx * s - 1.5 * s, yy * s), (xx * s + 1.5 * s, yy * s + 1.5 * s)], fill=(20, 20, 20, 255), width=int(0.8 * s))
        elif kind == 'bike':
            for x in (7, 23):
                d.ellipse(((x - 6) * s, 17 * s, (x + 6) * s, 29 * s), outline=(30, 30, 40, 255), width=int(1.4 * s))
            d.line([(7 * s, 23 * s), (14 * s, 15 * s), (23 * s, 23 * s), (15 * s, 23 * s), (7 * s, 23 * s)], fill=(220, 50, 50, 255),
                   width=int(1.3 * s))
            d.line([(14 * s, 15 * s), (16 * s, 9 * s)], fill=(60, 120, 220, 255), width=int(3 * s))
            d.ellipse((14 * s, 2 * s, 20 * s, 8 * s), fill=(250, 214, 180, 255))
            d.line([(17 * s, 11 * s), (22 * s, 14 * s)], fill=(60, 120, 220, 255), width=int(1.5 * s))
        elif kind == 'walk':
            d.ellipse((cx - 3.5 * s, 1 * s, cx + 3.5 * s, 8 * s), fill=(250, 214, 180, 255))
            d.rounded_rectangle((cx - 4 * s, 8 * s, cx + 4 * s, 20 * s), 2 * s, fill=(240, 160, 60, 255))
            d.line([(cx - 2 * s, 20 * s), (cx - 4 * s, 29 * s)], fill=(40, 40, 60, 255), width=int(1.5 * s))
            d.line([(cx + 2 * s, 20 * s), (cx + 4 * s, 29 * s)], fill=(40, 40, 60, 255), width=int(1.5 * s))
        elif kind == 'bird':
            d.polygon([(2 * s, 4 * s), (cx, 9 * s), (W - 2 * s, 4 * s), (cx, 12 * s)], fill=(30, 30, 40, 255))
            d.ellipse((cx - 3 * s, 7 * s, cx + 5 * s, 13 * s), fill=(240, 240, 250, 255), outline=(30, 30, 40, 255))
        else:
            c1 = (230, 50, 60) if kind == 'kite' else (240, 200, 60)
            d.rectangle((3 * s, 2 * s, W - 3 * s, 24 * s), fill=c1 + (255,), outline=(60, 40, 30, 255), width=int(0.8 * s))
            d.ellipse((cx - 4 * s, 9 * s, cx + 4 * s, 17 * s), fill=(255, 255, 255, 255))
            if kind == 'kite':
                d.rectangle((3 * s, 2 * s, W - 3 * s, 7 * s), fill=(40, 60, 170, 255))
            d.line([(cx, 24 * s), (cx - 4 * s, 30 * s), (cx + 3 * s, H - 1 * s)], fill=(240, 240, 240, 255), width=int(0.8 * s))
    return art('s16_%s' % kind, sz[0], sz[1], f)


# ================================================================== 17. 다리 조명 기억
def s17_cell(state):
    def f(d, im, s):
        W = im.width
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, W - 1 * s), 6 * s, fill=(16, 22, 48, 255), outline=(70, 90, 160, 255),
                            width=int(1 * s))
        if state == 'off':
            d.ellipse((W * 0.3, W * 0.3, W * 0.7, W * 0.7), fill=(40, 48, 80, 255), outline=(90, 100, 150, 255))
        else:
            col = {'on': (255, 236, 150), 'ok': (110, 230, 255), 'bad': (255, 80, 90), 'miss': (255, 180, 80)}[state]
            _blur_layer(im, lambda g: g.ellipse((W * 0.12, W * 0.12, W * 0.88, W * 0.88), fill=col + (200,)), 3 * s)
            d.ellipse((W * 0.26, W * 0.26, W * 0.74, W * 0.74), fill=col + (255,), outline=(255, 255, 255, 255), width=int(1 * s))
            if state == 'bad':
                d.line([(W * 0.36, W * 0.36), (W * 0.64, W * 0.64)], fill=(80, 0, 10, 255), width=int(2 * s))
                d.line([(W * 0.64, W * 0.36), (W * 0.36, W * 0.64)], fill=(80, 0, 10, 255), width=int(2 * s))
    return art('s17_%s' % state, 34, 34, f)


# ================================================================== 18. 윷놀이
def s18_board(nodes, size=200):
    """nodes: [(x, y, big)] 판 중심 기준 무대 좌표."""
    def f(d, im, s):
        W, H = im.size
        c = W / 2
        d.rounded_rectangle((2 * s, 2 * s, W - 2 * s, H - 2 * s), 12 * s, fill=(236, 214, 170, 255), outline=(120, 80, 40, 255),
                            width=int(3 * s))
        P_ = lambda x, y: (c + x * s, c - y * s)
        h = size / 2 - 18
        for a, b in (((h, -h), (h, h)), ((h, h), (-h, h)), ((-h, h), (-h, -h)), ((-h, -h), (h, -h)), ((h, h), (-h, -h)),
                     ((-h, h), (h, -h))):
            d.line([P_(*a), P_(*b)], fill=(140, 100, 60, 255), width=int(2 * s))
        for x, y, big in nodes:
            r = (9 if big else 6) * s
            px, py = P_(x, y)
            d.ellipse((px - r, py - r, px + r, py + r), fill=(250, 240, 220, 255), outline=(110, 70, 30, 255), width=int(1.5 * s))
        px, py = P_(h, -h)
        _txt(d, (px - 2 * s, py + 15 * s), '출발·도착', 7 * s, (120, 60, 20, 255), fname='nsr')
    return art('s18_board', size, size, f)


def s18_piece(who, n):
    def f(d, im, s):
        W = im.width
        col = (50, 100, 230) if who == 'me' else (220, 60, 60)
        d.ellipse((1 * s, 2 * s, W - 1 * s, W), fill=(0, 0, 0, 90))
        d.ellipse((1 * s, 1 * s, W - 1 * s, W - 2 * s), fill=col + (255,), outline=(255, 255, 255, 255), width=int(1.4 * s))
        _txt(d, (W / 2, W / 2 - 0.5 * s), ('나' if who == 'me' else '이') + str(n), 7 * s, (255, 255, 255, 255))
    return art('s18_%s%d' % (who, n), 20, 20, f)


def s18_stick(flat):
    def f(d, im, s):
        W, H = im.size
        if flat:
            d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 5 * s, fill=(250, 236, 200, 255), outline=(120, 80, 40, 255),
                                width=int(1.2 * s))
            for k in range(3):
                y = H * (0.3 + k * 0.2)
                d.line([(W * 0.3, y - 2 * s), (W * 0.7, y + 2 * s)], fill=(120, 80, 40, 255), width=int(1 * s))
                d.line([(W * 0.7, y - 2 * s), (W * 0.3, y + 2 * s)], fill=(120, 80, 40, 255), width=int(1 * s))
        else:
            d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 5 * s, fill=(190, 130, 70, 255), outline=(100, 60, 20, 255),
                                width=int(1.2 * s))
            d.line([(W * 0.35, 4 * s), (W * 0.35, H - 4 * s)], fill=(220, 170, 110, 255), width=int(1.5 * s))
    return art('s18_stick%d' % flat, 14, 56, f)


def s18_elder():
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((2 * s, 2 * s, W - 2 * s, W - 2 * s), fill=(60, 40, 40, 255), outline=(220, 90, 90, 255), width=int(2 * s))
        d.ellipse((c - 11 * s, c - 12 * s, c + 11 * s, c + 12 * s), fill=(245, 205, 170, 255))
        d.chord((c - 11 * s, c - 12 * s, c + 11 * s, c + 2 * s), 200, 340, fill=(230, 230, 235, 255))
        for sx in (-1, 1):
            d.line([(c + sx * 7 * s, c - 2 * s), (c + sx * 3 * s, c - 2 * s)], fill=(240, 240, 240, 255), width=int(2 * s))
            d.arc((c + sx * 5 * s - 2 * s, c, c + sx * 5 * s + 2 * s, c + 3 * s), 180, 360, fill=(40, 30, 30, 255), width=int(s))
        d.chord((c - 7 * s, c + 3 * s, c + 7 * s, c + 13 * s), 0, 180, fill=(240, 240, 240, 255))
        d.arc((c - 3 * s, c + 3 * s, c + 3 * s, c + 7 * s), 20, 160, fill=(120, 50, 40, 255), width=int(s))
    return art('s18_elder', 40, 40, f)


# ================================================================== 19. 굴렁쇠
def s19_hoop():
    def f(d, im, s):
        W, H = im.size
        d.ellipse((2 * s, 2 * s, W - 2 * s, H - 2 * s), outline=(150, 150, 165, 255), width=int(4 * s))
        d.ellipse((3 * s, 3 * s, W - 3 * s, H - 3 * s), outline=(230, 230, 245, 255), width=int(1.5 * s))
    return art('s19_hoop', 16, 70, f)


def s19_kid(frame):
    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        a = 3 if frame else -3
        d.line([(cx - 5 * s, 44 * s), (cx - 6 * s + a * s, 58 * s)], fill=(40, 50, 90, 255), width=int(4 * s))
        d.line([(cx + 5 * s, 44 * s), (cx + 6 * s - a * s, 58 * s)], fill=(40, 50, 90, 255), width=int(4 * s))
        d.rounded_rectangle((cx - 10 * s, 22 * s, cx + 10 * s, 46 * s), 5 * s, fill=(230, 80, 80, 255), outline=(120, 30, 30, 255))
        d.ellipse((cx - 8 * s, 6 * s, cx + 8 * s, 24 * s), fill=(40, 30, 30, 255))
        d.line([(cx + 8 * s, 26 * s), (cx + 4 * s, 2 * s)], fill=(250, 214, 180, 255), width=int(3 * s))
        d.line([(cx + 4 * s, 4 * s), (cx + 2 * s, -10 * s)], fill=(150, 100, 50, 255), width=int(2 * s))
    return art('s19_kid%d' % frame, 30, 60, f)


def s19_road(w=420, h=150):
    def f(d, im, s):
        W, H = im.size
        top, bot = 30, 200
        d.polygon([(W / 2 - top * s, 0), (W / 2 + top * s, 0), (W / 2 + bot * s, H), (W / 2 - bot * s, H)], fill=(196, 170, 130, 255))
        d.line([(W / 2 - top * s, 0), (W / 2 - bot * s, H)], fill=(120, 90, 60, 255), width=int(3 * s))
        d.line([(W / 2 + top * s, 0), (W / 2 + bot * s, H)], fill=(120, 90, 60, 255), width=int(3 * s))
        rng = random.Random(19)
        for k in range(160):
            y = rng.uniform(0, 1) ** 0.7
            x = W / 2 + rng.uniform(-1, 1) * (top + (bot - top) * y) * s * 0.95
            r = (0.4 + 1.2 * y) * s
            d.ellipse((x - r, y * H - r * 0.6, x + r, y * H + r * 0.6), fill=(160, 136, 100, 255))
    return art('s19_road', w, h, f)


def s19_stone():
    def f(d, im, s):
        W, H = im.size
        d.ellipse((1 * s, 3 * s, W - 1 * s, H - 1 * s), fill=(120, 116, 120, 255), outline=(60, 56, 60, 255), width=int(1.2 * s))
        d.ellipse((W * 0.25, 4 * s, W * 0.55, H * 0.5), fill=(180, 176, 180, 255))
    return art('s19_stone', 26, 16, f)


def s19_dash():
    def f(d, im, s):
        d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 2 * s, fill=(250, 246, 230, 230))
    return art('s19_dash', 4, 14, f)


def s19_gauge(w=200, h=24):
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((s, 4 * s, W - s, H - 4 * s), 6 * s, fill=(20, 24, 50, 230), outline=(110, 130, 200, 255), width=int(s))
        for frac, col in ((0.18, (220, 60, 60)), (0.32, (230, 180, 60))):
            d.rounded_rectangle((s, 4 * s, W * frac, H - 4 * s), 6 * s, fill=col + (200,))
            d.rounded_rectangle((W * (1 - frac), 4 * s, W - s, H - 4 * s), 6 * s, fill=col + (200,))
        d.rectangle((W * 0.32, 4 * s, W * 0.68, H - 4 * s), fill=(60, 180, 110, 200))
        d.line([(W / 2, 2 * s), (W / 2, H - 2 * s)], fill=(255, 255, 255, 255), width=int(1 * s))
    return art('s19_gauge', w, h, f)


def s19_needle():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(W / 2, H - 1 * s), (1 * s, 1 * s), (W - 1 * s, 1 * s)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    return art('s19_needle', 10, 12, f)


# ================================================================== 20. 정원 노노그램
def s20_cell(state, col=(240, 90, 120)):
    def f(d, im, s):
        W = im.width
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, W - 1 * s), 4 * s, fill=(110, 80, 50, 255), outline=(70, 50, 30, 255),
                            width=int(1 * s))
        d.rounded_rectangle((3 * s, 3 * s, W - 3 * s, W - 3 * s), 3 * s, fill=(140, 104, 70, 255))
        if state == 'x':
            d.line([(W * 0.3, W * 0.3), (W * 0.7, W * 0.7)], fill=(240, 230, 220, 255), width=int(2 * s))
            d.line([(W * 0.7, W * 0.3), (W * 0.3, W * 0.7)], fill=(240, 230, 220, 255), width=int(2 * s))
        elif state != 'e':
            c = W / 2
            d.line([(c, c), (c, W - 4 * s)], fill=(60, 150, 60, 255), width=int(1.6 * s))
            for k in range(5):
                a = math.radians(k * 72 - 90)
                px, py = c + math.cos(a) * 5.5 * s, c - 1 * s + math.sin(a) * 5.5 * s
                d.ellipse((px - 4.2 * s, py - 4.2 * s, px + 4.2 * s, py + 4.2 * s), fill=col + (255,), outline=(255, 255, 255, 180))
            d.ellipse((c - 3 * s, c - 4 * s, c + 3 * s, c + 2 * s), fill=(255, 220, 80, 255))
    return art('s20_%s' % state, 28, 28, f)
