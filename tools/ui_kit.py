# -*- coding: utf-8 -*-
"""게임 UI 키트: 유리 패널, 광택 버튼, 리본 배너, 큰 글자, 배지, 아이콘, 막대, 파티클.

모든 크기는 '무대 픽셀'(480x270 기준)로 받고, 파일은 2배 해상도로 저장한다(pic_scale=0.5).
내부적으로는 SS배 더 크게 그린 뒤 줄여서 가장자리를 매끈하게 한다.
"""
import hashlib
import math
from art_common import *

SS = 3          # 슈퍼샘플링
R2 = 2          # 파일 해상도 배율 (무대 1px = 파일 2px)

GOLD = ((255, 236, 150), (246, 186, 56), (150, 92, 10))
PAL = {
    # (위, 아래, 테두리/외곽선)
    'gold': ((255, 224, 120), (236, 150, 30), (122, 64, 6)),
    'blue': ((110, 196, 255), (34, 98, 222), (12, 36, 110)),
    'cyan': ((140, 240, 255), (30, 170, 230), (8, 70, 110)),
    'purple': ((200, 150, 255), (116, 60, 224), (50, 20, 112)),
    'red': ((255, 132, 132), (222, 40, 60), (110, 10, 24)),
    'pink': ((255, 150, 200), (232, 60, 140), (110, 14, 64)),
    'green': ((150, 240, 150), (34, 170, 84), (10, 84, 34)),
    'gray': ((214, 218, 228), (124, 132, 150), (54, 60, 76)),
    'navy': ((70, 88, 160), (26, 36, 90), (10, 14, 44)),
    'white': ((255, 255, 255), (220, 228, 245), (60, 70, 110)),
}


def _k(*a):
    return hashlib.md5(repr(a).encode('utf-8')).hexdigest()[:10]


def _path(prefix, *a):
    return os.path.join(ensure_out(), '%s_%s.png' % (prefix, _k(prefix, *a)))


def _canvas(w, h):
    return Image.new('RGBA', (int(w * R2 * SS), int(h * R2 * SS)), (0, 0, 0, 0))


def _finish(im, w, h, path):
    im = im.resize((int(w * R2), int(h * R2)), Image.LANCZOS)
    im.save(path, optimize=True)
    return path


def _grad(size, top, bottom, mid=None):
    w, h = size
    g = Image.new('RGBA', size)
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1)
        if mid is not None:
            c = lerp(top, mid, t * 2) if t < 0.5 else lerp(mid, bottom, (t - 0.5) * 2)
        else:
            c = lerp(top, bottom, t)
        d.line([(0, y), (w, y)], fill=tuple(c) + ((255,) if len(c) == 3 else ()))
    return g


def _rr_mask(size, box, r):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255)
    return m


