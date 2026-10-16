# -*- coding: utf-8 -*-
"""작전 본부 '회의실': 해외 투자자와 협상해서 자본을 투자받는다.

투자금은 바로 들어오지만, 유세 6번 뒤에 원금 + 약속한 수익률만큼 갚아야 한다 (총자산에서는 빚으로 빠짐).
투자자마다 속으로 정한 '최소 수익률'이 있고, 그보다 낮게 부르면 거절. 인내심이 바닥나면 협상 결렬.
"""
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, fmt_money, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX

# (이름, 나라, 투자금 3단계(만원), 기본 최소 수익률 %, 인내심, 좋아하는 것)
INVESTORS = [
    ('이글 캐피털', '미국', [50000, 100000, 200000], 20, 4, '계열사'),
    ('하나비 상사', '일본', [30000, 60000, 120000], 13, 3, '지지율'),
    ('오아시스 펀드', '중동', [100000, 200000, 400000], 17, 2, '지배 자본'),
]
DUE = 6
LIKE_TEXT = {'계열사': '계열사가 많은 회사를 좋아함', '지지율': '지지율이 높은 후보를 좋아함', '지배 자본': '지배 자본 지분을 중요하게 봄'}

INVEST_VARS = dict(투자자=0, 투자단계=0, 투자액=0, 제시율=10, 최소율=0, 투자인내=0, 투자전략=0, 투자글='', 투자결과=0)


def setup(P):
    P.list('투자자이름', [i[0] for i in INVESTORS])
    P.list('투자금액', [a for i in INVESTORS for a in i[2]])
    P.list('투자부채', [0, 0, 0])
    P.list('투자만기', [0, 0, 0])
    P.list('투자결렬', [0, 0, 0])


def reset_blocks():
    return [lst_set(nm, k, 0) for nm in ('투자부채', '투자만기', '투자결렬') for k in (1, 2, 3)] + scale_blocks()


def scale_blocks():
    """투자 금액을 지금 단계 규모로 (시장 선거 ×50, 대선 ×1000)."""
    amts = [a for i in INVESTORS for a in i[2]]
    return [lst_set('투자금액', k, mul(a, LGET('상점배율', V('단계')))) for k, a in enumerate(amts, 1)]


def debt_total():
    return add(add(LGET('투자부채', 1), LGET('투자부채', 2)), LGET('투자부채', 3))


def overnight_blocks(liquidate):
    """유세 결과 때: 만기가 된 투자금 갚기, 결렬 대기 줄이기."""
    b = []
    for k in (1, 2, 3):
        b.append(if_(and_(gt(LGET('투자부채', k), 0), ge(V('유세횟수'), LGET('투자만기', k))),
                     chg('돈', mul(LGET('투자부채', k), -1)), lst_set('투자부채', k, 0), lst_set('투자만기', k, 0),
                     setv('계열사소식', join(LGET('투자자이름', k), '에 투자금과 약속한 수익을 갚았다'))))
        b.append(if_(gt(LGET('투자결렬', k), 0), lst_set('투자결렬', k, sub(LGET('투자결렬', k), 1))))
    b.append(if_(lt(V('돈'), 0), *liquidate))
    return b


