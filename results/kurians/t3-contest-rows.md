# T3 (#40): contest and rows on the current bot (Kurians' Claude, 22 Oct)

**Branch** `team/kurians/t3-contest-rows`.

**Candidates** (all copied from the live `v24z`):

| Folder | Change | Verdict |
|---|---|---|
| `bots/kurians-t3-spawnfix` | A farmer standing on a respawning (non-monolith) target group's spawn tile steps to the ring beside it | **Proposed.** Fixes the rows deadlock; neutral on the other 39 maps |
| `bots/kurians-t3-contestrecall` | spawnfix + contest only: low-HP and shop recalls need no visible enemy within 9 tiles | See the contest section |
| `bots/kurians-t3-rowsfarm` | spawnfix + rows only: one champion farms the harmless gold-only flank group | **Rejected locally** (3/10 vs spawnfix 6/10) |

**Tools:**
- `tools/t3fetch.py`: download and decode our ranked games on chosen maps.
- `tools/t3analyse.py`: per-map us vs them: captures by third, deaths by cause, idle share, stand-still streaks.
- `tools/headtohead.py`: a candidate vs a base on every map in a folder, both sides.
- `tools/t3contest.py`: contest A/B with deaths while recalling.
- Earlier: `tools/captures.py`, `tools/openings.py`, `tools/econ.py`, `tools/oppstyle.py`.

**Data:**
- **Ranked:** our games since v24k went live (21 Oct 15:24 UTC), as of 22 Oct. **Contest: 13 games (4 wins). Rows: 16 games (7 wins). All decoded.**
  - Engine-1.0.3 games need cambc 3.0.5's visualiser assets and `v1_0_3` in `tools/replay/extract3.mjs`'s version list (added on this branch).
  - Detailed tables below were first computed on the 11 + 12 games decodable earlier. Rerun on all 29 games, the headline numbers barely move:
    - **Contest:** captures r150 6.7 vs 7.3, r600 22.7 vs 33.3 (middle 15.5 vs 23.7); gold r600 2430 vs 3337; **48.4 deaths per game, 12.2 while recalling.**
    - **Rows:** captures r150 2.3 vs 4.1; gold r150 415 vs 552.
    - **The rows deadlock (≥100 rounds) appears in 3 of our 11 side-A games, all losses.** Only 1 side-A rows game has been played on engine 1.0.3 so far, so "absent on 1.0.3" is not established either way.

**Ranked games by live bot version and engine** (live version from `SUBMISSIONS.md` submit times; a game counts under the last submission before it started):

| Map | Live bot | Engine | Games | Wins | Rows: side-A games / deadlock games |
|---|---|---|---|---|---|
| contest | v24p | 1.0.2 | 2 | 1 | |
| contest | v24u | 1.0.2 | 1 | 1 | |
| contest | v24z | 1.0.2 | 8 | 1 | |
| contest | v24z | 1.0.3 | 2 | 1 | |
| rows | v24k | 1.0.2 | 1 | 0 | 1 / 0 |
| rows | v24n | 1.0.2 | 1 | 0 | 1 / 0 |
| rows | v24u | 1.0.2 | 1 | 0 | 1 / 1 |
| rows | v24v | 1.0.2 | 1 | 1 | 0 / 0 |
| rows | v24w | 1.0.2 | 1 | 0 | 0 / 0 |
| rows | v24z | 1.0.2 | 9 | 4 | 7 / 2 |
| rows | v24z | 1.0.3 | 2 | 2 | 1 / 0 |

- **Contest** behaviour is the same from v24p (its Vesper/Willow contest draft) through v24z; the later versions only change other maps. So the 13 contest games are one cohort, apart from the engine.
- **Rows changed twice in this window:** v24n (smaller banks on rows) and v24u (Varg-first/Willow draft on rows for teams of 4+). So 12 of the 16 rows games (v24u onward) share today's rows code; the 4 earlier ones don't. The deadlock code path (line 1425) is unchanged in all of them.
- The rows and contest averages in sections 2–3 pool all cohorts; the table lets anyone re-split them.
- **Local:** the current 40-map pool (`cambc maps pull`), engine 1.0.2 (cambc 3.0.4).

