# UK panel: the 9 UK teams ranked above us (8 Nov 2026)

`tools/panel/panel_uk.json`: BattleCats, Claudus Maximus, QS2isLaw, Rogue Lock Pickers, bentheboss, smurphy (UK 6th), 剑桥夜爬者, DOOMSDAY, 0xDEADBEEF. 5 maps each (45 games), stratified across map families, sides alternating. Every candidate runs pinned to the baseline's opponent versions (`--pin uk_i`).

Ladder at 11:00 UTC: Tatakai **68th, 2,078** (81st, 2,027 on 8 Nov morning). UK 6th (smurphy) is 2,200, 122 points ahead.

## Baseline: v53i (236) = 9/45, deaths 7.36 per game, mean margin -361
| team | wins | deaths | maps (our gems - theirs) |
|---|---|---|---|
| BattleCats | 0/5 | 8.2 | 00rushbait_v2 936-1009, 01corridors 626-1030, 02treasure_box 558-1046, 03showdown 344-1040, 04wilds 588-1023 |
| Claudus Maximus | 0/5 | 3.0 | adgato_gemcombat5 63-1106, 00gem_fields 202-1007, 01big_world 728-1197, 02uncharted_lands 744-1064, 03twisty 87-1106 |
| QS2isLaw | 1/5 | 3.6 | 04barbell 891-1022, adgato_gemcombat4 744-1026, **00road_of_riches 1058-880**, 01yellow_brick_road 609-1000, 02cuts 907-1011 |
| Rogue Lock Pickers | 0/5 | 11.0 | 03honeycomb 526-1012, 04plaza 230-1034, adgato_gemcombat1 252-1061, 00ambush 942-1028, 01hooks 68-1010 |
| bentheboss | 0/5 | 7.8 | 02the_pack 521-1013, 03one_gem 0-176, 04spiral_moat 211-1042, adgato_gemcombat3 510-1080, 00expanse 718-1043 |
| smurphy | 2/5 | 5.4 | **01islands 1053-657**, 02geodes 768-1028, 03homonoliths 0-1200, **04standing_stones 1021-552**, adgato_gemcombat2 126-1027 |
| 剑桥夜爬者 | 2/5 | 16.0 | 00gemfight 358-1001, **01starvation 873-696** (round limit), 02gift_wrapping 358-1038, **03riverbed 1008-937**, 04horseshoes 188-1004 |
| DOOMSDAY | 2/5 | 8.6 | 00galaxy 446-1032, **01gold_rush 1128-301**, 02guardians 0-1088, 03the_front 850-1062, **04orchard 1043-814** |
| 0xDEADBEEF | 2/5 | 2.6 | **00anvil 1054-307**, 01boss_battle 0-1005, 02harvest 843-1020, 03contours 741-1063, **04duel_ring 1020-275** |

## Flaw found: boss maps (measured)
We banked 0-87 gems on 01boss_battle, 02guardians, 03homonoliths and 03twisty. Rounds with one of our champions within 4 of a monolith or golem, us vs them:

| map | us / them |
|---|---|
| 03twisty | 3 / 35 |
| 02guardians | 4 / 233 |
| 03homonoliths | 358 / 954 |
| 01boss_battle | 228 / 309 |

Our siege planner counts at most one hypothetical helper (`max_hypothetical_joiners 1`). A 20,000 HP, 200-strength monolith is never feasible, so its group scores 0 and nobody goes. The "jackpot" logic (gem weight x3, up to 4 helpers) exists but is off (`jackpot_share 0`; 0.4 on all maps was rejected in an old-engine head-to-head).

**v53r** turns jackpots on only for monolith/golem groups, and only on maps where such groups produce at least 50% of the gem output, measured by the bot at the start of any map:
- On for 21 of 128 maps, including 03homonoliths 1.00, 00contest 1.00 and 03twisty 0.60.
- Misses 01boss_battle (< 0.2) and 02guardians (0.34): output share undervalues bosses because they respawn slowly.

Local tests (all maps vs v53i and v226, unseen boards, with a boss-map split) are running.

## v53r (boss jackpots from round 1): rejected
| test | boss-economy maps (21) | other maps | all |
|---|---|---|---|
| vs v53i | **14/42** | 122/214 | 136-120 |
| vs v226 | 19/42 | 115/214 | 134-122 |
| unseen boards vs v53i | | | 71-69 |

The "other maps" differ only through fuel timing. Grinding a monolith early loses the farm race.

