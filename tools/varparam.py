# -*- coding: utf-8 -*-
"""변수까지 매개변수로: 모양이 같고 '어떤 변수를 쓰는지'만 다른 코드 덩어리를 함수 하나로 묶는다.

slim 의 묶기는 숫자·글자 값만 매개변수로 바꾼다. 엔트리 함수는 변수 자체를 넘겨받을 수 없으므로
  - 덩어리 안에서 읽기만 하는 변수   → 부를 때 그 변수의 '값'을 넘긴다
  - 덩어리 안에서 바꾸는 변수        → 함수 전용 임시 변수에 계산한 뒤, 부른 자리에서 원래 변수에 되돌려 넣는다
                                      (덩어리가 그 변수를 먼저 읽거나 모든 경우에 정하지 않으면 처음 값도 넘긴다)
안전 조건 (하나라도 어기면 묶지 않음):
  - 덩어리에 기다림이 없다 (기다리기·반복·묻기·실시간 리스트/변수 쓰기·기다림 있는 함수 부르기) → 중간에 다른 코드가 끼어들지 않음
  - 덩어리 안에서 부르는 함수가, 바뀌는 변수를 쓰지 않고 / 덩어리가 바꾸는 변수를 읽지 않는다
  - 같은 변수가 들어간 자리 무늬가 모든 곳에서 같다 (A=A+1 과 B=C+1 은 다른 모양)
임시 변수는 '얼마나 깊이 겹쳐 부르는가'에 따라 나눠 쓴다 (안쪽 함수와 바깥 함수가 같은 임시 변수를 쓰지 않게).
"""
import collections
import copy

import entrygen as EG
from entrygen import Ref

YIELD = {'wait_second', 'repeat_basic', 'repeat_inf', 'repeat_while_true', 'wait_until_true', 'ask_and_wait',
         'message_cast_wait', 'locate_xy_time', 'move_xy_time', 'locate_object_time', 'rotate_by_time',
         'direction_relative_duration', 'dialog_time', 'sound_something_wait_with_block',
         'sound_from_to_and_wait', 'sound_something_second_wait_with_block', 'get_canvas_input_value'}
UNSAFE = {'when_clone_start', 'create_clone', 'delete_clone', 'remove_all_clones', 'stop_object', 'stop_repeat',
          'continue_repeat', 'start_scene', 'start_neighbor_scene', 'stop_run', 'restart_project',
          'get_func_variable', 'set_func_variable', 'change_func_variable'}
LISTMOD = {'add_value_to_list', 'remove_value_from_list', 'insert_value_to_list', 'change_value_list_index'}
VW = {'set_variable', 'change_variable'}
TMP = '§tmp:'          # 임시 변수 자리표 (마지막에 실제 변수 id 로 바꾼다)


def _walk(x, fn):
    if isinstance(x, dict):
        fn(x)
        for q in x.get('params') or []:
            _walk(q, fn)
        for st in x.get('statements') or []:
            for s in st:
                _walk(s, fn)
    elif isinstance(x, list):
        for q in x:
            _walk(q, fn)


def _size(b):
    n = [0]
    _walk(b, lambda x: n.__setitem__(0, n[0] + (1 if 'type' in x else 0)))
    return n[0]


def resolve_refs(RP):
    """DSL 로 넣은 코드의 이름 참조(Ref)를 원본 id 로 (변수·리스트·신호)."""
    def fix(x):
        if isinstance(x, dict):
            ps = x.get('params') or []
            for i, q in enumerate(ps):
                if isinstance(q, Ref):
                    try:
                        ps[i] = RP._ref(q)
                    except KeyError:
                        pass
                else:
                    fix(q)
            for st in x.get('statements') or []:
                for s in st:
                    fix(s)
    for o in RP.objects:
        for sc in o.scripts:
            for b in sc:
                fix(b)
    for f in RP.functions:
        for b in f.get('body') or []:
            fix(b)
        if isinstance(f.get('value'), dict):
            fix(f['value'])


