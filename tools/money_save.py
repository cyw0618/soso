# -*- coding: utf-8 -*-
"""money_game 저장 강화 — 군수집 막내아들의 저장(savegame.py)과 같은 틀을 그대로 가져옴.

저장할 때마다 같은 글(+ 끝에 저장 번호)을 세 군데에 쓴다:
  - 실시간 리스트 '저장칸목록'의 내 칸 A·B (번갈아 씀: 한쪽이 깨지거나 쓰다 끊겨도 직전 저장이 남음)  [군수집과 같은 이름]
  - 공유 리스트 '세이브회원' + '세이브1~N' (계정마다 한 칸, 300글자 조각)                              [군수집과 같은 이름]
  - 원래 있던 저장데이터 (랭킹도 이 리스트들을 씀)
기록을 찾을 때(계정 확인·이어하기·새로 시작하기) 위 네 군데 가운데 온전하고 저장 번호가 가장 큰 것을 골라,
실시간 저장데이터가 그것보다 낡았거나 깨졌으면 그것으로 되살린다.
저장 글 끝: ...H|END|123|   (번호 없는 예전 저장은 0 으로 읽힘 → 예전 저장도 그대로 이어서 할 수 있다)
"""
from entrygen import (V, setv, chg, wait, if_, ifelse, until, eq, ne, gt, lt, le, and_, or_, add, sub,
                      LGET, LLEN, lst_add, lst_set, join, slen, str_index, substr)

NCH, CH = 14, 300            # 공유 리스트 조각 수 × 글자 수 = 4200자까지
SL = '저장칸목록'
MEM = '세이브회원'
CHUNKS = ['세이브%d' % k for k in range(1, NCH + 1)]
PAD = '~' * (NCH * CH)
END = '|END|'
KEY = '^'


def _fn(call):
    import copy
    return copy.deepcopy(call)


def _stamp_of(src, out):
    """src 글의 저장 번호를 out 에 (없으면 0)."""
    i = V('_sv_bi2')
    return [setv(out, 0), setv('_sv_bi2', str_index(V(src), END)),
            if_(and_(gt(i, 0), lt(add(i, 5), slen(V(src)))),
                setv('_sv_bt2', substr(V(src), add(i, 5), slen(V(src)))),
                setv('_sv_bp2', str_index(V('_sv_bt2'), '|')),
                if_(gt(V('_sv_bp2'), 1), setv(out, substr(V('_sv_bt2'), 1, sub(V('_sv_bp2'), 1)))))]


def _valid(src, ok):
    return [setv(ok, 0),
            if_(and_(eq(str_index(V(src), 'MG1|'), 1), gt(str_index(V(src), END), 0)), setv(ok, 1))]


def _chunks_ok():
    c = le(V('_sv_bm'), LLEN(CHUNKS[0]))
    for nm in CHUNKS[1:]:
        c = and_(c, le(V('_sv_bm'), LLEN(nm)))
    return and_(gt(V('_sv_bm'), 0), c)


def _member_search():
    return [setv('_sv_bm', 0), setv('_sv_bi', LLEN(MEM)),
            until(or_(lt(V('_sv_bi'), 1), gt(V('_sv_bm'), 0)),
                  if_(eq(LGET(MEM, V('_sv_bi')), V('계정키')), setv('_sv_bm', V('_sv_bi'))),
                  chg('_sv_bi', -1))]


def _row_search(key):
    """저장칸목록에서 key 로 시작하는 칸 찾기 (최근 칸부터) → _rp (없으면 0)."""
    return [setv('_sv_rp', 0), setv('_sv_ri', LLEN(SL)),
            until(or_(lt(V('_sv_ri'), 1), gt(V('_sv_rp'), 0)),
                  if_(eq(str_index(LGET(SL, V('_sv_ri')), key), 1), setv('_sv_rp', V('_sv_ri'))),
                  chg('_sv_ri', -1))]


