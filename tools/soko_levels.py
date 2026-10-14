# -*- coding: utf-8 -*-
"""징검돌 놓기(소코반) 단계와 풀이 확인기. python3 soko_levels.py 로 모든 단계가 풀리는지 확인."""
from collections import deque
# '.' 땅 0, '~' 물 1, 'o' 돌 2, '#' 바위 3, 'G' 도착 4, 'P' 시작(땅)  /  5 = 물에 놓인 징검돌(지나갈 수 있음), 6 = 징검돌 위의 돌
def parse(rows):
    g = []; start = None
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            v = {'.': 0, '~': 1, 'o': 2, '#': 3, 'G': 4, 'P': 0}[ch]
            if ch == 'P': start = (r, c)
            g.append(v)
    return g, start, len(rows), len(rows[0])
def solve(rows, maxn=400000):
    g, start, R, C = parse(rows)
    init = (start, tuple(g))
    prev = {init: None}
    q = deque([init])
    D = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    while q:
        (pr, pc), cells = q.popleft()
        if cells[pr * C + pc] == 4:
            path = []
            st = ((pr, pc), cells)
            while prev[st]:
                st, mv = prev[st]
                path.append(mv)
            return path[::-1], len(prev)
        for mv, (dr, dc) in D.items():
            nr, nc = pr + dr, pc + dc
            if not (0 <= nr < R and 0 <= nc < C): continue
            t = cells[nr * C + nc]
            cl = list(cells)
            if t in (0, 4, 5):
                ns = ((nr, nc), cells)
            elif t in (2, 6):
                br, bc = nr + dr, nc + dc
                if not (0 <= br < R and 0 <= bc < C): continue
                b = cells[br * C + bc]
                if b not in (0, 1, 5): continue
                cl[nr * C + nc] = 5 if t == 6 else 0
                cl[br * C + bc] = {0: 2, 1: 5, 5: 6}[b]
                ns = ((nr, nc), tuple(cl))
            else:
                continue
            if ns not in prev:
                prev[ns] = (((pr, pc), cells), mv)
                q.append(ns)
                if len(prev) > maxn: return None, len(prev)
    return None, len(prev)
LEVELS = [
    ["....#~....",
     "....#~....",
     ".Po..~..G.",
     "....#~....",
     "....#~....",
     "....#~...."],
    ["...#~~#...",
     ".o..~~....",
     "P...~~..G.",
     ".o..~~....",
     "...#~~#...",
     "...#~~#..."],
    ["..#.~~~...",
     ".o..~#~...",
     "P.o.~#~.G.",
     "..o.~~~...",
     "#...#~~...",
     "....#~~..."],
]
if __name__ == '__main__':
    for i, L in enumerate(LEVELS):
        p, n = solve(L)
        print(i, 'moves', len(p) if p else None, ''.join(p) if p else '', 'states', n)
