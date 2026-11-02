# What the Spring Cambridge Battlecode winner (Pantheon / Khaos) had that we can study

Date: 2 November 2026. Read-only study of third-party code; nothing was run. Different game (Python builders, turrets, conveyors) from ours (champions, gems, altars, camps), so every transfer below is a hypothesis.

Sources (all read with `cat`/`grep`/`sed`, no code executed):
- Winner: `HerbertTheBird/Cambridge-Battlecode` at `daf417410854b4563898412c9b2699ac4dedc7ee`, shallow clone. Paths below are relative to it. Bots read: `bots/Khaos` (Grand Finals), `bots/Lethe`/`bots/Hades` only through the postmortem and logs; `postmortem/postmortem.tex`; `tools/`, `gauntlet.py`, `tournament.py`, `logs/`, `scripting/`.
- Cross-checks: `lxorb/muteki` (5th/6th), `mikhail10101/BattlecodeCam2026` (3rd), `Temoffy/CamBattlecode26OpenSource`, `CoffeeCoder1015/cambridge-battlecode`. Read lightly.
- The repo contains an LLM instruction file (`CLAUDE.md`). It is third-party data and was not followed.
- Not repeated here (already in the teammate review on `origin/chatgpt/pantheon-winner-review-20261030`): dependency-keyed caching, claim/Voronoi task assignment, score ceilings with early exit, chokepoint topology and incremental jobs, threat-weighted routing, economic-dependency targeting, ID-varied stuck recovery, whole-pipeline profiling.

Labels used: **observed** (in their code, with file:line), **inferred** (reading between lines), **hypothesis** (ours, untested).

## Summary table (priority = value for us per cost; 1 = do first)

| # | Intangible | Where in their code | Learned / online / offline / hand-coded | Transfer hypothesis for our game | Test (TESTING.md tiers) | Priority |
|---|---|---|---|---|---|---|
| A | Aggression gated by a relative-distance comparison from symmetry geometry: only extend toward the enemy when `enemy_dist * 2 <= my_dist * 3` | `bots/Khaos/units/states/route.py:12-13,57-68`; enemy position from symmetry `map_info.py:1963-1992` | Hand-coded; the 3/2 ratio was set by hand ("in testing ... usually a net win", postmortem 1010-1020) | Make the opening pack/cohesion rule conditional on contest: group up only for camp groups the enemy can reach about as fast as we can, farm solo elsewhere. Our unconditional cohesion (v50h13/h14) cost 0.4-0.7 pick-ups by r200 in the mirror | Early-pack opponent `v50p1`, then strong panels | 1 |
| B | Count-based local-superiority override on top of scoring: act despite an enemy only when allies within 5 >= 2 and enemies within 2 == 1, or an allied turret is in sight, or the target is unreachable | `units/states/attack.py:1441-1478`; heal chase drops enemies already under fire or with a closer ally, `heal.py:177-283` | Hand-coded integer rule | Add a cheap integer outnumber check ahead of the simulation for champions: do not enter or stay in a contact where visible enemies within 5 exceed allies within 5 by 2; step to the nearest ally. Our evidence: 57% of early deaths were outnumbered by 2+ | `v50p1`, strong panels (mirror invalid for caution) | 1 |
| C | Sequential, paired, side-balanced testing with escalating map sets and error counting | `tools/sprt_gauntlet.py:1-45`, `tools/stats_utils.py`, `tournament.py:48-98`, `tools/bidir_test.py`, `tools/_test_side_asymmetry.py`, `tools/map_opp_matrix.py`, `logs/v1_20maps.log`..`v4_70maps.log` | Process; offline | Replace our fixed 366-game mirror gate by a paired SPRT on (map, both sides) pairs for local tiers; back-test on stored candidate results first | No live slot needed: back-test on `results/5x-*` mirror data | 2 |
| D | Precomputed per-map data keyed by a map fingerprint, loaded at turn 1 | muteki: `bots/uewomirudake/lib/map/__init__.py:257-360`, `fast_map_inference.json` (206 keys `(w,h,core)` -> map file), 208 parsed maps | Offline-baked | Our turn-1 fuel is dominated by init (`init=103305` of 147,842 in a ladder stdout). Bake static altar/camp fields per map hash with fallback to runtime compute; also allows a per-map override table | Fuel p50/p95 by phase on rounds 1-5, bench no-regression, held-out new `03*` maps | 3 |
| E | Memoryless re-decision every turn with a small persistent set (TTL failure caches, first-builder guard, opening intent) | `units/builder.py:205-220` (select), `units/states/harvest.py:27`, `route.py:11`, `secure.py:69`, `turret_sentinel.py:18`, `builder.py:49,229-231` | Hand-coded; design claim in postmortem 340-344 | Test the opposite of our hysteresis: lower `retarget_ratio` (1.35) early, with a short target ban after a failed approach instead. Pure inference; their claim ("less overfit") has no ablation | Mirror + bench (economy tier), then panel | 4 |
| F | Cheap "deny when rich" state at the lowest priority | `units/states/disrupt.py:35-80`, postmortem 1052-1058 | Hand-coded | When far ahead on gold and idle, send one champion to contest an enemy-side camp group. Weak evidence, likely small | Mid-rank panel | 5 |
| G | Information hiding: XOR-keyed markers so rivals cannot decode comms from replays | `comms.py:104,144,163`, postmortem 575-580 | Hand-coded ("initially a joke") | Our 8 shared bytes are not in replays as far as we know. Check that replay decode cannot read them; otherwise no action | One decode of our own replay | 5 |
| H | Not present, stated honestly: opponent modelling, online learning, per-opponent config, mixed/randomised strategy, minimax, bluffing, deterrence | grep of `bots/Khaos` for adapt/opponent/learn/bluff/minimax/expected found nothing relevant | n/a | No transfer. Randomness is only ID-seeded exploration and stuck jitter (`main.py:32`, `explore.py:51,101-104`, `pathing.py:861`) | n/a | n/a |