def build(RP, proj, F, add_vars):
    RP.list(SL, [], cloud=True)               # 실시간 리스트
    RP.list(MEM, [], cloud='shared')          # 공유 리스트 (백업)
    for nm in CHUNKS:
        RP.list(nm, [], cloud='shared')
    add_vars(RP, proj, [(n, v) for n, v in (
        ('저장번호', '0'), ('_sv_ab', '0'), ('_sv_bm', '0'), ('_sv_bi', '0'), ('_sv_bi2', '0'), ('_sv_bt', ''), ('_sv_bt2', ''),
        ('_sv_bp2', '0'), ('_sv_ss', ''), ('_sv_sn', '0'), ('_sv_cs', ''), ('_sv_cok', '0'), ('_sv_cn', '0'), ('_sv_best', ''),
        ('_sv_bestn', '-1'), ('_sv_ri', '0'), ('_sv_rp', '0'), ('_sv_pok', '0'), ('_sv_pn', '-1'), ('_sv_ps', ''), ('_sv_w9', '0'),
        ('_저장돈', '0'), ('_sv_wk', ''), ('_sv_wl', ''))])
    slotfind, pad = F['저장 슬롯 찾기'], F['저장 리스트 맞추기']
    fstamp = RP.new_function('저장 번호 읽기', _stamp_of('_sv_ss', '_sv_sn'))
    # 후보 하나(_cs)가 온전하고 더 새것이면 _best 로
    fpick = RP.new_function('저장 후보 고르기', [
        *_valid('_sv_cs', '_sv_cok'),
        if_(eq(V('_sv_cok'), 1), setv('_sv_ss', V('_sv_cs')), _fn(fstamp), setv('_sv_cn', V('_sv_sn')),
            if_(gt(V('_sv_cn'), V('_sv_bestn')), setv('_sv_best', V('_sv_cs')), setv('_sv_bestn', V('_sv_cn'))))])

    # ---- 백업 쓰기: A/B 번갈아 + 공유 리스트
    def write_row(letter):
        key = join(V('계정키'), KEY, letter)
        return [setv('_sv_wk', key),
                *_row_search(V('_sv_wk')),
                ifelse(gt(V('_sv_rp'), 0), [lst_set(SL, V('_sv_rp'), join(V('_sv_wk'), V('_save')))],
                       [setv('_sv_ri', LLEN(SL)), lst_add(SL, join(V('_sv_wk'), V('_save'))), setv('_sv_w9', 0),
                        # 실시간 리스트는 서버에 다녀와야 늘어난다: 늘어날 때까지 기다림(최대 4초)
                        until(or_(gt(LLEN(SL), V('_sv_ri')), gt(V('_sv_w9'), 40)), wait(0.1), chg('_sv_w9', 1))])]
    write = [if_(ne(V('계정키'), ''),
                 ifelse(eq(V('_sv_ab'), 1), [setv('_sv_ab', 0), *write_row('A')], [setv('_sv_ab', 1), *write_row('B')]),
                 if_(gt(V('_sv_bm'), LLEN(MEM)), setv('_sv_bm', 0)),
                 if_(gt(V('_sv_bm'), 0), if_(ne(LGET(MEM, V('_sv_bm')), V('계정키')), setv('_sv_bm', 0))),
                 if_(eq(V('_sv_bm'), 0), *_member_search()),
                 if_(eq(V('_sv_bm'), 0), lst_add(MEM, V('계정키')), setv('_sv_bm', LLEN(MEM)),
                     *[lst_add(nm, '') for nm in CHUNKS]),
                 if_(and_(_chunks_ok(), le(slen(V('_save')), NCH * CH)),
                     setv('_sv_bt', substr(join(V('_save'), PAD), 1, NCH * CH)),
                     *[if_(ne(LGET(nm, V('_sv_bm')), substr(V('_sv_bt'), (k - 1) * CH + 1, k * CH)),
                           lst_set(nm, V('_sv_bm'), substr(V('_sv_bt'), (k - 1) * CH + 1, k * CH)))
                       for k, nm in enumerate(CHUNKS, 1)]))]
    fwrite = RP.new_function('백업 쓰기', write)

    # ---- 백업 복구: 네 군데 중 가장 새것으로 실시간 저장데이터를 되살림
    def read_row(letter):
        key = join(V('계정키'), KEY, letter)
        return [setv('_sv_wk', key), *_row_search(V('_sv_wk')),
                if_(gt(V('_sv_rp'), 0),
                    setv('_sv_wl', LGET(SL, V('_sv_rp'))),
                    if_(gt(slen(V('_sv_wl')), slen(V('_sv_wk'))),
                        setv('_sv_cs', substr(V('_sv_wl'), add(slen(V('_sv_wk')), 1), slen(V('_sv_wl')))), _fn(fpick)))]
    read_c = [*_member_search(),
              if_(_chunks_ok(),
                  setv('_sv_bt', ''), *[setv('_sv_bt', join(V('_sv_bt'), LGET(nm, V('_sv_bm')))) for nm in CHUNKS],
                  setv('_sv_bp2', str_index(V('_sv_bt'), '~')),
                  if_(gt(V('_sv_bp2'), 1), setv('_sv_bt', substr(V('_sv_bt'), 1, sub(V('_sv_bp2'), 1)))),
                  setv('_sv_cs', V('_sv_bt')), _fn(fpick))]
    restore = [if_(eq(V('저장슬롯'), 0),
                   lst_add('저장키', V('계정키')), setv('_sv_w9', 0),
                   until(or_(gt(V('저장슬롯'), 0), gt(V('_sv_w9'), 40)), wait(0.1), chg('_sv_w9', 1), {'type': 'func_' + slotfind, 'params': [], 'statements': []})),
               if_(gt(V('저장슬롯'), 0),
                   {'type': 'func_' + pad, 'params': [], 'statements': []},
                   if_(le(V('저장슬롯'), LLEN('저장데이터')),
                       lst_set('저장데이터', V('저장슬롯'), V('_sv_best')),
                       setv('저장상태', '☁ 저장 기록이 비어 있거나 낡아서, 가장 새 백업으로 되살렸어요')))]
    recover = [if_(ne(V('계정키'), ''),
                   setv('_sv_best', ''), setv('_sv_bestn', -1), setv('_sv_pn', -1), setv('_sv_ps', ''),
                   if_(and_(gt(V('저장슬롯'), 0), le(V('저장슬롯'), LLEN('저장데이터'))),
                       setv('_sv_ps', LGET('저장데이터', V('저장슬롯')))),
                   setv('_sv_cs', V('_sv_ps')), _fn(fpick), setv('_sv_pn', V('_sv_bestn')),
                   *read_row('A'), *read_row('B'), *read_c,
                   if_(and_(gt(V('_sv_bestn'), -1), gt(V('_sv_bestn'), V('_sv_pn'))), *restore))]
    frecover = RP.new_function('백업 복구', recover)
    return fwrite, fstamp, frecover