def _shadow(size, box, r, blur, alpha=130, off=(0, 0)):
    m = Image.new('L', size, 0)
    b = (box[0] + off[0], box[1] + off[1], box[2] + off[0], box[3] + off[1])
    ImageDraw.Draw(m).rounded_rectangle(b, r, fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new('RGBA', size, (0, 0, 0, 255))
    sh.putalpha(m)
    return sh


def _words_width(f, ln):
    words = ln.split(' ')
    gap = f.size * 0.28
    return sum(f.getlength(w) for w in words) + gap * (len(words) - 1)


def _draw_line(md, cx, cy, ln, f, fill):
    """띄어쓰기를 직접 처리해서 가운데 정렬로 그린다 (잘난체에는 공백 글리프가 없음)."""
    words = ln.split(' ')
    gap = f.size * 0.28
    x = cx - _words_width(f, ln) / 2
    for w in words:
        md.text((x, cy), w, font=f, fill=fill, anchor='lm')
        x += f.getlength(w) + gap


def _text_layer(size, xy, text, f, fill_top, fill_bottom, outline, ow, anchor='mm', glow=None, glow_r=0,
                shadow=None, spacing=0):
    """그라데이션 글자 + 외곽선 + 글로우 레이어."""
    W, H = size
    mask = Image.new('L', size, 0)
    md = ImageDraw.Draw(mask)
    lines = text.split('\n')
    lh = f.size * 1.18 + spacing
    for i, ln in enumerate(lines):
        y = xy[1] + (i - (len(lines) - 1) / 2) * lh
        _draw_line(md, xy[0], y, ln, f, 255)
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    if glow is not None and glow_r:
        g = mask.filter(ImageFilter.MaxFilter(int(ow * 2) | 1)).filter(ImageFilter.GaussianBlur(glow_r))
        gl = Image.new('RGBA', size, tuple(glow[:3]) + (255,))
        gl.putalpha(g.point(lambda v: int(v * (glow[3] if len(glow) > 3 else 200) / 255)))
        out.alpha_composite(gl)
    if shadow:
        sx, sy, sc = shadow
        sm = mask.filter(ImageFilter.MaxFilter(int(ow * 2) | 1))
        sl = Image.new('RGBA', size, tuple(sc[:3]) + (255,))
        sl.putalpha(sm.point(lambda v: int(v * (sc[3] if len(sc) > 3 else 160) / 255)))
        out.alpha_composite(sl, (int(sx), int(sy)))
    if ow:
        om = mask.filter(ImageFilter.MaxFilter(int(ow * 2) | 1))
        ol = Image.new('RGBA', size, tuple(outline) + (255,))
        ol.putalpha(om)
        out.alpha_composite(ol)
    bb = mask.getbbox() or (0, 0, W, H)
    gr = Image.new('RGBA', size, (0, 0, 0, 0))
    gg = _grad((W, max(1, bb[3] - bb[1])), fill_top, fill_bottom)
    gr.paste(gg, (0, bb[1]))
    gr.putalpha(mask)
    out.alpha_composite(gr)
    # 글자 윗부분 하이라이트
    hl = Image.new('RGBA', size, (255, 255, 255, 0))
    hm = Image.new('L', size, 0)
    hd = ImageDraw.Draw(hm)
    hd.rectangle((0, bb[1], W, bb[1] + (bb[3] - bb[1]) * 0.42), fill=70)
    hm = ImageChops.multiply(hm, mask)
    hl.putalpha(hm)
    out.alpha_composite(hl)
    return out


# ------------------------------------------------------------------ 패널
def panel(w, h, kind='glass', r=12, header=None):
    path = _path('ui_panel', w, h, kind, r, header)
    if os.path.exists(path):
        return path
    im = _canvas(w, h)
    W, H = im.size
    s = R2 * SS
    pad = 5 * s
    box = (pad, pad, W - pad, H - pad - 2 * s)
    rr = r * s
    im.alpha_composite(_shadow(im.size, box, rr, 4 * s, 150, (0, 3 * s)))
    if kind in ('glass', 'glass_cyan', 'alert', 'glass_purple'):
        body = _grad(im.size, (30, 38, 86), (10, 14, 40))
        a = 228
    elif kind == 'card':
        body = _grad(im.size, (44, 56, 112), (20, 26, 64))
        a = 240
    elif kind == 'light':
        body = _grad(im.size, (255, 255, 255), (232, 238, 252))
        a = 250
    else:
        body = _grad(im.size, (16, 20, 46), (6, 8, 24))
        a = 215
    body.putalpha(_rr_mask(im.size, box, rr).point(lambda v: v * a // 255))
    im.alpha_composite(body)
    # 위쪽 유리 반사
    gl = Image.new('RGBA', im.size, (255, 255, 255, 0))
    gm = Image.new('L', im.size, 0)
    ImageDraw.Draw(gm).rounded_rectangle((box[0] + 2 * s, box[1] + 2 * s, box[2] - 2 * s, box[1] + (box[3] - box[1]) * 0.38), rr, fill=26 if kind != 'light' else 0)
    gl.putalpha(gm)
    im.alpha_composite(gl)
    if header:
        hc = PAL[header]
        hb = (box[0], box[1], box[2], box[1] + 22 * s)
        hg = _grad(im.size, hc[0], hc[1])
        hm = _rr_mask(im.size, hb, rr)
        cut = Image.new('L', im.size, 0)
        ImageDraw.Draw(cut).rectangle((box[0], box[1] + 11 * s, box[2], hb[3]), fill=255)
        hm = ImageChops.lighter(hm, ImageChops.multiply(cut, _rr_mask(im.size, box, rr)))
        hg.putalpha(hm)
        im.alpha_composite(hg)
    # 테두리
    d = ImageDraw.Draw(im)
    if kind in ('glass', 'card'):
        border = Image.new('RGBA', im.size, (0, 0, 0, 0))
        bm = Image.new('L', im.size, 0)
        ImageDraw.Draw(bm).rounded_rectangle(box, rr, outline=255, width=int(1.6 * s))
        bg_ = _grad(im.size, GOLD[0], GOLD[2], GOLD[1])
        bg_.putalpha(bm)
        im.alpha_composite(bg_)
    elif kind == 'glass_cyan':
        d.rounded_rectangle(box, rr, outline=(110, 220, 255, 255), width=int(1.6 * s))
    elif kind == 'glass_purple':
        d.rounded_rectangle(box, rr, outline=(190, 140, 255, 255), width=int(1.6 * s))
    elif kind == 'alert':
        glow = Image.new('L', im.size, 0)
        ImageDraw.Draw(glow).rounded_rectangle(box, rr, outline=255, width=int(3 * s))
        glow = glow.filter(ImageFilter.GaussianBlur(3 * s))
        gl = Image.new('RGBA', im.size, (255, 60, 80, 255))
        gl.putalpha(glow)
        im.alpha_composite(gl)
        d.rounded_rectangle(box, rr, outline=(255, 110, 120, 255), width=int(1.6 * s))
    elif kind == 'light':
        d.rounded_rectangle(box, rr, outline=(180, 190, 220, 255), width=int(1 * s))
    # 안쪽 얇은 빛 테두리
    d.rounded_rectangle((box[0] + 2 * s, box[1] + 2 * s, box[2] - 2 * s, box[3] - 2 * s), max(1, rr - 2 * s),
                        outline=(255, 255, 255, 34), width=max(1, int(0.6 * s)))
    return _finish(im, w, h, path)


# ------------------------------------------------------------------ 버튼
def button(text, w, h, color='gold', fsize=None, icon=None, disabled=False):
    path = _path('ui_btn', text, w, h, color, fsize, icon, disabled)
    if os.path.exists(path):
        return path
    top, bottom, edge = PAL['gray' if disabled else color]
    im = _canvas(w, h)
    W, H = im.size
    s = R2 * SS
    pad = 3 * s
    box = (pad, pad, W - pad, H - pad - 3 * s)
    rr = int((box[3] - box[1]) / 2)
    im.alpha_composite(_shadow(im.size, box, rr, 2.5 * s, 150, (0, 3 * s)))
    # 아래 두께(입체)
    base = Image.new('RGBA', im.size, (0, 0, 0, 0))
    bm = _rr_mask(im.size, (box[0], box[1] + 3 * s, box[2], box[3] + 3 * s), rr)
    bl = Image.new('RGBA', im.size, tuple(lerp(edge, bottom, 0.35)) + (255,))
    bl.putalpha(bm)
    im.alpha_composite(bl)
    g = _grad(im.size, top, bottom)
    g.putalpha(_rr_mask(im.size, box, rr))
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    # 광택
    gl = Image.new('RGBA', im.size, (255, 255, 255, 0))
    gm = Image.new('L', im.size, 0)
    ImageDraw.Draw(gm).rounded_rectangle((box[0] + 4 * s, box[1] + 2 * s, box[2] - 4 * s, box[1] + (box[3] - box[1]) * 0.48), rr, fill=95)
    gl.putalpha(gm.filter(ImageFilter.GaussianBlur(1 * s)))
    im.alpha_composite(gl)
    d.rounded_rectangle(box, rr, outline=tuple(edge) + (255,), width=int(1.4 * s))
    d.rounded_rectangle((box[0] + 1.5 * s, box[1] + 1.5 * s, box[2] - 1.5 * s, box[3] - 1.5 * s), rr, outline=(255, 255, 255, 90), width=max(1, int(0.6 * s)))
    fs = int((fsize or (h * 0.46)) * s)
    f = font('jalnan', fs)
    tw = _words_width(f, text)
    avail = (box[2] - box[0]) - 14 * s - (h * 0.8 * s if icon else 0)
    while tw > avail and fs > 8:
        fs = int(fs * 0.92)
        f = font('jalnan', fs)
        tw = _words_width(f, text)
    cx = W / 2 + (h * 0.38 * s if icon else 0)
    cy = (box[1] + box[3]) / 2 + 0.5 * s
    if icon:
        isz = int((box[3] - box[1]) * 0.66)
        ic = Image.open(icon_img(icon, 64)).resize((isz, isz), Image.LANCZOS)
        im.alpha_composite(ic, (int(cx - tw / 2 - isz - 4 * s), int(cy - isz / 2)))
    txt = _text_layer(im.size, (cx, cy), text, f, (255, 255, 255), lerp((255, 255, 255), top, 0.25), edge, 1.5 * s,
                      shadow=(0, 1.5 * s, tuple(edge) + (200,)))
    im.alpha_composite(txt)
    return _finish(im, w, h, path)


# ------------------------------------------------------------------ 큰 글자 (팝업, 판정, 제목)
def big_text(text, fsize, style='gold', w=None, h=None, outline=None, glow=True, fontname='jalnan'):
    styles = {
        'gold': ((255, 250, 210), (255, 176, 40), (90, 36, 0), (255, 200, 80, 170)),
        'white': ((255, 255, 255), (206, 222, 255), (22, 30, 80), (120, 180, 255, 150)),
        'red': ((255, 210, 210), (240, 40, 60), (70, 0, 10), (255, 70, 90, 170)),
        'cyan': ((230, 255, 255), (40, 200, 255), (0, 40, 90), (60, 200, 255, 170)),
        'green': ((230, 255, 220), (60, 210, 90), (0, 60, 20), (90, 255, 120, 160)),
        'pink': ((255, 230, 245), (255, 70, 160), (80, 0, 40), (255, 90, 170, 170)),
        'purple': ((246, 230, 255), (160, 90, 255), (40, 0, 80), (190, 120, 255, 170)),
        'gray': ((240, 240, 245), (150, 156, 170), (30, 34, 46), (160, 160, 170, 120)),
    }
    top, bot, ol, gc = styles[style]
    ol = outline or ol
    path = _path('ui_big', text, fsize, style, w, h, outline, glow, fontname)
    if os.path.exists(path):
        return path
    s = R2 * SS
    f = font(fontname, int(fsize * s))
    tmp = ImageDraw.Draw(Image.new('L', (10, 10)))
    lines = text.split('\n')
    tw = max(_words_width(f, ln) for ln in lines)
    th = int(fsize * s * 1.18 * len(lines))
    W = w * s if w else tw + fsize * s * 0.9
    H = h * s if h else th + fsize * s * 0.9
    im = Image.new('RGBA', (int(W), int(H)), (0, 0, 0, 0))
    lay = _text_layer(im.size, (W / 2, H / 2), text, f, top, bot, ol, max(2, fsize * 0.09) * s,
                      glow=gc if glow else None, glow_r=fsize * 0.18 * s, shadow=(0, fsize * 0.06 * s, ol + (220,)))
    im.alpha_composite(lay)
    ww, hh = im.width / s, im.height / s
    return _finish(im, ww, hh, path)


# ------------------------------------------------------------------ 리본 배너
def banner(text, w, h, color='gold', fsize=None):
    path = _path('ui_banner', text, w, h, color, fsize)
    if os.path.exists(path):
        return path
    top, bottom, edge = PAL[color]
    im = _canvas(w, h)
    W, H = im.size
    s = R2 * SS
    tail = H * 0.42
    fold = H * 0.16
    body = (tail * 0.75, H * 0.12, W - tail * 0.75, H * 0.80)
    d = ImageDraw.Draw(im)
    dark = tuple(lerp(edge, bottom, 0.4)) + (255,)
    for side in (-1, 1):
        if side < 0:
            pts = [(0, H * 0.30), (tail * 1.1, H * 0.30), (tail * 1.1, H * 0.98), (0, H * 0.98), (tail * 0.45, H * 0.64)]
        else:
            pts = [(W, H * 0.30), (W - tail * 1.1, H * 0.30), (W - tail * 1.1, H * 0.98), (W, H * 0.98), (W - tail * 0.45, H * 0.64)]
        d.polygon(pts, fill=dark)
    im.alpha_composite(_shadow(im.size, body, 4 * s, 2 * s, 120, (0, 2 * s)))
    g = _grad(im.size, top, bottom)
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rectangle(body, fill=255)
    g.putalpha(m)
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    d.rectangle(body, outline=tuple(edge) + (255,), width=int(1.4 * s))
    d.line([(body[0] + 3 * s, body[1] + 3 * s), (body[2] - 3 * s, body[1] + 3 * s)], fill=(255, 255, 255, 110), width=int(1 * s))
    for x in (body[0], body[2]):
        d.polygon([(x, body[3]), (x + (fold if x == body[0] else -fold), body[3]), (x, H * 0.98)], fill=tuple(lerp(edge, (0, 0, 0), 0.3)) + (255,))
    fs = int((fsize or h * 0.42) * s)
    f = font('jalnan', fs)
    while _words_width(f, text) > (body[2] - body[0]) - 16 * s and fs > 8:
        fs = int(fs * 0.92)
        f = font('jalnan', fs)
    txt = _text_layer(im.size, (W / 2, (body[1] + body[3]) / 2 + 0.5 * s), text, f, (255, 255, 255), (255, 246, 220),
                      edge, 1.6 * s, shadow=(0, 1.5 * s, tuple(edge) + (200,)))
    im.alpha_composite(txt)
    return _finish(im, w, h, path)


# ------------------------------------------------------------------ 배지
def badge(text, w, h, color='red', fsize=None):
    path = _path('ui_badge', text, w, h, color, fsize)
    if os.path.exists(path):
        return path
    top, bottom, edge = PAL[color]
    im = _canvas(w, h)
    W, H = im.size
    s = R2 * SS
    box = (1 * s, 1 * s, W - 1 * s, H - 2 * s)
    rr = int((box[3] - box[1]) / 2.4)
    g = _grad(im.size, top, bottom)
    g.putalpha(_rr_mask(im.size, box, rr))
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, rr, outline=tuple(edge) + (255,), width=int(1 * s))
    f = font('jalnan', int((fsize or h * 0.56) * s))
    txt = _text_layer(im.size, (W / 2, (box[1] + box[3]) / 2), text, f, (255, 255, 255), (255, 255, 255), edge, 1.0 * s)
    im.alpha_composite(txt)
    return _finish(im, w, h, path)


# ------------------------------------------------------------------ 아이콘
def icon_img(name, size):
    """size: 무대 px. 반환 경로."""
    path = _path('ui_icon', name, size)
    if os.path.exists(path):
        return path
    im = _canvas(size, size)
    W, H = im.size
    s = W / 100.0
    d = ImageDraw.Draw(im)

    def C(x, y):
        return (x * s, y * s)

    def circ(cx, cy, r, fill, outline=None, width=0):
        d.ellipse((C(cx - r, cy - r), C(cx + r, cy + r)), fill=fill, outline=outline, width=int(width * s))

    if name == 'coin':
        circ(52, 54, 42, (150, 92, 10, 255))
        circ(50, 50, 42, (255, 206, 70, 255), (150, 92, 10, 255), 3)
        circ(50, 50, 32, (255, 228, 120, 255), (214, 150, 30, 255), 2)
        d.text(C(50, 52), '₩', font=font('jalnan', int(40 * s)), fill=(170, 100, 10, 255), anchor='mm')
        d.ellipse((C(28, 22), C(46, 34)), fill=(255, 255, 255, 140))
    elif name == 'ballot':
        d.rounded_rectangle((C(14, 40), C(86, 92)), int(8 * s), fill=(90, 120, 220, 255), outline=(20, 36, 110, 255), width=int(3 * s))
        d.rectangle((C(14, 40), C(86, 52)), fill=(130, 160, 245, 255))
        d.rectangle((C(32, 44), C(68, 49)), fill=(20, 36, 110, 255))
        d.rounded_rectangle((C(36, 10), C(64, 48)), int(3 * s), fill=(255, 255, 255, 255), outline=(60, 70, 110, 255), width=int(2 * s))
        d.line([C(42, 24), C(48, 32), C(58, 18)], fill=(230, 40, 60, 255), width=int(4 * s))
    elif name == 'mega':
        d.polygon([C(18, 40), C(70, 16), C(70, 84), C(18, 60)], fill=(255, 90, 90, 255), outline=(110, 10, 24, 255))
        d.rounded_rectangle((C(10, 38), C(24, 62)), int(3 * s), fill=(240, 240, 250, 255), outline=(60, 60, 80, 255), width=int(2 * s))
        d.ellipse((C(62, 14), C(80, 86)), fill=(255, 150, 150, 255), outline=(110, 10, 24, 255), width=int(2 * s))
        d.rectangle((C(28, 60), C(38, 84)), fill=(60, 60, 80, 255))
        for i, r in enumerate((10, 18)):
            d.arc((C(78 - r, 50 - r * 1.5), C(78 + r * 1.4, 50 + r * 1.5)), -40, 40, fill=(255, 220, 100, 255), width=int(3 * s))
    elif name == 'chart':
        d.rounded_rectangle((C(8, 8), C(92, 92)), int(14 * s), fill=(20, 40, 90, 255), outline=(110, 220, 255, 255), width=int(3 * s))
        for i, hh in enumerate((26, 40, 34, 56)):
            x = 20 + i * 16
            d.rectangle((C(x, 80 - hh), C(x + 10, 80)), fill=(80, 200, 255, 255))
        d.line([C(18, 62), C(40, 46), C(56, 54), C(82, 24)], fill=(255, 210, 80, 255), width=int(5 * s), joint='curve')
        d.polygon([C(84, 18), C(86, 34), C(72, 26)], fill=(255, 210, 80, 255))
    elif name == 'shield':
        d.polygon([C(50, 8), C(86, 22), C(80, 64), C(50, 92), C(20, 64), C(14, 22)], fill=(80, 170, 255, 255), outline=(10, 40, 110, 255))
        d.polygon([C(50, 18), C(76, 28), C(72, 60), C(50, 80)], fill=(150, 210, 255, 255))
        d.line([C(36, 50), C(46, 62), C(66, 36)], fill=(255, 255, 255, 255), width=int(6 * s))
    elif name == 'star':
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 44 if i % 2 == 0 else 19
            pts.append(C(50 + r * math.cos(a), 52 + r * math.sin(a)))
        d.polygon(pts, fill=(255, 210, 60, 255), outline=(150, 92, 10, 255))
    elif name == 'clock':
        circ(50, 50, 42, (255, 255, 255, 255), (40, 50, 90, 255), 5)
        d.line([C(50, 50), C(50, 22)], fill=(40, 50, 90, 255), width=int(6 * s))
        d.line([C(50, 50), C(70, 60)], fill=(230, 50, 70, 255), width=int(5 * s))
        circ(50, 50, 5, (40, 50, 90, 255))
    elif name == 'trophy':
        d.polygon([C(26, 14), C(74, 14), C(68, 50), C(32, 50)], fill=(255, 200, 60, 255), outline=(150, 92, 10, 255))
        d.arc((C(10, 16), C(34, 44)), 90, 270, fill=(255, 200, 60, 255), width=int(5 * s))
        d.arc((C(66, 16), C(90, 44)), -90, 90, fill=(255, 200, 60, 255), width=int(5 * s))
        d.rectangle((C(44, 50), C(56, 70)), fill=(220, 160, 40, 255))
        d.rounded_rectangle((C(28, 70), C(72, 86)), int(4 * s), fill=(150, 92, 10, 255))
    elif name == 'bolt':
        d.polygon([C(58, 6), C(20, 56), C(46, 56), C(38, 94), C(80, 40), C(54, 40)], fill=(255, 220, 60, 255), outline=(150, 92, 10, 255))
    elif name == 'shop':
        d.rounded_rectangle((C(14, 36), C(86, 90)), int(8 * s), fill=(255, 240, 220, 255), outline=(110, 60, 20, 255), width=int(3 * s))
        for i in range(5):
            col = (230, 60, 70, 255) if i % 2 == 0 else (255, 255, 255, 255)
            d.polygon([C(10 + i * 16, 22), C(26 + i * 16, 22), C(26 + i * 16, 40), C(10 + i * 16, 40)], fill=col)
        d.rectangle((C(40, 58), C(60, 90)), fill=(110, 60, 20, 255))
    elif name == 'map':
        d.polygon([C(10, 20), C(36, 10), C(64, 22), C(90, 12), C(90, 80), C(64, 90), C(36, 78), C(10, 88)], fill=(240, 230, 190, 255), outline=(110, 80, 30, 255))
        d.line([C(36, 10), C(36, 78)], fill=(180, 150, 90, 255), width=int(2 * s))
        d.line([C(64, 22), C(64, 90)], fill=(180, 150, 90, 255), width=int(2 * s))
        d.line([C(16, 70), C(40, 50), C(56, 60), C(80, 30)], fill=(230, 50, 70, 255), width=int(4 * s))
    elif name == 'person':
        circ(50, 30, 18, (255, 220, 190, 255), (60, 40, 30, 255), 2)
        d.pieslice((C(16, 52), C(84, 120)), 180, 360, fill=(40, 60, 140, 255))
    elif name == 'back':
        d.polygon([C(14, 50), C(48, 18), C(48, 36), C(86, 36), C(86, 64), C(48, 64), C(48, 82)], fill=(255, 255, 255, 255))
    elif name == 'up':
        d.polygon([C(50, 14), C(86, 62), C(62, 62), C(62, 88), C(38, 88), C(38, 62), C(14, 62)], fill=(255, 80, 90, 255))
    elif name == 'down':
        d.polygon([C(50, 86), C(86, 38), C(62, 38), C(62, 12), C(38, 12), C(38, 38), C(14, 38)], fill=(70, 150, 255, 255))
    im = im.resize((size * R2, size * R2), Image.LANCZOS)
    im.save(path, optimize=True)
    return path


# ------------------------------------------------------------------ 막대 세트
def bar_set(name, w, h, color, steps=41):
    top, bottom, edge = PAL[color]
    out = []
    for i in range(steps):
        path = os.path.join(ensure_out(), 'ui_bar_%s_%s_%02d.png' % (name, _k(w, h, color, steps), i))
        if not os.path.exists(path):
            im = _canvas(w, h)
            W, H = im.size
            s = R2 * SS
            rr = H // 2
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, W - 1, H - 1), rr, fill=(8, 12, 32, 235), outline=(255, 255, 255, 120), width=int(0.8 * s))
            frac = i / (steps - 1)
            if frac > 0:
                ins = int(1.6 * s)
                fw = max(H - 2 * ins, int((W - 2 * ins) * frac))
                g = _grad((fw, H - 2 * ins), top, bottom)
                g.putalpha(_rr_mask((fw, H - 2 * ins), (0, 0, fw - 1, H - 2 * ins - 1), (H - 2 * ins) // 2))
                im.alpha_composite(g, (ins, ins))
                hl = Image.new('RGBA', (fw, (H - 2 * ins) // 2), (255, 255, 255, 0))
                hm = _rr_mask(hl.size, (2 * s, 0, max(2 * s + 1, fw - 2 * s), hl.height - 1), hl.height // 2).point(lambda v: v * 80 // 255)
                hl.putalpha(hm)
                im.alpha_composite(hl, (ins, ins))
            _finish(im, w, h, path)
        out.append(('%02d' % i, path))
    return out


# ------------------------------------------------------------------ 파티클
def sparkle(size=16, color=(255, 236, 150)):
    path = _path('fx_spark', size, color)
    if os.path.exists(path):
        return path
    im = _canvas(size, size)
    W = im.width
    d = ImageDraw.Draw(im)
    c = W / 2
    for r, a in ((W * 0.48, 90), (W * 0.30, 160)):
        d.ellipse((c - r * 0.35, c - r * 0.35, c + r * 0.35, c + r * 0.35), fill=tuple(color) + (a,))
    d.polygon([(c, 0), (c + W * 0.09, c - W * 0.09), (W, c), (c + W * 0.09, c + W * 0.09), (c, W), (c - W * 0.09, c + W * 0.09), (0, c), (c - W * 0.09, c - W * 0.09)], fill=(255, 255, 255, 255))
    im = im.filter(ImageFilter.GaussianBlur(W * 0.01))
    return _finish(im, size, size, path)


def confetti(i, size=10):
    cols = [(255, 90, 110), (255, 210, 70), (90, 200, 255), (130, 230, 130), (200, 140, 255), (255, 150, 60)]
    path = _path('fx_conf', i, size)
    if os.path.exists(path):
        return path
    im = _canvas(size, size)
    W = im.width
    d = ImageDraw.Draw(im)
    col = cols[i % len(cols)]
    if i % 3 == 0:
        d.rectangle((W * 0.25, W * 0.05, W * 0.75, W * 0.95), fill=col + (255,))
    elif i % 3 == 1:
        d.ellipse((W * 0.1, W * 0.1, W * 0.9, W * 0.9), fill=col + (255,))
    else:
        d.polygon([(W * 0.5, 0), (W, W), (0, W)], fill=col + (255,))
    return _finish(im, size, size, path)


def portrait_ring(src_img, size, ring='gold', name='p'):
    """원형 초상 + 금속 테두리."""
    path = _path('ui_port', name, size, ring)
    if os.path.exists(path):
        return path
    im = _canvas(size, size)
    W = im.width
    s = R2 * SS
    face = src_img.convert('RGBA')
    side = min(face.size)
    face = face.crop(((face.width - side) // 2, 0, (face.width - side) // 2 + side, side)).resize((W, W), Image.LANCZOS)
    m = Image.new('L', (W, W), 0)
    ImageDraw.Draw(m).ellipse((3 * s, 3 * s, W - 3 * s, W - 3 * s), fill=255)
    bg = _grad((W, W), (60, 76, 150), (20, 26, 70))
    bg.putalpha(m)
    im.alpha_composite(bg)
    face.putalpha(ImageChops.multiply(m, face.getchannel('A')))
    im.alpha_composite(face)
    top, bottom, edge = PAL[ring]
    rm = Image.new('L', (W, W), 0)
    ImageDraw.Draw(rm).ellipse((1 * s, 1 * s, W - 1 * s, W - 1 * s), outline=255, width=int(2.4 * s))
    rg = _grad((W, W), top, bottom)
    rg.putalpha(rm)
    im.alpha_composite(rg)
    return _finish(im, size, size, path)


def preview_sheet(path):
    """키트 확인용 시트."""
    sheet = Image.new('RGBA', (960, 540), (0, 0, 0, 255))
    sheet.paste(vgradient((960, 540), (20, 24, 60), (60, 30, 90)).convert('RGBA'))
    def put(p, x, y):
        im = Image.open(p)
        sheet.alpha_composite(im, (x, y))
    put(panel(220, 120, 'glass', header='gold'), 10, 10)
    put(panel(160, 90, 'card'), 470, 10)
    put(panel(150, 90, 'alert'), 800, 10)
    put(button('게임 시작', 130, 34, 'gold'), 10, 260)
    put(button('주식', 90, 30, 'blue', icon='chart'), 280, 260)
    put(button('사건', 90, 30, 'purple', icon='bolt'), 470, 260)
    put(button('매수 +1', 80, 28, 'red'), 660, 260)
    put(button('매도 -1', 80, 28, 'blue'), 830, 260)
    put(banner('조치원역 광장 · 댄스배틀', 230, 40, 'gold'), 10, 330)
    put(banner('돌발상황!', 160, 40, 'red'), 480, 330)
    put(big_text('PERFECT!', 34), 10, 420)
    put(big_text('성공!', 34, 'green'), 330, 420)
    put(big_text('실패...', 30, 'red'), 520, 420)
    put(badge('대형', 40, 18, 'red'), 820, 340)
    put(badge('중형', 40, 18, 'gold'), 820, 380)
    for i, n in enumerate(['coin', 'ballot', 'mega', 'chart', 'shield', 'star', 'clock', 'trophy', 'bolt', 'shop', 'map']):
        put(icon_img(n, 28), 700 + (i % 4) * 64, 400 + (i // 4) * 44)
    bars = bar_set('test', 120, 12, 'gold')
    put(bars[28][1], 10, 200)
    put(sparkle(16), 300, 200)
    sheet.convert('RGB').save(path)
