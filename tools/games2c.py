# -*- coding: utf-8 -*-
"""세종시장 선거 미니게임 21~30번."""
import random
from games_common import *
import mg_art3 as A3

T = 2
GAMES, game = registry()
import art2c as AC


# ------------------------------------------------------------------ 공통 도우미
def stamp():
    """도장 찍기 (지금 모양을 그 자리에 남김; 붓 지우기로 지워짐)."""
    return B('brush_stamp')


def reset_size():
    return B('reset_scale_size')


def grow_rel(p):
    """지금 크기의 p% 만큼 키우기 (모양 크기가 달라도 같은 비율)."""
    return B('change_scale_percent', VALUE=p)


def pen_alpha(v):
    return B('set_brush_tranparency', VALUE=v)


def pop_blocks():
    """모양마다 크기가 달라도 똑같이 튀어나오는 효과 (복제본이 아닌 오브젝트용)."""
    return [reset_size(), grow_rel(30), to_front(), show(), rep(5, grow_rel(-4.6), wait(0.016))]


def judge_pop(m, base, styles, x, y, msg, var='_mv', hold=0.55):
    """styles: [(글, 크기, 색)...] — var 번호(1부터)의 글이 튀어나왔다 사라진다."""
    pics = [('j%d' % (k + 1), K.big_text(t_, sz, col)) for k, (t_, sz, col) in enumerate(styles)]
    o = m.S(base, pics, x, y, visible=False)
    o.on(on_msg(msg), shape(V(var)), *pop_blocks(), wait(hold), hide())
    return o


def clamp_(var, lo, hi):
    return [if_(lt(V(var), lo), setv(var, lo)), if_(gt(V(var), hi), setv(var, hi))]


