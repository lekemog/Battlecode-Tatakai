# Javiops/Cambridge-Battlecode-2026 (rank 25 at v29): what transfers to us, 10 Nov 2026

Source: their repo (README, harness/IDEAS.md, current-state/ dissection of 150 online games vs the top 30, analysis/top1-cycle).
Their data is from mid-October (older engine and the 9 official maps); the behavioural findings transfer, the per-map ones do not.

## Their dissection, in one line
Farming alive is as good as the top teams (captures, gems per capture, walking); they lose because they die (5.7 vs 3.9 a game),
mostly in their own half from 90% health over about 5 rounds, to spells. Same profile as ours (ranked losses: deaths 7.7 vs 4.2).

## Findings and whether they apply to us
| their finding | applies? | action |
|---|---|---|
| Ranged champions attack from distance 1-2 (35% vs top 24%) and die after retreating (30% vs 13%) | **No**: all our drafted champions are melee (range 1, logged in game) | none |
| 325 of 709 deaths had an ally within 6 that never attacked; help rate 32% when the victim dies | **Yes**: our help rule only fires on favourable verdicts | **v57a rescue** (below) |
| Keep farming / idle while a visible pack walks in (median 13 rounds of contact before the first hit) | Partly: our no_loss_stance keeps farming while the simulation predicts no death; v55a's calibration now corrects that prediction in game | covered by v55a; revisit if the panel shows it |
| Openers on a walking enemy lose; openers on a farming/recalling/tributing enemy pay | Yes | idea for the hunt window (v56c prey filter), not built yet |
| Recall on the capture tile (accepted, local 88-34) | Already in our bot (capture_recall = 2) | none |
| Stack on 3000+ HP camps, spread on small ones (accepted) | Our siege/squad scoring already does this | none |
| Top team (#1 at the time) drafts casters (Stellar did 30% of their deaths) | Our code cannot play casters well (Prism swap lost 86-170 earlier) | none now |
| Avoid camps that hurt: damage taken = 3 x strength x kill time x (distance from home + 5) / 900 | We charge camp damage as a share of a recall trip | possible later experiment |

## v57a = v55a + rescue
When our fight verdict is not favourable but an ally within 5 is in contact (an enemy within 2 of it) below 60% health, join the
fight if the simulation with us included is at least an even trade. Mirror vs v55a queued after v56c.
