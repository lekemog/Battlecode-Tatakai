# Native-event recall audit — 21 October 2026

Question from Claude in #37: does Fish recall for low HP, shopping, or bag size?

**Answer:** these five games show both low-health resets and high-health shopping resets, often carrying gems. The compact cache's recall counts are not reliable enough to infer frequency or a threshold. The native trace has **289 recall starts, 264 completions, 20 manual cancellations and 5 damage interruptions**. This does not establish a universal policy.

## Coverage and boundaries

Re-downloaded the same five Fish/procless ranked games in series `42c0ad6a-6ea5-4ea8-8dda-180339c5711b`. This is deeper event-level coverage, **zero additional independent games**. Fish is side B. All five decode under official engine **1.0.1** from cambc 3.0.3, and their replay SHA-256s match the original study. No replay-content duplicates; each recall is keyed by actual game round, native input position and champion ID. The decoded final duplicate state is not counted as another action.

Fish/opponent submission IDs are not exposed by the downloaded replay bundle and remain unknown for this series; do not pool it into a submission-specific causal estimate. The wider cache now has 300 distinct match-ID records (250 marked win, 50 loss), but no replay hashes, engine IDs or submission IDs. Distinct IDs alone do not prove independent deterministic trajectories. We used its five matching records to audit instrumentation, not to claim 300 newly reviewed games.

## Native counts versus cache

| Map | Match ID | Starts | Completed | Manual cancels | Damage interrupts | Median HP at start | Cache Fish recalls |
|---|---|---:|---:|---:|---:|---:|---:|
| collision | 793352d2-2946-44a1-b89b-225a5879311d | 57 | 56 | 1 | 0 | 55.9% | 0 |
| fracture | 3a6c4ece-f962-4241-9369-234a5939d6a1 | 57 | 56 | 1 | 0 | 27.1% | 0 |
| fragment | 7a568552-0496-47aa-a018-67af3b520a35 | 65 | 55 | 8 | 2 | 47.1% | 0 |
| split | d148b5ea-d71d-4480-bff4-0fba938d6429 | 54 | 53 | 1 | 0 | 46.7% | 0 |
| concentrated_wealth | 8f0bc4a5-9eb5-426d-a180-fffe6083ad04 | 56 | 44 | 9 | 3 | 33.7% | 0 |

The native counts are independently checked by channel transitions: Recall action kind 11 changes channel 0→1; completion changes 1→0 at timer zero with Move kind 4; manual cancellation is kind 16; interruptions here occur at Attack/Cast kinds 5/6. We retain both start and terminal state. These are successful starts, not failed API requests. Completions retain carried gems. No open channels remain at the end of these five games.

`fishstudy.py` infers a recall from a >=4-tile position jump ending within four tiles of a supposed spawn centre. That centre is estimated from champions' positions at array index 25, after they have already moved. This can miss real recalls; dashes near the estimate can also satisfy it. Do not replace the published 5.6/game with 52.8/game as a population estimate: **52.8 is only this selected five-game series**. Recompute the wider cohort from channel/actions.

## Concrete traces, actual action rounds

| Game / champion | Recall starts → completes | HP at start | Gold / bag at start | Initial channel | Observation two game rounds after completion |
|---|---|---:|---:|---:|---|
| collision / Stellar | 39 → 44 | 730/750 | 220 / 8 | 5 | gold 10, full HP; +Treasure Focus emblem, +2 Power Focus shards |
| collision / Stellar | 739 → 742 | 1446/1500 | 286 / 72 | 3 | gold 16, full HP; +2 Power Focus emblems, −1 shard |
| split / HoR | 65 → 70 | 830/1000 | 350 / 27 | 5 | gold 20; +Power Focus, +Treasure Focus, +Home Health shard |
| split / Stellar | 203 → 208 | 750/750 | 290 / 12 | 5 | gold 20; +Treasure Focus, +4 Power Focus shards |
| split / HoR | 725 → 728 | 1874/2000 | 194 / 0 | 3 | gold 14; +Power Focus emblem and shard; HP remains 1874 |
| fragment / HoR | 278 → 283 | 900/1000 | 210 / 4 | 5 | gold 0; Treasure Focus upgrade and +4 Power Focus shards |
| fragment / HoR | 1067 → 1070 | 1856/2000 | 192 / 0 | 3 | gold 12; +2 Power Focus emblems, −4 shards; HP remains 1856 |

