"""Generate the six-map regression cases in a configured CLI 5 workspace."""
import argparse,json,shlex
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('project',type=Path);a=p.parse_args();root=a.project.resolve()
out=root/'history-results';out.mkdir(exist_ok=True);lines=[];index=[]
for bot in ['v50h5e','chatgpt-v50h5e-history']:
 for opp in ['v50h5e','x_daniel8','h_mohnish']:
  for name in ['00collision','00contest','00eight','00rows','00expanse','00corners']:
   m=root/'maps'/(name+'.map26a');assert m.is_file(),m
   for side in [0,1]:
    first,second=(bot,opp) if side==0 else (opp,bot)
    tag=f'{bot}--{opp}--{name}--{side}'
    lines.append(shlex.join(map(str,[root/'bots'/first,root/'bots'/second,m,out/(tag+'.repl26a'),'--statistics',out/(tag+'.json'),'--json'])))
    index.append(dict(tag=tag,bot=bot,opp=opp,map=name,side='teamA' if side==0 else 'teamB'))
(out/'manifest.txt').write_text('\n'.join(lines)+'\n');(out/'index.json').write_text(json.dumps(index,indent=2))
print('72 cases:',out/'manifest.txt')
