# -*- coding: utf-8 -*-
"""새 미니게임 25종 (유세지 16~40). 모두 기존 15종과 장르가 다르다.

공통 틀은 minigames.MG 를 그대로 쓴다 (소개 창 → 3·2·1 → 게임 → FINISH → 유세 결과).
"""
import random
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
import data as D
import mg_art as A
import mg_art2 as A2
from minigames import MG, clamp_blocks


def _vars(P, *names):
    for n in names:
        if n not in P.vars:
            P.var(n, 0)


def hidden(m, base):
    """보이지 않는 담당 오브젝트."""
    return m.T(base, '', -300, -300, 8, visible=False)


# ================================================================== 32. 폐교 방탈출 (어려움)
def g32(P, ctx):
    """잠긴 교실 탈출: 시계 → 서랍(시각 4자리) → 손전등 → 책장(빛나는 숫자) → 사물함(색 3개)
    → 열쇠·쪽지(앞 두 자리) + 휴지통 종이(뒤 두 자리 = 의자 다리 수) → 문. 정답은 매번 무작위."""
    TL = 180
    _vars(P, '방향', '창', '키대상', '선택템', '힌트수', '서랍열림', '비춤', '사물함열림', '휴지통뒤짐', '문풀림', '탈출',
          '시H', '시M', '쪽지수', '앞의자', '뒤의자', '다리수', '다이얼1', '다이얼2', '다이얼3', '틀린수')
    for v in ('키입력', '서랍코드', '문코드', '방글'):
        P.var(v, '')
    P.list('책색', [1, 2, 3, 4, 1])
    P.list('책표시', [0, 0, 0, 0, 0])       # 그 책에 빛나는 숫자 (0 이면 없음)
    P.list('사물함코드', [1, 2, 3])
    P.list('가방', [0, 0, 0, 0])
    m = MG(P, 32, ctx, time_limit=TL, status='단서를 찾아라', dim=0)
    sc = m.sc
    can = lambda: and_(eq(V('게임중'), 1), eq(V('창'), 0))
    say = lambda t: [setv('방글', t), cast('방말')]
    front, back = 1, 2

    def side(o, v, extra=None):
        cond = eq(V('방향'), v) if extra is None else and_(eq(V('방향'), v), extra)
        o.on(on_msg('방갱신'), ifelse(cond, [show()], [hide()]))
        o.on(on_scene(), hide())
        return o
    room = m.S('교실', [('front', A2.room_bg('front')), ('back', A2.room_bg('back'))], 0, 0)
    room.on(on_msg('방갱신'), ifelse(eq(V('방향'), front), [shape('front')], [shape('back')]))
    # ---------------- 앞쪽 벽: 칠판, 시계, 교탁 서랍, 문
    board = side(m.S('칠판', A.plain_rect(230, 92, (0, 0, 0, 1), 'hit_board'), -55, 53), front)
    clock = side(m.S('시계', A2.room_clock(), -205, 72), front)
    hh = side(m.S('시침', A2.room_hand('h'), -205, 72), front)
    mh = side(m.S('분침', A2.room_hand('m'), -205, 72), front)
    hh.on(on_msg('방갱신'), rot(add(mul(mod(V('시H'), 12), 30), mul(V('시M'), 0.5))))
    mh.on(on_msg('방갱신'), rot(mul(V('시M'), 6)))
    drawer = side(m.S('서랍', [('c', A2.room_drawer('closed')), ('o', A2.room_drawer('open'))], -55, -51), front)
    drawer.on(on_msg('방갱신'), ifelse(eq(V('서랍열림'), 1), [shape('o')], [shape('c')]))
    door = side(m.S('문', [('c', A2.room_door('closed')), ('o', A2.room_door('open'))], 165, 2), front)
    door.on(on_msg('방갱신'), ifelse(eq(V('탈출'), 1), [shape('o')], [shape('c')]))
    # ---------------- 뒤쪽 벽: 책장(색 책 5권), 창문, 사물함, 휴지통
    shelf = side(m.S('책장', A.plain_rect(146, 156, (0, 0, 0, 1), 'hit_shelf'), -143, 17), back)
    books = []
    for k in range(1, 6):
        bk = side(m.S('책%d' % k, [(c, A2.room_book(c)) for c in A2.ROOM_COL_NAMES], -196 + (k - 1) * 24, 73), back)
        bk.on(on_msg('방갱신'), shape(LGET('책색', k)))
        books.append(bk)
        mk = side(m.S('책숫자%d' % k, [('n%d' % n, A2.uv_mark(n)) for n in (1, 2, 3)], -196 + (k - 1) * 24, 76), back,
                  and_(eq(V('비춤'), 1), gt(LGET('책표시', k), 0)))
        mk.on(on_msg('방갱신'), if_(gt(LGET('책표시', k), 0), shape(LGET('책표시', k))))
    win = side(m.S('창문', A.plain_rect(130, 90, (0, 0, 0, 1), 'hit_window'), 25, 50), back)
    locker = side(m.S('사물함', [('c', A2.room_locker('closed')), ('o', A2.room_locker('open'))], 160, -2), back)
    locker.on(on_msg('방갱신'), ifelse(eq(V('사물함열림'), 1), [shape('o')], [shape('c')]))
    trash = side(m.S('휴지통', A2.room_trash(), 100, -46), back)
    cone = m.S('손전등빛', A2.flash_cone(), -143, 40, visible=False)
    cone.on(on_msg('비추기'), show(), fx('transparency', 0), wait(0.5), rep(10, fx_add('transparency', 10), wait(0.03)), hide())
    # ---------------- 의자 (앞 2~5개, 뒤 1~4개)
    for i, (x, y) in enumerate(((-215, -72), (-175, -78), (35, -76), (80, -72), (225, -76)), 1):
        side(m.S('앞의자%d' % i, A2.room_chair(), x, y), front, le(i, V('앞의자')))
    for i, (x, y) in enumerate(((-50, -74), (0, -80), (55, -72), (222, -78)), 1):
        side(m.S('뒤의자%d' % i, A2.room_chair(), x, y), back, le(i, V('뒤의자')))
    # ---------------- 가방
    def add_item(it):
        return [setv('_ma', 0), *[if_(and_(eq(V('_ma'), 0), eq(LGET('가방', k), 0)), lst_set('가방', k, it), setv('_ma', 1))
                                 for k in range(1, 5)], cast('가방갱신')]
    note_txt = join('쪽지: "문 비밀번호 앞 두 자리는 ', V('쪽지수'), '"')
    paper_txt = '구겨진 종이: "뒤 두 자리 = 이 교실 의자 다리 수 (앞뒤 모두)"'
    # ---------------- 클릭 반응
    board.on(on_click(), if_(can(), ifelse(eq(V('선택템'), 1), say('칠판을 비춰 봤지만 아무것도 없다. 다른 곳을 비춰 볼까?'),
                                           say('칠판: "서랍은 멈춘 시각을 기억한다 (시·분 네 자리)"'))))
    clock.on(on_click(), if_(can(), *say('시계가 멈춰 있다. 몇 시 몇 분일까?')))
    drawer.on(on_click(), if_(can(), ifelse(eq(V('서랍열림'), 0),
                                            [setv('키대상', 1), setv('키입력', ''), setv('창', 1), cast('번호창'),
                                             *say('서랍이 잠겨 있다. 네 자리 비밀번호!')],
                                            say('빈 서랍이다.'))))
    door.on(on_click(), if_(can(), ifelse(eq(V('문풀림'), 0),
                                          [ifelse(eq(V('선택템'), 2),
                                                  [setv('문풀림', 1), setv('선택템', 0), cast('가방갱신'), cast('철컥'),
                                                   *say('철컥! 열쇠로 자물쇠를 풀었다. 이제 번호판에 네 자리를!')],
                                                  say('문이 잠겨 있다. 열쇠 구멍과 번호판이 있다.'))],
                                          [setv('키대상', 2), setv('키입력', ''), setv('창', 1), cast('번호창'),
                                           *say('문 번호판: 네 자리 비밀번호')])))
    for bk in [shelf] + books:
        bk.on(on_click(), if_(can(), ifelse(eq(V('선택템'), 1),
                                            [setv('비춤', 1), cast('비추기'), cast('방갱신'),
                                             *say('책 세 권에 보라색 숫자 1, 2, 3 이 빛난다!')],
                                            [ifelse(eq(V('비춤'), 1), say('빛나는 숫자 1 → 2 → 3 ... 책 색깔에 뜻이 있을까?'),
                                                    say('오래된 책들이다. 표지 색이 제각각이다.'))])))
    win.on(on_click(), if_(can(), *say('밖은 캄캄하다. 달만 떠 있다.')))
    locker.on(on_click(), if_(can(), ifelse(eq(V('사물함열림'), 0),
                                            [setv('창', 2), cast('색창'), *say('색깔 자물쇠 세 칸이 달린 사물함이다.')],
                                            say('빈 사물함이다.'))))
    trash.on(on_click(), if_(can(), ifelse(eq(V('휴지통뒤짐'), 0),
                                           [setv('휴지통뒤짐', 1), *add_item(4), cast('찾음'), *say('휴지통에서 구겨진 종이를 찾았다! (가방에서 눌러 읽기)')],
                                           say('휴지통엔 더 이상 아무것도 없다.'))))
    # ---------------- 시점 화살표
    for sx, ang, nm in ((-226, 0, '왼쪽'), (226, 180, '오른쪽')):
        ar = m.S('시점' + nm, K.icon_img('back', 26), sx, 10)
        ar.on(on_scene(), rot(ang))
        G.hover_scripts(ar, 115)
        ar.on(on_click(), if_(can(), setv('방향', sub(3, V('방향'))), cast('방갱신'), cast('딸깍')))
    # ---------------- 아래: 말 상자, 힌트, 가방
    panel(P, sc, '방말판', -122, -116, 236, 30, 'glass')
    msg = m.T('방말글', '', -122, -116, 9, C_WHITE, F_BODY, True, 0, w=224, h=26)
    msg.on(on_msg('방말'), write(V('방글')))
    hint_lines = [
        (eq(V('서랍열림'), 0), '힌트: 서랍 비밀번호는 시계가 멈춘 시각! (예: 7시 5분 → 0705)'),
        (eq(V('비춤'), 0), '힌트: 가방에서 손전등을 고른 뒤, 뒤쪽 벽 책장을 눌러 봐.'),
        (eq(V('사물함열림'), 0), '힌트: 빛나는 1 → 2 → 3 책의 색을 사물함 자물쇠에 차례로!'),
        (eq(V('휴지통뒤짐'), 0), '힌트: 쪽지에 앞 두 자리가 있어. 뒤 두 자리 단서는 휴지통 속에!'),
        (eq(V('문풀림'), 0), '힌트: 가방에서 열쇠를 고른 뒤 문을 눌러 자물쇠부터!'),
    ]
    # 힌트: 아직 못 푼 첫 단계의 힌트
    chain = say('힌트: 의자 하나에 다리 4개! 앞쪽·뒤쪽 벽 의자를 모두 세서 곱해.')
    for c_, t_ in reversed(hint_lines):
        chain = [ifelse(c_, say(t_), chain)]
    hint_act = [if_(can(), chg('힌트수', 1), cast('힌트'), *chain)]
    hb = button(P, sc, '힌트버튼', '힌트 -10', 22, -116, 62, 26, 'purple', actions=hint_act)
    for k in range(1, 5):
        pics = [('i%d' % it, A2.room_item(nm)) for it, nm in enumerate(('none', 'light', 'key', 'note', 'paper'))]
        pics += [('s%d' % it, A2.room_item(nm, True)) for it, nm in enumerate(('none', 'light', 'key', 'note', 'paper'))]
        sl = m.S('가방칸%d' % k, pics, 74 + (k - 1) * 42, -116)
        it = LGET('가방', k)
        sl.on(on_msg('가방갱신'), ifelse(and_(gt(it, 0), eq(V('선택템'), it)), [shape(add(6, it))], [shape(add(1, it))]))
        sl.on(on_scene(), shape(1))
        sl.on(on_click(), if_(and_(can(), gt(it, 0)),
                              ifelse(eq(V('선택템'), it), [setv('선택템', 0)], [setv('선택템', it)]), cast('가방갱신'), cast('딸깍'),
                              if_(eq(it, 1), *say('손전등을 들었다. 비춰 볼 곳을 눌러.')),
                              if_(eq(it, 2), *say('열쇠를 들었다. 어디에 쓸까?')),
                              if_(eq(it, 3), setv('방글', note_txt), cast('방말')),
                              if_(eq(it, 4), *say(paper_txt))))
    # ---------------- 번호판 창 (서랍/문)
    kp = []
    kp.append(m.S('번호어둡게', A.plain_rect(480, 270, (2, 3, 12, 170), 'dim_kp'), 0, 0))
    kp.append(panel(P, sc, '번호판', 0, 4, 210, 200, 'glass', header='royal'))
    kt = m.T('번호제목', '', 0, 86, 11, C_WHITE, F_NUM, False, 0, w=180, h=16)
    kt.on(on_msg('번호창'), ifelse(eq(V('키대상'), 1), [write('서랍 자물쇠')], [write('문 번호판')]))
    kp.append(kt)
    disp = m.T('번호표시', '', 0, 62, 20, C_ACC, F_NUM, False, 0, w=160, h=28, bg=C_BOX)
    disp.on(on_msg('번호갱신'), ifelse(lt(slen(V('키입력')), 4), [write(join(V('키입력'), substr('____', 1, sub(4, slen(V('키입력'))))))],
                                     [write(V('키입력'))]))
    kp.append(disp)
    def kpress(d):
        return [if_(and_(eq(V('창'), 1), lt(slen(V('키입력')), 4)), setv('키입력', join(V('키입력'), d)), cast('번호갱신'), cast('딸깍'))]
    for d in range(10):
        r, c = (d - 1) // 3 if d else 3, (d - 1) % 3 if d else 1
        bt = button(P, sc, '번호%d' % d, str(d), -46 + c * 46, 30 - r * 30, 40, 26, 'blue', actions=kpress(d))
        kp.append(bt)
        hidden(m, '번호키%d' % d).on(on_key(48 + d), *kpress(d))
    back_ = [if_(and_(eq(V('창'), 1), gt(slen(V('키입력')), 0)),
                 ifelse(eq(slen(V('키입력')), 1), [setv('키입력', '')], [setv('키입력', substr(V('키입력'), 1, sub(slen(V('키입력')), 1)))]),
                 cast('번호갱신'))]
    kp.append(button(P, sc, '번호지움', '지움', -46, -60, 40, 26, 'gray', actions=back_))
    hidden(m, '번호지움키').on(on_key(8), *back_)
    ok = [if_(and_(eq(V('창'), 1), eq(slen(V('키입력')), 4)), cast('번호확인'))]
    kp.append(button(P, sc, '번호확인', '확인', 46, -60, 40, 26, 'royal', actions=ok))
    hidden(m, '번호확인키').on(on_key(K_ENTER), *ok)
    close_kp = [if_(eq(V('창'), 1), setv('창', 0), cast('번호닫기'))]
    kp.append(button(P, sc, '번호닫기', '닫기', 82, 86, 40, 20, 'gray', actions=close_kp))
    for o in kp:
        o.on(on_scene(), hide())
        o.on(on_msg('번호창'), show())
        o.on(on_msg('번호닫기'), hide())
    disp.on(on_msg('번호창'), cast('번호갱신'))
    kmgr = hidden(m, '번호담당')
    kmgr.on(on_msg('번호확인'),
            ifelse(eq(V('키대상'), 1),
                   [ifelse(eq(V('키입력'), V('서랍코드')),
                           [setv('서랍열림', 1), setv('창', 0), cast('번호닫기'), cast('방갱신'), *add_item(1), cast('찾음'),
                            *say('서랍이 열렸다! 손전등을 찾았다.')],
                           [chg('틀린수', 1), setv('키입력', ''), cast('번호갱신'), cast('삐빅'), *say('삐빅! 비밀번호가 틀렸다.')])],
                   [ifelse(eq(V('키입력'), V('문코드')),
                           [setv('창', 0), cast('번호닫기'), setv('탈출', 1), cast('방갱신'), cast('탈출'),
                            *say('문이 열렸다! 탈출 성공!')],
                           [chg('틀린수', 1), setv('키입력', ''), cast('번호갱신'), cast('삐빅'), *say('삐빅! 번호가 틀렸다.')])]))
    # ---------------- 색깔 자물쇠 창 (사물함)
    cp = [m.S('색어둡게', A.plain_rect(480, 270, (2, 3, 12, 170), 'dim_kp'), 0, 0),
          panel(P, sc, '색판', 0, 4, 230, 150, 'glass', header='purple'),
          m.T('색제목', '사물함 색깔 자물쇠', 0, 62, 11, C_WHITE, F_NUM, False, 0, w=200, h=16),
          m.T('색설명', '칸을 누르면 색이 바뀌어요', 0, 42, 8, C_DIM, F_BODY, True, 0, w=200, h=12)]
    for i in (1, 2, 3):
        dl = m.S('다이얼%d' % i, [(c, A2.color_dial(c)) for c in A2.ROOM_COL_NAMES], -60 + (i - 1) * 60, 4)
        dl.on(on_msg('색창'), shape(V('다이얼%d' % i)))
        dl.on(on_click(), if_(eq(V('창'), 2), chg('다이얼%d' % i, 1), if_(gt(V('다이얼%d' % i), 4), setv('다이얼%d' % i, 1)),
                              shape(V('다이얼%d' % i)), cast('딸깍')))
        cp.append(dl)
        cp.append(m.T('다이얼번호%d' % i, str(i), -60 + (i - 1) * 60, -24, 9, C_DIM, F_NUM, False, 0, w=20, h=12))
    cok = [if_(eq(V('창'), 2), cast('색확인'))]
    cp.append(button(P, sc, '색확인', '확인', -40, -48, 64, 24, 'royal', actions=cok))
    cp.append(button(P, sc, '색닫기', '닫기', 40, -48, 64, 24, 'gray', actions=[if_(eq(V('창'), 2), setv('창', 0), cast('색닫기'))]))
    for o in cp:
        o.on(on_scene(), hide())
        o.on(on_msg('색창'), show())
        o.on(on_msg('색닫기'), hide())
    cmgr = hidden(m, '색담당')
    cmgr.on(on_msg('색확인'),
            ifelse(and_(and_(eq(V('다이얼1'), LGET('사물함코드', 1)), eq(V('다이얼2'), LGET('사물함코드', 2))),
                        eq(V('다이얼3'), LGET('사물함코드', 3))),
                   [setv('사물함열림', 1), setv('창', 0), cast('색닫기'), cast('방갱신'), *add_item(2), *add_item(3), cast('찾음'),
                    *say('사물함이 열렸다! 열쇠와 쪽지가 있다. (가방에서 쪽지를 눌러 읽기)')],
                   [chg('틀린수', 1), cast('삐빅'), *say('덜컥... 열리지 않는다.')]))
    # ---------------- 탈출 연출과 점수
    flash = m.S('탈출빛', A.plain_rect(480, 270, (200, 220, 255, 255), 'white_full'), 0, 0, visible=False)
    flash.on(on_msg('탈출'), wait(0.4), fx('transparency', 100), show(), rep(10, fx_add('transparency', -8), wait(0.03)))
    G.big_pop(P, sc, '탈출글', K.big_text('탈출 성공!', 40, 'royal'), 0, 20, '탈출', hold=1.2)
    spent = sub(TL, V('남은시간'))
    esc_score = sub(sub(100, mul(V('힌트수'), 10)), mul(V('_mk'), 0.25))
    mgr = hidden(m, '탈출담당')
    mgr.on(on_msg('탈출'), setv('_mk', sub(spent, 70)), if_(lt(V('_mk'), 0), setv('_mk', 0)),
           setv('합계', esc_score), if_(lt(V('합계'), 40), setv('합계', 40)),
           wait(1.6), *m.end_blocks(V('합계')))
    part = add(add(add(mul(V('서랍열림'), 12), mul(V('비춤'), 12)), add(mul(V('사물함열림'), 14), mul(V('휴지통뒤짐'), 6))),
               sub(mul(V('문풀림'), 10), mul(V('힌트수'), 5)))
    mgr.on(on_msg('시간끝'), setv('창', 0), cast('번호닫기'), cast('색닫기'), *say('시간이 다 됐다... 갇혀 버렸다!'),
           wait(1.0), *m.end_blocks(part))
    status = hidden(m, '방탈출상태')
    status.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                       setv('미니표시', join('힌트 ', V('힌트수'), '번 · 실수 ', V('틀린수'))), wait(0.2)))
    # ---------------- 시작: 정답 무작위로 정하기
    m.on_start(setv('방향', 1), setv('창', 0), setv('선택템', 0), setv('힌트수', 0), setv('틀린수', 0),
               setv('서랍열림', 0), setv('비춤', 0), setv('사물함열림', 0), setv('휴지통뒤짐', 0), setv('문풀림', 0), setv('탈출', 0),
               setv('키입력', ''), setv('방글', '교실에 갇혔다! 단서를 찾아 탈출하자. (◀ ▶ 로 벽 바꾸기)'),
               *[lst_set('가방', k, 0) for k in range(1, 5)],
               setv('시H', rnd(1, 12)), setv('시M', mul(rnd(0, 11), 5)),
               setv('서랍코드', V('시H')), if_(lt(V('시H'), 10), setv('서랍코드', join('0', V('서랍코드')))),
               if_(lt(V('시M'), 10), setv('서랍코드', join(V('서랍코드'), '0'))), setv('서랍코드', join(V('서랍코드'), V('시M'))),
               *[lst_set('책색', k, rnd(1, 4)) for k in range(1, 6)],
               *[lst_set('책표시', k, 0) for k in range(1, 6)],
               setv('_ma', rnd(1, 5)), setv('_mb', rnd(1, 5)), until(ne(V('_mb'), V('_ma')), setv('_mb', rnd(1, 5))),
               setv('_mk', rnd(1, 5)), until(and_(ne(V('_mk'), V('_ma')), ne(V('_mk'), V('_mb'))), setv('_mk', rnd(1, 5))),
               lst_set('책표시', V('_ma'), 1), lst_set('책표시', V('_mb'), 2), lst_set('책표시', V('_mk'), 3),
               lst_set('사물함코드', 1, LGET('책색', V('_ma'))), lst_set('사물함코드', 2, LGET('책색', V('_mb'))),
               lst_set('사물함코드', 3, LGET('책색', V('_mk'))),
               setv('다이얼1', 1), setv('다이얼2', 1), setv('다이얼3', 1),
               setv('쪽지수', rnd(10, 99)), setv('앞의자', rnd(2, 5)), setv('뒤의자', rnd(1, 4)),
               setv('다리수', mul(add(V('앞의자'), V('뒤의자')), 4)),
               setv('문코드', join(V('쪽지수'), V('다리수'))),
               cast('방갱신'), cast('가방갱신'), cast('방말'))
    m.snd('딸깍', play('tick'))
    m.snd('찾음', play('good'))
    m.snd('삐빅', play('bad'))
    m.snd('철컥', play('stamp'))
    m.snd('비추기', play('shutter'))
    m.snd('탈출', play('fanfare'))
    m.finish('신대리 폐교 교실에 갇혔다! 3분 안에 탈출하라.\n단서를 모아 자물쇠를 하나씩 풀어야 해요. 정답은 매번 달라요!',
             '조작: 마우스 클릭  ·  ◀ ▶ 벽 바꾸기  ·  가방의 물건을 고른 뒤 쓸 곳을 클릭  ·  힌트는 -10점')
    return True


