# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 11~20번."""
import random
from games_common import *
import mg_art3 as A3

T = 2
GAMES, game = registry()
import art2b as AB


def _pop_text(m, base, path, x, y, msg, hold=0.6):
    """msg 신호에 튀어나왔다 사라지는 그림."""
    return G.big_pop(m.P, m.sc, base, path, x, y, msg, hold=hold)


# ================================================================== 11. 음악분수 연출 (모양 맞추기)
@game(11)
def g11(P, ctx):
    pats = [('계단', [1, 2, 3, 4, 5]), ('산', [1, 3, 5, 3, 1]), ('V자 계곡', [5, 3, 1, 3, 5]), ('물결', [2, 4, 2, 4, 2]),
            ('내리막', [5, 4, 3, 2, 1]), ('가운데 탑', [0, 1, 5, 1, 0]), ('양쪽 기둥', [5, 1, 0, 1, 5]), ('파도', [1, 3, 5, 4, 2]),
            ('M자', [2, 5, 2, 5, 2]), ('왕관', [4, 2, 3, 2, 4]), ('들쭉날쭉', [0, 4, 1, 5, 2]), ('분수 쇼', [5, 0, 5, 0, 5])]
    NP = len(pats)
    m = mg(P, ctx, T, 11, time_limit=60, status='모양 1/%d' % NP, dim=70)
    P.list('s11_pat', [v for _, p in pats for v in p])
    P.list('s11_name', [nm for nm, _ in pats])
    P.list('s11_h', [1] * 5)
    vars_(P, 's11_sel', 's11_n', 's11_ok', 's11_t0', 's11_lock', 's11_gain')
    XS = [-132 + 66 * k for k in range(5)]
    CY = -8                                   # 기둥 그림 중심 (바닥 y = -96)
    tgt = lambda k: LGET('s11_pat', add(mul(sub(V('s11_n'), 1), 5), k))
    hues = [0, 12, 70, 82, 30]
    for k in range(1, 6):
        gh = m.S('s11목표%d' % k, [('g%d' % L, AB.s11_ghost(L)) for L in range(6)], XS[k - 1], CY)
        gh.on(on_msg('s11새모양'), shape(add(tgt(k), 1)), gh.pct(120), rep(5, gh.grow_pct(-4), wait(0.016)))
    for k in range(1, 6):
        col = m.S('s11분수%d' % k, [('h%d' % L, AB.s11_column(L)) for L in range(6)], XS[k - 1], CY)
        col.local('s11_cur', 1)
        col.local('s11_tk', 0)
        col.on(on_scene(), setv('s11_cur', 1), shape('h1'), fx('color', hues[k - 1]))
        col.on(on_msg('게임시작'),
               until(eq(V('게임중'), 0),
                     ifelse(lt(V('s11_cur'), LGET('s11_h', k)), [chg('s11_cur', 1), shape(add(V('s11_cur'), 1))],
                            [if_(gt(V('s11_cur'), LGET('s11_h', k)), chg('s11_cur', -1), shape(add(V('s11_cur'), 1)))]),
                     chg('s11_tk', 1), if_(eq(mod(V('s11_tk'), 5), 0), flip_x()),
                     wait(0.035)))
        col.on(on_msg('s11성공'), rep(12, fx_add('color', 8), fx_add('brightness', 2), wait(0.03)),
               fx('color', hues[k - 1]), fx('brightness', 0))
    m.S('s11수조', AB.s11_basin(), 0, -103)
    sel = m.S('s11선택', AB.s11_sel(), XS[0], -107)
    sel.on(on_msg('s11선택'), lx(add(-132, mul(sub(V('s11_sel'), 1), 66))), sel.pct(115), wait(0.05), sel.pct(100))
    for k in range(1, 6):
        ok = m.S('s11맞음%d' % k, AB.check_badge('s11_ok'), XS[k - 1] + 15, -110, visible=False)
        ok.on(on_msg('s11확인'), ifelse(eq(LGET('s11_h', k), tgt(k)), [show()], [hide()]))
        ok.on(on_msg('s11새모양'), hide())
    panel(P, m.sc, 's11판', 205, 28, 66, 96, 'glass')
    m.T('s11목표글', '목표 모양', 205, 64, 8, C_DIM, F_BODY, True, 0, w=60, h=12)
    nm = m.T('s11이름', ' ', 205, 40, 11, '#FFE08A', F_NUM, False, 0, w=62, h=30)
    nm.on(on_msg('s11새모양'), write(LGET('s11_name', V('s11_n'))))
    cnt = m.T('s11맞춤', ' ', 205, 8, 9, C_WHITE, F_BODY, True, 0, w=62, h=28)
    cnt.on(on_msg('s11확인'), write(join('맞춘 분수\n', V('s11_ok'), ' / 5')))
    m.T('s11도움', '노란 점선 = 목표 높이', 205, -26, 7, C_DIM, F_BODY, True, 0, w=70, h=22)
    _pop_text(m, 's11완성', K.big_text('완성!', 30, 'royal'), 0, 20, 's11성공', hold=0.4)
    gain = m.T('s11득점', ' ', 0, -14, 14, '#FFE08A', F_NUM, False, 0, w=120, h=20, visible=False)
    gain.on(on_msg('s11성공'), write(join('+', V('s11_gain'))), show(), wait(0.8), hide())

    play_ok = and_(eq(V('게임중'), 1), eq(V('s11_lock'), 0))
    keys = hidden(m, 's11키')
    keys.on(on_key(K_LEFT), if_(and_(play_ok, gt(V('s11_sel'), 1)), chg('s11_sel', -1), cast('s11선택')))
    keys.on(on_key(K_RIGHT), if_(and_(play_ok, lt(V('s11_sel'), 5)), chg('s11_sel', 1), cast('s11선택')))
    keys.on(on_key(K_UP), if_(and_(play_ok, lt(LGET('s11_h', V('s11_sel')), 5)),
                              lst_set('s11_h', V('s11_sel'), add(LGET('s11_h', V('s11_sel')), 1)), cast('s11올림'), cast('s11확인')))
    keys.on(on_key(K_DOWN), if_(and_(play_ok, gt(LGET('s11_h', V('s11_sel')), 0)),
                                lst_set('s11_h', V('s11_sel'), sub(LGET('s11_h', V('s11_sel')), 1)), cast('s11내림'), cast('s11확인')))
    status = setv('미니표시', join('모양 ', V('s11_n'), '/', NP, ' · ', V('합계'), '점'))
    new_pat = [chg('s11_n', 1), setv('s11_t0', timer()), cast('s11새모양'), cast('s11확인'), status]
    mgr = hidden(m, 's11담당')
    mgr.on(on_msg('게임시작'), setv('s11_n', 0), *new_pat, cast('s11선택'))
    mgr.on(on_msg('s11확인'),
           setv('s11_ok', 0), *[if_(eq(LGET('s11_h', k), tgt(k)), chg('s11_ok', 1)) for k in range(1, 6)],
           if_(and_(eq(V('s11_ok'), 5), eq(V('s11_lock'), 0)),
               setv('s11_lock', 1),
               setv('s11_gain', add(8, floor(div(sub(12, sub(timer(), V('s11_t0'))), 4)))),
               if_(lt(V('s11_gain'), 8), setv('s11_gain', 8)),
               chg('합계', V('s11_gain')), status, cast('s11성공'), wait(1.1),
               ifelse(ge(V('s11_n'), NP), [*m.end_blocks(add(V('합계'), mul(V('남은시간'), 0.5)))],
                      [*new_pat, setv('s11_lock', 0)])))
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(V('합계'), mul(V('s11_ok'), 1))))
    m.on_start(setv('합계', 0), setv('s11_sel', 1), setv('s11_n', 1), setv('s11_lock', 0), setv('s11_ok', 0),
               *[lst_set('s11_h', k, 1) for k in range(1, 6)])
    m.snd('s11선택', play('click'))
    m.snd('s11올림', play('tone3'))
    m.snd('s11내림', play('tone1'))
    m.snd('s11성공', play('good'))
    m.finish('← → 로 분수를 고르고 ↑ ↓ 로 물 높이를 바꿔\n노란 점선 목표 모양을 만드세요! 빨리 만들수록 점수 UP',
             '조작: ← → 분수 고르기  ·  ↑ ↓ 높이 (0~5단)  ·  60초 동안 12가지 모양')
    return True


