# Ready-to-post issues (from the top-25 unranked study; evidence in README.md)

All counts are v221 (v50c) games against the current top 25, 2026-10-28T13:58Z to 23:28Z (125 games, 21 wins, 104 losses). Replays decoded with tools/replay/extract4.mjs; summaries from `cambc matches summary`.

---

## Issue A: Mixed-map gem races lost with almost no fighting (00lanes, 00expanse, 00rows, 00quadrants, 02fields, 02cuts)

**Evidence.** 41 of the 104 v50-line losses are on these six maps (records: 00lanes 0-11, 00expanse 1-12, 00rows 3-8, 00quadrants 0-4, 02fields 0-3, 02cuts 0-3). Deaths are almost absent: 1 of ours and 0 of theirs by r400. Final banked in those losses: 606 vs 1,050. The gap is collection speed:

| | us | them |
|---|---|---|
| gems collected r200 / r400 / r800 | 95 / 231 / 537 | 134 / 326 / 820 |
| earned gold r200 / r400 / r800 | 837 / 1,982 / 4,586 | 1,071 / 2,552 / 6,020 |
| median first deposit | r54 | r72 |

The gap is already 29% at r200. Decoded examples (side B): 00expanse `8b723e56-ccb1-4ea3-82dc-37f72c8d4fd3` (policy wonk) and `c98bbac6-0c52-4f6f-b479-8b8727257780` (newer team): we claim more groups (97 vs 74; 94 vs 86) and camps (246 vs 203) but bank 841 vs 1,011 and 810 vs 1,037. Their first captures are the 15-gem groups (r35 g2, r82 g22); ours are zero-gem and 4-gem groups. 00lanes `511dcc6f-6baf-4245-9dfd-fc12f259e5f5` (Trzy Kwaterki): 86 groups vs 101, collected 863 vs 1,020, 2 deaths vs 0. Others: 00lanes `e6fffeea-d2c2-451b-a717-e679ba983fc4`, 00rows `fef89915-210e-4db0-bbb5-59a09dabb21f`, 00quadrants `d5a32edc-815d-4c96-8229-8e273217510d`, 02fields `fb91c6b1-03e9-41a1-a747-0ae6af98aa64`, 02cuts `74034685-8342-4aa3-8522-5508e79fbc08`.

