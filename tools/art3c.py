# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 21~30번 그림 (mg_art3.art 로 2배 해상도 저장, 크기 인자는 무대 px)."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3



def art(name, w, h, draw, colors=96):
    """A3.art 로 그린 뒤 팔레트 PNG 로 줄여 저장 (용량 1/3 정도)."""
    p = A3.art(name, w, h, draw)
    im = Image.open(p)
    if im.mode != 'P':
        im.quantize(colors=colors, method=Image.Quantize.FASTOCTREE).save(p, optimize=True)
    return p


def _c(col, a=255):
    return tuple(col[:3]) + (a,)


def _glow_disc(d, cx, cy, r, col, steps=8, amax=90):
    for k in range(steps, 0, -1):
        rr = r * k / steps
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=_c(col, int(amax * (1 - k / steps) + 8)))


# ================================================================== 21 테이블 하키
def hockey_table(w=440, h=200, goal_h=68):
    def f(d, im, s):
        W, H = im.width, im.height
        rim = 10 * s
        d.rounded_rectangle((0, 0, W - 1, H - 1), 22 * s, fill=(34, 52, 120, 255), outline=(150, 176, 255, 255), width=int(1.5 * s))
        d.rounded_rectangle((4 * s, 4 * s, W - 4 * s, H - 4 * s), 19 * s, outline=(80, 108, 210, 255), width=int(1 * s))
        x0, y0, x1, y1 = rim, rim, W - rim, H - rim
        d.rounded_rectangle((x0, y0, x1, y1), 14 * s, fill=(14, 22, 58, 255), outline=(190, 210, 255, 255), width=int(1.2 * s))
        # 공기 구멍
        for yy in range(int(y0 + 10 * s), int(y1 - 6 * s), int(14 * s)):
            for xx in range(int(x0 + 10 * s), int(x1 - 6 * s), int(14 * s)):
                d.ellipse((xx - 0.7 * s, yy - 0.7 * s, xx + 0.7 * s, yy + 0.7 * s), fill=(44, 60, 120, 255))
        cx, cy = W / 2, H / 2
        d.line((cx, y0, cx, y1), fill=(120, 150, 255, 200), width=int(1.6 * s))
        r = 30 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(120, 150, 255, 200), width=int(1.6 * s))
        d.ellipse((cx - 4 * s, cy - 4 * s, cx + 4 * s, cy + 4 * s), fill=(120, 150, 255, 220))
        gh = goal_h * s / 2
        for side, col in ((0, (80, 150, 255)), (1, (255, 80, 100))):
            gx = x0 if side == 0 else x1
            r2 = 42 * s
            box = (gx - r2, cy - r2, gx + r2, cy + r2)
            d.arc(box, -90 if side == 0 else 90, 90 if side == 0 else 270, fill=_c(col, 220), width=int(1.6 * s))
            # 골문 (틈)
            gx0 = 0 if side == 0 else x1 - 1 * s
            gx1 = x0 + 1 * s if side == 0 else W
            d.rectangle((gx0, cy - gh, gx1, cy + gh), fill=(4, 6, 16, 255))
            for k in range(6):
                a = 200 - k * 30
                xx = (x0 + k * s) if side == 0 else (x1 - k * s)
                d.line((xx, cy - gh, xx, cy + gh), fill=_c(col, a), width=int(1 * s))
            d.ellipse((gx - 3 * s, cy - gh - 3 * s, gx + 3 * s, cy - gh + 3 * s), fill=(230, 236, 255, 255))
            d.ellipse((gx - 3 * s, cy + gh - 3 * s, gx + 3 * s, cy + gh + 3 * s), fill=(230, 236, 255, 255))
    return art('k21_table', w, h, f)


def hockey_puck(r=10):
    def f(d, im, s):
        W = im.width
        d.ellipse((0.5 * s, 1.5 * s, W - 0.5 * s, W - 0.2 * s), fill=(0, 0, 0, 120))
        d.ellipse((s, s, W - s, W - 2 * s), fill=(250, 210, 70, 255), outline=(120, 80, 0, 255), width=int(1 * s))
        d.ellipse((W * 0.26, W * 0.24, W * 0.74, W * 0.66), outline=(255, 244, 190, 255), width=int(1 * s))
        d.ellipse((W * 0.3, W * 0.18, W * 0.5, W * 0.32), fill=(255, 255, 255, 140))
    return art('k21_puck', r * 2, r * 2, f)


def hockey_mallet(kind, r=15):
    col = {'me': ((90, 150, 255), (20, 50, 170)), 'ai': ((255, 100, 120), (150, 20, 40))}[kind]

    def f(d, im, s):
        W = im.width
        d.ellipse((s, 2 * s, W - s, W), fill=(0, 0, 0, 110))
        d.ellipse((s, s, W - s, W - 2 * s), fill=_c(col[1]), outline=(255, 255, 255, 255), width=int(1.2 * s))
        d.ellipse((W * 0.16, W * 0.14, W * 0.84, W * 0.8), fill=_c(col[0]))
        d.ellipse((W * 0.32, W * 0.3, W * 0.68, W * 0.64), fill=_c(col[1]), outline=(255, 255, 255, 180), width=int(0.8 * s))
        d.ellipse((W * 0.36, W * 0.32, W * 0.5, W * 0.42), fill=(255, 255, 255, 170))
    return art('k21_mallet_%s' % kind, r * 2, r * 2, f)


