# -*- coding: utf-8 -*-
"""money_fix 결과 폴더 → .ent (쓰는 그림만, 그림은 크기·이름 그대로 색 수만 줄여 다시 압축).

    python3 -I tools/money_pack.py 결과폴더 출력.ent

  - PNG: libimagequant 256색(디더링) + oxipng, 더 작아질 때만
  - JPG: 원본 그대로 (다시 저장한 JPG 는 엔트리 사이트에서 배경이 사라졌음)
  - 미리보기(thumb): 64색
"""
import gzip
import io
import json
import os
import sys
import tarfile

from PIL import Image


def png_small(data, colors):
    im = Image.open(io.BytesIO(data))
    out = data
    if im.mode != 'P':
        try:
            import imagequant
            q = imagequant.quantize_pil_image(im.convert('RGBA'), dithering_level=1.0, max_colors=colors)
        except Exception:
            q = im.convert('RGBA').quantize(colors=colors, method=Image.Quantize.FASTOCTREE)
        buf = io.BytesIO()
        q.save(buf, 'PNG', optimize=True)
        out = buf.getvalue()
    try:
        import oxipng
        out = oxipng.optimize_from_memory(out, level=4)
    except Exception:
        pass
    return out if len(out) < len(data) else data


def jpg_small(data, quality=82):
    im = Image.open(io.BytesIO(data))
    buf = io.BytesIO()
    im.convert('RGB').save(buf, 'JPEG', quality=quality, optimize=True, progressive=True)
    out = buf.getvalue()
    return out if len(out) < len(data) else data


def main(out_dir, dst):
    base = os.path.abspath(out_dir)
    proj_path = os.path.join(base, 'temp', 'project.json')
    proj = json.load(open(proj_path, encoding='utf-8'))
    files = set()
    for o in proj['objects']:
        for p in o['sprite'].get('pictures', []):
            files.add(p['fileurl'])
            if p.get('thumbUrl'):
                files.add(p['thumbUrl'])
        for s in o['sprite'].get('sounds', []):
            files.add(s['fileurl'])
    raw = io.BytesIO()
    before = after = 0
    dirs = set()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as tar:
        def add_dir(path):
            parts = path.split('/')
            for i in range(1, len(parts)):
                d = '/'.join(parts[:i]) + '/'
                if d not in dirs:
                    dirs.add(d)
                    ti = tarfile.TarInfo(d)
                    ti.type = tarfile.DIRTYPE
                    ti.mode = 0o755
                    tar.addfile(ti)

        def add(name, data):
            add_dir(name)
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            ti.mode = 0o644
            tar.addfile(ti, io.BytesIO(data))

        data = open(proj_path, 'rb').read()
        add('temp/project.json', data)
        for f in sorted(files):
            data = open(os.path.join(base, f), 'rb').read()
            before += len(data)
            if '/thumb/' in f and f.endswith('.png'):
                data = png_small(data, 64)
            elif f.endswith('.png'):
                data = png_small(data, 256)
            elif f.endswith('.jpg') or f.endswith('.jpeg'):
                pass        # JPG(장면 배경)는 원본 그대로: 다시 저장(프로그레시브)하면 엔트리에 올렸을 때 배경이 안 나왔음
            after += len(data)
            add(f, data)
    with open(dst, 'wb') as fp:
        fp.write(gzip.compress(raw.getvalue(), 9, mtime=0))
    print('그림 %d개: %.2fMB → %.2fMB' % (len(files), before / 1e6, after / 1e6))
    print('.ent %.2fMB' % (os.path.getsize(dst) / 1e6))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
