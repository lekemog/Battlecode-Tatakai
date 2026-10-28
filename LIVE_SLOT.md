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
| Leke / ChatGPT | deploy pinned v50c (2d93a14) | User requested v50c submission; no scrims | 2026-10-28 13:56 | 2026-10-28 13:58 | ended; v221 selected, compilation pending; fallback v220 |
| Leke / main Claude | panel base219 vs c217 (pinned, 50 games each) | compare v25z (219) with v29e (217) on frozen mid-rank teams | 2026-10-27 12:40 | 2026-10-27 14:30 | ended, live restored to 219 (then Szymon submitted 220) |
