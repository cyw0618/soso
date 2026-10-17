# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 21~30번."""
import random
from games_common import *
import mg_art3 as A3

T = 3
GAMES, game = registry()

import art3c as AC
import mg_art as A


def clamp(var, lo, hi):
    return [if_(lt(V(var), lo), setv(var, lo)), if_(gt(V(var), hi), setv(var, hi))]


def pop_fx(m, base, pics, x, y, msg, hold=0.6):
    """신호를 받으면 튀어나왔다 사라지는 글자 (pics: [(이름, 경로)], 모양은 V('_mv') 번호)."""
    o = m.S(base, pics, x, y, visible=False)
    o.on(on_msg(msg), *([shape(V('_mv'))] if len(pics) > 1 else []), xy(x, y), to_front(), o.pct(40), fx('transparency', 0), show(),
         rep(5, o.grow_pct(14), wait(0.016)), rep(2, o.grow_pct(-5), wait(0.016)), wait(hold),
         rep(8, fx_add('transparency', 12), mvy(1), wait(0.02)), hide())
    return o


# ================================================================== 21. 테이블 하키
@game(21)
def g21(P, ctx):
    TL, WIN = 45, 5
    CY = -22                      # 탁자 가운데 y
    PX, PY0, PY1 = 200, CY - 80, CY + 80     # 퍽 중심이 움직이는 범위
    MX, MY0, MY1 = 195, CY - 75, CY + 75     # 채 중심 범위
    GH = 30                       # 골문 반 높이 (퍽 중심 기준)
    RR = 25                       # 채 반지름 + 퍽 반지름
    m = mg(P, ctx, T, 21, time_limit=TL, status='나 0 : 0 상대', dim=70)
    vs = ['px', 'py', 'vx', 'vy', 'mx', 'my', 'mvx', 'mvy', 'ax', 'ay', 'avx', 'avy', 'me', 'ai', 'st', 'dx', 'dy', 'd',
          'vn', 'nx', 'ny', 'tx', 'ty', 'cool', 'fr', 'sp', 'who']
    vars_(P, *['k21_' + v for v in vs])
    W = lambda n: V('k21_' + n)
    S_ = lambda n, v: setv('k21_' + n, v)
    C_ = lambda n, v: chg('k21_' + n, v)
    cl = lambda n, lo, hi: clamp('k21_' + n, lo, hi)
    m.S('탁자', AC.hockey_table(440, 200, GH * 2 + 8), 0, CY)
    m.S('점수판', AC.score_pill(150, 22), 0, 91)
    m.S('내얼굴', ctx['PORT']['me'], -62, 91)
    m.S('상대얼굴', ctx['PORT']['p1'], 62, 91)
    sc = m.T('점수글', '0 : 0', 0, 91, 14, C_WHITE, F_NUM, False, 0, w=80, h=20)
    sc.on(on_msg('k21_점수'), write(join(W('me'), ' : ', W('ai'))))
    puck = m.S('퍽', AC.hockey_puck(10), -60, CY)
    me = m.S('내채', AC.hockey_mallet('me'), -150, CY)
    ai = m.S('상대채', AC.hockey_mallet('ai'), 150, CY)
    for o, a, b in ((puck, 'px', 'py'), (me, 'mx', 'my'), (ai, 'ax', 'ay')):
        o.on(on_msg('게임시작'), until(eq(V('게임중'), 0), xy(W(a), W(b))))

    def hit(mx, my, mvx, mvy):
        return [S_('dx', sub(W('px'), W(mx))), S_('dy', sub(W('py'), W(my))),
                S_('d', add(mul(W('dx'), W('dx')), mul(W('dy'), W('dy')))),
                if_(lt(W('d'), RR * RR),
                    S_('d', fn('root', W('d'))),
                    if_(lt(W('d'), 0.5), S_('d', 1), S_('dx', ifelse_num(mx))),
                    S_('nx', div(W('dx'), W('d'))), S_('ny', div(W('dy'), W('d'))),
                    S_('vn', add(mul(sub(W('vx'), W(mvx)), W('nx')), mul(sub(W('vy'), W(mvy)), W('ny')))),
                    if_(lt(W('vn'), 0), C_('vx', mul(mul(W('vn'), -1.85), W('nx'))), C_('vy', mul(mul(W('vn'), -1.85), W('ny')))),
                    S_('px', add(W(mx), mul(W('nx'), RR + 0.5))), S_('py', add(W(my), mul(W('ny'), RR + 0.5))),
                    if_(eq(W('cool'), 0), S_('cool', 6), cast('k21_딱')))]

    def ifelse_num(mx):
        return 1 if mx == 'mx' else -1

    goal = lambda who: [S_('st', 1), S_('who', who), cast('k21_골')]
    phys = [
        # 내 채: 마우스를 따라가되 한 프레임에 14px 까지
        S_('tx', mouse_x()), S_('ty', mouse_y()), *cl('tx', -MX, -16), *cl('ty', MY0, MY1),
        S_('mvx', sub(W('tx'), W('mx'))), S_('mvy', sub(W('ty'), W('my'))), *cl('mvx', -14, 14), *cl('mvy', -14, 14),
        C_('mx', W('mvx')), C_('my', W('mvy')),
        # 상대 채: 퍽이 상대 진영이면 공격, 아니면 골문 앞 수비
        ifelse(gt(W('px'), -8),
               [ifelse(lt(W('ax'), add(W('px'), 8)),
                       [S_('tx', add(W('px'), 30)), ifelse(gt(W('py'), W('ay')), [S_('ty', sub(W('py'), 30))], [S_('ty', add(W('py'), 30))])],
                       [S_('tx', add(W('px'), 10)), S_('ty', W('py'))])],
               [S_('tx', 168), S_('ty', add(CY, mul(sub(W('py'), CY), 0.55)))]),
        S_('avx', sub(W('tx'), W('ax'))), S_('avy', sub(W('ty'), W('ay'))),
        *cl('avx', mul(W('sp'), -1), W('sp')), *cl('avy', mul(W('sp'), -1), W('sp')),
        C_('ax', W('avx')), C_('ay', W('avy')), *cl('ax', 16, MX), *cl('ay', MY0, MY1),
        if_(eq(W('st'), 0),
            C_('px', W('vx')), C_('py', W('vy')), S_('vx', mul(W('vx'), 0.994)), S_('vy', mul(W('vy'), 0.994)),
            if_(gt(W('py'), PY1), S_('py', PY1), S_('vy', mul(abs_(W('vy')), -0.9))),
            if_(lt(W('py'), PY0), S_('py', PY0), S_('vy', mul(abs_(W('vy')), 0.9))),
            if_(lt(W('px'), -PX), ifelse(lt(abs_(sub(W('py'), CY)), GH),
                                         [if_(lt(W('px'), -PX - 16), *goal(2))],
                                         [S_('px', -PX), S_('vx', mul(abs_(W('vx')), 0.9))])),
            if_(gt(W('px'), PX), ifelse(lt(abs_(sub(W('py'), CY)), GH),
                                        [if_(gt(W('px'), PX + 16), *goal(1))],
                                        [S_('px', PX), S_('vx', mul(abs_(W('vx')), -0.9))])),
            *hit('mx', 'my', 'mvx', 'mvy'), *hit('ax', 'ay', 'avx', 'avy'),
            S_('d', add(mul(W('vx'), W('vx')), mul(W('vy'), W('vy')))),
            if_(gt(W('d'), 121), S_('d', div(11, fn('root', W('d')))), S_('vx', mul(W('vx'), W('d'))), S_('vy', mul(W('vy'), W('d'))))),
        if_(gt(W('cool'), 0), C_('cool', -1)),
        C_('fr', 1)]
    mgr = hidden(m, '하키담당')
    mgr.on(on_msg('게임시작'), S_('st', 0), until(eq(V('게임중'), 0), *phys))
    end_score = add(add(50, mul(sub(W('me'), W('ai')), 12)), mul(W('me'), 3))
    mgr.on(on_msg('k21_골'),
           ifelse(eq(W('who'), 1), [C_('me', 1), setv('_mv', 1)], [C_('ai', 1), setv('_mv', 2)]),
           cast('k21_점수'), cast('k21_골팝'), setv('미니표시', join('나 ', W('me'), ' : ', W('ai'), ' 상대')),
           S_('sp', add(2.7, mul(W('me'), 0.22))),
           wait(1.2),
           if_(or_(ge(W('me'), WIN), ge(W('ai'), WIN)), *m.end_blocks(end_score)),
           ifelse(eq(W('who'), 1), [S_('px', 60)], [S_('px', -60)]), S_('py', CY), S_('vx', 0), S_('vy', 0),
           S_('ax', 168), S_('ay', CY), S_('st', 0))
    mgr.on(on_msg('시간끝'), *m.end_blocks(end_score))
    pop_fx(m, '골글', [('a', K.big_text('골인!', 40, 'royal')), ('b', K.big_text('실점...', 32, 'red'))], 0, 20, 'k21_골팝', 0.6)
    m.on_start(S_('px', -60), S_('py', CY), S_('vx', 0), S_('vy', 0), S_('mx', -150), S_('my', CY), S_('ax', 150), S_('ay', CY),
               S_('mvx', 0), S_('mvy', 0), S_('avx', 0), S_('avy', 0), S_('me', 0), S_('ai', 0), S_('st', 1), S_('cool', 0),
               S_('fr', 0), S_('sp', 2.7), cast('k21_점수'))
    m.snd('k21_딱', play('tick'))
    m.snd('k21_골팝', ifelse(eq(V('_mv'), 1), [play('good')], [play('bad')]))
    m.finish('마우스로 파란 채를 움직여 노란 퍽을 치세요!\n오른쪽 상대 골문에 먼저 5골 넣으면 승리!',
             '조작: 마우스 이동 (채는 내 진영 왼쪽 절반만)  ·  45초')
    return True


