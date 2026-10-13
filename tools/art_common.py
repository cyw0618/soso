# -*- coding: utf-8 -*-
"""그림 제작용 공통 도구 (PIL). 모든 그림은 4배 크기로 그린 뒤 줄여서 부드럽게 만든다."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets_src')
OUT = os.path.join(HERE, '..', 'build', 'art')

# 폰트: 처음 한 번 `npm i @fontsource/black-han-sans @fontsource/do-hyeon @fontsource/nanum-gothic`
# 로 받은 woff 를 쓴다. 경로는 FONT_DIR 환경변수로 지정.
FONT_DIR = os.environ.get('FONT_DIR', os.path.join(HERE, 'fonts'))


def _font_path(name):
    cands = {
        'black': 'black-han-sans/files/black-han-sans-korean-400-normal.woff',
        'dohyeon': 'do-hyeon/files/do-hyeon-korean-400-normal.woff',
        'nanum': 'nanum-gothic/files/nanum-gothic-korean-700-normal.woff',
        'nanumx': 'nanum-gothic/files/nanum-gothic-korean-800-normal.woff',
    }
    return os.path.join(FONT_DIR, cands[name])


_fcache = {}


def font(name, size):
    k = (name, size)
    if k not in _fcache:
        _fcache[k] = ImageFont.truetype(_font_path(name), int(size))
    return _fcache[k]


def ensure_out():
    os.makedirs(OUT, exist_ok=True)
    return OUT


def save(im, name):
    ensure_out()
    p = os.path.join(OUT, name + '.png')
    im.save(p, optimize=True)
    return p


def text_size(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0], b[3] - b[1]


def draw_text(im, xy, s, f, fill=(255, 255, 255), stroke=0, stroke_fill=(0, 0, 0), anchor='la', shadow=None):
    d = ImageDraw.Draw(im)
    if shadow:
        ox, oy, col = shadow
        d.text((xy[0] + ox, xy[1] + oy), s, font=f, fill=col, anchor=anchor, stroke_width=stroke, stroke_fill=col)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def vgradient(size, top, bottom):
    w, h = size
    im = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bottom, y / max(1, h - 1)))
    return im


def rgba(c, a=255):
    return (c[0], c[1], c[2], a)


def rounded_box(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def downscale(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


def quantize_png(im, colors=256):
    """작은 파일 크기를 위해 팔레트 PNG 로 (알파 있으면 RGBA 유지)."""
    if im.mode == 'RGBA':
        return im
    return im.convert('RGB').quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
