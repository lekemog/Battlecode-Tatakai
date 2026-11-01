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
| Leke / main Claude | strong-opponent panel (ha²t, Gamblr, Valenki, Kratos; 20 games per run): baseline v223 first, then candidates one at a time (each is live during its own run) | test candidates against the teams that beat us | 2026-11-01 13:20 | 2026-11-01 20:00 | ended: v226 (v50h5e) made live at 20:00 UTC after two strong panels; revert target v223 |
| Leke / main Claude | pinned panel run for candidate v223 (v50e1, Prospector opener) vs the same frozen teams as the v222 baseline; v223 is live during the run | candidate test | 2026-11-01 04:55 | 2026-11-01 06:10 | ended: v223 won the panel (35/45 vs 32/45); v223 stays live, revert target v222 |
| Leke / main Claude | pinned panel baseline: v222 (v50d) vs ten frozen mid-rank teams (50 games); live bot unchanged | baseline for candidate v50e1 | 2026-11-01 04:35 | 2026-11-01 04:30 | ended: baseline done (v222 32/45 wins) |
| Leke / main Claude | submit v50d (v50c + sealed-altar breach) as the lock-night bot; no scrims | ladder locks at midnight UK; fixes zero-deposit games on altar-ringed maps (issue #45) | 2026-10-31 23:11 | 2026-10-31 23:22 | ended: v222 active at 23:21 UTC; revert target v221 (`cambc submissions activate 221`) |
| Leke / main Claude | panel base219 vs c217 (pinned, 50 games each) | compare v25z (219) with v29e (217) on frozen mid-rank teams | 2026-10-27 12:40 | 2026-10-27 14:30 | ended, live restored to 219 (then Szymon submitted 220) |
