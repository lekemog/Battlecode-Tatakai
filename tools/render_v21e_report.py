#!/usr/bin/env python3
"""Render completed paired local panels as a reviewable Markdown report."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/v21e-candidates'
BOTS=['cg_cycle','cg_task','cg_capture','cg_siege']
NAMES=dict(zip(['25d8','2e98','3991','3a5c','3e2d','699c','7bfc','8192','9385','9925','b135','b777','bb12','df22','e3c2','f2b6','f930'],
 ['rows','collision','monolith','contest','eight','ambush','pilgrimage','expanse','lanes','fragment','packs','interlock','elkring','rushbait_v2','corners','stampede','swirl']))
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
        ['| '+' | '.join(map(str,row))+' |' for row in rows])+'\n'
def main():
    data=json.loads((OUT/'comparison.json').read_text())
    paired=list(csv.DictReader((OUT/'paired-games.csv').open()))
    groups={'v21e':data['baseline'],**{b:data['candidates'][b]['groups'] for b in BOTS}}
    report=['# v21e: four isolated local experiments\n',
        'Our team: **Ben, Kurian, Leke and Szymon**. This implements the split requested in Issue #33.\n',
        '## Decision\n']
    passing=[b for b in BOTS if data['candidates'][b]['passes_local_gate']]
    decision='Only passing candidates qualify for main Claude’s guarded ranked review.' if passing else 'None meets the agreed retention rule; retain v21e as the benchmark control.'
    report+=['Local gate passed: **'+(', '.join(passing) if passing else 'none')+'**. '+decision+' Passing requires more wins on both frozen panels and zero reported own bot faults. Any combined policy needs its own comparison.\n',
        '## Complete panels\n',
        'cambc2.2.4, release mode, 17 maps × both sides × five opponents per set. **1,700 completed games**: 340 baseline and 340 per candidate. Same map hashes, engine build and seeds were checked for each candidate/baseline pairing. No submitted bots or platform match groups were created.\n']
    rows=[]
    for bot,g in groups.items():
        rows.append([bot,f"{g['tuning']['wins']}/170",f"{g['heldout']['wins']}/170",
            f"{g['tuning']['mean_margin']:+.2f}",f"{g['heldout']['mean_margin']:+.2f}",
            g['tuning']['own_faults']+g['heldout']['own_faults'],
            'control' if bot=='v21e' else 'pass' if bot in passing else 'reject this candidate'])
    report+=[table(['Bot','Tuning wins','Held-out wins','Tuning mean margin','Held-out mean margin','Own bot faults','Local gate'],rows),
        'Margins are **per-game submitted-gem differences**. The earlier +1663 baseline figure is the sum of the five opponent means: 5 × +332.56 = +1662.82, rounded. It is not a different baseline result.\n',
        'The disabled adapter control compiles to the **same release Wasm bytes as v21e**: SHA-256 `a569e467d5c1184d7f2a50e1016113050be7a03811109667319da12d99fc277e`. All four release builds and native strict C++20/UBSan policy checks passed.\n',
        '## Paired changes\n']
    rows=[]
    for b in BOTS:
        for cohort,p in data['candidates'][b]['paired'].items():
            rows.append([b,cohort,p['gained_wins'],p['lost_wins'],f"{p['margin_delta']:+.2f}"])
    report+=[table(['Candidate','Panel','Loss→win','Win→loss','Mean margin change'],rows),
        'These are deterministic matched scenarios, not a random sample of the ranked population. A small panel gain does not establish ladder strength. The earlier health-build ordering failure remains relevant.\n',
        '## Opponents\n']
    rows=[]
    for cohort in ['tuning','heldout']:
        for opponent in groups['v21e'][cohort]['opponents']:
            rows.append([cohort,opponent]+[f"{groups[b][cohort]['opponents'][opponent]['wins']}/34" for b in ['v21e']+BOTS])
    report+=[table(['Panel','Opponent','v21e']+BOTS,rows),
        'Public repository names do not establish ranked team identity or top-100 strength. Frozen paths/blobs are in opponents.json; opponent sources were used locally and are not committed.\n',
        '## Map results\n',
        'Each cell combines tuning and held-out opponents: **20 games/map**. This is the complete map table, including both gains and regressions.\n']
    rows=[]
    for m in groups['v21e']['tuning']['maps']:
        wins=lambda bot:sum(groups[bot][c]['maps'][m]['wins'] for c in ['tuning','heldout'])
        rows.append([NAMES[m[2:6]],m]+[f"{wins(b)}/20" for b in ['v21e']+BOTS])
    report+=[table(['Map','File','v21e']+BOTS,rows),
        '## Early execution measurements\n',
        'Mean **candidate minus baseline** at sample 150 of the engine’s round timeline, using only pairs where both games contain that sample. Gold and deaths are summed over our champions; banking is submitted gems. These measurements describe associated changes; they do not prove the cause of a win.\n']
    rows=[]
    for b in BOTS:
        for cohort,p in data['candidates'][b]['paired'].items():
            m=p['at150_mean_delta']
            rows.append([b,cohort,p['at150_common_games']]+[f"{m.get(k,0):+.2f}" for k in ['earnedGold','spentGold','deaths','collectedGems','submittedGems']])
    report+=[table(['Candidate','Panel','Common games','Gold earned','Gold spent','Deaths','Gems collected','Gems banked'],rows),
        '## Interpretation and next changes\n',
        '**Our recommendation:** test the task-memory repair separately next. Task state is the closest candidate, but its held-out gains and losses cancel; rushbait falls from 11/20 to 9/20. Cycle scoring improves monolith (13→17) and ambush (17→20) while losing interlock (19→15) and packs (16→13). Its extra early gold is accompanied by lower early spending in both sets, so income alone has not established faster useful power. These are paired observations, not proof of one cause.\n',
        '**The central weakness remains:** contest is 5/20 for the baseline, cycle and task candidates, and 6/20 for siege. These public-bot games do not replace the top-100 audit, but none of our four changes resolves that map. Centre income/control remains in main Claude’s separate queue.\n',
        '- **Cycle:** tests occupied-body cost, travel/respawn overlap, selective recipients and fractional recovery inside the existing pack controller. It retains the parent’s safety gates and gold weight. Assigned living squad members are an approximation of workers; recovery and future helper release are estimates, not measured promises.\n',
        '- **Task:** tests observed versus unknown camp knowledge, bounded capture progress/holding, and a death reset together as one execution-policy change. A gain does not isolate which of those repairs helped. The next ablation should separate memory from capture/death state.\n',
        '- **Capture:** this implementation rejects every carrying champion during election. **Static failure case:** if all locally eligible champions carry a small bag that does not trigger bank(), no new owner is eligible, so the reward can remain unclaimed. This is a code-level counterexample, not a demonstrated cause of every lost match. A follow-up should allow non-channeling small-bag carriers, then compare on a fresh panel; do not retain this candidate merely because one map improves.\n',
        '- **Siege:** safe firing goals and immediate kill→capture are bundled. Empty safe sets preserve the melee approach. Movement goals do not prove the entire path safe, and only visible threats are modeled. Separate final-kill completion from safe-position selection before attributing a result to geometry.\n',
        'A concrete **untested** capture repair is provided in [followups/capture-small-bags.patch](followups/capture-small-bags.patch): remove `c.gem_count()>0` from both owner invalidation and candidate rejection, retaining recall/submit invalidation. bank() still runs first; a small bag alone should not invalidate a productive capture owner. The patch passes `git apply --check` and was not applied to the measured snapshots.\n',
        '## Replay review queue\n',
        'Examples below select the largest absolute margin change among outcome flips for each candidate/panel. Full paired outcomes, hashes, seeds and round counts are in paired-games.csv. Reproduce a row with its two bot folders, map and side using cambc run --release; raw local stats/replays are retained under results/<bot>/.\n']
    rows=[]
    for b in BOTS:
        for cohort in ['tuning','heldout']:
            for flip in ['gain','loss']:
                choices=[p for p in paired if p['bot']==b and p['cohort']==cohort and p['flip']==flip]
                if choices:
                    p=max(choices,key=lambda x:abs(float(x['margin_delta'])))
                    rows.append([b,cohort,flip,p['opponent'],p['map_name'],p['side'],p['baseline_margin'],p['margin']])
    report+=[table(['Candidate','Panel','Flip','Opponent','Map','Our side','Old margin','New margin'],rows),
        '## Reproduction and provenance\n',
        'See README.md, opponents.json, comparison.json, paired-games.csv and the five freeze JSON files. Parent commit: `76d0d2617c58a2fce8d8130a513ea26383ef60ef`. The parent tuning result reproduced Claude’s 127/170, including 20/34 vs Daniel7. Exact public snapshots are pinned here; equality with Claude’s unpublished original opponent revisions is not claimed.\n',
        'No source drift was detected during these runs. All 151 opponent source imports were verified against their public Git blob plus the measured final-LF normalization. Raw match statistics/replays are generated locally rather than committed. Candidate source and result snapshots remain reviewable on this branch.\n']
    (OUT/'RESULTS.md').write_text('\n'.join(report))
    print(OUT/'RESULTS.md')
if __name__=='__main__':
    main()

