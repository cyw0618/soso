# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 31~40번."""
import random
from games_common import *
import mg_art3 as A3

T = 2
GAMES, game = registry()
import math
import mg_art as A
import art2d as AD


def _pop(m, base, pics, x, y, msg, hold=0.6, pre=()):
    """신호를 받으면 튀어나왔다 사라지는 큰 글자 (pics: 그림 또는 [(이름, 그림)])."""
    return G.big_pop(m.P, m.sc, base, pics, x, y, msg, hold=hold, pre=pre)


def _float_text(m, base, x, y, size, color, msg, var, dy=18):
    """msg 신호에 var 글을 (x, y)에 띄워 위로 사라지게."""
    o = m.T(base, '', x, y, size, color, F_NUM, False, 0, w=160, h=size + 8, visible=False)
    o.on(on_msg(msg), write(V(var)), xy(x, y), fx('transparency', 0), show(),
         rep(12, mvy(dy / 12.0), wait(0.03)), rep(8, fx_add('transparency', 12), wait(0.03)), hide())
    return o


# ================================================================== 31. 드론 방제 한붓그리기
def _s31_puzzles():
    N = 5

    def nb(i):
        r, c = divmod(i, N)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < N and 0 <= cc < N:
                yield rr * N + cc

    def count(free, start, cap=400):
        tot, seen, cnt = len(free), {start}, [0]

        def dfs(h, depth):
            if cnt[0] >= cap:
                return
            if depth == tot:
                cnt[0] += 1
                return
            for j in nb(h):
                if j in free and j not in seen:
                    seen.add(j)
                    dfs(j, depth + 1)
                    seen.discard(j)
        dfs(start, 1)
        return cnt[0]
    rng = random.Random(3131)
    out = []
    for b, lo, hi in ((4, 25, 400), (3, 4, 24), (2, 1, 3)):
        got = []
        while len(got) < 5:
            blocks = sorted(rng.sample(range(25), b))
            free = set(range(25)) - set(blocks)
            st = rng.choice(sorted(free))
            if lo <= count(free, st) <= hi and (blocks, st) not in got:
                got.append((blocks, st))
        for blocks, st in got:
            s = ''.join(str(rng.choice((2, 3))) if k in blocks else '0' for k in range(25))
            out.append((s, st + 1, 25 - len(blocks)))
    return out


