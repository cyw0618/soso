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
            d.ellipse((cx - r * 0.18, stem_top - r * 0.3, cx + r * 0.05, stem_top - r * 0.1), fill=(255, 255, 255, 255))
        # 화분
        pw, pb = W * 0.42, W * 0.30
        d.polygon([(cx - pw, pot_top), (cx + pw, pot_top), (cx + pb, H - 1.5 * s), (cx - pb, H - 1.5 * s)],
                  fill=_c((196, 102, 60)), outline=_c((70, 30, 14)))
        d.rectangle((cx - pw - 2 * s, pot_top - 4 * s, cx + pw + 2 * s, pot_top + 4 * s), fill=_c((214, 120, 74)),
                    outline=_c((70, 30, 14)), width=int(1 * s))
        d.ellipse((cx - pw + 2 * s, pot_top - 4 * s, cx + pw - 2 * s, pot_top + 1 * s), fill=_c((84, 54, 36)))
        d.polygon([(cx - pw * 0.7, pot_top + 6 * s), (cx - pw * 0.5, pot_top + 6 * s), (cx - pb * 0.55, H - 4 * s),
                   (cx - pb * 0.75, H - 4 * s)], fill=(214, 136, 100, 255))
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
        d.rectangle((pad + 2 * s, top + 2 * s, pad + 3.2 * s, bot - 2 * s), fill=(235, 240, 255, 255))
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
            d.ellipse((cx - r * 0.5, cy + r * 0.1, cx - r * 0.1, cy + r * 0.6), fill=(190, 220, 255, 255))
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
        d.rectangle((W * 0.36, H * 0.34, W * 0.46, H * 0.62), fill=(120, 190, 250, 255))
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
        d.ellipse((W * 0.34, W * 0.32, W * 0.48, W * 0.44), fill=(255, 240, 200, 255))
    return art('s02_sun', 40, 40, f)


