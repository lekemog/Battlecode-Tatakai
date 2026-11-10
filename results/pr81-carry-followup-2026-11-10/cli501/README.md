# CLI 5.0.1 rerun verification

10 November 2026. Complete rerun of PR #82 at d7b852165109e531baf8754c05dc89600dc48007. No behavior changes, submissions, activations or scrims.

**1,536/1,536 unique games completed, zero failed jobs, zero bot-fault events on either side. All exported per-case CSV fields match the prior CLI 5.0.0 run exactly: zero differing cases, zero differing fields.** This checks recorded metrics, not byte identity of replay bundles.

CLI version was confirmed as `cambc 5.0.1`; CLI executable SHA-256: `490eb88beb6202fec20bdd2c2365f829ec85d881a9e8e0850ae313a68b92b03f`. Clean release builds used the 5.0.1-initialised SDK and official wasi-sdk 33.0. Every match summary verified engine **3.0.0**, build `96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd`.

The inputs were held fixed: 128 repository maps and unchanged v60d/v60f/v60g/v53x/v50p1 source from the pinned PR. Every retrieved file was verified against its Git blob SHA. The map refresh could not reach the platform from the CLI, so this establishes CLI-version equivalence on the PR pool; it does not certify current platform pool coverage.

| Policy | Wins vs v53x / 256 | Wins vs early-pack / 256 |
|---|---:|---:|
| v60d | 97 | 160 |
| v60f | 99 | 176 |
| v60g | 104 | 165 |

The interpretation is unchanged: v60f has the stronger anti-pack signal, neither candidate establishes superiority to v53x, and no deployment is warranted from this rerun alone. Fuel-exhaustion events still occur and exactly match the earlier CSV; zero bot faults must not be mistaken for zero fuel exhaustion.

## Reproduction and evidence

- `cases.csv`, `summary.json`: rerun metrics and aggregate results.
- `comparison.json`: comparison against every original cases.csv field, keyed by policy/opponent/map/side.
- `hashes.json`: source, release WASM, SDK headers and map SHA-256 fingerprints.
- `compare.py`: portable comparison script.
- `cli-version.txt`, `cli-binary-sha256.txt`: CLI identity.

Initialise a separate lab with CLI 5.0.1; copy the pinned bot sources and maps without build caches. Use the parent report's reproduce.py with the 5.0.1 binary first on PATH, then analyze.py. Run compare.py with --project LAB --new RERUN_OUTPUT --output RERUN_OUTPUT. The old CSV is read from LAB/results/pr81-carry-followup-2026-11-10/cases.csv.
