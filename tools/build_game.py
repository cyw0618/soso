# -*- coding: utf-8 -*-
"""'군수집 막내아들' 엔트리 게임 빌드 스크립트.

    python3 tools/build_game.py            → 저장소 루트에 군수집_막내아들.ent 생성
    python3 tools/build_game.py --dev DIR  → 테스트용으로 풀어놓은 temp/ 도 DIR 에 생성
"""
import os
import sys
import json
from PIL import Image, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('FONT_DIR', os.path.join(HERE, 'fonts'))

from entrygen import *
import ui_kit as K
import sprites as SP
import gui as G
from gui import text, sprite, panel, button, go, hud, round1, fmt_comma, F_BODY, F_NUM
import data as D
from art_common import save, ensure_out, OUT

P = Project('군수집 막내아들')

# ------------------------------------------------------------------ 장면 이름
S_TITLE, S_STORY, S_HOWTO, S_MAP = '타이틀', '이야기', '게임 방법', '조치원 지도'
S_GAME = ['%02d %s' % (p['id'], p['short']) for p in D.PLACES]
S_RESULT, S_EVENT, S_SHOP, S_STOCK = '유세 결과', '돌발상황', '작전 본부', '주식'
S_VOTE, S_RANK, S_BANKRUPT = '개표', '랭킹', '파산'
for s in [S_TITLE, S_STORY, S_HOWTO, S_MAP] + S_GAME + [S_RESULT, S_EVENT, S_SHOP, S_STOCK, S_VOTE, S_RANK, S_BANKRUPT]:
    P.scene(s)

# ------------------------------------------------------------------ 변수/리스트
VARS = dict(돈=1000, 내지지율=12, 큰A=44, 큰B=44, 유세횟수=0, 현재지역=0, 점수=0, 방어권=0, 차단턴=0,
            획득지지=0, 반격A=0, 반격B=0, 획득재화=0, 등급=0, 선택=0, 이벤트=0, 남은시간=0, i=0, j=0, k=0,
            tmp=0, tmp2=0, 호버지역=0, 페이지=1, 타자중=0, 최종점수=0, 당선=0, 총자산=0, 선택종목=1,
            콤보=0, 판정=0, 결과처리됨=0, 돈표시='', _n=0, _hi=0, _lo=0, _mid=0, _p3='', _m3='', 표시글='',
            다음장면=0, 게임중=0, 카운트=0, 목표=0, 맞춤=0, 틀림=0, 진행=0, 플레이어이름='')
for k_, v_ in VARS.items():
    P.var(k_, v_)

P.list('지역완료', [0] * 15)
P.list('지역점수', [0] * 15)
P.list('지역이름', [p['name'] for p in D.PLACES])
P.list('지역게임', [p['game'] for p in D.PLACES])
P.list('지역설명', [p['help'] for p in D.PLACES])
P.list('지역비중', [p['weight'] for p in D.PLACES])
P.list('이야기', D.INTRO_STORY)
P.list('랭킹이름', [n for n, s in D.SEED_RANK] + ['-'] * (10 - len(D.SEED_RANK)) + ['끝'])
P.list('랭킹점수', [s for n, s in D.SEED_RANK] + [0] * (10 - len(D.SEED_RANK)) + [-1])

# ------------------------------------------------------------------ 공통 그림
ensure_out()
import make_title
import make_places
from make_cover import build_cover

print('· 표지/배경 그림 만드는 중...')
COVER = build_cover()
TITLE_BG = make_title.title_bg(COVER)
save(TITLE_BG, 'title_bg')
story = ImageEnhance.Brightness(TITLE_BG.filter(ImageFilter.GaussianBlur(10))).enhance(0.42)
save(story, 'story_bg')
PIN_POS, DT_CIRCLE, INSET_POS, INSET_SIZE = make_places.build_all()
ART = lambda n: os.path.join(OUT, n + '.png')
BLACK = SP.plain(480, 270, (0, 0, 0, 255), 'black_full')
DIM = SP.plain(480, 270, (4, 8, 24, 150), 'dim_full')
PORT = {k: K.portrait_ring(SP.portrait_crop(COVER, k), 24, {'me': 'gold', 'gp': 'white', 'u1': 'red', 'u2': 'purple'}[k], name=k)
        for k in ('me', 'gp', 'u1', 'u2')}
