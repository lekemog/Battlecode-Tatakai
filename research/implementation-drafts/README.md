# Polaris implementation drafts for review

20 October 2026. Original C++20 sketches, informed by our field research. These are **SDK-independent policy components**, not a runnable cambc bot or a patch already integrated into v21a. They make the proposed behavior concrete without pretending that adapter calls, budgets or performance are verified.

## My recommendation

Implement complete-cycle farm selection first, then explicit task outcomes and reliable capture ownership. Keep the current fight-back trial separate. Add siege geometry once ordinary farming and delivery are measurable. Defer a larger opponent-style classifier until these execution contracts work.

The latest #33 follow-up reports 592 ranked games (294 wins / 298 losses). In its loss cohort, team gold at round150 is680 versus758 and deaths13.5 versus6.0. These are Claude's reported aggregates, not a new causal analysis: early deaths can cause income loss and income loss can cause later deaths.

Reviewed baseline: main `bots/v21a/src/bot.cpp`, blob `56259f5ae3c793ee0f3ffe15614ab5b253284aa9`; header `be3148af52ce282ae136ad87545d395db6ccfe1d`. Resolve the accepted baseline again before integrating; START_HERE's live-version description is older than #33.

## 1. Complete-cycle selection: cycle_score.h

Current `choose_group()` charges only0.15 times altar distance, and `solo_target()` charges0.3 times it. Solo also uses straight-line distance to the group center rather than the terrain field used by pack selection. This can misrank work, but an observed score mismatch is not proof that it caused a match loss.

My first candidate would keep draft, builds, mode, eligibility gates, combat and banking unchanged. It would replace target ranking only after recording old/new scores in a shadow trace. Log groups rejected before scoring: a scoring improvement cannot rescue candidates removed by role/safety/side/wait filters.

`score_cycle()` estimates reward per occupied champion-round:

```cpp
// Adapter sketch: these inputs must be built from the selected group's legal facts.
polaris_draft::Cycle job;
job.travel = path_rounds;                 // terrain-aware, not center distance
job.ready_in = observed_respawn_wait;     // overlap with travel
job.clear = measured_clear_rounds;
job.capture = capture_remaining;
job.workers = participating_workers;
job.capturers = capture_participants;
job.carriers = delivery_participants;
job.delivery = mean_carrier_travel_rounds;
job.channel = mean_carrier_channel_rounds;
job.gems = group_gems; job.gold = group_gold;
job.recovery_body_rounds = predicted_healing_and_return_cost;
auto score = polaris_draft::score_cycle(job, calibrated_gold_value);
if (score.feasible && score.rate > best_rate) { /* retain this offer */ }
```

Those names are **adapter inputs**, not existing SDK symbols. Helpers pay approach/clear time; only capturers/carriers pay their later phases. Supply the sum through equivalent mean durations when routes/bags differ. For an extra helper on an already assigned job, compare incremental improvement to the existing job, not the full group's reward again. Evaluate the idle helper's alternative too.

The probability inputs are unconditional probabilities of reward receipt/delivery/loss. Do not invent them from an arbitrary HP ratio. First compare safe jobs using1/1/0 and explicit feasibility gates; investigate uncertain jobs separately. They must later be calibrated using held-out events. Gold value starts with the baseline's existing phase/role weight so this experiment does not also change economy preference. Denial defaults to zero and must never double-count gems already credited.

Acceptance: improved productive opening time and delivered score on corners/rushbait/packs, with the same external panel and both sides. Preserve ambush/stampede. Trace the first changed target and whether it actually executes.

## 2. Task outcomes and honest memory: task_state.h

`play_turn()` calls `handle_enemies()` and `bank()` before the claimed-capture branch. A new capture rule lower down cannot affect a turn already consumed there. A held capture is productive even if no SDK action is issued; a rejected attack is not progress.

Draft outcome contract:

```cpp
using polaris_draft::Result;
Result outcome = try_current_intent(); // proposed adapter, not an existing Bot method
if (polaris_draft::consumes_policy_turn(outcome)) return;
// Failed/no-action may fall through only after refreshing any facts changed by actions.
```

Integration must distinguish movement, damage dealt, completed capture and resolved tribute from merely attempting a call. A task transition starts a fresh hold deadline. Repeated observations cannot perpetually extend the same wait. Death invalidates the task; fuel suspension does not establish tactical abandonment. Recheck round identity and legality after expensive calculation and before issuing an action.

