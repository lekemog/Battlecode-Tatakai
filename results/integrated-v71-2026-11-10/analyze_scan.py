from pathlib import Path
import csv,json,re,zipfile,collections
r=Path.cwd();out=r/'results/integrated-v71-2026-11-10';rows=[]
base={3:{6,2,9},4:{11,6,2,9},5:{11,0,6,2,9}}
pat=re.compile(r'MDPLAN size(\d+) groups(\d+) walk(\d+) screened(\d+) expected(\d+) refined(\d+) shortlist(\d+) used(\d+) start(\d+) best(\d+) base(\d+) anchor(-?\d+)')
for p in sorted((r/'draft_scan').glob('*.repl26a')):
 c,o,m,side=p.stem.split('__');side=int(side);log=zipfile.ZipFile(p).read('team-a.stdout' if side==0 else 'team-b.stdout').decode(errors='replace').replace('\x00','');plans=pat.findall(log);picks=[int(v) for v in re.findall(r'MDPICK p(\d+)',log)]
 row=dict(map=m,side=side,plans=len(plans),picks=' '.join(map(str,picks)),core=0,turn_errors=log.count('turn error'))
 for k in ['size','groups','spawn_walk','screened','expected','refined','shortlist','fuel_used','fuel_start','mask','baseline_mask','anchor']:row[k]=0
 if plans:
  assert len(plans)==1
  for k,v in zip(['size','groups','spawn_walk','screened','expected','refined','shortlist','fuel_used','fuel_start','mask','baseline_mask','anchor'],plans[0]):row[k]=int(v)
  assert row['screened']==row['expected'];assert len(set(picks))==len(picks)==row['size']
  row['core']=int({11,3}.issubset(picks));assert row['core'] or set(picks)==base[row['size']],row
 rows.append(row)
with (out/'draft_scan.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sets=collections.defaultdict(collections.Counter)
for v in rows:
 if v['plans']:sets[v['size']][tuple(sorted(map(int,v['picks'].split())))]+=1
s={'scans':len(rows),'planned':sum(v['plans'] for v in rows),'core_drafts':sum(v['core'] for v in rows),'max_fuel':max(v['fuel_used'] for v in rows),'max_fuel_share':max(v['fuel_used']/v['fuel_start'] for v in rows if v['plans']),'turn_errors':sum(v['turn_errors'] for v in rows),'sets':{str(n):{' '.join(map(str,p)):v for p,v in cs.items()} for n,cs in sets.items()}}
(out/'draft_summary.json').write_text(json.dumps(s,indent=2));print(json.dumps(s,indent=2))
