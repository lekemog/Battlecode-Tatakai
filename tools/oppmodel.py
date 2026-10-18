"""Can a bot predict an opponent's FUTURE style from what it senses early? Tested on decoded top-vs-top replays.
Each game gives two rows: each team as the OBSERVER, the other as the OPPONENT.

Features (what the observer's bot could sense by round R, R = 60 or 100):
  stun_picks   - opponent draft: champions with a stun kit (known at round 0)
  seen_in_half - opponent champion-rounds in our half AND within 8 tiles of one of our champions. A vision PROXY:
                 walls, bushes and wards are not modelled, so validate against real observations before runtime use.
  near_spawn   - opponent's closest approach to our spawn centroid, Chebyshev tiles (lower = deeper)
  our_deaths   - our deaths so far
  their_banked - opponent's tributed gems (global score)
Label (future-only, review on #22): the opponent spends >=25% of its champion-rounds in our HALF during rounds R+1..250.
"Half" = nearer our spawn centroid than theirs. This is not the "enemy third" used by tools/openings.py.

Evaluation:
  - standardisation and logistic regression are fitted on training rows only (inside each fold)
  - two hold-out schemes: leave-one-GAME-out, and leave-one-OPPONENT-TEAM-out
  - per-map AUC of each single feature, and precision/recall at fixed model-probability thresholds
usage: python tools/oppmodel.py DECODED_DIR        (game list from top-replays/README.md)"""
import json, math, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = sys.argv[1]
STUN = {0, 3, 6, 7, 9, 11}   # Ryth, Cassi, Prism, Marcella, Ren, Tavi (type ids as in howtheywin.py)
ROUNDS = (60, 100)
NAMES = ['stun_picks', 'seen_in_half', 'near_spawn', 'our_deaths', 'their_banked']
team_name = lambda s: re.sub(r'\s*\(#\d+\)\s*$', '', s)

def games():
    for line in open(os.path.join(ROOT, 'top-replays', 'README.md'), encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) == 5 and c[4].startswith('`'):
            yield c[0], c[4].strip('`').replace('.repl26a', ''), team_name(c[1]), team_name(c[2])

def rows_for(path):
    d = json.load(open(path, encoding='utf-8'))
    R = {}
    for x in d['rounds']:
        if x['phase'] != 12: R[x['round']] = x
    first = R[min(R)]
    cen = {}
    for t in (0, 1):
        ps = [c['position'] for c in first['champions'] if c['team'] == t]
        cen[t] = (sum(p['x'] for p in ps) / len(ps), sum(p['y'] for p in ps) / len(ps))
    cheb = lambda p, q: max(abs(p['x'] - q[0]), abs(p['y'] - q[1]))
    out = []
    for me in (0, 1):
        op = 1 - me
        stun = sum(1 for c in first['champions'] if c['team'] == op and c['type'] in STUN)
        feats = {}; seen = 0; near = 999
        half = {R_: [0, 0] for R_ in ROUNDS}      # future window R_+1..250: [rounds in our half, total]
        for r in sorted(R):
            if r > 250: break
            x = R[r]
            mine = [c for c in x['champions'] if c['team'] == me and c['alive']]
            for c in x['champions']:
                if c['team'] != op or not c['alive']: continue
                p = c['position']; ours = cheb(p, cen[me]) < cheb(p, cen[op])
                for R_ in ROUNDS:
                    if r > R_: half[R_][0] += ours; half[R_][1] += 1
                if ours and any(max(abs(p['x'] - m['position']['x']), abs(p['y'] - m['position']['y'])) <= 8 for m in mine):
                    seen += 1; near = min(near, cheb(p, cen[me]))
            for R_ in ROUNDS:
                if r <= R_:
                    feats[R_] = {'stun_picks': stun, 'seen_in_half': seen, 'near_spawn': near if near < 999 else 60,
                                 'our_deaths': sum(c['kda'][1] for c in x['champions'] if c['team'] == me),
                                 'their_banked': x['submittedGems'][op]}
        out.append({'observer': me, 'feats': feats,
                    'label': {R_: int(half[R_][0] / max(1, half[R_][1]) >= .25) for R_ in ROUNDS},
                    'future_share': {R_: half[R_][0] / max(1, half[R_][1]) for R_ in ROUNDS}})
    return out

def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]; neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg: return float('nan')
    return sum((p > n) + .5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))

