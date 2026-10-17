# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 21~30번 그림 (mg_art3.art 사용: 무대 px 단위로 그리고 2배 해상도로 저장)."""
import math
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3

art = A3.art


def _c(col, a=255):
    return tuple(col[:3]) + (a,)


def _shade(col, k):
    """k<1 어둡게, k>1 밝게."""
    if k <= 1:
        return tuple(int(c * k) for c in col[:3])
    return tuple(int(c + (255 - c) * (k - 1)) for c in col[:3])


def _blur_layer(im, draw_fn, radius):
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(radius)))


# ================================================================== 21. 농구 자유투
def s21_ball():
    def f(d, im, s):
        W = im.width
        d.ellipse((0.5 * s, 0.5 * s, W - 0.5 * s, W - 0.5 * s), fill=(236, 112, 34, 255), outline=(60, 22, 6, 255), width=int(1 * s))
        d.ellipse((W * 0.18, W * 0.12, W * 0.55, W * 0.4), fill=(255, 200, 150, 90))
        lw = max(1, int(0.7 * s))
        d.line([(W / 2, 1 * s), (W / 2, W - 1 * s)], fill=(50, 18, 6, 255), width=lw)
        d.line([(1 * s, W / 2), (W - 1 * s, W / 2)], fill=(50, 18, 6, 255), width=lw)
        d.arc((-W * 0.35, W * 0.1, W * 0.42, W * 0.9), -60, 60, fill=(50, 18, 6, 255), width=lw)
        d.arc((W * 0.58, W * 0.1, W * 1.35, W * 0.9), 120, 240, fill=(50, 18, 6, 255), width=lw)
    return art('s21_ball', 14, 14, f)


# 골대 좌표 (무대): 림 앞 x=144, 뒤 x=180, 높이 y=22, 백보드 앞면 x=186 (y 12~78), 기둥 x=212
def s21_hoop():
    X0, Y0 = 136, 84      # 그림 왼쪽 위 = 무대 (136, 84)

    def f(d, im, s):
        P = lambda x, y: ((x - X0) * s, (Y0 - y) * s)
        # 기둥과 받침
        d.rectangle((*P(206, 46), *P(216, -100)), fill=(70, 80, 110, 255), outline=(20, 24, 40, 255), width=int(1 * s))
        d.rectangle((*P(208, 46), *P(210, -100)), fill=(130, 140, 170, 255))
        d.polygon([P(190, 50), P(212, 50), P(212, 40), P(190, 44)], fill=(60, 70, 100, 255), outline=(20, 24, 40, 255))
        d.rounded_rectangle((*P(198, -92), *P(224, -101)), 2 * s, fill=(40, 46, 70, 255))
        # 백보드
        d.rectangle((*P(186, 80), *P(192, 10)), fill=(230, 236, 250, 255), outline=(30, 36, 60, 255), width=int(1 * s))
        d.rectangle((*P(186, 44), *P(188, 24)), fill=(220, 50, 60, 255))
        # 림 뒤쪽 반 + 그물 뒤쪽
        d.ellipse((*P(142, 26), *P(184, 18)), outline=(170, 60, 20, 255), width=int(2 * s))
        d.rectangle((*P(180, 24), *P(187, 20)), fill=(200, 80, 30, 255))
        for k in range(6):
            x0 = 146 + k * 6.6
            d.line([P(x0, 21), P(152 + k * 4.2, -6)], fill=(200, 205, 225, 150), width=max(1, int(0.6 * s)))
    return art('s21_hoop', 92, 186, f)


