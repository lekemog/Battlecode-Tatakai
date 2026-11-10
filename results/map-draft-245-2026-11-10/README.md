# v245 map-draft experiment: reject the broad selector as an upgrade

This is the completed **v245/v61j** experiment. Leke subsequently requested a Heart/Cassi/Issac core on **v66i**; see the separate v66i-heart-pair experiment. Do not combine their outcomes or call these v66i tests.

Source freeze: `015e70443bbffcaa96109493d3f090ff628c6e7e`. Base: `ccdc6659d8ccb1405a0061dd2b196051564e536c`, v61j/submission245 per repository records. The source is retained on `chatgpt/v245-mapdraft-20261110`.

## Top-team draft variation measured

All50 stored engine3 t10b_240 summaries were decoded and their compressed-source Git hashes verified. Every opponent changes its unordered champion set within at least one draft size. The best-fitting one set per team/size matches34/50 games;16/50 (32%) require another set. Same-team, same-size composition comparisons differ32/46 times. These are descriptive cohort rates; five games/team do not estimate general transition probabilities or prove map causation.

| Opponent | Games | Drafts unmatched by one fixed set within each size |
|---|---:|---:|
| Ad_Astra-de0b1e3c | 5 | 3 |
| BattleCats-285f4eb5 | 5 | 1 |
| Intercontinental_Fish-1890540d | 5 | 1 |
| Mite-ee83f5e5 | 5 | 1 |
| NEETCoders-882106d4 | 5 | 3 |
| Trzy_Kwaterki-36258abf | 5 | 2 |
| Univardisty-a4350547 | 5 | 1 |
| caterpillow-ec2b57be | 5 | 1 |
| stellar_best_girl-547efb5b | 5 | 2 |
| test4-c00b682e | 5 | 1 |

The frequent core is visible: Heart appears43/50, Cassi/Issac41/50 and Vesper38/50. Mite, Fish and several others retain3–4 champions across their five-pick maps and vary the remaining slots. The later Franklin handoff reports a larger3,885-game study with mostly one composition per map and little revealed-opponent reaction; that is repository-reported evidence, not this session’s reconstructed raw dataset.

## Draft computation

256/256 two-round truncated scans (128 maps/both sides), no failures or logged turn errors. All policy-valid composition screens completed; no fallback. Measured initial fuel about9.99million; maximum search use5,698,467 (57.04%). Final sets:4 three-pick,7 four-pick,7 five-pick. These scans verify draft behavior, not game strength.

## Full release comparison

1,536/1,536 games completed,128 maps/both sides, CLI/SDK5.0.1, asserted engine3.0.0/build96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd.

| Policy | wins vs v61j /256 | wins vs early pack /256 | deaths vs v61j | deaths vs pack |
|---|---:|---:|---:|---:|
| v61j | 128 | 201 | 3.867 | 4.949 |
| cg-md245-plan | 77 | 160 | 8.359 | 10.340 |
| cg-md245-react | 77 | 160 | 8.316 | 10.328 |

Both selectors regress badly:77/256 vs the baseline and160/256 vs early pack, whose baseline wins201/256. Early-pack team gold at r200 changes726.56→732.54 for map-only (+0.8%), but deaths increase4.949→10.340 (+109%). A slightly better initial gold estimate does not compensate for a draft our current controller cannot execute safely. The reaction ablation produces the same aggregate wins and does not rescue it.

All bot-fault counts are zero, but fuel-exhaustion events persist. Candidate-side totals (v61j / early pack): baseline273 /219; map552 /417; reactive552 /417. New bodies/roles change ordinary-turn cost despite draft-only search. Do not promote this selector. The experiment establishes working bounded map selection and observed variety, not superior play.

See DESIGN.md for mechanics, role constraints, unimplemented role penalties and the pick-sequence confound. cases.csv, summary.json, paired.json and families.csv retain every outcome. draft_scan.csv includes measured budget/composition per map. hashes.json freezes source/maps/WASM. Reproduction scripts and exact manifests are included. No fresh live ladder census, real-opponent qualification, unseen-map gate or live-slot change.
