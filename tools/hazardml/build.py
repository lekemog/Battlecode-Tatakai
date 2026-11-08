"""build.py OUT.npz DIR [DIR ...] : death-hazard dataset from engine-3 decoded replays (tools/replay/extract5.mjs).

One row per (round, alive champion off its spawn with an enemy champion within 8 tiles, not on the enemy spawn), with exactly
the 20 features the bot computes in brain.cpp (cfg::hazard), from the omniscient replay state:
  bias, hp_frac, hp/1000, max_hp/2000, allies4/4, allies8/4, enemies4/4, enemies8/4, S4, S8, nearest_enemy/8, nearest_ally/8,
  ranged_enemies5/4, spawn_dist/40, round/1000, gems/100, enemy_hp_mean_frac, hp_lost3/max, enemy_max_hp/2000, cut_off.
Label: the champion dies within the next 10 rounds with an enemy champion within 6 tiles the round before it dies.
Group id = replay, for held-out-by-match validation. Rows are subsampled every 2nd round to cut correlation.
"""
import glob
import json
import os
import sys

import numpy as np


def cheb(a, b):
    return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))


def rows_of(path):
    d = json.load(open(path))
    rounds = [r for r in d['rounds'] if r.get('phase') == 1 and r['round'] >= 1]
    by_round = {}
    for r in rounds:
        by_round[r['round']] = r
    if not by_round:
        return [], []
    keys = sorted(by_round)
    first = by_round[keys[0]]
    spawn = {}
    for team in (0, 1):
        pts = [c['position'] for c in first['champions'] if c['team'] == team]
        if pts:
            spawn[team] = {'x': round(sum(p['x'] for p in pts) / len(pts)), 'y': round(sum(p['y'] for p in pts) / len(pts))}
    if len(spawn) < 2:
        return [], []
    ident = lambda c: (c['team'], c['entity']['index'])
    # killed-by-enemy death rounds per champion
    deaths = {}
    prev = None
    for k in keys:
        st = by_round[k]
        if prev is not None:
            alive_prev = {ident(c): c for c in prev['champions'] if c['alive']}
            for c in st['champions']:
                i = ident(c)
                if i in alive_prev and not c['alive']:
                    p = alive_prev[i]
                    if any(e['alive'] and e['team'] != c['team'] and cheb(e['position'], p['position']) <= 6 for e in prev['champions']):
                        deaths.setdefault(i, []).append(k)
        prev = st
    hp_hist = {}
    X, y = [], []
    for k in keys:
        st = by_round[k]
        ch = st['champions']
        for c in ch:
            hp_hist.setdefault(ident(c), {})[k] = c['health'] if c['alive'] else -1.0
        if k % 2:
            continue
        for c in ch:
            if not c['alive']:
                continue
            team = c['team']
            home, their = spawn[team], spawn[1 - team]
            if cheb(c['position'], home) <= 2:
                continue
            pos = c['position']
            a4 = a8 = e4 = e8 = r5 = cut = 0
            na = ne = 8
            hp = float(c['health']); mx = float(c['maxHealth'])
            hp4 = hp8 = hp
            eh4 = eh8 = 0.0
            fs = 0.0
            emax = 0.0
            for o in ch:
                if not o['alive'] or o is c:
                    continue
                dd = cheb(o['position'], pos)
                if o['team'] == team:
                    na = min(na, dd)
                    if dd <= 4: a4 += 1; hp4 += o['health']
                    if dd <= 8: a8 += 1; hp8 += o['health']
                else:
                    if cheb(o['position'], their) <= 2:
                        continue
                    ne = min(ne, dd)
                    emax = max(emax, o['maxHealth'])
                    if dd <= 4: e4 += 1; eh4 += o['health']
                    if dd <= 8: e8 += 1; eh8 += o['health']; fs += o['health'] / max(1.0, o['maxHealth'])
                    if dd <= 5 and o.get('attackRange', 1) > 1: r5 += 1
                    if dd <= 5 and cheb(o['position'], home) < cheb(pos, home): cut = 1
            if e8 == 0:
                continue
            h3 = hp_hist[ident(c)].get(k - 3, -1.0)
            lost = (h3 - hp) / max(1.0, mx) if h3 >= 0 else 0.0
            x = [1.0, hp / max(1.0, mx), hp / 1000.0, mx / 2000.0, a4 / 4.0, a8 / 4.0, e4 / 4.0, e8 / 4.0,
                 hp4 / (hp4 + eh4 + 1.0), hp8 / (hp8 + eh8 + 1.0), ne / 8.0, na / 8.0, r5 / 4.0, cheb(pos, home) / 40.0,
                 k / 1000.0, c.get('gems', 0) / 100.0, fs / e8, lost, emax / 2000.0, float(cut)]
            label = any(k < dr <= k + 10 for dr in deaths.get(ident(c), []))
            X.append(x); y.append(1.0 if label else 0.0)
    return X, y


def main():
    out = sys.argv[1]
    files = []
    for d in sys.argv[2:]:
        files += sorted(glob.glob(os.path.join(d, '*.json')))
    X, y, g = [], [], []
    for gi, f in enumerate(files):
        try:
            a, b = rows_of(f)
        except Exception as e:
            print('skip', f, e)
            continue
        X += a; y += b; g += [gi] * len(a)
    X = np.array(X, dtype=np.float32); y = np.array(y, dtype=np.float32); g = np.array(g)
    np.savez_compressed(out, X=X, y=y, g=g, files=np.array(files))
    print(f'{len(files)} replays, {len(y)} rows, positives {int(y.sum())} ({y.mean():.3%})')


if __name__ == '__main__':
    main()