Current `observe()` turns an unseen reward older than six rounds into `ready_round = seen_round + respawn`. That assumes when and whether an unseen capture completed. `CampMemory` instead makes old reward knowledge unknown while retaining only directly observed respawn deadlines. Reaching a deadline also becomes unknown, not proof a camp is alive.

Do not add a second timer beside Group.ready_round without migrating its consumers. Extend Group with an explicit knowledge state, adapt the visibility-gated state observation once, then audit `choose_group()`, `solo_target()` and capture completion. An unknown camp should receive a bounded inspection policy, not permanent exclusion. This change is separate from score ranking.

Acceptance: reproduce one abandoned capture, one false-success pursuit and one stale reward before changing behavior. Existing productive channel/cast/wait fixtures must remain valid. Then paired outcomes, not only fewer target switches.

## 3. Capture ownership: capture_owner.h

Polaris already has pack claim bytes and rotates small captures; large rewards deliberately share. I would improve ownership stability and helper reassignment, not replace everything with permanent exclusive claims.

`capture_owner()` honors a fresh lease even when its owner is outside local vision. It elects among eligible visible candidates only when the lease expires or its invalidity is established. Tie-breaking is independent of iteration order. Opportunity cost is expressed in equivalent occupied champion-rounds; begin with zero until a defensible estimate exists.

`release_helper()` applies only after the group is cleared. The helper should move off reward tiles if necessary and immediately ask the existing target selector for other work. Keep the incumbent controller's explicit shared-capture policy as a separate toggle to compare: health, income distribution and upcoming item spikes can justify sharing.

**The Lease struct is not a shared-memory format.** All eight existing bytes already have mode-specific meanings. Adapt the existing kClaimGroup/kClaimSlot/kClaimStamp protocol in pack mode, including its modulo-age handling; solo slots need a separately reviewed protocol. Do not serialize this struct or allocate extra bytes blindly. A local visible election alone cannot guarantee global consensus, so test conflicting/hidden views and stale leases.

Acceptance: no valid owner displaced merely because unseen; re-election after expiry/proven invalidity; helpers do not abandon live clears; increased team throughput exceeds capture-sharing/upgrade disadvantages.

## 4. Legal siege positions: siege_tiles.h

Existing siege staging includes head-count and elapsed-wait triggers. I would evaluate actual firing positions and remaining-monster threats before committing the selected casters, while keeping ordinary farmers productive.

`siege_positions()` filters a small supplied tile set against every remaining damaging monster, including ones our attack may wake. The caller's `can_cast_from` predicate must validate the actual ability's geometry, target rules and line of sight. The Chebyshev attack model is appropriate only after checking the current monster rule. Unknown monsters require a conservative design-based threat envelope.

For a Euclidean range-four cast versus Chebyshev range-three retaliation, a cardinal tile at distance4 can work; diagonal(3,3) is unsafe, and(4,1) is outside spell range. Tests cover that difference and an additional monster invalidating an otherwise safe tile.

The adapter must also ensure path reachability, fresh occupancy, a ready damaging ability, escape/HP reserve, sufficient fuel and enemy arrival margin. A safe tile alone does not make the overall siege worthwhile. After final kill, explicitly switch to capture and then delivery; do not remain on the old firing ring.

Acceptance: monolith/elkring objective conversion improves without prolonged staging, interrupted ordinary income or a stampede regression.

## What I would defer

- A full bot rewrite, new draft and item build packaged with these changes.
- Permanent whole-team escort or global solo-farming rules.
- A new aggression classifier. Later model response time to a specific camp/altar, chasing persistence and route repetition with recency and uncertainty. It should change a local job choice, not force the whole team to surrender the middle.
- Replacing native pathfinding with historical Java optimizations without profiling current fuel costs.

## Validation and next gate

Native compilation with C++20, `-O2 -Wall -Wextra -Werror -pedantic` passed. The same scenarios passed UndefinedBehaviorSanitizer. Checks include400 monotonicity cases, respawn/travel overlap, worker-cost accounting, malformed inputs, finite hysteresis, fixed hold deadlines, death reset, unseen reward uncertainty, owner-election order, unseen leases, helper release and siege geometry.

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Werror -pedantic checks.cpp -o /tmp/polaris-draft-checks
/tmp/polaris-draft-checks
```

These tests validate the pure draft's contracts, **not SDK integration, fuel use, game strength or Elo**. The next gate is one adapter/candidate per hypothesis under main Claude's testing workflow. No engine matches, submissions or platform scrims were run for these drafts.
