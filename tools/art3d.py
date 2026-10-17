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


def _f(name, size, s):
    return font(name, int(size * s))


# ================================================================== 32. 근대 학교 방탈출
def room_wall():
    """교실 벽 (회반죽 + 아래 나무 징두리 + 위 몰딩) 480x160."""
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(214, 196, 160, 255))
        for k in range(0, int(W), int(40 * s)):
            d.line((k, 0, k, H * 0.8), fill=(206, 186, 150, 255), width=int(0.6 * s))
        d.rectangle((0, 0, W, 8 * s), fill=(120, 80, 48, 255))
        d.rectangle((0, H - 34 * s, W, H), fill=(128, 84, 50, 255))
        d.rectangle((0, H - 36 * s, W, H - 32 * s), fill=(92, 58, 34, 255))
        for k in range(0, int(W), int(24 * s)):
            d.line((k, H - 32 * s, k, H), fill=(100, 64, 38, 255), width=int(1 * s))
    return art('k32_wall', 480, 160, f)


def room_floor():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(92, 62, 40, 255))
        for k in range(0, int(H), int(12 * s)):
            d.line((0, k, W, k), fill=(70, 46, 30, 255), width=int(1 * s))
            off = (k // int(12 * s)) % 3 * 50 * s
            for x in range(int(off), int(W), int(150 * s)):
                d.line((x, k, x, k + 12 * s), fill=(70, 46, 30, 255), width=int(1 * s))
    return art('k32_floor', 480, 110, f)


def blackboard():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(110, 72, 40, 255))
        d.rectangle((5 * s, 5 * s, W - 5 * s, H - 9 * s), fill=(34, 70, 52, 255))
        d.rectangle((0, H - 6 * s, W, H), fill=(140, 96, 56, 255))
        for x, w in ((W * 0.7, 10), (W * 0.76, 6)):
            d.rectangle((x, H - 9 * s, x + w * s, H - 6 * s), fill=(240, 240, 230, 255))
        for k in range(6):
            x = W * (0.1 + k * 0.15)
            d.line((x, H * 0.2, x + 14 * s, H * 0.24), fill=(70, 110, 90, 255), width=int(1 * s))
    return art('k32_board', 160, 74, f)


def timetable_small():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(120, 80, 44, 255))
        d.rectangle((3 * s, 3 * s, W - 3 * s, H - 3 * s), fill=(236, 226, 196, 255))
        d.text((W / 2, 10 * s), '時間表', font=_f('nanum', 8, s), fill=(60, 40, 30, 255), anchor='mm')
        for r in range(5):
            y = 17 * s + r * (H - 22 * s) / 4
            d.line((5 * s, y, W - 5 * s, y), fill=(120, 100, 80, 255), width=int(0.7 * s))
        for c in range(7):
            x = 5 * s + c * (W - 10 * s) / 6
            d.line((x, 17 * s, x, H - 5 * s), fill=(120, 100, 80, 255), width=int(0.7 * s))
    return art('k32_tt', 48, 62, f)


def world_map():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(120, 80, 44, 255))
        d.rectangle((3 * s, 3 * s, W - 3 * s, H - 3 * s), fill=(196, 214, 210, 255))
        blobs = [(0.12, 0.25, 0.32, 0.55), (0.22, 0.55, 0.32, 0.85), (0.42, 0.2, 0.58, 0.5), (0.45, 0.5, 0.58, 0.8),
                 (0.55, 0.15, 0.85, 0.55), (0.78, 0.65, 0.9, 0.82)]
        for x0, y0, x1, y1 in blobs:
            d.ellipse((W * x0, H * y0, W * x1, H * y1), fill=(196, 170, 120, 255))
        for k in range(1, 4):
            d.line((W * k / 4, 3 * s, W * k / 4, H - 3 * s), fill=(150, 170, 170, 255), width=int(0.5 * s))
            d.line((3 * s, H * k / 4, W - 3 * s, H * k / 4), fill=(150, 170, 170, 255), width=int(0.5 * s))
    return art('k32_map', 78, 48, f)


def globe_cab():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((W * 0.05, H * 0.55, W * 0.95, H), fill=(110, 70, 40, 255), outline=(70, 44, 26, 255), width=int(1 * s))
        d.rectangle((W * 0.12, H * 0.65, W * 0.88, H * 0.95), outline=(80, 50, 30, 255), width=int(1 * s))
        cx, cy, r = W * 0.5, H * 0.28, H * 0.22
        d.line((cx, cy + r, cx, H * 0.55), fill=(150, 120, 60, 255), width=int(2 * s))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(70, 130, 190, 255), outline=(200, 170, 80, 255), width=int(1.2 * s))
        d.ellipse((cx - r * 0.6, cy - r * 0.5, cx + r * 0.1, cy + r * 0.3), fill=(110, 170, 90, 255))
        d.ellipse((cx + r * 0.2, cy - r * 0.1, cx + r * 0.7, cy + r * 0.6), fill=(110, 170, 90, 255))
    return art('k32_globe', 60, 70, f)


def desk():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, 8 * s), fill=(150, 100, 60, 255))
        d.rectangle((6 * s, 8 * s, W - 6 * s, H), fill=(118, 76, 44, 255), outline=(80, 50, 28, 255), width=int(1 * s))
        d.rectangle((16 * s, 14 * s, W - 16 * s, H - 6 * s), outline=(90, 58, 34, 255), width=int(1 * s))
    return art('k32_desk', 150, 46, f)


def abacus_small():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(90, 56, 30, 255))
        d.rectangle((2 * s, 2 * s, W - 2 * s, H - 2 * s), fill=(60, 36, 20, 255))
        d.line((2 * s, H * 0.35, W - 2 * s, H * 0.35), fill=(120, 80, 40, 255), width=int(1.2 * s))
        for k in range(5):
            x = W * (0.15 + k * 0.175)
            d.ellipse((x - 3 * s, 3 * s, x + 3 * s, 6 * s), fill=(200, 150, 90, 255))
            for j in range(3):
                d.ellipse((x - 3 * s, H * 0.48 + j * 3.2 * s, x + 3 * s, H * 0.48 + j * 3.2 * s + 3 * s), fill=(200, 150, 90, 255))
    return art('k32_abs', 44, 20, f)


