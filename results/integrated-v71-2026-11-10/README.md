# v72 integrated strategy: tested, experimental

**Do not promote this bundle yet.** It implements adaptive Heart/Cassi/Issac drafting, local frontline farming, kit roles, economic-area preference and capture/shop changes on v71a. Local early-pack wins improved, but the selected pair compositions still lose too often, and ordinary-turn fuel exhaustion increased. The complete evidence is preserved rather than selecting winning maps after the test.

Latest checked development base: `bots/v71a`, PR81 head `010047f8dba8e06fd5038b3121f262885406ac40`. Rechecked after the suite: PR81 head unchanged. Source freeze: `1c704680d24e316988182867ba5a47066c48f734`. New bot: `bots/cg-v72-integrated/src`. Diagnostic: `bots/cg-v72-core-control/src`. No active submission was verified or changed; CLI account authentication is expired.

## Complete local comparison

**1,536 full release games on 128 maps, both sides**: unchanged v71a and the candidate against each of three opponents. Same map hashes and seeds asserted for each paired baseline/candidate case. CLI5.0.1, actual engine3.0.0; exact build in sourcepins.json. These are local sparring bots, not matches against the current ladder top ten.

| Opponent | v71a wins | Integrated wins | Net | Mean banked margin: baseline → candidate |
|---|---:|---:|---:|---:|
| v71a | 128/256 | 131/256 | +3 | 0.0 → 11.8 |
| v66i | 134/256 | 134/256 | +0 | 24.9 → 32.4 |
| v50p1 | 198/256 | 208/256 | +10 | 367.8 → 379.0 |

The v71a head-to-head is51.2%, a small result. Paired loss-to-win versus win-to-loss flips were64/61 against v71a,57/57 against v66i and33/23 against early-pack v50p1. Deterministic games and two sides of the same map are not independent repeated trials; this is not evidence of a robust ladder gain. The candidate is36/84 on the04 family against v71a, versus42/84 for unchanged v71a.

## Early economy and runtime

Values below are mean team totals per game, except fuel events, which are totals over256 games. Round metrics use the statistics engine's round-indexed cumulative timelines. C&I is one draft pick but two physical heroes.

| Opponent | Gold r100, base → new | Gold r200, base → new | Spent r200, base → new | Deaths r200, base → new | Fuel exhaustion, base → new |
|---|---:|---:|---:|---:|---:|
| v71a | 310.0 → 324.1 | 767.6 → 759.1 | 690.5 → 679.8 | 0.34 → 0.33 | 318 → 359 |
| v66i | 309.6 → 321.6 | 765.3 → 746.8 | 688.0 → 672.3 | 0.32 → 0.33 | 321 → 359 |
| v50p1 | 336.5 → 333.3 | 805.2 → 783.9 | 720.0 → 699.1 | 0.64 → 0.64 | 162 → 729 |

The bundle does **not** solve the overall early-gold deficit: mean r200 gold/spend is lower against all three opponents. Zero bot faults, logged turn errors or rejected pair actions were recorded in all1,568 full games, but that does not mean zero interrupted turns. Candidate fuel exhaustion is1,447 events over768 main games versus801 for the baseline; early (≤r200) events are193 versus178. Only12 candidate main-suite events belonged to Cassi/Issac. The fuel increase therefore cannot simply be blamed on the pair routine.

The largest fuel case is retained-original draft on04gem-caverns, side1 versus early pack:272 events versus42 for the matched baseline. Role counts: Heart6, Ryth92, Marcella69, Vendetta98, Varg7. Side0 is168 versus39. Both candidate cases win, showing why a win-only gate misses the runtime problem. Other large hotspot:02the-pack side0,169 versus35. Profiling these paths is required before promotion.

## Does the new core earn its place?

The opening100x planner completed all256 two-round scans. It chooses Heart + Cassi/Issac on15 maps/30 sides, retaining original v71a picks on113 maps/226 sides. Peak planning cost is1,710,140 fuel,17.12% of the available opening budget. Five-pick maps use two sets; four-pick maps three sets; three-pick maps retain one set. Drafts are determined by map features, not opponent names or random variety. See [DESIGN.md](DESIGN.md) and draft_scan.csv for exact rules and traces.

| Selected-core cohort, same30 map-sides | Baseline wins | Integrated wins | Mean total deaths, base → new |
|---|---:|---:|---:|
| vs v71a | 15/30 | 11/30 | 3.73 → 5.50 |
| vs v66i | 19/30 | 11/30 | 3.37 → 5.33 |
| vs v50p1 | 20/30 | 20/30 | 5.80 → 8.33 |

