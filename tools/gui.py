# -*- coding: utf-8 -*-
"""엔트리 오브젝트로 만드는 UI 부품 (버튼, 패널, 글자, HUD, 화면 전환, 팝업, 효과)."""
import os
import json
from entrygen import *
import ui_kit as K

F_BODY = 'NanumSquareRound'
F_NUM = 'yg-jalnan'

# 글자색 (검정+청색 테마)
C_WHITE = '#FFFFFF'
C_ACC = '#7D97FF'      # 청색 강조
C_DIM = '#AEB8D6'
C_RED = '#FF5C70'      # 오름(한국 증시 관례: 빨강)
C_BLUE = '#5E8BFF'     # 내림(파랑)
C_VIOLET = '#B094FF'
C_BOX = '#0A0F24'      # 글상자 배경

_names = {}


def uname(scene, base):
    """오브젝트 이름은 프로젝트 전체에서 겹치지 않게 (장면 약칭을 붙인다)."""
    key = '%s_%s' % (base, scene)
    n = _names.get(key, 0)
    _names[key] = n + 1
    return key if n == 0 else '%s%d' % (key, n + 1)


# ------------------------------------------------------------------ 기본 부품
def sprite(P, scene, base, pics, x=0, y=0, scale=1.0, visible=True):
    if isinstance(pics, str):
        pics = [('기본', pics)]
    return P.sprite(uname(scene, base), scene, pics, x=x, y=y, scale=scale, visible=visible)


def bg(P, scene, path_or_pics, base='배경'):
    return sprite(P, scene, base, path_or_pics, 0, 0)


def text(P, scene, base, txt, x, y, size=12, color='#ffffff', font=F_BODY, bold=True, align=0, w=None, h=None,
         visible=True, bg=None):
    """글상자. w 를 주면 고정 폭(줄바꿈 모드), 주지 않으면 글자 길이에 맞춤."""
    fnt = '%dpx %s' % (size, font)
    if w:
        return P.textbox(uname(scene, base), scene, txt, x=x, y=y, width=w, height=h or int(size * 1.6), bg=bg,
                         font=fnt, bold=bold, color=color, align=align, line_break=True, visible=visible)
    return P.textbox(uname(scene, base), scene, txt, x=x, y=y, width=max(20, int(len(txt) * size * 0.9)),
                     height=int(size * 1.5), bg=bg, font=fnt, bold=bold, color=color, align=align,
                     line_break=False, visible=visible)


def panel(P, scene, base, x, y, w, h, kind='glass', header=None, visible=True):
    return sprite(P, scene, base, K.panel(w, h, kind, header=header), x, y, visible=visible)


def hover_scripts(o, big=108, normal=100, first_scene=False):
    """마우스를 올리면 살짝 커지고 밝아지는 효과. 상태가 바뀔 때만 크기·밝기를 바꾼다 (매 프레임 바꾸면 화면이 느려짐).
    상태는 지역 변수 대신 '지금 크기'로 판단한다 → 버튼마다 같은 코드가 되어 함수 하나로 합쳐진다."""
    mid = round(o.base_size * (big + normal) / 200.0, 2)
    size = B('coordinate_object', VALUE='self', COORDINATE='size')
    loop = [o.pct(normal), fx('brightness', 0),
            forever(ifelse(touch('mouse'), [if_(lt(size, mid), o.pct(big), fx('brightness', 12))],
                           [if_(gt(size, mid), o.pct(normal), fx('brightness', 0))]),
                    wait(0.04))]
    o.on(on_scene(), *loop)
    if first_scene:
        o.on(on_run(), *loop)


def button(P, scene, base, label, x, y, w, h, color='royal', icon=None, actions=(), hover=True, visible=True,
           first_scene=False):
    o = sprite(P, scene, base, K.button(label, w, h, color, icon=icon), x, y, visible=visible)
    if hover:
        hover_scripts(o, first_scene=first_scene)
    # 누름 효과와 동작을 따로 (빠르게 여러 번 눌러도 동작은 매번 실행)
    o.on(on_click(), o.pct(92), cast('snd:click'), *flat(actions))
    o.on(on_click(), wait(0.07), ifelse(touch('mouse'), [o.pct(108)], [o.pct(100)]))
    return o


