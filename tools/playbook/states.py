"""states.py LABEL=DIR [...] : what teams do in each game state, from decoded engine-3 replays.

Per alive champion-round (every 2nd round), activity (first match wins):
  bank   : its carried gems fell this round while alive (tributing at an altar);
  fight  : an enemy champion within 4;
  farm   : a living camp within 2 (own half) / invade: same on the enemy half (closer to the enemy spawn);
  home   : within 3 of its own spawn (shopping, healing, recall);
  carry  : carrying 20+ gems, none of the above (on the way to bank);
  move   : anything else.
States: numbers = (living champions ours - theirs): ahead / even / behind; phase: r<200, 200-600, 600+.
Also per state: gems banked per champion-round and kills per 100 champion-rounds. 'us*' labels count Tatakai's side only.
"""
import collections
import glob
import json
import os
import sys


def cheb(a, b):
    return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))


ACTS = ['bank', 'fight', 'farm', 'invade', 'home', 'carry', 'move']


def game(path, only):
    d = json.load(open(path))
    rounds = [r for r in d['rounds'] if r.get('phase') == 1 and r['round'] >= 1]
    if not rounds:
        return []
    first = rounds[0]
    spawn = {}
    for t in (0, 1):
        pts = [c['position'] for c in first['champions'] if c['team'] == t and 'position' in c]
        spawn[t] = {'x': round(sum(p['x'] for p in pts) / len(pts)), 'y': round(sum(p['y'] for p in pts) / len(pts))}
    out = []
    prev = {}
    prev_kda = {}
    for i, st in enumerate(rounds):
        k = st['round']
        ch = st['champions']
        alive = {t: sum(1 for c in ch if c['team'] == t and c.get('alive')) for t in (0, 1)}
        camps = [c for c in st.get('camps', []) if 'position' in c and c.get('health', 0) > 0]
        kills_now = {}
        for c in ch:
            key = (c['team'], c['entity']['index'])
            kda = (c.get('kda') or [0, 0, 0])[0]
            kills_now[key] = kda - prev_kda.get(key, kda)
            prev_kda[key] = kda
        if i % 2:
            for c in ch:
                prev[(c['team'], c['entity']['index'])] = c.get('gems', 0)
            continue
        for c in ch:
            key = (c['team'], c['entity']['index'])
            g0 = prev.get(key, c.get('gems', 0))
            prev[key] = c.get('gems', 0)
            if not c.get('alive') or 'position' not in c:
                continue
            team = c['team']
            if only is not None and team != only:
                continue
            pos = c['position']
            enemies = [o for o in ch if o['team'] != team and o.get('alive') and 'position' in o]
            banked = max(0, g0 - c.get('gems', 0))
            if banked > 0:
                act = 'bank'
            elif any(cheb(o['position'], pos) <= 4 for o in enemies):
                act = 'fight'
            elif any(cheb(m['position'], pos) <= 2 for m in camps):
                act = 'invade' if cheb(pos, spawn[1 - team]) < cheb(pos, spawn[team]) else 'farm'
            elif cheb(pos, spawn[team]) <= 3:
                act = 'home'
            elif c.get('gems', 0) >= 20:
                act = 'carry'
            else:
                act = 'move'
            diff = alive[team] - alive[1 - team]
            num = 'ahead' if diff > 0 else 'behind' if diff < 0 else 'even'
            phase = 'r<200' if k < 200 else 'r200-600' if k < 600 else 'r600+'
            out.append((num, phase, act, banked, kills_now.get(key, 0)))
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
            except Exception:
                pass
        print(f'\n=== {label}: {len(rows)} champion-rounds')
        print(f'   {"state":16s} {"share":>6s} ' + ' '.join(f'{a:>6s}' for a in ACTS) + '  gems/100r kills/100r')
        groups = collections.defaultdict(list)
        for r in rows:
            groups[r[0]].append(r); groups[r[1]].append(r)
        for key in ('ahead', 'even', 'behind', 'r<200', 'r200-600', 'r600+'):
            g = groups.get(key, [])
            if not g:
                continue
            cnt = collections.Counter(r[2] for r in g)
            print(f'   {key:16s} {len(g) / len(rows):6.1%} ' + ' '.join(f'{cnt[a] / len(g):6.1%}' for a in ACTS) +
                  f'  {100 * sum(r[3] for r in g) / len(g):8.1f} {100 * sum(r[4] for r in g) / len(g):8.2f}')


if __name__ == '__main__':
    main()
