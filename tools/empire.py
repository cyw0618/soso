# -*- coding: utf-8 -*-
"""조치원 계열사 15개 쟁탈전 + 큰아버지와의 지배 자본 협상 테이블.

- 계열사: 인수하면 유세 1번마다 돈을 벌어 오고, 많을수록 최종 점수가 높다. 큰아버지들도 주인 없는 회사를 사들이고
  내 회사를 빼앗으려 한다. 큰아버지 회사는 '적대적 인수'로 빼앗을 수 있다(비싸고 실패할 수 있음).
- 협상 테이블: 큰아버지에게서 지배 자본 지분(1/3/5%)을 사 온다. 큰아버지가 속으로 정한 최소 웃돈은 숨겨져 있고,
  인내심이 바닥나면 협상이 깨진다. 유세 1번마다 한 번만 협상할 수 있다. 가장 어렵다.
"""
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, fmt_comma, fmt_money, fmt_price, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
import data as D

NA = len(D.AFFILIATES)
CTL = len(D.STOCKS) + 1

EMPIRE_VARS = dict(계열사수=0, 계열사수입=0, 첫째계열사=0, 둘째계열사=0, 선택회사=1, 회사알림='', 계열사소식='', 지배알림=0,
                   협상기회=1, 협상금지턴=0, 협상상대=2, 협상단계=1, 협상량=1000, 최소배율=2, 제시율=40, 인내심=3,
                   협상말='', 전술사용=0, 협상결과=0, _e=0, _t=0, _u=0, _w=0)


def setup(P):
    P.list('계열사이름', [a[0] for a in D.AFFILIATES])
    P.list('계열사가격', [a[1] for a in D.AFFILIATES])
    P.list('계열사수익', [a[2] for a in D.AFFILIATES])
    P.list('계열사주인', [a[3] for a in D.AFFILIATES])
    P.list('주인이름', ['나', '첫째', '둘째'])
    P.list('가능성말', ['낮음', '보통', '높음', '매우 높음'])


def stake_pct(expr=None):
    """내 지배 자본 지분 % (소수 첫째 자리)."""
    return round1(div(LGET('보유', CTL) if expr is None else expr, D.CONTROL_SHARES / 100.0))


def stats_blocks():
    b = [setv('계열사수', 0), setv('계열사수입', 0), setv('첫째계열사', 0), setv('둘째계열사', 0)]
    for i in range(1, NA + 1):
        o = LGET('계열사주인', i)
        b += [if_(eq(o, 1), chg('계열사수', 1), chg('계열사수입', LGET('계열사수익', i))),
              if_(eq(o, 2), chg('첫째계열사', 1)), if_(eq(o, 3), chg('둘째계열사', 1))]
    return b


def reset_blocks():
    return [lst_set('계열사주인', i, D.AFFILIATES[i - 1][3]) for i in range(1, NA + 1)] + stats_blocks()


def overnight_blocks():
    """유세 1번이 끝날 때: 계열사 수익, 큰아버지들의 계열사 매수/탈취, 협상 기회 회복."""
    return [
        *stats_blocks(),
        chg('돈', V('계열사수입')),
        setv('계열사소식', ''),
        # 큰아버지가 주인 없는 회사를 산다 (45%)
        setv('_e', rnd(1, NA)),
        if_(and_(eq(LGET('계열사주인', V('_e')), 0), le(rnd(1, 100), 45)),
            setv('_u', rnd(2, 3)), lst_set('계열사주인', V('_e'), V('_u')),
            setv('계열사소식', join(ifelse_name(V('_u')), ' 큰아버지가 ', LGET('계열사이름', V('_e')), ' 인수'))),
        # 큰아버지가 내 회사를 빼앗으려 한다 (18%, 정보 차단 중이면 못 함)
        setv('_e', rnd(1, NA)),
        if_(and_(and_(eq(LGET('계열사주인', V('_e')), 1), le(rnd(1, 100), 18)), eq(V('이번차단'), 0)),
            setv('_u', rnd(2, 3)), lst_set('계열사주인', V('_e'), V('_u')),
            setv('계열사소식', join(ifelse_name(V('_u')), ' 큰아버지가 내 ', LGET('계열사이름', V('_e')), '를 빼앗아 갔다!'))),
        *stats_blocks(),
        setv('협상기회', 1),
        if_(gt(V('협상금지턴'), 0), chg('협상금지턴', -1)),
    ]


