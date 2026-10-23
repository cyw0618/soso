# -*- coding: utf-8 -*-
"""엔트리(.ent) 프로젝트 생성기.

엔트리 런타임(@entrylabs/entry)의 블록 정의에서 뽑은 시그니처(blocks_sig.json)를 기준으로
블록 JSON을 만들고, project.json 과 이미지 에셋을 gzip tar(.ent)로 묶는다.

.ent 구조 (실제 .ent 샘플과 dotent 소스로 확인한 형식)
    gzip( tar )
      temp/project.json
      temp/<파일명[0:2]>/<파일명[2:4]>/image/<파일명>.png
      temp/<파일명[0:2]>/<파일명[2:4]>/thumb/<파일명>.png

사용 방법은 build_game.py 참고. 장면/변수/리스트/신호/오브젝트/모양은 이름으로 참조하면
빌드 마지막에 ID 로 치환된다.
"""
import copy
import gzip
import hashlib
import io
import json
import os
import random
import tarfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SIG = json.load(open(os.path.join(HERE, 'blocks_sig.json'), encoding='utf-8'))
# blocks_sig.json 에 빠진 글자 블록 (엔트리 block_calc 정의 그대로)
SIG.setdefault('index_of_string', {
    'params': [{'type': 'Text', 'text': ''}, {'type': 'Block'}, {'type': 'Text', 'text': '에서'}, {'type': 'Block'},
               {'type': 'Text', 'text': '의 시작 위치'}],
    'def': {'params': [None, {'type': 'text', 'params': ['안녕 엔트리!']}, None, {'type': 'text', 'params': ['엔트리']}, None],
            'type': 'index_of_string'},
    'paramsKeyMap': {'LEFTHAND': 1, 'RIGHTHAND': 3}, 'cls': 'calc_string', 'skeleton': 'basic_string_field', 'statements': 0})
SIG.setdefault('count_match_string', {
    'params': [{'type': 'Block'}, {'type': 'Text', 'text': '에서'}, {'type': 'Block'}, {'type': 'Text', 'text': '의 개수'}],
    'def': {'params': [{'type': 'text', 'params': ['엔트리봇']}, None, {'type': 'text', 'params': ['엔트리']}, None],
            'type': 'count_match_string'},
    'paramsKeyMap': {'STRING': 0, 'TARGET': 2}, 'cls': 'calc_string', 'skeleton': 'basic_string_field', 'statements': 0})
SIG.setdefault('replace_string', {
    'params': [{'type': 'Text', 'text': ''}, {'type': 'Block'}, {'type': 'Text', 'text': '의'}, {'type': 'Block'},
               {'type': 'Text', 'text': '을(를)'}, {'type': 'Block'}, {'type': 'Text', 'text': '(으)로 바꾼 값'}],
    'def': {'params': [None, {'type': 'text', 'params': ['안녕 엔트리!']}, None, {'type': 'text', 'params': ['안녕']}, None,
                       {'type': 'text', 'params': ['반가워']}, None], 'type': 'replace_string'},
    'paramsKeyMap': {'STRING': 1, 'OLD_WORD': 3, 'NEW_WORD': 5}, 'cls': 'calc_string', 'skeleton': 'basic_string_field',
    'statements': 0})

# ---------------------------------------------------------------- ids
_rng = random.Random(20260101)
_used_ids = set()


def new_id():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    while True:
        i = ''.join(_rng.choice(chars) for _ in range(4))
        if i not in _used_ids:
            _used_ids.add(i)
            return i


def fmt_num(v):
    if isinstance(v, bool):
        raise TypeError('bool is not a number literal')
    if isinstance(v, int):
        return str(v)
    if float(v).is_integer():
        return str(int(v))
    return repr(round(float(v), 6))


# ---------------------------------------------------------------- block DSL
class Ref(tuple):
    """이름 참조 (빌드 마지막에 id 로 치환)."""


def ref(kind, name):
    return Ref((kind, name))


def lit(v):
    """파이썬 값을 리터럴 블록으로."""
    if isinstance(v, dict) or isinstance(v, Ref):
        return v
    if isinstance(v, bool):
        return {'type': 'True' if v else 'False', 'params': [None]}
    if isinstance(v, (int, float)):
        return {'type': 'number', 'params': [fmt_num(v)]}
    if isinstance(v, str):
        return {'type': 'text', 'params': [v]}
    raise TypeError('cannot make literal from %r' % (v,))


