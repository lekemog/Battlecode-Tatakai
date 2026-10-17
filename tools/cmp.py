import json, statistics, collections, sys
rows = json.load(open('/home/claude/data/feat.json'))
def grp(r):
    if r['label'] == 'US': return 'US'
    if r['label'] == 'OPP': return 'OPP(vs us)'
    rk = int(r['label'][3:])
    return 'TOP1-10' if rk <= 10 else 'TOP11-50'
G = collections.defaultdict(list)
for r in rows: G[grp(r)].append(r)
keys = ['win', 'rounds', 'gems', 'g200', 'g400', 'first_score', 'first_buy', 'gold100', 'gold200', 'gold', 'deaths', 'kills', 'kills_early',
        'lost_gems', 'gems_from_kills', 'n_sub', 'avg_sub', 'camp_clears', 'big_camps', 'top_share', 'wards', 'locks', 'tps', 'champ_dmg', 'mon_dmg']
def mean(v):
    v = [x for x in v if x is not None]
    return statistics.mean(v) if v else float('nan')
print(f"{'metric':16}" + ''.join(f'{g:>13}' for g in G))
print(f"{'n':16}" + ''.join(f'{len(v):>13}' for v in G.values()))
for k in keys:
    print(f'{k:16}' + ''.join(f'{mean([float(r[k]) if r[k] is not None else None for r in v]):>13.2f}' for v in G.values()))
# first emblem family share
for g, v in G.items():
    c = collections.Counter();
    for r in v:
        for e in r['emblems'][:3]: c[e.split(' Emblem')[0]] += 1
    tot = sum(c.values()) or 1
    print(g, 'first-3 emblem families:', {k: round(n / tot, 2) for k, n in c.most_common()})
