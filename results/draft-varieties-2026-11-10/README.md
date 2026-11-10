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
