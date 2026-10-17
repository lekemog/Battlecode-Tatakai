# Discord mechanics audit and Polaris experiment backlog

Research session: 17–18 October 2026, Europe/London. Prepared for main Claude, Szymon's agent and Leke.

## Scope and evidence standard

Read approximately 400 distinct rendered messages across portions of #devs and #strategy; opened 29 distinct current-game question/bug threads; checked current FAQ, announcements, developer updates and open-source; searched the server for camp, capture, respawn, tribute, altar and bush discussions. Searches and chronological reads overlap. This is a substantial targeted review, **not an exhaustive Discord export**. Long channel histories, attachments, unvisited threads and messages posted after this review remain gaps. Discord search results labelled “Message could not be loaded” were treated as leads, not full thread verification.

No messages were sent to Discord. Leke explicitly clarified GitHub is the publication destination. No other servers or DMs were researched. Only relevant findings are paraphrased here; unrelated chat is not copied.

**O** = explicit organiser/developer answer observed; **P** = participant claim or measurement; **H** = our inference or experiment. O means source confidence, not that we independently reproduced the engine or established strategic superiority. Answers date from 13–17 October and may be superseded. Pin CLI, SDK and engine versions when testing. A promise to fix something is not evidence it is fixed.

This report does not identify the currently live bot or assert these behaviors are missing from the latest candidate. README/NOTES version labels lag later discussions. Audit the actual candidate commit before changing it. No bot files, platform matches or submissions were changed.

## Highest-value conclusions

1. **Unseen maps are the tournament target.** Passing the public 17-map suite is necessary regression evidence, not proof of generalisation.
2. **Fuel spent initialising memory can erase strategic gains.** Measure byte clearing/copying and observations in the actual Wasm release build.
3. **Camp safety needs per-monster geometry and timing.** Group wake-up, individual sleep, nearest-target selection and turn-order ties are different rules.
4. **Resource conversion remains a stronger immediate hypothesis than elaborate intent prediction.** Spawn healing and shopping overlap can make return trips useful; no camp sleep healing makes safe staged clearing plausible.
5. **Read the end of bug threads.** Several apparently serious engine defects were unconfirmed or resolved as API misuse.

## Camp clearing, capture and cycle planning

| ID | Observed evidence | Potential Polaris adaptation and limit |
|---|---|---|
| C1 | **O:** monsters attack the nearest champion in range; ties use who acts earlier within that round. [S1], #devs 17 Oct 14:00–14:02. | **H:** estimate damage per monster and champion position. Compare controlled durable-first positioning with independent farmers. A nearby tank is not persistent aggro: movement and deaths can change targets. |
| C2 | **O:** members of one camp group wake together but sleep on their two-turn aggression cooldown individually. [S1] | **H:** avoid one group-wide awake flag for damage prediction. Track or query individual state; do not assume every monster stopped attacking when one slept. |
| C3 | **O:** sleep follows two rounds without an in-range champion; an awake monster need not be hit again to keep attacking. #devs, Chris, 16 Oct 17:05–17:06. | **H:** a retreat must leave the relevant ranges. Merely stopping attacks is not disengagement. Check routes through other awakened monsters. |
| C4 | **O:** sleeping monsters do not heal. [S2] | **H:** staged clearing after a heal/shop return may preserve progress. Compare whole-cycle time and contest risk; this is not proof it beats completing the group immediately. |
| C5 | **O:** cardinally adjacent monsters form a camp group; attacking a member wakes the group; rewards require all members dead. “Camp” can mean one monster. [S3] | **H:** use combined remaining group workload for clear-time estimates. Taking one gem cluster beside a live monolith does not produce an independently collectible reward. |
| C6 | **O:** an occupied monster spawn tile can prevent respawn; the red hand indicates a blocked spawn attempt. [S4] | **H:** move an idle farmer off the spawn tile after collection. Test our own accidental blocking before considering deliberate denial. Parking for denial costs an active champion and may be worse than farming. |
| C7 | **O, search excerpt:** group respawn time is the maximum over its members; a monolith can determine the whole group's next cycle. #questions “Are camp group rewards only available on the maximum respawn length?”, Chris, 15 Oct 18:52. | **H:** score repeat routes with group timers, not a wolf or gem cluster's shorter individual timer. Confirm timer semantics in the actual engine. |
| C8 | **O, search excerpt:** one champion can capture an entire cleared group. #general, Chris, 16 Oct 08:11. | **H:** additional capturers need a reason: faster progress, safety or useful resource splitting. They are not required merely because the group contains multiple monsters. |

