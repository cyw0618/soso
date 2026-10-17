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
