# Completed map-robustness experiments — 29 October 2026

**2,800 completed local engine games**, five fixed policies, 70 unique active map layouts, four opponents including unchanged v50c, both sides. No bot was deployed. Exact source/map hashes, frozen plans, patches and per-case metrics accompany this report.

## Results

| Policy | Old 40 maps vs 3 bots | Extra 30 maps vs 3 bots | Direct v50c across 70 maps | Total | Our faults |
|---|---:|---:|---:|---:|---:|
| v50c | 238/240 | 177/180 | 70/140 | 485/560 | 0 |
| v50c-hazard-history | 239/240 | 177/180 | 70/140 | 486/560 | 0 |
| v50c-ring-carrier | 238/240 | 176/180 | 63/140 | 477/560 | 0 |
| v50c-danger-bank | 238/240 | 178/180 | 68/140 | 484/560 | 0 |
| v50c-combined | 238/240 | 177/180 | 69/140 | 484/560 | 0 |

The three frozen opponents are Daniel v8, DE41H v4 and Mohnish from our repository benchmark. They are much weaker than current top-ten teams. The direct v50c column includes a 70/140 self-play control for unchanged v50c. A win-count edge here is not a ladder-strength estimate.

## Paired changes relative to baseline

Every comparison checks identical map hash, default engine seed, opponent and our side. Outcomes are paired; deterministic repeats do not create new independent evidence. Whole-map bootstrap intervals below are descriptive sensitivity estimates, not proof of generalisation or a correction for trying multiple candidates.

| Policy | Baseline losses converted | Baseline wins lost | Map-block delta interval, percentage points |
|---|---:|---:|---|
| v50c-hazard-history | 2 | 1 | [-0.36, 0.71] |
| v50c-ring-carrier | 3 | 11 | [-2.5, -0.54] |
| v50c-danger-bank | 15 | 16 | [-1.61, 1.25] |
| v50c-combined | 20 | 21 | [-1.96, 1.61] |

## Per-map net win changes

Counts below sum eight matched cases per map: three frozen opponents plus v50c, both sides. Names are display-normalized; exact hashes and source names remain in local-games.json.

