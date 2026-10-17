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
    mgr.on(on_msg('게임시작'), reset_timer(), start_timer(), *shuffle, S_('n', 1), until(gt(W('n'), NP), *pitch, chg('k24_n', 1)),
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


# ================================================================== 26. 관광객 통역
K26_GREET = ['Konnichiwa!', 'Arigatou!', 'Ni hao!', 'Xie xie!', 'Hello!', 'Hi there!', 'Bonjour!', 'Merci!', 'Hola!', 'Gracias!',
             'Guten Tag!', 'Danke!', 'Ciao!', 'Grazie!', 'Xin chao!', 'Cam on!', 'Sawasdee!', 'Khob khun!', 'Namaste!',
             'Dhanyavaad!', 'Privet!', 'Spasibo!', 'Ola! Tudo bem?', 'Obrigado!']


@game(26)
def g26(P, ctx):
    TL, NO = 35, 6
    TX, TY = 40, -2
    m = mg(P, ctx, T, 26, time_limit=TL, status='통역 0명', dim=70)
    vars_(P, *['k26_' + v for v in ('a', 'v', 'sty', 'pat', 'pt', 'ans', 'rdy', 'mood', 'n')])
    W = lambda n: V('k26_' + n)
    S_ = lambda n, v: setv('k26_' + n, v)
    P.list('k26_greet', K26_GREET)
    P.list('k26_all', list(range(1, 13)))
    P.list('k26_opt', [1, 2, 3, 4, 5, 6])
    m.S('안내소', K.badge('명동 통역 안내소', 116, 20, 'royal'), -164, 84)
    m.S('나', ctx['BUST']['me'], -190, 6, scale=0.45)
    itp = m.S('통역사', AC.interpreter(), -150, -6, visible=False)
    itp.on(on_msg('k26_맞음'), xy(-150, -6), show(), glide(0.3, TX - 32, TY - 4), wait(0.3), hide())
    tour = m.S('관광객', [('t%d%s' % (i, md), AC.tourist(i, md)) for i in range(4) for md in 'nhs'], 300, TY)
    tour.on(on_msg('k26_새손님'), shape(add(mul(sub(W('sty'), 1), 3), 1)), xy(300, TY), show(), glide(0.3, TX, TY))
    tour.on(on_msg('k26_맞음'), shape(add(mul(sub(W('sty'), 1), 3), 2)), wait(0.6), glide(0.25, -300, TY))
    tour.on(on_msg('k26_틀림'), shape(add(mul(sub(W('sty'), 1), 3), 3)), wait(0.4),
            if_(eq(W('rdy'), 1), shape(add(mul(sub(W('sty'), 1), 3), 1))))
    tour.on(on_msg('k26_떠남'), shape(add(mul(sub(W('sty'), 1), 3), 3)), wait(0.2), glide(0.3, 300, TY))
    bub = m.S('말풍선', AC.speech_bubble(), 8, 66, visible=False)
    say_ = m.T('인사말', '', 8, 70, 15, '#1A2050', F_BODY, True, 0, w=140, h=24)
    bub.on(on_msg('k26_새손님'), wait(0.3), show())
    say_.on(on_msg('k26_새손님'), write(''), wait(0.3), write(LGET('k26_greet', add(mul(sub(W('a'), 1), 2), W('v')))))
    for o in (bub, say_):
        o.on(on_msg('k26_끝'), hide() if o is bub else write(''))
    pat = m.S('인내', [('p%d' % i, AC.patience_bar(i)) for i in range(11)], TX, TY - 50, visible=False)
    pat.on(on_msg('k26_새손님'), wait(0.3), show(), until(eq(W('rdy'), 0), ifelse(gt(W('pat'), 0), [shape(add(ceil_(W('pat')), 1))], [shape(1)]), wait(0.1)), hide())
    for j in range(NO):
        fx_ = -175 + 70 * j
        fl = m.S('국기%d' % (j + 1), [('f%d' % k, AC.flag_btn(k)) for k in range(12)], fx_, -100)
        fl.on(on_msg('k26_새손님'), shape(LGET('k26_opt', j + 1)))
        fl.on(on_click(), if_(eq(W('rdy'), 1),
                              ifelse(eq(LGET('k26_opt', j + 1), W('a')),
                                     [S_('ans', 1)],
                                     [chg('합계', -3), chg('틀림', 1), chg('k26_pat', -3), cast('k26_틀림'),
                                      fx('brightness', -40), wait(0.25), fx('brightness', 0)])))
        G.hover_scripts(fl)
    mgr = hidden(m, '통역담당')
    new = [rep(12, setv('_ma', rnd(1, 12)), setv('_mb', rnd(1, 12)), setv('_mk', LGET('k26_all', V('_ma'))),
               lst_set('k26_all', V('_ma'), LGET('k26_all', V('_mb'))), lst_set('k26_all', V('_mb'), V('_mk'))),
           S_('a', rnd(1, 12)), S_('v', rnd(1, 2)), S_('sty', rnd(1, 4)),
           *[lst_set('k26_opt', j, LGET('k26_all', j)) for j in range(1, NO + 1)],
           if_(not_(lst_has('k26_opt', W('a'))), lst_set('k26_opt', rnd(1, NO), W('a'))),
           S_('pat', 10), S_('ans', 0), cast('k26_새손님'), wait(0.3), S_('rdy', 1)]
    mgr.on(on_msg('게임시작'),
           until(eq(V('게임중'), 0),
                 *new,
                 until(or_(ne(W('ans'), 0), le(W('pat'), 0)), wait(0.05), chg('k26_pat', mul(-0.5, div(1, W('pt'))))),
                 S_('rdy', 0), cast('k26_끝'),
                 ifelse(eq(W('ans'), 1),
                        [chg('합계', add(8, mul(W('pat'), 0.3))), chg('맞춤', 1), cast('k26_맞음'), wait(0.85)],
                        [cast('k26_떠남'), wait(0.6)]),
                 setv('미니표시', join('통역 ', V('맞춤'), '명 · ', rounded(V('합계')), '점')),
                 S_('pt', sub(5.5, mul(V('맞춤'), 0.2))), if_(lt(W('pt'), 3), S_('pt', 3))))
    mgr.on(on_msg('시간끝'), S_('rdy', 0), *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('틀림', 0), S_('rdy', 0), S_('pt', 5.5))
    m.snd('k26_맞음', play('coin'))
    m.snd('k26_틀림', play('bad'))
    m.snd('k26_떠남', play('fail_big'))
    m.finish('명동에 온 관광객의 인사말을 보고 어느 나라 사람인지\n국기를 눌러 통역사를 보내세요! 빠를수록 점수 UP',
             '조작: 국기 클릭  ·  틀리면 -3점  ·  35초')
    return True


# ================================================================== 27. 장바구니 기억
@game(27)
def g27(P, ctx):
    R = 6
    NS = [5, 6, 7, 7, 8, 9]
    STIME = [3.0, 3.2, 3.5, 3.3, 3.8, 4.0]
    BX, BY = -62, -20
    SX = [BX - 72, BX, BX + 72]
    SY = [BY + 54, BY + 2, BY - 50]
    OX, OY = [132, 198, 132, 198], [8, 8, -58, -58]
    m = mg(P, ctx, T, 27, status='라운드 1/%d' % R, dim=70)
    vars_(P, *['k27_' + v for v in ('n', 'mi', 'miss', 'c', 'ans', 'rdy', 't0', 'rt', 'pos', 'j')])
    W = lambda n: V('k27_' + n)
    S_ = lambda n, v: setv('k27_' + n, v)
    P.list('k27_deck', list(range(1, 17)))
    P.list('k27_show', [0] * 9)
    P.list('k27_opt', [1, 2, 3, 4])
    P.list('k27_ns', NS)
    P.list('k27_st', STIME)
    m.S('바구니', AC.basket(), BX, BY - 4)
    items = [('i%d' % k, AC.market_item(k)) for k in range(16)]
    it = m.S('물건', items, 0, -300, scale=1.25, visible=False)
    it.local('k27_s', 0)
    it.local('복제', 0)
    it.on(on_scene(), setv('k27_s', 0), rep(9, chg('k27_s', 1), clone_self()))
    it.on(on_clone(), setv('복제', 1),
          xy(add(SX[0], mul(mod(sub(V('k27_s'), 1), 3), 72)), sub(SY[0], mul(floor(div(sub(V('k27_s'), 1), 3)), 52))))
    it.on(on_msg('k27_그림'), if_(eq(V('복제'), 1),
                                ifelse(gt(LGET('k27_show', V('k27_s')), 0), [shape(LGET('k27_show', V('k27_s'))), it.pct(60), show(),
                                                                            rep(4, it.grow_pct(10), wait(0.016))], [hide()])))
    cl = m.S('보자기', AC.cloth(), BX, BY - 8, visible=False)
    cl.on(on_msg('k27_덮기'), xy(BX, BY + 100), show(), glide(0.2, BX, BY - 8))
    cl.on(on_msg('k27_열기'), glide(0.2, BX, BY + 100), hide())
    cl.on(on_msg('k27_시작'), hide())
    msg = m.T('안내글', '', BX, 90, 13, C_WHITE, F_BODY, True, 0, w=240, h=20)
    q = m.T('질문글', '빠진 물건은?', 165, 52, 12, C_ACC, F_BODY, True, 0, w=130, h=18, visible=False)
    q.on(on_msg('k27_보기'), show())
    q.on(on_msg('k27_시작'), hide())
    for k in range(4):
        card = m.S('보기판%d' % (k + 1), [('n', AC.item_card()), ('s', AC.item_card(sel=True))], OX[k], OY[k], visible=False)
        oi = m.S('보기%d' % (k + 1), items, OX[k], OY[k], scale=1.25, visible=False)
        pick = [if_(eq(W('rdy'), 1), S_('ans', k + 1), S_('rt', sub(timer(), W('t0'))))]
        for o in (card, oi):
            o.on(on_msg('k27_시작'), hide())
            o.on(on_click(), *pick)
        card.on(on_msg('k27_보기'), shape('n'), show())
        card.on(on_msg('k27_정답보기'), if_(eq(W('c'), k + 1), shape('s'), rep(3, card.pct(112), wait(0.1), card.pct(100), wait(0.1))))
        oi.on(on_msg('k27_보기'), shape(LGET('k27_opt', k + 1)), show())
        G.hover_scripts(card)
    mgr = hidden(m, '기억담당')
    rnd_round = [
        S_('n', LGET('k27_ns', V('라운드'))),
        rep(16, setv('_ma', rnd(1, 16)), setv('_mb', rnd(1, 16)), setv('_mk', LGET('k27_deck', V('_ma'))),
            lst_set('k27_deck', V('_ma'), LGET('k27_deck', V('_mb'))), lst_set('k27_deck', V('_mb'), V('_mk'))),
        S_('mi', rnd(1, W('n'))), S_('miss', LGET('k27_deck', W('mi'))),
        *[ifelse(le(s, W('n')), [lst_set('k27_show', s, LGET('k27_deck', s))], [lst_set('k27_show', s, 0)]) for s in range(1, 10)],
        cast('k27_시작'), cast('k27_그림'), setv('미니표시', join('라운드 ', V('라운드'), '/', R, ' · ', V('맞춤'), '개'))]
    msg.on(on_msg('k27_시작'), write(join('물건 ', W('n'), '개! 잘 기억하세요')))
    msg.on(on_msg('k27_덮기'), write('하나를 몰래 꺼내는 중...'))
    msg.on(on_msg('k27_보기'), write('무엇이 사라졌을까요?'))
    msg.on(on_msg('k27_정답보기'), ifelse(eq(W('ans'), W('c')), [write('정답! 잘 기억했어요')], [write('아쉬워요! 초록 칸이 정답')]))
    rearrange = [
        *[lst_set('k27_show', s, 0) for s in range(1, 10)], S_('j', 1),
        rep(W('n'), if_(ne(W('j'), W('mi')), S_('pos', rnd(1, 9)), until(eq(LGET('k27_show', W('pos')), 0), S_('pos', rnd(1, 9))),
                        lst_set('k27_show', W('pos'), LGET('k27_deck', W('j')))),
            chg('k27_j', 1)),
        S_('c', rnd(1, 4)),
        *[ifelse(eq(qq, W('c')), [lst_set('k27_opt', qq, W('miss'))],
                 [ifelse(lt(qq, W('c')), [lst_set('k27_opt', qq, LGET('k27_deck', add(W('n'), qq)))],
                         [lst_set('k27_opt', qq, LGET('k27_deck', add(W('n'), qq - 1)))])]) for qq in range(1, 5)]]
    mgr.on(on_msg('게임시작'), reset_timer(), start_timer(), setv('라운드', 1),
           until(or_(gt(V('라운드'), R), eq(V('게임중'), 0)),
                 *rnd_round,
                 wait(LGET('k27_st', V('라운드'))),
                 cast('k27_덮기'), wait(0.5), *rearrange, wait(0.4), cast('k27_그림'), cast('k27_열기'), cast('k27_보기'),
                 S_('ans', 0), S_('t0', timer()), S_('rdy', 1),
                 wait_until(or_(gt(W('ans'), 0), gt(timer(), add(W('t0'), 8)))),
                 S_('rdy', 0),
                 ifelse(eq(W('ans'), W('c')),
                        [chg('맞춤', 1), chg('합계', 15), if_(lt(W('rt'), 6), chg('합계', mul(sub(6, W('rt')), 0.35))), setv('_mv', 1)],
                        [chg('틀림', 1), setv('_mv', 2)]),
                 cast('k27_정답보기'), cast('k27_판정'), wait(1.4), chg('라운드', 1)),
           *m.end_blocks(V('합계')))
    pop_fx(m, '기억판정', [('a', K.big_text('정답!', 34, 'royal')), ('b', K.big_text('땡!', 34, 'red'))], BX, BY, 'k27_판정', 0.5)
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('틀림', 0), S_('rdy', 0), setv('라운드', 1))
    m.snd('k27_덮기', play('pop'))
    m.snd('k27_판정', ifelse(eq(V('_mv'), 1), [play('good')], [play('bad')]))
    m.finish('서문시장 장바구니 속 물건을 잘 기억하세요! 보자기를\n걷으면 하나가 사라져요. 빠진 물건을 고르세요 (6라운드)',
             '조작: 오른쪽 보기 4개 중 하나 클릭  ·  빨리 맞히면 보너스')
    return True


