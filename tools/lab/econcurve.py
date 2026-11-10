"""econcurve.py PANEL_LABEL [...] : gold economy by round, us vs the opponent, from real panel games (results/panel).
For each checkpoint round: team earned gold, spent gold, gold held unspent, gems carried, deaths, and the share of earned gold spent.
Series are rebuilt from the run-length timelines in the match summaries (championTimelines)."""
import collections, glob, gzip, json, os, statistics, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'panel')
CP = (50, 100, 150, 200, 300, 400, 500, 600, 800)

def series(tl):
    out = []
    for r in tl['runs']:
        out += [float(r['value'])] * int(r['duration'])
    return out

def team_curves(j, team):
    cur = collections.defaultdict(lambda: collections.defaultdict(list))
    for t in j['championTimelines']:
        if t['owner'].get('team') != team or t['metric'] not in ('earnedGold', 'spentGold', 'gold', 'gems', 'deaths'):
            continue
        cur[t['metric']][t['owner']['id']] = series(t)
    res = {}
    for m, per in cur.items():
        n = max(len(s) for s in per.values())
        tot = [0.0] * n
        for s in per.values():
            for i in range(n):
                tot[i] += s[i] if i < len(s) else (s[-1] if s else 0)
        res[m] = tot
    return res

def main():
    games = []
    for lab in sys.argv[1:]:
        p = json.load(open(os.path.join(ROOT, lab + '.json')))
        for opp, gs in p['games'].items():
            for g in gs:
                f = os.path.join(ROOT, 'summaries', g['match'] + '.json')
                try:
                    j = json.load(gzip.open(f + '.gz', 'rt')) if os.path.exists(f + '.gz') else json.load(open(f))
                except Exception:
                    continue
                me = 'teamA' if g['side'] == 'a' else 'teamB'
                games.append((team_curves(j, me), team_curves(j, 'teamB' if me == 'teamA' else 'teamA')))
    print(len(games), 'games')
    for name, key in (('earned gold', 'earnedGold'), ('spent gold', 'spentGold'), ('gold held unspent', 'gold'), ('gems carried', 'gems'), ('deaths (cumulative)', 'deaths')):
        print(f'\n{name}:  round  ' + ''.join(f'{c:>7d}' for c in CP))
        for side, lab in ((0, 'us'), (1, 'them')):
            row = []
            for c in CP:
                v = [g[side][key][c] for g in games if key in g[side] and len(g[side][key]) > c]
                row.append(statistics.mean(v) if v else float('nan'))
            print(f'  {lab:5s}              ' + ''.join(f'{x:7.0f}' for x in row))
    # gold-rounds held unspent while above 150 (one emblem), per champion-round, first 600 rounds
    for side, lab in ((0, 'us'), (1, 'them')):
        v = []
        for g in games:
            if 'gold' in g[side] and len(g[side]['gold']) > 600:
                v.append(sum(1 for x in g[side]['gold'][:600] if x >= 4 * 150) / 600)  # team gold >= 4 emblems' worth
        print(f'{lab}: share of the first 600 rounds the team holds >= 600 unspent gold: {statistics.mean(v):.2f}')

main()
