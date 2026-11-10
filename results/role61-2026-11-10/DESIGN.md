# Anti-melee carry-role experiment

Hypothesis: the PR81 carry composition is underperforming partly because its combat positioning does not adapt to a coordinated melee dive. Keep the draft and economy fixed to isolate role execution. This experiment tests one concrete controller; it cannot establish that every possible role policy fails or succeeds.

Base source: v60d at PR81 commit 17081c7b8c261e6bec7d78a2915586e697175c0c. New source commit 2c0c37cf0b9dd466a05239decd1f46671998854b. No changes to v60d, v53x, v50p1, PR81 or PR82 source.

| Champion | Role and behavior |
|---|---|
| Heart of Ruin | Bodyguard: stay near visible/recent Vesper, help her camp, cover captures for up to eight consecutive turns; use the area stun dash against a diver inside the carry leash. Existing self-shield logic remains. |
| Vesper Vale | Ranged gold carry: avoid spending a basic attack before necessary escape movement, use defensive dash at close range, value frontline cover, avoid intentional gap-closing in the role handler. Keep the parent capture funnel and carry upgrade plan. |
| Marcella | Durable control and sustained melee damage: converge on the carry's nearest threat; retain kit-aware ranged damage and enhanced-basic handling. |
| Vendetta | Leashed finisher: favor a basic-lethal target close to both herself and Vesper; retain attack resets and kill-reset passive behavior supplied by the engine. |
| Varg | Splash frontline: converge on the same local diver; retain splash attack, area damage and shield handling. |

`cg-role61-kite`: same source with bodyguard and melee-peel flags disabled. Only the Vesper combat behavior is enabled.

`cg-role61`: full controller. Standard fight simulation and hazard veto run before accepting the new positioning handler. Existing emergency retreat, health, banking and farm handlers remain available. Heart's farming assignment can follow Vesper's published camp; other melee farm normally outside local protection range. Both retain the original 60-round opening escort, capture-gold funnel, shop and map selection logic. No map-specific parameters added.

This is a local coordination policy, not a global five-champion permanent formation. Observed carry positions expire after six rounds; dead carries release the guard. Missing vision and recall release protection. Capture cover can re-arm after a normal-policy turn if the same reward remains available; it is not a total eight-round lifetime cap. Retreats share a homeward objective and local losing-fight rule, but there is no atomic teamwide retreat broadcast or guaranteed formation. Camp occupancy and spawn-rate macro remain the parent's existing planner, not a new centralized map-control optimizer. No dynamic draft changes were introduced: Heart, Marcella, Vesper, Vendetta, Varg are held constant.

Smoke tests exposed two problems before freeze: preempting the established fight evaluator caused unsafe commitments, and distant sightings could block productive actions. The frozen version gates the role handler behind accepted fights and returns control when there is no role action. Diagnostic tracing changes fuel consumption; traced smoke outcomes are excluded from the release suite.

Test matrix: three policies × three opponents × 128 pinned repository maps × both sides = 2,304 release games. Opponents are two local melee-heavy bot snapshots (v53x, v50p1) and the parent mixed carry composition (v60d); these are not a freshly downloaded top-ten ladder panel. This is paired map/side testing, not unseen-map qualification. No platform submission or activation.

CLI/SDK 5.0.1; actual embedded engine 3.0.0, build 96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd. `analyze.py` asserts every game's engine/build and paired map hash/seed. Map freshness against the live server was not independently verified. `hashes.json` records source, maps and compiled WASM SHA256.