Against v71a on these same selected map-sides, r100 gold improves484.1 →589.4 (+21.8%) and r200 gold1,286.4 →1,349.7 (+4.9%), but wins fall15 →11, total deaths3.73 →5.50 (+47.3%), and mean banked margin becomes−97. This supports the narrower observation that the opening clear improves while later conversion/survival remains weak. It does not establish the cause of every loss.

**Concrete failure:04sanctum side0 versus v71a.** Candidate banks121 against1,026; matched baseline banks1,000 against546. Cassi deals8,316 monster damage while taking zero monster damage, but earns zero gold and buys no items. Issac earns700 gold; Vendetta1,975; Varg1,140. Cassi and Issac both die to enemy Varg at r462 and lose21 +32 gems. This is direct evidence that protecting Cassi from camps and writing a shop plan does not ensure she gets an item budget or survives enemy contact. Their death positions are six Chebyshev tiles apart. It is a specific failure case, not the entire cohort. Across all30 selected-core games against v71a, mean earned gold is508 for Cassi versus968 for Issac and1,928 for Varg; Cassi averages418 champion damage.

**Next changes indicated by this evidence:** give Cassi a minimum useful item budget before the optional Varg/Vendetta funnel; price item growth, altar access and pair death cost into draft utility; tighten pair/frontline positioning during actual PvP; profile the retained-draft fuel hotspots. These are proposed follow-ups, not changes silently added after the frozen suite. The capture income policy currently prefers nearby Varg/Vendetta over Cassi; its contribution to underfunding requires an isolated ablation.

## Forced-core diagnostic and exclusions

The separate32-game forced-core test on eight preselected maps scores7/16 against v71a and10/16 against v50p1, with mean total deaths10.12/12.25 and pair deaths6.62/7.25. It exercises pair behavior where the adaptive draft often declines it. It is exploratory and is not pooled into qualification. Preliminary mandatory-core pilots/scans were excluded; the source freeze predates all final main/diagnostic results. No map gate was refitted after these results.

Unit/property checks cover caster range/strictly-closer cover, unsafe escape-score invariance, partner TTL, regroup cap, stun immunity and core composition eligibility. The preparation helper also passed a source/map copy-and-hash check with no copied build caches. Batch logs report1,536 main and32 diagnostic replay bundles with zero failed matches. Ordinary-turn fuel remains a failed qualification concern.

## Reproduce and inspect

Use a checkout of this branch and CLI5.0.1. The128 maps are pinned repository snapshots; refreshing server maps failed here, so live-pool freshness is unverified. Full stats assertions check engine3.0.0/build96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd. No ordinary-turn fuel increase is used.

```bash
cambc --version
cambc init --yes /tmp/cg-v72-lab
python results/integrated-v71-2026-11-10/prepare.py /tmp/cg-v72-lab
cd /tmp/cg-v72-lab
c++ -std=c++20 -Wall -Wextra -Werror results/integrated-v71-2026-11-10/test-policy.cpp -o /tmp/cg-policy
/tmp/cg-policy
python results/integrated-v71-2026-11-10/reproduce.py --scan
python results/integrated-v71-2026-11-10/reproduce.py --jobs 8
python results/integrated-v71-2026-11-10/reproduce.py --core-control --jobs 8
python results/integrated-v71-2026-11-10/analyze.py
```

Initialize in a fresh scratch project and use only the128 pinned maps; if init downloads extras, remove the extras from that scratch project. `prepare.py` validates262 source/map hashes and copies source only, preventing reused bot build caches. Toolchain downloads may need a curl-installed WASI SDK33/CMake/Ninja in proxied environments. Native C++ was used for pure model assertions; actual gameplay is the release WASI engine execution.

Evidence: `summary.json` (all results/cohorts); `cases.csv.gz` (all1,568 per-game rows); `families.csv`; `draft_scan.csv`; `draft_summary.json`; `hashes.json` (source/maps/release modules); `sourcepins.json`; `batch-logs.tar.gz` (all final batch logs/manifests); `samples/` (explicitly illustrative full replays and statistics). Run `gzip -dc cases.csv.gz > cases.csv` to inspect rows. Analysis and reproduction scripts are included. Samples intentionally include a core win, a core loss, and the worst fuel case; they are not an unbiased performance sample.

No authenticated top-ten scrim, transformed/unseen-map test or live submission was performed. Keep this as an experimental branch for the next controlled ablations; retain the existing live version.
