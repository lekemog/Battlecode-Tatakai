# #45 — zero-deposit losses on the_pack: replay study and local reproduction

Date: 31 October 2026. Baseline: v50c (`2d93a142`, branch `claude/vibrant-turing-rtpcwn`). Ladder engine 2.0.0.

## Summary

On `02the_pack` the only altar is ringed by one 48-camp group. Opponents open a gap by killing a few camps and bank through it. v50c never banks, because its altar pathing ignores gaps and its fallback targets the whole ring. The siege planner rejects the whole ring as infeasible, so no champion attacks it. Carriers keep farming with growing bags until they die or the game ends.

Reproduced locally on both sides against `x_daniel8`. As side B, v50c banks 0 in 2,000 rounds.

## Map facts (decoded from the replays)

- 45×45, no walls. One altar at (22,22).
- It is enclosed by a closed ring of 48 camps. All belong to **camp group 0**, at 1,350 HP each (64,800 total). **Correction (4 Nov):** I first wrote that these camps do not respawn, reading `respawnRounds -1`. That value only means the group is alive. When all 48 die, the group's reward can be captured and the ring respawns 40 rounds later (seen in the post-#222 ladder games below).
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

## Candidates 2 and 2b: `bots/v50c-breach`, `bots/v50c-breach2` (breach targeting)

**v50c-breach** builds on v50c-ringgap. A carrier with at least `ring_min_gems` that cannot walk to the sealed altar attacks the next camp on the cheapest breach path. The path comes from a 0-1 search over seal-zone tiles: the fewest camps between our walkable region and free floor in submit range. Seen gaps cost nothing, and ties go to the path nearest our spawn. The new mode runs between tribute and farm.

- On the_pack, the search finds a single-camp diagonal breach, e.g. (25,21) from (26,20). There are 8 symmetric single-camp breaches, cheaper than the 2-camp gap Trzy used.
- Smoke game, side B vs `x_daniel8`: 501 banked (v50c 0). But breaching started at r90 with 1,000–1,200 HP champions, the camp fell only at r486, and we died 6 times.
- **The whole ring wakes when any member is hit.** The replay shows 0 → 48 awake ring camps, back asleep within roughly 10–15 rounds. The camps have range 3. Exposure counts: a melee attack tile is covered by 14 ring camps, the altar-adjacent tiles inside by 28, and the best range-3 attack tile by 3.

**v50c-breach2** attacks only from the least-exposed tile within the champion's own range. It breaches only when exposure × camp strength × 0.5 (attack cooldown 2) × rounds-to-kill fits `trip_pool`. Otherwise it keeps farming, and a stronger or longer-ranged ally may breach instead.

Paired the_pack batch (same 7 bench bots × 2 sides):

| Bot | Wins | Banked us / them | Zero-deposit | Games reaching 1000, mean rounds |
|---|---|---|---|---|
| v50c | 13/14 | 13,451 / 376 | 3 | 10, ~1626 |
| v50c-ringgap | 14/14 | 10,996 / 401 | 3 | — |
| v50c-breach | 13/14 | 9,984 / 1,217 | **0** | — |
| v50c-breach2 | **14/14** | 11,946 / 1,542 | **0** | 8, ~1553 |

Reading:

- Breach2 removes the zero-deposit games on this bench and wins all 14.
- Total banked is about 1,500 below v50c. That is within this bench's noise: ringgap moved 2,500 with no meaningful behaviour change.
- **Opponents bank more** (376 → 1,542) because our breach opens the ring for them too. Bench bots never breach by themselves. Against ladder opponents, who breach anyway, this cost should mostly vanish, but that is untested.

## Candidate 3: `bots/v50c-breach3` (breach2 + leave the ring by recall) — current best

Head-to-head, breach2 vs v50c (side B) exposed a second bug. From r1020 to r1440, all three of our champions idled inside the ring with empty bags. Only the altar field knows the gaps, so every other field (farm targets, spawn) is unreachable from the interior. When v50c's late full-ring siege woke the ring, all three died within four rounds (r1460–64).

