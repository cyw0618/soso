# -*- coding: utf-8 -*-
"""계정별 '이어하기' 저장.

게임을 끝내기(군수 선거 패배·파산·'여기서 끝내기') 전까지는, 같은 엔트리 계정이면 작품을 나갔다 들어와도 이어서 할 수 있다.
군수가 된 뒤(커리어 모드)에는 엔딩을 봐도 계속 투자할 수 있으므로 저장을 지우지 않는다.
엔트리 '공유 리스트'(저장목록) 하나에 한 계정당 한 칸, '계정§데이터' 형태로 저장한다.
  - 데이터 = 'S2|값|값|...|E'  (S2: 저장 형식 버전, 값 개수가 맞지 않으면 무시)
  - 0~9 한 자리 값만 갖는 리스트(유세 완료, 인수 레벨 ...)는 숫자를 이어 붙인 글자 하나로 저장한다.
  - 칸을 지우지 않고(다른 사람 칸 번호가 밀리지 않게) 게임이 끝나면 '계정§없음'으로 바꾼다.
지도·집무실 장면에 들어올 때마다 자동 저장한다. 로그인하지 않았으면 저장하지 않는다.
"""
from entrygen import *
import data as D
import data2 as D2
import scene_stock as ST

VERSION = 'S5'
SEP, KEY = '|', '^'
SL = '저장칸목록'
# 백업: 참고 작품('저장기능 v3')처럼 공유 리스트에 '회원 번호' 칸마다 짧은 값으로 저장한다.
#   세이브회원[n] = 계정, 세이브1~NCH[n] = 저장글을 CH 글자씩 나눈 조각 (긴 글 한 칸보다 서버에 안전하게)
MEM = '세이브회원'
NCH, CH = 8, 300
CHUNKS = ['세이브%d' % k for k in range(1, NCH + 1)]
SAVE_VARS = ['저장번호', '돈', '내지지율', '큰A', '큰B', '유세횟수', '방어권', '차단턴', '장시간', '첫째주', '둘째주', '지배알림',
             '협상기회', '협상금지턴', '지도모드',
             '단계', '직위', '캠페인중', '평판', '창당', '당원', '공천', '당선', '회사상태', '회사업종', '회사가치', '회사투자',
             '회사부스트', '마지막시각', '결재수', '결재타이머', '등록점수', '정당이름', '회사이름', '등록이름', '지역번호',
             '의혹', '수사기관', '수사혐의', '수사남은', '수사위험']
DIGIT_LISTS = [('지역완료', D.N_PLACES * 3), ('인수레벨', len(D2.COMPANIES)), ('땅보유', len(D2.LANDS)),
               ('계열사주인', len(D.AFFILIATES))]
SAVE_LISTS = [('주가', ST.N), ('보유', ST.N), ('평단', ST.N), ('배수', ST.N), ('투자부채', 3), ('투자만기', 3), ('투자결렬', 3),
              ('땅가격', len(D2.LANDS)), ('땅예정', len(D2.LANDS)), ('땅배율', len(D2.LANDS)), ('특별X', len(D2.SPECIALS)),
              ('세력인원', len(D2.OPS_MEMBERS)), ('직원수', len(D2.POSITIONS)), ('직원능력합', len(D2.POSITIONS)),
              ('매수남은', len(D2.AGENCIES))]
FIELDS = len(SAVE_VARS) + len(DIGIT_LISTS) + sum(n for _, n in SAVE_LISTS)


_P = None
_FN = {}


def setup(P):
    global _P
    _P = P
    _FN.clear()
    P.list('저장칸목록', [], cloud=True, lid='sv7q')
    # 백업: 엔트리 '공유 리스트' (회원 번호 칸마다 짧은 조각)
    P.list(MEM, [], cloud='shared', lid='cym1')
    for k, nm in enumerate(CHUNKS, 1):
        P.list(nm, [], cloud='shared', lid='cy%02d' % k)
    for v, d in (('내계정', ''), ('저장위치A', 0), ('저장위치B', 0), ('저장슬롯', 0), ('저장번호', 0), ('저장틱', 0), ('저장필요', 0), ('_okA', 0), ('_okB', 0), ('_nA', 0), ('_nB', 0), ('_t', ''), ('_t2', ''), ('_n0', 0), ('_w', 0), ('회원번호', 0), ('저장중', 0), ('_초', 0), ('_okC', 0), ('_nC', 0), ('_tC', ''), ('_L', 0), ('_bk', 0), ('_bn', 0), ('저장있음', 0), ('저장글', ''), ('_불러온', ''), ('_sp', 0), ('_si', 0),
                 ('_dg', ''), ('_v', ''), ('_i', 0)):
        P.var(v, d)


