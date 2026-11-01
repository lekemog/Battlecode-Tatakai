# #54 mass-death losses: replay study, candidates and mirror results

Date: 1 November 2026. Baseline: v50d (live 222, `bots/v50d`). Engine 2.0.0, cambc 4.0.0.
Candidates: `bots/v50e1` ... `bots/v50e9` (each = v50d plus one change, header line 1 of main.cpp says which).

## Summary

20 of our 37 recent ranked losses (60 games since 2026-10-31T23:22Z) have 10+ deaths and few kills back (losses average 13.0 deaths vs 3.8 in wins; kills 2.4 vs 5.3). Decoding 8 of the worst games shows the deaths are almost all champion-vs-champion (217 of 218 deaths have an enemy champion within 6 tiles one round earlier; one is a camp kill), in groups of 3-4 enemies meeting 1-3 of our champions, often from round 21-37 in the middle of the map. The opponent then converts kill gold into 2-3x our item points by r400 and out-fights us for the rest of the game. Our own fight simulation already predicted more loss for us than for them in 365 of 479 deaths logged by the bot, so the problem is not an over-optimistic "favourable" verdict but contact we cannot leave or avoid.

None of the one-knob candidates tested (earlier hazard disengage, committed homeward retreat, enemy phantoms, local-power tactics, pairs, opening ball) improved on v50d in the self-play mirror; the existing tuning is hard to beat in self-play. The only candidate that passes the gate is v50e1 (Prospector opener), which is an economy change, not a death fix (57.4% of 366 mirror games).

## Facts decoded from replays

Replays: `cambc matches download`, decoded with `tools/replay/extract4.mjs`; deaths labelled by `tools/replay/deaths54.py` (health 10/5/2 rounds before, enemy champions and allies within 6 tiles one round before, awake camps in range, bag, item points of both teams). Our team index 0 = side A.

| match | map | opponent (rank) | side | deaths | first death | lone (no ally within 6) | labels (outnumbered / duel-ish / camp) | items r200 us/them | items r400 us/them |
|---|---|---|---|---|---|---|---|---|---|
| 37bf881a | 00swirl | 84 | A | 26 | r22 | 7 | 11 / 15 / 0 | 4 / 12 | 10 / 29 |
| a897224d | 02stalactites | 94 | A | 28 | r28 | 11 | 24 / 4 / 0 | 3 / 11 | 3 / 20 |
| 3d95fd45 | 02arena | 74 | A | 36 | r118 | 17 | 17 / 19 / 0 | 6 / 8 | 11 / 15 |
| 2db1fc60 | 00crater | 74 | A | 26 | r37 | 4 | 12 / 14 / 0 | 4 / 8 | 6 / 16 |
| f18145d8 | 00swirl | 72 | B | 27 | r21 | 8 | 7 / 20 / 0 | 4 / 11 | 9 / 30 |
| 3136e6ac | 00quarry | 94 | A | 36 | r158 | 19 | 12 / 24 / 0 | 11 / 6 | 12 / 14 |
| da77b062 | 02crossing | 77 | A | 20 | r168 | 6 | 9 / 11 / 0 | 9 / 8 | 9 / 16 |
| e5e7b7ff | 02treasure_box | 72 | B | 19 | r130 | 7 | 2 / 16 / 1 | 9 / 17 | 18 / 34 |
| total | | | | 218 | | 79 | 94 / 123 / 1 | | |

(outnumbered: enemy champions within 6 > our allies within 6 + 1; duel-ish: equal numbers or one more; 65 deaths had >= 70% health three rounds earlier, i.e. died in under 3 rounds.)

- Opening contact: in 00swirl (both games), 02stalactites and 00crater the first deaths come at r21-37 at the middle of the map (e.g. r22 at (23,16): 4 enemy champions, three of ours with one ally, 3 camps awake). The opposing team moves as a pack to the central groups; our champions go to their individually best targets and meet it piecemeal.
- Cohesion (mean pairwise distance, r20-200): 00swirl 4.9 vs 4.9, 02stalactites 9.2 vs 7.5, 02arena 8.0 vs 5.2, 00crater 18.1 vs 8.1, 00quarry 11.8 vs 11.6: we are looser than the opponent in 5 of 8 games, equal in 2.
- Snowball: kill gold funds items; their item points are 1.5-3x ours at r400 in 7 of 8 games (00quarry shows the reverse early, 11 vs 6, and still loses 36 deaths later).
- Camp deaths are negligible (1 of 218): this is not a camp-fight-planning problem.
- Bot-side log (stdout `death` lines, 479 deaths in the 37 losses): mode at death is PvP in 80%, our simulated loss exceeded theirs in 365, equal in 86, smaller in 28.