class VarParam:
    def __init__(self, RP, max_w=8, min_gain=3, max_params=40):
        self.RP = RP
        self.max_w, self.min_gain, self.max_params = max_w, min_gain, max_params
        proj = RP.proj
        self.scal = {v['id'] for v in proj['variables'] if v.get('variableType') == 'variable'
                     and not v.get('object') and not v.get('isRealTime') and not v.get('isCloud')}
        self.scal |= {vid for vid, _ in RP.new_vars.values()}
        self.rt = {v['id'] for v in proj['variables'] if v.get('isRealTime') or v.get('isCloud')}
        self.made = []          # 만든 함수 id
        self.tmps = {}          # 함수 id -> 임시 자리표 목록

    # ---- 블록 성질
    def _is_tmp(self, s):
        return isinstance(s, str) and s.startswith(TMP)

    def _yields(self, b):
        t = b.get('type', '')
        if t in YIELD:
            return True
        ps = b.get('params') or []
        if t in LISTMOD and any(isinstance(q, str) and q in self.rt for q in ps):
            return True
        if t in VW and ps and ps[0] in self.rt:
            return True
        return False

    def func_info(self):
        """함수마다 읽는 변수·쓰는 변수·기다림 여부 (부르는 함수까지 따라가서)."""
        info = {}
        for f in self.RP.functions:
            if f.get('value') == 'RAW':
                info[f['id']] = [set(), set(), True, set()]
                continue
            r, w, y, c = set(), set(), [False], set()

            def fn(b):
                t = b.get('type', '')
                ps = b.get('params') or []
                if t == 'get_variable' and ps:
                    r.add(ps[0])
                if t in VW and ps:
                    w.add(ps[0])
                    if t == 'change_variable':
                        r.add(ps[0])
                if self._yields(b):
                    y[0] = True
                if t.startswith('func_'):
                    c.add(t[5:])
            _walk(f.get('body') or [], fn)
            if isinstance(f.get('value'), dict):
                _walk(f['value'], fn)
            info[f['id']] = [r, w, y[0], c]
        changed = True
        while changed:
            changed = False
            for fid, (r, w, y, c) in info.items():
                for g in list(c):
                    if g not in info:
                        continue
                    gr, gw, gy, _ = info[g]
                    if not gr <= r or not gw <= w or (gy and not y):
                        r |= gr
                        w |= gw
                        if gy:
                            info[fid][2] = True
                        changed = True
        self.info = info

    # ---- 모양 + 자리 (같은 순서로 두 번 쓰임: 모양 계산 / 함수 몸통 고치기)
    def walk_slots(self, b, cb, parent=None, idx=None, st=None):
        """b 의 모양 글자를 돌려주고, 자리(값·변수)를 만날 때마다 cb(kind, container, index, block) 를 부른다."""
        if not isinstance(b, dict):
            return repr(b)
        t = b.get('type')
        if t in ('number', 'text') and len(b.get('params') or []) >= 1 and not isinstance(b['params'][0], dict):
            cb('lit', parent, idx, b)
            return '#'
        ps = b.get('params') or []
        if t == 'get_variable' and ps and isinstance(ps[0], str) and ps[0] in self.scal:
            cb('read', parent, idx, b)
            return 'V'
        if st is not None:
            if t in YIELD or t in UNSAFE or self._yields(b) or str(t).startswith(('stringParam', 'booleanParam')):
                st['bad'] = True
            if str(t).startswith('func_'):
                st['calls'].add(t[5:])
            for q in ps:
                if self._is_tmp(q):
                    st['tmps'].add(q[len(TMP):].split(':')[0])
        parts = []
        for i, q in enumerate(ps):
            if i == 0 and t in VW and isinstance(q, str) and q in self.scal:
                cb('write' if t == 'set_variable' else 'rw', b, 0, b)
                parts.append('V')
            elif isinstance(q, dict):
                parts.append(self.walk_slots(q, cb, ps, i, st))
            else:
                parts.append(repr(q))
        ss = []
        for stl in b.get('statements') or []:
            ss.append(','.join(self.walk_slots(s, cb, stl, j, st) for j, s in enumerate(stl)))
        return '%s(%s){%s}' % (t, ','.join(parts), ';'.join(ss))

    def stmt_info(self, b):
        k = id(b)
        if k in self.cache:
            return self.cache[k]
        slots = []
        st = {'bad': False, 'calls': set(), 'tmps': set()}

        def cb(kind, cont, i, blk):
            if kind == 'lit':
                slots.append(('lit', str(blk['params'][0]), None))
            else:
                slots.append(('var', blk['params'][0], kind))
        if not isinstance(b, dict):
            r = (None, (), True, set(), 0, set())
        else:
            sig = self.walk_slots(b, cb, st=st)
            r = (sig, tuple(slots), st['bad'], st['calls'], _size(b), st['tmps'])
        self.cache[k] = r
        return r

    # ---- 후보 모으기
    def collect_lists(self):
        lists = []
        self.anc = {}

        def coll(stmts, head, anc, owner):
            lists.append((stmts, head, owner))
            self.anc[id(stmts)] = anc
            for b in stmts[head:]:
                if isinstance(b, dict):
                    for stl in b.get('statements') or []:
                        coll(stl, 0, anc + (id(b),), owner)
        for o in self.RP.objects:
            for sc in o.scripts:
                if sc:
                    coll(sc, 1, (), None)
        for f in self.RP.functions:
            if f.get('value') == 'RAW':
                continue
            coll(f['body'], 0, (), f['id'])
        return lists

    def candidates(self):
        self.cache = {}
        groups = collections.defaultdict(list)
        for L, head, owner in self.collect_lists():
            n = len(L)
            for i in range(head, n):
                sigs, slots, calls, tot = [], [], set(), 0
                for w in range(1, self.max_w + 1):
                    if i + w > n:
                        break
                    b = L[i + w - 1]
                    sig, sl, bad, cl, sz, tm = self.stmt_info(b)
                    tail = False
                    if bad and w > 1 and self._tail_wait(b):
                        tail = True          # 맨 끝의 '기다리기(숫자)'는 함수 안으로 넣어도 같다 (바꾸는 변수 없을 때만)
                    elif bad or sig is None or (tm and tm != {owner}):
                        break
                    sigs.append(sig)
                    slots.extend(sl)
                    calls |= cl
                    tot += sz
                    if tot >= 4:
                        vs = [s[1] for s in slots if s[0] == 'var']
                        if vs:
                            pat = tuple(vs.index(v) for v in vs)
                            groups[('|'.join(sigs), pat, tail)].append((L, i, w, tot, tuple(slots), frozenset(calls),
                                                                       tuple(L[i:i + w])))
                    if tail:
                        break
        return groups

    @staticmethod
    def _tail_wait(b):
        if not isinstance(b, dict) or b.get('type') != 'wait_second':
            return False
        a = (b.get('params') or [None])[0]
        return isinstance(a, dict) and a.get('type') in ('number', 'text') and not isinstance((a.get('params') or [None])[0], dict)

    # ---- 한 묶음 평가
    def plan(self, key, occ):
        slots0 = occ[0][4]
        nsl = len(slots0)
        lit_vary = [j for j in range(nsl) if slots0[j][0] == 'lit' and len({o[4][j][1] for o in occ}) > 1]
        var_slots = [j for j in range(nsl) if slots0[j][0] == 'var']
        pat = key[1]
        classes = collections.OrderedDict()           # 대표 자리 번호 -> [자리들]
        for k, j in enumerate(var_slots):
            classes.setdefault(pat[k], []).append(j)
        vary_cls = []
        for c, js in classes.items():
            j0 = js[0]
            if len({o[4][j0][1] for o in occ}) > 1:
                roles = {slots0[j][2] for j in js}
                vary_cls.append((c, js, roles))
        if not vary_cls:
            return None
        wcls = [x for x in vary_cls if x[2] & {'write', 'rw'}]
        rcls = [x for x in vary_cls if not (x[2] & {'write', 'rw'})]
        # 부르는 함수와 겹침 검사
        ok = []
        for o in occ:
            vv = {o[4][js[0]][1] for _, js, _ in vary_cls}
            wv = {o[4][js[0]][1] for _, js, _ in wcls}
            bad = False
            for g in o[5]:
                gi = self.info.get(g)
                if gi is None or gi[2] or (gi[1] & vv) or (gi[0] & wv):
                    bad = True
                    break
            if not bad:
                ok.append(o)
        return lit_vary, vary_cls, wcls, rcls, ok

    def needs_init(self, tmpl_stmts, cls_js, slots_pos):
        """임시 변수에 처음 값을 넘겨야 하나: 덩어리가 그 변수를 읽거나(바꾸기 포함), 모든 경우에 정하지는 않으면."""
        roles = {slots_pos[j][0] for j in cls_js}
        if 'read' in roles or 'rw' in roles:
            return True
        wblocks = {id(slots_pos[j][3]) for j in cls_js if slots_pos[j][0] == 'write'}

        def dw_list(stmts):
            return any(dw(b) for b in stmts)

        def dw(b):
            if not isinstance(b, dict):
                return False
            if b.get('type') == 'set_variable' and id(b) in wblocks:
                return True
            if b.get('type') == 'if_else':
                sts = b.get('statements') or [[], []]
                return dw_list(sts[0]) and dw_list(sts[1] if len(sts) > 1 else [])
            return False
        return not dw_list(tmpl_stmts)

    def cost(self, sz, n, n_lit, n_r, n_init, form):
        np_ = n_lit + n_r + n_init
        body = sz + 2 + 2 * np_ + 2 * n_init + (1 if form == 'value' else 0)
        per = (2 if form == 'value' else 1) + np_
        return n * sz - body - n * per

    @staticmethod
    def non_overlap(occ):
        """같은 목록 안에서 겹치는 자리는 앞의 것만 (이득을 부풀려 세지 않게)."""
        out, last = [], {}
        for o in sorted(occ, key=lambda o: (id(o[0]), o[1])):
            k = id(o[0])
            if k in last and o[1] < last[k]:
                continue
            last[k] = o[1] + o[2]
            out.append(o)
        return out

    @staticmethod
    def form_of(wcls):
        return 'plain' if not wcls else ('value' if len(wcls) == 1 else None)

    def run_round(self):
        self.func_info()
        groups = self.candidates()
        order = []
        for key, occ in groups.items():
            if len(occ) < 2:
                continue
            occ = self.non_overlap(occ)
            if len(occ) < 2:
                continue
            pl = self.plan(key, occ)
            if pl is None:
                continue
            lit_vary, vary_cls, wcls, rcls, ok = pl
            form = self.form_of(wcls)
            if form is None or len(ok) < 2 or (key[2] and form != 'plain'):
                continue
            g = self.cost(ok[0][3], len(ok), len(lit_vary), len(rcls), len(wcls), form)
            if g >= self.min_gain:
                order.append((g, key, ok))
        order.sort(key=lambda x: -x[0])
        consumed = set()
        total, made = 0, 0
        for g0, key, occ in order:
            live = []
            seen = set()
            for o in occ:
                L, i, w, tot, slots, calls, blocks = o
                if any(id(b) in consumed for b in blocks):
                    continue
                ids = {id(b) for b in blocks}
                if ids & seen:          # 같은 목록 안에서 겹치는 자리
                    continue
                try:
                    i2 = next(k for k, x in enumerate(L) if x is blocks[0])
                except StopIteration:
                    continue
                if i2 + w > len(L) or any(L[i2 + k] is not blocks[k] for k in range(w)):
                    continue
                seen |= ids
                live.append(o)
            if len(live) < 2:
                continue
            pl = self.plan(key, live)
            if pl is None:
                continue
            lit_vary, vary_cls, wcls, rcls, live = pl
            form = self.form_of(wcls)
            if form is None or len(live) < 2 or (key[2] and form != 'plain'):
                continue
            if len(lit_vary) + len(rcls) + len(wcls) > self.max_params:
                continue
            # 본보기 덩어리 (첫 자리) 복사 → 자리 위치
            tmpl = copy.deepcopy(list(live[0][6]))
            pos = []

            def cb(kind, cont, i, blk):
                pos.append((kind, cont, i, blk))
            for b in tmpl:
                self.walk_slots(b, cb)
            if len(pos) != len(live[0][4]):
                continue
            inits = [self.needs_init(tmpl, js, pos) for (_, js, _) in wcls]
            g = self.cost(live[0][3], len(live), len(lit_vary), len(rcls), sum(inits), form)
            if g < self.min_gain:
                continue
            fid = EG.new_id()
            ptypes = []
            for j in lit_vary:                                  # 1) 값 자리
                pt = 'stringParam_' + EG.new_id()
                ptypes.append(pt)
                kind, cont, i, blk = pos[j]
                cont[i] = {'type': pt, 'params': []}
            for (_, js, _) in rcls:                             # 2) 읽기만 하는 변수 → 값으로
                pt = 'stringParam_' + EG.new_id()
                ptypes.append(pt)
                for j in js:
                    kind, cont, i, blk = pos[j]
                    cont[i] = {'type': pt, 'params': []}
            pre, value, tnames = [], None, []
            if form == 'value':                                 # 3) 바꾸는 변수 하나 → 임시 변수, 함수 값으로 돌려줌
                (_, js, _), ini = wcls[0], inits[0]
                tn = '%s%s:0' % (TMP, fid)
                tnames.append(tn)
                for j in js:
                    kind, cont, i, blk = pos[j]
                    blk['params'][0] = tn
                if ini:
                    pt = 'stringParam_' + EG.new_id()
                    ptypes.append(pt)
                    pre.append({'type': 'set_variable', 'params': [tn, {'type': pt, 'params': []}, None],
                                'statements': []})
                value = {'type': 'get_variable', 'params': [tn, None]}
            f = dict(id=fid, name='변수묶음%d' % (len(self.made) + 1), body=pre + tmpl, params=ptypes)
            if value is not None:
                f['value'] = value
            self.RP.functions.append(f)
            self.made.append(fid)
            self.tmps[fid] = tnames
            for o in live:
                L, i, w, tot, slots, calls, blocks = o
                lit_blocks = []

                def lb(kind, cont, i_, blk):
                    lit_blocks.append(blk)
                for b in blocks:
                    self.walk_slots(b, lb)
                args = [copy.deepcopy(lit_blocks[j]) for j in lit_vary]   # 값 블록 그대로 (number/text 유지)
                for (_, js, _) in rcls:
                    args.append({'type': 'get_variable', 'params': [slots[js[0]][1], None]})
                if form == 'value':
                    (_, js, _) = wcls[0]
                    wv = slots[js[0]][1]
                    if inits[0]:
                        args.append({'type': 'get_variable', 'params': [wv, None]})
                    new = [{'type': 'set_variable', 'params': [wv, {'type': 'func_' + fid, 'params': args},
                                                               None], 'statements': []}]
                else:
                    new = [{'type': 'func_' + fid, 'params': args + [None], 'statements': []}]
                i2 = next(k for k, x in enumerate(L) if x is blocks[0])
                L[i2:i2 + w] = new
                for b in blocks:
                    _walk(b, lambda x: consumed.add(id(x)))
                consumed.update(self.anc.get(id(L), ()))     # 바깥 블록은 모양이 바뀜 → 이번 판에서 다른 묶음에 쓰지 않기
            total += g
            made += 1
        return made, total

    # ---- 임시 변수 정하기 (깊이별로 나눠 쓰기)
    def finish(self):
        calls = {}
        for f in self.RP.functions:
            c = set()
            _walk(f.get('body') or [], lambda b: c.add(b['type'][5:]) if str(b.get('type', '')).startswith('func_') else None)
            if isinstance(f.get('value'), dict):
                _walk(f['value'], lambda b: c.add(b['type'][5:]) if str(b.get('type', '')).startswith('func_') else None)
            calls[f['id']] = c
        made = set(self.made)
        memo = {}

        def depth(fid, stack=()):
            if fid in memo:
                return memo[fid]
            if fid in stack:
                return 0
            d = 0
            for g in calls.get(fid, ()):
                d = max(d, depth(g, stack + (fid,)))
            if fid in made:
                d += 1
            memo[fid] = d
            return d
        mapping = {}
        pool = {}
        for fid in self.made:
            d = depth(fid)
            for k, tn in enumerate(self.tmps[fid]):
                name = '_vp%d_%d' % (d, k)
                if name not in pool:
                    vid = EG.new_id()
                    self.RP.new_vars[name] = (vid, 0)
                    pool[name] = vid
                mapping[tn] = pool[name]

        def fix(b):
            ps = b.get('params') or []
            for i, q in enumerate(ps):
                if isinstance(q, str) and q in mapping:
                    ps[i] = mapping[q]
        for o in self.RP.objects:
            for sc in o.scripts:
                _walk(sc, fix)
        for f in self.RP.functions:
            _walk(f.get('body') or [], fix)
            if isinstance(f.get('value'), dict):
                _walk(f['value'], fix)
        return len(pool)