def patch(RP, proj, F, fwrite, fstamp, frecover):
    def fbody(label):
        return next(f for f in RP.functions if f['id'] == F[label])['body']
    dl = RP.var_ids['_dl']
    cnt = {'rec': 0, 'num': 0, 'bk': 0, 'load': 0}

    def walk(lst, fn):
        fn(lst)
        for b in list(lst):
            if isinstance(b, dict):
                for st in b.get('statements') or []:
                    walk(st, fn)

    def add_recover(lst):
        i = 0
        while i < len(lst):
            b = lst[i]
            if isinstance(b, dict) and b.get('type') == 'func_' + F['저장 슬롯 찾기'] and i + 1 < len(lst):
                n = lst[i + 1]
                if isinstance(n, dict) and n.get('type') == 'set_variable' and n['params'][0] == dl:
                    lst.insert(i + 1, _fn(frecover))
                    cnt['rec'] += 1
                    i += 1
            i += 1
    for label in ('계정 확인', '이어하기', '새로 시작하기'):
        walk(fbody(label), add_recover)

    def add_save(lst):
        i = 0
        while i < len(lst):
            b = lst[i]
            if isinstance(b, dict) and b.get('type') == 'func_' + F['저장 문자열 만들기']:
                lst[i + 1:i + 1] = [chg('저장번호', 1), setv('_save', join(V('_save'), V('저장번호'), '|'))]
                cnt['num'] += 1
                i += 2
                continue
            if isinstance(b, dict) and b.get('type') == 'change_value_list_index' and b['params'][0] == RP.var_ids['저장시각']:
                lst.insert(i + 1, _fn(fwrite))
                cnt['bk'] += 1
                i += 1
            i += 1
    walk(fbody('실시간 저장'), add_save)

    def add_load(lst):
        for i, b in enumerate(lst):
            if isinstance(b, dict) and b.get('type') == 'set_variable' and b['params'][0] == RP.var_ids['_src']:
                lst[i + 1:i + 1] = [setv('_sv_ss', V('_src')), _fn(fstamp), setv('저장번호', V('_sv_sn'))]
                cnt['load'] += 1
                return
    add_load(fbody('저장 불러오기'))
    assert cnt['num'] == 1 and cnt['bk'] == 1 and cnt['load'] == 1 and cnt['rec'] >= 3, cnt
    return cnt
