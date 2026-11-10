# Why we lose to the top 10, and what to build (10 Nov 2026)

Data: today's pinned top-10 panel `t10b_240` (live bot 240 = `bots/v53x`, 50 games, 3 wins; opponents: stellar best girl,
Mite, Intercontinental Fish, BattleCats, test4, Ad Astra, Trzy Kwaterki, Univardisty, NEETCoders, caterpillow), cross-checked on the UK
panel `uk_x` (same bot, 45 games, 12 wins). Engine 3.0.0. Every number below comes from the official match summaries stored in
`results/panel/summaries/` and is reproduced by `python3 -I tools/top10gap/gap.py t10b_240 uk_x` (full output in `gap_output.txt`).
Local tests: `cambc` 5.0.1, 128 maps x 2 sides, `tools/lab/mirror.sh`.

## 1. The losses in numbers (top-10 panel, per game, us / them)
| | us | them |
|---|---|---|
| earned gold r25 / r100 / r200 / r500 | 14 / 231 / 566 / 1,688 | 31 / 437 / 1,014 / 3,274 |
| kills / deaths / assists | **0.8 / 9.8** / 1.5 | **9.5 / 1.9** / 18.4 |
| camp clears (own third / middle / enemy third) | 25.5 / **14.8** / 1.1 | 27.0 / **29.6** / 3.9 |
| gems collected / banked / lost | 511 / 373 / 89 | 1,089 / 1,019 / 18 |
| monster damage | 69K | 109K |
| healing done | 0 | 3,720 (Willow 12.4K a game when fielded) |
| teleport crystals bought | **0** | **5.9** (half the games; wall, water and corridor maps) |

- **Ahead on gold at r200 in only 8 of 50 games.** The gap is 2x from round 25 onward and is the same in every opponent but Mite.
- **98% of our deaths are to champions** (477 of 488). **90% happen in the middle (222) or our own third (220)**, and only 46 in theirs.
  They are mostly **one at a time**: of 401 groups of deaths within 10 rounds, 323 are single deaths. 70% of the dead carry no gems.
- **Same champion, different result.** Their Marcella: 4.1 kills, 0.3 deaths, 2,339 gold a game. Ours: 0.3 kills, 2.4 deaths, 843 gold.
  Their Heart: 1.9 / 0.3 / 1,024. Ours: 0.2 / 2.1 / 823. Their Vendetta: 1.5 / 0.4. Ours: 0.1 / 1.8. **The draft is not the whole story.**
- **Vesper Vale is their engine.** She takes 3,756 gold a game (the funnel), gets 3.6 kills and 0.1 deaths, and is credited with 137 of our 488 deaths (28%).
- Per opponent, 9 of 10 beat us through the kill war (our deaths 6.6 to 15.2 a game, theirs 0.2 to 5.0). **Mite is the exception**:
  it beats us on economy alone (2.2 deaths for us, 1.4 for them), and it is where we won 2 of 5.
- UK panel, same bot: the same shape, but smaller. Gold at r200 is 675 vs 848, deaths 7.5 vs 3.7, kills 2.0 vs 7.0, 12 of 45 won.
  The UK teams also buy crystals: bentheboss bought 130 in 5 games, Claudus Maximus 91.

## 2. Why: what they do that we do not
1. **They win the middle as a group.** They take twice our middle captures (29.6 vs 14.8) and kill us there and on our side.
   Our champions reach the middle one by one and meet 2 to 4 of theirs. This matches `results/54-mass-death-losses` and
   `results/unit-coordination-2026-11`: we are alone in 31-38% of rounds, their supports in 11-13%.
2. **They convert contact into kills, and we feed.** Each of our deaths pays them 100 gold, costs us 60 rounds of respawn plus the walk back,
   and drops the bag. 9.5 kills is about 950 of their 7,119 gold. Their items then out-scale ours, which makes the next fight worse (the snowball).