# ================================================================== 30. 고갯길 결투 (반응속도)
def g30(P, ctx):
    R = 5
    _vars(P, '신호', '눌림', '반칙', '내반응', '상대반응', '승리수')
    m = MG(P, 30, ctx, status='승리 0/%d' % R, dim=60)
    me = m.S('결투나', ctx['BUST']['me'], -160, -36, scale=0.55)
    foe = m.S('결투상대', ctx['BUST']['u2'], 160, -36, scale=0.55)
    sig = m.S('결투신호', [('ready', K.big_text('준비...', 30, 'white')), ('fire', K.big_text('쏴!', 64, 'royal')),
                          ('fake1', K.big_text('쏘지 마!', 36, 'red')), ('fake2', K.big_text('잠깐!', 36, 'red'))],
              0, 40, visible=False)
    sig.on(on_msg('준비'), shape('ready'), show())
    sig.on(on_msg('가짜'), ifelse(eq(rnd(1, 2), 1), [shape('fake1')], [shape('fake2')]), sig.pct(120),
           rep(4, sig.grow_pct(-5), wait(0.016)))
    sig.on(on_msg('쏴'), shape('fire'), sig.pct(140), show(), rep(5, sig.grow_pct(-8), wait(0.016)))
    sig.on(on_msg('판정'), hide())
    fl_me = m.S('불꽃나', A2.muzzle(), -100, -10, visible=False)
    fl_foe = m.S('불꽃상대', A2.muzzle(), 100, -10, visible=False)
    fl_me.on(on_msg('내가쏨'), show(), wait(0.12), hide())
    fl_foe.on(on_msg('상대쏨'), show(), wait(0.12), hide())
    res = m.S('결투결과', [('w', K.big_text('승리!', 34, 'royal')), ('l', K.big_text('패배...', 30, 'red')),
                          ('f', K.big_text('반칙!', 30, 'red'))], 0, 40, visible=False)
    res.on(on_msg('판정'), ifelse(eq(V('반칙'), 1), [shape('f')],
                                [ifelse(eq(V('_mk'), 1), [shape('w')], [shape('l')])]),
           res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.016)), wait(1.0), hide())
    info = m.T('결투기록', '', 0, -100, 11, C_WHITE, F_NUM, False, 0, w=360, h=18, bg=C_BOX)
    info.on(on_msg('판정'), ifelse(eq(V('반칙'), 1), [write('신호 전에 쏘면 반칙이에요!')],
                                 [ifelse(eq(V('눌림'), 1), [write(join('내 반응 ', div(rounded(mul(V('내반응'), 1000)), 1000),
                                                                    '초  vs  상대 ', V('상대반응'), '초'))],
                                         [write(join('상대가 먼저! (', V('상대반응'), '초)'))])]))
    info.on(on_msg('준비'), write('"쏴!"가 뜨면 바로 SPACE!'))
    me.on(on_msg('내가쏨'), rep(3, mvx(-3), wait(0.02), mvx(3), wait(0.02)))
    foe.on(on_msg('상대쏨'), rep(3, mvx(3), wait(0.02), mvx(-3), wait(0.02)))
    me.on(on_msg('판정'), if_(and_(eq(V('_mk'), 0), eq(V('반칙'), 0)), rot(-8), wait(0.6), rot(0)))
    foe.on(on_msg('판정'), if_(eq(V('_mk'), 1), rot(8), wait(0.6), rot(0)))
    keys = hidden(m, '결투키')
    keys.on(on_key(K_SPACE), if_(and_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)), eq(V('눌림'), 0)),
                                 setv('눌림', 1),
                                 ifelse(eq(V('신호'), 1), [setv('내반응', timer()), cast('내가쏨')], [setv('반칙', 1)])))
    # 기다리기: 반칙이면 바로 끝
    def hold(sec_expr):
        return [setv('_mt', add(timer(), sec_expr)), until(or_(ge(timer(), V('_mt')), eq(V('반칙'), 1)), wait(0.01))]
    mgr = hidden(m, '결투담당')
    mgr.on(on_msg('게임시작'), reset_timer(), start_timer(), setv('라운드', 1),
           until(gt(V('라운드'), R),
                 setv('신호', 0), setv('눌림', 0), setv('반칙', 0), setv('_mk', 0), setv('대기', 1), cast('준비'),
                 *hold(div(rnd(120, 300), 100)),
                 if_(and_(eq(V('반칙'), 0), and_(ge(V('라운드'), 2), le(rnd(1, 100), 45))),
                     setv('신호', 2), cast('가짜'), *hold(0.9), if_(eq(V('반칙'), 0), setv('신호', 0), cast('준비')),
                     *hold(div(rnd(60, 150), 100))),
                 if_(eq(V('반칙'), 0),
                     setv('상대반응', div(add(sub(46, mul(V('라운드'), 3)), rnd(0, 10)), 100)),
                     reset_timer(), setv('신호', 1), cast('쏴'),
                     wait_until(or_(eq(V('눌림'), 1), ge(timer(), V('상대반응')))),
                     ifelse(and_(eq(V('눌림'), 1), lt(V('내반응'), V('상대반응'))), [setv('_mk', 1), chg('승리수', 1)],
                            [setv('_mk', 0), cast('상대쏨')])),
                 setv('대기', 0), cast('판정'),
                 setv('미니표시', join('승리 ', V('승리수'), '/', R)),
                 wait(1.6), chg('라운드', 1)),
           *m.end_blocks(mul(V('승리수'), 100.0 / R)))
    m.on_start(setv('승리수', 0), setv('대기', 0), setv('신호', 0))
    m.snd('내가쏨', play('hit'))
    m.snd('상대쏨', play('hit'))
    m.snd('쏴', play('beep'))
    m.snd('판정', ifelse(eq(V('_mk'), 1), [play('good')], [play('bad')]))
    m.finish('둘째 큰아버지와 고갯길 결투! 5판 승부.\n"쏴!"가 뜨는 순간 SPACE! 가짜 신호에 속으면 반칙!',
             '조작: SPACE  ·  상대는 판이 갈수록 빨라져요')
    return True


# ================================================================== 36. 민원 서류 짝 맞추기
def g36(P, ctx):
    _vars(P, '첫카드', '둘카드', '잠김')
    m = MG(P, 36, ctx, time_limit=60, status='짝 0/8', dim=90)
    icons = ['coin', 'ballot', 'mega', 'chart', 'shield', 'star', 'clock', 'trophy']
    pics = [('back', A2.icon_card(None, 52, 52, 'back', name='icard_back'))]
    pics += [('f%d' % i, A2.icon_card(ic)) for i, ic in enumerate(icons, 1)]
    pics += [('d%d' % i, A2.icon_card(ic, kind='done')) for i, ic in enumerate(icons, 1)]
    P.list('짝카드', [k for k in range(1, 9) for _ in range(2)])
    P.list('짝열림', [0] * 16)
    panel(P, m.sc, '짝판', 0, -16, 252, 236, 'glass')
    for k in range(1, 17):
        r, c = (k - 1) // 4, (k - 1) % 4
        x, y = -87 + c * 58, 72 - r * 58
        cd = m.S('짝카드%d' % k, pics, x, y)
        cd.on(on_scene(), shape('back'))
        cd.on(on_msg('카드갱신'),
              ifelse(eq(LGET('짝열림', k), 0), [shape('back')],
                     [ifelse(eq(LGET('짝열림', k), 1), [shape(add(1, LGET('짝카드', k)))], [shape(add(9, LGET('짝카드', k)))])]))
        cd.on(on_click(), if_(and_(and_(eq(V('게임중'), 1), eq(V('잠김'), 0)), eq(LGET('짝열림', k), 0)),
                              lst_set('짝열림', k, 1), cast('카드갱신'), cast('카드뒤집기'),
                              ifelse(eq(V('첫카드'), 0), [setv('첫카드', k)], [setv('둘카드', k), setv('잠김', 1), cast('짝판정')])))
        cd.on(on_click(), if_(eq(V('게임중'), 1), cd.pct(90), wait(0.06), cd.pct(100)))
    mgr = hidden(m, '짝담당')
    a, b = LGET('짝카드', V('첫카드')), LGET('짝카드', V('둘카드'))
    mgr.on(on_msg('짝판정'),
           ifelse(eq(a, b), [lst_set('짝열림', V('첫카드'), 2), lst_set('짝열림', V('둘카드'), 2), chg('합계', 1), cast('짝맞음'),
                             setv('미니표시', join('짝 ', V('합계'), '/8'))],
                  [wait(0.7), lst_set('짝열림', V('첫카드'), 0), lst_set('짝열림', V('둘카드'), 0), cast('짝틀림')]),
           setv('첫카드', 0), setv('둘카드', 0), cast('카드갱신'), setv('잠김', 0),
           if_(ge(V('합계'), 8), wait(0.4), *m.end_blocks(add(80, mul(V('남은시간'), 0.7)))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 10)))
    # 섞기 (소개 창이 떠 있는 동안)
    m.on_start(setv('합계', 0), setv('첫카드', 0), setv('둘카드', 0), setv('잠김', 0),
               setv('_mi', 1), rep(16, lst_set('짝열림', V('_mi'), 0), chg('_mi', 1)),
               rep(40, setv('_ma', rnd(1, 16)), setv('_mb', rnd(1, 16)), setv('_mk', LGET('짝카드', V('_ma'))),
                   lst_set('짝카드', V('_ma'), LGET('짝카드', V('_mb'))), lst_set('짝카드', V('_mb'), V('_mk'))),
               cast('카드갱신'))
    m.snd('카드뒤집기', play('tick'))
    m.snd('짝맞음', play('good'))
    m.snd('짝틀림', play('bad'))
    m.finish('행정복지센터 민원 서류 정리! 카드를 두 장씩 뒤집어\n같은 그림 8쌍을 모두 찾으세요. 빨리 찾을수록 점수 UP!',
             '조작: 마우스로 카드 클릭  ·  60초')
    return True


# ================================================================== 37. 떡 주문 받기 (주문 만들기)
def g37(P, ctx):
    MAXL = 5
    _vars(P, '떡진행', '떡길이', '인내')
    m = MG(P, 37, ctx, time_limit=45, status='손님 0명', dim=100)
    P.list('떡주문', [1] * MAXL)
    icons = [('t%d' % k, A2.tteok_icon(k - 1)) for k in range(1, 7)]
    # 손님 + 말풍선
    m.S('손님', K.icon_img('person', 46), -186, 60)
    m.S('주문말풍선', A2.speech(236, 64), -40, 64)
    for j in range(1, MAXL + 1):
        o = m.S('주문칸%d' % j, icons, -120 + (j - 1) * 40, 70, visible=False)
        o.on(on_msg('새주문'), if_(le(j, V('떡길이')), shape(LGET('떡주문', j)), fx('brightness', 0), show()),
             if_(gt(j, V('떡길이')), hide()))
        o.on(on_msg('떡갱신'), ifelse(lt(j, V('떡진행')), [fx('brightness', -55)], [fx('brightness', 0)]))
    bar = m.S('인내막대', K.bar_set('patience_red', 120, 7, 'red'), -40, 36)
    bar.on(on_msg('게임시작'), until(eq(V('게임중'), 0), shape(add(floor(mul(div(V('인내'), 100), 40)), 1)), wait(0.05)))
    m.T('인내글', '손님 인내심', -140, 36, 8, C_DIM, F_BODY, True, 1, w=70, h=12)
    # 접시
    m.S('접시', A2.plate(170, 44), 40, -40)
    for j in range(1, MAXL + 1):
        o = m.S('접시칸%d' % j, icons, -24 + (j - 1) * 32, -32, visible=False)
        o.on(on_msg('떡갱신'), ifelse(lt(j, V('떡진행')), [shape(LGET('떡주문', j)), show()], [hide()]))
        o.on(on_msg('새주문'), hide())
    # 재료 버튼
    names = [t[0] for t in A2.TTEOK]
    for k in range(1, 7):
        x = -150 + (k - 1) * 60
        b = m.S('재료%d' % k, A2.tile(54, 54, (40, 60, 150), (16, 24, 70), name='tteok_btn'), x, -98)
        ic = m.S('재료그림%d' % k, icons[k - 1][1], x, -92)
        m.T('재료이름%d' % k, '%d.%s' % (k, names[k - 1]), x, -118, 7, C_WHITE, F_NUM, False, 0, w=56, h=11)
        act = [if_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)),
                   ifelse(eq(LGET('떡주문', V('떡진행')), k),
                          [chg('떡진행', 1), cast('떡갱신'), cast('떡딱'),
                           if_(gt(V('떡진행'), V('떡길이')), setv('대기', 0), chg('합계', 1), cast('떡완성'))],
                          [setv('떡진행', 1), chg('틀림', 1), cast('떡갱신'), cast('떡실수')]))]
        for o in (b, ic):
            o.on(on_click(), *act)
            G.hover_scripts(o, 106)
        hidden(m, '재료키%d' % k).on(on_key(48 + k), *act)
    res = m.S('떡결과', [('o', K.big_text('맛있다!', 26, 'royal')), ('x', K.big_text('그거 아닌데...', 20, 'red')),
                        ('l', K.big_text('손님이 떠났다', 20, 'red'))], 40, 8, visible=False)
    for msg_, sh in (('떡완성', 'o'), ('떡실수', 'x'), ('손님떠남', 'l')):
        res.on(on_msg(msg_), shape(sh), res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.016)), wait(0.5), hide())
    mgr = hidden(m, '떡담당')
    new_order = [setv('떡길이', add(3, floor(div(V('합계'), 3)))), if_(gt(V('떡길이'), MAXL), setv('떡길이', MAXL)),
                 *[lst_set('떡주문', j, rnd(1, 6)) for j in range(1, MAXL + 1)],
                 setv('떡진행', 1), setv('인내', 100), cast('새주문'), cast('떡갱신'), setv('대기', 1)]
    mgr.on(on_msg('게임시작'),
           until(eq(V('게임중'), 0),
                 *new_order,
                 until(or_(or_(eq(V('대기'), 0), le(V('인내'), 0)), eq(V('게임중'), 0)),
                       wait(0.05), chg('인내', sub(-0.55, mul(V('합계'), 0.03)))),
                 if_(and_(eq(V('대기'), 1), eq(V('게임중'), 1)), setv('대기', 0), cast('손님떠남')),
                 setv('미니표시', join('손님 ', V('합계'), '명')),
                 wait(0.5)))
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(V('합계'), 10), mul(V('틀림'), 2))))
    m.on_start(setv('합계', 0), setv('틀림', 0), setv('대기', 0), setv('인내', 100), setv('떡길이', 3), setv('떡진행', 1))
    m.snd('떡딱', play('tick'))
    m.snd('떡완성', play('coin'))
    m.snd('떡실수', play('bad'))
    m.snd('손님떠남', play('bad'))
    m.finish('명리 방앗간 떡 주문! 손님 말풍선의 재료를\n왼쪽부터 순서대로 눌러 떡을 만드세요. 틀리면 처음부터!',
             '조작: 재료 클릭 또는 숫자키 1~6  ·  45초  ·  손님 인내심이 다 닳기 전에!')
    return True


