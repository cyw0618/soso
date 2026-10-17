# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 11~20번 그림 (mg_art3.art 위에 그린다: 무대 px 기준, 2배 해상도로 저장)."""
import math
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3

INK = {1: (232, 44, 56), 2: (48, 108, 245), 3: (255, 208, 20), 4: (28, 172, 84)}
INK_NAME = {1: '빨강', 2: '파랑', 3: '노랑', 4: '초록'}


def art(name, w, h, f, colors=96):
    """A3.art 로 그린 뒤 팔레트 PNG 로 줄인다 (파일 크기 1/4 정도)."""
    p = A3.art(name, w, h, f)
    im = Image.open(p)
    if im.mode != 'P':
        im.convert('RGBA').quantize(colors=colors, method=Image.FASTOCTREE).save(p, optimize=True)
    return p


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
    return art('k11_w%d%d' % (word, ink), 120, 56, f)


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
    return art('k11_card%d' % rule, 220, 92, f)


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
    return art('k11_flag%d%s' % (k, 'L' if lit else ''), 76, 78, f)


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
    return art('k12_%s%d' % (kind, n), 42, 42, f)


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
    return art('k12_board', size, size, f)


# ================================================================== 13. 로켓 발사
def _metal(d, box, s, base=(226, 230, 242), dark=(140, 148, 176)):
    x0, y0, x1, y1 = box
    n = 12
    for i in range(n):
        t = i / (n - 1)
        k = 1 - abs(t - 0.35) * 1.1
        col = tuple(int(dark[j] + (base[j] - dark[j]) * max(0, min(1, k))) for j in range(3))
        d.rectangle((x0 + (x1 - x0) * i / n, y0, x0 + (x1 - x0) * (i + 1) / n, y1), fill=col + (255,))


def k13_stage(k):
    """로켓 단 그림 (k=1 맨 아래 부스터, 2 가운데, 3 꼭대기 캡슐)."""
    W_, H_ = {1: (34, 62), 2: (30, 46), 3: (30, 58)}[k]
    def f(d, im, s):
        W, H = im.size
        if k == 3:
            body = (2 * s, 26 * s, W - 2 * s, H - 1 * s)
            _metal(d, body, s)
            # 원뿔 머리
            pts = [(W / 2, 0), (W - 2 * s, 26 * s), (2 * s, 26 * s)]
            d.polygon(pts, fill=(214, 46, 64, 255), outline=(60, 10, 20, 255))
            d.polygon([(W / 2, 0), (W / 2 - 3 * s, 26 * s), (2 * s, 26 * s)], fill=(240, 90, 100, 255))
            d.ellipse((W / 2 - 6 * s, 33 * s, W / 2 + 6 * s, 45 * s), fill=(40, 70, 160, 255), outline=(20, 30, 70, 255), width=int(1.4 * s))
            d.ellipse((W / 2 - 4 * s, 35 * s, W / 2 - 0.5 * s, 39 * s), fill=(200, 230, 255, 200))
            d.text((W / 2, H - 6 * s), 'KOREA', font=font('jalnan', int(5 * s)), fill=(30, 50, 140, 255), anchor='mm')
            d.rectangle((2 * s, 26 * s, W - 2 * s, H - 1 * s), outline=(70, 76, 100, 255), width=int(1 * s))
        else:
            body = (2 * s, 0, W - 2 * s, H - (8 if k == 1 else 3) * s)
            _metal(d, body, s)
            d.rectangle(body, outline=(70, 76, 100, 255), width=int(1 * s))
            d.rectangle((2 * s, 3 * s, W - 2 * s, 7 * s), fill=(40, 70, 170, 255))
            d.text((W / 2, (H - 8 * s) / 2 + 2 * s), '%d단' % k, font=font('jalnan', int(8 * s)), fill=(40, 50, 90, 255), anchor='mm')
            if k == 1:
                # 날개 + 엔진 노즐
                d.polygon([(0, H - 26 * s), (2 * s, H - 30 * s), (2 * s, H - 8 * s), (0, H - 4 * s)], fill=(200, 40, 60, 255))
                d.polygon([(W, H - 26 * s), (W - 2 * s, H - 30 * s), (W - 2 * s, H - 8 * s), (W, H - 4 * s)], fill=(200, 40, 60, 255))
                d.polygon([(W / 2 - 9 * s, H - 8 * s), (W / 2 + 9 * s, H - 8 * s), (W / 2 + 12 * s, H), (W / 2 - 12 * s, H)],
                          fill=(70, 74, 90, 255), outline=(20, 22, 30, 255))
            else:
                d.polygon([(W / 2 - 8 * s, H - 3 * s), (W / 2 + 8 * s, H - 3 * s), (W / 2 + 10 * s, H), (W / 2 - 10 * s, H)],
                          fill=(70, 74, 90, 255))
    return art('k13_stage%d' % k, W_, H_, f)


