# -*- coding: utf-8 -*-
"""게임 효과음/배경음을 numpy 로 직접 합성해서 mp3 로 저장 (외부 음원 없음, 모두 새로 만든 소리).

    python3 tools/make_sounds.py   → tools/assets_src/sounds/*.mp3 + sounds.json(길이)

mp3 인코딩에는 lameenc(PyPI) 가 필요하다. 만들어 둔 mp3 는 저장소에 들어 있으므로 빌드할 때는 필요 없다.
"""
import os
import json
import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets_src', 'sounds')
rng = np.random.default_rng(1927)


# ------------------------------------------------------------------ 기본 재료
def tt(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, d=0.05, s=0.6, r=0.1, hold=None):
    """ADSR 엔벨로프 (n 샘플)."""
    a_, d_, r_ = int(a * SR), int(d * SR), int(r * SR)
    h_ = n - a_ - d_ - r_ if hold is None else int(hold * SR)
    h_ = max(0, h_)
    e = np.concatenate([np.linspace(0, 1, max(1, a_)), np.linspace(1, s, max(1, d_)), np.full(h_, s),
                        np.linspace(s, 0, max(1, r_))])
    if len(e) < n:
        e = np.concatenate([e, np.zeros(n - len(e))])
    return e[:n]


def decay(n, k):
    return np.exp(-np.arange(n) / SR * k)


def osc(freq, d, kind='sine', phase=0.0):
    t = tt(d)
    f = np.broadcast_to(np.asarray(freq, dtype=float), t.shape) if np.ndim(freq) else np.full(t.shape, float(freq))
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    if kind == 'sine':
        return np.sin(ph)
    if kind == 'tri':
        return 2 / np.pi * np.arcsin(np.sin(ph))
    if kind == 'square':
        return np.tanh(np.sin(ph) * 6) * 0.8
    if kind == 'saw':
        x = (ph / (2 * np.pi)) % 1.0
        return 2 * x - 1
    raise ValueError(kind)


def noise(d):
    return rng.uniform(-1, 1, int(SR * d))


def filt(x, lo=None, hi=None):
    """FFT 로 대역 통과 (lo~hi Hz)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def note_hz(n):
    """MIDI 번호 → Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def mix(total_d, events):
    """events: [(시작초, 신호, 볼륨)]"""
    out = np.zeros(int(SR * total_d) + SR)
    for t0, sig, vol in events:
        i = int(t0 * SR)
        j = min(len(out), i + len(sig))
        if j > i:
            out[i:j] += sig[:j - i] * vol
    return out[:int(SR * total_d)]


def norm(x, peak=0.89):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def soft(x, drive=1.4):
    return np.tanh(x * drive) / np.tanh(drive)


# ------------------------------------------------------------------ 악기
def kick(d=0.35):
    t = tt(d)
    f = 45 + 110 * np.exp(-t * 28)
    return osc(f, d) * decay(len(t), 9) + filt(noise(d), hi=2000) * decay(len(t), 60) * 0.25


def snare(d=0.25):
    n = len(tt(d))
    return filt(noise(d), lo=900, hi=8000) * decay(n, 18) * 0.9 + osc(190, d) * decay(n, 25) * 0.5


def hat(d=0.06, open_=False):
    n = len(tt(d))
    return filt(noise(d), lo=6000) * decay(n, 20 if open_ else 70) * 0.6


def clap(d=0.2):
    n = len(tt(d))
    x = filt(noise(d), lo=1000, hi=6000)
    e = np.zeros(n)
    for k in range(3):
        i = int(k * 0.011 * SR)
        e[i:] += decay(n - i, 40) * (0.6 if k < 2 else 1.0)
    return x * e * 0.8


def bass(midi, d):
    f = note_hz(midi)
    x = osc(f, d, 'saw') * 0.6 + osc(f / 2, d, 'sine') * 0.6
    return filt(x, hi=700) * env(len(x), 0.004, 0.08, 0.7, 0.04)


def pluck(midi, d, bright=3000):
    f = note_hz(midi)
    x = osc(f, d, 'saw') * 0.5 + osc(f * 1.005, d, 'square') * 0.3
    return filt(x, hi=bright) * decay(len(x), 7) * env(len(x), 0.002, 0.02, 1.0, 0.03)