def logged_in():
    # 로그인하지 않으면 계정 아이디가 ' ' (엔트리 비교에서는 0 으로 바뀌어 ' ' 와 같다고 나옴)
    return ne(V('내계정'), ' ')


def _slot_key(letter):
    return join(V('내계정'), KEY, letter)


def _search(key, out, lst=SL):
    """저장 리스트에서 key 로 시작하는 칸 찾기 (최근 칸부터). 못 찾으면 out=0."""
    return [setv(out, 0), setv('_si', LLEN(lst)),
            until(or_(lt(V('_si'), 1), gt(V(out), 0)),
                  if_(eq(str_index(LGET(lst, V('_si')), key), 1), setv(out, V('_si'))),
                  chg('_si', -1))]


def _check(pos, letter, ok, num, lst=SL):
    """칸 pos 의 저장이 온전한지(형식 버전·값 개수) 보고, 저장 번호를 num 에 넣는다 (ok=1 이면 쓸 수 있음)."""
    return [setv(ok, 0), setv(num, 0),
            if_(gt(V(pos), 0),
                setv('_t', LGET(lst, V(pos))),
                setv('_t', substr(V('_t'), add(slen(V('내계정')), 3), slen(V('_t')))),
                if_(and_(eq(str_index(V('_t'), VERSION + SEP), 1), eq(str_count(V('_t'), SEP), FIELDS + 1)),
                    setv('_t2', substr(V('_t'), len(VERSION) + 2, slen(V('_t')))),
                    setv('_sp', str_index(V('_t2'), SEP)),
                    setv(num, substr(V('_t2'), 1, sub(V('_sp'), 1))),
                    setv(ok, 1)))]


def _chunks_ok():
    """모든 조각 리스트에 회원번호 칸이 있는지 (칸이 없으면 읽기·쓰기를 하지 않는다: 엔트리는 없는 칸에서 멈춘다)."""
    c = le(V('회원번호'), LLEN(CHUNKS[0]))
    for nm in CHUNKS[1:]:
        c = and_(c, le(V('회원번호'), LLEN(nm)))
    return and_(gt(V('회원번호'), 0), c)


def _member_search():
    """세이브회원 리스트에서 내 계정 칸 번호 찾기 (최근 칸부터). 못 찾으면 회원번호=0."""
    return [setv('회원번호', 0), setv('_si', LLEN(MEM)),
            until(or_(lt(V('_si'), 1), gt(V('회원번호'), 0)),
                  if_(eq(LGET(MEM, V('_si')), V('내계정')), setv('회원번호', V('_si'))),
                  chg('_si', -1))]


def _member_check():
    """회원번호 칸의 조각을 이어 붙여(_tC) 온전한지 보고 저장 번호를 _nC 에."""
    joins = [setv('_tC', join(V('_tC'), LGET(nm, V('회원번호')))) for nm in CHUNKS]
    return [setv('_okC', 0), setv('_nC', 0), setv('_tC', ''),
            if_(_chunks_ok(), *joins,
                if_(and_(eq(str_index(V('_tC'), VERSION + SEP), 1), eq(str_count(V('_tC'), SEP), FIELDS + 1)),
                    setv('_t2', substr(V('_tC'), len(VERSION) + 2, slen(V('_tC')))),
                    setv('_sp', str_index(V('_t2'), SEP)),
                    setv('_nC', substr(V('_t2'), 1, sub(V('_sp'), 1))),
                    setv('_okC', 1)))]


def find_blocks():
    """저장 찾기 함수를 부르는 블록."""
    if 'find' not in _FN:
        _FN['find'] = _P.new_function('저장찾기', _find_body())
    return [dict(_FN['find'])]


