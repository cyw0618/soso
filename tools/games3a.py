# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 1~10번."""
import random
from games_common import *
import mg_art3 as A3

T = 3
GAMES, game = registry()
import art3a as R


# ------------------------------------------------------------------ 공통 도우미
def popper(m, base, shapes, x, y, msg, sel=None, hold=0.5, at=None):
    """msg 신호에 튀어나왔다가 사라지는 그림 글자. sel: 모양 번호 변수 이름, at: (x식, y식) 나타날 자리."""
    o = m.S(base, shapes, x, y, visible=False)
    o.on(on_msg(msg), *([shape(V(sel))] if sel else []), *([xy(*at)] if at else []), to_front(), o.pct(135),
         fx('transparency', 0), show(), rep(5, o.grow_pct(-7), wait(0.016)), wait(hold),
         rep(6, fx_add('transparency', 16), wait(0.016)), hide())
    return o


def pad_shape(e):
    """K.bar_set 모양('00'~'40')을 번호식 e(0~40)로 고르기 (모양 이름이 숫자 글자라 이름으로 고른다)."""
    return ifelse(lt(e, 10), [shape(join('0', e))], [shape(join(e, ''))])


def clamp_(var, lo, hi):
    return [if_(lt(V(var), lo), setv(var, lo)), if_(gt(V(var), hi), setv(var, hi))]