# ================================================================== 24. 비밀번호 추리 (숫자 야구)
def g24(P, ctx):
    T = 8
    _vars(P, '비번1', '비번2', '비번3', '시도', '최고스트', '스트', '볼')
    P.var('입력', '')
    P.var('추리기록', '')
    m = MG(P, 24, ctx, time_limit=90, status='시도 0/%d' % T, dim=120)
    panel(P, m.sc, '입력판', -122, -14, 196, 216, 'glass', header='royal')
    m.T('입력제목', '비밀번호 입력', -122, 78, 10, C_WHITE, F_NUM, False, 0, w=160, h=16)
    for i in range(1, 4):
        bx = m.S('입력칸%d' % i, [('e', A2.digit_box('empty')), ('on', A2.digit_box('on'))], -122 + (i - 2) * 40, 50)
        bx.on(on_msg('입력갱신'), ifelse(ge(slen(V('입력')), i), [shape('on')], [shape('e')]))
        dt = m.T('입력숫자%d' % i, '', -122 + (i - 2) * 40, 50, 18, C_WHITE, F_NUM, False, 0, w=30, h=26)
        dt.on(on_msg('입력갱신'), ifelse(ge(slen(V('입력')), i), [write(char_at(V('입력'), i))], [write('')]))
    # 엔트리는 '그리고'의 양쪽을 다 계산하므로, 글자 수보다 큰 자리를 읽지 않게 '000'을 붙여서 본다 (숫자는 1~9)
    padded = join(V('입력'), '000')
    has = lambda d: or_(or_(eq(char_at(padded, 1), d), eq(char_at(padded, 2), d)), eq(char_at(padded, 3), d))
    for d in range(1, 10):
        r, c = (d - 1) // 3, (d - 1) % 3
        act = [if_(and_(eq(V('게임중'), 1), and_(lt(slen(V('입력')), 3), not_(has(d)))),
                   setv('입력', join(V('입력'), d)), cast('입력갱신'), cast('딸깍'))]
        button(P, m.sc, '숫자%d' % d, str(d), -162 + c * 40, 14 - r * 32, 36, 28, 'blue', actions=act)
        hidden(m, '숫자키%d' % d).on(on_key(48 + d), *act)
    erase = [if_(gt(slen(V('입력')), 0),
                 ifelse(eq(slen(V('입력')), 1), [setv('입력', '')], [setv('입력', substr(V('입력'), 1, sub(slen(V('입력')), 1)))]),
                 cast('입력갱신'))]
    button(P, m.sc, '지우기', '지우기', -82, -82, 60, 26, 'gray', actions=erase)
    hidden(m, '지우기키').on(on_key(8), *erase)
    ok = [if_(and_(eq(V('게임중'), 1), eq(slen(V('입력')), 3)), cast('추리판정'))]
    button(P, m.sc, '확인', '확인', -150, -82, 64, 26, 'royal', actions=ok)
    hidden(m, '확인키').on(on_key(K_ENTER), *ok)
    # 기록판
    panel(P, m.sc, '기록판', 100, -14, 236, 216, 'glass', header='purple')
    m.T('기록제목', '추리 기록  (S: 자리까지 맞음, B: 숫자만 맞음)', 100, 78, 8, C_WHITE, F_BODY, True, 0, w=226, h=14)
    rec = m.T('기록글', '', 100, -8, 11, C_WHITE, F_NUM, False, 1, w=200, h=150)
    rec.on(on_msg('기록갱신'), write(V('추리기록')))
    big = m.S('추리결과', [('o', K.big_text('정답!', 34, 'royal')), ('x', K.big_text('실패...', 30, 'red'))], 0, 0, visible=False)
    big.on(on_msg('추리끝'), ifelse(eq(V('스트'), 3), [shape('o')], [shape('x')]), big.pct(130), show(),
           rep(5, big.grow_pct(-6), wait(0.016)))
    ans = m.T('정답공개', '', 0, -40, 14, C_ACC, F_NUM, False, 0, w=240, h=22, visible=False, bg=C_BOX)
    ans.on(on_msg('추리끝'), write(join('비밀번호는 ', V('비번1'), V('비번2'), V('비번3'))), show())
    g = [char_at(V('입력'), i) for i in (1, 2, 3)]
    s = [V('비번1'), V('비번2'), V('비번3')]
    mgr = hidden(m, '추리담당')
    mgr.on(on_msg('추리판정'),
           setv('스트', 0), setv('볼', 0),
           *[if_(eq(g[i], s[i]), chg('스트', 1)) for i in range(3)],
           *[if_(eq(g[i], s[j]), chg('볼', 1)) for i in range(3) for j in range(3) if i != j],
           chg('시도', 1),
           setv('추리기록', join(V('추리기록'), V('시도'), '.  ', g[0], ' ', g[1], ' ', g[2], '   →   ',
                               V('스트'), 'S ', V('볼'), 'B\n')),
           if_(gt(V('스트'), V('최고스트')), setv('최고스트', V('스트'))),
           setv('입력', ''), cast('입력갱신'), cast('기록갱신'),
           setv('미니표시', join('시도 ', V('시도'), '/', T)),
           ifelse(eq(V('스트'), 3), [cast('추리끝'), wait(1.4), *m.end_blocks(sub(108, mul(V('시도'), 8)))],
                  [cast('추리틀림'), if_(ge(V('시도'), T), cast('추리끝'), wait(1.6),
                                         *m.end_blocks(add(15, mul(V('최고스트'), 12))))]))
    mgr.on(on_msg('시간끝'), cast('추리끝'), wait(1.2), *m.end_blocks(add(10, mul(V('최고스트'), 12))))
    m.on_start(setv('시도', 0), setv('최고스트', 0), setv('입력', ''), setv('추리기록', ''),
               setv('비번1', rnd(1, 9)), setv('비번2', rnd(1, 9)), until(ne(V('비번2'), V('비번1')), setv('비번2', rnd(1, 9))),
               setv('비번3', rnd(1, 9)), until(and_(ne(V('비번3'), V('비번1')), ne(V('비번3'), V('비번2'))), setv('비번3', rnd(1, 9))),
               cast('입력갱신'), cast('기록갱신'))
    m.snd('딸깍', play('tick'))
    m.snd('추리틀림', play('beep'))
    m.snd('추리끝', ifelse(eq(V('스트'), 3), [play('fanfare')], [play('bad')]))
    m.finish('동아리방 비밀번호를 맞혀라! 서로 다른 숫자 3개(1~9).\n숫자와 자리까지 맞으면 S, 숫자만 맞으면 B. 8번 안에!',
             '조작: 숫자 버튼/숫자키로 입력 → 확인(Enter)  ·  지우기(Backspace)')
    return True


# ================================================================== 16. 오봉산 계단 오르기 (무한의 계단)
def g16(P, ctx):
    rng = random.Random(16)
    dirs, x, xs = [], 0, [0]
    d = 1
    while len(dirs) < 400:
        run = rng.randint(1, 4)
        for _ in range(run):
            dirs.append(d)
            x += d
            xs.append(x)
        d = -d
    P.list('계단x', xs[:401])
    _vars(P, '계단시작', '계단cur', '기절')
    m = MG(P, 16, ctx, time_limit=30, status='0계단', dim=70)
    STEP_W, STEP_H, Y0 = 34, 22, -78
    base_x = lambda j: mul(sub(LGET('계단x', add(add(V('계단시작'), V('계단cur')), j + 1)),
                               LGET('계단x', add(V('계단시작'), add(V('계단cur'), 1)))), STEP_W)
    for j in range(10):
        st = m.S('계단%d' % j, A2.stair_block(), 0, Y0 + j * STEP_H)
        st.on(on_msg('계단갱신'), lx(base_x(j)), ly(Y0 + j * STEP_H))
    me = m.S('등산객', ctx['PORT']['me'], 0, Y0 + 18, scale=0.62)
    me.on(on_msg('계단갱신'), ly(Y0 + 18), me.pct(110), wait(0.05), me.pct(100))
    me.on(on_msg('미끄러짐'), rep(4, mvx(-4), wait(0.03), mvx(4), wait(0.03)))
    hgt = m.T('높이글', '0m', 150, 60, 20, C_WHITE, F_NUM, False, 0, w=120, h=28)
    hgt.on(on_msg('계단갱신'), write(join(mul(V('합계'), 2), 'm')))
    slip = m.S('미끄럼글', K.big_text('미끄러졌다!', 22, 'red'), 0, 30, visible=False)
    slip.on(on_msg('미끄러짐'), show(), wait(0.45), hide())
    nd = sub(LGET('계단x', add(add(V('계단시작'), V('계단cur')), 2)), LGET('계단x', add(add(V('계단시작'), V('계단cur')), 1)))
    def press(dr):
        return [if_(and_(eq(V('게임중'), 1), eq(V('기절'), 0)),
                    ifelse(eq(nd, dr), [chg('계단cur', 1), chg('합계', 1), cast('계단갱신'), cast('계단딱'),
                                         setv('미니표시', join(V('합계'), '계단'))],
                           [setv('기절', 1), chg('틀림', 1), cast('미끄러짐'), wait(0.5), setv('기절', 0)]))]
    keys = hidden(m, '계단키')
    keys.on(on_key(K_LEFT), *press(-1))
    keys.on(on_key(K_RIGHT), *press(1))
    mgr = hidden(m, '계단담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(V('합계'), 100.0 / 55), mul(V('틀림'), 2))))
    m.on_start(setv('합계', 0), setv('틀림', 0), setv('기절', 0), setv('계단cur', 0), setv('계단시작', rnd(0, 150)),
               cast('계단갱신'))
    m.snd('계단딱', play('tick'))
    m.snd('미끄러짐', play('bad'))
    m.finish('오봉산 돌계단을 30초 동안 최대한 높이!\n다음 계단이 왼쪽에 있으면 ←, 오른쪽에 있으면 →',
             '조작: ← → 방향키  ·  틀리면 미끄러져서 잠깐 멈춰요')
    return True


# ================================================================== 17. 홍보 드론 비행 (날기)
def g17(P, ctx):
    _vars(P, '드론y', '드론vy', '목숨', '무적', '통과')
    m = MG(P, 17, ctx, time_limit=40, status='통과 0 · ♥3', dim=40)
    dr = m.S('드론', A2.drone(), -120, 0, scale=0.85)
    gate = m.S('나무기둥', A2.tree_gate(92), 300, 0, visible=False)
    gate.local('통과', 0)
    gate.local('복제', 0)
    gate.on(on_msg('게임시작'), until(eq(V('게임중'), 0), clone_self(), wait(1.55)))
    gate.on(on_clone(), setv('복제', 1), setv('통과', 0), xy(270, rnd(-55, 55)), show(),
            until(or_(lt(obj_x(), -280), eq(V('게임중'), 0)),
                  mvx(sub(-2.4, mul(V('합계'), 0.06))),
                  if_(and_(eq(V('통과'), 0), lt(obj_x(), -120)), setv('통과', 1), chg('합계', 1), cast('통과'))),
            del_clone())
    flap = [if_(eq(V('게임중'), 1), setv('드론vy', 4.6), cast('푸드덕'))]
    keys = hidden(m, '드론키')
    keys.on(on_key(K_SPACE), *flap)
    keys.on(on_key(K_UP), *flap)
    keys.on(on_mouse_down(), *flap)
    crash = [chg('목숨', -1), setv('무적', 1), cast('쾅'), setv('드론y', 0), setv('드론vy', 0),
             if_(le(V('목숨'), 0), *m.end_blocks(mul(V('합계'), 100.0 / 14)))]
    dr.on(on_msg('게임시작'), setv('드론y', 0), setv('드론vy', 0),
          until(eq(V('게임중'), 0),
                chg('드론vy', -0.3), if_(lt(V('드론vy'), -6.5), setv('드론vy', -6.5)),
                chg('드론y', V('드론vy')), ly(V('드론y')), rot(mul(V('드론vy'), -3)),
                if_(eq(V('무적'), 0),
                    if_(or_(or_(gt(V('드론y'), 122), lt(V('드론y'), -122)), touch(gate.name)), *crash))))
    dr.on(on_msg('쾅'), rep(6, fx('transparency', 70), wait(0.1), fx('transparency', 0), wait(0.1)), setv('무적', 0))
    st = hidden(m, '드론상태')
    st.on(on_msg('게임시작'), until(eq(V('게임중'), 0), setv('미니표시', join('통과 ', V('합계'), ' · ♥', V('목숨'))), wait(0.1)))
    boom = m.S('쾅글', K.big_text('쾅!', 28, 'red'), -120, 30, visible=False)
    boom.on(on_msg('쾅'), show(), wait(0.4), hide())
    mgr = hidden(m, '드론담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 100.0 / 14)))
    m.on_start(setv('합계', 0), setv('목숨', 3), setv('무적', 0), setv('드론y', 0), setv('드론vy', 0))
    m.snd('푸드덕', play('jump'))
    m.snd('통과', play('coin'))
    m.snd('쾅', play('hit'))
    m.finish('홍보 드론을 띄워 고복저수지 나무 사이를 통과하세요!\n14번 통과하면 만점. 부딪히면 목숨이 하나 줄어요 (3개).',
             '조작: SPACE · ↑ · 마우스 클릭 = 위로 붕~')
    return True


# ================================================================== 18. 마을회관 삼목 대결 (보드게임)
def g18(P, ctx):
    R = 3
    lines = [(1, 2, 3), (4, 5, 6), (7, 8, 9), (1, 4, 7), (2, 5, 8), (3, 6, 9), (1, 5, 9), (3, 5, 7)]
    P.list('삼목판', [0] * 9)
    P.list('삼목줄', [c for ln in lines for c in ln])
    _vars(P, '삼목차례', '삼목승자', '삼목수', '_s1', '_s2', '_s3', '삼목승', '삼목무')
    m = MG(P, 18, ctx, status='1판 · 승 0', dim=120)
    m.S('바둑판', A2.go_board(), 0, -10)
    m.S('이장님', K.icon_img('person', 40), 170, 40)
    m.T('이장님이름', '이장님 (백)', 170, 10, 9, C_WHITE, F_NUM, False, 0, w=80, h=14)
    m.S('나표시', ctx['PORT']['me'], -170, 40, scale=0.8)
    m.T('나이름', '나 (흑)', -170, 10, 9, C_WHITE, F_NUM, False, 0, w=80, h=14)
    turn_t = m.T('삼목차례글', '', 0, 98, 11, C_ACC, F_NUM, False, 0, w=240, h=16)
    turn_t.on(on_msg('삼목갱신'), ifelse(eq(V('삼목차례'), 1), [write('내 차례! 빈 칸을 누르세요')], [write('이장님이 생각 중...')]))
    pics = [('e', A2.go_stone('e')), ('b', A2.go_stone('b')), ('w', A2.go_stone('w')), ('bw', A2.go_stone('bw')),
            ('ww', A2.go_stone('ww'))]
    for k in range(1, 10):
        r, c = (k - 1) // 3, (k - 1) % 3
        o = m.S('삼목칸%d' % k, pics, -58 + c * 58, 48 - r * 58)
        o.on(on_msg('삼목갱신'), shape(add(LGET('삼목판', k), 1)))
        o.on(on_msg('삼목놓음'), if_(eq(V('삼목수'), k), o.pct(130), rep(5, o.grow_pct(-6), wait(0.016))))
        o.on(on_click(), if_(and_(and_(eq(V('게임중'), 1), eq(V('삼목차례'), 1)), eq(LGET('삼목판', k), 0)),
                             lst_set('삼목판', k, 1), setv('삼목수', k), setv('삼목차례', 0), cast('삼목갱신'), cast('삼목놓음'),
                             cast('삼목검사')))
    res = m.S('삼목결과', [('w', K.big_text('이겼다!', 30, 'royal')), ('l', K.big_text('졌다...', 28, 'red')),
                          ('d', K.big_text('무승부', 28, 'white'))], 0, -10, visible=False)
    res.on(on_msg('판끝'), ifelse(eq(V('삼목승자'), 1), [shape('w')], [ifelse(eq(V('삼목승자'), 2), [shape('l')], [shape('d')])]),
           res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.016)), wait(1.1), hide())
    # 승자 검사 (8줄)
    check = [setv('삼목승자', 0), setv('_mi', 1),
             rep(8, setv('_s1', LGET('삼목판', LGET('삼목줄', V('_mi')))), setv('_s2', LGET('삼목판', LGET('삼목줄', add(V('_mi'), 1)))),
                 setv('_s3', LGET('삼목판', LGET('삼목줄', add(V('_mi'), 2)))),
                 if_(and_(gt(V('_s1'), 0), and_(eq(V('_s1'), V('_s2')), eq(V('_s2'), V('_s3')))), setv('삼목승자', V('_s1'))),
                 chg('_mi', 3)),
             setv('_mk', 0), *[if_(eq(LGET('삼목판', k), 0), chg('_mk', 1)) for k in range(1, 10)],
             if_(and_(eq(V('삼목승자'), 0), eq(V('_mk'), 0)), setv('삼목승자', 3))]
    # 이장님 수: 이기는 수 → (75%) 막는 수 → 가운데 → 아무 데나
    def find(who):
        return [setv('_mi', 1),
                rep(8, if_(eq(V('삼목수'), 0),
                           setv('_s1', LGET('삼목줄', V('_mi'))), setv('_s2', LGET('삼목줄', add(V('_mi'), 1))),
                           setv('_s3', LGET('삼목줄', add(V('_mi'), 2))),
                           setv('_ma', add(add(eq_n(LGET('삼목판', V('_s1')), who), eq_n(LGET('삼목판', V('_s2')), who)),
                                           eq_n(LGET('삼목판', V('_s3')), who))),
                           setv('_mb', add(add(eq_n(LGET('삼목판', V('_s1')), 0), eq_n(LGET('삼목판', V('_s2')), 0)),
                                           eq_n(LGET('삼목판', V('_s3')), 0))),
                           if_(and_(eq(V('_ma'), 2), eq(V('_mb'), 1)),
                               ifelse(eq(LGET('삼목판', V('_s1')), 0), [setv('삼목수', V('_s1'))],
                                      [ifelse(eq(LGET('삼목판', V('_s2')), 0), [setv('삼목수', V('_s2'))], [setv('삼목수', V('_s3'))])]))),
                    chg('_mi', 3))]
    ai = [setv('삼목수', 0), *find(2),
          if_(and_(eq(V('삼목수'), 0), le(rnd(1, 100), 75)), *find(1)),
          if_(and_(eq(V('삼목수'), 0), eq(LGET('삼목판', 5), 0)), setv('삼목수', 5)),
          if_(eq(V('삼목수'), 0), setv('삼목수', rnd(1, 9)), until(eq(LGET('삼목판', V('삼목수')), 0), setv('삼목수', rnd(1, 9)))),
          lst_set('삼목판', V('삼목수'), 2), cast('삼목갱신'), cast('삼목놓음')]
    mgr = hidden(m, '삼목담당')
    new_round = [*[lst_set('삼목판', k, 0) for k in range(1, 10)], setv('삼목승자', 0), cast('삼목갱신')]
    mgr.on(on_msg('삼목검사'), *check,
           ifelse(gt(V('삼목승자'), 0), [cast('판끝')],
                  [wait(0.6), *ai, *check, ifelse(gt(V('삼목승자'), 0), [cast('판끝')], [setv('삼목차례', 1), cast('삼목갱신')])]))
    mgr.on(on_msg('판끝'), setv('삼목차례', 0),
           if_(eq(V('삼목승자'), 1), chg('삼목승', 1)), if_(eq(V('삼목승자'), 3), chg('삼목무', 1)),
           wait(1.5), chg('라운드', 1),
           ifelse(gt(V('라운드'), R), [*m.end_blocks(add(mul(V('삼목승'), 40), mul(V('삼목무'), 20)))],
                  [*new_round, setv('미니표시', join(V('라운드'), '판 · 승 ', V('삼목승'))),
                   ifelse(eq(mod(V('라운드'), 2), 0), [wait(0.5), *ai, setv('삼목차례', 1), cast('삼목갱신')],
                          [setv('삼목차례', 1), cast('삼목갱신')])]))
    mgr.on(on_msg('게임시작'), setv('라운드', 1), *new_round, setv('삼목차례', 1), cast('삼목갱신'))
    m.on_start(setv('삼목승', 0), setv('삼목무', 0), setv('삼목차례', 0), *new_round)
    m.snd('삼목놓음', play('tick'))
    m.snd('판끝', ifelse(eq(V('삼목승자'), 1), [play('good')], [ifelse(eq(V('삼목승자'), 2), [play('bad')], [play('beep')])]))
    m.finish('마을회관 이장님과 삼목 3판 승부!\n가로·세로·대각선으로 내 돌 3개를 먼저 놓으면 승리.',
             '조작: 빈 칸 클릭  ·  승리 40점, 무승부 20점  ·  2판째는 이장님이 먼저')
    return True


