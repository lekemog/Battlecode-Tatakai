# Faux execution lab: official engine, measured variants and independent review

18 October 2026. Local testing only. Source parents read at main9e0e356ad3a29722c3db78e7af09fb6571eab54b; latest review and v19b comparison pinned to main6efc1dfd6245911fed809d7d46da3a05788b385e. Leke explicitly authorised modifications to testing bots and asked to import the engine so both main and faux execution can be studied.

## Publication update

Repository rechecked at main `2555ce4746c995b262f219823e9394f2567fee33` after publication was reauthorised. `START_HERE_AGENTS.md` now reports v19f/version131 live, with weak-map paired scores v19f10/75, v19a7/75, v18x6/75, v19b3/75 and v19c1/75. These are Claude-reported outcomes, not rerun here. The v19b engine results below describe the earlier pinned baseline and must not be presented as tests of current v19f. No v19f local comparison was run in this study. The v19b mortality-feature concern below remains a historical code finding; verify it against v19f before carrying it forward.

## Delivered and verified

Official `cambc==2.2.4` local runner installed, matching the repository SDK. WASI SDK33, CMake3.31.8 and Ninja1.12.1 successfully built release WebAssembly. The original direct GitHub toolchain downloads failed; official release archives were downloaded through the browser and verified (WASI SHA256 `0ba8b5bfaeb2adf3f29bab5841d76cf5318ab8e1642ea195f88baba1abd47bce`; CMake `630615d8e98ac33eba7fbe472626dff5c899c85af3c024585ae109166a6909d0`). The tested setup used workspace-local caches. This review package contains reproducible setup code, not the runtime caches or external SDK binaries; setup must be rerun in a fresh workspace.

The engine actually completed **366 local match executions**, covering **348 distinct source-pair/map/side/seed cells**. Eighteen screenings repeat cells in later full-map checks; they are not independent evidence. All366 have readable completed statistics. Three initial v3 build attempts failed before matches because a copied CMake cache pointed at the parent folder; generators now exclude `.cambc`. These failures are not counted as games. One eight-game journal stopped at seven records despite eight statistics files; its missing row was recovered from the existing completed statistics and explicitly marked. No match outcome was invented or rerun to fill that row.

Engine metadata in the results: version0.0.3, build `d7e29ae3546357b011419c764204b7b9e2232bdb1b07868250c6b35d4c18d2a5`. Maps and source files are fingerprinted per execution; engine seeds match within map cohorts. Four Python metric/coverage tests and native C++ policy assertions pass. Selected variants built and ran in the real release engine; syntax checks alone are not the validation claim.

`FAUX_LAB.md` contains setup, commands, role definitions, limitations and the two-way learning procedure. `tools/faux_lab.py` records both sides, keeps planned/completed/failed denominators, uses the official outcome including tiebreaks, preserves map/seed/source identity and supports replay retention. It never calls login, submit, abrun or platform match creation. `tools/export_faux_study.py` excludes commands, local paths and diagnostics from published data.

## Revision: my first broad patch was not an upgrade

The first v2 bundle corrected summed group HP, bounded pursuit, healing, bag/capture lifecycle, ban checks and siege commitment, plus some profile tuning. These are plausible engineering changes; the package still regressed. I reject it as a default replacement. Its components cannot be credited or blamed individually from a bundled test.

| Arm | Wins against original parent | Decision |
|---|---:|---|
| fz_solo_v2 broad bundle |0/8|Reject |
| fz_herd_v2 broad bundle |2/6|Reject |
| fz_hunt_v2 broad bundle |2/6|Reject |
| fz_tank_v2 broad bundle |5/6 initial;14/34 full pool|Retain only as a specialist counterexample, not a general upgrade |
| fz_solo_v3 earlier shopping |4/8|No demonstrated gain |
| fz_solo_v4 earlier health |3/8|Reject |
| fz_herd_v3 control draft |2/6|Reject |
| fz_hunt_v3 need0.45→0.85 only |4/6 initial;19/34 full pool|Promising alternative; keep original too |
| fz_herd_v4 siege150→600 only |4/6 initial;18/34 full pool|Narrow contest improvement; keep original too |

The full pool is all17 published maps from both sides. Small-map screenings were chosen by the intended behaviour (solo: corners/collision/lanes/rows; hunt: corners/eight/rows; herd: contest/stampede/rows; tank: corners/collision/eight). The later full-map checks include those screenings, so do not add their denominators. Multiple arms were tried;19/34 is provisional and does not establish superiority against a population of opponents.

No improved solo replacement passed. Preserving the original is the evidence-based choice. Rejected sources can be recreated with the versioned generators; the default suite excludes them.

## What the additional opponents catch

Against historical baseline v17w on six maps/both sides:

| Opponent | v17w wins/12 |
|---|---:|
| original herd / herd_v4 |8 /7|
| original solo |8|
| original hunt / hunt_v3 |8 /11|
| original tank / tank_v2 |9 /8|

Thus hunter_v3 beating its own parent does not make it a harder v17w opponent. Tank_v2 losing to its own parent overall does not make it useless: it exposes additional v17w failures on corners-sideB, contest-both sides and stampede-sideB. Herd_v4 exposes contest-sideA. These are local identifiers in the corresponding evidence files, not platform match UUIDs.

