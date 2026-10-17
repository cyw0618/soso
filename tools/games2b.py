# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 11~20번."""
import random
from games_common import *
import mg_art3 as A3
import mg_art as A

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


# ================================================================== 13. 청사 엘리베이터 (운행 관리)
@game(13)
def g13(P, ctx):
    TL, CAP, PAT = 60, 4, 20
    FL = AB.E13_FLOORS
    CX = 10                                   # 승강기 x
    m = mg(P, ctx, T, 13, time_limit=TL, status='배달 0', dim=70)
    P.list('s13_py', [y + 20 for y in FL])        # 사람 중심 y
    P.list('s13_cyl', [y + 19 for y in FL])       # 승강기 중심 y
    P.list('s13_cnt', [0] * 5)                    # 층별 기다리는 사람
    P.list('s13_qn', [0] * 5)                     # 줄 번호 매기기용
    P.list('s13_ride', [0] * 5)                   # 안에 탄 사람의 목적층별 수
    vars_(P, 's13_cy', 's13_at', 's13_tg', 's13_need', 's13_busy', 's13_load', 's13_done', 's13_angry', 's13_iv',
          's13_last', 's13_dt', 's13_nf', 's13_nd')
    m.S('s13건물', AB.s13_building(), -15, -8)
    car = m.S('s13승강기', [('closed', AB.s13_car('closed')), ('open', AB.s13_car('open'))], CX, FL[0] + 19)
    # 사람 (원본 = 생성 담당, 복제본 = 사람)
    pics = [('p%d' % d, AB.s13_person(d)) for d in range(1, 6)] + [('a%d' % d, AB.s13_person(d, True)) for d in range(1, 6)]
    pp = m.S('s13사람', pics, -300, -300, visible=False)
    for v in ('s13_f', 's13_d', 's13_s', 's13_q', 's13_b', 's13_me'):
        pp.local(v, 0)
    f_, d_, s_, q_ = V('s13_f'), V('s13_d'), V('s13_s'), V('s13_q')
    requeue = [*[lst_set('s13_qn', k, 0) for k in range(1, 6)], cast('s13줄번호')]
    pp.on(on_msg('게임시작'), if_(eq(V('s13_me'), 0),
          setv('s13_iv', 2.6), wait(0.6),
          until(eq(V('게임중'), 0),
                ifelse(le(rnd(1, 100), 45), [setv('s13_f', 1), setv('s13_d', rnd(2, 5))],
                       [setv('s13_f', rnd(2, 5)),
                        ifelse(le(rnd(1, 100), 60), [setv('s13_d', 1)],
                               [setv('s13_d', rnd(2, 5)), until(ne(V('s13_d'), V('s13_f')), setv('s13_d', rnd(2, 5)))])]),
                if_(lt(LGET('s13_cnt', f_), 4), lst_set('s13_cnt', f_, add(LGET('s13_cnt', f_), 1)), clone_self(), cast('s13등장')),
                wait(V('s13_iv')), if_(gt(V('s13_iv'), 1.7), chg('s13_iv', -0.06)))))
    carx = lambda: add(CX - 12, mul(sub(q_, 1), 8))
    pp.on(on_clone(), setv('s13_me', 1), setv('s13_s', 1), setv('s13_q', 9), setv('s13_b', timer()), shape(d_),
          xy(-175, LGET('s13_py', f_)), show(), *requeue,
          until(eq(s_, 9),
                if_(eq(s_, 1),
                    lx(add(obj_x(), mul(sub(sub(-30, mul(sub(q_, 1), 19)), obj_x()), 0.18))),
                    if_(gt(sub(timer(), V('s13_b')), PAT * 0.6), shape(add(d_, 5))),
                    if_(gt(sub(timer(), V('s13_b')), PAT),
                        setv('s13_s', 4), lst_set('s13_cnt', f_, sub(LGET('s13_cnt', f_), 1)), chg('s13_angry', 1),
                        cast('s13화남'), *requeue)),
                if_(eq(s_, 2), xy(carx(), add(V('s13_cy'), 1))),
                if_(eq(s_, 3), mvx(3.2), if_(gt(obj_x(), 128), setv('s13_s', 9))),
                if_(eq(s_, 4), mvx(-3.2), if_(lt(obj_x(), -170), setv('s13_s', 9))),
                if_(eq(V('게임중'), 0), setv('s13_s', 9))),
          del_clone())
    pp.on(on_msg('s13줄번호'), if_(and_(eq(V('s13_me'), 1), eq(s_, 1)),
                                lst_set('s13_qn', f_, add(LGET('s13_qn', f_), 1)), setv('s13_q', LGET('s13_qn', f_))))
    pp.on(on_msg('s13하차'), if_(and_(eq(V('s13_me'), 1), and_(eq(s_, 2), eq(d_, V('s13_at')))),
                              setv('s13_s', 3), lst_set('s13_ride', d_, sub(LGET('s13_ride', d_), 1)), chg('s13_done', 1),
                              ly(LGET('s13_py', d_)), cast('s13배달')))
    pp.on(on_msg('s13재배치'), if_(and_(eq(V('s13_me'), 1), eq(s_, 2)), chg('s13_load', 1), setv('s13_q', V('s13_load'))))
    pp.on(on_msg('s13탑승'), if_(and_(and_(eq(V('s13_me'), 1), eq(s_, 1)), and_(eq(f_, V('s13_at')), lt(V('s13_load'), CAP))),
                              chg('s13_load', 1), setv('s13_q', V('s13_load')), setv('s13_s', 2), shape(d_),
                              lst_set('s13_cnt', f_, sub(LGET('s13_cnt', f_), 1)),
                              lst_set('s13_ride', d_, add(LGET('s13_ride', d_), 1)), cast('s13탐')))
    # 승강기 운행 (시간 기준)
    ty = LGET('s13_cyl', V('s13_tg'))
    car.local('s13_dir', 0)
    status = setv('미니표시', join('배달 ', V('s13_done'), ' · 화남 ', V('s13_angry')))
    car.on(on_msg('게임시작'), setv('s13_last', timer()),
           until(eq(V('게임중'), 0),
                 setv('s13_dt', sub(timer(), V('s13_last'))), setv('s13_last', timer()),
                 if_(gt(V('s13_dt'), 0.1), setv('s13_dt', 0.1)),
                 if_(eq(V('s13_busy'), 0),
                     ifelse(lt(V('s13_cy'), ty), [chg('s13_cy', mul(100, V('s13_dt'))), if_(gt(V('s13_cy'), ty), setv('s13_cy', ty))],
                            [if_(gt(V('s13_cy'), ty), chg('s13_cy', mul(-100, V('s13_dt'))),
                                 if_(lt(V('s13_cy'), ty), setv('s13_cy', ty)))]),
                     ly(V('s13_cy')),
                     setv('s13_at', add(rounded(div(sub(V('s13_cy'), FL[0] + 19), 42)), 1)),
                     if_(and_(eq(V('s13_cy'), ty), eq(V('s13_need'), 1)),
                         setv('s13_need', 0), setv('s13_busy', 1), setv('s13_at', V('s13_tg')),
                         shape('open'), cast('s13열림'), cast('s13하차'), wait(0.35),
                         setv('s13_load', 0), cast('s13재배치'), wait(0.08), cast('s13탑승'), wait(0.45), *requeue,
                         status, wait(0.1), shape('closed'), setv('s13_busy', 0)))))
    # 오른쪽 조작판
    panel(P, m.sc, 's13판', 196, -12, 64, 228, 'glass')
    disp = m.T('s13층표시', ' ', 196, 84, 10, '#FFD27A', F_NUM, False, 0, w=60, h=14)
    disp.on(on_scene(), *G.live_write(disp, setv('_mv', join(V('s13_at'), '층 · ', V('s13_load'), '/', CAP)), '_mv', 0.1))
    for k in range(1, 6):
        b = m.S('s13버튼%d' % k, [(st, AB.s13_button(k, st)) for st in ('off', 'ride', 'go')], 196, -82 + 36 * (k - 1))
        b.local('s13_v', 0)
        b.local('s13_w', 0)
        b.on(on_click(), if_(eq(V('게임중'), 1), setv('s13_tg', k), setv('s13_need', 1), cast('s13누름')),
             b.pct(88), wait(0.06), b.pct(100))
        b.on(on_msg('게임시작'), setv('s13_w', 0),
             until(eq(V('게임중'), 0),
                   setv('s13_v', 1), if_(gt(LGET('s13_ride', k), 0), setv('s13_v', 2)),
                   if_(and_(eq(V('s13_tg'), k), eq(V('s13_need'), 1)), setv('s13_v', 3)),
                   if_(ne(V('s13_v'), V('s13_w')), setv('s13_w', V('s13_v')), shape(V('s13_v'))), wait(0.06)))
        lamp = m.S('s13호출%d' % k, [('off', AB.s13_lamp(0)), ('on', AB.s13_lamp(1))], -124, FL[k - 1] + 12)
        lamp.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ifelse(gt(LGET('s13_cnt', k), 0), [shape('on')], [shape('off')]),
                                        wait(0.15)))
    m.T('s13판글', '층 버튼', 196, -126, 7, C_DIM, F_BODY, True, 0, w=60, h=10)
    tip = m.T('s13도움', '말풍선 숫자 = 가고 싶은 층', -60, -122, 8, C_DIM, F_BODY, True, 0, w=200, h=12)
    plus = m.T('s13득점', '+6', CX + 30, 0, 12, '#FFD27A', F_NUM, False, 0, w=40, h=16, visible=False)
    plus.on(on_msg('s13배달'), ly(add(V('s13_cy'), 26)), show(), rep(10, mvy(1.5), wait(0.03)), hide())
    mgr = hidden(m, 's13담당')
    mgr.on(on_msg('s13화남'), status)
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(V('s13_done'), 6), mul(V('s13_angry'), 2))))
    m.on_start(setv('s13_cy', FL[0] + 19), setv('s13_at', 1), setv('s13_tg', 1), setv('s13_need', 0), setv('s13_busy', 0),
               setv('s13_load', 0), setv('s13_done', 0), setv('s13_angry', 0),
               *[lst_set(nm, k, 0) for nm in ('s13_cnt', 's13_qn', 's13_ride') for k in range(1, 6)])
    m.snd('s13누름', play('click'))
    m.snd('s13열림', play('beep'))
    m.snd('s13배달', play('coin'))
    m.snd('s13화남', play('bad'))
    m.snd('s13등장', play('tick'))
    m.finish('공무원 머리 위 숫자가 가고 싶은 층! 층 버튼을 눌러\n승강기를 보내 태우고 내려 주세요. (최대 4명)',
             '조작: 오른쪽 층 버튼 클릭  ·  주황 버튼 = 안에서 누른 층  ·  오래 기다리면 화나서 가요')
    return True


