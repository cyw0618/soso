# -*- coding: utf-8 -*-
"""조치원 증권거래소: 국내 주식 15 + 해외 주식 6 + 코인 6 + 특별 주식 '조치원 지배 자본'.

- 장 시간 동안 1초마다 시세가 움직이고(실시간), 가끔 뉴스(속보/루머)가 떠서 종목에 추세가 생긴다.
- 해외 주식은 국내보다, 코인은 그보다 훨씬 크게 출렁인다. 코인은 장이 닫혀도 24시간 움직인다.
- 유세를 한 번 할 때마다 밤사이 시세가 변하고(갭), 장 시간이 늘어나며, 큰아버지들이 지배 자본을 조금씩 사 모은다.
- 지배 자본 지분 50% 초과는 승리 조건의 절반 (지지율 50% 초과와 함께 있어야 군수).

종목 번호: 1~15 국내, 16 지배 자본, 17~22 해외, 23~28 코인.
엔트리의 반복 블록은 한 바퀴에 한 프레임이 걸리므로, 시세 계산과 차트 그리기는 반복문을 풀어서 만든다.
"""
import math
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, fmt_comma, fmt_money, fmt_price, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
import data as D
import data2 as D2
import stock_art as SA

ND = len(D.STOCKS)              # 15 국내
CTL = ND + 1                    # 16 지배 자본
FOR0 = CTL                      # 해외는 17~
COIN0 = CTL + len(D.FOREIGN)    # 코인은 23~
SPEC0 = COIN0 + len(D.COINS)    # 특별주는 29~
LEV0 = SPEC0 + len(D2.SPECIALS)  # (예전 레버리지 상품 자리 — 지금은 종목마다 인버스·레버리지 주문 모드가 있다)
N = LEV0                         # 34
HIST = 30
ALL = list(D.STOCKS) + [(D.CONTROL_NAME, D.CONTROL_PRICE, D.CONTROL_VOL, '경영권')] + list(D.FOREIGN) + list(D.COINS) + \
    [(nm, p, 99, '특별주 · 코인의 %d배 출렁임' % (100 if t == 2 else 500)) for nm, p, t in D2.SPECIALS]
SPEC_IDX = [SPEC0 + i for i in range(1, len(D2.SPECIALS) + 1)]
EXP_K = 60                      # 특별주 상태 -60~60 → 가격 × e^(상태/10)
NAMES = [s[0] for s in ALL]
PRICES = [s[1] for s in ALL]
VOLS = [s[2] for s in ALL]
SECTORS = [s[3] for s in ALL]
KIND = [1] * ND + [0] + [2] * len(D.FOREIGN) + [3] * len(D.COINS) + [4] * len(D2.SPECIALS)
# 1 국내, 0 지배, 2 해외, 3 코인, 4 특별
FLOORS = [max(0.0001, round(p / (60.0 if k == 3 else 20.0), 4)) if k else 40 for p, k in zip(PRICES, KIND)]
COIN_IDX = [i for i in range(1, N + 1) if KIND[i - 1] == 3]
TABS = [('국내', 0, ND), ('해외', FOR0, len(D.FOREIGN)), ('코인', COIN0, len(D.COINS)), ('특별주', SPEC0, len(D2.SPECIALS))]
BTC = COIN0 + 1                 # 비트코인

STOCK_VARS = dict(장시간=D.MARKET_START, 기록위치=1, 채움=1, 첫째주=D.CONTROL_UNCLES[0], 둘째주=D.CONTROL_UNCLES[1],
                  유통주=0, 평가금=0, 지배달성=0, 주문방향=1, 주문수량=1, 매매수량=0, 이번차단=0,
                  뉴스글='', 뉴스종목=0, 뉴스호재=1, 뉴스루머=3, 뉴스진짜=1, 뉴스세기=0, 변동률=0, 탭=1, 탭기준=0, 탭개수=ND,
                  체결성공=0, _po=0, _rd=0, _rf=0, _rb=1, _lr=0, _lf=1, _lk=0, _pv=0, _ph=0, _pl=0, _pc='', _pt='', _s=1, _p=0, _b=0, _k0=0, _mn=0, _mx=0, _v=0, _rg=1, _c=0, _q='', _m='', _a=0, _bb=0, 체결글='', _ml='')


def round2(x):
    """가격 저장용 반올림 (만원 단위 소수 넷째 자리 = 1원 단위)."""
    return div(rounded(mul(x, 10000)), 10000)


