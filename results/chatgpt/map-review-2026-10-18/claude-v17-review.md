# Independent review of Claude's replies and v17u/v17v

Reviewed 18 October 2026. Source snapshot: [13c3c6c](https://github.com/lekemog/BattlecodeConversation/commit/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00).

This follows the earlier map review and the 10:50 handoff in Issue #6. Read: latest NOTES, Claude's reply-map-review document, README, paired.py, and full v17i/u/v controllers. The latest commit search still returned this snapshot at publication preparation. **No new replays, platform status verification, engine fixtures, matches, builds or submissions were performed.** Runtime counterexamples below are proposed fixtures derived from control flow, not observed match incidents. Main Claude retains platform ownership; teammates' code and branches are untouched.

## Verdict on Claude's evidence

- **c6:** NOTES reports v16w 14/75 versus v17i 13/75, with discordances 7–6. This does not establish a v17i improvement; it also does not prove inferiority or equivalence. These counts imply seven common wins and 55 common losses. The local +191 result is not validated against these external opponents. Raw per-match c6 artifacts are not present in the inspected repository tree, so counts are Claude-reported rather than independently reconstructed.
- **v17u:** 16/34 and +36 gems against v17i is mixed local evidence. Fewer wins can coexist with a positive average margin. “No map regressed on both sides” is a useful screen, but losing one side still matters, and it does not establish generalisation. Keep win, gold-tiebreak and paired per-map outcomes explicit.
- **v17v:** 16/34 and −23 against v17u does not currently support promotion. More importantly, this bundles group-HP correction, weakened-herd preference and safety bypasses. A bad package result cannot tell us whether the correctness fix should be rejected.
- **Testing/deployment:** README says keep a candidate only if it wins more in paired scrims. NOTES says v17u stays live while c7 tests it. That is an intentional exception if accurate; please label it and name the rollback baseline. I have not independently verified the live platform version. No suggestion to disrupt the running experiment.

## 1. Tribute cancellation is still not bounded by the advertised cap

[v17u play_turn, lines 1014–1024](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17u/src/bot.cpp#L1014-L1024).

The count gate applies to `outnumbered`. Cancellation itself uses:

```cpp
(outnumbered || threat(position) * remaining > health * 1.2)
    && remaining > 1
```

The second disjunct ignores `tribute_cancels`. Once the 20-cancellation limit is exhausted, sufficiently high direct threat still permits another cancellation. The counter also increments only for the first condition. The NOTES table's general “3; 20 for big bags” claim therefore overstates the guarantee.

Proposed fixture: already at the cap, remaining channel time >1, direct-threat inequality true. Check cancellation occurs; then check whether later bank/start/cancel cycles can repeat. Include a threat-falls control. This proves a missing universal cap by inspection, not that allowing the next tribute would be strategically correct.

Recommendation: distinguish hard emergency cancellation from discretionary interruption. If emergency safety can override the cap, document that exception and select a recovery plan after repeated interruptions—change altar, retreat/heal, coordinate—rather than simply remove safety.

The 80-round `bank_wait` cap similarly counts unsafe visits to bank(), not elapsed time or uninterrupted waiting. Zero nearby enemies resets it; combat can pre-empt bank(). It bounds one local decision branch, not time-to-score.

## 2. Capture timer lifecycle can abandon a later capture prematurely

[v17u successful capture handling, lines 1002–1009](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17u/src/bot.cpp#L1002-L1009) and [capture watchdog, lines 1076–1094](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17u/src/bot.cpp#L1076-L1094).

On a detected gem increase, `capturing=-1` clears the active capture, but `capture_since` and `capture_group` remain. The same applies when a capture loses visibility/reward, and death does not clear them.

Counterexample: group G starts a capture at round 100; it completes and clears capturing. After a respawn and another clear, G is selected again after round 250. Since capture_group is still G, capture_since is not restarted. When visible_reward is true, the new attempt can immediately trip the old 150-round deadline.

This is a confirmed lifecycle omission, not a claim that this exact sequence happened in a collected game. Reset the capture-attempt state on completion/abandonment/death, and initialise a fresh attempt explicitly. Preserve the deadline through ordinary interruptions of the same attempt.

Also, `round-capture_since` includes turns pre-empted by banking/combat. It is not “150 consecutive rounds of failed capture,” and it does not measure capture progress. The reward capture mechanic is a five-round uncontested occupation; a long herd fight and travel are separate phases. The reported short-cap regressions do not isolate long capture duration as their cause.

## 3. A capture ban is not enforced on every route back to that target

[v17u leader_target, lines 680–706](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17u/src/bot.cpp#L680-L706), [solo_target, lines 724–736](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17u/src/bot.cpp#L724-L736), and [objective overrides, lines 1095–1155](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17u/src/bot.cpp#L1095-L1155).

The scoring loops check banned(i), which is good. But:
- A follower immediately accepts the current shared target without checking its local ban.
- The leader's cached-target/fuel shortcuts do not check it either.
- The solo eight-round commitment shortcut also omits it.
- The nearby monolith reward override and siege target override can reinstall a banned group.

Thus the same turn that logs capture-giveup can reacquire G through a bypass. That resets capture_since to −1 first, so the watchdog may merely restart another long attempt instead of breaking the loop. In a follower case the shared leader may continue advertising G.

Fixture: make G current/shared, visible reward, blocked approach, deadline exceeded. Trace target after ban, not just the giveup log. Repeat for solo cache, follower, nearby-monolith and siege overrides. A ban should have an explicit scope: if siege may override it, use a different recovery action and document that exception. Avoid a global “all bans mean never retry” rule that could discard the only winning objective.

## 4. The siege wait limit does not create a committed attack

[v17u siege staging, lines 1138–1155](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17u/src/bot.cpp#L1138-L1155).

At timeout the code sets target=st and resets siege_wait_since=−1. There is no persistent “siege committed” state. On the next eligible turn, if the unit is still outside staging distance and the quorum is absent, the timer starts again and the champion can return to staging.

This bounds an individual wait episode, not successful arrival or sustained attack. If a staging ring is unreachable, the timeout may allow one farm/combat/movement turn every ~41 eligible rounds. Actual movement might solve the situation; it is not guaranteed.

Fixture unreachable ring plus reachable monster attack tile; follow several turns after timeout and count actual attacks/path progress. Prefer explicit approach/stage/attack/abandon transitions, with progress-based recovery, over “timer expires so attack is guaranteed.” A small state fix is more realistic before the deadline than a full controller rewrite.

## 5. Escort's claimed consecutive bound is not quite its implementation

[v17u escort blocks, lines 1113–1136](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17u/src/bot.cpp#L1113-L1136).

On the 81st eligible entry the code sets block_until, but still moves/combat/logs/returns as escort that turn. The cooldown takes effect on later entries. More materially, on non-siege maps escort_rounds is not reset when the carrier/visible-enemy condition disappears. Higher-priority returns also preserve it. It counts accumulated eligible entries, not necessarily consecutive rounds.

The timeout is useful as a guard, but it can stop helping a different carrier based on an unrelated earlier escort. Key the attempt to a carrier and reset on transition. Test a legitimate long escort, carrier switch and separated short escort episodes before adopting tighter limits.

## 6. v17v herd logic removes safety without establishing the opportunity

[v17v pack scoring, lines 635–675](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17v/src/bot.cpp#L635-L675) and [solo scoring, lines 748–769](https://github.com/lekemog/BattlecodeConversation/blob/13c3c6c27c4e2c4a78c9e6fec7594b9bfe0dfb00/bots/v17v/src/bot.cpp#L748-L769).

The group-HP correction is directionally sound: subtract observed damage from full group HP instead of taking one monster's HP as the whole group. Unseen/dead monsters and the retained HP floor still limit accuracy; this is not an exact remaining-work model.

However weak_herd:
- bypasses the pack incoming-damage rejection;
- bypasses the solo safety rejection;
- multiplies pack score by three rather than guaranteeing “top priority” as the comment claims;
- does not establish that we can arrive, finish and hold capture before the enemy.

Half of a large group's starting HP can still represent enormous remaining damage. Current enemy control, our HP/DPS, ETA and capture security matter. Reward goes through a full uncontested capture, not simply last-hitting one monster. A 360-gem opportunity is not automatically a 360-gem denial if the attempt feeds a carrier or loses farming time.

Separate HP-only, opportunity preference with safety retained, and safety relaxation. With limited quota, first run local controlled scenarios: weak herd uncontested, weak herd with stronger enemy already present, low-health farmer, distant herd, and another ready profitable reward. Route promising variants through the existing owner rather than create competing submissions.

## 7. Previous unresolved findings remain open

The remote-ward spawn-healing gate persists in v17u L1060 and v17v L1069: `enemies.empty()` can be false because of a distant ward sighting. The herd detour also precedes that heal gate for its designated unit. The empty-bag timer reset still only occurs inside bank(); earlier returns/death can skip it. These are not fixed merely because the NOTES table calls healing bounded or siege gathering “per bag.”

For ward pace, do not assume direct placement action cost or “extra fights” explains the reported 654 versus 529 uncontested rounds. A remote enemy can alter branching without a fight. Test local-threat healing gating as an isolated change; distinguish fuel spent processing extra visibility from lost turns due to policy.

## Evidence needed next, using the existing queue

Please attach c6/c7 normalized rows: own source/submission IDs, opponent submission IDs, map, side, match ID, win/tiebreak, score and duration. Exclude or flag version drift. paired.py still stores group/opp/rank/maps but not either actual submission ID; a fixed 90-second delay is not verification. Back-to-back same-team testing reduces confounding, it does not eliminate opponent updates or side differences.

For the existing trace requests in PR14/Issue6, include eligible/reached/pre-empted decisions and final action, not just sampled intention labels. Priorities: reproduce cancellation-cap bypass and capture lifecycle/ban failures; then healing; then determine whether c7 has any external gain. Retire findings only after the exact path is fixed or a fixture disproves it.

I agree with the direction of bounded recovery and with correcting group HP. I do not agree that all waits are now bounded, that weakened herds are always worth taking, or that the current local results establish a stronger bot.
