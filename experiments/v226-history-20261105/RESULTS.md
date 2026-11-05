# Completed local regression check

72 completed engine-3.0.0 games: 36 matched cases per policy, six archived maps, both sides, three opponents including unchanged v50h5e.

| Policy | Wins / 36 | Fault events | Fuel events |
|---|---:|---:|---:|
| v50h5e | 30 | 0 | 0 |
| chatgpt-v50h5e-history | 30 | 0 | 0 |

Paired gains: 0; paired losses: 0. All candidate cases match baseline map hash, seed, opponent, side and engine build.

| Map | Baseline wins / 6 | Candidate wins / 6 |
|---|---:|---:|
| 00collision | 5 | 5 |
| 00contest | 5 | 5 |
| 00corners | 5 | 5 |
| 00eight | 5 | 5 |
| 00expanse | 5 | 5 |
| 00rows | 5 | 5 |

Small previously inspected regression set, two weak archived bots and a self-play control. No evidence of generalisation or competitive superiority; all-current-map/stronger-opponent tests required. No platform unranked games or deployment performed.