def B(type_, **kw):
    """블록 생성. kw 키는 paramsKeyMap / statementsKeyMap 의 이름."""
    sig = SIG.get(type_)
    if sig is None:
        raise KeyError('unknown block type: %s' % type_)
    pk = sig.get('paramsKeyMap') or {}
    sk = sig.get('statementsKeyMap') or {}
    ptypes = sig['params']
    params = [None] * len(ptypes)
    # 기본값 (def.params) 을 먼저 깔고, 호출자가 준 값으로 덮어쓴다
    defp = (sig.get('def') or {}).get('params') or []
    for i, d in enumerate(defp):
        if i < len(params) and d is not None:
            params[i] = copy.deepcopy(d)
    statements = [[] for _ in range(sig.get('statements') or 0)]
    for k, v in kw.items():
        if k in pk:
            i = pk[k]
            if ptypes[i]['type'] == 'Block':
                params[i] = lit(v)
            else:
                params[i] = v
        elif k in sk:
            statements[sk[k]] = [s for s in flat(v)]
        else:
            raise KeyError('%s has no param %s (params=%s statements=%s)' % (type_, k, list(pk), list(sk)))
    return {'type': type_, 'params': params, 'statements': statements}


def flat(*items):
    out = []
    for it in items:
        if it is None:
            continue
        if isinstance(it, (list, tuple)) and not isinstance(it, Ref):
            out.extend(flat(*it))
        else:
            out.append(it)
    return out


# ---- 리터럴/참조
def n(x):
    return lit(float(x) if isinstance(x, float) else int(x))


def t(s):
    return {'type': 'text', 'params': [str(s)]}


def V(name):
    return {'type': 'get_variable', 'params': [ref('var', name), None]}


def LGET(lst, idx):
    return B('value_of_index_from_list', LIST=ref('list', lst), INDEX=idx)


def LLEN(lst):
    return B('length_of_list', LIST=ref('list', lst))


# ---- 연산
def _calc(op, a, b):
    return B('calc_basic', LEFTHAND=a, OPERATOR=op, RIGHTHAND=b)


def add(a, b, *more):
    r = _calc('PLUS', a, b)
    for m in more:
        r = _calc('PLUS', r, m)
    return r


def sub(a, b):
    return _calc('MINUS', a, b)


def mul(a, b):
    return _calc('MULTI', a, b)


def div(a, b):
    return _calc('DIVIDE', a, b)


def rnd(a, b):
    return B('calc_rand', LEFTHAND=a, RIGHTHAND=b)


def mod(a, b):
    return B('quotient_and_mod', LEFTHAND=a, RIGHTHAND=b, OPERATOR='MOD')


def quo(a, b):
    return B('quotient_and_mod', LEFTHAND=a, RIGHTHAND=b, OPERATOR='QUOTIENT')


def fn(op, a):
    return B('calc_operation', LEFTHAND=a, VALUE=op)  # floor/ceil/round/abs/root/square ...


def abs_(a):
    return fn('abs', a)


def floor(a):
    return fn('floor', a)


def rounded(a):
    return fn('round', a)


def join(*parts):
    parts = [lit(p) for p in parts]
    r = parts[0]
    for p in parts[1:]:
        r = B('combine_something', VALUE1=r, VALUE2=p)
    return r


def slen(s):
    return B('length_of_string', STRING=s)


def char_at(s, i):
    return B('char_at', LEFTHAND=s, RIGHTHAND=i)


def str_index(s, t):
    """s 안에서 t 가 처음 나오는 위치 (1부터, 없으면 0)."""
    return B('index_of_string', LEFTHAND=s, RIGHTHAND=t)


def str_count(s, t):
    """s 안에 t 가 몇 번 들어 있는지."""
    return B('count_match_string', STRING=s, TARGET=t)


def str_replace(s, old, new):
    """s 안의 old 를 모두 new 로 (엔트리는 old 를 정규식으로 쓰므로 특수 문자는 피할 것)."""
    return B('replace_string', STRING=s, OLD_WORD=old, NEW_WORD=new)


def date_(kind):
    """현재 YEAR / MONTH / DAY / DAY_OF_WEEK / HOUR / MINUTE / SECOND."""
    return B('get_date', VALUE=kind)


def now_sec():
    """실제 시계로 잰 초 (달이 바뀌어도 줄어들지 않게 한 달 = 31일로 계산)."""
    days = add(add(mul(date_('YEAR'), 372), mul(date_('MONTH'), 31)), date_('DAY'))
    return add(mul(add(mul(add(mul(days, 24), date_('HOUR')), 60), date_('MINUTE')), 60), date_('SECOND'))