def setup(P):
    global _P
    _P = P
    _FN.clear()
    P.list('주식이름', NAMES)
    P.list('주가', PRICES)
    P.list('전주가', PRICES)
    P.list('변동폭', VOLS)
    P.list('업종', SECTORS)
    P.list('변동성표시', [('●' * min(5, max(1, round(v / 9.0))) + '○' * (5 - min(5, max(1, round(v / 9.0))))) if k != 4 else '★★★★★'
                         for v, k in zip(VOLS, KIND)])
    for nm in ('보유', '평단', '추세', '추세남은'):
        P.list(nm, [0] * N)
    P.list('주가기록', [p for p in PRICES for _ in range(HIST)])
    P.list('배수', [1] * N)          # 종목별 주문 모드: 1 일반, -1 인버스, 2·5·10 레버리지(코인·특별주), -2·-5·-10 인버스 레버리지
    P.list('상품가', PRICES)
    P.list('특별X', [0] * len(D2.SPECIALS))
    P.list('특별단계', [t for _, _, t in D2.SPECIALS])
    P.list('특별기준', [p for _, p, _ in D2.SPECIALS])
    P.list('지수표', [round(math.exp(k / 10.0), 6) for k in range(-EXP_K, EXP_K + 1)])
    P.list('호재뉴스', D.NEWS_GOOD)
    P.list('악재뉴스', D.NEWS_BAD)
    P.list('코인호재', D.COIN_NEWS_GOOD)
    P.list('코인악재', D.COIN_NEWS_BAD)
    P.list('해외호재', D.FOREIGN_NEWS_GOOD)
    P.list('해외악재', D.FOREIGN_NEWS_BAD)
    P.list('지배호재', D.CONTROL_NEWS_GOOD)
    P.list('지배악재', D.CONTROL_NEWS_BAD)


# ------------------------------------------------------------------ 공통 블록
_P = None
_FN = {}


def _shared(name, make_body):
    """같은 코드를 엔트리 함수 하나로 두고 여러 곳에서 부르기만 한다 (블록 수·작품 용량 절약)."""
    if _P is None:
        return make_body()
    if name not in _FN:
        _FN[name] = _P.new_function(name, make_body())
    return [dict(_FN[name])]


def _assets_body():
    b = list(_price_body())
    b.append(setv('평가금', 0))
    for i in range(1, N + 1):
        b.append(chg('평가금', mul(LGET('보유', i), LGET('상품가', i))))
    # 해외 투자자에게 갚아야 할 돈은 빚이라 총자산에서 뺀다
    debt = add(add(LGET('투자부채', 1), LGET('투자부채', 2)), LGET('투자부채', 3))
    b.append(setv('총자산', add(sub(add(V('돈'), V('평가금')), debt), V('투자자산'))))
    b.append(if_(eq(V('회사상태'), 1), chg('총자산', V('회사가치'))))
    return b


def _save():
    import savegame as SG
    return [if_(eq(V('체결성공'), 1), *SG.save_blocks())]


def assets_blocks():
    """평가금(주식·코인 평가액 = 보유 × 상품가)과 총자산(현금+평가금)을 계산."""
    return _shared('자산계산', _assets_body)


def _price_body():
    """종목마다 '상품가'(내 포지션 1주의 가치)를 구한다: 평단 + 배수 × (현재가 − 평단).
    배수 1 = 그냥 사기, 음수 = 인버스, 2·5·10 = 레버리지 (코인·특별주). 0 밑으로는 내려가지 않는다 (강제청산)."""
    b = []
    for i in range(1, N + 1):
        b.append(ifelse(gt(LGET('보유', i), 0),
                        [lst_set('상품가', i, add(LGET('평단', i), mul(LGET('배수', i), sub(LGET('주가', i), LGET('평단', i))))),
                         if_(lt(LGET('상품가', i), 0), lst_set('상품가', i, 0))],
                        [lst_set('상품가', i, LGET('주가', i))]))
    return b


def reset_blocks():
    b = []
    for i in range(1, N + 1):
        p = PRICES[i - 1]
        b += [lst_set('주가', i, p), lst_set('전주가', i, p), lst_set('보유', i, 0), lst_set('평단', i, 0),
              lst_set('배수', i, 1), lst_set('상품가', i, p),
              lst_set('추세', i, 0), lst_set('추세남은', i, 0), lst_set('주가기록', (i - 1) * HIST + 1, p)]
    b += [lst_set('특별X', i, 0) for i in range(1, len(D2.SPECIALS) + 1)]
    b += [lst_set('주식이름', CTL, D2.CONTROL_NAMES[0])]
    return b


def _record_blocks():
    b = [setv('기록위치', add(mod(V('기록위치'), HIST), 1)), if_(lt(V('채움'), HIST), chg('채움', 1))]
    for i in range(1, N + 1):
        b.append(lst_set('주가기록', add((i - 1) * HIST, V('기록위치')), LGET('주가', i)))
    return b


