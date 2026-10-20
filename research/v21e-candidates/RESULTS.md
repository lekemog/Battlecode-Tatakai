# v21e: four isolated local experiments

Our team: **Ben, Kurian, Leke and Szymon**. This implements the split requested in Issue #33.

## Decision

Local gate passed: **none**. None meets the agreed retention rule; retain v21e as the benchmark control. Passing requires more wins on both frozen panels and zero reported own bot faults. Any combined policy needs its own comparison.

## Complete panels

cambc2.2.4, release mode, 17 maps × both sides × five opponents per set. **1,700 completed games**: 340 baseline and 340 per candidate. Same map hashes, engine build and seeds were checked for each candidate/baseline pairing. No submitted bots or platform match groups were created.

| Bot | Tuning wins | Held-out wins | Tuning mean margin | Held-out mean margin | Own bot faults | Local gate |
| --- | --- | --- | --- | --- | --- | --- |
| v21e | 127/170 | 137/170 | +332.56 | +358.58 | 0 | control |
| cg_cycle | 131/170 | 135/170 | +349.75 | +376.57 | 0 | reject this candidate |
| cg_task | 133/170 | 137/170 | +357.83 | +374.10 | 0 | reject this candidate |
| cg_capture | 119/170 | 117/170 | +243.44 | +240.56 | 0 | reject this candidate |
| cg_siege | 126/170 | 139/170 | +327.26 | +366.63 | 0 | reject this candidate |

Margins are **per-game submitted-gem differences**. The earlier +1663 baseline figure is the sum of the five opponent means: 5 × +332.56 = +1662.82, rounded. It is not a different baseline result.

The disabled adapter control compiles to the **same release Wasm bytes as v21e**: SHA-256 `a569e467d5c1184d7f2a50e1016113050be7a03811109667319da12d99fc277e`. All four release builds and native strict C++20/UBSan policy checks passed.

## Paired changes

| Candidate | Panel | Loss→win | Win→loss | Mean margin change |
| --- | --- | --- | --- | --- |
| cg_cycle | tuning | 14 | 10 | +17.18 |
| cg_cycle | heldout | 9 | 11 | +17.99 |
| cg_task | tuning | 12 | 6 | +25.26 |
| cg_task | heldout | 8 | 8 | +15.52 |
| cg_capture | tuning | 7 | 15 | -89.12 |
| cg_capture | heldout | 5 | 25 | -118.02 |
| cg_siege | tuning | 0 | 1 | -5.31 |
| cg_siege | heldout | 3 | 1 | +8.05 |

These are deterministic matched scenarios, not a random sample of the ranked population. A small panel gain does not establish ladder strength. The earlier health-build ordering failure remains relevant.

## Opponents

| Panel | Opponent | v21e | cg_cycle | cg_task | cg_capture | cg_siege |
| --- | --- | --- | --- | --- | --- | --- |
| tuning | x_daniel7 | 20/34 | 18/34 | 23/34 | 18/34 | 20/34 |
| tuning | x_simon6 | 21/34 | 21/34 | 23/34 | 19/34 | 21/34 |
| tuning | x_jame4 | 27/34 | 28/34 | 28/34 | 26/34 | 27/34 |
| tuning | x_tarotsq21 | 26/34 | 31/34 | 26/34 | 25/34 | 26/34 |
| tuning | x_tarot16 | 33/34 | 33/34 | 33/34 | 31/34 | 32/34 |
| heldout | h_mohnish | 24/34 | 24/34 | 23/34 | 18/34 | 24/34 |
| heldout | h_deysag | 16/34 | 16/34 | 18/34 | 12/34 | 17/34 |
| heldout | h_vatsal | 31/34 | 29/34 | 31/34 | 27/34 | 32/34 |
| heldout | h_photon | 33/34 | 33/34 | 32/34 | 32/34 | 33/34 |
| heldout | h_apex | 33/34 | 33/34 | 33/34 | 28/34 | 33/34 |

