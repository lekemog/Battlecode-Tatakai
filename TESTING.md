# TESTING.md: how to test a bot version (written for teammates' agents)

Read this top to bottom before you run anything. Every rule here was paid for with a wasted afternoon.
Team Tatakai (ladder name `LionelMSISS`), Cambridge Battlecode 2026a, `cambc` 4.0.0 (engine 2.0.0).

## 0. Ground rules (the ones that bite)

1. **The live slot is shared.** Scrims, the panel and ranked games all play whichever submission is *active*. Before you submit, activate a version or
   create match groups, read `LIVE_SLOT.md`; add a row with your window; close it when done. Log every submission in `SUBMISSIONS.md`.
2. **Submitting replaces the live bot** (the new build activates by itself ~10 minutes after upload). So does `cambc submissions activate N` (also ~10 minutes,
   the old version stays live meanwhile). Use `tools/lab/submit_wait.sh` and `tools/lab/activate_wait.sh`: they wait until it is really live.
3. **`cambc login` lasts 7 days.** When it expires every account command fails with `Sign in first with cambc login` (and loops of retries burn quota). Run
   `cambc login` in the background, give the printed URL to a human to approve, and re-check with `tools/lab/live_status.sh`.
4. **Rate limit (HTTP 429).** Several agents calling the CLI at once get `Rate limit exceeded ... retry after N seconds`. Sleep 1 s between calls and retry with
   backoff. **Every failed panel attempt can create a new match group and burn the shared unranked quota (about 50 groups per hour):** `panel_run.sh` allows 4 attempts.
5. **Always copy bots without their build cache:** `rm -rf bots/*/.cambc` (a copied cache makes `cambc` reuse the wrong binary). `setup_lab.sh` does this.
6. **Games are deterministic** (same bots, same map, same side = same game). A repeat proves nothing; a paired comparison on identical games is valid, but 1 to 2 game
   swings on a single map are noise (changing fuel use or one extra branch changes the whole path). Judge totals and big map moves.
7. **Do not `pkill -f <pattern>`** in a shell whose own command line contains the pattern (it kills your shell). Kill by pid.
8. **Never commit anything that names another team's repository or code origin.** Opponent *team names* as data in result tables are fine.
9. Work on your own branch, new versions in new folders (`bots/vNNx/`), plain `git pull` (never `--rebase` while others push), commit only your own paths.

## 1. Which version is which

Current ladder bot line = **v50\*** ("Polaris v50", C++, `bots/v50*`). The older **v25 to v41** line (squad/cluster core) is far weaker on the ladder
(rank 321 vs 74); keep it only as a reference opponent. Old folders v1x to v24x are in `bots/_archive/`.

| Folder | What it is | Submission | Notes |
|---|---|---|---|
| `bots/v50h5e` | v50e1 with `hazard_threshold` 0.2 (disengage earlier) | **226 (live)** | won 2 strong panels 22/40 vs v223 15/40 |
| `bots/v50e1` | v50d with a Prospector (not Treasure) shop opener | 223 | fallback; won the mid-rank panel 35/45 vs v222 32/45 |
| `bots/v50d` | v50c + sealed-altar breach (`02the-pack`) | 222 | |
| `bots/v50c` | v50a + ring-gate banking for camp-ringed altars | 221 | |
| `bots/v50a`, `v50b` | imported base / first 4.0 adaptation | | |
| `bots/v50p1`..`p4` | **early-pack opponents** (rush the centre with a grouped team); *test opponents, never submit* | | see section 4 |
| `bots/v50q*`, `v50r*`, `v50h*`, `v50g*`, `v50e2..e9` | single-change candidates (see `results/5x-*` READMEs); most rejected | | |
| `bots/v40a` | best of the v35/v39 line (106/240 on the sparring set; the v50 line scores 235/240) | | |
| `bots/v25u` | older line, live until 26 Oct | | |

Bench opponents: `bench/bots/{x_daniel8,x_de41h4,h_mohnish,h_deysag,h_vatsal,h_photon,h_apex}` (frozen, all now beaten ~99%: **no longer discriminating**,
use them only as a no-regression check). The map pool is the 86 maps on the platform (16 new `03*` maps and `00happy_halloween` appeared on 2 Nov): refresh with `cambc maps pull`.

## 2. Setup (once per machine)

```bash
pip install cambc==4.0.0 && cambc --version          # must say 4.0.0
cambc login                                           # needs a human to approve the printed URL (7 days)
cambc view <any replay>                               # once: downloads the visualiser assets used by tools/replay/extract4.mjs
tools/lab/setup_lab.sh ~/lab v50h5e v50e1             # project dir, all current maps, the 7 bench opponents, and the bots you name
export PROJ=~/lab REPO=$PWD                           # printed by the script
```