def run(RP, rounds=6, log=print):
    import os
    resolve_refs(RP)
    vp = VarParam(RP, max_w=int(os.environ.get('VP_W', '8')))
    for r in range(rounds):
        made, gain = vp.run_round()
        log('· 변수까지 매개변수로: 함수 %d개 (약 %d블록)' % (made, gain))
        if made == 0:
            break
    n = vp.finish()
    log('· 임시 변수 %d개' % n)
    return vp


# ---------------------------------------------------------------- 매개변수 정리
_PURE = {'number', 'text', 'get_variable', 'calc_basic', 'calc_operation', 'combine_something',
         'value_of_index_from_list', 'length_of_list', 'quotient_and_mod', 'boolean_basic_operator',
         'boolean_and_or', 'boolean_not', 'length_of_string', 'char_at', 'substring', 'True', 'False'}


def _pure(b):
    ok = [True]

    def f(x):
        t = x.get('type', '')
        if t not in _PURE and not t.startswith(('stringParam_', 'booleanParam_')):
            ok[0] = False
    _walk(b, f)
    return ok[0]


def _key(b):
    if isinstance(b, dict):
        return '%s(%s){%s}' % (b.get('type'), ','.join(_key(x) for x in b.get('params') or []),
                               ';'.join(','.join(_key(s) for s in st) for st in b.get('statements') or []))
    return repr(b)


