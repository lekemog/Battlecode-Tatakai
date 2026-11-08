# Priority channel and draft memory: evaluation (8 Nov 2026, engine 3.0.0, 128 maps)

Question: should the bot use the SDK's two extra channels, `set_priority` / `query_priority` (32 bits per champion, readable from any visible champion) and 1,024 bytes of draft memory (written once in the draft, copied to each champion)?

## Facts measured
- **Cost** (probe bot, `cambc` 5.0.0): `set_priority` 32 fuel, reading own priority 50, reading each visible ally 37. About 150 fuel a turn for four allies; negligible against the 5-10K fuel cliff (`results/code-efficiency-2026-11-03`).
- **Plumbing** (`v51h1` with counters): on `00contest` each champion published 566-694 messages and read 305-432 from visible allies; on `01fracture` 10-61 published, 51-118 read.
- **Draft memory** was not built. Reasons: the heavy per-turn work is observation, and distance fields do not fit in 1,024 bytes; the opening is not where we lose (real games vs the top 10: capture #3 at round 61 vs 64, #5 at 110 vs 107).
- **History:** the earlier SOS / sighting / pack-sharing tests (win share .443 / .407) ran with `group_news` off because the features share the three tail bytes of the shared memory; no control isolated that, and the notes say a mirror cannot show a benefit of sharing.

## Candidates (all on v51d; the channel carries the old messages, `group_news` stays on; roster rank in the top bits keeps turn order)
| Bot | Change |
|---|---|
| `v51h1` | `peer_channel` + `share_sightings` |
| `v51h2` | `peer_channel` + `sos_radius 12` |
| `v51h3` | `peer_channel` + `phantom_mode 2` (shared pack sightings) |
| `v51h0` | control: `group_news` off, nothing else |

## Result: against the live bot (v50h5e = v226), all 128 maps x 2 sides = 256 games, 0 bot faults
| Matchup | Wins | Margin | Gold r100 / r200 / r400 vs live | Banked | Deaths |
|---|---|---|---|---|---|
| v51d (reference, no channel) | 141-115 (55.1%) | +41 | | 835 | 3.6 |
| v51h1 sightings | 136-120 (53.1%) | +45 | -2.8% / -3.0% / -2.9% | 835 | 3.6 |
| v51h2 SOS | 134-122 (52.3%) | +24 | +2.2% / -1.8% / -3.0% | 834 | 3.8 |
| v51h3 pack sightings | 134-122 (52.3%) | +41 | -2.6% / -1.8% / 0.0% | 831 | 3.6 |
| v51h0 control: `group_news` off only | 112-144 (43.8%) | -41 | -2.7% / -2.7% / -3.2% | | |

Noise at 256 games is about +-8 wins. All three sit 5-7 wins below v51d, inside the noise, with slightly lower income. **No evidence that sharing through the channel helps, and a small hint that it costs.**

**The control explains the old results.** Switching `group_news` off on its own costs about 11 points of win share (55.1% for v51d, 43.8% for the control). The earlier SOS / sighting / pack tests (.407 to .443) were run with it off, so they mostly measured that loss. With `group_news` kept on, sharing through the priority channel is close to neutral (52-53%, 2-3 points below v51d, inside the noise). Conclusion: `group_news` is valuable and must stay on; sharing sightings, SOS or pack information adds nothing measurable in the mirror.

## Decision
- Do not ship any of them. Keep `peer_channel` off (flag stays in the three folders).
- Draft memory: do not build.
- Limit of this test: it is a mirror against our own strategy, where nothing collapses a lone champion, so it cannot reward information. The right test is against the early-pack bot (`v50p1`) and a real-opponent panel; neither was run for this change.
- Related screening on the same day (vs v51d, 128 games): learned shop off 65-63 (+6.1% gold at round 400); + Capture emblem 68-60 (+6.9%); + Monster opener 62-66; + Skirmish 60-68; one capture recipient 58-70; Vesper-first draft 34-94 and 43-85 (income -7% to -9%).