def k13_flame(fr):
    def f(d, im, s):
        W, H = im.size
        L = H * (0.92 if fr == 1 else 0.78)
        for i, (col, wk) in enumerate((((255, 110, 40, 160), 1.0), ((255, 190, 60, 220), 0.72), ((255, 250, 210, 255), 0.4))):
            w = W * 0.5 * wk
            d.polygon([(W / 2 - w, 0), (W / 2 + w, 0), (W / 2 + w * 0.3, L * (0.6 + 0.4 * wk)), (W / 2, L * (0.7 + 0.3 * wk)),
                       (W / 2 - w * 0.3, L * (0.6 + 0.4 * wk))], fill=col)
    return art('k13_flame%d' % fr, 26, 50, f)


def k13_tower():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, H - 10 * s, W, H), fill=(60, 64, 80, 255))
        d.rectangle((0, H - 12 * s, W, H - 10 * s), fill=(250, 200, 60, 255))
        x0, x1 = W - 26 * s, W - 8 * s
        d.rectangle((x0, 4 * s, x0 + 2 * s, H - 10 * s), fill=(200, 60, 60, 255))
        d.rectangle((x1, 4 * s, x1 + 2 * s, H - 10 * s), fill=(200, 60, 60, 255))
        y = 4 * s
        while y < H - 14 * s:
            d.line([(x0, y), (x1 + 2 * s, y + 10 * s)], fill=(220, 90, 90, 255), width=int(1.2 * s))
            d.line([(x1 + 2 * s, y), (x0, y + 10 * s)], fill=(220, 90, 90, 255), width=int(1.2 * s))
            y += 10 * s
        for yy in (30, 70, 110):
            d.rectangle((W / 2 + 14 * s, yy * s, x0, yy * s + 3 * s), fill=(180, 60, 60, 255))
    return art('k13_tower', 110, 150, f)


def k13_cloud(k):
    def f(d, im, s):
        W, H = im.size
        import random
        r = random.Random(k)
        for i in range(7):
            cx = W * (0.24 + 0.52 * i / 6)
            rr = H * r.uniform(0.25, 0.42)
            cy = H * 0.6 - r.uniform(0, H * 0.18)
            d.ellipse((cx - rr * 1.2, cy - rr, cx + rr * 1.2, cy + rr), fill=(236, 242, 255, 200))
    return art('k13_cloud%d' % k, 120, 46, f)


def k13_stars():
    def f(d, im, s):
        import random
        r = random.Random(13)
        W, H = im.size
        for i in range(26):
            x, y = r.uniform(0, W), r.uniform(0, H)
            rr = r.choice((0.6, 0.8, 1.0, 1.4)) * s
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 255, 255, r.randint(150, 255)))
    return art('k13_stars', 160, 90, f)


def k13_gauge():
    """속도계 (반원: 초록·노랑·빨강)."""
    def f(d, im, s):
        W, H = im.size
        cx, cy, R = W / 2, H - 6 * s, W / 2 - 4 * s
        d.pieslice((cx - R - 3 * s, cy - R - 3 * s, cx + R + 3 * s, cy + R + 3 * s), 180, 360, fill=(8, 12, 30, 235),
                   outline=(120, 150, 240, 255), width=int(1.2 * s))
        # 0 ~ 130% → 180°~360°
        segs = [(0, 0.55, (90, 110, 160)), (0.55, 0.77, (40, 200, 110)), (0.77, 0.80, (250, 200, 40)), (0.80, 1.0, (240, 50, 60))]
        for a, b, col in segs:
            d.arc((cx - R + 4 * s, cy - R + 4 * s, cx + R - 4 * s, cy + R - 4 * s), 180 + 180 * a, 180 + 180 * b, fill=col + (255,),
                  width=int(7 * s))
        d.text((cx, cy - R * 0.42), '속도', font=font('jalnan', int(8 * s)), fill=(200, 210, 240, 255), anchor='mm')
    return art('k13_gauge', 96, 56, f)


def k13_needle():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(W / 2 - 2 * s, H / 2), (W / 2, 1 * s), (W / 2 + 2 * s, H / 2)], fill=(255, 255, 255, 255))
        d.ellipse((W / 2 - 4 * s, H / 2 - 4 * s, W / 2 + 4 * s, H / 2 + 4 * s), fill=(230, 240, 255, 255), outline=(30, 40, 80, 255))
    return art('k13_needle', 10, 84, f)


def k13_marker():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(0, H / 2), (W * 0.55, 0), (W, 0), (W, H), (W * 0.55, H)], fill=(255, 220, 90, 255), outline=(60, 40, 0, 255))
    return art('k13_marker', 16, 10, f)