def eq_n(a, b):
    """정수 a, b 가 같으면 1, 다르면 0 (숫자 계산으로)."""
    d = abs_(sub(a, b))
    return sub(1, div(sub(add(d, 1), abs_(sub(d, 1))), 2))


# ================================================================== 23. 과일 상자 쌓기 (쌓기)
def g23(P, ctx):
    _vars(P, '상자x', '상자폭', '상자방향', '상자속도', '꼭대기y', '바닥0', '바닥1', '_o0', '_o1', '완벽')
    m = MG(P, 23, ctx, time_limit=50, status='0층', dim=60)
    widths = list(range(4, 124, 4))
    pics = [('w%d' % w, A2.crate_w(w)) for w in widths]
    m.S('트럭', A2.truck_bed(150, 30), 0, -104)
    placed = m.S('쌓인상자', pics, 0, -300, visible=False)
    placed.local('복제', 0)
    placed.on(on_msg('상자놓기'), clone_self())
    placed.on(on_clone(), if_(eq(V('복제'), 0), setv('복제', 1), shape(div(V('상자폭'), 4)), xy(div(add(V('_o0'), V('_o1')), 2), V('꼭대기y')),
                                show()))
    placed.on(on_msg('내리기'), if_(eq(V('복제'), 1), rep(4, mvy(-4), wait(0.016))))
    mover = m.S('움직이는상자', pics, 0, -74, visible=False)
    mover.on(on_msg('게임시작'), show(),
             until(eq(V('게임중'), 0),
                   if_(eq(V('대기'), 1),
                       chg('상자x', mul(V('상자방향'), V('상자속도'))),
                       if_(gt(add(V('상자x'), div(V('상자폭'), 2)), 210), setv('상자방향', -1)),
                       if_(lt(sub(V('상자x'), div(V('상자폭'), 2)), -210), setv('상자방향', 1))),
                   shape(div(V('상자폭'), 4)), xy(V('상자x'), add(V('꼭대기y'), 0))),
             hide())
    drop = [if_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)),
                setv('대기', 0),
                setv('_o0', sub(V('상자x'), div(V('상자폭'), 2))), setv('_o1', add(V('상자x'), div(V('상자폭'), 2))),
                setv('완벽', 0),
                if_(lt(abs_(sub(V('상자x'), div(add(V('바닥0'), V('바닥1')), 2))), 4),
                    setv('완벽', 1), setv('_o0', V('바닥0')), setv('_o1', V('바닥1'))),
                if_(lt(V('_o0'), V('바닥0')), setv('_o0', V('바닥0'))), if_(gt(V('_o1'), V('바닥1')), setv('_o1', V('바닥1'))),
                ifelse(lt(sub(V('_o1'), V('_o0')), 4), [cast('상자빗나감'), wait(0.8), *m.end_blocks(mul(V('합계'), 100.0 / 14))],
                       [setv('상자폭', mul(floor(div(sub(V('_o1'), V('_o0')), 4)), 4)),
                        setv('_o1', add(V('_o0'), V('상자폭'))),
                        cast('상자놓기'), chg('합계', 1), ifelse(eq(V('완벽'), 1), [cast('완벽')], [cast('쿵')]),
                        setv('미니표시', join(V('합계'), '층')),
                        setv('바닥0', V('_o0')), setv('바닥1', V('_o1')),
                        chg('꼭대기y', 16), chg('상자속도', 0.22),
                        if_(gt(V('꼭대기y'), 20), cast('내리기'), chg('꼭대기y', -16)),
                        setv('상자x', mul(-150, V('상자방향'))),
                        wait(0.15), setv('대기', 1)]))]
    keys = hidden(m, '상자키')
    keys.on(on_key(K_SPACE), *drop)
    keys.on(on_mouse_down(), *drop)
    perfect = m.S('완벽글', K.big_text('딱 맞다!', 22, 'royal'), 0, 60, visible=False)
    perfect.on(on_msg('완벽'), show(), wait(0.5), hide())
    miss = m.S('빗나감글', K.big_text('와르르...', 26, 'red'), 0, 30, visible=False)
    miss.on(on_msg('상자빗나감'), show())
    mgr = hidden(m, '상자담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 100.0 / 14)))
    m.on_start(setv('합계', 0), setv('상자폭', 120), setv('상자x', -150), setv('상자방향', 1), setv('상자속도', 2.2),
               setv('꼭대기y', -74), setv('바닥0', -60), setv('바닥1', 60), setv('대기', 1))
    m.snd('쿵', play('hit'))
    m.snd('완벽', play('good'))
    m.snd('상자빗나감', play('fail_big'))
    m.finish('과수원 트럭에 과일 상자를 높이 쌓으세요!\n아래 상자와 어긋난 부분은 잘려 나가요. 딱 맞추면 그대로!',
             '조작: SPACE 또는 마우스 클릭으로 떨어뜨리기  ·  14층이면 만점')
    return True


# ================================================================== 25. 연기향교 제기차기
def g25(P, ctx):
    _vars(P, '제기x', '제기y', '제기vx', '제기vy', '발x', '떨굼', '차는중')
    m = MG(P, 25, ctx, time_limit=40, status='0번 · 떨굼 0/3', dim=50)
    kid = m.S('제기꾼', [('s', A2.kicker('stand')), ('k', A2.kicker('kick'))], 0, -88)
    jg = m.S('제기', A2.jegi(), 0, 100)
    kid.on(on_msg('게임시작'), setv('발x', 0),
           until(eq(V('게임중'), 0),
                 if_(key(K_LEFT), chg('발x', -3.4)), if_(key(K_RIGHT), chg('발x', 3.4)),
                 *clamp_blocks('발x', -210, 210), lx(V('발x'))))
    kid.on(on_msg('차기'), shape('k'), wait(0.18), shape('s'))
    jg.on(on_msg('게임시작'), setv('제기x', 0), setv('제기y', 100), setv('제기vx', 0), setv('제기vy', 0),
          until(eq(V('게임중'), 0),
                chg('제기vy', -0.2), chg('제기x', V('제기vx')), chg('제기y', V('제기vy')),
                if_(gt(abs_(V('제기x')), 220), setv('제기vx', mul(V('제기vx'), -1)), *clamp_blocks('제기x', -220, 220)),
                xy(V('제기x'), V('제기y')), rot(mul(V('제기vx'), 6)),
                if_(lt(V('제기y'), -125),
                    chg('떨굼', 1), cast('떨굼'), setv('미니표시', join(V('합계'), '번 · 떨굼 ', V('떨굼'), '/3')),
                    if_(ge(V('떨굼'), 3), *m.end_blocks(mul(V('합계'), 100.0 / 30))),
                    wait(0.7), setv('제기x', V('발x')), setv('제기y', 110), setv('제기vx', 0), setv('제기vy', 0))))
    kick = [if_(and_(eq(V('게임중'), 1), eq(V('차는중'), 0)),
                setv('차는중', 1), cast('차기'),
                if_(and_(and_(lt(abs_(sub(V('제기x'), V('발x'))), 30), lt(V('제기vy'), 0)),
                         and_(gt(V('제기y'), -100), lt(V('제기y'), -40))),
                    setv('제기vy', add(6.6, div(rnd(0, 10), 10))),
                    setv('제기vx', add(mul(sub(V('제기x'), V('발x')), 0.09), div(rnd(-12, 12), 10))),
                    chg('합계', 1), cast('뻥'), setv('미니표시', join(V('합계'), '번 · 떨굼 ', V('떨굼'), '/3'))),
                wait(0.22), setv('차는중', 0))]
    hidden(m, '제기키').on(on_key(K_SPACE), *kick)
    cnt = m.T('제기수', '', 0, 60, 30, C_WHITE, F_NUM, False, 0, w=120, h=40)
    cnt.on(on_msg('뻥'), write(V('합계')), cnt.pct(130), rep(5, cnt.grow_pct(-6), wait(0.016)))
    mgr = hidden(m, '제기담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 100.0 / 30)))
    m.on_start(setv('합계', 0), setv('떨굼', 0), setv('차는중', 0))
    m.snd('뻥', play('pop'))
    m.snd('떨굼', play('bad'))
    m.finish('연기향교 마당에서 제기차기! 제기가 발 위로 내려올 때\nSPACE 로 차 올리세요. 30번이면 만점, 3번 떨어뜨리면 끝!',
             '조작: ← → 이동, SPACE 차기  ·  제기 바로 밑에 서야 잘 맞아요')
    return True


# ================================================================== 19. 봉산리 향나무 투호 (투척)
def g19(P, ctx):
    N = 10
    _vars(P, '힘', '힘방향', '충전', '화살x', '화살y', '화살vx', '화살vy', '항아리x', '던진수', '넣은수')
    m = MG(P, 19, ctx, status='0/%d 넣음' % N, dim=40)
    SX, SY, JY = -170, -40, -72
    m.S('던지는사람', A2.kicker('stand'), -200, -78)
    jar = m.S('항아리', A2.tuho_jar(False), 100, JY)
    jar.on(on_msg('새던지기'), lx(V('항아리x')))
    arrow = m.S('화살', A2.tuho_arrow(), SX, SY)
    arrow.local('복제', 0)
    jar_f = m.S('항아리앞', A2.tuho_jar(True), 100, JY)
    jar_f.on(on_msg('새던지기'), lx(V('항아리x')))
    pw = m.S('힘막대', K.bar_set('tuho_power', 90, 10, 'royal'), -190, -112)
    m.T('힘글', '힘', -248 + 14, -112, 9, C_WHITE, F_NUM, False, 0, w=20, h=12)
    pw.on(on_msg('게임시작'), until(eq(V('게임중'), 0), shape(add(floor(mul(div(V('힘'), 100), 40)), 1)), wait(0.03)))
    res = m.S('투호결과', [('o', K.big_text('쏙!', 34, 'royal')), ('x', K.big_text('아깝다!', 26, 'red'))], 40, 40, visible=False)
    res.on(on_msg('넣음'), shape('o'), res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.016)), wait(0.6), hide())
    res.on(on_msg('놓침'), shape('x'), show(), wait(0.6), hide())
    holding = or_(mouse_down(), key(K_SPACE))
    fly = [setv('화살vx', mul(add(3, mul(V('힘'), 0.07)), 0.643)), setv('화살vy', mul(add(3, mul(V('힘'), 0.07)), 0.766)),
           setv('화살x', SX), setv('화살y', SY), setv('_mk', 0),
           until(not_(eq(V('_mk'), 0)),
                 chg('화살vy', -0.18), chg('화살x', V('화살vx')), chg('화살y', V('화살vy')),
                 xy(V('화살x'), V('화살y')), rot(mul(-1, fn('atan_radian', div(V('화살vy'), V('화살vx'))))),
                 if_(and_(lt(V('화살vy'), 0), and_(lt(V('화살y'), add(JY, 32)), gt(V('화살y'), add(JY, 22)))),
                     if_(lt(abs_(sub(V('화살x'), V('항아리x'))), 11), setv('_mk', 1), xy(V('항아리x'), add(JY, 30)), rot(80))),
                 if_(or_(lt(V('화살y'), -118), gt(V('화살x'), 250)), setv('_mk', 2))),
           ifelse(eq(V('_mk'), 1), [chg('넣은수', 1), cast('넣음')], [cast('놓침')]),
           clone_self(), wait(0.6)]
    arrow.on(on_clone(), setv('복제', 1))
    arrow.on(on_msg('새던지기'), if_(eq(V('복제'), 1), del_clone()))
    arrow.on(on_msg('게임시작'),
             setv('던진수', 0),
             until(or_(ge(V('던진수'), N), eq(V('게임중'), 0)),
                   setv('항아리x', rnd(10, 190)), cast('새던지기'), xy(SX, SY), rot(-40), setv('힘', 0), setv('힘방향', 1),
                   setv('미니표시', join(V('넣은수'), '/', N, ' 넣음 · ', add(V('던진수'), 1), '번째')),
                   wait_until(holding), cast('충전'),
                   until(not_(holding), chg('힘', mul(V('힘방향'), 2.6)),
                         if_(gt(V('힘'), 100), setv('힘', 100), setv('힘방향', -1)),
                         if_(lt(V('힘'), 0), setv('힘', 0), setv('힘방향', 1))),
                   cast('휙'), *fly, chg('던진수', 1)),
             *m.end_blocks(mul(V('넣은수'), 100.0 / N)))
    m.on_start(setv('넣은수', 0), setv('던진수', 0), setv('힘', 0), setv('항아리x', 100))
    m.snd('휙', play('jump'))
    m.snd('넣음', play('good'))
    m.snd('놓침', play('bad'))
    m.finish('봉산리 향나무 아래 전통 놀이 투호! 화살 10개를\n항아리에 넣으세요. 항아리 위치는 매번 바뀌어요.',
             '조작: 마우스(또는 SPACE)를 누르고 있으면 힘이 오르내리고, 떼는 순간 던져요')
    return True


