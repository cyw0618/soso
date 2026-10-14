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
from gui import text, sprite, panel, button, go, hud, round1, fmt_comma, fmt_money, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
import data as D
from art_common import save, ensure_out, OUT

P = Project('군수집 막내아들')

# ------------------------------------------------------------------ 장면 이름
S_TITLE, S_STORY, S_HOWTO, S_MAP = '타이틀', '이야기', '게임 방법', '조치원 지도'
S_GAME = ['%02d %s' % (p['id'], p['short']) for p in D.PLACES]
S_RESULT, S_EVENT, S_SHOP, S_STOCK = '유세 결과', '돌발상황', '작전 본부', '주식'
S_VOTE, S_RANK, S_BANKRUPT, S_CONTROL = '개표', '랭킹', '파산', '조치원 장악'
S_GROUP, S_NEGO = '계열사', '협상 테이블'
for s in [S_TITLE, S_STORY, S_HOWTO, S_MAP] + S_GAME + [S_RESULT, S_EVENT, S_SHOP, S_STOCK, S_GROUP, S_NEGO, S_VOTE,
                                                         S_CONTROL, S_RANK, S_BANKRUPT]:
    P.scene(s)

# ------------------------------------------------------------------ 변수/리스트
VARS = dict(돈=D.START_MONEY, 내지지율=12, 큰A=44, 큰B=44, 유세횟수=0, 현재지역=0, 점수=0, 방어권=0, 차단턴=0,
            획득지지=0, 반격A=0, 반격B=0, 획득재화=0, 등급=0, 선택=0, 이벤트=0, 남은시간=0, i=0, j=0, k=0,
            tmp=0, tmp2=0, 호버지역=0, 지도모드=0, 개표창=0, 페이지=1, 타자중=0, 최종점수=0, 당선=0, 총자산=0, 선택종목=1,
            콤보=0, 판정=0, 결과처리됨=0, 돈표시='', _n=0, _hi=0, _lo=0, _mid=0, _p3='', _m3='', 표시글='',
            다음장면=0, 게임중=0, 카운트=0, 목표=0, 맞춤=0, 틀림=0, 진행=0, 플레이어이름='')
P.var('내순위', 0)
P.var('방금등록', 0)
P.var('랭킹쪽', 1)
import scene_stock as ST
import empire as E
VARS.update(ST.STOCK_VARS)
VARS.update(E.EMPIRE_VARS)
for k_, v_ in VARS.items():
    P.var(k_, v_)

N_PL = D.N_PLACES
P.list('지역완료', [0] * N_PL)
P.list('지역점수', [0] * N_PL)
P.list('지역이름', [p['name'] for p in D.PLACES])
P.list('지역게임', [p['game'] for p in D.PLACES])
P.list('지역설명', [p['help'] for p in D.PLACES])
P.list('지역비중', [p['weight'] for p in D.PLACES])
P.list('이야기', D.INTRO_STORY)
# 랭킹: 공유 리스트(작품을 공유하면 모든 플레이어의 기록이 계속 쌓임). 처음에는 비어 있고 끝에 표시용 항목('끝', -1)만 있다.
P.list('랭킹이름', ['끝'], cloud=True, lid='rk2n')
P.list('랭킹점수', [-1], cloud=True, lid='rk2s')

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
PIN_POS, DT_CIRCLE = make_places.build_all()
DT_IDS = make_places.DOWNTOWN_IDS
ART = lambda n: os.path.join(OUT, n + '.png')
BLACK = SP.plain(480, 270, (0, 0, 0, 255), 'black_full')
DIM = SP.plain(480, 270, (4, 8, 24, 150), 'dim_full')
PORT = {k: K.portrait_ring(SP.portrait_crop(COVER, k), 24, {'me': 'royal', 'gp': 'silver', 'u1': 'red', 'u2': 'purple'}[k], name=k)
        for k in ('me', 'gp', 'u1', 'u2')}