# ================================================================== 14. 오케스트라 지휘 (지휘)
@game(14)
def g14(P, ctx):
    TEMPI = [('빠르게', 0.45), ('보통', 0.7), ('느리게', 1.0)]
    # (빠르기 번호, 셈여림 1=f 2=p, 박 수)
    secs = [(1, 1, 6), (0, 1, 9), (2, 2, 5), (1, 2, 6), (0, 2, 9), (2, 1, 5), (1, 1, 6), (0, 1, 9)]
    NS = len(secs)
    MAXP = sum(b for _, _, b in secs) * 3
    m = mg(P, ctx, T, 14, status='정확도 -', dim=60)
    P.list('s14_iv', [TEMPI[t][1] for t, _, _ in secs])
    P.list('s14_dy', [d for _, d, _ in secs])
    P.list('s14_nbm', [b for _, _, b in secs])
    P.list('s14_card', [t * 2 + d for t, d, _ in secs] + [7])
    P.list('s14_mel', [1, 2, 3, 3, 4, 3, 2, 1, 2, 3, 4, 4, 3, 2, 3, 1])
    vars_(P, 's14_k', 's14_iv', 's14_dy', 's14_nb', 's14_nbm', 's14_ts', 's14_last', 's14_now', 's14_err', 's14_pts',
          's14_judge', 's14_dok', 's14_cnt', 's14_mi', 's14_tone')
    m.S('s14중앙선', A3.line_img('s14_mid', 400, 4, [(0, 0.5), (1, 0.5)], (180, 190, 230), 1, dash=5), 10, 0)
    m.S('s14위', AB.s14_band('f 세게 ↑', 1), -206, 30)
    m.S('s14아래', AB.s14_band('p 여리게 ↓', 0), -206, -30)
    kinds = ['violin', 'flute', 'drum', 'trumpet', 'cello']
    pos = [(-150, -66), (-75, -48), (0, -40), (75, -48), (150, -66)]
    for k, (kd, (x, y)) in enumerate(zip(kinds, pos)):
        o = m.S('s14연주자%d' % k, [('a', AB.s14_player(kd, 0)), ('b', AB.s14_player(kd, 1))], x, y)
        o.on(on_msg('s14박'), next_shape(), ifelse(eq(V('s14_dy'), 1), [o.pct(116), mvy(5), wait(0.07), mvy(-5)],
                                                  [o.pct(104), wait(0.07)]), o.pct(100))
    cards = [('c%d' % (t * 2 + d), AB.s14_card(TEMPI[t][0], 'f' if d == 1 else 'p')) for t in range(3) for d in (1, 2)]
    cards.append(('end', K.badge('끝', 60, 30, 'royal')))
    cur = m.S('s14악보', cards, 0, 80, visible=False)
    cur.on(on_msg('s14새악장'), shape(LGET('s14_card', V('s14_k'))), cur.pct(115), show(), rep(5, cur.grow_pct(-3), wait(0.016)))
    nxt = m.S('s14다음악보', cards, 160, 80, scale=0.55, visible=False)
    nxt.on(on_msg('s14새악장'), if_(lt(V('s14_k'), NS), shape(LGET('s14_card', add(V('s14_k'), 1))), show()),
           if_(ge(V('s14_k'), NS), hide()))
    m.T('s14다음글', '다음', 160, 98, 7, C_DIM, F_BODY, True, 0, w=40, h=10)
    prog = m.S('s14진행', K.bar_set('s14_prog', 150, 6, 'royal'), 0, 54)
    prog.on(on_msg('s14새악장'), until(or_(eq(V('게임중'), 0), ge(sub(timer(), V('s14_ts')), mul(V('s14_iv'), V('s14_nbm')))),
                                       shape(add(floor(mul(div(sub(timer(), V('s14_ts')), mul(V('s14_iv'), V('s14_nbm'))), 40)), 1)),
                                       wait(0.05)))
    lamp = m.S('s14박자등', A3.disc('s14_lamp', 7, (255, 210, 90)), -92, 80, visible=False)
    lamp.on(on_msg('s14가이드'), show(), wait(0.12), hide())
    m.T('s14박자글', '준비 박자', -92, 66, 7, C_DIM, F_BODY, True, 0, w=50, h=10)
    judge = m.S('s14판정', [('j1', K.big_text('딱 맞아요!', 20, 'royal')), ('j2', K.big_text('좋아요', 18, 'white')),
                           ('j3', K.big_text('빨라요!', 20, 'red')), ('j4', K.big_text('느려요!', 20, 'purple'))], 0, 20, visible=False)
    judge.on(on_msg('s14판정'), shape(V('s14_judge')), judge.pct(80), show(), rep(4, judge.grow_pct(5), wait(0.016)), wait(0.25), hide())
    dynw = m.S('s14셈여림', [('f', K.big_text('위로! 세게 f', 14, 'red')), ('p', K.big_text('아래로! 여리게 p', 14, 'purple'))],
               0, -2, visible=False)
    dynw.on(on_msg('s14판정'), if_(eq(V('s14_dok'), 0), shape(V('s14_dy')), show(), wait(0.4), hide()))
    baton = m.S('s14지휘봉', AB.s14_baton(), 0, 0)
    baton.on(on_msg('게임시작'), until(eq(V('게임중'), 0), xy(add(mouse_x(), 11), add(mouse_y(), 11))))
    baton.on(on_msg('s14박'), rot(-25), wait(0.08), rot(0))
    mgr = hidden(m, 's14담당')
    mgr.on(on_mouse_down(),
           if_(and_(eq(V('게임중'), 1), ge(V('s14_k'), 1)),
               setv('s14_now', sub(timer(), V('s14_last'))), setv('s14_last', timer()), cast('s14박'),
               if_(and_(lt(V('s14_now'), 2.2), lt(V('s14_nb'), V('s14_nbm'))),
                   chg('s14_nb', 1), chg('s14_cnt', 1),
                   setv('s14_err', div(abs_(sub(V('s14_now'), V('s14_iv'))), V('s14_iv'))),
                   ifelse(lt(V('s14_err'), 0.15), [chg('s14_pts', 2), setv('s14_judge', 1)],
                          [ifelse(lt(V('s14_err'), 0.3), [chg('s14_pts', 1), setv('s14_judge', 2)],
                                  [ifelse(lt(V('s14_now'), V('s14_iv')), [setv('s14_judge', 3)], [setv('s14_judge', 4)])])]),
                   setv('s14_dok', 0),
                   if_(or_(and_(eq(V('s14_dy'), 1), gt(mouse_y(), 0)), and_(eq(V('s14_dy'), 2), lt(mouse_y(), 0))),
                       setv('s14_dok', 1), chg('s14_pts', 1)),
                   cast('s14판정'),
                   setv('미니표시', join('정확도 ', rounded(mul(div(V('s14_pts'), mul(V('s14_cnt'), 3)), 100)), '%')))))
    mgr.on(on_msg('게임시작'), setv('s14_k', 0), wait(0.8),
           rep(NS, chg('s14_k', 1), setv('s14_iv', LGET('s14_iv', V('s14_k'))), setv('s14_dy', LGET('s14_dy', V('s14_k'))),
               setv('s14_nbm', LGET('s14_nbm', V('s14_k'))), setv('s14_nb', 0), setv('s14_ts', timer()), cast('s14새악장'),
               cast('s14가이드'), wait(V('s14_iv')), cast('s14가이드'),
               wait(mul(V('s14_iv'), sub(V('s14_nbm'), 1)))),
           setv('s14_k', NS + 1), cast('s14끝'), wait(0.6),
           *m.end_blocks(mul(div(V('s14_pts'), MAXP), 108)))
    mel = m.T('s14멜로디', ' ', -300, -300, 8, visible=False)
    mel.on(on_msg('s14박'), chg('s14_mi', 1), if_(gt(V('s14_mi'), 16), setv('s14_mi', 1)),
           setv('s14_tone', LGET('s14_mel', V('s14_mi'))),
           *[if_(eq(V('s14_tone'), k), cast('s14음%d' % k)) for k in range(1, 5)])
    for k in range(1, 5):
        m.snd('s14음%d' % k, play('tone%d' % k))
    m.on_start(setv('s14_k', 0), setv('s14_pts', 0), setv('s14_cnt', 0), setv('s14_mi', 0), setv('s14_last', 0), setv('s14_dy', 1))
    m.snd('s14가이드', play('tick'))
    m.snd('s14끝', play('fanfare'))
    m.finish('클릭하는 간격이 연주 빠르기! 악보의 빠르게·보통·느리게에\n맞춰 박자를 치고, f 는 위쪽·p 는 아래쪽에서 클릭하세요.',
             '조작: 박자에 맞춰 클릭 (악장 시작 때 노란 등이 2번 박자를 알려 줘요)  ·  f=화면 위쪽, p=아래쪽')
    return True