@game(31)
def g31(P, ctx):
    TL, N, CL, R = 100, 5, 38, 3
    BX, BY = -46, -12
    X0, Y0 = BX - 2 * CL, BY + 2 * CL
    puz = _s31_puzzles()
    m = mg(P, ctx, T, 31, time_limit=TL, status='논 1/%d' % R, dim=70)
    P.list('s31_퍼즐', [p[0] for p in puz])
    P.list('s31_시작', [p[1] for p in puz])
    P.list('s31_칸수', [p[2] for p in puz])
    P.list('s31_칸', [0] * 25)
    P.list('s31_길', [1] * 25)
    P.list('s31_x', [X0 + (k % N) * CL for k in range(25)])
    P.list('s31_y', [Y0 - (k // N) * CL for k in range(25)])
    vars_(P, 's31_머리', 's31_목표', 's31_남은', 's31_길이', 's31_판', 's31_시작칸', 's31_총', 's31_빈이웃')
    panel(P, m.sc, 's31_판넬', BX, BY, N * CL + 16, N * CL + 16, 'glass')
    cell = m.S('논칸', [(k, AD.s31_cell(k)) for k in ('paddy', 'done', 'house', 'tree')], -300, -300, visible=False)
    cell.local('번호', 0)
    cell.on(on_scene(), hide(), setv('번호', 0), rep(25, chg('번호', 1), clone_self()))
    cell.on(on_clone(), xy(LGET('s31_x', V('번호')), LGET('s31_y', V('번호'))), shape(add(LGET('s31_칸', V('번호')), 1)), show())
    cell.on(on_msg('s31_판갱신'), if_(gt(V('번호'), 0), shape(add(LGET('s31_칸', V('번호')), 1))))
    cell.on(on_click(), if_(and_(gt(V('번호'), 0), and_(eq(V('게임중'), 1), eq(V('입력가능'), 1))),
                            setv('s31_목표', V('번호')), cast('s31_이동')))
    ring = m.S('출발표시', AD.s31_start_ring(), -300, -300)
    ring.on(on_msg('s31_새판'), xy(LGET('s31_x', V('s31_시작칸')), LGET('s31_y', V('s31_시작칸'))), show())
    ring.on(on_scene(), hide())
    # 드론: 붓으로 지나온 길을 그린다
    dr = m.S('드론', [('a', AD.s31_drone(1)), ('b', AD.s31_drone(2))], -300, -300)
    hx, hy = LGET('s31_x', V('s31_머리')), LGET('s31_y', V('s31_머리'))
    redraw = [pen_up(), pen_clear(), pen_color('#9FF3FF'), pen_size(5),
              xy(LGET('s31_x', LGET('s31_길', 1)), LGET('s31_y', LGET('s31_길', 1))), pen_down(),
              *[if_(le(k, V('s31_길이')), xy(LGET('s31_x', LGET('s31_길', k)), LGET('s31_y', LGET('s31_길', k))))
                for k in range(2, 26)], pen_up(), xy(hx, hy)]
    dr.on(on_scene(), hide(), pen_up(), pen_clear())
    dr.on(on_msg('s31_새판'), *redraw, show(), to_front())
    dr.on(on_msg('s31_다시그림'), *redraw)
    dr.on(on_msg('s31_전진'), pen_color('#9FF3FF'), pen_size(5), pen_down(), xy(hx, hy), pen_up(),
          dr.pct(118), wait(0.05), dr.pct(100))
    dr.on(on_msg('게임시작'), until(eq(V('게임중'), 0), next_shape(), wait(0.06)))
    # 오른쪽 안내판
    RX = 160
    panel(P, m.sc, 's31_안내판', RX, 16, 128, 92, 'glass')
    info = m.T('s31_남은글', '', RX, 30, 12, C_WHITE, F_NUM, False, 0, w=118, h=40)
    info.on(on_msg('s31_판갱신'), write(join('남은 논\n', V('s31_남은'), '칸')))
    m.T('s31_설명', '이웃한 논을 클릭\n(방향키도 돼요)', RX, -12, 8, C_DIM, F_BODY, True, 0, w=118, h=26)
    tip = m.T('s31_막힘글', '', RX, -100, 9, C_RED, F_BODY, True, 0, w=128, h=30)
    tip.on(on_msg('s31_판갱신'), ifelse(and_(eq(V('s31_빈이웃'), 0), gt(V('s31_남은'), 0)),
                                        [write('막혔어요!\n되돌리기를 눌러 보세요')], [write('')]))
    # 이동 판정
    h = V('s31_머리')
    t_ = V('s31_목표')
    adj = eq(add(abs_(sub(floor(div(sub(h, 1), N)), floor(div(sub(t_, 1), N)))), abs_(sub(mod(sub(h, 1), N), mod(sub(t_, 1), N)))), 1)
    check_free = [setv('s31_빈이웃', 0),
                  if_(gt(h, N), if_(eq(LGET('s31_칸', sub(h, N)), 0), chg('s31_빈이웃', 1))),
                  if_(le(h, 25 - N), if_(eq(LGET('s31_칸', add(h, N)), 0), chg('s31_빈이웃', 1))),
                  if_(gt(mod(sub(h, 1), N), 0), if_(eq(LGET('s31_칸', sub(h, 1)), 0), chg('s31_빈이웃', 1))),
                  if_(lt(mod(sub(h, 1), N), N - 1), if_(eq(LGET('s31_칸', add(h, 1)), 0), chg('s31_빈이웃', 1)))]
    undo = [if_(and_(gt(V('s31_길이'), 1), eq(V('입력가능'), 1)),
                lst_set('s31_칸', h, 0), chg('s31_길이', -1), setv('s31_머리', LGET('s31_길', V('s31_길이'))),
                chg('s31_남은', 1), *check_free, cast('s31_판갱신'), cast('s31_다시그림'), cast('s31_되돌림'))]
    status = setv('미니표시', join('논 ', V('라운드'), '/', R, ' · 남은 ', V('s31_남은')))
    mgr = hidden(m, 's31_담당')
    mgr.on(on_msg('s31_이동'),
           setv('_mk', 0),
           if_(gt(V('s31_길이'), 1), if_(eq(t_, LGET('s31_길', sub(V('s31_길이'), 1))), setv('_mk', 1))),
           if_(and_(ge(t_, 1), le(t_, 25)),
               ifelse(eq(V('_mk'), 1), undo,
                      [ifelse(and_(eq(LGET('s31_칸', t_), 0), adj),
                              [chg('s31_길이', 1), lst_set('s31_길', V('s31_길이'), t_), lst_set('s31_칸', t_, 1),
                               setv('s31_머리', t_), chg('s31_남은', -1), *check_free, status,
                               cast('s31_판갱신'), cast('s31_전진')],
                              [cast('s31_못감')])])))
    for kc, cond, d in ((K_LEFT, gt(mod(sub(h, 1), N), 0), -1), (K_RIGHT, lt(mod(sub(h, 1), N), N - 1), 1),
                        (K_UP, gt(h, N), -N), (K_DOWN, le(h, 25 - N), N)):
        mgr.on(on_key(kc), if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)),
                               ifelse(cond, [setv('s31_목표', add(h, d))], [setv('s31_목표', 0)]), cast('s31_이동')))
    load = [*[lst_set('s31_칸', k, char_at(V('s31_판'), k)) for k in range(1, 26)],
            lst_set('s31_칸', V('s31_시작칸'), 1), lst_set('s31_길', 1, V('s31_시작칸')), setv('s31_길이', 1),
            setv('s31_머리', V('s31_시작칸')), setv('s31_남은', sub(V('s31_총'), 1)), *check_free, status,
            cast('s31_판갱신'), cast('s31_새판')]
    button(P, m.sc, 's31_되돌리기', '↶ 되돌리기', RX, -46, 108, 24, 'steel', actions=undo)
    button(P, m.sc, 's31_처음', '처음부터', RX, -74, 108, 24, 'gray',
           actions=[if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)), *load)])
    ok = m.S('s31_성공', K.big_text('방제 완료!', 32, 'royal'), BX, BY, visible=False)
    ok.on(on_msg('s31_성공'), ok.pct(40), show(), rep(6, ok.grow_pct(10), wait(0.016)), wait(0.8), hide())
    mgr.on(on_msg('게임시작'), setv('라운드', 1),
           until(or_(gt(V('라운드'), R), eq(V('게임중'), 0)),
                 setv('_mi', add(mul(sub(V('라운드'), 1), 5), rnd(1, 5))),
                 setv('s31_판', LGET('s31_퍼즐', V('_mi'))), setv('s31_시작칸', LGET('s31_시작', V('_mi'))),
                 setv('s31_총', LGET('s31_칸수', V('_mi'))), *load, setv('입력가능', 1),
                 wait_until(or_(eq(V('s31_남은'), 0), eq(V('게임중'), 0))),
                 setv('입력가능', 0),
                 if_(eq(V('s31_남은'), 0), chg('맞춤', 1), cast('s31_성공'), wait(1.2)),
                 chg('라운드', 1)),
           *m.end_blocks(add(mul(V('맞춤'), 27), mul(V('남은시간'), 0.35))))
    mgr.on(on_msg('시간끝'), setv('입력가능', 0),
           *m.end_blocks(add(mul(V('맞춤'), 27), mul(div(sub(V('s31_길이'), 1), sub(V('s31_총'), 1)), 14))))
    m.on_start(setv('맞춤', 0), setv('입력가능', 0), setv('s31_길이', 1), setv('s31_남은', 0), setv('s31_빈이웃', 1),
               setv('s31_머리', 13), *[lst_set('s31_칸', k, 0) for k in range(1, 26)])
    m.snd('s31_전진', play('tick'))
    m.snd('s31_되돌림', play('pop'))
    m.snd('s31_못감', play('beep'))
    m.snd('s31_성공', play('good'))
    m.finish('드론이 모든 논을 딱 한 번씩 지나가며 약을 뿌려야 해요.\n집·나무 칸은 못 가요. 한붓그리기 논 3판!',
             '조작: 드론 옆 논을 클릭 (또는 방향키)  ·  지나온 칸을 누르면 되돌리기')
    return True


