# v66i: Heart + Cassi/Issac core, role execution and map flex

Source freeze: `65e10501953a578445b27399eae9d13d9dad0f68`.
Base: `bots/v66i` at `5d282cec10e87be370b86ecae46fb056a31e5dae` on PR81. Leke identifies this as the latest live bot. The source is verified; CLI session is unauthenticated, so the active account submission was not independently read. Original v66i and other owners' folders are unchanged. No live upload or activation.

## Preserve the new base

v66i keeps v61j's map/fuel/banking fixes and adds an opening phase before round200: gem weight×0.3 and hazard threshold0.12. Those gameplay changes remain intact. The draft model's early gem heuristic is4×the configured phase multiplier, not a fitted or exact copy of the gameplay target score.

## Core and variants

Heart and Cassi/Issac are **two draft choices, three physical champions**. Every experimental draft and its fallback requires both on3/4/5-pick maps; the remaining1/2/3 slots are the flex budget. A five-pick team therefore has six bodies. Do not compare its raw individual-death total as if it had the same number of bodies as the baseline; linked deaths still remove two bodies at once and are a real cost.

| Folder | Mechanism |
|---|---|
| `cg-hci66-draft` | Fixed Heart, pair, Marcella, Vendetta, Varg prefix by size; Cassi camp-strike prerequisite, no added pair roles. Control. |
| `cg-hci66-role` | Same draft plus pair safety/shared camp intent/regroup and shared accepted-fight focus. |
| `cg-hci66-map` | Roles plus broad map search. Diagnostic variant: extra ranged kits still lack full carry/support integration and retain base-specific farm behavior. Not the preferred next development base. |
| `cg-hci66-flex` | Roles plus constrained map search: only Ryth, Marcella, Vendetta, Varg and Ren may fill flex slots. Cassi supplies the dedicated ranged caster role. Avoids relying on unfinished additional ranged/support roles. |

The fixed control's3-pick team is Heart/pair/Marcella;4 adds Vendetta;5 adds Varg. All variants use literal drafts (`draft_learned=false`). The map variants preserve this configured priority within their selected set, beginning Heart then pair. All logging/config flags are frozen for tests.

## Roles implemented

- **Heart:** ordinary farming/health/banking remain. In an accepted fight, prioritize a visible enemy threatening Cassi when close enough to help. Existing kit-aware shield and stunning-dash execution handles the chosen focus. No permanent bodyguard follow tax.
- **Cassi:** use the shared focus rather than an independent random victim. Prefer her actual range4 stun against a diver/channel unless the damage spell estimates a finisher, respecting readiness, immunity and movement exclusivity. Attempt legal basics/casts **before** considering an escape walk. Query `can_move()` after acting; do not assume walk/basic allowances are symmetric. Existing generic spell selection supplies the damaging spell. No assumed AoE, shield or heal.
- **Issac:** attack/reset, then make a bounded step toward the local focus inside the carry leash. Do not spend his short non-damaging dash to initiate through this handler; inherited retreat/travel dash logic remains.
- **Pair:** share currently visible live-camp intent; Issac adopts Cassi's nearby living target. Do not adopt reward/capture waits. Calm regroup is limited to four successful steps across a5–8 tile gap; blocked movement releases to normal policy. Stale positions expire after three rounds, and a dead partner clears memory. Either partner below35%HP triggers retreat under contact or a safe recall. A healthy body can therefore react to the vulnerable body instead of independently committing.

All new offensive positioning is inside the original favourable/not-doomed/hazard gate. Pair emergency can preempt a fight to retreat; it never initiates one. No new global shared-memory layout: use existing camp-intent slots and per-instance recent partner state.

## Opening-budget map planning

The first draft turn's100× budget computes ally/enemy terrain fields, reachable resources, camp HP/damage, clustering, capture cost and respawn value. It screens every composition admitted by required-core, allowed-pool, frontline and ranged-body constraints, refines a shortlist using more camp representatives, and caches it for later ordinary-budget picks. Committed choices are always retained. An incomplete search returns to the fixed core draft. Versioned draft-memory records fit the available capacity. No map names/hashes, randomness or diversity quotas enter selection. Opponent-reactive re-ranking is disabled.

Broad core:256/256 two-round scans passed, max28.23% of initial fuel,3/4/7 distinct sets for3/4/5 picks. Constrained flex:256/256 scans passed, max15.97%,2/3/2 distinct sets. All512 scans keep Heart and pair and complete their expected screens with no logged turn errors/fallbacks. These are truncated draft checks, not512 full games or strength evidence.

The constrained model is small enough to score all its admitted flex combinations within the100× budget; spending the rest simply to consume fuel is not an objective. The analytical score estimates income and survivability; it does not simulate a complete RTS game or prove an optimal draft.

## Top-team evidence and prior experiment

[PR85](https://github.com/lekemog/BattlecodeConversation/pull/85) preserves the completed earlier v245 experiment separately. We decoded50 stored engine3 top-ten-panel summaries: all10 opponents vary unordered composition within at least one draft size; the best fixed set per team/size matches34/50, leaving16/50 requiring another set. Five maps/team are insufficient for a population rate or map-causal claim.

The updated Franklin handoff additionally reports a3,885-game study: usually one composition per map (57–63 maps with one set,0–4 with several) and little revealed-opponent reaction in testable cases. This larger result is repository-reported, not reconstructed from raw ranked lists in this session. It supports stable core/map flex rather than arbitrary rotation. The new candidate disables reactive picks accordingly.

## Gaps requiring further work

- No atomic pair health/retreat broadcast through fog. Health/position memory can be stale and recalls/banking are not fully synchronized.
- This is not a complete Cassi camp-admission/tanking optimizer. Camp adoption and the inherited safety evaluator can still let a vulnerable body take unsafe exposure. Pair dying rates remain high in the measured screen.
- Current stun priority checks immunity, not remaining stun duration; overlapping Heart/Cassi control can be wasted.
- Map utility uses starting kits, aggregated team camp DPS and simple recovery costs. It lacks upgrade trajectories, exact per-body tanking/turn order, collision, future route schedules and calibrated role-execution costs.
- The constrained pool deliberately excludes Vesper/Stellar/Tavi/Prism/Willow as flex until their individual execution is validated. Their omission is a capability constraint, not a claim that they are intrinsically weak.
- Fuel exhaustion remains substantial on full games. Draft fuel is comfortably bounded; ordinary gameplay must be profiled on heavy maps before qualification.
- The160 complete games reuse an eight-map development screen. No all128-map strength qualification, transformed/unseen geometry or current real-opponent panel was run for these v66i candidates.

Next gates: profile fuel/death traces first; isolate shared focus, pair recall and camp admission; confirm the surviving variant on the remaining120 maps and transformed boards; then follow the coordinated pinned real-opponent panel process. No promotion recommendation from this screen.
