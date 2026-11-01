# -*- coding: utf-8 -*-
"""money_game(.ent) 손보기: 저장 지킴이 + 시작 인트로 + 코드 줄이기.

    python3 -I tools/money_fix.py 원본/temp 결과폴더 [--no-slim]

  1) 저장 지킴이: 모든 장면(타이틀 빼고)에 0.5초마다 '저장요청'을 확인해 저장하는 코드 묶음을 붙인다.
     - 하루 진행 코드(HUD) 안에서 바로 저장하던 것을 지킴이로 옮김 → 서버 응답이 늦어도 게임 시간이 멈추지 않음
     - 하루가 안 흐르는 장면(카지노·바카라·알바들·게임설정)에서도 저장·자동 저장(20초)이 됨
     - 저장 뒤 서버에 들어간 값을 다시 읽어 맞는지 확인, 다르면 다시 저장
     - 처음 시작할 때 저장 칸을 못 받았으면(서버가 느림) 저장할 때 다시 찾음 (내 계정 키일 때만)
  2) 인트로: 타이틀 장면 맨 위에 덮개 + 로고 조각(동전·글자·부제)을 올려 4초 남짓 연출, 화면을 누르면 건너뜀.
     마지막 장면이 타이틀 로고와 같은 자리라서 덮개가 걷히면 그대로 타이틀로 이어진다.
  3) rawslim 으로 같은 코드 → 함수, 값만 다른 코드 → 매개변수 함수 …
"""
import collections
import hashlib
import io
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import entrygen as EG  # noqa: E402
from entrygen import (B, V, t, setv, chg, wait, rep, forever, if_, ifelse, eq, ne, gt, lt, ge, le, and_, add, sub,  # noqa: E402
                      mul, rnd, LGET, LLEN, show, hide, xy, lx, ly, cast, on_run, on_msg, on_clone, fx, fx_add,
                      size, grow, next_shape, obj_x, obj_y, clone_self, del_clone)
import rawslim  # noqa: E402
from rawslim import RawProject, RObj  # noqa: E402

LOGO_FILE = '7d35382406daa4bd4ff4f3e5ec7be7a2'      # 타이틀로고 그림 (720x192, 무대 (0,78) 0.5배)


def stage_of(px, py):
    """로고 그림 좌표 → 무대 좌표."""
    return (-180 + px * 0.5, 126 - py * 0.5)


def func(fid):
    return {'type': 'func_' + fid, 'params': [], 'statements': []}


def stop_others():
    return B('stop_object', TARGET='otherThread')


def cur_size():
    return B('coordinate_object', VALUE='self', COORDINATE='size')


def on_mouse():
    return B('mouse_clicked')


# ------------------------------------------------------------------ 그림
class Art:
    def __init__(self, out_temp):
        self.out = out_temp
        self.bytes = 0

    def pic(self, im, name):
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        data = buf.getvalue()
        md5 = hashlib.md5(data).hexdigest()
        d = os.path.join(self.out, md5[:2], md5[2:4])
        os.makedirs(os.path.join(d, 'image'), exist_ok=True)
        os.makedirs(os.path.join(d, 'thumb'), exist_ok=True)
        with open(os.path.join(d, 'image', md5 + '.png'), 'wb') as fp:
            fp.write(data)
        th = im.copy()
        th.thumbnail((96, 96))
        th.save(os.path.join(d, 'thumb', md5 + '.png'), 'PNG', optimize=True)
        self.bytes += len(data)
        return {'id': EG.new_id(), 'name': name, 'filename': md5, 'imageType': 'png',
                'fileurl': 'temp/%s/%s/image/%s.png' % (md5[:2], md5[2:4], md5),
                'thumbUrl': 'temp/%s/%s/thumb/%s.png' % (md5[:2], md5[2:4], md5),
                'dimension': {'width': im.width, 'height': im.height}}


def alias(p, name):
    """같은 파일을 다른 오브젝트에서 쓰는 그림 항목 (파일은 하나)."""
    q = dict(p, id=EG.new_id(), name=name)
    q['dimension'] = dict(p['dimension'])
    return q


