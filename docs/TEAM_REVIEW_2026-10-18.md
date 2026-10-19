# Team review: preserving strengths and designing the next Polaris
18 October 2026. Review baseline: main `e9d3eb2c79afc2bfa3a41b9e8808ba63a9115959`. Our collective findings; proposed experiments are not validated fixes.

## Executive decision
Keep the recorded final v19n submission unchanged tonight. Our next development version should improve **productive time and reliable scoring**, with small independently switchable changes. Do not merge all earlier suggestions: some have now lost real tests.

The latest recorded deployment is v148/v19n at 20:19 UTC, not independently verified on the platform in this review. Sources: [submission log](../SUBMISSIONS.md), [final result](https://github.com/lekemog/BattlecodeConversation/issues/20#issuecomment-6254676865). No new engine runs or scrims were performed here.

## Current evidence, without hiding the losses
| Candidate | Weak-map development wins /75 | Strong-map check /35 | Interpretation |
|---|---:|---:|---|
| v18x | 6 | 6 | Earlier reference |
| v19f | 10 | 4 | Early recall improves selected weak-map total; possible strong-map cost |
| v19g | 7 | Not reported here | Focus plus lifecycle package |
| v19i | 6 | Not reported here | Conditional focus, but unintended off-gate maths change |
| v19m | 8 | Not reported here | Carrier protection plus lifecycle package; not a demonstrated improvement |
| v19j | 11 | Not reported here | Contest remains 0/15; extra win is on untouched stampede |
| v19n | 12 | 4 | Final recorded choice; eight 1, corners 2, collision 3, stampede 6, contest 0 |

These are reused development opponents, not an overall ladder win rate. “Same games” in team notes means matched test conditions; do not assume deterministic replays or fixed opponent binaries. The unchanged-map flips in v19j/v19n demonstrate baseline variability or uncontrolled differences. We cannot assign every extra win to the patch or estimate a stable noise rate from three flips.

**Where we are genuinely uncompetitive:** contest is 0/15 in the latest development comparisons; eight remains 1/15 for the final candidate. Corners 2/15 and collision 3/15 are weak too. Stampede 6/15 is relatively better, not dominant. “Strong maps” is a historical test-group label: 4/35 against this cohort does not establish current strength. We need earlier and current versions against a common contemporary panel before quantifying the loss of formerly dominant performance.

## What stronger bots do well
The best-supported distinction is not “more aggressive”: they turn time, income and positioning into score efficiently, and tolerate fights when those fights secure resources.

### Named examples against other strong bots
These are historical matches in our [12-summary Fish-centred study](../results/chatgpt/top50-study-2026-10-17.md), not universal team identities or current rankings.
- **Intercontinental Fish: productive combat and conversion.** Contest victories over Sneaky Bush Campers and AlphaSlop were 1000–0, with 80 vs20 and 63 vs40 camp clears. Fish still died29–30 times: winning did not require refusing combat. Against procless on elkring, clears tied24–24 but Fish won1008–612 with fewer deaths and lost gems. Against Sneaky on collision it cleared51 vs19 camps and won1068–330.
- **procless: efficient farming races in the observed matchups.** It beat Fish1022–668 on ambush with zero deaths and zero gem losses on both sides. That is a throughput/conversion defeat, not a fight-selection failure. It also won their rows and monolith games, but this sample cannot identify exact routing code.
- **AlphaSlop: strong map-specific economic execution.** It beat Fish4–1 in that series, including corners and lanes, but lost contest1000–0. Its corners win used fewer clears than Fish (28 vs34), so capture count alone is insufficient. Locks were present, not proven causal.
- **Mite: competitive races, uneven contested execution.** It nearly matched Fish on lanes (986–1006), and won packs/pilgrimage, yet lost eight0–1020. More wards did not save its swirl game. This is why copying one team's draft or ward count is not a strategy.

### Patterns against us and across top-vs-top play
Our own v19f eight sample leads earned gold299–161 at r50, but trails577–810 at r150 with roughly4 vs1 deaths. Contest already trails105–160 at r50 and314–834 at r150. These are different failures.

Kurian's corrected 49-game opening study finds contest winners take4.7 middle-third captures vs2.3, while own-third captures are almost equal. Eight winners bank aroundr101 vs152; collision first-bank timing is similar but banked gems diverge later. Stampede winners bank733 vs100 by r600 and many losers never bank. [Corrected research](https://github.com/lekemog/BattlecodeConversation/blob/kurians/top-openings/results/kurians/openings-contest-eight.md), [corrections](https://github.com/lekemog/BattlecodeConversation/issues/22#issuecomment-6253118920).

Interpretation: **secure useful camps, survive the transition, deliver, repeat**. These aggregate observations do not establish formation, exact routes or causes for each team.

## Regression investigation: three separate mechanisms
### 1. Early shopping: a real policy change, an unproven causal explanation
Source comparison of v18x/v19f controller shows the recall threshold180→110 before r250. It applies to repeated eligible recalls, not only the first purchase. Both require an empty bag and other safety conditions.

The r1 comparison lost interlock, fragment and swirl, gained pilgrimage: four discordances, net minus2. Plausible mechanism: extra recall/channel/return travel breaks camp cycles, group arrival or objective timing. We have not yet traced the lost matches to prove that mechanism. Do not turn these four games into a permanent map blacklist.

**Experiment:** compare180 vs110 with identical builds, then a bounded upgrade-aware recall: recall when an actual useful purchase/heal is available and its estimated benefit exceeds travel plus missed-objective cost. Record all recall triggers, actual purchases, return-to-action delay, camps missed and score. Re-run baseline-vs-baseline first to estimate repeatability. Preserve both sides and submission identity; record unknown opponent versions explicitly.

### 2. v19i was not actually neutral outside its focus gate
In bank(), handle_enemies() and tribute safety, v19i used `(strength + focus_w()*focus)*1.5*HP` for self. With focus_w=0 this becomes `strength*1.5*HP`, NOT the old `dps()*HP`. dps() includes ability contribution. Thus an off-gate caster can look weaker, changing retreat/bank decisions.

v19n explicitly restores `dps()*HP` when the gate is off. This corroborates [the team's correction](https://github.com/lekemog/BattlecodeConversation/issues/20#issuecomment-6254365291). It does **not** prove the lifecycle resets caused the earlier corner/collision losses, nor explain the separate v18x→v19f regression.

**Test:** differential fixtures: with the gate off, same legal observation/state must yield the same scores and chosen action as v19f; check every affected function, not just focus_w(). Test representative spell cooldowns and champions. With gate on, label this a valuation package, not pure isolated focus addition.

### 3. Sensible safety fixes can remove productive behaviour
v19m lost8–10; the available-support approximation lost87–100 in the faux gauntlet. These do not prove bugs should remain, but do reject “obviously correct therefore stronger”.
- A hard40-gem pursuit cutoff can miss cheap safe kills, fail to clear a blocked route, or leave escorts without coherent assignments.
- Counting every distant ally at half is neither arrival-aware nor reliable; it can reject productive camps without reducing actual danger.
- Timer resets can affect commitment length. Separate death-only reset, successful-completion reset, abandonment reset and carrier-switch reset, then inspect actual changed trajectories.

Keep v19m as reference implementation for Kurian's work, but use v19n as the performance baseline. Do not import the whole losing package without ablation.

## Next-version proposal: Polaris v20 experimental series
No combined deployment until individual changes pass. Suggested names are proposals, not existing versions.

| Concern | Small candidate | Acceptance / diagnostic |
|---|---|---|
| Wrong/stalled action priority | v20a: explicit intent and Acted/DeliberateWait/Blocked/NoAction results; protect delivery while retaining immediate defence | Carrier progresses to tribute; blocked chase falls through; no unintended monster attacks or attack/move starvation |
| Capture-state correctness | v20b: begin/end attempt transitions, one reset family per test | Death→same camp and completion→revisit fixtures; no timeout-ban bypass or repeated abandonment |
| Recall regression | v20c: useful-upgrade/heal recall with bounded travel/tempo cost | Recover strong-map losses without giving back weak-map gains; compare recalled time and purchases |
| Contest opening | v20d: assign feasible middle camps with support arrival and fallback, rather than merely allowing new territory | More completed middle captures and gold by150, without more exposed deaths; partner-required variant is unproven |
| Delivery/convoy | v20e: stable carrier, destination, escort roles; Gather→Travel→Secure→Release with expiries | Submitted gems, lost carried gems and escort opportunity cost; no endless rally |
| Altar detours | v20f: rank reachable legal tribute tiles by time, exposure and interruption risk | Less unnecessary detouring without increased carrier losses; score standing tiles, not altar coordinates |
| Combat estimate | v20g: short-horizon available damage, current HP, arrival, cooldown/range and escape | Fewer costly false commitments without excessive evasions; capture/score throughput remains a gate |
| Stale camp/idle time | bounded replanning on no-progress, explicit visibility/respawn state | Productive-action share and completed captures; no repeated retarget loop |
| Health/item gap | separate affordability, purchase delay, build and farm-income experiments | Spend/power gained per time lost; no blanket frontline build swap |

Use the existing8-byte protocol deliberately; reserve/version fields, establish one writer or deterministic aggregation, and test champion ordering. Do not silently overwrite claims with model state.

## Opponent modelling: yes, but not a global personality switch
The poker analogy is useful: maintain uncertainty about likely behaviour, update from observations, and choose the action with better expected value. It does not mean “label aggressive, then turtle.” Battlecode has spatial objectives, partial visibility, linked teammates and immediate execution costs.

Our current controller already has a decaying shared aggression score and a raid response. Improving this is a refinement, not adding adaptation from zero. Historical v15a/full-model rejection and the present corrections argue against another large bundled switch.

Kurian's corrected future-only model has combined AUC0.76/0.83 at r60/r100; unseen-team0.73/0.83. At r100,p>=0.2 it alerts51 times with39% precision and57% recall. Its per-map seen-in-half signal is0.51 on eight. High AUC does not supply a useful operating threshold, and these results do not support a global automatic switch.

Instead track independent, uncertain signals:
| Observable situation | Bounded response to test | Safeguard |
|---|---|---|
| Repeated visible pressure near our delivery route | Earlier banking, nearer escort or alternate approach | Keep emergency defence; no automatic retreat from the only scoring area |
| Enemy commitment to a distant objective | Take a verified safe local resource window | Missing vision alone is not proof the enemy is absent |
| Contested central camp, support can arrive before engagement | Coordinate arrival/target, else select productive fallback | Do not wait indefinitely for a partner |
| Visible isolated valuable enemy carrier | Bounded intercept by a non-carrier if time/risk justifies it | Our carrier continues delivery; no map-wide chase |
| Low observed pressure with adequate coverage | Preserve farming parallelism | Unseen means unknown, not passive |

Separate fast local danger from slower tendencies. Age evidence; deduplicate correlated teammate sightings; normalize by observation opportunities; use confidence and different enter/exit thresholds to avoid oscillation. Do not infer hostile champion damage solely from HP loss near an enemy.

First run in **shadow mode**: log the proposed action change without taking it. Then compare fixed policy, current aggression policy, one simple situational rule and a learned rule using the same action interface. Model quality matters only if it improves delivered score/wins after reaction costs. No cross-match persistence or replay-only knowledge at runtime.

## Evaluation and tooling before promotion
- A small factual manifest per match: map, side, time, own source/build/submission, opponent team/version if available, outcome/tiebreak; report missing rows.
- Actual game rounds and stable entity IDs; no snapshot-index assumptions. Event-time hit attribution, separated encounters and non-overlapping evaluation windows.
- Submitted-gem events/totals for banking; distinguish transfers/deaths/partial tribute and unfinished bags. Never-bank fractions alongside timing.
- Held-out opponents and fresh map/side cases, plus baseline repeats. All17 maps for regression coverage when feasible; current35-game check covers only a subset.
- Track win/score plus mechanism metrics: useful captures, gold/spend, recall downtime, carrier loss, escort cost, evasion time, fuel/errors.
- Treat lower death count as diagnostic, not victory. Treat faux bots as execution/adversarial screens, not faithful top-100 substitutes.
- Freeze tests on validation/auth/HTTP400 failures; do not label every error quota exhaustion. The failed repeated-contest-map test left an untested arm submitted for over an hour: verify and restore baseline through the designated operator, and mark affected ranked intervals.
- Keep source corrections and observed performance separate. Propose a fix/test for each concern; mark it proposed, locally rejected, ladder-rejected or accepted. None is “solved” merely because code exists.

## Team credit and provenance

Polaris is a shared project by **Ben, Kurian, Leke and Szymon**. Our work spans strategy, replay analysis, implementation and testing. Original commit attribution and AI-assistance provenance are preserved. Shared wording does not imply unanimous endorsement of every hypothesis.

See the [replay-review guide](REPLAY_REVIEW.md) for a common format that turns observations into testable changes.
