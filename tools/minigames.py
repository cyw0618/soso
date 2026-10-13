# -*- coding: utf-8 -*-
"""미니게임 15종 (지역마다 장르가 모두 다름).

공통 틀(MG): 장소 사진 배경 → 소개 창(규칙/조작) → 3·2·1·START → 게임 → FINISH → 점수(0~100) → 유세 결과 장면.
build_minigame(P, idx, ctx) 가 True 를 돌려주면 구현된 것.
"""
import random
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
import data as D
import mg_art as A

SHARED_VARS = ['시작됨', '미니표시', '합계', '_mx', '_my', '_mt', '_mi', '_mk', '_ma', '_mb', '라운드', '정답', '입력순서',
               '라운드길이', '입력가능', '실패', '켜짐', '위치', '상대힘', '마지막키', '대기', '선택', '문제', '다음번호', '벌점',
               '점프중', 'vy', '넘은수', '넘어짐', '바늘', '방향', '사진수', '바속도', '바y', '물고기y', '목표y', '진행도', '잡은수',
               '놓침', '상대손', '내손', '비김', '힌트', '종류', '경과', '_mv']


def need_vars(P):
    for v in SHARED_VARS:
        if v not in P.vars:
            P.var(v, 0)


# ================================================================== 공통 틀
class MG:
    def __init__(self, P, idx, ctx, time_limit=None, status='', dim=0, music='bgm_game'):
        need_vars(P)
        self.music = music
        self.snd_map = []
        self.P, self.idx, self.ctx = P, idx, ctx
        self.sc = ctx['S_GAME'][idx - 1]
        self.p = D.PLACES[idx - 1]
        self.time_limit = time_limit
        self.init_blocks = []
        G.bg(P, self.sc, ctx['ART']('place_%02d' % idx))
        if dim:
            self.S('어둡게', A.plain_rect(480, 270, (2, 4, 14, dim), 'dim_%d' % dim), 0, 0)
        self.status0 = status

    # 줄임 함수
    def S(self, base, pics, x=0, y=0, scale=1.0, visible=True):
        return sprite(self.P, self.sc, base, pics, x, y, scale=scale, visible=visible)

    def T(self, base, txt, x, y, size=10, color=C_WHITE, font=F_BODY, bold=True, align=0, w=None, h=None, visible=True, bg=None):
        return text(self.P, self.sc, base, txt, x, y, size, color, font, bold, align, w=w, h=h, visible=visible, bg=bg)

    def snd(self, msg, *blocks):
        """msg 신호를 받으면 소리 담당이 실행할 블록 (play('pop') 등)."""
        self.snd_map.append((msg, flat(*blocks)))

    def on_start(self, *blocks):
        """장면이 시작될 때(소개 창 전) 초기화할 블록."""
        self.init_blocks += flat(*blocks)

    def end_blocks(self, score_expr=None):
        """게임 끝: 점수를 정하고 '게임종료' 신호."""
        b = []
        if score_expr is not None:
            b.append(setv('점수', score_expr))
        b += [cast('게임종료')]
        return [if_(eq(V('게임중'), 1), setv('게임중', 0), *b)]

    def finish(self, help_lines, controls, end_on_time=None):
        """HUD/소개/카운트다운/시간/종료 처리 오브젝트를 만든다 (게임 오브젝트보다 앞에 보이도록 마지막에 호출)."""
        P, sc, ctx, p = self.P, self.sc, self.ctx, self.p
        # HUD
        self.S('제목띠', K.banner('%s · %s' % (p['name'], p['game']), 236, 30, 'royal'), -116, 118)
        panel(P, sc, 'HUD판', 162, 118, 152, 24, 'glass')
        st = self.T('HUD상태', self.status0, 128, 118, 10, C_WHITE, F_NUM, False, 1, w=96, h=15)
        st.on(on_scene(), forever(write(V('미니표시')), wait(0.05)))
        if self.time_limit:
            self.S('HUD시계', K.icon_img('clock', 13), 186, 118)
            tm = self.T('HUD시간', '', 214, 118, 10, C_ACC, F_NUM, False, 2, w=36, h=15)
            tm.on(on_scene(), forever(write(join(ceil_(V('남은시간')), '초')), wait(0.05)))
        # 소개 창
        intro = [self.S('소개어둡게', A.plain_rect(480, 270, (2, 3, 12, 205), 'dim_intro'), 0, 0)]
        intro.append(panel(P, sc, '소개판', 0, -4, 320, 186, 'glass', header='royal'))
        intro.append(self.S('소개제목', K.big_text(p['game'], 22, 'white'), 0, 72))
        intro.append(self.S('소개종류', K.badge(p['kind'], 74, 18, 'royal'), 0, 46))
        intro.append(self.T('소개설명', help_lines, 0, 14, 11, C_WHITE, F_BODY, True, 0, w=290, h=44))
        intro.append(self.T('소개조작', controls, 0, -22, 9, C_ACC, F_BODY, True, 0, w=290, h=28))
        start_act = [if_(eq(V('시작됨'), 0), setv('시작됨', 1), cast('시작누름'))]
        intro.append(button(P, sc, '시작버튼', '시작!', 0, -60, 110, 28, 'royal', icon='star', actions=start_act))
        intro.append(self.T('소개안내', 'SPACE 키로도 시작할 수 있어요', 0, -82, 8, C_DIM, F_BODY, True, 0, w=200, h=12))
        for o in intro:
            o.on(on_msg('시작누름'), hide())
        # 카운트다운
        for k, (lbl, msg) in enumerate([('3', 'cd3'), ('2', 'cd2'), ('1', 'cd1'), ('START!', 'cdgo')]):
            G.big_pop(P, sc, '카운트%d' % k, K.big_text(lbl, 56 if k < 3 else 44, 'royal'), 0, 10, msg, hold=0.25)
        G.big_pop(P, sc, '끝팝', K.big_text('FINISH!', 44, 'royal'), 0, 22, '끝팝', hold=0.9, fade=False)
        fin = self.T('끝점수', '', 0, -24, 18, C_WHITE, F_NUM, False, 0, w=200, h=26, visible=False)
        fin.on(on_msg('끝팝'), wait(0.4), write(join('유세 점수 ', V('점수'), '점')), show())
        # 담당: 초기화 / 시작 / 시간 / 종료
        mgr = self.T('미니담당', '', -300, -300, 8, visible=False)
        mgr.on(on_scene(), setv('게임중', 0), setv('시작됨', 0), setv('점수', 0), setv('미니표시', self.status0),
               setv('남은시간', self.time_limit or 0), *self.init_blocks)
        mgr.on(on_key(K_SPACE), if_(eq(V('시작됨'), 0), setv('시작됨', 1), cast('시작누름')))
        mgr.on(on_msg('시작누름'), wait(0.25), cast('cd3'), wait(0.55), cast('cd2'), wait(0.55), cast('cd1'), wait(0.55),
               cast('cdgo'), setv('게임중', 1), cast('게임시작'))
        if self.time_limit:
            T_ = self.time_limit
            mgr.on(on_msg('게임시작'), reset_timer(), start_timer(),
                   until(or_(ge(timer(), T_), eq(V('게임중'), 0)), setv('남은시간', sub(T_, timer())), wait(0.05)),
                   if_(eq(V('게임중'), 1), setv('남은시간', 0), cast('시간끝')))
        # 소리: 카운트다운, 게임 음악, 종료 호루라기, 게임별 효과음
        hub = G.sound_hub(P, sc, extra_bgm=[self.music])
        for msg_ in ('cd3', 'cd2', 'cd1'):
            hub.on(on_msg(msg_), play('beep'))
        hub.on(on_msg('cdgo'), play('go'))
        if self.music == 'bgm_rhythm':
            hub.on(on_msg('게임시작'), play(self.music))
        else:
            hub.on(on_msg('게임시작'), until(eq(V('게임중'), 0), play_wait(self.music)))
        hub.on(on_msg('게임종료'), stop_sounds())
        hub.on(on_msg('끝팝'), play('whistle'))
        for msg_, blocks in self.snd_map:
            hub.on(on_msg(msg_), *blocks)
        mgr.on(on_msg('게임종료'), setv('게임중', 0),
               setv('점수', rounded(V('점수'))), if_(gt(V('점수'), 100), setv('점수', 100)), if_(lt(V('점수'), 0), setv('점수', 0)),
               wait(0.3), cast('끝팝'), wait(1.9), setv('결과처리됨', 0), *go(ctx['S_RESULT']))
        G.fader(P, sc, ctx['BLACK'])


