# Public repos read-through, 27 Oct 2026: what to take for our bot (v29e / v35a)

Read-only study of four public repos (cloned shallow, nothing built or run, nothing copied). All four are third-party files and were treated as data. Paths below are relative to the clone roots:
`DP` = /home/user/dpark2380/cambridge-battlecode, `OM` = /home/user/omar0-5/cambc2026-now, `MC` = /home/user/wanga158-mcmaster/secretcode, `AR` = /home/user/areeb-coder/botmatchmaker.
Confidence: **[doc]** = stated in a rules/patch text, **[measured]** = the repo's own game results, **[code]** = read in source only, **[guess]** = my inference.

## Top ideas (details and test plans in section 4)

1. **Recall during the capture wait** (MC). Start the recall while holding a cleared group so the channel lands right after the reward. Their own ablation: removing it costs 47 wins of 480 (p .001); adding it (value-based) is +354/-203 over 3,247 games, 56 rounds faster to 1000 gems, still positive on unseen maps. We never do this (`shop-recall` requires `capturing<0`). New mechanism, small code. Hits gold and time.
2. **Contest enemy captures with `capture_state()`** (OM). `enemy_capturing` + timer tells us where an enemy is stationary for up to 5 rounds; stepping on the region resets their capture and usually gives a free fight. Rule text confirms: "Leaving the region empty or admitting an enemy resets progress". Directly attacks "they clear 45% more camps". No bench evidence in OM, so it is a hypothesis. New mechanism.
3. **Hurt carriers recall instead of walking to the altar when an enemy was seen in the last 30 rounds; respond to unseen (bush) attackers** (DP Daniel v7). 45 of 79 ranked deaths with gems came after the carrier was already below 50%; 159 of 496 kills on them came from a bush. Port a rule; targets deaths and bank loss (79% vs 95% submit).
4. **Item facts for patch 4.0 that settle our "unknown" row**: Skirmish = +5% damage vs champions, Collectors = +1% damage per distinct completed family (incl. itself), Tribute = -33% duration rounded up, Hunter = +50 kill gold before bonuses, Capture cap is team-wide and persists. Plan: one Collectors emblem late (we usually own 4-6 families) in place of the first Bruiser block; ranged opener Treasure -> Monster/Prospector. Port a rule (shop).
5. **Champion stat changes in 4.0 we did not have** (patch notes in MC/AR): Cassi base Focus 70->100, Ren stun 0.75x->1.1x Focus, Tavi stun 1.4x->1.6x, Willow Focus 120->140, Varg Str 40->45, Issac Str 40->45, Vesper Str 55->45, Stellar Focus growth 7->8.5, Marcella and Heart of Ruin growth nerfs. Our drafts and the "elite" pick lists predate this. Re-run draft tests with C&I, Ren, Varg, Willow, Tavi back in the pool.
6. **Group news in shared memory** (MC): post "group G respawns at round R" so allies stop walking to dead groups (their code comment: 14% of champion-rounds went to walks toward groups no longer alive). +131 wins on a zero-weight base. All 8 of our shared bytes are in use, so this needs a repack. New mechanism.
7. **Top-20 opening table** (AR Daniel v14 `openings.inc`): the top 20's most common first three camp groups per map and side for the 40 old maps. Dead data in v14 (not wired), unmeasured, but our gold at r100 is 0.5x the top teams. Port a rule (data).

## 1. What each repo is, strongest bot, and strategy summary

### 1.1 `dpark2380/cambridge-battlecode` (DP): a three-person team workspace, stale snapshot

