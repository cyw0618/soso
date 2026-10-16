# -*- coding: utf-8 -*-
"""시간에 따라 돌아가는 경제: 내 회사 · 실제 기업 인수 · 부동산과 정보꾼 · 작전 세력 · 계약서 서명.

- 실제 시계(엔트리 '현재 시각' 블록)로 10초마다 한 번 '경제 한 걸음'을 돌린다. 화면을 오래 비웠다 와도 최대 30번(5분)치만 쌓인다.
  수입: 직위 급여(평판에 따라) + 정당 후원금 + 내 회사 배당 + 인수한 기업 수익 + 땅 임대료 + 지배 자본 과반 배당(시장·대통령 선거).
- 큰 거래(회사 설립, 기업 인수, 땅 매입, 창당, 작전 세력, 출마 등록)는 '계약서' 장면에서 마우스로 서명해야 체결된다.
돈 단위는 만원.
"""
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, fmt_comma, fmt_money, fmt_price, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
import data as D
import data2 as D2

PERIOD = 10                  # 초
NC = len(D2.COMPANIES)       # 100
NL = len(D2.LANDS)           # 15
NT = len(D2.MYCO_TYPES)      # 5
TAB_START = [0, 40, 75]
TAB_COUNT = [40, 35, 25]
LAND_TAB = [0, 5, 10]

ECON_VARS = dict(마지막시각=0, 주기수입=0, 투자자산=0, 이번수입=0, 인수가치=0, 땅가치합=0, _ci2=0, _li=0, _lp=0,
                 회사상태=0, 회사이름='', 회사업종=1, 회사가치=0, 회사투자=0, 회사부스트=0, 회사소식='', 회사배당=0, 설립업종=1,
                 인수수=0, 인수수입=0, 땅수입=0, 기업탭=1, 기업쪽=1, 선택기업=1, 땅탭=1, 선택땅=1, 정보글='',
                 경제알림='', 작전종목=1, 작전단계=0, 작전틱=0, 작전비용=0, 작전결과='', 작전대상=1, 작전폭=0, 작전위험=0, 작전변호=0,
                 세력비용합=0, 세력힘합=0, 세력위험합=0,
                 계약종류=0, 계약대상=0, 계약금액=0, 계약제목='', 계약내용='', 계약상대='', 서명길이=0, 계약확인=0,
                 결재수=1, 결재타이머=0, 서류번호=0,
                 의혹=0, 수사기관=0, 수사혐의=1, 수사남은=0, 수사위험=60, 수사결과글='', _cf=0, _ca=0, _cp=0,
                 경영력=0, 직원급여합=0, 직원총수=0, 선택직급=9, 후보직급=9, 후보이름='', 후보나이=0, 후보경력=0, 후보능력=50,
                 후보성격=1, 후보급여=0, 질문수=0, 질문1=0, 질문2=0, 질문3=0, 후보정보1='', 후보정보2='', 후보정보3='', _hc=0, _now=0, _el=0, _np=0, _ei=0, _eg=0, _ev=0, _ek=0, _inc=0, _펜=0, _px=0, _py=0)


def setup(P):
    C = D2.COMPANIES
    P.list('기업이름', [c[0] for c in C])
    P.list('기업업종', [c[1] for c in C])
    P.list('기업단계', [c[2] for c in C])
    P.list('기업가격', [c[3] * 10000 for c in C])
    P.list('기업수익률', [c[4] for c in C])
    P.list('인수레벨', [0] * NC)
    P.list('땅이름', [l[0] for l in D2.LANDS])
    P.list('땅단계', [l[1] for l in D2.LANDS])
    P.list('땅기본가', [l[2] * 10000 for l in D2.LANDS])
    P.list('땅가격', [l[2] * 10000 for l in D2.LANDS])
    P.list('땅수익률', [l[3] for l in D2.LANDS])
    P.list('땅보유', [0] * NL)
    P.list('땅예정', [0] * NL)
    P.list('땅배율', [1] * NL)
    P.list('땅호재', D2.LAND_GOOD)
    P.list('땅악재', D2.LAND_BAD)
    P.list('업종이름', [t[0] for t in D2.MYCO_TYPES])
    P.list('업종성장', [t[1] for t in D2.MYCO_TYPES])
    P.list('업종흔들림', [t[2] for t in D2.MYCO_TYPES])
    P.list('업종대박', [t[3] for t in D2.MYCO_TYPES])
    P.list('업종위기', [t[4] for t in D2.MYCO_TYPES])
    P.list('회사호재', D2.MYCO_NEWS_GOOD)
    P.list('회사악재', D2.MYCO_NEWS_BAD)
    P.list('회사기록', [0] * 20)
    P.list('정보꾼이름', [b[0] for b in D2.BROKERS])
    P.list('정보꾼값', [b[1] * 10000 for b in D2.BROKERS])
    P.list('정보꾼확률', [b[2] for b in D2.BROKERS])
    P.list('급여', D2.SALARY)
    P.list('기관이름', D2.AGENCIES)
    P.list('기관짧은', D2.AGENCY_SHORT)
    P.list('매수남은', [0] * len(D2.AGENCIES))
    P.list('혐의기관', [c[0] for c in D2.CHARGES])
    P.list('혐의이름', [c[1] for c in D2.CHARGES])
    P.list('혐의설명', [c[2] for c in D2.CHARGES])
    PO = D2.POSITIONS
    P.list('직급이름', [p[0] for p in PO])
    P.list('직급정원', [p[1] for p in PO])
    P.list('직급급여', [p[2] for p in PO])
    P.list('직급배수', [p[3] for p in PO])
    P.list('직급능력최소', [p[4][0] for p in PO])
    P.list('직급능력최대', [p[4][1] for p in PO])
    P.list('직급경력최소', [p[5][0] for p in PO])
    P.list('직급경력최대', [p[5][1] for p in PO])
    P.list('직원수', [0] * len(PO))
    P.list('직원능력합', [0] * len(PO))
    P.list('성격힌트', D2.TRAIT_HINT)
    P.list('성씨', D2.SURNAMES)
    P.list('이름', D2.GIVEN)
    P.list('세력이름', [m[0] for m in D2.OPS_MEMBERS])
    P.list('세력비용', [m[2] * 10000 for m in D2.OPS_MEMBERS])
    P.list('세력힘', [m[3] for m in D2.OPS_MEMBERS])
    P.list('세력위험', [m[4] for m in D2.OPS_MEMBERS])
    P.list('세력인원', [0] * len(D2.OPS_MEMBERS))


def reset_blocks():
    b = [lst_set('인수레벨', i, 0) for i in range(1, NC + 1)]
    for i in range(1, NL + 1):
        b += [lst_set('땅보유', i, 0), lst_set('땅가격', i, D2.LANDS[i - 1][2] * 10000), lst_set('땅예정', i, 0), lst_set('땅배율', i, 1)]
    b += [lst_set('회사기록', i, 0) for i in range(1, 21)]
    b += [lst_set('매수남은', i, 0) for i in range(1, len(D2.AGENCIES) + 1)]
    b += staff_reset()
    return b


NP = len(D2.POSITIONS)
NA = len(D2.AGENCIES)


def staff_reset():
    return [lst_set('직원수', i, 0) for i in range(1, NP + 1)] + [lst_set('직원능력합', i, 0) for i in range(1, NP + 1)] + \
        [setv('경영력', 0), setv('직원급여합', 0), setv('직원총수', 0)]


def staff_calc():
    """경영력 = Σ(직급별 능력 합 × 직급 배수)/100, 급여 합, 직원 수."""
    b = [setv('경영력', 0), setv('직원급여합', 0), setv('직원총수', 0)]
    for i in range(1, NP + 1):
        b += [chg('경영력', div(mul(LGET('직원능력합', i), LGET('직급배수', i)), 100)),
              chg('직원급여합', mul(LGET('직원수', i), LGET('직급급여', i))), chg('직원총수', LGET('직원수', i))]
    return b + [setv('경영력', round1(V('경영력')))]


# ------------------------------------------------------------------ 계산
def company_value(i):
    L = LGET('인수레벨', i)
    return mul(LGET('기업가격', i), add(1, mul(D2.COMPANY_UP_COST / 2, mul(L, sub(L, 1)))))


def company_income(i):
    L = LGET('인수레벨', i)
    return mul(div(mul(LGET('기업가격', i), LGET('기업수익률', i)), 1000), add(1, mul(D2.COMPANY_UP_INCOME, sub(L, 1))))


def income_sum():
    """10초마다 들어올 돈(주기수입)과 투자자산(인수 기업 장부가 + 땅값) 계산. 합계는 거래할 때마다 갱신해 둔 값을 쓴다."""
    return [setv('투자자산', add(V('인수가치'), V('땅가치합'))),
            setv('회사배당', 0),
            if_(eq(V('회사상태'), 1), setv('회사배당', rounded(div(mul(V('회사가치'), D2.MYCO_PAYOUT), 1000)))),
            setv('주기수입', sub(add(add(V('인수수입'), V('땅수입')), V('회사배당')), V('직원급여합'))),
            if_(gt(V('직위'), 0), chg('주기수입', mul(LGET('급여', add(V('직위'), 1)), add(0.5, div(V('평판'), 100))))),
            if_(eq(V('창당'), 1), chg('주기수입', mul(V('당원'), D2.PARTY_FEE))),
            control_dividend(),
            setv('주기수입', rounded(V('주기수입')))]


income_blocks = income_sum


def recalc_loop():
    """처음부터 다시 셈 (이어하기로 불러온 뒤 등). 반복문이라 몇 프레임 걸린다."""
    return [setv('인수가치', 0), setv('인수수', 0), setv('인수수입', 0), setv('_ci2', 1),
            rep(NC, if_(le(V('_ci2'), NC), if_(gt(LGET('인수레벨', V('_ci2')), 0), chg('인수가치', company_value(V('_ci2'))),
                                                chg('인수수', 1), chg('인수수입', company_income(V('_ci2'))))), chg('_ci2', 1)),
            *land_totals_loop(), *staff_calc(), *income_sum()]


def land_totals_loop():
    return [setv('땅가치합', 0), setv('땅수입', 0), setv('_ci2', 1),
            rep(NL, if_(le(V('_ci2'), NL), if_(eq(LGET('땅보유', V('_ci2')), 1), chg('땅가치합', LGET('땅가격', V('_ci2'))),
                        chg('땅수입', div(mul(LGET('땅가격', V('_ci2')), LGET('땅수익률', V('_ci2'))), 1000)))), chg('_ci2', 1))]


def control_dividend():
    """시장·대통령 선거 중 지배 자본 과반이면 10초마다 시가총액의 0.3% 배당."""
    return if_(and_(gt(V('단계'), 1), gt(LGET('보유', 16), D.CONTROL_GOAL)),
               chg('주기수입', mul(mul(LGET('주가', 16), D.CONTROL_SHARES), 0.003)))