BUST = {k: SP.bust(COVER, k) for k in ('gp', 'me', 'u1', 'u2')}
PLACE_PICS = [('%02d' % i, ART('place_%02d' % i)) for i in range(1, 16)]
CONF = [('c%d' % i, K.confetti(i, 8)) for i in range(6)]
SPARK = K.sparkle(16)


def art2stage(x, y):
    return x / 2 - 240, 135 - y / 2


# ================================================================== 타이틀
def scene_title():
    sc = S_TITLE
    G.bg(P, sc, ART('title_bg'))
    # 초기화 담당 (보이지 않는 오브젝트)
    mgr = text(P, sc, '초기화담당', '', -300, -300, 8, visible=False)
    init = [setv(k_, v_) for k_, v_ in VARS.items() if k_ not in ('돈표시', '_p3', '_m3', '표시글', '플레이어이름')]
    init += [setv('i', 1), rep(15, lst_set('지역완료', V('i'), 0), lst_set('지역점수', V('i'), 0), chg('i', 1))]
    init += STOCK_RESET
    mgr.on(on_msg('초기화'), *init)
    for lbl, yy, col, ic, act in [('게임 시작', 34, 'gold', 'star', [cast_wait('초기화')] + go(S_STORY)),
                                  ('게임 방법', -6, 'blue', 'map', go(S_HOWTO)),
                                  ('랭킹', -46, 'purple', 'trophy', go(S_RANK))]:
        button(P, sc, '버튼' + lbl, lbl, 170, yy, 120, 32, col, icon=ic, actions=act, first_scene=True)
    G.fader(P, sc, BLACK, first_scene=True)


# ================================================================== 이야기 (대화)
SPEAKERS = [('gp', '할아버지'), ('me', '나')]


def scene_story():
    sc = S_STORY
    G.bg(P, sc, ART('story_bg'))
    port = sprite(P, sc, '화자', [(k, BUST[k]) for k in ('gp', 'me', 'u1', 'u2')], -150, 18, scale=1.05)
    u1 = sprite(P, sc, '큰아버지1', BUST['u1'], 120, 30, scale=0.8, visible=False)
    u2 = sprite(P, sc, '큰아버지2', BUST['u2'], 200, 30, scale=0.8, visible=False)
    panel(P, sc, '대화창', 20, -82, 420, 96, 'glass')
    nametag = sprite(P, sc, '이름표', [(nm, K.badge(nm, 64, 18, 'gold')) for _, nm in SPEAKERS],
                     -150, -32)
    body = text(P, sc, '대사', '', 26, -86, 13, '#FFFFFF', F_BODY, True, 1, w=380, h=72)
    nxt = sprite(P, sc, '다음표시', K.icon_img('back', 14), 212, -118, visible=False)
    nxt.on(on_scene(), rot(180), forever(if_(eq(V('타자중'), 0), show()), if_(eq(V('타자중'), 1), hide()),
                                       mvx(1), wait(0.12), mvx(-1), wait(0.12)))
    # 페이지 표시
    def page_blocks():
        return [
            setv('타자중', 1),
            cast('화자변경'),
            setv('표시글', ''), setv('i', 1),
            until(or_(gt(V('i'), slen(LGET('이야기', V('페이지')))), eq(V('타자중'), 0)),
                  setv('표시글', join(V('표시글'), char_at(LGET('이야기', V('페이지')), V('i')))),
                  write(V('표시글')), chg('i', 1), wait(0.025)),
            write(LGET('이야기', V('페이지'))), setv('타자중', 0)]
    body.on(on_scene(), setv('페이지', 1), *page_blocks())
    body.on(on_msg('다음페이지'), *page_blocks())
    # 화자 사진/이름 바꾸기
    sp_map = {i_ + 1: k_ for i_, k_ in enumerate(D.STORY_SPEAKER)}
    port.on(on_msg('화자변경'),
            *[if_(eq(V('페이지'), pg), shape(k)) for pg, k in sp_map.items()],
            port.pct(96), fx('transparency', 40), rep(5, port.grow_pct(0.8), fx_add('transparency', -8), wait(0.02)))
    port.on(on_scene(), forever(rep(30, mvy(0.1), wait(0.03)), rep(30, mvy(-0.1), wait(0.03))))
    nametag.on(on_msg('화자변경'), *[if_(eq(V('페이지'), pg), shape('나' if k == 'me' else '할아버지')) for pg, k in sp_map.items()])
    for o in (u1, u2):
        o.on(on_msg('화자변경'), ifelse(eq(V('페이지'), 2), [show()], [hide()]))
    # 클릭 진행
    adv = [ifelse(eq(V('타자중'), 1), [setv('타자중', 0)],
                  [ifelse(lt(V('페이지'), len(D.INTRO_STORY)), [chg('페이지', 1), cast('다음페이지')], go(S_MAP))])]
    body.on(on_mouse_down(), *adv)
    body.on(on_key(K_SPACE), *adv)
    button(P, sc, '건너뛰기', '건너뛰기', 200, 116, 70, 24, 'gray', actions=go(S_MAP))
    G.fader(P, sc, BLACK)


