# -*- coding: utf-8 -*-
"""대통령 선거 미니게임 11~20번."""
import random
from games_common import *
import mg_art3 as A3

T = 3
GAMES, game = registry()
import art3b as B3
import os
_TS = float(os.environ.get('K3B_TS', '1'))      # 테스트용: 시간 제한 배율 (느린 하네스에서만 올린다)


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
    m = mg(P, ctx, T, 11, time_limit=TL * _TS, status='점수 0', dim=90)
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
    combo = m.T('콤보', ' ', 0, -30, 11, C_ACC, F_NUM, False, 0, w=200, h=16)
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
    m = mg(P, ctx, T, 12, time_limit=TL * _TS, status='연못 1/%d' % R, dim=70)
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
    info = m.T('스도쿠안내', ' ', BX, -66, 9, C_WHITE, F_BODY, True, 0, w=120, h=44)
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
    m = mg(P, ctx, T, 13, time_limit=TL * _TS, status='고도 0km', dim=40)
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
    warn = m.T('경고글', ' ', GX, 3, 9, C_RED, F_BODY, True, 0, w=110, h=13)
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


# ================================================================== 14. 땅따먹기 선긋기 (점과 상자)
@game(14)
def g14(P, ctx):
    TL, N, PI = 150, 5, 46
    CX, CY = -18, -14
    m = mg(P, ctx, T, 14, time_limit=TL * _TS, status='나 0 : 0 응원단장', dim=70)
    NB = (N - 1) * (N - 1)
    edges = []      # (세로?, x, y, 상자1, 상자2)
    for r in range(N):
        for c in range(N - 1):
            b1 = (r - 1) * (N - 1) + c + 1 if r > 0 else 0
            b2 = r * (N - 1) + c + 1 if r < N - 1 else 0
            edges.append((0, CX + (c - 1.5) * PI, CY + (2 - r) * PI, b1, b2))
    for r in range(N - 1):
        for c in range(N):
            b1 = r * (N - 1) + c if c > 0 else 0
            b2 = r * (N - 1) + c + 1 if c < N - 1 else 0
            edges.append((1, CX + (c - 2) * PI, CY + (1.5 - r) * PI, b1, b2))
    NE = len(edges)
    P.list('k14_ev', [e[0] for e in edges])
    P.list('k14_ex', [e[1] for e in edges])
    P.list('k14_ey', [e[2] for e in edges])
    P.list('k14_b1', [e[3] for e in edges])
    P.list('k14_b2', [e[4] for e in edges])
    P.list('k14_선', [0] * NE)
    P.list('k14_변', [0] * NB)
    P.list('k14_주인', [0] * NB)
    P.list('k14_bx', [CX + (c - 1.5) * PI for r in range(N - 1) for c in range(N - 1)])
    P.list('k14_by', [CY + (1.5 - r) * PI for r in range(N - 1) for c in range(N - 1)])
    vars_(P, 'k14_차례', 'k14_수', 'k14_내땅', 'k14_상대땅', 'k14_얻음', 'k14_최고', 'k14_최고수', 'k14_끝')
    panel(P, m.sc, '땅판', CX, CY, PI * (N - 1) + 40, PI * (N - 1) + 40, 'glass')
    # 상자 (주인 표시)
    box = m.S('땅', [('n', B3.k14_box(0)), ('me', B3.k14_box(1)), ('ai', B3.k14_box(2))], 0, -300, visible=False)
    for v_ in ('내번호', '복제'):
        box.local(v_, 0)
    box.on(on_scene(), setv('내번호', 0), rep(NB, chg('내번호', 1), clone_self()))
    box.on(on_clone(), setv('복제', 1), xy(LGET('k14_bx', V('내번호')), LGET('k14_by', V('내번호'))), shape('n'), show())
    box.on(on_msg('k14_땅'), if_(and_(eq(V('복제'), 1), gt(LGET('k14_주인', V('내번호')), 0)),
                                if_(ne(V('_ls'), LGET('k14_주인', V('내번호'))), setv('_ls', LGET('k14_주인', V('내번호'))),
                                    shape(add(1, V('_ls'))), box.pct(40), rep(6, box.grow_pct(10), wait(0.016)))))
    box.local('_ls', 0)
    box.on(on_clone(), setv('_ls', 0))
    m.S('점들', B3.k14_dots(N, PI), CX, CY)
    # 선 (40개 복제본)
    pics = [('h0', B3.k14_edge(0, 0)), ('h1', B3.k14_edge(0, 1)), ('h2', B3.k14_edge(0, 2)),
            ('v0', B3.k14_edge(1, 0)), ('v1', B3.k14_edge(1, 1)), ('v2', B3.k14_edge(1, 2))]
    ed = m.S('선', pics, 0, -300, visible=False)
    for v_ in ('내번호', '복제', '_a', '_b', '_s'):
        ed.local(v_, 0)
    me = V('내번호')
    mine = LGET('k14_선', me)
    ed.on(on_scene(), setv('내번호', 0), rep(NE, chg('내번호', 1), clone_self()))
    ed.on(on_clone(), setv('복제', 1), xy(LGET('k14_ex', me), LGET('k14_ey', me)), shape(add(1, mul(3, LGET('k14_ev', me)))), show())
    ed.on(on_click(), if_(and_(and_(eq(V('복제'), 1), eq(V('입력가능'), 1)), eq(mine, 0)),
                          setv('k14_수', me), setv('입력가능', 0)))
    ed.on(on_msg('k14_그음'), if_(and_(eq(V('복제'), 1), eq(me, V('k14_수'))),
                                 shape(add(add(1, mul(3, LGET('k14_ev', me))), mine)), to_front(),
                                 ed.pct(150), rep(5, ed.grow_pct(-10), wait(0.016))))
    # 응원단장 평가: 상자를 완성하는 선 > 안전한 선 > 상자를 내주는 선
    ed.on(on_msg('k14_평가'), if_(and_(eq(V('복제'), 1), eq(mine, 0)),
          setv('_a', 0), setv('_b', 0),
          if_(gt(LGET('k14_b1', me), 0), setv('_a', LGET('k14_변', LGET('k14_b1', me)))),
          if_(gt(LGET('k14_b2', me), 0), setv('_b', LGET('k14_변', LGET('k14_b2', me)))),
          ifelse(or_(eq(V('_a'), 3), eq(V('_b'), 3)), [setv('_s', 300)],
                 [ifelse(or_(eq(V('_a'), 2), eq(V('_b'), 2)), [setv('_s', 0)], [setv('_s', 100)])]),
          chg('_s', rnd(0, 99)),
          if_(gt(V('_s'), V('k14_최고')), setv('k14_최고', V('_s')), setv('k14_최고수', me))))
    # 양쪽 표시
    m.S('나얼굴', ctx['PORT']['me'], -200, 52, scale=1.3)
    m.T('나이름', '나', -200, 22, 10, C_ACC, F_NUM, False, 0, w=60, h=14)
    mys = m.T('나점수', '0', -200, 0, 22, C_WHITE, F_NUM, False, 0, w=60, h=26)
    mys.on(on_msg('k14_땅'), write(V('k14_내땅')))
    mys.on(on_scene(), write('0'))
    m.S('응원단장', B3.k14_cheer(), 196, 50)
    m.T('응원단장이름', '응원단장', 196, 4, 10, C_RED, F_NUM, False, 0, w=70, h=14)
    ais = m.T('응원단장점수', '0', 196, -18, 22, C_WHITE, F_NUM, False, 0, w=60, h=26)
    ais.on(on_msg('k14_땅'), write(V('k14_상대땅')))
    ais.on(on_scene(), write('0'))
    turn = m.T('차례글', ' ', CX, 96, 11, C_WHITE, F_BODY, True, 0, w=260, h=16)
    turn.on(on_msg('k14_차례'), ifelse(eq(V('k14_차례'), 1), [write('내 차례! 점 사이 선을 클릭하세요')], [write('응원단장이 고르는 중...')]))
    m.T('규칙글', '네모를 완성하면\n내 땅 + 한 번 더!', -200, -70, 9, C_DIM, F_BODY, True, 0, w=80, h=30)
    _pop(m, '한번더', K.big_text('한 번 더!', 26, 'royal'), CX, CY, 'k14_한번더', hold=0.3)
    res = m.S('결과', [('w', K.big_text('땅따먹기 승리!', 30, 'royal')), ('l', K.big_text('아쉽게 졌어요', 28, 'red')),
                     ('d', K.big_text('무승부!', 30, 'white'))], CX, CY, visible=False)
    res.on(on_scene(), hide())
    res.on(on_msg('k14_결과'), ifelse(gt(V('k14_내땅'), V('k14_상대땅')), [shape('w')],
                                      [ifelse(lt(V('k14_내땅'), V('k14_상대땅')), [shape('l')], [shape('d')])]),
           to_front(), res.pct(40), show(), rep(6, res.grow_pct(10), wait(0.016)))
    # 진행
    mgr = hidden(m, '땅담당')
    sv = V('k14_수')
    def claim(bexpr):
        return [lst_set('k14_변', bexpr, add(LGET('k14_변', bexpr), 1)),
                if_(eq(LGET('k14_변', bexpr), 4), lst_set('k14_주인', bexpr, V('k14_차례')), chg('k14_얻음', 1),
                    ifelse(eq(V('k14_차례'), 1), [chg('k14_내땅', 1)], [chg('k14_상대땅', 1)]))]
    score = add(mul(V('k14_내땅'), 6), mul(10, gt_num(V('k14_내땅'), V('k14_상대땅'))))
    mgr.on(on_msg('게임시작'), setv('k14_차례', 1),
           until(or_(eq(V('게임중'), 0), eq(V('k14_끝'), 1)),
                 cast('k14_차례'),
                 ifelse(eq(V('k14_차례'), 1),
                        [setv('입력가능', 1), wait_until(or_(eq(V('입력가능'), 0), eq(V('게임중'), 0)))],
                        [wait(0.6), setv('k14_최고', -1), setv('k14_최고수', 0), cast_wait('k14_평가')]),
                 setv('입력가능', 0),
                 if_(and_(eq(V('게임중'), 1), gt(sv, 0)),
                     lst_set('k14_선', sv, V('k14_차례')), setv('k14_얻음', 0),
                     if_(gt(LGET('k14_b1', sv), 0), *claim(LGET('k14_b1', sv))),
                     if_(gt(LGET('k14_b2', sv), 0), *claim(LGET('k14_b2', sv))),
                     cast('k14_그음'), cast('k14_땅'),
                     setv('미니표시', join('나 ', V('k14_내땅'), ' : ', V('k14_상대땅'), ' 응원단장')),
                     ifelse(gt(V('k14_얻음'), 0), [if_(eq(V('k14_차례'), 1), cast('k14_한번더'), wait(0.3))],
                            [setv('k14_차례', sub(3, V('k14_차례')))]),
                     if_(ge(add(V('k14_내땅'), V('k14_상대땅')), NB), setv('k14_끝', 1)))),
           if_(eq(V('게임중'), 1), wait(0.5), cast('k14_결과'), wait(1.6), *m.end_blocks(score)))
    mgr.on(on_msg('시간끝'), setv('입력가능', 0), setv('k14_끝', 1), *m.end_blocks(score))
    m.on_start(setv('k14_내땅', 0), setv('k14_상대땅', 0), setv('k14_차례', 0), setv('입력가능', 0), setv('k14_끝', 0),
               setv('k14_수', 0),
               *[lst_set('k14_선', i, 0) for i in range(1, NE + 1)], *[lst_set('k14_변', i, 0) for i in range(1, NB + 1)],
               *[lst_set('k14_주인', i, 0) for i in range(1, NB + 1)])
    m.snd('k14_그음', play('tick'))
    m.snd('k14_땅', if_(gt(V('k14_얻음'), 0), ifelse(eq(V('k14_차례'), 1), [play('coin')], [play('bad')])))
    m.snd('k14_결과', ifelse(gt(V('k14_내땅'), V('k14_상대땅')), [play('fanfare')], [play('fail_big')]))
    m.finish('응원단장과 번갈아 점 사이에 선을 그어요. 네모의 마지막\n변을 그으면 내 땅 + 한 번 더! 땅 16칸 중 많이 차지하세요.',
             '조작: 점 사이 선 클릭  ·  세 변이 그어진 네모를 상대에게 넘겨주지 않게 조심!')
    return True