# ================================================================== 20. 봉산로 숲길 그림 퍼즐 (슬라이딩)
def g20(P, ctx):
    TL = 90
    P.list('퍼즐판', list(range(1, 10)))
    P.list('퍼즐위치', list(range(1, 9)))
    _vars(P, '빈칸', '이동수', '맞은칸', '_pd', '_pp')
    m = MG(P, 20, ctx, time_limit=TL, status='0번 이동', dim=110)
    tiles = A2.puzzle_tiles(3, 64)
    cx = lambda pos: add(-96, mul(mod(sub(pos, 1), 3), 64))
    cy = lambda pos: sub(50, mul(floor(div(sub(pos, 1), 3)), 64))
    panel(P, m.sc, '퍼즐판넬', -32, -14, 206, 206, 'glass')
    m.S('완성그림', A2.puzzle_preview(96), 160, 30)
    m.T('완성글', '완성 그림', 160, -26, 9, C_DIM, F_NUM, False, 0, w=90, h=14)
    for k in range(1, 9):
        t = m.S('조각%d' % k, tiles[k - 1], 0, 0)
        t.on(on_msg('퍼즐놓기'), xy(cx(LGET('퍼즐위치', k)), cy(LGET('퍼즐위치', k))))
        t.on(on_msg('퍼즐이동'), if_(eq(V('_pd'), k), glide(0.08, cx(LGET('퍼즐위치', k)), cy(LGET('퍼즐위치', k)))))
        p_, b_ = LGET('퍼즐위치', k), V('빈칸')
        adj = or_(and_(eq(floor(div(sub(p_, 1), 3)), floor(div(sub(b_, 1), 3))), eq(abs_(sub(p_, b_)), 1)), eq(abs_(sub(p_, b_)), 3))
        t.on(on_click(), if_(and_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)), adj),
                             setv('_pp', p_), lst_set('퍼즐판', V('빈칸'), k), lst_set('퍼즐판', V('_pp'), 9),
                             lst_set('퍼즐위치', k, V('빈칸')), setv('빈칸', V('_pp')), setv('_pd', k),
                             chg('이동수', 1), cast('퍼즐이동'), cast('퍼즐검사')))
    done = m.S('퍼즐완성', K.big_text('완성!', 36, 'royal'), -32, -14, visible=False)
    done.on(on_msg('퍼즐완성'), done.pct(130), show(), rep(5, done.grow_pct(-6), wait(0.016)))
    count = [setv('맞은칸', 0), *[if_(eq(LGET('퍼즐판', i), i), chg('맞은칸', 1)) for i in range(1, 9)]]
    mgr = hidden(m, '퍼즐담당')
    mgr.on(on_msg('퍼즐검사'), *count, setv('미니표시', join(V('이동수'), '번 이동 · 맞은 조각 ', V('맞은칸'), '/8')),
           if_(eq(V('맞은칸'), 8), setv('대기', 0), cast('퍼즐완성'), wait(1.2), *m.end_blocks(add(70, mul(V('남은시간'), 0.6)))))
    mgr.on(on_msg('시간끝'), *count, *m.end_blocks(mul(V('맞은칸'), 6)))
    # 섞기: 빈칸을 60번 무작위로 움직인다 (항상 풀 수 있음)
    shuffle = [setv('_mi', 0), setv('_ma', 0),
               rep(70, setv('_mk', rnd(1, 4)),
                   setv('_mb', 0),
                   if_(and_(eq(V('_mk'), 1), gt(V('빈칸'), 3)), setv('_mb', sub(V('빈칸'), 3))),
                   if_(and_(eq(V('_mk'), 2), le(V('빈칸'), 6)), setv('_mb', add(V('빈칸'), 3))),
                   if_(and_(eq(V('_mk'), 3), gt(mod(sub(V('빈칸'), 1), 3), 0)), setv('_mb', sub(V('빈칸'), 1))),
                   if_(and_(eq(V('_mk'), 4), lt(mod(sub(V('빈칸'), 1), 3), 2)), setv('_mb', add(V('빈칸'), 1))),
                   if_(and_(gt(V('_mb'), 0), ne(V('_mb'), V('_ma'))),
                       setv('_ma', V('빈칸')), setv('_pd', LGET('퍼즐판', V('_mb'))),
                       lst_set('퍼즐판', V('빈칸'), V('_pd')), lst_set('퍼즐위치', V('_pd'), V('빈칸')),
                       lst_set('퍼즐판', V('_mb'), 9), setv('빈칸', V('_mb'))))]
    m.on_start(setv('이동수', 0), setv('대기', 0), setv('빈칸', 9),
               *[lst_set('퍼즐판', i, i) for i in range(1, 10)], *[lst_set('퍼즐위치', i, i) for i in range(1, 9)],
               *shuffle, *count, cast('퍼즐놓기'), setv('대기', 1))
    m.snd('퍼즐이동', play('tick'))
    m.snd('퍼즐완성', play('fanfare'))
    m.finish('봉산로 숲길 사진이 뒤섞였어요! 빈칸 옆 조각을 눌러\n밀어서 오른쪽 완성 그림처럼 맞추세요. (90초)',
             '조작: 빈칸 바로 옆 조각 클릭  ·  빨리 맞출수록 점수 UP')
    return True


# ================================================================== 21. 송곡리 승부차기
def g21(P, ctx):
    R = 10
    _vars(P, '키퍼방향', '텔', '슛방향', '입력방향', '골수', '막은수', '공x', '공y', '공tx', '공ty', '공틱')
    m = MG(P, 21, ctx, status='골 0 · 선방 0', dim=60)
    TX = {1: -92, 2: 0, 3: 92}
    m.S('골대', A2.goal_frame(), 0, 40)
    kp = m.S('골키퍼', [(p, A2.keeper(p)) for p in ('c', 'l', 'r', 'tl', 'tr')], 0, 12)
    bl = m.S('축구공', A2.soccer_ball(20), 0, -90)
    for d, x in (('l', -60), ('c', 0), ('r', 60)):
        o = m.S('조준%s' % d, A2.aim_arrow(d), x, -60, visible=False)
        o.on(on_msg('차기안내'), show())
        o.on(on_msg('안내끝'), hide())
    role = m.T('승부역할', '', 0, -118, 12, C_WHITE, F_NUM, False, 0, w=360, h=18, bg=C_BOX)
    role.on(on_msg('차기안내'), write('내가 찬다! ← ↓ → 로 방향 고르기 (키퍼 몸짓을 읽어라)'))
    role.on(on_msg('막기안내'), write('내가 막는다! 공이 날아가는 쪽으로 ← ↓ → !'))
    res = m.S('승부결과', [('g', K.big_text('골!', 40, 'royal')), ('s', K.big_text('선방!', 36, 'royal')),
                          ('n', K.big_text('막혔다...', 28, 'red')), ('m', K.big_text('먹혔다...', 28, 'red'))], 0, 70, visible=False)
    res.on(on_msg('승부판정'), shape(V('_mk')), res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.016)), wait(0.8), hide())
    keyset = hidden(m, '승부키')
    for kc, dv in ((K_LEFT, 1), (K_DOWN, 2), (K_RIGHT, 3)):
        keyset.on(on_key(kc), if_(and_(eq(V('게임중'), 1), and_(eq(V('대기'), 1), eq(V('입력방향'), 0))), setv('입력방향', dv)))
    dive = lambda var: [ifelse(eq(V(var), 1), [shape('l')], [ifelse(eq(V(var), 3), [shape('r')], [shape('c')])])]
    kp.on(on_msg('키퍼텔'), ifelse(eq(V('텔'), 1), [shape('tl')], [ifelse(eq(V('텔'), 3), [shape('tr')], [shape('c')])]))
    kp.on(on_msg('키퍼날기'), *dive('키퍼방향'))
    kp.on(on_msg('내가날기'), *dive('입력방향'))
    kp.on(on_msg('키퍼서기'), shape('c'), xy(0, 12))
    bl.on(on_msg('공날기'), setv('공x', 0), setv('공y', -90),
          rep(20, chg('공x', div(V('공tx'), 20)), chg('공y', div(sub(V('공ty'), -90), 20)),
              xy(V('공x'), V('공y')), bl.grow_pct(-1.5), rot_by(20), wait(V('공틱'))))
    bl.on(on_msg('공제자리'), xy(0, -90), bl.pct(100))
    target = lambda var: [ifelse(eq(V(var), 1), [setv('공tx', -92)], [ifelse(eq(V(var), 3), [setv('공tx', 92)], [setv('공tx', 0)])]),
                          setv('공ty', ifelse_y(var))]
    mgr = hidden(m, '승부담당')
    mgr.on(on_msg('게임시작'), setv('라운드', 1),
           until(gt(V('라운드'), R),
                 cast('키퍼서기'), cast('공제자리'), setv('입력방향', 0), setv('대기', 0), wait(0.6),
                 ifelse(eq(mod(V('라운드'), 2), 1),
                        # 내가 차기: 키퍼 몸짓(70% 진짜) 보고 반대로
                        [setv('키퍼방향', rnd(1, 3)), setv('텔', V('키퍼방향')),
                         if_(gt(rnd(1, 100), 70), setv('텔', rnd(1, 3))),
                         cast('키퍼텔'), cast('차기안내'), setv('대기', 1),
                         setv('_mt', 0), until(or_(gt(V('입력방향'), 0), ge(V('_mt'), 1.8)), wait(0.05), chg('_mt', 0.05)),
                         setv('대기', 0), cast('안내끝'), if_(eq(V('입력방향'), 0), setv('입력방향', 2)),
                         setv('슛방향', V('입력방향')), *target('슛방향'), setv('공틱', 0.01), cast('찼다'), cast('공날기'),
                         cast('키퍼날기'), wait(0.45),
                         ifelse(ne(V('슛방향'), V('키퍼방향')), [setv('_mk', 1), chg('골수', 1)], [setv('_mk', 3)])],
                        # 내가 막기: 공이 날아가는 쪽으로 몸 날리기
                        [cast('막기안내'), wait(0.7), setv('슛방향', rnd(1, 3)), *target('슛방향'),
                         setv('공틱', sub(0.03, mul(V('라운드'), 0.001))), setv('대기', 1), cast('찼다'), cast('공날기'),
                         setv('_mt', 0),
                         rep(24, if_(eq(V('_mt'), 0), if_(gt(V('입력방향'), 0), setv('_mt', 1), cast('내가날기'))),
                             wait(V('공틱'))),
                         setv('대기', 0), wait(0.15),
                         ifelse(eq(V('입력방향'), V('슛방향')), [setv('_mk', 2), chg('막은수', 1)], [setv('_mk', 4)])]),
                 cast('승부판정'), setv('미니표시', join('골 ', V('골수'), ' · 선방 ', V('막은수'))),
                 wait(1.0), chg('라운드', 1)),
           *m.end_blocks(mul(add(V('골수'), V('막은수')), 100.0 / R)))
    m.on_start(setv('골수', 0), setv('막은수', 0), setv('대기', 0))
    m.snd('찼다', play('hit'))
    m.snd('승부판정', ifelse(le(V('_mk'), 2), [play('good')], [play('bad')]))
    m.finish('송곡리 마을 축구 승부차기 10번! (차기 5 + 막기 5)\n찰 땐 키퍼 몸짓을 읽고, 막을 땐 공 방향으로 몸을 날려요.',
             '조작: ← 왼쪽 · ↓ 가운데 · → 오른쪽')
    return True


def ifelse_y(var):
    """구석(1,3)은 조금 낮게, 가운데(2)는 높게: 공 도착 y."""
    return sub(48, mul(eq_n(V(var), 2), -12))


# ================================================================== 22. 금이로 고개 낙석 피하기 (마우스 피하기)
def g22(P, ctx):
    TL = 30
    _vars(P, '차x', '차y', '맞음', '무적')
    m = MG(P, 22, ctx, time_limit=TL, status='♥5', dim=30)
    car = m.S('유세차', A2.campaign_car(), 0, -80)
    rk = m.S('낙석', [('r%d' % k, A2.rock(k)) for k in range(3)], 0, 200, visible=False)
    for v in ('복제', 'vx', 'vy'):
        rk.local(v, 0)
    rk.on(on_msg('게임시작'), until(eq(V('게임중'), 0), clone_self(),
                                  wait(div(sub(50, mul(sub(TL, V('남은시간')), 1.0)), 100))))
    rk.on(on_clone(), setv('복제', 1), shape(rnd(1, 3)), xy(rnd(-220, 220), 150), setv('vy', div(rnd(-30, -10), 10)),
          setv('vx', 0), if_(le(rnd(1, 100), 30), setv('vx', div(rnd(-20, 20), 10))), show(),
          until(or_(lt(obj_y(), -150), eq(V('게임중'), 0)),
                chg('vy', -0.12), mvx(V('vx')), mvy(V('vy')), rot_by(mul(V('vx'), 3)),
                if_(gt(abs_(obj_x()), 235), setv('vx', mul(V('vx'), -1)))),
          del_clone())
    car.on(on_msg('게임시작'), setv('차x', 0), setv('차y', -80),
           until(eq(V('게임중'), 0),
                 chg('차x', mul(sub(mouse_x(), V('차x')), 0.3)), chg('차y', mul(sub(mouse_y(), V('차y')), 0.3)),
                 *clamp_blocks('차x', -220, 220), *clamp_blocks('차y', -112, 80),
                 xy(V('차x'), V('차y')),
                 if_(and_(eq(V('무적'), 0), touch(rk.name)),
                     chg('맞음', 1), setv('무적', 1), cast('쿵'), setv('미니표시', join('♥', sub(5, V('맞음')))),
                     if_(ge(V('맞음'), 5), *m.end_blocks(mul(div(sub(TL, V('남은시간')), TL), 40))))))
    car.on(on_msg('쿵'), rep(5, fx('transparency', 70), wait(0.1), fx('transparency', 0), wait(0.1)), setv('무적', 0))
    mgr = hidden(m, '낙석담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(100, mul(V('맞음'), 18))))
    m.on_start(setv('맞음', 0), setv('무적', 0))
    m.snd('쿵', play('hit'))
    m.finish('금이로 고갯길에 낙석 주의! 유세차를 마우스로 움직여\n떨어지는 돌을 30초 동안 피하세요. 5번 맞으면 끝!',
             '조작: 마우스 포인터를 따라 유세차가 움직여요  ·  한 번 맞을 때마다 -18점')
    return True


# ================================================================== 26. 서북부 택지지구 유세 행렬 모으기 (뱀 게임)
def g26(P, ctx):
    TL, COLS, ROWS = 60, 20, 11
    X0, Y0, CELL = -152, 68, 16
    P.list('뱀몸', [])
    P.list('뱀칸', [0] * (COLS * ROWS))
    _vars(P, '뱀방향', '뱀다음', '뱀c', '뱀r', '먹이', '뱀목숨', '_nc', '_nr', '_ni', '뱀자람')
    m = MG(P, 26, ctx, time_limit=TL, status='행렬 0명 · ♥2', dim=80)
    m.S('뱀바닥', A2.grid_floor(COLS, ROWS, CELL, 'snake_floor'), X0 + (COLS - 1) * CELL / 2, Y0 - (ROWS - 1) * CELL / 2)
    cx = lambda idx: add(X0, mul(mod(sub(idx, 1), COLS), CELL))
    cy = lambda idx: sub(Y0, mul(floor(div(sub(idx, 1), COLS)), CELL))
    food = m.S('시민', A2.snake_part('food'), 0, 0)
    food.on(on_msg('먹이갱신'), xy(cx(V('먹이')), cy(V('먹이'))), food.pct(140), rep(4, food.grow_pct(-10), wait(0.016)))
    body = m.S('행렬', A2.snake_part('body'), 0, -300, visible=False)
    body.local('복제', 0)
    body.local('내번호', 0)
    body.on(on_msg('뱀새몸'), if_(eq(V('복제'), 0), setv('내번호', LLEN('뱀몸')), clone_self()))
    body.on(on_clone(), setv('복제', 1), xy(cx(LGET('뱀몸', V('내번호'))), cy(LGET('뱀몸', V('내번호')))), show())
    body.on(on_msg('뱀이동'), if_(and_(eq(V('복제'), 1), le(V('내번호'), LLEN('뱀몸'))),
                               xy(cx(LGET('뱀몸', V('내번호'))), cy(LGET('뱀몸', V('내번호'))))))
    body.on(on_msg('뱀초기화'), if_(eq(V('복제'), 1), del_clone()))
    head = m.S('행렬머리', A2.snake_part('head'), 0, 0)
    head.on(on_msg('뱀이동'), xy(cx(LGET('뱀몸', 1)), cy(LGET('뱀몸', 1))))
    head.on(on_msg('뱀꽝'), rep(4, fx('transparency', 70), wait(0.08), fx('transparency', 0), wait(0.08)))
    keys = hidden(m, '뱀키')
    for kc, dv, opp in ((K_UP, 1, 3), (K_RIGHT, 2, 4), (K_DOWN, 3, 1), (K_LEFT, 4, 2)):
        keys.on(on_key(kc), if_(and_(eq(V('게임중'), 1), ne(V('뱀방향'), opp)), setv('뱀다음', dv)))
    clear = [until(eq(LLEN('뱀몸'), 0), lst_set('뱀칸', LGET('뱀몸', 1), 0), lst_del('뱀몸', 1))]
    start_cell = 5 * COLS + 6
    reset = [cast('뱀초기화'), *clear,
             lst_add('뱀몸', start_cell), lst_add('뱀몸', start_cell - 1), lst_add('뱀몸', start_cell - 2),
             lst_set('뱀칸', start_cell, 1), lst_set('뱀칸', start_cell - 1, 1), lst_set('뱀칸', start_cell - 2, 1),
             setv('뱀방향', 2), setv('뱀다음', 2), setv('뱀c', 5), setv('뱀r', 5),
             wait(0.05), cast('뱀새몸'), wait(0.05), cast('뱀새몸'), cast('뱀이동')]
    new_food = [setv('먹이', rnd(1, COLS * ROWS)), until(eq(LGET('뱀칸', V('먹이')), 0), setv('먹이', rnd(1, COLS * ROWS))),
                cast('먹이갱신')]
    die = [chg('뱀목숨', -1), cast('뱀꽝'), setv('미니표시', join('행렬 ', V('합계'), '명 · ♥', V('뱀목숨'))),
           ifelse(le(V('뱀목숨'), 0), [*m.end_blocks(mul(V('합계'), 7))], [wait(0.6), *reset])]
    mgr = hidden(m, '뱀담당')
    mgr.on(on_msg('게임시작'),
           until(eq(V('게임중'), 0),
                 wait(sub(0.13, mul(V('합계'), 0.0025))),
                 setv('뱀방향', V('뱀다음')),
                 setv('_nc', V('뱀c')), setv('_nr', V('뱀r')),
                 if_(eq(V('뱀방향'), 1), chg('_nr', -1)), if_(eq(V('뱀방향'), 2), chg('_nc', 1)),
                 if_(eq(V('뱀방향'), 3), chg('_nr', 1)), if_(eq(V('뱀방향'), 4), chg('_nc', -1)),
                 ifelse(or_(or_(lt(V('_nc'), 0), ge(V('_nc'), COLS)), or_(lt(V('_nr'), 0), ge(V('_nr'), ROWS))), [*die],
                        [setv('_ni', add(add(mul(V('_nr'), COLS), V('_nc')), 1)),
                         setv('뱀자람', eq_n(V('_ni'), V('먹이'))),
                         if_(eq(V('뱀자람'), 0), lst_set('뱀칸', LGET('뱀몸', LLEN('뱀몸')), 0), lst_del('뱀몸', LLEN('뱀몸'))),
                         ifelse(eq(LGET('뱀칸', V('_ni')), 1), [*die],
                                [lst_ins('뱀몸', 1, V('_ni')), lst_set('뱀칸', V('_ni'), 1), setv('뱀c', V('_nc')), setv('뱀r', V('_nr')),
                                 cast('뱀이동'),
                                 if_(eq(V('뱀자람'), 1), chg('합계', 1), cast('뱀새몸'), cast('냠'), *new_food,
                                     setv('미니표시', join('행렬 ', V('합계'), '명 · ♥', V('뱀목숨'))))])])))
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 7)))
    m.on_start(setv('합계', 0), setv('뱀목숨', 2), *reset, *new_food)
    m.snd('냠', play('coin'))
    m.snd('뱀꽝', play('hit'))
    m.finish('서북부 새 아파트 단지! 방향키로 유세 행렬을 이끌고\n시민들을 모으세요. 벽이나 내 행렬에 부딪히면 ♥ 하나 잃어요.',
             '조작: ↑ ↓ ← → 방향 바꾸기  ·  60초  ·  15명이면 만점')
    return True


