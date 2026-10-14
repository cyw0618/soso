# -*- coding: utf-8 -*-
"""새 유세지 25곳(16~40)의 배경 그림.

사진이 없는 곳이라 밤 풍경 일러스트로 그린다 (검정+청색 테마). 2배 크기로 그린 뒤 줄여서 부드럽게 만든다.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from art_common import save, ensure_out

W, H = 960, 540
S = 2

# 밤 풍경 색
SKY_TOP = (6, 10, 30)
SKY_LOW = (38, 58, 128)
HILL_FAR = (26, 38, 86)
HILL_MID = (17, 26, 64)
HILL_NEAR = (10, 16, 42)
GROUND = (12, 20, 48)
LIGHT = (200, 220, 255)      # 창문·가로등 (차가운 빛)
WARM = (255, 214, 170)       # 아주 조금만 쓰는 따뜻한 빛
LEAF = (20, 52, 70)
LEAF_HI = (40, 96, 120)
TRUNK = (20, 18, 36)
WATER = (20, 46, 120)


class Canvas:
    def __init__(self, seed):
        self.im = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 255))
        self.rng = random.Random(seed)

    # ---- 레이어
    def new(self):
        return Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))

    def add(self, lay, blur=0, alpha=1.0):
        if blur:
            lay = lay.filter(ImageFilter.GaussianBlur(blur * S))
        if alpha < 1:
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * alpha)))
        self.im.alpha_composite(lay)

    def pen(self, fn, blur=0, alpha=1.0, glow=None):
        """fn(Pen) 으로 그린 레이어를 얹는다. glow=(반경, 세기) 면 빛 번짐도."""
        lay = self.new()
        fn(Pen(lay))
        if glow:
            g = lay.filter(ImageFilter.GaussianBlur(glow[0] * S))
            g.putalpha(g.getchannel('A').point(lambda v: min(255, int(v * glow[1]))))
            self.im.alpha_composite(g)
        self.add(lay, blur, alpha)

    # ---- 배경 요소
    def sky(self, top=SKY_TOP, low=SKY_LOW, horizon=0.62):
        h = int(H * S * horizon)
        a = np.zeros((H * S, W * S, 4), np.uint8)
        t = np.clip(np.arange(H * S) / max(1, h), 0, 1) ** 1.4
        for c in range(3):
            a[:, :, c] = (top[c] + (low[c] - top[c]) * t)[:, None]
        a[:, :, 3] = 255
        self.im.alpha_composite(Image.fromarray(a, 'RGBA'))

    def stars(self, n=90, ymax=0.45):
        def f(p):
            for _ in range(n):
                x, y = self.rng.uniform(0, W), self.rng.uniform(0, H * ymax)
                r = self.rng.choice([0.6, 0.8, 1.0, 1.4])
                a = self.rng.randint(90, 230)
                p.ell(x, y, r, r, (210, 225, 255, a))
        self.pen(f)

    def moon(self, x, y, r=22):
        self.pen(lambda p: p.ell(x, y, r * 2.6, r * 2.6, (90, 130, 255, 70)), blur=18)
        self.pen(lambda p: p.ell(x, y, r, r, (226, 234, 255, 255)), glow=(6, 0.8))
        self.pen(lambda p: p.ell(x + r * 0.35, y - r * 0.15, r * 0.82, r * 0.82, (0, 0, 0, 0)))

    def hills(self, base, amp, col, seed=0, rim=True, freq=1.0):
        rng = random.Random(seed)
        ph = [rng.uniform(0, 6.28) for _ in range(3)]
        pts = []
        for i in range(0, W + 9, 8):
            y = base - amp * (0.55 * math.sin(i / 160 * freq + ph[0]) + 0.3 * math.sin(i / 70 * freq + ph[1])
                              + 0.15 * math.sin(i / 31 * freq + ph[2]))
            pts.append((i, y))
        poly = [(0, H)] + pts + [(W, H)]
        self.pen(lambda p: p.poly(poly, col + (255,)))
        if rim:
            hi = tuple(min(255, c + 34) for c in col) + (200,)
            self.pen(lambda p: p.line(pts, hi, 1.6), blur=0.6)
        return pts

    def mountains(self, base, peaks, col, rim=True):
        """peaks: [(x, 높이)] 로 뾰족한 산줄기."""
        pts = [(0, base)]
        for x, h in peaks:
            pts.append((x, base - h))
        pts.append((W, base))
        poly = [(0, H)] + pts + [(W, H)]
        self.pen(lambda p: p.poly(poly, col + (255,)))
        if rim:
            self.pen(lambda p: p.line(pts[1:-1], tuple(min(255, c + 40) for c in col) + (220,), 1.5), blur=0.5)

    def ground(self, y, col=GROUND, col2=None):
        col2 = col2 or tuple(max(0, c - 6) for c in col)
        a = np.zeros((H * S, W * S, 4), np.uint8)
        y0 = int(y * S)
        t = np.clip((np.arange(H * S) - y0) / max(1, H * S - y0), 0, 1)
        for c in range(3):
            a[:, :, c] = (col[c] + (col2[c] - col[c]) * t)[:, None]
        a[:y0, :, 3] = 0
        a[y0:, :, 3] = 255
        self.im.alpha_composite(Image.fromarray(a, 'RGBA'))

    def water(self, y0, y1, col=WATER, lights=()):
        def f(p):
            p.rect(0, y0, W, y1, col + (255,))
            for k in range(26):
                y = self.rng.uniform(y0 + 4, y1 - 2)
                x = self.rng.uniform(0, W)
                w = self.rng.uniform(20, 90)
                p.line([(x, y), (x + w, y)], (120, 160, 255, self.rng.randint(40, 110)), 1.2)
        self.pen(f)
        for lx, lc in lights:     # 불빛이 물에 비침
            self.pen(lambda p: [p.line([(lx - 8 + self.rng.uniform(-4, 4), y), (lx + 8, y)], lc + (120,), 1.4)
                                for y in np.arange(y0 + 4, y1, 7)], blur=0.8)

    def lamp(self, x, base, h=70, col=LIGHT):
        self.pen(lambda p: (p.rect(x - 1.5, base - h, x + 1.5, base, (14, 18, 40, 255)),
                            p.rect(x - 1.5, base - h, x + 10, base - h + 3, (14, 18, 40, 255))))
        self.pen(lambda p: p.ell(x + 9, base - h + 6, 20, 20, col + (90,)), blur=10)
        self.pen(lambda p: p.ell(x + 9, base - h + 5, 3.5, 3, col + (255,)), glow=(4, 1.0))

    def light_cone(self, x, y_top, y_bot, w, col=LIGHT, alpha=50):
        self.pen(lambda p: p.poly([(x - 4, y_top), (x + 4, y_top), (x + w, y_bot), (x - w, y_bot)], col + (alpha,)), blur=8)

    def round_tree(self, x, base, h, col=LEAF, hi=LEAF_HI, fruits=None, fruit_col=(255, 150, 190)):
        r = h * 0.38

        def f(p):
            p.poly([(x - h * 0.04, base), (x + h * 0.04, base), (x + h * 0.025, base - h * 0.55), (x - h * 0.025, base - h * 0.55)],
                   TRUNK + (255,))
            for dx, dy, k in ((-0.45, 0.1, 0.75), (0.45, 0.1, 0.75), (0, -0.2, 1.0), (-0.2, 0.25, 0.7), (0.25, 0.25, 0.7)):
                p.ell(x + dx * r, base - h * 0.62 + dy * r, r * k, r * k * 0.86, col + (255,))
            p.ell(x - r * 0.25, base - h * 0.72, r * 0.45, r * 0.32, hi + (150,))
        self.pen(f)
        if fruits:
            rng = random.Random(int(x * 7 + base))

            def g(p):
                for _ in range(fruits):
                    a = rng.uniform(0, 6.28)
                    rr = rng.uniform(0.1, 0.85) * r
                    fx, fy = x + math.cos(a) * rr, base - h * 0.62 + math.sin(a) * rr * 0.8
                    p.ell(fx, fy, 3.2, 3.2, fruit_col + (255,))
                    p.ell(fx - 1, fy - 1, 1.1, 1.1, (255, 230, 240, 230))
            self.pen(g, glow=(3, 0.5))

    def pine(self, x, base, h, col=(14, 40, 60)):
        def f(p):
            p.rect(x - h * 0.03, base - h * 0.2, x + h * 0.03, base, TRUNK + (255,))
            for k in range(4):
                yb = base - h * (0.15 + k * 0.2)
                wdt = h * (0.32 - k * 0.06)
                p.poly([(x - wdt, yb), (x + wdt, yb), (x, yb - h * 0.34)], col + (255,))
            p.line([(x, base - h), (x - h * 0.2, base - h * 0.62)], (60, 110, 150, 120), 1.2)
        self.pen(f)

    def bamboo(self, x, base, h, col=(24, 70, 74), lean=0.0):
        def f(p):
            w = 5 + h / 120
            top = (x + lean * h, base - h)
            p.poly([(x - w / 2, base), (x + w / 2, base), (top[0] + w / 3, top[1]), (top[0] - w / 3, top[1])], col + (255,))
            for k in range(1, 12):
                t = k / 12
                yy = base - h * t
                xx = x + lean * h * t
                p.line([(xx - w / 2, yy), (xx + w / 2, yy)], (60, 130, 120, 200), 1.2)
                if k % 3 == 0:
                    d = 1 if k % 2 else -1
                    p.poly([(xx, yy), (xx + d * 26, yy - 6), (xx + d * 24, yy - 1)], (30, 90, 80, 230))
        self.pen(f)

    def house(self, x, base, w, h, wall=(26, 34, 70), roof=(12, 18, 46), lit=True, door=True):
        rng = self.rng

        def f(p):
            p.rect(x, base - h, x + w, base, wall + (255,))
            p.poly([(x - 10, base - h), (x + w + 10, base - h), (x + w * 0.5, base - h - h * 0.55)], roof + (255,))
            p.line([(x - 10, base - h), (x + w * 0.5, base - h - h * 0.55), (x + w + 10, base - h)], (70, 100, 170, 200), 1.4)
            if door:
                p.rect(x + w * 0.42, base - h * 0.5, x + w * 0.58, base, (10, 12, 30, 255))
        self.pen(f)
        if lit:
            def g(p):
                for wx in (x + w * 0.14, x + w * 0.7):
                    c = WARM if rng.random() < 0.3 else LIGHT
                    p.rect(wx, base - h * 0.75, wx + w * 0.17, base - h * 0.45, c + (230,))
            self.pen(g, glow=(5, 0.9))

    def hanok(self, x, base, w, h, wall=(30, 34, 60), roof=(14, 18, 40)):
        def f(p):
            p.rect(x, base - h, x + w, base, wall + (255,))
            for k in range(5):
                xx = x + w * (0.1 + k * 0.2)
                p.rect(xx - 2, base - h, xx + 2, base, (16, 18, 36, 255))
            # 기와지붕 (끝이 살짝 들린 곡선)
            pts = []
            for i in range(41):
                t = i / 40
                xx = x - w * 0.18 + (w * 1.36) * t
                lift = (abs(t - 0.5) * 2) ** 3 * h * 0.28
                pts.append((xx, base - h - lift))
            top = [(x + w * 0.12, base - h - h * 0.62), (x + w * 0.88, base - h - h * 0.62)]
            p.poly(pts + top[::-1], roof + (255,))
            p.line(pts, (80, 110, 190, 220), 1.6)
            p.line(top, (80, 110, 190, 160), 1.4)
        self.pen(f)

    def apartment(self, x, base, w, h, col=(20, 28, 62), lit=0.35):
        rng = self.rng

        def f(p):
            p.rect(x, base - h, x + w, base, col + (255,))
            p.line([(x, base - h), (x + w, base - h)], (80, 110, 190, 220), 1.4)
        self.pen(f)

        def g(p):
            rows = int(h / 16)
            cols = max(2, int(w / 14))
            for r in range(rows):
                for c in range(cols):
                    if rng.random() < lit:
                        wx = x + 5 + c * (w - 8) / cols
                        wy = base - h + 8 + r * 16
                        cc = WARM if rng.random() < 0.15 else LIGHT
                        p.rect(wx, wy, wx + 6, wy + 7, cc + (rng.randint(150, 240),))
        self.pen(g, glow=(3, 0.6))

    def sign(self, x, y, w, h, col):
        self.pen(lambda p: p.rect(x, y, x + w, y + h, col + (235,), r=3), glow=(6, 1.0))
        self.pen(lambda p: p.rect(x + 4, y + h * 0.4, x + w - 4, y + h * 0.6, (255, 255, 255, 120)))

    def road(self, vx, vy, bottom_w, col=(18, 22, 46), line=(150, 170, 230), dashes=True):
        def f(p):
            p.poly([(vx - 3, vy), (vx + 3, vy), (W / 2 + bottom_w / 2, H), (W / 2 - bottom_w / 2, H)], col + (255,))
            if dashes:
                for k in range(10):
                    t0, t1 = (k / 10) ** 1.8, ((k + 0.5) / 10) ** 1.8
                    p.line([(vx + (W / 2 - vx) * t0, vy + (H - vy) * t0), (vx + (W / 2 - vx) * t1, vy + (H - vy) * t1)],
                           line + (200,), 1 + 3 * t1)
        self.pen(f)

    def people(self, n, y0, y1, col=(8, 12, 30)):
        rng = self.rng

        def f(p):
            for _ in range(n):
                x = rng.uniform(20, W - 20)
                y = rng.uniform(y0, y1)
                s_ = 0.6 + (y - y0) / max(1, y1 - y0) * 0.6
                p.ell(x, y - 30 * s_, 6 * s_, 6 * s_, col + (255,))
                p.poly([(x - 9 * s_, y), (x + 9 * s_, y), (x + 6 * s_, y - 24 * s_), (x - 6 * s_, y - 24 * s_)], col + (255,))
        self.pen(f)

    def fog(self, y, h=60, alpha=60):
        self.pen(lambda p: p.rect(-20, y - h / 2, W + 20, y + h / 2, (90, 120, 220, alpha)), blur=18)

    def finish(self):
        from make_places import finish_place
        im = self.im.convert('RGB').resize((W, H), Image.LANCZOS)
        return finish_place(im)


class Pen:
    """960x540 좌표로 그리는 펜 (내부적으로 S배)."""

    def __init__(self, lay):
        self.d = ImageDraw.Draw(lay)

    def poly(self, pts, col):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=col)

    def rect(self, x0, y0, x1, y1, col, r=0):
        if r:
            self.d.rounded_rectangle((x0 * S, y0 * S, x1 * S, y1 * S), r * S, fill=col)
        else:
            self.d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), fill=col)

    def ell(self, cx, cy, rx, ry, col):
        self.d.ellipse(((cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S), fill=col)

    def line(self, pts, col, w=1.0):
        self.d.line([(x * S, y * S) for x, y in pts], fill=col, width=max(1, int(w * S)), joint='curve')


# ================================================================== 장소별 그림
def p16(c):   # 오봉산 등산로: 산줄기 + 돌계단
    c.sky(); c.stars(); c.moon(780, 80)
    c.mountains(330, [(80, 120), (200, 210), (330, 150), (470, 250), (600, 170), (760, 230), (900, 130)], HILL_FAR)
    c.hills(380, 40, HILL_MID, 3)
    for x in (60, 130, 200, 760, 830, 900):
        c.pine(x, 420 + (x % 3) * 8, 150)
    c.ground(420, (14, 22, 52))

    def steps(p):
        for k in range(12):
            t0, t1 = k / 12, (k + 1) / 12
            y0, y1 = H - (H - 250) * t0 ** 0.9, H - (H - 250) * t1 ** 0.9
            w0, w1 = 300 * (1 - t0 * 0.85), 300 * (1 - t1 * 0.85)
            cx = W / 2 + math.sin(t0 * 3) * 30
            p.poly([(cx - w0 / 2, y0), (cx + w0 / 2, y0), (cx + w1 / 2, y1), (cx - w1 / 2, y1)], (40, 52, 96, 255))
            p.line([(cx - w1 / 2, y1), (cx + w1 / 2, y1)], (120, 150, 230, 230), 1.4)
    c.pen(steps)
    c.lamp(330, 470, 80); c.lamp(610, 470, 80)


def p17(c):   # 고복자연공원: 저수지 + 정자
    c.sky(); c.stars(); c.moon(200, 90)
    c.hills(250, 60, HILL_FAR, 1)
    c.hills(290, 30, HILL_MID, 2)
    c.water(300, 540, lights=[(640, LIGHT), (700, LIGHT), (240, (160, 180, 255))])

    def deck(p):
        p.rect(560, 300, 900, 312, (16, 20, 44, 255))
        for x in range(570, 900, 40):
            p.rect(x, 300, x + 4, 345, (12, 14, 34, 255))
        # 정자
        p.rect(690, 220, 696, 300, (14, 16, 36, 255)); p.rect(784, 220, 790, 300, (14, 16, 36, 255))
        p.poly([(660, 222), (820, 222), (790, 196), (690, 196)], (12, 16, 40, 255))
        p.line([(660, 222), (690, 196), (790, 196), (820, 222)], (90, 120, 200, 230), 1.6)
    c.pen(deck)
    c.lamp(600, 300, 60); c.lamp(880, 300, 60)
    for x in (40, 110, 420):
        c.round_tree(x, 300, 110)


def p18(c):   # 고복리 마을회관
    c.sky(); c.stars(); c.moon(820, 70)
    c.hills(300, 40, HILL_FAR, 4)
    c.ground(360)
    c.house(80, 380, 120, 80); c.house(700, 390, 150, 90)
    # 마을회관
    def hall(p):
        p.rect(330, 250, 630, 400, (28, 38, 80, 255))
        p.poly([(310, 252), (650, 252), (600, 210), (360, 210)], (14, 20, 50, 255))
        p.line([(310, 252), (360, 210), (600, 210), (650, 252)], (90, 120, 210, 230), 1.6)
        p.rect(445, 330, 515, 400, (10, 14, 32, 255))
    c.pen(hall)
    c.sign(400, 262, 160, 26, (60, 110, 240))
    c.pen(lambda p: [p.rect(350 + k * 210, 300, 400 + k * 210, 330, LIGHT + (220,)) for k in range(2)], glow=(6, 1.0))
    c.round_tree(250, 400, 150, fruits=14, fruit_col=(255, 160, 110))
    c.people(5, 430, 520)


def p19(c):   # 봉산리 향나무: 크고 구부러진 노거수
    c.sky(); c.stars(); c.moon(160, 80, 26)
    c.hills(320, 30, HILL_FAR, 5)
    c.ground(380)

    def tree(p):
        trunk = [(440, 470), (500, 470), (505, 400), (530, 330), (520, 280), (480, 250), (470, 300), (450, 360), (445, 420)]
        p.poly(trunk, (24, 20, 44, 255))
        p.line([(470, 460), (480, 380), (500, 320)], (70, 70, 120, 200), 2)
        for cx, cy, r in ((420, 230, 70), (520, 200, 90), (610, 240, 70), (470, 170, 60), (570, 150, 60), (360, 270, 45), (660, 290, 45)):
            p.ell(cx, cy, r, r * 0.7, (16, 54, 66, 255))
            p.ell(cx - r * 0.3, cy - r * 0.3, r * 0.5, r * 0.3, (36, 92, 104, 170))
    c.pen(tree)
    # 돌담
    def wall(p):
        for k in range(24):
            x = k * 42
            p.rect(x, 440 + (k % 2) * 3, x + 40, 470, (34, 40, 76, 255), r=6)
            p.line([(x + 4, 442 + (k % 2) * 3), (x + 36, 442 + (k % 2) * 3)], (90, 110, 180, 200), 1)
    c.pen(wall)
    c.light_cone(500, 100, 470, 160, alpha=26)


def p20(c):   # 봉산로 숲길
    c.sky(top=(4, 8, 24), low=(26, 40, 96)); c.stars(40, 0.3)
    c.ground(330, (12, 18, 44))

    def path(p):
        p.poly([(470, 330), (490, 330), (720, 540), (240, 540)], (34, 40, 78, 255))
        p.line([(470, 330), (240, 540)], (90, 110, 190, 160), 1.4)
        p.line([(490, 330), (720, 540)], (90, 110, 190, 160), 1.4)
    c.pen(path)
    for k, x in enumerate((20, 120, 210, 300, 380, 560, 640, 730, 830, 930)):
        c.pine(x, 360 + abs(x - 480) * 0.25, 220 + abs(x - 480) * 0.35, col=(12, 34, 52))
    c.lamp(400, 420, 90); c.lamp(570, 430, 90)
    c.fog(330, 50, 50)


def p21(c):   # 송곡리 마을 운동장
    c.sky(); c.stars(); c.moon(140, 70)
    c.hills(260, 40, HILL_FAR, 6)
    c.house(40, 300, 110, 70); c.house(780, 300, 120, 70)
    c.ground(310, (14, 34, 46), (10, 26, 36))

    def field(p):
        p.poly([(240, 320), (720, 320), (900, 540), (60, 540)], (18, 46, 56, 255))
        p.line([(240, 320), (720, 320), (900, 540)], (150, 190, 240, 220), 1.6)
        p.line([(240, 320), (60, 540)], (150, 190, 240, 220), 1.6)
        p.line([(480, 320), (480, 540)], (150, 190, 240, 140), 1.2)
        # 골대
        p.rect(400, 260, 404, 330, (220, 230, 255, 255)); p.rect(556, 260, 560, 330, (220, 230, 255, 255))
        p.rect(400, 258, 560, 262, (220, 230, 255, 255))
        for k in range(12):
            p.line([(404 + k * 13, 262), (404 + k * 13, 326)], (180, 200, 255, 70), 0.6)
    c.pen(field)
    c.lamp(200, 330, 120); c.lamp(760, 330, 120)
    c.light_cone(209, 210, 540, 160, alpha=30); c.light_cone(769, 210, 540, 160, alpha=30)


def p22(c):   # 금이로 고개: 굽은 고갯길 + 절벽
    c.sky(); c.stars(); c.moon(760, 70, 18)
    c.mountains(300, [(100, 160), (300, 230), (520, 180), (720, 250), (900, 170)], HILL_FAR)

    def cliff(p):
        p.poly([(0, 540), (0, 200), (120, 240), (200, 330), (260, 540)], (16, 22, 52, 255))
        p.poly([(960, 540), (960, 220), (840, 260), (760, 360), (720, 540)], (16, 22, 52, 255))
        for k in range(8):
            p.line([(20 + k * 25, 230 + k * 20), (60 + k * 22, 260 + k * 24)], (60, 80, 150, 140), 1)
    c.hills(380, 40, HILL_MID, 7)
    # 굽은 길
    def road(p):
        pts_l, pts_r = [], []
        for i in range(30):
            t = i / 29
            y = 310 + (540 - 310) * t
            cx = 480 + math.sin(t * 3.4) * 120 * (1 - t * 0.3)
            w = 18 + 300 * t ** 1.4
            pts_l.append((cx - w / 2, y)); pts_r.append((cx + w / 2, y))
        p.poly(pts_l + pts_r[::-1], (28, 32, 64, 255))
        p.line(pts_r, (200, 210, 255, 200), 2)
        for i in range(0, 29, 3):
            a, b = pts_l[i], pts_r[i]
            a2, b2 = pts_l[i + 1], pts_r[i + 1]
            p.line([((a[0] + b[0]) / 2, a[1]), ((a2[0] + b2[0]) / 2, a2[1])], (230, 230, 255, 220), 1 + 2 * i / 29)
    c.pen(road)
    c.pen(cliff)
    # 떨어지는 돌
    c.pen(lambda p: [p.ell(x, y, r, r * 0.8, (60, 66, 110, 255)) for x, y, r in ((300, 120, 10), (650, 160, 14), (520, 80, 8))])


def p23(c):   # 신안리 과수원: 과일나무 줄 + 상자
    c.sky(); c.stars(); c.moon(840, 80)
    c.hills(260, 30, HILL_FAR, 8)
    c.ground(290, (16, 30, 52))
    for row in range(4):
        y = 300 + row * 60
        h = 70 + row * 40
        for k in range(6 - row // 2):
            x = 60 + k * (900 / (6 - row // 2)) + (row % 2) * 40
            c.round_tree(x, y + h * 0.2, h, fruits=10 + row * 4, fruit_col=(255, 190, 140) if (k + row) % 2 else (255, 130, 160))

    def crates(p):
        for k, (x, y) in enumerate(((380, 490), (430, 490), (405, 455))):
            p.rect(x, y, x + 46, y + 34, (70, 52, 60, 255))
            p.line([(x, y + 12), (x + 46, y + 12)], (120, 96, 110, 255), 1.4)
            p.line([(x, y + 24), (x + 46, y + 24)], (120, 96, 110, 255), 1.4)
    c.pen(crates)


def p24(c):   # 서창리 대학가: 원룸·카페 거리
    c.sky(); c.stars(40)
    for k, (x, w, h) in enumerate(((0, 140, 260), (150, 120, 210), (280, 150, 300), (440, 110, 230), (560, 160, 280), (730, 120, 220), (860, 110, 250))):
        c.apartment(x, 420, w, h, lit=0.45)
    c.ground(420, (20, 24, 54))
    c.sign(170, 300, 80, 24, (80, 120, 255)); c.sign(470, 290, 70, 22, (150, 90, 255)); c.sign(740, 300, 80, 24, (60, 160, 255))
    c.road(480, 420, 900, col=(22, 26, 56))
    c.lamp(120, 470, 100); c.lamp(820, 470, 100)
    c.people(7, 440, 530)


def p25(c):   # 연기향교: 한옥 + 홍살문 + 은행나무
    c.sky(); c.stars(); c.moon(160, 80)
    c.hills(270, 30, HILL_FAR, 9)
    c.hanok(300, 340, 360, 90)
    c.ground(340, (20, 24, 52))

    def gate(p):
        for x in (140, 820):
            p.rect(x - 5, 230, x + 5, 470, (110, 30, 50, 255))
        p.rect(130, 236, 830, 246, (110, 30, 50, 255))
        for k in range(26):
            x = 160 + k * 25
            p.rect(x - 1.5, 246, x + 1.5, 270, (110, 30, 50, 255))
        p.rect(130, 268, 830, 274, (110, 30, 50, 255))
    c.pen(gate)

    def steps(p):
        for k in range(5):
            p.rect(380 - k * 20, 350 + k * 22, 580 + k * 20, 372 + k * 22, (40, 46, 84, 255))
            p.line([(380 - k * 20, 350 + k * 22), (580 + k * 20, 350 + k * 22)], (110, 130, 210, 220), 1.2)
    c.pen(steps)
    c.round_tree(860, 420, 220, col=(60, 60, 40), hi=(110, 110, 60))


def p26(c):   # 서북부 택지지구: 새 아파트 + 크레인
    c.sky(); c.stars(50)
    for k in range(7):
        x = 20 + k * 135
        c.apartment(x, 400, 90, 180 + (k % 3) * 60, lit=0.3)

    def crane(p):
        p.rect(720, 80, 728, 400, (40, 50, 96, 255))
        p.rect(560, 80, 900, 88, (40, 50, 96, 255))
        p.line([(724, 60), (600, 84)], (60, 80, 140, 255), 1.2)
        p.line([(724, 60), (880, 84)], (60, 80, 140, 255), 1.2)
        p.rect(610, 88, 612, 180, (60, 80, 140, 255))
        p.rect(596, 180, 626, 196, (60, 70, 120, 255))
    c.pen(crane)
    c.pen(lambda p: p.ell(724, 62, 3, 3, (255, 90, 110, 255)), glow=(5, 1.0))
    c.ground(400, (18, 24, 54))
    c.road(480, 400, 1000)


def p27(c):   # 신흥리 복숭아밭
    c.sky(); c.stars(); c.moon(130, 70, 20)
    c.hills(240, 40, HILL_FAR, 10)
    c.ground(270, (16, 28, 50))
    for row in range(3):
        y = 290 + row * 80
        h = 90 + row * 60
        for k in range(5):
            x = 70 + k * 205 + (row % 2) * 90
            c.round_tree(x, y + h * 0.25, h, col=(24, 56, 66), fruits=14 + row * 6, fruit_col=(255, 140, 170))


def p28(c):   # 죽림리 대숲
    c.sky(top=(4, 8, 22), low=(20, 40, 90)); c.moon(480, 70, 24)
    c.ground(420, (10, 22, 32))
    rng = random.Random(28)
    for k in range(40):
        x = rng.uniform(-20, W + 20)
        c.bamboo(x, 560, rng.uniform(380, 560), col=(18 + k % 3 * 4, 58 + k % 4 * 6, 60), lean=rng.uniform(-0.06, 0.06))
    c.light_cone(480, 90, 540, 180, alpha=30)
    c.fog(470, 80, 70)


def p29(c):   # 번암리 들녘: 논 + 물길
    c.sky(); c.stars(); c.moon(760, 90)
    c.hills(250, 25, HILL_FAR, 11)
    c.ground(260, (16, 32, 50))

    def paddies(p):
        vx, vy = 480, 250
        for k in range(-8, 9):
            p.line([(vx + k * 8, vy), (W / 2 + k * 160, H)], (40, 70, 110, 200), 1.2)
        for j in range(1, 9):
            t = (j / 9) ** 1.7
            y = vy + (H - vy) * t
            p.line([(0, y), (W, y)], (40, 70, 110, 200), 1.2)
        # 물길
        p.poly([(474, 250), (486, 250), (560, 540), (400, 540)], (40, 90, 200, 255))
    c.pen(paddies)
    c.pen(lambda p: [p.line([(480 + (t - 0.5) * 60 * k / 9, 260 + k * 30), (480 + (t - 0.5) * 60 * k / 9 + 10, 260 + k * 30)],
                            (180, 210, 255, 160), 1) for k in range(9) for t in (0.3, 0.7)])


def p30(c):   # 성제리 고갯길: 해 진 고개 + 이정표
    c.sky(top=(8, 10, 34), low=(70, 60, 140), horizon=0.6)
    c.moon(480, 150, 34)
    c.mountains(330, [(120, 90), (300, 140), (480, 110), (660, 150), (860, 100)], (24, 28, 70))
    c.hills(400, 30, HILL_MID, 12)
    c.road(480, 330, 520, col=(30, 30, 62))

    def post(p):
        p.rect(770, 300, 778, 470, (40, 30, 50, 255))
        p.poly([(700, 320), (850, 320), (870, 340), (850, 360), (700, 360)], (60, 44, 70, 255))
        p.rect(170, 330, 176, 470, (40, 30, 50, 255))
        p.ell(173, 330, 30, 8, (40, 30, 50, 255))
    c.pen(post)
    c.pen(lambda p: [p.ell(x, 470, 70, 8, (0, 0, 0, 120)) for x in (174, 774)], blur=4)


def p31(c):   # 연서면 들판: 허수아비 + 새
    c.sky(); c.stars(); c.moon(800, 70)
    c.hills(280, 30, HILL_FAR, 13)
    c.ground(300, (22, 34, 48))
    rng = random.Random(31)

    def crops(p):
        for k in range(600):
            x = rng.uniform(0, W)
            y = rng.uniform(310, 540)
            h = 8 + (y - 300) * 0.12
            p.line([(x, y), (x + rng.uniform(-3, 3), y - h)], (60, 90, 80, 220), 1)
            p.ell(x, y - h, 2, 3.5, (110, 120, 70, 230))
    c.pen(crops)

    def scarecrow(p):
        p.rect(476, 300, 484, 470, (50, 40, 50, 255))
        p.rect(420, 330, 540, 338, (50, 40, 50, 255))
        p.poly([(450, 330), (510, 330), (520, 410), (440, 410)], (60, 70, 120, 255))
        p.ell(480, 300, 22, 22, (200, 190, 150, 255))
        p.poly([(450, 290), (510, 290), (480, 262)], (90, 70, 60, 255))
    c.pen(scarecrow)
    c.pen(lambda p: [p.line([(x - 10, y), (x, y + 5), (x + 10, y)], (14, 18, 40, 255), 2) for x, y in
                     ((300, 140), (340, 120), (620, 100), (660, 130), (700, 110))])


def p32(c):   # 신대리 마을: 정자 + 초롱
    c.sky(); c.stars(); c.moon(140, 80)
    c.hills(290, 30, HILL_FAR, 14)
    c.ground(340)
    c.house(40, 360, 140, 80); c.house(780, 370, 140, 80); c.house(600, 340, 110, 60)

    def pavilion(p):
        for x in (330, 470, 610):
            p.rect(x - 4, 270, x + 4, 400, (40, 30, 50, 255))
        p.rect(310, 380, 630, 392, (50, 40, 60, 255))
        pts = []
        for i in range(31):
            t = i / 30
            pts.append((290 + 360 * t, 270 - (abs(t - 0.5) * 2) ** 3 * 26))
        p.poly(pts + [(580, 220), (360, 220)], (14, 18, 40, 255))
        p.line(pts, (90, 120, 200, 220), 1.6)
    c.pen(pavilion)
    c.pen(lambda p: [p.ell(x, 290, 9, 12, (120, 160, 255, 255)) for x in (360, 470, 580)], glow=(10, 1.0))
    c.people(4, 400, 440)


def p33(c):   # 조천 징검다리
    c.sky(); c.stars(); c.moon(780, 80)
    c.hills(250, 30, HILL_FAR, 15)
    c.ground(260, (16, 30, 46))
    c.water(330, 470, lights=[(780, (210, 225, 255))])

    def stones(p):
        for k in range(8):
            x = 150 + k * 95
            y = 400 + math.sin(k) * 14
            p.ell(x, y, 34, 12, (60, 66, 100, 255))
            p.ell(x - 6, y - 4, 22, 5, (110, 120, 170, 200))
        rng = random.Random(33)
        for k in range(70):
            x = rng.uniform(0, W)
            y = rng.choice((330, 470)) + rng.uniform(-6, 6)
            p.line([(x, y), (x + rng.uniform(-6, 6), y - rng.uniform(20, 46))], (30, 60, 70, 255), 1.6)
    c.pen(stones)


def p34(c):   # 조천 둑방길: 자전거길 + 가로등
    c.sky(); c.stars(); c.moon(140, 70)
    c.water(290, 360, lights=[(300, LIGHT), (650, LIGHT)])
    c.ground(360, (18, 34, 50))

    def bank(p):
        p.poly([(0, 380), (960, 340), (960, 420), (0, 470)], (34, 40, 76, 255))
        p.line([(0, 425), (960, 380)], (120, 160, 255, 220), 1.4)
        p.line([(0, 380), (960, 340)], (90, 120, 200, 200), 1)
    c.pen(bank)
    for x in (120, 380, 640, 900):
        c.lamp(x, 420 - x * 0.042, 90)
    for x in (60, 250, 520, 780):
        c.round_tree(x, 300, 120, col=(40, 40, 80), hi=(110, 100, 170), fruits=18, fruit_col=(255, 200, 230))


def p35(c):   # 시외버스터미널
    c.sky(); c.stars(40)
    c.apartment(0, 330, 160, 160, lit=0.3); c.apartment(800, 330, 160, 190, lit=0.3)

    def terminal(p):
        p.rect(170, 200, 790, 330, (30, 40, 86, 255))
        p.rect(150, 190, 810, 206, (16, 22, 52, 255))
        for k in range(8):
            p.rect(200 + k * 72, 240, 250 + k * 72, 310, (140, 170, 240, 200))
    c.pen(terminal, glow=(6, 0.4))
    c.sign(380, 150, 200, 34, (70, 120, 255))
    c.ground(330, (20, 24, 54))

    def buses(p):
        for k, x in enumerate((120, 400, 680)):
            y = 400 + k % 2 * 10
            p.rect(x, y - 70, x + 230, y, (60, 90, 190, 255), r=10)
            p.rect(x + 10, y - 60, x + 220, y - 34, (160, 190, 255, 230))
            p.ell(x + 40, y, 16, 16, (10, 10, 20, 255)); p.ell(x + 190, y, 16, 16, (10, 10, 20, 255))
    c.pen(buses)


def p36(c):   # 행정복지센터: 관공서 + 깃발
    c.sky(); c.stars(); c.moon(820, 70)

    def office(p):
        p.rect(220, 170, 740, 380, (34, 42, 84, 255))
        p.rect(200, 160, 760, 176, (16, 22, 52, 255))
        for r in range(3):
            for k in range(8):
                p.rect(250 + k * 60, 200 + r * 55, 280 + k * 60, 235 + r * 55, LIGHT + (180 if (k + r) % 3 else 60,))
        p.rect(430, 320, 530, 380, (14, 18, 40, 255))
        for k in range(4):
            p.rect(400 - k * 20, 380 + k * 12, 560 + k * 20, 392 + k * 12, (40, 48, 90, 255))
    c.pen(office, glow=(4, 0.3))
    c.sign(380, 130, 200, 28, (70, 120, 255))
    c.ground(420, (20, 26, 56))

    def flags(p):
        for k, x in enumerate((110, 160, 800, 850)):
            p.rect(x - 2, 200, x + 2, 420, (150, 160, 200, 255))
            p.poly([(x + 2, 204), (x + 46, 214), (x + 2, 236)], [(220, 60, 80, 255), (70, 120, 255, 255)][k % 2])
    c.pen(flags)


def p37(c):   # 명리 방앗간: 굴뚝 + 김 + 쌀가마
    c.sky(); c.stars(); c.moon(160, 70)

    def mill(p):
        p.rect(300, 220, 700, 420, (36, 34, 66, 255))
        p.poly([(280, 222), (720, 222), (680, 170), (320, 170)], (16, 18, 44, 255))
        p.line([(280, 222), (320, 170), (680, 170), (720, 222)], (100, 120, 200, 220), 1.6)
        p.rect(600, 90, 630, 180, (40, 30, 50, 255))
        p.rect(440, 320, 560, 420, (14, 14, 34, 255))
    c.pen(mill)
    c.pen(lambda p: [p.ell(615 + k * 14, 70 - k * 22, 20 + k * 6, 14 + k * 4, (180, 190, 230, 90 - k * 12)) for k in range(5)], blur=4)
    c.sign(400, 236, 200, 30, (110, 90, 255))
    c.pen(lambda p: [p.rect(330 + k * 290, 280, 380 + k * 290, 320, WARM + (210,)) for k in range(2)], glow=(6, 0.9))
    c.ground(420, (22, 24, 52))

    def sacks(p):
        for k, (x, y) in enumerate(((180, 470), (240, 470), (210, 430), (760, 470), (820, 470))):
            p.ell(x, y, 30, 26, (170, 160, 140, 255))
            p.line([(x - 20, y - 4), (x + 20, y - 4)], (120, 110, 100, 255), 1.6)
    c.pen(sacks)


def p38(c):   # 새내 골목: 좁은 골목 + 전선 + 벽보
    c.sky(top=(6, 8, 26), low=(30, 44, 100), horizon=0.4); c.stars(30, 0.2)

    def alley(p):
        p.poly([(0, 0), (380, 140), (380, 420), (0, 540)], (30, 34, 70, 255))
        p.poly([(960, 0), (580, 140), (580, 420), (960, 540)], (26, 30, 64, 255))
        p.poly([(380, 420), (580, 420), (960, 540), (0, 540)], (20, 22, 48, 255))
        for k in range(6):
            p.line([(0, 80 + k * 70), (380, 170 + k * 45)], (40, 46, 90, 255), 1)
            p.line([(960, 80 + k * 70), (580, 170 + k * 45)], (36, 40, 84, 255), 1)
        # 전선
        for k in range(3):
            p.line([(0, 60 + k * 14), (480, 120 + k * 8), (960, 50 + k * 12)], (10, 10, 24, 255), 1)
    c.pen(alley)

    def posters(p):
        for k, (x0, y0) in enumerate(((60, 200), (190, 230), (680, 230), (820, 200))):
            col = [(90, 130, 255), (160, 100, 255), (230, 90, 120), (80, 170, 255)][k]
            p.poly([(x0, y0), (x0 + 90, y0 + (20 if x0 < 480 else -20)), (x0 + 90, y0 + 130 + (20 if x0 < 480 else -20)), (x0, y0 + 130)], col + (230,))
            p.rect(x0 + 15, y0 + 20, x0 + 75, y0 + 30, (255, 255, 255, 160))
    c.pen(posters)
    c.lamp(560, 400, 160)


def p39(c):   # 으뜸길 상가: 간판 + 차양
    c.sky(); c.stars(30)
    for k in range(5):
        x = k * 196
        c.apartment(x, 330, 186, 200 + (k % 2) * 40, lit=0.25)
    cols = [(80, 130, 255), (150, 90, 255), (230, 80, 120), (60, 170, 255), (120, 100, 255)]
    for k in range(5):
        c.sign(k * 196 + 20, 200, 146, 30, cols[k])

    def shops(p):
        for k in range(5):
            x = k * 196
            p.rect(x + 6, 330, x + 190, 430, (20, 24, 54, 255))
            p.rect(x + 20, 350, x + 176, 420, LIGHT + (110,))
            for j in range(8):
                p.poly([(x + 6 + j * 23, 320), (x + 29 + j * 23, 320), (x + 29 + j * 23, 345), (x + 6 + j * 23, 345)],
                       (cols[k] if j % 2 else (230, 235, 255)) + (255,))
    c.pen(shops, glow=(4, 0.4))
    c.ground(430, (22, 24, 52))
    c.people(9, 450, 530)


def p40(c):   # 남리 철길 건널목: 철길 + 차단기 + 경고등
    c.sky(); c.stars(); c.moon(800, 70)
    c.hills(300, 25, HILL_FAR, 16)
    c.ground(310, (18, 22, 50))

    def tracks(p):
        p.rect(0, 360, 960, 420, (26, 28, 56, 255))
        for k in range(40):
            x = k * 26
            p.rect(x, 364, x + 12, 416, (50, 44, 60, 255))
        for y in (372, 404):
            p.rect(0, y, 960, y + 5, (170, 180, 220, 255))
        # 차단기
        p.rect(160, 250, 168, 360, (200, 200, 220, 255))
        for k in range(9):
            p.rect(168 + k * 30, 268, 198 + k * 30, 278, ((230, 60, 80) if k % 2 else (240, 240, 250)) + (255,))
        p.rect(800, 250, 808, 360, (200, 200, 220, 255))
        p.rect(140, 250, 190, 262, (30, 30, 40, 255))
        p.rect(780, 250, 830, 262, (30, 30, 40, 255))
    c.pen(tracks)
    c.pen(lambda p: [p.ell(x, 256, 7, 7, (255, 60, 80, 255)) for x in (152, 178, 792, 818)], glow=(8, 1.2))
    c.road(480, 310, 400, col=(24, 26, 54), dashes=False)
    c.pen(lambda p: p.rect(380, 360, 580, 420, (30, 32, 64, 255)))


SCENES = {16: p16, 17: p17, 18: p18, 19: p19, 20: p20, 21: p21, 22: p22, 23: p23, 24: p24, 25: p25,
          26: p26, 27: p27, 28: p28, 29: p29, 30: p30, 31: p31, 32: p32, 33: p33, 34: p34, 35: p35,
          36: p36, 37: p37, 38: p38, 39: p39, 40: p40}


def build_all(only=None, force=False):
    import os
    from art_common import OUT
    ensure_out()
    out = {}
    me = os.path.getmtime(__file__)
    for k, fn in SCENES.items():
        if only and k not in only:
            continue
        path = os.path.join(OUT, 'place_%02d.png' % k)
        if not force and not only and os.path.exists(path) and os.path.getmtime(path) > me:
            out[k] = path
            continue
        c = Canvas(k)
        fn(c)
        out[k] = save(c.finish(), 'place_%02d' % k)
    return out


if __name__ == '__main__':
    import sys
    only = [int(a) for a in sys.argv[1:]] or None
    build_all(only)