def gt_num(a, b):
    """정수 a > b 이면 1, 아니면 0 (숫자 계산으로)."""
    d = sub(a, b)
    mm = div(add(abs_(d), d), 2)
    return div(sub(add(mm, 1), abs_(sub(mm, 1))), 2)


# ================================================================== 15. 물통 나누기
@game(15)
def g15(P, ctx):
    TL, U = 100, B3.U15
    ROUNDS = [(3, 5, 4, 6), (4, 9, 6, 8), (5, 7, 6, 10)]
    R = len(ROUNDS)
    m = mg(P, ctx, T, 15, time_limit=TL * _TS, status='물통 1/%d' % R, dim=70)
    P.list('k15_통', [x for r in ROUNDS for x in r])
    vars_(P, 'k15_a', 'k15_b', 'k15_ca', 'k15_cb', 'k15_목표', 'k15_최소', 'k15_횟수', 'k15_양', 'k15_동작', 'k15_얻음')
    caps = sorted({c for r in ROUNDS for c in r[:2]})

    def cap_shape(cv):
        return [if_(eq(cv, c), shape('c%d' % c)) for c in caps]
    YB = -120
    JX = [-150, 20]
    for j, nm in enumerate(('a', 'b')):
        cv, lv = V('k15_c' + nm), V('k15_' + nm)
        wa = m.S('물%s' % nm, [('c%d' % c, B3.k15_water(c)) for c in caps], JX[j], -300)
        wa.on(on_msg('k15_물'), *cap_shape(cv), ly(sub(add(YB, mul(lv, U)), div(mul(cv, U), 2))))
        jug = m.S('물통%s' % nm, [('c%d' % c, B3.k15_jug(c)) for c in caps], JX[j], -200)
        jug.on(on_msg('k15_새판'), *cap_shape(cv), ly(add(YB - 14, div(add(mul(cv, U), 16), 2))))
        lab = m.T('양글%s' % nm, ' ', JX[j], 0, 11, C_WHITE, F_NUM, False, 0, w=90, h=16)
        lab.on(on_msg('k15_물'), write(join(round1(lv), 'L / ', cv, 'L')), ly(add(YB + 14, mul(cv, U))))
        bx = JX[j] + 72
        other = 'b' if nm == 'a' else 'a'
        for k, (txt, col, act) in enumerate((('채우기', 'royal', 1), ('비우기', 'steel', 2), ('붓기 →' if nm == 'a' else '← 붓기', 'green', 3))):
            button(P, m.sc, 'k15%s%d' % (nm, k), txt, bx, -40 - 30 * k, 70, 26, col,
                   actions=[if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)), setv('k15_동작', act + (0 if nm == 'a' else 3)),
                                setv('입력가능', 0))])
    stream = m.S('물줄기', B3.k15_stream(), -60, -40, visible=False)
    stream.on(on_scene(), hide())
    goal = m.T('목표글', ' ', 0, 84, 13, C_WHITE, F_NUM, False, 0, w=360, h=20)
    goal.on(on_msg('k15_새판'), write(join('목표: 한 물통에 정확히 ', V('k15_목표'), 'L!')))
    cnt = m.T('횟수글', ' ', 0, 64, 10, C_ACC, F_BODY, True, 0, w=360, h=15)
    cnt.on(on_msg('k15_물'), write(join('옮긴 횟수 ', V('k15_횟수'), '  ·  최소 ', V('k15_최소'), '번이면 만점')))
    button(P, m.sc, 'k15다시', '처음 상태로', 190, 40, 86, 24, 'steel',
           actions=[if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)), setv('k15_동작', 7), setv('입력가능', 0))])
    _pop(m, '성공글', K.big_text('정확히 맞췄어요!', 28, 'royal'), 0, 30, 'k15_성공', hold=0.7)
    pts = m.T('라운드점수', ' ', 0, 6, 12, C_ACC, F_NUM, False, 0, w=200, h=18, visible=False)
    pts.on(on_msg('k15_성공'), write(join('+', V('k15_얻음'), '점')), show(), wait(1.1), hide())
    # 진행: 동작 1~3 = A 채우기/비우기/A→B, 4~6 = B, 7 = 처음으로
    a, b, ca, cb = V('k15_a'), V('k15_b'), V('k15_ca'), V('k15_cb')
    def anim(to_a, to_b, sx=None):
        """a, b 를 목표값으로 12단계에 걸쳐 바꾸기 (물 높이 애니메이션)."""
        return [setv('_ma', div(sub(to_a, a), 12)), setv('_mb', div(sub(to_b, b), 12)), setv('_mx', to_a), setv('_my', to_b),
                rep(12, chg('k15_a', V('_ma')), chg('k15_b', V('_mb')), cast('k15_물'), wait(0.025)),
                setv('k15_a', V('_mx')), setv('k15_b', V('_my')), cast('k15_물')]
    mgr = hidden(m, '물통담당')
    pour_ab = [setv('k15_양', b), setv('_mk', sub(cb, b)), if_(lt(a, V('_mk')), setv('_mk', a))]
    pour_ba = [setv('_mk', sub(ca, a)), if_(lt(b, V('_mk')), setv('_mk', b))]
    new_round = [setv('_mi', mul(sub(V('라운드'), 1), 4)), setv('k15_ca', LGET('k15_통', add(V('_mi'), 1))),
                 setv('k15_cb', LGET('k15_통', add(V('_mi'), 2))), setv('k15_목표', LGET('k15_통', add(V('_mi'), 3))),
                 setv('k15_최소', LGET('k15_통', add(V('_mi'), 4))), setv('k15_a', 0), setv('k15_b', 0), setv('k15_횟수', 0),
                 cast('k15_새판'), cast('k15_물'), setv('미니표시', join('물통 ', V('라운드'), '/%d · ' % R, rounded(V('합계')), '점')),
                 setv('입력가능', 1)]
    mgr.on(on_msg('게임시작'), setv('라운드', 1), *new_round)
    mgr.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
           wait_until(or_(eq(V('입력가능'), 0), eq(V('게임중'), 0))),
           if_(and_(eq(V('게임중'), 1), gt(V('k15_동작'), 0)),
               setv('_mv', V('k15_동작')), setv('k15_동작', 0),
               if_(eq(V('_mv'), 1), *anim(ca, b)), if_(eq(V('_mv'), 2), *anim(0, b)),
               if_(eq(V('_mv'), 4), *anim(a, cb)), if_(eq(V('_mv'), 5), *anim(a, 0)),
               if_(eq(V('_mv'), 3), *pour_ab, setv('_mt', 1), cast('k15_붓기'), *anim(sub(a, V('_mk')), add(b, V('_mk')))),
               if_(eq(V('_mv'), 6), *pour_ba, setv('_mt', 2), cast('k15_붓기'), *anim(add(a, V('_mk')), sub(b, V('_mk')))),
               cast('k15_붓기끝'),
               ifelse(eq(V('_mv'), 7), [*anim(0, 0)], [chg('k15_횟수', 1)]),
               cast('k15_물'),
               if_(or_(eq(a, V('k15_목표')), eq(b, V('k15_목표'))),
                   setv('k15_얻음', sub(33, mul(4, sub(V('k15_횟수'), V('k15_최소'))))), if_(lt(V('k15_얻음'), 8), setv('k15_얻음', 8)),
                   chg('합계', V('k15_얻음')), chg('맞춤', 1), cast('k15_성공'), wait(1.6), chg('라운드', 1),
                   ifelse(gt(V('라운드'), R), [*m.end_blocks(add(V('합계'), mul(V('남은시간'), 0.12)))], new_round)),
               if_(eq(V('게임중'), 1), setv('입력가능', 1)))))
    stream.on(on_msg('k15_붓기'), ifelse(eq(V('_mt'), 1), [lx(JX[1]), ly(add(YB + 40, mul(cb, U)))],
                                         [lx(JX[0]), ly(add(YB + 40, mul(ca, U)))]), show())
    stream.on(on_msg('k15_붓기끝'), hide())
    mgr.on(on_msg('시간끝'), setv('입력가능', 0), *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('입력가능', 0), setv('k15_동작', 0), setv('k15_a', 0), setv('k15_b', 0),
               setv('k15_ca', 3), setv('k15_cb', 5))
    m.snd('k15_붓기', play('splash'))
    m.snd('k15_성공', play('fanfare'))
    m.finish('두 물통의 채우기·비우기·붓기만으로 한 물통에 정확히\n목표만큼 물을 담으세요! 적게 옮길수록 점수 UP (3문제)',
             '조작: 물통 옆 단추 클릭  ·  붓기 = 다른 물통이 가득 차거나 내 물통이 빌 때까지')
    return True


