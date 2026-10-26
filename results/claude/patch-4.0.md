# Patch 4.0.0 (cambc 3.0.5 -> 4.0.0): what changed, what the new items do, what to change in our bot

Date: 2026-10-26. Everything below was measured locally with `cambc 4.0.0` (SDK at `sdk_version = "4.0.0"`). No patch notes were available offline, so item effects are inferred from `item_type::info()` plus instrumented games (probe bots). Confidence is flagged per line: **[confirmed]** = seen in game logs, **[inferred]** = consistent with data but not isolated, **[guess]** = name/magnitude only.

## 1. What changed (diffs of the SDK, maps, tests)

Compared `sdk/` of a fresh 4.0.0 project with our 3.0.5 `sdk/` (C++, Rust, OCaml, Python all carry the same changes), plus `maps/`.

| Area | Change |
|---|---|
| Items | 7 new item families (tribute, capture, prospector, hunter, skirmish, greed, collectors): 14 families x 3 stats x (shard, emblem) = **84 item types** (was 42). `item_passive` gains tribute, capture, prospector, hunter, skirmish, collectors (greed has no passive). New `item_family`, `item_stat` enums and `get_item_enum(family, stat, shard=true)`. Item ids are `family*6 + stat*2 + (shard?0:1)`. |
| Existing emblems | Monster emblem camp damage 10% -> **15%**. Treasure emblem gold 20% -> **10%**. All other emblems unchanged (Durability -10% incoming, Jungle -30% camp damage, Home recall 5 -> 3 turns, Power = 6 shards, Bruiser = 5 + 1 + 1). |
| Capture API | New `camp_group.capture_state()` -> `{timer, state}` with state in `no_capture_available, ally_capturing, contested, enemy_capturing, capture_available`. Needs the group visible (not the champions). New ABI import `camp_group_capture_state`. |
| Fuel | First draft turn fuel 10x -> **100x** (champion first turn still 2x). |
| SDK internals (perf) | `item_type::info()` is now cached per item (no host call after the first); `cached_my_champion` / `cached_my_team` replace `sdk_my_champion()` / `sdk_my_team()` host calls in `team()`, `is_draft()`, etc.; `ability.valid_targets()` now reports the immutable design flags (no live query); `ability::can_use` does one champion query instead of a nested lookup. Net: fewer host calls per turn, a little more fuel headroom. |
| Constants | **Unchanged in the headers**; runtime values read by probe on 4.0.0: `capture_time=5, camp_sleep=2, respawn=60, recall=5, submit mult 0.1 (min 1), range 1, max_rounds 2000, winning_gems 1000, kill_gold 100, assist 0, passive 0, spawn_heal 1, wards 1 (cd 10, vis 6, place 2), altar_hits 5, tp_crystal 3`. |
| Champions / camps | Header text and runtime base stats unchanged (probe printed all 13 champions and 6 camp types: e.g. Ryth 1200+100 hp, 45+4.5 str; wolf 1350 hp/20 str, elk 2400/60, cluster 120 hp, monolith 20000/200 range 5, golem 5000/120 range 4). I cannot compare against the old engine's numbers (3.0.5 engine is gone), but the old header docs carry the same numbers. |
| Maps | The 40 old maps are **byte-identical**. 30 new maps (70 total): `00anvil 00breadcrumbs 00crater 00dunes 00galaxy 00oasis 00quarry 00ribs 00the-line 00vault`, `02arena 02crossing 02cuts 02famine 02fields 02geodes 02gift-wrapping 02guardians 02harvest 02stalactites 02tangle 02the-pack 02the-pond 02treasure-box 02uncharted-lands`, `adgato-gemcombat1..5`. |
| Tests / python / rust / ocaml | Only mirror the above (new enums, capture state, 84-slot item array). Nothing else documented. |

### The new maps are economically different from the old pool

Probe (`MAPINFO`, round 1, whole-map totals of camp-group gold/gems; numbers include both mirrored halves, so use ratios):

| | old 40 | new 30 |
|---|---|---|
| mean total group gold | 2130 | **1142** |
| mean total group gems | 500 | 369 |
| mean walls | 157 | 270 |
| mean elk camps | 9.4 | 2.6 |

Notable: `adgato-gemcombat1..5` have **zero gold** (gem clusters only, 126-735 gems on the map total), so nothing but kill gold (100) buys items there, and gold weighting in target choice (`kGoldW`) is irrelevant. `00breadcrumbs` has 34 tiny groups (240 gold, 154 gems, no walls). `00galaxy` (93x93, 160 gold total) and `00vault` (359 gems, 49 gem clusters) are gem-starved/gem-rich extremes. Several `02*` maps are very gold-rich (`02the-pack` 3480 gold with 62 wolves, `02treasure-box` 3070, `02gift-wrapping` 3020, `02cuts` 2840 gold and 908 gems). Per-map details: `scratchpad/mapinfo.txt` equivalents are reproducible with the `mapinfo` probe (see section 6).