def vec(row, R_):
    return [(-row['feats'][R_][n] if n == 'near_spawn' else row['feats'][R_][n]) for n in NAMES]   # higher = more invasive

def fit(X, y, iters=600, lr=.3, l2=.01):
    w = [0.0] * (len(X[0]) + 1)
    for _ in range(iters):
        g = [0.0] * len(w)
        for x, t in zip(X, y):
            z = w[0] + sum(a * b for a, b in zip(w[1:], x)); p = 1 / (1 + math.exp(-max(-30, min(30, z))))
            g[0] += p - t
            for k, v in enumerate(x): g[k + 1] += (p - t) * v
        for k in range(len(w)): w[k] -= lr * (g[k] / len(X) + (l2 * w[k] if k else 0))
    return w

def held_out(data, R_, group_of):
    """Predictions for every row from a model fitted (scaling included) without that row's group."""
    raw = [vec(r, R_) for r in data]; y = [r['label'][R_] for r in data]; preds = [None] * len(data)
    for g in sorted({group_of(r) for r in data}):
        tr = [i for i, r in enumerate(data) if group_of(r) != g]; te = [i for i, r in enumerate(data) if group_of(r) == g]
        if sum(y[i] for i in tr) == 0: continue
        cols = list(zip(*[raw[i] for i in tr]))
        mu = [sum(c) / len(c) for c in cols]; sd = [max(1e-9, (sum((v - m) ** 2 for v in c) / len(c)) ** .5) for c, m in zip(cols, mu)]
        z = lambda row: [(v - m) / s for v, m, s in zip(row, mu, sd)]
        w = fit([z(raw[i]) for i in tr], [y[i] for i in tr])
        for i in te:
            s = w[0] + sum(a * b for a, b in zip(w[1:], z(raw[i]))); preds[i] = 1 / (1 + math.exp(-s))
    return preds, y

def report(preds, y, label):
    keep = [(p, t) for p, t in zip(preds, y) if p is not None]
    p_, y_ = [k[0] for k in keep], [k[1] for k in keep]
    print(f'  {label}: AUC {auc(p_, y_):.2f}  (rows scored {len(keep)})')
    print(f"    {'alert if p >=':>14} {'alerts':>6} {'precision':>9} {'recall':>6}")
    for th in (.1, .2, .3, .5):
        a = [p >= th for p in p_]; tp = sum(1 for x, t in zip(a, y_) if x and t); n = sum(a)
        print(f'    {th:>14.1f} {n:>6} {tp / max(1, n):>9.0%} {tp / max(1, sum(y_)):>6.0%}')

def main():
    data = []
    for mp, gid, a, b in games():
        p = os.path.join(DEC, gid + '.json')
        if not os.path.exists(p): continue
        for row in rows_for(p):
            row.update(map=mp, game=gid, opponent=b if row['observer'] == 0 else a); data.append(row)
    print(f'{len({r["game"] for r in data})} games, {len(data)} observer rows, {len({r["opponent"] for r in data})} distinct opponent teams')
    for R_ in ROUNDS:
        y = [r['label'][R_] for r in data]
        print(f'\n===== features up to r{R_}; label = >=25% of rounds {R_ + 1}-250 in our half: {sum(y)} positives ({sum(y) / len(y):.0%}) =====')
        print('  single-feature AUC, pooled and per map (maps with >=2 positives):')
        maps = sorted({r['map'] for r in data if sum(x['label'][R_] for x in data if x['map'] == r['map']) >= 2})
        print(f"    {'feature':13} {'pooled':>6} " + ' '.join(f'{m[:9]:>9}' for m in maps))
        for k, n in enumerate(NAMES):
            line = f'    {n:13} {auc([vec(r, R_)[k] for r in data], y):6.2f} '
            for m in maps:
                sub = [r for r in data if r['map'] == m]
                line += f"{auc([vec(r, R_)[k] for r in sub], [r['label'][R_] for r in sub]):9.2f} "
            print(line)
        report(*held_out(data, R_, lambda r: r['game']), 'combined, leave-one-GAME-out')
        report(*held_out(data, R_, lambda r: r['opponent']), 'combined, leave-one-OPPONENT-TEAM-out')
    os.makedirs(os.path.join(ROOT, 'results', 'kurians'), exist_ok=True)
    json.dump(data, open(os.path.join(ROOT, 'results', 'kurians', 'oppmodel_rows.json'), 'w'), indent=0)

if __name__ == '__main__':
    main()
