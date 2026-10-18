# Polaris: Battlecode 2026a bot (team LionelMSISS)

This is a shared workspace for Leke, Claude and ChatGPT. The bot is C++, built against the official `cambc` SDK 2.2.4. The ladder freezes on **Sunday 18 Oct 2026 at 23:59 (Irish time)**.

## Layout
| Path | What |
|---|---|
| `bots/v12c/` | **Current best, live on the ladder** |
| `bots/v12f/` | Candidate under test (v12c with fight memory and gold-map caution) |
| `bots/v12a`, `v11a`, `v9c`, `v7n` | Earlier versions, kept as references and benchmark opponents |
| `tools/` | Python scripts for scrims, A/B runs, benchmarks and match-summary analysis (see NOTES.md) |
| `results/Polaris_Testing_Results.xlsx` | Every scrim and ranked result, plus a "Top teams vs us" comparison |
| `maps/` | The 17 ladder maps (`p_<hash>.map26a`) |
| `START_HERE_AGENTS.md` | **Guide for teammates and their agents: rules, current state, data, how to get tests run** |
| `NOTES.md` | Findings, what was tried, and what to try next. **Read this first.** |
| `CONVERSATION.md` | Message thread between Claude and ChatGPT (newest at the bottom) |

## Collaboration rules
1. **Only Claude submits to the ladder** (`cambc submit`). Each candidate is run in real scrims against the same opponents back to back with the current best, and is kept only if it wins more. Untested code going live costs ranked games.
2. Work on your own branch: `chatgpt/<idea>` or `claude/<idea>`. Don't push straight to `main`.
3. To propose a change, open a **GitHub Issue** or a PR from your branch. Say what it changes and why, and give the evidence (match IDs, maps, numbers). Claude will run it through the scrim pipeline and post the result.
4. A new bot version goes in a new folder (`bots/v13x/`). Copy the closest parent and edit only what you need, so diffs stay readable.
5. Stay legal: use the official API only, with no exploits.

## Building and running locally
```
cambc run bots/v12c bots/v12a --map maps/p_2e9820ee.map26a --release --statistics out.json --json
```
Map hashes to names: 25d8 rows, 2e98 collision, 3991 monolith, 3a5c contest, 3e2d eight, 699c ambush, 7bfc pilgrimage, 8192 expanse, 9385 lanes, 9925 fragment, b135 packs, b777 interlock, bb12 elkring, df22 rushbait_v2, e3c2 corners, f2b6 stampede, f930 swirl.
