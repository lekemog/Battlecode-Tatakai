# League macro applied to Battlecode: conversion, tempo and joint objectives

5 November 2026. Base: `bots/v51d` at `03b34544c02d0e9b501183f5d1f4a60759ceec9f`, rechecked as the head of the current gameplay branch. v226 (`bots/v50h5e`) is the reported live baseline; its platform activation was not independently queried. This study uses the champion/camp/gem/altar game. The builder/conveyor game is a different ruleset.

## What the games say

**New analysis of existing current-engine game summaries:** 80 v51d-versus-v226 games on 40 archived maps, both sides, engine 3.0.0. These are the v226 control games from the previous history experiment, analysed from v51d's side. No new top-ten ladder games are implied. Per-game rows: `diagnosis-v51d.json`; source raw summaries remain in the prior experiment's local output. The engine's events and metrics were analysed, rather than a fresh visual review of all replay frames.

| v51d cohort | Games | Wins | Mean banked | Mean deaths | Mean gem losses | Median first deposit, among games with a deposit |
|---|---:|---:|---:|---:|---:|---:|
| All | 80 | 42 | 826.16 | 4.28 | 203.64 | 121 |
| Wins | 42 | 42 | 1029.43 | 2.43 | 22.79 | 113 |
| Losses | 38 | 0 | 601.50 | 6.32 | 403.53 | 137 |

One loss had no deposit. Crucially, **14,109 of 16,291 lost gems (86.6%) came from just the two `01boss-battle` games**. Excluding that map, mean losses were 27.97 gems/game; among the remaining losing games, 34.03. Gem-loss sums can count recirculated gems, so they are not a count of unique resources destroyed. This is a map-conditioned failure, not evidence that every map needs much more caution.

Those two boss-map games banked 94 and 343, with first deposits at rounds 977 and 1562. All 21 v51d deaths there were champion-caused; there were zero v51d fuel-exhaustion events in those two games. One Marcella death at round 1837 dropped 3,304 gems. The events establish severe late conversion failure. They do not establish whether a chase, blocked altar, poor group coordination or an earlier gate decision caused it.

**Historical top-opponent evidence, old engine:** `results/fish-watch-2026-11/` records ten unranked losses to Intercontinental Fish. The separate `results/unit-coordination-2026-11/` replay study reported 104 deaths versus 21, isolation farther than seven tiles from the nearest ally on 41% versus 28% of rounds 30–200, and far fewer favourable local matchups. These are prior repository findings, not newly measured engine-3 rates. They suggest creating good engagements before improving aggression. They cannot qualify a new combat policy after the patch.

## What transfers from League research

These sources provide coaching ideas and community observations, not proof of a Battlecode policy or verified professional credentials. Their League patch details are not transplanted.

