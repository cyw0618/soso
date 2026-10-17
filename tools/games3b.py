# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 11~20번."""
import random
from games_common import *
import mg_art3 as A3

T = 3
GAMES, game = registry()
import art3b as B3


def _bar(o, frac):
    """막대 모양(bar_set 41칸)을 비율 frac(0~1)에 맞춘다."""
    o.local('_bf', 1)
    return [setv('_bf', add(1, floor(mul(40, frac)))), if_(lt(V('_bf'), 1), setv('_bf', 1)), if_(gt(V('_bf'), 41), setv('_bf', 41)),
            shape(V('_bf'))]


def _pop(m, base, pics, x, y, msg, hold=0.35, pre=()):
    """신호를 받으면 커졌다 사라지는 글자 (pics: [(이름, 경로)] → pre 로 모양 고르기)."""
    return G.big_pop(m.P, m.sc, base, pics, x, y, msg, hold=hold, pre=pre)


# ================================================================== 11. 신호 깃발 판단 (스트룹)
@game(11)
def g11(P, ctx):
    TL = 30
    m = mg(P, ctx, T, 11, time_limit=TL, status='점수 0', dim=90)
    vars_(P, 'k11_글자', 'k11_색', 'k11_규칙', 'k11_답', 'k11_창', 'k11_t0', 'k11_n', 'k11_남은', 'k11_콤보', 'k11_얻음')
    # 규칙 띠 + 문제판
    rule = m.S('규칙띠', [('ink', K.badge('글자의 색깔 깃발을 드세요!', 230, 24, 'royal')),
                          ('word', K.badge('지금은 글자 뜻 깃발을 드세요!', 230, 24, 'red'))], 0, 80)
    rule.on(on_msg('k11_규칙'), shape(V('k11_규칙')), rule.pct(120), rep(4, rule.grow_pct(-5), wait(0.02)))
    card = m.S('문제판', [('ink', B3.k11_card(1)), ('word', B3.k11_card(2))], 0, 26)
    card.on(on_msg('k11_규칙'), shape(V('k11_규칙')))
    word = m.S('문제글자', [('w%d%d' % (w, k), B3.k11_word(w, k)) for w in range(1, 5) for k in range(1, 5)], 0, 28,
               visible=False)
    word.on(on_msg('k11_문제'), shape(add(mul(sub(V('k11_글자'), 1), 4), V('k11_색'))), word.pct(70), show(),
            rep(4, word.grow_pct(7.5), wait(0.016)))
    word.on(on_msg('k11_끝문제'), hide())
    # 남은 시간 막대 (문제마다)
    bars = K.bar_set('k11_t', 196, 8, 'royal')
    tb = m.S('시간막대', bars, 0, -12, visible=False)
    tb.on(on_msg('k11_문제'), show(),
          until(or_(eq(V('입력가능'), 0), eq(V('게임중'), 0)),
                *_bar(tb, sub(1, div(sub(timer(), V('k11_t0')), V('k11_창')))), wait(0.03)),
          hide())
    # 깃발 4개 (클릭 / 1~4 키)
    keys = [K_1, K_2, K_3, K_4]
    for k in range(1, 5):
        fl = m.S('깃발%d' % k, [('off', B3.k11_flag(k)), ('on', B3.k11_flag(k, True))], -132 + 88 * (k - 1), -76)
        pick = [if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)), setv('선택', k), setv('입력가능', 0), cast('k11_들기%d' % k))]
        fl.on(on_click(), *pick)
        fl.on(on_key(keys[k - 1]), *pick)
        fl.on(on_msg('k11_들기%d' % k), shape('on'), fl.pct(112), mvy(10), wait(0.18), mvy(-10), fl.pct(100), shape('off'))
    # 판정 글자
    judge = m.S('판정', [('ok', K.big_text('정답!', 26, 'green')), ('no', K.big_text('땡!', 28, 'red')),
                       ('late', K.big_text('늦었어요!', 24, 'gray'))], 0, 26, visible=False)
    judge.on(on_msg('k11_판정'), shape(V('k11_얻음')), to_front(), judge.pct(60), show(),
             rep(4, judge.grow_pct(12), wait(0.016)), wait(0.22), hide())
    combo = m.T('콤보', '', 0, -30, 11, C_ACC, F_NUM, False, 0, w=200, h=16)
    combo.on(on_msg('k11_판정'), ifelse(ge(V('k11_콤보'), 3), [write(join(V('k11_콤보'), '연속 정답!'))], [write('')]))
    _pop(m, '규칙변경', K.big_text('규칙 변경!', 34, 'red'), 0, 26, 'k11_변경', hold=0.55)
    # 진행
    mgr = hidden(m, '신호담당')
    win = V('k11_창')
    mgr.on(on_msg('게임시작'), setv('k11_규칙', 1), cast('k11_규칙'), setv('k11_남은', rnd(5, 7)), setv('k11_n', 0),
           until(eq(V('게임중'), 0),
                 chg('k11_n', 1),
                 if_(le(V('k11_남은'), 0),
                     setv('k11_규칙', sub(3, V('k11_규칙'))), cast('k11_규칙'), cast('k11_변경'), wait(1.0),
                     ifelse(eq(V('k11_규칙'), 2), [setv('k11_남은', rnd(3, 5))], [setv('k11_남은', rnd(5, 7))])),
                 chg('k11_남은', -1),
                 setv('k11_글자', rnd(1, 4)), setv('k11_색', rnd(1, 4)),
                 if_(le(rnd(1, 100), 85), until(ne(V('k11_색'), V('k11_글자')), setv('k11_색', rnd(1, 4)))),
                 ifelse(eq(V('k11_규칙'), 1), [setv('k11_답', V('k11_색'))], [setv('k11_답', V('k11_글자'))]),
                 setv('k11_창', sub(2.6, mul(V('k11_n'), 0.05))), if_(lt(win, 1.25), setv('k11_창', 1.25)),
                 setv('선택', 0), setv('k11_t0', timer()), setv('입력가능', 1), cast('k11_문제'),
                 wait_until(or_(eq(V('입력가능'), 0), gt(timer(), add(V('k11_t0'), win)), eq(V('게임중'), 0))),
                 setv('입력가능', 0),
                 if_(eq(V('게임중'), 1),
                     ifelse(eq(V('선택'), V('k11_답')),
                            [chg('맞춤', 1), chg('k11_콤보', 1), setv('k11_얻음', 1),
                             chg('합계', add(2.2, mul(1.8, sub(1, div(sub(timer(), V('k11_t0')), win))))),
                             if_(ge(V('k11_콤보'), 5), chg('합계', 0.4))],
                            [setv('k11_콤보', 0),
                             ifelse(eq(V('선택'), 0), [setv('k11_얻음', 3)], [setv('k11_얻음', 2), chg('틀림', 1), chg('합계', -1.5)])]),
                     if_(lt(V('합계'), 0), setv('합계', 0)),
                     cast('k11_끝문제'), cast('k11_판정'),
                     setv('미니표시', join('점수 ', rounded(V('합계')))),
                     wait(0.4))))
    mgr.on(on_msg('시간끝'), setv('입력가능', 0), *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('틀림', 0), setv('입력가능', 0), setv('k11_콤보', 0),
               setv('k11_규칙', 1), setv('선택', 0))
    m.snd('k11_판정', ifelse(eq(V('k11_얻음'), 1), [play('coin')], [play('bad')]))
    m.snd('k11_변경', play('whistle'))
    m.snd('k11_문제', play('tick'))
    m.finish('글자의 뜻 말고 글자 색깔과 같은 깃발을 빨리 드세요!\n빨간 테로 "규칙 변경!"이 뜨면 그땐 글자 뜻대로!',
             '조작: 깃발 클릭 또는 숫자키 1 빨강 · 2 파랑 · 3 노랑 · 4 초록')
    return True