How the UK teams take bosses (decoded):
- Late (r692-929 for the first boss), with 2-4 champions, usually led by a ranged carry (Vesper, Marcella).
- 03homonoliths: Vesper + Cassi from r692, then Vesper, Marcella and Issac.
- 02guardians: Vendetta, then Vendetta + Varg, from r829.

## The real flaw on boss maps and in close races: banking (measured from summaries)
- **01boss_battle: we collected 4,605 gems and banked 0.** At the end we still held 3,577 (one champion 2,406). This is an altar-reach failure on that map (the bank routine exits when it finds no reachable altar). Not fixed yet.
- **Close races lost with gems in hand:**

| map | collected | banked | held at end | opponent's winning total |
|---|---|---|---|---|
| 04barbell | 1,205 | 891 | 314 | 1,022 |
| 02cuts | 1,145 | 907 | 194 | 1,011 |
| adgato_gemcombat4 | 1,129 | 744 | 217 | 1,026 |

- Across all 45 UK games we finished holding 6,106 unbanked gems (of 36,597 collected; 25,941 banked).
- Cause: the bank trigger is per champion (its own bag of 25-40, or its own gems winning). Nobody accounts for the team total near the end.

**v53s**: once either side has banked 800, every champion banks any bag of 5+. Local tests running.

## v53s (race-end banking): passes locally
| test | wins | margin | banked (v53s / opponent) |
|---|---|---|---|
| vs v53i | 133-123 | +16 | 825 / 809 |
| vs v226 | **158-98** | +98 | 844 / 746 (v53i: 151-105) |
| unseen boards vs v53i | 70-70 | +7 | |