def company_step():
    t = V('회사업종')
    return [if_(eq(V('회사상태'), 1),
                setv('_eg', div(add(rnd(mul(LGET('업종흔들림', t), -1), LGET('업종흔들림', t)), LGET('업종성장', t)), 1000)),
                if_(gt(V('회사부스트'), 0), chg('_eg', 0.012), chg('회사부스트', -1)),
                chg('_eg', mul(V('경영력'), 0.0004)),
                setv('_ek', rnd(1, 100)),
                ifelse(le(V('_ek'), add(LGET('업종대박', t), div(V('경영력'), 40))),
                       [chg('_eg', div(rnd(30, 80), 100)), setv('회사소식', LGET('회사호재', rnd(1, len(D2.MYCO_NEWS_GOOD))))],
                       [if_(gt(V('_ek'), sub(100, sub(LGET('업종위기', t), div(V('경영력'), 15)))),
                            chg('_eg', div(rnd(-45, -25), 100)), setv('회사소식', LGET('회사악재', rnd(1, len(D2.MYCO_NEWS_BAD)))))]),
                setv('회사가치', rounded(mul(V('회사가치'), add(1, V('_eg'))))),
                lst_del('회사기록', 1), lst_add('회사기록', V('회사가치')),
                if_(lt(V('회사가치'), mul(V('회사투자'), 0.15)),
                    setv('회사상태', 2), setv('회사가치', 0), setv('회사소식', '회사가 부도났다... 투자금을 모두 잃었다'),
                    *staff_reset(),
                    setv('경제알림', join(V('회사이름'), ' 부도!')), cast('경제알림')))]


def land_step():
    """땅값 흔들림 + 예정된 개발 소식 터뜨리기 + 합계 (반복문) + 새 소식 예약."""
    i = V('_li')
    body = [lst_set('땅가격', i, rounded(mul(LGET('땅가격', i), add(1, div(rnd(-12, 16), 1000))))),
            if_(gt(LGET('땅예정', i), 0),
                lst_set('땅예정', i, sub(LGET('땅예정', i), 1)), chg('_lp', 1),
                if_(eq(LGET('땅예정', i), 0),
                    lst_set('땅가격', i, rounded(mul(LGET('땅가격', i), LGET('땅배율', i)))),
                    ifelse(gt(LGET('땅배율', i), 1),
                           [setv('경제알림', join(LGET('땅이름', i), ': ', LGET('땅호재', rnd(1, len(D2.LAND_GOOD))), ' 땅값 폭등!'))],
                           [setv('경제알림', join(LGET('땅이름', i), ': ', LGET('땅악재', rnd(1, len(D2.LAND_BAD))), ' 땅값 폭락'))]),
                    lst_set('땅배율', i, 1), cast('경제알림'))),
            if_(eq(LGET('땅보유', i), 1), chg('땅가치합', LGET('땅가격', i)),
                chg('땅수입', div(mul(LGET('땅가격', i), LGET('땅수익률', i)), 1000))),
            chg('_li', 1)]
    return [setv('_li', 1), setv('_lp', 0), setv('땅가치합', 0), setv('땅수입', 0), rep(NL, if_(le(V('_li'), NL), *body[:-1]), body[-1]),
            # 새 개발 소식 예약 (진행 중인 것이 없을 때 25%)
            if_(and_(and_(eq(V('_lp'), 0), gt(V('직위'), 0)), le(rnd(1, 100), 25)),
                setv('_ei', rnd(1, mul(5, ifelse_min3(V('직위'))))),
                lst_set('땅예정', V('_ei'), rnd(6, 12)),
                ifelse(le(rnd(1, 100), 72), [lst_set('땅배율', V('_ei'), div(rnd(20, 38), 10))],
                       [lst_set('땅배율', V('_ei'), div(rnd(4, 7), 10))]))]


def clamp13(v):
    """min(3, max(1, v)) (정수)."""
    mx = div(add(add(v, 1), abs_(sub(v, 1))), 2)
    return ifelse_min3(mx)


def ifelse_min3(v):
    """min(v, 3) (정수)."""
    return sub(3, div(add(sub(3, v), abs_(sub(3, v))), 2))


def docs_step():
    return [if_(gt(V('직위'), 0), chg('결재타이머', mul(V('_np'), PERIOD)),
                if_(ge(V('결재타이머'), D2.DOC_REFILL), setv('결재타이머', 0), if_(lt(V('결재수'), 3), chg('결재수', 1))))]


def bribe_mult():
    return LGET('상점배율', clamp13(V('직위')))


def case_step():
    """검찰·금감원·노동청·공정위 수사 (세종시장 이상). 의혹이 클수록, 직원·인수 기업이 많을수록 잘 들어온다.
    미리 매수해 둔 기관은 그 시간 동안 수사를 하지 않는다."""
    return [*[if_(gt(LGET('매수남은', a), 0), lst_set('매수남은', a, sub(LGET('매수남은', a), mul(V('_np'), PERIOD))),
                  if_(lt(LGET('매수남은', a), 0), lst_set('매수남은', a, 0))) for a in range(1, NA + 1)],
            if_(gt(V('의혹'), 0), chg('의혹', mul(V('_np'), -0.5)), if_(lt(V('의혹'), 0), setv('의혹', 0))),
            ifelse(gt(V('수사기관'), 0),
                   [chg('수사남은', mul(V('_np'), -PERIOD)),
                    ifelse(le(V('수사남은'), 0), case_verdict(),
                           [if_(eq(mod(V('수사남은'), 30), 0),
                                setv('경제알림', join('⚖ ', LGET('기관짧은', V('수사기관')), ' 수사 중! 남은 ', V('수사남은'),
                                                      '초 · 집무실 「수사 대응」')), cast('경제알림'))])],
                   [if_(ge(V('직위'), 2),
                        setv('_ca', rnd(1, NA)),
                        setv('_cp', add(1, div(V('의혹'), 10))),
                        if_(eq(V('_ca'), 3), chg('_cp', div(V('직원총수'), 10))),
                        if_(eq(V('_ca'), 4), chg('_cp', div(V('인수수'), 3))),
                        if_(and_(le(rnd(1, 100), V('_cp')), le(LGET('매수남은', V('_ca')), 0)),
                            setv('수사기관', V('_ca')), setv('수사혐의', add(mul(sub(V('_ca'), 1), 5), rnd(1, 5))),
                            setv('수사남은', mul(rnd(D2.CASE_TIME[0] // 10, D2.CASE_TIME[1] // 10), 10)), setv('수사위험', D2.CASE_RISK),
                            setv('경제알림', join(LGET('기관이름', V('_ca')), ' ', LGET('혐의이름', V('수사혐의')),
                                                  ' 수사 착수! 집무실 「수사 대응」에서 막으세요')),
                            cast('경제알림')))])]


def case_verdict():
    return [ifelse(le(rnd(1, 100), V('수사위험')),
                   [setv('_cf', rounded(mul(V('총자산'), D2.CASE_FINE / 100.0))), if_(lt(V('_cf'), 0), setv('_cf', 0)),
                    chg('돈', mul(V('_cf'), -1)), chg('평판', -20), if_(lt(V('평판'), 0), setv('평판', 0)),
                    if_(eq(V('캠페인중'), 1), chg('내지지율', -4), if_(lt(V('내지지율'), 0.5), setv('내지지율', 0.5))),
                    chg('의혹', 10), *fmt_money(V('_cf'), '_m'),
                    setv('수사결과글', join(LGET('기관짧은', V('수사기관')), ' 수사 결과 유죄! 벌금 ', V('_m'), ', 평판 -20'))],
                   [chg('평판', 3), setv('수사결과글', join(LGET('기관짧은', V('수사기관')), ' 수사 결과 무혐의!'))]),
            setv('수사기관', 0), setv('경제알림', V('수사결과글')), cast('경제알림')]


def tick_blocks():
    """1초마다: 실제 시각을 보고 10초가 지났으면 경제 한 걸음."""
    return [setv('_now', now_sec()),
            if_(or_(eq(V('마지막시각'), 0), or_(lt(V('_now'), V('마지막시각')), gt(sub(V('_now'), V('마지막시각')), 86400))),
                setv('마지막시각', V('_now'))),
            setv('_el', sub(V('_now'), V('마지막시각'))),
            if_(ge(V('_el'), PERIOD),
                setv('_np', floor(div(V('_el'), PERIOD))),
                chg('마지막시각', mul(V('_np'), PERIOD)),
                if_(gt(V('_np'), 30), setv('_np', 30)),
                *company_step(), *land_step(), *docs_step(), *case_step(), *income_sum(),
                setv('이번수입', mul(V('주기수입'), V('_np'))),
                chg('돈', V('이번수입')),
                if_(ne(V('이번수입'), 0), cast('수입팝')),
                cast('경제갱신'))]


def ticker(P, sc):
    o = text(P, sc, '경제시계', '', -300, -300, 8, visible=False)
    o.on(on_scene(), *income_sum(), forever(wait(1), *tick_blocks()))
    return o


def income_pop(P, sc, x=-150, y=104):
    """돈 옆에 '+1.2억' 이 떠올랐다 사라짐."""
    t = text(P, sc, '수입팝', '', x, y, 10, '#7CFFB2', F_NUM, False, 0, w=120, h=15, visible=False)
    t.on(on_msg('수입팝'), *fmt_money(V('이번수입'), '_m'),
         ifelse(ge(V('이번수입'), 0), [write(join('+', V('_m'))), text_color('#7CFFB2')], [write(V('_m')), text_color(C_RED)]),
         xy(x, y), to_front(), show(), rep(20, mvy(0.6), wait(0.03)), hide())
    note = text(P, sc, '경제알림', '', 0, -100, 9, C_WHITE, F_NUM, False, 0, w=320, h=16, visible=False, bg=C_BOX)
    note.on(on_msg('경제알림'), write(V('경제알림')), to_front(), show(), wait(2.6), hide())
    return t


# ------------------------------------------------------------------ 계약서
CONTRACT_KINDS = {}      # 종류 번호 → (적용 블록, 돌아갈 장면 블록)


def contract_go(ctx, kind, target, amount, title, body, party):
    """계약서 장면으로 (돈 확인은 부르는 쪽에서)."""
    return [setv('계약종류', kind), setv('계약대상', target), setv('계약금액', amount), setv('계약제목', title),
            setv('계약내용', body), setv('계약상대', party), *go(ctx['S_CONTRACT'])]


def build_contract(P, ctx):
    sc = ctx['S_CONTRACT']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    paper = sprite(P, sc, '계약서종이', _paper_art(), 0, -4)
    paper.on(on_scene(), paper.pct(94), rep(6, paper.grow_pct(1), wait(0.02)))
    tt = text(P, sc, '계약제목', '', 0, 104, 16, '#1A2050', F_NUM, False, 0, w=300, h=24)
    tt.on(on_scene(), write(V('계약제목')))
    body = text(P, sc, '계약본문', '', 0, 52, 9, '#202640', F_BODY, True, 1, w=290, h=70)
    body.on(on_scene(), write(V('계약내용')))
    amt = text(P, sc, '계약금액', '', 0, 6, 12, '#B0182E', F_NUM, False, 0, w=290, h=18)
    amt.on(on_scene(), *fmt_money(V('계약금액'), '_m'), write(join('계약 금액: ', V('_m'))))
    who = text(P, sc, '계약당사자', '', -60, -24, 9, '#202640', F_BODY, True, 1, w=170, h=30)
    who.on(on_scene(), write(join('갑: ', V('계약상대'), '\n을: 막내 (아래에 서명)')))
    dt = text(P, sc, '계약날짜', '', 96, -24, 9, '#202640', F_BODY, True, 2, w=110, h=14)
    dt.on(on_scene(), write(join(date_('YEAR'), '년 ', date_('MONTH'), '월 ', date_('DAY'), '일')))
    text(P, sc, '서명안내', '마우스를 누른 채로 아래 칸에 서명하세요', 0, -40, 8, '#56607E', F_BODY, True, 0, w=260, h=12)
    # 서명 펜
    BX0, BX1, BY0, BY1 = -110, 110, -96, -50
    pen = sprite(P, sc, '서명펜', K.icon_img('star', 2), 0, -300)
    inside = and_(and_(gt(mouse_x(), BX0), lt(mouse_x(), BX1)), and_(gt(mouse_y(), BY0), lt(mouse_y(), BY1)))
    pen.on(on_scene(), pen_up(), pen_clear(), setv('서명길이', 0), setv('_펜', 0), setv('계약확인', 0),
           pen_color('#1A2050'), pen_size(3),
           forever(ifelse(and_(mouse_down(), and_(inside, eq(V('계약확인'), 0))),
                          [ifelse(eq(V('_펜'), 0), [xy(mouse_x(), mouse_y()), pen_down(), setv('_펜', 1)],
                                  [setv('_px', obj_x()), setv('_py', obj_y()), xy(mouse_x(), mouse_y()),
                                   chg('서명길이', add(abs_(sub(obj_x(), V('_px'))), abs_(sub(obj_y(), V('_py')))))])],
                          [if_(eq(V('_펜'), 1), pen_up(), setv('_펜', 0))])))
    pen.on(on_msg('서명지우기'), pen_up(), pen_clear(), setv('서명길이', 0), setv('_펜', 0))
    note = text(P, sc, '계약알림', '', 0, -118, 9, C_WHITE, F_NUM, False, 0, w=300, h=15, visible=False, bg=C_BOX)
    note.on(on_msg('계약알림'), write(V('경제알림')), to_front(), show(), wait(1.8), hide())
    # 도장
    G.big_pop(P, sc, '계약도장', K.big_text('계약 체결!', 34, 'red'), 120, -60, '계약체결', hold=0.8, fade=False)
    # 버튼
    button(P, sc, '다시쓰기', '다시 쓰기', -188, -60, 80, 24, 'gray', actions=[if_(eq(V('계약확인'), 0), cast('서명지우기'))])
    ok = [if_(eq(V('계약확인'), 0),
              ifelse(ge(V('서명길이'), 60),
                     [setv('계약확인', 1), cast('계약체결'), G.sfx('stamp'), wait(1.3), cast('계약적용')],
                     [setv('경제알림', '서명란에 마우스로 서명해 주세요!'), cast('계약알림'), G.sfx('bad')]))]
    button(P, sc, '서명완료', '서명 완료', 188, -60, 84, 26, 'royal', icon='star', actions=ok)
    cancel = [if_(eq(V('계약확인'), 0), setv('계약확인', 2), cast('계약취소'))]
    button(P, sc, '계약취소', '취소', -188, -92, 80, 22, 'navy', icon='back', actions=cancel)
    mgr = text(P, sc, '계약담당', '', -300, -300, 8, visible=False)
    apply_chain = []
    back_chain = []
    for kind, (apply_blocks, back_blocks) in sorted(CONTRACT_KINDS.items()):
        apply_chain.append(if_(eq(V('계약종류'), kind), *apply_blocks))
        back_chain.append(if_(eq(V('계약종류'), kind), *back_blocks))
    mgr.on(on_msg('계약적용'), *apply_chain, *back_chain)
    mgr.on(on_msg('계약취소'), *back_chain)
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])


def _paper_art():
    import os
    from PIL import Image, ImageDraw, ImageFilter
    from art_common import ensure_out, font
    p = os.path.join(ensure_out(), 'contract_paper.png')
    if os.path.exists(p):
        return p
    S = 2
    w, h = 320 * S, 252 * S
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((26, 30, w + 26, h + 30), 10, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, w + 20, h + 20), 10, fill=(250, 246, 234, 255), outline=(190, 170, 130, 255), width=3)
    d.rectangle((34, 34, w + 6, h + 6), outline=(200, 180, 140, 255), width=2)
    for k in range(9):
        y = 20 + (50 + k * 13) * S
        d.line((50, y, w - 10, y), fill=(225, 215, 190, 255), width=1)
    # 서명 칸 (무대 좌표 -110~110, -96~-50 → 종이 기준)
    cx, cy = (w + 40) / 2, (h + 40) / 2 + 4 * S
    x0, x1 = cx - 110 * S, cx + 110 * S
    y0, y1 = cy + 50 * S, cy + 96 * S
    for x in range(int(x0), int(x1), 14):
        d.line((x, y0, x + 7, y0), fill=(160, 150, 130, 255), width=2)
        d.line((x, y1, x + 7, y1), fill=(160, 150, 130, 255), width=2)
    for y in range(int(y0), int(y1), 14):
        d.line((x0, y, x0, y + 7), fill=(160, 150, 130, 255), width=2)
        d.line((x1, y, x1, y + 7), fill=(160, 150, 130, 255), width=2)
    d.text((x0 + 8, y0 + 6), '서명', font=font('nsrb', 11 * S), fill=(170, 160, 140, 255))
    im.save(p)
    return p


