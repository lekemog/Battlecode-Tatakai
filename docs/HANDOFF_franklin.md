# Handoff from session admiring-franklin (10 Nov 2026)

Branch `claude/admiring-franklin-y3jf7g` (draft PR #81, stacked on `claude/loving-bell-dmxe0j` / PR #79). Read `docs/HANDOFF_fable.md` first; this
adds what changed today. Live bot: **submission 245 = `bots/v61j`**. Fallback 242 (`bots/v61b`), then 240 (`bots/v53x`).

## State
- Ladder 10 Nov: Tatakai 73rd, 2,087. Top ten 2,501-2,833 (#1 "stellar best girl"). UK teams above us unchanged.
- Panels (pinned; compare only against these labels): UK `uk_i` pins: 240 = 12/45, 242 = 14, 243 = 10, 244 = 11, 245 = 12.
  Top ten `tools/panel/panel_top10b.json`, pins `t10b_240`: 240 = 3/50, 244 = 2, 245 = 2 (deaths 9.5-9.8, kills 0.8-1.0).
- The agent session cannot run `cambc submissions activate N` (blocked by its permission check): a revert needs Leke, or upload the older folder again.

## What is established today
1. **The pinned panel is not paired in practice.** Any code change shifts fuel use and reshuffles games: a version built to be a no-op on
   ordinary maps still changed about 3 of 45 results. Treat +-3 wins on 45 games as noise; use both panels (95 games) and the 256-game mirror.
2. **Our results depend on the map** (`results/map-failures-2026-11-10`): 1,200 ranked games, chi-square 247 on 128 maps. Never won:
   04gem_caverns, 03one_gem, 00collision, 03showdown. Fixed in 245: 04gem_caverns (chooser starved of fuel on 114 groups) and gem-starved
   maps (03one_gem, 03ultrastarvation). Still open: 00swirl (feeding at the enemy-held altar), 02stalactites, 00galaxy, 00collision, 00lanes, 03showdown, 03fan.
3. **01yellow_brick_road is fuel-critical** (28 groups, 160 camps): a few hundred fuel more per choose loses it. Keep new per-group work out of `choose_target`.
4. **Drafts by team size** (in 242+): 3-pick Marcella, Vendetta, Varg; 4-pick Heart, Marcella, Vendetta, Varg; 5-pick unchanged. `draft_mode 99` is
   now literal (`draft_learned false`): the learned weights had silently reordered every earlier draft experiment (v58a-d, the forced comps).
5. **Meta** (3,885 recent ranked games, `tools/playbook/meta_now.py`): 9 of the top 10 draft Cassi & Issac with Heart, plus Vesper or Prism, often
   Willow. Their Vesper takes 48% of team gold. Among comps our code plays, only the small-map ones above beat rating expectation.
6. **Ranged bugs fixed in the v60 line** (not in the live bot, which fields no ranged champion): the attack skipped on a "bad spot", captures never handed to
   the carry, the carry build reordered by learned shop weights. Our Vesper went from 719 to 2,256 gold a game (UK Vespers 4,120); the Vesper
   comp still loses 96-160 to our five in self-play; Cassi & Issac 93-163 (the pair dies 2.5 times a game); Ren for Ryth 57-105.
7. **Fuel overall is not a lever** (double fuel 68-64 over 132 games), but it decides specific maps (points 2 and 3).

## Rejected today (do not repeat without a new idea)
- Three-champion ball all game (55-201); Cassi escorting Issac through the escort code (67-189); caution rising with each own death (114-142, deaths not lower).
- Chooser fuel reserve scaled by group size on every map (243: UK 10/45; alone 3-9 on the six lost maps).
- Opening planned in the 100x draft turn (`bots/v63a`, `plan_opening` in draft.cpp): first hit 2 rounds sooner and +5-9% gold at r50, but 130-126 on one base and
  121-135 on the live base with more deaths (4.12 vs 3.52). Stacked with the altar memory (`v65a`): 118-138. Not uploaded.
- Altar danger memory (`bots/v64a`): 128-128 locally; untested on real opponents (needs 00swirl replays via `--source-group`).

## What I would do next
1. Close the Vesper gap with replays: `an/top` method (download top-six games, `tools/playbook/roles_decoded.py`): their Vesper averages Strength 166 over the first
   600 rounds and is a camp's nearest target 15% of rounds; ranged supports 5-8%. Build "ranged never tanks" and early gold funnel before any other role.
2. Test `v64a` on 00swirl with the stored groups in `results/map-failures-2026-11-10/worst_groups_242.json`.
3. For each remaining worst map, reproduce locally first (04gem_caverns and 03one_gem both reproduced in self-play in minutes).
4. Counter-draft on small maps from the opponent's revealed picks only once there are enough games per comp (now 20-80).

## Tools added
`tools/lab/`: `mir.sh`, `champ_stats.py`, `champ_curve.py`, `trace_summary.py`, `trace_positions.py`, `run_decoded.sh`.
`tools/playbook/`: `fetch_lists.py`, `meta_now.py`, `roles_decoded.py`. `tools/panel/panel_top10b.json`.
