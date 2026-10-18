# How top teams win contest and eight: winner vs loser (Kurians' Claude, 18 Oct)

**Data:** every contest and eight game in `top-replays/` (10 per map, top-20 vs top-20). Decoded with `tools/replay/extract.mjs`; the hashed engine-file fix is on branch `kurians/top-openings`. Analysed with `tools/openings.py MAP DIR`.

**Caveats:**
- 10 games per map.
- Top-vs-top only, so these are correlations, not causes.
- Zones use each tile's distance to the two spawn centroids (thirds).

## Contest (10 games)
| Measure | Winners | Losers |
|---|---|---|
| Gold earned r50 / r100 / r150 | 178 / **411** / **702** | 160 / 253 / 334 |
| Items owned r100 / r150 | 5.1 / **8.7** | 4.8 / 5.6 |
| Deaths by r150 | **2.0** | 4.1 |
| Champion-time in the middle third, r0–150 | **71%** | 59% |
| Champion-time in the enemy third, r0–150 | 0% | 0% |
| First tribute (monolith gems) | r1210 | r1594 (5 of 10 never) |

- Nobody banks anything before about round 800.
- Level at r50, then the winners earn **2.1× the gold by r150**.
- **Nobody invades:** both sides stay out of the enemy third.
- Winners hold the middle more and die half as often.
- Drafts are nearly identical (Stellar, Cassi & Issac in almost every game). Winners lean slightly towards Tavi, Ryth and Prism; losers towards Varg and Willow.

## Eight (10 games)
| Measure | Winners | Losers |
|---|---|---|
| First tribute | **r101** | r152 |
| Banked r150 / r300 / r600 | **117 / 402 / 953** | 51 / 90 / 270 |
| Gold earned r50 / r100 / r150 | 162 / **512** / **856** | **208** / 337 / 540 |
| Items owned r100 / r150 | **7.9** / 9.4 | 5.2 / 7.2 |
| Deaths by r150 | **1.3** | 3.0 |
| Middle third, r0–150 | 44% | 44% |
| Enemy third, r0–150 | 1% | 3% |

- **Losers are ahead on gold at r50, but winners lead by r100 and keep it.** The swing happens between r50 and r100.
- Winners bank about 50 rounds earlier and convert continuously. By r300 they have 4.5× the losers' banked gems.
- Winners don't invade more. The losers spend slightly *more* time in the enemy third, and die more.
- Drafts are almost the same on both sides.

## What this suggests for our bot (hypotheses to test, not conclusions)
1. **Contest:** winning is about earning gold safely in the middle third during r50–150 without dying, not about sieging early. Our ladder notes show we die about 50 times per contest game. Our bot's r150 gold and deaths on contest against these numbers would show how big our gap is.
2. **Eight:** the r50→r100 window decides it, with the first bank around r100 and steady small banks after. That matches #18 (we lose bags while carrying them). Our first tribute and banked gems at r300 on eight, against 101 / 402, would size the gap.
3. **Raiding/invading is not how top teams win these maps.** That's relevant to v18f's raid mode.

## Per-game detail
Run `python tools/openings.py contest DIR` and `python tools/openings.py eight DIR` (match IDs are printed for every game).
