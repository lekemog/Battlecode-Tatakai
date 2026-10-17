# What past winners actually said: Discord history review

18 October 2026 (Europe/London). Research for Polaris, main Claude and Szymon's agent.

## Who was searched, and why

| Author | Verified reason for inclusion | Search coverage screened |
|---|---|---|
| [Blue Dragon] Sam / samh___ | Official #announcements names Blue Dragon with Sam and Benjamin as Sprint 2 winners (29 March) and Sprint 3 winners (6 April); Sam's profile also displays Sprint 5 Winner. | All 206 results returned by from:samh___ in:strategy, across nine pages. |
| [The Rational Merlin] /// / tripleslash__ | Official #announcements, 23 March, names The Rational Merlin as Sprint 1 winner; profile badge agrees. | All 39 strategy results and 99 devs results, across six pages. |
| Benjamin Kovacs / benjaminkovacs. | Named alongside Sam in the official Blue Dragon winner announcements. | All three results returned for the verified account; no strategy-channel results. |
| [Intercontinental Fish] Miles / s0miles | Strong current opponent already included in our ranked-match studies; not identified here as a historical tournament winner. | All 37 results returned after 12 October across two pages. |
| [Mite] xRyann_ / xryann_ | Strong current opponent whose wins over Fish were analysed in PR #4; not identified here as a historical tournament winner. | All 48 results returned after 12 October across two pages. |

**Total: 432 author-search result entries screened**, plus winner-verification searches and surrounding original discussion in four selected cases. Some entries were empty/image-only or labelled “Message could not be loaded”; screening a displayed excerpt is not the same as retrieving every attachment or complete conversation. Search indexing can omit content. This is not all history from every winner.

Only relevant Battlecode material is summarised. No DMs were searched, no messages were sent to Discord, no bots/scrims/submissions were changed. Publication to this repository follows Leke's explicit clarification.

## Main judgement

The useful lessons are about **choosing and validating decisions**, not copying one advertised meta. The search did not reveal a complete winning algorithm for the current game.

Past success earns attention, not automatic agreement. Old healing turrets, conveyors, titanium, launchers and axionite belong to the spring game. Their costs and tactics do not transfer directly to autumn champions, camps and tributes. Current Fish/Mite comments also contain jokes, impressions and limited implementation disclosure; do not invent their internal architecture from them.

### 1. Economy, attack and defence must be valued together

**What Sam said:** on 12 April at 19:10, he described the three interacting jobs as building an economy, damaging the opposing economy, and defending one's own. He explicitly allowed strong disruption to compensate for weaker economy. Original message ID: 1492950176799789136 in #strategy.

**Context checked:** this answered a request about improving from low rank, amid advice to work on economy. Nearby, another participant reported a pure-economy bot beating Kessoku. That is an unverified participant match claim, but it is a useful warning against turning Sam's framework into “all bots must fight constantly.”

**Our Battlecode hypothesis:** evaluate a proposed contest by the value gained or preserved and the value denied, minus our opportunity cost. A kill is one possible mechanism. A safe camp clear, escorted tribute or forcing a carrier away from an altar can also be valuable.

**My critique:** this does not justify replacing farming with aggression. We have previously lost maps with no deaths, and excessive caution has also failed tests. Diagnose the particular map and bottleneck first. Do not put gold, gems, HP and kills into one arbitrary sum and call it a win probability.

**Experiment:** isolate one local contest decision with a bounded alternative: farm elsewhere, protect a carrier, or contest. Record own tributed gems, opposing tribute delay, own lost productive time, deaths and actual terminal outcome.

### 2. Effective pressure can matter without a kill

**What Sam said:** on 5 April at 23:36, an opponent could be neutralised by being forced to spend its time healing. When another participant objected that it could walk away, Sam replied that repelling it was itself a result.

Original messages: 1490480274876792932 (healing downtime), 1490480404686311556 (repelled), #strategy. The original conversation was a spring defensive-combat discussion, not an autumn farming benchmark.

**Our adaptation:** count forced recall, lost camp access and delayed banking when reviewing fights. A short attack that causes an enemy carrier to abandon a safe bank may outperform a long chase that finally gets a kill.

**My critique:** damage dealt is still a bad standalone reward. If we send two champions on a long detour to make one enemy briefly heal, we may lose more productive time than it does. Ending a chase can be the correct result even when we have dealt damage.

**Experiment:** compare the unchanged parent with a short pursuit budget tied to a concrete objective. Classify the end of pursuit as kill, enemy disengagement, our disengagement, or wasted chase. Use score/wins to judge, not more damage or fewer deaths alone.