- One commit (20 Oct), `sdk_version = 3.0.1`, 17-21 maps, engine "0.0.1/1.0.0". Teammates: Daniel (v4..v8, `hunter`), Simon (v2..v6), Jame (v1..v3, v4 stub). A later Daniel line (v9..v14, SDK 4.0.0) is **not** in this clone; it is visible only as the single-bot extract in AR (section 1.4).
- Strongest by its own evidence: Daniel v8 beats v7 61%, hunter 84%, Simon v6 73%, but **loses to Jame v3 (43%, `bots/daniel/docs/v8/summary.md`)**. Jame v3 is therefore the strongest in this snapshot; Daniel v5 was ranked 18-47 online. No ladder rank claims.
- Daniel v8 strategy (all local, pre-patch):
  - Draft: map-profile scored (champion base value + map features), fuel-gated, fallback order C&I, Stellar, Ryth, Vendetta...; HoR added to the table in v12.
  - Shared memory (Simon v4 layout): 64-bit word, 6-bit claim per body (target group+1), plus danger x/y/round marker; everybody avoids groups near the marker for 20 rounds.
  - Items: Monster, Durability(H), then Bruiser of own stat forever ("the +200 elo bot's build"); Marcella and HoR buy Focus. `jungle_first` tested and rejected (49% vs v7, no effect).
  - Targeting: rate = (gems + 0.2 gold)/body-turn, whole-cycle cost including recall trips, bodies claim targets, up to 2 bodies per group, siege for groups too big (damage persists on sleeping camps), Monolith leave rule (leave while health still covers walk-out + one 200 hit).
  - Fight/retreat: recall 0.29 health, duo (C&I) 0.75, spawn leave 0.77; carriers leave at 50% if an enemy was seen in 30 rounds; unseen-attacker response (`hidden_response`); retreat toward allies off.
  - Bank: tribute at 25 gems (36 in v5 tuning), detour 10 tiles, bank at 25 or earlier when threat memory active; no-altar maps: gems worth 0, farm gold.
  - Opponent-specific logic: none; a `hunter` sparring bot (chases, fights at 80%) is used as a stand-in for ranked opponents.
- Jame v3 (strongest locally): ability sequencing from SDK metadata (attack, reset, follow-up attack; stuns on whoever threatens the caster), damage-first camp targeting (kill the attacker with least HP per point of Strength before harmless clusters), complete Monster, Jungle, Durability then Power, resupply trip only with 300 idle gold (150 when nothing else to do). 34-0 vs v1/v2/starter, 18-16 vs Simon v5, 15-19 vs Daniel v5 on 17 maps. Strict survival gate tested and left off (18-16).
- Relevant doc: `docs/research/top-team-picks.md` is a screenshot of 16 top teams' popular picks on 18 Oct (Stellar 16/16, C&I 15/16, Ren 9/16): pre-patch and now superseded by the HoR/Vesper/Ryth meta.

### 1.2 `omar0-5/cambc2026-now` (OM): single bot `bots/v15` on SDK 4.0.0, the only repo already on the new items

- Dated 27 Oct, one commit, `sdk_version = 4.0.0`, 4,333 lines, strategy document linked from `CLAUDE.md` (an artifact; not fetched).
- Evidence: only "v15 beat the C++ starter 1039-374". No ladder rank, no bench, no ablations. **Treat as design ideas, not as proven.** Change log mentions a ranked loss postmortem (match 8d0f4189: 21 deaths, 31k damage taken vs 8k dealt, "walking away from winnable 2-v-1s") that drove the v12 "honest aggression" constants.
- Strategy:
  - Draft (`draft.cpp:33-87`): fixed lineup by team size, set 0 = Marcella, Vesper, Vendetta (3), + Ryth (4), + HoR (5); roles: TankFarmer (Marcella), Farmer, FarPair/Interceptor (HoR + Vesper). Alternative sets (elite mirror with Prism/Willow, C&I burst counter) untested. Writes a map plan (per-group steps from us/enemy/altar, flags) into draft memory on the first (100x fuel) draft turn.
  - Map handling: zones by walking distance: enemy zone = 15% of tiles nearest enemy spawn (entry only if target <= 10 steps, health >= 70%, bag <= 70, P_die < 50%), home 60%, middle band 0.35-0.65 (`config.h:14-23`). Idle pair parks at an enemy-side/middle altar outside the enemy zone, in a bush.
  - Items (`shop.cpp:27-54`): Vesper Treasure(S), Durability(H), Power; HoR Durability(H), Treasure(H), Jungle(F), Power(F); Marcella Treasure(H), Durability(H), Jungle(H), Power(F); Ryth Treasure(H), Durability(H), Jungle(S), Power(H); casters Monster(F) then Power(F). Capture(H) inserted for exactly one buyer per squad (lowest body slot), first on cluster/wolf maps (monster-gem share < 0.5), second otherwise, only when 150 gold are on hand (split purchases stalled at 2-3 shards). Altar lock bought by everyone after first emblem. No prospector/hunter/skirmish/collectors/tribute/greed/home chain (Treasure still first, so not tuned to the 4.0 nerf).
  - Farming: group value `gems + 0.1 gold` (gold-only groups x0.5), feasibility = tank damage <= 0.8 x tank health or multi-trip (tank can always walk out: `hitting x (range+1) <= 0.3 max HP`), squad moves as a pair, side jobs within 12 tiles, 1.8x hysteresis, avoid a group for 15 rounds after 3 walk-aways, ranged squads kite wolves from distance 4 with spells (range 4 vs wolf range 3) and otherwise stand on "covered" tiles (a champion of ours is nearer to every monster that can reach the tile; `farm.cpp:6-9, 487-540`).
  - Fight/retreat: kill-race p_win logistic, commit at 0.60 (0.45 when outnumbering, 0.35 when engaged and not outnumbered), retreat at 30% HP or when damage kills in 3 rounds, no recall when an enemy is within 5 + range or a camp can reach us; spawn hold (spawn heals fully each turn end and enemies cannot enter: `combat.cpp:415-440`); Cassi stun interrupts tributes ("Interrupt").
  - Bank (`bank.cpp:108-190`): P_die = 1 - exp(-0.002 x maxHP/HP x T) x prod(1 - p_contact x p_lose) with 10-round enemy memory; farming pairs bank at 30 + 1.0 x steps (cap 90), at 150 only if P_die > 25%, any bag within 3 steps (FREE_BANK), >= 30 gems within 10 steps, recall-then-walk when faster by 6 rounds; team endgame when banked + all bags >= 1000.
  - Shared memory (`comms.h:9-25`): byte0-3 squad targets, bytes4-6 enemy sighting (x, y, count, tributing flag, round&15), byte7 focus type, home flags, help flag, Jungle flag. Draft memory (1024 B) carries roster, squads, roles, zone thresholds, per-group distances/flags.
  - Opponent-specific: none. Map flags for gate maps (boss battle) only.
