import json,glob,os,collections,sys
d,cand,base=sys.argv[1:4]
def series(runs):
    out=[]
    for r in runs: out += [float(r['value'])]*r['duration']
    return out
A=collections.defaultdict(lambda: collections.Counter())
R=(50,100,200,300,500)
for f in glob.glob(d+'/*.json'):
    if 'manifest' in f: continue
    j=json.load(open(f)); cs='teamA' if f.endswith(f'_{cand}_{base}.json') else 'teamB'
    ids={c['id']:c for c in j['champions']}
    for t in j['championTimelines']:
        c=ids[t['owner']['id']]
        if t['metric'] not in('earnedGold','monsterDamageDone','collectedGems','monsterDamageTaken'): continue
        s=series(t['runs']); a=A[('C ' if c['team']==cs else 'B ')+c['name']]
        for r in R: a[(t['metric'],r)]+=s[min(r,len(s)-1)]
        if t['metric']=='earnedGold': a['n']+=1
for n,a in sorted(A.items()):
    if len(sys.argv)>4 and sys.argv[4] not in n: continue
    k=a['n']; print(f"{n:16}", 'gold',[round(a[('earnedGold',r)]/k) for r in R],'mdmg',[round(a[('monsterDamageDone',r)]/k) for r in R],'gems',[round(a[('collectedGems',r)]/k) for r in R],'mtaken',[round(a[('monsterDamageTaken',r)]/k) for r in R])