def s21_rim(swish):
    X0, Y0 = 136, 30

    def f(d, im, s):
        P = lambda x, y: ((x - X0) * s, (Y0 - y) * s)
        lw = max(1, int(0.8 * s))
        bot = -6 if not swish else -12
        narrow = 0 if not swish else 3
        # 그물 앞쪽
        for k in range(7):
            x0 = 145 + k * 5.6
            x1 = 152 + narrow + k * (4.2 - narrow / 3)
            d.line([P(x0, 20), P(x1, bot)], fill=(240, 244, 255, 230), width=lw)
            d.line([P(x0, 20), P(x1 + 6, bot)], fill=(240, 244, 255, 150), width=lw)
        for yy, k in ((12, 0.2), (3, 0.45)):
            d.line([P(145 + k * 8, yy), P(181 - k * 8, yy)], fill=(240, 244, 255, 170), width=lw)
        d.line([P(151 + narrow, bot), P(178 - narrow, bot)], fill=(240, 244, 255, 200), width=lw)
        # 림 앞쪽 (둥근 테)
        d.arc((*P(142, 26), *P(184, 18)), 0, 180, fill=(236, 96, 30, 255), width=int(2.4 * s))
    return art('s21_rim_%d' % swish, 52, 46, f)


def s21_player(pose):
    """옆모습 선수 (오른쪽을 봄). pose: ready / shot. 발 = 그림 아래, 크기 34x76."""
    def f(d, im, s):
        P = lambda x, y: (x * s, y * s)
        skin = (240, 204, 170, 255)
        shirt = (44, 84, 220, 255)
        dark = (14, 22, 60, 255)
        # 다리
        d.line([P(15, 50), P(13, 72)], fill=(30, 34, 60, 255), width=int(5 * s))
        if pose == 'shot':
            d.line([P(19, 50), P(22, 72)], fill=(30, 34, 60, 255), width=int(5 * s))
        else:
            d.line([P(19, 50), P(20, 61), P(17, 72)], fill=(30, 34, 60, 255), width=int(5 * s), joint='curve')
        for x in (13, 20):
            d.rounded_rectangle((*P(x - 4, 71), *P(x + 6, 75.5)), 2 * s, fill=(240, 240, 250, 255), outline=dark, width=int(0.6 * s))
        # 몸 (유니폼 + 번호)
        d.rounded_rectangle((*P(9, 28), *P(25, 53)), 5 * s, fill=shirt, outline=dark, width=int(0.8 * s))
        d.rectangle((*P(9, 47), *P(25, 53)), fill=(30, 50, 150, 255))
        d.text(P(17, 38), '7', font=font('jalnan', int(9 * s)), fill=(255, 255, 255, 255), anchor='mm')
        # 머리
        d.ellipse((*P(9, 12), *P(25, 28)), fill=skin, outline=(60, 40, 30, 255), width=int(0.6 * s))
        d.chord((*P(9, 11), *P(25, 24)), 180, 360, fill=(30, 26, 34, 255))
        d.ellipse((*P(20, 18), *P(22, 20)), fill=(20, 20, 30, 255))
        d.rectangle((*P(9, 15), *P(25, 17)), fill=(230, 60, 80, 255))
        # 팔
        if pose == 'ready':
            d.line([P(14, 31), P(20, 18), P(25, 8)], fill=skin, width=int(3.6 * s), joint='curve')
            d.line([P(20, 31), P(26, 20), P(29, 9)], fill=skin, width=int(3.6 * s), joint='curve')
        else:
            d.line([P(14, 31), P(22, 14), P(30, 2)], fill=skin, width=int(3.6 * s), joint='curve')
            d.line([P(20, 31), P(27, 16), P(33, 4)], fill=skin, width=int(3.6 * s), joint='curve')
    return art('s21_player_%s' % pose, 36, 76, f)


def s21_aim():
    """회전 중심 = 그림 가운데. 오른쪽 절반에 점선 화살표 (길이 56)."""
    def f(d, im, s):
        H = im.height
        cy = H / 2
        x0 = im.width / 2 + 9 * s
        for k in range(6):
            a = x0 + k * 7.5 * s
            d.ellipse((a, cy - 1.6 * s, a + 3.2 * s, cy + 1.6 * s), fill=(255, 255, 255, 120 + k * 22))
        tip = im.width / 2 + 60 * s
        d.polygon([(tip, cy), (tip - 9 * s, cy - 5 * s), (tip - 9 * s, cy + 5 * s)], fill=(255, 255, 255, 255),
                  outline=(20, 30, 90, 255))
    return art('s21_aim', 124, 14, f)