Public repository names do not establish ranked team identity or top-100 strength. Frozen paths/blobs are in opponents.json; opponent sources were used locally and are not committed.

## Map results

Each cell combines tuning and held-out opponents: **20 games/map**. This is the complete map table, including both gains and regressions.

| Map | File | v21e | cg_cycle | cg_task | cg_capture | cg_siege |
| --- | --- | --- | --- | --- | --- | --- |
| rows | p_25d81311.map26a | 20/20 | 20/20 | 20/20 | 19/20 | 20/20 |
| collision | p_2e9820ee.map26a | 15/20 | 16/20 | 15/20 | 6/20 | 15/20 |
| monolith | p_3991a8b3.map26a | 13/20 | 17/20 | 14/20 | 8/20 | 13/20 |
| contest | p_3a5c2468.map26a | 5/20 | 5/20 | 5/20 | 5/20 | 6/20 |
| eight | p_3e2df5be.map26a | 17/20 | 16/20 | 18/20 | 14/20 | 17/20 |
| ambush | p_699c96a0.map26a | 17/20 | 20/20 | 18/20 | 18/20 | 17/20 |
| pilgrimage | p_7bfc2edd.map26a | 15/20 | 15/20 | 16/20 | 17/20 | 15/20 |
| expanse | p_81929320.map26a | 14/20 | 14/20 | 14/20 | 14/20 | 14/20 |
| lanes | p_93852276.map26a | 16/20 | 16/20 | 18/20 | 16/20 | 16/20 |
| fragment | p_9925f416.map26a | 16/20 | 17/20 | 16/20 | 15/20 | 16/20 |
| packs | p_b135e0fc.map26a | 16/20 | 13/20 | 15/20 | 15/20 | 16/20 |
| interlock | p_b777c8c8.map26a | 19/20 | 15/20 | 19/20 | 15/20 | 19/20 |
| elkring | p_bb12893c.map26a | 19/20 | 19/20 | 19/20 | 19/20 | 19/20 |
| rushbait_v2 | p_df22386f.map26a | 11/20 | 13/20 | 9/20 | 5/20 | 11/20 |
| corners | p_e3c29b68.map26a | 13/20 | 13/20 | 15/20 | 12/20 | 13/20 |
| stampede | p_f2b6903f.map26a | 18/20 | 17/20 | 19/20 | 18/20 | 18/20 |
| swirl | p_f930f43f.map26a | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |

## Early execution measurements

Mean **candidate minus baseline** at sample 150 of the engine’s round timeline, using only pairs where both games contain that sample. Gold and deaths are summed over our champions; banking is submitted gems. These measurements describe associated changes; they do not prove the cause of a win.

| Candidate | Panel | Common games | Gold earned | Gold spent | Deaths | Gems collected | Gems banked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cg_cycle | tuning | 170 | +30.03 | -24.88 | -0.13 | +5.95 | -5.19 |
| cg_cycle | heldout | 170 | +30.35 | -9.71 | -0.26 | +5.28 | -1.47 |
| cg_task | tuning | 170 | +14.59 | -3.35 | +0.02 | +2.86 | +0.38 |
| cg_task | heldout | 170 | +8.03 | +4.24 | +0.04 | +2.46 | +2.13 |
| cg_capture | tuning | 170 | -15.97 | -38.12 | +0.18 | -1.04 | -4.04 |
| cg_capture | heldout | 170 | -13.65 | -16.06 | -0.08 | -4.02 | +0.28 |
| cg_siege | tuning | 170 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |
| cg_siege | heldout | 170 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |

## Interpretation and next changes

**Our recommendation:** test the task-memory repair separately next. Task state is the closest candidate, but its held-out gains and losses cancel; rushbait falls from 11/20 to 9/20. Cycle scoring improves monolith (13→17) and ambush (17→20) while losing interlock (19→15) and packs (16→13). Its extra early gold is accompanied by lower early spending in both sets, so income alone has not established faster useful power. These are paired observations, not proof of one cause.

