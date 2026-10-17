# Champion compositions and meta — evidence inspected 18 October 2026

## Finding

The strongest evidenced general five-pick **baseline candidate** is **Cassi & Issac, Stellar, Ren, Ryth, Varg**. Fish and procless both use it. This is a useful baseline, not a proven optimal draft. A separate control composition deserves testing on contested objectives: **Cassi & Issac, Stellar, Tavi, Prism, Ryth** (Mite), compared with **Ren replacing Ryth** (Fish).

The most consistent observed core is **Cassi & Issac + Stellar**. Prioritize correct execution of that core and map-dependent remaining picks. Do not replace a working implementation merely because a champion is popular.

## Scope and reproducibility

This synthesis reuses 17 detailed match summaries collected on 17 October: 12 from the top-team study and 5 from the Mite–Fish study. These yield 34 team-game lineups across five teams: Intercontinental Fish, Mite, procless, Sneaky Bush Campers and AlphaSlop. Fish appears in every game. The 17 summary hashes are distinct. This is a convenience sample, not a ladder census or a controlled draft experiment.

Original evidence:
- [Top-team data, immutable commit](https://github.com/lekemog/BattlecodeConversation/blob/33dda638b5d6835f8a30d826d721417af5b5d593/results/chatgpt/top50-evidence-2026-10-17.json).
- [Mite–Fish data, immutable commit](https://github.com/lekemog/BattlecodeConversation/blob/3456b2ca328a2886b6f6a33c8cce4e47a64772bb/results/chatgpt/mite-fish-evidence-2026-10-17.json).
- All original runtime drafts contain Cassi and Issac as separate bodies. Here they count as **one pick**. Draft arrays do not establish selection order.
- The historical rank snapshot put Fish first, Mite second and procless fifth; these are dated observations, not newly verified live ranks.
- The later 15-game review has no detailed summaries/drafts and is excluded from this composition sample.
- Current ladder freshness could not be verified through web retrieval in this pass. Fresh Discord discussion was read directly through the authorized signed-in browser. Nothing was posted to Discord.

## Which champions recur?

| Pick | Lineups containing pick / 34 |
|---|---:|
| Stellar | 33 |
| Cassi & Issac | 32 |
| Ren | 28 |
| Varg | 20 |
| Ryth | 19 |
| Tavi | 14 |
| Prism | 7 |
| Willow | 3 |

Marcella, Vendetta and Vesper Vale were absent from these detailed lineups. Absence is not evidence they are weak. Counts combine different allowed team sizes and repeat opponents/versions. They measure this sample's usage, not independent win probabilities.

## Compositions worth carrying forward

| Purpose | Picks | Evidence and limit |
|---|---|---|
| General five-pick baseline | Cassi & Issac, Stellar, Ren, Ryth, Varg | Used by Fish and procless. Both wins and losses, including mirror drafts. |
| Contested-objective candidate | Cassi & Issac, Stellar, Tavi, Prism, Ryth | Mite beat Fish's Ren variant on contest and stampede in one series. Two maps, one matchup; composition advantage is unproven. |
| Alternative contested-objective candidate | Cassi & Issac, Stellar, Tavi, Prism, Ren | Fish beat Sneaky Bush Campers and AlphaSlop 1000–0 on contest, but lost to Mite. |
| Sustain variant | Cassi & Issac, Stellar, Tavi, Ren, Willow | AlphaSlop beat Fish on corners 1000–624 and lanes 1024–890. Willow causality cannot be isolated. |
| Three-pick baseline | Cassi & Issac, Stellar, Ren | Fish beat Sneaky Bush Campers 1068–330 on collision. Mite lost with this draft on expanse to Fish's Varg variant. |
| Three-pick farming alternative | Cassi & Issac, Stellar, Varg | Fish beat Mite 1008–862 on expanse. One game; not universally preferable to Ren. |

Allowed pick count comes from each match, not inferred from map area. Cassi & Issac yields two controlled bodies for one pick, with linked death risk.

## What the match evidence actually says

**Execution can decide mirror drafts without a kill.** On ambush, Fish and procless had exactly the general five-pick composition. Procless won 1022–668; neither side recorded a death. Source top-study group `80f7be78-d289-4c6d-a912-3b5c2daf95a5`, game 2. On monolith procless also beat the same Fish draft, while on elkring Fish beat procless. There is no draft-only explanation for the reversal.

**Control drafts can dominate fights but still need objective conversion.** Fish's Ren/Prism/Tavi lineup won two contest games 1000–0. Against Mite's Ryth replacement, however, contest ended 0–0 banked gems with Mite winning on the gold tiebreak: 17036–2496 earned gold, 4 versus 59 deaths. Match `dc1e8caa-6d05-4659-a03c-480944121696`. These gold figures are not solely farming income.

**Camp count alone is a poor strategy metric.** In the same series, Mite won stampede 1008–0 despite clearing 17 camps to Fish's 41. Match `8c39b253-1a32-4e49-a299-1d3fd50ea398`. Camp selection, reward value, routes and banking matter; this is not proof that fewer clears cause wins.

**Close banking races should not be credited to a champion swap.** Mite's four-pick Cassi & Issac/Ren/Ryth/Varg beat Fish's Cassi & Issac/Ren/Stellar/Varg 1012–990 on rows. Match `8fa203b5-2403-4869-8f7f-50ded297c094`. The prior event study identifies a last split and Ren's winning tribute; the 22-gem result does not isolate Ryth versus Stellar.

## Mechanistic interpretation — hypotheses to test

These roles follow the 17 October handbook snapshot and prior mechanics audit, not a newly verified patch:
- **Cassi & Issac:** two bodies, bags and action opportunities from one pick. Cassi supplies ranged burst/control; Issac supplies melee attacks, reset and dash. Protect both because either death kills the pair.
- **Stellar:** ranged burst and area damage support fast grouped-camp clears and focus fire. Normal walking conflicts with her spells/attacks; movement policy can erase her apparent paper advantage.
- **Varg:** splash basic attacks and an attack reset make grouped camps a natural assignment. Shielding may reduce recovery downtime. Strong farm role is plausible, not a measured universal superiority.
- **Ren:** stun, dash and retaliation provide chase, escape and frontline pressure.
- **Ryth:** durability and an area stun offer a different frontline/control package. The Mite series motivates an isolated Ren/Ryth experiment, not an automatic replacement.
- **Tavi / Prism:** additional stun/burst and area damage support contested fights. Tavi can buy shards away from spawn; consumables remain restricted. Prism's gem-dependent scaling creates a carry-versus-bank tradeoff.
- **Willow:** healing may extend time on the map, but could cost damage or farming speed. AlphaSlop's wins warrant a sustain test.

Do not hard-code MOBA roles such as permanent lanes, a single farm carry or healer merely by analogy to Dota/LoL. Transfer the measurable ideas: safe resource routes, burst timing, coordinated disables, vision, retreat thresholds and converting pressure into banked gems. Assess the marginal value of each pick under Battlecode's pick count, action rules and objective economy.

## Fresh Discord evidence and patch caveat

Read during this research pass on 18 October (Discord displays UK times):
- [General meta discussion, 17 October 23:49](https://discord.com/channels/1479274986203123883/1479277301417119785/1561149066484912199): Lawliet reports near-universal Stellar and Cassi & Issac usage in the teams being discussed. The scope of that observation is unclear; it is not an audited ladder-wide count. Their later claim that a simple Stellar/Cassi/Ren bot should reach 1600+ is speculation, and another participant says a similar approach has not reached that rating. Later in the same visible context, Lawliet describes Varg as strong at farming and against poor micro. Treat these as hypotheses.
- [Prism discussion, 17 October 20:55](https://discord.com/channels/1479274986203123883/1479277301417119785/1561105489931276413): participants discuss a future patch. The 1–2 Focus per gem number is explicitly a player's guess. It is **not a confirmed live change**.
- Current announcement and dev-updates channel views were checked. No inspected official message established a live Prism coefficient change. This does not prove no change exists elsewhere. Verify installed engine/SDK and authoritative patch notes before tuning coefficients.

Past winners' spring 2026 comments concern a different game; they cannot establish the autumn champion meta. See [past-winners history study](https://github.com/lekemog/BattlecodeConversation/pull/12) and [mechanics audit](https://github.com/lekemog/BattlecodeConversation/pull/11).

## Concrete evaluation recommendation

Keep a general baseline and compare **one slot at a time**: Ren↔Ryth in the control composition; Ren↔Varg in three-pick games; Willow versus the displaced pick in sustain candidates. Freeze engine version, bot source and item policy, and use both sides across multiple maps/opponents. Record wins plus banked/carried/lost gems, objective availability, gold, deaths, travel/recovery downtime and control/fuel failures. A draft swap is worthwhile only if its gains survive broader matchups and do not merely exploit one opponent.

This report triggers no runs, scrims, ladder submissions or bot edits.

## Complete normalized observations

W/L is the observed game outcome, including the contest gold tiebreak. Source “top” identifies group/game fields in the top-team evidence; source “mite” identifies match IDs in the Mite–Fish evidence.

| Source | Map | Team | Picks | Result | Banked gems |
|---|---|---|---|---|---:|
| top | pilgrimage | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar, Varg | L | 796 |
| top | pilgrimage | Mite | Cassi & Issac, Ren, Stellar, Tavi, Varg | W | 1008 |
| top | monolith | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar, Varg | L | 886 |
| top | monolith | procless | Cassi & Issac, Ren, Ryth, Stellar, Varg | W | 1010 |
| top | eight | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar, Varg | W | 1020 |
| top | eight | Mite | Cassi & Issac, Ryth, Stellar, Tavi, Varg | L | 0 |
| top | collision | Sneaky Bush Campers | Ren, Stellar, Tavi | L | 330 |
| top | collision | Intercontinental Fish | Cassi & Issac, Ren, Stellar | W | 1068 |
| top | swirl | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar | W | 1116 |
| top | swirl | Mite | Cassi & Issac, Ryth, Stellar, Varg | L | 294 |
| top | corners | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar, Varg | L | 624 |
| top | corners | AlphaSlop | Cassi & Issac, Ren, Stellar, Tavi, Willow | W | 1000 |
| top | lanes | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar, Varg | L | 890 |
| top | lanes | AlphaSlop | Cassi & Issac, Ren, Stellar, Tavi, Willow | W | 1024 |
| top | elkring | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar, Varg | W | 1008 |
| top | elkring | procless | Cassi & Issac, Ren, Ryth, Stellar, Varg | L | 612 |
| top | lanes | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar, Varg | W | 1006 |
| top | lanes | Mite | Cassi & Issac, Ren, Stellar, Tavi, Varg | L | 986 |
| top | ambush | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar, Varg | L | 668 |
| top | ambush | procless | Cassi & Issac, Ren, Ryth, Stellar, Varg | W | 1022 |
| top | contest | Sneaky Bush Campers | Prism, Ren, Stellar, Tavi, Willow | L | 0 |
| top | contest | Intercontinental Fish | Cassi & Issac, Prism, Ren, Stellar, Tavi | W | 1000 |
| top | contest | Intercontinental Fish | Cassi & Issac, Prism, Ren, Stellar, Tavi | W | 1000 |
| top | contest | AlphaSlop | Cassi & Issac, Ren, Stellar, Tavi, Varg | L | 0 |
| mite | expanse | Mite | Cassi & Issac, Ren, Stellar | L | 862 |
| mite | expanse | Intercontinental Fish | Cassi & Issac, Stellar, Varg | W | 1008 |
| mite | stampede | Mite | Cassi & Issac, Prism, Ryth, Stellar, Tavi | W | 1008 |
| mite | stampede | Intercontinental Fish | Cassi & Issac, Prism, Ren, Stellar, Tavi | L | 0 |
| mite | rows | Mite | Cassi & Issac, Ren, Ryth, Varg | W | 1012 |
| mite | rows | Intercontinental Fish | Cassi & Issac, Ren, Stellar, Varg | L | 990 |
| mite | contest | Mite | Cassi & Issac, Prism, Ryth, Stellar, Tavi | W | 0 |
| mite | contest | Intercontinental Fish | Cassi & Issac, Prism, Ren, Stellar, Tavi | L | 0 |
| mite | rushbait_v2 | Mite | Cassi & Issac, Ryth, Stellar, Varg | L | 776 |
| mite | rushbait_v2 | Intercontinental Fish | Cassi & Issac, Ren, Ryth, Stellar | W | 1008 |