def ifelse_name(u):
    """2 → '첫째', 3 → '둘째'."""
    return LGET('주인이름', u)


def overnight_object(P, sc):
    o = text(P, sc, '계열사정산', '', -300, -300, 8, visible=False)
    o.on(on_msg('주가변동'), *overnight_blocks())
    return o


# ------------------------------------------------------------------ 지배 자본 과반 알림 (여러 장면에서 사용)
def majority_check():
    return [if_(and_(gt(LGET('보유', CTL), D.CONTROL_GOAL), eq(V('지배알림'), 0)), setv('지배알림', 1), cast('지배과반'))]


def majority_pop(P, sc):
    G.big_pop(P, sc, '과반팝', K.big_text('지배 자본 과반 확보!', 30, 'royal'), 0, 30, '지배과반', hold=1.4)
    t = text(P, sc, '과반안내', '이제 지지율도 50%를 넘겨야 군수 자리에 앉아요!', 0, -2, 11, C_WHITE, F_BODY, True, 0, w=360, h=18,
             visible=False, bg=C_BOX)
    t.on(on_msg('지배과반'), to_front(), show(), wait(2.6), hide())


# ================================================================== 계열사 쟁탈전 장면
OWN_PICS = None


def _owner_card_pics():
    import stock_art as SA
    from PIL import Image, ImageDraw, ImageFilter
    from art_common import ensure_out, save
    import os
    out = []
    for key, top, bot, rim in (('none', (26, 30, 46), (8, 10, 18), (90, 100, 130)),
                               ('me', (30, 60, 170), (6, 14, 60), (120, 160, 255)),
                               ('u1', (120, 20, 40), (40, 4, 12), (240, 90, 110)),
                               ('u2', (80, 40, 160), (24, 8, 60), (170, 130, 255))):
        p = os.path.join(ensure_out(), 'aff_card_%s.png' % key)
        if not os.path.exists(p):
            s = 6
            w, h = 86 * s, 52 * s
            im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            m = Image.new('L', (w, h), 0)
            ImageDraw.Draw(m).rounded_rectangle((2 * s, 2 * s, w - 2 * s, h - 2 * s), 7 * s, fill=240)
            g = K._grad((w, h), top, bot)
            g.putalpha(m)
            im.alpha_composite(g)
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((2 * s, 2 * s, w - 2 * s, h - 2 * s), 7 * s, outline=rim + (255,), width=int(1.2 * s))
            d.rectangle((2 * s + 4, 2 * s + 6 * s, 5 * s, h - 8 * s), fill=rim + (255,))
            im = im.resize((86 * 2, 52 * 2), Image.LANCZOS)
            im.save(p)
        out.append((key, p))
    return out


