# -*- coding: utf-8 -*-
"""세종시장 선거 전용 미니게임 (군수 선거 게임과 모두 다른 장르). 7번 퀴즈는 군수 장면을 같이 쓰고 문제만 다르다.
게임은 games2a.py (1~10번), games2b.py (11~20번), games2c.py (21~30번), games2d.py (31~40번) 에 있다."""
from games_common import build_tier
import games2a
import games2b
import games2c
import games2d

T = 2
GAMES = {}
for _m in (games2a, games2b, games2c, games2d):
    GAMES.update(_m.GAMES)


def build_all(P, ctx):
    build_tier(P, ctx, T, GAMES)
