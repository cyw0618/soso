# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 21~30번."""
import random
from games_common import *
import mg_art3 as A3

T = 3
GAMES, game = registry()

import art3c as AC


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
