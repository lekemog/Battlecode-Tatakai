# Code efficiency and decision timing of the live bot (v50h5e = #226), 3 Nov 2026

Tools: `bots/v51p` (profiler build; `tools/lab/add_profiler.py` adds it to any v50-line bot), `tools/lab/profsweep.sh`, `tools/lab/profreport.py`.
Data: 16 maps x 2 opponents (x_daniel8, v50p1) x both sides = 64 games, 290K champion-turns. Full tables: `profile_v51p_live.txt` (live bot), `profile_v51q_v51b.txt` (v51b).
The profiler reads fuel() a few times per turn, so it is almost, not exactly, behaviour-neutral. Limits: local opponents, one game per cell, profile lines are cumulative to the last print (every 250 rounds).

## 1. Is the code fast enough? On average yes, with a sharp cliff
- Each turn starts with ~100K fuel and uses 36K on average. 9.6% of turns use over 60K; 38 of 293K turns were suspended (fuel ran out), 36 of them on `02the-pack`.
- Fuel by phase: farm 33%, observe 18.5%, groups 15%, threats 7%, support 6%, warm 4%, tribute 4%, the rest under 4% each.
- Share of times a fuel gate blocked its step: threats 0.33%, low-health 0.00%, tribute 0.03%, farm 0.17%, target choice 0.78%, **full-map route field 11.3%** (30-36% on 03the-front, 03colosseum, 02the-pack). Only 02the-pack skips the threat phase (5.2%); only 03colosseum defers target choice often (8.9%).
- The route-cost model underestimates the real cost: actual/estimate median 1.27, p90 1.49, max 1.80 (1,449 logged misses).

**Sensitivity (the strongest result).** `noise_burn` wastes fuel at the start of every turn (2000 = +18K). Copies of the live bot against the live bot, 172 games each (86 maps, both sides):

| extra fuel burnt per turn | +0 (control) | +9K | +18K | +27K | +36K | +54K |
|---|---|---|---|---|---|---|
| share of decided games won | 50.6% | 45.9% | 36.0% | 7.6% | 1.2% | 0.0% |
| mean gem margin | +9 | -22 | -155 | -633 | -909 | -996 |

Reading: the bot is already on the slope. +9K costs about 5 points; from +18K it collapses because the phase gates (threats need 45K + 14K reserve left) start skipping the fight and recall logic. Consequences:
1. A new per-turn feature that adds more than about 5-10K will lose games on its own; measure fuel with `profreport.py` before benching it.
2. Saving fuel on the heavy maps (observe + groups bookkeeping is 50-70K per turn on 02the-pack once many camps are in view) is the realistic speed-up target. Nothing here shows that speed-ups on ordinary maps would win games: the gates there almost never fire. The burn curve measures the cost of being slower, not the gain from being faster.

## 2. Are decisions made as soon as required?
| Decision | Measure | Result |
|---|---|---|
| leave spawn | first round off spawn, median | 3-4 |
| first fight | median | 11-13 (Varg 26) |
| first camp capture | median | 38-53 |
| **first bank** | median | Marcella 140, Heart 184, Ryth 180, Varg 287, Vendetta 356 (top teams: round 44-87 per the public review, third-party data) |
| bank with a bag at or above 25 gems | turns not banking | **71.9%** (89% of those while farming or capturing); mean 52 gems waiting |
| low health (under the recall threshold, off spawn) | turns not yet healing or in a player fight | 51.9% (78% of those: camp fight or capture) |
| no target | `idle/idle-none` turns | 3.5% overall, **46% on 03the-front**; each such turn re-scores every group for ~65K fuel, the most expensive decision in the bot |

v51b (bag cap 40, guarded-altar routing): turns not banking 71.9% -> 49.6%; first bank Heart 184 -> 159, Ryth 180 -> 154. Varg (307) and Vendetta (316) are still late.

## 3. Bug found by following the idle turns: altar-access deadlock (03the-front)
Vs v50p1 on 03the-front, Marcella and Varg stood two tiles from unlocked altars carrying 118 and 91 gems for over 800 rounds (713 consecutive tribute turns). The altar column has camps above and below, so the only access tiles are x=29, y=31..33, and those were held by Heart and Ryth, idle with no target (~1,650 idle-none turns each). `handle_tribute` returns true without moving, so nothing ever changed. Same symptom as "carriers hoard and never bank" in `results/zero-bank-2026-11`.
Live bot in that game: round limit, 407 banked. v51c: wins at round 1063, 1,032 banked.

**v51c** = v50h5e + `blocked_detour` (a carrier that cannot step toward its altar for 4 turns walks to the nearest altar at least 6 tiles away for 60 rounds) + `idle_yield` (an idle champion with no gems beside an altar steps away when an allied carrier with 10+ gems is near). Both are flags.

| test (172 games) | v51c | v50h5e |
|---|---|---|
| mirror vs v50h5e | 84-88 (48.8%), margin +5, deaths 4.2 vs 4.1 | |
| vs v50p1 (early pack) | 112 wins (65.1%), margin +186 | 108 (62.8%), +174 |

Reading: neutral in aggregate (the deadlock needs a narrow altar column and idle champions), clearly positive on 03the-front. +4 against v50p1 and -4 in the mirror are inside noise. Not ablated (detour only / yield only), no panel run.

## 4. Suggested next steps
1. Idle-none cost: skip re-scoring all groups every turn when the last choice found nothing (re-score when a respawn timer expires or a group changes state).
2. Panel-test v51c (low risk, flags only) after ablating the two flags.
3. Reduce observe + groups bookkeeping on camp-dense maps; target 02the-pack's 35-70K turns.
4. Recalibrate the route-cost model (x1.3); this also moves the 11% field deferral.
5. Bank earlier: first bank at round 140-356 vs 44-87 is the clearest decision-timing gap. A smaller threshold and a per-champion cap for Varg and Vendetta are untested.