## 2. Item table (measured with `item_type::info()` on 4.0.0, effects measured in games)

All shards cost 30 gold and give 1 point of the named stat (1 point = the champion's growth in that stat). Emblems cannot be bought, only combined. `combine` is the shard count. "pts" = stat points of the emblem (the emblem's `health/strength/focus_points`).

| Family | Shards -> emblem | Emblem pts | `passive_magnitude` | Effect |
|---|---|---|---|---|
| monster | 5 -> 150g | 5 main | 0.15 | +15% damage to camps (doc) |
| power | 5 -> 150g | 6 main | - | no passive; 6 pts for 5 shards |
| durability | 5 -> 150g | 5 main | 0.10 | -10% incoming damage (doc) |
| treasure | 5 -> 150g | 5 main | 0.10 | +10% gold gained. **[confirmed]**: gold from clusters 60 -> 66, 80 -> 88 |
| jungle | 5 -> 150g | 5 main | 0.30 | -30% damage from camps (doc) |
| home | 5 -> 150g | 5 main | 0.50 | recall 5 -> 3 turns (doc) |
| bruiser | 5 -> 150g | 5 main + 1 + 1 off-stats | - | 7 pts for 5 shards |
| **tribute** | 5 -> 150g | 5 main | 0.33 | **[inferred]** gem submission (tribute channel) about 1 round shorter. In two matched games a 33-gem tribute took 2 rounds vs 3 without; a 51-gem tribute 4 vs 5. Does not change gems credited and does not add gold. No visible stacking. Exact rule (-33% duration?) **[guess]** |
| **capture** | 5 -> 150g | 5 main | 3 | **[confirmed]** capturing a cleared camp group takes **3 rounds instead of 5**. Seen in `capture_state().timer`: with a capture emblem the countdown starts at 3 (3,2,1) instead of 5. Does not stack (still 3 with 7 emblems). Magnitude = capture time. |
| **prospector** | 5 -> 150g | 5 main | 0.25 | **[confirmed]** +25% of the **cluster** camps' rewards: gold clusters pay 20 -> 25 gold each (group of 3: 60 -> 75, group of 4: 80 -> 100, Vesper then 100 -> 133); gem clusters ~7 -> ~9 gems (group with 3 gem clusters: 51 -> 56 gems). Wolf/elk/golem/monolith drops (e.g. the 180-gold part of a mixed group) are not boosted. Does **not** raise the 100 kill gold. |
| **hunter** | 5 -> 150g | 5 main | 50 | **[inferred]** +50 gold on kills (kill reward 100 -> 150 in the matched logs; flat 50 vs 50% cannot be told apart at kill_gold 100). Our bots get ~13-15 kills per game, so at most ~700 gold per game spread over the team. |
| **skirmish** | 5 -> 150g | 5 main | 0.05 | **[guess]** nothing visible in gold/gems/stats. Probably +5% damage or similar in fights vs champions. Not isolated. |
| **greed** | **25 -> 750g** | **35 main** | - | no passive (not in `item_passive`), pure stats: 35 pts for 25 shards (+40% on completion). Per gold: 21.4 g/pt, vs shard 30, Power 25, Bruiser 21.4 (but Bruiser's off-stat points are worth less than main-stat points). |
| **collectors** | 5 -> 150g | 5 main | 0.01 | **[guess]** nothing visible: strength/gold/gems/submit unchanged while carrying 51 gems. Perhaps a per-gem or per-camp stackable bonus of 1%. Treat as unknown. |

Rewards for reference (from `camp_groups()` at round 1 on `00ambush`): gold-cluster camps pay ~20 gold each; gem-cluster camps ~7 gems each; mixed groups 150-200 gold / 33-51 gems; `kill_gold=100` is paid per credited kill.

## 3. Capture mechanic (what the API and the logs show)

- Capture itself is **not new**. The old SDK already had `constants::capture_time` (5) and `camp_group_reward_available`. What is new is the telemetry and the capture item.
- Measured lifecycle (`v27o` instrumented, every state change printed): when the last camp of a group dies the group becomes `capture_available` (timer = 5, the configured maximum). When one of our champions stands to capture it, the state goes `ally_capturing` and the timer counts **5,4,3,2,1** (one step per round), after which the reward is paid and the group is in respawn (`camp_group_respawning`, 50-60 rounds). Outside capture the timer reads the maximum.
- `contested` and `enemy_capturing` exist (both teams present / only the enemy capturing) but never occurred in my instrumented games, so what interrupts or resets a contested capture is **[guess]**: presumably the timer pauses/resets when both teams are inside, and the enemy can steal the reward by finishing first. The state is readable for any visible group, even when champions are hidden, which gives a cheap way to see "enemy is capturing that group" without seeing the capturer.
- Practical reading for the bot: `capture_state()` lets us (a) know exactly how many rounds are left (replace the guess `constants::capture_time` in the farming cost formulas, lines ~833-997 of v27o `bot.cpp`), (b) see the enemy capturing a group we are walking to and divert, (c) with a capture emblem the cost is 3, not 5, so `constants::capture_time` over-estimates the cycle by 2 for emblem holders.
- Value of the capture emblem: a champion captures ~14-21 groups per 1100 rounds on `00ambush`; saving 2 rounds each is roughly 3-4% of that champion's time. Small but free; best on cluster-heavy maps where the cycle is short (a pure cluster group has no fight, so the 5 capture rounds are a large part of its cycle).

## 4. Baseline on 4.0.0 (old 40-map pool, 7 opponents, 560 games)

Run with the usual `gauntlet.py` (JOBS=4, two gauntlets in parallel; all 80 games completed per opponent). Opponents were rebuilt on 4.0.0 too.

| Opponent | v25u 3.0.5 | v25u 4.0.0 | v27o 3.0.5 | v27o 4.0.0 |
|---|---|---|---|---|
| x_daniel8 | 65 | 57 | 58 | 58 |
| x_de41h4 | 69 | 66 | 75 | 68 |
| h_mohnish | 66 | 64 | 66 | 62 |
| h_deysag | 68 | 66 | 73 | 65 |
| h_vatsal | 80 | 80 | 80 | 80 |
| h_photon | 80 | 80 | 77 | 79 |
| h_apex | 80 | 79 | 79 | 79 |
| **Total /560** | **508** | **492** | **508** | **491** |
| margin | +4405 | +4127 | +4464 | +4000 |

Both bots compile on 4.0.0 with **no errors or new warnings from our code** (the old API is source compatible: only additions). They lose about 16-17 games, concentrated against the four tuning/strong opponents (daniel8, de41h4, mohnish, deysag). Games are chaotic (only 1 of 380 compared game outcomes+scores were identical to the old run), so +-5 per opponent is noise-sized, but the drop is in the same direction on 10 of the 14 rows, and the changed numbers (treasure halved, monster +50%) hit both our openers. Treat it as a real ~3% drop from the patch, not a bot problem.

## 5. Which of our assumptions are affected

1. **Treasure opener for ranged carries** (`order={ranged?T:M, JH2, D}`, comment "+20% gold"): treasure is now +10%. Its value halved. Replace.
2. **Monster opener for melee**: +15% camp damage now (was 10%). Slightly better than before; `M` is the safest opener on 4.0.0 for everyone.
3. **`kGoldW=0.10`** (gold weighting in target choice): gold still buys stats, but on the 30 new maps total gold is about half and on `adgato-gemcombat*` it is zero; and prospector makes cluster gold worth +25% to a holder. No change needed for the old pool; the weighting should be map-aware (see recommendations).
4. **`constants::capture_time` (5) in all `cost`/`score` formulas**: wrong by 2 for capture-emblem holders; and the new `capture_state()` makes the first-turn guess `g.reward` / `seen_round + 6` heuristics replaceable by the real state.
5. **Post-emblem filler = Bruiser shards** (`extra`): greed (35 pts per 750g, single stat) gives more main-stat per gold than bruiser, see experiment below.
6. **Item arrays sized 42**: none in our code (`item_count()` is an `enum_map`); compiled fine.
7. **First draft turn has 100x fuel**: the draft heavy computation (per-map draft tables) can now be done on the first draft turn; no code change needed.
8. Games vs h_* opponents and ladder opponents will shift as they adopt new items (hunter/capture/prospector openers are likely to appear on the ladder within days; check scrim replays for `item_passive` 6..11).

EXPERIMENT_SECTION

## 7. Reproducing

- Scratch project: `S/proj` now has the 4.0.0 `sdk/`, `cmake/`, `cambc.toml`; the old SDK is kept as `S/proj_sdk_3.0.5_old`; the 70-map set is in `S/proj/maps_new` (the bench pool `S/proj/maps` is still the old 40).
- Probe bots (not committed, in `S/proj/bots`): `ptab` (prints constants, all 84 items, champion and camp stats, camp groups), `mapinfo` (prints per-map camp totals), `x4_<family>` (v27o with every emblem replaced by one family, logs gold/gem/strength deltas and capture timers). Logs are in the replay zip (`team-a.stdout`): `cambc run ... -o dir`, then `unzip -p dir/*.repl26a team-a.stdout`.