def score_pill(w=150, h=22):
    def f(d, im, s):
        d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height / 2, fill=(6, 10, 30, 225),
                            outline=(110, 140, 255, 255), width=int(1 * s))
    return art('k2x_pill_%d_%d' % (w, h), w, h, f)


# ================================================================== 22 눈길 운전
def snow_road(w=124, h=26):
    def f(d, im, s):
        W, H = im.width, im.height
        bank = 12 * s
        d.rectangle((0, 0, W, H), fill=(0, 0, 0, 0))
        # 눈둑
        d.rounded_rectangle((0, 0, bank + 4 * s, H), 5 * s, fill=(236, 242, 255, 255))
        d.rounded_rectangle((W - bank - 4 * s, 0, W, H), 5 * s, fill=(236, 242, 255, 255))
        # 아스팔트
        d.rectangle((bank, 0, W - bank, H), fill=(62, 70, 96, 255))
        rnd = random.Random(7)
        for _ in range(26):
            x = rnd.uniform(bank + 2 * s, W - bank - 2 * s)
            y = rnd.uniform(0, H)
            r = rnd.uniform(0.6, 1.6) * s
            d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 162, 196, 140))
        # 바퀴 자국 (밝은 눈 사이)
        for xx in (0.3, 0.7):
            d.line((W * xx, 0, W * xx, H), fill=(52, 58, 84, 255), width=int(4 * s))
        # 가장자리 흰 선
        d.line((bank + 2.5 * s, 0, bank + 2.5 * s, H), fill=(250, 250, 255, 255), width=int(1.6 * s))
        d.line((W - bank - 2.5 * s, 0, W - bank - 2.5 * s, H), fill=(250, 250, 255, 255), width=int(1.6 * s))
        # 가운데 노란 점선 (한 칸에 하나)
        d.rectangle((W / 2 - 1.2 * s, H * 0.18, W / 2 + 1.2 * s, H * 0.62), fill=(255, 196, 40, 255))
    return art('k22_road', w, h, f)


def snow_car():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((1.5 * s, 3 * s, W - 1.5 * s, H - 2 * s), 6 * s, fill=(0, 0, 0, 90))
        for x0 in (0.5 * s, W - 4 * s):
            for y0 in (6 * s, H - 13 * s):
                d.rounded_rectangle((x0, y0, x0 + 3.5 * s, y0 + 7 * s), 1.5 * s, fill=(20, 20, 26, 255))
        d.rounded_rectangle((2.5 * s, 1 * s, W - 2.5 * s, H - 3 * s), 6 * s, fill=(40, 96, 230, 255), outline=(200, 220, 255, 255),
                            width=int(1 * s))
        d.rounded_rectangle((5 * s, 8 * s, W - 5 * s, 15 * s), 2 * s, fill=(160, 210, 255, 255))     # 앞유리
        d.rounded_rectangle((5 * s, H - 12 * s, W - 5 * s, H - 7 * s), 2 * s, fill=(120, 170, 240, 255))  # 뒷유리
        d.rectangle((5 * s, 15.5 * s, W - 5 * s, H - 12.5 * s), fill=(30, 76, 200, 255))
        d.rectangle((W / 2 - 1 * s, 15.5 * s, W / 2 + 1 * s, H - 12.5 * s), fill=(240, 244, 255, 255))  # 띠
        d.ellipse((3.5 * s, 1.5 * s, 7.5 * s, 4.5 * s), fill=(255, 250, 200, 255))
        d.ellipse((W - 7.5 * s, 1.5 * s, W - 3.5 * s, 4.5 * s), fill=(255, 250, 200, 255))
        d.rectangle((3.5 * s, H - 5 * s, 7 * s, H - 3.5 * s), fill=(255, 60, 70, 255))
        d.rectangle((W - 7 * s, H - 5 * s, W - 3.5 * s, H - 3.5 * s), fill=(255, 60, 70, 255))
    return art('k22_car', 20, 34, f)


def snow_pine(r=18):
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((c - W * 0.42 + 2 * s, c - W * 0.42 + 3 * s, c + W * 0.42 + 2 * s, c + W * 0.42 + 3 * s), fill=(40, 60, 110, 70))
        for k, (rr, col) in enumerate(((0.46, (24, 84, 70)), (0.34, (34, 110, 86)), (0.2, (50, 136, 104)))):
            pts = []
            for i in range(28):
                a = math.radians(i * 360 / 28 + k * 7)
                q = W * rr * (1.0 if i % 2 == 0 else 0.86)
                pts.append((c + q * math.cos(a), c + q * math.sin(a)))
            d.polygon(pts, fill=_c(col))
        rnd = random.Random(3)
        for _ in range(9):
            a = rnd.uniform(0, 6.28)
            q = rnd.uniform(0.05, 0.36) * W
            x, y = c + q * math.cos(a), c + q * math.sin(a)
            rr = rnd.uniform(1.5, 3.2) * s
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(240, 246, 255, 235))
    return art('k22_pine', r * 2, r * 2, f)


