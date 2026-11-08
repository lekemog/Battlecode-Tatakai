# Match audit: 18 Oct 2026

**Method.** Our ranked replays (most recent first) and one 130-game test cycle against top-100 teams were downloaded and decoded round by round.
- Every death of ours is classified by what was happening and mapped to the bot function that made the decision.
- Classification inputs: enemies and allies within 5, gems carried, near an altar or camp, which half of the map, tribute channel, and Cassi/Issac linked death.
- Each death is joined to the bot's own log line for that champion.
- Tools: `tools/audit/` (`fetch.py`, `cycle.py`, `audit.py`).

## All decoded games so far (187 games: 64 wins, 2003 deaths, 17,903 gems lost on death)

| Decision path | Deaths | Gems lost |
|---|---|---|
| `handle_enemies()`: fought or stayed while outnumbered | 26% | 1590 |
| `handle_enemies()`: kept farming as enemies closed in | 21% | 3622 |
| Cassi & Issac linked death (losing Cassi kills Issac) | 16% | 2832 |
| Unclassified | 15% | 702 |
| `choose_group()`/`solo_target()`: deep in the enemy half | 10% | 1388 |
| `bank()`: tribute channel with enemies arriving | 5% | **4948** |
| Chase rule pulled us into a losing fight | 3% | 839 |
| `bank()`: walking to an altar with a bag | 1% | **1772** |

- Altar and bag deaths are only 6% of deaths but **38% of lost gems**.
- Contest: **42 deaths per game** (21 games).
- 30 of 123 losses were pure farming races (≤2 deaths).

## Top-100 test cycle 1 (v16o, 55 decoded games so far, 19/130 wins overall)
- Contest deaths fell to **16 per game**, down from 42. The v16o lone-farmer fix works.
- Swirl is now the worst map at 25 deaths per game.
- **18 of 50 losses were pure farming races.** At top-100 level, farming pace matters as much as dying.

## Sample deaths, round by round
1. **Elkring, Stellar.** Full HP (750) with Prism and Tavi 7 tiles away, dead 2 rounds later: a stun plus burst from range. `threat()` counts only enemy strength, and the burst is focus-based.
2. **Swirl, Cassi.** Sat at 360/700 HP for 8 rounds with 3 enemies within 3–4 tiles, logged action "fight", then died. `handle_enemies()` judged the fight favourable because 4 allies were near, but the enemy focused Cassi.
3. **Lanes, Issac.** Alone, poked down from 900 to 160 HP over 8 rounds by a ranged Cassi at 4–9 tiles while it kept farming. The retreat only fires below 30% HP.

## Fixes
| Version | Change | Status |
|---|---|---|
| v16n | `bank()` has no forced tribute for bags of 60+ and uses the learned danger estimate; `handle_enemies()` leaves when outnumbered by 3+; Cassi needs a 1.3× edge; evade starts at enemy range +3 | Deployed |
| v16o | Gold-only maps: farm our half, never fight alone away from home | Deployed; contest deaths 42 → 16 per game |
| v16p | Count enemy focus in fight strength; Cassi never fights alone | Rejected: 11/34, −184 locally |
| v16q | Burst-aware `threat()`, retreat at 50% HP with an enemy close, drain detector | Rejected: 10/34, −215 locally |
| v16r | Burst-aware threat plus drain retreat only | Rejected: 10/34, −171 locally |

**Lesson.** Making the bot more cautious keeps losing heavily in local tests: retreating costs more farming and fights than it saves. The remaining gains are in **farming pace** (18 of 50 top-100 losses had ≤2 deaths) and in **targeted** protection: bags and Cassi, not blanket caution.

## Ladder
- Rank ~352 overnight, then 313 on v16m, then **264 on v16n/v16o** (5 series won, 3 lost since 03:10).
