# Integrated strategy on the latest checked development bot

Source freeze: `1c704680d24e316988182867ba5a47066c48f734`.
Base: `bots/v71a` at PR81 head `010047f8dba8e06fd5038b3121f262885406ac40`. This was the newest candidate in the handoff at task start, not an authenticated claim about the active submission. CLI account access is expired. The earlier user-reported live v66i is included as a comparison opponent. Original versions and the live slot are unchanged.

## Requested systems implemented

| Requirement | Implementation | Limits |
|---|---|---|
| Latest working base | Preserve v71a's pre-r200 gold weight/caution, map/fuel/banking fixes, kit-aware buying and Heart camp-dash bar0.9 | These inherited results are repository-reported until reproduced in this suite |
| Opening100x planning and map variety | Compute terrain fields, accessible camp resources, clustering, respawn rates and candidate kit values; cache composition shortlist | Heuristic utility, not a win probability or full game simulation |
| Tank/ranged/DPS roles | Heart tanks/clears with shield and stun dash; Cassi stuns/bursts shared targets; Issac resets attacks with a local leash; Varg clears clusters; Vendetta finishes via parent logic | No new Willow/Prism/Vesper role transplant |
| Pair protection | Weak-link retreat/recall, expiring partner memory, bounded Issac regroup and accepted-fight shared focus; uncovered Cassi avoids ready enemy reach | No atomic teamwide formation/retreat broadcast through fog |
| Productive grouped farming | Cassi adopts a visible healthy frontliner's active camp, favoring Heart; Issac adopts Cassi's nearby live camp | Rewards/channels are not copied as follow objectives; blocked paths release to the normal planner |
| Avoid unsupported camp exposure | Cassi can solo short-range groups from safety; long-range groups require partner intent; actual attack/position gate requires being out of camp range or a strictly closer healthy melee ally | Does not formally certify every inherited travel step; camp-admission and local fight-position safety are checked |
| Resource-area occupation | Draft chooses an accessible high-respawn resource neighborhood; at peace, camps within10 tiles receive a12% early preference | Ends at r200 and switches off with visible enemies; never a permanent all-team ball |
| Concentrate capture income | Prefer Varg, then Vendetta for gold, Marcella for gems, when the recipient is already on a member tile | No cross-map waiting, no distant capture detours; unavailable recipients do not block collection |
| Useful upgrades | Pair buys two Durability Health shards, then Monster role stat, Jungle Health, then Bruiser role stat. Cassi Focus, Issac Strength; others retain parent builds | Experimental sequence, not proven globally optimal; pair plan bypasses learned reordering |
| Runtime/evidence | Existing fuel gates retained; complete source/map/WASM pins, per-game engine assertions and logs | Fuel exhaustion is still measured as a failure concern; zero bot faults is not a clean-turn guarantee |

## Adaptive core instead of forcing a losing composition

Earlier PR84/86 and the v245-wide experiment exposed large losses when forcing ranged/pair compositions through generic play. The integrated version keeps a **Heart + Cassi/Issac core as a candidate**, not an unconditional requirement. The original v71a composition is always retained.

A core composition must score at least5% above the original composition in the analytical model. Small maps (3/4 picks) with spawn walk below45 retain the proven composition, reflecting the observed close-brawl failure mode. This is a pre-test feature rule, not a map-name table, fitted win probability or post-hoc selection of winning maps. If screening cannot complete, the original draft function is the fallback.

Core flex is limited to the existing melee kits Ryth, Marcella, Vendetta, Varg and Ren. Within a selected core, Heart and the pair are picked first. A retained original composition preserves its original order. Committed picks cannot be discarded. No opponent reaction or random diversity is enabled.

All256 final two-round draft scans completed. The core is selected in30 side-games (15 maps), and the original composition in226. The search peaks at1,710,140 fuel (~17.12% of the initial100x budget). Three-pick maps retain Marcella/Vendetta/Varg; four-pick maps have three selected sets; five-pick maps have two. The exact trace is in draft_scan.csv.

`cg-v72-core-control` is an additional forced-core diagnostic with the same gameplay code and core draft prefixes. Its32 games on a fixed eight-map subset exercise the pair mechanics even where the adaptive version retains the original team. These are not pooled into the full-map qualification result.

## What changed relative to previous experiments

- No permanent Heart escort: joining is driven by current visible farming intent or a real local diver.
- Cassi no longer blindly walks toward Issac while he independently farms. Issac is the bounded pair follower; Cassi prefers a frontline objective.
- Ranged actions use actual engine availability: stun/basic/damage before a legal escape walk, never an assumption that walking and attacking are symmetric.
- A caster never attacks from a tile the new guard deems unsupported. Strictly closer, healthy, nonchanneling melee cover is required when within camp attack range; unseen awake-camp threat is conservative.
- Preflight caught escape scoring that could reward an unsafe step merely for becoming closer to a camp. Unsafe escape tiles now tie at a constant bad value, covered by a property test.
- Capture income does not wait for a distant carry, and the supported role shop cannot be reordered by old learned family/stat weights.
- The opening region record is actually read by gameplay, with a one-time REGION log. It is a bounded economic preference, not a forced opening assignment like rejected v63a.

## Evidence tiers and acceptance

- Unit/property checks: caster range/cover/tie safety, unsafe-score invariance, stale partner release, bounded regroup, stun immunity and exhaustive composition eligibility.
- Draft checks:256 deliberately truncated two-round games on128 pinned repository maps/both sides. Preliminary probes and mandatory-core scans are excluded.
- Main suite:1,536 complete release games: unchanged v71a and integrated candidate versus v71a, v66i and early-pack v50p1,128 maps/both sides.
- Diagnostic:32 forced-core full games on eight preselected maps/both sides against v71a and early pack. Exploratory, not independent confirmation.

CLI/SDK5.0.1; actual engine3.0.0/build96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd asserted per complete game. Server map refresh failed, so the128-map pool is pinned repository data rather than independently refreshed live metadata. No fuel limit increase. Logs/config/source are frozen for the suite.

Evaluate wins, banked margin, deaths, early gold/spend, pair deaths, ordinary-turn fuel events and family tails together. A model score or implemented feature list is not evidence of superior play. No real-opponent panel, transformed/unseen-map qualification or live deployment is implied. If the complete candidate regresses, retain it as a rejected integration test and keep v71a intact.

## Remaining limits

The controller is local and visible/recent-state based, not globally synchronized. Stun overlap duration is not optimized. The draft estimates initial team damage/recovery and does not simulate exact item curves, tank order, collision, altar logistics or all future camp routes. The region lease is static during the opening and deliberately relinquished under pressure. The new caster gate does not replace every travel/navigation policy. The shop sequence and5%/45-step draft rules need held-out calibration if this bundle survives initial testing. New pair roles may increase ordinary-turn fuel cost. This is an integrated prototype, not a claim that every tactical edge case is solved.
