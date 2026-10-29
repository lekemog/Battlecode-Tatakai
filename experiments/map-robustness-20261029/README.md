# Tatakai map robustness experiments — 29 October 2026

This pack tests isolated repairs, their combination, and a learned-layer ablation against multiple opponent implementations. It contains 3,360 completed local engine games across all 70 current layouts, plus a separate audit of 313 historical match IDs. No candidate was deployed or merged.

## Decision

Retain unchanged v50c as the comparison baseline. Keep the stamped health-history repair available for further correctness validation; its one-win edge is too small to establish strength. Reject the carrier-route experiment as currently implemented. Neither the danger-banking policy nor the three-way combination earns promotion.

| Policy | Wins / 560 matched cases | Net wins vs baseline |
|---|---:|---:|
| v50c | 485 | — |
| Health-history validity | 486 | +1 |
| Carrier-relative ring routing | 477 | -8 |
| Earlier danger banking | 484 | -1 |
| All three together | 484 | -1 |
| Learned adjustments disabled (exploratory) | 456 | -29 |

The exploratory learned-off result is reported separately in [ABLATION.md](ABLATION.md). It was added after benchmark saturation was observed; it is not an untouched confirmatory test. Retain the learned layer: disabling it regresses across both old and added layouts, and scores only 39/140 directly against v50c.

The biggest finding is an evaluation gap. Unchanged v50c wins 415/420 against the archived Daniel v8, DE41H v4 and Mohnish implementations, while the recovered current v221 top-ten sample is 5/50. The three archived bots are useful regression checks but poor proxies for strong live opponents. Local wins cannot certify ladder improvement. The v50c self-play control contributes another 70/140.

The old pool contains 40 layouts; the active pool contains those same 40 by byte hash, plus 30 missing layouts. Fourteen old names use different punctuation. We tested both sides across every layout. No clear old/new degradation appears against the weak archived opponents, but their saturation limits that conclusion. This study does not prove or disprove statistical overfitting.

## Read these first

- [RESULTS.md](RESULTS.md): original 2,800 games, matched gains/losses, map-block sensitivity intervals, per-map regressions and validation slices.
- [ABLATION.md](ABLATION.md): separate 560-case learned-layer ablation and its limits.
- [map-history.md](map-history.md): every recovered historical map outcome, separated by cohort/version. Collision is a recurring loss signal. Small current samples on Quadrants, Expanse, Rows and others identify review priorities, not reliable map win-rate estimates.
- [design-review.md](design-review.md): source adaptability review and public-repository lessons, including season/compatibility limits.
- [FOLLOW_UP.md](FOLLOW_UP.md): concrete next actions and acceptance criteria.

## Reproduce the candidates and cases

Use CLI 4.0.0, SDK 4.0.0, WASI SDK 33.0 and release mode. See [toolchain.json](toolchain.json). Every saved result reports engine 2.0.0 and build `85aa7167b44db7cea97509f55e997750520e33d644e9f4f90d6128c50eba1d21`; reject comparisons against another build.

1. From this Git repository, recover `bots/v50c` at parent `2d93a142df388db48596f82842cf7cca47809cec`. Recover the three `bench/bots/{x_de41h4,x_daniel8,h_mohnish}` source folders at main snapshot `3f68e9561a3ee059759a9a6a9c78ecaee8d87ea5`. Put the four projects under `PROJECT/bots/`. Use fresh build directories and an SDK 4.0.0 project root. The source manifest checks every tested source file; do not reuse compile_commands or build caches as provenance.
2. Run `python materialize_candidates.py PROJECT/bots/v50c PROJECT`. This checks the baseline source hashes and applies all five frozen patch files into new candidate folders, refusing overwrites. Patch application was reproduced byte-for-byte against all tested candidates.
3. Extract `current-maps.zip` into `PROJECT/maps-current/`. Run `python make_manifest.py PROJECT DATASET` for each of robustness, new-map-validation, baseline-validation and learned-ablation. The script verifies source and map hashes and writes absolute-path manifests/indexes. `--resume` skips completed JSON cases; invalid/mismatched engine files must be resolved rather than silently counted.
4. Run `cambc run-batch PROJECT/results/DATASET/manifest.txt --jobs 4 --release --json --timeout 300 --log-limit 0`. Concurrency was adjusted during this session; completed case files were retained and interrupted cases rerun. There is one final result per planned case. A deterministic repeat is not a fresh sample. Do not reduce the denominator when a run fails.

The original plan froze four candidates before inspecting results. Its 40-map wording reflects that first stage; the added 30-map and direct-v50c indexes extend coverage without altering those policies. `ablation-plan.json` records the later diagnostic. `index-*.json` records all 3,360 intended cases, sides, opponents and split flags.

`local-games.json.gz` contains the final compact per-case metrics, map hashes, seeds, engine builds and fault/fuel event counts. It is a JSON object keyed by dataset/tag. `historical-games.json` preserves the recovered historical match IDs; historical records are not inserted into the local comparison. Full local engine summaries/replays are reproducible from these manifests and source hashes; they are not all uploaded in this compact pack.

To regenerate aggregate comparisons, decompress the compact JSON into `PROJECT/results/audit/local-games.json` and run `python finalize_audit.py PROJECT` and `python finalize_ablation.py PROJECT`. The first script asserts 2,800 original cases; the second asserts all 560 ablation cases and checks pairing. `summarize_history.py` regenerates the history table beside itself. `audit_results.py PROJECT` extracts metrics from fresh engine summaries; its historical-input section expects the repository cache snapshots named in that script. `test_hazard_history.cpp` exercises stale observation gaps, reset, signed healing and 20,000 reference rounds; compile from PROJECT after materializing the history candidate.

## Limits

One default deterministic seed per map/opponent/side; no fresh-seed generalisation claim. Added maps are outside the old benchmark but some appeared in earlier online loss analysis. Mohnish is withheld from this experiment's tuning slice, although the baseline had historical exposure. No weights were retrained. Public code reviewed here targets an earlier game and is not a new compatible opponent set. The historical audit covers the recovered caches, not all lifetime platform games; a complete team export is still needed. No policy was selected using map-name or coordinate fingerprints.
