"""Emit the batch manifest from the committed plan and index, after source/map hash checks.

python results/<report>/reproduce.py /path/to/cli5-lab /path/to/output
Then cambc run-batch OUTPUT/manifest.txt --release --jobs 8 --timeout 180 --log-limit 0
"""
import argparse
import hashlib
import json
import shlex
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('project', type=Path)
ap.add_argument('output', type=Path)
args = ap.parse_args()
here = Path(__file__).resolve().parent
root, out = args.project.resolve(), args.output.resolve()
plan = json.loads((here / 'plan.json').read_text())
index = json.loads((here / 'index.json').read_text())
validation = json.loads((here / 'validation.json').read_text())
for bot, build in validation['builds'].items():
    for name, h in build['sources'].items():
        f = root / 'bots' / bot / 'src' / name
        data = f.read_bytes()
        # The measured download fixture added one final LF. Reproduce only
        # that exact, hash-verified whitespace normalisation, never a code edit.
        if hashlib.sha256(data).hexdigest() != h and hashlib.sha256(data + b'\n').hexdigest() == h:
            f.write_bytes(data + b'\n')
        assert hashlib.sha256(f.read_bytes()).hexdigest() == h, f
for name, h in plan['maps'].items():
    assert hashlib.sha256((root / 'maps-sandbox' / name).read_bytes()).hexdigest() == h
out.mkdir(parents=True, exist_ok=True)
lines = []
for c in index:
    a, b = (c['bot'], c['opp']) if c['side'] == 'teamA' else (c['opp'], c['bot'])
    fields = [root / 'bots' / a, root / 'bots' / b, root / 'maps-sandbox' / (c['map'] + '.map26a'),
              out / (c['tag'] + '.repl26a'), '--statistics', out / (c['tag'] + '.json'), '--json']
    lines.append(shlex.join(map(str, fields)))
(out / 'manifest.txt').write_text('\n'.join(lines) + '\n')
(out / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
(out / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
print(len(lines), 'cases:', out / 'manifest.txt')
