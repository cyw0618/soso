# -*- coding: utf-8 -*-
"""사진 얼굴을 웹툰 그림체로 바꿔 표지 그림에 넣는다 (numpy + PIL 만 사용).

- 사진은 '균일 배율'로만 키우고 이동한다 (이목구비 비율, 얼굴형은 본인 그대로).
- 양방향 평활 + 색 단계화 + 어두운 디테일 선(눈, 코, 입, 주름)으로 웹툰 느낌을 낸다.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 3  # 작업 배율 (원본 표지 1px = 작업 3px)


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def gaussian(arr2d, r):
    im = Image.fromarray(np.clip(arr2d, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32)


def median_rgb(arr, size):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.MedianFilter(size)), np.float32)


def bilateral(img, radius=4, sigma_s=3.0, sigma_r=28.0, step=1):
    """간단한 양방향 필터(벡터화). img: HxWx3 float."""
    h, w = img.shape[:2]
    pad = np.pad(img, ((radius, radius), (radius, radius), (0, 0)), mode='edge')
    acc = np.zeros_like(img)
    wsum = np.zeros((h, w, 1), np.float32)
    for dy in range(-radius, radius + 1, step):
        for dx in range(-radius, radius + 1, step):
            ws = np.exp(-(dx * dx + dy * dy) / (2 * sigma_s ** 2))
            sh = pad[radius + dy:radius + dy + h, radius + dx:radius + dx + w]
            diff = ((sh - img) ** 2).sum(-1, keepdims=True)
            wr = np.exp(-diff / (2 * (sigma_r ** 2) * 3)) * ws
            acc += sh * wr
            wsum += wr
    return acc / np.maximum(wsum, 1e-6)


def ramp(colors, t):
    ts = np.array([c[0] for c in colors], np.float32)
    cs = np.array([c[1] for c in colors], np.float32)
    out = np.zeros(t.shape + (3,), np.float32)
    for ch in range(3):
        out[..., ch] = np.interp(t, ts, cs[:, ch])
    return out


def toon_photo(photo_rgb, palette, line_col, pal_mix=0.55, bands=5, line_C=7.0, line_blur=(1.2, 4.5),
               skin_mask=None, shade=None, shade_mix=0.0, hair=None):
    """photo_rgb: HxWx3 float (이미 작업 배율로 키운 사진). palette: [(t, rgb)] 어두움→밝음.
    반환 (rgb, line_alpha)."""
    sm = photo_rgb
    for _ in range(3):
        sm = bilateral(sm, radius=4, sigma_s=2.5, sigma_r=30.0)
    sm = median_rgb(sm, 5)
    L = lum(sm)
    ref = L if skin_mask is None else L[skin_mask > 0.5]
    lo, hi = np.percentile(ref, [5, 95])
    t = np.clip((L - lo) / max(hi - lo, 1), 0, 1)
    if shade is not None and shade_mix > 0:
        t = (1 - shade_mix) * t + shade_mix * shade
    q = np.round(t * (bands - 1)) / (bands - 1)
    q = gaussian(q * 255, 1.8) / 255.0
    cel = ramp(palette, q)
    # 사진 고유의 색감 일부를 남겨 닮게 한다 (피부톤/입술색)
    photo_q = np.asarray(Image.fromarray(np.clip(sm, 0, 255).astype(np.uint8)).quantize(
        colors=24, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB'), np.float32)
    rgb = cel * pal_mix + photo_q * (1 - pal_mix)
    if hair is not None:      # hair=(임계 밝기, 위쪽 한계 행, 색): 사진의 어두운 앞머리를 선명한 검은 머리로
        thr, row_max, hcol = hair
        rows = (np.arange(L.shape[0])[:, None] < row_max).astype(np.float32) * np.ones((1, L.shape[1]), np.float32)
        hw = np.clip((thr - gaussian(L, 1.0)) / 18.0, 0, 1) * rows
        hw = gaussian(hw * 255, 1.3) / 255.0
        rgb = rgb * (1 - hw[..., None]) + np.array(hcol, np.float32) * hw[..., None]
    # 선: 국소적으로 어두운 부분(눈, 눈썹, 콧구멍, 입, 주름)
    Lg = lum(median_rgb(photo_rgb, 3))
    fine = gaussian(Lg, line_blur[0])
    coarse = gaussian(Lg, line_blur[1])
    dark = np.clip((coarse - fine - line_C) / 10.0, 0, 1)
    dark_img = Image.fromarray((dark * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))
    dark = np.clip((np.asarray(dark_img, np.float32) / 255.0 - 0.28) * 2.8, 0, 1)
    return rgb, dark


def dark_lines(photo_rgb, C, blur=(1.2, 4.5)):
    Lg = lum(median_rgb(photo_rgb, 3))
    fine = gaussian(Lg, blur[0])
    coarse = gaussian(Lg, blur[1])
    dark = np.clip((coarse - fine - C) / 10.0, 0, 1)
    img = Image.fromarray((dark * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))
    return np.clip((np.asarray(img, np.float32) / 255.0 - 0.28) * 2.8, 0, 1)


def ellipse_layer(shape_hw, ellipses_px, feather=6):
    h, w = shape_hw
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    for cx, cy, rx, ry in ellipses_px:
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(feather)), np.float32) / 255.0


def poly_layer(size_wh, pts_px, feather=1.5):
    m = Image.new('L', size_wh, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts_px], fill=255)
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m, np.float32) / 255.0


def place_face(base, cover_s, photo, contour, s, tx, ty, palette, line_col, keep_fn=None, pal_mix=0.55,
               bands=5, line_C=7.0, line_region=None, shade_mix=0.0, outline=None, feather=1.6,
               post_fn=None, line_gain=1.0, hair=None, eye_boost=None):
    """photo: PIL 사진. contour: 사진 좌표 얼굴 윤곽(폴리곤). (s, tx, ty): 사진→표지(원본px) 변환 x'=s*x+tx.
    keep_fn(region_cartoon_rgb)->0..1 : 1이면 웹툰 원본을 남김(머리카락 등)."""
    k = s * S
    pw, ph = photo.size
    big = photo.convert('RGB').resize((max(1, int(pw * k)), max(1, int(ph * k))), Image.LANCZOS)
    arr = np.asarray(big, np.float32)
    mask = poly_layer(big.size, [(x * k, y * k) for x, y in contour], feather=feather)
    ys, xs = np.where(mask > 0.02)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    arr_c = arr[y0:y1, x0:x1]
    m_c = mask[y0:y1, x0:x1]
    shade = None
    ox, oy = int(round(tx * S + x0)), int(round(ty * S + y0))   # 표지(S배) 좌표에서의 위치
    cart = np.asarray(cover_s.crop((ox, oy, ox + (x1 - x0), oy + (y1 - y0))), np.float32)
    if shade_mix > 0:
        Lc = gaussian(lum(cart), 14)
        lo, hi = np.percentile(Lc[m_c > 0.5], [5, 95])
        shade = np.clip((Lc - lo) / max(hi - lo, 1), 0, 1)
    hair_arg = None
    if hair is not None:
        thr, ymax_photo, hcol = hair
        hair_arg = (thr, ymax_photo * k - y0, hcol)
    rgb, dark = toon_photo(arr_c, palette, line_col, pal_mix=pal_mix, bands=bands, line_C=line_C,
                           skin_mask=m_c, shade=shade, shade_mix=shade_mix, hair=hair_arg)
    inner = Image.fromarray((m_c > 0.9).astype(np.uint8) * 255).filter(ImageFilter.MinFilter(15)).filter(ImageFilter.GaussianBlur(5))
    dark = dark * (np.asarray(inner, np.float32) / 255.0)
    if eye_boost is not None:   # [(cx,cy,rx,ry)] 사진 좌표: 눈 주변은 민감하게 다시 추출
        ell = [((cx * k - x0), (cy * k - y0), rx * k, ry * k) for cx, cy, rx, ry in eye_boost]
        em = ellipse_layer(arr_c.shape[:2], ell, feather=5)
        d2 = dark_lines(arr_c, 5.0) * em * (np.asarray(inner, np.float32) / 255.0)
        dark = np.maximum(dark, d2)
    if line_region is not None:
        dark = dark * line_region(arr_c.shape[:2], (x0, y0), k)
    dark = np.clip(dark * line_gain, 0, 1)
    face = rgb * (1 - dark[..., None]) + np.array(line_col, np.float32) * dark[..., None]
    a = m_c.copy()
    if keep_fn is not None:
        a = a * (1 - keep_fn(cart, (ox, oy)))
    if post_fn is not None:
        face = post_fn(face, a, (ox, oy))
    out = cart * (1 - a[..., None]) + face * a[..., None]
    base.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), (ox, oy))
    return (ox, oy, ox + (x1 - x0), oy + (y1 - y0))