def snowflake(r=3):
    def f(d, im, s):
        W = im.width
        _glow_disc(d, W / 2, W / 2, W / 2, (255, 255, 255), 6, 255)
    return art('k22_flake', r * 2, r * 2, f)


def snow_field():
    def f(d, im, s):
        d.rectangle((0, 0, im.width, im.height), fill=(206, 218, 242, 255))
    return art('k22_field', 480, 236, f)


# ================================================================== 23 크레인 운전
CONT_COLS = [(220, 70, 80), (60, 130, 240), (250, 170, 50), (60, 180, 120), (160, 100, 240)]


def container(i, w=28, h=22):
    col = CONT_COLS[i]

    def f(d, im, s):
        W, H = im.width, im.height
        dark = tuple(int(c * 0.55) for c in col)
        d.rectangle((0, 0, W - 1, H - 1), fill=_c(col), outline=_c(dark), width=int(1.2 * s))
        for k in range(1, 7):
            x = W * k / 7
            d.line((x, 2 * s, x, H - 2 * s), fill=_c(dark, 200), width=int(0.8 * s))
        d.rectangle((0, 0, W - 1, 2.2 * s), fill=_c(dark))
        d.rectangle((0, H - 2.2 * s, W - 1, H - 1), fill=_c(dark))
        d.rectangle((W * 0.3, H * 0.36, W * 0.7, H * 0.62), fill=(255, 255, 255, 230))
        d.text((W / 2, H * 0.5), 'K%d' % (i + 1), font=font('jalnan', int(5.5 * s)), fill=_c(dark), anchor='mm')
    return art('k23_box%d' % i, w, h, f)


def crane_rail(w=480, h=14):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 2 * s, W, H - 2 * s), fill=(220, 70, 60, 255))
        d.rectangle((0, 2 * s, W, 4 * s), fill=(255, 140, 120, 255))
        d.rectangle((0, H - 4 * s, W, H - 2 * s), fill=(120, 30, 30, 255))
        step = 16 * s
        x = 0
        while x < W:
            d.line((x, 4 * s, x + step / 2, H - 4 * s), fill=(150, 40, 36, 255), width=int(1.2 * s))
            d.line((x + step / 2, H - 4 * s, x + step, 4 * s), fill=(150, 40, 36, 255), width=int(1.2 * s))
            x += step
    return art('k23_rail', w, h, f)


def trolley():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((1 * s, 3 * s, W - 1 * s, H - 3 * s), 2 * s, fill=(250, 200, 60, 255), outline=(90, 60, 0, 255),
                            width=int(1 * s))
        d.rectangle((4 * s, 6 * s, W - 4 * s, 10 * s), fill=(40, 40, 60, 255))
        for x in (5 * s, W - 5 * s):
            d.ellipse((x - 3 * s, H - 6 * s, x + 3 * s, H), fill=(40, 40, 50, 255))
    return art('k23_trolley', 30, 20, f)


def hook(steady):
    def f(d, im, s):
        W, H = im.width, im.height
        c = W / 2
        if steady:
            _glow_disc(d, c, H * 0.45, W / 2, (80, 255, 150), 8, 120)
        d.rectangle((c - 6 * s, 1 * s, c + 6 * s, 7 * s), fill=(250, 200, 60, 255), outline=(90, 60, 0, 255), width=int(0.8 * s))
        d.arc((c - 6 * s, 6 * s, c + 6 * s, 18 * s), 200, 160 + 360 - 20, fill=(210, 220, 240, 255), width=int(2 * s))
        d.line((c, 6 * s, c, 9 * s), fill=(210, 220, 240, 255), width=int(2 * s))
    return art('k23_hook%d' % steady, 20, 20, f)


def quay(w=172, h=44):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(120, 128, 150, 255))
        d.rectangle((0, 0, W, 3 * s), fill=(250, 210, 60, 255))
        for x in range(0, int(W), int(12 * s)):
            d.line((x, 0, x + 6 * s, 3 * s), fill=(40, 40, 50, 255), width=int(2 * s))
        for y in range(int(8 * s), int(H), int(10 * s)):
            d.line((0, y, W, y), fill=(96, 104, 126, 255), width=int(0.8 * s))
        d.rectangle((W - 6 * s, 3 * s, W - 2 * s, 9 * s), fill=(40, 40, 50, 255))
    return art('k23_quay', w, h, f)


