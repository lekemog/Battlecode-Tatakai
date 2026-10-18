"""Can a bot predict an opponent's style early? Tested on decoded top-vs-top replays.
Each game gives two rows: each team as the OBSERVER, the other as the OPPONENT.
Label (NOTES.md definition, at r250): the opponent is AGGRESSIVE if it killed >3 of the observer's champions
or spent >=25% of its champion-rounds in the observer's half; otherwise PASSIVE.
Early features use only what the observer's bot could sense by round R (60 and 100):
  stun_picks   - opponent draft: champions with a stun kit (known at round 0)
  seen_in_half - opponent champion-rounds inside our half AND within 8 tiles of one of our champions (vision proxy)
  near_spawn   - opponent's closest approach to our spawn centroid (tiles; lower = deeper)
  our_deaths   - our deaths so far
  their_banked - opponent's tributed gems (global score)
Reports per-feature AUC and a leave-one-game-out logistic model's accuracy and AUC.
usage: python tools/oppmodel.py DECODED_DIR   (reads top-replays/README.md for the game list)"""
import json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = sys.argv[1]
STUN = {0, 3, 6, 7, 9, 11}   # Ryth, Cassi, Prism, Marcella, Ren, Tavi (type ids as in howtheywin.py)
ROUNDS = (60, 100)

def games():
    for line in open(os.path.join(ROOT, 'top-replays', 'README.md'), encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) == 5 and c[4].startswith('`'):
            yield c[0], c[4].strip('`').replace('.repl26a', '')

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
        feats = {R_: {} for R_ in ROUNDS}
        seen = 0; near = 999; their_half = 0; their_total = 0
        stun = sum(1 for c in first['champions'] if c['team'] == op and c['type'] in STUN)
        for r in sorted(R):
            if r > 250: break
            x = R[r]
            mine = [c for c in x['champions'] if c['team'] == me and c['alive']]
            for c in x['champions']:
                if c['team'] != op or not c['alive']: continue
                p = c['position']
                in_our_half = cheb(p, cen[me]) < cheb(p, cen[op])
                their_total += 1; their_half += in_our_half
                if in_our_half and any(max(abs(p['x'] - m['position']['x']), abs(p['y'] - m['position']['y'])) <= 8 for m in mine):
                    seen += 1
                    near = min(near, cheb(p, cen[me]))
            for R_ in ROUNDS:
                if r <= R_:
                    feats[R_] = {'stun_picks': stun, 'seen_in_half': seen, 'near_spawn': near if near < 999 else 60,
                                 'our_deaths': sum(c['kda'][1] for c in x['champions'] if c['team'] == me),
                                 'their_banked': x['submittedGems'][op]}
        last = R[max(r for r in R if r <= 250)]
        kills_on_us = sum(c['kda'][1] for c in last['champions'] if c['team'] == me)
        share = their_half / max(1, their_total)
        out.append({'aggr': int(kills_on_us > 3 or share >= .25), 'aggr_half': int(share >= .25), 'kills_on_us': kills_on_us, 'half_share': share, 'feats': feats})
    return out

def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]; neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg: return float('nan')
    return sum((p > n) + .5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))

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

def main():
    data = []
    for mp, gid in games():
        p = os.path.join(DEC, gid + '.json')
        if not os.path.exists(p): continue
        for row in rows_for(p): row.update(map=mp, game=gid); data.append(row)
    for label in ('aggr', 'aggr_half'):
        print(f'\n########## LABEL {label}: ' + ('kills on us >3 OR >=25% of time in our half (NOTES.md)' if label == 'aggr' else '>=25% of time in our half only (no deaths in the label)'))
        evaluate(data, label)
    json.dump(data, open(os.path.join(ROOT, 'results', 'kurians', 'oppmodel_rows.json'), 'w'), indent=0)

def evaluate(data, label):
    y = [r[label] for r in data]
    print(f'{len(data) // 2} games, {len(data)} observer rows; aggressive opponents: {sum(y)} ({sum(y) / len(y):.0%})')
    print(f"  label parts: kills_on_us>3 in {sum(r['kills_on_us'] > 3 for r in data)}, half_share>=25% in {sum(r['half_share'] >= .25 for r in data)}")
    names = ['stun_picks', 'seen_in_half', 'near_spawn', 'our_deaths', 'their_banked']
    for R_ in ROUNDS:
        print(f'\n--- signals by round {R_} (AUC: 0.5 = no information, 1.0 = perfect; near_spawn is negated so higher = deeper) ---')
        for n in names:
            s = [(-r['feats'][R_][n] if n == 'near_spawn' else r['feats'][R_][n]) for r in data]
            print(f'  {n:13} AUC {auc(s, y):.2f}   mean aggressive {sum(v for v, l in zip(s, y) if l) / max(1, sum(y)):7.1f}   passive {sum(v for v, l in zip(s, y) if not l) / max(1, len(y) - sum(y)):7.1f}')
        # leave-one-GAME-out logistic regression on standardised features
        raw = [[(-r['feats'][R_][n] if n == 'near_spawn' else r['feats'][R_][n]) for n in names] for r in data]
        mu = [sum(c) / len(c) for c in zip(*raw)]; sd = [max(1e-9, (sum((v - m) ** 2 for v in c) / len(c)) ** .5) for c, m in zip(zip(*raw), mu)]
        X = [[(v - m) / s for v, m, s in zip(row, mu, sd)] for row in raw]
        preds = [None] * len(X)
        gids = sorted({r['game'] for r in data})
        for g in gids:
            tr = [i for i, r in enumerate(data) if r['game'] != g]; te = [i for i, r in enumerate(data) if r['game'] == g]
            w = fit([X[i] for i in tr], [y[i] for i in tr])
            for i in te:
                z = w[0] + sum(a * b for a, b in zip(w[1:], X[i])); preds[i] = 1 / (1 + math.exp(-z))
        acc = sum((p >= .5) == bool(t) for p, t in zip(preds, y)) / len(y)
        base = max(sum(y), len(y) - sum(y)) / len(y)
        confident = [(p, t) for p, t in zip(preds, y) if p >= .75 or p <= .25]
        cacc = sum((p >= .5) == bool(t) for p, t in confident) / max(1, len(confident))
        print(f'  COMBINED (held-out games): accuracy {acc:.0%} vs always-guess-majority {base:.0%}; AUC {auc(preds, y):.2f}; '
              f'confident calls (p<=.25 or >=.75): {len(confident)}/{len(y)} rows, {cacc:.0%} correct')
        w = fit(X, y)
        print('  weights (standardised):', ', '.join(f'{n} {v:+.2f}' for n, v in zip(names, w[1:])))

if __name__ == '__main__':
    main()