- Unique 4.0 content: capture_state use for contesting (`world.cpp:160-180`, `roles.cpp:134-157`), Capture emblem buyer logic (`shop.cpp:64-78, 106-117`), and a GameRules.md that spells out the new items (section 2).

### 1.3 `wanga158-mcmaster/secretcode` (MC): by far the strongest and best-documented. Main bot v53/v55 (platform 55)

- Snapshot of 25-26 Oct, `sdk_version = 3.0.5` (engine 1.0.3). The repo is mostly a population/test farm (194 extended-suite bots, `arena` tooling, native fast runner) plus `bots/main` (the submission) and 30+ frozen anchors `main-v18..v55`. Its docs say the 4.0.0 bundle is staged but production was still on 3.0.5, so **no 4.0 item or capture-emblem play exists in its bots**.
- Evidence (own): ladder #36, 1988.9 on 25 Oct 20:08 UTC (#1 2365.9); v44 was #52. v44 win rate by opponent rank band: 9% vs 1-10, 30% vs 11-30, 43% vs 31-60, 66% vs 61-150, 96% beyond. v53 22% vs ranks 1-30 (1,499 games). Local: v53 beats every local archetype 86-95%. v55 vs v53 head to head 44-36 in the gate and +224/-141 over 4,994 broad keys. For comparison we are around rank 300.
- Their failure modes match ours: vs top-15 they die 4.3 vs 1.5 times by r400, ~13 deaths/game vs top 10; gold 258/395 at r100, 1333/2333 at r400; their gap decomposition (D326): kill gold 39-43%, base capture gold 35-40% (mostly elk), Vesper passive 14-19%, Treasure 3-5%; per farming round top teams are not faster; by r400 65% of the gold gap is dead-champion time. Camp-gold difference at r300 predicts a loss with AUC .82 (D360).
- Strategy of main (`bots/main/main/src`, defaults in `config.h`):
  - Draft (`draft_mode 8`, `config.h:211-217`): Heart of Ruin, Marcella, Ryth, Vendetta, Varg, Vesper, Stellar, Tavi, C&I, Prism, Willow, Ren (3 picks: HoR, Marcella, Ryth). Vesper-led and "meta" drafts were worse on their chassis (-65 of 480 at p .001; online 10 vs 14 of 100).
  - Squads: squad_size 1 (everyone solo-farms, claims in shared memory); pairs, an escorted opening ball and cohesion bonuses all rejected (cohesion -119..-233 wins, crowding).
  - Items: `shop_plan 7`, melee `335 435 225 035 625 630` = Treasure(main) x5, Jungle(main), Durability(H), Monster(main), Bruiser(H), Bruiser(main) forever; ranged `335 435 035 630` (`config.h:484-489`). HoR builds Focus. Plan 14 (health first), Home orders (12/13), value-model shop (plan 100) all tested without a clear win. A learned layer (94 weights over target scores, fight verdict, bank/recall thresholds, draft order, shop order) trained by ES against their own bots is on.
  - Farming: target rate with whole-cycle cost, gem value 1.5 (4.0 on gem-rich maps), 1.35x hysteresis, re-score every 8 rounds, respawn travel, `capture_handoff 1` (one ally holds the capture, others leave: `brain.cpp:2930-2960`), `capture_recall 2` (section 4), `group_news` (shared bytes), watchdog bans for farm/retreat standoffs.
  - Fight/retreat: fight-simulation verdict, `hazard 1` threshold 0.3 (20-feature logistic P(killed within 10 rounds), AUC .87, `hazard_model.h`, `brain.cpp:1640-1690`), calm_farm, "doomed: take a kill first", SOS call to healthy allies. Recall at 50% health when nothing can hit; travel-recall as transport when it saves >= 4 rounds; shop recall at 300 gold if detour <= 20.
  - Bank: tribute at 25 gems (detour 8 tiles), tribute-recall as transport, endgame/race logic.
  - Wards: `ward_mode 4`, drop the ward whenever ready, on a bush if one is within reach (~526 per game; top teams place 65-558).
  - Shared memory: one byte per champion (target + status), 3 tail bytes reused as one of news / sighting / SOS / pack. Draft memory unused beyond roster.
  - Opponent-specific logic: none. They keep personas (hunter7, hx1, "lethal sparring partner") to test against.
