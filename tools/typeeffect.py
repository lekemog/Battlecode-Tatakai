"""Per-opponent-type effect of each tested strategy switch, from paired scrims.
For each (opponent, map) played by both arms, classify the situation at round 200 from the
baseline game (same features/centroids as the bot) and record candidate minus baseline margin."""
import json, os, sys, collections
sys.argv += []
exec(open('/home/claude/tools/oppfeat.py').read().split('def main():')[0])
C = json.load(open('/home/claude/data/clusters.json'))
NAMES = ['even race', 'brawl', 'we ahead', 'out-farmed']
def ctype(f):
    ts = 5 if f['W'] * f['H'] >= 2400 else 4
    x = [(f['e200'] - f['o200']) / (f['e200'] + f['o200'] + 50), f['d200'] / ts]
    z = [(x[i] - C['mu'][i]) / C['sd'][i] for i in range(2)]
    return min(range(4), key=lambda c: sum((z[i] - C['centers'][c][i]) ** 2 for i in range(2)))
GC = json.load(open('/home/claude/data/ab/groupcache.json'))
games = {}
for g, v in GC.items():
    for mm in v['matches']:
        p = f"/home/claude/data/ladder/{mm['matchId']}.json"
        if not os.path.exists(p): continue
        side = 'team' + mm['side'].upper()
        try:
            r = rows(p, lambda t: 'US' if t == side else None, {'map': mm['map']})
        except Exception:
            continue
        if r: games[(v['tag'], v['opp'], mm['map'])] = r[0]
PAIRS = [('w8_v12f', 'w8_v12c', 'cautious'), ('w9_v12f', 'w9_v12c', 'cautious'), ('w10_v12h', 'w10_v12c', 'shop sooner'),
         ('w11_v12l', 'w11_v12c', 'solo farming'), ('w12_v13a', 'w12_v12m', 'race chase/protect'), ('w13_v13b', 'w13_v12m', 'type model')]
for a, b, name in PAIRS:
    eff = collections.defaultdict(list)
    for (tag, opp, mp), fb in games.items():
        if tag != b: continue
        fa = games.get((a, opp, mp))
        if not fa: continue
        eff[ctype(fb)].append(fa['margin'] - fb['margin'])
    if not eff: continue
    print(f'{name:20} ({a} vs {b})')
    for c in range(4):
        v = eff.get(c, [])
        if v: print(f'   {NAMES[c]:11} n={len(v):2}  mean diff {sum(v)/len(v):+7.0f}  better/worse {sum(x>0 for x in v)}/{sum(x<0 for x in v)}')
