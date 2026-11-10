"""shop.py SUMMARY_DIR ALLMATCHES.json [--ours DIR_OF_GZ_SUMMARIES] : what top teams buy, when, on which champion, and what
wins. Match summaries from `cambc matches summary <id> --json`.

Per champion type (top-20 teams only): first purchase round; share of item spend per family (Hunter, Prospector, Treasure, Jungle,
Monster, Capture, Durability, Skirmish, Collectors, Tribute, Bruiser, Greed, ...) and per stat (Health/Strength/Focus), in three
windows (r<=200, 200-500, >500). Team level: for each family, the win rate of team-games in the top / bottom third of that
family's spend share (top-20 teams; a rough association, not causal). --ours adds the same table for Tatakai's games.
"""
import collections
import glob
import gzip
import json
import os
import sys


def load(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        return json.load(f)


def parse(item):
    w = item.split()
    fam = w[0]
    kind = 'emblem' if 'Emblem' in item else 'shard' if 'Shard' in item else 'other'
    stat = w[-1] if w[-1] in ('Health', 'Strength', 'Focus') else '-'
    return fam, kind, stat


def team_rows(d, team_filter):
    """yield (teamKey, champion name, [(round, family, kind, stat, cost)]) per champion"""
    out = collections.defaultdict(list)
    for e in d.get('events', []):
        if e.get('kind') != 'buyItem':
            continue
        own = e['owner']
        if own.get('kind') != 'champion' or not team_filter(own['team']):
            continue
        for en in e['entries']:
            fam, kind, stat = parse(en['target']['name'])
            out[(own['team'], own['id'], own['name'])].append((en['timestamp']['round'], fam, kind, stat, float(en.get('amount', 0))))
    return out


def summarise(label, games):
    """games: list of (summary, team side 'teamA'/'teamB', won)"""
    per = collections.defaultdict(lambda: {'n': 0, 'first': [], 'fam': collections.Counter(), 'stat': collections.Counter(), 'win': [0.0, 0.0]})
    team_share = []
    for d, side, won in games:
        rows = team_rows(d, lambda t: t == side)
        tot = collections.Counter()
        for (team, cid, name), buys in rows.items():
            p = per[name]
            p['n'] += 1
            p['first'].append(min(b[0] for b in buys))
            for r, fam, kind, stat, cost in buys:
                win = 0 if r <= 200 else 1 if r <= 500 else 2
                p['fam'][(win, fam)] += cost
                p['stat'][(win, stat)] += cost
                tot[fam] += cost
            p['win'][0] += won; p['win'][1] += 1
        s = sum(tot.values())
        if s > 0:
            team_share.append(({f: c / s for f, c in tot.items()}, won))
    print(f'\n=== {label}: {len(games)} team-games')
    for name, p in sorted(per.items(), key=lambda kv: -kv[1]['n']):
        if p['n'] < 10:
            continue
        fs = sorted(p['first'])
        line = f'   {name:14s} n {p["n"]:4d}  first buy median r{fs[len(fs) // 2]:4d}  team win {p["win"][0] / p["win"][1]:.2f}'
        for wi, wn in enumerate(('<=200', '200-500', '>500')):
            tot = sum(v for (w, f), v in p['fam'].items() if w == wi)
            if tot <= 0:
                continue
            top = sorted(((v / tot, f) for (w, f), v in p['fam'].items() if w == wi), reverse=True)[:3]
            st = {s: v / tot for (w, s), v in p['stat'].items() if w == wi}
            line += f'\n        {wn:8s} ' + ', '.join(f'{f} {sh:.0%}' for sh, f in top) + \
                    f'   | H {st.get("Health", 0):.0%} S {st.get("Strength", 0):.0%} F {st.get("Focus", 0):.0%}'
        print(line)
    fams = collections.Counter(f for sh, _ in team_share for f in sh)
    print('   family spend share vs win (top third / bottom third of team-games by that share):')
    for f, _ in fams.most_common(14):
        xs = sorted(team_share, key=lambda t: t[0].get(f, 0.0))
        k = len(xs) // 3
        lo = sum(w for _, w in xs[:k]) / max(1, k); hi = sum(w for _, w in xs[-k:]) / max(1, k)
        print(f'      {f:12s} high {hi:.2f}  low {lo:.2f}  diff {hi - lo:+.2f}')


def main():
    sdir, allm = sys.argv[1], sys.argv[2]
    ours_dir = sys.argv[sys.argv.index('--ours') + 1] if '--ours' in sys.argv else None
    ms = json.load(open(allm))
    lad = json.load(open(os.path.expanduser('~/games/ladder60.json')))
    rows = lad.get('teams') or lad.get('items') or lad
    top = {(r.get('teamId') or r.get('id')) for r in rows[:20]}
    games = []
    for f in glob.glob(os.path.join(sdir, '*.json')):
        mid = os.path.basename(f)[:-5]
        m = ms.get(mid)
        if not m:
            continue
        try:
            d = load(f)
        except Exception:
            continue
        for t in m['teams']:
            if t['teamId'] in top and t['result'] in ('win', 'loss'):
                games.append((d, 'teamA' if t['side'] == 'a' else 'teamB', 1.0 if t['result'] == 'win' else 0.0))
    summarise('top-20 teams', games)
    if ours_dir:
        og = []
        for f in glob.glob(os.path.join(ours_dir, '*.json*')):
            try:
                d = load(f)
            except Exception:
                continue
            names = [t for t in d.get('roster', [])]
            # our side: the team whose roster draft is Heart, Ryth, Marcella, Vendetta, Varg is not reliable; use teams[].name
            side = None
            for t in d.get('teams', []):
                if 'Tatakai' in json.dumps(t):
                    side = t.get('team')
            if side is None:
                continue
            won = 1.0 if d['match'].get('outcome') == side else 0.0
            og.append((d, side, won))
        summarise('Tatakai', og)


if __name__ == '__main__':
    main()
