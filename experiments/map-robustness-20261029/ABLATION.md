# Exploratory learned-layer ablation

This follow-up was specified after initial benchmark saturation was observed. It is not a new untouched confirmatory holdout. Only cfg::learned changes from 1 to 0; the separate death-hazard model remains enabled. Disabling learned adjustments also changes compute cost, so differences cannot uniquely identify statistical overfitting. No weights were retrained or searched.

| Slice | Games | Learned off wins | v50c wins | Improved cases | Regressed cases | Mean gem-margin delta |
|---|---:|---:|---:|---:|---:|---:|
| all | 560 | 456 | 485 | 21 | 50 | -61.94 |
| old_layouts | 320 | 258 | 278 | 11 | 31 | -57.41 |
| new_layouts | 240 | 198 | 207 | 10 | 19 | -67.98 |
| h_mohnish | 140 | 138 | 137 | 2 | 1 | -16.64 |
| v50c | 140 | 39 | 70 | 17 | 48 | -205.59 |
| x_daniel8 | 140 | 139 | 139 | 1 | 1 | -8.97 |
| x_de41h4 | 140 | 140 | 139 | 1 | 0 | -16.55 |

## Per-map comparison

Each row contains eight cases: four opponents, both sides.

| Map | Learned off wins | Baseline wins | Net |
|---|---:|---:|---:|
| adgato_gemcombat1 | 6/8 | 7/8 | -1 |
| adgato_gemcombat2 | 6/8 | 7/8 | -1 |
| adgato_gemcombat3 | 8/8 | 7/8 | +1 |
| adgato_gemcombat4 | 6/8 | 7/8 | -1 |
| adgato_gemcombat5 | 8/8 | 7/8 | +1 |
| ambush | 6/8 | 7/8 | -1 |
| anvil | 6/8 | 7/8 | -1 |
| arena | 6/8 | 7/8 | -1 |
| big_world | 7/8 | 7/8 | +0 |
| boss_battle | 6/8 | 7/8 | -1 |
| breadcrumbs | 8/8 | 6/8 | +2 |
| broken_curve | 7/8 | 7/8 | +0 |
| collision | 7/8 | 7/8 | +0 |
| concentrated_wealth | 8/8 | 7/8 | +1 |
| contest | 7/8 | 7/8 | +0 |
| corners | 7/8 | 7/8 | +0 |
| corridors | 6/8 | 7/8 | -1 |
| crater | 7/8 | 7/8 | +0 |
| crossing | 7/8 | 7/8 | +0 |
| cuts | 7/8 | 7/8 | +0 |
| dunes | 7/8 | 7/8 | +0 |
| eight | 6/8 | 7/8 | -1 |
| elk_arena | 6/8 | 7/8 | -1 |
| elkring | 6/8 | 7/8 | -1 |
| expanse | 7/8 | 7/8 | +0 |
| famine | 6/8 | 7/8 | -1 |
| fields | 6/8 | 7/8 | -1 |
| fracture | 8/8 | 7/8 | +1 |
| fragment | 7/8 | 7/8 | +0 |
| galaxy | 6/8 | 7/8 | -1 |
| gem_fields | 6/8 | 7/8 | -1 |
| gemfight | 6/8 | 7/8 | -1 |
| geodes | 6/8 | 7/8 | -1 |
| gift_wrapping | 7/8 | 6/8 | +1 |
| gold_rush | 7/8 | 7/8 | +0 |
| great_wall | 6/8 | 7/8 | -1 |
| guardians | 7/8 | 7/8 | +0 |
| harvest | 7/8 | 7/8 | +0 |
| hooks | 7/8 | 7/8 | +0 |
| interlock | 6/8 | 7/8 | -1 |
| islands | 6/8 | 7/8 | -1 |
| lanes | 4/8 | 5/8 | -1 |
| lost_world | 7/8 | 7/8 | +0 |
| monolith | 6/8 | 7/8 | -1 |
| oasis | 6/8 | 7/8 | -1 |
| packs | 7/8 | 7/8 | +0 |
| pilgrimage | 7/8 | 7/8 | +0 |
| quadrants | 7/8 | 7/8 | +0 |
| quarry | 6/8 | 7/8 | -1 |
| reverse_spiral | 7/8 | 7/8 | +0 |
| ribs | 7/8 | 7/8 | +0 |
| road_of_riches | 7/8 | 7/8 | +0 |
| rows | 6/8 | 7/8 | -1 |
| rushbait_v2 | 6/8 | 7/8 | -1 |
| shortcut | 6/8 | 7/8 | -1 |
| split | 6/8 | 7/8 | -1 |
| stalactites | 7/8 | 7/8 | +0 |
| stampede | 6/8 | 7/8 | -1 |
| starfish | 6/8 | 7/8 | -1 |
| starvation | 7/8 | 7/8 | +0 |
| swirl | 6/8 | 7/8 | -1 |
| tangle | 6/8 | 7/8 | -1 |
| the_farm | 6/8 | 7/8 | -1 |
| the_line | 6/8 | 7/8 | -1 |
| the_pack | 8/8 | 6/8 | +2 |
| the_pond | 6/8 | 7/8 | -1 |
| treasure_box | 6/8 | 7/8 | -1 |
| uncharted_lands | 6/8 | 7/8 | -1 |
| vault | 7/8 | 7/8 | +0 |
| yellow_brick_road | 6/8 | 7/8 | -1 |

All 560 cases have matched map hashes, default engine seeds, opponent and side. Results supplement the original 2,800-game experiment. Disabling the learned adjustments loses 29 net wins and reduces average gem margin by 61.94; retain the layer. Regression appears on both old and added layouts. This is evidence against this removal, not proof the existing model is free of overfitting. Stronger opponents and fresh seeds are still needed.
