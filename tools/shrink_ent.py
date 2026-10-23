# -*- coding: utf-8 -*-
"""완성된 .ent 의 그림 용량을 줄인다 (크기·파일 이름은 그대로, 색만 256색 이하로).

    python3 tools/shrink_ent.py 군수집_막내아들.ent
"""
import sys
import io
import gzip
import tarfile
import subprocess
from PIL import Image


def shrink(png, colors=128):
    """libimagequant(고품질 팔레트 변환) + oxipng(손실 없는 재압축). 더 작아지지 않으면 원래 그림 그대로."""
    im = Image.open(io.BytesIO(png))
    if im.mode == 'P' or len(png) < 4000:
        out = png
    else:
        try:
            import imagequant
            q = imagequant.quantize_pil_image(im.convert('RGBA'), dithering_level=1.0, max_colors=colors)
        except Exception:
            q = im.convert('RGBA').quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        buf = io.BytesIO()
        q.save(buf, 'PNG', optimize=True)
        out = buf.getvalue()
    try:
        import oxipng
        out = oxipng.optimize_from_memory(out, level=4)
    except Exception:
        pass
    return out if len(out) < len(png) else png


def shrink_sound(mp3):
    """효과음·배경음을 모노 56kbps 로 다시 인코딩 (길이는 그대로)."""
    try:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-ac', '1', '-ar', '32000', '-b:a', '56k', '-f', 'mp3', 'pipe:1'],
                           input=mp3, capture_output=True, check=True)
        return r.stdout if 0 < len(r.stdout) < len(mp3) else mp3
    except Exception:
        return mp3


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
            if '/sound/' in m.name:
                new = shrink_sound(data)
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
