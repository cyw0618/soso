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


def maxv(a, b):
    return div(add(add(a, b), abs_(sub(a, b))), 2)


def minv(a, b):
    return div(sub(add(a, b), abs_(sub(a, b))), 2)


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


# ================================================================== 32. 근대 학교 방탈출
@game(32)
def g32(P, ctx):
    import mg_art as A
    TL = 170
    m = mg(P, ctx, T, 32, time_limit=TL, status='힌트 0 · 실수 0', dim=0)
    sc = m.sc
    W, S_, C_ = pfx('k32_')
    vars_(P, *['k32_' + v for v in ('a', 'b', 'c', 'ans', 'd1', 'd2', 'd3', 'box', 'has', 'sel', 'lit', 'lamp', 'ok', 'seen', 'day',
                                     'per', 'subj', 't1', 't2', 'win', 'hint', 'miss', 'esc', 'spin')])
    P.var('k32_글', '')
    SUBJ = ['국어', '산수', '지리', '역사', '창가', '체조', '습자', '도화', '과학']
    SYL = [ch for s_ in SUBJ for ch in s_]
    DAYS = '월화수목금토'
    P.list('k32_subj', SUBJ)
    P.list('k32_syl', SYL)
    P.list('k32_tt', [1] * 24)
    LX = [-50, -15, 18]
    P.list('k32_lx', LX)
    can = and_(eq(V('게임중'), 1), eq(W('win'), 0))
    say = lambda txt: [S_('글', txt), cast('k32_말')]
    refresh = cast('k32_방갱신')

    def room(o):
        o.on(on_msg('k32_방갱신'), ifelse(eq(W('lit'), 1), [fx('brightness', 0)], [fx('brightness', -42)]))
        return o
    room(m.S('벽', AD.room_wall(), 0, 55))
    room(m.S('바닥', AD.room_floor(), 0, -80))
    tt = room(m.S('시간표', AD.timetable_small(), -208, 52))
    board = room(m.S('칠판', AD.blackboard(), -100, 55))
    chalk = m.T('칠판글', '', -100, 60, 15, '#F4F1E0', F_NUM, False, 0, w=150, h=24)
    chalk.on(on_msg('k32_방갱신'), write(join(W('a'), ' × ', W('b'), ' + ', W('c'), ' = ?')))
    m.T('칠판글2', '산수 숙제: 주판으로 셈하시오', -100, 36, 8, '#C9D8C8', F_BODY, True, 0, w=150, h=14)
    mp = room(m.S('세계지도', AD.world_map(), 40, 76))
    globe = room(m.S('지구본', AD.globe_cab(), 122, -12))
    hangs = []
    for k, (x, y) in enumerate(((30, 98), (50, 95)), 1):
        h_ = m.S('나무조각%d' % k, AD.hanging(k), x, y)
        h_.on(on_scene(), forever(rep(20, rot_by(0.3), wait(0.05)), rep(20, rot_by(-0.3), wait(0.05))))
        hangs.append(h_)
    sh1 = m.S('그림자1', [('d%d' % (k + 1), AD.shadow_glyph(DAYS[k], 'd%d' % k)) for k in range(6)], 22, 28, visible=False)
    sh2 = m.S('그림자2', [('p%d' % (k + 1), AD.shadow_glyph(str(k + 1), 'p%d' % k)) for k in range(4)], 58, 28, visible=False)
    dlt = sub(W('lamp'), W('ok'))
    for o, x, a, sz, var in ((sh1, 22, 35, 125, 'day'), (sh2, 58, -50, 140, 'per')):
        o.on(on_msg('k32_방갱신'), shape(join('d' if var == 'day' else 'p', W(var))),
             ifelse(eq(W('lit'), 1),
                    [show(), ifelse(eq(dlt, 0), [xy(x, 28), rot(0), o.pct(100), fx('transparency', 10)],
                                    [xy(add(40, mul(dlt, 9 if var == 'day' else -7)), add(28, mul(dlt, 3))), rot(mul(dlt, a)),
                                     o.pct(sz), fx('transparency', 35)])],
                    [hide()]))
    dr = room(m.S('문', [('c', AD.door(0)), ('o', AD.door(1))], 200, 2))
    dr.on(on_msg('k32_방갱신'), ifelse(eq(W('esc'), 1), [shape('o')], [shape('c')]))
    room(m.S('교탁', AD.desk(), -60, -46))
    box = room(m.S('상자', [('c', AD.wood_box(0)), ('o', AD.wood_box(1))], -88, -12))
    box.on(on_msg('k32_방갱신'), ifelse(eq(W('box'), 1), [shape('o')], [shape('c')]))
    ab = room(m.S('주판', AD.abacus_small(), -118, -15))
    lampo = m.S('등잔', [('off', AD.lamp(0)), ('on', AD.lamp(1))], LX[1], 2)
    room(lampo)
    lampo.on(on_msg('k32_방갱신'), lx(LGET('k32_lx', W('lamp'))), ifelse(eq(W('lit'), 1), [shape('on')], [shape('off')]))
    # ---------------- 아래: 말 상자, 힌트, 가방
    panel(P, sc, '말판', -82, -116, 296, 30, 'glass')
    msg = m.T('말글', '', -82, -116, 9, C_WHITE, F_BODY, True, 0, w=284, h=26)
    msg.on(on_msg('k32_말'), write(W('글')))
    m.T('가방글', '가방', 160, -116, 9, C_DIM, F_BODY, True, 0, w=30, h=14)
    bag = m.S('가방칸', [('e', AD.slot_empty()), ('m', AD.match_item(0)), ('s', AD.match_item(1))], 190, -116)
    bag.on(on_msg('k32_방갱신'), ifelse(eq(W('has'), 0), [shape('e')], [ifelse(eq(W('sel'), 1), [shape('s')], [shape('m')])]))
    bag.on(on_click(), if_(and_(can, eq(W('has'), 1)), S_('sel', sub(1, W('sel'))), refresh, cast('k32_딸깍'),
                           if_(eq(W('sel'), 1), *say('성냥을 들었다. 불을 붙일 곳을 눌러 보자.'))))
    chain = say('힌트: 그림자는 요일과 교시! 시간표에서 그 과목을 찾아 문의 활판에 찍어요.')
    for c_, t_ in reversed([(eq(W('box'), 0), '힌트: 칠판 산수의 답을 교탁 위 주판에 놓아요. (윗알 5, 아랫알 1)'),
                            (eq(W('lit'), 0), '힌트: 가방의 성냥을 고른 뒤 등잔을 눌러 불을 붙여요.'),
                            (eq(W('seen'), 0), '힌트: 등잔을 누르면 자리가 바뀌어요. 벽 그림자가 똑바로 보일 때까지!')]):
        chain = [ifelse(c_, say(t_), chain)]
    button(P, sc, '힌트버튼', '힌트 -8', 102, -116, 60, 24, 'purple', actions=[if_(can, C_('hint', 1), *chain)])
    # ---------------- 방 클릭
    open_ab = [S_('win', 1), cast('k32_주판창'), *say('주판 자물쇠! 칠판 문제의 답을 놓고 "확인".')]
    board.on(on_click(), if_(can, *say(join('칠판: "', W('a'), ' × ', W('b'), ' + ', W('c'), ' = ?" 주판으로 셈하라고 적혀 있다.'))))
    chalk.on(on_click(), if_(can, *say(join('칠판: "', W('a'), ' × ', W('b'), ' + ', W('c'), ' = ?" 주판으로 셈하라고 적혀 있다.'))))
    for o in (ab, box):
        o.on(on_click(), if_(can, ifelse(eq(W('box'), 0), open_ab, say('열린 상자. 이제 비어 있다.'))))
    tt.on(on_click(), if_(can, ifelse(eq(W('lit'), 0), say('너무 어두워서 시간표 글씨가 안 보인다...'),
                                      [S_('win', 2), cast('k32_표창'), *say('1920년대 시간표. 요일과 교시마다 과목이 있다.')])))
    mp.on(on_click(), if_(can, *say('세계지도. 경성에서 상하이, 런던까지 붉은 선이 이어져 있다.')))
    globe.on(on_click(), if_(can, *say('지구본을 돌려 봤다. 빙글빙글~ 꿈이 커지는 느낌!'), cast('k32_딸깍')))
    for h_ in hangs:
        h_.on(on_click(), if_(can, *say('천장에 나무 조각 두 개가 매달려 있다. 빛을 비추면 무엇이 보일까?')))
    dr.on(on_click(), if_(can, S_('t1', 0), S_('t2', 0), S_('win', 3), cast('k32_활판창'),
                          *say('문 자물쇠는 활판이다. 활자 두 개를 끼워 찍어야 열린다.')))
    lampo.on(on_click(), if_(can, ifelse(eq(W('lit'), 0),
                                         [ifelse(eq(W('sel'), 1),
                                                 [S_('lit', 1), S_('sel', 0), S_('has', 0), cast('k32_불'),
                                                  if_(eq(W('lamp'), W('ok')), S_('seen', 1)), refresh,
                                                  *say('등잔불이 켜졌다! 벽에 나무 조각 그림자가 비친다.')],
                                                 say('등잔이다. 불을 붙일 것이 있으면 좋겠다.'))],
                                         [S_('lamp', add(mod(W('lamp'), 3), 1)), if_(eq(W('lamp'), W('ok')), S_('seen', 1)), refresh,
                                          cast('k32_딸깍'), *say('등잔을 옆으로 옮겼다. 그림자가 바뀐다!')])))
    # ---------------- 창: 공통
    def window(objs, open_msg, close_msg):
        for o in objs:
            o.on(on_scene(), hide())
            o.on(on_msg(open_msg), show())
            o.on(on_msg(close_msg), hide())
    close = lambda w_, msg_: [if_(eq(W('win'), w_), S_('win', 0), cast(msg_))]
    # ---------------- 주판 창
    ow = [m.S('주판어둡게', A.plain_rect(480, 270, (2, 3, 12, 170), 'dim_kp'), 0, 0),
          panel(P, sc, '주판판', 0, 8, 262, 176, 'glass', header='royal'),
          m.T('주판제목', '교탁 상자의 주판 자물쇠', 0, 84, 11, C_WHITE, F_NUM, False, 0, w=220, h=16),
          m.S('주판틀', AD.abacus_frame(), 0, 20)]
    for i, x in enumerate((-60, 0, 60), 1):
        rod = m.S('주판알%d' % i, [('b%d' % dg, AD.abacus_rod(dg)) for dg in range(10)], x, 20)
        rod.on(on_msg('k32_주판'), shape(join('b', W('d%d' % i))))
        dv = 'k32_d%d' % i
        rod.on(on_click(), if_(eq(W('win'), 1),
                               ifelse(gt(mouse_y(), add(obj_y(), 19)),
                                      [ifelse(ge(V(dv), 5), [chg(dv, -5)], [chg(dv, 5)])],
                                      [ifelse(eq(mod(V(dv), 5), 4), [chg(dv, -4)], [chg(dv, 1)])]),
                               cast('k32_주판'), cast('k32_딸깍')))
        lab = m.T('주판수%d' % i, '0', x, -44, 14, C_ACC, F_NUM, False, 0, w=30, h=18)
        lab.on(on_msg('k32_주판'), write(W('d%d' % i)))
        ow += [rod, lab]
    ow.append(m.T('주판설명', '윗알 하나 = 5 · 아랫알 하나 = 1  (숫자키로도 놓을 수 있어요)', 0, -57, 8, C_DIM, F_BODY, True, 0, w=250, h=12))
    chk = [if_(eq(W('win'), 1),
               ifelse(eq(add(add(mul(W('d1'), 100), mul(W('d2'), 10)), W('d3')), W('ans')),
                      [S_('box', 1), S_('has', 1), S_('win', 0), cast('k32_주판닫기'), refresh, cast('k32_찾음'),
                       *say('딸깍! 상자가 열렸다. 성냥을 얻었다! (가방)')],
                      [C_('miss', 1), cast('k32_삐빅'), *say('덜컥... 상자가 열리지 않는다. 다시 셈해 보자.')]))]
    ow.append(button(P, sc, '주판확인', '확인', -44, -72, 70, 22, 'royal', actions=chk))
    ow.append(button(P, sc, '주판닫기', '닫기', 44, -72, 70, 22, 'gray', actions=close(1, 'k32_주판닫기')))
    window(ow, 'k32_주판창', 'k32_주판닫기')
    kmgr = hidden(m, '주판키')
    for d in range(10):
        kmgr.on(on_key(48 + d), if_(eq(W('win'), 1), S_('d1', W('d2')), S_('d2', W('d3')), S_('d3', d), cast('k32_주판'), cast('k32_딸깍')))
    kmgr.on(on_msg('k32_주판창'), cast('k32_주판'))
    # ---------------- 시간표 창
    tw = [m.S('표어둡게', A.plain_rect(480, 270, (2, 3, 12, 170), 'dim_kp'), 0, 0),
          panel(P, sc, '표판', 0, 4, 340, 184, 'glass', header='royal'),
          m.T('표제목', '시간표 (時間表)', 0, 84, 11, C_WHITE, F_NUM, False, 0, w=220, h=16)]
    for c in range(6):
        tw.append(m.T('표요일%d' % c, DAYS[c], -95 + c * 44, 58, 12, C_ACC, F_NUM, False, 0, w=36, h=16))
    for r in range(4):
        tw.append(m.T('표교시%d' % r, '%d교시' % (r + 1), -142, 32 - r * 26, 10, C_ACC, F_NUM, False, 0, w=44, h=14))
        for c in range(6):
            cell = m.T('표칸%d_%d' % (r, c), '', -95 + c * 44, 32 - r * 26, 11, C_WHITE, F_BODY, True, 0, w=42, h=16)
            cell.on(on_msg('k32_표창'), write(LGET('k32_subj', LGET('k32_tt', r * 6 + c + 1))))
            tw.append(cell)
    tw.append(button(P, sc, '표닫기', '닫기', 0, -74, 70, 22, 'gray', actions=close(2, 'k32_표닫기')))
    window(tw, 'k32_표창', 'k32_표닫기')
    # ---------------- 활판 창 (문)
    rng = random.Random(32)
    order = list(range(18))
    rng.shuffle(order)
    pw = [m.S('활판어둡게', A.plain_rect(480, 270, (2, 3, 12, 170), 'dim_kp'), 0, 0),
          panel(P, sc, '활판판', 0, 0, 362, 196, 'glass', header='purple'),
          m.T('활판제목', '문 자물쇠 · 활판 인쇄', 0, 84, 11, C_WHITE, F_NUM, False, 0, w=220, h=16),
          m.T('활판설명', '그림자가 가리키는 요일·교시의 과목 이름을 찍으세요.\n활자는 거울에 비친 것처럼 뒤집혀 있어요!', 0, 62, 9, C_DIM, F_BODY, True, 0,
              w=330, h=28),
          m.T('활판글', '활판', -62, 34, 10, C_ACC, F_NUM, False, 0, w=40, h=14)]
    tpics = [('e', AD.slot_empty())] + [('t%d' % (j + 1), AD.type_block(SYL[j], 'm%d' % j)) for j in range(18)]
    for k in (1, 2):
        sl = m.S('활판칸%d' % k, tpics, -36 + 36 * k, 34)
        tv = W('t%d' % k)
        sl.on(on_msg('k32_활자'), ifelse(eq(tv, 0), [shape('e')], [shape(join('t', tv))]))
        pw.append(sl)
    for j in range(18):
        g = order.index(j)
        c, r = g % 6, g // 6
        tb = m.S('활자%d' % (j + 1), AD.type_block(SYL[j], 'm%d' % j), -105 + 42 * c, 2 - 34 * r)
        tb.on(on_click(), if_(eq(W('win'), 3),
                              ifelse(eq(W('t1'), 0), [S_('t1', j + 1)], [if_(eq(W('t2'), 0), S_('t2', j + 1))]),
                              cast('k32_활자'), cast('k32_딸깍'), tb.pct(88), wait(0.06), tb.pct(100)))
        pw.append(tb)
    res = m.T('찍힌글', '', 150, -66, 13, C_WHITE, F_NUM, False, 0, w=60, h=40, bg=C_BOX)
    res.on(on_msg('k32_활판창'), write('찍은 글\n?'))
    res.on(on_msg('k32_찍음'), write(join('찍은 글\n', LGET('k32_syl', W('t1')), LGET('k32_syl', W('t2')))))
    pw.append(res)
    good = and_(eq(W('t1'), sub(mul(W('subj'), 2), 1)), eq(W('t2'), mul(W('subj'), 2)))
    stamp = [if_(and_(eq(W('win'), 3), gt(W('t2'), 0)), cast('k32_찍음'), cast('k32_철컥'), wait(0.5),
                 ifelse(good,
                        [S_('esc', 1), S_('win', 0), cast('k32_활판닫기'), refresh, cast('k32_탈출'), *say('철컥! 문이 열렸다. 탈출 성공!')],
                        [C_('miss', 1), cast('k32_삐빅'), S_('t1', 0), S_('t2', 0), cast('k32_활자'),
                         *say('문이 꿈쩍도 안 한다. 다른 과목인가?')]))]
    pw.append(button(P, sc, '활판찍기', '찍기', 150, 34, 56, 24, 'royal', actions=stamp))
    pw.append(button(P, sc, '활판지움', '지움', 150, 4, 56, 24, 'steel',
                     actions=[if_(eq(W('win'), 3), S_('t1', 0), S_('t2', 0), cast('k32_활자'))]))
    pw.append(button(P, sc, '활판닫기', '닫기', 150, -26, 56, 24, 'gray', actions=close(3, 'k32_활판닫기')))
    window(pw, 'k32_활판창', 'k32_활판닫기')
    hidden(m, '활판담당').on(on_msg('k32_활판창'), cast('k32_활자'))
    # ---------------- 탈출·점수
    flash = m.S('탈출빛', A.plain_rect(480, 270, (255, 246, 214, 255), 'k32_white'), 0, 0, visible=False)
    flash.on(on_msg('k32_탈출'), wait(0.4), fx('transparency', 100), show(), rep(10, fx_add('transparency', -8), wait(0.03)))
    G.big_pop(P, sc, '탈출글', K.big_text('탈출 성공!', 40, 'royal'), 0, 20, 'k32_탈출', hold=1.2)
    mgr = hidden(m, '탈출담당')
    mgr.on(on_msg('k32_탈출'), setv('_mk', sub(sub(TL, V('남은시간')), 75)), if_(lt(V('_mk'), 0), setv('_mk', 0)),
           setv('합계', sub(sub(sub(100, mul(W('hint'), 8)), mul(W('miss'), 2)), mul(V('_mk'), 0.3))),
           if_(lt(V('합계'), 40), setv('합계', 40)), wait(1.6), *m.end_blocks(V('합계')))
    part = sub(add(add(mul(W('box'), 15), mul(W('lit'), 10)), mul(W('seen'), 10)), mul(W('hint'), 4))
    mgr.on(on_msg('시간끝'), S_('win', 0), cast('k32_주판닫기'), cast('k32_표닫기'), cast('k32_활판닫기'),
           *say('시간이 다 됐다... 교실에 갇혀 버렸다!'), wait(1.0), *m.end_blocks(part))
    mgr.on(on_msg('게임시작'), until(eq(V('게임중'), 0), setv('미니표시', join('힌트 ', W('hint'), ' · 실수 ', W('miss'))), wait(0.3)))
    m.on_start(S_('win', 0), S_('hint', 0), S_('miss', 0), S_('box', 0), S_('has', 0), S_('sel', 0), S_('lit', 0), S_('seen', 0),
               S_('esc', 0), S_('t1', 0), S_('t2', 0), S_('d1', 0), S_('d2', 0), S_('d3', 0), S_('lamp', 2),
               S_('a', rnd(12, 29)), S_('b', rnd(3, 9)), S_('c', rnd(11, 99)),
               S_('ans', add(mul(W('a'), W('b')), W('c'))),
               S_('ok', rnd(1, 3)), until(ne(W('ok'), 2), S_('ok', rnd(1, 3))),
               *[lst_set('k32_tt', k, rnd(1, 9)) for k in range(1, 25)],
               S_('day', rnd(1, 6)), S_('per', rnd(1, 4)),
               S_('subj', LGET('k32_tt', add(mul(sub(W('per'), 1), 6), W('day')))),
               S_('글', '1920년대 교실에 갇혔다! 칠판, 교탁, 등잔... 단서를 찾자.'), refresh, cast('k32_말'))
    m.snd('k32_딸깍', play('tick'))
    m.snd('k32_찾음', play('good'))
    m.snd('k32_삐빅', play('bad'))
    m.snd('k32_철컥', play('stamp'))
    m.snd('k32_불', play('pop'))
    m.snd('k32_탈출', play('fanfare'))
    m.finish('100년 된 군산의 근대 학교 교실에 갇혔다!\n주판·등잔불·시간표·활자로 문을 여세요. 정답은 매번 달라요.',
             '조작: 마우스 클릭 (주판은 숫자키도)  ·  가방 물건을 고른 뒤 쓸 곳 클릭  ·  힌트 -8점')
    return True


