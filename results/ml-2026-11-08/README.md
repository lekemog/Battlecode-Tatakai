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
