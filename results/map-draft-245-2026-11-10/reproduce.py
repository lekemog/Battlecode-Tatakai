import pathlib,subprocess,argparse
p=argparse.ArgumentParser();p.add_argument('--draft-scan',action='store_true');p.add_argument('--jobs',type=int,default=8);a=p.parse_args()
assert subprocess.check_output(['cambc','--version'],text=True).strip()=='cambc 5.0.1'
r=pathlib.Path.cwd();out=r/('md_draftscan' if a.draft_scan else 'md_results');out.mkdir(exist_ok=True);lines=[]
cs=['cg-md245-plan'] if a.draft_scan else ['v61j','cg-md245-plan','cg-md245-react'];os=['v61j'] if a.draft_scan else ['v61j','v50p1']
for c in cs:
 for o in os:
  for m in sorted((r/'maps').glob('*.map26a')):
   for side in [0,1]:
    first,second=(c,o) if side==0 else (o,c);stem=out/f'{c}__{o}__{m.stem}__{side}';lines.append(f'{r}/bots/{first} {r}/bots/{second} {m} {stem}.repl26a --statistics {stem}.json --json')
assert len(lines)==(256 if a.draft_scan else 1536),'Expected128 pinned maps'
manifest=r/('md_finalscan_manifest.txt' if a.draft_scan else 'md_manifest.txt');manifest.write_text('\n'.join(lines)+'\n')
cmd=['cambc','run-batch',str(manifest),'--jobs',str(a.jobs),'--release','--json','--timeout','240','--log-limit','20000']
if a.draft_scan:cmd+=['--rounds','2']
subprocess.run(cmd,check=True)
subprocess.run(['python',str(r/'results/map-draft-245-2026-11-10'/('analyze_scan.py' if a.draft_scan else 'analyze.py'))],check=True)
