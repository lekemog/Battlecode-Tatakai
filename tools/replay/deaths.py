"""Context of each death: round, gems carried, allies/enemies within 5, half of map. usage: deaths.py <json_dir>"""
import json, glob, os, sys, math, collections
CH = ['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HeartOfRuin']
J = sys.argv[1]
maps = json.load(open(os.path.join(J, 'maps.json')))
tot = collections.defaultdict(collections.Counter)
for p in sorted(glob.glob(os.path.join(J, 'match-*.json'))):
    mid = os.path.basename(p)[:-5]; mp = maps[mid][0]
    d = json.load(open(p)); R = d['rounds']; h = R[-1]['_h']
    # spawn centroid per team from round where all alive first
    spawn = {}
    for r in R:
        for t in (0, 1):
            ps = [c['position'] for c in r['champions'] if c['team'] == t and c.get('position')]
            if ps and t not in spawn: spawn[t] = (sum(q['x'] for q in ps)/len(ps), sum(q['y'] for q in ps)/len(ps))
        if len(spawn) == 2: break
    for k in range(1, len(R)):
        for c in R[k]['champions']:
            pc = next((q for q in R[k-1]["champions"] if q["entity"]["index"] == c["entity"]["index"]), None)
            if pc is None: continue
            if not (pc.get('alive') and not c.get('alive')): continue
            t = c['team']; pos = pc.get('position')
            if not pos: continue
            P = (pos['x'], pos['y'])
            al = sum(1 for q in R[k-1]['champions'] if q['team'] == t and q.get('alive') and q.get('position') and q is not pc and math.dist(P, (q['position']['x'], q['position']['y'])) <= 5)
            en = sum(1 for q in R[k-1]['champions'] if q['team'] != t and q.get('alive') and q.get('position') and math.dist(P, (q['position']['x'], q['position']['y'])) <= 5)
            own = math.dist(P, spawn[t]) < math.dist(P, spawn[1-t])
            win = 'W' if h['outcome'] == t + 1 else 'L'
            key = win
            tot[key]['deaths'] += 1
            tot[key]['gems_lost'] += pc.get('gems') or 0
            tot[key]['own_half' if own else 'enemy_half'] += 1
            tot[key]['outnumbered' if en > al + 1 else 'even_or_better'] += 1
            tot[key]['alone' if al == 0 else 'with_ally'] += 1
            tot[key]['by_camp' if en == 0 else 'by_enemy'] += 1
            tot[key]['early<150' if R[k]['_h']['round'] < 150 else 'late'] += 1
for k, v in tot.items(): print(k, dict(v))