# ================================================================== 33. 강 건너기 퍼즐
@game(33)
def g33(P, ctx):
    TL, N = 120, 6
    m = mg(P, ctx, T, 33, time_limit=TL, status='퍼즐 1/2 · 0번', dim=40)
    sc = m.sc
    W, S_, C_ = pfx('k33_')
    vars_(P, *['k33_' + v for v in ('pz', 'side', 'bx', 's1', 's2', 'mv', 'mv1', 'mv2', 'ok1', 'ok2', 'bad', 'busy', 'osd', 'n',
                                     'sa', 'sb', 'oa', 'ob', 'why', 'np')])
    P.list('k33_loc', [1] * N)
    P.list('k33_old', [1] * N)
    P.list('k33_seat', [0] * N)
    BY, BX = -46, 64
    LXs = [-205, -165, -125, -205, -165, -125]
    LYs = [8, 8, 8, -46, -46, -46]
    P.list('k33_lx', LXs)
    P.list('k33_ly', LYs)
    m.S('왼둑', AD.bank(0), -175, -28)
    m.S('오른둑', AD.bank(1), 175, -28)
    m.S('강', AD.river(), 0, -28)
    rule = m.T('규칙글', '', 0, 74, 10, C_WHITE, F_BODY, True, 0, w=430, h=30, bg=C_BOX)
    rule.on(on_msg('k33_퍼즐'), ifelse(eq(W('pz'), 1),
                                     [write('퍼즐 1: 사공만 배를 저어요. 사공이 없으면 호랑이는 염소를,\n염소는 배추를 먹어요! 모두 오른쪽 둑으로 (최소 7번)')],
                                     [write('퍼즐 2: 배에는 둘까지, 아무나 저어요. 어느 둑이든 반대파가\n지지자보다 많으면 싸움이 나요! 모두 오른쪽으로 (최소 11번)')]))
    bt = m.S('배', AD.boat(), -BX, BY)
    bt.on(on_msg('k33_갱신'), xy(W('bx'), BY))
    # 사람·동물 6 칸: 퍼즐 1 은 1~4 (사공·호랑이·염소·배추), 퍼즐 2 는 1~3 지지자, 4~6 반대파
    sup = AD.person((60, 110, 230), sign=((40, 90, 220), '♥'), tag='sup')
    opp = AD.person((200, 50, 60), sign=((200, 40, 50), '✕'), tag='opp')
    boatman = AD.person((90, 70, 50), hat=(200, 170, 90), tag='boatman')
    p1 = [boatman, AD.tiger(), AD.goat(), AD.cabbage(), AD.blank(), AD.blank()]
    loc = lambda i: LGET('k33_loc', i)
    for i in range(1, N + 1):
        o = m.S('인물%d' % i, [('a', p1[i - 1]), ('b', sup if i <= 3 else opp)], LXs[i - 1], LYs[i - 1])
        o.on(on_msg('k33_갱신'),
             ifelse(and_(eq(W('pz'), 1), gt(i, 4)), [hide()],
                    [show(), shape(W('pz')),
                     ifelse(eq(loc(i), 3), [xy(add(W('bx'), sub(mul(LGET('k33_seat', i), 26), 39)), BY + 18)],
                            [ifelse(eq(loc(i), 1), [xy(LXs[i - 1], LYs[i - 1])], [xy(-LXs[i - 1], LYs[i - 1])])])]))
        o.on(on_click(), if_(and_(eq(V('게임중'), 1), eq(W('busy'), 0)),
                             ifelse(eq(loc(i), 3),
                                    [lst_set('k33_loc', i, W('side')), if_(eq(W('s1'), i), S_('s1', 0)), if_(eq(W('s2'), i), S_('s2', 0)),
                                     cast('k33_갱신'), cast('k33_딸깍')],
                                    [ifelse(eq(loc(i), W('side')),
                                            [ifelse(eq(W('s1'), 0), [S_('s1', i), lst_set('k33_seat', i, 1), lst_set('k33_loc', i, 3)],
                                                    [ifelse(eq(W('s2'), 0), [S_('s2', i), lst_set('k33_seat', i, 2), lst_set('k33_loc', i, 3)],
                                                            [S_('why', 1), cast('k33_안내')])]),
                                             cast('k33_갱신'), cast('k33_딸깍')],
                                            [S_('why', 2), cast('k33_안내')])])))
    # 안내 말
    note = m.T('안내글', '', 0, -112, 10, C_ACC, F_BODY, True, 0, w=300, h=16)
    for k, txt in enumerate(['배에는 둘까지만 탈 수 있어요!', '배가 건너편에 있어요.', '배에 아무도 없어요.',
                             '사공이 있어야 배를 저을 수 있어요.', '호랑이가 염소를 잡아먹었어요! 되돌려요.',
                             '염소가 배추를 먹어 버렸어요! 되돌려요.', '반대파가 더 많아서 싸움이 났어요! 되돌려요.',
                             '성공! 모두 무사히 건넜어요!'], 1):
        note.on(on_msg('k33_안내'), if_(eq(W('why'), k), write(txt)))
    note.on(on_msg('k33_퍼즐'), write('인물을 눌러 배에 태우고 내리기 · 배나 "건너기!"를 눌러 출발'))
    # 건너기
    def count(var, lo, hi, b):
        return [S_(var, 0)] + [if_(eq(loc(j), b), C_(var, 1)) for j in range(lo, hi + 1)]
    check1 = [S_('osd', sub(3, loc(1))),
              if_(and_(eq(loc(2), W('osd')), eq(loc(3), W('osd'))), S_('bad', 5)),
              if_(and_(eq(W('bad'), 0), and_(eq(loc(3), W('osd')), eq(loc(4), W('osd')))), S_('bad', 6))]
    check2 = [*count('sa', 1, 3, 1), *count('oa', 4, 6, 1), *count('sb', 1, 3, 2), *count('ob', 4, 6, 2),
              if_(or_(and_(gt(W('sa'), 0), gt(W('oa'), W('sa'))), and_(gt(W('sb'), 0), gt(W('ob'), W('sb')))), S_('bad', 7))]
    move_boat = lambda tgt: [rep(16, C_('bx', div(sub(tgt, W('bx')), 4)), cast('k33_갱신'), wait(0.02)), S_('bx', tgt), cast('k33_갱신')]
    go_ = [if_(and_(eq(V('게임중'), 1), eq(W('busy'), 0)),
               ifelse(and_(eq(W('s1'), 0), eq(W('s2'), 0)), [S_('why', 3), cast('k33_안내')],
                      [ifelse(and_(eq(W('pz'), 1), ne(loc(1), 3)), [S_('why', 4), cast('k33_안내')],
                              [S_('busy', 1), cast('k33_출발')])]))]
    bt.on(on_click(), *go_)
    button(P, sc, '건너기', '건너기!', 0, -88, 90, 24, 'royal', actions=go_)
    reset = [if_(and_(eq(V('게임중'), 1), eq(W('busy'), 0)), cast('k33_처음'))]
    button(P, sc, '처음부터', '처음부터', 190, -112, 76, 20, 'steel', actions=reset)
    mgr = hidden(m, '강담당')
    sync = lambda: [setv('미니표시', join('퍼즐 ', W('pz'), '/2 · ', W('mv'), '번'))]
    restart = [S_('side', 1), S_('bx', -BX), S_('s1', 0), S_('s2', 0), S_('mv', 0),
               *[lst_set('k33_loc', j, 1) for j in range(1, N + 1)], *[lst_set('k33_seat', j, 0) for j in range(1, N + 1)],
               cast('k33_갱신'), *sync()]
    mgr.on(on_msg('k33_처음'), *restart, cast('k33_퍼즐'))
    mgr.on(on_msg('k33_출발'),
           *[lst_set('k33_old', j, loc(j)) for j in range(1, N + 1)],
           cast('k33_노'), *move_boat(mul(W('side'), -BX)), S_('side', sub(3, W('side'))), S_('bx', mul(sub(mul(W('side'), 2), 3), BX)),
           *[if_(eq(loc(j), 3), lst_set('k33_loc', j, W('side'))) for j in range(1, N + 1)],
           S_('s1', 0), S_('s2', 0), C_('mv', 1), cast('k33_갱신'), *sync(),
           S_('bad', 0), ifelse(eq(W('pz'), 1), check1, check2),
           ifelse(gt(W('bad'), 0),
                  [S_('why', W('bad')), cast('k33_안내'), cast('k33_싸움'), C_('n', 1), wait(1.3),
                   *[lst_set('k33_loc', j, LGET('k33_old', j)) for j in range(1, N + 1)],
                   *move_boat(mul(W('side'), -BX)), S_('side', sub(3, W('side'))), S_('bx', mul(sub(mul(W('side'), 2), 3), BX)),
                   C_('mv', -1),
                   *[if_(eq(loc(j), 3), lst_set('k33_loc', j, W('side'))) for j in range(1, N + 1)],
                   cast('k33_갱신'), *sync()],
                  []),
           *count('np', 1, N, 2),
           ifelse(and_(eq(W('pz'), 1), ge(W('np'), 4)),
                  [S_('ok1', 1), S_('mv1', W('mv')), S_('why', 8), cast('k33_안내'), cast('k33_성공'), wait(1.6), S_('pz', 2), *restart,
                   cast('k33_퍼즐')],
                  [if_(and_(eq(W('pz'), 2), ge(W('np'), 6)),
                       S_('ok2', 1), S_('mv2', W('mv')), S_('why', 8), cast('k33_안내'), cast('k33_성공'), wait(1.6),
                       *m.end_blocks(score33(W)))]),
           S_('busy', 0))
    mgr.on(on_msg('시간끝'), *count('np', 1, N, 2), *m.end_blocks(score33(W, True)))
    pop(m, '싸움', [('a', K.big_text('앗!', 34, 'red'))], 0, 20, 'k33_싸움', 0.6)
    pop(m, '성공', [('a', K.big_text('모두 건넜다!', 30, 'royal'))], 0, 20, 'k33_성공', 0.8)
    m.on_start(S_('pz', 1), S_('ok1', 0), S_('ok2', 0), S_('n', 0), S_('busy', 0), S_('mv1', 0), S_('mv2', 0), *restart, cast('k33_퍼즐'))
    m.snd('k33_딸깍', play('tick'))
    m.snd('k33_노', play('splash'))
    m.snd('k33_싸움', play('bad'))
    m.snd('k33_성공', play('good'))
    m.finish('청계천 나룻배로 모두 오른쪽 둑에 건너 주세요! 배엔 둘까지.\n퍼즐 1 사공·호랑이·염소·배추, 퍼즐 2 지지자·반대파 (2문제)',
             '조작: 인물 클릭 = 타기/내리기  ·  배 또는 "건너기!" 클릭 = 출발  ·  적게 건널수록 높은 점수')
    return True


