# -*- coding: utf-8 -*-
"""표지 합성: 사진1(어르신) → 뒤쪽 할아버지, 사진3(청년) → 가운데 청년.

얼굴을 왜곡하지 않고(균일 배율) 본인의 얼굴형 그대로 웹툰 그림체(셀 셰이딩 + 선)로 바꿔서
웹툰 얼굴 위치에 넣는다. 웹툰의 머리카락은 위에 겹쳐서 자연스럽게 이어 붙이고,
청년의 머리는 본인처럼 검은 머리로 바꾼다.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_common import *
from face_toon import *

DEBUG = False


def _palette_from(cover_s, poly_orig, lum_floor):
    box = (min(p[0] for p in poly_orig) * S, min(p[1] for p in poly_orig) * S,
           max(p[0] for p in poly_orig) * S, max(p[1] for p in poly_orig) * S)
    box = tuple(int(v) for v in box)
    crop = np.asarray(cover_s.crop(box), np.float32)
    m = poly_layer((box[2] - box[0], box[3] - box[1]), [((p[0] * S - box[0]), (p[1] * S - box[1])) for p in poly_orig], feather=0)
    L = lum(crop)
    sel = (m > 0.7) & (L > lum_floor)
    px, Ls = crop[sel], L[sel]
    qs = np.percentile(Ls, [8, 35, 65, 92])
    cols = []
    for lo, hi in [(0, qs[0]), (qs[0], qs[1]), (qs[1], qs[2]), (qs[2], qs[3]), (qs[3], 255)]:
        pick = px[(Ls >= lo) & (Ls <= hi)]
        cols.append(tuple(np.median(pick, 0)) if len(pick) else (200, 160, 150))
    return [(i / (len(cols) - 1), c) for i, c in enumerate(cols)]


# ------------------------------------------------------------------ 할아버지
GP_FACE = [(105, 42), (127, 38), (150, 42), (164, 52), (170, 66), (173, 85), (175, 105), (175, 125), (172, 145),
           (166, 160), (155, 174), (142, 184), (127, 189), (110, 185), (94, 176), (82, 162), (76, 145), (73, 125),
           (74, 105), (78, 85), (84, 66), (92, 52)]
GP_CARTOON_FACE = [(50, 52), (60, 43), (80, 40), (104, 39), (124, 41), (130, 48), (131, 70), (131, 95), (130, 112),
                   (127, 132), (124, 150), (120, 166), (108, 172), (92, 173), (76, 169), (64, 159), (54, 147),
                   (44, 135), (36, 124), (33, 108), (34, 92), (39, 77), (44, 63)]


def do_grandpa(base, cover_s, photo):
    pal = _palette_from(cover_s, GP_CARTOON_FACE, 95)
    s = 0.90
    tx, ty = 85 - s * 126, 172 - s * 190

    def keep(cart, org):  # 웹툰 흰 머리카락은 얼굴 위로 겹친다 (이마 위쪽과 왼쪽 관자놀이 쪽만)
        h, w = cart.shape[:2]
        yy = (np.arange(h)[:, None] + org[1]) / S
        xx = (np.arange(w)[None, :] + org[0]) / S
        zone = np.clip((60.0 - yy) / 4.0, 0, 1) * np.ones((1, w))
        zone = np.maximum(zone, np.clip((46.0 - xx) / 4.0, 0, 1) * np.ones((h, 1)))
        R, Bc = cart[..., 0], cart[..., 2]
        hair = ((Bc - R) > 24) & (lum(cart) > 120)
        k = np.asarray(Image.fromarray((hair * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0)), np.float32) / 255.0
        return k * zone

    place_face(base, cover_s, photo, GP_FACE, s, tx, ty, pal, (84, 46, 92), keep_fn=keep, pal_mix=0.5, bands=4,
               line_C=13.0, shade_mix=0.35, line_gain=1.0)


# ------------------------------------------------------------------ 청년
YO_FACE = [(46, 80), (70, 76), (100, 74), (126, 76), (143, 82), (146, 92), (144, 104), (141, 118), (136, 134),
           (127, 145), (115, 151), (102, 153), (88, 151), (74, 146), (60, 138), (52, 126), (47, 110), (44, 94), (44, 86)]
YO_CARTOON_FACE = [(143, 236), (146, 227), (160, 223), (180, 222), (200, 222), (220, 224), (232, 230), (238, 242),
                   (238, 256), (234, 272), (226, 286), (214, 298), (200, 307), (190, 311), (178, 308), (165, 298),
                   (153, 286), (146, 272), (142, 256)]


def recolor_hair_black(cover_s, region):
    """웹툰의 갈색 머리를 본인처럼 검은 머리(푸른빛 하이라이트)로."""
    x0, y0, x1, y1 = [int(v * S) for v in region]
    crop = np.asarray(cover_s.crop((x0, y0, x1, y1)), np.float32)
    mx, mn = crop.max(-1), crop.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    L = lum(crop)
    r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]
    brownish = (r > g * 1.05) & (g > b * 1.05)          # 갈색/금색 계열 (파랑 배경, 흰 피부 제외)
    w = np.clip((sat - 0.30) / 0.18, 0, 1) * np.clip((235 - L) / 50, 0, 1) * brownish
    # 어두운 갈색은 거의 검정으로, 밝은 금빛 하이라이트는 푸른 회색으로
    target_L = np.clip(L * 0.42 + 6, 0, 255)
    tgt = np.stack([target_L * 0.92, target_L * 0.97, target_L * 1.12 + 6], -1)
    out = crop * (1 - w[..., None]) + tgt * w[..., None]
    cover_s.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), (x0, y0))
    return (w > 0.5)


def do_youth(base, cover_s, photo):
    region = (118, 130, 262, 252)
    recolor_hair_black(cover_s, region)
    # base 에도 같은 머리색 적용
    base.paste(cover_s.crop(tuple(int(v * S) for v in region)), tuple(int(v * S) for v in region[:2]))
    pal = _palette_from(cover_s, YO_CARTOON_FACE, 150)
    s = 0.95
    tx, ty = 190 - s * 98, 241 - s * 87.3      # 눈 높이를 웹툰 눈 높이(241)에 맞춘다

    def keep(cart, org):  # 위쪽 웹툰 머리(검게 바뀐 부분)는 얼굴 위로 겹친다
        h, w = cart.shape[:2]
        yy = (np.arange(h)[:, None] + org[1]) / S
        band = np.clip((233.0 - yy) / 6.0, 0, 1) * np.ones((1, w))
        hair = ((lum(cart) < 110) | ((cart[..., 2] > cart[..., 0] * 1.0) & (lum(cart) < 150))) * band
        return np.asarray(Image.fromarray((hair * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)), np.float32) / 255.0

    place_face(base, cover_s, photo, YO_FACE, s, tx, ty, pal, (62, 36, 30), keep_fn=keep, pal_mix=0.72, bands=4,
               line_C=12.0, shade_mix=0.3, line_gain=1.0,
               eye_boost=[(79, 87.5, 17, 9), (123, 88, 17, 9), (101, 120, 14, 8), (101, 135, 22, 8)])


def build_cover():
    cover = Image.open(os.path.join(SRC, 'cover_original.png')).convert('RGB')
    gp = Image.open(os.path.join(SRC, 'photo_grandpa.png')).convert('RGB')
    yo = Image.open(os.path.join(SRC, 'photo_youth.png')).convert('RGB')
    cover_s = cover.resize((cover.width * S, cover.height * S), Image.LANCZOS)
    base = cover_s.copy()
    do_youth(base, cover_s, yo)      # 청년을 먼저 (머리색 영역 붙여넣기가 할아버지 영역과 겹침)
    do_grandpa(base, cover_s, gp)
    return base


if __name__ == '__main__':
    DEBUG = True
    ensure_out()
    im = build_cover()
    im.save(os.path.join(OUT, 'cover_preview_big.png'))
    im.crop((0, 90, 140 * S, 190 * S)).save(os.path.join(OUT, 'cover_prev_grandpa.png'))
    im.crop((110 * S, 130 * S, 270 * S, 340 * S)).save(os.path.join(OUT, 'cover_prev_youth.png'))
    print('ok', im.size)
