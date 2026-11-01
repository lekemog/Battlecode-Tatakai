# #56 — early gold deficit and 0-5 records against ha²t, Gamblr, Valenki and Kratos

Date: 1 November 2026. Baseline: v50d (live version 222). Ladder engine 2.0.0, cambc 4.0.0.

## Summary

- The early gold deficit is real but it is **specific to these four opponents**. Over all 60 ranked games since v222 our gold at r200 is 601 against 615 for the opponent. In the 40 games against other teams it is 659 against 597 (we lead). In the 20 games against the four it is 484 against 650.
- Against everyone else these four average 8.8 to 9.7 pick-ups by r200 and we average 9.2, so the camp economy is level. In the 20 games against the four we make 8.7 pick-ups by r200 against their 10.2. The difference comes from **champion deaths in the first 150 rounds**: the pick-ups we miss while a champion is dead (about 60 rounds plus the walk back), the 50-110 gold a kill pays the other side, and the bag we lose.
- In the 20 decoded games our champions die 70 times before r300, theirs 28 times. Our first death comes before theirs in 15 of 20 games (median r93, theirs r166).
- Those deaths are collapses on a champion that is away from its team: **57% of our early deaths are against two or more enemies than we have allies nearby (theirs 7%), and 43% happen with no ally within 7 tiles (theirs 21%)**. In rounds 30-200 our champions stand more than 7 tiles from their nearest ally 38% of the time (opponents 26%; against Gamblr and Valenki 44% against 15%).
- Items and draft are not the first-order cause. We buy earlier and more than three of the four (median first purchase r52 against r67; 13.8 items by r200 against 11.3). Gamblr, Valenki and Kratos draft Vesper Vale and Vendetta with Heart of Ruin and Cassi & Issac; ha²t drafts exactly our order.
- Fourteen isolated candidates (v50h1 to v50h13 copied from v50d, v50h14 from v50e1, one change each) were run against their base in paired mirror games (70 maps, both sides). None passes 55%; the mirror cannot judge them (see below). Proposed for the strong panel: v50h13/v50h14 (opening cohesion), v50h5 and v50h2.
- Pinning: `cambc match-groups create <team id> --source-group <group id>` can pin all four teams (details below). I did not run it.

## Facts

### Data

| Set | Size | Source |
|---|---|---|
| Our games against the four since 23:30 on 31 Oct (incl. 20 ranked since v222 went live) | 30 matches summarised, 20 decoded | `cambc matches list --team me`, `matches summary`, `matches download` + `extract4.mjs` |
| Each of the four against everyone (most recent 100 finished matches each) | 410 matches summarised in total | `cambc matches list --team <id>`, `matches summary` |

Team ids: ha²t `34b36bab-66bb-4506-b032-2df6a081758d`, Gamblr `f583fbd0-8720-484e-b00c-61159d393c7f`, Valenki `975c2c15-506b-489b-a439-839c8145933b`, KratosMessi `6599a236-7801-436f-a863-4acbb6aafa91`, us (Tatakai) `9c16b699-cad2-453e-8042-dae23ff934d8`. `--team Gamblr` is ambiguous by name; use the id.

The summary JSON (`cambc matches summary <full id> --json -o s.json`, one second per match, needs the full match UUID) carries `buyItem`, `buyConsumable`, `campClear`, `gemCollection`, `gemSubmission`, `kill`, `death` events with round and tile, and per-champion `earnedGold`. The decoded replay (`extract4.mjs`) adds every champion's tile and health each round. Scripts are in `scripts/`, outputs in `out/`.

Two things learned about the data:
- Gold comes from camp pick-ups (a fixed amount per group, 40 to 297), from kills (about 110 including the 50 bounty) and from banking (a few gold per deposit). On the `adgato_gemcombat` maps camps pay nearly no gold, so early gold there is almost entirely kills.
- A dead champion is out for about 60 rounds (`respawnTimer` 59-60 at r111-127) plus the walk back.

### The four teams against everyone (their last 100 games, our 30 for comparison)

