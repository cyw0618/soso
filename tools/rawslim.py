# -*- coding: utf-8 -*-
"""다른 사람이 만든 엔트리 작품(.ent 의 project.json)을 그대로 읽어 코드 블록 수를 줄인다.

우리 생성기(entrygen)의 '코드 줄이기'(slim.py: 같은 코드 → 함수, 값만 다른 코드 → 매개변수 함수,
매개변수 → 리스트 한 줄 …)를 원본 형식에 맞춘 얇은 껍데기(RawProject)로 그대로 돌린다.
엔트리 저장 데이터는 블록 하나마다 200바이트쯤 붙으므로 블록 수가 곧 작품 크기다.

쓰는 법:  python3 rawslim.py 원본/temp/project.json 결과/temp/project.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import entrygen as EG
from entrygen import Ref
import slim

# 함수 안으로 옮기면 안 되는 블록: 함수 지역 변수·매개변수(원본 함수 것), 이 작품에서 오브젝트마다 뜻이 달라지는 것
EXTRA_UNSAFE = {'get_func_variable', 'set_func_variable', 'change_func_variable', 'show_func_variable'}
slim.UNSAFE_TYPES |= EXTRA_UNSAFE
MIN_STMT = int(os.environ.get('MIN_STMT', '4'))
MAX_W = int(os.environ.get('MAX_W', '24'))
MIN_SEQ = int(os.environ.get('MIN_SEQ', '5'))


class RObj:
    """slim 이 쓰는 오브젝트 모양 (scripts: [[머리 블록, 블록...], ...])."""
    def __init__(self, raw, scene_name):
        self.raw = raw
        self.name = raw['name']
        self.scene = scene_name
        self.kind = raw.get('objectType')
        js = raw['script']
        self.scripts = json.loads(js) if isinstance(js, str) else js
        self.locals = {}
        self.sounds = []
        self.pictures = []


class RawProject:
    def __init__(self, proj):
        self.proj = proj
        sc = {s['id']: s['name'] for s in proj['scenes']}
        self.objects = [RObj(o, sc.get(o['scene'], o['scene'])) for o in proj['objects']]
        # 쓰이는 id 는 새 id 와 겹치지 않게
        for v in proj['variables']:
            EG._used_ids.add(v['id'])
        for m in proj['messages']:
            EG._used_ids.add(m['id'])
        for o in proj['objects']:
            EG._used_ids.add(o['id'])
            for p in o['sprite'].get('pictures', []):
                EG._used_ids.add(p['id'])
            for s in o['sprite'].get('sounds', []):
                EG._used_ids.add(s['id'])
        for s in proj['scenes']:
            EG._used_ids.add(s['id'])
        self.functions = []
        for f in proj.get('functions', []):
            EG._used_ids.add(f['id'])
            js = json.loads(f['content']) if isinstance(f['content'], str) else f['content']
            thread = js[0]
            head = thread[0]
            meta = {k: v for k, v in f.items() if k != 'content'}
            if head.get('type') != 'function_create' or f.get('useLocalVariables') or f.get('localVariables'):
                # 값 함수·지역 변수 함수는 손대지 않고 그대로 (몸통만 줄이기 대상에서 빠짐)
                self.functions.append(dict(id=f['id'], name=f['id'], body=[], value='RAW', raw_content=f['content'], meta=meta))
                continue
            params = []

            def chain(b):
                while isinstance(b, dict):
                    if b.get('type', '').startswith('function_field_') and b['type'] != 'function_field_label':
                        p0 = b['params'][0]
                        params.append(p0.get('type') if isinstance(p0, dict) else p0)
                    b = b['params'][1] if len(b.get('params', [])) > 1 else None
            chain(head['params'][0] if head.get('params') else None)
            # 몸통: 엔트리가 저장한 형식은 머리 블록의 statements[0], 예전 형식은 머리 뒤에 이어 붙은 블록들
            body = list(((head.get('statements') or [[]])[0]) or []) + list(thread[1:])
            head = dict(head, statements=[[]])
            self.functions.append(dict(id=f['id'], name=f['id'], body=body, params=params,
                                       value='USER' if params else None, raw_head=head, meta=meta))
        self.new_lists = {}         # 이름 → (id, 항목)
        self.new_vars = {}
        # 이름으로 찾기 (새로 넣는 코드에서 V('이름'), cast('신호') 를 쓸 수 있게)
        self.var_ids = {v['name']: v['id'] for v in proj['variables'] if not v.get('object')}
        self.msg_ids = {m['name']: m['id'] for m in proj['messages']}

    # ---- slim 이 부르는 것
    def new_function(self, name, body):
        fid = EG.new_id()
        self.functions.append(dict(id=fid, name=name, body=body))
        return {'type': 'func_' + fid, 'params': [], 'statements': []}

    def new_param_function(self, name, body, ptypes):
        fid = EG.new_id()
        self.functions.append(dict(id=fid, name=name, body=body, params=list(ptypes)))
        return fid

    def new_value_function(self, name, expr, ptypes):
        fid = EG.new_id()
        self.functions.append(dict(id=fid, name=name, body=[], params=list(ptypes), value=expr))
        return fid

    def list(self, name, items=(), **kw):
        self.new_lists[name] = (EG.new_id(), list(items))
        if not hasattr(self, 'list_cloud'):
            self.list_cloud = {}
        self.list_cloud[name] = kw.get('cloud')

    def var(self, name, value=0, **kw):
        self.new_vars[name] = (EG.new_id(), value)

    # ---- 다시 원본 형식으로
    def _ref(self, v):
        kind, name = v
        if kind == 'list':
            return self.new_lists[name][0] if name in self.new_lists else self.var_ids[name]
        if kind == 'var':
            return self.new_vars[name][0] if name in self.new_vars else self.var_ids[name]
        if kind == 'msg':
            if name not in self.msg_ids:
                mid = EG.new_id()
                self.msg_ids[name] = mid
                self.proj['messages'].append(dict(id=mid, name=name))
            return self.msg_ids[name]
        raise KeyError(v)

    def _fin(self, b, x=0, y=0):
        if b is None:
            return None
        if isinstance(b, Ref):
            return self._ref(b)
        if not isinstance(b, dict):
            return b
        out = {'id': EG.new_id(), 'x': x, 'y': y, 'type': b['type'],
               'params': [self._fin(p) if isinstance(p, (dict, Ref)) else p for p in b.get('params', [])],
               'statements': [[self._fin(s) for s in st] for st in (b.get('statements') or [])]}
        if not out['statements']:
            del out['statements']
        if not x and not y:
            del out['x'], out['y']
        return out

    def _label(self, f):
        nxt = None
        for pt in reversed(f.get('params', [])):
            nxt = {'type': 'function_field_string', 'params': [{'type': pt, 'params': []}, nxt]}
        return {'type': 'function_field_label', 'params': [f['name'], nxt]}

    def to_json(self):
        proj = self.proj
        for o in self.objects:
            threads = []
            yy = 40
            for sc in o.scripts:
                if not sc:
                    continue
                threads.append([self._fin(b, 40 if i == 0 else 0, yy if i == 0 else 0) for i, b in enumerate(sc)])
                yy += 300
            o.raw['script'] = json.dumps(threads, ensure_ascii=False, separators=(',', ':'))
        funcs = []
        for f in self.functions:
            if f.get('value') == 'RAW':
                funcs.append(dict(f['meta'], content=f['raw_content']))
                continue
            if f.get('value') not in (None, 'USER'):
                create = {'type': 'function_create_value', 'statements': [list(f['body'])],
                          'params': [self._label(f), None, None, f['value']]}
                blocks = [self._fin(create, 40, 40)]
                ftype = 'value'
            else:
                # 원본 함수의 머리(이름표·매개변수 칸)는 그대로, 새 함수는 이름표에 매개변수 칸을 단다.
                # 몸통은 엔트리가 저장하는 형식대로 머리 블록의 statements 안에 넣는다.
                head = dict(f.get('raw_head') or {'type': 'function_create', 'params': [self._label(f), None]})
                head['statements'] = [list(f['body'])]
                blocks = [self._fin(head, 40, 40)]
                ftype = 'normal'
            meta = f.get('meta') or dict(id=f['id'], type=ftype, localVariables=[], useLocalVariables=False)
            funcs.append(dict(meta, content=json.dumps([blocks], ensure_ascii=False, separators=(',', ':'))))
        proj['functions'] = funcs
        for name, (lid, items) in self.new_lists.items():
            cl = getattr(self, 'list_cloud', {}).get(name)
            proj['variables'].append(dict(name=name, id=lid, visible=False, value=0, variableType='list',
                                          isCloud=(cl == 'shared'), isRealTime=(cl in (True, 'realtime')),
                                          cloudDate=False, object=None, x=0, y=0, width=100, height=120,
                                          array=[dict(data=str(i)) for i in items]))
        for name, (vid, val) in self.new_vars.items():
            proj['variables'].append(dict(name=name, id=vid, visible=False, value=val, variableType='variable',
                                          isCloud=False, isRealTime=False, cloudDate=False, object=None, x=0, y=0))
        return proj


def count_blocks(proj):
    n = [0]

    def walk(x):
        if isinstance(x, dict):
            if 'type' in x:
                n[0] += 1
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for o in proj['objects']:
        walk(json.loads(o['script']) if isinstance(o['script'], str) else o['script'])
    for f in proj.get('functions', []):
        walk(json.loads(f['content']) if isinstance(f['content'], str) else f['content'])
    return n[0]


def pictures_as_names(RP):
    """모양 바꾸기의 그림 id → 그림 이름(글자). 엔트리는 이름으로도 모양을 찾는다 → 오브젝트가 달라도 같은 코드가 되어
    함수로 묶을 수 있다 (그 오브젝트 안에서 이름이 하나뿐일 때만)."""
    n = [0]
    for o in RP.objects:
        pics = o.raw['sprite'].get('pictures', [])
        names = {}
        for pc in pics:
            names[pc['name']] = names.get(pc['name'], 0) + 1
        by_id = {pc['id']: pc['name'] for pc in pics if names[pc['name']] == 1}

        def fix(b):
            if isinstance(b, dict):
                ps = b.get('params', []) or []
                for i, q in enumerate(ps):
                    if isinstance(q, dict) and q.get('type') == 'get_pictures' and q.get('params') \
                            and isinstance(q['params'][0], str) and q['params'][0] in by_id:
                        ps[i] = {'type': 'text', 'params': [by_id[q['params'][0]]]}
                        n[0] += 1
                    else:
                        fix(q)
                for st in b.get('statements') or []:
                    for x in st:
                        fix(x)
        for sc in o.scripts:
            for b in sc:
                fix(b)
    return n[0]


def run_slim(RP, rounds=3):
    """slim.apply 에서 원본 작품에 맞는 단계만 (우리 생성기 전용 단계는 뺌)."""
    print('· 모양 id → 이름 %d곳' % pictures_as_names(RP))
    print('· 같은 시작 조건 코드 묶음 합침 %d개' % slim.merge_same_hats(RP))
    for r in range(rounds):
        groups = slim.analyze(RP)
        print('· 함수 %d개로 합침' % slim.functionize(RP, groups))
        n, g = slim.functionize_params(RP)
        print('· 값만 다른 코드 %d묶음 → 매개변수 함수 (약 %d블록)' % (n, g))
        for _ in range(3):
            n, g = slim.outline_statements(RP, min_size=MIN_STMT)
            print('· 코드 속 되풀이 덩어리 %d묶음 → 함수 (약 %d블록)' % (n, g))
            if n == 0:
                break
        for _ in range(4):
            n, g = slim.outline_sequences(RP, max_w=MAX_W, min_size=MIN_SEQ)
            print('· 되풀이 연속 블록 %d묶음 → 함수 (약 %d블록)' % (n, g))
            if n == 0:
                break
    n, g = slim.inline_functions(RP)
    print('· 작은 함수 %d개 풀어 넣음 (약 %d블록)' % (n, g))
    n, g = slim.args_to_lists(RP)
    print('· 함수 입력값 → 리스트 행 번호 %d개 함수 (약 %d블록)' % (n, g))


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    proj = json.load(open(src, encoding='utf-8'))
    before = count_blocks(proj)
    RP = RawProject(proj)
    run_slim(RP)
    out = RP.to_json()
    after = count_blocks(out)
    print('블록: %d → %d' % (before, after))
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as fp:
        json.dump(out, fp, ensure_ascii=False, separators=(',', ':'))
