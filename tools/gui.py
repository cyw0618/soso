# -*- coding: utf-8 -*-
"""엔트리 오브젝트로 만드는 UI 부품 (버튼, 패널, 글자, HUD, 화면 전환, 팝업, 효과)."""
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
    """마우스를 올리면 살짝 커지고 밝아지는 효과."""
    loop = forever(ifelse(touch('mouse'), [o.pct(big), fx('brightness', 12)], [o.pct(normal), fx('brightness', 0)]),
                   wait(0.03))
    o.on(on_scene(), loop)
    if first_scene:
        o.on(on_run(), loop)


def button(P, scene, base, label, x, y, w, h, color='royal', icon=None, actions=(), hover=True, visible=True,
           first_scene=False):
    o = sprite(P, scene, base, K.button(label, w, h, color, icon=icon), x, y, visible=visible)
    if hover:
        hover_scripts(o, first_scene=first_scene)
    # 누름 효과와 동작을 따로 (빠르게 여러 번 눌러도 동작은 매번 실행)
    o.on(on_click(), o.pct(92), *flat(actions))
    o.on(on_click(), wait(0.07), o.pct(100))
    return o


def big_pop(P, scene, base, path, x, y, msg, hold=0.7, fade=True, then=()):
    """신호(msg)를 받으면 튀어나오며 커졌다가 사라지는 큰 글자/그림."""
    o = sprite(P, scene, base, path, x, y, visible=False)
    o.on(on_msg(msg), xy(x, y), to_front(), o.pct(25), fx('transparency', 0), show(),
         rep(6, o.grow_pct(17), wait(0.016)), rep(3, o.grow_pct(-6), wait(0.016)),
         wait(hold),
         *([rep(10, fx_add('transparency', 10), mvy(1), wait(0.02)), hide()] if fade else []),
         *flat(then))
    return o


# ------------------------------------------------------------------ 화면 전환
def fader(P, scene, black_path, first_scene=False):
    """장면 시작 시 검은 화면에서 밝아지고, '페이드아웃' 신호를 받으면 어두워진다."""
    o = sprite(P, scene, '전환', black_path, 0, 0)
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
    """src(만원 단위 숫자)를 '1억 2,500만원' / '8,500만원' / '3억원' 형태의 문자열로 변수 dst 에 넣는 블록들."""
    pad3 = lambda v: ifelse(lt(v, 10), [setv('_p3', join('00', v))],
                            [ifelse(lt(v, 100), [setv('_p3', join('0', v))], [setv('_p3', v)])])
    return [
        setv('_n', floor(abs_(src))),
        setv('_hi', floor(div(V('_n'), 10000))),
        setv('_lo', mod(V('_n'), 10000)),
        ifelse(lt(V('_lo'), 1000), [setv('_m3', V('_lo'))],
               [pad3(mod(V('_lo'), 1000)), setv('_m3', join(floor(div(V('_lo'), 1000)), ',', V('_p3')))]),
        ifelse(eq(V('_hi'), 0), [setv(dst, join(V('_m3'), '만원'))],
               [ifelse(eq(V('_lo'), 0), [setv(dst, join(V('_hi'), '억원'))],
                       [setv(dst, join(V('_hi'), '억 ', V('_m3'), '만원'))])]),
        if_(lt(src, 0), setv(dst, join('-', V(dst)))),
    ]


def round1(e):
    """소수 첫째 자리 반올림."""
    return div(rounded(mul(e, 10)), 10)


# ------------------------------------------------------------------ 공통 HUD (재산 · 유세 진행 · 지지율)
def hud(P, scene, portraits, first_scene=False):
    """portraits: {'me':path,'u1':path,'u2':path} (원형 초상 그림)"""
    objs = []
    # 재산 (왼쪽 위 구석)
    panel(P, scene, 'HUD재산판', -172, 118, 128, 24, 'glass')
    sprite(P, scene, 'HUD동전', K.icon_img('coin', 16), -224, 118)
    t = text(P, scene, 'HUD재산', '1억원', -160, 118, 12, C_WHITE, F_NUM, False, 1, w=100, h=18)
    t.on(on_scene(), forever(*fmt_money(V('돈'), '돈표시'), write(V('돈표시')), wait(0.1)))
    # 유세 진행 (재산 아래)
    panel(P, scene, 'HUD유세판', -196, 95, 80, 22, 'glass')
    sprite(P, scene, 'HUD투표함', K.icon_img('ballot', 14), -224, 96)
    t2 = text(P, scene, 'HUD유세', '유세 0/15', -188, 95, 11, '#FFFFFF', F_NUM, False, 1, w=56, h=16)
    t2.on(on_scene(), forever(write(join('유세 ', V('유세횟수'), '/15')), wait(0.2)))
    # 지지율 (3줄)
    panel(P, scene, 'HUD지지판', 160, 106, 152, 52, 'glass')
    rows = [('me', '나', '내지지율', 'royal', C_ACC), ('u1', '첫째', '큰A', 'red', C_RED),
            ('u2', '둘째', '큰B', 'purple', C_VIOLET)]
    for i, (pk, nm, var, col, hexc) in enumerate(rows):
        yy = 122 - i * 15
        sprite(P, scene, 'HUD얼굴' + pk, portraits[pk], 96, yy, scale=0.62)
        text(P, scene, 'HUD이름' + pk, nm, 116, yy, 9, hexc, F_NUM, False, 1, w=26, h=13)
        bars = K.bar_set('sup_' + col, 64, 8, col)
        b = sprite(P, scene, 'HUD막대' + pk, bars, 166, yy)
        b.on(on_scene(), forever(shape(add(floor(div(V(var), 2.5)), 1)), wait(0.1)))
        tv = text(P, scene, 'HUD값' + pk, '0%', 216, yy, 10, '#FFFFFF', F_NUM, False, 2, w=36, h=13)
        tv.on(on_scene(), forever(write(join(round1(V(var)), '%')), wait(0.1)))
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