# ================================================================== 1. 버스킹 음정 맞추기 (음정 따라가기)
@game(1)
def g01(P, ctx):
    BEAT, SPD, MX, T0, GAP, Y0, TOL = 0.6, 55.0, -120, 3.0, 20, -64, 9
    BPX = BEAT * SPD
    m = mg(P, ctx, T, 1, status='정확도 0%', dim=70)
    # 학교종이 땡땡땡 + 떨림 음이 있는 둘째 가락 (높이 1~8 = 도~높은 도, 0 = 쉼)
    A = [(5, 1), (5, 1), (6, 1), (6, 1), (5, 1), (5, 1), (3, 2), (5, 1), (5, 1), (3, 1), (3, 1), (2, 3), (0, 1),
         (5, 1), (5, 1), (6, 1), (6, 1), (5, 1), (5, 1), (3, 2), (5, 1), (3, 1), (2, 1), (3, 1), (1, 3), (0, 3)]
    B = [(8, 2, 1), (5, 1), (3, 1), (6, 2), (4, 2), (2, 1), (7, 1), (8, 4, 1), (0, 1), (6, 1), (4, 1), (3, 1), (2, 1),
         (3, 2), (5, 2), (2, 1), (7, 1), (1, 4, 1)]
    st, en, ys, hw, shp, vb = [], [], [], [], [], []
    b = 0
    for nt in A + B:
        lv, n = nt[0], nt[1]
        v = nt[2] if len(nt) > 2 else 0
        if lv:
            s = T0 + b * BEAT
            st.append(round(s, 3))
            en.append(round(s + n * BEAT, 3))
            ys.append(Y0 + (lv - 1) * GAP)
            hw.append((n * BPX - 4) / 2.0)
            shp.append(('v%d' if v else 'b%d') % n)
            vb.append(v)
        b += n
    N, END = len(st), en[-1]
    for nm, vals in (('k01_st', st), ('k01_en', en), ('k01_y', ys), ('k01_hw', hw), ('k01_shp', shp), ('k01_vb', vb)):
        P.list(nm, vals)
    vars_(P, 'k01_my', 'k01_vy', 'k01_ty', 'k01_act', 'k01_on', 'k01_hit', 'k01_tot', 'k01_nh', 'k01_nt', 'k01_ptr',
          'k01_si', 'k01_now', 'k01_prev', 'k01_dt', 'k01_j', 'k01_tip')
    panel(P, m.sc, '음정판', 0, 6, 470, 176, 'glass')
    m.S('오선', R.k01_staff(452, 172, GAP, 8), 0, Y0 + 3.5 * GAP)
    m.S('지금선', R.k01_nowline(176), MX, Y0 + 3.5 * GAP)
    # 음표 막대 (복제본이 시간에 맞춰 왼쪽으로 흐른다)
    bars = [('b%d' % k, R.k01_bar(k, BPX)) for k in (1, 2, 3, 4)] + [('v%d' % k, R.k01_bar(k, BPX, True)) for k in (2, 4)]
    nt = m.S('음표', bars, 400, 0, visible=False)
    nt.local('k01_ls', 0)
    nt.local('k01_lh', 0)
    nt.on(on_msg('k01_go'), setv('k01_si', 1),
          until(or_(gt(V('k01_si'), N), eq(V('게임중'), 0)),
                wait_until(or_(ge(timer(), sub(LGET('k01_st', V('k01_si')), 6.8)), eq(V('게임중'), 0))),
                setv('k01_ls', LGET('k01_st', V('k01_si'))), setv('k01_lh', LGET('k01_hw', V('k01_si'))),
                shape(LGET('k01_shp', V('k01_si'))), xy(400, LGET('k01_y', V('k01_si'))), clone_self(), chg('k01_si', 1)))
    nt.on(on_clone(), lx(add(add(MX, mul(sub(V('k01_ls'), timer()), SPD)), V('k01_lh'))), show(),
          until(or_(lt(add(obj_x(), V('k01_lh')), -198), eq(V('게임중'), 0)),
                lx(add(add(MX, mul(sub(V('k01_ls'), timer()), SPD)), V('k01_lh')))),
          del_clone())
    # 목소리 꼬리 (지나간 내 음 높이)
    tr = m.S('꼬리', [('off', R.k01_dot(0)), ('on', R.k01_dot(1))], MX, -300, visible=False)
    tr.local('k01_born', 0)
    tr.on(on_msg('k01_go'), until(eq(V('게임중'), 0), wait(0.08), clone_self()))
    tr.on(on_clone(), setv('k01_born', timer()), shape(add(V('k01_on'), 1)), xy(MX, V('k01_my')), show(),
          until(or_(gt(sub(timer(), V('k01_born')), 1.3), eq(V('게임중'), 0)),
                lx(sub(MX, mul(sub(timer(), V('k01_born')), SPD)))),
          del_clone())
    mk = m.S('목소리', [('off', R.k01_mark(0)), ('on', R.k01_mark(1))], MX, -70)
    mk.local('k01_ls2', -1)
    mk.on(on_scene(), xy(MX, -70), shape('off'))
    mk.on(on_msg('k01_go'), setv('k01_ls2', -1),
          until(eq(V('게임중'), 0), ly(V('k01_my')),
                if_(ne(V('k01_on'), V('k01_ls2')), setv('k01_ls2', V('k01_on')), shape(add(V('k01_on'), 1)))))
    # 아래: 나, 기타 가방, 관객
    m.S('나', ctx['BUST']['me'], -206, -104, scale=0.26)
    m.S('기타가방', R.k01_case(), -148, -121)
    crowd = m.S('관객', [('idle', R.k01_crowd(0)), ('cheer', R.k01_crowd(1))], 98, -112, scale=1.15)
    crowd.on(on_msg('k01_judge'), if_(eq(V('k01_j'), 1), shape('cheer'), mvy(3), wait(0.15), mvy(-3), wait(0.45), shape('idle')))
    coin = m.S('동전', K.icon_img('coin', 12), 0, -300, visible=False)
    coin.on(on_msg('k01_judge'), if_(eq(V('k01_j'), 1), xy(rnd(10, 190), -92), show(), glide(0.35, -148, -118), hide()))
    popper(m, '판정', [('g', K.big_text('완벽!', 18, 'green')), ('o', K.big_text('좋아요', 16, 'royal')),
                     ('x', K.big_text('음이탈!', 16, 'red'))], MX + 60, 0, 'k01_judge', sel='k01_j', hold=0.3,
           at=(MX + 62, V('k01_my')))
    # 담당: 시간·음 높이·판정
    judge = [if_(gt(V('k01_nt'), 0.1),
                 ifelse(ge(div(V('k01_nh'), V('k01_nt')), 0.75), [setv('k01_j', 1), chg('k01_tip', 1)],
                        [ifelse(ge(div(V('k01_nh'), V('k01_nt')), 0.4), [setv('k01_j', 2)], [setv('k01_j', 3)])]),
                 cast('k01_judge'),
                 setv('미니표시', join('정확도 ', rounded(mul(div(V('k01_hit'), V('k01_tot')), 100)), '% · 팁 ', V('k01_tip')))),
             setv('k01_nh', 0), setv('k01_nt', 0)]
    phase = sub(V('k01_now'), LGET('k01_st', V('k01_ptr')))
    vib = [setv('_mv', mul(6, sin_(mul(360 * SPD / 30.0, phase)))),
           setv('k01_ty', add(LGET('k01_y', V('k01_ptr')), mul(LGET('k01_vb', V('k01_ptr')), V('_mv'))))]
    mgr = hidden(m, '음정담당')
    mgr.on(on_msg('게임시작'), reset_timer(), start_timer(), setv('k01_prev', 0), cast('k01_go'),
           until(or_(gt(timer(), END + 1.2), eq(V('게임중'), 0)),
                 setv('k01_now', timer()), setv('k01_dt', sub(V('k01_now'), V('k01_prev'))), setv('k01_prev', V('k01_now')),
                 if_(gt(V('k01_dt'), 0.1), setv('k01_dt', 0.1)),
                 # 목소리: 누르는 동안 가속, 놓으면 금방 멈춤
                 if_(key(K_UP), chg('k01_vy', mul(1500, V('k01_dt')))),
                 if_(key(K_DOWN), chg('k01_vy', mul(-1500, V('k01_dt')))),
                 chg('k01_my', mul(V('k01_vy'), V('k01_dt'))),
                 setv('_mk', mul(9, V('k01_dt'))), if_(gt(V('_mk'), 0.9), setv('_mk', 0.9)),
                 setv('k01_vy', mul(V('k01_vy'), sub(1, V('_mk')))),
                 if_(gt(V('k01_my'), 86), setv('k01_my', 86), setv('k01_vy', 0)),
                 if_(lt(V('k01_my'), -74), setv('k01_my', -74), setv('k01_vy', 0)),
                 # 지금 음
                 if_(le(V('k01_ptr'), N), if_(gt(V('k01_now'), LGET('k01_en', V('k01_ptr'))), *judge, chg('k01_ptr', 1))),
                 setv('k01_act', 0), setv('k01_on', 0),
                 if_(le(V('k01_ptr'), N),
                     if_(ge(V('k01_now'), LGET('k01_st', V('k01_ptr'))), setv('k01_act', 1), *vib)),
                 if_(eq(V('k01_act'), 1), chg('k01_tot', V('k01_dt')), chg('k01_nt', V('k01_dt')),
                     if_(lt(abs_(sub(V('k01_my'), V('k01_ty'))), TOL), setv('k01_on', 1), chg('k01_hit', V('k01_dt')),
                         chg('k01_nh', V('k01_dt'))))),
           *m.end_blocks(mul(div(V('k01_hit'), add(V('k01_tot'), 0.01)), 112)))
    m.on_start(setv('k01_my', -70), setv('k01_vy', 0), setv('k01_hit', 0), setv('k01_tot', 0), setv('k01_nh', 0),
               setv('k01_nt', 0), setv('k01_ptr', 1), setv('k01_on', 0), setv('k01_act', 0), setv('k01_tip', 0),
               setv('k01_ty', -300))
    m.snd('k01_judge', ifelse(eq(V('k01_j'), 1), [play('coin')], [ifelse(eq(V('k01_j'), 3), [play('bad')], [play('pop')])]))
    m.finish('홍대 거리 버스킹! 오른쪽에서 흘러오는 음표 막대에\n목소리 표시를 맞춰 부르세요. 물결 막대는 떨림 음!',
             '조작: ↑ ↓ 방향키로 목소리 높이 (누르고 있으면 빨라져요)')
    return True


