# -*- coding: utf-8 -*-
"""돌발상황 / 작전 본부 / 주식 / 개표 / 랭킹 / 파산 장면."""
from entrygen import *
import gui as G


def build_all(P, ctx):
    for key in ('S_EVENT', 'S_SHOP', 'S_STOCK', 'S_VOTE', 'S_RANK', 'S_BANKRUPT'):
        sc = ctx[key]
        G.bg(P, sc, ctx['ART']('story_bg'))
        t = G.text(P, sc, '임시', sc + ' (준비 중) - 클릭하면 지도로', 0, 0, 14, '#FFFFFF', w=320, h=30, bg='#16224d')
        t.on(on_click(), *G.go(ctx['S_MAP']))
        G.fader(P, sc, ctx['BLACK'])