**Important model distinction:** group total HP is relevant to total clearing work; it does not mean every monster can hit every champion every round. Fixing the former with an excessively pessimistic damage estimate can still wrongly reject solo camps.

## Banking, shopping, vision and combat

| ID | Observed evidence | Potential Polaris adaptation and limit |
|---|---|---|
| B1 | **O:** spawn/recall placement uses the next free slot in Team A's bottom-to-top, left-to-right ordering, reflected for Team B. #devs, Chris, 17 Oct 14:02. | **H:** improve return-route timing; do not assume spawn-centre placement. Future occupancy is uncertain. Lower priority than eliminating long stalls. |
| B2 | **O:** standing on an own spawn tile heals to full in a single turn; it is not unique to arriving by recall. #strategy, Chris, 16 Oct 23:26–23:27. | **H:** compare walking onto a nearby spawn tile against recalling. Verify the exact turn boundary; do not treat arrival as immediate invulnerability. Burst before the next healing boundary can still kill. |
| B3 | **O:** shopping is permitted while standing on the spawn tile during the healing wait. #devs, Chris, 16 Oct 13:00. | **H:** shop during necessary healing downtime instead of adding an unnecessary extra wait. Preserve bank-before-shop decisions when needed; avoid unconditional recall with vulnerable gem bags. |
| B4 | **O:** tribute attempts against an enemy lock become attacks on the lock; the usual tribute wait is still needed after breaking it. #devs, Chris, 16 Oct 12:40. | **H:** altar cost includes breaking the lock and subsequent tribute delay. A valid tribute call is not evidence gems were deposited. Compare alternate altars including travel and interception risk. |
| V1 | **O:** a ward can stay behind after the owner moves farther away. [S5] | **H:** keep vision on a useful altar or interception corridor rather than relocating automatically with every step. |
| V2 | **O:** a ward persists after death and its owner can see through it while dead. [S6] | **H:** do not drop useful observations solely because the ward owner died. Determine which controlled instance actually has that vision; do not assume pooled team vision. Dead-instance computation is also mentioned by Chris in #devs, 16 Oct 16:34, but measure fuel and process behavior before designing around it. |
| A1 | **O:** attack-reset spells permit a second basic attack in one turn. [S7] | **H:** legal attack → reset → attack sequences can improve farming and fights. Recheck target existence/range after each state-changing action. Audit current code before duplicating existing logic. |
| A2 | **O:** normal ranged movement conflicts with a basic attack and with abilities marked ranged; dash is not normal movement for this restriction. Normal move plus dash is allowed. [S8] | **H:** evaluate legal action sequences rather than an assumption of one action per turn. Test dash→attack and attack→dash using the actual ability; permission is not an instruction to dash into danger. |
| A3 | **O:** the dash implementation was described as instant traversal of a short route, allowing two diagonal steps around a wall via a hole; it was explicitly not traversal through that wall. #strategy, Chris, 17 Oct 14:52–14:53. | **H:** use engine legal tiles instead of a straight-line-only approximation. The text is not enough to reconstruct all dash geometry. |
| A4 | **O:** Ryth's area stun affects enemies/camps, with no harmful friendly effects; Chris confirmed the no-friendly-harm answer for other champion abilities too. [S9] | **H:** do not reject useful offensive AoE solely because an ally is in the area. Preserve intended ally-target healing/shields; this answer is not “abilities never affect allies.” |
| A5 | **O:** Ren's retaliation can trigger when hit from an unseen bush attacker. [S10] | **H:** include that passive in combat estimates even without attacker vision. It does not reveal hidden enemy coordinates or authorise targeted attacks on an unseen entity. |
| E1 | **O:** gold/items are per champion, including separate resources for Cassi and Issac; there is no simple item-count cap; most emblem effects do not stack, except Power and Bruiser. [S11] | **H:** audit duo shopping, redundant purchases and effective stats. Test item-specific stacking; do not extrapolate this short answer into unverified shard formulas. |
| E2 | **O:** Vesper's gold passive applies to all gold sources, including champion-kill gold. #devs, Chris, 16 Oct 16:56. | **H:** an economic simulation should include kill income. This alone does not justify changing the draft or pursuing kills instead of scoring. |

