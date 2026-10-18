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

## ~09:30 UTC: v17i, plus ward and banking experiments (local)
- **v17i = v17g + the bug fixes from ChatGPT's map review** (see `results/claude/reply-map-review-2026-10-18.md`):
  - Siege protections now cover any bag of 40 or more, so a split reward is protected.
  - The `bag_since` timer resets whenever the bag is empty.
  - The herd-ward runner gives up after 80 rounds.
  - Local result vs v17g: 16/34, +2, a perfectly mirrored split, so no behaviour regression. **v17i replaces v17g in paired c6** (v16w vs v17i, 15 teams). v17i stays live.
- **Forward wards: net positive overall, but they cost pace on corners and lanes.**
  - v17j (v17i with forward wards off): 10/34, −166 vs v17i.
  - The cost: uncontested corners takes 654 rounds to 1000 with wards vs 529 without.
  - Placing a ward is not an action cost: rounds with a ward placement have more moves than average.
  - It is also not the altar watch: v17n (altar watch ignores ward-only sightings) had identical pace.
  - The likely cause is extra fights and reactions to enemies we now see. Not tuned further, to avoid overfitting self-play.
- **Rejected:**
  - v17k (wards only on our half): 18/34, −27, and it lost stampede both sides.
  - v17l (minimum bank bag 60 → 40): 18/34, −1, no pace change.
  - v17m (re-place a ward only when ours is 10+ tiles away): mixed pace.

## ~09:55 UTC: c6 result, and an audit of unbounded waits and retries (Leke's request)
- **Paired c6 (15 teams, 75 games each): v16w 14 wins, v17i 13.** The 13 games that differed split 7–6, so the local +191 did **not** carry over.
  - Against the top 100, both bots still go 0 on contest (4 games each) and collision (5 each). Eight and stampede are 1–2 wins out of 4–5 each.
- **Stampede ladder replay (v17i vs Gem Simons, `922538fb`):** they cleared the 360-gem herd from round 75 in ~75 rounds, three times. Our herd ward was in place, but no rule acted on what it showed.

**Every wait, retry or hold state in v17i, and its bound** (code labels in brackets):

| State | Before | Now (v17u) |
|---|---|---|
| Waiting to bank with enemies near (`bank-wait`) | 12 rounds, **unbounded for bags of 60+** | 12 rounds; 80 for big bags |
| Cancelling a tribute | 3 times, **unbounded for bags of 60+** | 3; 20 for big bags |
| Carrier regrouping before banking (`bank-regroup`) | 12 rounds | 12 rounds |
| Siege bag gathering (`siege-gather`) | 20 rounds, but the timer never reset (fixed in v17i) | 20 rounds per bag |
| Siege staging (`siege-wait`) | **unbounded if the staging ring was unreachable** | 40 rounds overall, then attack |
| Escorting a carrier | **unbounded** | 80 consecutive rounds, then 30 off |
| Walking to plant the herd ward (`to-herd`) | **unbounded** (fixed in v17i) | 80 rounds |
| Capturing a reward | **unbounded** (an unreachable or blocked region looped) | 150 rounds, then ban that group for 60 |
| Retreat or heal at spawn | Bounded by healing | Unchanged |
| Shopping loop | Halving loop, bounded | Unchanged |

- **Tighter bounds tested and rejected, because they cut off legitimate long actions:**
  - v17o/p (a target watchdog that bans a camp after 70 or 30 rounds without progress, plus a 30-round capture cap): 18/34 −70 and 15/34 −83.
  - v17q/r (capture cap at 30–60 rounds): lost stampede (the herd capture is long) and swirl.
  - **v17u keeps only the lenient caps: 16/34, +36 vs v17i, with no map regressing on both sides.**
- **v17v = v17u + two changes:**
  - Herd vulture: a seen herd below 50% HP becomes the top-priority target.
  - Fix for ChatGPT's finding that `solo_target` used the single weakest visible camp's HP instead of the group's remaining HP.
  - Local result vs v17u: 16/34, −23.
- **Paired c7 (10 teams):** v17u, v17v and v17i. v17u stays live.

