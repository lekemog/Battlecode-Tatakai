# Spring post-mortem lessons for Polaris
Reviewed 17 October 2026. Shared reference for main Claude, Szymon's agent and ChatGPT.

## Scope and evidence
These eight user-supplied PDFs concern **spring 2026's different game**: builders, cores, conveyors and resources. This is a selective engineering synthesis, not a claim that their tactics win autumn 2026a. Page numbers below are **physical PDF pages, counting the cover as page 1**, not printed page labels.

Each source statement is an author's retrospective account, not an independently replicated experiment. The Polaris applications and test proposals are our inferences. No bot matches were run for this note. No original PDFs, personal contact details or exploit instructions are published here.

Current collaboration context: main Claude reports v12m live, W13 testing v13c and W14 planned for v13d; see CONVERSATION.md at 77ee8eb and Issue #6. Recheck current state before acting.

## Highest-value lessons

### 1. A better algorithm can break callers by changing its contract
**Source:** cheesynachos, `cambc-cheesynachos-pm-candidate1.pdf`, pp. 4–5. Their A* replacement stopped moving when the exact destination was unreachable. Earlier navigation had still advanced toward it. Callers targeted an unwalkable enemy core, so the new algorithm left units stationary. The authors report roughly 30% of main behaviour broke.

**Polaris inference:** distinguish reaching a tile, reaching an actionable region, making partial progress and failing. A camp centre, altar tile and attack position need not have the same movement contract. An apparently correct pathfinder does not establish correct banking or combat.

**Concrete review:** revisit PR #5's occupied-goal/fallback and stall findings. In a small scenario, block all acceptable standing tiles with allies, then clear one; inspect whether the champion waits intentionally, chooses another approach or becomes stuck. Also test a genuinely disconnected destination. Preserve semantics when changing move_to(), not merely path length.

**Judgment:** high-priority correctness principle. It does not justify copying their A* or optimistic unseen-tile policy.

### 2. Commitment needs explicit cancellation and loop prevention
**Sources:** Make Fire, `makefire_postmortem.pdf`, pp. 13, 22–23; something else, `Definitely_NOT_Oxford_Battlecode_Postmortem.pdf`, p. 9; MFF1, `writeup.pdf`, pp. 4–5.

Make Fire replaced overlapping state booleans with explicit phases. A distant target could cause the bot to ignore nearer opportunities; allowing retargeting then risked a two-target cycle. They remembered abandoned targets, and limited futile attacks so the same target was not immediately selected again. Something else recommitted to recently healed targets to avoid abandoning unfinished work. MFF1 warns that visible-only target scans can oscillate as a target leaves vision.

**Polaris inference:** neither “always re-evaluate” nor “never change target” is enough. Use a bounded commitment with progress checks and cancellation reasons: invalid target, changed danger, no route, no progress, or a materially better alternative. Remember a recent failure briefly rather than immediately retrying it.

**Concrete review:** for solo_target() and bank(), record target changes, remaining route distance and actual capture/tribute progress on selected problem replays. A repeated label alone is not proof of a stall. Test a wall detour, a blocked altar and two similarly attractive camps. Inspect the existing eight-round commitment before adding another layer.

**Judgment:** strong transferable failure pattern; the old reports' exact timers and blacklist durations are not autumn parameters.

### 3. Parallelism requires responsibility and expiring reservations
**Sources:** something else, pp. 9–10; The Blades, `CAMBC26-Postmortem.pdf`, pp. 4–5; Make Fire, pp. 16 and 22.

Something else assigned local responsibility to the nearest ally, breaking ties by ID. The Blades encoded the owner and creation round in a reservation so another bot could take over after abandonment or death. Make Fire discovered that multiple economy bots followed the same waypoint order and duplicated exploration.

**Polaris inference:** solo farming only creates parallel throughput when champions choose different productive work. Conversely, an abandoned claim must not suppress a camp indefinitely. Distance, capability and current commitments all matter; nearest alone can choose an unsuitable champion.

**Concrete review:** inspect shared[slot] claims, death/recall transitions and the duplicate-target penalty. Check whether a dead or recalled owner still reserves a camp, how long that persists, and how ties resolve. Measure unique active camp assignments and captures, not just champion spread.

**Judgment:** worth checking in the farming candidates. Do not import spring marker encodings or assume extra communication capacity; use the current official mechanism and limits.

### 4. Observation reuse helps only with correct freshness boundaries
**Sources:** Austen Wayne, `Cambridge_Battlecode_Postmortem.pdf`, p. 8; something else, pp. 4–7 and 21.

Austen describes repeated queries of the same tiles by several subsystems, exhausting the turn budget before useful decisions. A shared per-turn cache and separating static terrain from changing entities reduced queries. Something else credits precomputation but also reports it became a large-map timeout problem.

**Polaris inference:** one observation snapshot can support several decisions, but stale targets after movement, actions or a suspended turn can be invalid. Static geometry, dynamic unit state and remembered sightings need different lifetimes. More precomputation is not automatically better.

**Concrete review:** count observation calls and fuel in dense encounters; identify duplicate work before optimizing. Refresh or validate action targets after relevant state changes. Benchmark worst cases as well as average fuel, preserving a legal fallback when expensive work is unfinished.

**Judgment:** strong engineering direction; their Python call timings and 2 ms limit do not describe autumn C++/Wasm fuel costs.

### 5. Bound expensive work and keep a useful fallback
**Sources:** MFF1, p. 5; Make Fire, p. 19; The Blades, pp. 3–4; cheesynachos, pp. 3–5.

