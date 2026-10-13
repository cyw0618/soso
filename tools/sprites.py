# -*- coding: utf-8 -*-
"""게임 전용 그림: 지도 핀, 등급 도장, 인물 상반신, 단색 판 등. (2배 해상도, pic_scale 0.5)"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from art_common import *
import ui_kit as K

R2, SS = 2, 3


def _cv(w, h):
    return Image.new('RGBA', (int(w * R2 * SS), int(h * R2 * SS)), (0, 0, 0, 0))


def _fin(im, w, h, name):
    im = im.resize((int(w * R2), int(h * R2)), Image.LANCZOS)
    return save(im, name)


def plain(w, h, rgba, name):
    p = os.path.join(ensure_out(), name + '.png')
    if not os.path.exists(p):
        Image.new('RGBA', (w * R2, h * R2), rgba).save(p)
    return p


def pin(n, state='on'):
    """지도 핀: 금색 물방울 + 번호. state: on / done / hot"""
    w, h = 24, 30
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    cols = {'on': ((255, 226, 110), (236, 150, 30), (110, 56, 4)),
            'hot': ((255, 160, 160), (230, 50, 70), (110, 10, 24)),
            'done': ((190, 196, 210), (110, 118, 136), (40, 44, 58))}[state]
    cx, r = W / 2, W * 0.42
    cy = r + 1.5 * s
    # 그림자
    sh = Image.new('L', im.size, 0)
    ImageDraw.Draw(sh).ellipse((cx - r * 0.7, H - 5 * s, cx + r * 0.7, H - 1 * s), fill=120)
    shd = Image.new('RGBA', im.size, (0, 0, 0, 255))
    shd.putalpha(sh.filter(ImageFilter.GaussianBlur(1.5 * s)))
    im.alpha_composite(shd)
    body = Image.new('L', im.size, 0)
    bd = ImageDraw.Draw(body)
    bd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    bd.polygon([(cx - r * 0.72, cy + r * 0.62), (cx + r * 0.72, cy + r * 0.62), (cx, H - 3 * s)], fill=255)
    g = K._grad(im.size, cols[0], cols[1])
    g.putalpha(body)
    im.alpha_composite(g)
    ol = body.filter(ImageFilter.MaxFilter(int(1.6 * s) | 1))
    olay = Image.new('RGBA', im.size, cols[2] + (255,))
    olay.putalpha(ImageChops_sub(ol, body))
    im.alpha_composite(olay)
    d = ImageDraw.Draw(im)
    d.ellipse((cx - r * 0.66, cy - r * 0.66, cx + r * 0.66, cy + r * 0.66), fill=(255, 255, 255, 235))
    if state == 'done':
        d.line([(cx - r * 0.35, cy), (cx - r * 0.05, cy + r * 0.3), (cx + r * 0.42, cy - r * 0.32)], fill=(60, 160, 90, 255), width=int(2.4 * s))
    else:
        f = font('jalnan', int(r * (1.0 if n < 10 else 0.85)))
        d.text((cx, cy + 0.6 * s), str(n), font=f, fill=cols[2] + (255,), anchor='mm')
    return _fin(im, w, h, 'pin_%s_%02d' % (state, n))


def ImageChops_sub(a, b):
    from PIL import ImageChops
    return ImageChops.subtract(a, b)


def grade_stamp(g):
    cols = {'S': 'royal', 'A': 'white', 'B': 'purple', 'C': 'gray', 'D': 'red'}
    return K.big_text(g, 44, cols[g])


def bust(cover_big, key):
    """표지에서 인물 상반신을 잘라 아래쪽을 부드럽게 투명 처리."""
    S = 3
    boxes = {'gp': (0, 0, 150, 200), 'me': (110, 120, 270, 330), 'u1': (0, 190, 140, 345), 'u2': (205, 150, 359, 330)}
    b = boxes[key]
    crop = cover_big.crop(tuple(v * S for v in b)).convert('RGBA')
    w, h = crop.size
    a = Image.new('L', (w, h), 255)
    ad = ImageDraw.Draw(a)
    fade = int(h * 0.22)
    for y in range(h - fade, h):
        ad.line([(0, y), (w, y)], fill=int(255 * (h - y) / fade))
    side = int(w * 0.08)
    for x in range(side):
        v = int(255 * x / side)
        ad.line([(x, 0), (x, h)], fill=v)
        ad.line([(w - 1 - x, 0), (w - 1 - x, h)], fill=v)
    from PIL import ImageChops
    crop.putalpha(ImageChops.multiply(crop.getchannel('A'), a))
    tw = 190
    th = int(h * tw / w)
    crop = crop.resize((tw * R2, th * R2), Image.LANCZOS)
    return save(crop, 'bust_%s' % key)


def portrait_crop(cover_big, key):
    S = 3
    boxes = {'me': (140, 192, 240, 292), 'gp': (22, 40, 132, 150), 'u1': (8, 222, 112, 326), 'u2': (232, 178, 332, 278)}
    b = boxes[key]
    return cover_big.crop(tuple(v * S for v in b))


def number_card(text, w, h, color):
    return K.badge(text, w, h, color)


def arrow_marker(n, state='on'):
    """지도 화살표: 번호 원 + 아래를 가리키는 화살표 (끝이 장소를 가리킴). 크기 22x32. 검정+청색 테마."""
    w, h = 22, 32
    im = _cv(w, h)
    W, H = im.size
    s = R2 * SS
    cols = {'on': ((60, 100, 236), (10, 18, 70), (0, 2, 12), (40, 90, 255)),
            'hot': ((230, 64, 86), (110, 8, 28), (16, 0, 4), (255, 60, 90))}[state]
    body = Image.new('L', im.size, 0)
    bd = ImageDraw.Draw(body)
    cx = W / 2
    ay0 = H * 0.46
    bd.polygon([(cx - W * 0.20, ay0), (cx + W * 0.20, ay0), (cx + W * 0.20, H * 0.66), (cx + W * 0.42, H * 0.66),
                (cx, H - 1.5 * s), (cx - W * 0.42, H * 0.66), (cx - W * 0.20, H * 0.66)], fill=255)
    r = W * 0.40
    cy = r + 1.2 * s
    bd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    # 청색 빛 번짐 + 그림자
    gl = body.filter(ImageFilter.MaxFilter(int(2.2 * s) | 1)).filter(ImageFilter.GaussianBlur(1.8 * s))
    glow = Image.new('RGBA', im.size, cols[3] + (255,))
    glow.putalpha(gl.point(lambda v: v * 200 // 255))
    im.alpha_composite(glow)
    sh = body.filter(ImageFilter.GaussianBlur(1.6 * s))
    shd = Image.new('RGBA', im.size, (0, 0, 0, 255))
    shd.putalpha(sh.point(lambda v: v * 170 // 255))
    im.alpha_composite(shd, (0, int(1.2 * s)))
    g = K._grad(im.size, cols[0], cols[1])
    g.putalpha(body)
    im.alpha_composite(g)
    ol = body.filter(ImageFilter.MaxFilter(int(1.8 * s) | 1))
    olay = Image.new('RGBA', im.size, cols[2] + (255,))
    olay.putalpha(ImageChops_sub(ol, body))
    im.alpha_composite(olay)
    d = ImageDraw.Draw(im)
    d.ellipse((cx - r * 0.74, cy - r * 0.74, cx + r * 0.74, cy + r * 0.74), fill=(4, 6, 16, 250),
              outline=(200, 214, 255, 255), width=int(0.8 * s))
    f = font('jalnan', int(r * (1.05 if n < 10 else 0.86)))
    d.text((cx, cy + 0.5 * s), str(n), font=f, fill=(255, 255, 255, 255), anchor='mm')
    d.polygon([(cx - W * 0.12, ay0 + 2 * s), (cx - W * 0.04, ay0 + 2 * s), (cx - W * 0.04, H * 0.62)], fill=(255, 255, 255, 70))
    return _fin(im, w, h, 'arrow2_%s_%02d' % (state, n))