def abacus_rod(dg):
    """주판 한 줄 (숫자 dg 를 놓은 모양): 위 5알 하나, 아래 1알 넷."""
    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        beam = H * 0.3
        d.line((cx, 0, cx, H), fill=(150, 110, 60, 255), width=int(2 * s))
        d.rectangle((0, beam - 2 * s, W, beam + 2 * s), fill=(110, 70, 36, 255))
        bw, bh = W * 0.42, 6.5 * s
        def bead(y, lit=True):
            col = (226, 170, 96, 255) if lit else (176, 126, 70, 255)
            d.ellipse((cx - bw, y - bh, cx + bw, y + bh), fill=col, outline=(90, 54, 24, 255), width=int(1 * s))
            d.ellipse((cx - bw * 0.6, y - bh * 0.7, cx, y - bh * 0.1), fill=(255, 230, 180, 120))
        bead(beam - 2 * s - bh if dg >= 5 else bh + 1 * s, dg >= 5)
        ones = dg % 5
        for k in range(4):
            if k < ones:
                y = beam + 2 * s + bh + k * 2 * bh
            else:
                y = H - bh - 1 * s - (3 - k) * 2 * bh
            bead(y, k < ones)
    return art('k32_rod_%d' % dg, 40, 96, f)


def lamp(lit):
    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        if lit:
            for k in range(14, 0, -1):
                r = W * 0.5 * k / 14
                d.ellipse((cx - r, H * 0.3 - r, cx + r, H * 0.3 + r), fill=(255, 210, 120, 10 + (14 - k) * 6))
            d.ellipse((cx - 3.5 * s, H * 0.18, cx + 3.5 * s, H * 0.38), fill=(255, 240, 180, 255))
            d.ellipse((cx - 1.8 * s, H * 0.26, cx + 1.8 * s, H * 0.36), fill=(255, 255, 255, 255))
        d.rectangle((cx - 1 * s, H * 0.38, cx + 1 * s, H * 0.46), fill=(80, 70, 60, 255))
        d.ellipse((cx - 9 * s, H * 0.44, cx + 9 * s, H * 0.6), fill=(210, 220, 230, 255), outline=(120, 120, 130, 255), width=int(1 * s))
        d.rectangle((cx - 2 * s, H * 0.58, cx + 2 * s, H * 0.85), fill=(120, 80, 40, 255))
        d.ellipse((cx - 8 * s, H * 0.82, cx + 8 * s, H * 0.92), fill=(140, 96, 50, 255))
    return art('k32_lamp_%d' % lit, 50, 60, f)


def hanging(k):
    def f(d, im, s):
        W, H = im.width, im.height
        d.line((W / 2, 0, W / 2, H * 0.4), fill=(230, 230, 220, 255), width=int(0.8 * s))
        pts = [(W * 0.35, H * 0.4), (W * 0.62, H * 0.42), (W * 0.58, H * 0.98), (W * 0.4, H * 0.95)] if k == 1 else \
              [(W * 0.3, H * 0.4), (W * 0.7, H * 0.45), (W * 0.62, H * 0.9), (W * 0.36, H * 0.98)]
        d.polygon(pts, fill=(150, 104, 60, 255), outline=(90, 60, 30, 255))
    return art('k32_hang%d' % k, 14, 30, f)


def shadow_glyph(txt, key):
    def f(d, im, s):
        W, H = im.width, im.height
        fo = _f('black', 30, s)
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((W / 2, H / 2), txt, font=fo, fill=(30, 18, 10, 170), anchor='mm')
        sh = sh.filter(ImageFilter.GaussianBlur(1.2 * s))
        im.alpha_composite(sh)
    return art('k32_sh_%s' % key, 44, 44, f)


def type_block(txt, key, mirror=True):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 2 * s, fill=(168, 130, 84, 255), outline=(90, 62, 34, 255),
                            width=int(1 * s))
        d.rectangle((4 * s, 4 * s, W - 4 * s, H - 4 * s), fill=(70, 70, 78, 255))
        g = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).text((W / 2, H / 2), txt, font=_f('black', 16, s), fill=(226, 230, 240, 255), anchor='mm')
        if mirror:
            g = g.transpose(Image.FLIP_LEFT_RIGHT)
        im.alpha_composite(g)
    return art('k32_type_%s%s' % (key, '' if mirror else 'n'), 28, 28, f)


def slot_empty():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 2 * s, fill=(30, 30, 40, 200), outline=(150, 160, 200, 255),
                            width=int(1 * s))
    return art('k32_slot', 28, 28, f)


def door(op):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(80, 50, 28, 255))
        if op:
            d.rectangle((5 * s, 5 * s, W - 5 * s, H), fill=(255, 246, 210, 255))
            d.polygon([(5 * s, 5 * s), (16 * s, 12 * s), (16 * s, H - 4 * s), (5 * s, H)], fill=(130, 86, 50, 255))
        else:
            d.rectangle((5 * s, 5 * s, W - 5 * s, H), fill=(136, 90, 52, 255))
            for y0, y1 in ((12, 48), (56, 112)):
                d.rectangle((11 * s, y0 * s, W - 11 * s, y1 * s), outline=(96, 62, 34, 255), width=int(1.2 * s))
            d.rectangle((14 * s, 16 * s, W - 14 * s, 44 * s), fill=(190, 210, 220, 255))
            d.line((W / 2, 16 * s, W / 2, 44 * s), fill=(96, 62, 34, 255), width=int(1 * s))
            d.rectangle((W - 20 * s, 62 * s, W - 9 * s, 80 * s), fill=(60, 60, 70, 255), outline=(200, 190, 140, 255), width=int(1 * s))
            for k in range(2):
                d.rectangle((W - 18 * s + k * 5 * s, 66 * s, W - 15 * s + k * 5 * s, 76 * s), fill=(200, 190, 140, 255))
    return art('k32_door_%d' % op, 64, 124, f)


