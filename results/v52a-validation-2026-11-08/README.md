# v52a validation and bisect (8 Nov 2026, engine 3.0.0 / cambc 5.0.0)

128 maps x both sides = 256 games per row. Noise about +-8 wins. Bot faults: 0 in every game of every row.

## Lab reproduction
| Row | Wins | Share | Recorded before |
|---|---|---|---|
| v51d vs v50h5e (live) | 141-115 | 55.1% | 141-115 (identical) |

## v52a mirrors
| Row | Wins | Share | Gem margin | Banked (cand / base) | Deaths (cand / base) | Gold r400 |
|---|---|---|---|---|---|---|
| v52a vs v51d | 100-156 | 39.1% | -121 | 756 / 876 | 4.1 / 3.3 | -3.5% |
| v52a vs v50h5e | 116-140 | 45.3% | -73 | 779 / 851 | 3.9 / 3.2 | -3.6% |
| v52a vs v50p1 | 162-94 | 63.3% | +183 | 854 / 671 | 6.7 / 6.7 | +13.6% |

v52a is worse than v51d on every measure: wins (about 3.5 SE), banking, deaths and income. By the handoff rule it is not the candidate.

## Bisect: v52a with one feature removed, vs v51d (v52a itself: 100)
| Variant | Change from v52a | Wins vs v51d | Delta vs v52a | Banked | Gold r400 |
|---|---|---|---|---|---|
| v52g | guard_aware 0 (no guarded-altar routing) | 122-134 | +22 | 795 | -1.7% |
| v52l | learned_shop true (no hand plan, so no Capture) | 110-146 | +10 | 799 | -3.9% |
| v52c | guard_n 0 (no contest guards) | 103-153 | +3 (noise) | 760 | -1.4% |
| v52k | no Capture emblem / timing (hand plan kept) | 89-167 | -11 | 753 | -1.9% |

Reading: guarded-altar routing is the main cost (+22 wins when removed). The hand shop plan costs about 10. The Capture emblem helps within the hand plan. Contest guards are neutral. Even the best repaired variant (v52g, 47.7%) does not beat v51d. The leftover v52g features (hand shop + Capture + contest guards) are -12 vs v51d, within noise, so there is no evidence for any of them.

## Decision
Ship candidate: **v51d** (unchanged). The variant folders exist only in the lab (`config.h` one-line edits of `bots/v52a`). They are not added to `bots/`.
