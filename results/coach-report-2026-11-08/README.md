# Coach's report: Tatakai bot, 8 Nov 2026 (engine 3.0.0, patch 4.0.0)

Everything below comes from today's work, which is in this branch.

**Evidence base**
- 4,680 engine-3 matches (drafts and results) from the top 60 teams.
- 410 downloaded replays: 166 top-15 vs top-15 games and our own games, decoded round by round.
- 800 match summaries (shop events).
- Local mirrors: 256 games each, 128 maps x 2 sides.
- Real-opponent panels pinned to ha²t, Gamblr, Valenki and Kratos (40 games per bot).

Facts are marked (measured). Hypotheses are marked (hypothesis).

## Competition rules that shape strategy (from the SDK and GameRules)
- First team to tribute 1,000 gems wins. Gems come from capturing camp groups and are banked at altars; gems carried by a champion are lost when it dies.
- Gold comes from camp pick-ups, kills (~110 including a 50 bounty) and passive income; it buys shards and emblems on spawn.
- Champion turns alternate between teams; **within a team, higher `set_priority` acts first** and a change applies from the next round.
- A dead champion is out ~60 rounds plus the walk back.
- The draft is one pick at a time, so later picks can see the opponent's earlier ones. The first draft turn has **100x fuel** and there are 1,024 bytes of draft memory.
- Per-turn fuel is ~100K: anything heavy must be cheap or precomputed.
- Tournament maps are outside the ladder pool, so map-specific tuning does not transfer.

## The three most consequential weaknesses (before today's fixes)

### 1. We are caught alone and outnumbered, then we feed (positioning, macro)
- (measured) On close and contest maps (spawn walk 60 or less) our largest group in rounds 1-150 is **2.3 champions vs their 3.0**. At contact we are outnumbered **36 rounds per game vs their 12**, and die **1.2 times by r150 vs their 0.4**. On far maps we match them.
- (measured) We enter danger states **~90 times per game vs ~44**, with about **1 ally within 8 vs ~3**. Once in danger we survive as often as they do (death rate 0.18 vs 0.22): the problem is getting into danger, not escaping it.
- (measured) Deaths feed their economy: in earlier studies about a third of the income gap is kill gold and lost bags.
- Root cause: five independent farmers chase their individually best camp and meet the enemy pack piecemeal.

### 2. We start fights and do not finish them (micro, execution)
- (measured) We get more kill chances than top teams (23.8 vs 16.4 per game) and commit more often (71% vs 56%), but convert **15% vs 28%**. Committing does not raise our conversion at all.
- (measured) At a local power ratio of 3x or more, **54%** of our chances end with the target damaged but alive (top teams 31%). The nearest attacker averages 1.6 tiles away, and only a third of the target's health comes off.
- (measured) Our kill rate does not rise with power (17% even at 5x or more); theirs rises from 22% to 39%.
- (measured) Top teams order turns: a champion that can finish an enemy acts first in its team 60% of the time (23% otherwise). We never set priority.
- Root cause: split targets (each champion runs its own simulation), no turn ordering, and damage spread instead of focused.

### 3. We are weaker than our gold allows (economy to power conversion)
- (measured) Stat choice did not match the kits. Ryth, whose bonus health adds strength, bought **Strength 72-91%**; top teams buy her **Health 83-99%**. Marcella bought Strength; top teams buy Focus. After r500 we dropped Health to 7-23% of spend (top teams keep ~35-40%).
- (measured) The fixed draft holds the two weakest top-team picks (Ryth -0.28 log-odds on near maps, strength-controlled) and never uses the funnel the top teams build: Vesper as gold carry (3,300 gold per game), Prism as gem carry (carrying 72% of the time), and grouped supports (Cassi&Issac, Willow, alone only 11-14% of the time).
- Constraint (measured): forcing their compositions or single champions into our code loses badly (16-34%; Ryth to Prism 86-170, Ryth to Cassi&Issac 85-171). Our play code is written for our five. A draft change needs champion-specific play first.

## A. Coach's diagnosis: how we play
Five individually greedy farmers with a strong economic engine: banking discipline, ring/sealed-altar handling, capture handoff. Fights are decided one champion at a time by a local simulation plus a learned danger model that disengages early (live v226). Identity: a farming team that does not group, fight or snowball. It beats mid-ladder teams on economy and loses to teams that group, pick off and convert kills into items.

## B. How the top teams beat us
| what they do | why it works | what we did | change | test |
|---|---|---|---|---|
| Open with a 3-4 champion main group on contest maps; split late, one at a time, on their own half | numbers at first contact win the opening fight, and kill gold funds items | five solo farmers | v53d pack opening (first 3 drafted escort one leader to r100, spawn walk 60 or less) | mirror 129-127 vs v51d (no cost); 143-113 vs live |
| Focus one target and order turns so the finisher acts first | converts chances (28-39% vs our 15-17%) | split targets, fixed order | v53f team focus; v53i turn order | v53f 131-125 vs v53d (+15% kills, -10% deaths); v53i 141-115 vs v53g (+16% kills, -11% deaths) |
| Buy the stat the kit scales with; keep Health all game | more power per gold: their kill rate rises with power, ours did not | heuristic stat choice | v53g kit-aware shop | 151-105 vs v53f (+37% kills, -24% deaths); 135-121 vs live |
| Funnel: gold/gem carries plus grouped supports, draft by map | resources concentrate into one spike | fixed five, no map or opponent reaction | not yet: needs champion-specific play code | draft screen (rejected for now) |
| Read the opponent's picks (counters) | Varg > Marcella +0.43, Ryth > Vendetta +0.32 | draft ignores them | reactive draft among champions we play well | not built |