# ================================================================== 3. 장터 흥정
def s03_merchant(face):
    """부강 오일장 상인 아저씨 (상반신). face: smile / sweat / frown / angry."""
    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        skin, skin_d = (240, 196, 160), (120, 70, 44)
        # 몸 (조끼 + 앞치마)
        d.rounded_rectangle((W * 0.10, H * 0.66, W * 0.90, H + 20 * s), 18 * s, fill=(70, 96, 150, 255), outline=(16, 24, 50, 255),
                            width=int(1.5 * s))
        d.polygon([(cx - W * 0.22, H * 0.70), (cx + W * 0.22, H * 0.70), (cx + W * 0.26, H), (cx - W * 0.26, H)],
                  fill=(222, 120, 60, 255), outline=(90, 40, 14, 255))
        d.text((cx, H * 0.86), '부강상회', font=font('jalnan', int(9 * s)), fill=(255, 245, 230, 255), anchor='mm')
        d.polygon([(cx - 10 * s, H * 0.66), (cx, H * 0.74), (cx + 10 * s, H * 0.66)], fill=skin + (255,))
        # 목·얼굴
        d.rectangle((cx - 9 * s, H * 0.56, cx + 9 * s, H * 0.68), fill=skin + (255,))
        hx0, hy0, hx1, hy1 = cx - 30 * s, H * 0.14, cx + 30 * s, H * 0.62
        d.ellipse((hx0 - 6 * s, H * 0.33, hx0 + 6 * s, H * 0.45), fill=skin + (255,), outline=skin_d + (255,), width=int(1 * s))
        d.ellipse((hx1 - 6 * s, H * 0.33, hx1 + 6 * s, H * 0.45), fill=skin + (255,), outline=skin_d + (255,), width=int(1 * s))
        red = face == 'angry'
        d.ellipse((hx0, hy0, hx1, hy1), fill=((236, 140, 120) if red else skin) + (255,), outline=skin_d + (255,), width=int(1.4 * s))
        # 머리 + 수건 머리띠
        d.chord((hx0, hy0 - 4 * s, hx1, hy0 + 30 * s), 180, 360, fill=(40, 34, 30, 255))
        d.rectangle((hx0 - 1 * s, hy0 + 9 * s, hx1 + 1 * s, hy0 + 17 * s), fill=(250, 250, 250, 255), outline=(150, 160, 180, 255),
                    width=int(1 * s))
        d.polygon([(hx1 - 2 * s, hy0 + 11 * s), (hx1 + 12 * s, hy0 + 6 * s), (hx1 + 10 * s, hy0 + 18 * s)], fill=(250, 250, 250, 255),
                  outline=(150, 160, 180, 255))
        ey = H * 0.40
        ex = 12 * s
        ink = (30, 20, 16, 255)
        # 눈썹
        brow = {'smile': (-2, -2), 'sweat': (3, -3), 'frown': (-3, 2), 'angry': (-6, 5)}[face]
        for sx in (-1, 1):
            x0, x1 = cx + sx * (ex + 7 * s), cx + sx * (ex - 7 * s)
            d.line([(x0, ey - 9 * s + brow[0] * s * (1 if sx < 0 else 1) * 0.5), (x1, ey - 9 * s + brow[1] * s * 0.5)],
                   fill=ink, width=int(2.4 * s))
        # 눈
        for sx in (-1, 1):
            x = cx + sx * ex
            if face == 'smile':
                d.arc((x - 5 * s, ey - 4 * s, x + 5 * s, ey + 4 * s), 200, 340, fill=ink, width=int(2 * s))
            elif face == 'angry':
                d.ellipse((x - 3.5 * s, ey - 2.5 * s, x + 3.5 * s, ey + 3.5 * s), fill=ink)
                d.line([(x - 5 * s, ey - 4 * s + sx * 0), (x + 5 * s, ey - 4 * s)], fill=ink, width=int(1.5 * s))
            else:
                d.ellipse((x - 3 * s, ey - 3 * s, x + 3 * s, ey + 3 * s), fill=ink)
                d.ellipse((x - 1.5 * s, ey - 2 * s, x, ey - 0.5 * s), fill=(255, 255, 255, 255))
        # 코
        d.arc((cx - 4 * s, ey + 2 * s, cx + 4 * s, ey + 10 * s), 300, 90, fill=skin_d + (255,), width=int(1.4 * s))
        # 입
        my = H * 0.52
        if face == 'smile':
            d.chord((cx - 11 * s, my - 6 * s, cx + 11 * s, my + 8 * s), 0, 180, fill=(140, 30, 40, 255), outline=ink, width=int(1.2 * s))
            d.rectangle((cx - 8 * s, my + 1 * s, cx + 8 * s, my + 3 * s), fill=(255, 255, 255, 255))
        elif face == 'sweat':
            d.arc((cx - 9 * s, my - 2 * s, cx + 9 * s, my + 8 * s), 200, 340, fill=ink, width=int(2 * s))
            # 땀방울
            for (x, y, r) in ((hx1 - 2 * s, H * 0.24, 4.5), (hx0 + 4 * s, H * 0.27, 3.2)):
                d.ellipse((x - r * s, y, x + r * s, y + r * 2.2 * s), fill=(110, 190, 255, 255), outline=(30, 90, 200, 255), width=int(0.8 * s))
                d.polygon([(x - r * 0.8 * s, y + r * 0.6 * s), (x, y - r * 1.2 * s), (x + r * 0.8 * s, y + r * 0.6 * s)],
                          fill=(110, 190, 255, 255))
        elif face == 'frown':
            d.arc((cx - 9 * s, my + 1 * s, cx + 9 * s, my + 11 * s), 200, 340, fill=ink, width=int(2.2 * s))
        else:
            d.chord((cx - 10 * s, my - 2 * s, cx + 10 * s, my + 10 * s), 180, 360, fill=(120, 20, 30, 255), outline=ink, width=int(1.4 * s))
            for x, y in ((hx1 + 2 * s, H * 0.16), (hx0 - 4 * s, H * 0.18)):
                d.line([(x - 5 * s, y - 5 * s), (x + 5 * s, y + 5 * s)], fill=(230, 30, 50, 255), width=int(2.2 * s))
                d.line([(x - 5 * s, y + 5 * s), (x + 5 * s, y - 5 * s)], fill=(230, 30, 50, 255), width=int(2.2 * s))
        if face in ('smile', 'sweat'):
            for sx in (-1, 1):
                x = cx + sx * 20 * s
                d.ellipse((x - 5 * s, my - 6 * s, x + 5 * s, my - 1 * s), fill=(246, 166, 146, 255))
    return art('s03_merchant_' + face, 104, 128, f)