# ================================================================== 28. 대나무 칼 꽂기
@game(28)
def g28(P, ctx):
    TL, LIVES = 60, 3
    CX, CY, RR = 0, 34, 46
    KD = RR + 19                       # 꽂힌 칼 가운데까지 거리
    HY = -96                           # 던지기 전 칼 위치
    NK = [6, 7, 8]
    PRE = [0, 2, 3]
    m = mg(P, ctx, T, 28, time_limit=TL, status='1단계 · ♥3', dim=60)
    vars_(P, *['k28_' + v for v in ('th', 'w', 'lv', 'left', 'pts', 'cur', 'lives', 'fly', 'na', 'hit', 'dt', 'lt', 't0', 'rdy', 'run')])
    W = lambda n: V('k28_' + n)
    S_ = lambda n, v: setv('k28_' + n, v)
    C_ = lambda n, v: chg('k28_' + n, v)
    P.list('k28_nk', NK)
    P.list('k28_pre', PRE)
    log = m.S('대나무통', AC.bamboo_log(RR), CX, CY)
    log.on(on_msg('게임시작'), until(eq(W('run'), 0), rot(W('th'))))
    log.on(on_msg('k28_통과'), rep(3, log.pct(112), wait(0.05), log.pct(100), wait(0.05)))
    stuck = m.S('꽂힌칼', AC.knife(), 0, -300, visible=False)
    for v in ('k28_a', '복제', 'k28_d'):
        stuck.local(v, 0)
    stuck.on(on_msg('k28_꽂기'), if_(eq(V('복제'), 0), setv('k28_a', W('na')), clone_self()))
    stuck.on(on_clone(), setv('복제', 1), show(),
             until(eq(W('run'), 0),
                   setv('k28_d', add(V('k28_a'), W('th'))),
                   xy(add(CX, mul(KD, sin_(V('k28_d')))), add(CY, mul(KD, cos_(V('k28_d'))))), rot(sub(V('k28_d'), 180))),
             del_clone())
    stuck.on(on_msg('k28_검사'), if_(eq(V('복제'), 1),
                                    if_(lt(abs_(sub(mod(add(sub(V('k28_a'), W('na')), 540), 360), 180)), 13), S_('hit', 1))))
    stuck.on(on_msg('k28_비우기'), if_(eq(V('복제'), 1), rep(8, mvy(-6), fx_add('transparency', 12), wait(0.02)), del_clone()))
    hand = m.S('던질칼', AC.knife(), 0, HY)
    hand.on(on_msg('k28_던짐'), rep(6, mvy((CY - KD - HY) / 6.0), wait(0.012)))
    hand.on(on_msg('k28_튕김'), rep(14, mvy(-6), mvx(4), rot_by(25), wait(0.016)), rot(0))
    hand.on(on_msg('k28_장전'), rot(0), xy(0, HY - 30), show(), glide(0.08, 0, HY))
    hand.on(on_msg('k28_숨김'), hide())
    left = m.T('남은칼', '', -176, -100, 12, C_WHITE, F_BODY, True, 0, w=110, h=20)
    left.on(on_msg('k28_정보'), write(join('남은 칼 ', W('left'), '개')))
    keys = hidden(m, '칼키')
    keys.on(on_key(K_SPACE), if_(and_(eq(W('rdy'), 1), eq(W('fly'), 0)), S_('fly', 1), cast('k28_휙')))
    # 회전 담당 (시간 기준이라 프레임 속도와 무관)
    spin = hidden(m, '회전담당')
    spin.on(on_msg('게임시작'), S_('lt', timer()),
            until(eq(W('run'), 0),
                  S_('dt', sub(timer(), W('lt'))), S_('lt', timer()), *clamp('k28_dt', 0, 0.1),
                  ifelse(eq(W('lv'), 1), [S_('w', 2.1)],
                         [ifelse(eq(W('lv'), 2), [S_('w', add(2.4, mul(1.7, sin_(mul(sub(timer(), W('t0')), 110)))))],
                                 [S_('w', add(0.7, mul(3.6, sin_(mul(sub(timer(), W('t0')), 75)))))])]),
                  S_('th', mod(add(W('th'), mul(mul(W('w'), W('dt')), 60)), 360))))
    mgr = hidden(m, '칼담당')
    start_level = [cast_wait('k28_비우기'), S_('left', LGET('k28_nk', W('lv'))), S_('cur', 0), S_('t0', timer()),
                   rep(LGET('k28_pre', W('lv')), S_('na', rnd(0, 359)), S_('hit', 0), cast_wait('k28_검사'),
                       if_(eq(W('hit'), 0), cast_wait('k28_꽂기'))),
                   cast('k28_정보'), cast('k28_장전'), S_('fly', 0), S_('rdy', 1),
                   setv('미니표시', join(W('lv'), '단계 · ♥', W('lives')))]
    score = add(mul(add(W('pts'), W('cur')), 4.4), ifelse_score(W))
    mgr.on(on_msg('게임시작'), S_('lv', 1), *start_level)
    mgr.on(on_msg('k28_휙'),
           cast('k28_던짐'), wait(0.08),
           S_('na', mod(sub(180, W('th')), 360)), S_('hit', 0), cast_wait('k28_검사'),
           ifelse(eq(W('hit'), 1),
                  [S_('rdy', 0), cast('k28_쨍'), cast('k28_튕김'), C_('lives', -1), wait(0.8),
                   ifelse(le(W('lives'), 0), [S_('cur', 0), *m.end_blocks(score)],
                          [S_('cur', 0), cast('k28_실패글'), wait(0.6), *start_level])],
                  [cast('k28_꽂기'), cast('k28_숨김'), cast('k28_퍽'), C_('cur', 1), C_('left', -1), cast('k28_정보'),
                   ifelse(le(W('left'), 0),
                          [S_('rdy', 0), C_('pts', W('cur')), S_('cur', 0), cast('k28_통과'), wait(0.9),
                           ifelse(ge(W('lv'), 3), [*m.end_blocks(score)], [C_('lv', 1), *start_level])],
                          [wait(0.05), cast('k28_장전'), wait(0.08), S_('fly', 0)])]))
    mgr.on(on_msg('시간끝'), S_('rdy', 0), *m.end_blocks(score))
    mgr.on(on_msg('게임종료'), S_('run', 0))
    pop_fx(m, '실패글', [('a', K.big_text('칼끼리 쨍! 다시!', 24, 'red'))], 0, -20, 'k28_실패글', 0.4)
    pop_fx(m, '통과글', [('a', K.big_text('통과!', 34, 'royal'))], 0, -20, 'k28_통과', 0.4)
    m.on_start(S_('th', 0), S_('lv', 1), S_('pts', 0), S_('cur', 0), S_('lives', LIVES), S_('fly', 0), S_('rdy', 0), S_('run', 1),
               S_('left', NK[0]), cast('k28_정보'))
    m.snd('k28_퍽', play('hit'))
    m.snd('k28_쨍', play('fail_big'))
    m.snd('k28_통과', play('good'))
    m.snd('k28_휙', play('jump'))
    m.finish('돌아가는 대나무 통에 칼을 모두 꽂으면 다음 단계!\n이미 꽂힌 칼에 부딪히면 ♥를 잃어요. (3단계)',
             '조작: SPACE 칼 던지기  ·  통은 빨라졌다 느려졌다, 거꾸로도 돌아요')
    return True


