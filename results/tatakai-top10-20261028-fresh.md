# Tatakai: fresh top-ten unranked review — 28 October 2026

50 new games, 10 five-map series, submission 221 throughout. **5 wins, 45 losses.** This is a new random-map cohort, separate from the earlier 10/50 fixed-five-map study. Current cohort selection ranks: Mite, Fish, prism, newer, Ad Astra, print, NEETCoders, hello, Trzy, Claudus. Sides alternate by opponent index and map index: 25 A / 25 B; no mirrored rematch for each map. Engine 2.0.0, build 85aa7167b44db7cea97509f55e997750520e33d644e9f4f90d6128c50eba1d21.

## Observations and priorities

- Mean gold earned at r200: **587.78 us / 895.56 them** (52% more for opponents). Farming/clear/travel efficiency needs a separate experiment from shopping timing.
- Mean deaths: **11.40 us / 2.54 them**. Zero recorded botFault events; three fuelExhausted events for us. These do not establish action-level causation.
- Five zero-deposit games have different mechanisms. Contest collected no gems; hooks collected only 22 and lost all 22; guardians collected 93 and lost 78; stalactites collected only 4. They cannot all be explained by a blocked bank route.
- **Strong banking reproducer:** Trzy/the_pack, match `4490976d-43a4-4d7e-b6a9-e08712a3dbda`, our side B: collected 908, held 618 at end, lost 290, deposited 0; opponent deposited 1,025. Prioritize #45.
- Mite/expanse again ended 575–1,040; Fish/expanse 603–1,020. The repeat deficit supports opening-economy investigation (#47), but these final scores alone do not identify which camp choice is wrong.
- The three largest single bag losses are below. Two occurred in games we won: inspect counterexamples, not only losses, before choosing a globally conservative policy.

## Independent ownership

| Task | Issue | Deliverable |
|---|---|---|
| Banking/pathfinding | #45 | Gate/route trace and one progress-aware commitment candidate |
| Combat/carrier safety | #46 | Pre-death trace; distinguish escape, focus and interception |
| Opening economy | #47 | r0–200 camp value, clear duration, travel and allocation measurements |
| Runtime/liveness | #48 | Locate fuel events and prove whether decisions were skipped |

Different teammates should claim one issue each with name and branch. Ownership remains unclaimed rather than inventing GitHub identities. Coordinate existing claims in #40. Keep candidates isolated; test baseline vs candidate with same seeds/maps and both sides, then fresh games. Do not deploy on this observational evidence alone.

## Results by opponent

| Rank | Opponent | Our wins | Series |
|---|---|---:|---|
| 1 | Mite | 1/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/ecece844-992f-419f-bcba-819bc9c4e0dd) |
| 2 | Intercontinental Fish | 0/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/e4e73fe8-d092-4b5b-bbb8-dc47d7d15328) |
| 3 | prism best girl | 0/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/c47f97a6-9f49-41f6-8615-4707ac13ec36) |
| 4 | newer team | 1/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/1fceac53-e746-4dce-a892-e088738a3fda) |
| 5 | Ad Astra | 0/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/f36549c0-fa6e-4009-96fa-002f7855d351) |
| 6 | print dont int | 1/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/eeafc4ea-5cf4-40fb-8531-dfbdae77a5d1) |
| 7 | NEETCoders | 1/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/5a995cc7-c9ec-4aaa-b471-10f7c12cd879) |
| 8 | hello | 0/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/f5476c8e-c49e-4438-848f-4ec022e20478) |
| 9 | Trzy Kwaterki | 1/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/93d5dbc1-9fac-4265-beb7-84c4f840af9f) |
| 10 | Claudus Maximus | 0/5 | [Results](https://2026a.battlecode.co.uk/game/match-groups/9fe6fb10-3f84-4772-8efa-e0b6ba2fc96c) |

## Per-game evidence

Scores below are normalized to **us / opponent**, not raw team A / B order. All IDs identify official visualiser replays; original summary data was downloaded and checked.

| Opponent | Map | Match ID | Our side | W/L | Banked us/them | Gold r200 us/them | Deaths us/them |
|---|---|---|---|---|---|---|---|
| Mite | 00elkring | `5bb99dfd-4428-49e5-85e3-3f95531e2282` | teamB | L | 506/1034 | 862/1776 | 13/0 |
| Mite | 00expanse | `5dd8629c-9faa-443a-b29a-0c80aecdfa39` | teamA | L | 575/1040 | 985/1122 | 1/0 |
| Mite | 02guardians | `a037cec8-2677-451f-910e-4007cb9f38c8` | teamA | W | 1020/592 | 580/280 | 11/19 |
| Mite | adgato_gemcombat2 | `c337e236-d1b8-48d4-8dc0-b2b1da5998cb` | teamA | L | 210/1021 | 112/400 | 10/0 |
| Mite | 00contest | `e1704314-9216-4a66-8106-928a06fa9c8e` | teamB | L | 0/0 | 816/1398 | 54/1 |
| Intercontinental Fish | 00expanse | `11ea194a-0755-4c50-8d82-7a7d6c52894d` | teamA | L | 603/1020 | 1109/1043 | 2/2 |
| Intercontinental Fish | adgato_gemcombat3 | `45a4378b-f92d-4a8f-9ca3-3495bbac4b2c` | teamA | L | 231/1001 | 0/400 | 11/2 |
| Intercontinental Fish | 01hooks | `66b64009-2337-4732-bf74-d2cb4457fa4f` | teamB | L | 0/1012 | 610/1094 | 28/7 |
| Intercontinental Fish | 00quadrants | `a2766a09-a0f8-4ad9-be14-758b705f3d0a` | teamB | L | 884/1092 | 678/865 | 4/1 |
| Intercontinental Fish | 02stalactites | `bf2a4031-3dd5-4c1e-ae57-39eea03322b1` | teamB | L | 126/1063 | 154/1444 | 10/0 |
| prism best girl | 01the_farm | `5a13cb4b-5488-4a78-8b60-3bd5189538e9` | teamA | L | 390/1012 | 690/1001 | 9/3 |
| prism best girl | 01fracture | `64e392c7-7d9a-401e-80d6-0f17480c2795` | teamB | L | 208/1016 | 941/811 | 3/4 |
| prism best girl | 00quarry | `654ff187-d6bf-4d00-b8b5-d8f256fbb240` | teamA | L | 190/1043 | 838/1240 | 16/7 |
| prism best girl | 02guardians | `b2cbdecb-87e7-401f-a52f-254d77f7ba3a` | teamB | L | 0/1071 | 140/905 | 25/6 |
| prism best girl | 02crossing | `f21006bf-6d94-46be-8522-7f9177b29057` | teamA | L | 365/1084 | 536/1056 | 16/3 |
| newer team | 00the_line | `408c77e2-5413-4b08-8906-5a018e2bed8a` | teamB | W | 1065/241 | 540/300 | 1/8 |
| newer team | 00quadrants | `722ac6e6-2010-4df0-bc61-95dd586cf8f9` | teamB | L | 501/1048 | 588/1042 | 3/0 |
| newer team | 02gift_wrapping | `b8fcfa2e-5d15-452f-9878-b952022f79fd` | teamA | L | 342/1006 | 1397/1389 | 5/0 |
| newer team | 02cuts | `f3e73015-b4da-4761-a9a3-9a16dc65e508` | teamB | L | 247/1016 | 794/452 | 0/1 |
| newer team | 02fields | `fae56cd3-1f2e-478d-8ba3-7de5734cc9fb` | teamA | L | 675/1015 | 652/642 | 4/4 |
| Ad Astra | 00collision | `017cacee-9fd1-45e6-a832-2add8e6bc26c` | teamB | L | 280/1035 | 867/1211 | 8/0 |
| Ad Astra | 00rows | `380b9511-0770-4a52-b960-21b4fe5ec20c` | teamA | L | 518/1030 | 934/1509 | 0/1 |
| Ad Astra | 00stampede | `6e07a1cb-2033-4d80-9360-a8d0ccf614fa` | teamB | L | 480/1001 | 804/1032 | 18/7 |
| Ad Astra | adgato_gemcombat1 | `71445b17-6c66-440a-9e6c-5590dfcab040` | teamA | L | 399/1016 | 84/200 | 14/1 |
| Ad Astra | 00galaxy | `bdb68b38-87ec-475b-b84e-94df758ae4d8` | teamA | L | 430/1030 | 120/253 | 14/3 |
| print dont int | 02treasure_box | `1748aa18-87f1-452b-9686-16ce88ca094c` | teamB | W | 1058/681 | 883/480 | 6/10 |
| print dont int | 00packs | `5a1adcd1-4909-4596-a6e9-c4440634231f` | teamA | L | 52/1000 | 220/1028 | 20/0 |
| print dont int | 00eight | `65c49ab3-22f7-42f9-8ce2-da6d91f25f6f` | teamB | L | 41/1053 | 560/890 | 27/0 |
| print dont int | 00stampede | `c12ea5c3-956b-46e9-8677-173d43647125` | teamA | L | 480/861 | 812/760 | 28/3 |
| print dont int | 00rows | `fef89915-210e-4db0-bbb5-59a09dabb21f` | teamB | L | 639/1088 | 758/1298 | 0/0 |
| NEETCoders | 00reverse_spiral | `6dbe970b-08dc-4dc6-bd20-1538f86d9229` | teamB | L | 894/1002 | 208/372 | 16/8 |
| NEETCoders | 02cuts | `74034685-8342-4aa3-8522-5508e79fbc08` | teamA | L | 469/1113 | 730/733 | 2/0 |
| NEETCoders | 02stalactites | `be2ee3bf-14d3-4ee4-8ce9-bf6094cd174a` | teamA | L | 0/1036 | 0/1157 | 12/0 |
| NEETCoders | 01fracture | `da53b235-d4e0-4cdb-996e-21e1c4472310` | teamB | W | 1074/966 | 941/831 | 1/1 |
| NEETCoders | 00collision | `ea20403e-5c36-4b59-bed4-bca86124996f` | teamA | L | 60/1000 | 530/1341 | 12/0 |
| hello | 00ribs | `1aad813e-5891-48cb-bbcc-702c54341413` | teamB | L | 100/1011 | 160/434 | 18/1 |
| hello | 02famine | `505756e5-e121-4377-bece-3698701ea1ef` | teamA | L | 762/1006 | 480/662 | 4/1 |
| hello | 01fracture | `599660ea-a29f-49ef-8786-d8f1e2eb748e` | teamB | L | 498/1025 | 941/815 | 3/1 |
| hello | 01gold_rush | `b08cd52b-d7c7-4506-966d-567e6736eccd` | teamB | L | 33/1022 | 160/1208 | 29/2 |
| hello | adgato_gemcombat4 | `d1a5b5f7-57ef-4e9e-a8a6-4206c0ef7b97` | teamA | L | 700/1011 | 70/440 | 12/0 |
| Trzy Kwaterki | 00pilgrimage | `01521d59-e618-46ee-8030-7ed33bbde89b` | teamB | L | 621/1005 | 780/947 | 15/4 |
| Trzy Kwaterki | 00reverse_spiral | `32706f72-38c3-460e-bb93-001908fe62ca` | teamA | L | 158/1041 | 538/500 | 12/5 |
| Trzy Kwaterki | 02the_pack | `4490976d-43a4-4d7e-b6a9-e08712a3dbda` | teamB | L | 0/1025 | 468/1161 | 4/3 |
| Trzy Kwaterki | 01boss_battle | `5a1338d6-b3b7-44d4-ab58-a44cc08e01e0` | teamA | W | 1004/96 | 1462/1979 | 0/0 |
| Trzy Kwaterki | 00anvil | `b75acc7b-03e5-4570-b90b-415e9098a4a3` | teamA | L | 67/1000 | 424/954 | 15/2 |
| Claudus Maximus | 00fragment | `0b4e7d4b-cd24-4942-88d3-1ad6f2f3a23d` | teamB | L | 58/1022 | 278/772 | 23/1 |
| Claudus Maximus | 02famine | `7b9bed3d-b46f-4a78-8fbb-1ebc4b6f224e` | teamA | L | 506/1085 | 434/594 | 6/2 |
| Claudus Maximus | 00quadrants | `d5a32edc-815d-4c96-8229-8e273217510d` | teamA | L | 605/1015 | 692/878 | 4/1 |
| Claudus Maximus | 00packs | `e57a8d47-6b10-4a8a-ad50-154c8807a94e` | teamB | L | 252/1018 | 393/619 | 15/2 |
| Claudus Maximus | 02fields | `fb91c6b1-03e9-41a1-a747-0ae6af98aa64` | teamB | L | 584/1138 | 636/1060 | 6/0 |

## Largest individual carried-gem losses

- Mite / 02guardians, `a037cec8-2677-451f-910e-4007cb9f38c8`: Heart of Ruin lost 306 at r1236, (19,20), context camp; game won.
- newer team / 00the_line, `408c77e2-5413-4b08-8906-5a018e2bed8a`: Ryth lost 161 at r959, (23,10), context champion; game won.
- print dont int / 00stampede, `c12ea5c3-956b-46e9-8677-173d43647125`: Marcella lost 160 at r736, (18,22), context champion; game lost.

## Limits

Official summary/timeline/event analysis; no claim of watching every action. WebGL2 prevented replay rendering in the earlier browser session. Five random maps per opponent do not estimate a controlled causal opponent-style effect. Enemy drafts, maps, sides and seeds differ. Historical issue hypotheses require reproduction on current source before implementation. Gem losses and collection may count stolen/recollected gems again. A zero final deposit is a symptom, not automatically a pathfinding bug.