def score33(W, timeout=False):
    """퍼즐 1: 45점 (7번보다 한 번 더 건널 때마다 -3, 최소 25), 퍼즐 2: 55점 (11번 기준, 최소 30), 싸움 한 번 -3.
    시간이 끝나면 못 푼 퍼즐은 오른쪽에 건넌 수 x 4."""
    p1 = mul(W('ok1'), maxv(25, sub(45, mul(sub(W('mv1'), 7), 3))))
    p2 = mul(W('ok2'), maxv(30, sub(55, mul(sub(W('mv2'), 11), 3))))
    base = add(p1, p2)
    if timeout:
        base = add(base, mul(W('np'), 4))
    return sub(base, mul(W('n'), 3))


# ================================================================== 34. 얼음 컬링
@game(34)
def g34(P, ctx):
    NS, NA, R = 4, 3, 8
    NT = NS + NA
    CY, HX, HR, SX = -12, 150, 40, -200
    m = mg(P, ctx, T, 34, time_limit=100, status='스톤 1/%d' % NS, dim=50)
    sc = m.sc
    W, S_, C_ = pfx('k34_')
    vars_(P, *['k34_' + v for v in ('shot', 'ang', 'pw', 'pdir', 'phase', 'curl', 'sw', 'swt', 'mov', 'pts', 'best', 'ai', 'out',
                                     'k', 'd')])
    for nm in ('x', 'y', 'vx', 'vy', 'in'):
        P.list('k34_' + nm, [0] * NT)
    m.S('얼음판', AD.curling_sheet(470, 128, HX, HR), 0, CY)
    curl_t = m.T('얼음결', '', -150, 70, 10, C_WHITE, F_BODY, True, 0, w=200, h=16, bg=C_BOX)
    curl_t.on(on_msg('k34_새스톤'), ifelse(gt(W('curl'), 0), [write(join('얼음결: 위로 휘어요 ↑ (세기 ', abs_(W('curl')), ')'))],
                                         [write(join('얼음결: 아래로 휘어요 ↓ (세기 ', abs_(W('curl')), ')'))]))
    arrow = m.S('조준', AD.aim_arrow(), SX + 50, CY)
    arrow.on(on_msg('k34_조준'), xy(add(SX, mul(cos_(W('ang')), 52)), add(CY, mul(sin_(W('ang')), 52))), rot(mul(W('ang'), -1)))
    arrow.on(on_msg('k34_던짐'), hide())
    arrow.on(on_msg('k34_새스톤'), show())
    pwb = m.S('힘막대', K.bar_set('k34_pw', 120, 9, 'royal'), -150, -100)
    m.T('힘글', '힘', -222, -100, 9, C_WHITE, F_NUM, False, 0, w=24, h=12)
    pwb.on(on_msg('k34_힘'), shape(add(floor(mul(div(W('pw'), 100), 40)), 1)))
    # 스톤 (복제본 7개): 위치·속도는 리스트에
    st = m.S('스톤', [('me', AD.stone((60, 110, 240), 'blue')), ('ai', AD.stone((230, 60, 70), 'red'))], 0, -300, visible=False)
    st.local('si', 0)
    st.local('복제', 0)
    for v in ('v', 'nv', 'dx', 'dy', 'dd', 'p', 'nx', 'ny', 'f', 'c'):
        st.local('q' + v, 0)
    L = lambda nm, i: LGET('k34_' + nm, i)
    me = V('si')
    phys = [S_('mov', 1),
            setv('qv', fn('root', add(mul(L('vx', me), L('vx', me)), mul(L('vy', me), L('vy', me))))),
            setv('qf', 0.09), setv('qc', mul(W('curl'), 0.004)),
            if_(eq(W('sw'), 1), setv('qf', 0.055), setv('qc', mul(W('curl'), 0.002))),
            setv('qnv', sub(V('qv'), V('qf'))),
            ifelse(le(V('qnv'), 0), [lst_set('k34_vx', me, 0), lst_set('k34_vy', me, 0)],
                   [lst_set('k34_vx', me, mul(L('vx', me), div(V('qnv'), V('qv')))),
                    lst_set('k34_vy', me, add(mul(L('vy', me), div(V('qnv'), V('qv'))), V('qc')))]),
            lst_set('k34_x', me, add(L('x', me), L('vx', me))), lst_set('k34_y', me, add(L('y', me), L('vy', me)))]
    for j in range(1, NT + 1):
        phys.append(if_(and_(ne(me, j), eq(L('in', j), 1)),
                        setv('qdx', sub(L('x', j), L('x', me))), setv('qdy', sub(L('y', j), L('y', me))),
                        setv('qdd', add(mul(V('qdx'), V('qdx')), mul(V('qdy'), V('qdy')))),
                        if_(and_(lt(V('qdd'), 4 * R * R), gt(V('qdd'), 0.01)),
                            setv('qdd', fn('root', V('qdd'))), setv('qnx', div(V('qdx'), V('qdd'))), setv('qny', div(V('qdy'), V('qdd'))),
                            setv('qp', add(mul(sub(L('vx', me), L('vx', j)), V('qnx')), mul(sub(L('vy', me), L('vy', j)), V('qny')))),
                            if_(gt(V('qp'), 0),
                                lst_set('k34_vx', me, sub(L('vx', me), mul(V('qp'), V('qnx')))),
                                lst_set('k34_vy', me, sub(L('vy', me), mul(V('qp'), V('qny')))),
                                lst_set('k34_vx', j, add(L('vx', j), mul(V('qp'), V('qnx')))),
                                lst_set('k34_vy', j, add(L('vy', j), mul(V('qp'), V('qny')))),
                                cast('k34_딱')),
                            lst_set('k34_x', j, add(L('x', me), mul(V('qnx'), 2 * R + 0.3))),
                            lst_set('k34_y', j, add(L('y', me), mul(V('qny'), 2 * R + 0.3))))))
    phys += [if_(or_(gt(L('x', me), 232), gt(abs_(sub(L('y', me), CY)), 60)),
                 lst_set('k34_in', me, 0), lst_set('k34_vx', me, 0), lst_set('k34_vy', me, 0), cast('k34_아웃'))]
    st.on(on_msg('k34_배치'), if_(eq(V('복제'), 0), setv('si', 0), rep(NT, chg('si', 1), clone_self())))
    st.on(on_clone(), setv('복제', 1), ifelse(gt(V('si'), NS), [shape('ai')], [shape('me')]),
          until(eq(V('게임중'), -1),
                ifelse(eq(L('in', me), 1),
                       [if_(or_(ne(L('vx', me), 0), ne(L('vy', me), 0)), *phys),
                        xy(L('x', me), L('y', me)), show()],
                       [hide()])))
    brm = m.S('빗자루', AD.broom(), 0, -300, visible=False)
    brm.on(on_msg('k34_던짐'), until(eq(W('phase'), 0),
                                   ifelse(eq(W('sw'), 1),
                                          [xy(add(L('x', W('shot')), 16), add(L('y', W('shot')), rnd(-6, 6))), show(), rot(rnd(-20, 20))],
                                          [hide()])), hide())
    # 진행
    stopped = and_(*[and_(eq(L('vx', i), 0), eq(L('vy', i), 0)) for i in range(1, NT + 1)])
    mgr = hidden(m, '컬링담당')
    held = key(K_SPACE)
    dist = lambda i: fn('root', add(mul(sub(L('x', i), HX), sub(L('x', i), HX)), mul(sub(L('y', i), CY), sub(L('y', i), CY))))
    calc = [S_('pts', 0), S_('best', 999), S_('ai', 999), S_('out', 0)]
    for i in range(1, NT + 1):
        if i <= NS:
            calc.append(if_(eq(L('in', i), 1), S_('d', dist(i)),
                            if_(le(W('d'), HR + 2), C_('pts', sub(25, mul(W('d'), 0.4)))),
                            if_(lt(W('d'), W('best')), S_('best', W('d')))))
        else:
            calc.append(ifelse(eq(L('in', i), 1), [S_('d', dist(i)), if_(lt(W('d'), W('ai')), S_('ai', W('d')))], [C_('out', 1)]))
    calc += [if_(lt(W('best'), W('ai')), C_('pts', 10)), C_('pts', mul(W('out'), 6))]
    mgr.on(on_msg('게임시작'), S_('shot', 0),
           until(or_(ge(W('shot'), NS), eq(V('게임중'), 0)),
                 C_('shot', 1), S_('k', W('shot')),
                 lst_set('k34_x', W('k'), SX), lst_set('k34_y', W('k'), CY), lst_set('k34_vx', W('k'), 0), lst_set('k34_vy', W('k'), 0),
                 lst_set('k34_in', W('k'), 1),
                 S_('ang', 0), S_('pw', 0), S_('pdir', 1), S_('curl', mul(div(rnd(5, 12), 10), sub(mul(rnd(0, 1), 2), 1))),
                 setv('미니표시', join('스톤 ', W('shot'), '/', NS)), cast('k34_새스톤'), cast('k34_조준'), cast('k34_힘'),
                 S_('phase', 1),
                 until(or_(held, eq(V('게임중'), 0)),
                       if_(key(K_UP), C_('ang', 0.35)), if_(key(K_DOWN), C_('ang', -0.35)), *clamp('k34_ang', -12, 12),
                       cast('k34_조준')),
                 until(or_(not_(held), eq(V('게임중'), 0)),
                       C_('pw', mul(W('pdir'), 2.2)),
                       if_(gt(W('pw'), 100), S_('pw', 100), S_('pdir', -1)), if_(lt(W('pw'), 0), S_('pw', 0), S_('pdir', 1)),
                       cast('k34_힘')),
                 S_('d', add(3, mul(W('pw'), 0.065))),
                 lst_set('k34_vx', W('k'), mul(W('d'), cos_(W('ang')))), lst_set('k34_vy', W('k'), mul(W('d'), sin_(W('ang')))),
                 S_('phase', 2), cast('k34_던짐'),
                 wait(0.2), until(or_(stopped, eq(V('게임중'), 0)),
                                  ifelse(or_(mouse_down(), gt(W('swt'), 0)), [S_('sw', 1)], [S_('sw', 0)]),
                                  if_(gt(W('swt'), 0), C_('swt', -1))),
                 S_('phase', 0), S_('sw', 0), *calc, cast('k34_점수'), wait(0.8)),
           *calc, wait(0.5), *m.end_blocks(W('pts')))
    mgr.on(on_key(K_S), if_(eq(W('phase'), 2), S_('swt', 8)))
    mgr.on(on_msg('시간끝'), *calc, *m.end_blocks(W('pts')))
    score_t = m.T('점수글', '', 150, 70, 10, C_WHITE, F_NUM, False, 0, w=170, h=16, bg=C_BOX)
    score_t.on(on_msg('k34_점수'), write(join('지금 점수 ', rounded(W('pts')), '점')))
    score_t.on(on_scene(), write('과녁 가운데일수록 높은 점수'))
    sw_t = m.T('쓸기글', '쓸기!', -20, -100, 12, C_ACC, F_NUM, False, 0, w=80, h=16, visible=False)
    sw_t.on(on_msg('k34_던짐'), until(eq(W('phase'), 0), ifelse(eq(W('sw'), 1), [show()], [hide()])), hide())
    m.T('조작글', '↑↓ 방향 · SPACE 꾹 → 놓으면 발사 · 미끄러질 때 마우스 꾹(또는 S 연타) = 쓸기', 40, -118, 8, C_DIM, F_BODY, True, 0, w=330, h=12)
    pop(m, '딱', [('a', K.big_text('딱!', 18, 'white'))], 0, 0, 'k34_딱', 0.2, follow=(L('x', W('shot')), add(L('y', W('shot')), 18)))
    m.on_start(*[lst_set('k34_in', i, 0) for i in range(1, NS + 1)],
               *[lst_set('k34_vx', i, 0) for i in range(1, NT + 1)], *[lst_set('k34_vy', i, 0) for i in range(1, NT + 1)],
               lst_set('k34_x', NS + 1, rnd(40, 90)), lst_set('k34_y', NS + 1, add(CY, rnd(-18, 18))),
               lst_set('k34_x', NS + 2, add(HX, rnd(-30, 10))), lst_set('k34_y', NS + 2, add(CY, rnd(-26, 26))),
               lst_set('k34_x', NS + 3, add(HX, rnd(8, 34))), lst_set('k34_y', NS + 3, add(CY, rnd(-30, 30))),
               *[lst_set('k34_in', i, 1) for i in range(NS + 1, NT + 1)],
               S_('phase', 0), S_('sw', 0), S_('swt', 0), S_('pts', 0), S_('shot', 0), S_('ang', 0), S_('curl', 0.6),
               cast('k34_배치'), cast('k34_새스톤'), cast('k34_조준'))
    m.snd('k34_딱', play('hit'))
    m.snd('k34_던짐', play('whistle'))
    m.snd('k34_아웃', play('pop'))
    m.finish('충주호 얼음판 컬링! 파란 스톤 4개를 과녁 가운데로.\n빨간 스톤을 쳐 낼 수도 있어요. 얼음결 따라 살짝 휘어요.',
             '조작: ↑↓ 방향 · SPACE 를 누르고 있다가 떼면 발사 · 마우스 꾹(S 연타) = 쓸기(덜 느려짐)')
    return True