def user_id():
    """로그인한 엔트리 계정 아이디 (로그인 안 했으면 ' ')."""
    return B('get_user_name')


# ---- 판단
def _cmp(op, a, b):
    return B('boolean_basic_operator', LEFTHAND=a, OPERATOR=op, RIGHTHAND=b)


def eq(a, b):
    return _cmp('EQUAL', a, b)


def ne(a, b):
    return _cmp('NOT_EQUAL', a, b)


def gt(a, b):
    return _cmp('GREATER', a, b)


def lt(a, b):
    return _cmp('LESS', a, b)


def ge(a, b):
    return _cmp('GREATER_OR_EQUAL', a, b)


def le(a, b):
    return _cmp('LESS_OR_EQUAL', a, b)


def and_(a, b, *more):
    r = B('boolean_and_or', LEFTHAND=a, OPERATOR='AND', RIGHTHAND=b)
    for m in more:
        r = B('boolean_and_or', LEFTHAND=r, OPERATOR='AND', RIGHTHAND=m)
    return r


def or_(a, b, *more):
    r = B('boolean_and_or', LEFTHAND=a, OPERATOR='OR', RIGHTHAND=b)
    for m in more:
        r = B('boolean_and_or', LEFTHAND=r, OPERATOR='OR', RIGHTHAND=m)
    return r


def not_(a):
    return B('boolean_not', VALUE=a)


def key(code):
    return B('is_press_some_key', VALUE=str(code))


def touch(target):
    """target: 'mouse' | 'wall' | 'wall_up' ... | 오브젝트 이름"""
    if target in ('mouse', 'wall', 'wall_up', 'wall_down', 'wall_left', 'wall_right'):
        return B('reach_something', VALUE=target)
    return B('reach_something', VALUE=ref('obj', target))


def mouse_down():
    """마우스를 누르고 있는가?"""
    return B('is_clicked')


def mouse_x():
    return B('coordinate_mouse', VALUE='x')


def mouse_y():
    return B('coordinate_mouse', VALUE='y')


def obj_x(name='self'):
    return B('coordinate_object', VALUE=('self' if name == 'self' else ref('obj', name)), COORDINATE='x')


def obj_y(name='self'):
    return B('coordinate_object', VALUE=('self' if name == 'self' else ref('obj', name)), COORDINATE='y')


def timer():
    return {'type': 'get_project_timer_value', 'params': [None, None]}


def answer():
    return {'type': 'get_canvas_input_value', 'params': [None]}


COMPACT = True    # 블록 JSON 을 짧게 (False 면 엔트리 저장 형식 그대로)


# ---- 키 코드
K_LEFT, K_UP, K_RIGHT, K_DOWN = 37, 38, 39, 40
K_SPACE, K_ENTER = 32, 13
K_A, K_S, K_D, K_F, K_J, K_K, K_L = 65, 83, 68, 70, 74, 75, 76
K_Z, K_X, K_C = 90, 88, 67
K_1, K_2, K_3, K_4, K_5 = 49, 50, 51, 52, 53


# ---- 문(Statement)
def setv(name, v):
    return B('set_variable', VARIABLE=ref('var', name), VALUE=v)


def chg(name, v):
    return B('change_variable', VARIABLE=ref('var', name), VALUE=v)


def wait(sec):
    return B('wait_second', SECOND=sec)


def rep(count, *body):
    return B('repeat_basic', VALUE=count, DO=body)


def forever(*body):
    return B('repeat_inf', DO=body)


def while_(cond, *body):
    return B('repeat_while_true', BOOL=cond, OPTION='while', DO=body)


def until(cond, *body):
    return B('repeat_while_true', BOOL=cond, OPTION='until', DO=body)


def if_(cond, *then):
    return B('_if', BOOL=cond, STACK=then)


def ifelse(cond, then, other):
    return B('if_else', BOOL=cond, STACK_IF=then, STACK_ELSE=other)


def wait_until(cond):
    return B('wait_until_true', BOOL=cond)


def brk():
    return B('stop_repeat')


def cont():
    return B('continue_repeat')


def stop_all():
    return B('stop_object', TARGET='all')


def stop_self():
    return B('stop_object', TARGET='thisOnly')


def stop_thread():
    return B('stop_object', TARGET='thisThread')


def goto_scene(name):
    return B('start_scene', VALUE=ref('scene', name))


def cast(msg):
    return B('message_cast', VALUE=ref('msg', msg))