# ================================================================== 16. 패러글라이딩 착지 (위에서 본 조종)
@game(16)
def g16(P, ctx):
    FX, FY = 0, -12
    FL = [  # 출발 x, y, 방향, 목표 x, y, 상승기류 x, y
        (-140, -90, 45, 60, 40, -40, 50),
        (140, 70, 225, -80, -50, 50, -60),
        (-135, 72, 120, 95, -70, 0, -5)]
    R = len(FL)
    m = mg(P, ctx, T, 16, status='비행 1/%d' % R, dim=60)
    P.list('k16_비행', [x for f in FL for x in f])
    vars_(P, 'k16_x', 'k16_y', 'k16_각', 'k16_고도', 'k16_풍향', 'k16_풍속', 'k16_tx', 'k16_ty', 'k16_hx', 'k16_hy', 'k16_t',
          'k16_dt', 'k16_거리', 'k16_얻음', 'k16_비행중', 'k16_바람t', 'k16_목풍향')
    x, y, alt = V('k16_x'), V('k16_y'), V('k16_고도')
    m.S('들판', B3.k16_field(), FX, FY)
    tgt = m.S('착지점', B3.k16_target(), 0, 0)
    tgt.on(on_msg('k16_새비행'), xy(V('k16_tx'), V('k16_ty')))
    th = m.S('상승기류', B3.k16_thermal(), 0, 0)
    th.on(on_msg('k16_새비행'), xy(V('k16_hx'), V('k16_hy')))
    th.on(on_msg('게임시작'), until(eq(V('게임중'), 0), rot_by(2), wait(0.03)))
    shadow = m.S('그림자', B3.k16_glider(True), 0, -300)
    gl = m.S('글라이더', B3.k16_glider(), 0, -300)
    gl.on(on_msg('k16_그리기'), xy(x, add(y, mul(alt, 0.45))), rot(V('k16_각')), gl.pct(add(90, mul(alt, 0.5))))
    shadow.on(on_msg('k16_그리기'), xy(x, y), rot(V('k16_각')))
    # 오른쪽 계기
    panel(P, m.sc, '계기판', 207, 20, 58, 150, 'glass')
    m.T('바람이름', '바람', 207, 82, 9, C_DIM, F_BODY, True, 0, w=50, h=12)
    wind = m.S('바람표', B3.k16_wind(), 207, 58)
    wind.on(on_msg('k16_그리기'), rot(V('k16_풍향')))
    wt = m.T('바람글', ' ', 207, 33, 9, C_WHITE, F_NUM, False, 0, w=56, h=12)
    wt.on(on_msg('k16_새비행'), until(eq(V('k16_비행중'), 0), write(join(rounded(V('k16_풍속')), 'm/s')), wait(0.3)))
    m.T('고도이름', '고도', 207, 12, 9, C_DIM, F_BODY, True, 0, w=50, h=12)
    at = m.T('고도글', ' ', 207, -6, 14, C_ACC, F_NUM, False, 0, w=56, h=18)
    at.on(on_msg('k16_새비행'), until(eq(V('k16_비행중'), 0), write(join(ceil_(alt), 'm')), wait(0.1)), write('0m'))
    m.T('거리이름', '거리', 207, -28, 9, C_DIM, F_BODY, True, 0, w=50, h=12)
    dt_ = m.T('거리글', ' ', 207, -46, 12, C_WHITE, F_NUM, False, 0, w=56, h=18)
    dt_.on(on_msg('k16_새비행'), until(eq(V('k16_비행중'), 0), write(join(rounded(V('k16_거리')), 'm')), wait(0.15)))
    land = m.T('착지글', ' ', FX, 70, 16, C_WHITE, F_NUM, False, 0, w=300, h=24, visible=False)
    land.on(on_msg('k16_착지'), write(join('착지! 목표에서 ', rounded(V('k16_거리')), 'm  +', rounded(V('k16_얻음')), '점')), show(),
            wait(1.6), hide())
    # 비행 물리 (시간 기준)
    dist = fn('root', add(mul(sub(x, V('k16_tx')), sub(x, V('k16_tx'))), mul(sub(y, V('k16_ty')), sub(y, V('k16_ty')))))
    in_th = lt(add(mul(sub(x, V('k16_hx')), sub(x, V('k16_hx'))), mul(sub(y, V('k16_hy')), sub(y, V('k16_hy')))), 28 * 28)
    mgr = hidden(m, '비행담당')
    fi = lambda k: LGET('k16_비행', add(mul(sub(V('라운드'), 1), 7), k))
    mgr.on(on_msg('게임시작'), setv('라운드', 1),
           until(or_(gt(V('라운드'), R), eq(V('게임중'), 0)),
                 setv('k16_x', fi(1)), setv('k16_y', fi(2)), setv('k16_각', fi(3)), setv('k16_tx', fi(4)), setv('k16_ty', fi(5)),
                 setv('k16_hx', fi(6)), setv('k16_hy', fi(7)), setv('k16_고도', 70),
                 setv('k16_풍향', rnd(0, 359)), setv('k16_목풍향', V('k16_풍향')), setv('k16_풍속', add(4, mul(V('라운드'), 3))),
                 setv('k16_거리', dist), setv('k16_비행중', 1), cast('k16_새비행'), cast('k16_그리기'),
                 setv('미니표시', join('비행 ', V('라운드'), '/%d · ' % R, rounded(V('합계')), '점')),
                 setv('k16_t', timer()), setv('k16_바람t', add(timer(), 3)),
                 until(or_(le(alt, 0), eq(V('게임중'), 0)),
                       setv('k16_dt', sub(timer(), V('k16_t'))), setv('k16_t', timer()), if_(gt(V('k16_dt'), 0.1), setv('k16_dt', 0.1)),
                       if_(key(K_LEFT), chg('k16_각', mul(-120, V('k16_dt')))),
                       if_(key(K_RIGHT), chg('k16_각', mul(120, V('k16_dt')))),
                       if_(gt(timer(), V('k16_바람t')), setv('k16_바람t', add(timer(), 3)),
                           setv('k16_목풍향', add(V('k16_풍향'), rnd(-60, 60)))),
                       chg('k16_풍향', mul(sub(V('k16_목풍향'), V('k16_풍향')), mul(V('k16_dt'), 0.8))),
                       chg('k16_x', mul(add(mul(sin_(V('k16_각')), 26), mul(sin_(V('k16_풍향')), V('k16_풍속'))), V('k16_dt'))),
                       chg('k16_y', mul(add(mul(cos_(V('k16_각')), 26), mul(cos_(V('k16_풍향')), V('k16_풍속'))), V('k16_dt'))),
                       if_(lt(x, -160), setv('k16_x', -160)), if_(gt(x, 160), setv('k16_x', 160)),
                       if_(lt(y, -114), setv('k16_y', -114)), if_(gt(y, 88), setv('k16_y', 88)),
                       ifelse(in_th, [chg('k16_고도', mul(4, V('k16_dt')))], [chg('k16_고도', mul(-5.5, V('k16_dt')))]),
                       if_(gt(alt, 95), setv('k16_고도', 95)),
                       setv('k16_거리', dist), cast('k16_그리기')),
                 setv('k16_비행중', 0), setv('k16_고도', 0), cast('k16_그리기'),
                 if_(eq(V('게임중'), 1),
                     setv('k16_얻음', sub(34, mul(V('k16_거리'), 0.34))), if_(lt(V('k16_얻음'), 0), setv('k16_얻음', 0)),
                     chg('합계', V('k16_얻음')), cast('k16_착지'), wait(2.0)),
                 chg('라운드', 1)),
           *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('k16_비행중', 0), setv('k16_고도', 0))
    m.snd('k16_착지', ifelse(gt(V('k16_얻음'), 22), [play('fanfare')], [ifelse(gt(V('k16_얻음'), 8), [play('good')], [play('bad')])]))
    m.snd('k16_새비행', play('whistle'))
    m.finish('패러글라이더가 천천히 내려가요. 바람에 밀리니 방향을 잘\n잡아 고도 0m 일 때 과녁 한가운데 내리세요! (3번 비행)',
             '조작: ← → 방향 돌리기  ·  너무 높으면 빙글빙글 돌며 고도를 낮추고, 주황 기류에선 위로 떠요')
    return True


