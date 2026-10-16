# -*- coding: utf-8 -*-
"""게임을 켜면 맨 처음 나오는 제작사 로고 영상 (제작자 제공 'CYW GAMES' 영상).

엔트리에는 동영상 블록이 없어서, 영상을 그림(프레임)과 소리로 나눠 0.75배 속도로 이어서 보여 준다.
  - 원본 4.06초, 24fps → 0.75배 = 5.42초. 원본에서 1초에 16장을 뽑아 1초에 12장씩 보여 준다 (= 0.75배).
  - 소리는 ffmpeg atempo=0.75 로 늘인 mp3.
클릭하거나 스페이스를 누르면 건너뛴다.
"""
import os
import glob
import subprocess
from PIL import Image
from entrygen import *
import gui as G
from art_common import OUT

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets_src', 'intro', 'intro.mp4')
DIR = os.path.join(OUT, 'intro')
SPEED = 0.75
SRC_FPS = 16
SHOW_FPS = SRC_FPS * SPEED      # 12


def make_assets():
    """프레임(256색 PNG)과 0.75배 소리를 만든다 (이미 있으면 그대로)."""
    os.makedirs(DIR, exist_ok=True)
    mp3 = os.path.join(DIR, 'intro_075.mp3')
    if not glob.glob(os.path.join(DIR, 'q_*.png')):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vf', 'fps=%d,scale=362:270:flags=lanczos' % SRC_FPS,
                        os.path.join(DIR, 'f_%03d.png')], check=True)
        for f in sorted(glob.glob(os.path.join(DIR, 'f_*.png'))):
            im = Image.open(f).convert('RGB')
            im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(
                f.replace('f_', 'q_'), optimize=True)
    if not os.path.exists(mp3):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vn', '-filter:a', 'atempo=%g' % SPEED, '-ac', '2',
                        '-ar', '44100', '-b:a', '128k', mp3], check=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', mp3],
                               capture_output=True, text=True).stdout.strip())
    return sorted(glob.glob(os.path.join(DIR, 'q_*.png'))), mp3, dur


def build(P, ctx):
    sc = ctx['S_INTRO']
    frames, mp3, dur = make_assets()
    G.bg(P, sc, ctx['BLACK'])
    v = P.sprite(G.uname(sc, '인트로영상'), sc, [('%02d' % k, f) for k, f in enumerate(frames, 1)], pic_scale=1.0, x=0, y=0)
    v.add_sound('intro', mp3, round(dur, 2))
    P.var('인트로끝', 0)
    done = [if_(eq(V('인트로끝'), 0), setv('인트로끝', 1), stop_sounds(), goto_scene(ctx['S_TITLE']))]
    v.on(on_run(), setv('인트로끝', 0), shape('01'), show(), wait(0.1), play('intro'),
         rep(len(frames) - 1, wait(round(1.0 / SHOW_FPS, 4)), next_shape()),
         wait(0.6), *done)
    v.on(on_click(), *done)
    text(P, sc, '건너뛰기안내', '클릭하면 건너뛰기', 180, -122, 8, '#5A6488', G.F_BODY, True, 0, w=110, h=12) \
        .on(on_key(K_SPACE), *done)
    return v


text = G.text
