# Start here — Tatakai teammates and agents
Updated 5 November 2026. Read [CURRENT_STATE.md](CURRENT_STATE.md), [UK top-six plan](docs/UK_TOP6_PLAN.md), then the working branch's TESTING.md and LIVE_SLOT.md.

1. **Verify your base.** Main is the coordination entry point; newest gameplay work is on Claude's branches linked in README. Confirm the actual active platform submission, source SHA, CLI, engine build and current map pool. Folder order is not a version registry.
2. **Claim a task.** Use #40; comment on #71, #72 or #73 with branch, scope and expected deliverable. Existing owners retain their claims. Do not allocate someone else's identity or repeat their in-flight run.
3. **One change per candidate.** New folder under bots/ and own branch; preserve historical versions. Log the hypothesis, mechanism and counterexample before tuning.
4. **Use the correct gate.** Weak bots catch faults/regressions; self-play can penalise caution. Combat/cohesion needs early-pack stress and pinned real opponents. Patch-altered draft/shop needs fresh engine-3 tests. All-current-map scan plus family tails; no pooled old/new-engine scores.
5. **Shared live slot.** Anyone may test after due diligence, but first inspect/book the shared LIVE_SLOT.md and coordination issue. Never overlap submission/activation/scrim windows. Confirm activation and opponent pins, record the revert target, restore afterward and close your window. This replaces obsolete “only main Claude may submit” instructions; it is not permission to bypass coordination.
6. **Prove liveness.** Separate useful solo farming from unsupported straying. Label channel/capture/recall/stun/wait correctly before calling stationary turns a bug. Report action success and objective progress, not only policy names.
7. **Preserve evidence.** Exact map hashes, sides, opponents/versions, source SHA, engine build, counts including errors, summary/replay IDs and per-map regressions. Deterministic repeats and rotated copies are not independent fresh samples.
8. **Cleanup conservatively.** Reachability/config audit and profile first; behaviour-preserving refactors separately from policy changes. No bulk branch/bot/replay deletion. Old docs are retained under docs/history; old test reports stay dated.

Current runtime/correctness work is not certified complete. Follow issue acceptance criteria and post failures as well as wins.
