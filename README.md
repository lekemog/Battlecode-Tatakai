# Polaris — team LionelMSISS
Our shared Battlecode 2026a bot, research and experiment record. Polaris is written in C++ against the official `cambc` SDK (the existing project documents version2.2.4).

## Current checkpoint
**Latest recorded final submission: v19n / platform version148, 18 October2026 at20:19 UTC.** See [SUBMISSIONS.md](SUBMISSIONS.md) for the authoritative repository log; this is a recorded checkpoint, not a live platform-status query.

| Test cohort | v18x | v19f | v19n |
|---|---:|---:|---:|
| Five weak maps,75 games per arm | 6 | 10 | 12 |
| Strong-map subset,35 games per arm | 6 | 4 | 4 |

These are reused development cohorts, not overall ladder win rates. Contest remains0/15 in the latest tests; v19n wins1/15 on eight. Strong-map regressions remain open. [Final result and limitations](https://github.com/lekemog/BattlecodeConversation/issues/20#issuecomment-6254676865).

## Start here
- [Team review and next-version plan](docs/TEAM_REVIEW_2026-10-18.md): opponent styles, regressions, proposed solutions and validation.
- [Contributor guide](START_HERE_AGENTS.md): ownership, evidence and testing rules.
- [Experiment history](NOTES.md): chronological record, newest entries at the bottom.
- [Submission history](SUBMISSIONS.md): exact recorded deployments, including test arms.
- [Discussion archive](CONVERSATION.md): original messages and attribution.

## Repository map
| Path | Purpose |
|---|---|
| `bots/v19n/` | Recorded final candidate |
| `bots/v19f/`, `bots/v18x/` | Comparison baselines |
| `bots/v19m/` | Carrier/lifecycle experiment; not a proven improvement |
| `bots/` | Versioned candidates and historical references; names do not imply promotion |
| `tools/` | Scrim orchestration, local tests and analysis |
| `tools/replay/` | Replay decoding and analysis |
| `top-replays/` | Indexed top-team replay corpus |
| `results/` | Committed studies, traces and historical workbook |
| `maps/` | Seventeen competition maps |
| `docs/` | Curated team synthesis and planning |

## Shared ownership and credit

Polaris is a shared project by **Ben, Kurian, Leke and Szymon**. Our work spans strategy, replay analysis, implementation and testing. We retain original commit attribution and AI-assistance provenance.

Everyone can contribute a strategic review using the [replay-review guide](docs/REPLAY_REVIEW.md); observations and proposed alternatives are valuable independently of implementation.

## Collaboration
1. Only the designated main Claude session submits bots or creates platform scrims. Other contributors request tests in an issue.
2. Work on a named branch and open a PR; do not push directly to main. Put new gameplay candidates in new `bots/<version>/` folders.
3. Tie claims to source, match IDs or clearly scoped aggregates. Separate observations, hypotheses and tested effects.
4. Require local mechanism checks and paired external evaluation, including regressions. A small win-count increase alone is not proof.
5. Use only the official legal API. Never deploy untested changes or alter another contributor's experiment mid-run.

The recorded Sprint1 freeze is18 October2026 at22:59 UTC (23:59 Irish time). The final handoff says no more ladder tests tonight. Preserve the deployed checkpoint.

## Build and run locally
Example using the existing CLI syntax:
```bash
cambc run bots/v19n bots/v19f --map maps/p_2e9820ee.map26a --release --statistics out.json --json
```
This documentation example was not executed in this review.

Map filename prefixes:25d8 rows;2e98 collision;3991 monolith;3a5c contest;3e2d eight;699c ambush;7bfc pilgrimage;8192 expanse;9385 lanes;9925 fragment;b135 packs;b777 interlock;bb12 elkring;df22 rushbait_v2;e3c2 corners;f2b6 stampede;f930 swirl.
