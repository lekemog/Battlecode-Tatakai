# Patch 4.0.0 (published 4 Nov 2026 23:08 UTC, engine 3.0.0, `cambc` 5.0.0)

Source: the platform's patch-notes feed (`/api/v1/patch-notes`). The notes are a champion changelog (text plus a picture summary: nerfs Heart of Ruin, Vesper Vale, Marcella, Vendetta; buffs Prism, Varg, Stellar) and two items.

| Change | Before -> after |
|---|---|
| Vendetta | Health 1000 -> 900, Strength 70 -> 65 |
| Vesper Vale | Strength 45 -> 35 |
| Stellar | Focus 70 -> 85 |
| Prism | Focus 80 -> 90 |
| Marcella | Strength 45 -> 40; Strength per shard 4.5 -> 3.5; Focus per shard 14 -> 10 |
| Varg | Strength 45 -> 50 |
| Heart of Ruin | Focus 100 -> 80; Focus per shard 10 -> 9 |
| Skirmish emblem | bonus damage against champions 5% -> 10% |
| Greed emblem | shard value per emblem 35 -> 40 |

`cambc` 5.0.0 changes only doc comments in the SDK header (position snapshots); the balance is in the engine. The map pool is now 128 maps (42 new `04*` maps; our old lab had 86).

## What the ladder shows (our ranked games from 23:20 UTC 4 Nov to 01:10 UTC 5 Nov, all engine 3.0.0)
- Live bot (v226): 31-29 over 60 games; 11-8 on the new `04*` maps, 20-21 on older maps (small samples).
- Top-8 teams' picks in their last 60 ranked games each (480 team-games, all on 3.0.0, so no pre-patch comparison): Heart of Ruin 93%, Marcella 83%, Vesper 64%, Cassi & Issac 61%, Vendetta 46%, Willow 38%, Ryth 23%, Varg 13%, Prism 9%, Ren 8%, Stellar 1%, Tavi 1%. Their combined record 274-206. The meta had not visibly shifted yet.

## Our candidates re-tested on engine 3.0.0 (cambc 5.0.0, all 128 maps x 2 sides = 256 games per row, deterministic)
| Matchup | result | margin | banked / game | deaths / game |
|---|---|---|---|---|
| v50h5e (live) vs v50p1 (early pack) | 165-91 (64.5%) | +230 | 879 | 5.7 |
| v51d vs live | 141-115 (55.1%) | +41 | 835 | 3.6 |
| v51e1 (v51d + Marcella on Focus) vs live | 140-116 (54.7%) | +73 | 853 | 3.4 |
| v51d vs v50p1 (early pack) | 182-74 (71.1%) | +281 | | |
| v51e1 vs v50p1 (early pack) | 190-66 (74.2%) | +311 | | |

Reading: **the Marcella-on-Focus advantage did not survive the patch** (old balance: v51e1 103-69 vs v51d 90-82 against the live bot; new balance: 140-116 vs 141-115). Her Focus per shard fell 29% and Strength per shard 22%, and base Strength 11%. v51d's gain over the live bot is intact (55.1%, about the same as the 52.3% before).

Against the early-pack stress opponent both candidates beat the live bot's own result (165-91): v51d by +17 wins, v51e1 by +25. Against the live bot itself they are level (141 vs 140 wins). So v51e1's Marcella-Focus change helps against a rushing opponent but not in the mirror; neither result is a real-opponent test.

## Implications
1. v51d is the candidate to carry forward (qualification is tracked in issue #71). v51e1 is only worth a panel if someone wants to test Marcella Focus against real opponents: it is level with v51d in the mirror and +8 wins against the early-pack bot.
2. Heart of Ruin (-20% base Focus, -10% growth), Marcella and Vendetta are all in our draft; only Varg was buffed. Our `heart_focus` build still reads Focus growth from the engine, but the Heart nerf is a reason to re-check it.
3. Skirmish (+10% damage against champions) is untested here; we never buy it (`p4_shop_late`, off). Candidate for a single-emblem test.
4. All earlier local numbers in `results/51..54` are on engine 2.0.0 and need the 5.0.0 lab (`PATH=<venv with cambc==5.0.0>/bin`, 128 maps) before they are quoted as current.
