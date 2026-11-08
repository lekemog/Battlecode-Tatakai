# Handoff prompt: finish and ship the combined bot (v52a)

Paste the block below into a new session (Opus). Repo: lekemog/BattlecodeConversation, branch `claude/sharp-hamilton-p1cf39`.

---
You are continuing work on Team Tatakai's Cambridge Battlecode 2026a C++ bot. Goal: UK top six. The version live at lock (~10 Nov, hour unconfirmed) is the one that plays the UK qualifier (~11 Nov), on maps outside the ladder pool. Be honest and efficient; do not decide from sunk cost; explain mechanisms briefly.

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

## After shipping (if time remains), in priority order
1. Survival rework (deaths are 4x top teams).
2. Vesper carry economy: capture relay, role-specific shop, protection (est. +10-15% income, unbuilt).
3. Event-driven idle re-score (re-score only when a respawn timer expires or a group changes state).

Report numbers faithfully, including failures. Commit and push to the branch above and keep the draft PR (#70) description current.
---
