# Faux opponent execution lab

The official engine can now run these opponents locally, without login, submissions or platform scrims. The lab measures both teams so a faux strategy can be improved independently of the main candidate.

## Setup

From the repository root:

```sh
python3 tools/setup_faux_lab.py
.venv-faux/bin/cambc --version
python3 tools/faux_lab.py --cli .venv-faux/bin/cambc --candidate v17w --out results/local/example
```

On Windows use `.venv-faux/Scripts/cambc.exe`. Installation pins official `cambc==2.2.4` to match this repository. Its managed WASI SDK, CMake and Ninja are cached in `.engine-cache/`. They are downloaded, not committed. If direct release downloads are restricted, use the official WebAssembly/wasi-sdk, Kitware/CMake and ninja-build/ninja releases with the exact versions requested by the CLI; never use an unofficial mirror. This study used WASI SDK33, CMake3.31.8 and Ninja1.12.1. Keep the repository's published maps; init can refresh them when the platform is reachable.

The default is six maps, both sides, with the four original faux bots plus three new variants. Use `--maps` and `--opponents` to narrow a mechanism check. Output directories must be new so evidence cannot be silently overwritten. Local replays are deleted after statistics are recorded unless `--keep-replays` is passed. `runner.txt`, raw stats and build logs remain local; use `tools/export_faux_study.py` for a report without diagnostics.

## Opponent roles and evidence

| Bot | Role | Status |
|---|---|---|
| fz_solo | Frequent-bank independent farming | Original retained; all attempted replacements failed or tied |
| fz_hunt | Reckless bag-hunting pressure | Original retained; catches weaknesses the safer hunter misses |
| fz_herd | Early objective rush | Original retained as a distinct stress case |
| fz_tank | Health stacking | Original retained |
| fz_herd_v4 | Same herd bot, siege starts at600 instead of150 |18/34 against parent; contest2/2; narrow alternative |
| fz_hunt_v3 | Same hunter, fight need0.85 instead of0.45 |19/34 against parent; weaker than parent against v17w in the six-map screen |
| fz_tank_v2 | Mixed durability/damage plus bounded execution fixes |14/34 against parent; useful specialist, not general replacement |

Every new bot has its own source folder. Generators recreate rejected arms for investigation; they are not the default opponents. Do not turn local scores into a claim of top-100 equivalence. These bots still share Polaris ancestry and therefore share blind spots.

## Two learning questions per match

1. Does the main candidate withstand the strategy? Use official outcome/tiebreak, then submitted value, bag losses and fuel.
2. Does the faux bot execute its strategy well? Inspect both sides' first purchase and tribute, earned gold, camp-clear events, damage, deaths, carried-gem losses and timeline samples. First purchase alone does not measure purchase delay: affordability and item owner need a separate join. Capture events are champion-attributed events; they are not automatically unique physical clears. The distinct-group count measures coverage, not repeat captures.

Timeline horizons are explicitly sample indices100/200/300/400; missing or ended timelines stay null. MaxHealth is not exposed in these summary timelines and remains null. No route, pursuit-efficiency or exact formation claim follows from these totals; use a retained replay and a separate decision trace when that question matters.

Raw win percentage can be diluted by adding easy clones. The family check groups original and variant opponents: a candidate passes a map/side only if it beats every tested variant in that family. Missing games make the cell incomplete rather than a loss. Report raw per-opponent denominators alongside this deliberately strict robustness measure. A lower family pass count is not statistical proof of ladder strength.

See [the dated study](results/chatgpt/faux-lab-2026-10-18/report.md) for measured outcomes, rejected changes and limitations. Main Claude retains all platform test and submission ownership.