# ================================================================== 21. 농구 자유투 (슛)
@game(21)
def g21(P, ctx):
    N = 10
    spots = [-40, -40, -100, -100, -10, -10, -140, -140, -70, -70]
    RX0, RX1, RY, BR, BX = 144, 180, 22, 7, 186
    G_, FLOOR = 0.32, -93
    m = mg(P, ctx, T, 21, time_limit=75, status='슛 1/%d · 골 0' % N, dim=40)
    vars_(P, 's21_x', 's21_y', 's21_vx', 's21_vy', 's21_각도', 's21_힘', 's21_지난힘', 's21_상태', 's21_림', 's21_골',
          's21_깔끔', 's21_슛', 's21_선수x', 's21_py', 's21_nx', 's21_ny', 's21_d', 's21_vn', 's21_t0', 's21_바닥', 's21_끝', 's21_골인')
    P.list('s21_자리', spots)
    X, Y, VX, VY = 's21_x', 's21_y', 's21_vx', 's21_vy'
    m.S('코트', AC.s21_floor(), 0, -118)
    m.S('골대', AC.s21_hoop(), 182, -9)
    pl = m.S('선수', [('ready', AC.s21_player('ready')), ('shot', AC.s21_player('shot'))], -40, -62)
    pl.on(on_msg('s21_자리'), shape('ready'), glide(0.25, V('s21_선수x'), -62))
    pl.on(on_msg('s21_던짐'), shape('shot'))
    mark = m.S('자유투선', AC.s21_mark(), -40, -101)
    mark.on(on_msg('s21_자리'), lx(V('s21_선수x')))
    # 조준 화살표 (공을 중심으로 회전, 힘에 따라 길어짐)
    aim = m.S('조준선', AC.s21_aim(), 0, 0, visible=False)
    aim.on(on_msg('게임시작'),
           until(eq(V('게임중'), 0),
                 ifelse(or_(eq(V('s21_상태'), 1), eq(V('s21_상태'), 2)),
                        [xy(V(X), V(Y)), rot(mul(V('s21_각도'), -1)), show(),
                         if_(eq(V('s21_상태'), 2), aim.pct(add(70, mul(V('s21_힘'), 0.55))))],
                        [hide(), aim.pct(70)]),
                 wait(0.016)),
           hide())
    # 힘 막대 + 지난번 힘 표시
    bar = m.S('힘막대', K.bar_set('s21_pow', 64, 8, 'red'), -40, -111)
    bar.on(on_msg('s21_자리'), lx(V('s21_선수x')), shape(1))
    bar.on(on_msg('s21_충전'), until(ne(V('s21_상태'), 2), shape(add(floor(mul(V('s21_힘'), 0.4)), 1)), wait(0.016)))
    ghost = m.S('지난힘', AC.s21_mark(), -40, -105, visible=False)
    ghost.on(on_msg('s21_자리'), if_(gt(V('s21_지난힘'), 0), xy(add(sub(V('s21_선수x'), 30), mul(V('s21_지난힘'), 0.6)), -105), show()),
             if_(eq(V('s21_지난힘'), 0), hide()))
    dist = m.T('거리글', ' ', -40, -125, 9, C_WHITE, F_NUM, False, 0, w=90, h=13)
    dist.on(on_msg('s21_자리'), lx(V('s21_선수x')),
            write(join('거리 ', div(rounded(div(sub(162, V('s21_선수x')), 5)), 10), 'm')))
    # 공
    ball = m.S('농구공', AC.s21_ball(), -30, -27)

    def rim_hit(px, py):
        d2 = add(mul(sub(V(X), px), sub(V(X), px)), mul(sub(V(Y), py), sub(V(Y), py)))
        return if_(lt(d2, BR * BR),
                   setv('s21_d', fn('root', d2)),
                   if_(gt(V('s21_d'), 0.01),
                       setv('s21_nx', div(sub(V(X), px), V('s21_d'))), setv('s21_ny', div(sub(V(Y), py), V('s21_d'))),
                       setv('s21_vn', add(mul(V(VX), V('s21_nx')), mul(V(VY), V('s21_ny')))),
                       if_(lt(V('s21_vn'), 0),
                           chg(VX, mul(mul(V('s21_vn'), -1.55), V('s21_nx'))), chg(VY, mul(mul(V('s21_vn'), -1.55), V('s21_ny'))),
                           setv('s21_림', 1), cast('s21_링')),
                       setv(X, add(px, mul(V('s21_nx'), BR + 0.3))), setv(Y, add(py, mul(V('s21_ny'), BR + 0.3)))))

    aim_calc = [setv('_ma', sub(mouse_x(), V(X))), setv('_mb', sub(mouse_y(), V(Y))),
                ifelse(lt(V('_ma'), 3), [setv('s21_각도', 80)], [setv('s21_각도', fn('atan_radian', div(V('_mb'), V('_ma'))))]),
                *clamp_('s21_각도', 15, 80)]
    flight = [setv(VX, mul(add(4, mul(V('s21_힘'), 0.1)), cos_(V('s21_각도')))),
              setv(VY, mul(add(4, mul(V('s21_힘'), 0.1)), sin_(V('s21_각도')))),
              setv('s21_림', 0), setv('s21_바닥', 0), setv('s21_끝', 0), setv('_mi', 0), setv('s21_골인', 0),
              pen_clear(), pen_down(),
              until(eq(V('s21_끝'), 1),
                    setv('s21_py', V(Y)),
                    chg(VY, -G_), chg(X, V(VX)), chg(Y, V(VY)),
                    # 백보드
                    if_(and_(and_(gt(V(X), BX - BR), lt(V(X), BX + 8)), and_(gt(V(Y), 10), lt(V(Y), 80))),
                        if_(gt(V(VX), 0), setv(VX, mul(V(VX), -0.55)), setv(X, BX - BR), setv('s21_림', 1), cast('s21_판'))),
                    rim_hit(RX0, RY), rim_hit(RX1, RY),
                    # 골 판정: 림 높이를 위에서 아래로 지나감
                    if_(and_(and_(ge(V('s21_py'), RY), lt(V(Y), RY)), and_(gt(V(X), RX0 + 2), lt(V(X), RX1 - 2))),
                        if_(eq(V('s21_골인'), 0),
                            setv('s21_골인', 1), chg('s21_골', 1), ifelse(eq(V('s21_림'), 0), [chg('s21_깔끔', 1), setv('_mv', 2)], [setv('_mv', 1)]),
                            cast('s21_판정'), cast('s21_그물'))),
                    # 바닥
                    if_(lt(V(Y), FLOOR),
                        setv(Y, FLOOR), setv(VY, mul(V(VY), -0.45)), setv(VX, mul(V(VX), 0.6)), chg('s21_바닥', 1),
                        if_(ge(V('s21_바닥'), 2), setv('s21_끝', 1))),
                    if_(gt(abs_(V(X)), 250), setv('s21_끝', 1)),
                    chg('_mi', 1), if_(gt(V('_mi'), 420), setv('s21_끝', 1)),
                    xy(V(X), V(Y)), rot_by(mul(V(VX), 4))),
              pen_up()]
    ball.on(on_scene(), pen_up(), pen_clear(), pen_size(1.6), pen_color('#AFC0FF'), pen_alpha(45))
    ball.on(on_msg('게임시작'),
            setv('s21_슛', 0),
            until(or_(ge(V('s21_슛'), N), eq(V('게임중'), 0)),
                  setv('s21_선수x', LGET('s21_자리', add(V('s21_슛'), 1))),
                  if_(eq(mod(V('s21_슛'), 2), 0), setv('s21_지난힘', 0), pen_up(), pen_clear()),
                  setv('미니표시', join('슛 ', add(V('s21_슛'), 1), '/', N, ' · 골 ', V('s21_골'))),
                  cast('s21_자리'), rot(0), hide(), wait(0.3),
                  setv(X, add(V('s21_선수x'), 10)), setv(Y, -27), xy(V(X), V(Y)), show(),
                  setv('s21_힘', 0), setv('s21_상태', 1),
                  wait_until(not_(mouse_down())),
                  until(or_(mouse_down(), eq(V('게임중'), 0)), *aim_calc),
                  setv('s21_상태', 2), setv('s21_t0', timer()), cast('s21_충전'),
                  until(or_(not_(mouse_down()), eq(V('게임중'), 0)), *aim_calc,
                        setv('s21_힘', mul(sub(timer(), V('s21_t0')), 66)), if_(gt(V('s21_힘'), 100), setv('s21_힘', 100))),
                  setv('s21_상태', 3), setv('s21_지난힘', V('s21_힘')), cast('s21_던짐'),
                  *flight,
                  if_(eq(V('s21_골인'), 0), ifelse(eq(V('s21_림'), 1), [setv('_mv', 3)], [setv('_mv', 4)]), cast('s21_판정')),
                  chg('s21_슛', 1), setv('s21_상태', 0),
                  setv('미니표시', join('슛 ', V('s21_슛'), '/', N, ' · 골 ', V('s21_골'))),
                  wait(0.5)),
            hide(),
            *m.end_blocks(add(mul(V('s21_골'), 9), V('s21_깔끔'))))
    rim = m.S('림앞', [('n', AC.s21_rim(0)), ('w', AC.s21_rim(1))], 162, 7)
    rim.on(on_msg('s21_그물'), shape('w'), wait(0.25), shape('n'))
    judge_pop(m, '슛판정', [('골인!', 30, 'royal'), ('클린슛!', 30, 'green'), ('아깝다!', 26, 'red'), ('에어볼...', 24, 'gray')],
              40, 62, 's21_판정')
    tip = m.T('슛안내', '마우스로 방향 · 꾹 눌렀다 떼면 슛!', -60, 84, 10, C_WHITE, F_BODY, True, 0, w=240, h=16, bg=C_BOX)
    tip.on(on_msg('s21_던짐'), if_(eq(V('s21_슛'), 0), hide()))
    mgr = hidden(m, '슛담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(mul(V('s21_골'), 9), V('s21_깔끔'))))
    m.on_start(setv('s21_골', 0), setv('s21_깔끔', 0), setv('s21_상태', 0), setv('s21_지난힘', 0), setv('s21_힘', 0),
               setv('s21_선수x', spots[0]))
    m.snd('s21_던짐', play('jump'))
    m.snd('s21_링', play('tick'))
    m.snd('s21_판', play('hit'))
    m.snd('s21_판정', ifelse(le(V('_mv'), 2), [play('good')], [play('bad')]))
    m.finish('공에서 마우스 쪽으로 슛 방향이 정해져요. 꾹 누른 시간만큼\n힘이 세져요! 같은 자리에서 두 번씩, 지난 공 궤적을 참고!',
             '조작: 마우스로 조준 → 누르고 있다가 떼면 슛  ·  10번 (골 9점, 클린슛 +1)')
    return True


# ================================================================== 22. 다운힐 슬라롬 (조향)
@game(22)
def g22(P, ctx):
    N, BY, GAP = 20, 62, 170
    m = mg(P, ctx, T, 22, status='통과 0/%d' % N, dim=110)
    vars_(P, 's22_x', 's22_vx', 's22_속도', 's22_거리', 's22_다음문', 's22_다음돌', 's22_문수', 's22_판정수', 's22_통과',
          's22_놓침', 's22_충돌', 's22_gx', 's22_무적')
    SPD = 's22_속도'
    m.S('산길', AC.s22_road(), 0, -16)
    # 길 위 자갈 (속도감) · 길가 나무: 화면 밖으로 나가면 아래로 되돌아온다
    peb = m.S('자갈', [('a', AC.s22_dot(0)), ('b', AC.s22_dot(1)), ('c', AC.s22_dot(2))], 0, -300, visible=False)
    peb.local('복제', 0)
    peb.local('k', 0)
    peb.on(on_msg('게임시작'), *[flat(setv('k', k), clone_self()) for k in range(9)])
    peb.on(on_clone(), setv('복제', 1), shape(add(mod(V('k'), 3), 1)), xy(rnd(-150, 150), sub(130, mul(V('k'), 30))), show(),
           until(eq(V('게임중'), 0), mvy(V(SPD)), if_(gt(obj_y(), 104), xy(rnd(-150, 150), -132))), del_clone())
    tree = m.S('길가나무', [('a', AC.s22_tree(0)), ('b', AC.s22_tree(1))], 0, -300, visible=False)
    tree.local('복제', 0)
    tree.local('k', 0)
    tree.on(on_msg('게임시작'), *[flat(setv('k', k), clone_self()) for k in range(8)])
    tree.on(on_clone(), setv('복제', 1), shape(rnd(1, 2)),
            xy(mul(rnd(192, 222), sub(mul(mod(V('k'), 2), 2), 1)), sub(120, mul(V('k'), 34))), show(),
            until(eq(V('게임중'), 0), mvy(V(SPD)),
                  if_(gt(obj_y(), 150), ly(-150), lx(mul(rnd(192, 222), sub(mul(rnd(0, 1), 2), 1))), shape(rnd(1, 2)))),
            del_clone())
    # 깃문
    gate = m.S('깃문', [('n', AC.s22_gate('n')), ('ok', AC.s22_gate('ok')), ('x', AC.s22_gate('x'))], 0, -300, visible=False)
    for v in ('gx', '판정', '복제'):
        gate.local(v, 0)
    gate.on(on_msg('게임시작'), setv('s22_다음문', 40), setv('s22_gx', 0),
            until(or_(ge(V('s22_문수'), N), eq(V('게임중'), 0)),
                  wait_until(or_(ge(V('s22_거리'), V('s22_다음문')), eq(V('게임중'), 0))),
                  setv('s22_gx', add(V('s22_gx'), mul(rnd(45, 105), sub(mul(rnd(0, 1), 2), 1)))),
                  if_(gt(V('s22_gx'), 118), setv('s22_gx', sub(V('s22_gx'), 150))),
                  if_(lt(V('s22_gx'), -118), setv('s22_gx', add(V('s22_gx'), 150))),
                  setv('gx', V('s22_gx')), clone_self(), chg('s22_문수', 1), chg('s22_다음문', GAP)))
    gate.on(on_clone(), setv('복제', 1), setv('판정', 0), shape('n'), xy(V('gx'), -150), show(),
            until(or_(gt(obj_y(), 150), eq(V('게임중'), 0)),
                  mvy(V(SPD)),
                  if_(and_(eq(V('판정'), 0), ge(obj_y(), BY)),
                      setv('판정', 1), chg('s22_판정수', 1),
                      ifelse(lt(abs_(sub(V('s22_x'), V('gx'))), 25),
                             [shape('ok'), chg('s22_통과', 1), setv('_mv', 1)],
                             [shape('x'), chg('s22_놓침', 1), setv('_mv', 2)]),
                      cast('s22_판정'),
                      setv('미니표시', join('통과 ', V('s22_통과'), '/', N)))),
            del_clone())
    # 바위 (깃문 사이에 가끔)
    rock = m.S('바위', AC.s22_rock(), 0, -300, visible=False)
    for v in ('복제', '맞음'):
        rock.local(v, 0)
    rock.on(on_msg('게임시작'), setv('s22_다음돌', 40 + GAP * 2 + GAP // 2),
            until(or_(ge(V('s22_문수'), N), eq(V('게임중'), 0)),
                  wait_until(or_(ge(V('s22_거리'), V('s22_다음돌')), eq(V('게임중'), 0))),
                  if_(le(rnd(1, 100), 70), clone_self()), chg('s22_다음돌', GAP)))
    rock.on(on_clone(), setv('복제', 1), setv('맞음', 0), xy(rnd(-140, 140), -150), show(),
            until(or_(gt(obj_y(), 150), eq(V('게임중'), 0)),
                  mvy(V(SPD)),
                  if_(and_(and_(eq(V('맞음'), 0), lt(abs_(sub(obj_y(), BY)), 13)),
                           and_(lt(abs_(sub(obj_x(), V('s22_x'))), 15), eq(V('s22_무적'), 0))),
                      setv('맞음', 1), chg('s22_충돌', 1), setv('_mv', 3), cast('s22_판정'), cast('s22_쿵'))),
            del_clone())
    # 자전거
    bike = m.S('자전거', [('a', AC.s22_bike(False)), ('b', AC.s22_bike(True))], 0, BY)
    bike.on(on_scene(), xy(0, BY), rot(0), shape('a'))
    bike.on(on_msg('게임시작'), setv('s22_x', 0), setv('s22_vx', 0),
            until(eq(V('게임중'), 0),
                  if_(key(K_LEFT), chg('s22_vx', -0.42)), if_(key(K_RIGHT), chg('s22_vx', 0.42)),
                  setv('s22_vx', mul(V('s22_vx'), 0.91)), chg('s22_x', V('s22_vx')),
                  if_(gt(abs_(V('s22_x')), 150), setv('s22_x', mul(150, div(V('s22_x'), abs_(V('s22_x'))))), setv('s22_vx', 0)),
                  lx(V('s22_x')), if_(eq(V('s22_무적'), 0), rot(mul(V('s22_vx'), -6)))))
    bike.on(on_msg('s22_쿵'), setv('s22_무적', 1), setv(SPD, 0.3), shape('b'),
            rep(12, rot_by(30), wait(0.03)), rot(0), shape('a'),
            rep(4, fx('transparency', 60), wait(0.08), fx('transparency', 0), wait(0.08)), setv('s22_무적', 0))
    mgr = hidden(m, '슬라롬담당')
    mgr.on(on_msg('게임시작'), setv('s22_거리', 0), setv(SPD, 1.0),
           until(or_(ge(V('s22_판정수'), N), eq(V('게임중'), 0)),
                 setv('_ma', add(1.25, mul(V('s22_판정수'), 0.07))),
                 ifelse(lt(V(SPD), V('_ma')), [chg(SPD, 0.012)], [setv(SPD, V('_ma'))]),
                 chg('s22_거리', V(SPD))),
           wait(0.6), *m.end_blocks(sub(mul(V('s22_통과'), 5), mul(V('s22_충돌'), 4))))
    judge_pop(m, '슬라롬판정', [('통과!', 20, 'green'), ('놓쳤다!', 20, 'red'), ('쿵!', 26, 'red')], 0, 22, 's22_판정', hold=0.3)
    m.on_start(setv('s22_통과', 0), setv('s22_놓침', 0), setv('s22_충돌', 0), setv('s22_판정수', 0), setv('s22_문수', 0),
               setv('s22_무적', 0), setv(SPD, 0), setv('s22_x', 0))
    m.snd('s22_판정', ifelse(eq(V('_mv'), 1), [play('coin')], [ifelse(eq(V('_mv'), 2), [play('bad')], [play('hit')])]))
    m.finish('장군산 고갯길을 자전거로 내려가요! 빨강·파랑 깃발 사이로\n지나가세요. 바위에 부딪히면 느려져요. 점점 빨라져요!',
             '조작: ← → 방향키 (핸들이 미끄러지니 미리 꺾기)  ·  깃문 20개, 통과 1개 5점')
    return True


# ================================================================== 23. 불량품 골라내기 (공간 지각: 돌린 모양 / 뒤집힌 모양)
@game(23)
def g23(P, ctx):
    N, NS = 15, len(AC.S23_SHAPES)
    SX, SY = 70, 12
    m = mg(P, ctx, T, 23, status='부품 1/%d' % N, dim=70)
    vars_(P, 's23_번호', 's23_모양', 's23_뒤집힘', 's23_각', 's23_답', 's23_대기', 's23_제한', 's23_t0', 's23_정답')
    panel(P, m.sc, '도면판', -160, 0, 142, 176, 'glass')
    plan = m.S('도면', [('d%d' % (i + 1), AC.s23_plan(i)) for i in range(NS)], -160, 4)
    plan.on(on_msg('s23_도면'), shape(V('s23_모양')), plan.pct(90), rep(4, plan.grow_pct(2.5), wait(0.016)))
    m.T('도면글', '이 도면대로 만들어야 해요', -160, -80, 8, C_DIM, F_BODY, True, 0, w=136, h=12)
    belt = m.S('컨베이어', [('a', AC.s23_belt(0)), ('b', AC.s23_belt(1))], 75, -30)
    belt.on(on_msg('s23_벨트'), rep(10, next_shape(), wait(0.05)))
    m.S('출고상자', AC.s23_box('ship'), -66, -36)
    m.S('불량통', AC.s23_box('bin'), 212, -76)
    scan = m.S('검사틀', [('n', AC.s23_scanner('n')), ('ok', AC.s23_scanner('ok')), ('x', AC.s23_scanner('x'))], SX, SY)
    scan.on(on_msg('s23_판정'), ifelse(le(V('_mv'), 2), [shape('ok')], [shape('x')]), wait(0.6), shape('n'))
    tb = m.S('검사시간', K.bar_set('s23_t', 86, 6, 'royal'), SX, 62)
    tb.on(on_msg('s23_검사'), until(eq(V('s23_대기'), 0),
                                   shape(add(floor(mul(sub(1, div(sub(timer(), V('s23_t0')), V('s23_제한'))), 40)), 1)), wait(0.05)),
          shape(1))
    part = m.S('부품', [('p%d%s' % (i + 1, 'nm'[mr]), AC.s23_part(i, mr)) for i in range(NS) for mr in (0, 1)], 270, SY,
               visible=False)
    ok_expr = or_(and_(eq(V('s23_답'), 1), eq(V('s23_뒤집힘'), 0)), and_(eq(V('s23_답'), 2), eq(V('s23_뒤집힘'), 1)))
    part.on(on_msg('게임시작'), setv('s23_번호', 1),
            until(or_(gt(V('s23_번호'), N), eq(V('게임중'), 0)),
                  setv('s23_모양', rnd(1, NS)), if_(le(V('s23_번호'), 4), setv('s23_모양', rnd(1, 3))),
                  setv('s23_뒤집힘', rnd(0, 1)), setv('s23_각', rnd(0, 3)),
                  if_(eq(V('s23_번호'), 1), setv('s23_각', rnd(1, 3))),
                  setv('미니표시', join('부품 ', V('s23_번호'), '/', N, ' · 정확 ', V('맞춤'))),
                  cast('s23_도면'), cast('s23_벨트'),
                  shape(add(mul(sub(V('s23_모양'), 1), 2), V('s23_뒤집힘'), 1)), rot(mul(V('s23_각'), 90)), xy(270, SY), show(),
                  glide(0.5, SX, SY),
                  setv('s23_답', 0), setv('s23_제한', sub(5.2, mul(V('s23_번호'), 0.17))), setv('s23_t0', timer()),
                  setv('s23_대기', 1), cast('s23_검사'),
                  wait_until(or_(or_(ne(V('s23_답'), 0), gt(sub(timer(), V('s23_t0')), V('s23_제한'))), eq(V('게임중'), 0))),
                  setv('s23_대기', 0),
                  ifelse(ok_expr, [chg('맞춤', 1), setv('_mv', V('s23_답'))],
                         [chg('틀림', 1), ifelse(eq(V('s23_답'), 0), [setv('_mv', 4)], [setv('_mv', 3)])]),
                  cast('s23_판정'), wait(0.35),
                  ifelse(eq(V('s23_답'), 2), [glide(0.3, 212, -60)],
                         [ifelse(eq(V('s23_답'), 1), [cast('s23_벨트'), glide(0.4, -66, SY - 10)], [glide(0.3, SX, -150)])]),
                  hide(), chg('s23_번호', 1), wait(0.3)),
            setv('미니표시', join('정확 ', V('맞춤'), '/', N)),
            *m.end_blocks(mul(V('맞춤'), 100.0 / N)))
    expl = m.T('검사설명', ' ', SX, -58, 10, C_WHITE, F_BODY, True, 0, w=200, h=16, bg=C_BOX, visible=False)
    expl.on(on_msg('s23_판정'), ifelse(eq(V('s23_뒤집힘'), 0), [write('정답: 정상 (돌리면 도면과 같아요)'), text_color('#7DFFB0')],
                                     [write('정답: 불량 (뒤집힌 모양이에요!)'), text_color('#FF8C9C')]),
            show(), wait(1.0), hide())
    pick = lambda v: [if_(and_(eq(V('s23_대기'), 1), eq(V('게임중'), 1)), setv('s23_답', v))]
    button(P, m.sc, '정상버튼', '← 정상', 0, -104, 104, 28, 'green', actions=pick(1))
    button(P, m.sc, '불량버튼', '불량 →', 140, -104, 104, 28, 'red', actions=pick(2))
    keys = hidden(m, '검사키')
    keys.on(on_key(K_LEFT), *pick(1))
    keys.on(on_key(K_RIGHT), *pick(2))
    judge_pop(m, '검사판정', [('정상 OK!', 24, 'green'), ('불량 적발!', 24, 'royal'), ('틀렸어요!', 24, 'red'),
                          ('시간 초과!', 22, 'red')], SX, 84, 's23_판정', hold=0.45)
    m.on_start(setv('맞춤', 0), setv('틀림', 0), setv('s23_대기', 0), setv('s23_모양', 1))
    m.snd('s23_판정', ifelse(le(V('_mv'), 2), [play('good')], [play('bad')]))
    m.snd('s23_벨트', play('tick'))
    m.finish('도면을 돌리기만 한 모양이면 정상, 뒤집어야 같아지면 불량!\n머릿속으로 부품을 돌려 보세요. (15개, 점점 빨라져요)',
             '조작: ← 정상 · → 불량 (또는 아래 버튼 클릭)')
    return True


# ================================================================== 24. 실험 색 배합 (색 맞추기)
S24_TARGETS = [('주황', 4, 2, 0), ('보라', 2, 0, 4), ('하늘', 1, 3, 4), ('연두', 2, 4, 0), ('분홍', 4, 1, 3),
               ('청록', 0, 3, 3), ('노랑', 4, 4, 0), ('갈색', 2, 1, 0), ('남색', 0, 1, 3), ('자주', 3, 0, 2),
               ('살구', 4, 3, 2), ('올리브', 2, 2, 0), ('회색', 2, 2, 2), ('민트', 2, 4, 3), ('빨강', 4, 0, 0)]
S24_HEX = ['00', '48', '88', 'C4', 'FF']


@game(24)
def g24(P, ctx):
    NT, NC = 5, len(S24_TARGETS)
    m = mg(P, ctx, T, 24, time_limit=80, status='시약 1/%d' % NT, dim=110)
    vars_(P, 's24_r', 's24_g', 's24_b', 's24_tr', 's24_tg', 's24_tb', 's24_조절', 's24_목표', 's24_대기', 's24_맞음', 's24_시작',
          's24_비슷')
    P.list('s24_hex', S24_HEX)
    P.list('s24_이름', [t_[0] for t_ in S24_TARGETS])
    P.list('s24_R', [t_[1] for t_ in S24_TARGETS])
    P.list('s24_G', [t_[2] for t_ in S24_TARGETS])
    P.list('s24_B', [t_[3] for t_ in S24_TARGETS])
    hexcol = lambda a, b, c: join('#', LGET('s24_hex', add(V(a), 1)), LGET('s24_hex', add(V(b), 1)), LGET('s24_hex', add(V(c), 1)))
    CH = [('s24_r', '빨강', 81, K_A), ('s24_g', '초록', 87, K_S), ('s24_b', '파랑', 69, K_D)]
    LX, RX, CY = -158, 158, 22
    panel(P, m.sc, '목표판', LX, CY - 8, 128, 168, 'glass', header='royal')
    panel(P, m.sc, '내판', RX, CY - 8, 128, 168, 'glass', header='royal')
    m.T('목표제목', '목표 색', LX, CY + 64, 11, C_WHITE, F_NUM, False, 0, w=110, h=16)
    m.T('내제목', '내가 만든 색', RX, CY + 64, 11, C_WHITE, F_NUM, False, 0, w=110, h=16)
    tsw = m.T('목표색', ' ', LX, CY, 8, C_WHITE, F_BODY, False, 0, w=76, h=76, bg='#000000')
    tsw.on(on_msg('s24_새목표'), B('text_change_bg_color', VALUE=hexcol('s24_tr', 's24_tg', 's24_tb')))
    msw = m.T('내색', ' ', RX, CY, 8, C_WHITE, F_BODY, False, 0, w=76, h=76, bg='#000000')
    msw.on(on_msg('s24_갱신'), B('text_change_bg_color', VALUE=hexcol('s24_r', 's24_g', 's24_b')))
    m.S('목표틀', AC.s24_frame(), LX, CY)
    mfr = m.S('내틀', AC.s24_frame(), RX, CY)
    mfr.on(on_msg('s24_성공'), rep(3, mfr.pct(108), wait(0.08), mfr.pct(100), wait(0.08)))
    tname = m.T('목표이름', ' ', LX, CY - 58, 11, C_ACC, F_NUM, False, 0, w=120, h=16)
    tname.on(on_msg('s24_새목표'), write(join(LGET('s24_이름', V('s24_시작')), ' 시약')))
    cnt = m.T('조절글', ' ', RX, CY - 58, 10, C_DIM, F_BODY, True, 0, w=120, h=16)
    cnt.on(on_msg('s24_갱신'), write(join('조절 ', V('s24_조절'), '번')))
    # 빨강·초록·파랑 조절기
    check = [setv('s24_비슷', sub(100, mul(add(abs_(sub(V('s24_r'), V('s24_tr'))), abs_(sub(V('s24_g'), V('s24_tg'))),
                                            abs_(sub(V('s24_b'), V('s24_tb')))), 100.0 / 12))),
             if_(eq(V('s24_비슷'), 100), setv('s24_맞음', 1))]
    for k, (var, nm, kup, kdn) in enumerate(CH):
        x = -64 + 64 * k
        tube = m.S('시험관%d' % k, [('l%d' % lv, AC.s24_tube(k, lv)) for lv in range(5)], x, CY + 4)
        tube.on(on_msg('s24_갱신'), shape(add(V(var), 1)))
        m.T('채널글%d' % k, nm, x, CY - 56, 10, ['#FF7A88', '#6EE69A', '#8FB0FF'][k], F_NUM, False, 0, w=60, h=14)
        for up in (1, 0):
            act = [if_(and_(eq(V('s24_대기'), 1), (lt if up else gt)(V(var), 4 if up else 0)),
                       chg(var, 1 if up else -1), chg('s24_조절', 1), *check, cast('s24_갱신'), cast('s24_딸깍'))]
            b = m.S('%s%d' % ('올림' if up else '내림', k), AC.s24_arrow(k, up), x, CY + 50 if up else CY - 40)
            G.hover_scripts(b, 110)
            b.on(on_click(), *act)
            b.on(on_click(), b.pct(85), wait(0.06), b.pct(100))
            hidden(m, '조절키%d%d' % (k, up)).on(on_key(kup if up else kdn), *act)
    # 비슷한 정도 막대
    m.T('비슷글', '비슷한 정도', -112, -96, 9, C_DIM, F_BODY, True, 0, w=80, h=13)
    sb = m.S('비슷막대', K.bar_set('s24_sim', 200, 9, 'green'), 30, -96)
    sb.on(on_msg('s24_갱신'), shape(add(floor(mul(V('s24_비슷'), 0.4)), 1)))
    pct = m.T('비슷값', ' ', 158, -96, 10, C_WHITE, F_NUM, False, 0, w=50, h=14)
    pct.on(on_msg('s24_갱신'), write(join(rounded(V('s24_비슷')), '%')))
    judge_pop(m, '배합판정', [('똑같아요!', 30, 'green')], 0, 70, 's24_성공', var='s24_맞음', hold=0.6)
    mgr = hidden(m, '배합담당')
    mgr.on(on_msg('게임시작'), setv('s24_목표', 0), setv('_mk', rnd(0, NC - 1)),
           until(or_(ge(V('s24_목표'), NT), eq(V('게임중'), 0)),
                 setv('s24_시작', add(mod(add(V('_mk'), mul(V('s24_목표'), 3)), NC), 1)),
                 setv('s24_tr', LGET('s24_R', V('s24_시작'))), setv('s24_tg', LGET('s24_G', V('s24_시작'))),
                 setv('s24_tb', LGET('s24_B', V('s24_시작'))),
                 setv('s24_r', 0), setv('s24_g', 0), setv('s24_b', 0), setv('s24_조절', 0), setv('s24_맞음', 0), *check,
                 setv('미니표시', join('시약 ', add(V('s24_목표'), 1), '/', NT, ' · 성공 ', V('맞춤'))),
                 cast('s24_새목표'), cast('s24_갱신'), setv('s24_대기', 1),
                 wait_until(or_(eq(V('s24_맞음'), 1), eq(V('게임중'), 0))),
                 setv('s24_대기', 0),
                 if_(eq(V('s24_맞음'), 1), chg('맞춤', 1),
                     # 가장 적은 조절 횟수(목표 단계의 합)보다 더 누른 만큼 보너스가 줄어든다
                     setv('_ma', sub(6, sub(V('s24_조절'), add(V('s24_tr'), V('s24_tg'), V('s24_tb'))))),
                     if_(lt(V('_ma'), 0), setv('_ma', 0)), chg('합계', V('_ma')),
                     cast('s24_성공'), wait(1.0)),
                 chg('s24_목표', 1)),
           *m.end_blocks(add(mul(V('맞춤'), 14), V('합계'))))
    mgr.on(on_msg('시간끝'), setv('s24_대기', 0), *m.end_blocks(add(add(mul(V('맞춤'), 14), V('합계')), mul(V('s24_비슷'), 0.08))))
    m.on_start(setv('맞춤', 0), setv('합계', 0), setv('s24_대기', 0), setv('s24_r', 0), setv('s24_g', 0), setv('s24_b', 0),
               setv('s24_tr', 0), setv('s24_tg', 0), setv('s24_tb', 0), setv('s24_시작', 1), setv('s24_비슷', 0))
    m.snd('s24_딸깍', play('tick'))
    m.snd('s24_성공', play('good'))
    m.finish('빛의 빨강·초록·파랑을 섞어 목표 색을 만드세요! (시약 5개)\n빨강+초록=노랑, 초록+파랑=하늘, 빨강+파랑=보라',
             '조작: ▲▼ 버튼 클릭 (키: Q·W·E 올리기, A·S·D 내리기)  ·  적게 누를수록 보너스')
    return True


# ================================================================== 25. 널뛰기 (타이밍)
@game(25)
def g25(P, ctx):
    TL = 25
    LOW, HIGH, VS = -96, -66, 0.72          # 발 높이: 낮은 끝 / 높은 끝, 화면 높이 배율
    m = mg(P, ctx, T, 25, time_limit=TL, status='최고 0.0m', dim=40)
    vars_(P, 's25_H', 's25_Hp', 's25_상태', 's25_t0', 's25_T', 's25_착지', 's25_눌림', 's25_누른때', 's25_대기',
          's25_내발', 's25_상대발', 's25_최고', 's25_u')
    ME, OP = -92, 92
    m.S('짚단', AC.s25_straw(), 0, -103)
    pl = m.S('널', AC.s25_plank(), 0, -86)
    pl.on(on_scene(), rot(-8))
    pl.on(on_msg('s25_상대뜀'), rot(-8))
    pl.on(on_msg('s25_내뜀'), rot(8))
    chars = []
    for who, x, col, face, fv in (('나', ME, (50, 96, 230), ctx['PORT']['me'], 's25_내발'),
                                  ('상대', OP, (214, 52, 74), ctx['PORT']['m2'], 's25_상대발')):
        body = m.S(who + '몸', [('stand', AC.s25_body(col, 'stand')), ('jump', AC.s25_body(col, 'jump'))], x, LOW + 24)
        head = m.S(who + '얼굴', face, x, LOW + 56, scale=1.05)
        fly = 's25_내뜀' if who == '나' else 's25_상대뜀'
        land = 's25_상대뜀' if who == '나' else 's25_내뜀'
        body.on(on_msg(fly), shape('jump'))
        body.on(on_msg(land), shape('stand'))
        for o, dy in ((body, 24), (head, 56)):
            o.on(on_scene(), ly(LOW + dy))
            o.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ly(add(V(fv), dy))))
        chars.append(body)
    m.S('내이름', K.badge('나', 40, 16, 'royal'), ME, -122)
    m.S('상대이름', K.badge('2번 후보', 64, 16, 'red'), OP, -122)
    # 높이 자
    RY0 = -60
    m.S('높이자', AC.s25_ruler(), 214, RY0 + 2)
    m.T('높이자글', '높이', 214, RY0 + 76, 8, C_DIM, F_BODY, True, 0, w=40, h=12)
    mk = m.S('내높이', AC.s25_marker((90, 140, 255)), 228, RY0 - 62)
    mk.on(on_msg('게임시작'), until(eq(V('게임중'), 0), ly(add(RY0 - 62, mul(sub(V('s25_내발'), LOW), 0.8)))))
    best = m.S('최고높이', AC.s25_marker((255, 90, 110)), 200, RY0 - 62, visible=False)
    best.on(on_msg('s25_판정'), ly(add(RY0 - 62, mul(V('s25_최고'), VS * 0.8))), show())
    best.on(on_scene(), rot(180))
    hgt = m.T('높이글', ' ', ME, 40, 13, C_WHITE, F_NUM, False, 0, w=90, h=18, visible=False)
    hgt.on(on_msg('s25_판정'), write(join(div(rounded(div(V('s25_H'), 10)), 10), 'm')), show(), wait(0.9), hide())
    u = V('s25_u')
    arc = lambda Hv: add(add(HIGH, mul(LOW - HIGH, u)), mul(mul(Hv, VS * 4), mul(u, sub(1, u))))
    flight = lambda Hv, foot: [setv('s25_t0', timer()), setv('s25_T', add(0.5, mul(V(Hv), 0.0045))),
                               setv('s25_착지', add(V('s25_t0'), V('s25_T'))), setv('s25_u', 0),
                               until(or_(ge(V('s25_u'), 1), eq(V('게임중'), 0)),
                                     setv('s25_u', div(sub(timer(), V('s25_t0')), V('s25_T'))),
                                     if_(gt(V('s25_u'), 1), setv('s25_u', 1)), setv(foot, arc(V(Hv)))),
                               setv(foot, LOW)]
    mgr = hidden(m, '널담당')
    mgr.on(on_key(K_SPACE), if_(and_(eq(V('s25_대기'), 1), eq(V('s25_눌림'), 0)),
                                ifelse(lt(timer(), sub(V('s25_착지'), 0.3)), [setv('s25_눌림', 2)],
                                       [setv('s25_눌림', 1), setv('s25_누른때', timer())]), cast('s25_쿵')))
    mgr.on(on_msg('게임시작'), setv('s25_H', 40), setv('s25_Hp', 40),
           until(eq(V('게임중'), 0),
                 # 상대가 뛰는 동안: 내려오는 순간에 맞춰 SPACE
                 setv('s25_눌림', 0), setv('s25_대기', 1), setv('s25_상태', 1), cast('s25_상대뜀'),
                 *flight('s25_Hp', 's25_상대발'),
                 wait_until(or_(ne(V('s25_눌림'), 0), gt(timer(), add(V('s25_착지'), 0.2)))),
                 setv('s25_대기', 0),
                 setv('_ma', abs_(sub(V('s25_누른때'), V('s25_착지')))),
                 ifelse(eq(V('s25_눌림'), 1),
                        [ifelse(lt(V('_ma'), 0.08), [setv('_mv', 1), chg('s25_H', 24)],
                                [ifelse(lt(V('_ma'), 0.17), [setv('_mv', 2), chg('s25_H', 6)], [setv('_mv', 3), chg('s25_H', -10)])])],
                        [ifelse(eq(V('s25_눌림'), 2), [setv('_mv', 4)], [setv('_mv', 5)]), setv('s25_H', mul(V('s25_H'), 0.5))]),
                 *clamp_('s25_H', 15, 170),
                 chg('합계', sub(V('s25_H'), 15)), if_(gt(V('s25_H'), V('s25_최고')), setv('s25_최고', V('s25_H'))),
                 cast('s25_판정'),
                 setv('미니표시', join('최고 ', div(rounded(div(V('s25_최고'), 10)), 10), 'm')),
                 # 내가 뛴다
                 setv('s25_상태', 2), cast('s25_내뜀'),
                 *flight('s25_H', 's25_내발'),
                 setv('s25_Hp', add(mul(V('s25_H'), 0.85), 8))))
    mgr.on(on_msg('시간끝'), setv('s25_대기', 0), *m.end_blocks(div(V('합계'), 13)))
    judge_pop(m, '널판정', [('최고!', 30, 'royal'), ('좋아!', 26, 'green'), ('아쉬워!', 24, 'white'),
                         ('너무 빨라요!', 22, 'red'), ('놓쳤다!', 24, 'red')], 0, 48, 's25_판정', hold=0.35)
    tip = m.T('널안내', '상대(빨강)가 널에 닿는 순간 SPACE!', 0, 84, 10, C_WHITE, F_BODY, True, 0, w=250, h=16, bg=C_BOX)
    tip.on(on_msg('s25_판정'), hide())
    m.on_start(setv('합계', 0), setv('s25_최고', 0), setv('s25_대기', 0), setv('s25_내발', LOW), setv('s25_상대발', LOW),
               setv('s25_H', 40), setv('s25_눌림', 0), setv('s25_착지', 999))
    m.snd('s25_쿵', play('hit'))
    m.snd('s25_내뜀', play('jump'))
    m.snd('s25_판정', ifelse(le(V('_mv'), 2), [play('good')], [ifelse(eq(V('_mv'), 3), [play('pop')], [play('bad')])]))
    m.finish('2번 후보와 널뛰기 한판! 상대가 널에 내려앉는 순간\nSPACE 를 누르면 내가 더 높이 올라가요. 박자가 생명!',
             '조작: SPACE (너무 빠르거나 늦으면 낮아져요)  ·  25초, 높이 뛸수록 점수 UP')
    return True


