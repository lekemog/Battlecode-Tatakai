# Tatakai — Cambridge Battlecode 2026a

Tatakai (formerly LionelMSISS) is our Cambridge Battlecode team. This repository holds the C++ bot, local benchmarks, replay analysis and team work queue.

## Start here

- **Current work and task claims:** [team coordination #40](../../issues/40).
- **Latest source baseline used in our top-ten study:** v50c at `2d93a142df388db48596f82842cf7cca47809cec`, on `claude/vibrant-turing-rtpcwn`.
- **Platform baseline:** submission 221, verified in the match UI on 28 October 2026. Treat this as a dated observation; check active submission before every test.
- Read the newest entries in [NOTES.md](NOTES.md), [SUBMISSIONS.md](SUBMISSIONS.md) and [CONVERSATION.md](CONVERSATION.md). Older live-version, deadline and map-count statements in historical documents are snapshots, not current configuration.

## Repository map

| Path | Purpose |
|---|---|
| `bots/` | Versioned bot sources; keep historical versions for comparisons |
| `bench/` | Portable benchmark materials |
| `tools/` | Scrim, benchmark and replay-analysis utilities |
| `maps/`, `maps2/` | Map assets; use the map hash and engine version recorded with each result |
| `data/`, `results/` | Evidence, experiments and test outputs |
| `top-replays/` | Reference replays; see its index |
| `START_HERE_AGENTS.md` | Agent workflow; historical status sections need checking against current notes |
| `HANDOFF_2026-10-25.md` | Dated handoff |

## Working together

1. Claim one current issue before implementing, naming the owner and branch. Keep banking, combat and opening-economy experiments separate.
2. Work on `chatgpt/<idea>`, `claude/<idea>` or `team/<person>/<task>`; submit a PR rather than pushing bot changes directly to `main`.
3. Put each candidate in a new bot folder. Preserve the baseline and avoid unrelated edits.
4. Include match IDs, maps, sides, engine build, submission version, numbers and the proposed mechanism. Distinguish observations from hypotheses.
5. Coordinate scrim quota and active submissions through the test owner. Explicit instructions from Leke may authorize a particular unranked batch; otherwise follow the shared test queue. Only the deployment owner submits candidate bots.
6. Compare candidates against the unchanged baseline on matched seeds/maps and both sides, then verify on fresh games. Reduced deaths alone is not success if income or banked gems deteriorate.
7. Use only the official game API and legal observations. Never infer private opponent code from a team name or one draft.

## Local testing

Use the SDK and engine required by the candidate and its recorded benchmark. Historical SDK versions and old map-name tables are not a current compatibility guarantee. Start with the commands documented alongside the selected bot and benchmark; record the exact command and version with results.

Keep reports and datasets in descriptive dated paths, and link active tasks from the coordination issue. Preserve historical evidence rather than deleting old experiments to tidy the repository.