# ================================================================== 27. 신흥리 복숭아 썰기 (썰기)
def g27(P, ctx):
    TL = 30
    _vars(P, '칼속도', '_pmx', '_pmy', '벌레썬')
    m = MG(P, 27, ctx, time_limit=TL, status='0개', dim=50)
    pc = m.S('날복숭아', [('p', A.peach('ripe')), ('b', A2.bug()), ('c', A2.peach_cut())], 0, -200, visible=False)
    for v in ('복제', 'vx', 'vy', '종', '썰림'):
        pc.local(v, 0)
    pc.on(on_msg('게임시작'), until(eq(V('게임중'), 0), clone_self(), if_(le(rnd(1, 100), 35), wait(0.12), clone_self()),
                                  wait(div(rnd(45, 75), 100))))
    pc.on(on_clone(), setv('복제', 1), setv('썰림', 0),
          ifelse(le(rnd(1, 100), 16), [setv('종', 2), shape('b')], [setv('종', 1), shape('p')]),
          xy(rnd(-170, 170), -150), setv('vx', div(rnd(-20, 20), 10)), setv('vy', div(rnd(78, 98), 10)),
          if_(gt(obj_x(), 60), setv('vx', div(rnd(-28, -5), 10))), if_(lt(obj_x(), -60), setv('vx', div(rnd(5, 28), 10))),
          show(),
          until(or_(and_(lt(obj_y(), -160), lt(V('vy'), 0)), eq(V('게임중'), 0)),
                chg('vy', -0.17), mvx(V('vx')), mvy(V('vy')), rot_by(mul(V('vx'), 2)),
                if_(and_(and_(eq(V('썰림'), 0), mouse_down()), and_(touch('mouse'), gt(V('칼속도'), 5))),
                    setv('썰림', 1),
                    ifelse(eq(V('종'), 1), [chg('합계', 1), shape('c'), cast('썰기')], [chg('벌레썬', 1), cast('벌레')]),
                    setv('미니표시', join(V('합계'), '개 · 벌레 ', V('벌레썬'))),
                    if_(eq(V('종'), 2), hide()))),
          del_clone())
    blade = m.S('칼날', A2.blade_dot(), 0, -300, visible=False)
    blade.local('복제', 0)
    blade.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                     setv('칼속도', fn('root', add(mul(sub(mouse_x(), V('_pmx')), sub(mouse_x(), V('_pmx'))),
                                                                   mul(sub(mouse_y(), V('_pmy')), sub(mouse_y(), V('_pmy')))))),
                                     setv('_pmx', mouse_x()), setv('_pmy', mouse_y()),
                                     if_(mouse_down(), clone_self())))
    blade.on(on_clone(), setv('복제', 1), xy(mouse_x(), mouse_y()), show(), rep(8, blade.grow_pct(-10), fx_add('transparency', 12)),
             del_clone())
    bad = m.S('벌레경고', K.big_text('벌레! -10', 22, 'red'), 0, 40, visible=False)
    bad.on(on_msg('벌레'), show(), wait(0.5), hide())
    mgr = hidden(m, '썰기담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(V('합계'), 4), mul(V('벌레썬'), 10))))
    m.on_start(setv('합계', 0), setv('벌레썬', 0))
    m.snd('썰기', play('pop'))
    m.snd('벌레', play('bad'))
    m.finish('신흥리 복숭아밭! 날아오르는 복숭아를 마우스로 썰어요.\n초록 벌레를 썰면 -10점! (25개면 만점)',
             '조작: 마우스 버튼을 누른 채로 빠르게 그어서 썰기')
    return True


# ================================================================== 28. 죽림리 대숲 함정 찾기 (지뢰찾기)
def g28(P, ctx):
    TL, C, R, NT = 120, 9, 6, 10
    N = C * R
    X0, Y0, CL = -126, 46, 24
    P.list('함정', [0] * N)
    P.list('대숲열림', [0] * N)
    P.list('대숲수', [0] * N)
    P.list('대숲큐', [])
    _vars(P, '대숲모드', '대숲생성', '대숲목숨', '연칸', '_qc', '_qr', '_qi', '대숲클릭')
    m = MG(P, 28, ctx, time_limit=TL, status='0/%d칸 · ♥2' % (N - NT), dim=100)
    panel(P, m.sc, '대숲판', X0 + (C - 1) * CL / 2, Y0 - (R - 1) * CL / 2, C * CL + 16, R * CL + 16, 'glass')
    kinds = ['hid', 'flag', 'boom', 'trap'] + ['n%d' % i for i in range(9)]
    cell = m.S('대숲칸', [(k, A2.mine_cell(k)) for k in kinds], 0, -300, visible=False)
    cell.local('복제', 0)
    cell.local('내번호', 0)
    cell.on(on_scene(), setv('내번호', 0), rep(N, chg('내번호', 1), clone_self()))
    cell.on(on_clone(), setv('복제', 1), xy(add(X0, mul(mod(sub(V('내번호'), 1), C), CL)), sub(Y0, mul(floor(div(sub(V('내번호'), 1), C)), CL))),
            shape('hid'), show())
    st = LGET('대숲열림', V('내번호'))
    cell.on(on_msg('대숲갱신'), if_(eq(V('복제'), 1),
                                 ifelse(eq(st, 0), [shape('hid')],
                                        [ifelse(eq(st, 2), [shape('flag')],
                                                [ifelse(eq(st, 3), [shape('boom')], [shape(add(5, LGET('대숲수', V('내번호'))))])])])))
    cell.on(on_msg('대숲공개'), if_(and_(eq(V('복제'), 1), and_(eq(LGET('함정', V('내번호')), 1), ne(st, 3))), shape('trap')))
    cell.on(on_click(), if_(and_(eq(V('복제'), 1), and_(eq(V('게임중'), 1), eq(V('대기'), 1))),
                            setv('대숲클릭', V('내번호')), cast('대숲누름')))
    # 이웃 처리 (펼쳐서): 칸 i 의 열/행을 _qc/_qr 에 두고, 8방향마다 블록 실행
    def neighbors(body):
        out = []
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                if dc == 0 and dr == 0:
                    continue
                cond = and_(and_(ge(add(V('_qc'), dc), 0), lt(add(V('_qc'), dc), C)),
                            and_(ge(add(V('_qr'), dr), 0), lt(add(V('_qr'), dr), R)))
                idx = add(add(mul(add(V('_qr'), dr), C), add(V('_qc'), dc)), 1)
                out.append(if_(cond, *body(idx)))
        return out
    def at(i):
        return [setv('_qc', mod(sub(i, 1), C)), setv('_qr', floor(div(sub(i, 1), C)))]
    # 첫 클릭 칸 주변은 안전하게 함정 배치
    gen = [setv('_mk', 0),
           until(ge(V('_mk'), NT),
                 setv('_qi', rnd(1, N)),
                 setv('_ma', mod(sub(V('_qi'), 1), C)), setv('_mb', floor(div(sub(V('_qi'), 1), C))),
                 if_(and_(eq(LGET('함정', V('_qi')), 0),
                          or_(gt(abs_(sub(V('_ma'), mod(sub(V('대숲클릭'), 1), C))), 1),
                              gt(abs_(sub(V('_mb'), floor(div(sub(V('대숲클릭'), 1), C)))), 1))),
                     lst_set('함정', V('_qi'), 1), chg('_mk', 1),
                     *at(V('_qi')), *neighbors(lambda j: [lst_set('대숲수', j, add(LGET('대숲수', j), 1))]))),
           setv('대숲생성', 1)]
    flood = [lst_add('대숲큐', V('대숲클릭')),
             until(eq(LLEN('대숲큐'), 0),
                   setv('_qi', LGET('대숲큐', 1)), lst_del('대숲큐', 1),
                   if_(eq(LGET('대숲열림', V('_qi')), 0),
                       lst_set('대숲열림', V('_qi'), 1), chg('연칸', 1), cast('대숲갱신'),
                       if_(eq(LGET('대숲수', V('_qi')), 0),
                           *at(V('_qi')),
                           *neighbors(lambda j: [if_(and_(eq(LGET('대숲열림', j), 0), eq(LGET('함정', j), 0)), lst_add('대숲큐', j))]))))]
    end_win = add(70, mul(V('남은시간'), 0.4))
    mgr = hidden(m, '대숲담당')
    ci = V('대숲클릭')
    mgr.on(on_msg('대숲누름'), setv('대기', 0),
           ifelse(eq(V('대숲모드'), 1),
                  [ifelse(eq(LGET('대숲열림', ci), 0), [lst_set('대숲열림', ci, 2)],
                          [if_(eq(LGET('대숲열림', ci), 2), lst_set('대숲열림', ci, 0))]),
                   cast('대숲갱신')],
                  [if_(eq(V('대숲생성'), 0), *gen),
                   if_(eq(LGET('대숲열림', ci), 0),
                       ifelse(eq(LGET('함정', ci), 1),
                              [lst_set('대숲열림', ci, 3), chg('대숲목숨', -1), cast('대숲갱신'), cast('대숲쾅'),
                               if_(le(V('대숲목숨'), 0), cast('대숲공개'), wait(1.2), *m.end_blocks(mul(V('연칸'), 1.4)))],
                              [*flood, cast('대숲딱')]))]),
           setv('미니표시', join(V('연칸'), '/', N - NT, '칸 · ♥', V('대숲목숨'))),
           if_(ge(V('연칸'), N - NT), cast('대숲공개'), cast('대숲성공'), wait(1.2), *m.end_blocks(end_win)),
           setv('대기', 1))
    mgr.on(on_msg('시간끝'), cast('대숲공개'), wait(1.0), *m.end_blocks(mul(V('연칸'), 1.4)))
    mode_b = m.S('깃발모드', [('off', K.button('깃발 모드: 끔', 104, 26, 'navy', icon='shield')),
                              ('on', K.button('깃발 모드: 켬', 104, 26, 'red', icon='shield'))], 182, -20)
    mode_b.on(on_scene(), shape('off'))
    mode_b.on(on_click(), if_(eq(V('게임중'), 1), setv('대숲모드', sub(1, V('대숲모드'))),
                              ifelse(eq(V('대숲모드'), 1), [shape('on')], [shape('off')]), cast('딸깍')))
    hidden(m, '깃발키').on(on_key(K_F), if_(eq(V('게임중'), 1), setv('대숲모드', sub(1, V('대숲모드'))), cast('깃발바꿈')))
    mode_b.on(on_msg('깃발바꿈'), ifelse(eq(V('대숲모드'), 1), [shape('on')], [shape('off')]))
    m.T('대숲설명', '숫자 = 주변 8칸의 함정 수\n깃발로 함정을 표시해요', 182, 30, 8, C_DIM, F_BODY, True, 0, w=110, h=28)
    win = m.S('대숲성공글', K.big_text('대숲 통과!', 32, 'royal'), -20, 0, visible=False)
    win.on(on_msg('대숲성공'), show())
    m.on_start(setv('연칸', 0), setv('대숲목숨', 2), setv('대숲생성', 0), setv('대숲모드', 0), setv('대기', 1),
               *[lst_set(nm, i, 0) for nm in ('함정', '대숲열림', '대숲수') for i in range(1, N + 1)])
    m.snd('대숲딱', play('tick'))
    m.snd('대숲쾅', play('fail_big'))
    m.snd('대숲성공', play('fanfare'))
    m.snd('딸깍', play('click'))
    m.finish('죽림리 대숲에 함정 10개가 숨어 있어요! 칸을 열어 숫자\n힌트로 함정을 피하고, 안전한 칸 44개를 모두 여세요.',
             '조작: 칸 클릭 = 열기  ·  깃발 모드(버튼 또는 F 키)에서 클릭 = 깃발  ·  함정 2번이면 끝')
    return True


# ================================================================== 29. 번암리 논 물길 잇기 (연결 퍼즐)
PIPE_C, PIPE_R = 6, 4
DIR = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}     # 0 위 1 오른쪽 2 아래 3 왼쪽 (열, 행)


def _pipe_levels():
    """단계마다 (시작 줄, 끝 줄, 칸별 종류[24]). 정답 길은 무작위로 만들되 씨앗을 고정."""
    out = []
    for seed, (sr, tr, lo, hi) in enumerate(((1, 2, 8, 11), (0, 3, 11, 15), (3, 0, 13, 18))):
        rng = random.Random(100 + seed)
        while True:
            path = [(0, sr)]
            ok = False
            for _ in range(60):
                c, r = path[-1]
                if c == PIPE_C - 1 and r == tr:
                    ok = True
                    break
                opts = []
                for d, (dc, dr) in DIR.items():
                    nc, nr = c + dc, r + dr
                    if 0 <= nc < PIPE_C and 0 <= nr < PIPE_R and (nc, nr) not in path:
                        opts.append((nc, nr))
                if not opts:
                    break
                path.append(rng.choice(opts))
            if ok and lo <= len(path) <= hi:
                break
        kinds = [rng.randint(1, 2) for _ in range(PIPE_C * PIPE_R)]
        prev_dir = 1        # 왼쪽에서 오른쪽으로 들어옴
        for i, (c, r) in enumerate(path):
            if i + 1 < len(path):
                nc, nr = path[i + 1]
                out_dir = [d for d, (dc, dr) in DIR.items() if (c + dc, r + dr) == (nc, nr)][0]
            else:
                out_dir = 1
            in_side = (prev_dir + 2) % 4
            kinds[r * PIPE_C + c] = 1 if (in_side + 2) % 4 == out_dir else 2
            prev_dir = out_dir
        out.append((sr, tr, kinds, path))
    return out


def g29(P, ctx):
    TL = 75
    levels = _pipe_levels()
    N = PIPE_C * PIPE_R
    X0, Y0, CL = -100, 44, 40
    P.list('물길종류', [k for lv in levels for k in lv[2]])
    P.list('물길시작', [lv[0] for lv in levels])
    P.list('물길끝', [lv[1] for lv in levels])
    # 열림표/출구표: 인덱스 = ((종류-1)*4 + 회전)*4 + 들어오는 면 + 1
    open_t, exit_t = [], []
    for kind in (1, 2):
        for r in range(4):
            sides = ({0, 2} if r % 2 == 0 else {1, 3}) if kind == 1 else {r, (r + 1) % 4}
            for side in range(4):
                open_t.append(1 if side in sides else 0)
                exit_t.append((sides - {side}).pop() if side in sides else -1)
    P.list('열림표', open_t)
    P.list('출구표', exit_t)
    P.list('관종류', [1] * N)
    P.list('관회전', [0] * N)
    P.list('관물', [0] * N)
    _vars(P, '물단계', '물시작줄', '물끝줄', '_wc', '_wr', '_we', '_wk', '물성공')
    m = MG(P, 29, ctx, time_limit=TL, status='1/3 단계', dim=80)
    panel(P, m.sc, '물길판', X0 + (PIPE_C - 1) * CL / 2, Y0 - (PIPE_R - 1) * CL / 2, PIPE_C * CL + 16, PIPE_R * CL + 16, 'glass')
    src = m.S('물시작', A2.water_source(), X0 - CL, 0)
    dst = m.S('논', A2.paddy(), X0 + PIPE_C * CL, 0)
    src.on(on_msg('물단계시작'), ly(sub(Y0, mul(V('물시작줄'), CL))))
    dst.on(on_msg('물단계시작'), ly(sub(Y0, mul(V('물끝줄'), CL))))
    pics = [('p%d_%d_%d' % (k, r, w), A2.pipe_tile(k, r, bool(w))) for k in (1, 2) for r in range(4) for w in (0, 1)]
    for i in range(1, N + 1):
        c, r = (i - 1) % PIPE_C, (i - 1) // PIPE_C
        t = m.S('관%d' % i, pics, X0 + c * CL, Y0 - r * CL)
        t.on(on_msg('물길갱신'), shape(add(add(mul(sub(LGET('관종류', i), 1), 8), mul(LGET('관회전', i), 2)), add(LGET('관물', i), 1))))
        t.on(on_click(), if_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)),
                             lst_set('관회전', i, mod(add(LGET('관회전', i), 1), 4)), cast('물길갱신'), cast('관돌림'), cast('물흐름')))
        t.on(on_msg('관돌림'), if_(eq(V('_wk'), i), t.pct(88), wait(0.05), t.pct(100)))
    trace = [*[lst_set('관물', i, 0) for i in range(1, N + 1)],
             setv('_wc', 0), setv('_wr', V('물시작줄')), setv('_we', 3), setv('물성공', 0), setv('_mk', 0),
             until(or_(eq(V('_mk'), 1), eq(V('물성공'), 1)),
                   setv('_wk', add(add(mul(V('_wr'), PIPE_C), V('_wc')), 1)),
                   setv('_mi', add(mul(add(mul(sub(LGET('관종류', V('_wk')), 1), 4), LGET('관회전', V('_wk'))), 4), add(V('_we'), 1))),
                   ifelse(eq(LGET('열림표', V('_mi')), 0), [setv('_mk', 1)],
                          [lst_set('관물', V('_wk'), 1), cast('물길갱신'),
                           setv('_ma', LGET('출구표', V('_mi'))),
                           if_(eq(V('_ma'), 0), chg('_wr', -1)), if_(eq(V('_ma'), 1), chg('_wc', 1)),
                           if_(eq(V('_ma'), 2), chg('_wr', 1)), if_(eq(V('_ma'), 3), chg('_wc', -1)),
                           setv('_we', mod(add(V('_ma'), 2), 4)),
                           if_(or_(or_(lt(V('_wc'), 0), ge(V('_wc'), PIPE_C)), or_(lt(V('_wr'), 0), ge(V('_wr'), PIPE_R))),
                               setv('_mk', 1),
                               if_(and_(eq(V('_wc'), PIPE_C), and_(eq(V('_wr'), V('물끝줄')), eq(V('_ma'), 1))), setv('물성공', 1))),
                           wait(0.02)]))]
    start_level = [setv('물시작줄', LGET('물길시작', V('물단계'))), setv('물끝줄', LGET('물길끝', V('물단계'))),
                   *[lst_set('관종류', i, LGET('물길종류', add(mul(sub(V('물단계'), 1), N), i))) for i in range(1, N + 1)],
                   *[lst_set('관회전', i, rnd(0, 3)) for i in range(1, N + 1)],
                   cast('물단계시작'), *trace, cast('물길갱신'),
                   setv('미니표시', join(V('물단계'), '/3 단계'))]
    good = m.S('물길성공글', K.big_text('물이 들어간다!', 26, 'royal'), 0, 80, visible=False)
    good.on(on_msg('물길성공'), show(), wait(0.9), hide())
    mgr = hidden(m, '물길담당')
    mgr.on(on_msg('물흐름'), setv('대기', 0), *trace,
           ifelse(eq(V('물성공'), 1),
                  [cast('물길성공'), chg('합계', 1), wait(1.0),
                   ifelse(ge(V('물단계'), 3), [*m.end_blocks(add(70, mul(V('남은시간'), 0.6)))],
                          [chg('물단계', 1), *start_level, setv('대기', 1)])],
                  [setv('대기', 1)]))
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 30)))
    m.on_start(setv('물단계', 1), setv('합계', 0), setv('대기', 1), *start_level)
    m.snd('관돌림', play('tick'))
    m.snd('물길성공', play('splash'))
    m.finish('번암리 들녘 논에 물을 대야 해요! 수로 조각을 눌러 돌려서\n왼쪽 "물"에서 오른쪽 "논"까지 물길을 이으세요. (3단계)',
             '조작: 조각 클릭 = 90도 회전  ·  파랗게 물이 찬 곳까지가 연결된 길이에요')
    return True


