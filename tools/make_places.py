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

# 지도 캡처(16_지도_확대.png, 1521x786) 위의 장소 위치
MAP_POS = {1: (553, 478), 2: (538, 452), 3: (588, 500), 4: (600, 522), 5: (572, 470), 6: (575, 540),
           7: (628, 452), 8: (545, 525), 9: (478, 600), 10: (505, 630), 11: (622, 600), 12: (598, 697),
           13: (462, 233), 14: (452, 367), 15: (395, 347)}
MAP_CROP = (140, 160, 1192, 752)          # 게임 지도로 쓸 영역 (16:9)
DOWNTOWN = (515, 425, 655, 565)           # 시내 확대 창 영역
DOWNTOWN_IDS = [1, 2, 3, 4, 5, 6, 7, 8]


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
    img = Image.alpha_composite(img, dark).convert('RGB')
    return save(img, 'place_%02d' % i)


def _night(im):
    """밝은 지도 → 야간 테마 (반전 + 색상 180도 회전 + 남색 톤)."""
    a = np.asarray(im.convert('RGB'), np.float32) / 255.0
    inv = 1.0 - a
    # 색상 180도 회전(반전으로 뒤집힌 색을 되돌림): YIQ 공간에서 I,Q 부호 반전
    Y = 0.299 * inv[..., 0] + 0.587 * inv[..., 1] + 0.114 * inv[..., 2]
    I = 0.596 * inv[..., 0] - 0.274 * inv[..., 1] - 0.322 * inv[..., 2]
    Q = 0.211 * inv[..., 0] - 0.523 * inv[..., 1] + 0.312 * inv[..., 2]
    I, Q = -I, -Q
    r = Y + 0.956 * I + 0.621 * Q
    g = Y - 0.272 * I - 0.647 * Q
    b = Y - 1.106 * I + 1.703 * Q
    out = np.clip(np.stack([r, g, b], -1), 0, 1)
    # 남색 톤 입히기 (어두운 바탕을 남색으로)
    navy = np.array([0.07, 0.10, 0.24])
    lum = out.mean(-1, keepdims=True)
    out = out * 0.85 + navy * (1 - lum) * 0.9
    # 도로/하천을 살짝 빛나게
    out = np.clip(out * 1.08, 0, 1)
    return Image.fromarray((out * 255).astype(np.uint8))


# 지도 캡처에서 지울 부분: 개인 저장 장소 핀/문구, 호텔 광고 핀
MAP_ERASE = [(508, 456, 652, 499), (762, 170, 852, 230)]


def _clean_map(src):
    from make_cover import push_pull
    arr = np.asarray(src, np.float32)
    for x0, y0, x1, y1 in MAP_ERASE:
        m = 30
        X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(src.width, x1 + m), min(src.height, y1 + m)
        sub = arr[Y0:Y1, X0:X1].copy()
        hole = np.zeros(sub.shape[:2], bool)
        hole[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = True
        filled = push_pull(sub, ~hole, levels=5)
        arr[Y0:Y1, X0:X1] = np.where(hole[..., None], filled, sub)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def map_art():
    src = Image.open(os.path.join(SRC, 'places', '16_지도_확대.png')).convert('RGB')
    base = _night(_clean_map(src))
    crop = base.crop(MAP_CROP).resize((W, H), Image.LANCZOS)
    crop = ImageEnhance.Contrast(crop).enhance(1.1)
    crop = ImageEnhance.Brightness(crop).enhance(0.86)
    # 도로 빛번짐
    glow = crop.filter(ImageFilter.GaussianBlur(6))
    crop = ImageChops.screen(crop, ImageEnhance.Brightness(glow).enhance(0.35))
    sx = W / (MAP_CROP[2] - MAP_CROP[0])
    sy = H / (MAP_CROP[3] - MAP_CROP[1])
    pos = {k: ((x - MAP_CROP[0]) * sx, (y - MAP_CROP[1]) * sy) for k, (x, y) in MAP_POS.items()}
    # 시내 영역 표시 (점선 원)
    d = ImageDraw.Draw(crop)
    dx0 = (DOWNTOWN[0] - MAP_CROP[0]) * sx
    dy0 = (DOWNTOWN[1] - MAP_CROP[1]) * sy
    dx1 = (DOWNTOWN[2] - MAP_CROP[0]) * sx
    dy1 = (DOWNTOWN[3] - MAP_CROP[1]) * sy
    cx, cy, r = (dx0 + dx1) / 2, (dy0 + dy1) / 2, (dx1 - dx0) / 2
    for k in range(0, 360, 12):
        a0, a1 = math.radians(k), math.radians(k + 7)
        d.line([(cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))], fill=(70, 110, 255), width=3)
    # 출처 표기
    d.text((W - 8, H - 6), '지도: Google 지도 캡처를 게임용으로 편집', font=font('nsrb', 11), fill=(150, 170, 220), anchor='rd')
    save(crop, 'map_bg')
    # 시내 확대 창 (원형)
    inset_src = base.crop(DOWNTOWN)
    D = 240
    inset = inset_src.resize((D, D), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 70, 2))
    inset = ImageEnhance.Contrast(inset).enhance(1.12)
    inset = ImageEnhance.Brightness(inset).enhance(0.9)
    ring = Image.new('RGBA', (D + 24, D + 24), (0, 0, 0, 0))
    m = Image.new('L', (D, D), 0)
    ImageDraw.Draw(m).ellipse((0, 0, D - 1, D - 1), fill=255)
    sh = Image.new('L', ring.size, 0)
    ImageDraw.Draw(sh).ellipse((8, 14, D + 16, D + 22), fill=150)
    shadow = Image.new('RGBA', ring.size, (0, 0, 0, 255))
    shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(6)))
    ring.alpha_composite(shadow)
    ii = inset.convert('RGBA')
    ii.putalpha(m)
    ring.alpha_composite(ii, (12, 12))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((10, 10, D + 13, D + 13), outline=(60, 100, 240, 255), width=4)
    rd.ellipse((15, 15, D + 8, D + 8), outline=(255, 255, 255, 60), width=1)
    save(ring, 'map_inset')
    ipos = {k: (12 + (MAP_POS[k][0] - DOWNTOWN[0]) * D / (DOWNTOWN[2] - DOWNTOWN[0]),
                12 + (MAP_POS[k][1] - DOWNTOWN[1]) * D / (DOWNTOWN[3] - DOWNTOWN[1])) for k in DOWNTOWN_IDS}
    return pos, (cx, cy, r), ipos, ring.size


def build_all():
    for i in range(1, 16):
        place_bg(i)
    return map_art()


if __name__ == '__main__':
    import math
    pos, circle, ipos, isz = build_all()
    print('pins', {k: (round(v[0]), round(v[1])) for k, v in pos.items()})
    print('downtown circle', circle, 'inset', isz, {k: (round(v[0]), round(v[1])) for k, v in ipos.items()})