# ================================================================== 33. 물수제비 (던지기)
@game(33)
def g33(P, ctx):
    TL, NT = 50, 5
    WY = -50            # 물 높이
    m = mg(P, ctx, T, 33, time_limit=TL, status='던지기 1/%d' % NT, dim=40)
    vars_(P, 's33_각도', 's33_힘', 's33_단계', 's33_t0', 's33_던짐', 's33_튐', 's33_목표튐', 's33_hop', 's33_h', 's33_k', 's33_sx')
    P.var('s33_글', '')
    m.S('s33_물결', AD.s33_water(), 20, WY + 1)
    m.S('s33_둑', AD.s33_bank(), -186, -76)
    me = m.S('s33_나', ctx['BUST']['me'], -206, -64, scale=0.42)
    me.on(on_msg('s33_던지기'), rep(3, rot_by(-6), wait(0.02)), rep(3, rot_by(6), wait(0.02)))
    # 각도계와 힘 막대
    GX, GY = -196, 40
    m.S('s33_각도계', AD.s33_gauge(), GX, GY)
    nd = m.S('s33_바늘', AD.s33_needle(), GX, GY)
    m.T('s33_각도글', '각도', GX + 18, GY - 12, 8, C_DIM, F_BODY, True, 0, w=40, h=12)
    PX, PY, PH = -112, 50, 96
    m.S('s33_힘막대', AD.s33_power(PH), PX, PY)
    mk = m.S('s33_힘표시', AD.s33_marker(), PX - 14, PY - PH / 2)
    m.T('s33_힘글', '힘', PX, PY - PH / 2 - 10, 8, C_DIM, F_BODY, True, 0, w=30, h=12)
    stone = m.S('s33_돌', AD.s33_stone(), -186, -16, scale=1.2)
    splash = m.S('s33_물보라', AD.s33_splash(), 0, WY, visible=False)
    splash.local('복제', 0)
    splash.on(on_msg('s33_첨벙'), clone_self())
    splash.on(on_clone(), setv('복제', 1), xy(V('s33_sx'), add(WY, 6)), splash.pct(55), fx('transparency', 0), show(),
              rep(8, splash.grow_pct(8), fx_add('transparency', 11), wait(0.03)), del_clone())
    big = m.S('s33_퐁당', AD.s33_splash(), 0, WY, visible=False)
    big.on(on_msg('s33_퐁당'), xy(V('s33_sx'), add(WY, 10)), big.pct(90), fx('transparency', 0), show(),
           rep(10, big.grow_pct(9), fx_add('transparency', 9), wait(0.03)), hide())
    cnt = m.T('s33_횟수', '', 0, 20, 16, C_WHITE, F_NUM, False, 0, w=200, h=24)
    res = m.T('s33_결과', '', 40, 64, 14, C_ACC, F_NUM, False, 0, w=300, h=22)
    res.on(on_msg('s33_결과'), write(V('s33_글')), show(), wait(1.1), write(''))
    guide = m.T('s33_안내', '', 30, -112, 10, C_WHITE, F_BODY, True, 0, w=320, h=16)
    guide.on(on_msg('s33_안내'), ifelse(eq(V('s33_단계'), 1), [write('① 바늘이 초록 칸(20°)에 오면 클릭/스페이스!')],
                                        [ifelse(eq(V('s33_단계'), 2), [write('② 힘이 초록 네모에 오면 클릭/스페이스!')], [write('')])]))
    # 흔들리는 바늘과 힘
    mgr = hidden(m, 's33_담당')
    spd = add(170, mul(V('s33_던짐'), 22))
    mgr.on(on_msg('게임시작'), setv('s33_던짐', 0), setv('s33_단계', 1), setv('s33_t0', timer()), cast('s33_안내'),
           until(eq(V('게임중'), 0),
                 if_(eq(V('s33_단계'), 1), setv('s33_각도', mul(30, sub(1, cos_(mul(sub(timer(), V('s33_t0')), spd))))),
                     setv('s33_힘', 0)),
                 if_(eq(V('s33_단계'), 2), setv('s33_힘', mul(50, sub(1, cos_(mul(sub(timer(), V('s33_t0')), add(spd, 60))))))),
                 wait(0.016)))
    nd.on(on_msg('게임시작'), until(eq(V('게임중'), 0), rot(mul(V('s33_각도'), -1)), wait(0.016)))
    mk.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ly(add(PY - PH / 2 + 3, mul(V('s33_힘'), (PH - 6) / 100.0))), wait(0.016)))
    press = [if_(eq(V('게임중'), 1),
                 ifelse(eq(V('s33_단계'), 1), [setv('s33_단계', 2), setv('s33_t0', timer()), cast('s33_딸깍'), cast('s33_안내')],
                        [if_(eq(V('s33_단계'), 2), setv('s33_단계', 3), cast('s33_딸깍'), cast('s33_안내'), cast('s33_던지기'))]))]
    mgr.on(on_key(K_SPACE), *press)
    mgr.on(on_mouse_down(), *press)
    # 튀는 횟수 계산과 돌 날리기
    q_ang = sub(1, div(abs_(sub(V('s33_각도'), 20)), 20))
    q_pow = sub(1, div(abs_(sub(V('s33_힘'), 86)), 45))
    fly = [setv('_ma', q_ang), if_(lt(V('_ma'), 0), setv('_ma', 0)),
           setv('_mb', q_pow), if_(lt(V('_mb'), 0), setv('_mb', 0)),
           setv('s33_목표튐', rounded(mul(mul(13, V('_ma')), V('_mb')))),
           if_(gt(V('s33_각도'), 42), setv('s33_목표튐', 0)),
           setv('s33_튐', 0), xy(-186, -16), show(),
           # 첫 비행: 둑에서 물까지 (각도가 클수록 높이 뜬다)
           setv('s33_h', add(14, mul(V('s33_각도'), 1.4))), setv('s33_k', 0),
           rep(12, chg('s33_k', 1), lx(add(-186, mul(V('s33_k'), 4))),
               ly(add(add(-16, mul(V('s33_k'), (WY + 16) / 12.0)), mul(V('s33_h'), sin_(mul(V('s33_k'), 15))))), rot_by(30),
               wait(0.016)),
           setv('s33_hop', add(26, mul(V('s33_힘'), 0.4))),
           until(ge(V('s33_튐'), V('s33_목표튐')),
                 chg('s33_튐', 1), setv('s33_sx', obj_x()), cast('s33_첨벙'), cast('s33_튐소리'),
                 setv('s33_h', mul(V('s33_hop'), 0.32)), setv('_mx', obj_x()), setv('s33_k', 0),
                 rep(8, chg('s33_k', 1), lx(add(V('_mx'), mul(V('s33_hop'), div(V('s33_k'), 8)))),
                     ly(add(WY, mul(V('s33_h'), sin_(mul(V('s33_k'), 22.5))))), rot_by(40), wait(0.016)),
                 setv('s33_hop', mul(V('s33_hop'), 0.83))),
           setv('s33_sx', obj_x()), cast('s33_퐁당'), rep(6, mvy(-2), fx_add('transparency', 16), wait(0.02)), hide(), fx('transparency', 0),
           chg('합계', V('s33_튐')), chg('s33_던짐', 1),
           ifelse(eq(V('s33_튐'), 0), [setv('s33_글', '퐁당... 0번')], [setv('s33_글', join(V('s33_튐'), '번 튀었다!'))]),
           cast('s33_결과'),
           setv('미니표시', join('던지기 ', V('s33_던짐'), '/', NT, ' · 합계 ', V('합계'))),
           wait(1.0),
           ifelse(ge(V('s33_던짐'), NT), [*m.end_blocks(mul(V('합계'), 1.7))],
                  [xy(-186, -16), show(), setv('s33_단계', 1), setv('s33_t0', timer()), cast('s33_안내')])]
    stone.on(on_msg('s33_던지기'), *fly)
    cnt.on(on_msg('s33_튐소리'), write(join(V('s33_튐'), '!')))
    cnt.on(on_msg('s33_결과'), wait(1.0), write(''))
    mgr.on(on_msg('시간끝'), setv('s33_단계', 0), *m.end_blocks(mul(V('합계'), 1.7)))
    m.on_start(setv('합계', 0), setv('s33_던짐', 0), setv('s33_단계', 0), setv('s33_각도', 0), setv('s33_힘', 0))
    m.snd('s33_딸깍', play('click'))
    m.snd('s33_튐소리', play('tick'))
    m.snd('s33_퐁당', play('splash'))
    m.finish('미호천 징검다리에서 물수제비! 바늘이 20° 근처일 때 멈추고,\n힘은 초록 네모에 맞추세요. 5번 던져 튄 횟수를 모아요.',
             '조작: 클릭 또는 스페이스 두 번 (① 각도 멈추기 → ② 힘 멈추기)')
    return True


