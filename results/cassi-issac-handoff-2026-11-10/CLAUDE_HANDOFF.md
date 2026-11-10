# Cassi & Issac: implementation handoff for Claude

Implementation source freeze: `764b7ccd4c80bcbc5a9263556e992b1443db2e44`.

## Goal and source

Use the two bodies as a productive farming/combat pair, not two independent farmers and not a permanent all-team escort ball. A single death loses both bodies, so optimize pair survival **and damage uptime**, rather than either champion's survival alone.

Base: `bots/v61j` at immutable PR81 head `9c973869107665154e661e6bb696cec745a0efc4`. Franklin's handoff reports submission245 = v61j; that is a repository report, not an authenticated live-slot check in this session. Read `docs/HANDOFF_franklin.md`. Existing owners' folders are unchanged. This does not include rejected role61 code from #83.

New folders:

| Folder | Purpose |
|---|---|
| `bots/cg-ci-draft` | Same v61j economy/fight logic, literal pair draft and Cassi ranged camp-strike prerequisite; pair logic off. This is the control, not a claim that the draft is stronger. |
| `bots/cg-ci-pair` | Control plus linked-pair emergency, shared live-camp assignment, bounded regroup, no solo chase, Cassi stun priority and Issac bounded combat movement. |
| `bots/cg-ci-shop` | Pair candidate plus Cassi Focus / Issac Health main-stat override. Inherits the existing family order and survival steps. Separate experimental ablation, not an optimized proven build. |

Draft for this experiment: Heart, Marcella, Cassi & Issac, Vendetta, Varg. Same literal order on every map size: three picks give Heart/Marcella/pair (four bodies); four add Vendetta; five add Varg (six bodies). `draft_learned=false` prevents silent reordering. The strongest small-map v61j draft is deliberately changed in the control too. Do not ship these small-map choices without separate evidence.

## Verified mechanics

CLI5.0.1 SDK header states that the pair is one pick/two physical champions and either dying kills both. A diagnostic release engine probe (`kit-probe.txt`) reads actual designs:

| Champion | HP / Strength / Focus | Basic range | Slot0 | Slot1 |
|---|---|---:|---|---|
| Cassi | 600 / 30 / 100 | 3 | Targeted damage, 2×Focus, range4, cooldown8, camps/enemies | Targeted CC, damage modifier0, range4, cooldown8, camps/enemies |
| Issac | 900 / 45 / 100 | 1 | Attack reset, cooldown8 | Non-damaging dash, range2, cooldown8 |

These are this engine's probe values, not balance constants hardcoded into the controller. Ability duration, exclusivity, ready state, ranges and damage are queried from decoded/runtime metadata. Cassi is not assumed to have an AoE or a heal. Issac is not assumed to have a shield, taunt or damaging dash.

## Plan implemented

1. **Pair safety.** Track only the actual linked partner. Release stale positions after three rounds and immediately clear on partner death. If either visible/recent partner is below35% HP, stop independent commitments: use the inherited retreat when exposed, otherwise recall. This includes a healthy body reacting to the vulnerable body. Capture safety can yield to this emergency.
2. **Efficient farming.** Cassi keeps the existing target planner; Issac adopts her published, currently visible, living camp intent when nearby. Rewards/captures are not adopted, so both do not wait for one payout. Existing camp safety, spells, health, banking and target validity remain. The parent ranged bad-spot path could skip every opening hit; all three variants let Cassi attempt an in-range basic/cast instead. This prerequisite is shared by control and candidates.
3. **Bounded regroup.** In calm conditions, reduce a gap of5–8 tiles for at most four successful regroup steps. Return to normal policy on blocked movement; never wait forever at a remembered position. No cross-map recovery chase. Actual proximity resets the allowance.
4. **Accepted fights only.** Keep the original hazard and favourable/doomed evaluator as the fight gate. Cassi attacks/casts from range without gap closing; immediate contact can justify one retreat step, rather than kiting against the entire theoretical dash envelope. Issac attacks/resets and can step toward the same local diver only within four tiles of Cassi. Pair members do not use the parent's generic PvP chase fallback.
5. **Cassi control.** Prefer the ready stun against a real diver or a channel when the target is not stun-immune, unless the damage spell estimates a finisher. Otherwise preserve the existing damage-spell/basic logic. The finisher estimate uses runtime damage_amount but is not a full mitigation/retaliation guarantee. Issac's existing reset is retained; pair combat does not spend his dash to initiate. Inherited travel/retreat dash logic remains available.
6. **Shop isolation.** `ci_shop` only changes main-stat selection: Cassi Focus, Issac Health. It does not guarantee the learned shop always buys that stat, or rewrite family order. Check actual item timelines. Health trades Issac basic DPS for protection of two bodies: test this, don't assume it wins.

