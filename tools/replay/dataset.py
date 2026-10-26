"""Imitation dataset: at sampled rounds, for each alive champion, candidate camp groups with
features our bot can compute, labelled by the group the champion engages next.
usage: dataset.py -> /home/claude/data/rep/dataset.npz"""
import json, glob, os, collections, math, sys
import numpy as np

HASH = {'rows': '25d8', 'collision': '2e98', 'monolith': '3991', 'contest': '3a5c', 'eight': '3e2d', 'ambush': '699c',
        'pilgrimage': '7bfc', 'expanse': '8192', 'lanes': '9385', 'fragment': '9925', 'packs': 'b135', 'interlock': 'b777',
        'elkring': 'bb12', 'rushbait_v2': 'df22', 'corners': 'e3c2', 'stampede': 'f2b6', 'swirl': 'f930'}
# camp kind -> (hp, strength), matches bot camp_stats_for: wolf, elk, monolith, other
KIND = {0: (1350, 20), 1: (2400, 60), 2: (20000, 200)}

def load_map(name):
    f = [p for p in glob.glob('/home/claude/data/mapdump/p_*.txt') if os.path.basename(p)[2:6] == HASH[name]][0]
    M = {'groups': []}
    txt = open(f).read().replace('DUMP ', '\nDUMP ')
    seen_g = set()
    for line in txt.split('\n'):
        t = line.split()
        if len(t) < 2 or t[0] != 'DUMP': continue
        if t[1] == 'group':
            if t[2] in seen_g or len(t) < 8: continue
            seen_g.add(t[2])
        if t[1].startswith('W='): M['W'] = int(t[1][2:]); M['H'] = int(t[2][2:])
        elif t[1] in ('walls', 'altars', 'spawnA', 'spawnB'):
            pts = []
            for x in t[2:]:
                a = x.split(',')
                if len(a) == 2 and a[0].isdigit() and a[1].isdigit(): pts.append((int(a[0]), int(a[1])))
            M[t[1]] = sorted(set(M.get(t[1], [])) | set(pts))
        elif t[1] == 'group':
            kv = dict(x.split('=') for x in t[3:6])
            camps = []
            for x in t[7:]:
                k, pos = x.split(':'); camps.append((int(k), tuple(map(int, pos.split(',')))))
            M['groups'].append({'gems': int(kv['gems']), 'gold': int(kv['gold']), 'resp': int(kv['resp']), 'camps': camps})
    W, H = M['W'], M['H']
    blocked = np.zeros((W, H), bool)
    for x, y in M.get('walls', []): blocked[x, y] = True
    for x, y in M.get('altars', []): blocked[x, y] = True
    M['blocked'] = blocked
    def bfs(srcs):
        D = np.full((W, H), 9999, np.int32)
        from collections import deque
        q = deque()
        for s in srcs:
            if 0 <= s[0] < W and 0 <= s[1] < H: D[s] = 0; q.append(s)
        while q:
            x, y = q.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and not blocked[nx, ny] and D[nx, ny] > D[x, y] + 1:
                        D[nx, ny] = D[x, y] + 1; q.append((nx, ny))
        return D
    for g in M['groups']:
        ring = set()
        for _, (x, y) in g['camps']:
            for dx in range(-1, 2):
                for dy in range(-1, 2): ring.add((x + dx, y + dy))
        g['D'] = bfs(list(ring))
        g['center'] = (sum(p[0] for _, p in g['camps']) / len(g['camps']), sum(p[1] for _, p in g['camps']) / len(g['camps']))
        g['hp'] = sum(KIND.get(k, (500, 0))[0] for k, _ in g['camps'])
        g['str'] = sum(KIND.get(k, (500, 0))[1] for k, _ in g['camps'])
        g['mono'] = any(k == 2 for k, _ in g['camps'])
    ring = set()
    for x, y in M.get('altars', []):
        for dx in range(-1, 2):
            for dy in range(-1, 2): ring.add((x + dx, y + dy))
    M['altarD'] = bfs(list(ring)) if ring else np.zeros((W, H), np.int32)
    M['bfs'] = bfs
    M['spawnD'] = [bfs(M['spawnA']), bfs(M['spawnB'])] if M.get('spawnA') and M.get('spawnB') else None
    return M

FEATS = ['logd', 'wait', 'gems', 'gold', 'hpfrac_grp', 'clear', 'danger', 'altar_d', 'side', 'ally_near', 'enemy_near',
         'rate', 'my_hp', 'carry', 'alive', 'cur']