# ================================================================== 게임 방법
def scene_howto():
    sc = S_HOWTO
    G.bg(P, sc, ART('story_bg'))
    panel(P, sc, '방법판', 0, -6, 440, 228, 'glass', header='gold')
    sprite(P, sc, '방법제목', K.banner('게임 방법', 180, 34, 'gold'), 0, 112)
    rows = [('map', '지도의 핀 15곳을 눌러 선거유세! 지역마다 단 한 번뿐.'),
            ('star', '지역마다 종목이 다른 미니게임. 잘할수록 지지율과 재화 UP'),
            ('bolt', '유세 뒤 돌발상황! 잘 대처하면 이익, 실패하면 크기만큼 손해'),
            ('shop', '작전 본부에서 재화로 사건을 만들거나 위기를 막을 수 있어요'),
            ('chart', '주식으로 선거자금을 불려요. 재산이 0원이 되면 파산!'),
            ('ballot', '15곳을 다 돌면 개표! 두 큰아버지보다 지지율이 높으면 당선')]
    for i, (ic, t) in enumerate(rows):
        yy = 66 - i * 30
        sprite(P, sc, '방법아이콘%d' % i, K.icon_img(ic, 22), -192, yy)
        text(P, sc, '방법글%d' % i, t, 14, yy, 12, '#FFFFFF', F_BODY, True, 1, w=370, h=22)
    button(P, sc, '돌아가기', '돌아가기', 0, -118, 110, 28, 'blue', icon='back', actions=go(S_TITLE))
    G.fader(P, sc, BLACK)