## Code path

`handle_threats` (PvP) runs first in `Brain::turn`: builds the fight simulation (`sim_*`), applies `fight_margin` / `behind_fight_margin`, and when the verdict is a loss calls `retreat` (safety field / home), which relies on being faster or out of reach. `cfg::hazard` (threshold 0.3) disengages at contact from a learned death-hazard model; `cfg::retreat_mode 0` keeps the local retreat. With enemies in a pack and no ally near (59% of deaths), retreat usually fails because the walking speed is equal and ranged enemies keep hitting.

## Local reproduction

The sparring and weak benches cannot reproduce it (v50a scores 235/240 there; those opponents do not hunt). The only local PvP-strong opponent is the bot itself, so the paired mirror v50eN vs v50d is used as a check of the isolated change (70 maps x both sides = 140 deterministic games; self-copy mirror is exactly 70-70):

Trace build: `bots/v50*scan` style builds (scratch, not committed) print one `T` line per 10 rounds per champion without changing play; the bot's own `death` log line already prints the last 10 turns (round offset, health, mode/why, enemies, nearest enemy distance, allies near, simulated losses).

## Isolated candidates (all on v50d, one flag each) and mirror results

| candidate | change | wins / 140 (share of decided) | mean gem margin | map 0-2 count | verdict |
|---|---|---|---|---|---|
| v50e4 | `hazard_threshold` 0.3 -> 0.15 | 50-90 (35.7%) | -123 | many | fail |
| v50e5 | `squad_size` 2 (farm in pairs) | 76-64 (54.3%) | +20 | | below gate |
| v50e6 | `retreat_mode` 2 (committed homeward retreat) | 50-90 (35.7%) | -213 | | fail |
| v50e7 | `phantom_mode` 1 (unseen enemies join the sim) | 35-105 (25.0%) | -239 | | fail |
| v50e8 | `tactics_s` 1 (local-power tactics) | 11-129 (7.9%) | -579 | | fail |
| v50e9 | opening ball (`squad_size` 9, `escort_until` 150) | 46-94 (32.9%) | -232 | | fail |
| v50e1 | Prospector emblem replaces Treasure as opener (patch 4.0) | 81-59 (57.9%) | +59 | 9 | passes |
| v50e2 | Capture emblem after Monster + 3-round capture timing | 58-82 (41.4%) | -77 | | fail |
| v50e3 | `capture_state()` drops groups an enemy is capturing | 59-81 (42.1%) | -58 | | fail |
| reference | v50d vs v50a | 79-61 (56.4%) | +25 | | |
| reference | v50d vs identical copy | 70-70 (50.0%) | 0 | 0 | |

v50e1 on 226 further games (rotated/flipped copies of the 26 square maps, `tools/replay/mapxform45.mjs`): 129-97 (57.1%, gem margin +67). Together 210-156 (57.4% of 366, one-sided p about 0.003).
With 2 games per map the "no map -3" rule cannot trigger; maps lost 0-2 by v50e1: 02treasure-box, 02guardians, 02stalactites, 00packs, 00lanes, 00gem-fields, 00rushbait-v2, 00dunes, 02gift-wrapping.

Reading: every knob that changes fight/retreat behaviour loses to v50d in self-play, because self-play rewards whoever fights better *given identical gear*, and the tuned defaults were fitted there. Self-play cannot measure the real failure, which is facing a pack with kill-gold snowball. Death-avoidance ideas need either a stronger local opponent (a pack-moving, early-contact bot) or the pinned panel.

## Scope scan

