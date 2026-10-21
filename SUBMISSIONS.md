# Submission log

Every ladder submission with a one-line comment. New submissions go through `tools/submit.py BOT "comment"`, which also writes the comment as a header in the bot's `src/main.cpp`, so it shows in the platform's source view. Versions 89–110 below were backfilled from the run logs.

| Version | Bot | Time (UTC) | Comment |
|---|---|---|---|
| 89 | v16o | 2026-10-18 ~02:30 | Contest fix: on gold-only maps solo farmers stay on our half; lone champions don't fight away from home. |
| 90 | v16s | ~04:55 | Cassi & Issac in the 3-pick draft. Rejected (3/36 on those maps). |
| 91 | v16o | ~06:19 | Revert to v16o. |
| 92 | v16t | ~06:22 | Engage enemies poking us from just outside range. |
| 93–95 | v16u, v16t, v16o | ~07:24–07:40 | Paired test c4 arms. v16t/v16u 6 wins each, v16o 3. |
| 96–97 | v16u, v16v | ~08:00–08:30 | Paired test c5 arms. v16v (top-100 item build) won 10 vs 6. |
| 98 | v16w | ~08:35 | Contest monolith siege. |
| 99 | v16x | ~08:48 | Test arm for an aborted c6 run; never meant to stay live. |
| 100–102 | v16w | ~09:10–09:30 | Resubmissions of v16w around the aborted run. |
| 103 | v17i | ~09:35 | Paired c6 arm: wards, contested-altar escort, review fixes. Tied v16w (13 vs 14). |
| 104–106 | v17u | ~10:10–10:30 | Bounded waits. Paired c7 arm (re-queued twice). |
| 107 | v17w | ~10:35 | Contest vulture + later siege + siege abort. Paired c7 arm. |
| 108 | v17x | ~10:40 | Single-camp solo farming. Paired c7 arm; rejected. |
| 109 | v17w | ~10:46 | Made live after c7 (v17u = v17w at 10 wins, v17x 8). |
| 110 | v18c | ~10:55 | Paired c8 arm: two solo gem farmers on single-camp maps. |
| 111 | v18c | 2026-10-18T10:59Z | v17w + two sturdy non-carries solo the single 22/36-gem camps on single-camp maps (corners pace). |
| 112 | v18c | 2026-10-18T11:00Z | v17w + two sturdy non-carries solo the single 22/36-gem camps on single-camp maps (corners pace). |
| 113 | v18c | 2026-10-18T11:28Z | v17w + two sturdy non-carries solo the single 22/36-gem camps on single-camp maps (corners pace). |
| 114 | v18f | 2026-10-18T11:30Z | v17w + RAID: vs passive farmers who lead us on big maps, take their-side camps and hunt carriers (bolder fights without a bag); off after 3 deaths. |
| 115 | v17w | 2026-10-18T11:37Z | v17u + contest: vulture monoliths under 50% HP, siege only from r600, abandon a siege after 150 rounds. |
| 116 | v18f | 2026-10-18T11:44Z | v17w + RAID: vs passive farmers who lead us on big maps, take their-side camps and hunt carriers (bolder fights without a bag); off after 3 deaths. |
| 117 | v18k | 2026-10-18T11:44Z | v18f (raid) + top-team winners draft for 4+ picks (Ryth over Tavi) + health items for frontliners. |
| 118 | v18m | 2026-10-18T12:13Z | v18f + monolith bag convoy: 100+ gem carrier goes home, rallies the team to spawn, walks to the altar with 2+ allies (60-round cap). |
| 119 | v18t | 2026-10-18T12:32Z | DIAGNOSTIC: behaviour identical to v18f; logs every decision (action, target, hp, gems, enemies, allies, posture, fight ratio) for weak-map analysis. |
| 120 | v18x | 2026-10-18T13:42Z | Weak-map fixes #16-#18: central altars no longer avoided on stale sightings; opponent model no longer turtles on middle-contest; small banks + working contested-altar logic on collision; monolith bag convoy. |
| 121 | v18t | 2026-10-18T13:45Z | DIAGNOSTIC: behaviour identical to v18f; logs every decision (action, target, hp, gems, enemies, allies, posture, fight ratio) for weak-map analysis. |
| 122 | v19b | 2026-10-18T13:52Z | v19a + #20: fight threshold calibrated on 1629 top-100 engagements (need 1.3, 0.9 next to spawn; was 0.6). |
| 123 | v19b | 2026-10-18T13:53Z | v19a + #20: fight threshold calibrated on 1629 top-100 engagements (need 1.3, 0.9 next to spawn; was 0.6). |
| 124 | v19c | 2026-10-18T14:57Z | v19b + strike-first rule from top-10 fights: engage from power ratio 0.85 when we can hit first (not hit by a champion for 4 rounds). |
| 125 | v19b | 2026-10-18T15:00Z | v19a + #20: fight threshold calibrated on 1629 top-100 engagements (need 1.3, 0.9 next to spawn; was 0.6). |
| 126 | v18x | 2026-10-18T15:05Z | Revert from v19b/v19c: on identical top-100 weak-map games v18x won 6, v19b 3, v19c 1 (the fight recalibration made us evade 17% of the time vs 10% and lost stampede races). |
| 127 | v19a | 2026-10-18T15:36Z | v18z + #20: fight power = strength + 0.5*focus for both sides (casters were valued by strength only). |
| 128 | v18x | 2026-10-18T15:47Z | Revert from v19b/v19c: on identical top-100 weak-map games v18x won 6, v19b 3, v19c 1 (the fight recalibration made us evade 17% of the time vs 10% and lost stampede races). |
| 129 | v19f | 2026-10-18T15:59Z | v18x + earlier first items: shop-recall at 110 gold before round 250 (was 180). |
| 130 | v18x | 2026-10-18T16:02Z | Revert from v19b/v19c: on identical top-100 weak-map games v18x won 6, v19b 3, v19c 1 (the fight recalibration made us evade 17% of the time vs 10% and lost stampede races). |
| 131 | v19f | 2026-10-18T16:18Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 132 | v19g | 2026-10-18T16:18Z | v19f + focus-inclusive fight valuation (v19a, thresholds unchanged): v19a alone 7 vs v18x 6 on the t1 games. |
| 133 | v19f | 2026-10-18T16:47Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 134 | v19f | 2026-10-18T16:59Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 135 | v18x | 2026-10-18T17:01Z | Revert from v19b/v19c: on identical top-100 weak-map games v18x won 6, v19b 3, v19c 1 (the fight recalibration made us evade 17% of the time vs 10% and lost stampede races). |
| 136 | v19f | 2026-10-18T17:04Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 137 | v19i | 2026-10-18T17:13Z | v19f + lifecycle resets + focus-inclusive fight valuation ONLY on single-central-altar brawl maps (eight): v19g won 2 eight games but lost corners/collision. |
| 138 | v19f | 2026-10-18T17:48Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 139 | v19j | 2026-10-18T18:01Z | v19f + contest: solo farmers may use the middle third (winners spend 71% of the opening there; Kurians #22). |
| 140 | v19m | 2026-10-18T19:14Z | v19f + review #15 rec 1 (carrier does not pursue; pursuit falls through if it neither moved nor hit) + lifecycle resets (rec 5: death ends a capture). |
| 141 | v19f | 2026-10-18T19:18Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 142 | v19j | 2026-10-18T19:33Z | v19f + contest: solo farmers may use the middle third (winners spend 71% of the opening there; Kurians #22). |
| 143 | v19f | 2026-10-18T19:36Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 144 | v19n | 2026-10-18T19:48Z | v19f + focus-inclusive fight valuation ONLY on single-central-altar contested maps; everywhere else byte-identical v19f maths (tests whether v19g/v19i lost corners/collision because of the v18z resets). |
| 145 | v19f | 2026-10-18T19:55Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 146 | v19n | 2026-10-18T20:15Z | v19f + focus-inclusive fight valuation ONLY on single-central-altar contested maps; everywhere else byte-identical v19f maths (tests whether v19g/v19i lost corners/collision because of the v18z resets). |
| 147 | v19f | 2026-10-18T20:18Z | Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5). |
| 148 | v19n | 2026-10-18T20:19Z | FINAL: v19f + focus-inclusive fight valuation only on single-central-altar contested maps (eight). Identical weak-map games 12/75 vs v19f 10; strong-map games 4/35 = v19f 4. |
| 149 | v20a | 2026-10-19T02:28Z | #25 test: v19n + corners solo farming (big-map rule from 70) + packs two squads. Local corners margin +180 vs +121; packs equal; other 15 maps byte-identical to v19n (control for the scrim A/B). |
| 150 | v19n | 2026-10-19T03:00Z | Revert from v20a: corners solo farmed 27 22-gem camps/game but gems@400 fell to 356 (v19n 423) and deaths rose to 4.7 vs the opponents' 0.7 (3 scrims). The packs squad split was a no-op (packs drafts 3 champions). |
| 151 | v20d | 2026-10-19T03:03Z | #25 packs: 3-champion pack drops the elk x1.5 clear penalty on the central 48s (small 6-altar map only). Local packs 13/16 (+158) vs v19n 8/14 (+10). All other maps byte-identical to v19n. |
| 152 | v20e | 2026-10-19T03:19Z | #25: v20d (packs elk fix) + corners: squad 3 of 3 sweeps single camps only. Map-gated changes, so packs and corners are read separately in the scrims; other 15 maps = v19n. Local corners 12/16 (+106) vs v19n 11/14 (+121): neutral. |
| 153 | v20h | 2026-10-19T03:31Z | #25: v20e (corners sweep pair) + packs 2+1 squads (replaces v20d elk fix). Local packs behaviour: 8/8 wins, 48s 5.5/game (v19n 3.0), 44s kept 12.8, first tribute r48, gems@400 706 (v19n 692). |
| 154 | v20i | 2026-10-19T04:10Z | #25 role fixes: corners sweep pair never merges (local: 22s 0.4->9.6/game, 36s and 96s kept); packs pair on centre 48s + solo on home 44s (local centre time 8%->15%, 48s ~3->6.2; first tribute r63, slower). Scrim behaviour test. |
| 155 | v20j | 2026-10-19T05:03Z | #25: corners-only change kept (v20i scrims: gems@400 484 vs v19n 450, deaths 3.4 vs 3.8, our 22s 6.0, their 22s 15.4 vs 19.7). Packs reverted to v19n: v20i packs first tribute r62 vs r39, deaths 2.8 vs 1.4, gems@400 513 vs 582. |
| 156 | v19n | 2026-10-19T06:35Z | Revert from v20j: corners sweep failed acceptance on 18 scrims (gems@400 431 vs v19n 450, deaths 4.0 vs 3.8, opponents' 22s unchanged at 19.5). No proven map fix; v19n baseline until a change passes scrim behaviour checks. |
| 157 | v20k | 2026-10-19T07:56Z | #26: frontliners build Bruiser-Health then Durability-Health before Power (carries unchanged). Local focus maps (32 games vs fz_hunt/tank/herd, v18x): wins 22/32 vs v19n 20/32; max HP@300 +17-30% on every map; deaths down on contest/eight/monolith. |
| 158 | v20l | 2026-10-19T09:46Z | #26 follow-up: frontliners Bruiser-Health replaces Jungle as first emblem, then v19n order. v20k (B,D,P,P) failed scrims: our deaths -30% but enemy deaths fell more, wins 4/60 vs v19n 8/60, gems@400 down on eight/elkring. v20l local focus maps 23/32 (v19n 20, v20k 22). |
| 159 | v19n | 2026-10-19T11:33Z | Revert from v20l (#26): health-first builds close the HP gap (v20l within 4-14%) but cost farming: gold@300 and gems@400 fall on eight/monolith/elkring, enemy deaths fall on eight/monolith, focus-map scrim wins 2/40 (v20k 4/60, v19n 8/60). Jungle emblem's farming speed matters more than HP. |
| 160 | v20m | 2026-10-19T11:39Z | #25 contest: disengage below 60% HP when outnumbered nearby (enemies within range+3 > allies within 5), escaping toward a safer ally. Map-gated (gold-only monolith map). Local contest 9/12 vs v19n 8/12, deaths 13.4 vs 14.8. |
| 161 | v20n | 2026-10-19T12:47Z | #27 contest disengage (from v20m) + #28 eight: carrier within 5 of the altar and not outnumbered finishes the deposit instead of retreating/evading. Map-gated separately. Local eight 6/12 vs v19n 3/12, deaths 8.4 vs 12.0, gems@400 439 vs 422. |
| 162 | v20o | 2026-10-19T14:51Z | #30: Ryth replaces Tavi in the draft (opponents' core, Ryth in 50/60 of their games). Built on v19n; v20n's contest and eight changes both failed scrim acceptance and are dropped. Local all-map bench 67/102 vs v19n 66/102. |
| 163 | v20p | 2026-10-19T15:51Z | Contest gold race: farm the four central 105-gold groups (either side of centre), skip far 35-gold edge singles. Vs teams at our rank, ranked contest is 3/27; they hold 38% of champion-time at the central groups vs our 13% and reach ~3x our gold by r600. Local: central time 18%->61%, opponent gold @600 1663->1298, wins 10/12 vs 8/12. v20o (Ryth draft) paused so contest is measured cleanly on v19n. |
| 164 | v19n | 2026-10-19T16:32Z | Stop experimenting on the live bot: ranked 13:00-16:30 UTC 28/65 (43%), rank 267. Back to plain v19n (~51% over 230 games); all further tests local-only until a change is clearly better. |
| 165 | v20p | 2026-10-19T19:21Z | Bounded ranked trial (#32 bench): v19n + contest central-gold farming only. Copycat bench: gold@600 gap 1.43x (v19n) -> 1.04x (v20p). Stop rule: overall <45% after 30 games or contest worse -> v19n. |
| 166 | v20q | 2026-10-19T21:08Z | Bounded trial: v20p (contest central gold) + eight: carriers below 85% HP recall to heal before the altar (#32 fight study: we engage altar fights at 74-76% HP vs their 83-84%; lose 916 vs 731 HP per fight). Local eight 6/8 vs v19n 1/8, deaths 9.2 vs 15.1. Map-gated; guard: overall <45% after 30 games -> v19n. |
| 167 | v19n | 2026-10-19T23:17Z | Revert v20q trial: contest+eight 0/11 since 19:20 (eight heal change and contest gold change did not convert). Back to plain v19n. |
| 168 | v21a | 2026-10-20T00:00Z | Bounded trial (#33): in enemy range with no ready dash -> fight back instead of walking away. External-bot bench 124/170 vs v19n 118/170, margin +1654 vs +1359. Stop rule: <45% after 30 ranked games -> v19n. |
| 169 | v21h | 2026-10-20T03:00Z | v21a + walled-camp farming fix (new pool bench 310/420 vs v21a 273) |
| 170 | v21m | 2026-10-20T04:33Z | v21h + whole-cycle camp cost + C&I in 3-pick drafts (new-pool bench 337/420 vs v21h 310; v21h ranked 25-15). Stop rule <45% after 30 -> v21h |
| 171 | v21p | 2026-10-20T06:26Z | v21m + out-of-reach camp fix (expanse Varg stuck on a chest 2 tiles away). Bench 343/420 vs v21m 337; ranked v21m expanse 0/4. Stop rule <45% after 30 -> v21m |
| 172 | v22f | 2026-10-20T12:45Z | Patch 3.0: v21p + gold weight 1.0 (post-patch ranked losses: gold@600 1767 vs 2702; games now go ~1700 rounds, gold decides fights and the tiebreak). 3.0 bench 307/420 vs v21p 299, both sets up. Stop rule <45% after 30 -> v21p |
| 173 | v22p | 2026-10-20T23:26Z | v22f + elite post-patch draft (Ryth, C&I, Stellar, Varg, Ren, Tavi for 4+ picks). 35-map bench: held-out 258 vs 251, tuning 250 vs 249, Daniel v8 30/70 = v22f. Guard <45% after 30 -> v22f |
| 174 | v22w | 2026-10-21T01:07Z | v22p + Ryth health-tank build (elite contest replay: Ryth 10,600 HP soaks monolith). 35-map bench: Daniel v8 34/70 (v22p 30), held-out 273/350 (258), tuning 259/350 (250). Guard <45% after 30 -> v22p |
| 175 | v23m | 2026-10-21T08:25Z | Engine 1.0.2 re-baseline: v22w + bank at 25-60 gems (Fish banks 34x/game, bag 22). On 1.0.2 vs Daniel v8 + DE41H v4 (140 games, 35 maps): 57 vs v22w 51. Guard <45% after 30 -> v22w |
| 176 | v23r | 2026-10-21T09:01Z | Engine 1.0.2: v23m + post-Stellar-nerf draft (5-6 picks Ryth, Varg, Vesper, Vendetta, Ren, C&I; 3 picks Varg, Vesper, Ryth). Screen vs Daniel v8 + DE41H v4 (140 games, 35 maps): 80 vs v23m 57 vs v22w 51, margins positive. Guard <40% after 30 -> v23m |
| 177 | v23v | 2026-10-21T11:26Z | v23r + two stall fixes from ranked losses (0/9 on starvation/shortcut/gold_rush/fracture): uncapped retry when the pack finds no reachable group (starvation: idled at spawn r153-2000); fight blocker / switch altar when the bank path fails (shortcut). Engine 1.0.2: screen 80/140 margin +234 (v23r 80, +177); held-out 283/350 (v23r 278). Guard <40% after 30 -> v23r |
| 178 | v24c | 2026-10-21T13:08Z | v23v + no banking while every altar submit tile is within 2 of a live monolith (boss battle: carriers stood by the monolith-ringed altar all game, 0 banked; now the pack kills the monoliths and banks). Boss battle vs DE41H/Mohnish/Apex: 0-0 x3 -> wins 1147-920, 1008-8, 1612-0. Screen 81/140 +263 (v23v 80 +234); held-out 285/350 (v23v 283). Guard <40% after 30 -> v23v |
| 179 | v24i | 2026-10-21T15:13Z | v24c + per-map farming mode: solo (bolder) on yellow_brick_road, ambush, rushbait_v2, fracture, elk_arena by map fingerprint (7-opp bench: solo lost clearly fewer there); leave contested captures of >=20-camp groups after 12 rounds. 7-opp bench 378/490 (v24c 366): screen 84/140, held-out 294/350 (v24c 81, 285); yellow brick losses 11->4, fracture 8->5, ambush 5->2. Guard <40% after 30 -> v24c |
| 180 | v24k | 2026-10-21T15:24Z | v24i + pack farming forced on contest (fingerprint 50x50, 2 altars, 14 groups, 34 camps). Contest vs 7 bench opponents: 12/14 (v24i 8/14; always-pack diag 12/14). All other maps unchanged. Guard <40% after 30 -> v24i |
| 181 | v24n | 2026-10-21T16:21Z | v24k + per-map smaller banks (rows, pilgrimage, gold_rush, split) and bolder pack (shortcut, starvation), from 13-map 7-opponent benches. Full 7-opp bench 387/490 margin +3012 (v24i 378 +2713; v24k ~382). Guard <40% after 30 -> v24k |
| 182 | v24p | 2026-10-21T17:10Z | v24n + per-map draft: Vesper/Willow-led order on quadrants, reverse_spiral, fracture, contest (map read during draft). Full 7-opp bench 396/490 margin +3137 (v24n 387 +3012); only those 4 maps changed: quadrants 7->4, reverse_spiral 5->3, fracture 5->3, contest 2->0 losses. Guard <40% after 30 -> v24n |
| 183 | v24u | 2026-10-21T17:37Z | v24p + per-map draft: Varg-first/Willow 5-pick on rows and rushbait_v2 (losses vs 7 bench opponents 5->1 and 6->4 of 14; only those maps change). Projected 7-opp bench 402/490 (v24p 396). New maps gem_fields/gemfight fingerprinted, no rule collisions. Guard <40% after 30 -> v24p |