def _news_blocks(coins_only=False):
    s = V('뉴스종목')
    if coins_only:
        pick = [setv('뉴스종목', rnd(COIN0 + 1, SPEC0))]
    else:
        pick = [ifelse(le(rnd(1, 100), 8), [setv('뉴스종목', CTL)],
                       [setv('뉴스종목', rnd(1, SPEC0 - 1)), if_(ge(V('뉴스종목'), CTL), chg('뉴스종목', 1))])]
    return [
        if_(le(rnd(1, 100), 16),
            *pick,
            ifelse(le(rnd(1, 100), 52), [setv('뉴스호재', 1)], [setv('뉴스호재', -1)]),
            ifelse(le(rnd(1, 100), 30), [setv('뉴스루머', 1)], [setv('뉴스루머', 0)]),
            setv('뉴스세기', div(rnd(30, 95), 10)),
            if_(gt(s, COIN0), chg('뉴스세기', mul(V('뉴스세기'), 0.25))),
            ifelse(eq(V('뉴스루머'), 1),
                   [chg('뉴스세기', mul(V('뉴스세기'), 0.4)),
                    ifelse(le(rnd(1, 100), 50), [setv('뉴스진짜', 1)], [setv('뉴스진짜', 0)])],
                   [ifelse(le(rnd(1, 100), 85), [setv('뉴스진짜', 1)], [setv('뉴스진짜', 0)])]),
            ifelse(eq(V('뉴스진짜'), 1), [lst_set('추세', s, mul(V('뉴스세기'), V('뉴스호재')))],
                   [lst_set('추세', s, mul(mul(V('뉴스세기'), V('뉴스호재')), -0.6))]),
            lst_set('추세남은', s, rnd(4, 8)),
            ifelse(eq(s, CTL),
                   [lst_set('추세', CTL, div(LGET('추세', CTL), 2.5)),
                    ifelse(eq(V('뉴스호재'), 1), [setv('뉴스글', LGET('지배호재', rnd(1, len(D.CONTROL_NEWS_GOOD))))],
                           [setv('뉴스글', LGET('지배악재', rnd(1, len(D.CONTROL_NEWS_BAD))))])],
                   [ifelse(gt(s, COIN0),
                           [ifelse(eq(V('뉴스호재'), 1),
                                   [setv('뉴스글', join(LGET('주식이름', s), LGET('코인호재', rnd(1, len(D.COIN_NEWS_GOOD)))))],
                                   [setv('뉴스글', join(LGET('주식이름', s), LGET('코인악재', rnd(1, len(D.COIN_NEWS_BAD)))))])],
                           [ifelse(gt(s, FOR0),
                                   [ifelse(eq(V('뉴스호재'), 1),
                                           [setv('뉴스글', join(LGET('주식이름', s), LGET('해외호재', rnd(1, len(D.FOREIGN_NEWS_GOOD)))))],
                                           [setv('뉴스글', join(LGET('주식이름', s), LGET('해외악재', rnd(1, len(D.FOREIGN_NEWS_BAD)))))])],
                                   [ifelse(eq(V('뉴스호재'), 1),
                                           [setv('뉴스글', join(LGET('주식이름', s), LGET('호재뉴스', rnd(1, len(D.NEWS_GOOD)))))],
                                           [setv('뉴스글', join(LGET('주식이름', s), LGET('악재뉴스', rnd(1, len(D.NEWS_BAD)))))])])])]),
            cast('뉴스')),
    ]


def _move(i, mult):
    v10 = VOLS[i - 1] * 10
    return [setv('변동률', mul(div(rnd(-v10, v10), 1000), mult)),
            if_(gt(LGET('추세남은', i), 0), chg('변동률', div(LGET('추세', i), 100)),
                lst_set('추세남은', i, sub(LGET('추세남은', i), 1))),
            lst_set('주가', i, round2(mul(LGET('주가', i), add(1, V('변동률'))))),
            if_(lt(LGET('주가', i), FLOORS[i - 1]), lst_set('주가', i, FLOORS[i - 1]))]


def _track(i, acc, moves):
    """종목 i 를 움직이기 전후 가격 비율을 acc 에 더한다 (지수 계산용)."""
    return [setv('_po', LGET('주가', i))] + moves + [chg(acc, div(LGET('주가', i), V('_po')))]


def _index_reset():
    return [setv('_rd', ND), setv('_rf', len(D.FOREIGN)), setv('_rb', 1)]


def special_blocks():
    """특별주: 평균으로 돌아가려는 힘 + 아주 큰 흔들림 (시장 단계 종목은 코인의 100배, 대통령 단계 종목은 500배)."""
    b = []
    for j, (nm, base, t) in enumerate(D2.SPECIALS, 1):
        a = D2.SPECIAL_SWING[t]
        s = SPEC0 + j
        b += [lst_set('특별X', j, rounded(add(mul(LGET('특별X', j), D2.SPECIAL_REVERT), rnd(-a, a)))),
              if_(gt(LGET('특별X', j), EXP_K), lst_set('특별X', j, EXP_K)),
              if_(lt(LGET('특별X', j), -EXP_K), lst_set('특별X', j, -EXP_K)),
              lst_set('주가', s, round2(mul(base, LGET('지수표', add(LGET('특별X', j), EXP_K + 1)))))]
    return b


def tick_blocks():
    """장중 1초마다: 모든 종목 시세 + 기록 + 뉴스 + 작전 세력."""
    import economy as EC
    b = [chg('장시간', -1), *_index_reset(), setv('_rd', 0), setv('_rf', 0)]
    for i in range(1, SPEC0 + 1):
        k = KIND[i - 1]
        if k == 1:
            b += _track(i, '_rd', _move(i, D.STOCK_TICK))
        elif k == 2:
            b += _track(i, '_rf', _move(i, D.STOCK_TICK))
        elif i == BTC:
            b += [setv('_rb', 0)] + _track(i, '_rb', _move(i, D.STOCK_TICK))
        else:
            b += _move(i, D.STOCK_TICK)
    b += special_blocks()
    b += EC.ops_tick_blocks()
    b += _record_blocks()
    b += _news_blocks()
    b += [if_(eq(V('장시간'), 0), setv('뉴스루머', 2), setv('뉴스글', '주식 장이 마감됐어요. 코인은 24시간 움직입니다!'),
              cast('뉴스'))]
    b += assets_blocks()
    return b


