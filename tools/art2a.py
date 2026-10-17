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


# ================================================================== 6. 모닥불 지키기
def s06_flame(k):
    def f(d, im, s):
        W, H = im.width, im.height
        layers = [((230, 60, 30), 1.0), ((255, 140, 30), 0.76), ((255, 214, 90), 0.5), ((255, 248, 220), 0.26)]
        for li, (col, sc) in enumerate(layers):
            left, right = [], []
            n = 24
            for i in range(n + 1):
                v = i / n
                hw = W * 0.46 * sc * (1 - v) ** 0.85 * min(1.0, v * 2.6 + 0.45)
                cx = W / 2 + math.sin(v * 5.0 + k * 2.1 + li) * W * 0.07 * v
                y = H - 3 * s - v * (H - 6 * s) * (0.35 + 0.65 * sc)
                left.append((cx - hw, y))
                right.append((cx + hw, y))
            d.polygon(left + right[::-1], fill=col + (255,))
    return art('s06_flame2_%d' % k, 70, 100, f)


def s06_pit():
    def f(d, im, s):
        W, H = im.width, im.height
        d.ellipse((6 * s, H * 0.30, W - 6 * s, H - 2 * s), fill=(40, 30, 30, 255))
        d.ellipse((18 * s, H * 0.38, W - 18 * s, H - 8 * s), fill=(90, 50, 30, 255))
        rnd = random.Random(6)
        for i in range(11):
            a = math.pi * (0.05 + 0.9 * i / 10)
            x = W / 2 - math.cos(a) * (W / 2 - 10 * s)
            y = H * 0.66 + math.sin(a) * H * 0.26
            r = (7 + rnd.random() * 3) * s
            g = 110 + rnd.randint(0, 40)
            d.ellipse((x - r, y - r * 0.75, x + r, y + r * 0.75), fill=(g, g - 6, g + 6, 255), outline=(30, 30, 40, 255), width=int(1 * s))
        d.line([(W * 0.28, H * 0.62), (W * 0.72, H * 0.50)], fill=(80, 46, 24, 255), width=int(7 * s))
        d.line([(W * 0.30, H * 0.48), (W * 0.70, H * 0.64)], fill=(100, 60, 30, 255), width=int(7 * s))
    return art('s06_pit', 130, 40, f)


def s06_log(lit):
    def f(d, im, s):
        W, H = im.width, im.height
        bark = (110, 66, 34) if not lit else (70, 36, 20)
        d.rounded_rectangle((1 * s, 2 * s, W - 1 * s, H - 2 * s), 6 * s, fill=bark + (255,), outline=(40, 20, 10, 255), width=int(1 * s))
        d.ellipse((W - 12 * s, 2 * s, W - 1 * s, H - 2 * s), fill=(214, 170, 110, 255) if not lit else (255, 120, 30, 255),
                  outline=(40, 20, 10, 255), width=int(1 * s))
        if lit:
            for x in (0.2, 0.42, 0.62):
                d.line([(W * x, H * 0.35), (W * (x + 0.1), H * 0.65)], fill=(255, 150, 40, 255), width=int(1.6 * s))
        else:
            d.line([(W * 0.15, H * 0.4), (W * 0.7, H * 0.4)], fill=(80, 46, 20, 255), width=int(1 * s))
    return art('s06_log_%d' % lit, 44, 14, f)


def s06_twig():
    def f(d, im, s):
        W, H = im.width, im.height
        d.line([(2 * s, H * 0.7), (W - 2 * s, H * 0.3)], fill=(120, 80, 40, 255), width=int(2.2 * s))
        d.line([(W * 0.45, H * 0.5), (W * 0.62, H * 0.1)], fill=(120, 80, 40, 255), width=int(1.6 * s))
        d.line([(W * 0.25, H * 0.6), (W * 0.30, H * 0.95)], fill=(120, 80, 40, 255), width=int(1.4 * s))
    return art('s06_twig', 34, 16, f)


def s06_gauge():
    def f(d, im, s):
        W, H = im.width, im.height
        top, bot = 3 * s, H - 3 * s
        h = bot - top
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 6 * s, fill=(8, 10, 24, 245))
        for a, b, col in ((0, 0.45, (70, 90, 150)), (0.45, 0.75, (60, 200, 110)), (0.75, 0.85, (240, 160, 50)), (0.85, 1.0, (230, 50, 60))):
            d.rectangle((3.5 * s, bot - h * b, W - 3.5 * s, bot - h * a), fill=col + (255,))
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 6 * s, outline=(230, 236, 255, 255), width=int(1.4 * s))
    return art('s06_gauge', 16, 150, f)


