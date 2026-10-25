import json,subprocess,os,sys,statistics as st,collections
S=sys.argv[1]
base=json.load(open(S+'/unr_all.json'));test=json.load(open(sys.argv[2] if len(sys.argv)>2 else S+'/test_matches.json'))
def key(m):
    us=[t for t in m['teams'] if t['name']=='LionelMSISS'][0];th=[t for t in m['teams'] if t['name']!='LionelMSISS'][0]
    return (th['teamId'],m['map'],us['side'])
B={key(m):m for m in base}
def stats(m):
    p=S+'/sum/%s.json'%m['matchId']
    import time
    for _ in range(5):
        if os.path.exists(p):break
        subprocess.run(['cambc','matches','summary',m['matchId'],'--json','-o',p],capture_output=True);time.sleep(2)
    d=json.load(open(p))
    us=[t for t in m['teams'] if t['name']=='LionelMSISS'][0];me='team'+us['side'].upper();them='teamB' if me=='teamA' else 'teamA'
    def val(runs,r):
        acc=0
        for run in runs:
            if acc+run['duration']>r:return float(run['value'])
            acc+=run['duration']
        return float(runs[-1]['value'])
    out={'win':us['result']=='win'}
    for w,tm in(('us',me),('them',them)):
        ch=[c for c in d['champions'] if c['team']==tm]
        M=lambda k:sum(float(c['metrics'][k]) for c in ch)
        out[w]=dict(gems=int([t for t in d['teams'] if t['team']==tm][0]['submittedGems']),deaths=M('deaths'),kills=M('kills'),gold=M('earnedGold'),cdmg=M('championDamageDone'),
            g100=sum(val(t['runs'],100) for t in d['championTimelines'] if t['metric']=='earnedGold' and t['owner'].get('team')==tm),
            g400=sum(val(t['runs'],400) for t in d['championTimelines'] if t['metric']=='earnedGold' and t['owner'].get('team')==tm),
            emb=sum(int(i['quantity']) for c in ch for i in c['items'] if 'Emblem' in i['item']))
    return out
pairs=[]
for m in test:
    k=key(m)
    if k in B:pairs.append((stats(B[k]),stats(m),k))
print('paired games',len(pairs))
for f in ['gems','deaths','kills','gold','g100','g400','cdmg','emb']:
    a=st.mean(p[0]['us'][f] for p in pairs);b=st.mean(p[1]['us'][f] for p in pairs)
    ta=st.mean(p[0]['them'][f] for p in pairs);tb=st.mean(p[1]['them'][f] for p in pairs)
    print(f'{f:7} v25u {a:8.1f}  v25y {b:8.1f}   | opponent vs v25u {ta:8.1f} vs v25y {tb:8.1f}')
print('wins v25u',sum(p[0]['win'] for p in pairs),'v25y',sum(p[1]['win'] for p in pairs))
better=sum(p[1]['us']['gems']>p[0]['us']['gems'] for p in pairs);print('v25y more gems than v25u in',better,'of',len(pairs))
pm=collections.defaultdict(list)
for a,b,k in pairs:pm[k[1]].append(b['us']['gems']-a['us']['gems'])
print({m:round(st.mean(v)) for m,v in pm.items()})
