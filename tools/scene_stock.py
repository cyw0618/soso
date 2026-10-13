# -*- coding: utf-8 -*-
"""조치원 증권거래소: 일반 15종목 + 특별 주식 '조치원 지배 자본'.

- 장 시간 동안 1초마다 시세가 움직이고(실시간), 가끔 뉴스(속보/루머)가 떠서 종목에 추세가 생긴다.
- 유세를 한 번 할 때마다 밤사이 시세가 변하고(갭), 장 시간이 늘어나며, 큰아버지들이 지배 자본을 조금씩 사 모은다.
- 지배 자본 지분 50% 이상을 모으면 즉시 '조치원 장악' 승리.

엔트리의 반복 블록은 한 바퀴에 한 프레임이 걸리므로, 시세 계산과 차트 그리기는 반복문을 풀어서 만든다.
"""
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, fmt_comma, fmt_money, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
import data as D
import stock_art as SA

N = len(D.STOCKS) + 1           # 16 (마지막이 지배 자본)
CTL = N
HIST = 30
NAMES = [s[0] for s in D.STOCKS] + [D.CONTROL_NAME]
PRICES = [s[1] for s in D.STOCKS] + [D.CONTROL_PRICE]
VOLS = [s[2] for s in D.STOCKS] + [D.CONTROL_VOL]
SECTORS = [s[3] for s in D.STOCKS] + ['경영권']
FLOORS = [max(0.5, round(p / 20.0, 1)) for p in PRICES[:-1]] + [40]

STOCK_VARS = dict(장시간=D.MARKET_START, 기록위치=1, 채움=1, 첫째주=D.CONTROL_UNCLES[0], 둘째주=D.CONTROL_UNCLES[1],
                  유통주=0, 평가금=0, 지배달성=0, 주문방향=1, 주문수량=1, 매매수량=0, 이번차단=0,
                  뉴스글='', 뉴스종목=0, 뉴스호재=1, 뉴스루머=3, 뉴스진짜=1, 뉴스세기=0, 변동률=0,
                  _s=1, _p=0, _b=0, _k0=0, _mn=0, _mx=0, _v=0, _rg=1, _c=0, _q='', _m='', _a=0, _bb=0, 체결글='')


def setup(P):
    P.list('주식이름', NAMES)
    P.list('주가', PRICES)
    P.list('전주가', PRICES)
    P.list('변동폭', VOLS)
    P.list('업종', SECTORS)
    P.list('변동성표시', ['●' * min(5, max(1, round(v / 4.5))) + '○' * (5 - min(5, max(1, round(v / 4.5)))) for v in VOLS])
    for nm in ('보유', '평단', '추세', '추세남은'):
        P.list(nm, [0] * N)
    P.list('주가기록', [p for p in PRICES for _ in range(HIST)])
    P.list('호재뉴스', D.NEWS_GOOD)
    P.list('악재뉴스', D.NEWS_BAD)
    P.list('지배호재', D.CONTROL_NEWS_GOOD)
    P.list('지배악재', D.CONTROL_NEWS_BAD)


# ------------------------------------------------------------------ 공통 블록
def assets_blocks():
    """평가금(주식 평가액)과 총자산(현금+주식)을 계산."""
    b = [setv('평가금', 0)]
    for i in range(1, N + 1):
        b.append(chg('평가금', mul(LGET('보유', i), LGET('주가', i))))
    b.append(setv('총자산', add(V('돈'), V('평가금'))))
    return b


def reset_blocks():
    b = []
    for i in range(1, N + 1):
        p = PRICES[i - 1]
        b += [lst_set('주가', i, p), lst_set('전주가', i, p), lst_set('보유', i, 0), lst_set('평단', i, 0),
              lst_set('추세', i, 0), lst_set('추세남은', i, 0), lst_set('주가기록', (i - 1) * HIST + 1, p)]
    return b


def _record_blocks():
    b = [setv('기록위치', add(mod(V('기록위치'), HIST), 1)), if_(lt(V('채움'), HIST), chg('채움', 1))]
    for i in range(1, N + 1):
        b.append(lst_set('주가기록', add((i - 1) * HIST, V('기록위치')), LGET('주가', i)))
    return b