# ------------------------------------------------------------------ 내 회사
def build_company(P, ctx):
    sc = ctx['S_COMPANY']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('내 회사', 120, 30, 'royal'), 0, 116)
    alive = eq(V('회사상태'), 1)
    # ---- 설립 화면
    found = []
    found.append(panel(P, sc, '설립판', 0, -12, 450, 190, 'glass', header='royal'))
    found.append(text(P, sc, '설립설명', '초기 자금 10억으로 회사를 세워요. 업종마다 성장 속도와 위험이 달라요.\n'
                                       '회사는 크게 성장할 수도, 망할 수도 있어요. 10초마다 가치의 1.2%를 배당받아요.',
                      0, 52, 9, C_WHITE, F_BODY, True, 0, w=420, h=30))
    dead = text(P, sc, '부도안내', '지난 회사는 부도났어요... 다시 도전해 보세요!', 0, 74, 9, C_RED, F_NUM, False, 0, w=400, h=14,
                visible=False)
    for k in range(1, NT + 1):
        x = -176 + (k - 1) * 88
        t = D2.MYCO_TYPES[k - 1]
        card = sprite(P, sc, '업종카드%d' % k, [('n', K.panel(82, 70, 'card')), ('s', K.panel(82, 70, 'card', header='royal'))], x, -2)
        nm = text(P, sc, '업종이름%d' % k, t[0], x, 18, 10, C_WHITE, F_NUM, False, 0, w=78, h=14)
        grow = min(5, max(1, round(t[1] - 2)))
        risk = min(5, max(1, round(t[2] / 18)))
        info = text(P, sc, '업종정보%d' % k, '성장 %s\n위험 %s' % ('●' * grow + '○' * (5 - grow), '●' * risk + '○' * (5 - risk)),
                    x, -10, 8, C_DIM, F_BODY, True, 0, w=78, h=26)
        sel = [setv('설립업종', k), cast('설립갱신')]
        for o in (card, nm, info):
            o.on(on_click(), *sel)
            found.append(o)
        card.on(on_msg('설립갱신'), ifelse(eq(V('설립업종'), k), [shape('s'), card.pct(106)], [shape('n'), card.pct(100)]))
    asker = sprite(P, sc, '이름묻기', K.icon_img('star', 2), 0, -40)
    start = button(P, sc, '설립버튼', '회사 설립 (10억)', 0, -80, 140, 28, 'royal', icon='shop',
                   actions=[cast('설립시작')])
    found.append(start)
    asker.on(on_msg('설립시작'),
             ifelse(lt(V('돈'), D2.MYCO_START),
                    [setv('경제알림', '현금 10억이 필요해요!'), cast('경제알림'), G.sfx('bad')],
                    [ask('회사 이름을 입력하세요 (예: 막내전자)'),
                     setv('회사이름', str_replace(str_replace(answer(), '[|§]', ''), ' ', '')),
                     if_(eq(slen(V('회사이름')), 0), setv('회사이름', '막내전자')),
                     if_(gt(slen(V('회사이름')), 10), setv('회사이름', substr(V('회사이름'), 1, 10))),
                     *contract_go(ctx, 1, V('설립업종'), D2.MYCO_START, '회사 설립 계약서',
                                  join('1. 을은 「', V('회사이름'), '」(업종: ', LGET('업종이름', V('설립업종')),
                                       ')을 설립하고 자본금 10억 원을 납입한다.\n2. 회사의 성장과 손실은 모두 을이 책임진다.\n'
                                       '3. 회사 가치의 1.2%를 10초마다 배당받는다.'),
                                  '조치원 법무사 사무소')]))
    # ---- 운영 화면
    run = []
    run.append(panel(P, sc, '회사판', -112, -10, 232, 196, 'glass', header='royal'))
    nm = text(P, sc, '회사명', '', -112, 76, 14, C_WHITE, F_NUM, False, 0, w=220, h=20)
    nm.on(on_msg('회사갱신'), write(V('회사이름')))
    st = text(P, sc, '회사단계', '', -112, 58, 9, C_ACC, F_BODY, True, 0, w=220, h=13)
    stage_b = []
    for th, lbl in D2.MYCO_STAGES:        # 큰 기준이 바깥쪽에 오도록 작은 것부터 감싼다
        stage_b = [ifelse(ge(V('회사가치'), th), [setv('_q', lbl)], stage_b or [setv('_q', '스타트업')])]
    st.on(on_msg('회사갱신'), *stage_b, write(join(LGET('업종이름', V('회사업종')), ' · ', V('_q'))))
    val = text(P, sc, '회사가치', '', -112, 34, 16, C_WHITE, F_NUM, False, 0, w=220, h=22)
    val.on(on_msg('회사갱신'), *fmt_money(V('회사가치'), '_m'), write(join('가치 ', V('_m'))))
    inv = text(P, sc, '회사투자', '', -112, 14, 9, C_DIM, F_BODY, True, 0, w=220, h=13)
    inv.on(on_msg('회사갱신'), *fmt_money(V('회사투자'), '_m'),
           setv('_c', round1(mul(sub(div(V('회사가치'), V('회사투자')), 1), 100))),
           ifelse(ge(V('_c'), 0), [write(join('넣은 돈 ', V('_m'), ' · 수익 +', V('_c'), '%')), text_color(C_RED)],
                  [write(join('넣은 돈 ', V('_m'), ' · 손실 ', V('_c'), '%')), text_color(C_BLUE)]))
    div_t = text(P, sc, '회사배당', '', -112, 0, 9, C_ACC, F_BODY, True, 0, w=220, h=13)
    div_t.on(on_msg('회사갱신'), *fmt_money(V('회사배당'), '_m'), write(join('10초마다 배당 +', V('_m'))))
    news = text(P, sc, '회사소식', '', -112, -98, 8, C_WHITE, F_BODY, True, 0, w=220, h=13)
    news.on(on_msg('회사갱신'), write(join('소식: ', V('회사소식'))))
    run += [nm, st, val, inv, div_t, news]
    # 가치 그래프 (최근 20번)
    chart = sprite(P, sc, '회사그래프', K.icon_img('star', 2), 0, -300)
    X0, XW, Y0, YH = -212, 200, -88, 70
    draw = [pen_up(), pen_clear(), setv('_mn', LGET('회사기록', 1)), setv('_mx', V('_mn'))]
    for i in range(1, 21):
        draw += [if_(lt(LGET('회사기록', i), V('_mn')), setv('_mn', LGET('회사기록', i))),
                 if_(gt(LGET('회사기록', i), V('_mx')), setv('_mx', LGET('회사기록', i)))]
    draw += [setv('_rg', sub(V('_mx'), V('_mn'))), if_(le(V('_rg'), 0), setv('_rg', 1)),
             ifelse(ge(LGET('회사기록', 20), LGET('회사기록', 1)), [pen_color('#ff3b55')], [pen_color('#3f7bff')]), pen_size(2)]
    for i in range(1, 21):
        draw += [xy(X0 + (i - 1) * XW / 19.0, add(Y0, mul(div(sub(LGET('회사기록', i), V('_mn')), V('_rg')), YH))), pen_down()]
    draw += [pen_up(), xy(-300, -300)]
    chart.on(on_msg('회사갱신'), ifelse(alive, draw, [pen_clear()]))
    # 오른쪽: 투자 / 매각
    run.append(panel(P, sc, '투자판', 126, -10, 214, 196, 'glass', header='purple'))
    run.append(text(P, sc, '투자제목', '추가 투자', 126, 76, 13, C_WHITE, F_NUM, False, 0, w=200, h=18))
    run.append(text(P, sc, '투자설명', '투자하면 가치가 오르고\n한동안 더 빨리 성장해요', 126, 52, 9, C_DIM, F_BODY, True, 0, w=200, h=28))
    for j, pct in enumerate((10, 30, 50)):
        amount = rounded(mul(V('돈'), pct / 100.0))
        b = button(P, sc, '투자버튼%d' % j, '현금의 %d%% 투자' % pct, 126, 20 - j * 30, 150, 24, 'royal', icon='coin',
                   actions=[if_(eq(V('회사상태'), 1),
                                ifelse(gt(amount, 0),
                                       [setv('_ev', amount), chg('돈', mul(V('_ev'), -1)), chg('회사가치', V('_ev')),
                                        chg('회사투자', V('_ev')), chg('회사부스트', 6),
                                        *fmt_money(V('_ev'), '_m'), setv('경제알림', join(V('_m'), ' 투자 완료! 한동안 빠르게 성장해요')),
                                        cast('경제알림'), G.sfx('cash'), *income_blocks(), cast('회사갱신')],
                                       [setv('경제알림', '현금이 없어요!'), cast('경제알림')]))])
        run.append(b)
    sell = button(P, sc, '매각버튼', '회사 매각 (가치의 90%)', 126, -76, 170, 24, 'gray', icon='coin',
                  actions=[if_(eq(V('회사상태'), 1), chg('돈', rounded(mul(V('회사가치'), 0.9))), setv('회사상태', 0),
                               setv('회사가치', 0), setv('회사투자', 0), *staff_reset(), setv('경제알림', '회사를 매각했어요! 직원들도 함께 넘어갔어요'),
                               cast('경제알림'),
                               G.sfx('cash'), *income_blocks(), cast('회사화면'))])
    run.append(sell)
    hire_b = button(P, sc, '면접버튼', '직원 면접·채용', 126, -100, 150, 22, 'purple', icon='person', actions=go(ctx['S_HIRE']))
    run.append(hire_b)
    staff_t = text(P, sc, '직원요약', '', -112, -14, 8, C_VIOLET, F_NUM, False, 0, w=220, h=12)
    staff_t.on(on_msg('회사갱신'), *fmt_money(V('직원급여합'), '_m'),
               write(join('직원 ', V('직원총수'), '명 · 경영력 ', V('경영력'), ' · 급여 -', V('_m'), '/10초')))
    run.append(staff_t)
    for o in found:
        o.on(on_msg('회사화면'), ifelse(alive, [hide()], [show()]))
    for o in run:
        o.on(on_msg('회사화면'), ifelse(alive, [show()], [hide()]))
    dead.on(on_msg('회사화면'), ifelse(eq(V('회사상태'), 2), [show()], [hide()]))
    chart.on(on_msg('회사화면'), cast('회사갱신'))
    mgr = text(P, sc, '회사담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), cast('회사화면'), cast('설립갱신'), cast('회사갱신'))
    mgr.on(on_msg('경제갱신'), cast('회사갱신'), if_(eq(V('회사상태'), 2), cast('회사화면')))
    button(P, sc, '돌아가기', '돌아가기', -196, -121, 76, 22, 'navy', icon='back', actions=ctx['GO_HOME']())
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])
    # 계약 적용: 설립
    CONTRACT_KINDS[1] = ([if_(ge(V('돈'), D2.MYCO_START), chg('돈', -D2.MYCO_START), setv('회사상태', 1),
                              setv('회사업종', V('계약대상')), setv('회사가치', D2.MYCO_START), setv('회사투자', D2.MYCO_START),
                              setv('회사부스트', 0), setv('회사소식', '회사를 세웠다! 이제 직원을 뽑아 보자.'), *staff_reset(),
                              *[lst_set('회사기록', i, D2.MYCO_START) for i in range(1, 21)])],
                         go(sc))


