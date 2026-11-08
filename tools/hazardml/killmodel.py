"""killmodel.py : when we commit to a kill chance, do we have the numbers, and how likely is the kill?
Commits = opportunities (offense.py definition) where our side closed in or hit within 3 rounds. Features at the commit:
our champions within 6 of the target, its allies within 6 of it, local power ratio (ours within 6 / its side within 6), target
health fraction, target distance to its own spawn, whether one of ours stands between it and its spawn (cut-off).
Fits a logistic kill model on top-team commits (held-out by game), then scores our commits with it."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import offense, train

def cheb(a, b): return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))
pw = lambda o: float(o.get('maxHealth', 1000)) * (float(o.get('strength', {}).get('effective', 0)) + float(o.get('focus', {}).get('effective', 0)))

def commits(path, only):
    d = json.load(open(path)); R = {r['round']: r for r in d['rounds'] if r.get('phase') == 1 and r['round'] >= 1}
    keys = sorted(R); first = R[keys[0]]; spawn = {}
    for t in (0, 1):
        pts = [c['position'] for c in first['champions'] if c['team'] == t and 'position' in c]
        spawn[t] = {'x': round(sum(p['x'] for p in pts) / len(pts)), 'y': round(sum(p['y'] for p in pts) / len(pts))}
    hp_hist = {}
    for k in keys:
        for c in R[k]['champions']: hp_hist[(c['team'], c['entity']['index'], k)] = c['health'] if c.get('alive') else -1
    w = train.shipped_weights(); last = {}; out = []
    for k in keys:
        if k + 10 not in R: continue
        ch = [c for c in R[k]['champions'] if c.get('alive') and 'position' in c]
        lat = {(c['team'], c['entity']['index']): c for c in R[k + 3]['champions']}
        for v in ch:
            at = 1 - v['team']
            if only is not None and at != only: continue
            if cheb(v['position'], spawn[v['team']]) <= 2: continue
            ours = [o for o in ch if o['team'] == at and cheb(o['position'], v['position']) <= 6]
            if not ours: continue
            x = offense.feats(v, R[k], spawn, k, hp_hist)
            if x is None or train.sig(x @ w) < 0.3: continue
            key = (v['team'], v['entity']['index'])
            if last.get(key, -99) >= k - 5: last[key] = k; continue
            last[key] = k
            v2 = lat.get(key)
            hit = v2 is not None and (not v2.get('alive') or v2['health'] < v['health'])
            closer = any(lat.get((o['team'], o['entity']['index'])) and 'position' in lat[(o['team'], o['entity']['index'])] and v2 is not None and 'position' in v2 and
                         cheb(lat[(o['team'], o['entity']['index'])]['position'], v2['position']) < cheb(o['position'], v['position']) for o in ours)
            if not (hit or closer): continue
            theirs = [o for o in ch if o['team'] == v['team'] and o is not v and cheb(o['position'], v['position']) <= 6]
            killed = False
            for j in range(k + 1, k + 11):
                c2 = [c for c in R[j]['champions'] if (c['team'], c['entity']['index']) == key]
                if c2 and not c2[0].get('alive'): killed = True; break
            ds = cheb(v['position'], spawn[v['team']])
            cut = int(any(cheb(o['position'], spawn[v['team']]) < ds for o in ours))
            ratio = sum(pw(o) for o in ours) / max(1.0, pw(v) + sum(pw(o) for o in theirs))
            out.append([len(ours), len(theirs) + 1, np.log(max(1e-3, ratio)), v['health'] / max(1, v['maxHealth']), ds / 40.0, cut, float(killed)])
    return out

side_of = {}
for line in open(os.path.expanduser('~/games/ours/list.txt')):
    mid, opp, side, mp = line.split(); side_of[mid] = 0 if side == 'a' else 1
data = {}
for label, path, us in (('us', '/root/games/ours_dec', True), ('top', '/root/games/dec', False)):
    rows, g = [], []
    for gi, f in enumerate(sorted(glob.glob(path + '/*.json'))):
        mid = os.path.basename(f)[:-5]
        if us and mid not in side_of: continue
        try: r = commits(f, side_of[mid] if us else None)
        except Exception: continue
        rows += r; g += [gi] * len(r)
    data[label] = (np.array(rows), np.array(g))
for label, (A, g) in data.items():
    adv = A[:, 0] - A[:, 1]
    print(f'{label}: {len(A)} commits, kill rate {A[:, 6].mean():.3f}; our attackers {A[:, 0].mean():.2f} vs target side {A[:, 1].mean():.2f}; '
          f'outnumbered {np.mean(adv < 0):.0%} even {np.mean(adv == 0):.0%} ahead {np.mean(adv > 0):.0%}; target hp {A[:, 3].mean():.2f}; target spawn dist {A[:, 4].mean() * 40:.1f}; cut-off {A[:, 5].mean():.0%}')
    for name, sel in (('outnumbered', adv < 0), ('even', adv == 0), ('+1', adv == 1), ('+2 or more', adv >= 2)):
        if sel.sum() >= 15: print(f'     {name:11s} n {int(sel.sum()):5d}  kill rate {A[sel, 6].mean():.3f}')
# logistic kill model on top commits, held out by game
A, g = data['top']; X = np.c_[np.ones(len(A)), A[:, :6]]; y = A[:, 6]
mu, sd = X[:, 1:].mean(0), X[:, 1:].std(0) + 1e-6
Z = np.c_[np.ones(len(A)), (X[:, 1:] - mu) / sd]
def fitlr(Z, y, lam=1.0):
    w = np.zeros(Z.shape[1])
    for _ in range(300):
        p = 1 / (1 + np.exp(-Z @ w)); H = Z.T @ (Z * (p * (1 - p))[:, None]) + lam * np.eye(len(w)); w -= np.linalg.solve(H, Z.T @ (p - y) + lam * w)
    return w
games = np.unique(g); rng = np.random.RandomState(0); rng.shuffle(games); P = np.zeros(len(y))
for fold in np.array_split(games, 5):
    te = np.isin(g, fold); w = fitlr(Z[~te], y[~te]); P[te] = 1 / (1 + np.exp(-Z[te] @ w))
print(f'top-team kill model held-out AUC {train.auc(y, P):.3f}')
w = fitlr(Z, y)
names = ['bias', 'our attackers', 'target side', 'log power ratio', 'target hp', 'target spawn dist', 'cut-off']
print('standardised effects: ' + ', '.join(f'{n} {v:+.2f}' for n, v in zip(names, w)))
B, _ = data['us']; Zu = np.c_[np.ones(len(B)), (B[:, :6] - mu) / sd]; Pu = 1 / (1 + np.exp(-Zu @ w))
print(f'our commits scored by the top-team model: mean predicted kill {Pu.mean():.3f} vs actual {B[:, 6].mean():.3f}; top commits predicted {P.mean():.3f} actual {y.mean():.3f}')
for lo, hi in ((0, .15), (.15, .3), (.3, .5), (.5, 1.01)):
    s = (Pu >= lo) & (Pu < hi); t = (P >= lo) & (P < hi)
    print(f'   predicted {lo:.2f}-{hi:.2f}: our share {s.mean():.0%} (actual {B[s, 6].mean() if s.any() else float("nan"):.2f})   top share {t.mean():.0%} (actual {y[t].mean() if t.any() else float("nan"):.2f})')