def make_art(art, logo_path):
    logo = Image.open(logo_path).convert('RGBA')
    out = {}
    # 동전 (돌아가는 6장): 가로로 눌러 회전처럼
    coin = logo.crop((18, 17, 156, 157))
    W, H = coin.size
    frames = []
    for i, f in enumerate((1.0, 0.78, 0.42, 0.1, 0.42, 0.78)):
        w = max(4, int(round(W * f)))
        c = coin.resize((w, H), Image.LANCZOS)
        if f < 1:
            r, g, b, a = c.split()
            k = 0.72 + 0.28 * f
            r, g, b = (ch.point(lambda v, k=k: int(v * k)) for ch in (r, g, b))
            c = Image.merge('RGBA', (r, g, b, a))
        can = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        can.paste(c, ((W - w) // 2, 0), c)
        frames.append(art.pic(can, 'c%d' % (i + 1)))
    out['coin'] = frames
    out['coin_box'] = (18, 17, 156, 157)
    # 글자 'money game' + 반짝이는 띠 5장
    word = logo.crop((159, 57, 701, 135))
    out['word_box'] = (159, 57, 701, 135)
    wf = [art.pic(word, 'w0')]
    ww, wh = word.size
    px = word.load()
    for k in range(5):
        cx = -60 + (ww + 120) * (k + 0.5) / 5.0
        g = word.copy()
        q = g.load()
        for y in range(wh):
            for x in range(ww):
                r, gg, b, a = px[x, y]
                if a == 0:
                    continue
                d = abs((x - cx) - (y - wh / 2) * 0.6)
                s = max(0.0, 1 - d / 34.0) * 0.85
                if s > 0:
                    q[x, y] = (int(r + (255 - r) * s), int(gg + (255 - gg) * s), int(b + (255 - b) * s), a)
        wf.append(art.pic(g, 'g%d' % (k + 1)))
    out['word'] = wf
    # 부제 '돈을 버는 모든 방법'
    out['sub_box'] = (164, 145, 556, 173)
    out['sub'] = [art.pic(logo.crop(out['sub_box']), '부제')]
    # 금빛 후광
    S = 200
    gl = Image.new('RGBA', (S, S))
    gp = gl.load()
    for y in range(S):
        for x in range(S):
            r = math.hypot(x - S / 2 + 0.5, y - S / 2 + 0.5) / (S / 2)
            a = max(0.0, 1 - r) ** 2 * 0.9
            gp[x, y] = (255, 200, 80, int(a * 255))
    out['glow'] = [art.pic(gl, '후광')]
    # 퍼지는 고리
    S = 240
    ring = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    d.ellipse((14, 14, S - 14, S - 14), outline=(255, 226, 140, 255), width=9)
    ring = ring.filter(ImageFilter.GaussianBlur(3))
    out['ring'] = [art.pic(ring, '고리')]
    # 덮개 (가운데가 살짝 밝은 남색 → 가장자리 검정), 3배로 키워 씀
    cw, ch = 160, 90
    cur = Image.new('RGBA', (cw, ch))
    cp = cur.load()
    for y in range(ch):
        for x in range(cw):
            r = min(1.0, math.hypot((x - cw / 2 + 0.5) / (cw / 2), (y - ch / 2 + 0.5) / (ch / 2)) / 1.25)
            k = (1 - r) ** 1.6
            cp[x, y] = (int(4 + 16 * k), int(5 + 21 * k), int(12 + 40 * k), 255)
    out['curtain'] = [art.pic(cur, '덮개')]
    # 섬광 (흰색), 16배로 키워 씀
    out['flash'] = [art.pic(Image.new('RGBA', (32, 18), (255, 250, 235, 255)), '섬광')]
    return out


# ------------------------------------------------------------------ 오브젝트
def sprite(name, scene, pics, x, y, scale):
    p0 = pics[0]['dimension']
    return {'id': EG.new_id(), 'name': name, 'objectType': 'sprite', 'rotateMethod': 'free', 'scene': scene,
            'lock': False, 'sprite': {'pictures': pics, 'sounds': []}, 'selectedPictureId': pics[0]['id'],
            'script': '[]',
            'entity': {'x': x, 'y': y, 'regX': p0['width'] / 2.0, 'regY': p0['height'] / 2.0, 'scaleX': scale,
                       'scaleY': scale, 'rotation': 0, 'direction': 90, 'width': p0['width'],
                       'height': p0['height'], 'visible': False}}


def textbox(name, scene, text, x, y, size_px, colour):
    w = len(text) * size_px * 0.9
    return {'id': EG.new_id(), 'name': name, 'text': text, 'objectType': 'textBox', 'rotateMethod': 'free',
            'scene': scene, 'lock': False, 'sprite': {'pictures': [], 'sounds': []}, 'script': '[]',
            'entity': {'x': x, 'y': y, 'regX': w / 2, 'regY': size_px / 2, 'scaleX': 1, 'scaleY': 1, 'rotation': 0,
                       'direction': 90, 'width': w, 'height': size_px, 'font': '%gpx Nanum Gothic' % size_px,
                       'visible': False, 'colour': colour, 'text': text, 'textAlign': 1, 'lineBreak': False,
                       'bgColor': 'transparent', 'underLine': False, 'strike': False, 'fontSize': size_px}}


def ease_to(axis, target, k):
    """현재 위치에서 목표까지 남은 거리의 k 만큼 다가간다."""
    if axis == 'x':
        return lx(add(obj_x(), mul(sub(target, obj_x()), k)))
    return ly(add(obj_y(), mul(sub(target, obj_y()), k)))


def fade_out(steps=14):
    return [rep(steps, fx_add('transparency', round(100.0 / steps + 0.5, 2)), wait(0.02)), hide()]


def add_intro(RP, proj, art_dir, src_temp):
    tid = proj['scenes'][0]['id']
    assert proj['scenes'][0]['name'] == '타이틀'
    logo = None
    for o in proj['objects']:
        for p in o['sprite'].get('pictures', []):
            if p.get('filename') == LOGO_FILE:
                logo = p
    assert logo, '타이틀 로고 그림을 못 찾음'
    art = Art(art_dir)
    A = make_art(art, os.path.join(src_temp, os.path.relpath(logo['fileurl'], 'temp')))

    cb, wb, sb = A['coin_box'], A['word_box'], A['sub_box']
    CX, CY = stage_of((cb[0] + cb[2]) / 2, (cb[1] + cb[3]) / 2)
    WX, WY = stage_of((wb[0] + wb[2]) / 2, (wb[1] + wb[3]) / 2)
    SX, SY = stage_of((sb[0] + sb[2]) / 2, (sb[1] + sb[3]) / 2)
    cw, chh = cb[2] - cb[0], cb[3] - cb[1]
    COIN_SIZE = (cw + chh) / 2 * 0.5           # 로고 속 동전 크기 (엔트리 '크기' = 가로세로 평균)
    BIG = round(COIN_SIZE * 1.6, 1)

    objs = []    # 위(앞)에서부터
    flash = sprite('인트로섬광', tid, A['flash'], 0, 0, 16)
    coin = sprite('인트로동전', tid, A['coin'], 0, 200, 0.5)
    word = sprite('인트로글자', tid, A['word'], WX, WY, 0.5)
    subt = sprite('인트로부제', tid, A['sub'], SX, SY, 0.5)
    glow = sprite('인트로빛', tid, A['glow'], 0, 10, 0.5)
    ring = sprite('인트로고리', tid, A['ring'], 0, 10, 0.5)
    parts = sprite('인트로입자', tid, [alias(p, p['name']) for p in A['coin']], 0, 150, 0.15)
    hint = textbox('인트로안내', tid, '화면을 누르면 건너뜁니다', 0, -122, 6, '#7d879c')
    cur = sprite('인트로막', tid, A['curtain'], 0, 0, 3.05)
    objs = [flash, coin, word, subt, hint, glow, ring, parts, cur]

    S = {}
    # 덮개 = 감독: 시간표대로 신호를 보낸다
    S[cur['name']] = [
        [on_run(), setv('_인트로', 1), fx('transparency', 0), show(), wait(0.25), cast('인트로동전'), wait(1.3),
         cast('인트로로고'), wait(0.8), cast('인트로부제'), wait(1.8), if_(eq(V('_인트로'), 1), cast('인트로끝'))],
        [on_mouse(), if_(eq(V('_인트로'), 1), cast('인트로끝'))],
        [on_msg('인트로끝'), setv('_인트로', 2), stop_others(), wait(0.1)] + fade_out(16) + [setv('_인트로', 0)],
    ]
    S[coin['name']] = [
        [on_msg('인트로동전'), B('change_to_some_shape', VALUE=t('c1')), size(BIG), xy(0, 200), fx('transparency', 0),
         show(), setv('_인트로y', 200), setv('_인트로v', 0),
         rep(80, chg('_인트로v', -1.15), chg('_인트로y', V('_인트로v')),
             if_(lt(V('_인트로y'), 8), setv('_인트로y', 8), setv('_인트로v', mul(V('_인트로v'), -0.42))),
             ly(V('_인트로y')))],
        [on_msg('인트로동전'), rep(400, next_shape(), wait(0.035))],
        [on_msg('인트로로고'), stop_others(), B('change_to_some_shape', VALUE=t('c1')),
         rep(18, ease_to('x', CX, 0.25), ease_to('y', CY, 0.25),
             size(add(cur_size(), mul(sub(COIN_SIZE, cur_size()), 0.25)))),
         xy(CX, CY), size(COIN_SIZE)],
        [on_msg('인트로끝'), stop_others()] + fade_out(),
    ]
    S[glow['name']] = [
        [on_msg('인트로동전'), wait(0.3), xy(0, 8), size(70), fx('transparency', 100), show(),
         rep(25, grow(4), fx_add('transparency', -3.4))],
        [on_msg('인트로로고'), stop_others(), rep(14, grow(12), fx_add('transparency', 6)), hide()],
        [on_msg('인트로끝'), stop_others(), hide()],
    ]
    S[ring['name']] = [
        [on_msg('인트로로고'), xy(0, 8), size(40), fx('transparency', 0), show(),
         rep(22, grow(14), fx_add('transparency', 4.6)), hide()],
        [on_msg('인트로끝'), stop_others(), hide()],
    ]
    S[flash['name']] = [
        [on_msg('인트로로고'), fx('transparency', 10), show(), rep(14, fx_add('transparency', 6.5), wait(0.02)), hide()],
        [on_msg('인트로끝'), stop_others(), hide()],
    ]
    S[word['name']] = [
        [on_msg('인트로로고'), wait(0.08), B('change_to_some_shape', VALUE=t('w0')), xy(WX + 70, WY),
         fx('transparency', 100), show(), rep(20, ease_to('x', WX, 0.2), fx_add('transparency', -5.5)),
         lx(WX), fx('transparency', 0)],
        [on_msg('인트로부제'), wait(0.5), B('change_to_some_shape', VALUE=t('g1')),
         rep(4, wait(0.045), next_shape()), wait(0.045), B('change_to_some_shape', VALUE=t('w0'))],
        [on_msg('인트로끝'), stop_others(), wait(0.1)] + fade_out(16),
    ]
    S[subt['name']] = [
        [on_msg('인트로부제'), xy(SX, SY - 12), fx('transparency', 100), show(),
         rep(18, ease_to('y', SY, 0.22), fx_add('transparency', -6.5)), ly(SY), fx('transparency', 0)],
        [on_msg('인트로끝'), stop_others(), wait(0.1)] + fade_out(16),
    ]
    S[parts['name']] = [
        [on_msg('인트로로고'), hide(), wait(0.15), rep(34, clone_self(), wait(0.07))],
        [on_clone(), B('change_to_some_shape', VALUE=rnd(1, 6)), size(rnd(9, 19)), xy(rnd(-230, 230), 150),
         fx('transparency', rnd(0, 40)), show(),
         B('locate_xy_time', VALUE1=rnd(1.3, 2.4), VALUE2=add(obj_x(), rnd(-50, 50)), VALUE3=-150), del_clone()],
        [on_clone(), forever(next_shape(), wait(0.05))],
        [on_msg('인트로끝'), B('remove_all_clones'), stop_others(), hide()],
    ]
    S[hint['name']] = [
        [on_msg('인트로동전'), wait(0.6), show()],
        [on_msg('인트로끝'), hide()],
    ]
    # 타이틀 장면 오브젝트들 앞(=화면 맨 위)에 끼운다
    first = next(i for i, o in enumerate(proj['objects']) if o['scene'] == tid)
    proj['objects'][first:first] = objs
    for o in objs:
        ro = RObj(o, '타이틀')
        ro.scripts = S.get(o['name'], [])
        RP.objects.append(ro)
    return art.bytes


# ------------------------------------------------------------------ 저장 지킴이
def save_guard():
    """0.5초마다: 저장 요청이 있으면 저장 → 서버에 들어간 값 확인 → 다르면 다시."""
    verify = if_(and_(gt(V('저장슬롯'), 0), le(V('저장슬롯'), LLEN('저장데이터'))),
                 if_(ne(LGET('저장데이터', V('저장슬롯')), V('_save')),
                     setv('저장상태', '⚠ 저장이 확인되지 않아 다시 저장합니다'), setv('저장요청', 1), wait(2)))
    return [B('when_scene_start'), forever(
        wait(0.5),
        if_(eq(V('로그인완료'), 1),
            chg('_저장초', 0.5),
            if_(and_(eq(V('자동저장'), 1), ge(V('_저장초'), 20)), setv('저장요청', 1)),
            ifelse(eq(V('저장요청'), 1),
                   [setv('_저장초', 0),
                    # 처음 시작할 때 서버가 느려 저장 칸을 못 받았으면 다시 찾는다 (내 계정 키일 때만)
                    if_(and_(eq(V('저장슬롯'), 0), eq(V('계정키'), V('_내계정'))), func('i7z0')),
                    ifelse(gt(V('저장슬롯'), 0), [func('lmmy'), verify],
                           [setv('저장상태', '⚠ 저장 칸을 찾는 중… (인터넷 연결 확인)'), wait(2)])],
                   [if_(eq(V('랭킹요청'), 1), setv('랭킹요청', 0), func('9j92'))])))]


def walk_lists(blocks, fn):
    """문장 목록마다 fn(list) 를 부른다 (안쪽까지)."""
    fn(blocks)
    for b in blocks:
        if isinstance(b, dict):
            for st in b.get('statements') or []:
                walk_lists(st, fn)


def edit_functions(RP):
    vid = RP.var_ids
    F = {f['id']: f for f in RP.functions}
    cnt = {'lmmy': 0, '9j92': 0, 'login': 0}

    # 하루 진행(g16v): 바로 저장하던 것 → 지킴이에게 맡김
    def day(lst):
        i = 0
        while i < len(lst):
            b = lst[i]
            if isinstance(b, dict) and b.get('type') == 'func_lmmy':
                del lst[i]
                cnt['lmmy'] += 1
                continue
            if isinstance(b, dict) and b.get('type') == 'func_9j92':
                lst[i] = setv('랭킹요청', 1)
                cnt['9j92'] += 1
            i += 1
    walk_lists(F['g16v']['body'], day)

    # 새로 시작하기(5fgy)·이어하기(gbq9): 로그인 성공 순간의 계정 키를 기억
    def login(lst):
        i = 0
        while i < len(lst):
            b = lst[i]
            if isinstance(b, dict) and b.get('type') == 'set_variable' and b['params'][0] == vid['로그인완료']:
                v = b['params'][1]
                if isinstance(v, dict) and v.get('params') and str(v['params'][0]) == '1':
                    lst.insert(i, setv('_내계정', V('계정키')))
                    cnt['login'] += 1
                    i += 1
            i += 1
    walk_lists(F['5fgy']['body'], login)
    walk_lists(F['gbq9']['body'], login)
    assert cnt == {'lmmy': 1, '9j92': 1, 'login': 2}, cnt
    return cnt


def add_save_guard(RP, proj):
    sc = {s['id']: s['name'] for s in proj['scenes']}
    hosts = {}
    for o in RP.objects:
        name = o.scene
        if name == '타이틀' or name in hosts:
            continue
        if o.kind == 'sprite':
            hosts[name] = o
    for o in RP.objects:      # 그림 오브젝트가 없는 장면은 아무 오브젝트에
        if o.scene != '타이틀' and o.scene not in hosts:
            hosts[o.scene] = o
    for o in hosts.values():
        o.scripts.append(save_guard())
    missing = [n for n in sc.values() if n != '타이틀' and n not in hosts]
    assert not missing, missing
    return sorted(hosts)


def add_vars(RP, proj, names):
    for nm, val in names:
        if nm in RP.var_ids:
            continue
        vid = EG.new_id()
        proj['variables'].append(dict(name=nm, id=vid, visible=False, value=val, variableType='variable',
                                      isCloud=False, isRealTime=False, cloudDate=False, object=None, x=0, y=0,
                                      array=[]))
        RP.var_ids[nm] = vid


def short_num(x, sig=4):
    """차트 기록 숫자를 유효숫자 sig 자리로 짧게 ('361750.0' → '361800', '1.06078' → '1.061')."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return x
    if v == 0 or v != v or abs(v) == float('inf'):
        return x
    s = str(int(round(v))) if abs(v) >= 10 ** (sig - 1) else '%.*g' % (sig, v)
    if 'e' in s:                      # 아주 작거나 큰 수는 그대로 (지수 표기 피함)
        return str(x)
    return s if len(s) < len(str(x)) else str(x)


def numeric_lists(proj):
    """리스트 칸의 숫자 글자('1724', '0', '0.9755')를 숫자로 저장 (따옴표 두 개씩 덜 씀). 실시간 리스트는 그대로.
    값을 그대로 다시 쓸 수 있는 꼴(앞자리 0·끝자리 0 없음)만 바꾼다."""
    import re
    pat = re.compile(r'^-?(0|[1-9][0-9]{0,14})(\.[0-9]{0,9}[1-9])?$')
    n = 0
    for v in proj['variables']:
        if v.get('variableType') != 'list' or v.get('isRealTime') or v.get('isCloud'):
            continue
        for it in v.get('array') or []:
            d = it.get('data')
            if isinstance(d, str) and pat.match(d):
                it['data'] = int(d) if '.' not in d else float(d)
                if isinstance(it['data'], float) and repr(it['data']) != d:
                    it['data'] = d
                    continue
                n += 1
    return n


def compact_candles(proj):
    """봉고가·봉저가·봉종가 N (종목별 80일 차트 기록, 약 10만 칸): 그림 그리기에만 쓰이므로 유효숫자 4자리로."""
    saved = 0
    for v in proj['variables']:
        if v.get('variableType') == 'list' and v['name'][:3] in ('봉고가', '봉저가', '봉종가'):
            for it in v.get('array') or []:
                old = str(it.get('data'))
                it['data'] = short_num(old)
                saved += len(old) - len(it['data'])
    return saved


# ------------------------------------------------------------------ 차트: 고가·저가 기록 대신 계산
def _label_of(f):
    h = f.get('raw_head') or {}
    try:
        return h['params'][0]['params'][0]
    except (KeyError, IndexError, TypeError):
        return None


def chart_wicks(RP, proj):
    """봉고가·봉저가 1~7 (종목 413개 × 80일, 리스트 14개 · 약 1.2MB) 를 없애고,
    차트 봉 계산 때 앞날 종가·오늘 종가와 종목 변동성으로 꼬리 길이를 정한다
    (원래도 '변동성 × 0.6 × 0~1 사이 무작위'였음 → 칸·종목마다 정해진 0~1 값으로)."""
    from entrygen import floor, div, mod, LGET, lst_set
    V_ = {v['name']: v for v in proj['variables']}
    hl = {V_['봉%s가%d' % (k, c)]['id'] for k in ('고', '저') for c in range(1, 8)}
    f = next(f for f in RP.functions if _label_of(f) == '차트 봉 계산')
    body = [setv('_crc', floor(div(sub(V('선택'), 1), 62))),
            setv('_crb', mul(mod(sub(V('선택'), 1), 62), 80)),
            setv('_crs', LGET('봉배율', V('선택'))),
            setv('_crw', mul(LGET('일변동성', V('선택')), 0.6))]
    for c in range(7):
        unit = []
        for _ in range(20):
            unit += [lst_set('차트링C', V('_crj'), mul(LGET('봉종가%d' % (c + 1), add(V('_crb'), V('_crj'))), V('_crs'))),
                     chg('_crj', 1)]
        body.append(if_(eq(V('_crc'), c), setv('_crj', 1), rep(4, *unit)))
    unit = []
    for _ in range(20):
        unit += [setv('_crq', LGET('차트링C', V('_crj'))),
                 setv('_crp', LGET('차트링C', add(mod(add(V('_crj'), 78), 80), 1))),
                 setv('_crh', V('_crq')), if_(gt(V('_crp'), V('_crh')), setv('_crh', V('_crp'))),
                 setv('_crl', V('_crq')), if_(lt(V('_crp'), V('_crl')), setv('_crl', V('_crp'))),
                 lst_set('차트링H', V('_crj'), mul(V('_crh'), add(1, mul(div(mod(add(mul(V('_crj'), 37), mul(V('선택'), 101)), 100), 100), V('_crw'))))),
                 lst_set('차트링L', V('_crj'), mul(V('_crl'), sub(1, mul(div(mod(add(mul(V('_crj'), 53), mul(V('선택'), 67)), 100), 100), V('_crw'))))),
                 chg('_crj', 1)]
    body += [setv('_crj', 1), rep(4, *unit)]
    f['body'] = body
    # 매일 갱신 코드의 고가·저가 기록 쓰기 빼기
    removed = [0]

    def strip(lst):
        keep = []
        for b in lst:
            if isinstance(b, dict) and b.get('type') in ('change_value_list_index', 'add_value_to_list',
                                                          'insert_value_to_list', 'remove_value_from_list') \
                    and any(isinstance(q, str) and q in hl for q in b.get('params') or []):
                removed[0] += 1
                continue
            if isinstance(b, dict):
                for st in b.get('statements') or []:
                    st[:] = strip(st)
            keep.append(b)
        return keep
    for o in RP.objects:
        for sc in o.scripts:
            sc[1:] = strip(sc[1:])
    for g in RP.functions:
        if g is not f and g.get('body'):
            g['body'][:] = strip(g['body'])
    left = json.dumps([o.scripts for o in RP.objects] + [g.get('body') for g in RP.functions], ensure_ascii=False, default=str)
    assert not any(('"%s"' % i) in left for i in hl), '고가·저가 기록이 아직 쓰임'
    proj['variables'][:] = [v for v in proj['variables'] if v['id'] not in hl]
    return removed[0]


def dead_stores(RP, proj, log=print):
    """어디서도 읽지 않는 변수: 그 변수에 값을 넣는 블록(부작용 없는 계산일 때)과 변수 자체를 지운다."""
    import varparam
    varparam.resolve_refs(RP)
    keepv = {v['id'] for v in proj['variables'] if v.get('isRealTime') or v.get('isCloud') or v.get('visible')}
    scal = {v['id'] for v in proj['variables'] if v.get('variableType') == 'variable' and not v.get('object')}
    scal |= {vid for vid, _ in RP.new_vars.values()}
    total = 0
    while True:
        cnt = collections.Counter()
        writes = collections.Counter()

        def count(b):
            ps = b.get('params') or []
            for i, q in enumerate(ps):
                if isinstance(q, str) and q in scal:
                    if i == 0 and b.get('type') in ('set_variable', 'change_variable'):
                        writes[q] += 1
                    else:
                        cnt[q] += 1
        for o in RP.objects:
            varparam._walk(o.scripts, count)
        for g in RP.functions:
            varparam._walk(g.get('body') or [], count)
            if isinstance(g.get('value'), dict):
                varparam._walk(g['value'], count)
        dead = {v for v in scal if cnt[v] == 0 and v not in keepv}
        n = [0]

        def pure(b):
            ok = [True]

            def fn(x):
                t = x.get('type', '')
                if t.startswith('func_') or t in ('ask_and_wait', 'get_canvas_input_value'):
                    ok[0] = False
            varparam._walk(b, fn)
            return ok[0]

        def strip(lst):
            keep = []
            for b in lst:
                if isinstance(b, dict):
                    t = b.get('type')
                    ps = b.get('params') or []
                    if t in ('set_variable', 'change_variable') and ps and ps[0] in dead and pure(b):
                        n[0] += 1
                        continue
                    for st in b.get('statements') or []:
                        st[:] = strip(st)
                    if t == '_if' and not any((b.get('statements') or [[]])) and pure(ps[0] if ps else None or {}):
                        n[0] += 1
                        continue
                keep.append(b)
            return keep
        for o in RP.objects:
            for sc in o.scripts:
                sc[1:] = strip(sc[1:])
        for g in RP.functions:
            if g.get('body') is not None and g.get('value') != 'RAW':
                g['body'][:] = strip(g['body'])
        total += n[0]
        if not n[0]:
            break
    # 아무 데도 안 나오는 변수 정의 지우기
    every = json.dumps([o.scripts for o in RP.objects] + [g.get('body') for g in RP.functions] +
                       [g.get('value') for g in RP.functions if isinstance(g.get('value'), dict)],
                       ensure_ascii=False, default=str)
    gone = [v for v in proj['variables'] if v['variableType'] == 'variable' and not v.get('object')
            and v['id'] not in keepv and ('"%s"' % v['id']) not in every]
    gid = {v['id'] for v in gone}
    proj['variables'][:] = [v for v in proj['variables'] if v['id'] not in gid]
    for nm in [k for k, (vid, _) in RP.new_vars.items() if ('"%s"' % vid) not in every]:
        del RP.new_vars[nm]
    log('· 읽히지 않는 변수에 넣는 블록 %d개, 변수 %d개 지움' % (total, len(gone)))
    return total, len(gone)


# ------------------------------------------------------------------ CYW GAMES 제작사 인트로 (군수집과 같은 영상)
def _canon(b):
    """id·위치를 뺀 블록 모양 (같은 코드인지 비교용)."""
    if isinstance(b, dict):
        return '%s(%s){%s}' % (b.get('type'), ','.join(_canon(x) for x in b.get('params') or []),
                               ';'.join(','.join(_canon(s) for s in st) for st in b.get('statements') or []))
    if isinstance(b, list):
        return '[' + ','.join(_canon(x) for x in b) + ']'
    return repr(b)


def add_cyw_intro(RP, proj, out_temp):
    """군수집에 넣었던 'CYW GAMES' 제작사 영상(200장 + 소리, 클릭·스페이스로 건너뛰기)을 맨 앞 장면으로 넣는다.
    영상이 끝나면 타이틀 장면으로 가고, 타이틀에서는 money game 로고 인트로가 이어진다.
    엔트리의 '시작하기를 클릭했을 때'는 첫 장면 오브젝트에서만 실행되므로 타이틀의 그 코드는
      - 같은 내용의 '장면이 시작되었을 때' 코드가 이미 있으면 지우고 (두 번 돌지 않게)
      - 없으면 '장면이 시작되었을 때 + 처음 한 번만'으로 옮긴다."""
    import add_intro as AI
    iproj, ifiles = AI._intro_project()
    tgt = next(s['id'] for s in iproj['scenes'] if s['name'] == AI.TARGET)
    isid = next(s['id'] for s in iproj['scenes'] if s['name'] == '인트로')
    title = proj['scenes'][0]['id']
    assert proj['scenes'][0]['name'] == '타이틀'
    names = {v['name'] for v in proj['variables']} | set(RP.new_vars)
    for v in iproj['variables']:
        if v['variableType'] in ('timer', 'answer'):
            continue
        assert v['name'] not in names, '변수 이름 겹침: ' + v['name']
        proj['variables'].append(v)
    have = {m['id'] for m in proj['messages']}
    for m in iproj.get('messages', []):
        if m['id'] not in have:
            proj['messages'].append(m)
    objs = []
    for o in iproj['objects']:
        if o['scene'] != isid:
            continue
        o = dict(o)
        sc = o['script'] if isinstance(o['script'], str) else json.dumps(o['script'], ensure_ascii=False)
        o['script'] = sc.replace('"%s"' % tgt, '"%s"' % title)
        objs.append(o)
    # 타이틀의 시작 버튼 코드 정리
    dropped = moved = 0
    flag = EG.new_id()
    first_obj = None
    for ro in RP.objects:
        if ro.raw['scene'] != title:
            continue
        first_obj = first_obj or ro
        starts = {_canon(th[1:]) for th in ro.scripts if th and th[0].get('type') == 'when_scene_start'}
        new = []
        for th in ro.scripts:
            if th and th[0].get('type') == 'when_run_button_click':
                if _canon(th[1:]) in starts:
                    dropped += 1
                    continue
                cond = {'type': 'boolean_basic_operator', 'params': [
                    {'type': 'get_variable', 'params': [flag, None]}, 'EQUAL', {'type': 'number', 'params': ['0']}]}
                th = [{'type': 'when_scene_start', 'params': [None]},
                      {'type': '_if', 'params': [cond, None], 'statements': [th[1:]]}]
                moved += 1
            new.append(th)
        ro.scripts = new
    proj['variables'].append(dict(name='_첫타이틀끝', id=flag, visible=False, value=0, variableType='variable',
                                  isCloud=False, isRealTime=False, cloudDate=False, object=None, x=0, y=0, array=[]))
    # 타이틀에 처음 들어오고 0.2초 뒤 '처음' 표시를 끈다 (설정에서 돌아올 때는 다시 안 함)
    first_obj.scripts.append([{'type': 'when_scene_start', 'params': [None]},
                              {'type': 'wait_second', 'params': [{'type': 'number', 'params': ['0.2']}, None]},
                              {'type': 'set_variable', 'params': [flag, {'type': 'number', 'params': ['1']}, None]}])
    proj['scenes'].insert(0, next(s for s in iproj['scenes'] if s['id'] == isid))
    proj['objects'][0:0] = objs
    for o in objs:
        RP.objects.append(RObj(o, '인트로'))
    # 영상 그림·소리 파일 (원본 폴더와 앞 두 글자가 같으면 연결 대신 실제 폴더로 바꾼 뒤 넣는다)
    nbytes = 0
    for path, data in ifiles.items():
        if path == 'temp/project.json':
            continue
        rel = os.path.relpath(path, 'temp')
        top = os.path.join(out_temp, rel.split(os.sep)[0])
        if os.path.islink(top):
            real = os.readlink(top)
            os.unlink(top)
            shutil.copytree(real, top)
        dst = os.path.join(out_temp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as fp:
            fp.write(data)
        nbytes += len(data)
    print('· CYW GAMES 인트로 장면 추가 (파일 %.1fMB) · 시작 버튼 코드: 겹쳐서 지움 %d, 처음 한 번으로 옮김 %d'
          % (nbytes / 1e6, dropped, moved))


def main(src_temp, out_dir, do_slim=True, cyw=True):
    proj = json.load(open(os.path.join(src_temp, 'project.json'), encoding='utf-8'))
    before = rawslim.count_blocks(proj)
    RP = RawProject(proj)
    if do_slim:
        import clonemerge
        rawslim.pictures_as_names(RP)
        clonemerge.clone_merge(RP)
    add_vars(RP, proj, [('_인트로', '0'), ('_인트로y', '0'), ('_인트로v', '0'), ('_저장초', '0'),
                        ('랭킹요청', '0'), ('_내계정', '')])
    out_temp = os.path.join(out_dir, 'temp')
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_temp)
    # 원본 그림 폴더는 연결만 (묶을 때 실제 파일로)
    for d in os.listdir(src_temp):
        if os.path.isdir(os.path.join(src_temp, d)):
            os.symlink(os.path.abspath(os.path.join(src_temp, d)), os.path.join(out_temp, d))
    new_art = os.path.join(out_dir, 'newart')
    os.makedirs(new_art)
    art_bytes = add_intro(RP, proj, new_art, src_temp)
    print('· 인트로 그림 %.1fKB' % (art_bytes / 1024))
    print('· 하루 진행 코드 수정', edit_functions(RP))
    print('· 저장 지킴이 붙인 장면 %d개' % len(add_save_guard(RP, proj)))
    add_vars(RP, proj, [(n, '0') for n in ('_crw', '_crq', '_crp', '_crh', '_crl')])
    print('· 차트 고가·저가 기록 리스트 14개 → 계산 (쓰기 블록 %d개 뺌)' % chart_wicks(RP, proj))
    dead_stores(RP, proj)
    if cyw:
        add_cyw_intro(RP, proj, out_temp)
    if do_slim:
        import varparam
        rawslim.MIN_STMT, rawslim.MIN_SEQ = 3, 4
        rawslim.run_slim(RP)
        os.environ.setdefault('VP_W', '12')
        varparam.run(RP)
        varparam.tidy_params(RP)
        rawslim.run_slim(RP, rounds=2)
        varparam.tidy_params(RP)
        varparam.inline_small(RP)
        rawslim.run_slim(RP, rounds=1)
        varparam.tidy_params(RP)
    out = RP.to_json()
    print('· 차트 기록 숫자 줄임 %.0fKB' % (compact_candles(out) / 1024))
    print('· 리스트 숫자 칸 %d개 → 숫자로' % numeric_lists(out))
    print('블록: %d → %d' % (before, rawslim.count_blocks(out)))
    # 새 그림을 temp 아래로 (같은 앞 두 글자 폴더가 원본에 있으면 그 안에 넣어야 하므로 실제 폴더로 풀어 둔다)
    for d in os.listdir(new_art):
        dst = os.path.join(out_temp, d)
        if os.path.islink(dst):
            real = os.readlink(dst)
            os.unlink(dst)
            shutil.copytree(real, dst)
        for root, _, files in os.walk(os.path.join(new_art, d)):
            rel = os.path.relpath(root, new_art)
            os.makedirs(os.path.join(out_temp, rel), exist_ok=True)
            for f in files:
                shutil.copy(os.path.join(root, f), os.path.join(out_temp, rel, f))
    shutil.rmtree(new_art)
    with open(os.path.join(out_temp, 'project.json'), 'w', encoding='utf-8') as fp:
        json.dump(out, fp, ensure_ascii=False, separators=(',', ':'))
    return out


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    main(args[0], args[1], do_slim='--no-slim' not in sys.argv, cyw='--no-cyw' not in sys.argv)
