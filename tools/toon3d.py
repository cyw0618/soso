# -*- coding: utf-8 -*-
"""3D 모델 렌더(색/음영/법선 3패스)를 깔끔한 웹툰풍 그림으로 바꾼다.

입력: assets_src/3d/<이름>_{albedo,shade,normal}.png  (three.js 로 렌더한 RGBA)
출력: 웹툰풍 RGBA 머리 이미지 (배경 투명)

원칙: 명암은 최소한(피부는 거의 한 톤 + 옅은 그늘 한 단계)으로, 선은 눈/코/입/귀/주름 위주로만.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_common import *
from face_toon import bilateral, gaussian, lum, ramp, median_rgb


def _load(name):
    d = os.path.join(SRC, '3d')
    return {k: Image.open(os.path.join(d, '%s_%s.png' % (name, k))).convert('RGBA') for k in ('albedo', 'shade', 'normal')}


def _poly_mask(size, pts):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.asarray(m, np.float32) / 255.0


def _cropped(name, work_h):
    p = _load(name)
    bbox = p['albedo'].getchannel('A').getbbox()
    m = 6
    box = (max(0, bbox[0] - m), max(0, bbox[1] - m), min(p['albedo'].width, bbox[2] + m), min(p['albedo'].height, bbox[3] + m))
    crop = {k: v.crop(box) for k, v in p.items()}
    sc = work_h / (box[3] - box[1])
    size = (int((box[2] - box[0]) * sc), work_h)
    return {k: v.resize(size, Image.LANCZOS) for k, v in crop.items()}, size


def debug_grid(name, work_h=640):
    """albedo 위에 0~1 비율 격자를 그려 다각형 좌표를 읽기 쉽게."""
    crop, size = _cropped(name, work_h)
    im = Image.new('RGB', size, (90, 100, 140))
    im.paste(crop['albedo'], (0, 0), crop['albedo'])
    d = ImageDraw.Draw(im)
    for i in range(0, 11):
        x = int(size[0] * i / 10)
        y = int(size[1] * i / 10)
        d.line([(x, 0), (x, size[1])], fill=(255, 255, 0), width=1)
        d.line([(0, y), (size[0], y)], fill=(255, 255, 0), width=1)
        d.text((x + 2, 2), '%.1f' % (i / 10), fill=(255, 255, 0))
        d.text((2, y + 2), '%.1f' % (i / 10), fill=(255, 255, 0))
    return im


def toon_head(name, work_h=640, skin_pal=None, shadow=0.90, shadow_tint=(0.94, 0.90, 0.98), outline=(74, 44, 54),
              line_gain=1.0, hair_pal=None, hair_levels=2, cloth_polys=(), skin_flat=0.55, crease_thr=0.30,
              feature_C=10.0):
    crop, size = _cropped(name, work_h)
    A = np.asarray(crop['albedo'], np.float32)
    Sd = np.asarray(crop['shade'], np.float32)
    Nm = np.asarray(crop['normal'], np.float32)
    al_b = (A[..., 3] > 128).astype(np.float32)
    rgb = A[..., :3].copy()
    W_, H_ = size
    for poly in cloth_polys:                                    # 옷 제거 (비율 좌표 다각형)
        al_b = al_b * (1 - _poly_mask(size, [(x * W_, y * H_) for x, y in poly]))
    rgb[al_b < 0.5] = np.array([200, 170, 150], np.float32)
    sm = rgb
    for _ in range(3):
        sm = bilateral(sm, radius=5, sigma_s=3.5, sigma_r=30.0)
    sm = median_rgb(sm, 7)
    L = lum(sm)
    hair_w = np.clip((72 - gaussian(L, 1.5)) / 26.0, 0, 1)
    flat = np.stack([gaussian(sm[..., c], 9.0) for c in range(3)], -1)
    skin_col = sm * (1 - skin_flat) + flat * skin_flat
    # 음영: 옅은 그늘 한 단계
    sl = gaussian(lum(Sd[..., :3]), 2.2) / 255.0
    inside = al_b > 0.5
    lo, hi = np.percentile(sl[inside], [3, 97])
    t = np.clip((sl - lo) / max(hi - lo, 1e-3), 0, 1)
    shade_amt = np.clip((0.40 - t) / 0.14, 0, 1)
    shade_amt = gaussian(shade_amt * 255, 1.6) / 255.0
    tint = np.array(shadow_tint, np.float32)
    mult = 1.0 - shade_amt[..., None] * (1.0 - tint[None, None, :] * shadow)
    colored = skin_col * mult
    if skin_pal is not None:                                    # 장면 색감에 살짝 맞춤
        mid = np.array(skin_pal, np.float32)
        ref = colored[inside & (hair_w < 0.2)]
        gain = mid / np.maximum(np.percentile(ref, 55, axis=0), 1)
        colored = colored * (1 + (gain[None, None, :] - 1) * 0.5)
    # 머리카락: 거의 검정 + 옅은 푸른 하이라이트
    hair_pal = hair_pal or [(0.0, (22, 22, 32)), (1.0, (92, 100, 132))]
    hl = np.clip((t - 0.52) / 0.30, 0, 1)
    hl = np.round(hl * hair_levels) / hair_levels
    hair_rgb = ramp(hair_pal, hl)
    colored = colored * (1 - hair_w[..., None]) + hair_rgb * hair_w[..., None]
    # 선
    N = [gaussian(Nm[..., c], 1.1) for c in range(3)]
    mag = sum(np.abs(np.gradient(n, axis=1)) + np.abs(np.gradient(n, axis=0)) for n in N) / 255.0
    crease = np.clip((mag - crease_thr * 0.25) / 0.12, 0, 1)
    crease = (gaussian(crease * 255, 0.8) / 255.0 > 0.5).astype(np.float32)
    Lg = lum(median_rgb(rgb, 3))
    dark = np.clip((gaussian(Lg, 5.0) - gaussian(Lg, 1.4) - feature_C) / 12.0, 0, 1)
    dark = np.clip((gaussian(dark * 255, 0.9) / 255.0 - 0.25) * 2.6, 0, 1)
    er = Image.fromarray((al_b * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))
    sil = np.clip(al_b - np.asarray(er, np.float32) / 255.0, 0, 1)
    line_a = np.maximum(np.maximum(crease * 0.7 * (1 - 0.65 * hair_w), dark * 0.95), sil) * line_gain
    line_a = np.clip(gaussian(line_a * 255, 0.6) / 255.0, 0, 1)
    out_rgb = colored * (1 - line_a[..., None]) + np.array(outline, np.float32) * line_a[..., None]
    a8 = gaussian(al_b * 255, 0.8).astype(np.uint8)
    return Image.fromarray(np.dstack([np.clip(out_rgb, 0, 255).astype(np.uint8), a8]), 'RGBA')


if __name__ == '__main__':
    ensure_out()
    for n in ('gpA', 'meB'):
        debug_grid(n).save(os.path.join(OUT, 'grid_%s.png' % n))
        toon_head(n).save(os.path.join(OUT, 'toon_%s.png' % n))
    print('ok')
