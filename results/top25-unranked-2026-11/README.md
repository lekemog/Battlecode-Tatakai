# Unranked games against the current top 25: what we keep losing and why

Date: 1 November 2026. Data pulled with the CLI on 1 November (matches list `--team me --kind unranked`, paged to exhaustion; ladder page 1 for the top 25). Scripts: `list_matches.py`, `download_matches.py`, `stats_top25.py`, `tables_top25.py` (this folder), `tools/replay/{extract4.mjs,deaths54.py,race55.py,clears55.py,sum55.py}`. Machine-readable: `games.json` (one row per game), `deaths-decoded-losses.json`, `per-opponent-tables.txt`.

## Data counts

| | games | wins | losses |
|---|---|---|---|
| all unranked games listed for us | 11,880 | | |
| opponent in the current top 25 (finished) | **1,030** | 53 | 977 |
| v50 line (v221 = v50c, 2026-10-28T13:58Z to 23:28Z) | **125** | 21 | **104** |
| older bot lines (2026-10-17 to 10-28T13:58Z: v29e, v25x, ...) | 905 | 32 | 873 |
| tournament-kind games | 0 | | |

- All 1,030 summaries downloaded. Replays: 50 of the 104 v50-line losses (the 40 largest-margin and the 10 closest), all decoded; they contain 747 of our deaths.
- **No top-25 unranked game is newer than 2026-10-28T23:28Z.** Everything after that in the unranked list is the panel chain against mid-rank teams (ignored). So the "v50 line" here is v221 only; v222 (v50d), v223 (v50e1) and v224 have no top-25 unranked games, and any v50-era finding must be re-checked against them (several are already addressed in v50d: see issue 5).
- 14 distinct top-25 teams appear in the v50 line (12 with 5+ games), 18 in the older lines.
- Bot faults in the 1,030 summaries: 0. Our stdout in the 50 decoded replays: no `bot error`, no fuel exhaustion lines.
- Era wins: v50 line 21 of 125 (17%), older lines 32 of 905 (3.5%). The v50 line is clearly stronger; the wins that exist are on the maps in the table below.

## Per opponent, v50 line (our means; deaths, gold and gems from the summary timelines)

See `per-opponent-tables.txt` for the older era too. Columns: our W-L, their most common draft, deaths by r400 us/them, earned gold by r200 us/them and r800, gems collected by r400 and r800, mean final banked gems in our losses.

| rank | opponent | v50 W-L | typical draft | deaths us/them r400 | earned gold us/them r200 | r800 | collected gems r400 | r800 | mean banked us/them (losses) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Intercontinental Fish | 2-18 | Cassi,Heart of Ruin,Issac,Vendetta,Vesper Vale | 4.2/0.9 | 608/986 | 2931/5031 | 211/467 | 421/874 | 366/1040 |
| 3 | newer team | 3-7 | Cassi,Heart of Ruin,Issac,Marcella,Varg,Vendetta | 1.2/0.3 | 771/947 | 3950/4963 | 276/398 | 534/855 | 487/1018 |
| 4 | Ad Astra | 0-10 | Heart of Ruin,Ryth,Vesper Vale | 2.1/0.4 | 647/965 | 3488/6069 | 208/263 | 477/751 | 431/1038 |
| 5 | Mite | 2-13 | Heart of Ruin,Marcella,Tavi,Vendetta,Vesper Vale | 3.9/0.4 | 598/978 | 3187/4995 | 234/327 | 532/817 | 494/951 |
| 6 | prism best girl | 0-10 | Cassi,Heart of Ruin,Issac,Vendetta,Vesper Vale | 4.1/1.2 | 739/996 | 3496/5560 | 221/303 | 489/822 | 367/969 |
| 7 | NEETCoders | 1-4 | Heart of Ruin,Marcella,Ryth,Vendetta,Vesper Vale | 3.6/0.2 | 482/887 | 3000/4035 | 159/430 | 383/772 | 356/1038 |
| 8 | policy wonk | 0-5 | Heart of Ruin,Marcella,Tavi,Varg,Vendetta | 2.4/0.0 | 798/1090 | 3759/6766 | 212/294 | 457/855 | 382/1075 |
| 9 | print dont int | 4-6 | Heart of Ruin,Marcella,Ryth,Vendetta,Vesper Vale | 2.9/1.2 | 763/894 | 4278/5515 | 175/216 | 477/568 | 408/1018 |
| 11 | Sponge(Albert and Bob) | 0-5 | Heart of Ruin,Marcella,Ryth,Vendetta,Willow | 3.6/0.8 | 582/874 | 3432/4760 | 282/236 | 724/742 | 600/1029 |
| 13 | test4 | 3-2 | Cassi,Heart of Ruin,Issac,Marcella,Tavi,Vesper Vale | 2.8/2.8 | 773/784 | 3804/4477 | 355/334 | 783/890 | 368/1012 |
| 15 | Trzy Kwaterki | 2-8 | Heart of Ruin,Marcella,Ryth,Vendetta,Vesper Vale | 1.9/1.1 | 811/1057 | 4779/5749 | 252/212 | 605/720 | 366/1018 |
| 17 | Claudus Maximus | 1-9 | Heart of Ruin,Marcella,Tavi,Vendetta,Vesper Vale | 3.4/0.6 | 631/954 | 2949/5269 | 202/292 | 461/701 | 332/1036 |
| 22 | conqueror_of_openai | 1-4 | Heart of Ruin,Marcella,Varg,Vendetta,Vesper Vale | 6.6/2.6 | 657/821 | 2501/6039 | 111/194 | 271/566 | 108/1015 |
| 24 | Sheeesh--- | 2-3 | Marcella,Prism,Tavi,Varg,Willow | 4.4/0.0 | 606/690 | 2691/3573 | 236/289 | 530/656 | 399/1017 |


