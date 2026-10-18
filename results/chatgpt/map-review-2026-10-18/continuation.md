# Map investigation continuation — 18 October 2026, approximately 10:15 BST

## What changed since PR #14

**55 additional ranked games, all 17 maps, no match-ID overlap with the earlier 65.** This brings the outcome inventory to 120 distinct games. Do not pool their win rates into a current-bot performance claim: the additional games use five platform versions and different opponents. Detailed JSON export for contest `5d0d482c-b719-4f33-8b2f-ac5bbf087e52` returned HTTP429 (retry12s); no new summary or team log was obtained and no replay was watched. The observations below are outcome evidence and static source analysis.

Main advanced while this investigation ran. Review pinned to **88ecc932a788f76697981300e2c34e04eefbf16b**, which adds v17g and `tools/mapstudy.py`. NOTES reports v16v item adoption, v16w siege, v16x/y experiments, then v17g. These statements are secondary evidence until their per-match artifacts are shared.

**Version correction:** the platform submissions page showed **v99 Active** (submission `6e1010af-da98-4c14-8754-ddfb761692ee`), v98 Cancelled, and v101 Waiting/selected next (`856552ee-de00-46db-a2c5-3952d426bf46`). The rendered v99 **bot.cpp** matches v16x after whitespace removal, SHA256 `84242334c1e795104534521d6e426b0cfccfcfd1e858fb206fb3df662cf99fd4`; it does not match v16w/y/17g. This is a controller-only identity check, not an archive/draft/header fingerprint. No source identity claimed for v95/96/97 or v101. Do not relabel v99 games as v17g or credit them to its escort/ward changes.

## Fresh map outcomes, versions separate

| Map | v95 | v96 | v97 | v99 |
|---|---:|---:|---:|---:|
| ambush | 1/1 | 1/1 | — | 1/1 |
| collision | — | 1/2 | 0/1 | 0/2 |
| contest | — | — | 0/1 | 0/1 |
| corners | — | 0/1 | 0/1 | 0/1 |
| eight | — | 0/1 | 0/1 | 0/1 |
| elkring | 0/2 | — | — | — |
| expanse | 0/1 | — | — | — |
| fragment | — | — | — | — |
| interlock | 1/2 | — | — | 1/1 |
| lanes | 1/1 | 2/2 | — | — |
| monolith | 0/1 | 2/3 | — | — |
| packs | 0/2 | 1/1 | — | — |
| pilgrimage | 0/1 | 0/2 | — | 1/1 |
| rows | 1/1 | 1/1 | — | 1/1 |
| rushbait_v2 | — | 0/2 | 1/1 | — |
| stampede | 0/1 | 2/3 | — | 1/1 |
| swirl | 1/2 | 0/1 | — | — |

The other five additional games are v92 versus Kamikaze: interlock/rows/swirl wins, fragment/stampede losses. v92's complete outcome stratum is consequently **22/30**, rather than the old 19/25. New-only totals: v95 **5/15**, v96 **10/20**, v97 **1/5**, v99 **5/10**. None is a paired effect estimate.

**Priorities strengthened by the additional observations:**

- **Corners:** three more losses across v96/97/99, with our scores 828/768/768. Repeated 768 does not prove identical routes: different match duration, opponent and version. Need camp IDs, rejection reasons and banked versus lost/held gems.
- **Eight:** three more losses, 430–1010, 376–1112 and 116–1070. The v99 loss ended r522. The previous v92 72–1008 loss is no longer the only severe example; still no proof of its exact cause.
- **Collision:** only 1/5 additional wins, including both v99 losses (758–1002 at r823; 946–1002 at r862). A late banking opportunity may matter, but final score cannot establish one existed.
- **Contest:** v97 lost 0–800 on gems at r2000; v99 lost 0–1000 at r1100. The latter controller contains the siege plan. This falsifies any claim that adding the plan alone reliably solves contest. Zero tributed is not zero captured: diagnose staging, clear, capture, transport and tribute separately.
- **Rows/ambush/lanes:** 4/4, 3/3 and 3/3 in this added sample, respectively, across versions. Preserve as controls; do not call them solved. Interlock adds 3/4. **Expanse adds a loss**, 922–1020 on v95; retire an unqualified claim that it is always strong.
- **Stampede remains variable:** v99 won 1080–360 at r839; v96 includes a r2000 240–840 loss and wins at r1038/r1396. v92 lost 0–1080 at r536. A single large objective requires a different diagnosis from corners' repeatable small camps.