`$PROJ/all.txt` is the list of current maps (one per line). Wrong toolchain download behind a TLS proxy (`UnknownIssuer`)? fetch wasi-sdk, CMake and ninja with
curl into `~/.cache/cambc/<name>/` (strip the top folder for wasi-sdk and CMake).

## 3. Which test for which kind of change (read this before choosing)

| Change type | Valid tests | Do NOT use as the gate |
|---|---|---|
| Economy, pathing, banking, shop, draft-neutral logic | smoke, bench no-regression, **mirror vs the live bot** (more than 55% of decided games over 366 games), mid-rank panel | |
| Fights, retreat, caution, escape, cohesion | smoke, **early-pack opponent** (section 4), **strong panels** (section 5, two independent map sets) | **the plain mirror**: self-play punishes caution. Example: `v50h5e` scored 41% in the mirror and won the real-opponent panels 22/40 vs 15/40 |
| Draft | the panel only (drafts only matter against real picks) | mirror, bench |
| A stuck state / one-map bug | reproduce locally on that map (both sides, flipped/rotated copies), smoke on all maps, then bench no-regression | |
| Anything touching banking on sealed altars | `02the-pack` family via `tools/replay/ring45.py` | |

## 4. Local tests (no account needed; 5 s per game)

```bash
tools/lab/smoke.sh v50h5e 02the-pack 01islands        # crashes, 'bot error' lines, error 97 'not in vision', fuel-outs. Must be clean.
python3 -I tools/lab/gauntlet_stats.py v50h5e         # 7 bench opponents x all maps in $MAPLIST (default bench/pool6.txt = 40 old maps), both sides
MAPLIST=$PROJ/all.txt JOBS=2 python3 -I tools/lab/gauntlet_stats.py v50h5e    # on the whole current pool
python3 -I tools/lab/stats.py v50h5e $BENCH_OUT          # $BENCH_OUT = the folder holding the bench_* output dirs (default $PROJ/bench_out); per-game means: kills, deaths, gems, gold at r200/r400, camp clears, error codes
python3 -I tools/lab/permap_losses.py v50h5e $BENCH_OUT   # losses per map
tools/lab/mirror.sh v50e2 v50e1                       # CAND vs BASE, all maps, both sides (140 games at 70 maps); prints share of decided games
```

* **Mirror gate:** share of decided games above 55% over 366 games (140 on the maps + 226 on rotated/flipped copies from `tools/replay/mapxform45.mjs`,
  which only handles ROTATIONAL180 maps), and no map 3 games worse. One-sided binomial p about 0.003 at 57.4%.
* **Early-pack opponent `bots/v50p1`** (= v50e1 with `hunt_mode 1`, `fight_margin 0`; it walks to the centre together with a tight pack like the top teams).
  It reproduces the real early deaths (first death median r112 vs r117 real; deaths 8.5 a game vs 13.0 in real losses). Run `tools/lab/mirror.sh CAND v50p1` and compare with the
  live bot's win share (v50e1: 63%): worth a panel if win share is higher AND deaths per game fall at least 10% AND the plain mirror stays at 50% or more. It is a stress
  test, not a replacement for the panel.
* **Rotated copies:** `node tools/replay/mapxform45.mjs <assets> <engine wasm> <in.map26a> <out_dir>` writes 7 new boards per map.
* **Quick checks on one map:** `cambc run bots/A bots/B --map maps/<name>.map26a --release --statistics out.json --json`.

## 5. Real-opponent panels (need the account and the live slot)

`tools/panel/panel.py` plays unranked match groups against frozen versions of real ladder teams, so a candidate and a baseline face **identical opponents, maps and sides**.
Configs (set `PANEL_FILE`): `panel.json` (ten mid-rank teams; one has left the ladder and is skipped), `panel_strong.json` and `panel_strong2.json`
(the four teams that beat us: ha²t, Gamblr, Valenki, Kratos; 5 maps each, different maps and flipped sides), `panel_top10.json` (current top 10).

Procedure (each panel is 20 to 50 games and takes 5 to 40 minutes):
```bash
# 0. announce the window in LIVE_SLOT.md; check tools/lab/live_status.sh
# 1. baseline with the live bot (opponents' CURRENT bots; records their pinned versions):
tools/lab/panel_run.sh tools/panel/panel_strong.json   sbase 226
# 2. each candidate: submit (replaces the live bot), then run pinned to the baseline's opponents:
tools/lab/submit_wait.sh /path/to/candidate_dir        # prints the new version N once it is live
tools/lab/panel_run.sh tools/panel/panel_strong.json   scand N sbase
# 3. repeat on the second, independent map set (panel_strong2.json) with its own baseline label
# 4. restore the intended bot:  tools/lab/activate_wait.sh 226     (and close your LIVE_SLOT.md row)
python3 -I tools/panel/panel.py compare sbase scand   # paired per-game table, wins, mean margin, deaths, kills
```
* **Decide on two panels together (40 games):** wins, mean gem margin and deaths per game. Needed: at least +4 wins over the baseline combined, deaths not worse, and
  the effect present in both panels. A single 20-game panel is only 1 to 2 standard errors; repeat before deploying.