def s06_wind():
    def f(d, im, s):
        W, H = im.width, im.height
        for y, x0, x1 in ((0.2, 0.1, 0.8), (0.5, 0.0, 0.95), (0.8, 0.2, 0.75)):
            d.line([(W * x0, H * y), (W * x1, H * y)], fill=(230, 240, 255, 255), width=int(2 * s))
            d.arc((W * x0 - 8 * s, H * y - 10 * s, W * x0 + 8 * s, H * y), 90, 270, fill=(230, 240, 255, 255), width=int(2 * s))
    return art('s06_wind', 120, 40, f)


def s06_drop():
    return A3.line_img('s06_drop', 4, 14, [(0.5, 0.0), (0.5, 1.0)], (160, 200, 255), width=1.6)


def s06_spark():
    return A3.disc('s06_spark', 3, (255, 200, 60), rim=(255, 120, 30), rimw=0.8)


# ================================================================== 8. 기록물 복원
_DOC = {}


def _doc_image(k):
    """기록물 전체 그림 (A3.S 배 해상도). k=0: 180×180 (3×3) / k=1: 200×150 (4×3)."""
    if k in _DOC:
        return _DOC[k]
    s = A3.S
    w, h = (180, 180) if k == 0 else (200, 150)
    im = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W, H = im.size
    rnd = random.Random(80 + k)
    d.rectangle((0, 0, W, H), fill=(238, 224, 188, 255))
    for i in range(7):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(10, 26) * s
        d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(226, 208, 166, 255))
    d.rectangle((0, 0, W - 1, H - 1), outline=(170, 140, 96, 255), width=int(2 * s))
    ink, red = (70, 46, 30, 255), (200, 40, 50, 255)
    F = lambda sz: font('nsr', int(sz * s))
    if k == 0:
        d.rectangle((8 * s, 8 * s, W - 8 * s, 12 * s), fill=red)
        d.text((W / 2, 22 * s), '대통령 기록물 제1호', font=F(9), fill=red, anchor='mm')
        d.text((W / 2, 40 * s), '행정수도 건설 계획서', font=F(15), fill=ink, anchor='mm')
        d.line([(14 * s, 53 * s), (W - 14 * s, 53 * s)], fill=ink, width=int(1.2 * s))
        # 사진 (오른쪽 가운데)
        px0, py0, px1, py1 = 104 * s, 62 * s, 168 * s, 116 * s
        d.rectangle((px0, py0, px1, py1), fill=(120, 150, 190, 255), outline=(60, 50, 40, 255), width=int(1.5 * s))
        d.rectangle((px0, py0 + (py1 - py0) * 0.62, px1, py1), fill=(90, 130, 90, 255))
        for i, (bx, bh) in enumerate(((0.12, 0.40), (0.30, 0.55), (0.52, 0.34), (0.72, 0.48))):
            x0 = px0 + (px1 - px0) * bx
            d.rectangle((x0, py0 + (py1 - py0) * (0.62 - bh), x0 + (px1 - px0) * 0.15, py0 + (py1 - py0) * 0.62), fill=(70, 80, 110, 255))
        d.ellipse((px1 - 16 * s, py0 + 5 * s, px1 - 6 * s, py0 + 15 * s), fill=(250, 230, 160, 255))
        # 글줄 (왼쪽)
        for i in range(6):
            y = (66 + i * 9) * s
            ln = rnd.uniform(0.6, 1.0)
            d.line([(14 * s, y), (14 * s + 80 * s * ln, y)], fill=(120, 100, 80, 255), width=int(2.4 * s))
        for i in range(3):
            y = (126 + i * 9) * s
            d.line([(14 * s, y), (14 * s + 150 * s * rnd.uniform(0.6, 1.0), y)], fill=(120, 100, 80, 255), width=int(2.4 * s))
        d.text((16 * s, 163 * s), '2004. 4. 15.', font=F(9), fill=ink, anchor='lm')
        cx, cy, r = 146 * s, 156 * s, 16 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=red, width=int(2.4 * s))
        d.ellipse((cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72), outline=red, width=int(1 * s))
        d.text((cx, cy - 3 * s), '대통령', font=F(6.5), fill=red, anchor='mm')
        d.text((cx, cy + 5 * s), '기록관', font=F(6.5), fill=red, anchor='mm')
    else:
        d.rectangle((0, 0, W, 26 * s), fill=(40, 70, 130, 255))
        d.text((W / 2, 13 * s), '세종시 출범 기념 사진첩', font=F(12), fill=(255, 255, 255, 255), anchor='mm')
        px0, py0, px1, py1 = 14 * s, 34 * s, 186 * s, 112 * s
        d.rectangle((px0, py0, px1, py1), fill=(150, 196, 236, 255), outline=(60, 50, 40, 255), width=int(1.5 * s))
        d.ellipse((px0 + 18 * s, py0 + 8 * s, px0 + 34 * s, py0 + 24 * s), fill=(255, 220, 120, 255))
        d.polygon([(px0, py0 + 50 * s), (px0 + 50 * s, py0 + 30 * s), (px0 + 100 * s, py0 + 46 * s), (px1, py0 + 26 * s), (px1, py1), (px0, py1)],
                  fill=(90, 140, 110, 255))
        d.rectangle((px0, py0 + 58 * s, px1, py1), fill=(70, 120, 200, 255))
        for i, (bx, bh, col) in enumerate(((0.55, 34, (230, 230, 240)), (0.64, 44, (200, 210, 230)), (0.74, 28, (240, 236, 220)), (0.84, 38, (210, 220, 240)))):
            x0 = px0 + (px1 - px0) * bx
            d.rectangle((x0, py0 + 58 * s - bh * s, x0 + 12 * s, py0 + 58 * s), fill=col + (255,), outline=(90, 100, 120, 255))
        d.ellipse((px0 + 30 * s, py0 + 50 * s, px0 + 96 * s, py0 + 70 * s), outline=(250, 250, 255, 255), width=int(2.4 * s))
        for (tx, ty) in ((px0 - 4 * s, py0 - 4 * s), (px1 - 14 * s, py0 - 4 * s)):
            d.rectangle((tx, ty, tx + 18 * s, ty + 8 * s), fill=(250, 240, 200, 255), outline=(200, 180, 130, 255))
        d.text((20 * s, 124 * s), '2012. 7. 1. 세종특별자치시 출범', font=F(8.5), fill=ink, anchor='lm')
        d.line([(20 * s, 136 * s), (120 * s, 136 * s)], fill=(120, 100, 80, 255), width=int(2.2 * s))
        cx, cy, r = 172 * s, 130 * s, 14 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 220, 220, 255), outline=red, width=int(2.4 * s))
        d.text((cx, cy), '기록', font=F(8), fill=red, anchor='mm')
    _DOC[k] = im
    return im


