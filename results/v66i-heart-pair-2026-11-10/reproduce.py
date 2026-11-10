import pathlib,subprocess,argparse
p=argparse.ArgumentParser();p.add_argument('--draft-scan',action='store_true');p.add_argument('--broad-scan',action='store_true');p.add_argument('--all-maps',action='store_true');p.add_argument('--jobs',type=int,default=8);a=p.parse_args()
assert subprocess.check_output(['cambc','--version'],text=True).strip()=='cambc 5.0.1'
r=pathlib.Path.cwd();ev=r/'results/v66i-heart-pair-2026-11-10';scan=a.draft_scan or a.broad_scan;directory=('hci_scan' if a.broad_scan else 'hci_flexscan') if scan else 'hci_results';out=r/directory;out.mkdir(exist_ok=True)
cs=['cg-hci66-map' if a.broad_scan else 'cg-hci66-flex'] if scan else ['v66i','cg-hci66-draft','cg-hci66-role','cg-hci66-map','cg-hci66-flex'];opps=['v66i'] if scan else ['v66i','v50p1']
names=['00collision','00swirl','01yellow-brick-road','02the-pack','03one-gem','03showdown','04gem-caverns','04hourglass'];maps=sorted((r/'maps').glob('*.map26a')) if scan or a.all_maps else [r/'maps'/(n+'.map26a') for n in names];lines=[]
for c in cs:
 for o in opps:
  for m in maps:
   for side in [0,1]:
    first,second=(c,o) if side==0 else (o,c);stem=out/f'{c}__{o}__{m.stem}__{side}';lines.append(f'{r}/bots/{first} {r}/bots/{second} {m} {stem}.repl26a --statistics {stem}.json --json')
manifest=r/'hci_reproduce_manifest.txt';manifest.write_text('\n'.join(lines)+'\n')
cmd=['cambc','run-batch',str(manifest),'--jobs',str(a.jobs),'--release','--json','--timeout','240','--log-limit','20000']
if scan:cmd+=['--rounds','2']
subprocess.run(cmd,check=True);script='analyze_scan.py' if a.broad_scan else 'analyze_flex_scan.py' if scan else 'analyze.py';subprocess.run(['python',str(ev/script)],check=True)
