# Ready-to-post issues from the unit-coordination study

Format follows issues #53-#60 and `results/winner-intangibles-2026-11/issues.md`. All are hypotheses; none is tested. Bot base: `bots/v50h5e` (live). Evidence is in `results/unit-coordination-2026-11/README.md` (sections 2 to 5). Mirror games are not a valid gate for caution or cohesion changes (TESTING.md section 3): use `v50p1` first, then the strong panels.

---

## Issue 1: Death and grave memory (v50h20)

**Evidence.** In the 10 Fish games (`results/fish-watch-2026-11/`, decoded) our champions lose 104 lives against Fish's 21. 66% of our deaths are followed by another death of the same champion within 300 rounds and 37% are within 8 tiles of that champion's previous grave. 78% of our deaths have an enemy champion near and no camp in reach; 19% have both; 3% a camp only. No `banned_until_` write in `brain.cpp` is keyed to our own death (lines 862, 1795, 3145, 3259, 3326, 3356, 3528, 3592, 3623, 3673), and `track_group_enemies` is off. Other bots flag a place as dangerous after a loss and clear the flag after a short time (4 Musketeers 2023 sector control status; Gone Fishin' 2023 dangerous wells).

**Question.** Does a ban on the group (and the tiles within 8) where a champion just died, lifted when two allies are within 7 of the target or after N rounds, cut repeat deaths without losing contested camps?

**Process.**
1. Copy `bots/v50h5e` to `bots/v50h20`, header `// Polaris v50h20: ...`. On a confirmed death, set the champion's `banned_until_` for the nearest group to `round + 120` and publish one bit in the spare shared bytes so allies apply a x0.3 rate to that group for 40 rounds. One change.
2. Smoke, then `tools/lab/mirror.sh v50h20 v50p1`; record repeat-death rate (same champion, within 8 tiles, within 300 rounds) from the decoded games.
3. Plain mirror for information. If deaths fall at least 10% against `v50p1`, run both strong panels.

**Acceptance.** Win share against `v50p1` above the live bot's, deaths per game down at least 10%, repeat-death rate down by a third, plain mirror at least 50%; then at least +4 wins on the two strong panels combined with deaths not worse.

**Expected failure.** The banned group is the valuable contested one (our source comment at `brain.cpp:2519-2520` records that avoiding contested groups lost 24 of 166 points); a ban without the ally-count release makes the team give the centre away. **Cheap diagnostic.** Pick-ups at r100/r200, repeat-death rate, rounds spent on spawn.

---

## Issue 2: Post-contact regroup and respawn join (v50h21)

**Evidence.** Crater against Fish (match `0a4f8e76`): our Heart, Marcella and Vendetta fought four Fish champions at r26-41 while Ryth and Varg stood 8-10 tiles away; four of ours died within 31 rounds; our recalled Ryth walked back alone to the Fish pack by r74. Oasis (`bb18f4cf`): Fish's four champions stay within 3-5 tiles from r10, ours spread over 15 columns, first death r31. Cohesion r30-200: ours 0.41 with the nearest ally more than 7 tiles away, Fish 0.28. Gone Fishin' 2023 section 5.6 dropped a lowest-ID leader (followers blocked the leader) and kept a 10-turn regroup toward the healthiest ally nearest the goal, lower-health units staying behind. The opening distance-penalty cohesion (v50h13/h14) lost pick-ups; this issue is a state after contact, not an opening rule.

**Question.** Does a regroup state (after our own death, an ally's death or a fight we leave, for 10 rounds, and for a respawned or recalled champion until it is within 6 tiles of a living ally) reduce chains after a first death without a pick-up cost?

**Process.**
1. `bots/v50h21` from `v50h5e`. State with a hard timeout and exits when capturing, channeling, banking or when no ally is within 15 tiles. Walk to the healthiest living ally; the lower-health champion stops, the higher continues.
2. Smoke, `tools/lab/mirror.sh v50h21 v50p1`, then both strong panels.
3. Measure chain length (deaths within 100 rounds of the first) from decoded replays.

**Acceptance.** As issue 1, plus mean chain length down at least 20% in the panel games.

**Expected failure.** Followers block the leader or wait for a champion that is capturing (the reason Gone Fishin' removed their first design); the opening ball lost 33% in the mirror (`v50e9`). Make sure the timeout is hard. **Cheap diagnostic.** Rounds in the regroup state per champion, pick-ups at r100, chain length.

---

## Issue 3: Count-based approach gate (v50h22)

**Evidence.** In the Fish games the share of champion-rounds with a favourable local count (allies within 7 at least enemies + 1, health at least 1.3 times) is 1766 against 682 unfavourable for us (2.6 to 1) and 2844 against 299 for Fish (9.5 to 1). Our rate of stepping toward the nearest enemy in a favourable state is 0.28, Fish's 0.27, so the gap is how often the state arises. Gone Fishin' 2023 section 5.3 chases only with "2+ more launchers than the other side". Closing-in margin changes in our simulation lost (`approach_margin` 0.5 and 1.0: wins 56 -> 47 and 31 of 80).

**Question.** Does a count rule that allows approaching beyond current reach only when allies within 7 minus enemies within 7 is at least 2, and otherwise holds position beside the nearest ally, convert more of our fights into favourable counts? (This is the same lever as issue 2 of `results/winner-intangibles-2026-11/issues.md`; do not build both, merge them.)

**Process.** `bots/v50h22` from `v50h5e`, one rule in the threats phase before the simulation, guarded to rounds below 400 and to non-channeling champions. Measure the favourable:unfavourable champion-round ratio from decoded replays as the primary metric, and kills per game as secondary.

**Acceptance.** Favourable:unfavourable ratio from 2.6 to at least 4 in the `v50p1` games, win share against `v50p1` above the live bot's, kills per game not lower; then the strong panels.

**Expected failure.** Holding position concedes camps and removes the kill chances the simulation finds; the count rule duplicates the simulation and changes nothing. **Cheap diagnostic.** Kills per game, pick-ups at r200.

---

## Issue 4: Draft Cassi and Issac on small maps and measure the extra body

**Evidence.** All 10 Fish drafts contain Cassi and Issac (draft id 3): `[1,6,3]` on three-pick maps, which fields four bodies (types 1, 3, 4, 7) against our three; `draft_pref` ranks it ninth and `draft_pref3`/`draft_pref4` are unset in `config.h`. A body is worth the same as a champion in the local counts of issue 3 (Fish is favourable 9.5 times per unfavourable). Earlier draft changes (v50h4, v50h7) lost in the mirror, and drafts are only measurable in the panel (TESTING.md section 3). The study decoded replays for 4 of 10 games with three picks.

**Question.** Does `draft_pref3` with Cassi and Issac in the first three (for example Heart, Marcella, Cassi) beat the current Heart, Marcella, Ryth on three-pick maps against the strong panel opponents?

**Process.** `bots/v50h23` from `v50h5e`, set only `draft_pref3 = { 11, 6, 3, ... }` (fill the rest from `draft_pref`). Smoke on the three-pick maps (`00anvil`, `00breadcrumbs`, `02the_pack`, `03homonoliths` are such maps in the Fish set); strong panels on the maps with three picks only; the panel is the gate, the mirror is not.

**Acceptance.** At least +4 wins over the baseline on the three-pick panel games, deaths not worse.

**Expected failure.** The reason our draft ranks Cassi and Issac ninth was not checked in this study; the extra body only helps if the team moves together; combine with issue 2 before judging. **Cheap diagnostic.** Deaths per game by champion, share of rounds with the nearest ally more than 7 tiles away.
