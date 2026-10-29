# Map-by-map match history audit

313 distinct match IDs recovered from repository data. This covers all matching records in the inspected caches, not a complete lifetime platform export. Engine/version metadata is incomplete for legacy caches. Do not pool cohorts into a current-bot win rate.

| Map | legacy-US-features | legacy-ranked-21oct | v221-top10-28oct | v24z-top4 | v25a-top4 | v25c-top4 |
|---|---:|---:|---:|---:|---:|---:|
| adgato_gemcombat1 | — | — | 0/1 | — | — | — |
| adgato_gemcombat2 | — | — | 0/1 | — | — | — |
| adgato_gemcombat3 | — | — | 0/1 | — | — | — |
| adgato_gemcombat4 | — | — | 0/1 | — | — | — |
| ambush | 3/3 | 3/5 | — | — | — | — |
| anvil | — | — | 0/1 | — | — | — |
| big_world | — | 1/4 | — | — | — | — |
| boss_battle | — | 2/4 | 1/1 | — | — | — |
| broken_curve | — | 2/2 | — | — | — | — |
| collision | 0/5 | 0/2 | 0/2 | — | — | — |
| concentrated_wealth | — | 2/4 | — | — | — | — |
| contest | 0/4 | 1/5 | 0/1 | — | — | — |
| corners | 0/3 | 4/7 | — | — | — | — |
| corridors | — | 2/4 | — | — | — | — |
| crossing | — | — | 0/1 | — | — | — |
| cuts | — | — | 0/2 | — | — | — |
| eight | 2/3 | 4/7 | 0/1 | — | — | — |
| elk_arena | — | 3/5 | — | — | — | — |
| elkring | 1/7 | 1/1 | 0/1 | — | — | — |
| expanse | 2/4 | 1/3 | 0/2 | 0/4 | 0/4 | 0/4 |
| famine | — | — | 0/2 | — | — | — |
| fields | — | — | 0/2 | — | — | — |
| fracture | — | 2/6 | 1/3 | — | — | — |
| fragment | 1/4 | — | 0/1 | — | — | — |
| galaxy | — | — | 0/1 | — | — | — |
| gift_wrapping | — | — | 0/1 | — | — | — |
| gold_rush | — | 0/3 | 0/1 | — | — | — |
| guardians | — | — | 1/2 | — | — | — |
| hooks | — | 1/4 | 0/1 | — | — | — |
| interlock | 2/6 | 3/3 | — | — | — | — |
| islands | — | 3/4 | — | — | — | — |
| lanes | 2/3 | 1/1 | — | 0/4 | 0/4 | 0/4 |
| lost_world | — | — | — | 0/4 | 0/4 | 0/4 |
| monolith | 3/6 | 0/4 | — | — | — | — |
| packs | 5/6 | 1/4 | 0/2 | — | — | — |
| pilgrimage | 4/5 | 3/5 | 0/1 | — | — | — |
| quadrants | — | 3/5 | 0/3 | — | — | — |
| quarry | — | — | 0/1 | — | — | — |
| reverse_spiral | — | 3/3 | 0/2 | — | — | — |
| ribs | — | — | 0/1 | — | — | — |
| rows | 7/7 | 6/7 | 0/2 | 0/4 | 0/4 | 0/4 |
| rushbait_v2 | 0/2 | 2/3 | — | 0/4 | 0/4 | 0/4 |
| shortcut | — | 0/3 | — | — | — | — |
| split | — | 0/2 | — | — | — | — |
| stalactites | — | — | 0/2 | — | — | — |
| stampede | 2/2 | 2/3 | 0/2 | — | — | — |
| starfish | — | 4/5 | — | — | — | — |
| starvation | — | 2/2 | — | — | — | — |
| swirl | 1/3 | 3/4 | — | — | — | — |
| the_farm | — | 1/3 | 0/1 | — | — | — |
| the_line | — | — | 1/1 | — | — | — |
| the_pack | — | — | 0/1 | — | — | — |
| treasure_box | — | — | 1/1 | — | — | — |
| yellow_brick_road | — | 0/3 | — | — | — | — |

Entries are wins / games. US-features records exclude opponent/top-vs-top labels. Exact match IDs are deduplicated, preferring newer cohorts. scrim_cache.json and scrim_cache_v24z.json contain the same 20 IDs and are counted once. Other-team fish caches and third-party top-50 scouting records are excluded. Names are normalized only for display; raw names and identity remain in historical-games.json. Similar names do not establish identical map hashes across patches.

Current v221 top-ten observations: quadrants 0/3; collision, expanse, packs, reverse_spiral, rows, stampede, cuts, famine and fields each 0/2. Fracture is 1/3 and guardians 1/2. These are diagnostic priorities, not statistically established map win rates. Maps with one game cannot be classified reliably.

Legacy persistence: collision is 0/5 and contest 0/4 in the US-features cohort; collision is also 0/2 in each of the recovered old-ranked and current-top-ten cohorts. That recurring signal warrants replay review, while opponent strength and patch changes remain confounders. The old v24z, v25a and v25c top-four cohorts each lost 20/20; this is broad competitive weakness rather than evidence isolating one bad map.

The earlier fixed-five-map 50-game study reported expanse 1/10, lanes 0/10, eight 2/10, rows 3/10, the_pack 4/10. Those prior aggregate figures are separate from the 313 recovered per-game records; their missing per-game source files are not fabricated into this audit.

The live team profile and match-history interface confirm a much larger lifetime history. The interface inspected here exposes match groups and filters, with no team-level map export found; the daily database ZIPs cover all teams and are very large. This report does not claim that its cached sample represents every platform win/loss. A full per-match team export with map hash, bot version, patch, opponent and side is still needed to estimate lifetime map performance.
