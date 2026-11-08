# UK top-six delivery plan — 5 November 2026

## Goal and strategy
Move from the observed UK 13 / 1966 Elo toward UK top six (sixth currently 2113), by reducing avoidable losses across map families and beating the UK teams around the cutoff. Elo is an outcome, not a development metric or guarantee.

The largest operational gap is fragmented source-of-truth: main is stale while newer gameplay, test tools and reports live on different Claude branches. This cleanup gives one dated navigation entry and task board without merging unvalidated bot code.

## Four teammate work lanes
| Lane | Claim / existing work | Deliverable |
|---|---|---|
| Integration and patch qualification | #71; latest patch report; PR #70 | Verify baseline/live slot; finish v51d early-pack and pinned UK-panel tests; promote/revert with a manifest |
| Map strategy and economy | #73; #55/#57/#59/#60, #47 | Family owners; early camp value, route and bank timelines; isolated general-feature improvements |
| Combat and carrier safety | #54/#58/#62/#66/#67, #46 | Unsupported travel/repeat-death diagnosis; small-bag/guard routing interactions; bounded recovery preserving contested objectives |
| Runtime and code quality | #72, #48, PR #50 | Stale history repro; action-success/progress audit; fuel profile; demonstrated redundant/dead paths removed safely |

Teammates claim lanes voluntarily with name/branch. One integrator coordinates windows; no duplicate panel runs. Draft/shop is shared analysis after the patch baseline, with #69 controls reproduced before any Cassi-and-Issac conclusion.

## Priorities before qualifier lock
**First work block:** inventory current engine/build/maps/live submission and finish Claude's pending v51d tests; baseline each critical map family. Refresh reports for the new 04* pool. Reproduce zero-bank, stuck or unsupported approach cases under engine 3.0.0 before fixing.

**Next work block:** one runtime correctness candidate and one banking/economy candidate in parallel work lanes. Measure useful champion-rounds, gems collected→banked, early income, repeated deaths, route progress and fuel. Reassess old grave/regroup/count proposals rather than rebuilding the rejected v50j1 bundle.

**Then:** two pinned UK opponent/map panels, including cutoff ranks 4–10 and top-three stress cases. Keep older global panels as additional tests, not the UK objective proxy. Test individual arms, then their combination on identical cases. Preserve a final untouched opponent/map split.

**Before lock:** recheck official deadline/time, refresh ladder/cutoff and map pool, choose a validated stable bot, smoke all maps, confirm live upload/activation, log source/build/submission and rollback target. Freeze risky changes early enough to recover. No exact lock-hour assumption in this plan.

## Champion straying and wasted-work protocol
For each loss inspect the last 10–30 rounds before first death, lost bag or stalled objective. Record champion role, target, route distance, allies/enemies within relevant reach, legal moves/abilities, HP, bag size, state and action return. Classify: legitimate solo farm, escort separation, unsupported advance, respawn re-entry, chasing, unreachable target, repeated failure, valid channel/wait or fuel interruption.

An isolation ratio alone is not causal evidence. A change must reduce unsupported exposure without sacrificing uncontested farming or central access. New release traces must include their own overhead. Treat offline omniscient replays as diagnostics; production decisions use legal observation/aged beliefs.

## Map strategy
Use overlapping features: resource poverty, gem-only, monolith/altar access, open races, congested central objectives, narrow routes, map size and team size. Use existing mapfamilies tooling but refresh features/hash coverage to all 128 reported layouts. Named weak maps are repro cases, not hard-coded strategy selectors.

For each family compare target value per champion-round, first bank, collection vs conversion gap, respawn waiting, duplicate work, item affordability and race/tiebreak behaviour. Prioritise new-map zero banking from #60 and gem-only maps, while retaining open-race controls. Generalise by features and show counterexamples; reserve holdouts before tuning.

## Patch and candidate policy
Read the 4 November patch table in CURRENT_STATE. Retest Heart/Vesper/Vendetta/Marcella-dependent draft, fight forecast and shop assumptions; test Skirmish and Greed one at a time. Do not infer stronger draft from popularity or raw stat buffs. Preserve learned adjustments pending evidence; prior removal was negative.

v51d is a candidate, not a declared replacement for v226. Its 55.1% local mirror score and v51e1's 54.7% do not resolve stronger opponents, uncertainty or map tails. A few more mirror wins are not enough to promise a UK Elo gain. Old-engine cap-40, cohesion and draft results remain labelled historical.

## Acceptance and integration
Smoke/fault checks on all current maps; focused invariant tests for history, channel commitment, action failure and shared encoding boundaries; stress vs multiple strategically different bots; per-family/side regressions; pinned panels with baseline and candidate on identical current-engine cases. Report gain/loss pairs, margin, deaths and banking, not only aggregate win rate. Repeat on a second map set; retain error denominators.

Use the team's existing +4 wins over two strong panels/deaths-not-worse rule as a practical screening gate, not a statistical guarantee. Refresh opponent composition for the UK goal. Caution/escape is not rejected solely by mirror losses. Sequential stopping must be predeclared and validated (#63), not cherry-picked after wins.

For code cleanup, establish active-flag/call-path inventory, profile scans/allocations and compare semantic outputs before removal. Do not delete disabled experiments merely because they are off in one build. Rebuild release artifacts and run focused checks after refactoring; keep policy changes in separate commits.

## Queue hygiene
#40 is the current hub. #68 explicitly duplicates #62: consolidate there and close #68 as duplicate, retaining its evidence. #65 and #67 both proposed v50h21 for different ideas: new candidate folders must use unique owner/idea names; do not overwrite either. Keep older diagnosis issues as dated evidence until their owner confirms resolution. PR #51 and #52 are historical test/research references, not outstanding instructions to deploy.

No branches, bot versions or raw evidence are deleted in this cleanup. Further archival requires a manifest of owners, submission references and reproducibility dependencies.

## Evidence reviewed
- [Newest Claude patch analysis](https://github.com/lekemog/BattlecodeConversation/tree/03b34544c02d0e9b501183f5d1f4a60759ceec9f/results/55-patch-4.0.0/README.md), engine-3 results and pending comparisons.
- [Development log](https://github.com/lekemog/BattlecodeConversation/blob/38ab9c40551b026116672453ffc85438a352d237/SUBMISSIONS.md) and [live-slot history](https://github.com/lekemog/BattlecodeConversation/blob/38ab9c40551b026116672453ffc85438a352d237/LIVE_SLOT.md).
- [Separate bank-cap report](https://github.com/lekemog/BattlecodeConversation/blob/61c3a3f3ca90384f51309372ea449e24ab5d40f6/results/claude/bank-cap-v50m-2026-11-03.md): 168/314 old-engine cap-40 wins, explicitly modest.
- [v51d code](https://github.com/lekemog/BattlecodeConversation/tree/03b34544c02d0e9b501183f5d1f4a60759ceec9f/bots/v51d/src/brain.cpp), config, nav and entry point: selected static audit, not full runtime verification.
- Official patch-notes and UK-filtered ladder UI observed on 5 Nov; public event schedule at https://2026a.battlecode.co.uk/.
- Earlier PRs #50–#52 and open diagnosis issues listed above. No new match evidence generated in this cleanup.
