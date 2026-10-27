# Start here: guide for teammates' agents (Kurians', Szymon's, ChatGPT)

Written by main Claude, which owns the ladder submissions and the scrim quota. Updated on Sun 18 Oct, ~16:30 UTC. **The ladder freezes at 22:59 UTC tonight. New ladder tests stop around 21:30 UTC.**

## Ground rules (please follow, they protect our ranked games)
1. **Check `LIVE_SLOT.md` before you run `cambc submit`, `cambc submissions activate` or `cambc match-groups create`.** Anyone on the team may submit and scrim, but scrims always play whichever bot is live and the team shares ~30 unranked groups per hour, so two overlapping tests corrupt each other. Open a window in `LIVE_SLOT.md` first, close it when you are done, and log every submission in `SUBMISSIONS.md`. (Updated 27 Oct: this replaces the old "never submit" rule.)
2. **Work on your own branch** (`<name>/<idea>`), with new bot versions in new folders (`bots/<name>-<idea>/`, copied from the live bot). Don't push to `main`.
3. **Every claim needs evidence:** match IDs, maps, counts. Every change needs a mechanism: which code lines, and why they produce the effect.
4. Official API only, no exploits.

## Current state
- **Live:** `bots/v19f` (version 131). Every submission and its one-line reason is in `SUBMISSIONS.md`.
- **How it was chosen:** paired ladder tests. Each candidate plays the **same 15 top-100 teams on the same maps** (`tools/audit/paired.py --same-as`). Weak-map score out of 75 identical games: v19f 10, v19a 7, v18x 6, v19b 3, v19c 1.
- **Read first:** `NOTES.md` (bottom = newest), then issues **#15** (weak-map diagnosis) and **#16–#21** (one cause each).

## Where we lose and why (summary of #15)
- **Weak maps:** contest, eight, collision, corners, stampede. Contest and eight are 0 wins vs the top 100 for every version.
- **What top teams do better** (detail in #15 and #20):
  - They earn ~26% more gold early and own 2× our items at round 50 (#21).
  - They bank small bags often, at the nearest central altar, and lose almost none (#16, #18).
  - They hold the middle and start fights 1.4–3.8× more often. Striking first is worth +10–25 points of win rate (#20).
  - Their frontliners have +300–560 max HP (#19).
- **Open problems with no working fix yet:**
  - **#17:** our defensive posture on contest/eight concedes the middle.
  - **#18:** we lose bags while carrying them.
  - Contest and eight have 0 wins.

## Data you can use
| What | Where |
|---|---|
| 164 top-vs-top replays (top-20 teams; both top 10 in 95) | `top-replays/` with an index README. Watch: `cambc view top-replays/<id>.repl26a` |
| Replay → JSON decoder | `tools/replay/extract.mjs` (needs the visualiser assets that `cambc view` downloads) |
| Our weak-map decision traces (what our bot decided before each death) | `results/traces/` |
| Analysis scripts | `tools/audit/` (`weakmap.py`, `bags.py`, `posture.py`, `traces.py`, `fightcal.py`, `topfights.py`, `topfights_report.py`) and `tools/howtheywin.py` |
| Map names ↔ files | see `README.md` |

Our own decoded top-100 games (~700) live in main Claude's container, not in the repo. Ask in an issue for specific match IDs or aggregates.

## How to get something tested
1. Open an issue (or comment on #15–#21) with your hypothesis, the evidence and your candidate folder or branch.
2. Main Claude will:
   - build it and run the local faux gauntlet (`tools/gauntlet.py`; useful as a crash/regression screen, biased against health/draft changes);
   - run a paired ladder test on the same games as the live bot;
   - post the per-game result back on your issue.
3. Deployment only happens when the candidate wins more of the identical games than the live bot.

## Good first tasks
- **#18 bag conversion:** where exactly are our carriers dying between camp and altar? There are traces for every death.
- **#17 defensive posture:** what should "defensive" do on a map whose only altar is in the middle?
- **Contest / eight:** watch 2–3 top-vs-top games for each map in `top-replays/` and describe their opening (first 150 rounds) concretely. Who goes where, and when they first bank.
