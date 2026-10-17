# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 1~10번 (games3a.py) 전용 그림. 모두 mg_art3.art 로 그려 g3_k??_*.png 로 캐시된다."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3

art = A3.art


def _rgba(c, a=255):
    return tuple(c[:3]) + (a,)


def _glow_layer(im, draw_fn, radius):
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    lay = lay.filter(ImageFilter.GaussianBlur(radius))
    im.alpha_composite(lay)


# ================================================================== 1. 버스킹 음정
NOTE_NAMES = ['도', '레', '미', '파', '솔', '라', '시', '도']


def k01_staff(w=452, h=172, gap=21, n=8):
    def f(d, im, s):
        W, H = im.size
        cy = H / 2
        for k in range(n):
            y = cy + ((n - 1) / 2 - k) * gap * s
            col = (150, 170, 255, 70) if k % 2 == 0 else (150, 170, 255, 40)
            d.line([(30 * s, y), (W - 4 * s, y)], fill=col, width=int(1 * s))
            d.text((14 * s, y), NOTE_NAMES[k], font=font('jalnan', int(10 * s)), fill=(200, 210, 255, 210), anchor='mm')
    return art('k01_staff', w, h, f)


def k01_bar(beats, beat_px, vib=False, amp=6, freq_px=30):
    w = beats * beat_px - 4
    h = 14 + (2 * amp if vib else 0)

    def f(d, im, s):
        W, H = im.size
        cy = H / 2
        if vib:
            pts = [(x, cy - amp * s * math.sin(2 * math.pi * (x / s) / freq_px)) for x in range(int(5 * s), int(W - 5 * s), 2)]

            def g(dd):
                dd.line(pts, fill=(80, 140, 255, 200), width=int(9 * s), joint='curve')
            _glow_layer(im, g, 3 * s)
            d.line(pts, fill=(130, 200, 255, 255), width=int(8 * s), joint='curve')
            d.line(pts, fill=(235, 245, 255, 255), width=int(3 * s), joint='curve')
        else:
            def g(dd):
                dd.rounded_rectangle((2 * s, 2 * s, W - 2 * s, H - 2 * s), 5 * s, fill=(80, 130, 255, 200))
            _glow_layer(im, g, 2.5 * s)
            d.rounded_rectangle((3 * s, 3 * s, W - 3 * s, H - 3 * s), 4 * s, fill=(110, 170, 255, 255),
                                outline=(230, 240, 255, 255), width=int(1 * s))
            d.rounded_rectangle((5 * s, 4.5 * s, W - 5 * s, H / 2), 2 * s, fill=(255, 255, 255, 110))
    return art('k01_%s%d' % ('v' if vib else 'b', beats), w, h, f)


def k01_mark(on):
    def f(d, im, s):
        W = im.width
        c = W / 2
        col = (90, 255, 170) if on else (255, 120, 190)

        def g(dd):
            dd.ellipse((c - 9 * s, c - 9 * s, c + 9 * s, c + 9 * s), fill=_rgba(col, 220))
        _glow_layer(im, g, 3 * s)
        d.ellipse((c - 8 * s, c - 8 * s, c + 8 * s, c + 8 * s), fill=(20, 20, 40, 255), outline=_rgba(col), width=int(2 * s))
        d.ellipse((c - 4 * s, c - 4 * s, c + 4 * s, c + 4 * s), fill=_rgba(col))
    return art('k01_mk_%d' % on, 28, 28, f)


def k01_dot(on):
    def f(d, im, s):
        W = im.width
        col = (90, 255, 170, 230) if on else (255, 110, 150, 190)
        d.ellipse((0.5 * s, 0.5 * s, W - 0.5 * s, W - 0.5 * s), fill=col)
    return art('k01_dot_%d' % on, 6, 6, f)


def k01_nowline(h=176):
    def f(d, im, s):
        W, H = im.size
        for k in range(0, int(H), int(6 * s)):
            d.line([(W / 2, k), (W / 2, k + 3 * s)], fill=(255, 255, 255, 150), width=int(1.2 * s))
    return art('k01_nowline', 4, h, f)


