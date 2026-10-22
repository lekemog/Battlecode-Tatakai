"""Early opponent-style signals: can a bot tell opponent styles apart by round 60/100?
Plays BOT against each style bot on every map (both sides) and reports, from BOT's side, signals a
champion can sense in-game: damage taken from enemy champions, our deaths, kills we make, and the
opponent's tributed gems (global). Portable; run from the repo root.
usage: python tools/oppstyle.py BOT [styles=fz_hunt,fz_solo,fz_herd] [--jobs N] [--maps a,b]
-> per-style summary at r60/r100 + results/oppstyle_BOT.json"""
import json, os, subprocess, sys, tempfile, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and not sys.argv[i - 1].startswith('--')]
opt = {sys.argv[i][2:]: sys.argv[i + 1] for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith('--')}
BOT = args[0]; STYLES = (args[1] if len(args) > 1 else 'fz_hunt,fz_solo,fz_herd').split(',')
JOBS = opt.get('jobs', '4'); ROUNDS = (60, 100, 150)
maps_dir = os.path.join(ROOT, 'maps')
MAPS = opt['maps'].split(',') if 'maps' in opt else sorted(f[:-7] for f in os.listdir(maps_dir) if f.endswith('.map26a'))

def at(runs, R):
    s = 0; v = 0
    for r in runs:
        if s > R: break
        v = float(r['value']); s += r['duration']
    return v

def signals(d, me, them):
    def tot(team, metric, R): return sum(at(c['runs'], R) for c in d['championTimelines'] if c['owner'].get('team') == team and c['metric'] == metric)
    their_bank = [t for t in d['teamTimelines'] if t['owner'] == them][0]['runs']
    out = {}
    for R in ROUNDS:
        out[R] = {'dmg_from_champs': tot(me, 'championDamageTaken', R), 'our_deaths': tot(me, 'deaths', R),
                  'our_kills': tot(me, 'kills', R), 'their_banked': at(their_bank, R)}
    return out

def main():
    out = tempfile.mkdtemp(prefix=f'oppstyle_{BOT}_')
    q = lambda p: '"' + p.replace('\\', '/') + '"'
    rows = []
    with open(os.path.join(out, 'manifest.txt'), 'w') as f:
        for sty in STYLES:
            for m in MAPS:
                for side in (0, 1):
                    a, b = (BOT, sty) if side == 0 else (sty, BOT)
                    tag = f'{sty}_{m}_{side}'; rows.append((sty, m, side, tag))
                    f.write(' '.join([q(os.path.join(ROOT, 'bots', a)), q(os.path.join(ROOT, 'bots', b)),
                                      q(os.path.join(maps_dir, m + '.map26a')), q(os.path.join(out, tag + '.repl26a')),
                                      '--statistics', q(os.path.join(out, tag + '.json')), '--json']) + '\n')
    subprocess.run(['cambc', 'run-batch', os.path.join(out, 'manifest.txt'), '--jobs', JOBS],
                   cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    res = []
    for sty, m, side, tag in rows:
        p = os.path.join(out, tag + '.json')
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding='utf-8'))
        me, them = ('teamA', 'teamB') if side == 0 else ('teamB', 'teamA')
        res.append({'style': sty, 'map': m, 'side': side, 'win': d['match']['outcome'] == me, 'sig': signals(d, me, them)})
        try: os.remove(os.path.join(out, tag + '.repl26a'))
        except OSError: pass
    keys = ('dmg_from_champs', 'our_deaths', 'our_kills', 'their_banked')
    for R in ROUNDS:
        print(f'--- by round {R} (mean, and share of games with any champion damage) ---')
        print(f"{'style':10}" + ''.join(f'{k:>17}' for k in keys) + f"{'any dmg':>9}")
        for sty in STYLES:
            g = [r['sig'][R] for r in res if r['style'] == sty]
            if not g: continue
            print(f'{sty:10}' + ''.join(f'{st.mean(x[k] for x in g):17.1f}' for k in keys) + f"{sum(x['dmg_from_champs'] > 0 for x in g) / len(g):9.0%}")
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    json.dump(res, open(os.path.join(ROOT, 'results', f'oppstyle_{BOT}.json'), 'w'), indent=1)

if __name__ == '__main__':
    main()
