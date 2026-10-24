# -*- coding: utf-8 -*-
"""엔트리 블록(코드) 수 줄이기: 빌드 마지막에 쓸모없는 블록·오브젝트를 정리한다.

 1. 소리 담당 오브젝트: 그 장면에서 실제로 쓰지 않는 효과음 신호 처리(snd:이름)와 소리 파일을 뺀다.
 2. 경제 시계(10초 수입 계산)는 돈·집무 화면에서만 돌게 하고 나머지 하위 화면에서는 뺀다 (시간은 다음에 돌아오면 이어서 계산).
"""
import os
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
    # 4) 모양·소리를 id 대신 이름(글자)으로: 엔트리는 이름으로도 찾는다 → 오브젝트가 달라도 같은 코드가 되어 함수로 합칠 수 있다
    if os.environ.get('NONAMEREF') != '1':
        print('· 모양·소리 이름으로 바꾼 곳 %d개' % names_as_text(P))
    groups = analyze(P)
    if os.environ.get('SKEL') == '1':
        analyze_skeleton(P)
    if os.environ.get('NOFUNC') != '1':
        print('· 함수 %d개로 합침' % functionize(P, groups))
        if os.environ.get('NOPARAM') != '1':
            n, g = functionize_params(P)
            print('· 값만 다른 코드 %d묶음을 매개변수 함수로 합침 (전체 블록 약 %d개 줄임)' % (n, g))
            if os.environ.get('NOOUTLINE') != '1':
                for rnd_ in range(3):
                    n, g = outline_statements(P)
                    print('· 코드 속 되풀이 덩어리 %d묶음을 함수로 뺌 (전체 블록 약 %d개 줄임)' % (n, g))
                    if n == 0:
                        break
    else:
        print('· (함수 사용 안 함)')
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
        if t in UNSAFE_TYPES:
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


def _canon_lit(b, flags):
    """analyze 와 같지만 숫자·글자 값은 무시한 뼈대 (값만 다른 코드가 얼마나 있는지 보려고)."""
    if isinstance(b, Ref):
        if b[0] in ('msg', 'var', 'list', 'scene'):
            return 'R:%s:%s' % (b[0], b[1])
        flags['bad'] = True
        return 'R?'
    if isinstance(b, dict):
        t = b.get('type')
        if t in UNSAFE_TYPES or (t or '').startswith('func_'):
            flags['bad'] = True
        if t in ('number', 'text'):
            return '{%s|#}' % t
        return '{%s|%s|%s}' % (t, ','.join(_canon_lit(p, flags) for p in b.get('params', [])),
                              ';'.join(','.join(_canon_lit(s, flags) for s in st) for st in b.get('statements', [])))
    if b is None:
        return 'N'
    return repr(b)


def analyze_skeleton(P, min_blocks=6):
    from collections import defaultdict
    groups = defaultdict(list)
    for o in P.objects:
        if o.locals:
            continue
        for sc in o.scripts:
            if len(sc) < 2:
                continue
            fl = {}
            key = '|'.join(_canon_lit(b, fl) for b in sc[1:])
            if fl.get('bad'):
                continue
            n = [0]
            for b in sc[1:]:
                _walk_stmt(b, lambda x: n.__setitem__(0, n[0] + 1))
            if n[0] >= min_blocks:
                groups[key].append((o, sc, n[0]))
    saved = sum((len(v) - 1) * v[0][2] - len(v) * 3 for v in groups.values() if len(v) >= 2)
    print('· (참고) 값만 다른 코드까지 합치면 줄일 수 있는 블록 약 %d개' % saved)


# ---------------------------------------------------------------- 숫자·글자만 다른 코드 묶음 → 매개변수 있는 함수
def _all_count(b):
    """값 블록까지 모두 센 블록 수 (엔트리가 저장할 때 블록 하나마다 데이터가 붙는다)."""
    n = [0]

    def f(x):
        if isinstance(x, dict):
            n[0] += 1
    _walk(b, f)
    return n[0]


def _lit_slots(body):
    """본문에서 숫자/글자 값 블록을 차례대로 (부모 params 리스트, 인덱스) 로."""
    out = []

    def rec(b):
        if isinstance(b, dict):
            ps = b.get('params', [])
            for i, p in enumerate(ps):
                if isinstance(p, dict) and p.get('type') in ('number', 'text') and len(p.get('params', [])) == 1 \
                        and not isinstance(p['params'][0], (dict, Ref)):
                    out.append((ps, i))
                else:
                    rec(p)
            for st in b.get('statements', []):
                for x in st:
                    rec(x)
    for b in body:
        rec(b)
    return out


def functionize_params(P, max_params=24, min_gain=8):
    import copy
    from collections import defaultdict
    from entrygen import new_id
    groups = defaultdict(list)
    for o in P.objects:
        if o.locals:
            continue
        for sc in o.scripts:
            if len(sc) < 2:
                continue
            fl = {}
            key = '|'.join(_canon_lit(b, fl) for b in sc[1:])
            if fl.get('bad'):
                continue
            groups[key].append((o, sc))
    made, gain_total = 0, 0
    for key, items in groups.items():
        if len(items) < 2:
            continue
        slots = [_lit_slots(sc[1:]) for _, sc in items]
        if len({len(s) for s in slots}) != 1:
            continue
        vals = [[ps[i]['params'][0] for ps, i in s] for s in slots]
        vary = [k for k in range(len(slots[0])) if len({str(v[k]) for v in vals}) > 1]
        if not vary or len(vary) > max_params:
            continue
        body_n = sum(_all_count(b) for b in items[0][1][1:])
        gain = (len(items) - 1) * body_n - len(items) * (1 + len(vary))
        if gain < min_gain:
            continue
        ptypes = ['stringParam_' + new_id() for _ in vary]
        body = copy.deepcopy(items[0][1][1:])
        bslots = _lit_slots(body)
        for pt, k in zip(ptypes, vary):
            ps, i = bslots[k]
            ps[i] = {'type': pt, 'params': []}
        made += 1
        fid = P.new_param_function('값함수%d' % made, body, ptypes)
        for (o, sc), s in zip(items, slots):
            args = [copy.deepcopy(s[k][0][s[k][1]]) for k in vary]
            sc[1:] = [{'type': 'func_' + fid, 'params': args + [None], 'statements': []}]
        gain_total += gain
    return made, gain_total


