"""Benchmark one bot against one opponent on the map pool, both sides. Keeps per-game aggregates (kills, deaths, gems, gold at r200/r400,
camp clears, engine error codes) in the per-game JSON so tools/lab/stats.py can summarise them. Usage: PROJ=<cambc project> python3 -I bench_stats.py BOT OPP"""
import json, os, subprocess, sys, time, statistics, shutil

PROJ = os.environ.get('PROJ') or os.getcwd()
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# MAPS = comma-separated map names; default: the 40 old-pool maps in bench/pool6.txt. MAPLIST = file with one map name per line (e.g. all 70).
if os.environ.get('MAPS'):
    MAPS = os.environ['MAPS'].split(',')
elif os.environ.get('MAPLIST'):
    MAPS = [x.strip() for x in open(os.environ['MAPLIST']) if x.strip()]
else:
    MAPS = open(os.path.join(_REPO, 'bench', 'pool6.txt')).read().strip().split(',')


def run(a, b):
    out = os.path.join(os.environ.get('BENCH_OUT', os.path.join(PROJ, 'bench_out')), f'bench_{a}_vs_{b}_{int(time.time()*1000)}')
    os.makedirs(out, exist_ok=True)
    rows = []
    with open(f'{out}/manifest.txt', 'w') as f:
        for m in MAPS:
            for first, second in ((a, b), (b, a)):
                tag = f'{m}_{first}_{second}'
                rows.append((m, first, second, tag))
                f.write(f'{PROJ}/bots/{first} {PROJ}/bots/{second} {PROJ}/maps/{m}.map26a {out}/{tag}.repl26a '
                        f'--statistics {out}/{tag}.json --json\n')
    subprocess.run(['cambc', 'run-batch', f'{out}/manifest.txt', '--jobs', os.environ.get('JOBS','2'), '--release', '--json',
                    '--timeout', '900', '--log-limit', '600000'], cwd=PROJ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wins, speed, per_map, margins = 0, [], {}, []
    for m, first, second, tag in rows:
        p = f'{out}/{tag}.json'
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        if os.path.getsize(p) > 20000:   # 3.0 statistics carry full timelines (~1.5 MB): keep only what we read
            agg = {}
            for c in d.get('champions', []):
                mt = c.get('metrics', {}); x = agg.setdefault(c['team'], {})
                for k in ('kills', 'deaths', 'collectedGems', 'submittedGems', 'earnedGold', 'championDamageDone', 'monsterDamageDone'):
                    x[k] = x.get(k, 0) + float(mt.get(k, 0))
            def _at(runs, r):
                t = 0; v = 0.0
                for x in runs:
                    if t + x['duration'] > r: return float(x['value'])
                    t += x['duration']; v = float(x['value'])
                return v
            for c in d.get('championTimelines', []):
                if c.get('metric') == 'earnedGold':
                    x = agg.setdefault(c['owner']['team'], {})
                    x['gold200'] = x.get('gold200', 0) + _at(c['runs'], 200)
                    x['gold400'] = x.get('gold400', 0) + _at(c['runs'], 400)
            for e in d.get('events', []):
                if e.get('kind') == 'campClear':
                    x = agg.setdefault(e['owner'].get('team'), {})
                    x['campClears'] = x.get('campClears', 0) + len(e.get('entries', []))
            errs = {}
            try:
                import zipfile, re as _re, collections as _c
                z = zipfile.ZipFile(f'{out}/{tag}.repl26a')
                raw = z.read('team-a.stdout' if first == a else 'team-b.stdout').decode('utf-8', 'replace')
                errs = dict(_c.Counter(_re.findall(r'engine error (\d+)', raw)))
            except Exception:
                errs = {'_nolog': 1}
            json.dump({'match': d['match'], 'teams': [{'team': t['team'], 'submittedGems': t['submittedGems']} for t in d['teams']], 'agg': agg, 'errs': errs}, open(p, 'w'))
        side = 'teamA' if first == a else 'teamB'
        won = d['match']['outcome'] == side
        gems = {t['team']: int(t['submittedGems']) for t in d['teams']}
        rounds = d['match']['roundsStarted']
        wins += won
        other = 'teamB' if side == 'teamA' else 'teamA'
        margins.append(gems[side] - gems[other])
        if won and gems[side] >= 1000:
            speed.append(rounds)
        per_map.setdefault(m, []).append(('W' if won else 'L') + str(rounds))
    for f in os.listdir(out):   # 3.0 writes replay bundles under other names too: keep only stats/manifest
        p = os.path.join(out, f)
        if not f.endswith(('.json', '.txt')):
            try:
                (shutil.rmtree if os.path.isdir(p) else os.remove)(p)
            except OSError: pass
    for m, first, second, tag in rows:   # replays are large; stats JSON is kept
        try: os.remove(f'{out}/{tag}.repl26a')
        except OSError: pass
    return wins, len(rows), speed, per_map, (statistics.mean(margins) if margins else 0)


def main():
    bot = sys.argv[1]
    opps = sys.argv[2].split(',') if len(sys.argv) > 2 else ['v1', 'hunter', 'polaris_v3']
    total = 0; tm = 0
    for o in opps:
        w, n, speed, per_map, margin = run(bot, o)
        total += w; tm += margin
        sp = f'{statistics.mean(speed):.0f}' if speed else '-'
        print(f'{bot} vs {o}: {w}/{n}  margin {margin:+.0f}  mean rounds to 1000 when winning: {sp}', flush=True)
        if '-v' in sys.argv:
            for m, r in per_map.items():
                print('   ', m, ' '.join(r))
    print(f'{bot} TOTAL {total}  margin {tm/len(opps):+.0f}')


if __name__ == '__main__':
    main()