# ------------------------------------------------------------------ 기업 인수
def build_ma(P, ctx):
    sc = ctx['S_MA']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('기업 인수', 130, 30, 'royal'), 0, 116)
    P.list('기업탭시작', TAB_START)
    P.list('기업탭개수', TAB_COUNT)
    for k, (lbl, col) in enumerate((('군수 (40개)', 'royal'), ('시장 (35개)', 'purple'), ('대통령 (25개)', 'red')), 1):
        tb = sprite(P, sc, '기업탭%d' % k, [('off', K.badge(lbl, 92, 18, 'navy')), ('on', K.badge(lbl, 92, 18, col)),
                                         ('lock', K.badge('잠김 · ' + lbl.split(' ')[0], 92, 18, 'gray'))], -184 + (k - 1) * 98, 86)
        tb.on(on_msg('기업갱신'), ifelse(lt(V('직위'), k), [shape('lock')], [ifelse(eq(V('기업탭'), k), [shape('on')], [shape('off')])]))
        tb.on(on_click(), ifelse(lt(V('직위'), k),
                                 [setv('경제알림', join(LGET('직위이름', add(k, 1)), '이(가) 되면 열려요!')), cast('경제알림')],
                                 [setv('기업탭', k), setv('기업쪽', 1), setv('선택기업', TAB_START[k - 1] + 1), cast('기업갱신')]))
    base = add(LGET('기업탭시작', V('기업탭')), mul(sub(V('기업쪽'), 1), 10))
    cnt = LGET('기업탭개수', V('기업탭'))
    cards = [('n', K.panel(116, 28, 'card')), ('own', K.panel(116, 28, 'card', header='royal')),
             ('sel', K.panel(116, 28, 'glass', header='purple'))]
    for j in range(1, 11):
        c, r = (j - 1) % 2, (j - 1) // 2
        x, y = -172 + c * 120, 56 - r * 31
        idx = add(base, j)
        on = le(add(mul(sub(V('기업쪽'), 1), 10), j), cnt)
        cd = sprite(P, sc, '기업칸%d' % j, cards, x, y)
        n1 = text(P, sc, '기업칸이름%d' % j, '', x, y + 6, 8, C_WHITE, F_NUM, False, 0, w=110, h=12)
        n2 = text(P, sc, '기업칸값%d' % j, '', x, y - 6, 7, C_DIM, F_BODY, True, 0, w=110, h=11)
        cd.on(on_msg('기업갱신'), ifelse(on, [show(), ifelse(eq(V('선택기업'), idx), [shape('sel')],
                                                                [ifelse(gt(LGET('인수레벨', idx), 0), [shape('own')], [shape('n')])])],
                                          [hide()]))
        n1.on(on_msg('기업갱신'), ifelse(on, [write(LGET('기업이름', idx)), show()], [hide()]))
        n2.on(on_msg('기업갱신'), ifelse(on, [ifelse(gt(LGET('인수레벨', idx), 0),
                                                     [write(join('보유 Lv', LGET('인수레벨', idx), ' · ', LGET('기업업종', idx))), text_color(C_ACC)],
                                                     [*fmt_money(LGET('기업가격', idx), '_m'), write(join(V('_m'), ' · ', LGET('기업업종', idx))),
                                                      text_color(C_DIM)])], [hide()]))
        for o in (cd, n1, n2):
            o.on(on_click(), if_(on, setv('선택기업', idx), cast('기업갱신')))
    pg = text(P, sc, '기업쪽글', '', -112, -102, 9, C_WHITE, F_NUM, False, 0, w=80, h=14)
    pg.on(on_msg('기업갱신'), write(join(V('기업쪽'), ' / ', ceil_(div(cnt, 10)), '쪽')))
    button(P, sc, '기업이전', '◀', -172, -102, 34, 20, 'navy', actions=[if_(gt(V('기업쪽'), 1), chg('기업쪽', -1), cast('기업갱신'))])
    button(P, sc, '기업다음', '▶', -52, -102, 34, 20, 'navy',
           actions=[if_(lt(mul(V('기업쪽'), 10), cnt), chg('기업쪽', 1), cast('기업갱신'))])
    # 오른쪽 상세
    S = V('선택기업')
    L = LGET('인수레벨', S)
    panel(P, sc, '기업상세판', 132, -8, 200, 196, 'glass', header='royal')
    d1 = text(P, sc, '기업상세이름', '', 132, 74, 13, C_WHITE, F_NUM, False, 0, w=190, h=18)
    d2 = text(P, sc, '기업상세업종', '', 132, 57, 9, C_DIM, F_BODY, True, 0, w=190, h=13)
    d3 = text(P, sc, '기업상세정보', '', 132, 24, 9, C_WHITE, F_BODY, True, 0, w=186, h=52)
    d1.on(on_msg('기업갱신'), write(LGET('기업이름', S)))
    d2.on(on_msg('기업갱신'), write(join(LGET('기업업종', S), ' · ', LGET('직위이름', add(LGET('기업단계', S), 1)), '급')))
    d3.on(on_msg('기업갱신'),
          ifelse(gt(L, 0),
                 [*fmt_money(company_value(S), '_m'), setv('_q', V('_m')), *fmt_money(company_income(S), '_m'),
                  write(join('보유 중 · 레벨 ', L, '/', D2.COMPANY_MAX_LV, '\n장부 가치 ', V('_q'), '\n10초마다 +', V('_m')))],
                 [*fmt_money(LGET('기업가격', S), '_m'), setv('_q', V('_m')),
                  *fmt_money(div(mul(LGET('기업가격', S), LGET('기업수익률', S)), 1000), '_m'),
                  write(join('인수가 ', V('_q'), '\n10초마다 +', V('_m'), '\n투자해서 키우면 수익이 늘어요'))]))
    up_cost = mul(mul(LGET('기업가격', S), D2.COMPANY_UP_COST), L)
    b_buy = button(P, sc, '인수버튼', '인수 계약', 132, -36, 120, 24, 'royal', icon='shop',
                   actions=[if_(eq(L, 0),
                                ifelse(lt(V('직위'), LGET('기업단계', S)),
                                       [setv('경제알림', '아직 인수할 수 없는 등급이에요!'), cast('경제알림')],
                                       [ifelse(ge(V('돈'), LGET('기업가격', S)),
                                               [*contract_go(ctx, 2, S, LGET('기업가격', S), '기업 인수 계약서',
                                                             join('1. 갑은 「', LGET('기업이름', S), '」의 경영권(지분 100%)을 을에게 넘긴다.\n'
                                                                  '2. 을은 인수 대금을 계약 즉시 지급한다.\n3. 인수 후 생기는 이익과 손실은 을에게 속한다.'),
                                                             join(LGET('기업이름', S), ' 대주주 일동'))],
                                               [setv('경제알림', '현금이 부족해요!'), cast('경제알림'), G.sfx('bad')])]))])
    b_up = button(P, sc, '키우기버튼', '투자해서 키우기', 132, -64, 130, 24, 'purple', icon='up',
                  actions=[if_(and_(gt(L, 0), lt(L, D2.COMPANY_MAX_LV)),
                               ifelse(ge(V('돈'), up_cost),
                                      [chg('돈', mul(up_cost, -1)), chg('인수가치', up_cost),
                                       chg('인수수입', mul(div(mul(LGET('기업가격', S), LGET('기업수익률', S)), 1000), D2.COMPANY_UP_INCOME)),
                                       lst_set('인수레벨', S, add(L, 1)),
                                       setv('경제알림', join(LGET('기업이름', S), ' 레벨 업! 수익이 늘었어요')), cast('경제알림'),
                                       G.sfx('cash'), *income_blocks(), cast('기업갱신')],
                                      [setv('경제알림', '현금이 부족해요!'), cast('경제알림'), G.sfx('bad')]))])
    upc = text(P, sc, '키우기비용', '', 132, -82, 8, C_DIM, F_BODY, True, 0, w=190, h=12)
    upc.on(on_msg('기업갱신'), ifelse(and_(gt(L, 0), lt(L, D2.COMPANY_MAX_LV)), [*fmt_money(up_cost, '_m'), write(join('키우기 비용 ', V('_m'))), show()],
                                      [hide()]))
    b_sell = button(P, sc, '매각버튼', '매각 (80%)', 132, -100, 100, 22, 'gray', icon='coin',
                    actions=[if_(gt(L, 0), chg('돈', rounded(mul(company_value(S), D2.COMPANY_SELL))),
                                 chg('인수가치', mul(company_value(S), -1)), chg('인수수입', mul(company_income(S), -1)), chg('인수수', -1),
                                 lst_set('인수레벨', S, 0),
                                 setv('경제알림', join(LGET('기업이름', S), ' 매각 완료')), cast('경제알림'), G.sfx('coin'),
                                 *income_blocks(), cast('기업갱신'))])
    b_buy.on(on_msg('기업갱신'), ifelse(eq(L, 0), [show()], [hide()]))
    b_up.on(on_msg('기업갱신'), ifelse(and_(gt(L, 0), lt(L, D2.COMPANY_MAX_LV)), [show()], [hide()]))
    b_sell.on(on_msg('기업갱신'), ifelse(gt(L, 0), [show()], [hide()]))
    sumt = text(P, sc, '기업요약', '', 60, -121, 9, C_ACC, F_NUM, False, 0, w=230, h=14)
    sumt.on(on_msg('기업갱신'), *fmt_money(V('인수수입'), '_m'), write(join('보유 ', V('인수수'), '개 · 10초마다 +', V('_m'))))
    mgr = text(P, sc, '기업담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), if_(gt(V('기업탭'), V('직위')), setv('기업탭', 1), setv('기업쪽', 1)),
           if_(or_(lt(V('선택기업'), 1), gt(V('선택기업'), NC)), setv('선택기업', 1)),
           *income_blocks(), cast('기업갱신'))
    mgr.on(on_msg('경제갱신'), cast('기업갱신'))
    button(P, sc, '돌아가기', '돌아가기', -196, -121, 76, 22, 'navy', icon='back', actions=ctx['GO_HOME']())
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])
    CONTRACT_KINDS[2] = ([if_(and_(ge(V('돈'), LGET('기업가격', V('계약대상'))), eq(LGET('인수레벨', V('계약대상')), 0)),
                              chg('돈', mul(LGET('기업가격', V('계약대상')), -1)), lst_set('인수레벨', V('계약대상'), 1),
                              chg('인수수', 1), chg('인수가치', LGET('기업가격', V('계약대상'))),
                              chg('인수수입', div(mul(LGET('기업가격', V('계약대상')), LGET('기업수익률', V('계약대상'))), 1000)),
                              *income_blocks())],
                         go(sc))


