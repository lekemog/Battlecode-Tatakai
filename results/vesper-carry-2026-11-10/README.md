# Vesper carry: why the UK teams beat us, and the v60 line (10 Nov 2026)

Tier of every number: **local self-play** (128 maps x 2 sides vs the live bot v53x) unless it says "UK panel"
(the 180 stored games of v53i / r5 / v53s / v53t against the nine UK teams above us). Nothing here has met a real opponent yet.

## What the stored UK-panel games show
- Champion by champion against us (UK side, per game): **Vesper Vale 2.98 kills, 0.74 deaths, 4,120 gold, 13.4K champion
  damage**; Prism 3.12 kills, 0.21 deaths; Marcella 2.39 kills. Every other champion is at or below 1.3 kills.
- In teams that field her, Vesper holds **48% of the team's gold** and does 36% of its monster damage (44.5K a game;
  the next best champion does 30K). Her curve: gold 195 / 431 / 692 / 1,303 at r100 / 200 / 300 / 500, while each
  teammate has 52 / 121 / 198 / 383. At r100 she has dealt *less* monster damage than a teammate (1,238 vs 1,542):
  early on the others kill and she takes the capture (+33% gold), later she is the main farmer.
- Her build (44 games): Prospector, Capture, Treasure, Jungle, Monster, **all Strength**, then Bruiser.
  Growth per 30-gold shard: Vesper +5 Strength on a base of 35 (Vendetta +6 on 65, Marcella +10 Focus on 60).
- Opening: by r10 the UK teams have dealt 2.3x our monster damage (383 vs 167) and their k-th champion lands its first
  monster hit 3 to 9 rounds before ours (medians 9/12/15/18/27 vs 12/18/21/28/36). Gold only comes from captures and
  kills (no passive income): at r50 they lead 137 to 98, about 20 of it from early kills.

## Things ruled out
- **Fuel is not a lever.** v53x with double fuel against v53x burning the surplus: 68-64 after 132 games.
- **The earlier draft swaps were not what they said.** With `draft_mode 99` the learned draft weights still reordered the
  list: "v58a = Ryth -> Vesper" really drafted Heart, Marcella, Vendetta, Vesper, Ryth (no Varg; no Vesper on 3-pick maps).
  v60a adds `draft_learned = false` so mode 99 is literal.
- **A three-champion ball all game** (v60e: escort_until 2000): 55-201. The escort code idles too much.

## The v60 line (each is the previous plus one change), vs v53x over 256 games
| bot | change | wins | Vesper gold / monster damage / gems per game |
|---|---|---|---|
| v60a | literal draft: Heart, Marcella, Vesper, Vendetta, Varg | 78-178 | 719 / 13.7K / 98 |
| v60b | ranged champions strike a camp even when they are its nearest target | 92-164 | 851 / 17.3K / 119 |
| v60c | carry shop build; capturer rule sees the carry within 5 tiles | 96-160 | 955 / 17.9K / 115 |
| v60d | teammates hand a gold capture to the carry once she stands on a member tile | 97-159 | **2,000 / 24.1K / 259** |
| v60e | v60d + ball all game | 55-201 | 1,829 / 19.7K / 214 |

Bugs found in the ranged play (all fixed in v60b-d):
1. `fight_camps` skipped the attack on a "bad spot" (the tile makes her the monsters' nearest target) and then found no
   better tile: a solo Vesper stood in an elk's range for 24 rounds without one hit, three times in one game.
2. `carrier_capture` is off, so whoever stood on a camp tile kept the capture: Vesper's first gold came at **round 304**
   in the traced game while Varg took 170 gold two tiles from her at r30 (226 on her).
3. The shop gave her the tank plan (Durability Health, Bruiser Health) instead of the Strength economy emblems.

## Where v60d stands
- Vesper now out-earns and out-kills the Ryth she replaces (2,000 gold, 0.78 kills, 0.57 deaths vs 1,232 / 0.37 / 1.07),
  but she is still at **half the UK curve** (gold 99 / 208 / 334 / 631 at r100-500) and the comp loses the self-play gem
  race (892 vs 973 gems collected).
- Self-play is the wrong judge for a draft (TESTING.md section 3): the comp needs the UK panel.

## Tools added (`tools/lab/`)
`mir.sh` (mirror with fuel / round options), `champ_stats.py` (per-champion table), `champ_curve.py` (gold, monster damage
and gems at r50-500), `trace_summary.py` (compress the bot's debug trace into runs), `trace_positions.py` (positions from
a decoded replay), `run_decoded.sh` (one game, decoded).