| Team | games | win | gold r100 / r200 / r300 | pick-ups r100 / r200 | kills by r300 | deaths by r300 | first purchase round | first deposit |
|---|---|---|---|---|---|---|---|---|
| ha²t | 105 | 67 | 274 / 693 / 1142 | 4.2 / 9.7 | 1.4 | 1.7 | 59 | 116 |
| Gamblr | 100 | 54 | 326 / 760 / 1238 | 4.3 / 9.3 | 1.4 | 2.5 | 68 | 107 |
| Valenki | 105 | 64 | 285 / 648 / 1056 | 4.2 / 9.3 | 1.8 | 1.7 | 75 | 92 |
| KratosMessi | 105 | 49 | 275 / 612 / 976 | 4.2 / 8.8 | 1.7 | 2.0 | 61 | 101 |
| us (30 games vs the four) | 30 | 8 | 243 / 539 / 884 | 4.4 / 9.2 | 0.7 | 3.1 | 41 | 94 |

Our 5-game blocks against each team (all ranked, all lost except Valenki and Kratos earlier blocks):

| | our gold r100 / r200 / r300 | theirs | our pick-ups r100 / r200 | theirs | our deaths by r150 / r300 | theirs |
|---|---|---|---|---|---|---|
| vs ha²t (0-5) | 153 / 372 / 587 | 224 / 602 / 964 | 5.2 / 10.6 | 6.6 / 13.4 | 1.4 / 3.0 | 0.2 / 1.0 |
| vs Gamblr (0-5) | 322 / 680 / 1197 | 383 / 854 / 1396 | 5.0 / 11.2 | 5.0 / 11.8 | 0.8 / 2.8 | 0.2 / 1.8 |
| vs Valenki (10 games, 5-5) | 226 / 552 / 990 | 278 / 655 / 1101 | 3.7 / 8.3 | 4.0 / 8.9 | 0.9 / 2.2 | 0.5 / 1.1 |
| vs Kratos (10 games, 3-7) | 266 / 539 / 768 | 233 / 541 / 1010 | 4.5 / 8.5 | 3.6 / 7.3 | 1.4 / 4.1 | 0.8 / 1.1 |

(Counts are means per game, from `out/gold_by_team.txt`.) Against ha²t the pick-up count is already behind at r100; against everyone else it is level and the gap is kills and deaths.

### The 20 decoded games, one row each (`out/pergame.md`)

See `out/pergame.md`. Highlights:
- In 7 of the 20 games we lose champions before r300 and they lose none: crater 7-0, elkring 5-0, gemcombat5 (Kratos) 4-0, gemcombat1 3-0, starvation 2-0, arena 2-0, anvil 2-0. Stalactites is 9-1.
- The first fight decided the game in most of them. On `00collision` against ha²t both sides made the same first five camp pick-ups (r9, r20/21, r26, r33/34, r47/48). The two Ryths then met on the centre tile at r59: theirs lost 202 health, ours 1,200 and died at r68. No later camp matches.

### Opponent openings (from the summaries)

| Team | draft (first three of five) | first purchase | items bought by r200 per game | camp-clear pace |
|---|---|---|---|---|
| ha²t | Heart, Ryth, Marcella (all 400 matches; fourth and fifth Vendetta, Varg) | Altar Lock then Treasure shards (73 of 105) | 12.6 Treasure, 3.8 Durability, 3.2 Altar Lock, 1.7 Bruiser | 4.1 clears by r100, 8.9 by r200 |
| Gamblr | Marcella or Vesper first, Vendetta, Heart; Cassi & Issac and Willow after | Capture shard (70 of 100); Jungle, Monster shards | 2.1 Capture, 1.6 Jungle, 0.8 Treasure, 0.7 Monster, 0.4 Prospector | 3.9 / 8.0 |
| Valenki | Vesper, Vendetta, Heart (90 of 105); Cassi & Issac, Marcella | Treasure 47, Jungle 41 | 8.1 Treasure, 4.1 Jungle, 1.5 Prospector, 1.4 Bruiser | 4.1 / 8.6 |
| Kratos | Marcella, Heart, Vendetta (71 of 105); Vesper, Vendetta, Heart (20); Marcella, Heart, Vesper (14) | Altar Lock (81 of 105) | 2.7 Jungle, 2.1 Treasure, 2.0 Altar Lock, 1.3 Teleport Crystal | 3.9 / 7.5 |
| us (v50d) | Heart, Ryth, Marcella, Vendetta, Varg | Altar Lock then Treasure | 10.5 Treasure, 3.6 Durability, 2.9 Altar Lock | 4.7 / 9.3 |

