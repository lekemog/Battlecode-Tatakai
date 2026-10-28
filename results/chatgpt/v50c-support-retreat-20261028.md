# v50c support and retreat candidates — 28 October 2026

Base: `bots/v50c` at `2d93a142df388db48596f82842cf7cca47809cec` on `claude/vibrant-turing-rtpcwn`.
These are experimental candidates, not measured strength improvements. No submission or match creation was performed.

## Exact changes

Each folder copies all 24 source files from the pinned base. Only one existing configuration switch changes false → true. All other files reuse the base Git blobs, preserving v50c ring-path caching, gated-altar handling, weights, hazard model and balance settings.

| Folder | Switch | Mechanism |
|---|---|---|
| bots/gpt-v50c-ally-range | sim_ally_range | Ctx::observe reads visible allies' runtime attack ranges; handle_enemies uses a.range to estimate arrival into attack reach. |
| bots/gpt-v50c-channel-observe | observe_ally_channels | Reads allied recall/submission/teleport states without activating channel-aware combat policy. Observation-cost control. |
| bots/gpt-v50c-ally-channels | sim_ally_channels | Same state observations; channeling allies remain targetable and retain existing shields, but contribute no attacks, casts or prospective ready shield. They also stop triggering the engaged-ally hold/help overrides. |
| bots/gpt-v50c-retreat-move | retreat_preserve_move | Scoped retreat movement reservation reaches try_spell_enemy's existing exclusive-with-movement filter. Optional countercasts cannot consume an available retreat walk. Basic attacks remain allowed; the later escape-dash path is unchanged. |

## Why separate arms

Range and channel corrections can push fight decisions in opposite directions. Combining them initially hides the cause of any result. Compare channel-aware policy with both the unmodified base and the observation-only control, which has equivalent observation work. Check fuel on range and retreat arms too.

The channel arm is conservative: it suppresses allied contribution for the entire forecast rather than predicting channel completion or cancellation. This can underestimate support. Retreat preservation can forgo a useful spell even if the subsequent walk is blocked. Neither is automatically a net gain.

## Validation completed here

- Confirmed all four baseline switches are false and uniquely declared in v50c.
- Inspected the actual observation, forecast, engaged-ally override and spell-filter call paths.
- All four configuration headers pass g++ C++20 syntax checking with -Wall -Wextra -pedantic. The only diagnostic is #pragma once in a standalone main header.
- Each candidate differs from base in exactly one configuration declaration; every other source blob is reused.

The Battlecode CLI/SDK/engine is absent in this environment. Full bot compilation, mechanism replays, fuel measurements and matches have NOT been run. Do not deploy these candidates based on the configuration checks.

## Test order for Claude

1. Build pinned v50c and all four candidates using the CURRENT ladder-compatible SDK/engine. The repository's old bench README and cambc.toml mention older versions; confirm the current setup rather than installing those blindly.
2. Mechanism cases:
   - Ally ranged at distance 4–5: compare modeled arrival with base.
   - Ally recalling, submitting or teleporting beside an enemy: confirm no offensive contribution/engaged override while the existing shield remains.
   - Melee retreat with a ready movement-exclusive counterspell and an available safe step: confirm movement stays available. Include a blocked-step counterexample and a no-movement control.
3. Freeze maps, opponents, seeds, side and engine/build hashes. Run base and candidates on identical keys, including both sides. Use the team's current full regression suite, plus stronger opponents representative of ladder play.
4. Compare channel-aware against observation-only, then each against base. Report paired win/loss flips, delivered-gem margin, carrier losses, deaths, productive farming time and fuel suspension/error counts; break down by map and side.
5. Reject regressions; combine only independently successful arms and retest the combination on held-out keys. Opening a ladder test window requires the LIVE_SLOT.md procedure. No candidate is approved for live submission by this PR.

No opponent-model retraining, hazard-threshold changes, siege-health changes or draft changes are bundled.
