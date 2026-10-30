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
import market_data as MD

ND = len(D.STOCKS)              # 15 국내
CTL = ND + 1                    # 16 지배 자본
FOR0 = CTL                      # 해외는 17~
COIN0 = CTL + len(D.FOREIGN)    # 코인은 23~
SPEC0 = COIN0 + len(D.COINS)    # 특별주는 29~
LEV0 = SPEC0 + len(D2.SPECIALS)  # (예전 레버리지 상품 자리 — 지금은 종목마다 인버스·레버리지 주문 모드가 있다)
N = LEV0                         # 34
HIST = 48                       # 시세 기록 칸 수 (0.5초마다 한 칸, 두 칸이 캔들 하나 → 캔들 24개)
NCANDLE = HIST // 2
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
CTL_FLOOR = 40                  # 바닥 가격은 지배 자본에만 (주식·코인은 바닥 없이 얼마든지 떨어진다)
TICK_SEC = 0.5                  # 시세가 움직이는 간격(초): 짧을수록 빠르게 출렁인다
TICKS_DAY = 120                 # 장 한 번(약 1분) ≈ 120걸음: 종목표의 '하루 변동성'을 한 걸음 폭으로 바꿀 때
GAP_DAY = 0.6 * math.sqrt(TICKS_DAY)     # 밤사이 갭 = 하루 변동성의 0.6배
# 시장 흐름 (지수 요인): 1 코스피, 2 나스닥, 3 코인(비트코인). 종목은 베타만큼 같이 움직인다 → 장이 한꺼번에 빨갛거나 파래진다
MKT_DVOL = {1: 3.0, 2: 4.0, 3: 8.0}     # 하루 변동성 %
MKT_KEEP, MKT_MOOD = 0.98, 0.15   # 시장 분위기(지수 기세): 이어지는 정도, 크기(한 걸음 흔들림의 0.15배)
LINK_KN = 0.35                  # 코스피가 나스닥을 따라가는 정도 (미국장 영향)
MKT_NEWS_PERMIL, MKT_NEWS_STR, MKT_NEWS_DUR = 15, (15, 40), (8, 16)   # 시황 뉴스: 걸음당 1.5%, 0.15~0.4%씩 8~16걸음
START_INDEX = {1: 2600, 2: 16000}
NEWS_PCT, NEWS_GOOD = 10, 50    # 한 번 움직일 때 종목 뉴스가 뜰 확률 %, 그중 호재 %
NEWS_STR = (5, 20)              # 뉴스 세기 0.5~2.0%/걸음 × 종목 뉴스 민감도, 4~8걸음
CRASH_PCT, SURGE_PCT, NEWS_MULT = 8, 12, (1, 1)   # 악재의 8% 는 폭락, 호재의 12% 는 폭등 (2배로 커진다)
FLASH_PCT, FLASH_SIZE = 3, (5, 15)   # 한 번 움직일 때 3% 확률로 종목 하나를 골라 기세에 따라 순간 급등·급락 (× 종목 급등락 크기)
# 기세(보이지 않는 매수·매도세): 종목마다 천천히 바뀌며 한동안 한쪽으로 기울게 민다. 화면에 따로 표시하지 않는다
MOOD_MAX, MOOD_KEEP, MOOD_STEP = 0.15, 0.97, 0.15
MOOD_WEAK, MOOD_STRONG = -0.25, 0.1   # 기세가 아주 약하면 급락, 조금만 세도 급등 → 급등이 급락보다 잦다
REV_EMA = 0.01                  # 되돌림 기준선 = 주가의 느린 평균
N_PICK = SPEC0 - 1              # 뉴스·급락이 고르는 종목 수 (지배 자본·특별주 빼고)
N_COIN = SPEC0 - COIN0
COIN_IDX = [i for i in range(1, N + 1) if KIND[i - 1] == 3]
# 화면 순서: 종목 번호(저장 칸)는 그대로 두고, 특별주만 시장 단계(특별주1) → 대통령 단계(특별주2) 순으로 보여 준다
SPEC1 = [SPEC0 + j for j, (_, _, t) in enumerate(D2.SPECIALS, 1) if t == 2]
SPEC2 = [SPEC0 + j for j, (_, _, t) in enumerate(D2.SPECIALS, 1) if t == 3]
ORDER = list(range(1, SPEC0 + 1)) + SPEC1 + SPEC2
# (이름, 표시 순서의 시작 위치, 개수, 열리는 단계)
TABS = [('국내', 0, ND, 1), ('해외', FOR0, len(D.FOREIGN), 1), ('코인', COIN0, len(D.COINS), 1),
        ('특별주1', SPEC0, len(SPEC1), 2), ('특별주2', SPEC0 + len(SPEC1), len(SPEC2), 3)]
BTC = COIN0 + 1                 # 비트코인
# 종목 성격 (market_data.TRAITS): 지배 자본·특별주는 비워 둔다
TR = [MD.TRAITS.get(nm) if KIND[i] in (1, 2, 3) else None for i, nm in enumerate(NAMES)]

STOCK_VARS = dict(장시간=D.MARKET_START, 기록위치=1, 채움=1, 첫째주=D.CONTROL_UNCLES[0], 둘째주=D.CONTROL_UNCLES[1],
                  유통주=0, 평가금=0, 지배달성=0, 주문방향=1, 주문수량=1, 매매수량=0, 이번차단=0,
                  뉴스글='', 뉴스종목=0, 뉴스호재=1, 뉴스루머=3, 뉴스진짜=1, 뉴스세기=0, 변동률=0, 탭=1, 탭기준=0, 탭개수=ND,
                  체결성공=0, _po=0, _lr=0, _lf=1, _pv=0, _ph=0, _pl=0, _pc='', _pt='', _s=1, _p=0, _b=0, _k0=0, _mn=0, _mx=0, _v=0, _rg=1, _c=0, _q='', _m='', _a=0, _bb=0, 체결글='', _ml='', _fx=1, _fy=0, _gi=0,
                  _mi=1, _mm=1, _rv=0, 코스피=START_INDEX[1], 나스닥=START_INDEX[2],
                  전코스피=START_INDEX[1], 전나스닥=START_INDEX[2], _pw=0, _pu=1, _i1='', _i2='', _i3='', _ci=1, _cn=0, _t=1, _yo=0, _yc=0)


def round2(x):
    """가격 저장용 반올림 (만원 단위 소수 넷째 자리 = 1원 단위)."""
    return div(rounded(mul(x, 10000)), 10000)


def _elog(A, B):
    """x 가 [A, B] 에서 고르게 나올 때 ln(1+x) 의 평균."""
    F = lambda x: (1 + x) * math.log(1 + x) - x
    return (F(B) - F(A)) / (B - A)


def _flat(lo, hi, scale, jump=None, need=0.0):
    """rnd(lo+s, hi+s) × scale 만큼 곱해 갈 때 ln 평균이 need 가 되는 정수 s.
    그냥 ±같은 폭으로 곱하면 값이 저절로 0 쪽으로 녹는다 (-10% 뒤 +10% 는 99%). 바닥이 없으니 그만큼 범위를 위로 옮긴다.
    need: 시장 흐름·급락·뉴스로 한 걸음마다 평균적으로 잃는 양 → 길게 보면 제자리 (언제 떨어질지 모른다).
    jump=(확률, 배): 가끔 변동이 몇 배로 커지는 경우까지 넣어서 계산."""
    def e(sh):
        A, B = (lo + sh) * scale, (hi + sh) * scale
        v = _elog(A, B)
        if jump:
            v = (1 - jump[0]) * v + jump[0] * _elog(A * jump[1], B * jump[1])
        return v
    a, b = 0.0, float(max(1, hi))
    for _ in range(60):
        m = (a + b) / 2
        if e(m) < need:
            a = m
        else:
            b = m
    return int(round(a))


# ------------------------------------------------------------------ 시장 요인 (0.01% = 1 단위)
def _mkt_sigma(m, day=1.0):
    """시장 요인 m 의 한 걸음 표준편차 (단위: 0.01%). day: 밤사이 갭 같은 큰 걸음은 배율."""
    return MKT_DVOL[m] * 100 / math.sqrt(TICKS_DAY) * day