def ship(w=272, h=58, spots=(), spot_w=30):
    """spots: 갑판 위 표시 x (그림 왼쪽 기준 무대 px)."""
    def f(d, im, s):
        W, H = im.width, im.height
        deck = 10 * s
        d.polygon([(0, deck), (W, deck), (W - 22 * s, H), (16 * s, H)], fill=(30, 40, 84, 255))
        d.polygon([(0, deck), (W, deck), (W - 6 * s, deck + 14 * s), (4 * s, deck + 14 * s)], fill=(200, 54, 60, 255))
        d.rectangle((0, deck - 2 * s, W, deck + 2 * s), fill=(230, 236, 250, 255))
        d.rectangle((0, 0, W, deck - 2 * s), fill=(0, 0, 0, 0))
        for k in range(8):
            x = 20 * s + k * 32 * s
            d.ellipse((x, deck + 22 * s, x + 6 * s, deck + 28 * s), fill=(160, 190, 255, 255))
        d.text((W - 60 * s, deck + 32 * s), 'KOREA', font=font('jalnan', int(9 * s)), fill=(230, 236, 255, 255), anchor='mm')
        for sx in spots:
            x0, x1 = (sx - spot_w / 2) * s, (sx + spot_w / 2) * s
            for k in range(0, int(spot_w), 6):
                d.line((x0 + k * s, deck - 3 * s, x0 + (k + 3) * s, deck - 3 * s), fill=(120, 255, 170, 255), width=int(1.6 * s))
            d.line((x0, deck - 8 * s, x0, deck - 2 * s), fill=(120, 255, 170, 255), width=int(1.6 * s))
            d.line((x1, deck - 8 * s, x1, deck - 2 * s), fill=(120, 255, 170, 255), width=int(1.6 * s))
    return art('k23_ship', w, h, f)


def spot_marker(w=30, h=22):
    def f(d, im, s):
        W, H = im.width, im.height
        for k in range(0, int(W), int(4 * s)):
            d.line((k, 0, k + 2 * s, 0), fill=(120, 255, 170, 220), width=int(1.4 * s))
            d.line((k, H - 1, k + 2 * s, H - 1), fill=(120, 255, 170, 220), width=int(1.4 * s))
        for k in range(0, int(H), int(4 * s)):
            d.line((0, k, 0, k + 2 * s), fill=(120, 255, 170, 220), width=int(1.4 * s))
            d.line((W - 1, k, W - 1, k + 2 * s), fill=(120, 255, 170, 220), width=int(1.4 * s))
        d.rectangle((0, 0, W, H), fill=(120, 255, 170, 40))
    return art('k23_spot', w, h, f)


# ================================================================== 24 야구 타격
def _person(d, s, cx, by, scale, jersey, pants, helmet, arm_pose, skin=(240, 200, 170)):
    """간단한 사람 (뒤/옆 모습). by: 발 y. arm_pose: 팔 끝점 [(x, y)] (상대 좌표)."""
    u = s * scale
    # 다리
    d.rounded_rectangle((cx - 9 * u, by - 26 * u, cx - 2 * u, by), 3 * u, fill=_c(pants))
    d.rounded_rectangle((cx + 2 * u, by - 26 * u, cx + 9 * u, by), 3 * u, fill=_c(pants))
    d.ellipse((cx - 11 * u, by - 4 * u, cx - 1 * u, by + 1 * u), fill=(30, 30, 40, 255))
    d.ellipse((cx + 1 * u, by - 4 * u, cx + 11 * u, by + 1 * u), fill=(30, 30, 40, 255))
    # 몸
    d.rounded_rectangle((cx - 11 * u, by - 52 * u, cx + 11 * u, by - 22 * u), 6 * u, fill=_c(jersey))
    # 팔
    for (ax, ay) in arm_pose:
        d.line((cx, by - 46 * u, cx + ax * u, by - 46 * u + ay * u), fill=_c(jersey), width=int(6 * u))
        d.ellipse((cx + ax * u - 3 * u, by - 46 * u + ay * u - 3 * u, cx + ax * u + 3 * u, by - 46 * u + ay * u + 3 * u), fill=_c(skin))
    # 머리
    d.ellipse((cx - 8 * u, by - 68 * u, cx + 8 * u, by - 52 * u), fill=_c(skin))
    d.chord((cx - 9 * u, by - 70 * u, cx + 9 * u, by - 54 * u), 180, 360, fill=_c(helmet))
    d.rectangle((cx - 9 * u, by - 62 * u, cx + 12 * u, by - 60 * u), fill=_c(helmet))


def pitcher(pose):
    arms = {'set': [(-6, 10), (6, 10)], 'wind': [(-12, -14), (10, -20)], 'throw': [(-10, 8), (14, 14)]}[pose]

    def f(d, im, s):
        W, H = im.width, im.height
        _person(d, s, W / 2, H - 1 * s, 0.5, (200, 50, 60), (230, 230, 236), (150, 20, 30), arms)
    return art('k24_pitcher_%s' % pose, 30, 40, f)