* The panel waits for the candidate to be *really* live (activation is asynchronous) before it creates any group. It does not restore the previous version: you do.
* A submission needs a note: prepend `// SUBMISSION NOTE (<name>, <date>)`, evidence and the revert target to `src/main.cpp` of the submitted copy.

## 6. Decoding a real game (what to do after a loss)

```bash
cambc matches list --team me --kind ranked --limit 100 --json        # also --kind unranked/tournament, --cursor to page; --team <name|uuid> for anyone
cambc matches summary <matchId> --json -o s.json                      # per-champion metrics, timelines (gold, items), events (deaths, clears, deposits)
cambc matches download <matchId> -o m.zip && unzip m.zip              # replay.repl26a (+ our bot's stdout when we have one)
ASSETS=$(ls -d ~/.cache/cambc/assets/*/visualiser/assets | head -1)
node tools/replay/extract4.mjs $ASSETS replay.repl26a decoded.json   # omniscient per-round snapshots
python3 -I tools/replay/deaths54.py decoded.json <0|1> s.json         # label every death (outnumbered, duel, camp, lone-chase...)
python3 -I tools/replay/race55.py   decoded.json <0|1>                # gems collected vs banked over time, deposits
python3 -I tools/replay/clears55.py decoded.json <0|1>                # camp-group captures per team over time
python3 -I tools/replay/ring45.py   decoded.json <0|1>                # sealed-altar ring (02the-pack)
```
Team index: 0 = side A, 1 = side B. Match JSON has `draftPicks` per team (0 ryth, 1 vesper_vale, 2 vendetta, 3 cassi_and_issac, 4 stellar, 5 prism, 6 marcella,
7 willow, 8 ren, 9 varg, 10 tavi, 11 heart_of_ruin). Existing studies to read first: `results/45-gate-banking`, `53-*`, `54-*`, `55-*`, `56-*`,
`top25-unranked-2026-11`, `real-losses-2026-11-01`, `top10-strategies-2026-11` (when present), and open issues #54 to #59.

## 7. Reference numbers (so you can sanity-check your setup)

* Weak bench (7 opponents, old 40 maps, 560 games): v50d 560, v50e1 559; new 30 maps (420): v50d 415, v50e1 418. Older line v29e: 501 / 376. Saturated.
* Sparring set (three stronger public-style bots, 240 games; not in the repo): v40a 106, v50a 235.
* Mirror vs v50e1 (140 games): v50e2 41%, v50e4 36%, v50e5 54%, v50h5e 41% (but it wins real panels).
* Early-pack opponent v50p1: v50e1 beats it 62.8% over 366 games, 8.5 to 9.5 deaths per game.
* Strong panel 1 (20 games): v223 6, v50h14 9, v50h2e 3, **v50h5e 12**, v50r2 9. Strong panel 2: v223 9, v50h5e 10, v50r2 11.
* Mid-rank panel (`panel.json`, 45 games): v222 32, v223 35 (a week earlier, the old v25z line scored 1 of 50).
* Ladder: rank 74 (rating 1,974) on 2 Nov; the top 10 are 2,328 to 2,584.

## 8. What a result write-up needs (copy the issue READMEs' structure)

Summary, facts (with match ids), the mechanism (trace build that changes no behaviour), hypothesis, candidates with paired tables (wins, share of decided, gem margin,
deaths), scope scan over all current maps, still to do. Put it in `results/<issue>-<slug>/README.md`, commit only your own files, and say which tier each number came from.

## 9. Known open gaps (2 Nov): please test on these first

* **The 16 new maps** (`00happy_halloween`, `03ambush_field`, `03colosseum`, `03contours`, `03fan`, `03homonoliths`, `03honeycomb`, `03membrane`, `03one_gem`, `03reef`,
  `03riverbed`, `03showdown`, `03shrines`, `03the_front`, `03twisty`, `03ultrastarvation`): the live bot loses to the weakest bench opponent on `03colosseum` and
  `03homonoliths` (0 gems banked there) and ties 0-0 on `03one_gem`.
* Issues #54 (deaths), #55 and #57 (gem races), #56 (early gold vs the strongest teams), #58 (rush on `00eight`/`00packs`), #59 (round-2000 tiebreaks).