# ================================================================== 35. 활주로 관제
@game(35)
def g35(P, ctx):
    TL, NP = 40, 8
    RY, RX0, RX1 = -6, -165, 165          # 활주로 y, 왼끝, 오른끝
    m = mg(P, ctx, T, 35, time_limit=TL, status='착륙 0 · 이륙 0', dim=60)
    sc = m.sc
    W, S_, C_ = pfx('k35_')
    vars_(P, *['k35_' + v for v in ('rw', 'land', 'dep', 'near', 'delay', 'slot', 'kind', 'qn', 'fx', 'fy')])
    for nm in ('kind', 'st', 'x', 'y', 'cl'):
        P.list('k35_' + nm, [0] * NP)
    m.S('공항', AD.airfield(), 0, -8)
    lamp = m.T('활주로등', '활주로 비었음', -150, 76, 10, '#7CFFA0', F_NUM, False, 0, w=130, h=16, bg=C_BOX)
    lamp.on(on_msg('k35_활주로'), ifelse(gt(W('rw'), 0), [write('활주로 사용 중'), text_color('#FF6B7A')],
                                       [write('활주로 비었음'), text_color('#7CFFA0')]))
    m.T('도움말', '착륙기(흰색)는 기본 "착륙 허가", 이륙기(주황)는 기본 "대기" · 클릭하면 바뀌어요', 40, -122, 8, C_DIM, F_BODY, True, 0,
        w=360, h=12)
    pl = m.S('비행기', [('a1', AD.plane('arr', 1)), ('a0', AD.plane('arr', 0)), ('d1', AD.plane('dep', 1)), ('d0', AD.plane('dep', 0))],
             0, -300, visible=False)
    for v in ('i', 'k', 's', 'px', 'py', 'c', 'w', 'sp', 'ang', '복제', 'on', 'hz'):
        pl.local('q' + v, 0)
    Q = lambda n: V('q' + n)
    SQ = lambda n, v: setv('q' + n, v)
    look = [ifelse(eq(Q('k'), 1), [ifelse(eq(Q('c'), 1), [shape('a1')], [shape('a0')])],
                   [ifelse(eq(Q('c'), 1), [shape('d1')], [shape('d0')])])]
    sync = [lst_set('k35_st', Q('i'), Q('s')), lst_set('k35_x', Q('i'), Q('px')), lst_set('k35_y', Q('i'), Q('py')),
            lst_set('k35_cl', Q('i'), Q('c'))]
    head = lambda tx, ty, spd: [SQ('ang', fn('atan_radian', div(sub(ty, Q('py')), add(abs_(sub(tx, Q('px'))), 0.001)))),
                                if_(lt(sub(tx, Q('px')), 0), SQ('ang', sub(180, Q('ang')))),
                                chg('qpx', mul(cos_(Q('ang')), spd)), chg('qpy', mul(sin_(Q('ang')), spd)),
                                rot(sub(90, Q('ang')))]
    enter_rw = [if_(gt(W('rw'), 0), C_('near', 1), S_('fx', Q('px')), S_('fy', Q('py')), cast('k35_근접')), C_('rw', 1), SQ('on', 1),
                cast('k35_활주로')]
    leave_rw = [if_(eq(Q('on'), 1), SQ('on', 0), C_('rw', -1), cast('k35_활주로'))]
    gate_x, thr_x = 205, RX1 - 8
    # 착륙기 상태: 1 접근, 2 대기 선회, 3 착륙 활주, 4 유도로로 빠짐 / 이륙기: 5 대기, 6 진입·이륙 활주, 7 상승
    arrive = [
        ifelse(eq(Q('s'), 1),
               [*head(gate_x, RY + 34, 0.9),
                if_(lt(abs_(sub(Q('px'), gate_x)), 4),
                    ifelse(eq(Q('c'), 1), [SQ('s', 8)], [SQ('s', 2), SQ('ang', 0)]))], []),
        ifelse(eq(Q('s'), 8),
               [*head(thr_x, RY, 1.5),
                if_(lt(abs_(sub(Q('px'), thr_x)), 3), SQ('px', thr_x), SQ('py', RY), SQ('s', 3), SQ('sp', 2.4), *enter_rw,
                    cast('k35_착지'))], []),
        ifelse(eq(Q('s'), 2),
               [chg('qang', 2), SQ('px', add(gate_x, mul(cos_(Q('ang')), 24))), SQ('py', add(RY + 62, mul(sin_(Q('ang')), 18))),
                rot(sub(0, Q('ang'))), chg('qw', 1),
                if_(gt(Q('w'), 600), SQ('c', 1), *look, cast('k35_연료')),
                if_(eq(Q('c'), 1), SQ('s', 1))], []),
        ifelse(eq(Q('s'), 3),
               [chg('qpx', mul(Q('sp'), -1)), SQ('sp', maxv(1.2, mul(Q('sp'), 0.993))), rot(-90),
                if_(lt(Q('px'), -95), *leave_rw, SQ('s', 4))], []),
        ifelse(eq(Q('s'), 4),
               [*head(-95, -60, 0.8), fx_add('transparency', 1.2),
                if_(lt(Q('py'), -55), C_('land', 1), cast('k35_점수'), SQ('s', 9))], [])]
    depart = [
        ifelse(eq(Q('s'), 5),
               [chg('qw', 1), if_(eq(Q('c'), 1), SQ('s', 6), SQ('sp', 0.5), *enter_rw, cast('k35_이륙'))], []),
        ifelse(eq(Q('s'), 6),
               [ifelse(lt(Q('py'), RY - 1), [*head(thr_x, RY, 1.2)],
                       [SQ('py', RY), chg('qpx', mul(Q('sp'), -1)), SQ('sp', minv(4.2, add(Q('sp'), 0.045))), rot(-90),
                        if_(lt(Q('px'), -60), SQ('s', 7), *leave_rw)])], []),
        ifelse(eq(Q('s'), 7),
               [chg('qpx', mul(Q('sp'), -1)), chg('qpy', 1.1), rot(-75), fx_add('transparency', 1.5),
                if_(lt(Q('px'), -240), C_('dep', 1), cast('k35_점수'), SQ('s', 9))], [])]
    pl.on(on_msg('게임시작'), S_('slot', 0),
          until(eq(V('게임중'), 0),
                C_('slot', 1), if_(gt(W('slot'), NP), S_('slot', 1)),
                if_(eq(LGET('k35_st', W('slot')), 0),
                    S_('kind', rnd(1, 2)),
                    if_(ge(W('qn'), 2), S_('kind', 1)),
                    clone_self()),
                wait(div(rnd(26, 42), 10))))
    pl.on(on_clone(), SQ('복제', 1), SQ('i', W('slot')), SQ('k', W('kind')), SQ('w', 0), SQ('on', 0), fx('transparency', 0),
          ifelse(eq(Q('k'), 1), [SQ('s', 1), SQ('c', 1), SQ('px', -250), SQ('py', rnd(66, 96))],
                 [SQ('s', 5), SQ('c', 0), C_('qn', 1), SQ('px', ifelse_q(W)), SQ('py', -56)]),
          lst_set('k35_kind', Q('i'), Q('k')), *look, xy(Q('px'), Q('py')), show(), *sync,
          until(or_(eq(V('게임중'), 0), eq(Q('s'), 9)),
                ifelse(eq(Q('k'), 1), arrive, depart), xy(Q('px'), Q('py')), *sync),
          if_(eq(Q('k'), 2), C_('qn', -1)), *leave_rw, lst_set('k35_st', Q('i'), 0), del_clone())
    pl.on(on_click(), if_(and_(eq(Q('복제'), 1), eq(V('게임중'), 1)),
                          if_(or_(eq(Q('s'), 1), or_(eq(Q('s'), 2), eq(Q('s'), 5))),
                              SQ('c', sub(1, Q('c'))), *look, lst_set('k35_cl', Q('i'), Q('c')), cast('k35_딸깍'))))
    # 지연 벌점: 대기 중인 비행기 수만큼
    mgr = hidden(m, '관제담당')
    mgr.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                   *[if_(or_(eq(LGET('k35_st', i), 2), and_(eq(LGET('k35_st', i), 5), gt(V('남은시간'), 0))),
                                         C_('delay', 0.1)) for i in range(1, NP + 1)],
                                   wait(0.1)))
    hud = setv('미니표시', join('착륙 ', W('land'), ' · 이륙 ', W('dep')))
    mgr.on(on_msg('k35_점수'), hud)
    score = sub(sub(mul(add(W('land'), W('dep')), 8), mul(W('near'), 15)), mul(W('delay'), 0.5))
    mgr.on(on_msg('시간끝'), *m.end_blocks(score))
    delay_t = m.T('지연글', '', 150, 76, 10, C_WHITE, F_NUM, False, 0, w=140, h=16, bg=C_BOX)
    delay_t.on(on_msg('게임시작'), until(eq(V('게임중'), 0), write(join('지연 ', rounded(W('delay')), '초 · 근접 ', W('near'))), wait(0.3)))
    pop(m, '근접', [('a', K.big_text('충돌 위험!', 24, 'red'))], 0, 30, 'k35_근접', 0.6)
    pop(m, '연료', [('a', K.big_text('연료 부족! 비상 착륙', 16, 'red'))], 0, 50, 'k35_연료', 0.6)
    m.on_start(S_('rw', 0), S_('land', 0), S_('dep', 0), S_('near', 0), S_('delay', 0), S_('qn', 0), S_('slot', 0),
               *[lst_set('k35_st', i, 0) for i in range(1, NP + 1)], cast('k35_활주로'))
    m.snd('k35_딸깍', play('tick'))
    m.snd('k35_근접', play('alarm'))
    m.snd('k35_착지', play('hit'))
    m.snd('k35_이륙', play('whistle'))
    m.snd('k35_점수', play('coin'))
    m.snd('k35_연료', play('bad'))
    m.finish('인천공항 관제탑! 활주로엔 한 번에 비행기 한 대만.\n비행기를 눌러 허가(초록)/대기(빨강)를 바꾸세요. 오래 기다리면 감점!',
             '조작: 비행기 클릭  ·  착륙·이륙 한 대 +8 · 충돌 위험 -15 · 지연 1초 -0.5  ·  40초')
    return True