def k01_crowd(cheer):
    def f(d, im, s):
        W, H = im.size
        rng = random.Random(11)
        n = 9
        for i in range(n):
            x = (i + 0.5) * W / n + rng.uniform(-4, 4) * s
            hh = rng.uniform(0, 6) * s
            body = (40 + rng.randint(0, 30), 20 + rng.randint(0, 20), 70 + rng.randint(0, 40), 255)
            top = H - 20 * s - hh
            if cheer:
                ax = rng.choice((-1, 1))
                d.line([(x - 7 * s, top + 8 * s), (x - 12 * s, top - 10 * s)], fill=body, width=int(4 * s))
                d.line([(x + 7 * s, top + 8 * s), (x + 12 * s, top - 10 * s)], fill=body, width=int(4 * s))
                stick = (255, 120, 200, 255) if i % 2 else (120, 200, 255, 255)
                lx = x + ax * 12 * s
                d.line([(lx, top - 10 * s), (lx + ax * 3 * s, top - 20 * s)], fill=stick, width=int(3 * s))
            d.rounded_rectangle((x - 9 * s, top + 4 * s, x + 9 * s, H + 4 * s), 7 * s, fill=body)
            d.ellipse((x - 6 * s, top - 8 * s, x + 6 * s, top + 4 * s), fill=(28, 18, 44, 255))
            d.arc((x - 6 * s, top - 8 * s, x + 6 * s, top + 4 * s), 200, 340, fill=(200, 120, 255, 200), width=int(1 * s))
    return art('k01_crowd_%d' % cheer, 210, 44, f)


def k01_case():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((2 * s, 6 * s, W - 2 * s, H - 2 * s), 8 * s, fill=(60, 30, 20, 255), outline=(20, 8, 4, 255), width=int(1.5 * s))
        d.rounded_rectangle((6 * s, 9 * s, W - 6 * s, H - 5 * s), 6 * s, fill=(140, 30, 60, 255))
        rng = random.Random(3)
        for k in range(9):
            x = rng.uniform(12, W / s - 12) * s
            y = rng.uniform(12, H / s - 7) * s
            d.ellipse((x - 3 * s, y - 2 * s, x + 3 * s, y + 2 * s), fill=(200, 200, 220, 255), outline=(90, 90, 110, 255))
    return art('k01_case', 64, 24, f)


# ================================================================== 2. 감귤 트럭
def k02_crate():
    def f(d, im, s):
        W, H = im.size
        # 귤 (위로 살짝 보이게)
        for k in range(5):
            x = (7 + k * 8) * s
            d.ellipse((x - 1 * s, 1 * s, x + 9 * s, 11 * s), fill=(255, 140, 20, 255), outline=(150, 60, 0, 255), width=int(0.8 * s))
            d.ellipse((x + 1.5 * s, 3 * s, x + 4.5 * s, 5.5 * s), fill=(255, 220, 160, 200))
        d.rounded_rectangle((1 * s, 7 * s, W - 1 * s, H - 1 * s), 3 * s, fill=(196, 140, 80, 255), outline=(70, 40, 14, 255), width=int(1.2 * s))
        for yy in (14, 24):
            d.line([(2 * s, yy * s), (W - 2 * s, yy * s)], fill=(150, 100, 50, 255), width=int(0.8 * s))
        d.rounded_rectangle((5 * s, 11 * s, W - 5 * s, H - 5 * s), 3 * s, fill=(255, 250, 238, 255), outline=(120, 80, 40, 255), width=int(0.8 * s))
    return art('k02_crate', 46, 40, f)


def k02_truck():
    def f(d, im, s):
        W, H = im.size
        # 짐칸 바닥
        d.rectangle((4 * s, 62 * s, 196 * s, 72 * s), fill=(70, 80, 110, 255), outline=(10, 14, 30, 255), width=int(1.2 * s))
        d.rectangle((4 * s, 56 * s, 8 * s, 66 * s), fill=(90, 100, 140, 255))
        # 운전석
        d.polygon([(200 * s, 72 * s), (200 * s, 22 * s), (226 * s, 22 * s), (244 * s, 44 * s), (246 * s, 72 * s)],
                  fill=(40, 90, 210, 255), outline=(6, 14, 50, 255))
        d.polygon([(206 * s, 28 * s), (224 * s, 28 * s), (238 * s, 44 * s), (206 * s, 44 * s)], fill=(180, 220, 255, 255))
        d.rectangle((240 * s, 58 * s, 248 * s, 64 * s), fill=(255, 220, 120, 255))
        d.rectangle((196 * s, 50 * s, 248 * s, 74 * s), fill=(30, 70, 180, 255), outline=(6, 14, 50, 255), width=int(1 * s))
        d.text((222 * s, 62 * s), '감귤', font=font('jalnan', int(8 * s)), fill=(255, 255, 255, 255), anchor='mm')
        # 바퀴
        for x in (40, 160, 222):
            d.ellipse(((x - 12) * s, 66 * s, (x + 12) * s, 90 * s), fill=(20, 20, 26, 255), outline=(0, 0, 0, 255))
            d.ellipse(((x - 5) * s, 73 * s, (x + 5) * s, 83 * s), fill=(160, 170, 190, 255))
    return art('k02_truck', 250, 92, f)


# ================================================================== 3. 생선 경매
FISH = ['고등어', '갈치', '참돔', '광어']


