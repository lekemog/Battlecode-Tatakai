"""Opponent-behaviour features at decision time, from match summaries, using only things a bot
can observe during a match: banked scores (global), our own deaths and where they happened.
Each summary yields one row per perspective (team X facing opponent Y).
Output: /home/claude/data/oppfeat.json"""
import json, os, glob

def tl_at(runs, R):
    s = 0; v = 0
    for r in runs:
        if s > R: break
        v = float(r['value']); s += r['duration']
    return v

def spawns(d):
    pos = {}
    for e in d['events']:
        if e['kind'] in ('buyItem', 'buyConsumable') and e['entries']:
            t = e['owner'].get('team')
            for x in e['entries']:
                pos.setdefault(t, []).append((x['x'], x['y']))
    out = {}
    for t, ps in pos.items():
        # most common purchase tile = spawn area
        best = max(set(ps), key=ps.count)
        out[t] = best
    return out

def rows(path, label_of, meta):
    d = json.load(open(path))
    m = d['match']; W, H = m['width'], m['height']
    sp = spawns(d)
    if len(sp) < 2: return []
    tt = {t['owner']: t['runs'] for t in d['teamTimelines']}
    final = {t['team']: int(t['submittedGems']) for t in d['teams']}
    deaths = {'teamA': [], 'teamB': []}
    for e in d['events']:
        if e['kind'] == 'death':
            t = e['owner'].get('team')
            for x in e['entries']:
                k = x['target'].get('kind') if isinstance(x['target'], dict) else ''
                deaths.setdefault(t, []).append((x['timestamp']['round'], x['x'], x['y'], k))
    out = []
    for us in ('teamA', 'teamB'):
        th = 'teamB' if us == 'teamA' else 'teamA'
        lab = label_of(us)
        if lab is None: continue
        hs, es = sp[us], sp[th]
        def ours_half(x, y):
            return (abs(x - hs[0]) + abs(y - hs[1])) < (abs(x - es[0]) + abs(y - es[1]))
        f = dict(label=lab, map=meta.get('map'), file=os.path.basename(path), W=W, H=H, rounds=m['roundsStarted'],
                 win=m['outcome'] == us, margin=final[us] - final[th])
        for T in (150, 200, 250):
            f[f'e{T}'] = tl_at(tt[th], T); f[f'o{T}'] = tl_at(tt[us], T)
            ch = [x for x in deaths.get(us, []) if x[0] <= T and x[3] == 'champion']
            f[f'd{T}'] = len(ch)
            f[f'inv{T}'] = sum(1 for x in ch if ours_half(x[1], x[2]))
            f[f'k{T}'] = len([x for x in deaths.get(th, []) if x[0] <= T and x[3] == 'champion'])
        out.append(f)
    return out

def main():
    R = []
    top = json.load(open('/home/claude/data/top/top.json'))
    TM = json.load(open('/home/claude/data/top/topmatches.json'))
    for p in glob.glob('/home/claude/data/top/sum/*.json'):
        mid = os.path.basename(p)[:-5]; m = TM.get(mid)
        if not m: continue
        try: R += rows(p, lambda t: 'top', {'map': m['map']})
        except Exception: pass
    ours = {m['matchId']: m for m in json.load(open('/home/claude/data/rk100.json'))['matches']}
    for mid, m in ours.items():
        p = f'/home/claude/data/ranked2/{mid}.json'
        if not os.path.exists(p): continue
        side = 'team' + [t for t in m['teams'] if t['teamId'].startswith('9c16')][0]['side'].upper()
        opp = [t for t in m['teams'] if not t['teamId'].startswith('9c16')][0]['name']
        try: R += rows(p, lambda t: f'US:ranked:{opp}' if t == side else None, {'map': m['map']})
        except Exception: pass
    GC = '/home/claude/data/ab/groupcache.json'
    if os.path.exists(GC):
        for g, v in json.load(open(GC)).items():
            for mm in v['matches']:
                p = f"/home/claude/data/ladder/{mm['matchId']}.json"
                if not os.path.exists(p): continue
                side = 'team' + mm['side'].upper()
                try: R += rows(p, lambda t: f"US:{v['tag']}:{v['name']}" if t == side else None, {'map': mm['map']})
                except Exception: pass
    json.dump(R, open('/home/claude/data/oppfeat.json', 'w'))
    print(len(R), sum(1 for r in R if r['label'].startswith('US')))

main()
