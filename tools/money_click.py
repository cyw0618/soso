# -*- coding: utf-8 -*-
"""버튼을 '아무 데나' 눌러도 되게 한다.

엔트리는 글상자(투명 배경)를 글자 크기만큼만, 그림은 그림 상자만큼만 누른 것으로 친다.
이 작품의 버튼은 '글상자(클릭 코드) + 같은 이름_배경 그림(코드 없음)'으로 되어 있어서, 눈에 보이는 버튼 면(배경 그림)을
눌러도 글상자 위가 아니면 아무 일도 안 일어났다.
→ 배경 그림에도 같은 클릭 코드를 붙인다.
  - 클릭 코드가 '오브젝트 자신'을 건드리지 않으면(함수·변수·장면 바꾸기만) 코드를 그대로 복사 (블록 몇 개)
  - 자신을 건드리면(글자 바꾸기·모양·보이기 …) 신호로 보내 글상자가 자기 코드를 돌게 한다
"""
import copy

import entrygen as EG
from entrygen import B, ref

SELF_PREFIX = ('locate', 'move', 'rotate', 'direction', 'text_', 'change_to', 'change_scale', 'set_scale', 'stretch',
               'flip', 'dialog', 'remove_dialog', 'create_clone', 'delete_clone', 'remove_all_clones',
               'change_object_index', 'brush', 'start_drawing', 'stop_drawing', 'stamp', 'erase', 'set_effect',
               'change_effect', 'add_effect', 'set_entity', 'show', 'hide', 'reach_something', 'get_pictures',
               'get_func_variable', 'set_func_variable', 'change_func_variable', 'sound_')


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


def _is_self(b):
    t = str(b.get('type', ''))
    if t.startswith(SELF_PREFIX):
        return True
    if t == 'coordinate_object':
        v = (b.get('params') or [None, None])[1]
        return v == 'self' or v is None
    return False


def forward_bg_clicks(RP, proj, log=print):
    funcs = {f['id']: f for f in RP.functions}
    local_ids = {}
    for v in proj['variables']:
        if v.get('object'):
            local_ids.setdefault(v['object'], set()).add(v['id'])
    selfy_cache = {}

    def func_selfy(fid, stack=()):
        if fid in selfy_cache:
            return selfy_cache[fid]
        if fid in stack:
            return False
        f = funcs.get(fid)
        if f is None or f.get('value') == 'RAW':
            selfy_cache[fid] = True          # 모르는 함수는 자신을 건드린다고 본다
            return True
        hit = [False]

        def fn(b):
            if _is_self(b):
                hit[0] = True
            t = str(b.get('type', ''))
            if t.startswith('func_') and func_selfy(t[5:], stack + (fid,)):
                hit[0] = True
        _walk(f.get('body') or [], fn)
        if isinstance(f.get('value'), dict):
            _walk(f['value'], fn)
        selfy_cache[fid] = hit[0]
        return hit[0]

    def selfy(blocks, oid=None):
        hit = [False]
        mine = local_ids.get(oid, set())

        def fn(b):
            if mine and any(isinstance(q, str) and q in mine for q in (b.get('params') or [])):
                hit[0] = True
            if _is_self(b):
                hit[0] = True
            t = str(b.get('type', ''))
            if t.startswith('func_') and func_selfy(t[5:]):
                hit[0] = True
        _walk(blocks, fn)
        return hit[0]

    by = {}
    for o in RP.objects:
        by.setdefault(o.scene, {})[o.name] = o

    def click_threads(o):
        return [th for th in o.scripts if th and th[0].get('type') == 'when_object_click']
    copied = msged = 0
    for o in list(RP.objects):
        cts = click_threads(o)
        if not cts:
            continue
        y = by.get(o.scene, {}).get(o.name + '_배경')
        if y is None or click_threads(y):
            continue
        body = [b for th in cts for b in th[1:]]
        if not body:
            continue
        if not selfy(body, o.raw['id']):
            y.scripts.append([EG.B('when_object_click')] + copy.deepcopy(body))
            copied += 1
        else:
            m = '클릭_%s_%s' % (o.scene, o.name)
            new_cts = []
            for th in o.scripts:
                if th and th[0].get('type') == 'when_object_click':
                    new_cts.append([th[0], EG.cast(m)])
                    new_cts.append([EG.on_msg(m)] + th[1:])
                else:
                    new_cts.append(th)
            o.scripts = new_cts
            y.scripts.append([EG.B('when_object_click'), EG.cast(m)])
            msged += 1
    log('· 버튼 배경 그림에도 클릭 코드: 복사 %d개, 신호 %d개' % (copied, msged))
    return copied, msged