def ifelse_q(W):
    """이륙 대기 자리 x (첫째 대기 175, 둘째 205)."""
    return add(145, mul(W('qn'), 30))


# ================================================================== 36. 국회 연설
LINES36 = [
    ('청년 월세를 나라가 돕겠습니다!', (12, 0, 0, -4, 4)),
    ('기초연금을 올려 드리겠습니다!', (-4, 14, 4, -4, 0)),
    ('쌀값을 제값 받게 지키겠습니다!', (0, 4, 15, -4, 0)),
    ('세금을 줄여 기업을 살리겠습니다!', (2, -2, -2, 15, -6)),
    ('최저임금을 올리겠습니다!', (6, 0, -2, -10, 14)),
    ('일자리를 확 늘리겠습니다!', (8, 0, 0, 4, 6)),
    ('주 4일 근무를 시작하겠습니다!', (10, -4, -4, -10, 12)),
    ('농촌에 큰 병원을 짓겠습니다!', (-2, 10, 10, -2, 0)),
    ('규제를 확 풀겠습니다!', (4, -4, -6, 14, -8)),
    ('대학 등록금을 반으로!', (14, -2, 0, -4, 2)),
    ('노인 일자리를 늘리겠습니다!', (-4, 12, 2, 0, -2)),
    ('스마트팜에 투자하겠습니다!', (6, 0, 10, 6, -2)),
    ('대기업 세금을 올리겠습니다!', (4, 2, 2, -14, 10)),
    ('버스·지하철 요금을 내리겠습니다!', (8, 8, 0, -4, 6)),
    ('수입 농산물을 막겠습니다!', (-4, 2, 14, -8, 0)),
    ('창업 지원금을 늘리겠습니다!', (12, -4, 0, 8, -2)),
    ('연금 개혁, 미루지 않겠습니다!', (8, -10, 0, 4, -2)),
    ('공장을 지방으로 옮기겠습니다!', (2, 4, 8, -6, 6)),
    ('일하는 시간을 유연하게!', (2, 0, 0, 12, -10)),
    ('효도 수당을 드리겠습니다!', (-6, 14, 6, -4, -2)),
    ('청년 농부를 키우겠습니다!', (8, 2, 10, 0, -2)),
    ('안전한 일터를 만들겠습니다!', (2, 0, 0, -4, 14)),
    ('수출 기업을 밀어 주겠습니다!', (0, 0, -4, 14, 4)),
    ('모두가 함께 잘사는 나라!', (3, 3, 3, 3, 3)),
]


