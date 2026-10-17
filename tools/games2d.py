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


# ================================================================== 40. 선로 전환 (교통 관리)
@game(40)
def g40(P, ctx):
    TL = 60
    N = {'E': (-262, 0), 'A': (-150, 0), 'a1': (-112, 48), 'B': (-52, 48), 'a2': (-112, -48), 'C': (-52, -48),
         'b1': (-14, 84), 'S1': (176, 84), 'b2': (-14, 16), 'S2': (176, 16), 'c1': (-14, -16), 'S3': (176, -16),
         'c2': (-14, -84), 'S4': (176, -84)}
    # (시작, 끝, 다음0, 다음1, 전환기, 역)
    E = [('E', 'A', 2, 4, 1, 0), ('A', 'a1', 3, 3, 0, 0), ('a1', 'B', 6, 8, 2, 0), ('A', 'a2', 5, 5, 0, 0), ('a2', 'C', 10, 12, 3, 0),
         ('B', 'b1', 7, 7, 0, 0), ('b1', 'S1', 0, 0, 0, 1), ('B', 'b2', 9, 9, 0, 0), ('b2', 'S2', 0, 0, 0, 2),
         ('C', 'c1', 11, 11, 0, 0), ('c1', 'S3', 0, 0, 0, 3), ('C', 'c2', 13, 13, 0, 0), ('c2', 'S4', 0, 0, 0, 4)]
    cols = dict(sx=[], sy=[], ux=[], uy=[], len=[], rot=[], n0=[], n1=[], sw=[], st=[])
    for a, b, n0, n1, sw, st in E:
        (x0, y0), (x1, y1) = N[a], N[b]
        L = math.hypot(x1 - x0, y1 - y0)
        for k, v in (('sx', x0), ('sy', y0), ('ux', round((x1 - x0) / L, 4)), ('uy', round((y1 - y0) / L, 4)), ('len', round(L, 2)),
                     ('rot', round(-math.degrees(math.atan2(y1 - y0, x1 - x0)), 2)), ('n0', n0), ('n1', n1), ('sw', sw), ('st', st)):
            cols[k].append(v)
    for k, v in cols.items():
        P.list('s40_' + k, v)
    P.list('s40_스위치', [0, 0, 0])
    vars_(P, 's40_속도', 's40_간격', 's40_새색', 's40_도착', 's40_px', 's40_py')
    P.var('s40_글', '')
    m = mg(P, ctx, T, 40, time_limit=TL, status='도착 0', dim=110)
    # 선로 (붓으로 그림)
    trk = hidden(m, 's40_선로')
    draw = [pen_up(), pen_clear()]
    for wid, col in ((12, '#1B2142'), (4, '#7F8AB4')):
        draw += [pen_size(wid), pen_color(col)]
        for a, b, *_ in E:
            draw += [xy(*N[a]), pen_down(), xy(*N[b]), pen_up()]
    trk.on(on_scene(), *draw)
    live = hidden(m, 's40_불빛')
    lit = [pen_up(), pen_clear(), pen_size(4), pen_color('#FFD45A')]
    for k, (node, up, dn) in enumerate((('A', 'a1', 'a2'), ('B', 'b1', 'b2'), ('C', 'c1', 'c2'))):
        (x0, y0) = N[node]
        for tgt, st in ((up, 0), (dn, 1)):
            x1, y1 = N[tgt]
            lit.append(if_(eq(LGET('s40_스위치', k + 1), st), xy(x0, y0), pen_down(), xy(x0 + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.75),
                           pen_up()))
    live.on(on_msg('s40_전환'), *lit)
    for k, lab in enumerate(('조치원', '세종', '대전', '청주')):
        m.S('s40_역%d' % (k + 1), AD.s40_station(k, lab), 202, N['S%d' % (k + 1)][1])
    for k, node in enumerate(('A', 'B', 'C')):
        sw = m.S('s40_전환기%d' % (k + 1), [('up', AD.s40_switch('up')), ('down', AD.s40_switch('down'))], N[node][0], N[node][1], scale=1.25)
        sw.on(on_msg('s40_전환'), shape(add(LGET('s40_스위치', k + 1), 1)))
        sw.on(on_click(), if_(eq(V('게임중'), 1), lst_set('s40_스위치', k + 1, sub(1, LGET('s40_스위치', k + 1))), cast('s40_전환'),
                              cast('s40_딸깍')))
        sw.on(on_click(), sw.pct(85), wait(0.06), sw.pct(100))
        G.hover_scripts(sw, 115)
        hidden(m, 's40_전환키%d' % (k + 1)).on(on_key((K_1, K_2, K_3)[k]),
                                             if_(eq(V('게임중'), 1), lst_set('s40_스위치', k + 1, sub(1, LGET('s40_스위치', k + 1))),
                                                 cast('s40_전환'), cast('s40_딸깍')))
        m.T('s40_전환번호%d' % (k + 1), str(k + 1), N[node][0], N[node][1] + 22, 9, C_DIM, F_NUM, False, 0, w=20, h=12)
    # 기차 (복제본)
    tr = m.S('s40_기차', [('c%d' % k, AD.s40_train(k)) for k in range(4)], -300, -300, visible=False)
    for v in ('복제', '색', '구간', '거리', '마지막'):
        tr.local(v, 0)
    e = V('구간')
    tr.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                 setv('색', rnd(1, 4)), clone_self(),
                                 wait(V('s40_간격'))))
    tr.on(on_clone(), setv('복제', 1), shape(V('색')), setv('구간', 1), setv('거리', 0), setv('마지막', timer()),
          rot(LGET('s40_rot', 1)), xy(LGET('s40_sx', 1), LGET('s40_sy', 1)), show(),
          until(or_(eq(V('구간'), 0), eq(V('게임중'), 0)),
                chg('거리', mul(V('s40_속도'), sub(timer(), V('마지막')))), setv('마지막', timer()),
                if_(ge(V('거리'), LGET('s40_len', e)),
                    ifelse(gt(LGET('s40_st', e), 0),
                           [setv('s40_도착', LGET('s40_st', e)), setv('s40_px', obj_x()), setv('s40_py', obj_y()),
                            ifelse(eq(LGET('s40_st', e), V('색')), [chg('맞춤', 1), cast('s40_맞음')], [chg('틀림', 1), cast('s40_틀림')]),
                            setv('구간', 0)],
                           [chg('거리', mul(LGET('s40_len', e), -1)),
                            ifelse(gt(LGET('s40_sw', e), 0),
                                   [ifelse(eq(LGET('s40_스위치', LGET('s40_sw', e)), 0), [setv('구간', LGET('s40_n0', e))],
                                           [setv('구간', LGET('s40_n1', e))])],
                                   [setv('구간', LGET('s40_n0', e))]),
                            rot(LGET('s40_rot', e))])),
                if_(gt(V('구간'), 0), xy(add(LGET('s40_sx', e), mul(LGET('s40_ux', e), V('거리'))),
                                       add(LGET('s40_sy', e), mul(LGET('s40_uy', e), V('거리'))))),
                wait(0.016)),
          rep(8, fx_add('transparency', 12), wait(0.03)), del_clone())
    ok = m.T('s40_맞음글', '+1 도착!', 0, 0, 12, '#5CFF9A', F_NUM, False, 0, w=90, h=16, visible=False)
    ok.on(on_msg('s40_맞음'), xy(170, add(V('s40_py'), 24)), show(), wait(0.7), hide())
    no = m.T('s40_틀림글', '다른 역이에요!', 0, 0, 11, C_RED, F_NUM, False, 0, w=110, h=16, visible=False)
    no.on(on_msg('s40_틀림'), xy(160, add(V('s40_py'), 24)), show(), wait(0.8), hide())
    mgr = hidden(m, 's40_담당')
    mgr.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                  setv('s40_속도', add(58, mul(sub(TL, V('남은시간')), 1.0))),
                                  setv('s40_간격', sub(4.2, mul(sub(TL, V('남은시간')), 0.035))),
                                  setv('미니표시', join('도착 ', V('맞춤'), ' · 실수 ', V('틀림'))), wait(0.1)))
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(V('맞춤'), 5.5), mul(V('틀림'), 2))))
    m.on_start(setv('맞춤', 0), setv('틀림', 0), setv('s40_속도', 58), setv('s40_간격', 4.2),
               *[lst_set('s40_스위치', k, 0) for k in (1, 2, 3)], cast('s40_전환'))
    m.snd('s40_딸깍', play('click'))
    m.snd('s40_맞음', play('coin'))
    m.snd('s40_틀림', play('bad'))
    m.finish('기차 색과 같은 색 역으로! 갈림길의 전환기를 눌러\n노란 불이 켜진 쪽으로 기차가 가요. 점점 빨라져요!',
             '조작: 전환기(동그라미) 클릭 또는 숫자키 1·2·3')
    return True