Breach3 makes a champion inside the ring with less than `ring_min_gems` recall. Gems are kept, and `handle_tribute` has already banked any bag worth banking.

| Bot (vs 7 bench bots × 2 sides) | Wins | Banked us / them | Zero-deposit | Reached 1000 / mean rounds |
|---|---|---|---|---|
| v50c | 13/14 | 13,451 / 376 | 3 | 10 / ~1626 |
| v50c-breach2 | 14/14 | 11,946 / 1,542 | 0 | 8 / ~1553 |
| **v50c-breach3** | **14/14** | **14,375 / 1,364** | **0** | **14 / ~1461** |

Head-to-head vs v50c on the_pack:

| Bot | Side A | Side B |
|---|---|---|
| breach2 | W 350–0 | L 384–1091 |
| breach3 | L 367–1277 | W 1007–192 |

- In the breach3 loss, we breached at r635 but banked only 367 in five deposits. v50c besieged the full ring from r1375 and banked two hoarded bags (620 + 657) at r1489–93. That was its own siege, not our gap.
- Post-breach income in the mirror looked like the open question here; the 16-game head-to-head below settles it.

### Larger head-to-head: breach3 vs v50c, 16 games

Local games are deterministic and the seed comes from the map, so one match-up on `02the-pack` gives only two distinct games. `tools/replay/mapxform45.mjs` writes the 7 flipped and rotated copies of the map. All of them preserve the ROTATIONAL180 symmetry, so team B's spawn stays mirrored. A transposed copy was checked: same altar, 132 camps, 35 groups, and the ring is still one 48-camp group at 1,350 HP.

| breach3 vs v50c | Wins | Banked breach3 / v50c | v50c banked 0 | breach3 banked 0 |
|---|---|---|---|---|
| Original map, both sides | 1/2 | 1374 / 1469 | 0 | 0 |
| 7 copies, both sides | 13/14 | 13,548 / 1,663 | 12 | 0 |
| **All 16** | **14/16** | **14,922 / 3,132** | **12** | **0** |

- One-sided binomial against 50%: P(≥14/16) ≈ 0.002.
- The only loss on the copies was x2, side A: 887 vs 1,663.
- Facing an opponent that farms as well as it does, v50c banked zero in 12 of 16 games. That reproduces the #45 failure, and breach3 removes it.

**Scope:** a 60-round scan of all 70 maps bundled with cambc 4.0.0 logged `seal45 zone` only on `02the-pack`. Every other map behaves exactly like v50c apart from a one-time check.

**Still to do:**
- Fresh-seed confirmation.
- Ideally, opponents that breach early like the ladder top ten.
- The full 40-map bench is unnecessary by construction, but cheap insurance.

## Acceptance check on the ladder (4 Nov): fails Leke's bar, 3 of 6