37 real losses classified: 20 mass deaths, 10 slow races (#55), 7 low banking / gold deficit. Deaths at r<100 in 12 of the 37 games' first deaths (r21-r97).

## Still to do

- Build a local "early pack" opponent (all champions move together to the central groups from r1) to reproduce the r21-37 contacts; test: (1) lone champion keeps away from known enemy reach in the opening, (2) first target of each champion chosen within N tiles of an ally for the first 60 rounds only (the opening ball tried to hold the team until r150 and lost 33%), (3) earlier recall/dash when the sim predicts loss and the champion is not cornered.
- Pinned panel on v50e1 (v50d baseline).
- Weak bench check for v50e1 (done): old 40 maps 559/560 (v50d 560/560), new 30 maps 418/420 (v50d 415/420); no regression.

## Local early-pack opponent (v50p1) and death-avoidance candidates

Base for everything below is `bots/v50e1` (live 223). Opponent: `bots/v50p1` = v50e1 + `hunt_mode 1` + `fight_margin 0` (test harness only; variants `v50p2` ball, `v50p3` pairs, `v50p4` no hazard / margins 0 and 0.3).

### What the real opponents do early (8 decoded replays)

- Both teams head for the map centre together: the opposing pack (3-6 champions) has mean pairwise distance 1-4 from r5 and is within 0-5 tiles of the centre group by r15 (00swirl: centre (22,15), their distances to it at r15: 3,5,2,1; ours 2,2,7,3).
- First contact is at the centre at r15-35 with 3-4 of them against 1-3 of ours, first deaths r21-37 in 4 of 8 games (00swirl x2, 02stalactites, 00crater) and r118-168 in the others.
- Cohesion r20-200 (us/them): 4.9/4.9, 9.2/7.5, 8.0/5.2, 18.1/8.1, 5.4/9.0, 11.8/11.6, 12.6/8.4, 9.4/6.3: they are tighter in 5 of 8.
- Fights are won by numbers at the point of contact; the kill gold then buys items (1.5-3x ours at r400).

### Validation of v50p1 (v50e1 playing against it, 140 games = 70 maps x both sides)

| metric | real losses (37 games / 8 decoded) | v50e1 vs v50p1 | v50e1 vs v50d (self) |
|---|---|---|---|
| deaths per game of the bot under test | 13.0 | 8.5 | 5.5 |
| first death <= r80 | 12 of 35 games (34%) | 55 of 140 (39%) | 39 of 140 (28%) |
| first death median | about r117 | r112 | r125 |
| deaths outnumbered (enemy champions > allies + 1) | 43% | 36% (110 deaths, 8 decoded games) | |
| deaths with no ally within 6 | 36% | 55% | |
| median first death, 8 decoded games | r84 | r85 | |

v50p1 reproduces the timing and the champion-vs-champion nature of the real deaths but not their depth (13 vs 8.5 deaths) and it is weaker than the real teams overall (v50e1 beats it 63.6%; the real teams beat us 62%), because it has no better economy or fight code than we do. It is a valid *stress test for avoidance rules*, not a replacement for the panel.

### Candidates vs v50p1 (win share of the candidate, 70 maps x 2 sides; baseline v50e1 63.6%)

| candidate (on v50e1) | change | vs v50p1 win share | deaths/game | first death median | <= r80 | plain mirror vs v50e1 |
|---|---|---|---|---|---|---|
| v50e1 (baseline) | | 63.6% | 8.5 | 112 | 39% | |
| v50q1 | hazard_threshold 0.15 | 56.4% | 6.5 | 130 | 34% | 47.1% (66-74) |
| v50q2 | retreat_mode 2 | 60.7% | 7.2 | 114 | 34% | 32.9% |
| v50q3 | squad_size 2 (pairs) | 60.0% | 8.3 | 109 | 34% | 42.9% |
| v50q4 | fight_margin 1.0 | 60.7% | 8.7 | 98 | 41% | 47.9% |
| v50q5 | sim_ally_contact 3 (allies join the fight simulation only when in contact) | **67.1%** | **6.8** | 132 | 32% | 51.4% |
| v50q6 | standoff_recall_turns 3 | 57.9% | 8.8 | 105 | 40% | 47.9% |

Only v50q5 is above the baseline. Rotated/flipped copies (226 games): v50q5 65.0% vs v50p1 (v50e1 62.4%), deaths 7.5 (v50e1 9.5), plain mirror vs v50e1 54.9% (124-102, gem margin +57). Over 366 games q5 scores 65.8% vs 62.8% for v50e1 against v50p1 (+3.0 points, below the +8 gate) with 20% fewer deaths, and 53.6% in the plain mirror. It is a candidate for the panel only if the panel slot is cheap; the evidence is deaths down, win share about flat. No candidate meets the "+8 points vs v50p1" rule.

New designs from the replays that are NOT yet built (need code, not flags): avoid the contested centre group for the first ~100 rounds when the opening enemy pack is expected to be there (route first targets to the nearest non-central group); flee when 2+ enemy champions are within 6 and no ally within 7 (a rule on the existing sim verdict); take the first centre target as a pair with the nearest ally.

### Hazard history port: `bots/v50e1h` (fresh implementation of the stale-sample fix)

Change: the hazard model's 4-slot health ring keeps the round of each sample and ignores a slot that is not from `round - 3`; the history and the committed-disengage deadline are cleared while the champion is dead (the deadline used to be a function-local static that also survived a death). `cfg::hazard 0` removes both.

| test | result |
|---|---|
| mirror vs v50e1, 70 maps x 2 sides (140 games) | 70-70, gem margin +4 |
| mirror vs v50e1 on rotated copies (226 games) | 113-113, gem margin +6; net wins 0 on every map |
| bot faults / engine error codes in 366 games | 0 / none |

Neutral in self-play (identical results in almost every game, as expected for a rare path), so it is safe to ship together with the next real change.

## Next ideas: quick coordinate search over learned weights

`learn::params` holds 94 weights (blocks: group 0-15, fight 16-31, bank 32-43, recall 44-55, draft 56-67, shop 68-79, spawn 80-87, group2 88-93). The shop block is applied in `learned_plan` as `shop_weight(family) + shop_weight(7 + stat) - plan_position` (a stable sort of the plan by that score). Current shop weights (family 0-6 = monster, power, durability, treasure, jungle, home, bruiser; 7-9 = strength, focus, health): -2.44, -0.86, -0.03, **+2.38**, -2.00, **+1.57**, +0.84, -4.07, -3.69, -2.15. They were fitted when Treasure paid 20%:

- Treasure (index 3, +2.38) keeps the opener in front of Jungle (-2.00); v50e1's Prospector step inherits this weight (`Step::wf = 3`).
- Home (index 5, +1.57) is not in the fixed plan but is appended by `learned_plan` as a 5-shard step, so it is bought early; with Monster at -2.44 and Jungle at -2.00 the learned order may differ from the plan 7 order.
- Group block features 9-15 (log gems, log gold, territory, jackpot, harmless, log health, altar distance) weigh gold against gems: gold features were fitted with Treasure at 20% and no Prospector.

Proposed sweep (no code yet): coordinate search over about 8 weights (shop 0, 3, 4, 5, 6; group 9, 10; bank threshold weight 32), each +-25% (16 candidates), evaluated as a paired mirror vs v50e1.

- Candidates need no compilation: the built `bot.wasm` carries the weights in a labelled data block (`magic` field of `learn::Params`, volatile floats); a script copies the wasm, finds the magic, writes the 94 floats and registers the bot folder (the local runner of the training tools does the same). If a rebuild is used instead, an incremental build of one file takes about 10 s.
- Cost per candidate: one 140-game mirror = about 2.0-2.5 minutes on the 4 cores (measured: 9 mirrors of 140 games ran at 1.6-2.6 min each); with the 226 rotated-copy games added, 366 games = about 5.5 minutes. A sweep of 16 candidates on 366 games = about 90 minutes (140 games only: 40 minutes); a second pass with only the 4 best on 366 fresh games adds 25 minutes. Statistical resolution: sd of the win share is about 4 points at 140 games and 2.6 at 366, so a weight change must move the mirror by 5+ points to be selected; smaller gains need the panel.
- Evaluate each candidate also vs v50p1 (another 5.5 minutes per candidate) only for weights touching fights or banking.