# ================================================================== 26. 미아 찾기 (사람 찾기)
S26_HATW = ['모자를 안 썼어요', '빨간 모자를 썼어요', '노란 모자를 썼어요', '파란 모자를 썼어요']
S26_SHIRTW = ['빨간 옷을 입었어요', '초록 옷을 입었어요', '노란 옷을 입었어요', '파란 옷을 입었어요']
S26_ITEMW = ['손에 아무것도 없어요', '풍선을 들고 있어요', '아이스크림을 들고 있어요', '가방을 메고 있어요']


@game(26)
def g26(P, ctx):
    R, VAR, NP = 5, 3, 21
    rng = random.Random(2626)
    combo = lambda h, s, i: h * 16 + s * 4 + i + 1
    people, targets, c1, c2, c3 = [], [], [], [], []
    for r in range(R):
        for v in range(VAR):
            th, ts, ti = rng.randrange(4), rng.randrange(4), rng.randrange(4)
            tgt = combo(th, ts, ti)
            others = []
            near = 7 + r * 2          # 라운드가 갈수록 비슷한 아이가 많아진다
            while len(others) < NP - 1:
                if len(others) < near:      # 두 가지만 같은 아이
                    h, s, i = th, ts, ti
                    k = rng.randrange(3)
                    if k == 0:
                        h = rng.choice([x for x in range(4) if x != th])
                    elif k == 1:
                        s = rng.choice([x for x in range(4) if x != ts])
                    else:
                        i = rng.choice([x for x in range(4) if x != ti])
                else:
                    h, s, i = rng.randrange(4), rng.randrange(4), rng.randrange(4)
                c = combo(h, s, i)
                if c != tgt:
                    others.append(c)
            lst = others + [tgt]
            rng.shuffle(lst)
            people += lst
            targets.append(tgt)
            c1.append(S26_HATW[th])
            c2.append(S26_SHIRTW[ts])
            c3.append(S26_ITEMW[ti])
    m = mg(P, ctx, T, 26, time_limit=60, status='찾은 아이 0/%d' % R, dim=60)
    vars_(P, 's26_판', 's26_목표', 's26_대기', 's26_찾음', 's26_속도')
    P.list('s26_사람', people)
    P.list('s26_목표들', targets)
    P.list('s26_단서1', c1)
    P.list('s26_단서2', c2)
    P.list('s26_단서3', c3)
    # 엄마와 단서 말풍선
    mom = m.S('엄마', AC.s26_mom(), -206, 40)
    mom.on(on_msg('s26_새판'), rep(3, mvy(4), wait(0.05), mvy(-4), wait(0.05)))
    panel(P, m.sc, '단서판', -60, 66, 250, 72, 'glass', header='red')
    m.T('단서제목', '엄마: "우리 아이를 찾아 주세요!"', -60, 90, 10, C_WHITE, F_NUM, False, 0, w=230, h=15)
    for k in range(3):
        t_ = m.T('단서%d' % (k + 1), ' ', -60, 70 - k * 15, 10, C_WHITE, F_BODY, True, 0, w=230, h=14)
        t_.on(on_msg('s26_새판'), write(join('· ', LGET('s26_단서%d' % (k + 1), V('s26_판')))))
    # 군중 (복제본 21명)
    pics = [('c%d%d%d' % (h, s, i), AC.s26_kid(h, s, i)) for h in range(4) for s in range(4) for i in range(4)]
    kid = m.S('아이', pics, 0, -300, scale=1.1, visible=False)
    for v in ('k', 'c', 'vx', 'vy', '복제'):
        kid.local(v, 0)
    kid.on(on_msg('게임시작'), *[flat(setv('k', k + 1), clone_self()) for k in range(NP)])
    kid.on(on_clone(), setv('복제', 1),
           until(eq(V('게임중'), 0),
                 if_(le(rnd(1, 100), 3), setv('vx', mul(div(rnd(-10, 10), 10), V('s26_속도'))),
                     setv('vy', mul(div(rnd(-10, 10), 10), mul(V('s26_속도'), 0.6)))),
                 mvx(V('vx')), mvy(V('vy')),
                 if_(lt(obj_x(), -150), lx(-150), setv('vx', abs_(V('vx')))), if_(gt(obj_x(), 222), lx(222), setv('vx', mul(abs_(V('vx')), -1))),
                 if_(lt(obj_y(), -110), ly(-110), setv('vy', abs_(V('vy')))), if_(gt(obj_y(), 8), ly(8), setv('vy', mul(abs_(V('vy')), -1)))),
           del_clone())
    kid.on(on_msg('s26_새판'), if_(eq(V('복제'), 1),
                                setv('c', LGET('s26_사람', add(mul(sub(V('s26_판'), 1), NP), V('k')))), shape(V('c')),
                                fx('color', 0), fx('brightness', 0),
                                xy(add(-146, mul(mod(sub(V('k'), 1), 7), 60)), add(-104, mul(floor(div(sub(V('k'), 1), 7)), 50))),
                                mvx(rnd(-14, 14)), mvy(rnd(-10, 10)), setv('vx', 0), setv('vy', 0), show()))
    kid.on(on_click(), if_(and_(eq(V('복제'), 1), and_(eq(V('s26_대기'), 1), eq(V('게임중'), 1))),
                           ifelse(eq(V('c'), V('s26_목표')),
                                  [setv('s26_대기', 0), setv('s26_찾음', 1), setv('_mv', 1), cast('s26_판정'),
                                   rep(3, mvy(8), wait(0.04), mvy(-8), wait(0.04))],
                                  [chg('틀림', 1), setv('_mv', 2), cast('s26_판정'), fx('brightness', -40),
                                   rep(3, mvx(3), wait(0.03), mvx(-3), wait(0.03))])))
    judge_pop(m, '미아판정', [('찾았다!', 30, 'green'), ('우리 애가 아니에요!', 20, 'red')], 40, 30, 's26_판정', hold=0.4)
    mgr = hidden(m, '미아담당')
    score = add(sub(mul(V('맞춤'), 16), mul(V('틀림'), 4)), mul(V('남은시간'), 0.34))
    mgr.on(on_msg('게임시작'), setv('라운드', 1), wait(0.1),
           until(or_(gt(V('라운드'), R), eq(V('게임중'), 0)),
                 setv('s26_판', add(mul(sub(V('라운드'), 1), VAR), rnd(1, VAR))),
                 setv('s26_목표', LGET('s26_목표들', V('s26_판'))), setv('s26_속도', add(0.15, mul(V('라운드'), 0.12))),
                 setv('s26_찾음', 0), cast('s26_새판'), setv('s26_대기', 1),
                 setv('미니표시', join('찾은 아이 ', V('맞춤'), '/', R, ' · ', V('라운드'), '번째')),
                 wait_until(or_(eq(V('s26_찾음'), 1), eq(V('게임중'), 0))),
                 if_(eq(V('s26_찾음'), 1), chg('맞춤', 1), wait(1.1)),
                 chg('라운드', 1)),
           setv('미니표시', join('찾은 아이 ', V('맞춤'), '/', R)),
           *m.end_blocks(score))
    mgr.on(on_msg('시간끝'), setv('s26_대기', 0), *m.end_blocks(score))
    m.on_start(setv('맞춤', 0), setv('틀림', 0), setv('s26_대기', 0), setv('s26_판', 1), setv('s26_속도', 0))
    m.snd('s26_판정', ifelse(eq(V('_mv'), 1), [play('good')], [play('bad')]))
    m.finish('엄마가 알려 준 세 가지 단서(모자·옷·손에 든 것)에\n모두 맞는 아이는 딱 한 명! 찾아서 클릭하세요. (5명)',
             '조작: 마우스 클릭  ·  잘못 누르면 감점, 빨리 찾을수록 보너스')
    return True