# ================================================================== 35. BRT 정차 (제동)
@game(35)
def g35(P, ctx):
    TL = 80
    STOPS = [(40, 70), (50, 88), (60, 110), (45, 62), (55, 100)]      # (처음 속도 km/h, 정류장까지 m)
    NS = len(STOPS)
    PXM = 3.0          # 1m = 3px
    BUSX, BUSY = -70, -52
    DOORX = BUSX + 86 - 31          # 앞문 가운데 (버스 그림 기준)
    ROADY = -82
    m = mg(P, ctx, T, 35, time_limit=TL, status='정류장 1/%d' % NS, dim=60)
    P.list('s35_속도', [round(v / 3.6, 3) for v, d in STOPS])
    P.list('s35_거리', [d for v, d in STOPS])
    vars_(P, 's35_v', 's35_d', 's35_압', 's35_감속', 's35_last', 's35_dt', 's35_정류장', 's35_정지시간', 's35_휘청', 's35_쿨',
          's35_넘어짐', 's35_달림', 's35_이동')
    P.var('s35_글', '')
    m.S('s35_도로', AD.s35_road(), 0, ROADY)
    # 배경 가로등 (복제본 5개가 거리에 맞춰 흘러감)
    post = m.S('s35_가로등', AD.s35_post(), -300, -20, visible=False)
    post.local('복제', 0)
    post.local('내번호', 0)
    post.on(on_scene(), hide(), setv('내번호', 0), rep(5, chg('내번호', 1), clone_self()))
    post.on(on_clone(), setv('복제', 1), show(),
            forever(lx(sub(mod(add(60000, sub(mul(V('내번호'), 120), mul(V('s35_이동'), PXM))), 600), 300)), wait(0.016)))
    dash = m.S('s35_차선', AD.s35_dash(), -300, ROADY - 6, visible=False)
    dash.local('복제', 0)
    dash.local('내번호', 0)
    dash.on(on_scene(), hide(), setv('내번호', 0), rep(6, chg('내번호', 1), clone_self()))
    dash.on(on_clone(), setv('복제', 1), show(),
            forever(lx(sub(mod(add(54000, sub(mul(V('내번호'), 90), mul(V('s35_이동'), PXM))), 540), 270)), wait(0.016)))
    # 정류장과 정차선
    mark_x = add(DOORX, mul(V('s35_d'), PXM))
    sh = m.S('s35_정류장', AD.s35_shelter(), 400, -27)
    sh.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(add(mark_x, 20)), wait(0.016)))
    mark = m.S('s35_정차선', AD.s35_mark(), 400, -36)
    mark.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(mark_x), wait(0.016)))
    for k, x in enumerate((22, 52)):
        rd = m.S('s35_승객%d' % k, [('a', AD.s35_rider(0)), ('b', AD.s35_rider(1))], 400, -32)
        rd.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(add(mark_x, x)), wait(0.016)))
    bus = m.S('s35_버스', AD.s35_bus(), BUSX, BUSY)
    bus.on(on_msg('게임시작'), until(eq(V('게임중'), 0), rot(mul(V('s35_감속'), 0.7)), ly(add(BUSY, mul(V('s35_감속'), -0.4))), wait(0.016)))
    bus.on(on_msg('s35_넘어짐'), rep(3, mvx(3), wait(0.02), mvx(-3), wait(0.02)))
    # 계기판
    panel(P, m.sc, 's35_계기판', 0, 70, 300, 52, 'glass')
    spd = m.T('s35_속도글', '', -90, 78, 15, C_WHITE, F_NUM, False, 0, w=110, h=22)
    dist = m.T('s35_거리글', '', 50, 78, 15, C_ACC, F_NUM, False, 0, w=150, h=22)
    m.T('s35_속도이름', '속도', -90, 60, 8, C_DIM, F_BODY, True, 0, w=80, h=12)
    m.T('s35_거리이름', '정차선까지', 50, 60, 8, C_DIM, F_BODY, True, 0, w=100, h=12)
    bar = m.S('s35_브레이크', K.bar_set('s35_brake', 80, 8, 'red'), 110, 60)
    m.T('s35_브글', '브레이크', 110, 72, 8, C_DIM, F_BODY, True, 0, w=70, h=12)
    spd.on(on_msg('게임시작'), until(eq(V('게임중'), 0), write(join(rounded(mul(V('s35_v'), 3.6)), ' km/h')), wait(0.08)))
    dist.on(on_msg('게임시작'), until(eq(V('게임중'), 0), write(join(div(rounded(mul(V('s35_d'), 10)), 10), ' m')), wait(0.08)))
    bar.on(on_msg('게임시작'), until(eq(V('게임중'), 0), shape(add(rounded(mul(V('s35_압'), 40)), 1)), wait(0.05)))
    res = m.T('s35_결과', '', 0, 6, 15, C_WHITE, F_NUM, False, 0, w=360, h=44)
    res.on(on_msg('s35_판정'), write(V('s35_글')), show(), wait(1.6), write(''))
    warn = m.S('s35_휘청글', K.big_text('승객이 휘청!', 20, 'red'), BUSX, -4, visible=False)
    warn.on(on_msg('s35_넘어짐'), show(), wait(0.7), hide())
    # 주행 (시간 기준 물리)
    mgr = hidden(m, 's35_담당')
    braking = and_(key(K_SPACE), eq(V('s35_달림'), 1))
    phys = [setv('s35_dt', sub(timer(), V('s35_last'))), setv('s35_last', timer()),
            if_(gt(V('s35_dt'), 0.1), setv('s35_dt', 0.1)),
            ifelse(braking, [chg('s35_압', mul(V('s35_dt'), 1.5))], [chg('s35_압', mul(V('s35_dt'), -4))]),
            *[if_(lt(V('s35_압'), 0), setv('s35_압', 0)), if_(gt(V('s35_압'), 1), setv('s35_압', 1))],
            setv('s35_감속', add(0.4, mul(V('s35_압'), 5.6))),
            ifelse(gt(V('s35_v'), 0), [chg('s35_v', mul(V('s35_감속'), mul(V('s35_dt'), -1)))], [setv('s35_감속', 0)]),
            # 브레이크를 떼면 천천히 기어간다 (자동 변속기)
            if_(and_(not_(braking), lt(V('s35_v'), 1.2)), setv('s35_v', 1.2), setv('s35_감속', 0)),
            if_(lt(V('s35_v'), 0), setv('s35_v', 0)),
            chg('s35_d', mul(V('s35_v'), mul(V('s35_dt'), -1))), chg('s35_이동', mul(V('s35_v'), V('s35_dt'))),
            # 급정거
            if_(gt(V('s35_쿨'), 0), chg('s35_쿨', mul(V('s35_dt'), -1))),
            ifelse(and_(gt(V('s35_감속'), 4.3), gt(V('s35_v'), 0.5)), [chg('s35_휘청', V('s35_dt'))], [setv('s35_휘청', 0)]),
            if_(and_(gt(V('s35_휘청'), 0.25), le(V('s35_쿨'), 0)), chg('s35_넘어짐', 1), setv('s35_쿨', 1.2), cast('s35_넘어짐')),
            ifelse(eq(V('s35_v'), 0), [chg('s35_정지시간', V('s35_dt'))], [setv('s35_정지시간', 0)])]
    judge = [setv('s35_달림', 0), setv('_ma', abs_(V('s35_d'))),
             setv('_mb', sub(14, mul(V('_ma'), 5))), if_(lt(V('_mb'), 0), setv('_mb', 0)),
             setv('_mk', sub(6, mul(V('s35_넘어짐'), 3))), if_(lt(V('_mk'), 0), setv('_mk', 0)),
             chg('합계', add(V('_mb'), V('_mk'))),
             ifelse(lt(V('_ma'), 0.5), [setv('s35_글', join('딱 맞춤! 오차 ', div(rounded(mul(V('_ma'), 100)), 100), 'm'))],
                    [ifelse(gt(V('s35_d'), 0), [setv('s35_글', join('조금 덜 갔어요 (', div(rounded(mul(V('_ma'), 10)), 10), 'm)'))],
                            [setv('s35_글', join('조금 지나쳤어요 (', div(rounded(mul(V('_ma'), 10)), 10), 'm)'))])]),
             setv('s35_글', join(V('s35_글'), '\n+', rounded(add(V('_mb'), V('_mk'))), '점')),
             cast('s35_판정'), ifelse(lt(V('_ma'), 1), [cast('s35_좋음')], [cast('s35_보통')])]
    mgr.on(on_msg('게임시작'), setv('s35_정류장', 0),
           until(or_(ge(V('s35_정류장'), NS), eq(V('게임중'), 0)),
                 chg('s35_정류장', 1),
                 setv('s35_v', LGET('s35_속도', V('s35_정류장'))), setv('s35_d', LGET('s35_거리', V('s35_정류장'))),
                 setv('s35_압', 0), setv('s35_넘어짐', 0), setv('s35_휘청', 0), setv('s35_쿨', 0), setv('s35_정지시간', 0),
                 setv('미니표시', join('정류장 ', V('s35_정류장'), '/', NS, ' · ', rounded(V('합계')), '점')),
                 setv('s35_last', timer()), setv('s35_달림', 1),
                 until(or_(or_(gt(V('s35_정지시간'), 0.8), lt(V('s35_d'), -6)), eq(V('게임중'), 0)), *phys),
                 if_(eq(V('게임중'), 1),
                     ifelse(lt(V('s35_d'), -6),
                            [setv('s35_달림', 0), setv('s35_글', '정류장을 지나쳤어요! 0점'), cast('s35_판정'), cast('s35_실패')],
                            judge),
                     setv('미니표시', join('정류장 ', V('s35_정류장'), '/', NS, ' · ', rounded(V('합계')), '점')),
                     setv('s35_v', 0), setv('s35_압', 0), setv('s35_감속', 0), wait(1.7))),
           *m.end_blocks(V('합계')))
    mgr.on(on_msg('시간끝'), setv('s35_달림', 0), *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('s35_v', 0), setv('s35_d', 60), setv('s35_압', 0), setv('s35_감속', 0), setv('s35_이동', 0),
               setv('s35_달림', 0))
    m.snd('s35_넘어짐', play('hit'))
    m.snd('s35_좋음', play('good'))
    m.snd('s35_보통', play('coin'))
    m.snd('s35_실패', play('bad'))
    m.finish('BRT 버스 앞문을 빨간 ▼ 정차선에 딱 맞춰 세우세요!\n세게 오래 밟으면 승객이 휘청해요. 정류장 5곳.',
             '조작: 스페이스를 누르는 동안 브레이크 (오래 누를수록 세짐)\n떼면 천천히 굴러가요 · 멈춘 뒤 잠깐 더 누르고 있으면 정차 완료')
    return True