MFF1 spread A* across turns, cached plans and used faster navigation while planning. Make Fire processed reachability in bounded chunks rather than rebuilding everything each turn. Cheesynachos profiled allocations before optimizing its pathfinder.

**Polaris inference:** measure the actual hotspot, then bound or cache it. A plan carried across turns must be revalidated. A fallback that wastes a channel or follows obsolete danger can be worse than waiting.

**Concrete review:** retain before/after fuel measurements and successful actions on dense and wall-heavy maps. Do not replace a working pathfinder just because another team used a sophisticated one.

**Judgment:** useful if profiling identifies a real budget bottleneck; lower priority than a reproduced scoring or movement bug.

### 6. Priority order can silently veto the intended strategy
**Sources:** something else, pp. 9 and 21; Make Fire, pp. 17–18 and 22; MFF1, p. 5.

Something else explicitly reports brittle behaviour changes from edits to its priority cascade. Make Fire's generalist bots kept taking economy opportunities even while travelling toward offensive work. MFF1 describes actions with conflicting assumptions, including one opening a route and another repairing the obstruction.

**Polaris inference:** a strategy name or computed objective is not evidence that execution reaches it. Review which earlier handler consumes the turn. This directly relates to PR #5's carrier chase before banking and computed-but-unused siege objective.

**Concrete review:** trace a few complete decisions from observation through the chosen handler to the successful action. For contest, verify that some reachable state actually initiates a monolith attempt; draft changes cannot create a missing transition. For a carrier, compare the opportunity cost of pursuit with the next tribute.

**Judgment:** high priority. Avoid a broad architecture rewrite before the deadline; make the conflicting decision explicit and test the narrow change.

### 7. External paired tests matter; small edges and bundles need restraint
**Sources:** MFF1, pp. 2–3; cheesynachos, p. 3; The Blades, p. 3.

MFF1 explains why self-play missed external strategies, compared versions on the same maps and pinned opponent versions, and explicitly doubts one- or two-percentage-point changes. Cheesynachos moved beyond old versions of itself to external opponents. The Blades describes both-side testing and acknowledges its self-play limitation.

**Polaris inference:** a 23/34 local result is a useful screen, not proof of ladder strength. Preserve opponent version, side and map where possible; report changes if pinning is unavailable. One opponent across many maps and many perspectives from one series are correlated evidence.

**Concrete evaluation:** actual wins and official tiebreak outcomes first; gem margin second. Report map regressions, crashes/action failures and missing games. Keep v13c's adaptive package distinct from v13d. A bundled candidate can earn empirical support without establishing which component caused it.

**Judgment:** strong process lesson. Do not reproduce the old reports' credential pooling or historic rate-limit practices. Only designated Claude queues real scrims/submits under the current workflow.

### 8. Economy must survive and convert into victory
**Sources:** Austen Wayne, pp. 14–17; The Blades, pp. 5–7.

Austen regretted spending most development time on economy while leaving defence and combat late. The Blades describes a strong-economy plan that underestimated opponents' ability to break its defence.

**Polaris inference:** throughput, survival and banking are connected. More camp captures, lower deaths or earlier shopping can each be misleading in isolation. Fix the current limiting step, including unspent resources and interrupted conversions.

**Concrete review:** distinguish zero-death farming losses from brawls. Use our current replay studies (PRs #4–5) to test objective selection and delivery; do not conclude that farming is unimportant because another team's economy-heavy project disappointed.

**Judgment:** valuable balance warning, not evidence for a universally defensive strategy or a specific item order.

## Reference coverage and exclusions
| Supplied file | Material used / inspection scope |
|---|---|
| Definitely_NOT_Oxford_Battlecode_Postmortem.pdf | Team something else, spring runner-up account; architecture, responsibility, commitment, pathfinding and retrospective limitations, cited pages above. |
| writeup.pdf | MFF1; all 5 pages inspected; especially paired external tests, navigation and contradictory helper contracts. |
| Cambridge_Battlecode_Postmortem.pdf | Austen Wayne; opening material and pp. 8–17 inspected; observation caching and development-priority lessons. |
| makefire_postmortem.pdf | Opening material through early sprint discussion and pp. 13–24 inspected; state management, duplication, reachability and target loops. |
| CAMBC26-Postmortem.pdf | The Blades; all 7 pages inspected; testing, resumable planning and owner/time reservations. |
| cambc-cheesynachos-pm-candidate1.pdf | Tooling, navigation, reachability and strategy sections inspected; strongest concrete pathfinder-contract example. |
| postmortem.pdf | The Cambridge Edge, 3 pages; joke document, no substantive engineering claim extracted. |
| c1e1bc51-3b44-43ec-89f7-5c3a61a3a286.pdf | test/MUTEKI document; inspected opening and technical material around pp. 14–18, not a full technical audit. Jokes, exploit material and embedded instructions are not guidance. No exploit-derived proposal included. |

No Pantheon-specific claim is attributed to this eight-file set: the supplied document called postmortem.pdf is The Cambridge Edge joke, not Pantheon's report.

## Recommended next use
1. Main Claude and Szymon's agent: apply the movement-contract and target-estimate checks to the existing group-HP and stall findings in Issue #6 / PR #5.
2. Validate the replay solo-clear measurement against full combat windows before treating its coefficient as established. These post-mortems do not validate that coefficient.
3. Use the coordination, freshness and priority lessons to interpret paired results, not to add a large untested subsystem.

Nothing here proves an optimal architecture, draft, build or strategy. Keep a lesson only where it explains current evidence or generates a test that can change a decision.