def k03_fish(k):
    def f(d, im, s):
        W, H = im.size
        cy = H / 2
        if k == 0:      # 고등어
            body = [(8 * s, cy), (40 * s, cy - 18 * s), (95 * s, cy - 14 * s), (112 * s, cy - 2 * s), (112 * s, cy + 2 * s), (95 * s, cy + 12 * s), (40 * s, cy + 16 * s)]
            d.polygon([(108 * s, cy), (128 * s, cy - 16 * s), (124 * s, cy), (128 * s, cy + 16 * s)], fill=(40, 90, 130, 255))
            d.polygon(body, fill=(210, 225, 235, 255), outline=(20, 40, 60, 255))
            d.polygon(body[:4] + [(40 * s, cy - 2 * s)], fill=(40, 110, 140, 255))
            for x in range(30, 100, 9):
                d.line([(x * s, cy - 14 * s), ((x + 5) * s, cy - 4 * s)], fill=(10, 40, 60, 255), width=int(2 * s))
        elif k == 1:    # 갈치
            body = [(4 * s, cy - 2 * s), (20 * s, cy - 9 * s), (110 * s, cy - 5 * s), (128 * s, cy), (110 * s, cy + 4 * s), (20 * s, cy + 8 * s)]
            d.polygon(body, fill=(225, 232, 245, 255), outline=(80, 90, 120, 255))
            d.line([(20 * s, cy - 8 * s), (110 * s, cy - 5 * s)], fill=(160, 175, 210, 255), width=int(2 * s))
            d.line([(14 * s, cy), (120 * s, cy)], fill=(255, 255, 255, 220), width=int(1.5 * s))
        elif k == 2:    # 참돔
            body = [(10 * s, cy + 2 * s), (36 * s, cy - 22 * s), (80 * s, cy - 20 * s), (108 * s, cy - 4 * s), (108 * s, cy + 4 * s), (80 * s, cy + 18 * s), (36 * s, cy + 18 * s)]
            d.polygon([(104 * s, cy), (126 * s, cy - 18 * s), (120 * s, cy), (126 * s, cy + 18 * s)], fill=(220, 70, 90, 255))
            d.polygon(body, fill=(240, 110, 120, 255), outline=(110, 20, 30, 255))
            for x in range(36, 96, 10):
                for y in (-10, -2, 6):
                    d.ellipse(((x - 1.5) * s, (cy / s + y - 1.5) * s, (x + 1.5) * s, (cy / s + y + 1.5) * s), fill=(120, 190, 255, 255))
        else:           # 광어
            d.ellipse((6 * s, cy - 20 * s, 104 * s, cy + 20 * s), fill=(150, 120, 80, 255), outline=(60, 40, 20, 255), width=int(1.2 * s))
            d.polygon([(100 * s, cy), (124 * s, cy - 14 * s), (124 * s, cy + 14 * s)], fill=(130, 100, 60, 255), outline=(60, 40, 20, 255))
            rng = random.Random(5)
            for _ in range(22):
                x, y = rng.uniform(20, 96), rng.uniform(-14, 14)
                d.ellipse(((x - 2) * s, (cy / s + y - 2) * s, (x + 2) * s, (cy / s + y + 2) * s), fill=(100, 70, 40, 200))
            d.ellipse((14 * s, cy - 12 * s, 22 * s, cy - 4 * s), fill=(255, 255, 255, 255))
            d.ellipse((24 * s, cy - 14 * s, 32 * s, cy - 6 * s), fill=(255, 255, 255, 255))
            d.ellipse((16 * s, cy - 10 * s, 20 * s, cy - 6 * s), fill=(0, 0, 0, 255))
            d.ellipse((26 * s, cy - 12 * s, 30 * s, cy - 8 * s), fill=(0, 0, 0, 255))
        if k != 3:
            ex = 20 if k != 1 else 14
            d.ellipse(((ex - 4) * s, cy - 8 * s, (ex + 4) * s, cy), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            d.ellipse(((ex - 1.5) * s, cy - 6 * s, (ex + 2) * s, cy - 2.5 * s), fill=(0, 0, 0, 255))
    return art('k03_fish_%d' % k, 130, 48, f)


def k03_stars(n):
    def f(d, im, s):
        for i in range(5):
            cx, cy = (9 + i * 17) * s, 8 * s
            pts = []
            for j in range(10):
                a = -math.pi / 2 + j * math.pi / 5
                r = (7.5 if j % 2 == 0 else 3.2) * s
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            d.polygon(pts, fill=(255, 200, 60, 255) if i < n else (60, 66, 96, 255), outline=(30, 20, 0, 255) if i < n else (110, 120, 160, 255))
    return art('k03_stars_%d' % n, 86, 16, f)


def k03_tray():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((1 * s, 4 * s, W - 1 * s, H - 1 * s), 6 * s, fill=(170, 200, 230, 255), outline=(40, 60, 100, 255), width=int(1.2 * s))
        rng = random.Random(8)
        for _ in range(40):
            x, y = rng.uniform(4, W / s - 4), rng.uniform(6, H / s - 4)
            d.rectangle(((x - 2) * s, (y - 1.5) * s, (x + 2) * s, (y + 1.5) * s), fill=(235, 245, 255, 220))
    return art('k03_tray', 170, 26, f)


# ================================================================== 4. 복숭아 바구니
def k04_basket():
    def f(d, im, s):
        W, H = im.size
        d.chord((4 * s, 4 * s, W - 4 * s, H * 2 - 14 * s), 180, 360, fill=(190, 140, 70, 255), outline=(80, 50, 20, 255), width=int(1.5 * s))
        d.rectangle((2 * s, H - 12 * s, W - 2 * s, H - 3 * s), fill=(150, 100, 40, 255), outline=(70, 40, 14, 255), width=int(1.2 * s))
        for k in range(1, 9):
            x = W * k / 9
            d.line([(x, H - 12 * s), (W / 2 + (x - W / 2) * 0.35, 8 * s)], fill=(140, 96, 40, 255), width=int(1 * s))
        for yy in (18, 30):
            d.arc((10 * s, yy * s, W - 10 * s, (yy + 40) * s), 200, 340, fill=(230, 190, 120, 255), width=int(1.2 * s))
        d.ellipse((W * 0.3, 10 * s, W * 0.48, 18 * s), fill=(255, 240, 200, 90))
    return art('k04_basket', 76, 58, f)


def k04_mat():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 8 * s, fill=(120, 40, 50, 230), outline=(240, 160, 170, 255), width=int(1.2 * s))
        for x in range(10, int(W / s), 14):
            d.line([(x * s, 4 * s), (x * s, H - 4 * s)], fill=(150, 60, 70, 200), width=int(1 * s))
    return art('k04_mat', 470, 30, f)


