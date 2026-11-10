"""For each solo capture: champion, round, HP at engage, min HP, rounds fighting, group HP/str. usage: solo.py <json_dir> [maps...]"""
import json, glob, os, sys, math, collections
CH = ['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HeartOfRuin']
J = sys.argv[1]; want = set(sys.argv[2:])
maps = json.load(open(os.path.join(J, 'maps.json')))
agg = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(J, 'match-*.json'))):
    mid = os.path.basename(p)[:-5]; mp = maps[mid][0]
    if want and mp not in want: continue
    d = json.load(open(p)); R = d['rounds']; h = R[-1]['_h']
    gc = collections.defaultdict(dict)
    for r in R:
        for c in r['camps']:
            if c.get('position') and c['entity']['index'] not in gc[c['group']]:
                gc[c['group']][c['entity']['index']] = (c['position']['x'], c['position']['y'], c['maxHealth'], c.get('strength', {}).get('effective'))
    for k in range(1, len(R)):
        a, b = R[k-1]['groups'], R[k]['groups']
        if len(a) != len(b): continue
        for gi, (x, y) in enumerate(zip(a, b)):
            if not (x['state'] == 2 and y['state'] == 3): continue
            t = x['captureTeam']
            if t not in (0, 1): continue
            cs = list(gc[gi].values())
            near = lambda c: c.get('alive') and c.get('position') and min(math.dist((c['position']['x'], c['position']['y']), (cx, cy)) for cx, cy, *_ in cs) <= 4
            team_near = [c for c in R[k-1]['champions'] if c['team'] == t and near(c)]
            if len(team_near) != 1: continue
            me = team_near[0]['entity']['index']
            # walk back while this champion stays near the group
            j = k - 1; hp_min = 1e9; start_hp = None; maxhp = None
            while j > 0:
                c = next(q for q in R[j]['champions'] if q['entity']['index'] == me)
                if not near(c): break
                hp_min = min(hp_min, c['health']); start_hp = c['health']; maxhp = c['maxHealth']; j -= 1
            fight = k - 1 - j
            ghp = sum(c[2] for c in cs); gstr = sum((c[3] or 0) for c in cs)
            win = h['outcome'] == t + 1
            ch = CH[team_near[0]['type']]
            items = sum(team_near[0].get('items') or [])
            print(f"{mp:10} {mid[6:14]} {'W' if win else 'L'} r{R[k]['_h']['round']:4} {ch:8} items={items:2} camps={len(cs)} groupHP={ghp:5} groupStr={gstr:5.0f} rounds={fight:3} hp {start_hp:.0f}->{hp_min:.0f} / {maxhp:.0f}  lost={100*(start_hp-hp_min)/maxhp:.0f}%")
            agg[(len(cs), ghp)].append(((start_hp - hp_min) / maxhp, fight))
print()
for k, v in sorted(agg.items()):
    print('camps,hp', k, 'n', len(v), 'avg loss %.0f%%' % (100*sum(a for a, _ in v)/len(v)), 'max loss %.0f%%' % (100*max(a for a, _ in v)), 'avg rounds %.0f' % (sum(b for _, b in v)/len(v)))
