# Local bench: how we test a bot before it goes live

**Rule (Leke):** nothing is submitted, not even for a scrim test, until it has passed this bench without doing worse than the live bot. Every submission changes our ranked rating.

## What it is

The candidate plays every map in the ranked pool against 7 fixed opponents, once from each side.

- **Maps:** `pool6.txt` lists the 40 ranked maps (refresh with `cambc maps pull`).
- **Opponents** (`bench/bots/`), all frozen:
  - Tuning: `x_daniel8` (Daniel v8), `x_de41h4` (DE41H v4).
  - Held-out: `h_mohnish`, `h_deysag`, `h_vatsal`, `h_photon`, `h_apex`.
- **Size:** 40 maps × 2 sides × 7 opponents = 560 games, about 45 minutes with 2 parallel jobs.
- **Determinism:** games are deterministic, so rerunning the same bot gives the same result.

## Setup (once)

```bash
pip install cambc==3.0.5            # engine 1.0.3, same as the ladder (check: cambc --version)
cambc init myproj --yes && cd myproj && cp <repo>/bench/maps/*.map26a maps/   # the 40 ranked maps (or: cambc maps pull)
cp -r <repo>/bench/bots/* bots/      # the 7 bench opponents
cp -r <repo>/bots/<candidate> bots/  # candidate and the live bot (bots/kurians-t3-spawnfix right now)
rm -rf bots/*/.cambc                 # ALWAYS: a copied build cache makes cambc reuse the wrong binary
```

## Run

```bash
export PROJ=$PWD                   # your cambc project (contains bots/ and maps/)
export MAPS=$(cat <repo>/bench/pool6.txt)
JOBS=2 python3 -I <repo>/bench/gauntlet.py CANDIDATE x_daniel8,x_de41h4,h_mohnish,h_deysag,h_vatsal,h_photon,h_apex
JOBS=2 python3 -I <repo>/bench/gauntlet.py LIVEBOT   x_daniel8,x_de41h4,h_mohnish,h_deysag,h_vatsal,h_photon,h_apex
python3 -I <repo>/bench/permap.py CANDIDATE LIVEBOT  # losses per map, side by side
```

- `gauntlet.py` prints wins and total gem margin per opponent, then a `GAUNTLET <bot> wins N` total. Ignore the "/ 70*k" denominator: it is 80 per opponent on 40 maps.
- For a quick look at one map: `MAPS=00rows`. Before a full run, use `bench/weak13.txt` for the weakest maps.
- For a subset run, compare with `ANY=1 python3 -I <repo>/bench/permap.py A B`.
- Results are written to `$BENCH_OUT` (default `$PROJ/bench_out`).

## Pass rule

- **Full 560-game total:** at least the live bot's total, and the gem margin not clearly lower.
- **Per-map regressions** (`permap.py`): a map losing 3+ more games out of 14 needs an explanation. Moves of ±1-2 are noise; changing fuel use shifts some games.
- **Map-specific changes** (fingerprint rules): bench the affected maps against all 7 opponents. Confirm the other maps are untouched by construction or by a full run.

## Reference totals (engine 1.0.3, 40 maps, 560 games)

| Bot | Wins | Margin |
|---|---|---|
| kurians-t3-spawnfix (live v191) | 458 | +3138 |

On the 39 maps shared with the previous pool: v24w 448, v24y 443.

## Known limits

- The bench opponents are much weaker than the ranked opponents: the bench wins ~82%, ranked ~50%. The bench catches regressions and bugs, but it overrates improvements.
- Scrims against the top 4 lost 0/20 for every version tried. Ranked, or scrims against ranks ~150-300, remain the real judge, *after* this bench passes.