# ================================================================== 37. 떡메치기 (박자)
@game(37)
def g37(P, ctx):
    TL = 25
    CX, CY = 10, -56
    m = mg(P, ctx, T, 37, time_limit=TL, status='콤보 0', dim=70)
    vars_(P, 's37_손', 's37_쿨', 's37_콤보', 's37_최고', 's37_뒤집기')
    m.S('s37_떡판', AD.s37_board(), CX, CY - 20)
    cake = m.S('s37_떡', [('round', AD.s37_cake('round')), ('flat', AD.s37_cake('flat')), ('tall', AD.s37_cake('tall'))], CX, CY)
    cake.on(on_msg('s37_쿵'), shape('flat'), wait(0.08), shape('round'))
    cake.on(on_msg('s37_손안'), wait(0.15), shape('tall'), flip_x(), wait(0.2), shape('round'))
    m.S('s37_나', ctx['BUST']['me'], -150, -44, scale=0.42)
    mal = m.S('s37_떡메', [('up', AD.s37_mallet('up')), ('down', AD.s37_mallet('down'))], CX - 36, 0)
    OUT, RISE, IN = (204, -36), (156, 16), (CX + 50, CY + 2)
    hand = m.S('s37_손', [('flat', AD.s37_hand('flat')), ('ouch', AD.s37_hand('ouch'))], OUT[0], OUT[1])

    def glide_to(o, x, y, n=5):
        return [setv('_ma', obj_x()), setv('_mb', obj_y()), *[xy(add(V('_ma'), mul(sub(x, V('_ma')), (k + 1) / float(n))),
                                                               add(V('_mb'), mul(sub(y, V('_mb')), (k + 1) / float(n))))
                                                             for k in range(n)]]
    hand.local('_ma', 0)
    hand.local('_mb', 0)
    hand.on(on_msg('s37_손위'), *flat([[b, wait(0.016)] for b in glide_to(hand, *RISE, n=6)]))
    hand.on(on_msg('s37_손안'), *flat([[b, wait(0.016)] for b in glide_to(hand, *IN, n=5)]))
    hand.on(on_msg('s37_손밖'), *flat([[b, wait(0.016)] for b in glide_to(hand, *OUT, n=6)]))
    hand.on(on_msg('s37_아야'), shape('ouch'), rep(3, mvx(4), wait(0.03), mvx(-4), wait(0.03)), wait(0.3), shape('flat'))
    hand.on(on_scene(), xy(*OUT), shape('flat'))
    warn = m.S('s37_조심', AD.s37_warn(), RISE[0] - 30, RISE[1] + 30, visible=False)
    warn.on(on_msg('s37_손위'), show(), warn.pct(70), rep(4, warn.grow_pct(8), wait(0.02)))
    warn.on(on_msg('s37_손안'), hide())
    warn.on(on_msg('s37_손밖'), hide())
    combo = m.T('s37_콤보글', '', CX, 60, 16, C_WHITE, F_NUM, False, 0, w=200, h=24)
    combo.on(on_msg('s37_갱신'), ifelse(ge(V('s37_콤보'), 3), [write(join(V('s37_콤보'), ' COMBO'))], [write('')]),
             setv('미니표시', join('떡메 ', V('합계'), ' · 콤보 ', V('s37_콤보'))))
    G.big_pop(P, m.sc, 's37_아야글', K.big_text('아야!', 34, 'red'), 120, 40, 's37_아야', hold=0.4)
    thud = m.S('s37_쿵글', K.big_text('쿵!', 18, 'white'), CX - 50, CY + 30, visible=False)
    thud.on(on_msg('s37_쿵'), xy(add(CX - 60, rnd(-10, 10)), add(CY + 30, rnd(-4, 8))), thud.pct(70), fx('transparency', 0), show(),
            rep(6, thud.grow_pct(8), fx_add('transparency', 12), wait(0.02)), hide())
    # 손 움직임 (불규칙한 박자 + 손이 먼저 들리는 신호)
    mgr = hidden(m, 's37_담당')
    mgr.on(on_msg('게임시작'),
           until(eq(V('게임중'), 0),
                 setv('s37_손', 0),
                 wait(add(div(rnd(55, 150), 100), mul(V('남은시간'), 0.012))),
                 if_(eq(V('게임중'), 1),
                     setv('s37_손', 1), cast('s37_손위'), wait(0.42),
                     ifelse(and_(lt(V('남은시간'), 17), le(rnd(1, 100), 25)),
                            [setv('s37_손', 3), cast('s37_손밖'), wait(0.15)],
                            [setv('s37_손', 2), cast('s37_손안'), wait(0.5), setv('s37_손', 3), cast('s37_손밖'), wait(0.15)]))))
    # 내리치기
    strike = [if_(and_(eq(V('게임중'), 1), eq(V('s37_쿨'), 0)),
                  setv('s37_쿨', 1), wait(0.05), shape('down'),
                  ifelse(or_(eq(V('s37_손'), 1), eq(V('s37_손'), 2)),
                         [chg('실패', 1), setv('s37_콤보', 0), cast('s37_아야'), cast('s37_갱신')],
                         [chg('합계', 1), chg('s37_콤보', 1), if_(gt(V('s37_콤보'), V('s37_최고')), setv('s37_최고', V('s37_콤보'))),
                          cast('s37_쿵'), cast('s37_갱신')]),
                  wait(0.1), shape('up'), wait(0.02), setv('s37_쿨', 0))]
    mal.on(on_key(K_SPACE), *strike)
    mal.on(on_scene(), shape('up'))
    score = sub(add(mul(V('합계'), 1.6), mul(V('s37_최고'), 0.3)), mul(V('실패'), 7))
    mgr.on(on_msg('시간끝'), *m.end_blocks(score))
    m.on_start(setv('합계', 0), setv('실패', 0), setv('s37_콤보', 0), setv('s37_최고', 0), setv('s37_쿨', 0), setv('s37_손', 0))
    m.snd('s37_쿵', play('hit'))
    m.snd('s37_아야', play('bad'))
    m.snd('s37_손안', play('pop'))
    m.finish('스페이스로 떡메를 내리쳐 떡을 쳐요! 손이 들리면(!) 곧 떡을\n뒤집으러 들어와요. 손이 빠졌을 때만 치세요. 손을 치면 -7점!',
             '조작: 스페이스 = 떡메 치기  ·  손이 들어오는 동안은 멈추기')
    return True