def s03_item(k):
    """0 뻥튀기 / 1 참기름 / 2 꽃고무신 / 3 대나무 소쿠리 / 4 호미."""
    def f(d, im, s):
        W, H = im.width, im.height
        cx, cy = W / 2, H / 2
        ink = (40, 26, 16, 255)
        if k == 0:
            d.rounded_rectangle((W * 0.16, H * 0.14, W * 0.84, H * 0.92), 6 * s, fill=(230, 240, 255, 150), outline=(150, 170, 210, 255),
                                width=int(1.2 * s))
            for (x, y) in ((0.36, 0.38), (0.62, 0.42), (0.46, 0.62), (0.66, 0.70), (0.34, 0.76)):
                r = W * 0.15
                d.ellipse((W * x - r, H * y - r, W * x + r, H * y + r), fill=(250, 238, 210, 255), outline=(200, 170, 120, 255),
                          width=int(1 * s))
                for a in range(0, 360, 60):
                    d.point((W * x + math.cos(math.radians(a)) * r * 0.5, H * y + math.sin(math.radians(a)) * r * 0.5), fill=(210, 180, 130, 255))
            d.rectangle((W * 0.16, H * 0.10, W * 0.84, H * 0.20), fill=(220, 60, 70, 255), outline=(120, 20, 30, 255), width=int(1 * s))
        elif k == 1:
            d.rounded_rectangle((W * 0.30, H * 0.30, W * 0.70, H * 0.94), 8 * s, fill=(196, 120, 30, 255), outline=ink, width=int(1.4 * s))
            d.rectangle((W * 0.42, H * 0.10, W * 0.58, H * 0.32), fill=(210, 140, 50, 255), outline=ink, width=int(1.2 * s))
            d.rectangle((W * 0.40, H * 0.04, W * 0.60, H * 0.13), fill=(200, 40, 40, 255), outline=ink, width=int(1 * s))
            d.rounded_rectangle((W * 0.33, H * 0.50, W * 0.67, H * 0.80), 3 * s, fill=(255, 248, 230, 255), outline=(120, 70, 20, 255),
                                width=int(1 * s))
            d.text((cx, H * 0.65), '참기름', font=font('jalnan', int(7 * s)), fill=(150, 40, 20, 255), anchor='mm')
            d.rectangle((W * 0.36, H * 0.34, W * 0.42, H * 0.48), fill=(226, 176, 110, 255))
        elif k == 2:
            pts = [(0.08, 0.62), (0.20, 0.46), (0.46, 0.44), (0.66, 0.36), (0.86, 0.40), (0.94, 0.58), (0.86, 0.74), (0.14, 0.76)]
            d.polygon([(W * x, H * y) for x, y in pts], fill=(250, 250, 255, 255), outline=(90, 100, 140, 255))
            d.ellipse((W * 0.50, H * 0.40, W * 0.86, H * 0.56), fill=(60, 70, 100, 255))
            d.line([(W * 0.10, H * 0.72), (W * 0.90, H * 0.70)], fill=(200, 60, 90, 255), width=int(2.5 * s))
            for (x, y) in ((0.28, 0.58), (0.38, 0.62)):
                for a in range(0, 360, 72):
                    px, py = W * x + math.cos(math.radians(a)) * 3 * s, H * y + math.sin(math.radians(a)) * 3 * s
                    d.ellipse((px - 2.4 * s, py - 2.4 * s, px + 2.4 * s, py + 2.4 * s), fill=(240, 90, 130, 255))
                d.ellipse((W * x - 1.6 * s, H * y - 1.6 * s, W * x + 1.6 * s, H * y + 1.6 * s), fill=(255, 220, 90, 255))
        elif k == 3:
            d.chord((W * 0.06, H * 0.10, W * 0.94, H * 0.94), 0, 180, fill=(200, 160, 90, 255), outline=(110, 76, 30, 255), width=int(1.6 * s))
            for i in range(1, 8):
                x = W * 0.06 + W * 0.88 * i / 8
                d.line([(x, H * 0.52), (cx + (x - cx) * 0.7, H * 0.92)], fill=(150, 110, 50, 255), width=int(1.2 * s))
            for j in range(1, 4):
                y = H * 0.52 + H * 0.4 * j / 4
                half = math.sqrt(max(0, 1 - ((y - H * 0.52) / (H * 0.42)) ** 2)) * W * 0.44
                d.line([(cx - half, y), (cx + half, y)], fill=(150, 110, 50, 255), width=int(1.2 * s))
            d.ellipse((W * 0.06, H * 0.42, W * 0.94, H * 0.62), fill=(230, 196, 130, 255), outline=(110, 76, 30, 255), width=int(1.6 * s))
            d.ellipse((W * 0.14, H * 0.46, W * 0.86, H * 0.58), fill=(170, 130, 70, 255))
        else:
            d.line([(W * 0.20, H * 0.86), (W * 0.62, H * 0.30)], fill=(150, 96, 50, 255), width=int(6 * s))
            d.line([(W * 0.20, H * 0.86), (W * 0.62, H * 0.30)], fill=(190, 130, 70, 255), width=int(3.5 * s))
            d.line([(W * 0.60, H * 0.32), (W * 0.70, H * 0.20)], fill=(90, 90, 100, 255), width=int(2.5 * s))
            d.polygon([(W * 0.66, H * 0.16), (W * 0.92, H * 0.24), (W * 0.84, H * 0.52), (W * 0.70, H * 0.30)],
                      fill=(130, 140, 160, 255), outline=(40, 44, 60, 255))
            d.line([(W * 0.70, H * 0.20), (W * 0.88, H * 0.27)], fill=(220, 226, 240, 255), width=int(1.2 * s))
    return art('s03_item_%d' % k, 64, 64, f)