def _news_blocks():
    s = V('뉴스종목')
    return [
        if_(le(rnd(1, 100), 14),
            ifelse(le(rnd(1, 100), 10), [setv('뉴스종목', CTL)], [setv('뉴스종목', rnd(1, N - 1))]),
            ifelse(le(rnd(1, 100), 55), [setv('뉴스호재', 1)], [setv('뉴스호재', -1)]),
            ifelse(le(rnd(1, 100), 30), [setv('뉴스루머', 1)], [setv('뉴스루머', 0)]),
            setv('뉴스세기', div(rnd(20, 70), 10)),
            ifelse(eq(V('뉴스루머'), 1),
                   [chg('뉴스세기', mul(V('뉴스세기'), 0.4)),
                    ifelse(le(rnd(1, 100), 50), [setv('뉴스진짜', 1)], [setv('뉴스진짜', 0)])],
                   [ifelse(le(rnd(1, 100), 88), [setv('뉴스진짜', 1)], [setv('뉴스진짜', 0)])]),
            ifelse(eq(V('뉴스진짜'), 1), [lst_set('추세', s, mul(V('뉴스세기'), V('뉴스호재')))],
                   [lst_set('추세', s, mul(mul(V('뉴스세기'), V('뉴스호재')), -0.6))]),
            lst_set('추세남은', s, rnd(4, 8)),
            ifelse(eq(s, CTL),
                   [lst_set('추세', CTL, div(LGET('추세', CTL), 2.5)),
                    ifelse(eq(V('뉴스호재'), 1), [setv('뉴스글', LGET('지배호재', rnd(1, len(D.CONTROL_NEWS_GOOD))))],
                           [setv('뉴스글', LGET('지배악재', rnd(1, len(D.CONTROL_NEWS_BAD))))])],
                   [ifelse(eq(V('뉴스호재'), 1),
                           [setv('뉴스글', join(LGET('주식이름', s), LGET('호재뉴스', rnd(1, len(D.NEWS_GOOD)))))],
                           [setv('뉴스글', join(LGET('주식이름', s), LGET('악재뉴스', rnd(1, len(D.NEWS_BAD)))))])]),
            cast('뉴스')),
    ]


def tick_blocks():
    """장중 1초마다: 16종목 시세 + 기록 + 뉴스."""
    b = [chg('장시간', -1)]
    for i in range(1, N + 1):
        v10 = VOLS[i - 1] * 10
        b += [setv('변동률', mul(div(rnd(-v10, v10), 1000), 0.45)),
              if_(gt(LGET('추세남은', i), 0), chg('변동률', div(LGET('추세', i), 100)),
                  lst_set('추세남은', i, sub(LGET('추세남은', i), 1))),
              lst_set('주가', i, round1(mul(LGET('주가', i), add(1, V('변동률'))))),
              if_(lt(LGET('주가', i), FLOORS[i - 1]), lst_set('주가', i, FLOORS[i - 1]))]
    b += _record_blocks()
    b += _news_blocks()
    b += [if_(eq(V('장시간'), 0), setv('뉴스루머', 2), setv('뉴스글', '오늘 장이 마감됐습니다. 유세를 하면 장이 다시 열려요!'),
              cast('뉴스'))]
    b += assets_blocks()
    return b