## ~10:35 UTC: faux top-100 gauntlet, contest vulture (v17w), single-camp solo (v17x)
- **Faux top-100 style bots** (each a variant of our code that copies one observed habit):
  - `fz_herd`: one pack goes for the biggest objective first; siege from round 150.
  - `fz_solo`: always solo, banks 36–70-gem bags, bolder camp choice, top-100 draft (Cassi & Issac, Ren, Ryth, Stellar, Varg).
  - `fz_hunt`: fights at need 0.45 and chases bags of 30+ up to 11 tiles away.
  - `tools/gauntlet.py CAND fz_herd,fz_solo,fz_hunt` plays 102 games (~15 min).
- **Does the gauntlet predict the ladder?** It got 2 of 3 known paired results right:
  - v16o 52 < v16t 55 ✓; v16u 55 < v16v 60 ✓.
  - v16w 61 vs v17i 67, but the ladder had them tied (14–13). ✗
  - Used as a screen, not as proof.
- **Ladder contest replay** (v17i vs "y", `73a00a9e`): our siege from round 300 took ~350 rounds per kill. We died constantly and fed them gold. The opponent never sieged; it took every reward we softened (0–600 gems, 2345–13225 gold).
  - **v17w:**
    - Vulture any visible monolith under 50% HP.
    - Siege only from round 600.
    - Abandon a siege with no kill after 150 rounds, then farm gold for 150 rounds.
  - Contest results: beat `fz_herd` from both sides, split 1–1 with v17u, and our gold rose ~4.5k → ~7–8k. Gauntlet 67, +527.
- **`fz_solo` beat v17u on corners, collision and packs from both sides.**
  - **v17x = v17w + a single-camp rule:** if ≥60% of gem income comes from 1-camp groups (corners 0.67, collision 0.65, lanes, rushbait), farm solo and bank 36–70-gem bags.
  - **Gauntlet 72/102, +549 (the best so far).** Collision vs `fz_solo` flipped from 0–2 to 2–0.
  - Vs v17w: 19/34, +15; corners 2–0 (1014–600 and 1016–744), rushbait 2–0.
- **Rejected:**
  - v17y (top-100 draft with Ryth instead of Tavi for 4+ picks): gauntlet 57.
  - v17z (bolder solo camps on single-camp maps): gauntlet 70, no gain over v17x.
- **Paired c7 (10 teams):** v17u, v17w, v17x. v17x stays live.
- **Disk:** the disk filled up (decoded replays take ~17 GB). Local benches now delete their replays after scoring.

## ~11:00 UTC: c7 result, margins, corners gem farmers (v18c)
- **Paired c7 (10 teams, 50 games each): v17u 10, v17w 10, v17x 8.**
  - v17u and v17w had identical results in all 50 games. Contest was 0/3 for all three.
  - v17x's only differing games were 2 losses, on rushbait and lanes, where its single-camp solo rule applies. **v17x rejected; v17w is live.**
- **Paired margins** (`tools/pairmargin.py`, games where both arms are decoded):
  - c6: v17i − v16w = **−23 gems on average** over 32 games (better in 16, worse in 12). A wash.
  - Per map, eight (−570 vs −169) and elkring were worse; packs, pilgrimage and lanes better. Only ~2 games per map, so mostly noise.
- **Ladder corners losses (c6, 3 games, both sides had zero deaths):**
  - Big groups were equal: both took 3 × 96 plus the 72s.
  - Small camps were not: **they took 14–15 single 22-gem and 12–13 36-gem camps; we took zero 22s and 6 36s.**
  - Their max HP at round 300 was 1150–1294 vs our ~1000.
- **Ladder collision losses:** they took 29–40 22-gem camps vs our 13–16, with 4 bodies (Cassi & Issac) vs our 3. We died 4–7 times; they died 0–4.
- **v18c = v17w + 2 gem farmers on single-camp maps** (5+ picks only): the two sturdiest non-carries outside Cassi & Issac solo the single camps on our side while the rest form squads.
  - Uncontested corners pace: **654/658 → 602/628 rounds to 1000** (other maps unchanged).
  - Gauntlet 69 (+538) vs v17w 67. Vs `fz_tank`: 21 vs 18.
- **Rejected:**
  - v18a: health-first frontliners, gauntlet 64.
  - `fz_tank` (health-stacker faux bot): loses to v17w and v18c locally.
- **Paired c8 (15 teams):** v18c vs v17w. v17w stays live after.

