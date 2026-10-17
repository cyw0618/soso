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


# ================================================================== 14. 땅따먹기 선긋기
ME_COL = (70, 130, 255)
AI_COL = (255, 80, 100)


def k14_edge(vert, who):
    """who 0: 아직 안 그은 선(점선, 넓은 클릭 영역), 1: 내 선, 2: 응원단장 선."""
    w, h = (14, 42) if vert else (42, 14)
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, H), fill=(255, 255, 255, 4))
        if who == 0:
            n = 5
            for i in range(n):
                if vert:
                    y0 = H * (i + 0.25) / n
                    d.rounded_rectangle((W / 2 - 1.3 * s, y0, W / 2 + 1.3 * s, y0 + H * 0.5 / n), 1 * s, fill=(200, 210, 240, 120))
                else:
                    x0 = W * (i + 0.25) / n
                    d.rounded_rectangle((x0, H / 2 - 1.3 * s, x0 + W * 0.5 / n, H / 2 + 1.3 * s), 1 * s, fill=(200, 210, 240, 120))
        else:
            col = ME_COL if who == 1 else AI_COL
            if vert:
                box = (W / 2 - 3 * s, 1 * s, W / 2 + 3 * s, H - 1 * s)
            else:
                box = (1 * s, H / 2 - 3 * s, W - 1 * s, H / 2 + 3 * s)
            d.rounded_rectangle(box, 3 * s, fill=col + (255,), outline=(255, 255, 255, 230), width=int(1 * s))
    return art('k14_e%d%d' % (vert, who), w, h, f)


def k14_box(who):
    def f(d, im, s):
        W, H = im.size
        if who == 0:
            d.rectangle((0, 0, W, H), fill=(255, 255, 255, 1))
            return
        col = ME_COL if who == 1 else AI_COL
        d.rounded_rectangle((2 * s, 2 * s, W - 2 * s, H - 2 * s), 5 * s, fill=col + (150,))
        d.text((W / 2, H / 2 + 1 * s), '나' if who == 1 else '응', font=font('jalnan', int(15 * s)), fill=(255, 255, 255, 255),
               anchor='mm')
    return art('k14_box%d' % who, 38, 38, f)


def k14_dots(n=5, pitch=46):
    size = pitch * (n - 1) + 14
    def f(d, im, s):
        for r in range(n):
            for c in range(n):
                x, y = (7 + c * pitch) * s, (7 + r * pitch) * s
                d.ellipse((x - 5 * s, y - 5 * s, x + 5 * s, y + 5 * s), fill=(10, 14, 30, 255))
                d.ellipse((x - 4 * s, y - 4 * s, x + 4 * s, y + 4 * s), fill=(250, 250, 255, 255))
    return art('k14_dots', size, size, f)


def k14_cheer():
    """응원단장 (머리띠·메가폰)."""
    def f(d, im, s):
        W, H = im.size
        cx = W * 0.42
        # 몸 (응원단복)
        d.rounded_rectangle((cx - 20 * s, 44 * s, cx + 20 * s, H), 10 * s, fill=(20, 40, 130, 255), outline=(8, 12, 40, 255), width=int(1.2 * s))
        d.polygon([(cx - 6 * s, 44 * s), (cx + 6 * s, 44 * s), (cx, 56 * s)], fill=(255, 255, 255, 255))
        d.rectangle((cx - 20 * s, 62 * s, cx + 20 * s, 66 * s), fill=(255, 210, 60, 255))
        # 얼굴
        d.ellipse((cx - 16 * s, 12 * s, cx + 16 * s, 46 * s), fill=(255, 216, 186, 255), outline=(60, 30, 20, 255), width=int(1.2 * s))
        d.chord((cx - 17 * s, 9 * s, cx + 17 * s, 36 * s), 180, 360, fill=(30, 24, 30, 255))
        d.rectangle((cx - 17 * s, 20 * s, cx + 17 * s, 25 * s), fill=(230, 40, 60, 255))
        d.polygon([(cx + 15 * s, 21 * s), (cx + 26 * s, 16 * s), (cx + 24 * s, 26 * s)], fill=(230, 40, 60, 255))
        for ex in (-6, 6):
            d.line([((cx + ex - 3) * 1, 31 * s), (cx + ex * s + 3 * s, 31 * s)], fill=(0, 0, 0, 0))
            d.arc((cx + ex * s - 3 * s, 29 * s, cx + ex * s + 3 * s, 34 * s), 180, 360, fill=(40, 20, 20, 255), width=int(1.4 * s))
        d.ellipse((cx - 5 * s, 36 * s, cx + 5 * s, 43 * s), fill=(160, 30, 40, 255))
        # 메가폰
        d.polygon([(cx + 18 * s, 50 * s), (W - 2 * s, 36 * s), (W - 2 * s, 66 * s), (cx + 18 * s, 58 * s)], fill=(255, 255, 255, 255),
                  outline=(30, 30, 60, 255))
        d.rectangle((cx + 14 * s, 49 * s, cx + 19 * s, 59 * s), fill=(230, 40, 60, 255))
    return art('k14_cheer', 64, 76, f)