# ================================================================== 34. 자전거 기어 변속
@game(34)
def g34(P, ctx):
    COURSE = [0, 0, 1, 1, 2, 2, 0, -1, -1, -2, -2, 0, 0, 1, 2, 2, 1, 0, -1, -2, 0, 0, 2, 2, 2, -1, -2, -2, 0, 0]
    IDEAL = {2: 13, 1: 19, 0: 27, -1: 33, -2: 39}
    TM, PXM, BX, GY = 40, 2, -120, -36       # 칸 길이(m), 1m=2px, 자전거 x, 자전거 바닥 높이
    goal = len(COURSE) * TM
    t_ideal = sum(TM / IDEAL[s] for s in COURSE)
    TL = int(t_ideal * 1.12) + 1
    slopes = [0] + COURSE + [0] * 7
    H = [0]
    for s_ in slopes:
        H.append(H[-1] + s_ * 10 * PXM)
    m = mg(P, ctx, T, 34, time_limit=TL, status='0 m', dim=40)
    P.list('s34_경사', slopes)
    P.list('s34_높이', H[:-1])
    P.list('s34_속력', [IDEAL[s] for s in slopes])
    vars_(P, 's34_거리', 's34_v', 's34_기어', 's34_체력', 's34_last', 's34_dt', 's34_칸', 's34_hb', 's34_차', 's34_목표v', 's34_상태',
          's34_기울기', 's34_완주')
    # 땅 (복제본 7개가 거리에 맞춰 이어진다)
    tile = m.S('s34_땅', [('t%d' % k, AD.s34_tile(k - 2)) for k in range(5)], -300, -300, visible=False)
    for v in ('복제', '내번호', '내칸', '_ls'):
        tile.local(v, 0)
    tile.on(on_scene(), hide(), setv('내번호', 0), rep(7, chg('내번호', 1), clone_self()))
    ti = add(V('s34_칸'), V('내번호'))
    tile.on(on_clone(), setv('복제', 1), setv('_ls', -1), show(),
            forever(setv('내칸', ti),
                    if_(ne(V('내칸'), V('_ls')), setv('_ls', V('내칸')), shape(add(LGET('s34_경사', V('내칸')), 3))),
                    xy(add(BX, mul(sub(mul(sub(V('내칸'), 1.5), TM), V('s34_거리')), PXM)),
                       sub(add(GY, sub(add(LGET('s34_높이', V('내칸')), mul(LGET('s34_경사', V('내칸')), 10)), V('s34_hb'))), 110)),
                    wait(0.016)))
    import mg_art2 as A2
    bike = m.S('s34_자전거', A2.bicycle(), BX, GY + 22, scale=1.3)
    bike.on(on_msg('게임시작'), until(eq(V('게임중'), 0), rot(V('s34_기울기')), wait(0.016)))
    bike.on(on_msg('s34_헉'), rep(2, mvy(2), wait(0.05), mvy(-2), wait(0.05)))
    # 코스 미리보기
    prof = [H[1 + i] for i in range(len(COURSE) + 1)]
    m.S('s34_코스', AD.s34_profile(prof), 40, 84)
    dot = m.S('s34_코스점', AD.s39_pop(), -110, 84, scale=0.35)
    dot.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(add(-110, mul(div(V('s34_거리'), goal), 300))), wait(0.1)))
    m.T('s34_코스글', '코스', -128, 84, 8, C_DIM, F_BODY, True, 0, w=30, h=12)
    # 계기: 기어, 페달 회전, 체력
    panel(P, m.sc, 's34_계기판', 150, -92, 170, 70, 'glass')
    gears = m.S('s34_기어', [('g%d' % g, AD.s34_gears(g)) for g in range(1, 6)], 108, -76, scale=0.75)
    gears.on(on_msg('s34_변속'), shape(V('s34_기어')))
    gt_ = m.T('s34_기어글', '', 108, -96, 11, C_WHITE, F_NUM, False, 0, w=80, h=16)
    gt_.on(on_msg('s34_변속'), write(join('기어 ', V('s34_기어'))))
    m.T('s34_기어도움', '↑ 무겁게  ↓ 가볍게', 108, -112, 7, C_DIM, F_BODY, True, 0, w=90, h=11)
    m.S('s34_회전계', AD.s34_gauge(), 192, -88)
    nd = m.S('s34_바늘', AD.s34_needle(), 192, -110)
    nd.on(on_msg('게임시작'), until(eq(V('게임중'), 0), rot(mul(V('s34_차'), -26)), wait(0.03)))
    sta = m.S('s34_체력막대', K.bar_set('s34_stamina', 70, 7, 'green'), 192, -120)
    sta.on(on_msg('게임시작'), until(eq(V('게임중'), 0), shape(add(rounded(mul(V('s34_체력'), 0.4)), 1)), wait(0.1)))
    spd = m.T('s34_속도글', '', -150, -110, 12, C_WHITE, F_NUM, False, 0, w=160, h=18)
    spd.on(on_msg('게임시작'), until(eq(V('게임중'), 0), write(join(rounded(mul(V('s34_v'), 1.0)), ' m/s · ', rounded(V('s34_거리')), ' / ', goal, 'm')),
                                    wait(0.12)))
    say = m.T('s34_말', '', BX, 34, 10, C_WHITE, F_BODY, True, 0, w=170, h=30)
    say.local('_ls', -1)
    say.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                  if_(ne(V('s34_상태'), V('_ls')), setv('_ls', V('s34_상태')),
                                      ifelse(eq(V('s34_상태'), 1), [write('끙... 너무 무거워!\n↓ 로 기어를 가볍게'), text_color('#FF8C9A')],
                                             [ifelse(eq(V('s34_상태'), 2), [write('헛바퀴 빙글빙글!\n↑ 로 기어를 무겁게'), text_color('#FFC27A')],
                                                     [ifelse(eq(V('s34_상태'), 3), [write('헉헉... 지쳤어요'), text_color('#FF5C70')],
                                                             [write('')])])])),
                                  wait(0.1)))
    # 주행
    for kc, d in ((K_UP, 1), (K_DOWN, -1)):
        hidden(m, 's34_키%d' % (d + 1)).on(on_key(kc), if_(eq(V('게임중'), 1), chg('s34_기어', d),
                                                          if_(gt(V('s34_기어'), 5), setv('s34_기어', 5)),
                                                          if_(lt(V('s34_기어'), 1), setv('s34_기어', 1)), cast('s34_변속'), cast('s34_딸깍')))
    cur = add(V('s34_칸'), 2)          # 지금 달리는 칸 (목록 번호)
    mgr = hidden(m, 's34_담당')
    mgr.on(on_msg('게임시작'), setv('s34_last', timer()),
           until(or_(eq(V('게임중'), 0), ge(V('s34_거리'), goal)),
                 setv('s34_dt', sub(timer(), V('s34_last'))), setv('s34_last', timer()), if_(gt(V('s34_dt'), 0.1), setv('s34_dt', 0.1)),
                 setv('s34_칸', floor(div(V('s34_거리'), TM))),
                 setv('s34_hb', add(LGET('s34_높이', cur), mul(mul(LGET('s34_경사', cur), 10 * PXM), sub(div(V('s34_거리'), TM), V('s34_칸'))))),
                 setv('s34_차', sub(V('s34_기어'), sub(3, LGET('s34_경사', cur)))),
                 setv('s34_목표v', LGET('s34_속력', cur)), setv('s34_상태', 0),
                 ifelse(gt(V('s34_차'), 0),
                        [setv('s34_목표v', mul(V('s34_목표v'), sub(1, mul(V('s34_차'), 0.3)))),
                         chg('s34_체력', mul(V('s34_dt'), mul(V('s34_차'), -9))), setv('s34_상태', 1),
                         if_(and_(ge(V('s34_차'), 2), ge(LGET('s34_경사', cur), 1)), setv('s34_목표v', mul(LGET('s34_속력', cur), 0.15)))],
                        [ifelse(lt(V('s34_차'), 0),
                                [setv('s34_목표v', mul(V('s34_목표v'), add(1, mul(V('s34_차'), 0.28)))), chg('s34_체력', mul(V('s34_dt'), 1)),
                                 setv('s34_상태', 2)],
                                [chg('s34_체력', mul(V('s34_dt'), 3))])]),
                 if_(lt(V('s34_체력'), 0), setv('s34_체력', 0)), if_(gt(V('s34_체력'), 100), setv('s34_체력', 100)),
                 if_(lt(V('s34_체력'), 1), setv('s34_목표v', mul(V('s34_목표v'), 0.45)), setv('s34_상태', 3)),
                 chg('s34_v', mul(sub(V('s34_목표v'), V('s34_v')), mul(V('s34_dt'), 2.5))),
                 chg('s34_거리', mul(V('s34_v'), V('s34_dt'))),
                 setv('s34_기울기', mul(LGET('s34_경사', cur), -13)),
                 setv('미니표시', join(rounded(V('s34_거리')), ' / ', goal, 'm'))),
           if_(eq(V('게임중'), 1), setv('s34_완주', 1), setv('s34_v', 0), cast('s34_완주'), wait(1.2),
               *m.end_blocks(add(80, mul(V('남은시간'), 1.5)))))
    G.big_pop(P, m.sc, 's34_완주글', K.big_text('완주!', 40, 'royal'), 0, 20, 's34_완주', hold=0.8)
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(div(V('s34_거리'), goal), 85), 10)))
    m.on_start(setv('s34_거리', 0), setv('s34_v', 0), setv('s34_기어', 3), setv('s34_체력', 100), setv('s34_칸', 0), setv('s34_hb', 0),
               setv('s34_차', 0), setv('s34_상태', 0), setv('s34_완주', 0), setv('s34_기울기', 0), cast('s34_변속'))
    m.snd('s34_딸깍', play('click'))
    m.snd('s34_완주', play('fanfare'))
    m.finish('금강 자전거길 %dm 달리기! 오르막은 가벼운 기어(1·2),\n평지는 3, 내리막은 무거운 기어(4·5)로 바꿔야 빨라요.' % goal,
             '조작: ↑ 기어 무겁게 · ↓ 기어 가볍게  ·  바늘이 초록이면 딱 맞는 기어')
    return True