@game(36)
def g36(P, ctx):
    NT, TT, NG = 6, 12, 5
    NL = len(LINES36)
    m = mg(P, ctx, T, 36, time_limit=None, status='연설 1/%d' % NT, dim=80)
    sc = m.sc
    W, S_, C_ = pfx('k36_')
    vars_(P, *['k36_' + v for v in ('turn', 'pick', 'wish', 'tleft', 'avg', 'low', 'k', 'e')] +
          ['k36_m%d' % g for g in range(1, NG + 1)] + ['k36_c%d' % c for c in range(1, 4)])
    P.list('k36_txt', [l[0] for l in LINES36])
    for g in range(NG):
        P.list('k36_e%d' % (g + 1), [l[1][g] for l in LINES36])
    P.list('k36_used', [0] * NL)
    GX = [-176, -88, 0, 88, 176]
    for g in range(NG):
        gn = g + 1
        mv = W('m%d' % gn)
        cr = m.S('청중%d' % gn, [('a', AD.crowd(g, 0)), ('b', AD.crowd(g, 1)), ('c', AD.crowd(g, 2))], GX[g], 64)
        cr.on(on_msg('k36_반응'), ifelse(lt(mv, 35), [shape('a')], [ifelse(lt(mv, 65), [shape('b')], [shape('c')])]),
              if_(ne(LGET('k36_e%d' % gn, W('pick')), 0),
                  ifelse(gt(LGET('k36_e%d' % gn, W('pick')), 0), [rep(3, mvy(5), wait(0.06), mvy(-5), wait(0.06))],
                         [rep(3, mvx(3), wait(0.04), mvx(-3), wait(0.04))])))
        cr.on(on_scene(), shape('b'))
        m.S('이름%d' % gn, K.badge(AD.GROUPS36[g][0], 54, 16, 'navy'), GX[g], 34)
        bar = m.S('기분%d' % gn, K.bar_set('k36_mood', 64, 7, 'royal'), GX[g], 22)
        bar.on(on_msg('k36_반응'), shape(add(floor(mul(div(mv, 100), 40)), 1)))
        bar.on(on_scene(), shape(21))
        num = m.T('기분수%d' % gn, '50', GX[g] + 40, 22, 8, C_WHITE, F_NUM, False, 0, w=24, h=12)
        num.on(on_msg('k36_반응'), write(rounded(mv)))
        num.on(on_scene(), write('50'))
        dlt = m.T('변화%d' % gn, '', GX[g], 92, 12, C_ACC, F_NUM, False, 0, w=50, h=16)
        dlt.on(on_msg('k36_반응'), S_('e', LGET('k36_e%d' % gn, W('pick'))), if_(eq(W('wish'), gn), if_(gt(W('e'), 0), S_('e', mul(W('e'), 2)))),
               ifelse(gt(W('e'), 0), [write(join('+', W('e'))), text_color('#7CFFA0')],
                      [ifelse(lt(W('e'), 0), [write(W('e')), text_color('#FF6B7A')], [write('')])]),
               wait(1.2), write(''))
    wish = m.T('바람글', '', 0, 92, 9, '#FFE08A', F_BODY, True, 0, w=110, h=14, bg=C_BOX, visible=False)
    wish.on(on_msg('k36_새판'), xy(LGET('k36_gx', W('wish')), 92), write('우리 얘기 해 주세요!'), show())
    wish.on(on_msg('k36_고름'), hide())
    P.list('k36_gx', GX)
    # 연설 카드 3장
    CX = [-152, 0, 152]
    for c in range(1, 4):
        lv = W('c%d' % c)
        card = m.S('카드%d' % c, K.panel(144, 84, 'card'), CX[c - 1], -62)
        G.hover_scripts(card, 104)
        m.S('카드번호%d' % c, K.badge(str(c), 20, 18, 'royal'), CX[c - 1] - 62, -24)
        t = m.T('카드글%d' % c, '', CX[c - 1], -52, 11, C_WHITE, F_BODY, True, 0, w=128, h=40)
        t.on(on_msg('k36_새판'), write(join('"', LGET('k36_txt', lv), '"')))
        pick = [if_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)), S_('pick', lv), setv('대기', 0), setv('선택', c))]
        card.on(on_click(), *pick)
        t.on(on_click(), *pick)
        hidden(m, '카드키%d' % c).on(on_key(48 + c), *pick)
        for g in range(NG):
            ic = m.S('효과%d_%d' % (c, g + 1), [('n', AD.blank()), ('u', AD.effect_icon(g, 1)), ('d', AD.effect_icon(g, 0))],
                     CX[c - 1] - 48 + g * 24, -90)
            e = LGET('k36_e%d' % (g + 1), lv)
            ic.on(on_msg('k36_새판'), ifelse(ge(e, 4), [shape('u')], [ifelse(le(e, -4), [shape('d')], [shape('n')])]))
            ic.on(on_scene(), shape('n'))
        card.on(on_msg('k36_고름'), ifelse(eq(V('선택'), c), [card.pct(110)], [fx('brightness', -40)]))
        card.on(on_msg('k36_새판'), card.pct(100), fx('brightness', 0))
    tb = m.S('시간막대', K.bar_set('k36_time', 220, 7, 'royal'), 20, 4)
    tb.on(on_msg('k36_시계'), shape(add(floor(mul(div(W('tleft'), TT), 40)), 1)))
    turn_t = m.T('차례글', '', -150, 4, 11, C_WHITE, F_NUM, False, 0, w=110, h=16)
    turn_t.on(on_msg('k36_새판'), write(join('연설 ', W('turn'), ' / ', NT)))
    m.S('나', ctx['PORT']['me'], -210, 4, scale=0.8)
    res = m.S('반응글', [('a', K.big_text('와아아!', 26, 'royal')), ('b', K.big_text('웅성웅성...', 22, 'white')),
                        ('c', K.big_text('우우~', 26, 'red'))], 0, -20, visible=False)
    res.on(on_msg('k36_반응'), shape(V('_mv')), res.pct(120), show(), rep(5, res.grow_pct(-4), wait(0.02)), wait(0.8), hide())
    apply = []
    for g in range(1, NG + 1):
        mv = 'k36_m%d' % g
        apply += [S_('e', LGET('k36_e%d' % g, W('pick'))), if_(and_(eq(W('wish'), g), gt(W('e'), 0)), S_('e', mul(W('e'), 2))),
                  chg(mv, W('e')), *clamp(mv, 0, 100), C_('k', W('e'))]
    timeout = [*[chg('k36_m%d' % g, -6) for g in range(1, NG + 1)], *[x for g in range(1, NG + 1) for x in clamp('k36_m%d' % g, 0, 100)]]
    stats = [S_('avg', div(add(*[W('m%d' % g) for g in range(1, NG + 1)]), NG)), S_('low', 0),
             *[if_(lt(W('m%d' % g), 30), C_('low', 1)) for g in range(1, NG + 1)]]
    mgr = hidden(m, '연설담당')
    deal = [*[lst_set('k36_used', i, 0) for i in range(1, NL + 1)]]
    pick3 = []
    for c in range(1, 4):
        pick3 += [S_('c%d' % c, rnd(1, NL)), until(eq(LGET('k36_used', W('c%d' % c)), 0), S_('c%d' % c, rnd(1, NL))),
                  lst_set('k36_used', W('c%d' % c), 1)]
    mgr.on(on_msg('게임시작'), *deal, S_('turn', 0),
           until(or_(ge(W('turn'), NT), eq(V('게임중'), 0)),
                 C_('turn', 1), *pick3, S_('wish', rnd(1, NG)), setv('선택', 0), S_('pick', 0),
                 setv('미니표시', join('연설 ', W('turn'), '/', NT)), cast('k36_새판'),
                 S_('tleft', TT), setv('대기', 1), reset_timer(), start_timer(),
                 until(or_(eq(V('대기'), 0), le(W('tleft'), 0)), S_('tleft', sub(TT, timer())), cast('k36_시계'), wait(0.05)),
                 setv('대기', 0),
                 ifelse(gt(W('pick'), 0),
                        [cast('k36_고름'), S_('k', 0), *apply,
                         ifelse(ge(W('k'), 12), [setv('_mv', 1)], [ifelse(ge(W('k'), 0), [setv('_mv', 2)], [setv('_mv', 3)])])],
                        [S_('pick', NL), *timeout, setv('_mv', 3), cast('k36_머뭇')]),
                 cast('k36_반응'), wait(1.6)),
           *stats, *m.end_blocks(sub(mul(sub(W('avg'), 38), 2.2), mul(W('low'), 8))))
    pop(m, '머뭇', [('a', K.big_text('머뭇머뭇... 모두 실망!', 18, 'red'))], 0, 40, 'k36_머뭇', 0.6)
    m.T('안내', '카드 아래 아이콘: ▲ 좋아함 · ▼ 싫어함 (얼마나인지는 몰라요) · "우리 얘기" 무리는 기쁨 두 배!', 0, -122, 8, C_DIM, F_BODY, True,
        0, w=440, h=12)
    m.on_start(*[S_('m%d' % g, 50) for g in range(1, NG + 1)], S_('pick', 0), S_('turn', 0), S_('wish', 0), setv('대기', 0),
               setv('선택', 0), S_('tleft', TT))
    m.snd('k36_고름', play('stamp'))
    m.snd('k36_반응', ifelse(eq(V('_mv'), 1), [play('cash')], [ifelse(eq(V('_mv'), 3), [play('bad')], [play('pop')])]))
    m.finish('국회 연설 6번! 문장 카드 3장 중 하나를 골라 외치세요.\n모든 청중 기분을 30 넘게 지키며 평균을 높이면 고득점!',
             '조작: 카드 클릭 또는 숫자키 1·2·3  ·  한 번에 12초 (안 고르면 모두 실망)')
    return True


# ================================================================== 37. 가래떡 썰기
@game(37)
def g37(P, ctx):
    NC, KX, RY = 10, 30, -22
    m = mg(P, ctx, T, 37, time_limit=70, status='0/%d 썰기' % NC, dim=60)
    W, S_, C_ = pfx('k37_')
    vars_(P, *['k37_' + v for v in ('hx', 'v', 'tg', 'n', 'cut', 'err', 'pts', 'tot', 'lt', 'dt', 'L', 'ph', 'good')])
    m.S('받침', AD.board(380), -28, -104)
    m.S('기계', AD.machine(), 205, RY - 10)
    rod = m.S('가래떡', AD.tteok_rod(340), KX + 170, RY)
    rod.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(add(W('hx'), 170))))
    m.S('기계앞', AD.machine(), 205, RY - 10)
    m.S('눈금자', AD.ruler(150), KX - 75, -42)
    m.T('눈금글', '눈금 숫자 = 칸', KX - 75, -56, 8, C_DIM, F_BODY, True, 0, w=100, h=12)
    guide = m.S('안내선', AD.guide_line(), KX - 90, RY + 4, visible=False)
    guide.on(on_msg('k37_새떡'), ifelse(le(W('n'), 6), [xy(sub(KX, W('tg')), RY + 4), show()], [hide()]))
    knife = m.S('칼', AD.knife(), KX, 40)
    knife.on(on_msg('k37_썰기'), glide(0.05, KX, -6), wait(0.08), glide(0.12, KX, 40))
    tgt = m.T('목표글', '', 0, 80, 14, C_WHITE, F_NUM, False, 0, w=300, h=22, bg=C_BOX)
    tgt.on(on_msg('k37_새떡'), write(join('목표 길이 ', div(W('tg'), 10), '칸  (', W('n'), '/', NC, ')')))
    res = m.T('결과글', '', -80, 58, 13, C_WHITE, F_NUM, False, 0, w=200, h=20)
    res.on(on_msg('k37_썰기'),
           ifelse(le(W('err'), 3), [write(join('완벽! 오차 ', rounded(W('err')))), text_color('#7CFFA0')],
                  [ifelse(le(W('err'), 9), [write(join('좋아요 오차 ', rounded(W('err')))), text_color('#FFFFFF')],
                          [write(join('아쉬워요 오차 ', rounded(W('err')))), text_color('#FF6B7A')])]))
    res.on(on_msg('k37_새떡'), write(''))
    pc = m.S('조각', AD.tteok_piece(36), KX - 20, RY, visible=False)
    pc.local('복제', 0)
    pc.local('qn', 0)
    pc.on(on_msg('k37_썰기'), if_(eq(V('복제'), 0), clone_self()))
    pc.on(on_clone(), setv('복제', 1), setv('qn', W('n')), xy(KX - 20, RY), show(), glide(0.12, KX - 22, -60),
          glide(0.3, add(-190, mul(sub(V('qn'), 1), 34)), -102))
    mgr = hidden(m, '떡담당')
    mgr.on(on_key(K_SPACE), if_(eq(W('ph'), 1), S_('cut', 1)))
    mgr.on(on_msg('게임시작'), S_('n', 0), S_('tot', 0), S_('ph', 0),
           until(or_(ge(W('n'), NC), eq(V('게임중'), 0)),
                 C_('n', 1), S_('tg', mul(rnd(6, 13), 10)), S_('v', add(add(62, mul(W('n'), 7)), rnd(0, 26))),
                 S_('hx', KX), S_('cut', 0), cast('k37_새떡'), wait(0.6), S_('lt', timer()), S_('ph', 1),
                 until(or_(or_(eq(W('cut'), 1), lt(W('hx'), KX - 190)), eq(V('게임중'), 0)),
                       S_('dt', sub(timer(), W('lt'))), S_('lt', timer()), if_(gt(W('dt'), 0.1), S_('dt', 0.1)),
                       C_('hx', mul(mul(W('v'), W('dt')), -1))),
                 S_('ph', 0), S_('L', sub(KX, W('hx'))), S_('err', abs_(sub(W('L'), W('tg')))),
                 S_('pts', sub(10, mul(W('err'), 0.4))), if_(lt(W('pts'), 0), S_('pts', 0)), C_('tot', W('pts')),
                 cast('k37_썰기'), setv('미니표시', join(W('n'), '/', NC, ' 썰기 · ', rounded(W('tot')), '점')), wait(1.0)),
           S_('hx', KX), *m.end_blocks(W('tot')))
    mgr.on(on_msg('시간끝'), *m.end_blocks(W('tot')))
    m.on_start(S_('hx', KX), S_('n', 0), S_('tot', 0), S_('ph', 0), S_('cut', 0), S_('tg', 80))
    m.snd('k37_썰기', play('stamp'))
    m.finish('이천 방앗간 가래떡 썰기! 떡이 왼쪽으로 흘러가요.\n목표 길이(칸)만큼 나왔을 때 스페이스로 썰어요. 10번!',
             '조작: SPACE 로 썰기  ·  분홍 점선이 목표 위치 (7번째부터는 점선 없이 눈금자만 보고!)')
    return True


