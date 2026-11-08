# Tatakai early economy and coordination audit

5 November 2026. Investigation only; no gameplay deployment or new unranked games.

## Evidence and scope

Read the repository entry documents, current-state notes, testing/live-slot instructions, early-gold and mass-death studies, top-ten panel results and census, historical opponent draft tables, and the v51d draft, shop, context, combat, coordination and target-scoring code. Source snapshot: `03b34544c02d0e9b501183f5d1f4a60759ceec9f`. Main explicitly says it does not contain the newest gameplay line. This is a targeted review of relevant source and evidence, not a claim to have read every archived bot or binary replay in the repository.

Independently inspected the signed-in platform and downloaded all five JSON summaries from a fresh Mite unranked group, `01a1ad80-feeb-7e8a-9fde-8ce8a1e9d031`. Our version was 226. All five use engine 3.0.0, with collision build hash `96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd`. Team A is Tatakai throughout this group. Platform ladder at observation: Tatakai overall 76, 2,021; Mite second, 2,673. Historical reports below use older engines and are not pooled with these fresh games.

Match group: https://2026a.battlecode.co.uk/game/match-groups/01a1ad80-feeb-7e8a-9fde-8ce8a1e9d031

## Finding: two separate early-economy failures

Isolation and early deaths are real, but do not explain every deficit. We also lose the farming race in games where no one dies early. Fixing combat cohesion alone will leave a substantial economic gap.

| Fresh Mite map | Gold earned at r200, us / Mite | Deaths by r200, us / Mite | Final banked gems, us / Mite |
|---|---:|---:|---:|
| 01hooks | 270 / 1,803 | 6 / 0 | 0 / 1,008 |
| 03reef | 930 / 1,413 | 0 / 0 | 527 / 1,010 |
| 00collision | 698 / 1,373 | 1 / 0 | 265 / 1,006 |
| 04wilds | 887 / 1,148 | 0 / 0 | 609 / 1,011 |
| 01yellow_brick_road | 765 / 2,285 | 1 / 0 | 369 / 1,016 |

Gold is cumulative earned gold, reconstructed from run-length encoded champion timelines at round 200, not purse balances. The summaries do not supply per-round positions, so these fresh games establish economy, draft, deaths and purchases, not a new spatial-cohesion measurement.

On reef the first death is r280; on wilds it is r522. Thus their r200 leads exist before kills. On hooks we eventually die 33 times without killing anyone. These require different remedies.

Historical decoded study against ha²t, Gamblr, Valenki and Kratos: 70 of our deaths before r300 against 28 enemy deaths across 20 games; 57% of our early deaths outnumbered by at least two, versus 7% for them. Our median first death r93 versus r166. Those opponents were not uniformly tighter: ha²t was no tighter than us. Avoid generalising one pack style to every strong team.

## Farming throughput and a protected carry

In collision Mite's Vesper alone earned 4,810 gold and banked 585 gems; our entire team earned 4,021 and banked 265. Vesper did 62,515 camp damage and 12,147 champion damage with zero deaths. This supports testing resource concentration and protection around an effective carry. It does not prove that all rewards were intentionally funnelled or that Vesper always travelled with the team.

Fresh Mite drafts:

| Maps | Mite draft order |
|---|---|
| collision, three picks | Vesper, Heart, Cassi & Issac |
| reef, wilds, yellow brick road, five picks | Vesper, Vendetta, Heart, Cassi & Issac, Tavi |
| hooks, four picks | Marcella, Vendetta, Heart, Cassi & Issac |

Cassi & Issac is one draft pick producing two units. Collision was four enemy bodies against three of ours. Evaluate their extra actions together with resource dilution, positioning, survivability and actual kit execution; an extra body alone does not establish draft superiority.

By r200, unique camp-group collection timestamps on collision were 13 for us and 20 for Mite after merging same-round, same-group shared recipients. On wilds: 8 versus 10; reef: 12 versus 16. Shared collection entries must be deduplicated before calling them captures. Gold differences also involve group values and item passives, so counts alone do not explain the entire lead.