BUST = {k: SP.bust(COVER, k) for k in ('gp', 'me', 'u1', 'u2')}
PLACE_PICS = [('%02d' % i, ART('place_%02d' % i)) for i in range(1, D.N_PLACES + 1)]
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
    init = [setv(k_, v_) for k_, v_ in VARS.items() if k_ not in ('돈표시', '_p3', '_m3', '표시글', '플레이어이름', '_q', '_m')]
    init += [setv('i', 1), rep(N_PL, lst_set('지역완료', V('i'), 0), lst_set('지역점수', V('i'), 0), chg('i', 1))]
    init += STOCK_RESET
    init += E.reset_blocks()
    mgr.on(on_msg('초기화'), *init)
    for lbl, yy, col, ic, act in [('게임 시작', 34, 'royal', 'star', [cast_wait('초기화')] + go(S_STORY)),
                                  ('게임 방법', -6, 'blue', 'map', go(S_HOWTO)),
                                  ('랭킹', -46, 'purple', 'trophy', go(S_RANK))]:
        button(P, sc, '버튼' + lbl, lbl, 170, yy, 120, 32, col, icon=ic, actions=act, first_scene=True)
    G.sound_hub(P, sc, 'bgm_title', first_scene=True)
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
    nametag = sprite(P, sc, '이름표', [(nm, K.badge(nm, 64, 18, 'royal')) for _, nm in SPEAKERS],
                     -150, -32)
    body = text(P, sc, '대사', '', 26, -84, 13, '#FFFFFF', F_BODY, True, 1, w=380, h=80)
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
    G.sound_hub(P, sc, 'bgm_title')
    G.fader(P, sc, BLACK)


# ================================================================== 게임 방법
def scene_howto():
    sc = S_HOWTO
    G.bg(P, sc, ART('story_bg'))
    panel(P, sc, '방법판', 0, -6, 440, 228, 'glass', header='royal')
    sprite(P, sc, '방법제목', K.banner('게임 방법', 180, 34, 'royal'), 0, 112)
    rows = [('map', '지도의 화살표 40곳을 눌러 선거유세! 지역마다 단 한 번뿐'),
            ('star', '지역마다 종목이 다른 미니게임. 잘할수록 지지율과 재화 UP'),
            ('bolt', '돌발상황 64종! 셋 중 하나는 반드시 안전하지만 어느 것인지는 몰라요'),
            ('shop', '작전 본부에서 재화로 사건을 만들거나 위기를 막을 수 있어요'),
            ('chart', '시작 자금 10억. 주식·코인으로 불리세요. 재산 0원이면 파산!'),
            ('trophy', '「조치원 지배 자본」 지분과 계열사를 큰아버지들과 다퉈요'),
            ('ballot', '개표는 언제든! 지지율 50% 초과 + 지배 자본 50% 초과면 당선')]
    for i, (ic, t) in enumerate(rows):
        yy = 70 - i * 26
        sprite(P, sc, '방법아이콘%d' % i, K.icon_img(ic, 20), -196, yy)
        text(P, sc, '방법글%d' % i, t, 20, yy, 11, '#FFFFFF', F_BODY, True, 1, w=396, h=20)
    button(P, sc, '돌아가기', '돌아가기', 0, -118, 110, 28, 'blue', icon='back', actions=go(S_TITLE))
    G.sound_hub(P, sc, 'bgm_title')
    G.fader(P, sc, BLACK)


# ================================================================== 지도
def _dt_ring(r):
    """전체 지도 위 '시내' 원 (누르면 시내 확대 지도로)."""
    from PIL import ImageDraw as _D
    k = 4
    sz = int(r * 2 + 8)
    im = Image.new('RGBA', (sz * k, sz * k), (0, 0, 0, 0))
    d = _D.Draw(im)
    c = sz * k / 2
    d.ellipse((c - r * k, c - r * k, c + r * k, c + r * k), fill=(60, 110, 255, 46), outline=(130, 170, 255, 230), width=3 * k)
    im = im.resize((sz * 2, sz * 2), Image.LANCZOS)
    return save(im, 'map_dt_ring_%d' % r)