def batter(pose):
    """오른손 타자 옆모습 (오른쪽 = 홈 플레이트 쪽). 방망이 자세 3가지."""
    def f(d, im, s):
        u = s
        P = lambda x, y: (x * u, y * u)
        jersey, pants, helmet, skin = (40, 90, 220), (235, 238, 245), (20, 40, 120), (240, 200, 170)
        hands = {'ready': (26, 22), 'swing': (50, 34), 'follow': (30, 24)}[pose]
        tip = {'ready': (15, 7), 'swing': (94, 30), 'follow': (4, 34)}[pose]
        # 다리
        d.line([P(30, 50), P(20, 80)], fill=_c(pants), width=int(8 * u))
        d.line([P(36, 50), P(48, 80)], fill=_c(pants), width=int(8 * u))
        d.ellipse((*P(13, 77), *P(25, 83)), fill=(30, 30, 40, 255))
        d.ellipse((*P(44, 77), *P(56, 83)), fill=(30, 30, 40, 255))
        # 몸
        d.rounded_rectangle((*P(22, 24), *P(42, 54)), 7 * u, fill=_c(jersey))
        d.text(P(31, 39), '7', font=font('jalnan', int(11 * u)), fill=(255, 255, 255, 255), anchor='mm')
        # 방망이 (손 뒤로)
        hx, hy = P(*hands)
        tx, ty = P(*tip)
        d.line((hx, hy, tx, ty), fill=(120, 70, 30, 255), width=int(3.5 * u))
        d.line((hx + (tx - hx) * 0.45, hy + (ty - hy) * 0.45, tx, ty), fill=(214, 150, 80, 255), width=int(6 * u))
        d.ellipse((tx - 3 * u, ty - 3 * u, tx + 3 * u, ty + 3 * u), fill=(214, 150, 80, 255))
        # 팔
        d.line([P(33, 28), (hx, hy)], fill=_c(jersey), width=int(6 * u))
        d.ellipse((hx - 3.5 * u, hy - 3.5 * u, hx + 3.5 * u, hy + 3.5 * u), fill=_c(skin))
        # 머리 + 헬멧 (오른쪽을 봄)
        d.ellipse((*P(25, 6), *P(41, 22)), fill=_c(skin))
        d.chord((*P(23, 3), *P(41, 21)), 180, 360, fill=_c(helmet))
        d.rectangle((*P(23, 11), *P(32, 18)), fill=_c(helmet))
        d.rectangle((*P(36, 11), *P(46, 13)), fill=_c(helmet))
        d.ellipse((*P(37, 14), *P(39, 16)), fill=(20, 20, 30, 255))
    return art('k24_batter2_%s' % pose, 96, 84, f)


def baseball(r=7):
    def f(d, im, s):
        W = im.width
        d.ellipse((0.5 * s, 0.5 * s, W - 0.5 * s, W - 0.5 * s), fill=(250, 250, 248, 255), outline=(150, 150, 160, 255), width=int(0.6 * s))
        d.arc((-W * 0.45, W * 0.1, W * 0.45, W * 0.9), -50, 50, fill=(220, 40, 50, 255), width=int(0.9 * s))
        d.arc((W * 0.55, W * 0.1, W * 1.45, W * 0.9), 130, 230, fill=(220, 40, 50, 255), width=int(0.9 * s))
    return art('k24_ball', r * 2, r * 2, f)


def strike_zone(w=50, h=56):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W - 1, H - 1), fill=(255, 255, 255, 18), outline=(255, 255, 255, 150), width=int(1.2 * s))
        for k in (1, 2):
            d.line((W * k / 3, 0, W * k / 3, H), fill=(255, 255, 255, 50), width=int(0.6 * s))
            d.line((0, H * k / 3, W, H * k / 3), fill=(255, 255, 255, 50), width=int(0.6 * s))
    return art('k24_zone', w, h, f)


def home_plate(w=44, h=22):
    def f(d, im, s):
        W, H = im.width, im.height
        d.polygon([(0, 0), (W, 0), (W, H * 0.45), (W / 2, H), (0, H * 0.45)], fill=(245, 245, 250, 255), outline=(150, 150, 170, 255))
    return art('k24_plate', w, h, f)


def mound(w=70, h=22):
    def f(d, im, s):
        W, H = im.width, im.height
        d.ellipse((0, 0, W, H), fill=(170, 110, 70, 255))
        d.rectangle((W * 0.38, H * 0.4, W * 0.62, H * 0.52), fill=(250, 250, 250, 255))
    return art('k24_mound', w, h, f)


# ================================================================== 25 매듭 잇기
FLOW_COLS = [(240, 70, 84), (70, 140, 255), (250, 204, 50), (60, 204, 120), (200, 100, 245)]
FLOW_TYPES = ['u', 'r', 'd', 'l', 'ud', 'lr', 'ur', 'rd', 'dl', 'lu', 'o', 'ou', 'or', 'od', 'ol']


