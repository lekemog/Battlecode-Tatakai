"""Rebuild a portable cambc manifest from the published case index.

Usage: python make_manifest.py PROJECT DATASET [--resume]
PROJECT contains bots/ and maps-current/; current-maps.zip is extracted there.
"""
import argparse, hashlib, json, re, shlex
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('project',type=Path)
p.add_argument('dataset',choices=['robustness','new-map-validation','baseline-validation','learned-ablation'])
p.add_argument('--resume',action='store_true')
a=p.parse_args(); root=a.project.resolve(); here=Path(__file__).resolve().parent
source=json.loads((here/'source-manifest.json').read_text())
def canonical(s):return re.sub(r'^\d\d','',s).replace('-','_')
maps={canonical(m.stem):m for m in (root/'maps-current').glob('*.map26a')}
for m in maps.values():
    assert hashlib.sha256(m.read_bytes()).hexdigest()==source['maps'][m.name], m
cases=json.loads((here/('index-'+a.dataset+'.json')).read_text())
for name in sorted({r[k] for r in cases for k in ['bot','opponent']}):
    for f,expected in {**source['candidates'],**source['opponents']}[name].items():
        assert hashlib.sha256((root/'bots'/name/f).read_bytes()).hexdigest()==expected,(name,f)
dest=root/'results'/a.dataset; dest.mkdir(parents=True,exist_ok=True)
lines=[]
for r in cases:
    output=dest/(r['tag']+'.json')
    if a.resume and output.exists():
        try:
            saved=json.loads(output.read_text())
            assert saved['match']['engineBuildHash']==source['engine_build']
            continue
        except (json.JSONDecodeError,KeyError):pass
    bot,opp=r['bot'],r['opponent']; first,second=(bot,opp) if r['side']=='teamA' else (opp,bot)
    fields=[root/'bots'/first,root/'bots'/second,maps[canonical(r['map'])],dest/(r['tag']+'.repl26a'),'--statistics',output,'--json']
    lines.append(shlex.join(map(str,fields)))
(dest/'manifest.txt').write_text('\n'.join(lines)+'\n')
(dest/'index.json').write_text(json.dumps(cases,indent=2))
print(len(lines),'cases:',dest/'manifest.txt')
