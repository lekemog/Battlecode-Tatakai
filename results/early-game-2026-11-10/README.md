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