def _mkt_var(day=1.0):
    """요인 분산·공분산 (분위기 흔들림 포함). 코스피 요인에는 나스닥 요인이 LINK_KN 만큼 섞여 있다."""
    v = {m: _mkt_sigma(m, day) ** 2 * (1 + MKT_MOOD ** 2) for m in (1, 2, 3)}
    v[1] += LINK_KN ** 2 * v[2]
    cov = {(1, 2): LINK_KN * v[2]}
    return v, cov


def _ab(i):
    """종목 i 가 따라가는 요인 (A: 시장, B: 연결) — 국내: 코스피·나스닥, 해외: 나스닥, 코인: 비트코인·나스닥."""
    return {1: (1, 2), 2: (2, None), 3: (3, 2)}[KIND[i - 1]]


def _pr(i, day=1.0):
    """종목 i 의 한 걸음 모양: (고유 흔들림 반폭 w, 베타, 연결 베타, 요인 A, 요인 B, 요인 분산 몫) — 단위 0.01%."""
    tr = TR[i - 1]
    A, B = _ab(i)
    beta, link = tr[2], (tr[3] if B else 0)
    tot = tr[1] * 100 / math.sqrt(TICKS_DAY) * day
    v, cov = _mkt_var(day)
    part = beta ** 2 * v[A] + (link ** 2 * v[B] + 2 * beta * link * cov.get((A, B), 0) if B else 0)
    idio = math.sqrt(max(tot ** 2 - part, (0.35 * tot) ** 2))
    return int(round(idio * math.sqrt(3))), beta, link, A, B, part


def _news_move(sens):
    """뉴스 한 번이 그 종목 값에 주는 ln 변화의 평균 (호재·악재 반반, 루머는 가짜일 수도)."""
    tot, n = 0.0, 0
    mults = list(range(NEWS_MULT[0], NEWS_MULT[1] + 1))
    for s10 in range(NEWS_STR[0], NEWS_STR[1] + 1):
        st = s10 / 10.0 * sens
        n += 1
        for good in (1, -1):
            pg = NEWS_GOOD / 100.0 if good == 1 else 1 - NEWS_GOOD / 100.0
            big = (SURGE_PCT if good == 1 else CRASH_PCT) / 100.0
            amps = [(1 - big, 1)] + [(big / len(mults), 1 + m) for m in mults]
            for pa, m in amps:
                for rumor, pr in ((1, 0.3), (0, 0.7)):
                    ptrue = 0.5 if rumor else 0.85
                    s2 = min(60.0, st * m * (0.4 if rumor else 1))
                    for true, pt in ((1, ptrue), (0, 1 - ptrue)):
                        tr = s2 * good * (1 if true else -0.6)
                        for dur in range(4, 9):
                            tot += pg * pa * pr * pt / 5.0 * dur * math.log(1 + tr / 100.0)
    return tot / n


def _jump_loss(i, coin_mode):
    """종목 i 가 한 걸음마다 뉴스·순간 급등락으로 평균적으로 잃는 ln 양 (양수면 잃음)."""
    tr = TR[i - 1]
    ys = [y * tr[5] for y in range(FLASH_SIZE[0], FLASH_SIZE[1] + 1)]
    drop = sum(math.log(1 - min(90.0, y) / 100.0) for y in ys) / len(ys)
    rise = sum(math.log(1 + y / 100.0) for y in ys) / len(ys)
    pick = (1.0 / N_COIN) if coin_mode else (0.92 / N_PICK)
    # 기세가 MOOD_WEAK 아래 / MOOD_STRONG 위일 확률 (기세 ≈ 정규분포, 표준편차 = 한 걸음 흔들림 / √(1 - 유지율²))
    sd = MOOD_STEP / math.sqrt(3) / math.sqrt(1 - MOOD_KEEP ** 2)
    cdf = lambda z: 0.5 * (1 + math.erf(z / sd / math.sqrt(2)))
    flash = cdf(MOOD_WEAK) * drop + (1 - cdf(MOOD_STRONG)) * rise
    return -(NEWS_PCT / 100.0 * pick * _news_move(tr[4]) +
             FLASH_PCT / 100.0 * (1.0 / N_COIN if coin_mode else 1.0 / N_PICK) * flash)


def _set_free(i):
    """바닥 없이 움직인 가격 저장 (소수 여섯째 자리 = 0.01원 단위, 0원이 되어 멈추지 않게 최소 0.01원)."""
    return lst_set('주가', i, div(rounded(add(mul(mul(LGET('주가', i), add(1, V('변동률'))), 1000000), 0.6)), 1000000))


def setup(P):
    global _P
    _P = P
    _FN.clear()
    P.list('주식이름', NAMES)
    P.list('주가', PRICES)
    P.list('전주가', PRICES)
    P.list('업종', SECTORS)
    P.list('변동성표시', [('●' * min(5, max(1, round(tr[1] / 4.0))) + '○' * (5 - min(5, max(1, round(tr[1] / 4.0))))) if tr
                         else ('★★★★★' if k == 4 else '●○○○○') for tr, k in zip(TR, KIND)])
    for nm in ('보유', '평단', '추세', '추세남은'):
        P.list(nm, [0] * N)
    P.list('주가기록', [0] * (N * HIST))     # 차트는 채운 칸(채움)만 읽는다
    P.list('배수', [1] * N)          # 종목별 주문 모드: 1 일반, -1 인버스, 2·5·10 레버리지(코인·특별주), -2·-5·-10 인버스 레버리지
    P.list('상품가', PRICES)
    P.list('특별X', [0] * len(D2.SPECIALS))
    # 종목 성격 (market_data): 기세(추세+되돌림), 기세폭, 되돌림 기준선(주가의 느린 평균, 0 이면 다음에 주가로)
    P.list('기세', [0] * N)
    P.list('기세속', [0] * N)
    P.list('기세폭', [int(round(MOOD_MAX * _pr(i)[0] * TR[i - 1][7])) if TR[i - 1] else 0 for i in range(1, N + 1)])
    P.list('기준', [0] * N)
    P.list('회귀', [round(TR[i - 1][6] * 10000, 2) if TR[i - 1] else 0 for i in range(1, N + 1)])
    P.list('되돌림폭', [int(round(0.4 * TR[i - 1][1] * 100 / math.sqrt(TICKS_DAY))) if TR[i - 1] else 0 for i in range(1, N + 1)])
    P.list('뉴스민감', [tr[4] if tr else 1 for tr in TR])
    P.list('점프', [tr[5] if tr else 1 for tr in TR])
    P.list('거래대금', [tr[8] if tr else (3000 if k == 4 else 0) for tr, k in zip(TR, KIND)])
    P.list('종목특징', [tr[0] if tr else SECTORS[i] for i, tr in enumerate(TR)])
    P.list('종목호재', [x for tr in TR for x in (tr[9] if tr else ('', ''))])
    P.list('종목악재', [x for tr in TR for x in (tr[10] if tr else ('', ''))])
    for k, v in step_params().items():
        P.list(k, v)
    P.list('요인', [0, 0, 0])
    # 시장 요인: 1 코스피, 2 나스닥, 3 코인
    for nm in ('지수기세', '시장추세', '시장남은'):
        P.list(nm, [0, 0, 0])
    P.list('시황호재', [t for m in (1, 2, 3) for t in MD.MARKET_NEWS[m][0]])
    P.list('시황악재', [t for m in (1, 2, 3) for t in MD.MARKET_NEWS[m][1]])
    P.list('특별기준', [p for _, p, _ in D2.SPECIALS])
    P.list('지수표', [round(math.exp(k / 10.0), 6) for k in range(-EXP_K, EXP_K + 1)])
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
    b.append(if_(eq(V('회사상태'), 1), chg('총자산', V('회사가치합'))))      # 내 회사들 가치 합
    return b


def _save():
    return [if_(eq(V('체결성공'), 1), setv('저장필요', 1))]


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
              lst_set('추세', i, 0), lst_set('추세남은', i, 0), lst_set('기준', i, 0), lst_set('주가기록', (i - 1) * HIST + 1, p)]
    b += [lst_set('특별X', i, 0) for i in range(1, len(D2.SPECIALS) + 1)]
    b += [lst_set('주식이름', CTL, D2.CONTROL_NAMES[0])]
    return b