# ================================================================== 지도
def scene_map():
    sc = S_MAP
    G.bg(P, sc, ART('map_bg'))
    # 시내 확대 창
    ix, iy = 960 - INSET_SIZE[0] - 10, 160
    icx, icy = art2stage(ix + INSET_SIZE[0] / 2, iy + INSET_SIZE[1] / 2)
    sprite(P, sc, '시내확대', ART('map_inset'), icx, icy)
    sprite(P, sc, '시내제목', K.badge('조치원 시내 확대', 92, 18, 'gold'), icx, icy + INSET_SIZE[1] / 4 + 4)
    # 핀 위치(무대 좌표)
    pin_xy = {}
    for k_ in range(1, 16):
        if k_ in INSET_POS:
            ax, ay = ix + INSET_POS[k_][0], iy + INSET_POS[k_][1]
        else:
            ax, ay = PIN_POS[k_]
        sx, sy = art2stage(ax, ay)
        pin_xy[k_] = (sx, sy + 15)         # 화살표 끝이 장소를 가리키도록
    P.list('핀X', [round(pin_xy[k_][0], 1) for k_ in range(1, 16)])
    P.list('핀Y', [round(pin_xy[k_][1], 1) for k_ in range(1, 16)])
    # 장소 이름표 (유세를 마치면 숨김)
    for k_ in range(1, 16):
        x_, y_ = pin_xy[k_]
        nm = D.PLACES[k_ - 1]['short']
        lb = text(P, sc, '이름표%02d' % k_, nm, x_, y_ - 21, 8, '#FFFFFF', F_BODY, True, 0, w=max(36, len(nm) * 9), h=12,
                  bg='#16224d')
        lb.on(on_scene(), forever(ifelse(eq(LGET('지역완료', k_), 1), [hide()], [show()]), wait(0.1)))
    # 화살표 (유세를 마치면 사라짐)
    for k_ in range(1, 16):
        x_, y_ = pin_xy[k_]
        pics = [('on', SP.arrow_marker(k_, 'on')), ('hot', SP.arrow_marker(k_, 'hot'))]
        o = sprite(P, sc, '화살표%02d' % k_, pics, x_, y_)
        o.on(on_scene(), xy(x_, y_),
             forever(ifelse(eq(LGET('지역완료', k_), 1), [hide(), if_(eq(V('호버지역'), k_), setv('호버지역', 0))],
                            [show(), ifelse(touch('mouse'), [shape('hot'), o.pct(125), setv('호버지역', k_)],
                                            [shape('on'), o.pct(100), if_(eq(V('호버지역'), k_), setv('호버지역', 0))])]),
                     wait(0.03)))
        o.on(on_scene(), forever(rep(8, mvy(0.6), wait(0.03)), rep(8, mvy(-0.6), wait(0.03)), wait(0.05)))
        o.on(on_click(), if_(eq(LGET('지역완료', k_), 0), setv('현재지역', k_), *go(S_GAME[k_ - 1])))
    # 툴팁
    tip = panel(P, sc, '툴팁판', 0, 0, 150, 52, 'card', visible=False)
    tip_t = text(P, sc, '툴팁제목', '', 0, 0, 11, '#FFE27A', F_NUM, False, 0, w=140, h=16, visible=False)
    tip_d = text(P, sc, '툴팁설명', '', 0, 0, 9, '#FFFFFF', F_BODY, True, 0, w=140, h=26, visible=False)
    for o, dy in ((tip, 0), (tip_t, 12), (tip_d, -8)):
        o.on(on_scene(), forever(
            ifelse(gt(V('호버지역'), 0),
                   [setv('tmp', LGET('핀X', V('호버지역'))),
                    if_(gt(V('tmp'), 150), setv('tmp', 150)), if_(lt(V('tmp'), -150), setv('tmp', -150)),
                    setv('tmp2', add(LGET('핀Y', V('호버지역')), 40)),
                    if_(gt(V('tmp2'), 70), setv('tmp2', sub(LGET('핀Y', V('호버지역')), 44))),
                    xy(V('tmp'), add(V('tmp2'), dy)), show()],
                   [hide()]),
            wait(0.03)))
    tip_t.on(on_scene(), forever(if_(gt(V('호버지역'), 0), write(join(LGET('지역이름', V('호버지역')), ' · ', LGET('지역게임', V('호버지역'))))), wait(0.05)))
    tip_d.on(on_scene(), forever(if_(gt(V('호버지역'), 0),
                                     ifelse(eq(LGET('지역완료', V('호버지역')), 1),
                                            [write(join('유세 완료! 점수 ', LGET('지역점수', V('호버지역')), '점'))],
                                            [write(LGET('지역설명', V('호버지역')))])), wait(0.05)))
    # 아래 버튼
    button(P, sc, '주식버튼', '주식 투자', -184, -116, 96, 28, 'blue', icon='chart', actions=go(S_STOCK))
    button(P, sc, '작전버튼', '작전 본부', -82, -116, 96, 28, 'purple', icon='bolt', actions=go(S_SHOP))
    sprite(P, sc, '지도안내', K.badge('핀을 눌러 유세 시작!', 120, 20, 'navy'), 60, -118)
    hud(P, sc, PORT)
    # 모든 지역을 돌았으면 개표로
    chk = text(P, sc, '진행검사', '', -300, -300, 8, visible=False)
    chk.on(on_scene(), wait(0.4), if_(ge(V('유세횟수'), 15), *go(S_VOTE)), if_(le(V('돈'), 0), *go(S_BANKRUPT)))
    G.fader(P, sc, BLACK)


