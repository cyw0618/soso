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
    if os.environ.get('NOBAKE') != '1':
        print('· 배경 바로 위의 움직이지 않는 그림 %d개를 배경 그림에 합침' % bake_static(P))
    if os.environ.get('NOHALF') != '1':
        print('· 41칸 막대 그림 %d개를 21칸으로' % halve_bars(P))
    # 2) 아무도 보내지 않는 신호 처리 지우기
    print('· 쓰이지 않는 신호 처리 %d개 삭제' % drop_dead_handlers(P))
    # 3) 경제 시계는 필요한 화면에만
    P.objects = [o for o in P.objects if not (o.name.startswith('경제시계_') and o.scene not in TICKER_KEEP)]
    # 3.5) 같은 오브젝트에서 머리(시작 조건)가 같은 코드 묶음 합치기 (앞 묶음에 기다림·반복이 없을 때만)
    if os.environ.get('NOMERGEHAT') != '1':
        print('· 같은 시작 조건 코드 묶음 합침 %d개' % merge_same_hats(P))
    # 4) 모양·소리를 id 대신 이름(글자)으로: 엔트리는 이름으로도 찾는다 → 오브젝트가 달라도 같은 코드가 되어 함수로 합칠 수 있다
    if os.environ.get('NONAMEREF') != '1':
        print('· 모양·소리 이름으로 바꾼 곳 %d개' % names_as_text(P))
    if os.environ.get('NOLOC') != '1':
        print('· 같은 모양 오브젝트 묶음의 지역 변수를 리스트 칸으로 바꿈 (오브젝트 %d개)' % locals_to_lists(P))
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
                if os.environ.get('EXPR') == '1':      # 값 함수: 엔트리에서 값이 안 나오는 경우가 있어 기본은 끔
                    n, g = outline_exprs(P)
                    print('· 되풀이되는 식 %d묶음을 값 함수로 (전체 블록 약 %d개 줄임)' % (n, g))
                if os.environ.get('NOSEQ') != '1':
                    for rnd_ in range(4):
                        n, g = outline_sequences(P)
                        print('· 되풀이되는 연속 블록 %d묶음을 함수로 뺌 (전체 블록 약 %d개 줄임)' % (n, g))
                        if n == 0:
                            break
    else:
        print('· (함수 사용 안 함)')
    if os.environ.get('NOFUNC') != '1' and os.environ.get('NOINLINE') != '1':
        n, g = inline_functions(P)
        print('· 한두 번만 부르는 작은 함수 %d개를 부르는 자리에 풀어 넣음 (전체 블록 약 %d개 줄임)' % (n, g))
    if os.environ.get('NOFUNC') != '1' and os.environ.get('NOROWS') != '1':
        n, g = args_to_lists(P)
        print('· 함수 입력값 %d개 함수를 리스트(행 번호)로 (전체 블록 약 %d개 줄임)' % (n, g))
    after = statement_count(P)
    print('· 블록 정리: %d → %d' % (before, after))


# ---------------------------------------------------------------- 그림 정리
def _obj_refs(P):
    refs = set()

    def f(b):
        if isinstance(b, dict):
            for p in b.get('params', []):
                if isinstance(p, Ref) and p[0] == 'obj':
                    refs.add(p[1])
    for o in P.objects:
        for sc in o.scripts:
            for b in sc:
                _walk(b, f)
    for fn in P.functions:
        for b in fn['body']:
            _walk(b, f)
    return refs