def ifelse_score(W):
    """3단계까지 다 깨면 남은 ♥ 하나에 4.5점."""
    return mul(mul(W('lives'), 3), div(sub(W('pts'), mod(W('pts'), 21)), 21))


# ================================================================== 29. 정확히 10초
@game(29)
def g29(P, ctx):
    R = 5
    TG = [5, 10, 7, 12, 10]
    PX, PY = 30, -10
    m = mg(P, ctx, T, 29, status='1/%d 라운드' % R, dim=60)
    vars_(P, *['k29_' + v for v in ('tg', 'st', 't0', 'el', 'e', 'pt', 'fill', 'ft', 'dist')])
    W = lambda n: V('k29_' + n)
    S_ = lambda n, v: setv('k29_' + n, v)
    P.list('k29_tg', TG)
    m.S('논', AC.paddy(), PX, PY)
    water = m.S('물', AC.paddy_water(), PX, PY, visible=False)
    water.on(on_msg('k29_라운드'), hide())
    water.on(on_msg('k29_열림'), water.pct(4), xy(PX - 99, PY), show(),
             until(ne(W('st'), 1),
                   S_('fill', div(sub(timer(), W('t0')), W('ft'))), if_(gt(W('fill'), 1), S_('fill', 1)),
                   water.pct(add(4, mul(W('fill'), 96))), lx(add(PX - 99, mul(W('fill'), 99))), wait(0.03)))
    m.S('모', AC.seedlings(), PX, PY)
    gate = m.S('물꼬', [('c', AC.water_gate(0)), ('o', AC.water_gate(1))], PX - 120, PY)
    gate.on(on_msg('k29_라운드'), shape('c'))
    gate.on(on_msg('k29_열림'), shape('o'))
    gate.on(on_msg('k29_닫힘'), shape('c'))
    fr = m.S('개구리', [('a', AC.frog(0)), ('b', AC.frog(1))], PX + 120, PY - 50)
    fr.on(on_msg('k29_열림'), until(ne(W('st'), 1), wait(div(rnd(60, 220), 100)),
                                   if_(and_(eq(W('st'), 1), ge(W('dist'), 1)), shape('b'), cast('k29_개굴'), wait(0.25), shape('a'))))
    bird = m.S('참새', AC.sparrow(), -300, 60, visible=False)
    bird.on(on_msg('k29_열림'), wait(div(rnd(100, 400), 100)),
            if_(and_(eq(W('st'), 1), ge(W('dist'), 2)), xy(-260, rnd(30, 80)), show(), glide(div(rnd(15, 30), 10), 260, rnd(20, 80)), hide()))
    tick = hidden(m, '가짜시계')
    tick.on(on_msg('k29_열림'), wait(0.4), until(ne(W('st'), 1), if_(ge(W('dist'), 3), cast('k29_똑딱')), wait(0.83)))
    tgt = m.T('목표글', '', PX, 74, 16, C_WHITE, F_BODY, True, 0, w=260, h=24)
    tgt.on(on_msg('k29_라운드'), write(join('목표: 딱 ', W('tg'), '초')))
    help_ = m.T('도움글', '', PX, -86, 11, C_ACC, F_BODY, True, 0, w=320, h=18)
    help_.on(on_msg('k29_라운드'), write('SPACE로 물꼬를 여세요'))
    help_.on(on_msg('k29_열림'), write('머릿속으로 세다가 SPACE로 닫기!'))
    help_.on(on_msg('k29_닫힘'), write(join('기록 ', div(rounded(mul(W('el'), 100)), 100), '초 · 오차 ',
                                           div(rounded(mul(W('e'), 100)), 100), '초')))
    rate = m.S('평가', [('a', K.big_text('완벽!', 34, 'royal')), ('b', K.big_text('훌륭해요', 28, 'white')),
                       ('c', K.big_text('아쉬워요', 26, 'gray')), ('d', K.big_text('너무 달라요', 24, 'red'))], PX, 30, visible=False)
    rate.on(on_msg('k29_닫힘'), shape(V('_mv')), rate.pct(130), show(), rep(5, rate.grow_pct(-6), wait(0.016)), wait(1.3), hide())
    keys = hidden(m, '물꼬키')
    keys.on(on_key(K_SPACE), if_(eq(V('게임중'), 1),
                                 ifelse(eq(W('st'), 0), [S_('t0', timer()), S_('st', 1), cast('k29_열림')],
                                        [if_(and_(eq(W('st'), 1), gt(sub(timer(), W('t0')), 0.5)), S_('el', sub(timer(), W('t0'))), S_('st', 2))])))
    mgr = hidden(m, '시간담당')
    mgr.on(on_msg('게임시작'), reset_timer(), start_timer(), setv('라운드', 1),
           until(gt(V('라운드'), R),
                 S_('tg', LGET('k29_tg', V('라운드'))), S_('dist', sub(V('라운드'), 1)), S_('st', 0), S_('el', 0),
                 S_('ft', mul(W('tg'), div(rnd(80, 130), 100))),
                 cast('k29_라운드'), setv('미니표시', join(V('라운드'), '/', R, ' 라운드 · ', rounded(V('합계')), '점')),
                 setv('_mt', timer()),
                 wait_until(or_(ne(W('st'), 0), gt(timer(), add(V('_mt'), 8)))),
                 if_(eq(W('st'), 1),
                     wait_until(or_(eq(W('st'), 2), gt(timer(), add(W('t0'), add(mul(W('tg'), 2), 2))))),
                     if_(eq(W('st'), 1), S_('el', sub(timer(), W('t0'))), S_('st', 2))),
                 ifelse(eq(W('st'), 2),
                        [S_('e', abs_(sub(W('el'), W('tg')))), S_('pt', sub(20, mul(W('e'), 16))), if_(lt(W('pt'), 0), S_('pt', 0)),
                         chg('합계', W('pt')),
                         ifelse(lt(W('e'), 0.2), [setv('_mv', 1)],
                                [ifelse(lt(W('e'), 0.6), [setv('_mv', 2)], [ifelse(lt(W('e'), 1.2), [setv('_mv', 3)], [setv('_mv', 4)])])]),
                         cast('k29_닫힘'), wait(2.2)],
                        [S_('st', 3)]),
                 chg('라운드', 1)),
           *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), S_('st', 0), S_('tg', TG[0]))
    m.snd('k29_열림', play('splash'))
    m.snd('k29_닫힘', play('stamp'))
    m.snd('k29_개굴', play('pop'))
    m.snd('k29_똑딱', play('tick'))
    m.finish('SPACE로 물꼬를 열고 머릿속으로 목표 시간을 센 뒤\n다시 SPACE로 닫으세요! 시계는 안 보여요 (5라운드)',
             '조작: SPACE 열기/닫기  ·  개구리·참새·가짜 똑딱 소리에 속지 마세요')
    return True


