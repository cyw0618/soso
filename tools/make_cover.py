# -*- coding: utf-8 -*-
"""표지 합성: 어르신(사진1/3D) → 뒤쪽 할아버지, 청년(사진3/3D) → 가운데 청년.

3D 모델(GLB)에서 표지 각도로 렌더한 머리를 웹툰풍(옅은 셀 셰이딩 + 선)으로 바꿔서
웹툰 속 인물의 머리 자리에 맞춘다. 원래 웹툰 머리(머리카락/귀/테두리)는 모두 지우고
주변 배경으로 메운 뒤 새 머리를 얹는다.
  - 3D 렌더 입력: assets_src/3d/{gpA,meB}_{albedo,shade,normal}.png
    (tools/assets_src/3d/pass3.js 로 GLB 를 three.js 로 렌더한 결과)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_common import *
import toon3d
from face_toon import S, lum

GP_CLOTH = [[(0, 0.69), (0.30, 0.69), (0.318, 0.70), (0.52, 1.0), (0, 1.0)]]
ME_CLOTH = [[(0, 0.66), (0.265, 0.66), (0.29, 0.74), (0.34, 0.86), (0.42, 0.97), (0.47, 1.0), (0, 1.0)],
            [(0.80, 0.80), (1.0, 0.80), (1.0, 1.0), (0.78, 1.0)],
            [(0.18, 0.62), (0.28, 0.62), (0.34, 0.82), (0.18, 0.82)]]

# 표지 원본 좌표에서 새 머리가 들어갈 자리(머리카락 윗끝~턱, 좌~우)
GP_TARGET = (0, 8, 133, 173)
ME_TARGET = (126, 138, 254, 312)

# 원래 웹툰 머리가 차지하던 영역 (지워서 배경으로 메울 곳)
GP_OLD = [(0, 0), (134, 0), (137, 64), (135, 112), (131, 140), (125, 162), (113, 177), (92, 180), (70, 175),
          (52, 161), (36, 153), (0, 153)]
ME_OLD = [(180, 130), (152, 136), (133, 156), (123, 188), (120, 218), (124, 232), (120, 240), (132, 256), (140, 268),
          (150, 284), (158, 298), (172, 308), (190, 314), (208, 310), (224, 298), (234, 280), (240, 262), (246, 250),
          (252, 236), (258, 214), (260, 190), (256, 170), (246, 148), (228, 136), (206, 130)]


def _pool2(a):
    h, w = a.shape[:2]
    a = a[:h - h % 2, :w - w % 2]
    return (a[0::2, 0::2] + a[1::2, 0::2] + a[0::2, 1::2] + a[1::2, 1::2]) / 4.0


def _up(a, shape):
    h, w = shape
    chans = []
    for c in range(a.shape[2]):
        im = Image.fromarray(a[..., c].astype(np.float32), mode='F').resize((w, h), Image.BICUBIC)
        chans.append(np.asarray(im, np.float32))
    return np.stack(chans, -1)


def push_pull(img, known, levels=7):
    """known=False 인 픽셀을 주변(known) 색으로 부드럽게 메운다 (푸시-풀 인페인팅)."""
    w0 = known.astype(np.float32)
    v0 = img * w0[..., None]
    vs, ws = [v0], [w0]
    for _ in range(levels):
        vs.append(_pool2(vs[-1]))
        ws.append(_pool2(ws[-1]))
    fill = None
    for lvl in range(levels, -1, -1):
        v, w = vs[lvl], ws[lvl]
        if fill is None:   # 가장 거친 단계: 비어 있는 칸은 알려진 픽셀 전체 평균색으로
            gmean = (img * w0[..., None]).sum((0, 1)) / max(w0.sum(), 1e-4)
            cur = np.where(w[..., None] > 1e-4, v / np.maximum(w[..., None], 1e-4), gmean[None, None, :])
        else:
            cur = np.where(w[..., None] > 1e-4, v / np.maximum(w[..., None], 1e-4), 0.0)
        if fill is not None:
            up = _up(fill, v.shape[:2])
            conf = np.clip(w[..., None] * 2.0, 0, 1)
            cur = cur * conf + up * (1 - conf)
        fill = cur
    return np.where(known[..., None], img, fill)


def erase_region(base_rgb, poly, pad=24, margin=3):
    """base_rgb(S배 RGB 이미지)에서 poly(표지 원본 좌표) 영역을 지우고 주변 색으로 메운다."""
    arr = np.asarray(base_rgb, np.float32)
    H, W = arr.shape[:2]
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in poly], fill=255)
    m = m.filter(ImageFilter.MaxFilter(margin * 2 + 1))
    hole = np.asarray(m, np.float32) > 127
    # 이미지 가장자리 바깥은 어두운 남색 배경으로 가정해 known 으로 추가
    bg = np.array([26, 36, 82], np.float32)
    big = np.zeros((H + pad, W + pad, 3), np.float32)
    big[:] = bg
    big[pad:, pad:] = arr
    bk = np.ones((H + pad, W + pad), bool)
    bk[pad:, pad:] = ~hole
    out = push_pull(big, bk)[pad:, pad:]
    # 메운 곳은 약간 흐리게 (배경의 부드러운 느낌)
    blurred = np.asarray(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)), np.float32)
    soft = np.asarray(Image.fromarray((hole * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5)), np.float32) / 255.0
    res = arr * (1 - soft[..., None]) + blurred * soft[..., None]
    return Image.fromarray(np.clip(res, 0, 255).astype(np.uint8))


def _fit(layer, target):
    """layer(RGBA) 의 불투명 영역 bbox 를 target(표지 원본 좌표 x0,y0,x1,y1) 안에 맞춰 S배로 변환."""
    bb = layer.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    crop = layer.crop(bb)
    tw, th = (target[2] - target[0]) * S, (target[3] - target[1]) * S
    sc = min(tw / crop.width, th / crop.height)
    nw, nh = int(crop.width * sc), int(crop.height * sc)
    crop = crop.resize((nw, nh), Image.LANCZOS)
    return crop, int(target[2] * S - nw), int(target[3] * S - nh)


def _fade_bottom(layer, frac=0.07):
    """머리 아래쪽(목)을 부드럽게 투명하게 해서 웹툰 옷깃에 자연스럽게 이어 붙인다."""
    a = np.asarray(layer.getchannel('A'), np.float32)
    h = a.shape[0]
    n = max(2, int(h * frac))
    ramp_ = np.ones(h, np.float32)
    ramp_[h - n:] = np.linspace(1, 0, n)
    a = a * ramp_[:, None]
    out = layer.copy()
    out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out


def _rim(layer_pos, color, spread=4, alpha=170):
    crop, x, y = layer_pos
    a = crop.getchannel('A')
    pad = spread * 4
    big = Image.new('L', (crop.width + 2 * pad, crop.height + 2 * pad), 0)
    big.paste(a, (pad, pad))
    glow = big.filter(ImageFilter.MaxFilter(spread * 2 + 1)).filter(ImageFilter.GaussianBlur(spread * 0.7))
    glow = glow.point(lambda v: int(v * alpha / 255))
    col = Image.new('RGBA', big.size, color + (255,))
    col.putalpha(glow)
    return col, x - pad, y - pad


# ------------------------------------------------------------------ 제목 글자 교체 ("재벌집" → "군수집")
TITLE_BOX = (250, 1070, 840, 1300)     # S배 좌표: 윗줄 글자가 있는 영역


def swap_title(rgb_img, new_text='군수집'):
    arr = np.asarray(rgb_img, np.float32)
    x0, y0, x1, y1 = TITLE_BOX
    sub = arr[y0:y1, x0:x1]
    L = lum(sub)
    text = (L > 175) & (sub[..., 2] > sub[..., 0] + 8)
    text[:int((1096 - y0) - 14)] = False                      # 위쪽 셔츠/손은 제외
    ys, xs = np.where(text)
    tb = (xs.min(), ys.min(), xs.max(), ys.max())             # 글자 bbox (sub 좌표)
    # 색 샘플: 글자 채움색(위/아래), 외곽선색
    fill_top = np.median(sub[(text) & (np.arange(sub.shape[0])[:, None] < tb[1] + (tb[3] - tb[1]) * 0.35)], 0)
    fill_bot = np.median(sub[(text) & (np.arange(sub.shape[0])[:, None] > tb[1] + (tb[3] - tb[1]) * 0.65)], 0)
    tm = Image.fromarray((text * 255).astype(np.uint8))
    ring = np.asarray(tm.filter(ImageFilter.MaxFilter(9)), np.float32) > 127
    ring &= ~text
    outline_col = np.array([26, 40, 98], np.float32)
    # 1) 지우기: 글자+외곽선+번짐을 크게 키워 구멍으로
    hole = np.asarray(tm.filter(ImageFilter.MaxFilter(17)), np.float32) > 127
    crop_arr = sub.copy()
    filled = push_pull(crop_arr, ~hole, levels=6)
    filled = np.asarray(Image.fromarray(np.clip(filled, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32)
    soft = np.asarray(Image.fromarray((hole * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.0)), np.float32) / 255.0
    sub2 = crop_arr * (1 - soft[..., None]) + filled * soft[..., None]
    out = arr.copy()
    out[y0:y1, x0:x1] = sub2
    base = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert('RGBA')
    # 2) 새 글자: 원래 글자 bbox 에 꽉 차게
    tw, th = tb[2] - tb[0] + 1, tb[3] - tb[1] + 1
    fs = 220
    while True:
        f = font('black', fs)
        d0 = ImageDraw.Draw(Image.new('L', (10, 10)))
        glyph_w = [d0.textbbox((0, 0), ch, font=f) for ch in new_text]
        gh = max(b[3] - b[1] for b in glyph_w)
        if gh <= th * 1.0 or fs < 60:
            break
        fs -= 4
    f = font('black', fs)
    widths = [b[2] - b[0] for b in glyph_w]
    gap = (tw - sum(widths)) / max(1, len(new_text) - 1)
    pad = 40
    mask_img = Image.new('L', (tw + 2 * pad, th + 2 * pad), 0)
    md = ImageDraw.Draw(mask_img)
    xcur = pad
    top_ref = min(b[1] for b in glyph_w)
    for ch, b, w in zip(new_text, glyph_w, widths):
        md.text((xcur - b[0], pad + (th - gh) / 2 - top_ref + (b[1] - top_ref) * 0 - 0), ch, font=f, fill=255)
        xcur += w + gap
    grad = vgradient(mask_img.size, tuple(int(v) for v in fill_top), tuple(int(v) for v in fill_bot)).convert('RGBA')
    outline = mask_img.filter(ImageFilter.MaxFilter(15))
    glow = mask_img.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.GaussianBlur(7))
    layer = Image.new('RGBA', mask_img.size, (0, 0, 0, 0))
    glow_col = Image.new('RGBA', mask_img.size, (150, 205, 255, 255))
    glow_col.putalpha(glow.point(lambda v: int(v * 0.55)))
    layer.alpha_composite(glow_col)
    oc = Image.new('RGBA', mask_img.size, tuple(int(v) for v in outline_col) + (255,))
    oc.putalpha(outline)
    layer.alpha_composite(oc)
    gl = grad.copy()
    gl.putalpha(mask_img)
    layer.alpha_composite(gl)
    base.alpha_composite(layer, (x0 + tb[0] - pad, y0 + tb[1] - pad))
    return base.convert('RGB')


def build_cover():
    cover = Image.open(os.path.join(SRC, 'cover_original.png')).convert('RGB')
    rgb = cover.resize((cover.width * S, cover.height * S), Image.LANCZOS)
    # 1) 원래 머리 지우기
    rgb = erase_region(rgb, GP_OLD)
    rgb = erase_region(rgb, ME_OLD)
    base = rgb.convert('RGBA')
    # 2) 3D 머리 → 웹툰풍
    pg = (214, 176, 186)    # 할아버지 쪽 장면 조명(보랏빛)에 맞춘 피부색
    py = (236, 196, 166)    # 청년 피부색
    gp = toon3d.toon_head('gpA', skin_pal=pg, cloth_polys=GP_CLOTH, shadow_tint=(0.90, 0.84, 0.96))
    me = toon3d.toon_head('meB', skin_pal=py, cloth_polys=ME_CLOTH, shadow=0.85)
    gp_pos = _fit(gp, GP_TARGET)
    gp_pos = (_fade_bottom(gp_pos[0], 0.08), gp_pos[1], gp_pos[2])
    me_pos = _fit(me, ME_TARGET)
    # 3) 청년: 푸른 테두리 빛 → 머리,  할아버지 → 머리
    rim = _rim(me_pos, (80, 180, 255))
    base.alpha_composite(rim[0], (max(0, rim[1]), max(0, rim[2])))
    base.alpha_composite(gp_pos[0], (gp_pos[1], gp_pos[2]))
    base.alpha_composite(me_pos[0], (me_pos[1], me_pos[2]))
    return swap_title(base.convert('RGB'))


if __name__ == '__main__':
    ensure_out()
    im = build_cover()
    im.save(os.path.join(OUT, 'cover_preview_big.png'))
    print('ok', im.size)
