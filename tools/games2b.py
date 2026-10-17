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
    disp = m.T('s13층표시', ' ', 196, 88, 10, '#FFD27A', F_NUM, False, 0, w=60, h=14)
    disp.on(on_scene(), *G.live_write(disp, setv('_mv', join(V('s13_at'), '층 · ', V('s13_load'), '/', CAP)), '_mv', 0.1))
    for k in range(1, 6):
        b = m.S('s13버튼%d' % k, [(st, AB.s13_button(k, st)) for st in ('off', 'ride', 'go')], 196, FL[k - 1] + 19)
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
