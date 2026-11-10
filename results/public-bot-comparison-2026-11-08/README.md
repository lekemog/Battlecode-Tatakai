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
All on v51d, 64 maps x 2 sides = 128 games each against v51d, engine 3.0.0, 0 bot faults.

| Variant | Change | Wins | Gold r100 / r200 / r400 vs v51d | Banked |
|---|---|---|---|---|
| `v51i1` | `gem_value` 3.0 (gold worth 1/3 gem) | 67-61 (52.3%) | -8.2% / -7.4% / -6.6% | 828 |
| `v51i2` | `gem_value` 6.0 (gold worth 1/6 gem) | 52-76 (40.6%) | -18.0% / -21.0% / -22.8% | 785 |
| `v51i3` | `rechoose_every` 4 (was 8) | 64-64 (50.0%) | -1.9% / +0.4% / -0.6% | 832 |

**None of the two public-bot differences transfers.** Lowering the weight of gold in camp value cuts income by 7% (x3) and 22% (x6) and loses at x6: gold buys stats, as source B's own mirror ("gold weights 0.06 / 0.03 / 0 lose") and our old tuning found; our current 1.5 is near the optimum for our bot. Re-scoring every 4 rounds is neutral (50.0%, income unchanged). Their numbers are tuned to their architecture and do not carry over, which is the general lesson of the crawl: copying a parameter from a different bot does not work.

## 7. Correction: these were grafts, not tests of the ideas
Each variant in sections 6 and in `results/team-channels-2026-11-08` changed one setting in a bot whose other code is built for a different design. A loss there shows the graft does not work, not that the idea fails. Diagnosis of the clearest case, the Vesper-first draft with captures funnelled to her (`v51g1`, 128 games vs v51d), per champion:

| | gold | share of team gold | clears | monster damage |
|---|---|---|---|---|
| Vesper (g1) | 1,682 | **30%** (top team: 64-74%) | 13.8 | 18.4k |
| Marcella (g1) | 1,247 | 28% | 14.8 | 21.2k |
| Marcella (v51d, same games) | 1,552 | 33% | 16.1 | 22.2k |

Team gold 5,194 vs 5,638. The funnel did not happen because every champion farms alone and captures its own groups; concentrating gold needs a capture relay (others clear and move on, the carry captures), role-specific shop plans, and protection for the carry. None exists. Conclusions that should therefore be read as "graft failed, integration untested": Vesper draft and capture funnel, Skirmish step (the fight model ignores the +10% champion damage), health mix (thresholds not rescaled), priority-channel sharing (consumers were written for a global channel; the priority channel reaches visible allies only), gem-value changes (the shop and siege models use the same weight). Results that are integrated by nature and stand: learned shop off, bag cap and ring window (v51d), re-score cadence.