def s21_floor():
    def f(d, im, s):
        W, H = im.size
        for y in range(int(H)):
            k = y / H
            d.line([(0, y), (W, y)], fill=(int(150 - 60 * k), int(98 - 40 * k), int(58 - 26 * k), 255))
        for k in range(14):
            x = k * 36 * s
            d.line([(x, 0), (x - 10 * s, H)], fill=(90, 56, 30, 120), width=int(0.6 * s))
        d.line([(0, 1 * s), (W, 1 * s)], fill=(255, 236, 200, 200), width=int(1.4 * s))
    return art('s21_floor', 480, 36, f)


def s21_mark():
    def f(d, im, s):
        W, H = im.size
        d.polygon([(0, H), (W, H), (W * 0.8, 0), (W * 0.2, 0)], fill=(255, 255, 255, 220))
    return art('s21_mark', 20, 4, f)


# ================================================================== 22. 다운힐 슬라롬 (위에서 본 모습)
def s22_bike(crash=False):
    """앞바퀴가 아래쪽. 20x40."""
    def f(d, im, s):
        P = lambda x, y: (x * s, y * s)
        tire = (20, 22, 30, 255)
        d.rounded_rectangle((*P(8.2, 23), *P(11.8, 39)), 1.6 * s, fill=tire)     # 앞바퀴
        d.rounded_rectangle((*P(8.2, 1), *P(11.8, 16)), 1.6 * s, fill=tire)      # 뒷바퀴
        d.line([P(10, 8), P(10, 31)], fill=(70, 120, 255, 255), width=int(2.2 * s))
        d.line([P(3, 28), P(17, 28)], fill=(200, 210, 230, 255), width=int(1.6 * s))   # 핸들
        d.ellipse((*P(1.5, 26.5), *P(4.5, 29.5)), fill=(30, 30, 40, 255))
        d.ellipse((*P(15.5, 26.5), *P(18.5, 29.5)), fill=(30, 30, 40, 255))
        # 선수: 어깨·팔·헬멧
        body = (40, 80, 220, 255) if not crash else (200, 60, 80, 255)
        d.line([P(5, 18), P(3.2, 27)], fill=body, width=int(2.4 * s))
        d.line([P(15, 18), P(16.8, 27)], fill=body, width=int(2.4 * s))
        d.ellipse((*P(4, 11), *P(16, 23)), fill=body, outline=(10, 16, 50, 255), width=int(0.6 * s))
        d.ellipse((*P(6, 16), *P(14, 26)), fill=(240, 244, 255, 255), outline=(20, 30, 70, 255), width=int(0.6 * s))
        d.line([P(10, 16.5), P(10, 25.5)], fill=(230, 60, 80, 255), width=int(1.2 * s))
    return art('s22_bike_%d' % crash, 20, 40, f)


def s22_gate(state):
    """state: n 보통 / ok 통과 / x 놓침. 폭 80: 깃대 x=8, 72 (가운데에서 ±32)."""
    def f(d, im, s):
        P = lambda x, y: (x * s, y * s)
        cy = 22
        if state == 'ok':
            d.line([P(10, cy), P(70, cy)], fill=(80, 255, 150, 230), width=int(2.4 * s))
        elif state == 'x':
            d.line([P(10, cy), P(70, cy)], fill=(255, 80, 100, 200), width=int(1.6 * s))
        else:
            for k in range(10):
                x = 13 + k * 6
                d.line([P(x, cy), P(x + 3, cy)], fill=(255, 255, 255, 170), width=int(1.2 * s))
        for x, col in ((8, (230, 50, 70)), (72, (50, 110, 255))):
            d.ellipse((*P(x - 4, cy - 3), *P(x + 4, cy + 3)), fill=(0, 0, 0, 70))
            d.ellipse((*P(x - 2.2, cy - 2.2), *P(x + 2.2, cy + 2.2)), fill=(240, 240, 250, 255), outline=(30, 30, 40, 255),
                      width=int(0.5 * s))
            sgn = 1 if x < 40 else -1
            d.polygon([P(x, cy - 2), P(x, cy - 18), P(x + sgn * 13, cy - 11)], fill=_c(col), outline=(20, 10, 20, 255))
        if state == 'x':
            d.line([P(34, cy - 6), P(46, cy + 6)], fill=(255, 80, 100, 255), width=int(2 * s))
            d.line([P(46, cy - 6), P(34, cy + 6)], fill=(255, 80, 100, 255), width=int(2 * s))
    return art('s22_gate_%s' % state, 80, 30, f)