# ================================================================== 38. 짜장면 배달
@game(38)
def g38(P, ctx):
    TL, CY = 50, -14
    DST = [(-140, -59), (-70, -59), (0, -59), (140, -59), (200, -59), (-140, 31), (0, 31), (70, 31), (140, 31)]
    RX, RYY = -205, 31
    m = mg(P, ctx, T, 38, time_limit=TL, status='배달 0건', dim=0)
    W, S_, C_ = pfx('k38_')
    vars_(P, *['k38_' + v for v in ('dt', 'lt', 'heat', 'cargo', 'dst', 'dx', 'dy', 'hits', 'deliv', 'pts', 'inv', 'sp', 'mx', 'my', 'dxk', 'dyk')])
    P.list('k38_dx', [d[0] for d in DST])
    P.list('k38_dy', [d[1] for d in DST])
    m.S('도시', AD.city([-140, 0, 140], [-45, 45], 12), 0, CY)
    rest = m.S('식당', AD.restaurant(), RX, RYY - 2, scale=0.5)
    blk = m.S('블록', AD.blocks38(), 0, CY)
    pin = m.S('목적지', AD.order_pin(1), 0, -300, visible=False)
    pin.on(on_msg('k38_주문'), xy(W('dxk'), add(W('dyk'), 12)), show())
    pin.on(on_msg('k38_끝'), hide())
    sco = m.S('스쿠터', AD.scooter(), -185, RYY, scale=0.85)
    sco.on(on_scene(), xy(-185, RYY), rot(90), fx('transparency', 0))
    spd = 120
    step = lambda key_, axis, sgn: if_(key(key_), (mvx if axis == 'x' else mvy)(mul(sgn * spd, W('dt'))),
                                       if_(touch(blk.name), (mvx if axis == 'x' else mvy)(mul(-sgn * spd, W('dt')))))
    new_order = [S_('dst', rnd(1, len(DST))), S_('dxk', LGET('k38_dx', W('dst'))), S_('dyk', LGET('k38_dy', W('dst'))),
                 S_('cargo', 1), S_('heat', 100), cast('k38_주문')]
    sco.on(on_msg('게임시작'),
           until(eq(V('게임중'), 0),
                 step(K_LEFT, 'x', -1), step(K_RIGHT, 'x', 1), step(K_UP, 'y', 1), step(K_DOWN, 'y', -1),
                 if_(key(K_RIGHT), rot(90)), if_(key(K_DOWN), rot(180)), if_(key(K_LEFT), rot(270)), if_(key(K_UP), rot(0)),
                 if_(lt(obj_x(), -214), lx(-214)), if_(gt(obj_x(), 214), lx(214)), if_(lt(obj_y(), -108), ly(-108)), if_(gt(obj_y(), 80), ly(80)),
                 S_('mx', obj_x()), S_('my', obj_y()),
                 ifelse(lt(timer(), W('inv')), [ifelse(eq(mod(floor(mul(timer(), 8)), 2), 0), [fx('transparency', 65)], [fx('transparency', 0)])],
                        [fx('transparency', 0)]),
                 if_(and_(eq(W('cargo'), 0), touch(rest.name)), *new_order, cast('k38_픽업')),
                 if_(eq(W('cargo'), 1),
                     if_(and_(lt(abs_(sub(W('mx'), W('dxk'))), 13), lt(abs_(sub(W('my'), W('dyk'))), 13)),
                         S_('cargo', 0), C_('deliv', 1), C_('pts', add(15, mul(W('heat'), 0.12))), cast('k38_배달'), cast('k38_끝'),
                         setv('미니표시', join('배달 ', W('deliv'), '건 · 충돌 ', W('hits')))))))
    # 시간·식는 온도
    mgr = hidden(m, '배달담당')
    mgr.on(on_msg('게임시작'), S_('lt', 0), S_('cargo', 0), *new_order, cast('k38_픽업'),
           until(eq(V('게임중'), 0),
                 S_('dt', sub(timer(), W('lt'))), S_('lt', timer()), if_(gt(W('dt'), 0.08), S_('dt', 0.08)), if_(lt(W('dt'), 0), S_('dt', 0)),
                 if_(eq(W('cargo'), 1), C_('heat', mul(mul(W('dt'), -1), 6.5)),
                     if_(le(W('heat'), 0), S_('cargo', 0), S_('heat', 0), C_('hits', 0), cast('k38_식음'), cast('k38_끝'))),
                 *clamp('k38_heat', 0, 100)))
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(W('pts'), 0.9), mul(W('hits'), 4))))
    bar = m.S('온기막대', K.bar_set('k38_heat', 100, 8, 'red'), -150, 96)
    bar.on(on_scene(), *G.live_shape(bar, add(floor(mul(div(W('heat'), 100), 40)), 1), 0.1))
    m.T('온기글', '짜장면 온기', -222, 96, 8, C_WHITE, F_BODY, True, 0, w=60, h=12)
    # 차 (복제본 6대)
    car = m.S('자동차', [('a', AD.car((60, 120, 220), 'blue')), ('b', AD.car((240, 200, 60), 'yellow')), ('c', AD.car((230, 230, 235), 'white'))],
              0, -300, visible=False)
    for v in ('ci', 'cx', 'cy', 'cvx', 'cvy'):
        car.local(v, 0)
    car.on(on_msg('게임시작'), setv('ci', 0), rep(6, chg('ci', 1), clone_self()))
    cfg = [(-100, -64, 75, 0, 90), (100, 36, -85, 0, 270), (-145, 60, 0, -70, 180), (145, -90, 0, 80, 0), (5, 20, 0, -60, 180),
           (60, -54, -70, 0, 270)]
    setup = []
    for i, (x0, y0, vx0, vy0, a0) in enumerate(cfg, 1):
        setup.append(if_(eq(V('ci'), i), setv('cx', x0), setv('cy', y0), setv('cvx', vx0), setv('cvy', vy0), rot(a0)))
    car.on(on_clone(), *setup, shape(add(mod(V('ci'), 3), 1)), xy(V('cx'), V('cy')), show(),
           until(eq(V('게임중'), 0),
                 setv('cx', add(V('cx'), mul(V('cvx'), W('dt')))), setv('cy', add(V('cy'), mul(V('cvy'), W('dt')))),
                 if_(gt(V('cx'), 236), setv('cx', -236)), if_(lt(V('cx'), -236), setv('cx', 236)),
                 if_(gt(V('cy'), 92), setv('cy', -120)), if_(lt(V('cy'), -120), setv('cy', 92)),
                 xy(V('cx'), V('cy')),
                 if_(and_(touch(sco.name), gt(timer(), W('inv'))),
                     S_('inv', add(timer(), 1.4)), C_('hits', 1), C_('heat', -25), cast('k38_쿵'),
                     setv('미니표시', join('배달 ', W('deliv'), '건 · 충돌 ', W('hits'))))),
           del_clone())
    pop(m, '쿵', [('a', K.big_text('쿵! 국물이 쏟아졌어요', 14, 'red'))], 0, 70, 'k38_쿵', 0.5)
    pop(m, '배달글', [('a', K.big_text('배달 완료!', 24, 'royal'))], 0, 50, 'k38_배달', 0.6)
    pop(m, '식음글', [('a', K.big_text('식어서 퇴짜...', 16, 'red'))], 0, 50, 'k38_식음', 0.6)
    m.on_start(S_('cargo', 0), S_('heat', 100), S_('hits', 0), S_('deliv', 0), S_('pts', 0), S_('inv', 0), S_('dt', 0.02), S_('lt', 0),
               S_('dxk', 0), S_('dyk', -300))
    m.snd('k38_쿵', play('hit'))
    m.snd('k38_배달', play('coin'))
    m.snd('k38_식음', play('bad'))
    m.snd('k38_픽업', play('pop'))
    m.finish('중화반점 오토바이로 짜장면 배달! 식당에서 주문을 받아\n주황 핀 자리로 식기 전에 배달하세요. 도로의 차를 조심!',
             '조작: ← ↑ → ↓ 방향키 (건물은 통과 못 해요)  ·  배달하면 다시 식당으로 가서 새 주문  ·  50초')
    return True


# ================================================================== 39. 탁구 대결
@game(39)
def g39(P, ctx):
    TL, WIN = 55, 11
    ZP, ZO = -0.12, 1.12            # 내 타격면 / 상대 타격면
    m = mg(P, ctx, T, 39, time_limit=TL, status='나 0 : 0 상대', dim=60)
    W, S_, C_ = pfx('k39_')
    vars_(P, *['k39_' + v for v in ('bx', 'bz', 'by', 'bvx', 'bvz', 'bvy', 'g', 'bd', 'st', 'v', 'hits', 'me', 'ai', 'rx', 'ry', 'dt', 'lt',
                                     't1', 't2', 'hh', 'xc', 'vya', 'ok', 'sx', 'sy', 'sc', 'dd', 'ex', 'who', 'pm', 'dx')])

    def proj(X, Z, Y=0):
        k = 1 - 0.38 * Z
        return (X * 130 * k, -78 + 86 * Z + Y * k)
    tpath, (tx, ty) = AD.tt_table(proj)
    m.S('탁구대', tpath, tx, ty)
    # 상대
    opp = m.S('상대채', AD.paddle((220, 50, 70), 'opp', 30), 0, 24)
    m.S('상대', ctx['PORT']['p1'], 0, 60, scale=0.5)
    shadow = m.S('그림자', AD.ball_shadow(), 0, -300, visible=False)
    ring = m.S('도착점', AD.target_ring(), 0, -300, visible=False)
    ball = m.S('공', AD.ball(), 0, -300, visible=False)
    me = m.S('내채', AD.paddle((60, 120, 240), 'me', 42), 0, -100)
    me.on(on_msg('게임시작'),
          until(eq(V('게임중'), 0),
                S_('rx', mouse_x()), S_('ry', mouse_y()), *clamp('k39_rx', -160, 160), *clamp('k39_ry', -125, -30),
                xy(W('rx'), W('ry'))))
    sx = mul(W('bx'), mul(130, W('sc')))
    sy = add(add(-78, mul(86, W('bz'))), mul(W('by'), W('sc')))
    place = [S_('sc', sub(1, mul(0.38, W('bz')))), S_('sx', sx), S_('sy', sy)]
    ball.on(on_msg('k39_공'), if_(eq(W('st'), 0), hide()))
    shadow.on(on_msg('k39_공'), if_(eq(W('st'), 0), hide()))

    def launch(dirz, zb, zend, xc, hh):
        return [S_('xc', xc), S_('hh', hh), S_('g', mul(400, mul(W('v'), W('v')))),
                S_('t1', div(abs_(sub(zb, W('bz'))), W('v'))), S_('t2', div(abs_(sub(zend, zb)), W('v'))),
                S_('bvy', sub(mul(mul(0.5, W('g')), W('t1')), div(W('by'), W('t1')))),
                S_('vya', div(add(W('hh'), mul(mul(0.5, W('g')), mul(W('t2'), W('t2')))), W('t2'))),
                S_('bvz', mul(dirz, W('v'))), S_('bvx', div(sub(W('xc'), W('bx')), add(W('t1'), W('t2')))), S_('bd', 0)]
    to_me = launch(-1, 0.35, ZP, div(rnd(-85, 85), 100), rnd(8, 26)) + [S_('st', 1), cast('k39_링'), cast('k39_탁')]
    step = [S_('dt', sub(timer(), W('lt'))), S_('lt', timer()), if_(gt(W('dt'), 0.06), S_('dt', 0.06)), if_(lt(W('dt'), 0), S_('dt', 0)),
            C_('bx', mul(W('bvx'), W('dt'))), C_('bz', mul(W('bvz'), W('dt'))), C_('by', mul(W('bvy'), W('dt'))),
            C_('bvy', mul(mul(W('g'), W('dt')), -1)),
            if_(and_(eq(W('bd'), 0), lt(W('by'), 0)), S_('by', 0), S_('bvy', W('vya')), S_('bd', 1), cast('k39_탁')),
            *place,
            xy(W('sx'), W('sy')), ball.pct(mul(150, W('sc'))), show()]
    ball.on(on_msg('k39_보임'), show())
    # 공 / 그림자 / 상대 채 위치는 담당 루프에서 계산한 값을 따라간다
    shadow.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                      ifelse(eq(W('st'), 0), [hide()],
                                             [xy(W('sx'), add(-78, mul(86, W('bz')))), shadow.pct(mul(100, W('sc'))), show()])))
    ring.on(on_msg('k39_링'), xy(mul(W('xc'), 135.9), add(-88.3, mul(W('hh'), 1.046))), show())
    ring.on(on_msg('k39_링끝'), hide())
    opp.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                   S_('ex', add(W('ex'), mul(sub(mul(W('bx'), 100), W('ex')), 0.12))),
                                   xy(W('ex'), add(18, mul(W('by'), 0.4)))))
    point = lambda who: [S_('st', 0), S_('who', who), cast('k39_링끝'), cast('k39_점')]
    mgr = hidden(m, '탁구담당')
    serve = [S_('v', min_(1.7, add(0.95, mul(add(W('me'), W('ai')), 0.03)))), S_('hits', 0), S_('bx', div(rnd(-50, 50), 100)), S_('bz', ZO), S_('by', 16),
             S_('lt', timer()), *to_me]
    judge = [
        # 상대가 칠 차례
        if_(and_(eq(W('st'), 2), ge(W('bz'), ZO)),
            ifelse(eq(W('ok'), 1),
                   [C_('hits', 1), S_('v', min_(1.85, add(W('v'), 0.07))), S_('by', maxv(W('by'), 8)), *to_me],
                   point(1))),
        # 내가 칠 수 있는지: 공이 튄 뒤 라켓과 겹침
        if_(and_(and_(eq(W('st'), 1), eq(W('bd'), 1)), lt(W('bz'), 0.25)),
            if_(and_(lt(abs_(sub(W('sx'), W('rx'))), 26), lt(abs_(sub(W('sy'), W('ry'))), 24)),
                S_('dx', div(sub(W('sx'), W('rx')), 26)),
                S_('xc', add(mul(W('bx'), 0.4), mul(W('dx'), 0.9))), *clamp('k39_xc', -1.2, 1.2),
                S_('pm', add(10, mul(W('hits'), 4))), if_(gt(abs_(W('xc')), 0.78), C_('pm', 50)),
                S_('ok', 0), if_(gt(rnd(1, 100), W('pm')), S_('ok', 1)),
                *launch(1, 0.72, ZO, W('xc'), rnd(8, 24)), S_('st', 2), cast('k39_링끝'), cast('k39_탁'), cast('k39_쾅'))),
        if_(and_(eq(W('st'), 1), lt(W('bz'), -0.4)), *point(2))]
    # launch 안에서 S_('xc', W('xc')) 로 자기 자신을 다시 읽는 것은 문제 없음
    mgr.on(on_msg('게임시작'), S_('me', 0), S_('ai', 0), S_('st', 0), S_('ex', 0),
           until(eq(V('게임중'), 0),
                 ifelse(ne(W('st'), 0), [*step, *judge],
                        [wait(1.0), if_(eq(V('게임중'), 1), *serve)])))
    mgr.on(on_msg('k39_점'),
           ifelse(eq(W('who'), 1), [C_('me', 1), setv('_mv', 1)], [C_('ai', 1), setv('_mv', 2)]),
           setv('미니표시', join('나 ', W('me'), ' : ', W('ai'), ' 상대')), cast('k39_점수글'),
           if_(or_(ge(W('me'), WIN), ge(W('ai'), WIN)), *m.end_blocks(add(mul(W('me'), 8), sub(11, W('ai'))))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(mul(W('me'), 8), div(sub(11, W('ai')), 2))))
    pop(m, '점수글', [('a', K.big_text('득점!', 30, 'royal')), ('b', K.big_text('실점...', 28, 'red'))], 0, 10, 'k39_점수글', 0.5)
    pop(m, '쾅글', [('a', K.big_text('탕!', 18, 'white'))], 0, 0, 'k39_쾅', 0.15, follow=(W('rx'), add(W('ry'), 30)))
    m.T('도움말', '노란 원 = 공이 내 쪽에 도착할 자리  ·  라켓 가장자리로 치면 공이 옆으로 가요', 0, -122, 8, C_DIM, F_BODY, True, 0, w=420, h=12)
    m.on_start(S_('me', 0), S_('ai', 0), S_('st', 0), S_('v', 1), S_('ex', 0), S_('rx', 0), S_('ry', -90), S_('bx', 0), S_('bz', 1), S_('by', 0),
               S_('sc', 0.62), S_('sx', 0), S_('sy', -300))
    m.snd('k39_탁', play('tick'))
    m.snd('k39_쾅', play('hit'))
    m.snd('k39_점', ifelse(eq(V('_mv'), 1), [play('good')], [play('bad')]))
    m.finish('광주 충장로 탁구 대결! 먼 쪽에서 날아오는 공의 도착점(노란 원)에\n라켓을 대면 자동으로 받아쳐요. 11점 먼저 얻으면 승리!',
             '조작: 마우스로 라켓 이동  ·  점점 빨라져요  ·  55초')
    return True