# ================================================================== 31. 연서면 참새 쫓기 (슈팅)
def g31(P, ctx):
    TL, COLS, ROWS = 40, 6, 3
    NB = COLS * ROWS
    _vars(P, '새대x', '새대y', '새방향', '새총x', '남은새', '새목숨', '쏘는중', '새속도')
    m = MG(P, 31, ctx, time_limit=TL, status='0마리 · ♥3', dim=30)
    m.S('곡식선', A.plain_rect(480, 3, (150, 200, 120, 160), 'crop_line'), 0, -72)
    bird = m.S('참새', [('a', A2.sparrow(0)), ('b', A2.sparrow(1))], 0, 300, visible=False)
    for v in ('복제', '내번호', '살아있음'):
        bird.local(v, 0)
    bird.on(on_msg('새떼'), if_(eq(V('복제'), 0), setv('내번호', 0), rep(NB, chg('내번호', 1), clone_self())))
    bx = add(V('새대x'), mul(mod(sub(V('내번호'), 1), COLS), 36))
    by = sub(V('새대y'), mul(floor(div(sub(V('내번호'), 1), COLS)), 26))
    bird.on(on_clone(), setv('복제', 1), setv('살아있음', 1), xy(bx, by), show(),
            until(or_(eq(V('살아있음'), 0), eq(V('게임중'), 0)),
                  xy(bx, by), ifelse(eq(mod(floor(div(timer(), 0.15)), 2), 0), [shape('a')], [shape('b')]),
                  if_(touch('콩알_' + m.sc), setv('살아있음', 0), chg('합계', 1), chg('남은새', -1), cast('짹'),
                      setv('미니표시', join(V('합계'), '마리 · ♥', V('새목숨'))))),
            if_(eq(V('살아있음'), 0), rot(180), rep(12, mvy(-6), fx_add('transparency', 8), wait(0.016))),
            del_clone())
    bird.on(on_msg('새치우기'), if_(eq(V('복제'), 1), del_clone()))
    pe = m.S('콩알', A2.pea(), 0, -300, visible=False)
    pe.local('복제', 0)
    pe.on(on_msg('발사'), if_(eq(V('복제'), 0), clone_self()))
    pe.on(on_clone(), setv('복제', 1), xy(V('새총x'), -88), show(),
          until(or_(touch('참새_' + m.sc), gt(obj_y(), 140)), mvy(8)), wait(0.03), del_clone())
    sling = m.S('새총', A2.slingshot(), 0, -104)
    sling.on(on_msg('게임시작'), setv('새총x', 0),
             until(eq(V('게임중'), 0),
                   if_(key(K_LEFT), chg('새총x', -4.5)), if_(key(K_RIGHT), chg('새총x', 4.5)),
                   *clamp_blocks('새총x', -220, 220), lx(V('새총x'))))
    hidden(m, '새총키').on(on_key(K_SPACE), if_(and_(eq(V('게임중'), 1), eq(V('쏘는중'), 0)),
                                             setv('쏘는중', 1), cast('발사'), cast('퉁'), wait(0.28), setv('쏘는중', 0)))
    steal = m.S('훔침글', K.big_text('곡식을 먹혔다!', 22, 'red'), 0, 0, visible=False)
    steal.on(on_msg('훔침'), show(), wait(0.7), hide())
    wave = [cast('새치우기'), setv('새대x', -90), setv('새대y', 96), setv('새방향', 1), setv('남은새', NB), wait(0.05), cast('새떼')]
    mgr = hidden(m, '새떼담당')
    mgr.on(on_msg('게임시작'), setv('새속도', 0.9), *wave,
           until(eq(V('게임중'), 0),
                 chg('새대x', mul(V('새방향'), V('새속도'))),
                 if_(gt(V('새대x'), 30), setv('새방향', -1), chg('새대y', -9)),
                 if_(lt(V('새대x'), -210), setv('새방향', 1), chg('새대y', -9)),
                 if_(le(V('남은새'), 0), chg('새속도', 0.35), wait(0.5), *wave),
                 if_(lt(sub(V('새대y'), 2 * 26), -60),
                     chg('새목숨', -1), cast('훔침'), setv('미니표시', join(V('합계'), '마리 · ♥', V('새목숨'))),
                     if_(le(V('새목숨'), 0), *m.end_blocks(mul(V('합계'), 100.0 / NB))),
                     wait(0.6), *wave),
                 wait(0.016)))
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 100.0 / NB)))
    m.on_start(setv('합계', 0), setv('새목숨', 3), setv('쏘는중', 0))
    m.snd('퉁', play('jump'))
    m.snd('짹', play('pop'))
    m.snd('훔침', play('bad'))
    m.finish('연서면 들판에 참새 떼가 내려와요! 새총으로 콩알을 쏴서\n곡식을 지키세요. 참새가 아래 선까지 오면 ♥ 하나 잃어요.',
             '조작: ← → 이동, SPACE 발사  ·  18마리면 만점')
    return True


# ================================================================== 33. 조천 징검돌 놓기 (밀기 퍼즐)
def g33(P, ctx):
    import soko_levels as SL
    TL = 100
    lv = [SL.parse(L) for L in SL.LEVELS]
    C, R = lv[0][3], lv[0][2]
    N = C * R
    X0, Y0, CL = -117, 51, 26
    P.list('징검판', [0] * N)
    P.list('징검원본', [v for g, st, _, _ in lv for v in g])
    P.list('징검시작', [st[0] * C + st[1] + 1 for g, st, _, _ in lv])
    _vars(P, '징검단계', '징검나', '_sd', '_st', '_sb', '_sv')
    m = MG(P, 33, ctx, time_limit=TL, status='1/3 단계', dim=90)
    panel(P, m.sc, '징검판넬', X0 + (C - 1) * CL / 2, Y0 - (R - 1) * CL / 2, C * CL + 14, R * CL + 14, 'glass')
    kinds = ['land', 'water', 'stone', 'rock', 'goal', 'step', 'stone']
    pics = [('k%d' % i, A2.stone_cell(k)) for i, k in enumerate(kinds)]
    for i in range(1, N + 1):
        c, r = (i - 1) % C, (i - 1) // C
        t = m.S('징검칸%d' % i, pics, X0 + c * CL, Y0 - r * CL)
        t.on(on_msg('징검갱신'), shape(add(LGET('징검판', i), 1)))
    me = m.S('징검나', ctx['PORT']['me'], 0, 0, scale=0.5)
    me.on(on_msg('징검갱신'), xy(add(X0, mul(mod(sub(V('징검나'), 1), C), CL)), sub(Y0, mul(floor(div(sub(V('징검나'), 1), C)), CL))))
    load = [*[lst_set('징검판', i, LGET('징검원본', add(mul(sub(V('징검단계'), 1), N), i))) for i in range(1, N + 1)],
            setv('징검나', LGET('징검시작', V('징검단계'))), cast('징검갱신'), setv('미니표시', join(V('징검단계'), '/3 단계'))]
    def move(dc, dr):
        okc = (lambda v: lt(add(mod(sub(v, 1), C), dc), C)) if dc > 0 else (lambda v: ge(add(mod(sub(v, 1), C), dc), 0))
        okr = (lambda v: lt(add(floor(div(sub(v, 1), C)), dr), R)) if dr > 0 else (lambda v: ge(add(floor(div(sub(v, 1), C)), dr), 0))
        inb = (lambda v: okc(v)) if dc else (lambda v: okr(v))
        d = dc + dr * C
        return [if_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)),
                    if_(inb(V('징검나')),
                        setv('_st', add(V('징검나'), d)), setv('_sv', LGET('징검판', V('_st'))),
                        ifelse(or_(or_(eq(V('_sv'), 0), eq(V('_sv'), 4)), eq(V('_sv'), 5)),
                               [setv('징검나', V('_st')), cast('징검갱신'), cast('징검걸음')],
                               [if_(and_(or_(eq(V('_sv'), 2), eq(V('_sv'), 6)), inb(V('_st'))),
                                    setv('_sb', add(V('_st'), d)), setv('_sd', LGET('징검판', V('_sb'))),
                                    if_(or_(or_(eq(V('_sd'), 0), eq(V('_sd'), 1)), eq(V('_sd'), 5)),
                                        ifelse(eq(V('_sv'), 6), [lst_set('징검판', V('_st'), 5)], [lst_set('징검판', V('_st'), 0)]),
                                        ifelse(eq(V('_sd'), 0), [lst_set('징검판', V('_sb'), 2)],
                                               [ifelse(eq(V('_sd'), 1), [lst_set('징검판', V('_sb'), 5), cast('풍덩')],
                                                       [lst_set('징검판', V('_sb'), 6)])]),
                                        setv('징검나', V('_st')), cast('징검갱신'), cast('징검밀기')))]),
                        if_(eq(LGET('징검판', V('징검나')), 4), cast('징검도착'))))]
    keys = hidden(m, '징검키')
    for kc, dc, dr in ((K_LEFT, -1, 0), (K_RIGHT, 1, 0), (K_UP, 0, -1), (K_DOWN, 0, 1)):
        keys.on(on_key(kc), *move(dc, dr))
    redo = [if_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)), *load, cast('다시'))]
    keys.on(on_key(82), *redo)
    button(P, m.sc, '다시버튼', '다시 (R)', 182, -112, 84, 24, 'gray', icon='back', actions=redo)
    good = m.S('징검성공', K.big_text('건넜다!', 32, 'royal'), 0, 0, visible=False)
    good.on(on_msg('징검도착'), show(), wait(0.9), hide())
    mgr = hidden(m, '징검담당')
    mgr.on(on_msg('징검도착'), setv('대기', 0), chg('합계', 1), wait(1.0),
           ifelse(ge(V('징검단계'), 3), [*m.end_blocks(add(70, mul(V('남은시간'), 0.5)))],
                  [chg('징검단계', 1), *load, setv('대기', 1)]))
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 30)))
    m.on_start(setv('징검단계', 1), setv('합계', 0), setv('대기', 1), *load)
    m.snd('징검걸음', play('tick'))
    m.snd('징검밀기', play('hit'))
    m.snd('풍덩', play('splash'))
    m.snd('징검도착', play('fanfare'))
    m.finish('조천을 건너 깃발까지! 회색 돌을 밀어 물에 빠뜨리면\n징검다리가 돼요. 바위는 못 밀어요. (3단계, 막히면 R)',
             '조작: 방향키로 한 칸씩  ·  돌 쪽으로 걸어가면 밀려요  ·  R 또는 다시 버튼 = 처음부터')
    return True


# ================================================================== 34. 조천 둑방길 자전거 따라가기 (따라가기)
def g34(P, ctx):
    TL = 30
    _vars(P, '자전거t', '자x', '자y', '켜짐수', '샘플수')
    m = MG(P, 34, ctx, time_limit=TL, status='0%', dim=40)
    ring = m.S('따라고리', [('off', A2.target_ring(0)), ('on', A2.target_ring(1))], 0, 0)
    bike = m.S('자전거', A2.bicycle(), 0, 0)
    dist = fn('root', add(mul(sub(mouse_x(), V('자x')), sub(mouse_x(), V('자x'))), mul(sub(mouse_y(), V('자y')), sub(mouse_y(), V('자y')))))
    bike.on(on_msg('게임시작'), setv('자전거t', 0), setv('_ma', rnd(0, 360)), setv('_mb', rnd(0, 360)),
            until(eq(V('게임중'), 0),
                  chg('자전거t', add(1.1, mul(sub(TL, V('남은시간')), 0.07))),
                  setv('자x', add(mul(sin_(add(mul(V('자전거t'), 0.9), V('_ma'))), 170), mul(sin_(mul(V('자전거t'), 2.3)), 35))),
                  setv('자y', sub(add(mul(sin_(add(mul(V('자전거t'), 1.3), V('_mb'))), 66), mul(sin_(mul(V('자전거t'), 3.1)), 16)), 12)),
                  xy(V('자x'), V('자y')),
                  chg('샘플수', 1),
                  ifelse(lt(dist, 26), [chg('켜짐수', 1), cast('고리켬')], [cast('고리끔')]),
                  setv('미니표시', join(rounded(mul(div(V('켜짐수'), V('샘플수')), 100)), '%'))))
    ring.on(on_msg('게임시작'), until(eq(V('게임중'), 0), xy(V('자x'), V('자y'))))
    ring.on(on_msg('고리켬'), shape('on'))
    ring.on(on_msg('고리끔'), shape('off'))
    mgr = hidden(m, '자전거담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(div(V('켜짐수'), add(V('샘플수'), 1)), 110)))
    m.on_start(setv('켜짐수', 0), setv('샘플수', 0), setv('자x', 0), setv('자y', 0))
    m.finish('조천 둑방길 자전거 홍보단을 따라가요! 마우스 포인터를\n자전거 위 동그라미 안에 계속 두세요. 점점 빨라져요!',
             '조작: 마우스 움직이기  ·  30초  ·  동그라미가 파란색이면 따라가는 중')
    return True


# ================================================================== 35. 시외버스터미널 유세 버스 주차 (주차)
def g35(P, ctx):
    TL = 60
    BAYX = [-160, -80, 0, 80, 160]
    BAYY = 58
    levels = [  # (목표 칸, [(x, y, 종류 1차/2고깔)])
        (2, [(BAYX[0], BAYY, 1), (BAYX[4], BAYY, 1), (-60, -20, 2), (60, -20, 2), (300, 300, 2)]),
        (0, [(BAYX[1], BAYY, 1), (BAYX[3], BAYY, 1), (-110, -30, 2), (-60, 0, 2), (20, -50, 2)]),
        (3, [(BAYX[2], BAYY, 1), (BAYX[4], BAYY, 1), (40, -30, 2), (120, -30, 2), (-40, -10, 2)]),
    ]
    P.list('주차목표', [BAYX[lv[0]] for lv in levels])
    P.list('장애x', [o[0] for lv in levels for o in lv[1]])
    P.list('장애y', [o[1] for lv in levels for o in lv[1]])
    P.list('장애종', [o[2] for lv in levels for o in lv[1]])
    _vars(P, '버스x', '버스y', '버스각', '버스속', '주차단계', '충돌', '쿵쿨', '주차tx')
    m = MG(P, 35, ctx, time_limit=TL, status='1/3 주차', dim=0)
    m.S('주차장', A2.parking_lot(), 0, -10)
    for i, x in enumerate(BAYX):
        b = m.S('주차칸%d' % i, [('idle', A2.bay('idle')), ('target', A2.bay('target'))], x, BAYY)
        b.on(on_msg('주차단계시작'), ifelse(eq(LGET('주차목표', V('주차단계')), x), [shape('target')], [shape('idle')]))
    ob = m.S('장애물', [('car', A2.parked_car((200, 60, 80))), ('cone', A2.cone())], 0, 300, visible=False)
    ob.local('복제', 0)
    ob.local('내번호', 0)
    ob.on(on_msg('주차단계시작'), if_(eq(V('복제'), 1), del_clone()),
          if_(eq(V('복제'), 0), setv('내번호', 0), rep(5, chg('내번호', 1), clone_self())))
    oi = add(mul(sub(V('주차단계'), 1), 5), V('내번호'))
    ob.on(on_clone(), setv('복제', 1), shape(LGET('장애종', oi)), xy(LGET('장애x', oi), LGET('장애y', oi)), show())
    bus = m.S('유세버스', A2.bus_top(), 0, -95)
    reset = [setv('버스x', 0), setv('버스y', -95), setv('버스각', 0), setv('버스속', 0), xy(0, -95), rot(0)]
    bus.on(on_msg('주차단계시작'), *reset)
    bus.on(on_msg('게임시작'),
           until(eq(V('게임중'), 0),
                 ifelse(key(K_UP), [chg('버스속', 0.09)], [ifelse(key(K_DOWN), [chg('버스속', -0.09)], [setv('버스속', mul(V('버스속'), 0.94))])]),
                 *clamp_blocks('버스속', -1.4, 2.2),
                 if_(key(K_LEFT), chg('버스각', mul(V('버스속'), -1.7))), if_(key(K_RIGHT), chg('버스각', mul(V('버스속'), 1.7))),
                 chg('버스x', mul(V('버스속'), sin_(V('버스각')))), chg('버스y', mul(V('버스속'), cos_(V('버스각')))),
                 *clamp_blocks('버스x', -222, 222), *clamp_blocks('버스y', -112, 96),
                 xy(V('버스x'), V('버스y')), rot(V('버스각')),
                 if_(gt(V('쿵쿨'), 0), chg('쿵쿨', -1)),
                 if_(and_(touch(ob.name), eq(V('쿵쿨'), 0)),
                     chg('버스x', mul(mul(V('버스속'), sin_(V('버스각'))), -3)), chg('버스y', mul(mul(V('버스속'), cos_(V('버스각'))), -3)),
                     setv('버스속', 0), chg('충돌', 1), setv('쿵쿨', 20), cast('쿵')),
                 if_(and_(and_(lt(abs_(sub(V('버스x'), V('주차tx'))), 8), lt(abs_(sub(V('버스y'), BAYY)), 10)),
                          and_(gt(cos_(V('버스각')), 0.97), lt(abs_(V('버스속')), 0.45))),
                     cast('주차성공'), chg('합계', 1), wait(1.0),
                     ifelse(ge(V('주차단계'), 3), [*m.end_blocks(sub(add(70, mul(V('남은시간'), 0.5)), mul(V('충돌'), 3)))],
                            [chg('주차단계', 1), setv('주차tx', LGET('주차목표', V('주차단계'))), cast('주차단계시작'),
                             setv('미니표시', join(V('주차단계'), '/3 주차 · 쿵 ', V('충돌')))]))))
    ok = m.S('주차글', K.big_text('주차 완료!', 30, 'royal'), 0, 0, visible=False)
    ok.on(on_msg('주차성공'), show(), wait(0.9), hide())
    mgr = hidden(m, '주차담당')
    mgr.on(on_msg('쿵'), setv('미니표시', join(V('주차단계'), '/3 주차 · 쿵 ', V('충돌'))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(V('합계'), 28), mul(V('충돌'), 3))))
    m.on_start(setv('주차단계', 1), setv('합계', 0), setv('충돌', 0), setv('쿵쿨', 0), setv('주차tx', LGET('주차목표', 1)),
               cast('주차단계시작'))
    m.snd('쿵', play('hit'))
    m.snd('주차성공', play('good'))
    m.finish('터미널 유세 버스를 파란 P 칸에 반듯하게 세우세요!\n다른 차나 고깔에 부딪히면 감점. 3번 주차하면 끝!',
             '조작: ↑ 앞으로 · ↓ 뒤로 · ← → 방향 (움직일 때만 돌아가요)  ·  칸 안에서 멈추면 성공')
    return True