def cast_wait(msg):
    return B('message_cast_wait', VALUE=ref('msg', msg))


def clone_self():
    return B('create_clone', VALUE='self')


def clone_of(name):
    return B('create_clone', VALUE=ref('obj', name))


def del_clone():
    return B('delete_clone')


def show():
    return B('show')


def hide():
    return B('hide')


def xy(x, y):
    return B('locate_xy', VALUE1=x, VALUE2=y)


def lx(x):
    return B('locate_x', VALUE=x)


def ly(y):
    return B('locate_y', VALUE=y)


def mvx(d):
    return B('move_x', VALUE=d)


def mvy(d):
    return B('move_y', VALUE=d)


def glide(sec, x, y):
    return B('locate_xy_time', VALUE1=sec, VALUE2=x, VALUE3=y)


def rot(deg):
    return B('rotate_absolute', VALUE=deg)


def rot_by(deg):
    return B('rotate_relative', VALUE=deg)


def size(pct):
    return B('set_scale_size', VALUE=pct)


def grow(pct):
    return B('change_scale_size', VALUE=pct)


def shape(name):
    """모양 바꾸기. name 이 문자열이면 그 이름의 모양, 숫자/블록이면 그 값(번호)으로 바꾼다."""
    if isinstance(name, str):
        return B('change_to_some_shape', VALUE={'type': 'get_pictures', 'params': [ref('pic', name)]})
    return B('change_to_some_shape', VALUE=name)


def next_shape():
    return B('change_to_next_shape', DRIECTION='next')


def fx(effect, v):
    """효과를 v 로 정한다. effect: color | brightness | transparency"""
    return B('change_effect_amount', EFFECT=effect, VALUE=v)


def fx_add(effect, v):
    return B('add_effect_amount', EFFECT=effect, VALUE=v)


def fx_clear():
    return B('erase_all_effects')


def to_front():
    return B('change_object_index', LOCATION='FRONT')


def to_back():
    return B('change_object_index', LOCATION='BACK')


def say(text, sec=None):
    if sec is None:
        return B('dialog', VALUE=text, OPTION='speak')
    return B('dialog_time', VALUE=text, SECOND=sec, OPTION='speak')


def unsay():
    return B('remove_dialog')


def write(text):
    return B('text_write', VALUE=text)


def ask(text):
    return B('ask_and_wait', VALUE=text)


def lst_add(lst, v):
    return B('add_value_to_list', VALUE=v, LIST=ref('list', lst))


def lst_del(lst, idx):
    return B('remove_value_from_list', VALUE=idx, LIST=ref('list', lst))


def lst_set(lst, idx, v):
    return B('change_value_list_index', LIST=ref('list', lst), INDEX=idx, DATA=v)


def lst_ins(lst, idx, v):
    return B('insert_value_to_list', DATA=v, LIST=ref('list', lst), INDEX=idx)


def lst_has(lst, v):
    return B('is_included_in_list', LIST=ref('list', lst), DATA=v)


def reset_timer():
    return B('choose_project_timer_action', ACTION='RESET')


def start_timer():
    return B('choose_project_timer_action', ACTION='START')


# ---- 이벤트(Hat)
def on_run():
    return B('when_run_button_click')


def on_key(code):
    return B('when_some_key_pressed', VALUE=str(code))


def on_scene():
    return B('when_scene_start')


def on_click():
    return B('when_object_click')


def on_msg(msg):
    return B('when_message_cast', VALUE=ref('msg', msg))


def on_clone():
    return B('when_clone_start')


def on_mouse_down():
    return B('mouse_clicked')


def on_mouse_up():
    return B('mouse_click_cancled')


def script(*blocks):
    return flat(*blocks)


# ---------------------------------------------------------------- project model
RES = float(os.environ.get('RES', '0.6'))      # 그림 해상도 배율 (1 이면 줄이지 않음)
_SHRINK_CACHE = {}