def flow_cell(ci, ty, cs=38):
    col = FLOW_COLS[ci]

    def f(d, im, s):
        W = im.width
        c = W / 2
        d.rounded_rectangle((1.5 * s, 1.5 * s, W - 1.5 * s, W - 1.5 * s), 4 * s, fill=_c(col, 46))
        arms = ty.replace('o', '')
        lw = 11 * s
        ends = {'u': (c, 0), 'd': (c, W), 'l': (0, c), 'r': (W, c)}
        for a in arms:
            d.line((c, c, ends[a][0], ends[a][1]), fill=_c(col), width=int(lw))
        if 'o' not in ty:
            d.ellipse((c - lw / 2, c - lw / 2, c + lw / 2, c + lw / 2), fill=_c(col))
        else:
            r = 13 * s
            d.ellipse((c - r, c - r, c + r, c + r), fill=_c(col), outline=(255, 255, 255, 255), width=int(1.4 * s))
            d.ellipse((c - r * 0.55, c - r * 0.7, c - r * 0.05, c - r * 0.25), fill=(255, 255, 255, 110))
    return art('k25_c%d_%s' % (ci, ty), cs, cs, f)


def flow_board(n=5, cs=38):
    def f(d, im, s):
        W = im.width
        pad = 3 * s
        d.rounded_rectangle((0, 0, W - 1, W - 1), 8 * s, fill=(8, 12, 30, 240), outline=(110, 140, 255, 255), width=int(1.5 * s))
        for r in range(n):
            for k in range(n):
                x0, y0 = pad + k * cs * s, pad + r * cs * s
                d.rounded_rectangle((x0 + 1.2 * s, y0 + 1.2 * s, x0 + cs * s - 1.2 * s, y0 + cs * s - 1.2 * s), 4 * s,
                                    fill=(22, 28, 60, 255), outline=(52, 62, 110, 255), width=int(0.8 * s))
    return art('k25_board', n * cs + 6, n * cs + 6, f)


def blank(w, h, name='k2x_blank'):
    return art('%s_%d_%d' % (name, w, h), w, h, lambda d, im, s: None)


# ================================================================== 26 관광객 통역
FLAGS = ['일본', '중국', '미국', '프랑스', '스페인', '독일', '이탈리아', '베트남', '태국', '인도', '러시아', '브라질']


def _star(d, cx, cy, r, col, rot=-90):
    pts = []
    for i in range(10):
        a = math.radians(rot + i * 36)
        q = r if i % 2 == 0 else r * 0.42
        pts.append((cx + q * math.cos(a), cy + q * math.sin(a)))
    d.polygon(pts, fill=col)


def _flag(d, s, x0, y0, w, h, k):
    X = lambda f: x0 + w * f
    Y = lambda f: y0 + h * f
    R, Wt, B = (220, 40, 50, 255), (250, 250, 250, 255), (30, 60, 160, 255)
    if k == 0:
        d.rectangle((x0, y0, X(1), Y(1)), fill=Wt)
        r = h * 0.3
        d.ellipse((X(0.5) - r, Y(0.5) - r, X(0.5) + r, Y(0.5) + r), fill=(200, 20, 50, 255))
    elif k == 1:
        d.rectangle((x0, y0, X(1), Y(1)), fill=(222, 40, 16, 255))
        _star(d, X(0.17), Y(0.27), h * 0.17, (255, 222, 0, 255))
        for fx, fy in ((0.33, 0.1), (0.4, 0.2), (0.4, 0.35), (0.33, 0.45)):
            _star(d, X(fx), Y(fy), h * 0.055, (255, 222, 0, 255))
    elif k == 2:
        for i in range(7):
            d.rectangle((x0, Y(i * 2 / 13), X(1), Y((i * 2 + 1) / 13)), fill=(190, 30, 50, 255))
            d.rectangle((x0, Y((i * 2 + 1) / 13), X(1), Y((i * 2 + 2) / 13)), fill=Wt)
        d.rectangle((x0, y0, X(0.42), Y(7 / 13)), fill=(40, 50, 110, 255))
        for r in range(4):
            for c in range(5):
                xx, yy = X(0.05 + c * 0.08), Y(0.06 + r * 0.12)
                d.ellipse((xx - 0.7 * s, yy - 0.7 * s, xx + 0.7 * s, yy + 0.7 * s), fill=Wt)
    elif k in (3, 6):
        cols = [B, Wt, R] if k == 3 else [(0, 146, 70, 255), Wt, (206, 43, 55, 255)]
        for i, c in enumerate(cols):
            d.rectangle((X(i / 3), y0, X((i + 1) / 3), Y(1)), fill=c)
    elif k == 4:
        d.rectangle((x0, y0, X(1), Y(1)), fill=(170, 21, 27, 255))
        d.rectangle((x0, Y(0.25), X(1), Y(0.75)), fill=(241, 191, 0, 255))
    elif k == 5:
        for i, c in enumerate([(20, 20, 20, 255), (221, 0, 0, 255), (255, 206, 0, 255)]):
            d.rectangle((x0, Y(i / 3), X(1), Y((i + 1) / 3)), fill=c)
    elif k == 7:
        d.rectangle((x0, y0, X(1), Y(1)), fill=(218, 37, 29, 255))
        _star(d, X(0.5), Y(0.52), h * 0.3, (255, 255, 0, 255))
    elif k == 8:
        for a, b, c in ((0, 1 / 6, R), (1 / 6, 2 / 6, Wt), (2 / 6, 4 / 6, (45, 42, 74, 255)), (4 / 6, 5 / 6, Wt), (5 / 6, 1, R)):
            d.rectangle((x0, Y(a), X(1), Y(b)), fill=c)
    elif k == 9:
        for i, c in enumerate([(255, 153, 51, 255), Wt, (19, 136, 8, 255)]):
            d.rectangle((x0, Y(i / 3), X(1), Y((i + 1) / 3)), fill=c)
        r = h * 0.13
        d.ellipse((X(0.5) - r, Y(0.5) - r, X(0.5) + r, Y(0.5) + r), outline=(0, 0, 128, 255), width=max(1, int(0.8 * s)))
        for i in range(12):
            a = math.radians(i * 30)
            d.line((X(0.5), Y(0.5), X(0.5) + r * math.cos(a), Y(0.5) + r * math.sin(a)), fill=(0, 0, 128, 255), width=max(1, int(0.4 * s)))
    elif k == 10:
        for i, c in enumerate([Wt, (0, 57, 166, 255), (213, 43, 30, 255)]):
            d.rectangle((x0, Y(i / 3), X(1), Y((i + 1) / 3)), fill=c)
    elif k == 11:
        d.rectangle((x0, y0, X(1), Y(1)), fill=(0, 156, 59, 255))
        d.polygon([(X(0.08), Y(0.5)), (X(0.5), Y(0.1)), (X(0.92), Y(0.5)), (X(0.5), Y(0.9))], fill=(255, 223, 0, 255))
        r = h * 0.22
        d.ellipse((X(0.5) - r, Y(0.5) - r, X(0.5) + r, Y(0.5) + r), fill=(0, 39, 118, 255))
        d.arc((X(0.5) - r * 1.3, Y(0.5) - r * 0.6, X(0.5) + r * 1.1, Y(0.5) + r * 1.6), 200, 330, fill=Wt, width=max(1, int(0.6 * s)))