def _record_blocks():
    return _shared('시세기록', _record_body)


def _record_body():
    b = [setv('기록위치', add(mod(V('기록위치'), HIST), 1)), if_(lt(V('채움'), HIST), chg('채움', 1))]
    for i in range(1, N + 1):
        b.append(lst_set('주가기록', add((i - 1) * HIST, V('기록위치')), LGET('주가', i)))
    return b


def _news_blocks(coins_only=False):
    """종목 뉴스: 종목마다 자기 호재·악재 (바이오는 임상, 엔터는 컴백…). 세기는 종목 뉴스 민감도만큼."""
    s = V('뉴스종목')
    pick = [ifelse(gt(V('장시간'), 0),
                   [ifelse(le(rnd(1, 100), 8), [setv('뉴스종목', CTL)],
                           [setv('뉴스종목', rnd(1, SPEC0 - 1)), if_(ge(V('뉴스종목'), CTL), chg('뉴스종목', 1))])],
                   [setv('뉴스종목', rnd(COIN0 + 1, SPEC0))])]
    k2 = add(mul(sub(s, 1), 2), rnd(1, 2))
    return [
        if_(le(rnd(1, 100), NEWS_PCT),
            *pick,
            ifelse(le(rnd(1, 100), NEWS_GOOD), [setv('뉴스호재', 1)], [setv('뉴스호재', -1)]),
            ifelse(le(rnd(1, 100), 30), [setv('뉴스루머', 1)], [setv('뉴스루머', 0)]),
            setv('뉴스세기', mul(div(rnd(*NEWS_STR), 10), LGET('뉴스민감', s))),
            # 가끔 뉴스가 2배로 커진다 (폭락·폭등: 호재 쪽이 더 잦다)
            ifelse(lt(V('뉴스호재'), 0), [if_(le(rnd(1, 100), CRASH_PCT), chg('뉴스세기', mul(V('뉴스세기'), rnd(*NEWS_MULT))))],
                   [if_(le(rnd(1, 100), SURGE_PCT), chg('뉴스세기', mul(V('뉴스세기'), rnd(*NEWS_MULT))))]),
            ifelse(eq(V('뉴스루머'), 1),
                   [chg('뉴스세기', mul(V('뉴스세기'), -0.6)),
                    ifelse(le(rnd(1, 100), 50), [setv('뉴스진짜', 1)], [setv('뉴스진짜', 0)])],
                   [ifelse(le(rnd(1, 100), 85), [setv('뉴스진짜', 1)], [setv('뉴스진짜', 0)])]),
            ifelse(eq(V('뉴스진짜'), 1), [lst_set('추세', s, mul(V('뉴스세기'), V('뉴스호재')))],
                   [lst_set('추세', s, mul(mul(V('뉴스세기'), V('뉴스호재')), -0.6))]),
            lst_set('추세남은', s, rnd(4, 8)),
            ifelse(eq(s, CTL),
                   [lst_set('추세', CTL, div(LGET('추세', CTL), 2.5)),
                    ifelse(eq(V('뉴스호재'), 1), [setv('뉴스글', LGET('지배호재', rnd(1, len(D.CONTROL_NEWS_GOOD))))],
                           [setv('뉴스글', LGET('지배악재', rnd(1, len(D.CONTROL_NEWS_BAD))))])],
                   [ifelse(eq(V('뉴스호재'), 1), [setv('뉴스글', join(LGET('주식이름', s), LGET('종목호재', k2)))],
                           [setv('뉴스글', join(LGET('주식이름', s), LGET('종목악재', k2)))])]),
            cast('뉴스')),
    ]


def _market_news_blocks(coins_only=False):
    """시황 뉴스: 시장 하나(코스피·나스닥·코인)가 한동안 같이 오르거나 내린다 (종목은 베타만큼)."""
    m = V('_mm')
    return [if_(le(rnd(1, 1000), MKT_NEWS_PERMIL),
                ifelse(gt(V('장시간'), 0), [setv('_mm', rnd(1, 3))], [setv('_mm', 3)]),
                ifelse(le(rnd(1, 100), 50),
                       [lst_set('시장추세', m, rnd(*MKT_NEWS_STR)), setv('뉴스글', LGET('시황호재', add(mul(sub(m, 1), 3), rnd(1, 3))))],
                       [lst_set('시장추세', m, mul(rnd(*MKT_NEWS_STR), -1)), setv('뉴스글', LGET('시황악재', add(mul(sub(m, 1), 3), rnd(1, 3))))]),
                lst_set('시장남은', m, rnd(*MKT_NEWS_DUR)), setv('뉴스루머', 3), cast('뉴스'))]


def _factor_blocks(ms):
    """시장 요인 한 걸음: 고른 흔들림 + 시장 분위기(천천히 바뀜) + 시황 뉴스 추세. 나스닥을 먼저 (코스피가 따라간다)."""
    b = []
    for m in ms:
        sg = _mkt_sigma(m)
        a, st = int(round(sg * math.sqrt(3))), max(1, int(round(sg * MKT_MOOD / 0.29)))
        b += [lst_set('지수기세', m, add(mul(LGET('지수기세', m), MKT_KEEP), div(rnd(-st, st), 10))),
              ifelse(gt(LGET('시장남은', m), 0), [lst_set('시장남은', m, sub(LGET('시장남은', m), 1))], [lst_set('시장추세', m, 0)]),
              lst_set('요인', m, add(add(add(rnd(-a, a), LGET('지수기세', m)), LGET('시장추세', m)),
                                    mul(LGET('요인', 2), LINK_KN) if m == 1 else 0))]
        if m in START_INDEX:
            nm = '코스피' if m == 1 else '나스닥'
            b.append(setv(nm, mul(V(nm), add(1, div(LGET('요인', m), 10000)))))
    return b


def _flash_blocks(coins_only=False):
    """가끔 종목 하나가 예고 없이 순간 급등·급락 (크기는 종목 성격만큼). 기세가 세면 급등, 아주 약하면 급락 (급등이 더 잦다)."""
    x = V('_fx')
    pick = [ifelse(gt(V('장시간'), 0), [setv('_fx', rnd(1, N_PICK)), if_(ge(x, CTL), chg('_fx', 1))],
                   [setv('_fx', rnd(COIN0 + 1, SPEC0))])]
    jump = lambda sign, tag, mark: [
        setv('_fy', rounded(mul(rnd(*FLASH_SIZE), LGET('점프', x)))), if_(gt(V('_fy'), 90), setv('_fy', 90)),
        lst_set('주가', x, div(rounded(add(mul(mul(LGET('주가', x), add(1, div(V('_fy'), 100 * sign))), 1000000), 0.6)), 1000000)),
        setv('뉴스루머', 0), setv('뉴스글', join(tag, LGET('주식이름', x), mark, V('_fy'), '%!')), cast('뉴스')]
    return [if_(le(rnd(1, 100), FLASH_PCT), *pick,
                ifelse(lt(LGET('기세', x), mul(LGET('기세폭', x), MOOD_WEAK)), jump(-1, '[급락] ', ' 갑자기 -'),
                       [if_(gt(LGET('기세', x), mul(LGET('기세폭', x), MOOD_STRONG)), *jump(1, '[급등] ', ' 갑자기 +'))]))]


def _trend(i):
    return [if_(gt(LGET('추세남은', i), 0), chg('변동률', div(LGET('추세', i), 100)),
                lst_set('추세남은', i, sub(LGET('추세남은', i), 1)))]


def _move(i):
    """한 걸음: 고유 흔들림 + 기세(추세·되돌림) + 시장 요인 × 베타 + 나스닥 × 연결 베타 + 뉴스 추세.
    종목마다 다른 값(폭·보정·베타·요인 번호)은 리스트에 두고, 종목 번호만 넘겨 함수 하나로 계산한다 (작품 크기 절약)."""
    if KIND[i - 1] == 0:           # 지배 자본은 예전처럼 (바닥 있음)
        v10 = VOLS[i - 1] * 10
        return [setv('변동률', mul(div(rnd(-v10, v10), 1000), TICK_AMP_CTL)), *_trend(i),
                lst_set('주가', i, round2(mul(LGET('주가', i), add(1, V('변동률'))))),
                if_(lt(LGET('주가', i), CTL_FLOOR), lst_set('주가', i, CTL_FLOOR))]
    return [setv('_mi', i), *_shared('한걸음', _step_body)]