def bake_static(P):
    """장면에서 배경 바로 위에 차례로 쌓인 그림 오브젝트 가운데 코드가 없고 다른 코드가 가리키지도 않는 것은
    배경 그림에 미리 그려 넣고 오브젝트를 없앤다 (보이는 모습은 같고, 오브젝트 하나마다 저장 데이터가 줄어든다)."""
    import hashlib
    from collections import defaultdict
    from PIL import Image
    from entrygen import Picture
    from art_common import ensure_out
    refs = _obj_refs(P)
    by_scene = defaultdict(list)
    for o in P.objects:
        by_scene[o.scene].append(o)
    gone = set()
    for sc, objs in by_scene.items():
        bg = objs[0]
        if bg.kind != 'sprite' or not bg.pictures or len(bg.pictures) > 3 or bg.x != 0 or bg.y != 0 or bg.scale != 1:
            continue
        if any(abs(p.w * p.scale - 480) > 2 for p in bg.pictures):
            continue
        run = []
        for o in objs[1:]:
            if (o.kind == 'sprite' and not o.scripts and o.visible and o.name not in refs and len(o.pictures) == 1
                    and not o.locals and not o.sounds):
                run.append(o)
            else:
                break
        if not run:
            continue
        pics = []
        for bp in bg.pictures:
            key = hashlib.md5((bp.path + '|'.join('%s,%s,%s,%s' % (o.pictures[0].path, o.x, o.y, o.scale) for o in run)).encode()).hexdigest()[:14]
            out = os.path.join(ensure_out(), 'bake_%s.png' % key)
            src = Image.open(bp.path)
            s0 = bp.scale * bp.w / float(src.width)            # 원래 그림의 배율 (줄이기 전)
            if not os.path.exists(out):
                im = src.convert('RGBA')
                f = im.width / 480.0
                for o in run:
                    pic = o.pictures[0]
                    dw, dh = pic.w * pic.scale * o.scale * f, pic.h * pic.scale * o.scale * f
                    q = Image.open(pic.path).convert('RGBA').resize((max(1, round(dw)), max(1, round(dh))), Image.LANCZOS)
                    im.alpha_composite(q, (int(round((240 + o.x) * f - q.width / 2)), int(round((135 - o.y) * f - q.height / 2))))
                im.convert('RGB').save(out, optimize=True)
            pics.append(Picture(bp.name, out, scale=s0))
        bg.pictures = pics
        gone.update(id(o) for o in run)
    P.objects = [o for o in P.objects if id(o) not in gone]
    return len(gone)


