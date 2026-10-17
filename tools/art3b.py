# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 11~20번 그림 (mg_art3.art 위에 그린다: 무대 px 기준, 2배 해상도로 저장)."""
import math
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3

INK = {1: (232, 44, 56), 2: (48, 108, 245), 3: (255, 208, 20), 4: (28, 172, 84)}
INK_NAME = {1: '빨강', 2: '파랑', 3: '노랑', 4: '초록'}


def _shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


# ================================================================== 11. 신호 깃발 판단
def k11_word(word, ink):
    """색 이름 글자(word)를 ink 색으로."""
    def f(d, im, s):
        fo = font('jalnan', int(40 * s))
        cx, cy = im.width / 2, im.height / 2 + 2 * s
        col = INK[ink] + (255,)
        for k in range(16):
            a = k * math.pi / 8
            d.text((cx + math.cos(a) * 2.2 * s, cy + math.sin(a) * 2.2 * s), INK_NAME[word], font=fo,
                   fill=(14, 18, 40, 255), anchor='mm')
        d.text((cx, cy), INK_NAME[word], font=fo, fill=col, anchor='mm')
    return A3.art('k11_w%d%d' % (word, ink), 120, 56, f)


def k11_card(rule):
    """문제판 (rule 1: 색깔 규칙 = 파란 테, 2: 뜻 규칙 = 빨간 테)."""
    rim = (70, 120, 255) if rule == 1 else (255, 70, 90)
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((2 * s, 4 * s, W - 2 * s, H - 1 * s), 14 * s, fill=(0, 0, 0, 90))
        d.rounded_rectangle((2 * s, 2 * s, W - 2 * s, H - 4 * s), 14 * s, fill=rim + (255,))
        d.rounded_rectangle((7 * s, 7 * s, W - 7 * s, H - 9 * s), 10 * s, fill=(244, 244, 250, 255))
        d.rounded_rectangle((7 * s, 7 * s, W - 7 * s, H * 0.42), 10 * s, fill=(255, 255, 255, 255))
        for x in (16, W / s - 16):
            d.ellipse(((x - 3) * s, 12 * s, (x + 3) * s, 18 * s), fill=_shade(rim, 0.6) + (255,))
    return A3.art('k11_card%d' % rule, 220, 92, f)


def k11_flag(k, lit=False):
    """깃발 버튼 (k: 1 빨강 2 파랑 3 노랑 4 초록)."""
    col = INK[k]
    def f(d, im, s):
        W, H = im.size
        if lit:
            for r in range(10, 0, -1):
                a = int(16 * (10 - r) / 10) + 6
                rr = W * 0.5 * r / 10
                d.ellipse((W / 2 - rr, H * 0.42 - rr, W / 2 + rr, H * 0.42 + rr), fill=(255, 255, 255, a))
        # 받침판
        d.rounded_rectangle((4 * s, H - 22 * s, W - 4 * s, H - 2 * s), 7 * s, fill=(10, 14, 36, 230),
                            outline=(120, 140, 220, 255) if not lit else (255, 255, 255, 255), width=int(1.4 * s))
        d.text((W / 2, H - 12 * s), str(k), font=font('jalnan', int(13 * s)), fill=(255, 255, 255, 255), anchor='mm')
        # 깃대
        px = 18 * s
        d.rounded_rectangle((px - 2 * s, 6 * s, px + 2 * s, H - 22 * s), 2 * s, fill=(210, 214, 230, 255))
        d.ellipse((px - 4 * s, 2 * s, px + 4 * s, 10 * s), fill=(250, 220, 120, 255))
        # 펄럭이는 깃발
        pts = []
        x0, x1 = px + 2 * s, W - 6 * s
        top, bot = 10 * s, 46 * s
        n = 16
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            pts.append((x, top + math.sin(i / n * math.pi * 1.6) * 3 * s))
        for i in range(n, -1, -1):
            x = x0 + (x1 - x0) * i / n
            pts.append((x, bot + math.sin(i / n * math.pi * 1.6) * 3 * s))
        d.polygon(pts, fill=col + (255,), outline=(12, 14, 30, 255))
        d.line(pts[:n + 1], fill=_shade(col, 1.25) + (255,), width=int(2 * s))
        d.polygon([(x0, top), (x0 + 10 * s, top + 4 * s), (x0 + 10 * s, bot - 4 * s), (x0, bot)], fill=_shade(col, 0.75) + (255,))
    return A3.art('k11_flag%d%s' % (k, 'L' if lit else ''), 76, 78, f)