def coin_tick_blocks():
    """장이 닫혔을 때: 코인만 1초마다 움직인다."""
    b = [*_index_reset()]
    for i in COIN_IDX:
        if i == BTC:
            b += [setv('_rb', 0)] + _track(i, '_rb', _move(i, D.STOCK_TICK))
        else:
            b += _move(i, D.STOCK_TICK)
    b += special_blocks()
    b += _record_blocks()
    b += _news_blocks(coins_only=True)
    b += assets_blocks()
    return b


def overnight_blocks():
    """유세 1번이 끝날 때(밤사이): 갭 변동, 장 시간 추가, 큰아버지들의 지배 자본 매수."""
    b = [*_index_reset(), setv('_rd', 0), setv('_rf', 0), setv('_rb', 0)]
    for i in range(1, N + 1):
        v10 = VOLS[i - 1] * 10
        k = KIND[i - 1]
        b.append(lst_set('전주가', i, LGET('주가', i)))
        if k == 4:
            continue
        b.append(setv('_po', LGET('주가', i)))
        if k == 0:
            b.append(setv('변동률', div(rnd(-25, 40), 1000)))
        elif k == 3:
            b += [setv('변동률', div(rnd(int(-v10 * 0.6), int(v10 * 0.66)), 1000))]
        else:
            b += [setv('변동률', div(rnd(-v10, int(v10 * 1.1)), 1000)),
                  if_(le(rnd(1, 100), 6), setv('변동률', mul(V('변동률'), 2.5)))]
        b += [lst_set('주가', i, round2(mul(LGET('주가', i), add(1, V('변동률'))))),
              if_(lt(LGET('주가', i), FLOORS[i - 1]), lst_set('주가', i, FLOORS[i - 1]))]
        acc = '_rd' if k == 1 else ('_rf' if k == 2 else ('_rb' if i == BTC else None))
        if acc:
            b.append(chg(acc, div(LGET('주가', i), V('_po'))))
    b += special_blocks()
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
              lst_set('주가', CTL, round2(mul(LGET('주가', CTL), add(1, mul(div(add(V('_a'), V('_bb')), D.CONTROL_SHARES), D.CONTROL_IMPACT))))))]
    b += assets_blocks()
    return b


def overnight_object(P, sc):
    o = text(P, sc, '주가담당', '', -300, -300, 8, visible=False)
    o.on(on_msg('주가변동'), *overnight_blocks())
    return o


def pct2(expr):
    """주식 수 → 지분 %(소수 둘째 자리)."""
    return div(rounded(div(expr, D.CONTROL_SHARES / 10000.0)), 100)


def change_blocks(i):
    """종목 i 의 등락률을 글로 (빨강=오름, 파랑=내림)."""
    return [setv('_c', round1(mul(sub(div(LGET('주가', i), LGET('전주가', i)), 1), 100))),
            ifelse(gt(V('_c'), 0), [write(join('▲', V('_c'), '%')), text_color(C_RED)],
                   [ifelse(lt(V('_c'), 0), [write(join('▼', abs_(V('_c')), '%')), text_color(C_BLUE)],
                           [write('0.0%'), text_color(C_DIM)])])]