def _find_body():
    """타이틀에서: 내 계정의 저장(실시간 A·B, 공유 리스트 백업 C)을 찾아, 온전한 것 중 저장 번호가 가장 큰 것을 고른다
    (저장있음=1, 내용은 _불러온 에)."""
    pick = []
    for k, (ok, num) in enumerate((('_okA', '_nA'), ('_okB', '_nB'), ('_okC', '_nC')), 1):
        pick.append(if_(and_(eq(V(ok), 1), gt(V(num), V('_bn'))), setv('_bn', V(num)), setv('_bk', k)))
    strip = lambda pos: setv('_불러온', substr(LGET(SL, V(pos)), add(slen(V('내계정')), 3), slen(LGET(SL, V(pos)))))
    return [setv('내계정', user_id()), setv('저장위치A', 0), setv('저장위치B', 0), setv('회원번호', 0), setv('저장있음', 0),
            setv('저장슬롯', 0),
            if_(logged_in(),
                *_search(_slot_key('A'), '저장위치A'), *_search(_slot_key('B'), '저장위치B'), *_member_search(),
                *_check('저장위치A', 'A', '_okA', '_nA'), *_check('저장위치B', 'B', '_okB', '_nB'), *_member_check(),
                setv('_bk', 0), setv('_bn', -1), *pick,
                if_(gt(V('_bk'), 0),
                    ifelse(eq(V('_bk'), 1), [strip('저장위치A'), setv('저장슬롯', 1)],
                           [ifelse(eq(V('_bk'), 2), [strip('저장위치B'), setv('저장슬롯', 2)],
                                   [setv('_불러온', V('_tC')), setv('저장슬롯', 0)])]),
                    setv('저장있음', 1)))]


def save_blocks():
    """저장 함수를 부르는 블록 (함수 본문은 한 번만 만든다)."""
    if 'save' not in _FN:
        _FN['save'] = _P.new_function('저장하기', _save_body())
    return [dict(_FN['save'])]


def _write_slot(letter, pos):
    """내 칸(letter)에 저장글을 쓴다. 칸 번호가 어긋났으면 다시 찾고, 없으면 새로 만든다."""
    key = _slot_key(letter)
    return [if_(gt(V(pos), LLEN('저장칸목록')), setv(pos, 0)),
            if_(gt(V(pos), 0), if_(ne(str_index(LGET('저장칸목록', V(pos)), key), 1), setv(pos, 0))),
            ifelse(gt(V(pos), 0), [lst_set('저장칸목록', V(pos), join(key, V('저장글')))],
                   # 실시간 리스트는 서버에 다녀와야 항목이 늘어난다: 늘어날 때까지(최대 4초) 기다렸다가 내 칸을 찾는다
                   [setv('_n0', LLEN('저장칸목록')), lst_add('저장칸목록', join(key, V('저장글'))), setv('_w', 0),
                    until(or_(gt(LLEN('저장칸목록'), V('_n0')), gt(V('_w'), 40)), wait(0.1), chg('_w', 1)),
                    *_search(key, pos)])]


PAD = '~' * (NCH * CH)


def _write_backup():
    """공유 리스트(백업)의 내 회원 칸에 저장글을 CH 글자씩 나눠 쓴다.
    저장글 뒤를 '~' 로 채워 길이를 NCH*CH 로 맞추면 조각마다 조건 없이 자를 수 있다 (읽을 때 'E' 뒤는 무시됨)."""
    return [if_(gt(V('회원번호'), LLEN(MEM)), setv('회원번호', 0)),
            if_(gt(V('회원번호'), 0), if_(ne(LGET(MEM, V('회원번호')), V('내계정')), setv('회원번호', 0))),
            if_(eq(V('회원번호'), 0), *_member_search()),
            if_(eq(V('회원번호'), 0), lst_add(MEM, V('내계정')), setv('회원번호', LLEN(MEM)),
                *[lst_add(nm, '') for nm in CHUNKS]),
            if_(and_(_chunks_ok(), le(slen(V('저장글')), NCH * CH)),
                setv('_tC', substr(join(V('저장글'), PAD), 1, NCH * CH)),
                # 바뀐 조각만 쓴다 (공유 리스트 쓰기는 한 번에 한 프레임씩 걸린다)
                *[if_(ne(LGET(nm, V('회원번호')), substr(V('_tC'), (k - 1) * CH + 1, k * CH)),
                      lst_set(nm, V('회원번호'), substr(V('_tC'), (k - 1) * CH + 1, k * CH))) for k, nm in enumerate(CHUNKS, 1)])]


