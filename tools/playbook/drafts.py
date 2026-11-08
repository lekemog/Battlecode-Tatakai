"""drafts.py ALLMATCHES.json WALK.txt : champion and duo value from match lists, controlled for team strength.

Model (per team-game): logit P(win) = team_strength[team] - team_strength[opp] + sum_c beta_c [c in our draft] - sum_c beta_c [c in theirs]
+ sum_pairs gamma_p [pair in ours] - [pair in theirs], L2-regularised (champions lambda 2, pairs lambda 8, teams lambda 1);
teams with < 15 games share one 'other' strength. Fitted separately for near maps (spawn walk <= 60) and far maps, and
3/4/5-pick maps pooled (draft indicator per champion). Reports champion effects (log-odds), the top and bottom pair synergies
(gamma, i.e. beyond the two champions' own effects) with games counts, and our usual five.
"""
import collections
import itertools
import json
import sys

import numpy as np

N = {0: 'Ryth', 1: 'Vesper', 2: 'Vendetta', 3: 'Cassi&Issac', 4: 'Stellar', 5: 'Prism', 6: 'Marcella', 7: 'Willow', 8: 'Ren',
     9: 'Varg', 10: 'Tavi', 11: 'Heart'}


def fit(rows, teams, pairs, iters=400, lr=0.5):
    nt, nc, npair = len(teams), 12, len(pairs)
    pidx = {p: i for i, p in enumerate(pairs)}
    # design: +1 for ours, -1 for theirs
    X = np.zeros((len(rows), nt + nc + npair), np.float32)
    y = np.zeros(len(rows), np.float32)
    for r, (ta, da, tb, db, win) in enumerate(rows):
        X[r, teams[ta]] += 1; X[r, teams[tb]] -= 1
        for c in da: X[r, nt + c] += 1
        for c in db: X[r, nt + c] -= 1
        for p in itertools.combinations(sorted(da), 2):
            if p in pidx: X[r, nt + nc + pidx[p]] += 1
        for p in itertools.combinations(sorted(db), 2):
            if p in pidx: X[r, nt + nc + pidx[p]] -= 1
        y[r] = win
    lam = np.concatenate([np.full(nt, 1.0), np.full(nc, 2.0), np.full(npair, 8.0)]).astype(np.float32)
    w = np.zeros(X.shape[1], np.float32)
    # Newton-like via gradient descent with Adam
    m = np.zeros_like(w); v = np.zeros_like(w)
    for t in range(1, iters + 1):
        p = 1 / (1 + np.exp(-(X @ w)))
        g = X.T @ (p - y) / len(y) + lam * w / len(y)
        m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g * g
        w -= 0.05 * (m / (1 - 0.9 ** t)) / (np.sqrt(v / (1 - 0.999 ** t)) + 1e-8)
    return w[nt:nt + nc], w[nt + nc:]


def main():
    ms = json.load(open(sys.argv[1]))
    walk = {}
    for line in open(sys.argv[2]):
        p = line.split()
        if len(p) >= 2 and p[1] != 'NA':
            walk[p[0]] = int(p[1])
    count = collections.Counter()
    for m in ms.values():
        for t in m['teams']:
            count[t['teamId']] += 1
    by_band = collections.defaultdict(list)
    for m in ms.values():
        a, b = m['teams']
        if a['result'] not in ('win', 'loss'):
            continue
        mp = m['map'].replace('_', '-')
        if mp not in walk:
            continue
        band = 'near' if walk[mp] <= 60 else 'far'
        ta = a['teamId'] if count[a['teamId']] >= 15 else 'other'
        tb = b['teamId'] if count[b['teamId']] >= 15 else 'other'
        by_band[band].append((ta, a['draftPicks'], tb, b['draftPicks'], 1.0 if a['result'] == 'win' else 0.0))
        by_band[band].append((tb, b['draftPicks'], ta, a['draftPicks'], 1.0 if b['result'] == 'win' else 0.0))
    out = {}
    for band, rows in sorted(by_band.items()):
        teams = {t: i for i, t in enumerate(sorted({r[0] for r in rows} | {r[2] for r in rows}))}
        pc = collections.Counter()
        for r in rows:
            for p in itertools.combinations(sorted(r[1]), 2):
                pc[p] += 1
        pairs = sorted(p for p, c in pc.items() if c >= 30)
        beta, gamma = fit(rows, teams, pairs)
        pick = collections.Counter(c for r in rows for c in r[1])
        print(f'\n=== {band} maps: {len(rows) // 2} games, {len(teams)} team strengths, {len(pairs)} pairs with >= 30 team-games')
        print('champion effect (log-odds, strength-controlled)   pick share')
        for c in sorted(range(12), key=lambda c: -beta[c]):
            print(f'   {N[c]:12s} {beta[c]:+.3f}   {pick[c] / len(rows):.1%}')
        order = np.argsort(-gamma)
        print('best pair synergies (beyond the two champions):')
        for i in order[:8]:
            print(f'   {N[pairs[i][0]]:11s} + {N[pairs[i][1]]:11s} {gamma[i]:+.3f}  (n {pc[pairs[i]]})')
        print('worst pair synergies:')
        for i in order[-6:]:
            print(f'   {N[pairs[i][0]]:11s} + {N[pairs[i][1]]:11s} {gamma[i]:+.3f}  (n {pc[pairs[i]]})')
        ours = [11, 0, 6, 2, 9]
        val = sum(beta[c] for c in ours) + sum(gamma[pairs.index(p)] for p in itertools.combinations(sorted(ours), 2) if p in pairs)
        out[band] = {'beta': beta.tolist(), 'pairs': [list(p) for p in pairs], 'gamma': gamma.tolist(), 'ours5': float(val)}
        print(f'our five (Heart, Ryth, Marcella, Vendetta, Varg): summed effect {val:+.3f}')
    json.dump(out, open('/root/games/draft_effects.json', 'w'))


if __name__ == '__main__':
    main()