# ================================================================== 22. 눈길 운전
@game(22)
def g22(P, ctx):
    TL, CARY, HW, VMAX = 40, -70, 42, 150
    m = mg(P, ctx, T, 22, time_limit=TL, status='0.00 km', dim=0)
    vars_(P, *['k22_' + v for v in ('d', 'x', 'h', 'vx', 'sp', 'dt', 'lt', 'f', 'A', 'rc', 'on', 'off', 'g', 'tg', 'fr', 'run')])
    W = lambda n: V('k22_' + n)
    S_ = lambda n, v: setv('k22_' + n, v)
    C_ = lambda n, v: chg('k22_' + n, v)

    def road_c(D):
        return mul(W('A'), add(mul(0.55, sin_(mul(D, 0.15))), mul(0.45, sin_(add(mul(D, 0.5), 40)))))

    def road_slope(D):
        return mul(W('A'), add(mul(0.55 * 0.15 * 0.017453, cos_(mul(D, 0.15))), mul(0.45 * 0.5 * 0.017453, cos_(add(mul(D, 0.5), 40)))))

    m.S('눈밭', AC.snow_field(), 0, -17)
    road = m.S('도로', AC.snow_road(), 0, -300, visible=False)
    for v in ('k22_k', 'k22_D', 'k22_s', '복제'):
        road.local(v, 0)
    road.on(on_scene(), S_('run', 1), setv('k22_k', -1), rep(14, chg('k22_k', 1), clone_self()))
    road.on(on_clone(), setv('복제', 1), show(),
            until(eq(W('run'), 0),
                  ly(sub(add(-140, mul(V('k22_k'), 22)), mod(W('d'), 22))),
                  setv('k22_D', add(add(W('d'), obj_y()), 70)),
                  lx(road_c(V('k22_D'))),
                  setv('k22_s', road_slope(V('k22_D'))),
                  rot(div(mul(V('k22_s'), 57.3), add(1, mul(mul(V('k22_s'), V('k22_s')), 0.28))))),
            del_clone())
    tree = m.S('소나무', AC.snow_pine(), 0, -300, visible=False)
    for v in ('k22_k', 'k22_D', 'k22_o', '복제'):
        tree.local(v, 0)
    tree.on(on_scene(), setv('k22_k', -1), rep(7, chg('k22_k', 1), clone_self()))
    new_off = [setv('k22_o', rnd(82, 150)), if_(eq(rnd(0, 1), 0), setv('k22_o', mul(V('k22_o'), -1)))]
    tree.on(on_clone(), setv('복제', 1), setv('k22_D', add(mul(V('k22_k'), 64), rnd(0, 30))), *new_off, tree.pct(rnd(80, 125)), show(),
            until(eq(W('run'), 0),
                  ly(sub(sub(V('k22_D'), W('d')), 70)),
                  if_(lt(obj_y(), -160), chg('k22_D', add(448, rnd(0, 40))), *new_off, ly(sub(sub(V('k22_D'), W('d')), 70))),
                  lx(add(road_c(V('k22_D')), V('k22_o')))),
            del_clone())
    car = m.S('차', AC.snow_car(), 20, CARY)
    car.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                   xy(W('x'), CARY), ifelse(eq(W('off'), 1), [rot(add(W('h'), rnd(-7, 7)))], [rot(W('h'))])))
    flake = m.S('눈송이', AC.snowflake(), 0, -300, visible=False)
    flake.local('복제', 0)
    flake.local('k22_k', 0)
    flake.on(on_scene(), rep(16, clone_self()))
    flake.on(on_clone(), setv('복제', 1), xy(rnd(-235, 235), rnd(-130, 100)), flake.pct(rnd(60, 160)), setv('k22_k', rnd(0, 360)),
             fx('transparency', rnd(0, 40)), show(),
             until(eq(W('run'), 0),
                   mvy(mul(add(0.8, mul(W('sp'), 0.012)), mul(W('f'), -1))), chg('k22_k', 4), mvx(mul(sin_(V('k22_k')), 0.6)),
                   if_(lt(obj_y(), -134), xy(rnd(-235, 235), 100)),
                   if_(eq(V('게임중'), 0), wait(0.05))),
             del_clone())
    warn = m.S('미끄럼경고', K.big_text('눈더미에 빠졌어요!', 20, 'red'), 0, 30, visible=False)
    warn.on(on_msg('k22_빠짐'), show(), wait(0.8), hide())
    mgr = hidden(m, '운전담당')
    road_now = road_c(W('d'))
    mgr.on(on_msg('게임시작'), S_('lt', timer()),
           until(eq(V('게임중'), 0),
                 S_('dt', sub(timer(), W('lt'))), S_('lt', timer()), *clamp('k22_dt', 0, 0.1), S_('f', mul(W('dt'), 60)),
                 if_(key(K_LEFT), C_('h', mul(W('f'), -2.4))), if_(key(K_RIGHT), C_('h', mul(W('f'), 2.4))),
                 S_('h', mul(W('h'), sub(1, mul(W('f'), 0.006)))), *clamp('k22_h', -75, 75),
                 S_('A', add(70, mul(W('d'), 0.016))), *clamp('k22_A', 0, 150),
                 S_('rc', road_now),
                 ifelse(gt(abs_(sub(W('x'), W('rc'))), HW),
                        [S_('g', 0.07), ifelse(gt(abs_(sub(W('x'), W('rc'))), 90), [S_('tg', 15)], [S_('tg', 45)]),
                         if_(eq(W('off'), 0), S_('off', 1), cast('k22_빠짐'))],
                        [S_('g', 0.03), S_('tg', VMAX), S_('off', 0)]),
                 C_('vx', mul(mul(sub(mul(W('sp'), sin_(W('h'))), W('vx')), W('g')), W('f'))),
                 C_('x', mul(W('vx'), W('dt'))),
                 if_(gt(abs_(W('x')), 226), *clamp('k22_x', -226, 226), S_('vx', 0), S_('sp', mul(W('sp'), 0.9))),
                 C_('d', mul(mul(W('sp'), cos_(W('h'))), W('dt'))),
                 if_(eq(W('off'), 0), C_('on', mul(mul(W('sp'), cos_(W('h'))), W('dt')))),
                 C_('sp', mul(mul(sub(W('tg'), W('sp')), 0.03), W('f'))),
                 C_('fr', 1),
                 if_(eq(mod(W('fr'), 8), 0), setv('미니표시', join(div(rounded(div(W('on'), 10)), 100), ' km')))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(div(sub(W('on'), 1100), 44)))
    mgr.on(on_msg('게임종료'), S_('run', 0))
    m.on_start(S_('d', 0), S_('x', 20), S_('h', 0), S_('vx', 0), S_('sp', 60), S_('A', 70), S_('on', 0), S_('off', 0), S_('fr', 0),
               S_('f', 1), S_('run', 1))
    m.snd('k22_빠짐', play('bad'))
    m.finish('꽁꽁 언 미시령 옛길! 차는 핸들을 꺾어도 늦게 돌아요.\n도로 밖 눈더미에 빠지지 않게 멀리 달리세요!',
             '조작: ← → 핸들  ·  미리미리 꺾고 일찍 풀기  ·  40초')
    return True


# ================================================================== 23. 크레인 운전
@game(23)
def g23(P, ctx):
    TL, NB = 60, 5
    P0 = 82                                   # 줄이 매달린 높이
    QX0, QX1, QY = -240, -68, -78             # 부두
    SX0, SX1, SY = -48, 224, -74              # 배 갑판
    SPOTS = [0, 44, 88, 132, 176]
    HOME = [-222, -191, -160, -129, -98]
    m = mg(P, ctx, T, 23, time_limit=TL, status='0/5 · 0점', dim=70)
    vars_(P, *['k23_' + v for v in ('tx', 'tv', 'ptv', 'a', 'L', 'th', 'om', 'hx', 'hy', 'phx', 'hvx', 'fl', 'lmax', 'carry', 'run',
                                    'cool', 'got', 'res')])
    W = lambda n: V('k23_' + n)
    S_ = lambda n, v: setv('k23_' + n, v)
    C_ = lambda n, v: chg('k23_' + n, v)
    P.list('k23_spot', [0] * NB)
    P.list('k23_bx', HOME)
    P.list('k23_by', [QY + 11] * NB)
    P.list('k23_bs', [0] * NB)

    def floor_of(xe, var):
        """xe 아래 바닥 높이를 var 에."""
        return [ifelse(lt(xe, QX1), [setv(var, QY)],
                       [ifelse(and_(gt(xe, SX0), lt(xe, SX1)), [setv(var, SY)], [setv(var, -118)])])]

    m.S('부두', AC.quay(172, 44), (QX0 + QX1) / 2, QY - 22)
    m.S('배', AC.ship(272, 58), (SX0 + SX1) / 2, SY + 10 - 29)
    for k, sx in enumerate(SPOTS):
        sp = m.S('자리%d' % (k + 1), AC.spot_marker(), sx, SY + 11)
        sp.on(on_msg('k23_칸'), ifelse(eq(LGET('k23_spot', k + 1), 0), [show()], [hide()]))
    m.S('레일', AC.crane_rail(), 0, P0 + 7)
    cable = m.S('케이블', A.clear_dot(), 0, P0)
    cable.on(on_scene(), pen_up(), pen_clear(), pen_color('#2A2F45'), pen_size(1.6), xy(0, P0), pen_down(), xy(0, P0 - 60), pen_up())
    cable.on(on_msg('게임시작'), until(eq(W('run'), 0), pen_up(), pen_clear(), xy(W('tx'), P0), pen_down(), xy(W('hx'), W('hy')), pen_up()),
             pen_clear())
    tro = m.S('트롤리', AC.trolley(), 0, P0 + 4)
    tro.on(on_msg('게임시작'), until(eq(W('run'), 0), lx(W('tx'))))
    hk = m.S('갈고리', [('n', AC.hook(0)), ('s', AC.hook(1))], 0, P0 - 40)
    hk.local('k23_st', 0)
    hk.on(on_msg('게임시작'), setv('k23_st', 0), shape('n'),
          until(eq(W('run'), 0), xy(W('hx'), W('hy')), rot(mul(W('th'), -1)),
                ifelse(and_(lt(abs_(W('th')), 2.5), lt(abs_(W('om')), 0.25)),
                       [if_(eq(V('k23_st'), 0), setv('k23_st', 1), shape('s'))],
                       [if_(eq(V('k23_st'), 1), setv('k23_st', 0), shape('n'))])))
    # 컨테이너 5개 (복제본)
    box = m.S('컨테이너', [('b%d' % k, AC.container(k)) for k in range(NB)], 0, -300, visible=False)
    for v in ('k23_i', 'k23_s', 'k23_vx', 'k23_vy', 'k23_f2', 'k23_j', '복제'):
        box.local(v, 0)
    box.on(on_scene(), setv('k23_i', 0), rep(NB, chg('k23_i', 1), clone_self()))
    BX, BY = LGET('k23_bx', V('k23_i')), LGET('k23_by', V('k23_i'))
    save_pos = [lst_set('k23_bx', V('k23_i'), obj_x()), lst_set('k23_by', V('k23_i'), obj_y()), lst_set('k23_bs', V('k23_i'), V('k23_s'))]
    land = [
        setv('k23_s', 0), rot(0),
        *floor_of(obj_x(), 'k23_f2'),
        ifelse(eq(V('k23_f2'), -118),
               # 바다에 빠짐 → 부두 제자리로
               [cast('k23_풍덩'), chg('틀림', 1), rep(8, mvy(-2), fx_add('transparency', 12), wait(0.02)), hide(),
                xy(LGET('k23_hx0', V('k23_i')), QY + 11), fx('transparency', 0), wait(0.4), show()],
               [ly(add(V('k23_f2'), 11)),
                if_(eq(V('k23_f2'), SY),
                    setv('k23_j', add(rounded(div(obj_x(), 44)), 1)), *clamp('k23_j', 1, NB),
                    setv('k23_vx', abs_(sub(obj_x(), mul(sub(V('k23_j'), 1), 44)))),
                    ifelse(and_(lt(V('k23_vx'), 13), eq(LGET('k23_spot', V('k23_j')), 0)),
                           [setv('k23_s', 3), lx(mul(sub(V('k23_j'), 1), 44)), lst_set('k23_spot', V('k23_j'), 1), chg('맞춤', 1),
                            ifelse(lt(V('k23_vx'), 6), [chg('합계', 18), setv('_mv', 1)], [chg('합계', 12), setv('_mv', 2)]),
                            cast('k23_칸'), cast('k23_놓음')],
                           [setv('_mv', 3), cast('k23_놓음'),
                            if_(eq(LGET('k23_spot', V('k23_j')), 1), if_(lt(V('k23_vx'), 28), ly(add(SY, 33))))]))]),
        *save_pos, cast('k23_상태')]
    box.on(on_clone(), setv('복제', 1), setv('k23_s', 0), shape(V('k23_i')), xy(BX, BY), show(),
           until(eq(W('run'), 0),
                 ifelse(eq(V('k23_s'), 1),
                        [xy(add(W('hx'), mul(sin_(W('th')), 15)), sub(W('hy'), mul(cos_(W('th')), 15))), rot(mul(W('th'), -1))],
                        [ifelse(eq(V('k23_s'), 2),
                                [chg('k23_vy', -0.35), mvx(V('k23_vx')), mvy(V('k23_vy')), rot(mul(V('k23_vx'), 4)),
                                 *floor_of(obj_x(), 'k23_f2'),
                                 if_(lt(sub(obj_y(), 11), V('k23_f2')), *land),
                                 if_(lt(obj_y(), -130), *land)],
                                [wait(0.03)])])),
           del_clone())
    box.on(on_msg('k23_집기'), if_(and_(eq(V('복제'), 1), eq(V('k23_s'), 0)),
                                 if_(and_(lt(abs_(sub(obj_x(), W('hx'))), 12), lt(abs_(sub(add(obj_y(), 15), W('hy'))), 9)),
                                     if_(eq(W('carry'), 0), S_('carry', V('k23_i')), setv('k23_s', 1), lst_set('k23_bs', V('k23_i'), 1),
                                         to_front(), cast('k23_잡음')))))
    box.on(on_msg('k23_놓기'), if_(and_(eq(V('복제'), 1), eq(V('k23_s'), 1)),
                                 setv('k23_s', 2), setv('k23_vx', W('hvx')), setv('k23_vy', 0), lst_set('k23_bs', V('k23_i'), 2)))
    P.list('k23_hx0', HOME)
    keys = hidden(m, '크레인키')
    keys.on(on_key(K_SPACE), if_(and_(eq(V('게임중'), 1), eq(W('cool'), 0)), S_('cool', 1),
                                 ifelse(eq(W('carry'), 0), [cast('k23_집기'), wait(0.05), if_(eq(W('carry'), 0), cast('k23_헛손'))],
                                        [cast('k23_놓기'), S_('carry', 0), cast('k23_뗌')]),
                                 wait(0.15), S_('cool', 0)))
    mgr = hidden(m, '크레인담당')
    mgr.on(on_msg('게임시작'),
           until(eq(W('run'), 0),
                 ifelse(key(K_RIGHT), [C_('tv', 0.16)], [ifelse(key(K_LEFT), [C_('tv', -0.16)], [S_('tv', mul(W('tv'), 0.86))])]),
                 *clamp('k23_tv', -2.4, 2.4),
                 C_('tx', W('tv')), if_(gt(abs_(W('tx')), 220), *clamp('k23_tx', -220, 220), S_('tv', 0)),
                 S_('a', sub(W('tv'), W('ptv'))), S_('ptv', W('tv')),
                 if_(key(K_UP), C_('L', -1.4)), if_(key(K_DOWN), C_('L', 1.4)),
                 *floor_of(W('hx'), 'k23_fl'), S_('lmax', sub(sub(P0, W('fl')), 26)),
                 if_(lt(W('L'), 20), S_('L', 20)), if_(gt(W('L'), W('lmax')), S_('L', W('lmax'))),
                 C_('om', mul(add(mul(sin_(W('th')), 0.25), mul(cos_(W('th')), W('a'))), div(-57.3, W('L')))),
                 S_('om', mul(W('om'), 0.996)), C_('th', W('om')), *clamp('k23_th', -75, 75),
                 S_('phx', W('hx')),
                 S_('hx', add(W('tx'), mul(W('L'), sin_(W('th'))))), S_('hy', sub(P0, mul(W('L'), cos_(W('th'))))),
                 S_('hvx', sub(W('hx'), W('phx')))))
    mgr.on(on_msg('k23_상태'), setv('미니표시', join(V('맞춤'), '/5 · ', V('합계'), '점')),
           if_(ge(V('맞춤'), NB), wait(0.6), *m.end_blocks(add(V('합계'), mul(V('남은시간'), 0.3)))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(V('합계')))
    mgr.on(on_msg('게임종료'), S_('run', 0))
    res = m.S('놓기판정', [('a', K.big_text('딱 맞게!', 26, 'royal')), ('b', K.big_text('좋아요!', 24, 'white')),
                          ('c', K.big_text('자리 밖!', 22, 'red'))], 88, 10, visible=False)
    res.on(on_msg('k23_놓음'), shape(V('_mv')), res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.016)), wait(0.6), hide())
    spl = m.S('풍덩', K.big_text('풍덩!', 24, 'red'), -58, -40, visible=False)
    spl.on(on_msg('k23_풍덩'), show(), wait(0.7), hide())
    m.on_start(S_('tx', 0), S_('tv', 0), S_('ptv', 0), S_('a', 0), S_('L', 60), S_('th', 0), S_('om', 0), S_('hx', 0),
               S_('hy', P0 - 60), S_('carry', 0), S_('run', 1), S_('cool', 0), setv('맞춤', 0), setv('합계', 0), setv('틀림', 0),
               *[lst_set('k23_spot', k + 1, 0) for k in range(NB)], *[lst_set('k23_bx', k + 1, HOME[k]) for k in range(NB)],
               *[lst_set('k23_by', k + 1, QY + 11) for k in range(NB)], *[lst_set('k23_bs', k + 1, 0) for k in range(NB)],
               cast('k23_칸'))
    m.snd('k23_잡음', play('click'))
    m.snd('k23_뗌', play('pop'))
    m.snd('k23_헛손', play('tick'))
    m.snd('k23_풍덩', play('splash'))
    m.snd('k23_놓음', ifelse(le(V('_mv'), 2), [play('good')], [play('bad')]))
    m.finish('컨테이너 5개를 배 위 초록 칸에 옮기세요! 짐이 흔들리면\n어긋나게 떨어져요. 갈고리가 초록빛일 때 놓으면 딱!',
             '조작: ← → 크레인 이동 · ↑ ↓ 줄 감기/풀기 · SPACE 집기/놓기')
    return True


