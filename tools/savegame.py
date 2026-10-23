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

VERSION = 'S4'
SEP, KEY = '|', '§'
SAVE_VARS = ['돈', '내지지율', '큰A', '큰B', '유세횟수', '방어권', '차단턴', '장시간', '첫째주', '둘째주', '지배알림',
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
    for v, d in (('내계정', ''), ('저장위치', 0), ('저장있음', 0), ('저장글', ''), ('_불러온', ''), ('_sp', 0), ('_si', 0),
                 ('_dg', '')):
        P.var(v, d)


def logged_in():
    # 로그인하지 않으면 계정 아이디가 ' ' (엔트리 비교에서는 0 으로 바뀌어 ' ' 와 같다고 나옴)
    return ne(V('내계정'), ' ')


def _my_key():
    return join(V('내계정'), KEY)


def _search():
    """저장목록에서 내 칸 찾기 (최근 칸부터)."""
    return [setv('저장위치', 0), setv('_si', LLEN('저장목록')),
            until(or_(lt(V('_si'), 1), gt(V('저장위치'), 0)),
                  if_(eq(str_index(LGET('저장목록', V('_si')), _my_key()), 1), setv('저장위치', V('_si'))),
                  chg('_si', -1))]


def find_blocks():
    """타이틀에서: 내 계정의 저장 칸을 찾고, 쓸 수 있는 저장이 있으면 저장있음=1 (내용은 _불러온 에)."""
    return [setv('내계정', user_id()), setv('저장위치', 0), setv('저장있음', 0),
            if_(logged_in(),
                *_search(),
                if_(gt(V('저장위치'), 0),
                    setv('_불러온', LGET('저장목록', V('저장위치'))),
                    setv('_불러온', substr(V('_불러온'), add(slen(V('내계정')), 2), slen(V('_불러온')))),
                    if_(and_(eq(str_index(V('_불러온'), VERSION + SEP), 1), eq(str_count(V('_불러온'), SEP), FIELDS + 1)),
                        setv('저장있음', 1))))]


def save_blocks():
    """저장 함수를 부르는 블록 (함수 본문은 한 번만 만든다)."""
    if 'save' not in _FN:
        _FN['save'] = _P.new_function('저장하기', _save_body())
    return [dict(_FN['save'])]


def _save_body():
    """지금 상태를 저장 (한 프레임 안에 끝나도록 반복 없이 펼쳐서)."""
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
                *data,
                # 내 칸 번호가 맞는지 확인 (아니면 다시 찾기)
                if_(gt(V('저장위치'), LLEN('저장목록')), setv('저장위치', 0)),
                if_(gt(V('저장위치'), 0), if_(ne(str_index(LGET('저장목록', V('저장위치')), _my_key()), 1), setv('저장위치', 0))),
                ifelse(gt(V('저장위치'), 0), [lst_set('저장목록', V('저장위치'), join(_my_key(), V('저장글')))],
                       [lst_add('저장목록', join(_my_key(), V('저장글'))), *_search()]),
                setv('저장있음', 1))]


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
    """게임이 끝나면(군수 선거 패배·파산·끝내기) 내 저장을 비운다."""
    return [if_(and_(logged_in(), gt(V('저장위치'), 0)),
                if_(le(V('저장위치'), LLEN('저장목록')),
                    if_(eq(str_index(LGET('저장목록', V('저장위치')), _my_key()), 1),
                        lst_set('저장목록', V('저장위치'), join(_my_key(), '없음')))),
                setv('저장있음', 0))]
