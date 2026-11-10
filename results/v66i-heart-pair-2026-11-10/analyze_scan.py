from pathlib import Path
import zipfile,re,csv,json,collections
r=Path.cwd();out=r/'results/v66i-heart-pair-2026-11-10';rows=[]
pat=re.compile(r'MDPLAN size(\d+) groups(\d+) walk(\d+) screened(\d+) expected(\d+) refined(\d+) shortlist(\d+) used(\d+) start(\d+)')
for p in sorted((r/'hci_scan').glob('*.repl26a')):
 _,_,m,side=p.stem.split('__');side=int(side);log=zipfile.ZipFile(p).read('team-a.stdout' if side==0 else 'team-b.stdout').decode(errors='replace').replace('\x00','');plans=pat.findall(log);picks=[int(v) for v in re.findall(r'MDPICK p(\d+)',log)]
 row=dict(map=m,side=side,plans=len(plans),logged_picks=' '.join(map(str,picks)),fallback=log.count('MDFALLBACK')+log.count('map draft fallback:'),turn_errors=log.count('turn error'))
 for k in ['size','groups','spawn_walk','screened','expected','refined','shortlist','fuel_used','fuel_start']:row[k]=0
 if plans:
  assert len(plans)==1,(m,side,'unexpected replan')
  for k,v in zip(['size','groups','spawn_walk','screened','expected','refined','shortlist','fuel_used','fuel_start'],plans[0]):row[k]=int(v)
  assert row['screened']==row['expected'],row
  assert len(picks)==len(set(picks))==row['size'],row
  assert 11 in picks and 3 in picks,('missing required core',row)
 rows.append(row)
with (out/'draft_scan.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sets=collections.defaultdict(collections.Counter)
for v in rows:
 if v['plans']:sets[v['size']][tuple(sorted(map(int,v['logged_picks'].split())))]+=1
summary={'scans':len(rows),'planned':sum(v['plans'] for v in rows),'unlogged_or_fallback':sum(not v['plans'] for v in rows),'max_fuel_used':max(v['fuel_used'] for v in rows),'min_initial_fuel':min(v['fuel_start'] for v in rows if v['plans']),'max_fuel_fraction':max(v['fuel_used']/v['fuel_start'] for v in rows if v['plans']),'distinct_compositions_by_size':{str(k):len(v) for k,v in sets.items()},'compositions_by_size':{str(k):{' '.join(map(str,s)):n for s,n in v.items()} for k,v in sets.items()},'turn_errors':sum(v['turn_errors'] for v in rows)}
(out/'draft_scan_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