def pad(midis, d):
    x = np.zeros(len(tt(d)))
    for m in midis:
        f = note_hz(m)
        for det in (0.996, 1.0, 1.004):
            x += osc(f * det, d, 'saw', phase=rng.uniform(0, 6))
    x = filt(x, hi=1600) / (len(midis) * 3)
    return x * env(len(x), 0.4, 0.3, 0.8, 0.6)


def piano(midi, d):
    f = note_hz(midi)
    x = osc(f, d, 'tri') * 0.7 + osc(f * 2, d, 'sine') * 0.25 + osc(f * 3, d, 'sine') * 0.08
    return x * decay(len(x), 3.2) * env(len(x), 0.003, 0.05, 1.0, 0.08)


def lead(midi, d):
    f = note_hz(midi)
    t = tt(d)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 3, 0, 1)
    x = osc(f * vib, d, 'square') * 0.5 + osc(f * vib * 2, d, 'sine') * 0.15
    return filt(x, hi=4500) * env(len(x), 0.01, 0.08, 0.7, 0.08)


def timpani(midi, d=1.2):
    f = note_hz(midi)
    x = osc(f, d) * 0.8 + osc(f * 1.5, d) * 0.25 + filt(noise(d), hi=400) * 0.3
    return x * decay(len(x), 3.5) * env(len(x), 0.003, 0.03, 1.0, 0.1)