class Picture:
    def __init__(self, name, path, scale=0.5):
        self.name = name
        self.path = path
        self.scale = scale
        with open(path, 'rb') as f:
            self.data = f.read()
        im = Image.open(io.BytesIO(self.data))
        self.w, self.h = im.size
        self.im = im.convert('RGBA')
        self.ext = 'jpg' if path.lower().endswith('.jpg') else 'png'
        if self.ext == 'jpg':
            pass        # JPEG 그림(인트로 영상 프레임)은 그대로 쓴다
        elif RES < 1.0 and self.w * self.h > 64 :
            self._shrink()
        self.file = hashlib.md5(self.data).hexdigest()  # 32자
        self.id = new_id()

    def _shrink(self):
        """작품 파일(.ent) 용량 제한(16MB)에 맞추려고 그림을 RES 배로 줄이고 128색으로 만든다.
        화면에 보이는 크기는 그대로 (scale 을 그만큼 키운다)."""
        key = (hashlib.md5(self.data).hexdigest(), RES)
        hit = _SHRINK_CACHE.get(key)
        if hit is None:
            w2, h2 = max(1, round(self.w * RES)), max(1, round(self.h * RES))
            im = self.im.resize((w2, h2), Image.LANCZOS)
            try:
                import imagequant
                q = imagequant.quantize_pil_image(im, dithering_level=0.5, max_colors=128)
            except Exception:
                q = im.quantize(colors=128, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
            buf = io.BytesIO()
            q.save(buf, 'PNG', optimize=True)
            data = buf.getvalue()
            try:
                import oxipng
                data = oxipng.optimize_from_memory(data, level=3)
            except Exception:
                pass
            hit = (data, w2, h2, im)
            _SHRINK_CACHE[key] = hit
        data, w2, h2, im = hit
        self.scale = self.scale * self.w / float(w2)
        self.data, self.w, self.h, self.im = data, w2, h2, im


class Sound:
    def __init__(self, name, path, duration):
        self.name = name
        with open(path, 'rb') as f:
            self.data = f.read()
        self.file = hashlib.md5(self.data).hexdigest()
        self.duration = float(duration)
        self.id = new_id()


class Obj:
    def __init__(self, project, name, scene, kind='sprite', pictures=None, x=0, y=0,
                 scale=1.0, visible=True, text=None, font='20px Nanum Gothic',
                 color='#000000', bg=None, width=None, height=None, align=0,
                 line_break=False, bold=False):
        self.p = project
        self.name = name
        self.scene = scene
        self.kind = kind
        self.pictures = pictures or []
        self.x, self.y = x, y
        self.scale = scale
        self.visible = visible
        self.text = text if text is not None else name
        self.font = ('bold ' if bold else '') + font
        self.color = color
        self.bg = bg
        self.width, self.height = width, height
        self.align = align
        self.line_break = line_break
        self.scripts = []
        self.locals = {}
        self.sounds = []
        self.id = new_id()

    def on(self, *blocks):
        self.scripts.append(flat(*blocks))
        return self

    @property
    def base_size(self):
        """엔트리 '크기'(픽셀, 가로·세로 평균) 기준의 원래 크기."""
        if self.kind != 'sprite' or not self.pictures:
            return 100.0
        pic = self.pictures[0]
        k = pic.scale * self.scale
        return (pic.w * k + pic.h * k) / 2.0

    def pct(self, p):
        """크기를 원래의 p% 로 (엔트리 크기 블록은 픽셀 단위라 환산)."""
        b = self.base_size
        if isinstance(p, (int, float)):
            return B('set_scale_size', VALUE=round(b * p / 100.0, 2))
        return B('set_scale_size', VALUE=mul(p, round(b / 100.0, 4)))

    def grow_pct(self, p):
        b = self.base_size
        if isinstance(p, (int, float)):
            return B('change_scale_size', VALUE=round(b * p / 100.0, 2))
        return B('change_scale_size', VALUE=mul(p, round(b / 100.0, 4)))

    def local(self, name, value=0):
        self.locals[name] = value

    def add_sound(self, name, path, duration):
        self.sounds.append(Sound(name, path, duration))


class Project:
    def __init__(self, name):
        self.name = name
        self.scenes = []        # [(id, name)]
        self.objects = []
        self.vars = {}          # name -> dict
        self.lists = {}         # name -> dict
        self.msgs = {}          # name -> id
        self.functions = []     # [dict(id, name, body)]  (엔트리 '함수' 정의: 같은 코드를 한 번만 두고 호출)
        self.pics = {}          # file md5 -> Picture (for packaging)
        self.snds = {}          # file md5 -> Sound

    # ---- 선언
    def scene(self, name):
        for sid, nm in self.scenes:
            if nm == name:
                return sid
        sid = new_id()
        self.scenes.append((sid, name))
        return sid

    def var(self, name, value=0, visible=False, x=0, y=0):
        self.vars[name] = dict(id=new_id(), value=value, visible=visible, x=x, y=y)

    def list(self, name, items=(), visible=False, x=0, y=0, w=100, h=120, cloud=False, lid=None):
        """cloud=True 면 엔트리 '공유 리스트'(작품을 공유했을 때 모든 사람이 같은 리스트를 씀). lid: 리스트 id 를 직접 지정."""
        self.lists[name] = dict(id=lid or new_id(), items=list(items), visible=visible, x=x, y=y, w=w, h=h, cloud=cloud)

    def msg(self, name):
        if name not in self.msgs:
            self.msgs[name] = new_id()
        return self.msgs[name]

    def sprite(self, name, scene, pics, pic_scale=0.5, **kw):
        """pic_scale: 그림 해상도 배율(2배 해상도로 그린 에셋이면 0.5). kw['scale']: 오브젝트 배율."""
        pictures = []
        for pn, path in pics:
            pic = Picture(pn, path, scale=pic_scale)
            pictures.append(pic)
        o = Obj(self, name, scene, 'sprite', pictures, **kw)
        self.objects.append(o)
        return o

    def textbox(self, name, scene, text='', **kw):
        o = Obj(self, name, scene, 'textBox', [], text=text, **kw)
        self.objects.append(o)
        return o

    # ---- 해석
    def _resolve(self, v, obj):
        if isinstance(v, Ref):
            kind, name = v
            if kind == 'var':
                if obj is not None and name in obj.locals:
                    return obj.local_ids[name]
                if name not in self.vars:
                    raise KeyError('undefined variable %r (obj %s)' % (name, obj.name if obj else None))
                return self.vars[name]['id']
            if kind == 'list':
                if name not in self.lists:
                    raise KeyError('undefined list %r' % name)
                return self.lists[name]['id']
            if kind == 'msg':
                return self.msg(name)
            if kind == 'scene':
                for sid, nm in self.scenes:
                    if nm == name:
                        return sid
                raise KeyError('undefined scene %r' % name)
            if kind == 'obj':
                for o in self.objects:
                    if o.name == name:
                        return o.id
                raise KeyError('undefined object %r' % name)
            if kind == 'pic':
                for pic in obj.pictures:
                    if pic.name == name:
                        return pic.id
                raise KeyError('undefined picture %r in %s' % (name, obj.name))
            if kind == 'snd':
                for sd in obj.sounds:
                    if sd.name == name:
                        return sd.id
                raise KeyError('undefined sound %r in %s' % (name, obj.name))
            raise KeyError(kind)
        return v

    def _finalize_block(self, b, obj, x=0, y=0):
        if b is None:
            return None
        if isinstance(b, Ref):
            return self._resolve(b, obj)
        if not isinstance(b, dict):
            return b
        out = {
            'id': new_id(), 'x': x, 'y': y, 'type': b['type'],
            'params': [self._finalize_block(p, obj) if isinstance(p, (dict, Ref)) else p for p in b.get('params', [])],
            'statements': [[self._finalize_block(s, obj) for s in st] for st in b.get('statements', [])],
        }
        if COMPACT:
            # 엔트리가 기본값으로 채우는 필드는 생략 (project.json 크기를 절반 가까이 줄임)
            if not out['statements']:
                del out['statements']
            if x == 0 and y == 0:
                del out['x'], out['y']
        else:
            out.update({'movable': None, 'deletable': 1, 'emphasized': False, 'readOnly': None,
                        'copyable': True, 'assemble': True, 'extensions': []})
        return out

    def _count(self, b):
        c = 1
        for st in b.get('statements', []):
            for s in st:
                c += self._count(s)
        return c

    def _script_json(self, obj):
        threads = []
        yy = 40
        for sc in obj.scripts:
            if not sc:
                continue
            blocks = []
            for i, b in enumerate(sc):
                blocks.append(self._finalize_block(b, obj, 40 if i == 0 else 0, yy if i == 0 else 0))
            threads.append(blocks)
            yy += 30 * sum(self._count(b) for b in sc) + 40
        return json.dumps(threads, ensure_ascii=False, separators=(',', ':'))

    def _entity(self, o):
        if o.kind == 'sprite':
            pic = o.pictures[0]
            ent = dict(x=o.x, y=o.y, regX=pic.w / 2, regY=pic.h / 2, scaleX=round(pic.scale * o.scale, 4),
                       scaleY=round(pic.scale * o.scale, 4), rotation=0, direction=90, width=pic.w, height=pic.h,
                       font='undefinedpx ', visible=o.visible)
            return ent
        w = o.width or 200
        h = o.height or 40
        ent = dict(x=o.x, y=o.y, regX=w / 2, regY=h / 2, scaleX=1, scaleY=1, rotation=0, direction=90,
                   width=w, height=h, text=o.text, font=o.font, colour=o.color,
                   bgColor=(o.bg or 'transparent'), underLine=False, strike=False, textAlign=o.align,
                   lineBreak=o.line_break, visible=o.visible)
        return ent

    def _functions_json(self):
        out = []
        base = self.objects[0] if self.objects else None
        for f in self.functions:
            create = {'type': 'function_create', 'statements': [],
                      'params': [{'type': 'function_field_label', 'params': [f['name'], None], 'statements': []}, None]}
            blocks = [self._finalize_block(b, base, 40 if i == 0 else 0, 40 if i == 0 else 0)
                      for i, b in enumerate([create] + list(f['body']))]
            out.append(dict(id=f['id'], type='normal', localVariables=[], useLocalVariables=False,
                            content=json.dumps([blocks], ensure_ascii=False, separators=(',', ':'))))
        return out

    def new_function(self, name, body):
        """함수를 만들고 부르는 블록을 돌려준다."""
        fid = new_id()
        self.functions.append(dict(id=fid, name=name, body=body))
        return {'type': 'func_' + fid, 'params': [], 'statements': []}

    def to_json(self):
        # 로컬 변수 id 먼저 배정
        for o in self.objects:
            o.local_ids = {nm: new_id() for nm in o.locals}
        variables = [
            dict(name='초시계', id='brih', visible=False, value=0, variableType='timer', isCloud=False,
                 isRealTime=False, cloudDate=False, object=None, x=134, y=-70),
            dict(name=' 대답 ', id='1vu8', visible=False, value='0', variableType='answer', isCloud=False,
                 isRealTime=False, cloudDate=False, object=None, x=150, y=-100),
        ]
        for nm, v in self.vars.items():
            variables.append(dict(name=nm, id=v['id'], visible=v['visible'], value=v['value'],
                                  variableType='variable', isCloud=False, isRealTime=False, cloudDate=False,
                                  object=None, x=v['x'], y=v['y']))
        for nm, v in self.lists.items():
            variables.append(dict(name=nm, id=v['id'], visible=v['visible'], value=0, variableType='list',
                                  isCloud=bool(v.get('cloud')), isRealTime=False, cloudDate=False, object=None,
                                  x=v['x'], y=v['y'], width=v['w'], height=v['h'],
                                  array=[dict(data=str(i)) for i in v['items']]))
        for o in self.objects:
            for nm, val in o.locals.items():
                variables.append(dict(name=nm, id=o.local_ids[nm], visible=False, value=val,
                                      variableType='variable', isCloud=False, isRealTime=False,
                                      cloudDate=False, object=o.id, x=0, y=0))
        sid_of = {nm: sid for sid, nm in self.scenes}
        objects = []
        # 엔트리는 오브젝트 목록의 앞쪽이 화면 맨 앞이다. DSL 에서는 만든 순서가 뒤→앞이므로 뒤집는다.
        for o in reversed(self.objects):
            pictures = []
            for pic in o.pictures:
                self.pics[pic.file] = pic
                pictures.append(dict(
                    id=pic.id, dimension=dict(width=pic.w, height=pic.h, scaleX=round(pic.scale * o.scale, 4),
                                              scaleY=round(pic.scale * o.scale, 4)),
                    filename=pic.file, name=pic.name, imageType=pic.ext,
                    fileurl='temp/%s/%s/image/%s.%s' % (pic.file[:2], pic.file[2:4], pic.file, pic.ext)))
            sounds = []
            for sd in o.sounds:
                self.snds[sd.file] = sd
                sounds.append(dict(duration=sd.duration, id=sd.id, filename=sd.file, name=sd.name,
                                   fileurl='temp/%s/%s/sound/%s.mp3' % (sd.file[:2], sd.file[2:4], sd.file), ext='.mp3'))
            od = dict(id=o.id, name=o.name, script=self._script_json(o), objectType=o.kind,
                      rotateMethod='free', scene=sid_of[o.scene],
                      sprite=dict(pictures=pictures, sounds=sounds),
                      selectedPictureId=(o.pictures[0].id if o.pictures else None),
                      lock=False, entity=self._entity(o))
            if o.kind == 'textBox':
                od['text'] = o.text
            objects.append(od)
        return dict(
            objects=objects,
            scenes=[dict(id=sid, name=nm) for sid, nm in self.scenes],
            variables=variables,
            messages=[dict(id=i, name=nm) for nm, i in self.msgs.items()],
            functions=self._functions_json(), tables=[], speed=60,
            interface=dict(canvasWidth=480, menuWidth=280, object=(self.objects[-1].id if self.objects else None)),
            expansionBlocks=[], aiUtilizeBlocks=[], hardwareLiteBlocks=[],
            externalModules=[], externalModulesLite=[],
            isopen=True, name=self.name, isPracticalCourse=False,
        )

    # ---- 출력
    def write_ent(self, out_path, dev_dir=None, fast=False):
        proj = self.to_json()
        pj = json.dumps(proj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        files = {'temp/project.json': pj}
        if fast and dev_dir:
            # 테스트용 빠른 빌드: .ent 를 만들지 않고, 이미 풀어둔 그림/소리는 건너뛴다
            for fh, sd in self.snds.items():
                files['temp/%s/%s/sound/%s.mp3' % (fh[:2], fh[2:4], fh)] = sd.data
            for fh, pic in self.pics.items():
                files['temp/%s/%s/image/%s.%s' % (fh[:2], fh[2:4], fh, pic.ext)] = pic.data
            for path, data in files.items():
                full = os.path.join(dev_dir, path)
                if path != 'temp/project.json' and os.path.exists(full):
                    continue
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, 'wb') as f:
                    f.write(data)
            return proj
        for fh, sd in self.snds.items():
            files['temp/%s/%s/sound/%s.mp3' % (fh[:2], fh[2:4], fh)] = sd.data
        for fh, pic in self.pics.items():
            rel = 'temp/%s/%s/' % (fh[:2], fh[2:4])
            files[rel + 'image/%s.%s' % (fh, pic.ext)] = pic.data
            # 미리보기(썸네일)는 엔트리 편집 화면의 그림 목록에서만 쓰여서 작게 (실행에는 안 쓰임): 가로세로 32px 이내, 색 64개
            th = pic.im.copy()
            th.thumbnail((24, 24))
            try:
                th = th.quantize(colors=32, method=Image.Quantize.FASTOCTREE)
            except Exception:
                pass
            buf = io.BytesIO()
            th.save(buf, 'PNG', optimize=True)
            files[rel + 'thumb/%s.png' % fh] = buf.getvalue()
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as tar:
            dirs = set()
            for path in files:
                parts = path.split('/')
                for i in range(1, len(parts)):
                    dirs.add('/'.join(parts[:i]))
            for d in sorted(dirs):
                ti = tarfile.TarInfo(d + '/')
                ti.type = tarfile.DIRTYPE
                ti.mode = 0o755
                ti.mtime = 0
                tar.addfile(ti)
            for path, data in files.items():
                ti = tarfile.TarInfo(path)
                ti.size = len(data)
                ti.mode = 0o644
                ti.mtime = 1767225600
                tar.addfile(ti, io.BytesIO(data))
        with open(out_path, 'wb') as f:
            f.write(gzip.compress(raw.getvalue(), 9, mtime=0))
        if dev_dir:
            # 개발용: 풀어놓은 형태 (테스트 하네스에서 사용)
            for path, data in files.items():
                full = os.path.join(dev_dir, path)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, 'wb') as f:
                    f.write(data)
        return proj


