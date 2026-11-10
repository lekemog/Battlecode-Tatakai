# Playbook study: champions, duos, roles, counters, shop, maps (8 Nov 2026, engine 3.0.0)

Data:
- 4,680 engine-3 matches from the last 100 matches of each of the top 60 teams. Drafts and results only: `tools/playbook/drafts.py`, `matchups.py`.
- Decoded replays: 166 top-15 vs top-15 games and our 40 strong-panel games (`tools/playbook/roles.py`).
- 800 match summaries for the shop (pending).

Map band: spawn walk measured by our bot (`~/lab/probe/walk.txt`). *Near* is 60 steps or less (81 maps), *far* is over 60.

## 1. Champion value (log-odds of winning, controlled for each team's strength; pairs and teams L2-regularised)
| champion | near | far | pick share near / far |
|---|---|---|---|
| Prism | **+0.41** | **+0.34** | 14% / 16% |
| Cassi&Issac | +0.25 | +0.17 | 34% / 46% |
| Vendetta | +0.27 | -0.04 | 59% / 78% |
| Varg | +0.26 | +0.07 | 19% / 24% |
| Vesper | 0.00 | +0.18 | 63% / 68% |
| Marcella | -0.01 | -0.23 | 84% / 83% |
| Heart | -0.21 | +0.08 | 64% / 72% |
| Ryth | **-0.28** | -0.13 | 38% / 47% |
| Tavi | -0.39 | -0.09 | 13% / 17% |

Our five (Heart, Ryth, Marcella, Vendetta, Varg), summed with pair terms: near +0.02, far **-0.45**.
- Best pairs: near Willow+Tavi +0.46, Ryth+Prism +0.43, Ryth+Vesper +0.33; far Ryth+Prism +0.52, Cassi&Issac+Tavi +0.39, Vendetta+Cassi&Issac +0.36.
- Worst pairs: near Varg+Tavi -0.69, Vesper+Prism -0.50, Vesper+Vendetta -0.44, Marcella+Varg -0.38; far Ryth+Cassi&Issac -0.61, **Heart+Vendetta -0.47 (n 2,011)**.

## 2. Roles (what each champion does; top-15 games vs ours)
| | pvp | farm | carry 20+ gems | solo | gold | kills | deaths | team win |
|---|---|---|---|---|---|---|---|---|
| top Prism | 0.07 | 0.13 | **0.72** | 0.24 | 1,168 | 2.73 | 0.88 | 0.54 |
| top Vesper | 0.12 | 0.20 | 0.33 | 0.26 | **3,299** | 2.82 | 1.13 | 0.45 |
| top Cassi / Issac | 0.07-0.09 | 0.14-0.34 | 0.12 | **0.13** | ~330 | 0.4 | 2.13 | 0.59 |
| top Willow | 0.07 | 0.15 | 0.05 | **0.11** | 126 | 0.20 | 1.34 | 0.55 |
| top Tavi | 0.09 | 0.12 | 0.10 | 0.20 | 915 | 1.16 | 1.61 | **0.79** |
| top Heart / Marcella / Vendetta / Ryth / Varg | 0.11-0.15 | 0.23-0.30 | 0.15-0.26 | 0.21-0.28 | 554-1,595 | | 1.3-1.9 | |
| **our five** | **0.16-0.22** | 0.21-0.29 | 0.22-0.29 | **0.31-0.38** | 852-1,550 | | Ryth **2.92** | 0.42 |

The top teams build a funnel: one or two carries (Vesper for gold, Prism for gems) with grouped supports (Cassi&Issac, Willow, rarely alone). Our five are independent farmers who fight more and are alone more. Swapping their champions in without their roles fails: forced top-team compositions lost 16-34% in our bot (`results/ml-2026-11-08`).

## 3. Counters (champion vs champion, controlled for team strength and each champion's value)
- Strongest counters (row beats column): Varg > Marcella +0.43 (n 1,553), Stellar > Cassi&Issac +0.34, Ryth > Vendetta +0.32 (n 2,755), Heart > Ren +0.30, Ren > Marcella +0.30, Ryth > Cassi&Issac +0.28, Prism > Cassi&Issac +0.26, Vesper > Heart +0.25 (n 3,964).
- Our five against each enemy champion: worst vs **Ryth -0.73**, Varg -0.22, Stellar -0.13; best vs **Marcella +0.73**, Cassi&Issac +0.56, Vendetta +0.30.
- Picks are sequential, so our later picks can react to theirs. The current draft ignores the opponent: this is a free counter-pick lever among the champions our code plays well.

## 4. In progress
- One-champion swaps for Ryth (Prism, Cassi&Issac, Vesper, Ren) vs v51d.
- Shop timing and choices from 800 summaries.
- Map-type behaviour (the pack study is in `results/opening-pack-2026-11-08`).
- v53f (team focus) mirror.

## 5. Shop (800 summaries; top-20 teams 276 team-games vs our 80 strong-panel team-games)
| champion | top-20 stat split (H/S/F) | ours |
|---|---|---|
| Ryth | **Health 83-99%** (her bonus health adds strength) | **Strength 72-91%** |
| Marcella | **Focus 63-69%** | **Strength 57-93%** |
| Heart | Focus ~60%, Health ~38% throughout | Focus 75-91%, Health 9% after r500 |
| Prism | Health ~100% | (not drafted) |