# ================================================================== 15. 금강 카누 (노 젓기)
@game(15)
def g15(P, ctx):
    TL = 60
    gates = [(300, 0), (520, -80), (740, 60), (960, 110), (1180, -40), (1400, -110), (1620, 20), (1840, 90)]
    NG = len(gates)
    FIN = 2060
    CYS = -70                                  # 카누 화면 y
    HALF = 36                                   # 관문 반폭
    m = mg(P, ctx, T, 15, time_limit=TL, status='관문 0/%d' % NG, dim=0)
    m.S('s15물', A.plain_rect(480, 270, (14, 48, 92, 222), 's15_water'), 0, 0)
    P.list('s15_gy', [g[0] for g in gates])
    P.list('s15_gx', [g[1] for g in gates])
    P.list('s15_gs', [0] * NG)                   # 0 아직 1 통과 2 놓침
    vars_(P, 's15_x', 's15_y', 's15_h', 's15_w', 's15_v', 's15_cur', 's15_dt', 's15_last', 's15_cool', 's15_g', 's15_ok',
          's15_bump', 's15_fin')
    rel = lambda wy: add(sub(wy, V('s15_y')), CYS)
    # 강변 (무늬가 80px 마다 반복)
    for x, fl in ((-221, False), (221, True)):
        b = m.S('s15강변', AB.s15_bank(), x, 0)
        if fl:
            b.on(on_scene(), flip_x())
        b.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ly(sub(mod(V('s15_y'), 80), 40))))
    # 잔물결
    rp = m.S('s15물결', AB.s15_ripple(), 0, -300, visible=False)
    rp.local('s15_rx', 0)
    rp.local('s15_ry', 0)
    rp.local('s15_me', 0)
    rp.on(on_scene(), *[[setv('s15_rx', -150 + (k * 97) % 300), setv('s15_ry', k * 31), clone_self()] for k in range(10)])
    rp.on(on_clone(), setv('s15_me', 1), show(),
          forever(xy(add(V('s15_rx'), mul(12, sin_(add(mul(timer(), 40), V('s15_ry'))))),
                     sub(mod(sub(V('s15_ry'), V('s15_y')), 310), 155))))
    # 물살 화살표 (세계 y 위치·방향 고정)
    arr = m.S('s15물살', AB.s15_arrow(), 0, -300, visible=False)
    arr.local('s15_ay', 0)
    arr.local('s15_me', 0)
    ays = [200 + 260 * k for k in range(8)]
    arr.on(on_scene(), *[[setv('s15_ay', y), clone_self()] for y in ays])
    arr.on(on_clone(), setv('s15_me', 1), ifelse(gt(sin_(mul(V('s15_ay'), 0.35)), 0), [rot(0)], [rot(180)]), show(),
           forever(xy(mul(70, sin_(mul(V('s15_ay'), 0.35))), rel(V('s15_ay')))))
    # 부표 (관문마다 2개)
    bu = m.S('s15부표', [('red', AB.s15_buoy('red')), ('green', AB.s15_buoy('green')), ('gray', AB.s15_buoy('gray'))], 0, -300,
             visible=False)
    for v in ('s15_bi', 's15_bs', 's15_me'):
        bu.local(v, 0)
    bu.on(on_scene(), *[[setv('s15_bi', g), setv('s15_bs', sd), clone_self()] for g in range(1, NG + 1) for sd in (-1, 1)])
    bu.on(on_clone(), setv('s15_me', 1), shape('red'), show(),
          forever(xy(add(LGET('s15_gx', V('s15_bi')), mul(V('s15_bs'), HALF + 4)), rel(LGET('s15_gy', V('s15_bi'))))))
    bu.on(on_msg('s15판정'), if_(and_(eq(V('s15_me'), 1), eq(V('s15_bi'), V('s15_g'))),
                              ifelse(eq(LGET('s15_gs', V('s15_bi')), 1), [shape('green')], [shape('gray')])))
    num = m.T('s15번호', ' ', 0, -300, 9, '#FFE08A', F_NUM, False, 0, w=40, h=14)
    num.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                 if_(le(V('s15_g'), NG), write(join(V('s15_g'), '번')),
                                     xy(LGET('s15_gx', V('s15_g')), add(rel(LGET('s15_gy', V('s15_g'))), 14))),
                                 if_(gt(V('s15_g'), NG), ly(-300))))
    fin = m.S('s15결승', AB.s15_finish(), 0, -300)
    fin.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ly(rel(FIN))))
    canoe = m.S('s15카누', [('c', AB.s15_canoe('c')), ('l', AB.s15_canoe('l')), ('r', AB.s15_canoe('r'))], 0, CYS)
    gy, gx = LGET('s15_gy', V('s15_g')), LGET('s15_gx', V('s15_g'))
    status = setv('미니표시', join('관문 ', V('s15_ok'), '/', NG))
    canoe.on(on_msg('게임시작'), setv('s15_last', timer()),
             until(eq(V('게임중'), 0),
                   setv('s15_dt', sub(timer(), V('s15_last'))), setv('s15_last', timer()),
                   if_(gt(V('s15_dt'), 0.1), setv('s15_dt', 0.1)),
                   chg('s15_h', mul(V('s15_w'), V('s15_dt'))),
                   setv('s15_w', mul(V('s15_w'), sub(1, mul(2.4, V('s15_dt'))))),
                   setv('s15_v', mul(V('s15_v'), sub(1, mul(0.45, V('s15_dt'))))),
                   if_(gt(V('s15_h'), 85), setv('s15_h', 85)), if_(lt(V('s15_h'), -85), setv('s15_h', -85)),
                   chg('s15_x', mul(add(mul(V('s15_v'), sin_(V('s15_h'))), mul(30, sin_(mul(V('s15_y'), 0.35)))), V('s15_dt'))),
                   chg('s15_y', mul(sub(mul(V('s15_v'), cos_(V('s15_h'))), 14), V('s15_dt'))),
                   if_(lt(V('s15_y'), 0), setv('s15_y', 0)),
                   if_(gt(abs_(V('s15_x')), 178),
                       ifelse(gt(V('s15_x'), 0), [setv('s15_x', 178)], [setv('s15_x', -178)]),
                       setv('s15_v', mul(V('s15_v'), 0.5)), if_(lt(V('s15_bump'), timer()), setv('s15_bump', add(timer(), 0.8)),
                                                               cast('s15쿵'))),
                   xy(V('s15_x'), CYS), rot(V('s15_h')),
                   if_(and_(le(V('s15_g'), NG), ge(V('s15_y'), gy)),
                       ifelse(lt(abs_(sub(V('s15_x'), gx)), HALF),
                              [lst_set('s15_gs', V('s15_g'), 1), chg('s15_ok', 1), cast('s15통과')],
                              [lst_set('s15_gs', V('s15_g'), 2), cast('s15놓침')]),
                       cast('s15판정'), status, wait(0.03), chg('s15_g', 1)),
                   if_(and_(eq(V('s15_fin'), 0), ge(V('s15_y'), FIN)), setv('s15_fin', 1), cast('s15골인'), wait(1.0),
                       *m.end_blocks(add(add(mul(V('s15_ok'), 9), 10), mul(V('남은시간'), 0.6))))))
    stroke = lambda sign, pose: if_(and_(eq(V('게임중'), 1), lt(V('s15_cool'), timer())),
                                    setv('s15_cool', add(timer(), 0.28)),
                                    setv('s15_v', add(V('s15_v'), 40)), if_(gt(V('s15_v'), 135), setv('s15_v', 135)),
                                    chg('s15_w', sign * 55), cast('s15노' + pose))
    canoe.on(on_key(K_LEFT), stroke(1, 'l'))
    canoe.on(on_key(K_RIGHT), stroke(-1, 'r'))
    canoe.on(on_msg('s15노l'), shape('l'), wait(0.22), shape('c'))
    canoe.on(on_msg('s15노r'), shape('r'), wait(0.22), shape('c'))
    # 진행 지도
    m.S('s15지도', A3.box('s15_mapbar', 8, 124, (20, 30, 70), rim=(110, 140, 230), r=4), 226, 10)
    dot = m.S('s15지도점', A3.disc('s15_dot', 4, (255, 120, 80)), 226, -50)
    dot.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ly(add(-50, mul(div(V('s15_y'), FIN), 112))), wait(0.1)))
    m.T('s15지도글', '결승', 226, 78, 7, C_DIM, F_BODY, True, 0, w=30, h=10)
    pass_t = m.S('s15통과글', [('ok', K.big_text('통과!', 22, 'green')), ('no', K.big_text('놓쳤어요', 20, 'red'))], 0, 30,
                 visible=False)
    pass_t.on(on_msg('s15통과'), shape('ok'), show(), wait(0.6), hide())
    pass_t.on(on_msg('s15놓침'), shape('no'), show(), wait(0.6), hide())
    gl = m.S('s15골인글', K.big_text('결승 통과!', 30, 'royal'), 0, 20, visible=False)
    gl.on(on_msg('s15골인'), show())
    mgr = hidden(m, 's15담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(mul(V('s15_ok'), 9), mul(div(V('s15_y'), FIN), 10))))
    m.on_start(setv('s15_x', 0), setv('s15_y', 0), setv('s15_h', 0), setv('s15_w', 0), setv('s15_v', 0), setv('s15_g', 1),
               setv('s15_ok', 0), setv('s15_fin', 0), setv('s15_cool', 0), setv('s15_bump', 0),
               *[lst_set('s15_gs', k, 0) for k in range(1, NG + 1)])
    m.snd('s15노l', play('splash'))
    m.snd('s15노r', play('splash'))
    m.snd('s15통과', play('good'))
    m.snd('s15놓침', play('bad'))
    m.snd('s15쿵', play('hit'))
    m.snd('s15골인', play('fanfare'))
    m.finish('← 는 왼쪽 노(오른쪽으로 돌아요), → 는 오른쪽 노!\n번갈아 저으면 곧게 가요. 부표 사이 관문을 지나 결승까지!',
             '조작: ← → 를 번갈아 눌러 노 젓기  ·  한쪽만 저으면 방향이 바뀌어요  ·  화살표 = 물살')
    return True


# ================================================================== 16. 망원경 찾기 (찾기)
@game(16)
def g16(P, ctx):
    TL, Z = 60, 2.5
    kinds = ['rb', 'flag', 'bike', 'bird', 'kite', 'bb', 'gb', 'bflag', 'walk', 'ykite']
    names = ['빨간 풍선', '태극기', '자전거', '까치', '방패연']
    # (모양 번호, x, y, 흔들 폭, 빠르기(도/초), 목표 번호)
    things = [(1, -170, 72, 6, 40, 1), (2, 62, 6, 0, 0, 2), (3, 0, -80, 150, 8, 3), (4, -100, 96, 110, 14, 4), (5, 150, 58, 10, 50, 5),
              (6, -60, 92, 6, 45, 0), (6, 118, 104, 6, 38, 0), (7, 12, 52, 6, 42, 0), (7, -128, 28, 6, 36, 0),
              (8, -152, -14, 0, 0, 0), (8, 172, -10, 0, 0, 0), (9, -100, -86, 30, 10, 0), (9, 40, -98, 40, 12, 0),
              (9, 160, -82, 25, 9, 0), (10, -24, 112, 10, 44, 0)]
    NT = len(things)
    m = mg(P, ctx, T, 16, time_limit=TL, status='찾음 0/5', dim=0)
    for nm, col in (('s16_k', 0), ('s16_wx', 1), ('s16_wy', 2), ('s16_ax', 3), ('s16_sp', 4), ('s16_tg', 5)):
        P.list(nm, [t[col] for t in things])
    P.list('s16_fd', [0] * 5)
    vars_(P, 's16_n', 's16_bad', 's16_cx', 's16_cy', 's16_hit')
    mx, my = mouse_x(), mouse_y()
    pano = m.S('s16전경', ctx['ART']('sj_13'), 0, 0, scale=Z)
    pano.on(on_msg('게임시작'), until(eq(V('게임중'), 0), xy(mul(mx, 1 - Z), mul(my, 1 - Z))))
    th = m.S('s16물건', [(k, AB.s16_thing(k)) for k in kinds], 0, -300, visible=False)
    for v in ('s16_i', 's16_me', 's16_px'):
        th.local(v, 0)
    i_ = V('s16_i')
    th.on(on_scene(), setv('s16_i', 0), rep(NT, chg('s16_i', 1), clone_self()))
    th.on(on_clone(), setv('s16_me', 1), shape(LGET('s16_k', i_)), xy(LGET('s16_wx', i_), LGET('s16_wy', i_)), th.pct(40), show(),
          wait_until(eq(V('게임중'), 1)), th.pct(100),
          until(eq(V('게임중'), 0),
                setv('s16_px', add(LGET('s16_wx', i_), mul(LGET('s16_ax', i_), sin_(add(mul(timer(), LGET('s16_sp', i_)), mul(i_, 40)))))),
                xy(add(mx, mul(sub(V('s16_px'), mx), Z)), add(my, mul(sub(LGET('s16_wy', i_), my), Z)))))
    th.on(on_msg('s16클릭'), if_(and_(eq(V('s16_me'), 1),
                                    lt(add(abs_(sub(obj_x(), V('s16_cx'))), abs_(sub(obj_y(), V('s16_cy')))), 20)),
                                ifelse(gt(LGET('s16_tg', i_), 0),
                                       [if_(eq(LGET('s16_fd', LGET('s16_tg', i_)), 0), lst_set('s16_fd', LGET('s16_tg', i_), 1),
                                            chg('s16_n', 1), setv('s16_hit', 1), cast('s16찾음'),
                                            rep(3, th.pct(140), wait(0.08), th.pct(100), wait(0.08)))],
                                       [setv('s16_hit', 2), cast('s16아님')])))
    scope = m.S('s16망원경', AB.s16_scope(), 0, 0)
    scope.on(on_msg('게임시작'), until(eq(V('게임중'), 0), xy(mx, my)))
    # 목록·지도 (망원경 그림 위)
    panel(P, m.sc, 's16목록판', 204, 24, 70, 146, 'glass')
    m.T('s16목록제목', '찾을 것', 204, 88, 9, '#FFE08A', F_NUM, False, 0, w=60, h=12)
    for k in range(5):
        y = 66 - k * 24
        m.S('s16목록그림%d' % k, AB.s16_thing(kinds[k]), 180, y, scale=0.55)
        m.T('s16목록글%d' % k, names[k], 214, y, 8, C_WHITE, F_BODY, True, 0, w=50, h=12)
        ck = m.S('s16체크%d' % k, AB.check_badge('s16_ok', 7), 236, y + 6, visible=False)
        ck.on(on_msg('s16찾음'), if_(eq(LGET('s16_fd', k + 1), 1), show()))
    mp = m.S('s16지도', ctx['ART']('sj_13'), 190, -100, scale=0.2)
    dot = m.S('s16지도점', A3.ring('s16_ring', 5, (255, 90, 90), 1.5), 190, -100)
    dot.on(on_msg('게임시작'), until(eq(V('게임중'), 0), xy(add(190, mul(mx, 0.2)), add(-100, mul(my, 0.2)))))
    pops = m.S('s16판정', [('ok', K.big_text('찾았다!', 24, 'green')), ('no', K.big_text('그건 아니에요', 16, 'red'))], 0, 0,
               visible=False)
    pops.on(on_msg('s16찾음'), shape('ok'), xy(mx, add(my, 48)), show(), wait(0.6), hide())
    pops.on(on_msg('s16아님'), shape('no'), xy(mx, add(my, 48)), show(), wait(0.5), hide())
    status = setv('미니표시', join('찾음 ', V('s16_n'), '/5'))
    mgr = hidden(m, 's16담당')
    mgr.on(on_mouse_down(), if_(eq(V('게임중'), 1), setv('s16_cx', mx), setv('s16_cy', my), setv('s16_hit', 0), cast('s16클릭')))
    mgr.on(on_msg('s16찾음'), status, if_(ge(V('s16_n'), 5), wait(0.8),
                                        *m.end_blocks(sub(add(80, mul(V('남은시간'), 0.5)), mul(V('s16_bad'), 2)))))
    mgr.on(on_msg('s16아님'), chg('s16_bad', 1))
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(V('s16_n'), 16), mul(V('s16_bad'), 2))))
    m.on_start(setv('s16_n', 0), setv('s16_bad', 0), *[lst_set('s16_fd', k, 0) for k in range(1, 6)])
    m.snd('s16찾음', play('shutter'))
    m.snd('s16아님', play('bad'))
    m.finish('원수산 전망대 망원경으로 세종시를 살펴보세요!\n목록의 5가지를 찾아 망원경 가운데에 두고 클릭!',
             '조작: 마우스로 망원경 움직이기 · 클릭 = 찾았다!  ·  오른쪽 아래 작은 지도 = 지금 보는 곳')
    return True