# ================================================================== 12. 연꽃 스도쿠
def k12_cell(kind, n=0):
    """kind: e(빈 연잎) g(주어진 숫자: 연꽃) p(내가 쓴 숫자) x(겹침)."""
    def f(d, im, s):
        W = im.width
        c = W / 2
        r = W * 0.46
        # 연잎 (갈라진 틈이 있는 원)
        pad = (52, 150, 86) if kind != 'x' else (170, 60, 70)
        dark = _shade(pad, 0.55)
        d.ellipse((c - r + 1 * s, c - r + 2 * s, c + r + 1 * s, c + r + 2 * s), fill=(0, 10, 20, 120))
        d.ellipse((c - r, c - r, c + r, c + r), fill=pad + (255,), outline=dark + (255,), width=int(1.4 * s))
        d.pieslice((c - r, c - r, c + r, c + r), 62, 82, fill=(0, 0, 0, 0))
        for a in range(0, 360, 45):
            if 60 < a < 85:
                continue
            x = c + math.cos(math.radians(a)) * r * 0.85
            y = c + math.sin(math.radians(a)) * r * 0.85
            d.line([(c, c), (x, y)], fill=_shade(pad, 0.8) + (255,), width=int(0.8 * s))
        if kind == 'g':
            # 연꽃 (분홍 꽃잎) 위에 진한 숫자
            for a in range(0, 360, 45):
                x = c + math.cos(math.radians(a)) * r * 0.42
                y = c + math.sin(math.radians(a)) * r * 0.42
                rr = r * 0.36
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 170, 205, 255), outline=(214, 90, 140, 255), width=int(0.8 * s))
            d.ellipse((c - r * 0.52, c - r * 0.52, c + r * 0.52, c + r * 0.52), fill=(255, 236, 244, 255))
            d.text((c, c + 1 * s), str(n), font=font('jalnan', int(21 * s)), fill=(120, 20, 70, 255), anchor='mm')
        elif kind in ('p', 'x'):
            d.ellipse((c - r * 0.55, c - r * 0.55, c + r * 0.55, c + r * 0.55), fill=_shade(pad, 0.7) + (255,))
            col = (255, 255, 255) if kind == 'p' else (255, 236, 120)
            fo = font('jalnan', int(22 * s))
            for k in range(12):
                a = k * math.pi / 6
                d.text((c + math.cos(a) * 1.4 * s, c + 1 * s + math.sin(a) * 1.4 * s), str(n), font=fo, fill=(10, 30, 20, 255), anchor='mm')
            d.text((c, c + 1 * s), str(n), font=fo, fill=col + (255,), anchor='mm')
    return A3.art('k12_%s%d' % (kind, n), 42, 42, f)


def k12_board(pitch=46, gap=8):
    """4×4 연못 판 (2×2 칸 구역이 보이게)."""
    size = pitch * 4 + gap + 16
    def f(d, im, s):
        W = im.width
        d.rounded_rectangle((0, 0, W - 1, W - 1), 16 * s, fill=(6, 22, 40, 215), outline=(120, 170, 255, 230), width=int(1.6 * s))
        h = (pitch * 2 + 2) * s
        for bx in range(2):
            for by in range(2):
                x0 = (6 + bx * (pitch * 2 + gap)) * s
                y0 = (6 + by * (pitch * 2 + gap)) * s
                d.rounded_rectangle((x0, y0, x0 + h, y0 + h), 10 * s, fill=(20, 60, 96, 255), outline=(70, 130, 200, 255),
                                    width=int(1 * s))
    return A3.art('k12_board', size, size, f)
