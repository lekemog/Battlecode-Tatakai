# Pantheon / Khaos winner-code transfer review for Tatakai
30 October 2026. Research and experiment specification; no gameplay code was changed and no new matches were run for this review.

## Decision
The most useful transfer is disciplined decision making under a small compute budget: coordinate work, invalidate dependent caches precisely, and spend optional compute after essential actions. Prioritise measurement and cache correctness, then role-aware assignment. Defer the full Voronoi geometry system and a wholesale memoryless controller rewrite.

This is a code-backed architecture review, not evidence that any proposed change improves our win rate. The README identifies Pantheon as the Grand Finals winner and Khaos as its finals submission, with Lethe used for International Qualifiers. I examined Khaos runtime code, selected geometry/coordination/combat sections, test tools, and the authors' postmortem TeX. I did not inspect every historical bot, vendored geometry module or Pong hardcoding tool.

## Reproducible scope
- [Winner repository](https://github.com/HerbertTheBird/Cambridge-Battlecode/tree/daf417410854b4563898412c9b2699ac4dedc7ee), frozen commit daf417410854b4563898412c9b2699ac4dedc7ee.
- [README identifying submissions](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/README.md).
- [Postmortem source](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/postmortem/postmortem.tex), especially Memoryless Architecture, Memoization, Floodfill for Voronoi Partition, Incremental Execution and Performance Optimization.
- Tatakai comparison: bots/v50c/src at 2d93a142df388db48596f82842cf7cca47809cec. The claude/vibrant-turing-rtpcwn branch still resolved to that commit when checked. This review does not infer the live platform submission from Git branch state.
- Repository base main: 3f68e9561a3ee059759a9a6a9c78ecaee8d87ea5. Prior test evidence: [PR #51](https://github.com/lekemog/BattlecodeConversation/pull/51). Its candidate policies are not silently substituted for v50c here.
- sources.json records reviewed file paths and Git blob hashes. Immutable source anchors below distinguish observed mechanisms from our proposed adaptations.

## 1. Coordinate marginal contributions, not just destinations — high priority
**Observed:** [pathing.py, claim_subset](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/bots/Khaos/pathing.py#L106-L262) partitions candidate work using competing flood fills from one builder and its allies. It caches a base ownership partition when claims lie on the same passable graph and falls back to another calculation when blocked claim tiles change that graph. Builder states reuse these claims instead of each independently choosing the same attractive tile.

**Already in ours:** Knowledge::read_slots/recount publishes engaging/capturing destinations; score_group counts committed allies, squads, estimated damage and required team size. It already avoids joining an occupied reward capture. Simply adding “shared targets” would duplicate existing machinery.

**Proposed delta:** assign a champion to a camp only when its marginal arrival improves expected completion or safety enough to justify its opportunity cost. Estimate ETA with existing fields and legal movement capabilities; include health, damage, bag exposure and required team size. Retain enough allies for hard camps instead of applying nearest-owner exclusion globally. Cheap local ownership is appropriate for harmless one-champion captures; role-aware slots are appropriate for difficult objectives and escorts.

**Important limitation:** Khaos' self-first tie handling is not a globally consistent champion-ID tie breaker. Different local views can also disagree. Use deterministic ID ties plus short-lived commitments and test simultaneous equal-distance claims. Do not copy self-first flood-fill logic as a guarantee of unique ownership. Our six-bit group-slot encoding also limits which IDs can be represented; preserve a legal fallback rather than silently aliasing larger IDs.

**Measure:** surplus champion-rounds on completed captures, required allies arriving late, duplicated solo assignments, reassignment frequency and banked gems. An apparent efficiency gain that strands hard camps is a failure.

## 2. Cache according to dependencies — high priority
**Observed:** [map_info.py](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/bots/Khaos/map_info.py#L1787-L1873) separates structural, resource-loaded and visible derived masks, each with an explicit key. [attack.py](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/bots/Khaos/units/states/attack.py#L971-L1016) lazily computes expensive scoring data after a per-round reset.

**Already in ours:** World caches full/partial distance fields and calibrates fuel estimates; nav.cpp caches obstacles and invalidates after moves/revealed occupants. We should not replace static fields with expensive per-turn rebuilds.

**Proposed delta:** document cache dependencies explicitly. Static terrain/altar geometry can remain long-lived. Champion occupancy and threats require observation/version stamps. A carrier-specific bank route additionally depends on start position, bag/channel state, relevant camp accessibility and route progress. Replan only when relevant inputs invalidate it, with bounded work and an existing valid fallback.

This is a better hypothesis than repeating the 16-round carrier-route refresh from PR #51: that tested policy lost eight net wins and increased our fuel-exhaustion events from 23 to 30 in 560 matched cases. The new proposal has not been tested and must not inherit a positive result from the old experiment.

**Correctness rule:** invalidate or generation-stamp time-dependent observations across gaps and deaths. The separately identified health-history repair is directly consistent with this lesson. A cached answer being cheap does not make it current.

## 3. Use score ceilings where they are provable — medium priority
**Observed:** [builder.py](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/bots/Khaos/units/builder.py#L205-L245) scores states in descending declared ceilings and stops when remaining states cannot win. States cache candidates for execution. Their controller chooses a state afresh each turn, although its map memory, failure caches and opening intentions persist.

**Already in ours:** Brain::choose_target already computes camp-score bounds and evaluates promising camps until bounds or fuel stop it; choose_chained adds limited lookahead. Therefore branch-and-bound itself is not a missing feature.

**Proposed delta:** audit the existing bound against every active multiplier and compare bounded selection with exhaustive evaluation on frozen decision snapshots. For future cross-mode arbitration, keep mandatory safety/channel legality outside the optional utility competition. Only skip a mode when its ceiling is valid in the same units. A learned adjustment, conditional reward or chained bonus can invalidate an assumed ceiling.

Do not port Khaos' numerical attack/heal ceilings, discard valid channel commitments, or recompute all policy modes every turn. Cheap event-triggered reassessment plus small switching costs is a safer experiment than a complete controller rewrite.

## 4. Turn topology into useful decisions — medium priority, after profiling
**Observed:** [chokepoint.py](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/bots/Khaos/chokepoint.py#L1362-L1437) waits for map/symmetry readiness; [post_turn](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/bots/Khaos/chokepoint.py#L1918-L2011) advances named stages under CPU/headroom checks. The fuller implementation builds geometry and a Voronoi-derived graph, prunes it and extracts actionable blockers.

**Transfer:** infer altar approach width, camp/altar connectivity, detour cost and alternate escape routes from actual terrain. Use those features for escort demand, ward placement, carrier route selection and when a central objective needs a group. Begin with a discrete connectivity/clearance sketch, not the full continuous Voronoi library.

**Scale:** for V walkable cells and E legal edges, a bounded graph traversal is O(V+E); an 8-neighbour grid has E=O(V). Storing a few arrays is O(V). Computing fields for every champion and every objective multiplies cost; profile before adding them. Run a finite number of expansions per optional slice and retain a cursor/generation. Reject partial results as complete plans, and reserve fuel for essential actions. One large atomic SDK call is not made interruptible by wrapping it in a budget check.

Khaos' settings include cardinal geometry assumptions and old turret/building footprints. Our graph must follow current SDK diagonal movement, obstacles and legal abilities. Each champion's runtime cache is local unless explicitly communicated; share compact assignments/features through the permitted buffer, not an imagined global Python map.

## 5. Route around actual risk, not only distance — medium priority
**Observed:** [pathing.py bfs_move](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/bots/Khaos/pathing.py#L547-L676) uses a bucketed weighted frontier with threat and barrier costs and local occupancy checks. The postmortem distinguishes soft from hard threat regions.

**Already in ours:** nav::step_along uses distance plus a tile penalty and rechecks rejected moves. The transferable delta is a carrier-specific exposure estimate, not basic avoidance.

For bank routes, compare expected submitted value over travel plus channel time, with exposure depending on enemy reach/cooldowns, our health, bag value and available allies. Use only legally observable information or aged beliefs. Avoid blanket penalties on all contested central territory: our existing source comments record that such avoidance can surrender the middle. Do not interpret a turret's stationary threat mask as an accurate moving-champion danger model. Keep this separate from cache changes so we can attribute outcomes.

## 6. Attack economic dependencies — exploratory
**Observed:** [turret_priority.py compute_priority_sets](https://github.com/HerbertTheBird/Cambridge-Battlecode/blob/daf417410854b4563898412c9b2699ac4dedc7ee/bots/Khaos/units/turret_priority.py#L202-L289) traces resource feeders, prioritises supply to threatening/multiple enemy turrets and protects infrastructure feeding friendly turrets even if enemy-owned.

**Transfer by analogy:** rank an intercept by the banked value it prevents or recovers and the camp/altar access it opens, rather than nearest enemy or damage alone. Compare interrupting a valuable carrier's route with farming or a low-value chase. Our bot already has combat, tribute locking, sightings and escort logic, so add an economic term to a narrowly identified decision point.

Conveyor hijacking, road spam, destroying feeders and permanent turret fortifications have no direct translation to this ruleset. A dependency graph for moving champions is uncertain and short-lived, not a static supply network. Do not call this opponent modelling: genuine opponent modelling would estimate repeatable enemy behaviour from observations and be evaluated separately.

## 7. Recover from failure without synchronising the whole team — cheap experiment
The postmortem describes ID-varied stuck recovery and target-failure TTLs. Our brain already tracks distance progress, bans targets temporarily and recognises staging waits; nav also handles rejected moves. The gap to investigate is repeated contention among allies in narrow passages.

Test a small deterministic champion-ID variation only after genuine route non-progress, with safety checks and short retry expiry. Do not random-walk a channeling, stunned, capturing or intentionally waiting champion. Expire failed-target caches early when the blocking dependency changes. Their 100-round TTL and ID-derived thresholds are not appropriate defaults for our game.

## 8. Profile the whole pipeline — first experiment
The authors' postmortem reports map updates and pathing among its largest runtime consumers, and labels its profile as one map's sample. Python big-integer masks and attribute-hoisting savings do not predict C++ WASM fuel savings.

Our baseline already has FuelTrace/FuelSpike, calibrated field costs and phase reserves. Extend those measurements to p50/p95/p99 fuel by phase and map family, plus safety actions skipped, turns without useful action, cache-hit/invalidation counts and progress toward objectives. Measure instrumentation overhead in release mode; free debug-block work would distort platform-equivalent costs. Keep engine version, build hash, source, map hash, side and opponent in every record.

## Testing and promotion
Use EXPERIMENTS.md for isolated arms and interactions. PR #51 supplies a reproducible regression suite, but baseline's 415/420 against three archived opponents is saturated; it cannot establish strength against top teams. The separately recovered v221 top-ten sample is 5/50 and is not pooled with local outcomes.

Keep all 70 current layouts, both sides, fixed opponents and matched seeds. Reserve fresh seeds and map families before tuning; once inspected, a holdout is no longer untouched. Obtain stronger current-season opponent snapshots or paired live evaluation through the main submission owner. Do not treat Khaos as a runnable current-season opponent. Retain errors and expected counts; do not hide failures in a successful-game win-rate denominator. Some reviewed scripts use very small subsets, so their test sizes are not a promotion standard.

Prioritise Collision and the existing weak-map cohorts for diagnosis, but validate globally. Report paired gains AND losses, mean/tail gem margin, per-map-family outcomes, fuel events and duplicated/idle champion-rounds. Combine changes only after isolated evaluation, then measure the combination independently. Retain the learned layer: the prior learned-off diagnostic regressed by 29 net wins. Winner status and a plausible mechanism are not substitutes for our tests.

## What this review does not claim
No new performance result, opponent-strength estimate or deployed improvement. Authors' claims that memoryless decisions reduced overfitting are their interpretation, not an isolated causal experiment. The Grand Finals winner attribution is supported by the repository's README, not independently re-certified tournament standings here. The post-finals _PONG tooling is outside the Grand Finals submission scope. All proposed code should be implemented originally against our SDK with source attribution; no external implementation is copied into this upload.