def scene_map():
    sc = S_MAP
    bgo = G.bg(P, sc, [('whole', ART('map_whole')), ('dt', ART('map_dt'))])
    bgo.on(on_scene(), ifelse(eq(V('지도모드'), 1), [shape('dt')], [shape('whole')]))
    bgo.on(on_msg('지도바꿈'), ifelse(eq(V('지도모드'), 1), [shape('dt')], [shape('whole')]))
    # 핀 위치(무대 좌표). 시내 15곳은 시내 확대 지도에서만 보인다.
    pin_xy, pin_mode = {}, {}
    for k_ in range(1, N_PL + 1):
        sx, sy = art2stage(*PIN_POS[k_])
        pin_xy[k_] = (round(sx, 1), round(sy + 15, 1))         # 화살표 끝이 장소를 가리키도록
        pin_mode[k_] = 1 if k_ in DT_IDS else 0
    P.list('핀X', [pin_xy[k_][0] for k_ in range(1, N_PL + 1)])
    P.list('핀Y', [pin_xy[k_][1] for k_ in range(1, N_PL + 1)])
    # 시내 원 (전체 지도에서만)
    rcx, rcy = art2stage(DT_CIRCLE[0], DT_CIRCLE[1])
    rr = int(DT_CIRCLE[2] / 2)
    ring = sprite(P, sc, '시내원', _dt_ring(rr), rcx, rcy)
    ring.on(on_scene(), forever(ifelse(eq(V('지도모드'), 0), [show()], [hide()]),
                                ifelse(and_(touch('mouse'), eq(V('개표창'), 0)), [fx('brightness', 25), ring.pct(106)],
                                       [fx('brightness', 0), ring.pct(100)]), wait(0.05)))
    ring.on(on_click(), if_(and_(eq(V('지도모드'), 0), eq(V('개표창'), 0)), setv('지도모드', 1), cast('지도바꿈'), G.sfx('click')))
    ring_t = text(P, sc, '시내원글', '', rcx, rcy, 9, C_WHITE, F_NUM, False, 0, w=70, h=28)
    dt_list = DT_IDS

    def remain_blocks(ids, var):
        b = [setv(var, 0)]
        for k_ in ids:
            b.append(if_(eq(LGET('지역완료', k_), 0), chg(var, 1)))
        return b
    ring_t.on(on_scene(), forever(ifelse(eq(V('지도모드'), 0), [show()], [hide()]),
                                  *remain_blocks(dt_list, 'tmp'), write(join('조치원 시내\n', V('tmp'), '곳 (클릭)')), wait(0.3)))
    # 화살표 (유세를 마치면 사라짐)
    for k_ in range(1, N_PL + 1):
        x_, y_ = pin_xy[k_]
        m_ = pin_mode[k_]
        pics = [('on', SP.arrow_marker(k_, 'on')), ('hot', SP.arrow_marker(k_, 'hot'))]
        o = sprite(P, sc, '화살표%02d' % k_, pics, x_, y_, scale=0.9)
        vis = and_(eq(LGET('지역완료', k_), 0), eq(V('지도모드'), m_))
        o.on(on_scene(), xy(x_, y_),
             forever(ifelse(not_(vis), [hide(), if_(eq(V('호버지역'), k_), setv('호버지역', 0))],
                            [show(), ifelse(and_(touch('mouse'), eq(V('개표창'), 0)), [shape('hot'), o.pct(125), setv('호버지역', k_)],
                                            [shape('on'), o.pct(100), if_(eq(V('호버지역'), k_), setv('호버지역', 0))])]),
                     wait(0.04)))
        o.on(on_click(), if_(and_(vis, eq(V('개표창'), 0)), setv('현재지역', k_), *go(S_GAME[k_ - 1])))
    # 툴팁
    tip = panel(P, sc, '툴팁판', 0, 0, 150, 52, 'card', visible=False)
    tip_t = text(P, sc, '툴팁제목', '', 0, 0, 10, C_ACC, F_NUM, False, 0, w=144, h=16, visible=False)
    tip_d = text(P, sc, '툴팁설명', '', 0, 0, 8, '#FFFFFF', F_BODY, True, 0, w=140, h=26, visible=False)
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
    tip_t.on(on_scene(), forever(if_(gt(V('호버지역'), 0), write(join(V('호버지역'), '. ', LGET('지역이름', V('호버지역'))))), wait(0.05)))
    tip_d.on(on_scene(), forever(if_(gt(V('호버지역'), 0), write(join('[', LGET('지역게임', V('호버지역')), '] ', LGET('지역설명', V('호버지역'))))),
                                 wait(0.05)))
    # 왼쪽 메뉴
    for k_, (nm_, lbl_, col_, ic_, to_) in enumerate((('주식버튼', '거래소', 'blue', 'chart', S_STOCK),
                                                      ('작전버튼', '작전 본부', 'purple', 'bolt', S_SHOP),
                                                      ('계열사버튼', '계열사', 'royal', 'shop', S_GROUP),
                                                      ('협상버튼', '협상 테이블', 'red', 'trophy', S_NEGO))):
        button(P, sc, nm_, lbl_, -186, -36 - k_ * 26, 96, 24, col_, icon=ic_,
               actions=[if_(eq(V('개표창'), 0), *go(to_))])
    # 오른쪽: 지도 모드, 안내, 개표
    mode_b = sprite(P, sc, '지도이름', [('whole', K.badge('조치원 전체 지도', 100, 18, 'navy')),
                                       ('dt', K.badge('조치원 시내', 100, 18, 'royal'))], 186, 52)
    mode_b.on(on_scene(), forever(ifelse(eq(V('지도모드'), 1), [shape('dt')], [shape('whole')]), wait(0.1)))
    back_b = button(P, sc, '전체지도버튼', '전체 지도', 186, 28, 96, 22, 'navy', icon='back',
                    actions=[if_(eq(V('개표창'), 0), setv('지도모드', 0), cast('지도바꿈'))])
    back_b.on(on_scene(), forever(ifelse(eq(V('지도모드'), 1), [show()], [hide()]), wait(0.1)))
    dt_b = button(P, sc, '시내버튼', '시내 확대', 186, 28, 96, 22, 'royal', icon='map',
                  actions=[if_(eq(V('개표창'), 0), setv('지도모드', 1), cast('지도바꿈'))])
    dt_b.on(on_scene(), forever(ifelse(eq(V('지도모드'), 0), [show()], [hide()]), wait(0.1)))
    text(P, sc, '지도안내', '화살표를 눌러\n유세 시작!', 186, 0, 9, C_DIM, F_BODY, True, 0, w=100, h=26)
    left_t = text(P, sc, '남은곳', '', 186, -24, 9, C_WHITE, F_NUM, False, 0, w=100, h=14)
    left_t.on(on_scene(), forever(write(join('남은 유세지 ', sub(N_PL, V('유세횟수')), '곳')), wait(0.3)))
    vote_b = button(P, sc, '개표버튼', '개표하기', 186, -56, 96, 26, 'red', icon='ballot',
                    actions=[if_(eq(V('개표창'), 0), setv('개표창', 1), cast('개표묻기'))])
    hud(P, sc, PORT, empire=True, empire_xy=(186, -98), empire_w=104)
    # 개표 확인 창
    dim_ = sprite(P, sc, '개표어둡게', DIM, 0, 0, visible=False)
    box_ = panel(P, sc, '개표판', 0, 0, 280, 150, 'glass', header='red', visible=False)
    q_t = text(P, sc, '개표질문', '지금 개표할까요?', 0, 52, 16, C_WHITE, F_NUM, False, 0, w=260, h=24, visible=False)
    s_t = text(P, sc, '개표상황', '', 0, 14, 10, C_WHITE, F_BODY, True, 0, w=260, h=44, visible=False)
    s_t.on(on_msg('개표묻기'),
           write(join('지지율 ', round1(V('내지지율')), '%  ·  지배 자본 ', div(rounded(div(LGET('보유', 16), 100)), 10), '%\n',
                      '둘 다 50%를 넘어야 당선! 개표하면 게임이 끝나요.\n(유세 ', V('유세횟수'), '/', N_PL, '곳)')))
    yes_b = button(P, sc, '개표시작', '개표 시작', -62, -42, 104, 26, 'red', icon='ballot', visible=False,
                   actions=[if_(eq(V('개표창'), 1), setv('개표창', 2), *go(S_VOTE))])
    no_b = button(P, sc, '개표취소', '더 유세하기', 62, -42, 104, 26, 'navy', icon='back', visible=False,
                  actions=[if_(eq(V('개표창'), 1), setv('개표창', 0), cast('개표닫기'))])
    for o in (dim_, box_, q_t, s_t, yes_b, no_b):
        o.on(on_msg('개표묻기'), show())
        o.on(on_msg('개표닫기'), hide())
        o.on(on_scene(), hide())
    E.majority_pop(P, sc)
    # 모든 지역을 돌았으면 개표로
    chk = text(P, sc, '진행검사', '', -300, -300, 8, visible=False)
    chk.on(on_scene(), setv('개표창', 0), setv('호버지역', 0), *E.stats_blocks(), wait(0.4), *ST.assets_blocks(),
           if_(ge(V('유세횟수'), N_PL), *go(S_VOTE)), if_(le(V('총자산'), 0), *go(S_BANKRUPT)))
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, BLACK)


