"""Per-team action rates: fraction of alive champion-rounds with a basic attack (kind 5), a cast
(kind 6) and a move (kind 4). usage: actrate.py json..."""
import json, sys, collections
tot = collections.Counter(); alive_rounds = collections.Counter()
for p in sys.argv[1:]:
    d = json.load(open(p)); R = d['rounds']
    team_of = {}
    for r in R[10:]:
        for c in r['champions']:
            team_of[c['entity']['index']] = c['team']
            if c.get('alive'): alive_rounds[c['team']] += 1
    seen = set()
    for e in d['events']:
        rnd, kind, ak, ai = e[0], e[1], e[2], e[3]
        if ak != 1 or rnd < 10: continue
        key = (p, rnd, ai, kind)
        if key in seen: continue
        seen.add(key)
        tot[(team_of.get(ai), kind)] += 1
for t in sorted(alive_rounds):
    a = alive_rounds[t]
    print(f'team {t}: alive champ-rounds {a}  attack {tot[(t,5)]/a:.2f}  cast {tot[(t,6)]/a:.2f}  move {tot[(t,4)]/a:.2f}  capture {tot[(t,2)]/a:.3f}')
