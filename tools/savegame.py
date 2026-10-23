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
SEP, KEY = '|', '§'
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
    P.list('저장목록', [], cloud=True, lid='sv1')
    for v, d in (('내계정', ''), ('저장위치A', 0), ('저장위치B', 0), ('저장슬롯', 0), ('저장번호', 0), ('저장틱', 0), ('저장필요', 0), ('_okA', 0), ('_okB', 0), ('_nA', 0), ('_nB', 0), ('_t', ''), ('_t2', ''), ('저장있음', 0), ('저장글', ''), ('_불러온', ''), ('_sp', 0), ('_si', 0),
                 ('_dg', '')):
        P.var(v, d)


def logged_in():
    # 로그인하지 않으면 계정 아이디가 ' ' (엔트리 비교에서는 0 으로 바뀌어 ' ' 와 같다고 나옴)
    return ne(V('내계정'), ' ')


def _slot_key(letter):
    return join(V('내계정'), KEY, letter)


def _search(key, out):
    """저장목록에서 key 로 시작하는 칸 찾기 (최근 칸부터). 못 찾으면 out=0."""
    return [setv(out, 0), setv('_si', LLEN('저장목록')),
            until(or_(lt(V('_si'), 1), gt(V(out), 0)),
                  if_(eq(str_index(LGET('저장목록', V('_si')), key), 1), setv(out, V('_si'))),
                  chg('_si', -1))]


def _check(pos, letter, ok, num):
    """칸 pos 의 저장이 온전한지(형식 버전·값 개수) 보고, 저장 번호를 num 에 넣는다 (ok=1 이면 쓸 수 있음)."""
    return [setv(ok, 0), setv(num, 0),
            if_(gt(V(pos), 0),
                setv('_t', LGET('저장목록', V(pos))),
                setv('_t', substr(V('_t'), add(slen(V('내계정')), 3), slen(V('_t')))),
                if_(and_(eq(str_index(V('_t'), VERSION + SEP), 1), eq(str_count(V('_t'), SEP), FIELDS + 1)),
                    setv('_t2', substr(V('_t'), len(VERSION) + 2, slen(V('_t')))),
                    setv('_sp', str_index(V('_t2'), SEP)),
                    setv(num, substr(V('_t2'), 1, sub(V('_sp'), 1))),
                    setv(ok, 1)))]


def find_blocks():
    """타이틀에서: 내 계정의 저장 두 칸(A·B)을 찾아, 온전한 것 중 더 최근 것을 고른다 (저장있음=1, 내용은 _불러온 에)."""
    return [setv('내계정', user_id()), setv('저장위치A', 0), setv('저장위치B', 0), setv('저장있음', 0), setv('저장슬롯', 0),
            if_(logged_in(),
                *_search(_slot_key('A'), '저장위치A'), *_search(_slot_key('B'), '저장위치B'),
                *_check('저장위치A', 'A', '_okA', '_nA'), *_check('저장위치B', 'B', '_okB', '_nB'),
                if_(or_(eq(V('_okA'), 1), eq(V('_okB'), 1)),
                    ifelse(and_(eq(V('_okA'), 1), or_(eq(V('_okB'), 0), ge(V('_nA'), V('_nB')))),
                           [setv('_불러온', LGET('저장목록', V('저장위치A'))), setv('저장슬롯', 1)],
                           [setv('_불러온', LGET('저장목록', V('저장위치B'))), setv('저장슬롯', 2)]),
                    setv('_불러온', substr(V('_불러온'), add(slen(V('내계정')), 3), slen(V('_불러온')))),
                    setv('저장있음', 1)))]


def save_blocks():
    """저장 함수를 부르는 블록 (함수 본문은 한 번만 만든다)."""
    if 'save' not in _FN:
        _FN['save'] = _P.new_function('저장하기', _save_body())
    return [dict(_FN['save'])]


def _write_slot(letter, pos):
    """내 칸(letter)에 저장글을 쓴다. 칸 번호가 어긋났으면 다시 찾고, 없으면 새로 만든다."""
    key = _slot_key(letter)
    return [if_(gt(V(pos), LLEN('저장목록')), setv(pos, 0)),
            if_(gt(V(pos), 0), if_(ne(str_index(LGET('저장목록', V(pos)), key), 1), setv(pos, 0))),
            ifelse(gt(V(pos), 0), [lst_set('저장목록', V(pos), join(key, V('저장글')))],
                   [lst_add('저장목록', join(key, V('저장글'))), *_search(key, pos)])]


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
    return [if_(logged_in(),
                chg('저장번호', 1),
                *data,
                ifelse(eq(V('저장슬롯'), 1), [setv('저장슬롯', 2), *_write_slot('B', '저장위치B')],
                       [setv('저장슬롯', 1), *_write_slot('A', '저장위치A')]),
                setv('저장있음', 1), setv('저장틱', 0), setv('저장필요', 0))]


