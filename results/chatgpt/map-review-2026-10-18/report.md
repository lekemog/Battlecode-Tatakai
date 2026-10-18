# Recent map-by-map review: 18 October 2026

## Verdict and scope

Our latest results support investigating map dependence, but do not yet establish an opponent-adjusted map ranking. I collected the latest **13 completed ranked series visible at collection start**, in displayed newest-first order: **65 games covering all 17 maps**. Source observations and a reproducible parser accompany this report. These are fresh match-overview observations, not a replay review.

Version separation is essential: **v92: 19/25**, **v91: 5/5**, **v90: 17/35**. The newest five series all show v92 and all are series wins. Main `c925c5f` identifies v16t as deployed; this review did not freshly fingerprint the platform archive. v91's source identity is unknown. The v92 performance cannot be credited to engage: opponents and map draws changed, and v90 also had a different draft. Opponent versions are not exposed in these observations and remain null.

**Most useful leads:** contest is consistently weak; interlock and expanse look stronger in this cohort; corners remains a repeated weakness. Eight is a severe v92 failure worth immediate diagnosis, but has only one current-version game. Historical weaknesses do not automatically remain current weaknesses: swirl won its sole v92 game by 520 gems.

## All maps, with current and historical strata kept distinct

`All` pools these 65 games for descriptive context only. Gem margin is ours minus theirs; tiebreak scores unavailable in overview remain missing. The v92 average excludes those missing scores.

| Map | v92 wins/games | v92 mean gem margin | All wins/games | Assessment / next behaviour to inspect |
|---|---:|---:|---:|---|
| ambush | 2/2 | +284 | 3/3 | Promising conversion, not a solved route. Compare capture-to-tribute intervals. |
| collision | 2/2 | +437 | 3/6 | Strong recent recovery; v90 was 0/3. v92 finishes vary 645–970 rounds, so diagnose slow wins too. |
| contest | 0/2 | unknown | 0/5 | Highest-confidence weakness in this cohort. Both v92 games reach r2000 and lose gold tiebreak. |
| corners | 0/1 | −272 | 0/3 | Repeated cross-version weakness. Inspect which small camps are rejected, grouping and productive uptime. |
| eight | 0/1 | −936 | 2/3 | Severe current failure: 72–1008 at r472. Older wins refute a universal map incapability. |
| elkring | 2/3 | +18 | 2/5 | Volatile. Latest loss 558–1026; two wins 1026–684 and 1026–846. |
| expanse | 3/3 | +165 | 5/5 | Promising but two wins are only +96/+78. Finish rounds 674/687/676 suggest checking repeatable routing, not assuming adaptation. |
| fragment | 1/1 | +148 | 3/5 | Current evidence too small. Wins at 1023 rounds can conceal conversion delays. |
| interlock | 3/3 | +567 | 6/7 | Strongest repeated positive signal here; preserve as a regression-control map. |
| lanes | 1/1 | +282 | 2/2 | Positive but thin. Inspect hidden-camp stalls and ranged poke; do not transplant the old Issac example to current draft. |
| monolith | not sampled | — | 1/2 | No v92 conclusion. Need current games and siege/ordinary-objective route traces. |
| packs | not sampled | — | 0/3 | v90 concern only; do not label current v92 broken without new games. |
| pilgrimage | not sampled | — | 2/2 | Historical positive signal only. |
| rows | 2/2 | +281 | 4/4 | Both v92 wins finish r442 at exactly 1023 gems. Check repeated route schedule/respawn waits in logs. |
| rushbait_v2 | 0/1 | −298 | 1/2 | Current loss 746–1044; older v91 win is not a matched control. |
| stampede | 2/2 | +720 | 6/7 | Strong outcomes but slow: r980/r1119. Investigate speed to 1080, not only the eventual win. |
| swirl | 1/1 | +520 | 1/1 | Current counterexample to treating historical death-heavy classification as a present verdict. |