Item deltas reflect inventory upgrades, not separate inferred purchase actions. Later HP staying below full warns against assuming every completed recall includes a full healing wait.

For completed recalls, straight-line Chebyshev distance from start to the observed spawn landing ranges from 2 to 58 tiles (median 21.5). Split alone: 6–30, median 19. These are geometric distances, not legal route lengths. The cache's split spawn estimate from array index 25 is (31.17, 9.17), already at actual r20; the observed r70 recall lands at (34,1), 8.17 tiles from that estimate, failing its <=4 filter.

Across 289 starts, **45 occur at >=80% HP; every one of those has >=172 unspent gold**. **141 starts carry gems** (including the 72-gem example). **94 starts have a three-turn timer**, consistent with Home. All are descriptions of this series, not a proven gold threshold. A low-HP-only model is contradicted by the full-HP shopping examples; a bag-zero prerequisite is contradicted by recall retention. Hidden route/target selection and non-recall opportunity states still need comparison.

## Item correction

I previously called item ID 35 Jungle Focus in FIELD_STUDY and #36/#37. **That was my labelling error.** The official 3.0.3 visualiser `B` name table maps:
- 21 → Treasure Emblem of Focus
- 27 → Jungle Emblem of Focus
- 35 → Home Emblem of Health

The split r800 HoR inventory includes **Home Health**, not Jungle Focus. The 988 focus and 11 Power Focus emblems remain correct. This correction strengthens the reset/shopping interpretation but does not prove its contribution to win rate.

## Experiment and next question

Keep the dash scoring experiment separate. Claude's subsequent #37 update says v23g's vision-exception fix was not adopted alone after a mixed bench, and v23k/d/f/e are queued on v22w. Keep the compared baseline frozen and treat the exception fix as its own factor; do not mix its behavioural effects into a recall experiment.

MOBA reset-tempo principle, translated into a measurable proposal: a recall can exchange channel + return travel time for an immediate item spike and/or healing. Score the next useful task's completion time under **walk, recall-shop-return, and bank-first-recall**, including bag retention, safe channel completion, recovery wait and purchase benefit. Near a winning bank, use the team finish-time estimate before taking optional shopping. The split r725 empty-bag HoR recall does not by itself prove it caused the later loss.

First measurement: log recall starts/completions/cancels, HP/gold/bag, purchase deltas, rounds until the next camp clear/bank, and gems lost before that task. Compare observed recalls with same-champion non-recall states to test candidate HP and spend thresholds. Do not hardcode 172 from a minimum in a selected sample. Main Claude owns any paired strength tests; none were run here.

Next replay question: HoR shield/dash sequencing on both sides of a recall/item spike, using the native action timeline; separate camp damage from champion damage and the escape cost.

## Engine 1.0.2 reply

Official [21 October patch notes](https://2026a.battlecode.co.uk/game/patch-notes/e251fa42-fb2a-4d9b-ab8c-2e044f21d599) explicitly list more than Prism/API changes: Stellar HP 750→650, HP/shard 75→65, focus 85→70, focus/shard 9→7; HoR strength 40→30, strength/shard 4→3.5, dash modifier 1.75→1.5; Ren S1 modifier 1.25→0.75; Vesper HP 900→1000 and strength 50→55; Vendetta HP 800→1000; Tavi HP 750→900 and focus 100→110; Prism focus/gem 1→1.5. These explain why a header-only diff can miss substantial benchmark changes. This run does not establish the engine now serving the ladder; all replay evidence above is 1.0.1.

## Reproduction

Use `recall_extract.mjs` with the official 3.0.3 visualiser assets, matching the original extractor's CLI. Then:
```sh
python recall_audit.py 'replays/*/recall_decoded.json' recall_evidence.json
```
`recall_evidence.json` includes every start/exit pair and replay hashes. Assertions verify unique native event keys, unique replay content and the engine cohort. No live bot/source, ranked submission, scrim, merge or deployment changed. Coordination: #37; related #36 and draft PR #38.


### Remaining question from the 04:20 UTC coordination note

The same faulty jump-to-estimated-spawn detector also underlies the reported zero recalls for our team. That zero is not sufficient evidence that our bot never completes recalls; validate both teams with native channels. The five-game audit does **not yet answer whether Fish deliberately steps out of camp range before recall**. That requires matching its same-turn movement to awake-camp ranges and targeting at each start. Nearby camps alone do not prove damage attribution. The low-HP recall candidate remains testable, but Fish's high-HP shopping branch is separate.
