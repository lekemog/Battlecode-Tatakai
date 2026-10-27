# MC (wanga158-mcmaster/secretcode) exhaustive inventory, learned-weight tables, and port specs v39a-v39t

Companion of `results/claude/mc-vs-ours-2026-10-27.md` (comparison and verdicts). Read-only study; nothing of MC's was built, run, or copied. All MC paths are relative to `/home/user/wanga158-mcmaster/secretcode/bots/main/main/src/` (v55 defaults, SDK 3.0.5, engine 1.0.3). `DECISIONS.md` = `bots/main/DECISIONS.md` (D-numbers). Our paths: `bots/v35a/src/bot.cpp` (`bot.cpp`), `bot.h`, `draft.cpp`.
Transfer codes: **T** = transfers to our chassis (squad core + solo farmers); **A** = transfers with adaptation (their code assumes solo farmers, `squad_size 1`, per-champion shared slots, or their fuel/field infrastructure); **C** = needs their chassis/learned layer; **X** = off in their v55 config or rejected by them (do not port as a feature).
Evidence tags: **[meas]** their own measured gain (their engine, their opponents, local self-play unless "online"), **[code]**, **[doc]**.

## Part A. Inventory of every mechanism in `bots/main/main/src`

### A1. Target scoring and cycle cost

| # | Mechanism | MC file:line | What it does | Measured (DECISIONS) | Transfer |
|---|---|---|---|---|---|
| 1 | Unified rate | brain.cpp:2213-2345 (`score_group`), model.h:638 (`group_rate`) | rate = reward / max(1, travel + wait + hp_rounds + siege_rounds + capture) / members; reward = gem_weight x gems + 1.0 x gold; travel = walking distance from `route_pos` on a cached per-group field. | Core since D58 (gem value 1.5 plateau 1-2: 143-144/216 vs 119 at 6.0); D100 | A (replaces `solo_target`/`cluster_target` scoring; `squad_target` can share the formula) |
| 2 | Gem weight | brain.cpp:2152-2201; config.h:171-180 | 1.5 flat (`gem_value_late` = same); gem-rich maps (harmless groups >= 1.4 gems/round map-wide) use 4.0 | D58, D83 (gem-rich: lost_world 735/934 -> 377-445 rounds vs starter; locally neutral; panel 18 -> 20/50) | T |
| 3 | Gold weight | config.h:190 (`gold_value 1.0`) | gold counted 1:1; no early/late schedule | D58 | T (ours is 0.04-0.15) |
| 4 | Multi-trip siege plan | model.h:118-165 (`plan_siege`), brain.cpp:2286-2316 | trips = ceil(damage x 1.6 / pool); rounds = fight rounds + (trips-1) x overhead; feasible if trips <= 4; best over extra hypothetical joiners 0..1 | D69 margin 1.6: 181 vs 165 of 280 (1.1: 150) | T |
| 5 | Damage forecast | model.h:36-116 (`forecast_camp_fight`, `FightConstants`, `forecast_from_constants`); world.cpp:99-125 (per-group `weighted_hp`) | Smith order (descending strength/HP); damage = max(0, W x scale / dps - 0.5 S); rounds = ceil(hp x scale / dps); a monster killed on our k-th attacking round attacked k-1 times | core | T |
| 6 | Heal cost in score | brain.cpp:2300-2308; config.h:93 (`hp_cost_weight 1.0`) | hp_rounds = int(frac x overhead), frac = min(1, damage x camp_mult / (members x max_hp)), overhead = recall + 1 + walk(spawn->group) | D100: 484 -> 501 (+91/-74) of 640, seeded 968 -> 1002 (+182/-148), small maps +112/-68; costs +22 rounds speedrun | T |
| 7 | Hypothetical joiners | brain.cpp:2281-2282; config.h:262 (`max_hypothetical_joiners 1`) | the best rate over 0..1 extra average allies; committed allies counted fully | D79 | A |
| 8 | Committed allies | brain.cpp:2232, 2253-2262; knowledge.cpp:~300 (`recount`) | allies engaging/capturing the group add dps and 0.8 x hp x growth to the pool and divide the reward (`members`); harmless group with a committed ally x0.1 | core | A (needs slot status bytes) |
| 9 | Re-score cadence + hysteresis | brain.cpp:3267-3313; config.h:239, 260 | every 8 rounds; switch only if score > 1.35 x current | D69 (1.2/1.5: 169/158 vs 181), D111 (interval: no difference) | T |
| 10 | Bound pruning | brain.cpp:2496-2559; config.h:243 | cheap upper bound reward/(travel + capture); full-score groups in descending bound until no bound beats best; <= 16 evals; each eval needs `fuel_score_group` 26K | D68: 8 -> 12/16 evals: 161 -> 169/167 of 280 | T |
| 11 | Rejected-score reasons | brain.cpp:2216-2234 | unreachable island, travel >= 2^14, respawn wait > `max_respawn_wait` (0), another ally capturing the reward -> score 0 | D60 (never wait: 145 vs ~126/216) | T |
| 12 | Respawn travel | brain.cpp:3340-3378; model.h:17 (`approach_respawn`); config.h:106-110 | walk toward a respawning group whose timer ends by arrival; wait only within 2 tiles; `blocked_respawn` (2203): a timer-zero group seen this turn that has not turned alive is rejected until it does | D124: **686 -> 757 wins (+141/-70, p 1e-6)** of 960 pool keys; legacy 283 -> 308 (+67/-42); idle-respawn team-turns 22.4 -> 0; D120 | T |
| 13 | Banned-group factor | brain.cpp:2333 | banned groups x0.05 (bans: capture give-up, watchdogs, handoff) | - | T |
| 14 | Enemy-near-group factor | brain.cpp:2332, 3753-3770; config.h:202 (`track_group_enemies false`) | would halve a group's rate for 20 rounds after an enemy was seen near it; OFF (radius 4/6/9: 142/132/119 vs 166 of 280) | X | X |
| 15 | Territory penalty, jackpot, gem_value_model, race_gem_boost, passive_rewards, prism battery | config.h:142-200; brain.cpp:2272-2276, 2336-2342 | all default off | D91 (-18 speedrun, -15/640), D97, D98 (0.4 jackpots: 85 -> 64-72/112), D108, D112 | X |
| 16 | Route chain (two-step lookahead) | brain.cpp:2565-2652; config.h:249 | blend plain and chained rate; off | D120, D362: w 1 -3 wins (p .93), w .5 +20 (p .34) | X |
| 17 | Planning turn | brain.cpp:2654-2678, 3234-3264; config.h:60-61 | a turn too poor for a full choice picks the next group round-robin from a score pass (<= 16 evals, 20K) so a no-target champion does not idle forever | D163/D164/D171 (reliability trio; strength not claimed) | A |
| 18 | Learned group factor | brain.cpp:2433-2494; learn.cpp (weights 0-15, 88-93) | multiplies rate and bound by factor(logit) = (1 + clamp(l,-3,3)/8)^8 | D340, D344: exploiter training +309/-219 of 6,974 (all sets, own family) | C |

### A2. Capture, handoff, recall