### 3. Damage and healing breakpoints can change the best action

**What Sam said:** on 5 April at 23:34 he distinguished values by whether a unit survives two shots with healing in between; nearby he discussed coordinating two attackers for a kill. Original message 1490479879999979632, #strategy. Earlier values belong to the spring balance patch.

**Our adaptation:** score a legal same-round combination using the target's actual HP, shield, available attacks, resets, abilities and action order. For farm estimates, model the number of actions needed to kill each monster rather than using only smooth average DPS.

**My critique:** this is not permission for a large combinatorial search every turn. A small enumerated set of legal attack/reset/spell sequences may be enough. Nor should five allies overkill a target because every instance independently predicts the same kill. Revalidate after actions and account for who already acted.

**Experiment:** controlled HP values just below/at/above a relevant threshold, including shield and turn-order changes. Verify action legality and remaining HP, then compare the bounded evaluator against its parent in release Wasm with fuel measured.

### 4. Beating a famous opponent is not the same as improving the bot

**What Sam said:** on 31 March at 22:34, beating Blue Dragon while continuing to beat the rest of the field was harder than building a narrow counter.

**Context checked:** another participant immediately said its new bot could beat Blue Dragon 3–2 while losing to most other teams. That is a self-report, not independently verified match evidence, but it directly illustrates the intended warning.

