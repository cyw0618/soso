# -*- coding: utf-8 -*-
"""커리어 모드: 조치원 군수 → 세종시장 → 대통령.

단계(1~3) = 지금 치르는(또는 마지막으로 치른) 선거, 직위(0~3) = 지금 자리, 캠페인중 = 선거 유세 중인지.
- 군수가 되면 집무실(결재 서류·투자·정당)이 열린다. 총자산과 정당 공천을 갖추면 다음 선거에 나간다.
  세종시장: 총자산 5000억 + 공천 / 대통령: 총자산 10조 + 공천. 상대 후보 둘 중 지지율 1등이면 당선.
- 유세지는 단계마다 40곳 (지역번호 = (단계-1)*40 + 지역). 미니게임 장면은 단계마다 배경·제목을 바꿔 다시 쓴다.
- 엔딩(대통령 취임·은퇴·낙선)을 봐도 '계속 투자하기'로 집무실에 돌아가 투자를 이어 갈 수 있다.
"""
import math
from PIL import Image, ImageDraw
from entrygen import *
import ui_kit as K
import sprites as SP
import gui as G
from gui import text, sprite, panel, button, go, fmt_comma, fmt_money, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
from art_common import save
import data as D
import data2 as D2
import economy as EC

CAREER_VARS = dict(단계=1, 직위=0, 캠페인중=1, 평판=50, 창당=0, 당원=0, 공천=0, 정당이름='', 출정알림=0, 엔딩종류=0, 취임알림=0,
                   지역번호=1, 등록이름='', 등록점수=-1, _cp=0, _cv=0, _ci=0, _ok1='', _ok2='', _o1='', _o2='', _o3='', _o4='', _o6='',
                   재계산=1)
N = 40


def setup(P):
    P.list('직위이름', ['없음', '군수', '세종시장', '대통령'])
    P.list('단계이름', D2.TIER_NAMES)
    P.list('지역명', D2.REGION)
    P.list('상대1이름', ['첫째', '1번', '1번'])
    P.list('상대2이름', ['둘째', '2번', '2번'])
    P.list('첫째말', ['첫째 큰아버지', '1번 후보', '1번 후보'])
    P.list('둘째말', ['둘째 큰아버지', '2번 후보', '2번 후보'])
    P.list('큰아버지말', ['큰아버지', '상대 후보', '상대 후보'])
    P.list('보상배율', D2.REWARD_MULT)
    P.list('상점배율', D2.SHOP_MULT)
    P.list('지배이름', D2.CONTROL_NAMES)
    P.list('지배가', D2.CONTROL_PRICES)
    P.list('지배총액', D2.CONTROL_TOTAL)
    P.list('출마조건', [0, D2.MAYOR_NEED, D2.PRES_NEED])
    P.list('공천조건', [0, D2.NOMINATE_NEED[2], D2.NOMINATE_NEED[3]])
    P.list('출마목표말', ['', '세종시장', '대통령'])
    P.list('서류제목', [d[0].replace('{R}', '○○') for d in D2.DOCS])
    P.list('서류내용', [d[1].replace('{R}', '○○') for d in D2.DOCS])
    P.list('서류종류', [d[2] for d in D2.DOCS])
    P.list('직위점수', [0, 0, 20000, 70000])
    P.list('공천말', ['없음', '없음', '세종시장 공천 ✔', '대통령 공천 ✔'])
    P.list('할아버지말', D2.GP_OFFICE)
    P.list('당원모집이름', [r[0] for r in D2.PARTY_RECRUIT])
    P.list('당원모집비용', [r[1] * 10000 for r in D2.PARTY_RECRUIT])
    P.list('당원모집수', [r[2] for r in D2.PARTY_RECRUIT])
    P.list('당원모집직위', [r[3] for r in D2.PARTY_RECRUIT])


def region_name():
    """결재 서류 속 '○○' 자리에 들어갈 지역 이름 (군수: 조치원, 시장: 세종시, 대통령: 대한민국)."""
    return LGET('지역명', EC.clamp13(V('직위')))


def rival_text(expr):
    """글 속 '첫째/둘째 큰아버지', '큰아버지' 를 단계에 맞는 상대 이름으로."""
    s = str_replace(expr, '첫째 큰아버지', LGET('첫째말', V('단계')))
    s = str_replace(s, '둘째 큰아버지', LGET('둘째말', V('단계')))
    return str_replace(s, '큰아버지', LGET('큰아버지말', V('단계')))


def go_home(ctx):
    """'지도로' 대신: 유세 중이면 그 단계의 지도, 아니면 집무실."""
    return [cast('페이드아웃'), wait(0.2),
            ifelse(eq(V('캠페인중'), 0), [goto_scene(ctx['S_OFFICE'])],
                   [ifelse(eq(V('단계'), 1), [goto_scene(ctx['S_MAP'])],
                           [ifelse(eq(V('단계'), 2), [goto_scene(ctx['S_MAP2'])], [goto_scene(ctx['S_MAP3'])])])])]


