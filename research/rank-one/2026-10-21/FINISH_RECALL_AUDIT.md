# Finish-time audit: recalls with a sufficient winning bag

21 October 2026 · follow-up to [RECALL_AUDIT.md](RECALL_AUDIT.md), #36 / #37 / draft PR #38.

## Question and result

Does Fish ever start a recall while its own carried bag, added to already banked gems, would cross the 1000-gem winning threshold?

**Yes: two native recall starts in the existing five-game series. Both occur in games Fish wins.** This is a concrete team-finish scheduling test case, not proof that recalling was wrong or that an earlier legal delivery existed. The observation challenges an assumption that Fish always stops resetting once an individually sufficient winning bag exists.

| Map / match | Native recall | Champion / entity | HP | Unspent gold | Bag | Conservative banked score | Banked + bag | Fish victory boundary |
|---|---|---|---:|---:|---:|---:|---:|---|
| fracture / `3a6c4ece-f962-4241-9369-234a5939d6a1` | r1061 → r1066 | Ren / 7 | 1486/1900 (78.2%) | 90 | 22 | 981 (observed r1041) | 1003 | r1067, 1011–830 |
| collision / `793352d2-2946-44a1-b89b-225a5879311d` | r1342 → r1345 | Stellar / 3 | 1392/1500 (92.8%) | 400 | 66 | 983 (observed r1330) | 1049 | r1370, 1016–760 |

Neither recalling carrier has a later bank recorded before the game ends. In fracture, HoR/entity 6 supplies the final observed 30-gem bank at r1067. In collision, HoR/entity 4 supplies the final observed 22-gem bank at r1370; other banking occurred between Stellar's recall and the final bank. The game ending before a carrier's bank is right-censoring, not evidence that it would never deliver.

Both recalls complete and retain the whole bag. High HP alone does not establish safety: enemy threats, path legality, altar access and ability states must still be examined. Ren's 90 gold also warns against labelling every high-HP recall as shopping.

## Coverage, joins and provenance

- Same five ranked Fish/procless games; **zero new independent games**. Scanned all **289 native recall starts** from the committed recall audit; two qualify.
- Fish side B / engine **1.0.1** for every record. Replay hashes agree between the native recall evidence and original series evidence; no duplicate replay hashes.
- Native event keys are `(actual game round, input position, champion ID)`. No array offsets enter this join.
- Score changes are inferred round-boundary observations. The query uses only a banked-score observation with round **strictly earlier** than the recall action's round. Score monotonicity is checked. This gives a conservative lower bound and avoids uncertain same-round action ordering.
- “Later bank” uses champion entity ID, not champion type, and remains an inferred round-boundary event. It does not provide sub-round execution times.
- The Fish and opponent submission IDs remain unknown. Do not generalise these five engine-1.0.1 games to other submissions or engine 1.0.2.
- This audit does not measure the fraction of all near-winning opportunities that trigger recall. It samples **recall starts**, not all decision states.
- The broader Fish cache has not been independently decoded or deduplicated by this run. Its aggregate recall counts remain subject to the detector problem documented in RECALL_AUDIT.

## Original measurable experiment

Apply the objective-clock principle as an explicit scheduling comparison: when visible team bags can finish, estimate the earliest **jointly feasible** winning bank under (a) direct delivery, (b) recall then delivery, and (c) a teammate delivering while this champion resets or protects the route.

A blanket “never recall with a winning bag” rule is not justified. If a teammate is already completing a winning channel, the reset may be irrelevant; if the direct route is lethal, recall can preserve value. Choose among feasible plans and preserve current channel commitments.

Before changing policy, reconstruct these two states and log:
1. Terrain-aware arrival, altar lock/queue and full tribute-channel completion time.
2. Carrier survival/interrupt exposure, dash/shield readiness, and the alternative carrier's committed arrival.
3. Prediction versus actual winning-bank time, plus carried gems lost and unnecessary travel.

Then, if the timing model is calibrated, freeze draft/build/micro and test only the finish scheduler on paired maps/opponents. Keep the Ren dash-scoring/build experiment separate. No claim of a win-rate improvement or deployment readiness follows from this audit.

## What remains unresolved

HoR shield/dash ordering, camp-escape before recall, and legal direct-delivery ETAs require the raw per-action trace and terrain. Those temporary decoded files were not present in this run; the saved evidence supports this narrower query without pretending to answer those questions. No new full-history coverage was added.

Claude's newest available #37 note remains the 04:20 UTC update about v23k/d/f/e on v22w; no newer bench verdict was visible when checked. His zero-recall comparison still requires native-channel validation for both teams.

Posting the progress comment to #37 remains blocked by the prior automatic approval rejection: the available connector requires a `pr_number` and describes PR conversation comments, while the approved destination is issue #37. No workaround or alternate-thread message was sent. The findings are saved here on the authorised research branch.

## Reproduce

Run beside the committed `recall_evidence.json` and `series_evidence.json`:

```sh
python finish_recall_audit.py
```

`finish_recall_evidence.json` contains both complete native recall records, score bounds, replay/source hashes and observed later banks. Assertions check engine/hash consistency, unique native keys and monotonic score. The script was executed successfully: 5 games / 289 starts / 2 qualifying events.

No live bot edits, submissions, scrims, merge or deployment.
