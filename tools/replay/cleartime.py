"""Clear time per camp group: rounds from first damage to all camps dead, champions involved,
and their summed damage stats. usage: cleartime.py json... (team filter optional via TEAM env)"""
import json, sys, os, statistics as st, collections
TEAM = os.environ.get('TEAM')
out = collections.defaultdict(list)
for p in sys.argv[1:]:
    d = json.load(open(p)); R = d['rounds']
    ng = len(R[50]['groups'])
    start = {}
    for t in range(10, len(R)):
        r = R[t]
        for gi in range(ng):
            cs = [c for c in r['camps'] if c['group'] == gi]
            if not cs: continue
            tot = sum(c['health'] for c in cs); mx = sum(c['maxHealth'] for c in cs)
            if gi not in start and 0 < tot < mx: start[gi] = (t, mx)
            if gi in start and tot == 0:
                t0, mx0 = start.pop(gi)
                # who was near at the end (within 4 of any camp of the group, using known camp positions)
                st_ = r['groups'][gi]
                team = st_.get('captureTeam')
                if TEAM is not None and str(team) != TEAM: continue
                out[mx0].append(t - t0)
for mx, v in sorted(out.items()):
    print(f'group HP {mx:6}: n={len(v):3} median clear {st.median(v):5.1f} rounds  mean {st.mean(v):5.1f}')