Observations: Gamblr, Valenki and Kratos spend little early (2 to 8 items by r200). Gold per pick-up by r300 (earned gold minus 110 per kill, divided by pick-ups): ha²t 74, Gamblr 81, Valenki 62, Kratos 43, us 64; so richer groups explain at most part of the ha²t and Gamblr lead. ha²t's economy profile equals ours; its edge against us is fights, not purchases.

### Fights: where, when, against whom (from `out/early_deaths.txt`)

| Before r300, 20 games | our deaths | their deaths |
|---|---|---|
| count | 70 | 28 |
| no ally within 7 tiles | 43% | 21% |
| two or more enemies within 7 tiles | 83% | 39% |
| outnumbered by two or more | 57% | 7% |
| on or before r100 | 16 | 8 |
| by champion | Ryth 23, Marcella 19, Heart 10, Vendetta 10, Varg 8 | Heart 6, Ryth 4, Marcella 4, Cassi 4, Issac 4, others 6 |

Deaths happen mid-map (mean 17 tiles from the nearer spawn, ours; 14.5 theirs). Enemy champions within 3 tiles of our victims: Heart 28, Vendetta 26, Marcella 18, Ryth 14, Vesper 11, Issac 9. By opponent (our deaths): Kratos 22 (50% alone), Valenki 19 (68% outnumbered), ha²t 15, Gamblr 14.

Cohesion in rounds 30-200 (`out/cohesion.txt`; "alone" = nearest ally more than 7 tiles away): ours 38%, opponents 26%. Per opponent, ours / theirs: Gamblr 0.15/0.11, 0.59/0.29, 0.31/0.18, 0.49/0.07, 0.22/0.11; Valenki 0.41/0.08, 0.65/0.18, 0.22/0.13, 0.24/0.10, 0.52/0.33; ha²t 0.32/0.42, 0.25/0.30, 0.51/0.49, 0.21/0.32, 0.72/0.76 (ha²t is no tighter than we are).

## Comparison with our first 300 rounds (same games)

| (means over the 20 decoded games) | us | opponent |
|---|---|---|
| gold r100 / r200 / r300 | 219 / 484 / 813 | 277 / 650 / 1,104 |
| camp pick-ups by r100 / r200 | 4.1 / 8.7 | 5.0 / 10.2 |
| first purchase (median round) | 52 | 67 |
| items bought by r100 / r200 | 6.2 / 13.8 | 4.0 / 11.3 |
| deaths by r150 / r300 | 1.4 / 3.5 | 0.5 / 1.4 |
| kills by r300 | 0.7 | 3.5 |
| first death (median round) | 93 | 166 |

Group choice is not the difference. Share of each pick-up's distance that lies on our own spawn side (0.5 = halfway): ours 0.34 (r1-100) and 0.36 (r101-200), theirs 0.39 and 0.40. We take groups slightly nearer home than they do.

### First deposits (summaries of the 410 matches)

| Team | first deposit, median round (all their games) | median size | gems banked by r200 (mean) | against us: first deposit / size / banked by r200 | us against them: first deposit / size / banked by r200 |
|---|---|---|---|---|---|
| ha²t | 115 | 22 | 66 | r67 / 7 / 116 | r191 / 29 / 38 |
| Gamblr | 103 | 26 | 51 | r78 / 31 / 59 | r60 / 21 / 109 |
| Valenki | 84 | 22 | 69 | r55 / 19 / 82 | r79 / 15 / 60 |
| Kratos | 101 | 21 | 50 | r111 / 31 / 78 | r100 / 27 / 74 |
| us (30 games) | 93 | 21 | 69 | | |

Only ha²t and Valenki bank first against us (ha²t 124 rounds before us, with a 7-gem bag: they deposit small and early, we hold a 29-gem bag until r191). Gamblr and Kratos do not bank earlier than we do.

