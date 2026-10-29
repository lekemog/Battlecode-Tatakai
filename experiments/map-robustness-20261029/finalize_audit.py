import json, statistics, collections, random, math, re, hashlib, sys
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
out=root/'results/audit'
cache=json.loads((out/'local-games.json').read_text());rows=[r for r in cache.values() if r['dataset']!='learned-ablation']
expected=2800
assert len(rows)==expected,(len(rows),expected)
assert len({(r['engine'],r['build']) for r in rows})==1
assert all(r['engine']=='2.0.0' for r in rows)
for folder,n in [('robustness',1200),('new-map-validation',900),('baseline-validation',700)]:
 assert sum(r['dataset']==folder for r in rows)==n
baseline={ (r['dataset'],r['opponent'],r['map'],r['side']):r for r in rows if r['bot']=='v50c'}
bots=['v50c','v50c-hazard-history','v50c-ring-carrier','v50c-danger-bank','v50c-combined']
def summary(rs):
 return {'games':len(rs),'wins':sum(r['win'] for r in rs),'margin':round(statistics.mean(r['us_submittedGems']-r['them_submittedGems'] for r in rs),2),'deaths':round(statistics.mean(r['us_deaths'] for r in rs),2),'faults':sum(r['us_botFault'] for r in rs),'fuel':sum(r['us_fuelExhausted'] for r in rs)}
def name(m):return re.sub(r'^\d\d','',m).replace('-','_')
stats={};deltas={}
for bot in bots:
 a=[r for r in rows if r['bot']==bot]
 assert len(a)==560
 filters={'all':lambda r:True,'old_weak':lambda r:r['dataset']=='robustness','new_weak':lambda r:r['dataset']=='new-map-validation','direct_v50c':lambda r:r['dataset']=='baseline-validation','tuning':lambda r:r['dataset']=='robustness' and r['tuning_map'] and not r['holdout_opponent'],'held_old_maps':lambda r:r['dataset']=='robustness' and not r['tuning_map'] and not r['holdout_opponent'],'mohnish':lambda r:r['opponent']=='h_mohnish'}
 stats[bot]={k:summary([r for r in a if pred(r)]) for k,pred in filters.items()}
 regress=collections.defaultdict(lambda:[0,0,0.0])
 paired=[];up=down=0
 for r in a:
  b=baseline[(r['dataset'],r['opponent'],r['map'],r['side'])]
  assert (r['map_hash'],r['seed'])==(b['map_hash'],b['seed'])
  delta=int(r['win'])-int(b['win']);up+=delta>0;down+=delta<0
  md=(r['us_submittedGems']-r['them_submittedGems'])-(b['us_submittedGems']-b['them_submittedGems'])
  regress[name(r['map'])][0]+=delta;regress[name(r['map'])][1]+=1;regress[name(r['map'])][2]+=md
  paired.append({'map':name(r['map']),'delta':delta,'margin_delta':md})
 # Resample whole maps, keeping sides/opponents coupled; descriptive sensitivity interval.
 grouped=collections.defaultdict(list)
 for r in paired:grouped[r['map']].append(r['delta'])
 keys=sorted(grouped);rng=random.Random(20261029);samples=[]
 for _ in range(5000):
  chosen=[rng.choice(keys) for __ in keys]
  samples.append(sum(sum(grouped[k]) for k in chosen)/sum(len(grouped[k]) for k in chosen)*100)
 samples.sort()
 deltas[bot]={'improved_cases':up,'regressed_cases':down,'map_block_delta_interval_pp':[round(samples[125],2),round(samples[4874],2)],'per_map':dict(regress)}
(out/'comparison.json').write_text(json.dumps({'summary':stats,'paired':deltas},indent=2))
lines=['# Completed map-robustness experiments — 29 October 2026','','**2,800 completed local engine games**, five fixed policies, 70 unique active map layouts, four opponents including unchanged v50c, both sides. No bot was deployed. Exact source/map hashes, frozen plans, patches and per-case metrics accompany this report.','', '## Results','','| Policy | Old 40 maps vs 3 bots | Extra 30 maps vs 3 bots | Direct v50c across 70 maps | Total | Our faults |','|---|---:|---:|---:|---:|---:|']
for bot in bots:
 s=stats[bot];lines.append('| '+bot+' | '+' | '.join(f"{s[k]['wins']}/{s[k]['games']}" for k in ['old_weak','new_weak','direct_v50c','all'])+f" | {s['all']['faults']} |")
lines+=['','The three frozen opponents are Daniel v8, DE41H v4 and Mohnish from our repository benchmark. They are much weaker than current top-ten teams. The direct v50c column includes a 70/140 self-play control for unchanged v50c. A win-count edge here is not a ladder-strength estimate.','', '## Paired changes relative to baseline','','Every comparison checks identical map hash, default engine seed, opponent and our side. Outcomes are paired; deterministic repeats do not create new independent evidence. Whole-map bootstrap intervals below are descriptive sensitivity estimates, not proof of generalisation or a correction for trying multiple candidates.','','| Policy | Baseline losses converted | Baseline wins lost | Map-block delta interval, percentage points |','|---|---:|---:|---|']
for b in bots[1:]:
 d=deltas[b];lines.append(f"| {b} | {d['improved_cases']} | {d['regressed_cases']} | {d['map_block_delta_interval_pp']} |")
lines+=['','## Per-map net win changes','','Counts below sum eight matched cases per map: three frozen opponents plus v50c, both sides. Names are display-normalized; exact hashes and source names remain in local-games.json.','','| Map | History | Carrier gate | Danger bank | Combined |','|---|---:|---:|---:|---:|']
for m in sorted(deltas['v50c']['per_map']):
 lines.append('| '+m+' | '+' | '.join(str(deltas[b]['per_map'][m][0]) for b in bots[1:])+' |')
lines+=['','## Validation splits','','| Policy | Tuning maps / first 2 bots | Withheld old maps / first 2 bots | Withheld Mohnish across 70 |','|---|---:|---:|---:|']
for b in bots:
 lines.append('| '+b+' | '+' | '.join(f"{stats[b][k]['wins']}/{stats[b][k]['games']}" for k in ['tuning','held_old_maps','mohnish'])+' |')
lines+=['','## Interpretation and limits','','Use the accompanying map-history and design-review reports to prioritise actual ladder problems. The old bench omitted 30 active layouts and is saturated against these opponents. Current v221 top-ten results (5/50) and historical cohorts are separate from this local evaluation. A high local win rate therefore cannot certify a fix.','', 'The candidates were not altered after results were inspected. The added-map set lies outside the old benchmark; some maps had already appeared in online loss analysis, so it is not a perfectly research-naive holdout. The old baseline may have been tuned on the old maps and bench opponents. A single deterministic engine seed is used per case; unseen seeds and stronger real opponents remain necessary before deploying.','', 'History validity is a confirmed logic repair. Carrier-relative ring routing and a 10-gem danger threshold remain policy experiments; combining them with history is independently measured. Reject broad regressions and do not rescue a weak combination by adding map-name selectors. Stronger/new opponent snapshots are the next priority for the evaluation suite.']
(out/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({b:stats[b]['all'] for b in bots},indent=2))