# ================================================================== 15. 물통 나누기
U15 = 11      # 1L = 11px


def k15_jug(cap):
    w, h = 54, cap * U15 + 16
    def f(d, im, s):
        W, H = im.size
        top = 2 * s
        bot = H - 14 * s
        d.rectangle((3 * s, bot, W - 3 * s, H), fill=(40, 46, 70, 255))
        d.rectangle((3 * s, bot, W - 3 * s, bot + 3 * s), fill=(150, 170, 220, 255))
        d.rounded_rectangle((3 * s, top, W - 3 * s, bot + 2 * s), 4 * s, fill=(200, 230, 255, 40), outline=(220, 236, 255, 255),
                            width=int(2 * s))
        d.rectangle((8 * s, top + 4 * s, 11 * s, bot - 4 * s), fill=(255, 255, 255, 70))
        for L in range(1, cap):
            y = bot - L * U15 * s
            d.line([(W - 14 * s, y), (W - 4 * s, y)], fill=(255, 255, 255, 200), width=int(1 * s))
            d.text((W - 16 * s, y), str(L), font=font('nsr', int(6 * s)), fill=(255, 255, 255, 220), anchor='rm')
    return art('k15_jug%d' % cap, w, h, f)


def k15_water(cap):
    w, h = 46, cap * U15
    def f(d, im, s):
        W, H = im.size
        for y in range(0, H, s):
            t = y / H
            d.rectangle((0, y, W, y + s), fill=(int(70 - 30 * t), int(150 - 40 * t), int(255 - 50 * t), 210))
        d.rectangle((0, 0, W, 2 * s), fill=(200, 236, 255, 255))
    return art('k15_water%d' % cap, w, h, f)


def k15_stream():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((W / 2 - 3 * s, 0, W / 2 + 3 * s, H), 3 * s, fill=(90, 170, 255, 220))
        d.line([(W / 2 - 1 * s, 0), (W / 2 - 1 * s, H)], fill=(220, 240, 255, 200), width=int(1 * s))
    return art('k15_stream', 10, 80, f)


# ================================================================== 16. 패러글라이딩 착지
def k16_field():
    def f(d, im, s):
        import random
        W, H = im.size
        r = random.Random(16)
        d.rounded_rectangle((0, 0, W - 1, H - 1), 14 * s, fill=(70, 140, 80, 235), outline=(200, 230, 255, 200), width=int(1.5 * s))
        for i in range(14):
            x, y = r.uniform(0, W), r.uniform(0, H)
            rx, ry = r.uniform(20, 50) * s, r.uniform(14, 30) * s
            d.ellipse((max(4 * s, x - rx), max(4 * s, y - ry), min(W - 4 * s, x + rx), min(H - 4 * s, y + ry)),
                      fill=r.choice([(86, 156, 86, 255), (60, 124, 72, 255), (110, 160, 80, 255)]))
        d.line([(0, H * 0.7), (W * 0.4, H * 0.62), (W, H * 0.8)], fill=(214, 190, 140, 255), width=int(5 * s))
        for i in range(22):
            x, y = r.uniform(10 * s, W - 10 * s), r.uniform(10 * s, H - 10 * s)
            rr = r.uniform(3, 6) * s
            d.ellipse((x - rr + s, y - rr + 2 * s, x + rr + s, y + rr + 2 * s), fill=(20, 50, 30, 120))
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(34, 96, 56, 255))
    return art('k16_field', 340, 214, f, colors=64)