# ---- 글상자/붓 보조
def text_color(hexcol):
    return B('text_change_font_color', VALUE={'type': 'text_color', 'params': [hexcol]})


def pen_color(hexcol):
    return B('set_color', VALUE={'type': 'color', 'params': [hexcol]})


def pen_size(n):
    return B('set_thickness', VALUE=n)


def pen_down():
    return B('start_drawing')


def pen_up():
    return B('stop_drawing')


def pen_clear():
    return B('brush_erase_all')


def append_text(v):
    return B('text_append', VALUE=v)


# ---- 수학/복제 보조
def sin_(deg):
    return fn('sin', deg)


def cos_(deg):
    return fn('cos', deg)


def ceil_(a):
    return fn('ceil', a)


def remove_all_clones():
    return B('remove_all_clones')


def flip_x():
    return B('flip_x')


# ---- 소리
def play(name):
    return B('sound_something_with_block', VALUE={'type': 'get_sounds', 'params': [ref('snd', name)]})


def play_wait(name):
    return B('sound_something_wait_with_block', VALUE={'type': 'get_sounds', 'params': [ref('snd', name)]})


def stop_sounds():
    return B('sound_silent_all', TARGET='all')


def substr(s, a, b):
    """s 의 a번째 글자부터 b번째 글자까지."""
    return B('substring', STRING=s, START=a, END=b)
