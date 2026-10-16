# -*- coding: utf-8 -*-
"""상대 후보 그림 (제작자가 준 사진 4장): HUD 원형 초상, 개표·미니게임용 사진 카드."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from art_common import ensure_out, save
import ui_kit as K

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets_src', 'candidates')
# 키: (파일, 얼굴 정사각형 상자, 테두리 색)
CANDS = {
    'm1': ('mayor_1.png', (22, 0, 162, 140), 'royal'),
    'm2': ('mayor_2.png', (38, 0, 178, 140), 'red'),
    'p1': ('pres_1.png', (40, 30, 280, 270), 'royal'),
    'p2': ('pres_2.png', (30, 60, 290, 320), 'red'),
}


def _src(key):
    f = CANDS[key][0]
    im = Image.open(os.path.join(SRC, f)).convert('RGBA')
    if key == 'p2':        # 흑백 판화 느낌 → 살짝 청색 톤
        g = ImageOps.grayscale(im).point(lambda v: 255 if v > 150 else int(v * 0.6))   # 바둑판 무늬(투명 표시) 지우기
        im = ImageOps.colorize(g, (8, 12, 40), (228, 234, 255)).convert('RGBA')
    return im


def ring(key, size=24):
    """HUD 용 원형 초상."""
    im = _src(key)
    face = im.crop(CANDS[key][1])
    return K.portrait_ring(face, size, CANDS[key][2], name='cand_' + key)


def card(key, w=118, h=150):
    """사진 카드 (둥근 모서리 + 테두리 + 아래 그라데이션). 무대 크기의 2배로 저장."""
    p = os.path.join(ensure_out(), 'cand_card_%s_%d.png' % (key, w))
    if os.path.exists(p):
        return p
    S = 2
    W, H = w * S, h * S
    im = _src(key)
    # 위쪽 중심으로 채우기
    r = W / H
    iw, ih = im.size
    if iw / ih > r:
        nw = int(ih * r)
        im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / r)
        im = im.crop((0, 0, iw, nh))
    im = im.resize((W, H), Image.LANCZOS)
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle((3, 3, W - 4, H - 4), 14 * S // 2, fill=255)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ph = im.copy()
    ph.putalpha(m)
    out.alpha_composite(ph)
    # 아래쪽 어둡게
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for y in range(int(H * 0.65), H):
        a = int(170 * (y - H * 0.65) / (H * 0.35))
        sd.line([(0, y), (W, y)], fill=(4, 6, 20, a))
    sh.putalpha(Image.fromarray(__import__('numpy').minimum(__import__('numpy').asarray(sh.getchannel('A')),
                                                             __import__('numpy').asarray(m))))
    out.alpha_composite(sh)
    col = {'red': (240, 90, 110), 'purple': (170, 130, 255), 'royal': (110, 150, 255)}[CANDS[key][2]]
    ImageDraw.Draw(out).rounded_rectangle((3, 3, W - 4, H - 4), 14 * S // 2, outline=col + (255,), width=3 * S // 2 + 1)
    out.save(p)
    return p


def all_rings():
    return {k: ring(k) for k in CANDS}


def all_cards(w=118, h=150):
    return {k: card(k, w, h) for k in CANDS}


if __name__ == '__main__':
    for k in CANDS:
        print(ring(k), card(k))
