import json,glob,collections,os,sys
# champ.py DIR CAND BASE : per-champion metrics for cand and base sides
d,cand,base=sys.argv[1:4]
A=collections.defaultdict(lambda: collections.Counter())
for f in glob.glob(d+'/*.json'):
    if f.endswith('manifest.json'): continue
    j=json.load(open(f)); b=os.path.basename(f); cs='teamA' if b.endswith(f'_{cand}_{base}.json') else 'teamB'
    for c in j['champions']:
        k=('C ' if c['team']==cs else 'B ')+c['name']; m=c['metrics']; a=A[k]; a['n']+=1
        for q in ['kills','deaths','earnedGold','championDamageDone','championDamageTaken','monsterDamageDone','collectedGems','submittedGems','monsterDamageTaken']: a[q]+=float(m[q])
print(f"{'':18} {'n':>4} {'kill':>5} {'death':>5} {'gold':>6} {'cdmg':>6} {'ctaken':>6} {'mdmg':>7} {'mtaken':>6} {'gems':>5} {'bank':>5}")
for k,a in sorted(A.items()):
    n=a['n']; print(f"{k:18} {n:4} {a['kills']/n:5.2f} {a['deaths']/n:5.2f} {a['earnedGold']/n:6.0f} {a['championDamageDone']/n:6.0f} {a['championDamageTaken']/n:6.0f} {a['monsterDamageDone']/n:7.0f} {a['monsterDamageTaken']/n:6.0f} {a['collectedGems']/n:5.0f} {a['submittedGems']/n:5.0f}")