def _halve_index(x):
    """모양 번호 식 x(1~41)를 1~21 로 바꾼다. 바꿀 수 없는 모양이면 False.
    - 숫자 n → (n-1)//2+1,  - add(floor(E), 1) → E 의 곱하기/나누기 수를 반으로 (안 되면 E/2)"""
    from entrygen import div, fmt_num
    if not isinstance(x, dict):
        return False
    ps = x.get('params', [])
    if x.get('type') == 'number':
        try:
            n = float(ps[0])
        except (TypeError, ValueError):
            return False
        ps[0] = fmt_num(int((n - 1) // 2 + 1))
        return True
    if x.get('type') == 'calc_basic' and len(ps) >= 3 and ps[1] == 'PLUS' and isinstance(ps[2], dict) \
            and ps[2].get('type') == 'number' and str(ps[2]['params'][0]) == '1' \
            and isinstance(ps[0], dict) and ps[0].get('type') == 'calc_operation' and 'floor' in ps[0].get('params', []):
        fp = ps[0]['params']
        E = fp[1]
        if isinstance(E, dict) and E.get('type') == 'calc_basic' and len(E['params']) >= 3 and isinstance(E['params'][2], dict) \
                and E['params'][2].get('type') == 'number' and E['params'][1] in ('MULTI', 'DIVIDE'):
            try:
                v = float(E['params'][2]['params'][0])
            except (TypeError, ValueError):
                v = None
            if v:
                E['params'][2]['params'][0] = fmt_num(v / 2 if E['params'][1] == 'MULTI' else v * 2)
                return True
        fp[1] = div(E, 2)
        return True
    return False


def halve_bars(P):
    """0~40 (41칸) 막대 그림을 짝수 칸만 남겨 21칸으로 (모양 번호 식도 같이 바꾼다).
    식 모양을 알 수 없거나 함수 안에서 모양을 바꾸는 막대는 그대로 둔다."""
    import copy
    names41 = ['%02d' % i for i in range(41)]
    fbody = {f['id']: f for f in P.functions}
    n = 0
    for o in P.objects:
        if o.kind != 'sprite' or [p.name for p in o.pictures] != names41:
            continue
        sites, bools, ok = [], [], [True]

        def find(b):
            if isinstance(b, dict):
                t = str(b.get('type', ''))
                if t == 'change_to_some_shape':
                    sites.append(b)
                elif t == 'boolean_basic_operator' and any(isinstance(p, dict) and p.get('type') == 'coordinate_object'
                                                           and 'picture_index' in p.get('params', []) for p in b.get('params', [])):
                    bools.append(b)
                elif t.startswith('func_') and t[5:] in fbody:
                    hit = []
                    _walk(fbody[t[5:]]['body'], lambda x: hit.append(1) if isinstance(x, dict) and x.get('type') == 'change_to_some_shape' else None)
                    if hit:
                        ok[0] = False
                elif t == 'coordinate_object' and 'picture_index' in b.get('params', []):
                    pidx.append(b)
        pidx = []
        for sc in o.scripts:
            for b in sc:
                _walk(b, find)
        if not ok[0] or not sites:
            continue
        # 모양 번호를 비교 말고 다른 데(계산 등)에 쓰면 건너뜀
        in_bool = sum(1 for b in bools for p in b['params'] if isinstance(p, dict) and p.get('type') == 'coordinate_object')
        if len(pidx) != in_bool:
            continue
        # 먼저 복사본으로 모두 바꿀 수 있는지 본다
        if not all(_halve_index(copy.deepcopy(s_['params'][0])) for s_ in sites):
            continue
        done = set()
        for s_ in sites:
            if id(s_['params'][0]) not in done:
                done.add(id(s_['params'][0]))
                _halve_index(s_['params'][0])
        for b in bools:
            for i, p in enumerate(b['params']):
                if isinstance(p, dict) and p.get('type') not in ('coordinate_object',) and id(p) not in done:
                    if isinstance(p, dict) and p.get('type') in ('calc_basic', 'number'):
                        done.add(id(p))
                        _halve_index(p)
        o.pictures = o.pictures[::2]
        n += 1
    return n


# ---------------------------------------------------------------- 지역 변수 → 리스트 칸
CLONE_TYPES = {'create_clone', 'when_clone_start', 'delete_clone', 'remove_all_clones'}


def locals_to_lists(P):
    """이름만 번호로 다른 오브젝트 묶음(같은 장면, 같은 지역 변수들)은 지역 변수 때문에 코드를 함수로 합칠 수 없다.
    지역 변수 x 를 리스트 '_칸x'의 (묶음 안 번호) 칸으로 바꾸면 코드가 숫자만 다르게 되어 함수 하나로 합쳐진다.
    복제본을 쓰는 오브젝트는 (복제본마다 지역 변수가 따로라서) 바꾸지 않는다."""
    import re
    from collections import defaultdict
    from entrygen import LGET, lst_set, add, new_id
    cloned = set()

    def find_clone_targets(b):
        if isinstance(b, dict) and b.get('type') == 'create_clone':
            for p in b.get('params', []):
                if isinstance(p, Ref) and p[0] == 'obj':
                    cloned.add(p[1])
    for o in P.objects:
        for sc in o.scripts:
            for b in sc:
                _walk(b, find_clone_targets)

    def uses_clone(o):
        hit = [False]

        def f(b):
            if isinstance(b, dict) and b.get('type') in CLONE_TYPES:
                hit[0] = True
        for sc in o.scripts:
            for b in sc:
                _walk(b, f)
        return hit[0]
    fams = defaultdict(list)
    for o in P.objects:
        if not o.locals or o.name in cloned or uses_clone(o):
            continue
        fams[(o.scene, re.sub(r'\d+', '#', o.name), tuple(sorted(o.locals)))].append(o)
    done = 0
    for (scn, base, names), objs in fams.items():
        if len(objs) < 2:
            continue
        # 지역 변수가 get/set/change 말고 다른 블록에 쓰이면 건너뜀
        ok = [True]
        nset = set(names)

        def check(b):
            if isinstance(b, dict):
                for i, p in enumerate(b.get('params', [])):
                    if isinstance(p, Ref) and p[0] == 'var' and p[1] in nset:
                        if not (i == 0 and b.get('type') in ('get_variable', 'set_variable', 'change_variable')):
                            ok[0] = False
        for o in objs:
            for sc in o.scripts:
                for b in sc:
                    _walk(b, check)
        if not ok[0]:
            continue
        lists = {}
        for nm in names:
            lname = '_칸%s_%s' % (nm, new_id())
            P.list(lname, [o.locals[nm] for o in objs])
            lists[nm] = lname
        for k, o in enumerate(objs, 1):
            def rw(b):
                if not isinstance(b, dict):
                    return b
                t = b.get('type')
                ps = b.get('params', [])
                if t in ('get_variable', 'set_variable', 'change_variable') and ps and isinstance(ps[0], Ref) \
                        and ps[0][0] == 'var' and ps[0][1] in lists:
                    ln = lists[ps[0][1]]
                    if t == 'get_variable':
                        return LGET(ln, k)
                    v = rw(ps[1])
                    if t == 'set_variable':
                        return lst_set(ln, k, v)
                    return lst_set(ln, k, add(LGET(ln, k), v))
                b['params'] = [rw(p) for p in ps]
                if b.get('statements'):
                    b['statements'] = [[rw(x) for x in st] for st in b['statements']]
                return b
            o.scripts = [[rw(b) for b in sc] for sc in o.scripts]
            o.locals = {}
        done += len(objs)
    return done


# ---------------------------------------------------------------- 같은 코드 묶음을 엔트리 '함수'로 한 번만 정의
UNSAFE_TYPES = {'when_clone_start', 'create_clone', 'delete_clone', 'remove_all_clones', 'stop_object', 'stop_repeat',
                'stop_run', 'restart_project', 'create_clone', 'when_object_click', 'when_some_key_pressed'}


_FNAMES = {}


def _fname(prefix):
    """함수 이름을 겹치지 않게 (같은 이름이 여러 개면 엔트리 편집기가 헷갈릴 수 있다)."""
    _FNAMES[prefix] = _FNAMES.get(prefix, 0) + 1
    return '%s%d' % (prefix, _FNAMES[prefix])


MIN_GAIN = int(os.environ.get('MINGAIN', '0'))      # 함수 하나로 줄이는 블록 수가 이보다 적으면 만들지 않는다


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


def analyze(P, min_blocks=3):
    from collections import defaultdict
    groups = defaultdict(list)
    for o in P.objects:
        locs = set(o.locals)
        for sc in o.scripts:
            if len(sc) < 2:
                continue
            if len(sc) == 2 and str(sc[1].get('type', '')).startswith('func_') and len(sc[1].get('params') or []) <= 1:
                continue            # 이미 함수 부르기 한 칸
            # 지역 변수를 쓰는 코드는 함수 밖에서 이름이 달라질 수 있어 제외
            if locs and any(_uses_names(b, locs) for b in sc[1:]):
                continue
            fl = {}
            key = '|'.join(_canon(b, fl) for b in sc[1:])
            if fl.get('bad'):
                continue
            n = sum(_all_count(b) for b in sc[1:])
            if n >= min_blocks:
                groups[key].append((o, sc, n))
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
        gain = (len(items) - 1) * n - len(items) - 3      # 함수 정의(머리·이름표) 몫 3
        if len(items) < 2 or gain < min_gain:
            continue
        made += 1
        body = copy.deepcopy(items[0][1][1:])
        for o, sc, _ in items:
            call = P.new_function_call(made) if False else None
        fn_call = P.new_function(_fname('공통'), body)
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
        if t in UNSAFE_TYPES or (t or '').startswith('func_') and os.environ.get('FUNCSEQ') == '0':
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


def _pcost(n_calls, n_vary):
    """매개변수 비용(블록 수): 2개 이상이면 행 번호(부를 때 1개) + 함수 안에서 리스트 읽기 식(6개씩)."""
    if n_vary <= 1:
        return n_calls * (1 + n_vary)
    return n_calls * 2 + 6 * n_vary


def functionize_params(P, max_params=60, min_gain=8):
    import copy
    from collections import defaultdict
    from entrygen import new_id
    groups = defaultdict(list)
    for o in P.objects:
        locs = set(o.locals)
        for sc in o.scripts:
            if len(sc) < 2:
                continue
            if len(sc) == 2 and str(sc[1].get('type', '')).startswith('func_'):
                continue
            if locs and any(_uses_names(b, locs) for b in sc[1:]):
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
        gain = (len(items) - 1) * body_n - _pcost(len(items), len(vary))
        if gain < max(min_gain, MIN_GAIN):
            continue
        ptypes = ['stringParam_' + new_id() for _ in vary]
        body = copy.deepcopy(items[0][1][1:])
        bslots = _lit_slots(body)
        for pt, k in zip(ptypes, vary):
            ps, i = bslots[k]
            ps[i] = {'type': pt, 'params': []}
        made += 1
        fid = P.new_param_function(_fname('값함수'), body, ptypes)
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


def outline_statements(P, min_size=4, max_params=60):
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
        gain = (len(items) - 1) * size - _pcost(len(items), len(vary))
        if gain > max(4, MIN_GAIN):
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
        g = (len(live) - 1) * size - _pcost(len(live), len(vary))
        if g <= 4:
            continue
        ptypes = ['stringParam_' + new_id() for _ in vary]
        body = copy.deepcopy(live[0][2])
        bslots = _lit_slots([body])
        for pt, k in zip(ptypes, vary):
            ps, i = bslots[k]
            ps[i] = {'type': pt, 'params': []}
        made += 1
        fid = P.new_param_function(_fname('덩어리'), [body], ptypes)
        for (stmts, i, b, _), sl in zip(live, slots):
            args = [copy.deepcopy(sl[k][0][sl[k][1]]) for k in vary]
            mark(b)
            stmts[i] = {'type': 'func_' + fid, 'params': args + [None], 'statements': []}
        total += g
    return made, total


def outline_sequences(P, max_w=24, min_size=5, max_params=60):
    """문장 목록 안에서 연달아 나오는 블록 묶음(2~max_w개)이 다른 곳에서도 같은 모양(값만 다름)으로 나오면 함수로 뺀다."""
    import copy
    from collections import defaultdict
    from entrygen import new_id
    lists = []                      # (문장 리스트, 지역 변수 이름들, 머리 블록 수)

    def collect(stmts, locs, head):
        lists.append((stmts, locs, head))
        for b in stmts[head:]:
            if isinstance(b, dict):
                for st in b.get('statements', []):
                    collect(st, locs, 0)
    for o in P.objects:
        for sc in o.scripts:
            collect(sc, set(o.locals), 1)
    for f in list(P.functions):
        collect(f['body'], set(), 0)
    info = {}                       # id(block) -> (key, size, ok)

    def binfo(b):
        k = id(b)
        if k not in info:
            if not isinstance(b, dict):
                info[k] = (None, 0, False)
            else:
                fl = {}
                key = _canon_lit(b, fl)
                ok = not fl.get('bad') and not _has_param_ref(b)
                info[k] = (key, _all_count(b), ok)
        return info[k]
    cands = defaultdict(list)       # key -> [(list, [blocks])]
    for stmts, locs, head in lists:
        n = len(stmts)
        for i in range(head, n):
            key_parts, size = [], 0
            for w in range(1, max_w + 1):
                j = i + w - 1
                if j >= n:
                    break
                b = stmts[j]
                k, sz, ok = binfo(b)
                if not ok or (locs and _uses_names(b, locs)):
                    break
                key_parts.append(k)
                size += sz
                if w >= 2 and size >= min_size:
                    cands['#'.join(key_parts)].append((stmts, stmts[i:j + 1], size))
    order = []
    for key, occ in cands.items():
        if len(occ) < 2:
            continue
        # 같은 리스트 안에서 겹치는 자리는 하나만
        seen, uniq = {}, []
        for stmts, blocks, size in occ:
            ids = [id(x) for x in blocks]
            lst = seen.setdefault(id(stmts), [])
            if any(set(ids) & set(o) for o in lst):
                continue
            lst.append(ids)
            uniq.append((stmts, blocks, size))
        if len(uniq) < 2:
            continue
        slots = [_lit_slots(blocks) for _, blocks, _ in uniq]
        if len({len(x) for x in slots}) != 1:
            continue
        vals = [[ps[i]['params'][0] for ps, i in x] for x in slots]
        vary = [k for k in range(len(slots[0])) if len({str(v[k]) for v in vals}) > 1]
        if len(vary) > max_params:
            continue
        size = uniq[0][2]
        gain = (len(uniq) - 1) * size - _pcost(len(uniq), len(vary)) - 4
        if gain > max(6, MIN_GAIN):
            order.append((gain, key, uniq, vary))
    order.sort(key=lambda r: -r[0])
    consumed = set()

    def mark(b):
        def f(x):
            if isinstance(x, dict):
                consumed.add(id(x))
        _walk(b, f)
    made, total = 0, 0
    for gain, key, uniq, vary in order:
        live = []
        for stmts, blocks, size in uniq:
            if any(id(b) in consumed for b in blocks):
                continue
            # 지금도 리스트 안에 그대로 이어서 있는지
            try:
                i0 = next(i for i, x in enumerate(stmts) if x is blocks[0])
            except StopIteration:
                continue
            if stmts[i0:i0 + len(blocks)] != blocks or any(a is not b for a, b in zip(stmts[i0:i0 + len(blocks)], blocks)):
                continue
            live.append((stmts, blocks, size))
        if len(live) < 2:
            continue
        slots = [_lit_slots(blocks) for _, blocks, _ in live]
        if len({len(x) for x in slots}) != 1:
            continue
        size = live[0][2]
        g = (len(live) - 1) * size - _pcost(len(live), len(vary)) - 4
        if g <= 6:
            continue
        ptypes = ['stringParam_' + new_id() for _ in vary]
        body = copy.deepcopy(live[0][1])
        bslots = _lit_slots(body)
        if len(bslots) != len(slots[0]):
            continue
        for pt, k in zip(ptypes, vary):
            ps, i = bslots[k]
            ps[i] = {'type': pt, 'params': []}
        made += 1
        fid = P.new_param_function(_fname('연속'), body, ptypes)
        for (stmts, blocks, _), sl in zip(live, slots):
            args = [copy.deepcopy(sl[k][0][sl[k][1]]) for k in vary]
            for b in blocks:
                mark(b)
            i0 = next(i for i, x in enumerate(stmts) if x is blocks[0])
            stmts[i0:i0 + len(blocks)] = [{'type': 'func_' + fid, 'params': args + [None], 'statements': []}]
        total += g
    return made, total


def _expr_candidates(P, min_size=5):
    """값 블록(식) 중 크기가 min_size 이상인 것: [(부모 params 리스트, 인덱스, 블록, 크기, 지역변수이름)]"""
    out = []

    def rec(b, locs):
        if not isinstance(b, dict):
            return
        ps = b.get('params', [])
        for i, p in enumerate(ps):
            if isinstance(p, dict):
                t = p.get('type', '')
                if t not in ('number', 'text') and not str(t).startswith('stringParam_') and not str(t).startswith('func_'):
                    sz = _all_count(p)
                    if sz >= min_size:
                        out.append((ps, i, p, sz, locs))
                rec(p, locs)
        for st in b.get('statements', []):
            for x in st:
                rec(x, locs)
    for o in P.objects:
        for sc in o.scripts:
            for b in sc:
                rec(b, set(o.locals))
    for f in P.functions:
        for b in f['body']:
            rec(b, set())
    return out


def analyze_exprs(P):
    from collections import defaultdict
    g = defaultdict(list)
    for ps, i, p, sz, locs in _expr_candidates(P):
        fl = {}
        k = _canon_lit(p, fl)
        if fl.get('bad') or _has_param_ref(p) or (locs and _uses_names(p, locs)):
            continue
        g[k].append((p, sz))
    gain = 0
    rows = []
    for k, items in g.items():
        if len(items) < 2:
            continue
        nl = len(_lit_slots([{'type': 'x', 'params': [items[0][0]]}]))
        gg = (len(items) - 1) * items[0][1] - len(items) * (1 + nl) - 4
        if gg > 0:
            gain += gg
            rows.append((gg, len(items), items[0][1]))
    rows.sort(reverse=True)
    print('· (참고) 되풀이되는 식을 값 함수로 바꾸면 줄일 블록 약 %d개 (겹침 포함 추정)' % gain, rows[:8])


def outline_exprs(P, max_params=12):
    """되풀이되는 식(값 블록 덩어리)을 값을 돌려주는 함수로."""
    import copy
    from collections import defaultdict
    from entrygen import new_id
    groups = defaultdict(list)
    for ps, i, p, sz, locs in _expr_candidates(P):
        fl = {}
        k = _canon_lit(p, fl)
        if fl.get('bad') or _has_param_ref(p) or (locs and _uses_names(p, locs)):
            continue
        groups[k].append((ps, i, p, sz))
    order = []
    for k, items in groups.items():
        if len(items) < 2:
            continue
        slots = [_lit_slots([{'type': 'x', 'params': [it[2]]}]) for it in items]
        if len({len(x) for x in slots}) != 1:
            continue
        vals = [[a[b]['params'][0] for a, b in x] for x in slots]
        vary = [j for j in range(len(slots[0])) if len({str(v[j]) for v in vals}) > 1]
        if len(vary) > max_params:
            continue
        g = (len(items) - 1) * items[0][3] - len(items) * (1 + len(vary)) - 4
        if g > 4:
            order.append((g, k, items, vary))
    order.sort(key=lambda r: -r[0])
    consumed = set()
    made, total = 0, 0
    for g, k, items, vary in order:
        live = []
        for ps, i, p, sz in items:
            if id(p) in consumed or i >= len(ps) or ps[i] is not p:
                continue
            fl = {}
            if _canon_lit(p, fl) != k or fl.get('bad'):
                continue
            live.append((ps, i, p, sz))
        if len(live) < 2:
            continue
        g2 = (len(live) - 1) * live[0][3] - len(live) * (1 + len(vary)) - 4
        if g2 <= 4:
            continue
        slots = [_lit_slots([{'type': 'x', 'params': [it[2]]}]) for it in live]
        ptypes = ['stringParam_' + new_id() for _ in vary]
        expr = copy.deepcopy(live[0][2])
        holder = {'type': 'x', 'params': [expr]}
        bs = _lit_slots([holder])
        for pt, j in zip(ptypes, vary):
            a, b = bs[j]
            a[b] = {'type': pt, 'params': []}
        expr = holder['params'][0]
        made += 1
        fid = P.new_value_function(_fname('식'), expr, ptypes)
        for (ps, i, p, sz), sl in zip(live, slots):
            args = [copy.deepcopy(sl[j][0][sl[j][1]]) for j in vary]

            def f(x):
                if isinstance(x, dict):
                    consumed.add(id(x))
            _walk(p, f)
            ps[i] = {'type': 'func_' + fid, 'params': args, 'statements': []}
        total += g2
    return made, total


def _is_lit(a):
    return isinstance(a, dict) and a.get('type') in ('number', 'text') and len(a.get('params', [])) == 1 \
        and not isinstance(a['params'][0], (dict, Ref))


def inline_functions(P, max_rounds=8):
    """부르는 곳이 적고 몸통이 작은 함수는 함수로 두는 것(정의 머리·이름표·부르기 블록)이 더 비싸다 → 부르는 자리에 몸통을 넣는다.
    입력값이 숫자·글자일 때만 (식이면 계산 시점이 달라질 수 있음)."""
    import copy
    made, total = 0, 0
    for _ in range(max_rounds):
        funcs = {f['id']: f for f in P.functions if f.get('value') is None}
        sites = {fid: [] for fid in funcs}

        def scan(stmts, owner):
            for b in stmts:
                if isinstance(b, dict):
                    t = str(b.get('type', ''))
                    if t.startswith('func_') and t[5:] in sites:
                        sites[t[5:]].append((stmts, b, owner))
                    for st in b.get('statements', []):
                        scan(st, owner)
        for o in P.objects:
            for sc in o.scripts:
                scan(sc, None)
        for f in P.functions:
            scan(f['body'], f['id'])
        removed, touched = set(), set()
        n_round = 0
        for fid, f in funcs.items():
            cs = sites[fid]
            if not cs or fid in touched:
                continue
            m = len(f.get('params') or [])
            if any(owner == fid for _, _, owner in cs):
                continue                    # 자기 자신을 부름
            if any(owner in removed for _, _, owner in cs):
                continue
            if any(not all(_is_lit(a) for a in c['params'][:m]) or len(c['params']) < m for _, c, _ in cs):
                continue
            body_n = sum(_all_count(b) for b in f['body'])
            c = len(cs)
            if c * body_n >= (3 + m) + body_n + c * (1 + m):
                continue
            idx = {pt: j for j, pt in enumerate(f.get('params') or [])}
            for stmts, call, owner in cs:
                args = call['params'][:m]
                body = copy.deepcopy(f['body'])

                def sub(x):
                    if isinstance(x, dict):
                        ps = x.get('params', [])
                        for i, p in enumerate(ps):
                            if isinstance(p, dict) and p.get('type') in idx:
                                ps[i] = copy.deepcopy(args[idx[p['type']]])
                            else:
                                sub(p)
                        for st in x.get('statements', []):
                            for y in st:
                                sub(y)
                for b in body:
                    sub(b)
                i0 = next(i for i, x in enumerate(stmts) if x is call)
                stmts[i0:i0 + 1] = body
                touched.add(owner)
            total += (3 + m) + body_n + c * (1 + m) - c * body_n
            removed.add(fid)
            touched.add(fid)
            n_round += 1
        if not n_round:
            break
        P.functions = [f for f in P.functions if f['id'] not in removed]
        made += n_round
    return made, total


def args_to_lists(P, min_gain=6):
    """매개변수가 2개 이상인 함수: 부를 때마다 값 블록을 여러 개 넘기는 대신, 값들을 리스트에 한 줄(행)로 저장하고
    행 번호 하나만 넘긴다. 함수 안에서는 '리스트의 (행-1)×개수+j 번째 항목'으로 읽는다.
    (값 블록 하나는 엔트리 저장 데이터에서 200바이트쯤, 리스트 항목은 십여 바이트)"""
    from entrygen import new_id, LGET, add, mul
    funcs = {f['id']: f for f in P.functions if f.get('params') and f.get('value') is None}
    calls = {fid: [] for fid in funcs}

    def scan(b):
        if isinstance(b, dict):
            t = str(b.get('type', ''))
            if t.startswith('func_') and t[5:] in calls:
                calls[t[5:]].append(b)
            for p in b.get('params', []):
                scan(p)
            for st in b.get('statements', []):
                for x in st:
                    scan(x)
    for o in P.objects:
        for sc in o.scripts:
            for b in sc:
                scan(b)
    for f in P.functions:
        for b in f['body']:
            scan(b)
    made, total = 0, 0
    for fid, f in funcs.items():
        cs = calls[fid]
        m = len(f['params'])
        if m < 2 or len(cs) < 2:
            continue
        ok = True
        for c in cs:
            args = c['params'][:m]
            if len(args) < m or any(not (isinstance(a, dict) and a.get('type') in ('number', 'text')
                                         and len(a.get('params', [])) == 1 and not isinstance(a['params'][0], (dict, Ref)))
                                    for a in args):
                ok = False
                break
        if not ok:
            continue
        uses = [0]
        pset = set(f['params'])

        def count(b):
            if isinstance(b, dict) and b.get('type') in pset:
                uses[0] += 1
        _walk(f['body'], count)
        gain = len(cs) * (m - 1) - 5 * uses[0] - 2 * (m - 1)
        if gain < min_gain:
            continue
        lname = '_인자_' + fid
        rows = []
        for c in cs:
            rows += [str(a['params'][0]) for a in c['params'][:m]]
        P.list(lname, rows)
        rp = 'stringParam_' + new_id()
        idx = {pt: j for j, pt in enumerate(f['params'], 1)}

        def repl(b):
            if isinstance(b, dict):
                ps = b.get('params', [])
                for i, p in enumerate(ps):
                    if isinstance(p, dict) and p.get('type') in idx:
                        j = idx[p['type']]
                        ps[i] = LGET(lname, add(mul({'type': rp, 'params': []}, m), j - m))
                    else:
                        repl(p)
                for st in b.get('statements', []):
                    for x in st:
                        repl(x)
        for b in f['body']:
            repl(b)
        f['params'] = [rp]
        for r, c in enumerate(cs, 1):
            tail = c['params'][m:]
            c['params'] = [{'type': 'number', 'params': [str(r)]}] + tail
        made += 1
        total += gain
    return made, total


YIELD_TYPES = {'wait_second', 'repeat_basic', 'repeat_inf', 'repeat_while_true', 'wait_until_true', 'ask_and_wait',
               'message_cast_wait', 'sound_something_wait_with_block', 'sound_from_to_and_wait', 'stop_object',
               'start_scene', 'start_neighbor_scene', 'create_clone', 'delete_clone', 'when_clone_start',
               'stop_repeat', 'continue_repeat', 'restart_project', 'stop_run', 'text_read'}


def _yields(b):
    hit = [False]

    def f(x):
        if isinstance(x, dict):
            t = str(x.get('type', ''))
            if t in YIELD_TYPES or t.startswith('func_') or 'wait' in t:
                hit[0] = True
    _walk(b, f)
    return hit[0]


def merge_same_hats(P):
    """한 오브젝트 안에서 같은 신호/같은 시작 조건의 코드 묶음이 여럿이면, 기다림이 없는 묶음들을 다른 묶음 앞에 이어 붙인다."""
    merged = 0
    for o in P.objects:
        groups = {}
        for sc in o.scripts:
            if not sc:
                continue
            h = sc[0]
            key = json_key(h)
            groups.setdefault(key, []).append(sc)
        keep = []
        done = set()
        for sc in o.scripts:
            if not sc:
                continue
            key = json_key(sc[0])
            if key in done:
                continue
            g = groups[key]
            if len(g) == 1:
                keep.append(sc)
                done.add(key)
                continue
            instant = [x for x in g if not any(_yields(b) for b in x[1:])]
            other = [x for x in g if x not in instant]
            if len(instant) + (1 if other else 0) <= 1 and len(other) <= 1:
                keep += g
                done.add(key)
                continue
            # 기다림 없는 묶음들은 하나로 합쳐 (기다림 있는 묶음이 있으면 그 중 하나의 앞에 붙인다)
            body = []
            for x in instant:
                body += x[1:]
            if other:
                first = other[0]
                new = [first[0]] + body + first[1:]
                keep.append(new)
                keep += other[1:]
            else:
                keep.append([instant[0][0]] + body)
            merged += len(instant) - (0 if other else 1)
            done.add(key)
        o.scripts = keep
    return merged


def json_key(h):
    import json as _j
    def norm(x):
        if isinstance(x, Ref):
            return ['R', x[0], x[1]]
        if isinstance(x, dict):
            return {'t': x.get('type'), 'p': [norm(p) for p in x.get('params', [])]}
        return x
    return _j.dumps(norm(h), ensure_ascii=False, sort_keys=True)
