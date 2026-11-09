# Live slot: who is testing on the ladder right now

Scrims (unranked match groups) and the pinned panel always play **whichever version is live**, and the team shares
about 30 unranked groups per hour. If two people submit or scrim at once, both tests are corrupted. Anyone may submit
and run tests, but announce it here first.

## Rules
1. **Before** you submit, activate a version, or create match groups: read the table below. If someone else has an
   open window, wait until it ends or ask them.
2. **Open a window** by adding a row (who, what version, why, start UTC, expected end UTC) and pushing it to the
   branch you work on AND commenting on PR #42 or the issue you use for coordination. A panel run
   (`tools/panel`, 10 groups, 50 games) needs about 60-90 minutes.
3. **Close the window** when done: restore the previous live version with `cambc submissions activate N`
   (`cambc submissions list` shows which version is live and who uploaded it), then mark the row ended.
4. **No window open:** you may submit. Log every submission in `SUBMISSIONS.md` with a one-line reason and the
   evidence, and say which version is the revert target.
5. Prefer `cambc submissions activate N` to re-uploading when the version already exists.

## Windows (newest first)
| Who | What | Why | Start (UTC) | End (UTC) | Status |
|---|---|---|---|---|---|
| Leke / Claude (session loving-bell) | Submit v53x (r5 + race-end banking + gate bosses + fuel fix), Leke approved; UK panel pinned to uk_i; keep only if it beats r5's 10/45 with deaths not worse, else reactivate 239 (r5) | candidate built on rohi-ds's r5 | 2026-11-09 04:00 | 2026-11-09 04:40 | open; revert target 239 |
| Leke / Claude (session loving-bell) | UK panel on the live teammate version 239 (r5), pinned to the uk_i baseline; no submission | compare r5 with v53i 9/45 and v53t 11/45 on the same games | 2026-11-09 03:20 | 2026-11-09 03:50 | ended: r5 (239) UK panel 10/45 (v53i 9, v53s 9, v53t 11); live stays 239 |
| Leke / Claude (session loving-bell) | UK panel tests of v53s (race-end banking) and v53t (+ gate bosses), each submitted and pinned to the uk_i baseline; Leke approved | best over v53i's 9/45 (deaths not worse) stays live, else 236 | 2026-11-08 17:43 | 2026-11-08 18:15 | ended: UK panel v53s 9/45, v53t 11/45 (v53i 9/45); v238 (v53t) stays live |
| Leke / Claude (session loving-bell) | UK panel baseline (new `tools/panel/panel_uk.json`: the 9 UK teams above us, 45 games) with v53i (236) live; no submission | benchmark for all further candidates (Leke: benchmark against the UK teams ahead of us) | 2026-11-08 11:00 | 2026-11-08 11:45 | ended: v53i UK baseline 9/45 |
| Leke / Claude (session loving-bell, overnight on Leke's instruction) | Panel v53i (v53g + turn order; 151-105 vs v226, 141-115 vs v53g locally) on the pinned strong panels; keep only if it beats v53g's 22/40 with deaths not worse | iterate overnight | 2026-11-08 06:01 | 2026-11-08 06:16 | ended: v236 (v53i) strong panels 27/40 (10 + 17) vs v53g 22/40, v226 17/40; deaths 6.8. v236 stays live |
| Leke / Claude (session loving-bell) | Submit v53g (pack opening + team focus + kit-aware shop) as the live bot (user: submit if it beats the live bot locally: 135-121 vs v226); then the pinned strong panels against the s8base / s8base2 baselines for real-opponent numbers | user decision; panel result reported | 2026-11-08 05:42 | 2026-11-08 05:55 | v53g strong panels done: 22/40 vs v226 17/40 (10 vs 6, 12 vs 11), deaths 7.25 vs 7.75: passes the gate, v235 stays live. Overnight: Claude keeps iterating (Leke's instruction) and may panel further candidates; each will be logged here |
| Leke / Claude (session loving-bell) | Strong panels (panel_strong + panel_strong2, 40 games each run): fresh engine-3 baseline v226 first, then candidate v51d pinned to the same opponent versions; v51d is live during its runs | first real-opponent test of v51d (141-115 vs v226 in the 256-game mirror) before the UK lock | 2026-11-08 03:05 | 2026-11-08 04:51 | ended 04:51 UTC: v234 (v51d) strong panels 18/40 vs v226 17/40 (panel 1 9 vs 6, panel 2 9 vs 11; deaths 7.6 vs 7.75): below the +4 gate; v226 restored. v53d panel not run (awaiting approval) |
| Leke / Claude (session sharp-hamilton) | TOP-10 panel for candidate v51b (bag cap 40, guarded-altar routing/rally, contest altar guards; PR #70), pinned to the t10_226 opponent versions; v51b is live during its run | test the top-ten bank-habit fix against the real top ten | 2026-11-03 16:53 | 2026-11-03 18:53 | ended 17:21 UTC: v233 (v51b) top-10 panel 5 vs 4 wins (v226), zero-bank 3 vs 5, banked 393 vs 382, deaths 11.3 vs 10.4; below the +4 gate; v226 restored |
| Leke / main Claude | TOP-10 panel for altar-guard candidates v50k1 (1 guard) and v50k2 (2 guards), pinned to the t10_226 opponent versions; each is live during its run (about 10 min) | test the altar-guard idea seen in the top-10 replays | 2026-11-02 21:30 | 2026-11-03 06:00 | ended 2026-11-03 ~05:00 UTC by the user: v232 (v50k3) was live ~7h, ranked 52/105 (50%); panel not completed; v226 restored. Candidates: v50k3 and v50k4 (guard at our own altar); v226 restored after each run; restore target v226 |
| Leke / main Claude | TOP-10 panel (Fish, Mite, Univardisty of Shingtonwash, Ad Astra, newer team, NEETCoders, print dont int, German Empire, Noobot, test4; 5 maps each): baseline v226 first, then candidate v50j1 (grave memory + regroup + contest cohesion) pinned to the same opponent versions | test candidate against the current top 10 | 2026-11-02 20:30 | 2026-11-02 23:59 | ended 20:51 UTC: v50j1 (229) did not beat v226 on the top-10 panel (3 vs 4 wins, deaths 10.6 vs 10.4); v226 restored |
| Leke / main Claude | strong-opponent panel (ha²t, Gamblr, Valenki, Kratos; 20 games per run): baseline v223 first, then candidates one at a time (each is live during its own run) | test candidates against the teams that beat us | 2026-11-01 13:20 | 2026-11-01 20:00 | ended: v226 (v50h5e) made live at 20:00 UTC after two strong panels; revert target v223 |
| Leke / main Claude | pinned panel run for candidate v223 (v50e1, Prospector opener) vs the same frozen teams as the v222 baseline; v223 is live during the run | candidate test | 2026-11-01 04:55 | 2026-11-01 06:10 | ended: v223 won the panel (35/45 vs 32/45); v223 stays live, revert target v222 |
| Leke / main Claude | pinned panel baseline: v222 (v50d) vs ten frozen mid-rank teams (50 games); live bot unchanged | baseline for candidate v50e1 | 2026-11-01 04:35 | 2026-11-01 04:30 | ended: baseline done (v222 32/45 wins) |
| Leke / main Claude | submit v50d (v50c + sealed-altar breach) as the lock-night bot; no scrims | ladder locks at midnight UK; fixes zero-deposit games on altar-ringed maps (issue #45) | 2026-10-31 23:11 | 2026-10-31 23:22 | ended: v222 active at 23:21 UTC; revert target v221 (`cambc submissions activate 221`) |
| Leke / main Claude | panel base219 vs c217 (pinned, 50 games each) | compare v25z (219) with v29e (217) on frozen mid-rank teams | 2026-10-27 12:40 | 2026-10-27 14:30 | ended, live restored to 219 (then Szymon submitted 220) |
