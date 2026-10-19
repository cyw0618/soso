# -*- coding: utf-8 -*-
"""시장·대통령 선거 전용 미니게임 공통 도구."""
from entrygen import *
import ui_kit as K
import gui as G
from gui import text, sprite, panel, button, go, round1, F_BODY, F_NUM
from gui import C_WHITE, C_ACC, C_DIM, C_RED, C_BLUE, C_VIOLET, C_BOX
import data2 as D2
from minigames import MG, need_vars


def mg(P, ctx, tier, idx, **kw):
    kind = (D2.KIND2 if tier == 2 else D2.KIND3).get(idx)
    return MG(P, idx, ctx, tier=tier, kind=kind, **kw)


def vars_(P, *names):
    for n in names:
        if n not in P.vars:
            P.var(n, 0)


def hidden(m, base):
    return m.T(base, '', -300, -300, 8, visible=False)


def stub(P, ctx, tier, idx):
    """아직 만들지 않은 게임 자리 (클릭하면 점수)."""
    m = mg(P, ctx, tier, idx, status='준비 중')
    t = m.T('임시', '게임 준비 중 · 클릭하면 끝', 0, 0, 13, C_WHITE, F_BODY, True, 0, w=300, h=30, bg=C_BOX)
    t.on(on_click(), if_(eq(V('게임중'), 1), *m.end_blocks(rnd(50, 90))))
    m.finish('곧 새 게임이 들어와요!', '조작: 클릭')
    return True


def build_tier(P, ctx, tier, games):
    for idx in range(1, 41):
        if idx == 7 or idx in D2.REMOVED.get(tier, ()):
            continue        # 퀴즈는 군수 장면을 같이 씀 / 용량 때문에 뺀 게임
        fn = games.get(idx)
        if fn is None:
            stub(P, ctx, tier, idx)
        else:
            fn(P, ctx)


def registry():
    """게임 모음 하나: (GAMES 사전, @game(번호) 장식자)."""
    games = {}

    def game(idx):
        def deco(fn):
            games[idx] = fn
            return fn
        return deco
    return games, game