# ================================================================== 2. 감귤 트럭 싣기 (배낭 문제)
def _knap_puzzles(seed, per_round=6):
    rng = random.Random(seed)
    out = []
    for rd in range(3):
        got = 0
        while got < per_round:
            w = [rng.randint(2, 9) for _ in range(8)]
            v = [max(2, int(round(x * rng.uniform(0.9, 2.6)))) for x in w]
            lim = int(round(sum(w) * rng.uniform(0.40, 0.52)))
            best = 0
            for mask in range(256):
                sw = sum(w[i] for i in range(8) if mask >> i & 1)
                if sw <= lim:
                    best = max(best, sum(v[i] for i in range(8) if mask >> i & 1))
            gw = gv = 0
            for i in sorted(range(8), key=lambda i: -v[i] / w[i]):
                if gw + w[i] <= lim:
                    gw += w[i]
                    gv += v[i]
            if rd > 0 and gv / best > 0.93:
                continue
            out.append((w, v, lim, best))
            got += 1
    return out


@game(2)
def g02(P, ctx):
    NR, PER = 3, 6
    puz = _knap_puzzles(3302, PER)
    m = mg(P, ctx, T, 2, time_limit=90, status='라운드 1/%d' % NR, dim=60)
    P.list('k02_w', [x for p in puz for x in p[0]])
    P.list('k02_v', [x for p in puz for x in p[1]])
    P.list('k02_lim', [p[2] for p in puz])
    P.list('k02_best', [p[3] for p in puz])
    P.list('k02_in', [0] * 8)
    vars_(P, 'k02_base', 'k02_pz', 'k02_sw', 'k02_sv', 'k02_lm', 'k02_bs', 'k02_tot', 'k02_rs', 'k02_res')
    SX = [-201, -151, -101, -51]
    SY = [24, -46]
    TX = [16, 62, 108, 154]
    TY = [-56, -16]
    panel(P, m.sc, '창고판', -126, -8, 216, 178, 'glass')
    m.T('창고글', '감귤 창고 (클릭해서 싣기)', -126, 68, 10, C_ACC, F_BODY, True, 0, w=200, h=16)
    panel(P, m.sc, '저울판', 110, 54, 226, 70, 'glass')
    truck = m.S('트럭', R.k02_truck(), 110, -60)
    truck.on(on_msg('k02_new'), xy(-420, -60), glide(0.6, 110, -60))
    truck.on(on_msg('k02_drive'), wait(0.15), glide(0.9, 450, -60))
    truck.on(on_msg('k02_over'), rep(3, mvx(4), wait(0.04), mvx(-4), wait(0.04)))
    sum_w = add(*[mul(LGET('k02_in', j), LGET('k02_w', add(V('k02_base'), j))) for j in range(1, 9)])
    sum_v = add(*[mul(LGET('k02_in', j), LGET('k02_v', add(V('k02_base'), j))) for j in range(1, 9)])
    recalc = [setv('k02_sw', sum_w), setv('k02_sv', sum_v), cast('k02_upd')]
    for i in range(1, 9):
        c, r = (i - 1) % 4, (i - 1) // 4
        sx, sy, tx, ty = SX[c], SY[r], TX[c], TY[r]
        toggle = [if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)),
                      lst_set('k02_in', i, sub(1, LGET('k02_in', i))), *recalc, cast('k02_clk'))]
        for kind in ('box', 'lab'):
            if kind == 'box':
                o = m.S('상자%d' % i, R.k02_crate(), sx, sy)
                dy = 0
            else:
                o = m.T('상자글%d' % i, '', sx, sy - 3, 9, '#5A2E00', F_NUM, False, 0, w=40, h=24)
                dy = -3
                o.on(on_msg('k02_new'), write(join(LGET('k02_w', add(V('k02_base'), i)), 'kg\n',
                                                   LGET('k02_v', add(V('k02_base'), i)), '만원')))
            o.local('k02_was', 0)
            o.on(on_click(), *toggle)
            o.on(on_msg('k02_new'), setv('k02_was', 0), xy(sx, sy + dy), show())
            o.on(on_msg('k02_upd'), if_(ne(LGET('k02_in', i), V('k02_was')), setv('k02_was', LGET('k02_in', i)),
                                        ifelse(eq(V('k02_was'), 1), [glide(0.14, tx, ty + dy)], [glide(0.14, sx, sy + dy)])))
            o.on(on_msg('k02_drive'), if_(eq(V('k02_was'), 1), wait(0.15), glide(0.9, tx + 340, ty + dy), hide()))
    wt = m.T('무게글', '', 110, 76, 11, C_WHITE, F_NUM, False, 0, w=210, h=16)
    vt = m.T('가격글', '', 110, 36, 11, C_ACC, F_NUM, False, 0, w=210, h=16)
    bar = m.S('무게막대', K.bar_set('k02_wbar', 180, 10, 'royal'), 110, 57)
    over = m.S('초과표', K.badge('무게 초과!', 64, 16, 'red'), 196, 76, visible=False)
    for o in (wt, vt, bar, over):
        o.on(on_msg('k02_upd'), *({wt: [write(join('싣은 무게 ', V('k02_sw'), ' / ', V('k02_lm'), 'kg')),
                                       ifelse(gt(V('k02_sw'), V('k02_lm')), [text_color(C_RED)], [text_color(C_WHITE)])],
                                  vt: [write(join('귤값 합계 ', V('k02_sv'), '만원'))],
                                  bar: [setv('_mk', floor(mul(div(V('k02_sw'), V('k02_lm')), 40))),
                                        if_(gt(V('_mk'), 40), setv('_mk', 40)), pad_shape(V('_mk'))],
                                  over: [ifelse(gt(V('k02_sw'), V('k02_lm')), [show()], [hide()])]}[o]))
    go_act = [if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)),
                  ifelse(gt(V('k02_sw'), V('k02_lm')), [cast('k02_over')], [setv('입력가능', 0)]))]
    button(P, m.sc, '출발버튼', '출발!', 186, -120, 82, 24, 'green', actions=go_act)
    clear = [if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)), *[lst_set('k02_in', j, 0) for j in range(1, 9)], *recalc)]
    button(P, m.sc, '내리기버튼', '모두 내리기', 84, -120, 96, 24, 'steel', actions=clear)
    popper(m, '결과팝', [('a', K.big_text('최고의 조합!', 24, 'green')), ('b', K.big_text('좋아요!', 24, 'royal')),
                       ('c', K.big_text('더 비싸게 실을 수 있어요', 18, 'red'))], 0, 30, 'k02_result', sel='k02_res', hold=1.0)
    det = m.T('결과글', '', 0, 2, 11, C_WHITE, F_NUM, False, 0, w=300, h=18, visible=False, bg=C_BOX)
    det.on(on_msg('k02_result'), write(join('내 트럭 ', V('k02_sv'), '만원  ·  최고 조합 ', V('k02_bs'), '만원')), show(),
           wait(1.5), hide())
    popper(m, '초과팝', K.big_text('너무 무거워요!', 22, 'red'), 110, 0, 'k02_over', hold=0.5)
    rscore = mul(div(sub(div(V('k02_sv'), V('k02_bs')), 0.6), 0.4), 100)
    mgr = hidden(m, '트럭담당')
    mgr.on(on_msg('게임시작'), setv('라운드', 1),
           until(or_(gt(V('라운드'), NR), eq(V('게임중'), 0)),
                 setv('k02_pz', add(mul(sub(V('라운드'), 1), PER), rnd(1, PER))),
                 setv('k02_base', mul(sub(V('k02_pz'), 1), 8)),
                 setv('k02_lm', LGET('k02_lim', V('k02_pz'))), setv('k02_bs', LGET('k02_best', V('k02_pz'))),
                 *[lst_set('k02_in', j, 0) for j in range(1, 9)], cast('k02_new'), *recalc,
                 setv('미니표시', join('라운드 ', V('라운드'), '/', NR)),
                 wait(0.6), setv('입력가능', 1),
                 wait_until(or_(eq(V('입력가능'), 0), eq(V('게임중'), 0))),
                 if_(eq(V('게임중'), 1),
                     setv('k02_rs', rscore), if_(lt(V('k02_rs'), 0), setv('k02_rs', 0)), chg('k02_tot', V('k02_rs')),
                     ifelse(ge(V('k02_sv'), V('k02_bs')), [setv('k02_res', 1)],
                            [ifelse(ge(div(V('k02_sv'), V('k02_bs')), 0.88), [setv('k02_res', 2)], [setv('k02_res', 3)])]),
                     cast('k02_result'), cast('k02_drive'), wait(1.8)),
                 chg('라운드', 1)),
           *m.end_blocks(div(V('k02_tot'), NR)))
    mgr.on(on_msg('시간끝'), if_(and_(eq(V('입력가능'), 1), le(V('k02_sw'), V('k02_lm'))),
                                setv('k02_rs', rscore), if_(gt(V('k02_rs'), 0), chg('k02_tot', V('k02_rs')))),
           setv('입력가능', 0), *m.end_blocks(div(V('k02_tot'), NR)))
    m.on_start(setv('k02_tot', 0), setv('입력가능', 0), setv('k02_sw', 0), setv('k02_sv', 0), setv('k02_base', 0),
               setv('k02_lm', 1), setv('k02_bs', 1), *[lst_set('k02_in', j, 0) for j in range(1, 9)])
    m.snd('k02_clk', play('pop'))
    m.snd('k02_over', play('bad'))
    m.snd('k02_result', ifelse(eq(V('k02_res'), 3), [play('bad')], [play('cash')]))
    m.snd('k02_drive', play('go'))
    m.finish('무게 제한 안에서 귤값 합계가 가장 비싸게! 상자를\n골라 트럭에 싣고 출발하세요. (3라운드, 최고 조합과 비교)',
             '조작: 상자 클릭 = 싣기/내리기  ·  "출발!" 버튼')
    return True