# ================================================================== 유세 결과
def scene_result():
    sc = S_RESULT
    bgo = G.bg(P, sc, PLACE_PICS)
    bgo.on(on_scene(), shape(V('현재지역')))
    sprite(P, sc, '어둡게', DIM, 0, 0)
    panel(P, sc, '결과판', 40, -8, 300, 214, 'glass', header='gold')
    sprite(P, sc, '결과제목', K.banner('유세 결과', 170, 34, 'gold'), 40, 106)
    place = text(P, sc, '결과장소', '', 40, 74, 13, '#FFFFFF', F_NUM, False, 0, w=300, h=20)
    place.on(on_scene(), write(join(LGET('지역이름', V('현재지역')), ' · ', LGET('지역게임', V('현재지역')))))
    score = text(P, sc, '결과점수', '0', 0, 36, 34, '#FFE27A', F_NUM, False, 0, w=140, h=44)
    text(P, sc, '점수단위', '점', 80, 30, 14, '#FFE27A', F_NUM, False, 1, w=30, h=20)
    stamp = sprite(P, sc, '등급도장', [(g, SP.grade_stamp(g)) for g in 'SABCD'], 150, 38, visible=False)
    rows = []
    labels = [('star', '지지율', '#7CF29A'), ('bolt', '큰아버지 반격', '#FF8C96'), ('coin', '재화', '#FFE27A')]
    for i, (ic, lb, col) in enumerate(labels):
        yy = -6 - i * 24
        sprite(P, sc, '결과아이콘%d' % i, K.icon_img(ic, 16), -88, yy)
        text(P, sc, '결과라벨%d' % i, lb, -26, yy, 12, '#DDE6FF', F_BODY, True, 1, w=100, h=18)
        rows.append(text(P, sc, '결과값%d' % i, '', 110, yy, 13, col, F_NUM, False, 2, w=150, h=18, visible=False))
    nxt = button(P, sc, '다음버튼', '다음', 40, -100, 100, 28, 'gold', icon='star', visible=False,
                 actions=[if_(le(V('돈'), 0), *go(S_BANKRUPT)),
                          if_(ge(V('유세횟수'), 15), *go(S_VOTE)),
                          ifelse(le(rnd(1, 100), 70), go(S_EVENT), go(S_MAP))])
    # ---- 계산 (한 번만)
    calc = text(P, sc, '결과계산', '', -300, -300, 8, visible=False)
    w = LGET('지역비중', V('현재지역'))
    calc.on(on_scene(),
            if_(eq(V('결과처리됨'), 0),
                setv('결과처리됨', 1),
                lst_set('지역완료', V('현재지역'), 1), lst_set('지역점수', V('현재지역'), V('점수')), chg('유세횟수', 1),
                # 지지율 얻기 (큰아버지 둘에게서 비율대로 가져옴)
                setv('획득지지', round1(div(mul(V('점수'), w), 100))),
                setv('tmp', div(V('큰A'), add(V('큰A'), V('큰B')))),
                chg('큰A', mul(mul(V('획득지지'), V('tmp')), -1)),
                chg('큰B', mul(mul(V('획득지지'), sub(1, V('tmp'))), -1)),
                chg('내지지율', V('획득지지')),
                # 큰아버지들의 반격
                ifelse(gt(V('차단턴'), 0), [setv('반격A', 0), setv('반격B', 0), chg('차단턴', -1)],
                       [setv('반격A', div(rnd(3, 11), 10)), setv('반격B', div(rnd(3, 11), 10))]),
                if_(lt(V('내지지율'), add(add(V('반격A'), V('반격B')), 2)), setv('반격A', 0), setv('반격B', 0)),
                chg('내지지율', mul(add(V('반격A'), V('반격B')), -1)), chg('큰A', V('반격A')), chg('큰B', V('반격B')),
                setv('내지지율', round1(V('내지지율'))), setv('큰A', round1(V('큰A'))),
                setv('큰B', round1(sub(sub(100, V('내지지율')), V('큰A')))),
                # 재화
                setv('획득재화', rounded(mul(V('점수'), 2.5))), if_(ge(V('점수'), 80), chg('획득재화', 60)),
                chg('돈', V('획득재화')),
                cast_wait('주가변동')))
    # 점수 올라가는 연출
    score.on(on_scene(), setv('카운트', 0), write('0'), wait(0.4),
             until(ge(V('카운트'), V('점수')), chg('카운트', add(1, floor(div(V('점수'), 30)))),
                   if_(gt(V('카운트'), V('점수')), setv('카운트', V('점수'))), write(V('카운트')), wait(0.02)),
             write(V('점수')), cast('도장'))
    stamp.on(on_msg('도장'),
             ifelse(ge(V('점수'), 90), [shape('S')], [ifelse(ge(V('점수'), 75), [shape('A')], [
                 ifelse(ge(V('점수'), 55), [shape('B')], [ifelse(ge(V('점수'), 35), [shape('C')], [shape('D')])])])]),
             stamp.pct(260), fx('transparency', 0), show(), rep(8, stamp.grow_pct(-20), wait(0.016)),
             if_(ge(V('점수'), 80), cast('축하')),
             wait(0.2), cast('결과줄'))
    rows[0].on(on_msg('결과줄'), write(join('+', V('획득지지'), '%p')), show())
    rows[1].on(on_msg('결과줄'), wait(0.25), write(join('-', round1(add(V('반격A'), V('반격B'))), '%p')), show())
    rows[2].on(on_msg('결과줄'), wait(0.5), *fmt_comma(V('획득재화'), '표시글'), write(join('+', V('표시글'), '만원')), show())
    nxt.on(on_msg('결과줄'), wait(0.9), show())
    # 할아버지 한마디
    gp = sprite(P, sc, '할아버지', BUST['gp'], -200, -40, scale=0.62, visible=False)
    bub = panel(P, sc, '말풍선', -178, 46, 116, 50, 'light', visible=False)
    say_t = text(P, sc, '한마디', '', -178, 46, 10, '#2A1E3A', F_BODY, True, 0, w=104, h=40, visible=False)
    for o in (gp, bub, say_t):
        o.on(on_msg('결과줄'), wait(0.6), show())
    say_t.on(on_msg('결과줄'),
             ifelse(ge(V('점수'), 90), [write(D.GP_GRADE['S'])], [ifelse(ge(V('점수'), 75), [write(D.GP_GRADE['A'])], [
                 ifelse(ge(V('점수'), 55), [write(D.GP_GRADE['B'])], [ifelse(ge(V('점수'), 35), [write(D.GP_GRADE['C'])], [write(D.GP_GRADE['D'])])])])]))
    G.confetti(P, sc, '축하', CONF)
    hud(P, sc, PORT)
    G.fader(P, sc, BLACK)
    # 주가 변동 담당
    stock_updater(sc)