# ================================================================== 12. 개구리 연잎 점프 (타이밍 점프)
@game(12)
def g12(P, ctx):
    # (세계 x, 종류 1보통/2작음/3연꽃, 흔들림 폭, 주기)
    pads = [(0, 1, 0, 3), (125, 1, 0, 3), (255, 1, 30, 3.0), (385, 2, 0, 3), (525, 1, 40, 2.6), (650, 2, 24, 3.0),
            (805, 1, 0, 3), (935, 1, 44, 2.2), (1075, 2, 0, 3), (1205, 2, 30, 2.8), (1355, 1, 40, 2.0), (1500, 3, 0, 3)]
    N = len(pads)
    TL = 50
    FY = -55
    m = mg(P, ctx, T, 12, time_limit=TL, status='연잎 1/%d' % N, dim=40)
    P.list('s12_x', [p[0] for p in pads])
    P.list('s12_ty', [p[1] for p in pads])
    P.list('s12_amp', [p[2] for p in pads])
    P.list('s12_per', [p[3] for p in pads])
    P.list('s12_hw', [{1: 31, 2: 19, 3: 40}[p[1]] for p in pads])
    P.list('s12_sx', [p[0] - 160 for p in pads])
    vars_(P, 's12_cam', 's12_camT', 's12_cur', 's12_st', 's12_p', 's12_t0', 's12_fx', 's12_dist', 's12_jx', 's12_tj',
          's12_u', 's12_land', 's12_fall')
    pad = m.S('s12연잎', [('n', AB.s12_pad('normal')), ('s', AB.s12_pad('small')), ('f', AB.s12_pad('final'))], 0, -300,
              visible=False)
    pad.local('s12_i', 0)
    pad.local('s12_me', 0)
    pad.local('s12_px', 0)
    i_ = V('s12_i')
    pad.on(on_scene(), setv('s12_i', 0), rep(N, chg('s12_i', 1), clone_self()))
    pad.on(on_clone(), setv('s12_me', 1), shape(LGET('s12_ty', i_)),
           ifelse(eq(LGET('s12_ty', i_), 3), [ly(-62)], [ly(-74)]), show(),
           forever(setv('s12_px', add(sub(LGET('s12_x', i_), V('s12_cam')),
                                      mul(LGET('s12_amp', i_), sin_(add(mul(div(timer(), LGET('s12_per', i_)), 360), mul(i_, 77)))))),
                   lx(V('s12_px')), lst_set('s12_sx', i_, V('s12_px'))))
    pad.on(on_msg('s12착지'), if_(and_(eq(V('s12_me'), 1), eq(i_, V('s12_cur'))), mvy(-3), wait(0.08), mvy(3)))
    for x in (-120, 120):
        m.S('s12물결', AB.s12_wave(), x, -82)
    frog = m.S('s12개구리', [('sit', AB.s12_frog('sit')), ('jump', AB.s12_frog('jump'))], -160, FY)
    splash = m.S('s12물보라', AB.s12_splash(), 0, -70, visible=False)
    splash.on(on_msg('s12풍덩'), lx(V('s12_fx')), splash.pct(60), show(), rep(8, splash.grow_pct(6), wait(0.03)),
              wait(0.3), hide())
    mark = m.S('s12표시', AB.s12_marker(), 0, -40, visible=False)
    mark.on(on_msg('s12충전'), show(), until(ne(V('s12_st'), 1), xy(add(V('s12_fx'), V('s12_dist')), -44)), hide())
    bar = m.S('s12힘', K.bar_set('s12_pow', 56, 7, 'royal'), 0, -24, visible=False)
    bar.on(on_msg('s12충전'), show(), until(ne(V('s12_st'), 1), xy(V('s12_fx'), -26), shape(add(floor(mul(V('s12_p'), 40)), 1))),
           hide())
    cur = V('s12_cur')

    def try_land(d):
        j = add(cur, d) if d else cur
        chk = if_(le(abs_(sub(V('s12_fx'), LGET('s12_sx', j))), LGET('s12_hw', j)), setv('s12_land', j))
        return if_(le(j, N), chk) if d else chk
    status = setv('미니표시', join('연잎 ', V('s12_cur'), '/', N, ' · 풍덩 ', V('s12_fall')))
    land = [setv('s12_land', 0), try_land(0), try_land(1), try_land(2),
            ifelse(gt(V('s12_land'), 0),
                   [setv('s12_cur', V('s12_land')), setv('s12_camT', add(LGET('s12_x', cur), 160)), shape('sit'),
                    setv('s12_st', 0), cast('s12착지'), status,
                    if_(eq(cur, N), setv('s12_st', 4), cast('s12골인'), wait(1.2),
                        *m.end_blocks(add(add(mul(N - 1, 7), 15), mul(V('남은시간'), 0.5))))],
                   [setv('s12_st', 3), chg('s12_fall', 1), status, cast('s12풍덩'), hide(), wait(1.0),
                    shape('sit'), show(), setv('s12_st', 0)])]
    frog.on(on_msg('게임시작'),
            until(eq(V('게임중'), 0),
                  chg('s12_cam', mul(sub(V('s12_camT'), V('s12_cam')), 0.14)),
                  if_(le(V('s12_st'), 1), setv('s12_fx', LGET('s12_sx', cur)), xy(V('s12_fx'), FY)),
                  if_(and_(eq(V('s12_st'), 0), key(K_SPACE)), setv('s12_st', 1), setv('s12_t0', timer()), setv('s12_p', 0),
                      setv('s12_dist', 30), cast('s12충전')),
                  if_(eq(V('s12_st'), 1),
                      setv('s12_p', mod(div(sub(timer(), V('s12_t0')), 1.1), 2)),
                      if_(gt(V('s12_p'), 1), setv('s12_p', sub(2, V('s12_p')))),
                      setv('s12_dist', add(30, mul(V('s12_p'), 230))),
                      if_(not_(key(K_SPACE)), setv('s12_st', 2), setv('s12_jx', V('s12_fx')), setv('s12_tj', timer()),
                          shape('jump'), cast('s12점프'))),
                  if_(eq(V('s12_st'), 2),
                      setv('s12_u', div(sub(timer(), V('s12_tj')), 0.5)), if_(gt(V('s12_u'), 1), setv('s12_u', 1)),
                      setv('s12_fx', add(V('s12_jx'), mul(V('s12_dist'), V('s12_u')))),
                      xy(V('s12_fx'), add(FY, mul(280, mul(V('s12_u'), sub(1, V('s12_u')))))),
                      if_(ge(V('s12_u'), 1), *land))))
    ok = m.S('s12골인글', K.big_text('연꽃 도착!', 30, 'green'), 0, 30, visible=False)
    ok.on(on_msg('s12골인'), show())
    mgr = hidden(m, 's12담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(sub(cur, 1), 7)))
    m.on_start(setv('s12_cur', 1), setv('s12_cam', 160), setv('s12_camT', 160), setv('s12_st', 0), setv('s12_fall', 0),
               setv('s12_p', 0), setv('s12_fx', -160))
    m.snd('s12점프', play('jump'))
    m.snd('s12착지', play('pop'))
    m.snd('s12풍덩', play('splash'))
    m.snd('s12골인', play('fanfare'))
    m.finish('스페이스를 누르는 동안 힘이 모이고, 떼면 점프!\n노란 화살표를 보고 움직이는 연잎에 맞춰 뛰세요.',
             '조작: 스페이스 누르기 = 힘 모으기 · 떼기 = 점프  ·  물에 빠지면 그 연잎에서 다시')
    return True
