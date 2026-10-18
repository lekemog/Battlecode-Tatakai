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

## Sun 18 Oct ~01:30: state at hand-off
- **Live: v12m (version 84).** Best proven: no candidate beat it in paired top-100 scrims.
- **Strongest untested candidate: `bots/v16g`.**
  - Contents: Tavi draft (Varg, Stellar, Tavi, Cassi, Ren), dash used for travel, skipping camps that need long respawn waits, and a solo→pack fallback for unseen maps.
  - Local results: 17/34, +92 vs v12m. Its W21 scrim was stopped.
- **v15e** (expected-value banking from the learned danger model): local 18/34, +59. W19 was 0/25 vs 0/25; margins never finished downloading.
- **Rejected:** v15a (full opponent model), imitation-learned camp choice, solo/multi-squad farming, altar locks with wards, Varg-first draft.
- **Key measurement** (`tools/replay/actrate.py`): our champions idle about 30% of rounds against 8% for top teams. On rows, 21% of our time is spent waiting at dead camps (6.5% for top teams).
- **v16m** = v16g + v15e EV banking. Local bench vs v12m: v16m TOTAL 20  margin +124

## Sun 18 Oct ~02:45 UTC: v16n deployed (audit-driven fixes on v16m)
From the audit of 39 recent ranked games (440 deaths, 4364 gems lost):
- **Altar deaths lost 1728 gems (40%).** `bank()`: for bags of 60 or more, the 12-round "unsafe" cap is removed and the learned danger (>.25) counts as unsafe. The tribute-cancel cap of 3 is removed for big bags.
- **Fights taken while outnumbered: 26% of deaths.** `handle_enemies()`: not favourable when enemies outnumber us by 3 or more away from home.
- **Cassi & Issac linked deaths: 18%.** Cassi needs a 1.3× edge to fight.
- **Caught farming as enemies closed in: 21%.** Evade starts at enemy range +3, where it used to be +1 outside defensive mode.
- **Local result vs v16m:** 18/34, −17 (neutral, so no regression). Self-play can't show the gain because v16m doesn't invade like ranked opponents do. It will be judged on ranked results.

## ~02:35 UTC: v16o deployed (contest fix on v16n)
The audit now covers 65 games (851 deaths). **Contest alone accounts for about 500 deaths**: 10 games, 2 wins, ~50 deaths per game. Most games end 0–0 and are decided on the gold tiebreak, and most deaths were a lone farmer (no ally within 5) caught by 1–2 enemies.

Fix, applied on gold-only maps only (`siege_group>=0`; other maps are unchanged):
- Solo farmers stay on our half.
- A champion with no ally within 6 never takes a fight away from home.

**Local contest result vs v16n:** won both sides on the gold tiebreak, 9830 vs 7960 and 8445 vs 5545 gold, with fewer deaths in one game.
- **v16p rejected:** counting enemy focus in the fight calculation and never letting Cassi fight alone went 11/34, −184 locally vs v16o (too cautious). **v16o stays live.**

## ~04:20 UTC: audit report and status
Full report: `results/match-audit-2026-10-18.md`.
- **Live:** v16o.
- **Rejected:** v16q and v16r (more caution = worse locally).
- **Next focus:** farming pace in top-100 games (18 of 50 losses had ≤2 deaths).

## ~05:00 UTC: loop run 2. Cycle 1 audited, v16s deployed (version 90)
- **Cycle 1 (v16o vs top 100):** 100 games decoded, 12 wins.
  - Deaths: farm_caught 25%, outnumbered 23%, linked Cassi/Issac 12%.
  - 30 of 88 losses had ≤2 deaths, so they were pure farming races.
- **Finding: the draft on 3-pick maps** (collision, expanse, fragment, packs).
  - We drafted Varg, Stellar and Tavi, which is 3 bodies.
  - The top-100 opponent had Cassi & Issac in **28 of 28** games, so they had 4 bodies. Their usual pick is Cassi, Stellar, Varg.
  - We won 4 of those 28 games.
- **Finding: corners pace.** We never take the 22-gem single camps; opponents take 8 to 17 per game. Across the cycle our score timelines are identical (the bot is deterministic).
- **v16s:** the 3-pick draft order is now Cassi & Issac, Varg, Stellar, Tavi, Ren.
  - Local result vs v16o: 15/34, −18. On the 3-pick maps it was only 2 of 8, so self-play disagrees with the ladder.
  - Deployed anyway to test it on the ladder: cycle 2 (`c2_v16s`, 30 groups vs the top 100). If cycle 2's 3-pick results don't beat cycle 1's 4/28, revert to v16o.

## ~06:20 UTC: loop run 3. v16s reverted, v16t deployed (version 92)
- **Cycle 2 (v16s):** 24 of 150 wins.
  - On the 3-pick maps it changed, v16s won 3 of 36 (v16o: 4 of 32), with an average gem margin of −525 (v16o: −434). **Draft change rejected.**
  - The extra wins came on maps the change didn't touch (stampede, pilgrimage, ambush), so they're opponent noise.
- **Cycle 2 audit:**
  - farm_caught: 26% of deaths.
  - Linked Cassi/Issac deaths: 17%.
  - farm_caught deaths mostly happen against 1–2 enemies with the logged action still `farm`. The fight is judged favourable, but the enemy stays outside our range and pokes, so `handle_enemies` returns false and we keep hitting the camp.
