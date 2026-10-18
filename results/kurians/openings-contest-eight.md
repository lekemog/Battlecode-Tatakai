# How top teams win the five weak maps: winner vs loser (Kurians' Claude, 18 Oct)

**Data:** every contest, eight, collision, corners and stampede game in `top-replays/` (10/10/10/10/9 games, top-20 vs top-20). Decoded with `tools/replay/extract.mjs`.

**Tools:**
- `tools/openings.py MAP DIR`: openings, winner vs loser.
- `tools/captures.py MAP DIR`: who captures which camps.

**Revised after the review on #22:**
- Gold **spent** (earned minus held) replaces item counts, which fall when shards merge into an emblem.
- The never-banked rate is shown next to first-tribute timing. The first-tribute average covers only teams that banked.
- The consumable "measure" is dropped.
- The enemy **third** is stated explicitly. It is stricter than the enemy *half* used by `tools/oppmodel.py`.

**Caveats:** 9–10 games per map, top-vs-top only, so these are correlations, not causes. Zones are thirds by distance to the two spawn centroids.

## Summary table (winners vs losers)
| Measure | Contest | Eight | Collision | Corners | Stampede |
|---|---|---|---|---|---|
| Never banked (whole game) | **20% vs 90%** | 0% vs 10% | 0% vs 0% | 0% vs 0% | **0% vs 56%** |
| First tribute (teams that banked) | r1210 vs r1594 (1 team) | **r101 vs r152** | r81 vs r86 | r68 vs r69 | r410 vs r386 (4 teams) |
| Banked r300 / r600 | 0 / 0 vs 0 / 0 | **402 / 953** vs 90 / 270 | 253 / **802** vs 180 / 367 | 399 / **872** vs 272 / 554 | 180 / **733** vs 60 / 100 |
| Gold earned r150 | **702** vs 334 | **856** vs 540 | **748** vs 560 | 1039 vs 911 | 606 vs 658 |
| Gold spent r50 / r100 / r150 | 50 / 259 / **495** vs 55 / 189 / 263 | 54 / **446** / 611 vs **124** / 293 / 439 | **139** / 334 / **599** vs 72 / 304 / 422 | **229 / 534** / 924 vs 159 / 397 / 767 | **3 / 57** / 461 vs 47 / 309 / 540 |
| Deaths by r150 | **2.0** vs 4.1 | **1.3** vs 3.0 | **0.6** vs 1.6 | 0.6 vs 1.2 | 0.8 vs 0.9 |
| Middle third, r0–150 | **71%** vs 59% | 44% vs 44% | 52% vs 47% | 47% vs 47% | 62% vs 56% |
| Enemy third, r0–150 | 0% vs 0% | 1% vs 3% | 1% vs 0% | 1% vs 0% | 5% vs 2% |

## Per map
- **Contest:** nobody banks before ~r800, and 9 of 10 losers never bank at all.
  - Level at r50; winners earn 2.1× the gold by r150 and invest about twice as much.
  - `tools/captures.py` (up to r150): winners make 6.3 captures vs 3.8 (65% of all captures). **The whole difference is middle-third gold clusters: 4.7 vs 2.3.** Own-third captures are equal (1.6 vs 1.5), and nobody captures in the enemy third. Kills: 3.2 vs 1.5.
- **Eight:** losers spend *more* by r50 (124 vs 54 gold), but winners lead on both gold earned and spent from r100.
  - Winners bank about 50 rounds earlier and convert continuously (402 vs 90 banked by r300).
  - Winners die less than half as often by r150.
- **Collision:** openings look alike (first bank ~r80 for both). The gap opens after r150 (802 vs 367 by r600), so it points at conversion (#18). Winners invest earlier (139 vs 72 gold spent by r50).
- **Corners:** winners invest earlier and more (229 vs 159 by r50, 534 vs 397 by r100), consistent with v19f. Ryth was in all 10 winning drafts against 5 of 10 losing ones (small sample).
- **Stampede:** winners spend almost nothing by r100 (57 vs 309 gold), then out-bank the losers 733 vs 100 by r600. **56% of losers never bank.** This suggests winners skip early shopping to race the 360-gem herd.
  - On main Claude's identical 15-team games, v19f's early shopping hasn't hurt stampede yet (v19f 5 = v18x 5 wins).

## What this does and doesn't show
- **Enemy third:** winners spend 0–5% of r0–150 there on all five maps. That's a statement about the opening third only. It doesn't rule out later pressure, or crossing the halfway line: on contest, 8 of 20 rows count as half-invaders over r0–250 in `tools/oppmodel.py`.
- **Not converting is the common failure.** Never banking (contest, stampede) or banking late and rarely (eight) shows up on three of the five maps.
- **The early economy depends on the map.** Investing earlier goes with winning on corners and collision, and the reverse holds on stampede.

## Reproduce
Run `python tools/openings.py MAP DIR` and `python tools/captures.py MAP DIR [ROUND]`. Both print the match IDs of every game.