def tick_blocks():
    """경제 시계(1초마다)에서: 30초마다, 또는 거래·구매 뒤 5초 안에 자동 저장."""
    if 'tick' not in _FN:
        _FN['tick'] = _P.new_function('자동저장틱', [
            chg('저장틱', 1),
            if_(and_(eq(V('저장있음'), 1), gt(V('총자산'), 0)),
                if_(or_(ge(V('저장틱'), 30), and_(eq(V('저장필요'), 1), ge(V('저장틱'), 5))), *save_blocks()))])
    return [dict(_FN['tick'])]


def load_blocks():
    """find_blocks 가 남긴 _불러온 을 풀어서 변수/리스트에 넣는다."""
    b = [setv('_불러온', substr(V('_불러온'), len(VERSION) + 2, slen(V('_불러온'))))]

    def take():
        return [setv('_sp', str_index(V('_불러온'), SEP))], substr(V('_불러온'), 1, sub(V('_sp'), 1)), \
            [setv('_불러온', substr(V('_불러온'), add(V('_sp'), 1), slen(V('_불러온'))))]
    for v in SAVE_VARS:
        pre, val, post = take()
        # 빈 글자(이름 없음)는 substring 이 실패하므로 구분자가 바로 나오면 '' 로
        b += pre + [ifelse(eq(V('_sp'), 1), [setv(v, '')], [setv(v, val)])] + post
    for lst, n in DIGIT_LISTS:
        pre, val, post = take()
        b += pre + [setv('_dg', val)] + post
        b += [lst_set(lst, i, char_at(V('_dg'), i)) for i in range(1, n + 1)]
    for lst, n in SAVE_LISTS:
        for i in range(1, n + 1):
            pre, val, post = take()
            b += pre + [lst_set(lst, i, val)] + post
    # 차트 기록과 '전날 가격'은 불러온 가격으로 다시 시작
    for i in range(1, ST.N + 1):
        b += [lst_set('전주가', i, LGET('주가', i)), lst_set('주가기록', (i - 1) * ST.HIST + 1, LGET('주가', i))]
    b += [lst_set('주식이름', ST.CTL, LGET('지배이름', V('단계')))]
    import invest as IV
    b += IV.scale_blocks()
    b += [lst_set('회사기록', i, V('회사가치')) for i in range(1, 21)]
    b += [setv('기록위치', 1), setv('채움', 1), setv('결과처리됨', 1), setv('현재지역', 0), setv('개표창', 0), setv('작전단계', 0),
          setv('재계산', 1),
          # 게임을 꺼 둔 동안은 수입이 쌓이지 않는다: 불러온 시각부터 다시 센다
          setv('마지막시각', 0)]
    return b


def clear_blocks():
    """게임이 끝나면(군수 선거 패배·파산·끝내기) 내 저장 두 칸을 모두 비운다."""
    if 'clear' not in _FN:
        body = [if_(logged_in(), *_search(_slot_key('A'), '저장위치A'), *_search(_slot_key('B'), '저장위치B'),
                    if_(gt(V('저장위치A'), 0), lst_set('저장목록', V('저장위치A'), join(_slot_key('A'), '없음'))),
                    if_(gt(V('저장위치B'), 0), lst_set('저장목록', V('저장위치B'), join(_slot_key('B'), '없음'))))]
        _FN['clear'] = _P.new_function('저장지우기', body)
    return [dict(_FN['clear']), setv('저장있음', 0), setv('저장필요', 0)]


def save_button(P, sc, x, y):
    """'저장' 버튼: 누르면 바로 저장하고 결과를 알려 준다 (경제알림 글상자 사용)."""
    from gui import button
    return button(P, sc, '지금저장', '지금 저장', x, y, 78, 22, 'green', icon='star',
                  actions=[ifelse(logged_in(),
                                  [*save_blocks(), setv('경제알림', '저장 완료! 같은 계정이면 어느 컴퓨터에서든 이어해요')],
                                  [setv('경제알림', '엔트리에 로그인해야 저장돼요')]),
                           cast('경제알림')])