Mite repeatedly revisits profitable groups: on wilds group 11 is collected at r34, r108, r188; Vesper collects groups 11, 19, 7 and 24 by r163. Candidate design: choose a productive local circuit using actual respawn times, travel, clearing and capture cost, safe return paths and enemy pressure. Holding one location forever is only worthwhile if its production exceeds alternative routes.

## What the code actually does

The inspected v51d source is a candidate snapshot, not an independent identification of the active v226 binary.

* `config.h`: `squad_size=1`, `escort_until=0`, `opening_party=0`, `carrier_capture=false`, `sim_ally_contact=0`, `route_chain=0`. The default macro policy still permits independent farming, without an opening escort or designated carry recipient.
* `brain.cpp` around 2490: camp value is divided by the number of champion workers. That charges grouped farming for extra bodies but does not explicitly credit their full deterrence, protection and denial value. This is a plausible structural reason that locally efficient solo choices can be globally unsafe.
* `brain.cpp` around 1310: allies within six tiles can enter our fight simulation; the optional contact filter is disabled. Proximity is not a commitment to help. A replacement should estimate arrival time, attack range, path and current objective, rather than simply enable a hard distance cutoff.
* `draft.cpp`: mode-based preference order plus learned reordering; there is no explicit formation contract assigning frontline, carry and protection jobs. Observed v226 uses Heart, Ryth, Marcella on three-pick maps, leaving no ranged specialist there.
* `ctx.cpp` decodes each champion's abilities, range and passives. `combat.cpp` distinguishes ability kinds, movement exclusivity, resets, shields and attack ranges. It would be incorrect to say every character is literally identical. The missing layer is team-level role coordination.
* `shop.cpp`: main stat is primarily an averaged ability/camp throughput comparison, with Heart Focus override; most melee champions inherit similar plan-7 survival/economy steps. This is not a role-aware shop. Learned sorting also changes purchase order, so changing the apparent plan order does not guarantee the live order.
* `brain.cpp` around 1678: the four-slot health history lacks round stamps in this snapshot. The repository already has a neutral tested history-fix candidate. Port and reverify it separately; do not claim it explains the economy deficit.

No Tatakai fuel-exhaustion events appear in the five fresh summaries. Mite has such events, including many on yellow brick road, yet wins. Our problem in this sample is not established as fuel starvation.

## Roles to test

These are candidate responsibilities, not a proven optimal draft:

| Role | Candidate | Required behaviour |
|---|---|---|
| Frontline / peel | Ryth or a suitably built Heart | Hold the safe side of contact, stop dives onto the carry, disengage with the group; avoid donating a tank alone |
| Ranged damage and farming carry | Vesper; compare Stellar under this patch | Attack from safe range, receive selected captures, maintain a safe farming circuit; reposition when threatened without wasting legal attacks |
| Finisher | Vendetta | Join a committed fight, choose reachable lethal targets to exploit reset mechanics; no unsupported chase |
| Burst / secondary frontline | Marcella | Coordinate ability timing with team contact; compare Focus and Strength under engine 3 rather than assuming the older Focus result survives |
| Extra utility / farming | Cassi & Issac, Tavi, Willow, Varg depending on map | Explicit support or safe-side job with a return condition; no generic independent expedition into unseen enemies |

Do not hard-code one tank, one marksman and one assassin on every map. Three-pick maps, narrow corridors, camp clusters, jackpot maps and low-gold maps create different tradeoffs. Heart's shield value already appears in actual metrics: our collision Heart generated 19,554 shielding and never died, but that did not keep Ryth alive or turn the team into an effective carry composition.

## Top-team selection evidence and freshness

Historical top-25 unranked table includes these teams from the top end of the ladder at its collection time:

| Team | Recorded typical composition, order not preserved |
|---|---|
| Intercontinental Fish | Cassi & Issac, Heart, Vendetta, Vesper |
| Pantheon, then named newer team | Cassi & Issac, Heart, Marcella, Varg, Vendetta |
| Ad Astra | Heart, Ryth, Vesper |
| Mite, historical | Heart, Marcella, Tavi, Vendetta, Vesper |
| prism best girl | Cassi & Issac, Heart, Vendetta, Vesper |
| NEETCoders | Heart, Marcella, Ryth, Vendetta, Vesper |
| policy wonk | Heart, Marcella, Tavi, Varg, Vendetta |
| print dont int | Heart, Marcella, Ryth, Vendetta, Vesper |

