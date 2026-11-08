"""train.py DATA.npz [DATA.npz ...] [--hidden 32,16] [--epochs 30] [--write bots/<bot>] : death-hazard models, numpy only.

Compares, on replays held out by match (5 folds by replay id):
  * the current bot model (bots/v51d/src/hazard_model.h weights, logistic) as shipped;
  * logistic regression refitted on this data;
  * an MLP (ReLU hidden layers, sigmoid output, Adam, class-balanced loss).
Reports AUC and, at the bot's threshold (0.2), precision/recall. --write exports the MLP fitted on all data to
<bot>/src/hazard_mlp.h (inference ~1.5K multiply-adds per call).
"""
import os
import re
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def auc(y, p):
    o = np.argsort(p)
    r = np.empty(len(p)); r[o] = np.arange(1, len(p) + 1)
    pos = y > 0.5
    n1, n0 = pos.sum(), (~pos).sum()
    return (r[pos].sum() - n1 * (n1 + 1) / 2) / max(1, n1 * n0)


def shipped_weights():
    s = open(os.path.join(REPO, 'bots', 'v51d', 'src', 'hazard_model.h')).read()
    w = re.search(r'kWeights\[kFeatures\] = \{([^}]*)\}', s).group(1)
    return np.array([float(x.strip().rstrip('f')) for x in w.split(',') if x.strip()])


