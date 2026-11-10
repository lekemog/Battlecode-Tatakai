# v55a / v55b: in-game fight calibration (online learning), 9 Nov 2026

## What it learns
Each champion, on rounds it ends isolated (no ally within 2, no camp awake within 4) with enemies in attack range,
compares the damage the fight simulation expects (basic + ready casts) with the damage taken next round (all its
health if it died). Multiplier m = (6 x mean_exp + sum_obs) / (6 x mean_exp + sum_exp), clamped; it scales enemy
damage in the fight simulation (and the "doomed" check) for the rest of the game.
- v55a: m in [0.8, 2.0] (learns both ways). v55b: m in [1.0, 2.0] (only more cautious). Both on v53y.

## Calibration seen in self-play (4 logged games, round 1000)
Observed / expected on isolated rounds mostly 0.25-0.8 (m at the 0.8 floor), a few near 1.0: against our own bot the
simulation over-predicts isolated damage (enemies often hit someone else or do not step in).

## Local results vs v53y (kills / deaths per game, candidate / base)
| candidate | all maps (256) | unseen (140) | kills | deaths |
|---|---|---|---|---|
| v55a | **135-121** (margin -19) | 72-68 (+26) | 3.39 / 4.05 | **4.46 / 3.82** |
| v55b | 128-128 (-4) | 71-69 (+1) | 3.43 / 3.44 | 3.92 / 3.85 |
| (v53y vs v53x) | 127-129 | 69-71 | 3.40 / 3.45 | 3.88 / 3.84 |

- v55a: learns that our own bot hits softer than predicted, fights more, wins +14 (about 1.7 sd) but dies 0.6 more a game.
- v55b: in self-play the multiplier rarely rises above 1, so it plays like v53y; it can only show anything against
  teams that hit harder than predicted (the UK panel). 0 faults in all runs.

## UK panel (v55a = submission 241, 45 pinned games)
**10/45**, deaths 7.51, kills 2.29, margin -361 (v53x: 12/45, 7.49, 2.02, -381). Per opponent: BattleCats 1, Claudus 0,
QS2isLaw 2, Rogue Lock Pickers 1 (first ever), bentheboss 0, smurphy 1, jianqiao 1, DOOMSDAY 3, 0xDEADBEEF 1.
More kills, no fewer deaths, two fewer wins (within noise). Not kept; 240 restored at 00:30 UTC 10 Nov.
