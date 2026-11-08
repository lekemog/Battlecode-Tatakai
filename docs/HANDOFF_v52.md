# Handoff prompt: finish and ship the combined bot (v52a)

Paste the block below into a new session (Opus). Repo: lekemog/BattlecodeConversation, branch `claude/sharp-hamilton-p1cf39`.

---
You are continuing work on Team Tatakai's Cambridge Battlecode 2026a C++ bot. Goal: UK top six. The version live at lock (~10 Nov, hour unconfirmed) is the one that plays the UK qualifier (~11 Nov), on maps outside the ladder pool. Be honest and efficient; do not decide from sunk cost; explain mechanisms briefly.

## UPDATE (8 Nov, later): v52a FAILED validation
256-game mirrors, 128 maps: v52a vs v51d 100-156 (39.1%); vs live v50h5e 116-140 (45.3%); vs v50p1 162-94 (63.3%) (v51d: 141-115 and 182-74). Income at r400 -3.5% vs v51d. No faults. So v52a is NOT a candidate; v51d remains the best tested bot. Bisect variants (each removes one v52a change, vs v51d on 64 maps): v52x1 guards off, v52x2 patch-4 shop flags off (v51d has p4_shop_cap/p4_capture_time false), v52x3 learned shop on. Rerun them to find the culprit. Ignore the "if v52a >= v51d" wording below unless the bisect repairs it.

Bisect result (64 maps, 128 games each, vs v51d): v52x1 (guards OFF) 68-60 (53.1%); v52x2 (guards on, patch-4 shop flags off) 46-82 (35.9%); v52x3 (guards on, learned shop on) 54-74 (42.2%). Conclusion: the guarded-altar routing + contest guards are what break v52a when stacked on v51d's ring window/detours (about -14 points); the other v52a changes (p4 shop flags, learned shop off) are neutral to slightly positive. v52x1 = v51d + those neutral changes; it was then run vs live and v50p1 on 128 maps (see results/README if added). Do NOT re-enable the guards without re-adapting them to the ring window/detour logic (the user's "formula 1 engine in a mini cooper" point).

v52x1 full result (128 maps, 256 games): vs live 137-119 (53.5%, v51d 141-115); vs v50p1 169-87 (66.0%, v51d 182-74). Zero faults, deaths 4.0. Slightly BELOW v51d though within noise (+-8). Verdict: v51d remains the best tested bot; the combining exercise added nothing. Ship v51d (after the real-opponent panel), and build further ideas as properly integrated changes on top of it.

## Setup (once)
1. Read `CURRENT_STATE.md`, `TESTING.md`, `CLI_FOR_AGENTS.md`, `LIVE_SLOT.md`, `bots/README.md`, `results/README.md`, `results/public-bot-comparison-2026-11-08/README.md`.
2. `pip install cambc==5.0.0` (engine 3.0.0). If the toolchain download fails with UnknownIssuer, curl wasi-sdk-33, CMake 3.31.8, ninja 1.12.1 into `~/.cache/cambc` exactly as in `CLI_FOR_AGENTS.md` section 2.
3. Lab: `tools/lab/setup_lab.sh ~/lab v50h5e v50p1 v51d v52a`, `export PROJ=~/lab`, `MAPLIST` = all 128 maps in `maps/`, `JOBS=4`. Remove any `.cambc` folder in bot dirs before committing.