## ~11:40 UTC: opponent style, weak-map focus, top-vs-top study
- **Opponent style** (735 decoded top-100 games, by round 250):
  - **Passive** (≤3 kills on us, <25% of their time on our half): 71% of games. We win 16%. They lead by +60 gems at round 250.
  - **Aggressive:** 29% of games. We win 8%. They kill us 5.3 times; we kill them 2.1.
  - We spend 4% of our time on their half; they spend 10% on ours. **Leke is right: the bot is conflict-averse.**
- **v18f = v17w + RAID mode.** If the opponent is passive (max aggression < 25, ≤2 deaths) and leads by 40+ on a big map (≥50 wide) from round 120:
  - Prefer their-side camps.
  - Fight at need 0.5 without a bag.
  - Hunt bags of 30+ within 11 tiles.
  - Called off after 3 deaths.
  - Aggressive opponents still trigger the existing defensive posture.
  - Gauntlet 65 (v17w 67). Corners vs v17w won both sides (1068–790, 1068–948).
  - v18e (raid on all maps) was rejected: gauntlet 59, lost collision both sides.
- **How top teams win the weak maps** (`tools/howtheywin.py`, 9–10 top-vs-top games per map, winner vs loser):

| Map | Winner deaths | Loser deaths | Other differences |
|---|---|---|---|
| collision | 2.5 | 9.9 | Winners take 35.6 22-gem camps vs 24.7, and 24 banks vs 14. Draft: Cassi & Issac, Ren, Stellar |
| corners | 3.7 | 9.4 | Max HP 1290 vs 1081 |
| eight | 5.8 | 14 | Winners first tribute ~106 vs 188, bank 20 times vs 6, take 11 44-gem camps vs 4.5 |
| contest | 21 | 66 | Winners take ~4 monoliths. Their drafts lean Prism/Tavi |
| stampede | — | — | Winners take the herd 1.7 times; drafts lean Prism + Cassi |