def clean_name(expr, chars='|§,/~^# '):
    """입력 이름에서 저장 글의 칸 나누는 글자와 띄어쓰기를 뺀 식 (엔트리 '바꾸기'는 글자 그대로 바꾼다)."""
    for ch in chars:
        expr = str_replace(expr, ch, '')
    return expr


def clone_rows(o, n, var, x_expr, y_expr, on_make=(), per=5):
    """오브젝트 o 를 줄(칸) n개의 '원본'으로: 장면이 시작되면 복제본 n개를 만들고(한 바퀴에 per개),
    복제본마다 지역 변수 var(1..n)에 자기 줄 번호가 있다. 원본은 숨긴 채 무대 밖에 둔다.
    on_make: 복제본이 생기자마자 할 블록 (처음 글·모양: 장면 시작 신호를 놓칠 수 있으므로)."""
    o.local(var, 0)
    full, rem = divmod(n, per)

    def mk():
        return [chg(var, 1), clone_self()]
    o.on(on_scene(), hide(), setv(var, 0), *([rep(full, *[b for _ in range(per) for b in mk()])] if full else []),
         *[b for _ in range(rem) for b in mk()])
    o.on(on_clone(), xy(x_expr, y_expr), *flat(on_make))
    return o


def live_write(o, make, var, period=0.2):
    """make 블록으로 변수 var 에 글을 만든 뒤, 글상자의 지금 글과 다를 때만 쓴다 (on_scene 에 붙일 블록 목록)."""
    cur = {'type': 'text_read', 'params': ['self', None]}
    return [forever(*flat(make), if_(ne(V(var), cur), write(V(var))), wait(period))]


def live_shape(o, expr, period=0.15):
    """모양 번호 expr 가 지금 모양 번호와 다를 때만 모양을 바꾼다."""
    cur = B('coordinate_object', VALUE='self', COORDINATE='picture_index')
    return [forever(if_(ne(expr, cur), shape(expr)), wait(period))]


def big_pop(P, scene, base, path, x, y, msg, hold=0.7, fade=True, then=(), pre=()):
    """신호(msg)를 받으면 튀어나오며 커졌다가 사라지는 큰 글자/그림. pre: 나타나기 전에 할 블록(모양 고르기 등)."""
    o = sprite(P, scene, base, path, x, y, visible=False)
    o.on(on_msg(msg), *flat(pre), xy(x, y), to_front(), o.pct(25), fx('transparency', 0), show(),
         rep(6, o.grow_pct(17), wait(0.016)), rep(3, o.grow_pct(-6), wait(0.016)),
         wait(hold),
         *([rep(10, fx_add('transparency', 10), mvy(1), wait(0.02)), hide()] if fade else []),
         *flat(then))
    return o


# ------------------------------------------------------------------ 화면 전환
_FX = {}         # 장면 → {'hub': 소리 담당, 'fader': 화면 전환} (둘을 오브젝트 하나로 합쳐 저장 크기를 줄임)


def fader(P, scene, black_path, first_scene=False):
    """장면 시작 시 검은 화면에서 밝아지고, '페이드아웃' 신호를 받으면 어두워진다.
    그 장면의 소리 담당이 이미 있으면 그 오브젝트가 검은 화면 모양을 갖고 전환도 맡는다."""
    fx_ = _FX.setdefault((id(P), scene), {})
    o = fx_.get('hub')
    if o is not None:
        o.pictures = [Picture('기본', black_path, scale=0.5)]
        o.x, o.y, o.visible = 0, 0, True
    else:
        o = sprite(P, scene, '전환', black_path, 0, 0)
    fx_['fader'] = o
    fade_in = [to_front(), show(), fx('transparency', 0), rep(12, fx_add('transparency', 8.5), wait(0.016)), hide()]
    o.on(on_scene(), *fade_in)
    if first_scene:
        o.on(on_run(), *fade_in)
    o.on(on_msg('페이드아웃'), to_front(), fx('transparency', 100), show(), rep(10, fx_add('transparency', -10), wait(0.016)))
    return o


def go(scene_name, delay=0.2):
    """페이드아웃 후 장면 이동."""
    return [cast('페이드아웃'), wait(delay), goto_scene(scene_name)]