# ================================================================== 36. 민원 창구 안내 (대기열 관리)
@game(36)
def g36(P, ctx):
    TL, NQ = 60, 6
    SERVE = [3.0, 5.0, 4.0, 4.0]
    CXS, CY = [-165, -55, 55, 165], 52
    SXS, SY = [-178 + k * 60 for k in range(NQ)], -60
    m = mg(P, ctx, T, 36, time_limit=TL, status='처리 0', dim=80)
    P.list('s36_요청', [0] * NQ)
    P.list('s36_인내', [0] * NQ)
    P.list('s36_바쁨', [0] * 4)
    P.list('s36_처리시간', SERVE)
    vars_(P, 's36_선택', 's36_창구', 's36_수', 's36_속도', 's36_x', 's36_y', 's36_뺄')
    P.var('s36_글', '')
    persons = [('p%d_%d' % (k, md), AD.s36_person(k, md)) for k in range(4) for md in range(3)]
    # 창구
    for k in range(4):
        c = m.S('s36_창구%d' % (k + 1), AD.s36_counter(k), CXS[k], CY)
        c.on(on_click(), if_(eq(V('게임중'), 1), setv('s36_창구', k + 1), cast('s36_창구누름')))
        G.hover_scripts(c, 106)
        sv = m.S('s36_손님%d' % (k + 1), persons, CXS[k], CY - 34, visible=False)
        sv.on(on_msg('s36_배정'), if_(eq(V('s36_창구'), k + 1), shape(add(mul(k, 3), 1)), xy(V('s36_x'), V('s36_y')), show(),
                                    setv('_ma', obj_x()), setv('_mb', obj_y()),
                                    *flat([[xy(add(V('_ma'), mul(sub(CXS[k], V('_ma')), j / 8.0)), add(V('_mb'), mul(sub(CY - 34, V('_mb')), j / 8.0))),
                                            wait(0.016)] for j in range(1, 9)])))
        sv.local('_ma', 0)
        sv.local('_mb', 0)
        bar = m.S('s36_처리막대%d' % (k + 1), K.bar_set('s36_busy', 70, 6, 'royal'), CXS[k], CY - 64, visible=False)
        bar.on(on_msg('s36_틱'), ifelse(gt(LGET('s36_바쁨', k + 1), 0),
                                       [shape(add(rounded(mul(sub(1, div(LGET('s36_바쁨', k + 1), SERVE[k])), 40)), 1)), show()],
                                       [hide()]))
        sv.on(on_msg('s36_틱'), if_(le(LGET('s36_바쁨', k + 1), 0), hide()))
    # 대기 줄
    ring = m.S('s36_고름', AD.s36_ring(), -300, -300, visible=False)
    ring.on(on_msg('s36_줄갱신'), ifelse(gt(V('s36_선택'), 0), [xy(LGET('s36_x목록', V('s36_선택')), SY), show()], [hide()]))
    P.list('s36_x목록', SXS)
    for j in range(1, NQ + 1):
        q = m.S('s36_줄%d' % j, persons, SXS[j - 1], SY, visible=False)
        q.local('_ls', -1)
        req, pat = LGET('s36_요청', j), LGET('s36_인내', j)
        q.on(on_msg('s36_줄갱신'),
             ifelse(gt(req, 0),
                    [setv('_mk', 3), if_(gt(pat, 25), setv('_mk', 2)), if_(gt(pat, 55), setv('_mk', 1)),
                     setv('_mk', add(mul(sub(req, 1), 3), V('_mk'))),
                     if_(ne(V('_mk'), V('_ls')), setv('_ls', V('_mk')), shape(V('_ls'))), show()],
                    [hide(), setv('_ls', -1)]))
        q.on(on_click(), if_(and_(eq(V('게임중'), 1), gt(req, 0)),
                             ifelse(eq(V('s36_선택'), j), [setv('s36_선택', 0)], [setv('s36_선택', j)]), cast('s36_줄갱신'), cast('s36_딸깍')))
        pb = m.S('s36_인내%d' % j, K.bar_set('s36_pat', 40, 6, 'red'), SXS[j - 1], SY - 34, visible=False)
        pb.local('_ls', -1)
        pb.on(on_msg('s36_줄갱신'), ifelse(gt(req, 0),
                                         [setv('_mk', add(rounded(mul(pat, 0.4)), 1)), if_(ne(V('_mk'), V('_ls')), setv('_ls', V('_mk')), shape(V('_ls'))),
                                          show()], [hide(), setv('_ls', -1)]))
    m.T('s36_줄글', '대기 줄 (민원인 클릭 → 창구 클릭)', -60, -100, 9, C_DIM, F_BODY, True, 0, w=300, h=14)
    msg = m.T('s36_말', '', 0, 0, 13, C_WHITE, F_NUM, False, 0, w=260, h=20)
    msg.on(on_msg('s36_말'), write(V('s36_글')), show(), wait(0.9), write(''))
    say = lambda t, sig=None: [setv('s36_글', t), cast('s36_말')] + ([cast(sig)] if sig else [])
    # 줄에서 j번째 빼기 (뒤 사람들이 앞으로)
    remove = [lst_del('s36_요청', V('s36_뺄')), lst_add('s36_요청', 0), lst_del('s36_인내', V('s36_뺄')), lst_add('s36_인내', 0),
              chg('s36_수', -1),
              if_(eq(V('s36_선택'), V('s36_뺄')), setv('s36_선택', 0)), if_(gt(V('s36_선택'), V('s36_뺄')), chg('s36_선택', -1)),
              cast('s36_줄갱신')]
    sel_req = LGET('s36_요청', V('s36_선택'))
    mgr = hidden(m, 's36_담당')
    k_ = V('s36_창구')
    mgr.on(on_msg('s36_창구누름'),
           ifelse(eq(V('s36_선택'), 0), say('먼저 줄에 선 민원인을 고르세요'),
                  [ifelse(gt(LGET('s36_바쁨', k_), 0), say('그 창구는 아직 바빠요!', 's36_삐'),
                          [ifelse(ne(sel_req, k_),
                                  [chg('틀림', 1), chg('합계', -2), lst_set('s36_인내', V('s36_선택'), sub(LGET('s36_인내', V('s36_선택')), 35)),
                                   setv('s36_선택', 0), cast('s36_줄갱신'), *say('여기가 아니잖아요! (화남)', 's36_틀림')],
                                  [chg('맞춤', 1), chg('합계', add(2, div(LGET('s36_인내', V('s36_선택')), 50))),
                                   lst_set('s36_바쁨', k_, LGET('s36_처리시간', k_)),
                                   setv('s36_x', LGET('s36_x목록', V('s36_선택'))), setv('s36_y', SY), cast('s36_배정'),
                                   setv('s36_뺄', V('s36_선택')), *remove, *say('안내 완료!', 's36_맞음')])])]),
           setv('미니표시', join('처리 ', V('맞춤'), ' · 점수 ', rounded(V('합계')))))
    # 0.1초마다: 인내심 줄이기, 창구 시간, 화나서 떠나기
    tick = []
    for j in range(1, NQ + 1):
        tick.append(if_(gt(LGET('s36_요청', j), 0), lst_set('s36_인내', j, sub(LGET('s36_인내', j), V('s36_속도')))))
    for k in range(1, 5):
        tick.append(if_(gt(LGET('s36_바쁨', k), 0), lst_set('s36_바쁨', k, sub(LGET('s36_바쁨', k), 0.1))))
    tick.append(setv('s36_뺄', 0))
    for j in range(NQ, 0, -1):
        tick.append(if_(gt(LGET('s36_요청', j), 0), if_(le(LGET('s36_인내', j), 0), setv('s36_뺄', j))))
    tick.append(if_(gt(V('s36_뺄'), 0), chg('실패', 1), chg('합계', -3), *remove, *say('기다리다 화나서 가 버렸어요!', 's36_떠남'),
                    setv('미니표시', join('처리 ', V('맞춤'), ' · 점수 ', rounded(V('합계'))))))
    tick += [cast('s36_줄갱신'), cast('s36_틱')]
    mgr.on(on_msg('게임시작'), until(eq(V('게임중'), 0), setv('s36_속도', add(0.55, mul(sub(TL, V('남은시간')), 0.006))), *tick, wait(0.1)))
    mgr.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                  if_(lt(V('s36_수'), NQ), chg('s36_수', 1), lst_set('s36_요청', V('s36_수'), rnd(1, 4)),
                                      lst_set('s36_인내', V('s36_수'), 100), cast('s36_줄갱신'), cast('s36_딩동')),
                                  wait(sub(div(rnd(150, 270), 100), mul(sub(TL, V('남은시간')), 0.012)))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('틀림', 0), setv('실패', 0), setv('s36_선택', 0), setv('s36_수', 0),
               *[lst_set('s36_요청', j, 0) for j in range(1, NQ + 1)], *[lst_set('s36_바쁨', k, 0) for k in range(1, 5)])
    m.snd('s36_딸깍', play('click'))
    m.snd('s36_맞음', play('coin'))
    m.snd('s36_틀림', play('bad'))
    m.snd('s36_떠남', play('fail_big'))
    m.snd('s36_삐', play('beep'))
    m.snd('s36_딩동', play('news'))
    m.finish('세종시청 민원실 안내원이 되어 민원인을 알맞은 빈 창구로!\n오래 기다리면 화나서 가 버려요. 급한 사람부터 보내세요.',
             '조작: 줄에 선 민원인 클릭 → 말풍선 그림과 같은 창구 클릭')
    return True


