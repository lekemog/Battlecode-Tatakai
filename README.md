# Tatakai — Cambridge Battlecode 2026a

Our target is the UK top six. Start with [CURRENT_STATE.md](CURRENT_STATE.md), then [the strategy and team tasks](docs/UK_TOP6_PLAN.md) and [START_HERE_AGENTS.md](START_HERE_AGENTS.md).

## Current working state — checked 5 November 2026
Main is the coordination/documentation entry point; it does **not** contain the newest Claude gameplay line. Do not infer the live bot from the latest folder name or main's bot inventory.

| Item | Where to look |
|---|---|
| Latest patch analysis and source snapshot | [Claude patch branch](https://github.com/lekemog/BattlecodeConversation/tree/03b34544c02d0e9b501183f5d1f4a60759ceec9f) — commit 03b34544, 5 Nov |
| Latest development line | [v50/v51 working branch](https://github.com/lekemog/BattlecodeConversation/tree/claude/vibrant-turing-rtpcwn) |
| Patch/toolchain | Patch 4.0.0; Claude reports CLI 5.0.0 / engine 3.0.0, 128 maps; verify build and pool before every run |
| Reported stable baseline | v226 / bots/v50h5e; verify actual active submission in the CLI before testing |
| Candidate under evaluation | v51d; not promoted by this documentation update |
| Testing and account setup | [Existing testing guide](https://github.com/lekemog/BattlecodeConversation/tree/03b34544c02d0e9b501183f5d1f4a60759ceec9f/TESTING.md), [CLI guide](https://github.com/lekemog/BattlecodeConversation/tree/03b34544c02d0e9b501183f5d1f4a60759ceec9f/CLI_FOR_AGENTS.md); read current-patch overrides in CURRENT_STATE.md first |
| Submission coordination | [Live-slot log](https://github.com/lekemog/BattlecodeConversation/tree/03b34544c02d0e9b501183f5d1f4a60759ceec9f/LIVE_SLOT.md), [submission history](https://github.com/lekemog/BattlecodeConversation/tree/03b34544c02d0e9b501183f5d1f4a60759ceec9f/SUBMISSIONS.md) — check newest shared branch and active slot |
| Team task board | [Issue #40](https://github.com/lekemog/BattlecodeConversation/issues/40), current priorities #71–#73 |
| Prior multi-map experiments | [PR #51](https://github.com/lekemog/BattlecodeConversation/pull/51), historical engine-2 evidence |
| Pantheon winner ideas | [PR #52](https://github.com/lekemog/BattlecodeConversation/pull/52), research hypotheses rather than tested upgrades |
| Previous root documentation | [Historical README](docs/history/README-before-20261105.md), [historical onboarding](docs/history/AGENTS-before-20261105.md) |

## Working agreement
Claim one task with your branch and evidence. Use a new candidate folder and branch; one hypothesis per change. Book the shared live slot before submitting, activating or creating scrims. Confirm activation, pin opponents, record source/engine/map/submission IDs, and restore the intended baseline afterward.

Archived bots, reports and replays remain reproducible evidence. They are not all current recommendations. No gameplay code, active submission or scrim window was changed by this cleanup.