- Honest negatives worth knowing (they save us tests): tactics_s fight rewrite 165 -> 83 wins; phantom enemies for unseen allies of a seen enemy 165 -> 103; individual retreat rules rejected ("the lever is to be grouped"); `recall_tail` -46; route lookahead null; opening ball and carrier_capture rejected; Vesper draft and Health-first shop worse online; hazard 0.3 gives +198/-134 locally and **+0.2 +- 1.7 pp online over 700 matched games** (D362). The local gauntlet saturates (99% vs weak opponents), as ours does.

### 1.4 `areeb-coder/botmatchmaker` (AR): a Windows matchmaker/aggregator, not a strong bot

- Packages four older bots from the tungtungsahur/tripytropa lineage (`candidate-bot`, `Ankv21`, `v20`, `v22`, SDK pin 2.1.6, ~2,700 lines each), the Daniel v14 single-bot extract (SDK 4.0.0), a stub `foundry-v16-bot`, plus 420 local outcomes over 70 maps.
- Evidence: candidate-bot 218/420 = 51.9% vs its own three siblings (v20 49.3%); not ladder evidence. Its audit itself calls DP's Daniel line "the strongest external foundation" but notes no license and no matched test. "Nothing was compiled or run" in the package prep.
- Candidate-bot is the only bot here with a written 4.0 shop (`bots/candidate-bot/PATCH_2.0.0_UPGRADE_NOTES.md`, `bot.cpp:1042-1081`), **untested**: tank Jungle(H), Durability(H), Monster(S), Skirmish(S), Collectors(S); fighter Monster, Skirmish, Hunter, Treasure, Collectors; marksman/mage Monster(F), Skirmish(F), Tribute(F), Treasure or Prospector(F), Collectors(F); farmer/capturer (Stellar, Varg) Capture(S) first, then Monster, Prospector, Treasure, Collectors. It also has a "peel" step (stun/damage the enemy that is tributing or recalling; biggest bag x channel left first) which we already have in `bot.cpp` (channel scoring 250).
- Daniel v14 (`bots/CAMBC_Daniel_v14_Single_Bot/src`, 1,134 lines bot + map-profile draft): v8 plus recall 0.29 / duo 0.75 / spawn leave 0.77, carriers recall at 50% with threat memory 30, hidden-attacker response, `max_damage_share 4.03` (accept costly fights because hurt champions walk out of camp reach), siege bodies up to 6, build Monster/Durability/Bruiser (`jungle_first` off), shared-memory claims. `openings.inc` has the top-20 opening table (unused). No 4.0 items, still `capture_turns = 5`.
- Other map-specific code (`lanes_team_b_side`, `swirl_counterdraft_active`, `interlock_map_active`) is the same fingerprint style we are trying to retire.

## 2. Facts in the docs that differ from or add to results/claude/patch-4.0.md

