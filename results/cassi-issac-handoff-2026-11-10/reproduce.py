"""From an initialized CLI5.0.1 project with the pinned repo bots/maps."""
import argparse,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('--all-maps',action='store_true');p.add_argument('--jobs',type=int,default=8);a=p.parse_args()
assert subprocess.check_output(['cambc','--version'],text=True).strip()=='cambc 5.0.1'
r=pathlib.Path.cwd();out=r/'ci_results';out.mkdir(exist_ok=True)
names=['00collision','00swirl','01yellow-brick-road','02the-pack','03one-gem','03showdown','04gem-caverns','04hourglass']
maps=sorted((r/'maps').glob('*.map26a')) if a.all_maps else [r/'maps'/(m+'.map26a') for m in names]
lines=[]
for c in ['cg-ci-draft','cg-ci-pair','cg-ci-shop']:
 for o in ['v61j','v50p1']:
  for m in maps:
   for side in [0,1]:
    first,second=(c,o) if side==0 else (o,c);stem=out/f'{c}__{o}__{m.stem}__{side}'
    lines.append(f'{r}/bots/{first} {r}/bots/{second} {m} {stem}.repl26a --statistics {stem}.json --json')
manifest=r/'ci_manifest.txt';manifest.write_text('\n'.join(lines)+'\n')
subprocess.run(['cambc','run-batch',str(manifest),'--jobs',str(a.jobs),'--release','--json','--timeout','240','--log-limit','20000'],check=True)
subprocess.run(['python',str(r/'results/cassi-issac-handoff-2026-11-10/analyze.py')],check=True)
