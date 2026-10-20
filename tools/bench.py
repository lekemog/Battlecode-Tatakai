"""Benchmark bots on the full map pool: wins vs each opponent and mean rounds-to-finish when winning on gems."""
import json, os, subprocess, sys, time, statistics, shutil

PROJ = '/home/claude/proj'
MAPS = (os.environ.get('MAPS') or open('/home/claude/tools/pool.txt').read().strip()).split(',')


def run(a, b):
    out = f'/home/claude/data/bench_{a}_vs_{b}_{int(time.time()*1000)}'
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
                    '--timeout', '900', '--log-limit', '0'], cwd=PROJ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wins, speed, per_map, margins = 0, [], {}, []
    for m, first, second, tag in rows:
        p = f'{out}/{tag}.json'
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
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
