# v66i Heart/Cassi/Issac core: implemented, not qualified

Code source freeze: `65e10501953a578445b27399eae9d13d9dad0f68`; pinned v66i base: `5d282cec10e87be370b86ecae46fb056a31e5dae`. Read DESIGN.md for exact mechanisms, capabilities and limits.

The requested core is present in every experimental draft and fallback. v66i’s gold-first opening/caution is retained. Four isolated new folders separate fixed draft, role behavior, broad map selection and constrained melee flex. No original bot was edited or activated.

## Completed validation

- CLI/SDK5.0.1 release builds, engine3.0.0/build96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd asserted for all complete games.
- C++20 model/property tests passed with -Wall -Wextra -Werror: exhaustive required-core eligibility, slot counts, stale partner release, bounded regroup, vulnerability and stun-immunity logic.
-512/512 two-round draft scans:128 pinned maps/both sides for broad and constrained planners. Every planned draft includes Heart and pair, has the right number of unique picks, and completes its composition screen. Zero failures/fallbacks/logged turn errors. These are deliberately truncated and not game-win evidence.
-160/160 full smoke games:five policies × two local opponents × eight preselected maps × both sides. No batch failures or bot faults on either side. No logged turn errors. This remains a development screen, not all-map strength qualification.

## Full-game screen

| Policy | wins vs v66i /16 | wins vs early pack /16 | deaths/game vs v66i | deaths/game vs pack |
|---|---:|---:|---:|---:|
| v66i | 8 | 13 | 4.688 | 6.062 |
| cg-hci66-draft | 6 | 9 | 10.625 | 12.812 |
| cg-hci66-role | 2 | 13 | 11.625 | 11.812 |
| cg-hci66-map | 3 | 12 | 10.375 | 12.375 |
| cg-hci66-flex | 3 | 13 | 9.250 | 13.938 |

**Do not promote.** The core/role/flex versions do not beat v66i on this screen. Role-only improves pack wins9→13 over the fixed core draft, matching the unchanged baseline’s13, but loses against v66i and retains high deaths. The constrained flex also wins13/16 vs pack and only3/16 vs v66i. Small counts and reused maps cannot establish superiority.

There is a measurable mechanism with a poor overall trade: against v66i, Cassi round-200 champion damage rises177.67→363.83 when roles are enabled, while wins fall6→2. Constrained flex achieves351.05 damage and team gold927 vs unchanged v66i859.94 (+7.8%), but deaths9.25 vs4.69 remain the central failure. Better caster output/early gold is insufficient. Pair death counts in cases.csv count both physical bodies.

## Runtime / draft budgets

| Policy | fuel events vs v66i | vs pack |
|---|---:|---:|
| v66i | 294 | 140 |
| cg-hci66-draft | 554 | 196 |
| cg-hci66-role | 266 | 236 |
| cg-hci66-map | 750 | 436 |
| cg-hci66-flex | 861 | 401 |

Fuel exhaustion remains a material problem; these are event counts, not affected games. Zero bot faults does not imply uninterrupted turns. For constrained flex, draft search peaks at1,594,990 fuel (15.97% of the initial budget); the problem is ordinary gameplay, not lack of opening planning capacity. Broad planning peaks at2,820,436 (28.23%).

Measured constrained choices:3-pick Heart/pair/Varg or Marcella;4-pick Heart/pair with combinations of Varg/Vendetta/Ryth/Marcella;5-pick mostly Heart/pair/Marcella/Vendetta/Varg, with Ryth replacing Marcella on a few maps. No random variety or map-name conditions.

## Evidence and next gate

cases.csv and summary.json retain all160 outcomes, early gold/spend/death curves, Cassi damage and pair deaths, actual map/seed/engine pins and runtime counts. Both draft-scan CSVs retain512 traces. hashes.json records source/maps/WASM. Exact manifests, logs, pure tests and reproduction scripts are included. Two sample release replays retain the fixed-core vs constrained-flex comparison on a fuel-stress map.

Next: inspect paired deaths and fuel-outs, isolate focus/recall/camp admission, then freeze and confirm on remaining120 maps and transformed geometry. Only a qualified candidate should reach coordinated real-opponent panels. The preceding v245 experiment/top-ten draft-rate study is preserved in PR85 and is not pooled with this v66i evidence.