# ================================================================== 5. 커피
CUPS = [  # (내부 폭, 내부 높이, 손잡이)
    (40, 40, True),
    (50, 72, True),
    (54, 104, False),
]


def k05_cup(k):
    iw, ih, handle = CUPS[k]
    w, h = iw + 30, ih + 10

    def f(d, im, s):
        W, H = im.size
        x0, x1 = 15 * s - 3 * s, 15 * s + iw * s + 3 * s
        bot = H - 2 * s
        top = 4 * s
        if handle:
            d.arc((x1 - 6 * s, top + ih * 0.15 * s, x1 + 14 * s, top + ih * 0.7 * s), -80, 80, fill=(225, 235, 255, 255), width=int(4 * s))
        d.rectangle((x0, top, x0 + 3 * s, bot), fill=(220, 232, 255, 200))
        d.rectangle((x1 - 3 * s, top, x1, bot), fill=(220, 232, 255, 200))
        d.rectangle((x0, bot - 4 * s, x1, bot), fill=(220, 232, 255, 230))
        d.line([(x0 + 1.5 * s, top), (x0 + 1.5 * s, bot)], fill=(255, 255, 255, 255), width=int(1 * s))
        d.rectangle((x0 - 1 * s, top - 1 * s, x1 + 1 * s, top + 1 * s), fill=(255, 255, 255, 255))
        # 눈금 (5칸)
        for j in range(1, 5):
            y = bot - 4 * s - (ih - 4) * s * j / 5
            d.line([(x1 - 9 * s, y), (x1 - 3 * s, y)], fill=(255, 255, 255, 120), width=int(0.8 * s))
    return art('k05_cup_%d' % k, w, h, f)


def k05_foam(k):
    iw = CUPS[k][0]

    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((0, 0, W, H), 2 * s, fill=(214, 160, 96, 255))
        d.line([(1 * s, 1 * s), (W - 1 * s, 1 * s)], fill=(250, 214, 160, 255), width=int(1.2 * s))
    return art('k05_foam_%d' % k, iw, 4, f)


def k05_stream(k):
    wd = [2, 4, 6][k]

    def f(d, im, s):
        W, H = im.size
        d.rectangle((W / 2 - wd * s / 2, 0, W / 2 + wd * s / 2, H), fill=(90, 50, 20, 255))
        d.line([(W / 2 - wd * s / 4, 0), (W / 2 - wd * s / 4, H)], fill=(170, 110, 60, 200), width=max(1, int(wd * s / 4)))
    return art('k05_stream_%d' % k, 8, 150, f)


