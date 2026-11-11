from pathlib import Path
import json,csv,collections,zipfile,hashlib,argparse
ap=argparse.ArgumentParser();ap.add_argument("--main-only",action="store_true");ap.add_argument("--core-only",action="store_true");args=ap.parse_args();assert not(args.main_only and args.core_only)
prefix="main_" if args.main_only else "core_" if args.core_only else ""
directories=["int_results"] if args.main_only else ["core_results"] if args.core_only else ["int_results","core_results"]
r=Path.cwd();out=r/'results/integrated-v71-2026-11-10';rows=[]
def at(t,round):
 n=0
 for v in t['runs']:
  n+=v['duration']
  if round<n:return float(v['value'])
 return float(t['runs'][-1]['value'])
for directory in directories:
 for p in sorted((r/directory).glob('*.json')):
  c,o,m,side=p.stem.split('__');side=int(side);team=['teamA','teamB'][side];other=['teamB','teamA'][side];x=json.load(p.open());meta=x['match']
  assert meta['engineVersion']=='3.0.0' and meta['engineBuildHash']=='96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd'
  champs=[v for v in x['champions'] if v['team']==team];gems={v['team']:int(v['submittedGems']) for v in x['teams']};draft=[v['champion'] for v in x['roster']['draft'] if v['team']==team];assert len(draft)==len(set(draft))
  row=dict(tier='all-maps' if directory=='int_results' else 'eight-map-forced-core',candidate=c,opponent=o,map=m,side=side,win=int(meta['outcome']==team),outcome=meta['outcome'],banked=gems[team],margin=gems[team]-gems[other],draft=' | '.join(draft),size=len(draft),core=int('Cassi & Issac' in draft),map_hash=meta['mapHash'],seed=meta['seed'],engine=meta['engineVersion'],engine_build=meta['engineBuildHash'],rounds=meta['roundsStarted'])
  for k in ['deaths','kills','earnedGold','monsterDamageDone','championDamageDone','submittedGems']:row[k]=sum(float(v['metrics'][k]) for v in champs)
  for round in [50,100,200]:
   for k in ['earnedGold','spentGold','deaths']:row[k+str(round)]=sum(at(t,round) for t in x['championTimelines'] if t['metric']==k and t['owner'].get('team')==team)
  row['pair_deaths']=sum(float(v['metrics']['deaths']) for v in champs if v['name'] in ['Cassi','Issac'])
  for name in ['Cassi','Issac','Heart of Ruin','Varg','Vendetta']:
   for metric in ['earnedGold','monsterDamageDone','championDamageDone']:
    row[name+'_'+metric]=sum(float(v['metrics'][metric]) for v in champs if v['name']==name)
  for kind in ['botFault','fuelExhausted']:
   row[kind]=sum(len(t['entries']) for t in x['events'] if t['kind']==kind and t['owner'].get('team')==team);row[kind+'_both']=sum(len(t['entries']) for t in x['events'] if t['kind']==kind)
  log=zipfile.ZipFile(p.with_suffix('.repl26a')).read('team-a.stdout' if side==0 else 'team-b.stdout').decode(errors='replace').replace('\x00','')
  row['early_fuel200']=sum(sum(int(e['timestamp']['round'])<=200 for e in t['entries']) for t in x['events'] if t['kind']=='fuelExhausted' and t['owner'].get('team')==team)
  row['pair_fuel']=sum(len(t['entries']) for t in x['events'] if t['kind']=='fuelExhausted' and t['owner'].get('team')==team and t['owner'].get('name') in ['Cassi','Issac'])
  row['pair_rejections']=log.count('pair action rejected:');row['turn_errors']=log.count('turn error');row['region_loaded']=log.count('REGION anchor')
  rows.append(row)
expected={('all-maps',c,o):256 for c in ['v71a','cg-v72-integrated'] for o in ['v71a','v66i','v50p1']} if not args.core_only else {}
if not args.main_only:expected.update({('eight-map-forced-core','cg-v72-core-control',o):16 for o in ['v71a','v50p1']})
actual=collections.Counter((v['tier'],v['candidate'],v['opponent']) for v in rows)
assert dict(actual)==expected,(actual,expected)
assert len({(v['tier'],v['candidate'],v['opponent'],v['map'],v['side']) for v in rows})==len(rows)
assert all(v['rounds']>2 for v in rows)
with (out/(prefix+'cases.csv')).open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
groups=collections.defaultdict(list)
for v in rows:groups[v['tier']+' / '+v['candidate']+' vs '+v['opponent']].append(v)
s={}
for k,vs in groups.items():
 fields=['banked','margin','deaths','kills','earnedGold50','earnedGold100','earnedGold200','spentGold200','deaths200','pair_deaths','monsterDamageDone','Cassi_championDamageDone','Varg_earnedGold']
 s[k]={'n':len(vs),'wins':sum(v['win'] for v in vs),'core_games':sum(v['core'] for v in vs),**{f:sum(v[f] for v in vs)/len(vs) for f in fields},**{f:sum(v[f] for v in vs) for f in ['botFault','botFault_both','fuelExhausted','fuelExhausted_both','pair_rejections','turn_errors','region_loaded','early_fuel200','pair_fuel']}}
base={(v['opponent'],v['map'],v['side']):v for v in rows if v['candidate']=='v71a' and v['tier']=='all-maps'};paired={}
for o in ([] if args.core_only else ['v71a','v66i','v50p1']):
 vs=[v for v in rows if v['candidate']=='cg-v72-integrated' and v['opponent']==o];up=down=0
 for v in vs:
  b=base[o,v['map'],v['side']];assert b['seed']==v['seed'] and b['map_hash']==v['map_hash'];up+=v['win']>b['win'];down+=v['win']<b['win']
 paired[o]={'pairs':len(vs),'loss_to_win':up,'win_to_loss':down}
cohorts={}
for o in ([] if args.core_only else ['v71a','v66i','v50p1']):
 for core in [0,1]:
  vs=[v for v in rows if v['candidate']=='cg-v72-integrated' and v['opponent']==o and v['core']==core]
  bs=[base[o,v['map'],v['side']] for v in vs]
  fs=['win','margin','earnedGold50','earnedGold100','earnedGold200','spentGold200','deaths200','deaths','fuelExhausted','monsterDamageDone']
  cohorts[o+(' / selected core' if core else ' / retained original')]={'n':len(vs),'maps':len(set(v['map'] for v in vs)),**{f:{'candidate':sum(v[f] for v in vs)/len(vs),'base':sum(v[f] for v in bs)/len(bs)} for f in fs}}
result={'total':len(rows),'summary':s,'paired':paired,'cohorts':cohorts};(out/(prefix+'summary.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
families=collections.defaultdict(lambda:[0,0])
for v in rows:
 if v['tier']=='all-maps':z=families[v['candidate'],v['opponent'],v['map'][:2]];z[0]+=1;z[1]+=v['win']
with (out/(prefix+'families.csv')).open('w') as f:
 w=csv.writer(f);w.writerow(['candidate','opponent','family','games','wins']);w.writerows([*k,*v] for k,v in sorted(families.items()))
