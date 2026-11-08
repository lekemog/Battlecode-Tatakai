# Public bot comparison and wider crawl (8 Nov 2026)

Repository names are not given (`TESTING.md` rule 8); sources are labelled A to H. All third-party and unverified; read as text, nothing run.

## 1. The HBH source does not exist publicly
Source A is HBH's write-up repository: two commits, README and two documents, **no bot code** (checked history and the owner's other repositories are not listable from this session). A code search for their parameter names (`fight_d`, `foc_most`, `entry_hp`, `combo100r28`) found `fight_d` only in source B and a notes file in another repository. So a line-by-line comparison with HBH is impossible; the closest public C++ bot with documented tunables is source B.

## 2. Crawl
GitHub search (15 queries, pushed since 10 Oct): **35 repositories**; 20 not previously read. Read in depth or skimmed: A write-up (HBH, Round of 32 of 830), B a C++ bot with a 100 KB research log (ladder 49% on its latest version), C a systematic team with ~1,500 versions and experiment, findings and engine-mechanics documents, D a C++ pack bot that began as a "copy of a top ladder team's play" reconstructed from replays (live version below its owner's 2,200 goal), E a long-running team bot (ladder ~#182) with per-version notes, F a solo bot (reached #24, research rewrite never validated), G an autonomous-loop bot (rank 124), H a Rust bot with a top-20 census of 1,040 ranked games. Not read: distributed-compute "worker" repositories and browser userscripts (they run code or ask to be installed); about ten small or stale bots (several are our bench opponents). The search API cannot list all repositories, so this is a lower bound.

## 3. Where our bot differs from source B (C++, same game, same engine era)
| Area | Source B (v81) | Ours (v51d) | Their evidence | Action |
|---|---|---|---|---|
| Camp value | `gems + 0.12 x gold` (source H: gold 0.15 early to 0.03 late) | `1.5 x gems + 1.0 x gold`: gold counts about 0.67 of a gem, 5 to 20 times more than they do | gold weights 0.06 / 0.03 / 0 lose in their mirror; higher untested | **test** (v51i1: 3.0, v51i2: 6.0) |
| Target re-score | every 4 rounds ("commitment beats reactivity": every round 20/70; 8 or 12 worse than 4) | every 8 | 4 best | **test** (v51i3) |
| Bank bag | 48 (20 with enemies near); 30 to 70 flat within noise | 25 x learned factor, cap 40 (v51d) | 25 rejected (gold at r300 -2.3 sigma), 35 neutral | no change; do not go below ~30 |
| Learned layers | none for the shop; fight model hand-written | learned shop weights fitted on old games (they drop Monster) | dropping Monster costs gold at r300 -2.2 sigma | switch learned shop off (v51f1: +4 to +6% income, neutral wins) |
| Roster | ranged-leaning: Vesper, Tavi, Willow, Cassi & Issac | melee-leaning: Heart, Ryth, Marcella, Vendetta, Varg | Vesper capture rule off: 29/70 | Vesper-first draft lost in our mirror (34-94, 43-85) |
| Fight stance | trade: start fights near an ally, stay to ~70% health; `fight_d` | chase only within reach (3 melee); leave earlier | top 10 start 41% of engagements and leave at 0.70; fleeing earlier loses (`OUTMATCHED`, `FIT_FIGHT`) | our `limited_chase` already tighter than `fight_d 4`; leave threshold untested |
| Sharing intel in memory | free byte for death spot and help calls: 39/70 vs 43/70 | tested v51h1-h3, `group_news` control | rejected | rejected here too |
| `set_priority` order | fighters first / last: 43 vs 47, 48 vs 47 | not used | neutral | no |
| Opening plan from draft turn | not built (tour planner scored 11/70) | not built | planners lose | no |
| Teleport crystals | kept on wall maps (>=300 gold) | `tp_shortcut_margin 0` (off) | a top-30 team buys ~6 a game on wall and water maps | candidate (untested) |
| Fuel | switches that halve fuel-outs win slightly less; games with 50+ suspended turns won 63% vs 52% | same finding (`results/code-efficiency-2026-11-03`) | fuel is not why games are lost | no |

## 4. Peer findings that match ours (independent confirmation)
- **Income gap is capture count, not reward size** (source C, vs the top 10: "79% from captures, 68 vs 40 clears a game, same ~118 gold per clear", 21% from kills). Ours: 46 vs 59 captures, per-capture reward within 11%.
- **Tribute every ~32 gems** for top teams (C); ours 37 per tribute but 12 tributes vs 33.
- **Items:** top teams build Bruiser everywhere, Marcella on Focus, Monster shards 7-14 a game; **copying the Power build alone lost (5/40)** (C). Our Vesper-first draft and Skirmish step lost the same way.
- **Early gold lead decides games** (B: gold lead at r300 AUC 0.82; 75% wins when ahead vs 23% behind).
- **Deaths:** isolated pick-offs while fleeing; "their teammates join and ours do not" (C); B: 4% of loss deaths are traded.
- **Almost every lever is neutral locally** (B ~70 experiments, D 22 levers in one morning, C hundreds); a learned fight model played far worse than hand rules (C: 19/60 vs 43/60).

## 5. Ideas worth testing that came from the crawl
1. Camp value weights and re-score cadence (v51i1-i3, below).
2. Pocket entries: dash into gem groups ringed by holes, found by watching top replays (D: 11/20 vs 6/20 in the same hour; map-specific). We have no equivalent.
3. Teleport crystals on wall/water maps (B, C).
4. Shared kill-zone marks (C: cut deaths 0.36 to 0.65 a game with gems held; we rejected a grave-memory variant).
5. Fitted death-risk carrier caution (C: `rk1`-`rk3`); partly covered by our hazard model.

## 6. Results of the tests above
(filled in below)