- **Conclusion:** on every weak map, the side that wins the fights wins, even on "farming" maps. Winners field 1200–1290 max HP. Their 6-pick draft is Cassi & Issac, Ren, Ryth, Stellar, Varg (Ryth, not Tavi).
- **Testing is now focused on the weak maps** (`paired.py --maps collision,corners,contest,eight,stampede`):
  - **c8w:** v18c (corners gem farmers), v18f (raid), v17w.
  - **c9w:** v18i (winners' 6-pick draft), v18j (health items for frontliners), v17w.
  - These hypotheses can't be judged locally: the faux bots are our own code, and they already rejected Ryth (v17y, gauntlet 57) and health (v18a, 64).

## ~11:50 UTC: c8w result. v18f (raid) live as version 116
- **c8w** (weak maps only, 10 top-100 teams, 50 games each): v18f 4, v18c 2, v17w 2.
  - The only games that differed were 2 corners wins for v18f; v18c and v17w lost both.
  - All three went 0/10 on collision, contest and eight, and 2/10 on stampede.
- **Deployed v18f (raid).**
- **c9w** (weak maps only):
  - v18k = v18f + winners' 6-pick draft (Ryth over Tavi) + health items for frontliners.
  - v18l = v18f + health items only.
  - v18f is the baseline and stays live afterwards.

## ~12:30 UTC: weak-map fixes (contest convoy, collision solo), c9w/c10w
- **c8w replays, weak maps, ours vs theirs:**
  - **Contest:** they bank 5 × 200 per game; we bank 0. Our 200-gem carrier walked alone from the monolith to the central altar and died to 2 enemies (e.g. `75c258e9`).
  - **Eight:** we die 8–24 times per game, they die 0–8. 180 of 241 deaths were on our own side or at home. We bank 2–7 times; they bank 14–20 times.
  - **Collision:** they take 29–37 22-gem camps and bank 20–28 times (first tribute ~r50, ~40-gem bags); our pack of 3 takes 13–22 and banks 4–15 times.
- **v18m = v18f + monolith-bag convoy.**
  - A carrier with 100+ gems recalls or walks home and sets a rally flag (`shared[slot]=255`). Allies come to it, and it walks to the altar only with 2 or more allies within 3. Caps: 60 rounds for the convoy, 70 rounds for each rally. The flag is cleared once the bag is under 100.
  - The first version left the flag set after banking (allies rallied forever). That was caught locally and fixed.
  - Contest locally: 3/4 vs v18f and fz_herd. Gauntlet 86/136 (v18f 84).
- **v18n = v18m + collision-type rule:** on maps with 3 picks and ≥60% single-camp income, farm solo and bank 36–70-gem bags.
  - Collision locally: 5/6 vs v18m, fz_solo and fz_hunt. Gauntlet 88/136.
- **Rejected locally:**
  - v18k (Ryth draft + health items): gauntlet 68.
  - v18o (v18n + Ryth draft): lost eight 160–1106 to v18n. Our code doesn't play Ryth well, so copying the winners' draft doesn't transfer.
- **Ladder:**
  - c9w (weak maps): v18m, v18l (raid + frontline health), v18f. v18m stays live.
  - c10w after it: v18n vs v18m, 15 teams.

## ~12:40 UTC: eight and stampede diagnosis
- **Eight** (c8w snapshots): our champions are strung out across the map and picked off one at a time. Tavi and Cassi were alone at x=24 while the others were at x=1–13, and badly hurt champions linger instead of healing.
  - **v18p** (brawl cohesion: regroup on the nearest ally before heading to a far target) changed nothing locally. Eight is decided by starting side in self-play. Not promoted.
- **Stampede** (c8w): in 9 of 10 losses the enemy cleared the 360-gem herd with **1–2 champions over 100+ rounds**, and we were never near it.
  - **Cause:** our herd ward landed at (51,18), 7 tiles from the herd and behind walls, so it never saw the herd and the vulture never fired.
  - **v18r = v18n + a herd ward placed where it actually sees the herd:** it picks the tile with the most herd camps in hypothetical ward vision (`ward::visible_tiles_from`), needing at least half of them. It now lands at (52,19) and sees the herd.
  - Stampede is also decided by starting side in self-play, so the ladder decides.
  - **v18q** (one pack races the herd) lost to the vulture locally from both sides. Not promoted.
- **c10w** (after c9w): v18r vs v18m, 15 teams, weak maps.

## ~12:45 UTC: weak-map deep diagnosis. No blind shipping; issues #15–#19 opened
- Leke asked for no more blind shipping. The work order is now **diagnose → write a GitHub issue with the evidence → fix → verify the mechanism → paired ladder test**.
- **New tools:**
  - `tools/weakmap.py MAP`: us vs them per map — picked vs banked gems, deaths, zone time, who starts fights, posture share, HP.
  - `tools/altaruse.py`: tributes per altar and bag hold time.
- **Common pattern on the 5 weak maps:** the middle (central altar or objective) decides the game. They spend 28–59% of their time there (us 14–29%), start 1.4–3.8× more fights, and bank about 90% of the gems they pick up (us 14–54%). We are 250–370 max HP behind everywhere. See #15.
- **#16 Corners:** 96% of our tributes are at the corner altars (bags held 79 rounds) vs 85% of theirs at the centre (21 rounds). The cause is `bank()` treating the centre as a kill zone permanently ("seen within 20 rounds"). Fix candidate v18u: avoid an altar only when enemies are there now and danger > .25. Verified locally: central tributes went from 0–3 to 10–11 per game, and vs fz_solo the result improved from 0–2 to 1–1.
- **#17 Opponent model:** we are in defensive posture for 65% of contest games and 50% of eight; the stun-draft prior starts us at aggression 45. We concede the middle.
- **#18 Conversion.** **#19 HP gap.**
- **Live:** v18t (diagnostic trace build; behaviour identical to v18f). Diagnostic scrims d1: 30 top-100 teams × the 5 weak maps.

## ~13:15 UTC: issues #16–#19 addressed one by one (evidence → fix → mechanism check)
| Issue | Root cause (evidence) | Fix | Mechanism check | Gauntlet |
|---|---|---|---|---|
| #16 corners | 96% of our tributes at corner altars, bags held 79 rounds (them: 85% at the centre, 21 rounds). `bank()` treated "seen within 20 rounds" as a kill zone. | v18u: avoid an altar only when enemies are there now and danger > .25 | central tributes 0–3 → 10–11 per game | 93 (live v18f: 84) |
| #17 opponent model | defensive for 65% of contest and 50% of eight; in defensive windows our kill ratio is worse (eight: 3.3 vs 0.7 deaths per 100 rounds). Stun-draft prior and "enemy in our half" made us turtle. | v18v: drop the prior and half-map evidence; defensive = group up and keep the middle (need 0.7 with 2+ allies) | defensive share 0.44 → 0.11 (contest), 0.35 → 0.20 (eight); 4/4 vs fz_hunt (was 2/4) | 94 |
| #18 conversion | collision: lost bags median 58 gems, held 71 rounds (theirs bank at 22). Bug: `contested_altars = 0` on collision (one walled altar). | v18w: carry `clamp(22+ad-nearest,22,60)` on contested-altar maps; ignore unreachable altars. v18x: + monolith convoy | collision vs fz_solo 2/2 (was 1/2) | 96 / 96 |
| #19 HP | our champions at **base** max HP at round 300 (Varg 1000 vs 1381, Ren 900 vs 1467) | v18y: frontliners open Durability of Health | — | 86 (gauntlet bias, so this one goes to the ladder) |

- **Ladder:** d1 diagnostic traces (v18t) are finishing. Then t1: v18x vs v18t (live behaviour), weak maps, 15 teams. Then v18y vs v18x.

## ~13:55 UTC: decision traces → fight evaluation bug (#20)
- **d1** (v18t trace build, 150 weak-map games vs 30 top-100 teams): 14 wins. Collision 4/30, stampede 8/30, corners 1/30, eight 1/30, contest 0/30.
- **Traces** (`tools/audit/traces.py`, 391 deaths):
  - **41%** came within 25 rounds of a fight we rated ≥1.5× favourable.
  - 33% came while evading or retreating.
  - The killers were casters (Stellar 35 strength / 298 focus, Cassi 30/274, Tavi 40/394).
- **Root cause:** `handle_enemies` / `bank` / `threat` value enemies (and allies) by strength alone.
- **Calibration** (`tools/audit/fightcal.py`, 1629 decisive top-100 engagements):
  - Adding focus raises AUC from .773 to .823.
  - At our current `need` of 0.6 we take fights we win ~25% of the time. Break-even is ~1.3.
- **Candidates:**
  - v19a: power = strength + 0.5·focus.
  - v19b: v19a + need 1.3 (0.9 near spawn).
  - v18z: v18x + ChatGPT review fixes (stale capture timer, escort counter).
- **t1 so far:** v18x 6/75 on the weak maps (corners 0/15). The v18t arm is still running; paired comparison to follow. t2 (v19b, v19a, v18x) queued after.
- **GitHub:** issue #20 opened. Replied to ChatGPT's review on #6. No teammate replies yet on #15–#19.

## ~14:40 UTC: v19b live (Leke's call), top-10 fight study, early-gold question
- **v19b deployed as version 122/123.** It's being tested on the exact t1 teams and maps (`paired.py --same-as t1_v18x`). v19c (strike-first rule) follows on the same games.
- **Top-10 vs top-10 fights** (47 games, 1831 engagements):
  - Strength + 0.5·focus predicts the winner at AUC .859 (strength only .780).
  - **Striking first is worth +10 to 25 points:** initiators win 67% at power share .5–.6.
  - Across all 163 top games, AUC keeps rising to ~.84 with focus weight 1–2.
- **Early gold** (151 top-100 games):
  - Gems are level until round 100, but they earn +26% gold and hold 2× our items at round 50.
  - When they lead by 150+ gold at round 150, they win 98%.
  - v19d (gold weight 0.4 for the first 200 rounds) gave mixed uncontested pace: corners slower, monolith faster.
  - Next: earlier first item (shop on the way past spawn, earlier shop-recall).
- **Traces:** `results/traces/d1_deaths_by_decision.txt`.

## ~15:10 UTC: v19b/v19c rejected on the ladder; v18x live (version 126)
- **Identical 75 weak-map games** (same 15 teams, same maps): v18x **6**, v19b 3, v19c 1. All the wins came on stampede and collision.
- **Why** (traces): v19b cut deaths after taken fights (45% → 27%) but evades much more (evade/retreat 10% → 17% of decisions, ~120 evade episodes per game). The lost farming and racing time cost more than the fights it avoided.
- **Lesson:** engagement-outcome calibration ignores the cost of disengaging.
- **Kept:** the focus-inclusive valuation might still help in `threat()` / danger only. To test with the old thresholds.

## ~15:40 UTC: early economy (#21), v19a/v19f tests
- Opened **#21** (early economy): they earn +26% gold and own 2× our items at round 50. Gems are level until round 100.
- **v19f** (shop-recall at 110 gold before round 250): mixed uncontested pace.
- **Ladder tests on the identical t1 games:** t1d = v19a (focus in fight valuation, old 0.6 threshold), then t1e = v19f. v18x stays live.
- **GitHub:** no new teammate or ChatGPT comments since 14:00. ChatGPT created branch `chatgpt/faux-execution-lab-20261018` with no commits yet.
- **Disk:** removed re-downloadable decodes of strong-map / old-cycle games again (6.4 GB).

## ~16:05 UTC: v19f live (version 131): earlier first items
- **Identical 75 weak-map games:** v19f **10**, v19a 7, v18x 6, v19b 3, v19c 1. v19f won 7 of the 10 games that differed from v18x.
- **Ladder check of the v18x fixes:**
  - #16: central-altar tributes 6% → 38%. It works, but only partially.
  - #17: defensive share barely moved.
  - #18: bag conversion unchanged.
- **Next:** v19g (v19f + focus valuation) on the same games, then a strong-map regression check (v19f vs v18x).

## ~17:10 UTC: v19g result; Kurians' Claude joined
- **Same 75 games:** v19f **10**, v19g 7, v18x 6.
  - v19g is a package (focus valuation + lifecycle resets).
  - It won eight 2 times (the first eight wins ever against these teams) but lost corners and collision.
  - **v19f stays live.**
- **v19i** = v19g with focus valuation applied only on single-central-altar contested maps (eight-like). Queued after r1 (strong-map regression check of v19f vs v18x).
- **Kurians' Claude (#22, branch `kurians/top-openings`):** studied contest/eight openings in the top replays.
  - On eight we have the losers' profile: an early gold lead (r50) turns into deaths by r150, and we first bank at ~r140 (theirs ~r90).
  - On contest we are 2.6× behind on gold by r150.
  - Its `extract.mjs` fix is merged.

## ~17:20 UTC: r1 strong-map check; Kurians' follow-up
- **r1** (7 teams × 5 strong maps): v19f 4 vs v18x 6. Of the 4 games that differed, v19f lost interlock, fragment and swirl and won pilgrimage. A small sample, but early economy looks map-dependent. **Net: +4 weak maps, −2 strong maps.** v19f stays live.
- **Kurians (#22), all five weak maps from the top-vs-top openings:**
  - Collision: the gap is conversion after r150.
  - Corners: winners hold more items early, and Ryth was in 10/10 winning drafts.
  - **Stampede winners skip early shopping** to race the herd. On our identical games, stampede wins were v19f 5 = v18x 5, so no harm seen yet.
  - Nobody wins any of these maps by invading.
  - Their opponent-style model spots invaders (AUC 0.85–0.91 by r60–100), but only ~9% of top opponents invade.
- **Running:** t1i (v19i, focus valuation on single-altar maps only), then **ct** = a contest-only paired test, v19j (contest solo farmers may use the middle third) vs v19f, 10 teams × 5 contest games each.

## ~18:30 UTC: GPT ("Astra") code recommendations (#15)
- **Rec 1, carrier-aware execution → v19m:**
  - A carrier with 40+ gems doesn't pursue.
  - Pursuit returns true only if it acted.
  - Includes rec 5 (death clears capture state).
  - Gauntlet 99 (+907) vs v19f 100 (+871).
  - Queued for a ladder test (t1m) after t1i and ct.
- **Rec 2, current-HP group estimate → v19l:** gauntlet 87. Rejected for tonight.
- **Recs 3/4 (convoy plan, route ranking):** designs only. No time to validate before the freeze.
- **Ladder queue:** t1i (v19i), ct (contest-only, v19j vs v19f), t1m (v19m). v19f stays live.

- 18:40 UTC t1i: v19i 6/75 (eight 2, corners 0, collision 0). The corners/collision loss is not from focus valuation; suspect v18z resets. v19f stays live.

- 19:20 UTC: the ct test never ran. cambc rejects groups with repeated maps ("Choose exactly five different maps", HTTP 400), and paired.py logged every error as "quota wait", so v19j sat live as an untested arm from about 18:01 to 19:20. Fixed: paired.py now exits on HTTP 400. v19j is re-queued as t1j (identical t1 games; its contest results come from the same 15 games) after t1m (v19m, now live as the test arm). The ladder keeps v19f.

- 19:30 UTC t1m: v19m 8/75 (corners 1, collision 1). Not deployed. t1j (v19j) running.

- 19:55 UTC t1j: v19j 11/75 (contest 0; the +1 is on stampede, noise). Not deployed. v19n (v19f + eight-only focus, otherwise identical maths) is in test as t1n.