# ------------------------------------------------------------------ 숫자 표시 (천 단위 쉼표)
def fmt_comma(src, dst):
    """src(숫자 블록)를 '1,234' 형태의 문자열로 변수 dst 에 넣는 블록들. 0~9,999,999 범위."""
    n = floor(abs_(src))
    pad3 = lambda v: ifelse(lt(v, 10), [setv('_p3', join('00', v))],
                            [ifelse(lt(v, 100), [setv('_p3', join('0', v))], [setv('_p3', v)])])
    return [
        setv('_n', n),
        ifelse(lt(V('_n'), 1000), [setv(dst, V('_n'))], [
            ifelse(lt(V('_n'), 1000000), [
                setv('_hi', floor(div(V('_n'), 1000))), setv('_lo', mod(V('_n'), 1000)), pad3(V('_lo')),
                setv(dst, join(V('_hi'), ',', V('_p3')))],
                [setv('_hi', floor(div(V('_n'), 1000000))), setv('_mid', floor(div(mod(V('_n'), 1000000), 1000))),
                 setv('_lo', mod(V('_n'), 1000)), pad3(V('_mid')), setv('_m3', V('_p3')), pad3(V('_lo')),
                 setv(dst, join(V('_hi'), ',', V('_m3'), ',', V('_p3')))])]),
        if_(lt(src, 0), setv(dst, join('-', V(dst)))),
    ]


def fmt_money(src, dst):
    """src(만원 단위 숫자)를 '1억 2,500만원' / '8,500만원' / '3억원' / '12조 3,456억원' 형태의 문자열로 변수 dst 에 넣는 블록들."""
    pad3 = lambda v: ifelse(lt(v, 10), [setv('_p3', join('00', v))],
                            [ifelse(lt(v, 100), [setv('_p3', join('0', v))], [setv('_p3', v)])])
    comma4 = lambda v: ifelse(lt(v, 1000), [setv('_m3', v)],
                              [pad3(mod(v, 1000)), setv('_m3', join(floor(div(v, 1000)), ',', V('_p3')))])
    return [
        setv('_n', floor(abs_(src))),
        setv('_hi', floor(div(V('_n'), 10000))),
        setv('_lo', mod(V('_n'), 10000)),
        ifelse(ge(V('_hi'), 10000),
               # 1조 이상: 'X조 Y억원' (만원 자리는 생략)
               [setv('_lo', mod(V('_hi'), 10000)), setv('_hi', floor(div(V('_hi'), 10000))), comma4(V('_lo')),
                ifelse(eq(V('_lo'), 0), [setv(dst, join(V('_hi'), '조원'))], [setv(dst, join(V('_hi'), '조 ', V('_m3'), '억원'))])],
               [comma4(V('_lo')),
                ifelse(eq(V('_hi'), 0), [setv(dst, join(V('_m3'), '만원'))],
                       [ifelse(eq(V('_lo'), 0), [setv(dst, join(V('_hi'), '억원'))],
                               [setv(dst, join(V('_hi'), '억 ', V('_m3'), '만원'))])])]),
        if_(lt(src, 0), setv(dst, join('-', V(dst)))),
    ]


def fmt_price(src, dst, short=False):
    """가격(만원 단위, 소수 가능) → 글자. long: '1억 919만원' / '1,234만원' / '97.2만원' / '800원'.
    short(시세판용): '1.4억' / '1,234만' / '97.2만' / '800원'."""
    big = ([setv(dst, join(div(rounded(div(V('_pv'), 1000)), 10), '억'))] if short else
           [setv('_ph', floor(div(V('_pv'), 10000))), setv('_pl', floor(mod(V('_pv'), 10000))),
            ifelse(eq(V('_pl'), 0), [setv(dst, join(V('_ph'), '억원'))],
                   [*fmt_comma(V('_pl'), '_pc'), setv(dst, join(V('_ph'), '억 ', V('_pc'), '만원'))])])
    unit = '만' if short else '만원'
    return [
        setv('_pv', src),
        ifelse(ge(V('_pv'), 10000), big,
               [ifelse(ge(V('_pv'), 100), [*fmt_comma(rounded(V('_pv')), '_pc'), setv(dst, join(V('_pc'), unit))],
                       [ifelse(ge(V('_pv'), 1), [setv(dst, join(div(rounded(mul(V('_pv'), 10)), 10), unit))],
                               [*fmt_comma(rounded(mul(V('_pv'), 10000)), '_pc'), setv(dst, join(V('_pc'), '원'))])])]),
    ]


