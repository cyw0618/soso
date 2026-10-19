# -*- coding: utf-8 -*-
"""돌발상황 / 작전 본부 / 개표 / 조치원 장악 / 랭킹 / 파산 장면."""
import re
import os
from PIL import Image, ImageDraw, ImageFilter
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, fmt_comma, fmt_money, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
from art_common import save, ensure_out
import data as D
import scene_stock as ST
import empire as E
import savegame as SG
import career as CR
import data2 as D2

W, H = 960, 540


# ------------------------------------------------------------------ 그림
def _edge_glow(name, rgb, strength=200, inner=0.62):
    p = os.path.join(ensure_out(), name + '.png')
    if os.path.exists(p):
        return p
    m = Image.new('L', (W // 4, H // 4), 255)
    ImageDraw.Draw(m).rounded_rectangle((W // 4 * (1 - inner) / 2, H // 4 * (1 - inner) / 2,
                                         W // 4 * (1 + inner) / 2, H // 4 * (1 + inner) / 2), 30, fill=0)
    m = m.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40)).point(lambda v: v * strength // 255)
    im = Image.new('RGBA', (W, H), rgb + (255,))
    im.putalpha(m)
    im.save(p)
    return p


def _tint(name, rgba):
    p = os.path.join(ensure_out(), name + '.png')
    if not os.path.exists(p):
        Image.new('RGBA', (W, H), rgba).save(p)
    return p


# ------------------------------------------------------------------ 지지율 계산 보조
def normalize():
    return [if_(lt(V('내지지율'), 0.5), setv('내지지율', 0.5)), if_(lt(V('큰A'), 1), setv('큰A', 1)),
            setv('내지지율', round1(V('내지지율'))), setv('큰A', round1(V('큰A'))),
            setv('큰B', round1(sub(sub(100, V('내지지율')), V('큰A')))),
            if_(lt(V('큰B'), 1), setv('큰B', 1), setv('큰A', round1(sub(99, V('내지지율')))))]


def support_gain(g):
    """g>0: 두 큰아버지에게서 비율대로 가져옴 (내 지지율이 높을수록 덜 오름), g<0: 두 큰아버지에게 반씩 넘어감."""
    return [setv('_g', g), if_(gt(V('_g'), 0), setv('_g', mul(V('_g'), sub(1.1, div(V('내지지율'), 100))))),
            ifelse(gt(V('_g'), 0),
                   [setv('tmp', div(V('큰A'), add(V('큰A'), V('큰B')))),
                    chg('큰A', mul(mul(V('_g'), V('tmp')), -1)), chg('큰B', mul(mul(V('_g'), sub(1, V('tmp'))), -1)),
                    chg('내지지율', V('_g'))],
                   [chg('내지지율', V('_g')), chg('큰A', mul(V('_g'), -0.5)), chg('큰B', mul(V('_g'), -0.5))]),
            *normalize()]


def transfer(from_var, x):
    """특정 큰아버지에게서 x%p 가져옴 (내 지지율이 높을수록 덜 오름)."""
    return [setv('_g', mul(x, sub(1.1, div(V('내지지율'), 100)))), chg(from_var, mul(V('_g'), -1)), chg('내지지율', V('_g')),
            *normalize()]


def grandpa_say(P, sc, ctx, x, y, msg, lines_expr_blocks, scale=0.6, bx=None, by=None, bw=150):
    """할아버지 상반신 + 말풍선. msg 를 받으면 나타남. lines_expr_blocks: 말풍선 글 쓰는 블록들."""
    gp = sprite(P, sc, '할아버지', ctx['BUST']['gp'], x, y, scale=scale, visible=False)
    bx = x + 70 if bx is None else bx
    by = y + 72 if by is None else by
    bub = panel(P, sc, '말풍선', bx, by, bw, 54, 'card', visible=False)
    t = text(P, sc, '한마디', '', bx, by, 10 if bw >= 140 else 9, C_WHITE, F_BODY, True, 0, w=bw - 14, h=44, visible=False)
    gp.on(on_msg(msg), gp.pct(90), fx('transparency', 60), show(), rep(6, gp.grow_pct(1.7), fx_add('transparency', -10), wait(0.02)))
    bub.on(on_msg(msg), wait(0.25), show())
    t.on(on_msg(msg), *lines_expr_blocks, wait(0.25), show())
    return gp


def score_blocks():
    """최종 점수 = 지지율×100 + 자산 점수 + 지배 자본 지분(%)×60 + 계열사×800 + 군수 8000 + 직위 보너스(시장 2만/대통령 7만)
    + 인수 기업×500 + 내 회사 1000. 자산 점수: 1000억까지 억당 20점, 넘으면 √(초과 억)×60."""
    eok = div(V('총자산'), 10000)
    return [
        *ST.assets_blocks(),
        setv('_sc', eok),
        ifelse(le(V('_sc'), 1000), [setv('_sc', mul(V('_sc'), 20))], [setv('_sc', add(20000, mul(fn('root', sub(V('_sc'), 1000)), 60)))]),
        if_(lt(V('_sc'), 0), setv('_sc', 0)),
        setv('최종점수', add(add(rounded(mul(V('내지지율'), 100)), floor(V('_sc'))),
                         rounded(mul(div(LGET('보유', ST.CTL), D.CONTROL_SHARES / 100.0), 60)))),
        chg('최종점수', mul(V('계열사수'), D.AFFILIATE_SCORE)),
        if_(or_(eq(V('당선'), 1), ge(V('직위'), 1)), chg('최종점수', 8000)),
        chg('최종점수', LGET('직위점수', add(V('직위'), 1))),
        chg('최종점수', mul(V('인수수'), 500)),
        if_(eq(V('회사상태'), 1), chg('최종점수', 1000)),
        setv('최종점수', rounded(V('최종점수'))),
    ]


def name_asker(P, sc, x=200, y=-64):
    """이름 입력 담당: 엔트리 질문 말풍선이 이 (투명한) 오브젝트 위에 뜬다. '이름입력' 신호로 시작.
    랭킹은 지우지 않고 계속 쌓는다 (점수 순서대로 끼워 넣음). 같은 판에서 다시 등록하면 내 이전 기록을 새 점수로 바꾼다."""
    p = os.path.join(ensure_out(), 'fx_clear_dot.png')
    if not os.path.exists(p):
        Image.new('RGBA', (8, 8), (0, 0, 0, 1)).save(p)
    o = sprite(P, sc, '이름입력', p, x, y)
    o.on(on_msg('이름입력'),
         ifelse(gt(slen(V('등록이름')), 0), [setv('플레이어이름', V('등록이름'))],
                [ask('랭킹에 올릴 이름을 입력!'), setv('플레이어이름', str_replace(answer(), '[|§]', ''))]),
         if_(eq(slen(V('플레이어이름')), 0), setv('플레이어이름', '막내')),
         if_(gt(slen(V('플레이어이름')), 12), setv('플레이어이름', substr(V('플레이어이름'), 1, 12))),
         # 이전 내 기록 지우기
         if_(and_(gt(slen(V('등록이름')), 0), ge(V('등록점수'), 0)),
             setv('i', 1),
             until(or_(gt(V('i'), sub(LLEN('랭킹이름'), 1)),
                       and_(eq(LGET('랭킹이름', V('i')), V('등록이름')), eq(LGET('랭킹점수', V('i')), V('등록점수')))),
                   chg('i', 1)),
             if_(le(V('i'), sub(LLEN('랭킹이름'), 1)), lst_del('랭킹이름', V('i')), lst_del('랭킹점수', V('i')))),
         setv('i', 1),
         until(lt(LGET('랭킹점수', V('i')), V('최종점수')), chg('i', 1)),
         lst_ins('랭킹이름', V('i'), V('플레이어이름')), lst_ins('랭킹점수', V('i'), V('최종점수')),
         setv('등록이름', V('플레이어이름')), setv('등록점수', V('최종점수')),
         setv('내순위', V('i')), setv('방금등록', 1),
         cast('랭킹등록'))
    return o


def finish_blocks(ctx, always=False):
    """점수 계산 후, 승리했거나 군수 이상이었으면 이름 입력 → 랭킹 등록. 아니면 등록 없이 끝."""
    if always:
        return [*score_blocks(), cast('이름입력')]
    return [*score_blocks(),
            ifelse(or_(eq(V('당선'), 1), ge(V('직위'), 1)), [cast('이름입력')], [setv('내순위', 0), cast('랭킹등록')])]


def ending_dim(P, sc):
    """엔딩 대사 때 뒤를 어둡게 (이름 입력창과 겹치지 않게 할아버지를 위로)."""
    o = sprite(P, sc, '엔딩어둡게', _tint('fx_dark_navy2', (2, 4, 14, 210)), 0, 0, visible=False)
    o.on(on_msg('엔딩대사'), fx('transparency', 100), show(), rep(10, fx_add('transparency', -10), wait(0.02)))
    return o


def ending_buttons(P, sc, ctx, y=-112, xs=(-64, 64)):
    b1 = button(P, sc, '랭킹보기', '랭킹 보기', xs[0], y, 110, 28, 'purple', icon='trophy', visible=False,
                actions=go(ctx['S_RANK']))
    b2 = button(P, sc, '처음으로', '처음으로', xs[1], y, 110, 28, 'royal', icon='back', visible=False,
                actions=go(ctx['S_TITLE']))
    for b in (b1, b2):
        b.on(on_msg('랭킹등록'), show())
    rk = text(P, sc, '내순위', '', 0, y + 24, 11, C_ACC, F_NUM, False, 0, w=300, h=16, visible=False)
    rk.on(on_msg('랭킹등록'), *fmt_comma(V('최종점수'), '_q'),
          ifelse(gt(V('내순위'), 0), [write(join('최종 점수 ', V('_q'), '점 · 명예의 전당 ', V('내순위'), '위 등록!')), text_color(C_ACC)],
                 [write(join('최종 점수 ', V('_q'), '점 · 군수가 되어야 랭킹에 오를 수 있어요')), text_color(C_DIM)]), show())


# ================================================================== 돌발상황
def scene_event(P, ctx):
    sc = ctx['S_EVENT']
    E = D.EVENTS
    P.list('사건제목', [e[0] for e in E])
    P.list('사건내용', [e[1] for e in E])
    P.list('사건크기', [e[2] for e in E])
    P.list('선택지', [o[0] for e in E for o in e[3]])
    P.list('선택확률', [o[1] for e in E for o in e[3]])
    P.list('성공돈', [o[2] for e in E for o in e[3]])
    P.list('성공지지', [o[3] for e in E for o in e[3]])
    P.list('실패돈', [o[4] for e in E for o in e[3]])
    # 결과 문장 속 괄호(돈 이야기)는 뺀다: 돈 결과는 매번 달라지기 때문
    P.list('성공문', [re.sub(r'\s*\([^)]*\)', '', o[5]) for e in E for o in e[3]])
    P.list('실패문', [re.sub(r'\s*\([^)]*\)', '', o[6] or '-') for e in E for o in e[3]])
    # 사건마다 선택지 순서를 섞고(순열 6가지), 확률·손익도 새로 굴린다
    P.list('순열', [x for pm in ((1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)) for x in pm])
    for v in ('카드옵션', '카드확률', '카드돈', '카드지지', '카드실패'):
        P.list(v, [0, 0, 0])
    for v in ('사건금액', '사건손익', '사건순익', '사건성공', '사건지지', '결정됨', '반대매매', '_i', '_g', '결과글'):
        P.var(v, 0)

    bg = G.bg(P, sc, ctx['PLACE_PICS'])
    bg.on(on_scene(), if_(lt(V('지역번호'), 1), setv('지역번호', 1)), shape(V('지역번호')))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    vig = sprite(P, sc, '경보빛', _edge_glow('fx_alert_red_dim', (150, 10, 30), 150), 0, 0)
    vig.on(on_scene(), forever(rep(12, fx_add('transparency', 4), wait(0.03)), rep(12, fx_add('transparency', -4), wait(0.03))))
    ban = sprite(P, sc, '사건제목띠', K.banner('돌발상황!', 170, 36, 'red'), 0, 112)
    ban.on(on_scene(), rep(3, mvx(4), wait(0.03), mvx(-8), wait(0.03), mvx(4), wait(0.03)))
    size_b = sprite(P, sc, '사건크기표', [('1', K.badge('소형 사건', 62, 18, 'navy')), ('2', K.badge('중형 사건', 62, 18, 'purple')),
                                       ('3', K.badge('대형 사건', 62, 18, 'red'))], 140, 112)
    size_b.on(on_msg('사건표시'), shape(LGET('사건크기', V('이벤트'))))
    panel(P, sc, '사건판', 0, 50, 430, 80, 'alert')
    t_title = text(P, sc, '사건이름', '', 0, 74, 14, C_WHITE, F_NUM, False, 0, w=400, h=20)
    t_desc = text(P, sc, '사건설명', '', 0, 50, 10, C_WHITE, F_BODY, True, 0, w=400, h=28)
    t_amt = text(P, sc, '사건규모', '', 0, 26, 9, C_ACC, F_NUM, False, 0, w=400, h=14)
    t_title.on(on_msg('사건표시'), write(CR.rival_text(LGET('사건제목', V('이벤트')))))
    t_desc.on(on_msg('사건표시'), write(CR.rival_text(LGET('사건내용', V('이벤트')))))
    t_amt.on(on_msg('사건표시'), *fmt_money(V('사건금액'), '_m'),
             write(join('사건 규모 ', V('_m'), '   ·   위기관리팀 ', V('방어권'), '회')))

    # 선택 카드 3장 (확률·비용·보상은 숨김: 고른 뒤에만 결과 공개)
    cards = []
    for k in (1, 2, 3):
        x = -146 + (k - 1) * 146
        idx = add(mul(sub(V('이벤트'), 1), 3), LGET('카드옵션', k))
        c = panel(P, sc, '선택카드%d' % k, x, -42, 138, 86, 'card')
        G.hover_scripts(c, 104)
        num = sprite(P, sc, '선택번호%d' % k, K.badge('선택 %d' % k, 46, 16, 'royal'), x, -10)
        lab = text(P, sc, '선택이름%d' % k, '', x, -44, 12, C_WHITE, F_NUM, False, 0, w=124, h=44)
        q = text(P, sc, '선택물음%d' % k, '결과는 고른 뒤에', x, -72, 8, C_DIM, F_BODY, True, 0, w=124, h=12)
        lab.on(on_msg('사건표시'), write(CR.rival_text(LGET('선택지', idx))))
        pick = [if_(eq(V('결정됨'), 0), setv('결정됨', 1), setv('선택', k), cast('사건선택'))]
        for o in (c, num, lab, q):
            o.on(on_click(), *pick)
            o.on(on_msg('사건결과'), hide())
        text(P, sc, '선택키%d' % k, '', -300, -300, 8, visible=False).on(on_key(48 + k), *pick)
        cards.append(c)
    # 시간 막대
    bars = K.bar_set('evt_time', 300, 7, 'red')
    tb = sprite(P, sc, '결정시간', bars, 0, 8)
    tb.on(on_scene(), show(), forever(shape(add(floor(mul(div(V('남은시간'), 12), 40)), 1)), wait(0.05)))
    tb.on(on_msg('사건결과'), hide())
    hint = text(P, sc, '결정안내', '12초 안에 고르세요! (클릭 또는 1·2·3)  셋 중 하나는 반드시 안전해요. 어느 것일까?', 0, -98, 8,
                C_DIM, F_BODY, True, 0, w=420, h=12)
    hint.on(on_msg('사건결과'), hide())

    # 결과 표시
    G.big_pop(P, sc, '성공팝', K.big_text('대처 성공!', 36, 'royal'), 0, 6, '사건성공팝', hold=0.9)
    G.big_pop(P, sc, '실패팝', K.big_text('대처 실패...', 34, 'red'), 0, 6, '사건실패팝', hold=0.9)
    res_p = panel(P, sc, '결과판', 52, -50, 316, 96, 'glass', visible=False)
    r_txt = text(P, sc, '결과글', '', 52, -22, 11, C_WHITE, F_BODY, True, 0, w=296, h=30, visible=False)
    r_money = text(P, sc, '결과돈', '', 52, -48, 14, C_WHITE, F_NUM, False, 0, w=296, h=20, visible=False)
    r_sup = text(P, sc, '결과지지', '', 52, -66, 10, C_WHITE, F_NUM, False, 0, w=296, h=15, visible=False)
    r_ext = text(P, sc, '결과추가', '', 52, -82, 8, C_RED, F_BODY, True, 0, w=296, h=12, visible=False)
    res_p.on(on_msg('사건결과'), wait(0.9), show())
    r_txt.on(on_msg('사건결과'), write(CR.rival_text(V('결과글'))), wait(1.0), show())
    r_money.on(on_msg('사건결과'), *fmt_money(abs_(V('사건순익')), '_m'),
               ifelse(gt(V('사건순익'), 0), [write(join('재산 +', V('_m'))), text_color(C_ACC)],
                      [ifelse(lt(V('사건순익'), 0), [write(join('재산 -', V('_m'))), text_color(C_RED)],
                              [write('재산 변화 없음'), text_color(C_DIM)])]), wait(1.1), show())
    r_sup.on(on_msg('사건결과'),
             ifelse(gt(V('사건지지'), 0), [write(join('지지율 +', round1(V('사건지지')), '%p')), text_color(C_ACC)],
                    [ifelse(lt(V('사건지지'), 0), [write(join('지지율 ', round1(V('사건지지')), '%p')), text_color(C_RED)],
                            [write('지지율 변화 없음'), text_color(C_DIM)])]),
             wait(1.2), show())
    r_ext.on(on_msg('사건결과'), if_(eq(V('반대매매'), 1), write('현금이 바닥나서 갖고 있던 주식이 강제로 팔렸다 (반대매매)'), wait(1.3), show()))
    nxt = button(P, sc, '계속버튼', '계속', 150, -112, 96, 26, 'royal', icon='star', visible=False,
                 actions=[*ST.assets_blocks(), if_(le(V('총자산'), 0), *go(ctx['S_BANKRUPT'])),
                          if_(ge(V('유세횟수'), LGET('곳수', V('단계'))), *go(ctx['S_VOTE'])), *ctx['GO_HOME']()])
    nxt.on(on_msg('사건결과'), wait(1.5), show())
    grandpa_say(P, sc, ctx, -200, -78, '사건결과',
                [wait(1.4), ifelse(eq(V('사건성공'), 1),
                                   [ifelse(lt(V('사건순익'), 0), [write('돈 좀 썼군.\n사람을 얻었으면 남는 장사다.')],
                                           [write('그래, 그거다.\n위기는 기회야.')])],
                                   [write('지금 뭐 하는 거냐!\n판을 읽어.')])], scale=0.45, bx=-178, by=-2, bw=116)
    # 선택지 순서 섞기 (안전한 선택지는 반드시 성공하고, 나머지는 돈 크기만 조금씩 흔들림)
    shuffle_cards = [setv('_g', rnd(1, 6))]
    for k in (1, 2, 3):
        shuffle_cards += [
            lst_set('카드옵션', k, LGET('순열', add(mul(sub(V('_g'), 1), 3), k))),
            setv('_i', add(mul(sub(V('이벤트'), 1), 3), LGET('카드옵션', k))),
            lst_set('카드확률', k, LGET('선택확률', V('_i'))),
            lst_set('카드돈', k, rounded(div(mul(LGET('성공돈', V('_i')), rnd(85, 115)), 100))),
            lst_set('카드지지', k, div(rounded(mul(LGET('성공지지', V('_i')), rnd(9, 11))), 10)),
            lst_set('카드실패', k, rounded(div(mul(LGET('실패돈', V('_i')), rnd(85, 115)), 100))),
        ]
    # 담당 (계산)
    mgr = text(P, sc, '사건담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(),
           setv('결정됨', 0), setv('이벤트', rnd(1, len(E))), *ST.assets_blocks(),
           setv('_v', mul(V('총자산'), D.EVENT_RATE)), if_(lt(V('_v'), D.EVENT_MIN), setv('_v', D.EVENT_MIN)),
           setv('사건금액', mul(rounded(div(mul(V('_v'), LGET('사건크기', V('이벤트'))), 100)), 100)),
           *shuffle_cards,
           cast('사건표시'),
           setv('남은시간', 12),
           until(or_(le(V('남은시간'), 0), eq(V('결정됨'), 1)), wait(0.1), chg('남은시간', -0.1)),
           if_(eq(V('결정됨'), 0), setv('결정됨', 1), setv('선택', 2), cast('사건선택')))
    sz = LGET('사건크기', V('이벤트'))
    liquidate = []
    for i in range(1, ST.N + 1):
        liquidate.append(if_(gt(LGET('보유', i), 0), chg('돈', mul(LGET('보유', i), LGET('주가', i))),
                             lst_set('보유', i, 0), lst_set('평단', i, 0)))
    mgr.on(on_msg('사건선택'),
           setv('_i', add(mul(sub(V('이벤트'), 1), 3), LGET('카드옵션', V('선택')))),
           ifelse(le(rnd(1, 100), LGET('카드확률', V('선택'))),
                  # 성공: 돈은 선택지에 따라 늘 수도, 줄 수도 있다
                  [setv('사건성공', 1),
                   setv('사건손익', rounded(div(mul(V('사건금액'), LGET('카드돈', V('선택'))), 100))),
                   chg('돈', V('사건손익')), setv('사건지지', LGET('카드지지', V('선택'))), *support_gain(V('사건지지')),
                   setv('결과글', LGET('성공문', V('_i')))],
                  [setv('사건성공', 0),
                   ifelse(gt(V('방어권'), 0),
                          [chg('방어권', -1), setv('사건손익', 0), setv('사건지지', 0),
                           setv('결과글', join(LGET('실패문', V('_i')), ' 그래도 위기관리팀이 막아냈다!'))],
                          [setv('사건손익', mul(rounded(div(mul(V('사건금액'), LGET('카드실패', V('선택'))), 100)), -1)),
                           chg('돈', V('사건손익')), setv('사건지지', mul(add(0.4, mul(0.4, sz)), -1)), *support_gain(V('사건지지')),
                           setv('결과글', LGET('실패문', V('_i')))])]),
           setv('사건순익', V('사건손익')),
           setv('반대매매', 0),
           if_(lt(V('돈'), 0), *liquidate, setv('반대매매', 1)),
           *ST.assets_blocks(),
           cast('사건결과'),
           ifelse(eq(V('사건성공'), 1), [cast('사건성공팝')], [cast('사건실패팝')]))
    G.hud(P, sc, ctx['PORT'])
    hub = G.sound_hub(P, sc)
    hub.on(on_msg('사건표시'), play('alarm'))
    hub.on(on_msg('사건성공팝'), play('good'))
    hub.on(on_msg('사건실패팝'), play('bad'))
    G.fader(P, sc, ctx['BLACK'])


# ================================================================== 작전 본부 (상점)
SHOP = [
    # (이름, 아이콘, 설명, 가격(만원), 효과 키, 알림)
    ('첫째 비리 제보', 'mega', '첫째 큰아버지의 비리를\n언론에 제보한다\n(지지율 +2.5%p)', 30000, 'expose_a', '첫째 큰아버지의 비리가 터졌다! 지지율 +2.5%p'),
    ('둘째 영상 폭로', 'mega', '둘째 큰아버지의 막말\n영상을 공개한다\n(지지율 +2.5%p)', 30000, 'expose_b', '둘째 큰아버지의 막말 영상이 퍼졌다! 지지율 +2.5%p'),
    ('복숭아 나눔', 'star', '조치원 복숭아를\n시민들께 나눈다\n(지지율 +1.5%p)', 20000, 'peach', '복숭아 나눔 행사 대성공! 지지율 +1.5%p'),
    ('유튜브 홍보', 'chart', '조치원 브이로그로\n젊은 표심 공략\n(지지율 +0.8%p)', 10000, 'youtube', '영상이 화제가 됐다! 지지율 +0.8%p'),
    ('현수막 100장', 'ballot', '읍내 곳곳에\n현수막을 건다\n(지지율 +0.4%p)', 5000, 'banner', '현수막이 걸렸다! 지지율 +0.4%p'),
    ('위기관리팀', 'shield', '돌발상황에서 실패해도\n손해를 1번 막아준다', 15000, 'guard', '위기관리팀을 고용했다! (방어 1회)'),
    ('정보 차단', 'bolt', '큰아버지들의 반격과\n지배 자본 매수를\n유세 3번 동안 막는다', 20000, 'block', '정보를 차단했다! (유세 3번 동안)'),
    ('선거 컨설팅', 'trophy', '전문 선거 컨설턴트가\n전략을 짜 준다\n(지지율 +1.2%p)', 25000, 'consult', '컨설팅 효과! 지지율 +1.2%p'),
]


SHOP_ALL = SHOP + D2.SHOP_T2 + D2.SHOP_T3
SHOP_TABS = [(0, 8), (8, 4), (12, 4)]


def scene_shop(P, ctx):
    sc = ctx['S_SHOP']
    P.var('상점알림', '')
    P.var('빼오기가', 0)
    P.var('상점탭', 1)
    P.var('_si2', 0)
    P.list('상품이름', [x[0] for x in SHOP_ALL])
    P.list('상품설명', [x[2] for x in SHOP_ALL])
    P.list('상품가격', [x[3] for x in SHOP_ALL])
    P.list('상품알림', [x[5] for x in SHOP_ALL])
    P.list('상품아이콘', [x[1] for x in SHOP_ALL])
    P.list('상점탭시작', [t[0] for t in SHOP_TABS])
    P.list('상점탭개수', [t[1] for t in SHOP_TABS])
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '상점제목', K.banner('작전 본부', 150, 32, 'purple'), 0, 116)
    st = text(P, sc, '작전상태', '', 0, 94, 9, C_DIM, F_BODY, True, 0, w=300, h=13)
    st.on(on_scene(), forever(write(join('위기관리팀 ', V('방어권'), '회  ·  정보 차단 ', V('차단턴'), '턴  ·  가격 ×',
                                         LGET('상점배율', V('단계')))), wait(0.2)))
    note = text(P, sc, '상점알림', '', 128, -121, 9, C_WHITE, F_NUM, False, 0, w=200, h=16, visible=False, bg=C_BOX)
    note.on(on_msg('상점알림'), write(V('상점알림')), to_front(), show(), wait(2.0), hide())
    # 탭
    for k, (lbl, col) in enumerate((('기본 작전', 'purple'), ('시장 선거 기술', 'royal'), ('대선 기술', 'red')), 1):
        tb = sprite(P, sc, '상점탭%d' % k, [('off', K.badge(lbl, 96, 18, 'navy')), ('on', K.badge(lbl, 96, 18, col)),
                                         ('lock', K.badge('잠김', 96, 18, 'gray'))], -150 + (k - 1) * 104, 76)
        tb.on(on_msg('상점갱신'), ifelse(lt(V('단계'), k), [shape('lock')], [ifelse(eq(V('상점탭'), k), [shape('on')], [shape('off')])]))
        tb.on(on_click(), ifelse(lt(V('단계'), k),
                                 [setv('상점알림', '%s 선거에 나가면 열려요!' % ('세종시장' if k == 2 else '대통령')), cast('상점알림')],
                                 [setv('상점탭', k), cast('상점갱신')]))
    effects = {
        'expose_a': transfer('큰A', 2.5), 'expose_b': transfer('큰B', 2.5),
        'peach': support_gain(1.5), 'youtube': support_gain(0.8), 'banner': support_gain(0.4),
        'guard': [chg('방어권', 1)], 'block': [chg('차단턴', 3)], 'consult': support_gain(1.2),
        'tv2': support_gain(2.0), 'dig_a': transfer('큰A', 3), 'book': support_gain(2.5), 'data': support_gain(1.5) + [chg('방어권', 1)],
        'tv3': support_gain(3.5), 'debate': support_gain(2.5), 'dig_b': transfer('큰B', 4), 'bus': support_gain(3),
    }
    icons = sorted(set(x[1] for x in SHOP_ALL))
    for j in range(8):
        c, r = j % 4, j // 4
        x, y = -171 + c * 114, 20 - r * 92
        idx = add(add(LGET('상점탭시작', V('상점탭')), j), 1)
        on = lt(j, LGET('상점탭개수', V('상점탭')))
        card = panel(P, sc, '상품카드%d' % j, x, y, 110, 88, 'card')
        ic = sprite(P, sc, '상품아이콘%d' % j, [(n, K.icon_img(n, 20)) for n in icons], x - 36, y + 26)
        nm = text(P, sc, '상품이름%d' % j, '', x + 10, y + 26, 10, C_WHITE, F_NUM, False, 1, w=70, h=14)
        ds = text(P, sc, '상품설명%d' % j, '', x, y + 1, 7, C_DIM, F_BODY, True, 0, w=100, h=30)
        pt = text(P, sc, '상품가격%d' % j, '', x, y - 21, 9, C_ACC, F_NUM, False, 0, w=100, h=13)
        price = mul(LGET('상품가격', idx), LGET('상점배율', V('단계')))
        bt = button(P, sc, '구매버튼%d' % j, '실행', x, y - 36, 64, 18, 'royal', actions=[setv('_si2', idx), cast('상품구매')])
        for o in (card, bt):
            o.on(on_msg('상점갱신'), ifelse(on, [show()], [hide()]))
        ic.on(on_msg('상점갱신'), ifelse(on, [shape(LGET('상품아이콘', idx)), show()], [hide()]))
        nm.on(on_msg('상점갱신'), ifelse(on, [write(CR.rival_text(LGET('상품이름', idx))), show()], [hide()]))
        ds.on(on_msg('상점갱신'), ifelse(on, [write(CR.rival_text(LGET('상품설명', idx))), show()], [hide()]))
        pt.on(on_msg('상점갱신'), ifelse(on, [*fmt_money(price, '_m'), write(V('_m')), show()], [hide()]))
    mgr = text(P, sc, '상점담당', '', -300, -300, 8, visible=False)
    S_ = V('_si2')
    price = mul(LGET('상품가격', S_), LGET('상점배율', V('단계')))
    chain = []
    for i, item in enumerate(SHOP_ALL, 1):
        chain.append(if_(eq(S_, i), *effects[item[4]]))
    mgr.on(on_msg('상품구매'),
           ifelse(ge(V('돈'), price),
                  [chg('돈', mul(price, -1)), *chain, setv('상점알림', CR.rival_text(LGET('상품알림', S_))), cast('구매반짝'), G.sfx('coin')],
                  [setv('상점알림', '재화가 부족해요!'), G.sfx('bad')]),
           cast('상점알림'))
    mgr.on(on_scene(), if_(gt(V('상점탭'), V('단계')), setv('상점탭', 1)), cast('상점갱신'))
    G.sparkles(P, sc, '구매반짝', ctx['SPARK'], 40, -121, 12, 40)
    button(P, sc, '지도로', '돌아가기', -196, -121, 76, 22, 'navy', icon='back', actions=ctx['GO_HOME']())
    button(P, sc, '주식으로', '주식', -112, -121, 70, 22, 'blue', icon='chart', actions=go(ctx['S_STOCK']))
    button(P, sc, '회의실로', '회의실', -30, -121, 84, 22, 'royal', icon='coin', actions=go(ctx['S_INVEST']))
    ops = button(P, sc, '작전세력', '작전 세력', 56, -121, 84, 22, 'red', icon='bolt', actions=go(ctx['S_OPS']))
    ops.on(on_scene(), ifelse(ge(V('직위'), 1), [show()], [hide()]))
    case_b = button(P, sc, '수사대응', '수사 대응', 146, -121, 84, 22, 'red', icon='shield', actions=go(ctx['S_CASE']))
    case_b.on(on_scene(), ifelse(ge(V('직위'), 2), [show()], [hide()]))
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])


