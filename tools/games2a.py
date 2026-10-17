# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 1~10번."""
import random
from games_common import *
import mg_art3 as A3
import art2a as AA

T = 2
GAMES, game = registry()


# ================================================================== 1. 무대 조명 퍼즐 (Lights Out)
def _lamp(on):
    def f(d, im, s):
        W = im.width
        c = W / 2
        if on:
            for k in range(12, 0, -1):
                a = int(10 + 12 * (12 - k))
                r = W * 0.5 * k / 12
                d.ellipse((c - r, c - r, c + r, c + r), fill=(255, 226, 120, min(255, a // 3)))
            d.ellipse((W * 0.2, W * 0.2, W * 0.8, W * 0.8), fill=(255, 244, 196, 255), outline=(255, 255, 255, 255), width=int(1.5 * s))
            d.ellipse((W * 0.32, W * 0.3, W * 0.5, W * 0.44), fill=(255, 255, 255, 200))
        else:
            d.ellipse((W * 0.2, W * 0.2, W * 0.8, W * 0.8), fill=(34, 40, 66, 255), outline=(96, 110, 160, 255), width=int(1.5 * s))
            d.ellipse((W * 0.3, W * 0.3, W * 0.7, W * 0.7), fill=(20, 24, 44, 255))
            d.ellipse((W * 0.34, W * 0.32, W * 0.48, W * 0.42), fill=(120, 130, 170, 90))
    return A3.art('s01_lamp_%d' % on, 42, 42, f)


@game(1)
def g01(P, ctx):
    R, N = 3, 4
    m = mg(P, ctx, T, 1, time_limit=80, status='라운드 1/%d' % R, dim=80)
    rng = random.Random(201)

    def press(b, k):
        r, c = divmod(k, N)
        for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < N and 0 <= cc < N:
                b[rr * N + cc] ^= 1
    puz = []
    for n_press in (3, 5, 7):
        got = []
        while len(got) < 8:
            b = [1] * (N * N)
            for k in rng.sample(range(N * N), n_press):
                press(b, k)
            s = ''.join(map(str, b))
            if s.count('0') >= 5 and s not in got:
                got.append(s)
        puz += got
    P.list('조명퍼즐', puz)
    P.list('조명', [1] * (N * N))
    vars_(P, '조명수', '조명판')
    panel(P, m.sc, '조명판넬', 0, -12, 206, 206, 'glass')
    xs = [-66 + 44 * c for c in range(N)]
    ys = [54 - 44 * r for r in range(N)]
    total = add(*[LGET('조명', k + 1) for k in range(N * N)])
    for k in range(N * N):
        r, c = divmod(k, N)
        o = m.S('조명%d' % (k + 1), [('off', _lamp(0)), ('on', _lamp(1))], xs[c], ys[r])
        nb = [k] + [rr * N + cc for rr, cc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)) if 0 <= rr < N and 0 <= cc < N]
        o.on(on_click(), if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)),
                             *[lst_set('조명', j + 1, sub(1, LGET('조명', j + 1))) for j in nb],
                             chg('합계', 1), setv('조명수', total), cast('조명갱신'), cast('조명누름')))
        o.on(on_msg('조명갱신'), shape(add(LGET('조명', k + 1), 1)))
        o.on(on_click(), if_(eq(V('입력가능'), 1), o.pct(88), wait(0.06), o.pct(100)))
    info = m.T('조명안내', '', 170, 40, 11, C_WHITE, F_BODY, True, 0, w=120, h=60)
    info.on(on_msg('조명갱신'), write(join('켜진 조명\n', V('조명수'), ' / ', N * N, '\n누른 횟수 ', V('합계'))))
    reset = [if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)),
                 *[lst_set('조명', k, char_at(V('조명판'), k)) for k in range(1, N * N + 1)],
                 setv('조명수', total), cast('조명갱신'))]
    button(P, m.sc, '처음부터', '처음 상태로', 170, -30, 100, 24, 'steel', actions=reset)
    ok = m.S('조명성공', K.big_text('ALL ON!', 34, 'royal'), 0, -12, visible=False)
    ok.on(on_msg('조명성공'), ok.pct(40), show(), rep(6, ok.grow_pct(12), wait(0.016)), wait(0.7), hide())
    mgr = hidden(m, '조명담당')
    mgr.on(on_msg('게임시작'), setv('라운드', 1),
           until(or_(gt(V('라운드'), R), eq(V('게임중'), 0)),
                 setv('조명판', LGET('조명퍼즐', add(mul(sub(V('라운드'), 1), 8), rnd(1, 8)))),
                 *[lst_set('조명', k, char_at(V('조명판'), k)) for k in range(1, N * N + 1)],
                 setv('합계', 0), setv('조명수', total), cast('조명갱신'), setv('입력가능', 1),
                 setv('미니표시', join('라운드 ', V('라운드'), '/', R)),
                 wait_until(or_(eq(V('조명수'), N * N), eq(V('게임중'), 0))),
                 setv('입력가능', 0),
                 if_(eq(V('조명수'), N * N), chg('맞춤', 1), cast('조명성공'), wait(1.1)),
                 chg('라운드', 1)),
           *m.end_blocks(add(mul(V('맞춤'), 26), mul(V('남은시간'), 0.4))))
    mgr.on(on_msg('시간끝'), setv('입력가능', 0), *m.end_blocks(add(mul(V('맞춤'), 26), div(V('조명수'), 2))))
    m.on_start(setv('맞춤', 0), setv('합계', 0), setv('입력가능', 0), setv('조명수', 0),
               *[lst_set('조명', k, 1) for k in range(1, N * N + 1)])
    m.snd('조명누름', play('tick'))
    m.snd('조명성공', play('good'))
    m.finish('조명을 누르면 그 조명과 위·아래·양옆 조명이 함께\n켜지거나 꺼져요. 16개를 모두 켜면 다음 무대! (3라운드)',
             '조작: 마우스로 조명 클릭  ·  막히면 "처음 상태로"')
    return True


# ================================================================== 공통 도우미 (2~10번)