def _step_body():
    i = V('_mi')
    u = add(add(add(rnd(sub(LGET('걸음이동', i), LGET('걸음폭', i)), add(LGET('걸음이동', i), LGET('걸음폭', i))), LGET('기세', i)),
                mul(LGET('요인', LGET('요인A', i)), LGET('베타', i))), mul(LGET('요인', LGET('요인B', i)), LGET('연결', i)))
    return [setv('변동률', div(u, 10000)), *_trend(i), _set_free(i)]


def _gap_body():
    i = V('_mi')
    u = add(add(rnd(sub(LGET('갭이동', i), LGET('갭폭', i)), add(LGET('갭이동', i), LGET('갭폭', i))),
                mul(LGET('요인', LGET('요인A', i)), LGET('베타', i))), mul(LGET('요인', LGET('요인B', i)), LGET('연결', i)))
    return [setv('변동률', div(u, 10000)), _set_free(i)]


def step_params():
    """종목별 한 걸음 값 (리스트에 넣을 것): 걸음폭·걸음이동·갭폭·갭이동·베타·연결·요인A·요인B."""
    rows = {k: [] for k in ('걸음폭', '걸음이동', '갭폭', '갭이동', '베타', '연결', '요인A', '요인B')}
    for i in range(1, N + 1):
        if not TR[i - 1]:
            for k in rows:
                rows[k].append(1 if k in ('요인A', '요인B') else 0)
            continue
        w, beta, link, A, B, part = _pr(i)
        sh = _flat(-w, w, 1 / 10000.0, need=_jump_loss(i, False) + part / 2e8)
        wg, _, _, _, _, partg = _pr(i, GAP_DAY)
        shg = _flat(-wg, wg, 1 / 10000.0, need=partg / 2e8)
        for k, v in (('걸음폭', w), ('걸음이동', sh), ('갭폭', wg), ('갭이동', shg), ('베타', beta), ('연결', link if B else 0),
                     ('요인A', A), ('요인B', B or 2)):
            rows[k].append(v)
    return rows


TICK_AMP_CTL = D.STOCK_TICK / math.sqrt(2)


def special_blocks():
    return _shared('특별주한걸음', _special_body)


def _special_body():
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


def market_step():
    """0.5초마다 한 걸음: 시장 요인 → (주식 장이 열려 있으면) 주식·지배 자본 → 코인(24시간) → 특별주 → 기록·뉴스·급등락."""
    import economy as EC
    stocks, coins = [], []
    for i in range(1, SPEC0 + 1):
        if KIND[i - 1] == 3:
            coins += _move(i)
        else:
            stocks += _move(i)
    return [*_factor_blocks((2, 3)),
            if_(gt(V('장시간'), 0), chg('장시간', -TICK_SEC), *_factor_blocks((1,)), *stocks, *EC.ops_tick_blocks(),
                if_(eq(V('장시간'), 0), setv('뉴스루머', 2), setv('뉴스글', '주식 장이 마감됐어요. 코인은 24시간 움직입니다!'),
                    cast('뉴스'))),
            *coins, *special_blocks(), *_record_blocks(), *_news_blocks(), *_market_news_blocks(), *_flash_blocks(),
            *assets_blocks()]




def overnight_blocks():
    """유세 1번이 끝날 때(밤사이): 시장마다 갭(코스피·나스닥·코인) + 종목 갭, 장 시간 추가, 큰아버지들의 지배 자본 매수."""
    b = [setv('전코스피', V('코스피')), setv('전나스닥', V('나스닥'))]
    for m in (2, 1, 3):
        a = int(round(_mkt_sigma(m, GAP_DAY) * math.sqrt(3)))
        b.append(lst_set('요인', m, add(rnd(-a, a), mul(LGET('요인', 2), LINK_KN) if m == 1 else 0)))
        if m in START_INDEX:
            nm = '코스피' if m == 1 else '나스닥'
            b.append(setv(nm, mul(V(nm), add(1, div(LGET('요인', m), 10000)))))
    for i in range(1, N + 1):
        k = KIND[i - 1]
        b.append(lst_set('전주가', i, LGET('주가', i)))
        if k == 4:
            continue
        if k == 0:
            b += [setv('변동률', div(rnd(-25, 40), 1000)),
                  lst_set('주가', i, round2(mul(LGET('주가', i), add(1, V('변동률'))))),
                  if_(lt(LGET('주가', i), CTL_FLOOR), lst_set('주가', i, CTL_FLOOR))]
            continue
        b += [setv('_mi', i), *_shared('갭한걸음', _gap_body)]
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


UT, UG, ULG = SA.UHEX['txt'], SA.UHEX['gray'], SA.UHEX['lgray']
UR, UB, UN = SA.UHEX['red'], SA.UHEX['blue'], SA.UHEX['navy']
VOL_UP, VOL_DN = '#eab4a9', '#a9c2ea'    # 거래량 막대 (연한 빨강·파랑)


def _won_body():
    """_pw(원) → _pt: 업비트처럼 원 단위 쉼표 (1만 원 이상은 앞 네 자리까지만 = 호가 단위), 작은 값은 소수."""
    pw = V('_pw')
    return [ifelse(ge(pw, 10000),
                   [setv('_pu', LGET('자릿값', sub(floor(fn('log', pw)), 2))),
                    *fmt_comma(mul(rounded(div(pw, V('_pu'))), V('_pu')), '_pt')],
                   [ifelse(ge(pw, 100), [*fmt_comma(rounded(pw), '_pt')],
                           [ifelse(ge(pw, 1), [setv('_pt', div(rounded(mul(pw, 100)), 100))],
                                   [setv('_pt', div(rounded(mul(pw, 10000)), 10000))])])])]


def won(src, dst='_pt'):
    """가격(만원) → 원 글 (변수 dst)."""
    b = [setv('_pw', mul(src, 10000)), *_shared('원글', _won_body)]
    return b + ([setv(dst, V('_pt'))] if dst != '_pt' else [])


def updown_color(i):
    """전일 종가보다 오르면 빨강, 내리면 파랑, 같으면 검정 (글자색)."""
    return [ifelse(gt(LGET('주가', i), LGET('전주가', i)), [text_color(UR)],
                   [ifelse(lt(LGET('주가', i), LGET('전주가', i)), [text_color(UB)], [text_color(UT)])])]


def change_blocks(i):
    """종목 i 의 전일 대비 등락률 글 (+1.23% 빨강 / -0.45% 파랑)."""
    return [setv('_c', div(rounded(mul(sub(div(LGET('주가', i), LGET('전주가', i)), 1), 10000)), 100)),
            ifelse(gt(V('_c'), 0), [write(join('+', V('_c'), '%'))], [write(join(V('_c'), '%'))]), *updown_color(i)]


def chg_text(i):
    """등락률 글 + 색 (함수 하나로: 부르는 글상자에 쓴다)."""
    return [setv('_ci', i), *_shared('등락글', lambda: change_blocks(V('_ci')))]


def ud_color(i):
    return [setv('_ci', i), *_shared('오르내림색', lambda: updown_color(V('_ci')))]


def comma(src):
    """숫자 → '1,234' (변수 _q)."""
    return [setv('_cn', src), *_shared('쉼표', lambda: fmt_comma(V('_cn'), '_q'))]


def tv_text(i):
    """거래대금(억): 기본 거래대금 × (1 + 오늘 등락폭 × 8)."""
    return comma(mul(LGET('거래대금', i), add(1, mul(abs_(sub(div(LGET('주가', i), LGET('전주가', i)), 1)), 8))))


def _ubtn(P, sc, base, pic, x, y, actions, visible=True):
    """평평한 버튼: 누르면 살짝 작아졌다 돌아온다 (업비트처럼 커지는 효과 없음)."""
    o = sprite(P, sc, base, pic, x, y, visible=visible)
    o.on(on_click(), o.pct(94), cast('snd:click'), *flat(actions))
    o.on(on_click(), wait(0.08), o.pct(100))
    return o


