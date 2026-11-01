import json,glob,os,sys,collections
C,B,D=sys.argv[1:4]
rows={}
for f in glob.glob(D+'/*.json'):
    t=os.path.basename(f)[:-5]
    if t=='manifest': continue
    try:j=json.load(open(f))
    except Exception: continue
    m,rest=t.split('_',1)
    if rest.startswith(C+'_'): cs='teamA'
    else: cs='teamB'
    sub={x['team']:int(x['submittedGems']) for x in j['teams']}
    bs='teamB' if cs=='teamA' else 'teamA'
    rows[t]=(m,cs,j['match']['outcome']==cs,j['match']['outcome']==bs,sub[cs]-sub[bs],j['match']['roundsStarted'])
w=sum(r[2] for r in rows.values());l=sum(r[3] for r in rows.values());n=len(rows)
print(f'MIRROR {C} vs {B}: games {n} cand wins {w} base wins {l} other {n-w-l}  cand share of decided {w/max(1,w+l):.3f}  mean gem margin {sum(r[4] for r in rows.values())/max(1,n):+.0f}')
pm=collections.defaultdict(lambda:[0,0])
for r in rows.values():
    pm[r[0]][0]+=r[2];pm[r[0]][1]+=r[3]
bad=[(m,v) for m,v in pm.items() if v[1]-v[0]>=3 or v[1]-v[0]<=-3]
print('maps with 2-0 swing >=3 (cand-base):',sorted([(m,v[0]-v[1]) for m,v in pm.items() if abs(v[0]-v[1])>=2]))
print('per map cand/base wins:',{m:tuple(v) for m,v in sorted(pm.items())})
# fuel/botfault
