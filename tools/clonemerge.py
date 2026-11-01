# -*- coding: utf-8 -*-
"""같은 장면에서 화면 순서가 붙어 있고 모양·코드 모양이 같은 그림 오브젝트들(카드 칸, 칩 …)을
'원본 하나 + 복제본'으로 합친다. 오브젝트 하나마다 그림 목록(카드 53장이면 약 14KB)과 코드가 따로 저장되던 것을 한 벌로.

  - 원본(맨 앞 오브젝트)이 장면 시작 때 나머지 칸을 아래쪽 칸부터 복제한다 (엔트리는 복제본을 원본 바로 아래 층에 넣으므로
    아래쪽부터 만들면 원래 앞뒤 순서와 같아진다). 칸 번호는 원본의 지역 변수 '_칸' (복제본은 만들 때 값을 복사해 감).
  - 칸마다 다른 위치·모양·보이기, 코드 속 숫자·글자 → 칸 번호로 읽는 리스트
  - 칸마다 다른 변수: 그 칸만 쓰는 변수 → 지역 변수(복제본마다 따로), 다른 곳에서도 쓰는 변수(읽기만) → 칸 번호로 고르는 값 함수
  - 다른 오브젝트가 id 로 가리키는 오브젝트, 복제·지우기 블록이 있는 코드, 시작 버튼 코드는 건드리지 않는다
"""
import collections
import copy
import json

import entrygen as EG

VW = {'set_variable', 'change_variable'}
BAD = {'create_clone', 'delete_clone', 'remove_all_clones', 'when_clone_start', 'when_run_button_click',
       'get_func_variable', 'set_func_variable', 'change_func_variable'}


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


class Shape:
    def __init__(self, scal):
        self.scal = scal

    def sig(self, b, cb, parent=None, idx=None, st=None):
        if not isinstance(b, dict):
            return repr(b)
        t = b.get('type')
        ps = b.get('params') or []
        if t in ('number', 'text') and ps and not isinstance(ps[0], dict):
            cb('lit', parent, idx, b)
            return '#'
        if t == 'get_variable' and ps and isinstance(ps[0], str) and ps[0] in self.scal:
            cb('read', parent, idx, b)
            return 'V'
        if st is not None and (t in BAD):
            st['bad'] = True
        parts = []
        for i, q in enumerate(ps):
            if i == 0 and t in VW and isinstance(q, str) and q in self.scal:
                cb('write', b, 0, b)
                parts.append('V')
            elif isinstance(q, dict):
                parts.append(self.sig(q, cb, ps, i, st))
            else:
                parts.append(repr(q))
        ss = []
        for stl in b.get('statements') or []:
            ss.append(','.join(self.sig(s, cb, stl, j, st) for j, s in enumerate(stl)))
        return '%s(%s){%s}' % (t, ','.join(parts), ';'.join(ss))

    def object_sig(self, scripts):
        slots, st = [], {'bad': False}

        def cb(kind, cont, i, blk):
            if kind == 'lit':
                slots.append(('lit', str(blk['params'][0]), None))
            else:
                slots.append(('var', blk['params'][0], kind))
        parts = []
        for th in scripts:
            parts.append('[' + ','.join(self.sig(b, cb, th, j, st) for j, b in enumerate(th)) + ']')
        vs = [s[1] for s in slots if s[0] == 'var']
        pat = tuple(vs.index(v) for v in vs)
        return '|'.join(parts), tuple(slots), pat, st['bad']