def s22_rock():
    def f(d, im, s):
        P = lambda x, y: (x * s, y * s)
        d.ellipse((*P(2, 6), *P(24, 20)), fill=(0, 0, 0, 80))
        d.polygon([P(2, 13), P(6, 4), P(14, 1.5), P(21, 5), P(23, 13), P(17, 18), P(7, 18)], fill=(118, 116, 130, 255),
                  outline=(40, 40, 52, 255))
        d.polygon([P(6, 5), P(14, 2.5), P(18, 7), P(10, 9)], fill=(170, 170, 186, 255))
    return art('s22_rock', 26, 21, f)


def s22_tree(kind):
    def f(d, im, s):
        W = im.width
        c = W / 2
        d.ellipse((c - 15 * s + 3 * s, c - 15 * s + 4 * s, c + 15 * s + 3 * s, c + 15 * s + 4 * s), fill=(0, 0, 0, 90))
        if kind == 0:
            d.ellipse((c - 15 * s, c - 15 * s, c + 15 * s, c + 15 * s), fill=(28, 92, 70, 255), outline=(10, 40, 30, 255),
                      width=int(0.8 * s))
            for (dx, dy, r) in ((-5, -5, 8), (5, -2, 7), (-1, 6, 7)):
                d.ellipse((c + (dx - r) * s, c + (dy - r) * s, c + (dx + r) * s, c + (dy + r) * s), fill=(44, 130, 92, 255))
            d.ellipse((c - 8 * s, c - 10 * s, c - 1 * s, c - 4 * s), fill=(120, 200, 150, 120))
        else:
            pts = []
            for i in range(16):
                a = i * math.pi / 8
                r = 15 if i % 2 == 0 else 10
                pts.append((c + r * s * math.cos(a), c + r * s * math.sin(a)))
            d.polygon(pts, fill=(22, 70, 64, 255), outline=(8, 30, 28, 255))
            pts2 = [(c + (p[0] - c) * 0.6, c + (p[1] - c) * 0.6) for p in pts]
            d.polygon(pts2, fill=(36, 104, 88, 255))
            d.ellipse((c - 2 * s, c - 2 * s, c + 2 * s, c + 2 * s), fill=(90, 60, 40, 255))
    return art('s22_tree_%d' % kind, 38, 38, f)


def s22_road():
    def f(d, im, s):
        W, H = im.size
        d.rectangle((0, 0, W, H), fill=(58, 54, 62, 236))
        d.rectangle((10 * s, 0, W - 10 * s, H), fill=(84, 78, 84, 240))
        d.rectangle((14 * s, 0, W - 14 * s, H), fill=(96, 90, 94, 240))
        for x in (10 * s, W - 10 * s):
            d.line([(x, 0), (x, H)], fill=(230, 230, 240, 160), width=int(1.2 * s))
    return art('s22_road', 344, 236, f)


def s22_dot(k):
    def f(d, im, s):
        W, H = im.size
        cols = [(120, 112, 118, 255), (66, 60, 68, 255), (136, 128, 132, 255)]
        d.ellipse((0, 0, W, H), fill=cols[k % 3])
    return art('s22_dot_%d' % k, 4 + k, 3 + k * 0.6, f)


# ================================================================== 23. 불량품 골라내기 (도면 · 부품)
S23_SHAPES = [
    [(0, 0), (0, 1), (0, 2), (1, 2)],                       # L
    [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)],               # P
    [(0, 1), (1, 0), (1, 1), (1, 2), (1, 3)],               # Y
    [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3)],               # N
    [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)],               # F
    [(0, 0), (1, 0), (1, 1), (2, 1), (1, 2), (1, 3)],       # 6칸
]


