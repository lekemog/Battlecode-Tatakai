"""Run from a cambc 5.0.0 project containing this branch's bots and maps."""
import argparse,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,default=Path.cwd());p.add_argument('--jobs',type=int,default=4);a=p.parse_args();root=a.project.resolve();maps=sorted((root/'maps').glob('*.map26a'));assert len(maps)==128,len(maps)
out=root/'eta_results';out.mkdir(exist_ok=True);lines=[]
for cand in ['v60d','v60f','v60g']:
 for opp in ['v53x','v50p1']:
  for m in maps:
   for side in [0,1]:
    one,two=(cand,opp) if side==0 else (opp,cand);key=f'{cand}__{opp}__{m.stem}__{side}'
    lines.append(f'{root}/bots/{one} {root}/bots/{two} {m} {out}/{key}.repl26a --statistics {out}/{key}.json --json')
manifest=root/'carry-followup-manifest.txt';manifest.write_text('\n'.join(lines)+'\n');print(len(lines),'games')
subprocess.run(['cambc','run-batch',str(manifest),'--jobs',str(a.jobs),'--release','--json','--timeout','240','--log-limit','20000'],cwd=root,check=True)