def start_tier_blocks(t):
    """t(2 시장 / 3 대통령) 선거 시작."""
    import scene_stock as ST
    CTL = ST.CTL
    b = [setv('단계', t), setv('캠페인중', 1), setv('유세횟수', 0), setv('지도모드', 0), setv('출정알림', 1), setv('당선', 0),
         setv('내지지율', round1(add(6, mul(V('평판'), 0.12)))),
         setv('큰A', round1(mul(sub(100, V('내지지율')), div(rnd(50, 57), 100)))),
         setv('큰B', round1(sub(sub(100, V('내지지율')), V('큰A')))),
         setv('결과처리됨', 1), setv('차단턴', 0), setv('장시간', D.MARKET_START), setv('현재지역', 0)]
    b += [setv('_ci', (t - 1) * N + 1), rep(N, lst_set('지역완료', V('_ci'), 0), chg('_ci', 1))]
    import invest as IV
    b += IV.scale_blocks()
    # 지배 자본: 갖고 있던 지분은 팔아서 현금으로, 새 '세종시/대한민국 지배 자본' 으로 바뀐다
    b += [chg('돈', mul(LGET('보유', CTL), LGET('주가', CTL))), lst_set('보유', CTL, 0), lst_set('평단', CTL, 0),
          lst_set('주식이름', CTL, D2.CONTROL_NAMES[t - 1]), lst_set('주가', CTL, D2.CONTROL_PRICES[t - 1]),
          lst_set('전주가', CTL, D2.CONTROL_PRICES[t - 1]),
          setv('첫째주', D.CONTROL_UNCLES[0]), setv('둘째주', D.CONTROL_UNCLES[1]), setv('지배알림', 0)]
    b += [setv('_ci', (CTL - 1) * ST.HIST + 1), rep(ST.HIST, lst_set('주가기록', V('_ci'), D2.CONTROL_PRICES[t - 1]), chg('_ci', 1))]
    return b


def win_tier_blocks():
    """시장·대통령 당선 처리 (개표 장면에서)."""
    return [setv('직위', V('단계')), setv('캠페인중', 0), setv('취임알림', V('직위')),
            if_(lt(V('평판'), 50), setv('평판', 50)), chg('당원', mul(V('직위'), 100000))]