def build_group(P, ctx):
    sc = ctx['S_GROUP']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('조치원 계열사 쟁탈전', 180, 30, 'royal'), -14, 117)
    sumt = text(P, sc, '계열사요약', '', -64, 89, 9, C_WHITE, F_NUM, False, 0, w=290, h=14)
    sumt.on(on_msg('계열사갱신'),
            *fmt_money(V('계열사수입'), '_m'),
            write(join('나 ', V('계열사수'), '개 · 첫째 ', V('첫째계열사'), '개 · 둘째 ', V('둘째계열사'), '개 | 유세마다 +', V('_m'))))
    pics = _owner_card_pics()
    for i in range(1, NA + 1):
        c, r = (i - 1) % 5, (i - 1) // 5
        x, y = -176 + c * 88, 54 - r * 56
        card = sprite(P, sc, '회사카드%d' % i, pics, x, y)
        nm = text(P, sc, '회사이름%d' % i, D.AFFILIATES[i - 1][0], x + 2, y + 13, 8, C_WHITE, F_NUM, False, 0, w=80, h=12)
        inc = text(P, sc, '회사수익%d' % i, '', x + 2, y - 1, 7, C_DIM, F_BODY, True, 0, w=80, h=11)
        own = text(P, sc, '회사주인%d' % i, '', x + 2, y - 14, 8, C_WHITE, F_NUM, False, 0, w=80, h=12)
        o = LGET('계열사주인', i)
        card.on(on_msg('계열사갱신'),
                ifelse(eq(o, 0), [shape('none')], [ifelse(eq(o, 1), [shape('me')], [ifelse(eq(o, 2), [shape('u1')], [shape('u2')])])]),
                ifelse(eq(V('선택회사'), i), [card.pct(108)], [card.pct(100)]))
        inc.on(on_scene(), *fmt_money(LGET('계열사수익', i), '_m'), write(join('수익 +', V('_m'))))
        own.on(on_msg('계열사갱신'),
               ifelse(eq(o, 0), [write('주인 없음'), text_color(C_DIM)],
                      [ifelse(eq(o, 1), [write('내 회사'), text_color(C_ACC)],
                              [ifelse(eq(o, 2), [write('첫째 큰아버지'), text_color(C_RED)], [write('둘째 큰아버지'), text_color(C_VIOLET)])])]))
        sel = [setv('선택회사', i), cast('계열사갱신')]
        for ob in (card, nm, inc, own):
            ob.on(on_click(), *sel)
    # 아래: 선택 회사 정보와 행동
    panel(P, sc, '행동판', 34, -112, 340, 34, 'glass')
    info = text(P, sc, '선택정보', '', -26, -112, 9, C_WHITE, F_BODY, True, 1, w=210, h=26)
    s = V('선택회사')
    price = LGET('계열사가격', s)
    owner = LGET('계열사주인', s)
    info.on(on_msg('계열사갱신'),
            ifelse(eq(owner, 0), [*fmt_money(price, '_m'), write(join(LGET('계열사이름', s), '\n인수가 ', V('_m'), ' (주인 없음)'))],
                   [ifelse(eq(owner, 1), [*fmt_money(mul(price, D.SELL_MULT), '_m'),
                                          write(join(LGET('계열사이름', s), '\n내 회사 · 팔면 ', V('_m')))],
                           [*fmt_money(mul(price, D.TAKEOVER_MULT), '_m'),
                            *chance_blocks(),
                            write(join(LGET('계열사이름', s), '\n적대적 인수 ', V('_m'), ' · 성공 가능성 ',
                                       LGET('가능성말', add(floor(div(V('_w'), 25)), 1))))])]))
    for lbl, col, cond in (('인수하기', 'royal', eq(owner, 0)), ('매각하기', 'gray', eq(owner, 1)), ('빼앗기', 'red', gt(owner, 1))):
        bt = button(P, sc, '행동' + lbl, lbl, 168, -112, 84, 24, col, icon='star', actions=[cast('계열사행동')])
        bt.on(on_msg('계열사갱신'), ifelse(cond, [show()], [hide()]))
    note = text(P, sc, '회사알림', '', 0, -88, 10, C_WHITE, F_NUM, False, 0, w=380, h=16, visible=False, bg=C_BOX)
    note.on(on_msg('회사알림'), write(V('회사알림')), to_front(), show(), wait(2.2), hide())
    mgr = text(P, sc, '계열사담당', '', -300, -300, 8, visible=False)
    cost_buy = price
    cost_take = mul(price, D.TAKEOVER_MULT)
    mgr.on(on_msg('계열사행동'),
           ifelse(eq(owner, 0),
                  [ifelse(ge(V('돈'), cost_buy),
                          [chg('돈', mul(cost_buy, -1)), lst_set('계열사주인', s, 1),
                           setv('회사알림', join(LGET('계열사이름', s), ' 인수 완료! 이제 유세마다 돈을 벌어 와요')), G.sfx('cash')],
                          [setv('회사알림', '돈이 부족해요!'), G.sfx('bad')])],
                  [ifelse(eq(owner, 1),
                          [chg('돈', mul(price, D.SELL_MULT)), lst_set('계열사주인', s, 0),
                           setv('회사알림', join(LGET('계열사이름', s), ' 매각 완료')), G.sfx('coin')],
                          [ifelse(ge(V('돈'), cost_take),
                                  [chg('돈', mul(cost_take, -1)), *chance_blocks(),
                                   ifelse(le(rnd(1, 100), V('_w')),
                                          [lst_set('계열사주인', s, 1),
                                           setv('회사알림', join('적대적 인수 성공! ', LGET('계열사이름', s), '는 이제 내 회사!')),
                                           G.sfx('fanfare')],
                                          [chg('돈', mul(cost_take, 0.6)),
                                           setv('회사알림', '인수 실패... 큰아버지가 막아냈다 (수수료 40% 손해)'), G.sfx('bad')])],
                                  [setv('회사알림', '돈이 부족해요!'), G.sfx('bad')])])]),
           *stats_blocks(), cast('회사알림'), cast('계열사갱신'))
    mgr.on(on_scene(), *stats_blocks(), cast('계열사갱신'))
    button(P, sc, '지도로', '지도로', -204, -112, 60, 22, 'navy', icon='back', actions=go(ctx['S_MAP']))
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])