# ================================================================== 27. 과일 저울 맞추기 (무게 맞추기)
S27_NAMES = ['귤', '사과', '복숭아', '배', '포도']
S27_W = [100, 250, 300, 400, 500]


def _s27_orders():
    rng = random.Random(2727)
    tg, st = [], []
    for o in range(5):
        for v in range(3):
            while True:
                stock = [rng.randint(0, 1 if o >= 2 else 2)] + [rng.randint(1, 3) for _ in range(4)]
                pool = [k for k in range(5) for _ in range(stock[k])]
                n = rng.randint(3, min(len(pool), 4 + o // 2))
                pick = rng.sample(pool, n)
                w = sum(S27_W[k] for k in pick)
                if 700 <= w <= 1950:
                    break
            tg.append(w)
            st += stock
    return tg, st


@game(27)
def g27(P, ctx):
    NO, NS = 5, 10
    tg, st = _s27_orders()
    m = mg(P, ctx, T, 27, time_limit=75, status='주문 1/%d' % NO, dim=70)
    vars_(P, 's27_목표', 's27_무게', 's27_주문', 's27_판', 's27_대기', 's27_새칸', 's27_새종류', 's27_각', 's27_글', 's27_끝')
    P.list('s27_목표표', tg)
    P.list('s27_재고표', st)
    P.list('s27_재고', [0] * 5)
    P.list('s27_무게표', S27_W)
    P.list('s27_접시', [0] * NS)
    SX, SY = 142, -36
    fmt = lambda var: [ifelse(ge(V(var), 1000),
                              [setv('s27_글', join(floor(div(V(var), 1000)), ',', substr(add(1000, mod(V(var), 1000)), 2, 4), ' g'))],
                              [setv('s27_글', join(V(var), ' g'))])]
    # 주문서
    panel(P, m.sc, '주문판', -120, 66, 236, 64, 'glass', header='royal')
    on_ = m.T('주문번호', ' ', -120, 88, 10, C_WHITE, F_NUM, False, 0, w=220, h=14)
    on_.on(on_msg('s27_새주문'), write(join('주문 ', V('s27_주문'), '/', NO, ' · 이 무게로 담아 주세요!')))
    ow = m.T('주문무게', ' ', -120, 60, 22, C_ACC, F_NUM, False, 0, w=200, h=30)
    ow.on(on_msg('s27_새주문'), *fmt('s27_목표'), write(V('s27_글')))
    # 선반 (과일 5종)
    pos = [(-196, 0), (-128, 0), (-60, 0), (-162, -74), (-94, -74)]
    for k in range(5):
        x, y = pos[k]
        bg_ = m.S('선반%d' % k, K.panel(64, 66, 'card'), x, y)
        ic = m.S('과일칸%d' % k, AC.s27_fruit(k, 30), x, y + 10)
        m.T('과일이름%d' % k, '%s %dg' % (S27_NAMES[k], S27_W[k]), x, y - 12, 9, C_WHITE, F_BODY, True, 0, w=64, h=13)
        cnt = m.T('재고%d' % k, ' ', x + 20, y + 22, 9, C_ACC, F_NUM, False, 0, w=30, h=13)
        cnt.on(on_msg('s27_갱신'), write(join('×', LGET('s27_재고', k + 1))))
        for o in (bg_, ic):
            o.on(on_msg('s27_갱신'), ifelse(eq(LGET('s27_재고', k + 1), 0), [fx('brightness', -45)], [fx('brightness', 0)]))
        find = [setv('s27_새칸', 0)] + [if_(eq(LGET('s27_접시', j), 0), setv('s27_새칸', j)) for j in range(NS, 0, -1)]
        add_ = [if_(and_(eq(V('s27_대기'), 1), gt(LGET('s27_재고', k + 1), 0)),
                    *find,
                    if_(gt(V('s27_새칸'), 0),
                        lst_set('s27_접시', V('s27_새칸'), k + 1), lst_set('s27_재고', k + 1, sub(LGET('s27_재고', k + 1), 1)),
                        chg('s27_무게', S27_W[k]), setv('s27_새종류', k + 1), cast('s27_올림'), cast('s27_갱신')))]
        for o in (bg_, ic):
            o.on(on_click(), *add_)
        ic.on(on_click(), ic.pct(85), wait(0.06), ic.pct(100))
        G.hover_scripts(ic, 112)
    # 저울
    m.S('저울', AC.s27_scale(), SX, SY)
    tm = m.S('목표표시', AC.s27_tmark(), SX, SY - 20)
    tm.on(on_msg('s27_새주문'), rot(add(-135, mul(V('s27_목표'), 0.135))))
    nd = m.S('바늘', AC.s27_needle(), SX, SY - 20)
    nd.on(on_scene(), rot(-135), setv('s27_각', -135))
    nd.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                   setv('_ma', add(-135, mul(V('s27_무게'), 0.135))), if_(gt(V('_ma'), 140), setv('_ma', 140)),
                                   if_(gt(abs_(sub(V('_ma'), V('s27_각'))), 0.3),
                                       chg('s27_각', mul(sub(V('_ma'), V('s27_각')), 0.25)), rot(V('s27_각'))), wait(0.016)))
    # 접시 위 과일 (복제본: 누르면 빠진다)
    fr = m.S('접시과일', [('f%d' % (k + 1), AC.s27_fruit(k, 22)) for k in range(5)], 0, -300, visible=False)
    for v in ('slot', 'kind', '복제'):
        fr.local(v, 0)
    fr.on(on_msg('s27_올림'), if_(eq(V('복제'), 0), setv('slot', V('s27_새칸')), setv('kind', V('s27_새종류')), clone_self()))
    fr.on(on_clone(), setv('복제', 1), shape(V('kind')),
          xy(add(SX - 36, mul(mod(sub(V('slot'), 1), 5), 18)), add(SY + 140, mul(floor(div(sub(V('slot'), 1), 5)), 15))), show(),
          glide(0.15, add(SX - 36, mul(mod(sub(V('slot'), 1), 5), 18)), add(SY + 74, mul(floor(div(sub(V('slot'), 1), 5)), 15))))
    fr.on(on_click(), if_(and_(eq(V('복제'), 1), eq(V('s27_대기'), 1)),
                          lst_set('s27_접시', V('slot'), 0), lst_set('s27_재고', V('kind'), add(LGET('s27_재고', V('kind')), 1)),
                          chg('s27_무게', mul(-1, LGET('s27_무게표', V('kind')))), cast('s27_갱신'), cast('s27_뺌'), del_clone()))
    fr.on(on_msg('s27_비움'), if_(eq(V('복제'), 1), del_clone()))
    fr.on(on_msg('s27_포장됨'), if_(eq(V('복제'), 1), glide(0.3, 40, -150), del_clone()))
    # 무게 표시 + 버튼
    rd = m.T('현재무게', ' ', 40, -46, 14, C_WHITE, F_NUM, False, 0, w=110, h=20, bg=C_BOX)
    rd.on(on_msg('s27_갱신'), *fmt('s27_무게'), write(V('s27_글')),
          ifelse(eq(V('s27_무게'), V('s27_목표')), [text_color('#6EF2A0')],
                 [ifelse(gt(V('s27_무게'), V('s27_목표')), [text_color('#FF7A8A')], [text_color('#FFFFFF')])]))
    m.T('현재무게글', '저울 무게', 40, -28, 8, C_DIM, F_BODY, True, 0, w=80, h=12)
    pack = [if_(and_(eq(V('s27_대기'), 1), gt(V('s27_무게'), 0)),
                ifelse(eq(V('s27_무게'), V('s27_목표')), [setv('s27_대기', 0), setv('s27_끝', 1)],
                       [chg('틀림', 1), setv('_mv', 2), cast('s27_판정')]))]
    button(P, m.sc, '포장버튼', '포장하기', 40, -78, 96, 26, 'green', actions=pack)
    clear = [if_(eq(V('s27_대기'), 1),
                 *[lst_set('s27_재고', k + 1, LGET('s27_재고표', add(mul(sub(V('s27_판'), 1), 5), k + 1))) for k in range(5)],
                 *[lst_set('s27_접시', j, 0) for j in range(1, NS + 1)], setv('s27_무게', 0), cast('s27_비움'), cast('s27_갱신'))]
    button(P, m.sc, '비우기버튼', '모두 빼기', 40, -108, 96, 24, 'steel', actions=clear)
    judge_pop(m, '저울판정', [('포장 완료!', 28, 'green'), ('무게가 달라요!', 24, 'red')], 40, 20, 's27_판정', hold=0.5)
    mgr = hidden(m, '저울담당')
    score = add(sub(mul(V('맞춤'), 16), mul(V('틀림'), 3)), mul(V('남은시간'), 0.27))
    mgr.on(on_msg('게임시작'), setv('s27_주문', 1),
           until(or_(gt(V('s27_주문'), NO), eq(V('게임중'), 0)),
                 setv('s27_판', add(mul(sub(V('s27_주문'), 1), 3), rnd(1, 3))),
                 setv('s27_목표', LGET('s27_목표표', V('s27_판'))),
                 *[lst_set('s27_재고', k + 1, LGET('s27_재고표', add(mul(sub(V('s27_판'), 1), 5), k + 1))) for k in range(5)],
                 *[lst_set('s27_접시', j, 0) for j in range(1, NS + 1)], setv('s27_무게', 0), setv('s27_끝', 0),
                 setv('미니표시', join('주문 ', V('s27_주문'), '/', NO, ' · 완료 ', V('맞춤'))),
                 cast('s27_새주문'), cast('s27_갱신'), setv('s27_대기', 1),
                 wait_until(or_(eq(V('s27_끝'), 1), eq(V('게임중'), 0))),
                 if_(eq(V('s27_끝'), 1), chg('맞춤', 1), setv('_mv', 1), cast('s27_판정'), cast('s27_포장됨'), wait(0.9)),
                 chg('s27_주문', 1)),
           setv('미니표시', join('완료 ', V('맞춤'), '/', NO)),
           *m.end_blocks(score))
    mgr.on(on_msg('시간끝'), setv('s27_대기', 0), *m.end_blocks(score))
    m.on_start(setv('맞춤', 0), setv('틀림', 0), setv('s27_대기', 0), setv('s27_무게', 0), setv('s27_목표', 0),
               *[lst_set('s27_재고', k + 1, 0) for k in range(5)])
    m.snd('s27_올림', play('pop'))
    m.snd('s27_뺌', play('tick'))
    m.snd('s27_판정', ifelse(eq(V('_mv'), 1), [play('cash')], [play('bad')]))
    m.finish('주문 무게와 딱 맞게 과일을 저울에 올리고 포장하세요!\n과일마다 무게가 달라요. 남은 개수(×)도 잘 보세요. (5주문)',
             '조작: 선반 과일 클릭 = 올리기 · 저울 위 과일 클릭 = 빼기 · 포장하기')
    return True