def k16_target():
    def f(d, im, s):
        W = im.width
        c = W / 2
        for k, col in enumerate([(255, 255, 255), (230, 50, 60), (255, 255, 255), (230, 50, 60)]):
            r = W / 2 * (1 - k * 0.24) - 1 * s
            d.ellipse((c - r, c - r, c + r, c + r), fill=col + (230,))
        d.line([(c - 4 * s, c), (c + 4 * s, c)], fill=(20, 20, 40, 255), width=int(1 * s))
        d.line([(c, c - 4 * s), (c, c + 4 * s)], fill=(20, 20, 40, 255), width=int(1 * s))
    return art('k16_target', 44, 44, f)


def k16_thermal():
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((2 * s, 2 * s, W - 2 * s, W - 2 * s), fill=(255, 160, 60, 50))
        for k in range(12):
            a0 = k * 30
            d.arc((3 * s, 3 * s, W - 3 * s, W - 3 * s), a0, a0 + 16, fill=(255, 190, 90, 230), width=int(2 * s))
        for k in range(3):
            a = math.radians(k * 120)
            d.arc((c - 14 * s, c - 14 * s, c + 14 * s, c + 14 * s), k * 120, k * 120 + 70, fill=(255, 220, 140, 220), width=int(2 * s))
        d.text((c, c), '상승', font=font('jalnan', int(8 * s)), fill=(255, 240, 210, 255), anchor='mm')
    return art('k16_thermal', 60, 60, f)


def k16_glider(shadow=False):
    def f(d, im, s):
        W, H = im.size
        if shadow:
            d.chord((2 * s, 4 * s, W - 2 * s, H * 1.4), 190, 350, fill=(0, 0, 0, 90))
            return
        d.chord((2 * s, 2 * s, W - 2 * s, H * 1.25), 188, 352, fill=(255, 90, 60, 255), outline=(60, 10, 10, 255))
        d.chord((10 * s, 6 * s, W - 10 * s, H * 1.25), 192, 348, fill=(255, 200, 70, 255))
        for k in (-1, 1):
            d.line([(W / 2 + k * 14 * s, H * 0.25), (W / 2, H - 4 * s)], fill=(240, 240, 255, 200), width=int(0.6 * s))
        d.ellipse((W / 2 - 3 * s, H - 8 * s, W / 2 + 3 * s, H - 2 * s), fill=(40, 60, 160, 255))
    return art('k16_glider%s' % ('S' if shadow else ''), 44, 26, f)


def k16_wind():
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((1 * s, 1 * s, W - 1 * s, W - 1 * s), fill=(10, 16, 40, 200), outline=(140, 170, 255, 255), width=int(1 * s))
        d.polygon([(c, 5 * s), (c + 8 * s, 18 * s), (c + 3 * s, 18 * s), (c + 3 * s, W - 6 * s), (c - 3 * s, W - 6 * s),
                   (c - 3 * s, 18 * s), (c - 8 * s, 18 * s)], fill=(140, 220, 255, 255))
    return art('k16_wind', 40, 40, f)


# ================================================================== 17. 드론 대형 기억
DRONE_COL = [(120, 200, 255), (255, 110, 170), (120, 255, 150), (255, 220, 90)]


def k17_drone(k):
    col = DRONE_COL[k - 1]
    def f(d, im, s):
        W = im.width
        c = W / 2
        for r in range(10, 0, -1):
            rr = W / 2 * r / 10
            d.ellipse((c - rr, c - rr, c + rr, c + rr), fill=col + (int(14 + 4 * (10 - r)),))
        d.ellipse((c - 5 * s, c - 5 * s, c + 5 * s, c + 5 * s), fill=(255, 255, 255, 255))
        d.ellipse((c - 3.5 * s, c - 3.5 * s, c + 3.5 * s, c + 3.5 * s), fill=col + (255,))
    return art('k17_d%d' % k, 22, 22, f)