Source: `OM/docs/GameRules.md` (4.0.0 handbook export), `MC/docs/reference/updates/2026-10-25-engine-2.0.0/patch-2.0.0.md` (the actual 2.0.0 patch notes), `MC/docs/rules-notes.md`.

| Topic | patch-4.0.md says | Public docs say | Action |
|---|---|---|---|
| **Skirmish** (marked unknown) | "[guess] nothing visible" | **+5% damage to champions** [doc, patch notes] | No measured effect anywhere; only the magnitude. Expect it only visible in fights |
| **Collectors** (unknown) | "[guess] 1% perhaps per gem/camp" | **+1% bonus damage per unique completed emblem family owned, including Collectors itself**; duplicate copies, other stat variants and shards do not add [doc] | Power and Bruiser count as families. With Jungle, Durability, Monster, Treasure/Home, Bruiser, Power you reach 5-7%. Unclear whether the bonus applies to camps as well as champions ("bonus damage") |
| **Tribute** | "~1 round shorter, exact rule guess" | **33% shorter, rounded up, min 1 turn** [doc]. by my arithmetic 1-2 ticks stay the same (3 ticks is borderline on rounding), 4 -> 3, 5 -> 4, 10 -> 7; your two matched games (33 gems: 3 -> 2 rounds, 51 gems: 5 -> 4) are consistent. Gain is 0-3 turns per bank | Low value for banks <= 30 gems (3 ticks) |
| **Hunter** | flat 50 vs 50% undecidable | **+50 gold per kill, awarded to the killer, before gold-income bonuses** (so Treasure/Vesper multiply it); linked C&I death = one reward [doc] | Confirms flat 50. 2.3 kills/game = ~115 gold |
| **Capture** | "countdown starts at 3, does not stack" | **Team-wide cap**: if any allied capturer holds it, the remaining timer is capped at 3; never increases; **the reduction persists if the holder leaves while another ally keeps capturing**; extra allies without the emblem do not speed it up; leaving the region empty or admitting an enemy **resets progress** [handbook]. Patch note instead says it applies when a holder is present *as the capture begins*. MC flags the two texts as conflicting and unverified | Test mid-capture joining with a probe: matters for handoff (the lowest-ID capturer should be the holder, as OM does) |
| **Prospector** | +25% of cluster rewards | Each capturer who holds it gets 25% of **its own share**, rounded down separately for gold and gems; **only the cluster parts**, not wolves/elk in the same group [doc]. Example in the doc: 20 cluster gold between two allies = 10 each, holder +2 (not +2.5) | With one capturer (handoff) the bonus is not diluted. With two holders rounding costs up to 1 per share |
| **Treasure/Vesper** | Treasure +10% | Gold bonuses **add**: Vesper 33% + Treasure 10% = 43% [doc] | Treasure on Vesper is worth less relative to base |
| **Greed** | 25 shards -> 35 pts | Same [doc]; "counts as 35 shards of the stat" | no change |
| **Champion stats** | "unchanged in header; cannot compare" | Patch notes (the diff): Cassi base Focus 70->100, Issac Str 40->45, Varg Str 40->45, Vesper Str 55->45, Willow Focus 120->140, Ryth Str growth 5->4.5, Stellar Focus growth 7->8.5, Prism HP growth 60->65, Marcella Str growth 5->4.5 and Focus growth 15->14, HoR Str growth 3.5->3 and Focus growth 12->10, Ren stun 0.75x->1.1x Focus, Tavi S2 stun 1.4x->1.6x [doc] | **New to us.** See idea 5 |
| First draft fuel | 100x | "x10" increase; exact `.fuel` headers: first draft turn **10,000,000**, later draft turns 100,000, first play turn 200,000 [MC measurement] | Consistent with 100x |
| Cluster stats | queried range 0? | MC: handbook table says range 0 but queried records show range three, strength 0, for clusters [MC measured] | Irrelevant while strength 0 |
| Recall/spawn | recall 5 | Recall 5 turn-ends, **3 with Home** ("five turn ends become three, rounded up"); arrives at turn start; stay on spawn until that turn ends to heal fully; **buying Health on spawn heals the amount gained** [handbook] | Known |
| Tribute timing | - | Length uses the bag **at start**; completion tributes the **whole current bag**, including gems gained since; captures resolve before channels [handbook] | A 1-tick tribute started with a small bag next to a capturing tile cashes in a bigger bag. Only useful where a group's spawn tile is within 1 tile of an altar: rare, noted not recommended |
| Camp wake | - | A woken group attacks the **nearest champion** until it dies or has no target in range for 2 turns; damage wakes the whole group; sleeping camps keep exact HP indefinitely [handbook, MC probe] | We use this already (sieges) |
| Camps | - | Camp kills destroy a victim's gems; dead champions keep shopping turns; Cassi and Issac die together for one 100-gold reward [handbook] | Known |

