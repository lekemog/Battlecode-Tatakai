# #45 — zero-deposit losses on the_pack: replay study and local reproduction

Date: 31 October 2026. Baseline: v50c (`2d93a142`, branch `claude/vibrant-turing-rtpcwn`). Ladder engine 2.0.0.

## Summary

On `02the_pack` the only altar is ringed by one 48-camp group. Opponents open a gap by killing a few camps and bank through it. v50c never banks, because its altar pathing ignores gaps and its fallback targets the whole ring. The siege planner rejects the whole ring as infeasible, so no champion attacks it. Carriers keep farming with growing bags until they die or the game ends.

Reproduced locally on both sides against `x_daniel8`. As side B, v50c banks 0 in 2,000 rounds.

## Map facts (decoded from the replays)

- 45×45, no walls. One altar at (22,22).
- It is enclosed by a closed ring of 48 camps. All belong to **camp group 0**, at 1,350 HP each (64,800 total). These camps do not respawn (`respawnRounds -1`).
- The ring interior has free floor next to the altar.
- `SUBMIT_GEMS_RANGE = 1`, read from the engine with a probe bot. A carrier must stand adjacent to the altar, so the ring must be breached.

## Ladder games

Both games: our side is B, and the spawns are side A (9–11, 21) and side B (33–35, 23). Totals match `data/tatakai-top10-20261028-fresh-metrics.json`.

| | Trzy Kwaterki `4490976d` | Claudus Maximus `b63ee66b` |
|---|---|---|
| Ring camps killed by them / us | **2 / 0** | **15 / 0** |
| Their first ring kill → first deposit | r335 → r568 (gap complete r544) | r308 → r596 |
| Final banked them / us | 1025 / **0** | 1004 / **0** |
| Our gems held at the end | 618 | 839 |
| Our turns in tribute mode (own stdout `trib`, r500 and r1000) | 0 | 0 |
| Rounds our champions carried ≥40 gems | 531 / 754 / 835 | 1269 / 1098 / 1115 |
| Peak bag | 364 | 563 |

- **Trzy** killed (19,25) at r335 and (20,24) at r544, a diagonal gap at the south-west. All 13 of their deposits came through it.
- **Claudus** made all 12 of their deposits through their own gaps. Their +424 at r1312 is almost exactly the 420-gem bag we lost at r1249.
- Our carriers almost never came within 6 tiles of the altar.

Commands:

```bash
node tools/replay/extract4.mjs $ASSETS replay.repl26a out.json
python3 -I tools/replay/ring45.py out.json 1
```

## Code path (v50c)

1. **Static altar field.** `World::altar_field` is computed once (`compute()` returns early when the slot exists, `world.cpp:217`). It treats every camp tile, living or dead, as a wall (`world.cpp:223`). On the_pack the distance to the altar is 16384 (unreachable) for the whole game. A gap opened by anyone is never seen.
2. **No gated-altar group.** The detector (`world.cpp:146–165`) needs no free floor within submit range. The ring interior is free floor, so `gate_group = -1` and banking goes to the `p5_ring` branch (`brain.cpp:2050–2069`).
3. **The whole ring becomes the gate.** `ring_gate()` walks the open path from spawn and finds group 0. While group 0 is "alive", `handle_tribute` returns false and the carrier farms.
4. **The gate is never attacked.** `choose_target` multiplies group 0's score by `ring_boost = 4`. But `score_group(0)` returns **0 with reject 5** ("beyond our whole team now"): `plan_siege` finds 64,800 HP infeasible. Four times zero is still zero.

## Local reproduction

Setup: cambc 4.0.0 (engine 2.0.0), the `02the-pack` map bundled with cambc 4.0.0, `--release`, opponent `x_daniel8`.

