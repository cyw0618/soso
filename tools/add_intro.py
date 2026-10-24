# -*- coding: utf-8 -*-
"""다른 엔트리 작품(.ent) 맨 앞에 'CYW GAMES' 인트로 장면을 끼워 넣는다.

    python3 tools/add_intro.py 원래작품.ent 새작품.ent

- 인트로 장면을 첫 장면으로 넣고, 인트로가 끝나면(또는 클릭·스페이스로 건너뛰면) 원래 첫 장면으로 간다.
- 엔트리의 '시작하기 버튼을 클릭했을 때'는 지금 장면의 오브젝트에서만 실행되므로, 원래 첫 장면에
  '시작하기를 클릭했을 때' 코드가 있으면 그 내용을 '장면이 시작되었을 때'로 옮겨 한 번만 실행되게 한다.
"""
import io
import os
import sys
import json
import gzip
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('FONT_DIR', os.path.join(HERE, 'fonts'))

from entrygen import *
import sprites as SP
import intro

TARGET = '__원래첫장면__'


def _read_ent(path):
    files = {}
    with tarfile.open(path) as t:
        for m in t.getmembers():
            if m.isfile():
                files[m.name] = t.extractfile(m).read()
    return files


def _intro_project():
    P = Project('인트로')
    P.scene('인트로')
    P.scene(TARGET)
    black = SP.plain(480, 270, (0, 0, 0, 255), 'black_full')
    intro.build(P, {'S_INTRO': '인트로', 'S_TITLE': TARGET, 'BLACK': black})
    tmp = os.path.join(tempfile.mkdtemp(), 'intro.ent')
    proj = P.write_ent(tmp)
    return proj, _read_ent(tmp)


def _new_id(used):
    import random
    abc = 'abcdefghijklmnopqrstuvwxyz0123456789'
    while True:
        s = random.choice(abc[:26]) + ''.join(random.choice(abc) for _ in range(3))
        if s not in used:
            used.add(s)
            return s


def _run_hats_to_once(proj, scene_id, used):
    """원래 첫 장면의 '시작하기를 클릭했을 때' → '장면이 시작되었을 때 + 처음 한 번만'."""
    flag_id = _new_id(used)
    changed = 0
    for o in proj['objects']:
        if o['scene'] != scene_id:
            continue
        is_str = isinstance(o['script'], str)
        scripts = json.loads(o['script']) if is_str else o['script']
        # 원래 첫 장면으로 가기만 하는 코드는 이제 필요 없다 (인트로가 그 장면으로 보내 준다)
        keep = []
        for sc in scripts:
            if (sc and sc[0].get('type') == 'when_run_button_click' and len(sc) == 2
                    and sc[1].get('type') == 'start_scene' and (sc[1].get('params') or [None])[0] == scene_id):
                continue
            keep.append(sc)
        scripts[:] = keep
        for sc in scripts:
            if sc and sc[0].get('type') == 'when_run_button_click':
                hat = sc[0]
                body = sc[1:]
                hat['type'] = 'when_scene_start'
                hat['params'] = [None]
                cond = {'id': _new_id(used), 'type': 'boolean_basic_operator', 'params': [
                    {'id': _new_id(used), 'type': 'get_variable', 'params': [flag_id]}, 'EQUAL',
                    {'id': _new_id(used), 'type': 'number', 'params': ['0']}]}
                sc[1:] = [{'id': _new_id(used), 'type': '_if', 'params': [cond], 'statements': [body]}]
                changed += 1
        o['script'] = json.dumps(scripts, ensure_ascii=False) if is_str else scripts
    if changed:
        # 처음 장면에 들어오고 0.2초 뒤 '처음 시작' 표시를 끈다 (이후 같은 장면으로 돌아오면 실행 안 함)
        proj['variables'].append(dict(name='_인트로뒤첫시작끝', id=flag_id, visible=False, value=0, variableType='variable',
                                      isCloud=False, isRealTime=False, cloudDate=False, object=None, x=0, y=0))
        for o in proj['objects']:
            if o['scene'] == scene_id:
                is_str = isinstance(o['script'], str)
                scripts = json.loads(o['script']) if is_str else o['script']
                scripts.append([{'id': _new_id(used), 'type': 'when_scene_start', 'params': [None], 'x': 40, 'y': 40},
                                {'id': _new_id(used), 'type': 'wait_second',
                                 'params': [{'id': _new_id(used), 'type': 'number', 'params': ['0.2']}, None]},
                                {'id': _new_id(used), 'type': 'set_variable',
                                 'params': [flag_id, {'id': _new_id(used), 'type': 'number', 'params': ['1']}, None]}])
                o['script'] = json.dumps(scripts, ensure_ascii=False) if is_str else scripts
                break
    return changed


def main(src, dst):
    files = _read_ent(src)
    proj = json.loads(files['temp/project.json'].decode('utf-8'))
    first = proj['scenes'][0]['id']
    iproj, ifiles = _intro_project()
    tgt = [s['id'] for s in iproj['scenes'] if s['name'] == TARGET][0]
    intro_sid = [s['id'] for s in iproj['scenes'] if s['name'] == '인트로'][0]
    used = set()
    for s in proj['scenes']:
        used.add(s['id'])
    for v in proj['variables']:
        used.add(v['id'])
    for o in proj['objects']:
        used.add(o['id'])
    if intro_sid in used:
        raise SystemExit('장면 id 가 겹침: 다시 실행해 주세요')
    # 인트로 오브젝트: 목표 장면 id 를 원래 첫 장면 id 로
    objs = []
    for o in iproj['objects']:
        if o['scene'] != intro_sid:
            continue
        o = dict(o)
        o['script'] = o['script'].replace('"%s"' % tgt, '"%s"' % first) if isinstance(o['script'], str) else \
            json.loads(json.dumps(o['script']).replace('"%s"' % tgt, '"%s"' % first))
        objs.append(o)
    names = {v['name'] for v in proj['variables']}
    for v in iproj['variables']:
        if v['variableType'] in ('timer', 'answer'):
            continue
        if v['name'] in names:
            raise SystemExit('변수 이름이 겹침: %s' % v['name'])
        proj['variables'].append(v)
    n_run = _run_hats_to_once(proj, first, used)
    proj['scenes'].insert(0, {'id': intro_sid, 'name': '인트로'})
    proj['objects'] = objs + proj['objects']
    files['temp/project.json'] = json.dumps(proj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    for k, data in ifiles.items():
        if k != 'temp/project.json':
            files.setdefault(k, data)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as tar:
        dirs = set()
        for path in files:
            parts = path.split('/')
            for i in range(1, len(parts)):
                dirs.add('/'.join(parts[:i]))
        for d in sorted(dirs):
            ti = tarfile.TarInfo(d + '/')
            ti.type = tarfile.DIRTYPE
            ti.mode = 0o755
            tar.addfile(ti)
        for path, data in files.items():
            ti = tarfile.TarInfo(path)
            ti.size = len(data)
            ti.mode = 0o644
            ti.mtime = 1767225600
            tar.addfile(ti, io.BytesIO(data))
    with open(dst, 'wb') as f:
        f.write(gzip.compress(raw.getvalue(), 9, mtime=0))
    print('인트로 추가 완료: %s (%.1f MB) · 장면 %d개 · 시작 코드 옮김 %d개'
          % (dst, os.path.getsize(dst) / 1e6, len(proj['scenes']), n_run))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
