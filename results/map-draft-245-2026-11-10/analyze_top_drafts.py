from pathlib import Path
import json,gzip,base64,collections,csv
root=Path.cwd();out=root/'results/map-draft-245-2026-11-10';panel=json.load(open(root/'meta-input/panel.json' if (root/'meta-input/panel.json').exists() else root/'results/panel/t10b_240.json'));rows=[]
for name,games in panel['games'].items():
 for g in games:
  p=root/'meta-input'/(g['match']+'.json.gz.b64');raw=base64.b64decode(p.read_text()) if p.exists() else (root/'results/panel/summaries'/(g['match']+'.json.gz')).read_bytes();x=json.loads(gzip.decompress(raw))
  assert x['match']['engineVersion']=='3.0.0'
  theirs='teamB' if g['side']=='a' else 'teamA';picks=[p['champion'] for p in x['roster']['draft'] if p['team']==theirs]
  rows.append(dict(opponent=name,match=g['match'],map=g['map'],side=theirs,draft_size=len(picks),ordered=' | '.join(picks),composition=' | '.join(sorted(picks)),engine_build=x['match']['engineBuildHash']))
with (out/'top10_draft_cases.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
report=[]
for name in sorted(panel['games']):
 rs=[r for r in rows if r['opponent']==name];by=collections.defaultdict(list)
 for r in rs:by[r['draft_size']].append(r)
 nonmodal=pairs=changed=0;detail={}
 for n,vs in by.items():
  counts=collections.Counter(v['composition'] for v in vs);nonmodal+=len(vs)-max(counts.values());pairs+=len(vs)*(len(vs)-1)//2
  changed+=sum(a['composition']!=b['composition'] for i,a in enumerate(vs) for b in vs[i+1:])
  detail[str(n)]={'n':len(vs),'compositions':dict(counts),'orders':dict(collections.Counter(v['ordered'] for v in vs))}
 report.append(dict(opponent=name,games=len(rs),unique_sets=len(set(r['composition'] for r in rs)),same_size_off_modal=nonmodal,off_modal_rate=nonmodal/len(rs),same_size_pairs=pairs,different_same_size_pairs=changed,detail=detail))
(out/'top10_draft_summary.json').write_text(json.dumps(report,indent=2))
for r in report:print(r['opponent'],r['games'],'sets',r['unique_sets'],'offmodal',r['same_size_off_modal'],'/',r['games'],'pairdiff',r['different_same_size_pairs'],'/',r['same_size_pairs'],r['detail'])
print('total games',len(rows),'offmodal',sum(x['same_size_off_modal'] for x in report),'teams vary',sum(x['same_size_off_modal']>0 for x in report))
