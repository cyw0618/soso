# -*- coding: utf-8 -*-
"""대통령 선거 전용 미니게임 (군수 선거 게임과 모두 다른 장르). 7번 퀴즈는 군수 장면을 같이 쓰고 문제만 다르다.
게임은 games3a.py (1~10번), games3b.py (11~20번), games3c.py (21~30번), games3d.py (31~40번) 에 있다."""
from games_common import build_tier
import games3a
import games3b
import games3c
import games3d

T = 3
GAMES = {}
for _m in (games3a, games3b, games3c, games3d):
    GAMES.update(_m.GAMES)


def build_all(P, ctx):
    build_tier(P, ctx, T, GAMES)
