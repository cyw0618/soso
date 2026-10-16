# -*- coding: utf-8 -*-
"""새 미니게임 25종(16~40) 그림. mg_art 와 같은 방식(2배 해상도 저장, 크기 인자는 '무대 px')."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from art_common import *
import ui_kit as K
from mg_art import _cv, _fin, _cached, _fill, _outline, _glow, _shadow, _hl, _jtext, R2, SS

S_ = R2 * SS     # 무대 1px 당 그림 px


def _rr(d, box, r, **kw):
    d.rounded_rectangle(box, r, **kw)


def _mask(size):
    m = Image.new('L', size, 0)
    return m, ImageDraw.Draw(m)


def _text(d, xy, s, size, fill, fname='jalnan', anchor='mm'):
    if fname == 'jalnan' and ' ' in s:
        _jtext(d, xy, s, size, fill)
    else:
        d.text(xy, s, font=font(fname, int(size)), fill=fill, anchor=anchor)


# ================================================================== 공통: 카드
def card(label, w=56, h=78, kind='face', col=(30, 50, 160), sub=None, name=None):
    """흰 카드(face) 또는 뒷면(back). label 은 가운데 큰 글자."""
    name = name or 'card_%s_%s_%d_%d_%d_%d_%d' % (kind, label, w, h, *col)
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 2 * S_, W - 2 * S_, H - 3 * S_), 7 * S_, fill=255)
    if kind == 'back':
        _fill(im, m, (52, 84, 220), (14, 26, 96))
        d = ImageDraw.Draw(im)
        for k in range(-H, W, int(7 * S_)):
            d.line([(k, 0), (k + H, H)], fill=(120, 150, 255, 60), width=int(1.2 * S_))
        im.putalpha(ImageChops.multiply(im.getchannel('A'), m))
        d = ImageDraw.Draw(im)
        _rr(d, (6 * S_, 6 * S_, W - 6 * S_, H - 7 * S_), 5 * S_, outline=(170, 190, 255, 200), width=int(1.2 * S_))
        _text(d, (W / 2, H / 2), label or '?', 18 * S_, (220, 230, 255, 255))
    else:
        _fill(im, m, (252, 252, 255), (214, 222, 240))
        d = ImageDraw.Draw(im)
        _text(d, (W / 2, H / 2 + 1 * S_), label, (26 if len(label) < 2 else 22) * S_, col + (255,))
        if sub:
            _text(d, (9 * S_, 11 * S_), sub, 9 * S_, col + (255,))
            _text(d, (W - 9 * S_, H - 13 * S_), sub, 9 * S_, col + (255,))
    _outline(im, m, (6, 10, 30), 1.4 * S_)
    im = _shadow(im, m, (0, 2 * S_), 2 * S_, 130)
    return _fin(im, w, h, name)


def icon_card(icon, w=52, h=52, kind='face', name=None):
    """짝 맞추기 카드: 앞면은 흰 바탕에 아이콘."""
    name = name or 'icard_%s_%s_%d_%d' % (kind, icon, w, h)
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 2 * S_, W - 2 * S_, H - 3 * S_), 7 * S_, fill=255)
    if kind == 'back':
        _fill(im, m, (44, 72, 210), (12, 22, 84))
        d = ImageDraw.Draw(im)
        _text(d, (W / 2, H / 2), '?', 20 * S_, (200, 215, 255, 255))
    else:
        _fill(im, m, (250, 251, 255), (206, 216, 238))
        ic = Image.open(K.icon_img(icon, 30)).convert('RGBA')
        ic = ic.resize((int(30 * S_), int(30 * S_)), Image.LANCZOS)
        im.alpha_composite(ic, (int((W - ic.width) / 2), int((H - ic.height) / 2)))
    _outline(im, m, (6, 10, 30), 1.4 * S_)
    if kind == 'done':
        im = _glow(im, m, (60, 110, 255), 3 * S_, 220)
    return _fin(im, w, h, name)


def tile(w, h, top, bottom, edge=(6, 10, 30), r=5, label=None, lsize=None, lcol=(255, 255, 255), name=None, glow=None):
    name = name or 'tile_%d_%d_%s_%s_%s' % (w, h, '%d.%d.%d' % top, '%d.%d.%d' % bottom, label or '')
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (1.5 * S_, 1.5 * S_, W - 1.5 * S_, H - 2 * S_), r * S_, fill=255)
    _fill(im, m, top, bottom)
    _hl(im, m, 0.4, 50)
    _outline(im, m, edge, 1.2 * S_)
    if label:
        d = ImageDraw.Draw(im)
        _text(d, (W / 2, H / 2), label, (lsize or min(w, h) * 0.55) * S_, lcol + (255,))
    if glow:
        im = _glow(im, m, glow, 3 * S_, 220)
    return _fin(im, w, h, name)


# ================================================================== 30. 결투: 신호 글자, 총구 불꽃
def muzzle():
    name = 'muzzle'
    if _cached(name):
        return _cached(name)
    w = h = 44
    im = _cv(w, h)
    W = im.width
    d = ImageDraw.Draw(im)
    c = W / 2
    pts = []
    for k in range(16):
        a = k * math.pi / 8
        r = (20 if k % 2 == 0 else 8) * S_
        pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
    d.polygon(pts, fill=(255, 240, 220, 255))
    m = im.getchannel('A')
    im = _glow(im, m, (255, 120, 90), 4 * S_, 230)
    return _fin(im, w, h, name)


# ================================================================== 37. 떡 재료 아이콘
TTEOK = [('백설기', (250, 250, 250), (210, 214, 230)), ('인절미', (236, 206, 140), (196, 160, 90)),
         ('팥', (150, 40, 50), (90, 16, 24)), ('쑥', (120, 170, 90), (60, 110, 50)),
         ('꿀', (255, 196, 70), (220, 140, 20)), ('깨', (60, 54, 60), (20, 18, 24))]


def tteok_icon(k, size=34):
    nm, top, bot = TTEOK[k]
    name = 'tteok_%d_%d' % (k, size)
    if _cached(name):
        return _cached(name)
    im = _cv(size, size)
    W, H = im.size
    m, md = _mask(im.size)
    c = W / 2
    if k in (0, 1, 3):      # 떡 덩어리
        _rr(md, (W * 0.14, H * 0.28, W * 0.86, H * 0.76), 6 * S_, fill=255)
    elif k == 2:            # 팥알 무더기
        for dx, dy in ((-0.16, 0.08), (0.16, 0.08), (0, -0.1), (-0.05, 0.22), (0.2, -0.12), (-0.22, -0.1)):
            md.ellipse((c + (dx - 0.12) * W, c + (dy - 0.1) * H, c + (dx + 0.12) * W, c + (dy + 0.1) * H), fill=255)
    elif k == 4:            # 꿀 방울
        md.ellipse((W * 0.26, H * 0.36, W * 0.74, H * 0.84), fill=255)
        md.polygon([(W * 0.5, H * 0.1), (W * 0.29, H * 0.5), (W * 0.71, H * 0.5)], fill=255)
    else:                   # 깨 그릇
        md.chord((W * 0.12, H * 0.2, W * 0.88, H * 0.86), 0, 180, fill=255)
    _fill(im, m, top, bot)
    _hl(im, m, 0.4, 90)
    d = ImageDraw.Draw(im)
    if k == 1:
        rng = random.Random(1)
        for _ in range(40):
            x, y = rng.uniform(W * 0.18, W * 0.82), rng.uniform(H * 0.3, H * 0.74)
            d.ellipse((x - S_, y - S_, x + S_, y + S_), fill=(250, 230, 170, 255))
    if k == 3:
        d.line([(W * 0.3, H * 0.52), (W * 0.7, H * 0.52)], fill=(40, 80, 40, 255), width=int(1.2 * S_))
    if k == 5:
        rng = random.Random(5)
        for _ in range(26):
            x, y = rng.uniform(W * 0.22, W * 0.78), rng.uniform(H * 0.24, H * 0.5)
            d.ellipse((x - 1.2 * S_, y - 0.7 * S_, x + 1.2 * S_, y + 0.7 * S_), fill=(250, 240, 210, 255))
    _outline(im, m, (10, 8, 20), 1.2 * S_)
    return _fin(im, size, size, name)


def plate(w=150, h=40):
    name = 'plate_%d_%d' % (w, h)
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.ellipse((2 * S_, 4 * S_, W - 2 * S_, H - 4 * S_), fill=255)
    _fill(im, m, (240, 244, 255), (170, 184, 220))
    d = ImageDraw.Draw(im)
    d.ellipse((W * 0.12, H * 0.25, W * 0.88, H * 0.72), outline=(150, 164, 200, 255), width=int(1.4 * S_))
    _outline(im, m, (10, 12, 30), 1.2 * S_)
    im = _shadow(im, m, (0, 2 * S_), 3 * S_, 150)
    return _fin(im, w, h, name)


def speech(w, h, name=None):
    name = name or 'speech_%d_%d' % (w, h)
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 2 * S_, W - 2 * S_, H - 12 * S_), 10 * S_, fill=255)
    md.polygon([(W * 0.18, H - 13 * S_), (W * 0.30, H - 13 * S_), (W * 0.14, H - 2 * S_)], fill=255)
    _fill(im, m, (250, 252, 255), (214, 222, 242))
    _outline(im, m, (8, 12, 34), 1.4 * S_)
    im = _shadow(im, m, (0, 2 * S_), 2 * S_, 120)
    return _fin(im, w, h, name)


# ================================================================== 24. 숫자 야구: 표시 칸
def digit_box(state='empty', w=34, h=40):
    name = 'digitbox_%s' % state
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 2 * S_, W - 2 * S_, H - 2 * S_), 6 * S_, fill=255)
    cols = {'empty': ((22, 30, 70), (10, 14, 40)), 'on': ((60, 100, 240), (20, 40, 150))}[state]
    _fill(im, m, *cols)
    _outline(im, m, (120, 150, 255) if state == 'on' else (60, 80, 160), 1.4 * S_)
    return _fin(im, w, h, name)


# ================================================================== 32. 폐교 방탈출
ROOM_COLS = {'빨강': ((235, 70, 90), (150, 20, 40)), '파랑': ((70, 130, 255), (20, 50, 170)),
             '초록': ((70, 200, 120), (20, 110, 60)), '보라': ((170, 110, 255), (80, 40, 170))}
ROOM_COL_NAMES = ['빨강', '파랑', '초록', '보라']


def _wall(im, d, W, H, floor_y):
    """어두운 교실 벽 + 나무 바닥 (밤)."""
    for y in range(H):
        t = y / H
        if y < floor_y:
            c = (int(22 + 10 * t), int(30 + 14 * t), int(62 + 20 * t))
        else:
            k = (y - floor_y) / max(1, H - floor_y)
            c = (int(44 - 14 * k), int(34 - 10 * k), int(42 - 12 * k))
        d.line([(0, y), (W, y)], fill=c + (255,))
    for k in range(0, W, int(26 * S_)):
        d.line([(k, floor_y), (k - 40 * S_, H)], fill=(30, 22, 30, 255), width=int(1 * S_))
    d.line([(0, floor_y), (W, floor_y)], fill=(70, 80, 130, 255), width=int(2 * S_))
    # 걸레받이
    d.rectangle((0, floor_y - 6 * S_, W, floor_y), fill=(16, 20, 44, 255))


def room_bg(view):
    """방탈출 교실 배경 (480x270). view: 'front' (칠판·교탁·문) / 'back' (책장·창문·사물함)."""
    name = 'room_' + view
    if _cached(name):
        return _cached(name)
    w, h = 480, 270
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    fy = 190 * S_
    _wall(im, d, W, H, fy)
    if view == 'front':
        # 칠판
        bx0, by0, bx1, by1 = 70 * S_, 36 * S_, 300 * S_, 128 * S_
        d.rectangle((bx0 - 6 * S_, by0 - 6 * S_, bx1 + 6 * S_, by1 + 6 * S_), fill=(70, 52, 50, 255))
        d.rectangle((bx0, by0, bx1, by1), fill=(22, 52, 44, 255))
        for k in range(14):
            rr = random.Random(k)
            x = bx0 + rr.uniform(4 * S_, bx1 - bx0 - 40 * S_)
            y = by0 + rr.uniform(56, 86) * S_
            d.line([(x, y), (x + rr.uniform(10, 30) * S_, y + rr.uniform(-3, 3) * S_)], fill=(60, 90, 80, 110), width=int(S_))
        f1 = font('nanum', int(11 * S_))
        d.text(((bx0 + bx1) / 2, by0 + 26 * S_), '서랍은 멈춘 시각을 기억한다', font=f1, fill=(230, 240, 230, 255), anchor='mm')
        d.text(((bx0 + bx1) / 2, by0 + 48 * S_), '(시·분 네 자리)', font=font('nanum', int(9 * S_)), fill=(200, 215, 205, 230), anchor='mm')
        d.text(((bx0 + bx1) / 2, by0 + 72 * S_), '빛은 숨은 것을 드러낸다', font=font('nanum', int(9 * S_)), fill=(190, 205, 200, 200), anchor='mm')
        d.rectangle((bx0, by1 + 4 * S_, bx1, by1 + 9 * S_), fill=(80, 60, 56, 255))
        # 교탁
        d.rectangle((110 * S_, 168 * S_, 260 * S_, 206 * S_), fill=(90, 62, 50, 255))
        d.rectangle((110 * S_, 160 * S_, 260 * S_, 170 * S_), fill=(120, 86, 66, 255))
        # 문틀
        d.rectangle((362 * S_, 70 * S_, 448 * S_, 196 * S_), fill=(30, 24, 30, 255))
        # 시계 자리 (그림은 따로)
    else:
        # 책장
        d.rectangle((24 * S_, 40 * S_, 170 * S_, 196 * S_), fill=(80, 56, 46, 255))
        for k in range(4):
            y = (78 + k * 38) * S_
            d.rectangle((30 * S_, y, 164 * S_, y + 6 * S_), fill=(110, 78, 60, 255))
        d.rectangle((30 * S_, 46 * S_, 164 * S_, 76 * S_), fill=(40, 28, 26, 255))
        for k in range(3):
            y = (84 + k * 38) * S_
            d.rectangle((30 * S_, y, 164 * S_, y + 30 * S_), fill=(40, 28, 26, 255))
        # 오래된 책들 (장식)
        rng = random.Random(7)
        for k in range(3):
            y = (84 + k * 38) * S_
            x = 34 * S_
            while x < 158 * S_:
                bw = rng.uniform(6, 11) * S_
                c = rng.choice([(70, 60, 70), (60, 66, 90), (90, 70, 60), (50, 60, 60)])
                d.rectangle((x, y + rng.uniform(2, 8) * S_, x + bw, y + 30 * S_), fill=c + (255,))
                x += bw + 1.5 * S_
        # 창문 (밤하늘)
        wx0, wy0, wx1, wy1 = 200 * S_, 40 * S_, 330 * S_, 130 * S_
        d.rectangle((wx0 - 6 * S_, wy0 - 6 * S_, wx1 + 6 * S_, wy1 + 6 * S_), fill=(60, 64, 90, 255))
        for y in range(int(wy0), int(wy1)):
            t = (y - wy0) / (wy1 - wy0)
            d.line([(wx0, y), (wx1, y)], fill=(int(10 + 20 * t), int(16 + 30 * t), int(50 + 60 * t), 255))
        d.ellipse((290 * S_, 52 * S_, 312 * S_, 74 * S_), fill=(220, 230, 255, 255))
        d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(60, 64, 90, 255), width=int(4 * S_))
        d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=(60, 64, 90, 255), width=int(4 * S_))
        d.line([(wx0 + 8 * S_, wy0 + 10 * S_), (wx0 + 40 * S_, wy0 + 50 * S_)], fill=(200, 210, 240, 90), width=int(S_))
    # 어둡게 모서리
    v = Image.new('L', (W // 8, H // 8), 0)
    vd = ImageDraw.Draw(v)
    for k in range(18):
        vd.rectangle((k, k, W // 8 - 1 - k, H // 8 - 1 - k), outline=int(140 * (1 - k / 18) ** 2))
    v = v.resize((W, H)).filter(ImageFilter.GaussianBlur(20 * S_))
    dark = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    dark.putalpha(v)
    im.alpha_composite(dark)
    return _fin(im, w, h, name)


def room_drawer(state):
    name = 'room_drawer_' + state
    if _cached(name):
        return _cached(name)
    w, h = 64, 26 if state == 'closed' else 34
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.rectangle((2 * S_, 2 * S_, W - 2 * S_, H - 2 * S_), fill=255)
    _fill(im, m, (140, 100, 76), (96, 64, 50))
    d = ImageDraw.Draw(im)
    if state == 'closed':
        d.rectangle((W / 2 - 8 * S_, H / 2 - 2 * S_, W / 2 + 8 * S_, H / 2 + 2 * S_), fill=(210, 200, 180, 255))
        d.ellipse((W - 18 * S_, H / 2 - 5 * S_, W - 8 * S_, H / 2 + 5 * S_), fill=(200, 180, 90, 255))
    else:
        d.rectangle((6 * S_, 4 * S_, W - 6 * S_, H - 12 * S_), fill=(30, 20, 20, 255))
    _outline(im, m, (20, 12, 10), 1.2 * S_)
    return _fin(im, w, h, name)


def room_door(state):
    name = 'room_door_' + state
    if _cached(name):
        return _cached(name)
    w, h = 80, 120
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.rectangle((2 * S_, 2 * S_, W - 2 * S_, H - 2 * S_), fill=255)
    if state == 'open':
        _fill(im, m, (200, 220, 255), (120, 150, 230))
        d = ImageDraw.Draw(im)
        d.polygon([(2 * S_, 2 * S_), (22 * S_, 12 * S_), (22 * S_, H - 12 * S_), (2 * S_, H - 2 * S_)], fill=(90, 70, 60, 255))
        im = _glow(im, m, (160, 190, 255), 6 * S_, 230)
    else:
        _fill(im, m, (110, 82, 70), (70, 50, 46))
        d = ImageDraw.Draw(im)
        d.rectangle((12 * S_, 12 * S_, W - 12 * S_, 46 * S_), fill=(50, 70, 120, 255))
        d.rectangle((14 * S_, 14 * S_, W - 14 * S_, 44 * S_), fill=(30, 40, 80, 255))
        d.ellipse((W - 22 * S_, 62 * S_, W - 10 * S_, 74 * S_), fill=(220, 200, 120, 255))
        d.rectangle((W - 20 * S_, 78 * S_, W - 12 * S_, 92 * S_), fill=(40, 40, 50, 255))
        d.rectangle((W - 18 * S_, 80 * S_, W - 14 * S_, 90 * S_), fill=(110, 230, 140, 255))
    _outline(im, m, (14, 10, 10), 1.4 * S_)
    return _fin(im, w, h, name)


def room_clock():
    name = 'room_clock'
    if _cached(name):
        return _cached(name)
    w = h = 52
    im = _cv(w, h)
    W = im.width
    c = W / 2
    m, md = _mask(im.size)
    md.ellipse((2 * S_, 2 * S_, W - 2 * S_, W - 2 * S_), fill=255)
    _fill(im, m, (240, 240, 230), (200, 200, 190))
    d = ImageDraw.Draw(im)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        r0, r1 = 19 * S_, (22 if k % 3 == 0 else 21) * S_
        d.line([(c + math.cos(a) * r0, c + math.sin(a) * r0), (c + math.cos(a) * r1, c + math.sin(a) * r1)],
               fill=(30, 30, 40, 255), width=int((1.6 if k % 3 == 0 else 1.0) * S_))
        n = 12 if k == 0 else k
        r2 = 14.5 * S_
        d.text((c + math.cos(a) * r2, c + math.sin(a) * r2), str(n), font=font('nsrb', int(6 * S_)), fill=(30, 30, 50, 255), anchor='mm')
    _outline(im, m, (70, 50, 40), 2.2 * S_)
    return _fin(im, w, h, name)


def room_hand(kind):
    """시계 바늘: 위(12시)를 가리키는 그림. 회전 중심은 그림 가운데라서, 길이 두 배 캔버스의 가운데에서 위로 뻗게 그린다."""
    name = 'room_hand_' + kind
    if _cached(name):
        return _cached(name)
    L = 13 if kind == 'h' else 19
    w, h = 8, L * 2
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    wd = (2.6 if kind == 'h' else 1.6) * S_
    d.rounded_rectangle((W / 2 - wd / 2, 1 * S_, W / 2 + wd / 2, H / 2 + 1 * S_), wd / 2, fill=(20, 20, 30, 255))
    d.ellipse((W / 2 - 2 * S_, H / 2 - 2 * S_, W / 2 + 2 * S_, H / 2 + 2 * S_), fill=(160, 30, 40, 255))
    return _fin(im, w, h, name)


def room_book(col):
    name = 'room_book_%s' % ROOM_COL_NAMES.index(col)
    if _cached(name):
        return _cached(name)
    w, h = 16, 34
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.rectangle((1.5 * S_, 1.5 * S_, W - 1.5 * S_, H - 1.5 * S_), fill=255)
    _fill(im, m, *ROOM_COLS[col])
    d = ImageDraw.Draw(im)
    for y in (6, H / S_ - 7):
        d.line([(3 * S_, y * S_), (W - 3 * S_, y * S_)], fill=(255, 255, 255, 120), width=int(1.2 * S_))
    _outline(im, m, (10, 8, 16), 1 * S_)
    return _fin(im, w, h, name)


def uv_mark(n):
    name = 'uv_mark_%d' % n
    if _cached(name):
        return _cached(name)
    w = h = 18
    im = _cv(w, h)
    W = im.width
    d = ImageDraw.Draw(im)
    d.text((W / 2, W / 2), str(n), font=font('jalnan', int(13 * S_)), fill=(200, 140, 255, 255), anchor='mm')
    im = _glow(im, im.getchannel('A'), (170, 90, 255), 2.5 * S_, 255)
    return _fin(im, w, h, name)


def room_locker(state, col_dots=True):
    name = 'room_locker_' + state
    if _cached(name):
        return _cached(name)
    w, h = 62, 124
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.rectangle((2 * S_, 2 * S_, W - 2 * S_, H - 2 * S_), fill=255)
    _fill(im, m, (90, 110, 150), (50, 64, 100))
    d = ImageDraw.Draw(im)
    if state == 'open':
        d.rectangle((6 * S_, 6 * S_, W - 6 * S_, H - 6 * S_), fill=(16, 20, 34, 255))
        d.rectangle((6 * S_, 50 * S_, W - 6 * S_, 53 * S_), fill=(70, 80, 110, 255))
    else:
        for k in range(4):
            d.line([(14 * S_, (16 + k * 5) * S_), (W - 14 * S_, (16 + k * 5) * S_)], fill=(30, 36, 60, 255), width=int(1.4 * S_))
        d.rectangle((W / 2 - 16 * S_, 56 * S_, W / 2 + 16 * S_, 70 * S_), fill=(30, 30, 40, 255))
        for k, cn in enumerate(['빨강', '파랑', '초록']):
            x = W / 2 - 10 * S_ + k * 10 * S_
            d.ellipse((x - 3 * S_, 60 * S_, x + 3 * S_, 66 * S_), fill=(120, 120, 140, 255))
    _outline(im, m, (14, 16, 30), 1.4 * S_)
    return _fin(im, w, h, name)


def room_trash():
    name = 'room_trash'
    if _cached(name):
        return _cached(name)
    w, h = 40, 44
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.polygon([(4 * S_, 8 * S_), (W - 4 * S_, 8 * S_), (W - 8 * S_, H - 2 * S_), (8 * S_, H - 2 * S_)], fill=255)
    _fill(im, m, (120, 130, 150), (70, 78, 96))
    d = ImageDraw.Draw(im)
    for k in range(4):
        x = (10 + k * 7) * S_
        d.line([(x, 12 * S_), (x + 1 * S_, H - 6 * S_)], fill=(60, 66, 84, 255), width=int(1.2 * S_))
    d.ellipse((10 * S_, 2 * S_, 26 * S_, 12 * S_), fill=(230, 230, 220, 255))
    _outline(im, m, (14, 16, 30), 1.2 * S_)
    return _fin(im, w, h, name)


def room_chair():
    name = 'room_chair'
    if _cached(name):
        return _cached(name)
    w, h = 30, 40
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    col = (150, 104, 74, 255)
    leg = (60, 64, 80, 255)
    d.rectangle((5 * S_, 2 * S_, W - 5 * S_, 16 * S_), fill=col)
    d.rectangle((3 * S_, 18 * S_, W - 3 * S_, 23 * S_), fill=col)
    for x in (5, 9, W / S_ - 9, W / S_ - 5):
        d.rectangle(((x - 1) * S_, 23 * S_, (x + 1) * S_, (H / S_ - 1) * S_), fill=leg)
    d.rectangle((4 * S_, 16 * S_, 7 * S_, 19 * S_), fill=leg)
    d.rectangle((W - 7 * S_, 16 * S_, W - 4 * S_, 19 * S_), fill=leg)
    return _fin(im, w, h, name)


def room_item(kind, sel=False):
    """인벤토리 칸 + 아이템. kind: none/light/key/note/paper"""
    name = 'room_item_%s_%d' % (kind, sel)
    if _cached(name):
        return _cached(name)
    w = h = 40
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 2 * S_, W - 2 * S_, H - 2 * S_), 6 * S_, fill=255)
    _fill(im, m, (40, 60, 150) if sel else (20, 28, 64), (16, 24, 80) if sel else (10, 14, 36))
    _outline(im, m, (150, 180, 255) if sel else (60, 76, 140), (2 if sel else 1.2) * S_)
    d = ImageDraw.Draw(im)
    c = W / 2
    if kind == 'light':
        d.rectangle((c - 12 * S_, c - 3 * S_, c + 6 * S_, c + 3 * S_), fill=(200, 200, 210, 255))
        d.polygon([(c + 6 * S_, c - 6 * S_), (c + 13 * S_, c - 8 * S_), (c + 13 * S_, c + 8 * S_), (c + 6 * S_, c + 6 * S_)], fill=(230, 230, 240, 255))
        d.ellipse((c + 9 * S_, c - 4 * S_, c + 15 * S_, c + 4 * S_), fill=(190, 130, 255, 255))
    elif kind == 'key':
        d.ellipse((c - 12 * S_, c - 6 * S_, c - 2 * S_, c + 4 * S_), outline=(240, 210, 120, 255), width=int(2.6 * S_))
        d.rectangle((c - 3 * S_, c - 2 * S_, c + 12 * S_, c + 1 * S_), fill=(240, 210, 120, 255))
        d.rectangle((c + 6 * S_, c + 1 * S_, c + 8 * S_, c + 5 * S_), fill=(240, 210, 120, 255))
        d.rectangle((c + 10 * S_, c + 1 * S_, c + 12 * S_, c + 4 * S_), fill=(240, 210, 120, 255))
    elif kind == 'note':
        d.rectangle((c - 9 * S_, c - 11 * S_, c + 9 * S_, c + 11 * S_), fill=(250, 245, 220, 255))
        for k in range(4):
            d.line([(c - 6 * S_, c + (-6 + k * 4) * S_), (c + 6 * S_, c + (-6 + k * 4) * S_)], fill=(90, 100, 140, 255), width=int(S_))
    elif kind == 'paper':
        d.polygon([(c - 10 * S_, c - 6 * S_), (c - 2 * S_, c - 11 * S_), (c + 9 * S_, c - 7 * S_), (c + 11 * S_, c + 5 * S_),
                   (c + 2 * S_, c + 11 * S_), (c - 9 * S_, c + 7 * S_)], fill=(230, 226, 210, 255))
        d.line([(c - 6 * S_, c - 3 * S_), (c + 5 * S_, c + 2 * S_)], fill=(150, 146, 140, 255), width=int(S_))
        d.line([(c - 3 * S_, c + 5 * S_), (c + 6 * S_, c - 5 * S_)], fill=(150, 146, 140, 255), width=int(S_))
    return _fin(im, w, h, name)


def color_dial(col):
    name = 'color_dial_%d' % ROOM_COL_NAMES.index(col)
    if _cached(name):
        return _cached(name)
    w = h = 44
    im = _cv(w, h)
    W = im.width
    m, md = _mask(im.size)
    md.ellipse((3 * S_, 3 * S_, W - 3 * S_, W - 3 * S_), fill=255)
    _fill(im, m, *ROOM_COLS[col])
    _hl(im, m, 0.4, 90)
    _outline(im, m, (230, 236, 255), 1.6 * S_)
    d = ImageDraw.Draw(im)
    d.text((W / 2, W / 2), col, font=font('nanum', int(9 * S_)), fill=(255, 255, 255, 255), anchor='mm')
    return _fin(im, w, h, name)


def flash_cone():
    name = 'flash_cone'
    if _cached(name):
        return _cached(name)
    w, h = 170, 170
    im = _cv(w, h)
    W, H = im.size
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).ellipse((10 * S_, 10 * S_, W - 10 * S_, H - 10 * S_), fill=150)
    m = m.filter(ImageFilter.GaussianBlur(16 * S_))
    lay = Image.new('RGBA', im.size, (170, 120, 255, 255))
    lay.putalpha(m)
    im.alpha_composite(lay)
    return _fin(im, w, h, name)


# ================================================================== 16. 계단
def stair_block():
    return tile(38, 14, (150, 160, 200), (80, 90, 140), edge=(10, 14, 34), r=3, name='stair_block')


# ================================================================== 17. 드론 / 나무 기둥
def drone():
    name = 'drone'
    if _cached(name):
        return _cached(name)
    w, h = 64, 46
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    for x in (10, 54):
        d.rectangle(((x - 9) * S_, 6 * S_, (x + 9) * S_, 8 * S_), fill=(200, 210, 240, 255))
        d.rectangle(((x - 1) * S_, 7 * S_, (x + 1) * S_, 14 * S_), fill=(60, 70, 100, 255))
    m, md = _mask(im.size)
    _rr(md, (12 * S_, 12 * S_, 52 * S_, 24 * S_), 5 * S_, fill=255)
    _fill(im, m, (90, 130, 255), (30, 60, 190))
    _hl(im, m, 0.5, 90)
    _outline(im, m, (8, 12, 40), 1.2 * S_)
    d = ImageDraw.Draw(im)
    d.ellipse((28 * S_, 15 * S_, 36 * S_, 22 * S_), fill=(180, 230, 255, 255))
    # 현수막
    d.line([(32 * S_, 24 * S_), (32 * S_, 28 * S_)], fill=(200, 200, 220, 255), width=int(S_))
    d.rectangle((12 * S_, 28 * S_, 52 * S_, 42 * S_), fill=(240, 244, 255, 255))
    d.text((32 * S_, 35 * S_), '막내 화이팅', font=font('nanum', int(7 * S_)), fill=(40, 60, 170, 255), anchor='mm')
    return _fin(im, w, h, name)


def tree_gate(gap=88, h=420):
    name = 'tree_gate_%d' % gap
    if _cached(name):
        return _cached(name)
    w = 56
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    c = H / 2
    g = gap / 2 * S_
    md.rectangle((10 * S_, 0, W - 10 * S_, c - g), fill=255)
    md.rectangle((10 * S_, c + g, W - 10 * S_, H), fill=255)
    _fill(im, m, (110, 80, 70), (70, 48, 44))
    d = ImageDraw.Draw(im)
    for y in range(0, H, int(14 * S_)):
        d.line([(12 * S_, y), (W - 12 * S_, y + 6 * S_)], fill=(60, 40, 36, 255), width=int(S_))
    im.putalpha(ImageChops.multiply(im.getchannel('A'), m))
    # 끝부분 잎
    m2, md2 = _mask(im.size)
    md2.ellipse((0, c - g - 18 * S_, W, c - g + 4 * S_), fill=255)
    md2.ellipse((0, c + g - 4 * S_, W, c + g + 18 * S_), fill=255)
    _fill(im, m2, (50, 140, 110), (20, 80, 70))
    _outline(im, ImageChops.lighter(m, m2), (8, 14, 20), 1.4 * S_)
    return _fin(im, w, h, name)


# ================================================================== 18. 삼목: 바둑판과 돌
def go_board():
    name = 'go_board3'
    if _cached(name):
        return _cached(name)
    w = h = 190
    im = _cv(w, h)
    W = im.width
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 2 * S_, W - 2 * S_, W - 2 * S_), 8 * S_, fill=255)
    _fill(im, m, (220, 180, 120), (180, 136, 80))
    d = ImageDraw.Draw(im)
    for k in range(4):
        p = (8 + k * 58) * S_
        d.line([(p, 8 * S_), (p, W - 8 * S_)], fill=(70, 46, 20, 255), width=int(1.6 * S_))
        d.line([(8 * S_, p), (W - 8 * S_, p)], fill=(70, 46, 20, 255), width=int(1.6 * S_))
    _outline(im, m, (40, 24, 10), 1.6 * S_)
    im = _shadow(im, m, (0, 3 * S_), 4 * S_, 160)
    return _fin(im, w, h, name)


def go_stone(kind):
    name = 'go_stone_%s' % kind
    if _cached(name):
        return _cached(name)
    w = h = 50
    im = _cv(w, h)
    W = im.width
    if kind in ('b', 'w', 'bw', 'ww'):
        m, md = _mask(im.size)
        md.ellipse((4 * S_, 4 * S_, W - 4 * S_, W - 4 * S_), fill=255)
        if kind[0] == 'b':
            _fill(im, m, (70, 74, 90), (8, 8, 14))
        else:
            _fill(im, m, (255, 255, 255), (200, 204, 216))
        _hl(im, m, 0.45, 120)
        _outline(im, m, (0, 0, 0), 1 * S_)
        if len(kind) == 2:
            im = _glow(im, m, (80, 140, 255), 4 * S_, 255)
        im = _shadow(im, m, (1.5 * S_, 2.5 * S_), 2 * S_, 140)
    else:   # 빈칸 (클릭용 거의 투명)
        d = ImageDraw.Draw(im)
        d.ellipse((4 * S_, 4 * S_, W - 4 * S_, W - 4 * S_), fill=(255, 255, 255, 2))
    return _fin(im, w, h, name)


# ================================================================== 23. 과일 상자 (폭마다 모양)
def crate_w(width, h=16):
    name = 'crate_%d' % width
    if _cached(name):
        return _cached(name)
    w = max(4, width)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.rectangle((0, 0, W, H), fill=255)
    _fill(im, m, (200, 150, 96), (150, 100, 60))
    d = ImageDraw.Draw(im)
    d.line([(0, H * 0.5), (W, H * 0.5)], fill=(120, 80, 46, 255), width=int(1.2 * S_))
    for x in range(int(6 * S_), int(W), int(12 * S_)):
        d.ellipse((x - 2.6 * S_, H * 0.12, x + 2.6 * S_, H * 0.12 + 5.2 * S_), fill=(255, 130, 150, 255))
    _outline(im, m, (60, 34, 18), 1.2 * S_)
    return _fin(im, w, h, name)


def truck_bed(w=150, h=30):
    name = 'truck_bed_%d' % w
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.rectangle((0, 0, W, H * 0.6), fill=255)
    md.ellipse((W * 0.1, H * 0.35, W * 0.28, H), fill=255)
    md.ellipse((W * 0.72, H * 0.35, W * 0.9, H), fill=255)
    _fill(im, m, (70, 110, 220), (30, 50, 140))
    d = ImageDraw.Draw(im)
    for cx in (W * 0.19, W * 0.81):
        d.ellipse((cx - 6 * S_, H * 0.55, cx + 6 * S_, H * 0.55 + 12 * S_), fill=(20, 20, 30, 255))
    _outline(im, m, (8, 12, 40), 1.2 * S_)
    return _fin(im, w, h, name)


# ================================================================== 25. 제기, 차는 사람
def jegi():
    name = 'jegi'
    if _cached(name):
        return _cached(name)
    w, h = 24, 32
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    for k in range(9):
        a = math.radians(-60 + k * 15)
        d.line([(W / 2, H * 0.62), (W / 2 + math.sin(a) * 11 * S_, H * 0.62 - math.cos(a) * 20 * S_)],
               fill=[(255, 90, 120), (90, 140, 255), (255, 255, 255)][k % 3] + (255,), width=int(2 * S_))
    d.ellipse((W / 2 - 6 * S_, H * 0.62 - 3 * S_, W / 2 + 6 * S_, H * 0.62 + 7 * S_), fill=(230, 210, 120, 255))
    d.ellipse((W / 2 - 3 * S_, H * 0.62 - 1 * S_, W / 2 + 3 * S_, H * 0.62 + 4 * S_), fill=(120, 90, 40, 255))
    return _fin(im, w, h, name)


def kicker(pose):
    """제기 차는 사람 (옆모습, 단순한 실루엣). pose: stand / kick"""
    name = 'kicker_' + pose
    if _cached(name):
        return _cached(name)
    w, h = 50, 80
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    body = (40, 70, 200, 255)
    skin = (240, 210, 180, 255)
    d.ellipse((17 * S_, 2 * S_, 33 * S_, 18 * S_), fill=skin)
    d.rectangle((16 * S_, 2 * S_, 34 * S_, 8 * S_), fill=(30, 26, 30, 255))
    d.rounded_rectangle((15 * S_, 18 * S_, 35 * S_, 46 * S_), 6 * S_, fill=body)
    d.line([(16 * S_, 24 * S_), (6 * S_, 38 * S_)], fill=body, width=int(5 * S_))
    d.line([(34 * S_, 24 * S_), (44 * S_, 36 * S_)], fill=body, width=int(5 * S_))
    pants = (30, 34, 60, 255)
    d.line([(21 * S_, 45 * S_), (19 * S_, 78 * S_)], fill=pants, width=int(6 * S_))
    if pose == 'kick':
        d.line([(29 * S_, 45 * S_), (40 * S_, 58 * S_), (34 * S_, 66 * S_)], fill=pants, width=int(6 * S_), joint='curve')
        d.ellipse((28 * S_, 62 * S_, 40 * S_, 70 * S_), fill=(240, 240, 250, 255))
    else:
        d.line([(29 * S_, 45 * S_), (31 * S_, 78 * S_)], fill=pants, width=int(6 * S_))
    d.ellipse((13 * S_, 75 * S_, 25 * S_, 80 * S_), fill=(240, 240, 250, 255))
    if pose != 'kick':
        d.ellipse((26 * S_, 75 * S_, 38 * S_, 80 * S_), fill=(240, 240, 250, 255))
    return _fin(im, w, h, name)


# ================================================================== 19. 투호: 화살, 항아리
def tuho_arrow():
    name = 'tuho_arrow'
    if _cached(name):
        return _cached(name)
    w, h = 44, 10
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    d.rectangle((4 * S_, H / 2 - 1 * S_, W - 8 * S_, H / 2 + 1 * S_), fill=(200, 150, 90, 255))
    d.polygon([(W - 9 * S_, H / 2 - 3 * S_), (W - 1 * S_, H / 2), (W - 9 * S_, H / 2 + 3 * S_)], fill=(220, 225, 240, 255))
    for k in range(3):
        x = (5 + k * 3) * S_
        d.polygon([(x, H / 2), (x + 4 * S_, H / 2 - 4 * S_), (x + 6 * S_, H / 2 - 4 * S_), (x + 2 * S_, H / 2)], fill=(230, 70, 90, 255))
        d.polygon([(x, H / 2), (x + 4 * S_, H / 2 + 4 * S_), (x + 6 * S_, H / 2 + 4 * S_), (x + 2 * S_, H / 2)], fill=(230, 70, 90, 255))
    return _fin(im, w, h, name)


def tuho_jar(front=False):
    """항아리. front=True 면 입구 앞쪽 테두리만 (화살이 들어간 것처럼 보이게)."""
    name = 'tuho_jar_%d' % front
    if _cached(name):
        return _cached(name)
    w, h = 54, 70
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    if not front:
        md.ellipse((4 * S_, 18 * S_, W - 4 * S_, H - 2 * S_), fill=255)
        md.rectangle((14 * S_, 6 * S_, W - 14 * S_, 26 * S_), fill=255)
        _fill(im, m, (70, 100, 200), (24, 40, 110))
        _hl(im, m, 0.4, 80)
        d = ImageDraw.Draw(im)
        d.ellipse((12 * S_, 2 * S_, W - 12 * S_, 12 * S_), fill=(10, 14, 30, 255))
        for k in range(3):
            y = (36 + k * 8) * S_
            d.arc((8 * S_, y - 10 * S_, W - 8 * S_, y + 10 * S_), 20, 160, fill=(150, 180, 255, 160), width=int(1.2 * S_))
        _outline(im, m, (6, 10, 30), 1.4 * S_)
    else:
        d = ImageDraw.Draw(im)
        d.arc((12 * S_, 2 * S_, W - 12 * S_, 12 * S_), 0, 180, fill=(110, 140, 230, 255), width=int(2.2 * S_))
    return _fin(im, w, h, name)


# ================================================================== 20. 슬라이딩 퍼즐 조각 (숲길 그림)
def puzzle_tiles(n=3, size=64):
    """place_20 배경 가운데를 잘라 n x n 조각. 반환: 조각 경로 리스트 (1..n*n-1)."""
    out = []
    src = Image.open(os.path.join(OUT, 'place_20.png')).convert('RGBA')
    S0 = min(src.size)
    sq = src.crop(((src.width - S0) // 2, 0, (src.width + S0) // 2, S0)).resize((n * size * R2, n * size * R2), Image.LANCZOS)
    for k in range(n * n - 1):
        name = 'ptile_%d_%d' % (n, k + 1)
        p = _cached(name)
        if p:
            out.append(p)
            continue
        r, c = k // n, k % n
        t = sq.crop((c * size * R2, r * size * R2, (c + 1) * size * R2, (r + 1) * size * R2))
        im = Image.new('RGBA', t.size, (0, 0, 0, 0))
        m = Image.new('L', t.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((2, 2, t.width - 3, t.height - 3), 8, fill=255)
        im.paste(t, (0, 0), m)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((2, 2, t.width - 3, t.height - 3), 8, outline=(150, 180, 255, 255), width=3)
        d.ellipse((6, 6, 30, 30), fill=(10, 16, 50, 220))
        d.text((18, 18), str(k + 1), font=font('jalnan', 16), fill=(220, 230, 255, 255), anchor='mm')
        p = os.path.join(ensure_out(), 'mg_' + name + '.png')
        im.save(p)
        out.append(p)
    return out


# ================================================================== 21. 승부차기
def goal_frame():
    name = 'goal_frame'
    if _cached(name):
        return _cached(name)
    w, h = 260, 120
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    for k in range(0, int(W), int(10 * S_)):
        d.line([(k, 8 * S_), (k, H)], fill=(200, 210, 240, 70), width=int(S_))
    for k in range(int(8 * S_), int(H), int(10 * S_)):
        d.line([(6 * S_, k), (W - 6 * S_, k)], fill=(200, 210, 240, 70), width=int(S_))
    d.rectangle((0, 0, 6 * S_, H), fill=(240, 244, 255, 255))
    d.rectangle((W - 6 * S_, 0, W, H), fill=(240, 244, 255, 255))
    d.rectangle((0, 0, W, 6 * S_), fill=(240, 244, 255, 255))
    return _fin(im, w, h, name)


def keeper(pose):
    """골키퍼 (정면). pose: c(가운데) / l, r(몸 날림) / tl, tr(살짝 기운 몸짓)"""
    name = 'keeper_' + pose
    if _cached(name):
        return _cached(name)
    w, h = 110, 80
    im = _cv(w, h)
    W, H = im.size
    lay = Image.new('RGBA', (int(40 * S_), int(70 * S_)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    LW, LH = lay.size
    shirt = (230, 60, 80, 255)
    d.ellipse((LW / 2 - 7 * S_, 0, LW / 2 + 7 * S_, 14 * S_), fill=(240, 210, 180, 255))
    d.rounded_rectangle((LW / 2 - 10 * S_, 14 * S_, LW / 2 + 10 * S_, 40 * S_), 5 * S_, fill=shirt)
    d.line([(LW / 2 - 9 * S_, 18 * S_), (2 * S_, 4 * S_)], fill=shirt, width=int(5 * S_))
    d.line([(LW / 2 + 9 * S_, 18 * S_), (LW - 2 * S_, 4 * S_)], fill=shirt, width=int(5 * S_))
    d.ellipse((0, 0, 7 * S_, 7 * S_), fill=(250, 250, 250, 255))
    d.ellipse((LW - 7 * S_, 0, LW, 7 * S_), fill=(250, 250, 250, 255))
    d.line([(LW / 2 - 5 * S_, 40 * S_), (LW / 2 - 9 * S_, LH - 2 * S_)], fill=(20, 24, 40, 255), width=int(6 * S_))
    d.line([(LW / 2 + 5 * S_, 40 * S_), (LW / 2 + 9 * S_, LH - 2 * S_)], fill=(20, 24, 40, 255), width=int(6 * S_))
    ang = {'c': 0, 'l': 70, 'r': -70, 'tl': 12, 'tr': -12}[pose]
    rot = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    dx = {'c': 0, 'l': -16, 'r': 16, 'tl': -4, 'tr': 4}[pose] * S_
    dy = {'c': 0, 'l': 12, 'r': 12, 'tl': 0, 'tr': 0}[pose] * S_
    im.alpha_composite(rot, (int(W / 2 - rot.width / 2 + dx), int(H - rot.height - 2 * S_ + dy) if pose in ('l', 'r') else int(H - rot.height)))
    return _fin(im, w, h, name)


def soccer_ball(size=20):
    name = 'soccer_ball_%d' % size
    if _cached(name):
        return _cached(name)
    im = _cv(size, size)
    W = im.width
    m, md = _mask(im.size)
    md.ellipse((1 * S_, 1 * S_, W - 1 * S_, W - 1 * S_), fill=255)
    _fill(im, m, (255, 255, 255), (200, 204, 220))
    d = ImageDraw.Draw(im)
    c = W / 2
    pts = [(c + math.cos(math.radians(a)) * W * 0.18, c + math.sin(math.radians(a)) * W * 0.18) for a in range(-90, 270, 72)]
    d.polygon(pts, fill=(20, 20, 30, 255))
    for a in range(-90, 270, 72):
        x, y = c + math.cos(math.radians(a)) * W * 0.42, c + math.sin(math.radians(a)) * W * 0.42
        d.ellipse((x - W * 0.08, y - W * 0.08, x + W * 0.08, y + W * 0.08), fill=(20, 20, 30, 255))
    _outline(im, m, (10, 10, 20), 0.8 * S_)
    return _fin(im, size, size, name)


def aim_arrow(dir_):
    name = 'aim_arrow_%s' % dir_
    if _cached(name):
        return _cached(name)
    w = h = 30
    im = _cv(w, h)
    W = im.width
    ang = {'l': 180, 'c': 90, 'r': 0}[dir_]
    from mg_art import _arrow_mask
    m = _arrow_mask(im.size, S_, ang, 0.9)
    _fill(im, m, (120, 160, 255), (40, 70, 220))
    _outline(im, m, (230, 236, 255), 1.4 * S_)
    return _fin(im, w, h, name)


# ================================================================== 22. 낙석, 유세차
def rock(k):
    name = 'rock_%d' % k
    if _cached(name):
        return _cached(name)
    size = [22, 30, 40][k]
    im = _cv(size, size)
    W = im.width
    rng = random.Random(k + 3)
    m, md = _mask(im.size)
    c = W / 2
    pts = []
    for i in range(9):
        a = i / 9 * 2 * math.pi
        r = W * rng.uniform(0.36, 0.48)
        pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
    md.polygon(pts, fill=255)
    _fill(im, m, (130, 120, 140), (70, 64, 80))
    _hl(im, m, 0.4, 70)
    _outline(im, m, (16, 12, 20), 1.2 * S_)
    return _fin(im, size, size, name)


def campaign_car():
    name = 'campaign_car'
    if _cached(name):
        return _cached(name)
    w, h = 46, 28
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 6 * S_, W - 2 * S_, H - 6 * S_), 4 * S_, fill=255)
    md.polygon([(10 * S_, 6 * S_), (16 * S_, 1 * S_), (32 * S_, 1 * S_), (36 * S_, 6 * S_)], fill=255)
    _fill(im, m, (90, 130, 255), (30, 60, 200))
    d = ImageDraw.Draw(im)
    d.polygon([(17 * S_, 2.5 * S_), (31 * S_, 2.5 * S_), (34 * S_, 6 * S_), (14 * S_, 6 * S_)], fill=(180, 220, 255, 255))
    d.rectangle((6 * S_, 9 * S_, W - 6 * S_, 15 * S_), fill=(240, 244, 255, 255))
    d.text((W / 2, 12 * S_), '기호 3번', font=font('nanum', int(5 * S_)), fill=(30, 50, 160, 255), anchor='mm')
    for x in (11, 35):
        d.ellipse(((x - 4) * S_, H - 10 * S_, (x + 4) * S_, H - 2 * S_), fill=(16, 16, 24, 255))
    _outline(im, m, (8, 12, 40), 1.2 * S_)
    return _fin(im, w, h, name)


# ================================================================== 26. 꼬리잡기(뱀): 머리, 행렬, 시민
def snake_part(kind):
    name = 'snake_' + kind
    if _cached(name):
        return _cached(name)
    size = 16
    im = _cv(size, size)
    W = im.width
    m, md = _mask(im.size)
    md.ellipse((1 * S_, 1 * S_, W - 1 * S_, W - 1 * S_), fill=255)
    if kind == 'head':
        _fill(im, m, (110, 150, 255), (40, 70, 220))
        d = ImageDraw.Draw(im)
        d.ellipse((4 * S_, 5 * S_, 7 * S_, 8 * S_), fill=(255, 255, 255, 255))
        d.ellipse((9 * S_, 5 * S_, 12 * S_, 8 * S_), fill=(255, 255, 255, 255))
        _outline(im, m, (230, 236, 255), 1 * S_)
    elif kind == 'body':
        _fill(im, m, (70, 100, 220), (24, 40, 140))
        d = ImageDraw.Draw(im)
        d.rectangle((7 * S_, 3 * S_, 9 * S_, 12 * S_), fill=(230, 236, 255, 255))
        d.polygon([(9 * S_, 3 * S_), (14 * S_, 5 * S_), (9 * S_, 7 * S_)], fill=(255, 90, 120, 255))
        _outline(im, m, (8, 12, 40), 0.8 * S_)
    else:   # 시민 (먹이)
        _fill(im, m, (255, 220, 190), (220, 170, 140))
        d = ImageDraw.Draw(im)
        d.ellipse((4.5 * S_, 6 * S_, 6.5 * S_, 8 * S_), fill=(20, 20, 30, 255))
        d.ellipse((9.5 * S_, 6 * S_, 11.5 * S_, 8 * S_), fill=(20, 20, 30, 255))
        d.arc((5 * S_, 7 * S_, 11 * S_, 12 * S_), 20, 160, fill=(150, 40, 60, 255), width=int(S_))
        _outline(im, m, (60, 30, 20), 0.8 * S_)
        im = _glow(im, m, (120, 160, 255), 2 * S_, 200)
    return _fin(im, size, size, name)


def grid_floor(cols, rows, cell, name):
    if _cached(name):
        return _cached(name)
    w, h = cols * cell + 8, rows * cell + 8
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (0, 0, W, H), 8 * S_, fill=255)
    _fill(im, m, (16, 24, 60), (8, 12, 34))
    d = ImageDraw.Draw(im)
    for c in range(cols + 1):
        x = (4 + c * cell) * S_
        d.line([(x, 4 * S_), (x, H - 4 * S_)], fill=(40, 56, 120, 140), width=int(0.8 * S_))
    for r in range(rows + 1):
        y = (4 + r * cell) * S_
        d.line([(4 * S_, y), (W - 4 * S_, y)], fill=(40, 56, 120, 140), width=int(0.8 * S_))
    _outline(im, m, (90, 130, 255), 1.6 * S_)
    return _fin(im, w, h, name)


# ================================================================== 27. 복숭아 썰기
def peach_half(side):
    name = 'peach_half_' + side
    if _cached(name):
        return _cached(name)
    w = h = 40
    im = _cv(w, h)
    W = im.width
    m, md = _mask(im.size)
    if side == 'l':
        md.pieslice((4 * S_, 4 * S_, W - 4 * S_, W - 4 * S_), 90, 270, fill=255)
    else:
        md.pieslice((4 * S_, 4 * S_, W - 4 * S_, W - 4 * S_), -90, 90, fill=255)
    _fill(im, m, (255, 170, 160), (230, 90, 110))
    d = ImageDraw.Draw(im)
    cx = W / 2 + (-3 if side == 'l' else 3) * S_
    d.ellipse((cx - 7 * S_, W / 2 - 9 * S_, cx + 7 * S_, W / 2 + 9 * S_), fill=(255, 230, 190, 255))
    d.ellipse((cx - 3 * S_, W / 2 - 5 * S_, cx + 3 * S_, W / 2 + 5 * S_), fill=(150, 70, 50, 255))
    _outline(im, m, (90, 20, 30), 1.2 * S_)
    return _fin(im, w, h, name)


def bug():
    name = 'bug'
    if _cached(name):
        return _cached(name)
    w = h = 34
    im = _cv(w, h)
    W = im.width
    d = ImageDraw.Draw(im)
    c = W / 2
    for k in (-1, 1):
        for j in range(3):
            y = c - 4 * S_ + j * 5 * S_
            d.line([(c, y), (c + k * 14 * S_, y + (j - 1) * 3 * S_)], fill=(20, 20, 20, 255), width=int(1.4 * S_))
    m, md = _mask(im.size)
    md.ellipse((c - 9 * S_, c - 11 * S_, c + 9 * S_, c + 12 * S_), fill=255)
    _fill(im, m, (90, 200, 90), (30, 120, 40))
    d = ImageDraw.Draw(im)
    d.line([(c, c - 9 * S_), (c, c + 11 * S_)], fill=(10, 60, 20, 255), width=int(1.2 * S_))
    d.ellipse((c - 6 * S_, c - 15 * S_, c + 6 * S_, c - 5 * S_), fill=(20, 30, 20, 255))
    _outline(im, m, (10, 30, 10), 1 * S_)
    return _fin(im, w, h, name)


def blade_dot():
    name = 'blade_dot'
    if _cached(name):
        return _cached(name)
    w = h = 14
    im = _cv(w, h)
    W = im.width
    m, md = _mask(im.size)
    md.ellipse((3 * S_, 3 * S_, W - 3 * S_, W - 3 * S_), fill=255)
    _fill(im, m, (230, 240, 255), (150, 180, 255))
    im = _glow(im, m, (100, 150, 255), 3 * S_, 255)
    return _fin(im, w, h, name)


# ================================================================== 28. 지뢰찾기 (대숲 함정) 칸
def mine_cell(kind, size=24):
    """kind: hid / flag / boom / trap / n0..n8"""
    name = 'mcell_%s' % kind
    if _cached(name):
        return _cached(name)
    im = _cv(size, size)
    W = im.width
    m, md = _mask(im.size)
    _rr(md, (1 * S_, 1 * S_, W - 1 * S_, W - 1 * S_), 3 * S_, fill=255)
    d = ImageDraw.Draw(im)
    if kind in ('hid', 'flag'):
        _fill(im, m, (60, 130, 90), (24, 80, 54))
        _hl(im, m, 0.45, 60)
        d = ImageDraw.Draw(im)
        for k in range(3):
            d.line([((5 + k * 6) * S_, (W / S_ - 4) * S_), ((9 + k * 6) * S_, 5 * S_)], fill=(110, 190, 130, 160), width=int(1 * S_))
        if kind == 'flag':
            d.line([(10 * S_, 5 * S_), (10 * S_, 19 * S_)], fill=(230, 230, 240, 255), width=int(1.4 * S_))
            d.polygon([(10.5 * S_, 5 * S_), (19 * S_, 8 * S_), (10.5 * S_, 11 * S_)], fill=(255, 70, 90, 255))
    else:
        _fill(im, m, (36, 34, 50) if kind != 'boom' else (160, 30, 50), (24, 22, 36) if kind != 'boom' else (100, 10, 30))
        d = ImageDraw.Draw(im)
        if kind.startswith('n') and kind != 'n0':
            n = int(kind[1])
            col = [(120, 170, 255), (110, 220, 140), (255, 110, 120), (190, 140, 255), (255, 170, 90), (90, 220, 230),
                   (240, 240, 240), (180, 180, 180)][n - 1]
            d.text((W / 2, W / 2), str(n), font=font('jalnan', int(13 * S_)), fill=col + (255,), anchor='mm')
        if kind in ('trap', 'boom'):
            d.ellipse((W / 2 - 6 * S_, W / 2 - 6 * S_, W / 2 + 6 * S_, W / 2 + 6 * S_), fill=(20, 16, 20, 255))
            for k in range(8):
                a = k * math.pi / 4
                d.line([(W / 2, W / 2), (W / 2 + math.cos(a) * 9 * S_, W / 2 + math.sin(a) * 9 * S_)], fill=(20, 16, 20, 255), width=int(1.6 * S_))
            d.ellipse((W / 2 - 3 * S_, W / 2 - 4 * S_, W / 2 - 1 * S_, W / 2 - 2 * S_), fill=(255, 255, 255, 255))
    _outline(im, m, (8, 10, 20), 1 * S_)
    return _fin(im, size, size, name)


# ================================================================== 29. 물길 조각 (직선/꺾임 × 회전, 물 찬 것)
def pipe_tile(kind, r, wet=False, size=40):
    """kind: 1 직선(r 짝수: 세로, 홀수: 가로) / 2 꺾임 (r=0: 위+오른쪽, 1: 오른쪽+아래, 2: 아래+왼쪽, 3: 왼쪽+위)"""
    name = 'pipe_%d_%d_%d' % (kind, r, wet)
    if _cached(name):
        return _cached(name)
    im = _cv(size, size)
    W = im.width
    m, md = _mask(im.size)
    _rr(md, (1 * S_, 1 * S_, W - 1 * S_, W - 1 * S_), 4 * S_, fill=255)
    _fill(im, m, (90, 70, 50), (60, 44, 34))
    d = ImageDraw.Draw(im)
    c = W / 2
    ww = 12 * S_
    col = (60, 140, 255, 255) if wet else (150, 120, 90, 255)
    edge = (160, 210, 255, 255) if wet else (190, 160, 120, 255)
    if kind == 1:
        if r % 2 == 0:
            d.rectangle((c - ww / 2, 0, c + ww / 2, W), fill=edge)
            d.rectangle((c - ww / 2 + 2 * S_, 0, c + ww / 2 - 2 * S_, W), fill=col)
        else:
            d.rectangle((0, c - ww / 2, W, c + ww / 2), fill=edge)
            d.rectangle((0, c - ww / 2 + 2 * S_, W, c + ww / 2 - 2 * S_), fill=col)
    else:
        sides = [(0, 1), (1, 2), (2, 3), (3, 0)][r]     # 0 위 1 오른쪽 2 아래 3 왼쪽
        for sd in sides:
            for wd, cc in ((ww, edge), (ww - 4 * S_, col)):
                if sd == 0:
                    d.rectangle((c - wd / 2, 0, c + wd / 2, c + wd / 2), fill=cc)
                elif sd == 1:
                    d.rectangle((c - wd / 2, c - wd / 2, W, c + wd / 2), fill=cc)
                elif sd == 2:
                    d.rectangle((c - wd / 2, c - wd / 2, c + wd / 2, W), fill=cc)
                else:
                    d.rectangle((0, c - wd / 2, c + wd / 2, c + wd / 2), fill=cc)
    _outline(im, m, (20, 14, 10), 1 * S_)
    return _fin(im, size, size, name)


def water_source():
    return tile(40, 40, (60, 120, 255), (20, 50, 180), label='물', lsize=14, name='water_source')


def paddy():
    return tile(40, 40, (90, 170, 100), (40, 110, 60), label='논', lsize=14, name='paddy_tile')


# ================================================================== 31. 참새, 새총, 콩알
def sparrow(frame):
    name = 'sparrow_%d' % frame
    if _cached(name):
        return _cached(name)
    w, h = 30, 24
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.ellipse((7 * S_, 8 * S_, 25 * S_, 20 * S_), fill=255)
    md.ellipse((19 * S_, 5 * S_, 28 * S_, 14 * S_), fill=255)
    if frame == 0:
        md.polygon([(10 * S_, 12 * S_), (2 * S_, 2 * S_), (17 * S_, 10 * S_)], fill=255)
    else:
        md.polygon([(10 * S_, 13 * S_), (2 * S_, 22 * S_), (17 * S_, 14 * S_)], fill=255)
    md.polygon([(8 * S_, 13 * S_), (1 * S_, 16 * S_), (8 * S_, 17 * S_)], fill=255)
    _fill(im, m, (170, 130, 100), (110, 80, 60))
    d = ImageDraw.Draw(im)
    d.ellipse((23 * S_, 7 * S_, 25 * S_, 9 * S_), fill=(10, 10, 10, 255))
    d.polygon([(28 * S_, 9 * S_), (30 * S_, 10 * S_), (28 * S_, 11 * S_)], fill=(230, 180, 60, 255))
    _outline(im, m, (30, 20, 14), 1 * S_)
    return _fin(im, w, h, name)


def slingshot():
    name = 'slingshot'
    if _cached(name):
        return _cached(name)
    w, h = 34, 40
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    br = (140, 96, 60, 255)
    d.line([(W / 2, H - 2 * S_), (W / 2, 20 * S_)], fill=br, width=int(5 * S_))
    d.line([(W / 2, 22 * S_), (6 * S_, 4 * S_)], fill=br, width=int(4 * S_))
    d.line([(W / 2, 22 * S_), (W - 6 * S_, 4 * S_)], fill=br, width=int(4 * S_))
    d.line([(6 * S_, 5 * S_), (W / 2, 12 * S_), (W - 6 * S_, 5 * S_)], fill=(230, 220, 200, 255), width=int(1.4 * S_))
    return _fin(im, w, h, name)


def pea():
    name = 'pea'
    if _cached(name):
        return _cached(name)
    w = h = 10
    im = _cv(w, h)
    W = im.width
    m, md = _mask(im.size)
    md.ellipse((1 * S_, 1 * S_, W - 1 * S_, W - 1 * S_), fill=255)
    _fill(im, m, (150, 230, 120), (60, 160, 60))
    _outline(im, m, (20, 60, 20), 0.8 * S_)
    return _fin(im, w, h, name)


# ================================================================== 33. 징검돌 퍼즐 칸
def stone_cell(kind, size=26):
    """kind: land / water / stone / rock / goal / step"""
    name = 'scell_' + kind
    if _cached(name):
        return _cached(name)
    im = _cv(size, size)
    W = im.width
    d = ImageDraw.Draw(im)
    if kind in ('land', 'goal'):
        d.rectangle((0, 0, W, W), fill=(40, 90, 70, 255))
        rng = random.Random(size)
        for _ in range(10):
            x, y = rng.uniform(2, size - 2) * S_, rng.uniform(4, size - 2) * S_
            d.line([(x, y), (x + 1 * S_, y - 4 * S_)], fill=(80, 150, 100, 255), width=int(S_))
        if kind == 'goal':
            d.line([(W / 2 - 2 * S_, 4 * S_), (W / 2 - 2 * S_, W - 3 * S_)], fill=(230, 230, 240, 255), width=int(1.6 * S_))
            d.polygon([(W / 2 - 1 * S_, 4 * S_), (W / 2 + 9 * S_, 7.5 * S_), (W / 2 - 1 * S_, 11 * S_)], fill=(80, 140, 255, 255))
    elif kind in ('water', 'step'):
        d.rectangle((0, 0, W, W), fill=(30, 80, 190, 255))
        for k in range(3):
            y = (6 + k * 7) * S_
            d.arc((2 * S_, y - 3 * S_, 12 * S_, y + 3 * S_), 200, 340, fill=(130, 180, 255, 200), width=int(S_))
            d.arc((13 * S_, y, 23 * S_, y + 6 * S_), 200, 340, fill=(130, 180, 255, 200), width=int(S_))
        if kind == 'step':
            d.ellipse((3 * S_, 5 * S_, W - 3 * S_, W - 5 * S_), fill=(140, 140, 160, 255))
            d.ellipse((6 * S_, 7 * S_, W - 10 * S_, 12 * S_), fill=(190, 190, 210, 255))
    elif kind == 'stone':
        d.rectangle((0, 0, W, W), fill=(40, 90, 70, 255))
        m, md = _mask(im.size)
        md.ellipse((2 * S_, 3 * S_, W - 2 * S_, W - 2 * S_), fill=255)
        _fill(im, m, (190, 190, 210), (110, 110, 130))
        _hl(im, m, 0.4, 100)
        _outline(im, m, (20, 20, 30), 1 * S_)
    else:  # rock (못 지나감)
        d.rectangle((0, 0, W, W), fill=(40, 90, 70, 255))
        m, md = _mask(im.size)
        md.polygon([(2 * S_, W - 2 * S_), (6 * S_, 4 * S_), (14 * S_, 1 * S_), (22 * S_, 6 * S_), (W - 1 * S_, W - 2 * S_)], fill=255)
        _fill(im, m, (90, 80, 90), (50, 44, 54))
        _outline(im, m, (14, 10, 14), 1 * S_)
    return _fin(im, size, size, name)


# ================================================================== 34. 자전거, 목표 고리
def bicycle():
    name = 'bicycle'
    if _cached(name):
        return _cached(name)
    w, h = 50, 34
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    for x in (11, 39):
        d.ellipse(((x - 9) * S_, 15 * S_, (x + 9) * S_, 33 * S_), outline=(220, 230, 255, 255), width=int(2 * S_))
    fr = (90, 140, 255, 255)
    d.line([(11 * S_, 24 * S_), (22 * S_, 24 * S_), (30 * S_, 13 * S_), (39 * S_, 24 * S_)], fill=fr, width=int(2 * S_))
    d.line([(22 * S_, 24 * S_), (18 * S_, 12 * S_)], fill=fr, width=int(2 * S_))
    d.line([(30 * S_, 13 * S_), (32 * S_, 7 * S_)], fill=fr, width=int(2 * S_))
    d.rectangle((14 * S_, 10 * S_, 22 * S_, 12 * S_), fill=(30, 30, 40, 255))
    d.ellipse((17 * S_, 0, 25 * S_, 8 * S_), fill=(240, 210, 180, 255))
    d.line([(21 * S_, 8 * S_), (24 * S_, 16 * S_)], fill=(230, 70, 90, 255), width=int(4 * S_))
    return _fin(im, w, h, name)


def target_ring(on):
    name = 'target_ring_%d' % on
    if _cached(name):
        return _cached(name)
    w = h = 56
    im = _cv(w, h)
    W = im.width
    d = ImageDraw.Draw(im)
    col = (90, 160, 255, 220) if on else (255, 90, 110, 160)
    d.ellipse((3 * S_, 3 * S_, W - 3 * S_, W - 3 * S_), outline=col, width=int(2.4 * S_))
    return _fin(im, w, h, name)


# ================================================================== 35. 주차: 버스(위에서 본 모습), 고깔, 주차칸
def bus_top():
    name = 'bus_top'
    if _cached(name):
        return _cached(name)
    w, h = 30, 64
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 2 * S_, W - 2 * S_, H - 2 * S_), 5 * S_, fill=255)
    _fill(im, m, (90, 130, 255), (40, 70, 200))
    d = ImageDraw.Draw(im)
    d.rectangle((5 * S_, 4 * S_, W - 5 * S_, 12 * S_), fill=(180, 220, 255, 255))
    for k in range(4):
        d.rectangle((5 * S_, (18 + k * 10) * S_, W - 5 * S_, (24 + k * 10) * S_), fill=(60, 90, 200, 255))
    d.rectangle((8 * S_, H - 8 * S_, W - 8 * S_, H - 5 * S_), fill=(255, 80, 100, 255))
    _outline(im, m, (230, 236, 255), 1.2 * S_)
    return _fin(im, w, h, name)


def cone():
    name = 'cone'
    if _cached(name):
        return _cached(name)
    w = h = 18
    im = _cv(w, h)
    W = im.width
    m, md = _mask(im.size)
    md.ellipse((2 * S_, 2 * S_, W - 2 * S_, W - 2 * S_), fill=255)
    _fill(im, m, (255, 120, 80), (220, 60, 40))
    d = ImageDraw.Draw(im)
    d.ellipse((W / 2 - 4 * S_, W / 2 - 4 * S_, W / 2 + 4 * S_, W / 2 + 4 * S_), fill=(250, 250, 255, 255))
    d.ellipse((W / 2 - 2 * S_, W / 2 - 2 * S_, W / 2 + 2 * S_, W / 2 + 2 * S_), fill=(230, 70, 50, 255))
    _outline(im, m, (60, 10, 10), 1 * S_)
    return _fin(im, w, h, name)


def parked_car(col):
    name = 'parked_car_%d_%d_%d' % col
    if _cached(name):
        return _cached(name)
    w, h = 26, 48
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (2 * S_, 2 * S_, W - 2 * S_, H - 2 * S_), 6 * S_, fill=255)
    _fill(im, m, col, tuple(int(c * 0.6) for c in col))
    d = ImageDraw.Draw(im)
    d.rectangle((5 * S_, 10 * S_, W - 5 * S_, 18 * S_), fill=(30, 40, 70, 255))
    d.rectangle((5 * S_, 32 * S_, W - 5 * S_, 38 * S_), fill=(30, 40, 70, 255))
    _outline(im, m, (10, 10, 20), 1 * S_)
    return _fin(im, w, h, name)


def parking_lot():
    """주차장 바닥 (480x210): 주차칸 선은 그림에 그리지 않고 오브젝트로."""
    name = 'parking_lot'
    if _cached(name):
        return _cached(name)
    w, h = 480, 210
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, H), fill=(34, 38, 56, 255))
    rng = random.Random(35)
    for _ in range(500):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        d.point((x, y), fill=(60, 64, 84, 255))
    return _fin(im, w, h, name)


def bay(state):
    name = 'parking_bay_%s' % state
    if _cached(name):
        return _cached(name)
    w, h = 44, 74
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    col = {'idle': (230, 230, 250, 255), 'target': (100, 170, 255, 255), 'ok': (110, 230, 140, 255)}[state]
    d.rectangle((1 * S_, 1 * S_, W - 1 * S_, H - 1 * S_), outline=col, width=int(2.2 * S_))
    if state == 'target':
        d.rectangle((3 * S_, 3 * S_, W - 3 * S_, H - 3 * S_), fill=(80, 140, 255, 50))
        d.text((W / 2, H / 2), 'P', font=font('jalnan', int(18 * S_)), fill=(120, 170, 255, 200), anchor='mm')
    return _fin(im, w, h, name)


# ================================================================== 38. 틀린 그림 찾기: 벽보 2장 (원본/바뀐 것)
DIFF_PUZZLES = [
    # 각 차이: (종류, 위치 x, y(벽보 안 좌표, 가운데 기준, 위가 +), 반지름)
    [('color_badge', -52, 58, 14), ('missing_star', 50, 60, 12), ('text', 0, -40, 16), ('extra_dot', 72, -22, 10),
     ('tie', -30, 2, 12)],
    [('moon', 54, 48, 12), ('number', 70, -56, 12), ('flower', -56, -54, 12), ('stripe', 0, -66, 14),
     ('glasses', -30, 18, 12)],
]


def poster(puz, changed):
    """새내 골목 선거 벽보 (190x170). puz: 0/1, changed: 바뀐 그림이면 True."""
    name = 'poster_%d_%d' % (puz, changed)
    if _cached(name):
        return _cached(name)
    w, h = 190, 170
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    md.rectangle((0, 0, W, H), fill=255)
    top, bot = ((240, 244, 255), (200, 210, 240)) if puz == 0 else ((230, 236, 255), (180, 196, 236))
    _fill(im, m, top, bot)
    d = ImageDraw.Draw(im)
    X = lambda x: (w / 2 + x) * S_
    Y = lambda y: (h / 2 - y) * S_
    # 띠
    d.rectangle((0, 0, W, 26 * S_), fill=(40, 70, 200, 255))
    _jtext(d, (W / 2, 13 * S_), '조치원을 바꿀 사람!' if puz == 0 else '막내에게 한 표를!', 12 * S_, (255, 255, 255, 255))
    # 얼굴 (간단한 캐릭터)
    d.ellipse((X(-58), Y(52), X(-2), Y(-4)), fill=(250, 220, 190, 255))
    d.chord((X(-60), Y(56), X(0), Y(20)), 180, 360, fill=(40, 30, 30, 255))
    d.ellipse((X(-42), Y(30), X(-36), Y(24)), fill=(20, 20, 20, 255))
    d.ellipse((X(-24), Y(30), X(-18), Y(24)), fill=(20, 20, 20, 255))
    d.arc((X(-40), Y(20), X(-20), Y(8)), 20, 160, fill=(150, 40, 50, 255), width=int(1.4 * S_))
    # 몸
    d.polygon([(X(-64), Y(-30)), (X(4), Y(-30)), (X(-6), Y(-4)), (X(-54), Y(-4))], fill=(40, 60, 130, 255))
    # 기호 번호 / 별
    d.ellipse((X(26), Y(36), X(74), Y(-12)), fill=(40, 70, 200, 255))
    d.text((X(50), Y(12)), '3', font=font('jalnan', int(26 * S_)), fill=(255, 255, 255, 255), anchor='mm')
    d.text((X(0), Y(-40)), '복숭아처럼 달콤한 조치원' if puz == 0 else '일자리 1000개 약속!', font=font('nanum', int(9 * S_)),
           fill=(30, 40, 90, 255), anchor='mm')
    diffs = DIFF_PUZZLES[puz]

    def star(cx, cy, r, col):
        pts = []
        for k in range(10):
            a = math.radians(-90 + k * 36)
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((X(cx) + math.cos(a) * rr * S_, Y(cy) + math.sin(a) * rr * S_))
        d.polygon(pts, fill=col)
    for kind, x, y, r in diffs:
        if kind == 'color_badge':
            d.ellipse((X(x - 10), Y(y + 10), X(x + 10), Y(y - 10)), fill=((230, 60, 80, 255) if changed else (60, 160, 90, 255)))
        elif kind == 'missing_star':
            if not changed:
                star(x, y, 10, (255, 190, 60, 255))
        elif kind == 'text':
            if changed:
                d.rectangle((X(x - 70), Y(y + 6), X(x + 70), Y(y - 6)), fill=top + (255,))
                d.text((X(x), Y(y)), '복숭아처럼 달콤한 조치읍', font=font('nanum', int(9 * S_)), fill=(30, 40, 90, 255), anchor='mm')
        elif kind == 'extra_dot':
            if changed:
                d.ellipse((X(x - 5), Y(y + 5), X(x + 5), Y(y - 5)), fill=(40, 70, 200, 255))
        elif kind == 'tie':
            d.polygon([(X(x - 4), Y(y + 4)), (X(x + 4), Y(y + 4)), (X(x + 2), Y(y - 18)), (X(x - 2), Y(y - 18))],
                      fill=((230, 60, 80, 255) if not changed else (60, 160, 90, 255)))
        elif kind == 'moon':
            if not changed:
                d.ellipse((X(x - 9), Y(y + 9), X(x + 9), Y(y - 9)), fill=(255, 210, 90, 255))
                d.ellipse((X(x - 4), Y(y + 11), X(x + 13), Y(y - 7)), fill=top + (255,))
        elif kind == 'number':
            d.text((X(x), Y(y)), '2026' if not changed else '2027', font=font('nanum', int(8 * S_)), fill=(30, 40, 90, 255), anchor='mm')
        elif kind == 'flower':
            if not changed:
                for k in range(5):
                    a = math.radians(k * 72)
                    d.ellipse((X(x + math.cos(a) * 5 - 4), Y(y + math.sin(a) * 5 + 4), X(x + math.cos(a) * 5 + 4),
                               Y(y + math.sin(a) * 5 - 4)), fill=(255, 130, 170, 255))
                d.ellipse((X(x - 3), Y(y + 3), X(x + 3), Y(y - 3)), fill=(255, 220, 90, 255))
        elif kind == 'stripe':
            d.rectangle((0, Y(y + 4), W, Y(y - 4)), fill=((40, 70, 200, 255) if not changed else (160, 60, 220, 255)))
        elif kind == 'glasses':
            if changed:
                for gx in (-39, -21):
                    d.ellipse((X(gx - 7), Y(y + 6), X(gx + 7), Y(y - 6)), outline=(20, 20, 30, 255), width=int(1.4 * S_))
                d.line([(X(-32), Y(y)), (X(-28), Y(y))], fill=(20, 20, 30, 255), width=int(1.4 * S_))
    _outline(im, m, (10, 14, 40), 1.6 * S_)
    return _fin(im, w, h, name)


def found_circle():
    name = 'found_circle'
    if _cached(name):
        return _cached(name)
    w = h = 32
    im = _cv(w, h)
    W = im.width
    d = ImageDraw.Draw(im)
    d.ellipse((2 * S_, 2 * S_, W - 2 * S_, W - 2 * S_), outline=(255, 60, 90, 255), width=int(2.6 * S_))
    return _fin(im, w, h, name)


# ================================================================== 39. 벽돌깨기
def brick(col):
    name = 'brick_%d_%d_%d' % col
    if _cached(name):
        return _cached(name)
    return tile(52, 18, col, tuple(int(c * 0.55) for c in col), edge=(8, 10, 24), r=3, name=name)


def paddle():
    return tile(70, 12, (180, 200, 255), (70, 100, 220), edge=(230, 236, 255), r=6, name='paddle')


def ball(size=12):
    name = 'ball_%d' % size
    if _cached(name):
        return _cached(name)
    im = _cv(size, size)
    W = im.width
    m, md = _mask(im.size)
    md.ellipse((1 * S_, 1 * S_, W - 1 * S_, W - 1 * S_), fill=255)
    _fill(im, m, (255, 255, 255), (170, 190, 255))
    im = _glow(im, m, (100, 150, 255), 2 * S_, 220)
    return _fin(im, size, size, name)


# ================================================================== 40. 건널목: 차, 기차, 길 바닥
def car_side(col, face='r'):
    name = 'car_side_%d_%d_%d_%s' % (*col, face)
    if _cached(name):
        return _cached(name)
    w, h = 44, 22
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (1 * S_, 7 * S_, W - 1 * S_, H - 4 * S_), 4 * S_, fill=255)
    md.polygon([(10 * S_, 7 * S_), (15 * S_, 1 * S_), (30 * S_, 1 * S_), (35 * S_, 7 * S_)], fill=255)
    _fill(im, m, col, tuple(int(c * 0.6) for c in col))
    d = ImageDraw.Draw(im)
    d.polygon([(16 * S_, 2.5 * S_), (29 * S_, 2.5 * S_), (33 * S_, 7 * S_), (12 * S_, 7 * S_)], fill=(180, 220, 255, 255))
    for x in (10, 34):
        d.ellipse(((x - 4) * S_, H - 8 * S_, (x + 4) * S_, H), fill=(16, 16, 24, 255))
    d.ellipse((W - 5 * S_, 9 * S_, W - 1 * S_, 13 * S_), fill=(255, 250, 200, 255))
    _outline(im, m, (8, 10, 20), 1 * S_)
    if face == 'l':
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return _fin(im, w, h, name)


def train(w=300, h=24):
    name = 'train_%d' % w
    if _cached(name):
        return _cached(name)
    im = _cv(w, h)
    W, H = im.size
    m, md = _mask(im.size)
    _rr(md, (1 * S_, 1 * S_, W - 1 * S_, H - 3 * S_), 5 * S_, fill=255)
    _fill(im, m, (220, 226, 240), (150, 160, 190))
    d = ImageDraw.Draw(im)
    for x in range(10, w - 10, 16):
        d.rectangle((x * S_, 5 * S_, (x + 10) * S_, 11 * S_), fill=(40, 60, 120, 255))
    d.rectangle((0, 14 * S_, W, 17 * S_), fill=(60, 110, 230, 255))
    for x in range(60, w, 60):
        d.line([(x * S_, 1 * S_), (x * S_, H - 3 * S_)], fill=(80, 90, 120, 255), width=int(1.4 * S_))
    _outline(im, m, (10, 12, 30), 1 * S_)
    return _fin(im, w, h, name)


def crossing_board(rows, cell=24, w=480):
    """건널목 바닥 (아래가 시작, 위가 목표). rows: 아래부터 'safe'/'road'/'rail'/'goal'"""
    name = 'crossing_board_%s' % ''.join(r[0] for r in rows)
    if _cached(name):
        return _cached(name)
    h = len(rows) * cell
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    for i, kind in enumerate(rows):
        y1 = H - i * cell * S_
        y0 = y1 - cell * S_
        if kind == 'road':
            d.rectangle((0, y0, W, y1), fill=(36, 38, 56, 255))
            if i + 1 < len(rows) and rows[i + 1] == 'road':
                for x in range(0, w, 30):
                    d.rectangle((x * S_, y0 - 1 * S_, (x + 16) * S_, y0 + 1 * S_), fill=(230, 230, 240, 200))
        elif kind == 'rail':
            d.rectangle((0, y0, W, y1), fill=(50, 44, 50, 255))
            for x in range(0, w, 12):
                d.rectangle((x * S_, y0 + 3 * S_, (x + 6) * S_, y1 - 3 * S_), fill=(90, 70, 60, 255))
            for yy in (y0 + 7 * S_, y1 - 9 * S_):
                d.rectangle((0, yy, W, yy + 2 * S_), fill=(190, 200, 230, 255))
        elif kind == 'goal':
            d.rectangle((0, y0, W, y1), fill=(40, 90, 200, 255))
            _jtext(d, (W / 2, (y0 + y1) / 2), '도착! 시민들이 기다려요', 11 * S_, (255, 255, 255, 255))
        else:
            d.rectangle((0, y0, W, y1), fill=(70, 74, 100, 255))
            for x in range(0, w, 24):
                d.line([(x * S_, y0), (x * S_, y1)], fill=(90, 96, 124, 255), width=int(S_))
    return _fin(im, w, h, name)


def puzzle_preview(size=96):
    name = 'puzzle_preview_%d' % size
    if _cached(name):
        return _cached(name)
    src = Image.open(os.path.join(OUT, 'place_20.png')).convert('RGBA')
    S0 = min(src.size)
    sq = src.crop(((src.width - S0) // 2, 0, (src.width + S0) // 2, S0)).resize((size * R2, size * R2), Image.LANCZOS)
    d = ImageDraw.Draw(sq)
    for k in (1, 2):
        p = k * size * R2 / 3
        d.line([(p, 0), (p, size * R2)], fill=(150, 180, 255, 200), width=2)
        d.line([(0, p), (size * R2, p)], fill=(150, 180, 255, 200), width=2)
    d.rectangle((0, 0, size * R2 - 1, size * R2 - 1), outline=(150, 180, 255, 255), width=3)
    p = os.path.join(ensure_out(), 'mg_' + name + '.png')
    sq.save(p)
    return p


def peach_cut():
    name = 'peach_cut'
    if _cached(name):
        return _cached(name)
    w, h = 56, 40
    im = _cv(w, h)
    l = Image.open(peach_half('l')).convert('RGBA').resize((int(40 * S_), int(40 * S_)), Image.LANCZOS)
    r = Image.open(peach_half('r')).convert('RGBA').resize((int(40 * S_), int(40 * S_)), Image.LANCZOS)
    im.alpha_composite(l.rotate(15, resample=Image.BICUBIC), (0, 0))
    im.alpha_composite(r.rotate(-15, resample=Image.BICUBIC), (int(16 * S_), 0))
    return _fin(im, w, h, name)


def signal_light(on):
    name = 'signal_light_%d' % on
    if _cached(name):
        return _cached(name)
    w, h = 30, 20
    im = _cv(w, h)
    W, H = im.size
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, H), fill=(20, 20, 30, 255))
    for k, x in enumerate((8, 22)):
        lit = on and k == 0 or (on == 2 and k == 1)
        col = (255, 60, 80, 255) if (on and (k == (on - 1))) else (70, 20, 30, 255)
        d.ellipse(((x - 5) * S_, 5 * S_, (x + 5) * S_, 15 * S_), fill=col)
    return _fin(im, w, h, name)


# ================================================================== 2번 받기: 시장(단풍잎) · 대통령(감귤) 단계 물건
def maple(kind):
    """kind: leaf / gold / dry (단풍잎)"""
    name = 'maple_' + kind
    if _cached(name):
        return _cached(name)
    w = h = 30
    im = _cv(w, h)
    W, H = im.size
    s = S_
    cx, cy = W / 2, H * 0.52
    m, d = _mask(im.size)
    pts = []
    for k in range(10):
        a = math.radians(-90 + k * 36)
        r = W * (0.46 if k % 2 == 0 else 0.2)
        if k in (4, 6):
            r *= 0.8
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=255)
    col = {'leaf': ((255, 110, 70), (200, 30, 30)), 'gold': ((255, 220, 120), (240, 90, 30)),
           'dry': ((150, 100, 70), (90, 50, 30))}[kind]
    _fill(im, m, col[0], col[1])
    d2 = ImageDraw.Draw(im)
    for k in (0, 2, 8):
        a = math.radians(-90 + k * 36)
        d2.line([(cx, cy), (cx + W * 0.4 * math.cos(a), cy + W * 0.4 * math.sin(a))], fill=(120, 20, 20, 150), width=int(0.6 * s))
    d2.line([(cx, cy), (cx, H - 1.5 * s)], fill=(110, 40, 20, 255), width=int(1.4 * s))
    _outline(im, m, (60, 10, 10), 1.2 * s)
    if kind == 'gold':
        im = _glow(im, m, (255, 220, 160), 3 * s, 230)
    return _fin(im, w, h, name)


def tangerine(kind):
    """kind: leaf(보통 감귤) / gold(황금 한라봉) / dry(상한 귤)"""
    name = 'tangerine_' + kind
    if _cached(name):
        return _cached(name)
    w = h = 30
    im = _cv(w, h)
    W, H = im.size
    s = S_
    cx, cy = W / 2, H * 0.56
    R = W * 0.36
    m, d = _mask(im.size)
    d.ellipse((cx - R, cy - R * 0.9, cx + R, cy + R * 0.9), fill=255)
    if kind == 'gold':
        d.ellipse((cx - R * 0.35, cy - R * 1.25, cx + R * 0.35, cy - R * 0.6), fill=255)
    col = {'leaf': ((255, 190, 60), (240, 120, 10)), 'gold': ((255, 236, 140), (250, 160, 20)),
           'dry': ((140, 130, 80), (80, 80, 50))}[kind]
    _fill(im, m, col[0], col[1])
    d2 = ImageDraw.Draw(im)
    d2.ellipse((cx - R * 0.5, cy - R * 0.6, cx - R * 0.1, cy - R * 0.25), fill=(255, 240, 200, 150))
    d2.polygon([(cx, cy - R * 0.85), (cx + R * 0.7, cy - R * 1.25), (cx + R * 0.3, cy - R * 0.75)], fill=(40, 140, 60, 255))
    if kind == 'dry':
        for (px, py) in ((0.4, 0.6), (0.62, 0.5), (0.55, 0.72)):
            d2.ellipse((W * px - 2 * s, H * py - 2 * s, W * px + 2 * s, H * py + 2 * s), fill=(60, 70, 40, 220))
    _outline(im, m, (90, 40, 0) if kind != 'dry' else (40, 40, 20), 1.2 * s)
    if kind == 'gold':
        im = _glow(im, m, (255, 230, 150), 3 * s, 230)
    return _fin(im, w, h, name)