def _save_body():
    """지금 상태를 저장 (한 프레임 안에 끝나도록 반복 없이 펼쳐서).
    저장 칸을 두 개(A·B) 번갈아 쓴다: 한쪽이 깨지거나 쓰다 끊겨도 직전 저장이 남는다."""
    data = [setv('저장글', VERSION + SEP)]
    for v in SAVE_VARS:
        data.append(setv('저장글', join(V('저장글'), V(v), SEP)))
    for lst, n in DIGIT_LISTS:
        for i in range(1, n + 1):
            data.append(setv('저장글', join(V('저장글'), LGET(lst, i))))
        data.append(setv('저장글', join(V('저장글'), SEP)))
    for lst, n in SAVE_LISTS:
        for i in range(1, n + 1):
            data.append(setv('저장글', join(V('저장글'), LGET(lst, i), SEP)))
    data.append(setv('저장글', join(V('저장글'), 'E')))
    if 'data' not in _FN:
        # 저장글 만들기 + 공유 리스트(백업)에 쓰기: 기다리는 블록이 없어 한 번에 끝난다
        _FN['bk'] = _P.new_function('백업쓰기', _write_backup())
        _FN['data'] = _P.new_function('저장글만들기', [chg('저장번호', 1), *data, dict(_FN['bk'])])
    # 저장은 리스트 조각을 여러 프레임에 걸쳐 쓰므로, 두 저장이 겹치면 조각이 섞인다 → 하나씩만 (10초 넘게 안 끝나면 풀림)
    return [if_(logged_in(),
                ifelse(_busy(), [setv('저장필요', 1)],
                       [setv('저장중', add(V('_초'), 1)),
                        dict(_FN['data']),
                        ifelse(eq(V('저장슬롯'), 1), [setv('저장슬롯', 2), *_write_slot('B', '저장위치B')],
                               [setv('저장슬롯', 1), *_write_slot('A', '저장위치A')]),
                        setv('저장있음', 1), setv('저장틱', 0), setv('저장필요', 0), setv('저장중', 0)]))]


def _busy():
    return and_(gt(V('저장중'), 0), lt(sub(add(V('_초'), 1), V('저장중')), 10))


def backup_blocks():
    """저장글을 만들어 백업(공유 리스트)에만 쓴다 (save_blocks 가 먼저 한 번 불려 함수가 만들어져 있어야 한다)."""
    if 'data' not in _FN:
        save_blocks()
    if 'quit' not in _FN:
        _FN['quit'] = _P.new_function('백업만저장', [
            setv('_w', 0), until(or_(not_(_busy()), gt(V('_w'), 30)), wait(0.1), chg('_w', 1)),
            setv('저장중', add(V('_초'), 1)), dict(_FN['data']), setv('저장중', 0)])
    return [dict(_FN['quit'])]


def tick_blocks():
    """경제 시계(1초마다)에서: 30초마다, 또는 거래·구매 뒤 5초 안에 자동 저장."""
    if 'tick' not in _FN:
        _FN['tick'] = _P.new_function('자동저장틱', [
            chg('저장틱', 1), chg('_초', 1),
            if_(and_(eq(V('저장있음'), 1), gt(V('총자산'), 0)),
                if_(or_(ge(V('저장틱'), 30), and_(eq(V('저장필요'), 1), ge(V('저장틱'), 5))), *save_blocks()))])
    return [dict(_FN['tick'])]


def _take_body():
    """_불러온 앞에서 값 하나를 꺼내 _v 에 (빈 값이면 '')."""
    return [setv('_sp', str_index(V('_불러온'), SEP)),
            ifelse(eq(V('_sp'), 1), [setv('_v', '')], [setv('_v', substr(V('_불러온'), 1, sub(V('_sp'), 1)))]),
            setv('_불러온', substr(V('_불러온'), add(V('_sp'), 1), slen(V('_불러온'))))]


