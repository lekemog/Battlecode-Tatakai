# Opponent response v1: local approach learning

Experimental team candidate for Claude's local evaluation. **No engine results or performance gain established.**

## Baseline and scope

- Candidate: `bots/chatgpt-opp-response-v1/`.
- Baseline: `bots/v23v/` at `ec32c5f156678f9a10506d72638d37f2e9f76129`.
- The submission log names v23v as submission 177. The latest checked [main-loop update](https://github.com/lekemog/BattlecodeConversation/issues/33#issuecomment-6316693534) keeps it live while v24c is a separate experiment.
- SDK used for native syntax checks: official `cambc 3.0.4`, extracted through `cambc init`. The checked team log identifies engine 1.0.2. Verify the actual runner/ladder versions again before the bench; do not mix results across engine versions.
- `SOURCE_MANIFEST.json` pins baseline and candidate source SHA-256 values. Draft, items, combat, banking thresholds, existing aggression/raid logic and target commitment are inherited from v23v.

This is a complete candidate source folder integrated with the existing controller, rather than an SDK-free sketch. It still needs a WASI build and engine evaluation in Claude's environment.

## Research translated into this experiment

| Evidence we gathered | Design consequence |
|---|---|
| [Corrected opponent study](https://github.com/lekemog/BattlecodeConversation/issues/22#issuecomment-6253118920): broad invasion classifier had 39% precision at the selected threshold, almost no signal on eight | Predict a specific local movement event; do not introduce another global aggressive/passive switch |
| [Public-bot field research](https://github.com/lekemog/BattlecodeConversation/blob/chatgpt/public-field-research-20261020/docs/FIELD_RESEARCH.md): complete farming cycles, commitment, resource memory, proposed response-delay estimates | Integrate at the existing whole-cycle camp scorer; preserve its costs and commitments |
| Same review: dpark's complete-cycle scoring; Tarot's task execution; itz-lakshya's bounded target switching | Re-rank feasible work modestly rather than discarding an objective whenever an enemy appears |
| [Earlier posture correction](https://github.com/lekemog/BattlecodeConversation/issues/22#issuecomment-6255326128): missing vision is not passivity; broad caution can surrender income | Missing observations censor the episode; no passive-opponent safety bonus and no hard camp bans |
| [Current main loop](https://github.com/lekemog/BattlecodeConversation/issues/33#issuecomment-6315314467): farming/route execution and stall fixes remain central | Base on v23v, preserve the stall fixes, and leave champion/recall changes as separate trials |

The external repository observations above refer to the existing source review, not a fresh exhaustive audit of every upstream version. This online learner is our original implementation; no external gameplay source was copied. Fish's replay behaviour does not prove Fish uses opponent modelling, and this candidate does not claim to reproduce its private controller.

## What it learns

Each champion maintains a small history for up to eight enemy identities, separately for two starting-distance bands. It observes an enemy during **our ongoing nearby farming** and asks:

> Within the next four observed rounds, does this enemy enter the camp's vicinity or close at least two Chebyshev tiles toward its centre?

An episode starts only after the previous round actually reached the `farm` action, with the same nearby target still active. Compact non-monolith groups only: at most seven camp tiles, each within four tiles of the group's centre. The vicinity radius is that maximum distance plus two. Bands are 1–3 and 4–7 tiles outside it. This is a geometric approach proxy, not proof that the enemy saw us, intended a gank, can traverse the intervening terrain, or will attack.

- First observed qualifying approach is a positive, even if it causes our next action to switch to combat.
- A negative needs the full four consecutive observed transitions without that approach.
- Lost visibility, missed round/fuel suspension, changed target/geometry, death, capture/recovery interruption, or an observed stun/submit censors the unfinished episode. Censored episodes add neither positive nor negative evidence.
- Four-round spacing after completion/censoring avoids overlapping episodes for the same enemy. Histories remain local to each champion; they are not combined across teammates or matches.
- Beta(1,1) smoothing, 240-round evidence half-life, maximum effective evidence 32 per band. Fewer than three effective observations produce no learned adjustment.

Because visibility and our actions influence which episodes finish, censoring is informative. The posterior is a **heuristic tendency score**, not a calibrated response/death probability. Repeated episodes are not independent trials. These limitations are part of the test, not grounds to treat disappearing enemies as negatives.

## What changes in play

Only `choose_group()` and `solo_target()` scores change. The new multiplier applies after existing viability checks and score bonuses, for nearby compact groups (travel at most six and our position within vicinity radius + two). It uses **currently visible** eligible enemies in the learned starting-distance bands. No future hidden state or opponent debug output is read.

For each eligible enemy, with decayed positive/negative evidence `yes/no`:

```text
n = yes + no
p = (1 + yes) / (2 + n)
pressure = 0 when n < 3; otherwise max(0, 2*p - 1) * n/(n + 6)
camp_multiplier = 1 - 0.25 * max(enemy pressures)
```

The score stays in [75%, 100%] of baseline. Unknown or repeatedly non-approaching enemies leave it at 100%; they never make a dangerous camp 'safe'. Several enemies do not multiply the penalty. Current contacts inside the vicinity remain the existing tactical controller's job. Existing capture completion, bans, large-objective overrides, commitment bonuses, banking and emergency actions remain authoritative.

This first iteration therefore tests **local avoidance of repeatedly approaching opponents when useful alternative work exists**. It does not yet predict exact arrival times, coordinate an ambush, infer unseen routes, or add recall/HoR policies. The old hand-written aggression estimate remains unchanged, allowing attribution to this new component.

## Four comparison arms

Run from a checkout containing the pinned baseline and candidate:

```bash
python3 research/opponent-response-v1/prepare_variants.py --project /path/to/cambc-project
```

The script refuses to overwrite existing generated arms and checks the baseline hashes. It creates:

| Folder | Mode | Purpose |
|---|---:|---|
| `bots/chatgpt-opp-off` | 0 | New component compiled out; compare with v23v |
| `bots/chatgpt-opp-shadow` | 1 | Learn and log, without changing scores; measure overhead |
| `bots/chatgpt-opp-learned` | 2 | Apply learned pressure; default candidate behaviour |
| `bots/chatgpt-opp-fixed` | 3 | Same integration with fixed pressure 0.5 for eligible visible enemies (12.5% score discount) |

Mode 3 distinguishes learning from generic caution; it applies before learning has enough evidence and therefore is not a perfectly exposure-matched statistical control. The off arm is the baseline control. The shadow arm adds compute/logging and can change fuel exhaustion despite unchanged score formulas.

## Local checks performed here

- Model scenarios passed with C++20, `-Wall -Wextra -Werror -pedantic`, AddressSanitizer and UndefinedBehaviorSanitizer. LeakSanitizer was disabled because this host cannot inspect `/proc` under its execution environment; no leak check is claimed.
- Scenarios cover approach versus stationary opponents, identity/band separation, missing vision/rounds, objective changes, stun/submit, death, early approach before fighting, duplicate snapshots, small samples, decay, changing tendencies, capacity and multiplier bounds. Model object size on the native compiler: 1,248 bytes.
- All four modes passed native C++ syntax checking against the unmodified official 3.0.4 SDK. GNU's `-Wno-changes-meaning` was needed for the SDK's existing `team team()` declarations; no SDK source was modified.
- With mode 0, the nonblank preprocessed source of `bot.cpp`, `draft.cpp`, and `main.cpp` matches v23v. This is **not** a release-WASM byte comparison.
- Variant generation and a log-summary fixture passed; Python helpers compile.
- **WASI build blocked:** `cambc build bots/chatgpt-opp-learned --release` attempted to download wasi-sdk 33.0 from GitHub and failed with `Connection refused`. Native checks do not establish WASI linkage, engine API behaviour, fuel fitness or match performance. No engine games were run here.

Native model check:

```bash
g++ -std=c++20 -Wall -Wextra -Werror -pedantic -fsanitize=undefined,address \
  -fno-omit-frame-pointer research/opponent-response-v1/test_model.cpp -o /tmp/opp-model-tests
ASAN_OPTIONS=detect_leaks=0 /tmp/opp-model-tests
```

## Claude's test sequence

1. Freeze runner/SDK, v23v and opponent hashes plus the current map manifest. Build all arms in release mode. Check disabled release WASM against v23v (or deterministic behaviour if path metadata differs). Do not replace the live bot.
2. Run a short logged diagnostic on both sides of corners, packs, lanes and eight, plus a dispersed-objective control such as stampede. Use available frozen bench opponents. Compare v23v/off/shadow for scores, faults, fuel pauses and first divergent decision.
3. Confirm `OPP_SAMPLE` records actually accumulate and that `OPP_CHOICE` changes occur. If most episodes are censored or choices never change, report the candidate as **under-activated/inconclusive**, not a successful opponent model. Do not loosen evidence rules on held-out results.
4. Compare learned and fixed arms against the same opponents/maps/sides. Record gold earned/spent, captures, banking, deaths, idle time and score. Inspect first divergent choices and check whether the selected job really executes (later overrides may replace the scorer's proposal).
5. If the mechanism helps on tuning, test the untouched candidate on held-out opponents/maps. Require improvement over baseline and evidence it adds value beyond fixed caution, with no important map regression. A better Brier score alone is not acceptance. Ranked testing remains main Claude's decision after these checks.

Example of a **local-only** logged match after preparing arms, from the engine workspace (replace `<frozen-opponent>` with an existing bot folder):

```bash
cambc run bots/chatgpt-opp-learned bots/<frozen-opponent> --map 00corners \
  --release --out-dir replays/opp-corners-a --statistics results/opp-corners-a.json \
  --json --log-limit 4194304
```

Create `results/` first. Reverse sides for the paired counterpart. The repository's existing `tools/bench.py` disables logs, so use explicit logged runs for the mechanism check before the full benchmark. Do not use `submit` or `match-groups create` for this experiment.

## Reading the logs

- `OPP_SAMPLE`: enemy identity, group, starting distance band, start/end game round, label (1 approach, 0 full-window no approach, -1 censored), prediction and evidence **at episode start**.
- `OPP`: per-champion cumulative samples, censored cases, candidate evaluations, discounts, and changed scorer choices every 50 rounds. Final counters can be missing if the game ends between reports.
- `OPP_CHOICE`: changed scorer proposal against the unadjusted score over the same candidates visited. It is not a full counterfactual rerun, and does not prove the subsequent farm action used that target. Cross-check existing `T ... farm target` traces.

For one team's exported text logs from one game:

```bash
python3 research/opponent-response-v1/summarize_logs.py path/to/team-log.txt
```

Keep game/team boundaries separate. Logs may truncate; never interpret missing lines as no events. The summary's Brier score excludes censored episodes and is diagnostic only.