# ================================================================== 17. 드론 대형 기억 (변화 찾기)
@game(17)
def g17(P, ctx):
    NS = [8, 10, 11, 12, 14, 16]
    R = len(NS)
    COLS, ROWS = 11, 5
    P.list('k17_sx', [-180 + 36 * c for r in range(ROWS) for c in range(COLS)])
    P.list('k17_sy', [86 - 26 * r for r in range(ROWS) for c in range(COLS)])
    P.list('k17_자리', [])
    P.list('k17_색', [])
    m = mg(P, ctx, T, 17, status='대형 1/%d' % R, dim=100)
    vars_(P, 'k17_종류', 'k17_ax1', 'k17_ay1', 'k17_ax2', 'k17_ay2', 'k17_빈', 'k17_t0', 'k17_얻음', 'k17_n')
    NSL = COLS * ROWS
    dr = m.S('드론', [('c%d' % k, B3.k17_drone(k)) for k in range(1, 5)], 0, -300, visible=False)
    for v_ in ('내번호', '복제'):
        dr.local(v_, 0)
    me = V('내번호')
    dr.on(on_scene(), setv('내번호', 0), rep(max(NS) + 1, chg('내번호', 1), clone_self()))
    dr.on(on_clone(), setv('복제', 1), hide())
    dr.on(on_msg('k17_켜기'), if_(eq(V('복제'), 1),
                               ifelse(le(me, LLEN('k17_자리')),
                                      [xy(LGET('k17_sx', LGET('k17_자리', me)), LGET('k17_sy', LGET('k17_자리', me))),
                                       shape(LGET('k17_색', me)), dr.pct(30), show(), rep(5, dr.grow_pct(14), wait(0.016))],
                                      [hide()])))
    dr.on(on_msg('k17_끄기'), if_(eq(V('복제'), 1), hide()))
    ring1 = m.S('정답테', A3.ring('k17_ring', 16, (255, 240, 120), 2.5), 0, -300, visible=False)
    ring2 = m.S('옛자리테', A3.ring('k17_ring2', 16, (160, 200, 255), 2), 0, -300, visible=False)
    ring1.on(on_msg('k17_공개'), xy(V('k17_ax1'), V('k17_ay1')), show(), rep(3, ring1.grow_pct(15), wait(0.05), ring1.grow_pct(-15), wait(0.05)))
    ring2.on(on_msg('k17_공개'), if_(eq(V('k17_종류'), 1), xy(V('k17_ax2'), V('k17_ay2')), show()))
    for r_ in (ring1, ring2):
        r_.on(on_msg('k17_끄기'), hide())
    msg = m.T('안내', ' ', 0, -60, 13, C_WHITE, F_BODY, True, 0, w=360, h=20)
    msg.on(on_msg('k17_안내'), write(V('_mt')))
    kind_t = m.T('정답설명', ' ', 0, -84, 10, C_ACC, F_BODY, True, 0, w=360, h=16)
    kind_t.on(on_msg('k17_공개'), ifelse(eq(V('k17_종류'), 1), [write('자리를 옮긴 드론 (파란 테 = 원래 자리)')],
                                        [ifelse(eq(V('k17_종류'), 2), [write('새로 나타난 드론')],
                                                [ifelse(eq(V('k17_종류'), 3), [write('사라진 드론 자리')], [write('색이 바뀐 드론')])])]))
    kind_t.on(on_msg('k17_끄기'), write(''))
    judge = m.S('판정', [('ok', K.big_text('찾았다!', 30, 'green')), ('no', K.big_text('아니에요!', 28, 'red'))], 0, -104, visible=False)
    judge.on(on_msg('k17_판정'), shape(V('k17_얻음')), judge.pct(50), show(), rep(5, judge.grow_pct(10), wait(0.016)), wait(1.0), hide())
    pick_empty = [setv('k17_빈', rnd(1, NSL)), until(not_(lst_has('k17_자리', V('k17_빈'))), setv('k17_빈', rnd(1, NSL)))]
    pos = lambda i: [LGET('k17_sx', LGET('k17_자리', i)), LGET('k17_sy', LGET('k17_자리', i))]
    mgr = hidden(m, '드론담당')
    say_ = lambda t: [setv('_mt', t), cast('k17_안내')]
    mgr.on(on_msg('게임시작'), setv('라운드', 1),
           until(or_(gt(V('라운드'), R), eq(V('게임중'), 0)),
                 setv('k17_n', LGET('k17_개수', V('라운드'))),
                 until(eq(LLEN('k17_자리'), 0), lst_del('k17_자리', 1), lst_del('k17_색', 1)),
                 until(ge(LLEN('k17_자리'), V('k17_n')), *pick_empty, lst_add('k17_자리', V('k17_빈')), lst_add('k17_색', rnd(1, 4))),
                 setv('미니표시', join('대형 ', V('라운드'), '/%d · ' % R, rounded(V('합계')), '점')),
                 *say_('드론 대형을 잘 기억하세요!'), cast('k17_켜기'), wait(add(2.6, mul(V('라운드'), 0.15))),
                 cast('k17_끄기'), *say_('...'), wait(1.1),
                 setv('k17_종류', rnd(1, 4)), setv('_mi', rnd(1, V('k17_n'))),
                 if_(eq(V('k17_종류'), 1), setv('k17_ax2', pos(V('_mi'))[0]), setv('k17_ay2', pos(V('_mi'))[1]), *pick_empty,
                     lst_set('k17_자리', V('_mi'), V('k17_빈')), setv('k17_ax1', pos(V('_mi'))[0]), setv('k17_ay1', pos(V('_mi'))[1])),
                 if_(eq(V('k17_종류'), 2), *pick_empty, lst_add('k17_자리', V('k17_빈')), lst_add('k17_색', rnd(1, 4)),
                     setv('k17_ax1', pos(LLEN('k17_자리'))[0]), setv('k17_ay1', pos(LLEN('k17_자리'))[1])),
                 if_(eq(V('k17_종류'), 3), setv('k17_ax1', pos(V('_mi'))[0]), setv('k17_ay1', pos(V('_mi'))[1]),
                     lst_del('k17_자리', V('_mi')), lst_del('k17_색', V('_mi'))),
                 if_(eq(V('k17_종류'), 4), setv('k17_ax1', pos(V('_mi'))[0]), setv('k17_ay1', pos(V('_mi'))[1]),
                     lst_set('k17_색', V('_mi'), add(mod(LGET('k17_색', V('_mi')), 4), 1))),
                 if_(ne(V('k17_종류'), 1), setv('k17_ax2', V('k17_ax1')), setv('k17_ay2', V('k17_ay1'))),
                 cast('k17_켜기'), *say_('무엇이 바뀌었을까요? 그 드론(자리)을 클릭!'),
                 setv('k17_t0', timer()), setv('선택', 0), setv('입력가능', 1),
                 wait_until(or_(eq(V('입력가능'), 0), gt(timer(), add(V('k17_t0'), 12)), eq(V('게임중'), 0))),
                 setv('입력가능', 0),
                 ifelse(eq(V('선택'), 1),
                        [setv('k17_얻음', 1), chg('맞춤', 1), chg('합계', 14),
                         if_(lt(sub(timer(), V('k17_t0')), 6), chg('합계', mul(sub(6, sub(timer(), V('k17_t0'))), 0.5)))],
                        [setv('k17_얻음', 2)]),
                 cast('k17_판정'), cast('k17_공개'), *say_(''), wait(1.8), cast('k17_끄기'), wait(0.3),
                 chg('라운드', 1)),
           *m.end_blocks(V('합계')))
    near = lambda ax, ay: lt(add(mul(sub(mouse_x(), V(ax)), sub(mouse_x(), V(ax))), mul(sub(mouse_y(), V(ay)), sub(mouse_y(), V(ay)))), 17 * 17)
    mgr.on(on_mouse_down(), if_(and_(eq(V('게임중'), 1), eq(V('입력가능'), 1)),
                                ifelse(or_(near('k17_ax1', 'k17_ay1'), near('k17_ax2', 'k17_ay2')), [setv('선택', 1)], [setv('선택', 2)]),
                                setv('입력가능', 0)))
    P.list('k17_개수', NS)
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('입력가능', 0))
    m.snd('k17_판정', ifelse(eq(V('k17_얻음'), 1), [play('good')], [play('bad')]))
    m.snd('k17_켜기', play('pop'))
    m.finish('광안리 밤하늘의 드론 대형을 잘 보세요. 잠깐 꺼졌다 켜지면\n드론 하나가 옮겨지거나 생기거나 사라지거나 색이 바뀌어요!',
             '조작: 바뀐 드론(사라졌으면 그 빈자리)을 마우스로 클릭  ·  6라운드, 점점 많아져요')
    return True