- Item families: top teams open on Prospector plus Treasure (17-40%), move to Durability/Jungle/Bruiser, and stack Bruiser after r500 (37-77%). Health stays at ~35-40% of spend all game.
- We are 76-91% Bruiser after r500 with Health at 7-23%.
- Spend-share vs win associations (Bruiser +0.25, Treasure -0.27) are confounded by game length and are not used.
- Candidate **v53g**: v53f plus kit-aware stats (Ryth and Prism Health, Marcella Focus, health steps for every champion). Mirror pending.

## 6. Offence fix measured: v53f (team focus fire) vs v53d, 256 games
131-125. Kills 3.54 vs 3.08 per game (+15%), deaths 3.62 vs 4.02 (-10%), banked 842 vs 818, 0 bot faults. The intended mechanism shows up: more kills and fewer deaths.

## 7. Mirror results of the stacked candidates (256 games each, 128 maps x 2 sides, 0 bot faults)
Kills and deaths are per game, from champion metrics with side taken from the file name. An earlier ad-hoc script matched on the folder path and mis-assigned sides; the numbers below are corrected.

| candidate vs base | wins | gem margin | banked | kills | deaths | gold r400 |
|---|---|---|---|---|---|---|
| v53d (pack opening) vs v51d | 129-127 | -6 | 814 / - | | 3.6 | -1.8% |
| v53f (+ team focus) vs v53d | 131-125 | +24 | 842 / 818 | **3.54 / 3.08** | **3.62 / 4.02** | +0.2% |
| **v53g (+ kit-aware shop) vs v53f** | **151-105 (59%)** | **+79** | **859 / 780** | **3.97 / 2.89** | **3.36 / 4.42** | +3.0% |
| v53h (+ kill commitment) vs v53g | running | | | | | |

Single-champion draft swap: Ryth to Prism, 86-170 vs v51d. Our code cannot play Prism yet. The other swaps are still running.

v53g confirms the strength hypothesis: buying the stat each kit scales with (Ryth Health, Marcella Focus, Health kept late) gives +37% kills and -24% deaths in self-play.
| v53h (+ kill commitment) vs v53g | 123-133 | -23 | 808 / 831 | 3.62 / 3.81 | 4.23 / 4.06 | -0.5% |

v53h is rejected locally: staying on targets the team "can finish" lost more carriers with full bags (unconverted gems 121 vs 106) and did not raise kills. v53g remains the lead candidate. The parameter search (`tools/tune/search.py`) is running on v53g.

## 8. What teams do in each game state (`tools/playbook/states.py`)
Activity per alive champion-round:
- bank: carried gems fell while alive.
- fight: an enemy within 4.
- farm / invade: a living camp within 2 on our / their half.
- home: within 3 of its own spawn.
- carry: 20+ gems.
- move: anything else.

State is living champions ours minus theirs.
- Us: 40 strong-panel games, our side only.
- Top: 166 top-15 games, both sides.

| state | share of rounds (us / top) | fight | farm | invade | carry | bank: gems per 100 champion-rounds | kills per 100 |
|---|---|---|---|---|---|---|---|
| ahead | **14.6% / 37.4%** | 18.6% / 9.2% | 19.2% / 17.9% | 6.3% / 3.4% | 13.9% / 16.6% | 26.8 / 20.5 | 0.46 / 0.34 |
| even | 36.9% / 36.4% | 18.2% / 8.7% | 20.9% / 20.4% | 3.7% / 2.5% | 14.3% / 14.8% | 18.1 / 14.4 | 0.04 / 0.06 |
| behind | **48.5% / 26.2%** | 15.0% / 12.1% | 17.7% / 19.9% | 2.7% / 2.5% | 14.9% / 13.6% | 12.0 / 13.2 | 0.01 / 0.05 |
| r<200 | 17.6% / 24.8% | **16.5% / 8.3%** | 21.8% / 23.3% | | 9.4% / 9.5% | 8.1 / 7.4 | 0.04 / 0.10 |
| r200-600 | 34.3% / 45.1% | 17.3% / 9.5% | 20.1% / 19.9% | | 15.7% / 17.9% | 14.5 / 19.7 | 0.09 / 0.17 |
| r600+ | **48.1% / 30.1%** | 16.3% / 11.5% | 17.5% / 15.3% | | 15.6% / 15.7% | 20.8 / 18.8 | 0.10 / 0.21 |

Readings (measured):
- Against the strong teams we play **half of all champion-rounds a champion down** (48.5%). When we are ahead, we already do what top teams do: bank faster (26.8 gems per 100 rounds vs 20.5) and invade more. Our problem is how rarely we are ahead.
- Top teams spend **8-12% of rounds near an enemy, we 15-19%**, twice as much as them before r200. They farm through the opening, and their fights come when they are behind (12.1%), i.e. forced. When ahead they convert: fight 9.2%, carry and bank.
- Our games run long: 48% of our champion-rounds are after r600 (top 30%). We lose slowly from behind rather than being run over.
- Implication: the respawn-window play already works when we get it. The lever is fewer forced fights and not being a champion down (positioning: pack opening, turn order), not a separate "when enemies are dead" mode.