def _cells_draw(d, cells, ox, oy, cs, s, fill, edge, ew, hole=None):
    cs_ = set(cells)
    for (x, y) in cells:
        d.rectangle((ox + x * cs * s, oy + y * cs * s, ox + (x + 1) * cs * s, oy + (y + 1) * cs * s), fill=fill)
    for (x, y) in cells:
        x0, y0, x1, y1 = ox + x * cs * s, oy + y * cs * s, ox + (x + 1) * cs * s, oy + (y + 1) * cs * s
        if (x, y - 1) not in cs_:
            d.line([(x0, y0), (x1, y0)], fill=edge, width=int(ew * s))
        if (x, y + 1) not in cs_:
            d.line([(x0, y1), (x1, y1)], fill=edge, width=int(ew * s))
        if (x - 1, y) not in cs_:
            d.line([(x0, y0), (x0, y1)], fill=edge, width=int(ew * s))
        if (x + 1, y) not in cs_:
            d.line([(x1, y0), (x1, y1)], fill=edge, width=int(ew * s))
        if hole:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            r = cs * s * 0.18
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hole[0], outline=hole[1], width=max(1, int(0.5 * s)))


def s23_part(i, mirror):
    cells = S23_SHAPES[i]
    if mirror:
        mx = max(x for x, y in cells)
        cells = [(mx - x, y) for x, y in cells]
    cs = 16
    gw = max(x for x, y in cells) + 1
    gh = max(y for x, y in cells) + 1
    size = 4 * cs + 6

    def f(d, im, s):
        ox = (im.width - gw * cs * s) / 2
        oy = (im.height - gh * cs * s) / 2
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        _cells_draw(ImageDraw.Draw(sh), cells, ox + 1.5 * s, oy + 2 * s, cs, s, (0, 0, 0, 110), (0, 0, 0, 110), 1)
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.5 * s)))
        d2 = ImageDraw.Draw(im)
        _cells_draw(d2, cells, ox, oy, cs, s, (150, 162, 192, 255), (24, 30, 52, 255), 1.6,
                    hole=((40, 46, 70, 255), (220, 228, 250, 255)))
        for (x, y) in cells:   # 윗면 반사
            d2.rectangle((ox + (x + 0.12) * cs * s, oy + (y + 0.1) * cs * s, ox + (x + 0.88) * cs * s, oy + (y + 0.3) * cs * s),
                         fill=(255, 255, 255, 50))
    return art('s23_part_%d_%d' % (i, mirror), size, size, f)


def s23_plan(i):
    cells = S23_SHAPES[i]
    cs = 20
    gw = max(x for x, y in cells) + 1
    gh = max(y for x, y in cells) + 1

    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 6 * s, fill=(22, 62, 160, 255), outline=(200, 220, 255, 255),
                            width=int(1.4 * s))
        for k in range(1, 12):
            d.line([(k * 11 * s, 22 * s), (k * 11 * s, H - 4 * s)], fill=(120, 160, 240, 60), width=max(1, int(0.5 * s)))
        for k in range(3, 14):
            d.line([(4 * s, k * 11 * s), (W - 4 * s, k * 11 * s)], fill=(120, 160, 240, 60), width=max(1, int(0.5 * s)))
        d.rectangle((1.5 * s, 1.5 * s, W - 1.5 * s, 18 * s), fill=(14, 40, 110, 255))
        d.text((W / 2, 10 * s), '도면 No.%d' % (i + 1), font=font('jalnan', int(10 * s)), fill=(230, 240, 255, 255), anchor='mm')
        ox = (W - gw * cs * s) / 2
        oy = 20 * s + (H - 20 * s - gh * cs * s) / 2
        _cells_draw(d, cells, ox, oy, cs, s, (60, 110, 220, 255), (240, 248, 255, 255), 1.8,
                    hole=((22, 62, 160, 255), (240, 248, 255, 255)))
        # 치수선 느낌
        d.line([(ox, H - 7 * s), (ox + gw * cs * s, H - 7 * s)], fill=(200, 220, 255, 160), width=max(1, int(0.6 * s)))
    return art('s23_plan_%d' % i, 120, 132, f)