The current top ten observed in the platform were Fish, Mite, Pantheon, Vvvvv @ 2FA (Univardisty), Ad Astra, BattleCats, Trzy Kwaterki, NEETCoders, T1 and subscribe to caterpillow. Historical ranks and names cannot be presented as current draft telemetry for all ten. Fresh draft verification in this audit covers Mite; a complete current-patch census of all ten remains outstanding.

Historical 100-game top-ten census: us/them 4,232/7,106 gold, 642/1,180 gems collected, 387/999 banked, 10.9/2.5 deaths. Collection volume and conversion both matter. The reported single-recipient metric of 1.00 on both sides is explicitly a counting artifact and cannot support a funnel claim.

## Prioritised changes and how to judge them

1. **Shared regional objective and contact rules.** Pick a profitable camp cluster and a safe fallback; assemble the needed members before contested entry. Keep the carry close enough to actual assistance. Allow safe-side solo harvesting only with a threat/return test. Stop trickling respawns into a lost fight. Measure unsupported deaths, first-fight numbers, useful farming time and gold at r100/r200.
2. **Capture recipient and camp circuit.** Test a designated recipient independently, preserving a fallback when the carry is absent or banking. Allies help clear and protect without all waiting on the capture tile. Measure carry gold share, team gold, camp throughput, deaths and banked gems, not just carry wealth.
3. **Draft and role-specific items.** Compare a ranged pick within the first three and Cassi & Issac under the current patch. Give the frontline enough survival, the carry the best marginal damage/capture throughput, and the finisher damage appropriate to its kit. Audit actual purchase events after learned sorting. Do not blindly copy every Mite item or buy Greed/Skirmish merely because they were buffed.
4. **Reachable support and synchronised target choice.** One committed fight target, individual legal actions; reserve lethal follow-up without excessive overkill. Count ally contribution only when it can arrive in time. Track enemy pack memory outside vision.
5. **Banking and upgrade windows.** Maintain a safe route and protection for carriers; use power spikes before central contests. Monitor collected-to-banked conversion, carried losses, first deposit and zero-bank maps. More coins are a means to control and gems, not the win condition.

Previous attempts constrain the design: v50j1 regroup/cohesion bundle lost 3/50 versus baseline 4/50; a long opening ball and fixed pairs also failed some tests. The new proposal must use adaptive regional cooperation rather than repeat those flags under another name. The earlier Marcella Focus advantage did not persist under patch 4.0.0 according to CURRENT_STATE.md.

Test each mechanism separately on engine 3 and the verified current pool, then pinned real opponents with identical maps and sides. Combat candidates need early-pack stress and real panels; self-play alone is not sufficient. Check all map families, errors and zero-bank failures. Before live scrims, inspect the newest shared slot and coordination state. No new games were necessary to establish these failures, and none were queued here.

## Repository references

* https://github.com/lekemog/BattlecodeConversation/blob/main/CURRENT_STATE.md
* https://github.com/lekemog/BattlecodeConversation/blob/03b34544c02d0e9b501183f5d1f4a60759ceec9f/results/56-early-gold-strong-opponents/README.md
* https://github.com/lekemog/BattlecodeConversation/blob/03b34544c02d0e9b501183f5d1f4a60759ceec9f/results/54-mass-death-losses/README.md
* https://github.com/lekemog/BattlecodeConversation/blob/03b34544c02d0e9b501183f5d1f4a60759ceec9f/results/54-public-insights/README.md
* https://github.com/lekemog/BattlecodeConversation/blob/03b34544c02d0e9b501183f5d1f4a60759ceec9f/results/top25-unranked-2026-11/per-opponent-tables.txt
* https://github.com/lekemog/BattlecodeConversation/blob/03b34544c02d0e9b501183f5d1f4a60759ceec9f/results/panel/t10_226.json