def s08_piece(k, idx):
    """k 번 문서의 idx(0부터) 번 조각."""
    cols, cell = (3, 60) if k == 0 else (4, 50)
    r, c = divmod(idx, cols)

    def f(d, im, s):
        full = _doc_image(k)
        crop = full.crop((c * cell * s, r * cell * s, (c + 1) * cell * s, (r + 1) * cell * s))
        im.paste(crop, (0, 0))
        d.rectangle((0, 0, im.width - 1, im.height - 1), outline=(110, 84, 50, 255), width=int(1.2 * s))
    return art('s08_p%d_%02d' % (k, idx), cell, cell, f)


def s08_full(k):
    w, h = (180, 180) if k == 0 else (200, 150)

    def f(d, im, s):
        im.paste(_doc_image(k), (0, 0))
    return art('s08_full_%d' % k, w, h, f)


def s08_board(k):
    cols, rows, cell = (3, 3, 60) if k == 0 else (4, 3, 50)

    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W - 1, H - 1), outline=(150, 170, 230, 255), width=int(1.6 * s))
        for i in range(1, cols):
            x = W * i / cols
            for y in range(0, H, int(6 * s)):
                d.line([(x, y), (x, y + 3 * s)], fill=(150, 170, 230, 255), width=int(1 * s))
        for j in range(1, rows):
            y = H * j / rows
            for x in range(0, W, int(6 * s)):
                d.line([(x, y), (x + 3 * s, y)], fill=(150, 170, 230, 255), width=int(1 * s))
    return art('s08_board_%d' % k, cols * cell, rows * cell, f)