# ================================================================== 개표
def scene_vote(P, ctx):
    sc = ctx['S_VOTE']
    for v in ('개표율', '표시나', '표시A', '표시B'):
        P.var(v, 0)
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '청색빛', _edge_glow('fx_edge_blue', (20, 50, 200), 170), 0, 0)
    ttl = sprite(P, sc, '개표제목', [('1', K.banner('조치원 군수 개표 방송', 210, 34, 'royal')),
                                    ('2', K.banner('세종시장 개표 방송', 200, 34, 'royal')),
                                    ('3', K.banner('대통령 선거 개표 방송', 210, 34, 'royal'))], 0, 114)
    ttl.on(on_scene(), shape(V('단계')))
    live = sprite(P, sc, 'LIVE', K.badge('LIVE', 40, 18, 'red'), 128, 114)
    live.on(on_scene(), forever(show(), wait(0.5), hide(), wait(0.3)))
    panel(P, sc, '개표판', 0, 6, 450, 176, 'glass')
    CA = ctx['CAND_CARD']
    cols = [('me', ['나 (막내)'] * 3, '표시나', ['royal'] * 3, C_ACC),
            ('u1', ['첫째 큰아버지', '1번 · ' + D2.RIVAL_PARTY[2][0], '1번 · ' + D2.RIVAL_PARTY[3][0]], '표시A', ['red', D2.RIVAL_COLOR[2][0], D2.RIVAL_COLOR[3][0]], C_RED),
            ('u2', ['둘째 큰아버지', '2번 · ' + D2.RIVAL_PARTY[2][1], '2번 · ' + D2.RIVAL_PARTY[3][1]], '표시B', ['purple', D2.RIVAL_COLOR[2][1], D2.RIVAL_COLOR[3][1]], C_VIOLET)]
    for k, (pk, names, var, cols_, hexc) in enumerate(cols):
        x = -146 + k * 146
        if pk == 'me':
            sprite(P, sc, '후보%d' % k, ctx['BUST'][pk], x, 44, scale=0.5)
        else:
            n = pk[1]
            ph = sprite(P, sc, '후보%d' % k, [('1', ctx['BUST'][pk]), ('2', CA['m' + n]), ('3', CA['p' + n])], x, 44, scale=0.5)
            ph.on(on_scene(), shape(V('단계')))
        nb = sprite(P, sc, '후보이름%d' % k, [(str(t + 1), K.badge(names[t], 104, 18, cols_[t])) for t in range(3)], x, -8)
        nb.on(on_scene(), shape(V('단계')))
        b = sprite(P, sc, '득표막대%d' % k, K.bar_set('vote_' + cols_[0], 120, 10, cols_[0]), x, -28)
        b.on(on_scene(), forever(shape(add(floor(div(V(var), 2.5)), 1)), wait(0.03)))
        tv = text(P, sc, '득표율%d' % k, '0%', x, -48, 18, hexc, F_NUM, False, 0, w=120, h=24)
        tv.on(on_scene(), forever(write(join(V(var), '%')), wait(0.03)))
    rate = text(P, sc, '개표율글', '', 0, -74, 10, C_WHITE, F_NUM, False, 0, w=200, h=15)
    rate.on(on_scene(), forever(write(join('개표율 ', V('개표율'), '%')), wait(0.05)))
    stake = text(P, sc, '지분확인', '', 0, -92, 11, C_WHITE, F_NUM, False, 0, w=420, h=16, visible=False)
    stake.on(on_msg('지분공개'),
             ifelse(eq(V('단계'), 1),
                    [write(join('조치원 지배 자본 내 지분 ', ST.pct2(LGET('보유', ST.CTL)), '%  (과반 기준 50%)')),
                     ifelse(gt(LGET('보유', ST.CTL), D.CONTROL_GOAL), [text_color(C_ACC)], [text_color(C_RED)])],
                    [write('후보 셋 가운데 지지율 1등이 당선!'), text_color(C_ACC)]), show())
    mgr = text(P, sc, '개표담당', '', -300, -300, 8, visible=False)
    noise = lambda: mul(div(rnd(-30, 30), 10), sub(1, div(V('개표율'), 100)))
    mgr.on(on_scene(), setv('개표율', 0), setv('당선', 0), setv('지배달성', 0), wait(1.0), G.sfx('drumroll'),
           until(ge(V('개표율'), 100), chg('개표율', 2),
                 setv('표시나', round1(add(mul(V('내지지율'), div(V('개표율'), 100)), noise()))),
                 setv('표시A', round1(add(mul(V('큰A'), div(V('개표율'), 100)), noise()))),
                 setv('표시B', round1(add(mul(V('큰B'), div(V('개표율'), 100)), noise()))),
                 if_(lt(V('표시나'), 0), setv('표시나', 0)), if_(lt(V('표시A'), 0), setv('표시A', 0)),
                 if_(lt(V('표시B'), 0), setv('표시B', 0)), wait(0.07)),
           setv('표시나', V('내지지율')), setv('표시A', V('큰A')), setv('표시B', V('큰B')),
           wait(0.8), cast('지분공개'), G.sfx('stamp'), wait(1.4),
           if_(gt(LGET('보유', ST.CTL), D.CONTROL_GOAL), setv('지배달성', 1)),
           # 군수: 지지율 50% 초과 + 지배 자본 50% 초과 / 시장·대통령: 후보 셋 중 1등
           ifelse(eq(V('단계'), 1),
                  [if_(and_(gt(V('내지지율'), D.WIN_SUPPORT), eq(V('지배달성'), 1)), setv('당선', 1))],
                  [if_(and_(gt(V('내지지율'), V('큰A')), gt(V('내지지율'), V('큰B'))), setv('당선', 1))]),
           ifelse(eq(V('당선'), 1),
                  [cast('당선'), cast('축하'), wait(2.4),
                   ifelse(eq(V('단계'), 1), go(ctx['S_CONTROL']),
                          [*CR.win_tier_blocks(),
                           ifelse(eq(V('단계'), 3), [setv('엔딩종류', 1), *go(ctx['S_ENDING'])], go(ctx['S_OFFICE']))])],
                  [cast('낙선'), wait(2.6), cast('엔딩대사'), wait(1.6),
                   if_(eq(V('직위'), 0), *SG.clear_blocks()),
                   *finish_blocks(ctx)]))
    ending_dim(P, sc)
    G.big_pop(P, sc, '당선팝', [('1', K.big_text('군수 당선!', 50, 'royal')), ('2', K.big_text('세종시장 당선!', 46, 'royal')),
                               ('3', K.big_text('대통령 당선!', 50, 'royal'))], 0, 20, '당선', hold=1.8, pre=[shape(V('단계'))])
    G.big_pop(P, sc, '낙선팝', K.big_text('낙선...', 46, 'red'), 0, 20, '낙선', hold=1.6)
    res = text(P, sc, '개표결과', '', 60, 84, 11, C_WHITE, F_NUM, False, 0, w=320, h=34, visible=False)
    res.on(on_msg('엔딩대사'),
           ifelse(gt(V('단계'), 1), [write('지지율 1등을 놓쳤다...\n그래도 집무실에서 다시 준비할 수 있다')],
                  [ifelse(and_(le(V('내지지율'), D.WIN_SUPPORT), eq(V('지배달성'), 0)),
                          [write('지지율도, 지배 자본도\n과반을 넘지 못했다...')],
                          [ifelse(le(V('내지지율'), D.WIN_SUPPORT), [write('지배 자본은 쥐었지만\n지지율이 과반을 넘지 못했다...')],
                                  [write('표는 얻었지만\n지배 자본이 과반을 넘지 못했다...')])])]),
           text_color(C_RED), show())
    G.confetti(P, sc, '축하', ctx['CONF'], 50)
    grandpa_say(P, sc, ctx, -170, -8, '엔딩대사',
                [ifelse(gt(V('단계'), 1), [write(D2.GP_TIER_LOSE)],
                        [ifelse(or_(gt(V('내지지율'), D.WIN_SUPPORT), eq(V('지배달성'), 1)), [write(D.GP_HALF)], [write(D.GP_LOSE)])])],
                scale=0.6, bx=40, by=30, bw=220)
    ending_buttons(P, sc, ctx, xs=(-150, 150))
    cont = button(P, sc, '계속투자', '집무실로 (계속)', 0, -112, 120, 28, 'green', icon='coin', visible=False,
                  actions=[setv('캠페인중', 0), *go(ctx['S_OFFICE'])])
    cont.on(on_msg('랭킹등록'), if_(ge(V('직위'), 1), show()))
    name_asker(P, sc)
    hub = G.sound_hub(P, sc)
    hub.on(on_msg('당선'), play('fanfare'))
    hub.on(on_msg('낙선'), play('fail_big'))
    G.fader(P, sc, ctx['BLACK'])