def clamp_blocks(var, lo, hi):
    return [if_(lt(V(var), lo), setv(var, lo)), if_(gt(V(var), hi), setv(var, hi))]


# ================================================================== 1. 댄스배틀 (리듬게임)
def g01(P, ctx):
    m = MG(P, 1, ctx, status='콤보 0', dim=120, music='bgm_rhythm')
    rng = random.Random(1)
    beat = 0.5
    times, lanes = [], []
    t = 2.0
    prev = 0
    pattern = [1, 1, 1, 1, 0.5, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, 1, 1, 0.5, 0.5, 0.5, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, 0.5, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, 2]
    for k, step in enumerate(pattern):
        times.append(round(t, 3))
        ln = rng.randint(1, 4)
        if ln == prev and step < 1:
            ln = ln % 4 + 1
        lanes.append(ln)
        prev = ln
        t += step * beat
    N = len(times)
    P.list('리듬시간', times)
    P.list('리듬레인', lanes)
    JY = -80
    LX = [-38, 14, 66, 118]
    sc = m.sc
    # 무대: 조명, 춤추는 나, 레인
    for k, (x, a0) in enumerate(((-150, 20), (230, -20))):
        sp = m.S('조명%d' % k, A.spotlight(), x, 20)
        sp.on(on_scene(), rot(a0), forever(rep(40, rot_by(-0.6 if k == 0 else 0.6), wait(0.03)),
                                         rep(40, rot_by(0.6 if k == 0 else -0.6), wait(0.03))))
    dancer = m.S('춤꾼', ctx['BUST']['me'], -170, -30, scale=0.62)
    dancer.on(on_msg('게임시작'), until(eq(V('게임중'), 0), dancer.pct(104), mvy(4), wait(0.12), dancer.pct(100), mvy(-4),
                                     wait(beat - 0.12)))
    m.S('레인', A.rhythm_lanes(208, 270, JY), 40, 0)
    for l in range(4):
        r = m.S('판정칸%d' % l, [('off', A.rhythm_receptor(l)), ('on', A.rhythm_receptor(l, True))], LX[l], JY)
        r.on(on_key([K_LEFT, K_DOWN, K_UP, K_RIGHT][l]), shape('on'), r.pct(112), wait(0.08), shape('off'), r.pct(100))
    note = m.S('노트', [('n%d' % l, A.rhythm_note(l)) for l in range(4)], 0, 200, visible=False)
    for v in ('내시간', '레인', '판정됨', '복제'):
        note.local(v, 0)
    note.on(on_msg('게임시작'), reset_timer(), start_timer(), setv('_mi', 1),
            until(gt(V('_mi'), N),
                  wait_until(ge(timer(), sub(LGET('리듬시간', V('_mi')), 1.25))),
                  setv('내시간', LGET('리듬시간', V('_mi'))), setv('레인', LGET('리듬레인', V('_mi'))),
                  clone_self(), chg('_mi', 1)),
            wait_until(gt(timer(), times[-1] + 0.6)),
            *m.end_blocks(rounded(mul(div(add(V('맞춤'), mul(V('진행'), 0.6)), N), 100))))
    note.on(on_clone(), setv('복제', 1), setv('판정됨', 0), shape(V('레인')),
            lx(add(-38, mul(sub(V('레인'), 1), 52))), ly(300),
            until(or_(eq(V('판정됨'), 1), gt(timer(), add(V('내시간'), 0.2))),
                  ly(add(JY, mul(sub(V('내시간'), timer()), 185))),
                  ifelse(gt(obj_y(), 100), [hide()], [if_(eq(V('판정됨'), 0), show())])),
            if_(eq(V('판정됨'), 0), setv('판정', 3), setv('콤보', 0), cast('판정표시')),
            del_clone())
    for l, kc in enumerate([K_LEFT, K_DOWN, K_UP, K_RIGHT]):
        note.on(on_key(kc), if_(and_(and_(eq(V('복제'), 1), eq(V('레인'), l + 1)),
                                    and_(eq(V('판정됨'), 0), lt(abs_(sub(timer(), V('내시간'))), 0.16))),
                               setv('판정됨', 1),
                               ifelse(lt(abs_(sub(timer(), V('내시간'))), 0.07), [setv('판정', 1), chg('맞춤', 1)],
                                      [setv('판정', 2), chg('진행', 1)]),
                               chg('콤보', 1), cast('판정표시'), hide()))
    judge = m.S('판정글', [('P', K.big_text('PERFECT', 26, 'royal')), ('G', K.big_text('GOOD', 24, 'white')),
                          ('M', K.big_text('MISS', 24, 'red'))], 40, 6, visible=False)
    judge.on(on_msg('판정표시'), shape(V('판정')), judge.pct(130), show(), rep(5, judge.grow_pct(-6), wait(0.016)), wait(0.25), hide())
    combo = m.T('콤보글', '', 40, 34, 14, C_WHITE, F_NUM, False, 0, w=160, h=20)
    combo.on(on_msg('판정표시'), ifelse(ge(V('콤보'), 2), [write(join(V('콤보'), ' COMBO'))], [write('')]),
             setv('미니표시', join('콤보 ', V('콤보'))))
    m.on_start(setv('맞춤', 0), setv('진행', 0), setv('콤보', 0))
    m.finish('화살표가 아래 판정선에 딱 닿을 때\n같은 방향키를 누르세요! 박자를 타면 PERFECT!',
             '조작: ← ↓ ↑ → 방향키')
    return True


# ================================================================== 2. 은행잎 받기
def g02(P, ctx):
    m = MG(P, 2, ctx, time_limit=20, status='점수 0')
    bk = m.S('바구니', A.basket(), 0, -100, scale=1.3)
    bk.on(on_msg('게임시작'), until(eq(V('게임중'), 0),
                                  if_(key(K_LEFT), mvx(-6)), if_(key(K_RIGHT), mvx(6)),
                                  if_(lt(obj_x(), -190), lx(-190)), if_(gt(obj_x(), 190), lx(190))))
    leaf = m.S('은행잎', [('leaf', A.ginkgo('leaf')), ('gold', A.ginkgo('gold')), ('dry', A.ginkgo('dry'))], 0, 200, scale=1.35, visible=False)
    for v in ('종', '기준x', '각', '낙하'):
        leaf.local(v, 0)
    leaf.on(on_msg('게임시작'), until(eq(V('게임중'), 0), clone_self(), wait(div(rnd(28, 55), 100))))
    leaf.on(on_clone(),
            setv('_mk', rnd(1, 100)),
            ifelse(le(V('_mk'), 12), [setv('종', 2)], [ifelse(le(V('_mk'), 34), [setv('종', 3)], [setv('종', 1)])]),
            shape(V('종')), setv('기준x', rnd(-215, 215)), setv('각', rnd(0, 360)),
            setv('낙하', add(div(rnd(18, 28), 10), mul(sub(20, V('남은시간')), 0.07))),
            xy(V('기준x'), 150), rot(rnd(-30, 30)), show(),
            until(or_(lt(obj_y(), -140), eq(V('게임중'), 0)),
                  mvy(mul(V('낙하'), -1)), chg('각', 5), lx(add(V('기준x'), mul(sin_(V('각')), 14))), rot_by(1.5),
                  if_(touch(bk.name),
                      ifelse(eq(V('종'), 1), [chg('합계', 1), setv('_mv', 1)],
                             [ifelse(eq(V('종'), 2), [chg('합계', 3), setv('_mv', 2)], [chg('합계', -2), setv('_mv', 3)])]),
                      setv('_mx', obj_x()), setv('미니표시', join('점수 ', V('합계'))), cast('잎효과'), del_clone())),
            del_clone())
    fx_ = m.S('잎글', [('a', K.big_text('+1', 18, 'white')), ('b', K.big_text('+3', 22, 'royal')), ('c', K.big_text('-2', 20, 'red'))],
              0, -70, visible=False)
    fx_.on(on_msg('잎효과'), shape(V('_mv')), xy(V('_mx'), -70), fx('transparency', 0), show(),
           rep(10, mvy(2), fx_add('transparency', 10), wait(0.02)), hide())
    m.on_start(setv('합계', 0))
    m.snd('잎효과', ifelse(eq(V('_mv'), 3), [play('bad')], [play('pop')]))
    mgr = m.T('잎담당', '', -300, -300, 8, visible=False)
    mgr.on(on_msg('시간끝'), wait(0.2), *m.end_blocks(mul(V('합계'), 3)))
    m.finish('떨어지는 은행잎을 바구니로 받으세요!\n반짝이는 황금잎은 +3, 마른 잎은 -2',
             '조작: ← → 방향키로 바구니 이동')
    return True


