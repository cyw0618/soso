# -*- coding: utf-8 -*-
"""완성된 .ent 의 project.json 을 줄인다 (엔트리 작품 업로드 용량 제한 대응).

  - 블록 id 삭제: 엔트리가 불러올 때 id 가 없으면 새로 만든다 (Entry.Block: if (!block.id) block.id = generateId()).
  - --array: 오브젝트/함수의 script 를 '글자'가 아니라 JSON 배열 그대로 넣는다 (따옴표 이스케이프가 사라져 크게 줄지만, 엔트리 쪽 가져오기가 받아 주는지는 확인이 필요).

    python3 tools/pack_json.py 입력.ent 출력.ent [--array]
"""
import sys
import io
import gzip
import json
import tarfile


def strip(b):
    if isinstance(b, dict):
        b.pop('id', None)
        for p in b.get('params', []):
            strip(p)
        for st in b.get('statements', []):
            for s in st:
                strip(s)
    elif isinstance(b, list):
        for x in b:
            strip(x)


def main(src_path, out_path, as_array):
    src = tarfile.open(src_path)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as out:
        for m in src.getmembers():
            if m.isdir():
                out.addfile(m)
                continue
            data = src.extractfile(m).read()
            if m.name.endswith('project.json'):
                pj = json.loads(data)
                for o in pj['objects']:
                    th = json.loads(o['script'])
                    strip(th)
                    o['script'] = th if as_array else json.dumps(th, ensure_ascii=False, separators=(',', ':'))
                for f in pj['functions']:
                    th = json.loads(f['content'])
                    strip(th)
                    f['content'] = json.dumps(th, ensure_ascii=False, separators=(',', ':'))    # 함수는 글자 그대로 (배열이면 엔트리가 빈 함수로 본다)
                data = json.dumps(pj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
                print('project.json %.2f MB' % (len(data) / 1e6))
            ti = tarfile.TarInfo(m.name)
            ti.size, ti.mode, ti.mtime = len(data), m.mode, m.mtime
            out.addfile(ti, io.BytesIO(data))
    with open(out_path, 'wb') as f:
        f.write(gzip.compress(raw.getvalue(), 9, mtime=0))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--array' in sys.argv)