# ================================================================== 38. 새내 골목 틀린 벽보 찾기 (틀린 그림)
def g38(P, ctx):
    TL = 70
    LX, RX, PY = -108, 108, -12
    diffs = A2.DIFF_PUZZLES
    P.list('틀린x', [d[1] for pz in diffs for d in pz])
    P.list('틀린y', [d[2] for pz in diffs for d in pz])
    P.list('틀린r', [d[3] for pz in diffs for d in pz])
    P.list('틀린찾음', [0] * 5)
    _vars(P, '틀린단계', '_lx', '_ly', '_hit')
    m = MG(P, 38, ctx, time_limit=TL, status='0/10 찾음', dim=110)
    left = m.S('원래벽보', [('p0', A2.poster(0, False)), ('p1', A2.poster(1, False))], LX, PY)
    right = m.S('바뀐벽보', [('p0', A2.poster(0, True)), ('p1', A2.poster(1, True))], RX, PY)
    m.T('왼쪽글', '원래 벽보', LX, 84, 9, C_DIM, F_NUM, False, 0, w=100, h=14)
    m.T('오른쪽글', '누가 바꿔 놓은 벽보', RX, 84, 9, C_RED, F_NUM, False, 0, w=140, h=14)
    for o in (left, right):
        o.on(on_msg('틀린단계시작'), shape(V('틀린단계')))
    di = lambda k: add(mul(sub(V('틀린단계'), 1), 5), k)
    for k in range(1, 6):
        for side, px in (('L', LX), ('R', RX)):
            c = m.S('찾은원%s%d' % (side, k), A2.found_circle(), 0, 0, visible=False)
            c.on(on_msg('틀린갱신'), ifelse(eq(LGET('틀린찾음', k), 1),
                                         [xy(add(px, LGET('틀린x', di(k))), add(PY, LGET('틀린y', di(k)))), show()], [hide()]))
    def click(px):
        body = [setv('_lx', sub(mouse_x(), px)), setv('_ly', sub(mouse_y(), PY)), setv('_hit', 0)]
        for k in range(1, 6):
            rr = add(LGET('틀린r', di(k)), 7)
            body.append(if_(and_(and_(eq(LGET('틀린찾음', k), 0), eq(V('_hit'), 0)),
                                 and_(le(abs_(sub(V('_lx'), LGET('틀린x', di(k)))), rr), le(abs_(sub(V('_ly'), LGET('틀린y', di(k)))), rr))),
                            lst_set('틀린찾음', k, 1), setv('_hit', 1), chg('합계', 1)))
        body += [ifelse(eq(V('_hit'), 1), [cast('틀린갱신'), cast('찾았다')], [chg('틀림', 1), cast('땡')]),
                 setv('미니표시', join(V('합계'), '/10 찾음 · 헛클릭 ', V('틀림'))),
                 if_(eq(V('합계'), mul(V('틀린단계'), 5)), cast('틀린다음'))]
        return [if_(and_(eq(V('게임중'), 1), eq(V('대기'), 1)), *body)]
    left.on(on_click(), *click(LX))
    right.on(on_click(), *click(RX))
    x_ = m.S('헛클릭', K.big_text('땡!', 22, 'red'), 0, 0, visible=False)
    x_.on(on_msg('땡'), xy(mouse_x(), mouse_y()), show(), wait(0.3), hide())
    mgr = hidden(m, '틀린담당')
    mgr.on(on_msg('틀린다음'), setv('대기', 0), wait(1.0),
           ifelse(ge(V('틀린단계'), 2), [*m.end_blocks(sub(add(80, mul(V('남은시간'), 0.5)), mul(V('틀림'), 2)))],
                  [chg('틀린단계', 1), *[lst_set('틀린찾음', k, 0) for k in range(1, 6)], cast('틀린갱신'), cast('틀린단계시작'),
                   setv('대기', 1)]))
    mgr.on(on_msg('시간끝'), *m.end_blocks(sub(mul(V('합계'), 9), mul(V('틀림'), 2))))
    m.on_start(setv('틀린단계', 1), setv('합계', 0), setv('틀림', 0), setv('대기', 1),
               *[lst_set('틀린찾음', k, 0) for k in range(1, 6)], cast('틀린갱신'), cast('틀린단계시작'))
    m.snd('찾았다', play('good'))
    m.snd('땡', play('bad'))
    m.finish('누군가 새내 골목 내 벽보를 몰래 바꿔 놨어요! 두 벽보에서\n다른 곳 5군데씩, 모두 10군데를 찾아 클릭하세요.',
             '조작: 다른 곳 클릭 (어느 쪽 벽보든 OK)  ·  헛클릭은 감점')
    return True


# ================================================================== 39. 으뜸길 상가 전단 벽돌깨기 (벽돌깨기)
def g39(P, ctx):
    TL, COLS, ROWS = 60, 7, 4
    NB = COLS * ROWS
    _vars(P, '공x', '공y', '공vx', '공vy', '발사됨', '패들x', '_pmx2', '반사쿨', '공목숨')
    m = MG(P, 39, ctx, time_limit=TL, status='0/%d · ♥3' % NB, dim=90)
    cols = [(80, 130, 255), (150, 100, 255), (230, 80, 120), (60, 170, 255)]
    br = m.S('전단벽돌', [('b%d' % i, A2.brick(c)) for i, c in enumerate(cols)], 0, 300, visible=False)
    br.local('복제', 0)
    br.local('내번호', 0)
    br.on(on_msg('게임시작'), setv('내번호', 0), rep(NB, chg('내번호', 1), clone_self()))
    br.on(on_clone(), setv('복제', 1), shape(add(floor(div(sub(V('내번호'), 1), COLS)), 1)),
          xy(add(-168, mul(mod(sub(V('내번호'), 1), COLS), 56)), sub(84, mul(floor(div(sub(V('내번호'), 1), COLS)), 22))), show(),
          wait_until(or_(touch('전단공_' + m.sc), eq(V('게임중'), 0))),
          if_(eq(V('게임중'), 1), chg('합계', 1), cast('벽돌맞음'), setv('미니표시', join(V('합계'), '/', NB, ' · ♥', V('공목숨'))),
              rep(5, br.grow_pct(-15), fx_add('transparency', 18), wait(0.016))),
          del_clone())
    pad = m.S('받침대', A2.paddle(), 0, -110)
    pad.on(on_msg('게임시작'), setv('패들x', 0), setv('_pmx2', mouse_x()),
           until(eq(V('게임중'), 0),
                 if_(key(K_LEFT), chg('패들x', -6)), if_(key(K_RIGHT), chg('패들x', 6)),
                 if_(ne(mouse_x(), V('_pmx2')), setv('패들x', mouse_x()), setv('_pmx2', mouse_x())),
                 *clamp_blocks('패들x', -200, 200), lx(V('패들x'))))
    ball = m.S('전단공', A2.ball(12), 0, -98)
    launch = [if_(and_(eq(V('게임중'), 1), eq(V('발사됨'), 0)), setv('발사됨', 1), setv('공vx', div(rnd(-20, 20), 10)), setv('공vy', 4.2))]
    keys = hidden(m, '벽돌키')
    keys.on(on_key(K_SPACE), *launch)
    keys.on(on_mouse_down(), *launch)
    ball.on(on_msg('게임시작'), setv('발사됨', 0),
            until(eq(V('게임중'), 0),
                  ifelse(eq(V('발사됨'), 0), [setv('공x', V('패들x')), setv('공y', -98)],
                         [chg('공x', V('공vx')), chg('공y', V('공vy')),
                          if_(gt(abs_(V('공x')), 232), setv('공vx', mul(V('공vx'), -1)), *clamp_blocks('공x', -232, 232)),
                          if_(gt(V('공y'), 112), setv('공vy', mul(abs_(V('공vy')), -1))),
                          if_(and_(lt(V('공vy'), 0), touch(pad.name)),
                              setv('공vy', abs_(V('공vy'))), setv('공vx', mul(sub(V('공x'), V('패들x')), 0.13)), cast('통')),
                          if_(lt(V('공y'), -134),
                              chg('공목숨', -1), setv('발사됨', 0), cast('공잃음'),
                              setv('미니표시', join(V('합계'), '/', NB, ' · ♥', V('공목숨'))),
                              if_(le(V('공목숨'), 0), *m.end_blocks(mul(V('합계'), 100.0 / NB))))]),
                  if_(gt(V('반사쿨'), 0), chg('반사쿨', -1)),
                  xy(V('공x'), V('공y'))))
    ball.on(on_msg('벽돌맞음'), if_(eq(V('반사쿨'), 0), setv('공vy', mul(V('공vy'), -1)), setv('반사쿨', 4),
                                  if_(lt(abs_(V('공vy')), 5.5), setv('공vy', mul(V('공vy'), 1.03)))),
            if_(ge(V('합계'), NB), *m.end_blocks(add(85, mul(V('남은시간'), 0.5)))))
    mgr = hidden(m, '벽돌담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(mul(V('합계'), 100.0 / NB)))
    m.on_start(setv('합계', 0), setv('공목숨', 3), setv('반사쿨', 0), setv('발사됨', 0))
    m.snd('벽돌맞음', play('pop'))
    m.snd('통', play('tick'))
    m.snd('공잃음', play('bad'))
    m.finish('으뜸길 상가에 큰아버지 전단이 가득! 공을 튕겨서\n전단 벽돌 28개를 모두 깨세요. 공을 3번 놓치면 끝.',
             '조작: 마우스 또는 ← → 로 받침대 이동  ·  SPACE/클릭으로 공 발사')
    return True


# ================================================================== 40. 남리 철길 건널목 건너기 (길 건너기)
def g40(P, ctx):
    TL = 45
    rows = ['safe', 'road', 'road', 'safe', 'rail', 'safe', 'road', 'road', 'goal']
    lanes = {1: (1.6, 'r', (230, 70, 90)), 2: (-2.2, 'l', (80, 140, 255)), 6: (-1.9, 'l', (170, 110, 255)), 7: (2.7, 'r', (90, 200, 140))}
    RY = lambda k: -110 + k * 24
    _vars(P, '건넘', '최고행', '개구리c', '개구리r', '건목숨', '건쿨', '배속', '기차온다')
    m = MG(P, 40, ctx, time_limit=TL, status='건넌 횟수 0 · ♥3', dim=0)
    m.S('건널목바닥', A2.crossing_board(rows), 0, RY(4))
    lane_keys = sorted(lanes)
    pics = []
    for k in lane_keys:
        sp, face, col = lanes[k]
        pics.append(('car%d' % k, A2.car_side(col, face)))
    car = m.S('건널차', pics, 0, 300, visible=False)
    car.local('복제', 0)
    car.local('차선', 0)
    for i, k in enumerate(lane_keys):
        sp, face, col = lanes[k]
        car.on(on_msg('게임시작'), wait(div(rnd(0, 80), 100)),
               until(eq(V('게임중'), 0), if_(eq(V('복제'), 0), setv('차선', i + 1), clone_self()),
                     wait(div(rnd(int(190 / abs(sp)), int(420 / abs(sp))), 100))))
    spd = [lanes[k][0] for k in lane_keys]
    ys = [RY(k) for k in lane_keys]
    car.on(on_clone(), setv('복제', 1), shape(V('차선')),
           *[if_(eq(V('차선'), i + 1), xy(-262 if spd[i] > 0 else 262, ys[i])) for i in range(len(lane_keys))],
           show(),
           until(or_(gt(abs_(obj_x()), 270), eq(V('게임중'), 0)),
                 *[if_(eq(V('차선'), i + 1), mvx(mul(spd[i], V('배속')))) for i in range(len(lane_keys))]),
           del_clone())
    lights = [m.S('경보등%d' % i, [('off', A2.signal_light(0)), ('a', A2.signal_light(1)), ('b', A2.signal_light(2))], x, RY(4) + 18)
              for i, x in enumerate((-200, 200))]
    for lt_ in lights:
        lt_.on(on_msg('경보'), rep(5, shape('a'), wait(0.15), shape('b'), wait(0.15)), shape('off'))
    tr = m.S('기차', A2.train(320, 24), -460, RY(4))
    tr.on(on_msg('게임시작'),
          until(eq(V('게임중'), 0),
                wait(div(rnd(350, 650), 100)), cast('경보'), setv('기차온다', 1), wait(1.5),
                xy(-460, RY(4)), until(or_(gt(obj_x(), 460), eq(V('게임중'), 0)), mvx(13)), setv('기차온다', 0)))
    me = m.S('건너는나', ctx['PORT']['me'], 0, RY(0), scale=0.5)
    pos = [xy(add(-228, mul(V('개구리c'), 24)), add(-110, mul(V('개구리r'), 24)))]
    home = [setv('개구리c', 10), setv('개구리r', 0), *pos]
    me.on(on_msg('게임시작'), *home,
          until(eq(V('게임중'), 0),
                if_(gt(V('건쿨'), 0), chg('건쿨', -1)),
                if_(and_(eq(V('건쿨'), 0), or_(touch(car.name), touch(tr.name))),
                    chg('건목숨', -1), setv('건쿨', 40), cast('치임'),
                    setv('미니표시', join('건넌 횟수 ', V('건넘'), ' · ♥', V('건목숨'))),
                    if_(le(V('건목숨'), 0), *m.end_blocks(add(mul(V('건넘'), 30), mul(V('최고행'), 2)))),
                    *home),
                if_(ge(V('개구리r'), 8),
                    chg('건넘', 1), chg('배속', 0.15), setv('최고행', 0), cast('건넜다'),
                    setv('미니표시', join('건넌 횟수 ', V('건넘'), ' · ♥', V('건목숨'))), *home)))
    me.on(on_msg('치임'), rep(5, fx('transparency', 70), wait(0.08), fx('transparency', 0), wait(0.08)))
    def step(dc, dr):
        return [if_(eq(V('게임중'), 1),
                    chg('개구리c', dc), chg('개구리r', dr), *clamp_blocks('개구리c', 0, 19), *clamp_blocks('개구리r', 0, 8),
                    if_(gt(V('개구리r'), V('최고행')), setv('최고행', V('개구리r'))), *pos, cast('폴짝'))]
    keys = hidden(m, '건널키')
    for kc, dc, dr in ((K_UP, 0, 1), (K_DOWN, 0, -1), (K_LEFT, -1, 0), (K_RIGHT, 1, 0)):
        keys.on(on_key(kc), *step(dc, dr))
    mgr = hidden(m, '건널담당')
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(mul(V('건넘'), 30), mul(V('최고행'), 2))))
    m.on_start(setv('건넘', 0), setv('최고행', 0), setv('건목숨', 3), setv('건쿨', 0), setv('배속', 1), setv('기차온다', 0),
               setv('개구리c', 10), setv('개구리r', 0))
    m.snd('폴짝', play('tick'))
    m.snd('치임', play('hit'))
    m.snd('건넜다', play('fanfare'))
    m.snd('경보', play('alarm'))
    m.finish('남리 철길 건널목! 차와 기차를 피해 맨 위 시민들에게 가요.\n경보등이 깜빡이면 곧 기차가 지나가요! (3번 건너면 만점)',
             '조작: 방향키로 한 칸씩  ·  부딪히면 처음으로, ♥3')
    return True


GAMES = {16: g16, 17: g17, 18: g18, 19: g19, 20: g20, 21: g21, 22: g22, 23: g23, 24: g24, 25: g25, 26: g26,
         27: g27, 28: g28, 29: g29, 30: g30, 31: g31, 32: g32, 33: g33, 34: g34, 35: g35, 36: g36, 37: g37, 38: g38,
         39: g39, 40: g40}
