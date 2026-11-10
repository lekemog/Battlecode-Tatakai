> **CLI 5.0.1 verification:** all 1,536 cases were rerun with unchanged inputs; every exported per-case metric matches the CLI 5.0.0 run. See [rerun evidence](cli501/README.md).

# PR #81 follow-up: capture arrival and committed tank waiting

10 November 2026. Local execution only. No upload, activation, scrim or ladder change.

## Scope and reproducibility

Pinned PR #81 head: `17081c7b8c261e6bec7d78a2915586e697175c0c`. All 200 retrieved bot/map blobs were verified against their Git blob SHA. The unchanged v60d control exactly reproduced PR #81: 97/256 against v53x and Vesper earned gold 2,000.375/game. This is new execution, not a requotation of the old scores.

CLI/SDK 5.0.0; every completed summary asserts engine 3.0.0 and build `96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd`. 128 pinned repository maps, both sides, three policies against two opponents: **1,536 unique completed games**. Map hashes and seeds match within every baseline/candidate pair. The map pool was not refreshed from the authenticated platform. These are the PR pool, not a fresh verification that the platform has added no maps.

## Isolated mechanisms

- **v60f, on v60d:** Vesper previously redirected toward the nearest visible gold reward even when an ally was about to finish capturing it. When shared memory reports a capturer, the candidate queries current capture progress and the actual terrain distance; it skips the diversion when arrival is no earlier than completion. It leaves teammates capturing and retains the existing on-tile handoff. Feature flag `carry_capture_eta`.
- **v60g, independently on v60d:** ranged camp-opening logic previously waited for any melee ally within six tiles while a camp slept, even if that ally targeted another group or was channeling. The candidate waits only for a non-channeling melee ally whose published target is this group; an ally already adjacent still counts. Ally slots are resolved by champion handle rather than assuming roster indices match. Feature flag `ranged_wait_committed`.

Both are hypotheses from source inspection. The matchup changes establish behavioral consequences, not a measured count of late-arrival diversions or false tank waits. A behavior-preserving trace study would still be required to quantify those mechanisms in real UK losses.

## Full-pool results

| Policy | Opponent | Wins / 256 | Banked/game | Gem margin | Deaths/game | Team gold r200 | Vesper gold r200 | Fuel exhaustion events |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v60d | v53x | 97 | 769.7 | -92.3 | 3.148 | 680.9 | 207.8 | 298 |
| v60d | v50p1 | 160 | 859.4 | +210.7 | 5.102 | 710.9 | 215.1 | 238 |
| v60f | v53x | 99 | 778.3 | -96.0 | 3.129 | 689.1 | 215.4 | 396 |
| v60f | v50p1 | 176 | 869.1 | +226.4 | 4.930 | 711.8 | 219.0 | 244 |
| v60g | v53x | 104 | 777.1 | -89.3 | 3.211 | 681.8 | 210.1 | 373 |
| v60g | v50p1 | 165 | 856.0 | +220.1 | 5.141 | 712.1 | 223.1 | 266 |

Wins are team wins, earned gold is cumulative, and fuel events are counts across the 256 games rather than games affected. Both sides are checked for bot faults separately. Smoke runs and interrupted/restarted jobs are excluded from the unique-case count; resumed deterministic keys count once. Completed summaries are authoritative.

## Paired changes against unchanged v60d

| Candidate | Opponent | Loss to win | Win to loss | Net wins |
|---|---|---:|---:|---:|
| v60f | v53x | 26 | 24 | +2 |
| v60f | v50p1 | 24 | 8 | +16 |
| v60g | v53x | 43 | 36 | +7 |
| v60g | v50p1 | 34 | 29 | +5 |

## Per-family wins