# ================================================================== 28. 숲길 기억 (길 기억)
def _s28_paths():
    rng = random.Random(2828)
    C, R = 7, 5
    out = []
    for lv, (lo, hi) in enumerate(((9, 11), (12, 14), (15, 18))):
        got = []
        while len(got) < 4:
            r0 = rng.randrange(R)
            path = [(0, r0)]
            ok = False
            for _ in range(60):
                c, r = path[-1]
                if c == C - 1:
                    ok = True
                    break
                moves = [(1, 0)] * 2 + [(0, 1), (0, -1)] * (2 + lv) + ([(-1, 0)] if lv == 2 and c > 1 else [])
                rng.shuffle(moves)
                for dc, dr in moves:
                    nc, nr = c + dc, r + dr
                    if not (0 <= nc < C and 0 <= nr < R) or (nc, nr) in path:
                        continue
                    if any(abs(nc - pc) + abs(nr - pr) == 1 for (pc, pr) in path[:-1]):
                        continue
                    path.append((nc, nr))
                    break
                else:
                    break
            if ok and lo <= len(path) <= hi and path not in got:
                got.append(path)
        out += got
    return out


@game(28)
def g28(P, ctx):
    C, R, CS, NL = 7, 5, 36, 3
    paths = _s28_paths()
    cell_list, order_list, lens = [], [], []
    for p in paths:
        cells = [0] * (C * R)
        for k, (c, r) in enumerate(p):
            cells[r * C + c] = k + 1
        cell_list += cells
        order_list += [r * C + c + 1 for (c, r) in p] + [0] * (20 - len(p))
        lens.append(len(p))
    GX, GY = 0, -16
    X = lambda c: add(GX - 3 * CS, mul(c, CS))
    Y = lambda r: sub(GY + 2 * CS, mul(r, CS))
    m = mg(P, ctx, T, 28, time_limit=90, status='숲길 1/%d' % NL, dim=60)
    vars_(P, 's28_판', 's28_c', 's28_r', 's28_nc', 's28_nr', 's28_dc', 's28_dr', 's28_v', 's28_L', 's28_움직임', 's28_대기',
          's28_통과', 's28_레벨', 's28_보기')
    P.list('s28_칸', cell_list)
    P.list('s28_순서', order_list)
    P.list('s28_길이', lens)
    m.S('숲바닥', AC.s28_floor(C, R, CS), GX, GY)
    # 길 표시 돌 (복제본 20개, 미리 보기 때 순서대로 나타남)
    st = m.S('징검돌', AC.s28_stone(), 0, -300, visible=False)
    for v in ('k', '복제'):
        st.local(v, 0)
    st.on(on_msg('게임시작'), *[flat(setv('k', k + 1), clone_self()) for k in range(20)])
    cellno = LGET('s28_순서', add(mul(sub(V('s28_판'), 1), 20), V('k')))
    st.on(on_msg('s28_보기'), if_(and_(eq(V('복제'), 1), le(V('k'), V('s28_L'))),
                               xy(X(mod(sub(cellno, 1), C)), Y(floor(div(sub(cellno, 1), C)))),
                               wait(mul(V('k'), 0.08)), if_(eq(V('s28_보기'), 1), show())))
    st.on(on_msg('s28_숨김'), hide())
    dark = m.S('어둠', AC.s28_dark(), 0, 0, visible=False)
    pl = m.S('나', ctx['PORT']['me'], 0, 0, scale=1.15)
    pl.on(on_scene(), hide())
    ex = m.S('출구판', AC.s28_sign('출구', (30, 150, 80)), 0, 0, visible=False)
    last = LGET('s28_순서', add(mul(sub(V('s28_판'), 1), 20), V('s28_L')))
    ex.on(on_msg('s28_새길'), xy(add(X(mod(sub(last, 1), C)), 30), add(Y(floor(div(sub(last, 1), C))), 6)), show())
    dark.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                    ifelse(eq(V('s28_보기'), 1), [hide()], [show(), xy(obj_x(pl.name), obj_y(pl.name))]),
                                    wait(0.016)), hide())
    first = LGET('s28_순서', add(mul(sub(V('s28_판'), 1), 20), 1))
    pl.on(on_msg('s28_새길'), setv('s28_c', mod(sub(first, 1), C)), setv('s28_r', floor(div(sub(first, 1), C))),
          xy(X(V('s28_c')), Y(V('s28_r'))), show())
    pl.on(on_msg('s28_이동'),
          setv('s28_nc', add(V('s28_c'), V('s28_dc'))), setv('s28_nr', add(V('s28_r'), V('s28_dr'))),
          if_(and_(and_(ge(V('s28_nc'), 0), lt(V('s28_nc'), C)), and_(ge(V('s28_nr'), 0), lt(V('s28_nr'), R))),
              setv('s28_v', LGET('s28_칸', add(mul(sub(V('s28_판'), 1), C * R), mul(V('s28_nr'), C), V('s28_nc'), 1))),
              glide(0.1, X(V('s28_nc')), Y(V('s28_nr'))),
              ifelse(gt(V('s28_v'), 0),
                     [setv('s28_c', V('s28_nc')), setv('s28_r', V('s28_nr')), cast('s28_발'),
                      if_(eq(V('s28_v'), V('s28_L')), setv('s28_통과', 1))],
                     [chg('틀림', 1), setv('_mv', 2), cast('s28_판정'), wait(0.4),
                      glide(0.15, X(V('s28_c')), Y(V('s28_r'))), cast('s28_잠깐')])),
          setv('s28_움직임', 0))
    keys = hidden(m, '숲길키')
    for kc, dc, dr in ((K_LEFT, -1, 0), (K_RIGHT, 1, 0), (K_UP, 0, -1), (K_DOWN, 0, 1)):
        keys.on(on_key(kc), if_(and_(eq(V('s28_대기'), 1), eq(V('s28_움직임'), 0)),
                                setv('s28_움직임', 1), setv('s28_dc', dc), setv('s28_dr', dr), cast('s28_이동')))
    keys.on(on_msg('s28_잠깐'), setv('s28_보기', 1), cast('s28_보기'), wait(0.9), setv('s28_보기', 0), cast('s28_숨김'))
    info = m.T('숲길안내', ' ', 0, 86, 11, C_WHITE, F_NUM, False, 0, w=300, h=16, bg=C_BOX)
    info.on(on_msg('s28_외워'), write('길을 잘 외우세요!'), text_color('#FFE08A'))
    info.on(on_msg('s28_출발'), write('어두워졌어요! 방향키로 출구까지'), text_color('#FFFFFF'))
    judge_pop(m, '숲길판정', [('숲을 빠져나왔다!', 26, 'green'), ('길을 잃었어요!', 24, 'red')], 0, 40, 's28_판정', hold=0.45)
    mgr = hidden(m, '숲길담당')
    score = add(sub(mul(V('맞춤'), 30), mul(V('틀림'), 4)), mul(V('남은시간'), 0.2))
    mgr.on(on_msg('게임시작'), setv('s28_레벨', 1), wait(0.1),
           until(or_(gt(V('s28_레벨'), NL), eq(V('게임중'), 0)),
                 setv('s28_판', add(mul(sub(V('s28_레벨'), 1), 4), rnd(1, 4))), setv('s28_L', LGET('s28_길이', V('s28_판'))),
                 setv('s28_통과', 0), setv('s28_대기', 0),
                 setv('미니표시', join('숲길 ', V('s28_레벨'), '/', NL)),
                 cast('s28_새길'), setv('s28_보기', 1), cast('s28_보기'), cast('s28_외워'),
                 wait(add(1.6, mul(V('s28_L'), 0.12))),
                 setv('s28_보기', 0), cast('s28_숨김'), cast('s28_출발'), setv('s28_대기', 1),
                 wait_until(or_(eq(V('s28_통과'), 1), eq(V('게임중'), 0))),
                 setv('s28_대기', 0),
                 if_(eq(V('s28_통과'), 1), chg('맞춤', 1), setv('_mv', 1), cast('s28_판정'),
                     setv('s28_보기', 1), cast('s28_보기'), wait(1.2), cast('s28_숨김')),
                 chg('s28_레벨', 1)),
           *m.end_blocks(score))
    mgr.on(on_msg('시간끝'), setv('s28_대기', 0), *m.end_blocks(score))
    m.on_start(setv('맞춤', 0), setv('틀림', 0), setv('s28_대기', 0), setv('s28_보기', 1), setv('s28_판', 1), setv('s28_L', 0))
    m.snd('s28_발', play('tick'))
    m.snd('s28_판정', ifelse(eq(V('_mv'), 1), [play('fanfare')], [play('bad')]))
    m.snd('s28_외워', play('shutter'))
    m.finish('잠깐 보이는 징검돌 길을 외우세요! 곧 숲이 어두워져요.\n방향키로 기억한 길만 밟아 출구까지! (숲길 3개)',
             '조작: ← ↑ → ↓ 방향키  ·  길 밖을 밟으면 감점 + 원래 자리로')
    return True