def flag_btn(k, w=64, h=54):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 0, W - 1, H - 1), 6 * s, fill=(12, 18, 44, 235), outline=(110, 140, 255, 255), width=int(1.2 * s))
        fx0, fy0, fw, fh = 6 * s, 5 * s, W - 12 * s, 30 * s
        d.rectangle((fx0 - 1 * s, fy0 - 1 * s, fx0 + fw + 1 * s, fy0 + fh + 1 * s), fill=(0, 0, 0, 255))
        _flag(d, s, fx0, fy0, fw, fh, k)
        fo = font('nanumx', int(10 * s))
        d.text((W / 2, H - 9 * s), FLAGS[k], font=fo, fill=(255, 255, 255, 255), anchor='mm')
    return art('k26_flag%d' % k, w, h, f, colors=128)


TOURIST_STYLE = [((230, 90, 60), (250, 220, 190), (90, 60, 30), 'cap'), ((60, 170, 140), (230, 190, 150), (30, 30, 30), 'none'),
                 ((240, 190, 60), (200, 150, 110), (240, 220, 140), 'hat'), ((170, 90, 220), (250, 215, 190), (150, 70, 40), 'bun')]


def tourist(i, mood='n'):
    shirt, skin, hair, hat = TOURIST_STYLE[i]

    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        # 다리/몸
        d.rounded_rectangle((cx - 10 * s, H - 30 * s, cx - 2 * s, H - 2 * s), 3 * s, fill=(50, 60, 100, 255))
        d.rounded_rectangle((cx + 2 * s, H - 30 * s, cx + 10 * s, H - 2 * s), 3 * s, fill=(50, 60, 100, 255))
        d.rounded_rectangle((cx - 15 * s, H - 58 * s, cx + 15 * s, H - 26 * s), 8 * s, fill=_c(shirt))
        # 배낭 끈 + 카메라
        d.line((cx - 8 * s, H - 58 * s, cx + 8 * s, H - 36 * s), fill=(40, 40, 50, 255), width=int(2 * s))
        d.rounded_rectangle((cx + 2 * s, H - 40 * s, cx + 14 * s, H - 31 * s), 2 * s, fill=(30, 30, 40, 255))
        d.ellipse((cx + 5 * s, H - 39 * s, cx + 11 * s, H - 33 * s), fill=(120, 160, 255, 255))
        # 머리
        hy = H - 74 * s
        d.ellipse((cx - 11 * s, hy, cx + 11 * s, hy + 22 * s), fill=_c(skin))
        if hat == 'cap':
            d.chord((cx - 12 * s, hy - 2 * s, cx + 12 * s, hy + 16 * s), 180, 360, fill=(40, 80, 200, 255))
            d.rectangle((cx - 2 * s, hy + 5 * s, cx + 17 * s, hy + 8 * s), fill=(40, 80, 200, 255))
        elif hat == 'hat':
            d.ellipse((cx - 19 * s, hy + 1 * s, cx + 19 * s, hy + 9 * s), fill=(230, 200, 120, 255))
            d.chord((cx - 11 * s, hy - 6 * s, cx + 11 * s, hy + 12 * s), 180, 360, fill=(230, 200, 120, 255))
            d.rectangle((cx - 11 * s, hy + 1 * s, cx + 11 * s, hy + 3 * s), fill=(200, 60, 60, 255))
        elif hat == 'bun':
            d.chord((cx - 12 * s, hy - 1 * s, cx + 12 * s, hy + 16 * s), 180, 360, fill=_c(hair))
            d.ellipse((cx - 6 * s, hy - 8 * s, cx + 6 * s, hy + 2 * s), fill=_c(hair))
        else:
            d.chord((cx - 12 * s, hy - 1 * s, cx + 12 * s, hy + 14 * s), 180, 360, fill=_c(hair))
        ey = hy + 12 * s
        for ex in (-4.5, 4.5):
            d.ellipse((cx + ex * s - 1.3 * s, ey - 1.3 * s, cx + ex * s + 1.3 * s, ey + 1.3 * s), fill=(30, 30, 40, 255))
        if mood == 'h':
            d.arc((cx - 5 * s, ey, cx + 5 * s, ey + 7 * s), 20, 160, fill=(150, 40, 40, 255), width=int(1.5 * s))
        elif mood == 's':
            d.arc((cx - 5 * s, ey + 4 * s, cx + 5 * s, ey + 10 * s), 200, 340, fill=(150, 40, 40, 255), width=int(1.5 * s))
            d.line((cx + 9 * s, hy + 2 * s, cx + 9 * s, hy + 7 * s), fill=(120, 180, 255, 255), width=int(1.5 * s))
        else:
            d.line((cx - 3 * s, ey + 5 * s, cx + 3 * s, ey + 5 * s), fill=(150, 40, 40, 255), width=int(1.5 * s))
    return art('k26_tourist%d_%s' % (i, mood), 44, 80, f)


