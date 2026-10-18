"""Early-economy benchmark (issue #21): BOT vs OPP on every map in maps/, both sides.
Per game, for BOT's team: gold earned at r50/r100/r150, first purchase round, gold spent by r100,
tributed gems at r300 and the round it reached 1000 (2000 if it never did).
Portable (no /home/claude paths): run from the repo root.
usage: python tools/econ.py BOT [OPP=starter-cpp] [--jobs N] [--maps a,b]   -> prints a table and writes results/econ_BOT_vs_OPP.json"""
import json, os, subprocess, sys, tempfile, time, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and not sys.argv[i - 1].startswith('--')]
opt = {sys.argv[i][2:]: sys.argv[i + 1] for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith('--')}
BOT = args[0]; OPP = args[1] if len(args) > 1 else 'starter-cpp'
JOBS = opt.get('jobs', '4')
maps_dir = os.path.join(ROOT, 'maps')
MAPS = opt['maps'].split(',') if 'maps' in opt else sorted(f[:-7] for f in os.listdir(maps_dir) if f.endswith('.map26a'))

def at(runs, R):
    """Value of a run-length timeline at round R."""
    s = 0; v = 0
    for r in runs:
        if s > R: break
        v = float(r['value']); s += r['duration']
    return v

def first_above(runs, x):
    s = 0
    for r in runs:
        if float(r['value']) > x: return s
        s += r['duration']
    return None

def team_stats(d, team):
    ch = [c for c in d['championTimelines'] if c['owner'].get('team') == team]
    def tot(metric, R): return sum(at(c['runs'], R) for c in ch if c['metric'] == metric)
    buys = [first_above(c['runs'], 0) for c in ch if c['metric'] == 'spentGold']
    buys = [b for b in buys if b is not None]
    tl = [t for t in d['teamTimelines'] if t['owner'] == team and t['metric'] == 'submittedGems'][0]['runs']
    reach = first_above(tl, 999)
    return {'gold50': tot('earnedGold', 50), 'gold100': tot('earnedGold', 100), 'gold150': tot('earnedGold', 150),
            'first_buy': min(buys) if buys else None, 'spent100': tot('spentGold', 100),
            'gems300': at(tl, 300), 'to1000': reach if reach is not None else 2000}

def main():
    out = tempfile.mkdtemp(prefix=f'econ_{BOT}_')
    rows = []
    with open(os.path.join(out, 'manifest.txt'), 'w') as f:
        for m in MAPS:
            for side in (0, 1):
                a, b = (BOT, OPP) if side == 0 else (OPP, BOT)
                tag = f'{m}_{side}'; rows.append((m, side, tag))
                q = lambda p: '"' + p.replace('\\', '/') + '"'
                f.write(' '.join([q(os.path.join(ROOT, 'bots', a)), q(os.path.join(ROOT, 'bots', b)),
                                  q(os.path.join(maps_dir, m + '.map26a')), q(os.path.join(out, tag + '.repl26a')),
                                  '--statistics', q(os.path.join(out, tag + '.json')), '--json']) + '\n')
    t0 = time.time()
    subprocess.run(['cambc', 'run-batch', os.path.join(out, 'manifest.txt'), '--jobs', JOBS],
                   cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    res = []
    for m, side, tag in rows:
        p = os.path.join(out, tag + '.json')
        if not os.path.exists(p): print('missing', tag); continue
        d = json.load(open(p, encoding='utf-8'))
        me, them = ('teamA', 'teamB') if side == 0 else ('teamB', 'teamA')
        s = team_stats(d, me); s['opp'] = team_stats(d, them)
        s.update(map=m, side=side, win=d['match']['outcome'] == me)
        res.append(s)
        try: os.remove(os.path.join(out, tag + '.repl26a'))   # replays are large; keep only the stats
        except OSError: pass
    print(f'{BOT} vs {OPP}: {len(res)} games in {time.time() - t0:.0f}s')
    print(f"{'map':12} {'side':>4} {'win':>3} {'g50':>5} {'g100':>5} {'g150':>5} {'1stbuy':>6} {'spent100':>8} {'gems300':>7} {'to1000':>6}")
    for s in res:
        print(f"{s['map'][:12]:12} {s['side']:>4} {'W' if s['win'] else '-':>3} {s['gold50']:5.0f} {s['gold100']:5.0f} {s['gold150']:5.0f} "
              f"{str(s['first_buy']):>6} {s['spent100']:8.0f} {s['gems300']:7.0f} {s['to1000']:6}")
    def avg(k): v = [s[k] for s in res if s[k] is not None]; return st.mean(v) if v else float('nan')
    print(f"MEAN  wins {sum(s['win'] for s in res)}/{len(res)}  gold50 {avg('gold50'):.0f}  gold100 {avg('gold100'):.0f}  "
          f"gold150 {avg('gold150'):.0f}  first_buy {avg('first_buy'):.0f}  spent100 {avg('spent100'):.0f}  "
          f"gems300 {avg('gems300'):.0f}  to1000 {avg('to1000'):.0f}")
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, 'results', f'econ_{BOT}_vs_{OPP}.json'), 'w'), indent=1)

if __name__ == '__main__':
    main()
