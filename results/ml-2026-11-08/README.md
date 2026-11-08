# ML experiments, 8 Nov 2026 (engine 3.0.0)

## 1. Death hazard: prediction is not the bottleneck
`tools/hazardml/build.py` and `train.py`: 20 bot features per champion-round from decoded replays. Label: killed by an enemy within 10 rounds.
Pilot: our 40 strong-panel games, 68,296 rows, 3.7% positive, 5 folds held out by match.

| model | AUC | recall at the shipped alarm rate (15.4%) |
|---|---|---|
| shipped logistic (v51d) | 0.899 | 0.749 |
| refitted logistic | 0.905 | 0.764 |
| MLP 32-16 | 0.902 | 0.744 |

The shipped model already flags three quarters of deaths in advance, and a neural network adds nothing on this data.

## 2. What happens after the alarm (`tools/hazardml/response.py`)
Response over the next 3 rounds after an alarm (shipped p >= 0.2):
- *ally*: moves toward the nearest ally.
- *home*: moves toward its own spawn.
- *enemy*: moves toward the nearest enemy.
- *hold*: moves 1 tile or less.

| | alarms | died within 10 | ally | home | enemy | hold | allies within 8 at alarm |
|---|---|---|---|---|---|---|---|
| us (40 games vs ha²t/Gamblr/Valenki/Kratos, our team only) | 3,605 (~90 per game) | 0.179 | 29% (0.148) | 33% (0.092) | 4% | 28% (0.142) | 0.8-1.5 |
| top-15 vs top-15 (59 games, both teams) | 5,207 (~44 per team-game) | 0.217 | 16% (0.203) | 34% (0.132) | 6% | 34% (0.120) | 2.7-3.5 |

Bracketed numbers are the death rate after that response.

Per alarm, we survive as well as the top teams. We enter about twice as many danger states, and with about one ally near instead of three. The lever is positioning (not being alone), not the retreat logic or the hazard model. This supports the pack opening (v53d, `results/opening-pack-2026-11-08`).

## 3. Learned map draft (bots/v54m, tools/draftml)
Running: 6 forced playstyles x 128 maps x both sides vs v51d and v50p1, plus map features dumped by the bot in the draft turn (100x fuel). The control (comp 0 through the new path) reproduces v51d exactly (128-128, margin 0). Results to follow.

## 4. Offence: we attack more and kill less (`tools/hazardml/offense.py`)
An opportunity is an enemy whose own hazard (shipped model, from its point of view) is at least 0.3, with one of ours within 6 tiles. One per enemy per 5 rounds.

| | us (40 strong-panel games) | top-15 vs top-15 (59 games) |
|---|---|---|
| opportunities per team-game | 23.8 (before r200 2.4) | 16.4 (2.1) |
| committed (closed in or hit within 3 rounds) | 0.71 | 0.56 |
| converted to a kill within 10 rounds | **0.15** | **0.28** |
| converted when committed | 0.15 | 0.26 |
| kills from opportunities per team-game | 3.6 (before r200 0.50) | 4.6 (0.84) |

We create and commit to more chances than the top teams but convert half as many. Committing does not raise our conversion at all. The offensive lever is execution (focus fire, stun first, numbers and cut-off at the commit), not aggression.

## 5. Draft screen: our bot cannot play the top teams' compositions
Forced draft vs v51d (128 maps x 2 sides):
- Heart, Cassi&Issac, Vendetta, Marcella, Vesper: 49-207, gold r400 -10.8%.
- Heart, Cassi&Issac, Vendetta, Willow, Prism: 40-216, -16.1%.
- Heart, Marcella, Cassi&Issac, Vendetta, Willow: 63-193, -5.4%.
- Control (our five through the new path): 128-128.

A learned draft can only choose among compositions the play code supports. Comps 4-5 and the v50p1 runs are still pending.

## 7. Is it power? Kill conversion by local power ratio (our champions within 6 / victim; power = max HP x (strength + focus))
| ratio | us: kill rate | top: kill rate |
|---|---|---|
| under 1 | 0.06 | 0.22 |
| 1-2 | 0.16 | 0.25 |
| 2-3 | 0.17 | 0.28 |
| 3-5 | 0.13 | 0.32 |
| over 5 | 0.17 | 0.39 |

The top teams convert more the stronger they are; we do not, at any ratio. Team power at those moments is about even (median 1.02).

At ratio 3 or more, outcomes within 10 rounds:

| outcome | us | top |
|---|---|---|
| killed | 15% | 36% |
| damaged, survived | **54%** | 31% |
| no damage | 19% | 20% |
| escaped to spawn | 12% | 13% |

In the "damaged, survived" cases the nearest attacker averages 1.6 tiles away, and only a third of the target's health comes off. We start fights and stop. Next fix: kill commitment (no disengage or camp switch while a focus target is about to die).

## 8. Numbers and kill probability at our commits (`tools/hazardml/killmodel.py`)
A commit is an opportunity (section 4) where the attacking side closes in or hits within 3 rounds.

| | us (40 strong-panel games) | top-15 (166 games) |
|---|---|---|
| commits | 704 | 3,498 |
| kill rate | **0.19** | **0.415** |
| our attackers within 6 / target side within 6 | 2.23 / 2.32 | 2.77 / 2.57 |
| outnumbered / even / ahead | **33% / 38% / 29%** | 27% / 33% / 40% |
| kill rate outnumbered, even, +1, +2 or more | 0.18, 0.18, 0.23, 0.20 | 0.39, 0.40, 0.43, 0.45 |

Logistic kill model fitted on top-team commits, held out by game (AUC 0.715). Standardised effects: log power ratio +0.74, target health -0.74, target side count +0.12, cut-off +0.10, attacker count +0.03, target distance to its spawn +0.02. Power and the target's health decide kills; head count and distance to its spawn barely matter once power is known.

Our commits scored by that model: predicted 0.37 (top teams' 0.42), actual 0.19. We pick slightly worse chances and are outnumbered more often, but even our best chances (predicted >= 0.5) convert at 0.40 against the top teams' 0.64. Execution is still the main gap. A commit gate (commit only when predicted kill >= ~0.4) is a cheap addition.