def chance_blocks():
    """적대적 인수 성공 확률(%) → _w: 35 + (내 지분 - 상대 지분)×0.8 + (내 지지율 - 상대 지지율)×0.8, 10~80."""
    s = V('선택회사')
    return [ifelse(eq(LGET('계열사주인', s), 2), [setv('_t', div(V('첫째주'), 1000)), setv('_u', V('큰A'))],
                   [setv('_t', div(V('둘째주'), 1000)), setv('_u', V('큰B'))]),
            setv('_w', add(add(35, mul(sub(stake_pct(), V('_t')), 0.8)), mul(sub(V('내지지율'), V('_u')), 0.8))),
            if_(lt(V('_w'), 10), setv('_w', 10)), if_(gt(V('_w'), 80), setv('_w', 80))]


# ================================================================== 협상 테이블 (지배 자본 지분 거래)
def build_nego(P, ctx):
    import mg_art as A
    sc = ctx['S_NEGO']
    P.list('협상인사', ['', '막내가 내 지분을 달라고? 간도 크군.\n얼마나 얹어 줄 건데?', '흐흐, 거래라...\n값만 맞으면 뭐든 팔지.'])
    P.list('인내표시', ['○○○', '●○○', '●●○', '●●●'])
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('협상 테이블', 160, 30, 'red'), 0, 117)
    me = sprite(P, sc, '나', ctx['BUST']['me'], -176, 0, scale=0.5)
    un = sprite(P, sc, '큰아버지', [('u1', ctx['BUST']['u1']), ('u2', ctx['BUST']['u2'])], 176, 0, scale=0.5)
    un.on(on_msg('협상단계'), ifelse(eq(V('협상상대'), 2), [shape('u1')], [shape('u2')]))
    un.on(on_msg('협상말'), rep(3, mvx(3), wait(0.03), mvx(-3), wait(0.03)))
    sprite(P, sc, '탁자', A.table_top(330, 46), 0, -56)
    panel(P, sc, '말판', 30, 54, 270, 50, 'card')
    say_t = text(P, sc, '협상말', '', 30, 54, 10, C_WHITE, F_BODY, True, 0, w=250, h=42)
    say_t.on(on_msg('협상말'), write(V('협상말')))
    st = text(P, sc, '협상상태', '', 0, 20, 9, C_ACC, F_BODY, True, 0, w=320, h=26)
    st.on(on_scene(), forever(
        ifelse(ge(V('협상단계'), 3),
               [*fmt_comma(V('협상량'), '_q'),
                *fmt_price(LGET('주가', CTL), '_pt'),
                write(join('거래 ', div(V('협상량'), 1000), '% (', V('_q'), '주) · 시가 ', V('_pt'), '/주\n인내심 ',
                           LGET('인내표시', add(V('인내심'), 1))))],
               [write(join('내 지분 ', stake_pct(), '%  ·  첫째 ', div(V('첫째주'), 1000), '%  ·  둘째 ', div(V('둘째주'), 1000), '%'))]),
        wait(0.15)))

    def phase_show(o, *phases):
        cond = None
        for ph in phases:
            c = eq(V('협상단계'), ph)
            cond = c if cond is None else or_(cond, c)
        o.on(on_msg('협상단계'), ifelse(cond, [show()], [hide()]))
        return o

    def say(txt):
        return [setv('협상말', txt), cast('협상말')]

    goto_phase = lambda ph: [setv('협상단계', ph), cast('협상단계')]
    # 1단계: 상대 고르기
    for u, lbl, col, x in ((2, '첫째와 협상', 'red', -70), (3, '둘째와 협상', 'purple', 70)):
        hold = V('첫째주') if u == 2 else V('둘째주')
        b = button(P, sc, '상대%d' % u, lbl, x, -20, 116, 26, col, actions=[
            setv('협상상대', u),
            ifelse(lt(hold, 1000), [*say('더 팔 지분 없어.\n딴 데 알아봐.')],
                   [*say(LGET('협상인사', u)), *goto_phase(2)])])
        phase_show(b, 1)
    # 2단계: 지분 고르기
    for k, q in enumerate(D.NEGO_LOTS):
        x = -100 + k * 100
        hold = ifelse_hold()
        b = button(P, sc, '지분%d' % q, '%d%% (%s주)' % (q // 1000, format(q, ',')), x, -20, 92, 24, 'royal', actions=[
            ifelse(lt(hold, q), [*say('그만큼은 없어.\n욕심 부리지 마.')],
                   [setv('협상량', q),
                    # 큰아버지가 속으로 정한 최소 웃돈 배율 (숨김)
                    ifelse(eq(V('협상상대'), 2),
                           [setv('최소배율', add(D.NEGO_BASE[2][0], div(rnd(0, int(D.NEGO_BASE[2][1] * 100)), 100))),
                            chg('최소배율', div(sub(V('큰A'), V('내지지율')), 150))],
                           [setv('최소배율', add(D.NEGO_BASE[3][0], div(rnd(0, int(D.NEGO_BASE[3][1] * 100)), 100))),
                            chg('최소배율', div(sub(V('큰B'), V('내지지율')), 150))]),
                    chg('최소배율', mul(div(q, 1000), 0.04)),
                    if_(gt(stake_pct(), 40), chg('최소배율', 0.25)),
                    if_(lt(V('최소배율'), 1.2), setv('최소배율', 1.2)),
                    setv('인내심', D.NEGO_PATIENCE), setv('제시율', 20), setv('전술사용', 0), setv('협상기회', 0),
                    *say('좋아, 들어나 보지.\n웃돈은 얼마나 얹을 건데?'), *goto_phase(3)])])
        phase_show(b, 2)
    # 3단계: 전술 (한 번만) + 제안
    tactics = [
        ('할아버지 얘기', 'navy', 60, -0.10, 0.08, '...아버지 얘기는 왜 꺼내.\n조금 깎아 주지.', '아버지 팔지 마!\n값은 더 올라간다.', False),
        ('약점 압박', 'red', 35, -0.30, 0, '...그거 어디서 들었어.\n알았어, 알았다고.', '지금 협박하는 거야?\n끝이야. 나가.', True),
        ('화합 호소', 'purple', 75, -0.05, 0.03, '그래, 그래도 한 핏줄이지.\n조금은 봐줄게.', '집안 화합? 웃기고 있네.', False),
    ]
    for k, (lbl, col, p, good, bad, ok_txt, ng_txt, breaks) in enumerate(tactics):
        x = -104 + k * 104
        fail = [*say(ng_txt)] + ([setv('협상금지턴', 3), setv('협상결과', 2), *goto_phase(4)] if breaks else [chg('최소배율', bad)])
        b = button(P, sc, '전술%d' % k, lbl, x, -20, 96, 24, col, actions=[
            if_(eq(V('전술사용'), 0), setv('전술사용', 1), cast('전술숨김'),
                ifelse(le(rnd(1, 100), p), [chg('최소배율', good), *say(ok_txt)], fail))])
        phase_show(b, 3)
        b.on(on_msg('전술숨김'), hide())
    offer = text(P, sc, '제시가', '', 0, -88, 10, C_WHITE, F_NUM, False, 0, w=170, h=28, bg=C_BOX)
    offer.on(on_scene(), forever(if_(eq(V('협상단계'), 3),
                                     *fmt_money(mul(mul(V('협상량'), LGET('주가', CTL)), add(1, div(V('제시율'), 100))), '_m'),
                                     write(join('웃돈 +', V('제시율'), '%\n총 ', V('_m')))), wait(0.1)))
    phase_show(offer, 3)
    bm = button(P, sc, '웃돈내림', '-10%', -116, -88, 52, 22, 'blue', actions=[if_(gt(V('제시율'), 0), chg('제시율', -10))])
    bp = button(P, sc, '웃돈올림', '+10%', 116, -88, 52, 22, 'blue', actions=[if_(lt(V('제시율'), 300), chg('제시율', 10))])
    mult = add(1, div(V('제시율'), 100))
    cost = mul(mul(V('협상량'), LGET('주가', CTL)), mult)
    give = V('첫째주')
    accept = [
        ifelse(lt(V('돈'), cost), [chg('인내심', -1), *say('돈도 없으면서\n무슨 거래야!')],
               [chg('돈', mul(cost, -1)),
                lst_set('평단', CTL, div(add(mul(LGET('평단', CTL), LGET('보유', CTL)), cost), add(LGET('보유', CTL), V('협상량')))),
                lst_set('보유', CTL, add(LGET('보유', CTL), V('협상량'))),
                ifelse(eq(V('협상상대'), 2), [chg('첫째주', mul(V('협상량'), -1))], [chg('둘째주', mul(V('협상량'), -1))]),
                setv('협상결과', 1),
                *say('...좋아. 거래하지.\n대신 아버지한텐 비밀이다.'), G.sfx('fanfare'),
                *goto_phase(4), *majority_check()])]
    propose = [
        ifelse(ge(mult, V('최소배율')), accept,
               [ifelse(lt(mult, mul(V('최소배율'), 0.8)),
                       [chg('인내심', -2), *say('장난해?\n그 돈이면 꿈도 꾸지 마.')],
                       [chg('인내심', -1),
                        setv('_t', rounded(mul(sub(add(V('최소배율'), div(rnd(5, 25), 100)), 1), 100))),
                        *say(join('아직 멀었어.\n최소 +', V('_t'), '%는 얹어야 생각해 보지.'))]),
                G.sfx('bad')]),
        if_(and_(le(V('인내심'), 0), eq(V('협상단계'), 3)),
            setv('협상금지턴', 2), setv('협상결과', 2), *say('됐어.\n너랑은 말이 안 통해.'), *goto_phase(4)),
    ]
    bo = button(P, sc, '제안하기', '제안하기', 186, -88, 80, 24, 'red', icon='bolt', actions=propose)
    for o in (bm, bp, bo):
        phase_show(o, 3)
    # 4단계: 결과
    res = text(P, sc, '협상결과글', '', 0, -22, 13, C_WHITE, F_NUM, False, 0, w=360, h=40)
    res.on(on_msg('협상단계'),
           ifelse(eq(V('협상결과'), 1), [*fmt_comma(V('협상량'), '_q'), write(join('협상 성공! 지배 자본 ', V('_q'), '주 확보')), text_color(C_ACC)],
                  [ifelse(eq(V('협상결과'), 2), [write(join('협상 결렬... 큰아버지들이 ', V('협상금지턴'), '번의 유세 동안 협상을 거부해요')),
                                               text_color(C_RED)],
                          [ifelse(gt(V('협상금지턴'), 0), [write(join('큰아버지들이 화가 나 있어요. 유세 ', V('협상금지턴'), '번 뒤에 다시 오세요')),
                                                          text_color(C_RED)],
                                  [write('이번 유세 기간에는 이미 협상했어요.\n유세를 하고 다시 오세요'), text_color(C_DIM)])])]))
    phase_show(res, 4)
    back = button(P, sc, '그만두기', '지도로', -200, -121, 66, 22, 'navy', icon='back', actions=go(ctx['S_MAP']))
    mgr = text(P, sc, '협상담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), setv('협상결과', 0),
           ifelse(or_(gt(V('협상금지턴'), 0), eq(V('협상기회'), 0)),
                  [*say('...'), *goto_phase(4)],
                  [*say('막내가 무슨 일로 찾아왔지?\n누구하고 얘기할 건데?'), *goto_phase(1)]))
    majority_pop(P, sc)
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])


def ifelse_hold():
    """협상 상대 큰아버지의 보유 주식 수 (변수 _e 에 넣고 쓰지 않고, 식으로): 첫째면 첫째주, 아니면 둘째주."""
    # 첫째주×[상대=2] + 둘째주×[상대=3]  (상대는 2 또는 3)
    return add(mul(V('첫째주'), sub(3, V('협상상대'))), mul(V('둘째주'), sub(V('협상상대'), 2)))
