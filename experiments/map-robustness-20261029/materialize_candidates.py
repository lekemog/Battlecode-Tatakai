"""Apply frozen experiments to an exact v50c source copy; no network or deployment."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('baseline',type=Path)
p.add_argument('project',type=Path)
args=p.parse_args()
here=Path(__file__).resolve().parent
hashes=json.loads((here/'baseline-sha256.json').read_text())
for name,expected in hashes.items():
    path=args.baseline/'src'/name
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise SystemExit('Baseline differs from tested v50c: '+str(path))
for patch in sorted(here.glob('v50c-*.patch')):
    target=args.project/'bots'/patch.stem
    if target.exists():
        raise SystemExit('Refusing to overwrite candidate: '+str(target))
    shutil.copytree(args.baseline,target,ignore=shutil.ignore_patterns('.cambc'))
    subprocess.run(['patch','--batch','-p1','-i',str(patch)],cwd=target,check=True)
    print(target)