3. **They have a carry and sustain; we have five solo melee farmers.** They field a ranged gold carry (Vesper), grouped
   supports (Cassi & Issac, Willow's healing) and Heart's shields. Our five are all range 1 and none of them heals.
4. **They move better.** They buy about 6 teleport crystals a game, flashing 3 tiles over walls after a 3-round channel, on exactly the maps
   where our walks are long. We never buy one: the code exists (`tp_shortcut_margin`) but is off and was never tested.
5. Our first bank comes later (median r115 vs r106) and is smaller: 28 vs 37 gems per tribute, 13 vs 28 tributes a game.

## 3. Implementation strategy (what to build, without overfitting)
Rules: a feature may key only on things the bot measures in-game (terrain, walking distance, spawn distance, enemies seen, deaths so far).
Never key on map names or team names: qualifier maps are unseen. Each feature gets its own flag, its own folder, and one test at a time.

| Priority | Feature | Gap it closes | General trigger | Fair local test | Decisive test |
|---|---|---|---|---|---|
| 1 | **Carry plus roles** (the v60/v61 line on `claude/admiring-franklin-y3jf7g`: Vesper funnel, ranged kiting, capture handoff) | 3, 2 | team size and kit, not map | self-play is the wrong judge (TESTING section 3) | UK and top-10 panels; **in progress in the other session (v61b UK panel, 10 Nov)** |
| 2 | **Contested-middle play as a group**: the first middle target is taken with the nearest ally, and a farmer alone in the middle with enemies seen nearby leaves before contact | 1, 2 | enemies seen near the target, ally distance | early-pack bot `v50p1`; deaths must fall at least 10% and wins rise | panels |
| 3 | **Adaptive caution**: tighten fight and retreat thresholds only once this game shows we are losing fights (built: `v62care1`) | 2 | team deaths in the last 150 rounds | `v50p1` plus the plain mirror | panels (caution only shows on real opponents: v226) |
| 4 | **Teleport-crystal shortcuts, bought only when useful** (built: `v62tp3`) | 4 | walking distance vs a 3-tile flash, measured per trip | the plain mirror is valid (economy and pathing) | ranked check while live |
| 5 | Bank smaller bags earlier when enemies are near, so less is lost per death | 5 | bag size, visible enemies | mirror plus `v50p1` | panels |

Order of work: (1) is the biggest lever and is owned by the other session. (2) is the next design to build here. (3) and (4) are built and measured below.

## 4. Candidates built today (each is v53x plus one flagged change)
| Bot | Change | vs live v53x (256 games) | vs early pack v50p1 (256) | kills / deaths vs v53x | Verdict |
|---|---|---|---|---|---|
| (reference) `v53x` | live 240 | | 185-71 (72.3%), deaths 5.57 | | |
| `v62care1` | careful mode: 3 team deaths in 150 rounds give hazard 0.12, fight margin 1.0, recall at 60% and a territory penalty of 1.0 until the window clears | 126-130 (49.2%), margin 0 | 182-74 (71.1%), deaths 5.64 | 3.82 / 3.99 vs 3.49 / 4.32 | **fails the v50p1 gate** (no fall in deaths); neutral in the mirror |
| `v62care2` | diagnostic: careful from the first death on | not run | 171-85 (66.8%), deaths 5.13 | | deaths -8%, wins -5.5 points: caution trades farming for survival |
| `v62tp1` | crystal shortcuts on camp trips (`tp_shortcut_margin 3`), one crystal always in stock | 120-136 (46.9%), -37 | | 3.38 / 4.11 vs 3.73 / 3.80 | rejected: crystal maps 16-12, other maps 104-124 (the 10 gold spent at round 0 everywhere) |
| `v62tp2` | `v62tp1` plus shortcuts on bank trips | 120-136 (46.9%), -44 | | 3.39 / 4.15 vs 3.76 / 3.80 | rejected |
| `v62tp3` | `v62tp2` plus lazy buying: a crystal is bought only after a qualifying shortcut was met without one | **130-126 (50.8%), +32** | 185-71 (72.3%), deaths 5.64 | **3.76 / 3.87 vs 3.38 / 4.27** | positive but within noise (about +-8 wins); 1.8 crystals a game on 45 maps; on maps with 4 or more crystal buys 30-24, elsewhere 100-102 |

All runs: 0 bot faults, smoke clean (02the-pack, 01islands, 01starvation, 00great-wall). By map family (`00/01/02/03/04/adgato`), `v62tp3` vs v53x
is 36-36, 18-12, 15-15, 17-13, **38-46**, 6-4. The 04 family's -8 is about one standard error; check it on the transformed maps before shipping.

**Neither candidate passes the local gates in TESTING.md**: more than 55% of decided games in the mirror for economy, and +win share with -10% deaths
against `v50p1` for caution. This is consistent with every earlier study: the local opponents cannot reproduce what the top teams do to us
(we beat `v50p1` 72% while losing 47 of 50 to the real top 10).

## 5. How to test next (as TESTING.md lays out)
1. Local, no account: `export PROJ=/root/lab JOBS=4; tools/lab/mirror.sh CAND v53x` and `tools/lab/mirror.sh CAND v50p1`,
   then `tools/lab/mirror_kd.py`. Unseen-map check on `/root/lab/xmaps.txt` (transformed copies, `tools/replay/mapxform55.mjs`); not run here,
   because the visualiser assets need a signed-in `cambc view`.
2. Real opponents (needs `cambc login`, a `LIVE_SLOT.md` booking and **Leke's approval**; the other session holds the slot right now for v61b):
   ```
   tools/lab/submit_wait.sh bots/v62tp3                     # prints the new version N once it is live
   tools/lab/panel_run.sh tools/panel/panel_top10b.json t10b_tp3 N t10b_240
   tools/lab/panel_run.sh tools/panel/panel_uk.json uk_tp3 N uk_i
   python3 -I tools/panel/panel.py compare t10b_240 t10b_tp3
   tools/lab/activate_wait.sh 240                           # unless it passes: +4 wins, deaths not worse
   ```
   Use the same commands for `v62care1`. Caution changes have only ever shown up on real panels (v226: 22/40 vs 15/40).
3. **Deadline: the UK qualifier lock is today, 10 Nov, and the exact hour is unconfirmed.** Nothing here should go live without a panel. The safe
   default is to keep 240 unless the other session's v61b passes its UK panel.

## 6. Update (evening, 10 Nov): decoded replays revise the diagnosis
All 50 `t10b_240` replays plus our bot's stdout were downloaded (`cambc matches download`) and decoded (`tools/replay/extract5.mjs`).
Scripts: `tools/top10gap/{deathlog,decdeaths,fights,escape}.py`; outputs `*_output.txt` here.

- **Not an information problem.** Our bot's death log: in 438 of 488 deaths an enemy was in view 8+ turns earlier. In 266 the
  fight simulation already predicted a loss at first sight.
- **Not mainly numbers.** First contact (median r66, 47 of 49 in the middle): we were outnumbered in 12 games, even in 20, ahead in 17.
  In fights where we had more champions involved we still lost 83 champions to 5.
- **Deaths are far more lopsided than damage.** Before r150 we take 1.33x the damage we deal but lose 72 champions to 13. The ratio grows to
  2.5x after r600 (the item snowball).
- **The hurt champion is the difference.** Below 35% health with an enemy within 5: we die within 15 rounds 62% of the time (649 cases),
  they die 14% (267). Three rounds later 11% of ours are 6+ tiles clear (theirs 33%). A teammate is within 3 tiles 36% of the time (theirs 63%).
- **Range.** All our champions have attack range 1, while 43% of their slots have range 3. In 268 of our deaths no enemy was adjacent in the last
  logged turns, and 330 had a ranged enemy within 6.

### Candidate v66s (on the live 245 = v61j): save the hurt champion
- Arm A (`ranged_leave_hp 0.6`): a melee champion that isn't winning, with a ranged enemy within 5, disengages below 60% health and retreats towards
  the nearest healthy ally within 10.
- Arm B (`rescue_radius 5`, the v57a rescue): join to protect an ally below 60% in contact when the simulation says it's at least an even trade.

| Run (256 games) | wins | deaths cand / opp |
|---|---|---|
| v66s vs live v61j | 128-128, margin +28 | **3.62 / 4.04** (kills 3.62 / 3.25) |
| v61j vs early pack v50p1 | 201-55 | 4.95 |
| v66s / v66a / v66b vs v50p1 | 198-58 / 202-54 / 196-60 | 5.08 / 5.01 / 5.09 |
| v61j vs Vesper bot v60g | 176-80 | 3.25 |
| v66s / v66a vs v60g | 172-84 / 174-82 | 3.20 / 3.27 |

Arm A only triggers against ranged enemies. v50p1 and v61j field none, and v60g has one weak Vesper, so **no local opponent exercises it**.
Locally v66s is a no-regression change (equal wins, fewer deaths against the live bot). Whether it helps can only be shown on the panels.

## Limits
- Zones use each team's most common shop tile as home. That is a proxy for the spawn, and mirrored maps make it symmetric.
- Kill credit, assists and gold come from summary events. Positions of the other champions at a death are not in the summaries, so
  "one at a time" is measured as deaths of ours within 10 rounds of each other, not as local numbers.
- Opponents' crystal *uses* are not in the summaries, only buys. Whether they flash for travel or for escape needs decoded replays.
- 50 + 45 games against pinned versions; per-opponent rows are 5 games each.