# ================================================================== 3. 생선 경매 (영국식 경매)
FISH_BASE = [8, 16, 24, 20]                  # 고등어 갈치 참돔 광어 (★3·중 기준, 만원)
STAR_F = [0.5, 0.75, 1.0, 1.25, 1.5]
SIZE_F = [0.8, 1.0, 1.25, 1.5]


def _auction_days(seed, n_days=4, n_fish=5):
    rng = random.Random(seed)
    days = []
    for _ in range(n_days):
        kinds = ['bargain', 'normal', 'normal', 'trap', 'close']
        rng.shuffle(kinds)
        fish = []
        for kd in kinds:
            sp = rng.randint(0, 3)
            stars = rng.randint(1, 5)
            sz = rng.randint(0, 3)
            val = max(4, int(round(FISH_BASE[sp] * STAR_F[stars - 1] * SIZE_F[sz])))
            hi = {'bargain': (0.55, 0.72), 'normal': (0.78, 0.9), 'trap': (1.12, 1.3), 'close': (0.92, 1.0)}[kd]
            a1 = rng.uniform(*hi)
            a2 = rng.uniform(0.5, a1)
            if rng.random() < 0.5:
                a1, a2 = a2, a1
            inc = max(1, int(round(val * 0.08)))
            start = max(1, int(round(val * 0.4)))
            v1, v2 = int(val * a1), int(val * a2)
            # 상인이 부를 수 있는 가장 높은 값 → 그다음 값으로 사면 이긴다
            lv = start
            top = None
            while lv <= max(v1, v2):
                top = lv
                lv += inc
            win = start if top is None else top + inc
            fish.append((sp + 1, stars, sz + 1, val, v1, v2, inc, start, max(0, val - win)))
        days.append(fish)
    return days


