"""Head-to-head on every map in a folder, both sides: CAND vs BASE. Portable (no /home/claude paths).
usage: python tools/headtohead.py CAND BASE MAPDIR [--jobs N] [--maps substr1,substr2]
Prints per-map results (CAND's gems, opponent's gems, winner) and totals; writes results/kurians/h2h_CAND_vs_BASE.json."""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and not sys.argv[i - 1].startswith('--')]
opt = {sys.argv[i][2:]: sys.argv[i + 1] for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith('--')}
CAND, BASE, MAPDIR = args[0], args[1], args[2]
JOBS = opt.get('jobs', '4')
maps = sorted(f[:-7] for f in os.listdir(MAPDIR) if f.endswith('.map26a'))
if 'maps' in opt: maps = [m for m in maps if any(s in m for s in opt['maps'].split(','))]

def main():
    out = tempfile.mkdtemp(prefix=f'h2h_{CAND}_')
    q = lambda p: '"' + p.replace('\\', '/') + '"'
    rows = []
    with open(os.path.join(out, 'm.txt'), 'w') as f:
        for m in maps:
            for side in (0, 1):
                a, b = (CAND, BASE) if side == 0 else (BASE, CAND)
                tag = f'{m}_{side}'; rows.append((m, side, tag))
                f.write(' '.join([q(os.path.join(ROOT, 'bots', a)), q(os.path.join(ROOT, 'bots', b)), q(os.path.join(MAPDIR, m + '.map26a')),
                                  q(os.path.join(out, tag + '.repl26a')), '--statistics', q(os.path.join(out, tag + '.json')), '--json']) + '\n')
    subprocess.run(['cambc', 'run-batch', os.path.join(out, 'm.txt'), '--jobs', JOBS], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    res = []
    for m, side, tag in rows:
        p = os.path.join(out, tag + '.json')
        if not os.path.exists(p): res.append({'map': m, 'side': side, 'missing': True}); continue
        d = json.load(open(p, encoding='utf-8'))
        me, them = ('teamA', 'teamB') if side == 0 else ('teamB', 'teamA')
        g = {t['team']: int(t['submittedGems']) for t in d['teams']}
        res.append({'map': m, 'side': side, 'cand': g[me], 'base': g[them], 'win': d['match']['outcome'] == me, 'rounds': d['match']['roundsStarted']})
        try: os.remove(os.path.join(out, tag + '.repl26a'))
        except OSError: pass
    ok = [r for r in res if not r.get('missing')]
    print(f'{CAND} vs {BASE}: {len(ok)} games on {len(maps)} maps')
    for m in maps:
        rr = [r for r in ok if r['map'] == m]
        print(f"  {m:24} " + '  '.join(f"{'W' if r['win'] else '-'} {r['cand']:>4}-{r['base']:<4}" for r in rr) + ('   <-- both lost' if rr and not any(r['win'] for r in rr) else ''))
    print(f"TOTAL {CAND} wins {sum(r['win'] for r in ok)}/{len(ok)}; mean gem margin {sum(r['cand'] - r['base'] for r in ok) / max(1, len(ok)):+.0f}"
          f"; missing {len(res) - len(ok)}")
    os.makedirs(os.path.join(ROOT, 'results', 'kurians'), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, 'results', 'kurians', f'h2h_{CAND}_vs_{BASE}.json'), 'w'), indent=1)

if __name__ == '__main__':
    main()
