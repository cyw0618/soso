# -*- coding: utf-8 -*-
"""세종시장 선거 40곳(s01~s40) · 대통령 선거 40곳(k01~k40) 배경 그림 (밤 풍경 일러스트, 검정+청색 테마).

place_art.Canvas 위에 랜드마크 부품(유리 빌딩, 궁궐 문, 관람차, 경기장, 크레인, 다리 ...)을 더해서 지역 특색을 살린다.
용량을 줄이려고 256색 PNG 로 저장한다.
"""
import math
import random
import os

from PIL import Image, ImageFilter

import place_art as PA
from place_art import Canvas, W, H, LIGHT, WARM, LEAF, LEAF_HI, HILL_FAR, HILL_MID, HILL_NEAR, GROUND, WATER
from art_common import ensure_out, OUT

PINK = (255, 160, 200)
ORANGE = (255, 170, 60)
NEON = [(90, 140, 255), (255, 80, 140), (120, 230, 255), (180, 120, 255), (255, 210, 120)]


class C2(Canvas):
    # ---------------------------------------------------------- 건물
    def glass(self, x, base, w, h, col=(18, 30, 80), lit=0.5, top=None):
        rng = self.rng

        def f(p):
            p.rect(x, base - h, x + w, base, col + (255,))
            for k in range(1, int(w / 12)):
                xx = x + k * 12
                p.line([(xx, base - h), (xx, base)], (50, 80, 170, 150), 0.8)
            p.line([(x, base - h), (x + w, base - h)], (130, 170, 255, 230), 1.4)
            if top:
                p.rect(x + w / 2 - 1.5, base - h - top, x + w / 2 + 1.5, base - h, (40, 60, 120, 255))

        self.pen(f)

        def g(p):
            for r in range(int(h / 10)):
                for c in range(int(w / 12)):
                    if rng.random() < lit:
                        p.rect(x + 3 + c * 12, base - h + 4 + r * 10, x + 10 + c * 12, base - h + 9 + r * 10,
                               (LIGHT if rng.random() > 0.1 else WARM) + (rng.randint(120, 230),))
        self.pen(g, glow=(3, 0.6))
        if top:
            self.pen(lambda p: p.ell(x + w / 2, base - h - top, 3, 3, (255, 70, 90, 255)), glow=(5, 1.2))

    def serpent(self, y, x0, x1, h=40, col=(22, 32, 76)):
        """정부세종청사처럼 길게 굽이치는 건물."""
        pts_t, pts_b = [], []
        for i in range(61):
            t = i / 60
            x = x0 + (x1 - x0) * t
            yy = y + math.sin(t * math.pi * 2.2) * 18
            pts_t.append((x, yy - h))
            pts_b.append((x, yy))
        self.pen(lambda p: p.poly(pts_t + pts_b[::-1], col + (255,)))
        self.pen(lambda p: p.line(pts_t, (60, 200, 140, 230), 3))     # 옥상정원
        rng = self.rng
        self.pen(lambda p: [p.rect(x - 3, yy - h * 0.7, x + 3, yy - h * 0.45, LIGHT + (rng.randint(110, 220),))
                            for (x, yy) in pts_b[::2] if rng.random() < 0.6], glow=(3, 0.6))

    def dome(self, cx, base, r, col=(30, 40, 90), stripes=True, glow=False):
        def f(p):
            p.d.pieslice(((cx - r) * PA.S, (base - r) * PA.S, (cx + r) * PA.S, (base + r) * PA.S), 180, 360, fill=col + (255,))
            if stripes:
                for k in range(1, 6):
                    a = math.pi * k / 6
                    p.line([(cx, base - r), (cx - math.cos(a) * r, base - math.sin(a) * r * 0.05)], (80, 120, 220, 150), 1)
                p.line([(cx - r, base), (cx + r, base)], (120, 160, 255, 200), 1.6)
        self.pen(f, glow=(10, 0.6) if glow else None)

    def palace_gate(self, cx, base, w=380, h=150, col=(34, 34, 64)):
        """궁궐 문: 석축 + 홍예문 3개 + 2층 기와지붕."""
        def f(p):
            p.rect(cx - w / 2, base - h * 0.45, cx + w / 2, base, (44, 46, 78, 255))
            for k in (-1, 0, 1):
                ax = cx + k * w * 0.26
                p.rect(ax - 22, base - h * 0.32, ax + 22, base, (8, 10, 26, 255))
                p.ell(ax, base - h * 0.32, 22, 18, (8, 10, 26, 255))
            for k in range(14):
                p.line([(cx - w / 2, base - k * h * 0.032), (cx + w / 2, base - k * h * 0.032)], (60, 64, 100, 120), 0.6)
        self.pen(f)
        self.hanok(cx - w * 0.36, base - h * 0.45, w * 0.72, h * 0.22, wall=(60, 30, 40), roof=(16, 20, 44))
        self.hanok(cx - w * 0.26, base - h * 0.78, w * 0.52, h * 0.16, wall=(60, 30, 40), roof=(16, 20, 44))

    def fortress(self, y, x0=0, x1=W, col=(40, 44, 76)):
        def f(p):
            p.rect(x0, y - 50, x1, y, col + (255,))
            for x in range(int(x0), int(x1), 26):
                p.rect(x, y - 62, x + 16, y - 50, col + (255,))
            for r in range(5):
                off = 0 if r % 2 else 13
                for x in range(int(x0) - 26 + off, int(x1), 26):
                    p.rect(x + 1, y - 48 + r * 10, x + 25, y - 39 + r * 10, (52, 56, 92, 140))
        self.pen(f)

    def gate_tower(self, cx, base, w=200, h=120):
        def f(p):
            p.rect(cx - w / 2, base - h * 0.5, cx + w / 2, base, (48, 50, 84, 255))
            p.rect(cx - 26, base - h * 0.36, cx + 26, base, (8, 10, 26, 255))
            p.ell(cx, base - h * 0.36, 26, 20, (8, 10, 26, 255))
        self.pen(f)
        self.hanok(cx - w * 0.4, base - h * 0.5, w * 0.8, h * 0.26, wall=(70, 34, 44), roof=(16, 20, 44))

    # ---------------------------------------------------------- 놀이·행사
    def ferris(self, cx, cy, r, n=14):
        def f(p):
            p.line([(cx, cy), (cx - r * 0.5, cy + r * 1.25)], (30, 40, 80, 255), 4)
            p.line([(cx, cy), (cx + r * 0.5, cy + r * 1.25)], (30, 40, 80, 255), 4)
            p.d.ellipse(((cx - r) * PA.S, (cy - r) * PA.S, (cx + r) * PA.S, (cy + r) * PA.S), outline=(90, 130, 255, 230), width=3 * PA.S)
            for k in range(n):
                a = 2 * math.pi * k / n
                p.line([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], (60, 90, 200, 180), 1)
        self.pen(f)
        self.pen(lambda p: [p.ell(cx + math.cos(2 * math.pi * k / n) * r, cy + math.sin(2 * math.pi * k / n) * r, 6, 6,
                                  NEON[k % len(NEON)] + (255,)) for k in range(n)], glow=(6, 1.2))

    def coaster(self, x0, x1, base, amp=90):
        pts = [(x, base - 40 - amp * abs(math.sin((x - x0) / (x1 - x0) * math.pi * 2.5))) for x in range(int(x0), int(x1), 6)]

        def f(p):
            for x, y in pts[::4]:
                p.line([(x, y), (x, base)], (24, 30, 64, 255), 1.5)
            p.line(pts, (255, 90, 140, 240), 3)
        self.pen(f, glow=(4, 0.6))

    def string_lights(self, pts, cols=None, sag=14):
        cols = cols or NEON

        def f(p):
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                seg = [(xa + (xb - xa) * t / 10, ya + (yb - ya) * t / 10 + sag * math.sin(math.pi * t / 10)) for t in range(11)]
                p.line(seg, (40, 50, 90, 200), 1)
                for k, (x, y) in enumerate(seg[1:-1:2]):
                    p.ell(x, y + 3, 3, 3, cols[(k + int(xa)) % len(cols)] + (255,))
        self.pen(f, glow=(4, 1.0))

    def stalls(self, y, n=5, x0=40, x1=920):
        rng = self.rng
        w = (x1 - x0) / n
        for k in range(n):
            x = x0 + k * w
            col = rng.choice([(40, 60, 150), (120, 40, 70), (60, 40, 130), (30, 90, 120)])

            def f(p, x=x, col=col):
                p.rect(x + 8, y - 70, x + w - 8, y, (16, 20, 44, 255))
                p.poly([(x, y - 70), (x + w, y - 70), (x + w - 14, y - 100), (x + 14, y - 100)], col + (255,))
                for s in range(6):
                    if s % 2:
                        sx = x + 14 + (w - 28) * s / 6
                        p.poly([(sx, y - 100), (sx + (w - 28) / 6, y - 100), (sx + (w - 28) / 6 + 2, y - 70), (sx - 2, y - 70)],
                               (230, 230, 245, 90))
                p.rect(x + 14, y - 40, x + w - 14, y - 30, (60, 70, 120, 255))
            self.pen(f)
            self.pen(lambda p, x=x: p.ell(x + w / 2, y - 66, 26, 10, WARM + (90,)), blur=8)
            self.pen(lambda p, x=x: [p.ell(x + 22 + j * (w - 44) / 4, y - 46, 5, 4, rng.choice([ORANGE, PINK, (255, 80, 80), (140, 220, 120)]) + (255,))
                                     for j in range(5)])

    def stadium(self, cx, base, w=640, h=150, field=(20, 70, 50)):
        def f(p):
            p.ell(cx, base, w / 2, h * 0.5, (26, 30, 66, 255))
            p.ell(cx, base + 6, w * 0.4, h * 0.32, field + (255,))
            p.d.ellipse(((cx - w * 0.4) * PA.S, (base + 6 - h * 0.32) * PA.S, (cx + w * 0.4) * PA.S, (base + 6 + h * 0.32) * PA.S),
                        outline=(220, 240, 255, 150), width=PA.S)
            for k in range(-6, 7):
                p.line([(cx + k * w / 14, base - h * 0.48), (cx + k * w / 18, base - h * 0.28)], (60, 80, 150, 140), 1)
        self.pen(f)
        for fx in (cx - w * 0.45, cx + w * 0.45):
            self.pen(lambda p, fx=fx: (p.rect(fx - 2, base - h * 1.1, fx + 2, base - h * 0.3, (30, 36, 70, 255)),
                                       p.rect(fx - 18, base - h * 1.2, fx + 18, base - h * 1.08, (230, 240, 255, 255))), glow=(10, 1.3))
            self.light_cone(fx, base - h * 1.1, base, 120, alpha=30)

    def track(self, y):
        def f(p):
            p.poly([(0, y), (W, y), (W, H), (0, H)], (120, 40, 50, 255))
            for k in range(6):
                t = k / 6
                yy = y + (H - y) * t ** 1.3
                p.line([(0, yy), (W, yy)], (240, 240, 255, 200), 1.2 + 2 * t)
        self.pen(f)

    def field_rows(self, y, col=(20, 50, 40), row=(50, 110, 70), n=14, vx=480):
        def f(p):
            p.rect(0, y, W, H, col + (255,))
            for k in range(-n, n + 1):
                p.line([(vx, y), (vx + k * 90, H)], row + (200,), 2)
        self.pen(f)

    def paddy(self, y, gold=False):
        base = (60, 70, 30) if gold else (20, 50, 60)
        hi = (200, 190, 90) if gold else (60, 120, 140)

        def f(p):
            p.rect(0, y, W, H, base + (255,))
            for k in range(8):
                yy = y + (H - y) * (k / 8) ** 1.4
                p.line([(0, yy), (W, yy)], hi + (120,), 1 + k * 0.4)
            for x in range(0, W, 7):
                for k in range(1, 8):
                    yy = y + (H - y) * (k / 8) ** 1.4
                    p.line([(x, yy), (x + 2, yy - 4 - k)], hi + (150,), 0.8)
        self.pen(f)

    def lotus(self, y0, y1, n=40, flowers=True):
        rng = self.rng

        def f(p):
            for _ in range(n):
                y = rng.uniform(y0, y1)
                s = 0.5 + (y - y0) / (y1 - y0) * 1.2
                x = rng.uniform(0, W)
                p.ell(x, y, 22 * s, 7 * s, (24, 90, 70, 255))
                p.ell(x - 3 * s, y - 1, 14 * s, 3 * s, (60, 150, 110, 160))
                if flowers and rng.random() < 0.3:
                    p.poly([(x - 6 * s, y - 3), (x, y - 16 * s), (x + 6 * s, y - 3)], PINK + (255,))
        self.pen(f, glow=(2, 0.4))

    def ship(self, x, y, w=320, col=(30, 36, 70)):
        def f(p):
            p.poly([(x, y), (x + w, y), (x + w * 0.9, y + 40), (x + w * 0.08, y + 40)], col + (255,))
            p.rect(x + w * 0.6, y - 50, x + w * 0.85, y, (40, 48, 90, 255))
            p.rect(x + w * 0.66, y - 80, x + w * 0.74, y - 50, (60, 70, 120, 255))
            p.line([(x, y), (x + w, y)], (140, 170, 255, 220), 1.5)
        self.pen(f)
        self.pen(lambda p: [p.rect(x + w * 0.62 + k * 9, y - 40, x + w * 0.62 + k * 9 + 5, y - 34, LIGHT + (220,)) for k in range(4)],
                 glow=(3, 0.8))

    def boat(self, x, y, s=1.0, light=True):
        self.pen(lambda p: (p.poly([(x - 30 * s, y), (x + 30 * s, y), (x + 22 * s, y + 10 * s), (x - 22 * s, y + 10 * s)], (20, 24, 50, 255)),
                            p.rect(x - 6 * s, y - 16 * s, x + 8 * s, y, (36, 44, 90, 255))))
        if light:
            self.pen(lambda p: p.ell(x, y - 20 * s, 3, 3, WARM + (255,)), glow=(5, 1.0))

    def crane(self, x, base, h=260, arm=200, col=(40, 50, 100)):
        def f(p):
            p.rect(x - 5, base - h, x + 5, base, col + (255,))
            for k in range(int(h / 16)):
                p.line([(x - 5, base - k * 16), (x + 5, base - k * 16 - 16)], (70, 90, 160, 180), 0.8)
            p.rect(x - arm * 0.25, base - h - 6, x + arm, base - h, col + (255,))
            p.line([(x + arm * 0.8, base - h), (x + arm * 0.8, base - h + 90)], (120, 140, 200, 200), 1)
            p.rect(x + arm * 0.8 - 14, base - h + 90, x + arm * 0.8 + 14, base - h + 104, (90, 60, 50, 255))
        self.pen(f)
        self.pen(lambda p: p.ell(x, base - h - 10, 3, 3, (255, 60, 80, 255)), glow=(5, 1.2))

    def gantry(self, cx, base, w=420, h=230):
        def f(p):
            for xx in (cx - w / 2, cx + w / 2 - 22):
                p.rect(xx, base - h, xx + 22, base, (150, 40, 50, 255))
            p.rect(cx - w / 2 - 20, base - h - 26, cx + w / 2 + 20, base - h, (170, 50, 60, 255))
            p.line([(cx - w / 2, base - h - 13), (cx + w / 2, base - h - 13)], (255, 210, 210, 160), 1)
        self.pen(f)

    def bridge(self, y, towers=(300, 660), h=150, col=(40, 50, 100), lights=NEON):
        def f(p):
            p.rect(0, y, W, y + 10, col + (255,))
            for tx in towers:
                p.rect(tx - 8, y - h, tx + 8, y + 40, col + (255,))
            pts = [(0, y - h * 0.3)]
            for i, tx in enumerate(towers):
                pts.append((tx, y - h))
                if i + 1 < len(towers):
                    pts.append(((tx + towers[i + 1]) / 2, y - 14))
            pts.append((W, y - h * 0.3))
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                seg = [(xa + (xb - xa) * t / 12, ya + (yb - ya) * t / 12 + (25 * math.sin(math.pi * t / 12) if ya < yb or ya > yb else 0))
                       for t in range(13)]
                p.line(seg, (120, 160, 255, 220), 2)
                for x, yy in seg[::2]:
                    p.line([(x, yy), (x, y)], (80, 110, 200, 120), 0.7)
        self.pen(f)
        self.pen(lambda p: [p.ell(x, y + 4, 2.5, 2.5, lights[(x // 30) % len(lights)] + (255,)) for x in range(10, W, 30)], glow=(4, 1.0))

    def ring_bridge(self, cx, cy, rx, ry):
        def f(p):
            p.d.ellipse(((cx - rx) * PA.S, (cy - ry) * PA.S, (cx + rx) * PA.S, (cy + ry) * PA.S), outline=(60, 80, 150, 255), width=12 * PA.S)
            p.d.ellipse(((cx - rx) * PA.S, (cy - ry) * PA.S, (cx + rx) * PA.S, (cy + ry) * PA.S), outline=(140, 180, 255, 230), width=2 * PA.S)
        self.pen(f, glow=(6, 0.6))
        self.pen(lambda p: [p.ell(cx + math.cos(a / 10) * rx, cy + math.sin(a / 10) * ry, 2.6, 2.6, LIGHT + (255,)) for a in range(0, 63, 3)],
                 glow=(4, 1.0))

    def statue(self, x, base, h=150, col=(30, 34, 70)):
        def f(p):
            p.rect(x - 34, base - h * 0.35, x + 34, base, (44, 48, 90, 255))
            p.poly([(x - 22, base - h * 0.35), (x + 22, base - h * 0.35), (x + 14, base - h * 0.8), (x - 14, base - h * 0.8)], col + (255,))
            p.ell(x, base - h * 0.88, 12, 13, col + (255,))
        self.pen(f)
        self.light_cone(x, base - h, base, 60, alpha=35)

    def plane(self, x, y, s=1.0):
        self.pen(lambda p: (p.poly([(x - 60 * s, y), (x + 60 * s, y - 4 * s), (x + 66 * s, y), (x + 60 * s, y + 4 * s)], (200, 210, 240, 255)),
                            p.poly([(x - 6 * s, y), (x + 14 * s, y), (x - 20 * s, y + 30 * s), (x - 34 * s, y + 30 * s)], (170, 180, 220, 255)),
                            p.poly([(x - 6 * s, y), (x + 14 * s, y), (x - 20 * s, y - 30 * s), (x - 34 * s, y - 30 * s)], (170, 180, 220, 255)),
                            p.poly([(x - 56 * s, y), (x - 44 * s, y), (x - 60 * s, y - 18 * s)], (170, 180, 220, 255))))
        self.pen(lambda p: (p.ell(x + 62 * s, y, 3, 3, (255, 60, 80, 255)), p.ell(x - 60 * s, y - 18 * s, 3, 3, (120, 255, 160, 255))), glow=(5, 1.2))

    def paifang(self, cx, base, w=360, h=220):
        """차이나타운 패루 (붉은 기둥 + 겹지붕)."""
        def f(p):
            for k in (-1, -0.36, 0.36, 1):
                xx = cx + k * w / 2
                p.rect(xx - 9, base - h * 0.75, xx + 9, base, (150, 30, 40, 255))
            p.rect(cx - w / 2 - 20, base - h * 0.8, cx + w / 2 + 20, base - h * 0.7, (170, 40, 50, 255))
            p.rect(cx - 60, base - h * 0.95, cx + 60, base - h * 0.8, (200, 160, 60, 255))
            for yy, ww in ((base - h * 0.8, w / 2 + 40), (base - h * 0.97, 90)):
                p.poly([(cx - ww, yy), (cx + ww, yy), (cx + ww - 20, yy - 24), (cx - ww + 20, yy - 24)], (20, 60, 70, 255))
        self.pen(f)
        self.pen(lambda p: [p.ell(cx + k * 70, base - h * 0.6, 12, 15, (255, 60, 60, 255)) for k in (-2, -1, 1, 2)], glow=(8, 1.0))

    def hedges(self, y, col=(20, 60, 50)):
        def f(p):
            p.rect(0, y, W, H, (30, 30, 50, 255))
            for k in range(7):
                t = k / 7
                yy = y + (H - y) * t ** 1.5
                hh = 10 + 40 * t
                p.rect(0, yy - hh, W * (0.3 + 0.1 * (k % 3)), yy, col + (255,))
                p.rect(W * (0.45 + 0.08 * ((k + 1) % 3)), yy - hh, W, yy, col + (255,))
                p.line([(0, yy - hh), (W, yy - hh)], (60, 130, 100, 120), 1)
        self.pen(f)

    def volcano(self, peak_x, top, base, w=700, col=HILL_MID):
        pts = [(peak_x - w / 2, base), (peak_x - 90, top + 20), (peak_x - 40, top), (peak_x + 40, top), (peak_x + 90, top + 20),
               (peak_x + w / 2, base)]
        self.pen(lambda p: p.poly(pts + [(peak_x + w / 2, H), (peak_x - w / 2, H)], col + (255,)))
        self.pen(lambda p: p.line(pts[1:-1], (200, 220, 255, 220), 2))
        self.pen(lambda p: p.poly([(peak_x - 90, top + 20), (peak_x - 40, top), (peak_x + 40, top), (peak_x + 90, top + 20),
                                   (peak_x + 60, top + 40), (peak_x - 60, top + 40)], (210, 225, 255, 180)), blur=1)

    def fountain(self, cx, base):
        self.pen(lambda p: p.ell(cx, base, 120, 18, (30, 50, 110, 255)))
        for k in range(-3, 4):
            self.pen(lambda p, k=k: p.line([(cx + k * 14, base), (cx + k * 22, base - 70 + abs(k) * 12), (cx + k * 30, base - 10)],
                                           (140, 200, 255, 200), 2), glow=(6, 1.0))

    def bookshelf_wall(self, y0, y1):
        rng = self.rng

        def f(p):
            p.rect(0, y0, W, y1, (20, 18, 40, 255))
            for r in range(int((y1 - y0) / 40)):
                yy = y0 + r * 40
                p.rect(0, yy + 36, W, yy + 40, (50, 40, 70, 255))
                x = 0
                while x < W:
                    bw = rng.uniform(6, 14)
                    p.rect(x, yy + rng.uniform(4, 12), x + bw, yy + 36, rng.choice([(40, 60, 130), (90, 40, 60), (40, 90, 90), (70, 60, 120)]) + (255,))
                    x += bw + 1
        self.pen(f)

    def terminal(self, x, base, w, h, col=(24, 34, 80)):
        def f(p):
            p.poly([(x, base), (x, base - h), (x + w * 0.5, base - h - 30), (x + w, base - h), (x + w, base)], col + (255,))
            for k in range(int(w / 20)):
                p.line([(x + k * 20, base - h + 4), (x + k * 20, base)], (80, 120, 220, 140), 1)
        self.pen(f)
        self.pen(lambda p: p.rect(x + 10, base - h * 0.6, x + w - 10, base - h * 0.3, LIGHT + (120,)), glow=(6, 0.8))

    def bus(self, x, base, col=(40, 90, 200), w=150):
        def f(p):
            p.rect(x, base - 50, x + w, base - 8, col + (255,), r=6)
            for k in range(5):
                p.rect(x + 10 + k * (w - 20) / 5, base - 44, x + 4 + (k + 1) * (w - 20) / 5, base - 28, (190, 220, 255, 220))
            p.ell(x + 26, base - 6, 10, 10, (10, 10, 20, 255))
            p.ell(x + w - 26, base - 6, 10, 10, (10, 10, 20, 255))
        self.pen(f, glow=(3, 0.3))

    def blossoms(self, xs, base, h, col=PINK):
        for x in xs:
            self.round_tree(x, base, h, col=(70, 40, 80), hi=(150, 90, 150), fruits=40, fruit_col=col)

    def petals(self, n=80, col=PINK):
        rng = self.rng
        self.pen(lambda p: [p.ell(rng.uniform(0, W), rng.uniform(80, H), 2.2, 1.4, col + (rng.randint(120, 230),)) for _ in range(n)],
                 glow=(2, 0.6))

    def tangerines(self, xs, base, h):
        for x in xs:
            self.round_tree(x, base, h, fruits=26, fruit_col=ORANGE)


# ================================================================== 세종시 40곳
def s01(c):   # 세종호수공원 수상무대
    c.sky(); c.stars(); c.moon(820, 70)
    c.apartment(40, 290, 90, 120); c.apartment(150, 290, 70, 90); c.glass(700, 290, 80, 140); c.glass(800, 290, 120, 100)
    c.water(290, 540, lights=[(480, LIGHT), (300, (255, 120, 200)), (660, (120, 220, 255))])
    c.pen(lambda p: (p.ell(480, 380, 210, 34, (30, 40, 90, 255)), p.rect(330, 300, 630, 370, (24, 30, 70, 255))))
    c.pen(lambda p: p.d.arc((330 * 2, 220 * 2, 630 * 2, 420 * 2), 180, 360, fill=(120, 160, 255, 255), width=8), glow=(8, 1.0))
    c.string_lights([(330, 300), (480, 286), (630, 300)])
    for x in (380, 430, 530, 580):
        c.light_cone(x, 300, 380, 40, (180, 120, 255), 40)


def s02(c):   # 국립세종수목원: 온실 + 단풍
    c.sky(top=(8, 10, 28), low=(60, 40, 90)); c.stars(60); c.moon(150, 70)
    c.hills(300, 30, HILL_FAR, 4)
    c.dome(480, 330, 150, (30, 60, 90), glow=True); c.dome(270, 340, 80, (28, 54, 84)); c.dome(690, 340, 80, (28, 54, 84))
    c.ground(330, (16, 30, 40))
    for x in (60, 150, 820, 910):
        c.round_tree(x, 420, 170, col=(110, 40, 30), hi=(200, 90, 50), fruits=20, fruit_col=(255, 120, 60))
    c.lamp(380, 440); c.lamp(580, 440)


def s03(c):   # 부강 오일장
    c.sky(); c.stars(); c.moon(760, 60)
    c.hills(280, 40, HILL_FAR, 5); c.house(60, 300, 120, 80); c.house(780, 300, 120, 80)
    c.ground(300, (22, 24, 50))
    c.stalls(440, 5)
    c.string_lights([(0, 250), (240, 240), (480, 250), (720, 240), (960, 250)], [WARM, ORANGE, (255, 120, 120)])
    c.people(18, 450, 540)


def s04(c):   # 로컬푸드 직매장
    c.sky(); c.stars(); c.moon(140, 70)
    c.glass(260, 360, 440, 120, (24, 40, 70), lit=0.7)
    c.sign(380, 205, 200, 30, (60, 200, 120))
    c.ground(360, (20, 26, 50))
    c.pen(lambda p: [p.rect(80 + k * 170, 430, 220 + k * 170, 470, (90, 60, 40, 255)) for k in range(5)])
    c.pen(lambda p: [p.ell(95 + k * 170 + j * 26, 425, 11, 10, (255, 150, 160, 255)) for k in range(5) for j in range(5)], glow=(2, 0.4))
    c.lamp(60, 470); c.lamp(900, 470)


def s05(c):   # 나성동 카페거리
    c.sky(); c.stars(); c.moon(480, 60)
    c.glass(0, 400, 200, 260, (20, 30, 70)); c.glass(760, 400, 200, 280, (20, 30, 70))
    c.glass(220, 400, 160, 180, (26, 34, 78)); c.glass(580, 400, 160, 200, (26, 34, 78))
    c.road(480, 300, 600)
    for x, col in ((240, WARM), (300, (255, 140, 180)), (620, (120, 220, 255)), (690, WARM)):
        c.sign(x, 330, 50, 18, col)
    c.string_lights([(200, 260), (480, 250), (760, 260)], [WARM])
    c.people(10, 430, 540)


def s06(c):   # 합강 오토캠핑장: 강변 + 텐트 + 모닥불
    c.sky(); c.stars(); c.moon(760, 70)
    c.hills(250, 50, HILL_FAR, 6)
    c.water(270, 330, lights=[(760, LIGHT)])
    c.ground(330, (20, 34, 40))
    for k, (x, col) in enumerate(((90, (60, 90, 170)), (300, (170, 70, 90)), (640, (60, 130, 120)), (840, (120, 80, 170)))):
        c.pen(lambda p, x=x, col=col: (p.poly([(x - 70, 440), (x + 70, 440), (x, 350)], col + (255,)),
                                         p.poly([(x - 14, 440), (x + 14, 440), (x, 395)], (14, 16, 30, 255))))
        c.pen(lambda p, x=x: p.ell(x, 418, 40, 26, WARM + (60,)), blur=10)
    c.pen(lambda p: (p.ell(480, 470, 46, 10, (40, 30, 30, 255)), p.poly([(462, 470), (498, 470), (480, 420)], (255, 150, 60, 255)),
                     p.poly([(470, 470), (490, 470), (480, 440)], (255, 230, 140, 255))), glow=(14, 1.2))
    c.string_lights([(0, 300), (300, 320), (640, 320), (960, 300)], [WARM, (255, 160, 120)])


def s07(c):   # 국립세종도서관 (책 펼친 모양 건물)
    c.sky(); c.stars(); c.moon(840, 70)
    c.water(400, 540, lights=[(480, LIGHT)])
    c.pen(lambda p: p.poly([(220, 400), (480, 230), (740, 400)], (24, 34, 80, 255)))
    c.pen(lambda p: [p.line([(220 + k * 26, 400), (480, 230)], (90, 130, 230, 160), 1) for k in range(21)])
    c.pen(lambda p: p.line([(220, 400), (480, 230), (740, 400)], (160, 200, 255, 255), 3), glow=(6, 0.8))
    c.pen(lambda p: p.rect(380, 360, 580, 400, LIGHT + (150,)), glow=(8, 0.8))


def s08(c):   # 대통령기록관 (정육면체 건물)
    c.sky(); c.stars(); c.moon(160, 70)
    c.pen(lambda p: (p.rect(300, 140, 660, 400, (22, 30, 70, 255)),))
    c.pen(lambda p: [p.rect(310 + k * 18, 150, 318 + k * 18, 390, (60, 90, 170, 200)) for k in range(20)])
    c.pen(lambda p: p.rect(440, 330, 520, 400, LIGHT + (200,)), glow=(10, 1.0))
    c.ground(400, (16, 20, 44))
    c.lamp(260, 470); c.lamp(700, 470)


def s09(c):   # 연동면 고구마밭
    c.sky(); c.stars(); c.moon(760, 70)
    c.hills(280, 50, HILL_FAR, 9); c.hills(320, 30, HILL_MID, 10)
    c.house(80, 330, 110, 70)
    c.field_rows(330, (40, 30, 30), (90, 60, 50))
    c.pen(lambda p: [p.ell(x, 420 + (x % 5) * 20, 10, 7, (150, 60, 100, 255)) for x in range(60, 960, 90)])


def s10(c):   # 금강 둔치 마라톤
    c.sky(); c.stars(); c.moon(200, 60)
    c.glass(560, 260, 80, 120); c.glass(660, 260, 60, 90); c.apartment(740, 260, 90, 110)
    c.water(260, 330, lights=[(600, LIGHT)])
    c.ground(330, (20, 34, 40))
    c.track(400)
    c.pen(lambda p: [p.rect(x, 380, x + 6, 410, (230, 230, 255, 255)) for x in (200, 480, 760)])


def s11(c):   # 방축천 벚꽃길
    c.sky(top=(10, 8, 34), low=(70, 40, 100)); c.stars(); c.moon(480, 70)
    c.apartment(0, 300, 120, 150); c.apartment(840, 300, 120, 160)
    c.water(380, 470, lights=[(480, PINK)])
    c.ground(300, (24, 22, 50)); c.water(380, 460, lights=[(480, PINK)])
    c.blossoms((120, 260, 700, 840), 380, 220)
    c.petals()
    c.fountain(480, 440)


def s12(c):   # 합강정 연꽃 습지
    c.sky(); c.stars(); c.moon(760, 80)
    c.hills(270, 40, HILL_FAR, 12)
    c.hanok(380, 300, 200, 60)
    c.water(300, 540, lights=[(480, WARM)])
    c.lotus(330, 540, 50)


def s13(c):   # 정부세종청사
    c.sky(); c.stars(); c.moon(860, 60)
    c.serpent(360, 0, 960, 70)
    c.ground(380, (16, 22, 46))
    c.pen(lambda p: [p.rect(80 + k * 120, 430, 84 + k * 120, 470, (60, 70, 120, 255)) for k in range(8)])
    c.lamp(240, 480); c.lamp(720, 480)


def s14(c):   # 세종예술의전당
    c.sky(); c.stars(); c.moon(140, 60)
    c.pen(lambda p: p.poly([(200, 380), (300, 200), (660, 200), (760, 380)], (26, 30, 70, 255)))
    c.pen(lambda p: [p.line([(300 + k * 24, 200), (200 + k * 37, 380)], (90, 120, 230, 150), 1) for k in range(16)])
    c.sign(380, 230, 200, 26, (180, 120, 255))
    c.ground(380, (18, 20, 46))
    c.string_lights([(160, 300), (480, 290), (800, 300)])
    c.people(14, 420, 540)


def s15(c):   # 금강 세종보
    c.sky(); c.stars(); c.moon(700, 70)
    c.hills(260, 30, HILL_FAR, 15)
    c.pen(lambda p: (p.rect(0, 270, W, 300, (40, 50, 90, 255)), [p.rect(30 + k * 100, 240, 70 + k * 100, 300, (50, 60, 110, 255)) for k in range(10)]))
    c.water(300, 540, lights=[(200, LIGHT), (700, LIGHT)])
    c.boat(260, 420, 1.2)


def s16(c):   # 원수산 전망대 계단
    PA.p16(c)
    c.pen(lambda p: (p.rect(440, 160, 520, 230, (30, 40, 90, 255)), p.rect(470, 120, 490, 160, (30, 40, 90, 255))))
    c.pen(lambda p: p.rect(450, 170, 510, 190, LIGHT + (200,)), glow=(6, 1.0))


def s17(c):   # 이응다리
    c.sky(); c.stars(); c.moon(840, 60)
    c.glass(60, 280, 70, 90); c.glass(140, 280, 50, 120); c.apartment(760, 280, 90, 100)
    c.water(280, 540, lights=[(480, LIGHT)])
    c.ring_bridge(480, 330, 330, 60)


def s18(c):   # 전의면 마을회관
    PA.p18(c)
    c.string_lights([(0, 220), (480, 200), (960, 220)], [WARM])


def s19(c):   # 고운뜰공원 놀이마당
    c.sky(); c.stars(); c.moon(160, 70)
    c.apartment(600, 300, 110, 160); c.apartment(720, 300, 110, 130); c.apartment(840, 300, 110, 170)
    c.ground(300, (18, 28, 46))
    c.pen(lambda p: (p.ell(480, 440, 70, 22, (90, 70, 50, 255)), p.rect(450, 360, 510, 440, (120, 90, 60, 255)),
                     p.ell(480, 360, 30, 10, (40, 30, 30, 255))))
    c.string_lights([(0, 200), (480, 240), (960, 200)], [(255, 90, 90), (90, 160, 255), (255, 220, 90)])
    c.people(10, 430, 540)


def s20(c):   # 정부청사 옥상정원
    c.sky(top=(8, 12, 30), low=(40, 70, 110)); c.stars(); c.moon(480, 60)
    c.serpent(250, -60, 1020, 30)
    c.pen(lambda p: p.rect(0, 300, W, H, (20, 50, 46, 255)))
    for x in range(40, 960, 110):
        c.round_tree(x, 360 + (x % 3) * 20, 120)
    c.pen(lambda p: p.poly([(430, 540), (530, 540), (500, 300), (460, 300)], (60, 64, 100, 255)))


def s21(c):   # 중앙공원 운동장
    c.sky(); c.stars()
    c.apartment(0, 260, 140, 120); c.apartment(820, 260, 140, 130)
    c.stadium(480, 360, 820, 200, (24, 80, 50))


def s22(c):   # 개미고개
    PA.p22(c)


def s23(c):   # 명학 산업단지
    c.sky(top=(10, 12, 30), low=(60, 50, 90)); c.stars(40)
    c.pen(lambda p: [p.rect(x, 260, x + 160, 380, (26, 30, 64, 255)) for x in (40, 380, 720)])
    c.pen(lambda p: [p.poly([(x, 260), (x + 40, 230), (x + 80, 260), (x + 120, 230), (x + 160, 260)], (34, 40, 80, 255)) for x in (40, 380, 720)])
    c.pen(lambda p: [p.rect(x + 120, 160, x + 140, 260, (40, 46, 90, 255)) for x in (40, 720)])
    c.pen(lambda p: [p.ell(x + 130, 140, 40, 18, (120, 130, 180, 60)) for x in (40, 720)], blur=10)
    c.crane(600, 380, 240, 160)
    c.ground(380, (24, 26, 50))
    c.pen(lambda p: [p.rect(100 + k * 60, 440 - (k % 3) * 30, 150 + k * 60, 480, (110, 80, 50, 255)) for k in range(12)])


def s24(c):   # 국책연구단지
    c.sky(); c.stars(); c.moon(820, 70)
    c.glass(80, 380, 200, 160, (20, 34, 80), lit=0.6); c.glass(320, 380, 300, 220, (22, 36, 86), lit=0.5, top=40)
    c.glass(660, 380, 220, 140, (20, 34, 80), lit=0.6)
    c.dome(780, 240, 50, (40, 50, 100))
    c.ground(380, (16, 22, 46))


def s25(c):   # 금남면 대평리 마을
    PA.p25(c)


def s26(c):   # 어반아트리움 상가거리
    c.sky(); c.stars(40)
    c.glass(0, 420, 260, 320, (18, 26, 64)); c.glass(700, 420, 260, 330, (18, 26, 64))
    c.pen(lambda p: (p.rect(260, 160, 700, 190, (40, 60, 130, 220)),))
    c.road(480, 330, 520, dashes=False)
    for k, x in enumerate((40, 120, 760, 860)):
        c.sign(x, 200 + k * 30, 70, 18, NEON[k])
    c.people(30, 380, 540)


def s27(c):   # 연동면 복숭아 농원
    PA.p27(c)


def s28(c):   # 전월산 숲길
    PA.p20(c)
    c.fog(380, 80, 70)


def s29(c):   # 장군면 들녘
    c.sky(); c.stars(); c.moon(700, 70)
    c.hills(260, 50, HILL_FAR, 29)
    c.house(100, 280, 90, 60); c.house(800, 280, 90, 60)
    c.paddy(290)
    c.pen(lambda p: p.poly([(470, 290), (490, 290), (560, 540), (400, 540)], (60, 110, 200, 255)))


def s30(c):   # 괴화산 정자: 능선 위 정자
    c.sky(); c.stars(); c.moon(800, 90)
    c.mountains(330, [(80, 90), (260, 150), (480, 220), (700, 160), (880, 110)], HILL_FAR)
    c.hills(400, 40, HILL_MID, 30)
    c.hanok(420, 270, 120, 46, wall=(60, 40, 40))
    c.pen(lambda p: p.poly([(430, 540), (530, 540), (500, 400), (470, 400)], (70, 60, 70, 255)))
    for x in (120, 220, 760, 860):
        c.pine(x, 470, 170)


def s31(c):   # 금남면 들판
    PA.p31(c)


def s32(c):   # 연동면 옛 분교
    PA.p32(c)


def s33(c):   # 미호천 징검다리
    PA.p33(c)


def s34(c):   # 금강 자전거길
    PA.p34(c)


def s35(c):   # 세종 BRT 정류장
    c.sky(); c.stars()
    c.glass(0, 340, 300, 220); c.glass(660, 340, 300, 200)
    c.ground(340, (20, 24, 50))
    c.road(480, 340, 900)
    c.pen(lambda p: (p.rect(300, 330, 660, 340, (120, 160, 255, 255)), [p.rect(320 + k * 80, 270, 326 + k * 80, 330, (60, 80, 150, 255)) for k in range(5)],
                     p.rect(300, 262, 660, 272, (60, 80, 150, 255))))
    c.bus(380, 470, (40, 120, 220), 200)


def s36(c):   # 세종시청
    c.sky(); c.stars(); c.moon(820, 60)
    c.pen(lambda p: (p.rect(180, 170, 780, 400, (24, 32, 76, 255)), p.ell(480, 170, 200, 30, (40, 56, 120, 255))))
    c.pen(lambda p: [p.rect(200 + k * 36, 200, 220 + k * 36, 390, (60, 90, 180, 160)) for k in range(16)])
    c.sign(400, 330, 160, 26, (110, 150, 255))
    c.ground(400, (16, 20, 44))
    c.people(12, 430, 540)


def s37(c):   # 금남 떡방앗간
    PA.p37(c)


def s38(c):   # 도담동 상가거리
    PA.p38(c)


def s39(c):   # 아름동 학원가
    c.sky(); c.stars(30)
    c.apartment(0, 420, 300, 300, lit=0.6); c.apartment(660, 420, 300, 300, lit=0.6)
    for k in range(6):
        c.sign(20 + (k % 2) * 140, 160 + k * 40, 110, 20, NEON[k % 5])
        c.sign(680 + (k % 2) * 140, 140 + k * 42, 110, 20, NEON[(k + 2) % 5])
    c.road(480, 300, 500)
    c.bus(400, 470, (230, 190, 60), 160)


def s40(c):   # 부강역 철길 건널목
    PA.p40(c)
    c.pen(lambda p: (p.rect(380, 230, 580, 300, (30, 36, 70, 255)), p.poly([(370, 230), (590, 230), (480, 200)], (24, 28, 60, 255))))
    c.sign(430, 245, 100, 16, (110, 150, 255))


# ================================================================== 전국 40곳
def k01(c):   # 홍대
    c.sky(top=(14, 6, 30), low=(80, 30, 90)); c.stars(30)
    c.glass(0, 420, 220, 330, (24, 18, 54)); c.glass(740, 420, 220, 330, (24, 18, 54))
    for k in range(8):
        c.sign(10 + (k % 2) * 110, 120 + k * 34, 90, 18, NEON[k % 5])
        c.sign(750 + (k % 2) * 110, 110 + k * 36, 90, 18, NEON[(k + 3) % 5])
    c.road(480, 300, 520, dashes=False)
    c.pen(lambda p: p.rect(380, 360, 580, 380, (40, 40, 80, 255)))
    c.light_cone(400, 120, 380, 60, (255, 90, 160), 50); c.light_cone(560, 120, 380, 60, (90, 160, 255), 50)
    c.people(30, 400, 540)


def k02(c):   # 제주 감귤 과수원
    c.sky(top=(8, 14, 34), low=(60, 60, 110)); c.stars(); c.moon(820, 70)
    c.volcano(300, 170, 330, 800, HILL_FAR)
    c.ground(330, (20, 36, 34))
    c.pen(lambda p: [p.rect(0, y, W, y + 10, (50, 50, 60, 255)) for y in (340,)])   # 돌담
    c.tangerines((80, 230, 380, 580, 730, 880), 470, 170)
    c.pen(lambda p: [p.ell(x, 500, 10, 9, ORANGE + (255,)) for x in range(40, 960, 70)], glow=(3, 0.5))


def k03(c):   # 자갈치시장
    c.sky(); c.stars(); c.moon(140, 60)
    c.water(260, 340, lights=[(300, LIGHT), (700, WARM)])
    c.boat(200, 300, 1.4); c.boat(700, 300, 1.2)
    c.ground(340, (24, 26, 50))
    c.stalls(470, 6)
    c.pen(lambda p: [p.ell(60 + k * 150, 445, 28, 8, (120, 160, 210, 255)) for k in range(6)])
    c.people(14, 480, 540)


def k04(c):   # 청도 복숭아밭
    PA.p23(c)


def k05(c):   # 강릉 커피거리
    c.sky(top=(8, 12, 34), low=(40, 70, 130)); c.stars(); c.moon(760, 70)
    c.water(260, 380, lights=[(760, LIGHT)])
    c.pen(lambda p: p.rect(0, 380, W, 420, (60, 56, 70, 255)))
    for x in (40, 240, 600, 800):
        c.house(x, 520, 140, 90, wall=(30, 30, 60))
    for x, col in ((60, WARM), (270, (255, 160, 120)), (620, WARM), (820, (180, 140, 100))):
        c.sign(x, 400, 90, 16, col)


def k06(c):   # 용인 놀이공원
    c.sky(top=(12, 8, 34), low=(60, 30, 100)); c.stars()
    c.ferris(250, 220, 130, 16)
    c.coaster(420, 960, 400, 140)
    c.pen(lambda p: (p.rect(560, 300, 700, 400, (40, 30, 80, 255)), p.poly([(540, 300), (720, 300), (630, 220)], (90, 40, 120, 255))))
    c.ground(400, (20, 18, 46))
    c.string_lights([(0, 380), (480, 360), (960, 380)])
    c.people(14, 440, 540)


def k07(c):   # 광화문광장
    c.sky(); c.stars(); c.moon(840, 60)
    c.mountains(240, [(300, 80), (480, 140), (680, 90)], HILL_FAR)
    c.palace_gate(480, 380, 420, 190)
    c.ground(380, (24, 26, 52))
    c.statue(220, 480, 170); c.statue(740, 480, 150)


def k08(c):   # 제주 김녕 미로공원
    c.sky(); c.stars(); c.moon(480, 60)
    c.water(260, 290, lights=[(480, LIGHT)])
    c.hedges(290)


def k09(c):   # 평창 감자밭
    c.sky(); c.stars(); c.moon(200, 70)
    c.mountains(280, [(80, 150), (260, 200), (480, 160), (700, 220), (880, 170)], HILL_FAR)
    c.pen(lambda p: [p.line([(x, 120), (x, 280)], (200, 210, 240, 200), 2) for x in (620, 760)])     # 풍력발전기
    c.pen(lambda p: [p.line([(x, 120), (x + 40 * math.cos(a), 120 + 40 * math.sin(a))], (200, 210, 240, 220), 3)
                     for x in (620, 760) for a in (0.3, 2.4, 4.5)])
    c.field_rows(300, (40, 32, 26), (80, 70, 50))
    c.pen(lambda p: [p.ell(x, 400 + (x % 7) * 15, 9, 7, (170, 140, 90, 255)) for x in range(50, 960, 80)])


def k10(c):   # 춘천 호반
    c.sky(); c.stars(); c.moon(820, 70)
    c.mountains(260, [(100, 100), (300, 140), (600, 110), (840, 130)], HILL_FAR)
    c.water(270, 360, lights=[(820, LIGHT)])
    c.ground(360, (20, 34, 40))
    c.track(420)
    c.string_lights([(0, 300), (480, 320), (960, 300)])


def k11(c):   # 진해 군항제
    c.sky(top=(12, 8, 34), low=(80, 50, 110)); c.stars(); c.moon(480, 60)
    c.water(360, 440, lights=[(480, PINK)])
    c.pen(lambda p: [p.rect(240 + k * 140, 340, 330 + k * 140, 360, (60, 60, 90, 255)) for k in range(4)])
    c.blossoms((90, 230, 730, 870), 380, 240)
    c.blossoms((330, 630), 360, 160)
    c.ground(440, (30, 22, 50))
    c.petals(120)


def k12(c):   # 부여 궁남지
    c.sky(); c.stars(); c.moon(760, 60)
    c.water(280, 540, lights=[(480, WARM)])
    c.pen(lambda p: (p.ell(480, 330, 120, 30, (30, 40, 70, 255)), p.rect(470, 330, 490, 380, (60, 50, 70, 255))))
    c.pen(lambda p: [p.line([(480 - 300 + t * 12, 330 + abs(t - 25) * 0.6), (480 - 300 + t * 12 + 12, 330)], (120, 60, 70, 255), 3) for t in (0,)])
    c.hanok(410, 300, 140, 40, wall=(70, 34, 44))
    c.lotus(360, 540, 60)


def k13(c):   # 대전 카이스트
    c.sky(); c.stars(); c.moon(140, 60)
    c.glass(260, 380, 180, 180, (20, 34, 80), lit=0.7); c.glass(480, 380, 240, 240, (22, 36, 86), lit=0.6, top=50)
    c.dome(820, 380, 90, (34, 44, 96), glow=True)
    c.pen(lambda p: [p.line([(820, 290), (820 + 140 * math.cos(a), 290 - 140 * math.sin(a))], (90, 160, 255, 70), 1) for a in (0.6, 1.2, 1.9, 2.5)])
    c.ground(380, (16, 24, 46))
    for x in (80, 180):
        c.round_tree(x, 440, 160)


def k14(c):   # 신촌 연세로
    c.sky(); c.stars(30)
    c.glass(0, 400, 240, 280, (20, 26, 60)); c.glass(720, 400, 240, 290, (20, 26, 60))
    c.road(480, 310, 600)
    c.string_lights([(240, 220), (480, 240), (720, 220)], [(70, 110, 255), (220, 40, 60)])
    c.sign(260, 260, 100, 22, (70, 110, 255)); c.sign(600, 260, 100, 22, (220, 40, 60))
    c.people(24, 400, 540)


def k15(c):   # 통영항
    c.sky(); c.stars(); c.moon(820, 70)
    c.hills(260, 50, HILL_FAR, 51)
    for k in range(10):
        c.house(40 + k * 92, 290 - (k % 3) * 20, 60, 40)
    c.water(300, 540, lights=[(200, WARM), (520, LIGHT), (800, WARM)])
    c.boat(200, 400, 1.5); c.boat(560, 440, 1.8); c.boat(800, 380, 1.2)


def k16(c):   # 한라산
    c.sky(top=(6, 10, 30), low=(40, 60, 120)); c.stars(140, 0.6); c.moon(160, 80)
    c.volcano(560, 130, 360, 900, HILL_FAR)
    c.hills(400, 30, HILL_MID, 16)
    for x in (60, 140, 820, 900):
        c.pine(x, 460, 160)

    def steps(p):
        for k in range(12):
            t0, t1 = k / 12, (k + 1) / 12
            y0, y1 = H - (H - 330) * t0, H - (H - 330) * t1
            w0, w1 = 320 * (1 - t0 * 0.8), 320 * (1 - t1 * 0.8)
            p.poly([(480 - w0 / 2, y0), (480 + w0 / 2, y0), (480 + w1 / 2, y1), (480 - w1 / 2, y1)], (60, 50, 50, 255))
            p.line([(480 - w1 / 2, y1), (480 + w1 / 2, y1)], (160, 150, 200, 220), 1.4)
    c.pen(steps)


def k17(c):   # 광안리
    c.sky(top=(6, 8, 30), low=(30, 40, 110)); c.stars()
    c.glass(0, 300, 90, 200); c.glass(100, 300, 70, 160); c.glass(820, 300, 140, 220)
    c.water(300, 440, lights=[(300, (255, 90, 160)), (600, (90, 160, 255))])
    c.bridge(300, (260, 700), 170)
    c.pen(lambda p: p.rect(0, 440, W, H, (60, 56, 76, 255)))
    c.pen(lambda p: [p.ell(200 + (k * 37) % 560, 90 + (k * 23) % 120, 2.5, 2.5, NEON[k % 5] + (255,)) for k in range(60)], glow=(4, 1.2))


def k18(c):   # 안동 하회마을
    c.sky(); c.stars(); c.moon(800, 70)
    c.hills(250, 60, HILL_FAR, 18)
    c.water(270, 320, lights=[(800, LIGHT)])
    c.ground(320, (30, 30, 46))
    c.hanok(60, 420, 260, 80); c.hanok(620, 430, 280, 90)
    c.pen(lambda p: [p.rect(x, 400, x + 120, 440, (50, 46, 60, 255)) for x in (360,)])
    c.round_tree(470, 420, 220, col=(26, 50, 50))


def k19(c):   # 경복궁
    c.sky(); c.stars(); c.moon(160, 70)
    c.mountains(220, [(200, 70), (480, 120), (760, 80)], HILL_FAR)
    c.ground(330, (40, 38, 60))
    c.palace_gate(480, 330, 520, 200)
    c.pen(lambda p: [p.rect(0, 330 + k * 30, W, 332 + k * 30, (60, 58, 80, 200)) for k in range(7)])
    c.lamp(120, 500); c.lamp(840, 500)


def k20(c):   # 순천만 국가정원
    c.sky(top=(8, 12, 30), low=(50, 70, 110)); c.stars(); c.moon(760, 70)
    c.hills(280, 40, HILL_FAR, 20)
    c.paddy(300, gold=True)
    c.pen(lambda p: p.poly([(0, 470), (300, 420), (660, 440), (960, 400), (960, 540), (0, 540)], (30, 50, 110, 255)))
    c.pen(lambda p: p.line([(0, 480), (300, 430), (660, 450), (960, 410)], (90, 70, 60, 255), 6))


def k21(c):   # 상암 월드컵경기장
    c.sky(); c.stars()
    c.stadium(480, 340, 860, 220, (24, 80, 50))
    c.pen(lambda p: [p.line([(480 + k * 60, 120), (480 + k * 40, 250)], (220, 230, 255, 140), 1) for k in range(-6, 7)])


def k22(c):   # 미시령 옛길
    PA.p22(c)
    c.fog(330, 60, 50)


def k23(c):   # 울산 조선소
    c.sky(top=(10, 10, 30), low=(60, 50, 90)); c.stars(40)
    c.gantry(480, 380, 520, 260)
    c.ship(200, 330, 560)
    c.crane(120, 380, 220, 140); c.crane(860, 380, 200, -140)
    c.water(400, 540, lights=[(480, WARM)])


def k24(c):   # 사직야구장
    c.sky(); c.stars()
    c.stadium(480, 360, 860, 220, (30, 90, 50))
    c.pen(lambda p: p.poly([(480, 360), (380, 410), (480, 450), (580, 410)], (120, 90, 60, 255)))
    c.pen(lambda p: [p.ell(100 + k * 40, 250 + (k % 2) * 6, 8, 6, (255, 140, 60, 220)) for k in range(20)])   # 주황 봉지 응원


def k25(c):   # 전주 한옥마을
    c.sky(); c.stars(); c.moon(480, 60)
    c.hills(250, 40, HILL_FAR, 25)
    for k, x in enumerate((0, 260, 520, 760)):
        c.hanok(x + 20, 360 + (k % 2) * 20, 200, 70)
    c.ground(380, (36, 34, 56))
    c.string_lights([(0, 300), (480, 330), (960, 300)], [WARM, (255, 120, 120)])


def k26(c):   # 명동
    c.sky(); c.stars(20)
    c.glass(0, 430, 230, 360, (20, 24, 60)); c.glass(730, 430, 230, 370, (20, 24, 60))
    for k in range(9):
        c.sign(10 + (k % 2) * 100, 90 + k * 34, 100, 18, NEON[k % 5])
        c.sign(740 + (k % 2) * 100, 80 + k * 36, 100, 18, NEON[(k + 1) % 5])
    c.road(480, 300, 520, dashes=False)
    c.stalls(470, 3, 260, 700)
    c.people(36, 380, 540)


def k27(c):   # 대구 서문시장
    c.sky(); c.stars(); c.moon(160, 60)
    c.glass(380, 300, 200, 120, (30, 30, 66))
    c.sign(420, 210, 120, 22, WARM)
    c.ground(300, (24, 24, 50))
    c.stalls(450, 5)
    c.pen(lambda p: [p.ell(70 + k * 37, 430, 9, 9, (230, 60, 60, 255)) for k in range(24)])    # 사과
    c.people(10, 460, 540)


def k28(c):   # 담양 죽녹원
    PA.p28(c)


def k29(c):   # 김제 지평선
    c.sky(top=(10, 12, 34), low=(90, 80, 120), horizon=0.7); c.stars(); c.moon(480, 90, 30)
    c.paddy(330, gold=True)
    c.pen(lambda p: p.poly([(470, 330), (490, 330), (600, 540), (360, 540)], (60, 110, 200, 255)))


def k30(c):   # 문경새재 관문
    c.sky(); c.stars(); c.moon(760, 60)
    c.mountains(300, [(100, 160), (300, 220), (640, 200), (860, 160)], HILL_FAR)
    c.fortress(400, 0, 960)
    c.gate_tower(480, 400, 260, 200)
    c.pen(lambda p: p.poly([(440, 540), (520, 540), (500, 400), (460, 400)], (60, 56, 70, 255)))


def k31(c):   # 철원 평야
    PA.p31(c)
    c.pen(lambda p: [p.ell(120 + k * 160, 90 + (k % 2) * 20, 14, 4, (220, 220, 240, 220)) for k in range(5)])   # 두루미


def k32(c):   # 군산 근대거리
    c.sky(); c.stars(); c.moon(160, 70)
    c.pen(lambda p: [p.rect(x, 220, x + 200, 400, (50, 40, 50, 255)) for x in (20, 380, 740)])
    c.pen(lambda p: [p.poly([(x - 10, 220), (x + 210, 220), (x + 100, 170)], (30, 30, 50, 255)) for x in (20, 380, 740)])
    c.pen(lambda p: [p.rect(x + 20 + k * 40, 260, x + 40 + k * 40, 300, WARM + (170,)) for x in (20, 380, 740) for k in range(4)], glow=(4, 0.6))
    c.ground(400, (26, 24, 44))
    c.lamp(320, 480); c.lamp(660, 480)


def k33(c):   # 청계천
    c.sky(); c.stars(30)
    c.glass(0, 300, 220, 260); c.glass(740, 300, 220, 270)
    c.pen(lambda p: p.rect(0, 300, W, 360, (50, 50, 80, 255)))
    c.water(360, 540, lights=[(300, (90, 160, 255)), (660, (255, 120, 200))])
    c.pen(lambda p: [p.rect(140 + k * 90, 430, 190 + k * 90, 450, (150, 150, 170, 255)) for k in range(8)])
    c.string_lights([(0, 320), (480, 340), (960, 320)])


def k34(c):   # 충주호
    PA.p34(c)
    c.fog(300, 50, 40)


def k35(c):   # 인천국제공항
    c.sky(top=(6, 10, 30), low=(30, 50, 110)); c.stars()
    c.plane(640, 120, 1.4)
    c.terminal(60, 360, 840, 120)
    c.ground(360, (20, 24, 48))
    c.pen(lambda p: [p.ell(x, 470, 3, 3, (120, 255, 160, 255)) for x in range(0, 960, 40)], glow=(4, 1.2))
    c.bus(120, 520, (40, 120, 220), 180); c.bus(640, 520, (200, 60, 70), 180)


def k36(c):   # 국회의사당
    c.sky(); c.stars(); c.moon(160, 60)
    c.pen(lambda p: p.rect(220, 240, 740, 400, (40, 42, 70, 255)))
    c.pen(lambda p: [p.rect(240 + k * 40, 260, 252 + k * 40, 400, (80, 84, 120, 255)) for k in range(13)])
    c.dome(480, 240, 150, (50, 80, 90), glow=True)
    c.ground(400, (20, 24, 46))
    c.water(440, 540, lights=[(480, LIGHT)])


def k37(c):   # 이천 쌀 방앗간
    PA.p37(c)


def k38(c):   # 인천 차이나타운
    c.sky(top=(12, 6, 26), low=(70, 30, 50)); c.stars(30)
    c.house(0, 420, 200, 160, wall=(60, 30, 40)); c.house(760, 420, 200, 160, wall=(60, 30, 40))
    c.paifang(480, 420, 400, 260)
    c.ground(420, (30, 20, 40))
    c.string_lights([(0, 200), (480, 230), (960, 200)], [(255, 60, 60), (255, 200, 80)])


def k39(c):   # 광주 충장로
    PA.p39(c)


def k40(c):   # 수원 화성
    c.sky(); c.stars(); c.moon(820, 60)
    c.fortress(360, 0, 960, (54, 52, 80))
    c.gate_tower(480, 360, 300, 220)
    c.road(480, 360, 700)
    c.pen(lambda p: [p.rect(80 + k * 90, 450, 140 + k * 90, 458, (240, 240, 255, 230)) for k in range(9)])


MOOD_CODE = {'D': 'day', 'S': 'sunset', 'K': 'dusk', 'N': 'night'}
#            1234567890123456789012345678901234567890
SJ_MOODS = 'NDDDSKDSDDDSDNSDNDDDKDSNDNDKDSDKDSDDDKNS'
KR_MOODS = 'NDDDSNDDDSDSDKSDNDSSNDDNKNDDSDDKNDSDDNNS'
T1_MOODS = {16: 'D', 17: 'S', 18: 'D', 19: 'D', 20: 'D', 21: 'N', 22: 'K', 23: 'D', 24: 'N', 25: 'D', 26: 'S', 27: 'D', 28: 'K',
            29: 'D', 30: 'S', 31: 'D', 32: 'N', 33: 'D', 34: 'S', 35: 'N', 36: 'D', 37: 'D', 38: 'K', 39: 'N', 40: 'S'}
assert len(SJ_MOODS) == 40 and len(KR_MOODS) == 40

SEJONG_ART = {k: globals()['s%02d' % k] for k in range(1, 41)}
KOREA_ART = {k: globals()['k%02d' % k] for k in range(1, 41)}


def _save_small(img, name):
    """256색 PNG 로 저장 (용량 절약)."""
    path = os.path.join(OUT, name + '.png')
    q = img.convert('RGB').quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    q.save(path, optimize=True)
    return path


def build_all(only=None, force=False):
    ensure_out()
    me = os.path.getmtime(__file__)
    out = {}
    for prefix, table, moods in (('sj', SEJONG_ART, SJ_MOODS), ('kr', KOREA_ART, KR_MOODS)):
        for k, fn in table.items():
            name = '%s_%02d' % (prefix, k)
            if only and name not in only:
                continue
            path = os.path.join(OUT, name + '.png')
            if not force and not only and os.path.exists(path) and os.path.getmtime(path) > me:
                out[name] = path
                continue
            c = C2(k * 7 + (0 if prefix == 'sj' else 500), MOOD_CODE[moods[k - 1]])
            fn(c)
            out[name] = _save_small(c.finish(), name)
    return out


if __name__ == '__main__':
    import sys
    build_all(sys.argv[1:] or None, force=True)