# ================================================================== 18. 리버시 (6×6)
@game(18)
def g18(P, ctx):
    import mg_art2 as A2
    TL, N, PI = 150, 6, 34
    CX, CY = -16, -18
    DIRS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    m = mg(P, ctx, T, 18, time_limit=TL * _TS, status='흑 2 : 2 백', dim=70)
    init = [0] * 36
    init[2 * 6 + 2] = init[3 * 6 + 3] = 2
    init[2 * 6 + 3] = init[3 * 6 + 2] = 1
    lens = []
    for i in range(36):
        r, c = divmod(i, 6)
        for dr_, dc in DIRS:
            L = 0
            rr, cc = r + dr_, c + dc
            while 0 <= rr < 6 and 0 <= cc < 6:
                L += 1
                rr += dr_
                cc += dc
            lens.append(L)
    val = []
    for i in range(36):
        r, c = divmod(i, 6)
        e = (r in (0, 5)) + (c in (0, 5))
        v = 100 if e == 2 else (12 if e == 1 else 0)
        if (r in (1, 4)) and (c in (1, 4)):
            v = -40
        if e == 1 and ((r in (0, 5) and c in (1, 4)) or (c in (0, 5) and r in (1, 4))):
            v = -10
        val.append(v)
    P.list('k18_판', init)
    P.list('k18_길이', lens)
    P.list('k18_가치', val)
    P.list('k18_x', [CX + (c - 2.5) * PI for r in range(6) for c in range(6)])
    P.list('k18_y', [CY + (2.5 - r) * PI for r in range(6) for c in range(6)])
    vars_(P, 'k18_누구', 'k18_가능', 'k18_최고', 'k18_수', 'k18_흑', 'k18_백', 'k18_패스', 'k18_끝', 'k18_뒤집', 'k18_차례글')
    m.S('판', B3.k18_board(N, PI), CX, CY)
    sc_ = 0.62
    cell = m.S('돌', [('e', A2.go_stone('e')), ('b', A2.go_stone('b')), ('w', A2.go_stone('w')), ('h', B3.k18_hint())],
               0, -300, scale=sc_, visible=False)
    locs = ['내번호', '복제', '_t', '_s', '_ls'] + ['f%d' % d for d in range(8)] + ['L%d' % d for d in range(8)]
    for v_ in locs:
        cell.local(v_, 0)
    me = V('내번호')
    M, O = V('k18_누구'), sub(3, V('k18_누구'))
    cell.on(on_scene(), setv('내번호', 0), rep(36, chg('내번호', 1), clone_self()))
    cell.on(on_clone(), setv('복제', 1), setv('_ls', -1), xy(LGET('k18_x', me), LGET('k18_y', me)),
            *[setv('L%d' % d, LGET('k18_길이', add(mul(sub(me, 1), 8), d + 1))) for d in range(8)], show())

    def ray(d, k):
        """d 방향으로 1..k-1 칸이 상대 돌임을 확인한 뒤, k 번째 칸 검사."""
        dr_, dc = DIRS[d]
        delta = dr_ * 6 + dc
        c = LGET('k18_판', add(me, k * delta))
        nxt = [if_(eq(c, O), if_(ge(V('L%d' % d), k + 1), ray(d, k + 1)))] if k < 5 else []
        return ifelse(eq(c, M), [setv('f%d' % d, k - 1)], nxt)

    def first(d):
        dr_, dc = DIRS[d]
        delta = dr_ * 6 + dc
        return if_(ge(V('L%d' % d), 2), if_(eq(LGET('k18_판', add(me, delta)), O), ray(d, 2)))
    cell.on(on_msg('k18_평가'), if_(eq(V('복제'), 1),
            *[setv('f%d' % d, 0) for d in range(8)], setv('_t', 0),
            if_(eq(LGET('k18_판', me), 0), *[first(d) for d in range(8)],
                setv('_t', add(*[V('f%d' % d) for d in range(8)]))),
            if_(gt(V('_t'), 0), chg('k18_가능', 1),
                setv('_s', add(add(mul(V('_t'), 10), LGET('k18_가치', me)), rnd(0, 9))),
                if_(gt(V('_s'), V('k18_최고')), setv('k18_최고', V('_s')), setv('k18_수', me)))))

    def flips(d):
        dr_, dc = DIRS[d]
        delta = dr_ * 6 + dc
        return [if_(ge(V('f%d' % d), k), lst_set('k18_판', add(me, k * delta), M)) for k in range(1, 5)]
    cell.on(on_msg('k18_놓기'), if_(and_(eq(V('복제'), 1), eq(me, V('k18_수'))),
                                   setv('k18_뒤집', V('_t')), lst_set('k18_판', me, M), *[b for d in range(8) for b in flips(d)]))
    st = LGET('k18_판', me)
    cell.on(on_msg('k18_그리기'), if_(eq(V('복제'), 1),
            if_(eq(st, 1), chg('k18_흑', 1)), if_(eq(st, 2), chg('k18_백', 1)),
            ifelse(eq(st, 0), [ifelse(and_(and_(eq(V('k18_누구'), 1), gt(V('_t'), 0)), eq(V('입력가능'), 1)), [shape('h')], [shape('e')]),
                               setv('_ls', 0)],
                   [if_(ne(st, V('_ls')),
                        ifelse(eq(V('_ls'), 0), [shape(add(1, st)), cell.pct(140), rep(4, cell.grow_pct(-10), wait(0.016))],
                               [rep(4, cell.grow_pct(-22), wait(0.016)), shape(add(1, st)), rep(4, cell.grow_pct(22), wait(0.016))]),
                        setv('_ls', st))])))
    cell.on(on_click(), if_(and_(and_(eq(V('복제'), 1), eq(V('입력가능'), 1)), and_(eq(st, 0), gt(V('_t'), 0))),
                            setv('k18_수', me), setv('입력가능', 0)))
    # 양쪽
    m.S('나얼굴', ctx['PORT']['me'], -196, 56, scale=1.3)
    m.T('나이름', '나 (흑)', -196, 26, 10, C_ACC, F_NUM, False, 0, w=70, h=14)
    bt = m.T('흑수', '2', -196, 4, 22, C_WHITE, F_NUM, False, 0, w=60, h=26)
    bt.on(on_msg('k18_세기'), write(V('k18_흑')))
    bt.on(on_scene(), write('2'))
    m.rival('상대', '1', 192, 48, scale=0.5)
    m.T('상대이름', '상대 후보 (백)', 192, 4, 10, C_RED, F_NUM, False, 0, w=90, h=14)
    wt = m.T('백수', '2', 192, -18, 22, C_WHITE, F_NUM, False, 0, w=60, h=26)
    wt.on(on_msg('k18_세기'), write(V('k18_백')))
    wt.on(on_scene(), write('2'))
    turn = m.T('차례글', ' ', CX, 98, 11, C_WHITE, F_BODY, True, 0, w=280, h=16)
    turn.on(on_msg('k18_차례'), ifelse(eq(V('k18_누구'), 1), [write('내 차례! 점 표시된 칸에 놓으세요')], [write('상대 후보가 생각 중...')]))
    _pop(m, '패스글', K.big_text('둘 곳이 없어 패스!', 24, 'white'), CX, CY, 'k18_패스', hold=0.6)
    res = m.S('결과', [('w', K.big_text('리버시 승리!', 32, 'royal')), ('l', K.big_text('아쉽게 졌어요', 28, 'red')),
                     ('d', K.big_text('무승부!', 30, 'white'))], CX, CY, visible=False)
    res.on(on_scene(), hide())
    res.on(on_msg('k18_결과'), ifelse(gt(V('k18_흑'), V('k18_백')), [shape('w')],
                                      [ifelse(lt(V('k18_흑'), V('k18_백')), [shape('l')], [shape('d')])]),
           to_front(), res.pct(40), show(), rep(6, res.grow_pct(10), wait(0.016)))
    # 진행
    count = [setv('k18_흑', 0), setv('k18_백', 0), cast_wait('k18_그리기'), cast('k18_세기'),
             setv('미니표시', join('흑 ', V('k18_흑'), ' : ', V('k18_백'), ' 백'))]
    score = add(add(15, mul(25, gt_num(V('k18_흑'), V('k18_백'))), mul(18, gt_num(add(V('k18_흑'), 1), V('k18_백')))),
                mul(V('k18_흑'), 1.2))
    mgr = hidden(m, '리버시담당')
    mgr.on(on_msg('게임시작'), setv('k18_누구', 1), setv('k18_패스', 0), *count,
           until(or_(eq(V('게임중'), 0), eq(V('k18_끝'), 1)),
                 setv('k18_가능', 0), setv('k18_최고', -999), setv('k18_수', 0), cast_wait('k18_평가'),
                 ifelse(eq(V('k18_가능'), 0),
                        [chg('k18_패스', 1), ifelse(ge(V('k18_패스'), 2), [setv('k18_끝', 1)],
                                                    [cast('k18_패스'), wait(1.0), setv('k18_누구', sub(3, V('k18_누구')))])],
                        [setv('k18_패스', 0), cast('k18_차례'),
                         ifelse(eq(V('k18_누구'), 1),
                                [setv('입력가능', 1), cast_wait('k18_그리기'),
                                 wait_until(or_(eq(V('입력가능'), 0), eq(V('게임중'), 0)))],
                                [wait(0.8)]),
                         setv('입력가능', 0),
                         if_(eq(V('게임중'), 1),
                             cast_wait('k18_놓기'), cast('k18_놓음'), *count,
                             if_(ge(add(V('k18_흑'), V('k18_백')), 36), setv('k18_끝', 1)),
                             setv('k18_누구', sub(3, V('k18_누구'))), wait(0.25))])),
           if_(eq(V('게임중'), 1), setv('입력가능', 0), *count, cast('k18_결과'), wait(1.8), *m.end_blocks(score)))
    mgr.on(on_msg('시간끝'), setv('입력가능', 0), setv('k18_끝', 1), *m.end_blocks(score))
    m.on_start(setv('입력가능', 0), setv('k18_끝', 0), setv('k18_누구', 1), *[lst_set('k18_판', i + 1, init[i]) for i in range(36)])
    m.snd('k18_놓음', play('stamp'))
    m.snd('k18_패스', play('beep'))
    m.snd('k18_결과', ifelse(gt(V('k18_흑'), V('k18_백')), [play('fanfare')], [play('fail_big')]))
    m.finish('상대 돌을 내 돌 사이에 끼우면 모두 내 색으로 뒤집혀요.\n판이 다 차면 돌이 많은 쪽이 승리! 나는 흑돌, 먼저 둬요.',
             '조작: 점(•) 표시된 칸 클릭  ·  모서리를 차지하면 유리해요')
    return True