# ================================================================== 17. 다리 조명 기억 (공간 기억)
@game(17)
def g17(P, ctx):
    TL, N, CL = 100, 5, 38
    m = mg(P, ctx, T, 17, time_limit=TL, status='3칸 · ♥3', dim=60)
    P.list('s17_on', [0] * 25)
    P.list('s17_st', [0] * 25)
    P.list('s17_seq', [0] * 8)
    vars_(P, 's17_lv', 's17_ph', 's17_hit', 's17_miss', 's17_life', 's17_cur', 's17_clr', 's17_c', 's17_k', 's17_j')
    panel(P, m.sc, 's17판', 0, -14, 208, 208, 'glass')
    cell = m.S('s17조명', [(st, AB.s17_cell(st)) for st in ('off', 'on', 'ok', 'bad', 'miss')], 0, -300, visible=False)
    cell.local('s17_i', 0)
    cell.local('s17_me', 0)
    i_ = V('s17_i')
    cell.on(on_scene(), setv('s17_i', 0), rep(25, chg('s17_i', 1), clone_self()))
    cell.on(on_clone(), setv('s17_me', 1), shape('off'),
            xy(add(-2 * CL, mul(mod(sub(i_, 1), N), CL)), sub(62, mul(floor(div(sub(i_, 1), N)), CL))), show())
    me = eq(V('s17_me'), 1)
    cell.on(on_msg('s17끄기'), if_(me, shape('off')))
    cell.on(on_msg('s17한칸'), if_(and_(me, eq(i_, V('s17_cur'))), shape('on'), cell.pct(118), wait(0.08), cell.pct(100)))
    cell.on(on_msg('s17정답'), if_(and_(me, and_(eq(LGET('s17_on', i_), 1), ne(LGET('s17_st', i_), 1))), shape('miss')))
    cell.on(on_click(), if_(and_(me, and_(eq(V('s17_ph'), 2), eq(LGET('s17_st', i_), 0))),
                            ifelse(eq(LGET('s17_on', i_), 1),
                                   [lst_set('s17_st', i_, 1), chg('s17_hit', 1), shape('ok'), cast('s17딩')],
                                   [lst_set('s17_st', i_, 2), chg('s17_miss', 1), shape('bad'), cast('s17삑')]),
                            cell.pct(88), wait(0.06), cell.pct(100)))
    info = m.T('s17안내', ' ', 0, 92, 10, '#FFE08A', F_NUM, False, 0, w=240, h=14)
    info.on(on_msg('s17보기'), write(join(V('s17_lv'), '칸이 켜져요. 잘 보세요!')))
    info.on(on_msg('s17입력'), write('켜졌던 칸을 모두 누르세요! (실수 2번까지)'))
    side = m.T('s17정보', ' ', 172, 10, 10, C_WHITE, F_BODY, True, 0, w=110, h=60)
    status = [setv('미니표시', join(V('s17_lv'), '칸 · ♥', V('s17_life'))),
              setv('_mv', join('단계 ', sub(V('s17_lv'), 2), ' / 6\n목숨 ♥', V('s17_life'), '\n기억한 칸 ', V('s17_clr')))]
    side.on(on_msg('s17정보'), write(V('_mv')))
    okp = m.S('s17결과', [('ok', K.big_text('완벽해요!', 28, 'royal')), ('no', K.big_text('아쉬워요', 26, 'red'))], 0, -14,
              visible=False)
    okp.on(on_msg('s17성공'), shape('ok'), show(), wait(0.8), hide())
    okp.on(on_msg('s17실패'), wait(0.6), shape('no'), show(), wait(0.7), hide())
    mgr = hidden(m, 's17담당')
    mgr.on(on_msg('게임시작'), setv('s17_lv', 3), setv('s17_life', 3), *status, cast('s17정보'),
           until(or_(gt(V('s17_lv'), 8), or_(le(V('s17_life'), 0), eq(V('게임중'), 0))),
                 *[lst_set('s17_on', k, 0) for k in range(1, 26)], *[lst_set('s17_st', k, 0) for k in range(1, 26)],
                 setv('s17_c', 0),
                 until(ge(V('s17_c'), V('s17_lv')), setv('s17_k', rnd(1, 25)),
                       if_(eq(LGET('s17_on', V('s17_k')), 0), lst_set('s17_on', V('s17_k'), 1), chg('s17_c', 1),
                           lst_set('s17_seq', V('s17_c'), V('s17_k')))),
                 setv('s17_ph', 1), cast('s17끄기'), cast('s17보기'), wait(0.7), setv('s17_j', 0),
                 rep(V('s17_lv'), chg('s17_j', 1), setv('s17_cur', LGET('s17_seq', V('s17_j'))), cast('s17한칸'), cast('s17띵'),
                     wait(0.45)),
                 wait(0.8), cast('s17끄기'), setv('s17_hit', 0), setv('s17_miss', 0), setv('s17_ph', 2), cast('s17입력'),
                 wait_until(or_(ge(V('s17_hit'), V('s17_lv')), or_(ge(V('s17_miss'), 2), eq(V('게임중'), 0)))),
                 setv('s17_ph', 0),
                 ifelse(ge(V('s17_hit'), V('s17_lv')),
                        [chg('s17_clr', V('s17_lv')), chg('s17_lv', 1), cast('s17성공'), wait(1.0)],
                        [chg('s17_life', -1), cast('s17정답'), cast('s17실패'), wait(1.6)]),
                 *status, cast('s17정보')),
           *m.end_blocks(add(mul(V('s17_clr'), 3), mul(V('남은시간'), 0.1))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('s17_clr'), 3)))
    m.on_start(setv('s17_lv', 3), setv('s17_life', 3), setv('s17_ph', 0), setv('s17_clr', 0),
               *[lst_set('s17_on', k, 0) for k in range(1, 26)])
    m.snd('s17띵', play('tone2'))
    m.snd('s17딩', play('pop'))
    m.snd('s17삑', play('bad'))
    m.snd('s17성공', play('good'))
    m.snd('s17실패', play('fail_big'))
    m.finish('이응다리 조명이 한 칸씩 켜졌다가 모두 꺼져요.\n켜졌던 칸을 순서 상관없이 모두 누르세요! (3칸 → 8칸)',
             '조작: 칸 클릭  ·  한 단계에 실수 2번이면 목숨 -1 (목숨 3개)')
    return True