# ------------------------------------------------------------------ 부동산 + 정보꾼
def build_land(P, ctx):
    sc = ctx['S_LAND']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('부동산', 110, 30, 'royal'), 0, 116)
    for k, lbl in enumerate(('조치원', '세종시', '전국'), 1):
        tb = sprite(P, sc, '땅탭%d' % k, [('off', K.badge(lbl, 70, 18, 'navy')), ('on', K.badge(lbl, 70, 18, 'royal')),
                                       ('lock', K.badge('잠김', 70, 18, 'gray'))], -190 + (k - 1) * 76, 86)
        tb.on(on_msg('땅갱신'), ifelse(lt(V('직위'), k), [shape('lock')], [ifelse(eq(V('땅탭'), k), [shape('on')], [shape('off')])]))
        tb.on(on_click(), ifelse(lt(V('직위'), k),
                                 [setv('경제알림', join(LGET('직위이름', add(k, 1)), '이(가) 되면 열려요!')), cast('경제알림')],
                                 [setv('땅탭', k), setv('선택땅', LAND_TAB[k - 1] + 1), cast('땅갱신')]))
    cards = [('n', K.panel(220, 26, 'card')), ('own', K.panel(220, 26, 'card', header='royal')),
             ('sel', K.panel(220, 26, 'glass', header='purple'))]
    for j in range(1, 6):
        y = 58 - (j - 1) * 30
        idx = add(mul(sub(V('땅탭'), 1), 5), j)
        cd = sprite(P, sc, '땅칸%d' % j, cards, -124, y)
        n1 = text(P, sc, '땅칸이름%d' % j, '', -170, y, 9, C_WHITE, F_NUM, False, 1, w=120, h=13)
        n2 = text(P, sc, '땅칸값%d' % j, '', -60, y, 8, C_ACC, F_NUM, False, 2, w=90, h=12)
        cd.on(on_msg('땅갱신'), ifelse(eq(V('선택땅'), idx), [shape('sel')],
                                     [ifelse(eq(LGET('땅보유', idx), 1), [shape('own')], [shape('n')])]))
        n1.on(on_msg('땅갱신'), write(LGET('땅이름', idx)))
        n2.on(on_msg('땅갱신'), *fmt_money(LGET('땅가격', idx), '_m'), write(V('_m')),
              ifelse(gt(LGET('땅가격', idx), LGET('땅기본가', idx)), [text_color(C_RED)], [text_color(C_BLUE)]))
        for o in (cd, n1, n2):
            o.on(on_click(), setv('선택땅', idx), cast('땅갱신'))
    # 상세
    S = V('선택땅')
    panel(P, sc, '땅상세판', 132, 22, 200, 132, 'glass', header='royal')
    d1 = text(P, sc, '땅상세이름', '', 132, 74, 12, C_WHITE, F_NUM, False, 0, w=190, h=17)
    d2 = text(P, sc, '땅상세정보', '', 132, 40, 9, C_WHITE, F_BODY, True, 0, w=186, h=44)
    d1.on(on_msg('땅갱신'), write(LGET('땅이름', S)))
    d2.on(on_msg('땅갱신'), *fmt_money(LGET('땅가격', S), '_m'), setv('_q', V('_m')),
          *fmt_money(div(mul(LGET('땅가격', S), LGET('땅수익률', S)), 1000), '_m'),
          write(join('시세 ', V('_q'), '\n10초마다 임대료 +', V('_m'), '\n',
                     LGET('땅보유말', add(LGET('땅보유', S), 1)))))
    P.list('땅보유말', ['아직 내 땅이 아니에요', '내 땅이에요!'])
    bb = button(P, sc, '땅사기', '매입 계약', 96, -22, 84, 24, 'royal', icon='shop',
                actions=[if_(eq(LGET('땅보유', S), 0),
                             ifelse(ge(V('돈'), LGET('땅가격', S)),
                                    [*contract_go(ctx, 3, S, LGET('땅가격', S), '부동산 매매 계약서',
                                                  join('1. 갑은 「', LGET('땅이름', S), '」을(를) 을에게 판다.\n'
                                                       '2. 을은 시세대로 대금을 즉시 지급한다.\n3. 앞으로 생기는 개발 이익과 손실은 을에게 속한다.'),
                                                  '부동산 중개 법인')],
                                    [setv('경제알림', '현금이 부족해요!'), cast('경제알림'), G.sfx('bad')]))])
    bs = button(P, sc, '땅팔기', '팔기', 176, -22, 64, 24, 'gray', icon='coin',
                actions=[if_(eq(LGET('땅보유', S), 1), chg('돈', LGET('땅가격', S)), lst_set('땅보유', S, 0),
                             chg('땅가치합', mul(LGET('땅가격', S), -1)), chg('땅수입', mul(div(mul(LGET('땅가격', S), LGET('땅수익률', S)), 1000), -1)),
                             setv('경제알림', join(LGET('땅이름', S), ' 매각 완료')), cast('경제알림'), G.sfx('coin'),
                             *income_blocks(), cast('땅갱신'))])
    bb.on(on_msg('땅갱신'), ifelse(eq(LGET('땅보유', S), 0), [show()], [hide()]))
    bs.on(on_msg('땅갱신'), ifelse(eq(LGET('땅보유', S), 1), [show()], [hide()]))
    # 정보꾼
    panel(P, sc, '정보판', 40, -84, 400, 62, 'glass', header='purple')
    text(P, sc, '정보제목', '정보꾼에게 개발 정보 사기 (가짜일 수도 있어요)', 40, -62, 8, C_DIM, F_BODY, True, 0, w=380, h=12)
    tip = text(P, sc, '정보글', '', 40, -102, 9, C_WHITE, F_BODY, True, 0, w=380, h=24)
    tip.on(on_scene(), write(V('정보글')))
    tip.on(on_msg('정보갱신'), write(V('정보글')))
    for k in range(1, 4):
        price = mul(LGET('정보꾼값', k), LGET('상점배율', V('단계')))
        bt = button(P, sc, '정보꾼%d' % k, D2.BROKERS[k - 1][0], -86 + (k - 1) * 126, -80, 120, 20, 'purple',
                    actions=[ifelse(ge(V('돈'), price), [chg('돈', mul(price, -1)), *_tip_blocks(k), G.sfx('coin'), cast('정보갱신')],
                                    [setv('경제알림', '현금이 부족해요!'), cast('경제알림'), G.sfx('bad')])])
    pr = text(P, sc, '정보값', '', 40, -118, 7, C_DIM, F_BODY, True, 0, w=380, h=11)
    pr_b = []
    for k in range(1, 4):
        pr_b += [*fmt_money(mul(LGET('정보꾼값', k), LGET('상점배율', V('단계'))), '_m'), setv('_p%d' % k, V('_m'))]
    for k in range(1, 4):
        P.var('_p%d' % k, '')
    pr.on(on_scene(), *pr_b, write(join('정보 값: ', V('_p1'), ' / ', V('_p2'), ' / ', V('_p3'), ' (정확도 50% / 75% / 95%)')))
    mgr = text(P, sc, '땅담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), if_(gt(V('땅탭'), V('직위')), setv('땅탭', 1), setv('선택땅', 1)), *income_blocks(), cast('땅갱신'))
    mgr.on(on_msg('경제갱신'), cast('땅갱신'))
    button(P, sc, '돌아가기', '돌아가기', -196, -121, 76, 22, 'navy', icon='back', actions=ctx['GO_HOME']())
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])
    CONTRACT_KINDS[3] = ([if_(and_(ge(V('돈'), LGET('땅가격', V('계약대상'))), eq(LGET('땅보유', V('계약대상')), 0)),
                              chg('돈', mul(LGET('땅가격', V('계약대상')), -1)), lst_set('땅보유', V('계약대상'), 1),
                              chg('땅가치합', LGET('땅가격', V('계약대상'))),
                              chg('땅수입', div(mul(LGET('땅가격', V('계약대상')), LGET('땅수익률', V('계약대상'))), 1000)),
                              *income_blocks())],
                         go(sc))


