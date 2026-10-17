# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 2~10번 (games2a.py) 전용 그림. 모두 A3.art 로 2배 해상도 저장 (이름 접두어 s0N_)."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3

art = A3.art


def _c(col, a=255):
    return tuple(col[:3]) + (a,)


# ================================================================== 2. 수목원 물주기
PLANT_TYPES = [((236, 70, 96), (255, 210, 220)), ((150, 96, 240), (236, 220, 255)), ((255, 150, 40), (255, 236, 170))]


def s02_plant(kind, stage):
    """kind 0~2 (꽃 색), stage 1 새싹 / 2 잎 / 3 꽃봉오리 / 4 활짝."""
    petal, center = PLANT_TYPES[kind]

    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        pot_top = H * 0.66
        # 줄기·잎
        stem_top = {1: 0.56, 2: 0.40, 3: 0.24, 4: 0.20}[stage] * H
        green, dark = (64, 176, 92), (24, 96, 52)
        d.line([(cx, pot_top), (cx, stem_top)], fill=_c(dark), width=int(3.2 * s))
        d.line([(cx, pot_top), (cx, stem_top)], fill=_c(green), width=int(2 * s))

        def leaf(y, side, ln):
            x0, x1 = cx, cx + side * ln * s
            pts = [(x0, y), (cx + side * ln * 0.5 * s, y - 6 * s), (x1, y - 3 * s), (cx + side * ln * 0.5 * s, y + 3 * s)]
            d.polygon(pts, fill=_c(green), outline=_c(dark))
            d.line([(x0, y), (x1, y - 3 * s)], fill=_c(dark, 160), width=int(0.6 * s))
        if stage == 1:
            leaf(H * 0.60, -1, 9)
            leaf(H * 0.58, 1, 9)
        else:
            leaf(H * 0.60, -1, 14)
            leaf(H * 0.55, 1, 14)
            leaf(H * 0.46, -1, 12)
            if stage >= 3:
                leaf(H * 0.38, 1, 11)
        if stage == 3:
            d.ellipse((cx - 5 * s, stem_top - 9 * s, cx + 5 * s, stem_top + 3 * s), fill=_c(petal), outline=_c(dark), width=int(0.8 * s))
            d.polygon([(cx - 5 * s, stem_top), (cx, stem_top + 6 * s), (cx + 5 * s, stem_top)], fill=_c(green))
        if stage == 4:
            r = 15 * s
            for k in range(8):
                a = k * math.pi / 4
                px, py = cx + math.cos(a) * r * 0.62, stem_top + math.sin(a) * r * 0.62
                d.ellipse((px - r * 0.48, py - r * 0.48, px + r * 0.48, py + r * 0.48), fill=_c(petal), outline=_c((90, 20, 40), 160),
                          width=int(0.6 * s))
            d.ellipse((cx - r * 0.42, stem_top - r * 0.42, cx + r * 0.42, stem_top + r * 0.42), fill=_c(center),
                      outline=_c((120, 70, 20)), width=int(0.8 * s))
            d.ellipse((cx - r * 0.18, stem_top - r * 0.3, cx + r * 0.05, stem_top - r * 0.1), fill=(255, 255, 255, 150))
        # 화분
        pw, pb = W * 0.42, W * 0.30
        d.polygon([(cx - pw, pot_top), (cx + pw, pot_top), (cx + pb, H - 1.5 * s), (cx - pb, H - 1.5 * s)],
                  fill=_c((196, 102, 60)), outline=_c((70, 30, 14)))
        d.rectangle((cx - pw - 2 * s, pot_top - 4 * s, cx + pw + 2 * s, pot_top + 4 * s), fill=_c((214, 120, 74)),
                    outline=_c((70, 30, 14)), width=int(1 * s))
        d.ellipse((cx - pw + 2 * s, pot_top - 4 * s, cx + pw - 2 * s, pot_top + 1 * s), fill=_c((84, 54, 36)))
        d.polygon([(cx - pw * 0.7, pot_top + 6 * s), (cx - pw * 0.5, pot_top + 6 * s), (cx - pb * 0.55, H - 4 * s),
                   (cx - pb * 0.75, H - 4 * s)], fill=(255, 255, 255, 50))
    return art('s02_plant_%d_%d' % (kind, stage), 60, 92, f)