# ================================================================== 18. 리버시
def k18_board(n=6, pitch=36):
    size = n * pitch + 12
    def f(d, im, s):
        W = im.width
        d.rounded_rectangle((0, 0, W - 1, W - 1), 8 * s, fill=(196, 150, 92, 255), outline=(60, 34, 12, 255), width=int(2 * s))
        d.rectangle((6 * s, 6 * s, W - 6 * s, W - 6 * s), fill=(214, 172, 110, 255))
        for k in range(n + 1):
            p = (6 + k * pitch) * s
            d.line([(p, 6 * s), (p, W - 6 * s)], fill=(90, 56, 24, 255), width=int(1.2 * s))
            d.line([(6 * s, p), (W - 6 * s, p)], fill=(90, 56, 24, 255), width=int(1.2 * s))
    return art('k18_board', size, size, f, colors=48)


def k18_hint():
    def f(d, im, s):
        W = im.width
        d.rectangle((0, 0, W, W), fill=(255, 255, 255, 2))
        d.ellipse((W / 2 - 5 * s, W / 2 - 5 * s, W / 2 + 5 * s, W / 2 + 5 * s), fill=(20, 30, 60, 110), outline=(255, 255, 255, 160))
    return art('k18_hint', 34, 34, f)


# ================================================================== 19. 수문장 교대식
def k19_guard(pose):
    """pose: idle up down left right — 수문장이 깃발 든 팔을 그 방향으로."""
    def f(d, im, s):
        W, H = im.size
        cx = W / 2
        red, dark = (200, 40, 50, 255), (60, 10, 16, 255)
        # 몸 (붉은 철릭)
        d.polygon([(cx - 18 * s, 54 * s), (cx + 18 * s, 54 * s), (cx + 26 * s, H - 8 * s), (cx - 26 * s, H - 8 * s)], fill=red, outline=dark)
        d.rectangle((cx - 20 * s, 74 * s, cx + 20 * s, 78 * s), fill=(250, 200, 60, 255))
        d.rectangle((cx - 12 * s, H - 8 * s, cx - 4 * s, H), fill=(30, 30, 40, 255))
        d.rectangle((cx + 4 * s, H - 8 * s, cx + 12 * s, H), fill=(30, 30, 40, 255))
        # 머리 + 전립(모자)
        d.ellipse((cx - 12 * s, 28 * s, cx + 12 * s, 54 * s), fill=(255, 216, 186, 255), outline=(60, 30, 20, 255))
        d.ellipse((cx - 22 * s, 24 * s, cx + 22 * s, 32 * s), fill=(20, 20, 26, 255))
        d.chord((cx - 12 * s, 10 * s, cx + 12 * s, 36 * s), 180, 360, fill=(20, 20, 26, 255))
        d.line([(cx, 10 * s), (cx + 2 * s, 2 * s)], fill=(240, 60, 60, 255), width=int(2 * s))
        for ex in (-5, 5):
            d.ellipse((cx + ex * s - 1.5 * s, 39 * s, cx + ex * s + 1.5 * s, 42 * s), fill=(20, 20, 20, 255))
        d.line([(cx - 4 * s, 48 * s), (cx + 4 * s, 48 * s)], fill=(120, 40, 40, 255), width=int(1 * s))
        # 왼팔은 허리, 오른팔이 깃발
        sh = (cx + 16 * s, 60 * s)
        tip = {'idle': (cx + 22 * s, 92 * s), 'up': (cx + 22 * s, 14 * s), 'down': (cx + 34 * s, 104 * s),
               'left': (cx - 48 * s, 58 * s), 'right': (cx + 48 * s, 58 * s)}[pose]
        if pose == 'left':
            sh = (cx - 16 * s, 60 * s)
        d.line([sh, tip], fill=red, width=int(7 * s))
        d.ellipse((tip[0] - 4 * s, tip[1] - 4 * s, tip[0] + 4 * s, tip[1] + 4 * s), fill=(255, 216, 186, 255))
        if pose != 'idle':
            fx_, fy_ = tip
            dx, dy = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}[pose]
            px, py = -dy, dx
            p0 = (fx_ + dx * 4 * s, fy_ + dy * 4 * s)
            p1 = (fx_ + dx * 24 * s, fy_ + dy * 24 * s)
            d.line([(fx_ - dx * 6 * s, fy_ - dy * 6 * s), p1], fill=(90, 60, 30, 255), width=int(2 * s))
            d.polygon([p0, p1, (p1[0] + px * 18 * s, p1[1] + py * 18 * s), (p0[0] + px * 18 * s, p0[1] + py * 18 * s)],
                      fill=(255, 220, 60, 255), outline=(90, 60, 0, 255))
        d.line([(cx - 16 * s, 60 * s), (cx - 18 * s, 80 * s)] if pose != 'left' else [(cx + 16 * s, 60 * s), (cx + 18 * s, 80 * s)],
               fill=red, width=int(7 * s))
    return art('k19_g_%s' % pose, 170, 134, f)