def main():
    maps = {}
    meta = json.load(open('/home/claude/data/rep/meta.json'))
    X, G, ROWS = [], [], []
    for p in sorted(glob.glob('/home/claude/data/rep/json/*.json')):
        mid = os.path.basename(p)[:-5]
        if mid not in meta: continue
        name = meta[mid]['map']
        if name not in maps: maps[name] = load_map(name)
        M = maps[name]
        try: d = json.load(open(p))
        except Exception: continue
        R = d['rounds']
        groups = M['groups']
        if M['spawnD'] is None:
            sp = [[(c['position']['x'], c['position']['y']) for c in R[1]['champions'] if c['team'] == tm and c.get('position')] for tm in (0, 1)]
            if not sp[0] or not sp[1]: continue
            M['spawnD'] = [M['bfs'](sp[0]), M['bfs'](sp[1])]
        if len(R) < 50 or len(R[50]['groups']) != len(groups): print('skip groups', name, len(R[50]['groups']) if len(R)>50 else 0, len(groups)); continue
        for gi, g in enumerate(groups):
            cs = [cc for cc in R[1]['camps'] if cc['group'] == gi]
            g['hp'] = sum(cc['maxHealth'] for cc in cs) or g['hp']
            g['str'] = sum(cc['strength']['effective'] for cc in cs)
            g['mono'] = any(cc['maxHealth'] >= 15000 for cc in cs)
        # camp entity -> group, from snapshots
        T = len(R)
        # per round: champion positions
        def cpos(c): return (c['position']['x'], c['position']['y']) if c.get('position') else None
        # engagement: champion within 3 (chebyshev) of a camp of a group whose camps are alive, or capturing
        def engaged(r, c):
            p = cpos(c)
            if p is None or not c.get('alive'): return -1
            best = -1; bd = 99
            for gi, g in enumerate(groups):
                st = r['groups'][gi]
                alive = any(cc['group'] == gi and cc['health'] > 0 for cc in r['camps'])
                if not (alive or st['state'] == 2): continue
                dd = min(max(abs(p[0] - x), abs(p[1] - y)) for _, (x, y) in g['camps'])
                if dd <= 3 and dd < bd: bd, best = dd, gi
            return best
        eng = [[engaged(r, c) for c in r['champions']] for r in R]
        nC = min(len(r['champions']) for r in R[10:])
        # decision points: the round a champion stops engaging a group (or first free round)
        points = []
        for ci in range(nC):
            prev = None
            for t in range(10, T - 30):
                e = eng[t][ci]
                if prev is not None and prev >= 0 and e != prev: points.append((t, ci, prev))
                prev = e
        for t, ci_pt, prevg in points:
            r = R[t]
            alive_g = [any(cc['group'] == gi and cc['health'] > 0 for cc in r['camps']) for gi in range(len(groups))]
            ghp = [sum(cc['health'] for cc in r['camps'] if cc['group'] == gi) for gi in range(len(groups))]
            for ci in [ci_pt]:
                c = r['champions'][ci]
                p = cpos(c)
                if p is None or not c.get('alive'): continue
                lab = eng[t][ci] if eng[t][ci] >= 0 and eng[t][ci] != prevg else -1
                for u in range(t + 1, min(T, t + 60)):
                    if lab >= 0: break
                    if eng[u][ci] >= 0 and eng[u][ci] != prevg: lab = eng[u][ci]; break
                    if not R[u]['champions'][ci].get('alive'): break
                if lab < 0: continue
                team = c['team']
                if team not in (0, 1): continue
                mates = [cpos(o) for o in r['champions'] if o['team'] == team and o is not c and o.get('alive') and cpos(o)]
                foes = [cpos(o) for o in r['champions'] if o['team'] != team and o.get('alive') and cpos(o)]
                hpf = c['health'] / max(1, c['maxHealth'])
                dps = c['strength']['effective'] + 0.3 * c['focus']['effective']
                cand = []
                for gi, g in enumerate(groups):
                    if g['mono'] or (g['gems'] <= 0 and g['gold'] <= 0): continue
                    dist = int(g['D'][p]) if g['D'][p] < 9999 else 200
                    st = r['groups'][gi]
                    resp = st['respawnRounds'] if (not alive_g[gi] and st['respawnRounds'] >= 0) else 0
                    if not alive_g[gi] and not st.get('rewardAvailable') and resp <= 0: resp = g['resp']
                    wait = max(0, resp - dist)
                    hpg = ghp[gi] if alive_g[gi] else g['hp']
                    clear = hpg / max(1.0, dps)
                    cx, cy = g['center']
                    an = min([max(abs(q[0] - cx), abs(q[1] - cy)) for q in mates] or [99])
                    en = min([max(abs(q[0] - cx), abs(q[1] - cy)) for q in foes] or [99])
                    hd = M['spawnD'][team][int(cx), int(cy)]; ed = M['spawnD'][1 - team][int(cx), int(cy)]
                    side = hd / max(1, hd + ed)
                    val = g['gems'] + 0.15 * g['gold']
                    f = [math.log1p(dist), wait / 50, g['gems'] / 50, g['gold'] / 300, hpg / max(1, g['hp']), min(clear, 300) / 100,
                         g['str'] * clear * 0.3 / max(1, c['maxHealth']), M['altarD'][int(cx), int(cy)] / 50, side,
                         min(an, 30) / 30, min(en, 30) / 30, val / (max(dist, resp) + clear + 5 + 0.3 * M['altarD'][int(cx), int(cy)]),
                         hpf, (c.get('gems') or 0) / 100, float(alive_g[gi] or bool(st.get('rewardAvailable'))), 0.0]
                    cand.append((gi, f))
                if len(cand) < 2 or lab not in [g for g, _ in cand]: continue
                for gi, f in cand:
                    X.append(f); ROWS.append((len(G), gi == lab))
                G.append((mid, name, t, ci, team))
        print(mid, name, len(G), flush=True)
    X = np.array(X, np.float32); y = np.array([r[1] for r in ROWS], np.int8); gid = np.array([r[0] for r in ROWS], np.int32)
    np.savez('/home/claude/data/rep/dataset.npz', X=X, y=y, gid=gid, meta=np.array([json.dumps(g) for g in G]))
    print('decisions', len(G), 'rows', len(X))

main()