# ================================================================== 30. 씨름
@game(30)
def g30(P, ctx):
    TL = 50
    m = mg(P, ctx, T, 30, time_limit=TL, status='나 0 : 0 상대', dim=60)
    vars_(P, *['k30_' + v for v in ('bal', 'F', 'tf', 'win', 'lose', 'tip', 'st', 'dt', 'lt', 'f', 'nt', 'cool', 'rnd')])
    W = lambda n: V('k30_' + n)
    S_ = lambda n, v: setv('k30_' + n, v)
    C_ = lambda n, v: chg('k30_' + n, v)
    m.S('모래판', AC.sand_ring(), 0, -66)
    pair = m.S('장사', [('n', AC.wrestlers('n')), ('t', AC.wrestlers('t')), ('w', AC.wrestlers('w')), ('l', AC.wrestlers('l'))], 0, -18)
    pair.on(on_msg('k30_판시작'), shape('n'), rot(0), xy(0, -18))
    pair.on(on_msg('게임시작'), until(eq(V('게임중'), 0), if_(eq(W('st'), 1), rot(mul(W('bal'), 0.18)), lx(mul(W('bal'), 0.25)))))
    pair.on(on_msg('k30_기울'), shape('t'))
    pair.on(on_msg('k30_바로'), if_(eq(W('st'), 1), shape('n')))
    pair.on(on_msg('k30_이김'), rot(0), shape('w'))
    pair.on(on_msg('k30_짐'), rot(0), shape('l'))
    m.S('균형막대', AC.balance_bar(), 0, -112)
    knob = m.S('균형표시', AC.bar_knob(), 0, -100)
    knob.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(mul(W('bal'), 1.32))))
    m.S('내얼굴', ctx['PORT']['me'], -196, 70)
    m.S('상대얼굴', ctx['PORT']['p1'], 196, 70)
    m.S('나표', K.badge('나', 40, 16, 'royal'), -196, 46)
    m.S('상대표', K.badge('상대', 40, 16, 'red'), 196, 46)
    board = m.T('판수', '0 : 0', 0, 84, 18, C_WHITE, F_NUM, False, 0, w=120, h=24)
    board.on(on_msg('k30_점수'), write(join(W('win'), ' : ', W('lose'))))
    tipw = m.S('기울었다', K.big_text('기울었다! 지금!', 26, 'royal'), 60, 50, visible=False)
    tipw.on(on_msg('k30_기울'), tipw.pct(70), show(), rep(4, tipw.grow_pct(8), wait(0.016)))
    tipw.on(on_msg('k30_바로'), hide())
    keys = hidden(m, '씨름키')
    keys.on(on_key(K_SPACE), if_(and_(eq(W('st'), 1), eq(W('cool'), 0)), S_('cool', 1),
                                 ifelse(and_(eq(W('tip'), 1), lt(abs_(W('bal')), 55)),
                                        [S_('st', 2), cast('k30_바로'), cast('k30_이김'), C_('win', 1), setv('_mv', 1), cast('k30_판끝')],
                                        [cast('k30_헛기술'), ifelse(lt(W('bal'), 0), [C_('bal', -30)], [C_('bal', 30)]),
                                         S_('F', mul(W('F'), 1.6))]),
                                 wait(0.35), S_('cool', 0)))
    mgr = hidden(m, '씨름담당')
    sign_rnd = sub(mul(rnd(0, 1), 2), 1)
    mgr.on(on_msg('k30_판시작'), S_('bal', 0), S_('F', 0), S_('tip', 0), S_('nt', add(timer(), div(rnd(20, 32), 10))),
           S_('tf', add(timer(), 0.5)), S_('lt', timer()), S_('st', 1), cast('k30_점수'),
           until(ne(W('st'), 1),
                 S_('dt', sub(timer(), W('lt'))), S_('lt', timer()), *clamp('k30_dt', 0, 0.1), S_('f', mul(W('dt'), 60)),
                 if_(gt(timer(), W('tf')),
                     S_('F', mul(sign_rnd, div(rnd(50, add(100, mul(W('rnd'), 20))), 100))), S_('tf', add(timer(), div(rnd(4, 11), 10)))),
                 if_(key(K_LEFT), C_('bal', mul(W('f'), -1.7))), if_(key(K_RIGHT), C_('bal', mul(W('f'), 1.7))),
                 C_('bal', mul(add(W('F'), mul(W('bal'), 0.012)), W('f'))),
                 # 상대가 기우는 순간 (기술 기회)
                 if_(and_(eq(W('tip'), 0), gt(timer(), W('nt'))), S_('tip', 1), S_('nt', add(timer(), 0.75)), cast('k30_기울')),
                 if_(and_(eq(W('tip'), 1), gt(timer(), W('nt'))), S_('tip', 0), S_('nt', add(timer(), div(rnd(22, 38), 10))),
                     cast('k30_바로')),
                 if_(ge(abs_(W('bal')), 100), S_('st', 2), cast('k30_바로'), cast('k30_짐'), C_('lose', 1), setv('_mv', 2), cast('k30_판끝'))))
    final = ifelse_final(W)
    mgr.on(on_msg('k30_판끝'), cast('k30_점수'), setv('미니표시', join('나 ', W('win'), ' : ', W('lose'), ' 상대')), wait(1.6),
           ifelse(or_(ge(W('win'), 2), ge(W('lose'), 2)), [*m.end_blocks(final)], [C_('rnd', 1), cast('k30_판시작')]))
    mgr.on(on_msg('게임시작'), S_('rnd', 1), cast('k30_판시작'))
    mgr.on(on_msg('시간끝'), S_('st', 2), *m.end_blocks(final))
    pop_fx(m, '판결과', [('a', K.big_text('넘겼다! 한 판!', 30, 'royal')), ('b', K.big_text('넘어갔다...', 28, 'red'))],
           0, 30, 'k30_판끝', 0.7)
    pop_fx(m, '헛기술', [('a', K.big_text('헛기술!', 22, 'red'))], -60, 40, 'k30_헛기술', 0.2)
    m.on_start(S_('win', 0), S_('lose', 0), S_('st', 0), S_('bal', 0), S_('tip', 0), S_('cool', 0), cast('k30_점수'))
    m.snd('k30_기울', play('alarm'))
    m.snd('k30_헛기술', play('bad'))
    m.snd('k30_판끝', ifelse(eq(V('_mv'), 1), [play('fanfare')], [play('fail_big')]))
    m.finish('← → 로 균형을 가운데에 지키며 버티다가, 상대가\n"기울었다!" 할 때 SPACE로 넘기세요! (3판 2선승)',
             '조작: ← → 버티기 · SPACE 기술  ·  아무 때나 쓰면 헛기술로 흔들려요')
    return True


def ifelse_final(W):
    """2판을 먼저 이기면 100 - 진 판×20, 아니면 이긴 판×35 + 10."""
    won = div(sub(W('win'), mod(W('win'), 2)), 2)          # win>=2 이면 1 (win 은 0~2)
    return add(mul(won, sub(100, mul(W('lose'), 20))), mul(sub(1, won), add(mul(W('win'), 35), 10)))
