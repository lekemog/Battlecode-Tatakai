"""bracket_sim.py : P(top 8) in a double-elimination qualifier by seed and rating, from the International Qualifier's real bracket.

Inputs (fetched from the public API and CLI):
- ~/games/t_<IQ id>.json : International Qualifier detail (bracket with winnerTo/loserTo links, snapshots with seeding ratings);
- ~/games/ladder_full.json : current ladder.
Steps:
1. Fit series odds on the IQ's 1,023 results: P(higher rated wins) = 1 / (1 + 10^(-gap / s)), MLE for s.
2. Rebuild the double-elimination graph (512 slots; upper round 1 holds the seeds; seeds beyond the field are byes).
3. UK field: the known UK teams above us, us, optional unknown UK teams, the rest drawn from the global ladder below us.
4. Simulate. Top 8 = champion, runner-up, and the losers of the last four lower-bracket rounds (as in the IQ).
Reports P(top 8) for our rating at our natural seed, and counterfactually at other seeds with the same strength.
"""
import json
import math
import random
import sys

IQ = '/root/games/t_3e98ebb8-a7eb-4751-bb6a-4aac2d565981.json'


def fit_scale(B, S):
    gaps = []
    for m in B:
        if m['status'] != 'finished' or not m['a'] or not m['b']:
            continue
        ra, rb = S[m['a']['teamId']]['seedingRating'], S[m['b']['teamId']]['seedingRating']
        fav_a = ra >= rb
        gaps.append((abs(ra - rb), (m['winner']['teamId'] == m['a']['teamId']) == fav_a))
    best = None
    for s in range(20, 400, 2):
        ll = sum(math.log(max(1e-9, (1 / (1 + 10 ** (-g / s))) if w else 1 - 1 / (1 + 10 ** (-g / s)))) for g, w in gaps)
        if best is None or ll > best[0]:
            best = (ll, s)
    return best[1]


def build(B):
    by = {m['code']: m for m in B}
    first = {}  # code -> (seedA, seedB)
    for m in B:
        if m['bracket'] == 'upper' and m['round'] == 1:
            first[m['code']] = (m['a']['seed'] if m['a'] else None, m['b']['seed'] if m['b'] else None)
    lower_rounds = sorted({m['round'] for m in B if m['bracket'] == 'lower'}, reverse=True)
    top_lower = set(lower_rounds[:4])
    order = sorted(B, key=lambda m: (m['round'], 0 if m['bracket'] == 'upper' else 1, m['position']))
    return by, first, order, top_lower


def simulate(order, first, top_lower, strength, s, rng):
    slots = {}
    for code, (sa, sb) in first.items():
        slots[(code, 'a')] = sa
        slots[(code, 'b')] = sb
    top8 = []
    champion = None
    for m in order:
        code = m['code']
        if m['bracket'] == 'reset':
            continue
        a, b = slots.get((code, 'a')), slots.get((code, 'b'))
        if a is None and b is None:
            w = l = None
        elif a is None or b is None:
            w, l = (a if b is None else b), None
        else:
            ra, rb = strength[a], strength[b]
            x = max(-30.0, min(30.0, -(ra - rb) / s))
            p = 1 / (1 + 10 ** x)
            w, l = (a, b) if rng.random() < p else (b, a)
        if m['winnerTo']:
            slots[(m['winnerTo'], m['winnerSide'])] = w
        if m['loserTo']:
            slots[(m['loserTo'], m['loserSide'])] = l
        elif l is not None and m['bracket'] == 'lower' and m['round'] in top_lower:
            top8.append(l)
        if m['bracket'] == 'final':
            champion = w
            top8 += [w, l]
    return set(x for x in top8 if x is not None)


def main():
    d = json.load(open(IQ))
    B, S = d['bracket'], {x['teamId']: x for x in d['snapshots']}
    s = fit_scale(B, S)
    by, first, order, top_lower = build(B)
    lad = json.load(open('/root/games/ladder_full.json'))
    known = [('BattleCats', 2558), ('Claudus Maximus', 2332), ('QS2isLaw', 2284), ('Rogue Lock Pickers', 2258), ('bentheboss', 2246),
             ('smurphy', 2200), ('jianqiao', 2187), ('DOOMSDAY', 2174), ('0xDEADBEEF', 2161)]
    us = float(sys.argv[1]) if len(sys.argv) > 1 else 2090.0
    n_field = int(sys.argv[2]) if len(sys.argv) > 2 else 188
    unknown = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] else []
    below = [r for rank, name, r in lad if r < us - 1]
    rng = random.Random(1)
    print(f'series scale s = {s} (P(fav) at gap 50 = {1 / (1 + 10 ** (-50 / s)):.2f}, gap 100 = {1 / (1 + 10 ** (-100 / s)):.2f})')
    sims = int(sys.argv[4]) if len(sys.argv) > 4 else 1500
    results = {}
    for trial_seed in [None] + list(range(5, 17)):
        hits = 0
        for k in range(sims):
            others = [r for _, r in known] + unknown
            k_rest = n_field - 1 - len(others)
            pool = sorted(rng.sample(below, min(k_rest, len(below))), reverse=True)
            field = sorted(others + pool, reverse=True)
            natural = 1 + sum(1 for r in field if r > us)
            seed_us = natural if trial_seed is None else trial_seed
            # seeds: field order with us inserted at seed_us
            ranked = field[:]
            ranked.insert(seed_us - 1, us)
            strength = {i + 1: ranked[i] for i in range(len(ranked))}
            for x in range(len(ranked) + 1, 513):
                strength[x] = -1e9
            top = simulate(order, first, top_lower, strength, s, rng)
            hits += seed_us in top
        results[trial_seed] = hits / sims
    nat = 1 + len(known) + len(unknown)
    print(f'our rating {us:.0f}, field {n_field}, UK teams above us {nat - 1}: natural seed {nat}, P(top 8) = {results[None]:.1%}')
    print('same strength, counterfactual seed -> P(top 8): ' + ', '.join(f'{k}: {v:.0%}' for k, v in results.items() if k is not None))


if __name__ == '__main__':
    main()