def min_(a, b):
    return minv(a, b)


# ================================================================== 40. 화포 쏘기
@game(40)
def g40(P, ctx):
    NS, GY, PX, PY = 6, -88, -205, -72
    G_, DT = 220, 1.0 / 60
    m = mg(P, ctx, T, 40, time_limit=150, status='1/%d발' % NS, dim=0)
    W, S_, C_ = pfx('k40_')
    vars_(P, *['k40_' + v for v in ('ang', 'pw', 'shot', 'fire', 'fly', 'bx', 'by', 'bvx', 'bvy', 'wind', 'fx', 'hit', 'hits', 'pts', 'tries', 'ph',
                                     'dist', 'lt', 'dt', 'v0')])
    for k in ('s1', 's2', 's3'):
        P.var('k40_' + k, '')
    m.S('땅', AD.ground40(), 0, -110)
    m.S('포대', AD.cannon_base(), PX, -79)
    barrel = m.S('포신', AD.cannon_barrel(), PX + 35, PY)
    barrel.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                      rot(mul(W('ang'), -1)), xy(add(PX, mul(cos_(W('ang')), 35)), add(PY, mul(sin_(W('ang')), 35)))))
    barrel.on(on_scene(), rot(-45))
    flag = m.S('적기', [('u', AD.enemy_flag(0)), ('d', AD.enemy_flag(1))], 120, -71)
    flag.on(on_msg('k40_새깃발'), shape('u'), xy(W('fx'), -71))
    flag.on(on_msg('k40_쓰러짐'), shape('d'), xy(W('fx'), -84))
    # 이전 탄도: 붓 두 개를 번갈아 (최근 두 발의 궤적이 남는다)
    for k, col in ((0, '#7DB2FF'), (1, '#FFC46B')):
        pen = m.S('붓%d' % k, AD.dot(), PX, PY)
        pen.on(on_msg('k40_발사%d' % k), pen_clear(), pen_color(col), pen_size(2), pen_up(), xy(W('bx'), W('by')), pen_down(),
               until(eq(W('fly'), 0), xy(W('bx'), W('by'))), pen_up())
        pen.on(on_msg('k40_새깃발'), pen_clear())
        pen.on(on_scene(), pen_clear())
    ball = m.S('포탄', AD.cannonball(), PX, PY, visible=False)
    ball.on(on_msg('k40_발사0'), show(), until(eq(W('fly'), 0), xy(W('bx'), W('by'))), hide())
    ball.on(on_msg('k40_발사1'), show(), until(eq(W('fly'), 0), xy(W('bx'), W('by'))), hide())
    boom = m.S('폭발', AD.boom(), 0, 0, visible=False)
    boom.on(on_msg('k40_착탄'), xy(W('bx'), add(W('by'), 6)), boom.pct(60), fx('transparency', 0), show(),
            rep(8, boom.grow_pct(14), fx_add('transparency', 11), wait(0.02)), hide())
    for k, (x, mk) in enumerate(((-150, 's1'), (0, 's2'), (150, 's3'))):
        t_ = m.T('수치%d' % k, '', x, 92, 11, C_WHITE, F_NUM, False, 0, w=140, h=18, bg=C_BOX)
        t_.on(on_scene(), *G.live_write(t_, [], 'k40_' + mk, 0.1))
    live = hidden(m, '수치담당')
    live.on(on_msg('게임시작'),
            until(eq(V('게임중'), 0),
                  S_('s1', join('각도 ', rounded(W('ang')), '°  ↑↓')), S_('s2', join('화약 ', div(rounded(mul(W('pw'), 10)), 10), '  ←→')),
                  ifelse(ge(W('wind'), 0), [S_('s3', join('바람 → ', div(rounded(W('wind')), 10)))],
                         [S_('s3', join('바람 ← ', div(rounded(abs_(W('wind'))), 10)))]),
                  wait(0.08)))
    res = m.T('결과글', '', 0, 56, 14, C_WHITE, F_NUM, False, 0, w=300, h=22)
    res.on(on_msg('k40_착탄'), ifelse(eq(W('hit'), 1), [write('명중!'), text_color('#7CFFA0')],
                                     [ifelse(gt(W('bx'), W('fx')), [write(join('빗나감! ', rounded(sub(W('bx'), W('fx'))), ' 만큼 멀리'))],
                                             [write(join('빗나감! ', rounded(sub(W('fx'), W('bx'))), ' 만큼 짧게'))]), text_color('#FF6B7A')]),
           wait(1.4), write(''))
    mgr = hidden(m, '포격담당')
    mgr.on(on_key(K_SPACE), if_(eq(W('ph'), 1), S_('fire', 1)))
    newflag = [S_('fx', rnd(10, 200)), S_('wind', rnd(-30, 30)), S_('tries', 0), cast('k40_새깃발')]
    mgr.on(on_msg('게임시작'), S_('shot', 0), S_('pts', 0), S_('hits', 0), *newflag,
           until(or_(ge(W('shot'), NS), eq(V('게임중'), 0)),
                 C_('shot', 1), C_('tries', 1), S_('fire', 0), S_('ph', 1), S_('lt', timer()),
                 setv('미니표시', join(W('shot'), '/', NS, '발 · 명중 ', W('hits'))),
                 until(or_(eq(W('fire'), 1), eq(V('게임중'), 0)),
                       S_('dt', sub(timer(), W('lt'))), S_('lt', timer()), if_(gt(W('dt'), 0.1), S_('dt', 0.1)),
                       if_(key(K_UP), C_('ang', mul(30, W('dt')))), if_(key(K_DOWN), C_('ang', mul(-30, W('dt')))),
                       if_(key(K_RIGHT), C_('pw', mul(3.5, W('dt')))), if_(key(K_LEFT), C_('pw', mul(-3.5, W('dt')))),
                       *clamp('k40_ang', 10, 80), *clamp('k40_pw', 1, 10)),
                 S_('ph', 0),
                 S_('bx', add(PX, mul(cos_(W('ang')), 72))), S_('by', add(PY, mul(sin_(W('ang')), 72))),
                 S_('v0', add(60, mul(W('pw'), 24))), S_('bvx', mul(W('v0'), cos_(W('ang')))), S_('bvy', mul(W('v0'), sin_(W('ang')))),
                 S_('fly', 1), S_('hit', 0), cast('k40_쾅'),
                 ifelse(eq(mod(W('shot'), 2), 1), [cast('k40_발사0')], [cast('k40_발사1')]),
                 until(or_(eq(W('fly'), 0), eq(V('게임중'), 0)),
                       C_('bvx', mul(W('wind'), DT)), C_('bx', mul(W('bvx'), DT)),
                       C_('bvy', -G_ * DT), C_('by', mul(W('bvy'), DT)),
                       if_(and_(lt(abs_(sub(W('bx'), W('fx'))), 14), and_(lt(W('by'), -52), gt(W('by'), -92))), S_('hit', 1), S_('fly', 0)),
                       if_(and_(eq(W('fly'), 1), and_(lt(W('by'), GY), lt(W('bvy'), 0))), S_('by', GY), S_('fly', 0))),
                 cast('k40_착탄'),
                 ifelse(eq(W('hit'), 1),
                        [C_('hits', 1), C_('pts', 100.0 / NS), cast('k40_쓰러짐'), cast('k40_명중'), wait(1.3), *newflag],
                        [S_('dist', abs_(sub(W('bx'), W('fx')))), C_('pts', maxv(0, sub(6, div(W('dist'), 12)))), wait(1.0),
                         if_(ge(W('tries'), 2), *newflag)])),
           *m.end_blocks(W('pts')))
    mgr.on(on_msg('시간끝'), *m.end_blocks(W('pts')))
    m.T('조작글', '↑↓ 각도 · ←→ 화약 양 · SPACE 발사 · 푸른/주황 선 = 이전 탄도', 0, -122, 8, C_DIM, F_BODY, True, 0, w=400, h=12)
    m.on_start(S_('ang', 45), S_('pw', 5), S_('shot', 0), S_('fire', 0), S_('fly', 0), S_('ph', 0), S_('pts', 0), S_('hits', 0),
               S_('wind', 0), S_('fx', 120), S_('hit', 0), cast('k40_새깃발'))
    m.snd('k40_쾅', play('hit'))
    m.snd('k40_착탄', ifelse(eq(W('hit'), 1), [play('fanfare')], [play('pop')]))
    m.finish('수원 화성의 화포로 성 밖 적 깃발을 맞히세요! 6발.\n각도·화약 양·바람을 보고 쏘세요. 이전 탄도가 선으로 남아요.',
             '조작: ↑↓ 각도  ·  ←→ 화약 양  ·  SPACE 발사  ·  깃발은 2발까지 시도')
    return True
