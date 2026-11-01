# #55 — slow races and low banking on the gem-poor maps: replay study and paired candidates

Date: 1 November 2026. Baseline: v50d (ladder 222). Ladder engine 2.0.0, cambc 4.0.0.

## Summary

(Filled in at the end of the file work; see "Candidates" for the numbers.)

## Facts from the real replays

Source: 18 of the 60 ranked games in `results/real-losses-2026-11-01/` (16 of the 17 target losses, plus two stalactites and two wins for contrast), downloaded with `cambc matches download`, decoded with `tools/replay/extract4.mjs` (cambc 4.0.0 assets) and summarised with `tools/replay/sum55.py`, `race55.py` and `clears55.py`. The per-game table is `replay-table.txt`; the gems each group class gave each side is `replay-heavy-groups.txt`.

"Collected" below is the cumulative growth of (banked + carried) gems per team, so a gem lost in a death counts as collected by the victim and again by the killer. Group captures are counted when a group goes from "reward available" to "claimed".

### 1. The two sides collect at very different rates, and the gap is in a few groups

| game | map | gems collected us / them | banked | camps claimed | deaths | gems lost in our bags |
|---|---|---|---|---|---|---|
| `eefca177` | gemcombat5 | 560 / 1106 | 140 / 1008 | 75 / 125 | 5 / 1 | 231 |
| `41c63132` | gemcombat2 | 539 / 1029 | 252 / 1001 | 74 / 121 | 12 / 3 | 182 |
| `176874c7` | gemcombat2 | 707 / 1120 | 441 / 1022 | 89 / 131 | 9 / 4 | 203 |
| `15cb2442` | gemcombat1 | 609 / 1002 | 420 / 1002 | 87 / 117 | 13 / 0 | 168 |
| `dd2143ee` | anvil | 319 / 1076 | 261 / 1030 | 152 / 130 | 8 / 8 | 21 |
| `e1171fcf` | stampede | 320 / 1057 | 320 / 1057 | 356 / 334 | 5 / 10 | 0 |
| `1a73dd15` | pilgrimage | 255 / 1066 | 195 / 1030 | 209 / 285 | 13 / 2 | 30 |
| `a897224d` | stalactites | 207 / 1061 | 130 / 1022 | 34 / 145 | 28 / 1 | 77 |
| `b3e86920` | stalactites | 1029 / 1069 | 721 / 1065 | 147 / 156 | 6 / 0 | 154 |
| `2f7dbafd` | fields | 835 / 1030 | 735 / 1023 | 141 / 122 | 3 / 7 | 0 |
| `3620988e` | collision | 698 / 1070 | 574 / 1019 | 174 / 204 | 8 / 2 | 78 |
| `affcea93` | geodes | 840 / 1055 | 558 / 1004 | 102 / 126 | 4 / 0 | 33 |
| `f9e02957` | crossing | 863 / 1094 | 727 / 1022 | 110 / 131 | 9 / 7 | 111 |
| `75e75bad` | split | 940 / 1119 | 867 / 1073 | 173 / 140 | 1 / 1 | 25 |
| `cc934a52` | split | 842 / 1044 | 834 / 1020 | 156 / 197 | 1 / 1 | 0 |
| `c3f51447` | big_world | 1166 / 1061 | 837 / 1000 | 169 / 204 | 0 / 0 | 0 |

The 16 losses fall into three groups:

**A. A heavy group decides the race and we never attack it (5 games: anvil, pilgrimage, stampede, fields, split `75e75bad`).**
A "heavy" group is one of at least 10,000 total health: a lone monolith (anvil: 20,000 HP, 200 gems + 300 gold a capture, respawns 150 rounds after death), the 20-camp herd on stampede (16,080 HP, 160 gems), a 16-camp group on pilgrimage (11,040 HP, 88 gems). Gems we and they got from heavy groups (`replay-heavy-groups.txt`):

| game | heavy-group gems us / them | their captures of heavy groups | ours |
|---|---|---|---|
| anvil `dd2143ee` | 0 / 600 | 3 | 0 |
| pilgrimage `1a73dd15` | 0 / 665 | 7 | 0 |
| stampede `e1171fcf` | 352 / 1056 | 6 | 2 |
| fields `2f7dbafd` | 284 / 661 | 3 | 2 |
| split `75e75bad` | 0 / 214 | 1 | 0 |

On anvil 600 of their 1030 gems came from three monolith captures; we claimed 76 groups to their 63, all gold or small gem groups, and 0 monoliths. They needed four champions standing at the monolith from r420 to r680 (20,000 → 0), and again r850–980 and r1120–1160 (the third time only 40 rounds). On stampede the herd is the only gem source; they first cleared it at r776 and took it 6 times, we took it twice (first clear r~1500).

**B. Gem-poor and gold-free maps where combat decides (6 games: gemcombat 1, 2, 2, 5, stalactites `a897224d` and `b3e86920`).** Both sides take the same near groups at the same times in the first 160 rounds (e.g. gemcombat2 `176874c7`: 17 vs 14 captures to r160), then they take the central 8-camp group 9 times to our once and kill us 9-13 times to their 0-4. Our champions are alive for 80% of their champion-rounds (gemcombat2 `41c63132` r600: 1850 vs 2284). On gemcombat the shop is not the issue: nobody can earn gold except by kills, and our 100 starting gold is spent.