def wood_box(op):
    def f(d, im, s):
        W, H = im.width, im.height
        if op:
            d.polygon([(2 * s, H * 0.4), (W - 2 * s, H * 0.4), (W - 6 * s, 0), (6 * s, 0)], fill=(150, 104, 60, 255))
            d.rectangle((2 * s, H * 0.4, W - 2 * s, H - 1 * s), fill=(110, 70, 40, 255), outline=(70, 44, 24, 255), width=int(1 * s))
            d.rectangle((6 * s, H * 0.4, W - 6 * s, H * 0.55), fill=(40, 26, 16, 255))
        else:
            d.rectangle((2 * s, H * 0.3, W - 2 * s, H - 1 * s), fill=(120, 78, 44, 255), outline=(70, 44, 24, 255), width=int(1 * s))
            d.rectangle((2 * s, H * 0.3, W - 2 * s, H * 0.45), fill=(150, 104, 60, 255))
            d.rectangle((W / 2 - 3 * s, H * 0.45, W / 2 + 3 * s, H * 0.7), fill=(200, 180, 110, 255))
    return art('k32_box_%d' % op, 36, 24, f)


def match_item(sel):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 5 * s, fill=(40, 52, 110, 255) if sel else (20, 26, 52, 230),
                            outline=(140, 170, 255, 255) if sel else (90, 104, 160, 255), width=int((2 if sel else 1) * s))
        d.rectangle((W * 0.22, H * 0.35, W * 0.78, H * 0.75), fill=(200, 60, 50, 255), outline=(255, 230, 200, 255), width=int(1 * s))
        for k in range(3):
            x = W * (0.32 + k * 0.14)
            d.line((x, H * 0.36, x + 2 * s, H * 0.18), fill=(230, 210, 170, 255), width=int(1.4 * s))
            d.ellipse((x + 0.5 * s, H * 0.12, x + 3.5 * s, H * 0.2), fill=(140, 30, 30, 255))
    return art('k32_match_%d' % sel, 30, 30, f)


# ================================================================== 33. 강 건너기
def bank(side):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(62, 120, 70, 255))
        for k in range(40):
            x = (k * 37 % 113) / 113 * W
            y = (k * 53 % 97) / 97 * H
            d.line((x, y, x + 2 * s, y - 4 * s), fill=(90, 160, 90, 255), width=int(1 * s))
        ex = W if side == 0 else 0
        d.rectangle((ex - 8 * s, 0, ex + 8 * s, H), fill=(170, 150, 110, 255))
    return art('k33_bank%d' % side, 130, 150, f)


def river():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(36, 84, 150, 255))
        for k in range(14):
            x = (k * 61 % 199) / 199 * W
            y = (k * 41 % 151) / 151 * H
            d.arc((x, y, x + 18 * s, y + 6 * s), 200, 340, fill=(120, 170, 230, 255), width=int(1.2 * s))
    return art('k33_river', 220, 150, f)


def boat():
    def f(d, im, s):
        W, H = im.width, im.height
        d.polygon([(0, H * 0.3), (W, H * 0.3), (W * 0.86, H), (W * 0.14, H)], fill=(150, 96, 50, 255), outline=(80, 50, 24, 255))
        d.rectangle((0, H * 0.3, W, H * 0.45), fill=(180, 120, 66, 255))
        d.line((W * 0.85, H * 0.3, W * 1.0, 0), fill=(120, 80, 40, 255), width=int(2 * s))
    return art('k33_boat', 84, 22, f)


def person(body, head=(240, 200, 160), hat=None, sign=None, tag=''):
    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        d.ellipse((cx - 9 * s, H - 6 * s, cx + 9 * s, H), fill=(0, 0, 0, 70))
        d.rounded_rectangle((cx - 9 * s, H * 0.42, cx + 9 * s, H - 3 * s), 4 * s, fill=_rgba(body), outline=(20, 20, 30, 255),
                            width=int(1 * s))
        d.ellipse((cx - 8 * s, H * 0.12, cx + 8 * s, H * 0.48), fill=_rgba(head), outline=(60, 40, 30, 255), width=int(1 * s))
        d.ellipse((cx - 4 * s, H * 0.26, cx - 2 * s, H * 0.3), fill=(30, 20, 20, 255))
        d.ellipse((cx + 2 * s, H * 0.26, cx + 4 * s, H * 0.3), fill=(30, 20, 20, 255))
        if hat:
            d.ellipse((cx - 13 * s, H * 0.14, cx + 13 * s, H * 0.22), fill=_rgba(hat))
            d.polygon([(cx - 7 * s, H * 0.17), (cx + 7 * s, H * 0.17), (cx, 0)], fill=_rgba(hat))
        if sign:
            d.line((cx + 10 * s, H * 0.55, cx + 10 * s, H * 0.18), fill=(120, 90, 50, 255), width=int(1.4 * s))
            d.rectangle((cx + 3 * s, 0, cx + 17 * s, H * 0.22), fill=_rgba(sign[0]), outline=(255, 255, 255, 255), width=int(1 * s))
            d.text((cx + 10 * s, H * 0.11), sign[1], font=_f('jalnan', 7, s), fill=(255, 255, 255, 255), anchor='mm')
    return art('k33_p_%s' % tag, 36, 44, f)


def tiger():
    def f(d, im, s):
        W, H = im.width, im.height
        d.ellipse((4 * s, H * 0.45, W - 4 * s, H - 3 * s), fill=(240, 150, 40, 255), outline=(60, 30, 10, 255), width=int(1 * s))
        for k in range(4):
            x = W * (0.25 + k * 0.15)
            d.line((x, H * 0.48, x + 2 * s, H * 0.7), fill=(40, 20, 10, 255), width=int(1.6 * s))
        cx = W * 0.5
        d.ellipse((cx - 11 * s, H * 0.1, cx + 11 * s, H * 0.55), fill=(245, 160, 50, 255), outline=(60, 30, 10, 255), width=int(1 * s))
        for ex in (-8, 8):
            d.ellipse((cx + ex * s - 3.5 * s, H * 0.06, cx + ex * s + 3.5 * s, H * 0.2), fill=(245, 160, 50, 255), outline=(60, 30, 10, 255))
        d.ellipse((cx - 6 * s, H * 0.3, cx + 6 * s, H * 0.5), fill=(255, 240, 220, 255))
        for ex in (-5, 5):
            d.ellipse((cx + ex * s - 2 * s, H * 0.24, cx + ex * s + 2 * s, H * 0.32), fill=(30, 30, 20, 255))
        d.line((cx - 3 * s, H * 0.15, cx + 3 * s, H * 0.15), fill=(40, 20, 10, 255), width=int(1.2 * s))
    return art('k33_tiger', 36, 44, f)