## Source findings to reproduce, not asserted match causes

Line references below use pinned v16w/v17g controller files; v16x retains the v16w siege logic.

### 1. Siege safety is keyed to one large bag, but captures can split it

v16w `bank()` L793–798 gathers only for **gems>=100**. `play_turn()` L1061–1066 escorts only a visible ally with **gems>=100**, and the escort itself must have zero gems. Gold-only maps initialize in solo mode; the reward path L1096–1099 can bring multiple champions onto the capture region. A 200-gem reward shared among three or more champions gives each less than 100. Then neither siege-specific protection fires for those carriers. With two 100-gem carriers, neither is a bag-less escort. This is a concrete policy coverage gap, not evidence that such a split occurred in the new losses. v17g retains these siege thresholds; its separate >=40 escort explicitly excludes siege maps.

**Reproduce:** 200-gem capture shared by 1/2/3/5/6 units; verify assigned bags, bank decisions and actual escort coverage. Evaluate a narrow objective-delivery policy based on total objective bags and reachable escorts, not simply lowering every banking threshold. Splitting can shorten tribute time and diversify risk, so concentrating the bag is not automatically better.

### 2. Siege bag timer persists across zero-bag periods and death

v16w `bank()` L768 returns immediately at gems<=0. Reset of `bag_since` occurs only later at L798, so zero-bag turns do not reset it. The death branch L979–987 does not reset it either. Example: a first 200-gem bag sets `bag_since=500`; after banking or dying, a new 200-gem bag at r800 sees `800<500+20` false and skips the intended up-to-20-round gathering window. This also exists in v17g. It is a deterministic lifecycle counterexample; no engine reproduction or match frequency measured.

**Reproduce:** obtain bag -> tribute -> zero -> second bag; obtain bag -> die -> respawn -> second bag; include sub-100 bags and win/endgame bypasses. Reset on actual episode boundaries, preserving the existing terminal-score exceptions. This fixes the meaning of the timer; whether longer gathering improves outcomes still needs a paired test.

### 3. Combat and shopping can pre-empt escort coordination

v17g `play_turn()` L1063–1067 invokes enemy handling, banking and shop recall before the escort blocks L1104–1109 and L1118–1123. `handle_enemies()` can return for fight/chase/engage/evade. Thus the non-siege escort condition requires visible enemies, while those same enemies can prevent that code ever executing. A safe bag-less ally with >=180 gold can also recall before reaching escort logic. This is conditional pre-emption, **not** an unreachable escort branch: favourable distant enemies or other fall-throughs can reach it.

**Reproduce:** carrier>=40 with one bag-less ally, nearby enemy in/out of attack range, favourable/unfavourable fight, ally gold179/180, and carrier on a winning tribute. Record the first handled branch and whether the ally actually protects the carrier. Keep emergency retreat above escort. Avoid moving all coordination above combat without testing: that can sacrifice a decisive kill or make escorts follow a doomed carrier.

### 4. Ward placement can take over a champion without a failure budget

v17g L1034–1043 sends the last slot to the large objective while `!herd_warded`, enemies are absent and its bag is zero. This occurs before the normal retreat, shop recall, farming and siege branches. Placement success is the only exit that sets `herd_warded`; no attempt/route timeout exists. An unreachable annulus, repeated placement failure or unavailable placement opportunity can keep returning `to-herd`. This is a new potential loop in a system already vulnerable to early returns. It is **not reproduced** on a real map.

Use fixtures with reachable/unreachable stage tiles, occupied placement cells, depleted/recharging ward, low HP and a successful placement. Bound failed travel/placement and allow productive fallback. Also check who consumes that ward's information: the documented ward expands its owner's vision, and the chosen last slot is not necessarily the squad leader. Do not assume a ward automatically informs every teammate's camp choice.

## Review of the new map-study and paired-test methods

`tools/mapstudy.py` is useful for locating hypotheses, but its labels cannot yet support exact causal narratives:

- It reads every decoded game for the map without filtering actual submission version or ranked/scrim cohort; field `cyc` is printed into rows but not used to stratify. Published percentages are historical decoded-subset descriptions, not current ranked rates.
- Any living champion's positive bag delta is counted as a pickup (`caps`): camp rewards, stolen bags and multiple same-round changes can be conflated. A +22 observation does not identify a single 22-gem camp. Join capture events/group IDs before claiming the opponent took 17–22 such camps.
- A living champion's negative bag delta is treated as a bank and the prior bag as its size. This is a useful proxy under stable snapshots, not verified tribute attribution. Join tribute completion and team score increments; explicitly handle same-round capture+tribute/death+respawn and missing frames.
- `at(400)` substitutes the final frame for shorter games, while first tribute/death counting starts at r11. Report at-risk counts and missing observations; do not compare postgame scores as if both teams were playing at r400.
- `nbank` is an unnormalised count across games with differing durations; use successful tributes per alive champion-round and capture-to-tribute time as well. Small bags can be efficient when altars are near and wasteful when far away.
- Decode failures are silently skipped and their denominators are missing. A lower death count does not establish a pure farming race or rule out bag loss.

`tools/paired.py` improves map/opponent-team matching, but the persisted plan records team IDs and map names, **not both actual submission IDs**, and does not counterbalance side/order. It submits one bot, waits90s and creates live scrims before the next arm; opponent updates or another team submission can still contaminate pairs. This is particularly material while v101 is waiting and v99 remains active. Require match-creation submission IDs for both sides and exclusion reasons before crediting gains.

NOTES reports item package v16v won **10/75 versus 6/75**, with **6–2** discordant outcomes. That is promising pragmatic evidence for the package in that cohort, not proof Jungle or Health individually is best. An exact two-sided sign test on eight discordant pairs is p=0.289, even before accounting for within-series dependence. Likewise do not interpret the local 21/34 of the bundled v17g as identifying which ward/escort/siege component helped. I support testing it; I do not endorse its components as optimal.

## Shared next actions

Main Claude owns all platform slots and submissions. No scrims, builds, bot edits, main updates or deployments were performed by this review. Existing teammate branches and artifacts are untouched.

1. **Contest owner:** trace v99 `5d0d482c-b719-4f33-8b2f-ac5bbf087e52` first. Need stage/first hit/clear/capture/bag split/first tribute/death timings, source identity and per-champion handled branches. Test timer lifecycle and split-bag protection separately.
2. **Eight/collision owner:** trace v99 `ed8a008d-4b2c-4e12-aa87-1ce3ba9e23d0`, `fc4444c8-c34f-4d0f-967a-4a6518176c36` and `90474f66-6d3c-436a-af08-fd2bd1424a15`. For v17g, count how often escort is eligible, reached, pre-empted and successful. Audit ward fallback before promotion.
3. **Corners owner:** trace v99 `1a5fe0e2-7316-4e74-bc96-85ca72184bb8`, matched against v97 `929750d3-2799-441e-9432-7bf603451abc` only as a diagnostic comparison, not a controlled effect. Distinguish camp rejection, transit, productive damage, capture and bag conversion; action rate alone cannot decide which is slow.
4. **Controls:** preserve rows `d37dd2cb-d1f0-4cc7-bf13-d1b9329b723a`, interlock `e1585096-afcf-4f39-9e8b-6d654f78d8a2`, ambush `2eaa711c-5cac-4b0a-a52b-dc9021d198fa`. On stampede measure objective availability and delivery, not aggregate camp counts.

Claim work in Issue #6 with owner, branch, pinned baseline, actual match versions and artifact link. No guessed assignment of teammates. This continuation adds documents/evidence to the existing ChatGPT PR; it is not a merge request for any bot candidate.

## Reproduction

`continuation-source-series.json` preserves 11 observed series texts/links. `continuation-evidence.json` uses the existing PR parser and includes 55 unique games plus version/map aggregates. Parse using `summarize(series, series)` (each observation includes its label), check disjoint IDs against `evidence.json`, and aggregate by actual platform version. All five games in each series and all available score/winner orientations were validated. Missing opponent versions stay null. Browser times are relative source labels; the report time is approximate BST, not the container clock.
