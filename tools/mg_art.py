# -*- coding: utf-8 -*-
"""미니게임 15종 그림 (2배 해상도로 저장, pic_scale 0.5). 크기 인자는 모두 '무대 px'.

UI 는 검정+청색 테마. 은행잎·복숭아·벚꽃처럼 물건 자체의 색은 실제 색을 쓴다.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from art_common import *
import ui_kit as K

R2, SS = 2, 3


def _cv(w, h):
    return Image.new('RGBA', (int(w * R2 * SS), int(h * R2 * SS)), (0, 0, 0, 0))


def _fin(im, w, h, name):
    p = os.path.join(ensure_out(), 'mg_' + name + '.png')
    im.resize((int(w * R2), int(h * R2)), Image.LANCZOS).save(p)
    return p


def _jtext(d, xy, text, size, fill):
    """잘난체(공백 글리프 없음) 가운데 정렬 글자."""
    f = font('jalnan', int(size))
    K._draw_line(d, xy[0], xy[1], text, f, fill)


def _cached(name):
    p = os.path.join(ensure_out(), 'mg_' + name + '.png')
    return p if os.path.exists(p) else None


def _mask_layer(size, draw_fn):
    m = Image.new('L', size, 0)
    draw_fn(ImageDraw.Draw(m))
    return m


def _fill(im, mask, top, bottom=None):
    g = K._grad(im.size, top, bottom or top)
    g.putalpha(ImageChops.multiply(mask, g.getchannel('A')))
    im.alpha_composite(g)


def _outline(im, mask, col, width):
    o = mask.filter(ImageFilter.MaxFilter(int(width) | 1))
    lay = Image.new('RGBA', im.size, col + (255,))
    lay.putalpha(ImageChops.subtract(o, mask))
    im.alpha_composite(lay)


def _glow(im, mask, col, radius, strength=200):
    g = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    lay = Image.new('RGBA', im.size, col + (255,))
    lay.putalpha(g.point(lambda v: min(255, v * strength // 255)))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(lay)
    out.alpha_composite(im)
    return out


def _shadow(im, mask, off, blur, alpha=140):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 255))
    sh.putalpha(mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * alpha // 255))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (int(off[0]), int(off[1])))
    out.alpha_composite(im)
    return out


def _hl(im, mask, frac=0.45, alpha=70):
    bb = mask.getbbox()
    if not bb:
        return
    hm = Image.new('L', im.size, 0)
    ImageDraw.Draw(hm).ellipse((bb[0] + (bb[2] - bb[0]) * 0.12, bb[1] + (bb[3] - bb[1]) * 0.05,
                                bb[2] - (bb[2] - bb[0]) * 0.35, bb[1] + (bb[3] - bb[1]) * frac), fill=alpha)
    hm = ImageChops.multiply(hm.filter(ImageFilter.GaussianBlur(im.width * 0.02)), mask)
    w = Image.new('RGBA', im.size, (255, 255, 255, 255))
    w.putalpha(hm)
    im.alpha_composite(w)


# ================================================================== 공통
def plain_rect(w, h, rgba, name):
    p = _cached(name)
    if p:
        return p
    im = Image.new('RGBA', (w * R2, h * R2), rgba)
    p = os.path.join(ensure_out(), 'mg_' + name + '.png')
    im.save(p)
    return p


def clear_dot():
    p = _cached('clear_dot')
    if p:
        return p
    p = os.path.join(ensure_out(), 'mg_clear_dot.png')
    Image.new('RGBA', (8, 8), (0, 0, 0, 1)).save(p)
    return p


# ================================================================== 1. 리듬 (댄스배틀)
LANE_COLS = [((150, 110, 255), (60, 30, 170)), ((70, 130, 255), (16, 50, 190)),
             ((255, 90, 120), (170, 20, 60)), ((170, 190, 240), (70, 90, 160))]
LANE_ANG = [180, 270, 90, 0]   # ← ↓ ↑ → (오른쪽 화살표 기준 회전, 반시계)


def _arrow_mask(size, s, ang, scale=1.0):
    W, H = size
    cx, cy = W / 2, H / 2
    L = W * 0.40 * scale
    pts = [(L, 0), (0, -L * 0.95), (0, -L * 0.42), (-L * 0.92, -L * 0.42), (-L * 0.92, L * 0.42), (0, L * 0.42), (0, L * 0.95)]
    a = math.radians(-ang)
    rp = [(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)) for x, y in pts]
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).polygon(rp, fill=255)
    return m


def rhythm_note(lane):
    name = 'note_%d' % lane
    if _cached(name):
        return _cached(name)
    w = h = 40
    im = _cv(w, h)
    s = R2 * SS
    m = _arrow_mask(im.size, s, LANE_ANG[lane])
    top, bot = LANE_COLS[lane]
    _fill(im, m, lerp(top, (255, 255, 255), 0.25), bot)
    _outline(im, m, (4, 6, 20), 2.2 * s)
    _hl(im, m, 0.5, 80)
    im = _glow(im, m, top, 3 * s, 150)
    return _fin(im, w, h, name)


def rhythm_receptor(lane, lit=False):
    name = 'recep_%d_%d' % (lane, lit)
    if _cached(name):
        return _cached(name)
    w = h = 44
    im = _cv(w, h)
    s = R2 * SS
    m = _arrow_mask(im.size, s, LANE_ANG[lane], 0.92)
    top, bot = LANE_COLS[lane]
    inner = m.filter(ImageFilter.MinFilter(int(3 * s) | 1))
    ring = ImageChops.subtract(m, inner)
    if lit:
        _fill(im, m, lerp(top, (255, 255, 255), 0.5), top)
        im = _glow(im, m, top, 6 * s, 255)
    else:
        lay = Image.new('RGBA', im.size, (10, 14, 34, 255))
        lay.putalpha(inner.point(lambda v: v * 150 // 255))
        im.alpha_composite(lay)
        lay = Image.new('RGBA', im.size, top + (255,))
        lay.putalpha(ring.point(lambda v: v * 200 // 255))
        im.alpha_composite(lay)
    return _fin(im, w, h, name)


def rhythm_lanes(w=208, h=270, judge_y=-80):
    name = 'lanes_%d' % judge_y
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    lw = W / 4
    for i in range(4):
        x0 = i * lw
        top, bot = LANE_COLS[i]
        g = K._grad((int(lw), H), (2, 3, 12), tuple(int(c * 0.22) for c in bot))
        g.putalpha(Image.new('L', g.size, 190))
        im.alpha_composite(g, (int(x0), 0))
        d = ImageDraw.Draw(im)
        d.line([(x0, 0), (x0, H)], fill=(60, 90, 200, 160), width=int(0.8 * s))
    d.line([(W - 1, 0), (W - 1, H)], fill=(60, 90, 200, 160), width=int(0.8 * s))
    jy = (h / 2 - judge_y) * R2 * SS
    gl = Image.new('L', im.size, 0)
    ImageDraw.Draw(gl).rectangle((0, jy - 2 * s, W, jy + 2 * s), fill=255)
    gl = gl.filter(ImageFilter.GaussianBlur(4 * s))
    lay = Image.new('RGBA', im.size, (60, 110, 255, 255))
    lay.putalpha(gl)
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    d.line([(0, jy), (W, jy)], fill=(200, 214, 255, 230), width=int(1 * s))
    return _fin(im, w, h, name)


# ================================================================== 2. 은행잎 받기
def ginkgo(kind):
    """kind: leaf / gold / dry"""
    name = 'ginkgo_' + kind
    if _cached(name):
        return _cached(name)
    w = h = 30
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    cx, cy = W / 2, H * 0.62
    R = W * 0.44
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.pieslice((cx - R, cy - R, cx + R, cy + R), 200, 340, fill=255)
    # 가운데 갈라짐
    d.polygon([(cx, cy - R * 0.9), (cx - R * 0.10, cy - R * 1.05), (cx + R * 0.10, cy - R * 1.05)], fill=0)
    d.polygon([(cx - R * 0.07, cy), (cx + R * 0.07, cy), (cx + R * 0.05, cy - R * 0.55), (cx - R * 0.05, cy - R * 0.55)], fill=255)
    col = {'leaf': ((255, 226, 90), (226, 160, 20)), 'gold': ((255, 246, 190), (240, 180, 30)),
           'dry': ((168, 120, 70), (96, 60, 30))}[kind]
    _fill(im, m, col[0], col[1])
    d2 = ImageDraw.Draw(im)
    for k in range(-3, 4):
        a = math.radians(270 + k * 16)
        d2.line([(cx, cy), (cx + R * 0.9 * math.cos(a), cy + R * 0.9 * math.sin(a))], fill=tuple(int(c * 0.8) for c in col[1]) + (130,), width=int(0.5 * s))
    d2.line([(cx, cy), (cx + R * 0.1, H - 1.5 * s)], fill=(110, 80, 20, 255), width=int(1.4 * s))
    _outline(im, m, (60, 40, 10) if kind != 'dry' else (40, 20, 6), 1.2 * s)
    if kind == 'gold':
        im = _glow(im, m, (255, 240, 170), 3 * s, 230)
        d3 = ImageDraw.Draw(im)
        for (px, py, r) in ((0.25, 0.25, 3), (0.78, 0.3, 2.2)):
            x, y = W * px, H * py
            d3.polygon([(x, y - r * s), (x + 0.6 * s, y - 0.6 * s), (x + r * s, y), (x + 0.6 * s, y + 0.6 * s), (x, y + r * s),
                        (x - 0.6 * s, y + 0.6 * s), (x - r * s, y), (x - 0.6 * s, y - 0.6 * s)], fill=(255, 255, 255, 255))
    return _fin(im, w, h, name)


def basket():
    name = 'basket'
    if _cached(name):
        return _cached(name)
    w, h = 76, 44
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.polygon([(W * 0.04, H * 0.30), (W * 0.96, H * 0.30), (W * 0.84, H * 0.96), (W * 0.16, H * 0.96)], fill=255)
    _fill(im, m, (150, 104, 60), (90, 58, 30))
    d = ImageDraw.Draw(im)
    for i in range(1, 6):
        y = H * 0.30 + (H * 0.66) * i / 6
        d.line([(W * 0.06 + i * 1.5 * s, y), (W * 0.94 - i * 1.5 * s, y)], fill=(70, 44, 20, 200), width=int(0.8 * s))
    for i in range(1, 9):
        x = W * 0.06 + (W * 0.88) * i / 9
        d.line([(x, H * 0.32), (W / 2 + (x - W / 2) * 0.78, H * 0.94)], fill=(70, 44, 20, 150), width=int(0.6 * s))
    d.rounded_rectangle((W * 0.02, H * 0.24, W * 0.98, H * 0.36), 3 * s, fill=(178, 130, 80, 255), outline=(60, 36, 14, 255), width=int(1 * s))
    # 청색 띠 + 기호
    d.rectangle((W * 0.14, H * 0.50, W * 0.86, H * 0.72), fill=(26, 52, 170, 255))
    _jtext(d, (W / 2, H * 0.61), '기호 3번 막내', H * 0.16, (255, 255, 255, 255))
    _outline(im, m, (40, 24, 8), 1.4 * s)
    return _fin(im, w, h, name)


# ================================================================== 3. 팔씨름
def arms():
    """두 팔이 맞잡은 모양. 회전 중심(팔꿈치 사이)이 그림 한가운데."""
    name = 'arms'
    if _cached(name):
        return _cached(name)
    w, h = 150, 200
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    cx, cy = W / 2, H / 2          # 회전 중심 (팔꿈치 높이)
    hy = cy - H * 0.36             # 맞잡은 손 위치
    for side, sleeve, skin in ((-1, (24, 40, 120), (238, 196, 168)), (1, (150, 20, 40), (214, 170, 140))):
        ex = cx + side * W * 0.26
        m = Image.new('L', im.size, 0)
        d = ImageDraw.Draw(m)
        d.line([(ex, cy + H * 0.02), (cx + side * W * 0.05, hy + H * 0.04)], fill=255, width=int(W * 0.17))
        d.ellipse((ex - W * 0.10, cy - W * 0.07, ex + W * 0.10, cy + W * 0.11), fill=255)
        mx, my = (ex + cx + side * W * 0.05) / 2, (cy + hy) / 2
        d.ellipse((mx - W * 0.10, my - W * 0.09, mx + W * 0.10, my + W * 0.11), fill=255)
        _fill(im, m, skin, tuple(int(c * 0.82) for c in skin))
        _outline(im, m, (40, 20, 16), 1.4 * s)
        sm = Image.new('L', im.size, 0)
        ImageDraw.Draw(sm).rounded_rectangle((ex - W * 0.15, cy + H * 0.02, ex + W * 0.15, cy + H * 0.2), 6 * s, fill=255)
        _fill(im, sm, lerp(sleeve, (255, 255, 255), 0.15), sleeve)
        _outline(im, sm, (6, 6, 14), 1.2 * s)
    # 맞잡은 손
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((cx - W * 0.16, hy - W * 0.13, cx + W * 0.16, hy + W * 0.14), fill=255)
    _fill(im, m, (240, 200, 172), (200, 156, 128))
    _outline(im, m, (40, 20, 16), 1.4 * s)
    d = ImageDraw.Draw(im)
    for k in range(3):
        y = hy - W * 0.05 + k * W * 0.05
        d.arc((cx - W * 0.09, y - W * 0.03, cx + W * 0.09, y + W * 0.03), 200, 340, fill=(120, 70, 50, 200), width=int(0.8 * s))
    return _fin(im, w, h, name)


def table_top(w=300, h=46):
    name = 'table_%d' % w
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((2 * s, 4 * s, W - 2 * s, H - 2 * s), 6 * s, fill=255)
    _fill(im, m, (92, 60, 40), (40, 24, 14))
    d = ImageDraw.Draw(im)
    rng = random.Random(3)
    for i in range(14):
        y = rng.uniform(8 * s, H - 6 * s)
        d.line([(6 * s, y), (W - 6 * s, y + rng.uniform(-3, 3) * s)], fill=(30, 18, 10, 80), width=int(0.6 * s))
    d.line([(4 * s, 6 * s), (W - 4 * s, 6 * s)], fill=(160, 120, 90, 160), width=int(1 * s))
    im = _shadow(im, m, (0, 3 * s), 3 * s)
    return _fin(im, w, h, name)


def tug_meter(w=260, h=22):
    name = 'tug_%d' % w
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    box = (2 * s, 4 * s, W - 2 * s, H - 4 * s)
    g = Image.new('RGBA', im.size, (0, 0, 0, 0))
    for x in range(int(box[0]), int(box[2])):
        t = (x - box[0]) / (box[2] - box[0])
        c = lerp((200, 30, 50), (10, 10, 20), t * 2) if t < 0.5 else lerp((10, 10, 20), (40, 90, 255), (t - 0.5) * 2)
        ImageDraw.Draw(g).line([(x, box[1]), (x, box[3])], fill=tuple(c) + (255,))
    mm = Image.new('L', im.size, 0)
    ImageDraw.Draw(mm).rounded_rectangle(box, (box[3] - box[1]) / 2, fill=255)
    g.putalpha(mm)
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, (box[3] - box[1]) / 2, outline=(200, 214, 255, 255), width=int(1 * s))
    d.line([(W / 2, 1 * s), (W / 2, H - 1 * s)], fill=(255, 255, 255, 255), width=int(1.2 * s))
    return _fin(im, w, h, name)


def tug_knob():
    name = 'tug_knob'
    if _cached(name):
        return _cached(name)
    w = h = 18
    im = _cv(w, h)
    W = im.width
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).ellipse((2 * s, 2 * s, W - 2 * s, W - 2 * s), fill=255)
    _fill(im, m, (255, 255, 255), (170, 186, 230))
    _outline(im, m, (4, 6, 20), 1.6 * s)
    im = _glow(im, m, (80, 130, 255), 3 * s, 200)
    return _fin(im, w, h, name)


# ================================================================== 4. 복숭아 선별
def peach(kind):
    """kind: raw(덜 익음) / ripe(잘 익음) / bad(상함)"""
    name = 'peach_' + kind
    if _cached(name):
        return _cached(name)
    w = h = 44
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((W * 0.12, H * 0.20, W * 0.56, H * 0.92), fill=255)
    d.ellipse((W * 0.44, H * 0.20, W * 0.88, H * 0.92), fill=255)
    d.ellipse((W * 0.20, H * 0.26, W * 0.80, H * 0.94), fill=255)
    cols = {'raw': ((190, 230, 120), (110, 170, 60)), 'ripe': ((255, 196, 186), (236, 92, 110)),
            'bad': ((170, 130, 100), (96, 64, 44))}[kind]
    _fill(im, m, cols[0], cols[1])
    if kind == 'ripe':
        bl = Image.new('L', im.size, 0)
        ImageDraw.Draw(bl).ellipse((W * 0.40, H * 0.30, W * 0.86, H * 0.86), fill=150)
        bl = ImageChops.multiply(bl.filter(ImageFilter.GaussianBlur(4 * s)), m)
        lay = Image.new('RGBA', im.size, (220, 40, 70, 255))
        lay.putalpha(bl)
        im.alpha_composite(lay)
    if kind == 'bad':
        d2 = ImageDraw.Draw(im)
        rng = random.Random(5)
        for i in range(6):
            x, y, r = W * rng.uniform(0.25, 0.75), H * rng.uniform(0.4, 0.85), W * rng.uniform(0.04, 0.09)
            d2.ellipse((x - r, y - r, x + r, y + r), fill=(52, 34, 22, 230))
    d3 = ImageDraw.Draw(im)
    d3.arc((W * 0.32, H * 0.22, W * 0.60, H * 0.90), 250, 340, fill=tuple(int(c * 0.75) for c in cols[1]) + (200,), width=int(1 * s))
    _hl(im, m, 0.45, 80)
    _outline(im, m, (50, 20, 16), 1.4 * s)
    # 잎
    lm = Image.new('L', im.size, 0)
    ImageDraw.Draw(lm).ellipse((W * 0.48, H * 0.06, W * 0.80, H * 0.24), fill=255)
    _fill(im, lm, (110, 190, 90), (40, 120, 50) if kind != 'bad' else (70, 70, 40))
    _outline(im, lm, (20, 50, 20), 1 * s)
    return _fin(im, w, h, name)


def conveyor(w=330, h=34):
    name = 'conveyor_%d' % w
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2 * s, 6 * s, W - 2 * s, H - 4 * s), (H - 10 * s) / 2, fill=(20, 22, 32, 255), outline=(110, 130, 190, 255), width=int(1.2 * s))
    for i in range(18):
        x = 8 * s + i * (W - 16 * s) / 17
        d.ellipse((x - 3 * s, H / 2 - 3 * s, x + 3 * s, H / 2 + 3 * s), fill=(70, 80, 110, 255))
    d.line([(6 * s, 8 * s), (W - 6 * s, 8 * s)], fill=(160, 176, 220, 120), width=int(0.8 * s))
    return _fin(im, w, h, name)


def crate(label, key_label, col):
    name = 'crate_%s' % key_label
    if _cached(name):
        return _cached(name)
    w, h = 96, 64
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((3 * s, 10 * s, W - 3 * s, H - 3 * s), 5 * s, fill=255)
    _fill(im, m, (118, 84, 54), (70, 46, 26))
    d = ImageDraw.Draw(im)
    for i in range(1, 4):
        y = 10 * s + (H - 13 * s) * i / 4
        d.line([(5 * s, y), (W - 5 * s, y)], fill=(50, 30, 14, 200), width=int(1 * s))
    top, bottom, edge, rim = K._pal(col)
    d.rounded_rectangle((8 * s, H * 0.36, W - 8 * s, H * 0.80), 4 * s, fill=bottom + (240,), outline=rim + (255,), width=int(1 * s))
    _jtext(d, (W / 2, H * 0.58), label, H * 0.17, (255, 255, 255, 255))
    kb = (W / 2 - 13 * s, 0, W / 2 + 13 * s, 14 * s)
    d.rounded_rectangle(kb, 3 * s, fill=(8, 10, 24, 255), outline=(200, 214, 255, 255), width=int(1 * s))
    d.text(((kb[0] + kb[2]) / 2, (kb[1] + kb[3]) / 2), key_label, font=font('nsrb', int(10 * s)), fill=(255, 255, 255, 255), anchor='mm')
    _outline(im, m, (30, 18, 8), 1.4 * s)
    return _fin(im, w, h, name)


# ================================================================== 5. 주문 기억하기
CAFE = [('아메리카노', (40, 26, 20)), ('카페라떼', (196, 150, 110)), ('복숭아에이드', (255, 150, 170)), ('조치원 케이크', (250, 240, 230))]


def cafe_card(i, lit=False):
    name = 'cafe_%d_%d' % (i, lit)
    if _cached(name):
        return _cached(name)
    w, h = 86, 96
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    box = (3 * s, 3 * s, W - 3 * s, H - 3 * s)
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, 10 * s, fill=255)
    if lit:
        _fill(im, m, (70, 110, 255), (20, 40, 160))
    else:
        _fill(im, m, (24, 30, 60), (6, 8, 22))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2, H * 0.42
    nm, col = CAFE[i]
    if i in (0, 1):     # 머그잔
        d.rounded_rectangle((cx - 16 * s, cy - 12 * s, cx + 14 * s, cy + 16 * s), 4 * s, fill=(240, 244, 255, 255), outline=(20, 24, 40, 255), width=int(1.2 * s))
        d.arc((cx + 8 * s, cy - 6 * s, cx + 24 * s, cy + 10 * s), 270, 90, fill=(240, 244, 255, 255), width=int(3 * s))
        d.ellipse((cx - 14 * s, cy - 15 * s, cx + 12 * s, cy - 8 * s), fill=col + (255,))
        if i == 1:
            d.text((cx - 1 * s, cy - 11.5 * s), '♥', font=font('nsrb', int(7 * s)), fill=(255, 255, 255, 255), anchor='mm')
        for k in range(3):
            x = cx - 8 * s + k * 7 * s
            d.arc((x - 3 * s, cy - 30 * s, x + 3 * s, cy - 18 * s), 100, 260, fill=(220, 230, 255, 180), width=int(1 * s))
    elif i == 2:        # 에이드 잔
        d.polygon([(cx - 14 * s, cy - 18 * s), (cx + 14 * s, cy - 18 * s), (cx + 10 * s, cy + 18 * s), (cx - 10 * s, cy + 18 * s)], fill=(255, 255, 255, 90), outline=(220, 230, 255, 255))
        d.polygon([(cx - 13 * s, cy - 8 * s), (cx + 13 * s, cy - 8 * s), (cx + 10 * s, cy + 17 * s), (cx - 10 * s, cy + 17 * s)], fill=col + (230,))
        d.line([(cx + 4 * s, cy - 26 * s), (cx + 1 * s, cy + 8 * s)], fill=(40, 90, 255, 255), width=int(2 * s))
        d.ellipse((cx - 12 * s, cy - 22 * s, cx - 2 * s, cy - 12 * s), fill=(255, 170, 160, 255), outline=(150, 40, 60, 255))
    else:               # 케이크
        d.polygon([(cx - 18 * s, cy + 14 * s), (cx + 18 * s, cy + 14 * s), (cx + 18 * s, cy - 4 * s), (cx - 4 * s, cy - 14 * s), (cx - 18 * s, cy - 4 * s)], fill=col + (255,), outline=(60, 40, 30, 255))
        d.line([(cx - 18 * s, cy + 3 * s), (cx + 18 * s, cy + 3 * s)], fill=(236, 110, 130, 255), width=int(3 * s))
        d.ellipse((cx - 6 * s, cy - 22 * s, cx + 4 * s, cy - 12 * s), fill=(255, 150, 160, 255), outline=(150, 40, 60, 255))
    _jtext(d, (W / 2, H * 0.84), nm, 10 * s if len(nm) < 6 else 8.5 * s, (255, 255, 255, 255))
    d.rounded_rectangle(box, 10 * s, outline=(200, 214, 255, 255) if lit else (70, 90, 170, 255), width=int((2 if lit else 1.2) * s))
    if lit:
        im = _glow(im, m, (60, 110, 255), 5 * s, 255)
    return _fin(im, w, h, name)


# ================================================================== 6. 풍선 사격
BALLOON_COLS = {'blue': ((90, 140, 255), (20, 50, 190)), 'red': ((255, 110, 130), (180, 20, 50)),
                'purple': ((190, 140, 255), (90, 40, 200)), 'silver': ((235, 240, 255), (130, 140, 170)),
                'gold': ((255, 240, 170), (230, 170, 30)), 'bomb': ((70, 70, 80), (10, 10, 14))}


def balloon(kind):
    name = 'balloon_' + kind
    if _cached(name):
        return _cached(name)
    w, h = 36, 58
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((W * 0.08, H * 0.02, W * 0.92, H * 0.66), fill=255)
    d.polygon([(W * 0.44, H * 0.64), (W * 0.56, H * 0.64), (W * 0.5, H * 0.70)], fill=255)
    top, bot = BALLOON_COLS[kind]
    _fill(im, m, top, bot)
    _hl(im, m, 0.4, 110)
    _outline(im, m, (8, 8, 16), 1.2 * s)
    d = ImageDraw.Draw(im)
    pts = [(W * 0.5 + math.sin(t / 3) * 2.5 * s, H * 0.70 + t * (H * 0.29) / 12) for t in range(13)]
    d.line(pts, fill=(220, 226, 240, 220), width=int(0.8 * s))
    if kind == 'bomb':
        cx, cy = W / 2, H * 0.32
        d.ellipse((cx - 8 * s, cy - 8 * s, cx + 8 * s, cy + 6 * s), fill=(240, 240, 240, 255))
        d.ellipse((cx - 5 * s, cy - 4 * s, cx - 1.5 * s, cy - 0.5 * s), fill=(10, 10, 10, 255))
        d.ellipse((cx + 1.5 * s, cy - 4 * s, cx + 5 * s, cy - 0.5 * s), fill=(10, 10, 10, 255))
        d.rectangle((cx - 4 * s, cy + 6 * s, cx + 4 * s, cy + 9 * s), fill=(240, 240, 240, 255))
        d.text((W / 2, H * 0.55), '꽝', font=font('jalnan', int(8 * s)), fill=(255, 80, 90, 255), anchor='mm')
    if kind == 'gold':
        d.text((W / 2, H * 0.34), '+3', font=font('jalnan', int(11 * s)), fill=(140, 80, 0, 255), anchor='mm')
        im = _glow(im, m, (255, 230, 140), 3 * s, 200)
    return _fin(im, w, h, name)


def crosshair():
    name = 'crosshair'
    if _cached(name):
        return _cached(name)
    w = h = 34
    im = _cv(w, h)
    W = im.width
    s = R2 * SS
    d = ImageDraw.Draw(im)
    c = W / 2
    for col, wd in (((0, 0, 0, 200), 3.2), ((255, 255, 255, 255), 1.4)):
        d.ellipse((c - 11 * s, c - 11 * s, c + 11 * s, c + 11 * s), outline=col, width=int(wd * s))
        for a, b in (((c, 0), (c, c - 5 * s)), ((c, c + 5 * s), (c, W)), ((0, c), (c - 5 * s, c)), ((c + 5 * s, c), (W, c))):
            d.line([a, b], fill=col, width=int(wd * s))
    d.ellipse((c - 1.5 * s, c - 1.5 * s, c + 1.5 * s, c + 1.5 * s), fill=(255, 60, 80, 255))
    return _fin(im, w, h, name)


def burst(col=(255, 255, 255)):
    name = 'burst_%d_%d_%d' % col
    if _cached(name):
        return _cached(name)
    w = h = 40
    im = _cv(w, h)
    W = im.width
    s = R2 * SS
    d = ImageDraw.Draw(im)
    c = W / 2
    for k in range(10):
        a = k * math.pi / 5
        d.line([(c + math.cos(a) * 7 * s, c + math.sin(a) * 7 * s), (c + math.cos(a) * 18 * s, c + math.sin(a) * 18 * s)],
               fill=col + (255,), width=int(2 * s))
    return _fin(im, w, h, name)


# ================================================================== 8. 미로
MAZE_W, MAZE_H = 15, 9
CELL = 24


def maze_layout(seed=1927):
    """완전 미로(DFS) + 몇 군데 벽을 더 뚫어 길을 여러 개로. 반환: walls[(x,y,dir)] 와 막다른 길 목록."""
    rng = random.Random(seed)
    W, H = MAZE_W, MAZE_H
    seen = [[False] * H for _ in range(W)]
    walls = set()
    for x in range(W):
        for y in range(H):
            walls.add((x, y, 'R'))
            walls.add((x, y, 'D'))
    stack = [(0, 0)]
    seen[0][0] = True
    while stack:
        x, y = stack[-1]
        nb = [(x + dx, y + dy, d) for dx, dy, d in ((1, 0, 'R'), (-1, 0, 'L'), (0, 1, 'D'), (0, -1, 'U'))
              if 0 <= x + dx < W and 0 <= y + dy < H and not seen[x + dx][y + dy]]
        if not nb:
            stack.pop()
            continue
        nx, ny, d = rng.choice(nb)
        if d == 'R':
            walls.discard((x, y, 'R'))
        elif d == 'L':
            walls.discard((nx, ny, 'R'))
        elif d == 'D':
            walls.discard((x, y, 'D'))
        else:
            walls.discard((nx, ny, 'D'))
        seen[nx][ny] = True
        stack.append((nx, ny))
    # 벽 몇 개 더 뚫기
    inner = [w_ for w_ in walls if (w_[2] == 'R' and w_[0] < W - 1) or (w_[2] == 'D' and w_[1] < H - 1)]
    for w_ in rng.sample(inner, 10):
        walls.discard(w_)

    def open_dirs(x, y):
        res = []
        if x < W - 1 and (x, y, 'R') not in walls:
            res.append((x + 1, y))
        if x > 0 and (x - 1, y, 'R') not in walls:
            res.append((x - 1, y))
        if y < H - 1 and (x, y, 'D') not in walls:
            res.append((x, y + 1))
        if y > 0 and (x, y - 1, 'D') not in walls:
            res.append((x, y - 1))
        return res
    dead = [(x, y) for x in range(W) for y in range(H) if len(open_dirs(x, y)) == 1 and (x, y) not in ((0, 0), (W - 1, H - 1))]
    rng.shuffle(dead)
    return walls, dead


def maze_walls(seed=1927):
    name = 'maze_%d' % seed
    walls, dead = maze_layout(seed)
    w, h = MAZE_W * CELL + 8, MAZE_H * CELL + 8
    if _cached(name):
        return _cached(name), dead
    im = _cv(w, h)
    s = R2 * SS
    k = CELL * s
    o = 4 * s
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    t = 3.2 * s
    d.rectangle((o - t, o - t, o + MAZE_W * k + t, o + t), fill=255)
    d.rectangle((o - t, o + MAZE_H * k - t, o + MAZE_W * k + t, o + MAZE_H * k + t), fill=255)
    d.rectangle((o - t, o - t, o + t, o + MAZE_H * k + t), fill=255)
    d.rectangle((o + MAZE_W * k - t, o - t, o + MAZE_W * k + t, o + MAZE_H * k + t), fill=255)
    for (x, y, dr) in walls:
        if dr == 'R' and x < MAZE_W - 1:
            d.rectangle((o + (x + 1) * k - t, o + y * k - t, o + (x + 1) * k + t, o + (y + 1) * k + t), fill=255)
        if dr == 'D' and y < MAZE_H - 1:
            d.rectangle((o + x * k - t, o + (y + 1) * k - t, o + (x + 1) * k + t, o + (y + 1) * k + t), fill=255)
    # 입구/출구 뚫기
    d.rectangle((o - t - 1, o + 0.2 * k, o + t + 1, o + 0.8 * k), fill=0)
    d.rectangle((o + MAZE_W * k - t - 1, o + (MAZE_H - 0.8) * k, o + MAZE_W * k + t + 1, o + (MAZE_H - 0.2) * k), fill=0)
    _fill(im, m, (120, 150, 255), (40, 70, 200))
    im = _glow(im, m, (40, 90, 255), 3 * s, 170)
    return _fin(im, w, h, name), dead


def maze_floor():
    w, h = MAZE_W * CELL + 8, MAZE_H * CELL + 8
    name = 'maze_floor'
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    s = R2 * SS
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 8 * s, fill=(4, 6, 18, 215))
    k = CELL * s
    for x in range(MAZE_W + 1):
        d.line([(4 * s + x * k, 4 * s), (4 * s + x * k, im.height - 4 * s)], fill=(30, 40, 90, 90), width=int(0.5 * s))
    for y in range(MAZE_H + 1):
        d.line([(4 * s, 4 * s + y * k), (im.width - 4 * s, 4 * s + y * k)], fill=(30, 40, 90, 90), width=int(0.5 * s))
    return _fin(im, w, h, name)


def ballot_paper():
    name = 'ballot_paper'
    if _cached(name):
        return _cached(name)
    w, h = 16, 18
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((1.5 * s, 1.5 * s, W - 1.5 * s, H - 1.5 * s), 2 * s, fill=255)
    _fill(im, m, (255, 255, 255), (210, 220, 240))
    d = ImageDraw.Draw(im)
    d.ellipse((W * 0.3, H * 0.3, W * 0.7, H * 0.66), outline=(220, 30, 50, 255), width=int(1.2 * s))
    d.text((W / 2, H * 0.48), '3', font=font('jalnan', int(6 * s)), fill=(220, 30, 50, 255), anchor='mm')
    _outline(im, m, (20, 24, 50), 1 * s)
    im = _glow(im, m, (80, 130, 255), 2 * s, 220)
    return _fin(im, w, h, name)


def exit_flag():
    name = 'exit_flag'
    if _cached(name):
        return _cached(name)
    w, h = 24, 24
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    d.line([(W * 0.3, H * 0.1), (W * 0.3, H * 0.92)], fill=(220, 226, 240, 255), width=int(1.6 * s))
    d.polygon([(W * 0.32, H * 0.12), (W * 0.9, H * 0.28), (W * 0.32, H * 0.46)], fill=(230, 40, 70, 255), outline=(40, 0, 8, 255))
    d.text((W * 0.55, H * 0.29), 'EXIT', font=font('nsrb', int(3.4 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return _fin(im, w, h, name)


# ================================================================== 9. 두더지
def hole_back():
    name = 'hole_back'
    if _cached(name):
        return _cached(name)
    w, h = 70, 30
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    d.ellipse((2 * s, 4 * s, W - 2 * s, H - 2 * s), fill=(70, 46, 28, 255))
    d.ellipse((7 * s, 7 * s, W - 7 * s, H - 5 * s), fill=(14, 8, 6, 255))
    return _fin(im, w, h, name)


def hole_front():
    """구멍 앞쪽 흙둔덕(두더지 아랫부분을 가림)."""
    name = 'hole_front'
    if _cached(name):
        return _cached(name)
    w, h = 76, 40
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.rectangle((0, H * 0.45, W, H), fill=255)
    d.ellipse((2 * s, H * 0.25 - 8 * s, W - 2 * s, H * 0.25 + 22 * s), fill=0)
    d.rectangle((0, H * 0.45, W, H), fill=255)
    cut = Image.new('L', im.size, 0)
    ImageDraw.Draw(cut).ellipse((0, H * 0.30, W, H * 1.0), fill=255)
    m = ImageChops.multiply(m, cut)
    _fill(im, m, (120, 84, 50), (64, 40, 20))
    d2 = ImageDraw.Draw(im)
    rng = random.Random(9)
    for i in range(16):
        x, y = rng.uniform(0.08, 0.92) * W, rng.uniform(0.6, 0.9) * H
        d2.ellipse((x - 1.4 * s, y - 1 * s, x + 1.4 * s, y + 1 * s), fill=(150, 110, 70, 200))
    _outline(im, m, (36, 22, 10), 1.2 * s)
    return _fin(im, w, h, name)


def mole(kind='mole', hit=False):
    name = 'mole_%s_%d' % (kind, hit)
    if _cached(name):
        return _cached(name)
    w, h = 54, 60
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    if kind == 'peach':
        p = Image.open(peach('ripe')).resize((int(W * 0.86), int(W * 0.86)), Image.LANCZOS)
        im.alpha_composite(p, (int(W * 0.07), int(H * 0.08)))
        d = ImageDraw.Draw(im)
        d.text((W / 2, H * 0.86), '때리면 감점', font=font('nsrb', int(7 * s)), fill=(255, 255, 255, 255), anchor='mm', stroke_width=int(1.2 * s), stroke_fill=(120, 0, 20, 255))
        return _fin(im, w, h, name)
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((W * 0.12, H * 0.10, W * 0.88, H * 0.80), fill=255)
    d.rectangle((W * 0.12, H * 0.45, W * 0.88, H), fill=255)
    _fill(im, m, (140, 100, 76), (86, 58, 40))
    _outline(im, m, (30, 18, 10), 1.6 * s)
    d = ImageDraw.Draw(im)
    # 얼굴
    d.ellipse((W * 0.30, H * 0.36, W * 0.70, H * 0.62), fill=(220, 186, 160, 255))
    if hit:
        for ex in (0.36, 0.64):
            x, y = W * ex, H * 0.30
            d.line([(x - 4 * s, y - 4 * s), (x + 4 * s, y + 4 * s)], fill=(10, 10, 10, 255), width=int(1.6 * s))
            d.line([(x - 4 * s, y + 4 * s), (x + 4 * s, y - 4 * s)], fill=(10, 10, 10, 255), width=int(1.6 * s))
        for k in range(3):
            a = -math.pi / 2 + (k - 1) * 0.7
            cx, cy = W / 2 + math.cos(a) * W * 0.45, H * 0.10 + math.sin(a) * H * 0.05
            d.text((cx, cy), '★', font=font('nsrb', int(8 * s)), fill=(255, 230, 120, 255), anchor='mm')
    else:
        for ex in (0.36, 0.64):
            x, y = W * ex, H * 0.30
            d.ellipse((x - 3.5 * s, y - 4 * s, x + 3.5 * s, y + 4 * s), fill=(10, 10, 10, 255))
            d.ellipse((x - 1.2 * s, y - 2.5 * s, x + 0.6 * s, y - 0.8 * s), fill=(255, 255, 255, 255))
    d.ellipse((W * 0.44, H * 0.38, W * 0.56, H * 0.47), fill=(230, 80, 110, 255))
    d.line([(W * 0.5, H * 0.47), (W * 0.5, H * 0.54)], fill=(60, 30, 20, 255), width=int(1 * s))
    for sx in (-1, 1):
        for k in (-1, 1):
            d.line([(W * 0.5 + sx * W * 0.12, H * 0.46 + k * 1.5 * s), (W * 0.5 + sx * W * 0.32, H * 0.44 + k * 3 * s)], fill=(60, 30, 20, 200), width=int(0.6 * s))
    # 넥타이 + 띠
    d.polygon([(W * 0.46, H * 0.66), (W * 0.54, H * 0.66), (W * 0.58, H * 0.92), (W * 0.5, H * 0.98), (W * 0.42, H * 0.92)], fill=(200, 26, 50, 255), outline=(60, 0, 10, 255))
    d.rounded_rectangle((W * 0.10, H * 0.70, W * 0.40, H * 0.84), 2 * s, fill=(10, 14, 34, 255))
    d.text((W * 0.25, H * 0.77), '반대', font=font('nsrb', int(5.4 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return _fin(im, w, h, name)


def hammer(down=False):
    name = 'hammer_%d' % down
    if _cached(name):
        return _cached(name)
    w = h = 54
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    lay = _cv(w, h)
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((W * 0.47, H * 0.30, W * 0.56, H * 0.95), 2 * s, fill=(150, 110, 70, 255), outline=(50, 30, 10, 255), width=int(1 * s))
    d.rounded_rectangle((W * 0.22, H * 0.10, W * 0.80, H * 0.36), 5 * s, fill=(40, 70, 210, 255), outline=(4, 8, 30, 255), width=int(1.4 * s))
    d.rectangle((W * 0.22, H * 0.10, W * 0.30, H * 0.36), fill=(200, 214, 255, 255))
    d.rectangle((W * 0.72, H * 0.10, W * 0.80, H * 0.36), fill=(200, 214, 255, 255))
    lay = lay.rotate(35 if not down else -10, resample=Image.BICUBIC, center=(W * 0.52, H * 0.85))
    im.alpha_composite(lay)
    return _fin(im, w, h, name)


# ================================================================== 10. 허들
def runner(frame):
    """frame: run1 / run2 / jump / fall"""
    name = 'runner_' + frame
    if _cached(name):
        return _cached(name)
    w, h = 44, 56
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    skin, shirt, pants = (236, 196, 166), (36, 70, 210), (12, 16, 40)
    hip = (W * 0.50, H * 0.58)
    sh = (W * 0.54, H * 0.32)
    poses = {
        'run1': dict(fl=((0.68, 0.74), (0.80, 0.94)), bl=((0.38, 0.76), (0.22, 0.90)), fa=((0.70, 0.40), (0.80, 0.30)), ba=((0.40, 0.44), (0.30, 0.54)), lean=4),
        'run2': dict(fl=((0.58, 0.78), (0.52, 0.97)), bl=((0.44, 0.78), (0.40, 0.97)), fa=((0.62, 0.46), (0.70, 0.54)), ba=((0.46, 0.42), (0.40, 0.30)), lean=2),
        'jump': dict(fl=((0.72, 0.62), (0.92, 0.66)), bl=((0.36, 0.70), (0.20, 0.62)), fa=((0.74, 0.30), (0.84, 0.18)), ba=((0.38, 0.40), (0.24, 0.34)), lean=10),
        'fall': dict(fl=((0.66, 0.80), (0.86, 0.90)), bl=((0.36, 0.82), (0.16, 0.90)), fa=((0.76, 0.52), (0.92, 0.62)), ba=((0.36, 0.52), (0.18, 0.60)), lean=28),
    }[frame]
    lw = 4.2 * s

    def limb(a, b, c, col):
        d.line([a, (W * b[0], H * b[1]), (W * c[0], H * c[1])], fill=col + (255,), width=int(lw), joint='curve')
    limb(hip, *poses['bl'], pants)
    limb(sh, *poses['ba'], skin)
    d.line([hip, sh], fill=shirt + (255,), width=int(9 * s))
    d.text(((hip[0] + sh[0]) / 2, (hip[1] + sh[1]) / 2), '3', font=font('jalnan', int(6 * s)), fill=(255, 255, 255, 255), anchor='mm')
    limb(hip, *poses['fl'], pants)
    limb(sh, *poses['fa'], skin)
    hx, hy = sh[0] + poses['lean'] * 0.3 * s, H * 0.18
    d.ellipse((hx - 6.5 * s, hy - 7 * s, hx + 6.5 * s, hy + 7 * s), fill=skin + (255,), outline=(40, 24, 16, 255), width=int(1 * s))
    d.chord((hx - 7 * s, hy - 8 * s, hx + 7 * s, hy + 4 * s), 180, 360, fill=(20, 18, 24, 255))
    d.rectangle((hx - 7 * s, hy - 3 * s, hx + 7 * s, hy - 1 * s), fill=(220, 30, 50, 255))
    if frame == 'fall':
        im = im.rotate(-20, resample=Image.BICUBIC, center=(W / 2, H * 0.9))
    return _fin(im, w, h, name)


def hurdle():
    name = 'hurdle'
    if _cached(name):
        return _cached(name)
    w, h = 30, 36
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    for x in (W * 0.18, W * 0.82):
        d.line([(x, H * 0.22), (x, H * 0.96)], fill=(200, 206, 220, 255), width=int(2 * s))
        d.line([(x - 4 * s, H * 0.96), (x + 4 * s, H * 0.96)], fill=(200, 206, 220, 255), width=int(2 * s))
    for i in range(5):
        x0 = W * 0.08 + i * W * 0.17
        d.rectangle((x0, H * 0.14, x0 + W * 0.17, H * 0.34), fill=((230, 40, 60) if i % 2 == 0 else (245, 245, 250)) + (255,))
    d.rectangle((W * 0.08, H * 0.14, W * 0.93, H * 0.34), outline=(30, 10, 14, 255), width=int(1 * s))
    return _fin(im, w, h, name)


def track(w=480, h=60):
    name = 'track_%d' % w
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    g = K._grad(im.size, (150, 50, 40), (90, 26, 20))
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    for y in (H * 0.08, H * 0.5):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 200), width=int(1.4 * s))
    d.line([(0, 0), (W, 0)], fill=(20, 10, 10, 255), width=int(2 * s))
    return _fin(im, w, h, name)


# ================================================================== 11. 벚꽃 촬영
def viewfinder(w=330, h=210):
    name = 'viewfinder'
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    L, t = 22 * s, 2.4 * s
    for (x, y, dx, dy) in ((0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)):
        d.line([(x + dx * t, y + dy * t), (x + dx * L, y + dy * t)], fill=(255, 255, 255, 240), width=int(t))
        d.line([(x + dx * t, y + dy * t), (x + dx * t, y + dy * L)], fill=(255, 255, 255, 240), width=int(t))
    c = (W / 2, H / 2)
    d.line([(c[0] - 10 * s, c[1]), (c[0] + 10 * s, c[1])], fill=(255, 255, 255, 200), width=int(1 * s))
    d.line([(c[0], c[1] - 10 * s), (c[0], c[1] + 10 * s)], fill=(255, 255, 255, 200), width=int(1 * s))
    d.ellipse((14 * s, 12 * s, 22 * s, 20 * s), fill=(255, 40, 60, 255))
    d.text((26 * s, 16 * s), 'REC', font=font('nsrb', int(8 * s)), fill=(255, 255, 255, 255), anchor='lm')
    for i in range(3):
        d.line([(W / 3 * (i + 1) if i < 2 else 0, 0), (W / 3 * (i + 1) if i < 2 else 0, H)], fill=(255, 255, 255, 40 if i < 2 else 0), width=int(0.6 * s))
        d.line([(0, H / 3 * (i + 1) if i < 2 else 0), (W, H / 3 * (i + 1) if i < 2 else 0)], fill=(255, 255, 255, 40 if i < 2 else 0), width=int(0.6 * s))
    return _fin(im, w, h, name)


def timing_bar(w=300, h=24):
    """왼쪽 끝→오른쪽 끝 막대. 가운데 정답 구간은 따로 그림(sweet zone)."""
    name = 'timing_bar'
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    box = (2 * s, 5 * s, W - 2 * s, H - 5 * s)
    d.rounded_rectangle(box, (box[3] - box[1]) / 2, fill=(6, 8, 22, 240), outline=(120, 140, 220, 255), width=int(1 * s))
    for i in range(1, 20):
        x = box[0] + (box[2] - box[0]) * i / 20
        d.line([(x, box[1] + 3 * s), (x, box[3] - 3 * s)], fill=(60, 80, 150, 120), width=int(0.5 * s))
    return _fin(im, w, h, name)


def sweet_zone(level):
    """level 0~4: 폭이 점점 좁아짐 (무대 px: 60,48,38,30,24)."""
    widths = [60, 48, 38, 30, 24]
    name = 'sweet_%d' % level
    if _cached(name):
        return _cached(name)
    w, h = widths[level], 14
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    g = Image.new('RGBA', im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for x in range(W):
        t = 1 - abs(x - W / 2) / (W / 2)
        gd.line([(x, 0), (x, H)], fill=(255, 120, 170, int(70 + 150 * t)))
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, W - 1, H - 1), H / 2, fill=255)
    g.putalpha(ImageChops.multiply(g.getchannel('A'), m))
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    d.line([(W / 2, 0), (W / 2, H)], fill=(255, 255, 255, 255), width=int(1 * s))
    return _fin(im, w, h, name)


def needle():
    name = 'needle'
    if _cached(name):
        return _cached(name)
    w, h = 10, 30
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    d.polygon([(W / 2, H * 0.30), (W * 0.9, 0), (W * 0.1, 0)], fill=(255, 255, 255, 255), outline=(10, 10, 20, 255))
    d.line([(W / 2, H * 0.28), (W / 2, H)], fill=(255, 255, 255, 255), width=int(1.6 * s))
    return _fin(im, w, h, name)


def polaroid(grade):
    """찍은 사진 느낌의 액자 (grade: S/A/B/C)."""
    name = 'polaroid_%s' % grade
    if _cached(name):
        return _cached(name)
    w, h = 90, 104
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rectangle((3 * s, 3 * s, W - 3 * s, H - 3 * s), fill=255)
    _fill(im, m, (250, 250, 252), (226, 230, 240))
    d = ImageDraw.Draw(im)
    d.rectangle((9 * s, 9 * s, W - 9 * s, H * 0.70), fill=(30, 26, 40, 255))
    rng = random.Random(ord(grade))
    n = {'S': 40, 'A': 28, 'B': 16, 'C': 6}[grade]
    for i in range(n):
        x, y, r = rng.uniform(12, W / s - 12) * s, rng.uniform(12, H * 0.68 / s) * s, rng.uniform(2, 4.5) * s
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, rng.randint(170, 210), rng.randint(200, 225), 230))
    _jtext(d, (W / 2, H * 0.84), {'S': '인생샷!', 'A': '잘 나왔다', 'B': '그럭저럭', 'C': '흔들렸다...'}[grade], 10 * s, (30, 40, 90, 255))
    _outline(im, m, (40, 44, 60), 1 * s)
    im = _shadow(im, m, (0, 3 * s), 3 * s)
    return _fin(im, w, h, name)


# ================================================================== 12. 연잎 순서 터치
def lotus_pad(n, done=False):
    name = 'lotus_%d_%d' % (n, done)
    if _cached(name):
        return _cached(name)
    w = h = 52
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((3 * s, 6 * s, W - 3 * s, H - 3 * s), fill=255)
    d.pieslice((3 * s, 6 * s, W - 3 * s, H - 3 * s), 280, 300, fill=0)
    _fill(im, m, (70, 160, 90), (24, 90, 50))
    d2 = ImageDraw.Draw(im)
    cx, cy = W / 2, (6 * s + H - 3 * s) / 2
    for k in range(9):
        a = math.radians(300 + k * 36)
        d2.line([(cx, cy), (cx + math.cos(a) * W * 0.42, cy + math.sin(a) * H * 0.40)], fill=(20, 70, 40, 160), width=int(0.6 * s))
    _outline(im, m, (8, 40, 20), 1.4 * s)
    if done:
        for k in range(8):
            a = k * math.pi / 4
            pm = Image.new('L', im.size, 0)
            px, py = cx + math.cos(a) * 7 * s, cy + math.sin(a) * 7 * s
            ImageDraw.Draw(pm).ellipse((px - 6 * s, py - 6 * s, px + 6 * s, py + 6 * s), fill=255)
            _fill(im, pm, (255, 210, 230), (240, 110, 160))
        d2 = ImageDraw.Draw(im)
        d2.ellipse((cx - 4 * s, cy - 4 * s, cx + 4 * s, cy + 4 * s), fill=(255, 220, 120, 255))
    else:
        d2.ellipse((cx - 11 * s, cy - 11 * s, cx + 11 * s, cy + 11 * s), fill=(6, 10, 30, 230), outline=(200, 214, 255, 255), width=int(1 * s))
        d2.text((cx, cy + 0.5 * s), str(n), font=font('jalnan', int(14 * s)), fill=(255, 255, 255, 255), anchor='mm')
    return _fin(im, w, h, name)


# ================================================================== 14. 가위바위보
def rps_hand(kind, side='me'):
    """kind: rock/paper/scissors, side: me(청색 소매, 오른쪽을 봄) / op(붉은 소매, 왼쪽을 봄). 손가락마다 외곽선."""
    name = 'rps2_%s_%s' % (kind, side)
    if _cached(name):
        return _cached(name)
    w, h = 96, 80
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    skin = (240, 204, 176)
    skin_d = (206, 160, 132)
    sleeve = (30, 56, 190) if side == 'me' else (180, 24, 50)
    line = (70, 36, 24)

    def part(box, r, rot=0, center=None):
        m = Image.new('L', im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255)
        if rot:
            m = m.rotate(rot, center=center, resample=Image.BICUBIC)
        _fill(im, m, skin, skin_d)
        _outline(im, m, line, 1.6 * s)
        return m
    # 소매
    sm = Image.new('L', im.size, 0)
    ImageDraw.Draw(sm).rounded_rectangle((0, H * 0.30, W * 0.26, H * 0.86), 5 * s, fill=255)
    _fill(im, sm, lerp(sleeve, (255, 255, 255), 0.18), sleeve)
    _outline(im, sm, (4, 4, 12), 1.4 * s)
    fx0 = W * 0.50       # 손가락 시작 x
    if kind == 'paper':
        part((W * 0.22, H * 0.30, W * 0.56, H * 0.84), 9 * s)                       # 손바닥
        for k in range(4):
            y = H * 0.22 + k * H * 0.15
            ln = [0.40, 0.44, 0.42, 0.34][k]
            part((fx0 - 4 * s, y, fx0 + W * ln, y + H * 0.13), 5 * s)
        part((W * 0.30, H * 0.06, W * 0.42, H * 0.40), 5 * s, rot=-18, center=(W * 0.36, H * 0.36))   # 엄지
    elif kind == 'rock':
        part((W * 0.22, H * 0.26, W * 0.62, H * 0.86), 12 * s)
        for k in range(4):
            y = H * 0.26 + k * H * 0.15
            part((W * 0.52, y, W * 0.72, y + H * 0.15), 6 * s)
        part((W * 0.34, H * 0.64, W * 0.66, H * 0.80), 6 * s)                        # 엄지 (앞쪽으로 감쌈)
    else:  # scissors
        part((W * 0.22, H * 0.30, W * 0.60, H * 0.86), 10 * s)
        part((fx0, H * 0.22, fx0 + W * 0.44, H * 0.35), 5 * s, rot=12, center=(fx0, H * 0.30))
        part((fx0, H * 0.38, fx0 + W * 0.46, H * 0.51), 5 * s, rot=-10, center=(fx0, H * 0.44))
        for k in range(2):
            y = H * 0.54 + k * H * 0.14
            part((W * 0.52, y, W * 0.68, y + H * 0.14), 5 * s)
        part((W * 0.34, H * 0.70, W * 0.62, H * 0.84), 6 * s)
    if side == 'op':
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return _fin(im, w, h, name)


# ================================================================== 15. 낚시
def fish_gauge(h=200):
    name = 'fish_gauge'
    if _cached(name):
        return _cached(name)
    w = 36
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((2 * s, 2 * s, W - 2 * s, H - 2 * s), 8 * s, fill=255)
    _fill(im, m, (10, 40, 90), (2, 10, 30))
    d = ImageDraw.Draw(im)
    for i in range(8):
        y = H * (i + 1) / 9
        d.arc((6 * s, y - 3 * s, W - 6 * s, y + 3 * s), 0, 180, fill=(80, 140, 230, 90), width=int(0.6 * s))
    d.rounded_rectangle((2 * s, 2 * s, W - 2 * s, H - 2 * s), 8 * s, outline=(140, 170, 250, 255), width=int(1.4 * s))
    return _fin(im, w, h, name)


def catch_bar(h=52, active=False):
    name = 'catch_bar_%d' % active
    if _cached(name):
        return _cached(name)
    w = 28
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 5 * s, fill=255)
    col = ((110, 160, 255), (40, 80, 230)) if active else ((70, 90, 150), (30, 40, 90))
    g = K._grad(im.size, col[0], col[1])
    g.putalpha(m.point(lambda v: v * 170 // 255))
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 5 * s, outline=(220, 230, 255, 255), width=int(1.2 * s))
    return _fin(im, w, h, name)


def fish_icon():
    name = 'fish_icon'
    if _cached(name):
        return _cached(name)
    w, h = 30, 20
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((W * 0.18, H * 0.15, W * 0.82, H * 0.85), fill=255)
    d.polygon([(W * 0.22, H * 0.5), (W * 0.02, H * 0.12), (W * 0.02, H * 0.88)], fill=255)
    _fill(im, m, (200, 220, 240), (90, 120, 160))
    _hl(im, m, 0.45, 90)
    _outline(im, m, (10, 20, 40), 1.2 * s)
    d = ImageDraw.Draw(im)
    d.ellipse((W * 0.66, H * 0.36, W * 0.74, H * 0.50), fill=(10, 10, 20, 255))
    return _fin(im, w, h, name)


def bobber():
    name = 'bobber'
    if _cached(name):
        return _cached(name)
    w, h = 16, 26
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    d.line([(W / 2, 0), (W / 2, H * 0.3)], fill=(220, 226, 240, 255), width=int(0.8 * s))
    d.ellipse((W * 0.15, H * 0.28, W * 0.85, H * 0.78), fill=(240, 40, 60, 255), outline=(30, 0, 6, 255), width=int(1 * s))
    d.chord((W * 0.15, H * 0.28, W * 0.85, H * 0.78), 0, 180, fill=(250, 250, 255, 255), outline=(30, 0, 6, 255))
    return _fin(im, w, h, name)


# ================================================================== 7. 퀴즈 카드 / 1. 조명
def quiz_card(state, w=128, h=70):
    """state: n(보통) / ok(정답) / no(오답)"""
    name = 'quiz_%s' % state
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    box = (3 * s, 3 * s, W - 3 * s, H - 3 * s)
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, 10 * s, fill=255)
    cols = {'n': ((24, 30, 64), (6, 8, 22), (90, 120, 230)), 'ok': ((20, 90, 60), (4, 34, 20), (90, 230, 150)),
            'no': ((110, 16, 34), (40, 4, 10), (255, 90, 110))}[state]
    _fill(im, m, cols[0], cols[1])
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, 10 * s, outline=cols[2] + (255,), width=int(1.6 * s))
    if state != 'n':
        im = _glow(im, m, cols[2], 5 * s, 230)
    return _fin(im, w, h, name)


def spotlight(w=160, h=300):
    name = 'spotlight'
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).polygon([(W * 0.47, 0), (W * 0.53, 0), (W, H), (0, H)], fill=255)
    g = Image.new('L', im.size, 0)
    gd = ImageDraw.Draw(g)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=int(110 * (1 - y / H) ** 0.8))
    m = ImageChops.multiply(m, g).filter(ImageFilter.GaussianBlur(W * 0.04))
    lay = Image.new('RGBA', im.size, (90, 140, 255, 255))
    lay.putalpha(m)
    im.alpha_composite(lay)
    return _fin(im, w, h, name)


# ================================================================== 미리보기
def preview(path):
    sheet = Image.new('RGBA', (1400, 1500), (0, 0, 0, 255))
    sheet.paste(vgradient((1400, 1500), (6, 8, 20), (20, 26, 60)).convert('RGBA'))
    items = ([rhythm_note(i) for i in range(4)] + [rhythm_receptor(i) for i in range(4)] + [rhythm_receptor(0, True)] +
             [ginkgo(k) for k in ('leaf', 'gold', 'dry')] + [basket(), arms(), tug_knob()] +
             [peach(k) for k in ('raw', 'ripe', 'bad')] + [crate('덜 익음', '←', 'green'), crate('잘 익음', '→', 'red'), crate('상함', '↓', 'gray')] +
             [cafe_card(i) for i in range(4)] + [cafe_card(2, True)] +
             [balloon(k) for k in BALLOON_COLS] + [crosshair(), burst()] +
             [maze_walls()[0], ballot_paper(), exit_flag()] +
             [hole_back(), mole(), mole('mole', True), mole('peach'), hole_front(), hammer(), hammer(True)] +
             [runner(f) for f in ('run1', 'run2', 'jump', 'fall')] + [hurdle()] +
             [timing_bar(), sweet_zone(0), needle(), polaroid('S'), polaroid('C')] +
             [lotus_pad(3), lotus_pad(7, True)] +
             [rps_hand(k) for k in ('rock', 'paper', 'scissors')] + [rps_hand('paper', 'op')] +
             [fish_gauge(), catch_bar(), catch_bar(active=True), fish_icon(), bobber()])
    x, y, rowh = 10, 10, 0
    for p in items:
        im = Image.open(p)
        if x + im.width > 1390:
            x, y = 10, y + rowh + 10
            rowh = 0
        sheet.alpha_composite(im, (x, y))
        x += im.width + 10
        rowh = max(rowh, im.height)
    sheet.convert('RGB').save(path)
