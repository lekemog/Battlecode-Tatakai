# Qualifier seeding: what position or rating gives a UK top-8 chance (9 Nov 2026)

Sources:
- the public tournaments API (`/api/v1/tournaments`, International Qualifiers detail: 504 entrants, double elimination with reset final, 21 games per match, seeded by ladder rating at the lock, 1,023 matches with links);
- the current ladder (700 teams).

Tool: `tools/playbook/bracket_sim.py`.

## What the International Qualifier shows (measured)
Series odds by rating gap (favourite = higher seeding rating):

| gap | n | favourite wins |
|---|---|---|
| 0-25 | 79 | 54% |
| 25-50 | 48 | 60% |
| 50-100 | 104 | 87% |
| 100-150 | 103 | 89% |
| 150-250 | 190 | 99% |
| 250+ | 479 | 100% |

The fitted model is P = 1 / (1 + 10^(-gap/108)), giving 0.74 at a 50-point gap and 0.89 at 100.

Top 8 by seed:

| seeds | in top 8 |
|---|---|
| 1-4 | 4/4 |
| 5-8 | 2/4 |
| 9-16 | 2/8 |
| 17+ | 0/488 |

- The lowest-rated top-8 team was 2,329.
- Top 8: Fish (1), newer team (3), Mite (2), NEETCoders (4), test4 (5), Trzy Kwaterki (8), Nyx (9), Sponge (13).
- 21-game series make upsets rare: the bracket mostly sorts by rating, with some luck among teams within about 50 points.

## UK qualifier simulation (assumptions marked)
Assumptions (unverified):
- The UK qualifier uses the same format: double elimination, 21-game series, ladder seeding, top 8 qualify.
- The field is 188 UK teams (the 5 Nov UK filter count).
- The UK teams above us are the nine identified ones, at their current ratings: BattleCats 2558, Claudus Maximus 2332, QS2isLaw 2284, Rogue Lock Pickers 2258, bentheboss 2246, smurphy 2200, 剑桥夜爬者 2187, DOOMSDAY 2174, 0xDEADBEEF 2161.
- The rest of the field is drawn from the global ladder below us.

The bracket is the IQ's own link graph, with empty seeds as byes.

| our rating at the lock | P(top 8) |
|---|---|
| 2,090 (now, natural seed 10) | **12%** |
| 2,150 | 31% |
| 2,200 (about smurphy, UK 6th) | 58% |
| 2,250 | 86% |
| 2,300 | 94% |

Same strength (2,090), counterfactual seed:

| seed | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P(top 8) | **43%** | **42%** | 11% | 12% | 10% | 10% | 8% | 9% | 8% | 5% | 7% | 4% |

- Seeds 5-6 have a much easier path in this bracket than seeds 7-16. The cliff is between 6 and 7.
- Sensitivity: with two unidentified UK teams above us (2,120 and 2,140), our 2,090 chance falls to 7.5% and seeds 5-6 give only 15% / 12%.

## Reading
1. **Rating is the lever.** Each +50 rating roughly doubles or more our chance in this range. Seed position adds a smaller effect.
2. If we can get into the top 6 UK seeds (rating at about smurphy's 2,200 or above, with the six ahead of us unchanged), we get both higher strength and the easier 5-6 path.
3. Everything below seed 6 is a 4-12% lottery at our current strength.

Caveats: the UK format, field size and the full UK membership above us are not confirmed (the API does not expose UK membership). The lock hour is unconfirmed.
