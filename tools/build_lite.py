# -*- coding: utf-8 -*-
"""시장·대통령 선거 미니게임만 담은 가벼운 테스트용 프로젝트 (개발용).

    python3 tools/build_lite.py --dev DIR --tier 2 --games 1,2,3
      → DIR/project.json + DIR/temp/ (그 게임 장면 + 간단한 '유세 결과' 장면만)
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('FONT_DIR', os.path.join(HERE, 'fonts'))

import build_game as BG
from entrygen import *
import gui as G


def main():
    a = sys.argv
    dev = a[a.index('--dev') + 1]
    tier = int(a[a.index('--tier') + 1])
    ids = [int(x) for x in a[a.index('--games') + 1].split(',') if x.strip()]
    P = Project('테스트')
    names = BG.S_GAME2 if tier == 2 else BG.S_GAME3
    P.scene('테스트시작')
    for i in ids:
        P.scene(names[i - 1])
    P.scene(BG.S_RESULT)
    for k, v in BG.VARS.items():
        P.var(k, v)
    for v in ('내순위', '방금등록', '랭킹쪽'):
        P.var(v, 0)
    P.var('단계', tier)
    ctx = dict(vars(BG))
    ctx['P'] = P
    G.bg(P, '테스트시작', BG.BLACK)
    if tier == 2:
        import games2 as GM
    else:
        import games3 as GM
    import games_common as GC
    for i in ids:
        fn = GM.GAMES.get(i)
        if fn is None:
            GC.stub(P, ctx, tier, i)
        else:
            fn(P, ctx)
    sc = BG.S_RESULT
    G.bg(P, sc, BG.BLACK)
    t = G.text(P, sc, '결과점수', '', 0, 0, 30, '#FFFFFF', G.F_NUM, False, 0, w=300, h=40)
    t.on(on_scene(), write(join('점수 ', V('점수'))))
    import slim
    slim.apply(P)
    os.makedirs(dev, exist_ok=True)
    proj = P.write_ent(os.path.join(dev, 'lite.ent'), dev_dir=dev, fast=True)
    json.dump(proj, open(os.path.join(dev, 'project.json'), 'w'), ensure_ascii=False)
    n_blocks = sum(o['script'].count('"type"') for o in proj['objects'])
    print('lite 완료: 장면 %d, 오브젝트 %d, 블록 약 %d개' % (len(proj['scenes']), len(proj['objects']), n_blocks))


if __name__ == '__main__':
    main()
