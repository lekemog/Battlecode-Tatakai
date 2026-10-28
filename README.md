# Polaris: Cambridge Battlecode 2026a bot (team LionelMSISS)

C++ bot for the Cambridge Battlecode 2026a game (champions, gems, altars, camps), built against the official `cambc` SDK. Current toolchain: `cambc` 4.0.0 (engine 2.0.0).

## Where things are
| Path | What |
|---|---|
| `bots/` | One folder per bot version, newest at the end of the alphabet. Old versions (v1x to v24x, early experiments) are in `bots/_archive/` |
| `bots/v40a/` | Best of the v35/v39 line (stand threshold, multi-trip siege with heal cost, recall package, ally-snapshot fix) |
| `bots/v50*/` | The next Polaris iteration (new base architecture plus the 4.0 patch adaptation); work in progress |
| `bench/` | Portable 7-opponent bench (`gauntlet.py`) and the map pools |
| `tools/panel/` | Pinned real-opponent panel (plays frozen versions of real ladder teams, paired with the live bot) |
| `tools/top10/` | Scrim scripts (`midtest.sh`, `top10test.sh`, comparison scripts) |
| `tools/scan/`, `tools/replay/` | Death and anomaly scanners, replay decoders |
| `results/` | Reports and raw results; `results/claude/patch-4.0.md` lists the 4.0 patch changes and item effects |
| `SUBMISSIONS.md` | Every ladder submission with its one-line reason and evidence |
| `LIVE_SLOT.md` | Who is testing on the ladder right now. **Check it before you submit or create match groups** |
| `START_HERE_AGENTS.md` | Guide for teammates and their agents |
| `NOTES.md`, `CONVERSATION.md`, `HANDOFF_*.md` | Findings, the coordination thread and hand-off notes |

## Test tiers (cheapest first)
1. **Weak bench**: 7 local opponents x 40 old maps (+ 30 new maps) x 2 sides. A version must not score below the live bot before submission.
2. **Sparring set**: 240 games against three stronger public-style bots. This is the discriminating local test (deaths, kills, gems submitted, gold, camp clears are the secondary metrics). Games are deterministic, so paired comparisons on the same games are valid.
3. **Pinned panel** (`tools/panel`): the live bot against frozen versions of ten real mid-rank ladder teams, with identical opponents and maps for baseline and candidate. Takes 60 to 90 minutes and needs the live slot.

## Rules for the live slot
Scrims always play whichever version is live, and the team shares about 30 unranked groups per hour. Anyone may submit and scrim, but announce it in `LIVE_SLOT.md` first and restore the previous version afterwards (`cambc submissions activate N`). Log every submission in `SUBMISSIONS.md`.

## Building and running locally
```
cambc build bots/v40a --release
cambc run bots/v40a bots/v35a --map maps/00eight.map26a --release --statistics out.json --json
cambc submissions list        # shows the live version
```
Work on your own branch, put new versions in new folders, and don't push to `main` directly.