# ================================================================== 18. 윷놀이 한 판 (보드게임)
def _yut_nodes(h):
    pos = {}
    for i in range(20):
        side, k = divmod(i, 5)
        f = 2 * h * k / 5
        pos[i] = [(h, -h + f), (h - f, h), (-h, h - f), (-h + f, -h)][side]
    pos[20] = (h, -h)
    for j, nid in enumerate((21, 22, 23, 24, 25)):
        f = 2 * h * (j + 1) / 6
        pos[nid] = (h - f, h - f)
    for j, nid in enumerate((26, 27, 30, 28, 29)):
        f = 2 * h * (j + 1) / 6
        pos[nid] = (-h + f, h - f)
    nxt = {i: i + 1 for i in range(19)}
    nxt.update({19: 20, 20: 20, 21: 22, 22: 23, 23: 24, 24: 25, 25: 15, 26: 27, 27: 30, 30: 28, 28: 29, 29: 20})
    short = dict(nxt)
    short.update({5: 21, 10: 26, 23: 28})
    dist = {}
    for i in range(31):
        q, n = short[i], 1
        while q != 20 and n < 40:
            q, n = nxt[q], n + 1
        dist[i] = 0 if i == 20 else n
    return pos, nxt, short, dist


@game(18)
def g18(P, ctx):
    TL = 120
    BX, BY, H = -62, -14, 82
    pos, nxt, short, dist = _yut_nodes(H)
    m = mg(P, ctx, T, 18, time_limit=TL, status='나 0 : 0 이장님', dim=90)
    P.list('s18_nx', [BX + pos[i][0] for i in range(31)])
    P.list('s18_ny', [BY + pos[i][1] for i in range(31)])
    P.list('s18_next', [nxt[i] for i in range(31)])
    P.list('s18_short', [short[i] for i in range(31)])
    P.list('s18_spot', [23 if i == 30 else i for i in range(31)])
    P.list('s18_dist', [dist[i] for i in range(31)])
    P.list('s18_pos', [0, 0, 0, 0])
    P.list('s18_flat', [1, 2, 3, 4, 0])
    vars_(P, 's18_turn', 's18_ph', 's18_r', 's18_pick', 's18_q', 's18_k', 's18_capt', 's18_win', 's18_sa', 's18_sb', 's18_o',
          's18_home1', 's18_home2')
    nodes = [(pos[i][0], pos[i][1], i in (0, 5, 10, 15, 23)) for i in list(range(20)) + [21, 22, 23, 24, 25, 26, 27, 28, 29]]
    m.S('s18판', AB.s18_board(nodes, 2 * H + 36), BX, BY)
    PP = lambda p: LGET('s18_pos', p)
    NX = lambda e: LGET('s18_nx', add(e, 1))
    NY = lambda e: LGET('s18_ny', add(e, 1))
    SPOT = lambda e: LGET('s18_spot', add(e, 1))
    # 오른쪽: 선수 카드
    m.S('s18나', ctx['PORT']['me'], 84, 76, scale=0.9)
    m.S('s18이장', AB.s18_elder(), 176, 76, scale=0.8)
    m.T('s18나글', '나', 84, 56, 8, C_WHITE, F_NUM, False, 0, w=30, h=10)
    m.T('s18이장글', '이장님', 176, 56, 8, C_WHITE, F_NUM, False, 0, w=40, h=10)
    m.T('s18도착1', '도착', 121, 92, 7, C_DIM, F_BODY, True, 0, w=30, h=10)
    m.T('s18도착2', '도착', 213, 92, 7, C_DIM, F_BODY, True, 0, w=30, h=10)
    slot0 = {1: (72, 40), 2: (96, 40), 3: (164, 40), 4: (188, 40)}
    slot20 = {1: (112, 76), 2: (130, 76), 3: (204, 76), 4: (222, 76)}
    offs = {1: (-3, 3), 2: (3, 3), 3: (-3, -3), 4: (3, -3)}
    pieces = {}
    for p in range(1, 5):
        who, n = ('me', p) if p <= 2 else ('ai', p - 2)
        o = m.S('s18말%d' % p, AB.s18_piece(who, n), *slot0[p])
        o.local('s18_tx', 0)
        o.local('s18_ty', 0)
        o.on(on_scene(), xy(*slot0[p]),
             forever(ifelse(eq(PP(p), 0), [setv('s18_tx', slot0[p][0]), setv('s18_ty', slot0[p][1])],
                            [ifelse(eq(PP(p), 20), [setv('s18_tx', slot20[p][0]), setv('s18_ty', slot20[p][1])],
                                    [setv('s18_tx', add(NX(PP(p)), offs[p][0])), setv('s18_ty', add(NY(PP(p)), offs[p][1]))])]),
                     xy(add(obj_x(), mul(sub(V('s18_tx'), obj_x()), 0.35)), add(obj_y(), mul(sub(V('s18_ty'), obj_y()), 0.35)))))
        if p <= 2:
            o.on(on_click(), if_(and_(eq(V('s18_ph'), 2), ne(PP(p), 20)), setv('s18_pick', p)))
            o.on(on_msg('s18고르기'), if_(ne(PP(p), 20), until(ne(V('s18_ph'), 2), o.pct(125), wait(0.15), o.pct(100), wait(0.15))))
        pieces[p] = o
    # 윷가락
    for k in range(1, 5):
        st = m.S('s18윷%d' % k, [('round', AB.s18_stick(0)), ('flat', AB.s18_stick(1))], 104 + 28 * k, 4)
        st.on(on_msg('s18던지기'), rep(8, shape(rnd(1, 2)), rot(rnd(-25, 25)), mvy(rnd(-4, 4)), wait(0.07)), rot(0), ly(4),
              ifelse(le(k, LGET('s18_flat', V('s18_r'))), [shape('flat')], [shape('round')]))
    res = m.S('s18결과', [(nm, K.big_text(t, 22, c)) for nm, t, c in
                         (('do', '도! (1칸)', 'white'), ('gae', '개! (2칸)', 'white'), ('geol', '걸! (3칸)', 'royal'),
                          ('yut', '윷! 한 번 더', 'green'), ('mo', '모! 한 번 더', 'green'))], 166, -40, visible=False)
    res.on(on_msg('s18결과'), shape(V('s18_r')), res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.016)))
    res.on(on_msg('s18던지기'), hide())
    capt = m.S('s18잡기', K.big_text('잡았다! 한 번 더', 18, 'red'), BX, BY, visible=False)
    capt.on(on_msg('s18잡음'), show(), wait(0.9), hide())
    turn_t = m.T('s18차례', ' ', 160, -106, 9, '#FFE08A', F_NUM, False, 0, w=160, h=14)
    turn_t.on(on_msg('s18안내'), ifelse(eq(V('s18_ph'), 2), [write('움직일 내 말(파랑)을 누르세요')],
                                      [ifelse(eq(V('s18_turn'), 1), [write('내 차례! 윷을 던지세요')], [write('이장님 차례...')])]))
    throw_b = button(P, m.sc, 's18던지기버튼', '윷 던지기', 160, -76, 110, 28, 'royal',
                     actions=[if_(and_(eq(V('게임중'), 1), and_(eq(V('s18_turn'), 1), eq(V('s18_ph'), 0))), setv('s18_ph', 1))])
    # 담당: 한 턴씩
    def sim(p, out):
        return [setv(out, LGET('s18_short', add(PP(p), 1))), rep(sub(V('s18_r'), 1), setv(out, LGET('s18_next', add(V(out), 1))))]

    def ai_score(p, out):
        mine = [if_(and_(and_(ne(PP(q), 0), ne(PP(q), 20)), eq(SPOT(V('s18_q')), SPOT(PP(q)))), chg(out, 60)) for q in (1, 2)]
        return [ifelse(eq(PP(p), 20), [setv(out, -999)],
                       [*sim(p, 's18_q'), setv(out, sub(0, LGET('s18_dist', add(V('s18_q'), 1)))),
                        if_(eq(V('s18_q'), 20), chg(out, 40)), *mine,
                        if_(or_(eq(V('s18_q'), 5), or_(eq(V('s18_q'), 10), eq(V('s18_q'), 23))), chg(out, 8))])]
    mover = V('s18_pick')

    def capture_of(qs):
        return [if_(and_(and_(ne(PP(q), 0), ne(PP(q), 20)), eq(SPOT(PP(q)), SPOT(PP(mover)))), lst_set('s18_pos', q, 0),
                    setv('s18_capt', 1)) for q in qs]
    status = [setv('s18_home1', 0), setv('s18_home2', 0),
              *[if_(eq(PP(q), 20), chg('s18_home1' if q <= 2 else 's18_home2', 1)) for q in range(1, 5)],
              setv('미니표시', join('나 ', V('s18_home1'), ' : ', V('s18_home2'), ' 이장님'))]
    mydist = add(LGET('s18_dist', add(PP(1), 1)), LGET('s18_dist', add(PP(2), 1)))
    aidist = add(LGET('s18_dist', add(PP(3), 1)), LGET('s18_dist', add(PP(4), 1)))
    turn = [ifelse(eq(V('s18_turn'), 1), [setv('s18_ph', 0), cast('s18안내'), wait_until(or_(eq(V('s18_ph'), 1), eq(V('게임중'), 0)))],
                   [setv('s18_ph', 1), cast('s18안내'), wait(0.7)]),
            setv('s18_k', rnd(1, 100)),
            ifelse(le(V('s18_k'), 15), [setv('s18_r', 1)], [ifelse(le(V('s18_k'), 50), [setv('s18_r', 2)],
                   [ifelse(le(V('s18_k'), 84), [setv('s18_r', 3)], [ifelse(le(V('s18_k'), 96), [setv('s18_r', 4)], [setv('s18_r', 5)])])])]),
            cast('s18던지기'), wait(0.7), cast('s18결과'), wait(0.6),
            setv('s18_pick', 0),
            ifelse(eq(V('s18_turn'), 1),
                   [ifelse(eq(PP(1), 20), [setv('s18_pick', 2)],
                           [ifelse(or_(eq(PP(2), 20), eq(PP(1), PP(2))), [setv('s18_pick', 1)],
                                   [setv('s18_ph', 2), cast('s18고르기'), cast('s18안내'),
                                    wait_until(or_(gt(V('s18_pick'), 0), eq(V('게임중'), 0)))])])],
                   [*ai_score(3, 's18_sa'), *ai_score(4, 's18_sb'),
                    ifelse(ge(V('s18_sa'), V('s18_sb')), [setv('s18_pick', 3)], [setv('s18_pick', 4)]), wait(0.3)]),
            if_(gt(V('s18_pick'), 0),
                setv('s18_ph', 3), cast('s18안내'),
                lst_set('s18_pos', mover, LGET('s18_short', add(PP(mover), 1))), cast('s18톡'), wait(0.2),
                rep(sub(V('s18_r'), 1), if_(ne(PP(mover), 20), lst_set('s18_pos', mover, LGET('s18_next', add(PP(mover), 1))),
                                            cast('s18톡'), wait(0.2))),
                setv('s18_capt', 0),
                if_(ne(PP(mover), 20), ifelse(le(mover, 2), capture_of((3, 4)), capture_of((1, 2)))),
                if_(eq(V('s18_capt'), 1), cast('s18잡음'), wait(0.6)),
                *status,
                if_(and_(eq(PP(1), 20), eq(PP(2), 20)), setv('s18_win', 1)),
                if_(and_(eq(PP(3), 20), eq(PP(4), 20)), setv('s18_win', 2)),
                if_(and_(lt(V('s18_r'), 4), eq(V('s18_capt'), 0)), setv('s18_turn', sub(3, V('s18_turn')))),
                wait(0.3))]
    mgr = hidden(m, 's18담당')
    mgr.on(on_msg('게임시작'), setv('s18_turn', 1),
           until(or_(gt(V('s18_win'), 0), eq(V('게임중'), 0)), *turn),
           if_(eq(V('s18_win'), 1), cast('s18승리'), wait(1.4), *m.end_blocks(add(75, mul(aidist, 0.6)))),
           if_(eq(V('s18_win'), 2), cast('s18패배'), wait(1.4), *m.end_blocks(sub(50, mul(mydist, 1.2)))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(50, mul(sub(aidist, mydist), 1.5))))
    endp = m.S('s18끝글', [('w', K.big_text('내가 이겼다!', 30, 'royal')), ('l', K.big_text('이장님 승리...', 28, 'red'))], BX, BY,
               visible=False)
    endp.on(on_msg('s18승리'), shape('w'), show())
    endp.on(on_msg('s18패배'), shape('l'), show())
    m.on_start(setv('s18_turn', 1), setv('s18_ph', 0), setv('s18_win', 0), setv('s18_r', 1), *[lst_set('s18_pos', k, 0) for k in range(1, 5)])
    m.snd('s18던지기', play('drumroll'))
    m.snd('s18톡', play('tick'))
    m.snd('s18잡음', play('hit'))
    m.snd('s18승리', play('fanfare'))
    m.snd('s18패배', play('fail_big'))
    m.finish('마을회관 이장님과 윷놀이! 말 2개를 먼저 한 바퀴 돌려\n도착하면 승리. 모서리에 멈추면 지름길, 잡으면 한 번 더!',
             '조작: "윷 던지기" 클릭 → 움직일 내 말(파랑) 클릭  ·  윷·모는 한 번 더 던져요')
    return True