## v53t (v53s + gate bosses)
When no altar is reachable on foot, a monolith/golem group within 3 tiles of an altar becomes a jackpot siege (up to 4 hypothetical helpers). The probe over all 128 maps triggers on exactly **01boss_battle and 02guardians**, both zero-gem UK losses.
- 01boss_battle, v53t as side A vs v53i: **1356-0, won at round 861** (v53i side B banked nothing).
- Reverse sides: v53i 1040 - v53t 729 (side A's altar is reachable; v53t as B still banks 729).

Full local tests are running.

### v53t full local results
- vs v53i 126-130 (margin +21); vs v226 148-108; unseen boards 73-67.
- Gate maps, mixed:
  - 01boss_battle vs v53i: 1-1 (1356-0 win, 729-1040 loss).
  - 02guardians vs v53i: 0-2.
  - Vs v226: boss_battle 0-2, guardians 1-1.
- The siege sometimes fixes the zero-bank collapse but is not reliable, and costs on 02guardians. v53s is the clean candidate; v53t is a targeted bet. The UK panel includes both gate maps (boss_battle vs 0xDEADBEEF, guardians vs DOOMSDAY, v53i 0 gems on both) and decides.

## UK panel results (pinned, same 45 games)
| bot | wins | deaths | margin |
|---|---|---|---|
| v53i (236) | 9/45 | 7.36 | -361 |
| v53s (237) | 9/45 | 7.51 | -348 |
| **v53t (238)** | **11/45** | **7.18** | **-328** |

- v53t is live on the agreed rule. The +2 is within noise.
- The gate-boss maps still score 0 against real teams (01boss_battle 0-1122, 02guardians 0-1098): they take or contest the gate boss first. The local fix does not transfer.
- v53t's gains were against BattleCats (1/5) and QS2isLaw (3/5).

## Boss maps against the UK teams (summaries of v53i's and v53t's games)
- Single central altar on both maps: (20,20) on 02guardians, (25,20) on 01boss_battle.
- The opponent's first tributes come only after the gate opens: r845-908 on 02guardians, r1258-1361 on 01boss_battle.
- We never tribute (collected 226-4,605).
- Gate detection works: an altar with only camp tiles in range gets a gate group. But we walk the gate only once we have seen the gate boss down, and no carrier goes to look.
- **v53v** (gate inference: an enemy tribute, or a stale belief plus a 60+ bag, sends carriers through the gate): rejected on the target map. 01boss_battle vs v53t: 113-1121 (14 deaths) as A, 0-1025 as B. Carriers walk into the enemy holding the gate. The gate needs map control, not inference.

## New public repository: toyeshhm/cambridge-battlecode-2026 (team EvilMangohh, peak rank 22, engine 2)
Their lessons that match ours:
- every "play safer" rule cost kills;
- changes inside fights almost never helped;
- local A/B against own bots misleads (38/64 locally became 0/25 on the platform).

Transferable rules:
- **same-turn tribute** (their biggest gain, 18 to 29 of 100 with a late bag cap);
- fast capture (melee steps onto the reward on the kill; nearest ally captures; 2.7 to 1.4 rounds);
- recall from the capture tile;
- monolith takes staged outside reach under a team-damage model with no enemy near;
- map-kind draft tables (contest/boss maps: five range-4 champions).

Our bot wasted a turn at every tribute. **v53u** (v53t + same-turn tribute) is verified to submit in the same turn (0 engine errors); local tests are running.

### v53u local results: neutral
- vs v53t: 133-123 (margin -5).
- vs v226: 139-117 (v53t 148-108).
- unseen boards vs v53t: 69-71.
- Banking and deaths unchanged within noise. The saved turn per tribute is too small to show in self-play. It is a safe addition, with no local evidence of gain.

## Teammate version r5 (239, live since 23:54 UTC 8 Nov): v53i with the opening pack released at r60
- Local: 152-104 vs v226 (kills 4.23 / 2.96, deaths 3.29 / 4.59); unseen boards 75-65 vs v53i; rohi-ds: 133-123 vs v53i.
- Ranked while live: 49/95 (rating about 2,093).
- UK panel, all versions on the same 45 pinned games:

| version | UK panel | deaths | margin |
|---|---|---|---|
| v53i (236) | 9/45 | 7.36 | -361 |
| v53s (237) | 9/45 | 7.51 | -348 |
| v53t (238) | 11/45 | 7.18 | -328 |
| r5 (239) | 10/45 | 7.47 | -394 |

All within noise. Next candidate: **v53w** = v53t plus r5's pack release at r60. The two changes are independent.

## v53w (v53t + r5's r60 pack release): local
- vs r5: 133-123 (margin +2).
- vs v226: **161-95** (kills 4.20 / 2.95, deaths 3.32 / 4.49), our best result against v226.
- unseen boards vs r5: 70-70.

## Refining r5's code (no strategy change): fuel
- r5 averages 0.5 fuel-exhausted turns a game, but **02the-pack about 35 a game** (04gem-caverns 10, 03the-front 5).
- Profile on 02the-pack (heavy turns):

| phase | median | max |
|---|---|---|
| observe | 16.6K | |
| observe_groups | 21.4K | 49K |
| seal bookkeeping | 5K | |
| remember_threats (spikes are charged suspended turns) | | 31.7K |

- Cause found: `camp_group::state()` in the SDK copies the whole vision bitboard on every call to re-check visibility. Our code only calls it for groups already known to be in view.
- **r5a**: query the engine (`sdk_camp_group_state` / `sdk_camp_group_cooldown`) directly, with the SDK call as fallback.
  - On 02the-pack: suspended turns 28 -> 21, observe_groups median 21.4K -> 9-17K.
  - Full mirror vs r5 and unseen boards running.
- **r5a full test**: 129-127 vs r5 (kills 3.45 / 3.46, deaths 3.92 / 3.91), unseen 72-68. **Fuel-exhausted turns per game 0.54 vs 0.77 (-30%)**. Safe refinement.

## Capture tempo (UK panel, r5's 45 games, from summaries)
| clear -> capture | us | UK teams |
|---|---|---|
| median rounds | 7 | 6 |
| under 6 rounds | 0% | 32% |

Captures are about 53 per game. Our learned shop never adds the Capture emblem: Capture comes after Bruiser in the family list, and the learned plan only fills families up to Bruiser.
**r5b** = r5a + Capture emblem (`p4_shop_cap`) and 3-round capture timing (`p4_capture_time`). Testing, including whether the emblem is bought and captures get faster.
- **r5b** (Capture emblem, now actually bought): clear->capture median 6, 35% under 6 rounds (r5a: 7, 0%), matching the UK teams. But 124-132 vs r5a (kills 3.25 / 3.48, deaths 3.96 / 3.72), unseen 69-71, 146-110 vs v226 (r5 152-104). The emblem's gold comes out of combat stats. Not adopted: capture tempo is not what holds us back.
- First r5b run was void: the disk filled (180/256 games); the learned sort left the Capture step behind the unlimited step, so it was never bought. Both fixed.
- **v53x** = v53w + r5a fuel fix: the combined candidate (r5 pack release, race-end banking, gate bosses, fuel fix). Local tests running.
- **v53x local**: 134-122 vs r5 (margin -10, kills 3.30 / 3.51, deaths 3.91 / 3.74), 150-106 vs v226, unseen 72-68 vs r5. Slightly ahead of r5, within noise. Ready for the UK panel, pending approval.