def clone_merge(RP, min_gain=1500, log=print):
    proj = RP.proj
    sc_name = {s['id']: s['name'] for s in proj['scenes']}
    first_scene = proj['scenes'][0]['id']
    scal = {v['id'] for v in proj['variables'] if v.get('variableType') == 'variable' and not v.get('object')
            and not v.get('isRealTime') and not v.get('isCloud')}
    vinit = {v['id']: v.get('value', 0) for v in proj['variables']}
    vname = {v['id']: v['name'] for v in proj['variables']}
    robj = {id(o.raw): o for o in RP.objects}
    # 다른 곳에서 id 로 가리키는 오브젝트
    code_all = json.dumps([o.scripts for o in RP.objects] + [f.get('body') for f in RP.functions] +
                          [f.get('raw_content') for f in RP.functions], ensure_ascii=False, default=str)
    refd = {o['id'] for o in proj['objects'] if ('"%s"' % o['id']) in code_all}
    # 변수마다 어느 오브젝트 코드에 나오는지, 함수에 나오는지
    var_objs = collections.defaultdict(set)
    for o in RP.objects:
        def f(b, oid=o.raw['id']):
            for q in b.get('params') or []:
                if isinstance(q, str) and q in scal:
                    var_objs[q].add(oid)
        _walk(o.scripts, f)
    var_in_func = set()
    for fn in RP.functions:
        def g(b):
            for q in b.get('params') or []:
                if isinstance(q, str) and q in scal:
                    var_in_func.add(q)
        _walk(fn.get('body') or [], g)
        if fn.get('raw_content'):
            for v in scal:
                if ('"%s"' % v) in fn['raw_content']:
                    var_in_func.add(v)
    S = Shape(scal)
    info = {}
    for o in proj['objects']:
        if o.get('objectType') not in ('sprite', 'textBox') or o['scene'] == first_scene or o['id'] in refd:
            continue
        ro = robj[id(o)]
        sig, slots, pat, bad = S.object_sig(ro.scripts)
        if bad or not any(th for th in ro.scripts):
            continue
        e = o['entity']
        pics = tuple((p['fileurl'], p['name']) for p in o['sprite'].get('pictures', []))
        style = None
        if o['objectType'] == 'textBox':
            style = tuple(e.get(k) for k in ('font', 'colour', 'bgColor', 'textAlign', 'lineBreak', 'width', 'height',
                                              'regX', 'regY', 'underLine', 'strike', 'fontSize'))
        key = (o['scene'], pics, o.get('rotateMethod'), e.get('scaleX'), e.get('scaleY'), e.get('rotation'),
               e.get('direction'), sig, pat, o['objectType'], style)
        info[o['id']] = (key, slots)
    # 같은 열쇠 묶음: 화면 순서상 사이에 낀 다른 오브젝트가 묶음 칸들과 겹치지 않을 때만
    order = {o['id']: i for i, o in enumerate(proj['objects'])}
    groups = collections.defaultdict(list)
    for o in proj['objects']:
        if o['id'] in info:
            groups[info[o['id']][0]].append(o)
    runs = []
    for k, objs in groups.items():
        if len(objs) < 2:
            continue
        # 앞에서부터 이어 붙이되, 사이에 낀 다른 오브젝트가 구간 칸들과 겹치면 거기서 끊는다
        seg, gap = [objs[0]], []
        for m in objs[1:]:
            mid_objs = [x for x in proj['objects'][order[seg[-1]['id']] + 1:order[m['id']]]]
            cand_gap = gap + mid_objs
            if any(_overlap(x, y) for x in cand_gap for y in seg + [m]):
                if len(seg) >= 2:
                    runs.append(seg)
                seg, gap = [m], []
            else:
                seg.append(m)
                gap = cand_gap
        if len(seg) >= 2:
            runs.append(seg)
    made = removed = 0
    saved_est = 0
    remove_ids = set()
    for members in runs:
        key, slots0 = info[members[0]['id']]
        N = len(members)
        allslots = [info[m['id']][1] for m in members]
        nsl = len(slots0)
        lit_vary = [j for j in range(nsl) if slots0[j][0] == 'lit' and len({s[j][1] for s in allslots}) > 1]
        var_js = [j for j in range(nsl) if slots0[j][0] == 'var']
        pat = key[8]
        is_text = key[9] == 'textBox'
        classes = collections.OrderedDict()
        for k, j in enumerate(var_js):
            classes.setdefault(pat[k], []).append(j)
        private, shared = [], []
        ok = True
        for c, js in classes.items():
            vals = [s[js[0]][1] for s in allslots]
            if len(set(vals)) == 1:
                continue
            if len(set(vals)) != N:            # 몇 칸만 같은 변수 → 복잡, 건너뜀
                ok = False
                break
            roles = {slots0[j][2] for j in js}
            is_private = all(var_objs[v] == {m['id']} and v not in var_in_func for v, m in zip(vals, members))
            if is_private:
                private.append((js, vals))
            elif roles == {'read'}:
                shared.append((js, vals))
            else:
                ok = False
                break
        if not ok:
            continue
        # 이득 어림: 지워지는 오브젝트(그림 목록 포함) + 코드 한 벌 − 복제 블록·리스트·고르기 함수
        obj_bytes = sum(len(json.dumps(dict(m, script=''), ensure_ascii=False)) for m in members[1:])
        nblocks = sum(EG_count(robj[id(m)].scripts) for m in members[1:])
        spawn_cost = 10 if N > 4 else 3 * (N - 1) + 2
        cost = 200 * (spawn_cost + 8 + 6 * N * len(shared) + 2 * len(lit_vary)) + 20 * N * (len(lit_vary) + 5)
        gain = obj_bytes - cost          # 코드는 줄이기 단계에서 이미 짧아지므로 오브젝트 몫만 셈
        if gain < min_gain * (N - 1):
            continue
        master = members[0]
        mro = robj[id(master)]
        mid = master['id']
        # 지역 변수: 칸 번호
        kid = EG.new_id()
        proj['variables'].append(dict(name='_칸', id=kid, visible=False, value='1', variableType='variable',
                                      isCloud=False, isRealTime=False, cloudDate=False, object=mid, x=0, y=0,
                                      array=[]))
        kget = {'type': 'get_variable', 'params': [kid, None]}

        def lst(name, items):
            lid = EG.new_id()
            proj['variables'].append(dict(name=name, id=lid, visible=False, value=0, variableType='list',
                                          isCloud=False, isRealTime=False, cloudDate=False, object=None, x=0, y=0,
                                          width=100, height=120, array=[dict(data=str(x)) for x in items]))
            return lid

        def lget(lid):
            return {'type': 'value_of_index_from_list', 'params': [None, lid, None, copy.deepcopy(kget)]}
        tag = master['name']
        lit_lists = {j: lst('_칸값_%s_%d' % (tag, n), [s[j][1] for s in allslots]) for n, j in enumerate(lit_vary)}
        loc = {}
        for js, vals in private:
            nid = EG.new_id()
            proj['variables'].append(dict(name='_칸_' + vname[vals[0]], id=nid, visible=False,
                                          value=vinit.get(vals[0], 0), variableType='variable', isCloud=False,
                                          isRealTime=False, cloudDate=False, object=mid, x=0, y=0, array=[]))
            for j in js:
                loc[j] = nid
        disp = {}
        for n, (js, vals) in enumerate(shared):
            fid = EG.new_id()
            pt = 'stringParam_' + EG.new_id()
            tmp = EG.new_id()
            proj['variables'].append(dict(name='_칸고르기_%s_%d' % (tag, n), id=tmp, visible=False, value=0,
                                          variableType='variable', isCloud=False, isRealTime=False, cloudDate=False,
                                          object=None, x=0, y=0, array=[]))
            body = [{'type': '_if', 'params': [{'type': 'boolean_basic_operator', 'params': [
                        {'type': pt, 'params': []}, 'EQUAL', {'type': 'number', 'params': [str(i + 1)]}]}, None],
                     'statements': [[{'type': 'set_variable', 'params': [tmp, {'type': 'get_variable', 'params': [v, None]}, None],
                                      'statements': []}]]} for i, v in enumerate(vals)]
            RP.functions.append(dict(id=fid, name='칸고르기_%s_%d' % (tag, n), body=body, params=[pt],
                                     value={'type': 'get_variable', 'params': [tmp, None]}))
            for j in js:
                disp[j] = fid
        # 원본 코드 → 칸 번호로 읽는 코드
        tmpl = copy.deepcopy(mro.scripts)
        pos = []

        def cb(kind, cont, i, blk):
            pos.append((kind, cont, i, blk))
        for th in tmpl:
            for j, b in enumerate(th):
                S.sig(b, cb, th, j)
        assert len(pos) == nsl
        for j in lit_vary:
            kind, cont, i, blk = pos[j]
            cont[i] = lget(lit_lists[j])
        for j, nid in loc.items():
            kind, cont, i, blk = pos[j]
            blk['params'][0] = nid
        for j, fid in disp.items():
            kind, cont, i, blk = pos[j]
            cont[i] = {'type': 'func_' + fid, 'params': [copy.deepcopy(kget)]}
        # 칸마다 다른 위치·모양·보이기
        props = []
        es = [m['entity'] for m in members]
        if len({(e['x'], e['y']) for e in es}) > 1:
            lx_ = lst('_칸X_%s' % tag, [e['x'] for e in es])
            ly_ = lst('_칸Y_%s' % tag, [e['y'] for e in es])
            props.append({'type': 'locate_xy', 'params': [lget(lx_), lget(ly_), None]})
        mpics = master['sprite']['pictures']
        sel = []
        for m in members if mpics else []:
            ids = [p['id'] for p in m['sprite']['pictures']]
            k = ids.index(m.get('selectedPictureId')) if m.get('selectedPictureId') in ids else 0
            sel.append(mpics[k]['id'])
        if len(set(sel)) > 1:
            lp = lst('_칸모양_%s' % tag, sel)
            props.append({'type': 'change_to_some_shape', 'params': [lget(lp), None]})
        if is_text:
            txts = [m.get('text', m['entity'].get('text', '')) for m in members]
            if len(set(txts)) > 1:
                lt = lst('_칸글_%s' % tag, txts)
                props.append({'type': 'text_write', 'params': [lget(lt), None]})
        vis = ['1' if e.get('visible') else '0' for e in es]
        if len(set(vis)) > 1:
            lv = lst('_칸보임_%s' % tag, vis)
            props.append({'type': 'if_else', 'params': [{'type': 'boolean_basic_operator', 'params': [
                lget(lv), 'EQUAL', {'type': 'text', 'params': ['1']}]}, None, None],
                'statements': [[{'type': 'show', 'params': [None]}], [{'type': 'hide', 'params': [None]}]]})
        spawn = []
        loop_spawn = N > 4
        if not loop_spawn:
            for idx in range(N - 1, 0, -1):          # 아래쪽 칸부터 복제 → 원래 앞뒤 순서
                spawn += [{'type': 'set_variable', 'params': [kid, {'type': 'number', 'params': [str(idx + 1)]}, None]},
                          {'type': 'create_clone', 'params': ['self', None]}]
            spawn.append({'type': 'set_variable', 'params': [kid, {'type': 'number', 'params': ['1']}, None]})
        else:
            # 반복문으로 한 프레임에 하나씩: 복제본은 전역 '다음 칸' 값을 받아 가고 하나 줄인다 (N, N-1, …, 2 → 아래쪽부터)
            nxt = EG.new_id()
            proj['variables'].append(dict(name='_칸다음_%s' % tag, id=nxt, visible=False, value=0,
                                          variableType='variable', isCloud=False, isRealTime=False, cloudDate=False,
                                          object=None, x=0, y=0, array=[]))
            spawn_thread = [{'type': 'when_scene_start', 'params': [None]},
                            {'type': 'set_variable', 'params': [nxt, {'type': 'number', 'params': [str(N)]}, None]},
                            {'type': 'repeat_basic', 'params': [{'type': 'number', 'params': [str(N - 1)]}, None],
                             'statements': [[{'type': 'create_clone', 'params': ['self', None]}]]}]
            props = [{'type': 'set_variable', 'params': [kid, {'type': 'get_variable', 'params': [nxt, None]}, None]},
                     {'type': 'change_variable', 'params': [nxt, {'type': 'number', 'params': ['-1']}, None]}] + props
        new = []
        clone_threads = [[{'type': 'when_clone_start', 'params': [None]}] + props] if props else []
        spawned = loop_spawn
        if loop_spawn:
            new.append(spawn_thread)
        for th in tmpl:
            if not th:
                continue
            if th[0].get('type') == 'when_scene_start':
                body = th[1:]
                if not spawned:
                    new.append([th[0]] + spawn + body)
                    spawned = True
                else:
                    new.append(th)
                clone_threads.append([{'type': 'when_clone_start', 'params': [None]}] + copy.deepcopy(body))
            else:
                new.append(th)
        if not spawned:
            new.insert(0, [{'type': 'when_scene_start', 'params': [None]}] + spawn)
        mro.scripts = clone_threads + new
        for m in members[1:]:
            remove_ids.add(m['id'])
        made += 1
        removed += N - 1
        saved_est += gain
        log('   · %s: %s 외 %d개 → 복제본 (칸별 값 %d, 지역 변수 %d, 고르기 %d)' % (
            sc_name[master['scene']], master['name'], N - 1, len(lit_vary), len(private), len(shared)))
    proj['objects'][:] = [o for o in proj['objects'] if o['id'] not in remove_ids]
    RP.objects[:] = [o for o in RP.objects if o.raw['id'] not in remove_ids]
    log('· 같은 모양 오브젝트 %d묶음 → 원본+복제본 (오브젝트 %d개 줄임, 약 %.0fKB)' % (made, removed, saved_est / 1024))
    return made, removed


def EG_count(x):
    n = [0]
    _walk(x, lambda b: n.__setitem__(0, n[0] + (1 if 'type' in b else 0)))
    return n[0]


def _bbox(o):
    e = o['entity']
    sx, sy = abs(e.get('scaleX') or 1), abs(e.get('scaleY') or 1)
    w, h = (e.get('width') or 0) * sx, (e.get('height') or 0) * sy
    left = e['x'] - (e.get('regX') or 0) * sx
    top = e['y'] + (e.get('regY') or 0) * sy
    if e.get('rotation'):
        r = (w * w + h * h) ** 0.5
        return (e['x'] - r, e['x'] + r, e['y'] - r, e['y'] + r)
    return (left, left + w, top - h, top)


def _overlap(a, b):
    """두 오브젝트의 처음 자리 상자가 겹치나 (조금 여유를 둠)."""
    x1, x2, y1, y2 = _bbox(a)
    u1, u2, v1, v2 = _bbox(b)
    pad = 2
    return not (x2 + pad <= u1 or u2 + pad <= x1 or y2 + pad <= v1 or v2 + pad <= y1)