## State
- Live bot = `bots/v50h5e` (#226). Never modify it.
- Best tested candidate = `bots/v51d` (ring window + detours + tribute cap 40): 141-115 vs live and 182-74 vs v50p1 (128 maps, both sides, engine 3). NOT yet tested vs real opponents.
- `bots/v52a` = v51d plus guarded-altar routing and contest guards (from v51a/b), learned shop off, hand shop plan, Capture emblem timing. Smoke-tested only (beats v50p1 on one map). Its three 256-game mirrors (vs v51d, vs v50h5e, vs v50p1) were running when this session ended; results were not saved. RERUN them:
  `tools/lab/mirror.sh v52a v51d`, `... v52a v50h5e`, `... v52a v50p1`, then `tools/lab/bankstats.py`, `tools/lab/mirror_econ.py`, check bot faults = 0.
- Noise: about +-8 wins at 256 games, +-4.4 at 128. Mirror cannot judge drafts or information sharing; only real-opponent panels can (gate: +4 wins over v226 across the two strong panels, deaths not worse; `TESTING.md` section 5).

## Decision rule
- If v52a >= v51d in the mirrors (no fault, income and banking not worse), v52a is the candidate. Otherwise bisect which ported feature hurts (guard routing, contest guards, learned_shop off, Capture emblem; each is a config flag) and ship the better of v51d / the repaired v52a.
- Then: book a row in `LIVE_SLOT.md`, post on the issue, submit, run the panel, log in `SUBMISSIONS.md`. Keep v226 as the revert target; restore it unless the panel gate passes. Needs `cambc login` approved by a human (link given to the user). Do not submit before the user confirms.
- Lock is imminent: the panel (~90 min) must finish before it. If time is short, say so and recommend based on mirror evidence only, flagging that it is unverified vs real opponents.

## Known facts to keep in mind
- Real top-10 gap (100 games): they collect 1,180 gems vs our 642, bank 999 vs 387, deaths 2.5 vs 10.9, earned gold 7,106 vs 4,232. Deaths feed their income (~a third of the gap). Top teams use a Vesper carry/funnel economy; our draft never picks Vesper.
- `group_news` must stay on (turning it off costs ~11 points). Shared memory is 8 bytes.
- The fuel cliff exists (100K/turn). An idle-throttle optimisation was measured WORSE and dropped; always measure optimisations.
- Priority channel and draft memory were evaluated and not adopted (issue #77).
- Patch 4.0.0 balance changes are already reflected in engine 3.0.0.
- The user's critique: past tests were grafts. When adding an idea, adapt the surrounding code to it, not just bolt it on.

## FULL FEATURE SCOPE (user request: include ALL of these, adapted into the bot, not bolted on)
Build one bot `bots/v53a` from v52a (after v52a validates) that integrates every item below. For each item, read the surrounding code and adapt it to the new behaviour (thresholds, fuel gates, shared-memory use, shop order), keep it behind a `config.h` flag, and test each flag on/off with `tools/lab/mirror.sh` so a bad item can be switched off. Do not judge an item by a single graft test.

A. Already in v52a: v51d ring window, detours, tribute cap 40, danger threshold 20; guarded-altar routing; contest guards (monolith maps); learned shop off; Capture-emblem timing.
B. Tested earlier but left out; re-test properly integrated (v51e1 marcella_focus, v51e2 health_mix, v51f1-f5, v51g1/g2, v51h1-h3 peer channel in knowledge.cpp, v51i1-i3). Known: i2 lost 40.6% (skip unless reworked); h1-h3 ~52-53% (keep only if it helps once integrated; it uses shared-memory bytes that group_news needs; group_news stays on). Read each folder's diff against v51d and the results docs to see what it did.
C. Never built:
   1. Vesper carry economy: draft Vesper, capture relay so others hand her the camps, role-specific shop for her, escorts/protection. Est. +10-15% income.
   2. Survival rework: deaths 10.9 vs 2.5 for top-10; fewer risky fights, retreat/regroup, rescaled health thresholds for patch 4.0.0.
   3. Skirmish emblem (now 10% vs champions) in the fight model; patch 4.0.0 stat changes (Vendetta 900 HP/65 Str, Vesper Str 35, Stellar Focus 85, Prism 90, Marcella 40 Str, Varg 50 Str, Heart Focus 80, Greed 40) reflected in draft scores and shop.
   4. Event-driven idle re-score (re-score only when a respawn timer expires or a group changes state). Earlier fixed-delay throttle was worse; measure.
   5. Line-by-line optimisation of brain.cpp (~4,174 lines): remove redundant work, but MEASURE each change (avg fuel, heavy-turn share, win rate); revert anything that does not help.
   6. Untested leads: pocket entries into hole-ringed gem groups, teleport crystals on wall maps (tp_shortcut_margin), shared kill-zone marks.
D. Ship rule: the final bot must at least match v51d in mirrors (>= 141-115 vs live, >= 182-74 vs v50p1 on 128 maps) with zero faults and no income/banking regression; otherwise submit the best verified one and say which items were dropped and why.

## After shipping (if time remains), in priority order
1. Survival rework (deaths are 4x top teams).
2. Vesper carry economy: capture relay, role-specific shop, protection (est. +10-15% income, unbuilt).
3. Event-driven idle re-score (re-score only when a respawn timer expires or a group changes state).

Report numbers faithfully, including failures. Commit and push to the branch above and keep the draft PR (#70) description current.
---
