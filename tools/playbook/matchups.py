"""matchups.py ALLMATCHES.json : champion-vs-champion counter effects from match lists, controlled for team strength and each
champion's own value. logit P(A wins) = s_A - s_B + sum beta(c in A) - sum beta(c in B) + sum_{a in A, b in B} delta[a,b] (antisymmetric),
L2 (teams 1, champions 2, matchups 6). Prints the strongest counters (a beats b) with team-game counts, and how our five fare
against each enemy champion."""
import collections, json, sys
import numpy as np
N = ['Ryth', 'Vesper', 'Vendetta', 'Cassi&Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'Heart']
ms = json.load(open(sys.argv[1]))
cnt = collections.Counter(t['teamId'] for m in ms.values() for t in m['teams'])
rows = []
for m in ms.values():
    a, b = m['teams']
    if a['result'] not in ('win', 'loss'): continue
    rows.append((a['teamId'] if cnt[a['teamId']] >= 15 else 'o', a['draftPicks'], b['teamId'] if cnt[b['teamId']] >= 15 else 'o', b['draftPicks'], float(a['result'] == 'win')))
teams = {t: i for i, t in enumerate(sorted({r[0] for r in rows} | {r[2] for r in rows}))}
pairs = [(i, j) for i in range(12) for j in range(i + 1, 12)]
pid = {p: k for k, p in enumerate(pairs)}
nt = len(teams)
X = np.zeros((len(rows), nt + 12 + len(pairs)), np.float32); y = np.zeros(len(rows), np.float32)
pc = collections.Counter()
for r, (ta, da, tb, db, w) in enumerate(rows):
    X[r, teams[ta]] += 1; X[r, teams[tb]] -= 1
    for c in da: X[r, nt + c] += 1
    for c in db: X[r, nt + c] -= 1
    for x in set(da):
        for z in set(db):
            if x == z: continue
            i, j = min(x, z), max(x, z); s = 1 if x < z else -1
            X[r, nt + 12 + pid[(i, j)]] += s; pc[(i, j)] += 1
    y[r] = w
lam = np.concatenate([np.full(nt, 1.0), np.full(12, 2.0), np.full(len(pairs), 6.0)]).astype(np.float32)
w = np.zeros(X.shape[1], np.float32); m = np.zeros_like(w); v = np.zeros_like(w)
for t in range(1, 601):
    p = 1 / (1 + np.exp(-(X @ w))); g = X.T @ (p - y) / len(y) + lam * w / len(y)
    m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g * g; w -= 0.05 * (m / (1 - 0.9 ** t)) / (np.sqrt(v / (1 - 0.999 ** t)) + 1e-8)
d = w[nt + 12:]
D = np.zeros((12, 12))
for (i, j), k in pid.items(): D[i, j] = d[k]; D[j, i] = -d[k]
print(f'{len(rows)} games')
print('strongest counters (row beats column, log-odds), n = games with the matchup:')
lst = sorted(((D[i, j], i, j) for i in range(12) for j in range(12) if i != j and pc[(min(i, j), max(i, j))] >= 100), reverse=True)
for val, i, j in lst[:14]:
    print(f'   {N[i]:12s} > {N[j]:12s} {val:+.3f}  (n {pc[(min(i, j), max(i, j))]})')
ours = [11, 0, 6, 2, 9]
print('our five against each enemy champion (sum of our counter terms; negative = it counters us):')
for e in sorted(range(12), key=lambda e: sum(D[o, e] for o in ours if o != e)):
    print(f'   vs {N[e]:12s} {sum(D[o, e] for o in ours if o != e):+.3f}')
json.dump({'D': D.tolist(), 'names': N}, open('/root/games/matchups.json', 'w'))
