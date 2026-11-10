"""usage: an2.py CAND BASE DIR : early deaths/gold/pick-ups of candidate vs base in the mirror games, plus bot faults."""
import json,glob,os,sys,statistics as st
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
C,B,D=sys.argv[1:4]
def tl_at(runs,r):
    t=0
    for x in runs:
        t+=x['duration']
        if r<t:return float(x['value'])
    return float(runs[-1]['value']) if runs else 0
rows={C:[],B:[]};faults=0;n=0
for f in glob.glob(D+'/*.json'):
    t=os.path.basename(f)[:-5]
    if t=='manifest':continue
    try:j=json.load(open(f))
    except Exception:continue
    m,rest=t.split('_',1)
    first=rest.split('_')[0]
    sides={first:'teamA',(B if first==C else C):'teamB'}
    n+=1
    faults+=sum(j['diagnostics']['botFaults'].values())
    for bot,tm in sides.items():
        ids={c['id'] for c in j['roster']['champions'] if c['team']==tm}
        deaths=[];colls=[];kills=0;earn={200:0}
        for e in j['events']:
            if e['owner'].get('id') not in ids:continue
            for x in e['entries']:
                r=x['timestamp']['round']
                if e['kind']=='death':deaths.append(r)
                if e['kind']=='gemCollection':colls.append(r)
                if e['kind']=='kill' and r<=300:kills+=1
        for t_ in j['championTimelines']:
            if t_['metric']=='earnedGold' and t_['owner']['id'] in ids: earn[200]+=tl_at(t_['runs'],200)
        rows[bot].append((sum(1 for r in deaths if r<=150),sum(1 for r in deaths if r<=300),sum(1 for r in colls if r<=100),sum(1 for r in colls if r<=200),earn[200],kills))
print(f'{C} vs {B}: {n} games, bot faults {faults}')
for bot in(C,B):
    v=rows[bot];m=lambda i:round(st.mean(x[i] for x in v),2)
    print(f'  {bot:8s} deaths<=150 {m(0)} deaths<=300 {m(1)} pickups<=100 {m(2)} pickups<=200 {m(3)} gold200 {m(4)} kills<=300 {m(5)}')
