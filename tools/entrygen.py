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
    return B('change_to_some_shape', VALUE={'type': 'get_pictures', 'params': [ref('pic', name)]})


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


def script(*blocks):
    return flat(*blocks)


# ---------------------------------------------------------------- project model
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
        self.file = hashlib.md5(self.data).hexdigest()  # 32자
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
        self.id = new_id()

    def on(self, *blocks):
        self.scripts.append(flat(*blocks))
        return self

    def local(self, name, value=0):
        self.locals[name] = value


class Project:
    def __init__(self, name):
        self.name = name
        self.scenes = []        # [(id, name)]
        self.objects = []
        self.vars = {}          # name -> dict
        self.lists = {}         # name -> dict
        self.msgs = {}          # name -> id
        self.pics = {}          # file md5 -> Picture (for packaging)

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

    def list(self, name, items=(), visible=False, x=0, y=0, w=100, h=120):
        self.lists[name] = dict(id=new_id(), items=list(items), visible=visible, x=x, y=y, w=w, h=h)

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
            'movable': None, 'deletable': 1, 'emphasized': False, 'readOnly': None,
            'copyable': True, 'assemble': True, 'extensions': [],
        }
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
            ent = dict(x=o.x, y=o.y, regX=pic.w / 2, regY=pic.h / 2, scaleX=pic.scale * o.scale,
                       scaleY=pic.scale * o.scale, rotation=0, direction=90, width=pic.w, height=pic.h,
                       font='undefinedpx ', visible=o.visible)
            return ent
        w = o.width or 200
        h = o.height or 40
        ent = dict(x=o.x, y=o.y, regX=w / 2, regY=h / 2, scaleX=1, scaleY=1, rotation=0, direction=90,
                   width=w, height=h, text=o.text, font=o.font, colour=o.color,
                   bgColor=(o.bg or 'transparent'), underLine=False, strike=False, textAlign=o.align,
                   lineBreak=o.line_break, visible=o.visible)
        return ent

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
                                  isCloud=False, isRealTime=False, cloudDate=False, object=None,
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
                    id=pic.id, dimension=dict(width=pic.w, height=pic.h, scaleX=pic.scale * o.scale,
                                              scaleY=pic.scale * o.scale),
                    filename=pic.file, name=pic.name, imageType='png',
                    fileurl='temp/%s/%s/image/%s.png' % (pic.file[:2], pic.file[2:4], pic.file)))
            od = dict(id=o.id, name=o.name, script=self._script_json(o), objectType=o.kind,
                      rotateMethod='free', scene=sid_of[o.scene],
                      sprite=dict(pictures=pictures, sounds=[]),
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
            functions=[], tables=[], speed=60,
            interface=dict(canvasWidth=480, menuWidth=280, object=(self.objects[-1].id if self.objects else None)),
            expansionBlocks=[], aiUtilizeBlocks=[], hardwareLiteBlocks=[],
            externalModules=[], externalModulesLite=[],
            isopen=True, name=self.name, isPracticalCourse=False,
        )

    # ---- 출력
    def write_ent(self, out_path, dev_dir=None):
        proj = self.to_json()
        pj = json.dumps(proj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        files = {'temp/project.json': pj}
        for fh, pic in self.pics.items():
            rel = 'temp/%s/%s/' % (fh[:2], fh[2:4])
            files[rel + 'image/%s.png' % fh] = pic.data
            th = pic.im.copy()
            th.thumbnail((96 * pic.w // max(pic.h, 1) if pic.h else 96, 96))
            if th.height > 96:
                th = th.resize((max(1, round(pic.w * 96 / pic.h)), 96))
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
