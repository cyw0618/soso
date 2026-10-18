# -*- coding: utf-8 -*-
"""완성된 .ent 의 그림 용량을 줄인다 (크기·파일 이름은 그대로, 색만 256색 이하로).

    python3 tools/shrink_ent.py 군수집_막내아들.ent
"""
import sys
import io
import gzip
import tarfile
from PIL import Image


def shrink(png):
    im = Image.open(io.BytesIO(png))
    if im.mode == 'P':
        best = png
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        return buf.getvalue() if len(buf.getvalue()) < len(best) else best
    if len(png) < 6000:
        return png
    if im.mode == 'RGB':
        q = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    else:
        q = im.convert('RGBA').quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    buf = io.BytesIO()
    q.save(buf, 'PNG', optimize=True)
    return buf.getvalue() if len(buf.getvalue()) < len(png) else png


def main(path):
    src = tarfile.open(path)
    raw = io.BytesIO()
    saved = 0
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as out:
        for m in src.getmembers():
            if m.isdir():
                out.addfile(m)
                continue
            data = src.extractfile(m).read()
            if '/image/' in m.name:
                new = shrink(data)
                saved += len(data) - len(new)
                data = new
            ti = tarfile.TarInfo(m.name)
            ti.size = len(data)
            ti.mode = m.mode
            ti.mtime = m.mtime
            out.addfile(ti, io.BytesIO(data))
    with open(path, 'wb') as f:
        f.write(gzip.compress(raw.getvalue(), 9, mtime=0))
    print('그림에서 %.1f MB 줄임' % (saved / 1e6))


if __name__ == '__main__':
    main(sys.argv[1])
