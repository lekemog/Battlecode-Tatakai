Source freeze: `015e70443bbffcaa96109493d3f090ff628c6e7e`.

# Codex: map-aware drafting on submission245 / v61j

## What this builds

Submission245 is recorded as `bots/v61j` in SUBMISSIONS.md and the Franklin handoff. Its source is unchanged between pins9c973869 and ccdc6659. This work copies that source into new folders. The active account submission was not independently checked: CLI authentication is unavailable. No live submission, activation or external match group was made.

- `bots/cg-md245-plan`: map-based composition search, cached after the first draft turn.
- `bots/cg-md245-react`: same search plus a small revealed-opponent-role re-ranking. This is a separate experimental ablation.
- `bots/v61j`: unchanged reference for all comparisons.

This is distinct from rejected v63a, which used the opening budget to assign camp targets. It changes the draft and leaves the gameplay planner/economy intact, with one required exception: ranged champions can attempt camp attacks/casts from an in-range bad-spot tile instead of skipping all opening damage. v245 itself uses melee and does not exercise that ranged branch. Results test the whole candidate, including this prerequisite.

## Use of the large budget

The SDK documents first draft turn100× fuel, each champion's first gameplay turn2×. The draft scan measures about9.99million initial draft fuel. No fuel limit is increased for tests.

1. Build static map knowledge and two terrain distance fields: from our spawn and theirs, treating living camp tiles as obstacles. Read camp HP/damage, splash clustering, rewards, respawn timers and approach distances. Keep accessible own-side/contested economic groups and at most36 high-value representatives.
2. Decode all12 draft choices from actual champion designs. Cassi/Issac are one pick with two physical kits. Shared-death exposure uses the weaker body's HP rather than summing both as independent survivability.
3. Screen **every composition admitted by the frontline/ranged constraints** of this map's draft size using six representative camps. Validity requires a melee frontline and at most two ranged bodies. For five picks there are at most792 subsets before constraints. An incomplete screen falls back to the original draft rather than selecting from a mask-order-biased partial search.
4. Re-score the strongest32 candidates on all selected camps. The analytic score estimates reward per travel/clear/capture time, incoming-damage/recovery cost, repeated respawn value, splash damage, basic range and control. Runtime kit metadata supplies damage/cooldowns, the SDK supplies capture/passive constants. A change must exceed the baseline model score by2.5%. Reserve fuel for a legal pick and diagnostics.
5. Reuse the cached shortlist on later ordinary-budget draft turns. Keep every already committed pick. Optionally re-rank by only the enemy picks revealed so far; this bonus is capped at4%. Never access a completed enemy draft in advance. Store a versioned target/committed-mask record in available draft memory. No gameplay consumer of that record is added.

The measured final implementation completes all256 initial scans, screens all expected valid candidates and uses at most5,698,467 fuel (57.04% of available initial fuel). The earlier exhaustive36-camp prototype consumed up to95% and was superseded before the strength suite. Preliminary outcomes are excluded.

## Variety and safety

There is no randomness, forced diversity quota, map-name lookup or map-hash gate. Changing map properties changes predicted value. A composition is chosen because it scores well under the model, not because it differs from the last game.

On128 pinned maps/both sides the final planner produces4 different three-pick sets,7 four-pick sets and7 five-pick sets. The trace-selected champions cover9 draft choices (10 physical types when counting Cassi and Issac separately). See draft_scan.csv for each map/side, picks and actual fuel.

Pick sequence uses the fixed priority Heart, Marcella, Vendetta, Varg, Ryth, pair, Vesper, Ren, Stellar, Tavi, Prism, Willow within the selected set. This differs from v245's five-pick order even when the selected set matches it. Therefore the strength comparison cannot separate composition effects from order effects. A future isolated sequence ablation should restore v245's order within an identical set. A search failure returns to the original draft function/order.

All source flags, including draft logging, are frozen for the suite. Disabling logs can change fuel/timing and requires another validation.

## What the top-team evidence actually establishes

We used all50 stored engine3 match summaries in today's `t10b_240` top-ten panel, five maps/opponent. Input source pin: ccdc6659. `top10_input_manifest.json` pins every underlying compressed summary blob; the repository already holds those raw inputs. This is not a new ladder census: the live public API returned401 / sign in with cambc login.

Champion sets are unordered for composition comparisons; pick order is analyzed separately. Draft sizes are stratified, so merely fielding3 rather than5 does not count as changing the strategy.

All10 teams have at least one within-size composition difference. The best-fitting single set per team/draft size explains34/50 games;16/50 (32%) need another set. Across comparable same-team/same-size pairs,32 of46 comparisons differ. These are two descriptive measures of this small cohort, not independent samples or a population transition probability. Ties for the modal set do not change the best-fitting count. Five matches/team cannot establish an exact general adaptation rate or prove that map features caused every change; draft order, opponents, side, timing, randomness and source versions can matter. Cohort group IDs are retained in t10b_240.json; per-game opponent source versions are not embedded in these summary records.

## Model limits and next work

This is a bounded heuristic search, not an exact RTS simulation, calibrated win probability or proven optimal composition. Top-team pick frequency is not used as a causal strength label.

- Uses initial kit stats/abilities. It does not model full upgrade curves, all item passives, kill/assist income, exact cooldown scheduling or individual role execution.
- Treats team camp damage as available together. It does not simulate travel splits, who actually tanks, collision/turn order, per-unit deaths or a full opening route schedule.
- Group values are estimated from accessible approaches, not a complete graph of future camp clears. Boss/camp barriers, altar/banking accessibility and later enemy control can distort value.
- Prism gem-battery and Willow coordination are not implemented in v245; heuristic penalties reduce their score but do not turn generic play into proper roles. No Cassi-pair prototype or Vesper funnel from other PRs is silently merged.
- Ordinary gameplay still has known fuel-critical maps. New draft bodies and role choices can change host-call cost and early deaths even though no new per-group gameplay scoring work is added.
- Source245's already-proven small-map draft is only a model prior, not a guaranteed performance floor. Model score improvement does not imply game improvement.

After the current evidence, keep or reject based on games, deaths, gold and family tails, not diversity count. Next isolated tests: sequence-preserving control, pair-risk/role compatibility, learned but regularized map score calibration with held-out maps, and confirmed real-opponent panels. Do not ship without transformed/unseen-map qualification and the existing coordinated live-slot process.