def goat():
    def f(d, im, s):
        W, H = im.width, im.height
        d.ellipse((5 * s, H * 0.5, W - 5 * s, H - 6 * s), fill=(240, 240, 235, 255), outline=(80, 80, 80, 255), width=int(1 * s))
        for x in (0.3, 0.65):
            d.line((W * x, H * 0.85, W * x, H - 1 * s), fill=(80, 80, 80, 255), width=int(2 * s))
        cx = W * 0.62
        d.ellipse((cx - 8 * s, H * 0.18, cx + 8 * s, H * 0.55), fill=(245, 245, 240, 255), outline=(80, 80, 80, 255), width=int(1 * s))
        d.line((cx - 4 * s, H * 0.2, cx - 8 * s, H * 0.04), fill=(150, 130, 100, 255), width=int(2 * s))
        d.line((cx + 4 * s, H * 0.2, cx + 8 * s, H * 0.04), fill=(150, 130, 100, 255), width=int(2 * s))
        d.ellipse((cx - 4 * s, H * 0.3, cx - 1 * s, H * 0.36), fill=(30, 30, 30, 255))
        d.ellipse((cx + 1 * s, H * 0.3, cx + 4 * s, H * 0.36), fill=(30, 30, 30, 255))
        d.polygon([(cx - 2 * s, H * 0.55), (cx + 2 * s, H * 0.55), (cx, H * 0.66)], fill=(200, 200, 190, 255))
    return art('k33_goat', 36, 44, f)


def cabbage():
    def f(d, im, s):
        W, H = im.width, im.height
        cx, cy = W / 2, H * 0.62
        for k, (r, col) in enumerate(((15, (70, 150, 60)), (12, (110, 190, 80)), (8, (170, 220, 120)))):
            d.ellipse((cx - r * s, cy - r * s * 0.95, cx + r * s, cy + r * s * 0.95), fill=_rgba(col), outline=(40, 90, 30, 255),
                      width=int(1 * s))
        d.line((cx, cy - 8 * s, cx, cy + 8 * s), fill=(220, 240, 190, 255), width=int(1 * s))
    return art('k33_cabbage', 36, 44, f)


# ================================================================== 34. 얼음 컬링
def curling_sheet(L, Hh, hx, hr):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 0, W, H), 8 * s, fill=(226, 238, 248, 255), outline=(120, 150, 200, 255), width=int(2 * s))
        for k in range(30):
            x = (k * 71 % 461) / 461 * W
            y = (k * 37 % 113) / 113 * H
            d.line((x, y, x + 20 * s, y + 3 * s), fill=(210, 226, 240, 255), width=int(1 * s))
        cx, cy = W / 2 + hx * s, H / 2
        for r, col in ((hr, (60, 100, 220)), (hr * 0.72, (245, 245, 255)), (hr * 0.45, (220, 60, 70)), (hr * 0.16, (245, 245, 255))):
            d.ellipse((cx - r * s, cy - r * s, cx + r * s, cy + r * s), fill=_rgba(col))
        d.line((cx, 4 * s, cx, H - 4 * s), fill=(150, 160, 190, 255), width=int(1 * s))
        d.line((4 * s, cy, W - 4 * s, cy), fill=(150, 160, 190, 255), width=int(1 * s))
        hog = W / 2 + (hx - 120) * s
        d.line((hog, 4 * s, hog, H - 4 * s), fill=(220, 60, 70, 255), width=int(2 * s))
        d.line((cx + (hr + 16) * s, 4 * s, cx + (hr + 16) * s, H - 4 * s), fill=(60, 100, 220, 255), width=int(1.4 * s))
    return art('k34_sheet', L, Hh, f)


def stone(col, name):
    def f(d, im, s):
        W, H = im.width, im.height
        d.ellipse((1 * s, 1 * s, W - 1 * s, H - 1 * s), fill=(110, 116, 130, 255), outline=(40, 44, 54, 255), width=int(1 * s))
        d.ellipse((W * 0.22, H * 0.22, W * 0.78, H * 0.78), fill=_rgba(col))
        d.rectangle((W * 0.42, H * 0.12, W * 0.58, H * 0.62), fill=(30, 30, 40, 255))
        d.ellipse((W * 0.28, H * 0.2, W * 0.5, H * 0.38), fill=(255, 255, 255, 90))
    return art('k34_stone_%s' % name, 18, 18, f)


def aim_arrow():
    def f(d, im, s):
        W, H = im.width, im.height
        for x in range(int(W * 0.5), int(W * 0.92), int(6 * s)):
            d.line((x, H / 2, x + 3 * s, H / 2), fill=(255, 220, 90, 255), width=int(2 * s))
        d.polygon([(W, H / 2), (W * 0.9, 0), (W * 0.9, H)], fill=(255, 220, 90, 255))
    return art('k34_arrow', 120, 10, f)


def broom():
    def f(d, im, s):
        W, H = im.width, im.height
        d.line((W * 0.8, 0, W * 0.4, H * 0.7), fill=(160, 110, 60, 255), width=int(2 * s))
        d.rounded_rectangle((0, H * 0.62, W * 0.7, H), 3 * s, fill=(220, 60, 70, 255), outline=(100, 20, 30, 255), width=int(1 * s))
    return art('k34_broom', 20, 26, f)


# ================================================================== 35. 활주로 관제
def airfield():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 0, W, H), 10 * s, fill=(40, 70, 52, 230))
        ry = H * 0.42
        d.rectangle((W * 0.12, ry - 13 * s, W * 0.86, ry + 13 * s), fill=(54, 56, 64, 255), outline=(200, 200, 210, 255), width=int(1 * s))
        for x in range(int(W * 0.16), int(W * 0.82), int(22 * s)):
            d.rectangle((x, ry - 1 * s, x + 11 * s, ry + 1 * s), fill=(240, 240, 240, 255))
        for k in range(4):
            y = ry - 9 * s + k * 6 * s
            d.rectangle((W * 0.12 + 3 * s, y, W * 0.12 + 12 * s, y + 3 * s), fill=(240, 240, 240, 255))
            d.rectangle((W * 0.86 - 12 * s, y, W * 0.86 - 3 * s, y + 3 * s), fill=(240, 240, 240, 255))
        ty = H * 0.78
        d.rectangle((W * 0.1, ty - 6 * s, W * 0.98, ty + 6 * s), fill=(70, 72, 80, 255))
        d.line((W * 0.1, ty, W * 0.98, ty), fill=(240, 200, 60, 255), width=int(1 * s))
        for x in (0.3, 0.92):
            d.rectangle((W * x - 6 * s, ry + 13 * s, W * x + 6 * s, ty - 6 * s), fill=(70, 72, 80, 255))
            d.line((W * x, ry + 13 * s, W * x, ty), fill=(240, 200, 60, 255), width=int(1 * s))
        d.rectangle((W * 0.0, H * 0.86, W * 0.24, H), fill=(90, 100, 130, 255))
        d.text((W * 0.12, H * 0.93), '터미널', font=_f('jalnan', 8, s), fill=(255, 255, 255, 255), anchor='mm')
    return art('k35_field', 470, 190, f)


