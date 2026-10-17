"""Pick 5 fresh top-100 opponents (never used before) for one A/B round.
usage: mkopps.py OUTFILE   -> writes [[teamId, maps], ...] and records them as used."""
import json, random, sys, os
POOL = json.load(open('/home/claude/data/ab/top100_pool.json'))
USED_F = '/home/claude/data/ab/top100_used.json'
used = set(json.load(open(USED_F))) if os.path.exists(USED_F) else set()
MAPS = ['rows', 'corners', 'lanes', 'swirl', 'monolith', 'fragment', 'packs', 'collision', 'expanse', 'rushbait_v2',
        'stampede', 'pilgrimage', 'elkring', 'interlock', 'eight', 'contest', 'ambush']
rnd = random.Random(len(used))
bands = [(21, 40, 1), (41, 70, 2), (71, 100, 2)]
pick = []
for lo, hi, n in bands:
    cand = [p for p in POOL if lo <= p[0] <= hi and p[1] not in used]
    rnd.shuffle(cand)
    pick += cand[:n]
off = (len(used) * 5) % 17
out = []
for i, (rank, tid, name) in enumerate(pick):
    maps = [MAPS[(off + i * 5 + k) % 17] for k in range(5)]
    out.append([tid, ','.join(maps)])
    used.add(tid)
    print(rank, name, ','.join(maps))
json.dump(out, open(sys.argv[1], 'w'))
json.dump(sorted(used), open(USED_F, 'w'))
