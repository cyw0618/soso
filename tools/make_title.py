# -*- coding: utf-8 -*-
"""타이틀 장면 배경(960x540).

편집한 표지 그림("군수집 막내아들")만 보여준다. 표지는 가운데에 크게, 양옆 여백은 같은 그림을
흐리게 늘려서 채운다. 다른 문구/장식은 넣지 않는다.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from art_common import *
from make_cover import build_cover

W, H = 960, 540


def title_bg(cover=None):
    cover = cover or build_cover()
    cw, ch = cover.size
    # 양옆 채움: 표지를 화면 너비로 키워 가운데 부분을 잘라 흐리게
    sc = W / cw
    back = cover.resize((W, int(ch * sc)), Image.LANCZOS)
    top = max(0, (back.height - H) // 2 + 40)
    back = back.crop((0, top, W, top + H)).filter(ImageFilter.GaussianBlur(22))
    back = ImageEnhance.Brightness(back).enhance(0.62)
    # 표지 본체 (세로를 화면에 꽉 채움)
    pw = int(cw * H / ch)
    panel = cover.resize((pw, H), Image.LANCZOS)
    bg = back.copy()
    px = (W - pw) // 2
    # 표지 좌우 가장자리를 부드럽게 섞어서 경계가 눈에 띄지 않게
    mask = Image.new('L', (pw, H), 255)
    md = ImageDraw.Draw(mask)
    for i in range(14):
        a = int(255 * (i / 14))
        md.line([(i, 0), (i, H)], fill=a)
        md.line([(pw - 1 - i, 0), (pw - 1 - i, H)], fill=a)
    bg.paste(panel, (px, 0), mask)
    return bg


def build():
    ensure_out()
    save(title_bg(), 'title_bg')


if __name__ == '__main__':
    build()
    print('title done')
