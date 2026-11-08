# Results index

Every study has its own folder with a `README.md` (summary first, evidence below). Engine eras matter: **never compare results across eras as paired evidence.**

| Era | Dates | Engine / CLI | Maps | Live bot |
|---|---|---|---|---|
| **3** (current) | from 4 Nov 23:00 UTC | 3.0.0 / `cambc` 5.0.0 (patch 4.0.0) | 128 (`maps/`) | v226 = `bots/v50h5e` |
| **2** | 28 Oct to 4 Nov | 2.0.0 / `cambc` 4.0.0 | 86 | v221 to v226 |
| **1** | 17 to 27 Oct | 1.x / `cambc` 2-3 | 40 to 70 | v19f to v225 (old v1x-v29 lines) |

## Era 3 (patch 4.0.0)
| Folder | What |
|---|---|
| [patch-4.0.0-engine3-2026-11-05](patch-4.0.0-engine3-2026-11-05/README.md) | Patch notes, ladder effect, v51d / v51e1 re-tested on 128 maps |

## Era 2 (engine 2.0.0), newest first
| Folder | What |
|---|---|
| [public-insights-2026-11-05](public-insights-2026-11-05/README.md) | Public-repo claims checked on 100 real top-10 games; item-build gaps; census |
| [v51d-ring-window-2026-11-04](v51d-ring-window-2026-11-04/README.md) | v51d from the #45 acceptance check (ring window, small bags under threat, bag cap) |
| [code-efficiency-2026-11-03](code-efficiency-2026-11-03/README.md) | Fuel by phase, decision latency, fuel-sensitivity curve, altar-access deadlock (v51c) |
| [bank-habit-v51ab-2026-11-03](bank-habit-v51ab-2026-11-03/README.md) | v51a / v51b bank habit; top-10 panel 5 vs 4 wins |
| [public-repos-2026-11](public-repos-2026-11/README.md) | Earlier review of public repositories |
| [zero-bank-2026-11](zero-bank-2026-11/README.md) | Why we bank nothing against the top ten |
| [top10-strategies-2026-11](top10-strategies-2026-11/) | Top-10 strategy notes |
| [unit-coordination-2026-11](unit-coordination-2026-11/README.md) | How other bots move and fight as a unit |
| [winner-intangibles-2026-11](winner-intangibles-2026-11/README.md) | What the spring-event winner had |
| [real-losses-2026-11-01](real-losses-2026-11-01/) | Decoded real ranked losses |
| [top25-unranked-2026-11](top25-unranked-2026-11/README.md) | Unranked games against the top 25 |
| [fish-watch-2026-11](fish-watch-2026-11/README.md) | Live bot vs rank-1 Fish, 10 unranked games |
| [map-stress-2026-11](map-stress-2026-11/README.md) | Map-family stress test of v226 |
| [pre221-features-2026-11](pre221-features-2026-11/README.md) | Do pre-221 features still beat the current bot? |
| [56-early-gold-strong-opponents](56-early-gold-strong-opponents/README.md), [55-gem-poor-races](55-gem-poor-races/README.md), [54-mass-death-losses](54-mass-death-losses/README.md), [53-side-b-deficit](53-side-b-deficit/README.md) | Issue studies (the number is the GitHub issue) |
| [tatakai-top10-20261028-fresh.md](tatakai-top10-20261028-fresh.md), [chatgpt/early-economy-audit-2026-11-05.md](chatgpt/early-economy-audit-2026-11-05.md) | Teammate audits (linked from `docs/`) |
| [panel/](panel/) | Real-opponent panel results (`<label>.json`) and raw match summaries (`summaries/*.json.gz`, packed with `tools/lab/pack_summaries.sh`) |

## Era 1 and earlier
[old-engine-2026-10](old-engine-2026-10/): the Polaris spreadsheet, October feature tables, early fight and trace studies, and the first scouting reports. Kept as history; do not quote their numbers as current.

## Conventions
- Folder name: `<topic>-<yyyy-mm-dd>` (or `<issue number>-<topic>` for an issue study). One `README.md` per folder.
- State the engine, map pool, opponents, sides and bot folders in the first lines.
- Raw bulk (replays, match summaries) is packed (`.gz`) or left out; keep the match IDs so it can be re-downloaded.