| Policy | Opponent | Family | Wins / games |
|---|---|---|---:|
| v60d | v50p1 | 00 | 44/72 |
| v60d | v50p1 | 01 | 21/30 |
| v60d | v50p1 | 02 | 16/30 |
| v60d | v50p1 | 03 | 23/30 |
| v60d | v50p1 | 04 | 49/84 |
| v60d | v50p1 | adgato | 7/10 |
| v60d | v53x | 00 | 27/72 |
| v60d | v53x | 01 | 13/30 |
| v60d | v53x | 02 | 15/30 |
| v60d | v53x | 03 | 13/30 |
| v60d | v53x | 04 | 26/84 |
| v60d | v53x | adgato | 3/10 |
| v60f | v50p1 | 00 | 50/72 |
| v60f | v50p1 | 01 | 22/30 |
| v60f | v50p1 | 02 | 21/30 |
| v60f | v50p1 | 03 | 24/30 |
| v60f | v50p1 | 04 | 52/84 |
| v60f | v50p1 | adgato | 7/10 |
| v60f | v53x | 00 | 29/72 |
| v60f | v53x | 01 | 16/30 |
| v60f | v53x | 02 | 18/30 |
| v60f | v53x | 03 | 10/30 |
| v60f | v53x | 04 | 23/84 |
| v60f | v53x | adgato | 3/10 |
| v60g | v50p1 | 00 | 48/72 |
| v60g | v50p1 | 01 | 23/30 |
| v60g | v50p1 | 02 | 16/30 |
| v60g | v50p1 | 03 | 24/30 |
| v60g | v50p1 | 04 | 47/84 |
| v60g | v50p1 | adgato | 7/10 |
| v60g | v53x | 00 | 24/72 |
| v60g | v53x | 01 | 16/30 |
| v60g | v53x | 02 | 13/30 |
| v60g | v53x | 03 | 15/30 |
| v60g | v53x | 04 | 34/84 |
| v60g | v53x | adgato | 2/10 |

## Interpretation and next gate

Zero bot-fault events on either side across all 1,536 cases. Fuel exhaustion is not zero: see the table and per-case evidence.

v60g adds 7 wins against v53x and 5 against early-pack. Against v53x Vesper camp damage rises from 24,081.6 to 26,046.6 (+8.2%), but deaths rise from 3.148 to 3.211 and kills fall from 3.066 to 2.871. Treat the win swings as weak local evidence, not a promotion case. v60f is the stronger anti-pack lead, but neither candidate closes the gap to v53x.

v60f improves early-pack wins by 16 but only adds two wins against v53x, with increased fuel exhaustion in that matchup. This is a style-specific local signal, not broad superiority. Do not deploy either candidate from this suite alone. Judge v60g from the full table rather than intermediate subset scores. No combined f+g candidate was tested: combining changes without evidence would obscure attribution.

The unchanged Vesper draft remains far behind v53x in direct self-play. This suite isolates execution within that draft; it does not certify a draft replacement. A pinned UK panel, real-death/early-gold traces, and unseen-map qualification remain necessary. Actual live submission was not independently authenticated here; v53x is the PR-pinned baseline, not a new platform-status claim.

The published capture slots have no commitment deadline. Future tests should measure elapsed capture diversion and actual ally arrival, then compare bounded carry/support assignments on productive camp circuits. Do not revive the rejected all-game ball. Do not disable learned draft ordering globally as a side effect; the literal draft is inherited only from the v60 line.

## Evidence files

- `cases.csv`: all 1,536 compact outcomes, early gold, carry metrics, errors, map hashes, seeds and engine build.
- `summary.json`: aggregate and paired outcomes.
- `hashes.json`: source, release WASM and map SHA-256 values.
- `reproduce.py`: portable manifest generator and release runner.
- `analyze.py`: aggregate script (`--project` and `--output`).

Reproduce from a separate clean lab: install cambc==5.0.0, initialise the SDK, copy this branch's maps and bot sources without .cambc build caches, then run `python reproduce.py --project LAB --jobs 4` and `python analyze.py --project LAB --output OUTPUT`. No account is needed for local execution. The standard official toolchain downloads needed curl recovery in this environment. No credentials were copied.