def round1(e):
    """소수 첫째 자리 반올림."""
    return div(rounded(mul(e, 10)), 10)


# ------------------------------------------------------------------ 공통 HUD (재산 · 유세 진행 · 지지율)
def _compose(parts, tag, bbox=None):
    """움직이지 않는 그림·글자 조각들을 그림 한 장(2배 해상도)으로. parts: ('img', 경로, x, y, 배율) / ('text', 글, x, y, 크기, 색, 폭).
    돌려주는 값: (경로, 가운데 x, 가운데 y, bbox)"""
    import hashlib
    from PIL import Image, ImageDraw
    from art_common import font, ensure_out
    R = 2
    boxes = []
    for p in parts:
        if p[0] == 'img':
            w, h = Image.open(p[1]).size
            w, h = w * p[4] / R, h * p[4] / R
        else:
            w, h = p[6], p[4] * 1.6
        boxes.append((p[2] - w / 2, p[3] - h / 2, p[2] + w / 2, p[3] + h / 2))
    if bbox is None:
        bbox = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
    x0, y0, x1, y1 = bbox
    key = hashlib.md5(json.dumps([tag, bbox, [list(map(str, p)) for p in parts]]).encode()).hexdigest()[:12]
    out = os.path.join(ensure_out(), 'hudc_%s.png' % key)
    if not os.path.exists(out):
        im = Image.new('RGBA', (int(round((x1 - x0) * R)), int(round((y1 - y0) * R))), (0, 0, 0, 0))
        md = ImageDraw.Draw(im)
        for p in parts:
            cx, cy = (p[2] - x0) * R, (y1 - p[3]) * R
            if p[0] == 'img':
                q = Image.open(p[1]).convert('RGBA')
                if p[4] != 1:
                    q = q.resize((max(1, round(q.width * p[4])), max(1, round(q.height * p[4]))), Image.LANCZOS)
                im.alpha_composite(q, (int(round(cx - q.width / 2)), int(round(cy - q.height / 2))))
            else:
                col = p[5].lstrip('#')
                md.text((cx - p[6] / 2 * R, cy), p[1], font=font('jalnan', p[4] * R),
                        fill=tuple(int(col[i:i + 2], 16) for i in (0, 2, 4)) + (255,), anchor='lm')
        im.save(out, optimize=True)
    return out, round((x0 + x1) / 2, 2), round((y0 + y1) / 2, 2), bbox


