# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 1~10번."""
import random
from games_common import *
import mg_art3 as A3

T = 2
GAMES, game = registry()


# ================================================================== 1. 무대 조명 퍼즐 (Lights Out)
def _lamp(on):
    def f(d, im, s):
        W = im.width
        c = W / 2
        if on:
            for k in range(12, 0, -1):
                a = int(10 + 12 * (12 - k))
                r = W * 0.5 * k / 12
                d.ellipse((c - r, c - r, c + r, c + r), fill=(255, 226, 120, min(255, a // 3)))
            d.ellipse((W * 0.2, W * 0.2, W * 0.8, W * 0.8), fill=(255, 244, 196, 255), outline=(255, 255, 255, 255), width=int(1.5 * s))
            d.ellipse((W * 0.32, W * 0.3, W * 0.5, W * 0.44), fill=(255, 255, 255, 200))
        else:
            d.ellipse((W * 0.2, W * 0.2, W * 0.8, W * 0.8), fill=(34, 40, 66, 255), outline=(96, 110, 160, 255), width=int(1.5 * s))
            d.ellipse((W * 0.3, W * 0.3, W * 0.7, W * 0.7), fill=(20, 24, 44, 255))
            d.ellipse((W * 0.34, W * 0.32, W * 0.48, W * 0.42), fill=(120, 130, 170, 90))
    return A3.art('s01_lamp_%d' % on, 42, 42, f)


@game(1)
def g01(P, ctx):
    R, N = 3, 4
    m = mg(P, ctx, T, 1, time_limit=80, status='라운드 1/%d' % R, dim=80)
    rng = random.Random(201)

    def press(b, k):
        r, c = divmod(k, N)
        for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < N and 0 <= cc < N:
                b[rr * N + cc] ^= 1
    puz = []
    for n_press in (3, 5, 7):
        got = []
        while len(got) < 8:
            b = [1] * (N * N)
            for k in rng.sample(range(N * N), n_press):
                press(b, k)
            s = ''.join(map(str, b))
            if s.count('0') >= 5 and s not in got:
                got.append(s)
        puz += got
    P.list('조명퍼즐', puz)
    P.list('조명', [1] * (N * N))
    vars_(P, '조명수', '조명판')
    panel(P, m.sc, '조명판넬', 0, -12, 206, 206, 'glass')
    xs = [-66 + 44 * c for c in range(N)]
    ys = [54 - 44 * r for r in range(N)]
    total = add(*[LGET('조명', k + 1) for k in range(N * N)])
    for k in range(N * N):
        r, c = divmod(k, N)
        o = m.S('조명%d' % (k + 1), [('off', _lamp(0)), ('on', _lamp(1))], xs[c], ys[r])
        nb = [k] + [rr * N + cc for rr, cc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)) if 0 <= rr < N and 0 <= cc < N]
        o.on(on_click(), if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)),
                             *[lst_set('조명', j + 1, sub(1, LGET('조명', j + 1))) for j in nb],
                             chg('합계', 1), setv('조명수', total), cast('조명갱신'), cast('조명누름')))
        o.on(on_msg('조명갱신'), shape(add(LGET('조명', k + 1), 1)))
        o.on(on_click(), if_(eq(V('입력가능'), 1), o.pct(88), wait(0.06), o.pct(100)))
    info = m.T('조명안내', '', 170, 40, 11, C_WHITE, F_BODY, True, 0, w=120, h=60)
    info.on(on_msg('조명갱신'), write(join('켜진 조명\n', V('조명수'), ' / ', N * N, '\n누른 횟수 ', V('합계'))))
    reset = [if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)),
                 *[lst_set('조명', k, char_at(V('조명판'), k)) for k in range(1, N * N + 1)],
                 setv('조명수', total), cast('조명갱신'))]
    button(P, m.sc, '처음부터', '처음 상태로', 170, -30, 100, 24, 'steel', actions=reset)
    ok = m.S('조명성공', K.big_text('ALL ON!', 34, 'royal'), 0, -12, visible=False)
    ok.on(on_msg('조명성공'), ok.pct(40), show(), rep(6, ok.grow_pct(12), wait(0.016)), wait(0.7), hide())
    mgr = hidden(m, '조명담당')
    mgr.on(on_msg('게임시작'), setv('라운드', 1),
           until(or_(gt(V('라운드'), R), eq(V('게임중'), 0)),
                 setv('조명판', LGET('조명퍼즐', add(mul(sub(V('라운드'), 1), 8), rnd(1, 8)))),
                 *[lst_set('조명', k, char_at(V('조명판'), k)) for k in range(1, N * N + 1)],
                 setv('합계', 0), setv('조명수', total), cast('조명갱신'), setv('입력가능', 1),
                 setv('미니표시', join('라운드 ', V('라운드'), '/', R)),
                 wait_until(or_(eq(V('조명수'), N * N), eq(V('게임중'), 0))),
                 setv('입력가능', 0),
                 if_(eq(V('조명수'), N * N), chg('맞춤', 1), cast('조명성공'), wait(1.1)),
                 chg('라운드', 1)),
           *m.end_blocks(add(mul(V('맞춤'), 26), mul(V('남은시간'), 0.4))))
    mgr.on(on_msg('시간끝'), setv('입력가능', 0), *m.end_blocks(add(mul(V('맞춤'), 26), div(V('조명수'), 2))))
    m.on_start(setv('맞춤', 0), setv('합계', 0), setv('입력가능', 0), setv('조명수', 0),
               *[lst_set('조명', k, 1) for k in range(1, N * N + 1)])
    m.snd('조명누름', play('tick'))
    m.snd('조명성공', play('good'))
    m.finish('조명을 누르면 그 조명과 위·아래·양옆 조명이 함께\n켜지거나 꺼져요. 16개를 모두 켜면 다음 무대! (3라운드)',
             '조작: 마우스로 조명 클릭  ·  막히면 "처음 상태로"')
    return True
