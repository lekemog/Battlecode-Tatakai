# How other Battlecode bots move and fight as a unit, and what transfers to our champions

Date: 2 November 2026. Read-only study. Nothing under `bots/` or `tools/` was changed, nothing was pushed, no bot or game was run. The only computation is a decode of the 10 Fish replays that were already in the repo. Different games (MIT: units, towers, launchers, rats; Cambridge winner: builders and turrets), so every transfer is a hypothesis.

Labels: **observed** (in a cited source or in our replays), **inferred** (reading between lines), **hypothesis** (ours, untested).

## Summary

- No source found has a formation engine. The mechanisms that exist are small and mostly count-based: regroup after a fight toward the healthier ally, chase only when ahead by 2 units, a "step up" rule when an ally is already in range, tile scoring that looks at allies and enemies nearby, and sharing danger reports. All are hand-coded, none is learned.
- The 2023 Gone Fishin' write-up is the most useful source. It records two grouping designs, one that failed (leader-follower, followers blocked the leader) and one that stayed (a short post-fight regroup toward the healthiest ally nearest the goal, lower-health units stay behind). It also records a chase gate of "2+ more launchers".
- The Cambridge winner (Khaos) does not move units relative to each other at all (section 1). Its only unit-vs-unit rules are integer counts for a single decision, as the earlier study found.
- In our 10 Fish games we lose 104 champion lives to Fish's 21. Fish keeps its champions closer together (share of rounds 30-200 with the nearest ally more than 7 tiles away: ours 0.41, Fish 0.28) and is in a locally favourable count 9.5 times for each unfavourable one against our 2.6 times. When both sides are in a favourable count, we step toward the nearest enemy at the same rate as Fish does (0.28 vs 0.27). So the gap is how often a favourable count arises, not how boldly we use it.
- The user's second observation holds: all 10 Fish drafts contain Cassi and Issac (draft id 3). On 3-pick maps Fish fields 4 bodies against our 3 (4 of 10 games).
- The user's first observation (solo farmers dying to camp monsters, then going back) is only partly supported. Only 23 of our 104 deaths had an awake camp in reach, and only 3 had a camp and no enemy champion near. But 66% of our deaths are followed by another death of the same champion within 300 rounds, and 37% of deaths are within 8 tiles of that champion's previous grave. Most of these returns are to a contested fight, not to a mob.

## 1. The Cambridge winner (HerbertTheBird/Cambridge-Battlecode, `daf4174`): unit-relative movement

Repo read locally at `/home/user/HerbertTheBird/Cambridge-Battlecode`, `bots/Khaos`. grep for escort, convoy, follow, formation, spacing spread, rally, lose, died found nothing relevant in `units/`. Findings:

| Question | Answer | Where |
|---|---|---|
| Claims | Territory claims only (Voronoi sets of tiles, turrets), not claims between units | `builder.py:146-162`, `pathing.py:236-261` (observed) |
| Spacing | **Not present** for builders. Spread is deliberate at spawn: four scouts picked to maximise pairwise angle | `spawn_plan.py:121-138` (observed) |
| Escort / convoy | **Not present** | grep (observed) |
| Leash | Round-1 builders stay within dist² 100 of the core | `builder.py:46-47` (observed) |
| Defender spawn | A new builder is spawned toward a visible enemy (dist² 20 of the core) only if no ally builder sits within the defence radius of the core | `core.py:61-101` (observed) |
| Turret/launcher placement | Placement is by BFS-distance gain; a gunner/sentinel leaves a tile if a friendly builder is strictly closer to the enemy than it is | `turret_gunner.py:74-84`, `turret_sentinel.py:120-127` (observed) |
| Reaction to losing a unit | **Not present.** Only a sentinel lock is released on death | `turret_sentinel.py:359` (observed) |

Conclusion: nothing there to copy for pack movement. Their units are mostly independent workers with a count rule at the point of contact.

## 2. Ranked mechanisms

Sources are public Battlecode postmortems from battlecode.org (PDFs fetched and read as text with pdftotext) unless stated. `GF` = Gone Fishin' 2023, `DAM` = Don't @ Me 2023, `NT` = no thoughts head empty 2023.