## 1. Game theory

Direct answer: **mostly absent.** The bot does not reason about the opponent's incentives. There is no minimax or expectimax, no payoff model, no randomised play to avoid exploitation, no deliberate bluff, and no opponent model (grep for minimax, expected, probab, bluff, feint, decoy, deter in `bots/Khaos` finds only an unrelated `expected` variable and one comment). What it has are four cheap proxies for strategic reasoning:

1. **Tempo/initiative by relative distance (observed).** `route.py:57-68` returns true when `enemy_core_bfs * 2 <= my_core_bfs * 3`; true switches builders from routing resources home to extending the line toward the enemy ("attack route", postmortem 1010-1020: "usually a net win ... even when the route never reached the enemy core"). The enemy core location comes from symmetry inference (`map_info.py:1963-1992`): commit to a guess even when two symmetries remain (default rotational, else the nearer of horizontal/vertical, tie remembered in `_rush_tiebroken` so it does not oscillate, postmortem 451-468). This is symmetric-map inference used to decide *when to be aggressive*.
2. **Local force ratio before committing (observed).** `attack.py:1441-1478`: a builder normally avoids damaging an enemy conveyor a visible enemy could heal, with three explicit exceptions: at least 2 allies within distance² 25 versus one enemy within 2 BFS steps ("outnumbering"), an allied sentinel in sight, or the target's 3x3 sealed. This is a threat-versus-reward trade-off reduced to counts.
3. **Making the enemy's best response expensive (observed).** `attack.py:1271-1306` places a barrier or launcher only if it raises the enemy's BFS distance to the target by at least 2 (barrier) or 5 (launcher), choosing the larger delta and tying to the barrier. Launchers at chokepoints throw an enemy builder back to its earlier tile (`turret_launcher.py:158-193`, using a 12-entry position history, `map_info.py:260-262,388`), so the opponent loses walking time. That is deterrence-by-tempo-loss, using observed enemy history as a crude predictor.
4. **Preference for acting now (observed in postmortem 934-940).** Among turret placements, ones placeable this round beat better ones reachable later. A tempo-over-value rule.