# ================================================================== 32. 옛 분교 교무실 방탈출
S32_NAMES = ['강다온', '김나래', '박도윤', '서하준', '윤봄', '최이안']


@game(32)
def g32(P, ctx):
    TL = 170
    m = mg(P, ctx, T, 32, time_limit=TL, status='단서를 찾아라', dim=0)
    sc = m.sc
    vars_(P, 's32_창', 's32_선택템', 's32_힌트', 's32_틀림', 's32_액자', 's32_서랍', 's32_풍금', 's32_난로', 's32_꽂음', 's32_금고',
          's32_탈출', 's32_연주', 's32_음', 's32_눌린건반', 's32_다이얼', 's32_방향', 's32_금고단계', 's32_커서', 's32_고른칸',
          's32_휠1', 's32_휠2', 's32_휠3')
    for v in ('s32_글', 's32_서랍코드', 's32_출석글'):
        P.var(v, '')
    P.list('s32_이름', S32_NAMES)
    P.list('s32_결석', [0] * 6)
    P.list('s32_배치', [1, 2, 3, 4, 5, 6])     # 자리 k 에 앉는 학생 번호
    P.list('s32_자리', [1, 2, 3, 4, 5, 6])     # 학생 k 의 자리 번호
    P.list('s32_가락', [1, 3, 5, 3, 1])
    P.list('s32_금고수', [3, 7, 1])
    P.list('s32_가방', [0] * 5)
    can = lambda: and_(eq(V('게임중'), 1), eq(V('s32_창'), 0))
    say = lambda t: [setv('s32_글', t), cast('s32_말')]
    sel = V('s32_선택템')

    def add_item(it):
        return [setv('_ma', 0), *[if_(and_(eq(V('_ma'), 0), eq(LGET('s32_가방', k), 0)), lst_set('s32_가방', k, it), setv('_ma', 1))
                                 for k in range(1, 6)], cast('s32_가방갱신'), cast('s32_찾음')]

    def use_item(it):       # 쓴 물건은 가방에서 뺀다
        return [*[if_(eq(LGET('s32_가방', k), it), lst_set('s32_가방', k, 0)) for k in range(1, 6)], setv('s32_선택템', 0), cast('s32_가방갱신')]

    def open_win(n):
        return [setv('s32_창', n), cast('s32_창갱신'), cast('s32_딸깍')]
    m.S('s32_방', AD.s32_room(), 0, 1)
    # ---------------- 방 안 물건
    frame = m.S('s32_액자', [('hang', AD.s32_frame('hang')), ('moved', AD.s32_frame('moved'))], -190, 62)
    chart = m.S('s32_배치표', AD.s32_paper('chart', 58, 42, '자리 배치표'), -128, 62)
    board = m.S('s32_칠판', AD.s32_board(), -40, 60)
    organ = m.S('s32_풍금', [('closed', AD.s32_organ('closed')), ('open', AD.s32_organ('open'))], -180, -50)
    m.S('s32_책상', AD.s32_desk(), -30, -66)
    book = m.S('s32_출석부', AD.s32_book(), -62, -38)
    drawer = m.S('s32_서랍', [('closed', AD.s32_drawer('closed')), ('open', AD.s32_drawer('open'))], 4, -62)
    stove = m.S('s32_난로', AD.s32_stove(), 75, -40)
    safe = m.S('s32_금고', [('closed', AD.s32_safe('closed')), ('open', AD.s32_safe('open'))], 140, -66)
    door = m.S('s32_문', [('closed', AD.s32_door('closed')), ('open', AD.s32_door('open'))], 205, -8)
    glow = m.S('s32_불빛', AD.s39_pop(), 75, -79, scale=0.5)
    glow.on(on_scene(), forever(fx('brightness', rnd(-10, 30)), wait(0.15)))
    glow.on(on_msg('s32_방갱신'), ifelse(eq(V('s32_난로'), 0), [show()], [hide()]))
    for o, var in ((frame, 's32_액자'), (organ, 's32_풍금'), (drawer, 's32_서랍'), (safe, 's32_금고'), (door, 's32_탈출')):
        o.on(on_msg('s32_방갱신'), shape(add(V(var), 1)))
    for o in (frame, chart, board, organ, book, drawer, stove, safe, door):
        G.hover_scripts(o, 106)
    note_txt = join('쪽지: "금고 ▶오른쪽으로 ', LGET('s32_금고수', 1), ', ◀왼쪽으로 ', LGET('s32_금고수', 2), ', ▶오른쪽으로 ',
                    LGET('s32_금고수', 3), ' (숫자마다 딸깍!)"')
    frame.on(on_click(), if_(can(), ifelse(eq(V('s32_액자'), 0),
                                           [setv('s32_액자', 1), cast('s32_방갱신'), *add_item(1), *say('액자를 들추니 뒤에 쪽지가! (가방에서 눌러 읽기)')],
                                           say('상장: "위 학생은 풍금 연주를 잘하여..."'))))
    chart.on(on_click(), if_(can(), *open_win(2)))
    board.on(on_click(), if_(can(), *say('칠판: "서랍 번호 = 오늘 결석한 아이들의 자리 번호 (출석 번호 순서대로)"')))
    book.on(on_click(), if_(can(), *open_win(1)))
    drawer.on(on_click(), if_(can(), ifelse(eq(V('s32_서랍'), 0), [*open_win(3), *say('세 자리 번호 자물쇠가 달린 서랍이다.')],
                                            say('빈 서랍이다.'))))
    organ.on(on_click(), if_(can(), ifelse(eq(V('s32_풍금'), 0), open_win(4), say('풍금 아래 칸은 이미 열려 있다.'))))
    stove.on(on_click(), if_(can(), ifelse(eq(V('s32_난로'), 1), say('난로 불이 따뜻하다.'),
                                           [ifelse(eq(sel, 3), [setv('s32_난로', 1), *use_item(3), cast('s32_방갱신'), *add_item(4),
                                                                *say('집게로 재를 뒤져 작은 열쇠를 꺼냈다!')],
                                                   say('난로 속 재 사이에서 뭔가 반짝! 뜨거워서 손으로는 못 꺼내.'))])))
    safe.on(on_click(), if_(can(), ifelse(eq(V('s32_금고'), 1), say('빈 금고다.'),
                                          [ifelse(eq(V('s32_꽂음'), 1), open_win(5),
                                                  [ifelse(eq(sel, 4), [setv('s32_꽂음', 1), *use_item(4), cast('s32_철컥'),
                                                                       *open_win(5), *say('열쇠를 꽂았다. 이제 다이얼!')],
                                                          say('작은 열쇠 구멍과 숫자 다이얼이 달린 금고다.'))])])))
    door.on(on_click(), if_(can(), ifelse(eq(sel, 5), [setv('s32_탈출', 1), *use_item(5), cast('s32_방갱신'), cast('s32_탈출'),
                                                       *say('문이 열렸다! 탈출 성공!')],
                                          say('교무실 문이 잠겨 있다. 큰 열쇠 구멍이 있다.'))))
    # ---------------- 아래: 말 상자, 힌트, 가방
    panel(P, sc, 's32_말판', -122, -117, 236, 28, 'glass')
    msg = m.T('s32_말글', '', -122, -117, 9, C_WHITE, F_BODY, True, 0, w=226, h=26)
    msg.on(on_msg('s32_말'), write(V('s32_글')))
    hints = [(eq(V('s32_서랍'), 0), '힌트: 출석부에서 결석한 3명을 찾아, 자리 배치표의 자리 번호를 출석 번호 순서로!'),
             (eq(V('s32_풍금'), 0), '힌트: 풍금을 눌러 악보대로 연주! 맨 아래 덧줄 음이 "도", 한 칸 오를 때마다 레·미·파…'),
             (eq(V('s32_난로'), 0), '힌트: 가방에서 집게를 고른 뒤 난로를 눌러 봐.'),
             (eq(V('s32_액자'), 0), '힌트: 벽에 걸린 상장 액자를 눌러 봐.'),
             (eq(V('s32_금고'), 0), '힌트: 금고 열쇠를 고르고 금고를 눌러. 쪽지대로 돌리고 숫자마다 딸깍!')]
    chain = say('힌트: 가방에서 큰 열쇠를 고르고 문을 눌러!')
    for c_, t_ in reversed(hints):
        chain = [ifelse(c_, say(t_), chain)]
    button(P, sc, 's32_힌트버튼', '힌트 -8', 24, -117, 62, 26, 'purple',
           actions=[if_(can(), chg('s32_힌트', 1), cast('s32_힌트음'), *chain)])
    items = [('none', A.clear_dot())] + [(k, AD.s32_item(k)) for k in ('note', 'sheet', 'tongs', 'key_s', 'key_d')]
    item_say = {1: None, 2: '악보다. 풍금 앞에서 보면 되겠다.', 3: '부젓가락(집게)이다. 뜨거운 것도 집을 수 있다.',
                4: '작은 쇠 열쇠다.', 5: '큰 놋쇠 열쇠다!'}
    for k in range(1, 6):
        x = 76 + (k - 1) * 34
        it = LGET('s32_가방', k)
        bg = m.S('s32_칸%d' % k, [('n', AD.s32_slot(0)), ('s', AD.s32_slot(1))], x, -117)
        ic = m.S('s32_물건%d' % k, items, x, -117)
        bg.on(on_msg('s32_가방갱신'), ifelse(and_(gt(it, 0), eq(sel, it)), [shape('s')], [shape('n')]))
        ic.on(on_msg('s32_가방갱신'), shape(add(it, 1)))
        act = [if_(and_(can(), gt(it, 0)), ifelse(eq(sel, it), [setv('s32_선택템', 0)], [setv('s32_선택템', it)]),
                   cast('s32_가방갱신'), cast('s32_딸깍'),
                   ifelse(eq(it, 1), [setv('s32_글', note_txt), cast('s32_말')],
                          [*[if_(eq(it, j), *say(t)) for j, t in item_say.items() if t]]))]
        bg.on(on_click(), *act)
        ic.on(on_click(), *act)
    # ---------------- 확대 창 (공용 틀)
    win = []
    win.append(m.S('s32_창어둡게', A.plain_rect(480, 270, (2, 3, 12, 175), 'dim_kp'), 0, 0))
    win.append(panel(P, sc, 's32_창판', 0, 2, 340, 210, 'glass', header='royal'))
    wt = m.T('s32_창제목', '', 0, 92, 12, C_WHITE, F_NUM, False, 0, w=240, h=18)
    titles = {1: '출석부 (오늘)', 2: '자리 배치표', 3: '서랍 자물쇠', 4: '풍금', 5: '금고 다이얼'}
    wt.on(on_msg('s32_창갱신'), *[if_(eq(V('s32_창'), k), write(t)) for k, t in titles.items()])
    win.append(wt)
    close = [if_(gt(V('s32_창'), 0), setv('s32_창', 0), cast('s32_창갱신'))]
    win.append(button(P, sc, 's32_닫기', '닫기', 140, 92, 48, 20, 'gray', actions=close))
    for o in win:
        o.on(on_scene(), hide())
        o.on(on_msg('s32_창갱신'), ifelse(gt(V('s32_창'), 0), [show()], [hide()]))

    def in_win(o, n, extra=None):
        cond = eq(V('s32_창'), n) if extra is None else and_(eq(V('s32_창'), n), extra)
        o.on(on_scene(), hide())
        o.on(on_msg('s32_창갱신'), ifelse(cond, [show()], [hide()]))
        return o
    # 1 출석부
    att = in_win(m.T('s32_출석', '', 0, 6, 12, '#1A1F3A', F_BODY, True, 0, w=240, h=150, bg='#F4F0E2'), 1)
    att.on(on_msg('s32_창갱신'), if_(eq(V('s32_창'), 1), write(V('s32_출석글'))))
    # 2 자리 배치표
    in_win(m.S('s32_자리그림', AD.s32_seats(), 0, -6), 2)
    for k in range(6):
        r, c = divmod(k, 3)
        nt = in_win(m.T('s32_자리이름%d' % (k + 1), '', -64 + 66 * c + 5, 9 - 42 * r - 6, 11, '#1A1F3A', F_BODY, True, 0, w=50, h=16), 2)
        nt.on(on_msg('s32_창갱신'), if_(eq(V('s32_창'), 2), write(LGET('s32_이름', LGET('s32_배치', k + 1)))))
    # 3 서랍 번호 바퀴
    in_win(m.T('s32_서랍도움', '칸 위쪽 클릭 +1 · 아래쪽 클릭 -1 · 숫자키로도 입력', 0, -60, 9, C_DIM, F_BODY, True, 0, w=300, h=14), 3)
    code_ok = eq(join(join(V('s32_휠1'), V('s32_휠2')), V('s32_휠3')), V('s32_서랍코드'))
    check_drawer = [if_(and_(eq(V('s32_창'), 3), code_ok),
                        setv('s32_서랍', 1), setv('s32_창', 0), cast('s32_창갱신'), cast('s32_방갱신'), cast('s32_철컥'), *add_item(2),
                        *say('철컥! 서랍이 열렸다. 안에 악보가 들어 있다.'))]
    for k in range(1, 4):
        wv = 's32_휠%d' % k
        wh = in_win(m.S('s32_바퀴%d' % k, [('w%d' % n, AD.s32_wheel(n)) for n in range(10)], -50 + (k - 1) * 50, 6, scale=1.4), 3)
        wh.on(on_msg('s32_휠갱신'), shape(add(V(wv), 1)))
        wh.on(on_click(), if_(eq(V('s32_창'), 3), ifelse(gt(mouse_y(), obj_y()), [chg(wv, 1)], [chg(wv, -1)]),
                              setv(wv, mod(add(V(wv), 10), 10)), setv('s32_커서', k), cast('s32_휠갱신'), cast('s32_딸깍'), *check_drawer))
        cur = in_win(m.S('s32_커서%d' % k, AD.s33_marker(), -50 + (k - 1) * 50, -36), 3)
        cur.on(on_scene(), rot(-90))
        cur.on(on_msg('s32_휠갱신'), if_(eq(V('s32_창'), 3), ifelse(eq(V('s32_커서'), k), [show()], [hide()])))
    for d in range(10):
        hidden(m, 's32_숫자키%d' % d).on(on_key(48 + d), if_(eq(V('s32_창'), 3),
                                                            *[if_(eq(V('s32_커서'), k), setv('s32_휠%d' % k, d)) for k in (1, 2, 3)],
                                                            setv('s32_커서', add(mod(V('s32_커서'), 3), 1)), cast('s32_휠갱신'), cast('s32_딸깍'),
                                                            *check_drawer))
    # 4 풍금 건반과 악보
    owned = lambda it: or_(or_(eq(LGET('s32_가방', 1), it), eq(LGET('s32_가방', 2), it)),
                           or_(or_(eq(LGET('s32_가방', 3), it), eq(LGET('s32_가방', 4), it)), eq(LGET('s32_가방', 5), it)))
    in_win(m.S('s32_오선', AD.s32_staff(), 0, 40), 4, owned(2))
    in_win(m.T('s32_악보없음', '악보가 없다... 무슨 곡이었더라?', 0, 40, 11, C_DIM, F_BODY, True, 0, w=260, h=18), 4, not_(owned(2)))
    for j in range(1, 6):
        nh = in_win(m.S('s32_음표%d' % j, [('l', AD.s32_notehead(1)), ('n', AD.s32_notehead(0))], -56 + 30 * j, 20), 4, owned(2))
        nh.on(on_msg('s32_창갱신'), if_(eq(V('s32_창'), 4), ly(add(19, mul(sub(LGET('s32_가락', j), 1), 4))),
                                       ifelse(eq(LGET('s32_가락', j), 1), [shape('l')], [shape('n')])))
    NAMES = ['도', '레', '미', '파', '솔', '라', '시', '도']
    play_note = lambda n: [if_(eq(V('s32_창'), 4), setv('s32_음', n), cast('s32_건반'))]
    for n in range(1, 9):
        x = -98 + 28 * (n - 1)
        ky = in_win(m.S('s32_건반%d' % n, [('u', AD.s32_key(0)), ('d', AD.s32_key(1))], x, -38), 4)
        ky.on(on_click(), *play_note(n))
        ky.on(on_msg('s32_건반'), if_(eq(V('s32_음'), n), shape('d'), wait(0.15), shape('u')))
        lb = in_win(m.T('s32_건반글%d' % n, NAMES[n - 1], x, -62, 10, '#1A1F3A', F_NUM, False, 0, w=24, h=14), 4)
        lb.on(on_click(), *play_note(n))
        hidden(m, 's32_건반키%d' % n).on(on_key(48 + n), *play_note(n))
    prog = in_win(m.T('s32_연주글', '', 0, -88, 11, C_ACC, F_NUM, False, 0, w=240, h=16), 4)
    prog.on(on_msg('s32_연주갱신'), write(join('♪ 맞게 친 음 ', V('s32_연주'), ' / 5   (숫자키 1~8 도 돼요)')))
    prog.on(on_msg('s32_창갱신'), cast('s32_연주갱신'))
    snd = m.S('s32_풍금소리', A.clear_dot(), -300, -300)
    for nm, path, dur in AD.s32_notes_snd():
        snd.add_sound(nm, path, dur)
    snd.on(on_msg('s32_건반'), *[if_(eq(V('s32_음'), n), play('s32_음%d' % n)) for n in range(1, 9)])
    pmgr = hidden(m, 's32_풍금담당')
    pmgr.on(on_msg('s32_건반'),
            ifelse(eq(V('s32_음'), LGET('s32_가락', add(V('s32_연주'), 1))), [chg('s32_연주', 1)],
                   [ifelse(eq(V('s32_음'), LGET('s32_가락', 1)), [setv('s32_연주', 1)], [setv('s32_연주', 0)])]),
            cast('s32_연주갱신'),
            if_(ge(V('s32_연주'), 5), setv('s32_연주', 0), wait(0.5), setv('s32_풍금', 1), setv('s32_창', 0), cast('s32_창갱신'),
                cast('s32_방갱신'), *add_item(3), *say('♪ 연주가 끝나자 풍금 아래 칸이 열렸다! 집게(부젓가락)가 있다.')))
    # 5 금고 다이얼
    dial = in_win(m.S('s32_다이얼', AD.s32_dial(), 0, 4), 5)
    dial.on(on_msg('s32_다이얼갱신'), rot(mul(V('s32_다이얼'), -36)))
    ptr = in_win(m.S('s32_바늘', AD.s33_marker(), 0, 66), 5)
    ptr.on(on_scene(), rot(90))
    dn = in_win(m.T('s32_다이얼수', '', 64, 66, 12, C_WHITE, F_NUM, False, 0, w=60, h=16), 5)
    dn.on(on_msg('s32_다이얼갱신'), write(join('▲ ', V('s32_다이얼'))))
    turn = lambda d: [if_(eq(V('s32_창'), 5), setv('s32_다이얼', mod(add(V('s32_다이얼'), 10 - d if d > 0 else 1), 10)),
                          setv('s32_방향', d), cast('s32_다이얼갱신'), cast('s32_딸깍'))]
    win5 = [button(P, sc, 's32_왼쪽', '◀ 왼쪽', -112, 4, 72, 26, 'steel', actions=turn(-1)),
            button(P, sc, 's32_오른쪽', '오른쪽 ▶', 112, 4, 72, 26, 'steel', actions=turn(1)),
            button(P, sc, 's32_딸깍', '딸깍!', 0, -72, 80, 26, 'royal', actions=[if_(eq(V('s32_창'), 5), cast('s32_금고확인'))])]
    for o in win5:
        in_win(o, 5)
    stp = in_win(m.T('s32_금고단계글', '', 0, -94, 9, C_DIM, F_BODY, True, 0, w=260, h=14), 5)
    stp.on(on_msg('s32_다이얼갱신'), write(join('맞춘 숫자 ', V('s32_금고단계'), ' / 3')))
    smgr = hidden(m, 's32_금고담당')
    want_dir = sub(1, mul(mod(V('s32_금고단계'), 2), 2))     # 단계 0,2: 오른쪽(1) / 단계 1: 왼쪽(-1)
    smgr.on(on_msg('s32_금고확인'),
            ifelse(and_(eq(V('s32_다이얼'), LGET('s32_금고수', add(V('s32_금고단계'), 1))), eq(V('s32_방향'), want_dir)),
                   [chg('s32_금고단계', 1), cast('s32_딸깍'), cast('s32_다이얼갱신')],
                   [setv('s32_금고단계', 0), chg('s32_틀림', 1), cast('s32_삐'), cast('s32_다이얼갱신'), *say('덜컥... 처음부터 다시 돌려야 한다.')]),
            if_(ge(V('s32_금고단계'), 3), wait(0.3), setv('s32_금고', 1), setv('s32_창', 0), cast('s32_창갱신'), cast('s32_방갱신'),
                cast('s32_철컥'), *add_item(5), *say('금고가 열렸다! 큰 놋쇠 열쇠를 찾았다.')))
    # ---------------- 탈출과 점수
    flash = m.S('s32_탈출빛', A.plain_rect(480, 270, (200, 220, 255, 255), 'white_full'), 0, 0, visible=False)
    flash.on(on_msg('s32_탈출'), wait(0.4), fx('transparency', 100), show(), rep(10, fx_add('transparency', -8), wait(0.03)))
    G.big_pop(P, sc, 's32_탈출글', K.big_text('탈출 성공!', 40, 'royal'), 0, 20, 's32_탈출', hold=1.2)
    mgr = hidden(m, 's32_담당')
    mgr.on(on_msg('s32_탈출'), setv('_mk', sub(sub(TL, V('남은시간')), 80)), if_(lt(V('_mk'), 0), setv('_mk', 0)),
           setv('합계', sub(sub(100, mul(V('s32_힌트'), 8)), mul(V('_mk'), 0.3))), if_(lt(V('합계'), 40), setv('합계', 40)),
           wait(1.6), *m.end_blocks(V('합계')))
    part = sub(add(add(mul(V('s32_서랍'), 14), mul(V('s32_풍금'), 12)), add(add(mul(V('s32_난로'), 8), mul(V('s32_액자'), 5)),
                                                                          mul(V('s32_금고'), 14))), mul(V('s32_힌트'), 4))
    mgr.on(on_msg('시간끝'), setv('s32_창', 0), cast('s32_창갱신'), *say('시간이 다 됐다... 갇혀 버렸다!'), wait(1.0), *m.end_blocks(part))
    mgr.on(on_msg('게임시작'), until(eq(V('게임중'), 0), setv('미니표시', join('힌트 ', V('s32_힌트'), ' · 실수 ', V('s32_틀림'))), wait(0.25)))
    # ---------------- 시작: 정답을 무작위로
    shuffle = []
    for k in range(6, 1, -1):
        shuffle += [setv('_mk', rnd(1, k)), setv('_mv', LGET('s32_배치', k)), lst_set('s32_배치', k, LGET('s32_배치', V('_mk'))),
                    lst_set('s32_배치', V('_mk'), V('_mv'))]
    m.on_start(setv('s32_창', 0), setv('s32_선택템', 0), setv('s32_힌트', 0), setv('s32_틀림', 0), setv('s32_액자', 0), setv('s32_서랍', 0),
               setv('s32_풍금', 0), setv('s32_난로', 0), setv('s32_꽂음', 0), setv('s32_금고', 0), setv('s32_탈출', 0), setv('s32_연주', 0),
               setv('s32_다이얼', 0), setv('s32_방향', 0), setv('s32_금고단계', 0), setv('s32_커서', 1),
               setv('s32_휠1', 0), setv('s32_휠2', 0), setv('s32_휠3', 0),
               *[lst_set('s32_가방', k, 0) for k in range(1, 6)],
               *[lst_set('s32_배치', k, k) for k in range(1, 7)], *shuffle,
               *[lst_set('s32_자리', LGET('s32_배치', k), k) for k in range(1, 7)],
               *[lst_set('s32_결석', k, 0) for k in range(1, 7)],
               setv('_ma', rnd(1, 6)), setv('_mb', rnd(1, 6)), until(ne(V('_mb'), V('_ma')), setv('_mb', rnd(1, 6))),
               setv('_mk', rnd(1, 6)), until(and_(ne(V('_mk'), V('_ma')), ne(V('_mk'), V('_mb'))), setv('_mk', rnd(1, 6))),
               lst_set('s32_결석', V('_ma'), 1), lst_set('s32_결석', V('_mb'), 1), lst_set('s32_결석', V('_mk'), 1),
               setv('s32_서랍코드', ''), setv('s32_출석글', ''),
               *[ifelse(eq(LGET('s32_결석', k), 1),
                        [setv('s32_서랍코드', join(V('s32_서랍코드'), LGET('s32_자리', k))),
                         setv('s32_출석글', join(V('s32_출석글'), '%d번  %s   ✕ 결석\n' % (k, S32_NAMES[k - 1])))],
                        [setv('s32_출석글', join(V('s32_출석글'), '%d번  %s   ○ 출석\n' % (k, S32_NAMES[k - 1])))])
                 for k in range(1, 7)],
               *[lst_set('s32_가락', j, rnd(1, 8)) for j in range(1, 6)],
               lst_set('s32_금고수', 1, rnd(1, 9)),
               lst_set('s32_금고수', 2, rnd(0, 9)), until(ne(LGET('s32_금고수', 2), LGET('s32_금고수', 1)), lst_set('s32_금고수', 2, rnd(0, 9))),
               lst_set('s32_금고수', 3, rnd(0, 9)), until(ne(LGET('s32_금고수', 3), LGET('s32_금고수', 2)), lst_set('s32_금고수', 3, rnd(0, 9))),
               setv('s32_글', '교무실에 갇혔다! 물건을 눌러 단서를 찾자.'),
               cast('s32_방갱신'), cast('s32_가방갱신'), cast('s32_말'), cast('s32_다이얼갱신'), cast('s32_휠갱신'))
    m.snd('s32_딸깍', play('tick'))
    m.snd('s32_찾음', play('good'))
    m.snd('s32_삐', play('bad'))
    m.snd('s32_철컥', play('stamp'))
    m.snd('s32_힌트음', play('pop'))
    m.snd('s32_탈출', play('fanfare'))
    m.finish('연동면 옛 분교 교무실에 갇혔다! 출석부·풍금·난로·금고의\n단서를 차례로 풀고 문 열쇠를 찾아 탈출하세요. 정답은 매번 달라요.',
             '조작: 마우스 클릭 (숫자키도 돼요)  ·  가방 물건을 고른 뒤 쓸 곳 클릭  ·  힌트 -8점')
    return True
