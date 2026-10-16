# -*- coding: utf-8 -*-
"""시장·대통령 선거 미니게임 그림 (2배 해상도로 그리고 무대 크기 인자는 무대 px)."""
import math
import os
from PIL import Image, ImageDraw, ImageFilter
from art_common import ensure_out, font

S = 4      # 무대 1px 당 그림 px (그린 뒤 2배 해상도로 줄임)


def _path(name):
    return os.path.join(ensure_out(), 'g3_%s.png' % name)


def art(name, w, h, draw):
    """draw(d, im, s) 로 (w×h 무대 px) 그림을 그려 2배 해상도 PNG 로 저장."""
    p = _path(name)
    if os.path.exists(p):
        return p
    im = Image.new('RGBA', (int(w * S), int(h * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw(d, im, S)
    im = im.resize((int(w * 2), int(h * 2)), Image.LANCZOS)
    im.save(p)
    return p


def disc(name, r, col, rim=(255, 255, 255), label=None, fsize=None, tcol=(255, 255, 255), rimw=1.5):
    def f(d, im, s):
        W = im.width
        d.ellipse((rimw * s, rimw * s, W - rimw * s, W - rimw * s), fill=col + (255,) if len(col) == 3 else col,
                  outline=rim + (255,) if rim else None, width=int(rimw * s) if rim else 0)
        d.ellipse((W * 0.22, W * 0.14, W * 0.5, W * 0.34), fill=(255, 255, 255, 60))
        if label is not None:
            d.text((W / 2, W / 2), str(label), font=font('jalnan', int((fsize or r) * s)), fill=tcol + (255,), anchor='mm')
    return art(name, r * 2, r * 2, f)


def box(name, w, h, col, label=None, fsize=None, tcol=(255, 255, 255), rim=(255, 255, 255), r=6, rimw=1.2, fname='jalnan'):
    def f(d, im, s):
        d.rounded_rectangle((rimw * s, rimw * s, im.width - rimw * s, im.height - rimw * s), r * s,
                            fill=col + (255,) if len(col) == 3 else col,
                            outline=(rim + (220,)) if rim else None, width=int(rimw * s) if rim else 0)
        d.rounded_rectangle((3 * s, 3 * s, im.width - 3 * s, im.height * 0.45), r * s, fill=(255, 255, 255, 28))
        if label is not None:
            d.text((im.width / 2, im.height / 2), str(label), font=font(fname, int((fsize or h * 0.5) * s)), fill=tcol + (255,),
                   anchor='mm')
    return art(name, w, h, f)


def poly(name, w, h, pts, col, rim=None, rimw=1.5):
    """pts: 0~1 비율 좌표."""
    def f(d, im, s):
        P = [(x * im.width, y * im.height) for x, y in pts]
        d.polygon(P, fill=col + (255,) if len(col) == 3 else col)
        if rim:
            d.line(P + [P[0]], fill=rim + (255,), width=int(rimw * s))
    return art(name, w, h, f)


def ring(name, r, col, width=2):
    def f(d, im, s):
        W = im.width
        d.ellipse((width * s, width * s, W - width * s, W - width * s), outline=col + (255,), width=int(width * s))
    return art(name, r * 2, r * 2, f)


def line_img(name, w, h, pts, col, width=2, dash=None):
    def f(d, im, s):
        P = [(x * im.width, y * im.height) for x, y in pts]
        if dash:
            for (x0, y0), (x1, y1) in zip(P, P[1:]):
                n = max(1, int(math.hypot(x1 - x0, y1 - y0) / (dash * s)))
                for k in range(0, n, 2):
                    d.line([(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n),
                            (x0 + (x1 - x0) * (k + 1) / n, y0 + (y1 - y0) * (k + 1) / n)], fill=col + (255,), width=int(width * s))
        else:
            d.line(P, fill=col + (255,), width=int(width * s), joint='curve')
    return art(name, w, h, f)


def glyph(name, txt, size, col=(255, 255, 255), fname='jalnan', outline=(0, 0, 0)):
    """글자 하나(또는 짧은 글)를 그림으로."""
    def f(d, im, s):
        fo = font(fname, int(size * s))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                d.text((im.width / 2 + dx * s, im.height / 2 + dy * s), txt, font=fo, fill=outline + (255,), anchor='mm')
        d.text((im.width / 2, im.height / 2), txt, font=fo, fill=col + (255,), anchor='mm')
    return art(name, size * max(1, len(txt)) * 1.1 + 4, size * 1.4, f)
