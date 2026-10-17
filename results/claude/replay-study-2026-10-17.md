# Replay study: 20 top-team matches (17 Oct)

Source: 20 replays Leke downloaded from the platform, covering 15 of the 17 ladder maps. They were decoded with `tools/replay/` (see its README). The raw per-team rows are in `replay_teams_2026-10-17.json`. Polaris does not appear to be in these games: no team drafts the v12c six-pick, which includes Prism. So the comparison here is **winner vs loser** among top teams.

## 1. Winners capture more camps, and mostly alone
| | Captures per game | Champions present per capture | Share of captures by one champion |
|---|---|---|---|
| Winners | **32.0** | 1.5 | 66% |
| Losers | 20.5 | 1.5 | 60% |

When the game is decided on farming, solo is the norm for the winner. On rows, the winners' captures were 94% and 100% solo. Monolith a5c6 was 73% and monolith 81c0 was 96%. Corners was 77%.

On rows (c67c7b39), the winner soloed the 3-camp group (4050 HP, 66 gems) at **round 28 with Varg holding no items**. It lost 4% HP doing so. Ren, Stellar, Issac and Cassi did the same thing later.

## 2. Camps hurt far less than v12c assumes
`tools/replay/solo.py` measures every solo capture: the HP lost while the champion stood next to the group, divided by (summed camp strength × rounds spent there).

| Group | n | Mean HP lost | Worst | Rounds | Lost per (strength·round) |
|---|---|---|---|---|---|
| 1 camp, 1350 HP, strength 20 | 90 | 12% | 62% | 18 | ≈0.33 |
| 1 camp, 2400 HP, strength 60 | 27 | 19% | 56% | 17 | ≈0.20 |
| 2 camps, 2700 HP | 82 | 15% | 74% | 20 | ≈0.17 |
| 3 camps, 4050 HP, strength 60 | 42 | 17% | 64% | 19 | ≈0.13 |
| 4 camps, 2000 HP | 26 | 4% | 55% | 16 | small |

v12c `solo_target()` rejects a group when `g.str*clear*.6 > my_hp*.6`. That uses a **coefficient of 1.0**, which is 3x too high for one camp and about 7x too high for three. `init()` also forces `pack_mode` on every gem map with 4 or more champions. Together these explain the farming gap in NOTES ("Our solo camp-safety check probably rejects the 22–36 gem camps that top teams solo"). It also explains why v12j ("just split") did not help: the champions were split up, but the check still turned down the camps.

## 3. Item builds: Health and Power, not Monster
Teams that opened with Monster shards or emblems went **2–9** in batch 1 (3–9 including batch 2). Winners' frontliners (Ren, Ryth, sometimes Issac) typically buy a **Durability shard of Health, then the Bruiser emblem of Health** between rounds 25 and 60. Carries open on **Power** (Stellar Power of Focus; Issac/Varg Power of Strength). Jungle is common on the winning side on swirl, eight and ambush.

v12c's `shop()` already contains this build (`B` and `D`). It is switched off with `(void)B;(void)D;` and `order={M,P,P,DS}`. The W7 test was Jungle-first, not this build.

## 4. Deaths decide most of the lopsided games
| | Deaths | Gems lost on death | In own half | No enemy within 5 (killed by camps) |
|---|---|---|---|---|
| Winners | 68 | 278 | 41 | 24 |
| Losers | 312 | 1404 | **263** | **89** |

Two contest games account for 129 of the losers' deaths. Even without them, losers die about 3x as often. Most of their deaths come from invaders on their own side, in fights where they were outnumbered by at most one (244/312). Winners simply have more effective HP and DPS from their items, which ties back to point 3.

## 5. Other observations
- **Tributes:** winners average 45–80 gems per trip; several losers average about 22 (one trip per camp). Submitting takes 0.1 round per gem with no base cost (`submit_gem_base_duration=0`), so many small trips only cost walking. v12c's `carry` threshold (60–140) is already in the winners' range.
- **Recall:** winners recall 20–40 times per game, as a free heal and shop (`recall_time=5`, `spawn_healing=1`).
- **Wards:** both sides place 25–100. The one team spamming more than 300 (Cassi/Stellar/Tavi/Varg) lost all 5 of its games, so ward count by itself is not what makes a team strong.
- **Altar locks and teleport crystals:** almost unused. There was 1 lock in 20 games and teleports in one game, so they are not worth time before the freeze.
- **Contest:** both winners held all gems until the monolith, which gave 5 tributes of 200. The win came from gold, items and kills (57–6 and 45–2), with captures at 76–79 against 35–66.

## Batch 2: corners 2fdff147 (1142–784, 587 rounds)
This was a close game that was decided at the end. The loser led from round 100 to 300 (138–44 at r100), and it was 800–740 at r550.
- **Farming:** captures were 34 against 33. The winner's captures were 82% solo, and it spread wide (mean distance between champions 17.3, about 4 separate groups). The loser played as a pack (spread 9.6, all 6 champions on one camp at r64). The pack's early lead disappeared by r350.
- **Closing out:** the winner's Ryth **carried 176 gems from about r520 to r587**. It stayed back while the enemy held the central altar. Once the enemy Stellar was killed and the rest of that team recalled, it **locked the altar and banked it all** (lock at r568, +176 at r587). The other two carriers banked at the corner altar (1,69) at the same moment. That made 342 gems in 6 rounds.
- **Altar locks:** the winner used 4 and the loser 11. Both used them the same way: place a lock on the contested central altar 1–3 rounds before banking there. Volume did not decide the game; timing at the end did.
- **Items:** the winner opened Monster and the loser opened Jungle. This is a counterexample, and Monster openers are now **3–9** across 21 games.
- **Solo damage:** the measurements match batch 1. 1-camp groups cost 12% HP on average (n=31) and 2400 HP singles cost 22% (n=17).

## Engine constants (from the wasm, SDK 2.2.4)
capture 5, camp sleep 2, respawn 60, recall 5, submit 0.1 per gem (minimum 1, base 0), kill gold 50, assist gold 0, shard cost 30, emblem 150 (5 shards), teleport crystal 10, altar lock 10 (3 hits), ward vision 6, ward placement 2, 1 active ward.
