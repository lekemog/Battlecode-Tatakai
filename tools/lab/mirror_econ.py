"""mirror_econ.py CAND BASE DIR : income and win share of CAND vs BASE from mirror.sh output (DIR = $PROJ/mirror_<CAND>_<BASE>).
Per game: team earned gold at rounds 100/200/400 (from championTimelines), compared candidate minus base; plus wins and gems banked."""
import collections, glob, json, os, statistics, sys
C, B, D = sys.argv[1:4]
def at(j, team, r):
    tot = 0.0
    for t in j['championTimelines']:
        if t['metric'] != 'earnedGold' or t['owner'].get('team') != team:
            continue
        s = []
        for run in t['runs']:
            s += [float(run['value'])] * int(run['duration'])
        tot += s[min(r, len(s) - 1)] if s else 0
    return tot
rows = collections.defaultdict(list); w = l = 0; sub = collections.defaultdict(list)
for f in glob.glob(os.path.join(D, '*.json')):
    if f.endswith('manifest.json'):
        continue
    try:
        j = json.load(open(f))
    except Exception:
        continue
    base = os.path.basename(f)[:-5]
    cs = 'teamA' if base.split('_', 1)[1].startswith(C + '_') else 'teamB'; bs = 'teamB' if cs == 'teamA' else 'teamA'
    o = j['match']['outcome']; w += o == cs; l += o == bs
    for r in (100, 200, 400):
        a, b = at(j, cs, r), at(j, bs, r)
        if a or b:
            rows[r].append((a, b))
    for t in j['teams']:
        sub[t['team']].append(int(t['submittedGems']))
n = w + l
print(f'{C} vs {B}: games {n}  wins {w} ({w / max(1, n):.1%})')
for r in (100, 200, 400):
    a = statistics.mean(x for x, _ in rows[r]); b = statistics.mean(y for _, y in rows[r])
    print(f'  earned gold by round {r}:  cand {a:6.0f}  base {b:6.0f}  ({100 * (a - b) / b:+.1f}%)  cand ahead in {sum(1 for x, y in rows[r] if x > y)}/{len(rows[r])} games')