def k05_line(k):
    iw = CUPS[k][0]
    w = iw + 46

    def f(d, im, s):
        W, H = im.size
        y = H / 2
        for x in range(int(8 * s), int(W - 16 * s), int(5 * s)):
            d.line([(x, y), (x + 3 * s, y)], fill=(255, 80, 110, 255), width=int(1.6 * s))
        d.polygon([(W - 2 * s, y - 5 * s), (W - 12 * s, y), (W - 2 * s, y + 5 * s)], fill=(255, 80, 110, 255))
        d.polygon([(2 * s, y - 5 * s), (10 * s, y), (2 * s, y + 5 * s)], fill=(255, 80, 110, 255))
    return art('k05_line_%d' % k, w, 12, f)


def k05_machine():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((2 * s, 2 * s, W - 2 * s, 36 * s), 6 * s, fill=(70, 76, 96, 255), outline=(10, 12, 20, 255), width=int(1.5 * s))
        d.rounded_rectangle((6 * s, 6 * s, W - 6 * s, 16 * s), 3 * s, fill=(110, 118, 140, 255))
        d.rectangle((W / 2 - 22 * s, 36 * s, W / 2 + 22 * s, 44 * s), fill=(40, 44, 58, 255), outline=(10, 12, 20, 255))
        d.polygon([(W / 2 - 8 * s, 44 * s), (W / 2 + 8 * s, 44 * s), (W / 2 + 4 * s, 54 * s), (W / 2 - 4 * s, 54 * s)], fill=(150, 156, 176, 255), outline=(10, 12, 20, 255))
        d.ellipse((14 * s, 20 * s, 26 * s, 32 * s), fill=(255, 80, 100, 255))
        d.ellipse((W - 26 * s, 20 * s, W - 14 * s, 32 * s), fill=(90, 220, 140, 255))
        d.text((W / 2, 25 * s), 'ESPRESSO', font=font('jalnan', int(7 * s)), fill=(230, 236, 255, 255), anchor='mm')
    return art('k05_machine', 120, 56, f)


def k05_counter():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, H), fill=(110, 70, 40, 255))
        d.rectangle((0, 0, W, 4 * s), fill=(160, 110, 70, 255))
        for x in range(0, int(W / s), 22):
            d.line([(x * s, 5 * s), ((x + 12) * s, H)], fill=(90, 56, 30, 255), width=int(1 * s))
    return art('k05_counter', 220, 18, f)


# ================================================================== 6. 다트
DART_ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
DART_R = dict(bull=9, obull=19, t_in=52, t_out=64, d_in=88, d_out=100)


def k06_board():
    R = DART_R
    pad = 14
    size = (R['d_out'] + pad) * 2

    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((c - (R['d_out'] + pad) * s, c - (R['d_out'] + pad) * s, c + (R['d_out'] + pad) * s, c + (R['d_out'] + pad) * s),
                  fill=(16, 16, 22, 255), outline=(80, 80, 100, 255), width=int(1.5 * s))
        cols_a = [(20, 20, 24, 255), (236, 226, 200, 255)]
        cols_b = [(206, 40, 52, 255), (30, 150, 80, 255)]

        def wedge(r, i, col):
            a0 = -90 - 9 + i * 18
            d.pieslice((c - r * s, c - r * s, c + r * s, c + r * s), a0, a0 + 18, fill=col)
        for i in range(20):
            wedge(R['d_out'], i, cols_b[i % 2])
            wedge(R['d_in'], i, cols_a[i % 2])
            wedge(R['t_out'], i, cols_b[i % 2])
            wedge(R['t_in'], i, cols_a[i % 2])
        d.ellipse((c - R['obull'] * s, c - R['obull'] * s, c + R['obull'] * s, c + R['obull'] * s), fill=(30, 150, 80, 255))
        d.ellipse((c - R['bull'] * s, c - R['bull'] * s, c + R['bull'] * s, c + R['bull'] * s), fill=(206, 40, 52, 255))
        for r in (R['d_out'], R['d_in'], R['t_out'], R['t_in'], R['obull'], R['bull']):
            d.ellipse((c - r * s, c - r * s, c + r * s, c + r * s), outline=(190, 190, 200, 255), width=int(0.7 * s))
        for i in range(20):
            a = math.radians(-90 - 9 + i * 18)
            d.line([(c + R['obull'] * s * math.cos(a), c + R['obull'] * s * math.sin(a)),
                    (c + R['d_out'] * s * math.cos(a), c + R['d_out'] * s * math.sin(a))], fill=(190, 190, 200, 255), width=int(0.7 * s))
            am = math.radians(-90 + i * 18)
            rr = (R['d_out'] + pad / 2 + 0.5) * s
            d.text((c + rr * math.cos(am), c + rr * math.sin(am)), str(DART_ORDER[i]), font=font('jalnan', int(9 * s)),
                   fill=(255, 255, 255, 255), anchor='mm')
    return art('k06_board', size, size, f)