# ================================================================== 38. 간판 글자 맞추기 (단어)
S38_WORDS = [('행복약국', '아플 때 약을 사요', '방'), ('세종서점', '책을 사요', '문'), ('도담분식', '떡볶이·김밥', '밥'),
             ('한솔치킨', '바삭한 닭튀김', '피'), ('새롬안경', '눈이 잘 보이게', '눈'), ('보람꽃집', '꽃다발을 사요', '화'),
             ('나성제과', '빵과 케이크', '빵'), ('아름미용실', '머리를 잘라요', '발'), ('종촌세탁소', '옷을 깨끗하게', '빨'),
             ('고운문구', '공책·연필', '점'), ('소담수산', '싱싱한 생선', '어'), ('다정반찬', '집밥 반찬', '국'),
             ('대평떡집', '떡을 팔아요', '방'), ('가람정육점', '고기를 팔아요', '고')]


@game(38)
def g38(P, ctx):
    TL, NW, NT = 60, 8, 6
    NWORD = len(S38_WORDS)
    m = mg(P, ctx, T, 38, time_limit=TL, status='간판 0/%d' % NW, dim=90)
    P.list('s38_단어', [w for w, h, x in S38_WORDS])
    P.list('s38_힌트', [h for w, h, x in S38_WORDS])
    P.list('s38_글자', [w + x for w, h, x in S38_WORDS])
    P.list('s38_순서', list(range(1, NWORD + 1)))
    P.list('s38_타일', [''] * NT)
    P.list('s38_씀', [0] * NT)
    vars_(P, 's38_번째', 's38_진행', 's38_개수', 's38_길이', 's38_누른', 's38_틀림')
    for v in ('s38_말', 's38_답'):
        P.var(v, '')
    sign = m.S('s38_간판', [('off', AD.s38_sign('off')), ('on', AD.s38_sign('on'))], 0, 52)
    sign.on(on_msg('s38_새단어'), shape('off'))
    sign.on(on_msg('s38_정답'), shape('on'))
    word = m.T('s38_간판글', '', 0, 52, 26, C_WHITE, F_NUM, False, 0, w=280, h=36)
    shown = join(substr(V('s38_답'), 1, V('s38_진행')), substr('○○○○○', 1, sub(V('s38_길이'), V('s38_진행'))))
    word.on(on_msg('s38_갱신'), ifelse(eq(V('s38_진행'), 0), [write(substr('○○○○○', 1, V('s38_길이')))], [write(shown)]))
    hint = m.T('s38_힌트글', '', 0, 6, 13, C_ACC, F_BODY, True, 0, w=360, h=20)
    hint.on(on_msg('s38_새단어'), write(join('힌트: ', LGET('s38_힌트', LGET('s38_순서', V('s38_번째'))), ' (', V('s38_길이'), '글자)')))
    m.T('s38_도움', '글자 하나는 가짜예요!', 0, -14, 9, C_DIM, F_BODY, True, 0, w=200, h=14)
    TY = -56
    for k in range(1, NT + 1):
        tx = mul(sub(k, div(add(V('s38_개수'), 1), 2)), 54)
        tl = m.S('s38_타일%d' % k, [('n', AD.s38_tile('n')), ('u', AD.s38_tile('u')), ('x', AD.s38_tile('x')), ('g', AD.s38_tile('g'))], 0, TY)
        tt = m.T('s38_타일글%d' % k, '', 0, TY + 3, 22, '#1A1F3A', F_NUM, False, 0, w=44, h=40)
        act = [if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)), if_(eq(LGET('s38_씀', k), 0), setv('s38_누른', k), cast('s38_누름')))]
        for o in (tl, tt):
            o.on(on_msg('s38_새단어'), ifelse(le(k, V('s38_개수')), [lx(tx), show()], [hide()]))
            o.on(on_click(), *act)
            o.on(on_scene(), hide())
        tt.on(on_msg('s38_새단어'), write(LGET('s38_타일', k)))
        tl.on(on_msg('s38_갱신'), ifelse(eq(LGET('s38_씀', k), 1), [shape('u')], [shape('n')]))
        tl.on(on_msg('s38_틀림'), if_(eq(V('s38_누른'), k), shape('x'), rep(3, mvx(4), wait(0.03), mvx(-4), wait(0.03))))
        tl.on(on_msg('s38_정답'), shape('g'))
        tl.on(on_click(), if_(eq(V('입력가능'), 1), tl.pct(90), wait(0.06), tl.pct(100)))
    # 단어 시작: 글자를 섞어 늘어놓기
    gl = LGET('s38_글자', LGET('s38_순서', V('s38_번째')))
    newword = [setv('s38_답', LGET('s38_단어', LGET('s38_순서', V('s38_번째')))), setv('s38_길이', slen(V('s38_답'))),
               setv('s38_개수', add(V('s38_길이'), 1)), setv('s38_진행', 0),
               *[lst_set('s38_타일', k, char_at(gl, k)) for k in range(1, NT + 1)],
               *[lst_set('s38_씀', k, 0) for k in range(1, NT + 1)]]
    for k in range(NT, 1, -1):
        newword.append(if_(le(k, V('s38_개수')), setv('_mk', rnd(1, k)), setv('_mv', LGET('s38_타일', k)),
                           lst_set('s38_타일', k, LGET('s38_타일', V('_mk'))), lst_set('s38_타일', V('_mk'), V('_mv'))))
    newword += [cast('s38_새단어'), cast('s38_갱신'), setv('입력가능', 1)]
    status = setv('미니표시', join('간판 ', V('맞춤'), '/', NW))
    mgr = hidden(m, 's38_담당')
    mgr.on(on_msg('s38_누름'),
           ifelse(eq(LGET('s38_타일', V('s38_누른')), char_at(V('s38_답'), add(V('s38_진행'), 1))),
                  [lst_set('s38_씀', V('s38_누른'), 1), chg('s38_진행', 1), cast('s38_갱신'), cast('s38_딸깍'),
                   if_(eq(V('s38_진행'), V('s38_길이')), setv('입력가능', 0), chg('맞춤', 1), status, cast('s38_정답'))],
                  [chg('s38_틀림', 1), setv('입력가능', 0), cast('s38_틀림'), wait(0.35),
                   setv('s38_진행', 0), *[lst_set('s38_씀', k, 0) for k in range(1, NT + 1)], cast('s38_갱신'), setv('입력가능', 1)]))
    mgr.on(on_msg('s38_정답'), wait(0.9), setv('s38_진행', 0), cast('s38_다음'))
    mgr.on(on_msg('s38_다음'), if_(eq(V('게임중'), 1),
                                  ifelse(ge(V('s38_번째'), NW), [*m.end_blocks(add(mul(V('맞춤'), 11), mul(V('남은시간'), 0.4)))],
                                         [chg('s38_번째', 1), *newword])))
    skip = [if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)), setv('입력가능', 0), cast('s38_다음'))]
    button(P, m.sc, 's38_넘기기', '모르겠어요 → 넘기기', 0, -100, 150, 24, 'steel', actions=skip)
    mgr.on(on_msg('게임시작'), setv('s38_번째', 1), *newword)
    mgr.on(on_msg('시간끝'), setv('입력가능', 0), *m.end_blocks(mul(V('맞춤'), 11)))
    shuffle = []
    for k in range(NWORD, 1, -1):
        shuffle += [setv('_mk', rnd(1, k)), setv('_mv', LGET('s38_순서', k)), lst_set('s38_순서', k, LGET('s38_순서', V('_mk'))),
                    lst_set('s38_순서', V('_mk'), V('_mv'))]
    m.on_start(setv('맞춤', 0), setv('s38_틀림', 0), setv('입력가능', 0), setv('s38_번째', 1), setv('s38_진행', 0), setv('s38_길이', 4),
               *shuffle)
    m.snd('s38_딸깍', play('tick'))
    m.snd('s38_틀림', play('bad'))
    m.snd('s38_정답', play('good'))
    m.finish('도담동 상가 간판 글자가 뒤죽박죽! 힌트를 보고 가게 이름을\n알아내 첫 글자부터 차례로 누르세요. 가짜 글자도 하나 있어요.',
             '조작: 글자 클릭  ·  틀리면 그 간판은 처음부터  ·  간판 8개, 60초')
    return True