def sig(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


class MLP:
    def __init__(self, sizes, seed=0):
        rng = np.random.RandomState(seed)
        self.W = [rng.randn(a, b).astype(np.float32) * np.sqrt(2.0 / a) for a, b in zip(sizes[:-1], sizes[1:])]
        self.b = [np.zeros(b, np.float32) for b in sizes[1:]]

    def forward(self, X):
        hs = [X]
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            z = hs[-1] @ W + b
            hs.append(np.maximum(z, 0) if i < len(self.W) - 1 else z)
        return hs

    def predict(self, X):
        return sig(self.forward(X)[-1][:, 0])

    def fit(self, X, y, epochs=30, lr=2e-3, batch=512, l2=1e-4, seed=0):
        rng = np.random.RandomState(seed)
        params = self.W + self.b
        m = [np.zeros_like(p) for p in params]; v = [np.zeros_like(p) for p in params]
        pw = (1 - y.mean()) / max(1e-6, y.mean())  # balance classes
        t = 0
        for ep in range(epochs):
            idx = rng.permutation(len(y))
            for s in range(0, len(y), batch):
                bi = idx[s:s + batch]
                hs = self.forward(X[bi])
                p = sig(hs[-1][:, 0])
                wt = np.where(y[bi] > 0.5, pw, 1.0)
                g = ((p - y[bi]) * wt / wt.sum())[:, None].astype(np.float32)
                gW, gb = [None] * len(self.W), [None] * len(self.b)
                for i in range(len(self.W) - 1, -1, -1):
                    gW[i] = hs[i].T @ g + l2 * self.W[i]
                    gb[i] = g.sum(0)
                    if i > 0:
                        g = (g @ self.W[i].T) * (hs[i] > 0)
                grads = gW + gb
                t += 1
                for j, (pp, gg) in enumerate(zip(params, grads)):
                    m[j] = 0.9 * m[j] + 0.1 * gg; v[j] = 0.999 * v[j] + 0.001 * gg * gg
                    pp -= lr * (m[j] / (1 - 0.9 ** t)) / (np.sqrt(v[j] / (1 - 0.999 ** t)) + 1e-8)
        return self


def main():
    args = sys.argv[1:]
    hidden, epochs, write = [32, 16], 30, None
    files = []
    while args:
        if args[0] == '--hidden': hidden = [int(x) for x in args[1].split(',')]; args = args[2:]
        elif args[0] == '--epochs': epochs = int(args[1]); args = args[2:]
        elif args[0] == '--write': write = args[1]; args = args[2:]
        else: files.append(args[0]); args = args[1:]
    Xs, ys, gs, off = [], [], [], 0
    for f in files:
        D = np.load(f)
        Xs.append(D['X']); ys.append(D['y']); gs.append(D['g'] + off); off = gs[-1].max() + 1
    X = np.concatenate(Xs); y = np.concatenate(ys); g = np.concatenate(gs)
    print(f'rows {len(y)}  positives {int(y.sum())} ({y.mean():.3%})  replays {len(np.unique(g))}')
    ws = shipped_weights()
    p_ship = sig(X @ ws)
    print(f'shipped logistic (v51d): AUC {auc(y, p_ship):.4f}')
    Xn = X[:, 1:]  # drop the bias column for the MLP
    mu, sd = Xn.mean(0), Xn.std(0) + 1e-6
    Z = ((Xn - mu) / sd).astype(np.float32)
    groups = np.unique(g); rng = np.random.RandomState(0); rng.shuffle(groups)
    folds = np.array_split(groups, 5)
    p_lr = np.zeros(len(y)); p_mlp = np.zeros(len(y))
    for k, fg in enumerate(folds):
        te = np.isin(g, fg); tr = ~te
        lr = MLP([Z.shape[1], 1], seed=k).fit(Z[tr], y[tr], epochs=epochs)
        p_lr[te] = lr.predict(Z[te])
        mlp = MLP([Z.shape[1]] + hidden + [1], seed=k).fit(Z[tr], y[tr], epochs=epochs)
        p_mlp[te] = mlp.predict(Z[te])
    print(f'held-out by match: shipped AUC {auc(y, p_ship):.4f}  refit logistic AUC {auc(y, p_lr):.4f}  MLP {hidden} AUC {auc(y, p_mlp):.4f}')
    # at matched alarm rate: how many of the deaths does each flag, when it raises the same number of alarms as shipped@0.2
    alarms = (p_ship >= 0.2).mean()
    for name, p in (('shipped', p_ship), ('refit', p_lr), ('mlp', p_mlp)):
        thr = np.quantile(p, 1 - alarms)
        f = p >= thr
        print(f'  {name:8s} at {alarms:.1%} alarms: recall {y[f].sum() / y.sum():.3f}  precision {y[f].mean():.3f}  (threshold {thr:.3f})')
    if write:
        mlp = MLP([Z.shape[1]] + hidden + [1], seed=0).fit(Z, y, epochs=epochs)
        thr = float(np.quantile(mlp.predict(Z), 1 - alarms))
        fmt = lambda a: ', '.join(f'{x:.6g}f' for x in np.asarray(a).ravel())
        with open(os.path.join(write, 'src', 'hazard_mlp.h'), 'w') as out:
            out.write('#pragma once\n// Generated by tools/hazardml/train.py: MLP P(killed by an enemy within 10 rounds) on the 19 hazard\n'
                      f'// features (no bias column), standardised. Layers {[Z.shape[1]] + hidden + [1]}, trained on {len(np.unique(g))} engine-3 replays,\n'
                      f'// {len(y)} rows. kAlarm = threshold giving the shipped model\'s alarm rate ({alarms:.3%}).\n#include <array>\nnamespace mb::hazard_mlp {{\n')
            out.write(f'inline constexpr int kIn = {Z.shape[1]};\n')
            out.write(f'inline constexpr float kAlarm = {thr:.6g}f;\n')
            out.write(f'inline constexpr std::array<float, {len(mu)}> kMean{{ {fmt(mu)} }};\n')
            out.write(f'inline constexpr std::array<float, {len(sd)}> kStd{{ {fmt(sd)} }};\n')
            for i, (W, b) in enumerate(zip(mlp.W, mlp.b)):
                out.write(f'inline constexpr int kRows{i} = {W.shape[0]}, kCols{i} = {W.shape[1]};\n')
                out.write(f'inline constexpr std::array<float, {W.size}> kW{i}{{ {fmt(W)} }};  // row-major [in][out]\n')
                out.write(f'inline constexpr std::array<float, {b.size}> kB{i}{{ {fmt(b)} }};\n')
            out.write(f'inline constexpr int kLayers = {len(mlp.W)};\n}} // namespace mb::hazard_mlp\n')
        print('wrote', os.path.join(write, 'src', 'hazard_mlp.h'), 'threshold', thr)


if __name__ == '__main__':
    main()