def k06_aim():
    def f(d, im, s):
        W = im.width
        c = W / 2
        for col, wd in (((0, 0, 0, 160), 3.2), ((255, 60, 90, 255), 1.6)):
            d.ellipse((c - 11 * s, c - 11 * s, c + 11 * s, c + 11 * s), outline=col, width=int(wd * s))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                d.line([(c + dx * 5 * s, c + dy * 5 * s), (c + dx * 15 * s, c + dy * 15 * s)], fill=col, width=int(wd * s))
        d.ellipse((c - 1.5 * s, c - 1.5 * s, c + 1.5 * s, c + 1.5 * s), fill=(255, 255, 255, 255))
    return art('k06_aim', 32, 32, f)


def k06_dart():
    """꽂힌 다트 (앞에서 비스듬히 본 모습). 끝이 그림 중심."""
    def f(d, im, s):
        W, H = im.size
        cx, cy = W / 2, H / 2
        d.line([(cx, cy), (cx + 9 * s, cy + 9 * s)], fill=(200, 200, 210, 255), width=int(2 * s))
        d.line([(cx + 8 * s, cy + 8 * s), (cx + 13 * s, cy + 13 * s)], fill=(40, 90, 230, 255), width=int(3.5 * s))
        d.polygon([(cx + 12 * s, cy + 12 * s), (cx + 20 * s, cy + 13 * s), (cx + 19 * s, cy + 19 * s), (cx + 13 * s, cy + 20 * s)],
                  fill=(255, 70, 110, 255), outline=(60, 0, 20, 255))
        d.ellipse((cx - 1.5 * s, cy - 1.5 * s, cx + 1.5 * s, cy + 1.5 * s), fill=(255, 255, 255, 255))
    return art('k06_dart', 42, 42, f)


# ================================================================== 8. 돌탑
STONE_W = [44, 62, 80, 98]
STONE_COL = [(120, 150, 255), (150, 120, 240), (90, 180, 200), (120, 130, 170)]


