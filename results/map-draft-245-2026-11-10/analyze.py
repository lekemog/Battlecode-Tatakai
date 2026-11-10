from pathlib import Path
import json,csv,collections,re,zipfile,hashlib
r=Path.cwd();out=r/'results/map-draft-245-2026-11-10';rows=[]
def at(t,round):
 n=0
 for run in t['runs']:
  n+=run['duration']
  if round<n:return float(run['value'])
 return float(t['runs'][-1]['value'])
for p in sorted((r/'md_results').glob('*.json')):
 c,o,m,side=p.stem.split('__');side=int(side);team=['teamA','teamB'][side];other=['teamB','teamA'][side];x=json.load(p.open());meta=x['match']
 assert meta['engineVersion']=='3.0.0' and meta['engineBuildHash']=='96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd'
 champs=[v for v in x['champions'] if v['team']==team];gems={v['team']:int(v['submittedGems']) for v in x['teams']};draft=[v['champion'] for v in x['roster']['draft'] if v['team']==team]
 assert len(draft)==len(set(draft))
 row=dict(candidate=c,opponent=o,map=m,side=side,win=int(meta['outcome']==team),outcome=meta['outcome'],margin=gems[team]-gems[other],banked=gems[team],seed=meta['seed'],map_hash=meta['mapHash'],draft_size=len(draft),draft=' | '.join(draft),composition=' | '.join(sorted(draft)),rounds=meta['roundsStarted'],engine=meta['engineVersion'],engine_build=meta['engineBuildHash'])
 for key in ['deaths','kills','earnedGold','monsterDamageDone','championDamageDone']:row[key]=sum(float(v['metrics'][key]) for v in champs)
 for round in [50,100,200]:
  for key in ['earnedGold','spentGold','deaths']:row[key+str(round)]=sum(at(t,round) for t in x['championTimelines'] if t['metric']==key and t['owner'].get('team')==team)
 for kind in ['botFault','fuelExhausted']:
  row[kind]=sum(len(t['entries']) for t in x['events'] if t['kind']==kind and t['owner'].get('team')==team);row[kind+'_both']=sum(len(t['entries']) for t in x['events'] if t['kind']==kind)
 log=zipfile.ZipFile(p.with_suffix('.repl26a')).read('team-a.stdout' if side==0 else 'team-b.stdout').decode(errors='replace').replace('\x00','')
 row['turn_errors']=log.count('turn error');row['draft_fallback']=log.count('MDFALLBACK')+log.count('map draft fallback:')
 rows.append(row)
if not rows:raise SystemExit('No complete games yet')
with (out/'cases.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
groups=collections.defaultdict(list)
for row in rows:groups[row['candidate']+' vs '+row['opponent']].append(row)
summary={}
for k,rs in groups.items():
 numeric=['banked','margin','deaths','kills','earnedGold50','earnedGold100','earnedGold200','spentGold200','deaths200']
 summary[k]={'n':len(rs),'wins':sum(v['win'] for v in rs),'draws':sum(v['outcome'] not in ['teamA','teamB'] for v in rs),**{a:sum(v[a] for v in rs)/len(rs) for a in numeric},**{a:sum(v[a] for v in rs) for a in ['botFault','botFault_both','fuelExhausted','fuelExhausted_both','turn_errors','draft_fallback']}}
base={(v['opponent'],v['map'],v['side']):v for v in rows if v['candidate']=='v61j'};paired={}
for c in ['cg-md245-plan','cg-md245-react']:
 for o in ['v61j','v50p1']:
  rs=[v for v in rows if v['candidate']==c and v['opponent']==o and (o,v['map'],v['side']) in base];up=down=0
  for v in rs:
   b=base[o,v['map'],v['side']];assert b['map_hash']==v['map_hash'] and b['seed']==v['seed'];up+=v['win']>b['win'];down+=v['win']<b['win']
  paired[c+' vs '+o]={'pairs':len(rs),'loss_to_win':up,'win_to_loss':down}
result={'total':len(rows),'summary':summary,'paired':paired};(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
family=collections.defaultdict(lambda:[0,0])
for v in rows:z=family[v['candidate'],v['opponent'],v['map'][:2]];z[0]+=1;z[1]+=v['win']
with (out/'families.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['candidate','opponent','family','games','wins']);w.writerows([*k,*v] for k,v in sorted(family.items()))