def k19_arrow(k, on):
    """k 0 ← 1 ↑ 2 → 3 ↓ 화살표 단추."""
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, W - 1 * s), 7 * s, fill=(60, 110, 255, 255) if on else (14, 20, 48, 230),
                            outline=(255, 255, 255, 255) if on else (110, 130, 200, 255), width=int(1.4 * s))
        pts = [(0, -11), (10, 1), (4, 1), (4, 10), (-4, 10), (-4, 1), (-10, 1)]
        ang = {0: -90, 1: 0, 2: 90, 3: 180}[k]
        a = math.radians(ang)
        P_ = [(c + (x * math.cos(a) - y * math.sin(a)) * s, c + (x * math.sin(a) + y * math.cos(a)) * s) for x, y in pts]
        d.polygon(P_, fill=(255, 255, 255, 255))
    return art('k19_a%d%d' % (k, on), 34, 34, f)


# ================================================================== 20. 흑두루미 세기
def k20_bird(kind, fr):
    """kind: crane(흑두루미: 회흑색 몸, 흰 목) egret(백로: 하양) duck(청둥오리: 초록 머리). fr 0/1 날갯짓."""
    w, h = {'crane': (66, 40), 'egret': (60, 38), 'duck': (42, 30)}[kind]
    def f(d, im, s):
        W, H = im.size
        cy = H * 0.55
        if kind == 'crane':
            body, wing, neck, head = (70, 72, 84), (40, 42, 52), (245, 245, 245), (245, 245, 245)
        elif kind == 'egret':
            body, wing, neck, head = (250, 250, 252), (226, 230, 240), (250, 250, 252), (250, 250, 252)
        else:
            body, wing, neck, head = (150, 120, 90), (110, 90, 70), (40, 140, 70), (30, 120, 60)
        out = (20, 20, 30, 255)
        # 다리 (뒤로)
        if kind != 'duck':
            d.line([(W * 0.32, cy), (2 * s, cy + 2 * s)], fill=(40, 40, 40, 255), width=int(1.2 * s))
        # 몸
        d.ellipse((W * 0.26, cy - H * 0.16, W * 0.66, cy + H * 0.16), fill=body + (255,), outline=out, width=int(0.8 * s))
        # 목 + 머리 (앞으로 쭉)
        nx = W * 0.86 if kind != 'duck' else W * 0.78
        d.line([(W * 0.62, cy - 1 * s), (nx, cy - 2 * s)], fill=neck + (255,), width=int((2.6 if kind != 'duck' else 4) * s))
        hr = (3.2 if kind != 'duck' else 3.8) * s
        d.ellipse((nx - hr, cy - 2 * s - hr, nx + hr, cy - 2 * s + hr), fill=head + (255,), outline=out, width=int(0.6 * s))
        if kind == 'crane':
            d.ellipse((nx - 1.4 * s, cy - 2 * s - hr, nx + 1.4 * s, cy - 2 * s - hr + 2.2 * s), fill=(220, 30, 40, 255))
        beak = (230, 180, 40) if kind != 'crane' else (90, 90, 70)
        d.polygon([(nx + hr * 0.8, cy - 3 * s), (W - 1 * s, cy - 1.5 * s), (nx + hr * 0.8, cy - 0.5 * s)], fill=beak + (255,))
        # 날개
        wy = -1 if fr == 0 else 1
        tip_y = cy + wy * H * 0.48
        d.polygon([(W * 0.28, cy), (W * 0.62, cy), (W * 0.46, tip_y), (W * 0.36, tip_y)], fill=wing + (255,), outline=out)
        if kind == 'crane':
            d.polygon([(W * 0.33, tip_y - wy * 5 * s), (W * 0.48, tip_y - wy * 5 * s), (W * 0.46, tip_y), (W * 0.36, tip_y)],
                      fill=(10, 10, 14, 255))
    return art('k20_%s%d' % (kind, fr), w, h, f)
