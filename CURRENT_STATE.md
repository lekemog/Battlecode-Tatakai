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