# ================================================================== 3. 팔씨름 (연타)
def g03(P, ctx):
    m = MG(P, 3, ctx, time_limit=15, status='힘 0')
    m.S('나', ctx['BUST']['me'], -168, 4, scale=0.6)
    op = m.S('상대', ctx['BUST']['u1'], 168, 4, scale=0.6)
    m.S('상대이름', K.badge('첫째 큰아버지', 80, 18, 'red'), 168, -50)
    m.S('내이름', K.badge('나 (막내)', 70, 18, 'royal'), -168, -50)
    ar = m.S('팔', A.arms(), 0, -44)
    m.S('탁자', A.table_top(300, 46), 0, -66)
    m.S('힘막대', A.tug_meter(260, 22), 0, -110)
    knob = m.S('힘표시', A.tug_knob(), 0, -110)
    knob.on(on_scene(), lx(0))
    knob.on(on_msg('게임시작'), until(eq(V('게임중'), 0), lx(mul(V('위치'), 1.2)), wait(0.02)))
    ar.on(on_scene(), rot(0))
    ar.on(on_msg('게임시작'), until(eq(V('게임중'), 0), rot(mul(V('위치'), 0.42)), wait(0.02)))
    op.on(on_msg('게임시작'), until(eq(V('게임중'), 0), if_(gt(V('상대힘'), 2.2), mvx(2), wait(0.03), mvx(-2)), wait(0.05)))
    push = [if_(eq(V('게임중'), 1), chg('위치', 4.0), cast('밀기'))]
    mgr = m.T('팔담당', '', -300, -300, 8, visible=False)
    mgr.on(on_key(K_LEFT), if_(ne(V('마지막키'), 1), setv('마지막키', 1), *push))
    mgr.on(on_key(K_RIGHT), if_(ne(V('마지막키'), 2), setv('마지막키', 2), *push))
    mgr.on(on_msg('게임시작'), setv('_mt', 0),
           until(eq(V('게임중'), 0),
                 setv('상대힘', add(add(0.45, mul(sub(15, V('남은시간')), 0.045)), div(rnd(-20, 30), 100))),
                 if_(le(rnd(1, 100), 4), setv('상대힘', 3.2)),
                 chg('위치', mul(V('상대힘'), -1)),
                 setv('미니표시', join('힘 ', rounded(V('위치')))),
                 if_(ge(V('위치'), 100), setv('위치', 100), *m.end_blocks(add(70, mul(V('남은시간'), 2.2)))),
                 if_(le(V('위치'), -100), setv('위치', -100), *m.end_blocks(20)),
                 wait(0.05)))
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(48, mul(V('위치'), 0.42))))
    shake = m.S('힘글', K.big_text('힘!', 20, 'white'), -60, 30, visible=False)
    shake.on(on_msg('밀기'), xy(rnd(-90, -40), rnd(10, 40)), shake.pct(80), fx('transparency', 0), show(),
             rep(6, shake.grow_pct(6), fx_add('transparency', 16), wait(0.016)), hide())
    m.on_start(setv('위치', 0), setv('상대힘', 0), setv('마지막키', 0))
    m.snd('밀기', play('tick'))
    m.finish('첫째 큰아버지와 팔씨름 한 판!\n← → 키를 번갈아 빠르게 눌러 팔을 넘기세요!',
             '조작: ← → 번갈아 연타 (한 키만 누르면 힘이 안 들어가요)')
    return True


# ================================================================== 4. 복숭아 선별
def g04(P, ctx):
    NP = 16
    m = MG(P, 4, ctx, status='선별 0/%d' % NP)
    m.S('컨베이어', A.conveyor(330, 34), 0, -6)
    cr = [m.S('상자왼', A.crate('덜 익음', '←', 'green'), -170, -92), m.S('상자아래', A.crate('상함', '↓', 'gray'), 0, -100),
          m.S('상자오른', A.crate('잘 익음', '→', 'red'), 170, -92)]
    pc = m.S('복숭아', [('raw', A.peach('raw')), ('ripe', A.peach('ripe')), ('bad', A.peach('bad'))], -230, 14, visible=False)
    target = {1: (-170, -84), 3: (0, -92), 2: (170, -84)}
    ok = m.S('정답글', [('o', K.big_text('정답!', 22, 'royal')), ('x', K.big_text('땡!', 22, 'red'))], 0, 52, visible=False)
    ok.on(on_msg('선별판정'), ifelse(eq(V('_mv'), 1), [shape('o')], [shape('x')]), ok.pct(130), show(),
          rep(5, ok.grow_pct(-6), wait(0.016)), wait(0.35), hide())
    mgr = m.T('복숭아담당', '', -300, -300, 8, visible=False)
    for kc, ch in ((K_LEFT, 1), (K_RIGHT, 2), (K_DOWN, 3)):
        mgr.on(on_key(kc), if_(eq(V('대기'), 1), setv('선택', ch), setv('대기', 0)))
    pc.on(on_msg('게임시작'), setv('_mi', 1),
          until(or_(gt(V('_mi'), NP), eq(V('게임중'), 0)),
                setv('종류', rnd(1, 3)), shape(V('종류')), xy(-230, 14), rot(0), show(), setv('선택', 0),
                setv('_mk', add(5, mul(V('_mi'), 0.45))),
                until(ge(obj_x(), 0), mvx(V('_mk')), rot_by(4)),
                lx(0), setv('대기', 1), setv('_mt', 0),
                until(or_(eq(V('대기'), 0), gt(V('_mt'), sub(2.6, mul(V('_mi'), 0.1)))), wait(0.05), chg('_mt', 0.05)),
                setv('대기', 0),
                ifelse(eq(V('선택'), V('종류')), [chg('맞춤', 1), setv('_mv', 1)], [chg('틀림', 1), setv('_mv', 2)]),
                cast('선별판정'),
                ifelse(eq(V('선택'), 1), [glide(0.2, target[1][0], target[1][1])],
                       [ifelse(eq(V('선택'), 2), [glide(0.2, target[2][0], target[2][1])],
                               [ifelse(eq(V('선택'), 3), [glide(0.2, target[3][0], target[3][1])], [glide(0.3, 250, 14)])])]),
                hide(), setv('미니표시', join('선별 ', V('_mi'), '/', NP)), chg('_mi', 1), wait(0.12)),
          *m.end_blocks(mul(div(V('맞춤'), NP), 100)))
    for o, ch in zip(cr, (1, 3, 2)):
        o.on(on_msg('선별판정'), if_(eq(V('선택'), ch), o.pct(112), wait(0.1), o.pct(100)))
    m.on_start(setv('맞춤', 0), setv('틀림', 0), setv('대기', 0))
    m.snd('선별판정', ifelse(eq(V('_mv'), 1), [play('good')], [play('bad')]))
    m.finish('컨베이어로 오는 복숭아를 알맞은 상자로!\n초록=덜 익음, 분홍=잘 익음, 점박이 갈색=상함',
             '조작: ← 덜 익음 · → 잘 익음 · ↓ 상함  (점점 빨라져요)')
    return True