def overnight_blocks():
    """유세 1번이 끝날 때(밤사이): 갭 변동, 장 시간 추가, 큰아버지들의 지배 자본 매수."""
    b = []
    for i in range(1, N + 1):
        v10 = VOLS[i - 1] * 10
        b.append(lst_set('전주가', i, LGET('주가', i)))
        if i == CTL:
            b.append(setv('변동률', div(rnd(-15, 30), 1000)))
        else:
            b += [setv('변동률', div(rnd(-v10, int(v10 * 1.1)), 1000)),
                  if_(le(rnd(1, 100), 6), setv('변동률', mul(V('변동률'), 3)))]
        b += [lst_set('주가', i, round1(mul(LGET('주가', i), add(1, V('변동률'))))),
              if_(lt(LGET('주가', i), FLOORS[i - 1]), lst_set('주가', i, FLOORS[i - 1]))]
    b += _record_blocks()
    b += [chg('장시간', D.MARKET_ADD), if_(gt(V('장시간'), D.MARKET_MAX), setv('장시간', D.MARKET_MAX))]
    # 큰아버지들의 지분 매수
    b += [if_(eq(V('이번차단'), 0),
              setv('_a', rnd(200, 900)), setv('_bb', rnd(150, 800)),
              setv('유통주', sub(sub(sub(D.CONTROL_SHARES, LGET('보유', CTL)), V('첫째주')), V('둘째주'))),
              if_(gt(add(V('_a'), V('_bb')), V('유통주')), setv('_a', floor(div(V('유통주'), 2))), setv('_bb', floor(div(V('유통주'), 2)))),
              if_(gt(add(add(V('첫째주'), V('둘째주')), add(V('_a'), V('_bb'))), D.CONTROL_UNCLE_CAP),
                  setv('_a', floor(div(sub(sub(D.CONTROL_UNCLE_CAP, V('첫째주')), V('둘째주')), 2))), setv('_bb', V('_a'))),
              if_(lt(V('_a'), 0), setv('_a', 0), setv('_bb', 0)),
              chg('첫째주', V('_a')), chg('둘째주', V('_bb')),
              lst_set('주가', CTL, round1(mul(LGET('주가', CTL), add(1, mul(div(add(V('_a'), V('_bb')), D.CONTROL_SHARES), D.CONTROL_IMPACT))))))]
    b += assets_blocks()
    return b


def overnight_object(P, sc):
    o = text(P, sc, '주가담당', '', -300, -300, 8, visible=False)
    o.on(on_msg('주가변동'), *overnight_blocks())
    return o


def pct2(expr):
    """주식 수 → 지분 %(소수 둘째 자리)."""
    return div(rounded(div(expr, D.CONTROL_SHARES / 10000.0)), 100)


def change_text(i, o):
    """종목 i 의 등락률을 글상자 o 에 (빨강=오름, 파랑=내림)."""
    return [setv('_c', round1(mul(sub(div(LGET('주가', i), LGET('전주가', i)), 1), 100))),
            ifelse(gt(V('_c'), 0), [write(join('▲', V('_c'), '%')), text_color(C_RED)],
                   [ifelse(lt(V('_c'), 0), [write(join('▼', abs_(V('_c')), '%')), text_color(C_BLUE)],
                           [write('0.0%'), text_color(C_DIM)])])]


