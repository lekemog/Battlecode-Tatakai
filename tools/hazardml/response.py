"""response.py LABEL=DIR [LABEL=DIR ...] [--team NAME] : what champions do when the shipped hazard model raises an alarm, and
whether they survive. Decoded engine-3 replays (extract5.mjs).

At every alarm (shipped logistic p >= 0.2, enemy within 8, off spawn), the move over the next 3 rounds is classed by which
distance shrinks most: 'ally' (toward the nearest ally), 'home' (toward own spawn), 'enemy' (toward the nearest enemy), 'hold'
(moved <= 1 tile). Reports the share of each response and the death rate within 10 rounds after it, per label.
For our own games (label 'us'), only our team's champions count; pass --us-team-from-list FILE (match id, opp, side, map) or
use top-team folders where both teams count.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
import train  # noqa: E402


def cheb(a, b):
    return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))


def analyse(path, only_team=None):
    d = json.load(open(path))
    rounds = {r['round']: r for r in d['rounds'] if r.get('phase') == 1 and r['round'] >= 1}
    keys = sorted(rounds)
    if not keys:
        return []
    first = rounds[keys[0]]
    spawn = {}
    for t in (0, 1):
        pts = [c['position'] for c in first['champions'] if c['team'] == t]
        spawn[t] = {'x': round(sum(p['x'] for p in pts) / len(pts)), 'y': round(sum(p['y'] for p in pts) / len(pts))}
    w = train.shipped_weights()

    out = []
    ident = lambda c: (c['team'], c['entity']['index'])
    death_round = {}
    prev = None
    for k in keys:
        st = rounds[k]
        if prev:
            ap = {ident(c) for c in prev['champions'] if c['alive']}
            for c in st['champions']:
                if ident(c) in ap and not c['alive']:
                    death_round.setdefault(ident(c), []).append(k)
        prev = st
    last_alarm = {}
    for k in keys:
        if k + 3 not in rounds:
            continue
        st, later = rounds[k], rounds[k + 3]
        lat = {ident(c): c for c in later['champions']}
        for c in st['champions']:
            if not c['alive'] or (only_team is not None and c['team'] != only_team):
                continue
            team = c['team']; pos = c['position']
            if cheb(pos, spawn[team]) <= 2:
                continue
            allies = [o for o in st['champions'] if o['alive'] and o['team'] == team and o is not c]
            enemies = [o for o in st['champions'] if o['alive'] and o['team'] != team and cheb(o['position'], spawn[1 - team]) > 2]
            near = [e for e in enemies if cheb(e['position'], pos) <= 8]
            if not near:
                continue
            # shipped features (subset recomputed as in build.rows_of)
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
            x = np.array([1.0, hp / max(1.0, mx), hp / 1000.0, mx / 2000.0, a4 / 4.0, a8 / 4.0, e4 / 4.0, e8 / 4.0,
                          hp4 / (hp4 + eh4 + 1.0), hp8 / (hp8 + eh8 + 1.0), min(ne, 8) / 8.0, min(na, 8) / 8.0, r5 / 4.0,
                          cheb(pos, spawn[team]) / 40.0, k / 1000.0, c.get('gems', 0) / 100.0, fs, 0.0, emax / 2000.0, float(cut)])
            if train.sig(x @ w) < 0.2:
                continue
            if last_alarm.get(ident(c), -99) >= k - 3:
                continue  # one sample per alarm episode start
            last_alarm[ident(c)] = k
            l = lat.get(ident(c))
            died = any(k < dr <= k + 10 for dr in death_round.get(ident(c), []))
            if l is None or not l['alive']:
                resp = 'hold' if not died else 'died<3'
            else:
                p2 = l['position']
                moved = cheb(p2, pos)
                ally_c = min(allies, key=lambda o: cheb(o['position'], pos)) if allies else None
                enemy_c = min(near, key=lambda o: cheb(o['position'], pos))
                d_ally = (cheb(pos, ally_c['position']) - cheb(p2, ally_c['position'])) if ally_c else -9
                d_home = cheb(pos, spawn[team]) - cheb(p2, spawn[team])
                d_enemy = cheb(pos, enemy_c['position']) - cheb(p2, enemy_c['position'])
                if moved <= 1:
                    resp = 'hold'
                else:
                    resp = max((('ally', d_ally), ('home', d_home), ('enemy', d_enemy)), key=lambda t: t[1])[0]
            out.append((resp, died, a8, e8))
    return out


def main():
    args = sys.argv[1:]
    for spec in args:
        label, path = spec.split('=', 1)
        only = None
        files = sorted(glob.glob(os.path.join(path, '*.json')))
        side_of = {}
        if label.startswith('us') and os.path.exists(os.path.join(os.path.dirname(path.rstrip('/')), 'ours', 'list.txt')):
            for line in open(os.path.join(os.path.dirname(path.rstrip('/')), 'ours', 'list.txt')):
                mid, opp, side, mp = line.split()
                side_of[mid] = 0 if side == 'a' else 1
        rows = []
        for f in files:
            mid = os.path.basename(f)[:-5]
            team = side_of.get(mid) if label.startswith('us') else None
            if label.startswith('us') and team is None:
                continue
            try:
                rows += analyse(f, team)
            except Exception as e:
                print('skip', f, e)
        n = len(rows)
        print(f'{label}: {n} alarms, died within 10 rounds {np.mean([r[1] for r in rows]):.3f}')
        for resp in ('ally', 'home', 'enemy', 'hold', 'died<3'):
            sub = [r for r in rows if r[0] == resp]
            if sub:
                print(f'   {resp:7s} {len(sub) / n:6.1%} of alarms   death rate {np.mean([r[1] for r in sub]):.3f}   '
                      f'mean allies8 {np.mean([r[2] for r in sub]):.2f} enemies8 {np.mean([r[3] for r in sub]):.2f}')


if __name__ == '__main__':
    main()