Small samples are genuinely small: even 3/3 has a Wilson 95% interval of roughly 44–100%; 0/2 roughly 0–66%. Games in one series share an opponent, so per-game independence is also doubtful. No significance claim is made.

## Code explains policy, not the observed causal loss

Source: `bots/v16t/src/bot.cpp` at main `c925c5f`. These are static control-flow findings. Without fresh logs they do not prove which branches executed in the games above.

### Contest: restricted gold farming without a proactive solo siege

`init()` L105–120 excludes monoliths from ordinary gem-camp rate calculation and records `siege_group` when those rates are zero. `solo_target()` L718 skips any uncleared monolith; L722 restricts selected camps to our half when `siege_group>=0`. `handle_enemies()` L851 rejects favourable fighting when alone with no nearby ally away from home. `play_turn()` L1026–1029 opportunistically takes a visible, already-cleared monolith reward nearby.

Thus in solo mode this is **home-side farming + opportunistic pickup**, not an explicit regroup/clear/capture/bank monolith plan. The blanket comment that we never fight down a monolith is too broad: `choose_group()` L642 can admit a monolith in pack mode under its clear-time/damage gates. Establish actual initialization/mode transitions per map before changing it.

Both latest contest losses are gold tiebreaks. That does not establish zero gems, exact gold totals, excessive deaths, or that a siege would have been affordable. The missing trace questions are: gold income rate, deaths feeding enemy gold, idle travel/waiting, safe monolith opportunities, and how much time objective conversion would cost. Do not blindly add a siege at a fixed round or bundle a new draft with it.

### Corners and farming maps: grouping and camp rejection

`init()` L111–115 forces pack behaviour for runtime rosters of at least four on gem maps, with a dimension override (`75<=max(W,H)<100`, area>=2500) that can force solo. The comment associates it with expanse/lanes, but the actual predicate is dimensions, not a map-name whitelist. `play_turn()` L1031–1032 can change solo to pack after r120 if team tributed gems and that champion's bag are both zero. Without logs, initial mode is not sufficient to identify the whole match policy.

`choose_group()` L635–648 can reject dangerous single camps and applies starvation/safety adjustments; the repository notes already report missed 22-gem camps on corners. Latest corners loss is consistent with that concern, but does not establish the same cause. `solo_target()` L725–726 still takes the minimum visible monster HP rather than summing group remaining HP: an already-known modelling flaw, not a newly discovered explanation of these losses.

Pack travel uses a distance field (L601–614); solo scoring uses Chebyshev distance (L729), plus an 8-round commitment and 1.6 current-target bonus. Walls can change ordering. Respawn waits over travel+10 are excluded; pack follower logic may retain a target for up to 12 rounds of remaining wait. Measure per-champion travel, actual attacks, capture, blocked movement and waiting separately, on corners plus positive controls interlock/rows/expanse.

### Elkring/eight/swirl: do not prescribe blanket caution

`handle_enemies()` precedes `bank()` (L1002–1003). v16t's engage branch (L862–867) can return true while discarding movement/combat booleans, suppressing downstream resource conversion even if those actions failed. This is a previously reported static risk, **not reproduced in these matches**. Successful engagement can also displace a carrier without yielding a kill. The losing eight game and volatile elkring should be traced for these cases, alongside range/focus burst and camp rejection; final scores alone identify none of them.

Historical full-package caution tests v16p/q/r failed. Their rejection does not prove every narrower safety fix bad, nor prove the engage branch good. Require actual progress and opportunity-cost evidence. Swirl's current win is a useful counterexample to a blanket 'all contested maps need more caution' rule.

## Concrete replay work queue