# ================================================================== 19. 굴렁쇠 굴리기 (균형)
@game(19)
def g19(P, ctx):
    TL, GOAL, HZ, HY = 45, 160, 40, -40
    m = mg(P, ctx, T, 19, time_limit=TL, status='0m / %dm' % GOAL, dim=40)
    vars_(P, 's19_th', 's19_w', 's19_x', 's19_v', 's19_d', 's19_dt', 's19_last', 's19_gust', 's19_fall', 's19_down', 's19_fin')
    m.S('s19길', AB.s19_road(), 0, HZ - 75)
    cam = sub(V('s19_d'), 3.5)

    def persp(o, lat):
        """세계 거리 s19_W, 옆 위치 lat → 화면 (local s19_s 사용)."""
        return [setv('s19_s', div(1, add(1, mul(sub(V('s19_W'), cam), 0.25)))),
                xy(mul(lat, mul(V('s19_s'), 1.875)), sub(HZ, mul(150, V('s19_s')))), o.pct(mul(V('s19_s'), 187.5))]
    dash = m.S('s19선', AB.s19_dash(), 0, -300, visible=False)
    for v in ('s19_W', 's19_s', 's19_me'):
        dash.local(v, 0)
    dash.on(on_scene(), *[[setv('s19_W', 3 + 5 * k), clone_self()] for k in range(6)])
    dash.on(on_clone(), setv('s19_me', 1), show(),
            forever(if_(lt(sub(V('s19_W'), cam), 0.4), chg('s19_W', 30)), *persp(dash, 0)))
    st = m.S('s19돌', AB.s19_stone(), 0, -300, visible=False)
    for v in ('s19_W', 's19_s', 's19_me', 's19_lat', 's19_pd'):
        st.local(v, 0)
    st.on(on_scene(), *[[setv('s19_W', 14 + 11 * k), setv('s19_lat', [-50, 40, 0][k]), clone_self()] for k in range(3)])
    st.on(on_clone(), setv('s19_me', 1), show(), setv('s19_pd', 99),
          forever(if_(lt(sub(V('s19_W'), cam), 0.4), chg('s19_W', add(28, rnd(0, 10))), setv('s19_lat', rnd(-85, 85)), setv('s19_pd', 99)),
                  *persp(st, V('s19_lat')),
                  if_(and_(gt(V('s19_pd'), 3.5), le(sub(V('s19_W'), cam), 3.5)),
                      if_(and_(lt(abs_(sub(V('s19_lat'), V('s19_x'))), 20), eq(V('s19_down'), 0)),
                          ifelse(gt(V('s19_x'), V('s19_lat')), [chg('s19_w', 75)], [chg('s19_w', -75)]), cast('s19쿵'))),
                  setv('s19_pd', sub(V('s19_W'), cam))))
    kid = m.S('s19아이', [('a', AB.s19_kid(0)), ('b', AB.s19_kid(1))], 0, -100)
    hoop = m.S('s19굴렁쇠', AB.s19_hoop(), 0, HY)
    kid.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(mul(V('s19_x'), 1.15)),
                                  if_(eq(V('s19_down'), 0), next_shape()), wait(div(0.9, add(V('s19_v'), 2)))))
    status = setv('미니표시', join(floor(V('s19_d')), 'm / ', GOAL, 'm'))
    hoop.on(on_msg('게임시작'), setv('s19_last', timer()), setv('s19_gust', add(timer(), 1)),
            until(eq(V('게임중'), 0),
                  setv('s19_dt', sub(timer(), V('s19_last'))), setv('s19_last', timer()),
                  if_(gt(V('s19_dt'), 0.1), setv('s19_dt', 0.1)),
                  chg('s19_w', mul(add(mul(V('s19_th'), 2.4), 0), V('s19_dt'))),
                  if_(key(K_LEFT), chg('s19_w', mul(-150, V('s19_dt')))),
                  if_(key(K_RIGHT), chg('s19_w', mul(150, V('s19_dt')))),
                  if_(gt(timer(), V('s19_gust')), setv('s19_gust', add(timer(), div(rnd(8, 18), 10))),
                      chg('s19_w', mul(rnd(-1, 1), rnd(8, 22)))),
                  setv('s19_w', mul(V('s19_w'), sub(1, mul(0.6, V('s19_dt'))))),
                  chg('s19_th', mul(V('s19_w'), V('s19_dt'))),
                  chg('s19_x', mul(mul(V('s19_th'), 3), V('s19_dt'))),
                  setv('s19_v', add(V('s19_v'), mul(0.9, V('s19_dt')))), if_(gt(V('s19_v'), 7), setv('s19_v', 7)),
                  chg('s19_d', mul(V('s19_v'), V('s19_dt'))),
                  xy(V('s19_x'), HY), rot(V('s19_th')), status,
                  if_(or_(gt(abs_(V('s19_th')), 40), gt(abs_(V('s19_x')), 112)),
                      setv('s19_down', 1), chg('s19_fall', 1), cast('s19넘어짐'),
                      ifelse(gt(V('s19_th'), 0), [rep(8, rot_by(6), mvy(-2), wait(0.03))], [rep(8, rot_by(-6), mvy(-2), wait(0.03))]),
                      wait(0.9), if_(gt(abs_(V('s19_x')), 100), setv('s19_x', 0)),
                      setv('s19_th', mul(rnd(-1, 1), 3)), setv('s19_w', 0), setv('s19_v', 1), setv('s19_last', timer()),
                      setv('s19_down', 0)),
                  if_(ge(V('s19_d'), GOAL), setv('s19_fin', 1), cast('s19골인'), wait(1.0),
                      *m.end_blocks(add(80, mul(V('남은시간'), 1.2))))))
    m.S('s19눈금', AB.s19_gauge(), 0, 84)
    nd = m.S('s19바늘', AB.s19_needle(), 0, 92)
    nd.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(mul(V('s19_th'), 2.5)), wait(0.02)))
    m.T('s19눈금글', '기울기', -122, 84, 8, C_DIM, F_BODY, True, 0, w=40, h=10)
    fall_t = m.S('s19넘어짐글', K.big_text('넘어졌다!', 26, 'red'), 0, 10, visible=False)
    fall_t.on(on_msg('s19넘어짐'), show(), wait(0.9), hide())
    gl = m.S('s19골인글', K.big_text('완주!', 34, 'royal'), 0, 10, visible=False)
    gl.on(on_msg('s19골인'), show())
    mgr = hidden(m, 's19담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(div(V('s19_d'), GOAL), 80)))
    m.on_start(setv('s19_th', 2), setv('s19_w', 0), setv('s19_x', 0), setv('s19_v', 1), setv('s19_d', 0), setv('s19_fall', 0),
               setv('s19_down', 0), setv('s19_fin', 0))
    m.snd('s19쿵', play('hit'))
    m.snd('s19넘어짐', play('fail_big'))
    m.snd('s19골인', play('fanfare'))
    m.finish('굴렁쇠가 기울면 그쪽으로 굴러가요. ← → 로 반대쪽을\n살짝 밀어 균형을 잡고 160m 를 달리세요! 돌을 조심!',
             '조작: ← → 누르고 있기 = 그쪽으로 기울이기  ·  위쪽 눈금 바늘을 가운데로  ·  길 밖 = 넘어짐')
    return True


# ================================================================== 20. 정원 노노그램 (논리 퍼즐)
@game(20)
def g20(P, ctx):
    TL = 120
    puz = [('하트', ['01010', '11111', '11111', '01110', '00100']), ('튤립', ['10101', '11111', '01110', '00100', '01110']),
           ('집', ['00100', '01110', '11111', '01010', '01110'])]
    NPZ = len(puz)

    def runs(r):
        out, c = [], 0
        for v in r:
            if v:
                c += 1
            elif c:
                out.append(c)
                c = 0
        if c:
            out.append(c)
        return out or [0]
    sol, rcl, ccl, rwi, cwi, ones = [], [], [], [], [], []
    for nm, g in puz:
        G = [[int(ch) for ch in r] for r in g]
        sol += [v for r in G for v in r]
        rcl += [' '.join(map(str, runs(r))) for r in G]
        ccl += ['\n'.join(map(str, runs([G[r][c] for r in range(5)]))) for c in range(5)]
        rwi += [sum(r) for r in G]
        cwi += [sum(G[r][c] for r in range(5)) for c in range(5)]
        ones.append(sum(map(sum, G)))
    m = mg(P, ctx, T, 20, time_limit=TL, status='그림 1/%d' % NPZ, dim=70)
    for nm, vals in (('s20_sol', sol), ('s20_rc', rcl), ('s20_cc', ccl), ('s20_rwi', rwi), ('s20_cwi', cwi), ('s20_ones', ones),
                     ('s20_name', [p[0] for p in puz])):
        P.list(nm, vals)
    P.list('s20_st', [0] * 25)
    P.list('s20_rw', [0] * 5)
    P.list('s20_cw', [0] * 5)
    vars_(P, 's20_n', 's20_wrong', 's20_mode', 's20_lock', 's20_solved')
    GX, GY, CL = 10, -30, 30
    xs = [GX - 2 * CL + CL * c for c in range(5)]
    ys = [GY + 2 * CL - CL * r for r in range(5)]
    panel(P, m.sc, 's20판', -14, -6, 250, 204, 'glass')
    base = mul(sub(V('s20_n'), 1), 5)
    for r in range(5):
        t = m.T('s20행%d' % r, ' ', -96, ys[r], 11, C_WHITE, F_NUM, False, 2, w=56, h=16)
        t.on(on_msg('s20새퍼즐'), write(LGET('s20_rc', add(base, r + 1))))
        t.on(on_msg('s20단서'), ifelse(eq(LGET('s20_rw', r + 1), 0), [text_color('#6F7A99')], [text_color('#FFFFFF')]))
    for c in range(5):
        t = m.T('s20열%d' % c, ' ', xs[c], 66, 11, C_WHITE, F_NUM, False, 0, w=24, h=40)
        t.on(on_msg('s20새퍼즐'), write(LGET('s20_cc', add(base, c + 1))))
        t.on(on_msg('s20단서'), ifelse(eq(LGET('s20_cw', c + 1), 0), [text_color('#6F7A99')], [text_color('#FFFFFF')]))
    cell = m.S('s20칸', [('e', AB.s20_cell('e')), ('f', AB.s20_cell('f')), ('x', AB.s20_cell('x'))], 0, -300, visible=False)
    for v in ('s20_i', 's20_me', 's20_o', 's20_nw', 's20_dd'):
        cell.local(v, 0)
    i_ = V('s20_i')
    cell.on(on_scene(), setv('s20_i', 0), rep(25, chg('s20_i', 1), clone_self()))
    cell.on(on_clone(), setv('s20_me', 1), shape('e'),
            xy(add(xs[0], mul(mod(sub(i_, 1), 5), CL)), sub(ys[0], mul(floor(div(sub(i_, 1), 5)), CL))), show())
    me = eq(V('s20_me'), 1)
    cell.on(on_msg('s20새퍼즐'), if_(me, shape('e')))
    cell.on(on_msg('s20완성'), if_(me, ifelse(eq(LGET('s20_sol', add(base, i_)), 1), [shape('f'), cell.pct(115), wait(0.1), cell.pct(100)],
                                             [shape('e')])))
    ri, ci = add(floor(div(sub(i_, 1), 5)), 1), add(mod(sub(i_, 1), 5), 1)
    upd = lambda d: [chg('s20_wrong', d), lst_set('s20_rw', ri, add(LGET('s20_rw', ri), d)), lst_set('s20_cw', ci, add(LGET('s20_cw', ci), d))]
    is_sol = eq(LGET('s20_sol', add(base, i_)), 1)
    cell.on(on_click(), if_(and_(me, and_(eq(V('게임중'), 1), eq(V('s20_lock'), 0))),
                            setv('s20_o', LGET('s20_st', i_)),
                            ifelse(eq(V('s20_mode'), 0), [ifelse(eq(V('s20_o'), 1), [setv('s20_nw', 0)], [setv('s20_nw', 1)])],
                                   [ifelse(eq(V('s20_o'), 2), [setv('s20_nw', 0)], [setv('s20_nw', 2)])]),
                            if_(and_(eq(V('s20_o'), 1), ne(V('s20_nw'), 1)), ifelse(is_sol, upd(1), upd(-1))),
                            if_(and_(ne(V('s20_o'), 1), eq(V('s20_nw'), 1)), ifelse(is_sol, upd(-1), upd(1))),
                            lst_set('s20_st', i_, V('s20_nw')), shape(add(V('s20_nw'), 1)),
                            ifelse(eq(V('s20_nw'), 1), [cast('s20심기')], [cast('s20딸깍')]), cast('s20단서'), cast('s20검사'),
                            cell.pct(85), wait(0.05), cell.pct(100)))
    mode_b = m.S('s20모드', [('f', K.button('꽃 심기 모드', 104, 28, 'green')), ('x', K.button('X 표시 모드', 104, 28, 'red'))], 180, -50)
    toggle = [if_(eq(V('게임중'), 1), setv('s20_mode', sub(1, V('s20_mode'))), cast('s20모드'))]
    mode_b.on(on_click(), *toggle)
    mode_b.on(on_msg('s20모드'), ifelse(eq(V('s20_mode'), 0), [shape('f')], [shape('x')]), mode_b.pct(90), wait(0.06), mode_b.pct(100))
    keys = hidden(m, 's20키')
    keys.on(on_key(K_X), *toggle)
    keys.on(on_key(K_SPACE), *toggle)
    m.T('s20모드글', '모드 바꾸기: 버튼 / X 키', 180, -74, 7, C_DIM, F_BODY, True, 0, w=110, h=10)
    info = m.T('s20정보', ' ', 180, 30, 10, C_WHITE, F_BODY, True, 0, w=110, h=60)
    info.on(on_msg('s20새퍼즐'), write(join('그림 ', V('s20_n'), ' / ', NPZ, '\n숫자 = 이어진\n꽃의 개수')))
    done = m.T('s20완성글', ' ', -14, -6, 16, '#FFE08A', F_NUM, False, 0, w=200, h=24, visible=False, bg=C_BOX)
    done.on(on_msg('s20완성'), write(join(LGET('s20_name', V('s20_n')), ' 완성!')), show(), wait(1.3), hide())
    newp = [chg('s20_n', 1), *[lst_set('s20_st', k, 0) for k in range(1, 26)],
            setv('s20_wrong', LGET('s20_ones', V('s20_n'))),
            *[lst_set('s20_rw', k, LGET('s20_rwi', add(base, k))) for k in range(1, 6)],
            *[lst_set('s20_cw', k, LGET('s20_cwi', add(base, k))) for k in range(1, 6)],
            cast('s20새퍼즐'), cast('s20단서'), setv('미니표시', join('그림 ', V('s20_n'), '/', NPZ)), setv('s20_lock', 0)]
    mgr = hidden(m, 's20담당')
    mgr.on(on_msg('게임시작'), setv('s20_n', 0), *newp)
    mgr.on(on_msg('s20검사'), if_(and_(eq(V('s20_wrong'), 0), eq(V('s20_lock'), 0)),
                                setv('s20_lock', 1), chg('s20_solved', 1), cast('s20완성'), wait(1.6),
                                ifelse(ge(V('s20_n'), NPZ), [*m.end_blocks(add(84, mul(V('남은시간'), 0.3)))], newp)))
    mgr.on(on_msg('시간끝'), setv('_mk', sub(10, mul(V('s20_wrong'), 2))), if_(lt(V('_mk'), 0), setv('_mk', 0)),
           *m.end_blocks(add(mul(V('s20_solved'), 28), V('_mk'))))
    m.on_start(setv('s20_n', 1), setv('s20_mode', 0), setv('s20_lock', 1), setv('s20_solved', 0), setv('s20_wrong', 0))
    m.snd('s20심기', play('pop'))
    m.snd('s20딸깍', play('tick'))
    m.snd('s20모드', play('click'))
    m.snd('s20완성', play('fanfare'))
    m.finish('줄마다 적힌 숫자는 이어서 심을 꽃의 개수예요.\n가로·세로 숫자 힌트에 맞게 꽃을 심어 그림 3개 완성!',
             '조작: 칸 클릭 = 꽃 심기/뽑기  ·  X 모드(버튼·X 키)로 빈칸 표시  ·  "1 1" = 1개, 띄고, 1개')
    return True