# ================================================================== 주식 데이터
STOCK_RESET = []
P.list('주식이름', [s[0] for s in D.STOCKS])
P.list('주가', [s[1] for s in D.STOCKS])
P.list('전주가', [s[1] for s in D.STOCKS])
P.list('변동폭', [s[2] for s in D.STOCKS])
P.list('보유', [0] * 5)
P.list('평단', [0] * 5)
P.list('주가기록', [s[1] for s in D.STOCKS for _ in range(12)])
for i_, (nm, pr, vol) in enumerate(D.STOCKS, 1):
    STOCK_RESET += [lst_set('주가', i_, pr), lst_set('전주가', i_, pr), lst_set('보유', i_, 0), lst_set('평단', i_, 0)]
STOCK_RESET += [setv('i', 1), rep(5, setv('j', 1), rep(12, lst_set('주가기록', add(mul(sub(V('i'), 1), 12), V('j')), LGET('주가', V('i'))), chg('j', 1)), chg('i', 1))]
P.var('뉴스', '')


def stock_updater(sc):
    o = text(P, sc, '주가담당', '', -300, -300, 8, visible=False)
    o.on(on_msg('주가변동'),
         setv('i', 1),
         rep(5,
             lst_set('전주가', V('i'), LGET('주가', V('i'))),
             setv('tmp', div(rnd(mul(LGET('변동폭', V('i')), -10), mul(LGET('변동폭', V('i')), 11)), 1000)),
             # 가끔 큰 뉴스 (급등/급락)
             if_(le(rnd(1, 100), 8), setv('tmp', mul(V('tmp'), 3))),
             lst_set('주가', V('i'), round1(mul(LGET('주가', V('i')), add(1, V('tmp'))))),
             if_(lt(LGET('주가', V('i')), 0.5), lst_set('주가', V('i'), 0.5)),
             # 기록 한 칸씩 밀기
             setv('j', 1),
             rep(11, lst_set('주가기록', add(mul(sub(V('i'), 1), 12), V('j')), LGET('주가기록', add(add(mul(sub(V('i'), 1), 12), V('j')), 1))), chg('j', 1)),
             lst_set('주가기록', mul(V('i'), 12), LGET('주가', V('i'))),
             chg('i', 1)))


