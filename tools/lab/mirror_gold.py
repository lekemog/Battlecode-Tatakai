"""mirror_gold.py CAND BASE : earned gold at rounds 50/100/200/300 and deaths before r300, candidate / base, from $PROJ=~/lab mirror_<CAND>_<BASE>."""
import json, glob, os, sys, collections
cand, base = sys.argv[1], sys.argv[2]
acc = collections.defaultdict(float); n = 0
def at(tl, r):
    s = []
    for run in tl['runs']: s += [float(run['value'])] * int(run['duration'])
    return s[min(r, len(s) - 1)] if s else 0.0
for f in glob.glob(f'/root/lab/mirror_{cand}_{base}/*.json'):
    if f.endswith('manifest.json'): continue
    j = json.load(open(f)); n += 1
    cs = 'teamA' if os.path.basename(f).endswith(f'_{cand}_{base}.json') else 'teamB'
    for tl in j['championTimelines']:
        if tl['metric'] != 'earnedGold': continue
        side = 'cand' if tl['owner'].get('team') == cs else 'base'
        for r in (50, 100, 200, 300): acc[(side, r)] += at(tl, r)
    for e in j['events']:
        if e['kind'] != 'death': continue
        side = 'cand' if e.get('owner', {}).get('team') == cs else 'base'
        acc[(side, 'd300')] += sum(1 for en in e['entries'] if en['timestamp']['round'] < 300)
n = max(1, n)
print(' '.join(f"gold{r} {acc[('cand', r)] / n:.0f}/{acc[('base', r)] / n:.0f}" for r in (50, 100, 200, 300)),
      f"deaths<300 {acc[('cand', 'd300')] / n:.2f}/{acc[('base', 'd300')] / n:.2f}")