def load_blocks():
    """find_blocks 가 남긴 _불러온 을 풀어서 변수/리스트에 넣는다 (반복문으로: 코드 수를 줄이려고. 몇 초 걸린다)."""
    if 'load' in _FN:
        return [dict(_FN['load'])]
    take = _P.new_function('값꺼내기', _take_body())
    b = [setv('_불러온', substr(V('_불러온'), len(VERSION) + 2, slen(V('_불러온'))))]
    for v in SAVE_VARS:
        b += [dict(take), setv(v, V('_v'))]
    for lst, n in DIGIT_LISTS:
        b += [dict(take), setv('_dg', V('_v')), setv('_i', 1),
              rep(n, lst_set(lst, V('_i'), char_at(V('_dg'), V('_i'))), chg('_i', 1))]
    for lst, n in SAVE_LISTS:
        b += [setv('_i', 1), rep(n, dict(take), lst_set(lst, V('_i'), V('_v')), chg('_i', 1))]
    # 차트 기록과 '전날 가격'은 불러온 가격으로 다시 시작
    b += [setv('_i', 1), rep(ST.N, lst_set('전주가', V('_i'), LGET('주가', V('_i'))),
                             lst_set('주가기록', add(mul(sub(V('_i'), 1), ST.HIST), 1), LGET('주가', V('_i'))), chg('_i', 1))]
    b += [lst_set('주식이름', ST.CTL, LGET('지배이름', V('단계')))]
    import invest as IV
    b += IV.scale_blocks()
    b += [setv('_i', 1), rep(20, lst_set('회사기록', V('_i'), V('회사가치')), chg('_i', 1))]
    b += [setv('기록위치', 1), setv('채움', 1), setv('결과처리됨', 1), setv('현재지역', 0), setv('개표창', 0), setv('작전단계', 0),
          setv('재계산', 1),
          # 게임을 꺼 둔 동안은 수입이 쌓이지 않는다: 불러온 시각부터 다시 센다
          setv('마지막시각', 0)]
    _FN['load'] = _P.new_function('불러오기', b)
    return [dict(_FN['load'])]


def clear_blocks():
    """게임이 끝나면(군수 선거 패배·파산·끝내기) 내 저장 칸(A·B·백업 C)을 모두 비운다."""
    if 'clear' not in _FN:
        body = [if_(logged_in(), *_search(_slot_key('A'), '저장위치A'), *_search(_slot_key('B'), '저장위치B'),
                    if_(gt(V('저장위치A'), 0), lst_set('저장칸목록', V('저장위치A'), join(_slot_key('A'), '없음'))),
                    if_(gt(V('저장위치B'), 0), lst_set('저장칸목록', V('저장위치B'), join(_slot_key('B'), '없음'))),
                    *_member_search(),
                    if_(_chunks_ok(), *[lst_set(nm, V('회원번호'), '') for nm in CHUNKS]))]
        _FN['clear'] = _P.new_function('저장지우기', body)
    return [dict(_FN['clear']), setv('저장있음', 0), setv('저장필요', 0)]


def save_button(P, sc, x, y):
    """'저장' 버튼: 누르면 바로 저장하고 결과를 알려 준다 (경제알림 글상자 사용)."""
    from gui import button
    return button(P, sc, '지금저장', '지금 저장', x, y, 78, 22, 'green', icon='star',
                  actions=[ifelse(logged_in(),
                                  [*save_blocks(), setv('경제알림', join('저장 완료! 저장 번호 ', V('저장번호'), ' · 서버 저장 ', LLEN('저장칸목록'), '칸'))],
                                  [setv('경제알림', '엔트리에 로그인해야 저장돼요')]),
                           cast('경제알림')])


def quit_button(P, sc, x, y):
    """'저장하고 끝내기': 저장한 뒤 작품을 정지한다. 정지할 때 공유 리스트(백업)가 서버에 올라가므로,
    실시간 연결이 끊겼더라도 이 버튼으로 끝내면 기록이 남는다."""
    from gui import button
    return button(P, sc, '저장끝내기', '저장·끝내기', x, y, 82, 22, 'red', icon='back',
                  actions=[ifelse(logged_in(),
                                  # 실시간 리스트는 서버 응답을 기다리므로 건너뛰고, 정지할 때 서버로 가는 백업만 확실히 쓴다
                                  [*backup_blocks(), setv('경제알림', '저장했어요! 작품을 정지합니다'), cast('경제알림'), wait(0.8),
                                   {'type': 'stop_run', 'params': [None], 'statements': []}],
                                  [setv('경제알림', '엔트리에 로그인해야 저장돼요'), cast('경제알림')])])