Unknown mechanics still open (confirmed unmeasured by MC too): Collectors damage scope (camps vs champions), Capture mid-entry timing, Skirmish actual effect, Prospector rounding in a multi-holder capture, `contested` vs `enemy_capturing` transitions during a joint capture.

Measured effects of Skirmish, Collectors and Tribute: **none exist in any of the four repos.** MC says explicitly "These are handbook rules plus queried magnitudes, not measured income or damage improvements." Their main bots do not buy any of them.

## 3. Cross-cutting findings that match our measured failure modes

- **Deaths**: MC die ~13 per game vs the top 10 (4 vs local opponents) and found no simple retreat rule that helps; what helped locally was an earlier hazard retreat (but neutral online). The one lever they trust is staying grouped. This matches our "scrims v26a/v26b: no gain" history. Expect no easy win from rules about fighting; economy and carrier-risk rules look cheaper.
- **Gold gap**: ~40% kill gold, ~35-40% capture gold (elk), 14-19% Vesper passive. Time dead explains 65% of the base gap by r400. MC found farming rate per round roughly equal early, so "farm more camps" alone is not the lever; "do not die" and "elk first in parties of 3-5" are.
- **Banks/submit ratio**: MC bank at 25 gems with tribute-as-transport; DP Daniel tributes at 25 with threat memory; OM uses a P_die formula with free banks near altars. We bank at 20 + altar distance - nearest group (25-60).
- **Capture time**: OM and MC both plan around a single designated capturer per group (handoff) and OM adds one capture emblem for that capturer. We already hand off ("nearest champion captures").

## 4. Ranked ideas we do not use (max 10)

Each has repo/file/lines, what it does, why it should help our measured gaps, a test plan on our benches (sparring set = siege+warlord+marcus 240 games; weak bench = 7 opponents x 80; pools = old 40 maps and new 30 maps; paired games, report wins, deaths/game, gold@r100/r400, submit ratio), and a type. Use paired keys and >= 1,000 games for any claim, since MC found 48-96 game gates cannot detect real gains (SE ~5 pp).

1. **Recall while holding a capture** - *new mechanism (small)*.
   - MC `bots/main/main/src/brain.cpp:3070-3100`, knob docs `config.h:461-472`, ablation in `bots/main/tracks/medium.md` ("removing recall rules costs strength: capture recall -47/480 p .001, shop recall -27 p .049"), result in `DECISIONS.md` D343 (+354/-203 over 3,247 games on all sets, margin +55 gems, 56 rounds faster; unseen maps +81/-55).
   - What: when holding a cleared group's tile with no enemy visible, none unseen, not hit, no camp threat, and `hold_turns >= capture_time - recall_turns + 1`, start `recall()` if (value mode) `shop_recall_benefit(reward) >= 0.3 x walk(spawn -> group)`, or gold after reward >= 90 or HP < 60%. The reward lands at round start, the recall at the next turn start, so the wait buys the trip home. They also publish status "capturing" while recalling so allies do not take the tile.
   - Why: our `shop-recall` needs `capturing<0` (`bot.cpp:1196`), so every shop/heal trip costs a separate 5-round channel plus the walk. Hits "gold 70% of theirs" (earlier items) and "15 deaths" (heal before the next camp) at once. With a capture emblem (3 rounds) hold turns shift; with Home (3 turns) it starts at hold 1.
   - Test: implement as a flag in a copy of v35a. Weak bench + 240 sparring; compare gold@r100/r400, trips per game, deaths. Cheap, expect modest win-rate change but robust gold effect. Guard against recall cancelled by a camp hit on a re-awakened tile (use our `camp_reach`).

2. **Contest enemy captures, walk onto the region** - *new mechanism*.
   - OM `bots/v15/src/roles.cpp:131-157` (`contest_capture`), state reading `world.cpp:160-180`, constants `config.h:56-66` (reward >= 8 gem-equivalents, bag <= 30, HP >= 50%, arrive within timer + 2). Rule text: empty or contested occupancy resets progress.
   - Why: they clear 45% more camps; capture is the choke point (5 rounds stationary, 3 with the emblem). `capture_state()` works from any visible group, even without seeing the capturer. A champion who steps on resets their timer and meets a stationary target. patch-4.0.md rec 3(b) proposed the opposite (drop the target); this is the offensive version. No evidence in OM it works; it is a hypothesis.
   - Test: v35a + rule; sparring (siege/warlord/marcus capture often), measure "enemy captures completed per game" via `camp_group` rewards, our deaths, kills. Reject if deaths rise > 1/game without a gold gain.

