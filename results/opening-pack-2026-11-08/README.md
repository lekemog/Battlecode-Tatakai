# Opening pack: top teams vs us, and candidate v53d (8 Nov 2026, engine 3.0.0)

Tools: `tools/replay/extract5.mjs` (engine-3 decoder), `tools/replay/decode_dir.py`, `tools/replay/opening5.py`. Rounds 1-150.
Columns:
- *main*: size of the largest group of active champions (link 6 tiles, champions more than 4 from spawn).
- *ahead / behind*: rounds where, at a champion-vs-champion contact (within 6), the team has more / fewer champions near it.
- *deaths*: deaths by r150.
- *near / far*: spawn walk at most / over 60 steps.

## Top-15 teams against each other (59 random engine-3 ranked games, 118 team samples)
| picks | n | main | share in main | deaths r150 |
|---|---|---|---|---|
| 3 | 18 | 2.49 | 0.83 | 0.72 |
| 4 | 24 | 2.98 | 0.80 | 1.42 |
| 5 | 76 | 3.63 | 0.70 | 0.74 |

## Us (v226) vs ha²t, Gamblr, Valenki, Kratos (the 40 baseline panel games, s8base + s8base2)
| | n | main | ahead | even | behind | deaths r150 | first death |
|---|---|---|---|---|---|---|---|
| them, near maps | 30 | 3.04 | 41.3 | 34.0 | 12.4 | 0.40 | r135 |
| **us, near maps** | 30 | **2.28** | **16.0** | 35.2 | **36.4** | **1.20** | **r106** |
| them, far maps | 10 | 3.69 | 12.4 | 7.9 | 5.5 | 0.10 | r146 |
| us, far maps | 10 | 3.13 | 9.8 | 8.6 | 7.4 | 0.10 | r146 |

On close and contest maps our biggest group is about one champion smaller. We are outnumbered at contact three times as often (36 rounds vs 12) and die three times as often before r150. On far maps we match them. This confirms the team's read: they open as a pack and pick off our split champions.

## Candidate v53d (bots/v53d)
v51d plus a pack opening:
- **Who:** the first three drafted champions (Heart, Ryth, Marcella: the top teams' anchor plus our two stunners) form one squad. On 3-pick maps it is the first two.
- **How:** the leader (lowest index) farms normally and the others escort it within 2 tiles (the existing `escort` code). The other two champions farm alone as satellites.
- **When:** until r100 (`escort_until`, `squad_until_round`), and only where the spawn walk is at most 60 steps. The walk comes from the bot's own spawn field.
- **Gate check:** probed on all 128 maps, the gate keeps the pack on 81. Every map the top-team study calls "farm" measures more than 60 steps (62 to 242), and every "contest" map measures 33 to 54.
- **Flags:** `pack_size`, `pack_max_walk`; 0 turns it off.

Mirror vs v51d (256 games): **129-127**, gem margin -6, deaths 3.6, gold r400 -1.8%, 0 bot faults. No self-play cost, unlike v53c's soft cohesion (110-146). Not yet tested against real opponents; that needs a submission.

Earlier evidence to weigh: a public team's pack opening (Ajayendra2705, vpk3) cut local deaths but came out level over 170 pinned games. Their pack was the whole team; ours is three champions plus satellites, which matches the measured top-team shape.