Reading:
- Over all 125 games: earned gold at r200 674 vs 946, at r800 3,454 vs 5,240; gems collected by r400 223 vs 320. Only test4 (3-2) and Sponge (gems r400) are level. The gap opens in the first 200 rounds and widens; it is 25-45% on every strong opponent.
- Deaths by r400: 3.3 of ours against 0.8 of theirs. Median first death r127 (ours) against r352 (theirs); median first kill ours r398, theirs r133.
- Our drafts are the same five champions in most games (Heart of Ruin, Marcella, Ryth, Varg, Vendetta in 76 of 125); the top teams play Heart of Ruin, Vendetta, Vesper Vale and Marcella, plus Cassi/Issac (Fish, prism best girl, newer team) or Tavi (Mite, Claudus Maximus, policy wonk). We do not draft Vesper Vale, Cassi/Issac or Tavi in these games.
- By side: v50 line as A 16 wins of 74, as B 5 of 51; older lines as A 13 of 527, as B 0 of 118.
- End reasons in the v50 line: 118 games end by gems; 7 end at round 2000 (tiebreak): we lost 3 (00contest, 00stampede, 02the_pack), won 4.

## Records by map (v50 line)

Losses and wins on the maps with 3+ games: 00expanse 1-12 (W-L), 00eight 2-10, 00lanes 0-11, 00rows 3-8, 02the_pack 5-6, 00quadrants 0-4, 02fields 0-3, 00packs 0-3, 02cuts 0-3. The nine maps hold 63 of the 104 losses.

## Decoded facts (50 losses, 747 deaths)

- Death labels (deaths54.py): outnumbered 372, duel/outnumbered-by-one 209, duel with help 161, camp 5. 315 deaths had no ally within 6 tiles; 139 died from 70%+ health within three rounds; 418 of 747 were 20+ tiles from our spawn.
- Timing: deaths per 150-round slice: 87, 120, 95, 120, 100, 89, 136 (no early cluster; they continue all game). 90 of 747 are before r150.
- Item points at the moment of death: ours 14.1, the killer's team 32.4.
- 7,238 gems were in bags when champions died (about 145 per decoded loss).
- Banked gems at the end of these losses: below 100 in 26 of the 50 decoded losses (and 26 of the 104 in total: 6 on 02the_pack, 5 on 00eight).

## Issues (details, evidence and example ids in `issues.md`)

1. **Mixed-map gem races lost without fights** (00lanes, 00expanse, 00rows, 00quadrants, 02fields, 02cuts: 41 of 104 losses, deaths about 1 by r400): we collect 30-45% fewer gems from r100 on and earn 25% less gold, while claiming as many or more camps; the top team's early captures are the gem-bearing groups, ours are gold-only ones.
2. **00eight and 00packs mass-death rushes** (00eight 2-10, 8.0 of our deaths against 0.9 by r400, banked 143 on average; 00packs 0-3, 6.0 deaths): the opponent walks five champions onto our half at r60-80.
3. **The field out-earns us 2:1 in items before any fight** (gold r200 -25%, items at death 14 vs 32; 13 of 13 opponents).
4. **Side B** (5 wins in 51 against 16 in 74; older lines 0 of 118): same maps, same opponents.
5. **Zero-deposit losses on camp-ringed altars** (02the_pack: 6 losses with 0 banked, v221 only; fixed in v50d by the breach logic of #45, needs a ladder check).
6. **Round-2000 and gold-only maps** (00contest lost 0-0 on gold after 17 deaths to 1; 00stampede 480 vs 861; 02the_pack).

## What each implies for the bot

See `issues.md`. Short form: 1 is target valuation and per-champion farming speed on mixed maps (the largest group, no fights involved); 2 is an opening/draft and cohesion problem on two small central-altar maps; 3 is #56; 4 is #53; 5 is closed pending a v222+ check; 6 is a scoring problem (gold tiebreak) that needs a policy decision.

## Limits

- The top-25 sample is all v221 (v50c). Nothing here measures v50d/v50e1.
- Replays were decoded only for 50 of 104 losses (largest margins), so the slow-race maps (issue 1) are over-represented in the summaries and under-represented in the decoded set: three decoded games (8b723e56, c98bbac6, 511dcc6f) support the group-choice finding, the rest rests on the summary timelines.
- "Collected gems" counts growth of banked plus carried gems, so a gem changing hands in a kill counts for both teams.