def s02_meter():
    def f(d, im, s):
        W, H = im.width, im.height
        pad = 1.2 * s
        top, bot = 2 * s, H - 2 * s
        h = bot - top

        def zone(a, b, col):
            d.rectangle((pad + 1.5 * s, bot - h * b, W - pad - 1.5 * s, bot - h * a), fill=_c(col))
        d.rounded_rectangle((pad, top - 1 * s, W - pad, bot + 1 * s), 4 * s, fill=(8, 12, 28, 240))
        zone(0, 0.30, (220, 110, 60))
        zone(0.30, 0.80, (60, 190, 110))
        zone(0.80, 1.0, (150, 80, 220))
        d.rounded_rectangle((pad, top - 1 * s, W - pad, bot + 1 * s), 4 * s, outline=(230, 236, 255, 255), width=int(1.2 * s))
        d.rectangle((pad + 2 * s, top + 2 * s, pad + 3.5 * s, bot - 2 * s), fill=(255, 255, 255, 60))
    return art('s02_meter', 12, 66, f)


def s02_marker():
    def f(d, im, s):
        W, H = im.width, im.height
        d.polygon([(0, 0), (W * 0.45, H / 2), (0, H)], fill=(255, 255, 255, 255), outline=(10, 14, 40, 255))
        d.rectangle((W * 0.3, H / 2 - 1 * s, W, H / 2 + 1 * s), fill=(255, 255, 255, 255))
    return art('s02_marker', 18, 9, f)


def s02_bubble(kind):
    def f(d, im, s):
        W, H = im.width, im.height
        col = (40, 120, 255) if kind == 'dry' else (140, 70, 200)
        d.ellipse((1 * s, 1 * s, W - 1 * s, H - 5 * s), fill=(255, 255, 255, 240), outline=_c(col), width=int(1.6 * s))
        d.polygon([(W * 0.4, H - 7 * s), (W * 0.5, H - 1), (W * 0.6, H - 7 * s)], fill=(255, 255, 255, 240))
        cx, cy = W / 2, (H - 5 * s) / 2
        if kind == 'dry':
            r = 6 * s
            d.ellipse((cx - r, cy - r * 0.4, cx + r, cy + r * 1.4), fill=_c(col))
            d.polygon([(cx - r * 0.85, cy + r * 0.2), (cx, cy - r * 1.5), (cx + r * 0.85, cy + r * 0.2)], fill=_c(col))
            d.ellipse((cx - r * 0.5, cy + r * 0.1, cx - r * 0.1, cy + r * 0.6), fill=(255, 255, 255, 180))
        else:
            d.text((cx, cy + 0.5 * s), '과습', font=font('jalnan', int(8.5 * s)), fill=_c(col), anchor='mm')
    return art('s02_bub_' + kind, 30, 28, f)


def s02_can():
    def f(d, im, s):
        W, H = im.width, im.height
        body = (60, 150, 240)
        d.rounded_rectangle((W * 0.30, H * 0.28, W * 0.78, H * 0.72), 4 * s, fill=_c(body), outline=_c((10, 30, 80)), width=int(1.2 * s))
        d.arc((W * 0.40, H * 0.08, W * 0.72, H * 0.46), 180, 360, fill=_c((10, 30, 80)), width=int(2.4 * s))
        d.polygon([(W * 0.32, H * 0.46), (W * 0.06, H * 0.62), (W * 0.04, H * 0.70), (W * 0.32, H * 0.60)], fill=_c(body),
                  outline=_c((10, 30, 80)))
        d.ellipse((W * 0.0, H * 0.58, W * 0.10, H * 0.78), fill=_c((40, 110, 200)), outline=_c((10, 30, 80)))
        d.rectangle((W * 0.36, H * 0.34, W * 0.46, H * 0.62), fill=(255, 255, 255, 70))
        for k, (x, y) in enumerate([(0.02, 0.86), (0.08, 0.95), (0.13, 0.84), (0.0, 0.98)]):
            d.ellipse((W * x, H * y - 2 * s, W * x + 3 * s, H * y + 1.5 * s), fill=(120, 200, 255, 230))
    return art('s02_can', 40, 34, f)


def s02_sun():
    def f(d, im, s):
        W = im.width
        c = W / 2
        for k in range(12):
            a = k * math.pi / 6
            d.line([(c + math.cos(a) * W * 0.30, c + math.sin(a) * W * 0.30), (c + math.cos(a) * W * 0.47, c + math.sin(a) * W * 0.47)],
                   fill=(255, 170, 40, 255), width=int(3 * s))
        d.ellipse((W * 0.24, W * 0.24, W * 0.76, W * 0.76), fill=(255, 200, 60, 255), outline=(230, 110, 20, 255), width=int(2 * s))
        d.ellipse((W * 0.34, W * 0.32, W * 0.48, W * 0.44), fill=(255, 255, 255, 140))
    return art('s02_sun', 40, 40, f)