# ================================================================== 39. 숫자 합 10 (숫자 퍼즐)
def _s39_boards(n=6, C=10, R=6):
    rng = random.Random(3939)

    def parts(k):
        while True:
            p = [rng.randint(1, 9) for _ in range(k - 1)]
            if sum(p) <= 10 - 1:
                p.append(10 - sum(p))
                if max(p) <= 9:
                    rng.shuffle(p)
                    return p
    out = []
    while len(out) < n:
        g = [[0] * C for _ in range(R)]
        ok = True
        for r in range(R):
            for c in range(C):
                if g[r][c]:
                    continue
                shapes = [(1, 2), (2, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2)]
                rng.shuffle(shapes)
                for h, w in shapes:
                    if r + h <= R and c + w <= C and all(g[r + i][c + j] == 0 for i in range(h) for j in range(w)):
                        p = parts(h * w)
                        for i in range(h):
                            for j in range(w):
                                g[r + i][c + j] = p[i * w + j]
                        break
                else:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            out.append(''.join(str(g[r][c]) for r in range(R) for c in range(C)))
    return out


@game(39)
def g39(P, ctx):
    TL, C, R, CL = 60, 10, 6, 30
    X0, Y0 = -135 - 20, 70
    m = mg(P, ctx, T, 39, time_limit=TL, status='지운 칸 0', dim=90)
    boards = _s39_boards()
    P.list('s39_판들', boards)
    P.list('s39_칸', [0] * (C * R))
    P.list('s39_x', [X0 + (k % C) * CL for k in range(C * R)])
    P.list('s39_y', [Y0 - (k // C) * CL for k in range(C * R)])
    vars_(P, 's39_x1', 's39_y1', 's39_c1', 's39_c2', 's39_r1', 's39_r2', 's39_합', 's39_끌기', 's39_k', 's39_r', 's39_c', 's39_px', 's39_py')
    P.var('s39_판', '')
    panel(P, m.sc, 's39_판넬', X0 + (C - 1) * CL / 2, Y0 - (R - 1) * CL / 2, C * CL + 14, R * CL + 14, 'glass')
    dg = m.S('s39_숫자', [('d%d' % k, AD.s39_digit(k)) for k in range(10)], -300, -300)
    dg.on(on_msg('s39_그리기'), pen_clear(), show(), setv('s39_k', 0),
          rep(C * R, chg('s39_k', 1), xy(LGET('s39_x', V('s39_k')), LGET('s39_y', V('s39_k'))),
              shape(add(LGET('s39_칸', V('s39_k')), 1)), B('brush_stamp')), xy(-300, -300))
    pop = m.S('s39_펑', AD.s39_pop(), -300, -300, visible=False)
    pop.on(on_msg('s39_펑'), clone_self())
    pop.on(on_clone(), xy(V('s39_px'), V('s39_py')), pop.pct(50), fx('transparency', 0), show(),
           rep(8, pop.grow_pct(12), fx_add('transparency', 12), wait(0.025)), del_clone())
    # 지우기: 네모 안 칸을 빈칸 그림으로 덮어 찍는다
    idx = add(add(mul(V('s39_r'), C), V('s39_c')), 1)
    dg.on(on_msg('s39_지우기'),
          setv('s39_r', V('s39_r1')),
          until(gt(V('s39_r'), V('s39_r2')),
                setv('s39_c', V('s39_c1')),
                until(gt(V('s39_c'), V('s39_c2')),
                      if_(gt(LGET('s39_칸', idx), 0),
                          lst_set('s39_칸', idx, 0), chg('합계', 1), xy(LGET('s39_x', idx), LGET('s39_y', idx)), shape('d0'),
                          B('brush_stamp'), setv('s39_px', obj_x()), setv('s39_py', obj_y()), cast('s39_펑')),
                      chg('s39_c', 1)),
                chg('s39_r', 1)),
          xy(-300, -300), setv('미니표시', join('지운 칸 ', V('합계'))))
    # 끌어서 네모 고르기
    cx = lambda x: floor(div(add(sub(x, X0), CL / 2.0), CL))
    ry = lambda y: floor(div(add(sub(Y0, y), CL / 2.0), CL))
    clampc = lambda v, hi: [if_(lt(V(v), 0), setv(v, 0)), if_(gt(V(v), hi), setv(v, hi))]
    rng_ = [setv('s39_c1', cx(V('s39_x1'))), setv('s39_c2', cx(mouse_x())),
            if_(gt(V('s39_c1'), V('s39_c2')), setv('_mk', V('s39_c1')), setv('s39_c1', V('s39_c2')), setv('s39_c2', V('_mk'))),
            setv('s39_r1', ry(V('s39_y1'))), setv('s39_r2', ry(mouse_y())),
            if_(gt(V('s39_r1'), V('s39_r2')), setv('_mk', V('s39_r1')), setv('s39_r1', V('s39_r2')), setv('s39_r2', V('_mk'))),
            *clampc('s39_c1', C - 1), *clampc('s39_c2', C - 1), *clampc('s39_r1', R - 1), *clampc('s39_r2', R - 1)]
    total = [setv('s39_합', 0)]
    for k in range(C * R):
        c, r = k % C, k // C
        total.append(if_(and_(le(V('s39_c1'), c), ge(V('s39_c2'), c), le(V('s39_r1'), r), ge(V('s39_r2'), r)),
                         chg('s39_합', LGET('s39_칸', k + 1))))
    sel = m.S('s39_선택', A.clear_dot(), -300, -300)
    sel.local('_ls', -1)
    L, Rr = sub(mul(V('s39_c1'), CL), CL / 2.0 - X0), add(mul(V('s39_c2'), CL), CL / 2.0 + X0)
    Tt, Bb = sub(Y0 + CL / 2.0, mul(V('s39_r1'), CL)), sub(Y0 - CL / 2.0, mul(V('s39_r2'), CL))
    rect = [pen_up(), pen_clear(), ifelse(eq(V('s39_합'), 10), [pen_color('#5CFF9A')], [pen_color('#BFD0FF')]), pen_size(3),
            xy(L, Tt), pen_down(), xy(Rr, Tt), xy(Rr, Bb), xy(L, Bb), xy(L, Tt), pen_up()]
    sumt = m.T('s39_합글', '', 196, 10, 22, C_WHITE, F_NUM, False, 0, w=80, h=30)
    m.T('s39_합이름', '고른 합', 196, 36, 9, C_DIM, F_BODY, True, 0, w=80, h=14)
    m.T('s39_목표', '목표 10', 196, -16, 10, C_ACC, F_NUM, False, 0, w=80, h=14)
    sel.on(on_msg('게임시작'),
           until(eq(V('게임중'), 0),
                 if_(eq(V('s39_끌기'), 1),
                     ifelse(mouse_down(), [*rng_, *total, *rect, if_(ne(V('s39_합'), V('_ls')), setv('_ls', V('s39_합')), cast('s39_합갱신'))],
                            [setv('s39_끌기', 0), pen_clear(),
                             ifelse(eq(V('s39_합'), 10), [cast('s39_좋음'), cast_wait('s39_지우기')],
                                    [if_(gt(V('s39_합'), 0), cast('s39_아님'))]),
                             setv('s39_합', 0), setv('_ls', -1), cast('s39_합갱신')])),
                 wait(0.016)))
    sumt.on(on_msg('s39_합갱신'), ifelse(eq(V('s39_합'), 0), [write('')], [write(V('s39_합'))]),
            ifelse(eq(V('s39_합'), 10), [text_color('#5CFF9A')], [ifelse(gt(V('s39_합'), 10), [text_color('#FF5C70')], [text_color('#FFFFFF')])]))
    mgr = hidden(m, 's39_담당')
    mgr.on(on_mouse_down(), if_(and_(eq(V('게임중'), 1), eq(V('s39_끌기'), 0)),
                                setv('s39_x1', mouse_x()), setv('s39_y1', mouse_y()), setv('s39_끌기', 1)))
    mgr.on(on_msg('시간끝'), setv('s39_끌기', 0), *m.end_blocks(mul(V('합계'), 2.2)))
    m.on_start(setv('합계', 0), setv('s39_끌기', 0), setv('s39_합', 0),
               setv('s39_판', LGET('s39_판들', rnd(1, len(boards)))),
               *[lst_set('s39_칸', k, char_at(V('s39_판'), k)) for k in range(1, C * R + 1)], cast('s39_그리기'))
    m.snd('s39_좋음', play('coin'))
    m.snd('s39_아님', play('beep'))
    m.finish('마우스로 끌어 네모를 그려서, 안에 든 숫자의 합이 딱 10이면\n그 칸들이 사라져요! 60초 동안 칸을 많이 지우세요.',
             '조작: 마우스를 누른 채 끌었다 놓기  ·  여러 칸을 한 번에 지울수록 이득')
    return True