# ================================================================== 9. 고구마 캐기
def s09_potato():
    def f(d, im, s):
        W, H = im.width, im.height
        d.ellipse((2 * s, 3 * s, W - 2 * s, H - 2 * s), fill=(170, 50, 90, 255), outline=(80, 20, 40, 255), width=int(1.4 * s))
        d.ellipse((W * 0.18, H * 0.18, W * 0.62, H * 0.42), fill=(210, 100, 140, 255))
        for x, y in ((0.30, 0.62), (0.55, 0.70), (0.72, 0.45), (0.45, 0.35)):
            d.line([(W * x, H * y), (W * x + 3 * s, H * y + 1 * s)], fill=(100, 30, 60, 255), width=int(1 * s))
        d.polygon([(W * 0.94, H * 0.48), (W, H * 0.40), (W * 0.98, H * 0.56)], fill=(120, 40, 70, 255))
    return art('s09_potato', 60, 34, f)


def s09_grip():
    def f(d, im, s):
        W, H = im.width, im.height
        g, dk = (70, 170, 80), (24, 90, 40)
        for a, ln in ((-50, 0.46), (-120, 0.44), (-85, 0.48), (-20, 0.36), (-160, 0.36)):
            r = math.radians(a)
            x1, y1 = W / 2 + math.cos(r) * W * ln, H * 0.62 + math.sin(r) * H * ln
            d.line([(W / 2, H * 0.62), (x1, y1)], fill=dk + (255,), width=int(1.4 * s))
            d.ellipse((x1 - 5 * s, y1 - 3.5 * s, x1 + 5 * s, y1 + 3.5 * s), fill=g + (255,), outline=dk + (255,), width=int(0.8 * s))
        d.ellipse((W / 2 - 6 * s, H * 0.62 - 6 * s, W / 2 + 6 * s, H * 0.62 + 6 * s), fill=(250, 220, 190, 255), outline=(120, 70, 40, 255),
                  width=int(1.2 * s))
    return art('s09_grip', 36, 34, f)


def s09_soil():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 0, W, H), 8 * s, fill=(110, 70, 40, 255))
        d.rectangle((0, 0, W, 8 * s), fill=(90, 140, 60, 255))
        rnd = random.Random(9)
        for i in range(26):
            x, y = rnd.uniform(0, W), rnd.uniform(12 * s, H)
            r = rnd.uniform(1.5, 4) * s
            c = rnd.choice([(130, 90, 56), (90, 56, 30), (150, 140, 130)])
            d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=c + (255,))
        for i in range(5):
            x = rnd.uniform(0.1, 0.9) * W
            d.line([(x, 8 * s), (x + rnd.uniform(-20, 20) * s, rnd.uniform(20, 40) * s)], fill=(160, 120, 80, 255), width=int(1 * s))
        d.rounded_rectangle((0, 0, W - 1, H - 1), 8 * s, outline=(50, 30, 16, 255), width=int(1.5 * s))
    return art('s09_soil', 270, 100, f)


