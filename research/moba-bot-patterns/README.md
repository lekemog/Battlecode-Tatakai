# Dota 2 / League bot ideas: original C++ research examples
17 October 2026. For main Claude, Szymon's agent and ChatGPT.

**Status:** research and host-tested examples, not a new playable bot. No Polaris source changed, no SDK integration, no game benchmark or submission. Code here is original illustrative C++20, not Riot/OpenAI/Valve code and not a port of their agents. It deliberately exposes estimates instead of inventing calibrated win probabilities.

## Primary sources and actual upstream code
1. **OpenAI Five paper** (2019), https://cdn.openai.com/dota-2.pdf : Appendix G, physical pp. 43–45 (reward/team spirit), Appendix N, p. 59 (opponent sampling), pp. 2–3 (scope), Appendix H/action architecture for factorized actions. It describes learned policies with shared team rewards and a mixture of latest/past opponents. Its final setup was restricted to 17 heroes and excluded certain multi-unit items. This is not a cheap scripted algorithm we can copy. The useful transfer is to reason about team benefit and avoid evaluation against only one predecessor.
2. **OpenAI Five benchmark engineering account** (2018), https://openai.com/index/openai-five-benchmark-results/ : Training section. Movement and ward placement initially shared an action head; the team split them after observing problematic placement. This suggests separating information placement from movement intent, not that our proposed ward score is validated.
3. **Riot bot architecture** (2023), https://www.leagueoflegends.com/en-gb/news/dev/dev-leveling-up-bots/ : “Fun Technical Jibber Jabber.” Riot describes behavior subtrees for tasks including combat, escape, movement, jungling and purchases. The displayed tree is expressly illustrative, not their actual bot tree.
4. **Riot rollout report** (2024), https://www.leagueoflegends.com/en-gb/news/dev/dev-new-bot-ai-oh-my-coming-14-6/ : reports jungling, rotations and objective play, alongside extensive bug fixes. Its goal is a better learning experience for players, not proving a tournament-optimal strategy. Neither article supplies production implementation source.
5. **Public Dota bot author source**, OpenHyperAI, pinned inspected commit **cb814c6c8dc51ed08045d6efd9f4a48147992711**:
   - [farming mode](https://github.com/forest0xia/dota2bot-OpenHyperAI/blob/cb814c6c8dc51ed08045d6efd9f4a48147992711/bots/mode_farm_generic.lua)
   - [retreat mode](https://github.com/forest0xia/dota2bot-OpenHyperAI/blob/cb814c6c8dc51ed08045d6efd9f4a48147992711/bots/mode_retreat_generic.lua)
   - [MIT license](https://github.com/forest0xia/dota2bot-OpenHyperAI/blob/cb814c6c8dc51ed08045d6efd9f4a48147992711/LICENSE).
   Farming exposes GetDesire()/GetDesireHelper() and distinguishes farm roles; retreat separately considers health, regeneration and incoming damage. This is a real inspectable community implementation, not evidence of superior competitive performance. Follow dependencies to understand it before reuse. No upstream code is vendored here.
6. Valve's [Dota Bot Scripting reference](https://developer.valvesoftware.com/wiki/Dota_Bot_Scripting) was discovered but full page retrieval failed. It is a further reading link, not the basis for an unverified API claim.

All source claims above are historical and attributed. Everything below is **our proposed Battlecode adaptation**, not a claim those systems implement these exact formulas.

## Code map and concrete transfers
Read [patterns.hpp](patterns.hpp) and [patterns_test.cpp](patterns_test.cpp).

| Transfer hypothesis | Code | Why it might help Polaris | What would refute it |
|---|---|---|---|
| Separate macro choice from execution; preserve an active action unless invalidated or endangered | select(), Commitment, Option | Combat or a fluctuating camp score need not silently cancel a tribute/capture. Different tasks share one explicit utility scale. | Longer commitments lose valuable opportunities, delay escape or keep invalid targets. |
| Maximize team benefit across independent tasks, rather than each champion picking its personal best camp | assign() | Gives distinct single-owner jobs to at most six agents; idle is allowed. Can include bank/shop as agent-private jobs with invalid entries for others. | Travel, uncertainty or shared-memory overhead erase gains; assignments disagree across champions. |
| Value the collection-to-score cycle, not camp reward alone | cycle_rate() | Includes arrival-aware respawn wait, clear/capture time, bank travel and tribute, plus a health reserve. | Per-camp banking assumptions overprice trips: a multi-camp loop beats the selected job. |
| Select a useful legal action on a visible target, accounting for already committed allied damage | focus() | Avoids assigning several attacks to an enemy already predicted dead; can value interruption. | Reservations are stale, allies cannot execute, or focus splitting lets enemies survive. |
| Place information where a decision could change; compare relocation with keeping the existing ward | vision_gain() | Relevant unseen approach tiles can matter more than always placing in travel direction. | Extra vision changes no action, or relocation loses more useful coverage. |

### 1. Decision structure: use the idea, avoid an architecture rewrite
The selector demonstrates explicit commitment, utility and emergency override. It is not Riot's proprietary behavior tree. A production adapter should produce clear outcomes such as success, running and failure; calling a handler is not evidence of a successful action. select() intentionally returns no action when no positive option exists, except a valid existing commitment can be retained during its lease.

**Important:** emergency is a caller-supplied judgment, not an automatic proof. Unsafe channels must be invalidated or given a legal emergency escape. Duplicate option IDs are not supported. Turn costs, loss and uncertainty need common units. Do not put raw gold, HP, probability and gems into one sum without specifying conversions.

**First experiment:** carrier-aware pursuit versus current order, leaving draft/items unchanged. Inspect completed tributes, lost carried gems and actual wins. Existing missing siege transitions and group-HP errors deserve correction before a new selector.

### 2. Team allocation: exact mathematics within a deliberately narrow model
assign() exactly solves the **supplied additive single-owner assignment matrix**, bounded to six agents and sixteen jobs. Runtime is O(jobs × agents × 2^agents); the claim of exactness concerns this matrix only. It does not solve the game optimally. Siege groups, escorts, shared rewards and complementary spell combinations violate additive independence.

A legal adapter must obtain a consistent snapshot through permitted observations/communication. This offline helper does not give champions free access to one another's private knowledge or expand shared memory. Use expiring claims if centralized allocation cannot be executed consistently. For jobs requiring several champions, build a separate small set of coalition candidates and evaluate overlap explicitly; do not pretend duplicate camp columns model synergy.

**First experiment:** assignments on a zero-death farming map, after fixing group HP. Compare unique camps served, productive travel, score pace and win outcomes. Include rows/expanse regressions. Use assignment only if it improves on the current cheap claims.

### 3. Farming tempo: use conservative mechanics, not a borrowed coefficient
cycle_rate() is a one-camp cycle estimator. Caller computes remaining wait at arrival, not raw time until respawn, and supplies full-group predicted damage with conservative unseen-member allowance. It does not learn damage from the flawed capture-end “solo” sample described in Issue #6.

It assumes banking after this cycle and therefore may be too pessimistic for nearby sequences of camps. An optional next step is bounded two-stop lookahead with actual path distances and a final bank leg; do not add it before measuring this bias. On gold-tiebreak maps, use a separately defined gold objective, not arbitrary gem conversion.

**Do not import Dota creep-stacking, lane freezing, last-hitting or deny mechanics:** they are not established features of autumn Battlecode.

### 4. Combat: useful reservations must be executable
focus() caps useful damage by remaining HP after allied reservations. The interruption bonus is a heuristic in HP-equivalent units, not calibrated expected win value. The caller must validate range, vision, cooldown, target identity and the actual action API immediately before execution. Nothing here models movement, mitigation, healing, retaliation, stun duration or attack order.

Reservations should be short-lived and conditioned on allies actually being able to act. A channel interrupted by a predicted hit is not a confirmed interrupt. No new always-fight rule follows from the source material.

### 5. Vision: expected information value is not ward count
vision_gain() only sums caller-assigned weights for newly covered decision-relevant tiles. It is a deterministic proxy, not a Bayesian value-of-information calculation. Correct geometry, duplicate-tile removal, existing allied coverage and legal placement belong in the adapter.

Compare forward placement, altar approach coverage and keeping the old position. The model must not use true unseen enemy locations. A historical sighting can motivate uncertainty, not fabricated current vision. Evaluate whether new observations alter routing or banking and whether those changes help.

## Testing and integration
Host checks:
```sh
g++ -std=c++20 -O2 -Wall -Wextra -Werror -pedantic patterns_test.cpp -o /tmp/moba-patterns-test
/tmp/moba-patterns-test
```
Passed: 200 randomly generated small assignment matrices checked against exhaustive enumeration, plus scenario checks for channel retention/escape override, invalid actions, nonfinite inputs, health reserve, arrival waiting, overkill reservations and redundant vision. These verify helper semantics, not strategic strength, Wasm fuel or SDK compatibility.

Choose **one** module for a new bot folder/branch and measure it against the frozen baseline. Keep old source and report exact source/platform version, map, side, opponent and result. Use wins and official tiebreaks first, gem margin as secondary; do not let arbitrary proxy rewards determine promotion.

**Current evidence integrity warning:** main Claude's CONVERSATION.md update (~22:15, blob 20e1a7aaf4e12e11d6acb3821913a815f702055d) reports an outside submission of platform v58 during W13, contaminating the v13c arm. Audit match-level submitted versions before using that round. A larger unverified sample does not repair mislabeled treatments.

Only designated main Claude submits or queues platform scrims. This example folder has no credentials, network access, submission code or SDK dependencies.

## My priority judgment
1. Highest near-term value: full-group damage/clear-time correctness, clear action commitment, and independent productive camp assignments.
2. Plausible after those: decision-relevant vision and conservative focus reservations.
3. Lower near-term value: new RL training, large behavior-tree rewrite, clever draft search without a reliable value function, or an unvalidated opponent-class strategy package.

The research supports testing these design patterns. It does not establish that any of these examples beats the existing bot.