# ================================================================== 조치원 장악 (군수 당선: 지지율 + 지배 자본 둘 다 과반)
def scene_control(P, ctx):
    sc = ctx['S_CONTROL']
    G.bg(P, sc, ctx['ART']('title_bg'))
    sprite(P, sc, '어둡게', _tint('fx_dark_navy', (2, 4, 16, 200)), 0, 0)
    glow = sprite(P, sc, '청색빛', _edge_glow('fx_edge_blue', (20, 50, 200), 170), 0, 0)
    glow.on(on_scene(), forever(rep(20, fx_add('transparency', 2), wait(0.04)), rep(20, fx_add('transparency', -2), wait(0.04))))
    G.big_pop(P, sc, '장악글', K.big_text('조치원 장악!', 50, 'royal'), 0, 82, '장악', hold=99, fade=False)
    sub_ = text(P, sc, '장악설명', '', 0, 46, 12, C_WHITE, F_NUM, False, 0, w=400, h=18, visible=False)
    sub_.on(on_msg('장악'), wait(0.6), write(join('지지율 ', V('내지지율'), '%  ·  지배 자본 ', ST.pct2(LGET('보유', ST.CTL)),
                                                   '%  ·  계열사 ', V('계열사수'), '개')), show())
    bx0, bw, by = -150, 300, 24
    bar = sprite(P, sc, '지분막대', K.icon_img('star', 2), bx0, by)
    seg = lambda e: add(bx0, mul(e, bw / float(D.CONTROL_SHARES)))
    bar.on(on_msg('장악'), wait(0.8), pen_up(), pen_clear(), pen_size(12),
           pen_color('#20263f'), xy(bx0, by), pen_down(), xy(bx0 + bw, by), pen_up(),
           pen_color('#3d6bff'), xy(bx0, by), pen_down(), xy(seg(LGET('보유', ST.CTL)), by), pen_up(),
           pen_color('#d42a46'), pen_down(), xy(seg(add(LGET('보유', ST.CTL), V('첫째주'))), by), pen_up(),
           pen_color('#7a46e6'), pen_down(), xy(seg(add(add(LGET('보유', ST.CTL), V('첫째주')), V('둘째주'))), by), pen_up(),
           xy(-300, -300))
    sprite(P, sc, '목표선', ST.SA.goal_marker(22), 0, by)
    lg = text(P, sc, '지분범례', '', 0, 8, 8, C_DIM, F_BODY, True, 0, w=320, h=12, visible=False)
    lg.on(on_msg('장악'), wait(0.9), write(join('나 ', ST.pct2(LGET('보유', ST.CTL)), '%  ·  첫째 ', ST.pct2(V('첫째주')),
                                                '%  ·  둘째 ', ST.pct2(V('둘째주')), '%')), show())
    me = sprite(P, sc, '나', ctx['BUST']['me'], 186, -40, scale=0.5, visible=False)
    me.on(on_msg('장악'), wait(1.2), show())
    ending_dim(P, sc)
    grandpa_say(P, sc, ctx, -170, -8, '엔딩대사', [write(D.GP_WIN)], scale=0.6, bx=40, by=28, bw=220)
    G.confetti(P, sc, '축하', ctx['CONF'], 60)
    # 계속(군수 취임) 또는 여기서 끝내기(랭킹 등록)
    go_on = button(P, sc, '군수취임', '군수 취임 (계속하기)', -80, -112, 150, 28, 'royal', icon='star', visible=False,
                   actions=[setv('직위', 1), setv('캠페인중', 0), setv('취임알림', 1), setv('평판', 50), setv('당선', 1),
                            *go(ctx['S_OFFICE'])])
    stop = button(P, sc, '끝내기', '여기서 끝내기', 92, -112, 120, 28, 'gray', icon='trophy', visible=False,
                  actions=[cast('끝내기'), *SG.clear_blocks(), *finish_blocks(ctx, always=True)])
    for b in (go_on, stop):
        b.on(on_msg('선택버튼'), show())
        b.on(on_msg('끝내기'), hide())
    mgr = text(P, sc, '장악담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), setv('지배달성', 1), setv('당선', 1), *E.stats_blocks(),
           wait(0.4), cast('장악'), cast('축하'), wait(2.0), cast('엔딩대사'), wait(1.8), cast('선택버튼'))
    ending_buttons(P, sc, ctx)
    name_asker(P, sc)
    hub = G.sound_hub(P, sc)
    hub.on(on_msg('장악'), play('fanfare'))
    G.fader(P, sc, ctx['BLACK'])


