# Latest unranked series: decisions, resource conversion and missing objectives

Study date: 17 October 2026. Snapshot: the ten most recent finished unranked match groups at the start of this review. Repository baseline: `ba8d7136c2115b98eecd1ce804db4348c9845fc5`.

## Coverage and limits

The site's ten entries contain **50 individual games**. All 50 outcome overviews were inspected. The newest two groups supplied **10 own-team stdout logs, containing 1,029 decision samples**. Submitted controller and draft source were read through the platform's historical source viewer, alongside README, NOTES and CONVERSATION on main.

This is a **partial diagnostic study**, not a completed 50-game replay review. Detailed statistical summary JSON was not obtained: exports timed out and a browser observation encountered a URL protocol policy block; that download route was stopped. The visualiser reported “This application requires WebGL2”; one retry produced the same result. No animated replay was watched. The other 40 games have outcome coverage only. Do not infer deaths, camp clears, purchases or gem-loss totals from these overviews.

Raw private logs are not committed. The companion JSON contains aggregate counts, hashes, selected derived observations, intervals and all 50 outcomes. Logs are throttled to at most one message per 25 rounds per champion. Repeated labels do not establish continuous inactivity, a fixed position, failed movement, or the absence of intervening actions. Remaining fuel is measured when the log executes, not at turn end.

## Identify the tested code before interpreting the experiment

| Platform version | Submitted source inspected | Controller distinction |
|---|---|---|
| 45 | submission `3a6663ac-3981-4fbb-b9bc-4bde1e6dc73b` | Earlier shop recall: gold >=150, gems <=22 |
| 46 | submission `5752c3a9-ce8d-4b41-84c4-f1b5132eb3ab` | Baseline recall: gold >=180, gems ==0 |

In the rendered submitted `bot.cpp`, v45 has 994 lines and v46 has 993. Removing whole-line comments leaves 893 lines in each; the sole difference is the shopping predicate. Submitted `draft.cpp` line arrays match. Header and main files were not independently compared. The baseline controller and draft correspond to the reviewed `bots/v12c/src` logic; v45 corresponds to the earlier-shopping experiment described as v12h in CONVERSATION. These are platform version numbers, not repository folder names.

The live version was **47** when the Submissions page was inspected. This report does not assume v47 is v45 or v46 and does not evaluate it.