def s23_belt(phase):
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((0, 2 * s, W, H - 2 * s), 7 * s, fill=(30, 34, 48, 255), outline=(8, 10, 20, 255), width=int(1 * s))
        d.rectangle((6 * s, 5 * s, W - 6 * s, 12 * s), fill=(58, 62, 80, 255))
        for k in range(-1, 40):
            x = (k * 12 + phase * 6) * s
            d.line([(x, 5 * s), (x + 4 * s, 12 * s)], fill=(90, 96, 120, 255), width=int(1.2 * s))
        for k in range(12):
            cx = (12 + k * 28) * s
            d.ellipse((cx - 4 * s, 14 * s, cx + 4 * s, 22 * s), fill=(70, 76, 100, 255), outline=(10, 12, 20, 255))
    return art('s23_belt_%d' % phase, 330, 24, f)


def s23_scanner(state):
    """state: n 보통 / ok 초록 / x 빨강."""
    col = {'n': (120, 160, 255), 'ok': (80, 230, 140), 'x': (255, 90, 110)}[state]

    def f(d, im, s):
        W, H = im.size
        L = 16 * s
        w = int(2.6 * s)
        for (x, y, dx, dy) in ((0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)):
            x = x + dx * 2 * s
            y = y + dy * 2 * s
            d.line([(x, y), (x + dx * L, y)], fill=_c(col), width=w)
            d.line([(x, y), (x, y + dy * L)], fill=_c(col), width=w)
        if state != 'n':
            d.rounded_rectangle((3 * s, 3 * s, W - 3 * s, H - 3 * s), 4 * s, outline=_c(col, 120), width=int(1.2 * s))
    return art('s23_scan_%s' % state, 86, 86, f)


def s23_box(kind):
    """kind: ship 출고 상자 / bin 불량 통."""
    def f(d, im, s):
        W, H = im.size
        if kind == 'ship':
            d.polygon([(2 * s, 10 * s), (W - 2 * s, 10 * s), (W - 5 * s, H - 1 * s), (5 * s, H - 1 * s)], fill=(176, 130, 80, 255),
                      outline=(70, 46, 20, 255))
            d.polygon([(2 * s, 10 * s), (10 * s, 2 * s), (W - 10 * s, 2 * s), (W - 2 * s, 10 * s)], fill=(140, 100, 60, 255),
                      outline=(70, 46, 20, 255))
            d.text((W / 2, H * 0.62), '출고', font=font('jalnan', int(10 * s)), fill=(255, 255, 255, 255), anchor='mm',
                   stroke_width=int(1 * s), stroke_fill=(70, 46, 20, 255))
        else:
            d.polygon([(2 * s, 8 * s), (W - 2 * s, 8 * s), (W - 6 * s, H - 1 * s), (6 * s, H - 1 * s)], fill=(150, 30, 50, 255),
                      outline=(40, 0, 10, 255))
            d.rectangle((1 * s, 4 * s, W - 1 * s, 10 * s), fill=(110, 20, 36, 255), outline=(40, 0, 10, 255))
            d.text((W / 2, H * 0.62), '불량', font=font('jalnan', int(10 * s)), fill=(255, 255, 255, 255), anchor='mm',
                   stroke_width=int(1 * s), stroke_fill=(40, 0, 10, 255))
    return art('s23_box_%s' % kind, 54, 40, f)


# ================================================================== 24. 실험 색 배합
S24_COL = [(236, 60, 72), (60, 200, 100), (70, 120, 255)]