# ================================================================== 지도 (단계마다 하나)
def _ring_img(r):
    k = 4
    sz = int(r * 2 + 8)
    im = Image.new('RGBA', (sz * k, sz * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = sz * k / 2
    d.ellipse((c - r * k, c - r * k, c + r * k, c + r * k), fill=(60, 110, 255, 46), outline=(130, 170, 255, 230), width=3 * k)
    im = im.resize((sz * 2, sz * 2), Image.LANCZOS)
    return save(im, 'map_dt_ring_%d' % r)


def build_map(P, ctx, tier, sc, whole, dt, pins, dt_ids, ring, mode_names, ring_label):
    """pins: {k: (무대 x, 무대 y)} (화살표 중심), ring: (배경 x, 배경 y, 반지름(배경 px))."""
    from gui import hud
    import scene_stock as ST
    import empire as E
    import savegame as SG
    off = (tier - 1) * N
    bgo = G.bg(P, sc, [('whole', whole), ('dt', dt)])
    bgo.on(on_scene(), ifelse(eq(V('지도모드'), 1), [shape('dt')], [shape('whole')]))
    bgo.on(on_msg('지도바꿈'), ifelse(eq(V('지도모드'), 1), [shape('dt')], [shape('whole')]))
    P.list('핀X%d' % tier, [pins[k][0] for k in range(1, N + 1)])
    P.list('핀Y%d' % tier, [pins[k][1] for k in range(1, N + 1)])
    rcx, rcy = ring[0] / 2 - 240, 135 - ring[1] / 2
    rr = int(ring[2] / 2)
    ro = sprite(P, sc, '확대원', _ring_img(rr), rcx, rcy)
    ro.local('_hv', 0)
    vis_ring = [ifelse(eq(V('지도모드'), 0), [show()], [hide()])]
    ro.on(on_msg('지도바꿈'), *vis_ring)
    ro.on(on_scene(), *vis_ring, setv('_hv', 0), fx('brightness', 0), ro.pct(100),
          forever(ifelse(and_(and_(touch('mouse'), eq(V('개표창'), 0)), eq(V('지도모드'), 0)),
                         [if_(eq(V('_hv'), 0), setv('_hv', 1), fx('brightness', 25), ro.pct(106))],
                         [if_(eq(V('_hv'), 1), setv('_hv', 0), fx('brightness', 0), ro.pct(100))]), wait(0.05)))
    ro.on(on_click(), if_(and_(eq(V('지도모드'), 0), eq(V('개표창'), 0)), setv('지도모드', 1), cast('지도바꿈'), G.sfx('click')))
    rt = text(P, sc, '확대원글', '', rcx, rcy, 9, C_WHITE, F_NUM, False, 0, w=80, h=28)
    skip = D2.REMOVED.get(tier, ())
    cnt = [setv('tmp', 0)] + [if_(eq(LGET('지역완료', off + k), 0), chg('tmp', 1)) for k in dt_ids if k not in skip]
    rt.on(on_msg('지도바꿈'), *vis_ring)
    rt.on(on_scene(), *vis_ring, *G.live_write(rt, [*cnt, setv('_mrt', join(ring_label, '\n', V('tmp'), '곳 (클릭)'))], '_mrt', 0.5))
    for k in range(1, N + 1):
        if k in skip:
            continue
        x_, y_ = pins[k]
        m_ = 1 if k in dt_ids else 0
        pics = [('on', SP.arrow_marker(k, 'on')), ('hot', SP.arrow_marker(k, 'hot'))]
        o = sprite(P, sc, '화살표%02d' % k, pics, x_, y_, scale=0.9)
        o.local('_pv', -1)       # 0 숨김 / 1 보통 / 2 마우스 올림 (바뀔 때만 모양·크기를 바꾼다)
        vis = and_(eq(LGET('지역완료', off + k), 0), eq(V('지도모드'), m_))
        o.on(on_scene(), xy(x_, y_), setv('_pv', -1),
             forever(ifelse(not_(vis), [if_(ne(V('_pv'), 0), setv('_pv', 0), hide()), if_(eq(V('호버지역'), k), setv('호버지역', 0))],
                            [ifelse(and_(touch('mouse'), eq(V('개표창'), 0)),
                                    [if_(ne(V('_pv'), 2), setv('_pv', 2), shape('hot'), o.pct(125), show()), setv('호버지역', k)],
                                    [if_(ne(V('_pv'), 1), setv('_pv', 1), shape('on'), o.pct(100), show()),
                                     if_(eq(V('호버지역'), k), setv('호버지역', 0))])]),
                     wait(0.05)))
        games = ctx['S_GAME'] if tier == 1 else ctx['S_GAME%d' % tier]
        o.on(on_click(), if_(and_(vis, eq(V('개표창'), 0)), setv('현재지역', k), setv('지역번호', off + k),
                             *go(games[k - 1])))
    tip = panel(P, sc, '툴팁판', 0, 0, 150, 52, 'card', visible=False)
    tip_t = text(P, sc, '툴팁제목', '', 0, 0, 10, C_ACC, F_NUM, False, 0, w=144, h=16, visible=False)
    tip_d = text(P, sc, '툴팁설명', '', 0, 0, 8, '#FFFFFF', F_BODY, True, 0, w=140, h=26, visible=False)
    rid = add(off, V('호버지역'))
    for o, dy, wr in ((tip, 0, []), (tip_t, 12, [write(join(V('호버지역'), '. ', LGET('지역이름', rid)))]),
                      (tip_d, -8, [write(join('[', LGET('지역게임', rid), '] ', LGET('지역설명', rid)))])):
        o.local('_th', -1)      # 마지막으로 보여 준 지역 (바뀔 때만 옮기고 쓴다)
        o.on(on_scene(), setv('_th', -1), forever(
            if_(ne(V('호버지역'), V('_th')), setv('_th', V('호버지역')),
                ifelse(gt(V('호버지역'), 0),
                       [setv('tmp', LGET('핀X%d' % tier, V('호버지역'))),
                        if_(gt(V('tmp'), 150), setv('tmp', 150)), if_(lt(V('tmp'), -150), setv('tmp', -150)),
                        setv('tmp2', add(LGET('핀Y%d' % tier, V('호버지역')), 40)),
                        if_(gt(V('tmp2'), 70), setv('tmp2', sub(LGET('핀Y%d' % tier, V('호버지역')), 44))),
                        xy(V('tmp'), add(V('tmp2'), dy)), *wr, show()],
                       [hide()])),
            wait(0.04)))
    # 왼쪽 메뉴
    if tier == 1:
        menu = (('거래소', 'blue', 'chart', ctx['S_STOCK']), ('작전 본부', 'purple', 'bolt', ctx['S_SHOP']),
                ('계열사', 'royal', 'shop', ctx['S_GROUP']), ('협상 테이블', 'red', 'trophy', ctx['S_NEGO']),
                ('내 회사', 'green', 'coin', ctx['S_COMPANY']))
    else:
        menu = (('거래소', 'blue', 'chart', ctx['S_STOCK']), ('작전 본부', 'purple', 'bolt', ctx['S_SHOP']),
                ('집무실', 'royal', 'person', ctx['S_OFFICE']), ('계열사', 'steel', 'shop', ctx['S_GROUP']),
                ('내 회사', 'green', 'coin', ctx['S_COMPANY']))
    for k_, (lbl_, col_, ic_, to_) in enumerate(menu):
        button(P, sc, '메뉴%d' % k_, lbl_, -186, -10 - k_ * 26, 96, 24, col_, icon=ic_,
               actions=[if_(eq(V('개표창'), 0), *go(to_))])
    mode_b = sprite(P, sc, '지도이름', [('whole', K.badge(mode_names[0], 100, 18, 'navy')),
                                       ('dt', K.badge(mode_names[1], 100, 18, 'royal'))], 186, 52)
    mode_sel = [ifelse(eq(V('지도모드'), 1), [shape('dt')], [shape('whole')])]
    mode_b.on(on_scene(), *mode_sel)
    mode_b.on(on_msg('지도바꿈'), *mode_sel)
    back_b = button(P, sc, '전체지도버튼', '전체 지도', 186, 28, 96, 22, 'navy', icon='back',
                    actions=[if_(eq(V('개표창'), 0), setv('지도모드', 0), cast('지도바꿈'))])
    vb = [ifelse(eq(V('지도모드'), 1), [show()], [hide()])]
    back_b.on(on_scene(), *vb)
    back_b.on(on_msg('지도바꿈'), *vb)
    dt_b = button(P, sc, '확대버튼', '확대 지도', 186, 28, 96, 22, 'royal', icon='map',
                  actions=[if_(eq(V('개표창'), 0), setv('지도모드', 1), cast('지도바꿈'))])
    vd = [ifelse(eq(V('지도모드'), 0), [show()], [hide()])]
    dt_b.on(on_scene(), *vd)
    dt_b.on(on_msg('지도바꿈'), *vd)
    text(P, sc, '지도안내', '화살표를 눌러\n유세 시작!', 186, 0, 9, C_DIM, F_BODY, True, 0, w=100, h=26)
    left_t = text(P, sc, '남은곳', '', 186, -24, 9, C_WHITE, F_NUM, False, 0, w=100, h=14)
    left_t.on(on_scene(), *G.live_write(left_t, [setv('_mlt', join('남은 유세지 ', sub(N, V('유세횟수')), '곳'))], '_mlt', 0.5))
    button(P, sc, '개표버튼', '개표하기', 186, -56, 96, 26, 'red', icon='ballot',
           actions=[if_(eq(V('개표창'), 0), setv('개표창', 1), cast('개표묻기'))])
    hud(P, sc, ctx['PORT'], empire=True, empire_xy=(186, -98), empire_w=104)
    # 개표 확인 창
    dim_ = sprite(P, sc, '개표어둡게', ctx['DIM'], 0, 0, visible=False)
    box_ = panel(P, sc, '개표판', 0, 0, 280, 150, 'glass', header='red', visible=False)
    q_t = text(P, sc, '개표질문', '지금 개표할까요?', 0, 52, 16, C_WHITE, F_NUM, False, 0, w=260, h=24, visible=False)
    s_t = text(P, sc, '개표상황', '', 0, 14, 10, C_WHITE, F_BODY, True, 0, w=260, h=44, visible=False)
    if tier == 1:
        s_t.on(on_msg('개표묻기'),
               write(join('지지율 ', round1(V('내지지율')), '%  ·  지배 자본 ', div(rounded(div(LGET('보유', 16), 100)), 10), '%\n',
                          '둘 다 50%를 넘어야 당선! 개표하면 선거가 끝나요.\n(유세 ', V('유세횟수'), '/', N, '곳)')))
    else:
        s_t.on(on_msg('개표묻기'),
               write(join('나 ', round1(V('내지지율')), '% · 1번 ', round1(V('큰A')), '% · 2번 ', round1(V('큰B')), '%\n',
                          '후보 셋 중 1등이면 당선! 개표하면 선거가 끝나요.\n(유세 ', V('유세횟수'), '/', N, '곳)')))
    yes_b = button(P, sc, '개표시작', '개표 시작', -62, -42, 104, 26, 'red', icon='ballot', visible=False,
                   actions=[if_(eq(V('개표창'), 1), setv('개표창', 2), *go(ctx['S_VOTE']))])
    no_b = button(P, sc, '개표취소', '더 유세하기', 62, -42, 104, 26, 'navy', icon='back', visible=False,
                  actions=[if_(eq(V('개표창'), 1), setv('개표창', 0), cast('개표닫기'))])
    for o in (dim_, box_, q_t, s_t, yes_b, no_b):
        o.on(on_msg('개표묻기'), show())
        o.on(on_msg('개표닫기'), hide())
        o.on(on_scene(), hide())
    E.majority_pop(P, sc)
    if tier > 1:
        G.big_pop(P, sc, '출정팝', K.big_text('%s 선거 시작!' % D2.TIER_SHORT[tier - 1], 40, 'royal'), 0, 30, '출정', hold=1.6)
        st_t = text(P, sc, '출정설명', '%s 40곳을 돌며 후보 셋 중 지지율 1등을 노려라!' % ('세종시' if tier == 2 else '전국'),
                    0, -6, 11, C_WHITE, F_BODY, True, 0, w=380, h=18, visible=False, bg=C_BOX)
        st_t.on(on_msg('출정'), to_front(), show(), wait(2.6), hide())
    sv = text(P, sc, '자동저장', '', -300, -300, 8, visible=False)
    sv.on(on_scene(), if_(eq(V('재계산'), 1), setv('재계산', 0), *EC.recalc_loop()), wait(0.2), *ST.assets_blocks(),
          if_(and_(lt(V('유세횟수'), N), gt(V('총자산'), 0)), *SG.save_blocks()))
    chk = text(P, sc, '진행검사', '', -300, -300, 8, visible=False)
    chk.on(on_scene(), setv('개표창', 0), setv('호버지역', 0), *E.stats_blocks(),
           if_(eq(V('출정알림'), 1), setv('출정알림', 0), wait(0.5), cast('출정')),
           wait(0.4), *ST.assets_blocks(),
           if_(ge(V('유세횟수'), N), *go(ctx['S_VOTE'])), if_(le(V('총자산'), 0), *go(ctx['S_BANKRUPT'])))
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])


