# Do pre-221 features still beat the current bot? (2026-11-02)

Live bot v50h5e (#226) against the three best pre-221 bots, all 86 maps, both sides (172 games each), local engine 2.0.0:

| old bot | what it was | v50h5e wins | margin |
|---|---|---|---|
| v40a | best of the v35/v39 line: stand threshold, multi-trip siege with heal cost, recall package, ally-snapshot fix, opponent-response model | 165/172 | +716 |
| v29e | ladder #217 (bounded bank attempt, oscillation detector) | 167/172 | +742 |
| v25u | ladder #204-212 | 169/172 | +712 |

Per family (vs v40a): v50h5e wins 100% on elk-herd, gem-only, gold-rich, large; 98% monolith, 93% standard, 90% gold-poor, **80% gem-starved**. Mean banked gems 1000+ vs 260-520 for v40a on every family except gem-starved (684 vs 56 on average, but 4 of 10 games reach round 2000). Raw output: `family_report` of `old_out`.

## Reading
- As whole bots the old line is dominated. No map family flips. So there is no "restore the old bot" edge, and v50 carries the economy features that mattered (ring-gate banking replaced the bank-attempt/oscillation fixes; hazard replaces the stand threshold).
- The only map where old bots beat us is `03one-gem` (4 of 6 games lost; v40a banks 119/126 gems in its games, v50h5e 28-35 when it loses; the bench there is decided at round 2000). Gem-starved is the only family under 90%. The old line collects more gems from non-group sources there; that is the one measured gap, and it overlaps issue #60.
- Features of the old line that v50 does NOT have, and are therefore worth porting tests (each as its own flag/version, sparring vs `v50p1` first, then strong panels; mirror invalid for caution):
  1. Opponent-response model (`opponent_response.h`, online estimate of whether enemies approach a camp): untested on v50. Predicted effect: small; deaths at contested camps.
  2. Multi-trip solo siege with heal cost and camp-HP memory (v39a): partly present as `big_siege_trips` in v50i1 (monolith only). Test generalising it to all groups.
  3. Recall package (transport/purse-free shop recall): v50 has `recall_in_target_travel`, `capture_before_recall` etc. all OFF; ablations existed for v50 flags, so test turning each on in turn.
  4. Siege 5-pick draft (Vendetta, Vesper, Ryth, Tavi, Marcella): v50 has its own learned draft; low prior.
- Honest limit: the old line was tuned for the pre-4.0 patch, so a feature that was good then may be neutral now; only paired tests on v50 decide.

## Next
Run feature 3 (flag flips) and 2 as candidates on `v50p1` + gem-starved/`03one-gem` maps; ship only what wins on both strong panels. Agents are rate-limited until 04:50 UTC; I can run the cheap flag flips locally meanwhile.

## Flag-flip results (vs v50p1, all 86 maps, both sides; baseline v50h5e 108/172, margin +174)
| variant | change | wins | margin | verdict |
|---|---|---|---|---|
| v50f1 | `siege_pool_from_recall = true` | 100 | +138 | worse (-8) |
| v50f2 | `capture_before_recall = 6` | 111 | +180 | +3, within noise; not shipped alone |
| v50f3 | `tribute_gems_danger = 40` | 107 | +172 | neutral |

Reproduce: copy `bots/v50h5e`, change the one constant in `src/config.h`, run `tools/lab/gauntlet_stats.py CAND v50p1` with `MAPLIST` = all maps. Consistent with the comments in `config.h` that these were already ablated. The only candidate worth a second look is `capture_before_recall` (try 3 and 10, then both strong panels) because a +3 repeated across values would be a signal; a single +3 is not.
