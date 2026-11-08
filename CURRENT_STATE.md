# Current state — 5 November 2026

This dated snapshot supersedes old onboarding claims about v19f, v50c, the 18 October freeze, 70/86 maps and CLI 4.0.0. It does not replace the platform's active-submission check.

## Sources and freshness
Latest checked Claude patch branch: 03b34544c02d0e9b501183f5d1f4a60759ceec9f, 5 Nov 01:23 UTC. Main remains 3f68e956 at review start. Development branch claude/vibrant-turing-rtpcwn resolves to 38ab9c40 (3 Nov). Additional teammate report at 61c3a3f3 (3 Nov). Use immutable links in docs/UK_TOP6_PLAN.md to reproduce this review.

Official patch notes checked in the signed-in platform UI: Patch 4.0.0 dated 4 Nov, newest listed. Vendetta HP 1000→900 and Strength 70→65; Vesper Strength 45→35; Stellar Focus 70→85; Prism Focus 80→90; Marcella Strength 45→40, Strength/shard 4.5→3.5, Focus/shard 14→10; Varg Strength 45→50; Heart Focus 100→80 and Focus/shard 10→9. Skirmish anti-champion damage 5%→10%; Greed shard value 35→40. Do not confuse patch 4.0.0 with CLI 4.0.0.

Claude's latest report states CLI 5.0.0, engine 3.0.0 and 128 maps (42 added 04* maps beyond 86). These versions/map counts were checked against that report, not independently rebuilt or enumerated here. Verify actual CLI version, engine build and map hashes before running. Existing TESTING.md and CLI_FOR_AGENTS.md still contain old installation/version/count instructions: use cambc==5.0.0 for this reported patch baseline, refresh maps, rebuild clean release artifacts and verify resulting engine build. Never compare engine-2 and engine-3 results as paired evidence.

## Ladder snapshot from official UI
UK filter: 188 teams. Tatakai UK 13 / overall 91, 1966 Elo. UK sixth is 剑桥夜爬者, 2113; gap 147 points at observation. Top six: BattleCats 2388, QS2isLaw 2280, Rogue Lock Pickers 2241, Claudus Maximus 2220, 0xDEADBEEF 2151, 剑桥夜爬者 2113. Next: DOOMSDAY 2104, smurphy 2076, bentheboss 2028, Prompt Beasts 2003. Ratings and membership are a moving snapshot, not a promised target Elo.

Official public schedule lists UK qualifier 11 Nov, lock 10 Nov. Recheck exact platform lock time before planning the final change window; this review does not infer an hour from an old sprint deadline.

## What Claude established (reported experiments)
- v50d sealed-altar breach addressed the_pack zero-deposit failure; v50e1 Prospector opener improved the old mid-rank panel 35/45 vs 32/45.
- v226/v50h5e earlier hazard disengage: two old-engine strong panels 22/40 vs 15/40 for v223. Its 41% mirror result did not invalidate the real-opponent gain.
- v50j1 grave/regroup/cohesion bundle: old top-ten panel 3/50 vs baseline 4/50; rejected. Do not rebrand it as a new proven improvement.
- New-engine v51d vs v226: 141–115 on 128 maps × both sides. v51e1 (Marcella Focus variation) 140–116. This is local evidence; v51d vs early pack was pending in the latest report.
- The prior Marcella-Focus advantage did not persist under the new patch. Skirmish and Greed changes warrant isolated checks, not automatic purchases.

## Static code findings, not runtime certification
v51d brain.cpp still has an unstamped four-slot HP buffer: write at line 339, modulo “three rounds ago” read at 1678. Revisit PR #50 with observation-gap/death-reset tests. Mode-name-based progress resetting around line 516 merits an action-success audit; no new match establishes it as a stall cause. Existing distance-progress tracking, bans, nav legality checks and fuel guards mean we should extend evidence rather than add duplicate systems.

No new matches, deployment, eligibility change or full dead-code proof was produced in this review.

## Update, 8 November 2026 (ladder and tidy)
- **Ladder** (official API, 8 Nov): Tatakai is **81st of the ladder, rating 2,026.6** (3,113 matches), 91st at the 5 Nov snapshot and 74th on 2 Nov. Top: 2,777. The top-100 cutoff is 1,983; ranks 80 to 82 are within 1.6 points. Not yet qualified for the International Qualifiers (Sprints 1 to 3 only).
- **UK teams identifiable on the global ladder** (UK rank needs the platform's UK filter, which the API does not expose): BattleCats 4th (2,603), QS2isLaw 20th (2,330), bentheboss 26th (2,285), Rogue Lock Pickers 27th (2,281), Claudus Maximus 34th (2,229), smurphy 36th (2,224), 剑桥夜爬者 40th (2,201), 0xDEADBEEF 47th (2,169), DOOMSDAY 62nd (2,098), **Tatakai 81st (2,027)**, Prompt Beasts 114th (1,944). Among these we are 10th of 11. The sixth-best of the listed UK teams is now about 2,224 (it was 2,113 on 5 Nov): we gained 61 points, the cutoff gained about 111. Other UK teams may sit above us; treat this as a lower bound on the gap (about 197).
- **Live submission:** v226 (`bots/v50h5e`), pinned; no live-slot window open. No submission was made since 3 Nov (v233 = v51b was the last test, reverted).
- **Engine-3 mirrors finished** (`results/patch-4.0.0-engine3-2026-11-05`): v51d 141-115 and v51e1 140-116 against v226; against the early-pack bot v226 165-91, v51d 182-74, v51e1 190-66.
- **Repository tidy (8 Nov):** the dev line now contains `main`; old bot folders are packed in `archive/`; `maps/` is the 128-map pool; raw panel summaries are gzipped; `results/`, `bots/` and `docs/` have index files. Details in `docs/README.md`.

## Update, 8 November 2026 (engine and public repositories)
- Default `cambc` upgraded from 4.0.0 to **5.0.0** (the latest on PyPI; engine 3.0.0 = patch 4.0.0). No patch newer than 4 Nov exists.
- The tournaments feed shows the International Qualifiers were double elimination, 21 games per match, seeded by the ladder at the lock (3 Nov 23:59). The UK qualifier is not listed yet: event 11 Nov and lock 10 Nov are from earlier notes, **the lock hour is unconfirmed**. Tournaments use maps outside the ladder pool.
- Second public-repository review: `results/public-insights-2026-11-08/README.md`.
