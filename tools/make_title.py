# -*- coding: utf-8 -*-
"""타이틀 장면 배경(960x540)과 큰 버튼 그림."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from art_common import *
from make_cover import build_cover

W, H = 960, 540


def sparkle(d, x, y, r, col):
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22),
               (x, y + r), (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=col)


def title_cover_panel():
    """표지 그림에서 '재벌집 막내아들' 글자를 가리고 '군수집 막내아들'로 바꾼 세로 표지."""
    cover = build_cover()               # 1077 x 1485
    cw, ch = cover.size
    cover = cover.convert('RGBA')
    # 아래쪽 제목 영역(원본 y>355/495)을 어두운 그라데이션으로 덮는다
    y0 = int(ch * 0.69)
    ov = Image.new('RGBA', cover.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for y in range(y0, ch):
        t = (y - y0) / (ch - y0)
        a = int(255 * min(1.0, 0.55 + t * 2.4))
        od.line([(0, y), (cw, y)], fill=(8, 14, 34, a))
    cover = Image.alpha_composite(cover, ov)
    d = ImageDraw.Draw(cover)
    f = font('black', int(cw * 0.125))
    cx, cy = cw / 2, ch * 0.915
    d.text((cx + 4, cy + 6), '군수집 막내아들', font=f, fill=(0, 10, 40, 255), anchor='mm', stroke_width=10, stroke_fill=(0, 10, 40, 255))
    d.text((cx, cy), '군수집 막내아들', font=f, fill=(255, 255, 255, 255), anchor='mm', stroke_width=7, stroke_fill=(20, 90, 200, 255))
    d.text((cx, cy), '군수집 막내아들', font=f, fill=(255, 255, 255, 255), anchor='mm')
    return cover.convert('RGB')


def title_bg():
    bg = vgradient((W, H), (10, 18, 48), (52, 28, 86)).convert('RGBA')
    rnd = random.Random(7)
    # 도시 야경 실루엣
    d = ImageDraw.Draw(bg)
    x = 0
    while x < W:
        bw = rnd.randint(30, 70)
        bh = rnd.randint(60, 220)
        col = (22 + rnd.randint(0, 14), 28 + rnd.randint(0, 14), 64 + rnd.randint(0, 20), 255)
        d.rectangle((x, H - bh, x + bw, H), fill=col)
        for wy in range(H - bh + 8, H - 6, 14):
            for wx in range(x + 6, x + bw - 6, 11):
                if rnd.random() < 0.35:
                    d.rectangle((wx, wy, wx + 5, wy + 7), fill=(255, 224, 140, 200))
        x += bw + rnd.randint(0, 8)
    # 반짝이
    for _ in range(40):
        sparkle(d, rnd.randint(0, W), rnd.randint(0, H), rnd.randint(3, 9), (255, 240, 180, rnd.randint(90, 220)))
    # 오른쪽 어둡게 (글자 가독성)
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for xx in range(W):
        a = int(110 * max(0, (xx - 330) / (W - 330)))
        sd.line([(xx, 0), (xx, H)], fill=(0, 0, 12, a))
    bg = Image.alpha_composite(bg, shade)

    # 표지 (왼쪽)
    cover = title_cover_panel()
    ph = H - 40
    pw = int(cover.width * ph / cover.height)
    cover = cover.resize((pw, ph), Image.LANCZOS)
    px, py = 34, 20
    glow = Image.new('RGBA', (pw + 60, ph + 60), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle((20, 20, pw + 40, ph + 40), 22, fill=(70, 150, 255, 200))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    bg.alpha_composite(glow, (px - 30, py - 30))
    m = Image.new('L', cover.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, pw, ph), 18, fill=255)
    bg.paste(cover, (px, py), m)
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle((px - 3, py - 3, px + pw + 3, py + ph + 3), 20, outline=(255, 226, 120, 255), width=4)

    # 오른쪽 제목 영역
    tx = px + pw + 40 + (W - (px + pw + 40) - 40) // 2
    d.text((tx, 66), '조치원 군수 선거 대작전', font=font('dohyeon', 30), fill=(255, 226, 120), anchor='mm', stroke_width=3, stroke_fill=(40, 20, 70))
    draw_text(bg, (tx, 128), '군수집', font('black', 96), fill=(255, 255, 255), stroke=7, stroke_fill=(30, 90, 210), anchor='mm', shadow=(5, 6, (10, 10, 40)))
    draw_text(bg, (tx, 224), '막내아들', font('black', 96), fill=(255, 214, 80), stroke=7, stroke_fill=(150, 40, 20), anchor='mm', shadow=(5, 6, (10, 10, 40)))
    d.text((tx, 292), '큰아버지 둘을 지지율로 꺾어라!', font=font('nanum', 22), fill=(220, 230, 255), anchor='mm')
    return bg.convert('RGB')


def make_button(text, w, h, top, bottom, edge, fsize=40, txt=(255, 255, 255)):
    S = 3
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = h * S // 2 - 2
    d.rounded_rectangle((3 * S, 5 * S, w * S - 3 * S, h * S - 2 * S), r, fill=(0, 0, 0, 90))  # 그림자
    grad = vgradient((w * S, h * S), top, bottom)
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((2 * S, 2 * S, w * S - 2 * S, h * S - 5 * S), r, fill=255)
    im.paste(grad, (0, 0), m)
    d.rounded_rectangle((2 * S, 2 * S, w * S - 2 * S, h * S - 5 * S), r, outline=edge, width=3 * S)
    # 윗면 하이라이트
    d.rounded_rectangle((12 * S, 6 * S, w * S - 12 * S, h * S // 2 - 2 * S), r // 2, fill=(255, 255, 255, 55))
    f = font('black', fsize * S)
    tcy = (h * S - 3 * S) // 2
    d.text((w * S / 2, tcy), text, font=f, fill=txt, anchor='mm', stroke_width=2 * S, stroke_fill=edge)
    return im.resize((w, h), Image.LANCZOS)


def build():
    ensure_out()
    save(title_bg(), 'title_bg')
    save(make_button('게임 시작', 300, 66, (255, 190, 70), (240, 110, 30), (130, 50, 10), 32), 'btn_start')
    save(make_button('게임 방법', 300, 66, (110, 190, 255), (40, 100, 220), (15, 40, 110), 32), 'btn_howto')
    save(make_button('랭킹', 300, 66, (190, 150, 255), (110, 70, 220), (50, 25, 110), 32), 'btn_rank')


if __name__ == '__main__':
    build()
    print('title done')