def names_as_text(P):
    n = [0]

    def fix(b):
        if isinstance(b, dict):
            ps = b.get('params', [])
            for i, p in enumerate(ps):
                if isinstance(p, dict) and p.get('type') in ('get_pictures', 'get_sounds') and p.get('params') \
                        and isinstance(p['params'][0], Ref) and p['params'][0][0] in ('pic', 'snd'):
                    ps[i] = {'type': 'text', 'params': [str(p['params'][0][1])]}
                    n[0] += 1
                else:
                    fix(p)
            for st in b.get('statements', []):
                for x in st:
                    fix(x)
    for o in P.objects:
        for sc in o.scripts:
            for b in sc:
                fix(b)
    return n[0]


def _uses_names(b, names):
    hit = [False]

    def f(x):
        if isinstance(x, dict):
            for p in x.get('params', []):
                if isinstance(p, Ref) and p[0] == 'var' and p[1] in names:
                    hit[0] = True
    _walk(b, f)
    return hit[0]


def _has_param_ref(b):
    hit = [False]

    def f(x):
        if isinstance(x, dict) and str(x.get('type', '')).startswith('stringParam_'):
            hit[0] = True
    _walk(b, f)
    return hit[0]


def outline_statements(P, min_size=6, max_params=16):
    """스크립트 안의 문장(블록 덩어리) 가운데 모양이 같은 것(숫자·글자 값만 다름)을 모아 매개변수 함수로 뺀다."""
    import copy
    from collections import defaultdict
    from entrygen import new_id
    cands = defaultdict(list)          # key -> [(stmt_list, index, block, size)]
    parent = {}

    def visit(stmts, o):
        for i, b in enumerate(stmts):
            if not isinstance(b, dict):
                continue
            for st in b.get('statements', []):
                for x in st:
                    parent[id(x)] = id(b)
                visit(st, o)
            size = _all_count(b)
            if size < min_size:
                continue
            fl = {}
            key = _canon_lit(b, fl)
            if fl.get('bad') or _has_param_ref(b):
                continue
            if o is not None and o.locals and _uses_names(b, set(o.locals)):
                continue
            cands[key].append((stmts, i, b, size))
    for o in P.objects:
        for sc in o.scripts:
            body = sc[1:]
            # 몸통 리스트를 그대로 써야 바꿔 넣을 수 있다
            for i, b in enumerate(sc):
                if i == 0 or not isinstance(b, dict):
                    continue
                for st in b.get('statements', []):
                    for x in st:
                        parent[id(x)] = id(b)
                    visit(st, o)
                size = _all_count(b)
                if size < min_size:
                    continue
                fl = {}
                key = _canon_lit(b, fl)
                if fl.get('bad') or _has_param_ref(b) or (o.locals and _uses_names(b, set(o.locals))):
                    continue
                cands[key].append((sc, i, b, size))
    # 함수 몸통도 (지역 변수 없음)
    for f in list(P.functions):
        visit(f['body'], None)
    order = []
    for key, items in cands.items():
        if len(items) < 2:
            continue
        slots = [_lit_slots([it[2]]) for it in items]
        if len({len(x) for x in slots}) != 1:
            continue
        vals = [[ps[i]['params'][0] for ps, i in x] for x in slots]
        vary = [k for k in range(len(slots[0])) if len({str(v[k]) for v in vals}) > 1]
        if len(vary) > max_params:
            continue
        size = items[0][3]
        gain = (len(items) - 1) * size - len(items) * (1 + len(vary))
        if gain > 4:
            order.append((gain, key, items, vary))
    order.sort(key=lambda r: -r[0])
    consumed = set()

    def ancestors_consumed(b):
        x = id(b)
        while x in parent:
            x = parent[x]
            if x in consumed:
                return True
        return False

    def mark(b):
        def f(x):
            if isinstance(x, dict):
                consumed.add(id(x))
        _walk(b, f)
    made, total = 0, 0
    for gain, key, items, vary in order:
        def same(b):
            fl = {}
            k2 = _canon_lit(b, fl)
            return not fl.get('bad') and k2 == key and not _has_param_ref(b)
        live = [it for it in items if id(it[2]) not in consumed and not ancestors_consumed(it[2])
                and it[0][it[1]] is it[2] and same(it[2])]
        if len(live) < 2:
            continue
        slots = [_lit_slots([it[2]]) for it in live]
        size = live[0][3]
        g = (len(live) - 1) * size - len(live) * (1 + len(vary))
        if g <= 4:
            continue
        ptypes = ['stringParam_' + new_id() for _ in vary]
        body = copy.deepcopy(live[0][2])
        bslots = _lit_slots([body])
        for pt, k in zip(ptypes, vary):
            ps, i = bslots[k]
            ps[i] = {'type': pt, 'params': []}
        made += 1
        fid = P.new_param_function('덩어리%d' % made, [body], ptypes)
        for (stmts, i, b, _), sl in zip(live, slots):
            args = [copy.deepcopy(sl[k][0][sl[k][1]]) for k in vary]
            mark(b)
            stmts[i] = {'type': 'func_' + fid, 'params': args + [None], 'statements': []}
        total += g
    return made, total
