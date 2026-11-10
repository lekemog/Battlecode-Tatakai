# Role61: reject this controller

2,304/2,304 release games completed; zero batch failures and zero bot faults on either side. All nine cells contain 256 games (128 maps, both sides). CLI/SDK 5.0.1; asserted embedded engine 3.0.0/build 96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd.

| Policy | v53x | Early pack v50p1 | Mixed carry v60d |
|---|---:|---:|---:|
| v60d | 97/256 | 160/256 | 128/256 |
| cg-role61-kite | 80/256 | 171/256 | 103/256 |
| cg-role61 | 85/256 | 132/256 | 102/256 |

The full role controller loses ground against all three opponents. Vesper-only kiting gains 11 wins against early pack, but the map-clustered bootstrap interval for its win-rate change spans zero (-1.95 to +10.94 percentage points), mean gem margin worsens slightly and deaths rise. Do not promote either candidate. The full controller loses 28 wins against early pack; map-clustered bootstrap interval -18.36 to -3.52 points. These are descriptive intervals over this pinned map set, not probabilities of live ladder strength. Multiple exploratory comparisons were not corrected.

Against early pack, the full controller changes round-200 team gold from 710.85 to 637.77 (-10.3%), gold spent from 634.30 to 564.06 (-11.1%), Vesper champion damage from 527.35 to 404.13 (-23.4%), and Vesper deaths from 0.121 to 0.102. Total deaths per game rise from 5.102 to 5.938 (+16.4%). Carry survival improves slightly while team economy and damage suffer. This supports a specific diagnosis of overprotective positioning/opportunity cost; it does not isolate Heart following, peel movement, spell timing and target selection from each other.

Against v53x, full-controller Vesper round-200 gold rises from 207.80 to 226.45 and early carry deaths fall from 0.066 to 0.031, yet team gold falls and wins decline. Merely funneling more gold into a safer carry does not ensure victory. The independent kiting ablation also reduces Vesper damage, implicating lost attack opportunities in addition to formation costs.

This does not settle the broad hypothesis that adapting to melee drafts can help. It rejects this particular local bodyguard/peel implementation as an upgrade. Keep the parent as the reference. Next isolated experiments should preserve guaranteed safe attack windows, escort only during actual dive pressure, and measure guard farming loss; do not bundle a new draft, economy planner and positioning controller. A live pinned opponent panel remains untested.

## Runtime and evidence

| Policy | Fuel exhaustion events vs v53x | vs early pack | vs v60d |
|---|---:|---:|---:|
| v60d | 298 | 238 | 330 |
| cg-role61-kite | 426 | 277 | 354 |
| cg-role61 | 284 | 278 | 324 |

Fuel exhaustion is a correctness/performance concern and can alter outcomes; this candidate is not certified clean. Event counts are candidate-side entries, not number of affected games. Zero bot faults does not mean zero interrupted turns.

See DESIGN.md for exact implemented vs inherited behavior and limitations. This is local coordination, not complete global five-unit formation or a new high-spawn camp-control planner. Results use local pinned opponent snapshots, not current top-ten selections. No platform submission, activation or unseen-map qualification. Baseline results reproduce prior CLI5.0.1 totals exactly (97 vs v53x, 160 vs v50p1).

cases.csv contains every compact per-game metric, actual map hash, engine build and seed. summary.json, paired.json, families.csv and map_deltas.csv retain failures and regressions. hashes.json freezes source/maps/WASM. manifest.txt records executed cases; reproduce.py regenerates the suite in an initialized CLI5.0.1 project. Samples below are actual release replay bundles; trace smoke games are excluded.

Selected paired replay map: `02guardians` (largest full-controller mean gem-margin regression against early pack; deliberately a failure example, not a representative random sample).