**Question.** Does the target valuation (gem weight 1.5 against gold 1.0, learned group factor) pick gold-only groups at the start where the top teams take gem groups, and does that cost us both gems and (through Marcella's tribute gold and Treasure) gold? Or is the gap per-champion farming speed (clear time, walking, heals)?

**Process.** (1) Per game, per champion, time series of camps cleared, gems per camp and gold per camp for both teams from the decoded replays (clears55.py); (2) trace bot logging the chosen group and its gems/gold every 25 rounds (bots/v50g0trace is a base); (3) paired candidates from the live bot: gem weight by map class, early-game group order, route chaining; paired against the live bot on these six maps plus all 70, both sides, transformed copies.

**Acceptance.** Cut the collection gap at r400 by half on the six maps in paired games, with no map -3 and more than 55% of decided games over 70 maps x 2 sides.

---

## Issue B: Mass deaths to a five-champion rush on 00eight and 00packs

**Evidence.** 00eight: 2 wins, 10 losses; our deaths by r400 8.0 against 0.9; banked 143 on average (5 of 10 losses under 100). 00packs: 0-3, deaths 6.0 against 0.3, banked 187. Decoded 00eight losses: `6d57c3c4-4aad-476a-90c3-8dd72e1e0595` (Intercontinental Fish, A: 27 deaths, first death r63), `b6da4193-5657-45ea-80d0-65e8d351c83a` (Claudus Maximus, B: 29 deaths, r81), `65c49ab3-22f7-42f9-8ce2-da6d91f25f6f` (print dont int, B: 27 deaths, r120), `77a55c96-c95e-4610-800a-e28edd332c1e` (policy wonk), `634c9c70` (Fish, B, 26 deaths, first death r73). In the first deaths four to six enemy champions are within six tiles of one or two of ours, 14-31 tiles from our spawn, at r63-83 (e.g. `6d57c3c4` r63: six enemy champions, four allies at the spot, dead at (15,9)); by r300 we have lost 8-11 champions while they lose 0-1. Their champion-rounds in `6d57c3c4` are 4,782 against our 2,492 because our champions spend the game dead. On 00packs: `5a1adcd1-4909-4596-a6e9-c4440634231f` (20 deaths), `5fb43821-5837-4892-8649-4fb434276394`, `e57a8d47-6b10-4a8a-ad50-154c8807a94e`.

**Question.** Is this the same cause as #54 (we meet a grouped team piecemeal and keep re-engaging as individuals) concentrated on two small central-altar maps? Where is the opponent's group at r40-80 and what would make us hold the spawn side as one group until they commit?

**Process.** Reproduce locally with a bot that rushes with a grouped team (a known opener from the replays) on 00eight and 00packs; trace our champions' positions and decisions for r40-150; candidates: hold-and-heal at the spawn until the group is within N tiles, grouped opening, retreat to the altar region.

**Acceptance.** Fewer than 3 deaths by r150 in the reproduction and a win rate over 55% on both maps in paired games against the live bot.

---

## Issue C: The top 25 out-earn us two to one before any fight, and our champions die with half their items

**Evidence.** Over the 125 games: earned gold r200 674 vs 946, r800 3,454 vs 5,240; gems collected by r400 223 vs 320; deaths by r400 3.3 vs 0.8; median first death r127 (ours) vs r352, first kill r398 (ours) vs r133. At the moment of our deaths our team holds 14.1 item points against the killer's 32.4 (747 deaths in 50 decoded losses). 13 of 14 opponents show the gold gap. This extends #56 (early gold, strong opponents) from ranked to unranked games and to the full top 25, and the numbers are consistent with it.

**Question.** What do the top teams buy first and when (summary itemsBought plus the spentGold timeline), and does our opener (v223: Prospector) close the r200 gap? These games are v221 only, so the first step is to repeat the same table for v222-v224 on fresh ladder games.

**Process.** Item purchase times per game, both teams (decoded replays, `items` array), against gold earned; compare with the live bot's first 300 rounds on the same maps.

**Acceptance.** Gold at r200 within 10% of the opponent in paired games against the top-25 bots or a documented reason it cannot be.

---

## Issue D: Side B

**Evidence.** v50 line: as side A 16 wins in 74, as side B 5 in 51 (older lines 13 of 527 and 0 of 118). Same maps and opponents on both sides. Counts are small; the older lines add 118 side-B games with zero wins. This is #53 (side-B deficit) seen in unranked games.

**Question.** Does the deficit come from our spawn geometry (distance to the first groups, who reaches the middle first) or from an asymmetric rule in the bot (tie-breaks by index, slot order, mirror assumptions)?

**Process.** Paired mirror games with the same bot on both sides on all 70 maps (v50dc against v50d showed 70-70); then per-map first-contact time and first-capture times by side in the ladder replays.

**Acceptance.** Win rate as B within 5 points of A in the mirror against the top-25 style bots, or the geometric cause identified.

---

## Issue E: Close verification of the sealed-altar breach on 02the_pack (v222+)

**Evidence.** 02the_pack: 5 wins, 6 losses in the v221 games, every loss with 0 banked (`afc91eeb-c57d-4bd9-8d45-b2e7af18245f`, `4490976d-43a4-4d7e-b6a9-e08712a3dbda`, `b63ee66b-2c88-4bba-a7c8-84446e03c64c`, `c45594a3`, `3f0c28d3`, `8e45424a`); the wins are tiebreak or opponent-weak games. This is #45. v50d added the breach; the unranked set has no v222+ the_pack game.

**Question.** On the ladder with v222/v223, does the bot now bank on 02the_pack against the top 25 (first deposit round, number of breached camps)?

**Process.** Next batch of ranked/unranked 02the_pack games against the top 25 with v50d/v50e1; apply tools/replay/ring45.py.

**Acceptance.** At least one deposit in every 02the_pack game, and the first deposit before r700.

---

## Issue F: Round-2000 games: gold tiebreak and 0-0 stalemates (00contest, 00stampede, 02the_pack)

**Evidence.** 7 of 125 games end at round 2000; we lost 3. 00contest `e1704314-9216-4a66-8106-928a06fa9c8e` (Mite, B): banked 0-0, we lost on gold (2,530 vs 6,324 at r800) with 17 deaths to 1. 00stampede `c12ea5c3-956b-46e9-8677-173d43647125` (print dont int): 480 vs 861 gems at r2000, 7 deaths to 1 by r800. 02the_pack `afc91eeb` (0 vs 242, 2000 rounds, no breach).

**Question.** On maps where nobody banks, gold decides; do we spend our gold (items) rather than hold it, and do we lose the gold race because of deaths (each death gives 50 gold to the killer)? Should the bot track the tiebreak (gems, then gold) in the last 500 rounds?

**Process.** Replay timeline of gold earned and spent on 00contest; candidate: tiebreak-aware late game (stop feeding kills, bank what exists, hold gold).

**Acceptance.** Win or draw-by-tiebreak share over 55% on 00contest and 00stampede against the live bot, no regression elsewhere.
