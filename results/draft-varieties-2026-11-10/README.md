# Draft varieties with a ranged role, 10 Nov 2026

Why: our five (Heart, Ryth, Marcella, Vendetta, Varg) are all melee (range 1) and score about 0 (near) / -0.45 (far) in
log-odds over 4,680 top-60 games; Ryth is the weakest pick (-0.28) and our deadliest (2.92 deaths a game). Top teams play a
funnel (Vesper gold carry, Prism gem carry, Cassi&Issac / Willow grouped supports). Forcing their comps into our melee code
lost 40-216 to 86-170 earlier, so each variety now runs with a ranged role first.

## v58k = v55a + ranged role
A ranged champion that has not moved this turn steps to the neighbour tile with the fewest enemies able to hit it next round
(melee: within 2), then one keeping a target within attack range, then one near an ally; it attacks after the step if it
has not yet. No effect on our melee five.

## Varieties (draft_mode 99; 3/4-pick maps take the first picks)
| bot | change | order |
|---|---|---|
| v58a | Ryth -> Vesper Vale (gold carry) | Heart, Marcella, Vesper, Vendetta, Varg |
| v58b | Ryth -> Cassi&Issac | Heart, Marcella, Cassi&Issac, Vendetta, Varg |
| v58c | Ryth -> Prism (gem carry) | Heart, Marcella, Prism, Vendetta, Varg |
| v58d | Vendetta -> Prism (Ryth+Prism is the best pair in the data) | Heart, Marcella, Ryth, Prism, Varg |

Each vs v55a, 128 maps x 2 sides, with kills/deaths and gold at r50-r300. Results below when done.

## Results vs v55a (128 maps x 2 sides, 0 faults)
| bot | wins | margin | kills / deaths (cand vs base) | gold r50 | gold r300 | deaths < r300 |
|---|---|---|---|---|---|---|
| v58a Ryth->Vesper | 76-180 | -139 | 3.48 / 3.54 vs 3.18 / 3.86 | 103 / 110 | 1035 / 1123 | 0.81 / 0.86 |
| v58b Ryth->Cassi&Issac | 90-166 | -166 | 3.37 / **7.59** vs 4.73 / 3.69 | **133 / 108** | 1156 / 1143 | 1.71 / 1.01 |
| v58c Ryth->Prism | 76-180 | -177 | 3.71 / 4.89 vs 4.50 / 4.07 | 111 / 111 | 1088 / 1155 | 1.13 / 1.07 |
| v58d Vendetta->Prism | 72-184 | -179 | 3.68 / 4.97 vs 4.58 / 4.11 | 110 / 110 | 1059 / 1143 | 1.19 / 1.04 |

- Every swap loses badly (28-35%) even with the kiting step: the play code, not the pick, is what fails.
- Each swap failed differently, and that points at what to build:
  - **Vesper** dies less but earns less gold. Our farming code never uses her bonus gold or carry role.
  - **Cassi&Issac** earns 23% more gold by r50 (133 vs 108), the only change so far that touches the opening gold gap,
    but deaths double (7.59): if either twin dies both die, and our code does not keep them together or out of fights.
  - **Prism** dies more and banks less: she gains focus from carried gems, so she should carry and stay back; our code
    plays her as a melee brawler.
- Next step for whoever continues: role code per champion (twins kept together and out of front lines; Prism carries and
  stays behind; Vesper as gold carry), then re-run these four swaps.