# ================================================================== 유세 결과
def scene_result():
    sc = S_RESULT
    bgo = G.bg(P, sc, PLACE_PICS)
    bgo.on(on_scene(), shape(V('현재지역')))
    sprite(P, sc, '어둡게', DIM, 0, 0)
    panel(P, sc, '결과판', 40, -8, 300, 214, 'glass', header='royal')
    sprite(P, sc, '결과제목', K.banner('유세 결과', 170, 34, 'royal'), 40, 106)
    place = text(P, sc, '결과장소', '', 40, 74, 13, '#FFFFFF', F_NUM, False, 0, w=300, h=20)
    place.on(on_scene(), write(join(LGET('지역이름', V('현재지역')), ' · ', LGET('지역게임', V('현재지역')))))
    score = text(P, sc, '결과점수', '0', 0, 36, 34, C_ACC, F_NUM, False, 0, w=140, h=44)
    text(P, sc, '점수단위', '점', 80, 30, 14, C_ACC, F_NUM, False, 1, w=30, h=20)
    stamp = sprite(P, sc, '등급도장', [(g, SP.grade_stamp(g)) for g in 'SABCD'], 150, 38, visible=False)
    rows = []
    labels = [('star', '지지율', C_WHITE), ('bolt', '큰아버지 반격', C_RED), ('coin', '재화', C_ACC), ('shop', '계열사 수익', C_ACC)]
    for i, (ic, lb, col) in enumerate(labels):
        yy = 2 - i * 20
        sprite(P, sc, '결과아이콘%d' % i, K.icon_img(ic, 16), -88, yy)
        text(P, sc, '결과라벨%d' % i, lb, -26, yy, 12, C_DIM, F_BODY, True, 1, w=100, h=18)
        rows.append(text(P, sc, '결과값%d' % i, '', 110, yy, 13, col, F_NUM, False, 2, w=150, h=18, visible=False))
    nxt = button(P, sc, '다음버튼', '다음', 40, -100, 100, 28, 'royal', icon='star', visible=False,
                 actions=[*ST.assets_blocks(), if_(le(V('총자산'), 0), *go(S_BANKRUPT)),
                          if_(ge(V('유세횟수'), N_PL), *go(S_VOTE)),
                          ifelse(le(rnd(1, 100), 70), go(S_EVENT), go(S_MAP))])
    # ---- 계산 (한 번만)
    calc = text(P, sc, '결과계산', '', -300, -300, 8, visible=False)
    w = LGET('지역비중', V('현재지역'))
    calc.on(on_scene(),
            if_(eq(V('결과처리됨'), 0),
                setv('결과처리됨', 1),
                lst_set('지역완료', V('현재지역'), 1), lst_set('지역점수', V('현재지역'), V('점수')), chg('유세횟수', 1),
                # 지지율 얻기 (큰아버지 둘에게서 비율대로 가져옴)
                # 지지율은 올라갈수록 덜 오른다
                setv('획득지지', round1(mul(mul(div(mul(V('점수'), w), 100), D.SUPPORT_MULT), sub(1.1, div(V('내지지율'), 100))))),
                if_(lt(V('획득지지'), 0), setv('획득지지', 0)),
                setv('tmp', div(V('큰A'), add(V('큰A'), V('큰B')))),
                chg('큰A', mul(mul(V('획득지지'), V('tmp')), -1)),
                chg('큰B', mul(mul(V('획득지지'), sub(1, V('tmp'))), -1)),
                chg('내지지율', V('획득지지')),
                # 큰아버지들의 반격
                ifelse(gt(V('차단턴'), 0), [setv('반격A', 0), setv('반격B', 0), chg('차단턴', -1), setv('이번차단', 1)],
                       [setv('반격A', div(rnd(*D.COUNTER_RANGE), 10)), setv('반격B', div(rnd(*D.COUNTER_RANGE), 10)), setv('이번차단', 0)]),
                if_(lt(V('내지지율'), add(add(V('반격A'), V('반격B')), 2)), setv('반격A', 0), setv('반격B', 0)),
                chg('내지지율', mul(add(V('반격A'), V('반격B')), -1)), chg('큰A', V('반격A')), chg('큰B', V('반격B')),
                setv('내지지율', round1(V('내지지율'))), setv('큰A', round1(V('큰A'))),
                setv('큰B', round1(sub(sub(100, V('내지지율')), V('큰A')))),
                # 재화
                setv('획득재화', rounded(mul(V('점수'), D.REWARD_PER_POINT))), if_(ge(V('점수'), 80), chg('획득재화', D.REWARD_BONUS)),
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
    rows[2].on(on_msg('결과줄'), wait(0.5), *fmt_money(V('획득재화'), '표시글'), write(join('+', V('표시글'))), show())
    rows[3].on(on_msg('결과줄'), wait(0.75), *fmt_money(V('계열사수입'), '표시글'),
               write(join('+', V('표시글'), ' (', V('계열사수'), '개)')), show())
    news_ = text(P, sc, '계열사소식', '', 40, -78, 9, C_RED, F_BODY, True, 0, w=280, h=13, visible=False)
    news_.on(on_msg('결과줄'), wait(0.9), if_(gt(slen(V('계열사소식')), 0), write(V('계열사소식')), show()))
    nxt.on(on_msg('결과줄'), wait(1.0), show())
    # 할아버지 한마디
    gp = sprite(P, sc, '할아버지', BUST['gp'], -200, -40, scale=0.62, visible=False)
    bub = panel(P, sc, '말풍선', -178, 46, 116, 50, 'card', visible=False)
    say_t = text(P, sc, '한마디', '', -178, 46, 10, C_WHITE, F_BODY, True, 0, w=104, h=40, visible=False)
    for o in (gp, bub, say_t):
        o.on(on_msg('결과줄'), wait(0.6), show())
    say_t.on(on_msg('결과줄'),
             ifelse(ge(V('점수'), 90), [write(D.GP_GRADE['S'])], [ifelse(ge(V('점수'), 75), [write(D.GP_GRADE['A'])], [
                 ifelse(ge(V('점수'), 55), [write(D.GP_GRADE['B'])], [ifelse(ge(V('점수'), 35), [write(D.GP_GRADE['C'])], [write(D.GP_GRADE['D'])])])])]))
    G.confetti(P, sc, '축하', CONF)
    hud(P, sc, PORT)
    hub = G.sound_hub(P, sc)
    hub.on(on_msg('도장'), play('stamp'))
    hub.on(on_msg('축하'), play('fanfare'))
    hub.on(on_msg('결과줄'), wait(0.5), play('coin'))
    G.fader(P, sc, BLACK)
    # 주가 변동 담당 (밤사이 시세, 장 시간, 큰아버지 지분 매수) + 계열사 수익/쟁탈
    ST.overnight_object(P, sc)
    E.overnight_object(P, sc)


# ================================================================== 주식 데이터
ST.setup(P)
E.setup(P)
STOCK_RESET = ST.reset_blocks()


# ================================================================== 미니게임 (임시: 나중에 교체)
def scene_minigame_stub(idx):
    sc = S_GAME[idx - 1]
    p = D.PLACES[idx - 1]
    G.bg(P, sc, ART('place_%02d' % idx))
    sprite(P, sc, '장소배너', K.banner('%s · %s' % (p['name'], p['game']), 230, 34, 'royal'), -110, 112)
    t = text(P, sc, '임시', '미니게임 준비 중 (클릭하면 점수)', 0, 0, 14, '#FFFFFF', F_BODY, True, 0, w=300, h=30, bg=C_BOX)
    t.on(on_click(), setv('점수', rnd(40, 100)), setv('결과처리됨', 0), *go(S_RESULT))
    G.fader(P, sc, BLACK)


def build(dev_dir=None, out=None):
    scene_title()
    scene_story()
    scene_howto()
    scene_map()
    import minigames
    for i in range(1, N_PL + 1):
        if not minigames.build_minigame(P, i, globals()):
            scene_minigame_stub(i)
    scene_result()
    ST.build(P, globals())
    E.build_group(P, globals())
    E.build_nego(P, globals())
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