# ------------------------------------------------------------------ 효과음
def sfx():
    S = {}
    n = lambda d: len(tt(d))
    S['click'] = norm(filt(noise(0.03), lo=2000) * decay(n(0.03), 150) * 0.5 + osc(1800, 0.03) * decay(n(0.03), 120), 0.6)
    S['beep'] = norm(osc(880, 0.14, 'square') * env(n(0.14), 0.003, 0.02, 0.8, 0.04), 0.55)
    S['go'] = norm((osc(1320, 0.4, 'square') + osc(1760, 0.4) * 0.4) * env(n(0.4), 0.003, 0.05, 0.7, 0.2), 0.6)
    t = tt(0.7)
    S['whistle'] = norm(osc(2900 + 180 * np.sin(2 * np.pi * 32 * t), 0.7) * env(n(0.7), 0.01, 0.05, 0.9, 0.12) +
                        filt(noise(0.7), lo=2500, hi=4000) * 0.15 * env(n(0.7), 0.01, 0.05, 0.9, 0.12), 0.6)
    S['stamp'] = norm(osc(55 + 60 * np.exp(-tt(0.35) * 30), 0.35) * decay(n(0.35), 11) + filt(noise(0.35), hi=1500) * decay(n(0.35), 40) * 0.6, 0.85)
    fan = mix(1.5, [(0.0, lead(72, 0.16), 0.5), (0.15, lead(76, 0.16), 0.5), (0.3, lead(79, 0.16), 0.5),
                    (0.45, lead(84, 0.9), 0.6), (0.45, pad([60, 64, 67, 72], 1.0), 0.6), (0.45, timpani(48, 1.0), 0.6)])
    S['fanfare'] = norm(fan, 0.8)
    S['coin'] = norm(np.concatenate([osc(988, 0.07, 'square') * 0.6, osc(1319, 0.22, 'square') * decay(n(0.22), 10) * 0.6]), 0.5)
    S['good'] = norm(mix(0.6, [(0, piano(84, 0.4), 1), (0.08, piano(88, 0.4), 1), (0.16, piano(91, 0.45), 1)]), 0.6)
    S['bad'] = norm(filt(osc(220 * np.exp(-tt(0.45) * 1.2), 0.45, 'saw'), hi=1500) * env(n(0.45), 0.005, 0.05, 0.8, 0.1), 0.55)
    ching = filt(noise(0.06), lo=3000) * decay(n(0.06), 60)
    bell = (osc(2637, 0.5) + osc(3520, 0.5) * 0.6) * decay(n(0.5), 6)
    S['cash'] = norm(mix(0.6, [(0, ching, 0.7), (0.05, bell, 0.6)]), 0.55)
    S['news'] = norm(mix(0.25, [(0, osc(1200, 0.08) * env(n(0.08), 0.002, 0.02, 0.7, 0.03), 1), (0.1, osc(1600, 0.1) * env(n(0.1), 0.002, 0.02, 0.7, 0.04), 1)]), 0.4)
    t = tt(1.4)
    siren = osc(np.where((t * 2.5) % 1 < 0.5, 760, 960), 1.4, 'square')
    S['alarm'] = norm(filt(siren, hi=3000) * env(n(1.4), 0.01, 0.05, 0.9, 0.2), 0.5)
    S['pop'] = norm(filt(noise(0.12), lo=400) * decay(n(0.12), 45) + osc(500 * np.exp(-tt(0.12) * 20), 0.12) * decay(n(0.12), 30) * 0.6, 0.65)
    S['hit'] = norm(filt(noise(0.16), hi=3000) * decay(n(0.16), 35) + osc(110 * np.exp(-tt(0.16) * 8), 0.16) * decay(n(0.16), 18), 0.75)
    S['jump'] = norm(osc(300 + 500 * tt(0.18) / 0.18, 0.18, 'square') * env(n(0.18), 0.003, 0.03, 0.7, 0.05), 0.4)
    clickx = filt(noise(0.02), lo=2500) * decay(n(0.02), 200)
    S['shutter'] = norm(mix(0.2, [(0, clickx, 1), (0.07, clickx, 0.8), (0.0, filt(noise(0.15), lo=1000, hi=6000) * decay(n(0.15), 25), 0.3)]), 0.7)
    sp = filt(noise(0.6), lo=200, hi=3000) * env(n(0.6), 0.01, 0.1, 0.5, 0.4)
    S['splash'] = norm(sp + filt(noise(0.6), lo=2500) * decay(n(0.6), 8) * 0.3, 0.6)
    for k, m in enumerate((64, 69, 73, 76)):
        f = note_hz(m)
        x = osc(f, 0.32, 'tri') * 0.8 + osc(f * 2, 0.32) * 0.15
        S['tone%d' % (k + 1)] = norm(x * env(len(x), 0.005, 0.05, 0.8, 0.08), 0.5)
    d = 2.6
    t = tt(d)
    roll = np.zeros(len(t))
    for i in range(int(d * 22)):
        tm = i / 22
        s_ = snare(0.08) * (0.3 + 0.7 * tm / d)
        a = int(tm * SR)
        roll[a:a + len(s_)] += s_[:len(roll) - a]
    S['drumroll'] = norm(roll, 0.7)
    wah = []
    for k, (m, dd) in enumerate(((58, 0.32), (57, 0.32), (56, 0.32), (55, 1.0))):
        f = note_hz(m)
        tw = tt(dd)
        x = filt(osc(f * (1 + 0.01 * np.sin(2 * np.pi * 6 * tw)), dd, 'saw'), hi=1100) * (0.6 + 0.4 * np.sin(np.pi * tw / dd))
        wah.append(x * env(len(x), 0.02, 0.05, 0.8, 0.08))
    S['fail_big'] = norm(np.concatenate(wah), 0.6)
    S['tick'] = norm(osc(2000, 0.04) * decay(n(0.04), 90), 0.4)
    return S


# ------------------------------------------------------------------ 배경음
def song(bpm, bars, chords, drums=True, bass_pat=None, lead_notes=None, pad_vol=0.35, kick_every=1, hats=True,
         stabs=True, intro_bars=0, piano_arp=False, tail=0.0):
    beat = 60.0 / bpm
    bar = beat * 4
    total = bars * bar + tail
    ev = []
    for b in range(bars):
        t0 = b * bar
        ch = chords[b % len(chords)]
        root = ch[0]
        in_intro = b < intro_bars
        ev.append((t0, pad([c + 12 for c in ch], bar + 0.4), pad_vol))
        if piano_arp:
            seq = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[1] + 12, ch[0] + 24, ch[2] + 12]
            for k, m in enumerate(seq):
                ev.append((t0 + k * beat / 2, piano(m, 1.2), 0.32))
        if not in_intro:
            pat = bass_pat or [0, None, 0, None, 0, None, 7, None]
            for k, iv in enumerate(pat):
                if iv is not None:
                    ev.append((t0 + k * beat / 2, bass(root - 12 + iv, beat / 2 * 0.95), 0.55))
            if stabs:
                for k in (1, 3):
                    for c in ch:
                        ev.append((t0 + k * beat + beat / 2, pluck(c + 12, 0.18), 0.12))
        if drums:
            for k in range(4):
                if not in_intro and k % kick_every == 0:
                    ev.append((t0 + k * beat, kick(), 0.9))
                if not in_intro and k in (1, 3):
                    ev.append((t0 + k * beat, snare(), 0.45))
                    ev.append((t0 + k * beat, clap(), 0.25))
                if hats:
                    ev.append((t0 + k * beat, hat(), 0.35))
                    ev.append((t0 + k * beat + beat / 2, hat(0.12, True), 0.3 if not in_intro else 0.45))
    if lead_notes:
        for (b, step, m, ln) in lead_notes:
            ev.append((b * bar + step * beat / 2, lead(m, ln * beat / 2), 0.32))
    return norm(soft(mix(total, ev), 1.3), 0.86), total