**Definitions:**
- "Idle" = off spawn, no movement, no health lost, and no camp within 4 tiles losing health.
- "Retreating" = distance to our spawn centroid fell by at least 2 over the last 3–4 alive rounds.
- "Outnumbered" = enemies within 6 > allies within 6 + 1.

## 1. Rows: a respawn deadlock (main finding, fix proposed)
### Mechanism
- **Reproduced locally:** v24k/v24z on the current rows map against v24c, fz_solo, cc_contest and starter-cpp, both sides.
- As **side A only**, one champion freezes on or beside camp group 0's spawn tiles at (18–19, 3–5):
  - v24k: 1055 rounds (Vendetta vs v24c, r606–1661, lost 692–1002), 590, 506 and 192 rounds.
  - v24z: 1438 and 358 rounds.
  - As side B the longest freeze is 15 rounds.
- **The replay shows the cause:**
  - At r606 Vendetta steps onto (18,4), one of group 0's six spawn tiles, while the group's respawn timer has 8 rounds left.
  - The timer reaches 0 around r650, but the group never respawns. An occupied spawn tile delays the whole group (game rules).
  - Its log says `farm` with target group 0 every 5 rounds for the whole 1055 rounds. It waits for a camp it is blocking.
- **Code** (v24z `bot.cpp` line 1425, also in v24k and v24p): `if(!found)goals=grow(g.spawns,1);` is the v21h rule for camps hidden behind walls.
  - A respawning group also has no visible monsters, so the farmer is sent onto the spawn tiles themselves.
  - The existing guard (line 1427 `if(g.reward)goals&=~g.spawns;`) covers rewards, not respawns.

### It happens in ranked play too
In our 12 decoded ranked rows games, a champion blocked a respawning group's tiles for long stretches in 3 of the 8 games we played as side A, all on group 0, all **losses**:
- 6c24d783 vs Lucky Shard: Vesper, **625 rounds** (r886–1511)
- 305fba7b vs test: Vendetta, **310 rounds** (r618–928)
- fdd77f08 vs Mu&Hoon: Ryth, **246 rounds** (r1225–1471)

A pure "didn't move" measure misses these, because the champion shuffles between neighbouring spawn tiles while still blocking.

### Fix and verification (`bots/kurians-t3-spawnfix`, one code line vs v24z)
`if(!found&&!g.monolith&&g.spawns.is_set(me.position())){goals=grow(g.spawns,1)&~g.spawns&~terrain; ...}`
- **Only when standing on a target spawn tile with none of its camps visible.** A live camp occupies its own tile, so this means the group is respawning.
- **Elsewhere the v21h behaviour is unchanged.**
- **Two rejected variants on the way:**
  - An unconditional "never on spawn tiles" version lost both corners games (it stopped champions stepping in to see walled camps).
  - The version without the monolith exclusion lost boss_battle 393–1538, where v24z wins 1023–188. Holding monolith spawn tiles there keeps the monoliths down and the guarded altars usable, so monolith groups are excluded.

**Rows, against 4 opponents × both sides:**

| | v24z | spawnfix |
|---|---|---|
| Wins | 4/8 | **5/8** |
| Longest stand-still | 1438 r, 358 r | ≤ 15 r |

- Side-B games are identical to v24z to the gem.
- The changed game: vs cc_contest as side A, v24z lost 970–1014 and spawnfix won 1000–653.

**40-map head-to-head vs v24z (80 games):**
- 41/80, mean gem margin −1.
- Every map splits like v24z vs itself except **ambush, where spawnfix wins both** (1024–616, 1029–887).
- boss_battle and corners mirror v24z.

### Engine 1.0.3 recheck with mechanism numbers (review follow-up)
Tools: `tools/t3engine103.ps1`, `tools/t3engine103_report.py` and `tools/spawnblock.py` (cambc 3.0.5, 22 games, all decoded as `v1_0_3`). spawnblock counts:
- rounds a non-monolith group was due (timer 0, no live camps) while one of our champions stood on its spawn tiles
- the delay from "due" to the camps actually reappearing
- any champion staying 10+ rounds on a due group's tile (the occupied/unreachable-ring edge case)