- **v16t = v16o + "engage":** if the fight is favourable and an enemy within its range+1 can hit us, we move in and fight it.
  - Local result vs v16o: **18/34, +26**.
  - Deployed. Cycle 3 is `c3_v16t`.

## ~08:00 UTC: loop run 4. Paired testing, item finding, v16v
- **Cycle 3 (v16t, unpaired):** 17 of 150 wins. Unpaired cycles vary too much with the opponents to compare bots, so testing is now **paired** (`tools/paired.py`): every bot plays the same top-100 teams on the same maps, one after another.
- **Cycle 4 (paired, 10 teams, 50 games each):** v16u 6, v16t 6, v16o 3.
  - Only 9 games had different outcomes across the three bots, and v16t/v16u took 6 of them. **The "engage" change beats v16o.**
  - v16u = v16t + Issac is never the lone gold farmer + Issac follows Cassi in solo play. Its outcomes were identical to v16t's; locally it was +6.
- **Idle time is no longer the gap.** On corners/expanse/rows we act in 78–84% of rounds, the same as the opponents.
- **The gap is items** (80 top-100 games, round 300):
  - **Max HP:** opponents grow from 909 to 1126; ours stays at 830.
  - **What they buy:** Power, Durability of Health (~100), Bruiser of Health (~83) and Jungle (~120).
  - **What we buy:** mostly Monster plus Power, and no health at all.
- **v16v = v16u + build Jungle, Power, Durability of Health, Power.** Local result vs v16u: 17/34, **+103**.
- **Cycle 5 (paired):** v16u vs v16v on 15 teams. v16v stays live afterwards.

## ~09:30 UTC: loop run 5. Items confirmed, contest siege, v16w live (version 98)
- **Cycle 5 (paired, 15 teams, 75 games each): v16v 10 wins vs v16u 6.** The 8 games that differed went 6–2 to v16v. **The item build (Jungle, Power, Durability of Health) is adopted.**
- **Contest:** in 28 top-100 games we scored 0 gems and won 0.
  - The opponent kills a 200-gem monolith at rounds ~420–1000, then again every ~150 rounds, and reaches 1000.
  - Our `siege_group` was computed but never used.
- **v16w = v16v + siege mode** (gold-only maps only):
  - From round 300 the team stages 5–6 tiles from our monolith and attacks once 3 are there or after 12 rounds staged. While the monolith is respawning, everyone farms gold.
  - Allies escort a visible carrier with 100+ gems. The carrier waits up to 20 rounds for the escort before walking to the central altar.
  - Bugs found locally along the way:
    - A lone carrier was killed and the enemy got the bag.
    - The head-count only saw 2 allies because vision is short.
  - **Local contest result vs v16v: won from both sides, 600–200 and 600–0** (it lost both before).
- **Cycle 6 (paired, 10 teams):** v16x, v16y and v16w. v16w stays live.
  - **v16x:** on swirl, deaths cluster on the central 36-gem camps. A death near a contested group (enemy_d ≤ home_d+4) now cuts its score ×0.45 (was ×0.7).
  - **v16y:** first emblem per champion, as top teams open: Ren/Ryth Bruiser of Health, Varg Jungle, everyone else Power. Then Durability of Health.

## ~09:15 UTC: map study and v17g (scenario detection by map features)
Leke flagged weak maps. `tools/mapstudy.py MAP` compares wins and losses: score race, deaths, pickups by size, bank count and size, max HP, opponent drafts.

| Map | Ranked win rate | Diagnosis |
|---|---|---|
| stampede | 49% | The only gems are a non-regenerating 360-gem herd (12 elks). Top teams take it 3 times (1080 total). Our pairs rejected it, and in losses our first tribute came at ~round 1660. |
| contest | 19% | The only gems are monoliths. We never sieged them (fixed in v16w). |
| eight | 38% | One central altar. 15k gems lost in bags over 42 games, mostly carriers alone at the altar. We bank 4 times a game, they bank 17. |
| collision | 26% | Both altars sit on the mirror line. 10.7k gems lost in bags. |
| corners | 32% | A farming race: they take 17–22 single 22-gem camps a game and bank 26 times with small bags; we bank 9 times with big bags. Still open. |

**v17g = v16w + three behaviours, each triggered by map features (no map names, so it generalises to unseen maps):**
1. **Big single gem source** (a monolith or a group with 8+ camps):
   - The last slot plants a permanent ward next to it (wards don't expire), so we can see it being weakened and finish it.
   - Everyone else keeps a ward pushed toward the enemy for early warning.
2. **All altars contested** (at most 2 altars, each within 3 steps of equidistant from the two spawns, measured from walkable neighbours):
   - Bag-less allies escort a carrier (40+ gems) when enemies are visible.
   - A carrier facing enemies alone backs off to regroup for up to 12 rounds.
3. **Gold-only map:** the siege from v16w.

**Rejected along the way:**
- v17b: one pack on herd maps (it died to the herd).
- v17c: a weakened-herd rule without vision (no change).
- v17e: had a bug where the contested-altar flag was true on every map; it went 13/34, −43 locally.

**Local result vs v16w: 21/34, +191.**
- Stampede, contest, swirl, packs, pilgrimage, rows, ambush and interlock: won from both sides.
- Still losing: corners, lanes, monolith, elkring.

**Cycle 6 (paired, 15 teams):** v16w vs v17g. v17g stays live.