| Run | v50c side | v50c banked | Ring camps killed by v50c | First deposit |
|---|---|---|---|---|
| v50c | A | 1166 (won at r1773) | 48 (starting r1497) | r1730 |
| v50c | B | **0** (2000 rounds) | 0 | — |
| v50c-gatetrace | A | 1108 | — | — |
| v50c-gatetrace | B | **0** (2000 rounds) | — | — |

`bots/v50c-gatetrace` is v50c plus two log lines (TR45/GT45), with no behaviour change. It logs every 50 rounds while a carrier holds a bag. The output is in `trace-local-sideA.txt` and `trace-local-sideB.txt`.

- **Every carrier line on both sides:** `da16384 gategroup-1 gate0 hpleft64800 walk1 score0.0000 rej5`.
- **Side A** flips at r1500 to `hpleft9810 score172 rej0 target0`, and only then clears all 48 camps.
- **Side B** never flips (rej5 through r1850). This side difference fits the feasibility threshold. What first breaks the ring belief on side A at around r1500 is not yet traced.

## Hypothesis (to test, not yet confirmed)

The zero-deposit the_pack losses come from treating the ring as one group that must be fully cleared, plus an altar map that never learns about gaps. This is a design gap, not a fuel or crash fault. No `botFault` was recorded, and the trace shows `fuelfarm1` throughout.

Proposed isolated candidates (banking/pathing only, no combat or draft changes):

1. **Gap awareness:** rebuild the altar field over *living* camps when a camp near a sealed altar dies, so a gap opened by anyone is used.
2. **Breach targeting:** when an altar is sealed, target the cheapest camps that open a path to an altar-adjacent tile, instead of the whole group. Here that is 2 camps (2,700 HP) instead of 48.

Acceptance (from #45): fewer zero-deposit games and more banked gems on the_pack, no regression on pack wins or other maps, paired seeds/maps and both sides, then fresh games.

## Candidate 1: `bots/v50c-ringgap` (gap awareness) — result: no improvement on its own

Change: detect a sealed altar once and mark the camp tiles of nearby groups as the seal zone. Zone tiles seen without a living camp become passable, and the altar field is rebuilt with them.

Paired batch: `02the-pack`, 7 bench opponents × both sides, `--release`, cambc 4.0.0. Summarised with `python3 -I tools/replay/pack45.py <dir>`.

| Bot | Wins | Banked us / them | Zero-deposit games |
|---|---|---|---|
| v50c | 13/14 | 13,451 / 376 | 3 (mohnish A, photon A, daniel8 B) |
| v50c-ringgap | 14/14 | 10,996 / 401 | 3 (mohnish A+B, de41h4 B) |

- **Mechanism check:** every candidate game logged `seal45 zone 48 tiles`, and rebuilds fired on each new gap. But the first gap was only seen at r1539–r1827, because no bench bot breaches the ring and we only breach once the whole-ring siege becomes feasible late. With nothing to act on, the outcomes swing game by game, both up (daniel8 B: 0 → 1368) and down (daniel8 A: 1166 → 18). Small fuel and trajectory differences explain this better than the fix does.
- **Bench limitation:** v50c banks in 11/14 of these bench games. The bench reproduces the ladder failure only weakly, because ladder opponents breach early and contest the altar.
- **Conclusion:** gap awareness is necessary (our own breach must update the field) but not sufficient. Next is breach targeting: attack the cheapest camps that open a path, roughly 2 on this ring. Evaluate it with the same batch plus a breaching opponent.

## Environment notes

- `bench/README.md` still says cambc 3.0.5 / engine 1.0.3. Ladder replays are now engine 2.0.0. `tools/replay/extract3.mjs` cannot decode them, so `extract4.mjs` is a patched copy for the cambc 4.0.0 visualiser.
- In sandboxes behind a TLS proxy, `cambc build` can fail to download wasi-sdk, CMake or ninja (`UnknownIssuer`). Fetching them with curl into `~/.cache/cambc/<name>/` works: wasi-sdk and CMake with the top folder stripped, ninja unzipped.