# ================================================================== 19. 수문장 교대식 (한 박자 / 두 박자 늦게 따라 하기)
@game(19)
def g19(P, ctx):
    PH = [(1, 12, 1.5), (2, 12, 1.65)]     # (몇 박자 전, 박자 수, 박자 길이)
    NANS = sum(n - b for b, n, _ in PH)
    m = mg(P, ctx, T, 19, status='0/%d' % NANS, dim=60)
    P.list('k19_순서', [])
    vars_(P, 'k19_n', 'k19_뒤', 'k19_답', 'k19_눌림', 'k19_얻음', 'k19_박', 'k19_동작')
    guard = m.S('수문장', [('idle', B3.k19_guard('idle')), ('left', B3.k19_guard('left')), ('up', B3.k19_guard('up')),
                         ('right', B3.k19_guard('right')), ('down', B3.k19_guard('down'))], 0, -8)
    guard.on(on_scene(), shape('idle'))
    guard.on(on_msg('k19_박'), shape(add(1, V('k19_동작'))), guard.pct(106), wait(0.06), guard.pct(100))
    guard.on(on_msg('k19_쉬기'), shape('idle'))
    rule = m.S('규칙띠', [('one', K.badge('한 박자 전 동작을 누르세요', 210, 22, 'royal')),
                         ('two', K.badge('두 박자 전 동작을 누르세요!', 210, 22, 'red'))], 0, 88)
    rule.on(on_scene(), shape('one'))
    rule.on(on_msg('k19_단계'), shape(V('k19_뒤')), rule.pct(130), rep(5, rule.grow_pct(-6), wait(0.016)))
    _pop(m, '단계글', K.big_text('이제 두 박자 전!', 30, 'red'), 0, 30, 'k19_단계', hold=1.0)
    # 방향키 표시
    keys = [K_LEFT, K_UP, K_RIGHT, K_DOWN]
    for k in range(4):
        a = m.S('키%d' % k, [('off', B3.k19_arrow(k, 0)), ('on', B3.k19_arrow(k, 1))], [-178, -138, -98, -138][k],
                [-104, -68, -104, -104][k])
        a.on(on_key(keys[k]), shape('on'), wait(0.12), shape('off'))
    beat_t = m.T('박자글', ' ', 160, 60, 12, C_WHITE, F_NUM, False, 0, w=120, h=18)
    beat_t.on(on_msg('k19_박'), write(join(V('k19_박'), ' 박자')))
    judge = m.S('판정', [('ok', K.big_text('좋아요!', 26, 'green')), ('no', K.big_text('틀렸어요', 24, 'red')),
                       ('late', K.big_text('놓쳤어요', 24, 'gray'))], 160, 20, visible=False)
    judge.on(on_msg('k19_판정'), shape(V('k19_얻음')), judge.pct(50), show(), rep(5, judge.grow_pct(10), wait(0.016)), wait(0.3), hide())
    for k in range(4):
        hidden(m, '입력%d' % k).on(on_key(keys[k]), if_(and_(eq(V('입력가능'), 1), eq(V('k19_눌림'), 0)),
                                                      setv('k19_눌림', k + 1)))
    mgr = hidden(m, '교대담당')
    judge_blocks = [if_(gt(V('k19_답'), 0),
                        ifelse(eq(V('k19_눌림'), V('k19_답')), [setv('k19_얻음', 1), chg('맞춤', 1)],
                               [ifelse(eq(V('k19_눌림'), 0), [setv('k19_얻음', 3)], [setv('k19_얻음', 2)])]),
                        cast('k19_판정'), setv('미니표시', join(V('맞춤'), '/%d' % NANS)))]
    body = [setv('k19_n', 0), setv('k19_박', 0), setv('k19_답', 0)]
    for back, nb, per in PH:
        body += [setv('k19_뒤', back), *([cast('k19_단계'), cast('k19_쉬기'), wait(2.2)] if back > 1 else []),
                 until(le(LLEN('k19_순서'), 0), lst_del('k19_순서', 1)),
                 setv('_mi', 0),
                 rep(nb,
                     chg('_mi', 1), chg('k19_박', 1),
                     setv('k19_동작', rnd(1, 4)), lst_add('k19_순서', V('k19_동작')),
                     ifelse(gt(V('_mi'), back), [setv('k19_답', LGET('k19_순서', sub(V('_mi'), back)))], [setv('k19_답', 0)]),
                     setv('k19_눌림', 0), setv('입력가능', 1), cast('k19_박'),
                     wait(per - 0.12), setv('입력가능', 0), *judge_blocks, wait(0.12)),
                 cast('k19_쉬기'), wait(0.6)]
    mgr.on(on_msg('게임시작'), *body, *m.end_blocks(mul(V('맞춤'), 100.0 / NANS)))
    m.on_start(setv('맞춤', 0), setv('입력가능', 0), setv('k19_박', 0))
    m.snd('k19_박', play('stamp'))
    m.snd('k19_판정', ifelse(eq(V('k19_얻음'), 1), [play('coin')], [play('bad')]))
    m.snd('k19_단계', play('whistle'))
    m.finish('수문장이 박자마다 깃발로 ← ↑ → ↓ 동작을 해요. 지금 동작이\n아니라 바로 전 박자의 동작을 방향키로 누르세요! (뒤에 2박자 전)',
             '조작: 방향키 ← ↑ → ↓  ·  첫 박자는 보기만 하세요')
    return True


