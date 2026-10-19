# -*- coding: utf-8 -*-
"""엔트리 블록(코드) 수 줄이기: 빌드 마지막에 쓸모없는 블록·오브젝트를 정리한다.

 1. 소리 담당 오브젝트: 그 장면에서 실제로 쓰지 않는 효과음 신호 처리(snd:이름)와 소리 파일을 뺀다.
 2. 경제 시계(10초 수입 계산)는 돈·집무 화면에서만 돌게 하고 나머지 하위 화면에서는 뺀다 (시간은 다음에 돌아오면 이어서 계산).
"""
from entrygen import Ref

TICKER_KEEP = {'집무실', '조치원 지도', '세종시 지도', '대한민국 지도', '주식', '유세 결과', '내 회사', '기업 인수', '부동산', '작전 세력'}


def _walk(b, fn):
    if isinstance(b, dict):
        fn(b)
        for p in b.get('params', []):
            _walk(p, fn)
        for st in b.get('statements', []):
            for s in st:
                _walk(s, fn)
    elif isinstance(b, (list, tuple)) and not isinstance(b, Ref):
        for x in b:
            _walk(x, fn)


def _count(objs):
    n = 0

    def f(b):
        nonlocal n
        n += 1
    for o in objs:
        for sc in o.scripts:
            for b in sc:
                _walk_stmt(b, lambda x: None)
    return n


def _walk_stmt(b, fn):
    fn(b)
    for st in b.get('statements', []):
        for s in st:
            _walk_stmt(s, fn)


def statement_count(P):
    n = [0]

    def f(b):
        n[0] += 1
    for o in P.objects:
        for sc in o.scripts:
            for b in sc:
                _walk_stmt(b, f)
    return n[0]


def apply(P):
    before = statement_count(P)
    # 1) 장면별로 실제 쓰는 snd: 신호 모으기
    used = {}
    for o in P.objects:
        def f(b, o=o):
            if b.get('type') in ('message_cast', 'message_cast_wait'):
                v = b['params'][0] if b.get('params') else None
                if isinstance(v, Ref) and v[0] == 'msg' and v[1].startswith('snd:'):
                    used.setdefault(o.scene, set()).add(v[1])
        for sc in o.scripts:
            for b in sc:
                _walk(b, f)
    for o in P.objects:
        if not o.name.startswith('소리_'):
            continue
        keep = []
        for sc in o.scripts:
            h = sc[0] if sc else None
            v = h['params'][1] if h and h.get('type') == 'when_message_cast' and len(h['params']) > 1 else None
            # on_msg 의 VALUE 는 params[1]
            if h and h.get('type') == 'when_message_cast':
                m = [p for p in h['params'] if isinstance(p, Ref) and p[0] == 'msg']
                if m and m[0][1].startswith('snd:') and m[0][1] not in used.get(o.scene, set()):
                    continue
            keep.append(sc)
        o.scripts = keep
        refs = set()

        def g(b):
            for p in b.get('params', []):
                if isinstance(p, Ref) and p[0] == 'snd':
                    refs.add(p[1])
        for sc in o.scripts:
            for b in sc:
                _walk(b, g)
        o.sounds = [s for s in o.sounds if s.name in refs]
    # 2) 경제 시계는 필요한 화면에만
    P.objects = [o for o in P.objects if not (o.name.startswith('경제시계_') and o.scene not in TICKER_KEEP)]
    after = statement_count(P)
    print('· 블록 정리: %d → %d' % (before, after))
