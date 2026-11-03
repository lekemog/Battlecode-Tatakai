# v51a / v51b: the top ten's bank habit, plus altar guards on contest (2026-11-03)

## Why
Two sources point to the same failure: against the top ten, our carriers hoard and die.
- **Public-repo review** (`results/public-repos-2026-11/`, third-party data, not verified by us): the top three bank **25-45 gem bags from round 44-87 onwards, many times a game**.
- **Zero-bank study** (`results/zero-bank-2026-11/`): in 4 of 5 zero-bank top-ten games we collected 250-750 gems and banked none. Carriers held 50-150 gems, stayed 13-21 tiles from a guarded altar, and in 14 of 16 deaths with a bag had **no ally within 7 tiles**.
- **Fresh top-ten review** (`results/tatakai-top10-20261028-fresh.md`): 5/50, deaths 11.4 vs 2.5, 00contest collected 0.

## Mechanism in our code (v50h5e, live #226)
`handle_tribute` triggers at `tribute_gems` (25) times a learned factor `learn::factor(...)`, which is clamped to e^±3. So the trigger bag can grow to about 500 gems. That is how 100-150-gem bags come about. Carriers then walk alone to the nearest altar, whether or not it is guarded.

## Changes (each a flag in `config.h`)
| Flag | v51a | What it does |
|---|---|---|
| `tribute_cap = 40` | on | The trigger bag never exceeds 40 gems (after the learned factor). |
| `guard_aware = 1` | on | An altar is *guarded* if enemies were seen within 6 tiles of it in the last 15 rounds. If the carrier's altar is guarded and it has fewer allies within 6 than there are guards: (1) bank at an unguarded altar at most 25 tiles farther (new `World::altar_field_at`), else (2) rally on the nearest visible ally for at most 30 rounds per trip, then go in anyway. Off on sealed or gated altars, near the end of the game, or when the bag wins. |
| v51b: `guard_n = 2` + `monolith_economy()` | v51b only | v50k4's two altar guards, **only** on maps where every gem comes from at most two monolith groups and there are 2+ altars (of the 86 maps: `00contest`). |

## Local results (engine 2.0.0, cambc 4.0.0, all 86 maps, both sides, deterministic)
| Test | Games | Result |
|---|---|---|
| v51a vs v50h5e (mirror) | 172 | **91-81 (52.9% of decided)**, gem margin −2; deaths 3.6 vs 4.0; unconverted gems 59 vs 64; zero-bank 5 vs 5 |
| v50h5e vs v50k4 (2-guard bot), baseline | 172 | 148-24 (86.0%); loses 00contest from both sides |
| v51b on 00contest vs v50h5e / v50k4 / v50p1, both sides | 6 | **5 of 6 won** (v50h5e lost both contest games vs v50k4) |
| v51a vs v50p1 (early pack), v50h5e vs v50p1, v51a vs v50k4 | 172 each | running, see the PR |

Reading:
- The mirror is +10 wins with fewer deaths. It is under the 55% mirror gate, so on its own this is "no regression" evidence, not proof of a gain.
- **Our local altar-guard bot does not reproduce the top ten.** The live bot banks 937 a game against it with only 4 zero-bank games in 172, compared with 5 of 50 against the real top ten. The local tiers cannot show the zero-bank fix. As `results/zero-bank-2026-11` already says, only the `t10_226` panel can (metrics: games with 0 banked, baseline 5/50; mean banked, baseline 382).
- `03homonoliths` is decided by side (side B wins in every pairing, including v50h5e vs v50k4). It is the separate #60 stall, so v51b's guards are switched off there.

## To do before deploying (needs the account and a LIVE_SLOT window)
1. `t10_226` top-ten panel: v51b vs v226 (pinned opponents). Gate: fewer zero-bank games and higher mean banked, with wins not worse.
2. Strong panels 1 and 2 (40 games), per TESTING.md section 5.
3. Ablate if positive: v51a with `guard_aware 0` (cap only) vs v51a, to see which half carries the effect.

Tool: `tools/lab/bankstats.py BOT DIR...` (wins, banked, collected, zero-bank games, deaths, unconverted gems per game).
