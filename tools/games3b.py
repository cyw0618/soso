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


# ================================================================== 12. 연꽃 스도쿠 (4×4)
def _sudoku4():
    import itertools
    rows = list(itertools.permutations([1, 2, 3, 4]))
    out = []
    for g in itertools.product(rows, repeat=4):
        if all(len({g[r][c] for r in range(4)}) == 4 for c in range(4)) and \
           all(len({g[br + i][bc + j] for i in range(2) for j in range(2)}) == 4 for br in (0, 2) for bc in (0, 2)):
            out.append(sum(g, ()))
    return out


def _k12_puzzles(n_given, count, rng, sols):
    got = []
    while len(got) < count:
        sol = rng.choice(sols)
        cells = list(range(16))
        rng.shuffle(cells)
        giv = set(range(16))
        for k in cells:
            if len(giv) <= n_given:
                break
            t = giv - {k}
            if sum(1 for s in sols if all(s[j] == sol[j] for j in t)) == 1:
                giv = t
        if len(giv) != n_given:
            continue
        p = ''.join(str(sol[j]) if j in giv else '0' for j in range(16))
        if p not in [x[0] for x in got]:
            got.append((p, ''.join(map(str, sol))))
    return got


@game(12)
def g12(P, ctx):
    TL, R, NV = 120, 3, 6
    m = mg(P, ctx, T, 12, time_limit=TL, status='연못 1/%d' % R, dim=70)
    rng = random.Random(1203)
    sols = _sudoku4()
    puz = []
    for ng in (8, 6, 5):
        puz += _k12_puzzles(ng, NV, rng, sols)
    P.list('k12_퍼즐', [p for p, s in puz])
    P.list('k12_정답', [s for p, s in puz])
    P.list('k12_판', [0] * 16)
    P.list('k12_고정', [0] * 16)
    peers = []
    for i in range(16):
        r, c = divmod(i, 4)
        ps = [r * 4 + cc for cc in range(4) if cc != c] + [rr * 4 + c for rr in range(4) if rr != r]
        br, bc = r // 2 * 2, c // 2 * 2
        ps += [(br + a) * 4 + bc + b for a in range(2) for b in range(2) if br + a != r and bc + b != c]
        assert len(ps) == 7
        peers += [p + 1 for p in ps]
    P.list('k12_이웃', peers)
    CX, CY, PI, GAP = -40, -14, 46, 8
    pos = [(CX + (c - 1.5) * PI + (GAP / 2 if c >= 2 else -GAP / 2), CY - (r - 1.5) * PI - (GAP / 2 if r >= 2 else -GAP / 2))
           for r in range(4) for c in range(4)]
    P.list('k12_x', [p[0] for p in pos])
    P.list('k12_y', [p[1] for p in pos])
    vars_(P, 'k12_선택', 'k12_ok', 'k12_맞은', 'k12_빈칸', 'k12_입력', 'k12_퍼즐번호', 'k12_시도')
    m.S('연못판', B3.k12_board(PI, GAP), CX, CY)
    ring = m.S('선택테', A3.ring('k12_sel', 25, (255, 236, 120), 2.5), 0, -300, visible=False)
    sel = V('k12_선택')
    ring.on(on_msg('k12_선택'), xy(LGET('k12_x', sel), LGET('k12_y', sel)), to_front(), show(), ring.pct(125),
            rep(4, ring.grow_pct(-6.25), wait(0.016)))
    ring.on(on_msg('k12_완성'), hide())
    pics = [('e', B3.k12_cell('e'))] + [('%s%d' % (k, n), B3.k12_cell(k, n)) for k in 'gpx' for n in range(1, 5)]
    cell = m.S('연잎', pics, 0, -300, visible=False)
    for v in ('내번호', '복제', '_v', '_c'):
        cell.local(v, 0)
    me = V('내번호')
    cell.on(on_scene(), setv('내번호', 0), rep(16, chg('내번호', 1), clone_self()))
    cell.on(on_clone(), setv('복제', 1), xy(LGET('k12_x', me), LGET('k12_y', me)), shape('e'), show())
    cell.on(on_msg('k12_갱신'), if_(eq(V('복제'), 1),
            setv('_v', LGET('k12_판', me)), setv('_c', 0),
            if_(gt(V('_v'), 0), *[if_(eq(LGET('k12_판', LGET('k12_이웃', add(mul(sub(me, 1), 7), j))), V('_v')), setv('_c', 1))
                                  for j in range(1, 8)]),
            ifelse(gt(LGET('k12_고정', me), 0), [shape(add(1, V('_v')))],
                   [ifelse(eq(V('_v'), 0), [shape(1)],
                           [ifelse(eq(V('_c'), 1), [shape(add(9, V('_v')))], [shape(add(5, V('_v')))]),
                            if_(eq(V('_v'), char_at(LGET('k12_정답', V('k12_퍼즐번호')), me)), chg('k12_맞은', 1))])]),
            if_(and_(gt(V('_v'), 0), eq(V('_c'), 0)), chg('k12_ok', 1))))
    cell.on(on_msg('k12_입력됨'), if_(and_(eq(V('복제'), 1), eq(me, sel)),
                                    rep(3, cell.grow_pct(6), wait(0.016)), rep(3, cell.grow_pct(-6), wait(0.016))))
    cell.on(on_msg('k12_완성'), if_(eq(V('복제'), 1), wait(mul(me, 0.03)), rep(4, cell.grow_pct(5), rot_by(4), wait(0.016)),
                                  rep(4, cell.grow_pct(-5), rot_by(-4), wait(0.016))))
    ok_input = and_(and_(eq(V('게임중'), 1), eq(V('k12_입력'), 1)), gt(sel, 0))
    # 값 넣기: _mv 에 새 값 → 판 갱신 → 검사
    put = [if_(ok_input,
               ifelse(gt(LGET('k12_고정', sel), 0), [cast('k12_잠김')],
                      [lst_set('k12_판', sel, V('_mv')), chg('k12_시도', 1), cast('k12_입력됨'), cast('k12_검사')]))]
    cell.on(on_click(), if_(and_(and_(eq(V('복제'), 1), eq(V('게임중'), 1)), eq(V('k12_입력'), 1)),
                            ifelse(eq(sel, me),
                                   [setv('_mv', mod(add(LGET('k12_판', me), 1), 5)), *put],
                                   [setv('k12_선택', me), cast('k12_선택')])))
    keyer = hidden(m, '스도쿠키')
    for n, kc in enumerate([48, K_1, K_2, K_3, K_4]):
        keyer.on(on_key(kc), setv('_mv', n), *put)
    for kc in (8, 46):
        keyer.on(on_key(kc), setv('_mv', 0), *put)
    for kc, d, cond in ((K_LEFT, -1, gt(mod(sub(sel, 1), 4), 0)), (K_RIGHT, 1, lt(mod(sub(sel, 1), 4), 3)),
                        (K_UP, -4, gt(sel, 4)), (K_DOWN, 4, le(sel, 12))):
        keyer.on(on_key(kc), if_(and_(eq(V('게임중'), 1), eq(V('k12_입력'), 1)),
                                 ifelse(eq(sel, 0), [setv('k12_선택', 1)], [if_(cond, chg('k12_선택', d))]), cast('k12_선택')))
    # 오른쪽 숫자 단추
    BX = 150
    m.T('단추안내', '칸을 고르고 숫자', BX, 70, 9, C_DIM, F_BODY, True, 0, w=110, h=14)
    for n in range(1, 5):
        button(P, m.sc, 'k12숫자%d' % n, str(n), BX - 24 + 48 * ((n - 1) % 2), 44 - 34 * ((n - 1) // 2), 42, 30, 'royal',
               actions=[setv('_mv', n), *put])
    button(P, m.sc, 'k12지우기', '지우기', BX, -24, 90, 26, 'steel', actions=[setv('_mv', 0), *put])
    info = m.T('스도쿠안내', '', BX, -66, 9, C_WHITE, F_BODY, True, 0, w=120, h=44)
    info.on(on_msg('k12_새판'), write(join('연못 ', V('라운드'), ' / %d\n빈 칸 ' % R, V('k12_빈칸'), '개')))
    m.T('스도쿠규칙', '가로줄 · 세로줄 · 2×2 구역에\n1~4가 한 번씩!', -40, 96, 9, C_DIM, F_BODY, True, 0, w=200, h=26)
    _pop(m, '완성글', K.big_text('연꽃 활짝!', 34, 'royal'), CX, CY, 'k12_완성', hold=0.6)
    lock = m.T('잠김글', '처음부터 있던 연꽃은 못 바꿔요', CX, -122, 9, C_ACC, F_BODY, True, 0, w=220, h=14, visible=False)
    lock.on(on_msg('k12_잠김'), show(), wait(0.9), hide())
    # 검사 담당
    chk = hidden(m, '스도쿠검사')
    chk.on(on_msg('k12_검사'), setv('k12_ok', 0), setv('k12_맞은', 0), cast_wait('k12_갱신'),
           if_(and_(eq(V('k12_ok'), 16), eq(V('k12_입력'), 1)), setv('k12_입력', 0), chg('맞춤', 1), cast('k12_완성')))
    mgr = hidden(m, '스도쿠담당')
    load = [setv('k12_퍼즐번호', add(mul(sub(V('라운드'), 1), NV), rnd(1, NV))),
            setv('_s', LGET('k12_퍼즐', V('k12_퍼즐번호'))), setv('k12_빈칸', 0),
            *[lst_set('k12_판', k, char_at(V('_s'), k)) for k in range(1, 17)],
            *[lst_set('k12_고정', k, char_at(V('_s'), k)) for k in range(1, 17)],
            setv('k12_빈칸', str_count(V('_s'), '0')),
            setv('k12_선택', 0), cast('k12_새판'), cast('k12_검사'), setv('k12_입력', 1),
            setv('미니표시', join('연못 ', V('라운드'), '/%d' % R))]
    mgr.on(on_msg('게임시작'), setv('라운드', 1), *load)
    mgr.on(on_msg('k12_완성'), wait(1.4), chg('라운드', 1),
           ifelse(gt(V('라운드'), R), [*m.end_blocks(add(mul(V('맞춤'), 27), mul(V('남은시간'), 0.35)))], load))
    mgr.on(on_msg('시간끝'), setv('k12_입력', 0),
           *m.end_blocks(add(mul(V('맞춤'), 27), mul(div(V('k12_맞은'), V('k12_빈칸')), 22))))
    vars_(P, '_s')
    m.on_start(setv('맞춤', 0), setv('k12_입력', 0), setv('k12_선택', 0), setv('k12_빈칸', 1), setv('k12_맞은', 0),
               setv('k12_퍼즐번호', 1), setv('k12_시도', 0), *[lst_set('k12_판', k, 0) for k in range(1, 17)])
    m.snd('k12_입력됨', play('pop'))
    m.snd('k12_선택', play('tick'))
    m.snd('k12_완성', play('fanfare'))
    m.snd('k12_잠김', play('bad'))
    m.finish('가로줄·세로줄·굵은 2×2 구역마다 1~4가 한 번씩\n들어가게 연잎을 채우세요! 연못 3개를 완성하면 끝.',
             '조작: 칸 클릭 → 숫자키 1~4 (또는 숫자 단추) · 같은 칸 다시 클릭 = 숫자 바꾸기 · 0 = 지우기')
    return True


# ================================================================== 13. 로켓 발사 (추진 조절)
@game(13)
def g13(P, ctx):
    TL, GOAL = 55, 100
    k = 1.6
    G_, VM0, VMK = round(0.12 * k * k, 4), round(0.8 * k, 4), round(0.045 * k, 4)
    F = [4.2, 3.6, 3.3]
    A = [round(a * k * k, 4) for a in (0.42, 0.40, 0.36)]
    m = mg(P, ctx, T, 13, time_limit=TL, status='고도 0km', dim=40)
    P.list('k13_연료', F)
    P.list('k13_추력', A)
    vars_(P, 'k13_h', 'k13_v', 'k13_vmax', 'k13_비', 'k13_단', 'k13_엔진', 'k13_분사', 'k13_hp', 'k13_최고', 'k13_예상',
          'k13_dt', 'k13_t', 'k13_흔들', 'k13_끝', 'k13_결과', 'k13_dx', 'k13_남은연료')
    h, v = V('k13_h'), V('k13_v')
    eng = V('k13_엔진')
    # 우주(위로 갈수록 어두워짐) + 별
    import mg_art as A1
    space = m.S('우주', A1.plain_rect(480, 270, (3, 5, 18, 255), 'k13_space'), 0, 0)
    space.on(on_scene(), fx('transparency', 100))
    space.on(on_msg('게임시작'), until(eq(V('게임중'), 0), fx('transparency', sub(100, mul(h, 0.92))), wait(0.1)))
    for i in range(6):
        st = m.S('별%d' % i, B3.k13_stars(), -160 + 160 * (i % 3), 90 - 90 * (i // 3) - 45, visible=True)
        st.on(on_scene(), fx('transparency', 100))
        st.on(on_msg('게임시작'), until(eq(V('게임중'), 0), fx('transparency', sub(160, mul(h, 1.6))), wait(0.12)))
    # 발사대 (처음에만 보이고 아래로 사라짐)
    RX = -30
    tower = m.S('발사대', B3.k13_tower(), RX + 18, -82)
    tower.on(on_scene(), ly(-82), show())
    tower.on(on_msg('게임시작'), until(or_(eq(V('게임중'), 0), gt(h, 6)), ly(sub(-82, mul(h, 60))), wait(0.02)), hide())
    # 구름 (낮은 고도에서 지나감)
    cloud = m.S('구름', [('a', B3.k13_cloud(1)), ('b', B3.k13_cloud(2))], 0, 200, visible=False)
    cloud.local('복제', 0)
    cloud.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                    if_(and_(gt(h, 2), lt(h, 45)), if_(gt(v, 0.3), clone_self())),
                                    wait(div(rnd(5, 9), add(abs_(v), 2)))))
    cloud.on(on_clone(), setv('복제', 1), shape(rnd(1, 2)), xy(rnd(-200, 200), 170), cloud.pct(rnd(70, 130)),
             fx('transparency', rnd(10, 50)), show(),
             until(or_(lt(obj_y(), -180), eq(V('게임중'), 0)), mvy(mul(v, -1.6)), wait(0.016)), del_clone())
    # 로켓 (3단) + 불꽃
    YS = {3: 50, 2: 1, 1: -52}
    parts = {}
    for st_ in (1, 2, 3):
        o = m.S('로켓%d단' % st_, B3.k13_stage(st_), RX, YS[st_])
        parts[st_] = o
        o.on(on_scene(), xy(RX, YS[st_]), rot(0), fx_clear(), show())
        o.on(on_msg('게임시작'), until(or_(eq(V('게임중'), 0), lt(V('k13_단'), st_ + 1) if st_ < 3 else eq(V('게임중'), 0)),
                                    lx(add(RX, V('k13_dx'))), wait(0.016)))
        if st_ < 3:
            o.local('_vy', 0)
            o.on(on_msg('k13_분리%d' % st_), setv('_vy', 0),
                 rep(40, chg('_vy', -0.25), mvy(V('_vy')), rot_by(1.5 if st_ == 1 else -1.5), fx_add('transparency', 2.5), wait(0.016)),
                 hide())
        o.on(on_msg('k13_폭발'), hide())
    flame = m.S('불꽃', [('a', B3.k13_flame(1)), ('b', B3.k13_flame(2))], RX, -98, visible=False)
    flame.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                    ifelse(eq(V('k13_분사'), 1),
                                           [show(), next_shape(), lx(add(RX, V('k13_dx'))),
                                            ifelse(eq(V('k13_단'), 1), [ly(-98)], [ifelse(eq(V('k13_단'), 2), [ly(-38)], [ly(-2)])])],
                                           [hide()]), wait(0.05)), hide())
    boom = m.S('폭발', K.big_text('펑!', 44, 'red'), RX, 10, visible=False)
    boom.on(on_scene(), hide())
    boom.on(on_msg('k13_폭발'), boom.pct(30), show(), rep(10, boom.grow_pct(10), wait(0.016)))
    # 왼쪽 계기판: 속도계, 연료, 기체
    GX = -170
    panel(P, m.sc, '계기판', GX, -6, 120, 206, 'glass')
    m.S('속도계', B3.k13_gauge(), GX, 54)
    needle = m.S('속도바늘', B3.k13_needle(), GX, 31)
    needle.on(on_msg('게임시작'), until(eq(V('게임중'), 0), rot(sub(mul(V('k13_비'), 138.5), 90)), wait(0.03)))
    needle.on(on_scene(), rot(-90))
    vt = m.T('속도글', '0.0 km/s', GX, 18, 10, C_WHITE, F_NUM, False, 0, w=100, h=14)
    vt.on(on_msg('게임시작'), until(eq(V('게임중'), 0), write(join(round1(v), ' km/s')), wait(0.1)))
    warn = m.T('경고글', '', GX, 3, 9, C_RED, F_BODY, True, 0, w=110, h=13)
    warn.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                   ifelse(eq(V('k13_흔들'), 1), [write('너무 빨라요!')],
                                          [ifelse(and_(lt(V('k13_비'), 0.6), gt(h, 1)), [write('더 밀어도 돼요')], [write('')])]),
                                   wait(0.15)))
    fbars = K.bar_set('k13_fuel', 70, 9, 'royal')
    for st_ in (1, 2, 3):
        yy = -22 - 18 * (st_ - 1)
        m.T('연료이름%d' % st_, '%d단' % st_, GX - 44, yy, 9, C_WHITE, F_NUM, False, 0, w=24, h=13)
        fb = m.S('연료막대%d' % st_, fbars, GX + 10, yy)
        fb.on(on_scene(), shape(41))
        fb.on(on_msg('게임시작'), until(eq(V('게임중'), 0), *_bar(fb, div(LGET('k13_연료', st_), F[st_ - 1])), wait(0.1)))
    hbars = K.bar_set('k13_hp', 70, 9, 'red')
    m.T('기체이름', '기체', GX - 44, -78, 9, C_WHITE, F_NUM, False, 0, w=24, h=13)
    hb = m.S('기체막대', hbars, GX + 10, -78)
    hb.on(on_scene(), shape(41))
    hb.on(on_msg('게임시작'), until(eq(V('게임중'), 0), *_bar(hb, div(V('k13_hp'), 100)), wait(0.1)))
    sep = m.S('분리안내', K.badge('S 키: 빈 단 분리!', 104, 20, 'red'), GX, -98, visible=False)
    sep.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                  ifelse(gt(V('k13_엔진'), V('k13_단')), [show(), wait(0.25), hide(), wait(0.15)], [hide(), wait(0.1)])))
    # 오른쪽: 고도 막대 + 예상 고도
    AX, AY0, AH = 200, -100, 190
    abars = K.bar_set('k13_alt', AH, 12, 'royal')
    ab = m.S('고도막대', abars, AX, AY0 + AH / 2)
    ab.on(on_scene(), rot(-90), shape(1))
    ab.on(on_msg('게임시작'), until(eq(V('게임중'), 0), *_bar(ab, div(h, GOAL)), wait(0.08)))
    m.S('목표선', K.badge('궤도 100km', 76, 16, 'royal'), AX - 30, AY0 + AH + 2)
    mk = m.S('예상표', B3.k13_marker(), AX + 14, AY0)
    mk.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ly(add(AY0, mul(AH / GOAL, V('k13_예상')))), wait(0.05)))
    m.T('예상글', '◀ 예상\n최고 고도', AX + 12, AY0 - 20, 7, '#FFD966', F_BODY, True, 0, w=50, h=20)
    at = m.T('고도글', '0 km', AX - 44, 0, 14, C_WHITE, F_NUM, False, 2, w=80, h=20)
    at.on(on_msg('게임시작'), until(eq(V('게임중'), 0), write(join(floor(h), ' km')), wait(0.1)))
    # 결과 글
    res = m.S('결과', [('ok', K.big_text('궤도 진입 성공!', 30, 'royal')), ('fail', K.big_text('궤도 실패...', 28, 'white')),
                     ('boom', K.big_text('기체 폭발!', 30, 'red'))], 30, 30, visible=False)
    res.on(on_scene(), hide())
    res.on(on_msg('k13_결과'), shape(V('k13_결과')), res.pct(40), show(), rep(6, res.grow_pct(10), wait(0.016)))
    # 물리 (시간 기준)
    fuel_e = LGET('k13_연료', eng)
    thrusting = and_(key(K_SPACE), gt(fuel_e, 0))
    left = add(LGET('k13_연료', 1), LGET('k13_연료', 2), LGET('k13_연료', 3))
    phys = hidden(m, '로켓물리')
    score_ok = sub(add(62, mul(div(V('k13_남은연료'), sum(F)), 200)), mul(sub(100, V('k13_hp')), 0.1))
    score_fail = sub(mul(V('k13_최고'), 0.6), mul(sub(100, V('k13_hp')), 0.1))
    phys.on(on_msg('게임시작'), setv('k13_t', timer()),
            until(or_(eq(V('게임중'), 0), eq(V('k13_끝'), 1)),
                  setv('k13_dt', sub(timer(), V('k13_t'))), setv('k13_t', timer()),
                  if_(gt(V('k13_dt'), 0.1), setv('k13_dt', 0.1)),
                  # 엔진: 연료가 남은 가장 아래 단
                  if_(and_(le(fuel_e, 0), lt(eng, 3)), chg('k13_엔진', 1)),
                  setv('k13_vmax', add(VM0, mul(VMK, h))),
                  ifelse(thrusting,
                         [setv('k13_분사', 1),
                          setv('_ma', mul(LGET('k13_추력', eng), add(1, mul(0.5, sub(1, div(fuel_e, LGET('k13_연료최대', eng))))))),
                          if_(gt(eng, V('k13_단')), setv('_ma', mul(V('_ma'), 0.5))),
                          chg('k13_v', mul(sub(V('_ma'), G_), V('k13_dt'))),
                          lst_set('k13_연료', eng, sub(fuel_e, V('k13_dt'))),
                          if_(lt(fuel_e, 0), lst_set('k13_연료', eng, 0))],
                         [setv('k13_분사', 0), chg('k13_v', mul(-G_, V('k13_dt')))]),
                  chg('k13_h', mul(v, V('k13_dt'))),
                  if_(lt(h, 0), setv('k13_h', 0), if_(lt(v, 0), setv('k13_v', 0))),
                  if_(gt(h, V('k13_최고')), setv('k13_최고', h)),
                  setv('k13_비', div(v, V('k13_vmax'))), if_(gt(V('k13_비'), 1.3), setv('k13_비', 1.3)),
                  if_(lt(V('k13_비'), 0), setv('k13_비', 0)),
                  ifelse(gt(div(v, V('k13_vmax')), 1.03),
                         [setv('k13_흔들', 1), chg('k13_hp', mul(mul(sub(div(v, V('k13_vmax')), 1.03), -150), V('k13_dt'))),
                          setv('k13_dx', rnd(-3, 3))],
                         [setv('k13_흔들', 0), setv('k13_dx', 0)]),
                  ifelse(gt(v, 0), [setv('k13_예상', add(h, div(mul(v, v), 2 * G_)))], [setv('k13_예상', h)]),
                  if_(gt(V('k13_예상'), GOAL * 1.04), setv('k13_예상', GOAL * 1.04)),
                  setv('미니표시', join('고도 ', floor(h), 'km')),
                  setv('k13_남은연료', left),
                  # 끝 판정
                  if_(ge(h, GOAL), setv('k13_끝', 1), setv('k13_결과', 1)),
                  if_(le(V('k13_hp'), 0), setv('k13_hp', 0), setv('k13_끝', 1), setv('k13_결과', 3)),
                  if_(and_(and_(lt(v, 0), le(V('k13_남은연료'), 0)), eq(V('k13_끝'), 0)), setv('k13_끝', 1), setv('k13_결과', 2)),
                  if_(and_(and_(le(h, 0), gt(V('k13_최고'), 1)), eq(V('k13_끝'), 0)), setv('k13_끝', 1), setv('k13_결과', 2))),
            setv('k13_분사', 0), setv('k13_흔들', 0), setv('k13_dx', 0),
            if_(eq(V('게임중'), 1),
                cast('k13_결과'),
                if_(eq(V('k13_결과'), 3), cast('k13_폭발')),
                wait(1.6),
                ifelse(eq(V('k13_결과'), 1), [*m.end_blocks(score_ok)],
                       [ifelse(eq(V('k13_결과'), 2), [*m.end_blocks(score_fail)], [*m.end_blocks(mul(V('k13_최고'), 0.4))])])))
    # 분리 (S)
    phys.on(on_key(K_S), if_(and_(and_(eq(V('게임중'), 1), eq(V('k13_끝'), 0)), lt(V('k13_단'), 3)),
                             lst_set('k13_연료', V('k13_단'), 0),
                             ifelse(eq(V('k13_단'), 1), [cast('k13_분리1')], [cast('k13_분리2')]),
                             chg('k13_단', 1), if_(lt(eng, V('k13_단')), setv('k13_엔진', V('k13_단'))), cast('k13_분리')))
    phys.on(on_msg('시간끝'), setv('k13_끝', 1), *m.end_blocks(score_fail))
    P.list('k13_연료최대', F)
    m.on_start(setv('k13_h', 0), setv('k13_v', 0), setv('k13_단', 1), setv('k13_엔진', 1), setv('k13_분사', 0), setv('k13_hp', 100),
               setv('k13_최고', 0), setv('k13_예상', 0), setv('k13_흔들', 0), setv('k13_끝', 0), setv('k13_결과', 0),
               setv('k13_dx', 0), setv('k13_비', 0), setv('k13_남은연료', sum(F)),
               *[lst_set('k13_연료', i + 1, F[i]) for i in range(3)])
    m.snd('k13_분리', play('pop'))
    m.snd('k13_폭발', play('fail_big'))
    m.snd('k13_결과', ifelse(eq(V('k13_결과'), 1), [play('fanfare')], [play('bad')]))
    m.snd('게임시작', until(eq(V('게임중'), 0), if_(eq(V('k13_흔들'), 1), play('alarm'), wait(0.5)), wait(0.05)))
    m.finish('스페이스를 누르는 동안 엔진 분사! 속도계 바늘이 빨간 칸에\n가면 기체가 망가져요. 단 연료가 다 떨어지면 S로 분리!',
             '조작: SPACE 누르기 = 분사 · S = 단 분리  ·  예상 최고 고도(◀)가 100km면 떼도 OK, 남은 연료가 많을수록 점수 UP')
    return True
