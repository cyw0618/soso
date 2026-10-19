# -*- coding: utf-8 -*-
"""업로드 한도 찾기용: 완성된 .ent 에서 일부 장면(게임)을 빼고 더 작은 .ent 를 만든다 (개발용, 게임 진행은 안 됨).

    python3 tools/split_ent.py 입력.ent 출력.ent 접두어,접두어   # 이 접두어로 시작하는 장면을 뺀다 (예: 대선,시장)
"""
import sys, io, gzip, json, tarfile


def main(src_path, out_path, prefixes):
    src = tarfile.open(src_path)
    pj = json.load(src.extractfile('temp/project.json'))
    drop = {s['id'] for s in pj['scenes'] if s['name'].startswith(tuple(prefixes))}
    pj['scenes'] = [s for s in pj['scenes'] if s['id'] not in drop]
    pj['objects'] = [o for o in pj['objects'] if o['scene'] not in drop]
    used = set()
    for o in pj['objects']:
        for p in o['sprite']['pictures']:
            used.add(p['filename'])
        for s in o['sprite'].get('sounds', []):
            used.add(s['filename'])
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as out:
        for m in src.getmembers():
            if m.isdir():
                out.addfile(m)
                continue
            if m.name.endswith('project.json'):
                data = json.dumps(pj, ensure_ascii=False, separators=(',', ':')).encode()
            else:
                if m.name.rsplit('/', 1)[-1].split('.')[0] not in used:
                    continue
                data = src.extractfile(m).read()
            ti = tarfile.TarInfo(m.name)
            ti.size, ti.mode, ti.mtime = len(data), m.mode, m.mtime
            out.addfile(ti, io.BytesIO(data))
    with open(out_path, 'wb') as f:
        f.write(gzip.compress(raw.getvalue(), 9, mtime=0))
    print(out_path, '장면', len(pj['scenes']), '오브젝트', len(pj['objects']), '그림', len(used))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3].split(','))