# ------------------------------------------------------------------ 장면
def build(P, ctx):
    import empire as E
    sc = ctx['S_STOCK']
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
                                    [write('주식 마감 · 코인만 거래'), text_color(C_RED)]), wait(0.2)))

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
                               [setv('뉴스루머', 2), setv('뉴스글', '주식 장은 마감. 코인은 24시간 움직여요. 유세를 하면 장이 다시 열립니다.')]),
            cast('뉴스'))

    def select_actions(idx_expr):
        return [setv('선택종목', idx_expr), cast('선택변경')]

    # ---- 조치원 지배 자본 카드 (크게, 맨 위)
    cx, cy = -106, 47
    card = sprite(P, sc, '지배카드', [('on', SA.control_card(262, 46)), ('sel', SA.control_card(262, 46, True))], cx, cy)
    card.on(on_msg('선택변경'), ifelse(eq(V('선택종목'), CTL), [shape('sel')], [shape('on')]))
    card.on(on_scene(), forever(rep(15, fx_add('brightness', 1), wait(0.04)), rep(15, fx_add('brightness', -1), wait(0.04))))
    card.on(on_click(), *select_actions(CTL))
    ttl = text(P, sc, '지배이름', '조치원 지배 자본 (총 1,000억)', -150, 61, 10, C_WHITE, F_NUM, False, 1, w=150, h=14)
    ttl.on(on_scene(), write(join(LGET('주식이름', CTL), ' (총 ', LGET('지배총액', V('단계')), ')')))
    mine = text(P, sc, '지배내지분', '', -10, 61, 11, C_ACC, F_NUM, False, 2, w=80, h=14)
    mine.on(on_msg('시세갱신'), write(join('내 지분 ', E.stake_pct(), '%')))
    cpr = text(P, sc, '지배가격', '', -106, 30, 8, C_DIM, F_BODY, True, 0, w=252, h=12)
    cpr.on(on_msg('시세갱신'),
           setv('유통주', sub(sub(sub(D.CONTROL_SHARES, LGET('보유', CTL)), V('첫째주')), V('둘째주'))),
           *fmt_price(LGET('주가', CTL), '_pt'),
           write(join(V('_pt'), '/주  ·  첫째 ', pct2(V('첫째주')), '%  ·  둘째 ', pct2(V('둘째주')),
                      '%  ·  유통 ', pct2(V('유통주')), '%')))
    for o in (ttl, mine, cpr):
        o.on(on_click(), *select_actions(CTL))
    bx0, bw, by = -226, 240, 45
    bar = sprite(P, sc, '지분막대', K.icon_img('star', 2), bx0, by)
    seg = lambda frac_expr: add(bx0, mul(frac_expr, bw / float(D.CONTROL_SHARES)))
    bar.on(on_msg('시세갱신'),
           pen_up(), pen_clear(), pen_size(9),
           pen_color('#20263f'), xy(bx0, by), pen_down(), xy(bx0 + bw, by), pen_up(),
           setv('_a', LGET('보유', CTL)),
           pen_color('#3d6bff'), xy(bx0, by), pen_down(), xy(seg(V('_a')), by), pen_up(),
           pen_color('#d42a46'), pen_down(), xy(seg(add(V('_a'), V('첫째주'))), by), pen_up(),
           pen_color('#7a46e6'), pen_down(), xy(seg(add(add(V('_a'), V('첫째주')), V('둘째주'))), by), pen_up(),
           xy(-300, -300))
    gm = sprite(P, sc, '목표선', SA.goal_marker(18), bx0 + bw / 2, by)
    gm.on(on_click(), *select_actions(CTL))
    text(P, sc, '목표글', '50%', bx0 + bw / 2 + 12, by + 8, 7, C_WHITE, F_NUM, False, 0, w=24, h=10)

    # ---- 탭: 국내 / 해외 / 코인
    for k, (lbl, base, cnt) in enumerate(TABS, 1):
        col = 'red' if k == 4 else ('purple' if k == 5 else 'royal')
        tb = sprite(P, sc, '탭%d' % k, [('off', K.badge(lbl, 50, 18, 'navy')), ('on', K.badge(lbl, 50, 18, col))],
                    -208 + (k - 1) * 52, 77)
        tb.on(on_msg('탭변경'), ifelse(eq(V('탭'), k), [shape('on'), tb.pct(108)], [shape('off'), tb.pct(100)]))
        act = [setv('탭', k), setv('탭기준', base), setv('탭개수', cnt), setv('선택종목', base + 1),
               cast('탭변경'), cast('시세갱신'), cast('선택변경')]
        if k == 4:
            tb.on(on_scene(), ifelse(ge(V('단계'), 2), [show()], [hide()]))
            act = [if_(ge(V('단계'), 2), *act)]
        tb.on(on_click(), *act)

    # ---- 시세판 (탭에 따라 종목이 바뀜, 최대 15칸)
    tiles = SA.tile_set()
    for j in range(1, ND + 1):
        c, r = (j - 1) % 3, (j - 1) // 3
        x, y = -194 + c * 88, 7 - r * 25
        idx = add(V('탭기준'), j)
        on_tab = le(j, V('탭개수'))
        tile = sprite(P, sc, '시세칸%02d' % j, tiles, x, y)
        st = [ifelse(on_tab, [show(),
                              ifelse(eq(V('선택종목'), idx),
                                     [ifelse(gt(LGET('주가', idx), LGET('전주가', idx)), [shape('us')],
                                             [ifelse(lt(LGET('주가', idx), LGET('전주가', idx)), [shape('ds')], [shape('fs')])])],
                                     [ifelse(gt(LGET('주가', idx), LGET('전주가', idx)), [shape('u')],
                                             [ifelse(lt(LGET('주가', idx), LGET('전주가', idx)), [shape('d')], [shape('f')])])])],
                     [hide()])]
        for m in ('시세갱신', '선택변경', '탭변경'):
            tile.on(on_msg(m), *st)
        nm = text(P, sc, '종목명%02d' % j, '', x - 1, y + 5, 8, C_WHITE, F_BODY, True, 1, w=70, h=12)
        pr = text(P, sc, '종목가%02d' % j, '', x - 12, y - 6, 8, C_WHITE, F_NUM, False, 1, w=48, h=12)
        ch = text(P, sc, '종목등락%02d' % j, '', x + 18, y - 6, 8, C_DIM, F_NUM, False, 2, w=40, h=12)
        nm.on(on_msg('탭변경'), ifelse(on_tab, [write(LGET('주식이름', idx)), show()], [hide()]))
        pr.on(on_msg('시세갱신'), ifelse(on_tab, [*fmt_price(LGET('주가', idx), '_pt', short=True), write(V('_pt')), show()], [hide()]))
        ch.on(on_msg('시세갱신'), ifelse(on_tab, [*change_blocks(idx), show()], [hide()]))
        for o in (tile, nm, pr, ch):
            o.on(on_click(), if_(on_tab, *select_actions(idx)))

    # ---- 오른쪽: 선택 종목 상세
    px = 133
    panel(P, sc, '상세판', px, -26, 206, 212, 'glass')
    d_nm = text(P, sc, '상세이름', '', px, 66, 12, C_WHITE, F_NUM, False, 0, w=190, h=18)
    d_sec = text(P, sc, '상세업종', '', px, 53, 8, C_DIM, F_BODY, True, 0, w=190, h=12)
    d_pr = text(P, sc, '상세가격', '', 108, 36, 16, C_WHITE, F_NUM, False, 0, w=130, h=22)
    d_ch = text(P, sc, '상세등락', '', 196, 34, 10, C_DIM, F_NUM, False, 0, w=60, h=15)
    sprite(P, sc, '차트틀', SA.chart_frame(196, 50), px, 6)
    info1 = text(P, sc, '상세정보1', '', px, -29, 9, C_WHITE, F_BODY, True, 0, w=196, h=13)
    info2 = text(P, sc, '상세정보2', '', px, -41, 9, C_DIM, F_BODY, True, 0, w=196, h=13)
    S = V('선택종목')
    detail = [
        d_nm, [write(LGET('주식이름', S))],
        d_sec, [write(join(LGET('업종', S), ' · 변동성 ', LGET('변동성표시', S)))],
        d_pr, [*fmt_price(LGET('주가', S), '_pt'), write(V('_pt'))],
    ]
    for k in range(0, len(detail), 2):
        o, blk = detail[k], detail[k + 1]
        o.on(on_msg('시세갱신'), *blk)
        o.on(on_msg('선택변경'), *blk)
    d_ch.on(on_msg('시세갱신'), *change_blocks(S))
    d_ch.on(on_msg('선택변경'), *change_blocks(S))
    D_ = LGET('배수', S)
    mode_lbl = [ifelse(eq(D_, 1), [setv('_ml', '일반')],
                       [ifelse(eq(D_, -1), [setv('_ml', '인버스')],
                               [ifelse(gt(D_, 0), [setv('_ml', join('레버리지 ×', D_))], [setv('_ml', join('인버스 ×', abs_(D_)))])])])]
    i1 = [ifelse(eq(S, CTL),
                 [*fmt_comma(LGET('보유', CTL), '_q'), write(join('내 지분 ', pct2(LGET('보유', CTL)), '%  (', V('_q'), '주)'))],
                 [*mode_lbl, *fmt_comma(LGET('보유', S), '_q'),
                  *fmt_price(LGET('평단', S), '_pt'),
                  write(join('보유 ', V('_q'), LGET('단위', ifelse_kind(S)), ' · 평단 ', V('_pt'), ' · ', V('_ml')))])]
    info1.on(on_msg('시세갱신'), *i1)
    info1.on(on_msg('선택변경'), *i1)
    i2 = [ifelse(eq(S, CTL),
                 [setv('_v', sub(D.CONTROL_GOAL + 1, LGET('보유', CTL))), if_(lt(V('_v'), 0), setv('_v', 0)),
                  *fmt_comma(V('_v'), '_q'), *fmt_money(mul(V('_v'), LGET('주가', CTL)), '_m'),
                  write(join('과반까지 ', V('_q'), '주 · 약 ', V('_m'))), text_color(C_ACC)],
                 [ifelse(gt(LGET('보유', S), 0),
                         [*fmt_money(mul(LGET('보유', S), LGET('상품가', S)), '_m'),
                          setv('_c', round1(mul(sub(div(LGET('상품가', S), LGET('평단', S)), 1), 100))),
                          ifelse(ge(V('_c'), 0), [write(join('평가 ', V('_m'), '  수익 +', V('_c'), '%')), text_color(C_RED)],
                                 [write(join('평가 ', V('_m'), '  손실 ', V('_c'), '%')), text_color(C_BLUE)])],
                         [*mode_lbl, write(join('아직 없어요 · 주문 모드: ', V('_ml'))), text_color(C_DIM)])])]
    info2.on(on_msg('시세갱신'), *i2)
    info2.on(on_msg('선택변경'), *i2)
    P.list('단위', ['주', '주', '주', '개'])     # ifelse_kind: 1 국내/지배, 2 해외, 3 국내, 4 코인

    # 차트 (붓): 최근 30칸, 오래된 것 → 최신
    pen = sprite(P, sc, '차트붓', K.icon_img('star', 2), 0, 0)
    X0, XW, Y0, YH = 41, 184, -13, 38
    dx = XW / float(HIST - 1)
    idx_h = lambda k: add(V('_b'), add(mod(add(V('기록위치'), k), HIST), 1))
    draw = [pen_up(), pen_clear(), setv('_b', mul(sub(S, 1), HIST)), setv('_k0', sub(HIST, V('채움'))),
            setv('_mn', LGET('주가기록', idx_h(HIST - 1))), setv('_mx', V('_mn'))]
    for k in range(HIST):
        draw.append(if_(ge(k, V('_k0')), setv('_v', LGET('주가기록', idx_h(k))),
                        if_(lt(V('_v'), V('_mn')), setv('_mn', V('_v'))), if_(gt(V('_v'), V('_mx')), setv('_mx', V('_v')))))
    draw += [setv('_rg', sub(V('_mx'), V('_mn'))), if_(lt(V('_rg'), mul(V('_mn'), 0.02)), setv('_rg', mul(V('_mn'), 0.02)),
                                                       setv('_mn', sub(V('_mn'), mul(V('_rg'), 0.4)))),
             if_(le(V('_rg'), 0), setv('_rg', 1)),
             ifelse(ge(LGET('주가기록', idx_h(HIST - 1)), LGET('주가기록', idx_h(V('_k0')))), [pen_color('#ff3b55')], [pen_color('#3f7bff')]),
             pen_size(2)]
    for k in range(HIST):
        draw.append(if_(ge(k, V('_k0')),
                        xy(add(X0, mul(sub(k, V('_k0')), dx)), add(Y0, mul(div(sub(LGET('주가기록', idx_h(k)), V('_mn')), V('_rg')), YH))),
                        pen_down()))
    draw += [pen_up(), xy(-300, -300)]
    pen.on(on_msg('시세갱신'), *draw)
    pen.on(on_msg('선택변경'), *draw)

    # 매수/매도 버튼
    def order(direction, qty):
        return [setv('주문방향', direction), setv('주문수량', qty), cast('주문')]
    big = 99999999
    for j, (lbl, dr, q) in enumerate([('매수 1', 1, 1), ('매수 10', 1, 10), ('최대 매수', 1, big)]):
        button(P, sc, '매수버튼%d' % j, lbl, 66 + j * 67, -76, 62, 22, 'red', actions=order(dr, q))
    for j, (lbl, dr, q) in enumerate([('매도 1', -1, 1), ('매도 10', -1, 10), ('전부 매도', -1, big)]):
        button(P, sc, '매도버튼%d' % j, lbl, 66 + j * 67, -100, 62, 22, 'blue', actions=order(dr, q))
    # ---- 주문 모드 (일반/인버스 + 코인·특별주는 레버리지 ×2·×5·×10): 보유 중에는 바꿀 수 없다
    def mode_btn(name, label, w, x, shown, lit, click):
        o = sprite(P, sc, name, [('off', K.badge(label, w, 15, 'navy')), ('on', K.badge(label, w, 15, 'royal'))], x, -55)
        upd = [ifelse(shown, [show(), ifelse(lit, [shape('on')], [shape('off')])], [hide()])]
        o.on(on_msg('선택변경'), *upd)
        o.on(on_msg('모드변경'), *upd)
        o.on(on_scene(), hide())
        o.on(on_click(), if_(and_(shown, eq(V('게임중'), 0)),
                             ifelse(gt(LGET('보유', S), 0),
                                    [setv('체결글', '보유 중에는 주문 모드를 바꿀 수 없어요 (먼저 정리)'), setv('체결성공', 0), cast('체결')],
                                    [*click, cast('모드변경')])))
        return o
    dd = LGET('배수', S)
    not_ctl = ne(S, CTL)
    levable = gt(S, COIN0)          # 코인(23~)·특별주만 레버리지
    sgn = ifelse(lt(dd, 0), [lst_set('배수', S, -1)], [lst_set('배수', S, 1)])
    mode_btn('모드롱', '일반', 34, 48, not_ctl, gt(dd, 0), [lst_set('배수', S, abs_(dd))])
    mode_btn('모드인버스', '인버스', 42, 92, not_ctl, lt(dd, 0), [lst_set('배수', S, mul(abs_(dd), -1))])
    for k_, w_, x_ in ((1, 26, 136), (2, 26, 163), (5, 26, 190), (10, 30, 219)):
        mode_btn('모드배%d' % k_, '×%d' % k_, w_, x_, and_(not_ctl, or_(eq(k_, 1), levable)), eq(abs_(dd), k_),
                 [ifelse(lt(dd, 0), [lst_set('배수', S, -k_)], [lst_set('배수', S, k_)])])
    text(P, sc, '단위안내', '1·10은 주(코인은 개) 단위 · 지배 자본은 100주 단위', px, -119, 7, C_DIM, F_BODY, True, 0, w=200, h=11)
    note = text(P, sc, '체결알림', '', px, 6, 9, C_WHITE, F_BODY, True, 0, w=186, h=18, visible=False, bg=C_BOX)
    note.on(on_msg('체결'), write(V('체결글')), to_front(), show(), wait(1.3), hide())

    # ---- 아래 버튼
    button(P, sc, '지도로', '돌아가기', -196, -121, 76, 22, 'navy', icon='back', actions=ctx['GO_HOME']())
    nego = button(P, sc, '협상으로', '협상 테이블', -104, -121, 96, 22, 'red', icon='bolt', actions=go(ctx['S_NEGO']))
    nego.on(on_scene(), ifelse(eq(V('단계'), 1), [show()], [hide()]))
    opsb = button(P, sc, '작전세력으로', '작전 세력', -104, -121, 96, 22, 'purple', icon='bolt', actions=go(ctx['S_OPS']))
    opsb.on(on_scene(), ifelse(and_(gt(V('단계'), 1), ge(V('직위'), 1)), [show()], [hide()]))
    opst = text(P, sc, '작전표시', '', 20, -121, 8, C_VIOLET, F_NUM, False, 0, w=120, h=12)
    opst.on(on_msg('시세갱신'), ifelse(gt(V('작전단계'), 0),
                                      [write(join('작전 중: ', LGET('주식이름', V('작전종목')))), show()], [hide()]))

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
                if_(eq(s_, CTL), lst_set('주가', CTL, round2(mul(LGET('주가', CTL),
                                                               add(1, mul(div(V('매매수량'), D.CONTROL_SHARES), D.CONTROL_IMPACT)))))),
                *fmt_comma(V('매매수량'), '_q'), setv('체결글', join('매수 체결!  +', V('_q'))), setv('체결성공', 1)],
               [setv('체결글', '현금이 부족하거나 살 수 있는 수량이 없어요'), setv('체결성공', 0)])]
    sell = [
        setv('매매수량', LGET('보유', s_)),
        ifelse(eq(s_, CTL), [if_(gt(V('매매수량'), mul(V('주문수량'), 100)), setv('매매수량', mul(V('주문수량'), 100)))],
               [if_(gt(V('매매수량'), V('주문수량')), setv('매매수량', V('주문수량')))]),
        ifelse(gt(V('매매수량'), 0),
               [chg('돈', mul(LGET('상품가', s_), V('매매수량'))),
                lst_set('보유', s_, sub(LGET('보유', s_), V('매매수량'))),
                if_(eq(LGET('보유', s_), 0), lst_set('평단', s_, 0)),
                if_(eq(s_, CTL), lst_set('주가', CTL, round2(mul(LGET('주가', CTL),
                                                               sub(1, mul(div(V('매매수량'), D.CONTROL_SHARES), D.CONTROL_IMPACT)))))),
                *fmt_comma(V('매매수량'), '_q'), setv('체결글', join('매도 체결!  -', V('_q'))), setv('체결성공', 1)],
               [setv('체결글', '팔 수량이 없어요'), setv('체결성공', 0)])]
    mgr.on(on_msg('주문'),
           *assets_blocks(),
           setv('_s', V('선택종목')), setv('_p', LGET('주가', V('_s'))),
           setv('_lk', 0),
           if_(and_(gt(V('_s'), SPEC0), le(V('_s'), LEV0)), if_(gt(LGET('특별단계', sub(V('_s'), SPEC0)), V('단계')), setv('_lk', 1))),
           ifelse(eq(V('_lk'), 1), [setv('체결글', '대통령 선거 때 열리는 특별주예요!'), setv('체결성공', 0)],
                  [ifelse(eq(V('주문방향'), 1), buy, sell)]),
           setv('돈', div(rounded(mul(V('돈'), 10)), 10)),
           cast('체결'), *assets_blocks(), *_save(), cast('시세갱신'), *E.majority_check())
    mgr.on(on_scene(), *assets_blocks(),
           if_(or_(lt(V('선택종목'), 1), gt(V('선택종목'), N)), setv('선택종목', 1)),
           setv('탭', 1), setv('탭기준', 0), setv('탭개수', ND),
           if_(gt(V('선택종목'), ND), setv('선택종목', 1)),
           cast('탭변경'), cast('시세갱신'), cast('선택변경'),
           forever(wait(1), ifelse(gt(V('장시간'), 0), [*tick_blocks()], [*coin_tick_blocks()]), cast('시세갱신')))
    E.majority_pop(P, sc)
    import economy as EC
    EC.ticker(P, sc)
    EC.income_pop(P, sc, -150, 80)
    hub = G.sound_hub(P, sc, 'bgm_map')
    hub.on(on_msg('뉴스'), play('news'))
    hub.on(on_msg('체결'), ifelse(eq(V('체결성공'), 1), [play('cash')], [play('bad')]))
    G.fader(P, sc, ctx['BLACK'])


def ifelse_kind(S):
    """종목 번호 → 단위 리스트 번호 (코인이면 4, 아니면 1)."""
    return add(1, mul(3, sub(ifelse_gt(S, COIN0), ifelse_gt(S, SPEC0))))


def ifelse_gt(a, b):
    """a > b 이면 1, 아니면 0 (정수 산술): (a-b 를 0~1 로 자름)."""
    x = sub(a, b)
    m = div(add(x, abs_(x)), 2)          # max(x, 0)
    return div(sub(add(m, 1), abs_(sub(m, 1))), 2)   # min(m, 1)