def plane(kind, go):
    def f(d, im, s):
        W, H = im.width, im.height
        cx, cy = W / 2, H / 2
        ring = (70, 230, 120, 255) if go else (255, 70, 80, 255)
        d.ellipse((1.5 * s, 1.5 * s, W - 1.5 * s, H - 1.5 * s), outline=ring, width=int(2.4 * s))
        body = (240, 244, 255, 255) if kind == 'arr' else (255, 190, 90, 255)
        # 위쪽을 향한 비행기
        d.rounded_rectangle((cx - 3 * s, cy - 12 * s, cx + 3 * s, cy + 11 * s), 3 * s, fill=body, outline=(40, 50, 80, 255), width=int(1 * s))
        d.polygon([(cx - 13 * s, cy + 2 * s), (cx + 13 * s, cy + 2 * s), (cx + 3 * s, cy - 5 * s), (cx - 3 * s, cy - 5 * s)], fill=body,
                  outline=(40, 50, 80, 255))
        d.polygon([(cx - 6 * s, cy + 11 * s), (cx + 6 * s, cy + 11 * s), (cx + 2 * s, cy + 6 * s), (cx - 2 * s, cy + 6 * s)], fill=body,
                  outline=(40, 50, 80, 255))
        d.ellipse((cx - 1.5 * s, cy - 10 * s, cx + 1.5 * s, cy - 6 * s), fill=(60, 120, 220, 255))
    return art('k35_plane_%s_%d' % (kind, go), 32, 32, f)


# ================================================================== 36. 국회 연설
GROUPS36 = [('청년', (80, 140, 255)), ('어르신', (190, 150, 240)), ('농민', (90, 190, 90)), ('기업인', (240, 180, 60)),
            ('노동자', (240, 110, 80))]


def crowd(g, mood):
    """청중 무리 (mood 0 화남, 1 보통, 2 기쁨)."""
    col = GROUPS36[g][1]

    def f(d, im, s):
        W, H = im.width, im.height
        for k, (x, y, r) in enumerate(((0.22, 0.52, 0.17), (0.78, 0.52, 0.17), (0.5, 0.42, 0.22))):
            cx, cy, rr = W * x, H * y, W * r
            d.rounded_rectangle((cx - rr * 1.1, cy + rr * 0.9, cx + rr * 1.1, H), int(rr * 0.6), fill=_rgba(col), outline=(20, 20, 30, 255),
                                width=int(1 * s))
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(250, 220, 190, 255), outline=(40, 30, 30, 255), width=int(1 * s))
            e = rr * 0.35
            d.ellipse((cx - e - 1.5 * s, cy - e * 0.6, cx - e + 1.5 * s, cy - e * 0.6 + 3 * s), fill=(30, 20, 20, 255))
            d.ellipse((cx + e - 1.5 * s, cy - e * 0.6, cx + e + 1.5 * s, cy - e * 0.6 + 3 * s), fill=(30, 20, 20, 255))
            mb = (cx - e, cy + e * 0.2, cx + e, cy + e * 1.4)
            if mood == 2:
                d.chord(mb, 0, 180, fill=(170, 40, 50, 255))
            elif mood == 1:
                d.line((cx - e * 0.8, cy + e * 0.8, cx + e * 0.8, cy + e * 0.8), fill=(60, 30, 30, 255), width=int(1.2 * s))
            else:
                d.arc((cx - e, cy + e * 0.6, cx + e, cy + e * 1.8), 200, 340, fill=(60, 30, 30, 255), width=int(1.4 * s))
                d.line((cx - e * 1.3, cy - e * 1.2, cx - e * 0.3, cy - e * 0.8), fill=(60, 30, 30, 255), width=int(1.2 * s))
                d.line((cx + e * 1.3, cy - e * 1.2, cx + e * 0.3, cy - e * 0.8), fill=(60, 30, 30, 255), width=int(1.2 * s))
    return art('k36_crowd_%d_%d' % (g, mood), 56, 44, f)


def effect_icon(g, up):
    col = GROUPS36[g][1]

    def f(d, im, s):
        W, H = im.width, im.height
        d.ellipse((1 * s, 1 * s, W - 1 * s, H - 1 * s), fill=_rgba(col), outline=(255, 255, 255, 230), width=int(1 * s))
        d.text((W / 2, H / 2 + 0.5 * s), GROUPS36[g][0][0], font=_f('jalnan', 8, s), fill=(255, 255, 255, 255), anchor='mm')
        ac = (60, 230, 110, 255) if up else (255, 70, 80, 255)
        tx, ty = W * 0.84, H * 0.2
        if up:
            d.polygon([(tx, ty - 4 * s), (tx - 4 * s, ty + 3 * s), (tx + 4 * s, ty + 3 * s)], fill=ac, outline=(0, 0, 0, 255))
        else:
            d.polygon([(tx, ty + 4 * s), (tx - 4 * s, ty - 3 * s), (tx + 4 * s, ty - 3 * s)], fill=ac, outline=(0, 0, 0, 255))
    return art('k36_eff_%d_%d' % (g, up), 22, 20, f)


def blank(w=4, h=4):
    def f(d, im, s):
        pass
    return art('k3_blank_%d_%d' % (w, h), w, h, f)


