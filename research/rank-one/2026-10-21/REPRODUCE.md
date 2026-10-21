# Reproduce this review

The raw binaries are third-party replays and are not republished here. Use the match IDs in FIELD_STUDY.md to download each replay through the official platform. Place each extracted `replay.repl26a` in a directory named by its match UUID beside these scripts. Use cambc 3.0.3's official visualiser assets containing engine `v1_0_1-*.wasm` for the current five-game series.

For each match:

```sh
node extract.mjs /path/to/official/visualiser/assets MATCH_UUID/replay.repl26a MATCH_UUID/decoded.json
```

Then from this directory:

```sh
python3 fish_summary.py
python3 turning_points.py
python3 frames.py
python3 export_evidence.py
```

`frames.py` needs matplotlib. It produces terrain-free spatial reconstructions, not screenshots of the live viewer. `export_evidence.py` can optionally receive a browser-history snapshot JSON path; without it, the committed partial history inventory is left unchanged.

Pure policy checks:

```sh
g++ -std=c++20 -Wall -Wextra -Werror -fsanitize=undefined,address policy_check.cpp -o policy_check
ASAN_OPTIONS=detect_leaks=0 ./policy_check
```

Observed result: compilation and assertions pass. Leak detection was disabled because this execution host cannot run LeakSanitizer under ptrace. These checks cover legal/illegal landing handling, overlapping-stun credit, rejecting predicted lethal landings and selecting a safe finishing delivery. They do not validate actual engine damage, game integration, ETAs, pathfinding, shared-memory coordination or competitive strength.

The main branch now has Claude's `tools/fishstudy.py` for broader collection. Do not treat array index as a game round: the decoder includes draft states, and the offset differs with draft size. Preserve engine and submission IDs, deduplicate replay hashes and distinguish confirmed events from proximity-based attribution.
