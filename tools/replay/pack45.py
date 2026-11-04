"""#45: summarise a paired the_pack batch (cambc run-batch --statistics --json).

usage: python3 -I tools/replay/pack45.py <dir> [-v]
Files are named <bot>__<opponent>__<A|B>.json (A = our bot is teamA).
Prints per bot: wins, banked gems (ours/theirs), zero-deposit games, first deposit round,
deaths and gems lost split by killer (camp vs champion); -v adds per-game rows."""
import json, os, sys, collections, statistics

d = sys.argv[1]
verbose = '-v' in sys.argv
rows = collections.defaultdict(list)
for f in sorted(os.listdir(d)):
    if not f.endswith('.json') or f.count('__') != 2:
        continue
    bot, opp, side = f[:-5].split('__')
    j = json.load(open(os.path.join(d, f)))
    me = 'teamA' if side == 'A' else 'teamB'
    them = 'teamB' if me == 'teamA' else 'teamA'
    gems = {t['team']: int(t['submittedGems']) for t in j['teams']}
    deaths = lost_camp = lost_champ = 0
    first_dep = None
    for e in j.get('events', []):
        if e.get('owner', {}).get('team') != me:
            continue
        for x in e.get('entries', []):
            r = x['timestamp']['round']
            if e['kind'] == 'death':
                deaths += 1
            elif e['kind'] == 'gemLoss':
                v = int(float(x['value']))
                if x.get('context') == 'camp':
                    lost_camp += v
                else:
                    lost_champ += v
            elif e['kind'] == 'gemSubmission' and int(float(x['value'])) > 0:
                first_dep = r if first_dep is None else min(first_dep, r)
    rows[bot].append(dict(opp=opp, side=side, win=j['match']['outcome'] == me, us=gems[me], them=gems[them],
                          rounds=j['match']['roundsStarted'], deaths=deaths, lost_camp=lost_camp, lost_champ=lost_champ, first=first_dep))

for bot, rs in rows.items():
    firsts = [r['first'] for r in rs if r['first'] is not None]
    print(f"{bot}: games {len(rs)}  wins {sum(r['win'] for r in rs)}  banked us {sum(r['us'] for r in rs)} / them {sum(r['them'] for r in rs)}"
          f"  zero-deposit {sum(1 for r in rs if r['us'] == 0)}  first deposit median {statistics.median(firsts) if firsts else '-'}"
          f" (after r700: {sum(1 for r in rs if r['first'] is None or r['first'] > 700)})"
          f"  deaths {sum(r['deaths'] for r in rs)}  gems lost to camps {sum(r['lost_camp'] for r in rs)} / to champions {sum(r['lost_champ'] for r in rs)}")
    for side in 'AB':
        s = [r for r in rs if r['side'] == side]
        if s:
            print(f"   side {side}: wins {sum(r['win'] for r in s)}/{len(s)}  banked {sum(r['us'] for r in s)}  zero-deposit {sum(1 for r in s if r['us'] == 0)}")
    if verbose:
        for r in rs:
            print(f"     {r['opp']:12s} {r['side']}  {'W' if r['win'] else 'L'}  us {r['us']:5d}  them {r['them']:5d}  rounds {r['rounds']}"
                  f"  first {r['first']}  deaths {r['deaths']}  lost camp {r['lost_camp']} champ {r['lost_champ']}")