# ================================================================== 29. 모내기 (간격 맞추기)
@game(29)
def g29(P, ctx):
    ROWS = [44, -8, -60]
    SPD = [78, 98, 122]
    xs = [[-180 + 45 * i for i in range(9)]]
    for start, gaps in ((-184, [36, 52, 40, 58, 38, 50, 44, 56]), (-190, [32, 60, 36, 64, 30, 58, 40, 62])):
        row = [start]
        for g_ in gaps:
            row.append(row[-1] + g_)
        xs.append(row)
    NM = 9
    TOT = NM * 3
    OFF = 30            # 이앙기 가운데에서 심는 곳까지
    m = mg(P, ctx, T, 29, status='1번째 줄 · 0점', dim=50)
    vars_(P, 's29_줄', 's29_px', 's29_표', 's29_t0', 's29_d', 's29_등급', 's29_쉼', 's29_진행', 's29_y')
    P.list('s29_표시', [x for row in xs for x in row] + [999])
    for y in ROWS:
        m.S('논줄', AC.s29_row(), 0, y)
    mark = m.S('표시선', AC.s29_mark(), 0, -300, visible=False)
    mark.on(on_scene(), pen_clear(),
            *[flat(xy(xs[r][k], ROWS[r] + 3), show(), stamp()) for r in range(3) for k in range(NM)], hide())
    seed = m.S('모', [('a', AC.s29_seed(0)), ('b', AC.s29_seed(1)), ('c', AC.s29_seed(2))], 0, -300, visible=False)
    seed.on(on_scene(), pen_clear(), hide())
    seed.on(on_msg('s29_심기'), shape(V('s29_등급')), xy(V('s29_px'), add(V('s29_y'), 2)), show(), stamp(), hide())
    pl = m.S('이앙기', AC.s29_planter(), -260, ROWS[0])
    ptr = m.S('심는곳', AC.s29_pointer(), -300, -300)
    nxt = LGET('s29_표시', add(mul(sub(V('s29_줄'), 1), NM), V('s29_표')))
    judge_mark = [setv('s29_d', abs_(sub(V('s29_px'), nxt)))]
    pl.on(on_msg('게임시작'), setv('s29_줄', 1),
          until(or_(gt(V('s29_줄'), 3), eq(V('게임중'), 0)),
                setv('s29_y', LGET('s29_y표', V('s29_줄'))), setv('s29_표', 1), setv('s29_t0', timer()),
                setv('미니표시', join(V('s29_줄'), '번째 줄 · ', rounded(V('합계')), '점')),
                setv('s29_진행', 1), cast('s29_새줄'),
                until(or_(gt(V('s29_px'), 236), eq(V('게임중'), 0)),
                      setv('s29_px', add(-250 + OFF, mul(sub(timer(), V('s29_t0')), LGET('s29_속도', V('s29_줄'))))),
                      xy(add(V('s29_px'), OFF), V('s29_y')),
                      # 지나쳐 버린 표시는 놓침
                      if_(and_(le(V('s29_표'), NM), gt(sub(V('s29_px'), nxt), 16)),
                          chg('s29_표', 1), setv('_mv', 4), setv('_ma', V('s29_px')), cast('s29_판정'))),
                setv('s29_진행', 0), chg('s29_줄', 1), wait(0.6)),
          *m.end_blocks(mul(V('합계'), 100.0 / (TOT * 10))))
    P.list('s29_y표', ROWS)
    P.list('s29_속도', SPD)
    pl.on(on_msg('s29_새줄'), xy(-250 + 2 * OFF, V('s29_y')))
    ptr.on(on_msg('게임시작'), until(eq(V('게임중'), 0), xy(V('s29_px'), add(V('s29_y'), 21))), hide())
    plant = [if_(and_(eq(V('s29_진행'), 1), eq(V('s29_쉼'), 0)),
                 setv('s29_쉼', 1), *judge_mark, setv('_ma', V('s29_px')),
                 ifelse(and_(le(V('s29_표'), NM), le(V('s29_d'), 16)),
                        [ifelse(le(V('s29_d'), 4), [setv('_mv', 1), chg('합계', 10), setv('s29_등급', 1)],
                                [ifelse(le(V('s29_d'), 9), [setv('_mv', 2), chg('합계', 7), setv('s29_등급', 1)],
                                        [setv('_mv', 3), chg('합계', 4), setv('s29_등급', 2)])]),
                         chg('s29_표', 1)],
                        [setv('_mv', 5), chg('합계', -3), setv('s29_등급', 3)]),
                 cast('s29_심기'), cast('s29_판정'),
                 setv('미니표시', join(V('s29_줄'), '번째 줄 · ', rounded(V('합계')), '점')),
                 wait(0.12), setv('s29_쉼', 0))]
    hidden(m, '모내기키').on(on_key(K_SPACE), *plant)
    pop = m.S('모판정', [('j%d' % (k + 1), K.big_text(t_, 14, c_)) for k, (t_, c_) in
                        enumerate((('딱!', 'green'), ('좋아', 'royal'), ('삐뚤', 'white'), ('놓침', 'red'), ('엉뚱해요', 'red')))],
              0, -300, visible=False)
    pop.on(on_msg('s29_판정'), shape(V('_mv')), xy(V('_ma'), add(V('s29_y'), 28)), fx('transparency', 0), to_front(), show(),
           rep(8, mvy(1.5), fx_add('transparency', 8), wait(0.03)), hide())
    m.T('모안내', '노란 화살표가 표시선(깃발)에 닿을 때 SPACE!', 0, 84, 10, C_WHITE, F_BODY, True, 0, w=300, h=16, bg=C_BOX)
    m.on_start(setv('합계', 0), setv('s29_진행', 0), setv('s29_쉼', 0), setv('s29_px', -400), setv('s29_y', ROWS[0]))
    m.snd('s29_판정', ifelse(le(V('_mv'), 2), [play('pop')], [ifelse(eq(V('_mv'), 3), [play('tick')], [play('bad')])]))
    m.finish('이앙기가 지나가며 모를 심어요. 노란 화살표가 논의 표시선에\n닿는 순간 SPACE! 딱 맞을수록 점수 UP (3줄, 점점 빨라져요)',
             '조작: SPACE 로 모 심기  ·  표시선이 없는 곳에 심으면 감점')
    return True