def _spawn(o, n, var='번호'):
    """장면 시작 때 복제본 n 개를 만든다 (복제본마다 지역 변수 var = 1..n, 원본은 0)."""
    o.local(var, 0)
    o.on(on_scene(), hide(), setv(var, 0), rep(n, chg(var, 1), clone_self()), setv(var, 0))


def _pop(m, base, pics, msg, x=None, y=None, hold=0.5, rise=True):
    """신호 msg 를 받으면 (x, y) 또는 (_mx, _my) 자리에서 튀어나왔다 사라지는 글자/그림. pics 가 여럿이면 _mv 번째 모양."""
    multi = isinstance(pics, list)
    o = m.S(base, pics, 0, 0, visible=False)
    px = V('_mx') if x is None else x
    py = V('_my') if y is None else y
    o.on(on_msg(msg), *([shape(V('_mv'))] if multi else []), xy(px, py), to_front(), o.pct(40), fx('transparency', 0), show(),
         rep(5, o.grow_pct(14), wait(0.016)), rep(2, o.grow_pct(-5), wait(0.016)), wait(hold),
         rep(8, fx_add('transparency', 12), *([mvy(1.5)] if rise else []), wait(0.02)), hide())
    return o


# ================================================================== 2. 수목원 물주기 (관리)
@game(2)
def g02(P, ctx):
    N, TL = 6, 40
    m = mg(P, ctx, T, 2, time_limit=TL, status='자람 0%', dim=70)
    vars_(P, 's02_배', 's02_햇볕', 's02_평균', 's02_꽃')
    P.list('s02_물', [50] * N)
    P.list('s02_자람', [0] * N)
    P.list('s02_상태', [1] * N)
    P.list('s02_속도', [2.6, 3.8, 3.2, 4.4, 3.0, 3.6])
    start = [58, 50, 62, 48, 56, 52]
    X0, DX, PY, MY = -196, 78, -48, -46
    MB, MH = MY - 31, 62
    WATER = 28
    k = V('번호')
    xk = add(X0 - DX, mul(k, DX))
    W_, G_ = LGET('s02_물', k), LGET('s02_자람', k)

    def water():
        return [if_(and_(gt(k, 0), eq(V('게임중'), 1)),
                    lst_set('s02_물', k, add(W_, WATER)), if_(gt(W_, 100), lst_set('s02_물', k, 100)),
                    setv('_mx', xk), cast('s02_물줌'))]
    m.S('화단', A3.box('s02_bed', 476, 26, (96, 62, 40), rim=(60, 36, 20), r=5), 0, -104)
    # 화분 (복제본 6개)
    pl = m.S('화분', [('%d' % (i + 1), AA.s02_plant(i // 4, i % 4 + 1)) for i in range(12)], 0, PY, visible=False)
    for v in ('t0', 'dt', 'w', '상태', '단계', '종', 'ns'):
        pl.local(v, 0)
    _spawn(pl, N)
    pl.on(on_clone(), setv('종', mod(sub(k, 1), 3)), setv('단계', 1), setv('상태', 1), xy(xk, PY),
          shape(add(mul(V('종'), 4), 1)), fx_clear(), show())
    tick = [setv('dt', sub(timer(), V('t0'))), setv('t0', timer()),
            if_(lt(V('dt'), 0), setv('dt', 0)), if_(gt(V('dt'), 0.3), setv('dt', 0.3)),
            setv('w', sub(W_, mul(mul(LGET('s02_속도', k), V('dt')), V('s02_배')))),
            if_(lt(V('w'), 0), setv('w', 0)),
            lst_set('s02_물', k, V('w')),
            ifelse(gt(V('w'), 80), [setv('ns', 3), lst_set('s02_자람', k, sub(G_, mul(6, V('dt'))))],
                   [ifelse(lt(V('w'), 30), [setv('ns', 2), lst_set('s02_자람', k, sub(G_, mul(1.5, V('dt'))))],
                           [setv('ns', 1), lst_set('s02_자람', k, add(G_, mul(3.0, V('dt'))))])]),
            if_(lt(G_, 0), lst_set('s02_자람', k, 0)), if_(gt(G_, 100), lst_set('s02_자람', k, 100)),
            # 상태가 바뀔 때만 효과
            if_(ne(V('ns'), V('상태')), setv('상태', V('ns')), lst_set('s02_상태', k, V('상태')), fx_clear(),
                if_(eq(V('상태'), 2), fx('brightness', -30)),
                if_(eq(V('상태'), 3), fx('color', 55), fx('brightness', -15), setv('_mx', xk), cast('s02_썩음'))),
            # 자란 단계
            ifelse(ge(G_, 100), [setv('ns', 4)], [setv('ns', add(1, floor(div(G_, 34))))]),
            if_(ne(V('ns'), V('단계')),
                if_(and_(eq(V('ns'), 4), lt(V('단계'), 4)), setv('_mx', xk), setv('_my', PY + 40), cast('s02_꽃핌')),
                setv('단계', V('ns')), shape(add(mul(V('종'), 4), V('단계'))))]
    pl.on(on_msg('게임시작'), if_(gt(k, 0), setv('t0', timer()), until(eq(V('게임중'), 0), *tick, wait(0.05))))
    pl.on(on_click(), *water())
    pl.on(on_click(), if_(and_(gt(k, 0), eq(V('게임중'), 1)), pl.pct(93), wait(0.06), pl.pct(100)))
    # 물 막대 + 눈금
    mt = m.S('물막대', AA.s02_meter(), 0, MY, visible=False)
    _spawn(mt, N)
    mt.on(on_clone(), xy(add(xk, 31), MY), show())
    mt.on(on_click(), *water())
    mk = m.S('물눈금', AA.s02_marker(), 0, MY, visible=False)
    _spawn(mk, N)
    mk.on(on_clone(), lx(add(xk, 24)), show(), forever(ly(add(MB, mul(W_, MH / 100.0))), wait(0.03)))
    # 말풍선 (목말라요 / 과습)
    bb = m.S('말풍선', [('dry', AA.s02_bubble('dry')), ('wet', AA.s02_bubble('wet'))], 0, 0, visible=False)
    bb.local('st', 1)
    _spawn(bb, N)
    bb.on(on_clone(), setv('st', 1), xy(sub(xk, 6), PY + 58),
          forever(if_(ne(LGET('s02_상태', k), V('st')), setv('st', LGET('s02_상태', k)),
                      ifelse(eq(V('st'), 1), [hide()], [shape(sub(V('st'), 1)), show()])), wait(0.06)))
    bb.on(on_click(), *water())
    # 자람 막대
    gb = m.S('자람막대', K.bar_set('s02_grow', 46, 7, 'green'), 0, -108, visible=False)
    gb.local('ls', 0)
    _spawn(gb, N)
    gb.on(on_clone(), setv('ls', 0), xy(add(xk, 4), -110), shape(1), show(),
          forever(if_(ne(add(1, floor(mul(G_, 0.4))), V('ls')), setv('ls', add(1, floor(mul(G_, 0.4)))), shape(V('ls'))),
                  wait(0.12)))
    # 물뿌리개
    can = m.S('물뿌리개', AA.s02_can(), 0, 0, visible=False)
    can.on(on_msg('s02_물줌'), xy(add(V('_mx'), 26), PY + 46), rot(-20), show(), rep(4, rot_by(5), wait(0.04)), wait(0.12), hide())
    _pop(m, '꽃글', K.big_text('활짝!', 20, 'pink'), 's02_꽃핌', hold=0.5)
    _pop(m, '썩음글', K.big_text('물이 넘쳐요!', 14, 'purple'), 's02_썩음', y=PY + 30, hold=0.4)
    # 햇볕 쨍쨍 (잠깐 빨리 마름)
    sun = m.S('해', AA.s02_sun(), -150, 76, visible=False)
    sun.on(on_msg('s02_해'), show(), until(eq(V('s02_햇볕'), 1), rot_by(3), wait(0.03)), hide())
    sun_t = m.S('해글', K.badge('햇볕 쨍쨍! 빨리 말라요', 150, 20, 'red'), -40, 76, visible=False)
    sun_t.on(on_msg('s02_해'), show(), wait_until(eq(V('s02_햇볕'), 1)), hide())
    total = add(*[LGET('s02_자람', i) for i in range(1, N + 1)])
    mgr = hidden(m, '물주기담당')
    count_bloom = [setv('s02_꽃', 0)] + [if_(ge(LGET('s02_자람', i), 100), chg('s02_꽃', 1)) for i in range(1, N + 1)]
    mgr.on(on_msg('게임시작'), setv('s02_햇볕', 1), wait(0.1),
           until(eq(V('게임중'), 0),
                 setv('s02_배', mul(add(1, div(timer(), 60)), V('s02_햇볕'))),
                 setv('s02_평균', div(total, N)), *count_bloom,
                 setv('미니표시', join('자람 ', floor(V('s02_평균')), '% · 꽃 ', V('s02_꽃'), '/', N)),
                 wait(0.2)))
    sun_ev = []
    for t0, dur in ((12, 4.5), (9.5, 4.5)):
        sun_ev += [wait(t0), if_(eq(V('게임중'), 1), setv('s02_햇볕', 1.6), cast('s02_해')), wait(dur), setv('s02_햇볕', 1)]
    mgr.on(on_msg('게임시작'), *sun_ev)
    mgr.on(on_msg('시간끝'), setv('s02_평균', div(total, N)), *m.end_blocks(V('s02_평균')))
    m.on_start(setv('s02_배', 1), setv('s02_햇볕', 1), setv('s02_꽃', 0), setv('s02_평균', 0),
               *[lst_set('s02_물', i + 1, start[i]) for i in range(N)],
               *[lst_set('s02_자람', i + 1, 0) for i in range(N)],
               *[lst_set('s02_상태', i + 1, 1) for i in range(N)])
    m.snd('s02_물줌', play('splash'))
    m.snd('s02_꽃핌', play('good'))
    m.snd('s02_썩음', play('bad'))
    m.snd('s02_해', play('alarm'))
    m.finish('화분 6개의 물 막대를 초록 칸 안에 지켜 주세요!\n초록 칸이면 쑥쑥 자라고, 보라 칸(과습)은 썩어요.',
             '조작: 화분 클릭 = 물 한 번 (막대 1/4쯤 올라가요)  ·  햇볕이 나면 빨리 말라요')
    return True


def _wonv(e):
    """1,000 이상 정수 금액을 '12,500' 꼴 글자로 (값 블록, 1,000,000 미만)."""
    return join(floor(div(e, 1000)), ',', substr(join('', add(1000, mod(e, 1000))), 2, 4))


def _won(e, dst):
    """금액 → 변수 dst 에 '12,500' / '700' 꼴 글자 (블록 목록)."""
    return [ifelse(lt(e, 1000), [setv(dst, e)], [setv(dst, _wonv(e))])]


# ================================================================== 3. 장터 흥정 (흥정)
@game(3)
def g03(P, ctx):
    NI, TL = 5, 80
    m = mg(P, ctx, T, 3, time_limit=TL, status='물건 1/%d' % NI, dim=60)
    names = ['뻥튀기 한 봉지', '참기름 한 병', '꽃무늬 고무신', '대나무 소쿠리', '무쇠 호미']
    prices = [6000, 18000, 12000, 24000, 15000]
    P.list('s03_이름', names)
    P.list('s03_정가표', prices)
    vars_(P, 's03_물건', 's03_정가', 's03_최저', 's03_상인가', 's03_제안', 's03_인내', 's03_거래', 's03_산값', 's03_말',
          's03_점', 's03_비율')
    IX, IY = 100, 50
    # 상인
    face = m.S('상인', [(f, AA.s03_merchant(f)) for f in ('smile', 'sweat', 'frown', 'angry')], -168, -36)
    face.on(on_msg('s03_반응'), shape(V('_mv')), if_(eq(V('_mv'), 4), rep(3, mvx(5), wait(0.03), mvx(-5), wait(0.03))))
    face.on(on_msg('s03_새물건'), shape(1))
    m.S('상인이름', K.badge('부강장터 사장님', 96, 18, 'red'), -168, -108)
    m.S('말풍선', AA.s03_bubble(), -128, 72)
    say_ = m.T('상인말', '', -128, 76, 10, '#1A2050', F_BODY, True, 0, w=204, h=34)
    say_.on(on_msg('s03_반응'), write(V('s03_말')))
    say_.on(on_msg('s03_새물건'), write(V('s03_말')))
    m.T('인내글', '인내심', -116, -76, 8, C_DIM, F_BODY, True, 0, w=50, h=12)
    for j in range(1, 5):
        hj = m.S('하트%d' % j, [('on', AA.s03_heart(1)), ('off', AA.s03_heart(0))], -136 + j * 17, -92)
        hj.on(on_msg('s03_갱신'), ifelse(ge(V('s03_인내'), j), [shape('on')], [shape('off')]))
    # 물건 카드
    panel(P, m.sc, '물건판', IX, IY, 236, 84, 'glass')
    item = m.S('물건', [('%d' % (k + 1), AA.s03_item(k)) for k in range(NI)], IX - 72, IY)
    item.on(on_msg('s03_새물건'), shape(V('s03_물건')), item.pct(60), rep(4, item.grow_pct(10), wait(0.02)))
    nm = m.T('물건이름', '', IX + 34, IY + 22, 13, C_WHITE, F_NUM, False, 0, w=150, h=20)
    nm.on(on_msg('s03_새물건'), write(LGET('s03_이름', V('s03_물건'))))
    lp = m.T('정가글', '', IX + 34, IY, 10, C_DIM, F_BODY, True, 0, w=150, h=16)
    lp.on(on_msg('s03_새물건'), write(join('정가 ', _wonv(V('s03_정가')), '원')))
    cp = m.T('상인가글', '', IX + 34, IY - 20, 10, '#FF9AAA', F_BODY, True, 0, w=160, h=16)
    cp.on(on_msg('s03_갱신'), write(join('사장님 부른 값 ', _wonv(V('s03_상인가')), '원')))
    # 내 제안
    panel(P, m.sc, '제안판', IX, -52, 236, 108, 'glass')
    m.T('제안이름', '내가 부를 값', IX, -12, 9, C_DIM, F_BODY, True, 0, w=120, h=14)
    of = m.T('제안글', '', IX, -32, 20, C_WHITE, F_NUM, False, 0, w=200, h=26)
    of.on(on_msg('s03_갱신'), write(join(_wonv(V('s03_제안')), '원')))
    ok = eq(V('입력가능'), 1)
    clampo = [if_(lt(V('s03_제안'), 1000), setv('s03_제안', 1000)),
              if_(gt(V('s03_제안'), V('s03_상인가')), setv('s03_제안', V('s03_상인가')))]
    for j, d in enumerate((-2000, -500, 500, 2000)):
        button(P, m.sc, '값%d' % j, ('%+d' % d).replace('+', '+'), IX - 84 + j * 56, -60, 52, 22,
               'steel' if d < 0 else 'royal', actions=[if_(ok, chg('s03_제안', d), *clampo, cast('s03_갱신'))])
    # 제안하기
    r_ = div(V('s03_제안'), V('s03_최저'))
    lower = lambda frac: [setv('s03_상인가', mul(ceil_(div(sub(V('s03_상인가'), mul(sub(V('s03_상인가'), V('s03_최저')), frac)), 500)), 500)),
                          if_(lt(V('s03_상인가'), V('s03_최저')), setv('s03_상인가', V('s03_최저')))]
    offer = [if_(ok, setv('입력가능', 0),
                 ifelse(ge(V('s03_제안'), V('s03_최저')),
                        [setv('s03_산값', V('s03_제안')), setv('_mv', 1), setv('s03_말', '좋아요, 가져가요!\n장사 잘하시네~'), setv('s03_거래', 1)],
                        [ifelse(ge(r_, 0.9),
                                [setv('_mv', 2), chg('s03_인내', -1), *lower(0.45),
                                 setv('s03_말', join('아이고~ 조금만 더 쳐 줘요!\n', _wonv(V('s03_상인가')), '원이면 드릴게.'))],
                                [ifelse(ge(r_, 0.75),
                                        [setv('_mv', 3), chg('s03_인내', -1), *lower(0.25),
                                         setv('s03_말', join('에이, 그 값엔 안 돼요.\n', _wonv(V('s03_상인가')), '원은 받아야지.'))],
                                        [setv('_mv', 4), chg('s03_인내', -2), setv('s03_말', '장난해요?!\n그 값엔 어림없어요!')])]),
                         if_(le(V('s03_인내'), 0), setv('s03_인내', 0), setv('_mv', 4), setv('s03_말', '에잇, 안 팔아요!\n다음 손님~'),
                             setv('s03_거래', 2)),
                         *clampo]),
                 cast('s03_반응'), cast('s03_갱신'),
                 if_(eq(V('s03_거래'), 0), wait(0.3), setv('입력가능', 1)))]
    button(P, m.sc, '제안버튼', '이 값에 주세요!', IX - 50, -92, 116, 26, 'green', actions=offer)
    take = [if_(ok, setv('입력가능', 0), setv('s03_산값', V('s03_상인가')), setv('_mv', 1),
                setv('s03_말', '그래요, 그 값에 가져가요!'), setv('s03_거래', 1), cast('s03_반응'))]
    button(P, m.sc, '수락버튼', '부른 값에 사기', IX + 66, -92, 104, 26, 'red', actions=take)
    # 결과 띠
    res = m.T('결과글', '', 0, 6, 12, C_WHITE, F_BODY, True, 0, w=420, h=40, visible=False, bg=C_BOX)
    res.on(on_msg('s03_결과'), write(V('s03_말')), to_front(), show(), wait(1.6), hide())
    _pop(m, '점수팝', [('ok', K.big_text('거래 성공!', 26, 'green')), ('no', K.big_text('흥정 실패', 26, 'red'))], 's03_끝', 0, 40,
         hold=0.9, rise=False)
    mgr = hidden(m, '흥정담당')
    mgr.on(on_msg('게임시작'), setv('s03_물건', 1),
           until(or_(gt(V('s03_물건'), NI), eq(V('게임중'), 0)),
                 setv('s03_정가', LGET('s03_정가표', V('s03_물건'))),
                 setv('s03_최저', mul(ceil_(div(mul(V('s03_정가'), div(rnd(56, 78), 100)), 500)), 500)),
                 setv('s03_상인가', V('s03_정가')), setv('s03_제안', V('s03_정가')), setv('s03_인내', 4), setv('s03_거래', 0),
                 setv('s03_말', join('어서 와요! ', LGET('s03_이름', V('s03_물건')), '?\n정가 ', _wonv(V('s03_정가')), '원이에요~')),
                 setv('미니표시', join('물건 ', V('s03_물건'), '/', NI, ' · ', rounded(V('합계')), '점')),
                 cast('s03_새물건'), cast('s03_갱신'), setv('입력가능', 1),
                 wait_until(or_(ne(V('s03_거래'), 0), eq(V('게임중'), 0))),
                 setv('입력가능', 0),
                 if_(eq(V('게임중'), 1),
                     wait(0.7),
                     ifelse(eq(V('s03_거래'), 1),
                            [setv('s03_점', mul(20, div(sub(V('s03_정가'), V('s03_산값')), sub(V('s03_정가'), V('s03_최저'))))),
                             chg('합계', V('s03_점')), chg('맞춤', 1), setv('_mv', 1),
                             setv('s03_말', join('정가 ', _wonv(V('s03_정가')), '원 → ', _wonv(V('s03_산값')), '원에 샀어요!  +',
                                                rounded(V('s03_점')), '점\n(사장님 최저가는 ', _wonv(V('s03_최저')), '원)'))],
                            [setv('_mv', 2), setv('s03_말', join('흥정 실패! 0점\n(사장님 최저가는 ', _wonv(V('s03_최저')), '원)'))]),
                     cast('s03_끝'), cast('s03_결과'), wait(2.2)),
                 chg('s03_물건', 1)),
           setv('미니표시', join('흥정 끝 · ', rounded(V('합계')), '점')),
           *m.end_blocks(V('합계')))
    mgr.on(on_msg('시간끝'), *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('입력가능', 0), setv('s03_물건', 1), setv('s03_정가', prices[0]),
               setv('s03_상인가', prices[0]), setv('s03_제안', prices[0]), setv('s03_최저', prices[0]), setv('s03_인내', 4),
               setv('s03_말', '어서 와요~ 구경하고 가요!'), cast('s03_새물건'), cast('s03_갱신'))
    m.snd('s03_반응', ifelse(eq(V('_mv'), 1), [play('cash')],
                             [ifelse(eq(V('_mv'), 4), [play('bad')], [ifelse(eq(V('_mv'), 2), [play('tone3')], [play('tone1')])])]))
    m.snd('s03_끝', ifelse(eq(V('_mv'), 1), [play('coin')], [play('fail_big')]))
    m.finish('사장님이 속으로 정한 최저가에 가깝게 살수록 점수 UP!\n너무 깎으면 화내요 (인내심 0이면 안 팔아요).',
             '조작: −/+ 로 값을 정하고 "이 값에 주세요!"  ·  사장님 표정이 힌트예요')
    return True


# ================================================================== 4. 거스름돈 계산 (계산)
@game(4)
def g04(P, ctx):
    NC, TL = 7, 80
    m = mg(P, ctx, T, 4, time_limit=TL, status='손님 1/%d' % NC, dim=80)
    goods = [('상추', 1800), ('두부', 2300), ('대파', 2700), ('우유', 2600), ('감자', 3200), ('사과', 4500), ('계란', 6900),
             ('복숭아', 8400), ('꿀', 12800), ('쌀', 23500)]
    VAL = [10000, 5000, 1000, 500, 100]
    P.list('s04_품목', [g[0] for g in goods])
    P.list('s04_가격', [g[1] for g in goods])
    P.list('s04_권종', VAL)
    P.list('s04_개수', [0] * 5)
    P.list('s04_지폐', [5000, 10000, 20000, 50000])
    vars_(P, 's04_손님', 's04_합계', 's04_받은', 's04_거스름', 's04_준', 's04_장수', 's04_최소', 's04_줄', 's04_말', 's04_상태',
          's04_기록', 's04_i', 's04_n', 's04_w', 's04_점')
    ok = and_(eq(V('입력가능'), 1), eq(V('게임중'), 1))
    # 손님
    cu = m.S('손님', [('%d' % (k + 1), AA.s04_customer(k)) for k in range(4)], -178, -42)
    cu.on(on_msg('s04_새손님'), shape(add(mod(sub(V('s04_손님'), 1), 4), 1)), lx(-300), glide(0.25, -178, -42))
    cu.on(on_msg('s04_틀림'), rep(3, mvx(4), wait(0.03), mvx(-4), wait(0.03)))
    cu.on(on_msg('s04_정답'), rep(2, mvy(6), wait(0.05), mvy(-6), wait(0.05)))
    m.S('손님말칸', AA.s03_bubble(), -150, 66)
    say_ = m.T('손님말', '', -150, 70, 10, '#1A2050', F_BODY, True, 0, w=204, h=34)
    for msg in ('s04_새손님', 's04_틀림', 's04_정답'):
        say_.on(on_msg(msg), write(V('s04_말')))
    # 영수증
    RX, RY = -42, 30
    m.S('영수증', AA.s04_receipt(), RX, RY)
    rc = m.T('영수증글', '', RX, RY + 22, 9, '#2A2A36', F_BODY, True, 0, w=126, h=50)
    rc.on(on_msg('s04_새손님'), write(V('s04_줄')))
    tot = m.T('영수증합계', '', RX, RY - 16, 9, '#2A2A36', F_BODY, True, 0, w=126, h=14)
    tot.on(on_msg('s04_새손님'), write(join('합계  ', _wonv(V('s04_합계')), '원')))
    paid = m.T('받은돈', '', RX, RY - 34, 10, '#1E7A46', F_BODY, True, 0, w=126, h=14)
    paid.on(on_msg('s04_새손님'), write(join('받은 돈  ', _wonv(V('s04_받은')), '원')))
    chg_t = m.T('거스름글', '', RX, RY - 52, 10, '#C0283C', F_BODY, True, 0, w=126, h=14)
    chg_t.on(on_msg('s04_새손님'), ifelse(le(V('s04_손님'), 2), [*_won(V('s04_거스름'), 's04_w'), write(join('거스름돈  ', V('s04_w'), '원'))],
                                       [write('거스름돈  ?')]))
    # 거스름돈 쟁반
    TX, TY = 134, 34
    panel(P, m.sc, '쟁반', TX, TY, 204, 112, 'glass')
    m.T('쟁반글', '내가 줄 거스름돈', TX, TY + 42, 9, C_DIM, F_BODY, True, 0, w=150, h=14)
    tx = [TX - 76, TX - 38, TX, TX + 40, TX + 74]
    for j in range(5):
        ic = m.S('쟁반돈%d' % j, AA.s04_money(j), tx[j], TY + 16, scale=0.56 if j < 3 else 0.9)
        ic.on(on_msg('s04_갱신'), ifelse(eq(LGET('s04_개수', j + 1), 0), [fx('brightness', -55)], [fx('brightness', 0)]))
        cnt = m.T('쟁반수%d' % j, '×0', tx[j], TY - 4, 10, C_WHITE, F_NUM, False, 0, w=34, h=14)
        cnt.on(on_msg('s04_갱신'), write(join('×', LGET('s04_개수', j + 1))))
    sm = m.T('쟁반합', '', TX, TY - 30, 13, C_WHITE, F_NUM, False, 0, w=190, h=20)
    sm.on(on_msg('s04_갱신'), *_won(V('s04_준'), 's04_w'), write(join('= ', V('s04_w'), '원')))
    # 돈 버튼
    BY = -76
    bx = [-196, -122, -48, 18, 66]
    fly = m.S('나는돈', [('%d' % (j + 1), AA.s04_money(j)) for j in range(5)], 0, 0, visible=False)
    fly.on(on_msg('s04_날기'), shape(V('_mv')), xy(V('_mx'), BY), to_front(), show(),
           glide(0.12, add(TX - 76, mul(sub(V('_mv'), 1), 37.5)), TY + 16), hide())
    for j in range(5):
        b = m.S('돈%d' % j, AA.s04_money(j), bx[j], BY, scale=1.1 if j < 3 else 1.25)
        G.hover_scripts(b)
        b.on(on_click(), if_(ok, chg('s04_장수', 1), chg('s04_준', VAL[j]), lst_set('s04_개수', j + 1, add(LGET('s04_개수', j + 1), 1)),
                             setv('s04_기록', join(V('s04_기록'), j + 1)), setv('_mv', j + 1), setv('_mx', bx[j]),
                             cast('s04_갱신'), cast('s04_날기')))
        b.on(on_click(), b.pct(90), wait(0.06), b.pct(100))
        m.T('돈글%d' % j, ['만 원', '오천 원', '천 원', '500원', '100원'][j], bx[j], BY - 26, 8, C_DIM, F_BODY, True, 0, w=60, h=12)
    last = char_at(V('s04_기록'), slen(V('s04_기록')))
    undo = [if_(and_(ok, gt(slen(V('s04_기록')), 0)),
                setv('s04_i', last), lst_set('s04_개수', V('s04_i'), sub(LGET('s04_개수', V('s04_i')), 1)),
                chg('s04_준', mul(-1, LGET('s04_권종', V('s04_i')))), chg('s04_장수', -1),
                ifelse(le(slen(V('s04_기록')), 1), [setv('s04_기록', '')],
                       [setv('s04_기록', substr(V('s04_기록'), 1, sub(slen(V('s04_기록')), 1)))]),
                cast('s04_갱신'))]
    button(P, m.sc, '빼기버튼', '하나 빼기', 170, -58, 96, 24, 'steel', actions=undo)
    give = [if_(and_(ok, gt(V('s04_장수'), 0)),
                ifelse(eq(V('s04_준'), V('s04_거스름')),
                       [setv('입력가능', 0), setv('s04_상태', 1)],
                       [chg('틀림', 1), chg('합계', -3),
                        ifelse(lt(V('s04_준'), V('s04_거스름')), [setv('s04_말', '어? 거스름돈이 모자라요!')],
                               [setv('s04_말', '어머, 너무 많이 주셨어요!')]),
                        setv('_mv', 2), cast('s04_틀림'), cast('s04_판정')]))]
    button(P, m.sc, '건네기버튼', '건네기', 170, -90, 96, 28, 'green', icon='coin', actions=give)
    _pop(m, '판정글', [('ok', K.big_text('정확해요!', 24, 'green')), ('no', K.big_text('다시 세어 봐요', 20, 'red')),
                     ('best', K.big_text('최소 장수! +4', 22, 'royal'))], 's04_판정', 134, -2, hold=0.5)
    # 손님 진행
    greedy = [setv('s04_w', V('s04_거스름')), setv('s04_최소', 0)]
    for v in VAL:
        greedy += [chg('s04_최소', floor(div(V('s04_w'), v))), setv('s04_w', mod(V('s04_w'), v))]
    order = [setv('s04_합계', 0), setv('s04_줄', ''),
             ifelse(le(V('s04_손님'), 2), [setv('s04_n', 1)], [setv('s04_n', rnd(2, 3))]),
             rep(V('s04_n'), setv('s04_i', rnd(1, len(goods))), chg('s04_합계', LGET('s04_가격', V('s04_i'))),
                 setv('s04_줄', join(V('s04_줄'), LGET('s04_품목', V('s04_i')), '  ', _wonv(LGET('s04_가격', V('s04_i'))), '원\n'))),
             setv('s04_i', 1),
             rep(3, if_(le(LGET('s04_지폐', V('s04_i')), V('s04_합계')), chg('s04_i', 1))),
             if_(and_(lt(V('s04_i'), 4), le(rnd(1, 100), 40)), chg('s04_i', 1)),
             setv('s04_받은', LGET('s04_지폐', V('s04_i'))), setv('s04_거스름', sub(V('s04_받은'), V('s04_합계'))),
             *greedy,
             *[lst_set('s04_개수', j, 0) for j in range(1, 6)], setv('s04_준', 0), setv('s04_장수', 0), setv('s04_기록', ''),
             setv('s04_말', join(_wonv(V('s04_받은')), '원 드릴게요.\n거스름돈 주세요~')), setv('s04_상태', 0)]
    mgr = hidden(m, '계산담당')
    mgr.on(on_msg('게임시작'), setv('s04_손님', 1),
           until(or_(gt(V('s04_손님'), NC), eq(V('게임중'), 0)),
                 *order, setv('미니표시', join('손님 ', V('s04_손님'), '/', NC, ' · ', V('합계'), '점')),
                 cast('s04_새손님'), cast('s04_갱신'), setv('입력가능', 1),
                 wait_until(or_(eq(V('s04_상태'), 1), eq(V('게임중'), 0))),
                 if_(eq(V('게임중'), 1),
                     chg('맞춤', 1), setv('s04_점', 10), setv('_mv', 1),
                     if_(le(V('s04_장수'), V('s04_최소')), chg('s04_점', 4), setv('_mv', 3)),
                     chg('합계', V('s04_점')), setv('s04_말', '딱 맞네요! 고마워요~'),
                     setv('미니표시', join('손님 ', V('s04_손님'), '/', NC, ' · ', V('합계'), '점')),
                     cast('s04_정답'), cast('s04_판정'), wait(1.2)),
                 chg('s04_손님', 1)),
           *m.end_blocks(add(V('합계'), div(V('남은시간'), 5))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('틀림', 0), setv('입력가능', 0), setv('s04_손님', 1), setv('s04_합계', 0),
               setv('s04_받은', 0), setv('s04_거스름', 0), setv('s04_준', 0), setv('s04_장수', 0), setv('s04_기록', ''),
               setv('s04_줄', ''), setv('s04_말', '어서 오세요~ 세종 로컬푸드!'),
               *[lst_set('s04_개수', j, 0) for j in range(1, 6)], cast('s04_새손님'), cast('s04_갱신'))
    m.snd('s04_정답', play('cash'))
    m.snd('s04_틀림', play('bad'))
    m.snd('s04_날기', ifelse(ge(V('_mv'), 4), [play('coin')], [play('tick')]))
    m.finish('받은 돈 − 물건값 = 거스름돈! 지폐·동전을 눌러\n딱 맞게 건네세요. 적은 장수로 주면 보너스!',
             '조작: 돈 클릭 = 쟁반에 올리기 · "하나 빼기" · "건네기"  (손님 7명)')
    return True


# ================================================================== 5. 라떼 아트 그리기 (그리기)
@game(5)
def g05(P, ctx):
    SEC = 16
    paths = AA.s05_paths()
    NS = len(paths)
    names = ['하트', '튤립', '별']
    m = mg(P, ctx, T, 5, status='하트 1/3', dim=90)
    CX, CY = -40, -14
    xs, ys, st, cnt = [], [], [], []
    for p in paths:
        st.append(len(xs) + 1)
        cnt.append(len(p))
        xs += [CX + x for x, y in p]
        ys += [CY + y for x, y in p]
    P.list('s05_x', xs)
    P.list('s05_y', ys)
    P.list('s05_시작', st)
    P.list('s05_수', cnt)
    P.list('s05_이름', names)
    vars_(P, 's05_판', 's05_다음', 's05_끝번', 's05_좋음', 's05_나쁨', 's05_그리기', 's05_ax', 's05_ay', 's05_vx', 's05_vy',
          's05_L2', 's05_t', 's05_d2', 's05_점', 's05_정확', 's05_진행', 's05_펜')
    m.S('잔', AA.s05_cup(), CX, CY)
    gd = m.S('도안', [('%d' % (k + 1), AA.s05_guide(k, paths[k])) for k in range(NS)], CX, CY)
    gd.on(on_msg('s05_새판'), shape(V('s05_판')), show())
    # 붓 (우유 거품)
    pen = m.S('우유붓', K.icon_img('star', 2), 0, -300)
    mx, my = V('_mx'), V('_my')
    inside = lt(add(mul(sub(mx, CX), sub(mx, CX)), mul(sub(my, CY), sub(my, CY))), 96 * 96)
    seg = [setv('s05_ax', LGET('s05_x', sub(V('s05_다음'), 1))), setv('s05_ay', LGET('s05_y', sub(V('s05_다음'), 1))),
           setv('s05_vx', sub(LGET('s05_x', V('s05_다음')), V('s05_ax'))), setv('s05_vy', sub(LGET('s05_y', V('s05_다음')), V('s05_ay'))),
           setv('s05_L2', add(mul(V('s05_vx'), V('s05_vx')), mul(V('s05_vy'), V('s05_vy')))), if_(lt(V('s05_L2'), 1), setv('s05_L2', 1))]
    nx, ny = LGET('s05_x', V('s05_다음')), LGET('s05_y', V('s05_다음'))
    near = lt(add(mul(sub(mx, nx), sub(mx, nx)), mul(sub(my, ny), sub(my, ny))), 15 * 15)
    started = gt(V('s05_다음'), LGET('s05_시작', V('s05_판')))
    measure = [setv('s05_t', div(add(mul(sub(mx, V('s05_ax')), V('s05_vx')), mul(sub(my, V('s05_ay')), V('s05_vy'))), V('s05_L2'))),
               if_(lt(V('s05_t'), 0), setv('s05_t', 0)), if_(gt(V('s05_t'), 1), setv('s05_t', 1)),
               setv('s05_d2', add(mul(sub(mx, add(V('s05_ax'), mul(V('s05_t'), V('s05_vx')))), sub(mx, add(V('s05_ax'), mul(V('s05_t'), V('s05_vx'))))),
                                  mul(sub(my, add(V('s05_ay'), mul(V('s05_t'), V('s05_vy')))), sub(my, add(V('s05_ay'), mul(V('s05_t'), V('s05_vy'))))))),
               ifelse(lt(V('s05_d2'), 12 * 12), [chg('s05_좋음', 1)], [chg('s05_나쁨', 1)])]
    draw = [setv('_mx', mouse_x()), setv('_my', mouse_y()),
            ifelse(and_(and_(mouse_down(), eq(V('s05_그리기'), 1)), inside),
                   [ifelse(eq(V('s05_펜'), 0), [xy(mx, my), pen_down(), setv('s05_펜', 1)], [xy(mx, my)]),
                    if_(started, *measure),
                    if_(near, chg('s05_다음', 1),
                        ifelse(gt(V('s05_다음'), V('s05_끝번')), [setv('s05_그리기', 0)], [*seg, cast('s05_점이동')]))],
                   [if_(eq(V('s05_펜'), 1), pen_up(), setv('s05_펜', 0))])]
    pen.on(on_scene(), pen_up(), pen_clear(), setv('s05_펜', 0))
    pen.on(on_msg('s05_새판'), pen_up(), pen_clear(), setv('s05_펜', 0), pen_color('#FFF6E6'), pen_size(7), xy(0, -300))
    pen.on(on_msg('게임시작'), until(eq(V('게임중'), 0), *draw), pen_up())
    ring = m.S('다음점', AA.s05_ring(), 0, -300, visible=False)
    ring.on(on_msg('s05_점이동'), xy(nx, ny), show())
    ring.on(on_msg('s05_판끝'), hide())
    ring.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ring.pct(130), wait(0.12), ring.pct(100), wait(0.12)))
    hint = m.T('시작안내', '여기서 시작!', 0, -300, 9, '#7DFFB4', F_BODY, True, 0, w=80, h=14, visible=False)
    hint.on(on_msg('s05_새판'), xy(LGET('s05_x', V('s05_다음')), add(LGET('s05_y', V('s05_다음')), 16)), show())
    hint.on(on_msg('s05_점이동'), if_(gt(V('s05_다음'), add(LGET('s05_시작', V('s05_판')), 1)), hide()))
    hint.on(on_msg('s05_판끝'), hide())
    # 오른쪽 판
    PX = 160
    panel(P, m.sc, '주문판', PX, -6, 140, 196, 'glass', header='royal')
    m.T('주문제목', '오늘의 주문', PX, 78, 10, C_WHITE, F_NUM, False, 0, w=120, h=16)
    od = m.T('주문이름', '', PX, 54, 15, '#FFD9A8', F_NUM, False, 0, w=130, h=22)
    od.on(on_msg('s05_새판'), write(join(LGET('s05_이름', V('s05_판')), ' 라떼')))
    info = m.T('진행글', '', PX, 22, 10, C_WHITE, F_BODY, True, 0, w=130, h=36)
    info.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                    setv('s05_진행', sub(V('s05_다음'), LGET('s05_시작', V('s05_판')))),
                                    setv('s05_정확', rounded(mul(100, div(V('s05_좋음'), add(add(V('s05_좋음'), V('s05_나쁨')), 0.001))))),
                                    write(join('따라 그린 점 ', V('s05_진행'), '/', sub(LGET('s05_수', V('s05_판')), 1), '\n정확도 ',
                                               V('s05_정확'), '%')), wait(0.2)))
    res = m.T('판결과', '', PX, -42, 10, '#B9C7FF', F_BODY, True, 0, w=130, h=60)
    res.on(on_scene(), write(''))
    res.on(on_msg('s05_판끝'), append_text(join(LGET('s05_이름', V('s05_판')), '  ', rounded(V('s05_점')), '점\n')))
    _pop(m, '판팝', [('a', K.big_text('훌륭해요!', 28, 'green')), ('b', K.big_text('좋아요!', 28, 'royal')),
                    ('c', K.big_text('아쉬워요', 26, 'red'))], 's05_판팝', CX, CY, hold=0.7, rise=False)
    mgr = hidden(m, '라떼담당')
    acc = div(V('s05_좋음'), add(add(V('s05_좋음'), V('s05_나쁨')), 0.001))
    mgr.on(on_msg('게임시작'), setv('s05_판', 1),
           until(or_(gt(V('s05_판'), NS), eq(V('게임중'), 0)),
                 setv('s05_다음', LGET('s05_시작', V('s05_판'))), setv('s05_끝번', sub(add(V('s05_다음'), LGET('s05_수', V('s05_판'))), 1)),
                 setv('s05_좋음', 0), setv('s05_나쁨', 0),
                 cast('s05_새판'), cast('s05_점이동'), wait(0.1), setv('s05_그리기', 1), reset_timer(),
                 until(or_(eq(V('s05_그리기'), 0), gt(timer(), SEC)),
                       setv('미니표시', join(LGET('s05_이름', V('s05_판')), ' ', V('s05_판'), '/', NS, ' · ', ceil_(sub(SEC, timer())), '초')),
                       wait(0.1)),
                 setv('s05_그리기', 0), wait(0.1),
                 setv('s05_t', mul(acc, 1.15)), if_(gt(V('s05_t'), 1), setv('s05_t', 1)),
                 setv('s05_점', mul(100.0 / NS, mul(div(sub(V('s05_다음'), LGET('s05_시작', V('s05_판'))), sub(LGET('s05_수', V('s05_판')), 1)),
                                                 V('s05_t')))),
                 chg('합계', V('s05_점')),
                 ifelse(ge(V('s05_점'), 27), [setv('_mv', 1)], [ifelse(ge(V('s05_점'), 17), [setv('_mv', 2)], [setv('_mv', 3)])]),
                 cast('s05_판끝'), cast('s05_판팝'), wait(1.6), chg('s05_판', 1)),
           *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('s05_판', 1), setv('s05_그리기', 0), setv('s05_다음', 1), setv('s05_좋음', 0), setv('s05_나쁨', 0),
               cast('s05_새판'))
    m.snd('s05_점이동', play('tick'))
    m.snd('s05_판팝', ifelse(eq(V('_mv'), 3), [play('bad')], [play('good')]))
    m.finish('마우스를 누른 채 초록 점을 따라 점선을 그려요!\n하트·튤립·별 3잔, 한 잔에 %d초. 정확할수록 점수 UP' % SEC,
             '조작: 마우스 누른 채 끌기 (초록 점 → 다음 초록 점)')
    return True