def hud(P, scene, portraits, first_scene=False, empire=False, empire_xy=(176, -98), empire_w=124):
    """portraits: {'me':path,'u1':path,'u2':path} (원형 초상 그림)
    움직이지 않는 판·아이콘·이름은 그림 몇 장으로 합쳐 둔다 (오브젝트 수를 줄여 저장 크기를 줄임)."""
    objs = []
    rows = [('me', '나', '내지지율', 'royal', C_ACC), ('u1', '첫째', '큰A', 'red', C_RED),
            ('u2', '둘째', '큰B', 'purple', C_VIOLET)]
    multi = 'm1' in portraits
    # 재산 (왼쪽 위 구석) + 유세 진행 (재산 아래): 판·아이콘 한 장
    lp, lx, ly, _ = _compose([('img', K.panel(144, 24, 'glass'), -164, 118, 1), ('img', K.icon_img('coin', 16), -224, 118, 1),
                              ('img', K.panel(80, 22, 'glass'), -196, 95, 1), ('img', K.icon_img('ballot', 14), -224, 96, 1)],
                             'left')
    sprite(P, scene, 'HUD왼쪽판', [('기본', lp)], lx, ly)
    t = text(P, scene, 'HUD재산', '1억원', -152, 118, 11, C_WHITE, F_NUM, False, 1, w=118, h=18)
    t.on(on_scene(), *live_write(t, fmt_money(V('돈'), '돈표시'), '돈표시', 0.15))
    import data as _D
    t2 = text(P, scene, 'HUD유세', '유세 0/40', -188, 95, 11, '#FFFFFF', F_NUM, False, 1, w=56, h=16)
    t2.on(on_scene(), *live_write(t2, [setv('_hu', join('유세 ', V('유세횟수'), '/', LGET('곳수', V('단계'))))], '_hu', 0.3))
    # 지지율 (3줄, 합계 100%) + 조치원 지배 자본 지분 (1줄): 판·내 얼굴·이름·왕관·'지배' 글자 한 장
    yy3 = 123 - 3 * 15
    right = [('img', K.panel(152, 68, 'glass'), 160, 99, 1), ('img', portraits['me'], 96, 123, 0.62),
             ('text', '나', 116, 123, 9, C_ACC, 26), ('img', K.icon_img('trophy', 13), 96, yy3, 1),
             ('text', '지배', 116, yy3, 9, '#FFFFFF', 26)]
    if not multi:
        right += [('img', portraits[pk], 96, 123 - i * 15, 0.62) for i, (pk, nm, _, _, hexc) in enumerate(rows) if i] + \
                 [('text', nm, 116, 123 - i * 15, 9, hexc, 26) for i, (pk, nm, _, _, hexc) in enumerate(rows) if i]
    rp, rx, ry, _ = _compose(right, 'right')
    sprite(P, scene, 'HUD지지판', [('기본', rp)], rx, ry)
    for i, (pk, nm, var, col, hexc) in enumerate(rows):
        yy = 123 - i * 15
        if pk != 'me' and multi:
            # 군수 선거: 큰아버지 / 시장 선거: 시장 후보 / 대선: 대통령 후보 (얼굴+이름 그림, 단계마다 모양)
            n = pk[1]
            names = ['첫째' if n == '1' else '둘째', '%s번' % n, '%s번' % n]
            vs = [[('img', portraits[k], 96, yy, 0.62), ('text', names[t_], 116, yy, 9, hexc, 26)]
                  for t_, k in enumerate((pk, 'm' + n, 'p' + n))]
            bb = None
            for v in vs:
                b0 = _compose(v, 'face')[3]
                bb = b0 if bb is None else (min(bb[0], b0[0]), min(bb[1], b0[1]), max(bb[2], b0[2]), max(bb[3], b0[3]))
            cs = [_compose(v, 'face', bb) for v in vs]
            fo = sprite(P, scene, 'HUD얼굴' + pk, [(str(t_ + 1), c[0]) for t_, c in enumerate(cs)], cs[0][1], cs[0][2])
            fo.on(on_scene(), shape(V('단계')))
        bars = K.bar_set('sup11_' + col, 64, 8, col, steps=11)      # 10% 단위 (그림 수를 줄여 저장 크기를 줄임)
        b = sprite(P, scene, 'HUD막대' + pk, bars, 166, yy)
        b.on(on_scene(), *live_shape(b, add(floor(div(V(var), 10)), 1)))
        tv = text(P, scene, 'HUD값' + pk, '0%', 216, yy, 10, '#FFFFFF', F_NUM, False, 2, w=36, h=13)
        tv.on(on_scene(), *live_write(tv, [setv('_hv' + pk, join(round1(V(var)), '%'))], '_hv' + pk, 0.15))
    # 지배 자본 (내 지분, 50% 표시)
    yy = 123 - 3 * 15
    bars = K.bar_set('stake11_royal', 64, 8, 'royal', steps=11)
    b = sprite(P, scene, 'HUD지배막대', bars, 166, yy)
    b.on(on_scene(), *live_shape(b, add(floor(div(LGET('보유', 16), 10000)), 1)))
    sprite(P, scene, 'HUD지배선', K.icon_img('up', 6), 166, yy - 5)
    tv = text(P, scene, 'HUD지배값', '0%', 216, yy, 10, C_ACC, F_NUM, False, 2, w=36, h=13)
    tv.on(on_scene(), *live_write(tv, [setv('_hst', join(div(rounded(div(LGET('보유', 16), 100)), 10), '%'))], '_hst', 0.2))
    if empire:
        # 지도: 오른쪽 아래 '재벌 현황' (계열사 수, 유세마다 버는 돈)
        ex, ey = empire_xy
        ep, epx, epy, _ = _compose([('img', K.panel(empire_w, 34, 'glass'), ex, ey, 1),
                                    ('img', K.icon_img('shop', 16), ex - empire_w / 2 + 12, ey, 1)], 'empire')
        sprite(P, scene, 'HUD계열사판', [('기본', ep)], epx, epy)
        t3 = text(P, scene, 'HUD계열사', '', ex + 10, ey, 8 if empire_w < 120 else 9, '#FFFFFF', F_NUM, False, 1,
                  w=empire_w - 26, h=26)
        t3.on(on_scene(), *live_write(t3, [*fmt_money(V('주기수입'), '_m'), setv('_q', V('_m')), *fmt_money(V('계열사수입'), '_m'),
                                           setv('_hem', join('계열사 ', V('계열사수'), '/15 · 유세 +', V('_m'), '\n10초마다 +', V('_q')))],
                                      '_hem', 0.4))
    import economy as EC
    EC.ticker(P, scene)
    EC.income_pop(P, scene)
    return objs