# ================================================================== 30. 바람 활쏘기 (활쏘기)
@game(30)
def g30(P, ctx):
    N = 8
    TX, TY = 60, 26
    dists = [30, 30, 50, 50, 50, 70, 70, 70]
    scl = {30: 1.0, 50: 0.74, 70: 0.54}
    fac = {30: 1.0, 50: 1.4, 70: 1.8}
    m = mg(P, ctx, T, 30, time_limit=70, status='화살 1/%d · 0점' % N, dim=40)
    vars_(P, 's30_발', 's30_바람', 's30_배율', 's30_흐름', 's30_cx', 's30_cy', 's30_hx', 's30_hy', 's30_숨', 's30_흔들',
          's30_대기', 's30_끝', 's30_점')
    P.list('s30_거리', dists)
    P.list('s30_크기', [scl[d_] for d_ in dists])
    P.list('s30_흐름표', [fac[d_] for d_ in dists])
    tgt = m.S('과녁', AC.s30_target(), TX, TY - 19)
    tgt.on(on_msg('s30_새발'), tgt.pct(mul(V('s30_배율'), 100)), ly(sub(TY, mul(19, V('s30_배율')))))
    stuck = m.S('꽂힌화살', AC.s30_stuck(), 0, -300, visible=False)
    stuck.on(on_scene(), pen_clear(), hide())
    stuck.on(on_msg('s30_새발'), pen_clear())
    stuck.on(on_msg('s30_꽂힘'), xy(V('s30_hx'), V('s30_hy')), show(), stamp(), hide())
    dtxt = m.T('거리글', ' ', TX, 84, 11, C_WHITE, F_NUM, False, 0, w=120, h=16, bg=C_BOX)
    dtxt.on(on_msg('s30_새발'), write(join('과녁까지 ', LGET('s30_거리', V('s30_발')), 'm')))
    # 바람 깃발 + 나뭇잎
    flag = m.S('바람깃발', [('w%d' % k, AC.s30_flag(k - 5)) for k in range(11)], -170, -10)
    flag.on(on_msg('s30_새발'), shape(add(V('s30_바람'), 6)))
    flag.on(on_msg('게임시작'), until(eq(V('게임중'), 0), rot(mul(sin_(mul(timer(), 400)), mul(abs_(V('s30_바람')), 0.6))), wait(0.03)))
    wtxt = m.T('바람글', ' ', -170, -46, 11, C_WHITE, F_NUM, False, 0, w=110, h=16, bg=C_BOX)
    wtxt.on(on_msg('s30_새발'), ifelse(eq(V('s30_바람'), 0), [write('바람 없음')],
                                     [ifelse(gt(V('s30_바람'), 0), [write(join('바람 → ', V('s30_바람')))],
                                             [write(join('바람 ← ', abs_(V('s30_바람'))))])]))
    leaf = m.S('나뭇잎', AC.s30_leaf(), 0, -300, visible=False)
    leaf.local('복제', 0)
    leaf.on(on_msg('게임시작'), until(eq(V('게임중'), 0), if_(ne(V('s30_바람'), 0), clone_self()), wait(0.35)))
    leaf.on(on_clone(), setv('복제', 1), xy(mul(-250, div(V('s30_바람'), abs_(V('s30_바람')))), rnd(-100, 90)), show(),
            until(or_(gt(abs_(obj_x()), 252), eq(V('게임중'), 0)), mvx(mul(V('s30_바람'), 1.1)), mvy(sin_(mul(obj_x(), 4))), rot_by(9)),
            del_clone())
    # 화살 (날아가는 모습)
    arr = m.S('화살', AC.s30_arrow_fly(), 0, -130, visible=False)
    ring = div(fn('root', add(mul(sub(V('s30_hx'), TX), sub(V('s30_hx'), TX)), mul(sub(V('s30_hy'), TY), sub(V('s30_hy'), TY)))),
               mul(36, V('s30_배율')))
    arr.on(on_msg('s30_발사'), xy(0, -140), arr.pct(100), show(),
           rep(12, xy(add(0, mul(sub(V('s30_hx'), 0), div(V('_mi'), 12))), add(-140, mul(add(140, V('s30_hy')), div(V('_mi'), 12)))),
               chg('_mi', 1), arr.grow_pct(-6), wait(0.03)),
           hide(), cast('s30_꽂힘'),
           setv('_ma', ring),
           ifelse(lt(V('_ma'), 0.2), [setv('s30_점', 10)],
                  [ifelse(lt(V('_ma'), 0.4), [setv('s30_점', 8)],
                          [ifelse(lt(V('_ma'), 0.6), [setv('s30_점', 6)],
                                  [ifelse(lt(V('_ma'), 0.8), [setv('s30_점', 4)],
                                          [ifelse(lt(V('_ma'), 1.0), [setv('s30_점', 2)], [setv('s30_점', 0)])])])])]),
           chg('합계', V('s30_점')), setv('_mv', add(floor(div(sub(10, V('s30_점')), 2)), 1)), cast('s30_판정'),
           setv('s30_끝', 1))
    # 조준점: 마우스 + 숨 흔들림 (SPACE 로 숨 참기)
    ch = m.S('조준점', AC.s30_cross(), 0, 0, visible=False)
    ch.on(on_msg('게임시작'), show(),
          until(eq(V('게임중'), 0),
                ifelse(and_(key(K_SPACE), gt(V('s30_숨'), 0)), [setv('s30_흔들', 2), chg('s30_숨', -1.1)],
                       [setv('s30_흔들', 10), if_(lt(V('s30_숨'), 100), chg('s30_숨', 0.45))]),
                if_(lt(V('s30_숨'), 0), setv('s30_숨', 0)),
                setv('s30_cx', add(mouse_x(), mul(V('s30_흔들'), sin_(mul(timer(), 115))))),
                setv('s30_cy', add(mouse_y(), mul(mul(V('s30_흔들'), 0.8), sin_(add(mul(timer(), 77), 40))))),
                xy(V('s30_cx'), V('s30_cy'))),
          hide())
    bb = m.S('숨막대', K.bar_set('s30_breath', 80, 7, 'royal'), 182, -112)
    m.T('숨글', '숨 (SPACE)', 182, -100, 8, C_DIM, F_BODY, True, 0, w=80, h=12)
    bb.on(on_msg('게임시작'), until(eq(V('게임중'), 0), shape(add(floor(mul(V('s30_숨'), 0.4)), 1)), wait(0.08)))
    shoot = [if_(and_(eq(V('s30_대기'), 1), eq(V('게임중'), 1)),
                 setv('s30_대기', 0), setv('s30_hx', add(V('s30_cx'), V('s30_흐름'))), setv('s30_hy', V('s30_cy')),
                 setv('_mi', 1), cast('s30_발사'))]
    hidden(m, '활키').on(on_mouse_down(), *shoot)
    judge_pop(m, '활판정', [('10점!', 30, 'royal'), ('8점', 26, 'green'), ('6점', 24, 'white'), ('4점', 22, 'white'),
                         ('2점', 22, 'gray'), ('빗나감...', 22, 'red')], TX, -56, 's30_판정', hold=0.5)
    mgr = hidden(m, '활담당')
    mgr.on(on_msg('게임시작'), setv('s30_발', 1),
           until(or_(gt(V('s30_발'), N), eq(V('게임중'), 0)),
                 setv('s30_바람', rnd(-5, 5)), if_(eq(V('s30_발'), 1), setv('s30_바람', 2)),
                 setv('s30_배율', LGET('s30_크기', V('s30_발'))),
                 setv('s30_흐름', mul(mul(V('s30_바람'), 5), LGET('s30_흐름표', V('s30_발')))),
                 setv('미니표시', join('화살 ', V('s30_발'), '/', N, ' · ', V('합계'), '점')),
                 cast('s30_새발'), setv('s30_끝', 0), wait(0.3), setv('s30_대기', 1),
                 wait_until(or_(eq(V('s30_끝'), 1), eq(V('게임중'), 0))),
                 setv('미니표시', join('화살 ', V('s30_발'), '/', N, ' · ', V('합계'), '점')),
                 wait(0.9), chg('s30_발', 1)),
           *m.end_blocks(mul(V('합계'), 100.0 / (N * 10))))
    mgr.on(on_msg('시간끝'), setv('s30_대기', 0), *m.end_blocks(mul(V('합계'), 100.0 / (N * 10))))
    m.on_start(setv('합계', 0), setv('s30_대기', 0), setv('s30_숨', 100), setv('s30_바람', 0), setv('s30_배율', 1), setv('s30_발', 1))
    m.snd('s30_발사', play('jump'))
    m.snd('s30_꽂힘', play('hit'))
    m.snd('s30_판정', ifelse(le(V('_mv'), 2), [play('good')], [ifelse(eq(V('_mv'), 6), [play('bad')], [play('pop')])]))
    m.finish('화살은 바람 따라 옆으로 밀려요! 깃발을 보고 바람 반대쪽을\n겨누세요. 멀수록 더 많이 밀려요. (화살 8발)',
             '조작: 마우스로 조준, 클릭하면 발사  ·  SPACE 를 누르고 있으면 숨 참기 (덜 흔들림)')
    return True