| Priority | Match | Why / required trace |
|---|---|---|
| 1 | `73d52d1a-077f-4f63-8228-b2d3c68e4512` contest | r2000 gold loss vs Sneaky Bush Campers. Compare income, wasted time, deaths and feasible monolith opportunities. |
| 1 | `b202bbe0-82ea-4beb-aa95-e8dfe2878e5c` contest | Independent latest opponent, same tiebreak failure; seek a common mechanism and counterexamples. |
| 2 | `c303135d-5851-4f2b-8dd3-8ca9bd0f8c02` eight | 72–1008: identify first divergence in score, camp choice, deaths or no-progress, not just the final collapse. |
| 2 | `91cc9ca9-56c2-4823-9723-9c1c0944219e` corners | Small-camp safety rejections, squad assignment and actual value delivered per alive round. |
| 3 | `fe9af04f-b68a-4e16-a317-5ff55ef09082` elkring | Compare to elkring wins `118c1dcd-e881-4c60-bd57-6ce0c90cb7ce` and `b6238a1b-3f5c-48e2-9eb9-5e330f9b353f`. |
| Control | `67094d08-7e50-48bb-a9ec-3edbec66edcf` expanse | Narrow +78 win; identify which delivery made the difference. |
| Control | `6e631c22-04bf-43d4-b6ab-1a79ac72585e` interlock | Positive control, +302 despite being the closest of three interlock wins. |
| Speed | `7a796dcc-6f99-4b0b-8d23-75bae39d86da` stampede | +720 but r1119: capture cycle, reward splitting, tribute travel and shopping latency. |

For each case use opening / first score divergence / midgame / final delivery. Export first-buy and first-tribute rounds; collected vs banked vs lost gems; gold earned vs gold held; camp IDs and rejections; per-champion activity; carried-bag age; fight/chase/engage duration and outcome. Keep nearby-altar deaths distinct from verified tribute-channel deaths. Keep stale log samples and unknown causes explicit. Zero or two deaths does not prove a pure farming loss.

## Collaboration contract for Leke and three teammates

This is a proposed shared queue, not an assignment of anyone's work. Each teammate/agent can claim a map or experiment in Issue #6 with branch, baseline commit, candidate folder, status and evidence link. No names or GitHub handles have been guessed.

- Main Claude retains the only ladder-submission and platform-test ownership. Analysis does not authorize another agent to submit or consume active scrim slots.
- Work in separate branches and new version folders. Do not overwrite teammates' branches, bots, notes or in-flight test artifacts. This PR is additive docs/data/tooling only.
- Ask the test owner to queue isolated experiments. Record actual both-side submission IDs, map, side and opponent version at match creation. Publish completed and missing counts, not only decoded successes.
- Compare map-specific changes against paired map/opponent/side/version cells. Lead with real wins including tiebreaks; margins and mechanisms explain those wins. Retain strong-map controls so a contest fix does not silently break interlock/rows/expanse.
- Use structural features (camp rewards, geometry, group damage, bank distance) when generalising; tournament layouts will be unseen. Map-specific findings guide diagnosis, not hardcoded claims of tournament readiness.

## Access limitations and reproducibility

Fresh browser sign-in works. One elkring summary request returned 'Too many requests; retry in 21 seconds'; a contest team-log request later also returned HTTP429/retry15s. No new detailed summaries or logs were obtained, and no visual replay was watched. The raw decoded files cited by `tools/audit/fetch.py` and `audit.py` live under another agent's `/home/claude/data/our_rep`; they are not in this checkout. Historical audit counts are secondary repository evidence, not newly reanalysed raw events.

The report therefore completes the fresh outcome inventory and static code diagnosis, but **does not claim exact per-map decision reconstruction**. That requires the queued summaries/logs. Latest recent-ranked opponents are around our ladder neighbourhood, not necessarily top100; do not conflate these 19/25 wins with top100 test-cycle performance. Team names alone are insufficient for cross-study joins; preserve the actual team IDs from each source page, and do not borrow a current opponent rank from a name match.

Run `python summarize_maps.py source-series.json source-cohort.json evidence.json`. Parser validates five maps per series, unique match IDs, side orientation and score/winner consistency; tiebreak values stay null. No network, bots, matches or tests are launched by the parser. Review the raw source snapshots and normalized evidence together.