def speech_bubble(w=150, h=46):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 10 * s), 12 * s, fill=(255, 255, 255, 250), outline=(80, 110, 220, 255),
                            width=int(1.4 * s))
        d.polygon([(W * 0.62, H - 11 * s), (W * 0.74, H - 11 * s), (W * 0.62, H - 1 * s)], fill=(255, 255, 255, 250))
        d.line((W * 0.62, H - 11 * s, W * 0.62, H - 1 * s), fill=(80, 110, 220, 255), width=int(1.4 * s))
        d.line((W * 0.62, H - 1 * s, W * 0.74, H - 10.5 * s), fill=(80, 110, 220, 255), width=int(1.4 * s))
    return art('k26_bubble', w, h, f)


def interpreter():
    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        d.rounded_rectangle((cx - 9 * s, H - 24 * s, cx - 2 * s, H - 1 * s), 3 * s, fill=(30, 34, 60, 255))
        d.rounded_rectangle((cx + 2 * s, H - 24 * s, cx + 9 * s, H - 1 * s), 3 * s, fill=(30, 34, 60, 255))
        d.rounded_rectangle((cx - 13 * s, H - 48 * s, cx + 13 * s, H - 20 * s), 7 * s, fill=(40, 100, 230, 255))
        d.rectangle((cx - 13 * s, H - 40 * s, cx + 13 * s, H - 35 * s), fill=(250, 220, 60, 255))
        hy = H - 66 * s
        d.ellipse((cx - 10 * s, hy, cx + 10 * s, hy + 20 * s), fill=(245, 205, 175, 255))
        d.chord((cx - 11 * s, hy - 1 * s, cx + 11 * s, hy + 13 * s), 180, 360, fill=(30, 30, 40, 255))
        d.arc((cx - 12 * s, hy - 2 * s, cx + 12 * s, hy + 18 * s), 180, 360, fill=(250, 220, 60, 255), width=int(2 * s))
        d.ellipse((cx - 14 * s, hy + 7 * s, cx - 9 * s, hy + 14 * s), fill=(250, 220, 60, 255))
        d.line((cx - 11 * s, hy + 13 * s, cx - 4 * s, hy + 17 * s), fill=(250, 220, 60, 255), width=int(1.2 * s))
        for ex in (-4, 4):
            d.ellipse((cx + ex * s - 1.2 * s, hy + 10 * s, cx + ex * s + 1.2 * s, hy + 12.4 * s), fill=(30, 30, 40, 255))
        d.arc((cx - 4 * s, hy + 11 * s, cx + 4 * s, hy + 17 * s), 20, 160, fill=(150, 40, 40, 255), width=int(1.3 * s))
    return art('k26_interp', 32, 70, f)


def patience_bar(i, n=10, w=46, h=7):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 0, W - 1, H - 1), H / 2, fill=(10, 12, 30, 230), outline=(200, 210, 240, 255), width=int(0.8 * s))
        fw = (W - 3 * s) * i / n
        if i > 0:
            col = (80, 220, 120) if i > 6 else ((250, 200, 50) if i > 3 else (240, 70, 80))
            d.rounded_rectangle((1.5 * s, 1.5 * s, 1.5 * s + max(fw, H - 3 * s), H - 1.5 * s), (H - 3 * s) / 2, fill=_c(col))
    return art('k26_pat%d' % i, w, h, f)
