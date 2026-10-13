# -*- coding: utf-8 -*-
"""증권거래소 화면 그림: 배경, 시세 칸(보합/오름/내림 × 선택), 지배 자본 카드, 차트 틀, 50% 표시. (2배 해상도)"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from art_common import *
import ui_kit as K

R2, SS = 2, 3
W, H = 960, 540


def _cv(w, h):
    return Image.new('RGBA', (int(w * R2 * SS), int(h * R2 * SS)), (0, 0, 0, 0))


def _fin(im, w, h, name):
    im = im.resize((int(w * R2), int(h * R2)), Image.LANCZOS)
    return save(im, name)


def exchange_bg():
    """어두운 거래소 배경: 검정→남색, 희미한 격자와 캔들 차트 실루엣, 위쪽 청색 빛."""
    p = os.path.join(ensure_out(), 'stock_bg.png')
    if os.path.exists(p):
        return p
    rng = random.Random(7)
    im = vgradient((W, H), (2, 3, 10), (8, 12, 34)).convert('RGBA')
    d = ImageDraw.Draw(im)
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(30, 44, 96, 40), width=1)
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(30, 44, 96, 40), width=1)
    # 캔들 실루엣
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    v = 300.0
    for i in range(64):
        x = 8 + i * 15
        o = v
        v = max(120, min(470, v + rng.uniform(-26, 24)))
        hi, lo = min(o, v) - rng.uniform(4, 18), max(o, v) + rng.uniform(4, 18)
        col = (200, 40, 60, 60) if v < o else (40, 80, 220, 60)
        ld.line([(x + 4, hi), (x + 4, lo)], fill=col, width=1)
        ld.rectangle((x, min(o, v), x + 8, max(o, v) + 1), fill=col)
    lay = lay.filter(ImageFilter.GaussianBlur(1.2))
    im.alpha_composite(lay)
    # 위쪽 청색 빛
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).ellipse((-200, -260, W + 200, 160), fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    gl = Image.new('RGBA', (W, H), (30, 60, 200, 255))
    gl.putalpha(glow)
    im.alpha_composite(gl)
    # 아래 비네트
    vm = Image.new('L', (W, H), 0)
    vd = ImageDraw.Draw(vm)
    for y in range(H):
        a = int(150 * max(0, (y - H * 0.55) / (H * 0.45)) ** 1.5)
        vd.line([(0, y), (W, y)], fill=a)
    dk = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    dk.putalpha(vm)
    im.alpha_composite(dk)
    im.convert('RGB').save(p)
    return p


TILE_W, TILE_H = 84, 25


def stock_tile(state):
    """state: f(보합) u(오름) d(내림), 뒤에 s 가 붙으면 선택됨."""
    base = state[0]
    sel = state.endswith('s')
    w, h = TILE_W, TILE_H
    im = _cv(w, h)
    Wc, Hc = im.size
    s = R2 * SS
    cols = {'f': ((20, 24, 46), (5, 6, 16), (64, 80, 140)),
            'u': ((54, 12, 24), (16, 3, 8), (226, 56, 78)),
            'd': ((12, 22, 64), (3, 6, 20), (64, 108, 255))}[base]
    box = (1.5 * s, 1.5 * s, Wc - 1.5 * s, Hc - 1.5 * s)
    rr = 5 * s
    if sel:
        gm = Image.new('L', im.size, 0)
        ImageDraw.Draw(gm).rounded_rectangle(box, rr, outline=255, width=int(2.4 * s))
        gm = gm.filter(ImageFilter.GaussianBlur(1.6 * s))
        g = Image.new('RGBA', im.size, (90, 130, 255, 255))
        g.putalpha(gm)
        im.alpha_composite(g)
    body = K._grad(im.size, cols[0], cols[1])
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, rr, fill=240)
    body.putalpha(m)
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    # 왼쪽 색 띠
    d.rounded_rectangle((box[0] + 1 * s, box[1] + 3 * s, box[0] + 3 * s, box[3] - 3 * s), 1 * s, fill=cols[2] + (255,))
    d.rounded_rectangle(box, rr, outline=(cols[2] if not sel else (200, 214, 255)) + (255,), width=int((1.6 if sel else 1.0) * s))
    return _fin(im, w, h, 'stock_tile_%s' % state)


def tile_set():
    return [(st, stock_tile(st)) for st in ('f', 'u', 'd', 'fs', 'us', 'ds')]


def control_card(w=262, h=44, sel=False):
    im = _cv(w, h)
    Wc, Hc = im.size
    s = R2 * SS
    box = (2 * s, 2 * s, Wc - 2 * s, Hc - 2 * s)
    rr = 8 * s
    gm = Image.new('L', im.size, 0)
    ImageDraw.Draw(gm).rounded_rectangle(box, rr, outline=255, width=int((3 if sel else 2) * s))
    gm = gm.filter(ImageFilter.GaussianBlur(2.2 * s))
    g = Image.new('RGBA', im.size, (40, 90, 255, 255))
    g.putalpha(gm.point(lambda v: min(255, v * (2 if sel else 1))))
    im.alpha_composite(g)
    body = K._grad(im.size, (18, 24, 60), (2, 3, 12))
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, rr, fill=246)
    body.putalpha(m)
    im.alpha_composite(body)
    bg_ = K._grad(im.size, (150, 176, 255), (30, 50, 150))
    bm = Image.new('L', im.size, 0)
    ImageDraw.Draw(bm).rounded_rectangle(box, rr, outline=255, width=int((1.8 if sel else 1.2) * s))
    bg_.putalpha(bm)
    im.alpha_composite(bg_)
    d = ImageDraw.Draw(im)
    # 왕관 무늬 (지배)
    cx, cy = box[0] + 12 * s, box[1] + 10 * s
    pts = [(cx - 7 * s, cy + 4 * s), (cx - 7 * s, cy - 4 * s), (cx - 3.5 * s, cy), (cx, cy - 6 * s), (cx + 3.5 * s, cy),
           (cx + 7 * s, cy - 4 * s), (cx + 7 * s, cy + 4 * s)]
    d.polygon(pts, fill=(200, 214, 255, 255), outline=(10, 16, 50, 255))
    return _fin(im, w, h, 'stock_control_%s' % ('sel' if sel else 'on'))


def goal_marker(h=16):
    w = 22
    im = _cv(w, h)
    Wc, Hc = im.size
    s = R2 * SS
    d = ImageDraw.Draw(im)
    cx = Wc / 2
    d.line([(cx, 0), (cx, Hc)], fill=(255, 255, 255, 230), width=int(1.2 * s))
    d.polygon([(cx - 3 * s, 0), (cx + 3 * s, 0), (cx, 3.5 * s)], fill=(255, 255, 255, 255))
    return _fin(im, w, h, 'stock_goal_marker')


def chart_frame(w=196, h=56):
    im = _cv(w, h)
    Wc, Hc = im.size
    s = R2 * SS
    box = (1 * s, 1 * s, Wc - 1 * s, Hc - 1 * s)
    body = K._grad(im.size, (4, 6, 18), (0, 0, 4))
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, 6 * s, fill=235)
    body.putalpha(m)
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    for i in range(1, 4):
        y = box[1] + (box[3] - box[1]) * i / 4
        for x in range(int(box[0] + 6 * s), int(box[2] - 6 * s), int(6 * s)):
            d.line([(x, y), (x + 3 * s, y)], fill=(60, 80, 150, 90), width=max(1, int(0.5 * s)))
    for i in range(1, 6):
        x = box[0] + (box[2] - box[0]) * i / 6
        d.line([(x, box[1] + 4 * s), (x, box[3] - 4 * s)], fill=(60, 80, 150, 50), width=max(1, int(0.5 * s)))
    d.rounded_rectangle(box, 6 * s, outline=(60, 84, 170, 255), width=int(1 * s))
    return _fin(im, w, h, 'stock_chart_frame')


def news_bar(w=336, h=20):
    im = _cv(w, h)
    Wc, Hc = im.size
    s = R2 * SS
    box = (1 * s, 1 * s, Wc - 1 * s, Hc - 1 * s)
    body = K._grad(im.size, (12, 16, 36), (2, 2, 8))
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, 4 * s, fill=235)
    body.putalpha(m)
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, 4 * s, outline=(54, 76, 160, 255), width=int(1 * s))
    return _fin(im, w, h, 'stock_news_bar')


def news_tag(kind):
    col = {'속보': 'red', '루머': 'purple', '시황': 'navy', '장마감': 'gray'}[kind]
    return K.badge(kind, 34, 16, col)


def pie_ring(size=120):
    """지분 원그래프 바탕(어두운 원 + 테두리)."""
    im = _cv(size, size)
    Wc = im.width
    s = R2 * SS
    d = ImageDraw.Draw(im)
    d.ellipse((2 * s, 2 * s, Wc - 2 * s, Wc - 2 * s), fill=(6, 8, 20, 240), outline=(80, 110, 230, 255), width=int(1.4 * s))
    return _fin(im, size, size, 'stock_pie_ring')
