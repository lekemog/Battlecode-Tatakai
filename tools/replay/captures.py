"""Per-capture detail: champions present, camp group size, gems gained. usage: captures.py <json_dir>"""
import json, glob, os, sys, math, collections

CH = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HeartOfRuin']
J = sys.argv[1]
maps = json.load(open(os.path.join(J, 'maps.json')))
summary = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(J, 'match-*.json'))):
    mid = os.path.basename(p)[:-5]
    d = json.load(open(p))
    R = d['rounds']
    h = R[-1]['_h']
    grp_camps = collections.defaultdict(list)
    seen = set()
    for r in R:
        for c in r['camps']:
            i = c['entity']['index']
            if i in seen or not c.get('position'): continue
            seen.add(i)
            grp_camps[c['group']].append((c['position']['x'], c['position']['y'], c['maxHealth']))
    prevg, prevr = None, None
    per = {0: [], 1: []}
    for r in R:
        g = r['groups']
        if prevg and len(prevg) == len(g):
            for gi, (a, b) in enumerate(zip(prevg, g)):
                if a['state'] == 2 and b['state'] == 3:
                    t = a['captureTeam']
                    if t not in (0, 1): continue
                    cs = grp_camps[gi]
                    near = [c for c in prevr['champions'] if c['team'] == t and c.get('alive') and c.get('position')
                            and min(math.dist((c['position']['x'], c['position']['y']), (x, y)) for x, y, _ in cs) <= 4]
                    gain = 0
                    for c in r['champions']:
                        if c['team'] != t: continue
                        pc = next(q for q in prevr['champions'] if q['entity']['index'] == c['entity']['index'])
                        gain += max(0, (c.get('gems') or 0) - (pc.get('gems') or 0))
                    per[t].append((r['_h']['round'], len(near), len(cs), int(sum(hp for *_, hp in cs)), gain,
                                   '+'.join(CH[c['type']][:3] for c in near)))
        prevg, prevr = g, r
    for t in (0, 1):
        win = h['outcome'] == t + 1
        L = per[t]
        early = [x for x in L if x[0] <= 200]
        print(f"{maps[mid][0]:11} {mid[6:14]} T{t} {'W' if win else 'L'} caps={len(L):3} early={len(early):2} "
              f"avgChamps={sum(x[1] for x in L)/max(1,len(L)):.1f} soloShare={sum(1 for x in L if x[1]<=1)/max(1,len(L)):.2f} "
              f"gems/cap={sum(x[4] for x in L)/max(1,len(L)):.1f}")
        print('     ', ' '.join(f"{x[0]}:{x[1]}c/{x[2]}camp/{x[3]}hp/+{x[4]}g[{x[5]}]" for x in early[:12]))
        summary['W' if win else 'L'].append((len(L), sum(x[1] for x in L) / max(1, len(L)), sum(1 for x in L if x[1] <= 1) / max(1, len(L))))
for k, v in summary.items():
    print(k, 'n', len(v), 'caps', sum(a for a, _, _ in v) / len(v), 'avgChamps', sum(b for _, b, _ in v) / len(v), 'solo', sum(c for *_, c in v) / len(v))
