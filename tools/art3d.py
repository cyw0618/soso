# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 31~40번 그림 (mg_art3.art 로 2배 해상도 저장, 이름 앞에 k3x_)."""
import math
from PIL import Image, ImageDraw, ImageFilter
from art_common import font
import mg_art3 as A3

art = A3.art


def _rgba(c, a=255):
    return tuple(c[:3]) + (a,)


# ================================================================== 31. 연싸움
def shield_kite():
    """내 방패연 (흰 종이, 가운데 방구멍, 파란 꼭지, 꼬리 둘)."""
    def f(d, im, s):
        W, H = im.width, im.height
        x0, y0, x1, y1 = W * 0.14, H * 0.04, W * 0.86, H * 0.74
        d.rectangle((x0, y0, x1, y1), fill=(246, 246, 238, 255), outline=(40, 70, 170, 255), width=int(1.6 * s))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        r = (x1 - x0) * 0.42
        d.pieslice((cx - r, y0 - r * 0.5, cx + r, y0 + r * 1.1), 0, 180, fill=(52, 92, 230, 255))
        d.line((x0, y0, x1, y1), fill=(150, 120, 80, 255), width=int(0.9 * s))
        d.line((x1, y0, x0, y1), fill=(150, 120, 80, 255), width=int(0.9 * s))
        d.line((cx, y0, cx, y1), fill=(150, 120, 80, 255), width=int(0.9 * s))
        rh = (x1 - x0) * 0.17
        d.ellipse((cx - rh, cy - rh, cx + rh, cy + rh), fill=(0, 0, 0, 0), outline=(40, 70, 170, 255), width=int(1.2 * s))
        d.ellipse((cx - rh + s, cy - rh + s, cx + rh - s, cy + rh - s), fill=(0, 0, 0, 0))
        for sx in (x0 + 2 * s, x1 - 2 * s):
            pts = [(sx + math.sin(k * 0.9) * 2.5 * s, y1 + k * (H - y1) / 8) for k in range(9)]
            d.line(pts, fill=(70, 120, 255, 255), width=int(1.6 * s), joint='curve')
    p = art('k31_shield', 30, 44, f)
    # 방구멍은 투명하게 (뒤 하늘이 보이게)
    return p


def ray_kite(col, name):
    """상대 가오리연 (마름모 + 긴 꼬리)."""
    def f(d, im, s):
        W, H = im.width, im.height
        top, left, right, bot = (W / 2, H * 0.02), (W * 0.06, H * 0.3), (W * 0.94, H * 0.3), (W / 2, H * 0.62)
        d.polygon([top, right, bot, left], fill=_rgba(col), outline=(255, 255, 255, 230))
        d.line([top, right, bot, left, top], fill=(255, 255, 255, 230), width=int(1.2 * s))
        d.polygon([top, (W / 2, H * 0.3), left], fill=(255, 255, 255, 60))
        d.line([top, bot], fill=(90, 50, 30, 255), width=int(0.9 * s))
        d.line([left, right], fill=(90, 50, 30, 255), width=int(0.9 * s))
        d.ellipse((W / 2 - 3 * s, H * 0.3 - 3 * s, W / 2 + 3 * s, H * 0.3 + 3 * s), fill=(20, 20, 30, 255))
        pts = [(W / 2 + math.sin(k * 0.8) * 3 * s, H * 0.62 + k * (H * 0.38) / 10) for k in range(11)]
        d.line(pts, fill=_rgba(col), width=int(1.8 * s), joint='curve')
        for k in (3, 6, 9):
            x, y = pts[k]
            d.polygon([(x - 3 * s, y - 2 * s), (x + 3 * s, y - 2 * s), (x, y + 3 * s)], fill=(255, 255, 255, 220))
    return art('k31_ray_%s' % name, 30, 50, f)


def reel():
    """얼레 (실 감는 나무틀)."""
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((W * 0.1, H * 0.25, W * 0.9, H * 0.75), 2 * s, fill=(196, 160, 110, 255), outline=(90, 60, 30, 255),
                            width=int(1 * s))
        for k in range(5):
            y = H * 0.32 + k * H * 0.09
            d.line((W * 0.2, y, W * 0.8, y), fill=(250, 250, 250, 255), width=int(0.8 * s))
        d.rectangle((W * 0.02, H * 0.05, W * 0.14, H * 0.95), fill=(120, 80, 40, 255))
        d.rectangle((W * 0.86, H * 0.05, W * 0.98, H * 0.95), fill=(120, 80, 40, 255))
    return art('k31_reel', 22, 16, f)


def spark(name, col=(255, 236, 140)):
    def f(d, im, s):
        W = im.width
        c = W / 2
        for k in range(8):
            a = k * math.pi / 4
            r1, r2 = W * 0.12, W * (0.48 if k % 2 == 0 else 0.34)
            d.line((c + math.cos(a) * r1, c + math.sin(a) * r1, c + math.cos(a) * r2, c + math.sin(a) * r2),
                   fill=_rgba(col), width=int(2 * s))
        d.ellipse((c - W * 0.1, c - W * 0.1, c + W * 0.1, c + W * 0.1), fill=(255, 255, 255, 255))
    return art('k3_spark_%s' % name, 30, 30, f)


def dot():
    """거의 투명한 작은 점 (붓 담당 오브젝트용)."""
    def f(d, im, s):
        d.rectangle((0, 0, im.width, im.height), fill=(255, 255, 255, 2))
    return art('k3_dot', 2, 2, f)
