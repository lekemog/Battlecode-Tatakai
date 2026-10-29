import json, math, statistics, hashlib, sys
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
out=root/'results/audit';out.mkdir(exist_ok=True)
plan=json.loads((root/'results/experiment-plan.json').read_text())
cache_path=out/'local-games.json';cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
for folder in ['robustness','new-map-validation','baseline-validation','learned-ablation']:
 p=root/'results'/folder
 if not (p/'index.json').exists():continue
 for row in json.loads((p/'index.json').read_text()):
  key=folder+'/'+row['tag']
  if key in cache:continue
  path=p/(row['tag']+'.json')
  if not path.exists():continue
  try:s=json.loads(path.read_text())
  except json.JSONDecodeError:continue
  side=row['side'];other='teamB' if side=='teamA' else 'teamA'
  r=dict(row,dataset=folder,win=s['match']['outcome']==side,rounds=s['match']['roundsStarted'],seed=s['match']['seed'],engine=s['match']['engineVersion'],build=s['match']['engineBuildHash'],map_hash=s['match']['mapHash'])
  for label,team in [('us',side),('them',other)]:
   for k in ['submittedGems','collectedGems','gems','deaths','earnedGold']:
    r[label+'_'+k]=sum(float(c['metrics'].get(k,0)) for c in s['champions'] if c['team']==team)
   for k in ['botFault','fuelExhausted','gemSubmission']:
    r[label+'_'+k]=sum(len(b['entries']) for b in s['events'] if b['kind']==k and b['owner'].get('team')==team)
  cache[key]=r
cache_path.write_text(json.dumps(cache,indent=2))
rows=list(cache.values())
def agg(rs):
 return {'games':len(rs),'wins':sum(r['win'] for r in rs),'gem_margin':round(statistics.mean(r['us_submittedGems']-r['them_submittedGems'] for r in rs),2) if rs else None,'our_faults':sum(r['us_botFault'] for r in rs),'opponent_faults':sum(r['them_botFault'] for r in rs),'our_fuel':sum(r['us_fuelExhausted'] for r in rs)}
summary={}
for bot in [plan['baseline']]+plan['candidates']:
 rs=[r for r in rows if r['bot']==bot]
 summary[bot]={cohort:agg([r for r in rs if pred(r)]) for cohort,pred in {
  'all':lambda r:True,'old_maps':lambda r:r['dataset']=='robustness','new_maps':lambda r:r['dataset']=='new-map-validation',
  'tuning':lambda r:r['tuning_map'] and not r['holdout_opponent'],'held_maps':lambda r:not r['tuning_map'] and not r['holdout_opponent'],
  'held_opponent':lambda r:r['holdout_opponent']}.items()}
(out/'local-summary.json').write_text(json.dumps(summary,indent=2))
print('completed',len(rows));print(json.dumps({b:v['all'] for b,v in summary.items()},indent=2))
# Keep historical cohorts separate: versions/opponent selection/engine differ.
history=[]
for f,name in [('history-fish_cache_9c16b699.json','legacy-ranked-21oct'),('history-scrim_cache.json','v24z-top4'),('history-scrim_cache_v24z.json','v24z-top4'),('history-scrim_cache_v25a.json','v25a-top4'),('history-scrim_cache_v25c.json','v25c-top4')]:
 for mid,r in json.loads((root/'results'/f).read_text()).items():history.append({'id':mid,'cohort':name,'map':r['map'],'win':r['result']=='win'})
for r in json.loads((root/'results/history-top_vs_us_features.json').read_text()):
 if r['label']=='US':history.append({'id':r['file'].removesuffix('.json'),'cohort':'legacy-US-features','map':r['map'],'win':r['win']})
for r in json.loads((root/'results/online-top10.json').read_text()):history.append({'id':r['id'],'cohort':'v221-top10-28oct','map':r['map'],'win':r['win']})
seen=set();unique=[]
for r in reversed(history):
 if r['id'] in seen:continue
 seen.add(r['id']);unique.append(r)
(out/'historical-games.json').write_text(json.dumps(unique,indent=2))
print('unique historical games',len(unique))
