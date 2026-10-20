# Additional field research: MIT Battlecode past years

20 October2026. Added from the supplied [official past-years index](https://battlecode.org/past.html). This is a separate game series from our Cambridge2026a champion game. Do not add its repositories to the count of current-game opponents.

## Sources actually reviewed

| Source | Observed lesson | Our proposed transfer |
|---|---|---|
| [2025 Just Woke Up postmortem](https://battlecode.org/assets/files/postmortem-2025-just-woke-up.pdf), physical pages2,7–10,20–23 | Authors describe state-based organization, retaining a return location after refilling, broad map comparisons and the limits of self-play. They caution that borrowed algorithms require understanding. | Keep a bounded intent through a useful reset, then revalidate its target; use independent opponent styles and inspect failed decisions. Avoid a large navigation rewrite before measuring its cost. |
| [2026 Generalized Stroke's Theorem postmortem](https://battlecode.org/assets/files/postmortem-2026-generalized-strokes-theorem.pdf), physical pages2–3,6–9 | Authors separate state selection from behavior execution, study stronger teams' macro and inspect individual combat decisions. They evaluate feasible local action combinations and describe budget tradeoffs. | One explicit decision layer with retained state; for combat enumerate a small set of legal action sequences with end-position threats. Validate those against our movement/cast restrictions. |
| [2024 muskellunge author account](https://dteather.com/blogs/battlecode24/), Strategies / Things to Improve | Escorts could obstruct their carrier; too much defense reduced attacking capacity. They also report specialization imbalance and passive standoffs. | Cap escort commitment, reserve the carrier's route, and measure lost farm opportunity. Test retreat/hold deadlocks. Flag passing and duck specialization are not Cambridge mechanics. |

These are author accounts, not causal proof that any single feature produced their finish. Only the selected sources were reviewed here; the archive spans many more years and this is not a claim to have analyzed its entire history. Tournament video links were identified, but videos were not watched in this pass.

## Source-code spot checks

We read three files, without copying them into the drafts:

- [battlecode-archive/2025-Just-Woke-Up — v57_Optimaler/Robot.java](https://github.com/battlecode-archive/2025-Just-Woke-Up/blob/main/java/src/v57_Optimaler/Robot.java), blob `95ce306a99f61e08c1bdddd530c4162b826be6a5`: an abstract per-unit turn loop, persistent returnLoc/map/comms objects, and action helpers that return whether an action was legal and issued. This file is a snapshot, not proof of the exact finals artifact.
- [uravt/Battlecode26 — Version41/StateUpdater.java](https://github.com/uravt/Battlecode26/blob/main/src/Version41/StateUpdater.java), blob `daac66c08d3f667584731574ef143adc5cb4b4ee`: an explicit behavior-selection interface.
- [uravt/Battlecode26 — Version41/DefectBRStateUpdater.java](https://github.com/uravt/Battlecode26/blob/main/src/Version41/BabyRatStateUpdaters/DefectBRStateUpdater.java), blob `7e30bb178ac63df6fc35f9cebad53484978e3c04`: ordered choices for distress/combat, reporting, formation, resource work and exploration. Disabled branches are visibly commented out. Repository-to-finals-submission correspondence was not established.

The [unofficial Battlecode Archive](https://github.com/battlecode-archive), linked by the official index, is a further source directory. Presence there does not certify rank, correctness or direct compatibility.

## How this changes the implementation recommendation

It reinforces a small sequence: measure a decision failure; give the chosen job an explicit lifecycle; evaluate legal action sequences; retain productive context through a reset; verify on independent strategies. It does not justify importing MIT action rules, numerical thresholds, communication limits, or a whole historical controller.

The four original C++ drafts in this folder implement parts of that proposal. The remaining experiment is a bounded tactical action selector. Build that only after measuring the current v21a fight-back trial: include legal stay/attack, move/attack, cast/move and escape options appropriate to each kit, recheck legality before execution, and compare score earned plus damage/risk and the job time surrendered. No engine performance is claimed here.