| Rows, side A | v24z: blocking rounds | v24z: respawn delay | spawnfix: blocking | spawnfix: delay |
|---|---|---|---|---|
| vs fz_solo | **1426** (group 0 never respawned) | — | 0 | ≤ 1 |
| vs cc_contest | **346** | 347 | 0 | 0 |
| vs starter-cpp / v24c | ≤ 1 | ≤ 2 | ≤ 1 | ≤ 2 |

- Side-B rows games: no blocking for either bot.
- **Results are identical to the 1.0.2 runs, to the gem.**
- **Controls:** corners (1000–965 as side A) and boss_battle (1034–717 as side A) mirror v24z, and corners' total respawn delay is identical to v24z (15 rounds).
- **Edge case seen once:** on corners as side B, a champion stayed 11 rounds on a due group's tile (group 26), then left by itself, with no extra delay compared with v24z. No lasting stall from an occupied or unreachable ring was observed; not ruled out.

### Status
Main Claude's 7-opponent bench on engine 1.0.3: 458/560 (449 vs v24w's 448 on the 39 shared maps), neutral. **Submitted as live on 22 Oct (#40).** Contest recall: 13/14 on the bench, same as v24z. It follows after ~40 ranked games of spawnfix.

## 2. Rows opening (diagnosed; proposal rejected locally)
- **Ranked:** we take 2.3 captures by r150 vs their 4.4, and earn 415 gold vs 601. Not a fighting problem: 2.0 deaths by r600 vs 3.3.
- **Our route is the same every game:**
  - Side A: g0 @57, g2 @85, g0 @164, g4 @170.
  - Side B: g1, g3, g5.
  - One pack, one group at a time. The first capture comes at r55–57 vs their r31–50.
- **Many opponents also farm a harmless gold-only flank group** (g7/g8: 4 camps × 120 HP, 80 gold, 0 gems; 43 walking steps from either spawn) in parallel.

**Rows camp groups, gold and gems per capture** (medians, ranked):

| Group | Gold | Gems |
|---|---|---|
| g0/g1 (3 wolves + 3 small camps) | 180 | 12 |
| g2/g3 | 160 | 19 |
| g4/g5 | 120 | 26 |
| g7/g8 (flank) | 80 | 0 |

- **Candidate `kurians-t3-rowsfarm`:** let the existing gold-farmer role take the flank group on rows only.
  - Default limits: 22 steps and a gold rate of 3. Rows: 45 steps, with the rate waived.
  - The first try used 32 tiles and never activated, because `home_d` is a *walking* distance (43). A diagnostic print confirmed this.
- **Mechanism worked:** captures by r150 rose 2.5 → 4.9 and gold by r150 426 → 728.
- **Outcome was worse:** 3/10 vs spawnfix's 6/10, losing to spawnfix from both sides (827–1008, 993–1006). The farmer adds gold but no gems, the 3-champion pack clears wolf groups more slowly, and the farmer idles about 50 rounds a cycle waiting for its group to respawn.
- **Rejected.** As on stampede, early gold isn't the lever on rows; the gem race is.

## 3. Contest
### v24p's bench gain doesn't hold up in ranked play
All 12 ranked contest games were played at or after v24p went live (17:10 UTC): **3 wins of 12**. On the 7-opponent bench it's 14/14.

### Where it's lost (11 decoded games)
- **Level at r150:** captures 6.5 vs 6.9 (middle 4.1 vs 4.6), gold 658 vs 676. Pack farming closed the early middle gap.
- **Behind from r150:** captures by r600 22.2 vs 31.7 (middle **14.8 vs 23.0**), gold by r600 **2274 vs 3401**.

### #27 ("dying while running away") still holds over a full game
An earlier draft of this report said otherwise: it counted only to r600.

| Phase | Our deaths per game |
|---|---|
| r0–150 | 2.9 |
| r150–600 | 10.8 |
| **r600+** | **36.6** |

That's about 50 per game in total. Deaths per phase across the 11 games:

| Profile at death | r150–600 (119 deaths) | r600+ (403 deaths) |
|---|---|---|
| In the middle third | 82% | 88% |
| Outnumbered | 46% | 42% |
| Alone (no ally within 6) | 30% | 42% |
| **While recalling** | 15% | **28%** |
| Retreating (not recalling) | 14% | 10% |
| HP share one round before death (median) | 0.08 | 0.10 |
| Carrying gems | 0 | 7 |

- **132 deaths came while recalling** (about 12 per game). A recall takes 5 turns and one hit cancels it.
- **The live rule** (v24z line 1250) recalls a low-HP champion when no enemy is within *its attack range + 2* (usually 5 tiles). Shop-recall (line 1257) uses range + 3.
  - Enemies 6–8 tiles away reach it before the recall completes.
  - v25a (recall earlier, at 50% HP) showed no gain in scrims. The data points at *where* the recall starts, not the HP threshold.

### Proposal: `bots/kurians-t3-contestrecall`
spawnfix + **on contest only** (the existing `forced_pack` fingerprint): low-HP and shop recalls need **no visible enemy within 9 tiles**. Otherwise the existing on-foot retreat runs. Other maps are unaffected.

**Local A/B vs spawnfix** (`tools/t3contest.py`, current contest map, 6 opponents × both sides: cc_contest 1–4, fz_hunt, v24c):

| | spawnfix | contestrecall |
|---|---|---|
| Wins | 12/12 | 12/12 |
| Deaths / game | 18.7 | **17.6** |
| … while recalling | 8.6 | **7.1** (−17%) |
| … by r600 | 2.9 | 2.6 |
| Our gold earned (tiebreak) | 9481 | **9856** |
| Opponent gold | 5046 | **4745** |

- Head-to-head between the two: 1–1 (side B wins both).
- **Verdict:** the mechanism moves the right way (fewer recall deaths, less gold fed), but the bench can't judge the outcome. Both versions win every bench game, while ranked contest is 3/12, and these opponents rarely chase. This is a contest-only, low-risk candidate for a ranked or scrim test, not a proven win.
- `t3contest.py` decides the winner from tributed gems, then gold earned. (The first run read the snapshot's `outcome` code as 0/1 by side, which is wrong; results above are recomputed from the printed gems/gold.)

### Low-HP episodes (review follow-up, `tools/lowhp.py`)
An episode starts when an alive champion off its spawn (>4 tiles) drops below 30% HP (the bot's retreat threshold). It ends at death, or when the champion is back off spawn with ≥90% HP ("recovered"). Recall = `channelType` 1, identified from replays: median 5 rounds; ends at spawn 671 times, in death 85, cancelled 60.

**Ranked contest, 13 games, us vs them:**

| | Us r150–600 | Them r150–600 | Us r600+ | Them r600+ |
|---|---|---|---|---|
| Episodes | 152 | 147 | 496 | 364 |
| Ended in death | **74%** | 49% | **73%** | 59% |
| Recall attempts / episode | 0.51 | 0.61 | 0.59 | 0.56 |
| Recalls completed | **60%** | 77% | **48%** | 71% |
| **Died while recalling (per attempt)** | **25%** | 9% | **45%** | 23% |
| Died when no recall was tried | 100% | 91% | 98% | 96% |

- **We recall about as often as opponents, but our recalls fail far more.** Where and when the recall starts is the problem, not whether we recall.
- **Not recalling is not a safe fallback either:** a low-HP champion that never recalls dies 96–100% of the time, for both teams. So refusing a recall could just move the death (the review's concern).

**Local check of that concern** (contest, 6 games per bot: fz_hunt, v24c, cc_contest × both sides; r600+, where most episodes are):

| | spawnfix | contestrecall |
|---|---|---|
| Episodes | 161 | 148 |
| Ended in death | 64% | **60%** |
| Recovered | 36% | **40%** |
| Recall attempts | 139 | 118 |
| Completed | 55% | **61%** |
| Died while recalling (per attempt) | 35% | **31%** |
| Deaths not while recalling | 54 | 53 |

- Locally, refused recalls did **not** turn into walking deaths (54 → 53), while recall deaths fell (49 → 36) and more champions recovered.
- Directionally positive, but small (6 games), and the local opponents share our code: their own recalls die 43–52% of attempts. A real ranked or scrim test is still the judge. The r150–600 local samples (18–20 episodes) are too small to read.

## 4. Open items
- **All ranked games are decoded** (cambc 3.0.5 assets + `v1_0_3` in `extract3.mjs`).
- **Local opponents don't reproduce ranked contest.** On the bench v24z/v24p win contest, and our local deaths are far below ranked. So contest proposals need main Claude's ranked or scrim test to be judged.
