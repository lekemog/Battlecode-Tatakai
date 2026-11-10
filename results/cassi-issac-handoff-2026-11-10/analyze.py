import pathlib,json,csv,collections,hashlib,zipfile,re
r=pathlib.Path.cwd();out=r/'results/cassi-issac-handoff-2026-11-10';rows=[]
def at(t,round):
 n=0
 for x in t['runs']:
  n+=x['duration']
  if round<n:return float(x['value'])
 return float(t['runs'][-1]['value'])
for p in sorted((r/'ci_results').glob('*.json')):
 c,o,m,side=p.stem.split('__');side=int(side);team=['teamA','teamB'][side];other=['teamB','teamA'][side];x=json.load(p.open());meta=x['match']
 assert meta['engineVersion']=='3.0.0' and meta['engineBuildHash']=='96ce858f548c14560eff737967a691a30eaf0a469afd1f4f400f125e094bd1fd'
 champs=[v for v in x['champions'] if v['team']==team];pair=[v for v in champs if v['name'] in ['Cassi','Issac']];assert len(pair)==2,[v['name'] for v in champs]
 gems={v['team']:int(v['submittedGems']) for v in x['teams']}
 row=dict(candidate=c,opponent=o,map=m,side=side,win=int(meta['outcome']==team),margin=gems[team]-gems[other],seed=meta['seed'],map_hash=meta['mapHash'],engine=meta['engineVersion'],engine_build=meta['engineBuildHash'])
 for key in ['deaths','kills','earnedGold','championDamageDone','monsterDamageDone']:
  row[key]=sum(float(v['metrics'][key]) for v in champs);row['pair_'+key]=sum(float(v['metrics'][key]) for v in pair)
 for key in ['earnedGold','spentGold','deaths','championDamageDone','monsterDamageDone']:
  row[key+'200']=sum(at(t,200) for t in x['championTimelines'] if t['metric']==key and t['owner'].get('team')==team)
  row['pair_'+key+'200']=sum(at(t,200) for t in x['championTimelines'] if t['metric']==key and t['owner'].get('team')==team and t['owner'].get('name') in ['Cassi','Issac'])
 for kind in ['botFault','fuelExhausted']:
  row[kind]=sum(len(t['entries']) for t in x['events'] if t['kind']==kind and t['owner'].get('team')==team)
  row[kind+'_both']=sum(len(t['entries']) for t in x['events'] if t['kind']==kind)
 z=zipfile.ZipFile(p.with_suffix('.repl26a'));log=z.read('team-a.stdout' if side==0 else 'team-b.stdout').decode(errors='replace').replace('\x00','')
 row['pair_rejections']=log.count('pair action rejected:');row['turn_errors']=log.count('turn error')
 rows.append(row)
with (out/'cases.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
groups=collections.defaultdict(list)
for row in rows:groups[row['candidate']+' vs '+row['opponent']].append(row)
summary={}
for k,rs in groups.items():
 numeric=['margin','deaths','pair_deaths','earnedGold200','spentGold200','pair_earnedGold200','pair_championDamageDone200','pair_monsterDamageDone200']
 summary[k]={'n':len(rs),'wins':sum(v['win'] for v in rs),**{a:sum(v[a] for v in rs)/len(rs) for a in numeric},**{a:sum(v[a] for v in rs) for a in ['botFault','botFault_both','fuelExhausted','fuelExhausted_both','pair_rejections','turn_errors']}}
paired={};base={(v['opponent'],v['map'],v['side']):v for v in rows if v['candidate']=='cg-ci-draft'}
for c in ['cg-ci-pair','cg-ci-shop']:
 for o in ['v61j','v50p1']:
  rs=[v for v in rows if v['candidate']==c and v['opponent']==o];up=down=0
  for v in rs:
   b=base[o,v['map'],v['side']];assert b['seed']==v['seed'] and b['map_hash']==v['map_hash'];up+=v['win']>b['win'];down+=v['win']<b['win']
  paired[c+' vs '+o]={'pairs':len(rs),'loss_to_win':up,'win_to_loss':down}
result={'total':len(rows),'summary':summary,'paired':paired};(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
hashes={}
for c in ['cg-ci-draft','cg-ci-pair','cg-ci-shop','v61j','v50p1']:
 for p in (r/'bots'/c).rglob('*'):
  if p.is_file() and (p.parent.name=='src' or p.suffix=='.wasm'):hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
for name in sorted(set(v['map'] for v in rows)):
 p=r/'maps'/(name+'.map26a');hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/'hashes.json').write_text(json.dumps(hashes,indent=2))