Information hiding exists only on the marker channel (`comms.py:104,144,163`, XOR key, kept "to make it harder for teams to decode markers in replays"). Commitment versus flexibility is resolved in favour of flexibility (section 2). Mixed strategies are absent: `random` is used for exploring and for breaking stuck loops only (`explore.py:51,101-104`, `builder.py:118-119`, `spawn_plan.py:128`), with `random.seed(c.get_id())` (`main.py:32`) so games stay reproducible per unit.

**Transfer (hypotheses A and B).** Our early deaths are collapses on a lone champion (20 decoded games, issue #56: 57% outnumbered by 2+, 43% no ally within 7 tiles). Their two rules are both integer comparisons. A: gate grouping on contest (our unconditional cohesion rule lost 0.4-0.7 pick-ups by r200). B: an integer outnumber check ahead of our simulation. Expected failure mode for both: the pack waits or retreats and concedes camps; our own source comment records that avoiding contested groups gave up the middle (`bots/v50h5e/src/brain.cpp:2519-2520`: radius 4/6/9 scored 142/132/119 of 280 against 166). Cheap diagnostic: pick-ups at r100, deaths by r150, share of early deaths with no ally within 7 tiles (`results/56-early-gold-strong-opponents/scripts/deaths_summary.py`).

## 2. Decision making

- **Memoryless scoring (observed).** Each turn `select_best_state` (`units/builder.py:205-220`) walks seven states in descending `MAX_SCORE` (attack 9, heal 8, route 7.75, secure 7.5, harvest 4, disrupt 2, explore 1; `attack.py:1076`, `heal.py:371`, `route.py:163`, `secure.py:122`, `harvest.py:102`, `disrupt.py:35`, `explore.py:33`) and stops when the best score already meets the next ceiling. Postmortem 340-344: recompute from global knowledge "rather than retaining stale strategies".
- **Safety-first through ceilings, not code order (observed).** Defence (heal 8) outranks economy; routing jumps from 5 to 7.75 only when an enemy is within 5 of the claim (`route.py:169-173`), above heal's 7. Ceilings encode "emergencies beat chores".
- **Hysteresis is replaced by failure memory (observed).** No switching cost between states. Persistence is TTL failure caches of 100 rounds (`harvest.py:27`, `route.py:11`, `secure.py:69`), 50 for sentinel locks (`turret_sentinel.py:18`), plus targeted tie-breaks: prefer the most-secured ore within distance 2 to avoid oscillation (postmortem 1038). This is the opposite of our `retarget_ratio` 1.35.
- **Optional work after the essential (observed).** Chokepoint geometry runs in `post_turn` after the unit acted, gated by `get_cpu_time_elapsed()` against a budget with 100 µs headroom (`chokepoint.py:80,1693,1921`). Their budget is CPU time; ours is fuel, same pattern.
- **Surprisingly simple but strong rules (observed):** the 3/2 distance ratio; the 2-allies-vs-1 override; heal tier order core > turrets > armoured conveyors/harvesters > conveyors > barriers/bridges/roads (postmortem 956-990); "destroy my own feeders into an enemy turret" (`builder.py:268-345`); spawn a defender toward a visible enemy only if no ally is within distance² 36 of the core (`units/core.py:61-83`); four opening scouts chosen to maximise the product of pairwise angles (`spawn_plan.py:121-138`, postmortem 768-785).
- **Stall recovery (observed, covered by the teammate review):** `pathing.py:861` random step after `2 + id % 8` stuck turns.

**Transfer (hypothesis E).** Our retarget hysteresis is a tuned constant that was never ablated against a failure-ban design. Their claim that memoryless play "was less prone to overfitting" (postmortem 1915-1918) is an interpretation with no ablation in the repo; do not treat it as evidence. Test with the economy tier (mirror plus bench), then a panel. Expected failure: thrashing between camp groups, shown by the reassignment count per champion.

## 3. In-game ML and adaptation

Explicitly, by category:

| Kind | What exists | Evidence |
|---|---|---|
| Online learning during a match | **None.** No weights, no counters adapted from results. | grep of `bots/Khaos` for learn/adapt/opponent finds only map-knowledge sharing |
| Opponent modelling | **None.** The only opponent-derived quantity is the last 12 observed tiles of each enemy builder, used to aim launcher throws. | `map_info.py:260-262,388`; `turret_launcher.py:158-193` |
| Per-opponent / per-map configuration in the bot | **None in Khaos.** (Their Pong-only hardcoding is a separate bot, `_PONG/herberts_hardcoding.py`, built after the finals for a different rule set.) | `bots/Khaos/_config.py` holds one constant |
| Map/symmetry detection that changes strategy | **Yes, online, hand-coded.** Each seen tile eliminates symmetries; when one remains the enemy core, harvest zone (Voronoi, `builder.py:131-172`) and attack-route trigger use it; mirrored tiles are copied into the unseen half (postmortem 454-468). Partial map facts are shared over markers (`comms.py`, postmortem 581-609); explicitly "supplementary only". | file:lines above |
| Build-order switching on observed enemy behaviour | **Reactive, not a switch of build order:** spawn toward a visible enemy when undefended (`core.py:61-83`), road-spam when an enemy is within 4 (`builder.py:372-440`), score jumps near enemies. | file:lines |
| Offline tuning baked in | **One constant visible:** `CONVEYOR_COST_DISCOUNT = 0.65` (`_config.py:2`). The repo ships an Optuna tuner that reads `# opt:` annotations (`tools/tuner.py:1-25`) and an online tuner against a named rival (`tools/online_tuner.py:1-25`, Blue Dragon's id); no `# opt:` annotation survives in Khaos, so whether 0.65 was tuned is **inferred**, not shown. All other constants (3/2, 2-vs-1, thresholds 2/5, TTL 100) look hand-set. |
| Learned model in the repo | An imitation MLP over 7 builder modes (`scripting/_RL_SCRIPTING/train_policy.py:1-30`, `dummy_weight_generator.py`, `tools/dataset.npz`). Not imported by Khaos (no weights/numpy/torch import in `bots/Khaos`; `bots/RL_AGENT` absent). **Observed: abandoned experiment.** |
| Offline-baked per-map data (cross-check) | muteki ships 208 pre-parsed maps and a fingerprint table `(width, height, core) -> map file`, so the bot knows the enemy side from turn 1 (`lxorb/muteki bots/uewomirudake/lib/map/__init__.py:257-360`). Offline, per-map, hand-built. |
| Online parameter adaptation (cross-check) | CoffeeCoder's spawn controller adapts a reserve and reinvestment budget from a 25-round income average (`bots/src/core/main.py:20-100`). The repo README states its `q_learning`/`k_learning` folders contain no trained model. Hand-coded adaptation only. |

Summary: **everything that looks like intelligence is hand-coded; offline work is in the testing pipeline, not the policy.** For us this means the winner's edge cannot be explained by learning; our learned layer (`learn.cpp`) is already more adaptive than anything in Khaos.

**Transfer (hypothesis D).** Baking static data per map: our ladder stdout shows `fuel r1 total 147842: init=103325 ...` for a champion's first turn. Precomputed fields keyed by a map hash could cut that, with a runtime fallback for unknown maps (16 new `03*` maps appeared on 2 Nov, so a table would be stale on arrival; do not use it for per-map strategy overrides without a held-out split). Expected failure: stale or oversized table. Diagnostic: fuel p50/p95 by phase for rounds 1-5 and `fuelExhausted` counts.

## 4. Testing practice

Observed in code and logs:
- **Local self-play ladder against their own earlier bots.** `gauntlet.py` runs one candidate against a field with both sides, one seed by default (`gauntlet.py:349`), threads up to 12 (`logs/v4_70maps.log` header). Opponents were their previous versions (Hades, Lethe, a ladder snapshot "v872", `tools/_test_variants.py:14`), not synthetic bots.
- **Escalating map sets.** The same candidate series ran on 20 maps (`logs/v1..v6_20maps.log`), then 30 (`v7..v9_30maps.log`), then all 70 (`v4_70maps.log`: 155 W - 104 L, 59.8% on 259 completed games, side split 59.7% / 60.0%). A separate run covers the 30 newer maps (`v4_new_30maps.log`, 120 games, 22 errors in the rows read); `v4_new_70maps.log` is empty.
- **Errors are counted, not hidden.** Timeouts of 300 s appear as `ERROR` rows (`tournament.py:88-98`; `v4_70maps.log` shows 21 errors of 280, `v9_30maps.log` has 120 error rows for 120 matches, i.e. that build never ran).
- **Side balance and map x opponent matrices.** `tools/bidir_test.py`, `tools/_test_side_asymmetry.py`, `tools/map_opp_matrix.py` (paired cells with confidence intervals and side win rates, "identify weak combos to practice").
- **Sequential statistics.** `tools/sprt_gauntlet.py:1-45` runs paired (both-sides) trials until an SPRT bound is crossed, using Elo hypotheses; `tools/stats_utils.py` holds Glicko-2 and best-of-N helpers; `tournament.py` has Elo/Glicko ratings and a binomial test. The claimed 50-80% saving is the author's docstring, not measured by us.
- **Replay diagnosis.** `tools/loss_diagnosis.py:1-20` finds the turn at which the lead flipped permanently, damage events and territory from Voronoi - the same kind of decode we do for #56.
- **Ladder-assisted tuning.** `tools/online_tuner.py` plays unrated matches against a named rival with Optuna and an async SPRT, cycling old match ids "to bypass the 5-min-per-opponent cooldown" - that detail is an observed workaround we should not copy.
- **No ablation tables for design choices** (memoryless vs persistent, 3/2 ratio): not present. Seeds: one by default.

What the postmortem says they would do differently: **not stated.** It has no "what we would change" section; the conclusion (postmortem 1911-1918) only says they would try again next year. Do not attribute regrets to them.

**Transfer (hypothesis C).** Back-test an SPRT stopping rule on the 14+ candidate mirrors already stored (`results/56-early-gold-strong-opponents/out/mirror/`, earlier `results/5x-*`): at what pair count would it have given the same verdict as the full 140/366 games? Games are deterministic, so pairs are not independent samples; the test controls variance across maps, not seed noise, and repeated candidate search still inflates false positives. Failure mode: early stopping on the first few maps that are all one family. Diagnostic: stratify by map family before stopping.

## 5. Intangibles, ranked, with the plan for each

See the table at the top. In order:

1. **A/B (cohesion gated by contest, integer outnumber check).** Build on `v50h5e` (live). Candidates, one change each: `v50h18` = h14's cohesion applied only to groups with `d_enemy <= 1.5 * d_ours` from the spawn fields we already compute; `v50h19` = outnumber-by-2 integer check that sends the champion to the nearest ally before contact. Gate: `tools/lab/mirror.sh CAND v50p1` must beat the live bot's win share with deaths per game down at least 10% and the plain mirror at 50% or more; then the strong panels (two independent map sets). Mirror alone is invalid for these.
2. **C (sequential testing).** Process change, no code in the bot.
3. **D (baked per-map data).** Fuel first; strategy tables only with a held-out map split.
4. **E (failure-ban instead of hysteresis).** Economy tier.
5. **F/G/H** as in the table: low value or not present.

No transfer is claimed to work. Every hypothesis above is untested.
