"""Copy pinned source/maps into an already initialized CLI 5.0.1 scratch project."""
import argparse,pathlib,shutil,json,hashlib
p=argparse.ArgumentParser();p.add_argument('project',type=pathlib.Path);a=p.parse_args()
repo=pathlib.Path(__file__).resolve().parents[2];project=a.project.resolve()
assert project!=repo and (project/'sdk').is_dir(),'Run cambc init --yes PROJECT first, using CLI 5.0.1'
assert '5.0.1' in (project/'cambc.toml').read_text()
pins=json.loads((repo/'results/integrated-v71-2026-11-10/hashes.json').read_text())
for name,want in pins.items():
 if name.endswith('.wasm'):continue
 source=repo/name;assert hashlib.sha256(source.read_bytes()).hexdigest()==want,name
 if name.startswith('bots/'):
  target=project/name
  assert not target.exists(),'Use a fresh project, without copied build caches'
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 elif name.startswith('maps/'):
  target=project/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
assert len(list((project/'maps').glob('*.map26a')))==128,'Remove extra downloaded maps from the scratch project; retain the pinned 128'
target=project/'results/integrated-v71-2026-11-10';target.mkdir(parents=True,exist_ok=True)
for n in ['analyze.py','analyze_scan.py','reproduce.py','test-policy.cpp','hashes.json','DESIGN.md']:
 shutil.copy2(pathlib.Path(__file__).parent/n,target/n)
print('Prepared pinned source and 128 maps:',project)
