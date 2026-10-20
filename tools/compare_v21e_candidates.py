#!/usr/bin/env python3
"""Paired comparison of the completed frozen v21e candidate panels."""
import contextlib
import csv
import importlib.util
import io
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BOTS=['cg_cycle','cg_task','cg_capture','cg_siege']
NAMES=dict(zip(['25d8','2e98','3991','3a5c','3e2d','699c','7bfc','8192','9385','9925','b135','b777','bb12','df22','e3c2','f2b6','f930'],
 ['rows','collision','monolith','contest','eight','ambush','pilgrimage','expanse','lanes','fragment','packs','interlock','elkring','rushbait_v2','corners','stampede','swirl']))

def key(row):
    return (row['cohort'],row['opponent'],row['map'],row['side'])

def at(timeline, sample):
    if timeline['sampleCount']<=sample:
        return None
    elapsed=0
    for run in timeline['runs']:
        elapsed+=run['duration']
        if sample<elapsed:
            return float(run['value'])
    return None

def metrics(path, side, sample=150):
    d=json.loads(Path(path).read_text())
    own='teamA' if side=='A' else 'teamB'
    totals={m:0 for m in ['earnedGold','spentGold','deaths','collectedGems','submittedGems']}
    valid=True
    for t in d['championTimelines']:
        if t['owner']['team']!=own or t['metric'] not in totals:
            continue
        value=at(t,sample)
        if value is None:
            valid=False
        else:
            totals[t['metric']]+=value
    return totals if valid else None

def main():
    spec=importlib.util.spec_from_file_location('bench',ROOT/'tools/bench_v21e_candidates.py')
    bench=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)
    summaries={}
    for bot in ['v21e']+BOTS:
        with contextlib.redirect_stdout(io.StringIO()):
            if not bench.summarize(bot,bench.rows_for(bot)):
                raise RuntimeError(f'{bot}: panel incomplete; not publishing a final comparison')
        summaries[bot]=json.loads((ROOT/'results'/bot/'summary.json').read_text())
    base={key(g):g for g in summaries['v21e']['games']}
    baseline_metrics={k:metrics(g['statistics'],g['side']) for k,g in base.items()}
    output={'baseline':summaries['v21e']['groups'],'candidates':{},'games':[]}
    for bot in BOTS:
        result={'groups':summaries[bot]['groups'],'paired':{}}
        for cohort in ['tuning','heldout']:
            pairs=[]
            for g in summaries[bot]['games']:
                if g['cohort']!=cohort:
                    continue
                b=base[key(g)]
                for field in ['seed','engine_build','map_hash']:
                    if g[field]!=b[field]:
                        raise RuntimeError(f'{bot}: mismatched {field} on {key(g)}')
                flip='gain' if g['result']=='wins' and b['result']!='wins' else 'loss' if b['result']=='wins' and g['result']!='wins' else 'same'
                pair=dict(bot=bot,cohort=cohort,opponent=g['opponent'],map=g['map'],map_name=NAMES[g['map'][2:6]],side=g['side'],
                    baseline_result=b['result'],result=g['result'],flip=flip,baseline_margin=b['margin'],margin=g['margin'],
                    margin_delta=g['margin']-b['margin'],own_faults=g['own_faults'],opponent_faults=g['opponent_faults'],
                    baseline_rounds=b['rounds'],rounds=g['rounds'],seed=g['seed'],engine_build=g['engine_build'],map_hash=g['map_hash'])
                early=metrics(g['statistics'],g['side'])
                before=baseline_metrics[key(g)]
                if early is not None and before is not None:
                    pair['at150_delta']={m:early[m]-before[m] for m in early}
                pairs.append(pair)
                output['games'].append(pair)
            goldpairs=[p['at150_delta'] for p in pairs if 'at150_delta' in p]
            result['paired'][cohort]=dict(gained_wins=sum(p['flip']=='gain' for p in pairs),lost_wins=sum(p['flip']=='loss' for p in pairs),
                margin_delta=sum(p['margin_delta'] for p in pairs)/len(pairs),
                at150_common_games=len(goldpairs),
                at150_mean_delta={m:sum(p[m] for p in goldpairs)/len(goldpairs) for m in goldpairs[0]} if goldpairs else {})
        result['passes_local_gate']=all(result['groups'][c]['wins']>output['baseline'][c]['wins'] for c in ['tuning','heldout']) and all(result['groups'][c]['own_faults']==0 for c in ['tuning','heldout'])
        output['candidates'][bot]=result
    out=ROOT/'research/v21e-candidates'
    aggregate={k:v for k,v in output.items() if k!='games'}
    (out/'comparison.json').write_text(json.dumps(aggregate,indent=2)+'\n')
    early_fields=['earnedGold','spentGold','deaths','collectedGems','submittedGems']
    fields=[x for x in output['games'][0] if x!='at150_delta']+[m+'150_delta' for m in early_fields]
    with (out/'paired-games.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
        writer.writeheader()
        for game in output['games']:
            for metric,value in game.get('at150_delta',{}).items():
                game[metric+'150_delta']=value
            writer.writerow(game)
    print(json.dumps({b:{'gate':v['passes_local_gate'],'paired':v['paired']} for b,v in output['candidates'].items()},indent=2))

if __name__=='__main__':
    main()