Source views: [v45](https://2026a.battlecode.co.uk/game/submissions?version=45), [v46](https://2026a.battlecode.co.uk/game/submissions?version=46).

## What the 50 outcomes establish

Both versions lost 25/25 against the same five opponent names and same map assignments. This is a difficult selected cohort, not an estimate of overall ladder win probability.

| Opponent | v45 gems across five maps | v46 gems across five maps | v45 minus v46 |
|---|---:|---:|---:|
| FRChronic | 2,844 | 2,742 | +102 |
| the uncancelables | 2,784 | 2,952 | -168 |
| tip | 2,378 | 1,944 | +434 |
| QS2 | 2,402 | 2,846 | -444 |
| KratosMessi | 3,094 | 3,350 | -256 |
| Total | 13,502 | 13,834 | -332 |

Across 25 opponent/map pairs, v45 scores more gems in five, fewer in five and the same in 15. Fourteen pairs have identical scores for both sides **and** identical duration. Identical terminal statistics do not prove identical trajectories. Opponent code versions and seeds were not independently checked, so these are matched descriptive comparisons, not a causal estimate.

Notable differences: v45 stampede vs tip 720 vs360; eight 268 vs72; fragment vs QS2 292 vs714; corners vs KratosMessi 598 vs876. There is no win-rate evidence here to promote earlier shopping. The improvement is also too narrow to address medium-sized gem bags.

## Priority 1: resource conversion can be gated off by the bag

**Confirmed sampled behaviour:** rows vs the uncancelables, match `0a6a7237-176c-4660-8c7d-d919f2ccdf27`. Slot1 logs farming target4 at rounds250,275,300,325,350 with **66 gems and270 gold** every time. Visible enemy count and aggression are zero at those five observations. HP changes from630 to430, so “the champion did nothing for100 rounds” would be an unsupported claim. At380 it logs banking with66 gems and90 gold.

Why the controller permits it, in v46 / repository v12c:

- `bank()`, lines746–755, permits a non-defensive carry threshold between60 and140. A66-gem bag can be below the computed threshold when farther from an altar.
- The shop recall at lines918–921 requires **zero gems**. Thus270 gold does not override a66-gem bag.
- v45 changes that limit only to22, so it **still excludes66**. Both versions finish this rows game at990–1056 in433 rounds.
- The same source's `log()` only reports25-round samples. We cannot reconstruct the threshold's exact value without position/altar-distance data.

The evidence supports a mismatch between **banking policy and shopping policy**, not “all losses are caused by insufficient gold.” The team can already clear and acquire a meaningful reward, then spend too long with value carried rather than converted. Rows is also close against KratosMessi:924–1023 in409 rounds for both versions. Neither close score establishes a guaranteed missed win.

**Next isolated test:** a safe conversion policy for medium bags: compare bank-first versus recall-with-bag when the actual spawn/shop/altar route reduces time to a completed purchase and tribute. Record carry age and conversion time. A global unconditional recall threshold could sacrifice farming tempo; do not promote it on a single close result. Preserve the existing v45 test as evidence that gems<=22 does not solve the66-gem case.

## Priority 2: contest has no autonomous monolith attack plan

**Code-established gap:** `init()` lines113–117 computes `siege_group` on maps without regular gem camps. Pack mode remains false there. Gameplay dispatch uses `solo_target()`; line714 skips a monolith while its reward is unavailable. The nearby monolith override at lines940–944 also requires the reward to be available. `siege_group` is assigned but is not consumed by the controller.

Consequently this path has **no intentional objective selection to clear an untouched monolith**. It can opportunistically take one someone else already cleared; it can also incidentally attack nearby monsters through combat. That is different from a planned siege.

Observed contest outcomes against the uncancelables:

- v46:0–1000 in1,329 rounds, match `46b6a7d6-1619-4df6-a625-779ce73faa2c`.
- v45:0–400 at the2,000-round limit, match `b3d4f6c2-ad26-4979-8c30-90e3fcd8298e`.

In the v46 log, slot2 samples the same farm target4 at rounds644,669,751,776,849, each with700 HP, zero gems and27 gold. These samples flag a low-progress objective worth inspecting; missing intermediate logs prevent calling this a continuous205-round freeze.

**Next isolated test:** an explicit gold-map progression from safe gold farming to team assembly to monolith siege to capture/bank, consuming `siege_group`. Require living-member proximity, current stats/health and enemy pressure rather than just elapsed time. Retain a fallback if assembly fails. Measure monolith damage, first capture, deaths and score in paired tests. A draft-only crowd-control change cannot repair an absent objective transition.

## Priority 3: profitable combat can pre-empt a carrier's scoring job

**Code-established ordering:** `play_turn()` lines916–917 runs `handle_enemies()` before `bank()`. In `handle_enemies()` lines836–843, favourable fights and chases return early. Chase eligibility considers the opponent's bag and health, but has no veto for **our own carried bag**, a winning tribute, or the opportunity cost of delaying it.

Derived log observations in v46:

| Map / match | Round / slot | Decision | Our carried gems |
|---|---|---|---:|
| packs / `c07ae63a-bc91-4d31-ad46-a585926effd1` |75 /2|chase|44|
| collision / `54798562-cecc-4cf8-918b-985633968cc5` |367 /1|chase|36|
| collision / same |592 /1|chase|58|

The collision slot subsequently logs bank at617 with58 gems. This does not establish a continuous25-round chase or prove those gems were lost.

**Next isolated test:** veto discretionary pursuit for a designated carrier when banking has higher expected score value, especially if its bag would reach1,000. Keep immediate survival and defensive attacks available. Compare extra completed tributes and lost bags, not kills alone. An expected-value model should include the value of **both** carried bags, probability of survival and the rounds until banking, not simply estimated burst damage.

## Static findings for the stall audit

These are confirmed code properties, not proven causes of the observed losses:

1. `move_to()` lines459–460 removes occupied goal tiles and immediately returns if none remain. The later terrain-only fallback at469–471 cannot help when **all goal tiles** were removed before the search.
2. The anti-stall penalty at479 checks `p==last_pos`. `play_turn()` line890 has already set `last_pos` to the current tile, and474–475 excludes that tile. This penalty cannot fire in the ordinary movement candidate loop. Merely moving the assignment does not create a useful escape policy after several stationary turns; use an explicit progress/visited-state mechanism.
3. `bank()` can log bank and return true after failed movement. Capture and chase paths also ignore some movement return values. The label reports the selected branch, not proof of successful progress.
4. The friendly-lock comment near813 says such altars are never targets, but goal construction does not remove their approach tiles. A possible self-lock no-progress path deserves a targeted local reproduction; no unlock/lock evidence in these ten stdout logs establishes that it occurred.

For a local regression harness, cover all-goals-occupied, a blocked corridor requiring a temporary sideways move, an altar with our lock, and an unreachable reward. Assert bounded progress or a timed target abandonment rather than only “the function returned.”

## What the logs do and do not say about opponent modelling

Aggression >=40 appears in sampled decisions on swirl, fragment, collision and contest; none of the sampled rows decisions are defensive. The model is therefore not simply permanently stuck in defensive posture across this sample.

| Map | Samples | Samples with aggression >=40 | Maximum sampled aggression |
|---|---:|---:|---:|
| swirl |75|14|58|
| monolith |102|0|22|
| fragment |74|20|56|
| packs |65|0|34|
| collision |82|6|46|
| contest |240|127|130|
| ambush |108|0|39|
| rows |84|0|0|
| corners |102|0|1|
| lanes |97|0|22|

These counts are **not fractions of champion turns**. Deaths, channels and throttling bias sampling. There were zero `bot error:` messages in the ten downloaded stdout files; that does not rule out silently caught SDK errors or fuel exhaustion. Remaining fuel at sampled log points ranges from14,031 upwards; no end-of-turn fuel-exhaustion claim is justified.

The poker-bot lesson still applies: infer opponent behaviour, carry uncertainty, and adapt. Here the first repair should be the decision contracts: a correctly classified opponent does not supply a missing siege transition or reconcile conflicting bank/shop gates. After those are measured, separate style beliefs from immediate local combat danger, and add hysteresis only where switch traces show harmful oscillation.

## Handoff to Claude

Recommended order: instrument resource/progress facts, test medium-bag conversion, then implement a complete contest objective transition, with carrier pursuit as a separate variant. Do not combine all changes in one candidate.

Minimal additional diagnostic fields: position, actual move success/failure, selected goal status, target camp health/reward state, carry age, global submitted score, bank-go reason and computed threshold. Existing aggression logging is sufficient to inspect the current scalar; no need to add another duplicate aggression trace.

Before promotion, obtain the missing40 logs and all detailed summaries, verify submitted source/seed metadata, inspect decisive timelines, and run side-swapped local tests plus the repository's back-to-back opponent cohort. **No bot code, live selection, submission or scrim queue was changed in this study.**
