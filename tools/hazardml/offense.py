"""offense.py LABEL=DIR [...] : kill opportunities and how they are used, from decoded engine-3 replays.

An opportunity = an enemy champion (off its spawn) whose own hazard (the shipped v51d logistic, computed from the enemy's point
of view) is >= T (default 0.3) while at least one of our champions is within 6 tiles. Episodes start when the hazard first
crosses T (one per enemy per 5 rounds). For each: did our side commit (any of our champions within 6 moved closer to it or hit it
over the next 3 rounds: health drop on the enemy), did it die within 10 rounds, and did we lose a champion within 10 rounds.
Labels starting with 'us' use the side list in ~/games/ours/list.txt (our team only); other labels count both teams.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import train  # noqa: E402


def cheb(a, b):
    return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))


def feats(c, st, spawn, k, hp_hist):
    team = c['team']; pos = c['position']
    allies = [o for o in st['champions'] if o['alive'] and o['team'] == team and o is not c]
    near = [o for o in st['champions'] if o['alive'] and o['team'] != team and cheb(o['position'], spawn[1 - team]) > 2 and cheb(o['position'], pos) <= 8]
    if not near:
        return None
    hp, mx = float(c['health']), float(c['maxHealth'])
    a4 = sum(cheb(o['position'], pos) <= 4 for o in allies); a8 = sum(cheb(o['position'], pos) <= 8 for o in allies)
    e4 = sum(cheb(o['position'], pos) <= 4 for o in near); e8 = len(near)
    hp4 = hp + sum(o['health'] for o in allies if cheb(o['position'], pos) <= 4)
    hp8 = hp + sum(o['health'] for o in allies if cheb(o['position'], pos) <= 8)
    eh4 = sum(o['health'] for o in near if cheb(o['position'], pos) <= 4); eh8 = sum(o['health'] for o in near)
    ne = min(cheb(o['position'], pos) for o in near); na = min([cheb(o['position'], pos) for o in allies] + [8])
    r5 = sum(cheb(o['position'], pos) <= 5 and o.get('attackRange', 1) > 1 for o in near)
    cut = int(any(cheb(o['position'], pos) <= 5 and cheb(o['position'], spawn[team]) < cheb(pos, spawn[team]) for o in near))
    fs = sum(o['health'] / max(1.0, o['maxHealth']) for o in near) / e8
    emax = max(o['maxHealth'] for o in near)
    h3 = hp_hist.get((team, c['entity']['index'], k - 3), -1.0)
    lost = (h3 - hp) / max(1.0, mx) if h3 >= 0 else 0.0
    return np.array([1.0, hp / max(1.0, mx), hp / 1000.0, mx / 2000.0, a4 / 4.0, a8 / 4.0, e4 / 4.0, e8 / 4.0,
                     hp4 / (hp4 + eh4 + 1.0), hp8 / (hp8 + eh8 + 1.0), min(ne, 8) / 8.0, min(na, 8) / 8.0, r5 / 4.0,
                     cheb(pos, spawn[team]) / 40.0, k / 1000.0, c.get('gems', 0) / 100.0, fs, lost, emax / 2000.0, float(cut)])


def analyse(path, our_team=None, T=0.3):
    d = json.load(open(path))
    rounds = {r['round']: r for r in d['rounds'] if r.get('phase') == 1 and r['round'] >= 1}
    raw = {k: list(r['champions']) for k, r in rounds.items()}
    for r in rounds.values():
        r['champions'] = [c for c in r['champions'] if 'position' in c]
    keys = sorted(rounds)
    if not keys:
        return []
    first = rounds[keys[0]]
    spawn = {}
    for t in (0, 1):
        pts = [c['position'] for c in first['champions'] if c['team'] == t]
        spawn[t] = {'x': round(sum(p['x'] for p in pts) / len(pts)), 'y': round(sum(p['y'] for p in pts) / len(pts))}
    ident = lambda c: (c['team'], c['entity']['index'])
    deaths = {}
    hp_hist = {}
    prev = None
    for k in keys:
        st = rounds[k]
        for c in st['champions']:
            hp_hist[(c['team'], c['entity']['index'], k)] = c['health'] if c['alive'] else -1.0
        if prev is not None:
            ap = {ident(c) for c in raw[prev] if c.get('alive')}
            for c in raw[k]:
                if ident(c) in ap and not c.get('alive'):
                    deaths.setdefault(c['team'], []).append((k, ident(c)))
        prev = k
    w = train.shipped_weights()
    last = {}
    out = []
    for k in keys:
        if k + 3 not in rounds:
            continue
        st, later = rounds[k], rounds[k + 3]
        lat = {ident(c): c for c in later['champions']}
        for victim in st['champions']:
            if not victim['alive']:
                continue
            attacker_team = 1 - victim['team']
            if our_team is not None and attacker_team != our_team:
                continue
            if cheb(victim['position'], spawn[victim['team']]) <= 2:
                continue
            ours = [o for o in st['champions'] if o['alive'] and o['team'] == attacker_team and cheb(o['position'], victim['position']) <= 6]
            if not ours:
                continue
            x = feats(victim, st, spawn, k, hp_hist)
            if x is None or train.sig(x @ w) < T:
                continue
            if last.get(ident(victim), -99) >= k - 5:
                last[ident(victim)] = k
                continue
            last[ident(victim)] = k
            v2 = lat.get(ident(victim))
            hit = v2 is not None and (not v2['alive'] or v2['health'] < victim['health'])
            closer = any(lat.get(ident(o)) and lat[ident(o)]['alive'] and v2 is not None and
                         cheb(lat[ident(o)]['position'], v2['position']) < cheb(o['position'], victim['position']) for o in ours)
            commit = hit or closer
            killed = any(k < r <= k + 10 and i == ident(victim) for r, i in deaths.get(victim['team'], []))
            lost = any(k < r <= k + 10 for r, i in deaths.get(attacker_team, []))
            pw = lambda o: float(o.get('maxHealth', 1000)) * (float(o.get('strength', {}).get('effective', 0)) + float(o.get('focus', {}).get('effective', 0)))
            ratio = sum(pw(o) for o in ours) / max(1.0, pw(victim))
            mine = sum(pw(o) for o in st['champions'] if o.get('alive') and o['team'] == attacker_team)
            theirs = sum(pw(o) for o in st['champions'] if o.get('alive') and o['team'] == victim['team'])
            out.append((commit, killed, lost, k, ratio, len(ours), mine / max(1.0, theirs)))
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
        rows, games = [], 0
        for f in sorted(glob.glob(os.path.join(path, '*.json'))):
            mid = os.path.basename(f)[:-5]
            team = side_of.get(mid) if label.startswith('us') else None
            if label.startswith('us') and team is None:
                continue
            games += 1 if label.startswith('us') else 2
            try:
                rows += analyse(f, team)
            except Exception as e:
                print('skip', f, e)
        if not rows:
            continue
        a = np.array(rows, dtype=float)
        early = a[a[:, 3] <= 200]
        print(f'{label}: {len(a)} opportunities ({len(a) / games:.1f} per team-game; before r200 {len(early) / games:.1f}), '
              f'committed {a[:, 0].mean():.2f}, killed {a[:, 1].mean():.2f} (when committed {a[a[:, 0] > 0, 1].mean():.2f}, '
              f'not {a[a[:, 0] == 0, 1].mean() if (a[:, 0] == 0).any() else float("nan"):.2f}), we lost a champion within 10 {a[:, 2].mean():.2f}')
        print(f'   kills from opportunities per team-game {a[:, 1].sum() / games:.2f}, before r200 {early[:, 1].sum() / games:.2f}')
        print(f'   mean power ratio at the opportunity (our champions within 6 / victim) {np.median(a[:, 4]):.2f} median; team power ratio (alive, ours/theirs) {np.median(a[:, 6]):.2f} median; attackers within 6 {a[:, 5].mean():.2f}')
        for lo, hi in ((0, 1), (1, 2), (2, 3), (3, 5), (5, 99)):
            sel = (a[:, 4] >= lo) & (a[:, 4] < hi)
            if sel.sum() >= 20:
                print(f'      power ratio {lo}-{hi}: n {int(sel.sum()):5d}  kill rate {a[sel, 1].mean():.3f}  we lose one {a[sel, 2].mean():.3f}')


if __name__ == '__main__':
    main()
