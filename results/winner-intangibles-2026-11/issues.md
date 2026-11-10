# Ready-to-post issues from the winner study

Format follows issues #53-#60. All are hypotheses from a different game's winner (see README.md in this folder); none is tested. Bot base for all: `bots/v50h5e` (live).

---

## Issue 1: Contest-gated opening cohesion (v50h18)

**Evidence.** In 20 decoded games against ha²t, Gamblr, Valenki and Kratos (issue #56) our champions died 70 times before r300, theirs 28. 57% of our early deaths were outnumbered by 2 or more (theirs 7%); 43% had no ally within 7 tiles. The winner of the Spring event gates aggression with one integer comparison, `enemy_dist * 2 <= my_dist * 3` (`bots/Khaos/units/states/route.py:57-68` in the winner repo at `daf4174`, observed). Our unconditional cohesion rule (v50h13/v50h14) was 47-48% in the mirror and cost 0.4 to 0.7 pick-ups by r200, which is the price of grouping on groups nobody contests.

**Question.** Does grouping only for camp groups the enemy can reach about as fast as we can (`d_enemy_spawn <= 1.5 * d_ours`) keep v50h14's death reduction without its pick-up cost?

**Process.**
1. Copy `bots/v50h5e` to `bots/v50h18`, header `// Polaris v50h18: ...`. Reuse the h14 block in `score_group`, but apply the distance penalty only to groups with `d_enemy <= 1.5 * d_ours` (fields already exist). One change.
2. Smoke, then `tools/lab/mirror.sh v50h18 v50p1` and compare with the live bot's win share against `v50p1`. Also the plain mirror (information only).
3. If it passes, both strong panels (`panel_strong.json`, `panel_strong2.json`).

**Acceptance.** Win share against `v50p1` above the live bot's, deaths per game down at least 10%, plain mirror at least 50%; then at least +4 wins over the baseline on the two strong panels combined with deaths not worse.

**Expected failure.** The pack waits for stragglers and loses contested camps; or gating on distance misses real contests on maps with long walls (walking distance versus spawn Chebyshev). **Cheap diagnostic.** Pick-ups at r100/r200, deaths by r150, share of early deaths with no ally within 7 tiles (`results/56-early-gold-strong-opponents/scripts/deaths_summary.py`).

---

## Issue 2: Integer outnumber check ahead of the fight simulation (v50h19)

**Evidence.** Same death data as above. The winner overrides its scoring with counts: attack despite an enemy only if at least 2 allies within distance² 25 face one enemy within 2 steps, or an allied turret is in sight, or the target is sealed (`attack.py:1441-1478`, observed). The live bot's `hazard_threshold` 0.2 (v50h5e) already moved in this direction and won two strong panels 22/40 against 15/40.

**Question.** Does a deterministic count rule, evaluated before the simulation (enemies within 5 minus allies within 5 at least 2: step to the nearest healthy ally instead of engaging), reduce lone deaths beyond what the learned hazard already does?

**Process.** `bots/v50h19` from `v50h5e`, one rule in the threats phase, guarded to rounds below 300 and to non-channeling, non-capturing champions. Tests as in issue 1. The mirror is not a valid gate for caution.

**Acceptance.** Same as issue 1, plus no drop in camp pick-ups at r200 larger than 0.3 in the `v50p1` games.

**Expected failure.** Retreat loops that surrender the middle (our source comments record that avoiding contested groups lost 24 of 166 points, `brain.cpp:2519-2520`); channel interruptions (never apply while submitting or recalling). **Cheap diagnostic.** Retreat episodes per champion, rounds spent on spawn, contested-camp share.

---

## Issue 3: Sequential paired testing for the local tiers

**Evidence.** The winner's tooling runs paired (both sides) trials until an SPRT bound is crossed (`tools/sprt_gauntlet.py:1-45`, observed), keeps side-asymmetry and map-by-opponent tables (`tools/_test_side_asymmetry.py`, `tools/map_opp_matrix.py`), counts timeouts as errors, and escalates 20, 30, 70 maps (`logs/`). Our gate is a fixed 366 mirror games, and each batch costs about 8 minutes of a shared 4-core machine.

**Question.** How many pairs would a paired SPRT have needed to reach the same verdict as the full gate on our stored candidate results, and would it ever have disagreed?

**Process.** Back-test only, no live slot: read per-map results from `results/56-early-gold-strong-opponents/out/mirror/` and earlier mirror folders; implement `tools/lab/sprt.py` (pair = both sides of a map; hypotheses 50% vs 55%; alpha and beta 0.05); report games saved and disagreements per candidate; stratify by map family.

**Acceptance.** Same verdict on every stored candidate with at least 30% fewer games on average, or a written reason it does not fit deterministic games.

**Expected failure.** Games are deterministic, so pairs are not independent samples of seeds and repeated candidate search inflates false positives; early stopping on one map family. **Cheap diagnostic.** Verdict versus pair count curve per candidate.

---

## Issue 4: Baked static map data to cut init fuel

**Evidence.** A ladder stdout line for a first turn reads `fuel r1 total 147842: init=103325 ... shop=11823 ... farm=2245`, so init dominates the opening. One finalist ships 208 pre-parsed maps and a `(width, height, core) -> map file` table (`lxorb/muteki bots/uewomirudake/lib/map/__init__.py:257-360`, observed) and so knows the board from turn 1. Sixteen new `03*` maps appeared on 2 Nov, so a table would start stale.

**Question.** How much first-turn and early-turn fuel can precomputed altar and camp distance fields keyed by a map hash save, with exact fallback to the runtime computation?

**Process.** (1) Measure only: fuel p50/p95 per phase for rounds 1-5 on all 86 maps from existing smoke runs. (2) If init is above 60% of turn-1 fuel, prototype `bots/v50h20` embedding fields for 10 maps, identical behaviour required (same decisions in a paired smoke on those maps). (3) No strategy overrides per map.

**Acceptance.** Bit-identical games on the 10 maps and at least 30% less turn-1 fuel; no change on unknown maps.

**Expected failure.** Binary size limit, a stale table after a map edit (hash mismatch must fall back), no real gain because early turns are not fuel-bound. **Cheap diagnostic.** `fuelExhausted` events and `FuelSpike` counts in rounds 1-20 across the bench.

---

## Issue 5 (low priority): failure-ban instead of retarget hysteresis

**Evidence.** The winner keeps no switching cost between states and instead remembers failed targets for 100 rounds (`harvest.py:27`, `route.py:11`, `secure.py:69`; observed); its authors attribute robustness to this but give no ablation. Ours uses `retarget_ratio` 1.35.

**Question.** On the economy tier, does `retarget_ratio` 1.1 plus a 40-round ban after a failed approach beat 1.35?

**Process.** One change in `bots/v50h21` from `v50h5e`; mirror (366 games), bench no-regression, then a mid-rank panel.

**Acceptance.** Above 55% of decided games over 366 games and no map 3 games worse.

**Expected failure.** Thrashing between camp groups; extra fuel from re-scoring. **Cheap diagnostic.** Reassignments per champion per 100 rounds.
