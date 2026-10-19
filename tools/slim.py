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


def _hat_msg(sc):
    h = sc[0] if sc else None
    if h and h.get('type') == 'when_message_cast':
        m = [p for p in h['params'] if isinstance(p, Ref) and p[0] == 'msg']
        return m[0][1] if m else None
    return None


def drop_dead_handlers(P):
    """그 장면 오브젝트 어디서도 보내지 않는 신호를 기다리는 코드 묶음(스크립트)을 지운다."""
    cast = {}
    for o in P.objects:
        def f(b, o=o):
            if b.get('type') in ('message_cast', 'message_cast_wait'):
                v = b['params'][0] if b.get('params') else None
                if isinstance(v, Ref) and v[0] == 'msg':
                    cast.setdefault(o.scene, set()).add(v[1])
        for sc in o.scripts:
            for b in sc:
                _walk(b, f)
    n = 0
    for o in P.objects:
        keep = []
        for sc in o.scripts:
            m = _hat_msg(sc)
            if m is not None and m not in cast.get(o.scene, set()):
                n += 1
                continue
            keep.append(sc)
        o.scripts = keep
    return n


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
    # 2) 아무도 보내지 않는 신호 처리 지우기
    print('· 쓰이지 않는 신호 처리 %d개 삭제' % drop_dead_handlers(P))
    # 3) 경제 시계는 필요한 화면에만
    P.objects = [o for o in P.objects if not (o.name.startswith('경제시계_') and o.scene not in TICKER_KEEP)]
    groups = analyze(P)
    print('· 함수 %d개로 합침' % functionize(P, groups))
    after = statement_count(P)
    print('· 블록 정리: %d → %d' % (before, after))


# ---------------------------------------------------------------- 같은 코드 묶음을 엔트리 '함수'로 한 번만 정의
UNSAFE_TYPES = {'when_clone_start', 'create_clone', 'delete_clone', 'remove_all_clones', 'stop_object', 'stop_repeat',
                'stop_run', 'restart_project', 'create_clone', 'when_object_click', 'when_some_key_pressed'}


def _canon(b, flags):
    """블록을 id 없는 글자로 (장면·오브젝트마다 달라지는 참조를 쓰면 flags['bad'] 표시)."""
    if isinstance(b, Ref):
        if b[0] == 'msg' or b[0] == 'var' or b[0] == 'list' or b[0] == 'scene':
            return 'R:%s:%s' % (b[0], b[1])
        flags['bad'] = True       # 그림·소리·오브젝트 참조는 오브젝트마다 달라서 함수로 옮기지 않는다
        return 'R?'
    if isinstance(b, dict):
        t = b.get('type')
        if t in UNSAFE_TYPES or (t or '').startswith('func_'):
            flags['bad'] = True
        return '{%s|%s|%s}' % (t, ','.join(_canon(p, flags) for p in b.get('params', [])),
                              ';'.join(','.join(_canon(s, flags) for s in st) for st in b.get('statements', [])))
    if b is None:
        return 'N'
    return repr(b)


def analyze(P, min_blocks=6):
    from collections import defaultdict
    groups = defaultdict(list)
    for o in P.objects:
        if o.locals:
            # 지역 변수를 쓸 수 있는 오브젝트는 함수 밖에서 이름이 달라질 수 있어 제외
            continue
        for sc in o.scripts:
            if len(sc) < 2:
                continue
            fl = {}
            key = '|'.join(_canon(b, fl) for b in sc[1:])
            if fl.get('bad'):
                continue
            n = [0]
            for b in sc[1:]:
                _walk_stmt(b, lambda x: n.__setitem__(0, n[0] + 1))
            if n[0] >= min_blocks:
                groups[key].append((o, sc, n[0]))
    saved = 0
    rows = []
    for key, items in groups.items():
        if len(items) >= 2:
            n = items[0][2]
            saved += (len(items) - 1) * n - len(items)
            rows.append((len(items), n, items[0][0].name))
    rows.sort(key=lambda r: -(r[0] * r[1]))
    print('· 함수로 합칠 수 있는 같은 코드: 묶음 %d개, 줄일 수 있는 블록 약 %d개' % (len(rows), saved))
    print('  ', rows[:12])
    return groups


def functionize(P, groups, min_gain=3):
    """같은 코드 묶음을 엔트리 함수 하나로 만들고, 각 오브젝트에는 함수 부르기 한 칸만 남긴다."""
    import copy
    made = 0
    for key, items in groups.items():
        n = items[0][2]
        gain = (len(items) - 1) * n - len(items)
        if len(items) < 2 or gain < min_gain:
            continue
        made += 1
        body = copy.deepcopy(items[0][1][1:])
        for o, sc, _ in items:
            call = P.new_function_call(made) if False else None
        fn_call = P.new_function('공통%d' % made, body)
        for o, sc, _ in items:
            sc[1:] = [dict(fn_call)]
    return made