# ================================================================== 24. 야구 타격
@game(24)
def g24(P, ctx):
    NP = 10
    ZX, ZY = 0, -56                      # 스트라이크 존 가운데
    RX, RY = 6, 38                       # 투수 손
    m = mg(P, ctx, T, 24, status='투구 0/%d · 0점' % NP, dim=70)
    vars_(P, *['k24_' + v for v in ('t0', 'T', 'tarr', 'ts', 'sw', 'ty', 'ball', 'x1', 'y1', 'bx', 'by', 'p', 'kmh', 'n', 'res',
                                    'fl', 'hit', 'e', 'a', 'b')])
    W = lambda n: V('k24_' + n)
    S_ = lambda n, v: setv('k24_' + n, v)
    # 구종: 1 직구 2 체인지업 3 커브, +10 이면 볼
    P.list('k24_seq', [1, 1, 3, 2, 1, 3, 2, 3, 11, 13])
    P.list('k24_pts', [11, 8, 3, 0, 6, 0])
    m.S('마운드', AC.mound(), 0, 22)
    pit = m.S('투수', [('set', AC.pitcher('set')), ('wind', AC.pitcher('wind')), ('throw', AC.pitcher('throw'))], 0, 40)
    pit.on(on_msg('k24_준비'), shape('set'), wait(0.25), shape('wind'))
    pit.on(on_msg('k24_던짐'), shape('throw'), wait(0.5), shape('set'))
    m.S('홈플레이트', AC.home_plate(), 0, -108)
    m.S('존', AC.strike_zone(), ZX, ZY)
    bat = m.S('타자', [('ready', AC.batter('ready')), ('swing', AC.batter('swing')), ('follow', AC.batter('follow'))], -50, -72)
    bat.on(on_msg('k24_스윙'), shape('swing'), wait(0.09), shape('follow'), wait(0.45), shape('ready'))
    ball = m.S('공', AC.baseball(), RX, RY, visible=False)
    BP = sub(timer(), W('t0'))
    ball.on(on_msg('k24_던짐'), S_('hit', 0), ball.pct(30), xy(RX, RY), show(),
            until(or_(gt(W('p'), 1.12), eq(W('hit'), 1)),
                  S_('p', div(sub(timer(), W('t0')), W('T'))),
                  S_('a', mul(mul(W('p'), sub(1, W('p'))), 4)),
                  xy(add(add(RX, mul(sub(W('x1'), RX), W('p'))), mul(W('bx'), W('a'))),
                     add(add(RY, mul(sub(W('y1'), RY), W('p'))), mul(W('by'), W('a')))),
                  ball.pct(add(30, mul(mul(W('p'), W('p')), 80)))),
            if_(eq(W('hit'), 0), hide()))
    ball.on(on_msg('k24_맞음'),
            ifelse(eq(W('res'), 1), [rep(24, mvy(7), mvx(1), ball.grow_pct(-4), wait(0.016))],
                   [ifelse(eq(W('res'), 2), [setv('_mx', rnd(-5, 5)), rep(20, mvy(3), mvx(V('_mx')), ball.grow_pct(-3), wait(0.016))],
                           [rep(16, mvy(4), mvx(-9), wait(0.016))])]),
            hide())
    # 구속판
    panel(P, m.sc, '구속판', 176, 40, 104, 70, 'glass')
    m.T('구속제목', '구속', 176, 64, 9, C_DIM, F_BODY, True, 0, w=90, h=14)
    spd = m.T('구속글', '- km/h', 176, 44, 16, C_WHITE, F_NUM, False, 0, w=96, h=22)
    spd.on(on_msg('k24_준비'), write('- km/h'))
    spd.on(on_msg('k24_던짐'), write(join(W('kmh'), ' km/h')))
    kind = m.T('구종글', '', 176, 22, 11, C_ACC, F_BODY, True, 0, w=96, h=16)
    kind.on(on_msg('k24_준비'), write(''))
    kind.on(on_msg('k24_판정'), write(LGET('k24_name', mod(W('ty'), 10))))
    P.list('k24_name', ['직구', '체인지업', '커브'])
    keys = hidden(m, '타격키')
    keys.on(on_key(K_SPACE), if_(and_(eq(W('fl'), 1), eq(W('sw'), 0)), S_('ts', timer()), S_('sw', 1), cast('k24_스윙')))
    res = m.S('타격결과', [('a', K.big_text('홈런!!', 40, 'royal')), ('b', K.big_text('안타!', 32, 'white')),
                          ('c', K.big_text('파울', 28, 'gray')), ('d', K.big_text('헛스윙', 28, 'red')),
                          ('e', K.big_text('볼! 잘 참았어요', 22, 'green')), ('f', K.big_text('스트라이크!', 26, 'red'))], 30, 70, visible=False)
    res.on(on_msg('k24_판정'), shape(W('res')), res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.016)), wait(0.8), hide())
    mgr = hidden(m, '타격담당')
    shuffle = [rep(12, setv('_ma', rnd(2, NP)), setv('_mb', rnd(2, NP)), setv('_mk', LGET('k24_seq', V('_ma'))),
                   lst_set('k24_seq', V('_ma'), LGET('k24_seq', V('_mb'))), lst_set('k24_seq', V('_mb'), V('_mk')))]
    pitch = [
        S_('ty', LGET('k24_seq', W('n'))), S_('ball', 0), if_(gt(W('ty'), 10), S_('ball', 1)),
        # 도착점
        ifelse(eq(W('ball'), 0), [S_('x1', add(ZX, rnd(-15, 15))), S_('y1', add(ZY, rnd(-17, 17)))],
               [ifelse(eq(rnd(0, 1), 0), [S_('x1', mul(rnd(42, 54), sub(mul(rnd(0, 1), 2), 1))), S_('y1', add(ZY, rnd(-10, 10)))],
                       [S_('x1', rnd(-12, 12)), S_('y1', sub(ZY, rnd(44, 52)))])]),
        ifelse(eq(mod(W('ty'), 10), 1), [S_('T', 0.6), S_('bx', 0), S_('by', 5), S_('kmh', rnd(145, 153))],
               [ifelse(eq(mod(W('ty'), 10), 2), [S_('T', 0.9), S_('bx', 0), S_('by', 12), S_('kmh', rnd(121, 128))],
                       [S_('T', 0.8), S_('bx', -26), S_('by', 24), S_('kmh', rnd(110, 118))])]),
        S_('sw', 0), S_('p', 0), cast('k24_준비'), wait(div(rnd(70, 140), 100)),
        S_('t0', timer()), S_('tarr', add(W('t0'), W('T'))), S_('fl', 1), cast('k24_던짐'),
        wait_until(or_(eq(W('sw'), 1), gt(timer(), add(W('tarr'), 0.2)))),
        ifelse(eq(W('sw'), 1),
               [S_('e', abs_(sub(W('ts'), W('tarr')))),
                ifelse(eq(W('ball'), 1), [S_('res', 4)],
                       [ifelse(le(W('e'), 0.035), [S_('res', 1)],
                               [ifelse(le(W('e'), 0.075), [S_('res', 2)], [ifelse(le(W('e'), 0.12), [S_('res', 3)], [S_('res', 4)])])])]),
                if_(le(W('res'), 3), S_('hit', 1), cast('k24_맞음'))],
               [ifelse(eq(W('ball'), 1), [S_('res', 5)], [S_('res', 6)])]),
        S_('fl', 0), chg('합계', LGET('k24_pts', W('res'))), cast('k24_판정'),
        setv('미니표시', join('투구 ', W('n'), '/', NP, ' · ', V('합계'), '점')),
        wait(1.3)]
    mgr.on(on_msg('게임시작'), *shuffle, S_('n', 1), until(gt(W('n'), NP), *pitch, chg('k24_n', 1)),
           *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), S_('n', 0), S_('fl', 0), S_('sw', 0), S_('p', 0),
               *[lst_set('k24_seq', k + 1, v) for k, v in enumerate([1, 1, 3, 2, 1, 3, 2, 3, 11, 13])])
    m.snd('k24_스윙', play('jump'))
    m.snd('k24_던짐', play('click'))
    m.snd('k24_판정', ifelse(eq(W('res'), 1), [play('fanfare')],
                           [ifelse(le(W('res'), 2), [play('hit')], [ifelse(eq(W('res'), 5), [play('good')], [play('bad')])])]))
    m.finish('공이 네모 존에 닿는 순간 SPACE로 스윙! (10구)\n구속을 보고 변화구를 읽고, 존 밖 볼은 참으세요!',
             '조작: SPACE 스윙  ·  홈런 11 · 안타 8 · 파울 3 · 볼 참기 6점')
    return True