@game(3)
def g03(P, ctx):
    NF = 5
    days = _auction_days(3303)
    m = mg(P, ctx, T, 3, status='이익 0만원', dim=90)
    flat_ = [f for d in days for f in d]
    for k, nm in enumerate(('k03_sp', 'k03_st', 'k03_sz', 'k03_val', 'k03_v1', 'k03_v2', 'k03_inc', 'k03_start')):
        P.list(nm, [f[k] for f in flat_])
    P.list('k03_ideal', [sum(f[8] for f in d) for d in days])
    P.list('k03_fname', R.FISH)
    P.list('k03_szname', ['소', '중', '대', '특대'])
    vars_(P, 'k03_day', 'k03_i', 'k03_idx', 'k03_price', 'k03_lead', 'k03_last', 'k03_ainext', 'k03_open', 'k03_out',
          'k03_money', 'k03_profit', 'k03_cd', 'k03_sold', 'k03_bidder', 'k03_gain', 'k03_can1', 'k03_can2')
    cur = lambda nm: LGET(nm, V('k03_idx'))
    # 왼쪽: 시세표
    panel(P, m.sc, '시세판', -170, 4, 128, 188, 'glass', header='royal')
    m.T('시세제목', '오늘의 시세표', -170, 88, 11, C_WHITE, F_NUM, False, 0, w=120, h=16)
    m.T('시세본문', '★★★ · 크기 중 기준\n고등어  8만원\n갈치  16만원\n참돔  24만원\n광어  20만원\n\n별 1개마다 ±25%\n크기  소 ×0.8\n대 ×1.25  특대 ×1.5',
        -170, 4, 10, C_WHITE, F_BODY, True, 0, w=122, h=150)
    # 가운데: 생선
    m.T('생선이름', '', 22, 86, 12, C_WHITE, F_NUM, False, 0, w=210, h=18).on(
        on_msg('k03_new'), write(join(V('k03_i'), '/', NF, '  ', LGET('k03_fname', cur('k03_sp')), ' · 크기 ',
                                      LGET('k03_szname', cur('k03_sz')))))
    m.S('얼음판', R.k03_tray(), 22, 30)
    fish = m.S('생선', [('f%d' % k, R.k03_fish(k)) for k in range(4)], 22, 48)
    fish.on(on_msg('k03_new'), shape(cur('k03_sp')), fish.pct(mul(LGET('k03_szf', cur('k03_sz')), 100)), xy(300, 48),
            glide(0.35, 22, 48))
    fish.on(on_msg('k03_sold'), wait(1.6), glide(0.3, -400, 48))
    P.list('k03_szf', [0.72, 0.86, 1.0, 1.14])
    stars = m.S('별', [('s%d' % k, R.k03_stars(k)) for k in range(1, 6)], 22, 8)
    stars.on(on_msg('k03_new'), shape(cur('k03_st')))
    # 가격판
    panel(P, m.sc, '가격판', 22, -44, 214, 60, 'glass')
    pt = m.T('현재가', '', 2, -34, 17, C_WHITE, F_NUM, False, 0, w=170, h=24)
    lt_ = m.T('최고입찰', '', 2, -58, 10, C_ACC, F_BODY, True, 0, w=170, h=16)
    for o in (pt, lt_):
        o.on(on_msg('k03_new'), write(''))
    pt.on(on_msg('k03_open'), write(join('시작가 ', V('k03_start_'), '만원')))
    lt_.on(on_msg('k03_open'), write('경매 시작! 입찰하세요'), text_color(C_ACC))
    pt.on(on_msg('k03_bid'), write(join('현재가 ', V('k03_price'), '만원')))
    lt_.on(on_msg('k03_bid'), ifelse(eq(V('k03_lead'), 1), [write('최고 입찰: 나'), text_color('#7CFFB0')],
                                     [write(join('최고 입찰: ', sub(V('k03_lead'), 1), '번 후보')),
                                      text_color(C_RED)]))
    cd = m.S('카운트', [('a', K.big_text('하나!', 16, 'white')), ('b', K.big_text('둘!', 16, 'white')),
                       ('c', K.big_text('낙찰!', 18, 'red'))], 98, -44, visible=False)
    cd.on(on_msg('k03_cd'), shape(V('k03_cd')), cd.pct(130), show(), rep(5, cd.grow_pct(-6), wait(0.016)))
    cd.on(on_msg('k03_bid'), hide())
    cd.on(on_msg('k03_new'), hide())
    # 오른쪽: 경쟁 상인 (상대 후보)
    for n, yy in (('1', 50), ('2', -30)):
        m.rival('상인%s' % n, n, 196, yy, scale=0.36)
        m.rival_badge('상인표%s' % n, '%s번 후보' % n, 196, yy - 34, 64, 'royal' if n == '1' else 'red')
        bub = m.T('상인말%s' % n, '', 196, yy + 34, 11, C_WHITE, F_NUM, False, 0, w=60, h=16, visible=False, bg='#B02238')
        bub.on(on_msg('k03_bid'), ifelse(eq(V('k03_lead'), int(n) + 1),
                                         [write(join(V('k03_price'), '만!')), show()], [hide()]))
        bub.on(on_msg('k03_new'), hide())
    # 버튼
    bid = [if_(and_(and_(eq(V('게임중'), 1), eq(V('k03_open'), 1)), and_(eq(V('k03_out'), 0), ne(V('k03_lead'), 1))),
               ifelse(gt(add(V('k03_price'), cur('k03_inc')), V('k03_money')), [cast('k03_poor')],
                      [chg('k03_price', cur('k03_inc')), setv('k03_lead', 1), setv('k03_last', timer()), setv('k03_cd', 0),
                       setv('k03_ainext', add(timer(), div(rnd(50, 120), 100))), cast('k03_bid')]))]
    bb = button(P, m.sc, '입찰버튼', '입찰!', -26, -100, 108, 28, 'royal', actions=bid)
    bt = m.T('입찰액', '', -26, -118, 8, C_DIM, F_BODY, True, 0, w=110, h=12)
    bt.on(on_msg('k03_new'), write(join('한 번에 +', cur('k03_inc'), '만원')))
    fold = [if_(and_(eq(V('k03_open'), 1), ne(V('k03_lead'), 1)), setv('k03_out', 1), cast('k03_fold'))]
    button(P, m.sc, '포기버튼', '포기', 80, -100, 76, 28, 'red', actions=fold)
    poor = m.T('돈부족', '돈이 모자라요!', -26, -76, 10, C_RED, F_NUM, False, 0, w=110, h=14, visible=False)
    poor.on(on_msg('k03_poor'), show(), wait(0.8), hide())
    # 결과 공개
    rv = m.T('공개', '', 22, 48, 12, C_WHITE, F_NUM, False, 0, w=230, h=40, visible=False, bg=C_BOX)
    rv.on(on_msg('k03_sold'), wait(0.3),
          ifelse(eq(V('k03_lead'), 1),
                 [ifelse(ge(V('k03_gain'), 0), [text_color('#7CFFB0')], [text_color(C_RED)]),
                  write(join('진짜 시세 ', cur('k03_val'), '만원!\n', V('k03_price'), '만원에 샀어요 → 이익 ',
                             V('k03_gain'), '만원'))],
                 [text_color(C_WHITE), write(join(sub(V('k03_lead'), 1), '번 후보가 ', V('k03_price'), '만원에 낙찰\n진짜 시세는 ',
                                                  cur('k03_val'), '만원'))]),
          to_front(), show(), wait(1.6), hide())
    # 담당
    ai_bid = [setv('k03_can1', 0), setv('k03_can2', 0),
              if_(and_(ne(V('k03_lead'), 2), le(add(V('k03_price'), cur('k03_inc')), cur('k03_v1'))), setv('k03_can1', 1)),
              if_(and_(ne(V('k03_lead'), 3), le(add(V('k03_price'), cur('k03_inc')), cur('k03_v2'))), setv('k03_can2', 1)),
              setv('k03_bidder', 0),
              ifelse(and_(eq(V('k03_can1'), 1), eq(V('k03_can2'), 1)), [setv('k03_bidder', add(1, rnd(1, 2)))],
                     [if_(eq(V('k03_can1'), 1), setv('k03_bidder', 2)), if_(eq(V('k03_can2'), 1), setv('k03_bidder', 3))]),
              ifelse(gt(V('k03_bidder'), 0),
                     [chg('k03_price', cur('k03_inc')), setv('k03_lead', V('k03_bidder')), setv('k03_last', timer()),
                      setv('k03_cd', 0), cast('k03_bid'),
                      ifelse(eq(V('k03_out'), 1), [setv('k03_ainext', add(timer(), 0.3))],
                             [setv('k03_ainext', add(timer(), div(rnd(60, 140), 100)))])],
                     [setv('k03_ainext', add(timer(), 0.3))])]
    mgr = hidden(m, '경매담당')
    mgr.on(on_msg('게임시작'), reset_timer(), start_timer(), setv('k03_day', rnd(1, len(days))), setv('k03_i', 1),
           until(or_(gt(V('k03_i'), NF), eq(V('게임중'), 0)),
                 setv('k03_idx', add(mul(sub(V('k03_day'), 1), NF), V('k03_i'))),
                 setv('k03_out', 0), setv('k03_open', 0), setv('k03_lead', 0), setv('k03_cd', 0),
                 setv('k03_price', sub(cur('k03_start'), cur('k03_inc'))), setv('k03_start_', cur('k03_start')),
                 cast('k03_new'), wait(1.6),
                 setv('k03_open', 1), setv('k03_last', timer()), setv('k03_ainext', add(timer(), 1.2)), cast('k03_open'),
                 until(or_(eq(V('k03_open'), 0), eq(V('게임중'), 0)),
                       if_(ge(timer(), V('k03_ainext')), *ai_bid),
                       setv('_mk', sub(timer(), V('k03_last'))),
                       if_(eq(V('k03_out'), 1), if_(eq(V('k03_lead'), 0), setv('k03_open', 0))),
                       if_(gt(V('k03_lead'), 0),
                           ifelse(ge(V('_mk'), 3.0), [setv('k03_open', 0)],
                                  [if_(and_(ge(V('_mk'), 2.0), lt(V('k03_cd'), 2)), setv('k03_cd', 2), cast('k03_cd')),
                                   if_(and_(ge(V('_mk'), 1.0), lt(V('k03_cd'), 1)), setv('k03_cd', 1), cast('k03_cd'))]))),
                 if_(eq(V('게임중'), 1),
                     setv('k03_cd', 3), cast('k03_cd'),
                     if_(eq(V('k03_lead'), 1), chg('k03_money', mul(V('k03_price'), -1)),
                         setv('k03_gain', sub(cur('k03_val'), V('k03_price'))), chg('k03_profit', V('k03_gain'))),
                     setv('미니표시', join('이익 ', V('k03_profit'), '만원')),
                     cast('k03_sold'), wait(2.1)),
                 chg('k03_i', 1)),
           *m.end_blocks(mul(div(V('k03_profit'), LGET('k03_ideal', V('k03_day'))), 100)))
    money = m.T('내돈', '', -170, -104, 11, C_WHITE, F_NUM, False, 0, w=128, h=16, bg=C_BOX)
    money.on(on_scene(), *G.live_write(money, [setv('_mt', join('내 돈 ', V('k03_money'), '만원'))], '_mt', 0.2))
    vars_(P, 'k03_start_')
    m.on_start(setv('k03_money', 100), setv('k03_profit', 0), setv('k03_open', 0), setv('k03_lead', 0), setv('k03_idx', 1),
               setv('k03_i', 1))
    m.snd('k03_bid', ifelse(eq(V('k03_lead'), 1), [play('stamp')], [play('tick')]))
    m.snd('k03_cd', ifelse(eq(V('k03_cd'), 3), [play('hit')], [play('beep')]))
    m.snd('k03_sold', wait(0.3), ifelse(eq(V('k03_lead'), 1), [ifelse(ge(V('k03_gain'), 0), [play('cash')], [play('bad')])],
                                        [play('pop')]))
    m.snd('k03_poor', play('bad'))
    m.finish('자갈치 새벽 경매! 별(신선도)과 크기로 진짜 값을 짐작해\n그보다 싸게 사면 이익, 비싸게 사면 손해예요. (5마리)',
             '조작: "입찰!" = 값 올려 부르기 · "포기" = 이번 생선 넘기기\n아무도 안 부르고 3초 지나면 낙찰!')
    return True
