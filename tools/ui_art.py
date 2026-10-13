# -*- coding: utf-8 -*-
"""UI 그림 생성: 버튼, 패널, 단계별 막대, 인물 초상. 모두 2배 해상도(pic_scale=0.5)로 만든다."""
import hashlib
from art_common import *

STYLES = {
    'orange': ((255, 196, 80), (240, 112, 30), (130, 52, 10)),
    'blue': ((120, 196, 255), (44, 104, 224), (16, 42, 114)),
    'purple': ((196, 156, 255), (112, 72, 224), (52, 26, 114)),
    'green': ((140, 230, 140), (40, 164, 74), (14, 84, 32)),
    'red': ((255, 140, 140), (224, 54, 64), (112, 16, 26)),
    'gray': ((206, 210, 220), (122, 130, 148), (52, 58, 72)),
    'gold': ((255, 238, 150), (242, 188, 44), (124, 82, 6)),
    'navy': ((92, 108, 168), (36, 48, 104), (14, 20, 56)),
}

_cache = {}


def _key(*a):
    return hashlib.md5(repr(a).encode('utf-8')).hexdigest()[:10]


def ui_button(text, w, h, style='orange', fsize=None, txt=(255, 255, 255), fontname='black'):
    """w, h 는 무대 좌표(픽셀) 크기. 파일은 2배 해상도."""
    k = _key('btn', text, w, h, style, fsize, txt, fontname)
    path = os.path.join(ensure_out(), 'ui_btn_%s.png' % k)
    if os.path.exists(path):
        return path
    top, bottom, edge = STYLES[style]
    SS = 4
    W, H = w * 2 * SS, h * 2 * SS
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(min(W, H) * 0.28)
    pad = 3 * SS
    d.rounded_rectangle((pad, pad + 5 * SS, W - pad, H - pad + 2 * SS), r, fill=(0, 0, 0, 80))
    grad = vgradient((W, H), top, bottom)
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle((pad, pad, W - pad, H - pad - 3 * SS), r, fill=255)
    im.paste(grad, (0, 0), m)
    d.rounded_rectangle((pad, pad, W - pad, H - pad - 3 * SS), r, outline=edge, width=int(2.2 * SS))
    d.rounded_rectangle((pad + 10 * SS, pad + 4 * SS, W - pad - 10 * SS, H // 2 - 2 * SS), r // 2, fill=(255, 255, 255, 60))
    fs = (fsize or int(h * 0.52)) * 2 * SS
    f = font(fontname, fs)
    lines = text.split('\n')
    while True:
        tw = max(text_size(d, ln, f)[0] for ln in lines)
        if tw <= W - 28 * SS or fs <= 16:
            break
        fs = int(fs * 0.92)
        f = font(fontname, fs)
    cy = (H - 3 * SS) / 2
    lh = fs * 1.12
    for i, ln in enumerate(lines):
        y = cy + (i - (len(lines) - 1) / 2) * lh
        d.text((W / 2, y), ln, font=f, fill=txt, anchor='mm', stroke_width=int(1.6 * SS), stroke_fill=edge)
    im = im.resize((w * 2, h * 2), Image.LANCZOS)
    im.save(path, optimize=True)
    return path


def ui_panel(w, h, fill=(12, 20, 46, 222), edge=(255, 226, 120, 255), r=16, name='panel'):
    k = _key('panel', w, h, fill, edge, r)
    path = os.path.join(ensure_out(), 'ui_%s_%s.png' % (name, k))
    if os.path.exists(path):
        return path
    SS = 3
    W, H = w * 2 * SS, h * 2 * SS
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4 * SS, 6 * SS, W - 4 * SS, H - 2 * SS), r * 2 * SS // 2, fill=(0, 0, 0, 70))
    d.rounded_rectangle((2 * SS, 2 * SS, W - 2 * SS, H - 6 * SS), r * 2 * SS // 2, fill=fill, outline=edge, width=int(1.6 * SS * 2))
    im = im.resize((w * 2, h * 2), Image.LANCZOS)
    im.save(path, optimize=True)
    return path


def ui_plain(w, h, fill, name='plain'):
    k = _key('plain', w, h, fill)
    path = os.path.join(ensure_out(), 'ui_%s_%s.png' % (name, k))
    if not os.path.exists(path):
        Image.new('RGBA', (w * 2, h * 2), fill).save(path, optimize=True)
    return path


def ui_bar_set(colname, w, h, top, bottom, steps=41, back=(28, 36, 64, 255)):
    """0~100% 를 steps 단계로 나눈 막대 그림 세트. 반환: [(모양이름, 경로)]"""
    out = []
    SS = 3
    for i in range(steps):
        k = _key('bar', colname, w, h, top, bottom, steps, back, i)
        path = os.path.join(ensure_out(), 'ui_bar_%s_%02d.png' % (colname, i))
        if not os.path.exists(path):
            W, H = w * 2 * SS, h * 2 * SS
            im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            r = H // 2
            d.rounded_rectangle((0, 0, W - 1, H - 1), r, fill=back, outline=(255, 255, 255, 200), width=SS * 2)
            frac = i / (steps - 1)
            if frac > 0:
                fw = max(H - 2 * SS * 2, int((W - 4 * SS) * frac))
                grad = vgradient((fw, H - 6 * SS), top, bottom).convert('RGBA')
                m = Image.new('L', grad.size, 0)
                ImageDraw.Draw(m).rounded_rectangle((0, 0, fw - 1, grad.height - 1), (H - 6 * SS) // 2, fill=255)
                im.paste(grad, (2 * SS, 3 * SS), m)
                d.rounded_rectangle((2 * SS + 8 * SS, 3 * SS + 2 * SS, 2 * SS + fw - 8 * SS, 3 * SS + (H - 6 * SS) // 2 - SS), r // 3, fill=(255, 255, 255, 60)) if fw > 24 * SS else None
            im = im.resize((w * 2, h * 2), Image.LANCZOS)
            im.save(path, optimize=True)
        out.append(('%02d' % i, path))
    return out


def ui_round_icon(text, size, fill=(255, 210, 70), edge=(120, 70, 10), fg=(90, 40, 0), fsize=None, name='icon'):
    k = _key('icon', text, size, fill, edge, fg, fsize)
    path = os.path.join(ensure_out(), 'ui_%s_%s.png' % (name, k))
    if os.path.exists(path):
        return path
    SS = 4
    W = size * 2 * SS
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4 * SS, 8 * SS, W - 4 * SS, W - 0), fill=(0, 0, 0, 80))
    d.ellipse((2 * SS, 2 * SS, W - 2 * SS, W - 6 * SS), fill=fill, outline=edge, width=3 * SS)
    f = font('black', (fsize or int(size * 0.8)) * 2 * SS)
    d.text((W / 2, (W - 4 * SS) / 2), text, font=f, fill=fg, anchor='mm')
    im = im.resize((size * 2, size * 2), Image.LANCZOS)
    im.save(path, optimize=True)
    return path


# ---------------------------------------------------------------- 인물 초상
def portraits(cover_big):
    """cover_big: 얼굴 합성이 끝난 표지(S=3배). 인물별 초상 PNG 를 만든다."""
    S = 3
    boxes = {
        'me': (116, 132, 256, 318),
        'gp': (0, 14, 136, 178),
        'u1': (8, 196, 124, 336),
        'u2': (212, 160, 342, 296),
    }
    out = {}
    for k, b in boxes.items():
        crop = cover_big.crop(tuple(v * S for v in b)).convert('RGBA')
        w, h = crop.size
        side = max(w, h)
        sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        sq.paste(crop, ((side - w) // 2, (side - h) // 2))
        SSZ = 192
        sq = sq.resize((SSZ, SSZ), Image.LANCZOS)
        mask = Image.new('L', (SSZ * 4, SSZ * 4), 0)
        ImageDraw.Draw(mask).rounded_rectangle((8, 8, SSZ * 4 - 8, SSZ * 4 - 8), SSZ * 4 // 6, fill=255)
        mask = mask.resize((SSZ, SSZ), Image.LANCZOS)
        frame = Image.new('RGBA', (SSZ, SSZ), (0, 0, 0, 0))
        frame.paste(sq, (0, 0), mask)
        fr = Image.new('RGBA', (SSZ * 4, SSZ * 4), (0, 0, 0, 0))
        ImageDraw.Draw(fr).rounded_rectangle((8, 8, SSZ * 4 - 8, SSZ * 4 - 8), SSZ * 4 // 6, outline=(255, 226, 120, 255), width=22)
        fr = fr.resize((SSZ, SSZ), Image.LANCZOS)
        frame = Image.alpha_composite(frame, fr)
        p = os.path.join(ensure_out(), 'portrait_%s.png' % k)
        frame.save(p, optimize=True)
        out[k] = p
    return out
