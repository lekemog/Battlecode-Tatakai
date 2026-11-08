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
