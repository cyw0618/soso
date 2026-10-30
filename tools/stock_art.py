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


# ================================================================== 업비트 스타일 (밝은 화면 + 남색 머리띠)
U = dict(navy=(9, 54, 135), red=(200, 74, 49), blue=(18, 97, 196), txt=(51, 51, 51), gray=(102, 102, 102),
         lgray=(153, 153, 153), page=(233, 236, 241), line=(222, 225, 231), line2=(241, 242, 245), ask=(238, 242, 251),
         bid=(251, 241, 239), sel=(238, 242, 250), white=(255, 255, 255), ctl=(255, 250, 232), ctl_line=(238, 214, 150),
         purple=(123, 75, 209))
UHEX = {k: '#%02x%02x%02x' % v for k, v in U.items()}

# 화면 배치 (무대 좌표). build() 와 그림이 같은 값을 쓴다
UL = dict(
    head=(117, 135), news=(102, 115),
    left=(-238, 54, -133, 99),           # 왼쪽 판: 종목 정보 + 차트 + 호가 + 주문
    chart=(-232, 20, 8, 64), vol=(-5, 4), axis_x=22,
    split_y=-9, hoga=(-238, -92), order=(-90, 54),
    right=(58, 238, -112, 99),           # 오른쪽 판: 탭 + 지배 자본 + 종목 목록
    tabs_y=93, ctl=(60, 236, 66, 86), list_head=(54, 64), row0=48.5, row_h=10.9, rows=15,
    hoga_y0=-26.5, hoga_h=10.6,
)


def _S(x, y):
    return ((x + 240) * 2, (135 - y) * 2)


def _rect(d, x0, y0, x1, y1, fill=None, outline=None, width=1):
    X0, Y0 = _S(x0, y1)
    X1, Y1 = _S(x1, y0)
    d.rectangle((X0, Y0, X1, Y1), fill=fill, outline=outline, width=width)


def _hline(d, x0, x1, y, col, width=1):
    d.line([_S(x0, y), _S(x1, y)], fill=col, width=width)


def _vline(d, x, y0, y1, col, width=1):
    d.line([_S(x, y0), _S(x, y1)], fill=col, width=width)


def _label(d, x, y, s, size, col, anchor='lm', bold=False):
    d.text(_S(x, y), s, font=font('nsr' if bold else 'nsrb', int(size * 2)), fill=col, anchor=anchor)