# ================================================================== 5. 주문 기억하기 (사이먼)
def g05(P, ctx):
    R = 5
    m = MG(P, 5, ctx, status='라운드 1/%d' % R, dim=90)
    P.list('주문순서', [1] * 8)
    m.S('손님', ctx['BUST']['u2'], 0, 74, scale=0.36)
    bub = m.T('손님말', '', 0, 40, 11, C_WHITE, F_NUM, False, 0, w=260, h=18, bg=C_BOX)
    xs = [-150, -50, 50, 150]
    for k in range(1, 5):
        c = m.S('메뉴%d' % k, [('off', A.cafe_card(k - 1)), ('on', A.cafe_card(k - 1, True))], xs[k - 1], -42)
        c.on(on_msg('카드켜기'), if_(eq(V('켜짐'), k), shape('on'), c.pct(108)))
        c.on(on_msg('카드끄기'), shape('off'), c.pct(100))
        # 판정은 기다림 없이 바로 (같은 메뉴를 빠르게 두 번 눌러도 놓치지 않게), 반짝임은 따로
        c.on(on_click(), if_(and_(eq(V('입력가능'), 1), eq(V('게임중'), 1)),
                             ifelse(eq(LGET('주문순서', V('입력순서')), k), [chg('입력순서', 1)], [setv('실패', 1)])))
        c.on(on_click(), if_(eq(V('입력가능'), 1), G.sfx('tone%d' % k), shape('on'), c.pct(108), wait(0.12), shape('off'), c.pct(100)))
    mgr = m.T('주문담당', '', -300, -300, 8, visible=False)
    mgr.on(on_msg('게임시작'),
           *[lst_set('주문순서', k, rnd(1, 4)) for k in range(1, 9)],
           setv('라운드', 1), setv('실패', 0),
           until(or_(gt(V('라운드'), R), eq(V('실패'), 1)),
                 setv('라운드길이', add(2, V('라운드'))), setv('미니표시', join('라운드 ', V('라운드'), '/', R)),
                 setv('입력가능', 0), setv('선택', 0), cast('말:보기'), wait(0.9),
                 setv('_mi', 1),
                 until(gt(V('_mi'), V('라운드길이')),
                       setv('켜짐', LGET('주문순서', V('_mi'))), cast('카드켜기'), wait(sub(0.6, mul(V('라운드'), 0.05))),
                       cast('카드끄기'), wait(0.16), chg('_mi', 1)),
                 cast('말:따라'), setv('입력순서', 1), setv('입력가능', 1),
                 wait_until(or_(gt(V('입력순서'), V('라운드길이')), eq(V('실패'), 1))),
                 setv('입력가능', 0),
                 ifelse(eq(V('실패'), 0), [chg('맞춤', 1), cast('말:성공'), wait(0.8), chg('라운드', 1)],
                        [cast('말:실패'), wait(1.0)])),
           *m.end_blocks(mul(V('맞춤'), 100.0 / R)))
    bub.on(on_msg('말:보기'), write(join('주문 들어갑니다! (', V('라운드길이'), '잔)')), text_color(C_WHITE))
    bub.on(on_msg('말:따라'), write('자, 순서대로 눌러 주세요!'), text_color(C_ACC))
    bub.on(on_msg('말:성공'), write('완벽해요! 단골 할게요~'), text_color(C_ACC))
    bub.on(on_msg('말:실패'), write('어... 그거 아닌데요?'), text_color(C_RED))
    m.on_start(setv('맞춤', 0), setv('입력가능', 0), setv('켜짐', 0))
    m.snd('카드켜기', *[if_(eq(V('켜짐'), k), play('tone%d' % k)) for k in range(1, 5)])
    m.snd('말:성공', play('good'))
    m.snd('말:실패', play('bad'))
    m.finish('손님의 주문 순서를 잘 보고 기억했다가\n같은 순서로 메뉴를 눌러 주세요! (5라운드)',
             '조작: 마우스로 메뉴 클릭  ·  라운드마다 주문이 1잔씩 늘어나요')
    return True


# ================================================================== 6. 풍선 사격
def g06(P, ctx):
    m = MG(P, 6, ctx, time_limit=20, status='점수 0')
    kinds = ['blue', 'red', 'purple', 'silver', 'gold', 'bomb']
    bl = m.S('풍선', [(k, A.balloon(k)) for k in kinds] + [('pop', A.burst()), ('popr', A.burst((255, 80, 100)))], 0, -200,
             visible=False)
    for v in ('종', '기준x', '각', '속', '맞음', '복제'):
        bl.local(v, 0)
    bl.on(on_msg('게임시작'), until(eq(V('게임중'), 0), clone_self(), wait(div(rnd(26, 52), 100))))
    bl.on(on_clone(), setv('복제', 1), setv('맞음', 0),
          setv('_mk', rnd(1, 100)),
          ifelse(le(V('_mk'), 8), [setv('종', 5)], [ifelse(le(V('_mk'), 22), [setv('종', 6)], [setv('종', rnd(1, 4))])]),
          shape(V('종')), setv('기준x', rnd(-215, 215)), setv('각', rnd(0, 360)),
          setv('속', add(div(rnd(12, 24), 10), mul(sub(20, V('남은시간')), 0.06))),
          xy(V('기준x'), -165), rot(0), show(),
          until(or_(or_(gt(obj_y(), 165), eq(V('맞음'), 1)), eq(V('게임중'), 0)),
                mvy(V('속')), chg('각', 3), lx(add(V('기준x'), mul(sin_(V('각')), 10)))),
          if_(eq(V('맞음'), 1), ifelse(eq(V('종'), 6), [shape('popr')], [shape('pop')]), bl.pct(70),
              rep(6, bl.grow_pct(10), fx_add('transparency', 15), wait(0.016))),
          del_clone())
    bl.on(on_mouse_down(), if_(and_(and_(eq(V('복제'), 1), eq(V('맞음'), 0)), and_(eq(V('게임중'), 1), touch('mouse'))),
                               setv('맞음', 1),
                               ifelse(eq(V('종'), 6), [chg('합계', -3), chg('틀림', 1)],
                                      [ifelse(eq(V('종'), 5), [chg('합계', 3)], [chg('합계', 1)])]),
                               setv('_mv', V('종')), cast('풍선펑'),
                               setv('미니표시', join('점수 ', V('합계')))))
    ch = m.S('조준', A.crosshair(), 0, 0, visible=False)
    ch.on(on_msg('게임시작'), show(), until(eq(V('게임중'), 0), xy(mouse_x(), mouse_y())), hide())
    ch.on(on_mouse_down(), if_(eq(V('게임중'), 1), ch.pct(80), wait(0.05), ch.pct(100)))
    mgr = m.T('풍선담당', '', -300, -300, 8, visible=False)
    mgr.on(on_msg('시간끝'), wait(0.2), *m.end_blocks(mul(V('합계'), 3.4)))
    m.on_start(setv('합계', 0), setv('틀림', 0))
    m.snd('풍선펑', ifelse(eq(V('_mv'), 6), [play('bad')], [play('pop')]))
    m.finish('올라오는 풍선을 클릭해서 터뜨리세요!\n황금 풍선은 +3, 해골 "꽝" 풍선은 -3',
             '조작: 마우스로 조준하고 클릭')
    return True


# ================================================================== 7. 조치원 퀴즈
def g07(P, ctx):
    Q = D.QUIZ
    m = MG(P, 7, ctx, status='문제 1/%d' % len(Q), dim=110)
    P.list('퀴즈문제', [q[0] for q in Q])
    P.list('퀴즈보기', [o for q in Q for o in q[1]])
    P.list('퀴즈정답', [q[2] for q in Q])
    panel(P, m.sc, '문제판', 0, 56, 420, 70, 'glass', header='royal')
    qn = m.T('문제번호', '', -170, 78, 10, C_WHITE, F_NUM, False, 1, w=80, h=14)
    qt = m.T('문제글', '', 0, 50, 13, C_WHITE, F_BODY, True, 0, w=390, h=36)
    tb = m.S('문제시간', K.bar_set('quiz_time', 300, 7, 'royal'), 0, 12)
    tb.on(on_msg('게임시작'), until(eq(V('게임중'), 0), shape(add(floor(mul(div(V('_mt'), 10), 40)), 1)), wait(0.05)))
    xs = [-140, 0, 140]
    for k in range(1, 4):
        c = m.S('보기%d' % k, [('n', A.quiz_card('n')), ('ok', A.quiz_card('ok')), ('no', A.quiz_card('no'))], xs[k - 1], -44)
        G.hover_scripts(c, 105)
        m.S('보기번호%d' % k, K.badge(str(k), 20, 18, 'royal'), xs[k - 1] - 50, -18)
        at = m.T('보기글%d' % k, '', xs[k - 1], -44, 12, C_WHITE, F_NUM, False, 0, w=116, h=40)
        idx = add(mul(sub(V('문제'), 1), 3), k)
        at.on(on_msg('새문제'), write(LGET('퀴즈보기', idx)))
        c.on(on_msg('새문제'), shape('n'))
        c.on(on_msg('정답공개'), ifelse(eq(V('정답'), k), [shape('ok')], [if_(eq(V('선택'), k), shape('no'))]))
        pick = [if_(and_(eq(V('대기'), 1), eq(V('게임중'), 1)), setv('선택', k), setv('대기', 0))]
        c.on(on_click(), *pick)
        at.on(on_click(), *pick)
        m.T('보기키%d' % k, '', -300, -300, 8, visible=False).on(on_key(48 + k), *pick)
    res = m.S('퀴즈결과', [('o', K.big_text('정답!', 30, 'royal')), ('x', K.big_text('오답...', 28, 'red'))], 0, -100, visible=False)
    res.on(on_msg('정답공개'), ifelse(eq(V('선택'), V('정답')), [shape('o')], [shape('x')]), res.pct(130), show(),
           rep(5, res.grow_pct(-6), wait(0.016)), wait(0.8), hide())
    mgr = m.T('퀴즈담당', '', -300, -300, 8, visible=False)
    mgr.on(on_msg('게임시작'), setv('문제', 1),
           until(gt(V('문제'), len(Q)),
                 setv('미니표시', join('문제 ', V('문제'), '/', len(Q))), cast('새문제'),
                 setv('선택', 0), setv('대기', 1), setv('_mt', 10),
                 until(or_(eq(V('대기'), 0), le(V('_mt'), 0)), wait(0.05), chg('_mt', -0.05)),
                 setv('대기', 0), setv('정답', LGET('퀴즈정답', V('문제'))),
                 if_(eq(V('선택'), V('정답')), chg('맞춤', 1)),
                 cast('정답공개'), wait(1.5), chg('문제', 1)),
           *m.end_blocks(mul(V('맞춤'), 100.0 / len(Q))))
    qn.on(on_msg('새문제'), write(join('Q', V('문제'), '.')))
    qt.on(on_msg('새문제'), write(LGET('퀴즈문제', V('문제'))))
    m.on_start(setv('맞춤', 0), setv('대기', 0), setv('_mt', 10), setv('문제', 1))
    m.snd('정답공개', ifelse(eq(V('선택'), V('정답')), [play('good')], [play('bad')]))
    m.finish('조치원에 대한 퀴즈 5문제!\n문제마다 10초 안에 정답을 고르세요.',
             '조작: 보기를 클릭하거나 숫자키 1 · 2 · 3')
    return True