# ================================================================== 20. 흑두루미 세기
@game(20)
def g20(P, ctx):
    RD = [(8, 3, 6, 2.2), (11, 4, 8, 2.5), (13, 5, 9, 2.8), (16, 6, 10, 3.1), (18, 7, 11, 3.4), (21, 8, 12, 3.8)]  # 전체, 두루미 최소, 최대, 속도
    R = len(RD)
    m = mg(P, ctx, T, 20, status='1/%d' % R, dim=50)
    P.list('k20_판', [x for r in RD for x in r])
    vars_(P, 'k20_전체', 'k20_두루미', 'k20_남은', 'k20_남은두루미', 'k20_날기', 'k20_답', 'k20_속도', 'k20_종', 'k20_얻음', 'k20_입력')
    bird = m.S('새', [('c0', B3.k20_bird('crane', 0)), ('c1', B3.k20_bird('crane', 1)), ('e0', B3.k20_bird('egret', 0)),
                     ('e1', B3.k20_bird('egret', 1)), ('d0', B3.k20_bird('duck', 0)), ('d1', B3.k20_bird('duck', 1))],
               0, -300, visible=False)
    for v_ in ('복제', '종류', '날개', '내속도'):
        bird.local(v_, 0)
    bird.on(on_clone(), setv('복제', 1), setv('종류', V('k20_종')), setv('날개', 0),
            setv('내속도', mul(V('k20_속도'), div(rnd(85, 115), 100))),
            xy(-275, rnd(-40, 84)), shape(sub(mul(V('종류'), 2), 1)), show(),
            until(or_(gt(obj_x(), 275), eq(V('게임중'), 0)),
                  mvx(V('내속도')), chg('날개', 1),
                  if_(eq(mod(V('날개'), 8), 0), shape(add(sub(mul(V('종류'), 2), 1), mod(div(V('날개'), 8), 2))))),
            chg('k20_날기', -1), del_clone())
    # 답 고르기 판
    ui = []
    ui.append(panel(P, m.sc, '답판', 0, -30, 250, 120, 'glass', header='royal', visible=False))
    ui.append(m.T('질문', '흑두루미는 몇 마리였나요?', 0, 14, 12, C_WHITE, F_BODY, True, 0, w=240, h=18, visible=False))
    num = m.T('답숫자', '0', 0, -24, 30, C_WHITE, F_NUM, False, 0, w=80, h=36, visible=False)
    num.on(on_msg('k20_답'), write(V('k20_답')))
    ui.append(num)
    ok_ = and_(eq(V('게임중'), 1), eq(V('k20_입력'), 1))
    inc = lambda d: [if_(ok_, chg('k20_답', d), if_(lt(V('k20_답'), 0), setv('k20_답', 0)), if_(gt(V('k20_답'), 20), setv('k20_답', 20)),
                         cast('k20_답'))]
    ui.append(button(P, m.sc, 'k20빼기', '−', -70, -24, 40, 34, 'steel', actions=inc(-1), visible=False))
    ui.append(button(P, m.sc, 'k20더하기', '+', 70, -24, 40, 34, 'royal', actions=inc(1), visible=False))
    done = [if_(ok_, setv('k20_입력', 0))]
    ui.append(button(P, m.sc, 'k20확인', '확인', 0, -68, 90, 26, 'green', actions=done, visible=False))
    for o in ui:
        o.on(on_msg('k20_묻기'), show())
        o.on(on_msg('k20_닫기'), hide())
    keyer = hidden(m, '세기키')
    keyer.on(on_key(K_UP), *inc(1))
    keyer.on(on_key(K_RIGHT), *inc(1))
    keyer.on(on_key(K_DOWN), *inc(-1))
    keyer.on(on_key(K_LEFT), *inc(-1))
    keyer.on(on_key(K_ENTER), *done)
    keyer.on(on_key(K_SPACE), *done)
    for n in range(10):
        keyer.on(on_key(48 + n), if_(ok_, setv('k20_답', n), cast('k20_답')))
    m.S('보기두루미', B3.k20_bird('crane', 0), -186, -120)
    m.T('보기글', '= 흑두루미 (세기!)', -112, -120, 10, C_WHITE, F_BODY, True, 1, w=110, h=14)
    m.S('보기백로', B3.k20_bird('egret', 0), 70, -120)
    m.S('보기오리', B3.k20_bird('duck', 0), 120, -120)
    m.T('보기글2', '= 세지 마세요', 186, -120, 10, C_DIM, F_BODY, True, 0, w=90, h=14)
    msg = m.T('결과글', ' ', 0, -106, 13, C_WHITE, F_NUM, False, 0, w=360, h=20, visible=False)
    msg.on(on_msg('k20_결과'), write(join('정답 ', V('k20_두루미'), '마리 · ', V('k20_얻음'), '점')), show(), wait(1.6), hide())
    ready = m.T('준비글', ' ', 0, 30, 14, C_ACC, F_NUM, False, 0, w=300, h=20, visible=False)
    ready.on(on_msg('k20_준비'), write(join(V('라운드'), '번째 무리가 와요!')), show(), wait(1.0), hide())
    mgr = hidden(m, '세기담당')
    rd = lambda k: LGET('k20_판', add(mul(sub(V('라운드'), 1), 4), k))
    mgr.on(on_msg('게임시작'), setv('라운드', 1),
           until(or_(gt(V('라운드'), R), eq(V('게임중'), 0)),
                 setv('미니표시', join(V('라운드'), '/%d · ' % R, rounded(V('합계')), '점')),
                 setv('k20_전체', rd(1)), setv('k20_두루미', rnd(rd(2), rd(3))), setv('k20_속도', rd(4)),
                 setv('k20_남은', V('k20_전체')), setv('k20_남은두루미', V('k20_두루미')), setv('k20_날기', V('k20_전체')),
                 cast('k20_준비'), wait(1.2),
                 until(or_(le(V('k20_남은'), 0), eq(V('게임중'), 0)),
                       ifelse(le(rnd(1, V('k20_남은')), V('k20_남은두루미')), [setv('k20_종', 1), chg('k20_남은두루미', -1)],
                              [setv('k20_종', rnd(2, 3))]),
                       chg('k20_남은', -1), clone_of(bird.name),
                       wait(div(rnd(12, 40), mul(V('k20_속도'), 10)))),
                 wait_until(or_(le(V('k20_날기'), 0), eq(V('게임중'), 0))),
                 setv('k20_답', 0), cast('k20_답'), cast('k20_묻기'), setv('k20_입력', 1),
                 wait_until(or_(eq(V('k20_입력'), 0), eq(V('게임중'), 0))),
                 cast('k20_닫기'),
                 ifelse(eq(V('k20_답'), V('k20_두루미')), [setv('k20_얻음', 17), chg('맞춤', 1)],
                        [ifelse(eq(abs_(sub(V('k20_답'), V('k20_두루미'))), 1), [setv('k20_얻음', 8)], [setv('k20_얻음', 0)])]),
                 chg('합계', V('k20_얻음')), cast('k20_결과'), wait(1.8), chg('라운드', 1)),
           *m.end_blocks(V('합계')))
    m.on_start(setv('합계', 0), setv('맞춤', 0), setv('k20_입력', 0))
    m.snd('k20_결과', ifelse(eq(V('k20_얻음'), 17), [play('fanfare')], [ifelse(gt(V('k20_얻음'), 0), [play('good')], [play('bad')])]))
    m.snd('k20_준비', play('whistle'))
    m.finish('순천만 하늘로 새 떼가 지나가요. 회색 몸에 하얀 목인\n흑두루미만 세세요! 흰 백로와 오리는 빼고요. (6번)',
             '조작: ↑ ↓ (또는 + − 단추, 숫자키) 로 답 고르기 → Enter/확인')
    return True