def upbit_bg():
    """거래소 배경: 바탕·판·머리띠·표 머리·호가 줄 색·주문 글 이름 (움직이지 않는 것은 모두 그림에)."""
    p = os.path.join(ensure_out(), 'upbit_bg_v2.png')
    if os.path.exists(p):
        return p
    im = Image.new('RGB', (W, H), U['page'])
    d = ImageDraw.Draw(im)
    # 머리띠
    _rect(d, -240, UL['head'][0], 240, 135, fill=U['navy'])
    X0, Y0 = _S(-234, 131)
    X1, Y1 = _S(-222, 121)
    d.rounded_rectangle((X0, Y0, X1, Y1), 5, fill=U['white'])
    cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
    d.polygon([(cx - 6, cy + 4), (cx, cy - 6), (cx + 6, cy + 4)], fill=U['navy'])
    _label(d, -218, 126.5, '조치원 거래소', 8.5, U['white'], bold=True)
    # 뉴스 띠
    _rect(d, -238, UL['news'][0], 238, UL['news'][1], fill=U['white'], outline=U['line'])
    # 왼쪽 판
    l0, l1, b0, b1 = UL['left']
    _rect(d, l0, b0, l1, b1, fill=U['white'], outline=U['line'])
    _hline(d, l0 + 2, l1 - 2, 68, U['line2'])
    # 차트: 가로 눈금, 세로 눈금, 오른쪽 가격축, 거래량 바닥
    cx0, cx1, cy0, cy1 = UL['chart']
    for k in range(5):
        y = cy0 + (cy1 - cy0) * k / 4.0
        for x in range(int(cx0), int(cx1), 4):
            _hline(d, x, x + 2, y, U['line2'])
    for k in range(1, 4):
        x = cx0 + (cx1 - cx0) * k / 4.0
        _vline(d, x, UL['vol'][0], cy1, U['line2'])
    _vline(d, UL['axis_x'], UL['vol'][0] - 1, cy1 + 2, U['line'])
    _hline(d, cx0, UL['axis_x'], UL['vol'][0] - 0.5, U['line'])
    _label(d, cx0, UL['vol'][1] + 1.5, '거래량', 5, U['lgray'])
    # 호가 · 주문 나눔
    _hline(d, l0 + 1, l1 - 1, UL['split_y'], U['line'])
    h0, h1 = UL['hoga']
    o0, o1 = UL['order']
    _vline(d, o0 - 1, b0 + 1, UL['split_y'], U['line'])
    _label(d, (h0 + h1) / 2, UL['split_y'] - 6, '호가 · 잔량', 6, U['gray'], 'mm', True)
    for r in range(1, 11):
        y = UL['hoga_y0'] - (r - 1) * UL['hoga_h']
        _rect(d, h0 + 1, y - UL['hoga_h'] / 2 + 0.6, h1 - 1, y + UL['hoga_h'] / 2 - 0.6, fill=U['ask'] if r <= 5 else U['bid'])
    for lbl, y in (('주문가능', -32), ('보유', -43), ('평가손익', -54), ('주문총액', -82)):
        _label(d, o0 + 2, y, lbl, 6, U['gray'])
    # 오른쪽 판
    r0, r1, rb0, rb1 = UL['right']
    _rect(d, r0, rb0, r1, rb1, fill=U['white'], outline=U['line'])
    _hline(d, r0 + 1, r1 - 1, UL['tabs_y'] - 6.5, U['line'])
    lh0, lh1 = UL['list_head']
    _rect(d, r0 + 1, lh0, r1 - 1, lh1, fill=(249, 250, 252))
    _hline(d, r0 + 1, r1 - 1, lh0, U['line'])
    _label(d, 62, (lh0 + lh1) / 2, '한글명', 6, U['gray'])
    _label(d, 160, (lh0 + lh1) / 2, '현재가', 6, U['gray'], 'rm')
    _label(d, 198, (lh0 + lh1) / 2, '전일대비', 6, U['gray'], 'rm')
    _label(d, 236, (lh0 + lh1) / 2, '거래대금', 6, U['gray'], 'rm')
    im.save(p)
    return p