# ================================================================== 8. 미로 탈출
def g08(P, ctx):
    m = MG(P, 8, ctx, time_limit=40, status='투표지 0/5', dim=60)
    wall_path, dead = A.maze_walls()
    m.S('미로바닥', A.maze_floor(), 0, -8)
    wall = m.S('미로벽', wall_path, 0, -8)
    cell = lambda cx, cy: (-168 + 24 * cx, 88 - 24 * cy - 8)
    ex, ey = cell(A.MAZE_W - 1, A.MAZE_H - 1)
    flag = m.S('출구', A.exit_flag(), ex + 2, ey + 2)
    me = m.S('나', ctx['PORT']['me'], *cell(0, 0), scale=0.62)
    sx, sy = cell(0, 0)
    me.on(on_scene(), xy(sx, sy))
    step = 2
    mv = []
    for kc, dx, dy in ((K_LEFT, -step, 0), (K_RIGHT, step, 0), (K_UP, 0, step), (K_DOWN, 0, -step)):
        if dx:
            mv.append(if_(key(kc), mvx(dx), if_(touch(wall.name), mvx(-dx))))
        else:
            mv.append(if_(key(kc), mvy(dy), if_(touch(wall.name), mvy(-dy))))
    me.on(on_msg('게임시작'), until(eq(V('게임중'), 0), *mv,
                                  if_(touch(flag.name), cast('탈출'), *m.end_blocks(add(add(50, mul(V('남은시간'), 1.0)), mul(V('진행'), 5)))))
          )
    for k, (cx, cy) in enumerate(dead[:5]):
        bx, by = cell(cx, cy)
        b = m.S('투표지%d' % k, A.ballot_paper(), bx, by)
        b.on(on_scene(), show(), forever(rep(10, mvy(0.3), wait(0.04)), rep(10, mvy(-0.3), wait(0.04))))
        b.on(on_msg('게임시작'), until(eq(V('게임중'), 0), if_(touch(me.name), chg('진행', 1), G.sfx('coin'),
                                                             setv('미니표시', join('투표지 ', V('진행'), '/5')), hide(), stop_thread()),
                                    wait(0.03)))
    mgr = m.T('미로담당', '', -300, -300, 8, visible=False)
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(10, mul(V('진행'), 6))))
    G.big_pop(P, m.sc, '탈출글', K.big_text('탈출 성공!', 30, 'royal'), 0, 40, '탈출', hold=0.6)
    m.on_start(setv('진행', 0))
    m.snd('탈출', play('good'))
    m.finish('1927아트센터 미로에서 출구(EXIT)를 찾아 탈출!\n가는 길에 투표지(최대 5장)를 주우면 보너스!',
             '조작: ← ↑ → ↓ 방향키  ·  빨리 나올수록 점수 UP')
    return True


# ================================================================== 9. 두더지잡기
def g09(P, ctx):
    m = MG(P, 9, ctx, time_limit=22, status='점수 0', dim=50)
    xs, ys = [-130, 0, 130], [36, -24, -84]
    for r in range(3):
        for c in range(3):
            k = r * 3 + c
            x, y = xs[c], ys[r]
            m.S('구멍%d' % k, A.hole_back(), x, y - 14)
            mo = m.S('두더지%d' % k, [('m', A.mole()), ('h', A.mole('mole', True)), ('p', A.mole('peach'))], x, y - 40, visible=False)
            mo.local('맞음', 0)
            mo.local('종', 0)
            mo.local('올라옴', 0)
            mo.on(on_msg('게임시작'),
                  until(eq(V('게임중'), 0),
                        wait(div(rnd(5, 32), 10)),
                        if_(eq(V('게임중'), 1),
                            ifelse(le(rnd(1, 100), 18), [setv('종', 3)], [setv('종', 1)]),
                            shape(V('종')), setv('맞음', 0), ly(y - 40), show(), setv('올라옴', 1),
                            rep(6, mvy(6), wait(0.016)),
                            setv('_mt', 0),
                            until(or_(eq(V('맞음'), 1), gt(V('_mt'), sub(1.1, mul(sub(22, V('남은시간')), 0.025)))), wait(0.05),
                                  chg('_mt', 0.05)),
                            if_(eq(V('맞음'), 1), wait(0.25)),
                            rep(6, mvy(-6), wait(0.016)), hide(), setv('올라옴', 0))))
            mo.on(on_mouse_down(), if_(and_(and_(eq(V('맞음'), 0), eq(V('게임중'), 1)), and_(eq(V('올라옴'), 1), touch('mouse'))),
                                       setv('맞음', 1),
                                       ifelse(eq(V('종'), 3), [chg('합계', -2), chg('틀림', 1), G.sfx('bad')],
                                              [chg('합계', 1), shape('h'), setv('_mx', obj_x()), setv('_my', obj_y()), cast('쾅')]),
                                       setv('미니표시', join('점수 ', V('합계')))))
            m.S('흙%d' % k, A.hole_front(), x, y - 26)
    boom = m.S('쾅', A.burst(), 0, 0, visible=False)
    boom.on(on_msg('쾅'), xy(V('_mx'), add(V('_my'), 14)), boom.pct(60), fx('transparency', 0), show(),
            rep(6, boom.grow_pct(12), fx_add('transparency', 15), wait(0.016)), hide())
    hm = m.S('뿅망치', [('up', A.hammer()), ('down', A.hammer(True))], 0, 0, visible=False)
    hm.on(on_msg('게임시작'), show(), until(eq(V('게임중'), 0), xy(add(mouse_x(), 16), add(mouse_y(), 14))), hide())
    hm.on(on_mouse_down(), if_(eq(V('게임중'), 1), shape('down'), wait(0.08), shape('up')))
    mgr = m.T('두더지담당', '', -300, -300, 8, visible=False)
    mgr.on(on_msg('시간끝'), wait(0.3), *m.end_blocks(mul(V('합계'), 4.6)))
    m.on_start(setv('합계', 0), setv('틀림', 0))
    m.snd('쾅', play('hit'))
    m.finish('구멍에서 튀어나오는 "반대" 두더지를 때리세요!\n복숭아를 때리면 감점! 점점 빨라져요.',
             '조작: 마우스 클릭')
    return True