**C. Plain slow races (5 games: geodes, crossing, collision, split `cc934a52`, big_world).** Deaths are modest (0-9), conversion of collected into banked gems is 80-100% (except big_world, 837 banked with 329 still in bags at the end), and the gap is a 15-25% lower collection rate. The camps-claimed gap is 10-25% (`cc934a52`: 156 vs 197). Nothing banking-specific shows here.

### 2. Banking is not the main lever

- Mean deposit: ours 34 gems, theirs 45 (16 games). Deposits per game: ours 2-33, theirs 10-42.
- Gems lost in our bags at death: 168-231 in four gemcombat games (30% of what we collected), under 80 in the rest. These come with the deaths in group B, not with the bag threshold.
- The bag threshold is not the nominal 25. The learned factor in `handle_tribute` lifts it to 40-64: local trace (`trace-local-anvil.txt`, TB55 lines) shows `bag` values 40-64 and champions carrying 21-25 gems 10-20 tiles from the altar without banking.

## Code path (v50d)

1. **Siege planner rejects heavy groups for a lone champion.** `score_group` (`brain.cpp`, "best_extra < 0 → last_reject_ = 5") plans the siege with the champion, committed allies and at most `max_hypothetical_joiners = 1` hypothetical ally. For the anvil monolith the plan needs 19-32 trips against `siege_max_trips = 4`: local trace `R5 r1 g10 gems200 gold300 hp20000 dmg32609 pool2107 trips25 joiners1 coming0` and the same at every later 50-round dump. The group has by far the highest cheap bound (`bound 170` vs 3 for the best ordinary group) but score 0 with reject 5, so nobody targets it and nobody is ever "coming". A deadlock: the siege is only feasible with 3-4 champions, and champions only commit once it is feasible.
2. `jackpot_share = 0` (the earlier 0.4 setting lost 85 → 64-72 of 112 on the old maps), so `jackpot_joiners = 4` never applies.
3. `max_respawn_wait = 0`: a group still respawning on arrival is rejected (reject 3) even if the wait is a few rounds.
4. Bag threshold: 25 × learned factor (`cfg::learned = 1`).

## Local reproduction

Setup: cambc 4.0.0 `--release`, scratch project with v50d, v50g candidates, `bots/v50g0trace` (v50d + log lines G55 income/bank every 50 rounds, TB55 bank decisions, TS/R5 group scores, GRP55 group table; no behaviour change except the fuel the logs use).

- anvil mirror v50g0trace (A) vs v50d (B): same slow race as on the ladder (banked 125 / 254 at r700, ladder 141 / 208), win for A at r1782-1956. R5 lines as above.
- `map-groups.txt` lists every map's group totals and heavy groups (57 maps with data; the others had no champion in slot 0 at r50).

Paired design: the candidate against v50d on all 70 maps, both sides, deterministic. `v50dc` (a copy of v50d) vs v50d gives exactly 70-70 and +0, so any deviation is caused by the change. Maps where the candidate changes nothing show 1-1 with margin +0.

## Hypothesis

The races on gem-poor maps are decided by a handful of groups that carry most of the gems: a lone heavy jackpot (A) or a central group the opponent holds by force (B). The first is a planner deadlock and is fixable; the second is a combat/posture problem. The slow races of group C are a general collection-rate gap and need no banking change.

## Candidates

All copied from `bots/v50d`, one change each; paired against v50d.

| bot | change | status |
|---|---|---|
| `bots/v50g1` | groups with total health ≥ 10,000 plan their siege with 3 hypothetical allies instead of 1 | result below |
| `bots/v50g2` | jackpot machinery on (`jackpot_share` 0.3: gem weight ×3, 4 joiners, patience) | result below |
| `bots/v50g3` | `max_respawn_wait` 0 → 20 | pending |
| `bots/v50g4` | gem-poor maps (≤ 400 gems per cycle): bank any bag ≥ 30 | pending |
| `bots/v50g5` | gem-poor maps: gem weight 4 (was 1.5) | pending |
| `bots/v50g6` | g1, only for heavy groups holding ≥ 35% of the map's gems per cycle | pending |

### v50g1: 70 / 70, margin -2

| | wins | share | margin | collected | deaths |
|---|---|---|---|---|---|
| v50g1 vs v50d, 70 maps × 2 sides | 70 / 140 | 0.500 | -2 | 1157 / 1129 | 5.9 / 5.7 |

Maps that moved by two games: anvil +2 (margin +883), 00monolith +2, 00rows +2, 01shortcut +2, 01the-farm +2; against it 00swirl -2 (margin -1814), 02harvest -2, 02cuts -2, 00split -2, 00lanes -2. Stampede 1-1 (+560): as side A 1040 vs 160, as side B 640 vs 960. The gain is where the heavy group holds most of the map's gems (anvil 200 of 258, rows 470 of 584), the loss where heavy groups are a minor share (swirl 88 of 638 per group, harvest 114 of 505, split 214 of 850): a lone champion leaves a good farm for a siege that needs the others.

### v50g2: 67 / 73, margin -82

Not an improvement; the jackpot machinery changes many maps at once (stampede -2, pilgrimage -794 margin, contest -2000).

(g3-g6 results are added below as the batches finish.)

## Still to do

- Fresh-seed confirmation and transformed copies of the loss maps for any candidate that passes.
- The central-group fights of group B (gemcombat) are a combat problem; no candidate here addresses them.