**Current baseline checked too:** official submissions UI showed **v123 LIVE/Active**, submission `c4bedfcc-79db-4748-b6d2-6a2dbaff239f`. Rendered controller normalised length/FNV1a32 **49525/2405946934** and draft **1981/2629334366** match repository v19b. Normalisation strips comment-only lines and whitespace. Headers/archive/build identity were not compared. SUBMISSIONS.md names v19b for v123; v122 is Cancelled in the UI. This supersedes the old v106 live observation. It does not identify every historical scrim. NOTES and Issue20 list v19a/v19b calibration work; no completed paired t2 superiority result was established by this review.

New v19b run: **84/84 completed**, v19b wins50. Same six maps and both sides:

| Family | v19b wins vs original | v19b wins vs additional variant |
|---|---:|---:|
| herd |7/12|6/12 (v4)|
| solo |9/12|No accepted replacement |
| hunt |6/12|5/12 (v3)|
| tank |7/12|10/12 (v2)|

Herd_v4 and hunter_v3 are modestly tougher against this current baseline; tank_v2 is easier here and remains an extra profile only. These results argue for a portfolio rather than globally replacing every old bot with the newest one.

For a family robustness check, pass a map/side only if the candidate beats every tested original/variant in that family. Missing games make a cell incomplete. This avoids diluting a hard counter with many easy clones. V17w passes33/48 original-only cells and28/48 expanded family cells. V19b passes29/48 original-only cells and22/48 expanded family cells. The expanded raw denominator is84 for both. The stricter check decreases by construction when more opponents are added; it is a stress measure, not independent evidence of top-100 quality. V19b and v17w differ in many components, so their comparison does not isolate the fight formula.

## Execution learning: what is measured, and what is not

Published per-side features come from official local summaries: first buyItem round, first gemSubmission round, champion death events, gemLoss event-value sum, campClear event count, distinct group IDs, earned gold, monster/champion damage, ward placements, bot-fault and fuel-exhaustion events, and gold/gems/earnedGold at timeline sample indices100/200/300/400. MaxHealth is absent from these timelines and stays null. Ended or missing timelines stay null, without substituting postgame totals.

Gem loss can include recirculating stolen gems. CampClear events are champion-attributed; distinct IDs count group coverage, not repeat clears. First purchase is not purchase delay: this run did not join item cost/affordability per owner. The data do not expose exact routes, local pursuit opportunity cost or convoy formation; those require retained replay/decision traces. No top100 routes/styles are inferred from final scores. No private bot debug logs, credentials or sessions are published.

The original faux bots are Polaris variants, not independently implemented top100 bots. Existing NOTES already reports the gauntlet falsely favoured v17i and v17x relative to external paired outcomes. The current study adds executable stress cases and transparent metrics, not a certified top100 simulator. Genuine calibration needs frozen external cohorts, matching map/pick-count/version/time, and held-out checks. Top-team item popularity and aggregate placement are hypothesis leads, not causal evidence.

## Fresh Claude feedback and one existing-issue follow-up

Read new reply `#6` comment6250631928. Acknowledge v18z's capture reset and per-carrier escort reset, rather than re-reporting the old bugs. The uncapped direct-threat tribute cancellation is now explicitly an intentional emergency exception; the old generic boundedness claim is retired. A siege wait episode still need not imply a committed objective; that distinction remains, without reopening the same queue.

**Issue20 source concern, not a new duplicate Issue:** v19b `danger_at()` also changes the inputs of the pretrained mortality model: enemy-strength sum now includes0.5focus (around984), ally-strength sum likewise (985–986), and own-strength feature9 is `(strength+0.5focus)/100` (992). The DW/DMU/DSD constants remain the older model's constants. This is broader than changing the direct fight/bank power ratio. It compounds the previously reported training/runtime mismatch and can change danger-triggered banking independently of fight selection. The referenced `tools/audit/fightcal.py` returned404 at pinned main6efc1df, so the1629-engagement analysis was not independently reproduced.

Smallest test: in a separate candidate, change only the `danger_at` feature transform back to the model's original definition, leaving v19b direct fight/threat/bank thresholds and focus-aware power fixed. Compare legal-state fixtures and the existing paired map/opponent/side cohort; record official wins/tiebreaks first, then danger values, bank delays, lost bags and fuel. Alternatively retrain and calibrate a separately versioned risk model with identical runtime features. Do not claim AUC proves causal EV or a universally optimal threshold. A local loss is a falsifiable regression signal, not something to dismiss solely because the opponent also has a weak model; external results can overturn it.

The Fullhouse lesson is to adapt to observed behaviour and retain uncertainty, not assign a universal strategy label from a score deficit. The MOBA lesson here is objective conversion versus combat opportunity cost. The bounded-search/caching lesson is to measure fuel and failed actions. These motivate the lab and fixtures; none establishes a performance claim without the recorded tests.

## Ownership and next use

Publication targets `chatgpt/faux-execution-lab-20261018`. The initial upload was rejected without explanation; Leke explicitly reauthorised publication before the retry. Selected new folders are fz_herd_v4, fz_hunt_v3 and fz_tank_v2. Existing bot folders, main and teammates' work are preserved. Engine setup is reusable through tools/setup_faux_lab.py; local execution needs no platform account. No ladder submissions, platform scrims, merges or live changes were made. Main Claude retains platform ownership. Use the current v19b suite result as the next local reference, not the historical v17w score alone.