# ================================================================== 37. 가래떡 썰기
def tteok_rod(L):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 1 * s, W + 20 * s, H - 1 * s), int(H / 2.2), fill=(250, 250, 244, 255), outline=(200, 196, 180, 255),
                            width=int(1 * s))
        d.rectangle((W * 0.0 + 6 * s, H * 0.22, W, H * 0.36), fill=(255, 255, 255, 255))
        d.rectangle((W * 0.0 + 6 * s, H * 0.7, W, H * 0.82), fill=(232, 230, 220, 255))
    return art('k37_rod_%d' % L, L, 18, f)


def tteok_piece(L):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 1 * s, W, H - 1 * s), 3 * s, fill=(250, 250, 244, 255), outline=(200, 196, 180, 255), width=int(1 * s))
        d.rectangle((2 * s, H * 0.22, W - 2 * s, H * 0.36), fill=(255, 255, 255, 255))
        d.rectangle((2 * s, H * 0.7, W - 2 * s, H * 0.82), fill=(232, 230, 220, 255))
    return art('k37_piece_%d' % L, L, 18, f)


def knife():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((W * 0.3, 0, W * 0.7, H * 0.32), 2 * s, fill=(110, 70, 40, 255), outline=(60, 36, 20, 255), width=int(1 * s))
        d.polygon([(W * 0.15, H * 0.3), (W * 0.85, H * 0.3), (W * 0.85, H * 0.9), (W * 0.5, H), (W * 0.15, H * 0.9)],
                  fill=(210, 220, 232, 255), outline=(90, 100, 120, 255))
        d.line((W * 0.5, H * 0.34, W * 0.5, H * 0.96), fill=(255, 255, 255, 200), width=int(1 * s))
    return art('k37_knife', 22, 58, f)


def machine():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((W * 0.2, 0, W, H * 0.9), 6 * s, fill=(170, 176, 190, 255), outline=(70, 76, 90, 255), width=int(1.5 * s))
        d.rectangle((W * 0.26, H * 0.1, W * 0.94, H * 0.3), fill=(60, 70, 100, 255))
        d.text((W * 0.6, H * 0.2), '떡 기계', font=_f('jalnan', 8, s), fill=(255, 255, 255, 255), anchor='mm')
        d.rounded_rectangle((0, H * 0.5, W * 0.3, H * 0.8), 3 * s, fill=(130, 136, 150, 255), outline=(70, 76, 90, 255), width=int(1 * s))
        d.ellipse((W * 0.62, H * 0.42, W * 0.82, H * 0.62), fill=(240, 80, 80, 255), outline=(90, 20, 20, 255), width=int(1 * s))
    return art('k37_machine', 70, 70, f)


def ruler(L):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(240, 220, 150, 255), outline=(120, 100, 50, 255), width=int(1 * s))
        for k in range(0, L + 1, 5):
            x = W - k * s
            h = H * (0.6 if k % 10 == 0 else 0.3)
            d.line((x, 0, x, h), fill=(60, 50, 30, 255), width=int(1 * s))
            if k % 10 == 0 and 0 < k < L:
                d.text((x, H * 0.82), str(k // 10), font=_f('nanum', 6, s), fill=(60, 50, 30, 255), anchor='mm')
    return art('k37_ruler_%d' % L, L, 14, f)


def board(L):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 0, W, H), 6 * s, fill=(196, 150, 96, 255), outline=(120, 84, 44, 255), width=int(1.5 * s))
        for k in range(6):
            y = H * (0.15 + k * 0.14)
            d.line((6 * s, y, W - 6 * s, y + 1 * s), fill=(180, 134, 84, 255), width=int(1 * s))
    return art('k37_board_%d' % L, L, 56, f)


def guide_line():
    def f(d, im, s):
        W, H = im.width, im.height
        for y in range(0, int(H), int(5 * s)):
            d.line((W / 2, y, W / 2, y + 3 * s), fill=(255, 80, 110, 255), width=int(1.6 * s))
        d.polygon([(W / 2 - 5 * s, 0), (W / 2 + 5 * s, 0), (W / 2, 6 * s)], fill=(255, 80, 110, 255))
    return art('k37_guide', 12, 44, f)


def plate():
    def f(d, im, s):
        W, H = im.width, im.height
        d.ellipse((0, 0, W, H), fill=(236, 240, 250, 255), outline=(120, 130, 160, 255), width=int(1.5 * s))
        d.ellipse((W * 0.12, H * 0.15, W * 0.88, H * 0.85), outline=(190, 200, 220, 255), width=int(1 * s))
    return art('k37_plate', 100, 30, f)


# ================================================================== 38. 짜장면 배달
def city(xs, ys, hw):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 0, W, H), 8 * s, fill=(160, 170, 150, 255))
        cx, cy = W / 2, H / 2
        for x in xs:
            d.rectangle((cx + (x - hw) * s, 0, cx + (x + hw) * s, H), fill=(58, 60, 68, 255))
        for y in ys:
            d.rectangle((0, cy - (y + hw) * s, W, cy - (y - hw) * s), fill=(58, 60, 68, 255))
        for x in xs:
            for k in range(0, int(H), int(14 * s)):
                d.line((cx + x * s, k, cx + x * s, k + 6 * s), fill=(220, 210, 120, 255), width=int(1 * s))
        for y in ys:
            for k in range(0, int(W), int(14 * s)):
                d.line((k, cy - y * s, k + 6 * s, cy - y * s), fill=(220, 210, 120, 255), width=int(1 * s))
    return art('k38_city', 440, 206, f)


def building(k):
    roofs = [(190, 90, 80), (90, 120, 190), (120, 160, 110), (200, 160, 90)]
    col = roofs[k]

    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(200, 196, 180, 255))
        d.rectangle((5 * s, 5 * s, W - 5 * s, H - 5 * s), fill=_rgba(col), outline=(60, 50, 50, 255), width=int(1 * s))
        d.line((5 * s, H / 2, W - 5 * s, H / 2), fill=tuple(int(c * 0.75) for c in col) + (255,), width=int(2 * s))
        for j in range(3):
            d.rectangle((W * (0.2 + j * 0.25), H * 0.2, W * (0.28 + j * 0.25), H * 0.3), fill=(230, 230, 240, 255))
    return art('k38_bld_%d' % k, 78, 62, f)


