# Reproduce the sandbox
Frozen: 480 cases, 40 unique archived maps, both sides, two policies and three opponents. Separate from the earlier 72-game test.

Recover bots/v50h5e, bots/v51d, bots/v50p1 and bench/maps from source commit 03b34544c02d0e9b501183f5d1f4a60759ceec9f. Candidate is this PR's bots/chatgpt-v50h5e-history. Configure CLI/SDK 5.0.0; copy sources without build caches. Put maps under PROJECT/maps-sandbox/. validation.json pins source hashes; plan.json pins map hashes.

Run python make_current_manifest.py PROJECT from this directory, then in PROJECT:
cambc run-batch sandbox-current/manifest.txt --jobs 8 --release --json --timeout 300 --log-limit 0

Run python analyse_sandbox.py PROJECT. It rejects mismatched engine/build and requires all 480 cases before producing full comparisons. For cached aggregation, copy this directory's index.json, plan.json and compact.json into PROJECT/sandbox-current/ first. The four release-built bot folders are required for binary/source provenance generation.

Current verified CLI: 5.0.0. Actual match engine: 3.0.0, build 96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd. CLI, SDK, engine and balance-patch versions differ. Read RESULTS.md for scope and no-promotion decision. No live activation, platform unranked games or quota use. This is not all-128-map qualification.
