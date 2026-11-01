# #56 — early gold deficit and 0-5 records against ha²t, Gamblr, Valenki and Kratos

Date: 1 November 2026. Baseline: v50d (live version 222). Ladder engine 2.0.0, cambc 4.0.0.

## Summary

- The early gold deficit is real but it is **specific to these four opponents**. Over all 60 ranked games since v222 our gold at r200 is 601 against 615 for the opponent. In the 40 games against other teams it is 659 against 597 (we lead). In the 20 games against the four it is 484 against 650.
- Against everyone else these four average 8.8 to 9.7 pick-ups by r200 and we average 9.2, so the camp economy is level. In the 20 games against the four we make 8.7 pick-ups by r200 against their 10.2. The difference comes from **champion deaths in the first 150 rounds**: the pick-ups we miss while a champion is dead (about 60 rounds plus the walk back), the 50-110 gold a kill pays the other side, and the bag we lose.
- In the 20 decoded games our champions die 70 times before r300, theirs 28 times. Our first death comes before theirs in 15 of 20 games (median r93, theirs r166).
- Those deaths are collapses on a champion that is away from its team: **57% of our early deaths are against two or more enemies than we have allies nearby (theirs 7%), and 43% happen with no ally within 7 tiles (theirs 21%)**. In rounds 30-200 our champions stand more than 7 tiles from their nearest ally 38% of the time (opponents 26%; against Gamblr and Valenki 44% against 15%).
- Items and draft are not the first-order cause. We buy earlier and more than three of the four (median first purchase r52 against r67; 13.8 items by r200 against 11.3). Gamblr, Valenki and Kratos draft Vesper Vale and Vendetta with Heart of Ruin and Cassi & Issac; ha²t drafts exactly our order.
- Eleven isolated candidates (v50h1 to v50h12, one change each, all copied from v50d) were built and are being run against v50d in paired mirror games. Results in the table below.
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

## Hypothesis

The four teams move as a group in the opening and their early contact fights are 2-3 against one champion of ours that is farming alone. v50d targets camps one champion at a time (`squad_size 1`), so a farmer is regularly more than 7 tiles from its nearest ally exactly where the opponent's pack arrives. Each such loss costs about 60 rounds of one champion, its bag and 50-110 gold to the other side, and the lead snowballs (the lost champions' camps are then taken by the winner). The other early-game levers are not the cause: group choice (no), item timing (we are earlier), draft (ha²t has our draft).

What would prove it wrong: if candidates that keep champions together or make them respect an unseen pack do not reduce early deaths in the paired games, or if the deaths against these teams are not the 2+ against 1 collapses the replay positions show.

## Candidates (all copied from v50d, header comment `// Polaris v50hN: ...`, one change each)

See the table in the section below; results are filled in as the batches finish.

## Scope scan

To be filled in.

## Still to do

To be filled in.