def restaurant():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 0, W, H), fill=(200, 196, 180, 255))
        d.rectangle((5 * s, 5 * s, W - 5 * s, H - 5 * s), fill=(190, 30, 40, 255), outline=(90, 10, 10, 255), width=int(1 * s))
        d.rectangle((10 * s, H * 0.3, W - 10 * s, H * 0.7), fill=(250, 220, 80, 255))
        d.text((W / 2, H / 2), '중화반점', font=_f('jalnan', 11, s), fill=(170, 20, 30, 255), anchor='mm')
        for x in (0.15, 0.85):
            d.ellipse((W * x - 4 * s, H * 0.12, W * x + 4 * s, H * 0.26), fill=(255, 80, 60, 255), outline=(255, 220, 120, 255))
    return art('k38_rest', 78, 62, f)


def scooter():
    def f(d, im, s):
        W, H = im.width, im.height
        cx = W / 2
        d.rounded_rectangle((cx - 3 * s, 0, cx + 3 * s, 6 * s), 2 * s, fill=(30, 30, 30, 255))
        d.rounded_rectangle((cx - 3 * s, H - 6 * s, cx + 3 * s, H), 2 * s, fill=(30, 30, 30, 255))
        d.rounded_rectangle((cx - 5 * s, 4 * s, cx + 5 * s, H - 4 * s), 3 * s, fill=(220, 40, 50, 255), outline=(80, 10, 10, 255), width=int(1 * s))
        d.line((cx - 8 * s, 6 * s, cx + 8 * s, 6 * s), fill=(60, 60, 60, 255), width=int(1.5 * s))
        d.ellipse((cx - 4 * s, H * 0.35, cx + 4 * s, H * 0.6), fill=(250, 210, 60, 255), outline=(90, 60, 10, 255))
        d.rectangle((cx - 6 * s, H * 0.62, cx + 6 * s, H - 5 * s), fill=(150, 30, 30, 255), outline=(60, 10, 10, 255))
    return art('k38_scooter', 18, 26, f)


def car(col, name):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((1 * s, 1 * s, W - 1 * s, H - 1 * s), 4 * s, fill=_rgba(col), outline=(20, 20, 30, 255), width=int(1 * s))
        d.rounded_rectangle((3 * s, H * 0.18, W - 3 * s, H * 0.36), 2 * s, fill=(150, 200, 240, 255))
        d.rounded_rectangle((3 * s, H * 0.68, W - 3 * s, H * 0.8), 2 * s, fill=(150, 200, 240, 255))
    return art('k38_car_%s' % name, 14, 24, f)


def order_pin(hot):
    def f(d, im, s):
        W, H = im.width, im.height
        col = (255, 120, 60, 255) if hot else (120, 140, 220, 255)
        d.ellipse((1 * s, 1 * s, W - 1 * s, W - 1 * s), fill=col, outline=(255, 255, 255, 255), width=int(1.4 * s))
        d.polygon([(W * 0.3, W * 0.8), (W * 0.7, W * 0.8), (W / 2, H)], fill=col)
        d.chord((W * 0.22, W * 0.3, W * 0.78, W * 0.78), 0, 180, fill=(255, 255, 255, 255))
        d.line((W * 0.3, W * 0.42, W * 0.7, W * 0.42), fill=(60, 30, 20, 255), width=int(1.2 * s))
    return art('k38_pin_%d' % hot, 20, 26, f)


# ================================================================== 39. 탁구
def tt_table(proj):
    """proj(X, Z) → 무대 (x, y). 탁구대 사다리꼴 + 그물."""
    W0, H0 = 340, 130
    ox, oy = W0 / 2, 30         # 그림 안에서 무대 (0, 0) 위치: x 가운데, 그림 위쪽에서 오프셋
    top = 20                     # 무대 y = 20 이 그림 맨 위

    def P(X, Z, Y=0):
        x, y = proj(X, Z, Y)
        return ((x + ox), (top - y))

    def f(d, im, s):
        def S(pt):
            return (pt[0] * s, pt[1] * s)
        c = [S(P(-1, 0)), S(P(1, 0)), S(P(1, 1)), S(P(-1, 1))]
        leg = [S(P(-0.9, 0.05)), S(P(0.9, 0.05))]
        for x, y in leg:
            d.rectangle((x - 2 * s, y, x + 2 * s, y + 22 * s), fill=(30, 30, 40, 255))
        d.polygon([c[0], c[1], (c[1][0], c[1][1] + 5 * s), (c[0][0], c[0][1] + 5 * s)], fill=(20, 50, 100, 255))
        d.polygon(c, fill=(32, 92, 170, 255), outline=(255, 255, 255, 255))
        d.line(c + [c[0]], fill=(255, 255, 255, 255), width=int(1.6 * s))
        d.line([S(P(0, 0)), S(P(0, 1))], fill=(255, 255, 255, 200), width=int(0.8 * s))
        a, b = S(P(-1.08, 0.5)), S(P(1.08, 0.5))
        a2, b2 = S(P(-1.08, 0.5, 0.13)), S(P(1.08, 0.5, 0.13))
        d.polygon([a, b, b2, a2], fill=(230, 230, 240, 150))
        for k in range(1, 12):
            t = k / 12
            d.line([(a[0] + (b[0] - a[0]) * t, a[1]), (a2[0] + (b2[0] - a2[0]) * t, a2[1])], fill=(80, 80, 90, 160), width=int(0.6 * s))
        d.line([a2, b2], fill=(255, 255, 255, 255), width=int(1.4 * s))
        d.line([a, a2], fill=(40, 40, 50, 255), width=int(1.6 * s))
        d.line([b, b2], fill=(40, 40, 50, 255), width=int(1.6 * s))
    return art('k39_table', W0, H0, f), (0, top - H0 / 2)


def ball():
    def f(d, im, s):
        W = im.width
        d.ellipse((0.5 * s, 0.5 * s, W - 0.5 * s, W - 0.5 * s), fill=(255, 250, 235, 255), outline=(200, 160, 100, 255), width=int(0.8 * s))
        d.ellipse((W * 0.2, W * 0.15, W * 0.5, W * 0.42), fill=(255, 255, 255, 255))
    return art('k39_ball', 12, 12, f)


def ball_shadow():
    def f(d, im, s):
        d.ellipse((0, 0, im.width, im.height), fill=(0, 0, 20, 110))
    return art('k39_shadow', 14, 6, f)


