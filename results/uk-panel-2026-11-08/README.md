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