def _flat(w, h, fill, outline=None, text=None, tcol=(255, 255, 255), fsize=None, r=2.5, bold=True, under=None):
    """평평한 버튼·칩·탭 그림 (2배 해상도)."""
    s = R2 * SS
    im = Image.new('RGBA', (int(w * s), int(h * s)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = (0.5 * s, 0.5 * s, w * s - 0.5 * s, h * s - 0.5 * s)
    if fill is not None or outline is not None:
        d.rounded_rectangle(box, r * s, fill=(fill + (255,)) if fill else None,
                            outline=(outline + (255,)) if outline else None, width=int(0.8 * s))
    if under:
        d.rectangle((0, h * s - 1.6 * s, w * s, h * s), fill=under + (255,))
    if text:
        f = font('nsr' if bold else 'nsrb', int((fsize or h * 0.58) * s))
        d.text((w * s / 2, h * s / 2 - (0.6 * s if under else 0)), text, font=f, fill=tcol + (255,), anchor='mm')
    return _fin(im, w, h, 'u_%s' % K._k(w, h, fill, outline, text, tcol, fsize, r, bold, under))


def u_button(label, w, h, kind):
    """kind: buy(빨강) sell(파랑) nav(흰 바탕 테두리) navy(남색)."""
    if kind == 'buy':
        return _flat(w, h, U['red'], text=label, fsize=h * 0.5)
    if kind == 'sell':
        return _flat(w, h, U['blue'], text=label, fsize=h * 0.5)
    if kind == 'navy':
        return _flat(w, h, U['navy'], text=label, fsize=h * 0.5)
    return _flat(w, h, U['white'], outline=U['line'], text=label, tcol=U['txt'], fsize=h * 0.5)


def u_chip(label, w, h=11):
    """[('off', …), ('on', …)] 주문 모드·수량 칩."""
    return [('off', _flat(w, h, U['white'], outline=(213, 214, 220), text=label, tcol=U['gray'], fsize=6, bold=False)),
            ('on', _flat(w, h, U['navy'], text=label, fsize=6))]


def u_tab(label, w=44, h=12):
    return [('off', _flat(w, h, None, text=label, tcol=U['lgray'], fsize=7, bold=False)),
            ('on', _flat(w, h, None, text=label, tcol=U['navy'], fsize=7, under=U['navy'])),
            ('lock', _flat(w, h, None, text='잠김', tcol=(200, 200, 205), fsize=6.5, bold=False))]


def u_news_tag(kind):
    col = {'속보': U['red'], '루머': U['purple'], '시황': U['navy'], '장마감': U['lgray']}[kind]
    return _flat(26, 10, col, text=kind, fsize=5.6)


def u_square(col, alpha=255, name=''):
    """캔들·거래량·호가 막대용 정사각형 (무대 10×10): 늘리고 줄여서 쓴다."""
    im = Image.new('RGBA', (20, 20), col + (alpha,))
    p = os.path.join(ensure_out(), 'u_sq_%s_%d_%d_%d_%d.png' % ((name,) + col + (alpha,)))
    im.save(p)
    return p


ROW_W = UL['right'][1] - UL['right'][0] - 2


def u_row(state):
    """목록 한 줄 바탕: n 보통, s 고른 줄 / 뒤에 u·d 가 붙으면 방금 가격이 오름·내림 (현재가 칸 테두리)."""
    w, h = ROW_W, UL['row_h']
    s = R2 * SS
    im = Image.new('RGBA', (int(w * s), int(h * s)), (U['sel'] if 's' in state else U['white']) + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, h * s - 0.7 * s, w * s, h * s), fill=U['line2'] + (255,))
    if 'u' in state or 'd' in state:
        col = U['red'] if 'u' in state else U['blue']
        x0 = (112 - UL['right'][0] - 1) * s
        x1 = (161 - UL['right'][0] - 1) * s
        d.rectangle((x0, 0.8 * s, x1, h * s - 1.2 * s), outline=col + (255,), width=int(0.8 * s))
    return _fin(im, w, h, 'u_row_%s' % state)


def u_row_set():
    return [(st, u_row(st)) for st in ('n', 'nu', 'nd', 's', 'su', 'sd')]


def u_ctl(sel=False):
    """지배 자본 띠 (오른쪽 위): 연한 노랑 + 지분 막대 자리 + 50% 표시."""
    x0, x1, y0, y1 = UL['ctl']
    w, h = x1 - x0, y1 - y0
    s = R2 * SS
    im = Image.new('RGBA', (int(w * s), int(h * s)), U['ctl'] + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w * s - 1, h * s - 1), outline=(U['navy'] if sel else U['ctl_line']) + (255,), width=int((1.2 if sel else 0.7) * s))
    # 50% 표시 (막대 가운데)
    bx = (CTL_BAR[0] + CTL_BAR[1]) / 2 - x0
    by = y1 - CTL_BAR[2]
    d.line([(bx * s, (by - 2.6) * s), (bx * s, (by + 2.6) * s)], fill=U['txt'] + (255,), width=int(0.7 * s))
    return _fin(im, w, h, 'u_ctl2_%s' % ('sel' if sel else 'on'))


CTL_BAR = (64, 232, 69.5)    # 지분 막대: 왼쪽 x, 오른쪽 x, y (무대)
