"""Conditional-logit (softmax over candidate camps) imitation model. Held-out by match."""
import numpy as np, json, sys
D = np.load('/home/claude/data/rep/dataset.npz')
X, y, gid = D['X'], D['y'], D['gid']
meta = [json.loads(m) for m in D['meta']]
FEATS = ['logd', 'wait', 'gems', 'gold', 'hpfrac_grp', 'clear', 'danger', 'altar_d', 'side', 'ally_near', 'enemy_near',
         'rate', 'my_hp', 'carry', 'alive', 'cur']
# interactions that let the model trade distance against value and state
def expand(X):
    logd, wait, gems, gold, hpf, clear, danger, altd, side, an, en, rate, myhp, carry, alive, cur = X.T
    cols = [logd, wait, gems, gold, hpf, clear, danger, altd, side, an, en, rate, alive,
            danger * (1 - myhp), carry * altd, logd * carry, side * en, np.log1p(rate * 50)]
    return np.stack(cols, 1)
NAMES = ['logd', 'wait', 'gems', 'gold', 'hpfrac', 'clear', 'danger', 'altar_d', 'side', 'ally_near', 'enemy_near', 'rate', 'alive',
         'danger*lowhp', 'carry*altar_d', 'logd*carry', 'side*enemy_near', 'log_rate']
Z = expand(X)
mu, sd = Z.mean(0), Z.std(0) + 1e-6
Zs = (Z - mu) / sd
matches = sorted(set(m[0] for m in meta))
rng = np.random.RandomState(0); rng.shuffle(matches)
test_m = set(matches[:max(1, len(matches) // 5)])
is_test_g = np.array([meta[g][0] in test_m for g in range(len(meta))])
def fit(Zs, idx, l2=1e-3, iters=400, lr=0.5):
    w = np.zeros(Zs.shape[1])
    g_idx = gid[idx]; Zi = Zs[idx]; yi = y[idx]
    ng = gid.max() + 1
    for it in range(iters):
        s = Zi @ w
        smax = np.full(ng, -1e9); np.maximum.at(smax, g_idx, s)
        e = np.exp(s - smax[g_idx]); den = np.zeros(ng); np.add.at(den, g_idx, e)
        p = e / den[g_idx]
        grad = Zi.T @ (p - yi) / (yi.sum()) + l2 * w
        w -= lr * grad
    return w
def acc(w, idx, score=None):
    s = Zs[idx] @ w if score is None else score[idx]
    g_idx = gid[idx]; yi = y[idx]
    best = {}
    for k, (g, v) in enumerate(zip(g_idx, s)):
        if g not in best or v > best[g][0]: best[g] = (v, yi[k])
    return np.mean([b[1] for b in best.values()]), len(best)
tr = np.where(~is_test_g[gid])[0]; te = np.where(is_test_g[gid])[0]
w = fit(Zs, tr)
print('model  train acc %.3f (n=%d)  test acc %.3f (n=%d)' % (*acc(w, tr), *acc(w, te)))
print('baseline our-rate-formula test acc %.3f' % acc(None, te, score=X[:, 11])[0])
print('baseline nearest-camp     test acc %.3f' % acc(None, te, score=-X[:, 0])[0])
print('random expected           %.3f' % np.mean([1 / np.sum(gid == g) for g in set(gid[te])]))
for n, v in sorted(zip(NAMES, w), key=lambda t: -abs(t[1])): print(f'  {n:16} {v:+.3f}')
# final fit on everything, export
wall = fit(Zs, np.arange(len(y)))
json.dump({'names': NAMES, 'w': wall.tolist(), 'mu': mu.tolist(), 'sd': sd.tolist()}, open('/home/claude/data/rep/model.json', 'w'))
