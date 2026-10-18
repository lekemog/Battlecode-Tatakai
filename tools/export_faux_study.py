"""Strip local paths, commands, diagnostics and purchase lists from lab results for a study."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lab',HERE/'faux_lab.py')
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

def export(run,output):
    d=json.loads((run/'results.json').read_text())
    for r in d['games']:
        # Re-parse with current metric definitions; runner/source identity is preserved.
        source=run/r['id']/'stats.json'
        if r['status']=='complete':r.update(lab.parse(json.loads(source.read_text())))
        r.pop('command',None)
        for s in ('teamA','teamB'):
            if s in r:r[s].pop('purchases',None)
    output.write_text(json.dumps(d,separators=(',',':'))+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();export(a.run,a.output)