def k08_stone(k):
    w, h = STONE_W[k], 22

    def f(d, im, s):
        W, H = im.size
        base = (70 + k * 6, 72 + k * 6, 86 + k * 6)
        d.rounded_rectangle((1 * s, 2 * s, W - 1 * s, H - 1 * s), 9 * s, fill=_rgba(base), outline=_rgba(STONE_COL[k]), width=int(1.6 * s))
        d.rounded_rectangle((5 * s, 4 * s, W - 5 * s, 9 * s), 3 * s, fill=(255, 255, 255, 50))
        rng = random.Random(30 + k)
        for _ in range(int(w / 5)):
            x, y = rng.uniform(6, w - 6), rng.uniform(8, h - 6)
            r = rng.uniform(0.8, 1.8)
            d.ellipse(((x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s), fill=(30, 32, 44, 200))
        d.text((W / 2, H / 2 + 1 * s), str(k + 1), font=font('jalnan', int(10 * s)), fill=_rgba(STONE_COL[k]), anchor='mm')
    return art('k08_stone_%d' % k, w, h, f)


def k08_peg():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((W / 2 - 3 * s, 4 * s, W / 2 + 3 * s, H - 8 * s), 3 * s, fill=(150, 110, 70, 255), outline=(60, 40, 20, 255), width=int(1 * s))
        d.rounded_rectangle((2 * s, H - 14 * s, W - 2 * s, H - 2 * s), 6 * s, fill=(60, 66, 84, 255), outline=(140, 150, 190, 255), width=int(1.2 * s))
    return art('k08_peg', 116, 120, f)


def k08_hit():
    """기둥 클릭 영역 (거의 투명)."""
    def f(d, im, s):
        d.rounded_rectangle((2 * s, 2 * s, im.width - 2 * s, im.height - 2 * s), 10 * s, fill=(120, 150, 255, 28), outline=(120, 150, 255, 70), width=int(1 * s))
    return art('k08_hit2', 120, 160, f)


# ================================================================== 9. 감자 장사
def k09_stall():
    def f(d, im, s):
        W, H = im.size
        for i in range(8):
            col = (220, 60, 70, 255) if i % 2 == 0 else (245, 240, 230, 255)
            d.polygon([(i * W / 8, 0), ((i + 1) * W / 8, 0), ((i + 1) * W / 8, 18 * s), (i * W / 8, 18 * s)], fill=col)
            d.chord((i * W / 8, 10 * s, (i + 1) * W / 8, 26 * s), 0, 180, fill=col)
        d.rectangle((6 * s, 18 * s, 10 * s, H), fill=(100, 70, 40, 255))
        d.rectangle((W - 10 * s, 18 * s, W - 6 * s, H), fill=(100, 70, 40, 255))
        d.rectangle((2 * s, H - 34 * s, W - 2 * s, H - 2 * s), fill=(150, 100, 56, 255), outline=(60, 36, 14, 255), width=int(1.4 * s))
        d.text((W / 2, H - 18 * s), '평창 감자', font=font('nsr', int(11 * s)), fill=(255, 245, 220, 255), anchor='mm')
        rng = random.Random(4)
        for _ in range(26):
            x, y = rng.uniform(16, W / s - 16), rng.uniform(H / s - 48, H / s - 34)
            d.ellipse(((x - 7) * s, (y - 5) * s, (x + 7) * s, (y + 5) * s), fill=(196, 150, 90, 255), outline=(110, 70, 30, 255))
    return art('k09_stall2', 150, 96, f)


def k09_weather(k):
    """0 맑음, 1 비, 2 무더위, 3 흐림."""
    def f(d, im, s):
        W = im.width
        c = W / 2
        if k in (0, 2):
            col = (255, 200, 60) if k == 0 else (255, 110, 50)
            for i in range(8):
                a = math.radians(i * 45)
                d.line([(c + 13 * s * math.cos(a), c + 13 * s * math.sin(a)), (c + 18 * s * math.cos(a), c + 18 * s * math.sin(a))],
                       fill=_rgba(col), width=int(2.5 * s))
            d.ellipse((c - 10 * s, c - 10 * s, c + 10 * s, c + 10 * s), fill=_rgba(col), outline=(120, 60, 0, 255))
            if k == 2:
                for x in (-6, 0, 6):
                    d.arc(((c / s + x - 2) * s, c + 2 * s, (c / s + x + 2) * s, c + 8 * s), 0, 180, fill=(255, 255, 255, 255), width=int(1 * s))
        else:
            d.ellipse((c - 16 * s, c - 6 * s, c + 2 * s, c + 8 * s), fill=(200, 210, 230, 255))
            d.ellipse((c - 8 * s, c - 14 * s, c + 12 * s, c + 6 * s), fill=(220, 228, 245, 255))
            d.rounded_rectangle((c - 16 * s, c - 2 * s, c + 17 * s, c + 8 * s), 5 * s, fill=(210, 220, 238, 255))
            if k == 1:
                for x in (-10, -2, 6, 14):
                    d.line([((c / s + x) * s, c + 11 * s), ((c / s + x - 3) * s, c + 18 * s)], fill=(90, 150, 255, 255), width=int(2 * s))
    return art('k09_wx_%d' % k, 40, 40, f)


def k09_cust(k):
    cols = [(60, 110, 230), (220, 80, 110), (60, 170, 120), (170, 110, 230)]

    def f(d, im, s):
        W, H = im.size
        c = W / 2
        col = _rgba(cols[k])
        d.ellipse((c - 5 * s, 1 * s, c + 5 * s, 11 * s), fill=(255, 214, 180, 255), outline=(60, 40, 30, 255))
        d.rounded_rectangle((c - 7 * s, 11 * s, c + 7 * s, 28 * s), 4 * s, fill=col, outline=(10, 10, 20, 255))
        d.rectangle((c - 5 * s, 27 * s, c - 1 * s, H - 1 * s), fill=(40, 44, 70, 255))
        d.rectangle((c + 1 * s, 27 * s, c + 5 * s, H - 1 * s), fill=(40, 44, 70, 255))
    return art('k09_cust_%d' % k, 18, 38, f)


def k09_potato():
    def f(d, im, s):
        W, H = im.size
        d.ellipse((1 * s, 1 * s, W - 1 * s, H - 1 * s), fill=(200, 150, 90, 255), outline=(100, 64, 26, 255), width=int(1 * s))
        for x, y in ((5, 4), (9, 7), (12, 4)):
            d.ellipse(((x - 0.8) * s, (y - 0.8) * s, (x + 0.8) * s, (y + 0.8) * s), fill=(120, 80, 40, 255))
    return art('k09_potato', 16, 12, f)


# ================================================================== 10. 수영
def k10_swimmer(frame, cap):
    """옆에서 본 자유형. frame 0~7 (팔 각도 45도씩), 머리는 오른쪽."""
    def f(d, im, s):
        W, H = im.size
        wy = H * 0.55
        skin = (250, 205, 170, 255)
        capc = {'me': (40, 100, 255, 255), 'r': (230, 50, 70, 255), 'r2': (170, 90, 255, 255)}[cap]
        # 다리 (물장구)
        kick = math.sin(frame * math.pi / 2) * 3
        d.line([(10 * s, wy + kick * s), (26 * s, wy + 1 * s)], fill=skin, width=int(4 * s))
        d.line([(10 * s, wy - kick * s + 2 * s), (26 * s, wy + 2 * s)], fill=(230, 185, 150, 255), width=int(4 * s))
        # 몸통
        d.rounded_rectangle((22 * s, wy - 5 * s, 56 * s, wy + 4 * s), 4 * s, fill=(30, 40, 80, 255))
        # 팔: 어깨(52, wy-2) 중심 회전, 0번 = 앞으로 뻗음(물 위)
        sx, sy = 52 * s, wy - 2 * s
        a = math.radians(frame * 45)
        L = 18 * s
        ex, ey = sx + L * math.cos(a), sy + L * math.sin(a) * 0.9
        d.line([(sx, sy), (ex, ey)], fill=skin, width=int(4.5 * s))
        d.ellipse((ex - 2.5 * s, ey - 2.5 * s, ex + 2.5 * s, ey + 2.5 * s), fill=skin)
        # 반대팔 (반 바퀴 차이)
        a2 = a + math.pi
        ex2, ey2 = sx + L * math.cos(a2), sy + L * math.sin(a2) * 0.9
        d.line([(sx, sy), (ex2, ey2)], fill=(225, 180, 145, 255), width=int(4 * s))
        # 머리
        d.ellipse((54 * s, wy - 9 * s, 68 * s, wy + 3 * s), fill=skin, outline=(80, 50, 30, 255))
        d.chord((54 * s, wy - 10 * s, 68 * s, wy + 2 * s), 180, 360, fill=capc)
        d.ellipse((62 * s, wy - 6 * s, 67 * s, wy - 2 * s), fill=(120, 200, 255, 255), outline=(10, 10, 20, 255))
        # 물결
        for x in range(0, int(W / s), 8):
            d.arc((x * s, wy - 1 * s, (x + 8) * s, wy + 3 * s), 180, 360, fill=(220, 240, 255, 230), width=int(1.2 * s))
    return art('k10_sx_%s_%d' % (cap, frame), 72, 34, f)


def k10_lane():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, H), fill=(20, 80, 170, 150))
        for x in range(0, int(W / s), 30):
            d.line([(x * s, 10 * s), ((x + 14) * s, 10 * s)], fill=(160, 210, 255, 90), width=int(1 * s))
            d.line([((x + 12) * s, 26 * s), ((x + 26) * s, 26 * s)], fill=(160, 210, 255, 70), width=int(1 * s))
        for x in range(0, int(W / s) + 6, 6):
            col = (255, 80, 90, 255) if (x // 6) % 4 < 2 else (255, 255, 255, 255)
            d.ellipse((x * s - 2.5 * s, H - 5 * s, x * s + 2.5 * s, H), fill=col)
    return art('k10_lane', 480, 44, f)


def k10_buoy():
    def f(d, im, s):
        W, H = im.size
        d.line([(W / 2, 2 * s), (W / 2, H - 10 * s)], fill=(230, 230, 240, 255), width=int(1.5 * s))
        d.polygon([(W / 2, 2 * s), (W / 2 + 12 * s, 6 * s), (W / 2, 10 * s)], fill=(255, 60, 80, 255))
        d.ellipse((W / 2 - 8 * s, H - 16 * s, W / 2 + 8 * s, H - 2 * s), fill=(255, 120, 30, 255), outline=(100, 30, 0, 255))
        d.rectangle((W / 2 - 8 * s, H - 10 * s, W / 2 + 8 * s, H - 8 * s), fill=(255, 255, 255, 255))
    return art('k10_buoy', 28, 40, f)


def k10_splash():
    def f(d, im, s):
        W, H = im.size
        rng = random.Random(7)
        for _ in range(16):
            x, y = rng.uniform(4, W / s - 4), rng.uniform(4, H / s - 4)
            r = rng.uniform(1.5, 4)
            d.ellipse(((x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s), fill=(220, 240, 255, 230))
    return art('k10_splash', 36, 24, f)


def k10_gauge():
    """스트로크 고리: 아래쪽(입수) 구간이 초록."""
    def f(d, im, s):
        W = im.width
        c = W / 2
        r = 22 * s
        d.ellipse((c - r, c - r, c + r, c + r), fill=(6, 10, 30, 220), outline=(120, 140, 220, 255), width=int(2 * s))
        # 입수 구간: 오른쪽 아래 (frame 1~2 사이 → 각도 45~90, 엔트리 회전과 맞춤)
        bb = (c - r + 3 * s, c - r + 3 * s, c + r - 3 * s, c + r - 3 * s)
        d.pieslice(bb, -35, 75, fill=(40, 120, 80, 255))
        d.pieslice(bb, -10, 50, fill=(60, 230, 120, 255))
        d.ellipse((c - 9 * s, c - 9 * s, c + 9 * s, c + 9 * s), fill=(6, 10, 30, 255))
    return art('k10_gauge2', 50, 50, f)


def k10_needle():
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.line([(c, c), (c + 21 * s, c)], fill=(255, 255, 255, 255), width=int(2.5 * s))
        d.ellipse((c - 3 * s, c - 3 * s, c + 3 * s, c + 3 * s), fill=(255, 255, 255, 255))
    return art('k10_needle', 50, 50, f)