# ================================================================== 미니게임 (임시: 나중에 교체)
def scene_minigame_stub(idx):
    sc = S_GAME[idx - 1]
    p = D.PLACES[idx - 1]
    G.bg(P, sc, ART('place_%02d' % idx))
    sprite(P, sc, '장소배너', K.banner('%s · %s' % (p['name'], p['game']), 230, 34, 'gold'), -110, 112)
    t = text(P, sc, '임시', '미니게임 준비 중 (클릭하면 점수)', 0, 0, 14, '#FFFFFF', F_BODY, True, 0, w=300, h=30, bg='#16224d')
    t.on(on_click(), setv('점수', rnd(40, 100)), setv('결과처리됨', 0), *go(S_RESULT))
    G.fader(P, sc, BLACK)


def build(dev_dir=None, out=None):
    scene_title()
    scene_story()
    scene_howto()
    scene_map()
    import minigames
    for i in range(1, 16):
        if not minigames.build_minigame(P, i, globals()):
            scene_minigame_stub(i)
    scene_result()
    import scenes_more
    scenes_more.build_all(P, globals())
    out = out or os.path.join(HERE, '..', '군수집_막내아들.ent')
    proj = P.write_ent(out, dev_dir=dev_dir)
    return proj


if __name__ == '__main__':
    dev = None
    if '--dev' in sys.argv:
        dev = sys.argv[sys.argv.index('--dev') + 1]
    proj = build(dev)
    if dev:
        json.dump(proj, open(os.path.join(dev, 'project.json'), 'w'), ensure_ascii=False)
    n_blocks = sum(o['script'].count('"type"') for o in proj['objects'])
    print('완료: 장면 %d, 오브젝트 %d, 블록 약 %d개' % (len(proj['scenes']), len(proj['objects']), n_blocks))