# ------------------------------------------------------------------ 효과
def confetti(P, scene, msg, pics, count=36):
    o = sprite(P, scene, '색종이', pics, 0, 200, visible=False)
    o.local('vx', 0)
    o.local('vy', 0)
    o.local('vr', 0)
    o.on(on_msg(msg), rep(count, clone_self()))
    o.on(on_clone(), shape(rnd(1, len(pics))), xy(rnd(-230, 230), rnd(140, 220)), o.pct(rnd(60, 130)),
         setv('vx', div(rnd(-20, 20), 10)), setv('vy', div(rnd(-40, -15), 10)), setv('vr', rnd(-12, 12)),
         to_front(), show(),
         rep(150, mvx(V('vx')), mvy(V('vy')), rot_by(V('vr')), wait(0.016)), del_clone())
    return o


def sparkles(P, scene, msg, path, x, y, count=14, spread=60):
    o = sprite(P, scene, '반짝', path, x, y, visible=False)
    o.local('vx', 0)
    o.local('vy', 0)
    o.on(on_msg(msg), rep(count, clone_self()))
    o.on(on_clone(), xy(x, y), o.pct(rnd(50, 140)), setv('vx', div(rnd(-spread, spread), 10)),
         setv('vy', div(rnd(-spread, spread), 10)), fx('transparency', 0), to_front(), show(),
         rep(25, mvx(V('vx')), mvy(V('vy')), fx_add('transparency', 4), rot_by(12), wait(0.016)), del_clone())
    return o


# ------------------------------------------------------------------ 소리 (효과음 · 배경음)
SND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets_src', 'sounds')
SND_META = json.load(open(os.path.join(SND_DIR, 'sounds.json')))
SFX_NAMES = [k for k in SND_META if not k.startswith('bgm_')]


def _snd_path(name):
    return os.path.join(SND_DIR, ('sfx_' + name if not name.startswith('bgm_') else name) + '.mp3')


def _clear_dot():
    p = os.path.join(K.ensure_out(), 'clear_dot_snd.png')
    if not os.path.exists(p):
        from PIL import Image
        Image.new('RGBA', (8, 8), (0, 0, 0, 1)).save(p)
    return p


def sfx(name):
    """효과음 신호 (그 장면의 '소리' 담당이 재생)."""
    return cast('snd:' + name)


def sound_hub(P, scene, bgm=None, first_scene=False, extra_bgm=()):
    """장면마다 하나: 모든 효과음을 갖고 'snd:이름' 신호에 재생. bgm 이 있으면 장면 시작 때 반복 재생."""
    fx_ = _FX.setdefault((id(P), scene), {})
    o = fx_.get('fader')
    if o is not None:
        o.name = uname(scene, '소리')       # slim 이 '소리_' 이름으로 소리 담당을 찾는다
    else:
        o = sprite(P, scene, '소리', _clear_dot(), -300, -300)
    fx_['hub'] = o
    for k in SFX_NAMES:
        o.add_sound(k, _snd_path(k), SND_META[k])
        o.on(on_msg('snd:' + k), play(k))
    for b in ([bgm] if bgm else []) + list(extra_bgm):
        o.add_sound(b, _snd_path(b), SND_META[b])
    start = [stop_sounds()] + ([forever(play_wait(bgm))] if bgm else [])
    o.on(on_scene(), *start)
    if first_scene:
        o.on(on_run(), *start)
    return o
