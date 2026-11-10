# Why we bank nothing against the top ten (2026-11-02)

Source: the 5 of 50 games in the v226 top-10 baseline panel (`results/panel/t10_226.json`) where we banked 0 gems (the candidate v50j1 had 9). Replays decoded with `tools/replay/extract4.mjs`; positions, bags and deaths read per round. Games: NEETCoders 00road_of_riches, Univardisty of Shingtonwash 01fracture and 02guardians, test4 01shortcut and 00contest.

## Finding
In 4 of 5 games we collect plenty (250 to 750 gems) and bank none. The gems are carried and lost on death.

| game | rounds | collected | lost with a dead carrier | carried at end | deaths with a bag (bag, enemies within 6, allies within 7) |
|---|---|---|---|---|---|
| 00road_of_riches (NEETCoders) | 558 | 538 | 148 | 390 on 4 champions | (50,0,0) (98,1,0) |
| 01fracture (Univardisty) | 1012 | 752 | 527 | 225 | 6 deaths, bags 72 to 108, 2 to 5 enemies, **0 allies** every time |
| 02guardians (Univardisty) | 1117 | 249 | 172 | 77 | 7 deaths, bags 11 to 59, 0 or 1 allies |
| 01shortcut (test4) | 766 | 546 | 279 | 267 | (21,3,0) (161,1,0) (97,2,0) |
| 00contest (test4) | 1073 | 0 | 0 | 0 | collects nothing: a different problem, not examined |

The opponent wins by banking 1000 first (r557 in the first game, submitted 200 by r200, 358 by r300, 933 by r500).

## Cause (observed in the road_of_riches replay, same pattern in the other three)
- The opponent keeps one to three champions standing at the altar it banks at (in road_of_riches the centre altar near (19,19)): average 1.4 to 2.3 enemy champions within 6 tiles of it in the games where we could tell. Those champions carry 0 gems, so they are guards, not carriers.
- Our carriers hold 50 to 150 gems each and stay far away: closest distance of a 50+ gem carrier to that altar averages 13 (road_of_riches), 19 (fracture), 17 (guardians), 21 (shortcut) tiles. They walk the map edge in "tribute" mode for 150 rounds. In road_of_riches four champions carried 94, 116, 150 and 30 gems at r400 to r550 and never entered.
- The ones that do approach arrive alone and die with the bag: allies within 7 tiles at death was 0 in 14 of 16 cases with a bag.
- So the bank rules (`tribute_gems` 25, guarded-altar back-off, hazard retreat) protect the carrier, and the result is hoarding. 400 gems on four champions is worth more than 0, and a bag of 150 that dies pays the enemy.

## What would change this (ranked)
1. **Joint push to the altar**: when the team's carried total is large (say 150+) and the bank altar has guards, all champions with bags plus escorts meet and go in together; carriers submit while escorts engage the guards (needs the regroup logic that did not help as a target-scoring change, but this is a different trigger and a concrete destination).
2. **Bank earlier and in small bags before guards arrive**: in road_of_riches the opponent had nobody at the altar at r100 and 3 by r250; our carriers held 14, 22, 71, 50 at r150 at distance 13. A lower threshold plus a bank trip while the altar is empty may move the first 100 to 200 gems (the opponent banked 200 by r200).
3. **A second altar** when the map has more than one and the first is guarded (not checked how many of these maps have one).
4. **Look at 00contest** (collected 0).

Test: the `t10_226` panel again, with metric "games with 0 banked" and "mean banked" (baseline 5 of 50 and 382), then the strong panels; the local mirror cannot show this because the weak bots do not guard altars.