# ================================================================== 랭킹
def scene_rank(P, ctx):
    sc = ctx['S_RANK']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '청색빛', _edge_glow('fx_edge_blue', (20, 50, 200), 170), 0, 0)
    sprite(P, sc, '랭킹제목', K.banner('명예의 전당', 170, 34, 'royal'), 0, 114)
    panel(P, sc, '랭킹판', 0, -6, 320, 204, 'glass')
    N = sub(LLEN('랭킹이름'), 1)            # 마지막은 표시용 '끝'
    badge_pics = [('1', K.badge('', 40, 16, 'royal')), ('2', K.badge('', 40, 16, 'silver')),
                  ('3', K.badge('', 40, 16, 'purple')), ('n', K.badge('', 40, 16, 'navy'))]
    for r in range(1, 11):
        y = 78 - (r - 1) * 18
        idx = add(V('랭킹쪽'), r - 1)
        bd = sprite(P, sc, '순위판%d' % r, badge_pics, -126, y)
        rn = text(P, sc, '순위글%d' % r, '', -126, y + 1, 9, C_WHITE, F_NUM, False, 0, w=40, h=13)
        nm = text(P, sc, '랭킹이름%d' % r, '', -30, y, 10, C_WHITE, F_BODY, True, 1, w=150, h=15)
        scr = text(P, sc, '랭킹점수%d' % r, '', 108, y, 10, C_ACC, F_NUM, False, 2, w=110, h=15)
        bd.on(on_msg('쪽갱신'), ifelse(le(idx, 3), [shape(idx)], [shape('n')]), ifelse(le(idx, N), [show()], [hide()]))
        rn.on(on_msg('쪽갱신'), ifelse(le(idx, N), [write(join(idx, '위'))], [write('')]))
        nm.on(on_msg('쪽갱신'), ifelse(le(idx, N), [write(LGET('랭킹이름', idx))], [write('')]),
              ifelse(and_(eq(V('내순위'), idx), gt(V('내순위'), 0)), [text_color(C_ACC)], [text_color(C_WHITE)]))
        scr.on(on_msg('쪽갱신'), ifelse(le(idx, N), [*fmt_comma(LGET('랭킹점수', idx), '_q'), write(join(V('_q'), '점'))],
                                       [write('')]))
    pg = text(P, sc, '쪽표시', '', 0, -104, 9, C_DIM, F_BODY, True, 0, w=220, h=13)
    pg.on(on_msg('쪽갱신'), ifelse(gt(N, 0), [write(join(V('랭킹쪽'), '~', add(V('랭킹쪽'), 9), '위  ·  지금까지 ', N, '명 기록'))],
                                  [write('')]))
    empty = text(P, sc, '빈랭킹', '아직 기록이 없어요.\n당선하거나 조치원을 장악하면\n원하는 이름으로 랭킹에 오를 수 있어요!', 0, -6, 12,
                 C_DIM, F_BODY, True, 0, w=280, h=60, visible=False)
    empty.on(on_msg('쪽갱신'), ifelse(eq(N, 0), [show()], [hide()]))
    button(P, sc, '이전쪽', '이전 쪽', -132, -104, 56, 18, 'navy',
           actions=[if_(gt(V('랭킹쪽'), 1), chg('랭킹쪽', -10), cast('쪽갱신'))])
    button(P, sc, '다음쪽', '다음 쪽', 132, -104, 56, 18, 'navy',
           actions=[if_(le(add(V('랭킹쪽'), 10), N), chg('랭킹쪽', 10), cast('쪽갱신'))])
    mgr = text(P, sc, '랭킹담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(),
           ifelse(and_(eq(V('방금등록'), 1), gt(V('내순위'), 0)),
                  [setv('랭킹쪽', add(mul(floor(div(sub(V('내순위'), 1), 10)), 10), 1))], [setv('랭킹쪽', 1)]),
           setv('방금등록', 0), cast('쪽갱신'))
    button(P, sc, '처음으로', '처음으로', 0, -122, 110, 24, 'royal', icon='back', actions=go(ctx['S_TITLE']))
    G.sound_hub(P, sc, 'bgm_title')
    G.fader(P, sc, ctx['BLACK'])