def tidy_params(RP, log=print):
    """매개변수 함수에서
      - 모든 부르는 곳에서 늘 같은 값끼리 넘겨지는 매개변수 → 하나로 합침
      - 모든 부르는 곳에서 같은 숫자·글자 하나만 받는 매개변수 → 함수 안에 그 값을 바로 넣고 지움"""
    funcs = {f['id']: f for f in RP.functions if f.get('params') and f.get('value') != 'RAW'}
    calls = {fid: [] for fid in funcs}

    def scan(b):
        if isinstance(b, dict):
            t = str(b.get('type', ''))
            if t.startswith('func_') and t[5:] in calls:
                calls[t[5:]].append(b)
            for q in b.get('params') or []:
                scan(q)
            for st in b.get('statements') or []:
                for x in st:
                    scan(x)
    for o in RP.objects:
        for sc in o.scripts:
            for b in sc:
                scan(b)
    for f in RP.functions:
        for b in f.get('body') or []:
            scan(b)
        if isinstance(f.get('value'), dict):
            scan(f['value'])
    merged = consts = 0
    for fid, f in funcs.items():
        cs = calls[fid]
        m = len(f['params'])
        if not cs or any(len(c.get('params') or []) < m for c in cs):
            continue
        keys = [[_key(c['params'][j]) for j in range(m)] for c in cs]
        repl = {}            # 매개변수 블록 종류 → 바꿀 블록
        drop = set()
        for j in range(m):
            if j in drop:
                continue
            col = [k[j] for k in keys]
            a0 = cs[0]['params'][j]
            # 1) 모든 곳에서 같은 값 하나 (숫자·글자)
            if len(set(col)) == 1 and isinstance(a0, dict) and a0.get('type') in ('number', 'text') \
                    and not isinstance((a0.get('params') or [None])[0], dict):
                repl[f['params'][j]] = a0
                drop.add(j)
                consts += 1
                continue
            # 2) 뒤의 매개변수가 늘 이것과 같은 값 → 합침
            if not all(_pure(c['params'][j]) for c in cs):
                continue
            for j2 in range(j + 1, m):
                if j2 in drop:
                    continue
                if all(k[j2] == k[j] for k in keys):
                    repl[f['params'][j2]] = {'type': f['params'][j], 'params': []}
                    drop.add(j2)
                    merged += 1
        if not drop:
            continue

        def sub(b):
            if isinstance(b, dict):
                ps = b.get('params') or []
                for i, q in enumerate(ps):
                    if isinstance(q, dict) and q.get('type') in repl:
                        ps[i] = copy.deepcopy(repl[q['type']])
                    else:
                        sub(q)
                for st in b.get('statements') or []:
                    for x in st:
                        sub(x)
        for b in f['body']:
            sub(b)
        if isinstance(f.get('value'), dict):
            if f['value'].get('type') in repl:
                f['value'] = copy.deepcopy(repl[f['value']['type']])
            else:
                sub(f['value'])
        keep = [j for j in range(m) if j not in drop]
        f['params'] = [f['params'][j] for j in keep]
        if not f['params'] and f.get('value') == 'USER':
            f['value'] = None
        for c in cs:
            tail = c['params'][m:]
            c['params'] = [c['params'][j] for j in keep] + tail
    log('· 늘 같은 값끼리 넘기는 매개변수 %d개 합침, 늘 같은 값인 매개변수 %d개 없앰' % (merged, consts))
    return merged, consts