3. **Carrier discipline + hidden-attacker response** - *port a rule*.
   - DP `bots/daniel/docs/v7/summary.md` rows 2 and 4; code in AR `bots/CAMBC_Daniel_v14_Single_Bot/src/bot.cpp:1007-1020` (`hidden_response`, `carrier_recall_health 0.5`, `threat_memory 30`), constants `bot.cpp:60-90`.
   - What: if HP fell last turn with no camp or visible enemy in reach, mark danger, raise the leave threshold to the duo value and walk away rather than recall (damage cancels recalls); carrying any gems with an enemy seen in the last 30 rounds: recall below 50% instead of continuing; lower `tribute_gems` to 25 under threat.
   - Why: "45 of 79 ranked deaths with gems came after the carrier was already below 50%; 159 of 496 kills on us came from a bush". We lose gems to killers (79% submit). Our `unsafe_recall` already stops recalls under fire but nothing moves us away from an unseen shooter.
   - Test: the hidden-attacker part is small. Weak bench + sparring; metrics: gems lost on death, submit ratio, deaths with bag > 20. Daniel's own test was 54% vs v7 and 71% vs hunter (base 68%), so expect small.

4. **Shop for 4.0: Collectors/Skirmish/Prospector/Monster instead of Treasure** - *port a rule (shop)*.
   - Facts in section 2. Edit `bot.cpp:343-366`. Candidate A: ranged opener Treasure(S/F) -> Prospector(S/F) or Monster; B: after Jungle(H), Durability(H) and the opener, buy **one** Collectors emblem of the main stat as the first post-core block, then Bruiser; C: Skirmish(main) in place of the first Bruiser block for ranged carries with burst; D: Home(H) for the carrier (recall 5 -> 3). AR candidate-bot lists a similar untested chain (`bot.cpp:1050-1081`); OM buys Capture(H) for one champion per squad (`shop.cpp:106-117`).
   - Why: Collectors with 4-6 families is +4-7% damage on 150 gold, a pure addition vs Bruiser's off-stat points. Treasure is 10% now (also additive with Vesper). The extra damage only helps fights if it applies to champions (unclear), so deaths/kills are the metric.
   - Test: each as a separate shop-only variant (like patch-4.0 section 6): 560 bench + 240 sparring + new-30 pool; claim only at >= +15 over 800 games. Expect a tie like prospector (491 vs 491). Priority is the free swap of Treasure; Collectors needs the damage-scope probe first (buy one, log damage dealt to camp vs champion, 1 game).

5. **Re-check the draft with the 4.0 stat changes** - *port a rule (data)*.
   - Patch notes: `MC/docs/reference/updates/2026-10-25-engine-2.0.0/patch-2.0.0.md`. Biggest moves: Cassi +43% base Focus, Ren stun +47%, Willow +17% Focus, Varg/Issac +12% Str, Vesper -18% Str, Marcella/HoR nerfs.
   - Why: our top-4 comp (HoR, Vesper, Ryth, Marcella, Vendetta) was fixed on 3.0.5 numbers. MC's `draft_pref` (HoR, Marcella, Ryth, Vendetta, Varg, Vesper...) was also set pre-patch.
   - Test: swap one slot at a time in v35a draft on sparring 240 + new pool; report pick-level win delta. Cheap and may matter more than any rule.

6. **Group news through shared memory** - *new mechanism, constrained*.
   - MC `brain.cpp:3692-3720` (`share_news`), `knowledge.cpp:229-260` (`news_out`, `apply_news`), `config.h:455-458`. Three tail bytes: group+1, respawn_round lo, hi. Effects: +131 wins on zero weights (+34 once weights were co-trained), faster to win vs every opponent.
   - Why: our farmers each guess "taken once out of sight for 6 rounds" (`bot.cpp:277-278`), so farmers walk to groups that are dead or not yet respawned. Targets "clear 45% fewer camps".
   - Constraint: all 8 of our bytes are used (`bot.cpp:37`, `787`). Try packing: drop `kFocus` or merge threat cell, or put group id in 6 bits plus (respawn_round / 8) in 8 bits across two bytes.
   - Test: sparring + weak bench with walking-to-dead-group counter (rounds spent travelling to a target that is dead/respawning on arrival) as the diagnostic; expect effect on camp count, not wins.