# ================================================================== 파산
def scene_bankrupt(P, ctx):
    sc = ctx['S_BANKRUPT']
    text(P, sc, '저장지움', '', -300, -300, 8, visible=False).on(on_scene(), *SG.clear_blocks())
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '붉은빛', _tint('fx_dark_red2', (8, 0, 4, 205)), 0, 0)
    sprite(P, sc, '경보빛', _edge_glow('fx_alert_red_dim', (150, 10, 30), 150), 0, 0)
    G.big_pop(P, sc, '파산글', K.big_text('파산', 64, 'red'), 0, 70, '파산', hold=99, fade=False)
    t = text(P, sc, '파산설명', '재산이 0원이 되어 더 이상 선거를 치를 수 없습니다.', 0, 24, 12, C_WHITE, F_BODY, True, 0, w=400, h=18,
             visible=False)
    t.on(on_msg('파산'), wait(0.6), show())
    grandpa_say(P, sc, ctx, -150, -60, '엔딩대사', [write(D.GP_BANKRUPT)], scale=0.55, bx=-60, by=-40)
    mgr = text(P, sc, '파산담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), wait(0.4), cast('파산'), wait(1.4), cast('엔딩대사'))
    button(P, sc, '처음으로', '처음으로', 120, -112, 110, 28, 'royal', icon='back', actions=go(ctx['S_TITLE']))
    hub = G.sound_hub(P, sc)
    hub.on(on_msg('파산'), play('fail_big'))
    G.fader(P, sc, ctx['BLACK'])


def build_all(P, ctx):
    scene_event(P, ctx)
    scene_shop(P, ctx)
    scene_vote(P, ctx)
    scene_control(P, ctx)
    scene_rank(P, ctx)
    scene_bankrupt(P, ctx)