def bgm_rhythm():
    # 120BPM, 1~4박(2초)은 하이햇 카운트인, 채보는 2.0초부터. 12마디 = 24초
    A, F, C, G = [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]
    chords = [A, F, C, G]
    mel = []
    phrase = [(0, 69, 2), (2, 72, 2), (4, 76, 3), (7, 74, 1), (8, 72, 2), (10, 69, 2), (12, 67, 2), (14, 69, 2)]
    for b0 in (1, 3, 5, 7, 9):
        for st, m, ln in phrase:
            bb = b0 + st // 8
            mel.append((bb, st % 8, m + (0 if b0 % 4 == 1 else 0), ln))
    x, total = song(120, 12, chords, bass_pat=[0, None, 0, 12, 0, None, 7, 12], lead_notes=mel, intro_bars=1)
    return x, total


def bgm_title():
    Am, F, Dm, E = [57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]
    beat = 60 / 72
    bars = 8
    x, total = song(72, bars, [Am, F, Dm, E], drums=False, bass_pat=[0, None, None, None, 0, None, None, None],
                    pad_vol=0.5, stabs=False, piano_arp=True)
    ev = [(b * beat * 4, timpani(45 if b % 4 != 3 else 40), 0.5) for b in range(bars)]
    tim = mix(total, ev)
    return norm(soft(x + tim * 0.8, 1.2), 0.8), total


def bgm_map():
    Am, G, F, E = [57, 60, 64], [55, 59, 62], [53, 57, 60], [52, 56, 59]
    x, total = song(100, 8, [Am, G, F, E], bass_pat=[0, 0, 0, 0, 0, 0, 0, 0], pad_vol=0.4, kick_every=2, stabs=False,
                    hats=True)
    return norm(x, 0.7), total


def bgm_game():
    C, Am, F, G = [60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]
    mel = []
    riff = [(0, 72, 1), (1, 76, 1), (2, 79, 1), (3, 76, 1), (4, 81, 2), (6, 79, 2)]
    for b in range(8):
        for st, m, ln in riff:
            mel.append((b, st, m - (0 if b % 2 == 0 else 3), ln))
    x, total = song(132, 8, [C, Am, F, G], bass_pat=[0, 12, 0, 12, 0, 12, 7, 12], lead_notes=mel)
    return norm(x, 0.75), total


# ------------------------------------------------------------------ 저장
def save_mp3(name, x):
    import lameenc
    os.makedirs(OUT, exist_ok=True)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(128)
    enc.set_in_sample_rate(SR)
    enc.set_channels(1)
    enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    with open(os.path.join(OUT, name + '.mp3'), 'wb') as f:
        f.write(data)
    return round(len(x) / SR, 2)


def build():
    meta = {}
    for k, v in sfx().items():
        meta[k] = save_mp3('sfx_' + k, v)
    for nm, fn in (('bgm_rhythm', bgm_rhythm), ('bgm_title', bgm_title), ('bgm_map', bgm_map), ('bgm_game', bgm_game)):
        x, total = fn()
        meta[nm] = save_mp3(nm, x)
    with open(os.path.join(OUT, 'sounds.json'), 'w') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return meta


if __name__ == '__main__':
    m = build()
    print(json.dumps(m, ensure_ascii=False))
