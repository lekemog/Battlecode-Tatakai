# Experiments for Claude / Tatakai
These are proposed tests, not completed gameplay experiments. Parent baseline: v50c at 2d93a142df388db48596f82842cf7cca47809cec. Keep PR #50's history repair as an explicitly labelled optional baseline, not an unrecorded prerequisite. Source review and transfer mechanisms are in README.md.

## Run order and isolated arms

| ID | Priority | Narrow change / code boundary | Diagnostic | Stop condition |
|---|---|---|---|---|
| W0 | First | Extend existing FuelTrace and decision counters; no intentional policy change | Phase fuel, cache hit/invalidation, useful-action gaps, duplicated assignments; instrumentation overhead | Excessive observer effect or any unexplained behavioural change |
| W1 | High | Dependency-stamped carrier route cache at Brain::ring_gate/handle_tribute; preserve route scoring | Cache age, stale-input use, rebuild fuel, successful deposits | Reproduce carrier-route regression or stale cache reused after invalidation |
| W2 | High | Stable ETA/ID ownership only for one-champion camp tasks; preserve hard-camp team requirements | Duplicate capture travel, surplus allies, late/abandoned hard camps | Reduced duplicates accompanied by missed valuable objectives |
| W3 | Medium | Existing choose_target bound audit, then optional bound/candidate reuse optimisation | Bounded choice versus exhaustive frozen-snapshot oracle; evaluated candidates/fuel | Any invalid bound or different selected best candidate beyond declared ties |
| W4 | Medium | Small incremental connectivity/clearance job; initially diagnostic-only | Completed/partial state, per-slice fuel and relevance to altar access | Optional work prevents mandatory actions or partial results treated as valid |
| W5 | Medium | Carrier exposure term in existing route penalties/tribute policy, independent of W1 | Submitted gems, time exposed per bag, avoided/accepted contest costs | Broad middle-map surrender or no conversion improvement |
| W6 | Exploratory | ID-varied safe recovery on true non-progress; existing bans expire on changed dependencies | Repeated ally contention, recovery latency, false stall triggers | Interrupting channels/captures/waits or unsafe random displacement |
| W7 | Later | Narrow economic interception score in existing combat/tribute-lock decision | Enemy deposit denied minus our farming/deposit opportunity cost | Long low-value chases, bag losses or dependence on unknowable enemy state |

W1 replaces neither the entire World cache nor the combat model. W2 is not a full-team assignment rewrite. W3 starts as a correctness audit because v50c already has upper bounds. W4's geometry must reflect actual legal movement; it is not a port of old cardinal Voronoi settings. W5 and W7 are policy changes with no inherent correctness claim.

## Essential invariant checks
1. A cache hit with unchanged dependencies returns the same answer as recomputation. Moving/revealing an occupant, changing relevant camp accessibility, death/respawn, channel changes and generation wrap invalidate appropriate entries; unrelated events do not rebuild static geometry.
2. Equal-ETA actors choose a stable winner for a solo task. Different local views converge when information becomes shared. Cooperative camps retain sufficient damage/health and legal group IDs.
3. Every evaluated score is at most its asserted bound under each enabled reward/learned/ring feature. Compare chosen target with exhaustive scoring on reachable/unreachable and high/low reward snapshots. If a factor cannot be bounded, disable pruning for that factor.
4. Optional jobs always retain a valid cursor and generation, discard stale partial results, terminate on exhausted/unreachable work and fall back safely when incomplete. Check worst-case cost of a single step; a pre-call budget check cannot bound an unbounded call.
5. Recovery distinguishes distance non-progress from valid waiting, channeling, capture, stun and recall. Test narrow corridors, ally swaps, repeated rejected moves and target deletion.
6. Packaged observations use legal API data. Missing sightings remain uncertain, not invented exact enemy positions.

## Evaluation stages
- First validate invariants with focused tests. These must exercise semantic boundaries, not mirror source statements.
- Reproduce PR #51's original 560 cases per policy across 70 layouts, three archived implementations plus v50c, both sides. This is a regression gate and establishes comparability with the prior result.
- For serious policy selection, add strategically different current-season snapshots. h_apex and h_photon already exist in our bench tree and can be assessed for compatibility and difficulty; neither is assumed strong until measured.
- Freeze fresh seeds using the documented engine interface where available and meaningful. If the game remains deterministic, repeated runs are not new independent samples. Burning fuel changes the policy budget; do not label that an independent equivalent seed.
- A planned extension with 70 maps × 4 opponents × 2 sides × 3 valid distinct seeds is 1,680 cases per policy. This is a proposed budget, not an already supported/verified seed configuration or a claim of independent observations.
- Stratify by reachable altar count, camp density/reward concentration, travel distances and bottlenecks before looking at candidate outcomes. Withhold families for policy selection and leave an untouched final seed/opponent set. Existing inspected maps are not new blind validation.
- Review both converted losses and newly lost wins. Keep full expected denominators, errors, bot faults, fuel events, per-side results and worst-family regressions. Whole-map paired resampling may describe sensitivity; it does not correct unlimited candidate search or weak opponents.

## Interactions worth testing after isolated arms
W1+W5 tests whether valid routes make exposure estimates actionable. W2+W4 tests whether topology improves assignment enough to cover its fuel cost. W2+W6 tests whether ownership reduces recovery contention. Test each combination against its constituent arms and the same baseline; reject combinations that merely shuffle wins between maps.

Do not repeat the previous three-way bundle as an assumed upgrade. It converted 20 baseline losses and lost 21 baseline wins in the prior suite. Do not remove learned adjustments: the existing ablation lost 29 net wins. Freeze parameter choices before held-out outcomes, and log every attempted configuration.

## Handoff contract
Use a separate branch and new candidate folder for each arm. Include source/engine/map hashes, seed semantics, changed functions, invariant results and a per-game comparison with any PR. Follow START_HERE_AGENTS.md's submission ownership: no direct submission or scrim-quota consumption from this research. Ask the submission owner to arrange paired strong-opponent evaluation through the repository workflow. No bot code or live slot is changed by this documentation PR.
