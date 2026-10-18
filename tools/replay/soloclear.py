"""Solo clears: a group cleared while exactly one champion (of the capturing side) stayed within 4.
Reports per champion type: clear rounds, HP lost (fraction), deaths during clear.
usage: soloclear.py TEAM json..."""
import json, sys, collections, statistics as st
CH = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi']
team = None if sys.argv[1] == 'any' else int(sys.argv[1])
res = collections.defaultdict(list)
for p in sys.argv[2:]:
    d = json.load(open(p)); R = d['rounds']; ng = len(R[50]['groups'])
    pos = collections.defaultdict(set)
    for r in R:
        for c in r['camps']:
            if c.get('position'): pos[c['group']].add((c['position']['x'], c['position']['y']))
    def near(r, gi):
        return [c for c in r['champions'] if c.get('alive') and c.get('position') and any(max(abs(c['position']['x'] - x), abs(c['position']['y'] - y)) <= 4 for x, y in pos[gi])]
    active = {}
    for t in range(10, len(R)):
        r = R[t]
        for gi in range(ng):
            cs = [c for c in r['camps'] if c['group'] == gi]
            if not cs: continue
            tot = sum(c['health'] for c in cs); mx = sum(c['maxHealth'] for c in cs)
            nb = near(r, gi)
            if 0 < tot < mx:
                if gi not in active: active[gi] = {'t0': t, 'who': set(), 'hp0': {}, 'mx': mx}
                for c in nb:
                    active[gi]['who'].add(c['entity']['index'])
                    active[gi]['hp0'].setdefault(c['entity']['index'], (c['health'], c['maxHealth'], c['team'], c['type']))
            elif tot == 0 and gi in active:
                a = active.pop(gi)
                if len(a['who']) != 1: continue
                i = next(iter(a['who'])); h0, mh, tm, ty = a['hp0'][i]
                if team is not None and tm != team: continue
                c = next((c for c in R[t]['champions'] if c['entity']['index'] == i), None)
                h1 = c['health'] if c and c.get('alive') else 0
                res[(CH[ty], a['mx'])].append((t - a['t0'], (h0 - h1) / mh, 0 if (c and c.get('alive')) else 1))
for k, v in sorted(res.items()):
    print(f'{k[0]:9} grpHP {k[1]:5}: n={len(v):3} clear {st.median(x[0] for x in v):5.1f}r  hp lost {st.mean(x[1] for x in v):.2f}  died {sum(x[2] for x in v)}')
