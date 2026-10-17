# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 31~40번."""
import random
from games_common import *
import mg_art3 as A3

T = 3
GAMES, game = registry()

import art3d as AD


def clamp(var, lo, hi):
    return [if_(lt(V(var), lo), setv(var, lo)), if_(gt(V(var), hi), setv(var, hi))]


def pfx(prefix):
    """접두어 붙은 변수 도우미: W(이름) 값, S(이름, 값) 정하기, C(이름, 값) 바꾸기."""
    return (lambda n: V(prefix + n), lambda n, v: setv(prefix + n, v), lambda n, v: chg(prefix + n, v))


def pop(m, base, pics, x, y, msg, hold=0.5, follow=None):
    """신호를 받으면 튀어나왔다 사라지는 글자/그림. pics 가 여럿이면 V('_mv') 번 모양. follow=(x식, y식) 이면 그 자리."""
    o = m.S(base, pics, x, y, visible=False)
    pos = [xy(follow[0], follow[1])] if follow else [xy(x, y)]
    o.on(on_msg(msg), *([shape(V('_mv'))] if len(pics) > 1 else []), *pos, to_front(), o.pct(40), fx('transparency', 0), show(),
         rep(5, o.grow_pct(14), wait(0.016)), rep(2, o.grow_pct(-5), wait(0.016)), wait(hold),
         rep(8, fx_add('transparency', 12), mvy(1), wait(0.02)), hide())
    return o


def seg_d2(px, py, ax, ay, bx, by, out, tag):
    """점 P 와 선분 AB 사이 거리의 제곱을 변수 out 에 (tag: 임시 변수 이름 앞글자, 오브젝트 지역 변수로 선언할 것)."""
    dx, dy, t_, qx, qy = [tag + s for s in ('dx', 'dy', 't', 'qx', 'qy')]
    return [setv(dx, sub(bx, ax)), setv(dy, sub(by, ay)),
            setv(t_, div(add(mul(sub(px, ax), V(dx)), mul(sub(py, ay), V(dy))), add(add(mul(V(dx), V(dx)), mul(V(dy), V(dy))), 0.01))),
            if_(lt(V(t_), 0), setv(t_, 0)), if_(gt(V(t_), 1), setv(t_, 1)),
            setv(qx, sub(add(ax, mul(V(t_), V(dx))), px)), setv(qy, sub(add(ay, mul(V(t_), V(dy))), py)),
            setv(out, add(mul(V(qx), V(qx)), mul(V(qy), V(qy))))]


def seg_locals(o, tag):
    for s in ('dx', 'dy', 't', 'qx', 'qy'):
        o.local(tag + s, 0)


