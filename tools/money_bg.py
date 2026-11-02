# -*- coding: utf-8 -*-
"""원본 작품의 배경 오브젝트(JPG 그림을 쓰는 오브젝트)를 지금 작품에 그대로 다시 붙인다.

    python3 -I tools/money_bg.py 원본/temp 지금결과폴더 새결과폴더

- 같은 id 의 오브젝트를 원본 것으로 통째로 바꾼다 (같은 자리 = 같은 화면 순서).
  원본 코드가 지금 작품에 없는 함수·변수를 부르면 코드만 지금 것으로 둔다.
- 그림 파일과 미리보기 파일도 원본 바이트 그대로 (money_pack 이 그 파일들은 건드리지 않음).
"""
import json
import os
import re
import shutil
import sys


def main(src_temp, cur_dir, out_dir):
    raw = json.load(open(os.path.join(src_temp, 'project.json'), encoding='utf-8'))
    cur_temp = os.path.join(cur_dir, 'temp')
    proj = json.load(open(os.path.join(cur_temp, 'project.json'), encoding='utf-8'))
    R = {o['id']: o for o in raw['objects']}
    fids = {f['id'] for f in proj['functions']}
    vids = {v['id'] for v in proj['variables']}
    mids = {m['id'] for m in proj['messages']}
    oids = {o['id'] for o in proj['objects']}
    sids = {s['id'] for s in proj['scenes']}
    replaced, kept_code, files = 0, 0, set()
    for i, o in enumerate(proj['objects']):
        if not any(p['fileurl'].endswith('.jpg') for p in o['sprite'].get('pictures', [])):
            continue
        ro = R.get(o['id'])
        if ro is None:
            continue
        new = json.loads(json.dumps(ro, ensure_ascii=False))
        sc = new['script'] if isinstance(new['script'], str) else json.dumps(new['script'], ensure_ascii=False)
        missing = [f for f in re.findall(r'"func_(\w{4})"', sc) if f not in fids]
        refs = set(re.findall(r'"([a-z0-9]{4})"', sc))
        # 원본 코드가 가리키는 변수·신호·오브젝트·장면이 지금 작품에 다 있는지 (블록 id 는 상관없음)
        gone = [x for x in refs if x in {v['id'] for v in raw['variables']} and x not in vids]
        gone += [x for x in refs if x in {m['id'] for m in raw['messages']} and x not in mids]
        gone += [x for x in refs if x in {q['id'] for q in raw['objects']} and x not in oids]
        gone += [x for x in refs if x in {s['id'] for s in raw['scenes']} and x not in sids]
        if missing or gone:
            new['script'] = o['script']          # 코드만 지금 것 (원본 코드가 부르는 함수·변수가 바뀜)
            kept_code += 1
        proj['objects'][i] = new
        replaced += 1
        for p in new['sprite'].get('pictures', []):
            files.add(p['fileurl'])
            if p.get('thumbUrl'):
                files.add(p['thumbUrl'])
    out_temp = os.path.join(out_dir, 'temp')
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_temp)
    # 지금 결과의 파일들은 연결, 원본 배경 파일은 실제 복사로 덮어씀
    for d in os.listdir(cur_temp):
        p = os.path.join(cur_temp, d)
        if os.path.isdir(p):
            os.symlink(os.path.realpath(p), os.path.join(out_temp, d))
    for f in sorted(files):
        rel = os.path.relpath(f, 'temp')
        top = os.path.join(out_temp, rel.split(os.sep)[0])
        if os.path.islink(top):
            real = os.readlink(top)
            os.unlink(top)
            shutil.copytree(real, top, symlinks=False)
        shutil.copyfile(os.path.join(src_temp, rel), os.path.join(out_temp, rel))
    with open(os.path.join(out_temp, 'project.json'), 'w', encoding='utf-8') as fp:
        json.dump(proj, fp, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(out_dir, 'original_files.txt'), 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(sorted(files)))
    print('배경 오브젝트 %d개 원본으로 다시 붙임 (코드는 지금 것 유지 %d개) · 원본 파일 %d개' % (replaced, kept_code, len(files)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