# ================================================================== 10. 허들 달리기
def g10(P, ctx):
    NH = 14
    m = MG(P, 10, ctx, status='허들 0/%d' % NH)
    GY = -76
    m.S('트랙', A.track(480, 60), 0, -112)
    rn = m.S('선수', [('run1', A.runner('run1')), ('run2', A.runner('run2')), ('jump', A.runner('jump')), ('fall', A.runner('fall'))],
             -150, GY, scale=1.2)
    rn.on(on_scene(), xy(-150, GY), shape('run1'))
    jump = [if_(and_(eq(V('점프중'), 0), eq(V('게임중'), 1)), setv('점프중', 1), setv('vy', 8.0), G.sfx('jump'))]
    rn.on(on_key(K_SPACE), *jump)
    rn.on(on_key(K_UP), *jump)
    rn.on(on_msg('게임시작'),
          until(eq(V('게임중'), 0),
                ifelse(eq(V('점프중'), 1),
                       [mvy(V('vy')), chg('vy', -0.4),
                        if_(le(obj_y(), GY), ly(GY), setv('점프중', 0), setv('vy', 0))],
                       [])))
    rn.on(on_msg('게임시작'),
          until(eq(V('게임중'), 0),
                ifelse(gt(V('넘어짐'), 0), [shape('fall'), wait(0.45), setv('넘어짐', 0)],
                       [ifelse(eq(V('점프중'), 1), [shape('jump'), wait(0.05)],
                               [shape('run1'), wait(0.1), if_(eq(V('점프중'), 0), shape('run2')), wait(0.1)])])))
    hd = m.S('허들', A.hurdle(), 300, GY - 6, visible=False)
    hd.local('부딪힘', 0)
    hd.local('지남', 0)
    hd.on(on_msg('게임시작'), setv('_mi', 1),
          until(or_(gt(V('_mi'), NH), eq(V('게임중'), 0)),
                clone_self(), chg('_mi', 1), wait(div(rnd(95, 170), 100))),
          wait(2.6), *m.end_blocks(mul(div(V('넘은수'), NH), 100)))
    hd.on(on_clone(), setv('부딪힘', 0), setv('지남', 0), xy(270, GY - 6), show(),
          until(or_(lt(obj_x(), -260), eq(V('게임중'), 0)),
                mvx(mul(add(4.2, mul(V('넘은수'), 0.12)), -1)),
                if_(and_(eq(V('부딪힘'), 0), touch(rn.name)), setv('부딪힘', 1), setv('넘어짐', 1), chg('틀림', 1), cast('꽈당'), rot(-70)),
                if_(and_(eq(V('지남'), 0), lt(obj_x(), -175)), setv('지남', 1),
                    if_(eq(V('부딪힘'), 0), chg('넘은수', 1), cast('넘음')),
                    setv('미니표시', join('허들 ', V('넘은수'), '/', NH)))),
          del_clone())
    ouch = m.S('꽈당', K.big_text('꽈당!', 22, 'red'), -150, -20, visible=False)
    ouch.on(on_msg('꽈당'), ouch.pct(120), show(), rep(5, ouch.grow_pct(-5), wait(0.02)), wait(0.3), hide())
    nice = m.S('나이스', K.big_text('NICE!', 18, 'royal'), -150, 0, visible=False)
    nice.on(on_msg('넘음'), nice.pct(120), fx('transparency', 0), show(), rep(8, mvy(1.5), fx_add('transparency', 12), wait(0.02)),
            ly(0), hide())
    m.on_start(setv('넘은수', 0), setv('점프중', 0), setv('vy', 0), setv('넘어짐', 0), setv('틀림', 0))
    m.snd('꽈당', play('bad'))
    m.snd('넘음', play('tick'))
    m.finish('세종시민운동장 허들 경기! 허들 14개를\n타이밍 맞춰 뛰어넘으세요. 점점 빨라져요!',
             '조작: SPACE 또는 ↑ 로 점프')
    return True


# ================================================================== 11. 벚꽃 촬영 (타이밍)
def g11(P, ctx):
    NS = 5
    m = MG(P, 11, ctx, status='사진 0/%d' % NS)
    m.S('뷰파인더', A.viewfinder(330, 210), 0, 12)
    m.S('타이밍바', A.timing_bar(300, 24), 0, -98)
    zone = m.S('정답구간', [('z%d' % k, A.sweet_zone(k)) for k in range(5)], 0, -98)
    nd = m.S('바늘', A.needle(), -146, -92)
    flash = m.S('플래시', A.plain_rect(480, 270, (255, 255, 255, 255), 'white_full'), 0, 0, visible=False)
    flash.on(on_msg('찰칵'), fx('transparency', 0), show(), rep(8, fx_add('transparency', 12.5), wait(0.02)), hide())
    pol = m.S('사진', [(g, A.polaroid(g)) for g in 'SABC'], 160, 30, visible=False)
    pol.on(on_msg('사진결과'), shape(V('_mv')), xy(240, 10), rot(-8), show(), glide(0.2, 165, 20), wait(0.9), glide(0.2, 260, 20), hide())
    HW = [30, 24, 19, 15, 12]
    zone.on(on_msg('새사진'), shape(add(V('사진수'), 1)), setv('_mx', rnd(-120, 120)), lx(V('_mx')))
    nd.on(on_msg('게임시작'), setv('방향', 1),
          until(eq(V('게임중'), 0),
                if_(eq(V('대기'), 1),
                    mvx(mul(V('방향'), add(3.2, mul(V('사진수'), 0.9)))),
                    if_(gt(obj_x(), 146), lx(146), setv('방향', -1)), if_(lt(obj_x(), -146), lx(-146), setv('방향', 1)))))
    shoot = [if_(and_(eq(V('대기'), 1), eq(V('게임중'), 1)), setv('대기', 0), setv('바늘', obj_x(nd.name)), cast('셔터'))]
    mgr = m.T('사진담당', '', -300, -300, 8, visible=False)
    mgr.on(on_key(K_SPACE), *shoot)
    mgr.on(on_msg('게임시작'), setv('사진수', 0),
           until(ge(V('사진수'), NS),
                 cast('새사진'), setv('대기', 1), wait_until(eq(V('대기'), 0)),
                 cast('찰칵'),
                 setv('_mk', abs_(sub(V('바늘'), V('_mx')))),
                 setv('_ma', LGET('구간폭', add(V('사진수'), 1))),
                 ifelse(le(V('_mk'), mul(V('_ma'), 0.35)), [setv('_mv', 1), chg('합계', 20)],
                        [ifelse(le(V('_mk'), V('_ma')), [setv('_mv', 2), chg('합계', 15)],
                                [ifelse(le(V('_mk'), mul(V('_ma'), 2)), [setv('_mv', 3), chg('합계', 8)], [setv('_mv', 4), chg('합계', 2)])])]),
                 cast('사진결과'), chg('사진수', 1), setv('미니표시', join('사진 ', V('사진수'), '/', NS)), wait(1.4)),
           *m.end_blocks(V('합계')))
    P.list('구간폭', HW)
    m.T('촬영안내', '바늘이 분홍 구간 한가운데 올 때 찰칵!', 0, -76, 9, C_WHITE, F_BODY, True, 0, w=260, h=14, bg=C_BOX)
    m.on_start(setv('합계', 0), setv('대기', 0), setv('사진수', 0))
    m.snd('찰칵', play('shutter'))
    m.finish('조천 벚꽃길에서 인생샷 5장!\n바늘이 분홍 구간 한가운데 왔을 때 셔터를 누르세요.',
             '조작: SPACE 셔터  ·  갈수록 구간이 좁아지고 바늘이 빨라져요')
    return True