## Code map and porting

- `src/pair.cpp`: Brain observation/emergency/farm/combat adapters.
- `src/pair_model.h`: SDK-independent TTL, vulnerable-pair, regroup-budget and stun-priority predicates.
- `src/brain.h`: per-instance partner state, helper declarations.
- `src/brain.cpp`: observe after legal turn/channel checks, emergency before threats, farm assignment after health/bank, pair combat inside accepted-fight gate, generic pair chase disabled.
- `src/combat.cpp`: shared Cassi ranged camp attack prerequisite.
- `src/shop.cpp`: optional stat ablation.
- `src/config.h`: four isolated flags and literal draft.

To port to a newer line, apply these adapters to a new folder; do not overwrite current v61j or newer owned versions wholesale. Shared-memory layout is unchanged: this uses existing ally camp-intent slots and local visible/recent partner state. No extra shared-memory bytes or map-name conditions.

## Validation and acceptance plan

Done here: compile release variants; pure decision-boundary tests; a preselected eight-map, both-side, two-opponent matrix (96 games). See README for actual results/errors. It is a smoke screen, not ladder/draft qualification. Do not tune thresholds on those eight maps and call the rerun a new sample.

Next, freeze a source SHA and compare all three variants against the draft control, reported live v61j and early-pack v50p1 across all128 pinned maps/both sides. Add the remaining120 maps as the first confirmation set, inspect family tails and transformed/unseen geometry, then follow the existing pinned UK/top-ten panel process after live-slot coordination and Leke's authorization. A local mirror cannot certify a draft.

Measure r50/r100/r200 gold and spend, Cassi spell/basic damage, pair deaths (both unit deaths and linked death episodes if decoded), time separated, time spent regrouping, camp nearest-target share, captures, banked gems and fuel-outs. Decode paired replays: a policy label is not proof an attack succeeded or that a turn was wasted. Distinguish stun/channel/recall/capture from idle.

Keep only if pair logic improves survival without erasing early economy/DPS across opponents/families. Require actual reduction in unsupported pair deaths; do not select on a handful of wins. Stat build must beat pair-only separately. Any new fuel suspension or rejected-action pattern needs diagnosis before shipping.

## Known limitations / next isolated improvements

- Not an atomic teamwide retreat broadcast. Fog, action order and recalls can make the two bodies react a turn apart. Local health memory expires; an unseen partner cannot be protected perfectly.
- Farm adoption helps Issac choose Cassi's camp but is not a complete min-max pair camp forecast. The old per-champion camp evaluator can still underestimate the cost of losing both bodies; it does not veto every camp that threatens the partner.
- Four-tile combat leash is geometric; walls can split the pair. Regroup is local step scoring with a budget, not a full path-to-partner planner.
- Pair healing/banking is not synchronized atomically; emergency recall may cost productive time. Test pressure-only recall separately if overprotective.
- Current stun helper checks immunity, not the target's remaining stun duration; chaining with Heart can waste control. A separate observed-buff-duration ablation should time the stun near expiry.
- No hard prohibition on every farm walk/dash exceeding the leash, no new gold-transfer system, and no global high-spawn camp-control scheduler. Do not describe this as complete optimal pair utilization.
- No live submission or activation. Existing reported bot remains untouched.
