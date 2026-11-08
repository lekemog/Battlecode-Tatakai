"""train.py : learned map draft for bots/v54m (playstyle choice from map features).

Data: $PROJ/feat/features.tsv (map, 22 features from mapfeat.h, dumped by the bot in the draft turn) and mirror.sh output folders
of each forced playstyle c<k> (or the v54 screen bots) against each opponent. Label per (map, comp, opponent): mean gem margin of
the comp over both sides (clipped to +-1000) and its win share.

Model: one ridge regression per comp, margin ~ standardised features (averaged over opponents). Policy: play the comp with the
highest predicted margin. Validation, what matters for unseen tournament maps:
  * leave-one-map-out (LOMO) and leave-one-family-out (LOFO: the 00/01/02/03/04/adgato map families, a stricter proxy);
  * realised held-out margin and wins of the chosen comp, against (a) always comp 0 (v51d) and (b) the best single comp chosen on
    the training folds only.
Writes bots/<bot>/src/draft_model.h with the model fitted on all maps when --write is given.
Usage: python3 -I tools/draftml/train.py [--lam 10] [--write bots/v54m]
"""
import glob
import json
import os
import sys

import numpy as np

PROJ = os.path.expanduser(os.environ.get('PROJ', '~/lab'))
NF = 22
# comp id -> folder name pattern per opponent (the v54 screen bots equal comps 0-3 against v51d)
SOURCES = {
    'v51d': {0: ['v54z', 'c0'], 1: ['v54a', 'c1'], 2: ['v54b', 'c2'], 3: ['v54c', 'c3'], 4: ['c4'], 5: ['c5']},
    'v50p1': {k: [f'c{k}'] for k in range(6)},
}


def load_features():
    feats = {}
    for line in open(os.path.join(PROJ, 'feat', 'features.tsv')):
        p = line.rstrip('\n').split('\t')
        feats[p[0]] = np.array([float(x) for x in p[1:1 + NF]])
    return feats


def load_labels():
    """labels[(map, comp, opp)] = (margin, win share)"""
    labels = {}
    for opp, comps in SOURCES.items():
        for k, names in comps.items():
            d = None
            for n in names:
                cand = os.path.join(PROJ, f'mirror_{n}_{opp}')
                if os.path.isdir(cand) and len(glob.glob(os.path.join(cand, '*.json'))) >= 200:
                    d, bot = cand, n
                    break
            if d is None:
                continue
            per = {}
            for f in glob.glob(os.path.join(d, '*.json')):
                if f.endswith('manifest.json'):
                    continue
                base = os.path.basename(f)[:-5]
                for a, b in ((bot, opp), (opp, bot)):
                    suf = f'_{a}_{b}'
                    if base.endswith(suf):
                        m = base[:-len(suf)]
                        cand_team = 'teamA' if a == bot else 'teamB'
                        break
                else:
                    continue
                try:
                    j = json.load(open(f))
                except Exception:
                    continue
                g = {t['team']: float(t['submittedGems']) for t in j['teams']}
                other = 'teamB' if cand_team == 'teamA' else 'teamA'
                margin = max(-1000.0, min(1000.0, g[cand_team] - g[other]))
                win = 1.0 if j['match']['outcome'] == cand_team else 0.0 if j['match']['outcome'] == other else 0.5
                per.setdefault(m, []).append((margin, win))
            for m, v in per.items():
                labels[(m, k, opp)] = (float(np.mean([x[0] for x in v])), float(np.mean([x[1] for x in v])))
    return labels


def family(m):
    return m[:2] if m[:2].isdigit() else m.split('-')[0]


def fit(X, y, lam):
    mu, sd = X.mean(0), X.std(0)
    sd[sd < 1e-6] = 1.0
    Z = (X - mu) / sd
    A = Z.T @ Z + lam * np.eye(Z.shape[1])
    w = np.linalg.solve(A, Z.T @ (y - y.mean()))
    return mu, sd, y.mean(), w


