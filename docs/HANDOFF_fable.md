# Prompt for the next agent: get Team Tatakai into the UK top 8

You are taking over Team Tatakai's C++ bot for Cambridge Battlecode 2026a (cambc 5.0.0, engine 3.0.0).
Repo `lekemog/BattlecodeConversation`, branch `claude/loving-bell-dmxe0j` (draft PR #79; coordination comments go on PR #42).
Your goal is to get us into the **UK top 8 of the qualifier**. Current state: rating about 2,062, 77th globally, **9 UK teams above
us** (BattleCats 2,558, Claudus Maximus 2,332, QS2isLaw 2,284, Rogue Lock Pickers 2,258, bentheboss 2,246, smurphy 2,200,
jianqiao 2,187, DOOMSDAY 2,174, 0xDEADBEEF 2,161). Our bracket simulation (`results/qualifier-seeding-2026-11-09`) puts P(top 8)
at about 12% at 2,090, 31% at 2,150, 58% at 2,200 and 86% at 2,250. We need roughly **+150 rating**: a structurally
stronger bot, not another +2 tweak.

## Read first (in this order)
1. `TESTING.md`, `LIVE_SLOT.md`, `SUBMISSIONS.md` (rules, the live-slot booking, every submission so far).
2. `results/early-game-2026-11-10`, `results/draft-varieties-2026-11-10`, `results/javiops-2026-11-10`,
   `results/online-calib-2026-11-09`, `results/uk-panel-2026-11-08`, `results/playbook-2026-11-08`, `results/ml-2026-11-08`.
3. `bots/v53x` (live, submission 240) and its `src/config.h`: every behaviour is a flagged constant with its evidence.

## What is established (do not re-derive)
- **We lose by dying.** Ranked losses: deaths 7.7 vs 4.2, kills 2.6 vs 7.3. Half the losses are fights where we die 3+ more.
- **Games are decided by round 200.** UK panel, 180 games: ahead on earned gold at r200 we win 44%, behind 12%.
  We are already 98 vs 137 gold at r50 with equal monster damage (809 vs 799). The escorted opening ball is NOT the cause
  (removing it lost 109-147). The cause is still unknown: find it.
- **Our draft is structurally weak.** All five picks are melee (range 1). Over 4,680 top-60 games our five score about 0
  (near maps) and -0.45 log-odds (far maps); Ryth is the worst pick (-0.28) and our deadliest (2.92 deaths a game).
  Top teams play a funnel: a gold carry (Vesper Vale, ~3,300 gold a game), a gem carry (Prism, carrying 20+ gems 72% of
  rounds, rarely dying) and grouped supports (Cassi&Issac, Willow; alone only 11-13% of rounds). Ours are solo farmers,
  alone 31-38% of rounds.
- **Copying their picks without their roles loses badly** (forced comps 40-216, 49-207, 63-193; Ryth->Prism 86-170).
  The play code treats every champion as a melee solo farmer.
- Things that did not move the UK panel (all within +-3 wins of each other, 9-12/45): pack opening, team focus,
  kit-aware shop, turn order, race-end banking, gate bosses, the fuel fix, in-game fight calibration (v55a 10/45).
- Three UK teams have never lost to us in 225 panel games (Claudus Maximus, Rogue Lock Pickers until v55a's single win,
  bentheboss): a strength gap, not a tactics gap.

## The plan I would follow
1. **Roles, then draft (the biggest lever).** Build real role code, then change the draft one swap at a time.
   - Ranged champions attack from max range, step back from melee, and never enter a fight first.
     `bots/v58k` has a first version of the kiting step.
   - A **carry** gets last hits, gems and gold, and banks early.
   - A **support** follows the carry within 2-3 tiles, peels for it and shields or heals it.
   - Read the official kit descriptions in the SDK (`cambc.h`, `enum class champion_draft`) and our kit decoder
     (`src/ctx.cpp`) before writing any per-champion behaviour.
   - The pending self-play results for `v58a`-`v58d` (single swaps on v58k, logged in
     `results/draft-varieties-2026-11-10`) tell you where to start.
2. **Find the r50 gold gap.**
   - Decode a few UK panel replays (`tools/replay/extract5.mjs`, `tools/replay/decode_dir.py`) and compare our first
     100 rounds with theirs, turn by turn: first camp, who gets the last hit, captures, shop, passives (Vesper's bonus gold).
3. **Cut deaths in the first 300 rounds.**
   - `v56c` (early hunt window: isolated, weaker prey, ally near) gave more kills and fewer early deaths locally.
   - `v57a` (rescue an ally in contact below 60%) is under test.
   - Javiops' 150-game dissection (`results/javiops-2026-11-10`) lists the death patterns worth checking against ours.

## How to test (the rules that kept us honest)
- **Local:**
  - Run `export PROJ=/root/lab JOBS=4; tools/lab/mirror.sh CAND BASE` (128 maps x 2 sides; noise about +-8 wins).
  - Do the unseen-map check with `MAPLIST=/root/lab/xmaps.txt` on renamed copies (`x<bot>`).
  - Get kills, deaths and gold with `tools/lab/mirror_kd.py` and `tools/lab/mirror_gold.py`.
  - Self-play understates caution: use it as a no-regression check for fight changes.
- **Real opponents:**
  - Run the UK panel with `tools/lab/panel_run.sh tools/panel/panel_uk.json LABEL VERSION uk_i`. It is 45 games against
    the 9 UK teams above us, with opponent versions pinned, so every candidate plays the same games.
  - Keep a candidate only if it beats the best panel score so far (**v53x: 12/45, deaths 7.49**) with deaths not worse.
  - Also glance at ranked results while a candidate is live (`cambc matches list --team me --kind ranked`).
- **Qualifier maps are unseen.** Never key behaviour on map names. Map features (spawn walk, altar distance, camp HP)
  are fine.

## Hard rules
- **Never submit without the user's (Leke's) explicit approval.**
  - Book `LIVE_SLOT.md` first.
  - Use `tools/lab/submit_wait.sh DIR`, put a submission note at the top of `src/main.cpp`, then run the panel.
  - Revert with `tools/lab/activate_wait.sh 240` unless the candidate passes the panel gate.
  - Log every upload and every revert in `SUBMISSIONS.md`, and post the result on PR #42.
- A teammate (rohi-ds) also uploads. Check `cambc submissions list` and the branches before and after every panel.
- Report numbers faithfully, including failures. No sunk cost: drop an idea when the panel says no.
- Commits end with the session's attribution lines. Never put tokens in chat or files.

## The user
Leke is a first-year student. Honest and efficient; explain with intuition; prompts are sometimes terse, so read between
the lines. They think like a League of Legends player (compositions, roles, power spikes), and that framing is welcome.
Ask for the qualifier submission deadline first: it decides how big a change is safe (roles take days; parameter
changes take hours).