| Map | History | Carrier gate | Danger bank | Combined |
|---|---:|---:|---:|---:|
| adgato_gemcombat1 | 0 | 0 | 0 | 0 |
| adgato_gemcombat2 | 0 | -1 | -1 | -1 |
| adgato_gemcombat3 | 0 | 0 | 0 | 0 |
| adgato_gemcombat4 | 0 | 0 | 0 | 0 |
| adgato_gemcombat5 | 0 | 0 | -1 | -1 |
| ambush | 0 | 0 | 0 | 0 |
| anvil | 0 | 0 | 0 | 0 |
| arena | 0 | 0 | 0 | 0 |
| big_world | 0 | 0 | 0 | 0 |
| boss_battle | 0 | 0 | 0 | 0 |
| breadcrumbs | 0 | 0 | 0 | 0 |
| broken_curve | 0 | 0 | 0 | 0 |
| collision | 0 | 0 | 0 | 0 |
| concentrated_wealth | 0 | 0 | 0 | 0 |
| contest | 0 | 0 | 0 | 0 |
| corners | 0 | 0 | 0 | 0 |
| corridors | 0 | 0 | -1 | -1 |
| crater | 0 | 0 | -1 | -1 |
| crossing | 0 | 0 | 0 | 0 |
| cuts | 0 | -1 | 0 | 0 |
| dunes | 0 | 0 | 0 | 0 |
| eight | 0 | -1 | 0 | 0 |
| elk_arena | 0 | 0 | 0 | 1 |
| elkring | 0 | 0 | 0 | -1 |
| expanse | 0 | 0 | 0 | 0 |
| famine | 0 | 0 | 0 | 1 |
| fields | 0 | 0 | 0 | 1 |
| fracture | 0 | 0 | 0 | 0 |
| fragment | 0 | 0 | 0 | 0 |
| galaxy | 0 | 0 | 1 | 1 |
| gem_fields | 0 | 0 | 0 | 0 |
| gemfight | 0 | 0 | 0 | 0 |
| geodes | 0 | 0 | 0 | 1 |
| gift_wrapping | 0 | 0 | 0 | 0 |
| gold_rush | 0 | 0 | 0 | 0 |
| great_wall | 0 | 0 | 0 | 0 |
| guardians | 0 | 0 | 0 | 0 |
| harvest | 0 | 0 | 0 | 0 |
| hooks | 0 | 0 | 1 | 1 |
| interlock | 0 | 0 | 0 | 0 |
| islands | 0 | 0 | 0 | 0 |
| lanes | 1 | 0 | 0 | 0 |
| lost_world | 0 | 0 | 0 | 0 |
| monolith | 0 | 0 | -1 | 0 |
| oasis | 0 | 0 | 0 | 0 |
| packs | 0 | 0 | 0 | 0 |
| pilgrimage | 0 | 0 | 0 | 0 |
| quadrants | 0 | 0 | 1 | 1 |
| quarry | 0 | 0 | 1 | 1 |
| reverse_spiral | 0 | 0 | -1 | -1 |
| ribs | 0 | 0 | 0 | 0 |
| road_of_riches | -1 | 0 | 0 | 0 |
| rows | 0 | 0 | 0 | 0 |
| rushbait_v2 | 0 | 0 | -1 | -1 |
| shortcut | 0 | 0 | 0 | -1 |
| split | 1 | 0 | -1 | 0 |
| stalactites | 0 | 0 | 1 | 1 |
| stampede | 0 | 0 | 0 | 0 |
| starfish | 0 | -1 | 1 | 1 |
| starvation | 0 | 0 | 0 | 0 |
| swirl | 0 | 0 | 0 | 0 |
| tangle | 0 | 0 | -1 | -1 |
| the_farm | 0 | -1 | 0 | -1 |
| the_line | 0 | 0 | 0 | 0 |
| the_pack | 0 | -2 | 0 | -2 |
| the_pond | 0 | 0 | 1 | 1 |
| treasure_box | 0 | -1 | 0 | -1 |
| uncharted_lands | 0 | 0 | 1 | 1 |
| vault | 0 | 0 | 0 | 0 |
| yellow_brick_road | 0 | 0 | 0 | 0 |

## Validation splits

| Policy | Tuning maps / first 2 bots | Withheld old maps / first 2 bots | Withheld Mohnish across 70 |
|---|---:|---:|---:|
| v50c | 56/56 | 104/104 | 137/140 |
| v50c-hazard-history | 56/56 | 104/104 | 138/140 |
| v50c-ring-carrier | 56/56 | 104/104 | 136/140 |
| v50c-danger-bank | 56/56 | 104/104 | 137/140 |
| v50c-combined | 56/56 | 104/104 | 136/140 |

## Interpretation and limits

Use the accompanying map-history and design-review reports to prioritise actual ladder problems. The old bench omitted 30 active layouts and is saturated against these opponents. Current v221 top-ten results (5/50) and historical cohorts are separate from this local evaluation. A high local win rate therefore cannot certify a fix.

The candidates were not altered after results were inspected. The added-map set lies outside the old benchmark; some maps had already appeared in online loss analysis, so it is not a perfectly research-naive holdout. The old baseline may have been tuned on the old maps and bench opponents. A single deterministic engine seed is used per case; unseen seeds and stronger real opponents remain necessary before deploying.

History validity is a confirmed logic repair. Carrier-relative ring routing and a 10-gem danger threshold remain policy experiments; combining them with history is independently measured. Reject broad regressions and do not rescue a weak combination by adding map-name selectors. Stronger/new opponent snapshots are the next priority for the evaluation suite.
