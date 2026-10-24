import json, sys, tarfile
EXTRA = ',"movable":null,"deletable":1,"emphasized":false,"readOnly":null,"copyable":true,"assemble":true,"extensions":[]'
def blk_size(b):
    if isinstance(b, dict):
        s = len('{"id":"abcd","x":0,"y":0,"type":%s,"params":[' % json.dumps(b.get('type'), ensure_ascii=False)) + 1
        ps = b.get('params', []) or []
        s += sum(blk_size(x) for x in ps) + max(0, len(ps) - 1)
        s += len('],"statements":[') + 1
        sts = b.get('statements', []) or []
        for st in sts:
            s += 2 + sum(blk_size(x) for x in st or []) + max(0, len(st or []) - 1)
        s += max(0, len(sts) - 1) + len(EXTRA) + 1
        return s
    return len(json.dumps(b, ensure_ascii=False).encode('utf-8'))
def est(p):
    tot = 0
    for o in p['objects']:
        sc = json.loads(o['script']) if isinstance(o['script'], str) else o['script']
        tot += sum(blk_size(b) for s in sc for b in s) + 4 * len(sc)
        oo = dict(o); oo['script'] = ''
        tot += len(json.dumps(oo, ensure_ascii=False).encode('utf-8')) + 200
    for f in p.get('functions', []):
        c = json.loads(f['content']) if isinstance(f['content'], str) else f['content']
        tot += sum(blk_size(b) for s in c for b in s) + 100
    tot += len(json.dumps(p['variables'], ensure_ascii=False).encode('utf-8'))
    return tot
if __name__ == '__main__':
    for path in sys.argv[1:]:
        p = json.loads(tarfile.open(path).extractfile('temp/project.json').read()) if path.endswith('.ent') else json.load(open(path))
        print(path.split('/')[-1], round(est(p) / 1e6, 2), 'MB')