## C. Roadmap (expected impact, difficulty, confidence)
| # | change | impact | difficulty | confidence | status |
|---|---|---|---|---|---|
| 1 | kit-aware shop (v53g) | high | low | **high: panel 22/40 vs 17/40** | **live (235)** |
| 2 | turn-order priority (v53i) | high | low | medium (mirror +26) | next panel |
| 3 | pack opening (v53d) and team focus (v53f) | medium | low | medium | inside v53g |
| 4 | parameter search (fight margin, danger threshold) | low-medium | low | low until confirmed | running |
| 5 | commit gate from the kill model (commit when predicted kill >= ~0.4) | medium | low | medium | not built |
| 6 | power-spike tempo: fight right after a shop spike, avoid fights while behind in items | medium | medium | hypothesis | not built |
| 7 | reactive counter-draft among playable champions | low-medium | low | hypothesis | not built |
| 8 | funnel economy with champion-specific play (Vesper gold carry, Prism gem carry, supports) | high | high | hypothesis | after the lock |
| 9 | opponent archetype detection (rush vs scaler) with posture switch | medium | medium | hypothesis | not built |
| rejected | kill commitment v53h (123-133; carriers died with full bags); earlier danger threshold 0.15 (50/128); one-champion swaps; neural-network hazard model (no AUC gain: 0.902 vs 0.899) | | | | |

## D. Implemented and tested C++ changes (each behind a `config.h` flag)
- v53d `pack_size`, `pack_max_walk`: pack squad and gate on spawn walk measured from the bot's own spawn field (`brain.cpp`, `knowledge.cpp`).
- v53f `team_focus`: deterministic shared target, ranked by kill pressure over health (`brain.cpp`, `team_focus()`).
- v53g `kit_stats`: Ryth/Prism Health, Marcella Focus, health steps for everyone (`shop.cpp`, `main_stat`).
- v53i `turn_order`: `set_priority` each turn (can finish +1000, contact +300, missing health, melee; draft order out of contact).
- v54m: draft-turn map features and a model hook (`mapfeat.h`, `draft_model.h`). Infrastructure only, not shipped.

## E. Performance report (what was actually tested)
Local (256 games, 0 bot faults in every row):

| bot | vs parent | vs live v226 | kills / deaths vs parent |
|---|---|---|---|
| v51d | | 141-115 | |
| v53d | 129-127 vs v51d | 143-113 | |
| v53f | 131-125 vs v53d | 133-123 | 3.54 / 3.62 vs 3.08 / 4.02 |
| v53g | 151-105 vs v53f | 135-121 | 3.97 / 3.36 vs 2.89 / 4.42 |
| v53i | 141-115 vs v53g | running | 3.86 / 3.78 vs 3.33 / 4.23 |

Real opponents (pinned strong panels; same opponents, maps and sides for every row):

| bot | panel 1 | panel 2 | total | deaths | margin p1 / p2 |
|---|---|---|---|---|---|
| v226 (baseline) | 6/20 | 11/20 | 17/40 | 7.75 | -282 / +76 |
| v51d (234) | 9/20 | 9/20 | 18/40 | 7.6 | -96 / -4 |
| **v53g (235)** | **10/20** | **12/20** | **22/40** | **7.25** | **-82 / +127** |

Limits:
- Mirrors are self-play: they cannot judge drafts and they under-rate caution.
- Panels are 20 games each (about 2 standard errors at +4).
- The top-10 panel has not been rerun on engine 3.

## F. Next iteration
1. Panel v53i: does turn order carry over to real opponents?
2. Commit gate and power-spike tempo (roadmap 5-6), built on the kill model's two dominant factors: local power ratio and target health.
3. After the lock: champion-specific play for a funnel composition, then a learned map/opponent draft over compositions we can actually play.

## Overnight log
- **v53i** (turn order): 151-105 vs v226 locally (kills 3.79/2.91, deaths 3.26/4.05). Submitted as 236 at 06:01. Strong panel 1: 10/20 (v53g 10/20, v226 6/20), margin -56 (v53g -82), deaths 9.8 (v53g 10.0). Panel 2 running.
- **v53j** (commit gate from the kill model, P >= 0.4): rejected. 115-141 vs v53i, 122-134 vs v226; kills 1.94 vs 3.12. The gate removes the sustained pressure that makes kills happen.
- Parameter screen (64 maps x 2 vs v53g; 64/128 is even):
  - fight_margin 0.7: 73
  - fight_margin 0.3: 67
  - hazard_threshold 0.25: 68
  - hazard_threshold 0.15: 50
  - hazard_commit 2: 61
  - escort_until 150: 62
  - pack_size 2: 67
  - pack_size 4: 59
  - tribute_gems_danger 15: 61
  - behind_fight_margin: no effect.
