# Mite beats Intercontinental Fish 3–2: five-game case study

Study date: 17 October 2026, about 20:10 UK/Irish time. This is the most recent **series victory** by Mite found with the exact head-to-head ranked/victory filters. The series was about seven hours old when inspected; it is not a claim about either team's current submission.

Source: [series 04d6a985-df7d-4ef3-934f-6867aaa6f308](https://2026a.battlecode.co.uk/game/match-groups/04d6a985-df7d-4ef3-934f-6867aaa6f308). Five authenticated Summary → Download JSON files were analysed. [Extracted evidence](mite-fish-evidence-2026-10-17.json) includes match IDs, source SHA-256 checksums, team/champion metrics, fixed-round snapshots, purchase/tribute events and selected collection/death events.

## Result

All scores are Mite first. Both teams are strong, but this is one series and two historical bot versions, not a causal benchmark.

| Map | Rounds | Score | Winner | Mite/Fish gold | Mite/Fish deaths |
|---|---:|---:|---|---:|---:|
| expanse | 601 | 862–1008 | Fish | 3680 / 4870 | 0 / 0 |
| stampede | 460 | 1008–0 | Mite | 3960 / 3668 | 0 / 3 |
| rows | 361 | 1012–990 | Mite | 4320 / 4590 | 0 / 0 |
| contest | 2000 | 0–0 | Mite | 17036 / 2496 | 4 / 59 |
| rushbait_v2 | 538 | 776–1008 | Fish | 3970 / 4300 | 2 / 0 |

The latest two other ranked head-to-head series visible in history were Fish 3–2 wins. Mite's win here is real, but it should not be represented as the latest head-to-head result overall.

## 1. Stampede: choose the score-bearing objective, not the greatest number of camps

Individual match: `8c39b253-1a32-4e49-a299-1d3fd50ea398`.

Mite clears **17 camp groups**, Fish **41**. Yet Mite collects **1080 gems**, Fish **zero**; final banked score is **1008–0**, with Mite's Ryth still carrying 72. Neither side loses any carried gems. This is not Fish losing a bag after farming it: the summary records no positive gem collection for Fish at all.

The decisive event sequence is explicit:

| Capture round | Group | Recipients | Gems per recipient | Total |
|---:|---:|---|---:|---:|
| 130 | 10 | Prism, Stellar, Cassi, Ryth, Tavi | 72 | 360 |
| 282 | 10 | Same five | 72 | 360 |
| 418 | 10 | Prism, Stellar, Issac, Ryth, Tavi | 72 | 360 |

Mite's first five bank events occur at rounds **168, 170, 172, 173, 174**, 72 gems each: 360 total. Another five follow at **319, 321, 322, 324, 326**, reaching 720. It wins during the next banking wave at round 460. The collection coordinates put the recipients together at the same objective; that is direct evidence of grouped collection. It does not reveal Mite's code or prove a particular pack-formation algorithm.

Fish clears many zero-gem groups. By round 100 it has earned **700 gold vs Mite's 140**, but by round 200 it has banked **0 vs 360**, despite near-equal lifetime gold **1470 vs 1430**. Raw early gold and camp count are poor substitutes for progress to the victory condition here.

Drafts: Mite uses Prism, Stellar, Cassi & Issac, Ryth, Tavi; Fish uses Stellar, Tavi, Prism, Cassi & Issac, Ren. Mite opens Jungle on the six runtime champions by round 135. Fish mixes Power/Bruiser/Treasure. Multiple differences coexist; this is **not** proof that Jungle or Ryth caused the win.

### Transfer to our bot

Inspect the current target selector on maps with concentrated gem supply. Compare expected **banked gems per full clear/capture/return/tribute cycle**, with gold as an investment in future cycles. The relevant distinction is between a camp that advances the score objective and one that merely produces activity.

Current `bots/v12c/src/bot.cpp` has a concrete issue worth checking separately: `siege_group` is assigned for maps with no non-monolith gem sources; `solo_target()` skips uncleared monoliths, and a turn-loop comment says never to fight one down, only collect already-cleared rewards. `choose_group()` can consider monoliths but includes safety limits. **The summaries do not identify group 10's camp type**, so do not equate this finding with a proven monolith bug on stampede. Inspect the actual map metadata first.

Smallest test: log candidate group identity, gem yield, clear/capture/bank cost, chosen target and rejection reason on stampede. If the productive group is being rejected or undervalued, create one target-selection candidate, with draft/items unchanged. Measure positive gem collection, completed score cycles, round to 360/720/1000 banked, deaths and fuel; compare both sides and several real opponents before adoption.

## 2. Rows: a tiny finishing tribute can beat a larger economy

Individual match: `8fa203b5-2403-4869-8f7f-50ded297c094`.

Both teams have **zero deaths**, zero champion damage done and zero gem losses. Fish clears **17** groups to Mite's **16** and earns **4590** gold to Mite's **4320**. At round 200 they are tied on both collected gems (**528 each**) and submitted gems (**462 each**). Mite nevertheless wins **1012–990**.

The finish:
- Mite reaches **990 submitted** at round 349.
- At round **350**, a 66-gem reward from group 0 is split among Varg, Issac and Ren: **22 each**.
- At round **361**, Ren submits those **22**, ending the game.
- Fish finishes with **132 carried**: 66 on Ren and 66 on Issac. Mite finishes with 44 carried.

This is a demonstrated **score-delivery race**, not a combat win or total-resource win. It is not proof that the split was deliberate endgame logic; accidental positioning could produce the same event pattern.

Fish opens Monster while Mite opens Jungle, but Fish purchases earlier (round **32 vs 44**) and finishes ahead in gold. “Earlier purchase always wins” and “more gold always wins” are both contradicted by this game.

### Transfer to our bot

Our current reward logic splits large rewards at `g.gems>=150` but generally assigns smaller rewards to a claimant. A finish-aware exception may be valuable when a smaller split still lets a nearby champion complete the victory threshold sooner. Before changing it, confirm current shared-score visibility, capture splitting and tribute timing in the official API.

Smallest test: when close to the win threshold, compare the completion time of existing bags, one full reward to a claimant, and a split reward to champions with faster safe altar access. Keep normal farming unchanged elsewhere. Test the boundary conditions as well as actual matched games. Preserve score completion and safe routing above a fixed bag-size rule. Do not hard-code 22 or round 350.

## 3. Contest: Mite wins the tiebreak through a large economic/combat advantage

Individual match: `dc1e8caa-6d05-4659-a03c-480944121696`.

The score is **0–0 after 2000 rounds**. Neither side records positive gem collection or tribute. Given the documented tiebreak order and the summary, the decisive advantage is **lifetime earned gold, 17036 vs 2496**. Mite clears 116 groups to Fish's 56. It has four runtime-entity deaths to Fish's 59, and 47 credited kills to Fish's four. Do not equate death counts with independent fights: the twins can produce paired death events without equal credited-kill counts.

The lead develops early and keeps widening:

| Round | Mite/Fish earned gold | Mite/Fish deaths |
|---:|---:|---:|
| 100 | 520 / 260 | 1 / 3 |
| 200 | 1165 / 435 | 1 / 5 |
| 400 | 2431 / 751 | 2 / 12 |
| 1000 | 7359 / 1530 | 4 / 23 |
| 1500 | 12105 / 2034 | 4 / 40 |
| 1999 | 17036 / 2496 | 4 / 59 |

Mite drafts Prism, Stellar, Cassi & Issac, Ryth, Tavi. Fish drafts Stellar, Tavi, Prism, Cassi & Issac, Ren. Mite completes Treasure on Stellar at 41 and Tavi at 65, with Treasure on Issac and Cassi later; Fish's first completed emblem is Power Focus on Prism at 65. This is an interesting **map-specific** investment pattern, not grounds to reverse our own rejected global Treasure-first trial.

By round 125 Mite has credited kills at rounds **21, 48, 111 and 125**, while Fish has one at 52. The first lead is not merely a late-game passive-gold phenomenon. Exactly which positioning, spell order or protection caused those outcomes remains unestablished by summary data.

Mite places 1536 wards and buys eight altar locks, Fish 37 wards and no locks. Neither side banks gems, so the locks cannot be credited with successful tribute protection in this match. Placement volume alone is not causal evidence for the combat advantage.

### Transfer to our bot

Contest needs two explicit objectives in the planner: convert a gem objective if feasible, and preserve/improve the gold tiebreak when gem conversion is not realistically available. “Always avoid fighting” and “always siege the monolith” are not supported by this outcome.

Proposed sequence:
1. First diagnose whether our losses are repeated unsupported engagements, poor fight evaluation, income interruption, or an objective-selection bug.
2. Test a contest-only change to commitment/retreat or tiebreak-aware target valuation. Keep the existing draft and items initially.
3. Only then isolate Ryth/Ren or a contest-only investment build, with enough comparable opponents to avoid overfitting this one historical match.

**Current project evidence matters:** NOTES now records W9 `v12c 15/25 vs v12f 13/25`, with contest `2/5 vs 0/5`; v12f is rejected. This contradicts treating prolonged defensive memory/home-side caution as established progress. W10 tests v12h's earlier shopping. Do not mix these interventions into that trial or adopt an old candidate because it sounds like the story here.

## Counterexamples from the same series

**Expanse:** Fish wins 1008–862 with no deaths on either side. Mite buys first at 34, Fish at 67; Mite's first tribute is 54, Fish's 61. Mite even leads early gold at round 200 (1150 vs 1110), yet loses. Monster vs Jungle, Varg vs Ren, allocation and routing all differ; the summary cannot isolate them.

**Rushbait_v2:** Mite banks earlier (first tribute 71 vs 136) and still loses 776–1008. At round 400 it leads banked score 578–512 but trails collected gems 710–768. Fish banks a late sequence of **94, 66, 132, 36, 168** gems at rounds **519, 525, 526, 527, 538** and wins. Earlier banking can be useful without being an unconditional advantage: excessive travel might sacrifice throughput, but this causal explanation still needs route evidence.

## What this changes in the working model

Three separate mechanisms explain the three Mite wins at the level the data supports:
- **Stampede:** repeated capture and delivery of the actual gem source; camp count is misleading.
- **Rows:** faster completion of the last score cycle; bigger economy and bags do not decide the race.
- **Contest:** gold tiebreak with strong survival/combat and camp throughput; no gem siege was completed.

A single opponent label such as “aggressive” cannot substitute for classifying the map's victory route and the current economic/race state. Opponent modelling should alter a mechanically sound map plan, not cover up a target-selection or banking bug.

## Limitations and checks

Five complete official summary JSONs were parsed. All ten team scores reconcile with both summed champion submitted-gem metrics and positive tribute events; recorded outcomes reconcile to Mite 3–2. No full replay was watched, no routes or spell sequences are claimed, and no bot test or platform scrim was run. Five fuel-exhaustion entries appear across Mite's rows (one) and contest (four), versus zero for Fish; there are zero reported bot faults for both teams in the downloaded summaries. Counters and event semantics are retained as supplied.

Historical submission IDs were not exposed in the inspected overview. Opponents, maps, item builds, draft orders and sides differ; no single item, champion or ward policy has a causal estimate here. Recommendations are isolated experiment proposals, not proven upgrades. No code changed and no ladder submission was made.