def s24_frame():
    """가운데 74x74 둥근 창만 뚫린 금속 틀 (뒤의 색 글상자 모서리를 가린다)."""
    def f(d, im, s):
        W, H = im.size
        m = Image.new('L', im.size, 0)
        md = ImageDraw.Draw(m)
        md.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 12 * s, fill=255)
        md.rounded_rectangle(((W - 74 * s) / 2, (H - 74 * s) / 2, (W + 74 * s) / 2, (H + 74 * s) / 2), 9 * s, fill=0)
        g = Image.new('RGBA', im.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        for y in range(H):
            k = y / H
            gd.line([(0, y), (W, y)], fill=(int(150 - 90 * k), int(166 - 96 * k), int(210 - 110 * k), 255))
        g.putalpha(m)
        im.alpha_composite(g)
        d2 = ImageDraw.Draw(im)
        d2.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 12 * s, outline=(14, 18, 40, 255), width=int(1.2 * s))
        d2.rounded_rectangle(((W - 74 * s) / 2, (H - 74 * s) / 2, (W + 74 * s) / 2, (H + 74 * s) / 2), 9 * s,
                             outline=(10, 12, 26, 255), width=int(1.4 * s))
        for (x, y) in ((6, 6), (W / s - 6, 6), (6, H / s - 6), (W / s - 6, H / s - 6)):
            d2.ellipse(((x - 2) * s, (y - 2) * s, (x + 2) * s, (y + 2) * s), fill=(220, 226, 245, 255), outline=(20, 24, 50, 255))
        # 유리 반사
        d2.polygon([((W - 70 * s) / 2, (H - 70 * s) / 2), ((W - 30 * s) / 2, (H - 70 * s) / 2), ((W - 70 * s) / 2, (H - 30 * s) / 2)],
                   fill=(255, 255, 255, 40))
    return art('s24_frame', 94, 94, f)


def s24_tube(ch, lv):
    col = S24_COL[ch]

    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((3 * s, 1 * s, W - 3 * s, H - 1 * s), 9 * s, fill=(14, 18, 36, 230), outline=(180, 196, 240, 255),
                            width=int(1.2 * s))
        for k in range(4):
            y1 = H - (4 + k * 13) * s
            y0 = y1 - 11 * s
            if k < lv:
                d.rounded_rectangle((6 * s, y0, W - 6 * s, y1), 3 * s, fill=_c(col), outline=_c(_shade(col, 0.5)))
                d.rectangle((8 * s, y0 + 2 * s, 11 * s, y1 - 2 * s), fill=(255, 255, 255, 90))
            else:
                d.rounded_rectangle((6 * s, y0, W - 6 * s, y1), 3 * s, outline=_c(col, 70), width=max(1, int(0.6 * s)))
    return art('s24_tube_%d_%d' % (ch, lv), 24, 58, f)


def s24_arrow(ch, up):
    col = S24_COL[ch]

    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 2 * s), 7 * s, fill=_c(_shade(col, 0.55)), outline=(10, 12, 26, 255),
                            width=int(1 * s))
        d.rounded_rectangle((2 * s, 2 * s, W - 2 * s, H * 0.5), 6 * s, fill=(255, 255, 255, 40))
        cx, cy = W / 2, H / 2 - 0.5 * s
        if up:
            pts = [(cx, cy - 5 * s), (cx + 7 * s, cy + 4 * s), (cx - 7 * s, cy + 4 * s)]
        else:
            pts = [(cx, cy + 5 * s), (cx + 7 * s, cy - 4 * s), (cx - 7 * s, cy - 4 * s)]
        d.polygon(pts, fill=(255, 255, 255, 255))
    return art('s24_arrow_%d_%d' % (ch, up), 34, 20, f)


# ================================================================== 25. 널뛰기
def s25_plank():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((0.5 * s, 2 * s, W - 0.5 * s, H - 1 * s), 3 * s, fill=(176, 120, 66, 255), outline=(70, 40, 16, 255),
                            width=int(1 * s))
        d.rectangle((3 * s, 3.5 * s, W - 3 * s, 5 * s), fill=(214, 164, 104, 255))
        for k in range(9):
            x = (12 + k * 24) * s
            d.arc((x - 8 * s, 4 * s, x + 8 * s, H + 4 * s), 200, 340, fill=(120, 78, 40, 180), width=max(1, int(0.6 * s)))
        d.rectangle((W / 2 - 9 * s, 2 * s, W / 2 + 9 * s, H - 1 * s), fill=(200, 40, 60, 255), outline=(80, 10, 20, 255))
    return art('s25_plank', 224, 11, f)