def build(P, ctx):
    import empire as E
    import economy as EC
    import savegame as SG
    sc = ctx['S_STOCK']
    L = SA.UL
    G.bg(P, sc, SA.upbit_bg())
    P.list('자릿값', [10 ** k for k in range(10)])
    S = V('선택종목')

    # ---- 머리띠: 지수 · 장 시간 · 현금 · 총자산 (흰 글자)
    def idx_part(now, prev, var):
        return [setv('_c', div(rounded(mul(sub(div(V(now), V(prev)), 1), 10000)), 100)),
                ifelse(ge(V('_c'), 0), [setv(var, join('▲', V('_c'), '%'))], [setv(var, join('▼', abs_(V('_c')), '%'))])]
    ix = text(P, sc, '지수글', '', -40, 126, 6.5, '#d6e0f5', F_BODY, True, 1, w=200, h=11)
    ix.on(on_msg('시세갱신'), *idx_part('코스피', '전코스피', '_i1'), *idx_part('나스닥', '전나스닥', '_i2'),
          setv('_c', div(rounded(mul(sub(div(LGET('주가', BTC), LGET('전주가', BTC)), 1), 10000)), 100)),
          ifelse(ge(V('_c'), 0), [setv('_i3', join('▲', V('_c'), '%'))], [setv('_i3', join('▼', abs_(V('_c')), '%'))]),
          write(join('코스피 ', div(rounded(mul(V('코스피'), 100)), 100), ' ', V('_i1'), '    나스닥 ', rounded(V('나스닥')), ' ', V('_i2'),
                     '    비트코인 ', V('_i3'))))
    t = text(P, sc, '장시간', '', 101, 126, 6.5, '#ffffff', F_BODY, True, 0, w=78, h=11)
    t.on(on_scene(), forever(ifelse(gt(V('장시간'), 0), [write(join('주식장 마감까지 ', ceil_(V('장시간')), '초')), text_color('#ffffff')],
                                    [write('주식 마감 · 코인 24시간'), text_color('#ffc2b5')]), wait(0.2)))
    t = text(P, sc, '현금', '', 190, 130.5, 6.5, '#ffffff', F_BODY, True, 2, w=94, h=10)
    t.on(on_scene(), forever(*fmt_money(V('돈'), '_m'), write(join('현금 ', V('_m'))), wait(0.15)))
    t = text(P, sc, '총자산', '', 190, 121.5, 6.5, '#b9cbf3', F_BODY, True, 2, w=94, h=10)
    t.on(on_scene(), forever(*fmt_money(V('총자산'), '_m'), write(join('총자산 ', V('_m'))), wait(0.15)))

    # ---- 뉴스 띠
    tag = sprite(P, sc, '뉴스표', [(k, SA.u_news_tag(k)) for k in ('속보', '루머', '장마감', '시황')], -223, 108.5)
    news = text(P, sc, '뉴스글', '', 16, 108.5, 7, UT, F_BODY, True, 1, w=440, h=11)
    tag_sel = [ifelse(eq(V('뉴스루머'), 0), [shape('속보')], [ifelse(eq(V('뉴스루머'), 1), [shape('루머')],
                                                                   [ifelse(eq(V('뉴스루머'), 2), [shape('장마감')], [shape('시황')])])])]
    tag.on(on_msg('뉴스'), *tag_sel, tag.pct(130), rep(5, tag.grow_pct(-6), wait(0.02)))
    news.on(on_msg('뉴스'), write(V('뉴스글')), lx(28), rep(6, mvx(-2), wait(0.016)))
    news.on(on_scene(), ifelse(gt(V('장시간'), 0),
                               [setv('뉴스루머', 3), setv('뉴스글', '장이 열렸습니다! 코스피·나스닥·코인 흐름과 뉴스를 보고 사고파세요. 루머는 가짜일 수도 있어요.')],
                               [setv('뉴스루머', 2), setv('뉴스글', '주식 장은 마감. 코인은 24시간 움직여요. 유세를 하면 장이 다시 열립니다.')]),
            cast('뉴스'))

    def select_actions(idx_expr):
        return [setv('선택종목', idx_expr), cast('시세갱신')]

    # ---- 왼쪽 위: 고른 종목 이름 · 현재가 · 등락 · 특징
    d_nm = text(P, sc, '상세이름', '', -174, 92, 10, UT, F_BODY, True, 1, w=120, h=14)
    d_pr = text(P, sc, '상세가격', '', -166, 80.5, 14, UT, F_BODY, True, 1, w=136, h=18)
    d_ch = text(P, sc, '상세등락', '', -60, 80, 7.5, UT, F_BODY, True, 1, w=76, h=11)
    d_tr = text(P, sc, '상세특징', '', -110, 72.5, 6, UG, F_BODY, False, 1, w=248, h=9)
    d_s1 = text(P, sc, '상세전일', '', 14, 93, 6, UG, F_BODY, False, 2, w=76, h=9)
    d_s2 = text(P, sc, '상세대금', '', 14, 84, 6, UG, F_BODY, False, 2, w=76, h=9)
    detail = [
        d_nm, [write(LGET('주식이름', S))],
        d_pr, [*won(LGET('주가', S)), write(V('_pt')), *ud_color(S)],
        d_tr, [write(join(LGET('종목특징', S), '  ·  변동성 ', LGET('변동성표시', S)))],
        d_s1, [*won(LGET('전주가', S)), write(join('전일 ', V('_pt')))],
        d_s2, [*tv_text(S), write(join('거래대금 ', V('_q'), '억'))],
        d_ch, [*chg_text(S)],
    ]
    for k in range(0, len(detail), 2):
        o, blk = detail[k], detail[k + 1]
        o.on(on_msg('시세갱신'), *blk)

    # ---- 캔들 차트 (복제본 24개가 저마다 붓으로 꼬리·몸통·거래량을 그린다)
    cx0, cx1, cy0, cy1 = L['chart']
    YH = cy1 - cy0
    dxc = (cx1 - cx0) / float(NCANDLE)
    bw = round(dxc * 0.62, 1)
    vb0, vb1 = L['vol']
    k_ = V('_k')
    # 차트 담당: 캔들 계산(최저·최고) → 그리기 → 가격축 글
    P.var('_cb', 0)
    P.var('_cq', 1)
    P.var('_codd', 0)
    P.var('_vmax', 0)
    cm = text(P, sc, '차트담당', '', -300, -300, 8, visible=False)
    ax_hi = text(P, sc, '축최고', '', 37, cy1 - 1, 5, ULG, F_BODY, False, 0, w=30, h=8)
    ax_lo = text(P, sc, '축최저', '', 37, cy0 + 1, 5, ULG, F_BODY, False, 0, w=30, h=8)
    ax_now = text(P, sc, '축현재', '', 37, 30, 5.5, UT, F_BODY, True, 0, w=30, h=8)
    newest = LGET('주가기록', add(V('_cb'), V('기록위치')))
    chart_go = [setv('_cb', mul(sub(S, 1), HIST)), setv('_cq', ceil_(div(V('기록위치'), 2))), setv('_codd', mod(V('기록위치'), 2)),
                setv('_mn', newest), setv('_mx', newest), setv('_vmax', 0),
                cast_wait('캔들계산'),
                setv('_rg', sub(V('_mx'), V('_mn'))),
                if_(lt(V('_rg'), mul(V('_mx'), 0.006)), setv('_mn', sub(V('_mn'), div(sub(mul(V('_mx'), 0.006), V('_rg')), 2))),
                    setv('_rg', mul(V('_mx'), 0.006))),
                setv('_mn', sub(V('_mn'), mul(V('_rg'), 0.06))), setv('_rg', mul(V('_rg'), 1.12)),
                if_(le(V('_rg'), 0), setv('_rg', 1)), if_(le(V('_vmax'), 0), setv('_vmax', 1)),
                cast('캔들그리기')]
    cm.on(on_msg('시세갱신'), *chart_go)
    for o_, expr in ((ax_hi, add(V('_mn'), V('_rg'))), (ax_lo, V('_mn'))):
        o_.on(on_msg('캔들그리기'), *won(expr), write(V('_pt')))
    ax_now.on(on_msg('캔들그리기'), *won(newest), write(V('_pt')), *ud_color(S),
              ly(add(cy0, mul(div(sub(newest, V('_mn')), V('_rg')), YH))))
    # 캔들 복제본
    cd = sprite(P, sc, '캔들', SA.u_square((255, 255, 255), 0, 'clear'), -300, -300, visible=False)
    for nm_ in ('_co', '_cc', '_ch', '_cl', '_cv', '_cok', '_cp'):
        cd.local(nm_, 0)
    rec = lambda pos: LGET('주가기록', add(V('_cb'), pos))
    p_ = V('_cp')
    calc = [setv('_cp', add(mod(add(sub(V('_cq'), 1), k_), NCANDLE), 1)),
            # 이 캔들의 첫 칸과 그 앞 칸(앞 캔들의 마지막 값)이 모두 기록 안에 있어야 그린다 (첫 칸 나이 + 1 < 채움)
            setv('_cok', 0),
            if_(lt(add(mod(add(sub(V('기록위치'), mul(p_, 2)), HIST + 1), HIST), 1), V('채움')),
                setv('_cok', 1),
                setv('_co', rec(add(mod(add(mul(p_, 2), HIST - 3), HIST), 1))),
                setv('_ch', rec(sub(mul(p_, 2), 1))),
                ifelse(and_(eq(p_, V('_cq')), eq(V('_codd'), 1)), [setv('_cc', V('_ch'))], [setv('_cc', rec(mul(p_, 2)))]),
                setv('_cl', V('_ch')),
                if_(gt(V('_co'), V('_ch')), setv('_ch', V('_co'))), if_(gt(V('_cc'), V('_ch')), setv('_ch', V('_cc'))),
                if_(lt(V('_co'), V('_cl')), setv('_cl', V('_co'))), if_(lt(V('_cc'), V('_cl')), setv('_cl', V('_cc'))),
                if_(gt(V('_ch'), V('_mx')), setv('_mx', V('_ch'))), if_(lt(V('_cl'), V('_mn')), setv('_mn', V('_cl'))),
                setv('_cv', div(add(abs_(sub(V('_cc'), V('_co'))), mul(sub(V('_ch'), V('_cl')), 0.5)), V('_co'))),
                if_(gt(V('_cv'), V('_vmax')), setv('_vmax', V('_cv'))))]
    ypos = lambda v: add(cy0, mul(div(sub(v, V('_mn')), V('_rg')), YH))
    xk = add(cx0 + dxc / 2, mul(sub(k_, 1), dxc))
    draw = [pen_up(), pen_clear(),
            if_(eq(V('_cok'), 1),
                setv('_yo', ypos(V('_co'))), setv('_yc', ypos(V('_cc'))),
                if_(lt(abs_(sub(V('_yc'), V('_yo'))), 1), setv('_yc', add(V('_yo'), 1))),
                ifelse(ge(V('_cc'), V('_co')), [pen_color(UR)], [pen_color(UB)]),
                pen_size(1), xy(xk, ypos(V('_cl'))), pen_down(), xy(xk, ypos(V('_ch'))), pen_up(),
                pen_size(bw), xy(xk, V('_yo')), pen_down(), xy(xk, V('_yc')), pen_up(),
                ifelse(ge(V('_cc'), V('_co')), [pen_color(VOL_UP)], [pen_color(VOL_DN)]),
                xy(xk, vb0), pen_down(), xy(xk, add(vb0 + 0.5, mul(div(V('_cv'), V('_vmax')), vb1 - vb0 - 0.5))), pen_up()),
            xy(-300, -300)]
    G.clone_rows(cd, NCANDLE, '_k', -300, -300, [show()])
    cd.on(on_msg('캔들계산'), if_(gt(k_, 0), *calc))
    cd.on(on_msg('캔들그리기'), if_(gt(k_, 0), *draw))
    opst = text(P, sc, '작전표시', '', -175, 61, 6, SA.UHEX['purple'], F_BODY, True, 1, w=110, h=9)
    opst.on(on_msg('시세갱신'), ifelse(gt(V('작전단계'), 0),
                                      [write(join('작전 중: ', LGET('주식이름', V('작전종목')))), show()], [hide()]))

    # ---- 호가창 (보기용: 현재가 위 5칸 매도, 아래 5칸 매수, 잔량은 그때그때)
    h0, h1 = L['hoga']
    hm = text(P, sc, '호가담당', '', -300, -300, 8, visible=False)
    P.list('호가잔량', [0] * 10)
    P.var('_hp', 0)
    P.var('_hu', 1)
    P.var('_hq', 1)
    hoga_go = [setv('_pw', mul(LGET('주가', S), 10000)),
               ifelse(ge(V('_pw'), 10000), [setv('_hu', LGET('자릿값', sub(floor(fn('log', V('_pw'))), 2)))],
                      [ifelse(ge(V('_pw'), 100), [setv('_hu', 1)], [ifelse(ge(V('_pw'), 1), [setv('_hu', 0.01)], [setv('_hu', 0.0001)])])]),
               setv('_hp', mul(rounded(div(V('_pw'), V('_hu'))), V('_hu'))),
               # 잔량 단위: 비싼 종목은 적게, 싼 종목은 많이
               setv('_hq', div(1000000, V('_pw'))), if_(lt(V('_hq'), 0.001), setv('_hq', 0.001)),
               *[lst_set('호가잔량', r, add(mul(LGET('호가잔량', r), 0.55), mul(rnd(5, 1000), 0.45))) for r in range(1, 11)],
               setv('_vmax', 1),
               cast('호가그리기')]
    hm.on(on_msg('시세갱신'), *hoga_go)
    r_ = V('_hr')
    hy = sub(L['hoga_y0'], mul(sub(r_, 1), L['hoga_h']))
    hb = sprite(P, sc, '호가막대', SA.u_square((255, 255, 255), 0, 'clear'), -300, -300, visible=False)
    hb.local('_hr', 0)
    bar_w = lambda: mul(div(LGET('호가잔량', r_), 1000), 44)
    hb_draw = [pen_up(), pen_clear(), pen_size(7),
               ifelse(le(r_, 5), [pen_color('#cfdcf3'), xy(h0 + 48, hy), pen_down(), xy(sub(h0 + 48, bar_w()), hy)],
                      [pen_color('#f3d3cc'), xy(h1 - 46, hy), pen_down(), xy(add(h1 - 46, bar_w()), hy)]),
               pen_up(), xy(-300, -300)]
    G.clone_rows(hb, 10, '_hr', -300, -300, [show()])
    hb.on(on_msg('호가그리기'), if_(gt(r_, 0), *hb_draw))
    hpt = text(P, sc, '호가가격', '', -300, -300, 6.5, UT, F_BODY, True, 0, w=48, h=9, visible=False)
    hpt.local('_hr', 0)
    hprice = add(div(V('_hp'), 10000), mul(div(V('_hu'), 10000), sub(5, sub(r_, 1))))   # 만원: 위 5칸은 +5~+1호가, 아래는 0~-4호가
    hpt_b = [*won(hprice), write(V('_pt')),
             ifelse(gt(hprice, LGET('전주가', S)), [text_color(UR)], [ifelse(lt(hprice, LGET('전주가', S)), [text_color(UB)], [text_color(UT)])])]
    G.clone_rows(hpt, 10, '_hr', (h0 + h1) / 2, hy, [show()])
    hpt.on(on_msg('호가그리기'), *hpt_b)
    hqt = text(P, sc, '호가잔량', '', -300, -300, 5.5, UG, F_BODY, False, 0, w=44, h=8, visible=False)
    hqt.local('_hr', 0)
    hq_val = mul(LGET('호가잔량', r_), V('_hq'))
    hqt_b = [ifelse(lt(hq_val, 10), [write(div(rounded(mul(hq_val, 1000)), 1000))], [*comma(rounded(hq_val)), write(V('_q'))])]
    G.clone_rows(hqt, 10, '_hr', add(h0 + 24, mul(ifelse_gt(r_, 5), (h1 - 23) - (h0 + 24))), hy, [show()])
    hqt.on(on_msg('호가그리기'), *hqt_b)

    # ---- 주문 (모드 칩 · 수량 칩 · 매수/매도)
    o0, o1 = L['order']
    def order(direction):
        return [setv('주문방향', direction), setv('주문수량', V('주문단위')), cast('주문')]
    big = 10 ** 12
    P.var('주문단위', 1)
    for j, (lbl, q) in enumerate([('1', 1), ('10', 10), ('100', 100), ('최대', big)]):
        ch_ = sprite(P, sc, '수량칩%d' % j, SA.u_chip(lbl, 33), o0 + 19 + j * 35, -68)
        ch_.on(on_msg('시세갱신'), ifelse(eq(V('주문단위'), q), [shape('on')], [shape('off')]))
        ch_.on(on_click(), setv('주문단위', q), cast('snd:click'), cast('시세갱신'))
    _ubtn(P, sc, '매수버튼', SA.u_button('매수', 68, 20, 'buy'), o0 + 36, -102, order(1))
    _ubtn(P, sc, '매도버튼', SA.u_button('매도', 68, 20, 'sell'), o0 + 108, -102, order(-1))
    t_cash = text(P, sc, '주문가능', '', 18, -32, 6.5, UT, F_BODY, True, 2, w=70, h=9)
    t_hold = text(P, sc, '보유글', '', 8, -43, 6.5, UT, F_BODY, True, 2, w=90, h=9)
    t_eval = text(P, sc, '평가글', '', 8, -54, 6.5, UT, F_BODY, True, 2, w=90, h=9)
    t_tot = text(P, sc, '주문총액', '', 18, -82, 6.5, UT, F_BODY, True, 2, w=70, h=9)
    t_cash.on(on_scene(), forever(*fmt_money(V('돈'), '_m'), write(V('_m')), wait(0.25)))
    hold_b = [ifelse(eq(S, CTL),
                     [*comma(LGET('보유', CTL)), write(join(V('_q'), '주 (', pct2(LGET('보유', CTL)), '%)'))],
                     [*comma(LGET('보유', S)), *won(LGET('평단', S)),
                      write(join(V('_q'), LGET('단위', ifelse_kind(S)), ' · 평단 ', V('_pt')))])]
    eval_b = [ifelse(gt(LGET('보유', S), 0),
                     [*fmt_money(sub(mul(LGET('보유', S), LGET('상품가', S)), mul(LGET('보유', S), LGET('평단', S))), '_m'),
                      setv('_c', round1(mul(sub(div(LGET('상품가', S), LGET('평단', S)), 1), 100))),
                      ifelse(ge(V('_c'), 0), [write(join('+', V('_m'), ' (+', V('_c'), '%)')), text_color(UR)],
                             [write(join(V('_m'), ' (', V('_c'), '%)')), text_color(UB)])],
                     [write('-'), text_color(ULG)])]
    tot_b = [ifelse(eq(V('주문단위'), big), [write('최대 (현금·보유 전부)')],
                    [ifelse(eq(S, CTL), [*fmt_money(mul(mul(V('주문단위'), 100), LGET('주가', CTL)), '_m')],
                            [*fmt_money(mul(V('주문단위'), LGET('주가', S)), '_m')]), write(join('약 ', V('_m')))])]
    for o_, blk in ((t_hold, hold_b), (t_eval, eval_b), (t_tot, tot_b)):
        o_.on(on_msg('시세갱신'), *blk)
    # 주문 모드 (일반/인버스 + 코인·특별주는 레버리지 ×2·×5·×10): 보유 중에는 바꿀 수 없다
    def mode_btn(name, label, w, x, shown, lit, click):
        o = sprite(P, sc, name, SA.u_chip(label, w), x, -18)
        upd = [ifelse(shown, [show(), ifelse(lit, [shape('on')], [shape('off')])], [hide()])]
        o.on(on_msg('시세갱신'), *upd)
        o.on(on_scene(), hide())
        o.on(on_click(), if_(and_(shown, eq(V('게임중'), 0)),
                             ifelse(gt(LGET('보유', S), 0),
                                    [setv('체결글', '보유 중에는 주문 모드를 바꿀 수 없어요 (먼저 정리)'), setv('체결성공', 0), cast('체결')],
                                    [*click, cast('시세갱신'), cast('snd:click')])))
        return o
    dd = LGET('배수', S)
    not_ctl = ne(S, CTL)
    levable = gt(S, COIN0)          # 코인·특별주만 레버리지
    mode_btn('모드롱', '일반', 24, o0 + 14, not_ctl, gt(dd, 0), [lst_set('배수', S, abs_(dd))])
    mode_btn('모드인버스', '인버스', 30, o0 + 43, not_ctl, lt(dd, 0), [lst_set('배수', S, mul(abs_(dd), -1))])
    for k2, w2, x2 in ((1, 19, o0 + 70), (2, 19, o0 + 90), (5, 19, o0 + 110), (10, 23, o0 + 132)):
        mode_btn('모드배%d' % k2, '×%d' % k2, w2, x2, and_(not_ctl, or_(eq(k2, 1), levable)), eq(abs_(dd), k2),
                 [ifelse(lt(dd, 0), [lst_set('배수', S, -k2)], [lst_set('배수', S, k2)])])
    note = text(P, sc, '체결알림', '', -92, 30, 8, '#ffffff', F_BODY, True, 0, w=200, h=16, visible=False, bg=UN)
    note.on(on_msg('체결'), write(V('체결글')), to_front(), show(), wait(1.3), hide())
    P.list('단위', ['주', '주', '주', '개'])     # ifelse_kind: 1 국내/지배, 2 해외, 3 국내, 4 코인

    # ---- 오른쪽: 탭 (국내 / 해외 / 코인 / 특별주1(시장 유세부터) / 특별주2(대통령 유세부터, 더 크게 출렁임))
    r0, r1 = L['right'][0], L['right'][1]
    tw = (r1 - r0) / float(len(TABS))
    P.list('표시순서', ORDER)
    for k, (lbl, base, cnt, need) in enumerate(TABS, 1):
        tb = sprite(P, sc, '탭%d' % k, SA.u_tab(lbl, int(tw) - 1), r0 + tw / 2 + (k - 1) * tw, L['tabs_y'])
        act = [setv('탭', k), setv('탭기준', base), setv('탭개수', cnt), setv('선택종목', ORDER[base]), cast('시세갱신')]
        if need > 1:
            locked = lt(V('단계'), need)
            tb.on(on_msg('시세갱신'), ifelse(locked, [shape('lock')], [ifelse(eq(V('탭'), k), [shape('on')], [shape('off')])]))
            act = [ifelse(locked, [setv('체결글', '%s는 %s 선거부터 열려요' % (lbl, '세종시장' if need == 2 else '대통령')),
                                   setv('체결성공', 0), cast('체결')], act)]
        else:
            tb.on(on_msg('시세갱신'), ifelse(eq(V('탭'), k), [shape('on')], [shape('off')]))
        tb.on(on_click(), *act)

    # ---- 조치원 지배 자본 띠 (게임 목표: 지분 50%)
    c0x, c1x, c0y, c1y = L['ctl']
    card = sprite(P, sc, '지배카드', [('on', SA.u_ctl()), ('sel', SA.u_ctl(True))], (c0x + c1x) / 2, (c0y + c1y) / 2)
    card.on(on_msg('시세갱신'), ifelse(eq(S, CTL), [shape('sel')], [shape('on')]))
    card.on(on_click(), *select_actions(CTL))
    ttl = text(P, sc, '지배이름', '', 117, 81, 6.5, UT, F_BODY, True, 1, w=110, h=9)
    ttl.on(on_msg('시세갱신'), *won(LGET('주가', CTL)), write(join(LGET('주식이름', CTL), '  ', V('_pt'))))
    mine = text(P, sc, '지배내지분', '', 205, 81, 6.5, UN, F_BODY, True, 2, w=60, h=9)
    mine.on(on_msg('시세갱신'), write(join('내 지분 ', E.stake_pct(), '%')))
    cpr = text(P, sc, '지배가격', '', 148, 75, 5.5, UG, F_BODY, False, 0, w=170, h=8)
    cpr.on(on_msg('시세갱신'),
           setv('유통주', sub(sub(sub(D.CONTROL_SHARES, LGET('보유', CTL)), V('첫째주')), V('둘째주'))),
           write(join('첫째 큰아버지 ', pct2(V('첫째주')), '%  ·  둘째 ', pct2(V('둘째주')), '%  ·  유통 ', pct2(V('유통주')), '%')))
    for o in (ttl, mine, cpr):
        o.on(on_click(), *select_actions(CTL))
    bx0, bx1, by = SA.CTL_BAR
    bwid = bx1 - bx0
    bar = sprite(P, sc, '지분막대', SA.u_square((255, 255, 255), 0, 'clear'), bx0, by)
    seg = lambda frac_expr: add(bx0, mul(frac_expr, bwid / float(D.CONTROL_SHARES)))
    bar.on(on_msg('시세갱신'),
           pen_up(), pen_clear(), pen_size(3),
           pen_color('#e3e6ee'), xy(bx0, by), pen_down(), xy(bx1, by), pen_up(),
           setv('_a', LGET('보유', CTL)),
           pen_color(UN), xy(bx0, by), pen_down(), xy(seg(V('_a')), by), pen_up(),
           pen_color(UR), pen_down(), xy(seg(add(V('_a'), V('첫째주'))), by), pen_up(),
           pen_color(SA.UHEX['purple']), pen_down(), xy(seg(add(add(V('_a'), V('첫째주')), V('둘째주'))), by), pen_up(),
           xy(-300, -300))

    # ---- 종목 목록 (탭에 따라 바뀜, 최대 15줄): 줄 바탕 · 이름 · 현재가 · 전일대비 · 거래대금
    j = V('_rj')
    yj = sub(L['row0'], mul(sub(j, 1), L['row_h']))
    idx = LGET('표시순서', add(V('탭기준'), j))
    on_tab = le(j, V('탭개수'))
    tile = sprite(P, sc, '시세칸', SA.u_row_set(), -300, -300, visible=False)
    tile.local('_lp', 0)
    up_ = gt(LGET('주가', idx), mul(V('_lp'), 1.004))
    dn_ = lt(LGET('주가', idx), mul(V('_lp'), 0.996))
    st = [ifelse(on_tab, [show(), setv('_t', 1), if_(up_, setv('_t', 2)), if_(dn_, setv('_t', 3)), if_(eq(S, idx), chg('_t', 3)),
                          shape(V('_t')), setv('_lp', LGET('주가', idx)), wait(0.3), ifelse(eq(S, idx), [shape(4)], [shape(1)])],
                 [hide()])]
    G.clone_rows(tile, ND, '_rj', (r0 + r1) / 2, yj, st)
    tile.on(on_msg('시세갱신'), *st)
    nm = text(P, sc, '종목명', '', -300, -300, 6.5, UT, F_BODY, True, 1, w=52, h=9, visible=False)
    pr = text(P, sc, '종목가', '', -300, -300, 6.5, UT, F_BODY, True, 2, w=50, h=9, visible=False)
    ch = text(P, sc, '종목등락', '', -300, -300, 6.5, UT, F_BODY, True, 2, w=36, h=9, visible=False)
    tv = text(P, sc, '종목대금', '', -300, -300, 5.5, ULG, F_BODY, False, 2, w=36, h=9, visible=False)
    nm_b = [ifelse(on_tab, [write(LGET('주식이름', idx)), show()], [hide()])]
    pr_b = [ifelse(on_tab, [*won(LGET('주가', idx)), write(V('_pt')), *ud_color(idx), show()], [hide()])]
    ch_b = [ifelse(on_tab, [*chg_text(idx), show()], [hide()])]
    tv_b = [ifelse(on_tab, [*tv_text(idx), write(join(V('_q'), '억')), show()], [hide()])]
    G.clone_rows(nm, ND, '_rj', 87, yj, nm_b)
    G.clone_rows(pr, ND, '_rj', 135, yj, pr_b)
    G.clone_rows(ch, ND, '_rj', 180, yj, ch_b)
    G.clone_rows(tv, ND, '_rj', 218, yj, tv_b)
    for o_, blk in ((nm, nm_b), (pr, pr_b), (ch, ch_b), (tv, tv_b)):
        o_.on(on_msg('시세갱신'), *blk)
    for o in (tile, nm, pr, ch, tv):
        o.on(on_click(), if_(on_tab, *select_actions(idx)))

    # ---- 아래 버튼 (오른쪽 아래)
    by_ = -123
    _ubtn(P, sc, '지도로', SA.u_button('돌아가기', 54, 15, 'nav'), 87, by_, ctx['GO_HOME']())
    nego = _ubtn(P, sc, '협상으로', SA.u_button('협상 테이블', 60, 15, 'navy'), 206, by_, go(ctx['S_NEGO']))
    nego.on(on_scene(), ifelse(eq(V('단계'), 1), [show()], [hide()]))
    opsb = _ubtn(P, sc, '작전세력으로', SA.u_button('작전 세력', 60, 15, 'navy'), 206, by_, go(ctx['S_OPS']))
    opsb.on(on_scene(), ifelse(and_(gt(V('단계'), 1), ge(V('직위'), 1)), [show()], [hide()]))
    SG.save_button(P, sc, 146, by_, pic=SA.u_button('지금 저장', 54, 15, 'nav'), hover=False)
    text(P, sc, '단위안내', '수량은 주(코인은 개) · 지배 자본은 100주 단위', -18, -121, 5.5, ULG, F_BODY, False, 0, w=140, h=8)

    # ---- 기세 담당: 한 프레임에 한 종목씩 돌아가며 기세를 바꾼다 (추세는 천천히 이어지고, 많이 벌어지면 평균으로 되돌림)
    gj = V('_gi')
    g_, w_ = LGET('기세속', gj), LGET('기세폭', gj)
    mood_o = text(P, sc, '기세담당', '', -300, -300, 8, visible=False)
    mood_o.on(on_scene(), setv('_gi', 0),
              forever(chg('_gi', 1), if_(gt(V('_gi'), SPEC0), setv('_gi', 1)),
                      if_(le(LGET('기준', gj), 0), lst_set('기준', gj, LGET('주가', gj))),
                      lst_set('기준', gj, add(mul(LGET('기준', gj), 1 - REV_EMA), mul(LGET('주가', gj), REV_EMA))),
                      lst_set('기세속', gj, add(mul(g_, MOOD_KEEP), mul(w_, div(rnd(-100, 100), 100 / MOOD_STEP)))),
                      if_(gt(g_, w_), lst_set('기세속', gj, w_)),
                      if_(lt(g_, mul(w_, -1)), lst_set('기세속', gj, mul(w_, -1))),
                      setv('_rv', mul(LGET('회귀', gj), sub(1, div(LGET('주가', gj), LGET('기준', gj))))),
                      if_(gt(V('_rv'), LGET('되돌림폭', gj)), setv('_rv', LGET('되돌림폭', gj))),
                      if_(lt(V('_rv'), mul(LGET('되돌림폭', gj), -1)), setv('_rv', mul(LGET('되돌림폭', gj), -1))),
                      lst_set('기세', gj, add(g_, V('_rv')))))

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
                *comma(V('매매수량')), setv('체결글', join('매수 체결!  +', V('_q'))), setv('체결성공', 1)],
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
                *comma(V('매매수량')), setv('체결글', join('매도 체결!  -', V('_q'))), setv('체결성공', 1)],
               [setv('체결글', '팔 수량이 없어요'), setv('체결성공', 0)])]
    mgr.on(on_msg('주문'),
           *assets_blocks(),
           setv('_s', V('선택종목')), setv('_p', LGET('주가', V('_s'))),
           ifelse(eq(V('주문방향'), 1), buy, sell),
           setv('돈', div(rounded(mul(V('돈'), 10)), 10)),
           cast('체결'), *assets_blocks(), *_save(), cast('시세갱신'), *E.majority_check())
    mgr.on(on_scene(), *assets_blocks(),
           if_(or_(lt(V('선택종목'), 1), gt(V('선택종목'), N)), setv('선택종목', 1)),
           setv('탭', 1), setv('탭기준', 0), setv('탭개수', ND),
           if_(gt(V('선택종목'), ND), if_(ne(V('선택종목'), CTL), setv('선택종목', 1))),
           cast('시세갱신'),
           forever(wait(TICK_SEC), *market_step(), cast('시세갱신')))
    E.majority_pop(P, sc)
    EC.ticker(P, sc)
    EC.income_pop(P, sc, 120, 126)
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