[Verified original discussion](https://discord.com/channels/1479274986203123883/1482062553990566080/1488652663620108519). Sam message ID 1488652663620108519; nearby self-report 1488652765960994867.

**Our adaptation:** maintain a matchup matrix across distinct opponent styles, not just a headline against Fish, Mite or the previous Polaris. Report map/side and version IDs. Keep a small held-out cohort for confirmation.

**My critique:** demanding improvement against every opponent can reject a sensible overall tradeoff; averaging everything can hide a catastrophic weakness. Declare the target opponent mix and unacceptable regressions before choosing the winner. A 23/34 local win count is useful evidence for that matchup, not tournament proof.

**Experiment:** test one isolated candidate against the frozen parent and several distinct legal opponents, both sides, separating farming and contested layouts. Show the result vector and uncertainty, not only aggregate gem margin.

### 5. Non-transitive matchups are plausible; authority is not a proof

**What Merlin said:** on 14 March at 03:01, strategies could form A-beats-B, B-beats-C, C-beats-A cycles. Sam, at 04:12, later discussed exploiting a non-uniform opponent population.

**Context checked:** this was an informal discussion of perfect play and mixed strategies. Merlin's stronger remarks about no best program and mixtures losing to everything were not established by that discussion; a later “Oh” followed an explanation. Do not cite those remarks as a theorem.

**Our adaptation:** a ladder Elo and a single best-response test can both miss matchup structure. A cautious policy, a fast farmer and a fighter may each expose different weaknesses. Opponent modelling is useful only when it selects a response that improves results against the appropriate opponent class.

**My critique:** this provides no validation for an aggression byte, invented “playstyle” labels or random strategy switching. Choose responses using observable, calibrated evidence and test the selector separately from the policies it selects.

**Experiment:** first measure a fixed policy-by-opponent matrix. Only if actual differences exist should we test a cheap within-game selector. Compare it against each fixed policy and a non-adaptive baseline; record incorrect switches and losses from delayed recognition.

### 6. Successful teams still use simple heuristics and repeated review

**What Sam said:** 6 April at 00:10 describes choosing the largest heuristic; 9 April at 05:25 emphasises sufficient game samples, and at 05:35 identifying problem maps and judging changes. On 16 April at 23:10 he described mature bots adding features/fixing bugs, with small changes capable of changing behavior substantially.

**Our adaptation:** start with a bounded, interpretable task score and reason-coded decisions. Trace a loss to the exact branch that chose farming/chasing/banking. Keep one experimental change per candidate.

**My critique:** “the winner used heuristics” is not proof our current weights are right. A simple rule can be consistently wrong. A large test count also cannot fix duplicated matches, weak opponents, version contamination or a metric that ignores gold tiebreak wins.

**Experiment:** for a candidate, nominate its predicted effect before testing, inspect examples where that effect occurred and where it did not, and verify that the outcome changed for the expected reason. Do not infer causal benefit solely from an aggregate win count.

### 7. “Feature exists” and “feature pays off” are different

**What Sam said:** 6 April at 21:01 cautioned against using launchers if they offered no benefit; 8 April at 16:33 distinguished writing breach behavior from supplying it at a useful location. These are spring examples, not an autumn equipment recommendation.

**Our adaptation:** wards, locks, teleports, focus reservations and opponent models need a named consumer and a measured payoff. A placed ward should alter a route/threat decision; a bought lock should actually delay an opposing bank enough to justify its gold and time.

**My critique:** activity counts are not capability. More wards, more casts, more locks or more model updates can make the bot slower without improving any decision. This agrees with PR #11's fuel and conversion audit; it does not introduce a new all-features candidate.

**Experiment:** add one feature behind an isolated flag; measure the decisions it changed, useful time/resources gained and release fuel. Reject unused information and redundant overhead.

### 8. Current strong players emphasise review and generalisation, not disclosed secrets

- **Fish / Miles**, 16 October 16:14, #questions “Tips and Tricks?”: recommends watching losses to understand why they happen. At 15:36 in #general he attributes rating changes after new maps to overfitting. The latter is an impression, not a controlled experiment.
- **Fish**, 16 October 10:02, #devs: reports quicker fuel exhaustion. This is a version-audit lead, not evidence of a universal fuel change.
- **Mite / xRyann_**, 15 October 00:51, #questions “qualifying and sprints”: asks for a larger match count to reduce variance. On 17 October 02:25 in #suggestions, asks for slower replay playback. These suggest what the author wanted from testing tools, not proof of how Mite trains or evaluates internally.
- **Mite**, 14 October 15:42, #general: stresses understanding how to direct LLMs rather than merely asking them to win. Treat this as workflow advice, not evidence that a particular model or prompt produces stronger bots.
- **Benjamin**, 6 May 14:33, #general: describes a historical case where a cheapest-path policy avoided an expensive unreachable resource route, while distant-resource maps were less reliable. The lesson is to test the interaction of target choice and reachability. It is **not** evidence we should remove reachability checks.
- Merlin's October source release in #open-source points to https://github.com/nzjt/cambattlecode26 . Source code was linked previously; this chat-history review does not claim a new code audit.

## What I would actually ask the agents to do

1. Keep PR #11's correctness/fuel checks first. No sophisticated strategy survives repeated forced suspension or resource-conversion stalls.
2. Add **objective-based pursuit accounting**: why a chase started, what it prevented/gained, when it stopped, and the productive time it cost.
3. Audit **damage breakpoints** on existing champion sequences before adding a larger combat search.
4. Present a **matchup matrix** and held-out-map result for the next candidate. A win against one predecessor cannot settle readiness.
5. Treat denial/forced recall as a separate experiment after farming correctness is established. Do not bundle it with draft, shopping and item changes.

These are recommendations for controlled experiments. None has been implemented or validated by this review. No candidate is endorsed for promotion.

## Source locator and limitations

Sources are server messages, not formal technical papers. Query text and timestamps make the observations repeatable for agents with Discord access. The exact server/channel URLs below were observed.

| Source | Where to find it |
|---|---|
| Winner verification | [#announcements](https://discord.com/channels/1479274986203123883/1479275336738013236): 23 March 16:15 (Merlin); 29 March 21:30 and 6 April 17:07 (Blue Dragon). Displayed profile roles were also checked for Sam and Merlin. |
| Historical strategy advice | [#strategy](https://discord.com/channels/1479274986203123883/1482062553990566080): use from:samh___ in:strategy and from:tripleslash__ in:strategy, then the dates/times above. All returned result pages were screened. |
| Merlin engineering history | [#devs](https://discord.com/channels/1479274986203123883/1480336541984362538): from:tripleslash__ in:devs, 99 results screened. Much is old-game balance/debug discussion or banter; it is not an autumn API reference. |
| Fish | from:s0miles after:2026-10-12, 37 results, all returned pages screened. [Tips thread](https://discord.com/channels/1479274986203123883/1549138713446191255/threads/1560670185176834111) was read in the prior audit. |
| Mite | from:xryann_ after:2026-10-12, 48 results, all returned pages screened. No detailed internal farming/coordination algorithm was disclosed in this sample. |
| Benjamin | from:benjaminkovacs., three results. The author was resolved through the official winner mention and Discord's matching author suggestion, not guessed from a similar name. |

The report deliberately omits unrelated personal biographies, conversation fragments, credentials and social discussion. There is no evidence here that fame makes a statement optimal, that all past winners think alike, or that the current leaders disclosed their strongest ideas in chat.
