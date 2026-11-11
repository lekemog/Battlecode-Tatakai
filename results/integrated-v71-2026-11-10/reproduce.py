import argparse,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('--scan',action='store_true');p.add_argument('--core-control',action='store_true');p.add_argument('--jobs',type=int,default=8);a=p.parse_args()
assert subprocess.check_output(['cambc','--version'],text=True).strip()=='cambc 5.0.1'
r=pathlib.Path.cwd()
import json,hashlib
pins=json.loads((r/'results/integrated-v71-2026-11-10/hashes.json').read_text())
for name,want in pins.items():
 if name.endswith('.wasm'):continue
 assert hashlib.sha256((r/name).read_bytes()).hexdigest()==want,name
assert len(list((r/'maps').glob('*.map26a')))==128
out=r/('draft_scan' if a.scan else 'core_results' if a.core_control else 'int_results');out.mkdir(exist_ok=True)
cs=['cg-v72-integrated'] if a.scan else ['cg-v72-core-control'] if a.core_control else ['v71a','cg-v72-integrated'];opps=['v71a'] if a.scan else ['v71a','v50p1'] if a.core_control else ['v71a','v66i','v50p1']
names=['00collision','00swirl','01yellow-brick-road','02the-pack','03one-gem','03showdown','04gem-caverns','04hourglass'];maps=[r/'maps'/(n+'.map26a') for n in names] if a.core_control else sorted((r/'maps').glob('*.map26a'));lines=[]
for c in cs:
 for o in opps:
  for m in maps:
   for side in [0,1]:
    first,second=(c,o) if side==0 else (o,c);stem=out/f'{c}__{o}__{m.stem}__{side}';lines.append(f'{r}/bots/{first} {r}/bots/{second} {m} {stem}.repl26a --statistics {stem}.json --json')
assert len(lines)==(256 if a.scan else 32 if a.core_control else 1536)
manifest=r/'integration_reproduce.txt';manifest.write_text('\n'.join(lines)+'\n')
cmd=['cambc','run-batch',str(manifest),'--jobs',str(a.jobs),'--release','--json','--timeout','240','--log-limit','20000']
if a.scan:cmd+=['--rounds','2']
subprocess.run(cmd,check=True)
analysis=['python',str(r/'results/integrated-v71-2026-11-10'/('analyze_scan.py' if a.scan else 'analyze.py'))]
if not a.scan:analysis+=['--core-only' if a.core_control else '--main-only']
subprocess.run(analysis,check=True)
