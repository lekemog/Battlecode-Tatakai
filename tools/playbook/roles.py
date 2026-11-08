"""roles.py LABEL=DIR [...] : what each champion type does, from decoded engine-3 replays (extract5.mjs).

Per champion-game (alive rounds, off spawn), shares of rounds:
  pvp   : an enemy champion within 4 tiles;
  camp  : a living camp within 2 tiles and no enemy champion within 4 (farming);
  carry : carrying 20+ gems;
  solo  : no ally within 8 tiles;
plus per game: earned gold, kills, deaths, gems submitted are not per champion in the replay, so 'gems carried peak' is shown.
Win share of the champion's team when the type is present. Labels starting with 'us' count only Tatakai's side (from
~/games/ours/list.txt); others count both teams.
"""
import collections
import glob
import json
import os
import sys

T = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'Heart']


def cheb(a, b):
    return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))


def game(path, only_team=None):
    d = json.load(open(path))
    rounds = [r for r in d['rounds'] if r.get('phase') == 1 and r['round'] >= 1]
    if not rounds:
        return []
    final = d['rounds'][-1]
    sub = final.get('submittedGems') or [0, 0]
    win = 0 if sub[0] > sub[1] else 1 if sub[1] > sub[0] else None
    first = rounds[0]
    spawn = {}
    for t in (0, 1):
        pts = [c['position'] for c in first['champions'] if c['team'] == t and 'position' in c]
        spawn[t] = {'x': round(sum(p['x'] for p in pts) / len(pts)), 'y': round(sum(p['y'] for p in pts) / len(pts))}
    stats = collections.defaultdict(lambda: collections.Counter())
    for st in rounds[::2]:
        champs = [c for c in st['champions'] if c.get('alive') and 'position' in c]
        camps = [c for c in st.get('camps', []) if c.get('alive', True) and 'position' in c and c.get('health', 1) > 0]
        for c in champs:
            if only_team is not None and c['team'] != only_team:
                continue
            key = (c['team'], c['entity']['index'], c['type'])
            s = stats[key]
            if cheb(c['position'], spawn[c['team']]) <= 2:
                continue
            s['n'] += 1
            enemy4 = any(o['team'] != c['team'] and cheb(o['position'], c['position']) <= 4 for o in champs)
            ally8 = any(o is not c and o['team'] == c['team'] and cheb(o['position'], c['position']) <= 8 for o in champs)
            camp2 = any(cheb(k['position'], c['position']) <= 2 for k in camps)
            s['pvp'] += enemy4
            s['camp'] += camp2 and not enemy4
            s['carry'] += c.get('gems', 0) >= 20
            s['solo'] += not ally8
    out = []
    last = {(c['team'], c['entity']['index']): c for c in final['champions']}
    for (team, idx, typ), s in stats.items():
        if s['n'] < 50:
            continue
        lc = last.get((team, idx), {})
        kda = lc.get('kda') or [0, 0, 0]
        out.append(dict(type=typ, pvp=s['pvp'] / s['n'], camp=s['camp'] / s['n'], carry=s['carry'] / s['n'], solo=s['solo'] / s['n'],
                        gold=lc.get('earnedGold', 0), kills=kda[0], deaths=kda[1], win=None if win is None else float(win == team)))
    return out


def main():
    side_of = {}
    lst = os.path.expanduser('~/games/ours/list.txt')
    if os.path.exists(lst):
        for line in open(lst):
            mid, opp, side, mp = line.split()
            side_of[mid] = 0 if side == 'a' else 1
    for spec in sys.argv[1:]:
        label, path = spec.split('=', 1)
        rows = []
        for f in sorted(glob.glob(os.path.join(path, '*.json'))):
            mid = os.path.basename(f)[:-5]
            team = side_of.get(mid) if label.startswith('us') else None
            if label.startswith('us') and team is None:
                continue
            try:
                rows += game(f, team)
            except Exception as e:
                print('skip', f, e)
        print(f'\n=== {label}: {len(rows)} champion-games')
        print(f'   {"type":9s} {"n":>4s} {"pvp":>5s} {"farm":>5s} {"carry":>5s} {"solo":>5s} {"gold":>6s} {"kills":>5s} {"deaths":>6s} {"win":>5s}')
        for t in range(len(T)):
            r = [x for x in rows if x['type'] == t]
            if len(r) < 5:
                continue
            m = lambda k: sum(x[k] for x in r) / len(r)
            wins = [x['win'] for x in r if x['win'] is not None]
            print(f'   {T[t]:9s} {len(r):4d} {m("pvp"):5.2f} {m("camp"):5.2f} {m("carry"):5.2f} {m("solo"):5.2f} {m("gold"):6.0f} {m("kills"):5.2f} {m("deaths"):6.2f} {sum(wins) / max(1, len(wins)):5.2f}')


if __name__ == '__main__':
    main()