# ================================================================== 25. 매듭 잇기 (Flow)
K25_PUZ = ['0000001000001040020032034', '0000002120030003004040100',
           '0012500000132003050040400', '1020000300005001045320004',
           '0012003452100030045000000', '0254001034005000001000023']


@game(25)
def g25(P, ctx):
    TL, N, CS = 100, 5, 38
    BX, BY = -44, -14
    NC = [4, 5, 5]
    m = mg(P, ctx, T, 25, time_limit=TL, status='퍼즐 1/3', dim=90)
    vs = ('lv', 'nc', 'c', 'dr', 'last', 'lo', 'mc', 'mr', 'lc', 'lr', 'nb', 'fill', 'cutc', 'cutl', 'ok', 'md', 'in', 'pz', 'sum',
          'full', 'bc')
    vars_(P, *['k25_' + v for v in vs])
    W = lambda n: V('k25_' + n)
    S_ = lambda n, v: setv('k25_' + n, v)
    C_ = lambda n, v: chg('k25_' + n, v)
    P.list('k25_puz', K25_PUZ)
    P.list('k25_dot', [0] * 25)
    P.list('k25_cell', [0] * 25)
    P.list('k25_ord', [0] * 25)
    P.list('k25_comp', [0] * 5)
    mt = [0] * 16
    for msk, ty in ((1, 0), (2, 1), (4, 2), (8, 3), (5, 4), (10, 5), (3, 6), (6, 7), (12, 8), (9, 9)):
        mt[msk] = ty
    md = [10] * 16
    for msk, ty in ((1, 11), (2, 12), (4, 13), (8, 14)):
        md[msk] = ty
    P.list('k25_mt', mt)
    P.list('k25_md', md)
    CELL = lambda i: LGET('k25_cell', i)
    ORD = lambda i: LGET('k25_ord', i)
    DOT = lambda i: LGET('k25_dot', i)
    m.S('판', AC.flow_board(N, CS), BX, BY)
    pics = [('e', AC.blank(CS, CS))] + [('c%d%s' % (ci, ty), AC.flow_cell(ci, ty, CS)) for ci in range(5) for ty in AC.FLOW_TYPES]
    cell = m.S('칸', pics, 0, -300, visible=False)
    for v in ('k25_i', 'k25_r', 'k25_k', 'k25_m', 'k25_sh', '복제'):
        cell.local(v, 0)
    cell.on(on_scene(), setv('k25_i', 0), rep(N * N, chg('k25_i', 1), clone_self()))
    cell.on(on_clone(), setv('복제', 1), setv('k25_r', floor(div(sub(V('k25_i'), 1), N))), setv('k25_k', mod(sub(V('k25_i'), 1), N)),
            xy(add(BX - 2 * CS, mul(V('k25_k'), CS)), sub(BY + 2 * CS, mul(V('k25_r'), CS))), setv('k25_sh', 1), shape(1), show())
    me = V('k25_i')

    def arm(cond, j, bit):
        return if_(cond, if_(eq(CELL(j), CELL(me)),
                             if_(and_(gt(ORD(j), 0), eq(abs_(sub(ORD(j), ORD(me))), 1)), chg('k25_m', bit))))
    cell.on(on_msg('k25_그림'), if_(eq(V('복제'), 1),
            setv('k25_m', 0),
            if_(and_(gt(CELL(me), 0), gt(ORD(me), 0)),
                arm(gt(V('k25_r'), 0), sub(me, N), 1), arm(lt(V('k25_k'), N - 1), add(me, 1), 2),
                arm(lt(V('k25_r'), N - 1), add(me, N), 4), arm(gt(V('k25_k'), 0), sub(me, 1), 8)),
            ifelse(eq(CELL(me), 0), [setv('_mi', 1)],
                   [ifelse(gt(DOT(me), 0), [setv('_mi', add(add(mul(sub(CELL(me), 1), 15), 2), LGET('k25_md', add(V('k25_m'), 1))))],
                           [setv('_mi', add(add(mul(sub(CELL(me), 1), 15), 2), LGET('k25_mt', add(V('k25_m'), 1))))])]),
            if_(ne(V('_mi'), V('k25_sh')), setv('k25_sh', V('_mi')), shape(V('k25_sh')))))
    cell.on(on_msg('k25_자르기'), if_(eq(V('복제'), 1),
            if_(and_(eq(CELL(me), W('cutc')), gt(ORD(me), W('cutl'))),
                lst_set('k25_ord', me, 0), if_(eq(DOT(me), 0), lst_set('k25_cell', me, 0), C_('fill', -1)))))
    # 오른쪽 정보판
    panel(P, m.sc, '정보판', 168, 4, 118, 128, 'glass')
    info = m.T('정보글', '', 168, 24, 11, C_WHITE, F_BODY, True, 0, w=110, h=70)
    info.on(on_msg('k25_정보'), write(join('퍼즐 ', W('lv'), ' / 3\n\n이은 선 ', W('sum'), ' / ', W('nc'), '\n채운 칸 ', W('fill'), ' / 25')))
    cut = lambda c, lim: [S_('cutc', c), S_('cutl', lim), cast_wait('k25_자르기')]
    redo = [if_(and_(eq(V('게임중'), 1), eq(W('ok'), 0)), S_('dr', 0),
                *[x for c in range(1, 6) for x in cut(c, 0)], *[lst_set('k25_comp', c, 0) for c in range(1, 6)],
                S_('sum', 0), cast_wait('k25_그림'), cast('k25_정보'))]
    button(P, m.sc, '다시하기', '처음부터', 168, -36, 96, 24, 'steel', actions=redo)
    m.T('도움말', '점을 눌러 끌기\n선을 눌러 고치기', 168, -64, 8, C_DIM, F_BODY, True, 0, w=110, h=26)
    sgn = lambda e: div(e, abs_(e))
    setup = [S_('pz', LGET('k25_puz', add(mul(sub(W('lv'), 1), 2), rnd(1, 2)))),
             *[x for i in range(1, 26) for x in (lst_set('k25_dot', i, char_at(W('pz'), i)), lst_set('k25_cell', i, char_at(W('pz'), i)),
                                                  lst_set('k25_ord', i, 0))],
             *[lst_set('k25_comp', c, 0) for c in range(1, 6)],
             ifelse(eq(W('lv'), 1), [S_('nc', NC[0])], [S_('nc', NC[1])]), S_('fill', mul(W('nc'), 2)), S_('sum', 0),
             S_('dr', 0), S_('ok', 0), cast_wait('k25_그림'), cast('k25_정보'), setv('미니표시', join('퍼즐 ', W('lv'), '/3'))]
    step = [S_('lc', mod(sub(W('last'), 1), N)), S_('lr', floor(div(sub(W('last'), 1), N))),
            ifelse(ne(W('mc'), W('lc')), [S_('nb', add(W('last'), sgn(sub(W('mc'), W('lc')))))],
                   [S_('nb', add(W('last'), mul(sgn(sub(W('mr'), W('lr'))), N)))]),
            ifelse(eq(CELL(W('nb')), 0),
                   [lst_set('k25_cell', W('nb'), W('c')), C_('lo', 1), lst_set('k25_ord', W('nb'), W('lo')), S_('last', W('nb')),
                    C_('fill', 1), cast_wait('k25_그림'), cast('k25_정보'), cast('k25_톡')],
                   [ifelse(eq(CELL(W('nb')), W('c')),
                           [ifelse(eq(ORD(W('nb')), 0),
                                   [C_('lo', 1), lst_set('k25_ord', W('nb'), W('lo')), lst_set('k25_comp', W('c'), 1), S_('dr', 0),
                                    S_('sum', add(*[LGET('k25_comp', c) for c in range(1, 6)])),
                                    cast_wait('k25_그림'), cast('k25_정보'), cast('k25_이음'),
                                    if_(eq(W('sum'), W('nc')), S_('ok', 1))],
                                   [if_(lt(ORD(W('nb')), W('lo')),
                                        *cut(W('c'), ORD(W('nb'))), S_('lo', ORD(W('nb'))), S_('last', W('nb')),
                                        cast_wait('k25_그림'), cast('k25_정보'))])],
                           [if_(eq(W('bc'), 0), S_('bc', 1), cast('k25_막힘'))])])]
    press = [S_('nb', add(add(mul(W('mr'), N), W('mc')), 1)),
             if_(gt(CELL(W('nb')), 0),
                 S_('c', CELL(W('nb'))),
                 ifelse(gt(DOT(W('nb')), 0),
                        [*cut(W('c'), 0), lst_set('k25_ord', W('nb'), 1), S_('lo', 1)],
                        [*cut(W('c'), ORD(W('nb'))), S_('lo', ORD(W('nb')))]),
                 lst_set('k25_comp', W('c'), 0), S_('sum', add(*[LGET('k25_comp', c) for c in range(1, 6)])),
                 S_('last', W('nb')), S_('dr', 1), cast_wait('k25_그림'), cast('k25_정보'), cast('k25_톡'))]
    frame = [S_('mc', floor(div(sub(mouse_x(), BX - 2.5 * CS), CS))), S_('mr', floor(div(sub(BY + 2.5 * CS, mouse_y()), CS))),
             S_('in', 0), if_(and_(and_(ge(W('mc'), 0), lt(W('mc'), N)), and_(ge(W('mr'), 0), lt(W('mr'), N))), S_('in', 1)),
             ifelse(mouse_down(),
                    [ifelse(eq(W('dr'), 0), [if_(and_(eq(W('md'), 0), eq(W('in'), 1)), *press)],
                            [if_(and_(eq(W('in'), 1), ne(add(add(mul(W('mr'), N), W('mc')), 1), W('last'))), *step)]),
                     S_('md', 1)],
                    [S_('dr', 0), S_('md', 0), S_('bc', 0)])]
    mgr = hidden(m, '매듭담당')
    mgr.on(on_msg('게임시작'), S_('lv', 1),
           until(or_(gt(W('lv'), 3), eq(V('게임중'), 0)),
                 *setup,
                 until(or_(eq(W('ok'), 1), eq(V('게임중'), 0)), *frame),
                 if_(eq(W('ok'), 1),
                     S_('full', 0), if_(eq(W('fill'), 25), S_('full', 1)),
                     chg('합계', add(26, mul(W('full'), 6))), setv('_mv', add(W('full'), 1)), cast('k25_완성'), wait(1.4)),
                 C_('lv', 1)),
           *m.end_blocks(add(V('합계'), mul(V('남은시간'), 0.12))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(V('합계'), mul(W('sum'), 4))))
    done = m.S('완성글', [('a', K.big_text('완성!', 34, 'royal')), ('b', K.big_text('빈칸 없이 완벽!', 28, 'royal'))], BX, BY,
               visible=False)
    done.on(on_msg('k25_완성'), shape(V('_mv')), done.pct(40), show(), rep(5, done.grow_pct(14), wait(0.016)), wait(0.9), hide())
    m.on_start(setv('합계', 0), S_('lv', 1), S_('dr', 0), S_('ok', 0), S_('md', 0), S_('sum', 0), S_('nc', 4),
               S_('pz', K25_PUZ[0]),
               *[x for i in range(1, 26) for x in (lst_set('k25_dot', i, char_at(W('pz'), i)), lst_set('k25_cell', i, char_at(W('pz'), i)),
                                                    lst_set('k25_ord', i, 0))],
               wait(0.6), cast('k25_그림'))
    m.snd('k25_톡', play('tick'))
    m.snd('k25_이음', play('coin'))
    m.snd('k25_막힘', play('bad'))
    m.snd('k25_완성', play('fanfare'))
    m.finish('같은 색 점끼리 칸을 따라 선으로 이으세요! 선끼리\n겹치면 안 돼요. 모든 칸을 채우면 보너스! (3판)',
             '조작: 점에서 마우스를 누른 채 끌기  ·  선을 다시 누르면 거기서부터 고치기')
    return True
