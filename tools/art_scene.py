# -*- coding: utf-8 -*-
"""장소 배경 일러스트용 그리기 도구. 1920x1080 에 그린 뒤 960x540 으로 줄인다."""
from art_common import *

W, H = 1920, 1080


class Scene:
    def __init__(self, seed=1, size=(W, H)):
        self.w, self.h = size
        self.im = Image.new('RGBA', size, (0, 0, 0, 255))
        self.d = ImageDraw.Draw(self.im)
        self.rnd = random.Random(seed)

    # ---- 기본
    def sky(self, top, bottom, horizon=0.62):
        g = vgradient((self.w, int(self.h * horizon)), top, bottom).convert('RGBA')
        self.im.paste(g, (0, 0))
        self.im.paste(rgba(bottom), (0, int(self.h * horizon), self.w, self.h))

    def rect(self, x0, y0, x1, y1, fill, outline=None, width=0):
        self.d.rectangle((x0, y0, x1, y1), fill=fill, outline=outline, width=width)

    def poly(self, pts, fill, outline=None):
        self.d.polygon(pts, fill=fill, outline=outline)

    def ell(self, x0, y0, x1, y1, fill, outline=None, width=0):
        self.d.ellipse((x0, y0, x1, y1), fill=fill, outline=outline, width=width)

    def rr(self, x0, y0, x1, y1, r, fill, outline=None, width=0):
        self.d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=fill, outline=outline, width=width)

    def line(self, pts, fill, width=2):
        self.d.line(pts, fill=fill, width=width)

    def blur_layer(self, drawfn, radius, alpha=255):
        """drawfn(draw) 로 그린 레이어를 블러해서 합성 (구름, 빛무리)."""
        layer = Image.new('RGBA', self.im.size, (0, 0, 0, 0))
        drawfn(ImageDraw.Draw(layer))
        layer = layer.filter(ImageFilter.GaussianBlur(radius))
        if alpha != 255:
            a = layer.getchannel('A').point(lambda v: v * alpha // 255)
            layer.putalpha(a)
        self.im = Image.alpha_composite(self.im, layer)
        self.d = ImageDraw.Draw(self.im)

    def glow(self, x, y, r, col, alpha=180):
        self.blur_layer(lambda d: d.ellipse((x - r, y - r, x + r, y + r), fill=rgba(col, alpha)), r * 0.45)

    # ---- 자연
    def sun(self, x, y, r, col=(255, 236, 170)):
        self.glow(x, y, r * 2.6, col, 120)
        self.ell(x - r, y - r, x + r, y + r, rgba(col))

    def clouds(self, n, y0, y1, col=(255, 255, 255), alpha=235, scale=1.0):
        for _ in range(n):
            cx = self.rnd.randint(0, self.w)
            cy = self.rnd.randint(int(y0), int(y1))
            s = self.rnd.uniform(0.8, 1.6) * scale
            for k in range(5):
                ox = self.rnd.randint(-int(120 * s), int(120 * s))
                oy = self.rnd.randint(-int(18 * s), int(18 * s))
                r = int(self.rnd.uniform(40, 80) * s)
                self.ell(cx + ox - r, cy + oy - r * 0.7, cx + ox + r, cy + oy + r * 0.7, rgba(col, alpha))

    def hills(self, base, amp, col, seed=0, freq=0.004, bottom=None):
        r = random.Random(seed + 11)
        ph = [r.uniform(0, 6.28) for _ in range(3)]
        pts = [(0, bottom or self.h)]
        for x in range(0, self.w + 20, 20):
            y = base - amp * (0.55 * math.sin(x * freq + ph[0]) + 0.3 * math.sin(x * freq * 2.3 + ph[1]) + 0.15 * math.sin(x * freq * 5.1 + ph[2]))
            pts.append((x, y))
        pts.append((self.w, bottom or self.h))
        self.poly(pts, rgba(col))

    def tree_round(self, x, base, h, leaf=(70, 160, 70), trunk=(110, 74, 44), hi=None):
        tw = max(6, int(h * 0.09))
        self.rect(x - tw, base - h * 0.45, x + tw, base, rgba(trunk))
        r = h * 0.38
        cy = base - h * 0.68
        hi = hi or lerp(leaf, (255, 255, 255), 0.18)
        self.ell(x - r * 1.05, cy - r * 0.9, x + r * 1.05, cy + r * 0.9, rgba(leaf))
        self.ell(x - r * 0.95, cy - r * 1.0, x + r * 0.35, cy + r * 0.2, rgba(hi, 200))

    def tree_ginkgo(self, x, base, h, leaf=(246, 196, 40), trunk=(96, 70, 48)):
        tw = max(6, int(h * 0.07))
        self.rect(x - tw, base - h * 0.5, x + tw, base, rgba(trunk))
        r = random.Random(int(x) + int(base))
        for _ in range(26):
            ox = r.uniform(-0.28, 0.28) * h
            oy = r.uniform(-0.95, -0.5) * h
            rr = r.uniform(0.09, 0.17) * h
            c = lerp(leaf, (255, 230, 90), r.random() * 0.6)
            self.ell(x + ox - rr, base + oy - rr, x + ox + rr, base + oy + rr, rgba(c, 235))

    def tree_blossom(self, x, base, h, col=(255, 184, 205), trunk=(88, 60, 48)):
        tw = max(6, int(h * 0.06))
        self.rect(x - tw, base - h * 0.5, x + tw, base, rgba(trunk))
        r = random.Random(int(x * 7) + int(base))
        for _ in range(34):
            ox = r.uniform(-0.34, 0.34) * h
            oy = r.uniform(-1.0, -0.45) * h
            rr = r.uniform(0.08, 0.16) * h
            c = lerp(col, (255, 240, 244), r.random() * 0.5)
            self.ell(x + ox - rr, base + oy - rr, x + ox + rr, base + oy + rr, rgba(c, 235))

    def pine(self, x, base, h, col=(40, 110, 70)):
        self.rect(x - 6, base - h * 0.2, x + 6, base, rgba((90, 62, 40)))
        for i in range(3):
            w = h * (0.34 - i * 0.07)
            y = base - h * (0.18 + i * 0.28)
            self.poly([(x - w, y), (x + w, y), (x, y - h * 0.4)], rgba(lerp(col, (255, 255, 255), i * 0.08)))

    def bush(self, x, base, w, col=(60, 140, 70)):
        for k in range(4):
            r = w * (0.22 + 0.04 * (k % 2))
            self.ell(x - w / 2 + k * w / 4 - r, base - r * 1.4, x - w / 2 + k * w / 4 + r, base, rgba(lerp(col, (255, 255, 255), 0.06 * k)))

    def grass(self, y0, col1, col2):
        g = vgradient((self.w, self.h - y0), col1, col2).convert('RGBA')
        self.im.paste(g, (0, y0))

    # ---- 건물/구조물
    def building(self, x, y, w, h, wall, roof=None, win=(190, 225, 255), cols=None, rows=None, door=True, trim=None):
        self.rect(x, y, x + w, y + h, rgba(wall))
        if trim:
            self.rect(x, y, x + w, y + h * 0.04, rgba(trim))
        if roof:
            self.poly([(x - w * 0.04, y), (x + w * 1.04, y), (x + w * 0.9, y - h * 0.16), (x + w * 0.1, y - h * 0.16)], rgba(roof))
        cols = cols or max(2, int(w / 90))
        rows = rows or max(1, int(h / 110))
        gw = w / cols
        gh = (h * (0.7 if door else 0.85)) / rows
        for r_ in range(rows):
            for c in range(cols):
                wx = x + c * gw + gw * 0.22
                wy = y + h * 0.08 + r_ * gh + gh * 0.12
                self.rect(wx, wy, wx + gw * 0.56, wy + gh * 0.66, rgba(win), rgba(lerp(wall, (0, 0, 0), 0.4)), 3)
        if door:
            dw = min(w * 0.18, 120)
            self.rect(x + w / 2 - dw / 2, y + h - h * 0.24, x + w / 2 + dw / 2, y + h, rgba(lerp(wall, (0, 0, 0), 0.45)))

    def windows_grid(self, x, y, w, h, cols, rows, lit=(255, 222, 130), dark=(40, 60, 100), lit_p=0.4):
        gw = w / cols
        gh = h / rows
        for r_ in range(rows):
            for c in range(cols):
                col = lit if self.rnd.random() < lit_p else dark
                self.rect(x + c * gw + gw * 0.2, y + r_ * gh + gh * 0.2, x + c * gw + gw * 0.8, y + r_ * gh + gh * 0.8, rgba(col))

    def person(self, x, base, h, shirt=(220, 80, 80), pants=(50, 60, 90), skin=(244, 205, 170), hair=(40, 30, 30), arms_up=False):
        r = h * 0.09
        # legs
        self.rect(x - h * 0.07, base - h * 0.38, x - h * 0.01, base, rgba(pants))
        self.rect(x + h * 0.01, base - h * 0.38, x + h * 0.07, base, rgba(pants))
        # body
        self.rr(x - h * 0.12, base - h * 0.72, x + h * 0.12, base - h * 0.34, h * 0.05, rgba(shirt))
        # arms
        if arms_up:
            self.line([(x - h * 0.12, base - h * 0.66), (x - h * 0.2, base - h * 0.9)], rgba(skin), int(h * 0.05))
            self.line([(x + h * 0.12, base - h * 0.66), (x + h * 0.2, base - h * 0.9)], rgba(skin), int(h * 0.05))
        else:
            self.line([(x - h * 0.12, base - h * 0.66), (x - h * 0.15, base - h * 0.42)], rgba(skin), int(h * 0.05))
            self.line([(x + h * 0.12, base - h * 0.66), (x + h * 0.15, base - h * 0.42)], rgba(skin), int(h * 0.05))
        # head
        self.ell(x - r * 1.05, base - h * 0.72 - r * 2.0, x + r * 1.05, base - h * 0.72, rgba(skin))
        self.ell(x - r * 1.1, base - h * 0.72 - r * 2.15, x + r * 1.1, base - h * 0.72 - r * 0.9, rgba(hair))

    def crowd(self, n, y0, y1, hmin, hmax, seed=3, xr=None):
        r = random.Random(seed)
        shirts = [(230, 90, 90), (90, 140, 230), (240, 190, 70), (110, 190, 120), (170, 110, 210), (240, 140, 80), (90, 190, 200)]
        hairs = [(35, 28, 28), (80, 55, 40), (30, 30, 40), (120, 90, 60), (200, 200, 200)]
        pts = sorted([(r.randint(*(xr or (0, self.w))), r.randint(y0, y1)) for _ in range(n)], key=lambda p: p[1])
        for x, y in pts:
            h = hmin + (hmax - hmin) * (y - y0) / max(1, (y1 - y0))
            self.person(x, y, h, shirt=r.choice(shirts), pants=r.choice([(50, 60, 90), (70, 70, 80), (40, 50, 70), (110, 90, 70)]), hair=r.choice(hairs))

    def sign(self, cx, cy, text, fsize=70, fill=(255, 248, 230), fg=(70, 40, 20), edge=(110, 70, 40), pad=34, post=False, fontname='black'):
        f = font(fontname, fsize)
        tw, th = text_size(self.d, text, f)
        x0, y0, x1, y1 = cx - tw / 2 - pad, cy - th / 2 - pad * 0.7, cx + tw / 2 + pad, cy + th / 2 + pad * 0.7
        self.rr(x0 + 8, y0 + 10, x1 + 8, y1 + 10, 24, (0, 0, 0, 90))
        self.rr(x0, y0, x1, y1, 24, rgba(fill), rgba(edge), 8)
        self.d.text((cx, cy - th * 0.08), text, font=f, fill=fg, anchor='mm')
        if post:
            self.rect(cx - 10, y1, cx + 10, y1 + 140, rgba(edge))

    def lantern(self, x, y, r=30, col=(255, 90, 70)):
        self.line([(x, y - r * 2.4), (x, y - r)], (60, 40, 30, 255), 4)
        self.glow(x, y, r * 2.2, col, 90)
        self.ell(x - r * 0.8, y - r, x + r * 0.8, y + r, rgba(col))
        self.rect(x - r * 0.4, y - r * 1.1, x + r * 0.4, y - r * 0.9, rgba((60, 40, 30)))
        self.rect(x - r * 0.4, y + r * 0.9, x + r * 0.4, y + r * 1.1, rgba((60, 40, 30)))

    def string_lights(self, x0, y0, x1, y1, sag=60, n=18, cols=((255, 240, 160), (255, 160, 120), (160, 220, 255), (190, 255, 170))):
        pts = []
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
            pts.append((x, y))
        self.line(pts, (40, 30, 30, 255), 4)
        for i, (x, y) in enumerate(pts):
            c = cols[i % len(cols)]
            self.glow(x, y + 10, 26, c, 130)
            self.ell(x - 9, y + 2, x + 9, y + 24, rgba(c))

    def awning(self, x, y, w, h, c1, c2, n=8):
        sw = w / n
        for i in range(n):
            col = c1 if i % 2 == 0 else c2
            self.poly([(x + i * sw, y), (x + (i + 1) * sw, y), (x + (i + 1) * sw + 6, y + h), (x + i * sw - 6, y + h)], rgba(col))
            self.ell(x + i * sw - 6, y + h - 14, x + (i + 1) * sw + 6, y + h + 14, rgba(col))

    def crate(self, x, y, w, h, fruit=None, col=(180, 130, 80)):
        self.rect(x, y, x + w, y + h, rgba(col), (90, 60, 30, 255), 4)
        self.line([(x, y + h * 0.5), (x + w, y + h * 0.5)], (90, 60, 30, 255), 4)
        if fruit:
            r = self.rnd
            n = max(3, int(w / 38))
            for i in range(n):
                fx = x + (i + 0.5) * w / n
                self.ell(fx - 20, y - 26, fx + 20, y + 14, rgba(fruit[r.randint(0, len(fruit) - 1)]))
                self.ell(fx - 8, y - 22, fx - 1, y - 10, (255, 255, 255, 90))

    def peach(self, x, y, r, col=(255, 160, 130)):
        self.ell(x - r, y - r, x + r, y + r, rgba(col))
        self.ell(x - r * 0.45, y - r * 0.6, x - r * 0.05, y - r * 0.25, (255, 255, 255, 110))
        self.ell(x - r * 0.1, y - r * 1.15, x + r * 0.7, y - r * 0.6, rgba((90, 170, 80)))

    def petals(self, n, col=(255, 200, 215), seed=5, area=None):
        r = random.Random(seed)
        a = area or (0, 0, self.w, self.h)
        for _ in range(n):
            x = r.randint(a[0], a[2])
            y = r.randint(a[1], a[3])
            s = r.randint(7, 15)
            self.ell(x - s, y - s * 0.6, x + s, y + s * 0.6, rgba(col, r.randint(150, 240)))

    def vignette(self, strength=70):
        v = Image.new('L', self.im.size, 0)
        vd = ImageDraw.Draw(v)
        for i in range(0, 60):
            a = int(strength * (i / 60) ** 2)
            vd.rectangle((i * 6, i * 4, self.w - i * 6, self.h - i * 4), outline=0)
        # 간단: 가장자리 어둡게
        mask = Image.new('L', (self.w // 8, self.h // 8), 0)
        md = ImageDraw.Draw(mask)
        for i in range(30):
            md.rectangle((i, i, mask.width - i, mask.height - i), outline=int(strength * (1 - i / 30) ** 2))
        mask = mask.resize(self.im.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
        dark = Image.new('RGBA', self.im.size, (0, 0, 0, 255))
        dark.putalpha(mask)
        self.im = Image.alpha_composite(self.im, dark)
        self.d = ImageDraw.Draw(self.im)

    def tint(self, col, alpha):
        ov = Image.new('RGBA', self.im.size, rgba(col, alpha))
        self.im = Image.alpha_composite(self.im, ov)
        self.d = ImageDraw.Draw(self.im)

    def finish(self, name, vignette=60):
        if vignette:
            self.vignette(vignette)
        out = self.im.convert('RGB').resize((960, 540), Image.LANCZOS)
        return save(quantize_png(out, 256), name), out
