"""Danger model dataset + training: P(champion dies within H rounds) from features a bot sees.
Vision is approximated as Chebyshev distance <= 8 (walls/bushes ignored, so slightly optimistic)."""
import json, glob, os, math, sys
import numpy as np
H = 30
exec(open('/home/claude/tools/replay/dataset.py').read().split('FEATS =')[0])   # load_map, HASH
FN = ['n_en8', 'en_str8', 'en_hpfrac8', 'near_en', 'n_en4', 'n_al5', 'al_str5', 'my_hp', 'my_hpabs', 'my_str', 'carry',
      'side', 'kills_on_us_rate', 'inv_rate', 'score_gap', 'round', 'str_ratio']
def build():
    meta = json.load(open('/home/claude/data/rep/meta.json'))
    maps = {}; X = []; Y = []; MID = []
    for p in sorted(glob.glob('/home/claude/data/rep/json/*.json')):
        mid = os.path.basename(p)[:-5]
        if mid not in meta: continue
        name = meta[mid]['map']
        if name not in maps: maps[name] = load_map(name)
        M = maps[name]
        try: d = json.load(open(p))
        except Exception: continue
        R = d['rounds']; T = len(R)
        if T < 80: continue
        sp = M['spawnD']
        if sp is None:
            s2 = [[(c['position']['x'], c['position']['y']) for c in R[1]['champions'] if c['team'] == tm and c.get('position')] for tm in (0, 1)]
            if not s2[0] or not s2[1]: continue
            sp = [M['bfs'](s2[0]), M['bfs'](s2[1])]
        nC = min(len(r['champions']) for r in R[10:])
        alive = np.array([[bool(r['champions'][i].get('alive')) if i < len(r['champions']) else False for i in range(nC)] for r in R])
        teams = [R[10]['champions'][i]['team'] for i in range(nC)]
        # cumulative deaths per team and invasion sightings
        deaths_t = np.zeros((T, 2)); inv_t = np.zeros((T, 2))
        for t in range(1, T):
            deaths_t[t] = deaths_t[t - 1]; inv_t[t] = inv_t[t - 1]
            for i in range(nC):
                if t > 10 and alive[t - 1, i] and not alive[t, i]: deaths_t[t, teams[i]] += 1
            for c in R[t]['champions'][:nC] if t >= 10 else []:
                if c.get('alive') and c.get('position') and c['team'] in (0, 1):
                    x, y = c['position']['x'], c['position']['y']
                    tm = c['team']; other = 1 - tm
                    # enemy of 'other' standing in other's half
                    if sp[other][x, y] < sp[tm][x, y]: inv_t[t, other] += 1.0 / max(1, nC // 2)
        for t in range(20, T - H, 3):
            r = R[t]
            cs = r['champions'][:nC]
            for i, c in enumerate(cs):
                if not c.get('alive') or not c.get('position') or c['team'] not in (0, 1): continue
                tm = c['team']; px, py = c['position']['x'], c['position']['y']
                en = [o for o in cs if o['team'] != tm and o.get('alive') and o.get('position')]
                al = [o for o in cs if o['team'] == tm and o is not c and o.get('alive') and o.get('position')]
                def dd(o): return max(abs(o['position']['x'] - px), abs(o['position']['y'] - py))
                e8 = [o for o in en if dd(o) <= 8]; e4 = [o for o in en if dd(o) <= 4]; a5 = [o for o in al if dd(o) <= 5]
                st = lambda o: o['strength']['effective'] + 0.5 * o['focus']['effective']
                es = sum(st(o) for o in e8); as_ = sum(st(o) for o in a5) + st(c)
                f = [len(e8), es / 100, (sum(o['health'] for o in e8) / max(1, sum(o['maxHealth'] for o in e8))) if e8 else 1.0,
                     min([dd(o) for o in e8] or [9]) / 9, len(e4), len(a5), as_ / 100, c['health'] / max(1, c['maxHealth']), c['health'] / 1000,
                     st(c) / 100, (c.get('gems') or 0) / 100, sp[tm][px, py] / max(1, sp[tm][px, py] + sp[1 - tm][px, py]),
                     deaths_t[t, tm] / max(1, t) * 100, inv_t[t, tm] / max(1, t) * 100,
                     (r['submittedGems'][1 - tm] - r['submittedGems'][tm]) / 500, t / 1000, es / max(1, as_)]
                died = (not alive[t + 1:t + H + 1, i].all())
                X.append(f); Y.append(died); MID.append(mid)
        print(mid, name, len(X), flush=True)
    X = np.array(X, np.float32); Y = np.array(Y, np.int8)
    np.savez('/home/claude/data/rep/danger.npz', X=X, Y=Y, MID=np.array(MID))
def train():
    D = np.load('/home/claude/data/rep/danger.npz'); X, Y, MID = D['X'], D['Y'].astype(float), D['MID']
    def ex(X):
        n_en8, en_str8, en_hpf, near_en, n_en4, n_al5, al_str5, my_hp, my_hpabs, my_str, carry, side, kr, ir, gap, rnd, sr = X.T
        return np.stack([n_en8, en_str8, en_hpf, near_en, n_en4, n_al5, al_str5, my_hp, my_hpabs, my_str, carry, side, kr, ir, gap, rnd,
                         np.log1p(sr), n_en8 * (1 - my_hp), side * kr, side * ir, en_str8 / (al_str5 + 0.1), (n_en8 > 0) * 1.0], 1)
    Z = ex(X); mu, sd = Z.mean(0), Z.std(0) + 1e-6; Zs = (Z - mu) / sd
    ms = sorted(set(MID)); rng = np.random.RandomState(1); rng.shuffle(ms); test = set(ms[:max(1, len(ms) // 5)])
    te = np.array([m in test for m in MID]); tr = ~te
    w = np.zeros(Zs.shape[1]); b = math.log(Y[tr].mean() / (1 - Y[tr].mean()))
    for it in range(600):
        p = 1 / (1 + np.exp(-(Zs[tr] @ w + b)))
        g = Zs[tr].T @ (p - Y[tr]) / tr.sum() + 1e-3 * w; gb = (p - Y[tr]).mean()
        w -= 0.5 * g; b -= 0.5 * gb
    def auc(s, y):
        o = np.argsort(s); r = np.empty(len(s)); r[o] = np.arange(len(s)); pos = y == 1
        return (r[pos].sum() - pos.sum() * (pos.sum() - 1) / 2) / (pos.sum() * (~pos).sum())
    pt = 1 / (1 + np.exp(-(Zs[te] @ w + b)))
    print('rows', len(Y), 'base rate %.3f' % Y.mean(), 'test AUC %.3f' % auc(pt, Y[te]), 'baseline(enemies near) AUC %.3f' % auc(X[te, 0] + X[te, 4], Y[te]))
    names = FN[:16] + ['log_str_ratio', 'en*lowhp', 'side*kills', 'side*inv', 'enstr/alstr', 'any_enemy']
    for n, v in sorted(zip(names, w), key=lambda t: -abs(t[1]))[:12]: print(f'  {n:14} {v:+.3f}')
    # calibration by decile
    q = np.quantile(pt, np.linspace(0, 1, 11))
    print('calibration (pred vs actual):', [(round(float(pt[(pt >= q[k]) & (pt <= q[k + 1])].mean()), 3), round(float(Y[te][(pt >= q[k]) & (pt <= q[k + 1])].mean()), 3)) for k in range(0, 10, 3)])
    json.dump({'w': w.tolist(), 'b': b, 'mu': mu.tolist(), 'sd': sd.tolist(), 'names': names}, open('/home/claude/data/rep/danger_model.json', 'w'))
if 'build' in sys.argv: build()
if 'train' in sys.argv: train()
