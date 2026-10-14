# -*- coding: utf-8 -*-
"""장소 사진 → 게임 배경(960x540), 조치원 지도 → 게임 지도(야간 테마) + 시내 확대 창.

입력: assets_src/places/NN_이름.png (사용자가 준 사진), 16_지도_확대.png (지도 캡처)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
from art_common import *

W, H = 960, 540

PHOTOS = ['01_조치원역', '02_상리은행나무길', '03_세종전통시장', '04_청과거리', '05_조치원테마거리', '06_왕성길',
          '07_조치원문화정원', '08_1927아트센터', '09_도도리파크', '10_세종시민운동장', '11_조천벚꽃길',
          '12_조천연꽃공원', '13_홍익대세종캠퍼스', '14_고려대세종캠퍼스', '15_신안저수지']

# 지도 캡처(16_지도_확대.png, 1521x786) 위의 장소 위치 (40곳)
MAP_POS = {1: (553, 478), 2: (538, 452), 3: (588, 500), 4: (600, 522), 5: (580, 462), 6: (575, 540),
           7: (628, 452), 8: (545, 525), 9: (462, 585), 10: (520, 642), 11: (622, 600), 12: (598, 697),
           13: (462, 233), 14: (452, 367), 15: (380, 330),
           16: (125, 262), 17: (38, 383), 18: (130, 470), 19: (305, 415), 20: (250, 330), 21: (200, 165),
           22: (395, 85), 23: (345, 245), 24: (540, 300), 25: (450, 460), 26: (400, 530), 27: (385, 610),
           28: (455, 705), 29: (530, 765), 30: (205, 660), 31: (80, 735), 32: (40, 650), 33: (690, 670),
           34: (625, 360), 35: (560, 505), 36: (615, 485), 37: (655, 525), 38: (580, 440), 39: (560, 568),
           40: (595, 600)}
WHOLE = (0, 0, 760, 786)                  # 전체 지도로 쓸 영역 (세종 쪽)
DOWNTOWN = (490, 410, 700, 627)           # 시내 확대 지도 영역
MAP_BOX = (219, 0, 741, 540)              # 960x540 배경 위에서 지도가 놓이는 칸 (가운데)
DOWNTOWN_IDS = [k for k, (x, y) in MAP_POS.items() if DOWNTOWN[0] <= x <= DOWNTOWN[2] and DOWNTOWN[1] <= y <= DOWNTOWN[3]]


def _cover(im, w=W, h=H, focus=0.5):
    r = w / h
    iw, ih = im.size
    if iw / ih > r:
        nw = int(ih * r)
        x0 = int((iw - nw) * focus)
        im = im.crop((x0, 0, x0 + nw, ih))
    else:
        nh = int(iw / r)
        y0 = int((ih - nh) * focus)
        im = im.crop((0, y0, iw, y0 + nh))
    return im.resize((w, h), Image.LANCZOS)


def place_bg(i):
    """i: 1~15. 사진을 16:9 로 채우고, 선명하게 + 색 보정 + 위/아래 어둡게(글자 잘 보이게)."""
    name = PHOTOS[i - 1]
    src = Image.open(os.path.join(SRC, 'places', name + '.png')).convert('RGB')
    w, h = src.size
    if w / h < 1.2:            # 세로 사진: 흐린 배경 + 가운데 사진
        back = _cover(src).filter(ImageFilter.GaussianBlur(18))
        back = ImageEnhance.Brightness(back).enhance(0.7)
        fh = H
        fw = int(w * fh / h)
        front = src.resize((fw, fh), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2.0, 80, 2))
        m = Image.new('L', (fw, fh), 255)
        md = ImageDraw.Draw(m)
        for k in range(30):
            md.line([(k, 0), (k, fh)], fill=int(255 * k / 30))
            md.line([(fw - 1 - k, 0), (fw - 1 - k, fh)], fill=int(255 * k / 30))
        back.paste(front, ((W - fw) // 2, 0), m)
        img = back
    else:
        focus = {14: 0.3}.get(i, 0.5)
        img = _cover(src, focus=focus).filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=2))
    img = ImageEnhance.Color(img).enhance(1.15)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    return save(finish_place(img), 'place_%02d' % i)


def finish_place(img):
    """배경 마무리: 위(제목/HUD)와 아래(조작 안내)를 살짝 어둡게 + 비네트."""
    # 위(제목/HUD)와 아래(조작 안내)를 살짝 어둡게
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for y in range(H):
        a = 0
        if y < 90:
            a = int(110 * (1 - y / 90) ** 1.6)
        elif y > H - 110:
            a = int(120 * ((y - (H - 110)) / 110) ** 1.6)
        od.line([(0, y), (W, y)], fill=(6, 10, 30, a))
    img = Image.alpha_composite(img.convert('RGBA'), ov)
    # 비네트
    vm = Image.new('L', (W // 8, H // 8), 0)
    vd = ImageDraw.Draw(vm)
    for k in range(24):
        vd.rectangle((k, k, W // 8 - 1 - k, H // 8 - 1 - k), outline=int(90 * (1 - k / 24) ** 2))
    vm = vm.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30))
    dark = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    dark.putalpha(vm)
    return Image.alpha_composite(img, dark).convert('RGB')


def _night(im):
    """밝은 지도 → 야간 테마. 바탕은 남색, 도로는 밝은 청백색, 물은 청색, 글자는 흰색으로 다시 칠한다."""
    a = np.asarray(im.convert('RGB'), np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    L = 0.299 * r + 0.587 * g + 0.114 * b
    sat = a.max(-1) - a.min(-1)

    def C(*c):
        return np.array(c, np.float32) / 255.0

    def put(out, m, col, k=1.0):
        m = np.clip(m * k, 0, 1)[..., None]
        return out * (1 - m) + m * col

    out = np.ones_like(a) * C(24, 38, 86)
    water = np.clip((g - r - 0.08) * 8, 0, 1) * np.clip((b - r - 0.15) * 8, 0, 1)
    terrain = np.clip(np.clip((g - b) * 5, 0, 1) + np.clip((r - b - 0.03) * 6, 0, 1), 0, 1) * (1 - water)
    out = put(out, terrain, C(30, 52, 92), 0.8)
    out = put(out, water, C(38, 105, 235))
    # 도로: 바탕보다 어둡고 푸른 기가 있는 선 (진할수록 큰 도로 → 더 밝게)
    d = np.clip((0.955 - L) / 0.33, 0, 1)
    bl = np.clip((b - r) / 0.09, 0, 1)
    text = np.clip((0.56 - L) * 4, 0, 1) * np.clip((0.2 - sat) * 8, 0, 1)
    road = np.clip(d * 3.2, 0, 1) * bl * (1 - water) * (1 - text)
    t = np.clip(d * 1.7, 0, 1)[..., None]
    out = put(out, road, C(78, 108, 190) * (1 - t) + C(185, 212, 255) * t)
    img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    glow = img.filter(ImageFilter.GaussianBlur(5))
    img = ImageChops.screen(img, ImageEnhance.Brightness(glow).enhance(0.35))
    out = np.asarray(img, np.float32) / 255.0
    # 글자: 어두운 테두리 + 흰 글씨
    tm = Image.fromarray((np.clip(text * 2, 0, 1) * 255).astype(np.uint8))
    halo = np.asarray(tm.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1)), np.float32) / 255.0
    out = put(out, halo, C(10, 16, 40), 0.7)
    out = put(out, text, C(240, 245, 255))
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


# 지도 캡처에서 지울 부분: 개인 저장 장소 핀/문구, 호텔 광고 핀
MAP_ERASE = [(508, 456, 652, 499), (762, 170, 852, 230)]


def _text_mask(src):
    """지도 글자(어두운 무채색)와 그 흰 테두리 자리."""
    a = np.asarray(src.convert('RGB'), np.float32) / 255.0
    L = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    sat = a.max(-1) - a.min(-1)
    t = (L < 0.5) & (sat < 0.09)
    return t


def _clean_map(src, night, box=(0, 0), scale=1.0, dil=7, no_text=False):
    """개인 저장 장소/광고 핀(주황·분홍 글자와 아이콘)만 골라 지우고 주변 골목 무늬로 메운다.
    box/scale: src 가 캡처의 어느 부분을 몇 배로 키운 것인지 (지울 영역 좌표 변환용)."""
    from make_cover import push_pull
    a = np.asarray(src, np.float32) / 255.0
    mark = ((a[..., 0] - a[..., 1]) > 0.18) & ((a.max(-1) - a.min(-1)) > 0.22)
    zone = np.zeros(mark.shape, bool)
    for x0, y0, x1, y1 in MAP_ERASE:
        X0, Y0 = int((x0 - 6 - box[0]) * scale), int((y0 - 6 - box[1]) * scale)
        X1, Y1 = int((x1 + 6 - box[0]) * scale), int((y1 + 6 - box[1]) * scale)
        zone[max(0, Y0):max(0, Y1), max(0, X0):max(0, X1)] = True
    hole = Image.fromarray(((mark & zone) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(dil))
    hole = np.asarray(hole) > 0
    # 도로 번호 방패(진한 파랑 동그라미)는 우리 화살표와 헷갈리니 지운다
    shield = (a[..., 2] > 0.6) & (a[..., 0] < 0.4) & (a[..., 2] - a[..., 1] > 0.2)
    sh = Image.fromarray((shield * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(int(9 * scale) | 1))
    hole = hole | (np.asarray(sh) > 0)
    if no_text:
        tm = Image.fromarray((_text_mask(src) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(dil))
        hole = hole | (np.asarray(tm) > 0)
    arr = np.asarray(night, np.float32)
    filled = push_pull(arr, ~hole, levels=4)
    return Image.fromarray(np.clip(filled, 0, 255).astype(np.uint8))


def _frame_bg():
    """지도 바깥(왼쪽·오른쪽 메뉴 자리): 짙은 남색 + 은은한 격자."""
    bg = Image.new('RGB', (W, H), (6, 10, 26))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(6 + 6 * t), int(10 + 8 * t), int(26 + 20 * t)))
    for x in range(0, W, 24):
        d.line([(x, 0), (x, H)], fill=(14, 22, 50))
    for y in range(0, H, 24):
        d.line([(0, y), (W, y)], fill=(14, 22, 50))
    return bg


def _place_map(bg, im):
    x0, y0, x1, y1 = MAP_BOX
    bg = bg.copy()
    # 바깥 빛
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).rectangle((x0 - 2, y0, x1 + 2, y1), fill=200)
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    bg = Image.composite(Image.new('RGB', (W, H), (50, 90, 220)), bg, glow.point(lambda v: int(v * 0.55)))
    bg.paste(im.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
    d = ImageDraw.Draw(bg)
    d.line([(x0, 0), (x0, H)], fill=(70, 110, 255), width=2)
    d.line([(x1, 0), (x1, H)], fill=(70, 110, 255), width=2)
    return bg


def whole_xy(k):
    """전체 지도 모드에서 장소 k 의 배경(960x540) 좌표."""
    cx, cy = MAP_POS[k]
    x0, y0, x1, y1 = MAP_BOX
    return x0 + (cx - WHOLE[0]) * (x1 - x0) / (WHOLE[2] - WHOLE[0]), y0 + (cy - WHOLE[1]) * (y1 - y0) / (WHOLE[3] - WHOLE[1])


def downtown_xy(k):
    cx, cy = MAP_POS[k]
    x0, y0, x1, y1 = MAP_BOX
    return x0 + (cx - DOWNTOWN[0]) * (x1 - x0) / (DOWNTOWN[2] - DOWNTOWN[0]), y0 + (cy - DOWNTOWN[1]) * (y1 - y0) / (DOWNTOWN[3] - DOWNTOWN[1])


def map_art():
    """전체 지도(map_whole)와 시내 확대 지도(map_dt)를 만든다. 핀 위치(배경 좌표)와 시내 원을 돌려준다."""
    src = Image.open(os.path.join(SRC, 'places', '16_지도_확대.png')).convert('RGB')
    base = _clean_map(src, _night(src))
    frame = _frame_bg()
    # 전체 지도
    whole = base.crop(WHOLE)
    wm = _place_map(frame, whole)
    d = ImageDraw.Draw(wm)
    # 시내 영역 (점선 원)
    x0, y0, x1, y1 = MAP_BOX
    sx = (x1 - x0) / (WHOLE[2] - WHOLE[0])
    sy = (y1 - y0) / (WHOLE[3] - WHOLE[1])
    cx = x0 + ((DOWNTOWN[0] + DOWNTOWN[2]) / 2 - WHOLE[0]) * sx
    cy = y0 + ((DOWNTOWN[1] + DOWNTOWN[3]) / 2 - WHOLE[1]) * sy
    r = (DOWNTOWN[2] - DOWNTOWN[0]) / 2 * sx * 1.06
    for k in range(0, 360, 12):
        a0, a1 = math.radians(k), math.radians(k + 7)
        d.line([(cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))],
               fill=(110, 150, 255), width=3)
    d.text((x1 - 6, H - 6), '지도: Google 지도 캡처를 게임용으로 편집', font=font('nsrb', 10), fill=(150, 170, 220), anchor='rd')
    save(wm, 'map_whole')
    # 시내 확대 지도 (해상도를 올려 선명하게)
    k = 2.5
    up = src.crop(DOWNTOWN).resize((int((DOWNTOWN[2] - DOWNTOWN[0]) * k), int((DOWNTOWN[3] - DOWNTOWN[1]) * k)), Image.LANCZOS)
    dt = _clean_map(up, _night(up), box=DOWNTOWN[:2], scale=k, dil=11, no_text=True)
    dt = dt.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    dm = _place_map(frame, dt)
    d = ImageDraw.Draw(dm)
    d.text((x1 - 6, H - 6), '지도: Google 지도 캡처를 게임용으로 편집', font=font('nsrb', 10), fill=(150, 170, 220), anchor='rd')
    save(dm, 'map_dt')
    pos = {k: (downtown_xy(k) if k in DOWNTOWN_IDS else whole_xy(k)) for k in MAP_POS}
    return pos, (cx, cy, r)


def build_all():
    for i in range(1, 16):
        place_bg(i)
    import place_art
    place_art.build_all()
    return map_art()


if __name__ == '__main__':
    pos, circle = map_art()
    print('downtown', DOWNTOWN_IDS)
    print('pins', {k: (round(v[0]), round(v[1])) for k, v in pos.items()})
