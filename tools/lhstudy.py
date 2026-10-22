"""Low-HP episodes from local games, read from the bots' own per-turn 'LH' log lines (same definitions as
tools/lowhp.py on team/kurians/t3-contest-rows, except 'off spawn' is the bot's own spawn-region flag).
LH line: LH round slot alive hp maxhp recalling onspawn nearest_visible_enemy
usage: python3 -I lhstudy.py DIR   (DIR holds <map>__<A>__<B>.repl26a bundles and .json stats)"""
import collections, glob, json, os, sys, zipfile, statistics as st

DIR = sys.argv[1]
FROM = 150

def episodes(lines):
    eps, open_ep, prev = [], {}, {}
    for r, s, alive, hp, mx, rec, sp, ne in lines:
        pc = prev.get(s); ep = open_ep.get(s)
        off = alive and not sp
        if ep is not None:
            if pc and pc['rec'] and not rec:
                if alive and sp: ep['done'] += 1
                elif alive: ep['cancel'] += 1
            if rec and not (pc and pc['rec']): ep['try'] += 1; ep['try_ne'].append(ne)
            if not alive:
                ep['end'] = 'death_recalling' if pc and pc['rec'] else 'death'
                eps.append(ep); del open_ep[s]
            elif off and hp >= .9 * mx:
                ep['end'] = 'resumed'; ep['len'] = r - ep['start']; eps.append(ep); del open_ep[s]
            elif r - ep['start'] > 300:
                ep['end'] = 'open'; eps.append(ep); del open_ep[s]
        elif alive and off and r >= FROM and hp < .3 * mx:
            open_ep[s] = {'start': r, 'try': int(rec), 'try_ne': [ne] if rec else [], 'done': 0, 'cancel': 0, 'late': r > 600}
        prev[s] = {'rec': rec}
    return eps

def load(path, bot):
    m, a, b = os.path.basename(path)[:-8].split('__')
    team = 'a' if a == bot else 'b'
    z = zipfile.ZipFile(path)
    txt = z.read(f'team-{team}.stdout').decode('utf-8', 'replace')
    lines = []
    for l in txt.splitlines():
        l = l.strip().strip('\x00').strip()
        if l.startswith('LH '):
            p = l.split()
            if len(p) == 9: lines.append(tuple(int(x) for x in p[1:]))
    stats = json.load(open(path[:-8] + '.json'))
    side = 'teamA' if team == 'a' else 'teamB'
    won = stats['match']['outcome'] == side
    g = {t['team']: int(t['submittedGems']) for t in stats['teams']}
    deaths = sum(int(c['metrics']['deaths']) for c in stats['champions'] if c['team'] == side)
    return m, lines, won, g[side] - g['teamB' if side == 'teamA' else 'teamA'], deaths

def summary(eps):
    n = len(eps)
    if not n: return 'no episodes'
    tries = sum(e['try'] for e in eps); done = sum(e['done'] for e in eps)
    dr = sum(e['end'] == 'death_recalling' for e in eps); dn = sum(e['end'] == 'death' for e in eps)
    res = [e for e in eps if e['end'] == 'resumed']
    return (f"{n:4d} eps | died {(dr + dn) / n:4.0%} (recalling {dr:3d}, otherwise {dn:3d}) | resumed {len(res) / n:4.0%}"
            f" | recalls {tries:3d}: completed {done / max(1, tries):4.0%}, died-while-recalling {dr / max(1, tries):4.0%}")

def main():
    bots = sorted({os.path.basename(p)[:-8].split('__')[i] for p in glob.glob(f'{DIR}/*.repl26a') for i in (1, 2) if os.path.basename(p)[:-8].split('__')[i].startswith('lh-')})
    data = collections.defaultdict(lambda: collections.defaultdict(list))
    res = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0]))
    for bot in bots:
        for p in sorted(glob.glob(f'{DIR}/*__*.repl26a')):
            if bot not in os.path.basename(p).split('__')[1:3] and bot + '.repl26a' not in os.path.basename(p): continue
            if not os.path.exists(p[:-8] + '.json'): continue
            m, lines, won, margin, deaths = load(p, bot)
            data[bot][m] += episodes(lines)
            r = res[bot][m]; r[0] += 1; r[1] += won; r[2] += margin; r[3] += deaths
    maps = sorted({m for b in bots for m in data[b]} | {m for b in bots for m in res[b]})
    for m in maps + ['ALL non-contest']:
        print(f'=== {m} ===')
        for bot in bots:
            ms = [x for x in maps if x != '00contest'] if m.startswith('ALL') else [m]
            g = [res[bot][x] for x in ms]
            n = sum(x[0] for x in g)
            if not n: continue
            print(f'  {bot:13s} games {n:3d} wins {sum(x[1] for x in g):3d} margin/game {sum(x[2] for x in g) / n:+6.0f} deaths/game {sum(x[3] for x in g) / n:5.1f}')
            eps = [e for x in ms for e in data[bot][x]]
            for lab, sel in (('r150-600', lambda e: not e['late']), ('r600+   ', lambda e: e['late'])):
                print(f'      {lab} {summary([e for e in eps if sel(e)])}')

if __name__ == '__main__':
    main()