7. **Top-20 opening table** - *port a rule (data)*.
   - AR `bots/CAMBC_Daniel_v14_Single_Bot/src/openings.inc` (40 old maps, side A and B, first three camp groups of the top 20, indexed by game_map group order; generated by `tools/openings.py`, not in the clone). Not wired in v14 (grep finds no include), so unmeasured.
   - Why: gold@r100 0.5x top teams; first targets matter most. Verify index order against our `groups[]` (ours may sort) and that those maps are byte-identical in 4.0 (patch-4.0.md says the 40 old maps are unchanged).
   - Test: force first target = table entry on the old pool; measure gold@r100 and first capture round vs v35a on sparring and bench. Reject if no gold@r100 gain.

8. **Ranged "covered tile" standing and wolf kiting** - *port a rule*.
   - OM `farm.cpp:1-12` and `487-540` (`covered`, `covered_ranged_tiles`), cost model `cost_of` with `kite` at lines 105-115. Monsters hit the nearest champion; a ranged champion should stand where every monster that can reach it has an ally nearer; spells (range 4) outrange wolves (range 3), so a squad of ranged units takes no damage from wolf-only groups.
   - Why: 3 camp deaths/game (earlier measure) and 24 camp deaths in 6 siege games after the recall fix. We have no such rule (grep finds only camp reach for recall). Wolf-heavy maps (02the-pack, 62 wolves) are on the new pool.
   - Test: 6-map slice with elk/wolf groups, then sparring; metric camp deaths and HP lost per camp.

9. **Hazard model for contact decisions** - *port a rule (refit)*.
   - MC `hazard_model.h` (20 features, weights fitted on their v44 online losses, AUC .87) and `brain.cpp:1640-1690`. Disengage when P(killed in 10 rounds) >= 0.3 for 3 rounds. Do not copy the weights (they describe their bot); refit on our scrim cache (`data/scrim_cache*.json`).
   - Evidence: +198/-134 local, deaths 9.8 -> 7.9, but online matched +0.2 +- 1.7 pp. Low expected value; included because it is the only rule with deaths measured down.
   - Test: refit logistic from our top-4 and mid-rank scrims; then sparring + the 100 paired mid-rank scrim protocol; accept only on deaths and wins both moving.

10. **Free bank near altars and P_die-driven bag size** - *port a rule*.
    - OM `bank.cpp:120-190`: bank any bag within 3 steps, >= 30 within 10 steps, 30 + 1.0 x steps capped at 90, keep farming past 150 only while P_die <= 25%, recall-then-walk when faster by 6 rounds. Our `carry` uses 20 + altar distance - nearest group (25-60) and only `gems >= 20 && ad <= 6` for near altars (`bot.cpp:551-556`).
    - Why: targets the 79% vs 95% submit gap; effect on our bank is probably small because we already bank early (v23m).
    - Test: sparring + weak bench; metric submit/collected, banks/game (we 17 vs their 37).

Not recommended, with evidence: spawn hold (MC `tactics_s` with spawn-exit hold lost 165 -> 83), phantom enemies / pack sightings (-62, -14), cohesion bonus (-119..-233), opening ball (+21..+28 rounds slower, 159 vs 165 wins), Vesper-led draft (-65), Greed filler (ours -13), Hunter (<= ~115 gold per game), Tribute for banks <= 30 gems, Capture emblem as a stand-alone bet (tie on old pool; only OM argues +5-10% throughput, unmeasured).

## 5. Sparring partners in the public repos (not run, per the rules)

- MC `bots/anchors/main-v53 / main-v55`: ladder #36, source on 3.0.5. Would be the strongest public sparring partner by far. Using it needs a decision from you on licensing (no license file seen in the clone) and a 4.0 rebuild; I did neither.
- MC `hunter7`, `hx1`-style personas and `compound-field-growth` are their discriminating opponents; the rest of their 194 bots are ~0% vs v53 and add nothing.
- DP Daniel v8 / Jame v3 are weaker and on 3.0.1; AR Daniel v14 is on SDK 4.0.0 and is a plausible extra opponent, but no strength evidence beyond "was the +200 elo bot".