def main():
    lam = 10.0
    write = None
    a = sys.argv[1:]
    while a:
        if a[0] == '--lam': lam = float(a[1]); a = a[2:]
        elif a[0] == '--write': write = a[1]; a = a[2:]
        else: a = a[1:]
    feats = load_features()
    labels = load_labels()
    comps = sorted({k for (_, k, _) in labels})
    opps = sorted({o for (_, _, o) in labels})
    maps = sorted(m for m in feats if all((m, k, o) in labels for k in comps for o in opps))
    print(f'maps {len(maps)}  comps {comps}  opponents {opps}  lambda {lam}')
    M = {k: np.array([np.mean([labels[(m, k, o)][0] for o in opps]) for m in maps]) for k in comps}
    W = {k: np.array([np.mean([labels[(m, k, o)][1] for o in opps]) for m in maps]) for k in comps}
    X = np.array([feats[m] for m in maps])
    print('in-sample mean margin / win share per comp (avg over opponents):')
    for k in comps:
        print(f'  comp {k}: margin {M[k].mean():+7.1f}  win {W[k].mean():.3f}')
    oracle = np.mean([max(M[k][i] for k in comps) for i in range(len(maps))])
    print(f'  oracle (best comp per map, in-sample upper bound): margin {oracle:+.1f}')

    for name, groups in (('LOMO', [[i] for i in range(len(maps))]),
                         ('LOFO', [[i for i, m in enumerate(maps) if family(m) == f] for f in sorted({family(m) for m in maps})])):
        res = {'base': [], 'single': [], 'model': []}
        wins = {'base': [], 'single': [], 'model': []}
        picks = []
        for test in groups:
            train = [i for i in range(len(maps)) if i not in test]
            best_single = max(comps, key=lambda k: M[k][train].mean())
            models = {k: fit(X[train], M[k][train], lam) for k in comps}
            for i in test:
                pred = {k: models[k][2] + ((X[i] - models[k][0]) / models[k][1]) @ models[k][3] for k in comps}
                kk = max(comps, key=lambda k: pred[k])
                picks.append(kk)
                for key, c in (('base', 0), ('single', best_single), ('model', kk)):
                    res[key].append(M[c][i]); wins[key].append(W[c][i])
        n = len(res['base'])
        print(f'{name}: held-out margin / win share  base {np.mean(res["base"]):+.1f} / {np.mean(wins["base"]):.3f}   '
              f'best-single {np.mean(res["single"]):+.1f} / {np.mean(wins["single"]):.3f}   '
              f'model {np.mean(res["model"]):+.1f} / {np.mean(wins["model"]):.3f}   '
              f'(model - single: {np.mean(np.array(res["model"]) - np.array(res["single"])):+.1f} '
              f'+- {np.std(np.array(res["model"]) - np.array(res["single"])) / np.sqrt(n):.1f})  picks {np.bincount(picks, minlength=len(comps)).tolist()}')

    if write:
        models = {k: fit(X, M[k], lam) for k in comps}
        mu, sd = models[comps[0]][0], models[comps[0]][1]
        fmt = lambda v: ', '.join(f'{x:.6g}f' for x in v)
        with open(os.path.join(write, 'src', 'draft_model.h'), 'w') as out:
            out.write('#pragma once\n// Generated by tools/draftml/train.py (lambda %g, %d maps, comps %s, opponents %s): per-playstyle ridge\n'
                      '// model of mean gem margin on standardised map features. Score = bias + w . (f - mean) / std.\n'
                      '#include <array>\n#include "mapfeat.h"\nnamespace mb {\n' % (lam, len(maps), comps, opps))
            out.write(f'inline constexpr int kComps = {len(comps)};\n')
            out.write(f'inline constexpr std::array<float, kMapFeatures> kFeatMean{{ {fmt(mu)} }};\n')
            out.write(f'inline constexpr std::array<float, kMapFeatures> kFeatStd{{ {fmt(sd)} }};\n')
            out.write(f'inline constexpr std::array<float, kComps> kCompBias{{ {fmt([models[k][2] for k in comps])} }};\n')
            out.write('inline constexpr std::array<std::array<float, kMapFeatures>, kComps> kCompW{ {\n')
            for k in comps:
                out.write(f'    {{ {fmt(models[k][3])} }},\n')
            out.write('} };\n} // namespace mb\n')
        print('wrote', os.path.join(write, 'src', 'draft_model.h'))


if __name__ == '__main__':
    main()
