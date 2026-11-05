"""Reproduce frozen sandbox cases in a configured CLI 5 workspace.

python make_current_manifest.py PROJECT
Place the 40 maps from pinned bench/maps/ in PROJECT/maps-sandbox first.
"""
import argparse,hashlib,json,shlex
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('project',type=Path)
a=parser.parse_args();root=a.project.resolve();here=Path(__file__).resolve().parent
plan=json.loads((here/'plan.json').read_text());validated=json.loads((here/'validation.json').read_text())
for bot,b in validated['builds'].items():
 for name,sha in b['sources'].items():
  f=root/'bots'/bot/'src'/name
  assert hashlib.sha256(f.read_bytes()).hexdigest()==sha,('source mismatch',f)
for name,sha in plan['maps'].items():
 f=root/'maps-sandbox'/name
 assert hashlib.sha256(f.read_bytes()).hexdigest()==sha,('map mismatch',f)
out=root/'sandbox-current';out.mkdir(exist_ok=True);lines=[]
cases=json.loads((here/'index.json').read_text())
for r in cases:
 first,second=(r['bot'],r['opp']) if r['side']=='teamA' else (r['opp'],r['bot'])
 fields=[root/'bots'/first,root/'bots'/second,root/'maps-sandbox'/(r['map']+'.map26a'),out/(r['tag']+'.repl26a'),'--statistics',out/(r['tag']+'.json'),'--json']
 lines.append(shlex.join(map(str,fields)))
(out/'manifest.txt').write_text('\n'.join(lines)+'\n');(out/'index.json').write_text(json.dumps(cases));(out/'plan.json').write_text(json.dumps(plan))
print(len(lines),'cases:',out/'manifest.txt')
