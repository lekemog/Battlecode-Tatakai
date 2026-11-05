# Public-repository insights, checked against our own games (5 Nov 2026)

Four public repositories for this game (2026a) were read as text only (nothing built or run; third-party claims unverified; repository names are not given here, per `TESTING.md` rule 8): a top-20 scouting repo with 1,040 ranked summaries, a lab repo with fight-model and top-10 scouting notes, a small experiments repo and an LLM bot-evolution repo. Rather than adopt claims, each was tested on our 100 real games against the top 10 (`results/panel/summaries`, `tools/lab/census.py`).

## 1. Where we differ from the top 10 (100 games, same metrics as the public census)
| | us | top-10 opponents | public top-20 range |
|---|---|---|---|
| gems collected / game | 642 | 1,180 | |
| gems banked / game | 387 | 999 | 690-850 |
| tributes / game, mean size | 12 @ 37 | 33 @ 43 | mean 18-56 |
| first tribute round (median) | 132 | 92 | 44-87 in the scouting notes |
| gem loss share | 26% | 2% | 5-24% |
| earned gold / game | 4,232 | 7,106 | |
| group captures / game | 46 | 59 | |
| champion damage / game | 13.0k | 28.5k | |
| camp damage / game | 90k | 110k | |
| deaths / kills per game | 10.9 / 1.1 | 2.5 / 10.6 | |
| kills before round 200 | 0.15 | 1.50 | |
| wards placed | **370** | 166 | 100-200 |
Full output: `census_us_vs_top10.txt`. (The single-recipient capture metric came out 1.00 for both sides, a counting artifact of the event format; discard it.)
Reading: collecting volume is the biggest gap (-46%), conversion second (60% of collected gems banked vs 85%), and early kills/deaths third. Wards are not a gap.

## 2. Item builds (shards bought per game, 100 games)
Families: we buy only Bruiser 85, Prospector 20, Durability 17, Jungle 12. They buy Bruiser 99, Power 13.5, Greed 9.7, Monster 12.4, Capture 9.8, Treasure 7.1, Jungle 15, Durability 16, Prospector 13, Hunter 4.6, Collectors 4.4. By stat: Strength 73 vs 76 (equal), **Health 78 vs 31, Focus 61 vs 27**.
Per champion (us | top 10): **Marcella** Bruiser Strength 19.7 | 0.1, Bruiser **Focus** 0 | 24.1, Bruiser Health 3.6 | 12.3. **Ryth** Strength 16.1 | 0.7, Health 3.1 | 6.5. **Heart of Ruin** Focus 19.6 | 5.9, Health 3.4 | 6.8. **Vendetta** Strength 10.1 | 13.0, Health 2.7 | 6.4. **Varg** Bruiser Strength 11.9 | 0.3, Power Strength 0 | 6.2.
Public data agrees (top-20 census: Marcella Bruiser Focus 4,814 > Health 4,348 > Strength 3,302 purchases; 18 of 20 teams habitually Bruiser-family; Health and Focus majorities more common than ours).
History: health-heavy builds for everyone were tried before (v25c, v25y; no gain on old lines, tiny scrim samples) and a Ryth tank build was kept. **Marcella on Focus was never tried.**

## 3. Other findings from the repositories
| Finding | Source type | Check / action |
|---|---|---|
| Rewards split between allies standing on the capture; top teams use one recipient 89-98% | census | Total team gold is conserved, so concentration shifts items to one carry (carry share 0.41-0.56 vs ours 0.39). Not tested; our `carrier_capture` flag exists, off. |
| Low carried-gem loss (<=15% of banked) goes with a 67% win rate; "small tributes (<25 mean)" goes with 35% | census | Correlational. Supports banking at 30-45 gems, not smaller; our danger-bag setting of 20 sits at the edge. |
| 3+ kills before round 200: 80% win rate | census | We average 0.15 early kills. Needs the opening study (#56). |
| Wards in 20 of 20 teams | census | We already place 2x the top 10. No action. |
| Graded bank thresholds: 30 anywhere, 15 within 15 tiles, 5 within 4; lower when threatened | a peer bot | Matches v51d (cap 40, danger 20, ring window). |
| A duel/fight win model: hero pair alone predicts 82% of duel winners; health/distance features matter in team fights; duel-only training fails in team fights | lab repo | Hero-pair matchup prior is a cheap addition to the fight verdict (untested). |
| Fuel is 100K per turn and tight | lab repo | Matches our profile (`results/52-code-efficiency`). |
| Locked-altar dead end (no delivery goal when every nearby altar is enemy-locked) | experiments repo | Ours attacks a lock within reach; not reproduced. |
| LLM-written patch loop with paired benchmarks | LLM-evolution repo | Process idea only: it validates the paired-test discipline we already use. Not adopted. |

## 4. Candidates built (flags on top of v51d; local, engine 2.0.0, 86 maps x 2 sides)
| | vs live bot (172) | vs v50p1 early pack (172) | bot faults |
|---|---|---|---|
| v51d (reference) | 90-82 (52.3%) | 122 (70.9%) | 0 |
| **v51e1** = v51d + Marcella on Focus (`marcella_focus`) | **103-69 (59.9%)**, margin +103, banked 856/game, deaths 3.8 | **128 (74.4%)**, margin +300 | 0 |
| v51e2 = v51d + Bruiser Health mix (`health_mix` 1) | 93-79 (54.1%) | 123 (71.5%) | 0 |
v51e1 is above the team's 55% mirror gate and 20 wins over the live bot on the early-pack stress opponent (108); smoke clean on six maps; `03the-front` 3 of 4 (one loss by 4 rounds). v51e2 is inside noise of v51d.
Caveats: local opponents are copies of our own strategy; item changes shift fuel use only slightly; the effect of Focus on a real top team (which kills Marcella more often) is untested. `v51e1` is `v51d` plus one flag.

## 5. To do
1. Top-10 panel for v51e1 (pin `t10_226`; bar +4 wins, deaths not worse). Needs a LIVE_SLOT window.
2. If it passes, test v51e1 + `health_mix` and the Ryth/Vendetta Health ratio separately.
3. Test `carrier_capture` (single recipient) as its own change.
4. Open (not a result of this work): on `03the-front` side B vs v50p1, all candidate versions still end at the round limit rather than banking out.
