# Cassi & Issac handoff: working prototype, not qualified

Start with [CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md) for the role plan, code map, limitations and next experiments. Based on v61j at PR81 head9c973869; reported live submission245 was not independently authenticated. No live-slot changes.

Source freeze: `764b7ccd4c80bcbc5a9263556e992b1443db2e44`.

## Validation completed

- CLI/SDK5.0.1 release builds of all three variants. Actual engine3.0.0/build96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd asserted for every game.
- Pure boundary tests compiled with C++20, -Wall -Wextra -Werror; all assertions passed (TTL, weak-link HP, bounded regroup, channels/contact, stun immunity/priority).
- 96/96 completed games; zero batch failures, bot faults on either side, logged pair-action rejections or logged turn errors. Log scanning is capped by the bot/CLI limits; absence of logged errors is not full runtime certification.
- Eight preselected maps × both sides × two local opponents × three variants. This is a smoke screen only. Maps were restored from pinned repository snapshots; server refresh was unavailable. No tuning after outcomes, no top-ten panel or unseen-map qualification.

| Variant | vs v61j wins/16 | vs early pack wins/16 | Pair deaths/game vs v61j | Pair deaths/game vs pack |
|---|---:|---:|---:|---:|
| cg-ci-draft | 5 | 12 | 7.875 | 8.375 |
| cg-ci-pair | 6 | 12 | 7.250 | 7.125 |
| cg-ci-shop | 5 | 14 | 7.250 | 6.625 |

Pair deaths count the two physical champions, not independent linked-death episodes. Pair-only lowers pair deaths vs control7.875→7.25 against v61j and8.375→7.125 against early pack, but win changes are tiny and this screen cannot establish superiority. Shop adds two pack wins but no v61j gain.

The tradeoff is unresolved: pair-only early-pack round-200 team gold rises800.88→821.63, but pair gold falls187.81→150.63 and pair champion damage falls877.47→609.33. Against v61j, team gold rises775.75→825.13, while pair champion damage falls616.73→516.57 and pair monster damage also falls. Protecting the pair can move productive work to other champions. Do not infer that Cassi spell uptime or pair farming is optimized.

| Variant | Fuel exhaustion vs v61j | vs pack |
|---|---:|---:|
| cg-ci-draft | 401 | 312 |
| cg-ci-pair | 559 | 191 |
| cg-ci-shop | 584 | 443 |

Fuel events remain severe and rise in some cells; these are events, not affected-game counts. Most important next step: profile the heavy maps before a broader qualification, then test pair mechanics and stat buying separately. No deployment recommendation.

## Reproduce and continue

From an initialized CLI5.0.1 project with this repo bots/maps:
```bash
c++ -std=c++20 -Wall -Wextra -Werror results/cassi-issac-handoff-2026-11-10/test-pair-model.cpp -o /tmp/test-pair-model
/tmp/test-pair-model
python results/cassi-issac-handoff-2026-11-10/reproduce.py
python results/cassi-issac-handoff-2026-11-10/reproduce.py --all-maps
```

Full-map mode expands to1,536 games, not completed here. Preserve the initial eight-map evidence before overwriting output files. Follow with transformed/unseen boards and the coordinated pinned real-opponent panel described in the handoff.

Evidence: cases.csv, summary.json, hashes.json, exact relocation-safe manifest.txt, batch.log, kit-probe.txt, analyzer and two sample release replays (01yellow-brick-road side0, control/pair; chosen as a known fuel-stress map, not a representative result).
