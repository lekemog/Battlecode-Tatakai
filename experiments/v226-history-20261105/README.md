# v226 health-history correctness iteration — 5 November 2026

## Base, rules and scope
Candidate: bots/chatgpt-v50h5e-history, copied from bots/v50h5e at 03b34544c02d0e9b501183f5d1f4a60759ceec9f. v226 is the best deployed baseline supported by the reviewed evidence; v51d remains the newer candidate, not a proven universal best. Check the actual active submission before platform use.

Autumn 2026a uses champions, camps, gems, gold, items and altars. The earlier builder/conveyor/Titanium game is not this target. No builder state machine, conveyor routing or turret exploit is transplanted here.

This iteration changes only the health-history input validity. One existing file, brain.cpp, changes and health_history.h is added. All other candidate sources match the pinned v50h5e bytes. No banking, draft, combat weights, thresholds, retreat commitment or pathfinding policy is retuned.

## Three-lens decision
| Lens | Reason for this change | What the evidence does not establish |
|---|---|---|
| RTS execution | A contact decision should use recent observed damage, not a sample left behind after a skipped turn or a prior life | Which particular live deaths came from this feature; that every cautious decision is good |
| Game-theory/economics | Incorrect risk information distorts the comparison between fighting, farming and preserving a bag. Repair information validity before estimating marginal action value | An exact Nash equilibrium or exact payoffs for the full partially observed game |
| C++ compute | Four float values plus four integer stamps, 32 bytes total; O(1) operations, no heap allocation in the new module; +16 bytes vs the prior HP array | Whole-bot allocation freedom, globally fastest implementation, or a measured fuel improvement |

The old ring reads slot (round+1)%4 as if it always held round-3. After recording HP 1000 at round 4 and querying round 11 at HP 600, it can report 40% recent loss from that stale sample. The new lookup requires the exact round-3 stamp, otherwise returns the existing neutral default of zero. Observed dead turns clear history. Signed healing remains negative as before, preserving the learned feature semantics on valid samples.

A missed observation is unknown, not proof of no damage. Returning zero follows the old missing-sample convention; separately modelling missingness would require a new feature/training experiment. Stamp checks do not justify changing hazard weights.

## Validation performed
CLI 5.0.0; SDK 5.0.0; official WASI SDK 33.0 / clang 22.1.0. Release baseline and candidate compile. CMake 4.4.4 and Ninja 1.13.2 supplied through the CLI's expected cache paths; their cache folder names contain older version numbers, so use actual version output as provenance. Official compiler archive SHA256: 0ba8b5bfaeb2adf3f29bab5841d76cf5318ab8e1642ea195f88baba1abd47bce.

Native C++20 -O2 -Wall -Wextra -Werror -pedantic tests pass, as do AddressSanitizer/UndefinedBehaviorSanitizer tests (leak detector disabled because of container support). Fixtures cover the stale gap, dead/reset semantics, signed healing, 20,000 continuous and 20,000 sparse reference rounds, initial/missing samples and denominator guarding. A compile-time size check enforces 32-byte fixed storage.

The local game report in RESULTS.md is a separate regression test, not native test output. Its six archived maps are Collision, Contest, Eight, Rows, Expanse and Corners, both sides, against unchanged v50h5e and two frozen benchmark bots. This is NOT the all-128-current-map suite, unseen-map validation or unranked ladder games. The platform map refresh failed from this shell; the six map bytes were recovered from the pinned repository. Maps are hashed in metrics.json.

To rerun the native test from the repository root:
g++ -std=c++20 -O2 -Wall -Wextra -Werror -pedantic experiments/v226-history-20261105/test_health_history.cpp -o /tmp/test_health_history
/tmp/test_health_history

For release builds use a CLI/SDK 5.0.0 workspace and cambc build bots/chatgpt-v50h5e-history --release. Case index and run manifest identify the games; regenerate absolute project paths for your machine. Full engine summaries/replays are not all committed, but compact per-case metrics and reproducible source/map IDs are.

## Public code searched and inspected
- [CoffeeCoder1015 navigation](https://github.com/CoffeeCoder1015/cambridge-battlecode/blob/main/bots/k_learning/builderbot/navigation.py): the reviewed source uses parent/next epoch arrays and bounded A* expansion loops. Transferable idea: distinguish generations and bound optional work. The new health-history implementation is original and uses exact observation rounds; no source implementation copied. Main is a moving reference; the source hash in provenance.json identifies the reviewed text.
- [Pantheon / Khaos](https://github.com/HerbertTheBird/Cambridge-Battlecode/tree/daf417410854b4563898412c9b2699ac4dedc7ee): previous code review in PR #52 covers dependency-keyed caches, task ownership and staged optional topology. These are hypotheses for our SDK, not current-season opponent binaries.
- Search also returned mining/conveyor repositories and MIT Battlecode material. Those are different engines and do not supply compatible Autumn opponents merely because their names say 2026.
- A current-season replay dataset surfaced at https://huggingface.co/datasets/derekz5/bcenv-replays-v1, explicitly engine 1.0.2. It may be useful for historical tooling tests, but is not current patch evaluation. Dataset contents were not downloaded or audited in this iteration.

Public source availability does not establish strength. Do not copy map-coordinate strategy tables or assume a winner's exact constants transfer.

## Next recursive cycle
1. Evaluate whether the corrected feature changes meaningful decisions and whether its small bookkeeping cost changes outcomes. Record both converted losses and lost baseline wins; do not select on aggregate wins alone.
2. Refresh all current map bytes and verify the engine build. Run all-map smoke and regression cases, plus early-pack stress. The existing 128 count is a dated report; enumerate the pool again.
3. Use the UK panel from #71: cutoff ranks and top-three stress cases, same source/engine/maps/sides/opponent versions. Book LIVE_SLOT.md before uploading or queuing. Confirm activation; restore v226 after candidate testing unless a validated promotion decision is recorded.
4. Only after correctness qualification, test dependency-stamped carrier route caching or role-aware solo camp ownership separately. Keep enough allies for difficult camps; preserve valid capture/bank channels.
5. Measure per-family tail regressions, bank conversion, useful champion-rounds, unsupported separation, repeated deaths and p95/p99 fuel. Avoid broad allocation rewrites until profiling identifies a hot path.

For macro decisions, estimate marginal banked gems and kill/camp gold over travel, clear, channel and risk time; compare the lost opportunity elsewhere. The terminal win/loss is zero-sum, but intermediate resources are not a fixed-sum accounting identity. A Nash claim requires a specified payoff matrix, action sets and information assumptions; use measured matchup robustness/exploitability rather than inventing an exact equilibrium for the entire game.

No deployment or ladder superiority is claimed by this iteration. Zero faults on a small suite is not proof of zero bugs.