## Hypothesis

The four teams move as a group in the opening and their early contact fights are 2-3 against one champion of ours that is farming alone. v50d targets camps one champion at a time (`squad_size 1`), so a farmer is regularly more than 7 tiles from its nearest ally exactly where the opponent's pack arrives. Each such loss costs about 60 rounds of one champion, its bag and 50-110 gold to the other side, and the lead snowballs (the lost champions' camps are then taken by the winner). The other early-game levers are not the cause: group choice (no), item timing (we are earlier), draft (ha²t has our draft).

What would prove it wrong: if candidates that keep champions together or make them respect an unseen pack do not reduce early deaths in the paired games, or if the deaths against these teams are not the 2+ against 1 collapses the replay positions show.

## Can the pinned panel hold these four teams? (read only, nothing was run)

Yes, on paper. `cambc match-groups create --help`: `<OPPONENT_TEAM_ID> [--source-group <previous match-group UUID or website link>] [--maps m1,..,m5] [--sides a|b ×5]`; `--source-group` "uses the opponent's bot from this previous match-group". `tools/panel/panel.py` takes `team_id`, `maps`, `sides` and an optional `source_group` per opponent and also supports `--pin BASE_LABEL`, which reuses the group each opponent was first played in.

The five ranked groups we already played against them are in the match list (`groupId`), so each can be used as the pin (the opponent's bot as it was in that group):

| opponent | team id | ranked group (pin candidate) | maps in position order (our side) |
|---|---|---|---|
| ha²t | `34b36bab-66bb-4506-b032-2df6a081758d` | `d7e371c5-1c49-43fc-8d38-95d81599ec90` | 00collision, 02crossing, 02geodes, adgato_gemcombat2, adgato_gemcombat5 (b) |
| Gamblr | `f583fbd0-8720-484e-b00c-61159d393c7f` | `7a4f9358-a5a5-4758-8ab8-d85eba20d8e6` | 00elkring, adgato_gemcombat5, 02fields, 00anvil, 00split (b) |
| Valenki | `975c2c15-506b-489b-a439-839c8145933b` | `49b9d769-3b7f-48a9-abc2-c92c0bc0fe33` | 00crater, 01starvation, 02arena, 01yellow_brick_road, adgato_gemcombat1 (a) |
| KratosMessi | `6599a236-7801-436f-a863-4acbb6aafa91` | `964ce40e-d86d-40fd-b4c3-2c5628123748` | 01concentrated_wealth, 02stalactites, 00quarry, adgato_gemcombat5, 01yellow_brick_road (a) |

Caveats:
- Not verified that the platform accepts a **ranked** group as `--source-group` (the help says "match-group", and `panel.py` only ever pins groups it created itself, which are unranked). If it refuses, one unpinned unranked group per opponent (five maps each, our slot) creates a pin for the following runs via `--pin`.
- Sides: all five games of a ranked group had our side fixed (b against ha²t and Gamblr, a against Valenki and Kratos). To compare like with like keep those sides, or alternate them (`--sides`) to remove the side effect: ha²t and Gamblr are the two teams where all ten ranked games had us on side b.
- Their draft and purchase profile is stable per team (ha²t 400 of 400 matches the same three first picks; Valenki 237 of 400 the same five), so one frozen version per team is a fair sample of its behaviour.
- Two of the teams share a draft (Valenki's main comp equals Kratos' second comp), so the four panel entries are not independent samples of the strong-opponent type.

## Candidates

All copied from v50d (v50h14 from v50e1, the live v223), header comment `// Polaris v50hN: ...`, one change each. Mirror = candidate against its base on all 70 maps, both sides, `--release`, deterministic (a control copy of v50d scores exactly 70/70). "Share" = candidate wins / decided games. The early-death columns are per game per side in the same mirror games (candidate / base).

| Bot | Change | Wins / 140 | Share | Gem margin | Deaths by r150 | Deaths by r300 | Gold r200 |
|---|---|---|---|---|---|---|---|
| v50h1 | opening party of three takes the nearest elk group (`opening_party 3`) | 66 | .471 | -57 | .67 / .63 | 1.51 / 1.36 | 648 / 687 |
| v50h2 | opening pairs until r150 (`squad_size 2`, `squad_until_round 150`) | 71 | .507 | -14 | .61 / .69 | 1.35 / 1.40 | 669 / 661 |
| v50h3 | opening escort ball until r120 (`escort_until 120`, squad 9) | 46 | .329 | -203 | .57 / .49 | 1.33 / 1.23 | 510 / 741 |
| v50h4 | draft mode 19 (Vesper second) | 54 | .386 | -100 | .73 / .62 | 1.34 / 1.16 | 637 / 668 |
| v50h5 | earlier disengage off spawn (`hazard_threshold 0.2`) | 70 | .500 | +20 | .67 / .66 | 1.31 / 1.32 | 653 / 649 |
| v50h6 | farm our half first (`territory_penalty 1.0`) | 73 | .521 | +14 | .82 / .80 | 1.54 / 1.62 | 666 / 670 |
| v50h7 | draft Heart, Vesper, Vendetta, Cassi & Issac, Marcella | 21 | .150 | -405 | 1.01 / .55 | 2.04 / 1.06 | 623 / 700 |
| v50h8 | Jungle shards before Treasure (`shop_plan 6`) | 60 | .429 | -114 | .83 / .80 | 1.59 / 1.52 | 669 / 664 |
| v50h9 | unseen pack members in the fight simulation (`phantom_mode 1`) | 35 | .250 | -239 | .49 / .43 | 1.05 / .89 | 612 / 682 |
| v50h10 | shared pack sightings (`phantom_mode 2`, `s_pack`; `group_news` off) | 57 | .407 | -137 | .83 / .75 | 1.53 / 1.36 | 649 / 672 |
| v50h11 | allies walk to a retreating champion (`sos_radius 12`; `group_news` off) | 62 | .443 | -56 | .71 / .84 | 1.44 / 1.64 | 649 / 655 |
| v50h12 | committed homeward retreat (`retreat_mode 2`) | 50 | .357 | -213 | .89 / .64 | 1.75 / 1.25 | 631 / 712 |
| v50h13 | opening cohesion: before r150 a group more than 12 tiles from the nearest ally's current target has its rate scaled by 12/distance (new code, `brain.cpp` score_group) | 66 | .471 | -36 | .80 / .65 | 1.57 / 1.41 | 643 / 682 |
| v50h14 | v50h13's change on v50e1 (against v50e1) | 67 | .479 | -10 | .79 / .65 | 1.53 / 1.53 | 645 / 680 |

Reading:
- No candidate reaches 55%. Best are v50h6 (.521) and v50h2 (.507), both within noise (a 140-game split of 73/67 is p about .3).
- The mirror cannot test the hypothesis. Two v50d bots farm solo against each other and lose only 1.0 to 1.6 champions by r300 per side (the real games against the four: 3.5). A fix for being collapsed by a pack has nothing to protect against here and only pays its cost (fewer pick-ups: 9.9 against 10.5 by r200 for h13). Every behaviour-changing knob lost or tied.
- Draft (h4, h7) and shop-order (h8) changes lose badly in the mirror; they were not diagnosed as the cause either.
- Panel proposal (to be run by the lead with `PANEL_FILE=tools/panel/panel_strong.json`, baseline v223): first v50h14 (cohesion on the live bot), then v50h2 (pairs, the least costly behaviour change) and v50h5 (earlier disengage, the only one directly targeting lone deaths with no mirror cost). Success measure: deaths by r150 and pick-ups at r100 against the four, not only wins.
- A trace copy (`v50h0trace`) was not built: our stdout in the ladder replays carries only fuel lines, but the decoded replay already gives every champion's tile and health each round, which is what the diagnosis needed.

## Banking study (why the 29-gem bag waited until r191) and candidates on v50e1 (v223)

Code (`handle_tribute`, v50e1): banking triggers when the bag reaches `tribute_gems` 25 times a learned factor (0.02 to 12.8, features include distance to the altar), or the altar is within `tribute_detour_tiles` 8, or the game is ending. Threats, low health and capture holds run first. So a bag of 29 is not blocked by the threshold in principle; the replay shows what blocks it (`scripts/bank.py`, 20 games):

- Gem-only `adgato_gemcombat` maps: our first bag of 25+ gems appears at r70-88 (35-63 gems) but the altar is 23-33 tiles away and the first deposit is r154-203 with bags of 49-77. Example `eefca177` (ha²t): Ryth holds 63 gems from r72, walks to the central altar (49,51), is within 2-4 tiles from r120 to r152 and never deposits: an enemy Marcella attacks it there (health 1,200 to 30), it dies at r153 and the enemy takes the 63 gems.
- Other maps: the first 25+ bag comes at r33-130, often at 5-11 tiles from an altar, and our first deposit is r34-95 with 4-22 gems. We do bank small bags early on these (Gamblr games r34-84); the late first banks are the gem-only maps and `00collision`/`02geodes`/`00crater` (never in the Valenki crater game: 0 gems).
- Banking therefore lags for two reasons: the bag is large before the carrier reaches a far altar, and a contested altar means the channel cannot start while an enemy attacks the carrier. A lower threshold fixes neither.

Candidates (built on v50e1; base v50e1; 70 maps both sides, 140 games, 0 bot faults):

| Bot | Change | Wins / 140 | Share | Gem margin | First deposit median | Banked by r200 | Pick-ups by r200 |
|---|---|---|---|---|---|---|---|
| v50h15 | until r250 with nothing banked: bank at 10 gems (`first_bank_gems`) or when an altar is within 16 tiles (`first_bank_detour`) | 68 | .486 | +8 | r74 (base r96) | 67 (base 70) | 10.0 / 10.5 |
| v50h16 | tribute recall as transport earlier (`tribute_recall_margin` 0) | 70 | .500 | -4 | r97 (r97) | 66 (66) | 10.4 / 10.4 |
| v50h17 | both | 66 | .471 | -6 | | | 10.0 / 10.5 |
| v50h2e | v50h2 rebuilt on v50e1 (opening pairs until r150) | 79 | **.564** | +47 | | | 9.7 / 10.3 |
| v50h5e | v50h5 rebuilt on v50e1 (`hazard_threshold` 0.2) | 58 | .414 | -78 | | | 10.1 / 10.5 |
| v50h14 | cohesion (see above) | 67 | .479 | -10 | | | 9.8 / 10.6 |

- v50h15 moves the first deposit 22 rounds earlier but banks no more by r200 and costs 0.4 pick-ups: earlier banking by itself is not a lever in the mirror. v50h16 changes nothing measurable (the recall branch rarely fires with enemies about).
- v50h2e passes 55% on the 70 maps (79/140, margin +47) but on 113 rotated and flipped copies (`mirx`, 226 games) it is 113/113 (.500), pooled 192/366 = .525. Treat as noise.
- v50h2e and v50h5e were smoke-tested by the full batches (no faults). The first v50h5e batch was cut short by a restart; it was rerun to the full 140 games.
- Proposal for the strong panel, in order: v50h14 (cohesion), v50h2e (pairs, the only one above 55%). v50h15 only if a panel against ha²t and Valenki (who bank at r55-67) is wanted for banking; the carrier that dies at the altar suggests the altar-contest, not the threshold, is the real target (a rule to bank from the nearest safe tile or to escort the carrier, not tested).

## Scope scan

All thirteen v50d-based candidates are constant changes except v50h13 (a 16-line block in `score_group`, active only before r150 and only when another ally has a current target). Bot faults: 0 in all 140-game batches. Per-map swings (2-0 on a map is the maximum, two games per map) are scattered with no map that loses for every candidate. Fuel was not scanned beyond the bot-fault count.

## Still to do

- Strong panel (lead): v223 baseline, then v50h14, v50h2, v50h5, with `--pin`.
- If cohesion helps in the panel: tune `cohesion_radius` (12) and `cohesion_until` (150); consider making the rule depend on a seen enemy so it costs nothing on quiet maps.
- ha²t banks small bags at r67 while we carry to r191 against it (see first deposits): an earlier-tribute rule when the enemy leads the bank race is a separate lever not tested.
- The ranked-group pin is untested.
