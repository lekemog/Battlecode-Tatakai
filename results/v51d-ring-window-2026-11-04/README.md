# v51d: built from the #45 acceptance check (Nawfal, 4 Nov) and the 3 Nov studies

Base: v51c (v50h5e + altar-access deadlock fixes, `results/code-efficiency-2026-11-03`). Not submitted; no panel run yet.

## Input
Nawfal's check of 63 post-v222 `02the_pack` games (6 against the top 25): the sealed-altar breach now works (5 of 6 deposit, v50c: 0 of 6) but 3 of 6 miss the bar (a deposit in every game, first before r700): first deposits r585-982, 203-735 gems lost to deaths per game, five deaths within 8 tiles of the altar in the Fish game. Three untested ideas: breach from range 3, treat a cleared ring as a 40-round banking window, carry smaller bags near the ring when enemies are seen.

## What was built (all flags in `config.h`)
| Change | Flag | Reason |
|---|---|---|
| Ring window: on a sealed-altar map, once the walk to the altar is open, bank any bag of 10+ gems that can reach it within 40 rounds | `ring_window_min 10`, `ring_window_walk 40` | idea 2; also uses the existing gap tracking |
| Smaller bags under threat: bank from 20 gems when an enemy was seen within 12 tiles in the last 15 rounds | `tribute_gems_danger 20` (was 0) | idea 3; existing mechanism, was off |
| Bag cap: the learned bank factor can no longer push the trigger above 40 gems | `tribute_cap 40` | from v51a: bags at 25+ gems waiting 72% -> 50% of turns |
| Altar-access deadlock fixes (carrier detour after 4 blocked turns, idle champion yields) | `blocked_detour`, `idle_yield` | v51c |
| Breach from range 3 (idea 1) | none needed | the breach already uses each champion's full attack range (`handle_breach`: `range = max(1, attack_range)`); the limit is the single-champion HP budget (`trip_pool`) |

Not changed on purpose: `ring_min_gems` (40, the bag size that starts a breach). Starting at 15 or 1 gave first banks 491/583/680/494 and 490/667/601/466 vs 563/564/598/498 on four the_pack games: mixed, inside noise.

## Local results (engine 2.0.0, 86 maps x 2 sides, deterministic)
| Test | v51d | v50h5e (live) |
|---|---|---|
| mirror vs live | **90-82** (52.3%), margin +40, banked 811 vs 771, deaths 4.2 vs 4.1, 0 bot faults | |
| vs v50p1 (early pack), 172 games | **122 wins (70.9%)**, margin +250, banked 854, unconverted gems 124, deaths 7.0 | 108 (62.8%), +174, banked 812, unconverted 137, deaths 6.6 |
| 02the_pack first bank, 4 games (v50p1, x_daniel8, both sides), third carrier | 635 / 705 / 635 / 542 | 685 / 726 / 722 / 620 |
| 02the_pack first bank, first carrier | unchanged (644/564/598/498 vs 563/564/598/498) | |
| smoke (contest, the_pack, the-front, colosseum, road_of_riches, islands) | 0 errors, 0 fuel-outs | |

Fuel on the four heaviest maps: 41K per turn (live bot about 43K), idle-none turns 7.3% (live bot about 12%). 03colosseum is still lost to x_daniel8 in the smoke test (known, #60).

## Reading
- Same local level as v51a against the early-pack bot (122), slightly ahead in the mirror, with the deadlock fix and the ring window added. No death reduction: deaths vs v50p1 are up 0.4.
- The ring window helps later carriers bank earlier; the first deposit on the_pack is limited by when the first ring camps die (r500-650 here), which none of these changes touch. That is the open problem in #45.
- Local opponents do not guard altars or camp the ring, so this cannot show the 203-735 gems lost per game; only a panel can.

## To do before deploying (needs a LIVE_SLOT window)
Top-10 panel (`t10_226` pin) for v51d: bar +4 wins over v226 with deaths not worse, zero-bank games below 5, mean banked above 382 (v51b got 5 wins, 3 zero-bank, 393 banked, deaths +0.9). Ablate if it moves: cap only vs the rest.
