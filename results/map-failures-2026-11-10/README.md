# Map-specific failures (10 Nov 2026)

## Is our result map-dependent? Yes
Our last 1,200 ranked games (8-10 Nov, submissions 239-242), each scored against the rating-expected result:
602 wins vs 624 expected; across the 128 maps chi-square is 247 where no map effect gives 128 +- 16.
- Never won (6+ games): `04gem_caverns` 0/12, `03one_gem` 0/11, `00collision` 0/7, `03showdown` 0/6.
- Other worst: `00galaxy` 2/14, `03ultrastarvation` 2/12, `00lanes` 1/9, `02stalactites` 1/10, `03fan` 2/12, `adgato_gemcombat3` 2/11, `00swirl` 2/11, `00dunes` 4/15.
- Best: `01corridors` 12/13, `01fracture` 11/12, `04bullseye` 12/14, `02geodes` 7/7, `01boss_battle` 7/8.
- The 16 worst maps: 23 wins where 86 were expected (165 games), about 5% of all our games.
Per-map table: `permap_ranked_1200.json` (games, wins, expected wins, variance, picks, games vs higher-rated).

## Confirmed on the current live bot (242): 20 unranked games vs teams ranked 56-66
Groups in `worst_groups_242.json` (reusable as `--source-group` pins). Result **3/20** (about 9 would be par).
| map | vs | result | banked | deaths | monster damage |
|---|---|---|---|---|---|
| 04gem_caverns | SilverSamurai / VeryGood | L / L | 210-980 / 42-1001 | 1-0 / 0-0 | 3k-17k / 3k-17k |
| 03one_gem | | W (0-0 tiebreak) / L | 0-0 / 0-160 | | 145k-43k / 102k-124k |
| 00swirl | | L / L | 627-1033 / 125-1027 | **41-12 / 32-6** | |
| 03fan | | W / L | 1004-0 / 544-1000 | | |
| 02stalactites | | L / L | 280-1066 / 563-1006 | 12-0 / 5-7 | games over by r498-532 |
| 00galaxy | will think later / EggsAfter11AM | L / L | 453-1020 / 882-1005 | 10-2 / 6-5 | |
| 00collision | | L / L | 590-1006 / 962-1009 | | |
| 03ultrastarvation | | L / W | 121-502 / 248-222 | 13-0 / 2-4 | |
| 00lanes | | L / L | 395-1009 / 721-1011 | 11-3 / 2-2 | 80k-155k / 139k-151k |
| 03showdown | | L / L | 637-1019 / 393-1027 | 18-7 / 13-7 | |

## Causes found and fixed (bots/v61e, v61f, v61g; each is the previous plus one change, on v61b)
1. **04gem_caverns** (114 single-crystal groups). The target chooser ranked all 114 groups through the walk fields (~55K of the
   turn's ~100K fuel), then needed a flat 26K reserve to score one, so it scored none and the champion idled about 50 rounds
   at a time; and the 16 evaluation slots went to freshly cleared neighbours that the scorer rejects for their respawn wait.
   - v61e: the per-evaluation reserve scales with group size (`score_reserve_by_size`).
   - v61f: above 48 groups the bound uses straight-line distance (`cheap_bound_groups`); respawning groups beyond
     `max_respawn_wait` are dropped before the evaluation loop (`bound_skips_respawn`, all maps).
   - Local: v61b self-play 245-210 after 2,000 rounds; **v61f vs v61b 1006-252 and 1003-231**.
2. **03one_gem** (one gem cluster among 34 gold groups) and **03ultrastarvation**. Gems were weighed against gold as on any
   map, so the only gem source lost to nearby gold groups; nobody can reach 1,000 there and the tiebreak (gems banked) decides.
   - v61g: scarcity = winning gems / the map's whole-game gem output, measured from the group list; above 0.5 the gem weight
     is multiplied by clamp(2 x scarcity, 1, 12). Triggers on exactly these two of the 128 maps (3.57 and 0.66; next 0.42).
   - Local: 03one_gem **205-0 and 222-0** vs v61b (was 0 gems); 03ultrastarvation 257-136 and 208-236.
3. Regression (128 maps x 2 sides): v61f vs v61b 135-121; **v61g vs v61b 135-121**, margin +13, 0 bot faults.

## Not yet explained
`00swirl` (32-41 deaths a game), `02stalactites` (opponents finish by r500), `00galaxy`, `00collision`, `00lanes`, `03showdown`, `03fan`.