## Fuel, APIs and execution correctness

| ID | Observed evidence | Audit or test |
|---|---|---|
| F1 | **O:** uninitialised allocation should cost O(1) fuel; initialisation costs O(n). [S12] | Profile full-array clears, fills and copies before blaming pathfinding alone. Distinguish capacity allocation from writing every byte. |
| F2 | **O:** memory.fill is charged approximately one fuel per byte; a participant's 10,000-byte clear measured 10,009 fuel. Assertions for copy/init were participant measurements. [S13] | Candidate experiments: touched-cell clearing, generation stamps, narrower element types, persistent static-map caches. These have their own overhead and wraparound/invalidation risks. Compare measured total turn fuel, not asymptotic slogans. |
| F3 | **O:** bitboard operations were described as having a custom cost of one fuel per 8×8 chunk. #devs, awu, 14 Oct 16:34. | Native bitboards are a promising benchmark arm, not automatically free or faster. Repeated allocations/wrappers, map shape and the exact operator matter. Verify current SDK costs. |
| F4 | **O:** the “zz” replay icon means fuel exhaustion, including when a champion appears to be capturing. [S14], [S15] | Separate intentional waiting from forced suspension. Log decisions actually completed and observation age, not only attempted actions or crashes. |
| F5 | **O:** a debug-block/fuel-pause discrepancy between release and debug was acknowledged; a fix was promised. [S16] | Test the exact release Wasm submitted. A debug run is not equivalent evidence. Record SDK/runtime versions; do not claim the promised fix shipped without checking. |
| F6 | **P:** one training discussion describes acting roughly every 2.2 rounds on stale observations and proposes latency-aware training. #devs, MarvinTMB, 16 Oct 21:43. | The useful warning is train/runtime mismatch, not the quoted latency or formula as an engine guarantee. Fix excessive computation first; simulate measured deployment dynamics if training remains worthwhile. |
| I1 | **O:** full distance fields use distance_field::compute; compute_to is a different, target-oriented operation. [S17] | One reusable field can replace repeated target path queries when semantics match. Occupancy and path origin invalidate caches; static geometry and live blockers need separate handling. |
| I2 | **O:** an unreached distance is uint16 maximum, i.e. 65535. [S18] | Test sentinel handling before adding distances, narrowing integers or taking minima. Exclude unreached jobs explicitly; do not let arithmetic wrap them into attractive targets. |
| I3 | **O:** static camp information is available, but querying runtime position() caused vision/init errors; spawn_position() was the intended static coordinate. [S19] | Cache static metadata after valid initialisation and query dynamic state only legally. The thread's initial “engine bug” hypothesis did not survive the later replies. |
| I4 | **O:** write draft memory before picking; picking can hand the turn to the other team and make a following write invalid. A fix was promised and the workaround was confirmed by the reporter. #devs, awu, 16 Oct 17:21–17:23. | Audit ordering on all picks including the last. Do not assume data written after a successful pick persisted. |
| I5 | **O:** the developer recommended champions(team::ally) for ally enumeration and said the website's “visible” description needed correction. [S20] | Distinguish enumeration from which fields are legal to read. Do not assume every method on an enumerated ally/enemy is universally visible. |
| I6 | **O:** champion_name() required vision in a reported error-97 case; a developer suggested finding self by handle equality in the ally list instead. [S21] | Use stable identity rather than alphabetically sorting names for shared-memory slots. Verify ordering guarantees before making list position a persistent identity. |
| I7 | **O:** reading visible enemy turn priorities was initially called unintended, then explicitly retained after discussion. #devs, Chris, 16 Oct 15:41 and 16:11. | A legitimate official-API micro input, subject to current rules/API verification. Use it to reason about acted/unacted enemies and camp tie breaks; do not equate priority bits with opponent intent. |

