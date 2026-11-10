"""priority.py : learn the top teams' turn order from decoded engine-3 replays, with features the bot computes.

Rows: top-15 champion-rounds (every 3rd round) where its team has 2+ living champions with distinct next priorities and an
enemy champion within 5 of any of them. Label: the champion has its team's highest nextPriority (acts first next round).
Features (all computable in brain.cpp):
  hazard  = shipped v51d hazard probability of the champion (danger),
  pkill   = kill-model probability for the most killable enemy within attack range + 1 (0 if none),
  can_kill= an enemy in reach + 1 with health <= 1.2 x strength,
  hp_frac, near = min(enemy distance, 8) / 8, ranged, gems / 100.
Fits a logistic model (held out by game) and prints integer-scaled weights for the bot.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import offense  # noqa: E402
import train  # noqa: E402


def cheb(a, b):
    return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))


def pw(o):
    return float(o.get('maxHealth', 1000)) * (float(o.get('strength', {}).get('effective', 0)) + float(o.get('focus', {}).get('effective', 0)))


def rows_of(path):
    d = json.load(open(path))
    R = {r['round']: r for r in d['rounds'] if r.get('phase') == 1 and r['round'] >= 1}
    keys = sorted(R)
    first = R[keys[0]]
    spawn = {}
    for t in (0, 1):
        pts = [c['position'] for c in first['champions'] if c['team'] == t and 'position' in c]
        spawn[t] = {'x': round(sum(p['x'] for p in pts) / len(pts)), 'y': round(sum(p['y'] for p in pts) / len(pts))}
    hp_hist = {}
    for k in keys:
        for c in R[k]['champions']:
            hp_hist[(c['team'], c['entity']['index'], k)] = c['health'] if c.get('alive') else -1
    w = train.shipped_weights()
    X, y = [], []
    for k in keys[::3]:
        ch = [c for c in R[k]['champions'] if c.get('alive') and 'position' in c and c.get('nextPriority') is not None]
        for team in (0, 1):
            mine = [c for c in ch if c['team'] == team]
            en = [c for c in ch if c['team'] != team]
            if len(mine) < 2 or not en or len({m['nextPriority'] for m in mine}) < 2:
                continue
            if not any(cheb(m['position'], e['position']) <= 5 for m in mine for e in en):
                continue
            top = max(m['nextPriority'] for m in mine)
            for m in mine:
                xf = offense.feats(m, R[k], spawn, k, hp_hist)
                hz = float(train.sig(xf @ w)) if xf is not None else 0.0
                rng = max(1, m.get('attackRange', 1))
                pk, ck = 0.0, 0.0
                for e in en:
                    if cheb(e['position'], m['position']) > rng + 1:
                        continue
                    if e['health'] <= 1.2 * float(m['strength']['effective']):
                        ck = 1.0
                    ours = sum(pw(o) for o in mine if cheb(o['position'], e['position']) <= 6)
                    them = pw(e) + sum(pw(o) for o in en if o is not e and cheb(o['position'], e['position']) <= 6)
                    z = 0.933 + 0.788 * np.log(max(1e-3, ours / max(1.0, them))) - 2.851 * e['health'] / max(1, e['maxHealth'])
                    pk = max(pk, float(1 / (1 + np.exp(-z))))
                near = min(min(cheb(m['position'], e['position']) for e in en), 8) / 8.0
                X.append([hz, pk, ck, m['health'] / max(1, m['maxHealth']), near, float(m.get('attackRange', 1) > 1), min(m.get('gems', 0), 100) / 100])
                y.append(1.0 if m['nextPriority'] == top else 0.0)
    return X, y


def main():
    files = sorted(glob.glob('/root/games/dec/*.json'))
    X, y, g = [], [], []
    for gi, f in enumerate(files):
        try:
            a, b = rows_of(f)
        except Exception:
            continue
        X += a; y += b; g += [gi] * len(a)
    X, y, g = np.array(X), np.array(y), np.array(g)
    names = ['hazard', 'pkill', 'can_kill', 'hp_frac', 'near', 'ranged', 'gems']
    print(f'rows {len(y)} first-share {y.mean():.3f} games {len(np.unique(g))}')
    Z = np.c_[np.ones(len(X)), X]

    def fit(Z, y):
        w = np.zeros(Z.shape[1])
        for _ in range(60):
            p = 1 / (1 + np.exp(-Z @ w)); H = Z.T @ (Z * (p * (1 - p))[:, None]) + 1e-3 * np.eye(len(w)); w -= np.linalg.solve(H, Z.T @ (p - y))
        return w
    games = np.unique(g); rng = np.random.RandomState(0); rng.shuffle(games); P = np.zeros(len(y))
    for fold in np.array_split(games, 5):
        te = np.isin(g, fold); w = fit(Z[~te], y[~te]); P[te] = 1 / (1 + np.exp(-Z[te] @ w))
    print(f'held-out AUC {train.auc(y, P):.3f}')
    w = fit(Z, y)
    print('raw weights: bias %.3f ' % w[0] + ' '.join(f'{n} {v:+.3f}' for n, v in zip(names, w[1:])))
    print('bot integer weights (x100): ' + ', '.join(f'{n} {int(round(v * 100))}' for n, v in zip(['bias'] + names, w)))


if __name__ == '__main__':
    main()