| # | Mechanism | MC file:line | What it does | Measured | Transfer |
|---|---|---|---|---|---|
| 19 | `go_capture` | brain.cpp:2887-2929 | on a member tile -> status capturing; else step along group field toward a free member tile (occupancy from `champion_tiles`); gives the target up after `capture_stall_turns 3` turns without a step | D78 (two champions blocked each other 1800 rounds on gold_rush) | T |
| 20 | Capture hold | brain.cpp:3042-3108 | stay on the tile until the reward lands; publish capturing; `capture_patience 100` turns -> ban 40 | D78/D74 (`capture_hold` knob = hold on enemy contact: +9/+1/-3, off) | T |
| 21 | Capture handoff | brain.cpp:2935-2961 (`handoff_capture`, `leave_capture`), 3051-3052, 3326-3331; config.h:257 | with no enemy visible, the ally with the lowest roster index on a member tile keeps the capture (or anyone already on one if we are not), the rest `leave_capture`: ban group for capture_time + 2, clear target, `leave_camp_tiles`, choose next turn | **D362: +209/-143 (p .001) on 1,920 keys; unseen 1,362 keys 916 -> 986 (+197/-127); pace -17 +- 4 rounds** | T |
| 22 | Capture recall | brain.cpp:3075-3105; config.h:461-472 | while holding, nothing hostile, no unseen, not hit: at hold >= capture_time - recall_turns + 1 recall if value benefit >= 0.3 x walk(spawn->group) - slack; publish capturing during the recall channel (435) | **D343: +354/-203 over 3,247 games, margin +55, 56 rounds faster; removal -47/480 (p .001)**; D326 first version (>=90 gold or <60% hp) 167 vs 165, speedrun +38 | T |
| 23 | Carrier capture (designated capturer) | brain.cpp:3641-3690; config.h:453 | Vesper for gold groups, Marcella/Prism for gem groups | D326: 158 vs 165, margin -70; OFF | X |
| 24 | Capture before recall | brain.cpp:1887-1894; config.h:103 | at low hp beside a cleared reward capture first; default 0 | D110 testing | X |
| 25 | `leave_camp_tiles` | brain.cpp:3893-3933 | idle champions never stand on a camp spawn tile (an occupied spawn tile delays the group's respawn); step away from centre, else bounded BFS (radius 10) to the nearest tile that is no camp tile | **D96: stampede 2000 -> 1564, great_wall 1048 -> 1000, boss_battle 850 -> 836** (a champion held a respawn 476-1141 rounds) | T |
| 26 | Heal recall | brain.cpp:1837-1975; config.h:82, 86 | recall when hp < 50% (or `in_danger`: hp < incoming x (escape + 1)), unless a nearly dead camp fight is cheaper to finish (`damage x mult < 0.6 hp and hp > 15%`); not threatened -> `recall()`; threatened -> `retreat()` | D61: 0.30 94, 0.40 ~127, 0.50 148, 0.60 138, 0.70 131 of 216 | T |
| 27 | Travel recall | brain.cpp:3435-3471; config.h:152 | recall instead of walking when walk > recall_turns + 1 + walk(spawn->target) + 4, nothing in view/unseen/camp threat, not on spawn | D64: dev 126 -> 132, holdout 40 -> 44 of 64; 4 recalls/game (26-31 on big/corridor maps) | T |
| 28 | Shop recall | brain.cpp:3444-3458; shop.cpp:547-590; config.h:157, 504 | purse rule 300 gold / detour 20 (D65) replaced by value rule: `shop_recall_benefit >= extra + 2` | D65: 300/20 179 vs 163; D115: 666 -> 696 (+103/-73), margin +49, speedrun 1006 -> 973, gold spent by r200 62% -> 75%, first shop r195 -> r163 | A |
| 29 | Tribute recall | brain.cpp:2096-2113; config.h:167 | recall when walk to altar > recall + walk(spawn->altar) + 4; gems are kept | D66: 168 -> 174 of 280, legacy 75 -> 81; fires 0.5x/game | T |
| 30 | Recall tail / cancel reach / standoff recall | brain.cpp:579-597, 413-430, 1816-1829; config.h:581, 585, 433 | OFF | D346: tail -46 (p .015), cancel k4 -100; D77 standoff recall 126/141 vs 153 | X |
| 31 | Home emblem scaling | ctx.cpp:245-262 (`recall_turns`, `damage_taken_multiplier`) | recall turns = ceil(5 x (1 - home magnitude)); jungle/durability multipliers cached, refreshed after a purchase | D64: Home as an item lost (after Treasure 101, after Monster 123 vs 121) | T |
| 32 | Teleport crystal shortcut | brain.cpp:2680-2724 | OFF | D74, D113: +17/-1/-16 | X |

### A3. Group news, slots, shared memory

| # | Mechanism | MC file:line | What it does | Measured | Transfer |
|---|---|---|---|---|---|
| 33 | Slot byte | knowledge.cpp:288-297 (`write_slot`), 140-185 (`read_slots`) | byte i (champion i, sorted by handle) = ((group+1) & 63) or (status << 6); status 0 engaging, 1 capturing, 2 cleared, 3 idle; a `cleared` post marks the group respawning for everyone (`mark_respawning` with the group's respawn constant) | core | A (needs repack, Part C) |
| 34 | Group news | brain.cpp:3692-3720; knowledge.cpp:257-286; config.h:457 | tail 3 bytes (size-3): group+1, respawn_round lo, hi. Post the respawning group we see, preferring one that an ally is walking to (`urgent`); a record is replaced only by equal-or-more urgent news; readers fold it unless they see the group this turn | **D345: +131 on zero weights, +34 with co-trained weights; C2 in tracks/medium.md; claimed cause: 14% of champion-rounds spent walking to dead groups** | A (one-byte variant, spec v39f) |
| 35 | Enemy sightings in the tail bytes | brain.cpp:3508-3548; knowledge.cpp:208-230; config.h:308-311 | OFF | D114: neutral; wider join radius worse | X |
| 36 | SOS beacon | brain.cpp:1811, 3018-3029; knowledge.cpp:187-206; config.h:423 | OFF (sos_radius 0) | D73: **129 / 105 vs 154 of 280 (lost badly)** | X |
| 37 | Pack sightings / phantom mode 2 | brain.cpp:3722-3750, 1420-1467; config.h:317-324 | OFF | D323 (phantom_mode 1: 165 -> 103), D324/D325 (online arm v48: 9/100) | X |
| 38 | Draft memory | - | unused | - | - |

### A4. Bank, tribute, transport

| # | Mechanism | MC file:line | What it does | Measured | Transfer |
|---|---|---|---|---|---|
| 39 | Tribute trigger | brain.cpp:2011-2049; config.h:132-134 | bank at bag >= 25 gems (x learned factor), or within 8 detour tiles of an altar, or rounds_left <= walk + channel + 15, or banking wins | D102: 40 -> 651, 60 -> 654, 90 -> 641 of 880 vs base 666 (hoarder loses to hunters); kept 25 | T |
| 40 | Tribute guard | brain.cpp:387-409 | cancel a tribute channel when enemy dps within (3 for melee, 5 for ranged) x rounds left >= 0.8 hp | - | T (we have a similar guard, 1128-1134) |
| 41 | Altar locks | brain.cpp:2726-2773, 458, 2062-2084; config.h:430 | lock mode 2: lock our own tribute altar before channelling, attack an enemy lock when in reach, lock the altar a visible enemy is tributing at; lock range 2 narrowed on engine error | **D76: +25 of 626, 3.6 locks/game**; D57 earlier variant rejected | T (we have v25s) |
| 42 | Gated altar | world.cpp:125-139, 147-161; brain.cpp:1989-2009 | altar ringed by one camp group (boss-battle): walk onto the group's tile when that group is down; field `gate_field` built early | - | T |
| 43 | Prism battery / bank danger bag / hunt carriers | config.h:142-146, 137, 401-406 | OFF | D108/D129/D136 (worse), D104 (neutral) | X |

### A5. Fight verdict, hazard, retreat

| # | Mechanism | MC file:line | What it does | Measured | Transfer |
|---|---|---|---|---|---|
| 44 | Skirmish simulation | model.h:187-366 (`Fighter`, `simulate_skirmish`); brain.cpp:1249-1535 | fighters: us + allies within 6, enemies within 8, remembered hidden enemies (<= 5 rounds, within 6 + age tiles), horizon 15. Per fighter: hp (+3 x max on a spawn tile; + active/ready shield), basic dps, two casts with live readiness and shared cooldown, arrival round = 1 + max(0, gap - reach)/2, Cassi/Issac linked death, value 1 + gems/40 per death. Focus = least-health arrived fighter; damage per side per round simultaneous, overkill carries | D59 (live cooldowns + dash reach 133 vs ~118/216), D75 (+26/626, kills +19%), D84, D85 | A |
| 45 | Verdict | brain.cpp:1593-1597 | favourable if their losses (+ learned edge) >= ours + 0.5 (0 when allies engaged); doomed = hp <= 2 x enemy_threat_at(pos) and rounds > 2 | D87 etc. | A |
| 46 | `no_loss_stance` | brain.cpp:1752-1761; config.h:394 | if ours losses < 0.5 and not doomed: answer in place if hit-able, else keep farming | **D87: 179 -> 201 /240 (+33/-11, p .001, margin +82)**; at v27 w/o D84 model it lost 152 vs 160 | A |
| 47 | `calm_farm 1` | brain.cpp:1778-1790; config.h:440 | when unfavourable: retreat only if an enemy can strike next turn; mode 2 (ban contested targets) off | D86: mode 1 177 vs 179 (neutral), mode 2 147 (p<.001); re-enabled with the reliability trio D168/D171: 268/266/274 per 374, +60/-54 n.s. | A |
| 48 | Stand/help with engaged allies | brain.cpp:1544-1552, 1713-1727; config.h:379-381 | ally within 3 in contact -> accept even trades; close in when an ally within 6 is in contact | D17, D61 (pooled 85/162; hunter 38-16) | T |
| 49 | Spawn handling | brain.cpp:1602-1639; config.h:376-377 | on own spawn: fight only what is reachable; a second sim without the spawn bonus decides whether leaving is ok; hold <= 40 rounds per visit | D78 fuel fix (second sim only while a hold can happen) | A |
| 50 | Hazard disengage | brain.cpp:1640-1697; hazard_model.h; config.h:17-19 | logistic over 20 contact features; z >= logit(0.3) with an enemy within 8 -> `retreat()` for 3 rounds (static `hazard_until`) | **D347: +198/-134 (977 -> 1041), deaths 9.8 -> 7.9; unseen +80/-49; D360 +66/-37; online matched +0.2 +- 1.7 pp over 700 games (D362)** | A (weights not portable; spec v39k) |
| 51 | `retreat()` | brain.cpp:635-819; config.h:288-302 | threat sources (awake camps within range+3, unseen camps, enemies repel by reach); bounded safety field (radius 10 BFS from tiles outside every reach); tile score -to_safety x 1e5 - threat x 10 - home - ally pull(2/tile); melee attacks while backing; escape dash scored with the same function | D59, D101/D103/D117 (committed homeward modes rejected: 562-656 of 880 vs 666) | A |
| 52 | Tactics S rewrite | brain.cpp:918-1226 | OFF (tactics_s 0) | **D327: 165 -> 83 wins** | X |
| 53 | Doomed: take the kill | brain.cpp:1697-1706; config.h:398 | OFF | combo2 notes: neutral | X |
| 54 | Hit-unseen / unseen camp memory | brain.cpp:3753-3811; ctx.h:109-110 | awake camps out of view are remembered 8 rounds (<= range+3 away) as `unseen` threats; hp loss without a visible cause sets `hit_unseen` (blocks recalls, raises learned recall) | D90s, D178 | T |
| 55 | Enemy memory | brain.cpp:3753, 1356-1368; config.h:305-311 | last-seen record per enemy roster index (<= 8); enters the sim for 5 rounds | D70: enemy_memory 0/10: 130/125; D114: wider radius worse | T |
| 56 | Retaliation reserve / retreat counters | retaliation-reserve.h; combat.cpp:482-538, 1104-1115; config.h:22-28 | pure scalar predicate: skip an optional retreat basic when the target (non-lethal) would retaliate (Ren: focus x ratio) and leave us <= one enemy basic | D350, D356: no strength claim; OFF | X |
| 57 | PvP camp basic | combat.cpp:1015-1102; config.h:28 | spend an unused melee basic on a freshly awake camp after favourable PvP; OFF | D358, D360: +46/-42 null | X |
| 58 | Enemy reach | combat.cpp:748-832 | reach = (2 for melee, 4 for ranged) + ready dash range + for each ready harmful spell: ceil(range + radius + (non-exclusive spell ? move speed : 0)); caches per champion type; `enemy_threat_at` sums dps of enemies within reach | D59, D175-D177 (spell underreach; +mirror tradeoff) | T |
| 59 | Strike dash / travel dash / support | combat.cpp:1163-1279 | travel dash when it saves >= 2 tiles and nothing in view (damaging dashes kept for fights unless far); camp strike dash needs 2 targets or a stun on a dealer; enemy strike dash value min(hp,dmg) + stun 120 + kill 400 + focus 200; support = shield when threatened, heal ally missing > half the heal | - | T |
| 60 | finish_kill / kill_chase / ally_help (combo2 only) | `bots/main/combo2/src/combat.cpp:981`, brain.cpp:3059, 3825; combo2 config.h:247-256, 418-434 | not in v55: kill a visible enemy off its spawn whose hp+shield <= this turn's burst (basic + ready damage/cc/aoe + reset), melee may step 1 tile; chase channeling or 2-hit-kill focus targets <= 6 tiles; walk to an ally within 12 that has an enemy within 3 when hp >= 50% | tracks/medium.md: fk2+kc6 **+201/-123** pool+train, **+178/-107** unseen (margin +3.3); ally_help 12 **+198/-152**, deaths 6.4 -> 5.5; EPF+capture-recall-walk+gem_value_model **+534/-248** on 2,270 unseen keys (online untested) | T |

### A6. Wards

| # | Mechanism | MC file:line | What it does | Measured | Transfer |
|---|---|---|---|---|---|
| 61 | Ward mode 4 | brain.cpp:2802-2885, 578; config.h:542 | every ready ward: candidate tiles within placement radius that are legal, free of champions/camps/wards; bush tiles first (others +100); keep the 3 nearest to aim; try each `place_ward`; skipped while any channel (recall/tribute/teleport) is running | **D71 (mode 2): +13 of 174 vs hunters, 173 vs 160; D72 (bush first): 172 vs 162 of 280, legacy 89 vs 74, 144 vs 129 of 210**; mode 1 147 vs 160; mode 3 160; mode 5 137 vs 154; mode 6 +9/+2/-5 | T |
| 62 | Ward errors | brain.cpp:2877-2884; D90 | first version ~7 failures/game (placing in the turn a channel starts) -> check the live state; dead-champion guard | D71, D90 | T |

### A7. Navigation, fields, fuel holds, mid-turn death

| # | Mechanism | MC file:line | What it does | Measured | Transfer |
|---|---|---|---|---|---|
| 63 | Static group fields | world.cpp:218-232 (`group_field`), 184-216 (`compute`); world.h | one distance field per camp group, rooted at its member tiles, walls = blocked | camp tiles of other groups; computed lazily, cached forever (map is static), reused by every query `World::distance(field, from, center)` | core; D67 | A |
| 64 | Field fuel model | world.cpp:168-216; model.h:140-150; config.h:49 | cost estimate = step_cost x depth_estimate(corner distance x 1.4 + 5) + 3000; step_cost measured as (cost - 3000 overhead) x 1.15 / steps, keeps the largest | **D67** (bug: 2-step pocket search measured 1720/step; afterwards every field refused; 21/32 -> 30/32 wins on blocked maps) | A |
| 65 | `route_pos` | ctx.cpp:130-147 | when standing on a camp tile, measure routes from the nearest non-camp walkable neighbour (camp tiles are walls in the fields) | - | T |
| 66 | Partial route fields | world.cpp:258-282 | bounded `compute_to_with_expansion_count` (layers = 2 x cheb + 8) from the target to our tile when the full field is unaffordable | - | A |
| 67 | `walk_reachable` | world.cpp:144-161 | a group is reachable if a cardinal neighbour of a member tile is reachable from the ally spawn field | D8x | T |
| 68 | Stepping | nav.cpp:128-195 | `step_along` (options with lower field value, sorted by d x 16 + penalty, `try_moves`), `step_best(score, stay_score)`, `step_greedy`; `try_moves` skips tiles that have a champion/camp and remembers a tile whose move failed (hidden occupant) for the turn (`remember_revealed`) | D78-D96 | T |
| 69 | Obstacles | nav.cpp:11-125 | per-turn cache of walls + units + teleports; invalidated after any move; `dash_landings` = reachable tiles over a mask that excludes walls, altars, enemy spawn, units (holes allowed) | - | T |
| 70 | Fuel phases | brain.cpp:485-509; config.h:34-76; main.cpp:17 | `fuel_ok(need)` = fuel > need + reserve 14K; phase thresholds: threats 45K, basic 12K, farm 25K, choose 45K, score group 26K, fight move 24K, strike dash 26K, escape dash 36K, safety field 16K, ward scan 30K; `field_tail_margin` 20K | **D344: reserve 20K alone cost 41 wins/1,638 (p .006); 14K clean in 10K+ games; layer compute w/ zero weights -63** | A |
| 71 | `choose_hold_fuel` | brain.cpp:3405-3411; config.h:57 | after a fresh target choice, open a camp fight only with 21K + reserve left, else hold one turn | **D343: unhealthy games 12 -> 0; +51/-42 n.s.**; 15K insufficient; holding all actions at 30K -42 (p .005) | T |
| 72 | Mid-turn death | main.cpp:35-58; brain.cpp:575; config.h:574 | an exception while our champion is dead -> log "died mid-turn", no error; `if (!me.is_alive()) return` before turn-end actions; `guarded()` checks `is_alive()` first | **D90 (3 games with errors vs Focus Ren), D345 (1 per ~2,000 games)** | T |
| 73 | `FuelTrace`, `FuelSpike`, `report_death` | util.h:57-102; brain.cpp:3875-3891 | per-phase fuel logging; death report of the last 10 turns with integer-only formatting (float formatting cost 85-87K of 100K fuel) | D345 | T |
| 74 | Stuck-field margin | config.h:45 | 0 | D68 no effect after D67 | X |
| 75 | First-turn init | brain.cpp:294-309 | build kit/rosters/powers; act only if 70K left; calibrate field cost with a whole-map spawn field as soon as affordable | - | T |

### A8. Shop, draft

| # | Mechanism | MC file:line | What it does | Measured | Transfer |
|---|---|---|---|---|---|
| 76 | Shop plan 7 | shop.cpp:37-110, 651-714; config.h:484-489 | melee: Treasure(main) x5, Jungle(main) x5, Durability(H) x5, Monster(main) x5, Bruiser(H) x5, Bruiser(main) forever; ranged: Treasure, Jungle, Monster, Bruiser(main). One shard bought per loop, `can_buy` guarded; a lock (10 gold) after items | D55 (Bruiser 7 pts for 5 shards beat Power), D88 (health-first online worse) | T |
| 77 | **Effective** shop after the learned reorder | shop.cpp:628-649; learn.cpp weights 68-79 | `learned_plan` appends every missing (family, main/health) pair (5 shards) and stable-sorts by w[family] + w[7+stat] - index. With the baked weights (table in Part B) my arithmetic gives melee order Treasure(main), Durability(H), Bruiser(H), Jungle(main), then unlimited Bruiser(main) (Monster and the appended Home/other steps sit after the unlimited step and are never reached) and ranged Treasure(main), Bruiser(main) forever. **[derived; check against a replay before relying]** | D340-D344 | C |
| 78 | Value shop (plan 100) | shop.cpp:113-522; config.h:497-530 | `ValueModel`: per-round time cost = fight share x dps ratio + camp-heal share x ... + pvp-heal + deaths x death cost x power ratio + recalls x recall turns; block value = rate saving x horizon; Treasure priced by its gold flow x 0.6 future share. Used by `shop_recall_benefit` (reads the same model) | D115: plan 100 alone speedrun +8..+20 (worse); recall mode 1 alone good | A |
| 79 | `shop_recall_benefit` | shop.cpp:547-590 | rate x wait + heal: rate = time saved per round by the purse spent as the shop would (finish a started block, then best blocks, shards = floor((gold + extra_gold)/30)), wait = min(spare hp / damage rate, gap between visits, horizon, 300), heal = trip x clamp((max_hp - hp)/pool,0,1), trip = recall + 1 + walk_back | D115, D343 | A |
| 80 | Shop signals | shop.h:22-41; brain.cpp:3825-3873 | per-champion history: alive rounds, gold earned, camp/pvp damage, fight rounds, deaths (own + allies' alive flags), recalls (recall channel ended on spawn), spawn visits; blended with priors over 120 rounds (config.h:506-513) | D115 | A |
| 81 | Main stat choice | shop.cpp:605-626; config.h:532-534 | focus if focus growth x focus value (spell modifiers per cooldown, aoe x 1.5, shield/heal x 0.3) > strength growth x attacks (splash x 2); HoR forced to Focus | D85 | T |
| 82 | Draft | draft.cpp:23-154; config.h:211-219 | order = mode 8 [HoR, Marcella, Ryth, Vendetta, Varg, Vesper, Stellar, Tavi, C&I, Prism, Willow, (Ren)]; then `learned_order`: stable sort by w[champion] - index (weights 56-67). With baked weights: HoR, Ryth, Marcella, Vendetta, Varg, Vesper, Tavi, C&I, Willow, Prism, Stellar, Ren **[derived]** | D116 (mode 8 near-optimal), D82 (meta draft rejected online), D322 (Vesper draft 10 vs 14/100), D361 (Vesper -65 p .001) | A |
| 83 | Prism battery shop | config.h:146 | off | D108/D129/D136 | X |

### A9. Spawn, escort, opening (all OFF), watchdogs, other

| # | Mechanism | MC file:line | What it does | Measured | Transfer |
|---|---|---|---|---|---|
| 84 | Learned spawn hold | brain.cpp:2381-2418, 494-500 | on spawn, soft_yes(dot(spawn weights)) holds <= 40 turns per visit (deterministic hash of round x 16 + index) | D340 | C |
| 85 | Fight watchdog | brain.cpp:3396-3404; config.h:270 | engaged and no attack/cast for 25 rounds -> ban group 60, disengage | D70 (events 2.33 -> 1.39/game after route scoring), D63 (15/40: 128/124 vs ~126) | T |
| 86 | Travel stall | brain.cpp:3423-3434 | best walking distance tracked; if not improved by 1 and not pushed back by > 4 for 15 rounds -> ban 40 | D78 | T |
| 87 | Staging | brain.cpp:2963-2985, 3161-3165; config.h:276 | wait outside a group's reach at distance max_range + 1 (tile score -50 x |nearest - want| - 10000 if in reach); patience 5 rounds (30 for jackpots, off), then ban 60 | D68 (patience 20/40: 157/150 vs 159 base) | T |
| 88 | Fight tile scoring | combat.cpp:350-446 | best tile: in reach 1000, else -40 x gap (walk distance counted when route known: max(straight, walk)); ranged +10 x distance when in reach; -3000 for tiles enemies can strike (calm_farm); ranged: -(4|40) x strength of any dangerous monster for which no ally is nearer (tank_near x40) | D70: wall-corner oscillation fixed, 157 vs 155 / 94 vs 85 | T |
| 89 | Ranged opens after melee | combat.cpp:866-880 | if a melee ally is near and the group is asleep, the ranged champion holds outside range and lets the melee wake it | - | T |
| 90 | Escort ball / opening party / squads | brain.cpp:3550-3640; knowledge.cpp:296-328; model.h:418-540; config.h:223-237 | OFF (squad_size 1 means each champion leads itself) | D99 (484 -> 449-457/640), D329 (pairs not better), tracks/medium.md (party3 +26 n.s., pairs150 -44, ball150 -131) | X |
| 91 | Cohesion bonus / marginal join | tracks/medium.md | rejected | -119/-154/-233, -82 | X |
| 92 | Learned layer weights | learn.cpp:7-20; learn.h:19-42 | 94 floats; "zero weights = hand-written rules" | D340-D345 | C |
| 93 | Reliability trio | config.h:60, 110, 440 | planning_turn + respawn_wait_liveness + calm_farm 1 | D171 | A |

## Part B. The learned layer: all 94 weights (`learn.cpp:7-20`), what each scales

`factor(l) = (1 + clamp(l, -3, 3)/8)^8` (about e^l, range 0.023-12.8). Blocks and offsets (learn.h:19-21): group 0-15, fight 16-31, bank 32-43, recall 44-55, draft 56-67, shop 68-79, spawn 80-87, group2 88-93 (6). Features are in the code at the cited lines. Values are the shipped (exploit3) numbers, rounded to 3 decimals.

**Group block (index: feature, weight)** - brain.cpp:2433-2494, 2347-2379. `logit = static + c_travel x travel + c_territory x territory + near x (c_enemy + group2 terms) + w1 x gem_share + w3 x wait/20 + w4 x committed/3 + w5 x health_left`; rate (and bound) multiplied by factor(logit).
- 0 travel/40 (**-0.553**), folded as `c_travel = (w0 + w8 x min(1, carried gems/100))/40` per tile of travel; 8 travel x gems/100 (**+0.315**): a 40-tile walk costs x0.58 empty-handed, x0.79 with 100 gems.
- 1 gem share of the reward when the group has gems and gold: `gem_value/(gem_value + gold)` (**+0.642**).
- 2 enemy proximity (1 at the group centre, 0 at 15 tiles, enemies in view and remembered <= 10 rounds) (**+0.455**: groups near enemies are *preferred*), 7 proximity x missing hp (**+0.011**).
- 3 respawn wait/20 (**-0.098**), 4 committed allies/3 (**+0.468**: crowding favoured), 5 health left fraction (**+0.222**), 6 territory x banked-gem gap (**-0.183**).
- Static, computed once per group (indices 9-15 = x[0..6]): 9 log1p(gems)/5 (**+0.176**), 10 log1p(gold)/6 (**+0.107**), 11 territory (d_ours - d_theirs)/(d_ours + d_theirs + 1) (**-0.099**), 12 jackpot (**-0.131**; knob off), 13 harmless (**+0.334**), 14 log1p(total hp)/8 (**+0.101**), 15 altar distance/40 (**+0.040**).
- Group2 block (88-93): `near x (w2[0] jackpot + w2[1] log gems + w2[2] committed/3 + w2[3] gap)`: 88 **+0.096**, 89 **-0.143**, 90 **-0.069**, 91 **-0.037**; 92 **+0.388** and 93 **-0.114** are unused.
- Raw weights 0-15: -0.553, 0.642, 0.455, -0.098, 0.468, 0.222, -0.183, 0.011, 0.315, 0.176, 0.107, -0.099, -0.131, 0.334, 0.101, 0.040.

**Fight block (16-31)** - brain.cpp:1566-1592: `their_losses += dot(x)` before the verdict `theirs >= ours + 0.5`. Features: 16 bias **+0.701**; 17 n_ours/5 +0.246; 18 n_theirs/5 +0.253; 19 ours_hp/(all_hp+1) +0.494; 20 hp_frac -0.047; 21 gems/100 +0.088; 22 enemy prize gems/100 +0.064; 23 on spawn **-0.426**; 24 nearest enemy/8 -0.284; 25 sim rounds/10 -0.176; 26 min(5, our_losses)/2 +0.077; 27 min(5, their_losses)/2 +0.120; 28 gem gap (enemy banked - ours)/300 clamped +-1 **+0.505**; 29 round/1000 -0.027; 30 allies_engaged +0.252; 31 spawn distance/40 +0.079. Effect: the learned edge makes marginal fights favourable (bias +0.70 = 1.4 x the 0.5 margin).

**Bank block (32-43)** - brain.cpp:2023-2046: `bag = round(25 x factor(dot))`. 32 bias **+0.493** (base bag ~41); 33 min(80, altar walk)/40 **+0.418** (far from the altar: carry more); 34 hunted (enemy memory <= 10 rounds within 10) **-0.234**; 35 hp_frac +0.059; 36 round/1000 +0.129; 37 our banked/1000 +0.176; 38 enemy banked/1000 **-0.275**; 39 allies within 6 /4 +0.178; 40 gold/500 +0.080; 41 enemies/3 -0.073; 42 min(2, gems/100) +0.085; 43 spawn distance/40 +0.234.

**Recall block (44-55)** - brain.cpp:1860-1883: `recall_frac = clamp(0.5 x factor(dot), 0.02, 0.98)`. 44 bias +0.060; 45 spawn distance/40 +0.001; 46 enemies within 8 /3 **+0.719** (up to x2: recall at ~98% when three enemies near, then `retreat()` if threatened); 47 gems/100 -0.026; 48 gold/500 -0.227; 49 round/1000 -0.303; 50 engaged in a camp fight **-0.409** (x0.66: stay and finish); 51 allies within 4 /3 -0.328; 52 min(2, incoming dps/max_hp x 10) -0.431; 53 hit_unseen **+0.343**; 54 hp_frac -0.078; 55 (their banked - ours)/300 negated -0.313.

**Draft block (56-67)** - draft.cpp:120-132: key = w[champion_draft] - index. 56 Ryth +0.526; 57 Vesper **-1.997**; 58 Vendetta -0.697; 59 C&I +0.066; 60 Stellar **-6.115**; 61 Prism -0.550; 62 Marcella -0.516; 63 Willow +0.543; 64 Ren -1.759; 65 Varg -1.812; 66 Tavi -0.925; 67 HoR **+3.890**.

**Shop block (68-79)** - shop.cpp:628-649: key = w[family] + w[7 + stat] - index. Families: 68 Monster **-2.435**; 69 Power -0.856; 70 Durability -0.034; 71 Treasure **+2.383**; 72 Jungle **-2.003**; 73 Home **+1.572**; 74 Bruiser +0.839; stats: 75 Strength **-4.068**; 76 Focus **-3.689**; 77 Health **-2.146**; 78, 79 unused (-0.286, +0.365). These were trained at Treasure = 20% and Monster = 10%; both changed in 4.0, so do not copy.

**Spawn-hold block (80-87)** - brain.cpp:2404-2417: hold on spawn when `soft_yes(dot)` (logit > 0 only; probability sigmoid(l) - 0.5 from a deterministic hash). 80 bias -0.133; 81 enemies near spawn (<= 10 rounds, within 10 of spawn)/3 **-1.359**; 82 min(3, strongest/max_hp)/3 -0.884; 83 alive allies share -0.071; 84 allies near spawn share +0.089; 85 min(1, deaths/10) **+0.589**; 86 hold_turns/20 -0.119; 87 round/1000 -0.361. In practice holds are rare: only after many deaths with no enemy near the spawn.

**Hazard weights** (hazard_model.h, not part of the 94): bias 0.44131; hp_frac -1.85129; hp/1000 -0.26579; max_hp/2000 -0.56072; allies within 4 /4 -0.69516; allies within 8 /4 +0.87246; enemies within 4 /4 +1.04075; enemies within 8 /4 +0.25555; S4 -0.24951; S8 **-3.45719**; nearest enemy/8 -1.52364; nearest ally/8 -0.12675; ranged enemies within 5 /4 +0.38594; spawn distance/40 +0.30764; round/1000 +1.65970; gems/100 -0.52176; mean enemy hp fraction (within 8) +0.58817; hp lost over 3 rounds/max +1.15225; enemy max hp/2000 -0.09465; cut_off (an enemy within 5 is nearer our spawn than we are) +0.08315. S4 = hp4/(hp4 + eh4 + 1), S8 likewise within 8, with our hp and allies' hp.

## Part C. Shared-memory repack for our chassis (used by v39f, v39g, v39h)

Current (bot.cpp:37-39, 789-790; v36a removed the dead rally writes): byte 0 squad target (group+1), bytes 1-5 solo claim of slot 0-4 (group+1), byte 6 team focus (idx + 1 | stamp<<3), byte 7 free (`kAltarSeen` is only written under `pack_mode`, which is forced false at line 149).
Proposed layout, all 8 bytes used:
- bytes 1-5 (slot i < 5): `(group+1) & 63 | status << 6`, status 0 engaging, 1 capturing, 2 cleared, 3 idle (MC knowledge.cpp:288-297). Requires `groups.size() <= 62`; on a map with more groups set a global `legacy_claims = true` and keep the full-byte encoding (news and status disabled). Check the largest group count on the 70 maps before relying on it.
- byte 0 stays the squad target (group+1, up to 255). byte 6 stays the focus.
- byte 7 = news: `(group+1) & 63 | counter << 6` (counter = 2-bit rolling post number). Writers increment the counter; a reader keeps `last_news_byte` and treats any change as a new post. Effective latency one round; ready_round is approximate (see v39f).

## Part D. Port specs, ordered by dependency and expected value

Common conventions for all specs: write fresh code in `bot.cpp`/`bot.h`; keep a `constexpr bool` per variant so an ablation is one flag; log one line per new action type (`log("name")` exists, 762); never call a new SDK method outside `try{}catch(const error&){}`. Round numbers: `round` is `unsigned` (bot.h); use `static_cast<int>`. Walk distances: `home_distance` (a `distance_field` from our spawn, built in init phase 2) and `altar_distance` exist; `group_dist(i)` below means a per-group field.

Dependencies: v39a -> everything (measure); v39b -> c, d, e, f, g, i, t; v39c -> d, h, e; v39f needs the Part C repack, and g and h read the status bits.

### v39a. Instrumentation and watchdogs (T; D70, D78, D345; no strength claim)
- Per-champion counters in `play_turn` (bot.cpp:1098): rounds per activity bucket `{dead, channel(recall/tribute), travel, fight, stage, capture, bank, idle, wait}` (MC `time_use_`, brain.cpp:537-558), counters of recalls by type, "wasted walks" (rounds travelling to a target whose group is found respawning/empty/alive-owned on arrival), watchdog events. Print one `P3` line every 500 rounds (extends `log()` at 762).
- Travel stall: remember `best_d` (walking distance to the current target from `home`/group field; use `Chebyshev * 5/4` as a fallback) and `progress_round`; reset when `d < best_d` or `d > best_d + 4`; if `round - progress_round > 15` and not engaged: `ban(target, 40)`, clear `objective`, `cluster_goal`, set `squad_choose = 0` (MC brain.cpp:3423-3434).
- Engagement watchdog: `last_hit_round` = last round `combat(target, ...)` returned true with an attack/cast on that group; if `engaged` (a monster of the group is awake or we are within attack range of one) and `round - last_hit_round > 25` and the group is not a monster-siege: `ban(target, 60)`, `squad_choose = 0` (3396-3404). Squad stall: if `squad_goal` unchanged for 40 rounds and no ally within 3 of a camp of it, `ban(sq, 60)`.
- Capture stall: if `move_to(g.spawns)` fails 3 turns in a row while capturing, drop the capture and `ban(g, 10)` (D78); capture patience: > 100 turns holding an uncaptured reward -> `ban(g, 40)` (3063).
- Edge cases: `ban()` is `round + rounds`; do not count turns while stunned or recalling; reset all trackers when the target changes.
- Test: 02gift-wrapping (910 squad turns), 02the-pack, 01shortcut, boss_battle: stuck turns per champion must fall; other maps neutral. Expected: reliability, not wins.

### v39b. Belief layer: per-group memory, liveness, respawn travel (T; D124, D60, D120)
- Replace `Group::{reward, ready_round, seen_round}` by `Belief{status(alive|reward|respawning), respawn_round, seen_round, hp_left, awake}` plus `std::vector<float> probe_hp` (HP last seen per camp, aligned with `probes`; initial = `camp_stats_for` max; set 0 on death; reset to max when status turns alive again after respawn). Update in `observe()` (bot.cpp:272-291): a group is seen if any probe tile is visible (existing). `hp_left = Σ visible camp hp + (unseen members x type max)`; sleeping camps keep exact HP [doc]. If no living camp is visible: if previously respawning and `respawn_round > round` keep; else query `g.handle.state()`: respawning(timer) -> `respawn_round = round + timer`; reward -> `status = reward, hp_left = 0`; else alive.
- `blocked_respawn(g)`: `status == respawning && seen_round == round && respawn_round <= round` -> reject target (MC brain.cpp:2203; avoid walking into a group at timer zero that is not alive yet).
- Respawn travel: accept a respawning group as a target if `respawn_round - round <= walk` (`approach_respawn`, model.h:17); on arrival within 2 tiles wait beside it, never on a member tile (v39t `leave_camp_tiles`); if `wait > max_respawn_wait (0)` after arrival, drop it. This replaces our `wait > travel + 10 -> fallback fb` rule (bot.cpp:853-856).
- Use `probe_hp` in `rem_hp()` (890) and `solo_target` (842) so damage persists across trips. `forecast()` (897) scale = `hp_left / total_hp`.
- Edge: when a member tile is visible but camps hidden by bushes are not counted, `unseen_hp` stays at max (MC knowledge.cpp:73-76).
- Test: speedrun vs the starter (pace), sparring 240, new pool; expect fewer idle-respawn turns (MC 22.4 -> 0 per game).

### v39c. Cached walking-distance fields and fuel calibration (A; D67)
- One lazily built `distance_field` per group rooted at its probe tiles, walls = `terrain | all camp tiles` minus the roots; cache in `std::vector<std::unique_ptr<distance_field>> group_field`. Build when `fuel_remaining() > est + 20000 + 14000` where `est = step_cost x depth + 3000`, `depth = max corner cheb distance x 7/5 + 5` (world.cpp:168-182). `step_cost` starts at 260, after each build update: `rate = (cost - 3000) x 115/100 / steps + 1` if steps >= 10 (keep the maximum; model.h:140-150). A 2-step pocket search must not poison the rate (D67).
- `walk(from, g) = field.get(from)` if reachable else `1<<14` (reject); fallback with no field = cheb x 5/4. Use `route_pos` = nearest non-camp walkable neighbour when standing on a camp tile (ctx.cpp:130-147).
- Replace the per-call 260-step field in `solo_target` (823) and `squad_target` (956), and `cluster_target` (997). Keep `home_distance`/`altar_distance`; add `spawn_field` calibration on the first turn (brain.cpp:306-310).
- Edge: giant maps (93x93): the full build is the worst case, so build the 3 nearest groups first (MC `warm_fields`, brain.cpp:611-633: altar field first, then the nearest uncomputed group while `fuel_ok(field_cost + 30000)`).
- Test: fuel usage per turn (add to v39a log), identical decisions on small maps, better on fracture/yellow-brick/quadrants.

### v39d. Target score v2 (A; D58, D68, D69, D100, D60, D120)
Applies to `solo_target` and `cluster_target`; `squad_target` keeps its test but takes the same cost terms.
- Inputs per group `g` (static): `gems`, `gold`, `hp` (total), `str_total`, `weighted_hp` (Smith: sort camps by strength/hp desc, `W = Σ str_k x cumulative_hp_k`), `home_walk` (= `home_distance` of the group centre, or walk from spawn). Dynamic: `hp_left`, `scale = min(1, hp_left/hp)`, `travel = walk(route_pos, g)`, `wait = max(0, respawn_round - (round + travel))`.
- `dps = camp_dps(me)`: `strength x attacks + Σ spell modifier x focus / cooldown (camps) (aoe x (1 + neighbours)); basic x (1+neighbours) for splash (Varg)`; `neighbours = min(n-1, 2.5)`. Our `dps()` (294) is close; add the neighbours terms.
- `forecast(dps, scale)`: `rounds = max(1, ceil(hp x scale/dps - 1e-4))`, `damage = max(0, W x scale/dps - 0.5 x str_total)`.
- `pool = my_hp / camp_mult` (camp_mult = (1 - 0.30 Jungle) x (1 - 0.10 Durability) owned; read from `me.item_count()`; refresh after a purchase), plus for each ally actually on this group (slot claim or visible within 8): `ally.hp x 0.8 x growth` and `ally.dps x growth` (growth = clamp(strength/base, 1, 4)).
- `trips = max(1, ceil(damage x margin / pool))`, margin **1.6** (MC `camp_safety_margin`; our v27 `kEff .6` already pessimises rounds, so start at 1.3 and sweep 1.0-1.6); feasible if `damage <= 0` or `trips <= 4` (**max trips 4**). `overhead = recall_time (5) + 1 + home_walk(g)`.
- `siege_rounds = rounds + (trips-1) x overhead`. `hp_rounds = int(1.0 x frac x overhead)`, `frac = min(1, damage x camp_mult/(members x max_hp))`.
- `members = 1 + max(committed, coming) + extra`; evaluate `extra in 0..min(1, team_size-1-committed)` (one hypothetical joiner of average ally dps/hp) and keep the best rate.
- `rate = (1.5 x gems + 1.0 x gold) / max(1, travel + wait + hp_rounds + siege_rounds + 5) / members`. Gold weight and gem weight are the two knobs to sweep: our current 0.15/0.08/0.04 vs MC 1.0 gold per 1.5 gem. Capture cost = 5, or `capture_state().timer` / 3 with the Capture emblem (v39s).
- Modifiers: harmless group with another ally committed x0.1; banned x0.05; the 8-round re-score and hysteresis: switch only if `new > 1.35 x current` (replace the 1.6 objective bonus, bot.cpp:861); bound pruning: rank groups by `reward / max(1, travel + 5)`, score at most 16 full groups, stop when the best score exceeds the next bound; planning fallback: when fuel < 45K+reserve, score groups round-robin (≤16) without acting.
- Engage test (MC `force_sufficient`, brain.cpp:3949): at arrival engage if the champions present reach `target_need` (committed + 1), or `damage x 1.6 <= pool`, or one trip removes >= 35% of the remaining hp: `progress = min(1, dps x (pool/1.6)/(damage/rounds) / hp_left)`; else stage outside reach at distance `max_range + 1`, max 5 rounds, then ban 60.
- Edge: the starter/passive-opponent speedrun can regress (+22 rounds when D100's heal cost is on); the gain was meeting enemies healthier, so judge on sparring wins and deaths, not speedrun.
- Test: flags `GOLDW`, `HEALCOST`, `TRIPS`, `HYST` separately; baselines per section 2 of the comparison file.

### v39e. Capture-wait recall and value-based shop recall (T/A; D343, D115, D65)
- State: `hold` = consecutive turns standing on a member tile of the group being captured (reset when we step off or capture completes).
- Capture recall: when `hold >= capture_time - recall_turns + 1` (5 - 5 + 1 = 1 without Home; with Home 3 turns: 5 - 3 + 1 = 3; with a Capture emblem use `timer` from `capture_state()`), `enemies.empty()`, no hidden source (`!unsafe_recall`), `threat(pos) < 1`, not already recalling: compute `after = gold + 1.33?(Vesper) x group_gold` (MC counts Vesper's +33%; the Treasure/Prospector bonus too), `benefit = shop_benefit(extra = reward_gold)`; recall if `benefit >= 0.3 x walk(spawn -> group) - 0` (MC `capture_recall_walk 0.3`, slack 0; the later candidate uses 1.0 except 0.3 near recent enemies). Fallback when the value model is not ported: `after >= 90` or `hp < 60%` (MC's first version, D326: 167 vs 165, speedrun +38, i.e. weak); the value rule is what gave +354/-203. Publish status capturing while recalling so allies do not step on the tile (MC brain.cpp:435).
- `shop_benefit(extra)` simplified: `shards = floor((gold + extra)/30)`; if 0 -> 0. `rate = time saved per round by spending the purse` approximated as `shards x 0.0015 x max(1, round_remaining/1000)` rounds per round ... **[the full model is v39p; until then use a step function: benefit = (shards >= 5 ? 25 : shards x 4) + heal, heal = trip x clamp((max_hp - hp)/ (0.5 x max_hp), 0, 1), trip = 6 + walk_back]** (guess constants; tune on weak bench). `wait` factor omitted.
- Shop recall on the way (replaces bot.cpp:1196): while travelling, nothing in view/unseen/camp threat, not spawn: `extra = from_spawn + recall + 1 - d`; recall if `benefit >= max(0, extra) + 2` (value mode) or, purse mode, `gold >= 300 && extra <= 20` (**D65: 300/20 gave 179 vs 163/280**). Remove our `gem_count()==0` condition (gems are kept through a recall, MC brain.cpp:2096).
- v38a already has a fixed-threshold capture recall; replace its condition with the above and keep its safety checks.
- Test: gold spent by r200, first shop round, recalls per champion, deaths; sparring 240.

### v39f. Group news in byte 7 (A; D345)
- Poster: in `observe()` after updating beliefs, for each group `g` seen this round with `status == respawning` and `respawn_round > round + 5`: urgent if an ally's claim/squad target (bytes 0-5) points at `g` and that ally is alive and not capturing it; choose the best (urgent first, then `gems + gold`); skip if the current byte already names `g` and no more urgent; write `(g+1)&63 | (counter+1)&3 << 6` (`write_byte(7, ...)`). Do not post when `groups.size() > 62` (see Part C).
- Reader: each `observe()`, read `shared[7]`; if different from `last_news_byte`: `g = (b & 63) - 1`; if `g` valid and we do not see `g` this round and our belief is not respawning with a later `respawn_round`: set `status = respawning`, `respawn_round = round + groups[g].respawn - 4` (approximate: the poster saw the timer near its start), `hp_left = -1`. MC writes the exact 16-bit round (brain.cpp:3692-3720, knowledge.cpp:257-286); ours is one byte, so the estimate is +-5 rounds.
- Also apply the `cleared` slot status (status 2 on a claim byte): a champion that finishes capturing publishes `cleared` for the group for the next turn; receivers `mark_respawning(g, groups[g].respawn)` (knowledge.cpp:155-166; `shared_capture_confirmed_only 1`: ignore the inferred 'capturing disappeared' signal).
- Test: the wasted-walk counter (v39a); expect 5-14% fewer wasted champion-rounds on mid and large maps.

### v39g. Capture handoff and designated capturer (T/A; D362)
- Rule (when `enemies.empty()` for the champion considering it): a champion standing on a member tile of a reward group keeps it only if no ally on a member tile has a lower roster slot; any other champion calls `leave_capture`: `ban(group, capture_time + 2)`, clear target/objective/squad claim, publish idle, `leave_camp_tiles()`, and re-choose next turn (do not rescore on the same turn: MC fuel exhaustion g101-001-01islands). With the slot status bits, count `capturers(g)` from allies with status capturing; do not start a capture if `capturers(g) > 0` (score 0, brain.cpp:2234).
- With a Capture emblem (v39s) the holder is the preferred capturer if it is within 3 tiles of the nearest; else keep the lowest slot.
- Replaces our "nearest champion within 10 captures" (bot.cpp:1212-1220) and the step-off rule.
- Test: pace vs the starter (MC -17 +- 4 rounds), sparring wins, captures split (reward shared) counter.

### v39h. Recall package (T; D61, D64, D66)
- `recall_health_frac`: sweep `heal_at` 0.40 -> 0.50 (non-careful; careful keeps +0.15) at bot.cpp:1172 (MC D61: 0.50 best at 148/216 vs 127). Also finish a nearly dead camp fight first: if `damage x camp_mult < 0.6 hp` and `hp_frac > 0.15`, skip the recall (brain.cpp:1937).
- Travel recall: before moving toward the target, if `d = walk(pos, target) < 1<<14`, `from_spawn = walk(spawn_center, target)`, `d > from_spawn + recall_turns + 1 + 4`, `enemies.empty()`, no hidden hit, `threat(pos) < 1`, `!spawn`: `me.recall()` (+log "travel-recall"). `recall_turns = ceil(5 x (1 - home_magnitude))` (Home: 3).
- Tribute recall (inside `bank()` before the walk, bot.cpp:638): if `ad > spawn_to_altar + recall_turns + 1 + 4` and nothing in view: recall; bag kept.
- Test: recalls per champion, travel share of time (MC: travel is ~34% of champion time), deaths on the walk.

### v39i. Tribute trigger and guards (T; D102, D76)
- Trigger: `gems >= 25` or `walk(altar) <= 8` or `rounds_left <= walk + channel + 15` or `banked + gems >= 1000` (MC brain.cpp:2047); channel = `ceil(gems x submit_gem_duration_multiplier)`, min 1. Compare with ours (bot.cpp:548-557: carry 25-60); do not adopt blindly: MC D102 kept 25 as the head-to-head optimum (bigger bags lose to hunters), and ours banks 17 vs 37 per game, so sweep carry floor 25/30/40 with `20 + ad - nearest_group` removed.
- Own altar lock before channelling (`lock_mode 2`): already in v25s.
- Cancel a tribute channel when `Σ dps of enemies within (3 for melee, 5 for ranged) x rounds_left >= 0.8 hp` (brain.cpp:395-398) and rounds_left > 1: ours (1131) uses `threat() x remaining > 0.9 hp`; equivalent.
- Test: submit/collected ratio (ours 79% vs 95%), banks/game, gems lost on death.

### v39j. Fight simulation and verdict (A; D59, D75, D84, D87)
Port `simulate_skirmish` and the verdict, replacing `fight()` (bot.cpp:1037-1096) lost/outnum/danger. Highest risk: MC's own rewrite failed (D327) and D86's calm_farm mode 2 lost. Do in stages: (1) sim as an extra veto/boost on the current rule; (2) replace.
- Fighter fields: `hp` (+ `3 x max_hp` if on its own spawn tile; + `shield_now` + a ready shield ability `modifier x focus`), `dps` = basic (`strength`, enemies: live strength/focus, allies: design power x growth), `cast[2]` (`modifier x focus` per damaging/cc/aoe ability that can hit enemies; attack reset = strength; dash damage `modifier x focus`), `ready[2] = 1 + live cooldown` (unknown enemy = ready; unknown ally = not ready), `cooldown = max ability cooldown`, `value = 1 + gems/40` (Cassi alone +1; linked pair dies together), `arrive = 1 + max(0, gap - reach)/2` with `gap = distance to the nearest opponent - sighting ages` and `reach = walk reach (melee 2, ranged 4) + ready dash range + ready spell geometry (range + radius + move)`.
- Rounds: horizon 15 (max 32). Each round both sides deal `Σ dps of arrived living + cast events due this round` to the opposing focus (the arrived living fighter with the least current hp); overkill carries; deaths update focus; stop when a side is dead or nobody can hit. Casts: each slot fires at `max(arrive, ready)` and every `cooldown` rounds; if both slots coincide the stronger first, the other one round later. Outcome: `our_losses`, `their_losses` = Σ value of dead fighters, `first_target`.
- Participants: us, allies within 6 (visible), enemies within 8 off their spawn (or within reach if on spawn), remembered enemies (seen 1-5 rounds ago, within 6 + age tiles, hp as last seen). Cap 16 fighters.
- Verdict: `favourable = their_losses >= our_losses + (allies_engaged ? 0 : 0.5)`; `doomed = hp <= 2 x enemy_threat_at(pos) && rounds > 2`. If on own spawn: fight if favourable; a second sim with hp without the spawn bonus decides `leave_ok`; hold up to 40 rounds per visit while `!leave_ok` and the nearest enemy is within 8.
- Branches: (a) favourable and not doomed: fight (close in when nearest <= 5 or an ally within 6 is in contact); (b) `no_loss_stance`: `our_losses < 0.5 && !doomed`: answer in place if hit-able, else keep farming; (c) otherwise retreat only if `nearest <= 5` or an enemy can strike next turn (`calm_farm 1`); else keep farming.
- Keep our shared team focus byte (focus candidate = `first_target`).
- Learned edge: optional, see v39r.
- Test: sparring kills/deaths, hunter proxy, then ladder scrims; abort if deaths rise > 1/game.

### v39k. Hazard disengage (A; D347, D360, D362) - low priority
- At the verdict step (not on spawn, `e8 > 0`): compute the 20 features and `z = Σ w x` with the default weights in Part B; fire if `z >= ln(0.3/0.7) = -0.847`; set `hazard_until = round + 2` (commit 3 rounds) and `retreat()` while hot. Retreat = v39t. Features: hp_frac, hp/1000, max_hp/2000, allies within 4/8 over 4, enemies within 4/8 over 4, S4/S8, nearest enemy/8, nearest ally/8 (default 8), ranged enemies within 5 over 4, spawn distance/40, round/1000, gems/100, mean enemy hp fraction within 8 (1 if none), hp lost over the last 3 rounds / max_hp (ring buffer by round%4), enemy max hp/2000, cut_off.
- Weights describe MC's v44 contact states and 3.0.5 stats; **refit** on our scrim cache before trusting (public-repos report item 9). Online effect for MC was +0.2 +- 1.7 pp; do it last.

### v39l. Offence: finish-kill, kill-chase, ally help (T; combo2 candidate)
- finish-kill: before any fight/retreat branch, for each visible enemy off its spawn within `max(range + 1, 4)` and in vision: `eff = hp + shield`; killable if `eff <= 0.9 x burst(d)`, `burst(d) = (can attack and d <= range ? strength : 0) + max over ready damage/cc/aoe abilities that reach d of modifier x focus + (attack reset ? strength : 0)`; melee may step one tile (never off our spawn) if `eff <= 0.9 x burst(d-1)`. Target score `gems x 20 - eff + (Cassi/Issac 500)`; step (score -2000), attack, then cast the best ability at it.
- kill-chase: in favourable fights chase the focus target up to 6 tiles if it is channeling or `hp + shield <= 2 x burst`; otherwise the limited chase (ranged `range + 1`, melee 3, target farther than 6 from their spawn).
- ally help: when `hp >= 50%`, not capturing, an ally within 12 (and beyond 2) has an enemy off spawn within 3, step toward it (`move_to(disk(ally,2))`); one per turn.
- Test: kills (ours 0.6/game), deaths, flips on sparring; MC's evidence +201/-123, +198/-152 (its own family).

### v39m. Wards (T; D71, D72)
- At turn end (after actions, not while recalling/tribute/teleport/dead; `me.ward_cooldown() == 0`): candidate tiles within `ward_placement_radius` (2): legal per `me.ward_placement_tiles()`, not wall/hole/altar, no champion/camp/ward on it; cost = `cheb(tile, pos) + (bush ? 0 : 100)`; keep 3 lowest; `place_ward` in order until one succeeds. Replaces bot.cpp:1146-1150 (altar/capture only). Count placed wards per game (MC ~526).
- Edge: wards cost nothing; check for engine error codes and stop after 3 errors logged.
- 4.0: wards cd 10, vis 6, place 2 (patch-4.0.md) - same values MC assumes.

### v39n. Navigation hardening (T; D78, D96, D70)
- `leave_camp_tiles` (MC brain.cpp:3893-3933): whenever idle/waiting/staging on a member tile of any camp group (not capturing): step to the neighbour that is not a camp tile and farther from the group centre (score = (non-camp ? 1000 : 0) + cheb to centre); if none, BFS (radius 10) from tiles that are neither walls nor camp tiles and step along it. Call it from every idle exit.
- Movement primitive: `try_moves(ordered)`: skip tiles with a visible champion/camp; on a failed move (hidden occupant) remember the tile for the turn and try the next. Obstacle mask cached per turn, invalidated after any move/dash. Our `move_to()` (376-415) uses one best neighbour only; add the fallback list.
- Safety-field retreat: bounded BFS (radius 10) from tiles outside every threat's reach (awake camps range+3, unseen, enemies by reach); score = -dist_to_safety x 1e5 - threat x 10 - home - 2 x cheb(ally) (retreat_ally_pull 2). Replace the `threat x .08 - 2 x nearest` rule in `move_to(flee)`.
- Fight tile scoring (combat.cpp:350-446): for ranged: never be the nearest champion to a dangerous monster when a melee ally is near (penalty `40 x strength`, else `4 x`); tiles an enemy can strike next turn -3000; out-of-reach uses `max(cheb, walk distance)`; ranged holds outside range while a melee ally opens the fight.
- Test: boss_battle/shortcut/stampede deadlocks (D96), camp deaths, oscillation counter (A/B tile swapping).

### v39o. Fuel discipline and mid-turn death (A; D343, D344, D345, D90)
- Reserve 14K (MC `fuel_reserve`): every optional action starts only if `fuel_remaining() > need + 14000`; phase needs: threats 45K, basic 12K, farm 25K, choose 45K, per-group score 26K, fight move 24K, strike dash 26K, escape dash 36K. After a fresh target choice, open a camp fight only with 21K + reserve left (`choose_hold_fuel`).
- `main` loop: catch exceptions per turn; if our champion is dead after an exception, log "died mid-turn" without an error (MC main.cpp:35-58); in turn-end actions check `me.is_alive()` first; keep `guarded(what, fn)` wrappers.
- Death report: integer-only formatting of the last 10 turns (floats cost 85-87K of 100K fuel on the death turn).
- Test: count suspended turns and error lines over a full bench; ours is currently unmeasured.

### v39p. Shop v2: value model and 4.0 families (A; D115, D55, D65, D88)
- Port `ValueModel` (shop.cpp:113-400): build = (strength, focus, health, owned passive families); per-round time cost = `fight_share x dps_ratio + camp_heal_share x dps_ratio x hp_ratio x camp_ratio + pvp_heal x hp_ratio x all_ratio + death_rate x death_cost x pvp_power0/pvp_power + recalls x recall_turns`; shares from `ShopSignals` blended with priors over 120 rounds (prior fight 0.36, heal 0.15, damage 4.0 hp/round, gap 130 rounds, deaths 0.0004/champion-round, income 1.4 gold/round, end 1200 rounds); block value = rate saving x horizon; `death_cost = respawn 60 + walk_back`; `walk_back` = median spawn-to-group distance. The recall benefit (v39e) calls it.
- 4.0: extend `Family` with tribute..collectors (ids `family x 6 + stat x 2 + (shard ? 0 : 1)`, first seven unchanged). Treasure magnitude is read at run time (0.10 now), so the model prices it correctly; Monster 0.15; Prospector/Capture/Hunter/Skirmish/Collectors need pricing: Capture = 2 rounds saved per capture x captures/round; Prospector = 0.25 x cluster income share; Hunter = 50 x kills/round; Skirmish = 0.05 x pvp dps; Collectors = 0.01 x families owned x dps.
- Order until the model exists: Monster(main), Jungle, Durability(H), Bruiser forever; then one Capture + Prospector for the designated capturer; drop Treasure. Do not copy MC's learned order (derived in A77) - trained at Treasure 20%.

### v39q. Draft (A; D116, D82, D322, D361)
- Keep the data-driven orders (v37a). Re-test with 4.0 stats (Vesper -18% Strength; HoR Focus growth 12 -> 10; Marcella/Ryth growth -10%; Cassi +43% base Focus; Ren stun 1.1x; Willow +17% Focus; Varg +12% Str; Stellar Focus growth 8.5): one-slot swaps on sparring and the new pool. MC's order for comparison: HoR, Ryth, Marcella, Vendetta, Varg, Vesper (derived after the learned reorder). Do not copy the learned offsets (HoR +3.89, Stellar -6.12, Vesper -2.0) - they are pre-patch.

### v39r. Optional learned-edge scaffolding (C; D340-D345)
Only for a coder who wants to reproduce MC's residual layer without training: implement `factor(l)` and the four blocks as multiplicative/additive adjustments with **zero** default weights (identity), then switch on single blocks one at a time using the Part B values as priors: fight edge (bias +0.70, gem gap +0.505), recall fraction (enemies +0.72, engaged -0.41, hit_unseen +0.34), bag (bias +0.49, altar distance +0.42, hunted -0.23), group factor (travel -0.553/40 per tile, gem share +0.642, harmless +0.334, committed +0.468). Expect no gain without retraining: MC measured +34 of ~160 for news once weights were co-trained and a -97 interaction when mixing (D345); the weights are fitted to their formulas.

### v39s. 4.0 capture state and Capture/Prospector holder (A; patch 4.0)
- `g.handle.capture_state()` -> `{timer, state}` (needs the group visible): use `timer` as the capture cost (3 with the emblem else 5) in all rate formulas, in the capture-recall hold counter, and in handoff; treat `enemy_capturing` as "reward will vanish": abandon unless arrival <= timer + 2 and hp >= 50% (contest), and mark `contested` groups banned for 10 rounds.
- Designate one holder per team (the lowest-slot melee or the champion with most gold at the first shop): buy Capture(main) 5 shards then Prospector(main) 5; handoff prefers the holder (v39g). The rule text is conflicting on mid-capture joins (see limits): probe once.

### v39t. Camp-fight micro and edge handling (T; D70, D88)
- Smith priority for the next camp target: `strength / hp`; harmless last (priority `-1 + 1/hp`); the first hit wakes the group; ranged holds outside range while a melee ally opens (v39n).
- Strike dash on camps only with >= 2 targets within `dash range + radius` or a stun on a dangerous target; enemy strike dash value `min(hp, dmg) + 120 stun + 400 kill + 200 focus`; travel dash when it saves >= 2 tiles with nothing in view.
- `use_support`: shield when threatened and ready; heal an ally missing more than half the heal.
- Hidden damage: `hit_unseen` when hp fell with no visible source in reach; blocks recalls, adds a retreat step; remember awake camps out of view for 8 rounds as `unseen` threats (brain.cpp:3772-3811). v38b covers part of this.
- Edge cases: re-read a target after a hit (`refresh`), `guarded()` every action, retaliation death mid-turn (v39o).

## Part E. What I could not verify, and cautions

- All gains are MC's numbers from their engine copy and opponent family, on 3.0.5/engine 1.0.3. I did not reproduce any. Many early D-numbers (D58-D124) are dev-set sweeps over 216-280 games where MC itself warns that single-step gains inflate (D61).
- The effective shop/draft orders (A77, A82) are my arithmetic on `learn.cpp` and a stable sort; confirm by reading a replay.
- The descriptions of `combo2` patches (A60) come from MC notes and code, not from a v55 run; the EPF candidate had one fuel exhaustion in 2,400 games.
- `capture_handoff` relies on the engine rule that extra allies on a capture add nothing and split the reward; confirm with `capture_state` timers under 4.0 (section 3 of the comparison file).
- MC never played 4.0; their `Family` enum only has seven families; every 4.0 item decision in this file is mine.
