"""mirror_kd.py CAND BASE : kills and deaths per game (candidate / base) and bot faults from $PROJ=~/lab mirror_<CAND>_<BASE>; side from the file name."""
import json,glob,collections,os,sys
cand,base=sys.argv[1],sys.argv[2]
k=collections.Counter(); fs=[f for f in glob.glob(f'/root/lab/mirror_{cand}_{base}/*.json') if not f.endswith('manifest.json')]
for f in fs:
    j=json.load(open(f)); b=os.path.basename(f); cs='teamA' if b.endswith(f'_{cand}_{base}.json') else 'teamB'
    for c in j['champions']:
        side='cand' if c['team']==cs else 'base'
        k[('kills',side)]+=float(c['metrics']['kills']); k[('deaths',side)]+=float(c['metrics']['deaths'])
    k['faults']+=sum(j['diagnostics']['botFaults'].values())
n=max(1,len(fs)); print(f"kills {k[('kills','cand')]/n:.2f} / {k[('kills','base')]/n:.2f}  deaths {k[('deaths','cand')]/n:.2f} / {k[('deaths','base')]/n:.2f}  faults {k['faults']}")