def _tip_blocks(k):
    """정보꾼 k 의 정보: 지금 예정된 개발 소식을 (정확도만큼) 알려 준다. 틀리면 엉뚱한 땅을 '호재'라고 한다."""
    nmax = mul(5, ifelse_min3(V('직위')))
    find = [setv('_ei', 0)]
    for i in range(1, NL + 1):
        find.append(if_(gt(LGET('땅예정', i), 0), setv('_ei', i)))
    return [*find,
            ifelse(le(rnd(1, 100), LGET('정보꾼확률', k)),
                   [ifelse(eq(V('_ei'), 0), [setv('정보글', join(LGET('정보꾼이름', k), ': "요즘은 조용해. 큰 개발 소식은 없어."'))],
                           [ifelse(gt(LGET('땅배율', V('_ei')), 1),
                                   [setv('정보글', join(LGET('정보꾼이름', k), ': "', LGET('땅이름', V('_ei')), '에 곧 큰 호재가 터진다. 1~2분 안에!"'))],
                                   [setv('정보글', join(LGET('정보꾼이름', k), ': "', LGET('땅이름', V('_ei')), ' 갖고 있으면 빨리 팔아. 곧 악재야."'))])])],
                   [setv('_ek', rnd(1, nmax)),
                    setv('정보글', join(LGET('정보꾼이름', k), ': "', LGET('땅이름', V('_ek')), '에 곧 큰 호재가 터진다. 1~2분 안에!"'))])]


# ------------------------------------------------------------------ 작전 세력 (내가 구성원을 모은다)
NM = len(D2.OPS_MEMBERS)


def crew_blocks():
    """고른 구성원으로 비용·띄우는 힘·적발 위험 계산."""
    b = [setv('세력비용합', 0), setv('세력힘합', 0), setv('세력위험합', D2.OPS_BASE_RISK)]
    for i in range(1, NM + 1):
        n = LGET('세력인원', i)
        b += [chg('세력비용합', mul(mul(n, LGET('세력비용', i)), LGET('상점배율', V('단계')))),
              chg('세력힘합', mul(n, LGET('세력힘', i))), chg('세력위험합', mul(n, LGET('세력위험', i)))]
    b += [if_(lt(V('세력위험합'), 2), setv('세력위험합', 2)), if_(gt(V('세력위험합'), 95), setv('세력위험합', 95))]
    return b


def build_ops(P, ctx):
    sc = ctx['S_OPS']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('작전 세력 구성', 150, 30, 'purple'), 0, 116)
    # 종목 고르기
    T = V('작전대상')
    panel(P, sc, '종목판', 0, 80, 240, 30, 'glass', header='royal')
    nm = text(P, sc, '대상이름', '', 0, 86, 11, C_WHITE, F_NUM, False, 0, w=170, h=16)
    pr = text(P, sc, '대상정보', '', 0, 72, 7, C_DIM, F_BODY, True, 0, w=200, h=11)
    nm.on(on_msg('작전갱신'), write(join('목표 종목: ', LGET('주식이름', T))))
    pr.on(on_msg('작전갱신'), *fmt_price(LGET('주가', T), '_pt'), *fmt_comma(LGET('보유', T), '_q'),
          write(join('지금 ', V('_pt'), '/주 · 내 보유 ', V('_q'), '주')))
    button(P, sc, '대상이전', '◀', -104, 80, 26, 22, 'navy', actions=[ifelse(gt(T, 1), [chg('작전대상', -1)], [setv('작전대상', 15)]),
                                                                       cast('작전갱신')])
    button(P, sc, '대상다음', '▶', 104, 80, 26, 22, 'navy', actions=[ifelse(lt(T, 15), [chg('작전대상', 1)], [setv('작전대상', 1)]),
                                                                      cast('작전갱신')])
    # 구성원 6종
    for i, m in enumerate(D2.OPS_MEMBERS, 1):
        c, r = (i - 1) % 2, (i - 1) // 2
        x, y = -118 + c * 236, 44 - r * 32
        panel(P, sc, '구성원판%d' % i, x, y, 228, 28, 'card')
        text(P, sc, '구성원이름%d' % i, m[0], x - 60, y + 6, 9, C_WHITE, F_NUM, False, 1, w=100, h=13)
        eff = []
        if m[3]:
            eff.append('힘 +%d%%' % m[3])
        eff.append('위험 %+d%%' % m[4])
        text(P, sc, '구성원설명%d' % i, '%s · %s' % (m[1], ' '.join(eff)), x - 60, y - 6, 7, C_DIM, F_BODY, True, 1, w=150, h=11)
        cnt = text(P, sc, '구성원수%d' % i, '0', x + 78, y, 11, C_ACC, F_NUM, False, 0, w=24, h=15)
        cnt.on(on_msg('작전갱신'), write(join(LGET('세력인원', i), '명')))
        button(P, sc, '빼기%d' % i, '−', x + 52, y, 20, 20, 'navy',
               actions=[if_(and_(gt(LGET('세력인원', i), 0), eq(V('작전단계'), 0)), lst_set('세력인원', i, sub(LGET('세력인원', i), 1))),
                        cast('작전갱신')])
        button(P, sc, '더하기%d' % i, '+', x + 102, y, 20, 20, 'purple',
               actions=[if_(and_(lt(LGET('세력인원', i), D2.OPS_MAX), eq(V('작전단계'), 0)), lst_set('세력인원', i, add(LGET('세력인원', i), 1))),
                        cast('작전갱신')])
    summ = text(P, sc, '세력요약', '', 0, -42, 10, C_WHITE, F_NUM, False, 0, w=440, h=15)
    summ.on(on_msg('작전갱신'), *crew_blocks(), *fmt_money(V('세력비용합'), '_m'),
            write(join('비용 ', V('_m'), '  ·  최대 상승 +', V('세력힘합'), '%  ·  적발 확률 ', V('세력위험합'), '%')))
    st = text(P, sc, '작전상태', '', 0, -60, 9, C_ACC, F_BODY, True, 0, w=440, h=13)
    st.on(on_msg('작전갱신'),
          ifelse(eq(V('작전단계'), 0), [write('구성원을 모아 작전을 시작하세요. 미리 사 두고, 꼭대기에서 파는 게 핵심!')],
                 [ifelse(eq(V('작전단계'), 1), [write(join('작전 준비 완료! 장이 열리면 ', LGET('주식이름', V('작전종목')), ' 주가가 오르기 시작해요'))],
                         [ifelse(eq(V('작전단계'), 2), [write(join('급등 중! ', LGET('주식이름', V('작전종목')), ' (', V('작전틱'), '/12초)'))],
                                 [write(join('세력 이탈 중... 주가가 무너진다 (', V('작전틱'), '/8초)'))])])]))
    res = text(P, sc, '작전결과', '', 0, -74, 9, C_WHITE, F_BODY, True, 0, w=440, h=13)
    res.on(on_msg('작전갱신'), write(V('작전결과')))
    go_ = [*crew_blocks(),
           ifelse(gt(V('작전단계'), 0), [setv('경제알림', '이미 작전이 진행 중이에요!'), cast('경제알림')],
                  [ifelse(le(V('세력힘합'), 0), [setv('경제알림', '주가를 띄울 구성원(큰손·리딩방·기자·단타)이 필요해요!'), cast('경제알림')],
                          [ifelse(ge(V('돈'), V('세력비용합')),
                                  [*contract_go(ctx, 5, V('작전대상'), V('세력비용합'), '비밀 약정서',
                                                join('1. 갑(세력)은 「', LGET('주식이름', V('작전대상')), '」 주가를 최대 +',
                                                     V('세력힘합'), '%까지 끌어올린다.\n2. 을은 수고비를 미리 낸다.\n'
                                                     '3. 이 약정은 절대 비밀이며, 들키면 을이 모든 책임을 진다.'),
                                                '익명의 작전 세력')],
                                  [setv('경제알림', '현금이 부족해요!'), cast('경제알림'), G.sfx('bad')])])])]
    button(P, sc, '작전시작', '작전 개시', 0, -98, 130, 26, 'purple', icon='bolt', actions=go_)
    text(P, sc, '작전안내', '장이 열리면 12초 동안 오르고 8초 동안 무너져요. 걸리면 벌금(수고비 3배)!', 40, -121, 7, C_DIM, F_BODY,
         True, 0, w=260, h=11)
    button(P, sc, '거래소로', '거래소', 196, -121, 70, 22, 'blue', icon='chart', actions=go(ctx['S_STOCK']))
    button(P, sc, '돌아가기', '돌아가기', -196, -121, 76, 22, 'navy', icon='back', actions=go(ctx['S_SHOP']))
    mgr = text(P, sc, '작전담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), if_(or_(lt(V('작전대상'), 1), gt(V('작전대상'), 15)), setv('작전대상', 1)), cast('작전갱신'))
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])
    CONTRACT_KINDS[5] = ([*crew_blocks(),
                          if_(and_(ge(V('돈'), V('계약금액')), eq(V('작전단계'), 0)),
                              chg('돈', mul(V('계약금액'), -1)), setv('작전비용', V('계약금액')), setv('작전종목', V('계약대상')),
                              setv('작전폭', V('세력힘합')), setv('작전위험', V('세력위험합')),
                              ifelse(gt(LGET('세력인원', NM), 0), [setv('작전변호', 1)], [setv('작전변호', 0)]),
                              setv('작전단계', 1), setv('작전틱', 0), setv('작전결과', ''))],
                         go(sc))