**The central weakness remains:** contest is 5/20 for the baseline, cycle and task candidates, and 6/20 for siege. These public-bot games do not replace the top-100 audit, but none of our four changes resolves that map. Centre income/control remains in main Claude’s separate queue.

- **Cycle:** tests occupied-body cost, travel/respawn overlap, selective recipients and fractional recovery inside the existing pack controller. It retains the parent’s safety gates and gold weight. Assigned living squad members are an approximation of workers; recovery and future helper release are estimates, not measured promises.

- **Task:** tests observed versus unknown camp knowledge, bounded capture progress/holding, and a death reset together as one execution-policy change. A gain does not isolate which of those repairs helped. The next ablation should separate memory from capture/death state.

- **Capture:** this implementation rejects every carrying champion during election. **Static failure case:** if all locally eligible champions carry a small bag that does not trigger bank(), no new owner is eligible, so the reward can remain unclaimed. This is a code-level counterexample, not a demonstrated cause of every lost match. A follow-up should allow non-channeling small-bag carriers, then compare on a fresh panel; do not retain this candidate merely because one map improves.

- **Siege:** safe firing goals and immediate kill→capture are bundled. Empty safe sets preserve the melee approach. Movement goals do not prove the entire path safe, and only visible threats are modeled. Separate final-kill completion from safe-position selection before attributing a result to geometry.

A concrete **untested** capture repair is provided in [followups/capture-small-bags.patch](followups/capture-small-bags.patch): remove `c.gem_count()>0` from both owner invalidation and candidate rejection, retaining recall/submit invalidation. bank() still runs first; a small bag alone should not invalidate a productive capture owner. The patch passes `git apply --check` and was not applied to the measured snapshots.

## Replay review queue

Examples below select the largest absolute margin change among outcome flips for each candidate/panel. Full paired outcomes, hashes, seeds and round counts are in paired-games.csv. Reproduce a row with its two bot folders, map and side using cambc run --release; raw local stats/replays are retained under results/<bot>/.

| Candidate | Panel | Flip | Opponent | Map | Our side | Old margin | New margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cg_cycle | tuning | gain | x_jame4 | ambush | B | -274 | 904 |
| cg_cycle | tuning | loss | x_jame4 | stampede | B | 840 | -720 |
| cg_cycle | heldout | gain | h_deysag | fragment | A | -624 | 648 |
| cg_cycle | heldout | loss | h_vatsal | pilgrimage | A | 372 | -880 |
| cg_task | tuning | gain | x_jame4 | ambush | B | -274 | 694 |
| cg_task | tuning | loss | x_tarotsq21 | stampede | A | 1080 | -360 |
| cg_task | heldout | gain | h_mohnish | stampede | B | -720 | 720 |
| cg_task | heldout | loss | h_photon | contest | B | 400 | -400 |
| cg_capture | tuning | gain | x_jame4 | eight | A | -326 | 810 |
| cg_capture | tuning | loss | x_tarot16 | collision | B | 882 | -742 |
| cg_capture | heldout | gain | h_mohnish | fragment | B | -422 | 696 |
| cg_capture | heldout | loss | h_deysag | eight | B | 766 | -1014 |
| cg_siege | tuning | loss | x_tarot16 | contest | B | 400 | 0 |
| cg_siege | heldout | gain | h_apex | contest | A | -800 | 200 |
| cg_siege | heldout | loss | h_apex | contest | B | 400 | 0 |

## Reproduction and provenance

See README.md, opponents.json, comparison.json, paired-games.csv and the five freeze JSON files. Parent commit: `76d0d2617c58a2fce8d8130a513ea26383ef60ef`. The parent tuning result reproduced Claude’s 127/170, including 20/34 vs Daniel7. Exact public snapshots are pinned here; equality with Claude’s unpublished original opponent revisions is not claimed.

No source drift was detected during these runs. All 151 opponent source imports were verified against their public Git blob plus the measured final-LF normalization. Raw match statistics/replays are generated locally rather than committed. Candidate source and result snapshots remain reviewable on this branch.
