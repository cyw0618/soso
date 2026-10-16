# -*- coding: utf-8 -*-
"""세종시 지도 · 대한민국 지도 (제작자가 준 지도 그림 → 게임용 야간 테마) + 확대 지도 + 유세지 핀 위치.

- 세종시: 전체 지도 + '행복도시(신도시) 확대' 지도
- 대한민국: 전체 지도(+ 제주도 따로 그린 상자) + '수도권 확대' 지도(직접 그림)
핀 위치는 무대 좌표로 돌려준다. 핀끼리 겹치지 않게 살짝 밀어낸다.
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from art_common import save, ensure_out, font, OUT
import make_places as MP
from make_places import W, H, MAP_BOX
import data2 as D2

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets_src', 'maps')
BX0, BY0, BX1, BY1 = MAP_BOX
BW, BH = BX1 - BX0, BY1 - BY0
CREDIT = '지도: 제작자 제공 지도를 게임용으로 편집'

# ------------------------------------------------------------------ 세종시 (원본 968x627 위의 위치)
SJ_POS = {1: (445, 305), 2: (470, 322), 3: (690, 242), 4: (357, 352), 5: (405, 338), 6: (600, 262), 7: (425, 315),
          8: (490, 318), 9: (590, 128), 10: (432, 382), 11: (395, 265), 12: (572, 245), 13: (405, 292), 14: (455, 334),
          15: (362, 408), 16: (395, 228), 17: (468, 352), 18: (372, 160), 19: (342, 258), 20: (392, 302), 21: (505, 302),
          22: (232, 345), 23: (560, 168), 24: (535, 343), 25: (440, 372), 26: (420, 355), 27: (622, 162), 28: (470, 226),
          29: (275, 282), 30: (512, 365), 31: (535, 478), 32: (548, 108), 33: (512, 142), 34: (325, 418), 35: (368, 300),
          36: (476, 382), 37: (498, 445), 38: (402, 252), 39: (372, 244), 40: (705, 226)}
SJ_WHOLE = (165, 0, 771, 627)
SJ_LABELS = [('산울동', (365, 201), 10), ('한별동', (418, 193), 10), ('해밀동', (424, 210), 10), ('누리동', (478, 212), 10),
             ('다솜동', (525, 198), 10), ('합강동', (577, 231), 10), ('아름동', (365, 252), 10), ('도담동', (405, 270), 10),
             ('종촌동', (362, 290), 10), ('어진동', (410, 296), 10), ('세종동', (482, 291), 10), ('집현동', (570, 307), 10),
             ('반곡동', (530, 326), 10), ('다정동', (352, 322), 10), ('새롬동', (350, 344), 10), ('나성동', (402, 348), 10),
             ('소담동', (495, 350), 10), ('한솔동', (385, 377), 10), ('보람동', (476, 368), 10), ('대평동', (432, 364), 10),
             ('가람동', (370, 396), 10), ('금남면', (493, 455), 11), ('세종호수공원', (446, 290), 9), ('금강', (418, 338), 12),
             ('미호천', (560, 262), 10)]
SJ_DT = (330, 190, 601, 470)
SJ_DT_IDS = [k for k, (x, y) in SJ_POS.items() if SJ_DT[0] <= x <= SJ_DT[2] and SJ_DT[1] <= y <= SJ_DT[3]]

# ------------------------------------------------------------------ 대한민국 (원본 579x657, 양옆 28px 바다 덧붙임)
KR_PAD = 28
KR_W, KR_H = 579 + KR_PAD * 2, 657


def kr_xy(lon, lat):
    """경위도 → (덧붙인) 대한민국 지도 그림 좌표. 서울·대전·부산·강릉·목포로 맞춘 값."""
    return 123.0 * lon - 15435 + KR_PAD, -155.1 * lat + 5950.5


JEJU_BOX = (46, 562, 178, 646)


def jeju_xy(lon, lat):
    return JEJU_BOX[0] + 12 + (lon - 126.12) * 123.0, JEJU_BOX[1] + 14 + (33.58 - lat) * 155.0


JEJU_IDS = [2, 8, 16]
# 수도권 확대 (직접 그림): 경위도 범위
CAP = (126.40, 37.12, 127.45, 37.98)      # 서경, 남위, 동경, 북위
KR_DT_IDS = [k for k, p in enumerate(D2.KOREA, 1)
             if CAP[0] <= p[3] <= CAP[2] and CAP[1] <= p[4] <= CAP[3]]


def cap_xy(lon, lat):
    """경위도 → 수도권 확대 지도(지도 칸 BWxBH) 좌표."""
    return (lon - CAP[0]) / (CAP[2] - CAP[0]) * BW, (CAP[3] - lat) / (CAP[3] - CAP[1]) * BH


# ------------------------------------------------------------------ 공통
def _night2(im, road_gain=1.0, terr_gain=0.8):
    """make_places._night 와 같은 야간 변환인데 도로·지형 세기를 조절할 수 있다 (도로가 빽빽한 지도용)."""
    from PIL import ImageChops, ImageEnhance
    a = np.asarray(im.convert('RGB'), np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    L = 0.299 * r + 0.587 * g + 0.114 * b
    sat = a.max(-1) - a.min(-1)
    C = lambda *c: np.array(c, np.float32) / 255.0

    def put(out, m, col, k=1.0):
        m = np.clip(m * k, 0, 1)[..., None]
        return out * (1 - m) + m * col
    out = np.ones_like(a) * C(24, 38, 86)
    water = np.clip((g - r - 0.08) * 8, 0, 1) * np.clip((b - r - 0.15) * 8, 0, 1)
    terrain = np.clip(np.clip((g - b) * 5, 0, 1) + np.clip((r - b - 0.03) * 6, 0, 1), 0, 1) * (1 - water)
    out = put(out, terrain, C(30, 52, 92), terr_gain)
    out = put(out, water, C(38, 105, 235))
    d = np.clip((0.955 - L) / 0.33, 0, 1)
    bl = np.clip((b - r) / 0.09, 0, 1)
    text = np.clip((0.56 - L) * 4, 0, 1) * np.clip((0.2 - sat) * 8, 0, 1)
    road = np.clip(d * 3.2, 0, 1) * bl * (1 - water) * (1 - text) * road_gain
    t = np.clip(d * 1.7, 0, 1)[..., None]
    out = put(out, road, C(60, 86, 160) * (1 - t) + C(150, 180, 240) * t)
    img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    glow = img.filter(ImageFilter.GaussianBlur(5))
    img = ImageChops.screen(img, ImageEnhance.Brightness(glow).enhance(0.3))
    out = np.asarray(img, np.float32) / 255.0
    tm = Image.fromarray((np.clip(text * 2, 0, 1) * 255).astype(np.uint8))
    halo = np.asarray(tm.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1)), np.float32) / 255.0
    out = put(out, halo, C(10, 16, 40), 0.7)
    out = put(out, text, C(240, 245, 255))
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def _clean(src, night, no_text=False):
    """도로 번호 방패(파랑 동그라미·노랑 네모)를 지워 화살표와 헷갈리지 않게."""
    from make_cover import push_pull
    a = np.asarray(src.convert('RGB'), np.float32) / 255.0
    blue = (a[..., 2] > 0.6) & (a[..., 0] < 0.4) & (a[..., 2] - a[..., 1] > 0.2)
    yellow = (a[..., 0] > 0.85) & (a[..., 1] > 0.7) & (a[..., 2] < 0.45)
    m = Image.fromarray(((blue | yellow) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
    hole = np.asarray(m) > 0
    if no_text:
        tm = Image.fromarray((MP._text_mask(src) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
        hole = hole | (np.asarray(tm) > 0)
    arr = np.asarray(night, np.float32)
    return Image.fromarray(np.clip(push_pull(arr, ~hole, levels=4), 0, 255).astype(np.uint8))


def _to_box(crop_box, src_xy):
    x0, y0, x1, y1 = crop_box
    return BX0 + (src_xy[0] - x0) * BW / (x1 - x0), BY0 + (src_xy[1] - y0) * BH / (y1 - y0)


def _dashed_circle(img, cx, cy, r):
    d = ImageDraw.Draw(img)
    for k in range(0, 360, 12):
        a0, a1 = math.radians(k), math.radians(k + 7)
        d.line([(cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))],
               fill=(110, 150, 255), width=3)


def _credit(img):
    ImageDraw.Draw(img).text((BX1 - 6, H - 6), CREDIT, font=font('nsrb', 10), fill=(150, 170, 220), anchor='rd')


def stage(xy):
    return xy[0] / 2 - 240, 135 - xy[1] / 2


def relax(pts, min_d=22.0, iters=300):
    """무대 좌표의 핀들을 서로 min_d 이상 떨어지게 밀어낸다 (원래 자리로 당기는 힘 포함)."""
    keys = list(pts)
    P = {k: list(pts[k]) for k in keys}
    A = {k: tuple(pts[k]) for k in keys}
    lo_x, hi_x = BX0 / 2 - 240 + 9, BX1 / 2 - 240 - 9
    for _ in range(iters):
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                dx, dy = P[b][0] - P[a][0], P[b][1] - P[a][1]
                d = math.hypot(dx, dy)
                if d < min_d:
                    if d < 1e-3:
                        dx, dy, d = 1.0, 0.3, 1.04
                    push = (min_d - d) / 2 * 0.5
                    P[a][0] -= dx / d * push; P[a][1] -= dy / d * push
                    P[b][0] += dx / d * push; P[b][1] += dy / d * push
        for k in keys:
            P[k][0] += (A[k][0] - P[k][0]) * 0.03
            P[k][1] += (A[k][1] - P[k][1]) * 0.03
            P[k][0] = min(hi_x, max(lo_x, P[k][0]))
            P[k][1] = min(100, max(-122, P[k][1]))
            if P[k][0] > 70 and P[k][1] > 60:       # 오른쪽 위 지지율 판 피하기
                P[k][1] = 60
    return {k: (round(P[k][0], 1), round(P[k][1], 1)) for k in keys}


# ------------------------------------------------------------------ 세종시
def sejong_art():
    src = Image.open(os.path.join(SRC, 'sejong_map.png')).convert('RGB')
    base = _clean(src, MP._night(src))
    frame = MP._frame_bg()
    whole = MP._place_map(frame, base.crop(SJ_WHOLE))
    # 행복도시 영역 표시
    c0 = _to_box(SJ_WHOLE, ((SJ_DT[0] + SJ_DT[2]) / 2, (SJ_DT[1] + SJ_DT[3]) / 2))
    r = (SJ_DT[2] - SJ_DT[0]) / 2 * BW / (SJ_WHOLE[2] - SJ_WHOLE[0]) * 1.1
    _dashed_circle(whole, c0[0], c0[1], r)
    _credit(whole)
    save(whole, 'map2_whole')
    k = 2
    up = src.crop(SJ_DT).resize(((SJ_DT[2] - SJ_DT[0]) * k, (SJ_DT[3] - SJ_DT[1]) * k), Image.LANCZOS)
    dt = _clean(up, MP._night(up), no_text=True).resize((BW, BH), Image.LANCZOS)
    dd = ImageDraw.Draw(dt)
    for txt, (lx, ly), sz in SJ_LABELS:
        x, y = (lx - SJ_DT[0]) * BW / (SJ_DT[2] - SJ_DT[0]), (ly - SJ_DT[1]) * BH / (SJ_DT[3] - SJ_DT[1])
        _halo_text(dd, (x, y), txt, sz, fill=(200, 215, 255) if sz < 12 else (240, 245, 255))
    _halo_text(dd, (BW - 8, 14), '행복도시 확대', 12, anchor='rm')
    dm = MP._place_map(frame, dt)
    _credit(dm)
    save(dm, 'map2_dt')
    pos = {}
    for kk, xy in SJ_POS.items():
        box = SJ_DT if kk in SJ_DT_IDS else SJ_WHOLE
        sx, sy = stage(_to_box(box, xy))
        pos[kk] = (sx, sy + 15)
    pos = {**relax({k_: v for k_, v in pos.items() if k_ in SJ_DT_IDS}),
           **relax({k_: v for k_, v in pos.items() if k_ not in SJ_DT_IDS})}
    return pos, (c0[0], c0[1], r)


# ------------------------------------------------------------------ 대한민국
JEJU = [(126.16, 33.30), (126.17, 33.38), (126.26, 33.44), (126.36, 33.47), (126.48, 33.51), (126.60, 33.52),
        (126.72, 33.55), (126.83, 33.55), (126.93, 33.50), (126.95, 33.45), (126.90, 33.40), (126.80, 33.32),
        (126.65, 33.27), (126.50, 33.23), (126.35, 33.22), (126.25, 33.24)]
LAND_C, TERR_C, SEA_C = (24, 38, 86), (30, 52, 92), (38, 105, 235)


def _halo_text(d, xy, txt, size, fill=(240, 245, 255), anchor='mm'):
    f = font('nsrb', size)
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            d.text((xy[0] + dx, xy[1] + dy), txt, font=f, fill=(10, 16, 40), anchor=anchor)
    d.text(xy, txt, font=f, fill=fill, anchor=anchor)


def korea_art():
    src0 = Image.open(os.path.join(SRC, 'korea_map.png')).convert('RGB')
    sea = src0.getpixel((560, 600))
    src = Image.new('RGB', (KR_W, KR_H), sea)
    src.paste(src0, (KR_PAD, 0))
    base = _clean(src, _night2(src, road_gain=0.45, terr_gain=0.35))
    # 제주도 상자
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(JEJU_BOX, 8, fill=(18, 60, 150), outline=(110, 150, 255), width=2)
    d.polygon([jeju_xy(*p) for p in JEJU], fill=TERR_C, outline=(150, 190, 255))
    d.ellipse([v - 3 for v in jeju_xy(126.53, 33.36)] + [v + 3 for v in jeju_xy(126.53, 33.36)], fill=(200, 220, 255))
    _halo_text(d, (JEJU_BOX[0] + 30, JEJU_BOX[3] - 12), '제주도', 11)
    frame = MP._frame_bg()
    whole = MP._place_map(frame, base)
    full = (0, 0, KR_W, KR_H)
    cx0, cy0 = kr_xy((CAP[0] + CAP[2]) / 2, (CAP[1] + CAP[3]) / 2)
    c0 = _to_box(full, (cx0, cy0))
    r = (CAP[2] - CAP[0]) * 123.0 / 2 * BW / KR_W * 1.05
    _dashed_circle(whole, c0[0], c0[1], r)
    _credit(whole)
    save(whole, 'map3_whole')
    save(MP._place_map(frame, capital_art()), 'map3_dt')
    pos = {}
    for kk, p in enumerate(D2.KOREA, 1):
        lon, lat = p[3], p[4]
        if kk in KR_DT_IDS:
            x, y = cap_xy(lon, lat)
            sx, sy = stage((BX0 + x, BY0 + y))
        elif kk in JEJU_IDS:
            sx, sy = stage(_to_box(full, jeju_xy(lon, lat)))
        else:
            sx, sy = stage(_to_box(full, kr_xy(lon, lat)))
        pos[kk] = (sx, sy + 15)
    pos = {**relax({k_: v for k_, v in pos.items() if k_ in KR_DT_IDS}, 24),
           **relax({k_: v for k_, v in pos.items() if k_ not in KR_DT_IDS})}
    return pos, (c0[0], c0[1], r)


def capital_art():
    """수도권 확대 지도 (야간 테마로 직접 그림)."""
    S = 2
    im = Image.new('RGB', (BW * S, BH * S), SEA_C)
    d = ImageDraw.Draw(im)
    P = lambda pts: [(x * S, y * S) for x, y in (cap_xy(lo, la) for lo, la in pts)]
    land = [(126.62, 38.0), (126.66, 37.80), (126.58, 37.72), (126.62, 37.62), (126.66, 37.56), (126.60, 37.50),
            (126.62, 37.44), (126.66, 37.38), (126.70, 37.33), (126.66, 37.28), (126.72, 37.22), (126.78, 37.16),
            (126.80, 37.10), (127.50, 37.10), (127.50, 38.0)]
    islands = [[(126.38, 37.80), (126.52, 37.79), (126.56, 37.70), (126.52, 37.62), (126.42, 37.60), (126.36, 37.67)],
               [(126.40, 37.52), (126.55, 37.51), (126.58, 37.47), (126.53, 37.43), (126.42, 37.43), (126.38, 37.47)],
               [(126.55, 37.30), (126.62, 37.29), (126.63, 37.24), (126.57, 37.23)]]
    for poly in [land] + islands:
        d.polygon(P(poly), fill=LAND_C)
    # 지형 얼룩 (산)
    rng = np.random.RandomState(3)
    tex = Image.new('L', (BW * S // 8, BH * S // 8), 0)
    tex.putdata([int(v) for v in rng.randint(0, 255, tex.size[0] * tex.size[1])])
    tex = tex.resize((BW * S, BH * S), Image.BICUBIC).filter(ImageFilter.GaussianBlur(14)).point(lambda v: 255 if v > 140 else 0)
    landm = Image.new('L', im.size, 0)
    ImageDraw.Draw(landm).polygon(P(land), fill=255)
    for poly in islands:
        ImageDraw.Draw(landm).polygon(P(poly), fill=255)
    terr = Image.new('RGB', im.size, TERR_C)
    im = Image.composite(terr, im, Image.fromarray(np.minimum(np.asarray(tex), np.asarray(landm)) // 2))
    d = ImageDraw.Draw(im)
    # 강
    han = [(127.50, 37.49), (127.38, 37.52), (127.30, 37.52), (127.22, 37.56), (127.15, 37.57), (127.10, 37.54),
           (127.05, 37.525), (127.00, 37.515), (126.95, 37.52), (126.90, 37.54), (126.85, 37.57), (126.80, 37.60),
           (126.73, 37.64), (126.66, 37.70), (126.58, 37.74)]
    d.line(P(han), fill=SEA_C, width=7 * S, joint='curve')
    d.line(P([(126.66, 37.76), (126.80, 37.83), (126.92, 37.90), (127.05, 37.98)]), fill=SEA_C, width=5 * S, joint='curve')
    # 도로 (고속도로·순환도로)
    roads = [[(127.03, 37.50), (127.06, 37.40), (127.08, 37.28), (127.10, 37.10)],
             [(126.65, 37.30), (126.90, 37.32), (127.10, 37.30), (127.30, 37.28), (127.50, 37.27)],
             [(126.88, 37.48), (126.84, 37.35), (126.82, 37.10)],
             [(126.60, 37.55), (126.52, 37.50)], [(126.64, 37.42), (126.53, 37.45)],
             [(127.10, 37.60), (127.30, 37.62), (127.50, 37.64)], [(126.98, 37.60), (126.95, 37.75), (126.90, 37.98)]]
    ring = [(126.99 + 0.21 * math.cos(a / 20 * math.pi), 37.55 + 0.17 * math.sin(a / 20 * math.pi)) for a in range(41)]
    for rd in roads + [ring]:
        d.line(P(rd), fill=(78, 108, 190), width=4 * S, joint='curve')
        d.line(P(rd), fill=(185, 212, 255), width=int(1.6 * S), joint='curve')
    # 서울 경계 (점선)
    seoul = [(126.80, 37.58), (126.85, 37.66), (126.95, 37.69), (127.07, 37.70), (127.12, 37.62), (127.18, 37.55),
             (127.13, 37.47), (127.05, 37.43), (126.95, 37.45), (126.85, 37.48), (126.80, 37.55), (126.80, 37.58)]
    sp = P(seoul)
    for (xa, ya), (xb, yb) in zip(sp, sp[1:]):
        n = max(1, int(math.hypot(xb - xa, yb - ya) / (10 * S)))
        for t in range(0, n, 2):
            d.line([(xa + (xb - xa) * t / n, ya + (yb - ya) * t / n), (xa + (xb - xa) * (t + 1) / n, ya + (yb - ya) * (t + 1) / n)],
                   fill=(140, 180, 255), width=2 * S)
    im = im.resize((BW, BH), Image.LANCZOS)
    glow = im.filter(ImageFilter.GaussianBlur(4))
    from PIL import ImageChops, ImageEnhance
    im = ImageChops.screen(im, ImageEnhance.Brightness(glow).enhance(0.3))
    d = ImageDraw.Draw(im)
    labels = [('서울', 126.99, 37.60, 18), ('인천', 126.70, 37.45, 12), ('수원', 127.01, 37.24, 12), ('용인', 127.22, 37.21, 12),
              ('이천', 127.43, 37.22, 12), ('성남', 127.14, 37.40, 11), ('고양', 126.83, 37.68, 11), ('김포', 126.70, 37.63, 11),
              ('부천', 126.78, 37.50, 11), ('안산', 126.82, 37.30, 11), ('하남', 127.23, 37.52, 11), ('남양주', 127.24, 37.66, 11),
              ('의정부', 127.05, 37.75, 11), ('파주', 126.80, 37.80, 11), ('영종도', 126.47, 37.40, 10), ('강화도', 126.45, 37.84, 10),
              ('한강', 127.20, 37.585, 10)]
    for txt, lo, la, sz in labels:
        _halo_text(d, cap_xy(lo, la), txt, sz)
    _halo_text(d, (BW - 8, 14), '수도권 확대', 12, anchor='rm')
    return im


def build_all():
    ensure_out()
    sj = sejong_art()
    kr = korea_art()
    return {'sj': sj, 'kr': kr}


if __name__ == '__main__':
    r = build_all()
    print('sejong dt', SJ_DT_IDS)
    print('korea dt', KR_DT_IDS)