def target_ring():
    def f(d, im, s):
        W = im.width
        d.ellipse((1 * s, 1 * s, W - 1 * s, W - 1 * s), outline=(255, 220, 90, 230), width=int(1.6 * s))
        d.ellipse((W / 2 - 2 * s, W / 2 - 2 * s, W / 2 + 2 * s, W / 2 + 2 * s), fill=(255, 220, 90, 230))
    return art('k39_ring', 26, 26, f)


def paddle(col, name, w=40):
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((W * 0.42, H * 0.6, W * 0.58, H), 2 * s, fill=(170, 120, 70, 255), outline=(80, 50, 30, 255), width=int(1 * s))
        d.ellipse((1 * s, 1 * s, W - 1 * s, H * 0.72), fill=_rgba(col, 225), outline=(30, 10, 10, 255), width=int(1.2 * s))
        d.ellipse((W * 0.2, H * 0.08, W * 0.5, H * 0.3), fill=(255, 255, 255, 60))
    return art('k39_paddle_%s' % name, w, w * 1.15, f)


# ================================================================== 40. 화포 쏘기
def ground40():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, 8 * s, W, H), fill=(110, 84, 54, 255))
        d.rectangle((0, 0, W, 10 * s), fill=(86, 140, 70, 255))
        for k in range(60):
            x = (k * 53 % 479) / 479 * W
            d.line((x, 8 * s, x + 2 * s, 2 * s), fill=(120, 180, 90, 255), width=int(1 * s))
    return art('k40_ground', 480, 40, f)


def fort_wall():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((0, H * 0.2, W, H), fill=(170, 150, 120, 255), outline=(90, 80, 60, 255), width=int(1 * s))
        for k in range(0, int(W), int(14 * s)):
            d.rectangle((k, 0, k + 8 * s, H * 0.22), fill=(170, 150, 120, 255), outline=(90, 80, 60, 255), width=int(1 * s))
        for r in range(5):
            y = H * 0.3 + r * 9 * s
            off = (r % 2) * 8 * s
            for x in range(int(-off), int(W), int(16 * s)):
                d.rectangle((x, y, x + 16 * s, y + 9 * s), outline=(140, 120, 95, 255), width=int(0.8 * s))
    return art('k40_wall', 80, 70, f)


def cannon_barrel():
    def f(d, im, s):
        W, H = im.width, im.height
        d.polygon([(W * 0.5, H * 0.2), (W, H * 0.3), (W, H * 0.7), (W * 0.5, H * 0.8)], fill=(60, 60, 66, 255))
        d.rounded_rectangle((W * 0.5, H * 0.18, W * 0.98, H * 0.82), 3 * s, fill=(70, 72, 80, 255), outline=(20, 20, 26, 255), width=int(1 * s))
        for x in (0.62, 0.8, 0.95):
            d.rectangle((W * x, H * 0.12, W * x + 2 * s, H * 0.88), fill=(150, 120, 60, 255))
    return art('k40_barrel', 70, 14, f)


def cannon_base():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rectangle((W * 0.1, H * 0.2, W * 0.9, H * 0.6), fill=(130, 90, 50, 255), outline=(60, 40, 20, 255), width=int(1 * s))
        for x in (0.25, 0.75):
            d.ellipse((W * x - 7 * s, H - 14 * s, W * x + 7 * s, H), fill=(100, 70, 40, 255), outline=(50, 30, 15, 255), width=int(1.5 * s))
            d.ellipse((W * x - 2 * s, H - 9 * s, W * x + 2 * s, H - 5 * s), fill=(50, 30, 15, 255))
    return art('k40_base', 40, 22, f)


def cannonball():
    def f(d, im, s):
        W = im.width
        d.ellipse((0.5 * s, 0.5 * s, W - 0.5 * s, W - 0.5 * s), fill=(40, 40, 46, 255), outline=(10, 10, 12, 255))
        d.ellipse((W * 0.2, W * 0.2, W * 0.45, W * 0.45), fill=(150, 150, 160, 255))
    return art('k40_ball', 9, 9, f)


def enemy_flag(down):
    def f(d, im, s):
        W, H = im.width, im.height
        if down:
            d.line((2 * s, H - 3 * s, W - 2 * s, H - 8 * s), fill=(110, 80, 40, 255), width=int(2 * s))
            d.polygon([(W * 0.5, H - 6 * s), (W - 3 * s, H - 9 * s), (W - 6 * s, H - 1 * s), (W * 0.55, H)], fill=(130, 40, 40, 255))
        else:
            d.line((W * 0.25, 0, W * 0.25, H), fill=(110, 80, 40, 255), width=int(2 * s))
            d.polygon([(W * 0.25, 2 * s), (W - 1 * s, H * 0.18), (W * 0.25, H * 0.36)], fill=(220, 50, 50, 255), outline=(100, 10, 10, 255))
            d.text((W * 0.5, H * 0.18), '敵', font=_f('black', 7, s), fill=(255, 240, 200, 255), anchor='mm')
            d.polygon([(W * 0.1, H), (W * 0.4, H), (W * 0.25, H - 6 * s)], fill=(90, 70, 40, 255))
    return art('k40_flag_%d' % down, 26, 38, f)


def boom():
    def f(d, im, s):
        W = im.width
        c = W / 2
        for k in range(10):
            a = k * math.pi / 5
            d.polygon([(c, c), (c + math.cos(a - 0.2) * W * 0.25, c + math.sin(a - 0.2) * W * 0.25),
                       (c + math.cos(a) * W * 0.48, c + math.sin(a) * W * 0.48),
                       (c + math.cos(a + 0.2) * W * 0.25, c + math.sin(a + 0.2) * W * 0.25)], fill=(255, 170, 60, 230))
        d.ellipse((c - W * 0.2, c - W * 0.2, c + W * 0.2, c + W * 0.2), fill=(255, 240, 160, 255))
    return art('k40_boom', 34, 34, f)


def abacus_frame():
    def f(d, im, s):
        W, H = im.width, im.height
        d.rounded_rectangle((0, 0, W, H), 6 * s, fill=(100, 62, 32, 255), outline=(60, 36, 18, 255), width=int(1.5 * s))
        d.rounded_rectangle((7 * s, 7 * s, W - 7 * s, H - 7 * s), 3 * s, fill=(46, 30, 20, 255))
    return art('k32_abframe', 200, 112, f)