# ================================================================== 31. 연싸움
@game(31)
def g31(P, ctx):
    TL, NO, AY = 40, 3, -110
    m = mg(P, ctx, T, 31, time_limit=TL, status='끊음 0 · 잃음 0', dim=40)
    W, S_, C_ = pfx('k31_')
    vars_(P, *['k31_' + v for v in ('kx', 'ky', 'vx', 'vy', 'tx', 'ty', 'sp', 'on', 'cut', 'lost', 'inv', 'hx', 'hy', 'hint', 'acc')])
    P.list('k31_ox', [0] * NO)
    P.list('k31_oy', [0] * NO)
    P.list('k31_ax', [-200, 200, -130])
    P.list('k31_st', [0] * NO)
    P.list('k31_anc', [-205, -130, 130, 205])
    # 얼레 (줄 시작점)
    for k, x in enumerate([-205, -130, 130, 205]):
        m.S('얼레%d' % k, AD.reel(), x, AY - 6)
    m.S('내얼레', AD.reel(), 0, AY - 6)
    # 줄 그리기 담당 (연보다 뒤에 있어야 하므로 먼저 만든다)
    pen = m.S('줄', AD.dot(), 0, AY)
    draw = [pen_clear(), pen_size(1.6), pen_up()]
    draw += [if_(eq(W('on'), 1), pen_color('#FFFFFF'), xy(0, AY), pen_down(), xy(W('kx'), W('ky')), pen_up())]
    for i in range(1, NO + 1):
        ox, oy, ax = LGET('k31_ox', i), LGET('k31_oy', i), LGET('k31_ax', i)
        draw += [ifelse(eq(LGET('k31_st', i), 1),
                        [pen_color('#FF9AAE'), xy(ax, AY), pen_down(), xy(ox, oy), pen_up()],
                        [if_(eq(LGET('k31_st', i), 2), pen_color('#FF9AAE'), xy(ox, oy), pen_down(),
                             xy(add(ox, 10), sub(oy, 34)), xy(add(ox, 4), sub(oy, 60)), pen_up())])]
    pen.on(on_scene(), pen_clear(), xy(0, AY))
    pen.on(on_msg('게임시작'), until(eq(V('게임중'), 0), *draw), pen_clear())
    # 상대 연 (복제본 3개)
    ob = m.S('상대연', [('a', AD.ray_kite((228, 58, 80), 'red')), ('b', AD.ray_kite((150, 80, 230), 'violet')),
                       ('c', AD.ray_kite((240, 130, 40), 'orange'))], 0, -300, visible=False)
    for v in ('ki', 'ox', 'oy', 'ovx', 'ovy', 'otx', 'oty', 'ocnt', 'ost', 'oax', 'of', 'od', '복제'):
        ob.local(v, 0)
    seg_locals(ob, 'z')
    elapsed = sub(TL, V('남은시간'))
    pick = [setv('ocnt', rnd(60, 120)),
            ifelse(and_(eq(W('on'), 1), le(rnd(1, 100), add(28, mul(elapsed, 1.3)))),
                   [setv('of', div(rnd(40, 80), 100)),
                    setv('otx', mul(W('kx'), V('of'))), setv('oty', add(AY, mul(V('of'), sub(W('ky'), AY)))),
                    setv('otx', add(V('otx'), mul(sub(V('otx'), V('ox')), 0.7))),
                    setv('oty', add(V('oty'), mul(sub(V('oty'), V('oy')), 0.7)))],
                   [setv('otx', rnd(-215, 215)), setv('oty', rnd(10, 88))]),
            *clamp('otx', -222, 222), *clamp('oty', -30, 92)]
    spawn = [setv('ost', 1), lst_set('k31_st', V('ki'), 1),
             setv('oax', LGET('k31_anc', rnd(1, 4))),
             if_(eq(V('ki'), 1), setv('oax', LGET('k31_anc', rnd(1, 2)))),
             if_(eq(V('ki'), 2), setv('oax', LGET('k31_anc', rnd(3, 4)))),
             lst_set('k31_ax', V('ki'), V('oax')),
             setv('ox', V('oax')), setv('oy', -70), setv('ovx', 0), setv('ovy', 0),
             setv('otx', mul(V('oax'), 0.7)), setv('oty', rnd(30, 85)), setv('ocnt', rnd(70, 110)),
             fx('transparency', 0), rot(0), xy(V('ox'), V('oy')), show()]
    fly = [chg('ocnt', -1), if_(le(V('ocnt'), 0), *pick),
           setv('ovx', add(mul(V('ovx'), 0.9), mul(sub(V('otx'), V('ox')), W('acc')))),
           setv('ovy', add(mul(V('ovy'), 0.9), mul(sub(V('oty'), V('oy')), W('acc')))),
           chg('ox', V('ovx')), chg('oy', V('ovy')), *clamp('ox', -226, 226), *clamp('oy', -60, 96),
           xy(V('ox'), V('oy')), rot(mul(V('ovx'), 7)),
           lst_set('k31_ox', V('ki'), V('ox')), lst_set('k31_oy', V('ki'), V('oy')),
           # (가) 내 연이 상대 줄을 스침
           if_(eq(W('on'), 1),
               *seg_d2(W('kx'), W('ky'), V('oax'), AY, V('ox'), V('oy'), 'od', 'z'),
               if_(lt(V('od'), 100),
                   ifelse(gt(W('sp'), 1.4),
                          [setv('ost', 2), lst_set('k31_st', V('ki'), 2), setv('ocnt', 0), C_('cut', 1),
                           S_('hx', W('kx')), S_('hy', W('ky')), cast('k31_싹둑')],
                          [if_(le(W('hint'), 0), S_('hint', 90), S_('hx', W('kx')), S_('hy', W('ky')), cast('k31_느림'))]))),
           # (나) 상대 연이 내 줄에 닿음
           if_(and_(and_(eq(W('on'), 1), eq(V('ost'), 1)), le(W('inv'), 0)),
               *seg_d2(V('ox'), V('oy'), 0, AY, W('kx'), W('ky'), 'od', 'z'),
               if_(lt(V('od'), 110), S_('on', 0), C_('lost', 1), S_('hx', W('kx')), S_('hy', W('ky')), cast('k31_잃음')))]
    fall = [chg('oy', -1.6), chg('ox', mul(V('ovx'), 0.5)), rot_by(11), fx_add('transparency', 1.2), xy(V('ox'), V('oy')),
            lst_set('k31_ox', V('ki'), V('ox')), lst_set('k31_oy', V('ki'), V('oy')),
            chg('ocnt', 1),
            if_(gt(V('ocnt'), 70), hide(), setv('ost', 0), lst_set('k31_st', V('ki'), 0), wait(div(rnd(5, 15), 10)),
                if_(eq(V('게임중'), 1), *spawn))]
    ob.on(on_msg('게임시작'), setv('ki', 0), rep(NO, chg('ki', 1), clone_self()))
    ob.on(on_clone(), setv('복제', 1), shape(V('ki')), wait(div(V('ki'), 3)), *spawn,
          until(eq(V('게임중'), 0), ifelse(eq(V('ost'), 1), fly, [if_(eq(V('ost'), 2), *fall)])),
          del_clone())
    # 내 연
    me = m.S('내연', AD.shield_kite(), 0, -10)
    my_fly = [S_('tx', mouse_x()), S_('ty', mouse_y()), *clamp('k31_tx', -224, 224), *clamp('k31_ty', -50, 94),
              S_('vx', add(mul(W('vx'), 0.86), mul(sub(W('tx'), W('kx')), 0.012))),
              S_('vy', add(mul(W('vy'), 0.86), mul(sub(W('ty'), W('ky')), 0.012))),
              C_('kx', W('vx')), C_('ky', W('vy')),
              S_('sp', fn('root', add(mul(W('vx'), W('vx')), mul(W('vy'), W('vy'))))),
              xy(W('kx'), W('ky')), rot(mul(W('vx'), 4)),
              if_(gt(W('inv'), 0), C_('inv', -1), if_(eq(W('inv'), 0), fx('transparency', 0))),
              if_(gt(W('hint'), 0), C_('hint', -1))]
    my_fall = [C_('ky', -2.2), C_('kx', mul(W('vx'), 0.3)), xy(W('kx'), W('ky')), rot_by(-13), fx_add('transparency', 2)]
    me.on(on_scene(), xy(0, -10), rot(0), fx('transparency', 0))
    me.on(on_msg('게임시작'),
          until(eq(V('게임중'), 0),
                ifelse(eq(W('on'), 1), my_fly,
                       [*my_fall, if_(lt(W('ky'), -125), hide(), wait(0.9),
                                      S_('kx', 0), S_('ky', -40), S_('vx', 0), S_('vy', 2), S_('inv', 70),
                                      fx('transparency', 45), rot(0), show(), S_('on', 1))])))
    m.S('나', ctx['PORT']['me'], 0, AY - 2, scale=0.75)
    # 효과
    pop(m, '싹둑', [('a', K.big_text('싹둑!', 22, 'royal'))], 0, 0, 'k31_싹둑', 0.35, follow=(W('hx'), add(W('hy'), 22)))
    pop(m, '느림', [('a', K.big_text('더 빠르게 스쳐요!', 14, 'white'))], 0, 0, 'k31_느림', 0.4,
        follow=(W('hx'), add(W('hy'), 20)))
    pop(m, '잃음', [('a', K.big_text('내 줄이 끊겼다!', 20, 'red'))], 0, 30, 'k31_잃음', 0.6)
    sp = m.S('불꽃', AD.spark('cut'), 0, 0, visible=False)
    sp.on(on_msg('k31_싹둑'), xy(W('hx'), W('hy')), sp.pct(50), fx('transparency', 0), show(),
          rep(8, sp.grow_pct(12), fx_add('transparency', 12), wait(0.02)), hide())
    hud = [setv('미니표시', join('끊음 ', W('cut'), ' · 잃음 ', W('lost')))]
    mgr = hidden(m, '연담당')
    mgr.on(on_msg('k31_싹둑'), *hud)
    mgr.on(on_msg('k31_잃음'), *hud)
    mgr.on(on_msg('게임시작'), until(eq(V('게임중'), 0), S_('acc', add(0.0011, mul(elapsed, 0.00003))), wait(0.5)))
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(sub(mul(W('cut'), 11), mul(W('lost'), 6)), 8)))
    m.on_start(S_('kx', 0), S_('ky', -10), S_('vx', 0), S_('vy', 0), S_('on', 1), S_('cut', 0), S_('lost', 0), S_('inv', 0),
               S_('hint', 0), S_('sp', 0), S_('acc', 0.0011),
               *[lst_set('k31_st', i, 0) for i in range(1, NO + 1)])
    m.snd('k31_싹둑', play('pop'))
    m.snd('k31_잃음', play('bad'))
    m.snd('k31_느림', play('tick'))
    m.finish('마우스로 내 방패연을 몰아 상대 연줄을 빠르게 스치면 싹둑!\n상대 연이 내 줄(흰 줄)에 닿으면 내 연을 잃어요.',
             '조작: 마우스 이동 (연이 살짝 늦게 따라와요)  ·  40초  ·  상대 연 가까이는 위험!')
    return True