# ================================================================== 집무실
def build_office(P, ctx):
    import scene_stock as ST
    import savegame as SG
    sc = ctx['S_OFFICE']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    ttl = sprite(P, sc, '제목', [('1', K.banner('조치원 군수 집무실', 180, 30, 'royal')), ('2', K.banner('세종시장 집무실', 170, 30, 'purple')),
                                ('3', K.banner('대통령 집무실', 160, 30, 'red'))], 0, 116)
    ttl.on(on_scene(), if_(gt(V('직위'), 0), shape(V('직위'))))
    # ---- 왼쪽 위: 결재 서류
    panel(P, sc, '서류판', -118, 24, 236, 120, 'glass', header='royal')
    text(P, sc, '서류머리', '오늘의 결재 서류', -164, 76, 10, C_WHITE, F_NUM, False, 1, w=120, h=14)
    left_ = text(P, sc, '서류수', '', -48, 76, 8, C_DIM, F_BODY, True, 2, w=90, h=12)
    dt_ = text(P, sc, '서류제목', '', -118, 56, 11, C_ACC, F_NUM, False, 0, w=224, h=16)
    db_ = text(P, sc, '서류내용', '', -118, 28, 8, C_WHITE, F_BODY, True, 0, w=224, h=34)
    has = and_(gt(V('결재수'), 0), gt(V('서류번호'), 0))
    left_.on(on_msg('서류갱신'), write(join('남은 서류 ', V('결재수'), '장')))
    dt_.on(on_msg('서류갱신'), ifelse(has, [write(str_replace(LGET('서류제목', V('서류번호')), '○○', region_name()))],
                                     [write('결재할 서류가 없어요')]))
    db_.on(on_msg('서류갱신'), ifelse(has, [write(str_replace(LGET('서류내용', V('서류번호')), '○○', region_name()))],
                                     [write('새 서류는 45초마다 올라와요.\n그동안 투자로 돈을 불리세요!')]))
    mult = LGET('상점배율', EC.clamp13(V('직위')))
    kind = LGET('서류종류', V('서류번호'))

    def decide(approve):
        if approve:
            res = [ifelse(eq(kind, 1), [chg('평판', D2.DOC_GOOD), setv('경제알림', '좋은 결정! 시민들이 반긴다 (평판 +5)')],
                          [ifelse(eq(kind, 2), [chg('평판', -D2.DOC_BAD), setv('경제알림', '시민들이 실망했다... (평판 -6)')],
                                  [setv('_cv', mul(D2.DOC_BRIBE, mult)), chg('돈', V('_cv')), chg('의혹', 15),
                                   setv('_cp', D2.DOC_BRIBE_RISK), if_(gt(LGET('매수남은', 1), 0), setv('_cp', D2.DOC_BRIBE_RISK / 2)),
                                   ifelse(le(rnd(1, 100), V('_cp')),
                                          [chg('평판', -15), chg('돈', mul(V('_cv'), -2)),
                                           setv('경제알림', '뒷돈이 들통났다! 벌금에 평판 -15')],
                                          [*fmt_money(V('_cv'), '_m'), setv('경제알림', join('아무도 모른다... (+', V('_m'), ')'))])])])]
        else:
            res = [ifelse(eq(kind, 1), [chg('평판', -D2.DOC_BAD), setv('경제알림', '필요한 일을 막았다는 비판 (평판 -6)')],
                          [ifelse(eq(kind, 2), [chg('평판', D2.DOC_GOOD), setv('경제알림', '현명한 반려! (평판 +5)')],
                                  [chg('평판', 3), setv('경제알림', '깨끗한 정치! (평판 +3)')])])]
        return [if_(has, *res, if_(gt(V('평판'), 100), setv('평판', 100)), if_(lt(V('평판'), 0), setv('평판', 0)),
                    chg('결재수', -1), setv('서류번호', 0), cast('경제알림'), G.sfx('stamp'), cast('서류새로'))]
    ba = button(P, sc, '승인', '승인', -164, -18, 70, 22, 'royal', icon='star', actions=decide(True))
    br = button(P, sc, '반려', '반려', -72, -18, 70, 22, 'red', icon='back', actions=decide(False))
    for b in (ba, br):
        b.on(on_msg('서류갱신'), ifelse(has, [show()], [hide()]))
    # ---- 왼쪽 아래: 평판 · 정당
    panel(P, sc, '평판판', -118, -76, 236, 70, 'glass')
    rep_b = sprite(P, sc, '평판막대', K.bar_set('rep_royal', 120, 8, 'royal'), -100, -52)
    rep_b.on(on_scene(), *G.live_shape(rep_b, add(floor(div(V('평판'), 2.5)), 1), 0.3))
    text(P, sc, '평판글자', '평판', -206, -52, 9, C_WHITE, F_NUM, False, 1, w=40, h=13)
    rep_t = text(P, sc, '평판값', '', -10, -52, 9, C_ACC, F_NUM, False, 2, w=40, h=13)
    rep_t.on(on_scene(), *G.live_write(rep_t, [setv('_o1', V('평판'))], '_o1', 0.3))
    rep_i = text(P, sc, '평판효과', '', -118, -68, 7, C_DIM, F_BODY, True, 0, w=226, h=12)
    rep_i.on(on_scene(), *G.live_write(rep_i, [setv('_o2', join('다음 선거 시작 지지율 ', round1(add(6, mul(V('평판'), 0.12))),
                                                                '% · 급여 ×', add(0.5, div(V('평판'), 100))))], '_o2', 0.4))
    pty = text(P, sc, '정당요약', '', -118, -90, 8, C_WHITE, F_BODY, True, 0, w=226, h=24)
    pty.on(on_scene(), *G.live_write(pty, [ifelse(eq(V('창당'), 1),
                                                  [*fmt_comma(V('당원'), '_q'),
                                                   setv('_o3', join('정당: ', V('정당이름'), ' · 당원 ', V('_q'), '명\n공천: ',
                                                                    ifelse_word(V('공천'))))],
                                                  [setv('_o3', '정당이 없어요. 시장 선거에 나가려면 창당하세요!')])], '_o3', 0.4))
    # ---- 오른쪽: 투자 메뉴
    menu = (('내 회사', 'green', 'coin', ctx['S_COMPANY']), ('기업 인수', 'royal', 'shop', ctx['S_MA']),
            ('부동산', 'purple', 'map', ctx['S_LAND']), ('정당', 'red', 'person', ctx['S_PARTY']),
            ('거래소', 'blue', 'chart', ctx['S_STOCK']), ('작전 본부', 'steel', 'bolt', ctx['S_SHOP']),
            ('수사 대응', 'red', 'shield', ctx['S_CASE']))
    for k, (lbl, col, ic, to) in enumerate(menu):
        c, r = k % 2, k // 2
        mb = button(P, sc, '투자메뉴%d' % k, lbl, 74 + c * 100, 58 - r * 22, 94, 20, col, icon=ic, actions=go(to))
        if lbl == '수사 대응':
            mb.on(on_scene(), forever(ifelse(gt(V('수사기관'), 0), [fx('brightness', 30), wait(0.4), fx('brightness', 0), wait(0.4)],
                                             [wait(1)])))
    inc = text(P, sc, '시간수입', '', 174, -8, 8, '#7CFFB2', F_NUM, False, 0, w=110, h=13)
    inc.on(on_scene(), *G.live_write(inc, [*fmt_money(V('주기수입'), '_m'), setv('_o4', join('10초마다 +', V('_m')))], '_o4', 0.5))
    # ---- 오른쪽 아래: 다음 선거
    panel(P, sc, '출마판', 124, -72, 220, 76, 'glass', header='red')
    tgt = add(V('직위'), 1)
    goal = text(P, sc, '출마목표', '', 124, -40, 10, C_WHITE, F_NUM, False, 0, w=210, h=15)
    cond = text(P, sc, '출마조건', '', 124, -62, 8, C_DIM, F_BODY, True, 0, w=210, h=26)
    goal.on(on_scene(), ifelse(ge(V('직위'), 3), [write('대한민국 정상에 섰다!')],
                               [ifelse(eq(V('캠페인중'), 1), [write(join(LGET('단계이름', V('단계')), ' 선거 유세 중'))],
                                       [write(join('다음 목표: ', LGET('출마목표말', add(V('직위'), 1))))])]))
    cond.on(on_scene(), *G.live_write(cond, [
        ifelse(or_(ge(V('직위'), 3), eq(V('캠페인중'), 1)),
               [ifelse(ge(V('직위'), 3), [setv('_o6', '엔딩 뒤에도 계속 투자하며\n재산을 불릴 수 있어요')],
                       [setv('_o6', '지도로 돌아가 유세를 이어 가세요')])],
               [*ST.assets_blocks(), *fmt_money(V('총자산'), '_m'), setv('_q', V('_m')),
                *fmt_money(LGET('출마조건', tgt), '_m'),
                ifelse(ge(V('총자산'), LGET('출마조건', tgt)), [setv('_ok1', '✔')], [setv('_ok1', '✘')]),
                ifelse(ge(V('공천'), tgt), [setv('_ok2', '✔')], [setv('_ok2', '✘')]),
                setv('_o6', join('총자산 ', V('_q'), ' / ', V('_m'), ' ', V('_ok1'), '\n정당 공천 ', V('_ok2')))])], '_o6', 0.5))
    elect = button(P, sc, '출마버튼', '출마 선언', 70, -98, 96, 24, 'red', icon='ballot',
                   actions=[*ST.assets_blocks(),
                            ifelse(eq(V('캠페인중'), 1), go_home(ctx),
                                   [ifelse(ge(V('직위'), 3), [setv('경제알림', '이미 대통령이에요!'), cast('경제알림')],
                                           [ifelse(and_(ge(V('총자산'), LGET('출마조건', tgt)), ge(V('공천'), tgt)),
                                                   EC.contract_go(ctx, 6, tgt, 0, '후보자 등록 신청서',
                                                                  join('1. 을은 ', LGET('출마목표말', add(V('직위'), 1)), ' 선거에 「',
                                                                       V('정당이름'), '」 공천 후보로 등록한다.\n'
                                                                       '2. 을은 선거법을 지키며 40곳을 돌며 유세한다.\n'
                                                                       '3. 후보 셋 가운데 지지율 1등이 당선된다.'),
                                                                  '중앙선거관리위원회'),
                                                   [setv('경제알림', '총자산과 정당 공천이 모두 필요해요!'), cast('경제알림'), G.sfx('bad')])])])])
    retire = button(P, sc, '은퇴버튼', '은퇴·기록', 176, -98, 92, 24, 'gray', icon='trophy',
                    actions=[setv('엔딩종류', 2), *go(ctx['S_ENDING'])])
    elect.on(on_scene(), ifelse(ge(V('직위'), 3), [hide()], [show()]))
    # 할아버지 / 취임 알림
    G.big_pop(P, sc, '취임팝', [('1', K.big_text('군수 취임!', 40, 'royal')), ('2', K.big_text('세종시장 취임!', 40, 'royal')),
                               ('3', K.big_text('대통령 집무 시작!', 36, 'royal'))], 0, 30, '취임', hold=1.6,
              pre=[if_(gt(V('직위'), 0), shape(V('직위')))])
    gp_t = text(P, sc, '할아버지말', '', 0, -2, 10, C_WHITE, F_BODY, True, 0, w=320, h=32, visible=False, bg=C_BOX)
    gp_t.on(on_msg('취임'), write(LGET('할아버지말', EC.clamp13(V('직위')))), to_front(), wait(0.4), show(), wait(3.2), hide())
    mgr = text(P, sc, '집무담당', '', -300, -300, 8, visible=False)
    new_doc = [if_(and_(gt(V('결재수'), 0), eq(V('서류번호'), 0)), setv('서류번호', rnd(1, len(D2.DOCS)))), cast('서류갱신')]
    mgr.on(on_scene(), *new_doc, if_(eq(V('재계산'), 1), setv('재계산', 0), *EC.recalc_loop()), *EC.income_sum(),
           if_(gt(V('취임알림'), 0), setv('취임알림', 0), wait(0.5), cast('취임')),
           wait(0.6), *ST.assets_blocks(), if_(gt(V('총자산'), 0), *SG.save_blocks()))
    mgr.on(on_msg('서류새로'), *new_doc)
    mgr.on(on_msg('경제갱신'), *new_doc)
    G.hud(P, sc, ctx['PORT'])
    hub = G.sound_hub(P, sc, 'bgm_map')
    hub.on(on_msg('취임'), play('fanfare'))
    G.confetti(P, sc, '취임', ctx['CONF'], 40)
    G.fader(P, sc, ctx['BLACK'])
    # 계약 6: 후보 등록 → 선거 시작
    EC.CONTRACT_KINDS[6] = ([if_(eq(V('계약대상'), 2), *start_tier_blocks(2)), if_(eq(V('계약대상'), 3), *start_tier_blocks(3))],
                            go_home(ctx))