def s03_heart(on):
    def f(d, im, s):
        W, H = im.width, im.height
        col = (240, 60, 90, 255) if on else (60, 66, 90, 255)
        r = W * 0.27
        d.ellipse((W * 0.5 - 2 * r, H * 0.12, W * 0.5, H * 0.12 + 2 * r), fill=col)
        d.ellipse((W * 0.5, H * 0.12, W * 0.5 + 2 * r, H * 0.12 + 2 * r), fill=col)
        d.polygon([(W * 0.5 - 2 * r + 1.2 * s, H * 0.12 + r * 1.3), (W * 0.5, H * 0.94), (W * 0.5 + 2 * r - 1.2 * s, H * 0.12 + r * 1.3)],
                  fill=col)
        if on:
            d.ellipse((W * 0.22, H * 0.24, W * 0.38, H * 0.38), fill=(255, 190, 200, 255))
    return art('s03_heart_%d' % on, 16, 15, f)


def s03_bubble():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((1.5 * s, 1.5 * s, W - 1.5 * s, H - 9 * s), 10 * s, fill=(255, 255, 255, 245), outline=(30, 40, 90, 255),
                            width=int(1.5 * s))
        d.polygon([(W * 0.18, H - 10.5 * s), (W * 0.14, H - 1), (W * 0.30, H - 10.5 * s)], fill=(255, 255, 255, 245))
        d.line([(W * 0.18, H - 9.5 * s), (W * 0.14, H - 1), (W * 0.30, H - 9.5 * s)], fill=(30, 40, 90, 255), width=int(1.5 * s))
    return art('s03_bubble', 224, 54, f)


# ================================================================== 4. 거스름돈 계산
def s04_money(k):
    """0 만원 / 1 오천원 / 2 천원 (지폐 64×30), 3 500원 / 4 100원 (동전)."""
    if k <= 2:
        col, dark, lab = [((120, 190, 120), (40, 100, 50), '10000'), ((236, 170, 110), (150, 80, 30), '5000'),
                          ((130, 170, 230), (40, 70, 140), '1000')][k]

        def f(d, im, s):
            W, H = im.width, im.height
            d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 3 * s, fill=_c(col), outline=_c(dark), width=int(1.4 * s))
            d.rounded_rectangle((4 * s, 4 * s, W - 4 * s, H - 4 * s), 2 * s, outline=_c(dark, 255), width=int(0.6 * s))
            cx = W * 0.70
            d.ellipse((cx - 9 * s, H / 2 - 9 * s, cx + 9 * s, H / 2 + 9 * s), fill=_c(tuple(min(255, c + 50) for c in col)),
                      outline=_c(dark), width=int(0.8 * s))
            d.ellipse((cx - 4 * s, H / 2 - 6 * s, cx + 4 * s, H / 2 + 1 * s), fill=_c(dark))
            d.chord((cx - 7 * s, H / 2 + 0 * s, cx + 7 * s, H / 2 + 12 * s), 180, 360, fill=_c(dark))
            d.text((W * 0.31, H * 0.46), lab, font=font('jalnan', int((8.5 if len(lab) > 4 else 10) * s)), fill=_c(dark), anchor='mm')
            d.text((W * 0.30, H * 0.78), '원', font=font('jalnan', int(5.5 * s)), fill=_c(dark), anchor='mm')
        return art('s04_money_%d' % k, 64, 30, f)
    r = 15 if k == 3 else 12.5
    lab = '500' if k == 3 else '100'

    def f(d, im, s):
        W = im.width
        d.ellipse((0.8 * s, 0.8 * s, W - 0.8 * s, W - 0.8 * s), fill=(196, 202, 214, 255), outline=(70, 76, 96, 255), width=int(1.2 * s))
        d.ellipse((3 * s, 3 * s, W - 3 * s, W - 3 * s), fill=(214, 220, 232, 255), outline=(150, 156, 176, 255), width=int(0.6 * s))
        d.text((W / 2, W / 2), lab, font=font('jalnan', int(r * 0.62 * s)), fill=(70, 76, 100, 255), anchor='mm')
        d.ellipse((W * 0.24, W * 0.16, W * 0.44, W * 0.30), fill=(240, 244, 255, 255))
    return art('s04_money_%d' % k, r * 2, r * 2, f)


