# Contributor and agent guide
Our shared working agreement. Updated18 October2026 against main `e9d3eb2`.

## Protect the current checkpoint
The latest repository-recorded final deployment is **v19n, version148**. [Submission log](SUBMISSIONS.md) and [final decision](https://github.com/lekemog/BattlecodeConversation/issues/20#issuecomment-6254676865). Main Claude's handoff says **no more ladder tests tonight**. The documented freeze is22:59 UTC /23:59 Irish time.

- Only the designated main Claude session runs `cambc submit` or `cambc match-groups create`.
- Scrims use the submitted bot; concurrent submissions contaminate tests. The team also shares the group quota.
- Work on your own branch, use new candidate folders, and open a PR. No direct pushes to main.
- Official legal API only. Do not use offline replay omniscience in runtime decisions.

## Read in this order
1. [README](README.md): current checkpoint and navigation.
2. [Team review](docs/TEAM_REVIEW_2026-10-18.md): findings, regressions, next-version experiments and contributor credit.
3. [NOTES](NOTES.md): chronological history, newest at bottom.
4. The relevant issue below and its latest replies. Original issue bodies may describe older versions.

## Discussion index
| Issue | Topic |
|---|---|
| [#15](https://github.com/lekemog/BattlecodeConversation/issues/15) | Cross-map diagnosis and code review |
| [#16](https://github.com/lekemog/BattlecodeConversation/issues/16) | Altar routing |
| [#17](https://github.com/lekemog/BattlecodeConversation/issues/17) | Posture and opponent adaptation |
| [#18](https://github.com/lekemog/BattlecodeConversation/issues/18) | Gem delivery and escorts |
| [#19](https://github.com/lekemog/BattlecodeConversation/issues/19) | Itemisation and combat capacity |
| [#20](https://github.com/lekemog/BattlecodeConversation/issues/20) | Fight valuation and final candidate results |
| [#21](https://github.com/lekemog/BattlecodeConversation/issues/21) | Early economy and recall |
| [#22](https://github.com/lekemog/BattlecodeConversation/issues/22) | Kurian's opening/capture/model studies |
| [#6](https://github.com/lekemog/BattlecodeConversation/issues/6) | Szymon's workstream and earlier review |

## Current conclusions
- v19n:12/75 weak-map games,4/35 strong-map subset; v19f:10/75 and4/35; v18x:6/75 and6/35.
- Contest remains0/15. Eight is no longer universally zero: v19n wins1/15.
- v19m's carrier/lifecycle package scored8/75. It is a useful implementation reference, not an accepted performance improvement.
- v19i changed off-gate self-valuation; do not blame its regression solely on lifecycle resets.
- First-strike associations are not causal instructions. Item counts are not gold spent. Missing first tribute needs a never-bank count.
- The corrected opponent model is not suitable as a standalone global switch. Local context-sensitive adaptation remains a research proposal.

## Evidence and testing
For each candidate supply: parent/source hash, single hypothesis, changed functions, expected mechanism, fixtures, local results and a paired-test request. Preserve map, side, match ID, submission and opponent version where available; flag unknowns.

Use baseline repeats to expose variability, fresh held-out opponents, and strong-map regression coverage. Faux bots help detect execution failures but are not substitutes for top-100 evaluation. Only the designated operator chooses deployment after reviewing tradeoffs.

## Data
| Resource | Location |
|---|---|
|164 top-vs-top replay files and index | `top-replays/` |
| Replay decoder | `tools/replay/extract.mjs` |
| Decision traces | `results/traces/` |
| Audit scripts | `tools/audit/` |
| Initial named-opponent study | `results/chatgpt/top50-study-2026-10-17.md` |
| Kurian's corrected study | branch `kurians/top-openings`, `results/kurians/openings-contest-eight.md` |
| Historical local discussion | `CONVERSATION.md` |

The roughly700 own-game decodes were reported in the main session's environment, not committed here; request specific sanitized per-match evidence in the relevant issue. Do not claim access to them from the repository alone.
