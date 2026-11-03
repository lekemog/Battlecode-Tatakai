# Public Cambridge Battlecode 2026a repositories (checked 2026-11-03)

Read-only review of public repos found by search. All are third-party; their claims are not verified by us. Nothing was built or run from them.

| Repo | What | Activity | Use to us |
|---|---|---|---|
| Faisal-Saqib/CambridgeBot | Rust and C++ bots, 40+ analysis docs on the top-20 ladder teams (299 ranked games of Mite, Fish, newer team), per-map plans for all 70 maps | last commit 2026-10-29 | high: independent top-3 scouting, see below |
| dpark2380/cambridge-battlecode | C++ bot with tuning scripts (recall_health, tribute_gems) | seen earlier | low-medium |
| Mada21v/CAMBC-2026-Midnight-Wardens, FHL-08/Tarot-Club-Cambc2026, MohnishDhangar/Cambc | C++ bots (Mohnish is our `h_mohnish` bench opponent) | seen earlier | low |
| Ahmed-Abdul-Rahim/definetly-not-battlecode | Rust bot and tooling, one commit 2026-10-18, docs on champions and fuel | stale | low |
| Coook13, Swapnanil-06, riic10 | other games or beginner bots | - | none |

## From CambridgeBot's top-3 scouting (their data, labelled [measured] there)
- Fish drafts Cassi and Issac in its signature comp (68/100 wins), Mite uses Heart of Ruin + Marcella + Tavi + Vendetta + Vesper, newer team uses Prism + Willow. Heart of Ruin, Vendetta and Vesper appear in all three.
- First tribute by about round 44 to 87 in all three, small bags (25 to 45 gems) many times a game: banking early and often, not hoarding. This matches our zero-bank finding (`results/zero-bank-2026-11/`).
- Mite places 150 to 290 wards a game; opponents buy about 4 altar locks and 1.8 teleport crystals a game; Fish buys 11 to 30 late Bruiser Strength shards. Winners die 1.5 to 5 times a game against our 15 to 19 in their data.
- Our bot already has lock_mode 2 and ward_mode 4, so the open items for us are the tribute habit (bag size at which we bank) and the item mix.

## Candidates to test (panel, now about 10 minutes per run)
1. Lower banking threshold (`tribute_gems` 25 stays but the learned bank factor grows bags to 100-150): force a cap of about 40 gems.
2. Item mix: Bruiser Strength after the first Health shards.
3. Cassi and Issac only on 3-pick maps, after the grave/regroup logic (local result negative).
