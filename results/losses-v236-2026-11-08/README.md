# Why v236 (v53i) loses: 100 ranked games since it went live (8 Nov 06:10-10:10 UTC)

Ranked record over these 100 games: 51-49 (ladder neighbours). Sources: match summaries for all 100 (`tools/playbook/losses.py`) and decoded replays of the 14 worst fight losses.

## Losses vs wins (per game, us / them)
| | losses (49) | wins (51) |
|---|---|---|
| deaths | **8.6 / 3.8** | 3.9 / 6.6 |
| kills | 2.9 / 8.2 | 4.6 / 3.5 |
| deaths before r300 | 1.7 / 1.2 | 1.2 / 1.1 |
| first death (round) | 374 / 505 | 485 / 518 |
| gems lost on death | **197 / 76** | 29 / 72 |
| banked by r400 | 172 / 204 | 271 / 160 |
| first bank (round) | **296** / 236 | 117 / 248 |
| earned gold r300 | 1,126 / 1,354 | 1,366 / 1,260 |
| earned gold r600 | 2,507 / 3,261 | 3,019 / 2,652 |

Loss causes (first rule that applies):
- **fights 30** (our deaths >= theirs + 3);
- economy 7 (gold at r300 at least 15% behind);
- other 6;
- bank 4;
- close 2.

The early game is no longer where we lose. Losses are decided by mid- and late-game fights.

## The 14 worst fight losses: 165 of our deaths after r300
- **Team power at death (ours / theirs, alive, max HP x (strength + focus)): median 0.51.** We die at half their item power.
- **52% of the dying champions moved toward the nearest enemy in the previous 6 rounds** (27% away).
- 44% alone (no ally within 6); 43% outnumbered by 2 or more; mean 0.83 allies vs 2.13 enemies within 6.
- 28% inside a chain of our deaths (team fight); the rest are picks.
- 22% carrying 20+ gems; 32% on the enemy half.
- By champion: Ryth 49, Marcella 42, Heart 29, Vendetta 23, Varg 22.
- Opponents' picks: Vendetta and Marcella (12 each), Ryth and Heart (8), Vesper (6), Varg and Tavi (5).

## Diagnosis
Once the opponent has snowballed to about twice our item power, we keep walking into them one at a time and feed more gold. The existing "behind" caution (`behind_caution_gap`) was off, and it keyed on banked gems after r800, which is too late.

## Change: v53o
v53o is v53i plus an out-itemed posture:
- Each champion remembers each enemy's last-seen power.
- From r200, if our per-champion power is below 0.7 of theirs, fights need +0.5 margin and champions do not close in unless they can finish an enemy outright.

Mirrors are a no-regression check only, since self-play rarely out-items. The real test is the strong panels and ranked games.

## Result: v53o rejected
| test | v53o | kills / deaths (v53o vs base) |
|---|---|---|
| vs v53i | **112-144** | 2.25 / 3.74 vs 3.34 / 2.69 |
| vs v226 | 132-124 (v53i 151-105) | |
| unseen boards vs v53i | **59-81** | |

The posture fires often even in self-play, and passivity raises deaths: hesitant champions still get caught and stop trading back. Not shipped. The actionable part of the diagnosis is isolation (44% of late deaths alone), not the fight threshold.