| # | Mechanism | Source | Label | How it maps onto our champions | Cheapest test (tier) | Expected failure |
|---|---|---|---|---|---|---|
| 1 | Regroup after contact toward the healthiest ally closest to the goal; the weaker unit stops and stays behind. Runs for 10 turns after a fight. | GF section 5.6, https://battlecode.org/assets/files/postmortem-2023-gone-fishin.pdf . Their first design (lowest-ID leader, everyone follows) was removed because followers blocked the leader (observed in the write-up). | observed (design and removal); effect size not stated | After a fight or after an ally's death, each surviving champion walks to the healthiest ally within 15 tiles for N rounds instead of resuming a solo target. Fits `retreat_ally_pull` (2) but that applies only while retreating. | `v50p1` stress opponent first (`tools/lab/mirror.sh CAND v50p1`), then both strong panels. NOT the plain mirror. | Pack waits for a champion that is capturing or channeling; concedes camps (the opening ball lost 33% in the mirror, `v50e9`). |
| 2 | Chase and push only when the local count is ahead by 2 | GF section 5.3: chase an out-of-range target only if no other target, the target is not a launcher, or "2+ more launchers than the other side". | observed | A numeric gate on `limited_chase` and on approaching: approach beyond the current reach only when allies within 7 minus enemies within 7 is at least 2. Complements the hazard disengage, which only subtracts. | `v50p1` then strong panels; check kills per game rise, not just deaths fall. | Same counts as the fight simulation, so it may add nothing; `approach_margin` 0.5 and 1.0 were rejected (wins 56 -> 47 / 31 of 80). |
| 3 | "Step up": if an ally is already in attack range of an enemy, step in instead of kiting away | DAM, kiting and step-up bullets, https://battlecode.org/assets/files/postmortem-2023-dont-at-me.pdf (about lines 425-447 of the extracted text) | observed | Equivalent exists: `help_engaged_allies` and `stand_with_engaged_allies` are on (`config.h`). Not new; the missing half is the lead unit pulling back to let others in, untested. | Already live; no test. | n/a |
| 4 | Death and danger memory shared through the comms array: report danger, avoid the place for a short time, flag cleared after a while | 4 Musketeers 2023, sector "control status" and "if a carrier encounters danger ... we report", https://battlecode.org/assets/files/postmortem-2023-4-musketeers.pdf (about lines 286-300); GF carriers mark wells dangerous when enemy launchers are seen, flag removed after a short time (GF about lines 165-176) | observed | A death at group G by champion X sets a ban or a heavy rate discount on G for that champion (and 1 bit shared for all) until an ally count there reaches 2 or N rounds pass. In our code no `banned_until_` write is keyed on our own death (writes at `brain.cpp` 862, 1795, 3145, 3259, 3326, 3356, 3528, 3592, 3623, 3673); `learn_state().deaths` only feeds the learned hazard. | `v50p1` stress test (reproduces champion-vs-champion deaths) and the Fish replay metric "same champion dies within 8 tiles of its last grave within 300 rounds" (37% now). | Gives up the one valuable contested group for good (our own comment, `brain.cpp:2519-2520`: avoiding contested groups lost 24 of 166 points). |
| 5 | Tile scoring with allies and enemies counted per neighbouring tile (XSquare micro) | Kragle 2025 MicroInfo (number of nearby enemies, distance to nearest enemy), https://battlecode.org/assets/files/postmortem-2025-the-kragle.pdf (about lines 745-760); SPAARK 2025 defaultMicro (penalties by allies around the tile, enemy range), https://battlecode.org/assets/files/postmortem-2025-spaark.pdf (about lines 338-352). The SPAARK ally penalty is specific to their paint rule. | observed (design); not a flocking term | Add a small ally-proximity bonus to the travel step and retreat tile choice (the retreat already pulls 2 tiles per tile toward an ally). Generic, cheap, a single term. | `v50p1`, plus the mirror as information only. | Clumping on a camp tile blocks capture tiles; Heart/Ryth melee reach conflicts. |
| 6 | Formation by spawn order and shape for the first units | GF section 5.4: spawn the first 4 launchers in a square, earliest spawned furthest out, because units act in spawn order; "wins about 2/3 of the game" against a version without it (author's claim, no sample size) | observed (claim) | Our champions do not spawn one by one; the equivalent is the opening staging point (`opening_party`, `staging_patience`). | The existing `opening_party 3` mirror (.471) is the only data; no cheap new test. | Low transfer. |
| 7 | Focus fire by a score: type value + hp attacked + missing hp/2 + 100 on a kill | DAM about lines 425-430 of the extracted text; GF 5.5: count friends that can hit each enemy, prefer one-shots | observed | `focus_s` already orders killable, Cassi/Issac, ranged carry, lowest effective health, shielded Heart last. Present. | none | n/a |
| 8 | Retreat only when it does not waste the approach; "do not retreat unless close to the tower" beat the older bots "by a very large margin" | SPAARK 2025, https://battlecode.org/assets/files/postmortem-2025-spaark.pdf (about line 223); Om Nom 2025: unconditional return at ~50 paint wasted ~10 attacks, https://battlecode.org/assets/files/postmortem-2025-om-nom.pdf (about line 127) | observed | Warning against more caution: our retreat knobs lose in self-play; the lesson is conditional retreat, not no retreat. Informs the stated direction of issue 2. | n/a | n/a |

Sources I could not use: the 2022 Whis repo (`github.com/christyjestin/battlecode22-whis`) shows only a README through WebFetch: "Soldiers will wait and/or regroup if they sense that they don't have enough teammates"; it gives no threshold, and the `src` directory was not fetched (disk was full, the clone failed), so that claim is observed as README text only. The 5 Musketeers 2022 guide says soldiers rush the weakest archon and watchtowers form a checkerboard; no code. The 2019 Big Red postmortem says tightly clumped preachers were easy AoE targets and describes a "lattice" with gaps so other units can pass: clumping has a cost when the enemy has area damage (observed). NT (https://battlecode.org/assets/files/postmortem-2023-no-thoughts.pdf) has launchers that group with other launchers when idle, kite after attacking, report enemies in the comms array so others travel there, and an HQ that "hallucinates" an enemy to pull launchers. No numbers. MIT's own Postmortems page and the open-source repos linked from the PDFs (for example `erikji/battlecode25`, `reeceyang/battlecode-2023`) were not opened; searches of GitHub code were not run.

What was not found anywhere: Lanchester-style force-ratio formulas, a rule of the form "attack when ahead by X percent" with a number other than GF's "2+ more", a stated rule to avoid trickle-in deaths, or leader-follower formation code that survived to the finals.

## 3. Our own evidence: the 10 Fish games

Method: replays in `results/fish-watch-2026-11/d_*/NN-*/replay.repl26a` decoded with `tools/replay/extract4.mjs` (it runs against the second asset folder in `~/.cache/cambc/assets`; the first folder is a different visualiser version and fails to import `PanelChrome-DXwmYkIC.js`). Unit types in the replay are draft id + 1 from id 4 up (7 marcella, 8 willow, 12 heart; type 4 is Issac). Positions are end of round, taken one round before each death; "near" is Chebyshev 7. Our side is the side with a `team-X.stdout` file. Maps identified from the README of that folder by round count.

| map | our side | team size | first death us / Fish | first death context (enemies / allies within 7) | alive 50 rounds later | chain (our deaths within 100 rounds, incl. first) | deaths by r300 us / Fish | all deaths us / Fish |
|---|---|---|---|---|---|---|---|---|
| 00ambush | A | 5 | 143 / 537 | 1 / 0 alone | 4 of 5 | 1 | 1 / 0 | 2 / 3 |
| 02the_pack | B | 3 | 466 / 399 | 0 / 1 (carrying 99 gems, nothing near) | 2 of 3 | 2 | 0 / 0 | 9 / 4 |
| 00anvil | A | 3 | 57 / 217 | 2 / 1 | 2 of 3 | 1 | 2 / 1 | 11 / 2 |
| 01shortcut | B | 4 | 315 / 393 | 1 / 1 | 3 of 4 | 1 | 0 / 0 | 3 / 3 |
| 00breadcrumbs | A | 3 | 107 / none | 2 / 1 | 1 of 3 | 2 | 2 / 0 | 11 / 0 |
| 03homonoliths | B | 3 | 362 / 631 | 1 / 0 alone | 2 of 3 | 1 | 0 / 0 | 4 / 1 |
| 02cuts | A | 5 | 733 / 212 | 1 / 0 alone | 4 of 5 | 1 | 0 / 2 | 1 / 5 |
| 00crater | B | 5 | 41 / 236 | 3 / 2 | 1 of 5 | 4 | 10 / 1 | 27 / 1 |
| 03colosseum | A | 5 | 133 / 77 | 1 / 3 | 3 of 5 | 2 | 6 / 2 | 12 / 2 |
| 00oasis | B | 4 | 31 / none | 3 / 1 | 2 of 4 | 2 | 6 / 0 | 24 / 0 |

(Match ids: the folder name after the number, for example crater is `03-0a4f8e76` in `d_6a27d888...`.) All 10 games lost; Fish has 21 deaths in total.

Reading:
- First death before r150 in 6 of 10 games (r31, 41, 57, 107, 133, 143). In 4 of these 6 a second champion dies within 100 rounds (crater 4 within 31 rounds, oasis, colosseum, breadcrumbs). Median first death: ours r138, Fish r314 (8 games where Fish loses anyone). Mean champions alive 50 rounds after our first death: 2.4 of 4.0.
- First death context, classed as alone (no ally within 7), outnumbered by 2 or more, equal count including the victim, supported, or no enemy near: alone 3 (homonoliths, cuts, ambush), outnumbered by 2+ 1 (oasis), equal count 3 (crater, anvil, breadcrumbs), supported 2 (colosseum, shortcut), no enemy near 1 (the_pack). This differs from the #56 finding (57% outnumbered by 2 or more): the first deaths here are mostly 1 against 1 or 2 against 2, and the collapse is in the chain after them (crater: r41 3 v 2, r44 3 v 1 ally, r54 1 v 0, r72 4 v 0).
- 63 of our 104 deaths are in three games (crater 27, oasis 24, colosseum 12). These are death spirals, not scattered losses.
- Cohesion rounds 30-200 (nearest ally more than 7 tiles away): ours 0.41 mean, Fish 0.28. Fish is tight in the games with early contact (oasis 0.06, crater 0.23).
- Trace of crater, r20-75 (our side B): our Heart, Marcella and Vendetta fight 4 Fish champions at (31-37, 19-24) while our Ryth stands at (36,11) and our Varg at (32-34, 6-12), 8-10 tiles away, from r23 to r41. Fish's Vendetta recalls home at 22 percent health at r53; our Heart stays until it dies at 4 percent. Our Ryth recalls home at 46 percent health (back at spawn (57,28) at r56, full health) and walks straight back to (39,23) by r74, next to the Fish pack at (31-33, 15-20); its next death is r180 (3 enemies, 1 ally near). Oasis, r10-35: all 4 Fish champions are within 3-5 tiles of each other; ours are spread over 15 columns, our Marcella is alone at (17,18) with 13 percent health at r30 and dies at r31.

Local count measure (champion-rounds r20-400 with an enemy within 8; favourable = allies within 7 at least enemies + 1 and health at least 1.3 times theirs, unfavourable = the reverse):

| | favourable | even | unfavourable | step toward nearest enemy (favourable / unfavourable) |
|---|---|---|---|---|
| ours | 1766 | 1249 | 682 | 0.28 / 0.24 |
| Fish | 2844 | 1076 | 299 | 0.27 / 0.27 |

Fish is in a favourable local count 9.5 times per unfavourable one; we are 2.6 times. Neither side steps toward the enemy more often when favourable.

## 4. Camp monsters versus enemy champions, and the "return to the grave" rate (new, from the coordinator's message)

Method: same decode. For each death, the previous round's snapshot gives enemy champions within 7 tiles and awake camp monsters with health whose attack range plus 2 covers the champion. Labels: champion (enemy near, no camp), both, camp (no enemy champion near), unseen. Return to the grave: the same champion dies again within 300 rounds at a tile within 8 of the previous death.

| | deaths | champion only | both | camp only | no source seen |
|---|---|---|---|---|---|
| ours | 104 | 81 (78%) | 20 (19%) | 3 (3%) | 0 |
| Fish | 21 | 7 | 1 | 11 | 2 |

| ours | count |
|---|---|
| deaths followed by another death of the same champion within 300 rounds | 69 of 104 (66%) |
| of those, within 8 tiles of the previous grave | 38 of 104 (37%) |
| deaths with a camp in reach | 23 |
| of those, same champion dies within 300 rounds at the same camp group or within 8 tiles | 9 of 17 that had a later death |
| deaths with a camp in reach and no enemy champion near | 3 (two on 02the_pack, one on 01shortcut) |

Reading:
- In these 10 games the dominant killer is the enemy champion pack (78%), not the monsters. Fish is the one that dies to monsters (11 of 21). The user's observation of solo farmers dying to the mob shows up only on the_pack and shortcut (long games with big bags, first deaths r315-r466), and the 99-gem Ryth death on the_pack at r466 had no enemy within 7.
- The return rate is real: 37% of deaths are within 8 tiles of the same champion's last grave within 300 rounds. In crater and oasis these are returns to the contested centre where the Fish pack stands, not to a mob. A grave memory needs to be keyed to "enemy pack was here", not only to camps.
- Caveats: one opponent, 10 games, three games hold 61% of the deaths; the camp test uses the "awake" flag at one snapshot; a camp that killed a champion and went back to sleep in the same round may be missed (this would undercount camps). The labels are not a damage attribution. The 56 study classified by the same radius (6 or 7) and found 43% of early deaths with no ally within 7.
- Existing code: groups get a ban for 8 to 60 rounds in several cases (retreat, standoff, capture timeout), and `track_group_enemies` (enemy seen near a group halves its rate for 20 rounds) is off. No ban is keyed to our own death at a group (checked by reading the `banned_until_` writes listed in the table above). So death memory is not tried.

Does anything in the other bots transfer? Only the danger flag with a short lifetime (GF, 4 Musketeers). It is a per-target failure ban shared with the team, and it is cheap, but those games had monsters or launchers as the danger; our dominant danger is an enemy pack that moves, so the flag must expire fast (the GF flag is "short"; the number is not given).

## 5. What already exists in `bots/v50h5e` and what was tested

| Mechanism | Setting (live value) | Result recorded |
|---|---|---|
| Pairs / squads | `squad_size 1`, `squad_until_round 0` | pairs until r150 (v50h2): .507 mirror, .564 on v50e1 (noise on rotated copies), 3/20 on strong panel 1 as v50h2e (SUBMISSIONS 225). Pairs vs `v50p1`: 60.0% vs 63.6% baseline (v50q3). |
| Opening ball / escort | `escort_until 0`, `escort_radius 2` | 46-94 in the mirror (v50e9), .329 (v50h3) |
| Opening party of 3 | `opening_party 0` | .471 (v50h1) |
| Opening cohesion (distance penalty when more than 12 tiles from an ally's target, before r150) | not in the live file; built in v50h13/v50h14 | .471 / .479 mirror; 9/20 vs 6/20 on strong panel 1 (SUBMISSIONS 224) |
| Disengage earlier | `hazard_threshold 0.2` | live; strong panels 22/40 vs 15/40, mirror .41 |
| Committed homeward retreat | `retreat_mode 0` | .357 mirror; 60.7% vs `v50p1` |
| SOS walk to a retreating ally | `sos_radius 0` | .443 (v50h11); mirror only |
| Unseen pack in the simulation | `phantom_mode 0` | .250 (v50h9), .407 (v50h10) |
| Local-power tactics | `tactics_s 0` | 11-129 (v50e8) |
| Allies join the simulation only in contact | `sim_ally_contact 0` | 3: vs `v50p1` 67.1% (baseline 63.6%), deaths 6.8 vs 8.5, but a note says "cuts deaths but loses ground (wins 56 -> 29/80)" |
| Closing in needs extra margin | `approach_margin 0` | 0.5 / 1.0 rejected |
| Help engaged allies / stand with engaged | both true | live |
| Hunting | `hunt_mode 0` (on in the `v50p1` opponent only) | the stress opponent |
| Shared enemy sightings | `share_sightings false`, `group_news true` | untested alone |
| Squad leader selection and handoff | `capture_handoff 1`, `staging_patience 5` | live |

NOT tried yet:
1. A death or grave memory that bans the group, or the tiles, where our own champion just died (until an ally count is reached).
2. A respawn rule: a respawned champion goes to the nearest living ally before taking a solo target (the crater Ryth walk).
3. A post-contact regroup (GF 5.6) as an explicit state with a time limit and the health ordering.
4. A numeric 2+ lead gate for approach (GF 5.3) based on counts, not the simulation.
5. An ally-proximity term in the travel step.
6. Drafting Cassi and Issac: `draft_pref` ranks it ninth (`config.h`), `draft_pref3` and `draft_pref4` are unset (all -1). Fish drafted it in 10 of 10 games.
7. Contest-gated cohesion (issue 1 of `results/winner-intangibles-2026-11/issues.md`) is proposed but not built; this study overlaps with that one and with its integer outnumber check (issue 2).

## 6. Answers

**(a) Is "not aggressive enough when we hold a mismatch" supported by our data?** Not as stated. In the 10 Fish games our champions step toward the nearest enemy in 28% of favourable champion-rounds and 24% of unfavourable ones; Fish does 27% and 27%. We are not less bold than Fish in the same state. What differs is the state: Fish is favourable 9.5 times per unfavourable and we 2.6 times. This is a coarse measure (one step, nearest enemy, one opponent, a definition of favourable I chose). It does not measure missed kills, and the 56 study's own results do not show it either. Closing-in margin changes (0.5, 1.0) lost. My reading (inferred): mismatches in our favour are rarer for us because of position, not because we hold back when they arise. A test of the other view needs a decode that counts how often a champion with a kill in reach did not attack; I did not do it.

**(b) Does the enemy prioritise annihilating a stray champion, and can we exploit or defend?** Observed in crater: Fish's pack followed our Vendetta from (39,28) at r44 to (41,38) at r54 and our Heart stayed to die, while our recalled Ryth walked back toward the pack alone (r56-74). Fish also recalls its own wounded champions (Vendetta at 22% health, r53). Whether this is a rule to chase strays or just a pack that stays together while we trickle in cannot be separated from one game. Bait and kite is a hypothesis: it needs a champion that can outrun or out-range a pack and an ally to punish the chasers; no source above reports a working bait for units that cannot move faster than the chaser (our own comment: a chase at equal speed never ends, `brain.cpp:710`). Defend first: stay within the support range of the nearest ally (mechanisms 1 and 4), and treat the respawned unit separately.

**(c) Coordination or information?** Both, and the data cannot separate them cleanly. Information: three of the five crater champions were 8-10 tiles from the fight; our vision radius was not measured here, so whether they saw it is unknown (hypothesis). The `phantom_mode` and `share_sightings` tests were mirror-only and lost 25% and 41%, which says little for or against. Coordination: the oasis opening shows Fish moving its four champions inside 3-5 tiles from round 10 while ours were spread over 15 columns, and our own `sos_radius` is off. The most direct cheap probe is a replay count of how many of our champions were within 10 tiles and in each other's vision when the first fight began, per game, and whether they joined within 5 rounds. Not done.

## Caveats

- 10 games, one opponent (rank 1 on 2 Nov), a stronger and different opponent from the four in #56.
- Positions are end-of-round; "near" uses a fixed Chebyshev radius.
- The MIT sources are for different games and the effect sizes are the authors' claims.
- The decoded JSON files (about 440 MB) were deleted from the scratchpad when the disk filled; re-decoding takes about 4 minutes with the command in section 3.
