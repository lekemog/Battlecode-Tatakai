"""#45: summarise a paired the_pack batch (cambc run-batch --statistics --json).

usage: python3 -I tools/replay/pack45.py <dir>
Files are named <bot>__<opponent>__<A|B>.json (A = our bot is teamA).
Prints per bot: wins, banked gems (ours/theirs), zero-deposit games, and per-game rows."""
import json, os, sys, collections

d = sys.argv[1]
rows = collections.defaultdict(list)
for f in sorted(os.listdir(d)):
    if not f.endswith('.json') or f.count('__') != 2:
        continue
    bot, opp, side = f[:-5].split('__')
    j = json.load(open(os.path.join(d, f)))
    me = 'teamA' if side == 'A' else 'teamB'
    gems = {t['team']: int(t['submittedGems']) for t in j['teams']}
    them = 'teamB' if me == 'teamA' else 'teamA'
    rows[bot].append((opp, side, j['match']['outcome'] == me, gems[me], gems[them], j['match']['roundsStarted']))

for bot, rs in rows.items():
    wins = sum(r[2] for r in rs)
    zero = sum(1 for r in rs if r[3] == 0)
    print(f'{bot}: games {len(rs)}  wins {wins}  banked us {sum(r[3] for r in rs)} / them {sum(r[4] for r in rs)}  zero-deposit {zero}')
    for side in 'AB':
        s = [r for r in rs if r[1] == side]
        if s:
            print(f'   side {side}: wins {sum(r[2] for r in s)}/{len(s)}  banked {sum(r[3] for r in s)}  zero-deposit {sum(1 for r in s if r[3] == 0)}')
    for r in rs:
        print(f'     {r[0]:10s} {r[1]}  {"W" if r[2] else "L"}  us {r[3]:5d}  them {r[4]:5d}  rounds {r[5]}')