## Evaluation, unseen maps and misleading evidence

- **O:** all tournaments use unseen maps. [S22] Organisers allow unusual layouts while aiming for a healthy quantity resembling the ladder's normal maps. [S23] Neither promises a fixed number of altars or familiar connectivity.
- **O:** champion count is independent of map dimensions: a 5v5 on 30×30 and 3v3 on 100×100 are possible (#devs, Chris, 16 Oct 18:39). “Between 3 and 5” in another thread was only a player's recollection; do not promote it to a guaranteed maximum. Draft picks and controlled entity count are not identical when Cassi/Issac are present.
- **O:** replay step mode shows actual action order; smooth playback merges actions visually (#strategy, Chris, 16 Oct 23:31). Apparent instantaneous kills are not proof of one action or one champion doing all the damage.
- **P:** players discuss challenging historical versions while a newer bot is current (#strategy, 17 Oct 15:06–15:47). This is a warning to record both version IDs, not proof that a specific opponent manipulated an experiment.
- **O:** early match endings might be forfeits, but the developer asked for links; no universal cause was established. [S24] Audit terminal reasons rather than treating every short game as a strategy outcome.
- **O:** the reported 1-based/0-based coordinate discrepancy was not reproduced; the developer proposed a stale-position explanation. [S25] Do not add an offset “fix” without reproducing it.
- **O:** the reported Respawning/RewardAvailable confusion was also not reproduced. [S26] Do not work around a title instead of checking the actual engine result.
- **P:** “bank immediately, hold gold” and claims of a guaranteed trick were unsupported strategy opinions. They are not recommendations.
- **O:** only bug fixes/hotfixes were planned during a sprint; balance changes were planned between sprint tournaments (#devs, Chris, 15 Oct 04:29–04:31). Historical April patch posts concern the other game and must not drive this season's champion decisions.
- **O:** the current FAQ permits AI assistance. The open-source channel includes an April Rational Merlin repository: https://github.com/nzjt/cambattlecode26 . This is a newly discovered reference, **not code reviewed in this audit** and not a current-rules strategy source.

## Proposed isolated experiments, ordered by expected usefulness

| Experiment | Mechanism | Meaningful acceptance evidence / rejection |
|---|---|---|
| T1: memory/fuel audit | Instrument clearing, copying, observation and path calls in release Wasm; measure actual execution cadence. | Lower p95/maximum fuel and fewer forced suspensions without changed behavior. Reject changes that just move work or introduce stale state. |
| T2: unseen-layout regression | Exercise map-derived logic on legal new layouts with changed altar count, chokepoints, camp composition, team size and both sides. | No crashes/stalls and robust outcomes against a frozen parent. Keep held-out layouts for final confirmation rather than tuning every result. |
| T3: camp-damage calibration | Micro-scenarios with two champions, swapped order, varied distances, mixed monster ranges and disengagement. | Predicted target/HP/time agree with engine; then evaluate farm throughput and wins. Never label capture-completion occupancy as proof of a truly solo clear. |
| T4: respawn hygiene | Compare waiting directly on a cleared spawn with moving to adjacent legal staging tiles. | Actual spawn/capture timings improve; no loss from moving away before claiming. Test group behavior and partial occupancy explicitly. |
| T5: heal/shop cycle | Measure walk-to-spawn versus recall, shop during heal wait, and resumed clearing of damaged sleeping groups. | Shorter useful conversion cycles and better wins, not simply earlier first purchase. Include gem theft risk and the previously observed medium-bag stall. |
| T6: correct movement/action sequences | Check full distance-field reuse, unreachable sentinel, dash/move/ranged restrictions and attack resets. | Identical legality, fewer errors/stalls, measured fuel and combat/farm improvement. Revalidate after movement and suspension. |
| T7: persistent useful wards | Preserve an informative ward through movement/death; consume sightings in concrete routing or threat decisions. | More useful warning/changed safe decisions and better outcomes at tolerable fuel, not raw placement count. |

For every candidate: freeze parent/candidate source hashes and engine versions; isolate the change in a new bots/ folder; compare same maps/sides and version-audited opponents; lead with actual wins and correct tiebreak outcomes; inspect regressions. These experiments have **not** been run in this audit. No ladder submission is authorised for ChatGPT.

## Sources

Exact thread URLs below were observed in the browser. Discord sign-in/server access may be required. Channel-only claims above include the speaker, date and displayed time for retrieval.

| Ref | Thread |
|---|---|
| S1 | [Camp Aggression Details](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560531044334182501) |
| S2 | [camp sleep behaviour](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560165658325557278) |
| S3 | [Camp group rewards](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1561086641324687501) |
| S4 | [Red hand / blocked respawn](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1561089683914629221) |
| S5 | [Wards](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1559968539857784853) |
| S6 | [Ward behaviour on death](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560625562119307334) |
| S7 | [Attack resets](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560334969656705104) |
| S8 | [Actions per turn](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1559968667289129081) |
| S9 | [Ryth Area Stun](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560302350164435034) |
| S10 | [Ren retaliation](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1559507172566503454) |
| S11 | [Item and gold](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1559966889206218803) |
| S12 | [Memory allocation/initialisation](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1559959589091287182) |
| S13 | [WASM bulk-memory fuel](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560413261038362734) |
| S14 | [Snoozing](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560619207408750683) |
| S15 | [Replay fuel instrumentation](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1559666644341624922) |
| S16 | [Fuel pause / debug mismatch](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560718446642200739) |
| S17 | [Distance Field](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1561081274255540386) |
| S18 | [Unreached distance](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1561053353616609373) |
| S19 | [Writing camps to draft memory](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560690795340632126) |
| S20 | [Ally attributes](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1561085058591359099) |
| S21 | [Error 97 / identity](https://discord.com/channels/1479274986203123883/1549138740772085821/threads/1560723660870778891) |
| S22 | [New maps](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560404407387037826) |
| S23 | [Unseen Maps](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560345348587655320) |
| S24 | [Early unranked endings](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1561068494072848454) |
| S25 | [Unconfirmed coordinate report](https://discord.com/channels/1479274986203123883/1549138740772085821/threads/1560932135215566908) |
| S26 | [Unconfirmed reward-state report](https://discord.com/channels/1479274986203123883/1549138740772085821/threads/1559737824448741557) |
| Channels | [devs](https://discord.com/channels/1479274986203123883/1480336541984362538), [strategy](https://discord.com/channels/1479274986203123883/1482062553990566080), [current FAQ](https://discord.com/channels/1479274986203123883/1554181673397133342), [announcements](https://discord.com/channels/1479274986203123883/1479275336738013236), [open-source](https://discord.com/channels/1479274986203123883/1484383505839427715) |

## Remaining gaps

No private DMs, hidden channels, complete message attachment export or exhaustive forum crawl. Some older threads were screened by title rather than opened. Search excerpts C7/C8 should receive full-thread follow-up before implementation. The actual current candidate needs a function-by-function audit to see which checks are already satisfied. No claim here establishes an optimal draft, optimal item build or tournament rank.
