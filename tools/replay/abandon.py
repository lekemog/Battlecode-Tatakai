"""Count camp groups damaged then left alive for 20+ rounds (abandoned clears), per 100 rounds.
usage: abandon.py json..."""
import json, sys, os
TEAMF = int(os.environ.get("TEAM", "0"))
for p in sys.argv[1:]:
    d = json.load(open(p)); R = d['rounds']; ng = len(R[50]['groups'])
    started = {}; aband = 0; done = 0; who = {}
    pos = {}
    for r in R:
        for c in r['camps']:
            if c.get('position'): pos.setdefault(c['group'], set()).add((c['position']['x'], c['position']['y']))
    for t in range(10, len(R)):
        r = R[t]
        for gi in range(ng):
            cs = [c for c in r['camps'] if c['group'] == gi]
            if not cs: continue
            tot = sum(c['health'] for c in cs); mx = sum(c['maxHealth'] for c in cs)
            if 0 < tot < mx:
                if gi not in started:
                    near = [c['team'] for c in R[t]['champions'] if c.get('alive') and c.get('position') and any(max(abs(c['position']['x']-x),abs(c['position']['y']-y))<=4 for x,y in pos.get(gi,[]))]
                    started[gi] = [t, tot]; who[gi] = max(set(near), key=near.count) if near else -1
                elif tot < started[gi][1]: started[gi] = [t, tot]
                elif t - started[gi][0] >= 20:
                    if who.get(gi) == TEAMF: aband += 1
                    del started[gi]
            elif tot == 0 and gi in started:
                if who.get(gi) == TEAMF: done += 1
                del started[gi]
    print(f'{p.split("/")[-1][:12]} rounds {len(R)} clears {done} abandoned {aband} per100r {aband/len(R)*100:.2f}')
