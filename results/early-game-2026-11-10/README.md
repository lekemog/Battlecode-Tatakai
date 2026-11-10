# Early game (first 300 rounds), 10 Nov 2026

## UK panel data (180 games: v53i, r5, v53t, v53x on the same pinned 45)
| | wins (42) | losses (138) |
|---|---|---|
| earned gold r100 us / them | 420 / 358 | 250 / 386 |
| earned gold r200 | 962 / 793 | 588 / 874 |
| earned gold r300 | 1542 / 1262 | 974 / 1420 |
| deaths before r300 us / them | 0.93 / 1.50 | 1.86 / 0.97 |

- Ahead in gold at r200: 44% wins (63 games). Behind: 12% (117). The game is mostly decided by r200.
- More enemy deaths than ours before r300: 40% wins; fewer: 12%.
- The gap starts before the fighting: gold at r50 is 98 vs 137 (-30%) with the same monster damage (809 vs 799), so we earn
  less gold for the same farming. Prime suspect: the escorted ball (before escort_until = 60 only the acting leader farms
  for the team). Per champion at r100 our Marcella earns 51 vs their Marcella 114; their Vesper Vale 208.
- Team size is set by the map (3/4/5 picks): not a lever.

## Experiments (on v55a)
- **v56a**: no escorted ball (escort_until 0, squad_until_round 0); the pack still forms on near maps.
- **v56b**: v56a + early hunt window (hunt_mode 4): rounds 60-300, chase an isolated enemy (no other enemy within 4 of it)
  whose health x damage (times the in-game calibration multiplier) is at least 1.3x below ours, only with an ally within 4.
  The fight simulation still decides whether to engage.
- Measured on gold at r50/100/200/300 and deaths before r300 (tools/lab/mirror_gold.py) as well as wins.

## Results
- **v56a (no escorted ball): rejected.** 109-147 vs v55a (margin -44), unseen 60-80; kills 3.52 / 4.19, deaths 4.64 / 3.90.
  Gold barely moved (r50 118 vs 109, r300 1114 vs 1118). The ball is not the cause of the r50 gold gap vs the UK teams,
  and it helps the opening fights. Hypothesis wrong.
- v56b inherits v56a's change, so its result is confounded; **v56c** = v55a + the early hunt window with the ball kept.

## New public repo (10 Nov): Javiops/Cambridge-Battlecode-2026 (rank 25 at v29)
- A 12-chapter tactics handbook (docs/tactics), a gate harness, 60 sealed holdout maps and 200 dev maps.
- Relevant: camp scoring counts team rewards once and personal gold separately, with even reward division (exponent 0.75
  for big camps); a rejected fight must not fall through to unsafe camp play; "power spikes" listed as Planned, not built.
- **v56b** (no ball + early hunt): 118-138 vs v55a (margin -27), unseen 70-70; kills 4.01 / 3.88, deaths 4.27 / 4.40,
  deaths before r300 1.09 / 1.16. Compared with v56a (no ball alone, 109-147, kills 3.52, deaths 4.64), the hunt window adds
  about +9 wins, +0.5 kills and -0.4 deaths. **v56c** (ball kept + hunt) is the clean test; running.