def inline_small(RP, log=print, rounds=6):
    """함수로 두는 것보다 부르는 자리에 풀어 넣는 쪽이 블록이 적으면 풀어 넣는다.
    넘기는 값이 숫자·글자·(부른 함수의) 매개변수이거나, 함수 안에서 바꾸지 않는 변수 읽기일 때만
    (그 함수에 기다림이 없을 때) — 그래야 '부를 때 계산한 값'과 '풀어 넣은 자리에서 읽은 값'이 같다."""
    total = made = 0
    for _ in range(rounds):
        vp = VarParam(RP)
        vp.func_info()
        NOINL = {'stop_repeat', 'continue_repeat', 'stop_object', 'stop_run', 'restart_project'}

        def plain_ok(f):
            hit = [False]
            _walk(f.get('body') or [], lambda x: hit.__setitem__(0, True) if x.get('type') in NOINL else None)
            return not hit[0]
        funcs = {f['id']: f for f in RP.functions
                 if f.get('value') in (None, 'USER') and f.get('body') is not None and plain_ok(f)}
        sites = {fid: [] for fid in funcs}

        def scan(stmts, owner):
            for i, b in enumerate(stmts):
                if isinstance(b, dict):
                    t = str(b.get('type', ''))
                    if t.startswith('func_') and t[5:] in sites:
                        sites[t[5:]].append((stmts, b, owner))
                    for st in b.get('statements') or []:
                        scan(st, owner)

        def scan_expr(x, owner, bad):
            # 값 자리에서 부르는 것(값 함수 아님)이 있으면 풀 수 없음 표시
            if isinstance(x, dict):
                t = str(x.get('type', ''))
                if t.startswith('func_') and t[5:] in sites:
                    bad.add(t[5:])
                for q in x.get('params') or []:
                    scan_expr(q, owner, bad)
                for st in x.get('statements') or []:
                    for s in st:
                        for q in s.get('params') or []:
                            scan_expr(q, owner, bad)
        bad_expr = set()
        for o in RP.objects:
            for sc in o.scripts:
                scan(sc, None)
                for b in sc:
                    if isinstance(b, dict):
                        for q in b.get('params') or []:
                            scan_expr(q, None, bad_expr)
        for f in RP.functions:
            scan(f.get('body') or [], f['id'])
        n_round = 0
        removed = set()
        touched = set()
        for fid, f in funcs.items():
            cs = sites[fid]
            if not cs or fid in bad_expr or fid in touched:
                continue
            if any(owner == fid or owner in removed for _, _, owner in cs):
                continue
            ptypes = list(f.get('params') or [])
            m = len(ptypes)
            info = vp.info.get(fid)
            if info is None:
                continue
            fr, fw, fy, _ = info
            uses = collections.Counter()
            _walk(f['body'], lambda x: uses.__setitem__(x['type'], uses[x['type']] + 1) if x.get('type') in ptypes else None)

            def safe(a):
                if not isinstance(a, dict):
                    return a is None
                t = a.get('type', '')
                if t in ('number', 'text') and not isinstance((a.get('params') or [None])[0], dict):
                    return True
                if t.startswith(('stringParam_', 'booleanParam_')):
                    return True
                if t == 'get_variable' and not fy:
                    v = (a.get('params') or [None])[0]
                    return isinstance(v, str) and v not in fw and not v.startswith(TMP)
                return False
            ok = all(len(c.get('params') or []) >= m and all(safe(a) for a in c['params'][:m]) for _, c, _ in cs)
            if not ok:
                continue
            B = _size(f['body'])
            cur = (2 + 2 * m) + B + sum(1 + sum(_size(a) for a in c['params'][:m]) for _, c, _ in cs)
            inl = sum(B + sum(uses[pt] * (_size(c['params'][j]) - 1) for j, pt in enumerate(ptypes)) for _, c, _ in cs)
            if inl >= cur:
                continue
            for stmts, c, owner in cs:
                args = {pt: c['params'][j] for j, pt in enumerate(ptypes)}
                body = copy.deepcopy(f['body'])

                def sub(x):
                    if isinstance(x, dict):
                        ps = x.get('params') or []
                        for i, q in enumerate(ps):
                            if isinstance(q, dict) and q.get('type') in args:
                                ps[i] = copy.deepcopy(args[q['type']])
                            else:
                                sub(q)
                        for st in x.get('statements') or []:
                            for y in st:
                                sub(y)
                for b in body:
                    sub(b)
                i0 = next((k for k, x in enumerate(stmts) if x is c), None)
                if i0 is None:
                    continue
                stmts[i0:i0 + 1] = body
                touched.add(owner)
            removed.add(fid)
            touched.add(fid)
            total += cur - inl
            n_round += 1
        if not n_round:
            break
        RP.functions[:] = [f for f in RP.functions if f['id'] not in removed]
        made += n_round
    log('· 부르는 자리에 풀어 넣은 함수 %d개 (약 %d블록)' % (made, total))
    return made, total