# ------------------------------------------------------------------ 장면
def build(P, ctx):
    sc = ctx['S_STOCK']
    ART = ctx['ART']
    G.bg(P, sc, SA.exchange_bg())

    # ---- 위쪽: 현금 / 총자산 / 제목 / 장 시간
    panel(P, sc, '현금판', -172, 118, 128, 24, 'glass')
    sprite(P, sc, '현금아이콘', K.icon_img('coin', 16), -224, 118)
    t = text(P, sc, '현금', '', -160, 118, 11, C_WHITE, F_NUM, False, 1, w=100, h=16)
    t.on(on_scene(), forever(*fmt_money(V('돈'), '_m'), write(join('현금 ', V('_m'))), wait(0.15)))
    panel(P, sc, '총자산판', -172, 95, 128, 22, 'glass')
    sprite(P, sc, '총자산아이콘', K.icon_img('chart', 14), -224, 95)
    t = text(P, sc, '총자산', '', -160, 95, 10, C_ACC, F_NUM, False, 1, w=100, h=15)
    t.on(on_scene(), forever(*fmt_money(V('총자산'), '_m'), write(join('총자산 ', V('_m'))), wait(0.15)))
    sprite(P, sc, '거래소제목', K.banner('조치원 증권거래소', 160, 28, 'royal'), 4, 118)
    panel(P, sc, '장시간판', 170, 118, 130, 24, 'glass')
    sprite(P, sc, '시계', K.icon_img('clock', 15), 118, 118)
    t = text(P, sc, '장시간', '', 178, 118, 10, C_WHITE, F_NUM, False, 1, w=96, h=15)
    t.on(on_scene(), forever(ifelse(gt(V('장시간'), 0), [write(join('장 마감까지 ', V('장시간'), '초')), text_color(C_WHITE)],
                                    [write('장 마감 (유세 후 개장)'), text_color(C_RED)]), wait(0.2)))

    # ---- 뉴스 띠
    sprite(P, sc, '뉴스띠', SA.news_bar(336, 20), 68, 95)
    tag = sprite(P, sc, '뉴스표', [(k, SA.news_tag(k)) for k in ('속보', '루머', '장마감', '시황')], -80, 95)
    news = text(P, sc, '뉴스글', '', 84, 95, 9, C_WHITE, F_BODY, True, 1, w=290, h=14)
    tag_sel = [ifelse(eq(V('뉴스루머'), 0), [shape('속보')], [ifelse(eq(V('뉴스루머'), 1), [shape('루머')],
                                                                   [ifelse(eq(V('뉴스루머'), 2), [shape('장마감')], [shape('시황')])])])]
    tag.on(on_msg('뉴스'), *tag_sel, tag.pct(140), rep(5, tag.grow_pct(-8), wait(0.02)))
    news.on(on_msg('뉴스'), write(V('뉴스글')), lx(96), rep(6, mvx(-2), wait(0.016)))
    news.on(on_scene(), ifelse(gt(V('장시간'), 0),
                               [setv('뉴스루머', 3), setv('뉴스글', '장이 열렸습니다! 뉴스를 보고 사고파세요. 루머는 가짜일 수도 있어요.')],
                               [setv('뉴스루머', 2), setv('뉴스글', '오늘 장은 마감됐어요. 유세를 하면 장이 다시 열립니다.')]),
            cast('뉴스'))

    # ---- 시세판 15칸
    tiles = SA.tile_set()

    def select_actions(i):
        return [setv('선택종목', i), cast('선택변경')]

    for i in range(1, N):
        c, r = (i - 1) % 3, (i - 1) // 3
        x, y = -194 + c * 88, 62 - r * 27
        tile = sprite(P, sc, '시세칸%02d' % i, tiles, x, y)
        st = [ifelse(eq(V('선택종목'), i),
                     [ifelse(gt(LGET('주가', i), LGET('전주가', i)), [shape('us')],
                             [ifelse(lt(LGET('주가', i), LGET('전주가', i)), [shape('ds')], [shape('fs')])])],
                     [ifelse(gt(LGET('주가', i), LGET('전주가', i)), [shape('u')],
                             [ifelse(lt(LGET('주가', i), LGET('전주가', i)), [shape('d')], [shape('f')])])])]
        tile.on(on_msg('시세갱신'), *st)
        tile.on(on_msg('선택변경'), *st)
        tile.on(on_click(), *select_actions(i))
        nm = text(P, sc, '종목명%02d' % i, NAMES[i - 1], x - 1, y + 5, 8, C_WHITE, F_BODY, True, 1, w=70, h=12)
        pr = text(P, sc, '종목가%02d' % i, '', x - 12, y - 6, 8, C_WHITE, F_NUM, False, 1, w=48, h=12)
        ch = text(P, sc, '종목등락%02d' % i, '', x + 18, y - 6, 8, C_DIM, F_NUM, False, 2, w=40, h=12)
        pr.on(on_msg('시세갱신'), write(join(round1(LGET('주가', i)), '만')))
        ch.on(on_msg('시세갱신'), *change_text(i, ch))
        for o in (nm, pr, ch):
            o.on(on_click(), *select_actions(i))

    # ---- 지배 자본 카드
    cx, cy = -106, -86
    card = sprite(P, sc, '지배카드', [('on', SA.control_card(262, 44)), ('sel', SA.control_card(262, 44, True))], cx, cy)
    card.on(on_msg('선택변경'), ifelse(eq(V('선택종목'), CTL), [shape('sel')], [shape('on')]))
    card.on(on_click(), *select_actions(CTL))
    ttl = text(P, sc, '지배이름', '조치원 지배 자본 · 총 1,000억', -155, -72, 9, C_WHITE, F_NUM, False, 1, w=130, h=13)
    cpr = text(P, sc, '지배가격', '', -30, -72, 8, C_WHITE, F_NUM, False, 2, w=96, h=12)
    cpr.on(on_msg('시세갱신'), setv('_c', round1(mul(sub(div(LGET('주가', CTL), LGET('전주가', CTL)), 1), 100))),
           write(join(round1(LGET('주가', CTL)), '만원/주  ', V('_c'), '%')))
    legend = text(P, sc, '지분범례', '', cx, -101, 7, C_DIM, F_BODY, True, 0, w=252, h=11)
    legend.on(on_msg('시세갱신'),
              setv('유통주', sub(sub(sub(D.CONTROL_SHARES, LGET('보유', CTL)), V('첫째주')), V('둘째주'))),
              write(join('나 ', pct2(LGET('보유', CTL)), '%  ·  첫째 ', pct2(V('첫째주')), '%  ·  둘째 ', pct2(V('둘째주')),
                         '%  ·  유통 ', pct2(V('유통주')), '%   (목표 50%)')))
    for o in (ttl, cpr, legend):
        o.on(on_click(), *select_actions(CTL))
    # 지분 막대 (붓으로 그림)
    bx0, bw, by = -226, 240, -88
    bar = sprite(P, sc, '지분막대', K.icon_img('star', 2), bx0, by)
    seg = lambda frac_expr: add(bx0, mul(frac_expr, bw / float(D.CONTROL_SHARES)))
    bar.on(on_msg('시세갱신'),
           pen_up(), pen_clear(), pen_size(7),
           pen_color('#20263f'), xy(bx0, by), pen_down(), xy(bx0 + bw, by), pen_up(),
           setv('_a', LGET('보유', CTL)),
           pen_color('#3d6bff'), xy(bx0, by), pen_down(), xy(seg(V('_a')), by), pen_up(),
           pen_color('#d42a46'), pen_down(), xy(seg(add(V('_a'), V('첫째주'))), by), pen_up(),
           pen_color('#7a46e6'), pen_down(), xy(seg(add(add(V('_a'), V('첫째주')), V('둘째주'))), by), pen_up(),
           xy(-300, -300))
    sprite(P, sc, '목표선', SA.goal_marker(16), bx0 + bw / 2, by)

    # ---- 오른쪽: 선택 종목 상세
    px = 133
    panel(P, sc, '상세판', px, -26, 206, 212, 'glass')
    d_nm = text(P, sc, '상세이름', '', px, 66, 12, C_WHITE, F_NUM, False, 0, w=190, h=18)
    d_sec = text(P, sc, '상세업종', '', px, 53, 8, C_DIM, F_BODY, True, 0, w=190, h=12)
    d_pr = text(P, sc, '상세가격', '', 108, 36, 16, C_WHITE, F_NUM, False, 0, w=130, h=22)
    d_ch = text(P, sc, '상세등락', '', 196, 34, 10, C_DIM, F_NUM, False, 0, w=60, h=15)
    sprite(P, sc, '차트틀', SA.chart_frame(196, 50), px, 6)
    info1 = text(P, sc, '상세정보1', '', px, -30, 9, C_WHITE, F_BODY, True, 0, w=196, h=13)
    info2 = text(P, sc, '상세정보2', '', px, -43, 9, C_DIM, F_BODY, True, 0, w=196, h=13)
    S = V('선택종목')
    detail = [
        d_nm, [write(LGET('주식이름', S))],
        d_sec, [write(join(LGET('업종', S), ' · 변동성 ', LGET('변동성표시', S)))],
        d_pr, [write(join(round1(LGET('주가', S)), '만원'))],
    ]
    for k in range(0, len(detail), 2):
        o, blk = detail[k], detail[k + 1]
        o.on(on_msg('시세갱신'), *blk)
        o.on(on_msg('선택변경'), *blk)
    chg_blk = [setv('_c', round1(mul(sub(div(LGET('주가', S), LGET('전주가', S)), 1), 100))),
               ifelse(gt(V('_c'), 0), [write(join('▲', V('_c'), '%')), text_color(C_RED)],
                      [ifelse(lt(V('_c'), 0), [write(join('▼', abs_(V('_c')), '%')), text_color(C_BLUE)],
                              [write('0.0%'), text_color(C_DIM)])])]
    d_ch.on(on_msg('시세갱신'), *chg_blk)
    d_ch.on(on_msg('선택변경'), *chg_blk)
    i1 = [ifelse(eq(S, CTL),
                 [*fmt_comma(LGET('보유', CTL), '_q'), write(join('내 지분 ', pct2(LGET('보유', CTL)), '%  (', V('_q'), '주)'))],
                 [*fmt_comma(LGET('보유', S), '_q'),
                  write(join('보유 ', V('_q'), '주 · 평단 ', round1(LGET('평단', S)), '만원'))])]
    info1.on(on_msg('시세갱신'), *i1)
    info1.on(on_msg('선택변경'), *i1)
    i2 = [ifelse(eq(S, CTL),
                 [setv('_v', sub(D.CONTROL_GOAL, LGET('보유', CTL))), if_(lt(V('_v'), 0), setv('_v', 0)),
                  *fmt_comma(V('_v'), '_q'), *fmt_money(mul(V('_v'), LGET('주가', CTL)), '_m'),
                  write(join('50%까지 ', V('_q'), '주 · 약 ', V('_m'))), text_color(C_ACC)],
                 [ifelse(gt(LGET('보유', S), 0),
                         [*fmt_money(mul(LGET('보유', S), LGET('주가', S)), '_m'),
                          setv('_c', round1(mul(sub(div(LGET('주가', S), LGET('평단', S)), 1), 100))),
                          ifelse(ge(V('_c'), 0), [write(join('평가 ', V('_m'), '  수익 +', V('_c'), '%')), text_color(C_RED)],
                                 [write(join('평가 ', V('_m'), '  손실 ', V('_c'), '%')), text_color(C_BLUE)])],
                         [write('아직 보유하지 않은 종목이에요'), text_color(C_DIM)])])]
    info2.on(on_msg('시세갱신'), *i2)
    info2.on(on_msg('선택변경'), *i2)

    # 차트 (붓): 최근 30칸, 오래된 것 → 최신
    pen = sprite(P, sc, '차트붓', K.icon_img('star', 2), 0, 0)
    X0, XW, Y0, YH = 41, 184, -13, 38
    dx = XW / float(HIST - 1)
    idx = lambda k: add(V('_b'), add(mod(add(V('기록위치'), k), HIST), 1))
    draw = [pen_up(), pen_clear(), setv('_b', mul(sub(S, 1), HIST)), setv('_k0', sub(HIST, V('채움'))),
            setv('_mn', LGET('주가기록', idx(HIST - 1))), setv('_mx', V('_mn'))]
    for k in range(HIST):
        draw.append(if_(ge(k, V('_k0')), setv('_v', LGET('주가기록', idx(k))),
                        if_(lt(V('_v'), V('_mn')), setv('_mn', V('_v'))), if_(gt(V('_v'), V('_mx')), setv('_mx', V('_v')))))
    draw += [setv('_rg', sub(V('_mx'), V('_mn'))), if_(lt(V('_rg'), mul(V('_mn'), 0.02)), setv('_rg', mul(V('_mn'), 0.02)),
                                                       setv('_mn', sub(V('_mn'), mul(V('_rg'), 0.4)))),
             if_(le(V('_rg'), 0), setv('_rg', 1)),
             ifelse(ge(LGET('주가기록', idx(HIST - 1)), LGET('주가기록', idx(V('_k0')))), [pen_color('#ff3b55')], [pen_color('#3f7bff')]),
             pen_size(2)]
    for k in range(HIST):
        draw.append(if_(ge(k, V('_k0')),
                        xy(add(X0, mul(sub(k, V('_k0')), dx)), add(Y0, mul(div(sub(LGET('주가기록', idx(k)), V('_mn')), V('_rg')), YH))),
                        pen_down()))
    draw += [pen_up(), xy(-300, -300)]
    pen.on(on_msg('시세갱신'), *draw)
    pen.on(on_msg('선택변경'), *draw)

    # 매수/매도 버튼
    def order(direction, qty):
        return [setv('주문방향', direction), setv('주문수량', qty), cast('주문')]
    big = 99999999
    for j, (lbl, dr, q) in enumerate([('매수 1', 1, 1), ('매수 10', 1, 10), ('최대 매수', 1, big)]):
        button(P, sc, '매수버튼%d' % j, lbl, 66 + j * 67, -64, 62, 22, 'red', actions=order(dr, q))
    for j, (lbl, dr, q) in enumerate([('매도 1', -1, 1), ('매도 10', -1, 10), ('전부 매도', -1, big)]):
        button(P, sc, '매도버튼%d' % j, lbl, 66 + j * 67, -89, 62, 22, 'blue', actions=order(dr, q))
    text(P, sc, '단위안내', '1·10은 주 단위 (지배 자본은 100주 단위)', px, -110, 7, C_DIM, F_BODY, True, 0, w=196, h=11)
    note = text(P, sc, '체결알림', '', px, 6, 9, C_WHITE, F_BODY, True, 0, w=186, h=18, visible=False, bg=C_BOX)
    note.on(on_msg('체결'), write(V('체결글')), to_front(), show(), wait(1.3), hide())

    # ---- 아래 버튼
    button(P, sc, '지도로', '지도로', -196, -121, 76, 22, 'navy', icon='back', actions=go(ctx['S_MAP']))
    button(P, sc, '작전본부로', '작전 본부', -112, -121, 84, 22, 'purple', icon='bolt', actions=go(ctx['S_SHOP']))
    text(P, sc, '거래안내', '종목을 눌러 고르고 사고파세요', -10, -121, 8, C_DIM, F_BODY, True, 0, w=110, h=12)

    # ---- 거래 담당 (보이지 않음)
    mgr = text(P, sc, '거래담당', '', -300, -300, 8, visible=False)
    s_ = V('_s')
    buy = [
        setv('매매수량', floor(div(V('돈'), V('_p')))),
        ifelse(eq(s_, CTL),
               [setv('유통주', sub(sub(sub(D.CONTROL_SHARES, LGET('보유', CTL)), V('첫째주')), V('둘째주'))),
                if_(gt(V('매매수량'), V('유통주')), setv('매매수량', V('유통주'))),
                if_(gt(V('매매수량'), mul(V('주문수량'), 100)), setv('매매수량', mul(V('주문수량'), 100)))],
               [if_(gt(V('매매수량'), V('주문수량')), setv('매매수량', V('주문수량')))]),
        ifelse(gt(V('매매수량'), 0),
               [lst_set('평단', s_, div(add(mul(LGET('평단', s_), LGET('보유', s_)), mul(V('_p'), V('매매수량'))),
                                       add(LGET('보유', s_), V('매매수량')))),
                lst_set('보유', s_, add(LGET('보유', s_), V('매매수량'))),
                chg('돈', mul(mul(V('_p'), V('매매수량')), -1)),
                if_(eq(s_, CTL), lst_set('주가', CTL, round1(mul(LGET('주가', CTL),
                                                               add(1, mul(div(V('매매수량'), D.CONTROL_SHARES), D.CONTROL_IMPACT)))))),
                *fmt_comma(V('매매수량'), '_q'), setv('체결글', join('매수 체결!  +', V('_q'), '주'))],
               [setv('체결글', '현금이 부족하거나 살 수 있는 주식이 없어요')])]
    sell = [
        setv('매매수량', LGET('보유', s_)),
        ifelse(eq(s_, CTL), [if_(gt(V('매매수량'), mul(V('주문수량'), 100)), setv('매매수량', mul(V('주문수량'), 100)))],
               [if_(gt(V('매매수량'), V('주문수량')), setv('매매수량', V('주문수량')))]),
        ifelse(gt(V('매매수량'), 0),
               [chg('돈', mul(V('_p'), V('매매수량'))),
                lst_set('보유', s_, sub(LGET('보유', s_), V('매매수량'))),
                if_(eq(LGET('보유', s_), 0), lst_set('평단', s_, 0)),
                if_(eq(s_, CTL), lst_set('주가', CTL, round1(mul(LGET('주가', CTL),
                                                               sub(1, mul(div(V('매매수량'), D.CONTROL_SHARES), D.CONTROL_IMPACT)))))),
                *fmt_comma(V('매매수량'), '_q'), setv('체결글', join('매도 체결!  -', V('_q'), '주'))],
               [setv('체결글', '팔 주식이 없어요')])]
    mgr.on(on_msg('주문'),
           setv('_s', V('선택종목')), setv('_p', LGET('주가', V('_s'))),
           ifelse(eq(V('주문방향'), 1), buy, sell),
           setv('돈', div(rounded(mul(V('돈'), 10)), 10)),
           cast('체결'), *assets_blocks(), cast('시세갱신'),
           if_(ge(LGET('보유', CTL), D.CONTROL_GOAL), setv('지배달성', 1), wait(0.8), *go(ctx['S_CONTROL'])))
    mgr.on(on_scene(), *assets_blocks(), if_(or_(lt(V('선택종목'), 1), gt(V('선택종목'), N)), setv('선택종목', 1)),
           cast('시세갱신'), cast('선택변경'),
           forever(wait(1), if_(gt(V('장시간'), 0), *tick_blocks(), cast('시세갱신'))))
    G.fader(P, sc, ctx['BLACK'])
