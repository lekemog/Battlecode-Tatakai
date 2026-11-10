import csv,json,collections,hashlib
from pathlib import Path
import argparse
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,default=Path('/tmp/pr81lab'));p.add_argument('--output',type=Path,default=Path('/tmp/pr81work'));a=p.parse_args();root=a.project;out=a.output;out.mkdir(parents=True,exist_ok=True);rows=[]
def at(t,r):
 n=0
 for run in t['runs']:
  n+=run['duration']
  if r<n:return float(run['value'])
 return float(t['runs'][-1]['value'])
for p in sorted((root/'eta_results').glob('*.json')):
 try:x=json.load(p.open())
 except json.JSONDecodeError:continue
 c,o,m,side=p.stem.split('__');side=int(side);team=['teamA','teamB'][side];other=['teamB','teamA'][side];meta=x['match']
 assert meta['engineVersion']=='3.0.0' and meta['engineBuildHash']=='96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd'
 champs=[a for a in x['champions'] if a['team']==team];carry=[a for a in champs if a['name']=='Vesper Vale'];gems={a['team']:int(a['submittedGems']) for a in x['teams']}
 row=dict(candidate=c,opponent=o,map=m,side=side,win=int(meta['outcome']==team),outcome=meta['outcome'],banked=gems[team],opp_banked=gems[other],margin=gems[team]-gems[other],rounds=meta['roundsStarted'],map_hash=meta['mapHash'],seed=meta['seed'],engine=meta['engineVersion'],build=meta['engineBuildHash'])
 for k in ['deaths','kills','earnedGold','collectedGems']:
  row[k]=sum(float(a['metrics'][k]) for a in champs)
 for k in ['earnedGold','monsterDamageDone','submittedGems']:
  row['vesper_'+k]=sum(float(a['metrics'][k]) for a in carry)
 row['gold200']=sum(at(t,200) for t in x['championTimelines'] if t['metric']=='earnedGold' and t['owner'].get('team')==team)
 row['vesper_gold200']=sum(at(t,200) for t in x['championTimelines'] if t['metric']=='earnedGold' and t['owner'].get('team')==team and t['owner'].get('name')=='Vesper Vale')
 for kind in ['botFault','fuelExhausted']:
  row[kind]=sum(len(t['entries']) for t in x['events'] if t['kind']==kind and t['owner'].get('team')==team)
  row[kind+'_both']=sum(len(t['entries']) for t in x['events'] if t['kind']==kind)
 rows.append(row)
if rows:
 with (out/'cases.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
groups=collections.defaultdict(list)
for r in rows:groups[r['candidate'],r['opponent']].append(r)
summary={}
for (c,o),rs in groups.items():
 fields=['banked','margin','deaths','kills','earnedGold','collectedGems','gold200','vesper_earnedGold','vesper_gold200','vesper_monsterDamageDone','vesper_submittedGems']
 summary[c+' vs '+o]={'n':len(rs),'wins':sum(r['win'] for r in rs),**{k:round(sum(r[k] for r in rs)/len(rs),3) for k in fields},**{k:sum(r[k] for r in rs) for k in ['botFault','botFault_both','fuelExhausted','fuelExhausted_both']}}
paired={}
for c in ['v60f','v60g']:
 for o in ['v53x','v50p1']:
  b={(r['map'],r['side']):r for r in rows if r['candidate']=='v60d' and r['opponent']==o};cs=[r for r in rows if r['candidate']==c and r['opponent']==o and (r['map'],r['side']) in b];converted=lost=0
  for r in cs:
   base=b[r['map'],r['side']];assert base['map_hash']==r['map_hash'] and base['seed']==r['seed'];converted+=r['win']>base['win'];lost+=r['win']<base['win']
  paired[c+' vs '+o]={'pairs':len(cs),'loss_to_win':converted,'win_to_loss':lost}
result={'total':len(rows),'summary':summary,'paired':paired};(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
