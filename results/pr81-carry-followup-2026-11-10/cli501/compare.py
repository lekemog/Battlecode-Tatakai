import argparse,csv,json,collections,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--new',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();old=a.project/'results/pr81-carry-followup-2026-11-10';new=a.new;out=a.output;out.mkdir(exist_ok=True,parents=True)
def load(p):
 return {(r['candidate'],r['opponent'],r['map'],r['side']):r for r in csv.DictReader(p.open())}
b=load(old/'cases.csv');c=load(new/'cases.csv');assert len(b)==len(c)==1536;assert b.keys()==c.keys();diffs=[]
for key in sorted(b):
 for field in b[key]:
  if b[key][field]!=c[key][field]:diffs.append({'case':key,'field':field,'cli500':b[key][field],'cli501':c[key][field]})
summary=json.load((new/'summary.json').open());report={'cli_version':'5.0.1','cases':len(c),'different_fields':len(diffs),'different_cases':len(set(tuple(x['case']) for x in diffs)),'differences':diffs,'summary':summary}
(out/'comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['differences','summary']}))
hashes={}
for bot in ['v60d','v60f','v60g','v53x','v50p1']:
 files=sorted((a.project/'bots'/bot/'src').glob('*'))+list((a.project/'bots'/bot/'.cambc/build-release').glob('bot.wasm'))
 hashes[bot]={str(f.relative_to(a.project)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files if f.is_file()}
hashes['sdk']={str(f.relative_to(a.project)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((a.project/'sdk/cpp').glob('*.h'))}
hashes['maps']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((a.project/'maps').glob('*.map26a'))};(out/'hashes.json').write_text(json.dumps(hashes,indent=2))
