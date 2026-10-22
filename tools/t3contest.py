"""T3 (#40) contest A/B: each BOT plays the same opponents on one map from both sides; decodes and compares deaths
(total, while recalling, by r600), gold earned (contest's tiebreak) and results. Portable.
usage: python tools/t3contest.py MAPFILE BOT_A,BOT_B OPP1,OPP2,... [--jobs N]"""
import glob, json, os, subprocess, sys, tempfile, zipfile, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_argv = sys.argv; sys.argv = ['t3analyse', '.', 'contest', '600']   # t3analyse reads its own CLI arguments at import
import t3analyse as T
sys.argv = _argv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and not sys.argv[i - 1].startswith('--')]
opt = {sys.argv[i][2:]: sys.argv[i + 1] for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith('--')}
MAP, BOTS, OPPS = args[0], args[1].split(','), args[2].split(',')

def assets():
    c = [d for d in glob.glob(os.path.join(os.environ['LOCALAPPDATA'], 'cambc', 'assets', '*', 'visualiser', 'assets'))
         if glob.glob(os.path.join(d, 'v1_0_2-*.wasm'))]
    return max(c, key=os.path.getmtime)

def main():
    out = tempfile.mkdtemp(prefix='t3contest_'); q = lambda p: '"' + p.replace('\\', '/') + '"'; games = []
    with open(os.path.join(out, 'm.txt'), 'w') as f:
        for bot in BOTS:
            for opp in OPPS + [b for b in BOTS if b != bot]:
                for side in (0, 1):
                    a, b = (bot, opp) if side == 0 else (opp, bot)
                    tag = f'{bot}__{opp}__{side}'; games.append((bot, opp, side, tag))
                    f.write(' '.join([q(os.path.join(ROOT, 'bots', a)), q(os.path.join(ROOT, 'bots', b)), q(MAP), q(os.path.join(out, tag + '.repl26a'))]) + '\n')
    subprocess.run(['cambc', 'run-batch', os.path.join(out, 'm.txt'), '--jobs', opt.get('jobs', '4')], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    A = assets(); res = {}
    for bot, opp, side, tag in games:
        rp = os.path.join(out, tag + '.repl26a'); js = os.path.join(out, tag + '.json')
        if not os.path.exists(rp): continue
        with zipfile.ZipFile(rp) as z: open(os.path.join(out, tag + '.raw'), 'wb').write(z.read('replay.repl26a'))
        subprocess.run(['node', os.path.join(ROOT, 'tools', 'replay', 'extract3.mjs'), A, os.path.join(out, tag + '.raw'), js], capture_output=True)
        if not os.path.exists(js): continue
        d = json.load(open(js, encoding='utf-8')); R = T.by_round(d); L = R[max(R)]
        T.UPTO = 2000; m = T.team_metrics(d, side); T.UPTO = 600; m6 = T.team_metrics(d, side)
        gold = sum(c['earnedGold'] for c in L['champions'] if c['team'] == side); ogold = sum(c['earnedGold'] for c in L['champions'] if c['team'] != side)
        # Winner from the rules (tributed gems, then lifetime gold earned); the snapshot's 'outcome' code is not 0/1 by side.
        g, og = L['submittedGems'][side], L['submittedGems'][1 - side]
        win = g > og or (g == og and gold > ogold)
        res.setdefault(bot, []).append(dict(opp=opp, side=side, win=bool(win), deaths=m['deaths'], recall=m['recall'], d600=m6['deaths'], gold=gold, ogold=ogold,
                                            gems=L['submittedGems'][side], ogems=L['submittedGems'][1 - side]))
        for ext in ('.repl26a', '.raw', '.json'):
            try: os.remove(os.path.join(out, tag + ext))
            except OSError: pass
    for bot in BOTS:
        rs = res.get(bot, [])
        for r in rs:
            print(f"{bot:26} vs {r['opp']:26} side {r['side']} {'WIN ' if r['win'] else 'loss'} gems {r['gems']:>4}-{r['ogems']:<4} gold {r['gold']:>5}-{r['ogold']:<5} deaths {r['deaths']:>3} (recalling {r['recall']:>2}, by r600 {r['d600']:>2})")
    print()
    for bot in BOTS:
        rs = res.get(bot, [])
        if rs:
            print(f"{bot:26} wins {sum(r['win'] for r in rs)}/{len(rs)}  deaths/game {st.mean(r['deaths'] for r in rs):.1f}  recalling {st.mean(r['recall'] for r in rs):.1f}"
                  f"  by r600 {st.mean(r['d600'] for r in rs):.1f}  gold {st.mean(r['gold'] for r in rs):.0f} vs {st.mean(r['ogold'] for r in rs):.0f}")

if __name__ == '__main__':
    main()
