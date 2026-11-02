# Map-family stress test of the live bot (v50h5e, ladder #226), 2026-11-02

Why: one map pool hides weaknesses. Maps were grouped into families from measured features (`tools/lab/mapfeatures.sh` -> `mapfeatures.csv`, `tools/lab/mapfamilies.py` -> `mapfamilies.csv`): gem-starved (<100 gems), gem-only (gold<300), monolith, elk-herd, large, gold-rich, gold-poor, standard. Every one of the 86 maps, both sides, against x_daniel8, h_mohnish (weak) and v50p1 (early-pack stress opponent). 516 games; `family_report.txt` has the full table.

## Result
Wins out of 172 games: x_daniel8 168, h_mohnish 169, v50p1 108 (63%). Weak opponents are saturated in every family except gem-starved (90-100%). The discriminating opponent is v50p1:

| family | maps | win% vs v50p1 | deaths/game | banked gems | note |
|---|---|---|---|---|---|
| elk-herd | 16 | 69 | 5.1 | 929 | fine |
| gold-poor | 10 | 75 | 8.2 | 814 | 3 games to r2000 |
| gem-starved | 5 | 80 | 8.8 | 451 | 3 zero-deposit games, 5 reach r2000: banking is slow, result decided by tiebreak |
| large | 4 | 75 | 3.1 | 990 | fine |
| monolith | 27 | 59 | 5.9 | 797 | 12 games reach r2000, 2 zero-deposit |
| standard | 14 | 57 | 8.0 | 807 | high deaths |
| gold-rich | 3 | 50 | 6.7 | 892 | only 3 maps, weak evidence |
| **gem-only** | 7 | **43** | 8.3 | 733 | the one family we lose (margin -110) |

## Reading
- Gem-only maps (no gold, so no shop/upgrade income) are the worst family against an early-pack opponent: we lose more than half, with 8.3 deaths per game and 733 gems banked instead of ~1030. Gold-poor and standard are close behind on deaths. Intuition: when gold cannot buy an edge, the fight over the first gem groups decides the game, which is exactly the early-death problem of #56 and the cohesion/outnumber ideas #61/#62. These families are where those candidates should be tested first (cheap: `MAPLIST` restricted to the family).
- Monolith maps rarely end early: 12 of 54 v50p1 games go to round 2000 (see #60, 03homonoliths fix in v50i1).
- Gem-starved maps are mostly won on the tiebreak, not by banking; zero-deposit games appear only here and on monolith.
- Deaths per game are 5-8 vs v50p1 but under 1.3 against the weak bots, so v50p1 is the right stress opponent for any caution change.

## How to reuse
`PROJ=<lab> MAPLIST=<lab>/all.txt BENCH_OUT=<dir> python3 -I tools/lab/gauntlet_stats.py CAND x_daniel8,h_mohnish,v50p1` then `python3 -I tools/lab/family_report.py CAND <dir> mapfamilies.csv`. Compare a candidate to this table per family; a candidate that gains overall but loses a family is suspect. Limits: one opponent is discriminating, families are small (3-27 maps), games are deterministic so no confidence intervals.