| Principle | Source and limitation | Battlecode application |
|---|---|---|
| Synchronise readiness and movement | [Dignitas recall guide, Fordola, 2021](https://dignitas.gg/articles/summoner-phone-home-a-guide-to-recalls): plan resource refresh and item breakpoints before objective arrival; keep team timing aligned. An authored guide on an esports organisation's site, not evidence the author played professionally. | Estimate when allies can actually participate before committing to an altar or gate. Preserve the bot's actual shop rules; League's shop/recall requirement does not carry over. |
| Use pressure while teammates can support it | [r/Jungle_Mains discussion](https://www.reddit.com/r/Jungle_Mains/comments/1rpr3jr/mid_to_late_game_macro/): respondents discuss staying near pushing allies and aligning resets, with farming during downtime. Community advice. | Spread to farm while safe; shift nearby champions together for a contested objective. A distant healthy ally should not count as immediate help. |
| Prepare the objective before fighting for it | [MOBAFire Worlds 2020 macro guide](https://www.mobafire.com/league-of-legends/build/worlds-2020-macro-tempo-meta-guide-582105): author describes vision setup, numbers advantages and turning from an objective onto responders. Archived community analysis; explicitly outdated. | Scout approach routes with legal observations, choose a rendezvous and clear access before exposing a valuable carrier. Do not hard-code League timers. |

The resulting strategic question is: **what scored objective does this action make possible, and who will reach it in time?** A good kill creates a deposit, a camp capture, denied access or a safe recovery window. Farming and fighting should be evaluated by those conversions.

## Strategy to build toward

This is a proposed coordination design, not a claim that the full state machine is implemented in this candidate. Use event-driven windows and map features rather than named-map exceptions or fixed round cutoffs.

| Phase | Entry evidence | Action and exit |
|---|---|---|
| Farm | No urgent contested conversion; profitable reachable camps | Distribute work with claims; avoid assigning the whole team to a low-value camp. Reconsider after a clear, enemy contact or a meaningful bag. |
| Set up | Valuable objective exists; legal observations suggest contest | Select carrier and a nearby escort, estimate travel times and cooldown readiness. Gather locally while other champions can continue farming. Abort when the required helpers cannot arrive. |
| Commit | Participants are present and the fight/access model is favourable | Execute one objective with short, bounded commitment. Recheck safety on new enemy arrival or an ally's death. Avoid repeatedly entering contact and withdrawing independently. |
| Convert | The fight opens access or the carrier can safely channel | Score the bag or capture the gate/camp. A non-carrier can zone a responder; the carrier's value includes the bag at risk. Reachability and gated-altar state matter before calling a deposit possible. |
| Recover | Team is depleted or the window is lost | Choose safe farm or healing with a next rendezvous. Preserve contest timing instead of returning one champion at a time. |

Economic lens: compare expected scored gems and future income against travel time, death risk, lost bag, enemy pickup and the farming forgone by escorts. A transferred bag can both reduce our future scoring and help the opponent; estimate the opponent's chance to convert it rather than mechanically doubling every loss. Farming creates resources, so the whole game is not strictly zero-sum. These data do not identify an exact Nash equilibrium.

Opponent modelling should initially record only observable tendencies: recent enemy pack size, approach direction, deposit sizes and timing, and chase duration. Track sample count and observation age; fall back to the base policy when confidence is weak. Enemy arrival estimates must use legal last-seen information, not omniscient replay state. Evaluate whether the model predicts held-out contact/deposit events before letting it alter combat. No learned opponent module is included here.

## Isolated implemented candidate

`bots/chatgpt-v51d-bank-first` copies all 24 source files from the measured local v51d fixture. That fixture has one additional final LF in each file compared with the pinned GitHub source, inherited from file retrieval; all 24 differences were checked to be exactly that whitespace (`source-normalization.json`). Only `brain.cpp` changes; `bank-first.patch` is the complete behavioural diff.

In the existing favourable-fight branch, a carrier at the existing `tribute_cap` of 40 gems cannot request aggressive closing unless a nearby ally is already engaged. In-place basic attacks and spells remain available, as does joining that engaged ally. If combat produces no action, the ordinary health and tribute phases can resume. The existing combat phase precedes tribute; this experiment tests one way that a locally favourable fight might delay conversion. It does not force a deposit, prevent every movement spell or override every other combat branch.

The added decision is O(1), with two scalar comparisons and a boolean gate; no dynamic allocation, new pathfinding, map selector or persistent state. No claim is made that the whole inherited bot avoids allocations. The inherited health-history implementation is unchanged; this does not combine the previous correctness candidate.

Risk: a full-bag champion can surrender useful pressure, fail to clear an altar defender or miss an easy chase kill. It may also hoard while standing and attacking. A lower death count is insufficient if scoring or wins fall. The candidate is deliberately fixed before the batch; thresholds are not tuned to the observed maps.

## Decision after the completed run

**Do not promote the bank-first candidate.** Against v226, it won 44/80 versus v51d's 42/80, but against the early pack it fell from 62/80 to 60/80. Across both opponents the total was unchanged at 104/160. Mean scoring fell in both matchups. Early-pack deaths rose from 5.412 to 5.562, failing the documented stress gate; the lower total gem losses concealed an increase outside the boss map, from 33.192 to 42.346 gems/game. This is a useful counterexample to applying a good League principle as a broad individual restriction.

All 320 games had zero bot-fault events across both teams. Candidate fuel-exhaustion events totalled four across 160 games, versus five for v51d; this is not a clean fuel budget result or evidence of a compute improvement. The candidate is a rejected, reproducible experiment, not a deployment recommendation. Keep the existing base while building a joint objective mechanism. See the complete paired results and changed-map table rather than selecting the favourable mirror statistic.

## Experiment and handoff

320 new release games: v51d and the candidate each face v226 and v50p1 on all 40 available archived benchmark maps, both sides. CLI/SDK 5.0.0, engine 3.0.0, build `96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd`. Engine/build, paired seed/map hashes, local source differences and release flags are checked by `analyse.py`. `RESULTS.md` contains the completed outcome table and per-map net changes; `validation.json` contains hashes and paired gains/losses; `compact.json` contains all per-game metrics.

The 40 maps are inspected stress cases, not blind holdouts or the full 128-map active pool. The existing local map refresh was blocked. No ladder games, submission or activation are part of this experiment. A combat policy still needs the repository's two pinned stronger-opponent panels and current-map coverage before deployment. Repeated deterministic games are not independent samples.

For Claude: review the result table before using the candidate. Next isolate the boss-map access/conversion failure with decision traces, then prototype a joint carrier/escort objective claim. Measure deposit timing, bag losses, camp income foregone by escorts and outcome across map families. Re-run recent strong-opponent games on the current engine before using historical isolation rates to set a cohesion threshold. Broad regroup/caution bundles have already failed previous tests; keep mechanisms separate.

Reproduction: initialise a CLI-5 lab, copy the four bot folders from this pinned branch (the reproduction helper normalises a single final LF only when needed to match a recorded source hash), and put the 40 hash-matched maps from the pinned `bench/maps/` into `maps-sandbox/`. Run `reproduce.py LAB OUTPUT`, then the emitted `cambc run-batch` command, then `analyse.py LAB OUTPUT`. Raw statistics and replay files are generated locally. The committed compact rows are measured outputs, not a replacement for raw replays when attributing a decision.