def ops_tick_blocks():
    """거래소 장중 1초마다 (scene_stock.tick_blocks 안에서): 작전 종목 띄우기 → 무너뜨리기 → 적발 판정."""
    s = V('작전종목')
    pump = div(V('작전폭'), 100.0 * D2.OPS_PUMP_TICKS)
    fine = ifelse(eq(V('작전변호'), 1), [setv('_ev', mul(V('작전비용'), 1.5))], [setv('_ev', mul(V('작전비용'), 3))])
    return [if_(eq(V('작전단계'), 1), setv('작전단계', 2), setv('작전틱', 0),
                setv('뉴스글', join(LGET('주식이름', s), ' 이상 급등! 정체 모를 매수세 몰려')), setv('뉴스루머', 0), cast('뉴스')),
            if_(eq(V('작전단계'), 2),
                lst_set('주가', s, mul(LGET('주가', s), add(1, mul(pump, div(rnd(7, 13), 10))))), chg('작전틱', 1),
                if_(ge(V('작전틱'), D2.OPS_PUMP_TICKS), setv('작전단계', 3), setv('작전틱', 0),
                    setv('뉴스글', join(LGET('주식이름', s), ', 세력 이탈설에 매물 폭탄!')), setv('뉴스루머', 0), cast('뉴스'))),
            if_(eq(V('작전단계'), 3),
                lst_set('주가', s, mul(LGET('주가', s), div(rnd(80, 90), 100))), chg('작전틱', 1),
                if_(ge(V('작전틱'), D2.OPS_DUMP_TICKS), setv('작전단계', 0),
                    setv('_cp', V('작전위험')), if_(gt(LGET('매수남은', 2), 0), setv('_cp', div(V('작전위험'), 2))),
                    chg('의혹', 10),
                    ifelse(le(rnd(1, 100), V('_cp')),
                           [fine, chg('돈', mul(V('_ev'), -1)), chg('평판', -20), if_(lt(V('평판'), 0), setv('평판', 0)),
                            chg('내지지율', -2), if_(lt(V('내지지율'), 0.5), setv('내지지율', 0.5)),
                            *fmt_money(V('_ev'), '_m'),
                            setv('작전결과', join('금감원에 적발! 벌금 ', V('_m'), ', 평판·지지율 하락...')),
                            setv('뉴스글', join(LGET('주식이름', s), ' 시세조종 적발! 금감원 조사 착수')), setv('뉴스루머', 0), cast('뉴스')],
                           [setv('작전결과', '작전 종료. 들키지 않았다!')])))]