def ifelse_word(nom):
    return LGET('공천말', add(nom, 1))


# ================================================================== 정당
def build_party(P, ctx):
    sc = ctx['S_PARTY']
    G.bg(P, sc, ctx['ART']('story_bg'))
    sprite(P, sc, '어둡게', ctx['DIM'], 0, 0)
    sprite(P, sc, '제목', K.banner('정당', 100, 30, 'red'), 0, 116)
    made = eq(V('창당'), 1)
    # 창당 전
    pre = [panel(P, sc, '창당판', 0, -6, 360, 150, 'glass', header='red'),
           text(P, sc, '창당설명', '군수 다음 자리에 오르려면 정당이 있어야 해요.\n정당을 만들고 당원을 모아 공천을 받으세요.\n창당 비용 10억',
                0, 30, 11, C_WHITE, F_BODY, True, 0, w=330, h=60)]
    asker = sprite(P, sc, '이름묻기', K.icon_img('star', 2), 0, -40)
    pre.append(button(P, sc, '창당버튼', '창당하기', 0, -50, 130, 28, 'red', icon='person', actions=[cast('창당시작')]))
    asker.on(on_msg('창당시작'),
             ifelse(lt(V('돈'), D2.PARTY_COST),
                    [setv('경제알림', '현금 10억이 필요해요!'), cast('경제알림'), G.sfx('bad')],
                    [ask('정당 이름을 입력하세요 (예: 조치원미래당)'),
                     setv('정당이름', str_replace(str_replace(answer(), '[|§]', ''), ' ', '')),
                     if_(eq(slen(V('정당이름')), 0), setv('정당이름', '조치원미래당')),
                     if_(gt(slen(V('정당이름')), 10), setv('정당이름', substr(V('정당이름'), 1, 10))),
                     *EC.contract_go(ctx, 4, 0, D2.PARTY_COST, '정당 창당 신고서',
                                     join('1. 을은 「', V('정당이름'), '」을(를) 창당하고 대표가 된다.\n'
                                          '2. 창당 비용 10억 원은 을이 낸다.\n3. 당원이 늘면 후원금이 들어오고, 공천을 줄 수 있다.'),
                                     '중앙선거관리위원회')]))
    # 창당 후
    post = [panel(P, sc, '정당판', -112, -6, 232, 190, 'glass', header='red')]
    nm = text(P, sc, '정당이름', '', -112, 74, 15, C_WHITE, F_NUM, False, 0, w=220, h=20)
    nm.on(on_msg('정당갱신'), write(V('정당이름')))
    mem = text(P, sc, '당원수', '', -112, 46, 12, C_ACC, F_NUM, False, 0, w=220, h=17)
    mem.on(on_msg('정당갱신'), *fmt_comma(V('당원'), '_q'), write(join('당원 ', V('_q'), '명')))
    fee = text(P, sc, '후원금', '', -112, 26, 9, C_WHITE, F_BODY, True, 0, w=220, h=13)
    fee.on(on_msg('정당갱신'), *fmt_money(mul(V('당원'), D2.PARTY_FEE), '_m'), write(join('10초마다 후원금 +', V('_m'))))
    nom = text(P, sc, '공천상태', '', -112, -6, 9, C_WHITE, F_BODY, True, 0, w=220, h=40)
    tgt = add(EC.clamp13(V('직위')), 1)
    nom.on(on_msg('정당갱신'),
           ifelse(ge(V('직위'), 3), [write('대통령을 배출한 정당!\n당원이 늘수록 후원금도 늘어요')],
                  [*fmt_comma(LGET('공천조건', EC.ifelse_min3(tgt)), '_q'),
                   ifelse(ge(V('공천'), tgt), [write(join(LGET('출마목표말', EC.ifelse_min3(tgt)), ' 선거 공천 완료 ✔'))],
                          [write(join(LGET('출마목표말', EC.ifelse_min3(tgt)), ' 공천 조건: 당원 ', V('_q'), '명'))])]))
    gb = button(P, sc, '공천버튼', '공천 받기', -112, -60, 120, 26, 'red', icon='ballot',
                actions=[if_(lt(V('직위'), 3),
                             ifelse(ge(V('공천'), tgt), [setv('경제알림', '이미 공천을 받았어요!')],
                                    [ifelse(ge(V('당원'), LGET('공천조건', EC.ifelse_min3(tgt))),
                                            [setv('공천', tgt), setv('경제알림', '공천 확정! 이제 집무실에서 출마를 선언하세요'), G.sfx('fanfare')],
                                            [setv('경제알림', '당원이 부족해요! 당원을 더 모으세요'), G.sfx('bad')])]),
                             cast('경제알림'), cast('정당갱신'))])
    post += [nm, mem, fee, nom, gb]
    post.append(panel(P, sc, '모집판', 124, -6, 210, 190, 'glass', header='purple'))
    post.append(text(P, sc, '모집제목', '당원 모으기', 124, 74, 13, C_WHITE, F_NUM, False, 0, w=200, h=18))
    for j, r in enumerate(D2.PARTY_RECRUIT, 1):
        y = 40 - (j - 1) * 46
        cost = mul(LGET('당원모집비용', j), LGET('상점배율', EC.clamp13(V('직위'))))
        b = button(P, sc, '모집%d' % j, r[0], 124, y, 150, 24, 'purple', icon='person',
                   actions=[ifelse(lt(V('직위'), r[3]), [setv('경제알림', '세종시장이 되면 할 수 있어요!')],
                                   [ifelse(ge(V('돈'), cost),
                                           [chg('돈', mul(cost, -1)), chg('당원', mul(r[2], div(rnd(80, 120), 100))),
                                            setv('당원', rounded(V('당원'))), setv('경제알림', '당원이 늘었다!'), G.sfx('coin')],
                                           [setv('경제알림', '현금이 부족해요!'), G.sfx('bad')])]),
                            cast('경제알림'), cast('정당갱신')])
        info = text(P, sc, '모집정보%d' % j, '', 124, y - 18, 8, C_DIM, F_BODY, True, 0, w=196, h=12)
        info.on(on_msg('정당갱신'), *fmt_money(cost, '_m'), *fmt_comma(r[2], '_q'), write(join(V('_m'), ' · 당원 약 +', V('_q'), '명')))
        post += [b, info]
    for o in pre:
        o.on(on_msg('정당화면'), ifelse(made, [hide()], [show()]))
    for o in post:
        o.on(on_msg('정당화면'), ifelse(made, [show()], [hide()]))
    mgr = text(P, sc, '정당담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), cast('정당화면'), cast('정당갱신'))
    mgr.on(on_msg('경제갱신'), cast('정당갱신'))
    button(P, sc, '돌아가기', '돌아가기', -196, -121, 76, 22, 'navy', icon='back', actions=go_home(ctx))
    G.hud(P, sc, ctx['PORT'])
    G.sound_hub(P, sc, 'bgm_map')
    G.fader(P, sc, ctx['BLACK'])
    EC.CONTRACT_KINDS[4] = ([if_(and_(ge(V('돈'), D2.PARTY_COST), eq(V('창당'), 0)), chg('돈', -D2.PARTY_COST), setv('창당', 1),
                                 setv('당원', 300))],
                            go(sc))


# ================================================================== 엔딩 (대통령 취임 · 은퇴)
def build_ending(P, ctx):
    import scenes_more as SM
    import scene_stock as ST
    sc = ctx['S_ENDING']
    G.bg(P, sc, ctx['ART']('title_bg'))
    sprite(P, sc, '어둡게', SM._tint('fx_dark_navy', (2, 4, 16, 200)), 0, 0)
    sprite(P, sc, '청색빛', SM._edge_glow('fx_edge_blue', (20, 50, 200), 170), 0, 0)
    G.big_pop(P, sc, '취임글', K.big_text('대통령 취임!', 50, 'royal'), 0, 82, '대통령취임', hold=99, fade=False)
    G.big_pop(P, sc, '은퇴글', K.big_text('명예로운 은퇴', 42, 'royal'), 0, 82, '은퇴', hold=99, fade=False)
    summ = text(P, sc, '엔딩요약', '', 0, 40, 11, C_WHITE, F_NUM, False, 0, w=420, h=36, visible=False)
    sm = [*ST.assets_blocks(), *fmt_money(V('총자산'), '_m'),
          write(join('최종 직위 ', LGET('직위이름', add(V('직위'), 1)), '  ·  총자산 ', V('_m'), '\n인수한 기업 ', V('인수수'),
                     '개  ·  당원 ', V('당원'), '명  ·  평판 ', V('평판'))), show()]
    summ.on(on_msg('대통령취임'), wait(0.6), *sm)
    summ.on(on_msg('은퇴'), wait(0.6), *sm)
    pres = sprite(P, sc, '나', ctx['BUST']['me'], 186, -40, scale=0.5, visible=False)
    pres.on(on_msg('대통령취임'), wait(1.0), show())
    SM.ending_dim(P, sc)
    SM.grandpa_say(P, sc, ctx, -170, -8, '엔딩대사',
                   [ifelse(eq(V('엔딩종류'), 1), [write(D2.GP_PRES_WIN)], [write('수고했다.\n네가 쌓은 건 아무도 못 뺏는다.')])],
                   scale=0.6, bx=40, by=28, bw=220)
    G.confetti(P, sc, '축하', ctx['CONF'], 60)
    # 버튼: 계속 투자하기 / 랭킹에 기록 / 처음으로
    cont = button(P, sc, '계속투자', '계속 투자하기', -130, -112, 120, 28, 'royal', icon='coin', visible=False,
                  actions=[setv('캠페인중', 0), *go(ctx['S_OFFICE'])])
    reg = button(P, sc, '기록남기기', '랭킹에 기록', 0, -112, 120, 28, 'purple', icon='trophy', visible=False,
                 actions=[cast('기록시작')])
    home = button(P, sc, '처음으로', '처음으로', 130, -112, 110, 28, 'navy', icon='back', visible=False,
                  actions=go(ctx['S_TITLE']))
    for b in (cont, reg, home):
        b.on(on_msg('엔딩버튼'), show())
        b.on(on_msg('이름입력'), hide())
        b.on(on_msg('랭킹등록'), show())
    rk = text(P, sc, '내순위', '', 0, -86, 11, C_ACC, F_NUM, False, 0, w=360, h=16, visible=False)
    rk.on(on_msg('랭킹등록'), *fmt_comma(V('최종점수'), '_q'),
          write(join('최종 점수 ', V('_q'), '점 · 명예의 전당 ', V('내순위'), '위!')), show())
    mgr = text(P, sc, '엔딩담당', '', -300, -300, 8, visible=False)
    mgr.on(on_scene(), wait(0.4),
           ifelse(eq(V('엔딩종류'), 1), [cast('대통령취임'), cast('축하')], [cast('은퇴')]),
           wait(2.0), cast('엔딩대사'), wait(1.4), cast('엔딩버튼'))
    mgr.on(on_msg('기록시작'), *SM.score_blocks(), cast('이름입력'))
    SM.name_asker(P, sc)
    hub = G.sound_hub(P, sc, 'bgm_title')
    hub.on(on_msg('대통령취임'), play('fanfare'))
    G.fader(P, sc, ctx['BLACK'])