# ================================================================== 12. 연잎 순서 터치
def g12(P, ctx):
    m = MG(P, 12, ctx, time_limit=40, status='다음 1', dim=40)
    slots = []
    for r in range(3):
        for c in range(3):
            slots.append((-150 + c * 150, 50 - r * 70))
    P.list('연잎자리', list(range(1, 10)))
    P.list('자리X', [s[0] for s in slots])
    P.list('자리Y', [s[1] for s in slots])
    for n in range(1, 10):
        pad = m.S('연잎%d' % n, [('n', A.lotus_pad(n)), ('d', A.lotus_pad(n, True))], 0, 0)
        pad.on(on_msg('연잎배치'), shape('n'), rot(rnd(-20, 20)),
               xy(add(LGET('자리X', LGET('연잎자리', n)), rnd(-26, 26)), add(LGET('자리Y', LGET('연잎자리', n)), rnd(-12, 12))))
        pad.on(on_click(), if_(eq(V('게임중'), 1),
                               ifelse(eq(V('다음번호'), n),
                                      [shape('d'), pad.pct(115), chg('다음번호', 1), setv('미니표시', join('다음 ', V('다음번호'))), G.sfx('tick'),
                                       wait(0.08), pad.pct(100)],
                                      [if_(gt(V('다음번호'), n), stop_thread()),
                                       chg('벌점', 1), cast('땡'), rep(3, mvx(4), wait(0.02), mvx(-4), wait(0.02))])))
    bad = m.S('땡', K.big_text('땡! +1초', 18, 'red'), 0, 100, visible=False)
    bad.on(on_msg('땡'), bad.pct(120), show(), rep(5, bad.grow_pct(-4), wait(0.02)), wait(0.3), hide())
    rd = m.S('라운드글', K.big_text('다음 연못!', 26, 'royal'), 0, 0, visible=False)
    rd.on(on_msg('라운드2'), rd.pct(130), show(), rep(5, rd.grow_pct(-6), wait(0.02)), wait(0.4), hide())
    shuffle = [setv('_mi', 9),
               until(lt(V('_mi'), 2),
                     setv('_mk', rnd(1, V('_mi'))), setv('_ma', LGET('연잎자리', V('_mi'))),
                     lst_set('연잎자리', V('_mi'), LGET('연잎자리', V('_mk'))), lst_set('연잎자리', V('_mk'), V('_ma')),
                     chg('_mi', -1)),
               cast('연잎배치')]
    mgr = m.T('연잎담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), *shuffle)
    mgr.on(on_msg('게임시작'),
           setv('라운드', 1), setv('다음번호', 1),
           wait_until(or_(gt(V('다음번호'), 9), eq(V('게임중'), 0))),
           if_(eq(V('게임중'), 1), cast('라운드2'), *shuffle, setv('다음번호', 1), setv('라운드', 2), setv('미니표시', '다음 1'),
               wait_until(or_(gt(V('다음번호'), 9), eq(V('게임중'), 0))),
               setv('_mt', add(sub(40, V('남은시간')), V('벌점'))),
               *m.end_blocks(sub(100, mul(sub(V('_mt'), 14), 2.5)))))
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(mul(sub(V('라운드'), 1), 30), mul(V('다음번호'), 2))))
    m.on_start(setv('다음번호', 1), setv('벌점', 0))
    m.snd('땡', play('bad'))
    m.snd('라운드2', play('good'))
    m.finish('연잎에 적힌 숫자를 1부터 9까지\n순서대로 빠르게 눌러 주세요! (연못 2개)',
             '조작: 마우스 클릭  ·  틀리면 1초 벌점')
    return True


# ================================================================== 13. 암산 대결 (타자)
def g13(P, ctx):
    NQ = 5
    m = MG(P, 13, ctx, status='문제 1/%d' % NQ, dim=120)
    panel(P, m.sc, '칠판', 0, 34, 400, 120, 'card')
    m.S('교수', ctx['BUST']['u1'], -170, 50, scale=0.4)
    qt = m.T('수식', '', 20, 44, 30, C_WHITE, F_NUM, False, 0, w=300, h=40)
    sub_ = m.T('수식안내', '', 20, 6, 10, C_DIM, F_BODY, True, 0, w=300, h=14)
    res = m.S('암산결과', [('o', K.big_text('정답!', 28, 'royal')), ('x', K.big_text('땡!', 28, 'red'))], 120, 80, visible=False)
    res.on(on_msg('채점'), ifelse(eq(V('_mv'), 1), [shape('o')], [shape('x')]), res.pct(130), show(),
           rep(5, res.grow_pct(-6), wait(0.02)), wait(0.5), hide())
    asker = m.S('질문', A.clear_dot(), 196, -60)
    gen = [
        ifelse(eq(V('문제'), 1), [setv('_ma', rnd(12, 49)), setv('_mb', rnd(11, 49)), setv('정답', add(V('_ma'), V('_mb'))),
                                 setv('미니표시', join('문제 1/', NQ)), setv('_mk', join(V('_ma'), ' + ', V('_mb'), ' = ?'))], []),
        ifelse(eq(V('문제'), 2), [setv('_ma', rnd(51, 98)), setv('_mb', rnd(12, 49)), setv('정답', sub(V('_ma'), V('_mb'))),
                                 setv('_mk', join(V('_ma'), ' − ', V('_mb'), ' = ?'))], []),
        ifelse(eq(V('문제'), 3), [setv('_ma', rnd(6, 9)), setv('_mb', rnd(6, 9)), setv('_mx', rnd(3, 9)),
                                 setv('정답', add(mul(V('_ma'), V('_mb')), V('_mx'))),
                                 setv('_mk', join(V('_ma'), ' × ', V('_mb'), ' + ', V('_mx'), ' = ?'))], []),
        ifelse(eq(V('문제'), 4), [setv('_ma', rnd(13, 29)), setv('_mb', rnd(3, 8)), setv('정답', mul(V('_ma'), V('_mb'))),
                                 setv('_mk', join(V('_ma'), ' × ', V('_mb'), ' = ?'))], []),
        ifelse(eq(V('문제'), 5), [setv('_ma', rnd(120, 480)), setv('_mb', rnd(35, 99)), setv('_mx', rnd(11, 60)),
                                 setv('정답', sub(add(V('_ma'), V('_mb')), V('_mx'))),
                                 setv('_mk', join(V('_ma'), ' + ', V('_mb'), ' − ', V('_mx'), ' = ?'))], []),
    ]
    asker.on(on_msg('게임시작'), setv('문제', 1),
             until(gt(V('문제'), NQ),
                   *gen, setv('미니표시', join('문제 ', V('문제'), '/', NQ)), cast('새수식'),
                   reset_timer(), start_timer(),
                   ask('답을 입력하고 Enter!'),
                   setv('_mt', timer()),
                   ifelse(eq(add(answer(), 0), V('정답')),
                          [setv('_mv', 1), chg('맞춤', 1), chg('합계', add(12, ifelse_num(V('_mt'))))],
                          [setv('_mv', 2)]),
                   cast('채점'), wait(0.9), chg('문제', 1)),
             *m.end_blocks(V('합계')))
    qt.on(on_msg('새수식'), write(V('_mk')))
    sub_.on(on_msg('새수식'), write('빠를수록 보너스! (문제당 최대 20점)'))
    sub_.on(on_msg('채점'), ifelse(eq(V('_mv'), 1), [write(join('정답! ', V('정답'), '  (', round1(V('_mt')), '초)'))],
                                 [write(join('정답은 ', V('정답')))]))
    m.on_start(setv('맞춤', 0), setv('합계', 0), setv('문제', 1))
    m.snd('채점', ifelse(eq(V('_mv'), 1), [play('good')], [play('bad')]))
    m.finish('홍익대 수학 교수님의 암산 대결!\n문제 5개, 답을 숫자로 입력하고 Enter.',
             '조작: 숫자 입력 + Enter  ·  빨리 맞힐수록 보너스')
    return True


def ifelse_num(t):
    """경과 시간 t초 → 속도 보너스 (0~8): max(0, 8 - t)."""
    return div(add(sub(8, t), abs_(sub(8, t))), 2)