def s04_customer(k):
    """손님 4명: 0 할머니 / 1 학생 / 2 회사원 / 3 아주머니."""
    hair, shirt, skin = [((200, 200, 210), (150, 90, 170), (238, 200, 170)), ((30, 26, 30), (40, 56, 110), (244, 208, 178)),
                         ((50, 40, 34), (230, 232, 240), (232, 190, 156)), ((110, 60, 36), (236, 120, 150), (244, 204, 176))][k]

    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        ink = (30, 20, 16, 255)
        if k == 3:
            d.rounded_rectangle((cx - 30 * s, H * 0.14, cx + 30 * s, H * 0.72), 20 * s, fill=_c(hair))
        d.rounded_rectangle((W * 0.10, H * 0.68, W * 0.90, H + 20 * s), 18 * s, fill=_c(shirt), outline=(16, 24, 50, 255), width=int(1.5 * s))
        if k == 2:
            d.polygon([(cx - 4 * s, H * 0.70), (cx + 4 * s, H * 0.70), (cx + 5 * s, H * 0.95), (cx, H), (cx - 5 * s, H * 0.95)],
                      fill=(200, 40, 60, 255))
        if k == 1:
            d.polygon([(cx - 14 * s, H * 0.68), (cx, H * 0.80), (cx + 14 * s, H * 0.68)], fill=(240, 240, 250, 255))
        d.rectangle((cx - 8 * s, H * 0.56, cx + 8 * s, H * 0.70), fill=_c(skin))
        hx0, hy0, hx1, hy1 = cx - 25 * s, H * 0.16, cx + 25 * s, H * 0.62
        d.ellipse((hx0, hy0, hx1, hy1), fill=_c(skin), outline=(120, 70, 44, 255), width=int(1.2 * s))
        if k == 0:
            d.chord((hx0 - 2 * s, hy0 - 3 * s, hx1 + 2 * s, hy0 + 26 * s), 180, 360, fill=_c(hair))
            d.ellipse((cx - 10 * s, hy0 - 14 * s, cx + 10 * s, hy0 + 2 * s), fill=_c(hair), outline=(150, 150, 160, 255))
        elif k == 1:
            d.chord((hx0 - 2 * s, hy0 - 4 * s, hx1 + 2 * s, hy0 + 30 * s), 180, 360, fill=_c(hair))
            d.rectangle((hx0, hy0 + 8 * s, cx - 4 * s, hy0 + 14 * s), fill=_c(hair))
        elif k == 2:
            d.chord((hx0 - 1 * s, hy0 - 3 * s, hx1 + 1 * s, hy0 + 24 * s), 180, 360, fill=_c(hair))
        else:
            d.chord((hx0 - 3 * s, hy0 - 4 * s, hx1 + 3 * s, hy0 + 28 * s), 180, 360, fill=_c(hair))
        ey = H * 0.40
        for sx in (-1, 1):
            x = cx + sx * 10 * s
            d.arc((x - 4.5 * s, ey - 3.5 * s, x + 4.5 * s, ey + 3.5 * s), 200, 340, fill=ink, width=int(1.8 * s))
            if k in (0, 1):
                d.ellipse((x - 7 * s, ey - 6 * s, x + 7 * s, ey + 6 * s), outline=(60, 60, 80, 255), width=int(1 * s))
            d.ellipse((x - 4 * s + sx * 4 * s, ey + 5 * s, x + 4 * s + sx * 4 * s, ey + 9 * s), fill=(246, 170, 160, 255))
        if k in (0, 1):
            d.line([(cx - 3 * s, ey), (cx + 3 * s, ey)], fill=(60, 60, 80, 255), width=int(1 * s))
        d.chord((cx - 8 * s, H * 0.48, cx + 8 * s, H * 0.56), 0, 180, fill=(170, 40, 50, 255), outline=ink, width=int(1 * s))
    return art('s04_cust_%d' % k, 84, 104, f)