Bar (from #45, 1 Nov): at least one deposit in every 02the_pack game against a top-25 opponent since v222 (31 Oct 23:21 UTC), first deposit before r700. Games come from `cambc matches list --team me --map 27a3bbc1-1f12-4051-a0ce-739ff3421e06`: 63 the_pack games since the cut-off, 6 of them against the top 25 by the 4 Nov ladder, all unranked losses. Every version live in that window descends from v50d, so all include breach3. Checked with `python3 -I tools/replay/acc45.py <dir>`.

| Game | Opponent | Side | Banked us / them | Deposits | First deposit | Collected | Lost to deaths | Deaths | Pass |
|---|---|---|---|---|---|---|---|---|---|
| `7e624263` | #1 Intercontinental Fish | B | 0 / 1078 | 0 | — | 635 | 573 | 9 | **no** |
| `1d727b4c` | #5 test4 | A | 87 / 1094 | 2 | r622 | 822 | 735 | 13 | yes |
| `c5cde853` | #5 test4 | A | 462 / 1077 | 7 | r695 | 758 | 254 | 5 | yes |
| `022fb08e` | #5 test4 | A | 46 / 737 | 1 | r982 | 534 | 376 | 15 | **no** (late) |
| `221fc9a6` | #5 test4 | A | 25 / 965 | 1 | r833 | 253 | 203 | 9 | **no** (late) |
| `b5a96e8d` | #5 test4 | A | 449 / 1067 | 11 | r585 | 906 | 353 | 11 | yes |

- **Better than v50c, not fixed.** v50c's six top-25 the_pack losses all banked 0. With breach3, 5 of 6 games deposit. But the amounts are small, and three games miss the r700 bar.
- **The breach mostly waits.** Our champions attack from range 1–2, so the best attack tile is covered by about 15 ring camps. The logs show expected damage (`need`) of 2,000–3,600 HP against a budget (`pool`) of 1,200–2,000, so carriers keep farming. The first ring kills that we made came at r502–917.
- **Top teams farm the whole ring.** In all six games, all 48 ring camps died, the opponent captured the reward, and the ring respawned 40 rounds later before being cleared again (`7e624263`: cleared r768, respawned r814; cleared r991, respawned r1035). The ring is a contested jackpot, not a static wall, and any gap closes again with each respawn.
- **We die around it.** In `7e624263`, five of our deaths between r466 and r691 were within 8 tiles of the altar. One of them, at r656, cost a 187-gem bag that the opponent then carried. Losses to deaths ran 203–735 gems per game against 253–906 collected.

**Reading:** sealed-altar access is no longer the main failure against top teams. What remains is surviving and banking while the opponent contests and farms the ring, which overlaps #46 (carrier safety). Possible next steps, untested:
- breach from range 3, where 3 camps cover the attack tile, for champions that have that range;
- treat a fully cleared ring as a 40-round banking window;
- carry smaller bags near the ring when enemies are seen.

## Candidate 4: `bots/v50h5e-breach4` (calibrated breach on the live bot) — negative

Built on the live bot v50h5e, whose breach code is breach3 unchanged.

**The change.** The breach estimate uses the ring's raw damage rate (exposure × camp strength × ½), because the measured ladder rate was 120–184 HP a round and armour barely reduced it. It applies the 1.6× `camp_safety_margin` against health above the recall threshold. A carrier shares the kill time with allies in range, holds at the breach spot for up to 60 rounds when only a full team could afford the breach, and aborts mid-breach when its health cannot pay for the rest of the kill.

Test: `02the-pack`, 7 bench bots × 2 sides, plus 16 boards head-to-head. Summarised with `python3 -I tools/replay/pack45.py <dir> -v`.

| Bot | Wins | Banked us / them | First deposit median | After r700 | Deaths | Gems lost to camps / champions |
|---|---|---|---|---|---|---|
| v50h5e (live) | 14/14 | 14,309 / 949 | r514 | 2 of 14 | 48 | 2,647 / 197 |
| v50h5e-breach4 | 14/14 | 12,212 / 660 | r831 | 11 of 14 | 29 | 2,883 / 457 |

- **Head-to-head, breach4 vs v50h5e:** 15/16 wins, banked 15,831 vs 10,744. But breach4 mostly banks through gaps that the live bot opens.
- **Why it fails:** all three drafted champions attack from range 1–2, so 15 ring camps cover the best spot. The correct estimate needs 3,000–5,800 HP of headroom against 300–1,100 available. In `h_vatsal` A the bot logged `wait` 1,100 times and never breached. Carriers go back to v50c-style hoarding: later deposits, two near-zero games (54 and 38), and the r700 bar missed far more often.
- **Lesson:** breach3's coin-flip breach is what produces early gaps. Its cost is the carrier's bag, so the next candidate keeps the coin flip for champions with small bags.

## Environment notes

- `bench/README.md` still says cambc 3.0.5 / engine 1.0.3. Ladder replays are now engine 2.0.0. `tools/replay/extract3.mjs` cannot decode them, so `extract4.mjs` is a patched copy for the cambc 4.0.0 visualiser.
- In sandboxes behind a TLS proxy, `cambc build` can fail to download wasi-sdk, CMake or ninja (`UnknownIssuer`). Fetching them with curl into `~/.cache/cambc/<name>/` works: wasi-sdk and CMake with the top folder stripped, ninja unzipped.