def s25_straw():
    def f(d, im, s):
        W, H = im.size
        d.ellipse((1 * s, 2 * s, W - 1 * s, H - 1 * s), fill=(214, 180, 100, 255), outline=(110, 80, 30, 255), width=int(1 * s))
        for k in range(10):
            x = (5 + k * 3.4) * s
            d.line([(x, 4 * s), (x + 1 * s, H - 3 * s)], fill=(160, 120, 50, 200), width=max(1, int(0.6 * s)))
        for y in (0.4, 0.7):
            d.line([(4 * s, H * y), (W - 4 * s, H * y)], fill=(120, 40, 40, 255), width=int(1.4 * s))
    return art('s25_straw', 40, 26, f)


def s25_body(col, pose):
    """한복 몸 (머리 없음). 30x48, 발 = 아래, 목 = 위 가운데."""
    top = (246, 242, 232)
    sk = col
    skin = (240, 206, 174, 255)

    def f(d, im, s):
        P = lambda x, y: (x * s, y * s)
        if pose == 'jump':
            d.line([P(9, 8), P(2, 1)], fill=_c(top), width=int(3.4 * s))
            d.line([P(21, 8), P(28, 1)], fill=_c(top), width=int(3.4 * s))
            d.ellipse((*P(0, -1), *P(4, 3)), fill=skin)
            d.ellipse((*P(26, -1), *P(30, 3)), fill=skin)
            d.polygon([P(9, 18), P(21, 18), P(30, 42), P(0, 42)], fill=_c(sk), outline=_c(_shade(sk, 0.45)))
            d.line([P(11, 42), P(9, 47)], fill=(250, 250, 255, 255), width=int(3 * s))
            d.line([P(19, 42), P(21, 47)], fill=(250, 250, 255, 255), width=int(3 * s))
        else:
            d.polygon([P(9, 18), P(21, 18), P(26, 45), P(4, 45)], fill=_c(sk), outline=_c(_shade(sk, 0.45)))
            d.line([P(9, 9), P(6, 22)], fill=_c(top), width=int(3.4 * s))
            d.line([P(21, 9), P(24, 22)], fill=_c(top), width=int(3.4 * s))
            d.ellipse((*P(4, 21), *P(8, 25)), fill=skin)
            d.ellipse((*P(22, 21), *P(26, 25)), fill=skin)
            d.ellipse((*P(8, 44), *P(14, 48)), fill=(250, 250, 255, 255))
            d.ellipse((*P(16, 44), *P(22, 48)), fill=(250, 250, 255, 255))
        # 저고리 + 고름
        d.rounded_rectangle((*P(8, 4), *P(22, 19)), 3 * s, fill=_c(top), outline=(90, 80, 70, 255), width=max(1, int(0.5 * s)))
        d.polygon([P(12, 4), P(15, 9), P(18, 4)], fill=_c(_shade(sk, 0.8)))
        d.line([P(15, 10), P(13, 17)], fill=_c(sk), width=int(1.4 * s))
        d.line([P(15, 10), P(17, 16)], fill=_c(sk), width=int(1.4 * s))
        d.rectangle((*P(13, 1), *P(17, 5)), fill=skin)
    return art('s25_body_%d_%d_%d_%s' % (col + (pose,)), 30, 48, f)


def s25_ruler():
    def f(d, im, s):
        W, H = im.size
        d.rounded_rectangle((4 * s, 0, W - 4 * s, H), 4 * s, fill=(10, 14, 32, 200), outline=(110, 140, 240, 200), width=int(1 * s))
        for k in range(0, 9):
            y = H - 4 * s - k * (H - 8 * s) / 8
            long_ = k % 2 == 0
            d.line([(4 * s, y), ((14 if long_ else 10) * s, y)], fill=(200, 214, 255, 255), width=max(1, int(0.8 * s)))
    return art('s25_ruler', 22, 132, f)


def s25_marker(col):
    def f(d, im, s):
        W, H = im.size
        d.polygon([(W, 0), (W, H), (0, H / 2)], fill=_c(col), outline=(10, 10, 20, 255))
    return art('s25_marker_%d_%d_%d' % col, 9, 9, f)
