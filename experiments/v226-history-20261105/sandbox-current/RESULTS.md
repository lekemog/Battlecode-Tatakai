# Sandbox against current repository bots — 5 November 2026

**480 completed local release-mode games**, 40 archived benchmark maps, both sides. Frozen source snapshot 03b34544c02d0e9b501183f5d1f4a60759ceec9f. Candidate is the unchanged PR #75 build from v226. No tuning during the run.

CLI 5.0.0 was checked against the package index as the latest available release. Every game is engine 3.0.0, build 96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd. Engine/build assertions fail closed.

| Policy | Opponent | Wins / 80 | Mean banked | Mean gem margin | Mean deaths | Fault events | Fuel events |
|---|---|---:|---:|---:|---:|---:|---:|
| v50h5e | v50h5e | 40 | 816.59 | 0.0 | 3.73 | 0 | 2 |
| v50h5e | v51d | 38 | 824.17 | -1.99 | 4.11 | 0 | 1 |
| v50h5e | v50p1 | 54 | 926.81 | 356.0 | 5.41 | 0 | 2 |
| chatgpt-v50h5e-history | v50h5e | 40 | 823.0 | 7.14 | 3.76 | 0 | 2 |
| chatgpt-v50h5e-history | v51d | 37 | 821.17 | -14.53 | 4.1 | 0 | 1 |
| chatgpt-v50h5e-history | v50p1 | 54 | 925.79 | 351.82 | 5.44 | 0 | 2 |

## Matched candidate changes

| Opponent | Converted losses | Lost baseline wins |
|---|---:|---:|
| v50h5e | 1 | 1 |
| v51d | 0 | 1 |
| v50p1 | 1 | 1 |

## Per-map net wins relative to v226

Each cell sums both matched sides.

| Map | vs v226 | vs v51d | vs early pack |
|---|---:|---:|---:|
| 00ambush | 0 | 0 | 0 |
| 00collision | 0 | 0 | 0 |
| 00contest | 0 | 0 | 0 |
| 00corners | 0 | 0 | 0 |
| 00eight | 0 | 0 | 0 |
| 00elkring | 0 | 0 | 0 |
| 00expanse | 0 | 0 | 0 |
| 00fragment | 0 | 0 | 0 |
| 00gem-fields | 0 | 0 | 0 |
| 00gemfight | 0 | 0 | 0 |
| 00great-wall | 0 | 0 | 0 |
| 00interlock | 0 | 0 | 0 |
| 00lanes | 0 | 0 | 0 |
| 00lost-world | 0 | 0 | 0 |
| 00monolith | 0 | 0 | 0 |
| 00packs | 0 | 0 | 0 |
| 00pilgrimage | 0 | 0 | 0 |
| 00quadrants | 0 | 0 | 0 |
| 00reverse-spiral | 0 | 0 | 0 |
| 00road-of-riches | 0 | 0 | 0 |
| 00rows | 0 | 0 | 0 |
| 00rushbait-v2 | 0 | 0 | 0 |
| 00split | 0 | 0 | 0 |
| 00stampede | 0 | 0 | 0 |
| 00swirl | 0 | 0 | 0 |
| 01big-world | 0 | 0 | 0 |
| 01boss-battle | 0 | -1 | 0 |
| 01broken-curve | 0 | 0 | 0 |
| 01concentrated-wealth | 0 | 0 | 0 |
| 01corridors | 0 | 0 | 0 |
| 01elk-arena | 0 | 0 | 0 |
| 01fracture | 0 | 0 | 0 |
| 01gold-rush | 0 | 0 | 0 |
| 01hooks | 0 | 0 | 0 |
| 01islands | 0 | 0 | 0 |
| 01shortcut | 0 | 0 | 0 |
| 01starfish | 0 | 0 | 0 |
| 01starvation | 0 | 0 | 0 |
| 01the-farm | 0 | 0 | 0 |
| 01yellow-brick-road | 0 | 0 | 0 |

## Interpretation and limits

v226/v50h5e is the live baseline reported by GitHub; v51d is the latest recommended development candidate, not asserted live. v50p1 is the documented local rush stress opponent. Active platform submission was not independently queried in this sandbox.

This covers the pinned 40-map benchmark, NOT all 128 active maps. CLI map download failed and the direct map listing required authentication; browser retrieval did not complete. Map bytes were recovered from the repository. These inspected maps are not blind holdouts. Default deterministic seeds do not create independent repeat evidence.

Use these results as a current-engine regression/stress screen. No unranked ladder groups, activation or deployment occurred. The testing guide requires stronger pinned panels for retreat changes; no promotion from these local results alone. Candidate source was unchanged throughout. The initial scheduler was stopped during setup before any games completed, to finish opponent compilation without overlapping build jobs; the completed run retains all 480 planned cases.

## Decision

Do not promote this candidate as a strength upgrade. Across 240 matched cases it wins 131 versus v226 control's 132; the early-pack result is unchanged and the v51d comparison loses one net win. The stamped history fixes a sample-validity defect, but this test does not establish a ladder benefit. Each policy has five fuel-exhaustion events, and all 480 games have zero bot-fault events on either side. Keep correctness review separate from competitive promotion.
