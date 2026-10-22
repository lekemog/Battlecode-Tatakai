# #40 follow-ups: contestrecall bench, and does the recall rule generalise? (Kurians' Claude, 22 Oct)

## Limits of this environment
- `2026a.battlecode.co.uk` is blocked by this container's network policy. So: no `cambc maps pull`, no ranked match list, no replay download.
- **Maps:** only the 21 maps in `maps2/` (the 40-map `pool6` isn't in the repo), plus `maps/p_df22…` for rushbait_v2. Totals are **not comparable to the 458/560 reference**. Compare contestrecall and spawnfix with each other only.
- **Ranked low-HP episodes can't be measured here**, because the replays can't be fetched. The recall study below uses local games instead.
- Engine 1.0.3 (cambc 3.0.5) throughout.

## 1. Bench: kurians-t3-contestrecall vs kurians-t3-spawnfix (live v191)
21 maps × 2 sides × 7 bench opponents = 294 games each, `bench/gauntlet.py` + `bench/permap.py`.

| Bot | Wins | Margin (sum over 7 opponents) |
|---|---|---|
| kurians-t3-contestrecall | **243/294** | +3264 |
| kurians-t3-spawnfix (live) | 242/294 | +3263 |

- Per-opponent results are identical except x_daniel8 (+1) and h_mohnish (margin +19).
- Per map, every map has the same losses except **contest: 1 vs 2**. That's expected: the rule only fires on the contest fingerprint.
- **Pass rule:** not below the live bot, no per-map regression. It passes on this 21-map subset.

## 2. Does the 9-tile recall rule generalise beyond contest? (local)
**Method**
- Two study-only bots (never to be submitted):
  - `bots/kurians-lh-spawnfix` = live bot.
  - `bots/kurians-lh-recallall` = live bot + contestrecall's rule on **every** map (low-HP and shop recalls need no visible enemy within max(range+2/3, 9)).
- Both print one `LH round slot alive hp maxhp recalling onspawn nearest_enemy` line per turn. `tools/lhstudy.py` rebuilds the episodes with `tools/lowhp.py`'s definitions.
- Maps: lanes, rushbait_v2, eight, plus contest as a check. lost_world isn't in the repo.
- 7 bench opponents × 2 sides = 14 games per map per bot.
- Raw output: `results/kurians/recall-generalise-local.txt`.

| Maps | Bot | Wins | Margin/game | Deaths/game | r150-600: died-while-recalling / recall attempts | r600+: same |
|---|---|---|---|---|---|---|
| lanes+rushbait+eight | spawnfix | 34/42 | +422 | 12.5 | 12/506 (2%) | 10/453 (2%) |
| lanes+rushbait+eight | recallall | 32/42 | +362 | 13.3 | 5/449 (1%) | 2/385 (1%) |
| contest | spawnfix | 13/14 | +786 | 17.4 | 3/39 (8%) | 11/160 (7%) |
| contest | recallall (= contestrecall there) | 13/14 | +786 | 16.1 | 6/69 (9%) | 6/153 (4%) |

**Findings**
- **The local bench can't reproduce the ranked problem.** Bench opponents almost never interrupt our recalls: 1-4% of attempts die while recalling, vs **25-45%** in ranked (#40 episode study). The rule's target is barely present locally.
- **Where it acts, it does what it should:** deaths while recalling on non-contest maps fall from 22 to 7, and completion rises from 90-91% to 94-95%.
- **But nothing improves overall on the non-contest maps:**
  - Episode death rates are the same (34-42% vs 35-41%).
  - Total deaths rise slightly (13.3 vs 12.5 per game).
  - Results: 2 fewer wins and −60 margin per game.
  - The cost is mostly on **eight**: deaths 16.7 → 19.0, margin +448 → +335, 10 vs 11 wins.
  - The saved recall deaths reappear as "died otherwise". Kurians' fallback concern shows up here, whereas on contest locally it didn't.
- **Contest check:** recall deaths r600+ 11 → 6 and total deaths 17.4 → 16.1, the same direction as Kurians' earlier local contest result (49 → 36).

**Conclusion:** there is no local evidence that the rule generalises, and there is a hint of harm on eight (14 games, so possibly noise). Recommendation:
- Keep it contest-only (kurians-t3-contestrecall) for the staged test after spawnfix's ~40 ranked games.
- A general version needs the ranked per-map episode numbers first (lanes / lost_world / rushbait). Someone with API access can produce them with `tools/t3fetch.py` + `tools/lowhp.py`.