# ------------------------------------------------------------------ 수사 대응 (검찰 · 금감원 · 노동청 · 공정위)
def build_case(P, ctx):
    sc = ctx['S_CASE']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('수사 대응', 120, 30, 'red'), 0, 116)
    on = gt(V('수사기관'), 0)
    mult = bribe_mult()
    # ---- 왼쪽: 진행 중인 수사
    panel(P, sc, '사건판', -112, 6, 232, 160, 'alert')
    ag = text(P, sc, '수사기관', '', -112, 72, 13, C_RED, F_NUM, False, 0, w=220, h=18)
    ch = text(P, sc, '수사혐의', '', -112, 52, 11, C_WHITE, F_NUM, False, 0, w=220, h=16)
    ds = text(P, sc, '수사설명', '', -112, 28, 8, C_DIM, F_BODY, True, 0, w=216, h=28)
    tm = text(P, sc, '수사남은', '', -112, 2, 10, C_WHITE, F_NUM, False, 0, w=216, h=15)
    rk = text(P, sc, '유죄확률', '', -112, -16, 10, C_ACC, F_NUM, False, 0, w=216, h=15)
    rb = sprite(P, sc, '유죄막대', K.bar_set('case_red', 180, 8, 'red'), -112, -32)
    upd = [ag, [ifelse(on, [write(join(LGET('기관이름', V('수사기관')), ' 수사 중!'))], [write('진행 중인 수사 없음')])],
           ch, [ifelse(on, [write(LGET('혐의이름', V('수사혐의')))], [write('')])],
           ds, [ifelse(on, [write(LGET('혐의설명', V('수사혐의')))], [write('세종시장이 되면 검찰·금감원·노동청·공정위가\n수사를 시작할 수 있어요.')])],
           tm, [ifelse(on, [write(join('결과 발표까지 ', V('수사남은'), '초'))], [write('')])],
           rk, [write(join('의혹 지수 ', rounded(V('의혹')), '  ·  유죄 확률 ', ifelse_case_risk(), '%'))]]
    for k in range(0, len(upd), 2):
        upd[k].on(on_msg('수사갱신'), *upd[k + 1])
    rb.on(on_msg('수사갱신'), ifelse(on, [shape(add(floor(div(V('수사위험'), 2.5)), 1)), show()], [hide()]))
    # 대응 버튼
    note = text(P, sc, '수사알림', '', 0, -100, 9, C_WHITE, F_NUM, False, 0, w=360, h=16, visible=False, bg=C_BOX)
    note.on(on_msg('수사알림'), write(V('수사결과글')), to_front(), show(), wait(2.6), hide())
    lawyer = mul(D2.LAWYER_COST, mult)
    bribe = mul(D2.BRIBE_COST, mult)

    def act(blocks):
        return [ifelse(on, blocks, [setv('수사결과글', '지금은 수사가 없어요.')]), cast('수사알림'), cast('수사갱신')]
    acts = [
        ('변호인단 선임', 'royal', act([ifelse(ge(V('돈'), lawyer),
                                         [chg('돈', mul(lawyer, -1)), chg('수사위험', -20), if_(lt(V('수사위험'), 5), setv('수사위험', 5)),
                                          setv('수사결과글', '전관 변호인단 합류! 유죄 확률 -20%p'), G.sfx('coin')],
                                         [setv('수사결과글', '변호사 비용이 부족해요!'), G.sfx('bad')])])),
        ('해명 기자회견', 'blue', act([ifelse(le(rnd(1, 100), 50),
                                        [chg('평판', 5), chg('수사위험', -10), if_(lt(V('수사위험'), 5), setv('수사위험', 5)),
                                         setv('수사결과글', '해명이 먹혔다! 여론이 돌아섰다 (유죄 확률 -10%p)'), G.sfx('good')],
                                        [chg('평판', -8), chg('수사위험', 10), if_(gt(V('수사위험'), 95), setv('수사위험', 95)),
                                         setv('수사결과글', '말실수를 했다... 유죄 확률 +10%p'), G.sfx('bad')])])),
        ('몰래 매수 시도', 'red', act([ifelse(ge(V('돈'), bribe),
                                        [chg('돈', mul(bribe, -1)),
                                         ifelse(le(rnd(1, 100), D2.BRIBE_OK),
                                                [chg('의혹', 20), setv('수사기관', 0),
                                                 setv('수사결과글', '수사가 흐지부지 끝났다... 무혐의 처리'), G.sfx('cash')],
                                                [chg('의혹', 25), chg('수사위험', 30), if_(gt(V('수사위험'), 95), setv('수사위험', 95)),
                                                 chg('평판', -15), chg('수사남은', 30),
                                                 setv('수사결과글', '매수 시도가 들통났다! 뇌물 공여 혐의까지 추가'), G.sfx('bad')])],
                                        [setv('수사결과글', '매수할 돈이 부족해요!'), G.sfx('bad')])])),
        ('수사 협조', 'gray', act([setv('_cf', rounded(mul(V('총자산'), 0.03))), if_(lt(V('_cf'), 0), setv('_cf', 0)),
                                    chg('돈', mul(V('_cf'), -1)), chg('평판', -5), chg('의혹', -10), if_(lt(V('의혹'), 0), setv('의혹', 0)),
                                    setv('수사기관', 0), *fmt_money(V('_cf'), '_m'),
                                    setv('수사결과글', join('잘못을 인정하고 협조했다. 벌금 ', V('_m'), ' 내고 마무리')), G.sfx('stamp')])),
    ]
    for j, (lbl, col, a) in enumerate(acts):
        button(P, sc, '대응%d' % j, lbl, -168 + (j % 2) * 112, -54 - (j // 2) * 26, 106, 22, col, actions=a)
    cost_t = text(P, sc, '대응비용', '', -112, -112, 7, C_DIM, F_BODY, True, 0, w=220, h=11)
    cost_t.on(on_scene(), *fmt_money(lawyer, '_m'), setv('_q', V('_m')), *fmt_money(bribe, '_m'),
              write(join('변호인단 ', V('_q'), ' · 매수 ', V('_m'), ' (성공 ', D2.BRIBE_OK, '%)')))
    # ---- 오른쪽: 미리 매수하기
    panel(P, sc, '매수판', 124, 6, 214, 160, 'glass', header='purple')
    text(P, sc, '매수제목', '미리 매수해 두기', 124, 72, 12, C_WHITE, F_NUM, False, 0, w=200, h=16)
    text(P, sc, '매수설명', '3분 동안 그 기관은 수사를 안 해요.\n(금감원: 작전 적발↓, 검찰: 뒷돈 적발↓) 의혹 +6',
         124, 50, 7, C_DIM, F_BODY, True, 0, w=200, h=22)
    pre = mul(mul(D2.BRIBE_COST, 0.6), mult)
    for a in range(1, NA + 1):
        y = 24 - (a - 1) * 30
        bt = button(P, sc, '미리매수%d' % a, D2.AGENCY_SHORT[a - 1] + ' 매수', 84, y, 92, 22, 'purple',
                    actions=[ifelse(ge(V('돈'), pre),
                                    [chg('돈', mul(pre, -1)), lst_set('매수남은', a, D2.PRE_BRIBE_TIME), chg('의혹', 6),
                                     setv('수사결과글', '%s 쪽 사람을 매수했다. 3분 동안 조용할 것이다' % D2.AGENCY_SHORT[a - 1]),
                                     G.sfx('cash')],
                                    [setv('수사결과글', '매수할 돈이 부족해요!'), G.sfx('bad')]),
                             cast('수사알림'), cast('수사갱신')])
        st = text(P, sc, '매수상태%d' % a, '', 174, y, 8, C_ACC, F_NUM, False, 0, w=86, h=13)
        st.on(on_msg('수사갱신'), ifelse(gt(LGET('매수남은', a), 0), [write(join('안전 ', LGET('매수남은', a), '초')), text_color(C_ACC)],
                                       [write('매수 안 함'), text_color(C_DIM)]))
    pc = text(P, sc, '매수비용', '', 124, -98, 7, C_DIM, F_BODY, True, 0, w=200, h=11)
    pc.on(on_scene(), *fmt_money(pre, '_m'), write(join('기관마다 ', V('_m'))))
    mgr = text(P, sc, '수사담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), *ST_assets(), cast('수사갱신'))
    mgr.on(on_msg('경제갱신'), cast('수사갱신'))
    button(P, sc, '돌아가기', '돌아가기', -196, -121, 76, 22, 'navy', icon='back', actions=ctx['GO_HOME']())
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])


def ifelse_case_risk():
    return V('수사위험')


def ST_assets():
    import scene_stock as ST
    return ST.assets_blocks()


# ------------------------------------------------------------------ 직원 면접 (내 회사)
def new_candidate():
    p = V('후보직급')
    return [setv('후보이름', join(LGET('성씨', rnd(1, len(D2.SURNAMES))), LGET('이름', rnd(1, len(D2.GIVEN))))),
            setv('후보경력', rnd(LGET('직급경력최소', p), LGET('직급경력최대', p))),
            setv('후보나이', add(add(24, V('후보경력')), rnd(0, 5))),
            setv('_hc', rnd(1, 100)),
            ifelse(le(V('_hc'), 40), [setv('후보성격', 1)],
                   [ifelse(le(V('_hc'), 65), [setv('후보성격', 2)], [ifelse(le(V('_hc'), 85), [setv('후보성격', 3)], [setv('후보성격', 4)])])]),
            setv('후보능력', rnd(LGET('직급능력최소', p), LGET('직급능력최대', p))),
            setv('후보급여', rounded(mul(LGET('직급급여', p), add(0.8, div(V('후보능력'), 250))))),
            setv('질문수', 0), setv('질문1', 0), setv('질문2', 0), setv('질문3', 0),
            setv('후보정보1', ''), setv('후보정보2', ''), setv('후보정보3', '')]


def build_hire(P, ctx):
    sc = ctx['S_HIRE']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('직원 면접', 120, 30, 'royal'), 0, 116)
    summ = text(P, sc, '인사요약', '', 0, 92, 9, C_ACC, F_NUM, False, 0, w=300, h=14)
    summ.on(on_msg('인사갱신'), *fmt_money(V('직원급여합'), '_m'),
            write(join('경영력 ', V('경영력'), ' · 직원 ', V('직원총수'), '명 · 급여 10초마다 -', V('_m'))))
    # ---- 왼쪽: 직급 목록
    panel(P, sc, '직급판', -128, -10, 204, 196, 'glass', header='royal')
    rows = [('n', K.panel(196, 18, 'card')), ('s', K.panel(196, 18, 'card', header='royal'))]
    for i, pos in enumerate(D2.POSITIONS, 1):
        y = 72 - (i - 1) * 20
        rc = sprite(P, sc, '직급칸%d' % i, rows, -128, y)
        rc.on(on_msg('인사갱신'), ifelse(eq(V('선택직급'), i), [shape('s')], [shape('n')]))
        t1 = text(P, sc, '직급명%d' % i, pos[0], -186, y, 9, C_WHITE, F_NUM, False, 1, w=70, h=13)
        t2 = text(P, sc, '직급현황%d' % i, '', -80, y, 8, C_DIM, F_BODY, True, 2, w=100, h=12)
        t2.on(on_msg('인사갱신'),
              ifelse(gt(LGET('직원수', i), 0),
                     [write(join(LGET('직원수', i), '/', pos[1], '명 · 평균 ', rounded(div(LGET('직원능력합', i), LGET('직원수', i)))))],
                     [write(join('0/', pos[1], '명'))]))
        sel = [setv('선택직급', i), setv('후보직급', i), *new_candidate(), cast('인사갱신')]
        for o in (rc, t1, t2):
            o.on(on_click(), *sel)
    fire = button(P, sc, '해고', '한 명 해고', -128, -110, 90, 20, 'gray',
                  actions=[if_(gt(LGET('직원수', V('선택직급')), 0),
                               lst_set('직원능력합', V('선택직급'), sub(LGET('직원능력합', V('선택직급')),
                                                                     div(LGET('직원능력합', V('선택직급')), LGET('직원수', V('선택직급'))))),
                               lst_set('직원수', V('선택직급'), sub(LGET('직원수', V('선택직급')), 1)),
                               setv('경제알림', join(LGET('직급이름', V('선택직급')), ' 한 명을 내보냈다')), cast('경제알림')),
                           *staff_calc(), *income_sum(), cast('인사갱신')])
    # ---- 오른쪽: 지원자
    panel(P, sc, '지원자판', 104, -10, 252, 196, 'glass', header='purple')
    nm = text(P, sc, '지원자이름', '', 104, 72, 13, C_WHITE, F_NUM, False, 0, w=240, h=18)
    nm.on(on_msg('인사갱신'), write(join(V('후보이름'), ' (', V('후보나이'), '세) · ', LGET('직급이름', V('후보직급')), ' 지원')))
    bio = text(P, sc, '지원자경력', '', 104, 54, 9, C_DIM, F_BODY, True, 0, w=240, h=13)
    bio.on(on_msg('인사갱신'), *fmt_money(V('후보급여'), '_m'), write(join('경력 ', V('후보경력'), '년 · 희망 급여 10초마다 ', V('_m'))))
    infos = []
    for k in range(1, 4):
        it = text(P, sc, '면접정보%d' % k, '', 104, 34 - (k - 1) * 18, 8, C_WHITE, F_BODY, True, 0, w=236, h=16)
        it.on(on_msg('인사갱신'), write(V('후보정보%d' % k)))
        infos.append(it)
    ql = text(P, sc, '질문남은', '', 104, -18, 8, C_ACC, F_NUM, False, 0, w=236, h=12)
    ql.on(on_msg('인사갱신'), write(join('질문은 2개까지 (남은 ', sub(2, V('질문수')), '개)')))
    qs = [('경력 확인', '질문1', [setv('_hc', add(V('후보능력'), rnd(-10, 10))), if_(eq(V('후보성격'), 3), chg('_hc', 25)),
                                if_(gt(V('_hc'), 99), setv('_hc', 99)),
                                setv('후보정보1', join('· 본인 말로는 능력이 ', V('_hc'), '점쯤 된다고 한다'))]),
          ('압박 질문', '질문2', [setv('후보정보2', join('· ', LGET('성격힌트', V('후보성격'))))]),
          ('실무 테스트', '질문3', [setv('_hc', add(V('후보능력'), rnd(-5, 5))), if_(eq(V('후보성격'), 4), chg('_hc', -15)),
                                  if_(lt(V('_hc'), 1), setv('_hc', 1)),
                                  setv('후보정보3', join('· 실무 테스트 점수 ', V('_hc'), '점'))])]
    for j, (lbl, flag, blk) in enumerate(qs):
        button(P, sc, '질문버튼%d' % j, lbl, 26 + j * 78, -40, 74, 22, 'blue',
               actions=[ifelse(and_(lt(V('질문수'), 2), eq(V(flag), 0)), [setv(flag, 1), chg('질문수', 1), *blk, G.sfx('click')],
                               [setv('경제알림', '더 물어볼 수 없어요'), cast('경제알림')]), cast('인사갱신')])
    hire = [ifelse(not_(eq(V('회사상태'), 1)), [setv('경제알림', '먼저 회사를 세워야 해요!')],
                   [ifelse(ge(LGET('직원수', V('후보직급')), LGET('직급정원', V('후보직급'))),
                           [setv('경제알림', '그 직급은 자리가 다 찼어요!')],
                           [setv('_hc', V('후보능력')), if_(eq(V('후보성격'), 4), chg('_hc', -15)), if_(lt(V('_hc'), 1), setv('_hc', 1)),
                            lst_set('직원수', V('후보직급'), add(LGET('직원수', V('후보직급')), 1)),
                            lst_set('직원능력합', V('후보직급'), add(LGET('직원능력합', V('후보직급')), V('_hc'))),
                            setv('경제알림', join(V('후보이름'), ' ', LGET('직급이름', V('후보직급')), ' 채용! 진짜 실력은 일하면서 드러나요')),
                            G.sfx('fanfare'), *staff_calc(), *income_sum(), *new_candidate()])]),
            cast('경제알림'), cast('인사갱신')]
    button(P, sc, '채용', '채용하기', 54, -70, 100, 26, 'royal', icon='person', actions=hire)
    button(P, sc, '다음지원자', '다음 지원자', 160, -70, 100, 26, 'navy', icon='back',
           actions=[*new_candidate(), cast('인사갱신')])
    text(P, sc, '면접안내', '허세가 심한 지원자는 경력을 부풀리고, 게으른 지원자는 채용 뒤 실력이 떨어져요.', 104, -96, 7, C_DIM, F_BODY,
         True, 0, w=240, h=20)
    mgr = text(P, sc, '인사담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), if_(or_(lt(V('선택직급'), 1), gt(V('선택직급'), NP)), setv('선택직급', NP)),
           setv('후보직급', V('선택직급')), *new_candidate(), *staff_calc(), cast('인사갱신'))
    button(P, sc, '돌아가기', '내 회사로', -196, -121, 80, 22, 'navy', icon='back', actions=go(ctx['S_COMPANY']))
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])
