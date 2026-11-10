"""Run from an initialized CLI 5.0.1 project containing this repo's bots/maps."""
import pathlib,subprocess,json
root=pathlib.Path.cwd(); evidence=root/'results/role61-2026-11-10'
assert subprocess.check_output(['cambc','--version'],text=True).strip().endswith('5.0.1'), 'Use CLI 5.0.1'
(root/'role_results').mkdir(exist_ok=True)
lines=[]
for candidate in ['v60d','cg-role61-kite','cg-role61']:
 for opponent in ['v53x','v50p1','v60d']:
  for m in sorted((root/'maps').glob('*.map26a')):
   for side in [0,1]:
    a,b=(candidate,opponent) if side==0 else (opponent,candidate)
    stem=root/'role_results'/f'{candidate}__{opponent}__{m.stem}__{side}'
    lines.append(f'{root}/bots/{a} {root}/bots/{b} {m} {stem}.repl26a --statistics {stem}.json --json')
assert len(lines)==2304, 'Expected exactly 128 pinned maps'
manifest=root/'role_manifest.txt';manifest.write_text('\n'.join(lines)+'\n')
subprocess.run(['cambc','run-batch',str(manifest),'--jobs','8','--release','--json','--timeout','240','--log-limit','20000'],check=True)
subprocess.run(['python',str(evidence/'analyze.py'),'--project',str(root),'--output',str(evidence)],check=True)
subprocess.run(['python',str(evidence/'paired.py')],check=True)
s=json.loads((evidence/'summary.json').read_text());assert s['total']==2304
assert all(x['n']==256 for x in s['summary'].values())