# ================================================================== 14. 가위바위보
def g14(P, ctx):
    NR = 5
    m = MG(P, 14, ctx, status='1/%d판' % NR, dim=70)
    m.S('나', ctx['BUST']['me'], -168, 40, scale=0.55)
    m.S('상대', ctx['BUST']['u2'], 168, 40, scale=0.55)
    m.S('상대이름', K.badge('둘째 큰아버지 (응원단장)', 120, 18, 'purple'), 168, -14)
    hands = ['rock', 'paper', 'scissors']
    mine = m.S('내손', [(h_, A.rps_hand(h_, 'me')) for h_ in hands], -78, -36, scale=1.35)
    his = m.S('상대손', [(h_, A.rps_hand(h_, 'op')) for h_ in hands], 78, -36, scale=1.35)
    for o in (mine, his):
        o.on(on_msg('흔들기'), shape('rock'), rep(3, mvy(8), wait(0.08), mvy(-8), wait(0.08)))
    mine.on(on_msg('공개'), shape(V('내손')))
    his.on(on_msg('공개'), shape(V('상대손')), his.pct(115), wait(0.08), his.pct(100))
    hint = m.T('상대말', '', 120, 90, 10, C_WHITE, F_BODY, True, 0, w=200, h=30, bg=C_BOX)
    hint.on(on_msg('새판'), write(LGET('가위바위보힌트', V('힌트'))))
    chant = m.T('구호', '', 0, 20, 20, C_WHITE, F_NUM, False, 0, w=200, h=28)
    res = m.S('판결과', [('w', K.big_text('승리!', 30, 'royal')), ('d', K.big_text('비김', 26, 'white')), ('l', K.big_text('패배...', 28, 'red'))],
              0, 60, visible=False)
    res.on(on_msg('판정'), shape(V('_mv')), res.pct(130), show(), rep(5, res.grow_pct(-6), wait(0.02)), wait(0.6), hide())
    # 힌트: 1=주먹 낸다, 2=보 낸다, 3=가위 낸다 (60% 는 진짜)
    P.list('가위바위보힌트', ['이번엔... 주먹이 운다!', '보자기로 다 덮어 주지!', '가위로 싹둑 잘라 주마!'])
    pick_btns = [('바위 (1)', 1, -110), ('보 (2)', 2, 0), ('가위 (3)', 3, 110)]
    for lbl, v, x in pick_btns:
        act = [if_(and_(eq(V('대기'), 1), eq(V('게임중'), 1)), setv('내손', v), setv('대기', 0))]
        button(P, m.sc, '손버튼%d' % v, lbl, x, -108, 96, 26, ['royal', 'purple', 'red'][v - 1], actions=act)
        m.T('손키%d' % v, '', -300, -300, 8, visible=False).on(on_key(48 + v), *act)
    mgr = m.T('가위담당', '', -300, -300, 8, visible=False)
    mgr.on(on_msg('게임시작'), setv('라운드', 1), setv('상대손', rnd(1, 3)),
           until(gt(V('라운드'), NR),
                 setv('미니표시', join(V('라운드'), '/', NR, '판')),
                 # 상대가 낼 손 정하기: 힌트는 60% 진짜
                 setv('_mk', rnd(1, 3)),
                 setv('힌트', V('_mk')),
                 ifelse(le(rnd(1, 100), 60), [setv('_ma', V('_mk'))], [setv('_ma', rnd(1, 3))]),
                 cast('새판'), setv('대기', 1), setv('내손', 0),
                 wait_until(eq(V('대기'), 0)),
                 cast('흔들기'),
                 cast('구호1'), wait(0.25), cast('구호2'), wait(0.25), cast('구호3'), wait(0.2),
                 setv('상대손', V('_ma')), cast('공개'),
                 # 1바위 2보 3가위: 이기는 경우 (나,상대) = (1,3) (2,1) (3,2)
                 ifelse(eq(V('내손'), V('상대손')), [setv('_mv', 2), chg('비김', 1)],
                        [ifelse(or_(or_(and_(eq(V('내손'), 1), eq(V('상대손'), 3)), and_(eq(V('내손'), 2), eq(V('상대손'), 1))),
                                    and_(eq(V('내손'), 3), eq(V('상대손'), 2))),
                                [setv('_mv', 1), chg('맞춤', 1)], [setv('_mv', 3)])]),
                 cast('판정'), wait(1.2), chg('라운드', 1)),
           *m.end_blocks(add(mul(V('맞춤'), 20), mul(V('비김'), 8))))
    chant.on(on_msg('구호1'), write('가위!'))
    chant.on(on_msg('구호2'), write('바위!'))
    chant.on(on_msg('구호3'), write('보!'))
    chant.on(on_msg('새판'), write(''))
    m.on_start(setv('맞춤', 0), setv('비김', 0), setv('대기', 0), setv('내손', 1), setv('상대손', 1))
    m.snd('공개', play('hit'))
    m.snd('판정', ifelse(eq(V('_mv'), 1), [play('good')], [if_(eq(V('_mv'), 3), play('bad'))]))
    m.finish('응원단장 둘째 큰아버지와 가위바위보 5판!\n상대의 말은 60%만 진짜... 심리전으로 이기세요!',
             '조작: 버튼 클릭 또는 1 바위 · 2 보 · 3 가위  (이기면 20, 비기면 8점)')
    return True


# ================================================================== 15. 낚시
def g15(P, ctx):
    m = MG(P, 15, ctx, time_limit=30, status='잡은 물고기 0')
    GX, GH = 150, 200
    m.S('게이지', A.fish_gauge(GH), GX, 0)
    bar = m.S('낚시바', [('n', A.catch_bar(52)), ('a', A.catch_bar(52, True))], GX, -70)
    fish = m.S('물고기', A.fish_icon(), GX, 0)
    prog = m.S('진행막대', K.bar_set('fish_prog', 180, 10, 'royal'), GX + 34, 0)
    prog.on(on_scene(), rot(-90))
    prog.on(on_msg('게임시작'), until(eq(V('게임중'), 0), shape(add(floor(mul(div(V('진행도'), 100), 40)), 1)), wait(0.03)))
    bob = m.S('찌', A.bobber(), -60, -40)
    bob.on(on_scene(), forever(rep(12, mvy(0.4), wait(0.05)), rep(12, mvy(-0.4), wait(0.05))))
    bob.on(on_msg('입질'), rep(4, mvy(-5), wait(0.03), mvy(5), wait(0.03)))
    LO, HI = -GH / 2 + 30, GH / 2 - 30
    bar.on(on_msg('게임시작'), setv('바y', -60), setv('바속도', 0),
           until(eq(V('게임중'), 0),
                 ifelse(key(K_SPACE), [chg('바속도', 0.34)], [chg('바속도', -0.3)]),
                 *clamp_blocks('바속도', -4, 4),
                 chg('바y', V('바속도')),
                 if_(lt(V('바y'), LO), setv('바y', LO), setv('바속도', mul(V('바속도'), -0.3))),
                 if_(gt(V('바y'), HI), setv('바y', HI), setv('바속도', 0)),
                 ly(V('바y')),
                 ifelse(lt(abs_(sub(V('물고기y'), V('바y'))), 27), [shape('a'), chg('진행도', 0.6)], [shape('n'), chg('진행도', -0.32)]),
                 if_(ge(V('진행도'), 100), chg('잡은수', 1), setv('진행도', 30), setv('미니표시', join('잡은 물고기 ', V('잡은수'))),
                     cast('월척')),
                 if_(le(V('진행도'), 0), chg('놓침', 1), setv('진행도', 30), cast('놓침'))))
    fish.on(on_msg('게임시작'), setv('물고기y', 0), setv('목표y', 0), setv('_mk', 0),
            until(eq(V('게임중'), 0),
                  chg('_mk', 1),
                  if_(gt(V('_mk'), rnd(25, 60)), setv('_mk', 0), setv('목표y', rnd(LO, HI)), cast('입질')),
                  chg('물고기y', mul(sub(V('목표y'), V('물고기y')), add(0.024, mul(V('잡은수'), 0.01)))),
                  ly(add(V('물고기y'), mul(sin_(mul(V('_mk'), 25)), 3)))))
    big = m.S('월척', K.big_text('월척!', 30, 'royal'), -40, 40, visible=False)
    big.on(on_msg('월척'), big.pct(130), show(), rep(5, big.grow_pct(-6), wait(0.02)), wait(0.6), hide())
    miss = m.S('놓침', K.big_text('놓쳤다...', 22, 'red'), -40, 40, visible=False)
    miss.on(on_msg('놓침'), show(), wait(0.6), hide())
    mgr = m.T('낚시담당', '', -300, -300, 8, visible=False)
    mgr.on(on_msg('시간끝'), *m.end_blocks(add(mul(V('잡은수'), 30), mul(V('진행도'), 0.1))))
    m.on_start(setv('진행도', 30), setv('잡은수', 0), setv('놓침', 0), setv('바y', -60), setv('물고기y', 0))
    m.snd('월척', play('splash'))
    m.snd('놓침', play('bad'))
    m.finish('신안저수지 낚시 대회! 파란 막대를 물고기에 겹쳐\n오른쪽 게이지를 가득 채우면 한 마리!',
             '조작: SPACE 를 누르고 있으면 막대가 올라가요 (떼면 내려감)')
    return True


GAMES = {1: g01, 2: g02, 3: g03, 4: g04, 5: g05, 6: g06, 7: g07, 8: g08, 9: g09, 10: g10, 11: g11, 12: g12, 13: g13,
         14: g14, 15: g15}


def build_minigame(P, idx, ctx):
    f = GAMES.get(idx)
    return bool(f and f(P, ctx))