def s09_meter():
    def f(d, im, s):
        W, H = im.width, im.height
        top, bot = 3 * s, H - 3 * s
        h = bot - top
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 6 * s, fill=(8, 10, 24, 245))
        for a, b, col in ((0, 0.12, (90, 100, 130)), (0.12, 0.8, (60, 200, 110)), (0.8, 1.0, (230, 50, 60))):
            d.rectangle((3.5 * s, bot - h * b, W - 3.5 * s, bot - h * a), fill=col + (255,))
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 6 * s, outline=(230, 236, 255, 255), width=int(1.4 * s))
        d.text((W / 2, bot - h * 0.9), '!', font=font('jalnan', int(9 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return art('s09_meter', 16, 140, f)


def s09_basket():
    def f(d, im, s):
        W, H = im.width, im.height
        d.polygon([(2 * s, H * 0.3), (W - 2 * s, H * 0.3), (W * 0.85, H - 2 * s), (W * 0.15, H - 2 * s)], fill=(196, 150, 80, 255),
                  outline=(110, 76, 30, 255))
        for i in range(1, 4):
            y = H * 0.3 + (H * 0.7 - 2 * s) * i / 4
            d.line([(W * 0.06, y), (W * 0.94, y)], fill=(150, 110, 50, 255), width=int(1.2 * s))
        d.ellipse((2 * s, H * 0.18, W - 2 * s, H * 0.42), outline=(110, 76, 30, 255), width=int(2 * s))
    return art('s09_basket', 64, 40, f)


# ================================================================== 10. 마라톤 페이스
def s10_runner(col, frame):
    """col: 셔츠 색, frame: a / b / fall."""
    def f(d, im, s):
        W, H = im.width, im.height
        skin, pants = (236, 196, 166), (20, 24, 50)
        hip, sh = (W * 0.50, H * 0.58), (W * 0.54, H * 0.32)
        poses = {'a': dict(fl=((0.68, 0.74), (0.80, 0.94)), bl=((0.38, 0.76), (0.22, 0.90)), fa=((0.70, 0.40), (0.80, 0.30)),
                           ba=((0.40, 0.44), (0.30, 0.54))),
                 'b': dict(fl=((0.58, 0.78), (0.52, 0.97)), bl=((0.44, 0.78), (0.40, 0.97)), fa=((0.62, 0.46), (0.70, 0.54)),
                           ba=((0.46, 0.42), (0.40, 0.30))),
                 'fall': dict(fl=((0.60, 0.80), (0.62, 0.97)), bl=((0.42, 0.80), (0.36, 0.97)), fa=((0.66, 0.50), (0.70, 0.66)),
                              ba=((0.44, 0.50), (0.40, 0.66)))}[frame]
        lw = 4.2 * s

        def limb(a, b, c, cc):
            d.line([a, (W * b[0], H * b[1]), (W * c[0], H * c[1])], fill=cc + (255,), width=int(lw), joint='curve')
        if frame == 'fall':
            hip, sh = (W * 0.50, H * 0.66), (W * 0.62, H * 0.44)
        limb(hip, *poses['bl'], pants)
        limb(sh, *poses['ba'], skin)
        d.line([hip, sh], fill=col + (255,), width=int(9 * s))
        limb(hip, *poses['fl'], pants)
        limb(sh, *poses['fa'], skin)
        hx, hy = sh[0] + 1.5 * s, sh[1] - H * 0.14
        d.ellipse((hx - 6.5 * s, hy - 7 * s, hx + 6.5 * s, hy + 7 * s), fill=skin + (255,), outline=(40, 24, 16, 255), width=int(1 * s))
        d.chord((hx - 7 * s, hy - 8 * s, hx + 7 * s, hy + 4 * s), 180, 360, fill=(20, 18, 24, 255))
        d.rectangle((hx - 7 * s, hy - 3 * s, hx + 7 * s, hy - 1 * s), fill=col + (255,))
        if frame == 'fall':
            for k in range(3):
                d.ellipse((hx + (8 + k * 4) * s, hy - (6 - k * 3) * s, hx + (10 + k * 4) * s, hy - (2 - k * 3) * s), fill=(120, 200, 255, 255))
    name = 's10_run_%d_%d_%d_%s' % (col + (frame,))
    return art(name, 44, 56, f)


def s10_track_bar():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, H * 0.3, W, H * 0.7), H * 0.2, fill=(10, 14, 34, 240), outline=(150, 170, 230, 255), width=int(1 * s))
        for i in range(0, 4):
            x = W * 0.02 + (W * 0.96) * i / 3
            d.line([(x, H * 0.15), (x, H * 0.85)], fill=(150, 170, 230, 255), width=int(1 * s))
        for i in range(8):
            for j in range(2):
                c = (255, 255, 255) if (i + j) % 2 == 0 else (20, 20, 30)
                x0 = W * 0.98 - 1 * s + 0
                d.rectangle((W - 8 * s + (i % 2) * 4 * s, j * H / 2, W - 4 * s + (i % 2) * 4 * s, (j + 1) * H / 2), fill=c + (255,)) if False else None
        d.rectangle((W - 5 * s, 0, W - 1 * s, H), fill=(255, 255, 255, 255))
    return art('s10_bar', 300, 12, f)


def s10_post():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((W * 0.45, H * 0.2, W * 0.55, H), fill=(220, 224, 236, 255))
        d.rounded_rectangle((0, 0, W, H * 0.34), 2 * s, fill=(40, 70, 160, 255), outline=(230, 236, 255, 255), width=int(1 * s))
    return art('s10_post', 20, 40, f)


def s10_finish():
    def f(d, im, s):
        W, H = im.width, im.height
        for x in (0, W - 4 * s):
            d.rectangle((x, 0, x + 4 * s, H), fill=(220, 224, 236, 255))
        d.rectangle((0, 0, W, 14 * s), fill=(200, 40, 60, 255))
        d.text((W / 2, 7 * s), 'FINISH', font=font('jalnan', int(9 * s)), fill=(255, 255, 255, 255), anchor='mm')
        n = 6
        for i in range(n):
            for j in range(2):
                c = (255, 255, 255) if (i + j) % 2 == 0 else (20, 20, 30)
                d.rectangle((W * 0.3 + i * 3 * s, H - (j + 1) * 3 * s, W * 0.3 + (i + 1) * 3 * s, H - j * 3 * s), fill=c + (255,))
    return art('s10_finish', 70, 90, f)