def build(P, ctx):
    sc = ctx['S_INVEST']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '회의제목', K.banner('회의실 · 해외 투자자', 168, 30, 'royal'), -4, 116)
    info = text(P, sc, '회의안내', '투자금은 바로 들어오지만 유세 %d번 뒤 원금 + 수익을 갚아야 해요' % DUE,
                -40, 94, 8, C_DIM, F_BODY, True, 0, w=250, h=13)
    # ---- 1단계: 투자자 고르기
    cards = []
    for k, (nm, ctry, amts, base, pat, like) in enumerate(INVESTORS, 1):
        x = -150 + (k - 1) * 150
        c = panel(P, sc, '투자자카드%d' % k, x, 20, 140, 120, 'card')
        G.hover_scripts(c, 104)
        t1 = text(P, sc, '투자자이름%d' % k, '%s (%s)' % (nm, ctry), x, 64, 11, C_WHITE, F_NUM, False, 0, w=130, h=16)
        t2 = text(P, sc, '투자자성향%d' % k, LIKE_TEXT[like], x, 36, 8, C_DIM, F_BODY, True, 0, w=126, h=24)
        t3 = text(P, sc, '투자자금액%d' % k, '', x, 8, 9, C_ACC, F_NUM, False, 0, w=126, h=26)
        t3.on(on_scene(), *fmt_money(amts[0], '_m'), setv('투자글', V('_m')), *fmt_money(amts[2], '_m'),
              write(join(V('투자글'), ' ~\n', V('_m'))), setv('투자글', ''))
        t4 = text(P, sc, '투자자상태%d' % k, '', x, -26, 9, C_WHITE, F_NUM, False, 0, w=126, h=24)
        t4.on(on_msg('회의갱신'),
              ifelse(gt(LGET('투자부채', k), 0), [write(join('계약 중\n유세 ', sub(LGET('투자만기', k), V('유세횟수')), '번 뒤 상환')),
                                                  text_color(C_ACC)],
                     [ifelse(gt(LGET('투자결렬', k), 0), [write(join('협상 결렬\n유세 ', LGET('투자결렬', k), '번 뒤 다시')), text_color(C_RED)],
                             [write('회의 가능\n(눌러서 시작)'), text_color(C_WHITE)])]))
        pick = [if_(and_(eq(V('투자단계'), 0), and_(eq(LGET('투자부채', k), 0), eq(LGET('투자결렬', k), 0))),
                    setv('투자자', k), setv('투자단계', 1), setv('투자인내', pat), setv('투자전략', 0), setv('제시율', 10),
                    setv('투자액', LGET('투자금액', (k - 1) * 3 + 1)), setv('_mk', 1), cast('최소율계산'),
                    setv('투자글', '얼마를, 몇 % 수익을 약속하고 받을지 정하세요.'), cast('회의갱신'))]
        for o in (c, t1, t2, t3, t4):
            o.on(on_click(), *pick)
            o.on(on_msg('회의갱신'), ifelse(eq(V('투자단계'), 0), [show()], [hide()]))
        cards += [c, t1, t2, t3, t4]
    # ---- 2단계: 협상
    neg = []
    neg.append(panel(P, sc, '협상판', 0, 10, 440, 150, 'glass', header='royal'))
    tn = text(P, sc, '협상상대', '', 0, 72, 12, C_WHITE, F_NUM, False, 0, w=400, h=18)
    tn.on(on_msg('회의갱신'), if_(gt(V('투자자'), 0), write(join(LGET('투자자이름', V('투자자')), '와(과) 회의 중  ·  인내심 ', V('투자인내')))))
    neg.append(tn)
    neg.append(text(P, sc, '금액제목', '투자금', -150, 46, 10, C_DIM, F_NUM, False, 0, w=80, h=14))
    for j in (1, 2, 3):
        idx = add(mul(sub(V('투자자'), 1), 3), j)
        b = sprite(P, sc, '금액버튼%d' % j, [('off', K.button('금액 %d' % j, 72, 24, 'navy')), ('on', K.button('금액 %d' % j, 72, 24, 'royal'))],
                   -182 + (j - 1) * 76, 24)
        b.on(on_msg('회의갱신'), if_(gt(V('투자자'), 0), ifelse(eq(V('투자액'), LGET('투자금액', idx)), [shape('on')], [shape('off')])))
        b.on(on_click(), if_(eq(V('투자단계'), 1), setv('투자액', LGET('투자금액', idx)), setv('_mk', j), cast('최소율계산'),
                             cast('회의갱신'), G.sfx('click')))
        neg.append(b)
    ta = text(P, sc, '금액표시', '', -116, 2, 11, C_ACC, F_NUM, False, 0, w=200, h=16)
    ta.on(on_msg('회의갱신'), *fmt_money(V('투자액'), '_m'), write(join('받을 돈 ', V('_m'))))
    neg.append(ta)
    neg.append(text(P, sc, '수익률제목', '약속할 수익률', 110, 46, 10, C_DIM, F_NUM, False, 0, w=120, h=14))
    tr = text(P, sc, '수익률표시', '', 110, 24, 18, C_WHITE, F_NUM, False, 0, w=80, h=24)
    tr.on(on_msg('회의갱신'), write(join(V('제시율'), '%')))
    neg.append(tr)
    for lbl, dx, d in (('-2%', -62, -2), ('+2%', 62, 2)):
        neg.append(button(P, sc, '수익률' + lbl, lbl, 110 + dx, 24, 44, 22, 'blue',
                          actions=[if_(eq(V('투자단계'), 1), chg('제시율', d), if_(lt(V('제시율'), 2), setv('제시율', 2)),
                                       if_(gt(V('제시율'), 60), setv('제시율', 60)), cast('회의갱신'))]))
    tp = text(P, sc, '갚을돈', '', 110, 2, 9, C_DIM, F_NUM, False, 0, w=200, h=14)
    tp.on(on_msg('회의갱신'), *fmt_money(mul(V('투자액'), add(1, div(V('제시율'), 100))), '_m'), write(join('나중에 갚을 돈 ', V('_m'))))
    neg.append(tp)
    msg = text(P, sc, '투자말', '', 0, -22, 10, C_WHITE, F_BODY, True, 0, w=400, h=28)
    msg.on(on_msg('회의갱신'), write(V('투자글')))
    neg.append(msg)
    # 전략 (회의마다 한 번)
    def tactic(chance, cut, fail_end, ok_msg, ng_msg):
        return [if_(and_(eq(V('투자단계'), 1), eq(V('투자전략'), 0)),
                    setv('투자전략', 1),
                    ifelse(le(rnd(1, 100), chance), [chg('최소율', -cut), setv('투자글', ok_msg), G.sfx('good')],
                           [setv('투자단계', 2), setv('투자결과', 2), setv('투자글', ng_msg), G.sfx('bad')] if fail_end else
                           [chg('투자인내', -1), setv('투자글', ng_msg), G.sfx('bad')]),
                    if_(le(V('투자인내'), 0), setv('투자단계', 2), setv('투자결과', 2)),
                    cast('회의갱신'), cast('회의끝검사'))]
    neg.append(button(P, sc, '전략비전', '조치원 비전 발표', -150, -56, 120, 24, 'purple', icon='star',
                      actions=tactic(65, 4, False, '발표가 먹혔다! 투자자의 눈빛이 달라졌다.', '발표가 지루했나 보다... 인내심 -1')))
    neg.append(button(P, sc, '전략경쟁', '다른 투자자도 있다', -20, -56, 124, 24, 'red', icon='bolt',
                      actions=tactic(35, 9, True, '"다른 데도 있다고요?" 조건이 확 좋아졌다!', '"그럼 거기랑 하시죠." 협상 결렬!')))
    offer = [if_(eq(V('투자단계'), 1),
                 ifelse(ge(V('제시율'), V('최소율')),
                        [chg('돈', V('투자액')), lst_set('투자부채', V('투자자'), rounded(mul(V('투자액'), add(1, div(V('제시율'), 100))))),
                         lst_set('투자만기', V('투자자'), add(V('유세횟수'), DUE)), setv('투자단계', 2), setv('투자결과', 1),
                         setv('투자글', '계약 성사! 투자금이 들어왔다.'), G.sfx('cash')],
                        [chg('투자인내', -1),
                         ifelse(le(sub(V('최소율'), V('제시율')), 4), [setv('투자글', '"조금만 더 쓰시죠." (거의 다 왔다)')],
                                [setv('투자글', '"장난하십니까?" (한참 모자라다)')]),
                         G.sfx('bad'),
                         if_(le(V('투자인내'), 0), setv('투자단계', 2), setv('투자결과', 2), setv('투자글', '인내심이 바닥났다. 협상 결렬!'))]),
                 cast('회의갱신'), cast('회의끝검사'))]
    neg.append(button(P, sc, '제안하기', '제안하기', 110, -56, 100, 26, 'royal', icon='coin', actions=offer))
    for o in neg:
        o.on(on_scene(), hide())
        o.on(on_msg('회의갱신'), ifelse(ge(V('투자단계'), 1), [show()], [hide()]))
    endc = text(P, sc, '회의결과', '', 0, -88, 12, C_ACC, F_NUM, False, 0, w=400, h=18, visible=False)
    endc.on(on_msg('회의갱신'), ifelse(eq(V('투자단계'), 2), [ifelse(eq(V('투자결과'), 1), [write('계약 성사!'), text_color(C_ACC)],
                                                                  [write('협상 결렬... 유세 3번 동안 만날 수 없어요'), text_color(C_RED)]), show()],
                                   [hide()]))
    mgr = text(P, sc, '회의담당', '', -300, -300, 8, visible=False)
    # 투자자가 속으로 정한 최소 수익률: 금액이 클수록, 내가 약할수록 높다. 좋아하는 것을 갖췄으면 낮아진다.
    likes = [mul(V('계열사수'), 1.3), mul(sub(V('내지지율'), 12), 0.25), mul(div(LGET('보유', 16), 1000), 0.3)]
    mgr.on(on_msg('최소율계산'),
           setv('최소율', add(add(LGET('_기본율', V('투자자')), mul(sub(V('_mk'), 1), 5)), rnd(0, 6))),
           chg('최소율', mul(sub(40, V('내지지율')), 0.12)),
           *[if_(eq(V('투자자'), k), chg('최소율', mul(likes[k - 1], -1))) for k in (1, 2, 3)],
           if_(lt(V('최소율'), 4), setv('최소율', 4)), setv('최소율', rounded(V('최소율'))))
    mgr.on(on_msg('회의끝검사'), if_(eq(V('투자단계'), 2), if_(eq(V('투자결과'), 2), lst_set('투자결렬', V('투자자'), 3)),
                                   wait(1.8), setv('투자단계', 0), cast('회의갱신')))
    mgr.on(on_scene(), setv('투자단계', 0), setv('투자글', ''), cast('회의갱신'))
    P.list('_기본율', [i[3] for i in INVESTORS])
    button(P, sc, '작전본부로', '작전 본부로', -180, -118, 100, 24, 'navy', icon='back',
           actions=[if_(ne(V('투자단계'), 1), *go(ctx['S_SHOP']))])
    button(P, sc, '회의그만', '회의 그만두기', 180, -118, 104, 24, 'gray',
           actions=[if_(eq(V('투자단계'), 1), setv('투자단계', 0), cast('회의갱신'))])
    debt = text(P, sc, '빚표시', '', 0, -118, 9, C_WHITE, F_NUM, False, 0, w=200, h=14)
    debt.on(on_scene(), forever(*fmt_money(debt_total(), '_m'), write(join('갚을 투자금 합계 ', V('_m'))), wait(0.3)))
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])
