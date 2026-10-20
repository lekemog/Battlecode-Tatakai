# Four independent v21e experiments

This is the implementation/testing handoff requested in [Issue #33](https://github.com/lekemog/BattlecodeConversation/issues/33#issuecomment-6280530996), building on our shared field research in PR #34.

Our team: **Ben, Kurian, Leke and Szymon**.

Parent: commit `76d0d2617c58a2fce8d8130a513ea26383ef60ef`; original `bots/v21e/src/bot.cpp` blob `3dd61d73500f4f81edf1718545b3c0ebbd46a481`. The original bot folder and main branch are unchanged by these experiments. Each candidate activates exactly one macro; no candidate combines the four policies.

| Bot folder | Policy | Mechanism |
|---|---|---|
| `bots/cg_cycle` | `POLARIS_CYCLE` | Pack value per occupied champion-round; actual selective capture recipients; full delivery/channel; fractional pooled-health recovery trips. Keeps v21e safety gates, pack/solo split and gold weight. |
| `bots/cg_task` | `POLARIS_TASK` | Explicit observed camp knowledge; stale rewards become unknown without inventing a respawn time. Capture commitment tracks distance progress and a bounded productive hold; death clears task state. |
| `bots/cg_capture` | `POLARIS_CAPTURE` | Adapt the existing 3-byte pack lease; retain a fresh unseen owner unless observed invalid; stable arrival/slot election; release helpers after a small reward becomes available. Large rewards retain shared capture. |
| `bots/cg_siege` | `POLARIS_SIEGE` | Movement goals outside every observed damaging monster's actual SDK attack range, intersected with usable champion reach. Actual casts check SDK masks. Re-query the group after attacking to move directly into capture after a final kill. |

## Source organization and scope

`src/bot.cpp` is a frozen v21e copy with guarded adapters; `src/bot.h`, draft and main files use the same parent. The tiny bot wrappers define one macro and include these files. This avoids four drifting 80-KB copies while keeping each policy separately buildable. These wrappers depend on this repository layout; do not copy only a wrapper folder for platform submission.

The four SDK-independent policy headers are original drafts from PR #34. SDK integration is in the guarded code. The siege helper models the SDK-documented Chebyshev cast range at candidate positions; the actual host action still enforces visibility, target categories and legality. It does not assume all monsters have radius 3. It preserves the existing melee approach if there is no safe firing tile. It does not infer unseen monsters, prove that an entire movement route is safe, or replace the existing siege start/cooldown policy.

Capture uses bytes 3–5 only in pack mode. Solo coordination, the existing one-lease capacity, threat bytes, shared big-reward policy, banking and enemy-handling order are unchanged. A fresh lease expires after five rounds, with the existing modulo-256 stamp. Visible unavailable/channeling/carrying owners can be invalidated; local absence alone cannot invalidate a fresh lease. Helper reassignment is provisional and does not publish a second squad target.

The cycle model is an experiment, not a calibrated simulator: recovery uses the existing predicted incoming damage and pooled health. Recovery estimates and helper-release assumptions can be wrong. It does not add speculative opponent probabilities or double-count denial as extra gem value.

## Validation and acceptance

- cambc **2.2.4**, official C++ SDK, release builds.
- All 17 checked-in pool maps, both sides, 34 games per frozen opponent.
- Five tuning and five held-out opponents; 170 games/set/candidate.
- Baseline reproduced **127/170 tuning**, **137/170 held-out**, zero reported bot faults.
- The tuning mean per-game margin is **+332.56 gems**. The sum of the five opponent means is **+1662.82**, explaining the earlier rounded +1663 figure.
- Native policy scenarios/400 monotonicity cases pass with strict C++20 and UndefinedBehaviorSanitizer.
- **All 1,700 games completed. None passed the two-set win requirement.** See [RESULTS.md](RESULTS.md), the paired CSV and comparison JSON for every outcome and regression.
- A candidate must improve wins on **both sets** before main Claude considers a guarded ranked trial. Local strength does not establish ladder strength; the bench previously over-rated health builds.

Main Claude owns wards/tripwires, centre income, capture punishment, draft, banking mechanics and all ranked decisions. No submission or platform match group was created here.

The no-switch control in `bots/cg_control` produces byte-identical release Wasm to v21e. The measured capture candidate has a small-bag eligibility failure case; [followups/capture-small-bags.patch](followups/capture-small-bags.patch) supplies an unapplied repair for a separate test. Its applicability was checked with `git apply --check`; it has not been engine-tested.

Generate the complete comparison after the five panels finish with `python tools/compare_v21e_candidates.py`, followed by `python tools/render_v21e_report.py`. The report includes map regressions and a replay review queue. Freeze files and `environment.json` record the measured source, map, SDK and toolchain hashes.

## Reproduce

Use a checkout with cambc 2.2.4 and SDK/toolchain initialized. With the GitHub CLI installed and its existing authentication available:

```sh
python tools/import_v21e_opponents.py
python tools/import_v21e_opponents.py --verify-only
g++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=undefined research/v21e-candidates/checks.cpp -o /tmp/polaris-policy-checks
/tmp/polaris-policy-checks
cambc build bots/cg_cycle --release
python tools/bench_v21e_candidates.py v21e --jobs 2
python tools/bench_v21e_candidates.py cg_cycle --jobs 2
python tools/bench_v21e_candidates.py cg_task --jobs 2
python tools/bench_v21e_candidates.py cg_capture --jobs 2
python tools/bench_v21e_candidates.py cg_siege --jobs 2
```

Set `CAMBC_BIN` if cambc is not on PATH and `CAMBC_CACHE` to an already prepared toolchain cache. The runner uses offline mode for repeatability and emits explicit missing/error cases. It retains stats and replays in `results/<bot>/`; `--summarize` rebuilds summaries without playing games. Its cache-resume check is for this frozen experiment; use a new results directory if source, maps or engine change.

`opponents.json` records each repository/tree/path/blob. Only `.cpp/.h/.hpp` under the selected public bot's `src/` are imported; no opponent code is committed here. All 151 imported files were verified to equal their public Git blobs plus exactly one final LF added by the connector-to-patch import. The importer reproduces those measured bytes; run freeze files additionally record installed SHA-256 values. This whitespace normalization does not change C++ behavior.

