# Team replay review
A common way to turn strategic observations into testable improvements. Anyone can post a review directly in an issue; no code change is needed.

## Start with one question, not the whole game
Choose a match, watch the opening, then inspect the first decision that creates a lasting disadvantage. Pause before seeing the outcome and write down the alternative you would prefer. Review a win as well as a loss so we preserve what works.

| Priority | Question | Post in |
|---|---|---|
| Corners | Which small camps are taken, by whom, and what prevents the other side from taking them? | #15 |
| Packs | Are the 48-gem opportunities unavailable, unsafe, unchosen, or abandoned? | #15 |
| Contest | Does the first bad exchange begin with poor positioning, late support, or a missed retreat? | #20 |
| Eight | Does the carrier's route have support when crossing the scoring area? | #18 |
| Strong-map regression | What changes first between the older and newer version: recall, target, arrival, fight or tribute? | #20 |
| Ambush control | Which successful routing and timing decisions must a new version preserve? | #15 |

A gem pickup is not automatically a camp capture. Follow the camp's state and the recipient; distinguish stolen gems, split rewards and tribute.

## Starter matches
These files are listed in the repository's top-team corpus. They are comparative examples, not selected proof of any hypothesis, and have not been newly watched for this guide. Historical ranks and results are in the [corpus index](../top-replays/README.md).

| Map | Teams | Replay |
|---|---|---|
| Corners | Intercontinental Fish / Boost | [Replay](../top-replays/050ab0d8-2d49-4b0d-b180-dce4a7e3b6d7.repl26a) |
| Packs | Intercontinental Fish / Sneaky Bush Campers | [Replay](../top-replays/307bcd46-6b80-4c26-9b97-dd9b6cc78137.repl26a) |
| Contest | Nyxius / Sneaky Bush Campers | [Replay](../top-replays/3c38a883-b838-4242-966d-ae6aeeec40ec.repl26a) |
| Eight | EMPEROR Tung / Quantom | [Replay](../top-replays/07cbae51-8b28-40a0-94b0-256a0364a364.repl26a) |
| Ambush | Univardisty of Shingtonwash / Mite | [Replay](../top-replays/17930cf8-730c-43fd-8e9c-ccddd962355c.repl26a) |

GitHub links download the files; they do not play the replay in GitHub. With the official viewer installed, open a file using `cambc view <replay-path>`. If viewing setup is inconvenient, request a browser-viewer match link or a short recording with round numbers in the relevant issue. A reviewer should not have to decode JSON to contribute.

For direct diagnosis, we also need our own comparable matches. The test operator should attach one loss, a contrasting win where available, and baseline/candidate pairs with map, side, version and result. Do not substitute top-vs-top examples for those pairs.

## Three passes
1. **Plan:** where does each unit go, what resources are being contested, and when should the team bank, regroup or buy?
2. **Turning point:** pause just before the first avoidable loss of time, position or resources. Identify the available choices and the cost of each.
3. **Execution:** did the bot choose the wrong plan, fail to carry out a reasonable plan, or face a situation it could not observe? Avoid explaining every loss as bad strategy.

Track useful time, not just aggression: travel, waiting, retreat loops, repeated targeting, late support, interrupted tribute and purchases that pull a unit away from an objective.

## Copy this into an issue comment
```text
Match link / ID:
Map, side, version:
Round range:
Question being investigated:

Observation (what visibly happened):
Information available to our bot then:
First decision I would change:
Alternative action and expected benefit:
Cost / danger of that alternative:
What would disprove this idea:
Contrasting example, if available:
Confidence: low / medium / high, and why:
```

Screenshots or a short clip with round numbers are welcome. Label replay-only information explicitly; an alternative requiring hidden information is not a legal runtime policy.

## From review to experiment
- Reviewer supplies the observation, alternative and expected mechanism.
- Implementation response identifies the relevant function, confirms the available information and proposes the smallest change or fixture.
- Test response links baseline/candidate results and checks the predicted mechanism, including regressions.
- Close the loop with **supported / contradicted / still uncertain**, not just a win count.

Initial tests should distinguish:
- camp not considered vs considered but rejected vs chosen then abandoned;
- poor engagement vs late retreat vs path blocked vs retreat interrupted;
- extra recall time vs improved purchases/healing;
- successful collection vs successful delivery.

Do not add a global death cap or retreat switch from one replay. A good proposal explains when the rule applies, when it should not, and how it returns to productive play.
