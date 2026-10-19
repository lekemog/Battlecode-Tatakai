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
