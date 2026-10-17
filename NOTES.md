# NOTES: findings and experiment log

Last updated: Sat 17 Oct, about 19:20 (Irish time). Ladder rank is roughly 245–280.

## How the bot works (bots/v12c/src)
- `draft.cpp` picks the champions by team size:
  - 3 picks: Varg, Stellar, Cassi & Issac, then Ren.
  - Otherwise: Ren, Stellar, Cassi & Issac, Varg, Ryth, then Prism.
  - Wolf-pack maps (rows) use their own order.
- `bot.cpp` is one champion controller with these parts:
  - `observe()` reads the map and visible units, and keeps an *aggression* score in shared memory. Being hit or killed raises it; at 40 or more the team goes defensive. It decays over time.
  - Farming either picks camps solo, by score per round, or moves as a pack/squad with a leader.
  - `bank()` decides when to tribute gems and walks to an altar.
  - `combat()` handles focus fire. Cassi is targeted first because Issac dies with her.
  - `shop()` buys Monster emblem, Power, Power, Durability (main stat), then Power shards.
- Gems only score once they are tributed at an altar. The first team to 1000 wins. Tiebreaks are tributed gems, then lifetime gold, then kills. A death gives the killer the gems you carry plus 50 gold.

## Testing method
- `tools/abrun.py SET bot1,bot2 --keep BEST --opps opps.json` submits each bot in turn and plays a 5-map group against each of 5 real ladder teams. Results go to `groups.json`, and the keep bot is resubmitted at the end.
- Opponents update their bots, so a candidate is only compared with a baseline run **back to back** against the same opponents.
- The quota is 30 scrim groups per rolling hour.
- `tools/bench.py A B` runs local A-vs-B on all 17 maps from both sides (34 games). `tools/speed.py` measures farming pace with no opposition.

## Results (real-ladder scrims, wins out of 25)
| Round | Opponents | Result |
|---|---|---|
| W5 | ranks 38, 105, 113, 265, 275 | v11a 6, Treasure-first 3, Treasure + Durability-Health 5, Jungle-frontline 5. **Treasure-first rejected.** |
| W6 | ranks ~113–275 | **v12a 10** vs v11a 8. Adopted. |
| W7 | same as W6 | **v12c 12** (adopted), v12d with Jungle emblem first 8 (rejected). |
| W8 | same as W6 | v12f 12, v12c 12 (tie). v12f won contest for the first time ever; it lost swirl to Tokyo. |
| W9 | 5 teams that beat us in ranked, on contest/stampede/swirl/fragment/elkring | **v12c 15**, v12f 13. Contest: v12c 2/5, v12f 0/5. **v12f rejected.** |
| W10 | **top-100 only** (ranks 31, 53, 67, 71, 98) | Both 0/25. Gem margin: v12h −11641, v12c −11853. 17 of 25 games were identical. Tie, so not adopted. |

## Key findings
1. **Altar-freeze bug (fixed in v12a).** If an enemy had recently been seen near the nearest altar, `bank()` routed to a different altar. When that route was blocked by our own teammates, the path search returned "unreachable" and the champion stood still. On collision this went on for about 100 rounds. The fix: when nothing is reachable, path through units, and fall back to the nearest altar. Collision against a passive bot now reaches 1000 at round 608 instead of 815.
2. **Top-50 teams compared with us** (match summaries, `tools/feat.py` and `tools/cmp.py`; see the "Top teams vs us" tab):
   - They buy their first item around **round 45**; we buy around **round 83**.
   - Top-10 first tribute is around round 70 on farming maps; ours is around round 101.
   - They place a ward many times per game (they move it every round); we place none.
   - Their most common first emblem is **Jungle** (30% less camp damage). We open Monster. Jungle-first did *not* help us (W7).
   - Their drafts are almost the same as ours. The most common 5-pick is Cassi, Ren, Ryth, Stellar, Varg, which is what v12c now uses.
3. **Where we lose.** Deaths per game are high on contest (about 58), swirl (about 24), fragment, elkring and interlock.
   - **Contest** is a gold-only map: camps give gold and the gems come from the monolith late in the game. We spread out, get picked off and feed the enemy gold, and they snowball. The winning top team on contest drafted a crowd-control comp (Stellar, Tavi, Prism, Cassi, Ren), farmed gold, then took the monolith.
   - **Collision** was slow because of the altar-freeze bug.
   - **Swirl**: we fight over the central camps early with a 4-pick that has no Varg.
4. **No cross-match learning.** The bot is identical every game. Within a game, its only adaptation is the aggression score, and that forgets in about 80 rounds. v12f halves the forgetting rate and keeps champions on our half on gold-only maps. Locally it beat v12a 19/34 (+76 gems) and 7/10 on the death-heavy maps.

## Ideas not yet done (open for anyone)
- **Contest plan.** Draft crowd control (Tavi, Prism), move as one pack, farm gold on our side, then siege the monolith once stronger. `siege_group` is computed but never used.
- **Wards.** Move the ward forward every round toward the enemy side or the next camp, or leave it on the altar we're about to use.
- **Earlier shopping.** Recall or path through spawn after the first captures.
- **Altar locks** (10 gold). Opponents use about 3 per game; we use none.
- **Teleport crystals** for shortcuts on wall-heavy maps.

## Top-100 farming gap (W10)
On open farming maps with **zero deaths** on both sides we still lose by 300–450 gems:
- corners −142 to −434
- lanes −308
- expanse −468
- ambush −486

In corners vs KratosMessi (match `153c6e14-174d-4cb6-b05d-13bac5e42682`), they captured **42 camps with champions farming solo in parallel**. We captured **14**, mostly the 96-gem central group as a 5-champion pack, and our Stellar collected 0 gems all game.

Tested `v12j` (solo farming on maps ≥70 wide). It was worse locally: gems at round 300 were 269 vs 310, and the benchmark margin was −111. So "just split" isn't it. Our solo camp-safety check (`choose()`: `g.str*clear*.6 > my_hp*.6`) probably rejects the 22–36 gem camps that top teams solo. This is the main open problem.
