# Engine 2.0.0 bench (cambc 4.0.0), 26 Oct

40 maps x 2 sides x 7 opponents = 560 games, JOBS=4, run in Szymon's Claude session.

| Bot | Change | Wins /560 | Margin |
|---|---|---|---|
| **v25u** | live | **492** | +4127 |
| v29b | v25u + Monster opener (no Treasure) | 485 | +3992 |
| v29c | v25u + Capture emblem 2nd | 483 | +3863 |
| v29t | v25u + Tribute emblem 3rd | 483 | +3846 |
| v29a | v25u + patch draft (C&I/Ren/Varg up; HoR/Vesper/Marcella down) | 472 | +3649 |
| v27j | v27i core + rally-flag fix | 469 | +3684 |
| v28 | v27j + draft + Monster + Capture (live as 218, 0/5 scrims) | 414 | +2800 |

**Verdict:** nothing beats v25u; keep it live. The patch-driven draft is the worst single change (-20); the item changes are each -7 to -9; together on v27j they compound to -55. The v27 core is -23 on the new engine. Caveat: the 7 bench bots are frozen pre-patch bots, so this measures our changes against old-meta opponents.

Per-opponent lines:
```
x_daniel8 v25u TOTAL 57  margin +334
x_de41h4 v25u TOTAL 66  margin +405
h_mohnish v25u TOTAL 64  margin +460
h_deysag v25u TOTAL 66  margin +481
h_vatsal v25u TOTAL 80  margin +839
h_photon v25u TOTAL 80  margin +835
h_apex v25u TOTAL 79  margin +773
x_daniel8 v27j TOTAL 50  margin +138
x_de41h4 v27j TOTAL 65  margin +417
h_mohnish v27j TOTAL 57  margin +334
h_deysag v27j TOTAL 65  margin +459
h_vatsal v27j TOTAL 78  margin +777
h_photon v27j TOTAL 79  margin +800
h_apex v27j TOTAL 75  margin +759
x_daniel8 v28 TOTAL 35  margin -0
x_de41h4 v28 TOTAL 52  margin +209
h_mohnish v28 TOTAL 51  margin +216
h_deysag v28 TOTAL 46  margin +120
h_vatsal v28 TOTAL 77  margin +789
h_photon v28 TOTAL 78  margin +782
h_apex v28 TOTAL 75  margin +684
x_daniel8 v29a TOTAL 58  margin +285
x_de41h4 v29a TOTAL 54  margin +284
h_mohnish v29a TOTAL 58  margin +335
h_deysag v29a TOTAL 63  margin +359
h_vatsal v29a TOTAL 80  margin +825
h_photon v29a TOTAL 79  margin +789
h_apex v29a TOTAL 80  margin +772
x_daniel8 v29b TOTAL 63  margin +369
x_de41h4 v29b TOTAL 60  margin +376
h_mohnish v29b TOTAL 61  margin +428
h_deysag v29b TOTAL 63  margin +413
h_vatsal v29b TOTAL 79  margin +821
h_photon v29b TOTAL 79  margin +813
h_apex v29b TOTAL 80  margin +772
x_daniel8 v29c TOTAL 60  margin +333
x_de41h4 v29c TOTAL 64  margin +351
h_mohnish v29c TOTAL 60  margin +361
h_deysag v29c TOTAL 63  margin +426
h_vatsal v29c TOTAL 79  margin +824
h_photon v29c TOTAL 79  margin +806
h_apex v29c TOTAL 78  margin +762
x_daniel8 v29t TOTAL 55  margin +294
x_de41h4 v29t TOTAL 57  margin +280
h_mohnish v29t TOTAL 64  margin +419
h_deysag v29t TOTAL 70  margin +458
h_vatsal v29t TOTAL 79  margin +815
h_photon v29t TOTAL 80  margin +824
h_apex v29t TOTAL 78  margin +756
```

## v27 core fixes (27 Oct)
| Bot | Change | Wins /560 | Margin |
|---|---|---|---|
| v27k | v27j + no long-range chase mid-capture (gemfight flip-flop) | 472 | +3723 |
| v27l | v27k + squad gives up on a target not captured in 120 rounds | 465 | +3557 |
| v27m | v27l + commit enough squad members to clear the squad target | 446 | +3385 |

Only v27k's fix holds up (+3 over v27j); v27l and v27m are rejected. The v27 line stays below v25u (492), so work moves
to v25u directly, driven by tools/scan/scan.py.

## Scanner round 1: v25v (27 Oct)
`tools/scan/scan.py` over 560 logged v25u games: 2.8 deaths a game to camps (40% of deaths). Traces showed a retreat
without hysteresis (retreat at ~30% HP, step out of camp reach, walk straight back). v25v = v25u + hold the retreat
below 50% HP until 60% or spawn.

| Bot | Wins /560 | Margin | Camp deaths/game | Champion deaths/game | Kills/game | Gems lost/game |
|---|---|---|---|---|---|---|
| v25u | 492 | +4127 | 2.82 | 4.12 | 16.46 | 65.8 |
| v25v | 491 | +4083 | 2.77 | 4.22 | 16.43 | 63.1 |

Fixed the traced game (reverse-spiral vs h_photon: 725-143 at r2000 -> 1001-229 at r1573, deaths 42 -> 16) but no
effect overall: camp deaths are not mainly this loop. Not a candidate; next scanner item.
