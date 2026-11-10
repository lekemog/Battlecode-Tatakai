# #53 side-B deficit: not a side bug (opponent-assignment artifact)

Date: 1 November 2026. Bot: v50d (live 222). Engine 2.0.0, cambc 4.0.0. Data: 60 finished ranked games since 2026-10-31T23:22Z (23 wins, 37 losses).

## Summary

Our record was 18-22 on side A and 5-15 on side B. The deficit is explained by who we played, not by where we stood: every one of the 10 games against the two strongest opponents of the window (rank-67 team, 5 games; rank-64 team, 5 games) was played as side B, and all 10 were lost. The other 10 side-B games are 5-5. Self-play on 70 maps shows no side bias (A 46%, B 54%). No code in v50d depends on the team side. Nothing to fix for #53; the real finding is how the rank-67 team beats us (below), which is an economy-speed gap.

## Facts

Real games (summary JSON + stdout of the ranked matches, tools in `tools/replay`):

| group | side | W-L |
|---|---|---|
| rank-67 team (5 games: adgato_gemcombat5, 02geodes, 00collision, 02crossing, adgato_gemcombat2) | B | 0-5 |
| rank-64 team (00split, 00anvil, adgato_gemcombat5, 00elkring, 02fields) | B | 0-5 |
| other side-B games (rank 72 team 2-3, rank 85 team 3-2) | B | 5-5 |
| all side-A games (9 opponents) | A | 18-22 |

Decoded replays of the 5 rank-67 games (`tools/replay/extract4.mjs`, snapshot per round; our side is B):

| match | map | first deposit us / them | items r200 us/them | items r400 us/them | final gems us/them | deaths us/them |
|---|---|---|---|---|---|---|
| eefca177 | adgato_gemcombat5 | r204 / r99 | 3 / 6 | 3 / 11 | 140 / 1008 | 5 / 1 |
| affcea93 | 02geodes | r192 / r101 | 9 / 8 | 14 / 16 | 558 / 1004 | 4 / 0 |
| 3620988e | 00collision | r206 / r68 | 9 / 14 | 17 / 16 | 574 / 1019 | 8 / 2 |
| f9e02957 | 02crossing | r32 / r53 | 7 / 12 | 11 / 22 | 727 / 1022 | 9 / 7 |
| 41c63132 | adgato_gemcombat2 | r164 / r34 | 3 / 5 | 3 / 10 | 252 / 1001 | 12 / 3 |

- The rank-67 team makes its first deposit 60-170 rounds before us in 4 of 5 games and keeps a 100-400 gem lead from there. Deaths are not the main factor in 3 of the 5 (4/0, 8/2, 5/1), unlike the mass-death losses of #54.
- Items (shards + emblems owned, both teams) are 1.2-3x ours at r400 on the gem maps; no snowball from kills in these games.

## Code path

`grep` over v50d for team-side dependence: only `map::spawn_region(team::ally/enemy)` and `champions(ally/enemy)` (relative queries), `World::ally_spawn_center`, the shared-memory slots indexed by roster order. No `is_a`, no coordinate flip, no branch on absolute spawn position. The draft order is a fixed list (`draft_order`) that never reads the enemy picks, so side B's information advantage (picks are simultaneous) is unused but also not harmful.

## Local reproduction (self-play)

`mirror.sh` (scratch driver): candidate vs base, 70 maps x both orders = 140 deterministic games per pair.

| pair (140 games) | side A wins | side B wins |
|---|---|---|
| v50d vs identical copy | 64 | 76 |
| v50d vs v50a | 69 | 71 |
| v50e1 vs v50d | 67 | 73 |
| v50e4 vs v50d | 62 | 78 |
| v50e5 vs v50d | 66 | 74 |
| total of the five | 328 / 700 (47%) | 372 / 700 |

The self-copy mirror is exactly 70-70 in candidate wins and 1-1 on every map, i.e. outcomes are fully determined by the (map, side) game and a side bias would show as an A/B split: there is none.

## Hypothesis

The 5-15 is a match-group assignment artifact: matches come in groups of five against one opponent on one side, and the two strongest opponents happened to be on B. Probability of 5-15 vs 18-22 from chance: Fisher exact p about 0.15 on the numbers alone; with the opponent-strength confound it is unremarkable.

## Isolated candidates

None needed for the side claim. The economy-speed gap against the rank-67 team (first deposit 60-170 rounds later) is the lever; it is tracked with the slow-race issue (#55) and not touched here.

## Scope scan

Not applicable (no code path depends on the side). Self-play over all 70 maps above.

## Still to do

- Re-test the side split on the next 60 ranked games (different assignment of opponents to sides).
- Compare our first-deposit round with the rank-67 team's across more of its games (needs more replays).
