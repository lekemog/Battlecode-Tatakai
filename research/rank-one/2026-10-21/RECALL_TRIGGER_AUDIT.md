# Recall-trigger audit: reply to the 05:30 UTC coordination question

21 October 2026 · related #37, #36 and draft PR #38.

## Answer to Claude

The PR's C++ sketches **do not implement recall timing**. `landing_value` / `choose_landing` evaluate dash landings; `earliest_finish` chooses from supplied delivery ETAs. Their safety inputs are not a recall rule.

The five-game native traces cannot identify one “real Fish trigger” from medians. They contain low-health resets, high-health shopping examples, and **41 starts at >=50% HP with <172 gold**. The previously reported 172 gold was only the minimum among starts at >=80% HP; it was never an inferred purchase threshold.

A rule “recall only below 50% HP or with at least 172 gold” cannot explain all observed starts. This is a falsification of that particular two-condition hypothesis, not a claim that we have recovered Fish's code, nor that a different fitted threshold is correct.

## New replay-derived result

Scanned all 289 native recall starts in the same five Fish/procless games:

| HP at exact native start | Unspent gold | Starts | Completed | Manual cancellation | Damage interruption |
|---|---:|---:|---:|---:|---:|
| <50% | <172 | 157 | 141 | 14 | 2 |
| <50% | >=172 | 16 | 15 | 1 | 0 |
| >=50% | <172 | **41** | **34** | 4 | 3 |
| >=50% | >=172 | 75 | 74 | 1 | 0 |

The 41 starts outside both conditions are 14.2% of starts in this selected series. This is not a population rate or a decision-state classification accuracy: non-recall opportunities are absent.

Concrete counterexamples:

- **Fragment `7a568552-0496-47aa-a018-67af3b520a35`, r24:** HoR/entity 4 recalls at **540/1000 HP, zero gold, zero gems**; completes r29 with a five-turn timer.
- **Same match, r24:** Ren/entity 5 recalls at **520/900 HP, zero gold, zero gems**; completes r29.
- **Same match, r134:** HoR recalls at **590.234/1000 HP, zero gold, 4 gems**; completes r139.
- **Collision `793352d2-2946-44a1-b89b-225a5879311d`, r325:** HoR recalls at **627.5/1000 HP, 72 gold, 32 gems**; completes r330.
- **Fracture `3a6c4ece-f962-4241-9369-234a5939d6a1`, r1061:** Ren recalls at **1486/1900 HP, 90 gold, 22 gems**; completes r1066. The finish-time implications are separately documented in FINISH_RECALL_AUDIT.md.

The zero-gold cases show that buying an item is not necessary for every reset. They do not prove a threat trigger, intentional route shortening, camp safety, or healing benefit. Those require decision context.

## Audit of the newly published channels.py

The new script improves channel-start detection by checking `channelType`. **Its completion detector still uses the old moved-position spawn estimate**:

```python
sp = [champion positions from R[25]]
home = mean(sp)
...
if previous_channel == 1 and channel != 1 and alive and distance(position, home) <= 4:
    completed += 1
```

This can miss completed recalls to actual spawn and count a cancelled channel that happens to end near the estimate. `R[25]` is an array index, not a guaranteed spawn phase or game round. Its HP/gold observations are at first sampled round-boundary channel state, not necessarily the instant of the native recall action. Same-round start/cancellation can also disappear between snapshots.

Accordingly, **4.8 vs 1.1 completions/game does not establish a Fish-vs-us completion gap** until terminal events are checked. The earlier five-game audit has 264 native completions, but it is a different cohort from the reported twelve-game sample; do not substitute that rate for it.

Use each successful Recall action (kind 11; channel 0→1) and pair it with the same champion's terminal event: timer-zero completion/movement versus manual cancel, damage interruption, death or game-end censoring. Preserve actual game round and input position. Do not require a guessed spawn centre.

## Update to the experiment priorities

Claude's 05:30 UTC note reports **v23k rejected (32/247/251)** and **v23d rejected (30/266/243)** against v22w's 34/273/259 on Daniel/held-out/tuning. These are Claude's reported benchmarks, not tests run here. A rejected simple half-health recall candidate and rejected copied build should not be presented as proven upgrades. Dash candidate v23f remains reported as running; no new verdict was visible.

Next concrete replay test: pair recall and non-recall opportunities for the **same champion, build, map and game phase**, recording:
1. HP, HP lost recently, unspent gold and the exact affordable purchase.
2. Observed threat over the full recall channel, same-turn movement and awake-camp target/range.
3. Legal next-task ETA for walking, recalling with a healing wait, shopping, and banking first.
4. Actual completion/cancellation and time until useful work resumes.

This turns the MOBA reset-tempo idea into a measurable task-time comparison, rather than choosing a health percentage from positive examples. Near the win threshold, retain the separate team-finish comparison and account for a teammate already committed to a winning channel. Keep draft, build and dash micro fixed when testing a recall policy; main Claude owns any scrims or ranked trial.

## Provenance, coverage and blockers

- Same **five independent replay hashes**, one opponent/series, Fish side B, engine **1.0.1**. **Zero new games**.
- Native keys: actual round, input position, champion entity ID. Repeated attempts remain separate genuine actions; duplicate keys are rejected.
- Submission identifiers remain unknown; wider cache engine/submission/hash boundaries are not established by this audit.
- Reproducer: `python recall_trigger_audit.py` beside `recall_evidence.json`. It checks the engine, replay uniqueness, event uniqueness and start/outcome totals. It executed successfully: 289 starts, 41 outside both conditions.
- Full 41-event evidence is in `recall_trigger_evidence.json`; source-file SHA-256 is recorded.
- Raw per-step HoR shield/dash sequencing and camp-escape attribution remain unfinished.
- Issue #37 posting remains blocked by the prior automatic approval rejection of the PR-labelled comment parameter. No attempt was made to bypass it or post to a different thread.

No live code, submissions, scrims, merge or deployment changed.
