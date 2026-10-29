# Adaptability and public-code review

## Current v50c source

Reviewed parent `2d93a142df388db48596f82842cf7cca47809cec`, especially world.cpp, draft.cpp, knowledge.cpp, learn.cpp, brain.cpp and config.h. The candidate source hashes are recorded separately.

- Geometry and camp health/strength/range are read from SDK metadata. Fields and group arrays use actual map dimensions/counts. The old v25m report's wrong-golem-stat and exact-map-fingerprint criticisms should not be automatically attributed to this source. No exact width/height map-selector branches were found in this v50c source search.
- Drafting has team-size and camp-clustering features, with a configured preference mode. This is feature-based adaptation, although the active fixed preference and learned coefficients still need validation across map families.
- Ring banking caches a single spawn-origin open path. A carrier can be elsewhere when banking becomes necessary. The isolated experiment starts from that carrier's route position and refreshes a completed plan every 16 rounds. It is a hypothesis about route relevance, not a demonstrated cure for the Trzy loss.
- A four-slot health ring without stamps can use stale samples after observation gaps. The history candidate corrects validity and resets state on death; targeted tests passed previously. This alone does not imply stronger play.
- The smaller-danger-bag experiment changes the existing legal enemy-memory condition from disabled to a 10-gem threshold. This is a policy experiment, not a confirmed bug fix; no threshold search was performed.
- Shared target IDs use six payload bits: group 64 aliases group 0 and group 63 becomes the no-group sentinel. No captured group IDs >=63 were found in the sampled baseline summaries. This is a concrete capacity constraint for larger future maps, not an established cause of current losses. Do not claim an arbitrary-size map guarantee.
- The learned coefficient arrays are frozen. Their dynamic inputs do not establish out-of-sample validity, and this source folder does not supply a full training/validation provenance manifest. Record map hashes, opponent sets, engine builds and validation exclusions whenever retraining.

## Public repositories inspected

1. [Scr1pting/cambridge-battlecode-26](https://github.com/Scr1pting/cambridge-battlecode-26), including `bots/starter/game_map/a_star_walk.py`, `gossip/codecs/harvester_claim.py` and `test.sh` on master. The pathfinder tracks interrupted searches, retains partial anchors and adapts its search heuristic; generation counters distinguish current work from stale state. Its claim codec separates an owner tag and epoch from location. These are useful original design directions for bounded path work and expiring coordination. Its two-sided map/seed test script is useful structurally, but skips runs with missing winner lines before forming its denominator: our harness must retain failures and expected counts. Its 6-bit coordinate packing is tied to that earlier game's map bounds and must not be transplanted into our larger maps.
2. [Coook13/cambridge-battlecode-bot](https://github.com/Coook13/cambridge-battlecode-bot), README and `bots/v97_no1_switch600/main.py`. The source routes exact width/height/core coordinates to specialist implementations and provides an unknown-map fallback. This is a useful counterexample: a strong local selector is not evidence it transfers. Prefer generic topology/camp features and test the fallback separately instead of adding our own coordinate table.
3. [Temoffy/CamBattlecode26OpenSource](https://github.com/Temoffy/CamBattlecode26OpenSource), repository/index review. It is an open collection with sparse top-level evidence; no strength or compatibility claim was established from the index. The code directory could not be retrieved through the web reader in this pass. Do not treat repository availability as measured opponent strength.

The first two repositories target the earlier mining/conveyor game, not this gem/champion engine. They are architecture references; none of their implementations was copied into the candidates or presented as a current-season opponent. Existing frozen C++ opponents were recovered from our own repository benchmark.

## Evidence rules

Keep map coverage, opponent difficulty, engine version and bot version separate. The 40-map old benchmark and 70-map active pool share 40 byte-identical layouts (14 have name punctuation differences); 30 layouts were missing from the old pool. Those are transfer tests outside that benchmark, not guaranteed research-naive maps: some appeared in the prior online-loss study. The map/hash split is frozen for this experiment, but historical baseline tuning may already have used old maps and opponents.

Use paired cases, include failures, compare equal completed sets and show per-map regressions. A combination is its own experiment; an improvement in separate parts need not survive combination. Small win-count changes on saturated opponents or deterministic seeds are insufficient for deployment. New-map transfer and withheld-opponent results help detect fragility but do not prove an absence of overfitting.