def s04_receipt():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H - 4 * s), fill=(250, 248, 240, 255))
        for i in range(12):
            x0 = W * i / 12
            d.polygon([(x0, H - 4 * s), (x0 + W / 24, H), (x0 + W / 12, H - 4 * s)], fill=(250, 248, 240, 255))
        d.rectangle((0, 0, W, 16 * s), fill=(40, 110, 70, 255))
        d.text((W / 2, 8 * s), '세종 로컬푸드 영수증', font=font('nsr', int(8.5 * s)), fill=(255, 255, 255, 255), anchor='mm')
        for y in (H * 0.62,):
            for x in range(int(6 * s), int(W - 6 * s), int(5 * s)):
                d.line([(x, y), (x + 2.5 * s, y)], fill=(140, 140, 150, 255), width=int(0.8 * s))
    return art('s04_receipt', 140, 132, f)


# ================================================================== 5. 라떼 아트
def s05_paths(step=19):
    """하트·튤립·별 경로를 같은 간격 점으로 (무대 px, 잔 가운데 기준). 닫힌 경로: 마지막 점 = 첫 점."""
    def resample(pts):
        pts = pts + [pts[0]]
        seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
        L = sum(seg)
        n = max(8, int(round(L / step)))
        out, acc, i = [], 0.0, 0
        for k in range(n):
            target = L * k / n
            while acc + seg[i] < target:
                acc += seg[i]
                i += 1
            f = (target - acc) / seg[i] if seg[i] else 0
            a, b = pts[i], pts[i + 1]
            out.append((round(a[0] + (b[0] - a[0]) * f, 1), round(a[1] + (b[1] - a[1]) * f, 1)))
        return out + [out[0]]
    heart = []
    for k in range(200):
        t = 2 * math.pi * k / 200
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        heart.append((x * 4.3, y * 4.3 + 10))
    tul = [(-0.5, -0.3), (-0.64, 0.12), (-0.58, 0.62), (-0.26, 0.3), (0, 0.72), (0.26, 0.3), (0.58, 0.62), (0.64, 0.12),
           (0.5, -0.3), (0.26, -0.52), (0, -0.58), (-0.26, -0.52)]
    tulip = [(x * 100, y * 100 + 6) for x, y in tul]
    star = []
    for k in range(10):
        a = math.pi / 2 - k * math.pi / 5
        r = 76 if k % 2 == 0 else 32
        star.append((r * math.cos(a), r * math.sin(a) - 4))
    return [resample(p) for p in (heart, tulip, star)]


def s05_cup():
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((0, 0, W, W), fill=(236, 238, 246, 255), outline=(150, 160, 190, 255), width=int(2 * s))
        d.ellipse((7 * s, 7 * s, W - 7 * s, W - 7 * s), fill=(200, 206, 222, 255))
        r = c - 11 * s
        d.ellipse((c - r, c - r, c + r, c + r), fill=(176, 116, 66, 255))
        r2 = r - 7 * s
        d.ellipse((c - r2, c - r2, c + r2, c + r2), fill=(142, 86, 44, 255))
        r3 = r2 - 18 * s
        d.ellipse((c - r3, c - r3, c + r3, c + r3), fill=(132, 78, 40, 255))
    return art('s05_cup', 212, 212, f)


def s05_guide(k, pts):
    def f(d, im, s):
        W = im.width
        c = W / 2
        P = [(c + x * s, c - y * s) for x, y in pts]
        for a, b in zip(P, P[1:]):
            for j in range(3):
                t0, t1 = j / 3.0, j / 3.0 + 0.17
                d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                       fill=(255, 236, 200, 230), width=int(2.2 * s))
    return art('s05_guide_%d' % k, 190, 190, f)


def s05_ring():
    def f(d, im, s):
        W = im.width
        d.ellipse((1 * s, 1 * s, W - 1 * s, W - 1 * s), outline=(80, 255, 170, 255), width=int(2.4 * s))
        d.ellipse((W * 0.36, W * 0.36, W * 0.64, W * 0.64), fill=(80, 255, 170, 255))
    return art('s05_ring', 22, 22, f)
