# -*- coding: utf-8 -*-
"""엔트리 서버 저장 점검용 작은 작품: 실시간 리스트(짧은 글/긴 글/3글자 id) · 공유 리스트 비교."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('FONT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts'))
from entrygen import *
import gui as G
from gui import text, button

P = Project('저장 점검')
sc = '점검'
P.scene(sc)
G.bg(P, sc, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'probe_bg.png'))
P.list('실시간A', [], cloud='realtime', lid='rtla')
P.list('실시간C', [], cloud='realtime', lid='rt3')
P.list('실시간D', [], cloud='realtime', lid='rtld')
P.list('공유B', [], cloud='shared', lid='shlb')
P.var('계정', '')
LONG = 'X' * 1200
text(P, sc, '제목', '저장 점검 (버튼 누르고 → 창 닫기 → 다시 열기)', 0, 115, 11, '#FFFFFF', G.F_BODY, True, 0, w=460, h=18)
st = text(P, sc, '상태', '', 0, 40, 11, '#FFE27A', G.F_NUM, False, 0, w=460, h=110)
st.on(on_run(), setv('계정', user_id()),
      forever(write(join('계정: [', V('계정'), ']\n',
                         'A 실시간(짧은 글): ', LLEN('실시간A'), '칸\n', 'D 실시간(긴 글 1200자): ', LLEN('실시간D'), '칸\n',
                         'C 실시간(id 3글자): ', LLEN('실시간C'), '칸\n',
                         'B 공유(정지해야 저장): ', LLEN('공유B'), '칸')), wait(0.5)))
button(P, sc, 'b1', 'A 짧은 글 +1', -165, -40, 140, 28, 'royal', actions=[lst_add('실시간A', join('짧', V('계정')))])
button(P, sc, 'b2', 'D 긴 글(1200자) +1', -10, -40, 150, 28, 'purple', actions=[lst_add('실시간D', LONG)])
button(P, sc, 'b3', 'C +1', 140, -40, 90, 28, 'green', actions=[lst_add('실시간C', 'c')])
button(P, sc, 'b4', 'B 공유 +1', -165, -80, 140, 28, 'blue', actions=[lst_add('공유B', 'b')])
text(P, sc, '안내', 'B는 정지(■) 버튼을 눌러야 저장돼요. A·C·D는 누르는 즉시 저장돼야 정상.', 0, -118, 9, '#AAB4D0', G.F_BODY, True, 0, w=460, h=14)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '업로드테스트', '저장점검.ent')
P.write_ent(out)
print('ok', out, os.path.getsize(out))
