# Public repositories, second review (8 Nov 2026)

Repository names are not given here (`TESTING.md` rule 8). All material is third-party and unverified; it was read as text and nothing was run.

## Engine check
- Installed `cambc` was 4.0.0; latest on PyPI is **5.0.0** (engine 3.0.0, patch 4.0.0). Upgraded the default CLI to 5.0.0 and re-ran a game as a sanity check (same result as in the 5.0.0 side environment).
- The platform's newest patch note is still Patch 4.0.0 (4 Nov 23:08 UTC). No newer patch, and no new announcement since 3 Nov.
- Repositories read on 3 Nov (top-20 scouting, fight-model lab, small experiments log, LLM patch loop): no new commits since.

## Newly updated repositories (pushed 1 to 7 Nov) and what they add
| Source | What it is | Useful for us |
|---|---|---|
| Qualifier post-mortem (Team HBH, Round of 32 of 830 in the International Qualifier) | 5-week write-up, 47 versions logged with outcomes | Paired testing on **unseen maps**; fuel makes games chaotic (a no-code rebuild flipped 36-38% of results); a bundle that looked fine locally went **4-21 on the ladder** and was rolled back in 70 minutes; builds that died less but did not win more were not shipped; **heavy work moved into the draft turn's larger fuel budget**; teamwork packed into the 8 shared bytes plus **the low bits of each champion's priority integer**; carry cap and carry order (Vesper > Heart of Ruin > Vendetta); `fight_d 4` (start a fight only when the nearest enemy is within 4 tiles, was 6) gave +0.104 +- 0.031 win share on 700 held-out pairs |
| Long-running team bot (ladder #182, rating 1,749 at the sprint 3 lock) | per-version summaries v1-v41 and a sprint report | Tournaments (sprint 3 was single elimination, 15 games per match) are played on **maps outside the ladder pool**; near equilibrium every bot wins about half and short ranked windows cannot separate bots; a fuel cache cut fuel-exhausted turns from 17.5 to 6.3 a game and was the version that held; they bank 30 small bags a game (median 17) and bigger bags lost locally |
| Solo bot (reached #24 on 19 Oct, 1,941 Elo) | research archive | A research-first rewrite never produced a validated replacement before the lock, and the entry fell back to the old bot: avoid big rewrites, ship flagged increments |
| Autonomous-loop bot (rank 124, 1,880) | analysis suite and bot notes | Pairing champions before round 300 removes isolated-champion pickoffs (matches our lone-carrier deaths); fixing fuel exhaustion in the target scorer lifted the win rate on large corridor maps from 2/24 to 20/24 (compare our `03the-front`, `03colosseum`, `02the-pack` fuel spikes) |
| Distributed "worker" repositories and browser userscripts | not read | Skipped on purpose (they run code or ask to be installed). |

## What is unused in our bot (checked in the SDK and in `bots/v50h5e`)
- **Draft memory**: 1,024 bytes written in the draft turn (10x fuel), read-only for champions. Our bot writes none. Candidate use: a precomputed opening plan (first target per champion, altar choice, map class) so the first turns cost no fuel and the plan can search far more than a turn allows.
- **Priority integer**: `set_priority(int32)` persists, and `query_priority()` reads it for any **visible** champion. Our bot never sets it. It is a 32-bit channel per champion, but only visible allies can read it, so it adds little beyond what nearby allies already see; the 8 shared bytes remain the only global channel.
- Our `share_sightings` setting is off (`config.h`); the priority channel would not collide with the shared tail bytes used by `group_news`.

## Schedule and format facts (platform tournaments feed, checked 8 Nov)
- The feed lists only finished events: Sprints 1 to 3 and the International Qualifiers.
- **International Qualifiers: double elimination, 21 games per match, seeded by the ladder at the lock time (3 Nov 23:59), 504 entrants.** We were not in it (our teams' qualifications are Sprints 1 to 3 only).
- The UK qualifier is not in the feed yet. Our notes say event 11 Nov and lock 10 Nov; **the exact lock hour is unconfirmed.** The version live at the lock is what plays.

## Recommendations
1. **Decide the lock-time bot now** (issue #71): the live slot is free and the lock is about two days away. A real-opponent panel for v51d on engine 3 takes about 90 minutes.
2. Judge anything new on held-out maps and real opponents, not on the ladder pool or the local mirror (every source agrees).
3. Ranked next experiments: opening plan in draft memory (research), `fight_d`-style engagement radius (cheap flag, panel only), champion pairing before round 300 (matches our #54/#66/#67 threads), fuel work on the three heaviest maps.
