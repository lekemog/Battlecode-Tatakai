# Rank-one field study: what we can learn, and what we should test

> **Engine boundary, 21 October:** Claude now reports the ladder on engine **1.0.2 / cambc 3.0.4**. All five independently reviewed Fish games below are **historical 1.0.1 evidence**, not current-engine validation. See [ENGINE_102_HANDOFF.md](ENGINE_102_HANDOFF.md) for the captured official combat changes, fixed-focus sensitivity and a matched-engine divergence test. No 1.0.2 Fish replay has been independently reviewed here.

Shared team research · 21 October 2026 · tracking issue [#36](https://github.com/lekemog/BattlecodeConversation/issues/36)

## Main recommendation

The original 1.0.1 study identified a **dash/build policy gap**, but it is not a demonstrated current-engine upgrade: Claude's 1.0.2 screen reports combined HoR candidate v23n at 46/140 versus v22w at 51, while smaller-bank v23m scores 57. Prioritise current-engine conversion and finish-time evidence; preserve the dash mechanism as a separately testable hypothesis. Do not generalise the small screen into a proven ladder advantage.

These are proposed experiments, not a claim that we have found a winning bot. No live bot, submission, scrim quota or deployment was changed.

## Coverage and provenance

The live ladder and team profile identify **Intercontinental Fish** (`1890540d-1ffc-4847-adbf-d0d08772f268`) as #1 at **2,322 Elo**, peak 2,331. The profile shows 693 ranked wins and 175 losses. The match-history UI was traversed to **868 loaded entries / end of history**; these are series entries, not 868 visually reviewed individual games. Virtualisation meant the saved inventory captured 724 distinct series URLs. A complete per-series/game census remains unfinished.

The ladder's last-50-game pick indicators show Heart of Ruin, Ren and Stellar each 50/50. The detailed current sample is **one five-game ranked series against procless**, `42c0ad6a-6ea5-4ea8-8dda-180339c5711b`, including two Fish losses. All five were downloaded and decoded successfully with the **official 1.0.1 engine** supplied by cambc 3.0.3. Engine 1.0.0 rejected them; no mismatched-engine results are used. Collection found a newer 1.0.2 patch announcement, but these replays remain 1.0.1 evidence.

The browser visualiser reports WebGL2 unavailable. We reviewed **reconstructed spatial frame sequences**, with champion positions, HP, bags and 15-round trails, then checked every round programmatically. The reconstructions omit terrain; they do not establish legal path lengths or the bot's hidden intent. Selected visual review rounds are recorded below. This is not a claim to have watched every available replay.

Three additional 1.0.0 elite replays against Mohnish were decoded as background (hello on contest/eight/gold_rush). They are **not Fish** and are excluded from the table and Fish conclusions. Historic top-20 replays from 17 October are also kept separate.

## Current five-game evidence

Fish is side B throughout. Gold = sum of champions' earnedGold, not unspent gold. Deaths = alive-to-dead transitions. Final outcomes/scores agree with the website.

| Map | Match ID | Fish / procless gems | Fish / procless deaths | Fish / procless earned gold | Result |
|---|---|---:|---:|---:|---|
| collision | `793352d2-2946-44a1-b89b-225a5879311d` | 1016 / 760 | 6 / 10 | 9442 / 6294 | win |
| fracture | `3a6c4ece-f962-4241-9369-234a5939d6a1` | 1011 / 830 | 10 / 4 | 6422 / 7434 | win |
| fragment | `7a568552-0496-47aa-a018-67af3b520a35` | 191 / 1022 | 37 / 12 | 3649 / 12444 | loss |
| split | `d148b5ea-d71d-4480-bff4-0fba938d6429` | 947 / 1003 | 2 / 3 | 5584 / 4430 | loss |
| concentrated_wealth | `8f0bc4a5-9eb5-426d-a180-fffe6083ad04` | 1000 / 693 | 3 / 4 | 7058 / 6054 | win |

### What its play actually shows

**It is not simply “few deaths and most gold wins.”** Fracture and split directly contradict that explanation. Deaths and gold are useful intermediate measures, but score conversion and completion timing need their own tests.

**Its current core is different from our historical elite draft.** In the three-pick games Fish takes Stellar, Heart of Ruin, Ren. Its five-pick games add Cassi & Issac and Ryth. This sample cannot prove that draft causes its rating advantage.

**It invests in focus carries.** On split at r800, Fish HoR has 988 focus, 2000 max HP, 11 Power-Focus emblems, Treasure-Focus, Home-Health and Durability-Health. Stellar has 517 focus. On fragment at r300 Fish HoR has 208 focus / 1000 max HP while procless HoR has 160 focus / 2000 max HP. The latter is a matchup/build contrast, not proof that one extra health purchase would reverse the game.

**It can recover from a large score deficit.** Collision: at r700 Fish trails 117–399, then reaches 430–432 by r900 and wins at r1370. At r750 Fish carries 103 gems and banks 172; at r800 it banks 282. Its economy advantage precedes the score comeback. A screenshot of score alone would badly misdescribe this position.

**It has exploitable failure cases, not just weaker opponents.** On fragment Fish leads gold 904–792 at r300, but by r600 trails 1249–2274 and has seven deaths to four. It banks 77 at r342 and does not increase that score until r798: a **456-round score drought**. Across its 37 deaths, 17 have no ally within six tiles five rounds beforehand (including three with no enemy in that radius). That is a proximity description, not attribution of every death to an enemy or proof of bad pathfinding.

**Split is a useful finish-race counterexample.** Fish leads 859–755 at r731; procless reverses to 945–859 at r768. At r800 the score is 970–914 and both teams carry 33 gems. Fish banks its 33 at r802; procless reaches 1003 at r809. At the final state Fish's Cassi holds 64 gems, enough to cross 1000 if delivered, but she acquired that bag late. We have **not shown it could legally have been banked before the loss**. The right experiment is scheduling harvest + delivery + channel completion, not asserting that a different bag cap wins this replay.

### Visual review checkpoints

- Fragment: r30, 100, 250, 300, 350, 400, 450, 500, 600, 900, 1200, 1800. These show changing separation between Fish's three champions and its stalled score; terrain-free frames alone cannot establish unsafe routes.
- Split: r30, 100, 300, 600, 700, 730, 750, 768, 779, 790, 800, 809. The score swing happens with few deaths and a large amount of bankable value changing hands.
- Collision: r30, 100, 300, 600, 700, 750, 800, 850, 900, 1000, 1200, 1370. The comeback develops after the opening rather than an early decisive rush.

## Code mechanism: why draft-only HoR is an incomplete test

Code inspected: main `ffb1478a9e5c6248a9fb3f57d1c38355d9fbd99c`, `bots/v22w/src/bot.cpp` and `draft.cpp`, plus v22u's draft. Re-check the newest branch before implementation.

1. `init()` computes focus value from targeted damage/CC and AoE modifiers; it does not add dash landing damage or shield scaling. HoR's dash and shield therefore do not contribute to this estimate. For a dash/shield-only kit, this favours strength under the existing calculation.
2. `combat()` evaluates heal, shield, attack reset, targeted damage/CC and AoE casts. It has no tactical `is_dash()` branch.
3. `move_to()` evaluates dash destinations by route distance and threat, not landing hits or stun value.
4. The official SDK defines dash as a **separate ability kind**. Its `modifier` scales landing damage with focus, `radius` specifies Chebyshev landing area, and `duration` is landing stun duration. `is_damage()`, `is_cc()`, and `is_aoe_damage()` do not automatically include it.
5. v22u inserts HoR sixth. None of the five studied games has six draft picks, so that insertion does not exercise HoR on these compositions.

This is a code-level gap, not yet a measured explanation of our ladder losses. Only kits with actual landing damage or stun exercise the new scoring branch. Ren was not a valid damaging-landing positive control in v22w; see DASH_OPPORTUNITY_AUDIT.md for the correction.

## Original experiments, in priority order

### A. Score tactical dashes before changing the draft

Keep v22w's draft/build fixed first. For each engine-legal landing tile, estimate damage on actual landing targets, non-overlapping stun value, follow-up attack reach, expected incoming damage and loss of the escape option. Compare against the best non-dash action. Reject an empty dash that merely makes the path shorter while an immediate objective/fight action is better.

Then independently fix the build estimate to include each kit's damaging dash and shield scaling. Only after behaviour is verified, test HoR in a slot that actually executes, with its supported build and micro. Use a factorial comparison to separate draft, build and landing policy; do not fold all three into an uninterpretable “copy Fish” patch.

### B. Plan the team's next decisive bank

When carried gems can finish the game, choose the smallest feasible set of carriers whose **legal, safe deliveries** can complete soonest. Compute arrival, altar availability and full channel time; protect that set and avoid optional shopping/chasing. When the team cannot finish from existing bags, include the next harvest in the estimate instead of banking everyone blindly.

For defence, visible enemy carriers plus submitted score give a lower bound on the opponent's finish threat. Unknown bags stay unknown. A stun that delays a winning channel may be worth more than a low-value kill elsewhere. A pure policy sketch is included in `policy_drafts.hpp`; it assumes ETAs are already legal and jointly feasible.

### C. Use participation time, not nearby-head counts

Our fight check counts allies within six tiles as combat strength, even if walls, cooldowns, channeling or another task prevent them contributing immediately. Estimate damage/disable each ally can deliver over the next few turns after path-to-range time. Fragment is the follow-up replay for testing this diagnostic. Do not infer contribution from omniscient enemy state that our bot cannot observe.

### D. Give an objective attempt an owner and an exit rule

Build on Claude's v22x siege positioning rather than duplicate it. Require a tank and damage participants to be in their valid roles before commitment; ensure the stage ring is outside the actual camp range. In v22w the stage ring includes distance five while the new monolith range is five. Verify against camp coordinates, not an approximate group centre.

A staging timeout should cancel/re-plan a failed assembly rather than automatically authorise an unsafe siege. Carry the plan through capture and delivery. Do not allocate new shared bytes casually: the current eight-byte layout already has squad/capture/threat uses. Use deterministic role selection or an explicitly reviewed memory layout and expiring task leases.

## Professional gaming ideas we can adapt

The transfer below is our inference; none is evidence that Fish implements that algorithm. These are strategic principles, not current LoL balance advice.

- **LoL: prepare the objective before entering it.** Dignitas's Worlds analysis describes gaining approach vision and using that information to enable earlier arrival/flanks. Our translation: scout the carrier route, establish a safe approach, and stage tank/escort before channeling. Judge warning lead time and completed banks, not raw ward count. [Dignitas: priority, tempo and vision](https://dignitas.gg/articles/blogs/Unknown/10280/transitioning-lane-priority-into-tempo-and-vision-control).
- **StarCraft: scout a temporary weakness, then commit.** Team Liquid's analysis of Life vs TaeJa describes decisions changing after scouting economic/technology commitments and pressure diverting an army. Our translation: attack an observed split or cooldown window, or take an uncontested camp while the opponent commits elsewhere. Do not imitate a fixed all-in or force a losing fight. [Team Liquid: TaeJa vs Life](https://teamliquid.com/news/2015/01/13/the-liquid-advantage-taeja-vs-life).
- **RTS timing attacks:** Blizzard frames attack timing as a decision about when an advantage exists. Our version should trigger on a completed emblem, allies arriving, shield/dash readiness or an enemy recall—not a fixed round number alone. [Blizzard: Timing Attacks](https://news.blizzard.com/en-gb/article/10036159/starcraft-art-of-war-timing-attacks).

## Validation request for team review

Start with A's dash-mechanics behaviour test, then one frozen paired benchmark. Log legal landing, targets hit, damage/stun, cooldown use, death within the follow-up window and fuel faults. Compare fixed drafts and then build changes separately. Count duplicate deterministic replays once.

For B, log the estimated team finish time, actual completed channels, interrupts, pending bags at defeat and lost farming time. Fracture/split demonstrate why lower deaths or higher gold alone cannot be the success criterion.

Use the current map pool and engine, both sides, held-out opponents including Daniel v8 and strong current dash-capable opponents where available. Do not generalise five games into a population effect. Main Claude owns any ranked trial.

## Reproduction and continuation

`series_evidence.json` records replay SHA-256s, final results, score changes, banking/death events and selected states. `fish_summary.py` reproduces that evidence from official decoder JSON; `turning_points.py` and `frames.py` generate the inspection output. Raw third-party replays remain downloadable from their match pages and are not republished here. The decoder is the repository's existing extractor adapted for the official 1.0.1 assets.

Remaining: complete all-series metadata inventory; stratify Fish's current and historical submissions/engine versions; extend the detailed sample across maps/opponents; inspect its losses against other top teams; run the proposed policy experiments. Hourly coordination continues in #36, with pointers in #33.

### Round-boundary and attribution note

The extractor keeps the first snapshot of each round and the final state. A bank or death timestamp in the compact evidence is the round boundary where the transition is first observed, not necessarily the native action's execution round. Use native event/action positions for sub-round causal analysis. Banking events are inferred from an alive champion's gem decrease and should be checked against the team score changes. A near-camp/no-enemy death is not a verified camp kill.

Claude has since added `tools/fishstudy.py` and opened #37 for the wider cohort. Our item/death review and hourly communication continue there, with #36 and this report as supporting evidence. The round-array-index issue and attribution caveats were posted directly in #37.


### Native recall audit follow-up — 21 October

See [RECALL_AUDIT.md](RECALL_AUDIT.md) for 289 native recall starts / 264 completions in these same five games, exact action-round evidence and reproduction scripts. This deepens the five-game review; it adds no independent games. The compact cache records zero Fish recalls for each of these five games, so its population recall rate needs recomputation. High-HP shopping resets contradict a low-HP-only policy. Item ID 35 is **Home Emblem of Health**; my earlier Jungle-Focus label was wrong and is corrected above. The dash/build gap remains a separate proposed experiment. Hourly coordination is in #37.


### Finish-time recall follow-up — 21 October

[FINISH_RECALL_AUDIT.md](FINISH_RECALL_AUDIT.md) joins all 289 native recall starts to conservative prior banked-score bounds. Two starts have an individually sufficient winning bag: fracture Ren r1061 (981+22) and collision Stellar r1342 (983+66). Both games are wins; neither proves direct delivery was legal, safe or faster. This motivates an ETA comparison across direct delivery, reset-return and a teammate's finishing bank. The audit adds no independent games. Reproduction and full records are committed alongside it. Posting to issue #37 remains blocked by the previously rejected PR-labelled comment parameter; no alternate-thread message was sent.


### Recall-trigger follow-up — 21 October

[RECALL_TRIGGER_AUDIT.md](RECALL_TRIGGER_AUDIT.md) answers Claude's 05:30 UTC question: the C++ sketches do not implement recall timing; 41 of the 289 native starts are at >=50% HP with <172 gold, including zero-gold cases. This falsifies that particular two-condition rule, not all possible threshold policies. The new channels.py still uses moved champion positions to guess spawn for completion detection, so its reported completion gap remains unvalidated. Claude reports v23k and v23d rejected; neither is a proven upgrade. Scripts and all 41 counterexamples are committed. No additional independent games were reviewed; issue #37 posting remains blocked by the prior target-parameter rejection.


### Dash-opportunity follow-up — 21 October

[DASH_OPPORTUNITY_AUDIT.md](DASH_OPPORTUNITY_AUDIT.md) responds to Claude's 06:45 UTC results. Plain travel dashes already exist: move_to is identical in v22w/v23f/v23n. Claude reports the damaging-landing-only candidate is a no-op under the baseline draft, so my earlier Ren positive-control suggestion was wrong. Ten-game cooldown-jump totals do not prove on-cooldown timing; measure held ready/legal opportunities and separate native dash displacement from walking. v23n's full paired result is pending. This run adds source evidence, not new independently decoded replays; coordination posting remains blocked as documented.


### Fresh source index — 21 October

[CURRENT_SERIES_STATUS.md](CURRENT_SERIES_STATUS.md) indexes five newly observed ranked Fish/Zarzorki games, including a close quadrants win and a rushbait_v2 loss. All five IDs are absent from the old 300-record cache. These are metadata-only: a browser download failed to synchronize to local analysis, so engine/submission IDs and replay hashes remain unverified. Independent decoded coverage remains five historical 1.0.1 games. The status also records Claude's current-engine candidate reversal and the lack of independently reviewed Vesper/Vendetta examples.
